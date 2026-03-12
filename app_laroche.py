import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="METRICAS VIDEO SCOUT", layout="wide", initial_sidebar_state="collapsed")

# --- ESTADOS ---
if 'log' not in st.session_state: st.session_state.log = []
if 'inicio' not in st.session_state: st.session_state.inicio = None
if 'pista' not in st.session_state: st.session_state.pista = []
if 'convocados' not in st.session_state: st.session_state.convocados = []
if 'pos_n' not in st.session_state: st.session_state.pos_n = 1
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'z_sel' not in st.session_state: st.session_state.z_sel = "Pintura"
if 'cambio_fase' not in st.session_state: st.session_state.cambio_fase = None

ROSTERS = {
    "Junior A": ["3.NACHO", "8.OSCAR", "15.JOAN", "18.GABI", "21.MARC", "50.ADRIAN", "99.PEPE", "2.LUCAS", "5.ADR.O", "11.PELLICER", "12.NAVÍO"],
    "Junior B": ["4.JUAN", "6.PABLO", "10.LUIS", "12.DAN", "14.RAUL", "20.IKER"]
}

# --- CÁLCULO DE STATS EN VIVO PARA LOS BOTONES ---
def get_stats_jugador(nombre):
    pts = sum(d['Pts'] for d in st.session_state.log if d['Jugador'] == nombre and d['Tipo'] == "Local")
    faltas = sum(1 for d in st.session_state.log if d['Jugador'] == nombre and d['Accion'] == "FALTA")
    return pts, faltas

def registrar(accion, pts, tipo="Local"):
    st.session_state.log.append({
        "Pos": st.session_state.pos_n, 
        "Reloj": int(time.time() - st.session_state.inicio) if st.session_state.inicio else 0,
        "Jugador": st.session_state.j_sel, "Zona": st.session_state.z_sel, 
        "Accion": accion, "Pts": pts, "Tipo": tipo, "Quinteto": list(st.session_state.pista)
    })
    st.toast(f"{accion} OK")

# --- CONFIGURACIÓN / VIDEO ---
if not st.session_state.inicio:
    st.title("📹 MODO SIMULACIÓN / VIDEO")
    equipo = st.selectbox("Equipo:", list(ROSTERS.keys()))
    st.session_state.convocados = st.multiselect("Convocados:", ROSTERS[equipo], default=ROSTERS[equipo])
    
    st.divider()
    video_file = st.file_uploader("Cargar video del partido (mp4):", type=["mp4", "mov"])
    if video_file:
        st.video(video_file)
        
    if len(st.session_state.convocados) >= 5:
        st.session_state.pista = st.multiselect("Quinteto Inicial:", st.session_state.convocados, max_selections=5)
        if len(st.session_state.pista) == 5 and st.button("🚀 EMPEZAR SCOUTING"):
            st.session_state.inicio = time.time(); st.rerun()
else:
    # --- INTERFAZ CON VIDEO Y BOTONES ---
    col_vid, col_stats = st.columns([1.5, 1])

    with col_vid:
        st.write("📺 **REPRODUCTOR**")
        # Aquí puedes volver a cargar el video para verlo mientras anotas
        st.info("Utiliza este espacio para el video o para ver el historial.")
        if st.button("🏁 SIGUIENTE POSESIÓN", type="primary", use_container_width=True):
            st.session_state.pos_n += 1; st.session_state.j_sel = None; st.rerun()
        
        # Historial rápido
        if st.session_state.log:
            df = pd.DataFrame(st.session_state.log).iloc[::-1]
            st.dataframe(df[['Pos', 'Jugador', 'Accion', 'Pts']].head(10), use_container_width=True)

    with col_stats:
        # BOTONES JUGADORES CON PUNTOS Y FALTAS
        st.write("🏃 **PISTA (Ptos | Faltas)**")
        q_cols = st.columns(3)
        for idx, j in enumerate(st.session_state.pista):
            p, f = get_stats_jugador(j)
            # Formato visual: Nombre + (Pts en azul / Faltas en rojo)
            label = f"{j}\n({p} pts | {f} F)"
            if q_cols[idx % 3].button(label, key=f"btn_{j}", use_container_width=True, type="primary" if st.session_state.j_sel == j else "secondary"):
                st.session_state.j_sel = j
        
        if st.button("🔄 CAMBIO", use_container_width=True):
            st.session_state.cambio_fase = "SALIENDO"; st.rerun()

        st.divider()
        
        # ACCIONES
        st.write("📍 **ZONA Y TIRO**")
        z1, z2, z3 = st.columns(3)
        if z1.button("T3"): st.session_state.z_sel = "T3"
        if z2.button("PINTURA"): st.session_state.z_sel = "Pintura"
        if z3.button("MED"): st.session_state.z_sel = "Med"
        
        c_a1, c_a2 = st.columns(2)
        if c_a1.button("✅ METIDO", use_container_width=True): registrar("MET", 3 if st.session_state.z_sel=="T3" else 2)
        if c_a2.button("❌ FALLO", use_container_width=True): registrar("FAL", 0)

        st.write("📊 **DEFENSA Y OTROS**")
        d1, d2, d3 = st.columns(3)
        if d1.button("ROBO 🧤"): registrar("ROBO", 0)
        if d2.button("FALTA 🟥"): registrar("FALTA", 0)
        if d3.button("AST"): registrar("AST", 0)
        
        st.write("🚫 **RIVAL**")
        r1, r2, r3 = st.columns(3)
        if r1.button("R-2P"): registrar("RIV-2P", 2, "Rival")
        if r2.button("R-3P"): registrar("RIV-3P", 3, "Rival")
        if r3.button("R-TL"): registrar("RIV-TL", 1, "Rival")

    # GESTIÓN DE CAMBIOS (Si se activa)
    if st.session_state.cambio_fase:
        # (Lógica de cambios de las versiones anteriores...)
        st.session_state.cambio_fase = None # Simplificado para el ejemplo
