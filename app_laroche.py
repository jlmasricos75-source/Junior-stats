<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>La Roche Scouting Pro v3</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        :root {
            --bg-dark: #0f172a;
            --accent: #f97316;
        }
        body { 
            background-color: var(--bg-dark); 
            color: white; 
            user-select: none; 
            font-family: 'Inter', system-ui, sans-serif;
            touch-action: manipulation;
        }
        .court-container { 
            position: relative; 
            width: 100%; 
            max-width: 600px; 
            margin: 0 auto; 
            aspect-ratio: 15 / 14; 
            background: #1e293b;
            border-radius: 16px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
            border: 2px solid #334155;
        }
        .btn-action { 
            transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1); 
            border-bottom: 4px solid rgba(0,0,0,0.4);
        }
        .btn-action:active { 
            transform: scale(0.96) translateY(2px); 
            border-bottom-width: 0px;
        }
        .player-card {
            position: relative;
            overflow: hidden;
        }
        .player-card.active {
            background: var(--accent) !important;
            border-color: #fb923c;
            box-shadow: 0 0 15px rgba(249, 115, 22, 0.4);
        }
        .stat-badge {
            position: absolute;
            top: 2px;
            right: 2px;
            font-size: 0.65rem;
            background: rgba(0,0,0,0.5);
            padding: 1px 4px;
            border-radius: 4px;
        }
        .shot-mark { 
            position: absolute; 
            width: 16px; 
            height: 16px; 
            border-radius: 50%; 
            transform: translate(-50%, -50%); 
            pointer-events: none;
            border: 2px solid white;
            z-index: 10;
        }
        .stats-scroll {
            scrollbar-width: thin;
            scrollbar-color: #334155 transparent;
        }
    </style>
