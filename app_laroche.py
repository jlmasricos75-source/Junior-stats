import streamlit as st
import pandas as pd
import datetime

# 1. CONFIGURACIÓN DE PANTALLA PARA BANQUILLO (OPTIMIZADO IPAD/LAPTOP)
st.set_page_config(page_title="ADN SCOUTING v55", layout="wide", initial_sidebar_state="collapsed")

# Estilos CSS Unificados (ADN + Interfaz Hoops-Flow)
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3.8em; font-weight: bold; border-radius: 10px; margin-bottom: 2px; }
    .pos-header { background-color: #1e3a8a; color: white; padding: 10px; border-radius: 12px; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 10px; }
    .stat-box { background-color: #ffffff; padding: 8px; border-radius: 8px; text-align: center; border: 2px solid #1e3a8a; font-weight: bold; font-size: 16px; }
    .bonus-flag { background-color: #ff4b4b; color: white; padding: 5px; border-radius: 5px; text-align: center; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.5; } }
    .court-container { background-color: #e5e7eb; padding: 15px; border-radius: 12px; border: 2px solid #374151; text-align: center; }
    .stVideo { border-radius: 12px; box-shadow: 0px 4px 10px rgba(0,0,0,0.2); }
    </style>
    """, unsafe_allow_html=True)

# 2. ROSTERS OFICIALES (Integrados para evitar re-configuración)
ROSTERS = {
    "JUNIOR A": ["3.SERRA", "8.MORANA", "15.AMER", "18.GABI", "21.ALÓS", "50.FERRER", "99.PEPE"],
    "JUNIOR B": ["2.LUCAS", "5.ADRIÁN", "9.ANDREU", "11.ALEJ.", "12.DAVID", "23.ANT.", "24.CARLOS", "28.DERIN", "32.GONZALO", "82.MIGUEL"]
}

# 3. ESTADO DE LA SESIÓN (Lógica v54+)
if 'log' not in st.session_state: st.session_state.log = []
if 'fase' not in st.session_state: st.session_state.fase = "CONFIG"
if 'pos_n' not in st.session_state: st.session_state.pos_n = 1
if 'inv_en_pos' not in st.session_state: st.session_state.inv_en_pos = 0
if 'pt_en_pos' not in st.session_state: st.session_state.pt_en_pos = 0
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'z_sel' not in st.session_state: st.session_state.z_sel = "PINTURA"
if 'periodo' not in st.session_state: st.session_state.periodo = "1Q"
if 'estado_cuarto' not in st.session_state: st.session_state.estado_cuarto = "PAUSA"
if 'pista' not in st.session_state: st.session_state.pista = []

# 4. FUNCIONES DE REGISTRO
def registrar(accion, pts, tipo="Local", detalle=""):
    if st.session_state.estado_cuarto == "PAUSA" and accion not in ["INICIO_CUARTO", "FIN_CUARTO"]:
        st.warning("⚠️ El reloj está en PAUSA"); return
    
    jugador = st.session_state.j_sel if tipo == "Local" else f"RIVAL-#{st.session_state.riv_sel}"
    
    st.session_state.log.append({
        "Pos#": st.session_state.pos_n,
        "Invs": st.session_state.inv_en_pos,
        "PT": st.session_state.pt_en_pos,
        "Q": st.session_state.periodo,
        "Jugador": jugador,
        "Accion": accion,
        "Zona": st.session_state.z_sel,
        "Pts": pts,
        "Tipo": tipo,
        "Hora": datetime.datetime.now().strftime("%H:%M:%S")
    })
    if pts > 0 or "FALLO" in accion or "FALTA" in accion:
        st.session_state.j_sel = None # Limpiar selección tras acción clave

def get_faltas_equipo(tipo_eq):
    return sum(1 for d in st.session_state.log if d['Tipo'] == tipo_eq and "FALTA" in d['Accion'] and d['Q'] == st.session_state.periodo)

# --- FLUJO DE INTERFAZ ---

if st.session_state.fase == "CONFIG":
    st.title("🏀 PRE-PARTIDO JUNIOR")
    cat = st.radio("Selecciona Equipo:", ["JUNIOR A", "JUNIOR B"], horizontal=True)
    pool = ROSTERS[cat]
    
    convocados = st.multiselect("Jugadores Disponibles:", pool, default=pool)
    st.session_state.pista = st.multiselect("Quinteto Inicial:", convocados, max_selections=5)
    st.session_state.riv_raw = st.text_input("Dorsales Rival (separados por coma):", "4, 5, 10, 12, 15")
    video_file = st.file_uploader("Subir Vídeo de Scouting (Opcional):", type=["mp4", "mov"])
    
    if st.button("🏟️ EMPEZAR SCOUTING", type="primary", use_container_width=True):
        if len(st.session_state.pista) == 5:
            st.session_state.convocados = convocados
            st.session_state.rivales = [r.strip() for r in st.session_state.riv_raw.split(",")]
            if video_file: st.session_state.video_data = video_file
            st.session_state.fase = "PARTIDO"
            st.rerun()
        else:
            st.error("Selecciona 5 jugadores para el quinteto inicial.")

elif st.session_state.fase == "PARTIDO":
    # Header de Marcador y Posesión
    pts_l = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
    pts_r = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")
    f_l = get_faltas_equipo("Local")
    f_r = get_faltas_equipo("Rival")

    st.markdown(f'<div class="pos-header">POS #{st.session_state.pos_n} | LOCAL {pts_l} - {pts_r} RIVAL</div>', unsafe_allow_html=True)

    # Métricas ADN en Tiempo Real
    m1, m2, m3 = st.columns([1,1,2])
    with m1: st.markdown(f'<div class="stat-box">🔄 INVERSIONES: {st.session_state.inv_en_pos}</div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="stat-box">🎨 PINTURA (PT): {st.session_state.pt_en_pos}</div>', unsafe_allow_html=True)
    with m3: 
        if st.button("🆕 NUEVA POSESIÓN (ADN RESET)", type="primary"):
            st.session_state.pos_n += 1; st.session_state.inv_en_pos = 0; st.session_state.pt_en_pos = 0; st.rerun()

    # Controles de Cuarto y Bonus
    c1, c2, c3 = st.columns(3)
    with c1:
        if f_l >= 4: st.markdown('<div class="bonus-flag">🚩 BONUS LOCAL</div>', unsafe_allow_html=True)
        else: st.metric("Faltas L", f_l)
    with c2:
        st.session_state.periodo = st.selectbox("Cuarto", ["1Q","2Q","3Q","4Q","OT"], index=["1Q","2Q","3Q","4Q","OT"].index(st.session_state.periodo))
        label_btn = "▶️ INICIAR RELOJ" if st.session_state.estado_cuarto == "PAUSA" else "⏸️ PAUSA RELOJ"
        if st.button(label_btn, use_container_width=True):
            st.session_state.estado_cuarto = "JUGANDO" if st.session_state.estado_cuarto == "PAUSA" else "PAUSA"
            st.rerun()
    with c3:
        if f_r >= 4: st.markdown('<div class="bonus-flag">🚩 BONUS RIVAL</div>', unsafe_allow_html=True)
        else: st.metric("Faltas R", f_r)

    # Vídeo si existe
    if 'video_data' in st.session_state:
        st.video(st.session_state.video_data)

    st.divider()

    # Cuerpo del Scouting
    col_j, col_c, col_a = st.columns([1, 2, 1])

    with col_j: # JUGADORES
        st.caption("🏃 QUINTETO")
        for j in st.session_state.pista:
            st.button(j, type="primary" if st.session_state.j_sel == j else "secondary", 
                      on_click=lambda player=j: setattr(st.session_state, 'j_sel', player))
        if st.button("🔄 CAMBIOS", use_container_width=True):
            st.session_state.fase = "CAMBIOS"; st.rerun()

    with col_c: # CAMPO Y ACCIÓN
        st.markdown('<div class="court-container">', unsafe_allow_html=True)
        cz1, cz2, cz3 = st.columns(3)
        if cz1.button("ESQ-IZQ"): st.session_state.z_sel = "ESQ_IZQ"
        if cz2.button("FRONTAL"): st.session_state.z_sel = "FRONTAL"
        if cz3.button("ESQ-DER"): st.session_state.z_sel = "ESQ_DER"
        cm1, cm2, cm3 = st.columns([1,2,1])
        if cm1.button("45º-I"): st.session_state.z_sel = "45_IZQ"
        if cm2.button("🟦 PINTURA", type="primary"): st.session_state.z_sel = "PINTURA"
        if cm3.button("45º-D"): st.session_state.z_sel = "45_DER"
        st.markdown('</div>', unsafe_allow_html=True)

        st.caption("🎯 ANOTACIÓN / REBOTES")
        a1, a2, a3 = st.columns(3)
        if a1.button("✅ 1P"): registrar("METIDO", 1)
        if a2.button("✅ 2P"): registrar("METIDO", 2)
        if a3.button("✅ 3P"): registrar("METIDO", 3)
        b1, b2, b3 = st.columns(3)
        if b1.button("⭕ FALLO"): registrar("FALLO", 0)
        if b2.button("📥 R-DEF"): registrar("REB_DEF", 0)
        if b3.button("🚀 R-OFF"): registrar("REB_OFF", 0)

    with col_a: # ADN Y RIVAL
        st.caption("🧠 ADN")
        if st.button("🔄 INVERSIÓN"):
            st.session_state.inv_en_pos += 1; registrar("INVERSION", 0)
        if st.button("🎨 PT (Pintura)"):
            st.session_state.pt_en_pos += 1; registrar("PT", 0)
        
        ca1, ca2 = st.columns(2)
        if ca1.button("🤝 AST"): registrar("ASIST", 0)
        if ca2.button("🧤 ROBO"): registrar("ROBO", 0)
        if ca1.button("🟥 FALTA"): registrar("FALTA", 0)
        if ca2.button("📉 PERD"): registrar("PERDIDA", 0)
        
        st.divider()
        st.caption("🚫 RIVAL")
        st.session_state.riv_sel = st.selectbox("Dorsal Rival:", st.session_state.rivales)
        ra, rb = st.columns(2)
        if ra.button("RIVAL +2"): registrar("RIVAL-2", 2, "Rival")
        if rb.button("RIVAL +3"): registrar("RIVAL-3", 3, "Rival")
        if ra.button("R-FALTA"): registrar("F_RIV", 0, "Rival")
        if rb.button("R-PERD"): registrar("P_RIV", 0, "Rival")

elif st.session_state.fase == "CAMBIOS":
    st.title("🔄 ROTACIÓN")
    pool_c = sorted(st.session_state.convocados, key=lambda x: int(x.split('.')[0]))
    nueva_pista = st.multiselect("Jugadores en Pista:", pool_c, default=list(st.session_state.pista), max_selections=5)
    if st.button("✅ CONFIRMAR QUINTETO", type="primary") and len(nueva_pista) == 5:
        st.session_state.pista = nueva_pista
        st.session_state.fase = "PARTIDO"; st.rerun()
    if st.button("↩️ VOLVER"): st.session_state.fase = "PARTIDO"; st.rerun()

# SIDEBAR: HISTORIAL Y EXPORTACIÓN
if st.session_state.log:
    with st.sidebar:
        st.header("📊 DATA")
        df = pd.DataFrame(st.session_state.log)
        st.download_button("📥 EXPORTAR CSV", df.to_csv(index=False), "scouting_junior.csv")
        st.dataframe(df.iloc[::-1], use_container_width=True)
