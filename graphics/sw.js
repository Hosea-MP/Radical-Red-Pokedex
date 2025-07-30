const CACHE_NAME = 'sprite-cache';

self.addEventListener('install', event => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (url.pathname.startsWith('/sprites/')) {
    event.respondWith(
      caches.open(CACHE_NAME).then(cache => {
        return cache.match(event.request).then(resp => {
          return resp || fetch(event.request).then(networkResp => {
            cache.put(event.request, networkResp.clone());
            return networkResp;
          });
        });
      })
    );
  }
});
