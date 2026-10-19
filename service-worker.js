const V='abs-v1',SHELL=['./','index.html','styles.css','app.js','manifest.json','python/script_analyzer.py','config/presets.json','config/models.json','assets/icon.svg'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==V).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
// Network first, cache fallback; also caches PyScript CDN files after first load.
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET')return;
  e.respondWith(fetch(e.request).then(r=>{if(r.ok){const cp=r.clone();caches.open(V).then(c=>c.put(e.request,cp))}return r}).catch(()=>caches.match(e.request)));
});
