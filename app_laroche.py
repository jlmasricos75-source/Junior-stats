import streamlit as st
import pandas as pd
import datetime

# Forzamos que el layout use todo el ancho pero con márgenes controlados
st.set_page_config(page_title="MVP PRO v35", layout="wide", initial_sidebar_state="collapsed")

# --- CSS PARA OPTIMIZAR EL TAMAÑO DE BOTONES Y VÍDEO ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3em; font-weight: bold; font-size: 14px; border-radius: 8px; }
    .stVideo { max-width: 600px; margin: 0 auto; border: 2px solid #ddd; border-radius: 10px; }
    .block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- ROSTER TOTAL 17 ---
ROSTER_TOTAL = [
    "3.NACHO", "8.OSCAR", "15.JOAN", "18.GABI", "21.MARC", "50.ADRIAN", "99.PEPE", 
    "2.LUCAS", "5.ADR.O", "9.ANDREU", "11.PELLICER", "12.NAVÍO", 
    "7.MATEO", "10.IZAN", "14.HUGO", "23.SAMU", "30.DANI"
]

# --- INICIALIZACIÓN ---
if 'fase' not in st.session_state: st.session_state.fase = "CONFIG"
if 'log' not in st.session_state: st.session_state.log = []
if 'pista' not in st.session_state: st.session_state.pista = []
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'periodo' not in st.session_state: st.session_state.periodo = "1Q"
if 'estado_cuarto' not in st.session_state: st.session_state.estado_cuarto = "PAUSA"
if 'rivales' not in st.session_state: st.session_state.rivales = ["GENERICO"]

def registrar(accion, pts, tipo="Local"):
    if st.session_state.estado_cuarto == "PAUSA":
        st.error("⚠️ El cuarto está en PAUSA. Pulsa INICIAR.")
        return
    
    tiempo = datetime.datetime.now().strftime("%M:%S")
    jugador = st.session_state.j_sel if tipo == "Local" else "RIVAL"
    
    st.session_state.log.append({
        "Periodo": st.session_state.periodo, "Jugador": jugador,
        "Accion": accion, "Pts": pts, "Tipo": tipo, "Reloj": tiempo
    })
    st.toast(f"✅ {accion}")

def get_stats(nombre):
    pts = sum(d['Pts'] for d in st.session_state.log if d['Jugador'] == nombre)
    faltas = sum(1 for d in st.session_state.log if d['Jugador'] == nombre and d['Accion'] == "FALTA")
    return pts, faltas

# --- FASE 1: CONFIGURACIÓN ---
if st.session_state.fase == "CONFIG":
    st.title("📋 CONFIGURACIÓN DE PARTIDO")
    c1, c2 = st.columns(2)
    with c1:
        conv = st.multiselect("Convoca 12 de 17:", ROSTER_TOTAL, default=ROSTER_TOTAL[:12])
        st.session_state.pista = st.multiselect("Quinteto Inicial:", conv, max_selections=5)
        st.session_state.rivales_input = st.text_input("Dorsales Rival (comas):", "4, 7, 10, 12")
    with c2:
        vid = st.file_uploader("Vídeo para Scouting (Opcional):", type=["mp4"])
        if vid: st.session_state.video_data = vid

    if len(st.session_state.pista) == 5:
        if st.button("🚀 INICIAR RECOGIDA", type="primary", use_container_width=True):
            st.session_state.rivales = [r.strip() for r in st.session_state.rivales_input.split(",")]
            st.session_state.fase = "PARTIDO"; st.rerun()

# --- FASE 2: PARTIDO (LAYOUT OPTIMIZADO) ---
else:
    # FILA 1: CONTROL DE TIEMPO (Muy accesible)
    c_per, c_play, c_fin = st.columns([1, 2, 1])
    with c_per:
        st.session_state.periodo = st.selectbox("Cuarto", ["1Q", "2Q", "3Q", "4Q", "OT"], label_visibility="collapsed")
    with c_play:
        txt = "▶️ INICIAR CUARTO" if st.session_state.estado_cuarto == "PAUSA" else "⏸️ FINALIZAR CUARTO (PAUSA)"
        if st.button(txt, type="primary" if st.session_state.estado_cuarto == "PAUSA" else "secondary"):
            st.session_state.estado_cuarto = "JUGANDO" if st.session_state.estado_cuarto == "PAUSA" else "PAUSA"; st.rerun()
    with c_fin:
        if st.button("🏁 FIN PARTIDO"): st.session_state.clear(); st.rerun()

    # FILA 2: EL VÍDEO (REDUCIDO)
    if 'video_data' in st.session_state:
        # Usamos columnas para centrar el vídeo y que no ocupe todo el ancho
        _, v_col, _ = st.columns([1, 2, 1])
        with v_col:
            st.video(st.session_state.video_data)
    
    st.divider()

    # FILA 3: PANEL DE CONTROL
    col_izq, col_cen, col_der = st.columns([1, 1.4, 1])

    with col_izq: # NUESTROS JUGADORES
        st.caption("🏃 JUGADORES (Pts | F)")
        for j in st.session_state.pista:
            p, f = get_stats(j)
            is_sel = (st.session_state.j_sel == j)
            if st.button(f"{j}  ({p}p | {f}F)", key=f"pj_{j}", type="primary" if is_sel else "secondary"):
                st.session_state.j_sel = j; st.rerun()
        if st.button("🔄 CAMBIOS/ACTA", type="secondary"): st.session_state.fase = "CONFIG"; st.rerun()

    with col_cen: # ACCIONES LOCALES
        st.caption("🏀 NUESTRAS ACCIONES")
        a1, a2, a3 = st.columns(3)
        if a1.button("2P ✅"): registrar("2P-M", 2)
        if a2.button("3P ✅"): registrar("3P-M", 3)
        if a3.button("TL ✅"): registrar("TL-M", 1)
        
        b1, b2, b3 = st.columns(3)
        if b1.button("2P ❌"): registrar("2P-F", 0)
        if b2.button("3P ❌"): registrar("3P-F", 0)
        if b3.button("TL ❌"): registrar("TL-F", 0)

        st.caption("🧠 FILOSOFÍA Y STATS")
        s1, s2, s3 = st.columns(3)
        if s1.button("🧤 ROBO"): registrar("ROBO", 0)
        if s2.button("🟥 FALTA"): registrar("FALTA", 0)
        if s3.button("🎨 PT"): registrar("PT", 0) # Paint Touch
        
        s4, s5, s6 = st.columns(3)
        if s4.button("AST"): registrar("AST", 0)
        if s5.button("➕ EXTRA"): registrar("ExtraP", 0)
        if s6.button("PER"): registrar("TOV", 0)

        st.caption("🏀 REBOTES")
        r_of, r_def = st.columns(2)
        if r_of.button("REB OF"): registrar("R-OF", 0)
        if r_def.button("REB DEF"): registrar("R-DF", 0)

    with col_der: # RIVAL
        st.caption("🚫 RIVAL")
        riv_sel = st.selectbox("Rival:", st.session_state.rivales, label_visibility="collapsed")
        ra, rb = st.columns(2)
        if ra.button("R2 ✅"): registrar(f"R-2P-#{riv_sel}", 2, "Rival")
        if rb.button("R3 ✅"): registrar(f"R-3P-#{riv_sel}", 3, "Rival")
        
        rc, rd = st.columns(2)
        if rc.button("R-TL ✅"): registrar(f"R-TL-#{riv_sel}", 1, "Rival")
        if rd.button("R-PER"): registrar(f"R-TOV-#{riv_sel}", 0, "Rival")
        
        st.caption("🛡️ REBOTES RIVAL")
        rro, rrd = st.columns(2)
        if rro.button("R. OF"): registrar("R-ROF", 0, "Rival")
        if rrd.button("R. DF"): registrar("R-RDF", 0, "Rival")
        
        st.divider()
        p_l = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
        p_r = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")
        st.metric("SCORE", f"{p_l} - {p_r}")

# --- LOG EN SIDEBAR ---
if st.session_state.log:
    with st.sidebar:
        st.write("### 📥 ÚLTIMAS ACCIONES")
        df = pd.DataFrame(st.session_state.log)
        st.dataframe(df.iloc[::-1], use_container_width=True)
        st.download_button("Descargar CSV", df.to_csv(index=False), "partido.csv")
