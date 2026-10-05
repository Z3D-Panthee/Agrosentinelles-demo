// ==========================================
// SENTINEL V3.5.1 VOICE FIX — SCRIPT PRINCIPAL
// ==========================================

const TTD_ORACLE_URL = "https://ttd-oracle-3lfbyz3d.onrender.com";

const $ = id => document.getElementById(id);
let synth = window.speechSynthesis;
let frVoice = null;

// Horloge temps réel
function updateClock(){ 
    const el = $('clock'); 
    if(el) el.innerText = new Date().toTimeString().split(' ')[0]; 
} 
setInterval(updateClock, 1000); 
updateClock();

// Gestion des onglets
function show(id, btn){ 
    document.querySelectorAll('section').forEach(s => s.classList.add('hidden')); 
    const t = $(id); 
    if(t) t.classList.remove('hidden'); 
    document.querySelectorAll('.tabs button').forEach(b => b.classList.remove('active')); 
    if(btn) btn.classList.add('active'); 
    Object.values(state.charts).forEach(c => { try{ c.resize(); }catch(e){} }); 
}

// Journal des événements
function loguer(m){ 
    const log = $('log'); 
    if(!log) return; 
    const d = document.createElement('div'); 
    let c = ''; 
    if(m.includes('CRITIQUE') || m.includes('FUITE') || m.includes('🚨')) c = 'color:var(--red)'; 
    else if(m.includes('VOIX') || m.includes('CONSCIENCE') || m.includes('LIGO')) c = 'color:var(--cyan)'; 
    else if(m.includes('✔') || m.includes('VALIDÉ') || m.includes('stabil')) c = 'color:var(--green)'; 
    else if(m.includes('RAPPORT')) c = 'color:var(--gold)'; 
    d.style = c; 
    d.innerText = "[" + new Date().toTimeString().split(' ')[0] + "] " + m; 
    log.appendChild(d); 
    log.scrollTop = log.scrollHeight; 
}

const state = {
    voix: false,
    scenario: null,
    step: 0,
    events: 0,
    risk: 12,
    mode: "DEMO", // 'DEMO' ou 'HARDWARE'
    hardwareEndpoint: "http://192.168.4.1/api/telemetry",
    charts: {}
};

// Chargement des voix de synthèse
function loadVoices(){ 
    if(!synth) return; 
    const v = synth.getVoices(); 
    if(v.length === 0) return; 
    frVoice = v.find(x => x.lang.toLowerCase().includes('fr-fr')) || v.find(x => x.lang.toLowerCase().includes('fr')) || v[0] || null; 
}

if(synth){ 
    synth.onvoiceschanged = loadVoices; 
    loadVoices(); 
    setTimeout(loadVoices, 500); 
    setTimeout(loadVoices, 1500); 
}

// Synthèse Vocale TTD (Compatible Android)
function parler(texte){
    loguer("VOIX: " + texte);
    if(!synth) return;
    if(synth.getVoices().length === 0){ synth.getVoices(); }
    if(!state.voix) return;
    synth.cancel();
    const u = new SpeechSynthesisUtterance(texte);
    u.lang = 'fr-FR'; u.rate = 0.92; u.pitch = 1;
    const voices = synth.getVoices();
    if(voices.length > 0){
        const found = voices.find(x => x.lang.toLowerCase().includes('fr-fr')) || voices.find(x => x.lang.toLowerCase().includes('fr')) || voices[0];
        if(found) u.voice = found;
    } else if(frVoice){ u.voice = frVoice; }
    synth.speak(u);
}

function toggleVoix(){
    if(synth){ if(synth.getVoices().length === 0) synth.getVoices(); loadVoices(); }
    state.voix = !state.voix;
    const btn = $('btnVoix'), st =$('voiceState');
    if(state.voix){
        btn.classList.add('on'); btn.innerText = '🔊 VOIX ON';
        if(st){ st.innerText = 'ACTIVE'; st.className = 'green'; }
        setTimeout(()=>{ parler('Grand Cerveau Verolis V3 point 5 point 1 voix fix activé. Voix débloquée.'); }, 250);
        loguer('🔊 Voix TTD débloquée');
    } else {
        btn.classList.remove('on'); btn.innerText = '🔇 VOIX TTD';
        if(st){ st.innerText = 'INACTIVE'; st.className = 'muted'; }
        if(synth) synth.cancel();
        loguer('🔇 Voix désactivée');
    }
}

