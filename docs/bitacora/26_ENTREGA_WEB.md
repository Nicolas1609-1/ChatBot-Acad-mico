# Entrega web académica

URL: https://academico.nicolas16.life/
Servidor: /home/nicolas/chatbot-academico
Servicio: chatbot-academico-web.service
Frontend: pc/dist. Consultas y agente: n8n Cloud. Datos: PostgreSQL/Supabase, Google Sheets y noticias UNAB.

Perfiles disponibles: U00100001 a U00100013. Nuevos: Laura U00100011 (semestre 2); Mateo U00100012 (5); Sofía U00100013 (7).

Completado: portal de vidrio azul, entrada por código, perfiles, memoria, RAG, calendario, noticias, proyección con prerrequisitos, guardrails, despliegue y Cloudflare. Documentación y respaldos actualizados.

FastMCP activo y probado por HTTPS con PostgreSQL de solo lectura. Pendiente únicamente guardar el token como credencial Bearer Auth de n8n y habilitar el nodo cliente tras verificarlo. Video aplazado. App móvil cancelada y eliminada. La publicación no convierte los datos simulados en datos oficiales ni agrega autenticación real.


## Cierre del 15 de noviembre de 2026
Credencial Bearer Auth validada por n8n. Cliente MCP habilitado y flujo principal publicado con 19 nodos. Plan y noticias se consultan por MCP; expediente y proyección conservan SQL vinculado al perfil. La ejecución 63 confirmó noticias vía MCP; la 64 confirmó el expediente personal. Consulta real por Cloudflare completada después de publicar. No queda pendiente la conexión MCP. Informe final disponible en Informe_final_Chatbot_Academico.pdf. Video aplazado; app móvil cancelada.


## Actualización del 18 de noviembre de 2026
La app móvil se retomó en app-movil/ (Expo, React Native) y usa el mismo proxy y agente que la web. Informe PDF regenerado con la app incluida. Ver ESTADO_DEL_PROYECTO.md.
