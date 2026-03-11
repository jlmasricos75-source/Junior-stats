import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Laroche Stats Pro", layout="wide")

# Estilo Verde Oliva
st.markdown("""
    <style>
    .stButton>button {
        background-color: #556B2F;
        color: white;
        border-radius: 10px;
        height: 50px;
        width: 100%;
        font-weight: bold;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏀 LAROCHE STATS - MODO PARTIDO")

# --- SECCIÓN 1: CONFIGURACIÓN ---
with st.expander("📝 Configuración del Partido"):
    col_config1, col_config2 = st.columns(2)
    with col_config1:
        rival = st.text_input("Equipo Rival", "Rival")
    with col_config2:
        fecha = st.date_input("Fecha del Partido")

# --- SECCIÓN 2: BASE DE DATOS ---
jugadores = ["MIGUEL DOLZ", "PEPE MÁS", "JORGE GIL", "HUGO MARQUÉS", "PABLO GADEA", 
             "GONZALO C.", "CARLOS BELTRÁN", "IÑAKI LÓPEZ", "NICO GIMÉNEZ", 
             "ALEX ROMERO", "ÁLVARO CH."]

# Inicializar estado si no existe
if 'stats' not in st.session_state:
    st.session_state.stats = {j: {"T2_A": 0, "T2_F": 0, "T3_A": 0, "T3_F": 0, "TL_A": 0, "TL_F": 0, 
                                  "REB": 0, "PT": 0, "STAMPEDE": 0} for j in jugadores}

# --- SECCIÓN 3: INTERFAZ DE REGISTRO ---
tab1, tab2 = st.tabs(["📊 Registro en Vivo", "📈 Visualización y Reporte"])

with tab1:
    for j in jugadores:
        with st.container():
            col_nom, col_t2, col_t3, col_otros = st.columns([2, 2, 2, 3])
            
            with col_nom:
                st.subheader(j)
                puntos = (st.session_state.stats[j]["T2_A"] * 2) + \
                         (st.session_state.stats[j]["T3_A"] * 3) + \
                         (st.session_state.stats[j]["TL_A"] * 1)
                st.write(f"**Puntos: {puntos}**")

            with col_t2:
                c1, c2 = st.columns(2)
                if c1.button(f"+2", key=f"t2a_{j}"): st.session_state.stats[j]["T2_A"] += 1
                if c2.button(f"F2", key=f"t2f_{j}"): st.session_state.stats[j]["T2_F"] += 1
            
            with col_t3:
                c3, c4 = st.columns(2)
                if c3.button(f"+3", key=f"t3a_{j}"): st.session_state.stats[j]["T3_A"] += 1
                if c4.button(f"F3", key=f"t3f_{j}"): st.session_state.stats[j]["T3_F"] += 1

            with col_otros:
                c5, c6, c7 = st.columns(3)
                if c5.button(f"REB", key=f"reb_{j}"): st.session_state.stats[j]["REB"] += 1
                if c6.button(f"PT", key=f"pt_{j}"): st.session_state.stats[j]["PT"] += 1
                if c7.button(f"STP", key=f"stp_{j}"): st.session_state.stats[j]["STAMPEDE"] += 1
            st.divider()

with tab2:
    st.header(f"Resumen vs {rival}")
    
    # Crear DataFrame para cálculos
    df = pd.DataFrame(st.session_state.stats).T
    df['Puntos'] = (df['T2_A']*2) + (df['T3_A']*3) + (df['TL_A']*1)
    
    # Gráficas visuales rápidas
    st.subheader("Puntos por Jugador")
    st.bar_chart(df['Puntos'])
    
    st.subheader("Rebotes por Jugador")
    st.bar_chart(df['REB'])

    # Tabla detallada
    st.dataframe(df)

    # Botón de Descarga
    csv = df.to_csv().encode('utf-8')
    st.download_button("📥 DESCARGAR INFORME PARTIDO (CSV)", csv, f"stats_{rival}_{fecha}.csv", "text/csv")

if st.button("🗑️ REINICIAR PARTIDO"):
    st.session_state.stats = {j: {"T2_A": 0, "T2_F": 0, "T3_A": 0, "T3_F": 0, "TL_A": 0, "TL_F": 0, 
                                  "REB": 0, "PT": 0, "STAMPEDE": 0} for j in jugadores}
    st.rerun()
