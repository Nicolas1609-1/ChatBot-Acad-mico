CREATE OR REPLACE FUNCTION academico_demo.proyectar_semestres(p_codigo text, p_limite integer DEFAULT 18)
RETURNS jsonb
LANGUAGE plpgsql STABLE SECURITY INVOKER SET search_path=pg_catalog
AS $proyeccion$
DECLARE
 v_codigo text := upper(trim(p_codigo));
 v_aprobadas text[];
 v_en_curso text[];
 v_seleccionadas text[];
 v_detalle jsonb;
 v_plan jsonb := '[]'::jsonb;
 v_creditos integer;
 v_periodo integer;
 v_materia record;
 v_total integer;
BEGIN
 IF p_limite IS NULL OR p_limite<1 OR p_limite>18 THEN
   RAISE EXCEPTION 'El limite de demostracion debe estar entre 1 y 18 creditos' USING ERRCODE='22023';
 END IF;
 IF NOT EXISTS (SELECT 1 FROM academico_demo.estudiantes e WHERE e.codigo=v_codigo) THEN
   RETURN jsonb_build_object('encontrado',false,'codigo',v_codigo,'datos_sinteticos',true,'plan','[]'::jsonb);
 END IF;
 SELECT coalesce(array_agg(DISTINCT h.materia),'{}'::text[]) INTO v_aprobadas
 FROM academico_demo.historial h WHERE h.estudiante=v_codigo AND h.estado='aprobada';
 SELECT coalesce(array_agg(DISTINCT h.materia),'{}'::text[]) INTO v_en_curso
 FROM academico_demo.historial h WHERE h.estudiante=v_codigo AND h.estado='en_curso';
 SELECT count(*) INTO v_total FROM academico_demo.materias;
 FOR v_periodo IN 1..32 LOOP
   EXIT WHEN cardinality(v_aprobadas)>=v_total;
   v_seleccionadas := '{}'::text[];
   v_detalle := '[]'::jsonb;
   v_creditos := 0;
   FOR v_materia IN
     SELECT m.* FROM academico_demo.materias m
     WHERE NOT (m.codigo=ANY(v_aprobadas))
       AND NOT EXISTS (SELECT 1 FROM academico_demo.prerrequisitos p
         WHERE p.materia=m.codigo AND NOT (p.requisito=ANY(v_aprobadas)))
     ORDER BY (m.codigo=ANY(v_en_curso)) DESC, m.semestre,
       (SELECT count(*) FROM academico_demo.prerrequisitos p WHERE p.requisito=m.codigo) DESC,m.codigo
   LOOP
     IF v_creditos+v_materia.creditos<=p_limite THEN
       v_seleccionadas:=array_append(v_seleccionadas,v_materia.codigo);
       v_creditos:=v_creditos+v_materia.creditos;
       v_detalle:=v_detalle||jsonb_build_array(jsonb_build_object(
         'codigo',v_materia.codigo,'nombre',v_materia.nombre,'creditos',v_materia.creditos,
         'semestre_plan',v_materia.semestre,'actualmente_en_curso',v_materia.codigo=ANY(v_en_curso)));
     END IF;
   END LOOP;
   EXIT WHEN cardinality(v_seleccionadas)=0;
   v_plan:=v_plan||jsonb_build_array(jsonb_build_object(
     'periodo_simulado',v_periodo,'creditos',v_creditos,'materias',v_detalle));
   v_aprobadas:=v_aprobadas||v_seleccionadas;
 END LOOP;
 RETURN jsonb_build_object(
   'encontrado',true,'codigo',v_codigo,'datos_sinteticos',true,
   'estado',CASE WHEN cardinality(v_aprobadas)=v_total THEN 'completo' ELSE 'bloqueado' END,
   'limite_creditos',p_limite,'semestres_simulados_desde_ahora',jsonb_array_length(v_plan),
   'plan',v_plan,
   'materias_sin_programar',(SELECT coalesce(jsonb_agg(m.codigo ORDER BY m.codigo),'[]'::jsonb)
     FROM academico_demo.materias m WHERE NOT (m.codigo=ANY(v_aprobadas))),
   'supuestos',jsonb_build_array(
     'Todas las materias seleccionadas se aprueban al finalizar su periodo.',
     'Todas las materias estan disponibles cada periodo; no se consideran horarios ni cupos.',
     'El primer periodo simulado incluye las materias actualmente en curso. No autoriza modificar la matricula actual.',
     'Se respetan los prerrequisitos aprobados en periodos anteriores y la carga maxima indicada.',
     'Plan sintetico con seleccion voraz: es una simulacion factible, no garantiza el minimo de semestres ni una fecha de grado.',
     'No incluye requisitos de grado externos a las 32 materias del plan sintetico.'));
