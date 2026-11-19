-- PROTOTIPO: todos los nombres, notas, periodos y reglas son ficticios.
-- Plan simplificado de demostracion; NO es el plan oficial de una universidad.
-- Ejecutar en SQL Editor de un proyecto PostgreSQL/Supabase nuevo.
BEGIN;
CREATE SCHEMA IF NOT EXISTS academico_demo;
COMMENT ON SCHEMA academico_demo IS 'Datos sinteticos de Ingenieria de Sistemas. No oficiales.';

CREATE TABLE IF NOT EXISTS academico_demo.estudiantes (
 codigo text PRIMARY KEY,
 nombre text NOT NULL,
 programa text NOT NULL DEFAULT 'Ingenieria de Sistemas'
   CHECK (programa = 'Ingenieria de Sistemas'),
 semestre_actual integer NOT NULL CHECK (semestre_actual BETWEEN 1 AND 8),
 es_sintetico boolean NOT NULL DEFAULT true CHECK (es_sintetico)
);
CREATE TABLE IF NOT EXISTS academico_demo.materias (
 codigo text PRIMARY KEY,
 nombre text NOT NULL,
 semestre integer NOT NULL CHECK (semestre BETWEEN 1 AND 8),
 creditos integer NOT NULL CHECK (creditos BETWEEN 1 AND 6)
);
CREATE TABLE IF NOT EXISTS academico_demo.prerrequisitos (
 materia text REFERENCES academico_demo.materias(codigo),
 requisito text REFERENCES academico_demo.materias(codigo),
 PRIMARY KEY (materia,requisito),
 CHECK (materia <> requisito)
);
CREATE TABLE IF NOT EXISTS academico_demo.matriculas (
 estudiante text REFERENCES academico_demo.estudiantes(codigo),
 periodo text NOT NULL,
 estado text NOT NULL CHECK (estado IN ('activa','pendiente','inactiva')),
 PRIMARY KEY (estudiante,periodo)
);
CREATE TABLE IF NOT EXISTS academico_demo.historial (
 estudiante text NOT NULL,
 periodo text NOT NULL,
 materia text REFERENCES academico_demo.materias(codigo),
 nota numeric(3,2) CHECK (nota BETWEEN 0 AND 5),
 estado text NOT NULL CHECK (estado IN ('aprobada','reprobada','en_curso')),
 PRIMARY KEY (estudiante,periodo,materia),
 FOREIGN KEY (estudiante,periodo) REFERENCES academico_demo.matriculas(estudiante,periodo),
 CHECK ((estado='en_curso' AND nota IS NULL)
     OR (estado='aprobada' AND nota >= 3)
     OR (estado='reprobada' AND nota < 3))
);

INSERT INTO academico_demo.materias VALUES
 ('S101','Fundamentos de programacion',1,4),('S102','Matematicas discretas',1,3),
 ('S103','Calculo diferencial',1,4),('S104','Comunicacion academica',1,2),
 ('S201','Programacion orientada a objetos',2,4),('S202','Algebra lineal',2,3),
 ('S203','Calculo integral',2,4),('S204','Introduccion a la ingenieria',2,2),
 ('S301','Estructuras de datos',3,4),('S302','Bases de datos I',3,4),
 ('S303','Probabilidad y estadistica',3,3),('S304','Arquitectura de computadores',3,3),
 ('S401','Analisis de algoritmos',4,4),('S402','Bases de datos II',4,4),
 ('S403','Sistemas operativos',4,3),('S404','Ingenieria de software I',4,3),
 ('S501','Desarrollo web',5,4),('S502','Redes de computadores',5,3),
 ('S503','Ingenieria de software II',5,4),('S504','Investigacion aplicada',5,2),
 ('S601','Inteligencia artificial',6,4),('S602','Sistemas distribuidos',6,4),
 ('S603','Seguridad informatica',6,3),('S604','Desarrollo movil',6,3),
 ('S701','Ciencia de datos',7,4),('S702','Computacion en la nube',7,3),
 ('S703','Proyecto de grado I',7,4),('S704','Gestion de proyectos',7,3),
 ('S801','Proyecto de grado II',8,4),('S802','Practica profesional',8,6),
 ('S803','Etica profesional',8,2),('S804','Electiva de sistemas',8,3)
ON CONFLICT DO NOTHING;

INSERT INTO academico_demo.prerrequisitos VALUES
 ('S201','S101'),('S203','S103'),('S301','S201'),('S302','S201'),
 ('S303','S202'),('S304','S102'),('S401','S301'),('S402','S302'),
 ('S403','S304'),('S404','S201'),('S501','S302'),('S501','S404'),
 ('S502','S403'),('S503','S404'),('S601','S401'),('S601','S303'),
 ('S602','S502'),('S603','S502'),('S604','S501'),('S701','S601'),
 ('S701','S402'),('S702','S602'),('S703','S504'),('S703','S503'),
 ('S704','S503'),('S801','S703'),('S802','S503'),('S804','S601')
ON CONFLICT DO NOTHING;

