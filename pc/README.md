# Portal de PC
Web activa: http://100.74.216.15:8091/ . Requiere Tailscale.
Carpeta remota: /home/nicolas/chatbot-academico/pc.

## Uso
Escribir una consulta o elegir una tarjeta. Ejemplos:
- Soy DEMO001. Cual es mi promedio y mi avance?
- Soy DEMO001. Cuantos semestres me faltan?
- Cuando comienzan las clases de 2027-1?
- Cuales son los tres pilares de competencias digitales segun el profesor?

La conexion se administra en el servidor. No hay que pegar URLs ni claves.
El proxy fija el destino n8n, valida la entrada y limita las consultas concurrentes. Los calculos academicos y el agente permanecen en n8n.
Todo expediente/calendario es ficticio. No hay login de alumnos reales ni cambios de matricula.

## Diseno
Vidrio translucido, desenfoque de fondo, reflejos diagonales, bordes iluminados y rail lateral compacto.
CSS en dist/glass.css, sobre la base de dist/styles.css y dist/theme-coral.css.
No se ejecuta HTML de respuestas. Los enlaces HTTPS y tablas se crean mediante DOM; URLs con parentesis conservan su ruta.

## Operacion
Servicio: systemctl --user status chatbot-academico-web.service
Reiniciar: systemctl --user restart chatbot-academico-web.service
Registro: journalctl --user -u chatbot-academico-web.service
Configuracion privada: /home/nicolas/chatbot-academico/deploy/app.env
El servicio escucha solo en 100.74.216.15:8091. No se cambio el resto de servicios.
La URL demo de n8n es publica sin contraseña por autorizacion expresa; el portal Tailscale no hace privada esa URL de n8n.

## Desarrollo local
Con Node.js: npm run start y abrir http://127.0.0.1:4173, o ejecutar Abrir_PC.cmd.
No necesita npm install.
El servidor Node es solo una vista local. La version instalada usa Python server.py y el proxy /api/chat.
El archivo deploy_install.py valida las rutas del paquete y solo instala este proyecto y su unidad de usuario.

## Verificacion
npm run check; npm test: 15 pruebas.
Python pytest tests/test_gateway.py: 12 pruebas.
Pruebas reales por el servidor: promedio 3.5, avance 20%, calendario 25 de enero de 2027 y RAG con cita.
La sesion UUID funciona tambien en HTTP privado con crypto.getRandomValues.
Los mensajes visibles no se guardan en disco. Nueva conversacion cambia la UUID; no borra memoria antigua de n8n.
