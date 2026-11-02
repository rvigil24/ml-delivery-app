# Asistente de Delivery Económico

Proyecto integrador de Python, Ciencia de Datos y Machine Learning. Equipo de dos integrantes. El repositorio comienza con **documentación operativa**, no con una aplicación previamente implementada: los agentes crearán el código al ejecutar cada tarea.

## Qué se construirá

Un MVP para pequeños comedores, pupuserías y negocios de almuerzos/cenas sin repartidor propio. Simula solicitudes por WhatsApp, cotiza envíos locales, gestiona entregas individuales/agrupadas, asigna repartidores simulados en bicicleta o motocicleta, registra efectivo ficticio y muestra resultados en Next.js. La predicción de duración usará **datos reales verificables** y modelos ML/DL evaluados; los costos comerciales se calculan por reglas explícitas, no por resultados fabricados.

## Documentación y configuración base

| Archivo | Para qué sirve |
|---|---|
| `README.md` | Introducción y comienzo rápido para ambos |
| `AGENTS.md` | Reglas compartidas para Codex o Claude Code |
| `docs/SPEC.md` | Requisitos y flujo de negocio del MVP |
| `docs/ARCHITECTURE.md` | Componentes, interfaces, datos, S3 y despliegue |
| `docs/DATA_ML.md` | Guía de obtención, procesamiento y ML/DL |
| `docs/TASKS.md` | 54 tareas, responsables y pasos de inicio verificables |
| `.env.example` | Variables de entorno no secretas |
| `.gitignore` | Exclusiones de Git |

Este paquete conserva los nombres y asignaciones reflejados en la última copia disponible del backlog de 54 tareas. **La hoja Excel compartida sigue siendo la fuente de verdad** para nuevos cambios de responsables, estados y prioridades.

## Configuración de AWS ya decidida

- S3 bucket **existente**: `ml-kodigo-resources`
- Región: `us-east-1`
- Prefijos: `datasets/`, `models/`, `docs/`
- No crear ni borrar el bucket. No subir objetos ni cambiar IAM sin aprobación.
- MongoDB se utilizará para entidades y estados del negocio; S3 para archivos/datasets/modelos.

## Inicio de ambos integrantes

1. Descomprimir en una carpeta `whatsapp-delivery/`.
2. Integrante que crea el repositorio: `git init` (o crear directamente el repositorio remoto y clonarlo); revisar `.gitignore`.
3. Ambos deben trabajar sobre **el mismo repositorio remoto** y consultar `AGENTS.md` y `docs/TASKS.md`.
4. Crear ramas separadas por tarea: ejemplo `feat/T01-estructura` y `data/T05-fuentes`.
5. Revisar cambios y pruebas antes de integrarlos a la rama compartida. No ejecutar despliegues AWS para probar tareas iniciales.

### Primer prompt del integrante Ruben (T01)

> Lee `AGENTS.md`, `README.md`, `docs/SPEC.md`, `docs/ARCHITECTURE.md` y `docs/TASKS.md`. Implementa exclusivamente T01, respetando los criterios de aceptación. No hagas commits automáticos, no implementes otras tareas y al final muestra archivos cambiados y verificaciones realizadas.

### Primer prompt del integrante Guillermo (T05)

> Lee `AGENTS.md`, `docs/SPEC.md`, `docs/DATA_ML.md` y `docs/TASKS.md`. Trabaja exclusivamente en T05: investiga y verifica fuentes reales de entregas adecuadas para el objetivo candidato. Documenta las fuentes, licencia, accesibilidad, variables y evidencia; no inventes etiquetas ni entrenes modelos todavía. No cambies archivos de arquitectura ajenos ni subas nada a S3 sin permiso.

**Importante para trabajo paralelo:** Guillermo puede investigar T05 de inmediato, pero debe esperar a que el repositorio/base esté compartido para incorporar su documentación. Ruben puede seguir con T02–T04 mientras se validan fuentes de datos.

## Orden de lectura para cualquier agente

1. `AGENTS.md`
2. `docs/TASKS.md` (tarea exacta y responsable)
3. `docs/SPEC.md` (reglas del negocio)
4. `docs/ARCHITECTURE.md` (contratos e integración)
5. `docs/DATA_ML.md` (para tareas de datos/ML)

Las guías académicas oficiales del curso prevalecen sobre estas notas. El equipo confirmará con el docente el alcance permitido de la asistencia mediante agentes antes de presentar el trabajo.

## Estructura inicial — T01

```text
backend/
  src/delivery/      # Base del código Python de dominio, servicios y API
  tests/             # Pruebas del backend
ml/
  data/              # Código de adquisición y ETL, no datasets versionados
  experiments/       # Código de entrenamiento y evaluación
frontend/            # Aplicación Next.js futura
infra/
  terraform/         # Infraestructura futura
docs/                # Especificación, arquitectura, datos y tareas compartidas
```

Los directorios iniciales contienen únicamente `.gitkeep` para conservarlos en
Git. Las capas internas del backend se describen en `docs/ARCHITECTURE.md` y se
crearán al abordar sus tareas. FastAPI, MongoDB y S3 se integrarán posteriormente;
Docker/Compose se incorporarán en T34 y Terraform en T42.

T01 no incluye una aplicación ejecutable, dependencias instaladas, endpoints,
datos ni modelos. El entorno Python y pytest corresponden a T02; Next.js comienza
en T47. `.env.example` contiene solo la región y el bucket existente acordados,
sin claves ni conexiones. Los datos locales deben guardarse en las rutas
ignoradas `data/`, `ml/data/raw/`, `ml/data/processed/` o `ml/data/splits/`; los
artefactos, en `models/`, `artifacts/` o `ml/experiments/artifacts/`.

El remoto `origin` está configurado en
`https://github.com/rvigil24/ml-delivery-app.git`. Al verificar T01, la rama local
actual es `main`, todavía sin commits ni ramas publicadas en el remoto. El primer
commit y el push quedan pendientes de una instrucción explícita.
Por indicación de Ruben, T01 no requiere aprobación de Guillermo. Esta excepción
aplica únicamente a T01; el backlog no se actualiza automáticamente.
