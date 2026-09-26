import streamlit as st
import openai
from openai import OpenAI
from streamlit.errors import StreamlitSecretNotFoundError
from pathlib import Path

st.set_page_config(
    page_title="Asesor DecoView",
    page_icon="🛋️",
    layout="centered",
    initial_sidebar_state="auto"
)

# Cargar CSS externo (tokens y estilos de la interfaz)
css_file = Path(__file__).parent / "styles.css"
if css_file.exists():
    with open(css_file, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<p class="dv-eyebrow">DecoView · Asesor de compra</p>
<h1 class="dv-title">Mide primero. <em>Compra una sola vez.</em></h1>
<p class="dv-lead">
    Cuéntame cómo es tu espacio (medidas, colores, estilo) y te ayudo a elegir un mueble
    que entre, combine y se quede en tu casa.
</p>
<div class="dv-wincha" aria-hidden="true">
    <span style="left:0">0</span><span style="left:80px">10</span><span style="left:160px">20</span>
    <span style="left:240px">30</span><span style="left:320px">40</span><span style="left:400px">50</span>
    <span style="left:480px">60</span><span style="left:560px">70</span><span style="left:640px">80 cm</span>
</div>
""", unsafe_allow_html=True)

# API Key de Groq (gratis en https://console.groq.com/keys)
# Usamos la librería "openai" porque Groq expone una API compatible con la de OpenAI:
# solo cambia la URL base (base_url) y el nombre de los modelos.
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "openai/gpt-oss-120b"

try:
    api_key = st.secrets["GROQ_API_KEY"]
except StreamlitSecretNotFoundError:
    st.error(
        "🔑 **No existe el archivo de secretos.**\n\n"
        "Falta el archivo `.streamlit/secrets.toml`. Créalo a partir de la plantilla:\n\n"
        "```bash\ncp .streamlit/secrets.toml.example .streamlit/secrets.toml\n```\n\n"
        "y pega tu clave en `GROQ_API_KEY`.\n\n"
        "Consigue tu clave gratis en https://console.groq.com/keys"
    )
    st.stop()
except KeyError:
    st.error(
        "🔑 **El archivo `.streamlit/secrets.toml` existe, pero no tiene la clave `GROQ_API_KEY`.**\n\n"
        "Agrégala así:\n\n"
        "```toml\nGROQ_API_KEY = \"gsk_...tu-clave...\"\n```\n\n"
        "Consigue tu clave gratis en https://console.groq.com/keys"
    )
    st.stop()

if not api_key or not api_key.strip():
    st.error("🔑 **`GROQ_API_KEY` está vacía** en `.streamlit/secrets.toml`. Pega tu clave real entre las comillas.")
    st.stop()

try:
    client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
except Exception as e:
    st.error(f"❌ **No se pudo inicializar el cliente de Groq.**\n\nDetalle técnico: `{e}`")
    st.stop()

SYSTEM_PROMPT = """
Eres el **Asesor Personal de Compra de DecoView**, una tienda peruana de mobiliario y decoración para el hogar fundada en 2024.

### Tu objetivo principal:
Ayudar a los clientes a elegir el producto correcto para su espacio real, reduciendo al máximo la probabilidad de devolución.

### Contexto de la empresa:
- Vendemos solo en línea (sin tiendas físicas).
- Atendemos principalmente Lima Metropolitana.
- El mayor problema son las devoluciones por color, tamaño o que el mueble no combina con el ambiente del cliente.
- Contamos con un módulo de visualización 3D llamado "Módulo RD".

### Cómo debes comportarte:
1. Sé cercano, amable y profesional. Usa siempre el "tú".
2. Habla en español peruano natural.
3. Nunca inventes productos, precios o stock.
4. Siempre prioriza reducir el riesgo de devolución.

### Proceso de razonamiento:
1. Identifica el tipo de ambiente (sala, dormitorio, etc.).
2. Pregunta o infiere estilo, colores y tamaño del espacio.
3. Recomienda productos considerando escala, color y armonía.
4. Justifica por qué esa recomendación reduce el riesgo de devolución.
5. Ofrece alternativas y sugiere usar el Módulo RD.

### Estructura de respuesta:
- Observación o pregunta empática
- Recomendación clara y justificada
- 1 o 2 alternativas
- Invitación a visualizar o seguir preguntando
"""

AVATARES = {"assistant": ":material/chair:", "user": ":material/person:"}

SUGERENCIAS = [
    "Busco un sofá para una sala de 3 × 4 m",
    "¿Qué color de mesa combina con piso de madera clara?",
    "Mi dormitorio es pequeño, ¿qué cama me recomiendas?",
    "Quiero renovar mi comedor sin gastar mucho",
]


def reiniciar_conversacion():
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.session_state.pop("pendiente", None)


def usar_sugerencia(texto):
    st.session_state.pendiente = texto


if "messages" not in st.session_state:
    reiniciar_conversacion()

with st.sidebar:
    st.markdown(
        '<p class="dv-ficha-titulo">Ficha de tu espacio</p>'
        '<p class="dv-ficha-nota">Lo que anotes aquí lo tendré en cuenta en cada respuesta.</p>',
        unsafe_allow_html=True,
    )
    ambiente = st.selectbox(
        "Ambiente",
        ["Sin definir", "Sala", "Comedor", "Dormitorio", "Estudio / oficina", "Terraza"],
    )
    col_ancho, col_largo = st.columns(2)
    ancho = col_ancho.number_input("Ancho (m)", min_value=0.0, max_value=20.0, step=0.1, format="%.1f")
    largo = col_largo.number_input("Largo (m)", min_value=0.0, max_value=20.0, step=0.1, format="%.1f")

    if ancho and largo:
        medida = f"{ancho:.1f} × {largo:.1f} m <small>· {ancho * largo:.1f} m²</small>"
    else:
        medida = "<small>por medir</small>"
    st.markdown(
        f'<div class="dv-medida"><span class="dv-medida-label">Área</span>'
        f'<span class="dv-medida-valor">{medida}</span></div>',
        unsafe_allow_html=True,
    )

    estilo = st.selectbox(
        "Estilo",
        ["Sin definir", "Moderno", "Nórdico", "Industrial", "Rústico", "Minimalista", "Clásico"],
    )
    colores = st.text_input("Colores del ambiente", placeholder="Ej. paredes blancas, piso de roble")

    st.button("Reiniciar conversación", key="reiniciar", on_click=reiniciar_conversacion,
              icon=":material/refresh:", width="stretch")

    st.markdown(
        '<p class="dv-pie">DecoView · Lima, Perú<br>Asesor con IA para que aciertes a la primera.</p>',
        unsafe_allow_html=True,
    )


def contexto_ficha():
    datos = []
    if ambiente != "Sin definir":
        datos.append(f"Ambiente: {ambiente}")
    if ancho and largo:
        datos.append(f"Medidas: {ancho:.1f} m × {largo:.1f} m ({ancho * largo:.1f} m²)")
    if estilo != "Sin definir":
        datos.append(f"Estilo: {estilo}")
    if colores.strip():
        datos.append(f"Colores: {colores.strip()}")
    if not datos:
        return None
    return "Ficha del espacio que llenó el cliente (úsala, no la vuelvas a preguntar):\n- " + "\n- ".join(datos)


# Mostrar los mensajes previos del historial en la interfaz
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar=AVATARES[message["role"]]):
            st.markdown(message["content"])

# Estado vacío: sugerencias para empezar
if len(st.session_state.messages) == 1:
    st.markdown('<p class="dv-label">Puedes empezar con…</p>', unsafe_allow_html=True)
    with st.container(key="sugerencias"):
        cols = st.columns(2)
        for i, texto in enumerate(SUGERENCIAS):
            cols[i % 2].button(texto, key=f"sug_{i}", on_click=usar_sugerencia, args=(texto,),
                               width="stretch")

# Capturar la entrada del usuario (escrita o desde una sugerencia)
escrito = st.chat_input("Cuéntame sobre tu espacio o qué mueble estás buscando…")
prompt = escrito or st.session_state.pop("pendiente", None)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar=AVATARES["user"]):
        st.markdown(prompt)

    # Generar la respuesta del modelo
    with st.chat_message("assistant", avatar=AVATARES["assistant"]):
        message_placeholder = st.empty()
        mensajes = list(st.session_state.messages)
        ficha = contexto_ficha()
        if ficha:
            mensajes.insert(1, {"role": "system", "content": ficha})
        try:
            with st.spinner("Tomando medidas…"):
                response = client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=mensajes,
                    temperature=0.6,
                    max_tokens=1200
                )
            choice = response.choices[0]
            full_response = choice.message.content

            # openai/gpt-oss-120b "piensa" antes de responder (usa tokens de razonamiento
            # ocultos). Si se queda sin presupuesto de tokens mientras piensa, el texto
            # visible (content) puede llegar vacío. Lo detectamos para no mostrar un
            # mensaje en blanco y confundir al usuario.
            if not full_response or not full_response.strip():
                if choice.finish_reason == "length":
                    st.warning(
                        "🤔 **El modelo se quedó pensando y se acabaron los tokens** antes de "
                        "escribir la respuesta visible.\n\n"
                        "Intenta con una pregunta más corta y directa, o reinicia la conversación "
                        "desde la barra lateral."
                    )
                else:
                    st.warning("🤔 El modelo respondió vacío. Intenta reformular tu mensaje.")
            else:
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        except openai.AuthenticationError:
            st.error(
                "🔑 **API Key inválida o revocada.**\n\n"
                "Genera una nueva (gratis) en https://console.groq.com/keys y actualiza "
                "`.streamlit/secrets.toml`."
            )

        except openai.RateLimitError as e:
            st.error(
                "⏳ **Alcanzaste el límite gratuito de Groq** (peticiones o tokens por minuto/día).\n\n"
                "Espera un minuto y vuelve a intentar, o revisa tus límites actuales en "
                "https://console.groq.com/settings/limits\n\n"
                f"Detalle técnico: `{e}`"
            )

        except openai.APITimeoutError:
            st.error("⏱️ **Se agotó el tiempo de espera** al contactar a Groq. Revisa tu conexión e intenta de nuevo.")

        except openai.APIConnectionError:
            st.error(
                "🌐 **No se pudo conectar con los servidores de Groq.**\n\n"
                "Revisa tu conexión a internet, firewall o proxy."
            )

        except openai.NotFoundError:
            st.error(
                f"❓ **El modelo `{GROQ_MODEL}` ya no existe o fue renombrado en Groq.**\n\n"
                "Revisa la lista de modelos vigentes en https://console.groq.com/docs/models "
                "y actualiza la variable `GROQ_MODEL` en `app_openai.py`."
            )

        except openai.PermissionDeniedError:
            st.error("⛔ **Tu cuenta de Groq no tiene permiso** para usar este modelo o región.")

        except openai.BadRequestError as e:
            st.error(f"⚠️ **La petición enviada a Groq fue inválida.**\n\nDetalle técnico: `{e}`")

        except openai.InternalServerError:
            st.error("🛠️ **Error interno de los servidores de Groq** (no es un problema de tu código). Intenta de nuevo en unos minutos.")

        except openai.APIStatusError as e:
            st.error(f"❌ **Groq devolvió un error HTTP {e.status_code}.**\n\nDetalle técnico: `{e}`")

        except openai.OpenAIError as e:
            st.error(f"❌ **Error de la librería de cliente no clasificado.**\n\nDetalle técnico: `{type(e).__name__}: {e}`")

        except Exception as e:
            st.error(f"❌ **Error inesperado (no relacionado a Groq).**\n\nDetalle técnico: `{type(e).__name__}: {e}`")
