// Solo para revisar la app en el navegador de la PC.
// El servidor rechaza peticiones con Origin distinto; este proxy local las reenvía sin Origin.
import http from 'node:http';

const DESTINO = 'https://academico.nicolas16.life';
const PUERTO = Number(process.env.PUERTO ?? 8099);

http
  .createServer(async (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Accept');
    if (req.method === 'OPTIONS') return res.writeHead(204).end();
    if (!['/api/student', '/api/chat'].includes(req.url)) return res.writeHead(404).end();
    const partes = [];
    for await (const p of req) partes.push(p);
    try {
      const r = await fetch(DESTINO + req.url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: Buffer.concat(partes),
      });
      res.writeHead(r.status, { 'Content-Type': 'application/json; charset=utf-8' });
      res.end(await r.text());
    } catch {
      res.writeHead(502).end('{"error":"Proxy sin conexion."}');
    }
  })
  .listen(PUERTO, () => console.log(`Proxy web en http://localhost:${PUERTO}`));
