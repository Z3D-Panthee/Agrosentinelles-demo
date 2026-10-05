const CACHE_NAME = 'sentinel-os-v10-cache-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/health',
  '/api/ligo-box/v1'
];

// Installation du Service Worker et mise en cache des ressources
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache ouvert');
        return cache.addAll(urlsToCache);
      })
  );
});

// Interception des requêtes réseau pour servir le cache en mode offline
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - retourne la réponse du cache
        if (response) {
          return response;
        }
        return fetch(event.request).catch(() => {
          // Fallback en cas de panne totale d'internet
          if (event.request.mode === 'navigate') {
            return caches.match('/index.html');
          }
        });
      })
  );
});
