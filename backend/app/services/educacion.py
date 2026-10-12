"""Contenido educativo (RF-08): hipertensión, dieta DASH adaptada a Colombia y
actividad física. Lenguaje sencillo, pensado para adultos mayores.

El contenido es orientativo y debe ser revisado por profesionales de salud
antes de publicarse (fuente validada = técnica BCT 'credible source').
"""

CONTENIDO: dict[str, dict] = {
    "que-es-la-hipertension": {
        "titulo": "¿Qué es la hipertensión?",
        "resumen": "La presión alta daña poco a poco el corazón, el cerebro y los riñones, casi siempre sin síntomas.",
        "secciones": [
            "La presión arterial se escribe con dos números: el de arriba (sistólica) y el de abajo (diastólica).",
            "Por debajo de 120/70 es una presión no elevada. Entre 120/70 y 139/89 es elevada. "
            "Desde 140/90 se habla de hipertensión.",
            "En casa, el promedio de varios días se considera alto desde 135/85.",
            "Que no sienta nada no significa que esté controlada: por eso es importante medir.",
        ],
    },
    "como-medir-en-casa": {
        "titulo": "Cómo medir bien su presión en casa",
        "resumen": "Una buena técnica hace que sus números sean confiables.",
        "secciones": [
            "Use un tensiómetro de brazo validado. Si tiene más de 4 años, hágalo revisar.",
            "No tome café, no fume ni haga ejercicio 30 minutos antes. Vaya al baño antes de medir.",
            "Siéntese 5 minutos con la espalda apoyada, los pies en el piso y el brazo a la altura del corazón.",
            "Tome 2 mediciones separadas por 1 o 2 minutos, en la mañana (antes del medicamento) y en la noche.",
            "Hágalo durante 7 días seguidos antes de su cita. La aplicación calcula el promedio por usted.",
        ],
    },
    "dieta-dash-colombiana": {
        "titulo": "Dieta DASH a la colombiana",
        "resumen": "Más frutas, verduras y granos; menos sal y ultraprocesados. Meta: menos de 2 g de sodio al día (menos de una cucharadita de sal).",
        "secciones": [
            "Prefiera: frutas como guayaba, papaya, mango, banano, lulo y mora (mejor enteras que en jugo con azúcar).",
            "Verduras en cada comida: ahuyama, habichuela, espinaca, tomate, zanahoria, repollo.",
            "Granos y tubérculos: fríjoles, lentejas y garbanzos cocinados sin cubo de caldo; arroz integral, papa y yuca cocidas, no fritas.",
            "Proteína: pollo sin piel, pescado, huevo; lácteos bajos en grasa como kumis o yogur natural.",
            "Reduzca: cubos y sazonadores de caldo, embutidos (salchichón, mortadela, chorizo), queso costeño y otros quesos muy salados, chicharrón, paquetes y enlatados.",
            "Truco: sazone con ajo, cebolla larga, cilantro, comino, limón y guascas en lugar de sal.",
            "Arepas y ajiaco pueden seguir en su mesa: prepárelos con poca sal y sin cubo de caldo.",
        ],
    },
    "actividad-fisica": {
        "titulo": "Actividad física recomendada",
        "resumen": "150 minutos a la semana de actividad moderada, más ejercicios de fuerza 2 o 3 veces.",
        "secciones": [
            "Caminar a paso rápido 30 minutos, 5 días a la semana, ya cumple la meta. Puede dividirlo en 3 caminatas de 10 minutos.",
            "Otras opciones: bicicleta (por ejemplo la ciclovía del domingo), baile, natación o aeróbicos.",
            "Fuerza 2 o 3 veces por semana: levantarse de una silla, subir escalas, bandas elásticas o botellas con agua.",
            "Si su presión está en 180/120 o más, no haga ejercicio y consulte a su médico.",
        ],
    },
    "otros-habitos": {
        "titulo": "Otros hábitos que ayudan",
        "resumen": "Pequeños cambios suman milímetros de mercurio.",
        "secciones": [
            "Mantenga un peso saludable.",
            "Si toma alcohol, hágalo con moderación, o mejor, evítelo.",
            "Deje de fumar: pida apoyo en su EPS.",
            "Tome sus medicamentos todos los días, aunque se sienta bien. Nunca los suspenda sin hablar con su médico.",
            "Consulte a su médico antes de usar suplementos de potasio, sobre todo si tiene problemas en los riñones.",
        ],
    },
}


def listar() -> list[dict]:
    return [{"slug": k, "titulo": v["titulo"], "resumen": v["resumen"]} for k, v in CONTENIDO.items()]


def obtener(slug: str) -> dict | None:
    item = CONTENIDO.get(slug)
    return {"slug": slug, **item} if item else None
