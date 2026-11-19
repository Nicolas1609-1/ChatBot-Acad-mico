import http.client
import json
import threading
from contextlib import contextmanager
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
import pytest
from server import chat_payload, upstream_url, RateLimiter, make_handler

URL="https://nicolas16.app.n8n.cloud/webhook/demo/chat"

@contextmanager
def server(forward=lambda url,payload:{"output":"promedio 3.5"}, configured=True):
    instance=ThreadingHTTPServer(("127.0.0.1",0),make_handler(URL if configured else "",{"localhost"},forward, student_url="https://nicolas16.app.n8n.cloud/webhook/sistemas-estudiante-demo", profile_forward=lambda url,payload:{"encontrado":payload["codigo"]=="U00100001","estudiante":{"codigo":payload["codigo"]}}))
    thread=threading.Thread(target=instance.serve_forever,daemon=True)
    thread.start()
    def request(method,path,body=None,headers=None):
        connection=http.client.HTTPConnection(*instance.server_address,timeout=5)
        connection.request(method,path,body,{"Host":"localhost",**(headers or {})})
        response=connection.getresponse()
        result=(response.status,response.read(),dict(response.getheaders()))
        connection.close()
        return result
    try: yield request
    finally: instance.shutdown();instance.server_close();thread.join(timeout=2)

def test_payload_strips_unknown_fields_and_forces_send_message():
    assert chat_payload({"chatInput":" Hola ","sessionId":"session-123456","action":"delete","url":"https://evil"})=={"chatInput":"Hola","sessionId":"session-123456","action":"sendMessage"}

@pytest.mark.parametrize("value",[None,[],{"chatInput":"","sessionId":"session-123456"},{"chatInput":"a"*6001,"sessionId":"session-123456"},{"chatInput":"hola","sessionId":"x';DROP"}])
def test_invalid_payload(value):
    with pytest.raises(ValueError):chat_payload(value)

def test_only_configured_n8n_instance_allowed():
    assert upstream_url(URL)==URL
    for invalid in ["http://nicolas16.app.n8n.cloud/chat","https://evil.example/chat","https://user:pass@nicolas16.app.n8n.cloud/chat","https://nicolas16.app.n8n.cloud/chat?key=abc"]:
        with pytest.raises(ValueError):upstream_url(invalid)

def test_rate_window_recovers():
    now=[0]
    limiter=RateLimiter(limit=2,window=60,clock=lambda:now[0])
    assert limiter.allow("client") and limiter.allow("client")
    assert not limiter.allow("client")
    now[0]=61
    assert limiter.allow("client")

def test_web_delivery_security_headers_and_fixed_proxy():
    seen=[]
    def forward(url,payload):seen.append((url,payload));return {"output":"3.5"}
    with server(forward) as request:
        status,body,headers=request("GET","/")
        assert status==200 and b"theme-coral.css" in body
        assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
        assert request("GET","/../server.py")[0]==404
        assert request("GET","/.env")[0]==404
        assert json.loads(request("GET","/api/config")[1])=={"serverConfigured":True}
        payload={"chatInput":"DEMO001","sessionId":"session-123456","extra":"do not forward"}
        request("POST","/api/student",json.dumps({"codigo":"U00100001","sessionId":"session-123456"}),{"Content-Type":"application/json"})
        status,body,_=request("POST","/api/chat",json.dumps(payload),{"Content-Type":"application/json","Origin":"http://localhost"})
        assert status==200 and json.loads(body)=={"output":"3.5"}
        assert seen==[(URL,{"chatInput":"Perfil seleccionado: U00100001\nConsulta: DEMO001","sessionId":"session-123456","action":"sendMessage"})]

def test_rejects_cross_origin_invalid_host_and_invalid_json():
    with server() as request:
        assert request("GET","/",headers={"Host":"evil.example"})[0]==403
        assert request("POST","/api/chat","{}",{"Content-Type":"application/json","Origin":"https://evil.example"})[0]==403
        assert request("POST","/api/chat","not-json",{"Content-Type":"application/json"})[0]==400
        assert request("POST","/api/chat","{}",{"Content-Type":"text/plain"})[0]==415

def test_masks_upstream_errors():
    def fail(url,payload):raise HTTPError(url,500,"PASSWORD_MUST_NOT_LEAK",None,None)
    with server(fail) as request:
        request("POST","/api/student",json.dumps({"codigo":"U00100001","sessionId":"session-123456"}),{"Content-Type":"application/json"})
        status,body,_=request("POST","/api/chat",json.dumps({"chatInput":"hola","sessionId":"session-123456"}),{"Content-Type":"application/json"})
        assert status==502 and b"PASSWORD_MUST_NOT_LEAK" not in body

def test_unconfigured_chat_is_not_fake_connected():
    with server(configured=False) as request:
        assert json.loads(request("GET","/api/config")[1])=={"serverConfigured":False}
        assert request("POST","/api/chat","{}",{"Content-Type":"application/json"})[0]==503


def test_identity_gate_and_unknown_code_do_not_call_chat():
    seen=[]
    with server(lambda url,payload:seen.append(payload) or {"output":"ok"}) as request:
        headers={"Content-Type":"application/json"}
        chat=json.dumps({"chatInput":"mi promedio", "sessionId":"session-123456"})
        assert request("POST","/api/chat",chat,headers)[0]==401
        assert request("POST","/api/student",json.dumps({"codigo":"DEMO001","sessionId":"session-123456"}),headers)[0]==400
        result=request("POST","/api/student",json.dumps({"codigo":"U00999999","sessionId":"session-123456"}),headers)
        assert result[0]==200 and not json.loads(result[1])["encontrado"]
        assert request("POST","/api/chat",chat,headers)[0]==401
        assert seen==[]


def test_mcp_requires_token_before_forwarding():
    with server() as request:
        status,body,_=request("POST","/mcp","{}",{"Content-Type":"application/json"})
        assert status==401
        assert b"Token MCP" in body
