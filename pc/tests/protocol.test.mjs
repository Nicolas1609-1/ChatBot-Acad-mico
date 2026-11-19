import {test} from 'node:test';
import assert from 'node:assert/strict';
import {endpoint,payload,parseAnswer,safeLink,sendMessage} from '../dist/protocol.mjs';
test('accepts HTTPS n8n chat but rejects credentials and query keys',()=>{
 assert.equal(endpoint(' https://example.org/webhook/id/chat '),'https://example.org/webhook/id/chat');
 for(const url of ['http://example.org/chat','https://user:pass@example.org/chat','https://example.org/chat?token=x','https://example.org/editor','javascript:alert(1)','https://example.org/chat#fragment'])assert.throws(()=>endpoint(url));
});
test('payload preserves session, escapes data and validates length',()=>{
 assert.deepEqual(payload(' Hola "nota"\nDEMO001 ','abc'),{action:'sendMessage',chatInput:'Hola "nota"\nDEMO001',sessionId:'abc'});
 for(const message of [' ','a'.repeat(6001)])assert.throws(()=>payload(message,'abc'));
 assert.throws(()=>payload('hola',''));
});
test('both n8n output shapes accepted; missing or ambiguous output rejected',()=>{
 assert.equal(parseAnswer({output:'3.5'}),'3.5');assert.equal(parseAnswer([{output:'3.5'}]),'3.5');
 for(const item of [{error:'private'},[],[{output:'a'},{output:'b'}],{output:''}])assert.throws(()=>parseAnswer(item));
});
test('unsafe links never become clickable',()=>{
 assert.equal(safeLink('javascript:alert(1)'),null);assert.equal(safeLink('https://user:pass@example.org'),null);assert.equal(safeLink('https://example.org/a'),'https://example.org/a');
});
test('posts exactly once, no cookies or redirect following',async()=>{
 let calls=0;
 const answer=await sendMessage('https://example.org/chat','DEMO001','session',{fetchImpl:async(url,options)=>{calls++;assert.equal(options.credentials,'omit');assert.equal(options.redirect,'error');assert.deepEqual(JSON.parse(options.body),payload('DEMO001','session'));return new Response('[{"output":"3.5"}]');}});
 assert.equal(answer,'3.5');assert.equal(calls,1);
});
test('429 is actionable and never exposes server error text',async()=>{
 await assert.rejects(()=>sendMessage('https://example.org/chat','hola','session',{fetchImpl:async()=>new Response('private token: DO_NOT_SHOW',{status:429})}),error=>error.message.includes('minuto')&&!error.message.includes('DO_NOT_SHOW'));
});
test('invalid JSON and missing output give controlled errors',async()=>{
 for(const body of ['<script>alert(1)</script>','{"error":"private"}'])await assert.rejects(()=>sendMessage('https://example.org/chat','hola','session',{fetchImpl:async()=>new Response(body)}));
});
test('timeout aborts request and explains that backend could continue',async()=>{
 await assert.rejects(()=>sendMessage('https://example.org/chat','hola','session',{timeoutMs:10,fetchImpl:async(url,{signal})=>new Promise((resolve,reject)=>signal.addEventListener('abort',()=>reject(new DOMException('Aborted','AbortError'))))}),/podría seguir/);
});
test('manual cancellation is different from a network failure',async()=>{
 const controller=new AbortController();
 const result=sendMessage('https://example.org/chat','hola','session',{signal:controller.signal,fetchImpl:async(url,{signal})=>new Promise((resolve,reject)=>signal.addEventListener('abort',()=>reject(new DOMException('Aborted','AbortError'))))});
 controller.abort();await assert.rejects(()=>result,/cancelada/);
});
test('network/CORS failure provides a useful message',async()=>{
 await assert.rejects(()=>sendMessage('https://example.org/chat','hola','session',{fetchImpl:async()=>{throw new TypeError('Failed to fetch');}}),/CORS/);
});
