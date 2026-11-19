# Panel azul y selección de expediente

El portal solicita U00 seguido de seis dígitos antes de mostrar el chat. Ejemplos ficticios: U00100001 (Ana), U00100002 (Bruno). Los diez códigos terminan en 100001 a 100010.

El perfil se consulta directamente en PostgreSQL mediante una rama del mismo flujo principal de n8n; no se usa IA para obtener las cifras del panel. El código no determina el semestre: este se lee del expediente. La columna codigo_institucional conserva las claves internas DEMO y sus relaciones sin cambiar notas.

El servidor vincula una sesión temporal con el código validado. El cliente no puede elegir otro expediente dentro del cuerpo del chat. Cambiar estudiante renueva la sesión y borra los mensajes visibles. Las herramientas personales usan el código seleccionado, incluso si el texto solicita otro. La sesión caduca a las dos horas y al reiniciar el servicio; vuelve a seleccionar el código.

Esto selecciona datos sintéticos, no autentica estudiantes reales. Para datos reales hará falta autenticación institucional.

N8N_STUDENT_URL=https://nicolas16.app.n8n.cloud/webhook/sistemas-estudiante-demo

Instalación nueva: ejecutar 01_base_academica.sql y después 21_codigos_estudiante.sql. No volver a sembrar la base existente: conservar las notas de demostración modificadas durante las pruebas.
