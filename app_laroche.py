import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="MVP PRO v34", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS ---
st.markdown("""<style> .stButton>button { width: 100%; height: 3.5em; font-weight: bold; } </style>""", unsafe_allow_html=True)

# --- ROSTER TOTAL 17 ---
ROSTER_TOTAL = [
    "3.NACHO", "8.OSCAR", "15.JOAN", "18.GABI", "21.MARC", "50.ADRIAN", "99.PEPE", 
    "2.LUCAS", "5.ADR.O", "9.ANDREU", "11.PELLICER", "12.NAVÍO", 
    "7.MATEO", "10.IZAN", "14.HUGO", "23.SAMU", "30.DANI"
]

# --- INICIALIZACIÓN CRÍTICA (Evita el AttributeError) ---
# Creamos todas las variables si no existen antes de ejecutar nada más
if 'fase' not in st.session_state: st.session_state.fase = "CONFIG"
if 'log' not in st.session_state: st.session_state.log = []
if 'pista' not in st.session_state: st.session_state.pista = []
if 'j_sel' not in st.session_state: st.session_state.j_sel = None # Aquí estaba el fallo
if 'periodo' not in st.session_state: st.session_state.periodo = "1Q"
if 'estado_cuarto' not in st.session_state: st.session_state.estado_cuarto = "PAUSA"
if 'rivales' not in st.session_state: st.session_state.rivales = ["GENERICO"]

# --- FUNCIONES ---
def registrar(accion, pts, tipo="Local"):
    if st.session_state.estado_cuarto == "PAUSA":
        st.error("⚠️ Cuarto en pausa. Dale a INICIAR.")
        return
    
    tiempo = datetime.datetime.now().strftime("%M:%S")
    jugador_actual = st.session_state.j_sel if tipo == "Local" else "RIVAL"
    
    st.session_state.log.append({
        "Periodo": st.session_state.periodo,
        "Jugador": jugador_actual,
        "Accion": accion, "Pts": pts, "Tipo": tipo,
        "Reloj": tiempo
    })
    st.toast(f"✅ {accion}")

def get_stats(nombre):
    pts = sum(d['Pts'] for d in st.session_state.log if d['Jugador'] == nombre)
    faltas = sum(1 for d in st.session_state.log if d['Jugador'] == nombre and d['Accion'] == "FALTA")
    return pts, faltas

# --- FASE 1: CONFIGURACIÓN ---
if st.session_state.fase == "CONFIG":
    st.title("🏀 CONFIGURACIÓN")
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("👥 Equipo")
        conv = st.multiselect("Convoca 12 de 17:", ROSTER_TOTAL, default=ROSTER_TOTAL[:12])
        st.session_state.pista = st.multiselect("Quinteto Inicial (5):", conv, max_selections=5)
        st.session_state.rivales_input = st.text_area("Dorsales Rivales (separados por comas):", "4, 7, 10, 12, 15")

    with c2:
        st.subheader("📹 Modo Scouting (Opcional)")
        vid = st.file_uploader("Sube el vídeo para análisis posterior:", type=["mp4", "mov"])
        if vid:
            st.session_state.video_data = vid
            st.success("Vídeo cargado")

    if len(st.session_state.pista) == 5:
        if st.button("🚀 INICIAR Y PASAR A PISTA", type="primary"):
            st.session_state.rivales = [r.strip() for r in st.session_state.rivales_input.split(",")]
            st.session_state.fase = "PARTIDO"
            st.rerun()

