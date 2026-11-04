import streamlit as st
import json
import random
import os
import html
import time

# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Circuit Trainer ⚡",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

ARCHIVO_CIRCUITOS = "circuitos.json"
ARCHIVO_PROGRESO = "progreso.json"
CARPETA_IMAGENES = "imagenes"
EJERCICIOS_EXCLUIDOS = {"9", "21", "110", "122"}


# ============================================================
# FORMULARIO DE FÓRMULAS
# ============================================================

FORMULAS = {
    "LEY DE OHM": r"""
### Ley de Ohm

Relaciona la tensión, la corriente y la resistencia de un circuito.

\[
V = R \cdot I
\]

\[
I = \frac{V}{R}
\qquad
R = \frac{V}{I}
\]

**Variables**
- \(V\): tensión o voltaje, en voltios (V).
- \(I\): corriente, en amperios (A).
- \(R\): resistencia, en ohmios (Ω).
""",
    "POTENCIA": r"""
### Potencia eléctrica

Indica la rapidez con la que un elemento consume o entrega energía eléctrica.

\[
P = V \cdot I
\]

\[
P = R \cdot I^2
\qquad
P = \frac{V^2}{R}
\]

**Variables**
- \(P\): potencia, en vatios (W).
- \(V\): tensión, en voltios (V).
- \(I\): corriente, en amperios (A).
- \(R\): resistencia, en ohmios (Ω).
""",
    "R EN SERIE": r"""
### Resistencias en serie

Las resistencias están conectadas una después de otra. La corriente es la misma en todas.

**Resistencia equivalente**

\[
R_{eq} = R_1 + R_2 + \cdots + R_n
\]

**Corriente**

\[
I_T = I_1 = I_2 = \cdots = I_n
\]

**Tensión total**

\[
V_T = V_1 + V_2 + \cdots + V_n
\]

**Divisor de tensión**

\[
V_n = V_T \cdot \frac{R_n}{R_T}
\]
""",
    "R EN PARALELO": r"""
### Resistencias en paralelo

Todas las resistencias comparten los mismos dos nodos. La tensión es igual en cada rama.

**Resistencia equivalente**

\[
\frac{1}{R_{eq}} =
\frac{1}{R_1} + \frac{1}{R_2} + \cdots + \frac{1}{R_n}
\]

**Para dos resistencias**

\[
R_{eq} = \frac{R_1 \cdot R_2}{R_1 + R_2}
\]

**Tensión y corriente**

\[
V_T = V_1 = V_2 = \cdots = V_n
\]

\[
I_T = I_1 + I_2 + \cdots + I_n
\]

**Divisor de corriente (dos ramas)**

\[
I_1 = I_T \cdot \frac{R_2}{R_1 + R_2}
\qquad
I_2 = I_T \cdot \frac{R_1}{R_1 + R_2}
\]
""",
    "LEYES DE KIRCHHOFF": r"""
### Primera ley: ley de nodos (LCK)

La suma de las corrientes que entran a un nodo es igual a la suma de las que salen.

\[
\sum I = 0
\]

Por ejemplo:

\[
I_1 + I_2 = I_3 + I_4
\]

### Segunda ley: ley de mallas (LTK)

La suma algebraica de las tensiones en una trayectoria cerrada es cero.

\[
\sum V = 0
\]

Para una malla con fuentes y resistencias:

\[
\sum E - \sum (R \cdot I) = 0
\]

**Importante:** los signos dependen del sentido de recorrido elegido.
""",
    "MÉTODO DE MALLAS": r"""
### Método de mallas

Se asigna una corriente a cada malla independiente. En una resistencia compartida se utiliza la diferencia entre las corrientes de malla.

**Ejemplo: dos mallas**

\[
R_1 I_A + R_3(I_A-I_B) = V_1
\]

\[
R_2 I_B + R_3(I_B-I_A) = V_2
\]

**Corriente por la resistencia compartida**

\[
I_{R_3} = I_A - I_B
\]

Si las corrientes elegidas tienen sentidos opuestos respecto de la rama, se suman algebraicamente en lugar de restarse.

**Importante:** respetá siempre los sentidos de circulación y las polaridades de las fuentes.
""",
    "MÉTODO DE NODOS": r"""
### Método de nodos

Se elige un nodo de referencia (tierra) y se asigna una tensión a cada uno de los demás nodos.

**Ley de corrientes de Kirchhoff**

\[
\sum I = 0
\]

**Corriente entre dos nodos**

\[
I = \frac{V_A - V_B}{R}
\]

**Ecuación general para un nodo**

\[
\sum_k \frac{V_n - V_k}{R_k} = 0
\]

Si el otro extremo de la resistencia está conectado a tierra:

\[
I = \frac{V_A}{R}
\]

**Importante:** las tensiones nodales se miden respecto del nodo de referencia.
"""
}


