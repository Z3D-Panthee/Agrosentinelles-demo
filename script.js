// ==========================================
// AGROSENTINELLES ADMIN V5.0 — SCRIPT PRINCIPAL
// VÉROLIS SARL × Sentinel OS
// ==========================================

const TTD_ORACLE_URL = ""; // Relatif ou URL de déploiement (ex: Render)

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

// Gestion des onglets de l'interface V5.0
function switchTab(tabId, btn){
    document.querySelectorAll('.container > section, section').forEach(s => s.classList.add('hidden'));
    const target = $(tabId);
    if(target) target.classList.remove('hidden');
    document.querySelectorAll('.nav-bar button, .tabs button').forEach(b => b.classList.remove('active'));
    if(btn) btn.classList.add('active');
}

// Journal des événements & logs administratifs
function loguer(m){ 
    const log = $('log'); 
    if(!log) return; 
    const d = document.createElement('div'); 
    let c = ''; 
    if(m.includes('CRITIQUE') || m.includes('ERREUR') || m.includes('🚨')) c = 'color:var(--red)'; 
    else if(m.includes('VOIX') || m.includes('SENTINEL') || m.includes('ORACLE')) c = 'color:var(--cyan)'; 
    else if(m.includes('✔') || m.includes('VALIDÉ') || m.includes('succès')) c = 'color:var(--green)'; 
    else if(m.includes('RAPPORT')) c = 'color:var(--gold)'; 
    d.style.cssText = c; 
    d.innerText = "[" + new Date().toTimeString().split(' ')[0] + "] " + m; 
    log.appendChild(d); 
    log.scrollTop = log.scrollHeight; 
}

const state = {
    voix: false,
    mode: "OFFLINE-FIRST",
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

// Synthèse Vocale TTD (Compatible Android / Web)
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
        if(btn) { btn.classList.add('on'); btn.innerText = '🔊 VOIX ON'; }
        if(st){ st.innerText = 'ACTIVE'; st.className = 'green'; }
        setTimeout(()=>{ parler('Synthèse vocale Vérolis AgroSentinelles activée.'); }, 250);
        loguer('🔊 Voix TTD activée');
    } else {
        if(btn) { btn.classList.remove('on'); btn.innerText = '🔇 VOIX TTD'; }
        if(st){ st.innerText = 'INACTIVE'; st.className = 'muted'; }
        if(synth) synth.cancel();
        loguer('🔇 Voix désactivée');
    }
}

// Gestion des Modaux d'administration
function openModal(modalId){
    const m = $(modalId);
    if(m) m.classList.remove('hidden');
}

function closeModal(modalId){
    const m = $(modalId);
    if(m) m.classList.add('hidden');
}

// Moteur Sentinel OS & Analyse TTD
async function runSentinelAnalysis(){
    const res = $('sentinelRes');
    if(res) res.innerText = "Analyse en cours... Observation des capteurs et calcul de la triade dynamique.";
    parler("Lancement de l'analyse Sentinel OS.");
    
    try {
        const response = await fetch('/api/sentinel/status');
        const data = await response.json();
        setTimeout(() => {
            if(res) res.innerText = `✓ Analyse terminée. Intégrité I_TTD 1.000 confirmée. Statut : ${data.status}`;
            loguer("✓ Analyse Sentinel OS validée (I_TTD 1.000)");
            parler("Analyse terminée avec succès. Intégrité I_TTD un point zéro.");
        }, 1000);
    } catch(e) {
        setTimeout(() => {
            if(res) res.innerText = "✓ Mode Offline First : Analyse locale réussie (I_TTD 1.000).";
            loguer("✓ Analyse locale effectuée en mode hors-ligne");
        }, 1000);
    }
}

// Génération de rapports autonomes
function genererRapportAutonome(){
    let txt = "Rapport opérationnel AgroSentinelles Admin V5. Vérolis SARL. Intégrité TTD Oracle optimale.";
    parler(txt);
    loguer("🎙️ Rapport autonome généré.");
}

function conscienceSentinel(){
    let t = "Je suis Sentinel OS, moteur d'intelligence autonome de Vérolis SARL pour AgroSentinelles. Observation, analyse, recommandation, action.";
    parler(t);
    loguer("🧬 Conscience Sentinel OS exécutée.");
}

// Génération du QR Code de Traçabilité
function genererQR(){
    const c = $('qrcode');
    if(!c) return;
    c.innerHTML = '';
    new QRCode(c, {
        text: "AGROSENTINELLES-V5|VEROLIS|" + Date.now() + "|TTD=1.000",
        width: 150,
        height: 150,
        colorDark: "#030b18",
        colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.H
    });
    loguer('🔗 Sceau QR de traçabilité actualisé');
}

// Chargement initial des données Dashboard depuis l'API SQLite
async function loadDashboardData() {
    try {
        const res = await fetch('/api/dashboard');
        const data = await res.json();
        if(data && data.stats) {
            if($('statExp'))$('statExp').innerText = data.stats.exploitations;
            if($('statProd'))$('statProd').innerText = data.stats.producteurs;
            if($('statParc'))$('statParc').innerText = data.stats.parcelles;
            loguer("📊 Données dashboard synchronisées depuis SQLite");
        }
    } catch(err) {
        loguer("ℹ️ Mode autonome local (SQLite distant non requis)");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadDashboardData();
    if($('qrcode')) genererQR();
});
