# Avance Android y MCP - 14 de noviembre de 2026

Nota: registro historico previo al despliegue del portal PC. El estado actual es 19_SERVIDOR_ACTUAL.md. FastMCP, telefono/Expo y video quedaron aplazados por el usuario.

## Android
Codigo fuente nativo en android/. Compilacion debug realizada con JDK 17, SDK 36 y Gradle 8.13. Cinco pruebas unitarias pasaron. La firma v2 del APK se verifico. Lint sin errores; advertencias de versiones, target y textos se documentan en el informe.
APK: entregables/SistemasAcademico-demo.apk.
No se ha probado en telefono/emulador ni contra n8n publicado. No contiene URL activa ni claves. Configurar la Chat URL al publicar o al escuchar pruebas.

## MCP
Implementado en mcp-server/, cuatro herramientas relacionales, consultas fijas parametrizadas, transacciones de solo lectura y autenticacion bearer con hash.
14 pruebas locales pasaron, incluidas llamadas de protocolo y autenticacion HTTP. La conexion real a Supabase, el contenedor en Linux y el cliente MCP de n8n quedan pendientes del despliegue/configuracion.
No se reutiliza ni se exporta la contraseña de Postgres guardada en n8n.

## Criterios antes de la entrega final
- Elegir despliegue del frontend/chat y URL accesible.
- Probar APK en dispositivo con esa URL.
- Configurar credencial de lectura para MCP, arrancar servicio y ejecutar smoke_db.py.
- Conectar el MCP al agente y repetir pruebas sin rutas SQL duplicadas.
- Revisar interfaz movil y comportamiento con interrupciones de red.
- Grabar el video y actualizar la documentacion con URL y evidencia reales.

No se han publicado workflows ni cambiado servicios de nicolas-server.
