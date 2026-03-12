<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Scouting ADN - Edición iPad</title>
    <style>
        :root {
            --primary: #0047ab;
            --bg: #f4f7f6;
            --text: #333;
            --white: #ffffff;
            --shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        * {
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        body {
            margin: 0;
            background-color: var(--bg);
            color: var(--text);
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }

        header {
            background: var(--primary);
            color: white;
            padding: 1rem;
            text-align: center;
            font-weight: bold;
            box-shadow: var(--shadow);
            z-index: 10;
        }

        .container {
            flex: 1;
            display: grid;
            grid-template-columns: 1fr 300px;
            gap: 10px;
            padding: 10px;
            overflow: hidden;
        }

        /* Si el iPad está en vertical */
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
                grid-template-rows: 1fr 200px;
            }
        }

        .court-area {
            background: var(--white);
            border-radius: 12px;
            box-shadow: var(--shadow);
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }

        #court-svg {
            width: 100%;
            height: 100%;
            max-width: 600px;
            touch-action: none;
        }

        .stats-area {
            background: var(--white);
            border-radius: 12px;
            box-shadow: var(--shadow);
            padding: 1rem;
            overflow-y: auto;
        }

        .action-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 1rem;
        }

        button {
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: opacity 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
        }

        button:active {
            opacity: 0.7;
            transform: scale(0.98);
        }

        .btn-success { background: #28a745; color: white; }
        .btn-fail { background: #dc3545; color: white; }
        .btn-undo { background: #6c757d; color: white; grid-column: span 2; }

        .log-item {
            padding: 8px;
            border-bottom: 1px solid #eee;
            font-size: 0.9rem;
            display: flex;
            justify-content: space-between;
        }

        .error-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255,255,255,0.9);
            z-index: 100;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 2rem;
        }
    </style>
</head>
<body>

<header>SCOUTING ADN - MODO IPAD</header>

<div class="container">
    <div class="court-area">
        <!-- SVG de Cancha de Baloncesto (Media Cancha para simplificar en iPad) -->
        <svg id="court-svg" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
            <!-- Rectángulo exterior -->
            <rect x="5" y="5" width="90" height="90" fill="none" stroke="#ccc" stroke-width="1" />
            <!-- Zona (Llave) -->
            <rect x="35" y="5" width="30" height="40" fill="#f0f0f0" stroke="#ccc" stroke-width="1" />
            <!-- Triple -->
            <path d="M 5 45 A 45 45 0 0 0 95 45" fill="none" stroke="#ccc" stroke-width="1" />
            <!-- Canasta -->
            <circle cx="50" cy="15" r="3" fill="none" stroke="#333" stroke-width="1" />
            <circle id="cursor" cx="-10" cy="-10" r="4" fill="var(--primary)" fill-opacity="0.6" />
        </svg>
    </div>

    <div class="stats-area">
        <h3>Acciones</h3>
        <p id="coord-text" style="font-size: 0.8rem; color: #666;">Toca la cancha para marcar posición</p>
        
        <div class="action-grid">
            <button class="btn-success" onclick="logAction('Canasta 2pt')">✅ CANASTA</button>
            <button class="btn-fail" onclick="logAction('Fallo 2pt')">❌ FALLO</button>
            <button class="btn-success" onclick="logAction('Triple OK')" style="background: #1a5a2a;">🏀 TRIPLE</button>
            <button class="btn-fail" onclick="logAction('Triple Fallo')" style="background: #8b0000;">🚫 T. FALLO</button>
            <button class="btn-undo" onclick="undo()">DESHACER ÚLTIMO</button>
        </div>

        <h4 style="margin-top: 2rem; border-bottom: 2px solid var(--primary);">Registro</h4>
        <div id="log-container"></div>
    </div>
</div>

<div id="error-screen" class="error-overlay">
    <h2>Algo ha fallado</h2>
    <p>La aplicación ha tenido un problema de carga en este dispositivo.</p>
    <button onclick="location.reload()" style="background: var(--primary); color: white;">Recargar aplicación</button>
</div>

<script>
    let lastCoords = { x: 0, y: 0 };
    let log = [];

    // Capturar clics/toques en el SVG
    const svg = document.getElementById('court-svg');
    const cursor = document.getElementById('cursor');
    const coordText = document.getElementById('coord-text');
    const logContainer = document.getElementById('log-container');

    svg.addEventListener('click', (e) => {
        updateCoords(e);
    });

    svg.addEventListener('touchstart', (e) => {
        const touch = e.touches[0];
        updateCoords(touch);
    }, {passive: true});

    function updateCoords(eventSource) {
        const pt = svg.createSVGPoint();
        pt.x = eventSource.clientX || eventSource.pageX;
        pt.y = eventSource.clientY || eventSource.pageY;
        
        const cursorPoint = pt.matrixTransform(svg.getScreenCTM().inverse());
        
        lastCoords.x = Math.round(cursorPoint.x);
        lastCoords.y = Math.round(cursorPoint.y);
        
        cursor.setAttribute('cx', lastCoords.x);
        cursor.setAttribute('cy', lastCoords.y);
        coordText.innerText = `Posición marcada: X:${lastCoords.x} Y:${lastCoords.y}`;
    }

    function logAction(type) {
        if (lastCoords.x === 0) {
            alert("Primero toca la zona de la cancha donde ha ocurrido la acción");
            return;
        }

        const entry = {
            time: new Date().toLocaleTimeString().slice(0,5),
            type: type,
            x: lastCoords.x,
            y: lastCoords.y
        };

        log.unshift(entry);
        renderLog();
        
        // Efecto visual de guardado
        cursor.setAttribute('fill', 'gold');
        setTimeout(() => cursor.setAttribute('fill', 'var(--primary)'), 300);
    }

    function renderLog() {
        logContainer.innerHTML = log.map((item, index) => `
            <div class="log-item">
                <span><strong>${item.time}</strong> - ${item.type}</span>
                <span style="color: #999;">[${item.x},${item.y}]</span>
            </div>
        `).join('');
    }

    function undo() {
        log.shift();
        renderLog();
    }

    // Manejo de errores global para evitar el "error gigante"
    window.onerror = function(msg, url, line) {
        document.getElementById('error-screen').style.display = 'flex';
        console.error("Error capturado: ", msg, " en linea: ", line);
        return true;
    };
</script>

</body>
</html>
