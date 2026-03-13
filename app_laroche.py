import streamlit as st
import streamlit.components.v1 as components

def main():
    # Estilos de Streamlit para limpiar la interfaz en el iPad
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp {background-color: #0f172a;}
        </style>
    """, unsafe_allow_html=True)

    # Todo el motor de la app en HTML/JS compatible con iPads antiguos
    html_code = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body { 
                background: #0f172a; color: white; font-family: sans-serif; 
                margin: 0; padding: 10px; overflow-x: hidden;
            }
            .screen { display: none; }
            .active { display: block; }
            
            /* Botones Grandes */
            .btn { 
                width: 100%; padding: 20px; margin: 5px 0; border: none; 
                border-radius: 12px; font-weight: bold; font-size: 16px; 
                cursor: pointer; color: white;
            }
            .btn-blue { background: #3b82f6; }
            .btn-green { background: #22c55e; }
            .btn-red { background: #ef4444; }
            .btn-orange { background: #f59e0b; color: black; }
            .btn-gray { background: #334155; }

            /* Grid Convocatoria */
            .roster-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
            .player-item { 
                background: #1e293b; padding: 15px; border-radius: 8px; 
                text-align: center; border: 2px solid transparent;
            }
            .selected { border-color: #3b82f6; background: #1e3a8a; }

            /* Campo de Juego */
            .court-box {
                position: relative; width: 100%; background: #1e293b; 
                border: 2px solid #475569; aspect-ratio: 1 / 1.1; margin-top: 10px;
                border-radius: 15px; overflow: hidden;
            }
            .court-line {
                position: absolute; border: 1.5px solid #64748b; pointer-events: none;
            }
            .shot-marker {
                position: absolute; width: 12px; height: 12px; border-radius: 50%;
                transform: translate(-50%, -50%); border: 1px solid white;
            }

            /* Panel de Acciones */
            .action-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
            .mini-btn { padding: 15px 5px; font-size: 12px; }
            
            .header { text-align: center; margin-bottom: 15px; border-bottom: 1px solid #334155; padding-bottom: 10px; }
            
            input, textarea { 
                width: 100%; padding: 15px; background: #1e293b; color: white; 
                border: 1px solid #334155; border-radius: 8px; margin-bottom: 10px; box-sizing: border-box;
            }
        </style>
    </head>
    <body>

    <!-- PANTALLA 1: SELECCION EQUIPO -->
    <div id="screen-start" class="screen active">
        <div class="header"><h2>CARGAR PARTIDO</h2></div>
        <button class="btn btn-blue" onclick="chooseTeam('A')">JUNIOR A (A + B)</button>
        <button class="btn btn-blue" onclick="chooseTeam('B')">JUNIOR B (Solo B)</button>
    </div>

    <!-- PANTALLA 2: CONVOCATORIA -->
    <div id="screen-conv" class="screen">
        <div class="header"><h3 id="conv-title">Convocatoria</h3></div>
        <div id="roster-list" class="roster-grid"></div>
        <div style="margin-top:20px;">
            <input type="text" id="rival-name" placeholder="Nombre Rival">
            <textarea id="rival-nums" placeholder="Dorsales Rival (4, 7, 12...)"></textarea>
            <button class="btn btn-green" onclick="startMatch()">INICIAR PARTIDO</button>
            <button class="btn btn-gray" onclick="location.reload()">Atrás</button>
        </div>
    </div>

    <!-- PANTALLA 3: CAMPO Y MÉTRICAS -->
    <div id="screen-match" class="screen">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div id="match-info" style="font-weight:bold; font-size:12px;"></div>
            <div id="global-score" style="color:#3b82f6; font-weight:bold;">PTS: 0 | FG: 0%</div>
        </div>

        <!-- Quinteto Activo -->
        <div id="on-court" style="display:grid; grid-template-columns:repeat(5, 1fr); gap:4px; margin:10px 0;"></div>

        <div style="display:grid; grid-template-columns: 1.2fr 1fr; gap:10px;">
            <!-- Campo -->
            <div class="court-box" id="court" onclick="clickCourt(event)">
                <div class="court-line" style="width:30%; height:30%; left:35%; top:0; border-top:0;"></div> <!-- Zona -->
                <div class="court-line" style="width:16%; height:16%; left:42%; top:0; border-radius:0 0 50% 50%; border-top:0;"></div> <!-- Aro -->
                <div class="court-line" style="width:80%; height:40%; left:10%; top:0; border-radius:0 0 100px 100px; border-top:0;"></div> <!-- 3P -->
                <div id="marks-layer"></div>
            </div>

            <!-- Botones Accion -->
            <div class="action-grid">
                <button class="btn btn-gray mini-btn" onclick="addStat('REB')">REB</button>
                <button class="btn btn-gray mini-btn" onclick="addStat('AST')">AST</button>
                <button class="btn btn-gray mini-btn" onclick="addStat('STL')">ROBO</button>
                <button class="btn btn-gray mini-btn" onclick="addStat('BLK')">TAP</button>
                <button class="btn btn-orange mini-btn" onclick="addStat('TOV')">PERD</button>
                <button class="btn btn-red mini-btn" onclick="addStat('FAL')">FAL</button>
                <button class="btn btn-blue mini-btn" onclick="addStat('TL_M')">TL ✅</button>
                <button class="btn btn-gray mini-btn" onclick="addStat('TL_F')">TL ❌</button>
                <button class="btn btn-green mini-btn" onclick="showSub()" style="grid-column: span 3;">CAMBIOS (🔄)</button>
            </div>
        </div>
        
        <button class="btn btn-gray" style="margin-top:10px; font-size:12px;" onclick="exportData()">EXPORTAR DATOS</button>
    </div>

    <!-- MODAL TIRO -->
    <div id="modal-shot" class="screen" style="position:fixed; inset:0; background:rgba(0,0,0,0.9); z-index:100; padding:20px;">
        <h2 style="text-align:center;">RESULTADO TIRO</h2>
        <button class="btn btn-red" onclick="saveShot(false)" style="padding:40px;">FALLADO</button>
        <button class="btn btn-green" onclick="saveShot(true)" style="padding:40px; margin-top:20px;">ANOTADO</button>
    </div>

    <script>
        var playersA = [
            {n:"03", name:"SERRA"}, {n:"08", name:"MORANA"}, {n:"15", name:"AMER"},
            {n:"18", name:"GABI"}, {n:"21", name:"ALÓS"}, {n:"50", name:"FERRER"}, {n:"99", name:"PEPE M"}
        ];
        var playersB = [
            {n:"02", name:"LUCAS M"}, {n:"05", name:"ADRIAN O"}, {n:"09", name:"ANDREU E"},
            {n:"11", name:"ALEJANDRO"}, {n:"12", name:"DAVID N"}, {n:"23", name:"ANTONIO P"},
            {n:"24", name:"CARLOS M"}, {n:"28", name:"DERIN A"}, {n:"32", name:"GONZALO R"}, {n:"82", name:"MIGUEL D"}
        ];

        var roster = [];
        var convocados = [];
        var quinteto = [];
        var activeId = null;
        var pendingShot = null;
        var stats = [];

        function chooseTeam(type) {
            roster = (type === 'A') ? playersA.concat(playersB) : playersB;
            document.getElementById('screen-start').className = 'screen';
            document.getElementById('screen-conv').className = 'screen active';
            
            var list = document.getElementById('roster-list');
            list.innerHTML = "";
            roster.forEach(function(p, i) {
                var div = document.createElement('div');
                div.className = 'player-item';
                div.innerHTML = "<b>#" + p.n + "</b><br><small>" + p.name + "</small>";
                div.onclick = function() { togglePlayer(i, div); };
                list.appendChild(div);
            });
        }

        function togglePlayer(idx, el) {
            var p = roster[idx];
            var found = convocados.indexOf(p);
            if (found > -1) {
                convocados.splice(found, 1);
                el.className = 'player-item';
            } else {
                convocados.push(p);
                el.className = 'player-item selected';
            }
        }

        function startMatch() {
            if (convocados.length < 5) { alert("Minimo 5 jugadores"); return; }
            quinteto = convocados.slice(0, 5);
            activeId = quinteto[0].n;
            
            document.getElementById('screen-conv').className = 'screen';
            document.getElementById('screen-match').className = 'screen active';
            document.getElementById('match-info').innerText = "Rival: " + document.getElementById('rival-name').value;
            renderQuinteto();
        }

        function renderQuinteto() {
            var div = document.getElementById('on-court');
            div.innerHTML = "";
            quinteto.forEach(function(p) {
                var b = document.createElement('div');
                b.className = (activeId === p.n) ? 'player-item selected' : 'player-item';
                b.style.padding = "10px 2px";
                b.innerHTML = "<b>" + p.n + "</b>";
                b.onclick = function() { activeId = p.n; renderQuinteto(); };
                div.appendChild(b);
            });
        }

        function clickCourt(e) {
            var c = document.getElementById('court');
            var r = c.getBoundingClientRect();
            pendingShot = {
                x: ((e.clientX - r.left) / r.width) * 100,
                y: ((e.clientY - r.top) / r.height) * 100
            };
            document.getElementById('modal-shot').className = 'screen active';
        }

        function saveShot(made) {
            var p = quinteto.find(function(x){ return x.n === activeId });
            var pts = (pendingShot.y > 40) ? 2 : 3;
            if(!made) pts = 0;

            stats.push({p: activeId, type: 'SHOT', made: made, pts: pts, x: pendingShot.x, y: pendingShot.y});
            
            var dot = document.createElement('div');
            dot.className = 'shot-marker';
            dot.style.left = pendingShot.x + "%";
            dot.style.top = pendingShot.y + "%";
            dot.style.background = made ? '#22c55e' : '#ef4444';
            document.getElementById('marks-layer').appendChild(dot);
            
            document.getElementById('modal-shot').className = 'screen';
            updateGlobal();
        }

        function addStat(type) {
            stats.push({p: activeId, type: type});
            updateGlobal();
            alert("Registrado: " + type + " para #" + activeId);
        }

        function updateGlobal() {
            var pts = 0, fga = 0, fgm = 0;
            stats.forEach(function(s) {
                if(s.pts) pts += s.pts;
                if(s.type === 'TL_M') pts += 1;
                if(s.type === 'SHOT') { fga++; if(s.made) fgm++; }
            });
            var pct = fga ? Math.round((fgm/fga)*100) : 0;
            document.getElementById('global-score').innerText = "PTS: " + pts + " | FG: " + pct + "%";
        }

        function showSub() {
            var salir = activeId;
            var banquillo = convocados.filter(function(p) { 
                return !quinteto.some(function(q) { return q.n === p.n });
            });
            
            if(banquillo.length === 0) { alert("No hay nadie en el banquillo"); return; }
            
            var msg = "Sustituir #" + salir + " por quién?\\n" + banquillo.map(function(p, i){ return (i+1) + ": #" + p.n }).join("\\n");
            var res = prompt(msg);
            if(res && banquillo[res-1]) {
                var idx = quinteto.findIndex(function(p){ return p.n === salir });
                quinteto[idx] = banquillo[res-1];
                activeId = quinteto[idx].n;
                renderQuinteto();
            }
        }

        function exportData() {
            var text = "ESTADISTICAS PARTIDO\\n\\n" + stats.map(function(s){ return s.p + ": " + s.type }).join("\\n");
            alert("Copia esto:\\n" + text);
        }
    </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=800, scrolling=False)

if __name__ == "__main__":
    main()
