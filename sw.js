// ==========================================
// AGROSENTINELLES ADMIN V5.0 — SERVICE WORKER FINALE v10.6
// VÉROLIS SARL × CEPT ASBL 0625/2010 × Sentinel OS v10.6
// 5 APK Agro + 3 APK Lois RC/RO/RI + APK Junior
// CACHE v10.6 FINALE IMPECCABLE — GEL 01/10 INSPECTION
// ==========================================

const CACHE_NAME = 'sentinel-os-v10-6-finale-impeccable-5apk-3apk-junior-v1';
const CORE_URLS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/health',
  '/api/dashboard',
  '/api/sentinel/status',
  '/api/ligo-box/v1',
  '/api/cept/verolis',
  '/api/exploitations',
  '/api/producteurs',
  '/api/lots',
  '/api/stocks'
];

const CDN_URLS = [
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js',
  'https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js'
];

// Install — cache core + CDN en mode tolerant
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(async cache => {
      console.log('[SW v10.6 FINALE] Cache initialisé');
      await Promise.allSettled(CORE_URLS.map(u => cache.add(u).catch(e => console.warn(`[SW] skip ${u}`, e.message))));
      await Promise.allSettled(CDN_URLS.map(u => cache.add(u).catch(e => console.warn(`[SW] skip CDN ${u}`, e.message))));
      self.skipWaiting();
    })
  );
});

// Activate — nettoie tous les anciens caches v3, v5
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.map(k => {
        if (k !== CACHE_NAME) {
          console.log('[SW v10.6 FINALE] Suppression ancien cache:', k);
          return caches.delete(k);
        }
      })
    )).then(() => self.clients.claim())
  );
});

// Fetch — Stratégie hybride FINALE 0 BUG
self.addEventListener('fetch', event => {
  const req = event.request;
  const url = new URL(req.url);

  if (req.method !== 'GET' || !url.protocol.startsWith('http')) return;

  // 1. API dynamique : Network-First puis Cache puis JSON offline sécurisé
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(req).then(res => {
        if (res && res.status === 200) {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(req, clone));
        }
        return res;
      }).catch(async () => {
        const cached = await caches.match(req);
        if (cached) return cached;
        // Fallback offline normalisé pour Sentinel OS v10.6
        return new Response(JSON.stringify({
          status: "offline_secure_v10_6",
          message: "Mode Offline-First actif — SQLite / IndexedDB — 2 écoles CEPT + 5APK+3APK+Junior — I_TTD=1.0",
          I_TTD: 1.0,
          epsilon: 1e-5,
          Tr_T: 0.0012,
          RC_RO_rad: 0.0012,
          organisation: "VÉROLIS SARL × CEPT ASBL 0625/2010",
          timestamp: new Date().toISOString()
        }), { status: 200, headers: { 'Content-Type': 'application/json' } });
      })
    );
    return;
  }

  // 2. Statique / HTML : Cache-First puis Network avec maj transparente
  event.respondWith(
    caches.match(req).then(cached => {
      const networkFetch = fetch(req).then(netRes => {
        if (netRes && netRes.status === 200 && netRes.type === 'basic') {
          const clone = netRes.clone();
          caches.open(CACHE_NAME).then(c => c.put(req, clone));
        }
        return netRes;
      }).catch(() => null);
      return cached || networkFetch || caches.match('/index.html');
    }).catch(async () => {
      if (req.mode === 'navigate') {
        return (await caches.match('/index.html')) || new Response('Offline — Sentinel OS v10.6', { status: 503 });
      }
      return new Response('Ressource offline', { status: 503 });
    })
  );
});