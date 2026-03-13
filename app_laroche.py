import streamlit as st

# Configuración de página - Estilo minimalista para evitar errores de renderizado
st.set_page_config(page_title="La Roche Scouting", layout="centered")

def main():
    # --- DATOS DE PLANTILLAS ---
    junior_a_base = ["#03 SERRA", "#08 MORANA", "#15 AMER", "#18 GABI", "#21 ALÓS", "#50 FERRER", "#99 PEPE MÁS"]
    junior_b_base = [
        "#02 LUCAS MÁS", "#05 ADRIAN OJEDA", "#09 ANDREU ESTELLÉS", 
        "#11 ALEJANDRO PELLICER", "#12 DAVID NAVÍO", "#23 ANTONIO PERANDRÉS", 
        "#24 CARLOS MÁS", "#28 DERIN AKYUZ", "#32 GONZALO RODRIGUEZ", "#82 MIGUEL DOLZ"
    ]

    st.title("🏀 La Roche: Cargar Partido")
    
    # 1. SELECCIÓN DE EQUIPO
    categoria = st.selectbox(
        "¿Qué equipo juega?",
        ["Junior A (A+B)", "Junior B (Solo B)"]
    )

    # Lógica de Roster
    if "Junior A" in categoria:
        roster_disponible = junior_a_base + junior_b_base
    else:
        roster_disponible = junior_b_base

    st.divider()

    # 2. CREAR CONVOCATORIA
    st.subheader("📝 Crear Convocatoria")
    
    # Multiselect simple (el más compatible con iPad)
    convocados = st.multiselect(
        "Selecciona jugadoras en acta:",
        options=roster_disponible,
        default=roster_disponible if "Junior B" in categoria else None
    )

    # 3. RIVAL
    st.subheader("🛡️ Información del Rival")
    nombre_rival = st.text_input("Nombre del equipo rival:", value="Rival")
    
    dorsales_rival = st.text_area(
        "Dorsales rivales (ej: 4, 7, 10...)", 
        value="", 
        help="Puedes editarlos luego"
    )

    # BOTÓN DE INICIO
    if st.button("🚀 INICIAR PARTIDO", use_container_width=True):
        if not convocados:
            st.warning("Selecciona al menos una jugadora.")
        else:
            # Guardamos en la memoria de la sesión
            st.session_state['fase'] = 'partido'
            st.session_state['equipo'] = categoria
            st.session_state['convocados'] = convocados
            st.session_state['rival'] = nombre_rival
            st.session_state['dorsales_rival'] = dorsales_rival
            
            st.success("¡Configuración guardada! Pasando al campo...")
            # Aquí llamaremos a la siguiente función en el próximo paso
            st.rerun()

if __name__ == "__main__":
    main()
