# Asesor DecoView

**Mide primero. Compra una sola vez.**

Chatbot web hecho con **Streamlit** que funciona como asesor personal de compra para **DecoView**, una tienda peruana (ficticia) de mobiliario y decoración que vende solo en línea. El asesor ayuda al cliente a elegir un mueble que **entre en su espacio, combine con su ambiente y no termine devuelto**.

La IA corre sobre **Groq** (gratis, sin tarjeta de crédito) con el modelo `openai/gpt-oss-120b`.

---

## Índice

1. [¿De qué trata?](#1-de-qué-trata)
2. [Funcionalidades](#2-funcionalidades)
3. [Instalación](#3-instalación)
4. [Cómo funciona por dentro](#4-cómo-funciona-por-dentro)
5. [Personalización](#5-personalización)
6. [Mensajes de error y soluciones](#6-mensajes-de-error-y-soluciones)
7. [Límites conocidos](#7-límites-conocidos)

---

## 1. ¿De qué trata?

En una tienda de muebles que solo vende en línea, el cliente no puede ver el producto en su casa antes de comprarlo. Por eso la causa más común de devoluciones es que el mueble **no entra, es de un color que no combina o no va con el estilo del ambiente**.

Este asesor ataca ese problema con una conversación:

1. El cliente cuenta cómo es su espacio: ambiente, medidas, estilo y colores.
2. El asesor pregunta lo que falta y, con esa información, recomienda qué tipo de mueble conviene.
3. Explica **por qué** esa elección reduce el riesgo de devolución (escala, color, armonía) y ofrece una o dos alternativas.
4. Invita al cliente a comprobarlo en el **Módulo RD**, el visualizador 3D de la tienda.

El asesor habla en español peruano, trata de "tú" y tiene la instrucción de **no inventar productos, precios ni stock**.

---

## 2. Funcionalidades

| Funcionalidad | Qué hace |
|---|---|
| **Chat con IA** | Conversación en tiempo real con memoria mientras la pestaña siga abierta. |
| **Ficha de tu espacio** | En la barra lateral, el cliente anota ambiente, ancho × largo (la app calcula los m²), estilo y colores. Esa ficha se envía al modelo en cada mensaje, así no vuelve a preguntar lo que ya sabe. |
| **Sugerencias de inicio** | Cuatro preguntas de ejemplo para empezar con un clic. Solo aparecen con la conversación vacía. |
| **Reiniciar conversación** | Borra el historial y empieza de cero. |
| **Errores explicados** | Si algo falla (clave inválida, límite gratuito, sin conexión…), el chat dice la causa exacta y qué hacer. Ver [sección 6](#6-mensajes-de-error-y-soluciones). |
| **Diseño propio** | Paleta de materiales (cal, lino, nogal, terracota), tipografía Fraunces + Figtree y una wincha (cinta métrica) como elemento de marca. Se adapta a móvil. |

---

## 3. Instalación

### Requisitos

- **Python 3.10 o superior**. Compruébalo con `python3 --version`.
- Una **API Key gratuita de Groq** (el paso 3 explica cómo conseguirla).

### Paso 1: descargar el proyecto

```bash
git clone <url-de-este-repositorio> "ChatBot DecoView"
cd "ChatBot DecoView"
```

### Paso 2: crear el entorno virtual e instalar dependencias

Un entorno virtual es una carpeta con una copia aislada de Python, para que las librerías de este proyecto no se mezclen con las de otros.

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Paso 3: configurar tu API Key de Groq

1. Entra a **https://console.groq.com/keys** e inicia sesión con Google, GitHub o correo. No pide tarjeta.
2. Haz clic en **Create API Key**, ponle un nombre (por ejemplo `decoview`) y cópiala. Empieza con `gsk_`.
3. Crea tu archivo de secretos copiando la plantilla que viene en el repositorio:

   ```bash
   # macOS / Linux
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml

   # Windows (PowerShell)
   Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
   ```

4. Abre `.streamlit/secrets.toml` y pega tu clave entre las comillas:

   ```toml
   GROQ_API_KEY = "gsk_tu-clave-real"
   ```

> **Importante:** `secrets.toml` está en `.gitignore` y **nunca debe subirse** a un repositorio. La plantilla `secrets.toml.example` sí se sube porque no contiene ninguna clave real.

### Paso 4: ejecutar la app

Con el entorno virtual activado:

```bash
streamlit run app_openai.py
```

La app se abre en el navegador, normalmente en **http://localhost:8501**. Para detenerla, pulsa `Ctrl + C` en la terminal.

---

## 4. Cómo funciona por dentro

### Estructura del proyecto

```
ChatBot DecoView/
├── app_openai.py                 → Toda la lógica: interfaz, ficha, chat y llamada a la IA
├── styles.css                    → Diseño: colores, tipografías, wincha, chat y barra lateral
├── requirements.txt              → Dependencias (streamlit, openai)
├── .gitignore                    → Excluye secretos, entorno virtual, cachés y herramientas locales
└── .streamlit/
    ├── config.toml               → Tema de Streamlit (colores base de la app)
    ├── secrets.toml.example      → Plantilla para tu API Key (se sube al repo)
    └── secrets.toml              → Tu API Key real (lo creas tú, NO se sube)
```

### ¿Por qué se usa la librería `openai` si la IA es de Groq?

Groq ofrece una API **compatible con la de OpenAI**, así que el código usa el cliente oficial `openai` de Python y solo le cambia dos cosas: la dirección del servidor (`base_url="https://api.groq.com/openai/v1"`) y el nombre del modelo. El archivo conserva el nombre `app_openai.py` por historia del proyecto, que empezó usando OpenAI.

### Flujo de una pregunta

```
El cliente escribe (o hace clic en una sugerencia)
        │
        ▼
El mensaje se guarda en el historial (st.session_state.messages)
        │
        ▼
Se arma el paquete que se envía a Groq:
   1. SYSTEM_PROMPT      → la "personalidad" y las reglas del asesor
   2. Ficha del espacio  → ambiente, medidas, estilo y colores (si se llenaron)
   3. Historial completo → todos los mensajes anteriores de la conversación
        │
        ▼
Groq (openai/gpt-oss-120b) genera la respuesta
        │
        ▼
Se muestra en el chat y se guarda en el historial
```

### Las piezas clave de `app_openai.py`

- **`SYSTEM_PROMPT`**: el texto que define quién es el asesor, el contexto de la empresa, cómo debe comportarse y cómo estructurar sus respuestas. Es el "cerebro" del bot: la app no tiene base de datos ni catálogo, así que todo lo que el asesor sabe sale de aquí.
- **`contexto_ficha()`**: convierte lo que el cliente llenó en la barra lateral en un mensaje de sistema adicional. No se guarda en el historial, se recalcula en cada pregunta, así que si el cliente cambia una medida el asesor la usa de inmediato.
- **`st.session_state.messages`**: la memoria de la conversación. Vive en la sesión del navegador y se pierde al recargar la página.
- **Manejo de errores**: cada tipo de error de la API tiene su propio mensaje en español (ver [sección 6](#6-mensajes-de-error-y-soluciones)).

### El modelo "piensa" antes de responder

`openai/gpt-oss-120b` es un modelo de razonamiento: antes de escribir la respuesta visible gasta tokens pensando internamente (eso no se muestra en el chat). Si una pregunta es muy larga y se agota el presupuesto (`max_tokens=1200`) mientras piensa, la respuesta llega vacía. La app lo detecta y muestra un aviso en lugar de un mensaje en blanco.

---

## 5. Personalización

Todo se cambia editando `app_openai.py` o `styles.css`:

| Quiero cambiar… | Dónde |
|---|---|
| El modelo de IA | Variable `GROQ_MODEL`. Modelos disponibles: https://console.groq.com/docs/models |
| La personalidad o las reglas del asesor | Texto `SYSTEM_PROMPT` |
| Qué tan creativa o larga es la respuesta | `temperature` y `max_tokens` en la llamada `client.chat.completions.create(...)` |
| Las preguntas de ejemplo | Lista `SUGERENCIAS` |
| Las opciones de ambiente o estilo | Los `st.selectbox` dentro de `with st.sidebar:` |
| Colores y tipografías | Variables al inicio de `styles.css` (`--terracota`, `--cal`, `--lino`…) y `.streamlit/config.toml` |

---

## 6. Mensajes de error y soluciones

Si algo falla, el chat muestra un mensaje claro y, cuando sirve, el detalle técnico exacto:

| Mensaje | Causa | Qué hacer |
|---|---|---|
| 🔑 No existe el archivo de secretos | Falta `.streamlit/secrets.toml` | Cópialo desde la plantilla (paso 3 de la instalación) |
| 🔑 Falta la clave `GROQ_API_KEY` | El archivo existe pero no tiene esa línea | Agrega `GROQ_API_KEY = "gsk_..."` |
| 🔑 API Key inválida o revocada | Clave mal copiada, borrada o todavía es la de ejemplo | Genera una nueva en https://console.groq.com/keys |
| ⏳ Límite gratuito alcanzado | Superaste las peticiones o tokens por minuto/día del plan gratuito | Espera un minuto; revisa tus límites en https://console.groq.com/settings/limits |
| ⏱️ Tiempo de espera agotado | Groq tardó demasiado en responder | Revisa tu conexión y reintenta |
| 🌐 No se pudo conectar | Sin internet, o un firewall/proxy lo bloquea | Revisa tu red |
| ❓ El modelo ya no existe | Groq retiró o renombró el modelo | Elige uno vigente en https://console.groq.com/docs/models y actualiza `GROQ_MODEL` |
| ⛔ Permiso denegado | Tu cuenta no puede usar ese modelo o región | Revisa tu cuenta en Groq |
| ⚠️ Petición inválida | El formato enviado a Groq tiene un problema | Revisa el detalle técnico mostrado |
| 🛠️ Error interno de Groq | Falla en los servidores de Groq | Reintenta en unos minutos |
| 🤔 Se acabaron los tokens pensando | El modelo agotó su presupuesto razonando | Haz una pregunta más corta o reinicia la conversación |

**Otros problemas comunes**

- **`command not found: streamlit`**: el entorno virtual no está activado. Actívalo (paso 2) o ejecuta `./.venv/bin/streamlit run app_openai.py`.
- **Sigue apareciendo un error que ya corregiste**: Streamlit puede estar ejecutando la versión anterior del código. Detén la app con `Ctrl + C`, vuelve a lanzarla y recarga el navegador.

---

## 7. Límites conocidos

- **No hay catálogo real.** El asesor no está conectado a productos, precios ni stock. Tiene la instrucción de no inventarlos, pero puede llegar a mencionar productos que no existen. Conectarle el catálogo real es la siguiente mejora natural.
- **Sin memoria persistente.** La conversación se pierde al recargar la página, porque no hay base de datos.
- **Sin autenticación.** Si publicas la app (por ejemplo en Streamlit Community Cloud), cualquiera con el enlace puede usarla y consumir tu cuota gratuita de Groq.
- **Plan gratuito de Groq.** Alcanza de sobra para uso personal o demos, pero no está pensado para muchos usuarios al mismo tiempo.
