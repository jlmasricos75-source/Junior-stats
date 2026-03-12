import streamlit as st
import pandas as pd
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Scouting Pro v59",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stButton > button { width: 100%; height: 3.5em; font-weight: bold; border-radius: 8px; }
    .main-header { background-color: #1E1E1E; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #444; margin-bottom: 10px; }
    .stat-card { background: #262730; padding: 10px; border-radius: 10px; border: 1px solid #444; text-align: center; }
    .active-p { background-color: #ff4b4b !important; color: white !important; border: 2px solid white !important; }
    .court-container { position: relative; display: inline-block; }
    .dot { position: absolute; width: 12px; height: 12px; background-color: yellow; border-radius: 50%; transform: translate(-50%, -50%); border: 2px solid black; }
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
if 'last_coord' not in st.session_state: st.session_state.last_coord = None
if 'equipo_nombre' not in st.session_state: st.session_state.equipo_nombre = "JUNIOR A"

# --- LÓGICA DE REGISTRO ---
def registrar(accion, pts=0, tipo="Local"):
    jugador = st.session_state.j_sel if tipo == "Local" else "RIVAL"
    x, y = st.session_state.last_coord if st.session_state.last_coord else (None, None)
    
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
    
    # Limpiar selección tras anotar tiro o pérdida
    if pts > 0 or "FALLO" in accion or "PERDIDA" in accion:
        st.session_state.j_sel = None
        st.session_state.last_coord = None

# --- PANTALLA 1: CONFIGURACIÓN ---
if st.session_state.fase == "CONFIG":
    st.title("🏀 Configuración de Partido")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.equipo_nombre = st.selectbox("Selecciona tu Equipo:", list(ROSTERS.keys()))
        acta = ROSTERS[st.session_state.equipo_nombre]
        st.session_state.pista = st.multiselect("Quinteto en Pista:", acta, default=acta[:5])
    with c2:
        st.session_state.rival_name = st.text_input("Nombre del Rival:", "Rival")
        st.session_state.periodo = st.selectbox("Periodo Inicial:", ["1Q", "2Q", "3Q", "4Q", "OT"])
    
    if st.button("INICIAR SCOUTING", type="primary"):
        st.session_state.fase = "PARTIDO"
        st.rerun()

# --- PANTALLA 2: PARTIDO ---
else:
    l_pts = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
    r_pts = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")
    
    # Header de Marcador
    st.markdown(f"""
    <div class='main-header'>
        <h1 style='margin:0;'>{st.session_state.equipo_nombre} {l_pts} - {r_pts} {st.session_state.rival_name}</h1>
        <p style='margin:0; color: #888;'>Posesión actual: #{st.session_state.pos_n} | Periodo: {st.session_state.periodo}</p>
    </div>
    """, unsafe_allow_html=True)

    # BARRA ADN (Inversiones y Paint Touches)
    adn1, adn2, adn3, adn4 = st.columns([1.5, 1.5, 2, 1])
    if adn1.button(f"🔄 INVERSIÓN ({st.session_state.inv_en_pos})"):
        st.session_state.inv_en_pos += 1
        st.rerun()
    if adn2.button(f"🎨 PAINT TOUCH ({st.session_state.pt_en_pos})"):
        st.session_state.pt_en_pos += 1
        st.rerun()
    if adn3.button("🆕 SIGUIENTE POSESIÓN", type="primary"):
        st.session_state.pos_n += 1
        st.session_state.inv_en_pos = 0
        st.session_state.pt_en_pos = 0
        st.rerun()
    st.session_state.periodo = adn4.selectbox("Cambiar Q", ["1Q", "2Q", "3Q", "4Q", "OT"], label_visibility="collapsed")

    st.divider()

    # CUERPO PRINCIPAL
    col_jug, col_court, col_actions = st.columns([1, 2.5, 1.5])

    with col_jug:
        st.subheader("Jugadores")
        for p in st.session_state.pista:
            is_active = st.session_state.j_sel == p
            if st.button(p, key=f"btn_{p}", type="primary" if is_active else "secondary"):
                st.session_state.j_sel = p
                st.rerun()
        st.divider()
        if st.button("🔁 Cambios"):
            st.session_state.fase = "CONFIG"
            st.rerun()

    with col_court:
        st.subheader("Ubicación del Tiro")
        # Campo interactivo usando st.image con coordenadas de clic
        # Nota: Streamlit registra el clic si se envuelve en un componente específico o se usa un truco de CSS.
        # Aquí usamos un mapa de calor simplificado:
        court_img = "https://raw.githubusercontent.com/gmfuentes/basketball-assets/main/half_court_dark.png"
        # Si no carga, usamos una alternativa de Wikimedia
        alt_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Basketball_court_half.svg/800px-Basketball_court_half.svg.png"
        
        # Simulamos el clic con dos sliders para máxima compatibilidad móvil/tablet
        cx = st.slider("Eje X (Lateral)", 0, 100, 50)
        cy = st.slider("Eje Y (Distancia)", 0, 100, 20)
        st.session_state.last_coord = (cx, cy)
        
        st.image(alt_img, caption="Haz coincidir los sliders con la zona del campo", use_container_width=True)

    with col_actions:
        st.subheader("Acción")
        
        # Tiros
        t1, t2 = st.columns(2)
        with t1:
            if st.button("✅ +3", key="t3"): registrar("T3", 3)
            if st.button("✅ +2", key="t2"): registrar("T2", 2)
            if st.button("✅ +1", key="t1"): registrar("T1", 1)
        with t2:
            if st.button("❌ Fallo 3", key="f3"): registrar("FALLO T3")
            if st.button("❌ Fallo 2", key="f2"): registrar("FALLO T2")
            if st.button("❌ Fallo 1", key="f1"): registrar("FALLO T1")
        
        st.divider()
        # Stats Normales
        s1, s2 = st.columns(2)
        if s1.button("🏀 Rebote"): registrar("REBOTE")
        if s2.button("🤝 Asist"): registrar("ASISTENCIA")
        if s1.button("🛡️ Robo"): registrar("ROBO")
        if s2.button("🗑️ Pérdida"): registrar("PERDIDA")
        if s1.button("❌ Falta C"): registrar("FALTA COMETIDA")
        if s2.button("🛑 Tapón"): registrar("TAPÓN")

        st.divider()
        st.write("RIVAL")
        if st.button("Rival Anota"): registrar("RIVAL ANOTA", 2, "Rival")

    # TABLA DE DATOS
    with st.expander("📊 Historial de Posesiones"):
        if st.session_state.log:
            df = pd.DataFrame(st.session_state.log)
            st.table(df.tail(10)) # Mostramos las últimas 10
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 DESCARGAR BASE DE DATOS", csv, f"scouting_{st.session_state.rival_name}.csv", "text/csv")
        else:
            st.write("Esperando acciones...")
