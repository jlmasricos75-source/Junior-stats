import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Laroche Philosophy Analytics", layout="wide")

# --- ROSTER Y FILOSOFÍA ---
fijos_a = ["3.-NACHO SERRA", "8.-OSCAR MORANA", "15.-JOAN AMER", "18.-GABI OFICIAL", "21.-MARC ALÓS", "50.-ADRIAN FERRER", "99.-PEPE MÁS"]
junior_b = ["2.-LUCAS MÁS", "5.-ADRIAN OJEDA", "9.-ANDREU ESTELLÉS", "11.-ALEJANDRO PELLICER", "12.-DAVID NAVÍO", "23.-ANTONIO PERANDRÉS", "24.-CARLOS MÁS", "28.-DERIN AKYUZ", "32.-GONZALO", "82.-MIGUEL DOLZ"]

# TUS MEDIDAS ESPECIALES
medidas_especiales = ["Paint Touch", "Corte", "Transición", "ExtraPass+Tiro", "Tiro en Reemplazo", "Stampede", "Otro/Desequilibrio"]

if 'log' not in st.session_state: st.session_state.log = []
if 'inicio' not in st.session_state: st.session_state.inicio = None
if 'jugador_activo' not in st.session_state: st.session_state.jugador_activo = None

# --- SIDEBAR ---
with st.sidebar:
    st.header("⏱️ Crono Partido")
    if st.button("🚀 INICIAR RELOJ"): st.session_state.inicio = time.time()
    
    if st.session_state.inicio:
        t = int(time.time() - st.session_state.inicio)
        st.metric("Tiempo Vídeo", f"{t//60:02d}:{t%60:02d}")
    
    equipo = st.radio("EQUIPO:", ["JUNIOR A", "JUNIOR B"])
    pool = sorted(fijos_a + junior_b) if equipo == "JUNIOR A" else sorted(junior_b)
    quinteto = st.multiselect("EN PISTA:", pool, max_selections=5)

# --- CAPTURA ---
st.title(f"🏀 Laroche {equipo} - Análisis Táctico")

if len(quinteto) < 5:
    st.warning("Selecciona el quinteto en la izquierda.")
else:
    # 1. SELECCIÓN DE JUGADOR
    cols_q = st.columns(5)
    for i, j in enumerate(quinteto):
        if cols_q[i].button(j, key=f"p_{j}", use_container_width=True, type="primary" if st.session_state.jugador_activo == j else "secondary"):
            st.session_state.jugador_activo = j

    # 2. SELECCIÓN DE ACCIÓN
    if st.session_state.jugador_activo:
        t_acc = "00:00"
        if st.session_state.inicio:
            ahora = int(time.time() - st.session_state.inicio)
            t_acc = f"{ahora//60:02d}:{ahora%60:02d}"

        st.info(f"Registrando para {st.session_state.jugador_activo} ({t_acc})")
        
        tab_conv, tab_especial = st.tabs(["📊 CONVENCIONAL", "✨ FILOSOFÍA (MEDIDAS ESPECIALES)"])
        
        with tab_conv:
            c1, c2, c3 = st.columns(3)
            if c1.button("🛡️ REB"): acc, pts, especial = "REB", 0, False
            if c2.button("🤝 AST"): acc, pts, especial = "AST", 0, False
            if c3.button("👟 TOV (Pérdida)"): acc, pts, especial = "TOV", 0, False
            if c1.button("🛡️ STL (Robo)"): acc, pts, especial = "STL", 0, False
            if c2.button("🚫 BLK (Tapón)"): acc, pts, especial = "BLK", 0, False

        with tab_especial:
            st.write("¿Cómo se generó la ventaja / Qué acción especial fue?")
            # Creamos botones para tus 6 medidas
            for medida in medidas_especiales:
                if st.button(medida, use_container_width=True):
                    # Por defecto asumimos que si marcas una medida especial ofensiva, es que ha habido puntos o tiro
                    # Aquí podrías elegir si fue acierto o fallo
                    res = st.selectbox(f"Resultado de {medida}:", ["Canasta T2", "Canasta T3", "Fallo", "Falta Recibida"])
                    puntos = 2 if "T2" in res else (3 if "T3" in res else 0)
                    
                    st.session_state.log.append({
                        "Minuto": t_acc, 
                        "Jugador": st.session_state.jugador_activo, 
                        "Acción": res, 
                        "Medida_Especial": medida, 
                        "Pts": puntos
                    })
                    st.success(f"Registrado: {medida} por {st.session_state.jugador_activo}")
                    st.session_state.jugador_activo = None
                    st.rerun()

        # Guardado para las convencionales
        if 'acc' in locals():
            st.session_state.log.append({
                "Minuto": t_acc, "Jugador": st.session_state.jugador_activo, 
                "Acción": acc, "Medida_Especial": "N/A", "Pts": pts
            })
            st.session_state.jugador_activo = None
            st.rerun()

# --- INFORMES ---
if st.session_state.log:
    st.divider()
    df = pd.DataFrame(st.session_state.log)
    
    st.header("📊 Análisis de Filosofía de Juego")
    # Gráfico de qué medida especial es más efectiva
    eficiencia = df[df['Medida_Especial'] != "N/A"].groupby("Medida_Especial")["Pts"].sum()
    st.bar_chart(eficiencia)
    
    

    with st.expander("🎥 Ver Log para Sesión de Vídeo"):
        st.table(df[["Minuto", "Jugador", "Medida_Especial", "Acción"]])
