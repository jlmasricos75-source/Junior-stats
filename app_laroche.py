import streamlit as st
import pandas as pd
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Junior Stats - Pro Scouting", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS INSPIRADOS EN HOOPSALYTICS ---
st.markdown("""
    <style>
    /* Botones de Jugadores */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3.5em; }
    /* Botones de Acción (Verde para acierto, Rojo para fallo) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { border-left: 10px solid #22c55e; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { border-left: 10px solid #ef4444; }
    /* Contenedores de estadísticas */
    .stat-card { background-color: #1e293b; color: white; padding: 15px; border-radius: 10px; text-align: center; }
    .metric-value { font-size: 24px; font-weight: bold; color: #38bdf8; }
    </style>
    """, unsafe_allow_html=True)

# --- DATOS MAESTROS (Corregidos) ---
JUNIOR_A = ["3.SERRA", "8.MORANA", "15.AMER", "18.GABI", "21.ALÓS", "50.FERRER", "99.PEPE"]
JUNIOR_B = ["2.LUCAS", "5.ADRIÁN", "9.ANDREU", "11.ALEJ.", "12.DAVID", "23.ANT.", "24.CARLOS", "28.DERIN", "32.GONZALO", "82.MIGUEL"]

# --- INICIALIZACIÓN DEL ESTADO (SESSION STATE) ---
if 'log' not in st.session_state: st.session_state.log = []
if 'fase' not in st.session_state: st.session_state.fase = "CONFIG"
if 'pista' not in st.session_state: st.session_state.pista = []
if 'convocados' not in st.session_state: st.session_state.convocados = []
if 'pos_n' not in st.session_state: st.session_state.pos_n = 1
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'periodo' not in st.session_state: st.session_state.periodo = "1Q"
if 'pt_count' not in st.session_state: st.session_state.pt_count = 0
if 'inv_count' not in st.session_state: st.session_state.inv_count = 0
if 'extra_count' not in st.session_state: st.session_state.extra_count = 0

# --- LÓGICA DE REGISTRO ---
def registrar_evento(accion, pts=0, tipo="Local", detalle=""):
    jugador = st.session_state.j_sel if tipo == "Local" else "RIVAL"
    
    # Calcular marcador actual
    l_pts = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
    r_pts = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")
    
    nuevo_evento = {
        "Pos#": st.session_state.pos_n,
        "Q": st.session_state.periodo,
        "Hora": datetime.datetime.now().strftime("%H:%M:%S"),
        "Jugador": jugador,
        "Accion": accion,
        "Pts": pts,
        "Tipo": tipo,
        "PT_Pos": st.session_state.pt_count,
        "Inv_Pos": st.session_state.inv_count,
        "Extra_Pos": st.session_state.extra_count,
        "Marcador": f"{l_pts + (pts if tipo == 'Local' else 0)}-{r_pts + (pts if tipo == 'Rival' else 0)}",
        "Pista": list(st.session_state.pista),
        "Detalle": detalle
    }
    
    st.session_state.log.append(nuevo_evento)
    # Limpiar selección tras acción de finalización
    if pts > 0 or "MISS" in accion or "TOV" in accion or "FALTA" in accion:
        st.session_state.j_sel = None
    st.toast(f"✅ {accion} - {jugador}")

# --- PANTALLA: CONFIGURACIÓN INICIAL ---
if st.session_state.fase == "CONFIG":
    st.title("🏀 Configuración del Partido")
    equipo_cat = st.radio("Selecciona Categoría:", ["JUNIOR A", "JUNIOR B"], horizontal=True)
    lista_base = JUNIOR_A if equipo_cat == "JUNIOR A" else JUNIOR_B
    
    st.session_state.convocados = st.multiselect(
        "Jugadores Convocados (Orden Dorsal):", 
        sorted(lista_base, key=lambda x: int(x.split('.')[0])),
        default=lista_base
    )
    
    st.session_state.pista = st.multiselect(
        "Quinteto Inicial (Elegir 5):",
        st.session_state.convocados,
        max_selections=5
    )
    
    if st.button("🚀 EMPEZAR SCOUTING", type="primary"):
        if len(st.session_state.pista) == 5:
            st.session_state.fase = "PARTIDO"
            st.rerun()
        else:
            st.error("¡Debes seleccionar exactamente 5 jugadores para empezar!")