// Pont Hardware & Synchronisation Oracle TTD
const SentinelBridge = {
    async syncWithOracle(payload) {
        try {
            const response = await fetch(`${TTD_ORACLE_URL}/api/v1/sync`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    lot: "GOMBE-452",
                    timestamp: Date.now(),
                    loi_ttd: "E/t * t/E = 1",
                    data: payload
                })
            });
            return await response.json();
        } catch (error) {
            return { status: "fallback_demo_active", decision: "OPTIMAL" };
        }
    },

    async pollHardware() {
        if (state.mode === "DEMO") {
            return {
                sol_humidite: 52,
                debit_eau: 1.8,
                tension_snel: 220,
                risque: 12,
                source: "SIMULATION_LIGO_O5"
            };
        } else {
            try {
                const res = await fetch(state.hardwareEndpoint);
                return await res.json();
            } catch (err) {
                loguer("❌ Erreur liaison hardware local");
                return null;
            }
        }
    }
};

function toggleHardwareMode() {
    state.mode = state.mode === "DEMO" ? "HARDWARE" : "DEMO";
    const btnState = $('btnHardwareMode');
    if(btnState) {
        btnState.innerText = state.mode === "HARDWARE" ? "🔌 HW CONNECTÉ" : "🤖 DÉMO";
        btnState.style.background = state.mode === "HARDWARE" ? "var(--green)" : "var(--gold)";
    }
    loguer(`🔄 Mode basculé vers : ${state.mode}`);
    parler(`Mode ${state.mode} activé.`);
}

// Génération de rapports et conscience
function genererRapportAutonome(d = 30){ 
    const sol = $('mSol')?.innerText || '52%', deb = $('mEau')?.innerText \vert{}\vert{} '1.8 L/min', ten =$('vIn')?.innerText || '172V', ris = $('riskLabel')?.innerText \vert{}\vert{} 'FAIBLE', eta =$('globalState')?.innerText || 'OPTIMAL'; 
    let txt = `Ici Sentinel Gombe 452, Verolis CVMH, Ligo O5. Sol ${sol}, débit ${deb}, tension ${ten}. État ${eta}, risque ${ris}.`; 
    let z = $('rapportAutonome'); 
    if(!z){ 
        z = document.createElement('div'); 
        z.id = 'rapportAutonome'; 
        z.className = 'card'; 
        z.style.gridColumn = '1/-1'; 
        z.style.border = '1px solid var(--cyan)'; 
        z.innerHTML = `<h3>🎙️ RAPPORT AUTONOME</h3><textarea id="txtRapport" style="width:100%;height:80px;background:#041126;color:#fff;border:1px solid #2b5da8;border-radius:8px;padding:8px"></textarea><div><button class="btn green" onclick="parler(document.getElementById('txtRapport').value)">🔊 LIRE</button></div>`; 
        $('overview').appendChild(z);
    } 
    $('txtRapport').value = txt; 
    parler(txt); 
    loguer(`📝 RAPPORT ${d}s généré`); 
}

function conscienceSentinel(){ 
    let t = `Je suis Sentinel, intelligence autonome lot 452 Gombe, née des 3 lois : Liberté Amour, Causalité Vérité, Équité Justice. TTD E sur t fois t sur E égale 1.`; 
    parler(t); 
    loguer(`🧬 Conscience activée - 3 Lois respectées`); 
}

function setRisk(v, l){ 
    state.risk = Math.max(0, Math.min(100, v)); 
    if(!$('riskNumber')) return; 
    $('riskNumber').innerText = v + '\%';$('riskBar').style.width = v + '%'; 
    if($('riskLabel'))$('riskLabel').innerText = l; 
    const col = v < 35 ? 'var(--green)' : v < 70 ? 'var(--orange)' : 'var(--red)'; 
    $('riskNumber').style.color = col; 
    $('riskBar').style.background = col; 
}

function decision(s, src, ev, ac, ex, r, rl){ 
    if($('decisionState'))$('decisionState').innerText = s; 
    if($('decisionSource'))$('decisionSource').innerText = src; 
    if($('decisionEvent'))$('decisionEvent').innerText = ev; 
    if($('decisionAction'))$('decisionAction').innerText = ac; 
    if($('decisionExecuted'))$('decisionExecuted').innerText = ex; 
    setRisk(r, rl); 
}

