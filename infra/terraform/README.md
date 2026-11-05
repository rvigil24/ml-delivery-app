# Infraestructura académica: ECS con Fargate

Esta carpeta **prepara** infraestructura; no demuestra un despliegue. Terraform
1.13+ y proveedor AWS bloqueado en `.terraform.lock.hcl`. Una tarea Linux x86_64
de 0.5 vCPU / 2 GiB; ECR, VPC/subred pública, entrada HTTP desde un /32, roles,
logs y contenedor de secreto Atlas. El bucket `ml-kodigo-resources` se consulta
con `data`, sin administrar sus políticas, objetos o ciclo de vida.

## Revisar sin crear recursos

Desde esta carpeta, usando un perfil AWS real (no un emulador):

```bash
terraform init
terraform fmt -check
terraform validate
cp terraform.tfvars.example terraform.tfvars
# Editar presenter_cidr e image_tag; conservar desired_count = 0.
AWS_PROFILE=remote-admin AWS_REGION=us-east-1 terraform plan -out=review.tfplan
terraform show -no-color review.tfplan
```

Si el entorno tiene `AWS_ENDPOINT_URL` o variantes por servicio, retirarlas para
esta ejecución: no apuntar el plan real a localhost/LocalStack. `plan` consulta
AWS, pero no crea recursos. Revisar siempre la cuenta seleccionada. No ejecutar
`apply` sin autorización explícita. Incluso con cero tareas, aplicar crearía
infraestructura, IAM y un secreto con costo; cero no equivale a despliegue gratuito.

Estado local por ahora, ignorado por Git junto a planes y variables privadas;
mantener copia privada antes de usar otro equipo. No configurar un backend en
el bucket compartido ni escribir secretos en tfvars. El lock del proveedor sí
se versiona. No hay scripts `local-exec` ni cambios implícitos con AWS CLI.

## Antes del primer arranque (posterior a aprobar el plan)

1. Publicar la imagen existente en ECR con la etiqueta inmutable indicada.
   La etiqueta del ejemplo todavía no existe; Terraform no construye ni publica.
2. Cargar **la URI completa como texto** en Secrets Manager fuera de Terraform,
   usando el ARN de salida y un mecanismo privado. No crear `secret_version`
   desde Terraform: el valor quedaría en el estado. Atlas debe tener el esquema
   e índices ya preparados por el procedimiento de MongoDB del proyecto.
3. El servicio ejecuta `python -m delivery.cloud_start`: espera conectividad y
   esquema Mongo antes de iniciar Uvicorn mediante `exec`, sin cambiar tarea/IP.
   El plazo es `start_timeout_seconds` (900 segundos por defecto, configurable
   hasta 3600). No crea índices, colecciones o datos. Una configuración inválida
   o el agotamiento del plazo detiene el proceso; los logs omiten credenciales.
   Solo tras autorizar el arranque, cambiar `desired_count` de cero a uno,
   obtener la IPv4 de la tarea y permitir su /32 en Atlas durante la espera.
   Repetir al reemplazar la tarea; no abrir Atlas globalmente.
4. Verificar predicción v2 y persistencia real; `/health` solo comprueba proceso.
   La demo automática sigue deshabilitada. El API utiliza el rol de tarea para
   descargar el bundle S3 fijado por SHA-256 al arrancar, sin claves locales.

El healthcheck ECS ejecuta `python -m delivery.cloud_start --healthcheck`.
Durante la espera comprueba PID y plazo; después consulta `/health`. Es una
comprobación de vitalidad: ECS puede indicar HEALTHY antes de que la API esté
lista. No usar ese estado como evidencia de predicción, Atlas o demo operativa.

### Consultar la IP tras un arranque autorizado

Comandos de lectura, con perfil real y sin endpoints de emulador:

```bash
aws ecs list-tasks --profile remote-admin --region us-east-1 \
  --cluster delivery-demo --service-name delivery-demo-api
aws ecs describe-tasks --profile remote-admin --region us-east-1 \
  --cluster delivery-demo --tasks <ARN-de-tarea> \
  --query 'tasks[].attachments[].details[?name==`networkInterfaceId`].value'
aws ec2 describe-network-interfaces --profile remote-admin --region us-east-1 \
  --network-interface-ids <eni-obtenida> \
  --query 'NetworkInterfaces[].Association.PublicIp'
```

La API de redes se llama `ec2` también para Fargate; esto no crea ni utiliza una
instancia EC2 del proyecto. No automatizar cambios de la lista Atlas desde la
aplicación ni darle permisos administrativos sobre Atlas.

No se incluyen EC2, EBS, Elastic IP, ALB, NAT Gateway, MongoDB en contenedor,
Next.js, TLS ni CI/CD. La IP es variable y HTTP se limita al equipo autorizado;
no enviar datos personales en esta demo. No es un endpoint público estable o
una configuración de alta disponibilidad. La salida de red se permite para
los endpoints variables de AWS/Atlas; la entrada queda restringida al /32.

