BEGIN;
INSERT INTO academico_demo.estudiantes(codigo,nombre,semestre_actual,codigo_institucional) VALUES
('DEMO011','Laura Ejemplo',2,'U00100011'),('DEMO012','Mateo Ejemplo',5,'U00100012'),('DEMO013','Sofia Ejemplo',7,'U00100013') ON CONFLICT DO NOTHING;
INSERT INTO academico_demo.matriculas(estudiante,periodo,estado)
SELECT e.codigo,'DEMO-S'||s,'activa' FROM academico_demo.estudiantes e CROSS JOIN LATERAL generate_series(1,e.semestre_actual) s WHERE e.codigo IN ('DEMO011','DEMO012','DEMO013') ON CONFLICT DO NOTHING;
INSERT INTO academico_demo.historial(estudiante,periodo,materia,nota,estado)
SELECT e.codigo,'DEMO-S'||m.semestre,m.codigo,CASE WHEN m.semestre=e.semestre_actual THEN NULL ELSE (3.2+((substring(e.codigo from 5)::integer+m.semestre)%8)*0.2)::numeric(3,2) END,CASE WHEN m.semestre=e.semestre_actual THEN 'en_curso' ELSE 'aprobada' END
FROM academico_demo.estudiantes e CROSS JOIN academico_demo.materias m WHERE e.codigo IN ('DEMO011','DEMO012','DEMO013') AND m.semestre<=e.semestre_actual ON CONFLICT DO NOTHING;
COMMIT;
SELECT e.codigo_institucional,r.nombre,r.semestre_actual,r.promedio_historico,r.creditos_aprobados,r.creditos_plan FROM academico_demo.estudiantes e JOIN academico_demo.v_resumen r ON r.codigo=e.codigo WHERE e.codigo IN ('DEMO011','DEMO012','DEMO013') ORDER BY e.codigo;
