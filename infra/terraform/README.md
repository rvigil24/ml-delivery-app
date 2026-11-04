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
3. Resolver el arranque con la IPv4 dinámica antes de habilitar una tarea:
   la API actual verifica Atlas una sola vez al iniciar. Añadir el /32 después
   de esa verificación no recupera sus repositorios; reemplazar la tarea vuelve
   a cambiar su IP. La configuración de ejecución posterior deberá esperar
   conectividad/esquema Atlas antes de iniciar Uvicorn, conservando la misma
   tarea e IP durante esa espera. No abrir Atlas globalmente. Por este motivo
   esta etapa valida exclusivamente `desired_count = 0`.
4. Verificar predicción v2 y persistencia real; `/health` solo comprueba proceso.
   La demo automática sigue deshabilitada. El API utiliza el rol de tarea para
   descargar el bundle S3 fijado por SHA-256 al arrancar, sin claves locales.

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
