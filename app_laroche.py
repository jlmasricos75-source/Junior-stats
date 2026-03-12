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
m3.
