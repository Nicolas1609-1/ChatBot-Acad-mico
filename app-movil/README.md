# App móvil — Asistente Académico (Android)

Aplicación Android hecha con **Expo (React Native)**. El estudiante entra con su código
(`U00` + 6 números) y conversa con el agente de n8n por el mismo webhook que usa la web.

## Qué hace

- **Entrada por código:** valida `U00XXXXXX` y consulta el expediente en `/api/student`.
- **Panel del estudiante:** nombre, semestre, estado de matrícula, promedio, créditos y avance.
- **Atajos:** Matrícula, Estado académico, Proyección, Recomendaciones, Calendario y Noticias.
- **Chat:** envía cada pregunta a `/api/chat` y muestra la respuesta del agente con formato
  (negritas, listas y tablas que se deslizan hacia los lados).
- **Cambiar código:** inicia una sesión nueva para otro estudiante.

## Cómo se conecta

```
App Android ──HTTPS──> academico.nicolas16.life (proxy en nicolas-server)
                             ├─ POST /api/student  → expediente (PostgreSQL vía n8n)
                             └─ POST /api/chat     → webhook del Chatbot Académico en n8n
                                                     (agente + Groq + RAG + MCP + calendario + noticias)
```

La app no guarda claves ni URLs privadas de n8n. El proxy del servidor fija el destino, valida
el código y la sesión, y limita las consultas.

## Abrirla en el celular con Expo Go

1. Instala **Expo Go** desde Play Store.
2. En esta carpeta ejecuta:

   ```powershell
   npx expo start
   ```

3. Escanea el código QR con Expo Go. El celular y el PC deben estar en la misma red Wi‑Fi.
   Si no lo están, usa `npx expo start --tunnel`.
4. Entra con un código de ejemplo: `U00100001` a `U00100013`.

## Revisarla en el navegador del PC

El servidor rechaza peticiones de navegador con otro origen, así que para la vista web hay un
proxy local:

```powershell
node tools/proxy-web.mjs
```

```powershell
$env:EXPO_PUBLIC_API_BASE="http://localhost:8099"; npx expo start --web
```

## Verificación

- `npx tsc --noEmit`: sin errores de tipos.
- `npx expo-doctor`: 20/20 comprobaciones.
- `npx expo export --platform android`: el paquete Android compila.
- Prueba real contra el servidor con `U00100012` (Mateo): panel 4.09 / 54 de 110 créditos / 49 %,
  y respuestas de Matrícula, Proyección (4 semestres) y Recomendaciones.

Datos simulados para el proyecto académico.
