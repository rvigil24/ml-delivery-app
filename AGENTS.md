# Reglas compartidas — agentes de desarrollo

Este archivo aplica a **ambos integrantes** y a cualquier agente (Codex/Claude Code) ejecutado sobre el repositorio. No supone que el uso de agentes esté autorizado académicamente; el equipo deberá consultar las normas del curso.

## Antes de escribir código

1. Lee `README.md`, `docs/TASKS.md` y los documentos pertinentes (`docs/SPEC.md`, `docs/ARCHITECTURE.md`, `docs/DATA_ML.md`).
2. Identifica **ID de tarea, responsable, dependencias y criterio de aceptación**. La hoja de backlog compartida es la autoridad para cambios de responsables/estado.
3. Si la petición no especifica tarea, continúa con la siguiente tarea pendiente del bloque activo documentado en `docs/TASKS.md`. Si no hay bloque activo o el alcance es ambiguo, pide el ID. No añadas tareas al bloque por iniciativa propia.
4. Inspecciona la rama, los archivos existentes y las interfaces antes de modificar código. Evita pisar trabajo del otro integrante.
5. Propón una solución pequeña que resuelva la tarea sin implementar componentes futuros.

## Disciplina de colaboración

- Trabaja una tarea a la vez dentro de un bloque pequeño de 2–3 tareas relacionadas. Usa una rama por bloque, creada desde `origin/main` actualizado, y un solo PR al cerrar el bloque. Identifica tareas y evidencia en los commits y en el PR. No sobreescribas ni reformatees código ajeno fuera del alcance.
- Mantén **interfaces compartidas** en `docs/ARCHITECTURE.md`; si necesitas cambiar contratos, presenta el cambio y coordina antes de aplicarlo.
- No cambies propietarios o estados del backlog automáticamente. No crees commits, `push`, `merge` ni PR sin una orden explícita.
- Flujo acordado con Ruben el 2026-11-03: «cerrá el bloque» constituye la orden explícita para verificar el bloque activo, actualizar el backlog local con evidencia, crear commit(s), hacer push, crear o actualizar su único PR y fusionarlo si las comprobaciones y las reglas del remoto lo permiten. No implica borrar ramas, iniciar otro bloque, desplegar ni modificar el Excel. No tratar un fallo de push, PR o merge como un cierre exitoso.
- Antes de cerrar un bloque, contrastar todos sus IDs y dependencias con la implementación y las comprobaciones reales. Una tarea bloqueada o sin evidencia permanece abierta y no permite avanzar a dependientes. Después del merge, verificar en remoto que el commit quedó incluido en `main`, actualizar la rama `main` local y la guía de estudio. Usar integración normal que conserve los commits; no forzar pushes ni eludir protecciones.
- Al terminar: lista archivos tocados, cambios reales, comandos ejecutados (y resultados), pruebas pendientes, decisiones y riesgos.
- El otro integrante revisa el trabajo antes de cerrar la tarea.
- Por solicitud de Ruben, al terminar cada tarea actualizar la guía personal de estudio `../GUIA_ESTUDIO_DELIVERY.md`, ubicada junto a la carpeta principal del repositorio y fuera de Git. Explicar qué se hizo, por qué, comprobaciones reales, conceptos para la exposición y pendientes; no incluir registros del dataset ni secretos. En worktrees usar la misma guía externa, sin crear copias divergentes.
- Las instrucciones y notas de asistencia a agentes son temporales y Ruben prevé retirarlas después. No introducir dependencias de ejecución hacia esos archivos; conservar decisiones, metodología y reproducción en README, documentación técnica y notebooks para que el proyecto siga siendo comprensible al retirarlas.

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