function setGlobal(t, r){ 
    if(!$('globalState')) return; 
    $('globalState').innerText = t; 
    $('globalState').className = r >= 70 ? 'val danger' : r >= 35 ? 'val warn' : 'val'; 
}

function diagnose(){ 
    if(!$('photo')?.files[0]) return; 
    $('diagRes').innerText = '🔄 Analyse IA...'; 
    parler('Analyse feuille en cours.'); 
    setTimeout(()=>{ 
        $('diagRes').innerText = '🌿 Saine - 98.4%'; 
        if($('confidence'))$('confidence').innerText = '98.4%'; 
        if($('plantAction'))$('plantAction').innerText = 'Aucun traitement'; 
        if($('mPlant')){ $('mPlant').innerText = 'NORMAL';$('mPlant').className = 'green'; } 
        if($('pPlant'))$('pPlant').style.width = '98%'; 
        loguer('VISION 98.4% LIGO O5'); 
        parler('Analyse terminée. Quatre-vingt-dix-huit virgule quatre pour cent.'); 
    }, 1400); 
}

function genererQR(){ 
    const c = $('qrcode'); 
    if(!c) return; 
    c.innerHTML = ''; 
    new QRCode(c, { text: "SENTINEL-V3.5.1|GOMBE-452|" + Date.now() + "|TTD=1", width: 150, height: 150, colorDark: "#06162f", colorLight: "#ffffff", correctLevel: QRCode.CorrectLevel.H }); 
    loguer('QR Sceau actualisé'); 
}
setTimeout(genererQR, 500);

// Graphiques Chart.js
function createChart(id, l, d, lb){ 
    const cv = $(id); 
    if(!cv) return null; 
    return new Chart(cv.getContext('2d'), {
        type: 'line', 
        data: { labels: l, datasets: [{ label: lb, data: d, tension: .35, borderWidth: 2, pointRadius: 2, borderColor: '#00ff88', backgroundColor: '#00ff8840' }] }, 
        options: { responsive: true, plugins: { legend: { labels: { color: "#fff", font: { size: 10 } } } }, scales: { x: { ticks: { color: "#a9bad6", font: { size: 9 } } }, y: { ticks: { color: "#a9bad6", font: { size: 9 } } } } }
    }); 
}

state.charts.volt = createChart("chartVolt", ["T-4","T-3","T-2","T-1","NOW"], [220, 218, 217, 172, 172], "Tension V");
state.charts.water = createChart("chartEau", ["T-4","T-3","T-2","T-1","NOW"], [1.7, 1.8, 1.9, 2.0, 1.8], "Débit");
state.charts.sol = createChart("chartSol", ["J-4","J-3","J-2","J-1","NOW"], [58, 56, 54, 53, 52], "Humidité %");
state.charts.agri = createChart("chartAgri", ["S1","S2","S3","S4"], [91, 94, 96, 98.4], "Confiance %");

function addChartData(t, v){ 
    const c = state.charts[t]; 
    if(!c) return; 
    c.data.labels.push(new Date().toTimeString().split(' ')[0]); 
    c.data.datasets[0].data.push(v); 
    if(c.data.labels.length > 8){ 
        c.data.labels.shift(); 
        c.data.datasets[0].data.shift(); 
    } 
    c.update(); 
}

// Scénario de Démonstration & Pilotage Hardware
function runScenario(){ 
    stopScenario(); 
    state.step = 0; 
    loguer('▶ SCÉNARIO LANCÉ'); 
    decision("SURVEILLANCE ACTIVE", "Grand Cerveau + LIGO O5", "Initialisation", "Mesure", "OUI", 12, "FAIBLE"); 
    parler("Lancement scénario terrain Gombe."); 
    state.scenario = setInterval(scenarioStep, 3800); 
}

