"""Private PC frontend and fixed n8n gateway. No SQL or model keys here."""
from __future__ import annotations
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
import json
import os
import re
import threading
import time

ROOT = Path(__file__).resolve().parent / "dist"
FILES = {"/": "index.html", "/index.html": "index.html", "/styles.css": "styles.css",
        "/theme-coral.css": "theme-coral.css", "/glass.css": "glass.css", "/app.js": "app.js", "/protocol.mjs": "protocol.mjs"}
MIME = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
        ".js": "text/javascript; charset=utf-8", ".mjs": "text/javascript; charset=utf-8"}

def chat_payload(value):
    if not isinstance(value, dict):
        raise ValueError("La consulta debe ser un objeto JSON.")
    text, session = value.get("chatInput"), value.get("sessionId")
    if not isinstance(text, str) or not 1 <= len(text.strip()) <= 6000:
        raise ValueError("Escribe entre 1 y 6000 caracteres.")
    if not isinstance(session, str) or not re.fullmatch(r"[A-Za-z0-9_-]{12,100}", session):
        raise ValueError("Sesion no valida. Inicia una nueva conversacion.")
    return {"action": "sendMessage", "chatInput": text.strip(), "sessionId": session}

def upstream_url(value):
    parsed = urlsplit(value)
    if parsed.scheme != "https" or parsed.hostname != "nicolas16.app.n8n.cloud" or parsed.username or parsed.password or parsed.query or parsed.fragment or not parsed.path.endswith("/chat"):
        raise ValueError("N8N_CHAT_URL debe apuntar al chat HTTPS de la instancia autorizada.")
    return value

class RateLimiter:
    def __init__(self, limit=12, window=60, clock=time.monotonic):
        self.limit, self.window, self.clock = limit, window, clock
        self.hits = defaultdict(deque)
        self.lock = threading.Lock()
    def allow(self, key):
        with self.lock:
            now = self.clock()
            for stale in list(self.hits):
                while self.hits[stale] and self.hits[stale][0] <= now - self.window:
                    self.hits[stale].popleft()
                if not self.hits[stale]:
                    del self.hits[stale]
            queue = self.hits[key]
            if len(queue) >= self.limit:
                return False
            queue.append(now)
            return True

