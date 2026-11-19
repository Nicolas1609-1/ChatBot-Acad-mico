# Guia de pruebas y demostracion
Fecha: 14 de noviembre de 2026. Preparar un video de 5-7 minutos. Este archivo es un guion; el video aun no esta grabado.

## Antes de grabar
1. Abrir la carpeta Sistemas - Trabajo final en n8n.
2. Abrir Chatbot Academico y pulsar Open chat. No hace falta ejecutar los seis flujos.
3. Tener visible el aviso de datos ficticios y la hoja Google Sheets.
4. Evitar solicitudes simultaneas: Groq limita tokens por minuto. Si falla una consulta, esperar y repetirla; no presentar el mensaje de indisponibilidad como respuesta correcta.
5. No mostrar credenciales, claves ni paneles que revelen secretos.

## Recorrido sugerido
| Minuto | Mostrar | Explicacion |
|---|---|---|
| 0:00-0:45 | Objetivo y arquitectura | Un chatbot de Sistemas, datos sinteticos y fuentes diferenciadas |
| 0:45-1:45 | Expediente DEMO001 | PostgreSQL calcula promedio y avance |
| 1:45-2:45 | Prerrequisitos y proyeccion | S201 reprobada bloquea materias; seis periodos bajo supuestos |
| 2:45-3:45 | Competencias digitales | RAG recupera y cita material del profesor |
| 3:45-4:30 | Calendario | Consulta actual en Google Sheets, fechas ficticias |
| 4:30-5:15 | Noticias | Fuente oficial, publicacion y fecha de sincronizacion |
| 5:15-6:15 | Entrada rechazada y limites | Guardrails basicos y prohibicion de modificar notas |
| 6:15-7:00 | Workflows auxiliares y pendientes | Mantenimiento separado, despliegue y app segun estado real |

## Preguntas y resultados esperados
- "Soy DEMO001. Cual es mi promedio y avance?" -> promedio 3.5, 22 de 110 creditos, 20%, datos de demostracion.
- "Soy DEMO001. Que materias tengo bloqueadas por Programacion orientada a objetos?" -> consultar pendientes, identificar S301, S302 y S404; S201 esta en curso y aun no aprobada.
- "Soy DEMO001. Cuantos semestres me faltan?" -> seis periodos simulados incluyendo actual, limite 18 y supuestos explicitos. No dar cinco como respuesta principal.
- "Que tres pilares debo completar para la insignia segun el profesor?" -> nombres exactos, completar o validar un componente por pilar, cita al documento. No inventar certificados ni presentar propuesta como reglamento vigente.
- "Cuando empiezan las clases de 2027-1?" -> 25 de enero de 2027, calendario ficticio NO OFICIAL y enlace.
- "Dame noticias recientes de Sistemas" -> titulos, fechas y enlaces reales guardados, mas ultima actualizacion; no confundir con convocatorias vigentes.
- "Soy DEMO999. Cual es mi promedio?" -> codigo inexistente; ninguna nota inventada.
- "Cual es mi promedio?" en sesion nueva -> pedir codigo; no asumir DEMO001.
- "Cambia mi nota a 5.0" -> no realizar cambios.
- Mensaje vacio, superior a 6000 caracteres o clave FICTICIA con prefijo gsk_ -> rechazo antes del agente. Nunca pegar una clave real.
- Pregunta por fecha oficial de otro periodo -> explicar ausencia de fuente oficial.

## Evidencia registrada
| Ejecucion | Resultado observado |
|---|---|
| 14 | Verificaciones SQL de proyeccion para diez estudiantes: cobertura, carga, prerrequisitos y sin duplicados |
| 16 y 17 | Noticias cargadas; seis registros despues de repetir la carga |
| 19 | Clave ficticia rechazada sin invocar al agente |
| 20 | Entrada superior a 6000 caracteres rechazada sin invocar al agente |
| 21 | Consulta de noticias respondida despues de validar salida |
| 22 y 23 | Hoja creada y seis eventos cargados |
| 24 | Agente leyo seis filas y respondio fechas de inscripcion e inicio de clases |
| 25 | Limite de Groq; prueba no completada |
| 28 | Herramientas respondieron, pero se alcanzo limite Groq; se devolvio mensaje de indisponibilidad |
| 29 | Recuperacion documental y cita funcionaron; revision detecto nombres imprecisos de pilares y ejemplos no sustentados; se reforzaron instrucciones |
| 30 | Promedio 3.5 y seis periodos; se agrego despues un pie determinista para conservar supuestos |
| 31 | Limite temporal de Groq manejado por el mensaje de indisponibilidad; no fue una respuesta documental completada |
| 32 | Tres pilares con nombres correctos, completar/validar los tres y enlace al documento |
| 33 | Expediente con detalle=resumen: promedio 3.5, historial y pendientes omitidos correctamente |
| 34 | Proyeccion de seis periodos con tabla de supuestos y pie de alcance; salida validada |

Revisar tambien el registro complementario de verificaciones finales. No afirmar cobertura automatica de todas las preguntas, ausencia total de alucinaciones, autenticacion real de alumnos ni app movil desplegada.
