"""Backend de Mi Presión.

Recorrido de una petición (de afuera hacia adentro):

    navegador -> api/rutas (recibe) -> schemas (valida) -> services (piensa)
              -> models + db (guarda en Supabase) -> respuesta al navegador
"""
