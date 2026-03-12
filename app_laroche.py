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
