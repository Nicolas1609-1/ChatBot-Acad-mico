import {endpoint,sendMessage,inlineParts,createSessionId} from './protocol.mjs';
const $=id=>document.getElementById(id);
const store={get(key){try{return localStorage.getItem(key);}catch{return null;}},set(key,value){try{localStorage.setItem(key,value);}catch{}}};
let url=store.get('sistemas.endpoint') || '';
try{if(url)url=endpoint(url);}catch{url='';}
let serverConfigured=false;
try{const response=await fetch('/api/config',{cache:'no-store'});if(response.ok){const config=await response.json();serverConfigured=config.serverConfigured===true;if(serverConfigured)url='/api/chat';}}catch{}
let session=createSessionId(), student=null;
let busy=false,controller=null;
function connectionState(){ $('status').textContent=serverConfigured?'n8n conectado':url?'Conexión configurada':'Configurar conexión';$('status-dot').classList.toggle('configured',!!url);$('connect').title=serverConfigured?'Conexión administrada por el servidor':url?new URL(url).host:'Conectar la Chat URL de n8n'; }
function showConnection(){if(busy)return;if(serverConfigured){info('Conexión del servidor',[['n8n conectado','Las consultas pasan por este servidor hacia el agente n8n. No necesitas pegar direcciones ni claves API.'],['Datos simulados','La interfaz consulta datos ficticios. No modifica notas ni matrícula.']]);return;}$('endpoint').value=url;$('connection-error').textContent='';$('connection-dialog').showModal();}
function newConversation(){if(busy)return;student=null;$('academic-layout').hidden=true;$('student-gate').hidden=false;$('student-code').focus();session=createSessionId();$('messages').replaceChildren();$('welcome').hidden=false;$('feedback').textContent='';$('question').value='';updateCount();}
function updateCount(){$('counter').textContent=$('question').value.length+' / 6000';}
function setBusy(value){busy=value;$('send').disabled=value;$('question').disabled=value;$('connect').disabled=value;$('new-chat').disabled=value;$('cancel').hidden=!value;$('waiting').hidden=!value;document.querySelectorAll('.suggestion').forEach(button=>button.disabled=value);}
function inline(parent,text){
  for(const part of inlineParts(text)){
    if(part.kind==='strong'){const strong=document.createElement('strong');strong.textContent=part.text;parent.append(strong);}
    else if(part.kind==='link'){const anchor=document.createElement('a');anchor.href=part.href;anchor.textContent=part.text;anchor.target='_blank';anchor.rel='noopener noreferrer';parent.append(anchor);}
    else parent.append(document.createTextNode(part.text));
  }
}
function markdown(parent,text){
  const lines=text.split(/\r?\n/);let index=0;
  while(index<lines.length){
    const line=lines[index].trim();
    if(!line){index++;continue;}
    if(line.includes('|') && index+1<lines.length && /^\s*\|?[\s:|-]+\|[\s:|-]*$/.test(lines[index+1])){
      const wrap=document.createElement('div');wrap.className='table-scroll';const table=document.createElement('table');const head=document.createElement('thead'),body=document.createElement('tbody');
      const cells=value=>value.replace(/^\s*\||\|\s*$/g,'').split('|').map(cell=>cell.trim());
      const row=(values,header)=>{const tr=document.createElement('tr');for(const value of values){const cell=document.createElement(header?'th':'td');if(header)cell.scope='col';inline(cell,value);tr.append(cell);}return tr;};
      head.append(row(cells(line),true));index+=2;while(index<lines.length && lines[index].includes('|')){body.append(row(cells(lines[index]),false));index++;}
      table.append(head,body);wrap.append(table);parent.append(wrap);continue;
    }
    const paragraph=document.createElement('p');inline(paragraph,line.replace(/^#{1,6}\s+/,''));parent.append(paragraph);index++;
  }
}
function addMessage(role,text,error=false){
  $('welcome').hidden=true;
  const article=document.createElement('article');article.className='message '+role+(error?' error':'');
  const head=document.createElement('div');head.className='message-head';
  const avatar=document.createElement('span');avatar.className='avatar';avatar.textContent=role==='user'?'T':'✧';
  head.append(avatar,document.createTextNode(role==='user'?'Tú':'Asistente de Sistemas'));article.append(head);
  const content=document.createElement('div');if(role==='user'){const paragraph=document.createElement('p');paragraph.textContent=text;content.append(paragraph);}else markdown(content,text);
  article.append(content);$('messages').append(article);article.scrollIntoView({behavior:'smooth',block:'end'});
}
$('connect').addEventListener('click',showConnection);
$('new-chat').addEventListener('click',newConversation);
$('connection-form').addEventListener('submit',event=>{
  event.preventDefault();
  try{const next=endpoint($('endpoint').value);if(next!==url)newConversation();url=next;store.set('sistemas.endpoint',url);connectionState();$('connection-dialog').close();$('feedback').textContent='Conexión guardada. La disponibilidad se comprobará al enviar una consulta.';$('question').focus();}
  catch(error){$('connection-error').textContent=error.message;}
});
document.querySelectorAll('[data-close]').forEach(button=>button.addEventListener('click',()=>$(button.dataset.close).close()));
document.querySelectorAll('.suggestion').forEach(button=>button.addEventListener('click',()=>{$('question').value=button.dataset.prompt;updateCount();$('question').focus();}));
$('question').addEventListener('input',updateCount);
$('question').addEventListener('keydown',event=>{if(event.key==='Enter' && !event.shiftKey && !event.isComposing){event.preventDefault();$('composer').requestSubmit();}});
$('cancel').addEventListener('click',()=>controller?.abort());
$('composer').addEventListener('submit',async event=>{
  event.preventDefault();if(busy)return;if(!student){newConversation();return;}
  const text=$('question').value.trim();if(!text){$('feedback').textContent='Escribe una pregunta para comenzar.';$('question').focus();return;}
  if(!url){$('feedback').textContent='Primero conecta la Chat URL de tu flujo n8n.';showConnection();return;}
  addMessage('user',text);$('question').value='';updateCount();$('feedback').textContent='';setBusy(true);controller=new AbortController();
  try{const answer=await sendMessage(url,text,session,{signal:controller.signal});addMessage('assistant',answer);}
  catch(error){addMessage('assistant',error.message,true);}
  finally{controller=null;setBusy(false);$('question').focus();}
});
function info(title,sections){$('info-title').textContent=title;$('info-content').replaceChildren();for(const [heading,text,href]of sections){const h=document.createElement('h3');h.textContent=heading;const p=document.createElement('p');p.textContent=text;$('info-content').append(h,p);if(href){const link=document.createElement('a');link.href=href;link.target='_blank';link.rel='noopener noreferrer';link.textContent='Abrir fuente ↗';$('info-content').append(link);}}$('info-dialog').showModal();}
$('sources').addEventListener('click',()=>info('Fuentes del asistente',[
['Expediente y plan','13 estudiantes ficticios, 32 materias y 110 créditos en PostgreSQL. No corresponden a un plan universitario oficial.'],
['Material del profesor','FAQ y propuesta de competencias digitales. Son referencias; la propuesta de julio de 2025 no acredita normativa vigente.','https://github.com/adiacla/clima-Biing26-UCC-Ibague/tree/9a01d6d4779579c464115543008defb216ad703e'],
['Calendario académico','Seis eventos ficticios para el periodo 2027-1. No es un calendario oficial.','https://docs.google.com/spreadsheets/d/1ett973VG0v2ZDECB9kYR8OO-T8kfz3pddtKPnYPidBE/edit'],
['Noticias de Sistemas','Publicaciones UNAB con fecha y enlace. El chatbot indica cuándo se sincronizaron.']
]));
$('scope').addEventListener('click',()=>info('Lo que puedes consultar',[
['Tu ruta académica','Promedio, avance, matrícula, historial, materias pendientes y simulación de semestres con prerrequisitos.'],
['Un prototipo de orientación','No matricula asignaturas, no cambia notas ni garantiza fechas de graduación. Los códigos U00 seleccionan expedientes ficticios y no autentican personas reales.'],
['Conexión y privacidad','No pegues claves API ni información real sensible. La sesión del estudiante se renueva al entrar o cambiar de perfil. Nueva conversación cambia la sesión; no borra la memoria antigua en n8n.'],
['Entrega actual en PC','La interfaz de teléfono y Expo están aplazados. El agente y todas las consultas siguen en n8n.']
]));
connectionState();updateCount();

$('change-student').addEventListener('click',newConversation);
document.querySelectorAll('[data-code]').forEach(button=>button.addEventListener('click',()=>{$('student-code').value=button.dataset.code;$('student-code').focus();}));
$('student-form').addEventListener('submit',async event=>{
 event.preventDefault();const codigo=$('student-code').value.trim().toUpperCase();
 if(!/^U00[0-9]{6}$/.test(codigo)){$('student-error').textContent='Usa U00 seguido de seis números.';return;}
 $('identify').disabled=true;$('student-error').textContent='Consultando tu expediente…';session=createSessionId();
 try{const response=await fetch('/api/student',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({codigo,sessionId:session})});const result=await response.json();
 if(!response.ok)throw new Error(result.error||'No se pudo consultar el expediente.');
 if(!result.encontrado||!result.estudiante)throw new Error('No encontramos ese código. Comprueba los números e inténtalo de nuevo.');
 student=result.estudiante;$('student-summary').textContent=student.nombre+' · '+student.codigo;
 $('profile-semester').textContent=student.semestre_actual;$('profile-enrollment').textContent='Matrícula '+student.estado_matricula;
 $('profile-gpa').textContent=Number(student.promedio_historico).toFixed(2);$('profile-credits').textContent=student.creditos_aprobados;
 $('profile-total').textContent='de '+student.creditos_plan+' créditos';$('profile-progress').textContent=Number(student.porcentaje_avance).toFixed(1)+'%';
 $('student-gate').hidden=true;$('academic-layout').hidden=false;$('student-error').textContent='';$('question').focus();
 }catch(error){$('student-error').textContent=error.message;}finally{$('identify').disabled=false;}
});
