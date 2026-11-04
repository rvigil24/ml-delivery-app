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


## Extensión T49 — panel de negocio

Se conserva el sistema T47. Selector de negocio y estado, tabla de pedidos y
panel de detalle/historial; dos columnas en escritorio y bloques apilados en
móvil. Datos de API, carga/error/vacío reales. Confirmación/cancelación según
estado; cancelación inline, sin modal. Nada cambia visualmente como guardado
hasta respuesta válida del servidor; conflictos muestran error y estado actual.
No se reemplazan tokens o identidad, ni se presenta el selector como autenticación.

Cierre T49: revisión independiente ship con seis capturas full-page válidas
en escritorio/móvil, sin correcciones materiales. La lectura Atlas se comprobó
sin modificar registros; las escrituras probadas pertenecen a fixtures aisladas.


## Extensión T50 — panel del repartidor

Se hereda T47. Selectores de repartidor y ruta, perfil actual y lista numerada de
paradas (los números expresan el orden operativo). Inicio/ubicaciones y distancia
de referencia, sin mapa o GPS ficticio. La próxima parada se destaca con el mismo
verde; sólo se ofrece su avance y, al entregar todo, el cierre explícito de ruta.
Estados reales de carga/error/vacío; sin cambios optimistas. En móvil se apilan
los controles y cada parada conserva lectura sin desborde. No cambia la identidad.

Cierre T50: revisión independiente ship; seis capturas full-page válidas de
vacío real y rutas activas/cerradas con fixtures aisladas en ambos tamaños.
Sin correcciones materiales; la lectura de API/servicio confirmó el dictamen.

T51: Operaciones consulta pedidos/efectivo y solicita desglose a FastAPI.
Mantiene la identidad existente; distingue registro ausente y previsualización
sin guardar. Revisión final ship, escritorio/móvil. No altera DESIGN.md ni tokens.

T52: el chat confirma sólo tras guardar por API; muestra referencia/estado y
enlace al negocio correspondiente. Error recuperable conserva referencia.
Revisión final ship: cuatro capturas escritorio/móvil. Mundo visual conservado.
