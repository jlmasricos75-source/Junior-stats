<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Junior STATS</title>
    <style>
        body { 
            background: #0f172a; color: white; font-family: -apple-system, sans-serif; 
            margin: 0; padding: 10px; -webkit-text-size-adjust: 100%;
        }
        .screen { display: none; }
        .active { display: block; }
        
        h2, h3 { text-align: center; margin: 10px 0; color: #60a5fa; text-transform: uppercase; }
        
        .btn { 
            width: 100%; padding: 20px; margin: 5px 0; border: none; border-radius: 12px; 
            font-weight: bold; font-size: 18px; color: white; cursor: pointer;
            display: block; box-sizing: border-box; text-align: center;
        }
        .btn-blue { background: #2563eb; }
        .btn-green { background: #16a34a; }
        .btn-red { background: #dc2626; }
        .btn-orange { background: #ea580c; }
        .btn-gray { background: #334155; }
        
        .player-card { 
            background: #1e293b; padding: 15px; margin-bottom: 8px; border-radius: 8px; 
            border: 2px solid transparent; font-size: 18px;
        }
        .selected { border-color: #3b82f6; background: #1e3a8a; }

        .main-layout { width: 100%; display: table; border-spacing: 10px; }
        .layout-col { display: table-cell; vertical-align: top; width: 50%; }

        .court { 
            width: 100%; background: #1e293b; border: 2px solid #475569; 
            position: relative; border-radius: 10px; overflow: hidden; height: 380px;
        }
        .marker { 
            position: absolute; width: 14px; height: 14px; border-radius: 50%; 
            transform: translate(-50%, -50%); border: 1px solid white; 
        }

        .mini-p { 
            display: inline-block; width: 18%; margin: 1%; padding: 12px 0; 
            text-align: center; background: #334155; border-radius: 6px; font-weight: bold;
        }
        .p-active { background: #2563eb; border: 2px solid white; }

        input { width: 100%; padding: 15px; margin: 10px 0; border-radius: 8px; border: 1px solid #334155; background: #1e293b; color: white; box-sizing: border-box; }
        #log-view { width: 100%; height: 100px; background: #000; color: #0f0; font-family: monospace; padding: 10px; border-radius: 5px; overflow-y: scroll; }
    </style>
</head>
<body>

    <div id="s1" class="screen active">
        <h2>JUNIOR STATS</h2>
        <button class="btn btn-blue" onclick="loadRoster('A')">JUNIOR A (A + B)</button>
        <button class="btn btn-blue" onclick="loadRoster('B')">JUNIOR B</button>
    </div>

    <div id="s2" class="screen">
        <h3>CONVOCATORIA</h3>
        <div id="list-box"></div>
        <input type="text" id="rival-name" placeholder="Nombre Rival">
        <button class="btn btn-green" onclick="goMatch()">INICIAR PARTIDO</button>
        <button class="btn btn-gray" onclick="location.reload()">ATRÁS</button>
    </div>

    <div id="s3" class="screen">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
            <span id="rival-label"></span>
            <span id="total-pts" style="color:#60a5fa; font-weight:bold;">PTS: 0</span>
        </div>

        <div id="on-court-line"></div>

        <div class="main-layout">
            <div class="row">
                <div class="layout-col">
                    <div class="court" id="court-img" onclick="handleCourt(event)">
                        <div style="position:absolute; width:40%; height:30%; left:30%; top:0; border:1px solid #555;"></div>
                        <div id="shots-layer"></div>
                    </div>
                </div>
                <div class="layout-col">
                    <button class="btn btn-gray" onclick="addStat('REB')">REB</button>
                    <button class="btn btn-gray" onclick="addStat('AST')">AST</button>
                    <button class="btn btn-orange" onclick="addStat('PERD')">PERD</button>
                    <button class="btn btn-red" onclick="addStat('FALTA')">FALTA</button>
                    <button class="btn btn-blue" onclick="addStat('TL_IN')">TL ✅</button>
                </div>
            </div>
        </div>

        <button class="btn btn-green" onclick="changePlayer()">CAMBIO (🔄)</button>
        <div id="log-view">Registro...</div>
        <button class="btn btn-gray" onclick="copyAll()">VER RESUMEN</button>
    </div>

    <div id="s-shot" class="screen" style="position:fixed; inset:0; background:rgba(0,0,0,0.95); z-index:99; padding:20px;">
        <h2 id="shot-title">TIRO</h2>
        <button class="btn btn-green" style="padding:50px; margin-bottom:20px;" onclick="processShot(true)">ANOTADO</button>
        <button class="btn btn-red" style="padding:50px;" onclick="processShot(false)">FALLADO</button>
    </div>

    <script>
        var pA = [{d:"03",n:"SERRA"},{d:"08",n:"MORANA"},{d:"15",n:"AMER"},{d:"18",n:"GABI"},{d:"21",n:"ALÓS"},{d:"50",n:"FERRER"},{d:"99",n:"PEPE MÁS"}];
        var pB = [{d:"02",n:"LUCAS M"},{d:"05",n:"ADRIAN O"},{d:"09",n:"ANDREU E"},{d:"11",n:"ALEJANDRO"},{d:"12",n:"DAVID N"},{d:"23",n:"ANTONIO P"},{d:"24",n:"CARLOS M"},{d:"28",n:"DERIN A"},{d:"32",n:"GONZALO R"},{d:"82",n:"MIGUEL D"}];
        var currentRoster = [], convocados = [], quinteto = [], activeDorsal = "", totalPoints = 0, history = [];

        function loadRoster(m) {
            currentRoster = (m == 'A') ? pA.concat(pB) : pB;
            var h = "";
            for(var i=0; i<currentRoster.length; i++) h += '<div class="player-card" id="card-'+currentRoster[i].d+'" onclick="toggleP('+i+')">#'+currentRoster[i].d+' '+currentRoster[i].n+'</div>';
            document.getElementById('list-box').innerHTML = h;
            show('s2');
        }

        function toggleP(i) {
            var p = currentRoster[i], pos = convocados.indexOf(p);
            if(pos > -1) { convocados.splice(pos, 1); document.getElementById('card-'+p.d).className = "player-card"; }
            else { convocados.push(p); document.getElementById('card-'+p.d).className = "player-card selected"; }
        }

        function goMatch() {
            if(convocados.length < 5) { alert("Mínimo 5 jugadores"); return; }
            quinteto = convocados.slice(0, 5); activeDorsal = quinteto[0].d;
            document.getElementById('rival-label').innerText = "Vs " + document.getElementById('rival-name').value;
            refreshQ(); show('s3');
        }

        function refreshQ() {
            var h = "";
            for(var i=0; i<quinteto.length; i++) {
                var cls = (quinteto[i].d == activeDorsal) ? "mini-p p-active" : "mini-p";
                h += '<div class="'+cls+'" onclick="setActive(\''+quinteto[i].d+'\')">#'+quinteto[i].d+'</div>';
            }
            document.getElementById('on-court-line').innerHTML = h;
        }

        function setActive(d) { activeDorsal = d; refreshQ(); }

        function handleCourt(e) {
            var r = document.getElementById('court-img').getBoundingClientRect();
            lastPos = { x: ((e.clientX - r.left)/r.width)*100, y: ((e.clientY - r.top)/r.height)*100 };
            document.getElementById('shot-title').innerText = "TIRO #" + activeDorsal;
            show('s-shot');
        }

        function processShot(ok) {
            var p = (lastPos.y > 38) ? 2 : 3; if(!ok) p = 0;
            totalPoints += p;
            history.push("#" + activeDorsal + ": Tiro " + (ok?"OK":"F") + " ("+p+"p)");
            var m = document.createElement('div'); m.className = "marker"; m.style.left = lastPos.x + "%"; m.style.top = lastPos.y + "%";
            m.style.background = ok ? "#22c55e" : "#ef4444"; document.getElementById('shots-layer').appendChild(m);
            finish();
        }

        function addStat(t) { if(t == 'TL_IN') totalPoints += 1; history.push("#" + activeDorsal + ": " + t); finish(); }

        function finish() {
            document.getElementById('total-pts').innerText = "PTS: " + totalPoints;
            document.getElementById('log-view').innerText = history.slice(-5).join("\n");
            show('s3');
        }

        function changePlayer() {
            var bench = convocados.filter(function(p){ return !quinteto.some(function(q){return q.d == p.d}) });
            var msg = "Sustituir #" + activeDorsal + " por:\n";
            for(var i=0; i<bench.length; i++) msg += (i+1) + ": #" + bench[i].d + "\n";
            var r = prompt(msg);
            if(r && bench[r-1]) {
                for(var i=0; i<quinteto.length; i++) if(quinteto[i].d == activeDorsal) quinteto[i] = bench[r-1];
                activeDorsal = bench[r-1].d; refreshQ();
            }
        }

        function show(id) {
            var ss = document.getElementsByClassName('screen');
            for(var i=0; i<ss.length; i++) ss[i].className = "screen";
            document.getElementById(id).className = "screen active";
        }

        function copyAll() { alert(history.join("\n")); }
    </script>
</body>
</html>
