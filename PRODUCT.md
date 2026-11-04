# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Next.js y TypeScript para la interfaz; FastAPI, MongoDB Atlas y modelos propios desde S3 para el backend existente.

## Users

Cliente, negocio, repartidor aprobado y operador. Ruben usa las cuatro vistas durante la exposición del proyecto.

## Product Purpose

Gestionar pedidos de comida y sus entregas locales simuladas, y explicar el recorrido desde la solicitud hasta la entrega y el registro de efectivo. Dos modelos estiman duración y riesgo de retraso.

## Operating Context

La pantalla inicial es Operaciones; un menú permite cambiar entre los cuatro roles. Cliente representa un chat de WhatsApp mediante un flujo guiado, sin LLM y sin conexión a WhatsApp real. Decisiones confirmadas por Ruben en esta conversación.

## Capabilities and Constraints

T47 cubre layout, navegación y ejecución local. T48 pide primero dirección y punto de entrega, consulta negocios por cercanía y menús en FastAPI, permite elegir productos/cantidades y prepara una confirmación local simulada; sin enviar ni persistir el pedido. El catálogo de productos es de ejemplo, versionado con la API y sin precios inventados. T49 consulta pedidos del negocio, detalle e historial en la API y permite confirmar/cancelar según estado y requisitos del backend, sin cambios optimistas. T50 consulta asignaciones y paradas de la API, registra avances secuenciales y libera al repartidor al finalizar una ruta entregada, sin crear rutas ficticias. T51–T54 incorporan operaciones y el resto de integración. No inventar cotizaciones, métricas, estados consultados, rutas viales ni datos de entrenamiento. Ejemplos claramente identificados; sin credenciales en el frontend.

## Brand Commitments

Nombre: Asistente de Delivery Económico. Español natural y breve. Cliente similar a WhatsApp e identificado como simulación; paneles claros con navegación convencional.

## Evidence on Hand

examples/exposicion.json contiene negocios, repartidores y pedidos ficticios aprobados para exposición. README y docs/ARCHITECTURE.md describen la API real desplegada. reports/ contiene presentación y evidencias científicas.

## Product Principles

- Mostrar el estado de los datos sin aparentar operaciones realizadas.
- Mantener las reglas y predicciones en el backend.
- Facilitar el cambio de rol durante la exposición.
- Distinguir la simulación de los mensajes, viajes y cobros reales.
