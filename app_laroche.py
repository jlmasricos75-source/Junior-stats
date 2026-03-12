import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="ADN Junior Pro v53", layout="wide")

st.markdown("""

.stButton>button { width: 100%; border-radius: 12px; font-weight: bold; height: 4.5em; margin-bottom: 8px; }
.adn-box { background-color: #fff7ed; border: 2px solid #f97316; padding: 10px; border-radius: 10px; text-align: center; }

""", unsafe_allow_html=True)

PLAYERS_DB = {
"JUNIOR A": ["3.SERRA", "8.MORANA", "15.AMER", "18.GABI", "21.ALÓS", "50.FERRER", "99.PEPE"],
"JUNIOR B": ["2.LUCAS", "5.ADRIÁN", "9.ANDREU", "11.ALEJ.", "12.DAVID", "23.ANT.", "24.CARLOS", "28.DERIN", "32.GONZALO", "82.MIGUEL"]
}

if 'log' not in st.session_state: st.session_state.log = []
if 'fase' not in st.session_state: st.session_state.fase = "CONFIG"
if 'pista' not in st.session_state: st.session_state.pista = []
if 'convocados' not in st.session_state: st.session_state.convocados = []
if 'pos_n' not in st.session_state: st.session_state.pos_n = 1
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'adn_pos' not in st.session_state: st.session_state.adn_pos = {"PT": 0, "PT8": 0, "INV": 0, "ESC": 0, "EXTRA": 0}

def registrar(accion, pts=0, tipo="Local"):
jugador = st.session_state.j_sel if tipo == "Local" else "RIVAL"
st.session_state.log.append({
"Pos#": st.session_state.pos_n, "Jugador": jugador, "Accion": accion, "Pts": pts,
"PT": st.session_state.adn_pos["PT"], "INV": st.session_state.adn_pos["INV"], "Tipo": tipo
})
st.session_state.j_sel = None
st.toast(f"Registrado: {accion}")

if st.session_state.fase == "CONFIG":
st.title("🏀 CONFIGURACIÓN v53")
c1, c2 = st.columns(2)
with c1:
for p in PLAYERS_DB["JUNIOR A"]:
if st.checkbox(p, key=f"a_{p}"): st.session_state.convocados.append(p)
with c2:
for p in PLAYERS_DB["JUNIOR B"]:
if st.checkbox(p, key=f"b_{p}"): st.session_state.convocados.append(p)
st.session_state.convocados = list(set(st.session_state.convocados))
st.session_state.pista = st.multiselect("Quinteto:", st.session_state.convocados, max_selections=5)
if st.button("EMPEZAR PARTIDO"):
if len(st.session_state.pista) == 5:
st.session_state.fase = "PARTIDO"
st.rerun()

elif st.session_state.fase == "PARTIDO":
pts_l = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
pts_r = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")

col1, col2, col3 = st.columns([1,2,1])
col1.metric("JUNIOR", pts_l)
col2.markdown(f"<div class='adn-box'>POS #{st.session_state.pos_n} | PT: {st.session_state.adn_pos['PT']}</div>", unsafe_allow_html=True)
col3.metric("RIVAL", pts_r)

st.write("---")
a1, a2, a3, a4 = st.columns(4)
if a1.button("🎨 PT"): st.session_state.adn_pos['PT'] += 1; st.rerun()
if a2.button("🔄 INV"): st.session_state.adn_pos['INV'] += 1; st.rerun()
if a3.button("🆕 SIG. POS"): 
    st.session_state.pos_n += 1
    st.session_state.adn_pos = {"PT": 0, "PT8": 0, "INV": 0, "ESC": 0, "EXTRA": 0}
    st.rerun()
if a4.button("🔄 CAMBIOS"): st.session_state.fase = "CAMBIOS"; st.rerun()

st.write("---")
cp, cc = st.columns([1, 2])
with cp:
    for j in st.session_state.pista:
        t = "primary" if st.session_state.j_sel == j else "secondary"
        if st.button(j, key=f"p_{j}", type=t): st.session_state.j_sel = j; st.rerun()
with cc:
    f1, f2, f3 = st.columns(3)
    if f1.button("✅ 1P"): registrar("1PM", 1)
    if f2.button("✅ 2P"): registrar("2PM", 2)
    if f3.button("✅ 3P"): registrar("3PM", 3)
    if st.button("❌ MISS"): registrar("MISS", 0)
    if st.button("🟥 FALTA"): registrar("FALTA", 0)
    if st.button("Rival +2"): registrar("R2", 2, "Rival")
elif st.session_state.fase == "CAMBIOS":
nueva = st.multiselect("Nueva Pista:", st.session_state.convocados, default=st.session_state.pista, max_selections=5)
if st.button("Confirmar"):
if len(nueva) == 5:
st.session_state.pista = nueva
st.session_state.fase = "PARTIDO"
st.rerun()

if st.session_state.log:
st.sidebar.download_button("Exportar CSV", pd.DataFrame(st.session_state.log).to_csv(), "stats.csv")