ECR impide borrar un repositorio con imágenes; el secreto tiene recuperación
de siete días. Revisar nombres existentes y planes de sustitución/destrucción
antes de aplicar. No se debe importar un recurso ajeno para resolver colisiones.

Referencias: [ECS/Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html),
[red de tareas](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/networking-outbound.html),
[recurso Terraform ECS](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecs_service).

## Integración y despliegue desde GitHub Actions

`.github/workflows/ci.yml` ejecuta en cada PR y push a main: pruebas básicas de
modelo de dominio/arranque (sin datasets o entrenamiento), validación estática
Terraform sin credenciales y construcción Docker sin publicar imagen. Usa las
versiones Python/uv/Terraform del proyecto y acciones fijadas por SHA.

`.github/workflows/deploy.yml` solo admite disparo manual desde main con el
texto DESPLEGAR. Exige CI aprobada para ese commit, variables de entorno GitHub
`AWS_DEPLOY_ROLE_ARN` y `AWS_ACCOUNT_ID`, y el entorno `aws-demo`. Antes de usarlo
hay que autorizar/aprovisionar infraestructura, configurar OIDC y restricciones
del entorno (main y aprobación), publicar el valor del secreto y preparar Atlas.
No contiene claves AWS permanentes. El rol AWS todavía no se ha creado; el entorno GitHub ya limita a main y exige aprobación de rvigil24;
no ejecutar el workflow como prueba mientras esos requisitos estén pendientes.

El job obtiene credenciales temporales, publica una imagen etiquetada con el
SHA del commit en el ECR existente, registra revisión de la definición actual
cambiando solo la imagen y actualiza el servicio a una tarea. Reutiliza una
imagen ya publicada con esa etiqueta inmutable. Muestra la IPv4 de la nueva
tarea para permitir su /32 en Atlas mientras espera. No ejecuta Terraform apply,
crea infraestructura, escribe el secreto o cambia políticas del bucket.

Un resultado verde de despliegue solo acredita actualización/estabilidad ECS;
no acredita API/modelos/persistencia funcionales. Esa validación se realiza
luego desde la IP permitida. La revisión anterior queda en el resumen para un
rollback manual autorizado; no se afirma rollback automático funcional.
Antes de un futuro plan/apply, sincronizar `image_tag` con el SHA desplegado y
`desired_count` con el estado acordado: CI/CD actualiza ECS fuera de Terraform y
un plan con variables viejas puede proponer volver a la imagen o cantidad previa.
Los permisos del rol OIDC se limitarán a ECR de demo, ECS de demo, descripción de
sus redes y PassRole de los dos roles de tarea. No necesita leer la URI Atlas,
modificar IAM, escribir S3 ni crear recursos. `ecr:GetAuthorizationToken` y las
operaciones Describe/List que AWS no permite limitar por recurso necesitan
Resource '*'; la confianza OIDC y el resto de recursos deben estar acotados.

## Seguridad preparada y activación pendiente

El proveedor OIDC y el rol de entrega se declaran en `github_oidc.tf`. Antes de
aplicarlo se comprobó que la cuenta no tenía proveedores OIDC. Si esto cambia,
revisar el plan: no crear duplicados ni importar identidades ajenas automáticamente.
La confianza usa aud `sts.amazonaws.com` y este sub exacto, obtenido de GitHub:

`repo:rvigil24@23065092/ml-delivery-app@1443588308:environment:aws-demo`

El formato inmutable fue confirmado por la API OIDC del repositorio. El entorno
GitHub `aws-demo` ya permite únicamente la rama main y exige aprobación de Ruben.
La aprobación propia se permite porque el proyecto tiene un único desarrollador
activo. El workflow también comprueba main, DESPLEGAR y CI aprobada. No hay
variables AWS configuradas todavía; se cargarán después de autorizar el apply.

El rol GitHub solo publica imágenes en el ECR de demo, registra revisiones de
su familia, actualiza su servicio y consulta tareas/IP. PassRole se limita a los
dos roles ECS y al servicio ecs-tasks.amazonaws.com. No lee o escribe el secreto
Atlas, no administra IAM ni escribe S3. Las confianzas ECS incluyen SourceAccount
y SourceArn de la cuenta/región para reducir usos desde otros contextos.

Plan revisado: 19 altas, cero cambios/bajas, servicio con cero tareas. Incluye los
16 recursos de infraestructura ya propuestos y tres de seguridad (proveedor,
rol GitHub y política). `deployment.tfvars` privado tiene la IPv4 pública /32
observada y el SHA base de imagen; se excluye de Git. La IP puede cambiar: confirmar
que sigue siendo la del equipo de exposición antes de aplicar. Crear la base con
cero tareas todavía crea IAM, ECR, logs y el contenedor de secreto con posible
costo de almacenamiento: necesita autorización explícita. No se ha aplicado.

