import streamlit as st
import streamlit.components.v1 as components

# Forzamos una configuración que oculte lo máximo posible de la interfaz original
st.set_page_config(page_title="La Roche Scouting", layout="wide", initial_sidebar_state="collapsed")

def main():
    # Este bloque CSS intenta ocultar los mensajes de error de Streamlit que Safari muestra por error
    st.markdown("""
        <style>
            .stAlert, .stException, .element-container:has(.stException) { display: none !important; }
            header, footer, #MainMenu { visibility: hidden !important; }
            .stApp { background-color: #0f172a; }
            /* Intentamos tapar el error rojo superior si aparece */
            div[data-testid="stDecoration"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

    # App completa en HTML/JS compatible con iPad antiguo (ES5)
    html_app = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body { background: #0f172a; color: white; font-family: -apple-system, sans-serif; margin: 0; padding: 10px; }
            .screen { display: none; }
            .active { display: block; }
            .btn { 
                width: 100%; padding: 18px; margin: 5px 0; border: none; border-radius: 10px; 
                font-weight: bold; font-size: 16px; color: white; cursor: pointer;
                -webkit-appearance: none;
            }
            .btn-blue { background: #2563eb; }
            .btn-green { background: #16a34a; }
            .btn-red { background: #dc2626; }
            .btn-orange { background: #ea580c; }
            .btn-gray { background: #334155; }
            
            .grid-2 { display: table; width: 100%; border-spacing: 5px; }
            .row { display: table-row; }
            .cell { display: table-cell; width: 50%; vertical-align: top; }
            
            .player-card { 
                background: #1e293b; padding: 12px; margin-bottom: 5px; border-radius: 6px; 
                text-align: center; border: 2px solid transparent;
            }
            .selected { border-color: #2563eb; background: #1e3a8a; }
            
            .court { 
                width: 100%; aspect-ratio: 1/1.2; background: #1e293b; border: 2px solid #475569; 
                position: relative; border-radius: 10px; overflow: hidden;
            }
            .marker { position: absolute; width: 12px; height: 12px; border-radius: 50%; transform: translate(-50%, -50%); border: 1px solid white; }
            
            input { width: 100%; padding: 15px; margin: 5px 0; border-radius: 8px; border: 1px solid #334155; background: #1e293b; color: white; box-sizing: border-box; }
            #log-output { width: 100%; height: 100px; background: #000; color: #0f0; font-family: monospace; font-size: 10px; margin-top: 10px; }
        </style>
    </head>
    <body>

    <!-- 1. INICIO -->
    <div id="s1" class="screen active">
        <h2 style="text-align:center;">JUNIOR LA ROCHE</h2>
        <button class="btn btn-blue" onclick="toConv('A')">PARTIDO JUNIOR A (A+B)</button>
        <button class="btn btn-blue" onclick="toConv('B')">PARTIDO JUNIOR B</button>
    </div>

    <!-- 2. CONVOCATORIA -->
    <div id="s2" class="screen">
        <h3>CONVOCATORIA</h3>
        <div id="roster-box"></div>
        <input type="text" id="rival" placeholder="Nombre Rival">
        <button class="btn btn-green" onclick="toMatch()">EMPEZAR PARTIDO</button>
        <button class="btn btn-gray" onclick="location.reload()">ATRAS</button>
    </div>

    <!-- 3. PARTIDO -->
    <div id="s3" class="screen">
        <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:5px;">
            <span id="label-rival"></span>
            <span id="score" style="color:#60a5fa; font-weight:bold;">PTS: 0</span>
        </div>
        
        <div id="on-court-line" style="display:flex; gap:3px; margin-bottom:10px;"></div>

        <div class="grid-2">
            <div class="row">
                <div class="cell">
                    <div class="court" id="court" onclick="mapClick(event)">
                        <div style="position:absolute; width:40%; height:30%; left:30%; top:0; border:1px solid #444;"></div>
                        <div id="shots"></div>
                    </div>
                </div>
                <div class="cell">
                    <button class="btn btn-gray" style="padding:12px" onclick="stat('REB')">REB</button>
                    <button class="btn btn-gray" style="padding:12px" onclick="stat('AST')">AST</button>
                    <button class="btn btn-gray" style="padding:12px" onclick="stat('ROBO')">ROBO</button>
                    <button class="btn btn-orange" style="padding:12px" onclick="stat('PERD')">PERD</button>
                    <button class="btn btn-red" style="padding:12px" onclick="stat('FALTA')">FALTA</button>
                    <button class="btn btn-blue" style="padding:12px" onclick="stat('TL_OK')">TL ✅</button>
                    <button class="btn btn-gray" style="padding:12px" onclick="stat('TL_ERR')">TL ❌</button>
                </div>
            </div>
        </div>
        <button class="btn btn-green" style="margin-top:10px;" onclick="doSub()">CAMBIO (🔄)</button>
        <button class="btn btn-gray" onclick="exportData()">COPIAR RESULTADOS</button>
        <textarea id="log-output" readonly></textarea>
    </div>

    <!-- MODAL TIRO -->
    <div id="s-shot" class="screen" style="position:fixed; inset:0; background:rgba(0,0,0,0.95); z-index:999; padding:20px;">
        <h2 style="text-align:center;">TIRO DE <span id="shot-player"></span></h2>
        <button class="btn btn-green" style="padding:40px; margin-bottom:20px;" onclick="shot(true)">ANOTADO</button>
        <button class="btn btn-red" style="padding:40px;" onclick="shot(false)">FALLADO</button>
    </div>

    <script>
        var playersA = [{d:"03",n:"SERRA"},{d:"08",n:"MORANA"},{d:"15",n:"AMER"},{d:"18",n:"GABI"},{d:"21",n:"ALÓS"},{d:"50",n:"FERRER"},{d:"99",n:"PEPE M"}];
        var playersB = [{d:"02",n:"LUCAS M"},{d:"05",n:"ADRIAN O"},{d:"09",n:"ANDREU E"},{d:"11",n:"ALEJANDRO"},{d:"12",n:"DAVID N"},{d:"23",n:"ANTONIO P"},{d:"24",n:"CARLOS M"},{d:"28",n:"DERIN A"},{d:"32",n:"GONZALO R"},{d:"82",n:"MIGUEL D"}];
        
        var currentRoster = [];
        var convocados = [];
        var quinteto = [];
        var selectedP = null;
        var lastXY = null;
        var logs = [];
        var puntos = 0;

        function toConv(t) {
            currentRoster = (t=='A') ? playersA.concat(playersB) : playersB;
            var box = document.getElementById('roster-box');
            box.innerHTML = "";
            for(var i=0; i<currentRoster.length; i++) {
                var p = currentRoster[i];
                var d = document.createElement('div');
                d.className = 'player-card';
                d.id = "pc-" + p.d;
                d.innerHTML = "#" + p.d + " " + p.n;
                d.onclick = (function(pl, div){ return function(){ toggle(pl, div); }})(p, d);
                box.appendChild(d);
            }
            show('s2');
        }

        function toggle(p, div) {
            var idx = convocados.indexOf(p);
            if(idx > -1) { convocados.splice(idx,1); div.className = 'player-card'; }
            else { convocados.push(p); div.className = 'player-card selected'; }
        }

        function toMatch() {
            if(convocados.length < 5) { alert("Mínimo 5 jugadores"); return; }
            quinteto = convocados.slice(0, 5);
            selectedP = quinteto[0].d;
            document.getElementById('label-rival').innerText = "Vs " + document.getElementById('rival').value;
            renderQ();
            show('s3');
        }

        function renderQ() {
            var box = document.getElementById('on-court-line');
            box.innerHTML = "";
            for(var i=0; i<quinteto.length; i++) {
                var p = quinteto[i];
                var d = document.createElement('div');
                d.style.flex = "1";
                d.style.padding = "10px 2px";
                d.style.textAlign = "center";
                d.style.borderRadius = "4px";
                d.style.background = (selectedP == p.d) ? "#2563eb" : "#334155";
                d.innerHTML = "#" + p.d;
                d.onclick = (function(id){ return function(){ selectedP = id; renderQ(); }})(p.d);
                box.appendChild(d);
            }
        }

        function mapClick(e) {
            var r = document.getElementById('court').getBoundingClientRect();
            lastXY = { x: ((e.clientX - r.left)/r.width)*100, y: ((e.clientY - r.top)/r.height)*100 };
            document.getElementById('shot-player').innerText = "#" + selectedP;
            show('s-shot');
        }

        function shot(ok) {
            var val = (lastXY.y > 35) ? 2 : 3;
            if(!ok) val = 0;
            puntos += val;
            logs.push("#" + selectedP + " Tiro " + (ok?"OK":"FALLO") + " (" + (val||"") + "pts)");
            
            var m = document.createElement('div');
            m.className = 'marker';
            m.style.left = lastXY.x + "%"; m.style.top = lastXY.y + "%";
            m.style.background = ok ? "#22c55e" : "#ef4444";
            document.getElementById('shots').appendChild(m);
            
            document.getElementById('score').innerText = "PTS: " + puntos;
            updateLog();
            show('s3');
        }

        function stat(t) {
            if(t == 'TL_OK') puntos += 1;
            logs.push("#" + selectedP + " " + t);
            document.getElementById('score').innerText = "PTS: " + puntos;
            updateLog();
        }

        function doSub() {
            var bench = convocados.filter(function(p){ 
                for(var j=0; j<quinteto.length; j++) if(quinteto[j].d == p.d) return false;
                return true;
            });
            if(bench.length == 0) { alert("Banquillo vacío"); return; }
            var m = "CAMBIO: Sale #" + selectedP + ". ¿Quién entra?\\n";
            for(var i=0; i<bench.length; i++) m += (i+1) + ": #" + bench[i].d + "\\n";
            var r = prompt(m);
            if(r && bench[r-1]) {
                for(var i=0; i<quinteto.length; i++) if(quinteto[i].d == selectedP) quinteto[i] = bench[r-1];
                selectedP = bench[r-1].d;
                renderQ();
            }
        }

        function updateLog() { document.getElementById('log-output').value = logs.slice(-5).join("\\n"); }
        function show(id) {
            var ss = document.getElementsByClassName('screen');
            for(var i=0; i<ss.length; i++) ss[i].className = 'screen';
            document.getElementById(id).className = 'screen active';
        }
        function exportData() {
            var t = "RESULTADOS:\\n" + logs.join("\\n");
            document.getElementById('log-output').value = t;
            alert("Datos copiados al cuadro inferior. Cópialos manualmente para enviar.");
        }
    </script>
    </body>
    </html>
    """
    
    # El iframe de Streamlit que contiene nuestra app compatible
    components.html(html_app, height=850, scrolling=False)

if __name__ == "__main__":
    main()
