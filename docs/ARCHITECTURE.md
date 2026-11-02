# ARCHITECTURE — Arquitectura del Asistente de Delivery Económico

**Estado:** arquitectura prevista para el MVP académico, no implementación terminada. T03 revisa y acuerda contratos; T04 implementa únicamente los modelos de dominio. Las decisiones aún abiertas se señalan expresamente.

**Propósito de este documento:** explicar qué responsabilidad tiene cada componente, cómo se comunican los dos integrantes y cómo almacenaremos los datos en AWS sin introducir infraestructura innecesaria.

## Visión de alto nivel

```text
               Next.js (T47–T54)
          chat / negocio / repartidor / operador
                        |
                   HTTP/JSON
                        v
                 FastAPI (T30)
          /health  /predict  + operaciones
                        |
          ┌─────────────┼──────────────────┐
          v             v                  v
     Pedidos/estados  Cotizaciones     Predicción ML
     y asignaciones   costos/rutas      (inferencia)
          |             |                  |
          └─────────────┼──────────────────┘
                        |
             puertos/adaptadores de IO
                   /            \
              MongoDB          Amazon S3
           entidades/eventos   datasets/ models/ docs/

     Procesamiento/entrenamiento (offline Python)
     fuente REAL → Pandas / Dask / PySpark local
                → ML + MLP → métricas y artefacto
                → S3 models/ [solo con autorización]
```

**Separación importante:** `predict()` estima una variable respaldada por datos; el motor comercial aplica reglas de tarifa/vehículo. Los resultados comerciales no se presentan como métricas ML.

## Stack acordado o previsto

| Capa | Tecnología | Función |
|---|---|---|
| Dominio y servicios | Python 3.9+ | Entidades, casos de uso, validación |
| API | FastAPI + Pydantic | `/health`, `/predict`, OpenAPI; otros contratos a acordar |
| BD operacional | MongoDB | Pedidos, negocios, repartidores, estados, eventos, índices/validaciones |
| Objetos | AWS S3 con `boto3` | Datasets, modelos, documentos |
| ETL | Pandas, Dask, PySpark local | Transformaciones comparables y benchmarks |
| ML/DL | scikit-learn + framework MLP a acordar | Baseline, 3 familias ML y MLP pequeña |
| Demo | Next.js | Cuatro vistas y chat simulado |
| Local | Docker / Docker Compose | Demo reproducible |
| Infraestructura | Terraform + AWS | Provisionar recursos nuevos de despliegue con permiso |
| CI/CD | GitHub Actions | Tests/build/deploy, en tareas posteriores |

No incluir Kubernetes, colas, microservicios ni servicios administrados caros sin necesidad demostrable.

## Contratos API y coordinación entre integrantes

- **Obligatorios por guía:** `GET /health`, `POST /predict`, documentación OpenAPI.
- El payload de `/predict` dependerá del **dataset real y sus features disponibles al momento de cotizar**. No congelar un contrato con features inventadas. T03 documenta el borrador; T13/T19 lo hacen viable; T30/T31 lo integran.
- Endpoints de pedidos, cotizaciones, repartidores y simulador son **propuestos** y deben documentarse antes de implementarse. La UI debe consumir la API y no acceder directamente a MongoDB.
- Modelos de dominio y DTOs de API se separan: los datos del negocio no se hacen depender de esquemas específicos de una fuente de ML.
- Evitar que el entrenamiento y la inferencia dependan de MongoDB si no aporta al caso.

### Borrador de organización de código (T01 puede ajustarla)

```text
backend/
  src/delivery/
    domain/          # entidades y reglas puras
    services/        # casos de uso
    ports/           # contratos repositorio/storage/predictor
    adapters/        # MongoDB, S3, modelo ML
    api/             # FastAPI + DTOs
  tests/
ml/
  data/              # adquisición/ETL reproducibles
  experiments/       # entrenamiento, evaluación, artefactos
frontend/            # Next.js (futuro)
infra/terraform/      # IaC (futuro)
docs/                # este diseño y acuerdos
```

No crear código vacío de todas estas capas al inicio; T01 crea una base mínima y T03 ratifica el diseño. Usar imports y paths acordados entre agentes.

## Persistencia y AWS S3

La aplicación utiliza **dos tipos de almacenamiento diferentes**, porque resuelven necesidades distintas:

| Componente | Qué almacena | Por qué se utiliza |
|---|---|---|
| MongoDB | Negocios, pedidos, repartidores, estados y registros de operaciones simuladas | Permite consultar y actualizar entidades del sistema mediante CRUD, índices y validaciones. |
| Amazon S3 | Archivos de datasets, resultados procesados, artefactos de modelos y evidencia académica | Permite guardar objetos con rutas estables y separa los archivos grandes de la base de datos transaccional. |

### Configuración confirmada

- Bucket **ya existente**: `ml-kodigo-resources`.
- Región: `us-east-1`.
- Prefijos principales existentes o acordados: `datasets/`, `models/` y `docs/`.
- **No crear ni eliminar el bucket**. Terraform, cuando se implemente, debe consultarlo como recurso externo, salvo un cambio explícitamente autorizado.
- No se ha verificado en este documento el estado actual de versionado, cifrado, políticas IAM o acceso público del bucket. Inspeccionarlos antes de depender de ellos; no modificarlos sin autorización.

### Organización propuesta de objetos en el bucket

La estructura siguiente es una **convención de nombres para futuros objetos**, no una afirmación de que ya existan. En S3 son prefijos de claves, no carpetas físicas.

