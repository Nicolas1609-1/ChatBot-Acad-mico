# Estado del proyecto - 14 de noviembre de 2026
Alcance activo: PC. FastMCP y video pendientes; aplicación móvil cancelada por el usuario.

## Instalado
- Carpeta remota: /home/nicolas/chatbot-academico.
- Web privada: http://100.74.216.15:8091/ (Tailscale).
- Servicio de usuario chatbot-academico-web.service habilitado, activo y con reinicio ante fallos.
- Los servicios primerpaso-tunnel, samurai-web y verdant-preview se comprobaron activos despues de instalarlo.
- No se uso sudo, no se reemplazaron proyectos existentes ni se publico el puerto en Internet.

## n8n
- Chatbot Academico, D8bc4f0Jt7tgJzeU: publicado; 18 nodos.
- Actualizacion de noticias, f5xfhE6WJaWYF1Dv: publicada; horario diario 08:00 America/Bogota.
- Preparacion de base, funcion de proyeccion, RAG y calendario: manuales, sin publicar.
- El usuario autorizo explicitamente el endpoint demo publico sin autenticacion tras explicar su alcance y consumo de cuota.
- La revision automatica bloqueo la primera habilitacion; despues de la autorizacion explicita, la misma accion fue aceptada.
- PostgreSQL contiene 10 estudiantes ficticios, 32 materias y 110 creditos; memoria persistente.
- RAG: 96 fragmentos, embeddings 1536 dimensiones, tres resultados por consulta. Maximo una busqueda documental por mensaje; ventana de memoria de dos interacciones para reducir TPM.
- Groq conserva su cuota de 8000 tokens/minuto; hay reintentos y respuesta de indisponibilidad. No se promete eliminar el limite.

## Evidencia
- 14: verificaciones de cobertura, prerrequisitos, carga y ausencia de duplicados para diez estudiantes.
- 16/17: noticias cargadas y actualizacion idempotente (seis registros).
- 19/20: clave ficticia y mensaje largo rechazados antes del agente.
- 24: calendario Google Sheets leido.
- 30/34: promedio 3.5 y seis periodos simulados, con supuestos.
- 35-37: consultas reales a traves del servidor, incluyendo calendario y promedio/avance. Captura chat-servidor-real.jpg.
- 38: se alcanzo cuota Groq en una busqueda RAG repetida; se ajustaron recuperacion y memoria.
- 39: RAG desde el portal respondio los tres pilares y el enlace exacto al documento despues del ajuste.
- PC: 15 pruebas de protocolo/formato y 12 del proxy, sin fallos.
- Revision visual final de vidrio: interfaz, navegacion y panel de fuentes; CSS HTTP 200 y backend configurado.

## Aplazados
- FastMCP instalado en entorno aislado del servidor; sin credencial PostgreSQL de lectura, sin servicio activo ni conexion al agente. El usuario eligio dejarlo para despues.
- Aplicación móvil cancelada y carpetas android/entregables eliminadas. Video pendiente.
- No hay autenticacion real de alumnos; los codigos DEMO solo seleccionan casos ficticios.

## Diseno
Se reviso el reel https://www.instagram.com/reel/DfrtgFyTmOM/.
Tras la aclaracion del usuario se aplico vidrio translucido con reflejos, fondo difuminado, bordes claros y rail lateral oscuro. El diseno se puede revisar en la URL del servidor.


Actualización 14/11: diseño de vidrio azul y entrada obligatoria con código U00 + seis dígitos. Perfiles y sesión vinculados en el servidor; ver 22_IDENTIFICACION_Y_AZUL.md. Verificado con Ana (3.50/22 créditos) y Bruno (4.01/40). 15 pruebas JS y 13 pruebas gateway aprobadas.

Publicación por Cloudflare solicitada. cloudflared ya está instalado; falta seleccionar dominio y configurar una ruta propia para el chatbot sin modificar las aplicaciones existentes.

Cloudflare verificado: https://academico.nicolas16.life/health devuelve estado ok y backend configurado. Tres nuevos perfiles consultados vía HTTPS: U00100011 (4.00/13 créditos), U00100012 (4.09/54), U00100013 (3.82/81). Total 13. FastMCP pendiente de conexión de solo lectura; se recomendó activarlo al usuario.

FastMCP activo: servicio chatbot-academico-mcp.service, HTTPS /mcp, rol dedicado de solo lectura y TLS validado. Lecturas reales y protocolo autenticado verificados. 14 pruebas MCP y 14 gateway aprobadas. Pendiente credencial Bearer Auth de n8n; nodo preparado deshabilitado en borrador, versión publicada conservada.


## Cierre del 15 de noviembre de 2026
Credencial Bearer Auth validada por n8n. Cliente MCP habilitado y flujo principal publicado con 19 nodos. Plan y noticias se consultan por MCP; expediente y proyección conservan SQL vinculado al perfil. La ejecución 63 confirmó noticias vía MCP; la 64 confirmó el expediente personal. Consulta real por Cloudflare completada después de publicar. No queda pendiente la conexión MCP. Informe final disponible en Informe_final_Chatbot_Academico.pdf. Video aplazado; app móvil cancelada.


## Actualizacion del 18 de noviembre de 2026
- App movil retomada en app-movil/ (Expo, React Native). Usa /api/student y /api/chat del proxy; reintenta sola ante el limite de Groq (40 s y 60 s).
- Revision de ejecuciones 69-100 del Chatbot Academico. Ajustes publicados (version b9f06ead): aviso de simulacion solo en proyecciones; "proximo semestre" usa el periodo 2 de Proyectar semestres; herramienta obligatoria en cada turno; noticias reales con fecha de actualizacion; maxTokensFromMemory=1200.
- Verificado por HTTPS con U00100012: proximo semestre (S602, S603, S604, S703, S701; 18 creditos), promedio 4.09/54/49.09 %, noticias y calendario 2027-1.
- Respaldo del flujo con estos cambios: 28_respaldo_ajustes_18nov.json.
- Limite Groq 8000 TPM sigue vigente: preguntas muy seguidas pueden recibir el aviso de indisponibilidad.

- Video de demostracion grabado sobre el portal real (U00100012, seis preguntas, ~3 min): docs/video/demo-chatbot-academico.mp4. README con capturas en docs/img.
- 19/11: el calendario cita siempre el enlace de la hoja (version 5522aab4). Repositorio: github.com/Nicolas1609-1/ChatBot-Acad-mico.
- 19/11: reintento automatico en n8n (If + Wait 45 s, una vez) ante limite de Groq; herramientas personales leen el perfil con first(). Version bf239077. Probado: rafaga de 5 preguntas, la 5a se recupero sola en 54 s con datos correctos.
