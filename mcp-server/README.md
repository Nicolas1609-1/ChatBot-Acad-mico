# FastMCP académico

Servicio activo: chatbot-academico-mcp.service. Endpoint HTTPS: https://academico.nicolas16.life/mcp. Backend escucha solo en 127.0.0.1:9000; el proxy fijo de la web transmite las solicitudes autenticadas.

Usuario PostgreSQL dedicado academico_mcp_reader, sin superusuario, creación de roles/bases ni BYPASSRLS. SELECT sobre las tablas y vistas académicas y EXECUTE sobre la función de proyección. La sesión aplica solo lectura y timeout de cinco segundos. TLS verify-full con CA de Supabase. Contraseña generada y guardada solo en deploy/mcp.env, modo 600. PostgreSQL recibió un verificador SCRAM, no la contraseña en texto.

Herramientas: consultar_expediente, consultar_plan_sistemas, proyectar_semestres y consultar_noticias_sistemas. Códigos públicos U00 + seis dígitos; 13 perfiles existentes. SQL fijo parametrizado, sin aceptar SQL libre.

Autenticación bearer: solo hash SHA-256 en el servicio. Token privado del cliente: /home/nicolas/chatbot-academico/deploy/mcp-client-token. No incluirlo en documentación, Git, ZIP o chat.

Verificado contra la base real: expediente Ana 3.5/22 créditos; proyección seis periodos; plan 32 materias; noticias; INSERT no permitido. Cliente FastMCP sobre HTTPS descubrió las cuatro herramientas y obtuvo promedio 4.09 de U00100012. Sin token: HTTP 401. 14 verificaciones de protocolo y autenticación pasan.

Último paso pendiente: crear credencial Bearer Auth en n8n y asignarla al nodo deshabilitado MCP academico - pendiente credencial. Después habilitarlo y sustituir las herramientas de plan/noticias por las MCP. Conservar expediente/proyección SQL que vinculan el código al perfil del portal. Repetir una consulta real antes de publicar. El flujo actualmente publicado sigue usando sus herramientas verificadas anteriores.


## Cierre del 15 de noviembre de 2026
Credencial Bearer Auth validada por n8n. Cliente MCP habilitado y flujo principal publicado con 19 nodos. Plan y noticias se consultan por MCP; expediente y proyección conservan SQL vinculado al perfil. La ejecución 63 confirmó noticias vía MCP; la 64 confirmó el expediente personal. Consulta real por Cloudflare completada después de publicar. No queda pendiente la conexión MCP. Informe final disponible en Informe_final_Chatbot_Academico.pdf. Video aplazado; app móvil cancelada.
