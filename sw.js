// ==========================================
// AGROSENTINELLES ADMIN V5.0 — SERVICE WORKER
// VÉROLIS SARL × Sentinel OS
// ==========================================

const CACHE_NAME = 'sentinel-os-v5-cache-v2';
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

// Installation du Service Worker et mise en cache des ressources critiques
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[Service Worker] Cache initialisé avec succès');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting())
  );
});

// Activation et nettoyage des anciens caches obsolètes
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Suppression de l ancien cache :', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Interception des requêtes réseau (Stratégie hybride Cache-First avec Network Fallback)
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Pour les requêtes API dynamiques : tentative réseau d'abord, puis repli local/cache
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Si la requête réseau réussit, on met à jour le cache de l'API en arrière-plan
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseClone);
          });
          return response;
        })
        .catch(() => {
          // Si le réseau échoue (mode offline total), on sert la réponse en cache
          return caches.match(event.request).then(cachedResponse => {
            if (cachedResponse) {
              return cachedResponse;
            }
            // Réponse de secours JSON si l'API n'a jamais été mise en cache
            return new Response(
              JSON.stringify({ status: "offline", message: "Mode Offline First actif — Données locales SQLite" }),
              { headers: { 'Content-Type': 'application/json' } }
            );
          });
        })
    );
    return;
  }

  // Pour les fichiers statiques et pages HTML : Cache d'abord, puis réseau
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request)
          .then(networkResponse => {
            return caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, networkResponse.clone());
              return networkResponse;
            });
          })
          .catch(() => {
            // Repli de navigation global en cas de panne totale hors-ligne
            if (event.request.mode === 'navigate') {
              return caches.match('/index.html');
            }
          });
      })
  );
});
