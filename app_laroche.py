import streamlit as st

# Configuración de página
st.set_page_config(page_title="La Roche Scouting - Inicio", layout="wide")

def main():
    # --- BASE DE DATOS DE JUGADORES ---
    junior_a_base = [
        {"dorsal": "03", "nombre": "SERRA"},
        {"dorsal": "08", "nombre": "MORANA"},
        {"dorsal": "15", "nombre": "AMER"},
        {"dorsal": "18", "nombre": "GABI"},
        {"dorsal": "21", "nombre": "ALÓS"},
        {"dorsal": "50", "nombre": "FERRER"},
        {"dorsal": "99", "nombre": "PEPE MÁS"},
    ]
    
    junior_b_base = [
        {"dorsal": "02", "nombre": "LUCAS MÁS"},
        {"dorsal": "05", "nombre": "ADRIAN OJEDA"},
        {"dorsal": "09", "nombre": "ANDREU ESTELLÉS"},
        {"dorsal": "11", "nombre": "ALEJANDRO PELLICER"},
        {"dorsal": "12", "nombre": "DAVID NAVÍO"},
        {"dorsal": "23", "nombre": "ANTONIO PERANDRÉS"},
        {"dorsal": "24", "nombre": "CARLOS MÁS"},
        {"dorsal": "28", "nombre": "DERIN AKYUZ"},
        {"dorsal": "32", "nombre": "GONZALO RODRIGUEZ"},
        {"dorsal": "82", "nombre": "MIGUEL DOLZ"},
    ]

    st.title("🏀 La Roche Scouting - Cargar Partido")
    st.markdown("---")

    # --- BLOQUE 1: SELECCIÓN DE EQUIPO ---
    st.subheader("1. Selección de Equipo")
    categoria = st.radio(
        "¿Qué equipo juega hoy?",
        ["Junior A", "Junior B"],
        horizontal=True
    )

    # Lógica de Roster disponible
    if categoria == "Junior A":
        # Junior A + Junior B (Muchos doblan)
        roster_disponible = junior_a_base + junior_b_base
        info_msg = "Se muestran jugadores del A y del B (Doblaje permitido)."
    else:
        # Solo Junior B
        roster_disponible = junior_b_base
        info_msg = "Se muestran únicamente los 10 jugadores del Junior B."

    st.info(info_msg)

    # --- BLOQUE 2: CREAR CONVOCATORIA ---
    st.markdown("---")
    st.subheader("2. Crear Convocatoria")
    
    col_izq, col_der = st.columns([2, 1])

    with col_izq:
        st.write("**Selecciona los jugadores convocados:**")
        # Generamos etiquetas para el multiselect
        opciones_jugadores = [f"#{j['dorsal']} - {j['nombre']}" for j in roster_disponible]
        convocados = st.multiselect(
            "Jugadores en acta:",
            options=opciones_jugadores,
            default=opciones_jugadores if categoria == "Junior B" else None
        )
        
    with col_der:
        st.write("**Información del Rival:**")
        nombre_rival = st.text_input("Nombre del Equipo Rival:", placeholder="Ej. Valencia Basket")
        
        # Gestión de dorsales rivales (Abierta)
        st.write("Dorsales rivales (separados por comas):")
        dorsales_rival_raw = st.text_area("Ej: 4, 7, 12, 15, 22...", value="", height=68)
        st.caption("Puedes añadir o quitar dorsales incluso durante el partido.")

    # --- BOTÓN DE INICIO ---
    st.markdown("---")
    if st.button("🚀 INICIAR PARTIDO Y SELECCIONAR QUINTETO", use_container_width=True):
        if not convocados:
            st.error("Debes seleccionar al menos un jugador para la convocatoria.")
        elif not nombre_rival:
            st.warning("Por favor, introduce el nombre del rival.")
        else:
            # Aquí guardaríamos en sesión y pasaríamos a la siguiente pantalla
            st.session_state['partido_activo'] = True
            st.session_state['convocados'] = convocados
            st.session_state['rival'] = nombre_rival
            st.session_state['dorsales_rival'] = [d.strip() for d in dorsales_rival_raw.split(",") if d.strip()]
            
            st.success(f"Partido configurado: La Roche {categoria} vs {nombre_rival}")
            st.balloons()

if __name__ == "__main__":
    main()
