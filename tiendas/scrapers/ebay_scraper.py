# ebay_scraper.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .base_scraper import BaseScraper

class EbayScraper(BaseScraper):
    def search_products(self, query, max_results=10):
        try:
            self.driver.get("https://www.ebay.com/")
            self._human_like_delay(1, 2)

            self._dismiss_popups()

            search_box = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "gh-ac"))
            )
            self._human_type(search_box, query)
            search_box.submit()
            self._human_like_delay(2, 3)

            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.s-item"))
            )

            self._simulate_human_scroll()

            products = []
            items = self.driver.find_elements(By.CSS_SELECTOR, "li.s-item")[:max_results]

            for item in items:
                try:
                    try:
                        title_elem = item.find_element(By.XPATH, ".//a[contains(@class, 's-item__link')]//div[contains(@class, 's-item__title')]//span")
                        title = title_elem.text.strip()
                    except:
                        title = "Título no disponible"

                    price = self._safe_extract(item, "span.s-item__price") or "No disponible"
                    rating = self._safe_extract(item, "div.x-star-rating span.clipped") or "No disponible"
                    url = self._safe_extract(item, "a.s-item__link", attr="href") or "No disponible"
                    image = (self._safe_extract(item, "img", attr="data-src") or 
                             self._safe_extract(item, "img", attr="src") or 
                             self._safe_extract(item, "img", attr="data-lazy") or
                             "No disponible"
                             )

                    products.append({
                        'tienda': 'ebay',
                        'titulo': title,
                        'precio': price,
                        'rating': rating,
                        'url': url,
                        'imagen': image,
                    })

                except Exception as e:
                    print(f"Error procesando producto de eBay: {str(e)[:200]}")
                    continue

            return products

        except TimeoutException:
            print("Tiempo de espera agotado en eBay")
            return []
        except Exception as e:
            print(f"Error en la búsqueda de eBay: {str(e)[:200]}")
            return []

    def _dismiss_popups(self):
        try:
            # eBay normalmente no tiene cookies forzosas visibles en todos los países,
            # pero dejamos esto por compatibilidad
            cookie_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aceptar todas')]"))
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
