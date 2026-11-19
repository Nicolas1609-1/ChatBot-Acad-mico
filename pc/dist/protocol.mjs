export function endpoint(raw){
  if(raw.trim()==='/api/chat')return '/api/chat';
  let url;try{url=new URL(raw.trim());}catch{throw new Error('Pega una URL de chat válida.');}
  if(url.protocol!=='https:' || url.username || url.password || url.search || url.hash || !url.pathname.endsWith('/chat')){
    throw new Error('Usa la Chat URL HTTPS terminada en /chat, sin claves ni parámetros.');
  }
  return url.href;
}
export function createSessionId(random=globalThis.crypto){
  if(typeof random.randomUUID==='function')return random.randomUUID();
  const bytes=random.getRandomValues(new Uint8Array(16));
  bytes[6]=(bytes[6]&15)|64;bytes[8]=(bytes[8]&63)|128;
  const hex=Array.from(bytes,value=>value.toString(16).padStart(2,'0')).join('');
  return [hex.slice(0,8),hex.slice(8,12),hex.slice(12,16),hex.slice(16,20),hex.slice(20)].join('-');
}
export function payload(message,sessionId){
  const text=message.trim();
  if(!text || text.length>6000)throw new Error('Escribe una consulta de entre 1 y 6000 caracteres.');
  if(typeof sessionId!=='string' || !sessionId.trim())throw new Error('Falta la sesión de conversación.');
  return {action:'sendMessage',chatInput:text,sessionId};
}
export function parseAnswer(data){
  const item=Array.isArray(data)?(data.length===1?data[0]:null):data;
  if(!item || typeof item.output!=='string' || !item.output.trim())throw new Error('La respuesta no contiene el campo output. Revisa el último nodo del flujo.');
  return item.output;
}
export function httpError(status){
  if(status===429)return 'El servicio alcanzó su límite temporal. Espera un minuto y vuelve a intentarlo.';
  if(status===401 || status===403)return 'El chat requiere autorización. Revisa el acceso configurado en n8n.';
  if(status===404)return 'La URL no está disponible. Comprueba que sea la Chat URL y que el flujo esté publicado o escuchando pruebas.';
  return 'No se pudo completar la consulta (HTTP '+status+').';
}
export async function sendMessage(rawEndpoint,message,sessionId,{fetchImpl=globalThis.fetch,signal,timeoutMs=120000}={}){
  const url=endpoint(rawEndpoint),body=payload(message,sessionId);
  const timeout=new AbortController();let timedOut=false;
  const timer=setTimeout(()=>{timedOut=true;timeout.abort();},timeoutMs);
  const abort=()=>timeout.abort();signal?.addEventListener('abort',abort,{once:true});
  if(signal?.aborted)timeout.abort();
  try{
    const response=await fetchImpl(url,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(body),signal:timeout.signal,redirect:'error',credentials:'omit',referrerPolicy:'no-referrer'});
    if(!response.ok)throw new Error(httpError(response.status));
    const text=await response.text();
    if(text.length>1024*1024)throw new Error('La respuesta es demasiado grande.');
    let data;try{data=JSON.parse(text);}catch{throw new Error('El chat no devolvió JSON. Comprueba la URL y el modo de respuesta de n8n.');}
    return parseAnswer(data);
  }catch(error){
    if(timedOut)throw new Error('La consulta tardó demasiado. n8n podría seguir procesándola; espera antes de reenviar.');
    if(signal?.aborted)throw new Error('Consulta cancelada en este navegador. n8n podría seguir procesándola.');
    if(error instanceof TypeError)throw new Error('No pude conectar con n8n. Revisa Internet, la URL y los orígenes permitidos (CORS).');
    throw error;
  }finally{clearTimeout(timer);signal?.removeEventListener('abort',abort);}
}
export function safeLink(raw){
  try{const url=new URL(raw);return url.protocol==='https:' && !url.username && !url.password?url.href:null;}catch{return null;}
}
export function inlineParts(text){
  const pattern=/(\[[^\]\n]+\]\(https:\/\/(?:[^\s()]|\([^()\s]*\))+\)|https:\/\/[^\s<>]+|\*\*[^*\n]+\*\*)/g;
  const parts=[];let cursor=0;
  for(const match of text.matchAll(pattern)){
    parts.push({kind:'text',text:text.slice(cursor,match.index)});
    const token=match[0];
    if(token.startsWith('**'))parts.push({kind:'strong',text:token.slice(2,-2)});
    else{
      const markdown=token.match(/^\[([^\]]+)\]\((https:\/\/(?:[^\s()]|\([^()\s]*\))+)\)$/);
      const href=safeLink(markdown?markdown[2]:token.replace(/[.,;]+$/,''));
      parts.push(href?{kind:'link',text:markdown?markdown[1]:href,href}:{kind:'text',text:token});
    }
    cursor=match.index+token.length;
  }
  parts.push({kind:'text',text:text.slice(cursor)});
  return parts;
}
