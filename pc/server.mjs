import http from 'node:http';
import {readFile} from 'node:fs/promises';
const port=Number(process.env.PORT || 4173);
const files=new Map([['/','index.html'],['/index.html','index.html'],['/styles.css','styles.css'],['/theme-coral.css','theme-coral.css'],['/glass.css','glass.css'],['/app.js','app.js'],['/protocol.mjs','protocol.mjs']]);
const types={html:'text/html; charset=utf-8',css:'text/css; charset=utf-8',js:'text/javascript; charset=utf-8',mjs:'text/javascript; charset=utf-8'};
const server=http.createServer(async(req,res)=>{
  if(!['GET','HEAD'].includes(req.method)){res.writeHead(405,{'Allow':'GET, HEAD'}).end();return;}
  const path=new URL(req.url,'http://localhost').pathname;
  if(path==='/api/config'){res.writeHead(200,{'Content-Type':'application/json'}).end('{"serverConfigured":false}');return;}
  if(path==='/health'){res.writeHead(200,{'Content-Type':'application/json'}).end('{"status":"ok","backend":"n8n","scope":"demo"}');return;}
  const name=files.get(path);
  if(!name){res.writeHead(404).end('No encontrado');return;}
  try{
    const body=await readFile(new URL('./dist/'+name,import.meta.url));
    res.writeHead(200,{'Content-Type':types[name.split('.').pop()],'Content-Length':body.length,
      'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer',
      'Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self' https:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"});
    res.end(req.method==='HEAD'?undefined:body);
  }catch{res.writeHead(500).end('No se pudo cargar la interfaz');}
});
server.listen(port,'127.0.0.1',()=>console.log('Sistemas PC: http://127.0.0.1:'+port));
for(const signal of ['SIGINT','SIGTERM'])process.on(signal,()=>server.close(()=>process.exit(0)));
