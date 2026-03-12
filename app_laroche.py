import streamlit as st
import pandas as pd
import datetime

# Optimización para iPad (Layout Wide)
st.set_page_config(page_title="MVP JUNIOR iPAD", layout="wide", initial_sidebar_state="collapsed")

# --- CSS TÁCTICO PARA iPAD ---
st.markdown("""
    <style>
    /* Botones más grandes para dedos */
    .stButton>button { 
        width: 100%; 
        height: 4.5em; 
        font-weight: bold; 
        border-radius: 12px; 
        font-size: 16px !important;
        margin-bottom: 5px;
        touch-action: manipulation;
    }
    /* Cabecera de Posesión */
    .pos-header { 
        background-color: #1e3a8a; color: white; padding: 20px; 
        border-radius: 15px; text-align: center; font-size: 28px; font-weight: bold;
    }
    /* Indicadores de éxito */
    .stat-box { 
        background-color: #f8f9fa; padding: 15px; border-radius: 12px; 
        text-align: center; border: 3px solid #1e3a8a; font-size: 20px;
    }
    /* Campo Visual */
    .court-container { 
        background-color: #f4d0a0; padding: 25px; border-radius: 20px; 
        border: 4px solid #333; text-align: center;
    }
    /* Desactivar selección de texto para evitar lags al tocar */
    * { -webkit-user-select: none; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'log' not in st.session_state: st.session_state.log = []
if 'fase' not in st.session_state: st.session_state.fase = "CONFIG"
if 'pos_n' not in st.session_state: st.session_state.pos_n = 1
if 'inv_en_pos' not in st.session_state: st.session_state.inv_en_pos = 0
if 'pt_en_pos' not in st.session_state: st.session_state.pt_en_pos = 0
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'z_sel' not in st.session_state: st.session_state.z_sel = "PINTURA"
if 'periodo' not in st.session_state: st.session_state.periodo = "1Q"
if 'estado_cuarto' not in st.session_state: st.session_state.estado_cuarto = "PAUSA"

# Rosters
JUNIOR_A = ["3.SERRA", "8.MORANA", "15.AMER", "18.GABI", "21.ALÓS", "50.FERRER", "99.PEPE"]
JUNIOR_B = ["2.LUCAS", "5.ADRIÁN", "9.ANDREU", "11.ALEJ.", "12.DAVID", "23.ANT.", "24.CARLOS", "28.DERIN", "32.GONZALO", "82.MIGUEL"]

def registrar(accion, pts, tipo="Local", detalle=""):
    if st.session_state.estado_cuarto == "PAUSA":
        st.error("⚠️ RELOJ PARADO"); return
    
    jugador = st.session_state.j_sel if tipo == "Local" else "RIVAL"
    st.session_state.log.append({
        "Pos#": st.session_state.pos_n, "Invs": st.session_state.inv_en_pos, "PT": st.session_state.pt_en_pos,
        "Q": st.session_state.periodo, "Jugador": jugador, "Accion": accion, "Pts": pts, "Tipo": tipo, "Detalle": detalle
    })
    st.toast(f"✅ {accion} +{pts}")
    if pts > 0 or "FALTA" in accion or "FALLO" in accion: st.session_state.j_sel = None

# --- PANTALLA 1: CONFIG ---
if st.session_state.fase == "CONFIG":
    st.title("🏀 CONVOCATORIA iPAD")
    cat = st.radio("Equipo:", ["JUNIOR A", "JUNIOR B"], horizontal=True)
    pool = JUNIOR_A + JUNIOR_B if cat == "JUNIOR A" else JUNIOR_B
    conv = st.multiselect("Acta:", pool, default=pool[:7])
    st.session_state.pista = st.multiselect("Quinteto Inicial:", conv, max_selections=5)
    st.session_state.riv_raw = st.text_input("Dorsales Rival:", "4, 5, 6")
    if st.button("🏟️ ENTRAR A PISTA", type="primary") and len(st.session_state.pista) == 5:
        st.session_state.rivales = [r.strip() for r in st.session_state.riv_raw.split(",")]
        st.session_state.fase = "PARTIDO"; st.rerun()

# --- PANTALLA 2: PARTIDO ---
else:
    # Marcador y Posesión (Grande para iPad)
    pts_l = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
    pts_r = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")
    st.markdown(f'<div class="pos-header">POS #{st.session_state.pos_n} | {pts_l} - {pts_r}</div>', unsafe_allow_html=True)
    
    st.write("")
    c_m1, c_m2, c_m3 = st.columns([1, 1, 2])
    with c_m1: st.markdown(f'<div class="stat-box">🔄 INVS: {st.session_state.inv_en_pos}</div>', unsafe_allow_html=True)
    with c_m2: st.markdown(f'<div class="stat-box">🎨 PT: {st.session_state.pt_en_pos}</div>', unsafe_allow_html=True)
    with c_m3:
        if st.button("🆕 NUEVA POSESIÓN / CAMBIO", type="primary"):
            st.session_state.pos_n += 1; st.session_state.inv_en_pos = 0; st.session_state.pt_en_pos = 0; st.rerun()

    st.write("")
    t1, t2, t3 = st.columns(3)
    with t1:
        f_l = sum(1 for d in st.session_state.log if d['Tipo'] == "Local" and "FALTA" in d['Accion'] and d['Q'] == st.session_state.periodo)
        st.metric("FALTAS L", f_l, delta="BONUS" if f_l >= 4 else None, delta_color="inverse")
    with t2:
        st.session_state.periodo = st.selectbox("Q", ["1Q","2Q","3Q","4Q","OT"], label_visibility="collapsed")
        lab = "▶️ START" if st.session_state.estado_cuarto == "PAUSA" else "⏸️ PAUSE"
        if st.button(lab): st.session_state.estado_cuarto = "JUGANDO" if st.session_state.estado_cuarto == "PAUSA" else "PAUSA"; st.rerun()
    with t3:
        f_r = sum(1 for d in st.session_state.log if d['Tipo'] == "Rival" and "FALTA" in d['Accion'] and d['Q'] == st.session_state.periodo)
        st.metric("FALTAS R", f_r, delta="BONUS" if f_r >= 4 else None, delta_color="inverse")

    st.divider()

    # Layout iPad (3 columnas)
    col_j, col_c, col_a = st.columns([1, 2, 1])

    with col_j: # JUGADORES (Botones XL)
        st.caption("🏃 NUESTRA PISTA")
        for j in st.session_state.pista:
            style = "primary" if st.session_state.j_sel == j else "secondary"
            if st.button(f"{j.split('.')[0]}", key=f"b_{j}", type=style):
                st.session_state.j_sel = j; st.rerun()
        st.write("---")
        if st.button("🗑️ BORRAR ÚLTIMA"): st.session_state.log.pop() if st.session_state.log else None; st.rerun()

    with col_c: # CAMPO VISUAL
        st.markdown('<div class="court-container">', unsafe_allow_html=True)
        z1, z2, z3 = st.columns(3)
        if z1.button("ESQ IZQ"): st.session_state.z_sel = "ESQ_IZQ"
        if z2.button("TRIPLE"): st.session_state.z_sel = "TRIPLE_F"
        if z3.button("ESQ DER"): st.session_state.z_sel = "ESQ_DER"
        m1, m2, m3 = st.columns([1, 1.5, 1])
        if m1.button("45º IZQ"): st.session_state.z_sel = "45_IZQ"
        if m2.button("🟦 PINTURA", type="primary"): st.session_state.z_sel = "PINTURA"
        if m3.button("45º DER"): st.session_state.z_sel = "45_DER"
        st.markdown('</div>', unsafe_allow_html=True)

        st.write(f"**{st.session_state.j_sel}** en **{st.session_state.z_sel}**")
        p1, p2, p3, pf = st.columns(4)
        if p1.button("✅ 1P"): registrar("ANOTADO", 1)
        if p2.button("✅ 2P"): registrar("ANOTADO", 2)
        if p3.button("✅ 3P"): registrar("ANOTADO", 3)
        if pf.button("⭕ FALLO"): registrar("FALLO", 0)

        st.write("---")
        rb1, rb2 = st.columns(2)
        if rb1.button("📥 REB DEF"): registrar("REB_DEF", 0)
        if rb2.button("🚀 REB OF"): registrar("REB_OF", 0)

    with col_a: # FILOSOFÍA
        st.caption("🧠 FILOSOFÍA")
        if st.button("🔄 INVERSIÓN", type="primary"):
            st.session_state.inv_en_pos += 1; registrar("INVERSION", 0)
        if st.button("🎨 PAINT TOUCH"):
            st.session_state.pt_en_pos += 1; registrar("PAINT_TOUCH", 0)
        
        f1, f2 = st.columns(2)
        if f1.button("🅰️ ASIST"): registrar("ASIST", 0)
        if f2.button("🧤 ROBO"): registrar("ROBO", 0)
        if st.button("🟥 FALTA NUESTRA"): registrar("FALTA", 0)
        
        st.write("---")
        st.caption("🚫 RIVAL")
        st.session_state.riv_sel = st.selectbox("Riv:", st.session_state.rivales, label_visibility="collapsed")
        ra, rb = st.columns(2)
        if ra.button("R-2 ✅"): registrar("RIVAL-2", 2, "Rival")
        if rb.button("R-3 ✅"): registrar("RIVAL-3", 3, "Rival")
        if ra.button("R-FAL"): registrar("FALTA_RIVAL", 0, "Rival")
        if rb.button("R-TOV"): registrar("PERD_RIVAL", 0, "Rival")

if st.session_state.log:
    with st.sidebar:
        df = pd.DataFrame(st.session_state.log)
        st.download_button("📥 DESCARGAR CSV", df.to_csv(index=False), "stats_ipad.csv")
        st.dataframe(df.iloc[::-1])
