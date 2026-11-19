"""Fixed read-only queries; no endpoint accepts SQL or table names."""
from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from typing import Any
import re
import psycopg
from psycopg.rows import dict_row
import queries

def codigo_demo(value: str) -> str:
    code = value.strip().upper()
    if not re.fullmatch(r"U00[0-9]{6}", code):
        raise ValueError("Usa U00 seguido de seis numeros.")
    return code

def json_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {key: json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    return value

class AcademicRepository:
    def __init__(self, dsn: str):
        self.dsn = dsn

    def _read(self, query: str, params: dict | None = None) -> dict:
        with psycopg.connect(self.dsn, connect_timeout=5, row_factory=dict_row,
                options="-c default_transaction_read_only=on -c statement_timeout=5000") as connection:
            with connection.transaction():
                connection.execute("SET TRANSACTION READ ONLY")
                row = connection.execute(query, params).fetchone()
                return json_value(row or {})

    def expediente(self, codigo: str, detalle: str = "resumen") -> dict:
        if detalle not in {"resumen", "historial", "pendientes", "completo"}:
            raise ValueError("Detalle no reconocido.")
        return self._read(queries.EXPEDIENTE, {"codigo": codigo_demo(codigo), "detalle": detalle})

    def plan(self) -> dict:
        return self._read(queries.PLAN)

    def proyeccion(self, codigo: str) -> dict:
        return self._read(queries.PROYECCION, {"codigo": codigo_demo(codigo)})

    def noticias(self) -> dict:
        return self._read(queries.NOTICIAS)