INSERT INTO academico_demo.estudiantes(codigo,nombre,semestre_actual) VALUES
 ('DEMO001','Ana Ejemplo',3),('DEMO002','Bruno Ejemplo',4),
 ('DEMO003','Carla Ejemplo',5),('DEMO004','Diego Ejemplo',2),
 ('DEMO005','Elena Ejemplo',6),('DEMO006','Felipe Ejemplo',7),
 ('DEMO007','Gabriela Ejemplo',1),('DEMO008','Hugo Ejemplo',8),
 ('DEMO009','Isabel Ejemplo',4),('DEMO010','Julian Ejemplo',5)
ON CONFLICT DO NOTHING;

-- Periodos DEMO-S1..S8: orden didactico ficticio, no calendario oficial.
INSERT INTO academico_demo.matriculas
SELECT e.codigo,'DEMO-S'||s,
 CASE WHEN s=e.semestre_actual AND e.codigo='DEMO009' THEN 'pendiente' ELSE 'activa' END
FROM academico_demo.estudiantes e
CROSS JOIN LATERAL generate_series(1,e.semestre_actual) s
ON CONFLICT DO NOTHING;

INSERT INTO academico_demo.historial
SELECT e.codigo,'DEMO-S'||m.semestre,m.codigo,
 CASE WHEN m.semestre=e.semestre_actual THEN NULL
      ELSE (3.2 + ((substring(e.codigo from 5)::integer + m.semestre) % 8)*0.2)::numeric(3,2) END,
 CASE WHEN m.semestre=e.semestre_actual THEN 'en_curso' ELSE 'aprobada' END
FROM academico_demo.estudiantes e CROSS JOIN academico_demo.materias m
WHERE m.semestre<=e.semestre_actual AND NOT
 (e.codigo='DEMO009' AND m.semestre=e.semestre_actual)
ON CONFLICT DO NOTHING;

-- Caso con perdida y repeticion, sin cursar asignaturas bloqueadas.
UPDATE academico_demo.historial SET nota=2.5,estado='reprobada'
WHERE estudiante='DEMO001' AND materia='S201' AND periodo='DEMO-S2';
DELETE FROM academico_demo.historial
WHERE estudiante='DEMO001' AND materia IN ('S301','S302') AND periodo='DEMO-S3';
INSERT INTO academico_demo.historial VALUES ('DEMO001','DEMO-S3','S201',NULL,'en_curso')
ON CONFLICT DO NOTHING;

CREATE OR REPLACE VIEW academico_demo.v_resumen AS
SELECT e.codigo,e.nombre,e.programa,e.semestre_actual,
 (SELECT estado FROM academico_demo.matriculas mt
   WHERE mt.estudiante=e.codigo AND mt.periodo='DEMO-S'||e.semestre_actual) AS estado_matricula,
 (SELECT round(sum(h.nota*m.creditos)/nullif(sum(m.creditos),0),2)
   FROM academico_demo.historial h JOIN academico_demo.materias m ON m.codigo=h.materia
   WHERE h.estudiante=e.codigo AND h.estado<>'en_curso') AS promedio_historico,
 coalesce((SELECT sum(m.creditos) FROM academico_demo.materias m WHERE EXISTS
   (SELECT 1 FROM academico_demo.historial h WHERE h.estudiante=e.codigo
     AND h.materia=m.codigo AND h.estado='aprobada')),0) AS creditos_aprobados,
 (SELECT sum(creditos) FROM academico_demo.materias) AS creditos_plan,
 true AS datos_sinteticos
FROM academico_demo.estudiantes e;

CREATE OR REPLACE VIEW academico_demo.v_materias_pendientes AS
SELECT e.codigo AS estudiante,m.codigo AS materia,m.nombre,m.semestre,m.creditos,
 EXISTS (SELECT 1 FROM academico_demo.historial h WHERE h.estudiante=e.codigo
   AND h.materia=m.codigo AND h.estado='en_curso') AS en_curso,
 NOT EXISTS (SELECT 1 FROM academico_demo.prerrequisitos p
   WHERE p.materia=m.codigo AND NOT EXISTS (
     SELECT 1 FROM academico_demo.historial h WHERE h.estudiante=e.codigo
       AND h.materia=p.requisito AND h.estado='aprobada')) AS prerrequisitos_cumplidos,
 ARRAY(SELECT p.requisito FROM academico_demo.prerrequisitos p
   WHERE p.materia=m.codigo AND NOT EXISTS (
     SELECT 1 FROM academico_demo.historial h WHERE h.estudiante=e.codigo
       AND h.materia=p.requisito AND h.estado='aprobada') ORDER BY p.requisito) AS requisitos_pendientes
FROM academico_demo.estudiantes e CROSS JOIN academico_demo.materias m
WHERE NOT EXISTS (SELECT 1 FROM academico_demo.historial h WHERE h.estudiante=e.codigo
  AND h.materia=m.codigo AND h.estado='aprobada');

-- Mantener este esquema fuera de los esquemas expuestos por la Data API.
-- Conexion prevista: Postgres desde n8n, con consultas parametrizadas.
REVOKE ALL ON SCHEMA academico_demo FROM PUBLIC;
COMMIT;

-- Comprobaciones esperadas: 10 estudiantes, 32 materias y 2 vistas.
SELECT count(*) AS estudiantes FROM academico_demo.estudiantes;
SELECT count(*) AS materias FROM academico_demo.materias;
SELECT * FROM academico_demo.v_resumen ORDER BY codigo;
SELECT * FROM academico_demo.v_materias_pendientes WHERE estudiante='DEMO001' ORDER BY semestre,materia;
