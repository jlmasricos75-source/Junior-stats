import streamlit as st
import pandas as pd
import datetime
from streamlit_extras.grid import grid

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Scouting Pro v58",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stButton > button { width: 100%; height: 3em; font-weight: bold; border-radius: 6px; }
    .shot-btn { height: 4em !important; }
    .main-header { background-color: #0e1117; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid #333; margin-bottom: 10px; }
    .court-container { position: relative; border: 2px solid #555; border-radius: 10px; cursor: crosshair; }
    .player-box { padding: 5px; border: 1px solid #444; border-radius: 5px; text-align: center; background: #1a1c24; }
    .active-p { background: #2e7d32 !important; border: 1px solid #fff; }
    </style>
    """, unsafe_allow_html=True)

# --- ROSTERS ---
ROSTERS = {
    "JUNIOR A": ["3.SERRA", "8.MORANA", "15.AMER", "18.GABI", "21.ALÓS", "50.FERRER", "99.PEPE"],
    "JUNIOR B": ["2.LUCAS", "5.ADR.", "9.AND.", "11.ALEJ.", "12.DAV.", "23.ANT.", "24.CARL.", "28.DER.", "32.GONZ.", "82.MIG."]
}

# --- ESTADO DE SESIÓN ---
if 'log' not in st.session_state: st.session_state.log = []
if 'fase' not in st.session_state: st.session_state.fase = "CONFIG"
if 'pos_n' not in st.session_state: st.session_state.pos_n = 1
if 'inv_en_pos' not in st.session_state: st.session_state.inv_en_pos = 0
if 'pt_en_pos' not in st.session_state: st.session_state.pt_en_pos = 0
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'periodo' not in st.session_state: st.session_state.periodo = "1Q"
if 'pista' not in st.session_state: st.session_state.pista = []
if 'last_coord' not in st.session_state: st.session_state.last_coord = (0, 0)
if 'equipo_nombre' not in st.session_state: st.session_state.equipo_nombre = "JUNIOR A"

# --- LÓGICA DE REGISTRO ---
def registrar(accion, pts=0, tipo="Local", detalle=""):
    jugador = st.session_state.j_sel if tipo == "Local" else "RIVAL"
    x, y = st.session_state.last_coord if "T" in accion or "F" in accion else (None, None)
    
    evento = {
        "Pos#": st.session_state.pos_n,
        "Q": st.session_state.periodo,
        "Jugador": jugador,
        "Accion": accion,
        "Pts": pts,
        "X": x, "Y": y,
        "Inv": st.session_state.inv_en_pos,
        "PT": st.session_state.pt_en_pos,
        "Tipo": tipo,
        "Timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.log.append(evento)
    if pts > 0 or "FALLO" in accion or "PERDIDA" in accion:
        st.session_state.j_sel = None
        st.session_state.last_coord = (0, 0)

# --- PANTALLA 1: CONFIGURACIÓN ---
if st.session_state.fase == "CONFIG":
    st.title("🏀 Configuración")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.equipo_nombre = st.selectbox("Equipo:", list(ROSTERS.keys()))
        acta = ROSTERS[st.session_state.equipo_nombre]
        st.session_state.pista = st.multiselect("Quinteto Inicial:", acta, max_selections=5)
    with c2:
        st.session_state.rival_name = st.text_input("Rival:", "Rival")
    if st.button("EMPEZAR", type="primary"):
        if len(st.session_state.pista) == 5:
            st.session_state.fase = "PARTIDO"
            st.rerun()

# --- PANTALLA 2: PARTIDO ---
else:
    l_pts = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
    r_pts = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")
    
    st.markdown(f"<div class='main-header'><h2>{st.session_state.equipo_nombre} {l_pts} - {r_pts} {st.session_state.rival_name} | POS #{st.session_state.pos_n}</h2></div>", unsafe_allow_html=True)

    # ADN BAR (Métricas Propias)
    adn_col = grid([2, 2, 2, 1], vertical_align="center")
    if adn_col.button(f"🔄 INVERSIÓN ({st.session_state.inv_en_pos})"): st.session_state.inv_en_pos += 1; st.rerun()
    if adn_col.button(f"🎨 PAINT TOUCH ({st.session_state.pt_en_pos})"): st.session_state.pt_en_pos += 1; st.rerun()
    if adn_col.button("🆕 SIGUIENTE POSESIÓN", type="primary"):
        st.session_state.pos_n += 1
        st.session_state.inv_en_pos = 0
        st.session_state.pt_en_pos = 0
        st.rerun()
    st.session_state.periodo = adn_col.selectbox("Q", ["1Q", "2Q", "3Q", "4Q", "OT"], label_visibility="collapsed")

    st.divider()

    # LAYOUT: JUGADORES | CAMPO | ACCIONES
    col_p, col_c, col_a = st.columns([0.8, 2, 1.2])

    with col_p:
        st.write("**PISTA**")
        for p in st.session_state.pista:
            style = "active-p" if st.session_state.j_sel == p else ""
            if st.button(p, key=f"p_{p}", help="Seleccionar jugador"):
                st.session_state.j_sel = p
                st.rerun()
        st.divider()
        if st.button("🔄 CAMBIOS"): st.session_state.fase = "CONFIG"; st.rerun()

    with col_c:
        st.write("**MAPA DE TIRO (Haz clic en la zona)**")
        # Simulación de clic en campo usando un slider o input para prototipo Streamlit 
        # En una app real usaríamos un componente canvas, aquí usamos inputs numéricos 
        # para representar las coordenadas X/Y del clic sobre una imagen
        img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Basketball_court_half.svg/1024px-Basketball_court_half.svg.png"
        st.image(img_url, use_container_width=True)
        
        c_coord1, c_coord2 = st.columns(2)
        x_c = c_coord1.slider("Coord X (Arrastra)", 0, 100, st.session_state.last_coord[0])
        y_c = c_coord2.slider("Coord Y (Arrastra)", 0, 100, st.session_state.last_coord[1])
        st.session_state.last_coord = (x_c, y_c)
        st.caption(f"Coordenada actual: {x_c}, {y_c}")

    with col_a:
        st.write("**ACCIONES**")
        # Tiros
        t_can, t_fall = st.columns(2)
        with t_can:
            if st.button("+3 PTOS", key="c3"): registrar("T3", 3)
            if st.button("+2 PTOS", key="c2"): registrar("T2", 2)
            if st.button("+1 PTO", key="c1"): registrar("T1", 1)
        with t_fall:
            if st.button("Falla T3", key="f3"): registrar("FALLO T3")
            if st.button("Falla T2", key="f2"): registrar("FALLO T2")
            if st.button("Falla T1", key="f1"): registrar("FALLO T1")
        
        st.divider()
        # Estadísticas Normales
        g_acc = grid(2, 2, vertical_align="center")
        if g_acc.button("🏀 REBOTE"): registrar("REBOTE")
        if g_acc.button("🤝 ASIST."): registrar("ASISTENCIA")
        if g_acc.button("🛡️ ROBO"): registrar("ROBO")
        if g_acc.button("🗑️ PÉRDIDA"): registrar("PERDIDA")
        if g_acc.button("❌ FALTA CM"): registrar("FALTA COMETIDA")
        if g_acc.button("🛑 TAPÓN"): registrar("TAPÓN")

        st.divider()
        st.write("**RIVAL**")
        cr1, cr2 = st.columns(2)
        if cr1.button("Rival +2"): registrar("Rival Anota", 2, "Rival")
        if cr2.button("Rival Falla"): registrar("Rival Falla", 0, "Rival")

    # LOG Y EXPORTACIÓN
    with st.expander("📄 Ver Datos Detallados"):
        if st.session_state.log:
            df = pd.DataFrame(st.session_state.log)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar Excel/CSV", csv, f"scouting_{datetime.date.today()}.csv", "text/csv")
        else:
            st.info("No hay acciones registradas.")
