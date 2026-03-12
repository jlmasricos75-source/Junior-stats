import streamlit as st
import pandas as pd

# 1. Configuración de la página (Debe ser lo primero)
st.set_page_config(page_title="Scouting ADN", layout="wide")

# 2. Inyección de CSS (CORREGIDO: Ahora está dentro de un string de Python)
st.markdown("""
    <style>
    :root {
        --primary: #0047ab;
        --bg: #f4f7f6;
        --shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main {
        background-color: var(--bg);
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    /* Optimización para tablets/iPad */
    @media (max-width: 768px) {
        .stButton>button {
            height: 4em;
            font-size: 1.2rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Lógica de la aplicación
st.title("🏀 Panel de Scouting - Junior")

if 'historial' not in st.session_state:
    st.session_state.historial = []

col_stats, col_hist = st.columns([2, 1])

with col_stats:
    st.subheader("Registro de Acciones")
    
    # Filas de botones
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ CANASTA 2PT", type="primary"):
            st.session_state.historial.append({"Acción": "Canasta 2PT", "Hora": pd.Timestamp.now().strftime('%H:%M:%S')})
    with c2:
        if st.button("❌ FALLO 2PT"):
            st.session_state.historial.append({"Acción": "Fallo 2PT", "Hora": pd.Timestamp.now().strftime('%H:%M:%S')})

    c3, c4 = st.columns(2)
    with c3:
        if st.button("🎯 TRIPLE OK"):
            st.session_state.historial.append({"Acción": "Triple OK", "Hora": pd.Timestamp.now().strftime('%H:%M:%S')})
    with c4:
        if st.button("🚫 TRIPLE FALLO"):
            st.session_state.historial.append({"Acción": "Triple Fallo", "Hora": pd.Timestamp.now().strftime('%H:%M:%S')})

    if st.button("🗑️ Borrar Última Acción"):
        if st.session_state.historial:
            st.session_state.historial.pop()
            st.rerun()

with col_hist:
    st.subheader("Eventos")
    if st.session_state.historial:
        df = pd.DataFrame(st.session_state.historial)
        st.dataframe(df, use_container_width=True, hide_index=True)
        if st.button("Limpiar Sesión"):
            st.session_state.historial = []
            st.rerun()
    else:
        st.info("No hay jugadas registradas.")
