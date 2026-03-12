import streamlit as st
import pandas as pd
import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ADN Junior Pro v53", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 3.8em; margin-bottom: 5px; }
    .main-header { background-color: #1e293b; color: white; padding: 15px; border-radius: 12px; text-align: center; }
    .adn-box { background-color: #fff7ed; border: 2px solid #f97316; padding: 10px; border-radius: 10px; text-align: center; }
    .court-bg { background-color: #fde68a; border: 2px solid #92400e; border-radius: 15px; padding: 20px; }
    .player-subtext { font-size: 0.75em; color: #475569; display: block; margin-top: -10px; font-weight: normal; }
    </style>
    """, unsafe_allow_html=True)

# --- BASES DE DATOS ---
PLAYERS_DB = {
    "JUNIOR A": ["3.SERRA", "8.MORANA", "15.AMER", "18.GABI", "21.ALÓS", "50.FERRER", "99.PEPE"],
    "JUNIOR B": ["2.LUCAS", "5.ADRIÁN", "9.ANDREU", "11.ALEJ.", "12.DAVID", "23.ANT.", "24.CARLOS", "28.DERIN", "32.GONZALO", "82.MIGUEL"]
}

# --- INICIALIZACIÓN ---
if 'log' not in st.session_state: st.session_state.log = []
if 'fase' not in st.session_state: st.session_state.fase = "CONFIG"
if 'pista' not in st.session_state: st.session_state.pista = []
if 'convocados' not in st.session_state: st.session_state.convocados = []
if 'pos_n' not in st.session_state: st.session_state.pos_n = 1
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'z_sel' not in st.session_state: st.session_state.z_sel = "PINTURA"
if 'periodo' not in st.session_state: st.session_state.periodo = "1Q"
if 'adn_pos' not in st.session_state: 
    st.session_state.adn_pos = {"PT": 0, "PT8": 0, "INV": 0, "ESC": 0, "EXTRA": 0}

# --- FUNCIONES DE CÁLCULO ---
def get_player_stats(player_name):
    pts = sum(d['Pts'] for d in st.session_state.log if d['Jugador'] == player_name and d['Tipo'] == "Local")
    fouls = sum(1 for d in st.session_state.log if d['Jugador'] == player_name and d['Accion'] == "FALTA")
    return pts, fouls

def registrar(accion, pts=0, tipo="Local", detalle="", calidad="BUENO"):
    jugador = st.session_state.j_sel if tipo == "Local" else "RIVAL"
    l_pts = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
    r_pts = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")
    
    st.session_state.log.append({
        "Pos#": st.session_state.pos_n,
        "Q": st.session_state.periodo,
        "Jugador": jugador,
        "Accion": accion,
        "Zona": st.session_state.z_sel,
        "Pts": pts,
        "Calidad": calidad,
        "PT": st.session_state.adn_pos["PT"],
        "PT8": st.session_state.adn_pos["PT8"],
        "INV": st.session_state.adn_pos["INV"],
        "ESC": st.session_state.adn_pos["ESC"],
        "EXTRA": st.session_state.adn_pos["EXTRA"],
        "Marcador": f"{l_pts + (pts if tipo == 'Local' else 0)}-{r_pts + (pts if tipo == 'Rival' else 0)}",
        "Pista": list(st.session_state.pista),
        "Hora": datetime.datetime.now().strftime("%H:%M:%S")
    })
    
    if pts > 0 or "MISS" in accion or "TOV" in accion or accion == "FALTA":
        st.session_state.j_sel = None
    st.toast(f"✅ {accion} - {jugador}")

# --- PANTALLA 1: CONFIGURACIÓN ---
if st.session_state.fase == "CONFIG":
    st.markdown("<div class='main-header'><h1>🏀 CONFIGURACIÓN PARTIDO</h1></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Junior A")
        for p in PLAYERS_DB["JUNIOR A"]:
            if st.checkbox(p, key=f"c_{p}"):
                if p not in st.session_state.convocados: st.session_state.convocados.append(p)
    with c2:
        st.subheader("Junior B")
        for p in PLAYERS_DB["JUNIOR B"]:
            if st.checkbox(p, key=f"cb_{p}"):
                if p not in st.session_state.convocados: st.session_state.convocados.append(p)
    
    st.divider()
    if st.session_state.convocados:
        st.session_state.convocados = sorted(list(set(st.session_state.convocados)), key=lambda x: int(x.split('.')[0]))
        st.subheader("Quinteto Inicial")
        st.session_state.pista = st.multiselect("Elige 5:", st.session_state.convocados, max_selections=5)
        if st.button("🚀 EMPEZAR", type="primary"):
            if len(st.session_state.pista) == 5:
                st.session_state.fase = "PARTIDO"
                st.rerun()

# --- PANTALLA 2: PARTIDO ---
elif st.session_state.fase == "PARTIDO":
    l_pts = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
    r_pts = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")
    
    m1, m2, m3 = st.columns([1,2,1])
    with m1: st.metric("JUNIOR", l_pts)
    with m2: st.markdown(f"<div class='adn-box'><b>POS #{st.session_state.pos_n} | {st.session_state.periodo}</b><br>PT: {st.session_state.adn_pos['PT']} | INV: {st.session_state.adn_pos['INV']} | ESC: {st.session_state.adn_pos['ESC']}</div>", unsafe_allow_html=True)
    with m3: st.metric("RIVAL", r_pts)

    st.write("")
    a1, a2, a3, a4, a5, a6 = st.columns(6)
    if a1.button("🎨 PT"): st.session_state.adn_pos['PT'] += 1; st.rerun()
    if a2.button("⚡ PT<8"): st.session_state.adn_pos['PT8'] += 1; st.session_state.adn_pos['PT'] += 1; st.rerun()
    if a3.button("🔄 INV"): st.session_state.adn_pos['INV'] += 1; st.rerun()
    if a4.button("🙈 ESC"): st.session_state.adn_pos['ESC'] += 1; st.rerun()
    if a5.button("➕ EXTRA"): st.session_state.adn_pos['EXTRA'] += 1; st.rerun()
    if a6.button("🆕 POS", type="primary"):
        st.session_state.pos_n += 1
        st.session_state.adn_pos = {"PT": 0, "PT8": 0, "INV": 0, "ESC": 0, "EXTRA": 0}
        st.rerun()

    st.divider()
    col_p, col_c, col_r = st.columns([1.2, 2.5, 1])

    with col_p:
        st.caption("🏃 PISTA (Pts | Fal)")
        for j in st.session_state.pista:
            p_pts, p_fls = get_player_stats(j)
            t = "primary" if st.session_state.j_sel == j else "secondary"
            # Botón con info de faltas y puntos
            if st.button(f"{j}\n({p_pts}p | {p_fls}f)", key=f"p_{j}", type=t):
                st.session_state.j_sel = j; st.rerun()
        if st.button("🔄 CAMBIOS", type="primary"): st.session_state.fase = "CAMBIOS"; st.rerun()

    with col_c:
        st.markdown("<div class='court-bg'>", unsafe_allow_html=True)
        z1, z2, z3 = st.columns(3)
        if z1.button("ESQ IZQ"): st.session_state.z_sel = "ESQ_IZQ"
        if z2.button("TRIPLE F"): st.session_state.z_sel = "FRONTAL"
        if z3.button("ESQ DER"): st.session_state.z_sel = "ESQ_DER"
        m1, m2, m3 = st.columns([1, 2, 1])
        if m1.button("45º IZQ"): st.session_state.z_sel = "45_IZQ"
        if m2.button("🏀 PINTURA", type="primary"): st.session_state.z_sel = "PINTURA"
        if m3.button("45º DER"): st.session_state.z_sel = "45_DER"
        st.markdown("</div>", unsafe_allow_html=True)

        st.write("")
        f1, f2, f3 = st.columns(3)
        if f1.button("✅ 1P"): registrar("1PM", 1)
        if f2.button("✅ 2P"): registrar("2PM", 2)
        if f3.button("✅ 3P"): registrar("3PM", 3)
        
        b1, b2, b3 = st.columns(3)
        if b1.button("⭕ MISS (B)"): registrar("MISS", 0, calidad="BUENO")
        if b2.button("❌ MISS (M)"): registrar("MISS", 0, calidad="MALO")
        if b3.button("👤 ASIST"): registrar("AST", 0)

    with col_r:
        st.caption("🧤 ACCIONES / RIVAL")
        if st.button("🟥 FALTA", type="primary"): registrar("FALTA", 0)
        d1, d2 = st.columns(2)
        if d1.button("🚀 OF"): registrar("OREB", 0)
        if d2.button("📥 DEF"): registrar("DREB", 0)
        if d1.button("🧤 STL"): registrar("STL", 0)
        if d2.button("🖐️ BLK"): registrar("BLK", 0)
        st.divider()
        if st.button("📉 TOV"): registrar("TOV", 0)
        if st.button("R+2"): registrar("R2", 2, "Rival")
        if st.button("R+3"): registrar("R3", 3, "Rival")
        st.divider()
        if st.button("🔴 RESET"): 
            st.session_state.log = []
            st.session_state.fase = "CONFIG"
            st.rerun()

# --- PANTALLA 3: CAMBIOS ---
elif st.session_state.fase == "CAMBIOS":
    st.title("🔄 PANEL DE CAMBIOS")
    jug_p = sorted(st.session_state.convocados, key=lambda x: int(x.split('.')[0]))
    nueva_p = st.multiselect("En pista:", jug_p, default=list(st.session_state.pista), max_selections=5)
    if st.button("✅ GUARDAR"):
        if len(nueva_p) == 5:
            st.session_state.pista = nueva_p
            st.session_state.fase = "PARTIDO"
            st.rerun()

# --- SIDEBAR: DATOS ---
if st.session_state.log:
    with st.sidebar:
        st.header("📊 RESUMEN")
        df = pd.DataFrame(st.session_state.log)
        st.download_button("📥 EXPORTAR", df.to_csv(index=False), "junior_stats.csv")
        st.dataframe(df.iloc[::-1])