Después de esa autorización: aplicar el plan revisado, configurar
`AWS_DEPLOY_ROLE_ARN` y `AWS_ACCOUNT_ID` en el entorno GitHub usando las salidas,
y cargar la URI completa en Secrets Manager desde `.env` mediante el operador
local. El valor no se añade a GitHub, Terraform o imagen, ni se imprime. Usar
perfil local y endpoint real de Secrets Manager; no un perfil de emulador.
No registrar `secret_version` en Terraform. La aplicación solo recibe ese valor
en runtime, a través de su rol de ejecución. Inicializar/migrar Atlas no forma
parte de este paso: el esquema existente se comprueba, sin recrearlo.

La validación funcional del rol OIDC, la inyección del secreto y el acceso Atlas
siguen pendientes hasta autorizar recursos y arrancar la demo. No sustituirlas
por fmt/validate o una CI verde. La activación de Fargate a una tarea mediante
el workflow manual constituye un despliegue adicional y debe estar autorizado.

### Activación autorizada y permisos comprobados

Ruben autorizó el 2026-11-04 crear los 19 recursos, cargar la URI Atlas y arrancar
una tarea. Apply inicial completado: 19 altas, cero cambios/bajas; valor del
secreto cargado fuera de Terraform, variables GitHub no secretas configuradas.
El pipeline autenticó OIDC y publicó ECR. Su primer intento detectó que
`ecs:DescribeTaskDefinition` requiere Resource '*': se corrigió únicamente esa
lectura con restricción de región. No confundir la consulta global con permisos
para desplegar fuera del servicio/familia autorizados. El reintento reutiliza la
misma imagen inmutable, sin reconstruirla o exponer credenciales.

El pipeline administra la revisión ECS activa. Terraform ignora cambios de
`task_definition` en el servicio para no revertir una entrega; mantiene la
configuración inicial como base. `desired_count` sigue bajo Terraform: el archivo
privado de despliegue ahora usa uno para coincidir con el servicio autorizado.
Para parar costos de cómputo se puede llevar explícitamente a cero; no hacerlo
implícitamente aplicando el archivo de ejemplo. S3 no fue recreado ni modificado.

### Espera manual de la lista Atlas

Para la demo desplegada se configuró `start_timeout_seconds = 0`: espera sin
límite mientras se permite el /32 de la tarea. Evita que un timeout del proceso
haga reemplazar la tarea y cambie su IP durante el paso manual. No convierte la
IPv4 en fija: otra caída o despliegue puede cambiarla. Valores 1–3600 siguen
habilitando una espera limitada. Durante la espera solo hay vitalidad; la API
no sirve solicitudes hasta verificar Mongo. Sigue consumiendo la tarea reservada.

El pipeline usa la última revisión de la familia como configuración base,
incorporando los cambios preparados por Terraform, y reemplaza su imagen por
la del commit aprobado. Conserva la revisión del servicio anterior para rollback.

El arranque de Fargate puede superar un minuto al reemplazar una tarea. El
workflow espera hasta tres minutos para obtener la IP. Una entrega correctiva
agotó el margen anterior de 60 segundos, pero su tarea sí arrancó después:
verificar ECS antes de reintentar un job, porque reintentar la entrega puede
reemplazar la tarea y cambiar su IP. La corrección del margen no despliega una
nueva imagen automáticamente. La tarea de espera 0 continúa ejecutándose.

### Comprobación funcional realizada

Tras autorizar 3.231.221.94/32 en Atlas se verificaron /health, predicción v2
con source S3 y creación/lectura HTTP de un negocio SIMULADO. Otra conexión
Atlas confirmó la persistencia; la fixture se eliminó y se comprobó ausencia.
Logs de arranque/predicción y series CPU/memoria CloudWatch comprobados, sin
ensayo de carga. Revisión activa :5 con imagen 17d4a75 y espera 0. Esta evidencia
no incluye la demo automática de efectivo en AWS (continúa deshabilitada).
Swagger actual: http://3.231.221.94:8000/docs, accesible desde la /32 permitida.
No redesplegar por actualizar documentos: reemplazar la tarea puede cambiar IP.


## Frontend Vercel y API pública de demo

Frontend verificado: https://delivery-economico.vercel.app. API actual:
http://3.239.180.88:8000/docs, revisión9, imagen f5ede18. El despliegue autorizado
activó `public_api_access=true` y `demo_enabled=true` en las variables privadas;
los valores predeterminados del módulo siguen siendo false. No se crearon
servidores adicionales ni se modificó S3. El SG permite HTTP8000 desde Internet;
esta API de demostración no tiene autenticación.

Ante otro reemplazo, permitir la IP nueva en Atlas, actualizar DELIVERY_API_URL
en Vercel y publicar nuevamente. El servicio conserva una tarea; el pipeline
administra su revisión activa y Terraform conserva la definición base. ECS estable
no sustituye verificar HTTP, modelos y persistencia. La última comprobación pública
cubrió pedido y grupo con efectivo usando modelos S3 y Atlas.