```text
s3://ml-kodigo-resources/
├── datasets/
│   └── <fuente-aprobada>/
│       └── <version>/
│           ├── raw/                 # Descarga original inalterada (si la licencia permite subirla)
│           ├── processed/           # Limpieza y transformaciones reproducibles
│           ├── splits/              # Particiones para experimentos, si corresponde
│           └── manifest.json        # Origen, hash, fecha, licencia y transformaciones
├── models/
│   └── delivery-duration/
│       └── <version-modelo>/
│           ├── pipeline.joblib      # Ejemplo de formato, sujeto al framework final
│           ├── metrics.json         # Resultados obtenidos, no valores predefinidos
│           └── manifest.json        # Dataset, features, unidades y dependencias
└── docs/
    └── <hito-o-evidencia>/           # Informes, gráficos y evidencias autorizadas
```

Los identificadores entre `< >` son marcadores de posición y **no** nombres ya aprobados. No crear directorios vacíos para simular que hay datasets o modelos disponibles. Los archivos originales pueden permanecer únicamente en la fuente externa si la licencia no autoriza redistribuirlos a S3.

### Recorrido reproducible de los datos

1. El integrante de datos identifica una fuente real, revisa permisos y verifica que el dataset es descargable (**T05**).
2. Documenta URL de origen, fecha, licencia, número de registros observado y checksum SHA-256; descarga la versión aprobada sin alterarla (**T06**).
3. Comprueba el significado y disponibilidad de la etiqueta objetivo, calidad y sesgos (**T07**).
4. Aplica un pipeline repetible con Pandas, equivalente en Dask y PySpark local. Conserva transformaciones, versiones y métricas obtenidas (**T08–T12**).
5. El entrenamiento y evaluación consumen **exactamente la versión validada** de datos; el resultado seleccionado se publica como artefacto versionado en `models/` solo cuando exista (**T13–T19**).
6. FastAPI carga una versión aprobada del modelo y ejecuta inferencia. No vuelve a entrenar en cada pedido (**T30–T31**).

**Acceso a datos:** localmente se puede descargar un objeto S3 a un directorio temporal o de trabajo ignorado por Git y procesarlo con herramientas Python. Esto simplifica la compatibilidad entre Pandas, Dask y PySpark local. Se registran la clave S3 y el hash para repetir experimentos. No depender de que todo el procesamiento ocurra dentro de AWS.

### Acceso seguro desde Python

- Usar `boto3`, las variables no sensibles `AWS_REGION` y `S3_BUCKET` y **credenciales fuera del repositorio**: perfil de AWS CLI para desarrollo, roles IAM para servicios desplegados.
- El frontend Next.js nunca recibe claves de AWS ni se conecta directamente a S3 con credenciales privilegiadas.
- Diferenciar permisos: lectura de datasets para ETL, escritura limitada al publicar objetos autorizados, lectura de modelos para inferencia y acceso restringido a evidencias.
- Si una persona no tiene permiso sobre una ruta, la tarea debe documentar la limitación; no ampliar IAM por iniciativa del agente.
- No subir datos personales innecesarios, archivos `.env`, credenciales ni muestras con información sensible.
- Verificar existencia, región y permisos **sin escribir** antes de conectar el servicio. No modificar el bucket en T01–T04.

### Política de versiones y reproducibilidad

- No sobreescribir objetos originales: cada versión debe quedar identificada por nombre, versión, hash o identificador de ejecución.
- Guardar un manifiesto por versión de datos y modelo con su procedencia y dependencias.
- No suponer que el *S3 Versioning* nativo está habilitado; puede utilizarse versionado lógico por prefijos.
- Diferenciar tres tipos de archivos: **datos observados**, **resultados transformados**, y **escenarios simulados**. Los escenarios de la UI no se añaden al entrenamiento real.

Para el detalle metodológico, ver [`DATA_ML.md`](DATA_ML.md).

## Despliegue objetivo (no implementarlo ahora)

```text
GitHub → GitHub Actions (test/build) → Docker image
                                        |
                              EC2 + Docker Compose
                              FastAPI + MongoDB
                                        |
                                       S3
                     Terraform: EC2, red, IAM y configuración
```

Next.js puede desplegarse junto al backend o por separado, según costos y facilidad demostrable. La decisión final se toma en T41. **Terraform debe consultar/referenciar el bucket ya existente**, no declararlo como recurso nuevo ni ejecutar cambios sobre él sin autorización. Un recurso de datos (`data`) sería una opción si su compatibilidad y permisos se comprueban cuando llegue T42. Antes de ejecutar `terraform apply`: revisar `plan`, costos, credenciales, permisos y alcance del cambio. Nunca aplicar automáticamente como parte de T01–T12. Docker Compose local debe poder funcionar sin un AWS pagado para las piezas que no requieren S3.

## Integración y orden

1. **T01–T04**: estructura, entorno, arquitectura y tipos de dominio (Ruben).
2. **T05–T12**: obtener/validar/transformar datos y comparar Pandas/Dask/PySpark (Guillermo, en paralelo).
3. **T13–T19**: entrenar/evaluar modelos con dataset validado (Ruben).
4. **T20–T34**: procesos de delivery y API/storage (responsables según backlog). Contratos revisados antes de conectarlos.
5. **T35–T40**: calidad, documentación y defensa.
6. **T41–T54**: despliegue y frontend, pendientes de asignar.

## Criterios transversales de calidad

Pruebas automatizadas, separación configuración/secretos, manejo explícito de errores, reproducibilidad, historial Git y revisión cruzada. No asumir que la API funciona con una predicción real hasta contar con artefacto entrenado y evaluado.
