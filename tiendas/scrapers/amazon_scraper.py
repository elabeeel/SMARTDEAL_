# scrapers/amazon_scraper.py

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
from urllib.parse import urlparse, parse_qs

class AmazonScraper:
    def __init__(self, headless=False):
        options = uc.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1000,1200")
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = uc.Chrome(options=options)

    def close(self):
        if self.driver:
            self.driver.quit()

    def search_products(self, query, max_results=10):
        results = []
        try:
            self.driver.get("https://www.amazon.com.mx/")
            self._human_like_delay(2, 4)
            self._dismiss_popups()

            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "field-keywords"))
            )
            search_input.send_keys(query)
            search_input.send_keys(Keys.RETURN)
            self._human_like_delay()

            while len(results) < max_results:
                items = self.driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")
                for item in items:
                    try:
                        name_elem = item.find_element(By.XPATH, ".//h2//span")
                        price_elem = item.find_element(By.XPATH, ".//span[@class='a-offscreen']")
                        rating_elem = item.find_element(By.XPATH, ".//span[@class='a-icon-alt']")
                        link_elem = item.find_element(By.XPATH, ".//a[@class='a-link-normal s-no-outline']")
                        img_elem = item.find_element(By.XPATH, ".//img[@class='s-image']")

                        # Detección de patrocinados
                        patrocinado = False
                        try:
                            item.find_element(By.XPATH, ".//*[contains(text(), 'Patrocinado')]")
                            patrocinado = True
                        except NoSuchElementException:
                            pass

                        results.append({
                            'tienda': 'Amazon',
                            'titulo': name_elem.text.strip(),
                            'precio': price_elem.text.strip(),
                            'rating': rating_elem.text.strip(),
                            'url': self._clean_url(link_elem.get_attribute("href")),
                            'imagen': img_elem.get_attribute("src"),
                            'patrocinado': patrocinado
                        })

                        if len(results) >= max_results:
                            break
                    except Exception as e:
                        print(f"⚠️ Error extrayendo producto: {type(e).__name__} - {str(e)[:120]}")
                
                if len(results) < max_results:
                    # Intentar ir a la siguiente página
                    try:
                        next_button = self.driver.find_element(By.XPATH, "//a[contains(@class, 's-pagination-next')]")
                        if "disabled" in next_button.get_attribute("class"):
                            break
                        next_button.click()
                        self._human_like_delay(2, 4)
                    except NoSuchElementException:
                        break

        except Exception as e:
            print(f"❌ Error en AmazonScraper: {type(e).__name__} - {str(e)[:200]}")
        return results

    def _clean_url(self, url):
        if not url.startswith("http"):
            return url
        parsed = urlparse(url)
        allowed_params = ['keywords', 'node', 'ref', 'qid']
        clean_params = {k: v for k, v in parse_qs(parsed.query).items() if k in allowed_params}
        return parsed.scheme + "://" + parsed.netloc + parsed.path + (
            "?" + "&".join([f"{k}={v[0]}" for k, v in clean_params.items()]) if clean_params else ""
        )

    def _dismiss_popups(self):
        try:
            btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.ID, "sp-cc-rejectall-link"))
            )
            btn.click()
        except:
            pass

    def _human_like_delay(self, min_sec=1, max_sec=3):
        time.sleep(random.uniform(min_sec, max_sec))
