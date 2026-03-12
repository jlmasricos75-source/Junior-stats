import streamlit as st
import streamlit.components.v1 as components

def main():
    st.set_page_config(page_title="HoopStat Pro", layout="wide")

    html_code = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            :root {
                --bg: #0f172a;
                --card: #1e293b;
                --primary: #3b82f6;
                --success: #22c55e;
                --danger: #ef4444;
                --warning: #f59e0b;
                --text: #f8fafc;
                --court-line: #94a3b8;
            }
            body { 
                background-color: var(--bg); color: var(--text); 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; padding: 10px; overflow-x: hidden;
            }
            .app-container { max-width: 600px; margin: 0 auto; display: flex; flex-direction: column; gap: 15px; }
            
            /* Stats Header */
            .header-stats {
                display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;
                background: var(--card); padding: 15px; border-radius: 15px; text-align: center;
            }
            .stat-box .val { font-size: 1.2rem; font-weight: bold; color: var(--primary); display: block; }
            .stat-box .label { font-size: 0.6rem; color: #94a3b8; text-transform: uppercase; }

            /* Court / Hoop Map */
            .court-wrapper {
                position: relative; width: 100%; background: #1e293b; 
                border-radius: 20px; border: 2px solid #334155; aspect-ratio: 1.2 / 1;
                overflow: hidden; touch-action: none;
            }
            .court-svg { position: absolute; width: 100%; height: 100%; stroke: var(--court-line); stroke-width: 1.5; fill: none; }
            .shot-marker {
                position: absolute; width: 12px; height: 12px; border-radius: 50%;
                transform: translate(-50%, -50%); border: 1.5px solid white; z-index: 10;
            }

            /* On Court Selection */
            .lineup-bar {
                display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px;
            }
            .player-pill {
                background: var(--card); padding: 10px 5px; border-radius: 10px;
                text-align: center; border: 2px solid transparent; cursor: pointer;
            }
            .player-pill.active { border-color: var(--primary); background: #1e3a8a; }
            .player-pill .num { font-weight: bold; font-size: 1rem; }

            /* Action Grid (All Metrics) */
            .metrics-grid {
                display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;
            }
            .btn-action {
                background: var(--card); border: 1px solid #334155; color: white;
                padding: 15px 5px; border-radius: 12px; font-weight: 600; font-size: 0.8rem;
                display: flex; flex-direction: column; align-items: center; gap: 5px;
                transition: transform 0.1s;
            }
            .btn-action:active { transform: scale(0.95); background: #334155; }
            .btn-action i { font-style: normal; font-size: 1.2rem; }

            /* Popups / Modals */
            .overlay {
                position: fixed; bottom: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.8); display: none; flex-direction: column; 
                justify-content: flex-end; z-index: 100;
            }
            .outcome-menu {
                background: var(--card); padding: 30px 20px; border-radius: 30px 30px 0 0;
                display: flex; gap: 15px;
            }
            .btn-outcome {
                flex: 1; padding: 20px; border-radius: 15px; border: none; 
                color: white; font-weight: bold; font-size: 1.1rem;
            }
        </style>
    </head>
    <body>
        <div class="app-container">
            <div class="header-stats">
                <div class="stat-box"><span class="val" id="total-pts">0</span><span class="label">PTS</span></div>
                <div class="stat-box"><span class="val" id="total-reb">0</span><span class="label">REB</span></div>
                <div class="stat-box"><span class="val" id="total-ast">0</span><span class="label">AST</span></div>
                <div class="stat-box"><span class="val" id="total-fg">0%</span><span class="label">FG%</span></div>
            </div>

            <div class="court-wrapper" id="court-map">
                <svg class="court-svg" viewBox="0 0 100 80">
                    <!-- Fondo de campo -->
                    <rect x="0" y="0" width="100" height="80" fill="#1e293b" />
                    <!-- Tablero y Aro -->
                    <line x1="40" y1="5" x2="60" y2="5" />
                    <circle cx="50" cy="8" r="3" />
                    <!-- Zona -->
                    <rect x="35" y="0" width="30" height="30" />
                    <circle cx="50" cy="30" r="8" />
                    <!-- Línea de 3 puntos (proporcional) -->
                    <path d="M 10 0 L 10 10 A 40 40 0 0 0 90 10 L 90 0" />
                    <!-- Medio campo -->
                    <line x1="0" y1="75" x2="100" y2="75" />
                    <circle cx="50" cy="75" r="10" />
                </svg>
                <div id="shots-layer"></div>
            </div>

            <div class="lineup-bar" id="on-court">
                <!-- Inyectado por JS -->
            </div>

            <div class="metrics-grid">
                <button class="btn-action" onclick="logMetric('reb')"><i>🏀</i>REB</button>
                <button class="btn-action" onclick="logMetric('ast')"><i>👟</i>AST</button>
                <button class="btn-action" onclick="logMetric('stl')"><i>🧤</i>ROBO</button>
                <button class="btn-action" onclick="logMetric('blk')"><i>✋</i>TAPÓN</button>
                <button class="btn-action" onclick="logMetric('tov')" style="color:var(--warning)"><i>⚠️</i>PÉRDIDA</button>
                <button class="btn-action" onclick="logMetric('fou')" style="color:var(--danger)"><i>🛑</i>FALTA</button>
            </div>
            
            <div style="text-align:center;">
                <button onclick="resetAll()" style="background:none; border:none; color:#475569; font-size:0.7rem;">REINICIAR PARTIDO</button>
            </div>
        </div>

        <div class="overlay" id="shot-overlay">
            <div class="outcome-menu">
                <button class="btn-outcome" style="background:var(--danger)" onclick="confirmShot(false)">FALLADO</button>
                <button class="btn-outcome" style="background:var(--success)" onclick="confirmShot(true)">ANOTADO</button>
            </div>
        </div>

        <script>
            let players = [
                {id: 1, num: '03', name: 'SERRA', pts:0, reb:0, ast:0, stl:0, blk:0, tov:0, fou:0, fga:0, fgm:0, on:true},
                {id: 2, num: '08', name: 'MORANA', pts:0, reb:0, ast:0, stl:0, blk:0, tov:0, fou:0, fga:0, fgm:0, on:true},
                {id: 3, num: '15', name: 'AMER', pts:0, reb:0, ast:0, stl:0, blk:0, tov:0, fou:0, fga:0, fgm:0, on:true},
                {id: 4, num: '18', name: 'GABI', pts:0, reb:0, ast:0, stl:0, blk:0, tov:0, fou:0, fga:0, fgm:0, on:true},
                {id: 5, num: '21', name: 'ALÓS', pts:0, reb:0, ast:0, stl:0, blk:0, tov:0, fou:0, fga:0, fgm:0, on:true},
            ];

            let activeId = 1;
            let pendingShot = null;

            function renderLineup() {
                const container = document.getElementById('on-court');
                container.innerHTML = '';
                players.filter(p => p.on).forEach(p => {
                    const el = document.createElement('div');
                    el.className = `player-pill ${activeId === p.id ? 'active' : ''}`;
                    el.innerHTML = `<div class="num">${p.num}</div><div style="font-size:0.5rem">${p.name}</div>`;
                    el.onclick = () => { activeId = p.id; renderLineup(); };
                    container.appendChild(el);
                });
            }

            // Click en el mapa
            document.getElementById('court-map').onclick = (e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width) * 100;
                const y = ((e.clientY - rect.top) / rect.height) * 100;
                pendingShot = { x, y };
                document.getElementById('shot-overlay').style.display = 'flex';
            };

            function confirmShot(made) {
                const p = players.find(p => p.id === activeId);
                p.fga++;
                if(made) {
                    p.fgm++;
                    p.pts += 2; // Simplificado a 2 por ahora
                }
                
                // Dibujar marcador
                const marker = document.createElement('div');
                marker.className = 'shot-marker';
                marker.style.left = pendingShot.x + '%';
                marker.style.top = pendingShot.y + '%';
                marker.style.background = made ? 'var(--success)' : 'var(--danger)';
                document.getElementById('shots-layer').appendChild(marker);
                
                closeOverlay();
                updateTotals();
            }

            function logMetric(type) {
                const p = players.find(p => p.id === activeId);
                p[type]++;
                updateTotals();
                
                // Feedback visual breve
                const btn = event.currentTarget;
                const original = btn.style.background;
                btn.style.background = "#334155";
                setTimeout(() => btn.style.background = original, 100);
            }

            function updateTotals() {
                let pts = 0, reb = 0, ast = 0, fga = 0, fgm = 0;
                players.forEach(p => {
                    pts += p.pts; reb += p.reb; ast += p.ast;
                    fga += p.fga; fgm += p.fgm;
                });
                
                document.getElementById('total-pts').innerText = pts;
                document.getElementById('total-reb').innerText = reb;
                document.getElementById('total-ast').innerText = ast;
                document.getElementById('total-fg').innerText = fga === 0 ? '0%' : Math.round((fgm/fga)*100) + '%';
            }

            function closeOverlay() {
                document.getElementById('shot-overlay').style.display = 'none';
            }

            function resetAll() {
                if(confirm("¿Borrar todo?")) location.reload();
            }

            renderLineup();
        </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=800, scrolling=False)

if __name__ == "__main__":
    main()
