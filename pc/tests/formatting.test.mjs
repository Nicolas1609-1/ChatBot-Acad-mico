import {test} from 'node:test';
import assert from 'node:assert/strict';
import {inlineParts} from '../dist/protocol.mjs';
test('preserves the professors source URLs with parentheses',()=>{
  const url='https://github.com/adiacla/clima-Biing26-UCC-Ibague/blob/version/Propuesta%20(1).md';
  const links=inlineParts('Fuente: [Propuesta]('+url+')').filter(part=>part.kind==='link');
  assert.deepEqual(links,[{kind:'link',text:'Propuesta',href:url}]);
});
test('HTML remains plain text and javascript never becomes a link',()=>{
  const parts=inlineParts('<script>alert(1)</script> [ver](javascript:alert(1))');
  assert.equal(parts.filter(part=>part.kind==='link').length,0);
  assert.equal(parts.map(part=>part.text).join(''),'<script>alert(1)</script> [ver](javascript:alert(1))');
});
test('bold and ordinary HTTPS links stay distinct',()=>{
  const parts=inlineParts('Promedio **3.5**. Ver https://example.org/a.');
  assert.equal(parts.find(part=>part.kind==='strong').text,'3.5');
  assert.equal(parts.find(part=>part.kind==='link').href,'https://example.org/a');
});
