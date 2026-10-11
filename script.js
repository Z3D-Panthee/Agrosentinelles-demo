// ==========================================================
// SENTINEL OS v10.6 — MOTEUR 3D & CLIENT LOGIC
// ==========================================================

const $ = id => document.getElementById(id);
let ecoleActive = 1; 
let chart = null;

// Three.js 3D Background Torus Animation
const scene = new THREE.Scene(); 
const camera = new THREE.PerspectiveCamera(75, innerWidth/innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas3d'), alpha: true }); 
renderer.setSize(innerWidth, innerHeight);

const geo = new THREE.TorusGeometry(8, 2, 16, 100); 
const mat = new THREE.MeshBasicMaterial({ color: 0x38bdf8, wireframe: true, transparent: true, opacity: 0.25 });
const torus = new THREE.Mesh(geo, mat); 
scene.add(torus); 
camera.position.z = 20;

function anim() {
  requestAnimationFrame(anim); 
  torus.rotation.x += 0.003; 
  torus.rotation.y += 0.005; 
  renderer.render(scene, camera);
} 
anim();

window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

// App Logic
function selMomo(m) {
  $('methodPaiement').value = m;
}

async function setEcole(id) {
  ecoleActive = id;
  $('chip1').classList.toggle('active', id == 1);$('chip2').classList.toggle('active', id == 2);
  refresh();
}

async function refresh() {
  try {
    let r = await fetch(`/api/eleves/${ecoleActive}`);
    let j = await r.json();
    
    $('titreEcole').innerText = ecoleActive == 1 ? 'GS Tshiseleka - Lemba' : 'GS Maman Gina KUMBI - Ngaba';$('caisse').innerText = (j.caisse || 0).toLocaleString() + ' CDF';
    
    let statsText = `Eleves: ${j.total || 0}`;
    if (j.by_method && Object.keys(j.by_method).length > 0) {
      statsText += ' | ' + Object.entries(j.by_method).map(([k, v]) => `${k}: ${v}`).join(' | ');
    } else {
      statsText += ' | Aucun paiement';
    }
    $('stats').innerText = statsText;
    
    $('liste').innerHTML = (j.eleves || []).map(e => `
      <div style="display:flex;justify-content:space-between;align-items:center;padding:10px;background:rgba(255,255,255,.05);border-radius:12px;margin:6px 0">
        <span>${e.id}. ${e.nom} - ${e.classe}</span>
        <button class="btn btn-green" style="padding:6px 12px" onclick="payer(${e.id})">PAYER</button>
      </div>
    `).join('') || '<small>Aucun élève - Ajoutez le premier</small>';
    
    let ctx = $('chartCaisse');
    if (chart) chart.destroy();
    
    let labels = Object.keys(j.by_method || {});
    let dataVals = Object.values(j.by_method || {});
    if (labels.length === 0) { labels = ['En attente']; dataVals = [1]; }
    
    chart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{ data: dataVals, backgroundColor: ['#e30613', '#ff7900', '#ff0000', '#0066ff', '#4ade80'] }]
      },
      options: { plugins: { legend: { labels: { color: '#fff' } } } }
    });
  } catch(err) {
    console.warn("Mode hors-ligne ou erreur de chargement", err);
  }
}

async function ajouterEleve() {
  let nom = $('nomEleve').value.trim();
  if (!nom) return;
  await fetch(`/api/eleves/add?nom=${encodeURIComponent(nom)}&ecole_id=${ecoleActive}`, { method: 'POST' });
  $('nomEleve').value = '';
  refresh();
}

async function payer(id) {
  let method = $('methodPaiement').value;
  let montant = $('montant').value;
  let res = await fetch(`/api/paiement/add?eleve_id=${id}&montant=${montant}&ecole_id=${ecoleActive}&method=${encodeURIComponent(method)}`, { method: 'POST' });
  let j = await res.json();
  alert(`✅ ${j.method} - ${montant} CDF\nTXN: ${j.txn_id}\n${j.message}`);
  refresh();
}

function exportExcel() { location.href = `/api/export/excel/${ecoleActive}`; }
function exportPDF() { let l = $('lang').value; location.href = `/api/export/pdf/${ecoleActive}?lang=${l}`; }

// QR code generation
window.addEventListener('DOMContentLoaded', () => {
  refresh();
  if (typeof QRCode !== 'undefined' && $('qrcode')) {
    new QRCode($('qrcode'), {
      text: "https://zenodo.org/records/19852087",
      width: 120, height: 120,
      colorDark: "#38bdf8", colorLight: "#020617"
    });
  }
});

fetch('/health').then(r => r.json()).then(h => {
  if($('health'))$('health').innerText = `● ${h.status} I_TTD=${h.I_TTD}`;
});
