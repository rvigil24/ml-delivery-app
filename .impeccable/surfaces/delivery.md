# Cuatro vistas de la demo

Mode: Operate. Dirección fijada por el usuario: chat similar a WhatsApp, identificación visible de simulación, Operaciones como inicio y menú entre cuatro roles. Se aplica el modo Operate sin sortear una identidad alternativa a la referencia solicitada.

## Direction contract

THESIS: un espacio de trabajo para seguir entregas y alternar roles, con el chat como punto de entrada del cliente.

OWN-WORLD: paneles blancos sobre fondo verde grisáceo, navegación verde profundo, acento verde y tipografía de interfaz legible. El chat adopta encabezado de contacto, fondo cálido y burbujas alineadas por emisor.

STORY: el presentador entra en Operaciones, reconoce los ejemplos y cambia a Cliente, Negocio o Repartidor sin perder la navegación.

FIRST VIEWPORT: barra lateral de 232 px a la izquierda, encabezado y tabla de pedidos en el área central; guía del recorrido al lado. En móvil, navegación horizontal y contenido apilado. Cliente dedica el área principal a una conversación de muestra, con etiqueta Simulación de WhatsApp.

FORM: interfaz web convencional de operaciones con referencia WhatsApp indicada por Ruben; seed: none (unavailable). La referencia explícita sustituye la elección de un mundo nuevo. Firma: el mismo recorrido de entrega aparece como secuencia de estados legible entre vistas; selección de navegación verde. Sin imágenes generadas ni mapa vial ficticio.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Cierre

Revisión independiente: ship para T47; ocho capturas de escritorio/móvil válidas,
sin correcciones materiales. Tokens extraídos en DESIGN.md y .impeccable/design.json.
Sin imágenes de producto ni comp generada; no hay atribuciones de raster pendientes.


## Extensión T48 — dirección y menú antes del pedido

La vista Cliente conserva el mundo visual T47. Corrección explícita de Ruben:
dirección y ubicación → negocios ordenados por cercanía desde API → menú desde
API con productos/cantidades → revisión → confirmación local simulada.
El usuario elige productos publicados en el catálogo de ejemplo; texto libre sólo
para dirección e indicaciones opcionales. El punto se selecciona con GPS,
coordenadas manuales o ejemplo; no se geocodifica el texto. No hay precios falsos,
LLM ni envío real. Se añaden estados de consulta/error/vacío, opciones de ubicación
y controles de cantidad usando la misma paleta, tipografía y componentes.

Cierre revisado tras correcciones: ship; seis capturas full-page válidas de
dirección, menú y revisión en 1440/390 px. Sin correcciones materiales.
