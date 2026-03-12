import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="MVP TACTICAL ARENA", layout="wide", initial_sidebar_state="collapsed")

# --- CSS: EL CORAZÓN DEL CAMPO VISUAL ---
st.markdown("""
    <style>
    /* Contenedor del campo */
    .basketball-court {
        background-color: #f4d0a0; /* Color madera */
        border: 3px solid #333;
        border-radius: 15px;
        padding: 20px;
        position: relative;
        text-align: center;
    }
    /* Línea de Triple (Simulada con bordes curvos) */
    .triple-arc {
        border: 3px solid #fff;
        border-radius: 200px 200px 0 0;
        height: 250px;
        width: 100%;
        margin: 0 auto;
        position: relative;
    }
    /* La Zona (Pintura) */
    .paint-area {
        background-color: #1e3a8a; /* Azul pintura */
        width: 140px;
        height: 180px;
        margin: 0 auto;
        border: 2px solid #fff;
        position: relative;
        bottom: 0;
    }
    /* Ajuste de botones para que parezcan tácticos */
    .stButton>button { border-radius: 5px; font-size: 12px; height: 3em; }
    .zona-btn button { background-color: rgba(255,255,255,0.7) !important; color: #000 !important; }
    .zona-active button { background-color: #ff4b4b !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ROSTERS OFICIALES ---
ROSTERS = {
    "JUNIOR A": ["3.NACHO SERRA", "8.OSCAR MORANA", "15.JOAN AMER", "18.GABI OFICIAL", "21.MARC ALÓS", "50.ADRIAN FERRER", "99.PEPE MÁS"],
    "JUNIOR B": ["2.LUCAS MÁS", "5.ADRIÁN OJEDA", "9.ANDREU ESTELLÉS", "11.ALEJANDRO PELLICER", "12.DAVID NAVÍO", "23.ANTONIO PERANDRÉS", "24.CARLOS MÁS", "28.DERIN AKYUZ", "32.GONZALO R.", "82.MIGUEL DOLZ"]
}

# --- INICIALIZACIÓN ---
if 'fase' not in st.session_state: st.session_state.fase = "CONFIG"
if 'log' not in st.session_state: st.session_state.log = []
if 'z_sel' not in st.session_state: st.session_state.z_sel = "PINTURA"
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'estado_cuarto' not in st.session_state: st.session_state.estado_cuarto = "PAUSA"

def registrar(accion, pts, tipo="Local"):
    if st.session_state.estado_cuarto == "PAUSA":
        st.error("⚠️ Pulsa INICIAR CUARTO"); return
    jugador = st.session_state.j_sel if tipo == "Local" else "RIVAL"
    st.session_state.log.append({
        "Q": st.session_state.periodo, "Jugador": jugador, "Accion": accion,
        "Zona": st.session_state.z_sel, "Pts": pts, "Tipo": tipo,
        "Hora": datetime.datetime.now().strftime("%M:%S")
    })
    st.toast(f"✅ {accion} en {st.session_state.z_sel}")
    if pts > 0 or "FALTA" in accion: st.session_state.j_sel = None

def get_stats(n):
    pts = sum(d['Pts'] for d in st.session_state.log if d['Jugador'] == n)
    faltas = sum(1 for d in st.session_state.log if d['Jugador'] == n and d['Accion'] == "FALTA")
    return pts, faltas

# --- FASE 1: CONFIG ---
if st.session_state.fase == "CONFIG":
    st.title("🏀 ARENA TÁCTICA: CONFIGURACIÓN")
    c1, c2 = st.columns(2)
    with c1:
        eq = st.selectbox("Equipo:", list(ROSTERS.keys()))
        st.session_state.pista = st.multiselect("Quinteto Inicial:", ROSTERS[eq], max_selections=5)
    with c2:
        st.session_state.rival_list = st.text_input("Dorsales Rival:", "4, 5, 6")
        vid = st.file_uploader("Vídeo de Partido:", type=["mp4"])
        if vid: st.session_state.video_data = vid
    if len(st.session_state.pista) == 5:
        if st.button("🏟️ ENTRAR AL CAMPO", type="primary"): 
            st.session_state.fase = "PARTIDO"; st.rerun()

# --- FASE 2: EL CAMPO ---
else:
    # CONTROLES SUPERIORES
    c_per, c_play, c_score = st.columns([1, 2, 1])
    with c_per: st.session_state.periodo = st.selectbox("Q", ["1Q","2Q","3Q","4Q","OT"])
    with c_play:
        label = "▶️ INICIAR" if st.session_state.estado_cuarto == "PAUSA" else "⏸️ PAUSA"
        if st.button(label):
            st.session_state.estado_cuarto = "JUGANDO" if st.session_state.estado_cuarto == "PAUSA" else "PAUSA"; st.rerun()
    with c_score:
        p_l = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
        p_r = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")
        st.metric("SCORE", f"{p_l} - {p_r}")

    st.divider()

    col_j, col_campo, col_actions = st.columns([0.8, 2, 0.8])

    with col_j: # JUGADORES (Vertical)
        st.caption("🏃 LOCAL")
        for j in st.session_state.pista:
            p, f = get_stats(j)
            sel = (st.session_state.j_sel == j)
            if st.button(f"{j.split('.')[0]} ({p}p|{f}F)", key=f"j_{j}", type="primary" if sel else "secondary"):
                st.session_state.j_sel = j; st.rerun()
        if st.button("🔄 CAMBIOS"): st.session_state.fase = "CONFIG"; st.rerun()

    with col_campo: # EL CAMPO DE VERDAD
        st.markdown('<div class="basketball-court">', unsafe_allow_html=True)
        
        # FILA 1: TRIPLES EXTERIORES
        t_l, t_c, t_r = st.columns(3)
        if t_l.button("ESQUINA IZQ (3)", type="primary" if st.session_state.z_sel=="CORNER_L" else "secondary"): st.session_state.z_sel="CORNER_L"; st.rerun()
        if t_c.button("TRIPLE FRONTAL", type="primary" if st.session_state.z_sel=="T3_FRONT" else "secondary"): st.session_state.z_sel="T3_FRONT"; st.rerun()
        if t_r.button("ESQUINA DER (3)", type="primary" if st.session_state.z_sel=="CORNER_R" else "secondary"): st.session_state.z_sel="CORNER_R"; st.rerun()
        
        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
        
        # FILA 2: MEDIA DISTANCIA Y PINTURA
        m_l, pintura, m_r = st.columns([1, 1.5, 1])
        if m_l.button("45º IZQ (2)"): st.session_state.z_sel="MID_L"; st.rerun()
        with pintura:
            if st.button("🟦 PINTURA / ZONA", type="primary" if st.session_state.z_sel=="PINTURA" else "secondary"): 
                st.session_state.z_sel="PINTURA"; st.rerun()
        if m_r.button("45º DER (2)"): st.session_state.z_sel="MID_R"; st.rerun()
        
        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
        
        # FILA 3: TIROS LIBRES
        _, tl_col, _ = st.columns([1, 1, 1])
        if tl_col.button("⚪ TIRO LIBRE"): st.session_state.z_sel="TL"; st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("")
        # BOTONES DE ACCIÓN FINAL (Debajo del campo)
        c_ok, c_fail = st.columns(2)
        if c_ok.button("🎯 CANASTA METIDA", type="primary", use_container_width=True):
            pts = 3 if "CORNER" in st.session_state.z_sel or "T3" in st.session_state.z_sel else (1 if st.session_state.z_sel=="TL" else 2)
            registrar(f"GOL-{st.session_state.z_sel}", pts)
        if c_fail.button("⭕ FALLO", use_container_width=True): registrar(f"MISS-{st.session_state.z_sel}", 0)

    with col_actions: # FILOSOFÍA Y RIVAL
        st.caption("🧠 FILOSOFÍA")
        f1, f2 = st.columns(2)
        if f1.button("🧤 ROBO"): registrar("ROBO", 0)
        if f2.button("🅰️ ASIST"): registrar("ASIST", 0)
        if f1.button("🎨 PT"): registrar("PT", 0)
        if f2.button("➕ EXTRA"): registrar("EXTRA", 0)
        if f1.button("🟥 FALTA"): registrar("FALTA", 0)
        if f2.button("📉 PERD"): registrar("TOV", 0)
        
        st.write("---")
        st.caption("🚫 RIVAL")
        if st.button("RIVAL 2 ✅"): registrar("RIVAL-2", 2, "Rival")
        if st.button("RIVAL 3 ✅"): registrar("RIVAL-3", 3, "Rival")
        if st.button("RIVAL REB"): registrar("R-REB", 0, "Rival")
        if st.button("RIVAL PERD"): registrar("R-TOV", 0, "Rival")

if st.session_state.log:
    with st.sidebar:
        df = pd.DataFrame(st.session_state.log)
        st.download_button("📥 DESCARGAR DATOS", df.to_csv(index=False), "partido.csv")
        st.dataframe(df.iloc[::-1], use_container_width=True)
