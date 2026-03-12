import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="METRICAS JUNIOR PRO", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS PARA EL CAMPO ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .pintura-btn>button { background-color: #f0f2f6; border: 2px solid #ff4b4b; height: 5em; font-weight: bold; }
    .zona-btn>button { background-color: #f9f9f9; border: 1px solid #ccc; }
    </style>
    """, unsafe_allow_html=True)

# --- DATOS ---
fijos_a = ["3.NACHO SERRA", "8.OSCAR MORANA", "15.JOAN AMER", "18.GABI OFICIAL", "21.MARC ALÓS", "50.ADRIAN FERRER", "99.PEPE MÁS"]
junior_b = ["2.LUCAS MÁS", "5.ADRIAN OJEDA", "9.ANDREU ESTELLÉS", "11.ALEJANDRO PELLICER", "12.DAVID NAVÍO", "23.ANTONIO PERANDRÉS", "24.CARLOS MÁS", "28.DERIN AKYUZ", "32.GONZALO", "82.MIGUEL DOLZ"]
especiales = ["PT < 8''", "Paint Touch", "Corte", "Transición", "ExtraPass+Tiro", "Tiro Reemplazo", "Stampede"]

if 'log' not in st.session_state: st.session_state.log = []
if 'inicio' not in st.session_state: st.session_state.inicio = None
if 'jugador_sel' not in st.session_state: st.session_state.jugador_sel = None
if 'zona_sel' not in st.session_state: st.session_state.zona_sel = None

def obtener_tiempo():
    if not st.session_state.inicio: return "00:00"
    t = int(time.time() - st.session_state.inicio)
    return f"{t//60:02d}:{t%60:02d}"

# --- SIDEBAR RIVAL ---
with st.sidebar:
    rival = st.text_input("Rival:", "RIVAL").upper()
    equipo = st.radio("EQUIPO:", ["JUNIOR A", "JUNIOR B"])
    pool = sorted(fijos_a + junior_b if equipo == "JUNIOR A" else junior_b, key=lambda x: int(x.split('.')[0]))
    quinteto = st.multiselect("EN PISTA:", pool, max_selections=5)
    if st.button("🚀 EMPEZAR PARTIDO"):
        st.session_state.inicio, st.session_state.log = time.time(), []

# --- INTERFAZ ---
p_l = sum(d['Pts'] for d in st.session_state.log if "Rival" not in d['Jugador'])
st.title(f"📊 {p_l} - METRICAS JUNIOR - {obtener_tiempo()}")

if st.session_state.inicio and len(quinteto) == 5:
    # PASO 1: JUGADOR
    st.write("### 1. ¿Quién?")
    cols_j = st.columns(5)
    for i, j in enumerate(quinteto):
        if cols_j[i].button(j, key=f"j_{j}", type="primary" if st.session_state.jugador_sel == j else "secondary"):
            st.session_state.jugador_sel = j
            st.session_state.zona_sel = None # Reset zona al cambiar jugador

    if st.session_state.jugador_sel:
        st.divider()
        col_c, col_a = st.columns([1.2, 1])

        # PASO 2: EL CAMPO (DIBUJO)
        with col_c:
            st.write(f"### 2. ¿Dónde? ({st.session_state.jugador_sel})")
            
            # Representación visual del campo
            # Fila Triples (Arco)
            t1, t2, t3, t4, t5 = st.columns(5)
            if t1.button("Esq IZQ", key="z1"): st.session_state.zona_sel = "T3-Esq-IZQ"
            if t2.button("45° IZQ", key="z2"): st.session_state.zona_sel = "T3-45-IZQ"
            if t3.button("FRONT", key="z3"): st.session_state.zona_sel = "T3-Front"
            if t4.button("45° DER", key="z4"): st.session_state.zona_sel = "T3-45-DER"
            if t5.button("Esq DER", key="z5"): st.session_state.zona_sel = "T3-Esq-DER"

            # Media distancia y Pintura
            st.write("")
            m1, pintura, m2 = st.columns([1, 2, 1])
            if m1.button("Med IZQ", key="z6"): st.session_state.zona_sel = "Med-IZQ"
            with pintura:
                if st.button("🏀 PINTURA 🏀", key="zp", type="primary", use_container_width=True):
                    st.session_state.zona_sel = "Pintura"
            if m2.button("Med DER", key="z7"): st.session_state.zona_sel = "Med-DER"

        # PASO 3: ACCIONES
        with col_a:
            if st.session_state.zona_sel:
                st.write(f"### 3. ¿Qué hizo en {st.session_state.zona_sel}?")
                acc, pts, finalizar = None, 0, False
                
                # Botones de acción grandes para iPad
                c1, c2 = st.columns(2)
                if c1.button("✅ CANASTA", use_container_width=True): 
                    acc = "T3-A" if "T3" in st.session_state.zona_sel else "T2-A"
                    pts = 3 if "T3" in st.session_state.zona_sel else 2
                    finalizar = True
                if c2.button("❌ FALLO", use_container_width=True): acc, pts, finalizar = "Fallo", 0, True
                
                st.write("**Otros / Filosofía**")
                f1, f2 = st.columns(2)
                if f1.button("🤝 ASISTENCIA"): acc, pts, finalizar = "AST", 0, True
                if f2.button("👟 PÉRDIDA"): acc, pts, finalizar = "TOV", 0, True
                
                for m in especiales:
                    if st.button(m, use_container_width=True):
                        acc, pts, finalizar = m, 0, True
                
                if finalizar:
                    st.session_state.log.append({
                        "Min": obtener_tiempo(), "Jugador": st.session_state.jugador_sel,
                        "Zona": st.session_state.zona_sel, "Acción": acc, "Pts": pts
                    })
                    st.session_state.zona_sel = None # Limpiar zona para encadenar otra acción
                    st.rerun()

# --- TABLA Y EFF ---
if st.session_state.log:
    st.divider()
    df = pd.DataFrame(st.session_state.log)
    st.write("### 🏆 Valoración EFF")
    # Lógica de EFF simplificada para el directo
    res = df.groupby('Jugador').agg(PTS=('Pts','sum'), ACC=('Acción','count'))
    st.dataframe(res.T)
    st.download_button("📥 Descargar Datos", df.to_csv(index=False), f"partido_{rival}.csv")
