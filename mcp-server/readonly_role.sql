-- Provisionar con el administrador. No ejecutar automaticamente.
-- Crear rol y contraseña por un canal privado; no poner la contraseña en este archivo.
-- El ejemplo requiere que el rol mcp_reader ya exista y sea LOGIN.
GRANT USAGE ON SCHEMA academico_demo TO mcp_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA academico_demo TO mcp_reader;
GRANT EXECUTE ON FUNCTION academico_demo.proyectar_semestres(text,integer) TO mcp_reader;
ALTER ROLE mcp_reader SET default_transaction_read_only = on;
ALTER ROLE mcp_reader SET statement_timeout = '5s';
-- Revisar que mcp_reader no herede roles de escritura y que no tenga BYPASSRLS/superuser.
-- No necesita acceso a la memoria ni a las credenciales de n8n.
