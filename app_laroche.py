import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="MVP JUNIOR v42", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS VISUALES (Bandera de Bonus y Campo) ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3.2em; font-weight: bold; border-radius: 10px; }
    .bonus-flag { 
        background-color: #ff4b4b; color: white; padding: 10px; 
        border-radius: 5px; text-align: center; font-weight: bold;
        animation: blinker 1.5s linear infinite;
    }
    @keyframes blinker { 50% { opacity: 0.5; } }
    .basketball-court {
        background-color: #f4d0a0; border: 3px solid #333; border-radius: 15px;
        padding: 20px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ROSTERS ORIGINALES ---
JUNIOR_A = ["3.NACHO SERRA", "8.OSCAR MORANA", "15.JOAN AMER", "18.GABI OFICIAL", "21.MARC ALÓS", "50.ADRIAN FERRER", "99.PEPE MÁS"]
JUNIOR_B = ["2.LUCAS MÁS", "5.ADRIÁN OJEDA", "9.ANDREU ESTELLÉS", "11.ALEJANDRO PELLICER", "12.DAVID NAVÍO", "23.ANTONIO PERANDRÉS", "24.CARLOS MÁS", "28.DERIN AKYUZ", "32.GONZALO R.", "82.MIGUEL DOLZ"]

# --- INICIALIZACIÓN ---
if 'fase' not in st.session_state: st.session_state.fase = "CONFIG"
if 'log' not in st.session_state: st.session_state.log = []
if 'pista' not in st.session_state: st.session_state.pista = []
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'z_sel' not in st.session_state: st.session_state.z_sel = "PINTURA"
if 'periodo' not in st.session_state: st.session_state.periodo = "1Q"
if 'estado_cuarto' not in st.session_state: st.session_state.estado_cuarto = "PAUSA"

# --- LÓGICA DE BONUS ---
def get_faltas_periodo(tipo_equipo):
    # En OT se cuentan las del 4Q + OT
    periodos_contar = [st.session_state.periodo]
    if st.session_state.periodo == "OT":
        periodos_contar = ["4Q", "OT"]
    
    return sum(1 for d in st.session_state.log 
               if d['Tipo'] == tipo_equipo 
               and d['Accion'].startswith("FALTA") 
               and d['Q'] in periodos_contar)

def registrar(accion, pts, tipo="Local", extra=""):
    if st.session_state.estado_cuarto == "PAUSA":
        st.error("⚠️ Cuarto en PAUSA"); return
    
    jugador = st.session_state.j_sel if tipo == "Local" else "RIVAL"
    st.session_state.log.append({
        "Q": st.session_state.periodo, "Jugador": jugador, "Accion": accion,
        "Zona": st.session_state.z_sel, "Pts": pts, "Tipo": tipo,
        "Info": extra, "Hora": datetime.datetime.now().strftime("%M:%S")
    })
    st.toast(f"✅ {accion}")
    if pts > 0 or "FALTA" in accion: st.session_state.j_sel = None

# --- FASE 1: CONFIGURACIÓN (CONVOCATORIA DINÁMICA) ---
if st.session_state.fase == "CONFIG":
    st.title("📋 CONVOCATORIA DE PARTIDO")
    
    categoria = st.radio("¿Qué equipo juega hoy?", ["JUNIOR A", "JUNIOR B"], horizontal=True)
    
    # Lógica de disponibilidad: 
    # El A puede elegir a todos. El B solo a los suyos.
    pool = JUNIOR_A + JUNIOR_B if categoria == "JUNIOR A" else JUNIOR_B
    
    c1, c2 = st.columns(2)
    with c1:
        convocados = st.multiselect(f"Selecciona jugadores para {categoria}:", pool, default=pool[:7])
        st.session_state.pista = st.multiselect("Quinteto Titular (5):", convocados, max_selections=5)
    with c2:
        st.session_state.rival_raw = st.text_input("Dorsales Rival (separados por comas):", "4, 7, 10")
        vid = st.file_uploader("Vídeo (Opcional):", type=["mp4"])
        if vid: st.session_state.video_data = vid

    if len(st.session_state.pista) == 5:
        if st.button("🏟️ EMPEZAR PARTIDO", type="primary", use_container_width=True):
            st.session_state.rivales = [r.strip() for r in st.session_state.rival_raw.split(",")]
            st.session_state.fase = "PARTIDO"; st.rerun()

# --- FASE 2: PANTALLA DE DATOS ---
else:
    # 1. MARCADOR Y BONUS (Banderas Rojas)
    f_loc = get_faltas_periodo("Local")
    f_riv = get_faltas_periodo("Rival")
    
    c_score, c_bonus_l, c_bonus_r = st.columns([2, 1, 1])
    with c_score:
        p_l = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
        p_r = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")
        st.subheader(f"🏀 {p_l} - {p_r} ({st.session_state.periodo})")
    
    with c_bonus_l:
        if f_loc >= 4: st.markdown('<div class="bonus-flag">🚩 BONUS LOCAL</div>', unsafe_allow_html=True)
        else: st.metric("Faltas Local", f_loc)
    with c_bonus_r:
        if f_riv >= 4: st.markdown('<div class="bonus-flag">🚩 BONUS RIVAL</div>', unsafe_allow_html=True)
        else: st.metric("Faltas Rival", f_riv)

    # 2. TIEMPOS
    t1, t2, t3 = st.columns([1, 2, 1])
    with t1: st.session_state.periodo = st.selectbox("Q", ["1Q","2Q","3Q","4Q","OT"], label_visibility="collapsed")
    with t2:
        txt = "▶️ INICIAR" if st.session_state.estado_cuarto == "PAUSA" else "⏸️ PAUSA"
        if st.button(txt, use_container_width=True):
            st.session_state.estado_cuarto = "JUGANDO" if st.session_state.estado_cuarto == "PAUSA" else "PAUSA"; st.rerun()
    with t3:
        if st.button("🏁 FIN"): st.session_state.clear(); st.rerun()

    st.divider()

    # 3. PANEL TÁCTICO
    col_j, col_campo, col_act = st.columns([0.8, 2, 0.8])

    with col_j: # JUGADORES
        st.caption("🏃 LOCAL")
        for j in st.session_state.pista:
            p = sum(d['Pts'] for d in st.session_state.log if d['Jugador'] == j)
            f = sum(1 for d in st.session_state.log if d['Jugador'] == j and d['Accion'] == "FALTA")
            label = f"{j.split('.')[0]} ({p}p|{f}F)"
            if f >= 4: label = f"🛑 {label}"
            if st.button(label, key=f"j_{j}", type="primary" if st.session_state.j_sel == j else "secondary"):
                st.session_state.j_sel = j; st.rerun()
        
        st.write("---")
        if st.button("🟥 NUESTRA FALTA", type="secondary"):
            if st.session_state.j_sel: registrar("FALTA", 0)
            else: st.warning("Elige jugador")

    with col_campo: # CAMPO VISUAL
        st.markdown('<div class="basketball-court">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        if c1.button("ESQ IZQ"): st.session_state.z_sel="ESQ_IZQ"; st.rerun()
        if c2.button("TRIPLE F"): st.session_state.z_sel="TRIPLE_F"; st.rerun()
        if c3.button("ESQ DER"): st.session_state.z_sel="ESQ_DER"; st.rerun()
        st.write("")
        m1, pintura, m2 = st.columns([1, 1.5, 1])
        if m1.button("45º IZQ"): st.session_state.z_sel="45_IZQ"; st.rerun()
        with pintura:
            if st.button("🟦 PINTURA (PT)", type="primary" if st.session_state.z_sel=="PINTURA" else "secondary"): 
                st.session_state.z_sel="PINTURA"; st.rerun()
        if m2.button("45º DER"): st.session_state.z_sel="45_DER"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("")
        ca1, ca2 = st.columns(2)
        if ca1.button("🎯 CANASTA OK", type="primary", use_container_width=True):
            pts = 3 if "ESQ" in st.session_state.z_sel or "TRIPLE" in st.session_state.z_sel else 2
            registrar("CANASTA", pts)
        if ca2.button("⭕ FALLO", use_container_width=True): registrar("FALLO", 0)
        
        if st.button("⚡ ATAQUE < 8s (TRANSICIÓN)", use_container_width=True):
            registrar("ATAQUE_RAPIDO", 0, extra="Transición")

    with col_act: # FILOSOFÍA Y RIVAL
        st.caption("🧠 FILOSOFÍA")
        if st.button("🎨 PAINT TOUCH"): registrar("PAINT_TOUCH", 0)
        if st.button("🅰️ ASISTENCIA"): registrar("ASIST", 0)
        if st.button("➕ EXTRA PASS"): registrar("EXTRA", 0)
        
        st.write("---")
        st.caption("🚫 RIVAL")
        st.session_state.riv_sel = st.selectbox("Dorsal:", st.session_state.rivales, label_visibility="collapsed")
        if st.button("RIVAL 2P ✅"): registrar("RIVAL-2", 2, "Rival")
        if st.button("RIVAL 3P ✅"): registrar("RIVAL-3", 3, "Rival")
        if st.button("🟨 FALTA RIVAL", type="secondary"):
            registrar("FALTA_RIVAL", 0, "Rival")

if st.session_state.log:
    with st.sidebar:
        df = pd.DataFrame(st.session_state.log)
        st.download_button("📥 DESCARGAR CSV", df.to_csv(index=False), "stats.csv")
        st.dataframe(df.iloc[::-1])
