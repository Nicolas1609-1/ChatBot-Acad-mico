import asyncio
import hashlib
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch
import pytest
import psycopg
from fastmcp import Client
from starlette.testclient import TestClient
from server import Settings, HashedBearerVerifier, build_server
from repository import AcademicRepository, codigo_demo, json_value
import queries

TOKEN = "token-sintetico-solo-pruebas-0000000000000000"
HASH = hashlib.sha256(TOKEN.encode()).hexdigest()

class FakeRepository:
    def expediente(self, codigo, detalle="resumen"):
        return {"codigo": codigo, "resumen": {"promedio_historico": 3.5}, "detalle": detalle, "datos_sinteticos": True}
    def plan(self): return {"creditos":110}
    def proyeccion(self, codigo): return {"codigo":codigo, "semestres_simulados":6}
    def noticias(self): return {"noticias":[],"cache_desactualizada":True}

@pytest.mark.parametrize("value", ["U00100001", "u00100013", " U00100005 "])
def test_normalizes_only_demo_codes(value):
    assert codigo_demo(value).startswith("U00")

@pytest.mark.parametrize("value", ["DEMO000", "U0010001", "123", "DEMO001'; DROP TABLE estudiantes;--", "DEMO001\nSELECT 1"])
def test_rejects_other_codes(value):
    with pytest.raises(ValueError): codigo_demo(value)

def test_token_hash_verification():
    verifier=HashedBearerVerifier(HASH)
    assert asyncio.run(verifier.verify_token(TOKEN)).scopes == ["academico:read"]
    assert asyncio.run(verifier.verify_token("incorrecto"*8)) is None
    assert asyncio.run(verifier.verify_token("corto")) is None
    with pytest.raises(ValueError): HashedBearerVerifier("")

def test_real_mcp_discovery_and_call_without_database():
    async def scenario():
        async with Client(build_server(Settings("test",HASH),FakeRepository())) as client:
            tools=await client.list_tools()
            names={tool.name for tool in tools}
            assert names == {"consultar_expediente","consultar_plan_sistemas","proyectar_semestres","consultar_noticias_sistemas"}
            for tool in tools: assert tool.annotations.read_only_hint is True
            result=await client.call_tool("consultar_expediente",{"codigo":"u00100001","detalle":"resumen"})
            assert result.data["resumen"]["promedio_historico"] == 3.5
            assert result.data["codigo"] == "U00100001"
            with pytest.raises(Exception):
                await client.call_tool("consultar_expediente",{"codigo":"DEMO001'; DELETE","detalle":"resumen"})
    asyncio.run(scenario())

def test_http_authentication_before_initialization():
    app=build_server(Settings("test",HASH),FakeRepository()).http_app(json_response=True,stateless_http=True)
    payload={"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"tests","version":"1"}}}
    headers={"Accept":"application/json, text/event-stream"}
    with TestClient(app,base_url="http://localhost") as client:
        assert client.post("/mcp",json=payload,headers=headers).status_code == 401
        assert client.post("/mcp",json=payload,headers={**headers,"Authorization":"Bearer "+("invalid"*8)}).status_code == 401
        valid=client.post("/mcp",json=payload,headers={**headers,"Authorization":"Bearer "+TOKEN})
        assert valid.status_code == 200
        assert "result" in valid.json()

def test_readonly_transaction_and_bound_parameters():
    connection=MagicMock()
    connection.__enter__.return_value=connection
    connection.transaction.return_value.__enter__.return_value=None
    connection.execute.return_value.fetchone.return_value={"nota":Decimal("3.50")}
    with patch("repository.psycopg.connect",return_value=connection) as connect:
        result=AcademicRepository("placeholder").expediente("u00100001","resumen")
    assert result == {"nota":3.5}
    assert "default_transaction_read_only=on" in connect.call_args.kwargs["options"]
    assert connection.execute.call_args_list[0].args == ("SET TRANSACTION READ ONLY",)
    assert connection.execute.call_args_list[1].args == (queries.EXPEDIENTE,{"codigo":"U00100001","detalle":"resumen"})
    assert "U00100001" not in queries.EXPEDIENTE

def test_never_leaks_database_exception_to_client():
    class Broken(FakeRepository):
        def plan(self): raise psycopg.OperationalError("password=THIS_MUST_NOT_LEAK")
    async def scenario():
        async with Client(build_server(Settings("test",HASH),Broken())) as client:
            with pytest.raises(Exception) as exc:
                await client.call_tool("consultar_plan_sistemas",{})
            assert "THIS_MUST_NOT_LEAK" not in str(exc.value)
            assert "no respondio" in str(exc.value)
    asyncio.run(scenario())

def test_json_conversion_preserves_missing_values():
    stamp=datetime(2026,11,14,tzinfo=timezone.utc)
    assert json_value({"fecha":stamp,"v":[Decimal("3.5"),None]}) == {"fecha":stamp.isoformat(),"v":[3.5,None]}
