import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="MVP JUNIOR v43", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS AVANZADOS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3.5em; font-weight: bold; border-radius: 10px; }
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
    .score-box {
        font-size: 32px; font-weight: bold; color: #1e3a8a;
        background: #f0f2f6; padding: 10px; border-radius: 10px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ROSTERS ---
JUNIOR_A = ["3.NACHO SERRA", "8.OSCAR MORANA", "15.JOAN AMER", "18.GABI OFICIAL", "21.MARC ALÓS", "50.ADRIAN FERRER", "99.PEPE MÁS"]
JUNIOR_B = ["2.LUCAS MÁS", "5.ADRIÁN OJEDA", "9.ANDREU ESTELLÉS", "11.ALEJANDRO PELLICER", "12.DAVID NAVÍO", "23.ANTONIO PERANDRÉS", "24.CARLOS MÁS", "28.DERIN AKYUZ", "32.GONZALO R.", "82.MIGUEL DOLZ"]

# --- INICIALIZACIÓN ---
if 'fase' not in st.session_state: st.session_state.fase = "CONFIG"
if 'log' not in st.session_state: st.session_state.log = []
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'z_sel' not in st.session_state: st.session_state.z_sel = "PINTURA"
if 'periodo' not in st.session_state: st.session_state.periodo = "1Q"
if 'estado_cuarto' not in st.session_state: st.session_state.estado_cuarto = "PAUSA"

# --- FUNCIONES DE CÁLCULO ---
def get_marcador():
    loc = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
    riv = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")
    return loc, riv

def get_faltas_periodo(tipo_eq):
    per = [st.session_state.periodo]
    if st.session_state.periodo == "OT": per = ["4Q", "OT"]
    return sum(1 for d in st.session_state.log if d['Tipo'] == tipo_eq and "FALTA" in d['Accion'] and d['Q'] in per)

def registrar(accion, pts, tipo="Local", extra=""):
    if st.session_state.estado_cuarto == "PAUSA":
        st.error("⚠️ Pulsa INICIAR CUARTO"); return
    
    jugador = st.session_state.j_sel if tipo == "Local" else "RIVAL"
    st.session_state.log.append({
        "Q": st.session_state.periodo, "Jugador": jugador, "Accion": accion,
        "Zona": st.session_state.z_sel, "Pts": pts, "Tipo": tipo,
        "Info": extra, "Hora": datetime.datetime.now().strftime("%M:%S")
    })
    st.toast(f"✅ {accion}")
    # Solo reseteamos jugador si es una acción final (puntos o falta)
    if pts > 0 or "FALTA" in accion: st.session_state.j_sel = None

# --- FASE 1: CONFIG ---
if st.session_state.fase == "CONFIG":
    st.title("📋 CONVOCATORIA JUNIOR")
    cat = st.radio("Equipo en juego:", ["JUNIOR A", "JUNIOR B"], horizontal=True)
    pool = JUNIOR_A + JUNIOR_B if cat == "JUNIOR A" else JUNIOR_B
    
    c1, c2 = st.columns(2)
    with c1:
        conv = st.multiselect("Seleccionar Convocados:", pool, default=pool[:7])
        st.session_state.pista = st.multiselect("Quinteto Inicial:", conv, max_selections=5)
    with c2:
        st.session_state.riv_raw = st.text_input("Dorsales Rival:", "4, 7, 10")
        if st.button("🏟️ ENTRAR A PISTA", type="primary", use_container_width=True):
            if len(st.session_state.pista) == 5:
                st.session_state.rivales = [r.strip() for r in st.session_state.riv_raw.split(",")]
                st.session_state.fase = "PARTIDO"; st.rerun()

# --- FASE 2: PARTIDO ---
else:
    # CABECERA: MARCADOR Y BONUS
    loc_score, riv_score = get_marcador()
    f_loc = get_faltas_periodo("Local")
    f_riv = get_faltas_periodo("Rival")
    
    st.markdown(f'<div class="score-box"> {loc_score} - {riv_score} </div>', unsafe_allow_html=True)
    
    c_b1, c_b2, c_b3 = st.columns([1,1,1])
    with c_b1:
        if f_loc >= 4: st.markdown('<div class="bonus-flag">🚩 BONUS LOCAL</div>', unsafe_allow_html=True)
        else: st.metric("Faltas Local", f_loc)
    with c_b2:
        st.session_state.periodo = st.selectbox("Q", ["1Q","2Q","3Q","4Q","OT"], label_visibility="collapsed")
        lab = "▶️ INICIAR" if st.session_state.estado_cuarto == "PAUSA" else "⏸️ PAUSA"
        if st.button(lab): st.session_state.estado_cuarto = "JUGANDO" if st.session_state.estado_cuarto == "PAUSA" else "PAUSA"; st.rerun()
    with c_b3:
        if f_riv >= 4: st.markdown('<div class="bonus-flag">🚩 BONUS RIVAL</div>', unsafe_allow_html=True)
        else: st.metric("Faltas Rival", f_riv)

    st.divider()

    col_j, col_campo, col_act = st.columns([0.8, 2, 1])

    with col_j: # NUESTROS JUGADORES
        st.caption("🏃 PISTA")
        for j in st.session_state.pista:
            pts_j = sum(d['Pts'] for d in st.session_state.log if d['Jugador'] == j)
            fal_j = sum(1 for d in st.session_state.log if d['Jugador'] == j and "FALTA" in d['Accion'])
            label = f"{j.split('.')[0]} ({pts_j}p|{fal_j}F)"
            if fal_j >= 4: label = f"🛑 {label}"
            if st.button(label, key=f"j_{j}", type="primary" if st.session_state.j_sel == j else "secondary"):
                st.session_state.j_sel = j; st.rerun()
        
        st.write("---")
        if st.button("🟥 NUESTRA FALTA"):
            if st.session_state.j_sel: registrar("FALTA", 0)

    with col_campo: # CAMPO VISUAL
        st.markdown('<div class="basketball-court">', unsafe_allow_html=True)
        z1, z2, z3 = st.columns(3)
        if z1.button("ESQ IZQ"): st.session_state.z_sel="ESQ_IZQ"; st.rerun()
        if z2.button("TRIPLE F"): st.session_state.z_sel="TRIPLE_F"; st.rerun()
        if z3.button("ESQ DER"): st.session_state.z_sel="ESQ_DER"; st.rerun()
        st.write("")
        m1, pintura, m2 = st.columns([1, 1.5, 1])
        if m1.button("45º IZQ"): st.session_state.z_sel="45_IZQ"; st.rerun()
        with pintura:
            if st.button("🟦 PINTURA", type="primary" if st.session_state.z_sel=="PINTURA" else "secondary"): 
                st.session_state.z_sel="PINTURA"; st.rerun()
        if m2.button("45º DER"): st.session_state.z_sel="45_DER"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.write(f"📍 **{st.session_state.z_sel}** | Jugador: **{st.session_state.j_sel if st.session_state.j_sel else '---'}**")
        
        # TIPOS DE CANASTA (Finalizadores de acción)
        st.caption("🎯 REGISTRAR FINALIZACIÓN")
        c_p, c_t, c_r = st.columns(3)
        if c_p.button("🔥 PENETRACIÓN"):
            pts = 3 if "ESQ" in st.session_state.z_sel or "TRIPLE" in st.session_state.z_sel else 2
            registrar("CANASTA_METIDA", pts, extra="Penetración")
        if c_t.button("🏹 C&S (TIRO)"):
            pts = 3 if "ESQ" in st.session_state.z_sel or "TRIPLE" in st.session_state.z_sel else 2
            registrar("CANASTA_METIDA", pts, extra="Catch & Shoot")
        if c_r.button("💪 TRAS REBOTE"):
            registrar("CANASTA_METIDA", 2, extra="Rebote Of.")
        
        if st.button("⭕ FALLO (Tiro errado)", use_container_width=True):
            registrar("FALLO", 0)

    with col_act: # FILOSOFÍA (INVERSIÓN CLAVE)
        st.caption("🧠 MÉTRICAS DE FILOSOFÍA")
        # LA INVERSIÓN: No resetea jugador para poder seguir la jugada
        if st.button("🔄 INVERSIÓN (Cambio Lado)", type="primary"):
            registrar("INVERSION", 0)
            
        f1, f2 = st.columns(2)
        if f1.button("🎨 PAINT TOUCH"): registrar("PAINT_TOUCH", 0)
        if f2.button("🅰️ ASIST"): registrar("ASISTENCIA", 0)
        if f1.button("➕ EXTRA PASS"): registrar("EXTRA_PASS", 0)
        if f2.button("⚡ < 8s"): registrar("ATAQUE_RAPIDO", 0)
        
        st.write("---")
        st.caption("🚫 RIVAL")
        st.session_state.riv_sel = st.selectbox("Rival:", st.session_state.rivales, label_visibility="collapsed")
        r1, r2 = st.columns(2)
        if r1.button("R-2P ✅"): registrar("RIVAL-2", 2, "Rival")
        if r2.button("R-3P ✅"): registrar("RIVAL-3", 3, "Rival")
        if st.button("🟨 FALTA RIVAL"): registrar("FALTA_RIVAL", 0, "Rival")

if st.session_state.log:
    with st.sidebar:
        st.title("📥 HISTORIAL")
        df = pd.DataFrame(st.session_state.log)
        st.download_button("DESCARGAR CSV", df.to_csv(index=False), "stats_v43.csv")
        st.dataframe(df.iloc[::-1])
