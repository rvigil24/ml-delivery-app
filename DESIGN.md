---
{
  "name": "Asistente de Delivery Económico",
  "description": "Sistema visual de la demostración local de entregas simuladas.",
  "colors": {
    "canvas": "#f3f6f4",
    "surface": "#ffffff",
    "ink": "#172f28",
    "muted": "#5c7068",
    "line": "#dce5df",
    "primary": "#17694b",
    "primary-hover": "#10543b",
    "rail": "#143c30",
    "rail-muted": "#b8cec2",
    "tint": "#e4f1e9",
    "chat": "#eee9df",
    "bubble": "#d9f4cf",
    "focus": "#3c8f70",
    "nav-text": "#d8e8df",
    "nav-hover": "#28513f",
    "nav-active": "#d6edce",
    "nav-active-text": "#163b2b",
    "status-bg": "#edf0ee",
    "status-text": "#51665b",
    "input-border": "#d2dfd6",
    "secondary-border": "#c4d6ca"
  },
  "typography": {
    "headline": {
      "fontFamily": "\"Segoe UI\", \"Helvetica Neue\", Arial, sans-serif",
      "fontSize": "clamp(1.8rem, 2.7vw, 2.65rem)",
      "fontWeight": 650,
      "lineHeight": 1.22,
      "letterSpacing": "-0.035em"
    },
    "title": {
      "fontFamily": "\"Segoe UI\", \"Helvetica Neue\", Arial, sans-serif",
      "fontSize": "1.13rem",
      "fontWeight": 650,
      "lineHeight": 1.22,
      "letterSpacing": "-0.015em"
    },
    "body": {
      "fontFamily": "\"Segoe UI\", \"Helvetica Neue\", Arial, sans-serif",
      "fontSize": "15px",
      "fontWeight": 400,
      "lineHeight": 1.6
    },
    "label": {
      "fontFamily": "\"Segoe UI\", \"Helvetica Neue\", Arial, sans-serif",
      "fontSize": "13px",
      "fontWeight": 600
    }
  },
  "rounded": {
    "panel": "14px",
    "button": "7px",
    "control": "8px",
    "message": "10px",
    "tag": "5px",
    "circle": "50%"
  },
  "spacing": {
    "4": "4px",
    "8": "8px",
    "12": "12px",
    "14": "14px",
    "16": "16px",
    "20": "20px",
    "24": "24px",
    "28": "28px",
    "32": "32px",
    "44": "44px"
  },
  "components": {
    "button-primary": {
      "backgroundColor": "{colors.primary}",
      "textColor": "{colors.surface}",
      "rounded": "{rounded.button}",
      "padding": "10px 16px",
      "typography": "{typography.label}"
    },
    "button-primary-hover": {
      "backgroundColor": "{colors.primary-hover}"
    },
    "button-secondary": {
      "backgroundColor": "{colors.surface}",
      "textColor": "{colors.primary}",
      "rounded": "{rounded.button}",
      "padding": "10px 16px",
      "typography": "{typography.label}"
    },
    "panel": {
      "backgroundColor": "{colors.surface}",
      "rounded": "{rounded.panel}"
    },
    "nav-link": {
      "textColor": "{colors.nav-text}",
      "rounded": "{rounded.control}",
      "padding": "13px 16px"
    },
    "nav-active": {
      "backgroundColor": "{colors.nav-active}",
      "textColor": "{colors.nav-active-text}"
    },
    "status-label": {
      "backgroundColor": "{colors.status-bg}",
      "textColor": "{colors.status-text}",
      "rounded": "{rounded.tag}",
      "padding": "4px 8px"
    },
    "input-preview": {
      "backgroundColor": "{colors.surface}",
      "textColor": "{colors.muted}",
      "rounded": "{rounded.control}",
      "padding": "11px 14px"
    },
    "message-incoming": {
      "backgroundColor": "{colors.surface}",
      "rounded": "{rounded.message}",
      "padding": "12px 14px 7px"
    },
    "message-outgoing": {
      "backgroundColor": "{colors.bubble}",
      "rounded": "{rounded.message}",
      "padding": "12px 14px 7px"
    }
  }
}
---

# Design System: Asistente de Delivery Económico

## Overview

**Creative North Star: "Espacio de trabajo de entregas"**

Paneles blancos sobre fondo verde grisáceo, navegación verde profundo y acento verde. La densidad favorece leer pedidos, estados y mensajes con una tipografía de interfaz compartida.

