# views.py

from django.shortcuts import render
from django.views import View
from .scrapers.amazon_scraper import AmazonScraper
from .scrapers.mercadolibre_scraper import MercadoLibreScraper
from .scrapers.ebay_scraper import EbayScraper

from .utils.scoring import calcular_score
import threading
import time

class BuscarProductosView(View):
    template_name = 'tiendas/index.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        query = request.POST.get('query', '')
        max_results = int(request.POST.get('max_results', 10))

        # Control simple de frecuencia para evitar abuso
        last_search_time = request.session.get('last_search_time', 0)
        current_time = time.time()

        if current_time - last_search_time < 15: # Reducido a 15s
            context = {
                'error': 'Por favor espera al menos 15 segundos entre búsquedas.',
                'query': query
            }
            return render(request, 'tiendas/resultados.html', context)

        request.session['last_search_time'] = current_time

        resultados = []
        lock = threading.Lock() # Lock para evitar race conditions
        threads = []

        def run_scraper(scraper_class, query, max_results):
            """Función genérica para ejecutar un scraper y manejar errores."""
            try:
                scraper = scraper_class(headless=True)
                productos = scraper.search_products(query, max_results)
                with lock: # Adquirir el lock antes de modificar la lista compartida
                    resultados.extend(productos)
                scraper.close()
            except Exception as e:
                print(f"Error ejecutando {scraper_class.__name__}: {str(e)}")

        # Configurar y lanzar hilos
        scrapers = [AmazonScraper, MercadoLibreScraper, EbayScraper]
        for scraper_cls in scrapers:
            thread = threading.Thread(target=run_scraper, args=(scraper_cls, query, max_results))
            threads.append(thread)
            thread.start()

        # Esperar a que todos los hilos terminen
        for t in threads:
            t.join()

        # Calcular score para cada producto
        for producto in resultados:
            producto['score'] = calcular_score(producto)

        # Ordenar por score descendente por defecto
        resultados_ordenados = sorted(resultados, key=lambda x: x.get('score', 0), reverse=True)

        context = {
            'query': query,
            'resultados': resultados_ordenados,
            'total_resultados': len(resultados_ordenados)
        }

        return render(request, 'tiendas/resultados.html', context)
