CREATE TABLE IF NOT EXISTS academico_demo.noticias (
 wp_id bigint PRIMARY KEY,
 titulo text NOT NULL CHECK(length(titulo) BETWEEN 1 AND 500),
 resumen text NOT NULL DEFAULT '',
 url text NOT NULL UNIQUE CHECK(url ~ '^https://unab[.]edu[.]co/'),
 publicada_en timestamptz NOT NULL,
 modificada_en timestamptz NOT NULL,
 consultada_en timestamptz NOT NULL DEFAULT now(),
 categoria text NOT NULL DEFAULT 'Ingenieria de Sistemas'
);
CREATE TABLE IF NOT EXISTS academico_demo.estado_fuentes (
 fuente text PRIMARY KEY, ultima_actualizacion_ok timestamptz, observacion text
);
INSERT INTO academico_demo.estado_fuentes(fuente,observacion)
VALUES ('noticias_sistemas_unab','Categoria oficial de Ingenieria de Sistemas. Ultimas 20 publicaciones; no equivale a toda la oferta de cursos.')
ON CONFLICT (fuente) DO NOTHING;
SELECT true AS preparado;
