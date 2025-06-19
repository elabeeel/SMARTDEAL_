# mercadolibre_scraper.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .base_scraper import BaseScraper

class MercadoLibreScraper(BaseScraper):
    def search_products(self, query, max_results=10):
        try:
            self.driver.get("https://www.mercadolibre.com.mx")
            self._human_like_delay(1, 2)
            
            self._dismiss_popups()
            
            search_box = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "cb1-edit")) # ID más estable
            )
            self._human_type(search_box, query)
            search_box.submit()
            self._human_like_delay(2, 3)
            
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-search-layout__item"))
            )
            
            self._simulate_human_scroll()
            
            products = []
            items = self.driver.find_elements(By.CSS_SELECTOR, "li.ui-search-layout__item")[:max_results]
            
            for item in items:
                try:
                    title = (self._safe_extract(item, "a.poly-component__title") or
                                     self._safe_extract(item, "h3.ui-search-item__title") or
                                     self._safe_extract(item, "h2.ui-search-item__title") or
                                     "Título no disponible"
                                     )

                    
                    # --- Lógica de precio corregida ---
                    price_fraction = self._safe_extract(item, "span.andes-money-amount__fraction")
                    price_cents = self._safe_extract(item, "span.andes-money-amount__cents")
                    
                    if price_fraction:
                        price = f"{price_fraction}"
                        if price_cents:
                            price += f".{price_cents}"
                    else:
                        price = "No disponible"
                    
                    rating = self._safe_extract(item, "span.poly-reviews__rating")
                    url = self._safe_extract(item, "a.poly-component__title", attr="href")
                    image = (self._safe_extract(item, "img", attr="data-src") or 
                             self._safe_extract(item, "img", attr="src") or 
                             self._safe_extract(item, "img", attr="data-lazy") or
                             "No disponible"
                             )

                    try:
                        official_store_elem = item.find_element(By.CSS_SELECTOR, "p.ui-search-official-store-label")
                        seller = official_store_elem.text.replace('por ', '').strip()
                        is_official = True
                    except:
                        seller = self._safe_extract(item, "span.ui-search-item__seller-name") or "Vendedor independiente"
                        is_official = False
                    
                    products.append({
                        'tienda': 'Mercado Libre',
                        'titulo': title or "Título no disponible",
                        'precio': f"${price.replace(',', '')}" if price != "No disponible" else price,
                        'rating': rating if rating else "No disponible",
                        'url': url or "No disponible",
                        'imagen': image or "No disponible",
                        'vendedor': seller,
                        'oficial': is_official
                    })
                    
                except Exception as e:
                    print(f"Error procesando producto de Mercado Libre: {str(e)[:200]}")
                    continue
            
            return products
            
        except TimeoutException:
            print("Tiempo de espera agotado en Mercado Libre")
            return []
        except Exception as e:
            print(f"Error en la búsqueda de Mercado Libre: {str(e)[:200]}")
            return []

    def _dismiss_popups(self):
        try:
            cookie_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aceptar cookies')]"))
            )
            cookie_button.click()
            self._human_like_delay(1, 2)
        except:
            pass

    def _safe_extract(self, parent, selector, attr=None):
        try:
            element = parent.find_element(By.CSS_SELECTOR, selector)
            return element.get_attribute(attr) if attr else element.text
        except:
            return None