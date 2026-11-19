"""Opt-in live read-only database check. Run only after setting DATABASE_URL."""
import os
from repository import AcademicRepository

def main():
    repository = AcademicRepository(os.environ["DATABASE_URL"])
    result = repository.expediente("U00100001", "resumen")
    assert result["resumen"]["datos_sinteticos"] is True
    assert result["resumen"]["promedio_historico"] == 3.5
    assert result["resumen"]["creditos_aprobados"] == 22
    projected = repository.proyeccion("U00100001")
    assert projected["proyeccion"]["semestres_simulados_desde_ahora"] == 6
    assert projected["proyeccion"]["estado"] == "completo"
    plan = repository.plan()
    assert len(plan["plan"]) == 32
    repository.noticias()
    print("Lecturas de expediente, plan, proyeccion y noticias correctas. Ninguna escritura.")

if __name__ == "__main__":
    main()
