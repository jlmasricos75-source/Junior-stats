<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scouting Junior Pro - La Roche</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0f172a; color: white; user-select: none; font-family: sans-serif; }
        .court-container { position: relative; width: 100%; max-width: 500px; margin: 0 auto; aspect-ratio: 15/14; }
        .btn-action { transition: all 0.2s; border: 1px solid rgba(255,255,255,0.1); }
        .btn-action:active { transform: scale(0.95); filter: brightness(1.2); }
        .stats-panel { height: 200px; overflow-y: auto; background: rgba(0,0,0,0.3); border-radius: 8px; font-family: monospace; }
        .shot-mark { position: absolute; width: 12px; height: 12px; border-radius: 50%; transform: translate(-50%, -50%); pointer-events: none; }
        .pt-minus-btn { background: #991b1b; color: white; } /* Rojo oscuro para PT -8 */
    </style>
</head>
<body class="p-2">

    <div class="max-w-4xl mx-auto">
        <!-- Header -->
        <div class="flex justify-between items-center mb-4 bg-slate-800 p-3 rounded-xl border border-slate-700">
            <h1 class="text-xl font-bold text-orange-500">LA ROCHE <span class="text-white text-sm font-normal">v2.1</span></h1>
            <div class="text-right">
                <div id="active-player" class="text-xs text-slate-400">SELECCIONA JUGADOR</div>
                <div id="current-selection" class="font-bold text-lg text-white">-</div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Columna Izquierda: Jugadores y Acciones -->
            <div>
                <div class="grid grid-cols-4 gap-2 mb-4" id="roster-grid">
                    <!-- Jugadores dinámicos -->
                </div>

                <div class="grid grid-cols-2 gap-2">
                    <button onclick="recordAction('Inversión')" class="btn-action bg-blue-600 h-16 rounded-lg font-bold text-lg">INVERSIÓN</button>
                    <button onclick="recordAction('PT')" class="btn-action bg-green-600 h-16 rounded-lg font-bold text-lg">PT (Paint Touch)</button>
                    <button onclick="recordAction('PT -8')" class="btn-action pt-minus-btn h-16 rounded-lg font-bold text-lg">PT -8</button>
                    <button onclick="undoLast()" class="btn-action bg-slate-700 h-16 rounded-lg font-bold">DESHACER</button>
                </div>
                
                <div class="mt-4 stats-panel p-2 text-xs" id="log">
                    <div class="text-slate-500 italic">Esperando acciones...</div>
                </div>
            </div>

            <!-- Columna Derecha: Campo Interactivo -->
            <div class="flex flex-col items-center">
                <div class="court-container bg-slate-900 rounded-xl overflow-hidden border-2 border-slate-700" id="court">
                    <!-- SVG del Medio Campo de Baloncesto -->
                    <svg viewBox="0 0 150 140" class="w-full h-full" onclick="handleShot(event)">
                        <!-- Líneas del campo -->
                        <rect x="0" y="0" width="150" height="140" fill="none" stroke="#64748b" stroke-width="2"/>
                        <!-- Triple -->
                        <path d="M 0 42 L 20 42 A 65 65 0 0 1 130 42 L 150 42" fill="none" stroke="#64748b" stroke-width="2"/>
                        <!-- Zona -->
                        <rect x="51" y="0" width="48" height="58" fill="none" stroke="#64748b" stroke-width="2"/>
                        <!-- Botella -->
                        <circle cx="75" cy="58" r="18" fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="2"/>
                        <!-- Aro y Tablero -->
                        <line x1="65" y1="4" x2="85" y2="4" stroke="white" stroke-width="2"/>
                        <circle cx="75" cy="10" r="4" fill="none" stroke="#f97316" stroke-width="2"/>
                    </svg>
                    <div id="marks-container"></div>
                </div>
                
                <div class="grid grid-cols-2 gap-2 w-full mt-4">
                    <button id="btn-make" onclick="setShotResult(true)" class="btn-action bg-green-500 py-4 rounded-lg font-black text-xl shadow-lg opacity-50" disabled>ENCESTADA</button>
                    <button id="btn-miss" onclick="setShotResult(false)" class="btn-action bg-red-500 py-4 rounded-lg font-black text-xl shadow-lg opacity-50" disabled>FALLADA</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const JUGADORES = ["3.SERRA", "8.MORANA", "15.AMER", "18.GABI", "21.ALÓS", "50.FERRER", "99.PEPE", "12.DAV"];
        let selectedPlayer = null;
        let pendingShot = null;
        let actions = [];

        function initRoster() {
            const grid = document.getElementById('roster-grid');
            JUGADORES.forEach(p => {
                const btn = document.createElement('button');
                btn.className = "btn-action bg-slate-800 p-3 rounded text-sm font-bold border-b-4 border-transparent hover:bg-slate-700";
                btn.innerText = p;
                btn.onclick = () => selectPlayer(p, btn);
                grid.appendChild(btn);
            });
        }

        function selectPlayer(name, btn) {
            document.querySelectorAll('#roster-grid button').forEach(b => b.classList.remove('border-orange-500', 'bg-slate-700'));
            selectedPlayer = name;
            btn.classList.add('border-orange-500', 'bg-slate-700');
            document.getElementById('current-selection').innerText = name;
        }

        function recordAction(type) {
            if (!selectedPlayer) return alert("Selecciona un jugador primero");
            const entry = { player: selectedPlayer, type: type, time: new Date().toLocaleTimeString() };
            actions.unshift(entry);
            updateLog();
        }

        function handleShot(e) {
            if (!selectedPlayer) return alert("Selecciona un jugador primero");
            
            const rect = e.currentTarget.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;

            pendingShot = { x, y };
            
            // Habilitar botones de resultado
            document.getElementById('btn-make').disabled = false;
            document.getElementById('btn-make').classList.remove('opacity-50');
            document.getElementById('btn-miss').disabled = false;
            document.getElementById('btn-miss').classList.remove('opacity-50');

            // Feedback visual temporal
            tempMark(x, y);
        }

        function tempMark(x, y) {
            const container = document.getElementById('marks-container');
            const mark = document.createElement('div');
            mark.className = "shot-mark bg-white border-2 border-black animate-ping";
            mark.style.left = x + "%";
            mark.style.top = y + "%";
            container.innerHTML = ""; // Solo permitimos un tiro pendiente
            container.appendChild(mark);
        }

        function setShotResult(made) {
            if (!pendingShot) return;

            const type = made ? "TIRO ANOTADO" : "TIRO FALLADO";
            const color = made ? "bg-green-400" : "bg-red-500";
            
            const entry = { 
                player: selectedPlayer, 
                type: type, 
                x: pendingShot.x, 
                y: pendingShot.y,
                color: color,
                time: new Date().toLocaleTimeString() 
            };
            
            actions.unshift(entry);
            renderAllMarks();
            updateLog();

            // Reset
            pendingShot = null;
            document.getElementById('btn-make').disabled = true;
            document.getElementById('btn-make').classList.add('opacity-50');
            document.getElementById('btn-miss').disabled = true;
            document.getElementById('btn-miss').classList.add('opacity-50');
        }

        function renderAllMarks() {
            const container = document.getElementById('marks-container');
            container.innerHTML = "";
            actions.forEach(a => {
                if (a.x !== undefined) {
                    const mark = document.createElement('div');
                    mark.className = `shot-mark ${a.color} border border-white`;
                    mark.style.left = a.x + "%";
                    mark.style.top = a.y + "%";
                    container.appendChild(mark);
                }
            });
        }

        function updateLog() {
            const log = document.getElementById('log');
            log.innerHTML = actions.map(a => `
                <div class="mb-1 border-b border-slate-700 pb-1">
                    <span class="text-slate-500">[${a.time}]</span> 
                    <span class="text-orange-400 font-bold">${a.player}</span>: 
                    <span class="${a.type.includes('ANOTADO') ? 'text-green-400' : (a.type.includes('PT -8') ? 'text-red-400' : 'text-white')}">${a.type}</span>
                </div>
            `).join('');
        }

        function undoLast() {
            actions.shift();
            renderAllMarks();
            updateLog();
        }

        window.onload = initRoster;
    </script>
</body>
</html>
