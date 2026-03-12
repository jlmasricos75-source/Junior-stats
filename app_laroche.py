import streamlit as st
import streamlit.components.v1 as components

# Forzar configuración de página
st.set_page_config(page_title="La Roche Stats", layout="centered")

def main():
    st.title("🏀 La Roche Scouting")
    
    # El contenido HTML se define como una cadena simple para evitar errores de sintaxis en Python
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { 
                background-color: #0e1117; 
                color: white; 
                font-family: sans-serif; 
                text-align: center;
            }
            .roster {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 10px;
                margin-bottom: 20px;
            }
            button {
                padding: 10px;
                cursor: pointer;
                border-radius: 5px;
                border: none;
            }
            .player-btn { background: #262730; color: white; }
            .player-btn.active { background: #ff4b4b; }
            
            .court {
                width: 100%;
                max-width: 400px;
                aspect-ratio: 1/1;
                background: #1e1e1e;
                border: 2px solid #555;
                position: relative;
                margin: 0 auto;
                touch-action: none;
            }
            .rim {
                position: absolute;
                top: 15%; left: 50%;
                width: 20px; height: 20px;
                border: 2px solid orange;
                border-radius: 50%;
                transform: translateX(-50%);
            }
            .marker {
                position: absolute;
                width: 12px; height: 12px;
                border-radius: 50%;
                transform: translate(-50%, -50%);
            }
            .controls { margin-top: 20px; display: none; }
            .btn-make { background: #28a745; color: white; padding: 15px; margin-right: 10px; }
            .btn-miss { background: #dc3545; color: white; padding: 15px; }
        </style>
    </head>
    <body>
        <div class="roster" id="btns"></div>
        <div class="court" id="court"><div class="rim"></div></div>
        <div id="msg">Selecciona un jugador</div>
        <div class="controls" id="ctrls">
            <button class="btn-make" onclick="save(true)">ANOTADA</button>
            <button class="btn-miss" onclick="save(false)">FALLADA</button>
        </div>

        <script>
            const players = ["3.SERRA", "8.MORANA", "15.AMER", "18.GABI", "21.ALÓS", "50.FERRER", "99.PEPE", "12.DAV"];
            let selected = null;
            let lastPos = {x:0, y:0};

            const container = document.getElementById('btns');
            players.forEach(p => {
                const b = document.createElement('button');
                b.className = 'player-btn';
                b.innerText = p;
                b.onclick = () => {
                    document.querySelectorAll('.player-btn').forEach(x => x.classList.remove('active'));
                    b.classList.add('active');
                    selected = p;
                    document.getElementById('msg').innerText = "Marcando para " + p;
                };
                container.appendChild(b);
            });

            const court = document.getElementById('court');
            court.onclick = (e) => {
                if(!selected) return alert("Elige jugador");
                const r = court.getBoundingClientRect();
                lastPos.x = ((e.clientX - r.left) / r.width) * 100;
                lastPos.y = ((e.clientY - r.top) / r.height) * 100;
                document.getElementById('ctrls').style.display = 'block';
            };

            function save(hit) {
                const m = document.createElement('div');
                m.className = 'marker';
                m.style.left = lastPos.x + "%";
                m.style.top = lastPos.y + "%";
                m.style.background = hit ? "#28a745" : "#dc3545";
                court.appendChild(m);
                document.getElementById('ctrls').style.display = 'none';
                console.log(selected, lastPos.x, lastPos.y, hit);
            }
        </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=700)

if __name__ == "__main__":
    main()