El chat usa un fondo cálido y burbujas alineadas por emisor; conserva visibles las indicaciones de simulación y de vista previa. Las cuatro vistas comparten navegación y jerarquía.

**Key Characteristics:**

- Superficies claras y separadores finos.
- Verde para navegación y acciones.
- Chat cálido con emisor reconocible.

## Colors

El verde profundo organiza el trabajo y los tonos claros distinguen contenido y conversación. Los valores normativos están en el frontmatter; la fuente implementada es `frontend/src/app/globals.css`.

### Primary

`primary` identifica acciones y pasos; `primary-hover` confirma interacción. `rail` sostiene la navegación, con selección `nav-active` y texto `nav-active-text`. `tint` acompaña avisos e iconos.

### Neutral

`canvas` es el fondo general; `surface`, los paneles. `ink` y `muted` separan contenido principal y apoyo; `line` delimita regiones. `chat` aporta el fondo cálido y `bubble` identifica al cliente. `status-bg` y `status-text` mantienen legibles los estados de muestra. `focus` señala el foco de teclado.

## Typography

Segoe UI, Helvetica Neue, Arial y sans-serif forman la pila real de toda la interfaz. No hay una fuente display independiente. `headline` corresponde a h1; `title`, a h2; `body`, al texto base; `label`, a botones y acciones. h3 usa tamaño de cuerpo relativo y peso seminegrita. Las tablas y apoyos reducen el tamaño; los identificadores se pueden partir y las coordenadas usan cifras tabulares. Los párrafos se limitan a 70ch; h1 a 23ch. En móvil h1 pasa a 29px.

## Layout

La aplicación usa una barra lateral de 232px y contenido flexible; el contenedor principal llega a 1560px con margen automático. El padding principal de escritorio es 46px 44px 56px. Las columnas auxiliares miden 266px en operaciones y 250px en chat, separadas por 32px.

A 1240px se apilan las columnas auxiliares; a 960px la barra pasa a 196px y se reduce el padding. A 700px la barra se convierte en cabecera con cuatro enlaces horizontales, el contenido se apila y el padding principal queda en 28px 20px 40px. Las tablas conservan desplazamiento horizontal propio. La escala de espaciado registra pasos repetidos observados, sin imponer un múltiplo único.

## Elevation & Depth

Las superficies son planas: bordes y cambios de tono aportan profundidad. No existen sombras ambientales. La navegación seleccionada usa una sombra interior transitoria como respuesta visual; se aplica únicamente cuando no se solicita reducir movimiento. Duración, curva y foco se registran en el sidecar.

## Shapes

Paneles y chat comparten esquinas suaves; controles y botones usan radios menores. Avatares y envío son circulares. Las burbujas conservan una esquina superior recta del lado del emisor. Los paneles recortan su contenido y usan un borde fino.

## Components

- **Botones:** primario verde y secundario blanco con borde; padding compartido y altura mínima de 44px. El hover cambia el fondo; el foco conserva el contorno global.
- **Navegación:** icono SVG y texto, selección verde clara y `aria-current`. En móvil se apilan icono y etiqueta dentro de cada enlace; el cambio de color dura 130ms.
- **Paneles y tablas:** fondo blanco, borde de separación y cabeceras suaves; el contenido tabular puede desplazarse sin ensanchar el documento.
- **Etiquetas:** estado compacto y aviso de ejemplo; acompañar el color con texto explícito.
- **Campo de chat:** borde fino y fondo blanco. En T47 está deshabilitado junto con el envío y muestra explicación persistente; no documentar un flujo de edición todavía inexistente.
- **Mensajes:** entrantes blancos a la izquierda y salientes verdes a la derecha; ancho máximo de 82%, ampliado a 92% en móvil. Remitente en texto pequeño al pie.
- **Recorrido:** pasos conectados por una línea vertical, primer punto verde y descripciones breves. Se reorganiza al apilar columnas.

## Do's and Don'ts

### Do:

- Do conservar la identificación de simulación y los estados sin consultar.
- Do mantener foco visible, navegación por teclado y adaptación a móvil.
- Do usar los tokens existentes y SVG de trazo para iconos.

### Don't:

- Don't presentar la vista previa como una operación realizada.
- Don't ocultar la explicación de los controles deshabilitados.
- Don't sustituir la navegación móvil por controles sin etiquetas.
