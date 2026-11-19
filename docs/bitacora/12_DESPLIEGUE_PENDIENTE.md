# Preparacion para el despliegue
Estado actualizado: la web de PC ya esta instalada en /home/nicolas/chatbot-academico y conectada a n8n. Acceso privado por Tailscale: http://100.74.216.15:8091/ . Esta guia conserva alternativas de restauracion; el estado vigente esta en 19_SERVIDOR_ACTUAL.md. FastMCP, movil/Expo y video estan aplazados por el usuario.

## Dos alternativas
1. Mantener n8n Cloud y Supabase; alojar una interfaz en el servidor que consulte el endpoint de chat publicado. Es la ruta con menos cambios, pero requiere activar el chat y controlar acceso y uso.
2. Migrar tambien n8n al servidor; requiere Docker con permisos, HTTPS, almacenamiento persistente, backups, credenciales reasignadas y un proveedor de embeddings fuera de Gateway si ese servicio no esta disponible en la nueva instancia.

Se eligio la primera alternativa: n8n Cloud y Supabase conservados, interfaz y proxy en el servidor. La clave de cifrado de n8n y las credenciales no van en Git ni en los JSON exportados.

## Prerequisitos antes de publicar
- Repetir la guia de pruebas final sin fallos materiales.
- Determinar URL, dominio y mecanismo de acceso. Un nombre SSH no es una URL publica.
- Comprobar permisos Docker o elegir un despliegue autorizado alternativo. El usuario nicolas no tenia acceso al socket Docker durante la inspeccion anterior.
- Publicar solo los workflows operativos necesarios: chat y actualizacion de noticias. No publicar ni programar seeds o reinstalaciones.
- Conservar los servicios existentes en nicolas-server. No sustituir sus tuneles o contenedores.
- Configurar HTTPS y limites de uso. No poner claves Groq/Postgres en HTML o en una app Android.
- Si se admiten datos reales, agregar autenticacion y control por alumno, roles SQL limitados, retencion y politicas de acceso. Los codigos DEMO no son autenticacion.
- Probar desde navegador fuera de la red local y desde Android antes de declarar acceso externo.

## Orden de restauracion en una instancia nueva
1. Crear PostgreSQL con pgvector y cargar 01_base_academica.sql en una base de pruebas vacia.
2. Instalar 07_proyeccion_semestres.sql.
3. Importar respaldos de workflows y reasignar credenciales PostgreSQL, Groq y Google Sheets.
4. Configurar embeddings para documentos y consultas con el MISMO modelo y 1536 dimensiones; reindexar si cambia el modelo. Los creditos Gateway no se deben asumir transferibles.
5. Reindexar documentos y comprobar 96 fragmentos si las fuentes/particion no han cambiado.
6. Ejecutar noticias para crear sus tablas y sincronizar registros.
7. Reutilizar la hoja calendario existente con permiso de la nueva credencial, o crear una nueva deliberadamente y actualizar su referencia. La escritura del seed actual esta desactivada.
8. Probar el chat, errores y fuentes; solo despues publicar.

Los respaldos JSON son configuraciones sanitizadas de n8n, no un backup completo de datos. Para una migracion se necesita tambien un backup PostgreSQL y una estrategia de restauracion de memoria/documentos.

## Aplicacion Android
La presentacion exige una app Android. Ya hay codigo nativo en android/ y APK debug en entregables/. Se compilo con herramientas portatiles y pasaron cinco pruebas unitarias. Falta probar en dispositivo con endpoint real. No se cambiaron JAVA_HOME ni el SDK a nivel de sistema: las variables se usaron solo en procesos de compilacion. El backend academico permanece en n8n. El APK no contiene una URL activa ni claves API.

## Servidor MCP
La conexion actual de Codex al MCP oficial de n8n permite administrar los workflows. Esto NO equivale a implementar el servidor Python FastMCP que aparece en la presentacion.
Ese componente ya esta implementado en mcp-server/: cuatro herramientas relacionales limitadas y autenticadas, con 14 verificaciones locales. Falta configurar credenciales de lectura, verificar acceso real a Supabase, desplegar y conectar el cliente MCP del agente n8n. No exponer SQL libre ni PostgreSQL directamente a Internet.
