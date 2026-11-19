import {test} from 'node:test';
import assert from 'node:assert/strict';
import {endpoint,createSessionId} from '../dist/protocol.mjs';
test('allows only the fixed same-origin server chat route',()=>{
  assert.equal(endpoint('/api/chat'),'/api/chat');
  for(const route of ['/other','//example.org/chat','/api/chat?url=https://other'])assert.throws(()=>endpoint(route));
});
test('session generation works on private HTTP without randomUUID',()=>{
  const id=createSessionId({getRandomValues(bytes){bytes.fill(7);return bytes;}});
  assert.match(id,/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/);
  assert.equal(createSessionId({randomUUID(){return 'native-id';}}),'native-id');
});
