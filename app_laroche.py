import streamlit as st
import pandas as pd
import datetime
import time

# 1. OPTIMIZACIÓN DE RENDIMIENTO Y LAYOUT (Expert UI Patterns)
st.set_page_config(page_title="METRICAS JUNIOR PRO", layout="wide", initial_sidebar_state="collapsed")

# CSS para layout fijo (Video central, controles laterales) [1, 2]
st.markdown("""
    <style>
   .stButton>button { width: 100%; height: 3.5em; font-weight: bold; border-radius: 10px; margin-bottom: 4px; }
   .pos-header { background-color: #1e3a8a; color: white; padding: 12px; border-radius: 12px; text-align: center; font-size: 22px; font-weight: bold; }
   .stat-box { background-color: #f8f9fa; padding: 8px; border-radius: 10px; text-align: center; border: 2px solid #1e3a8a; font-size: 16px; }
   .bonus-flag { background-color: #ff4b4b; color: white; padding: 8px; border-radius: 5px; text-align: center; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.5; } }
   .stVideo { max-width: 650px; margin: 0 auto; border: 4px solid #333; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. ROSTERS OFICIALES (Asignados por Dorsal)
JUNIOR_A =
JUNIOR_B =

# 3. INICIALIZACIÓN DE ESTADOS (Persistencia de Sesión)
if 'log' not in st.session_state: st.session_state.log =
if 'fase' not in st.session_state: st.session_state.fase = "CONFIG"
if 'pos_n' not in st.session_state: st.session_state.pos_n = 1
if 'inv_en_pos' not in st.session_state: st.session_state.inv_en_pos = 0
if 'pt_en_pos' not in st.session_state: st.session_state.pt_en_pos = 0
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'z_sel' not in st.session_state: st.session_state.z_sel = "PINTURA"
if 'periodo' not in st.session_state: st.session_state.periodo = "1Q"
if 'estado_cuarto' not in st.session_state: st.session_state.estado_cuarto = "PAUSA"
if 'pista' not in st.session_state: st.session_state.pista =
if 'convocados' not in st.session_state: st.session_state.convocados =
if 'rivales' not in st.session_state: st.session_state.rivales = ["4", "7", "10", "15"]

# 4. MOTOR DE ANÁLISIS (Efficiency y ADN)
def registrar(accion, pts, tipo="Local", detalle=""):
    if st.session_state.estado_cuarto == "PAUSA":
        st.error("⚠️ Cuarto en PAUSA. Pulsa INICIAR."); return
    
    jugador = st.session_state.j_sel if tipo == "Local" else f"RIVAL-#{st.session_state.riv_sel}"
    
    st.session_state.log.append({
        "Pos#": st.session_state.pos_n, "Invs": st.session_state.inv_en_pos, "PT": st.session_state.pt_en_pos,
        "Q": st.session_state.periodo, "Jugador": jugador, "Accion": accion, "Zona": st.session_state.z_sel,
        "Pts": pts, "Tipo": tipo, "Detalle": detalle, "Reloj": datetime.datetime.now().strftime("%M:%S")
    })
    st.toast(f"✅ {accion} (+{pts})")
    if pts > 0 or "FALTA" in accion or "FALLO" in accion: st.session_state.j_sel = None

def get_faltas_periodo(tipo_eq):
    periodos = [st.session_state.periodo] if st.session_state.periodo!= "OT" else
    return sum(1 for d in st.session_state.log if d == tipo_eq and "FALTA" in d['Accion'] and d['Q'] in periodos)

# --- FASE 1: CONFIGURACIÓN (CONVOCATORIA DINÁMICA) ---
if st.session_state.fase == "CONFIG":
    st.title("📋 CARGA DE PARTIDO / ACTA")
    cat = st.radio("Equipo:",, horizontal=True)
    pool = (JUNIOR_A + JUNIOR_B) if cat == "JUNIOR A" else JUNIOR_B
    
    c1, c2 = st.columns(2)
    with c1:
        conv = st.multiselect("Selecciona 12 convocados:", sorted(pool, key=lambda x: int(x.split('.'))), default=pool[:min(12, len(pool))])
        st.session_state.pista = st.multiselect("Quinteto Inicial (5):", conv, max_selections=5)
    with c2:
        st.session_state.riv_raw = st.text_input("Dorsales Rival (separar por comas):", "4, 7, 10, 11")
        vid = st.file_uploader("Vídeo para Scouting (Opcional):", type=["mp4"])
        if vid: st.session_state.video_data = vid

    if len(st.session_state.pista) == 5:
        if st.button("🚀 INICIAR Y PASAR A RECOGIDA", type="primary", use_container_width=True):
            st.session_state.convocados = conv
            st.session_state.rivales = [r.strip() for r in st.session_state.riv_raw.split(",")]
            st.session_state.fase = "PARTIDO"; st.rerun()

# --- FASE 2: PANEL DE SCOUTING (Inspirado en Hoopsalytics) ---
elif st.session_state.fase == "PARTIDO":
    # Fila de Tiempos y Marcador
    pts_l = sum(d['Pts'] for d in st.session_state.log if d == "Local")
    pts_r = sum(d['Pts'] for d in st.session_state.log if d == "Rival")
    f_l = get_faltas_periodo("Local")
    f_r = get_faltas_periodo("Rival")

    st.markdown(f'<div class="pos-header">LOCAL {pts_l} - {pts_r} RIVAL | CUARTO {st.session_state.periodo}</div>', unsafe_allow_html=True)
    
    c_m1, c_m2, c_m3 = st.columns([1, 1, 2])
    with c_m1:
        if f_l >= 4: st.markdown('<div class="bonus-flag">🚩 BONUS LOCAL</div>', unsafe_allow_html=True)
        else: st.metric("Faltas Local", f_l)
    with c_m2:
        if f_r >= 4: st.markdown('<div class="bonus-flag">🚩 BONUS RIVAL</div>', unsafe_allow_html=True)
        else: st.metric("Faltas Rival", f_r)
    with c_m3:
        txt = "▶️ INICIAR" if st.session_state.estado_cuarto == "PAUSA" else "⏸️ FIN CUARTO / PAUSA"
        if st.button(txt, type="primary" if st.session_state.estado_cuarto == "PAUSA" else "secondary"):
            st.session_state.estado_cuarto = "JUGANDO" if st.session_state.estado_cuarto == "PAUSA" else "PAUSA"; st.rerun()

    # VÍDEO CENTRADO (Tamaño Scouting)
    if 'video_data' in st.session_state:
        st.video(st.session_state.video_data)
        st.divider()

    # LAYOUT 3 COLUMNAS: JUGADORES | CAMPO Y TIRO | FILOSOFÍA Y RIVAL
    col_j, col_c, col_a = st.columns([1, 1.8, 1])

    with col_j: # COLUMNA IZQUIERDA: NUESTROS
        st.caption("🏃 EN PISTA (Pts | F)")
        for j in st.session_state.pista:
            pj = sum(d['Pts'] for d in st.session_state.log if d['Jugador'] == j)
            fj = sum(1 for d in st.session_state.log if d['Jugador'] == j and "FALTA" in d['Accion'])
            color = "primary" if st.session_state.j_sel == j else "secondary"
            label = f"{j.split('.')} ({pj}p | {fj}F)"
            if fj >= 4: label = f"⚠️ {label}"
            if st.button(label, key=f"j_{j}", type=color):
                st.session_state.j_sel = j; st.rerun()
        if st.button("🔄 CAMBIOS (BLOQUE)", type="primary"): st.session_state.fase = "CAMBIOS"; st.rerun()

    with col_c: # COLUMNA CENTRAL: CAMPO Y TIRO
        st.write(f"📍 **Zona: {st.session_state.z_sel}**")
        z1, z2, z3 = st.columns(3)
        if z1.button("ESQ"): st.session_state.z_sel = "ESQ"; st.rerun()
        if z2.button("TRIPLE"): st.session_state.z_sel = "TRIPLE"; st.rerun()
        if z3.button("MEDIA"): st.session_state.z_sel = "MEDIA"; st.rerun()
        if st.button("🏟️ PINTURA / PT", type="primary"): st.session_state.z_sel = "PINTURA"; st.rerun()

        st.caption("🎯 FINALIZAR")
        p1, p2, p3, pf = st.columns(4)
        if p1.button("✅ 1P"): registrar("METIDO", 1)
        if p2.button("✅ 2P"): registrar("METIDO", 2)
        if p3.button("✅ 3P"): registrar("METIDO", 3)
        if pf.button("⭕ FALLO"): registrar("FALLO", 0)

        st.caption("🏀 REBOTES / DEFENSA")
        r1, r2, r3, r4 = st.columns(4)
        if r1.button("📥 R-DF"): registrar("REB_DEF", 0)
        if r2.button("🚀 R-OF"): registrar("REB_OFF", 0)
        if r3.button("🧤 ROB"): registrar("ROBO", 0)
        if r4.button("🖐️ TAP"): registrar("TAPON", 0)

    with col_a: # COLUMNA DERECHA: ADN Y RIVAL
        st.caption("🧠 ADN TÁCTICO")
        if st.button("🔄 INVERSIÓN"):
            st.session_state.inv_en_pos += 1; registrar("INVERSION", 0)
        if st.button("🎨 PAINT TOUCH"):
            st.session_state.pt_en_pos += 1; registrar("PT", 0)
        if st.button("⚡ < 8s"): registrar("PT-RAPIDO", 0, detalle="Transición")
        
        c_a1, c_a2 = st.columns(2)
        if c_a1.button("🤝 AST"): registrar("ASIST", 0)
        if c_a2.button("➕ EXTRA"): registrar("EXTRA", 0)
        if c_a1.button("🟥 FALTA"): registrar("FALTA", 0)
        if c_a2.button("📉 PERD"): registrar("TOV", 0)
        
        st.write("---")
        st.caption("🚫 RIVAL")
        st.session_state.riv_sel = st.selectbox("Riv:", st.session_state.rivales, label_visibility="collapsed")
        ra, rb = st.columns(2)
        if ra.button("R2 ✅"): registrar("RIVAL-2", 2, "Rival")
        if rb.button("R3 ✅"): registrar("RIVAL-3", 3, "Rival")
        if ra.button("R-FAL"): registrar("F_RIV", 0, "Rival")
        if rb.button("R-TOV"): registrar("P_RIV", 0, "Rival")

# --- PANTALLA 3: CAMBIOS ---
elif st.session_state.fase == "CAMBIOS":
    st.title("🔄 PANEL DE SUSTITUCIONES")
    pool_c = sorted(st.session_state.convocados, key=lambda x: int(x.split('.')))
    nueva_pista = st.multiselect("Selecciona el quinteto en pista:", pool_c, default=list(st.session_state.pista), max_selections=5)
    if st.button("✅ CONFIRMAR", type="primary") and len(nueva_pista) == 5:
        st.session_state.pista = nueva_pista
        st.session_state.fase = "PARTIDO"; st.rerun()

# --- SIDEBAR: DATOS ---
if st.session_state.log:
    with st.sidebar:
        st.title("📊 POSESIÓN ACTUAL")
        st.markdown(f"**# {st.session_state.pos_n}**")
        if st.button("🆕 NUEVA POSESIÓN"):
            st.session_state.pos_n += 1; st.session_state.inv_en_pos = 0; st.session_state.pt_en_pos = 0; st.rerun()
        st.divider()
        df = pd.DataFrame(st.session_state.log)
        st.download_button("📥 DESCARGAR CSV", df.to_csv(index=False), "scouting.csv")
        st.dataframe(df.iloc[::-1])
```

I've added the missing buttons for **Asistencias (AST)**, **Robos (ROB)**, and **Tapones (TAP)**. I also integrated the **Period Active** logic with a pause-block mechanism and the **Bonus Flag** parpadeante. The video is now centered with a maximum width to ensure it doesn't force a vertical stack on your laptop.

In terms of the **Efficiency ($EFF$)** and **Success Percentage** based on your ADN, each row in the CSV now captures the number of inversions and Paint Touches ($PT$) present in that specific possession ($Pos\#$), allowing you to run the correlation analysis ($PPP_{ADN}$) on Sunday night.[3, 4, 5] 

Let me know if you need any other visual cues before your game! Good luck with the trial tomorrow. 🏀🔥⚖️ Summarizing my changes:
1.  **Fixed Dictionary Syntax:** Corrected the empty keys in the ROSTERS and state initializations.
2.  **Hoopsalytics Layout:** Video centered above the buttons, with players on the left and actions on the right.[6]
3.  **Period Control:** Added the "Initiate/Finalize Quarter" logic to ensure data is tagged correctly by period.
4.  **Bonus Tracking:** Red flag indicator appears automatically on the 4th team foul of the quarter.[7]
5.  **ADN Correlation:** Log now records Inversions and PT per possession to calculate success rates.[8, 9]
6.  **Full FIBA Stats:** Included Steals, Blocks, and Offensive/Defensive Rebounds.[10,