def call_n8n(url, payload):
    request = Request(url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
    with urlopen(request, timeout=120) as response:
        raw = response.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise ValueError("Respuesta demasiado grande.")
    item = json.loads(raw)
    if isinstance(item, list) and len(item) == 1:
        item = item[0]
    if not isinstance(item, dict) or not isinstance(item.get("output"), str):
        raise ValueError("El flujo no devolvio output.")
    return {"output": item["output"]}

def student_code(value):
    if not isinstance(value, str) or not re.fullmatch(r"U00[0-9]{6}", value.strip().upper()):
        raise ValueError("Codigo no valido.")
    return value.strip().upper()

def call_profile(url, payload):
    request = Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type":"application/json"}, method="POST")
    with urlopen(request, timeout=30) as response:
        result=json.loads(response.read(100000))
    if not isinstance(result, dict) or not isinstance(result.get("encontrado"), bool):
        raise ValueError("Perfil no valido.")
    return result

def make_handler(chat_url, allowed_hosts, forward=call_n8n, student_url="", profile_forward=call_profile):
    limiter = RateLimiter()
    active = threading.BoundedSemaphore(1)
    sessions = {}
    sessions_lock = threading.Lock()
    class Handler(BaseHTTPRequestHandler):
        server_version = "SistemasPC"
        def log_message(self, fmt, *args):
            # Never log request bodies, session IDs, credentials or upstream errors.
            print("%s %s" % (self.command, self.path.split("?")[0]), flush=True)
        def _headers(self, status, content_type, size):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(size))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self' https:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
            self.end_headers()
        def _json(self, status, value):
            raw = json.dumps(value, ensure_ascii=False).encode("utf-8")
            self._headers(status, "application/json; charset=utf-8", len(raw))
            if self.command != "HEAD":
                self.wfile.write(raw)
        def _host_ok(self):
            return self.headers.get("Host", "") in allowed_hosts
        def do_HEAD(self):
            self.do_GET()
        def do_GET(self):
            if not self._host_ok():
                return self._json(403, {"error": "Host no permitido."})
            path = urlsplit(self.path).path
            if path == "/health":
                return self._json(200, {"status": "ok", "application": "sistemas-pc", "serverConfigured": bool(chat_url)})
            if path == "/api/config":
                return self._json(200, {"serverConfigured": bool(chat_url)})
            name = FILES.get(path)
            if not name:
                return self._json(404, {"error": "No encontrado."})
            raw = (ROOT / name).read_bytes()
            self._headers(200, MIME[Path(name).suffix], len(raw))
            if self.command != "HEAD":
                self.wfile.write(raw)
        def _mcp_proxy(self):
            # Fixed loopback destination. Bearer verification belongs to FastMCP.
            if not self.headers.get("Authorization", "").startswith("Bearer "):
                return self._json(401, {"error":"Token MCP requerido."})
            try:
                size=int(self.headers.get("Content-Length","0"))
                if not 0 < size <= 64000:
                    return self._json(413,{"error":"Solicitud MCP demasiado grande o vacia."})
                headers={key:self.headers[key] for key in ("Authorization","Content-Type","Accept","MCP-Protocol-Version") if key in self.headers}
                request=Request("http://127.0.0.1:9000/mcp",data=self.rfile.read(size),headers=headers,method="POST")
                try:
                    response=urlopen(request,timeout=30)
                except HTTPError as exc:
                    response=exc
                with response:
                    body=response.read(1024*1024+1)
                    if len(body)>1024*1024:
                        return self._json(502,{"error":"Respuesta MCP demasiado grande."})
                    self._headers(response.code,response.headers.get("Content-Type","application/json"),len(body))
                    self.wfile.write(body)
            except (ValueError,URLError,TimeoutError,OSError):
                return self._json(502,{"error":"Servicio MCP no disponible."})

        def do_POST(self):
            if not self._host_ok():
                return self._json(403, {"error": "Host no permitido."})
            path = urlsplit(self.path).path
            if path == "/mcp":
                origin=self.headers.get("Origin")
                if origin and urlsplit(origin).netloc != self.headers.get("Host"):
                    return self._json(403,{"error":"Origen no permitido."})
                return self._mcp_proxy()
            if path not in ("/api/chat", "/api/student"):
                return self._json(404, {"error": "No encontrado."})
            origin = self.headers.get("Origin")
            if origin and urlsplit(origin).netloc != self.headers.get("Host"):
                return self._json(403, {"error": "Origen no permitido."})
            if not chat_url:
                return self._json(503, {"error": "Chat no configurado."})
            if self.headers.get_content_type() != "application/json":
                return self._json(415, {"error": "Usa application/json."})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 40000:
                    return self._json(413, {"error": "Solicitud demasiado grande o vacia."})
                value = json.loads(self.rfile.read(size))
                if path == "/api/student":
                    code = student_code(value.get("codigo"))
                    payload = chat_payload({"chatInput":"perfil", "sessionId":value.get("sessionId")})
                else:
                    payload = chat_payload(value)
            except (ValueError, UnicodeError):
                return self._json(400, {"error": "Consulta o sesion no valida."})
            if not limiter.allow(self.client_address[0]):
                return self._json(429, {"error": "Limite temporal de consultas."})
            if not active.acquire(blocking=False):
                return self._json(429, {"error": "Hay una consulta en curso; espera a que termine."})
            try:
                if path == "/api/student":
                    if not student_url:
                        return self._json(503, {"error":"Consulta de expedientes no configurada."})
                    result = profile_forward(student_url, {"codigo":code})
                    with sessions_lock:
                        now=time.monotonic()
                        for key in list(sessions):
                            if sessions[key][1] < now-7200:
                                del sessions[key]
                        if result.get("encontrado") and result.get("estudiante",{}).get("codigo") == code:
                            sessions[payload["sessionId"]]=(code,now)
                        else:
                            sessions.pop(payload["sessionId"],None)
                    return self._json(200,result)
                with sessions_lock:
                    selected=sessions.get(payload["sessionId"])
                if not selected or selected[1] < time.monotonic()-7200:
                    return self._json(401,{"error":"Selecciona primero tu codigo de estudiante."})
                payload["chatInput"]="Perfil seleccionado: "+selected[0]+"\nConsulta: "+payload["chatInput"]
                result = forward(chat_url, payload)
                return self._json(200, result)
            except HTTPError as exc:
                return self._json(429 if exc.code == 429 else 502, {"error": "n8n no pudo completar la consulta."})
            except (URLError, TimeoutError, ValueError, OSError):
                return self._json(502, {"error": "No se pudo consultar n8n."})
            finally:
                active.release()
    return Handler

if __name__ == "__main__":
    bind = os.environ.get("APP_BIND", "127.0.0.1")
    port = int(os.environ.get("APP_PORT", "8091"))
    chat = os.environ.get("N8N_CHAT_URL", "")
    if chat:
        chat = upstream_url(chat)
    student_url = os.environ.get("N8N_STUDENT_URL", "")
    if student_url and student_url != "https://nicolas16.app.n8n.cloud/webhook/sistemas-estudiante-demo":
        raise ValueError("Endpoint de expedientes no permitido.")
    hosts = set(os.environ.get("APP_ALLOWED_HOSTS", f"{bind}:{port},127.0.0.1:{port},localhost:{port}").split(","))
    server = ThreadingHTTPServer((bind, port), make_handler(chat, hosts, student_url=student_url))
    print(f"Sistemas PC iniciado en {bind}:{port}; chat configurado: {bool(chat)}", flush=True)
    server.serve_forever()