</head>
<body class="p-2 md:p-4">

    <div class="max-w-6xl mx-auto">
        <!-- Header Inteligente -->
        <header class="flex flex-wrap justify-between items-center mb-4 bg-slate-800/50 p-4 rounded-2xl backdrop-blur-md border border-slate-700">
            <div class="flex items-center gap-3">
                <div class="bg-orange-600 p-2 rounded-lg shadow-lg">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                </div>
                <div>
                    <h1 class="text-xl font-black tracking-tight">LA ROCHE <span class="text-orange-500">PRO</span></h1>
                    <div id="active-player-name" class="text-xs font-bold text-slate-400 uppercase tracking-widest italic">Esperando selección...</div>
                </div>
            </div>
            
            <div class="flex gap-2">
                <button onclick="copySummary()" class="bg-slate-700 hover:bg-slate-600 p-2 rounded-lg text-xs font-bold flex items-center gap-1 transition-colors">
                    <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012-2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" /></svg>
                    RESUMEN
                </button>
                <button onclick="undoLast()" class="bg-red-900/40 text-red-400 p-2 rounded-lg text-xs font-bold border border-red-900/50">DESHACER</button>
            </div>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
            
            <!-- SECCIÓN IZQUIERDA: JUGADORES Y LOGS -->
            <div class="lg:col-span-4 space-y-4">
                <div class="bg-slate-900/80 p-3 rounded-2xl border border-slate-800">
                    <h3 class="text-[10px] font-bold text-slate-500 mb-2 uppercase tracking-widest">Roster Activo</h3>
                    <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-2 gap-2" id="roster">
                        <!-- JS inyecta jugadores aquí -->
                    </div>
                </div>

                <div class="bg-slate-900/80 p-3 rounded-2xl border border-slate-800 flex flex-col h-[280px]">
                    <h3 class="text-[10px] font-bold text-slate-500 mb-2 uppercase tracking-widest">Historial de Juego</h3>
                    <div class="stats-scroll flex-1 overflow-y-auto space-y-1 pr-1" id="log-content">
                        <div class="text-slate-600 text-xs text-center mt-10 italic">Inicia el scouting...</div>
                    </div>
                </div>
            </div>

            <!-- SECCIÓN CENTRAL: CAMPO -->
            <div class="lg:col-span-5 flex flex-col items-center gap-4">
                <div class="court-container" id="court-area" onclick="handleCourtClick(event)">
                    <svg viewBox="0 0 150 140" class="w-full h-full opacity-80">
                        <rect width="150" height="140" fill="#1e293b" />
                        <path d="M 0 42 L 15 42 A 65 65 0 0 1 135 42 L 150 42" fill="none" stroke="#475569" stroke-width="2"/>
                        <rect x="51" y="0" width="48" height="58" fill="#334155" opacity="0.3" />
                        <rect x="51" y="0" width="48" height="58" fill="none" stroke="#64748b" stroke-width="1.5"/>
                        <circle cx="75" cy="58" r="18" fill="none" stroke="#475569" stroke-width="1" stroke-dasharray="4"/>
                        <circle cx="75" cy="11" r="5" fill="none" stroke="#f97316" stroke-width="3"/>
                        <line x1="60" y1="5" x2="90" y2="5" stroke="white" stroke-width="2"/>
                    </svg>
                    <div id="marks-layer"></div>
                    <div id="tap-feedback" class="absolute pointer-events-none hidden bg-white/20 rounded-full w-20 h-20 -translate-x-1/2 -translate-y-1/2 animate-ping"></div>
                </div>

                <!-- Botones de Acción Instantánea -->
                <div class="grid grid-cols-2 gap-3 w-full">
                    <button id="btn-make" onclick="confirmShot(true)" class="btn-action bg-emerald-500 h-20 rounded-2xl font-black text-2xl shadow-lg opacity-30 pointer-events-none">ANOTADA</button>
                    <button id="btn-miss" onclick="confirmShot(false)" class="btn-action bg-rose-600 h-20 rounded-2xl font-black text-2xl shadow-lg opacity-30 pointer-events-none">FALLADA</button>
                </div>
            </div>

            <!-- SECCIÓN DERECHA: TÁCTICA -->
            <div class="lg:col-span-3 space-y-3">
                <div class="bg-slate-800 p-4 rounded-2xl border border-slate-700 space-y-3 shadow-xl">
                    <h3 class="text-center text-[10px] font-black text-slate-400 uppercase tracking-widest">Acciones de Equipo</h3>
                    <button onclick="recordAction('INVERSIÓN', 'bg-blue-600')" class="btn-action w-full bg-blue-600 h-16 rounded-xl font-bold flex items-center justify-center gap-2">
                        <span class="text-xl">🔄</span> INVERSIÓN
                    </button>
                    <button onclick="recordAction('PT (Paint Touch)', 'bg-emerald-600')" class="btn-action w-full bg-emerald-600 h-16 rounded-xl font-bold flex items-center justify-center gap-2">
                        <span class="text-xl">🏀</span> PAINT TOUCH
                    </button>
                    <button onclick="recordAction('PT -8', 'bg-red-700')" class="btn-action w-full bg-red-700 h-16 rounded-xl font-bold flex items-center justify-center gap-2">
                        <span class="text-xl">⚠️</span> PT -8 SEG
                    </button>
                </div>
                
                <!-- Quick Stats -->
                <div class="bg-slate-900/50 p-4 rounded-2xl border border-slate-800">
                    <div class="text-[10px] font-bold text-slate-500 mb-2 uppercase tracking-widest">Efectividad Total</div>
                    <div id="total-perc" class="text-4xl font-black text-orange-500">0%</div>
                    <div id="total-count" class="text-xs text-slate-400">0/0 Tiros de campo</div>
                </div>
            </div>

        </div>
    </div>

    <!-- Notificación emergente -->
    <div id="toast" class="fixed bottom-10 left-1/2 -translate-x-1/2 bg-orange-600 text-white px-6 py-3 rounded-full font-bold shadow-2xl transition-all opacity-0 pointer-events-none translate-y-10 z-50"></div>

    <script>
        const JUGADORES = ["3.SERRA", "8.MORANA", "15.AMER", "18.GABI", "21.ALÓS", "50.FERRER", "99.PEPE", "12.DAV"];
        let selectedPlayer = null;
        let pendingShot = null;
        let actions = [];

        function init() {
            const roster = document.getElementById('roster');
            JUGADORES.forEach(name => {
                const btn = document.createElement('button');
                btn.id = `player-${name.split('.')[0]}`;
                btn.className = "player-card btn-action bg-slate-800 p-3 h-16 rounded-xl text-sm font-black border border-slate-700 flex flex-col items-center justify-center";
                btn.innerHTML = `
                    <span class="stat-badge" id="badge-${name}">0</span>
                    ${name}
                `;
                btn.onclick = () => selectPlayer(name, btn);
                roster.appendChild(btn);
            });
            updateStatsUI();
        }

        function selectPlayer(name, element) {
            document.querySelectorAll('.player-card').forEach(b => b.classList.remove('active'));
            element.classList.add('active');
            selectedPlayer = name;
            document.getElementById('active-player-name').innerText = `Scouting: ${name}`;
            renderMarks(); // Filtrado inteligente
        }

        function recordAction(label, colorClass) {
            if (!selectedPlayer) return showToast("⚠️ SELECCIONA UN JUGADOR");
            
            const action = {
                id: Date.now(),
                player: selectedPlayer,
                type: label,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '1-digit' }),
                isShot: false
            };
            
            actions.unshift(action);
            updateStatsUI();
            showToast(`${label} registrada`);
        }

        function handleCourtClick(e) {
            if (!selectedPlayer) return showToast("⚠️ ELIGE JUGADOR PRIMERO");

            const rect = document.getElementById('court-area').getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;

            // Feedback visual del tap
            const feedback = document.getElementById('tap-feedback');
            feedback.style.left = x + "%";
            feedback.style.top = y + "%";
            feedback.classList.remove('hidden');
            setTimeout(() => feedback.classList.add('hidden'), 400);

            pendingShot = { x, y };
            
            // Activar botones de confirmación
            const btnMake = document.getElementById('btn-make');
            const btnMiss = document.getElementById('btn-miss');
            [btnMake, btnMiss].forEach(b => {
                b.classList.remove('opacity-30', 'pointer-events-none');
            });

            renderMarks();
        }

        function confirmShot(made) {
            if (!pendingShot || !selectedPlayer) return;

            const action = {
                id: Date.now(),
                player: selectedPlayer,
                type: made ? "CANASTA" : "FALLO",
                x: pendingShot.x,
                y: pendingShot.y,
                made: made,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                isShot: true
            };

            actions.unshift(action);
            pendingShot = null;
            
            // Desactivar botones
            const btnMake = document.getElementById('btn-make');
            const btnMiss = document.getElementById('btn-miss');
            [btnMake, btnMiss].forEach(b => {
                b.classList.add('opacity-30', 'pointer-events-none');
            });

            updateStatsUI();
        }

        function updateStatsUI() {
            renderMarks();
            
            // Actualizar Log
            const log = document.getElementById('log-content');
            if (actions.length === 0) {
                log.innerHTML = '<div class="text-slate-600 text-xs text-center mt-10 italic">Inicia el scouting...</div>';
            } else {
                log.innerHTML = actions.map(a => `
                    <div class="flex justify-between items-center bg-slate-800/40 px-3 py-2 rounded-lg border-l-4 ${a.made ? 'border-green-500' : (a.type === 'FALLO' ? 'border-red-500' : 'border-blue-500')}">
                        <div class="flex flex-col">
                            <span class="text-[9px] text-slate-500">${a.time}</span>
                            <span class="text-xs font-bold text-slate-200">${a.player}</span>
                        </div>
                        <span class="text-xs font-black uppercase ${a.type === 'PT -8' ? 'text-red-400' : ''}">${a.type}</span>
                    </div>
                `).join('');
            }

            // Actualizar Badges de Jugadores
            JUGADORES.forEach(name => {
                const count = actions.filter(a => a.player === name && (a.type === 'PT (Paint Touch)' || a.type === 'INVERSIÓN')).length;
                const badge = document.getElementById(`badge-${name}`);
                if (badge) badge.innerText = count;
            });

            // Stats Globales
            const shots = actions.filter(a => a.isShot);
            const total = shots.length;
            const makes = shots.filter(a => a.made).length;
            const perc = total > 0 ? Math.round((makes / total) * 100) : 0;
            
            document.getElementById('total-perc').innerText = `${perc}%`;
            document.getElementById('total-count').innerText = `${makes}/${total} Tiros de campo`;
        }

        function renderMarks() {
            const container = document.getElementById('marks-layer');
            container.innerHTML = "";

            actions.forEach(a => {
                if (a.isShot) {
                    // Solo mostrar tiros del jugador seleccionado (o todos si no hay ninguno)
                    const isFocus = !selectedPlayer || a.player === selectedPlayer;
                    
                    const mark = document.createElement('div');
                    mark.className = `shot-mark transition-opacity duration-300 ${a.made ? 'bg-green-400' : 'bg-red-500'}`;
                    mark.style.left = a.x + "%";
                    mark.style.top = a.y + "%";
                    mark.style.opacity = isFocus ? "1" : "0.15";
                    container.appendChild(mark);
                }
            });

            if (pendingShot) {
                const pMark = document.createElement('div');
                pMark.className = "shot-mark bg-white animate-pulse ring-4 ring-orange-500/50";
                pMark.style.left = pendingShot.x + "%";
                pMark.style.top = pendingShot.y + "%";
                container.appendChild(pMark);
            }
        }

        function undoLast() {
            if (actions.length > 0) {
                actions.shift();
                updateStatsUI();
                showToast("🔙 ÚLTIMA ACCIÓN ELIMINADA");
            }
        }

        function showToast(msg) {
            const toast = document.getElementById('toast');
            toast.innerText = msg;
            toast.classList.replace('opacity-0', 'opacity-100');
            toast.classList.replace('translate-y-10', 'translate-y-0');
            setTimeout(() => {
                toast.classList.replace('opacity-100', 'opacity-0');
                toast.classList.replace('translate-y-0', 'translate-y-10');
            }, 2000);
        }

        function copySummary() {
            let summary = `🏀 RESUMEN SCOUTING LA ROCHE\n`;
            JUGADORES.forEach(p => {
                const pActions = actions.filter(a => a.player === p);
                const shots = pActions.filter(a => a.isShot);
                const makes = shots.filter(a => a.made).length;
                const pt = pActions.filter(a => a.type.includes('PT')).length;
                if(pActions.length > 0) {
                    summary += `\n${p}: ${makes}/${shots.length} FG | ${pt} PT`;
                }
            });
            
            const dummy = document.createElement("textarea");
            document.body.appendChild(dummy);
            dummy.value = summary;
            dummy.select();
            document.execCommand("copy");
            document.body.removeChild(dummy);
            showToast("📋 RESUMEN COPIADO");
        }

        window.onload = init;
    </script>
</body>
</html>