@st.dialog("☰  FÓRMULAS // REFERENCIA RÁPIDA", width="large")
def mostrar_formulas():
    st.markdown("""
    <div class="formula-intro">
        BASE DE CONSULTA // CIRCUITOS ELÉCTRICOS
        <br>Seleccioná una categoría para consultar sus fórmulas.
    </div>
    """, unsafe_allow_html=True)

    categoria = st.radio(
        "CATEGORÍAS",
        list(FORMULAS.keys()),
        index=0,
        label_visibility="collapsed",
        key="categoria_formulas"
    )

    st.markdown(
        f'<div class="formula-seccion">{html.escape(categoria)}</div>',
        unsafe_allow_html=True
    )
    st.markdown(FORMULAS[categoria])


# ============================================================
# NORMALIZACIÓN DE IDS
# ============================================================

def normalizar_id(valor):
    if valor is None:
        return None
    return str(valor).strip()


# ============================================================
# CARGA DE CIRCUITOS
# ============================================================

@st.cache_data
def cargar_circuitos():
    with open(ARCHIVO_CIRCUITOS, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


try:
    circuitos_originales = cargar_circuitos()
except FileNotFoundError:
    st.error("No se encontró circuitos.json. Crealo en la misma carpeta que app.py.")
    st.stop()
except json.JSONDecodeError:
    st.error("El archivo circuitos.json tiene un formato incorrecto.")
    st.stop()
except OSError as error:
    st.error(f"No se pudo leer circuitos.json: {error}")
    st.stop()

if not isinstance(circuitos_originales, list) or not circuitos_originales:
    st.error("No hay ejercicios cargados correctamente.")
    st.stop()


# ============================================================
# FILTRAR EJERCICIOS VÁLIDOS
# ============================================================

circuitos = []
for circuito in circuitos_originales:
    if not isinstance(circuito, dict):
        continue
    if "id" not in circuito:
        continue
    if not isinstance(circuito.get("variables", []), list):
        continue

    numero_guia = normalizar_id(
        circuito.get("ejercicio_guia", circuito["id"])
    )
    if numero_guia in EJERCICIOS_EXCLUIDOS:
        continue
    circuitos.append(circuito)

if not circuitos:
    st.error("No hay ejercicios válidos para mostrar.")
    st.stop()

ids_disponibles_set = {normalizar_id(c["id"]) for c in circuitos}


# ============================================================
# PREPARAR TABLERO
# ============================================================

ejercicios_tablero = {}
for circuito in circuitos:
    numero = normalizar_id(
        circuito.get("ejercicio_guia", circuito["id"])
    )
    if numero is not None and numero.isdigit():
        ejercicios_tablero[numero] = circuito


# ============================================================
# SISTEMA DE GUARDADO PERMANENTE
# ============================================================

def cargar_progreso():
    if not os.path.exists(ARCHIVO_PROGRESO):
        return {}

    try:
        with open(ARCHIVO_PROGRESO, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        if not isinstance(datos, dict):
            return {}

        resueltos = datos.get("resueltos", [])
        if not isinstance(resueltos, list):
            resueltos = []

        datos["resueltos"] = [
            normalizar_id(r)
            for r in resueltos
            if normalizar_id(r) in ids_disponibles_set
        ]

        actual = normalizar_id(datos.get("circuito_actual_id"))
        datos["circuito_actual_id"] = (
            actual if actual in ids_disponibles_set else None
        )

        if not isinstance(datos.get("respuestas"), dict):
            datos["respuestas"] = {}
        if not isinstance(datos.get("bloqueados"), dict):
            datos["bloqueados"] = {}

        return datos

    except (json.JSONDecodeError, OSError, TypeError):
        return {}


def guardar_progreso():
    datos = {
        "resueltos": sorted(
            list(st.session_state.resueltos),
            key=lambda x: int(x) if str(x).isdigit() else str(x)
        ),
        "circuito_actual_id": normalizar_id(
            st.session_state.circuito_actual_id
        ),
        "respuestas": {
            clave: valor
            for clave, valor in st.session_state.items()
            if clave.startswith("respuesta_")
        },
        "bloqueados": {
            clave: list(valores)
            for clave, valores in st.session_state.bloqueados.items()
        }
    }

    temporal = ARCHIVO_PROGRESO + ".tmp"
    try:
        with open(temporal, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
        os.replace(temporal, ARCHIVO_PROGRESO)
    except OSError as error:
        st.error(f"No se pudo guardar el progreso: {error}")


# ============================================================
# INICIALIZACIÓN DEL ESTADO
# ============================================================

if "resueltos" not in st.session_state:
    datos = cargar_progreso()

    st.session_state.resueltos = {
        normalizar_id(x)
        for x in datos.get("resueltos", [])
        if normalizar_id(x) in ids_disponibles_set
    }

    actual_guardado = normalizar_id(datos.get("circuito_actual_id"))
    st.session_state.circuito_actual_id = (
        actual_guardado if actual_guardado in ids_disponibles_set else None
    )

    st.session_state.bloqueados = {}
    for ejercicio_id, variables_bloqueadas in datos.get("bloqueados", {}).items():
        ejercicio_id = normalizar_id(ejercicio_id)
        if ejercicio_id not in ids_disponibles_set:
            continue
        if not isinstance(variables_bloqueadas, list):
            continue
        st.session_state.bloqueados[ejercicio_id] = set(
            str(v) for v in variables_bloqueadas
        )

    for clave, valor in datos.get("respuestas", {}).items():
        if clave.startswith("respuesta_"):
            st.session_state[clave] = valor

if "bloqueados" not in st.session_state:
    st.session_state.bloqueados = {}
if "circuito_actual_id" not in st.session_state:
    st.session_state.circuito_actual_id = None
if "resueltos" not in st.session_state:
    st.session_state.resueltos = set()
if "tiempos_ejercicios" not in st.session_state:
    st.session_state.tiempos_ejercicios = {}

st.session_state.resueltos = {
    normalizar_id(x)
    for x in st.session_state.resueltos
    if normalizar_id(x) in ids_disponibles_set
}
st.session_state.circuito_actual_id = normalizar_id(
    st.session_state.circuito_actual_id
)
if st.session_state.circuito_actual_id not in ids_disponibles_set:
    st.session_state.circuito_actual_id = None


# ============================================================
# DETECTAR EJERCICIOS EMPEZADOS
# ============================================================

def ejercicio_esta_empezado(circuito):
    ejercicio_id = normalizar_id(circuito["id"])

    if ejercicio_id in st.session_state.resueltos:
        return False

    variables_bloqueadas = st.session_state.bloqueados.get(
        ejercicio_id, set()
    )
    if variables_bloqueadas:
        return True

    for variable in circuito.get("variables", []):
        nombre = str(variable["nombre"])
        clave = f"respuesta_{ejercicio_id}_{nombre}"
        valor = st.session_state.get(clave, "")
        if valor is not None and str(valor).strip() != "":
            return True

    return False


# ============================================================
# FUNCIONES DEL JUEGO
# ============================================================

def obtener_disponibles():
    return [
        circuito for circuito in circuitos
        if normalizar_id(circuito["id"]) not in st.session_state.resueltos
    ]


def obtener_circuito_actual():
    actual = normalizar_id(st.session_state.circuito_actual_id)
    if actual is None:
        return None

    for circuito in circuitos:
        if normalizar_id(circuito["id"]) == actual:
            return circuito
    return None


def seleccionar_circuito():
    disponibles = obtener_disponibles()

    if not disponibles:
        st.session_state.circuito_actual_id = None
        guardar_progreso()
        return

    circuito_actual = obtener_circuito_actual()
    if circuito_actual is not None:
        numero_actual = int(
            circuito_actual.get("ejercicio_guia", circuito_actual["id"])
        )
    else:
        numero_actual = 0

    disponibles_ordenados = sorted(
        disponibles,
        key=lambda c: int(c.get("ejercicio_guia", c["id"]))
    )

    siguiente = None
    for circuito in disponibles_ordenados:
        numero = int(circuito.get("ejercicio_guia", circuito["id"]))
        if numero > numero_actual:
            siguiente = circuito
            break

    if siguiente is None:
        siguiente = disponibles_ordenados[0]

    st.session_state.circuito_actual_id = normalizar_id(siguiente["id"])
    guardar_progreso()


def comprobar_respuesta(valor, respuesta, tolerancia=0.05):
    if valor is None or str(valor).strip() == "":
        return None

    valor_str = str(valor).strip().replace(",", ".")
    try:
        numero = float(valor_str)
    except ValueError:
        return "invalido"

    try:
        correcto = float(respuesta)
    except (ValueError, TypeError):
        return "invalido"

    es_acierto = (
        abs(numero - correcto)
        <= float(tolerancia) * max(1.0, abs(correcto))
    )
    return True if es_acierto else False


def reiniciar_partida():
    claves = [
        clave for clave in list(st.session_state.keys())
        if clave.startswith("respuesta_")
    ]
    for clave in claves:
        del st.session_state[clave]

    st.session_state.resueltos = set()
    st.session_state.bloqueados = {}
    st.session_state.circuito_actual_id = None
    st.session_state.tiempos_ejercicios = {}
    guardar_progreso()


# ============================================================
# CRONÓMETRO
# ============================================================

@st.fragment(run_every="1s")
def mostrar_cronometro(id_ejercicio):
    if id_ejercicio not in st.session_state.tiempos_ejercicios:
        st.session_state.tiempos_ejercicios[id_ejercicio] = time.time()

    tiempo_inicio = st.session_state.tiempos_ejercicios[id_ejercicio]
    segundos_totales = int(time.time() - tiempo_inicio)

    horas = segundos_totales // 3600
    minutos = (segundos_totales % 3600) // 60
    segundos = segundos_totales % 60
    tiempo_formateado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    st.markdown(f"""
    <div style="
        font-family:'Fira Code',monospace;
        font-size:12px;
        font-weight:700;
        color:#ffffff;
        margin-top:-5px;
        margin-bottom:15px;
        letter-spacing:1px;
    ">
        ⏱ TIEMPO: {tiempo_formateado}
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# TABLERO DE SELECCIÓN
# ============================================================

@st.dialog("TABLERO DE CIRCUITOS", width="large")
def mostrar_tablero():
    st.markdown("""
    <div style="
        color:#ffffff;
        font-family:'Fira Code',monospace;
        font-size:11px;
        margin-bottom:15px;
    ">
        SELECCIONÁ UN CIRCUITO PARA ACCEDER DIRECTAMENTE
    </div>
    """, unsafe_allow_html=True)

    todos_los_numeros = sorted(
        int(k) for k in ejercicios_tablero.keys() if k.isdigit()
    )

    if not todos_los_numeros:
        st.warning("No hay ejercicios disponibles para mostrar en el tablero.")
        return

    estilos_naranja = []
    for numero in todos_los_numeros:
        circuito = ejercicios_tablero[str(numero)]
        if (
            normalizar_id(circuito["id"]) not in st.session_state.resueltos
            and ejercicio_esta_empezado(circuito)
        ):
            estilos_naranja.append(f"""
                .st-key-tablero_ejercicio_{numero} button {{
                    background:#854d0e !important;
                    border:1px solid #d97706 !important;
                    color:#ffffff !important;
                }}
                .st-key-tablero_ejercicio_{numero} button:hover {{
                    background:#a16207 !important;
                    border-color:#ffffff !important;
                    box-shadow:0 0 12px rgba(217,119,6,.45) !important;
                }}
            """)

    if estilos_naranja:
        st.markdown(
            "<style>" + "".join(estilos_naranja) + "</style>",
            unsafe_allow_html=True
        )

    st.markdown("""
    <div style="
        display:flex;
        flex-wrap:wrap;
        gap:18px;
        margin-bottom:18px;
        font-family:'Fira Code',monospace;
        font-size:11px;
    ">
        <span style="color:#0fa968;">🟩 RESUELTO</span>
        <span style="color:#d97706;">🟧 EMPEZADO</span>
        <span style="color:#a3a3a3;">⬜ PENDIENTE</span>
    </div>
    """, unsafe_allow_html=True)

    filas = [
        todos_los_numeros[i:i + 10]
        for i in range(0, len(todos_los_numeros), 10)
    ]

    for fila in filas:
        columnas = st.columns(10)
        for idx, numero in enumerate(fila):
            numero_str = str(numero)
            circuito_seleccionado = ejercicios_tablero.get(numero_str)
            esta_disponible = circuito_seleccionado is not None

            esta_resuelto = (
                esta_disponible
                and normalizar_id(circuito_seleccionado["id"])
                in st.session_state.resueltos
            )

            etiqueta = f"✓ {numero}" if esta_resuelto else str(numero)
            tipo = "primary" if esta_resuelto else "secondary"

            with columnas[idx]:
                if st.button(
                    etiqueta,
                    key=f"tablero_ejercicio_{numero}",
                    use_container_width=True,
                    type=tipo,
                    disabled=not esta_disponible
                ):
                    st.session_state.circuito_actual_id = normalizar_id(
                        circuito_seleccionado["id"]
                    )
                    guardar_progreso()
                    st.rerun()


# ============================================================
# DISEÑO VISUAL // MIEL UNLaM (#128268 + VERDE OSCURO MARCADO PARA ACIERTOS)
# ============================================================

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(ellipse at 15% 0%, rgba(18, 130, 104, 0.12), transparent 45%),
        #141414;
    color: #ffffff;
}

#MainMenu, footer { visibility:hidden; }

.stMainBlockContainer, .block-container {
    max-width:100% !important;
    padding-left:3rem !important;
    padding-right:3rem !important;
    padding-top:2.8rem !important;
}

h1, h2, h3 {
    color: #ffffff !important;
    font-family:'Fira Code','Courier New',monospace;
}

p, label, span { color:#ffffff !important; }

.progreso-contenedor {
    display:flex;
    align-items:center;
    background:#1f1f1f;
    border:2px solid #128268;
    border-radius:12px;
    padding:6px;
    margin:15px 0 10px 0;
    box-shadow:0 0 12px rgba(18,130,104,.25);
}

.progreso-texto-badge {
    background:linear-gradient(135deg,#128268,#0e6652);
    color:#ffffff;
    font-family:'Fira Code',monospace;
    font-weight:700;
    font-size:15px;
    padding:8px 14px;
    border-radius:8px;
    text-align:center;
    min-width:75px;
}

.progreso-barra-externa {
    flex-grow:1;
    background:#141414;
    border-radius:8px;
    height:14px;
    margin:0 15px;
    overflow:hidden;
    border:1px solid rgba(18,130,104,.4);
}

.progreso-barra-interna {
    height:100%;
    background:linear-gradient(90deg,#0fa968,#128268);
    border-radius:6px;
    transition:width .4s ease;
}

.progreso-contador-num {
    font-family:'Fira Code',monospace;
    font-weight:700;
    font-size:16px;
    color:#ffffff;
    padding-right:12px;
    min-width:95px;
    text-align:right;
}

.panel-titulo {
    color:#ffffff !important;
    font-family:'Fira Code',monospace;
    font-size:18px;
    font-weight:800;
    margin:0;
}

.separador-panel {
    height:1px;
    background:linear-gradient(90deg,rgba(18,130,104,.6),rgba(18,130,104,.15),transparent);
    margin:14px 0 18px 0;
}

.variable-label {
    color:#ffffff !important;
    font-family:'Fira Code',monospace;
    font-size:15px;
    font-weight:800;
    padding-top:12px;
}

.variable-unidad {
    color:#a3a3a3 !important;
    font-family:'Fira Code',monospace;
    font-size:14px;
    font-weight:700;
    padding-top:12px;
}

.stTextInput input, div[data-baseweb="input"] {
    font-family:'Fira Code',monospace !important;
    font-size:17px !important;
    font-weight:700 !important;
    color:#ffffff !important;
    text-align:center !important;
    border-radius:8px !important;
    border:1px solid #128268 !important;
    background-color:#1a1a1a !important;
    min-height:45px;
}

.stTextInput input:focus, div[data-baseweb="input"]:focus-within {
    border-color:#0fa968 !important;
    box-shadow:0 0 10px rgba(15,169,104,.35) !important;
}

.stTextInput input:disabled {
    color:#0fa968 !important;
    border-color:#0fa968 !important;
    background-color:#0d211a !important;
}

[data-testid="InputInstructions"] { display:none !important; }

.correcto {
    background:rgba(15,169,104,.18);
    border:2px solid #0fa968;
    color:#0fa968;
    padding:11px 14px;
    border-radius:8px;
    font-family:'Fira Code',monospace;
    font-size:12px;
    font-weight:800;
    margin:5px 0 10px 0;
}

.incorrecto {
    background:rgba(225,29,72,.12);
    border:1px solid rgba(225,29,72,.5);
    color:#ffffff;
    padding:11px 14px;
    border-radius:8px;
    font-family:'Fira Code',monospace;
    font-size:12px;
    font-weight:700;
    margin:5px 0 10px 0;
}

.advertencia {
    background:rgba(217,119,6,.12);
    border:1px solid rgba(217,119,6,.5);
    color:#ffffff;
    padding:11px 14px;
    border-radius:8px;
    font-family:'Fira Code',monospace;
    font-size:12px;
    font-weight:700;
    margin:5px 0 10px 0;
}

.estado-pendiente {
    color:#a3a3a3 !important;
    background:rgba(18,130,104,.10);
    border:1px solid rgba(18,130,104,.3);
    border-radius:6px;
    font-family:'Fira Code',monospace;
    font-size:10px;
    font-weight:700;
    padding:5px 9px;
}

/* BOTÓN PRINCIPAL DE FÓRMULAS */
.st-key-boton_formulas {
    width: 100%;
    margin-bottom: 20px;
}
.st-key-boton_formulas button {
    width: 100% !important;
    min-height: 48px !important;
    border-radius: 9px !important;
    border: 1px solid #128268 !important;
    background: linear-gradient(110deg,#18362f,#1a1a1a) !important;
    color: #ffffff !important;
    font-family: 'Fira Code', monospace !important;
    font-size: 14px !important;
    font-weight: 800 !important;
    letter-spacing: 1.2px !important;
    box-shadow: 0 0 10px rgba(18,130,104,.2) !important;
    transition: all .2s ease !important;
}
.st-key-boton_formulas button:hover {
    border-color: #0fa968 !important;
    color: #ffffff !important;
    box-shadow: 0 0 18px rgba(15,169,104,.4) !important;
    transform: translateY(-1px);
}

/* PANEL DE FÓRMULAS */
.formula-intro {
    color:#a3a3a3;
    font-family:'Fira Code',monospace;
    font-size:11px;
    line-height:1.9;
    letter-spacing:1px;
    padding:10px 13px;
    margin:3px 0 16px 0;
    border-left:2px solid #128268;
    background:rgba(18,130,104,.06);
}
.formula-seccion {
    color:#ffffff;
    font-family:'Fira Code',monospace;
    font-size:14px;
    font-weight:800;
    letter-spacing:1.5px;
    border-bottom:1px solid rgba(18,130,104,.35);
    padding:12px 0 10px 0;
    margin:12px 0 16px 0;
}
div[role="radiogroup"] {
    gap:7px !important;
}
div[role="radiogroup"] label {
    background:#1f1f1f !important;
    border:1px solid #235246 !important;
    border-radius:7px !important;
    padding:9px 12px !important;
    transition:all .2s ease;
}
div[role="radiogroup"] label:hover {
    border-color:#128268 !important;
    background:#172c26 !important;
}
div[data-testid="stDialog"] {
    border:1px solid rgba(18,130,104,.45) !important;
    box-shadow:0 0 25px rgba(18,130,104,.15) !important;
}

/* EJERCICIOS COMPLETADOS EN VERDE OSCURO */
div[data-testid="stDialog"] button[kind="primary"] {
    background:#0b533f !important;
    border:1px solid #0fa968 !important;
    color:#ffffff !important;
}
div[data-testid="stDialog"] button[kind="primary"]:hover {
    background:#0fa968 !important;
    border-color:#ffffff !important;
    box-shadow:0 0 12px rgba(15,169,104,.4) !important;
}

/* BOTONES DE NAVEGACIÓN */
.st-key-boton_siguiente {
    width:100%;
    margin-top:22px;
}
.st-key-boton_siguiente button {
    width:100% !important;
    height:58px !important;
    min-height:58px !important;
    border-radius:10px !important;
    border:1px solid #128268 !important;
    background:linear-gradient(100deg,#128268 0%,#0e6652 55%,#153830 100%) !important;
    color:#ffffff !important;
    font-family:'Fira Code',monospace !important;
    font-size:15px !important;
    font-weight:800 !important;
    letter-spacing:1px !important;
    box-shadow:0 0 15px rgba(18,130,104,.25);
    transition:all .25s ease !important;
}
.st-key-boton_siguiente button:hover {
    transform:translateY(-2px);
    box-shadow:0 0 22px rgba(15,169,104,.45) !important;
    border-color:#ffffff !important;
    color:#ffffff !important;
}

.st-key-boton_tablero {
    width:100%;
    margin-top:22px;
}
.st-key-boton_tablero button {
    width:100% !important;
    height:58px !important;
    min-height:58px !important;
    border-radius:10px !important;
    border:1px solid #128268 !important;
    background:linear-gradient(100deg,#1c453d 0%,#152d27 100%) !important;
    color:#ffffff !important;
    font-family:'Fira Code',monospace !important;
    font-size:14px !important;
    font-weight:800 !important;
    letter-spacing:.5px !important;
    transition:all .25s ease !important;
}
.st-key-boton_tablero button:hover {
    transform:translateY(-2px);
    box-shadow:0 0 20px rgba(18,130,104,.4) !important;
    border-color:#ffffff !important;
}

.portada {
    background:linear-gradient(135deg,#1f1f1f,#141414);
    border:1px solid rgba(18,130,104,.5);
    border-radius:16px;
    padding:45px 25px;
    text-align:center;
    box-shadow:0 0 30px rgba(18,130,104,.2);
    max-width:700px;
    margin:45px auto;
}

.pie-pagina {
    text-align:center;
    color:#a3a3a3 !important;
    font-family:'Fira Code',monospace;
    font-size:11px;
    letter-spacing:1px;
    margin-top:35px;
    padding:15px;
    border-top:1px solid rgba(18,130,104,.2);
}
</style>

<link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)


# ============================================================
# BARRA DE PROGRESO GENERAL
# ============================================================

total_circuitos = len(circuitos)
cantidad_resueltos = len(
    st.session_state.resueltos.intersection(ids_disponibles_set)
)
porcentaje = (
    cantidad_resueltos / total_circuitos
    if total_circuitos > 0 else 0
)
porcentaje_str = f"{porcentaje * 100:.0f}%"

st.markdown(f"""
<div class="progreso-contenedor">
    <div class="progreso-texto-badge">{porcentaje_str}</div>
    <div class="progreso-barra-externa">
        <div class="progreso-barra-interna" style="width:{porcentaje * 100}%;"></div>
    </div>
    <div class="progreso-contador-num">{cantidad_resueltos}/{total_circuitos}</div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# BOTÓN DE FÓRMULAS // UBICADO DEBAJO DE LA BARRA DE PROGRESO
# ============================================================

with st.container(key="boton_formulas"):
    if st.button("☰  FÓRMULAS // REFERENCIA RÁPIDA", key="abrir_formulas", use_container_width=True):
        mostrar_formulas()

st.divider()


# ============================================================
# FINALIZACIÓN
# ============================================================

if cantidad_resueltos >= total_circuitos and total_circuitos > 0:
    st.markdown("""
    <div class="portada">
        <div style="font-size:65px;">🏆</div>
        <h1>¡SISTEMA COMPLETADO!</h1>
        <p>Dominaste todos los circuitos de la guía con éxito.</p>
        <h2 style="color:#ffffff !important;">
            ¡Estás lista para romper el examen! ❤️
        </h2>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 Reiniciar entrenamiento", use_container_width=True):
        reiniciar_partida()
        st.rerun()

else:
    # ========================================================
    # RECUPERAR CIRCUITO ACTUAL
    # ========================================================

    if st.session_state.circuito_actual_id is None:
        seleccionar_circuito()

    circuito = obtener_circuito_actual()

    if circuito is None:
        seleccionar_circuito()
        circuito = obtener_circuito_actual()

    if circuito is None:
        st.warning(
            "No se pudo encontrar un ejercicio pendiente. "
            "Revisá el archivo de progreso o reiniciá el entrenamiento."
        )
        if st.button("🔄 Reiniciar entrenamiento"):
            reiniciar_partida()
            st.rerun()
        st.stop()

    circuito_id_str = normalizar_id(circuito["id"])
    if circuito_id_str not in st.session_state.bloqueados:
        st.session_state.bloqueados[circuito_id_str] = set()

    # ========================================================
    # DISTRIBUCIÓN PRINCIPAL
    # ========================================================

    col_img, col_inputs = st.columns([1.2, 1], gap="large")

    # ========================================================
    # COLUMNA IZQUIERDA // CIRCUITO Y DATOS DE ENTRADA DEL JSON
    # ========================================================

    with col_img:
        with st.container(border=True):
            numero_ejercicio = html.escape(
                str(circuito.get("ejercicio_guia", circuito["id"]))
            )

            st.markdown(f"""
            <div style="
                font-family:'Fira Code',monospace;
                font-size:15px;
                font-weight:800;
                letter-spacing:1px;
                color:#ffffff;
                padding-bottom:14px;
                margin-bottom:12px;
                border-bottom:1px solid rgba(18,130,104,.25);
            ">
                EJERCICIO N° {numero_ejercicio}
            </div>
            """, unsafe_allow_html=True)

            mostrar_cronometro(circuito_id_str)

            nombre_archivo_base = f"ej_{circuito['id']}"
            ruta_imagen = None

            for ext in [".png", ".PNG", ".jpg", ".JPG", ".jpeg", ".JPEG"]:
                posible_ruta = os.path.join(
                    CARPETA_IMAGENES,
                    nombre_archivo_base + ext
                )
                if os.path.exists(posible_ruta):
                    ruta_imagen = posible_ruta
                    break

            if ruta_imagen:
                st.image(ruta_imagen, use_container_width=True)
            else:
                st.warning(
                    f"No se encontró la imagen del ejercicio {circuito['id']} "
                    f"en la carpeta '{CARPETA_IMAGENES}'."
                )

            # --- LECTURA DEL CAMPO "datos_entrada" DEL JSON ---
            # Busca prioritariamente "datos_entrada", y de respaldo usa "datos" por si quedó alguno viejo.
            texto_datos = circuito.get("datos_entrada", "")
            if not texto_datos:
                texto_datos = circuito.get("datos", "")

            if texto_datos:
                st.markdown("""
                <div style="
                    font-family:'Fira Code',monospace;
                    font-size:14px;
                    font-weight:800;
                    color:#ffffff;
                    margin-top:20px;
                    margin-bottom:8px;
                ">
                    📋 DATOS DEL ENUNCIADO
                </div>
                """, unsafe_allow_html=True)
                st.info(texto_datos)

    # ========================================================
    # COLUMNA DERECHA // RESULTADOS
    # ========================================================

    with col_inputs:
        with st.container(border=True):
            variables = circuito.get("variables", [])
            cantidad_variables = len(variables)

            st.markdown("""
            <div class="panel-titulo">PANEL DE RESULTADOS</div>
            <div class="separador-panel"></div>
            """, unsafe_allow_html=True)

            if not variables:
                st.info("Este ejercicio no requiere ingreso numérico en grilla.")
            else:
                todas_correctas = True
                cantidad_correctas = 0
                hubo_cambios = False

                for variable in variables:
                    nombre = str(variable["nombre"])
                    respuesta_correcta = variable["respuesta"]
                    unidad = variable.get("unidad", "")
                    clave = f"respuesta_{circuito_id_str}_{nombre}"

                    esta_bloqueada = (
                        nombre in st.session_state.bloqueados[circuito_id_str]
                    )

                    if esta_bloqueada:
                        st.session_state[clave] = str(respuesta_correcta)

                    c_label, c_input, c_unidad = st.columns(
                        [1, 2.5, 0.8],
                        vertical_alignment="center"
                    )

                    with c_label:
                        st.markdown(
                            f'<div class="variable-label">{html.escape(nombre)}</div>',
                            unsafe_allow_html=True
                        )

                    with c_input:
                        valor = st.text_input(
                            f"Valor de {nombre}",
                            key=clave,
                            placeholder="Ingresar valor...",
                            max_chars=12,
                            label_visibility="collapsed",
                            disabled=esta_bloqueada
                        )

                    with c_unidad:
                        st.markdown(
                            f'<div class="variable-unidad">{html.escape(str(unidad))}</div>',
                            unsafe_allow_html=True
                        )

                    resultado = comprobar_respuesta(valor, respuesta_correcta)

                    if esta_bloqueada:
                        cantidad_correctas += 1
                        st.markdown(
                            f"""
                            <div class="correcto">
                                ✓ {html.escape(nombre)} — RESPUESTA CORRECTA
                                ({html.escape(str(respuesta_correcta))} {html.escape(str(unidad))})
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    elif resultado is True:
                        st.session_state.bloqueados[circuito_id_str].add(nombre)
                        hubo_cambios = True
                        cantidad_correctas += 1
                        st.markdown(
                            f"""
                            <div class="correcto">
                                ✓ {html.escape(nombre)} — RESPUESTA CORRECTA
                                ({html.escape(str(respuesta_correcta))} {html.escape(str(unidad))})
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    elif resultado == "invalido":
                        todas_correctas = False
                        st.markdown("""
                        <div class="advertencia">
                            ⚠ FORMATO INVÁLIDO — INGRESÁ SOLAMENTE NÚMEROS
                        </div>
                        """, unsafe_allow_html=True)

                    elif resultado is False:
                        todas_correctas = False
                        st.markdown("""
                        <div class="incorrecto">
                            ✕ VALOR INCORRECTO — VOLVÉ A INTENTARLO
                        </div>
                        """, unsafe_allow_html=True)

                    else:
                        todas_correctas = False
                        st.markdown("""
                        <div class="estado-pendiente">
                            ◷ PENDIENTE DE RESOLUCIÓN
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

                # =================================================
                # ESTADO GENERAL DEL EJERCICIO
                # =================================================

                st.markdown(
                    '<div class="separador-panel"></div>',
                    unsafe_allow_html=True
                )
                st.caption(
                    f"VARIABLES CORRECTAS: {cantidad_correctas}/{cantidad_variables}"
                )

                if todas_correctas and variables:
                    if circuito_id_str not in st.session_state.resueltos:
                        st.session_state.resueltos.add(circuito_id_str)
                        hubo_cambios = True

                if hubo_cambios:
                    guardar_progreso()
                    st.rerun()

                if (
                    todas_correctas
                    and variables
                    and circuito_id_str in st.session_state.resueltos
                ):
                    st.markdown("""
                    <div class="correcto" style="
                        text-align:center;
                        padding:16px;
                        font-size:13px;
                        margin-top:12px;
                    ">
                        ⚡ ¡CIRCUITO RESUELTO CON ÉXITO! ⚡
                    </div>
                    """, unsafe_allow_html=True)

    # ========================================================
    # BOTONES DE NAVEGACIÓN
    # ========================================================

    col_siguiente, col_tablero = st.columns([1, 1], gap="medium")

    with col_siguiente:
        with st.container(key="boton_siguiente"):
            if st.button("SIGUIENTE EJERCICIO  →", use_container_width=True):
                seleccionar_circuito()
                st.rerun()

    with col_tablero:
        with st.container(key="boton_tablero"):
            if st.button("▦  TABLERO DE CIRCUITOS", use_container_width=True):
                mostrar_tablero()

    # ========================================================
    # GUARDADO FINAL
    # ========================================================

    guardar_progreso()


# ============================================================
# PIE DE PÁGINA
# ============================================================

st.markdown("""
<div class="pie-pagina">
    CIRCUIT TRAINER // DISEÑADO PARA LARAJAZZ 💜
</div>
""", unsafe_allow_html=True)