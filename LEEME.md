# Chatbot academico de Sistemas - PC
## Abrir
https://academico.nicolas16.life/
Acceso HTTPS por Cloudflare. No requiere Tailscale para abrir el portal. Se abre en Chrome, Edge u otro navegador de PC.

## Ubicacion en el servidor
/home/nicolas/chatbot-academico
Servicio propio: chatbot-academico-web.service.
La interfaz vive en pc/dist y el servidor/proxy en pc/server.py.
No reemplaza los proyectos ni servicios anteriores.

## Estado actual
Web instalada y conectada a n8n Cloud. Promedio/avance, calendario y RAG probados desde la ruta del servidor. Las consultas y la logica academica siguen en n8n; PostgreSQL y Google Sheets conservan las fuentes.

Diseno activo: vidrio translucido, desenfoque, reflejos, bordes iluminados y barra lateral compacta. Referencia visual solicitada: https://www.instagram.com/reel/DfrtgFyTmOM/
Captura actual: verificacion/portal-vidrio-servidor.jpg.

El usuario autorizo explicitamente el endpoint demo publico de n8n sin contraseña. El portal de PC sigue limitado a Tailscale. Quien conozca la URL de n8n puede consultar los datos ficticios y consumir cuota de IA. No introducir datos reales.

Chatbot Academico y Sistemas - Actualizar noticias UNAB estan publicados. Los workflows de preparacion permanecen sin publicar. Todos estan en Personal > Sistemas - Trabajo final.

## Entregables y fuentes
- 10_DOCUMENTACION_TECNICA.md: arquitectura, datos y limites.
- 11_GUIA_DE_PRUEBAS_Y_VIDEO.md: preguntas y guion; el video NO se ha producido.
- 19_SERVIDOR_ACTUAL.md: operacion del servidor y autorizacion del endpoint.
- 20_DISENO_VIDRIO.md: alcance de la revision visual.
- 05, 06, 08, 09, 13 y 14: respaldos de los seis workflows; sin claves.
- 01 y 07: esquema academico y simulacion.
- 02, 03 y 04: fuentes del profesor y reglas ficticias.
- 15 y 16: preparacion SQL de noticias y RAG.

## Aplazado por el usuario
FastMCP: codigo y dependencias instalados, pero sin DATABASE_URL ni servicio activo; no conectado al agente.
Aplicación móvil: retomada el 18/11 en app-movil/ (Expo). Usa el mismo servidor y agente; ver app-movil/README.md.
Video: aplazado hasta aprobar el diseno.

No volver a ejecutar semillas o reindexaciones con cada consulta.

## Perfiles adicionales
U00100011: Laura, semestre 2, promedio 4.00, 13 créditos.
U00100012: Mateo, semestre 5, promedio 4.09, 54 créditos.
U00100013: Sofía, semestre 7, promedio 3.82, 81 créditos.
Son expedientes simulados; el código no es una contraseña.
