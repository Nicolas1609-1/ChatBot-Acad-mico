ALTER TABLE academico_demo.estudiantes ADD COLUMN IF NOT EXISTS codigo_institucional text;
UPDATE academico_demo.estudiantes SET codigo_institucional='U00'||lpad((100000+substring(codigo from 5)::integer)::text,6,'0') WHERE codigo ~ '^DEMO[0-9]{3}$' AND codigo_institucional IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS estudiantes_codigo_institucional_uidx ON academico_demo.estudiantes(codigo_institucional);
