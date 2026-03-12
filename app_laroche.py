import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="MVP JUNIOR PRO v38", layout="wide", initial_sidebar_state="collapsed")

# --- DISEÑO TÁCTICO ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3.5em; font-weight: bold; border-radius: 10px; border: 1px solid #d1d1d1; }
    .stVideo { max-width: 580px; margin: 0 auto; border: 3px solid #1e3a8a; border-radius: 15px; }
    .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- ROSTERS ACTUALIZADOS ---
ROSTERS = {
    "JUNIOR A": [
        "3.NACHO SERRA", "8.OSCAR MORANA", "15.JOAN AMER", "18.GABI OFICIAL", 
        "21.MARC ALÓS", "50.ADRIAN FERRER", "99.PEPE MÁS"
    ],
    "JUNIOR B": [
        "2.LUCAS MÁS", "5.ADRIÁN OJEDA", "9.ANDREU ESTELLÉS", "11.ALEJANDRO PELLICER", 
        "12.DAVID NAVÍO", "23.ANTONIO PERANDRÉS", "24.CARLOS MÁS", "28.DERIN AKYUZ", 
        "32.GONZALO R.", "82.MIGUEL DOLZ"
    ]
}

# --- INICIALIZACIÓN DE VARIABLES ---
for key in ['fase', 'log', 'pista', 'j_sel', 'z_sel', 'periodo', 'estado_cuarto', 'rivales']:
    if key not in st.session_state:
        if key == 'fase': st.session_state[key] = "CONFIG"
        elif key == 'log': st.session_state[key] = []
        elif key == 'z_sel': st.session_state[key] = "PINTURA"
        elif key == 'periodo': st.session_state[key] = "1Q"
        elif key == 'estado_cuarto': st.session_state[key] = "PAUSA"
        else: st.session_state[key] = None

# --- MOTOR DE REGISTRO ---
def registrar(accion, pts, tipo="Local"):
    if st.session_state.estado_cuarto == "PAUSA":
        st.error("⚠️ Cuarto en PAUSA. Pulsa INICIAR CUARTO."); return
    
    jugador = st.session_state.j_sel if tipo == "Local" else f"RIVAL-#{st.session_state.riv_sel}"
    
    st.session_state.log.append({
        "Periodo": st.session_state.periodo, "Jugador": jugador,
        "Accion": accion, "Zona": st.session_state.z_sel,
        "Pts": pts, "Tipo": tipo, "Reloj": datetime.datetime.now().strftime("%M:%S")
    })
    st.toast(f"✅ REGISTRADO: {accion} ({st.session_state.z_sel})")
    if pts > 0 or "FALTA" in accion: st.session_state.j_sel = None

def get_stats(nombre):
    p = sum(d['Pts'] for d in st.session_state.log if d['Jugador'] == nombre)
    f = sum(1 for d in st.session_state.log if d['Jugador'] == nombre and d['Accion'] == "FALTA")
    return p, f

# --- FASE 1: CONFIGURACIÓN ---
if st.session_state.fase == "CONFIG":
    st.title("📋 CONTROL DE PARTIDO: CARGA")
    c1, c2 = st.columns(2)
    with c1:
        eq = st.selectbox("Selecciona Equipo:", list(ROSTERS.keys()))
        conv = st.multiselect("Acta del día:", ROSTERS[eq], default=ROSTERS[eq])
        st.session_state.pista = st.multiselect("Titulares (5):", conv, max_selections=5)
    with c2:
        st.session_state.rival_raw = st.text_input("Dorsales Rival (ej: 4, 7, 10, 11):", "4, 7, 10")
        vid = st.file_uploader("Vídeo para Scouting (Mac/Casa):", type=["mp4"])
        if vid: st.session_state.video_data = vid

    if len(st.session_state.pista) == 5:
        if st.button("🚀 INICIAR Y PASAR A RECOGIDA", type="primary"):
            st.session_state.rivales = [r.strip() for r in st.session_state.rival_raw.split(",")]
            st.session_state.fase = "PARTIDO"; st.rerun()

# --- FASE 2: PANEL DE JUEGO ---
else:
    # FILA SUPERIOR: TIEMPOS
    t1, t2, t3 = st.columns([1, 2, 1])
    with t1: st.session_state.periodo = st.selectbox("CUARTO", ["1Q","2Q","3Q","4Q","OT"], label_visibility="collapsed")
    with t2:
        btn_label = "▶️ INICIAR CUARTO" if st.session_state.estado_cuarto == "PAUSA" else "⏸️ FINALIZAR CUARTO"
        if st.button(btn_label, type="primary" if st.session_state.estado_cuarto == "PAUSA" else "secondary"):
            st.session_state.estado_cuarto = "JUGANDO" if st.session_state.estado_cuarto == "PAUSA" else "PAUSA"; st.rerun()
    with t3:
        if st.button("🏁 CERRAR"): st.session_state.clear(); st.rerun()

    # VIDEO (Solo si existe)
    if 'video_data' in st.session_state:
        st.video(st.session_state.video_data)

    st.divider()

    # CUERPO DE DATOS (3 Columnas)
    col_j, col_a, col_r = st.columns([1, 1.3, 1])

    with col_j: # NUESTROS JUGADORES
        st.caption("🏃 JUGADORES EN PISTA")
        for j in st.session_state.pista:
            p, f = get_stats(j)
            tipo = "primary" if st.session_state.j_sel == j else "secondary"
            # Visualización rápida de faltas
            label = f"{j} | {p} pts | {f}F"
            if f >= 4: label = f"⚠️ {label}"
            if st.button(label, key=f"j_{j}", type=tipo):
                st.session_state.j_sel = j; st.rerun()
        if st.button("🔄 CAMBIOS"): st.session_state.fase = "CONFIG"; st.rerun()

    with col_a: # NUESTRA ACCIÓN
        st.caption("📍 ZONA DEL CAMPO")
        z1, z2, z3, z4 = st.columns(4)
        if z1.button("PINTURA", type="primary" if st.session_state.z_sel=="PINTURA" else "secondary"): st.session_state.z_sel="PINTURA"; st.rerun()
        if z2.button("T3", type="primary" if st.session_state.z_sel=="TRIPLE" else "secondary"): st.session_state.z_sel="TRIPLE"; st.rerun()
        if z3.button("MEDIA", type="primary" if st.session_state.z_sel=="MEDIA" else "secondary"): st.session_state.z_sel="MEDIA"; st.rerun()
        if z4.button("TL", type="primary" if st.session_state.z_sel=="TL" else "secondary"): st.session_state.z_sel="TL"; st.rerun()

        st.write(f"Jugador: **{st.session_state.j_sel if st.session_state.j_sel else 'SELECCIONA'}**")
        c1, c2 = st.columns(2)
        if c1.button("✅ CANASTA", use_container_width=True):
            val = 3 if st.session_state.z_sel=="TRIPLE" else (1 if st.session_state.z_sel=="TL" else 2)
            registrar(f"ANOTADO-{st.session_state.z_sel}", val)
        if c2.button("❌ TIRO FALLADO", use_container_width=True): registrar(f"FALLO-{st.session_state.z_sel}", 0)

        st.caption("🧠 FILOSOFÍA")
        f1, f2, f3 = st.columns(3)
        if f1.button("🧤 ROBO"): registrar("ROBO", 0)
        if f2.button("🅰️ ASIST"): registrar("ASISTENCIA", 0)
        if f3.button("🎨 PT"): registrar("PAINT_TOUCH", 0)
        
        f4, f5, f6 = st.columns(3)
        if f4.button("🟥 FALTA"): registrar("FALTA", 0)
        if f5.button("➕ EXTRA"): registrar("EXTRA_PASS", 0)
        if f6.button("📉 PERD"): registrar("PERDIDA", 0)

        st.caption("🏀 REBOTES")
        r1, r2 = st.columns(2)
        if r1.button("REB OF"): registrar("REB_OF", 0)
        if r2.button("REB DEF"): registrar("REB_DEF", 0)

    with col_der: # EL RIVAL
        st.caption("🚫 RIVAL")
        st.session_state.riv_sel = st.selectbox("Dorsal:", st.session_state.rivales, label_visibility="collapsed")
        ra, rb = st.columns(2)
        if ra.button("R-2P ✅"): registrar("RIVAL-2", 2, "Rival")
        if rb.button("R-3P ✅"): registrar("RIVAL-3", 3, "Rival")
        
        st.caption("🛡️ REBOTES RIVAL")
        rc, rd = st.columns(2)
        if rc.button("R-REB OF"): registrar("R-REB-OF", 0, "Rival")
        if rd.button("R-REB DF"): registrar("R-REB-DF", 0, "Rival")
        
        st.divider()
        p_l = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
        p_r = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")
        st.metric("MARCADOR", f"{p_l} - {p_r}", delta=p_l-p_r)

# SIDEBAR: LOG Y DESCARGA
if st.session_state.log:
    with st.sidebar:
        st.title("📥 DESCARGA")
        df = pd.DataFrame(st.session_state.log)
        st.download_button("BAJAR CSV", df.to_csv(index=False), "estadisticas_junior.csv")
        st.dataframe(df.iloc[::-1])
