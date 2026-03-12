import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="METRICAS JUNIOR PRO", layout="wide", initial_sidebar_state="collapsed")

# --- ESTADO DE SESIÓN ---
if 'log' not in st.session_state: st.session_state.log = []
if 'pos_n' not in st.session_state: st.session_state.pos_n = 1
if 'inicio' not in st.session_state: st.session_state.inicio = None
if 'jugador_sel' not in st.session_state: st.session_state.jugador_sel = None
if 'zona_sel' not in st.session_state: st.session_state.zona_sel = None

def get_time():
    if not st.session_state.inicio: return "00:00"
    t = int(time.time() - st.session_state.inicio)
    return f"{t//60:02d}:{t%60:02d}"

# --- DISEÑO DEL CAMPO (HTML/CSS) ---
# Esto crea una representación visual más parecida a un campo real
st.markdown("""
    <style>
    .court-container { border: 2px solid #333; border-radius: 10px; background-color: #fdf5e6; padding: 15px; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
pts_l = sum(d['Pts'] for d in st.session_state.log if "Rival" not in d['Jugador'])
c1, c2, c3 = st.columns([1,1,1])
c1.metric("POSESIÓN", f"#{st.session_state.pos_n}")
c2.metric("PUNTOS LOCAL", pts_l)
c3.metric("TIEMPO", get_time())

# --- CUERPO DE LA APP ---
if st.session_state.inicio:
    # 1. SELECTOR DE JUGADOR (SIEMPRE ARRIBA)
    jugadores = ["3.NACHO", "8.OSCAR", "15.JOAN", "18.GABI", "21.MARC", "50.ADRIAN", "99.PEPE"]
    cols_j = st.columns(len(jugadores))
    for idx, j in enumerate(jugadores):
        if cols_j[idx].button(j, key=f"btn_{j}", type="primary" if st.session_state.jugador_sel == j else "secondary"):
            st.session_state.jugador_sel = j

    st.divider()

    # 2. COLUMNAS PRINCIPALES (CAMPO IZQ | ACCIONES DER)
    col_mapa, col_stats = st.columns([1.8, 1])

    with col_mapa:
        st.subheader("📍 Plano del Campo")
        with st.container():
            # FILA TRIPLES
            z1, z2, z3, z4, z5 = st.columns(5)
            if z1.button("CORNER L", use_container_width=True): st.session_state.zona_sel = "T3-C-L"
            if z2.button("45° L", use_container_width=True): st.session_state.zona_sel = "T3-45-L"
            if z3.button("FRONT", use_container_width=True): st.session_state.zona_sel = "T3-F"
            if z4.button("45° R", use_container_width=True): st.session_state.zona_sel = "T3-45-R"
            if z5.button("CORNER R", use_container_width=True): st.session_state.zona_sel = "T3-C-R"
            
            # FILA MEDIA / PINTURA
            st.write("")
            m1, pintura, m2 = st.columns([1, 2, 1])
            if m1.button("MED L", use_container_width=True): st.session_state.zona_sel = "M-L"
            with pintura:
                if st.button("🏟️ PINTURA (POSTE/ENTRADA) 🏟️", type="primary", use_container_width=True):
                    st.session_state.zona_sel = "PINTURA"
            if m2.button("MED R", use_container_width=True): st.session_state.zona_sel = "M-R"
        
        st.info(f"Seleccionado: **{st.session_state.jugador_sel or 'Nadie'}** en **{st.session_state.zona_sel or '---'}**")

    with col_stats:
        st.subheader("📝 Acciones")
        # MÉTRICAS CONVENCIONALES
        a1, a2, a3 = st.columns(3)
        ev, p, finish = None, 0, False
        if a1.button("✅ CAN", use_container_width=True): 
            ev = "CANASTA"; p = 3 if "T3" in str(st.session_state.zona_sel) else 2; finish = True
        if a2.button("❌ FAL", use_container_width=True): ev = "FALLO"; finish = True
        if a3.button("🏀 TL", use_container_width=True): ev = "TL"; p = 1; finish = True

        st.write("**✨ FILOSOFÍA / OTROS**")
        f1, f2, f3 = st.columns(3)
        if f1.button("🤝 AST"): ev = "AST"; finish = True
        if f2.button("👟 TOV"): ev = "TOV"; finish = True
        if f3.button("🚀 REB"): ev = "REB"; finish = True

        for esp in ["Paint Touch", "Stampede", "ExtraPass", "Corte"]:
            if st.button(esp, use_container_width=True):
                st.session_state.log.append({"Pos": st.session_state.pos_n, "Jugador": st.session_state.jugador_sel, "Zona": st.session_state.zona_sel, "Acción": esp, "Pts": 0})
                st.toast(f"Anotado: {esp}")

        st.divider()
        if st.button("🏁 SIGUIENTE POSESIÓN", type="primary", use_container_width=True):
            if ev and finish:
                st.session_state.log.append({"Pos": st.session_state.pos_n, "Jugador": st.session_state.jugador_sel, "Zona": st.session_state.zona_sel, "Acción": ev, "Pts": p})
            st.session_state.pos_n += 1
            st.session_state.zona_sel = None
            st.rerun()

else:
    if st.button("🚀 EMPEZAR PARTIDO", type="primary", use_container_width=True):
        st.session_state.inicio = time.time()
        st.rerun()