# --- PANTALLA: PARTIDO (INTERFAZ HOOPSALYTICS) ---
elif st.session_state.fase == "PARTIDO":
    # Cabecera de Marcador y Posición
    l_pts = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
    r_pts = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")
    
    col_score, col_pos = st.columns([2, 1])
    with col_score:
        st.markdown(f"""<div class='stat-card'>
            <span style='font-size: 14px;'>MARCADOR</span><br>
            <span class='metric-value'>{l_pts} - {r_pts}</span>
            <span style='margin-left: 20px; font-size: 18px;'>Q: {st.session_state.periodo}</span>
        </div>""", unsafe_allow_html=True)
    
    with col_pos:
        if st.button(f"🔄 SIGUIENTE POS. (#{st.session_state.pos_n})", type="primary"):
            st.session_state.pos_n += 1
            st.session_state.pt_count = 0
            st.session_state.inv_count = 0
            st.session_state.extra_count = 0
            st.rerun()

    st.write("")
    
    # CUERPO PRINCIPAL
    col_players, col_main_actions, col_meta = st.columns([1, 2.5, 1])
    
    with col_players:
        st.caption("🏃 EN PISTA")
        for j in st.session_state.pista:
            # Resaltar jugador seleccionado
            color = "primary" if st.session_state.j_sel == j else "secondary"
            if st.button(f"#{j.split('.')[0]} {j.split('.')[1]}", key=f"p_{j}", type=color):
                st.session_state.j_sel = j
                st.rerun()
        
        st.divider()
        if st.button("➕ CAMBIOS", use_container_width=True):
            st.session_state.fase = "CAMBIOS"
            st.rerun()

    with col_main_actions:
        # Fila de Tiro
        c1, c2, c3 = st.columns(3)
        with c1: # ACIERTOS
            if st.button("🎯 2PT MADE"): registrar_evento("2PM", 2)
            if st.button("🎯 3PT MADE"): registrar_evento("3PM", 3)
            if st.button("🎯 FT MADE"): registrar_evento("FTM", 1)
        with c2: # FALLOS
            if st.button("❌ 2PT MISS"): registrar_evento("2PX", 0)
            if st.button("❌ 3PT MISS"): registrar_evento("3PX", 0)
            if st.button("❌ FT MISS"): registrar_evento("FTX", 0)
        with c3: # REBOTES
            if st.button("🚀 O-REB"): registrar_evento("OREB", 0)
            if st.button("📥 D-REB"): registrar_evento("DREB", 0)
            if st.button("🧤 STEAL"): registrar_evento("STL", 0)

        # Fila de Detalle Hoopsalytics
        st.caption("🏷️ ETIQUETAS DE ACCIÓN")
        d1, d2, d3 = st.columns(3)
        if d1.button("🎨 PAINT TOUCH"): st.session_state.pt_count += 1; registrar_evento("PT", 0)
        if d2.button("🔄 INVERSIÓN"): st.session_state.inv_count += 1; registrar_evento("INV", 0)
        if d3.button("➕ EXTRA PASS"): st.session_state.extra_count += 1; registrar_evento("EXTRA", 0)
        
        # Fila de Errores y Faltas
        e1, e2, e3 = st.columns(3)
        if e1.button("📉 TURNOVER"): registrar_evento("TOV", 0)
        if e2.button("👤 ASIST"): registrar_evento("AST", 0)
        if e3.button("🖐️ BLOCK"): registrar_evento("BLK", 0)

    with col_meta:
        st.caption("⏱️ CONTROL")
        st.session_state.periodo = st.selectbox("Periodo", ["1Q", "2Q", "3Q", "4Q", "OT"], label_visibility="collapsed")
        
        st.write("---")
        st.caption("🚩 RIVAL")
        if st.button("Rival +2"): registrar_evento("R-2P", 2, "Rival")
        if st.button("Rival +3"): registrar_evento("R-3P", 3, "Rival")
        if st.button("Rival TOV"): registrar_evento("R-TOV", 0, "Rival")
        
        st.write("---")
        if st.button("🗑️ BORRAR ÚLT.", use_container_width=True):
            if st.session_state.log: st.session_state.log.pop(); st.rerun()

# --- PANTALLA: PANEL DE CAMBIOS (SELECCIÓN TOTAL) ---
elif st.session_state.fase == "CAMBIOS":
    st.title("🔄 Sustituciones en Bloque")
    # Ordenar por dorsal para el panel
    jugadores_panel = sorted(st.session_state.convocados, key=lambda x: int(x.split('.')[0]))
    
    st.write("Selecciona los 5 jugadores que estarán en pista:")
    nueva_pista = st.multiselect("Quinteto:", jugadores_panel, default=list(st.session_state.pista), max_selections=5)
    
    if st.button("✅ CONFIRMAR QUINTETO", type="primary", use_container_width=True):
        if len(nueva_pista) == 5:
            st.session_state.pista = nueva_pista
            st.session_state.fase = "PARTIDO"
            st.rerun()
        else:
            st.warning("Debes seleccionar 5 jugadores.")
    
    if st.button("Cancelar"):
        st.session_state.fase = "PARTIDO"
        st.rerun()

# --- TABLA DE DATOS (AL FINAL) ---
if st.session_state.log:
    with st.expander("Ver Log de Eventos"):
        df = pd.DataFrame(st.session_state.log)
        st.dataframe(df.iloc[::-1], use_container_width=True)
