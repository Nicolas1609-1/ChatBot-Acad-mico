# Servidor instalado
Fecha: 14 de noviembre de 2026.
Servidor: nicolas-server. Usuario: nicolas.
Ruta: /home/nicolas/chatbot-academico.
Acceso PC: http://100.74.216.15:8091/ mediante Tailscale.

## Componentes
- pc/server.py: archivos estaticos y proxy fijo a n8n.
- pc/dist/: interfaz.
- deploy/app.env: configuracion del servicio, permiso 600. No contiene claves Groq ni contrasenas PostgreSQL.
- ~/.config/systemd/user/chatbot-academico-web.service: servicio habilitado.
- mcp-server/.venv: dependencias FastMCP instaladas; sin servicio activo.
- SQL, documentos y seis respaldos de workflows en la carpeta del proyecto.

## Autorizacion y acceso
El usuario confirmo literalmente "Si, autorizo el endpoint demo publico" tras ser informado de que quien conozca la URL puede consultar datos ficticios y consumir cuota IA.
Se habilito y publico el Chat Trigger de Chatbot Academico en modo webhook con respuesta del ultimo nodo. No se exportaron credenciales n8n al navegador.
El acceso web del servidor permanece privado por Tailscale. El endpoint de n8n es publico sin contraseña y esa limitacion sigue vigente.
Los flujos de preparacion no se publicaron. La actualizacion de noticias si esta publicada, con el horario diario preparado.

## Aislamiento
Se uso el puerto 8091 libre y una unidad nueva. Se comprobo que primerpaso-tunnel, samurai-web y verdant-preview seguian activos. No se cambio configuracion Docker, tuneles o proyectos anteriores.
El proxy admite solo el host autorizado, JSON de consulta limitado, una consulta concurrente y 12 intentos por minuto por direccion. No expone archivos del proyecto fuera de la lista estatica.
El servicio no registra el texto de las consultas ni valores de sesion.

## Estado restante
FastMCP, movil/Expo y video aplazados por el usuario. No se genero video.
Los limites de Groq pueden producir un aviso de indisponibilidad; datos reales requieren autenticacion y autorizacion adicionales.
