import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Laroche Stats Pro", layout="wide")

# --- DATA OFICIAL ---
fijos_a = ["3.-NACHO SERRA", "8.-OSCAR MORANA", "15.-JOAN AMER", "18.-GABI OFICIAL", "21.-MARC ALÓS", "50.-ADRIAN FERRER", "99.-PEPE MÁS"]
junior_b = ["2.-LUCAS MÁS", "5.-ADRIAN OJEDA", "9.-ANDREU ESTELLÉS", "11.-ALEJANDRO PELLICER", "12.-DAVID NAVÍO", "23.-ANTONIO PERANDRÉS", "24.-CARLOS MÁS", "28.-DERIN AKYUZ", "32.-GONZALO", "82.-MIGUEL DOLZ"]
medidas = ["Paint Touch", "Corte", "Transición", "ExtraPass+Tiro", "Tiro Reemplazo", "Stampede"]

# --- INICIALIZACIÓN SEGURA ---
if 'log' not in st.session_state: st.session_state.log = []
if 'inicio' not in st.session_state: st.session_state.inicio = None
if 'jugador_sel' not in st.session_state: st.session_state.jugador_sel = None

# --- FUNCIONES DE APOYO ---
def obtener_tiempo():
    if st.session_state.inicio is None:
        return "00:00"
    t_segundos = int(time.time() - st.session_state.inicio)
    mins, segs = divmod(t_segundos, 60)
    return f"{mins:02d}:{segs:02d}"

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Panel de Control")
    equipo = st.radio("EQUIPO:", ["JUNIOR A", "JUNIOR B"])
    pool = sorted(fijos_a + junior_b) if equipo == "JUNIOR A" else sorted(junior_b)
    quinteto = st.multiselect("QUINTETO EN PISTA:", pool, max_selections=5)
    
    st.divider()
    # Botón de Inicio con confirmación visual
    if st.button("🚀 INICIAR PARTIDO / RESET", use_container_width=True):
        st.session_state.inicio = time.time()
        st.session_state.log = []
        st.session_state.jugador_sel = None
        st.rerun()

    if st.session_state.inicio:
        st.success(f"⏱️ Reloj activo: {obtener_tiempo()}")

# --- INTERFAZ PRINCIPAL ---
st.title(f"📊 Laroche {equipo}")

# CAPA DE SEGURIDAD 1: Si no hay reloj, no hay botones
if st.session_state.inicio is None:
    st.warning("⚠️ El sistema está en espera. Pulsa 'INICIAR PARTIDO' en el menú lateral para activar la toma de datos.")
# CAPA DE SEGURIDAD 2: Si no hay quinteto, avisar
elif len(quinteto) < 5:
    st.info("👈 Selecciona los 5 jugadores que están en pista ahora mismo.")
else:
    # 1. SELECTOR DE JUGADOR
    st.write("### 1. Selecciona Jugador")
    cols_j = st.columns(5)
    for i, j in enumerate(quinteto):
        label = f"🏀 {j}" if st.session_state.jugador_sel == j else j
        if cols_j[i].button(label, key=f"j_{j}", use_container_width=True, 
                            type="primary" if st.session_state.jugador_sel == j else "secondary"):
            st.session_state.jugador_sel = j

    # 2. SELECTOR DE ACCIÓN
    if st.session_state.jugador_sel:
        st.divider()
        t_marcado = obtener_tiempo()
        st.subheader(f"Registrando para: {st.session_state.jugador_sel} (Min {t_marcado})")
        
        # FILOSOFÍA (Medidas Especiales)
        st.markdown("#### ✨ FILOSOFÍA LAROCHE")
        c1, c2, c3 = st.columns(3)
        for idx, m in enumerate(medidas):
            target_col = [c1, c2, c3][idx % 3]
            if target_col.button(f"🎯 {m}", key=f"m_{m}", use_container_width=True):
                st.session_state.log.append({
                    "Min": t_marcado, "Jugador": st.session_state.jugador_sel,
                    "Tipo": "FILOSOFÍA", "Acción": m
                })
                st.session_state.jugador_sel = None
                st.rerun()

        # CONVENCIONAL
        st.markdown("#### 📊 CONVENCIONAL")
        cv1, cv2, cv3, cv4 = st.columns(4)
        if cv1.button("✅ CANASTA", use_container_width=True): acc = "Canasta"
        if cv2.button("❌ FALLO", use_container_width=True): acc = "Fallo"
        if cv3.button("🛡️ REB", use_container_width=True): acc = "Rebote"
        if cv4.button("👟 PERD", use_container_width=True): acc = "Pérdida"

        if 'acc' in locals():
            st.session_state.log.append({
                "Min": t_marcado, "Jugador": st.session_state.jugador_sel,
                "Tipo": "CONVENCIONAL", "Acción": acc
            })
            st.session_state.jugador_sel = None
            st.rerun()

# --- TABLA DE DATOS ---
if st.session_state.log:
    st.divider()
    df = pd.DataFrame(st.session_state.log)
    st.write("📝 Últimas acciones (para control de vídeo):")
    st.dataframe(df.iloc[::-1], use_container_width=True)
    
    # Botón para descargar
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar CSV", csv, "partido_laroche.csv", "text/csv")
