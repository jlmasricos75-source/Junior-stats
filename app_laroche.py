import streamlit as st
import pandas as pd
import datetime

# 1. CONFIGURACIÓN BÁSICA (Evitamos funciones interactivas pesadas)
st.set_page_config(
    page_title="Scouting ADN v57",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CSS COMPATIBLE (Sin variables CSS complejas que Safari antiguo no lee)
st.markdown("""
    <style>
    body {
        background-color: #f0f2f6;
    }
    .stButton > button {
        width: 100%;
        height: 70px !important;
        font-size: 1.5rem !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        margin-bottom: 5px !important;
    }
    /* Forzamos colores simples para botones en iPad antiguos */
    .btn-green button { background-color: #28a745 !important; color: white !important; }
    .btn-red button { background-color: #dc3545 !important; color: white !important; }
    .btn-blue button { background-color: #007bff !important; color: white !important; }
    
    /* Quitamos el borde rosa de error de Streamlit si aparece */
    .stException { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. LÓGICA DE DATOS
if 'log' not in st.session_state:
    st.session_state.log = []

def registrar_evento(accion):
    hora = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.log.append({"Hora": hora, "Acción": accion})

# 4. INTERFAZ SIMPLIFICADA
st.title("SCOUTING JUNIOR - ADN")

col_izq, col_der = st.columns([2, 1])

with col_izq:
    st.subheader("CONTROL DE PARTIDO")
    
    # Fila 1
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="btn-green">', unsafe_allow_html=True)
        if st.button("CANASTA 2P"):
            registrar_evento("C-2PT")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="btn-red">', unsafe_allow_html=True)
        if st.button("FALLO 2P"):
            registrar_evento("F-2PT")
        st.markdown('</div>', unsafe_allow_html=True)

    # Fila 2
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="btn-green">', unsafe_allow_html=True)
        if st.button("TRIPLE OK"):
            registrar_evento("T-OK")
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="btn-red">', unsafe_allow_html=True)
        if st.button("T-FALLO"):
            registrar_evento("T-FALLO")
        st.markdown('</div>', unsafe_allow_html=True)

    # Fila 3
    c5, c6 = st.columns(2)
    with c5:
        st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
        if st.button("REBOTE"):
            registrar_evento("REBOTE")
        st.markdown('</div>', unsafe_allow_html=True)
    with c6:
        if st.button("FALTA"):
            registrar_evento("FALTA")

    st.write("---")
    if st.button("BORRAR ÚLTIMO"):
        if st.session_state.log:
            st.session_state.log.pop()
            st.rerun()

with col_der:
    st.subheader("REGISTRO")
    if st.session_state.log:
        # IMPORTANTE: Usamos st.table porque st.dataframe rompe iPads antiguos
        df = pd.DataFrame(st.session_state.log)
        st.table(df.tail(15)) # Tabla estática simple
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("DESCARGAR CSV", csv, "scouting.csv", "text/csv")
        
        if st.button("LIMPIAR TODO"):
            st.session_state.log = []
            st.rerun()
    else:
        st.write("Sin datos")