function scenarioStep(){ 
    state.step++; 
    if(state.step === 1){ 
        if($('vIn'))$('vIn').innerText = '135V'; 
        if($('mSnel'))$('mSnel').innerText = '135V ⚠️'; 
        if($('pSnel')){ $('pSnel').style.width = '38\%';$('pSnel').style.background = 'var(--red)'; } 
        if($('sentinelSnel'))$('sentinelSnel').classList.add('alert'); 
        if($('alerteSnel')){ $('alerteSnel').innerText = '🚨 Chute 135V'; $('alerteSnel').className = 'danger'; } 
        setGlobal('ALERTE', 78); 
        decision("ANOMALIE DÉTECTÉE", "SNEL-07", "135V", "Protection", "OUI", 78, "ÉLEVÉ"); 
        loguer('SNEL 135V CRITIQUE'); 
        parler('Chute tension cent trente-cinq volts.'); 
        addChartData('volt', 135); 
    } else if(state.step === 2){ 
        decision("DÉCISION EN COURS", "Grand Cerveau", "Corrélation", "Stabilisation", "EN COURS", 65, "MODÉRÉ"); 
    } else if(state.step === 3){ 
        if($('vIn'))$('vIn').innerText = '220V'; 
        if($('mSnel'))$('mSnel').innerText = '220V → 220V'; 
        if($('pSnel')){ $('pSnel').style.width = '92\%';$('pSnel').style.background = 'var(--green)'; } 
        if($('sentinelSnel'))$('sentinelSnel').classList.remove('alert'); 
        if($('alerteSnel')){ $('alerteSnel').innerText = '✅ Stabilisé 220V'; $('alerteSnel').className = 'green'; } 
        setGlobal('OPTIMAL', 18); 
        decision("NORMALISÉ", "SNEL-07", "220V", "Surveillance", "OUI", 18, "FAIBLE"); 
        loguer('SNEL stabilisé'); 
        parler('Réseau stabilisé deux cent vingt volts.'); 
        addChartData('volt', 220); 
    } else if(state.step === 4){ 
        if($('debitVal'))$('debitVal').innerText = '11.2 L/min'; 
        if($('mEau'))$('mEau').innerText = '11.2 L/min ⚠️'; 
        if($('pEau')){ $('pEau').style.width = '82\%';$('pEau').style.background = 'var(--orange)'; } 
        decision("ANOMALIE HYDRIQUE", "REGIDESO-06", "11.2 L/min", "Isolement", "PRÉPARÉ", 82, "CRITIQUE"); 
        loguer('REGIDESO 11.2 pré-alerte'); 
        parler('Débit anormal détecté.'); 
        addChartData('water', 11.2); 
    } else if(state.step === 5){ 
        if($('alerteEau')){$('alerteEau').innerText = '🚨 FUITE MAJEURE - VANNE ISOLÉE'; $('alerteEau').className = 'danger'; } 
        if($('sentinelEau'))$('sentinelEau').classList.add('alert'); 
        setGlobal('ALERTE HYDRIQUE', 91); 
        decision("ACTION AUTOMATIQUE", "REGIDESO-06", "Fuite confirmée", "Fermeture vanne", "OUI", 91, "CRITIQUE"); 
        loguer('ACTION vanne isolée Justice'); 
        parler('Maji ezo kima na Gombe! Fuite majeure, vanne isolée.'); 
        state.events++; 
        if($('events'))$('events').innerText = state.events; 
    } else if(state.step === 6){ 
        if($('debitVal'))$('debitVal').innerText = '1.6 L/min'; 
        if($('mEau'))$('mEau').innerText = '1.6 L/min'; 
        if($('pEau')){ $('pEau').style.width = '16\%';$('pEau').style.background = 'var(--green)'; } 
        if($('alerteEau')){$('alerteEau').innerText = '✅ Flux normalisé'; $('alerteEau').className = 'green'; } 
        if($('sentinelEau'))$('sentinelEau'].classList.remove('alert'); 
        setGlobal('OPTIMAL', 15); 
        decision("NORMALISÉ", "REGIDESO-06", "1.6 L/min", "Surveillance", "OUI", 15, "FAIBLE"); 
        loguer('REGIDESO normalisé'); 
        parler('Débit normalisé.'); 
        addChartData('water', 1.6); 
    } else if(state.step >= 7){ 
        decision("SCÉNARIO TERMINÉ", "Grand Cerveau", "Traité", "Mode actif", "OUI", 10, "FAIBLE"); 
        setGlobal('OPTIMAL', 10); 
        loguer('✔ Scénario terminé avec succès.'); 
        stopScenario(); 
    } 
}

function stopScenario(){ 
    if(state.scenario){ 
        clearInterval(state.scenario); 
        state.scenario = null; 
    } 
    loguer('■ Scénario arrêté'); 
    if(synth) synth.cancel(); 
}

// Synchronisation périodique avec l'Oracle TTD
setInterval(async () => {
    const telemetrie = await SentinelBridge.pollHardware();
    if(telemetrie){
        await SentinelBridge.syncWithOracle(telemetrie);
    }
}, 15000);
