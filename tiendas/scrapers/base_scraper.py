from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import random
import time
import os
from abc import ABC, abstractmethod
import requests
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class BaseScraper(ABC):
    def __init__(self, headless=True, use_proxy=False):
        self.driver = self._init_driver(headless, use_proxy)
        self._apply_stealth_settings()
        
    def _init_driver(self, headless, use_proxy):
        chrome_options = Options()
        
        # Configuración anti-detección avanzada
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-browser-side-navigation")
        chrome_options.add_argument("--dns-prefetch-disable")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--ignore-certificate-errors")
        
        # User-Agent aleatorio realista
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
        ]
        user_agent = random.choice(user_agents)
        chrome_options.add_argument(f"user-agent={user_agent}")
        
        # Tamaño de ventana aleatorio
        width = random.randint(1200, 1400)
        height = random.randint(800, 1000)
        chrome_options.add_argument(f"--window-size={width},{height}")
        
        if headless:
            chrome_options.add_argument("--headless=new")
        
        # Configuración de proxy si se requiere
        if use_proxy:
            proxy = self._get_random_proxy()
            chrome_options.add_argument(f'--proxy-server={proxy}')
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Directorio para perfiles de usuario
        profile_path = f"profiles/profile_{random.randint(1, 1000)}"
        if not os.path.exists(profile_path):
            os.makedirs(profile_path)
        chrome_options.add_argument(f"user-data-dir={os.path.abspath(profile_path)}")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Configuración adicional para evitar detección
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent})
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _get_random_proxy(self):
        """Obtiene un proxy aleatorio de una lista o API"""
        # Lista de proxies gratuitos (reemplazar con servicio premium para producción)
        proxies = [
            'http://45.77.56.113:3128',
            'http://138.197.222.35:8080',
            'http://165.227.36.231:3128',
            'http://68.183.221.156:80'
        ]
        return random.choice(proxies)
    
    def _apply_stealth_settings(self):
        """Aplica configuraciones adicionales para evitar detección"""
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                const newProto = navigator.__proto__;
                delete newProto.webdriver;
                navigator.__proto__ = newProto;
                
                window.navigator.chrome = {
                    runtime: {},
                };
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['es-MX', 'es', 'en-US', 'en'],
                });
            '''
        })
    
    def _human_like_delay(self, min_sec=0.5, max_sec=2.0):
        """Retraso aleatorio para simular comportamiento humano"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def _human_type(self, element, text):
        """Simula escritura humana con errores ocasionales"""
        for char in text:
            element.send_keys(char)
            self._human_like_delay(0.1, 0.3)
            # Simular error humano ocasional (10% de probabilidad)
            if random.random() > 0.9:
                element.send_keys(Keys.BACK_SPACE)
                self._human_like_delay(0.2, 0.4)
                element.send_keys(char)
    
    def _simulate_human_scroll(self):
        """Simula desplazamiento humano con variaciones"""
        scroll_pauses = [0.5, 1.2, 0.8, 1.5]
        scroll_amounts = [300, 500, 200, 400]
        
        for pause, amount in zip(scroll_pauses, scroll_amounts):
            self.driver.execute_script(f"window.scrollBy(0, {amount});")
            time.sleep(pause)
    
    def _simulate_mouse_movement(self):
        """Simula movimiento de ratón humano"""
        actions = ActionChains(self.driver)
        actions.move_by_offset(random.randint(5, 20), random.randint(5, 20)).perform()
        self._human_like_delay(0.2, 0.5)
    
    @abstractmethod
    def search_products(self, query, max_results):
        pass
    
    def close(self):
        """Cierra el navegador correctamente"""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()