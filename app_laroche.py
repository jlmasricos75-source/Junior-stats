import streamlit as st
import pandas as pd
import time

# Configuración para iPad/iPhone
st.set_page_config(page_title="METRICAS JUNIOR PRO", layout="wide", initial_sidebar_state="collapsed")

# --- DATOS Y ROSTER ---
def extraer_num(n):
    try: return int(n.split('.')[0])
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

# --- SIDEBAR: RIVAL Y CONFIG ---
with st.sidebar:
    st.header("🆚 RIVAL")
    rival_name = st.text_input("Nombre Rival:", value="RIVAL").upper()
    r_num = st.text_input("Dorsal Rival:", placeholder="00")
    
    c_r1, c_r2 = st.columns(2)
    if c_r1.button("✅ CANASTA"):
        st.session_state.log.append({"Min": obtener_tiempo(), "Jugador": f"Rival #{r_num}", "Zona": "N/A", "Acción": "Rival-Canasta", "Pts": 2})
    if c_r2.button("❌ FALLO"):
        st.session_state.log.append({"Min": obtener_tiempo(), "Jugador": f"Rival #{r_num}", "Zona": "N/A", "Acción": "Rival-Fallo", "Pts": 0})
    
    c_r3, c_r4 = st.columns(2)
    if c_r3.button("🚀 REB. OFF"):
        st.session_state.log.append({"Min": obtener_tiempo(), "Jugador": f"Rival #{r_num}", "Zona": "N/A", "Acción": "Rival-RebOff", "Pts": 0})
    if c_r4.button("🛡️ REB. DEF"):
        st.session_state.log.append({"Min": obtener_tiempo(), "Jugador": f"Rival #{r_num}", "Zona": "N/A", "Acción": "Rival-RebDef", "Pts": 0})
    
    st.divider()
    equipo_tipo = st.radio("EQUIPO:", ["JUNIOR A", "JUNIOR B"])
    pool = sorted(fijos_a + junior_b if equipo_tipo == "JUNIOR A" else junior_b, key=extraer_num)
    quinteto = st.multiselect("EN PISTA (5):", pool, max_selections=5)
    
    if st.button("🚨 RESET TOTAL PARTIDO"):
        st.session_state.inicio, st.session_state.log = time.time(), []
        st.rerun()

# --- MARCADOR Y RELOJ ---
p_local = sum(d['Pts'] for d in st.session_state.log if "Rival" not in d['Jugador'])
p_rival = sum(d['Pts'] for d in st.session_state.log if "Rival" in d['Jugador'])
st.title("📊 METRICAS JUNIOR")
m1, m2, m3 = st.columns(3)
m1.metric("LOCAL", p_local)
m2.metric(rival_name, p_rival)
m3.metric("RELOJ VÍDEO", obtener_tiempo())

# --- INTERFAZ DE JUEGO ---
if st.session_state.inicio and len(quinteto) == 5:
    # 1. JUGADOR
    cols_j = st.columns(5)
    for i, j in enumerate(quinteto):
        if cols_j[i].button(j, key=f"j_{j}", use_container_width=True, type="primary" if st.session_state.jugador_sel == j else "secondary"):
            st.session_state.jugador_sel = j

    if st.session_state.jugador_sel:
        # 2. ZONA
        st.write(f"📍 Zona: **{st.session_state.zona_temp}**")
        z = st.columns(6)
        z_n = ["C-IZQ", "45-IZQ", "FRON", "45-DER", "C-DER", "PINTURA"]
        z_v = ["T3-Esq-IZQ", "T3-45-IZQ", "T3-Front", "T3-45-DER", "T3-Esq-DER", "Pintura"]
        for i in range(6):
            if z[i].button(z_n[i], key=f"z_{i}"): st.session_state.zona_temp = z_v[i]

        st.divider()
        c_stats, c_filo = st.columns(2)
        acc, pts, finalizar = None, 0, False

        with c_stats:
            st.write("**📊 Convencionales (EFF)**")
            r1 = st.columns(3); r2 = st.columns(3); r3 = st.columns(3); r4 = st.columns(3)
            if r1[0].button("✅ 2P"): acc, pts, finalizar = "T2-A", 2, True
            if r1[1].button("🎯 3P"): acc, pts, finalizar = "T3-A", 3, True
            if r1[2].button("🏀 TL"): acc, pts, finalizar = "TL-A", 1, True
            if r2[0].button("❌ Fallo"): acc, pts, finalizar = "Fallo", 0, True
            if r2[1].button("🤝 ASIST"): acc, pts, finalizar = "AST", 0, True
            if r2[2].button("👟 PERD"): acc, pts, finalizar = "TOV", 0, True
            if r3[0].button("🚀 R-OFF"): acc, pts, finalizar = "REB-O", 0, True
            if r3[1].button("🛡️ R-DEF"): acc, pts, finalizar = "REB-D", 0, True
            if r3[2].button("🧤 ROBO"): acc, pts, finalizar = "STL", 0, True
            if r4[0].button("✋ TAPÓN"): acc, pts, finalizar = "BLK", 0, True
            if r4[1].button("⚠️ FALTA"): acc, pts, finalizar = "PF", 0, True
            if r4[2].button("🎁 F.REC"): acc, pts, finalizar = "F-REC", 0, True

        with c_filo:
            st.write("**✨ Filosofía**")
            for m in especiales:
                if st.button(m, use_container_width=True):
                    acc, pts, finalizar = m, 0, True

        if finalizar:
            st.session_state.log.append({
                "Min": obtener_tiempo(), "Jugador": st.session_state.jugador_sel,
                "Zona": st.session_state.zona_temp, "Acción": acc, "Pts": pts
            })
            st.rerun()

    if st.button("🔄 Nueva Posesión / Limpiar", use_container_width=True):
        st.session_state.jugador_sel, st.session_state.zona_temp = None, "N/A"
        st.rerun()

# --- ANALISIS PRO (EFF) ---
if st.session_state.log:
    st.divider()
    df = pd.DataFrame(st.session_state.log)
    df_l = df[~df['Jugador'].str.contains("Rival")]
    
    if not df_l.empty:
        st.write("### 🏆 Valoración EFF (FIBA)")
        res = df_l.groupby('Jugador').agg(
            PTS=('Pts', 'sum'),
            REB=('Acción', lambda x: x.str.contains('REB').sum()),
            AST=('Acción', lambda x: (x == 'AST').sum()),
            STL=('Acción', lambda x: (x == 'STL').sum()),
            BLK=('Acción', lambda x: (x == 'BLK').sum()),
            MISS=('Acción', lambda x: (x == 'Fallo').sum()),
            TOV=('Acción', lambda x: (x == 'TOV').sum())
        )
        res['EFF'] = (res['PTS'] + res['REB'] + res['AST'] + res['STL'] + res['BLK']) - (res['MISS'] + res['TOV'])
        st.dataframe(res[['PTS', 'REB', 'AST', 'EFF']].sort_values(by='EFF', ascending=False), use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 DESCARGAR CSV PARTIDO", csv, f"partido_{rival_name}.csv", "text/csv")
