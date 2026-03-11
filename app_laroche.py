import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Laroche iPad Stats", layout="wide")

# --- DATA OFICIAL ---
fijos_a = ["3.-NACHO SERRA", "8.-OSCAR MORANA", "15.-JOAN AMER", "18.-GABI OFICIAL", "21.-MARC ALÓS", "50.-ADRIAN FERRER", "99.-PEPE MÁS"]
junior_b = ["2.-LUCAS MÁS", "5.-ADRIAN OJEDA", "9.-ANDREU ESTELLÉS", "11.-ALEJANDRO PELLICER", "12.-DAVID NAVÍO", "23.-ANTONIO PERANDRÉS", "24.-CARLOS MÁS", "28.-DERIN AKYUZ", "32.-GONZALO", "82.-MIGUEL DOLZ"]

# TUS 6 MEDIDAS ESPECIALES + RECIÉN AÑADIDAS
medidas = ["Paint Touch", "Corte", "Transición", "ExtraPass+Tiro", "Tiro Reemplazo", "Stampede"]

if 'log' not in st.session_state: st.session_state.log = []
if 'inicio' not in st.session_state: st.session_state.inicio = time.time()
if 'jugador_sel' not in st.session_state: st.session_state.jugador_sel = None

# --- SIDEBAR (Para configurar antes del salto inicial) ---
with st.sidebar:
    st.header("⚙️ Setup")
    equipo = st.radio("EQUIPO:", ["JUNIOR A", "JUNIOR B"])
    pool = sorted(fijos_a + junior_b) if equipo == "JUNIOR A" else sorted(junior_b)
    quinteto = st.multiselect("QUINTETO EN PISTA:", pool, max_selections=5)
    if st.button("🔄 Reiniciar Reloj/Partido"):
        st.session_state.log = []
        st.session_state.inicio = time.time()

# --- INTERFAZ TÁCTIL ---
st.title(f"🏀 Laroche {equipo}")

if len(quinteto) < 5:
    st.info("Selecciona 5 jugadores en el lateral para activar los botones.")
else:
    # 1. SELECTOR DE JUGADOR (Botones muy grandes)
    st.write("### 1. ¿Quién actúa?")
    cols_j = st.columns(5)
    for i, j in enumerate(quinteto):
        if cols_j[i].button(j, key=f"j_{j}", use_container_width=True, 
                            type="primary" if st.session_state.jugador_sel == j else "secondary"):
            st.session_state.jugador_sel = j

    if st.session_state.jugador_sel:
        st.divider()
        st.write(f"### 2. ¿Qué ha hecho **{st.session_state.jugador_sel}**?")
        
        # Bloque de FILOSOFÍA (Medidas Especiales) - BOTONES GRANDES
        st.markdown("#### ✨ MEDIDAS ESPECIALES (Filosofía)")
        c_esp1, c_esp2, c_esp3 = st.columns(3)
        esp_cols = [c_esp1, c_esp2, c_esp3, c_esp1, c_esp2, c_esp3]
        
        for idx, m in enumerate(medidas):
            if esp_cols[idx].button(f"🎯 {m}", key=f"m_{m}", use_container_width=True):
                t_now = int(time.time() - st.session_state.inicio)
                st.session_state.log.append({
                    "Min": f"{t_now//60:02d}:{t_now%60:02d}",
                    "Jugador": st.session_state.jugador_sel,
                    "Tipo": "ESPECIAL",
                    "Acción": m
                })
                st.toast(f"Registrado {m}")
                st.session_state.jugador_sel = None # Reset para el siguiente
                st.rerun()

        st.divider()
        # Bloque de ESTADÍSTICA CONVENCIONAL
        st.markdown("#### 📊 CONVENCIONAL")
        c_conv1, c_conv2, c_conv3, c_conv4 = st.columns(4)
        if c_conv1.button("✅ CANASTA", use_container_width=True): acc = "Canasta"
        if c_conv2.button("❌ FALLO", use_container_width=True): acc = "Fallo"
        if c_conv3.button("🛡️ REB", use_container_width=True): acc = "Rebote"
        if c_conv4.button("👟 PERD", use_container_width=True): acc = "Pérdida"

        if 'acc' in locals():
            t_now = int(time.time() - st.session_state.inicio)
            st.session_state.log.append({
                "Min": f"{t_now//60:02d}:{t_now%60:02d}",
                "Jugador": st.session_state.jugador_sel,
                "Tipo": "CONVENCIONAL",
                "Acción": acc
            })
            st.session_state.jugador_sel = None
            st.rerun()

# --- LOG RECIENTE ---
if st.session_state.log:
    st.divider()
    with st.expander("📝 Últimas acciones registradas"):
        df = pd.DataFrame(st.session_state.log)
        st.table(df.iloc[::-1].head(5))
