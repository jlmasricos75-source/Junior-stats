import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="METRICAS JUNIOR", layout="wide")

# --- DATOS Y ORDENACIÓN ---
def extraer_numero(nombre):
    try: return int(nombre.split('.')[0])
    except: return 999

fijos_a = ["3.NACHO SERRA", "8.OSCAR MORANA", "15.JOAN AMER", "18.GABI OFICIAL", "21.MARC ALÓS", "50.ADRIAN FERRER", "99.PEPE MÁS"]
junior_b = ["2.LUCAS MÁS", "5.ADRIAN OJEDA", "9.ANDREU ESTELLÉS", "11.ALEJANDRO PELLICER", "12.DAVID NAVÍO", "23.ANTONIO PERANDRÉS", "24.CARLOS MÁS", "28.DERIN AKYUZ", "32.GONZALO", "82.MIGUEL DOLZ"]
especiales = ["PT < 8''", "Paint Touch", "Corte", "Transición", "ExtraPass+Tiro", "Tiro Reemplazo", "Stampede"]

if 'log' not in st.session_state: st.session_state.log = []
if 'inicio' not in st.session_state: st.session_state.inicio = None
if 'jugador_sel' not in st.session_state: st.session_state.jugador_sel = None
if 'zona_temp' not in st.session_state: st.session_state.zona_temp = "N/A"

def obtener_tiempo():
    if st.session_state.inicio is None: return "00:00"
    t = int(time.time() - st.session_state.inicio)
    return f"{t//60:02d}:{t%60:02d}"

# --- SIDEBAR: RIVAL SIMPLIFICADO ---
with st.sidebar:
    st.header("📋 Partido")
    rival_name = st.text_input("Rival:", value="RIVAL").upper()
    
    st.subheader("🔴 Acción Rival")
    r_num = st.text_input("Dorsal Rival:", key="r_num", placeholder="Dorsal")
    cr1, cr2 = st.columns(2)
    if cr1.button("✅ CANASTA", key="r_can"):
        st.session_state.log.append({"Min": obtener_tiempo(), "Jugador": f"Rival #{r_num}", "Acción": "Rival-Canasta", "Pts": 2, "Rival": rival_name})
    if cr2.button("❌ FALLO", key="r_fal"):
        st.session_state.log.append({"Min": obtener_tiempo(), "Jugador": f"Rival #{r_num}", "Acción": "Rival-Fallo", "Pts": 0, "Rival": rival_name})
    
    cr3, cr4 = st.columns(2)
    if cr3.button("🚀 R-OFF", key="r_roff"):
        st.session_state.log.append({"Min": obtener_tiempo(), "Jugador": f"Rival #{r_num}", "Acción": "Rival-RebOff", "Pts": 0, "Rival": rival_name})
    if cr4.button("🛡️ R-DEF", key="r_rdef"):
        st.session_state.log.append({"Min": obtener_tiempo(), "Jugador": f"Rival #{r_num}", "Acción": "Rival-RebDef", "Pts": 0, "Rival": rival_name})
    
    st.divider()
    equipo_tipo = st.radio("EQUIPO:", ["JUNIOR A", "JUNIOR B"])
    pool = sorted(fijos_a + junior_b if equipo_tipo == "JUNIOR A" else junior_b, key=extraer_numero)
    quinteto = st.multiselect("EN PISTA:", pool, max_selections=5)
    
    if st.button("🗑️ RESET"):
        st.session_state.inicio, st.session_state.log = time.time(), []
        st.rerun()

# --- MARCADOR ---
p_local = sum(d['Pts'] for d in st.session_state.log if "Rival" not in d['Jugador'])
p_rival = sum(d['Pts'] for d in st.session_state.log if "Rival" in d['Jugador'])
st.title("📊 METRICAS JUNIOR")
m1, m2, m3 = st.columns(3)
m1.metric("LOCAL", p_local)
m2.metric(rival_name, p_rival)
m3.metric("TIEMPO", obtener_tiempo())

# --- INTERFAZ LOCAL ---
if st.session_state.inicio and len(quinteto) == 5:
    st.write("### 1. Jugador")
    cols_j = st.columns(5)
    for i, j in enumerate(quinteto):
        if cols_j[i].button(j, key=f"btn_{j}", use_container_width=True, type="primary" if st.session_state.jugador_sel == j else "secondary"):
            st.session_state.jugador_sel = j

    if st.session_state.jugador_sel:
        # ZONA
        st.write(f"📍 Zona: **{st.session_state.zona_temp}**")
        z = st.columns(6)
        if z[0].button("C-IZQ"): st.session_state.zona_temp = "T3-Esq-IZQ"
        if z[1].button("45-IZQ"): st.session_state.zona_temp = "T3-45-IZQ"
        if z[2].button("FRON"): st.session_state.zona_temp = "T3-Front"
        if z[3].button("45-DER"): st.session_state.zona_temp = "T3-45-DER"
        if z[4].button("C-DER"): st.session_state.zona_temp = "T3-Esq-DER"
        if z[5].button("PINTURA", type="primary"): st.session_state.zona_temp = "Pintura"

        st.divider()
        col_stats, col_filo = st.columns(2)

        with col_stats:
            st.write("**📊 Convencionales**")
            # FILA 1: Puntos
            c1, c2, c3 = st.columns(3)
            if c1.button("✅ 2P", use_container_width=True): acc, pts = "T2-A", 2
            if c2.button("🎯 3P", use_container_width=True): acc, pts = "T3-A", 3
            if c3.button("🏀 TL", use_container_width=True): acc, pts = "TL-A", 1
            
            # FILA 2: Juego Ofensivo
            c4, c5, c6 = st.columns(3)
            if c4.button("❌ Fallo", use_container_width=True): acc, pts = "Fallo", 0
            if c5.button("🤝 ASIST", use_container_width=True): acc, pts = "AST", 0
            if c6.button("👟 PERD", use_container_width=True): acc, pts = "TOV", 0
            
            # FILA 3: Defensa y Rebote
            c7, c8, c9 = st.columns(3)
            if c7.button("🚀 R-OFF", use_container_width=True): acc, pts = "REB-O", 0
            if c8.button("🛡️ R-DEF", use_container_width=True): acc, pts = "REB-D", 0
            if c9.button("🧤 ROBO", use_container_width=True): acc, pts = "STL", 0
            
            # FILA 4: Otros
            c10, c11, c12 = st.columns(3)
            if c10.button("✋ TAPÓN", use_container_width=True): acc, pts = "BLK", 0
            if c11.button("⚠️ FALTA", use_container_width=True): acc, pts = "PF", 0
            if c12.button("🎁 F.REC", use_container_width=True): acc, pts = "F-REC", 0

        with col_filo:
            st.write("**✨ Filosofía**")
            grid = st.columns(2)
            for m in especiales:
                if grid[especiales.index(m)%2].button(m, use_container_width=True):
                    acc, pts = m, 0

        if 'acc' in locals():
            st.session_state.log.append({
                "Min": obtener_tiempo(), "Jugador": st.session_state.jugador_sel,
                "Zona": st.session_state.zona_temp, "Acción": acc, "Pts": pts, "Rival": rival_name
            })
            st.toast(f"Registrado: {acc}")
            st.rerun()

    if st.button("🔄 Nueva Posesión / Limpiar", use_container_width=True):
        st.session_state.jugador_sel, st.session_state.zona_temp = None, "N/A"
        st.rerun()

# --- HISTORIAL ---
if st.session_state.log:
    st.divider()
    df = pd.DataFrame(st.session_state.log)
    st.dataframe(df.iloc[::-1].head(10), use_container_width=True)
    