END;
$proyeccion$;
COMMENT ON FUNCTION academico_demo.proyectar_semestres(text,integer)
IS 'Simulacion de solo lectura para el plan ficticio de Sistemas. No es una proyeccion oficial.';

DO $pruebas$
DECLARE
 e record; r jsonb; periodo jsonb; v_test_materia jsonb;
 aprobadas text[]; nuevas text[]; suma integer;
BEGIN
 FOR e IN SELECT codigo FROM academico_demo.estudiantes LOOP
   r:=academico_demo.proyectar_semestres(e.codigo,18);
   IF r->>'estado'<>'completo' THEN RAISE EXCEPTION 'Proyeccion bloqueada: %',e.codigo; END IF;
   SELECT coalesce(array_agg(DISTINCT h.materia),'{}'::text[]) INTO aprobadas
     FROM academico_demo.historial h WHERE h.estudiante=e.codigo AND h.estado='aprobada';
   FOR periodo IN SELECT value FROM jsonb_array_elements(r->'plan') LOOP
     nuevas:='{}'::text[]; suma:=0;
     FOR v_test_materia IN SELECT value FROM jsonb_array_elements(periodo->'materias') LOOP
       IF v_test_materia->>'codigo'=ANY(aprobadas) OR v_test_materia->>'codigo'=ANY(nuevas) THEN
         RAISE EXCEPTION 'Materia duplicada: %',e.codigo;
       END IF;
       IF EXISTS (SELECT 1 FROM academico_demo.prerrequisitos p
         WHERE p.materia=v_test_materia->>'codigo' AND NOT (p.requisito=ANY(aprobadas))) THEN
         RAISE EXCEPTION 'Prerrequisito incumplido: % %',e.codigo,v_test_materia->>'codigo';
       END IF;
       nuevas:=array_append(nuevas,v_test_materia->>'codigo');
       suma:=suma+(v_test_materia->>'creditos')::integer;
     END LOOP;
     IF suma>18 OR suma<>(periodo->>'creditos')::integer THEN
       RAISE EXCEPTION 'Carga invalida: %',e.codigo;
     END IF;
     aprobadas:=aprobadas||nuevas;
   END LOOP;
   IF cardinality(aprobadas)<>(SELECT count(*) FROM academico_demo.materias) THEN
     RAISE EXCEPTION 'Plan incompleto: %',e.codigo;
   END IF;
 END LOOP;
 IF (academico_demo.proyectar_semestres('DEMO999')->>'encontrado')::boolean THEN
   RAISE EXCEPTION 'Codigo inexistente aceptado';
 END IF;
END;
$pruebas$;
SELECT e.codigo,
 (academico_demo.proyectar_semestres(e.codigo)->>'semestres_simulados_desde_ahora')::integer AS periodos_simulados,
 academico_demo.proyectar_semestres(e.codigo)->>'estado' AS estado,
 'Prerrequisitos, creditos y cobertura verificados' AS validacion
FROM academico_demo.estudiantes e ORDER BY e.codigo;
