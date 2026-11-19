"""Internal service-to-service MCP for synthetic Systems Engineering data."""
from __future__ import annotations
import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from typing import Literal
import psycopg
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.auth import AccessToken, TokenVerifier
from repository import AcademicRepository, codigo_demo

class HashedBearerVerifier(TokenVerifier):
    def __init__(self, expected_hash: str):
        super().__init__(required_scopes=["academico:read"])
        if not re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash):
            raise ValueError("MCP_TOKEN_SHA256 debe ser un hash SHA-256 hexadecimal.")
        self.expected_hash = expected_hash.lower()

    async def verify_token(self, token: str) -> AccessToken | None:
        if len(token) < 32:
            return None
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        if not hmac.compare_digest(digest, self.expected_hash):
            return None
        return AccessToken(token=token, client_id="n8n-academico",
                           scopes=["academico:read"], subject="n8n-academico")

@dataclass(frozen=True)
class Settings:
    database_url: str
    token_hash: str
    host: str = "127.0.0.1"
    port: int = 9000

    @classmethod
    def from_env(cls) -> "Settings":
        dsn = os.environ.get("DATABASE_URL", "")
        if not dsn:
            raise ValueError("Falta DATABASE_URL; el servidor no arranca sin configuracion.")
        return cls(dsn, os.environ.get("MCP_TOKEN_SHA256", ""),
                   os.environ.get("MCP_HOST", "127.0.0.1"),
                   int(os.environ.get("MCP_PORT", "9000")))

def build_server(settings: Settings, repository=None) -> FastMCP:
    repository = repository if repository is not None else AcademicRepository(settings.database_url)
    mcp = FastMCP("Apoyo academico - Sistemas",
        instructions="Solo datos sinteticos. Las herramientas consultan; no modifican notas ni matriculas. El token identifica al servicio n8n, no autentica a un alumno real.",
        auth=HashedBearerVerifier(settings.token_hash))
    annotations = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}

    def read(method, *args):
        try:
            return method(*args)
        except ValueError as exc:
            raise ToolError(str(exc)) from None
        except psycopg.Error:
            raise ToolError("La fuente academica no respondio. No hay resultados confirmados; intenta mas tarde.") from None

    @mcp.tool(annotations=annotations)
    def consultar_expediente(codigo: str, detalle: Literal["resumen", "historial", "pendientes", "completo"] = "resumen") -> dict:
        """Consulta matricula, promedio/avance y el detalle solicitado para U00100001-U00100013. Datos sinteticos."""
        try:
            code = codigo_demo(codigo)
        except ValueError as exc:
            raise ToolError(str(exc)) from None
        return read(repository.expediente, code, detalle)

    @mcp.tool(annotations=annotations)
    def consultar_plan_sistemas() -> dict:
        """Plan ficticio de Sistemas, 32 materias/110 creditos, prerrequisitos y ejemplos. No es un plan oficial."""
        return read(repository.plan)

    @mcp.tool(annotations=annotations)
    def proyectar_semestres(codigo: str) -> dict:
        """Proyeccion con prerrequisitos, maximo 18 creditos, incluye periodo actual; supone aprobar todo y oferta continua."""
        try:
            code = codigo_demo(codigo)
        except ValueError as exc:
            raise ToolError(str(exc)) from None
        return read(repository.proyeccion, code)

    @mcp.tool(annotations=annotations)
    def consultar_noticias_sistemas() -> dict:
        """Noticias oficiales UNAB guardadas, con fecha, enlace y marca de actualizacion. No confirma cupos ni inscripciones."""
        return read(repository.noticias)

    return mcp

if __name__ == "__main__":
    settings = Settings.from_env()
    build_server(settings).run(transport="http", host=settings.host, port=settings.port, stateless_http=True, json_response=True)
