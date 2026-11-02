# Reglas compartidas — agentes de desarrollo

Este archivo aplica a **ambos integrantes** y a cualquier agente (Codex/Claude Code) ejecutado sobre el repositorio. No supone que el uso de agentes esté autorizado académicamente; el equipo deberá consultar las normas del curso.

## Antes de escribir código

1. Lee `README.md`, `docs/TASKS.md` y los documentos pertinentes (`docs/SPEC.md`, `docs/ARCHITECTURE.md`, `docs/DATA_ML.md`).
2. Identifica **ID de tarea, responsable, dependencias y criterio de aceptación**. La hoja de backlog compartida es la autoridad para cambios de responsables/estado.
3. Si la petición no especifica tarea, pide el ID; no implementes varias tareas por iniciativa propia.
4. Inspecciona la rama, los archivos existentes y las interfaces antes de modificar código. Evita pisar trabajo del otro integrante.
5. Propón una solución pequeña que resuelva la tarea sin implementar componentes futuros.

## Disciplina de colaboración

- Una tarea por cambio y rama propia. No sobreescribas ni reformatees código ajeno fuera del alcance.
- Mantén **interfaces compartidas** en `docs/ARCHITECTURE.md`; si necesitas cambiar contratos, presenta el cambio y coordina antes de aplicarlo.
- No cambies propietarios o estados del backlog automáticamente. No crees commits, `push`, `merge` ni PR sin una orden explícita.
- Al terminar: lista archivos tocados, cambios reales, comandos ejecutados (y resultados), pruebas pendientes, decisiones y riesgos.
- El otro integrante revisa el trabajo antes de cerrar la tarea.

## Alcance y rigurosidad

- Python **3.9+**; favorecer módulos simples, tipado, separación de responsabilidades y POO cuando aporte valor.
- FastAPI para API; MongoDB para pedidos y estados; S3 existente para archivos; Next.js para la simulación visual; Docker/Terraform/AWS en tareas posteriores.
- Para procesamiento usar Pandas y demostrar transformaciones equivalentes con Dask y PySpark local. ML: baseline, 3 algoritmos de diferentes familias, CV/tuning, métricas reales y una MLP pequeña.
- **No crear datasets, etiquetas, valores de entrenamiento, tiempos reales, métricas, tarifas ni ROI falsos.** Ejemplos ilustrativos claramente separados de los experimentos reales.
- No afirmar predicción de tiempos por bicicleta/moto si los datos reales no permiten sostenerlo. Las reglas de vehículos/tarifas se documentan como reglas configurables, no resultados ML.
- WhatsApp, repartidores y pagos en efectivo son simulados. No conectar canales reales ni ejecutar cobros.
- El dataset real y la definición de la variable objetivo se **validan antes de entrenar**. Si no sirven, reportar el bloqueo y plantear opciones al equipo, sin cambiar el problema silenciosamente.
- Al menos 10 pruebas unitarias pytest en el producto académico, con otras pruebas según necesidad; no simular salidas de test.

## AWS, seguridad y costos

- Bucket ya existente: `ml-kodigo-resources`, región `us-east-1`, prefijos `datasets/`, `models/`, `docs/`.
- No crear/recrear el bucket, no borrarlo ni modificar políticas; Terraform debe referenciarlo como recurso existente salvo instrucción explícita y diseño aprobado.
- No usar ni versionar claves AWS, `.env` reales, credenciales, tokens o archivos privados. Usar AWS CLI perfiles locales o roles IAM; el frontend nunca debe recibir credenciales AWS.
- No desplegar, crear EC2, configurar IAM, cambiar DNS ni generar gastos AWS sin autorización explícita. Primero comprobar `terraform plan` cuando llegue esa tarea.
- Los experimentos se ejecutan localmente cuando sea posible; la API servirá un modelo entrenado y validado, no reentrenará en cada request.

## Cambios de especificación

No inventar números de distancias máximas, comisiones, porcentajes, sueldos, tiempos, zonas, límites de carga, combustible, fórmulas de tarifa ni rentabilidad. Marcar los valores pendientes como configurables y solicitar una decisión concreta si bloquean la tarea. Mantener las decisiones en los documentos existentes; no agregar un nuevo archivo por cada decisión.
