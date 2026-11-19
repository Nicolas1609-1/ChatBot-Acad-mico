# Flujos de n8n

Importa cada archivo en n8n con *Import from file* y asigna tus credenciales (los archivos no traen claves).

| Archivo | Flujo | Cuándo corre |
|---|---|---|
| `chatbot_academico.json` | Chatbot principal: agente, herramientas, memoria y guardrails | Con cada mensaje (publicado) |
| `ingesta_rag.json` | Indexa los documentos de `rag-fuentes/` en pgvector | Al instalar o cambiar documentos |
| `noticias_unab.json` | Sincroniza noticias de la UNAB | Todos los días a las 08:00 |
| `calendario_demo.json` | Prepara el calendario en Google Sheets | Una vez |
| `preparar_base.json` | Carga inicial de datos simulados | Una vez |
| `preparar_proyeccion.json` | Instala y verifica la función de proyección | Al cambiar el algoritmo |

`historial/` guarda versiones anteriores del chatbot para ver cómo evolucionó.