# --- FASE 2: PARTIDO (MODO DUAL) ---
else:
    # FILA SUPERIOR: CUARTOS
    c_p1, c_p2, c_p3 = st.columns([1, 2, 1])
    with c_p1:
        st.session_state.periodo = st.selectbox("Cuarto:", ["1Q", "2Q", "3Q", "4Q", "OT"])
    with c_p2:
        txt = "▶️ INICIAR CUARTO" if st.session_state.estado_cuarto == "PAUSA" else "🔔 FINALIZAR CUARTO"
        if st.button(txt, use_container_width=True):
            st.session_state.estado_cuarto = "JUGANDO" if st.session_state.estado_cuarto == "PAUSA" else "PAUSA"
            st.rerun()
    with c_p3:
        if st.button("🏁 FIN PARTIDO"):
            st.session_state.clear() # Limpia todo para evitar errores en el siguiente
            st.rerun()

    # VÍDEO (Solo si existe)
    if 'video_data' in st.session_state:
        st.video(st.session_state.video_data)
        st.divider()

    # BOTONERA 3 COLUMNAS
    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col1: # NUESTROS
        st.write("🏃 **PISTA**")
        for j in st.session_state.pista:
            p, f = get_stats(j)
            # SEGURO CONTRA ATTRIBUTE ERROR:
            is_selected = (st.session_state.j_sel == j)
            if st.button(f"{j} ({p}p | {f}F)", key=f"pj_{j}", type="primary" if is_selected else "secondary"):
                st.session_state.j_sel = j; st.rerun()
        
        if st.button("🔄 CAMBIOS/ACTA"): 
            st.session_state.fase = "CONFIG"; st.rerun()

    with col2: # NUESTRO ATAQUE Y FILOSOFÍA
        st.write("📝 **ACCIONES**")
        t1, t2, t3 = st.columns(3)
        if t1.button("2P ✅"): registrar("2P-M", 2)
        if t2.button("3P ✅"): registrar("3P-M", 3)
        if t3.button("TL ✅"): registrar("TL-M", 1)
        
        f1, f2, f3 = st.columns(3)
        if f1.button("2P ❌"): registrar("2P-F", 0)
        if f2.button("3P ❌"): registrar("3P-F", 0)
        if f3.button("TL ❌"): registrar("TL-F", 0)

        st.write("**🧠 FILOSOFÍA / DEF**")
        s1, s2, s3 = st.columns(3)
        if s1.button("🧤 ROBO"): registrar("ROBO", 0)
        if s2.button("🟥 FALTA"): registrar("FALTA", 0)
        if s3.button("🎨 PT"): registrar("PT", 0)
        
        s4, s5, s6 = st.columns(3)
        if s4.button("AST"): registrar("AST", 0)
        if s5.button("➕ EXTRA"): registrar("ExtraP", 0)
        if s6.button("PER"): registrar("TOV", 0)

        st.write("**🏀 REBOTES**")
        r_of, r_def = st.columns(2)
        if r_of.button("REB OF"): registrar("R-OF", 0)
        if r_def.button("REB DEF"): registrar("R-DF", 0)

    with col3: # RIVAL
        st.write("🚫 **RIVAL**")
        riv_sel = st.selectbox("Dorsal Rival:", st.session_state.rivales)
        ra, rb = st.columns(2)
        if ra.button("R-2P ✅"): registrar(f"R-2P-#{riv_sel}", 2, "Rival")
        if rb.button("R-3P ✅"): registrar(f"R-3P-#{riv_sel}", 3, "Rival")
        
        rc, rd = st.columns(2)
        if rc.button("R-TL ✅"): registrar(f"R-TL-#{riv_sel}", 1, "Rival")
        if rd.button("R-PER"): registrar(f"R-TOV-#{riv_sel}", 0, "Rival")
        
        st.write("**REBOTES RIVAL**")
        if st.button("RIVAL R.OF"): registrar("R-ROF", 0, "Rival")
        if st.button("RIVAL R.DF"): registrar("R-RDF", 0, "Rival")
        
        st.divider()
        p_l = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
        p_r = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")
        st.metric("MARCADOR", f"{p_l} - {p_r}")

# --- SIDEBAR LOG ---
if st.session_state.log:
    with st.sidebar:
        st.write("### 📥 LOG")
        df = pd.DataFrame(st.session_state.log)
        st.dataframe(df.iloc[::-1], use_container_width=True)
        st.download_button("BAJAR CSV", df.to_csv(index=False), "stats_junior.csv")
