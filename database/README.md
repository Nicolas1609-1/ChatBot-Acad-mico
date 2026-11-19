# Base de datos

Ejecuta los scripts en este orden sobre PostgreSQL con la extensión `pgvector`:

| # | Script | Qué crea |
|---|---|---|
| 01 | `01_base_academica.sql` | Esquema `academico_demo`: estudiantes, materias, prerrequisitos, matrículas, historial y vistas `v_resumen` y `v_materias_pendientes` |
| 02 | `02_proyeccion_semestres.sql` | Función `proyectar_semestres(codigo, 18)` |
| 03 | `03_estructura_noticias.sql` | Tablas `noticias` y `estado_fuentes` |
| 04 | `04_estructura_vectores.sql` | Tabla de vectores para el RAG |
| 05 | `05_codigos_estudiante.sql` | Códigos públicos `U00` + seis números |
| 06 | `06_tres_estudiantes.sql` | Tres perfiles adicionales (Laura, Mateo, Sofía) |

Todos los datos son simulados.
