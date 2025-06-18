import re
import math

def calcular_score(producto):
    """
    Calcula un score de 'calidad-precio' para un producto.
    Más robusto para manejar diferentes formatos de datos.
    """
    try:
        # --- Limpieza de Precio ---
        precio_str = str(producto.get("precio", "0"))
        # Extraer solo números y un punto decimal
        numeros_precio = re.findall(r'\d+\.?\d*', precio_str)
        if not numeros_precio:
            return 0.0
        precio = float("".join(numeros_precio))

        # --- Limpieza de Rating ---
        rating_str = str(producto.get("rating", "0")).replace(",", ".")
        numeros_rating = re.findall(r'\d+\.?\d*', rating_str)
        rating = float(numeros_rating[0]) if numeros_rating else 0.0

        # Asumir un número base de reviews si no está presente
        reviews_str = str(producto.get("reviews", "10"))
        numeros_reviews = re.findall(r'\d+', reviews_str)
        reviews = int("".join(numeros_reviews)) if numeros_reviews else 10
        # Evitar que reviews sea 0 para el logaritmo
        if reviews == 0:
            reviews = 1

        # Evitar división por cero
        if precio > 0:
            # Ponderar más el rating y darle importancia a las reviews
            score_bruto = (rating ** 2 * math.log10(reviews + 1)) / math.log1p(precio)
            
            # Normalizar el score a una escala (ej. 1 a 100)
            return round(score_bruto * 10, 2)
        
        return 0.0
    except (ValueError, TypeError, IndexError) as e:
        print(f"Error al calcular score para '{producto.get('titulo')}': {e}")
        return 0.0
