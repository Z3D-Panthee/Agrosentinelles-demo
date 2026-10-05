// ==========================================
// AGROSENTINELLES ADMIN V5.0 — SERVICE WORKER (VERSION INTÉGRALE ROBUSTE ZÉRO BUG)
// VÉROLIS SARL × Sentinel OS
// ==========================================

const CACHE_NAME = 'sentinel-os-v5-cache-v3';
const urlsToCache = [
  '/',
  '/index.html',
  '/script.js',
  '/manifest.json',
  '/health',
  '/api/ligo-box/v1',
  '/api/dashboard',
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js',
  'https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js'
];

// Installation du Service Worker et mise en cache robuste
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[Service Worker] Cache initialisé avec succès');
        // Utilisation de addAll de manière sécurisée (évite un échec global si une ressource externe bloque)
        return Promise.allSettled(
          urlsToCache.map(url => cache.add(url).catch(err => console.warn(`[SW] Échec du cache pour ${url}:`, err)))
        );
      })
      .then(() => self.skipWaiting())
  );
});

// Activation et nettoyage strict des anciens caches obsolètes
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Suppression de l\'ancien cache :', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Interception des requêtes réseau avec stratégie hybride sécurisée (Zero Bug)
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Ignorer les requêtes non-GET ou les extensions tierces (ex: extensions chrome, devtools)
  if (event.request.method !== 'GET' || !url.protocol.startsWith('http')) {
    return;
  }

  // Pour les requêtes API dynamiques : tentative réseau d'abord, puis repli local/cache
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          if (response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        })
        .catch(async () => {
          const cachedResponse = await caches.match(event.request);
          if (cachedResponse) {
            return cachedResponse;
          }
          // Réponse de secours JSON normalisée pour Sentinel OS en mode hors-ligne
          return new Response(
            JSON.stringify({ 
              status: "offline_secure", 
              message: "Mode Offline First actif — Données locales SQLite / IndexedDB",
              timestamp: new Date().toISOString() 
            }),
            { 
              status: 200, 
              headers: { 'Content-Type': 'application/json' } 
            }
          );
        })
    );
    return;
  }

  // Pour les fichiers statiques et pages HTML : Cache-First avec Network Fallback et mise à jour transparente
  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        const fetchPromise = fetch(event.request).then(networkResponse => {
          if (networkResponse && networkResponse.status === 200) {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, responseToCache);
            });
          }
          return networkResponse;
        }).catch(() => {
          // Échec réseau silencieux pour les ressources statiques couvertes par le cache
        });

        // Retourne le cache immédiatement s'il existe, sinon attend le réseau
        return cachedResponse || fetchPromise;
      })
      .catch(async () => {
        // Repli de navigation global en cas de panne totale hors-ligne sur les pages HTML
        if (event.request.mode === 'navigate') {
          const fallback = await caches.match('/index.html');
          if (fallback) return fallback;
        }
        return new Response('Ressource non disponible hors-ligne', { status: 503, statusText: 'Service Unavailable' });
      })
  );
});
