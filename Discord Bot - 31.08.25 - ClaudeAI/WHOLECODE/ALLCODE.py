# config.py - Configurazione centralizzata
import os
from dataclasses import dataclass
from typing import Dict

@dataclass
class BotConfig:
    token: str
    guild_id: int
    channels: Dict[str, int]
    cache_file: str = "games_cache.json"
    scrape_interval: int = 3600  # secondi (1 ora)

# Configura qui i tuoi dati
CONFIG = BotConfig(
    token=os.getenv("DISCORD_TOKEN", "IL_TUO_BOT_TOKEN"),
    guild_id=123456789,  # ID del tuo server
    channels={
        "prime_gaming": 123456789,    # ID canale Prime Gaming
        "xbox_gamepass": 123456789,   # ID canale Xbox Game Pass  
        "ps_plus": 123456789          # ID canale PS Plus
    }
)

# ==========================================

# cache_manager.py - Gestione della cache
import json
import hashlib
import os
from typing import Dict, List, Set
from datetime import datetime

class CacheManager:
    def __init__(self, cache_file: str):
        self.cache_file = cache_file
        self.cache_data = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Carica la cache dal file JSON"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Assicurati che tutte le chiavi esistano
                    for platform in ["prime_gaming", "xbox_gamepass", "ps_plus"]:
                        if platform not in data:
                            data[platform] = []
                    return data
            except Exception as e:
                print(f"Errore nel caricamento della cache: {e}")
        
        # Cache di default
        return {
            "prime_gaming": [],
            "xbox_gamepass": [],
            "ps_plus": [],
            "last_update": {}
        }
    
    def save_cache(self):
        """Salva la cache nel file JSON"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Errore nel salvataggio della cache: {e}")
    
    def get_content_hash(self, title: str, platform: str) -> str:
        """Genera un hash univoco per il contenuto"""
        content = f"{title}_{platform}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def is_duplicate(self, platform: str, game_hash: str) -> bool:
        """Controlla se il gioco è già presente nella cache"""
        return game_hash in self.cache_data.get(platform, [])
    
    def add_to_cache(self, platform: str, game_hash: str):
        """Aggiunge un hash alla cache della piattaforma"""
        if platform not in self.cache_data:
            self.cache_data[platform] = []
        
        if game_hash not in self.cache_data[platform]:
            self.cache_data[platform].append(game_hash)
            # Mantieni solo gli ultimi 100 hash per platform
            if len(self.cache_data[platform]) > 100:
                self.cache_data[platform] = self.cache_data[platform][-100:]
    
    def update_last_scrape(self, platform: str):
        """Aggiorna il timestamp dell'ultimo scraping"""
        if "last_update" not in self.cache_data:
            self.cache_data["last_update"] = {}
        self.cache_data["last_update"][platform] = datetime.now().isoformat()

# ==========================================

# scrapers/base_scraper.py - Classe base per tutti gli scraper
import aiohttp
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

class BaseScraper(ABC):
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.session: Optional[aiohttp.ClientSession] = None
        self.platform_name = ""
        self.platform_key = ""
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Ottiene o crea una sessione aiohttp"""
        if self.session is None or self.session.closed:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    @abstractmethod
    async def scrape(self) -> List[Dict]:
        """Metodo astratto per lo scraping - da implementare in ogni scraper"""
        pass
    
    async def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Effettua il fetch di una pagina e restituisce BeautifulSoup"""
        try:
            session = await self.get_session()
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    return BeautifulSoup(html, 'html.parser')
                else:
                    print(f"Errore HTTP {response.status} per {url}")
                    return None
        except Exception as e:
            print(f"Errore nel fetch di {url}: {e}")
            return None
    
    def create_game_data(self, title: str, image_url: str = "", game_url: str = "") -> Optional[Dict]:
        """Crea un oggetto dati del gioco se non è duplicato"""
        if not title.strip():
            return None
            
        game_hash = self.cache_manager.get_content_hash(title, self.platform_name)
        
        if self.cache_manager.is_duplicate(self.platform_key, game_hash):
            return None  # È un duplicato
        
        # Nuovo gioco trovato
        self.cache_manager.add_to_cache(self.platform_key, game_hash)
        
        return {
            'title': title.strip(),
            'image_url': image_url or '',
            'platform': self.platform_name,
            'url': game_url or '',
            'hash': game_hash
        }
    
    async def close(self):
        """Chiude la sessione aiohttp"""
        if self.session and not self.session.closed:
            await self.session.close()

# ==========================================

# scrapers/prime_gaming_scraper.py - Scraper specifico per Prime Gaming con Selenium
import os
import time
import re
import tempfile
import logging
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger("prime_gaming_bot.scraping")

class PrimeGamingScraper:
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.platform_name = "Prime Gaming"
        self.platform_key = "prime_gaming"
        self.base_url = "https://gaming.amazon.com"
    
    def extract_launcher(self, text: str) -> str:
        """Estrae il launcher dal testo della descrizione"""
        if not text:
            return "N/D"
        
        logger.debug(f"extract_launcher input: {text!r}")
        match = re.search(r'\bon\b\s+(.+?)(\.|$)', text, re.IGNORECASE)
        if match:
            launcher = match.group(1).strip().rstrip('.')
            logger.debug(f"extract_launcher output: {launcher!r}")
            return launcher
        logger.debug("extract_launcher output: N/D")
        return "N/D"
    
    def close_cookie_banner(self, driver):
        """Chiude il banner dei cookie se presente"""
        logger.debug("Trying to close cookie banner if present...")
        try:
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR,
                     "body > div:nth-child(10) > div > div > div > div.tw-justify-content-end.tw-pd-x-1 > div > button"))
            )
            btn.click()
            logger.info("Cookie banner chiuso.")
        except Exception as e:
            logger.debug(f"Nessun cookie banner da chiudere o errore: {e}")
    
    def get_game_links(self, driver):
        """Ottiene i link dei giochi dalla pagina principale"""
        logger.debug("Ricerca link giochi nella pagina principale...")
        elements = driver.find_elements(By.CSS_SELECTOR, "#offer-section-FGWP_FULL a")

        games = []
        for el in elements:
            url = el.get_attribute("href")
            if not url:
                continue

            # Estrai immagine (fallback se non trovata)
            try:
                image_tag = el.find_element(By.CSS_SELECTOR, "figure picture img")
                image_url = image_tag.get_attribute("src")
            except Exception:
                image_url = None

            games.append({
                "url": url,
                "image": image_url,
            })

        logger.info(f"Trovati {len(games)} giochi nella pagina principale.")
        return games
    
    def filter_game_links(self, links):
        """Filtra i link validi dei giochi"""
        logger.debug(f"Filtraggio link su {len(links)} elementi...")
        filtered = []
        seen_urls = set()
        for entry in links:
            url = entry['url']
            if url in seen_urls:
                logger.debug(f"Link duplicato ignorato: {url}")
                continue
            if any(x in url for x in ('/offer/', '/dp/', '/product/')):
                filtered.append(entry)
                seen_urls.add(url)
                logger.debug(f"Link valido aggiunto: {url}")
            else:
                logger.debug(f"Link scartato (non valido): {url}")
        logger.info(f"Filtrati {len(filtered)} link validi su {len(links)} totali")
        return filtered
    
    def estrai_dettagli_gioco(self, driver):
        """Estrae i dettagli del gioco usando i selettori testati"""
        def estrai(selector, descrizione):
            try:
                testo = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                logger.debug(f"Estrazione {descrizione}: {testo!r}")
                return testo
            except Exception as e:
                logger.warning(f"Errore estrazione {descrizione} con selettore {selector}: {e}")
                return "N/D"

        titolo = estrai("div.detail-page-base__buy-box div.buy-box-item-information > div.tw-mg-b-1 > h1", "titolo")
        descrizione = estrai("div.detail-page-base__buy-box div.buy-box-item-information > div.tw-mg-b-2.tw-mg-t-1 > p", "descrizione")
        scadenza = estrai("div.availability-callout span.tw-bold", "scadenza")
        launcher_text = estrai("div.tw-border-radius-medium > div > div.tw-lg-mg-t-3.tw-mg-t-2 > div > p", "launcher_text")
        piattaforma = estrai("div.about-the-game__grid > div:nth-child(3) > div:nth-child(2) > p", "piattaforma")
        modalita = estrai("div.about-the-game__grid > div:nth-child(2) > div:nth-child(2) > p", "modalita")
        genere = estrai("div.about-the-game__grid > div:nth-child(1) > div:nth-child(2) > p", "genere")
        
        # Estrai launcher usando la funzione testata
        launcher = self.extract_launcher(launcher_text)

        dettagli = {
            "titolo": titolo,
            "descrizione": descrizione,
            "scadenza": scadenza,
            "launcher": launcher,
            "piattaforma": piattaforma,
            "modalita": modalita,
            "genere": genere,
        }
        return dettagli
    
    def scroll_entire_page(self, driver, pause=0.7, scroll_px=300):
        """Scrolla l'intera pagina per caricare tutti i giochi"""
        logger.debug("Inizio scroll pagina per caricare tutti i giochi...")
        last_scroll_top = -1
        attempt = 0
        while True:
            driver.execute_script(f"document.querySelector('#root').scrollBy(0, {scroll_px});")
            time.sleep(pause)
            scroll_top = driver.execute_script("return document.querySelector('#root').scrollTop;")
            scroll_height = driver.execute_script("return document.querySelector('#root').scrollHeight;")
            client_height = driver.execute_script("return document.querySelector('#root').clientHeight;")
            logger.debug(f"Scroll pos: {scroll_top}, Altezza: {scroll_height}, Viewport: {client_height}")
            if scroll_top == last_scroll_top:
                logger.info("Scroll non avanzato, fine scroll.")
                break
            if scroll_top + client_height >= scroll_height:
                logger.info("Scroll raggiunta fine pagina.")
                break
            last_scroll_top = scroll_top
            attempt += 1
            if attempt > 1000:
                logger.warning("Troppi scroll, interrotto per sicurezza.")
                break
        logger.debug("Fine scroll pagina.")
    
    def create_enhanced_game_data(self, dettagli: Dict) -> Dict:
        """Crea i dati del gioco con tutte le informazioni estratte"""
        titolo = dettagli.get("titolo", "").strip()
        if not titolo or titolo == "N/D":
            return None
            
        game_hash = self.cache_manager.get_content_hash(titolo, self.platform_name)
        
        if self.cache_manager.is_duplicate(self.platform_key, game_hash):
            return None  # È un duplicato
        
        # Nuovo gioco trovato
        self.cache_manager.add_to_cache(self.platform_key, game_hash)
        
        return {
            'title': titolo,
            'descrizione': dettagli.get("descrizione", ""),
            'scadenza': dettagli.get("scadenza", ""),
            'launcher': dettagli.get("launcher", "N/D"),
            'piattaforma': dettagli.get("piattaforma", "N/D"),
            'modalita': dettagli.get("modalita", "N/D"),
            'genere': dettagli.get("genere", "N/D"),
            'image_url': dettagli.get("immagine", ""),
            'platform': self.platform_name,
            'url': dettagli.get("link", ""),
            'hash': game_hash
        }
    
    async def scrape(self) -> List[Dict]:
        """Scraping specifico per Prime Gaming usando Selenium"""
        logger.info("Avvio scraping Prime Gaming con Selenium...")
        
        # Configurazione Chrome
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        # Path del chromedriver
        if os.name == "nt":  # Windows
            chromedriver_path = "chromedriver.exe"
        else:  # Linux/Mac
            chromedriver_path = "/usr/bin/chromedriver"
            if not os.path.isfile(chromedriver_path):
                # Prova percorsi alternativi
                alternative_paths = [
                    "/usr/local/bin/chromedriver",
                    "./chromedriver",
                    "chromedriver"
                ]
                for path in alternative_paths:
                    if os.path.isfile(path):
                        chromedriver_path = path
                        break
                else:
                    logger.error(f"chromedriver non trovato. Assicurati di averlo installato.")
                    return []

        service = Service(chromedriver_path)
        giochi_dettagliati = []

        try:
            with tempfile.TemporaryDirectory() as tmp_profile:
                options.add_argument(f"--user-data-dir={tmp_profile}")
                driver = webdriver.Chrome(service=service, options=options)
                wait = WebDriverWait(driver, 20)

                try:
                    logger.info("Apro pagina principale Prime Gaming...")
                    driver.get(f"{self.base_url}/home")

                    # Chiudi banner cookie
                    self.close_cookie_banner(driver)

                    # Clicca il bottone "Giochi"
                    try:
                        logger.info("Aspetto e clicco il bottone 'Giochi'...")
                        giochi_button = wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                '#SearchBar > div > div.offer-filters.offer-filters__gradient-right.tw-flex.tw-flex-grow-1.tw-full-width.tw-mg-b-1.tw-overflow-auto.tw-pd-r-1.tw-sm-mg-b-0 > div > div:nth-child(2) > button')))
                        
                        giochi_button.click()
                        logger.info("Bottone 'Giochi' cliccato.")
                    except Exception as e:
                        logger.warning(f"Bottone 'Giochi' non trovato, continuo comunque: {e}")

                    # Aspetta che la sezione giochi sia caricata
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#offer-section-FGWP_FULL")))
                    
                    # Scrolla per caricare tutti i giochi
                    self.scroll_entire_page(driver)

                    # Ottieni e filtra i link dei giochi
                    link_entries = self.filter_game_links(self.get_game_links(driver))
                    logger.info(f"Trovati {len(link_entries)} link dopo il filtro.")

                    # Processa ogni gioco (limita a 10 per evitare troppo carico)
                    for i, entry in enumerate(link_entries[:10], 1):
                        try:
                            logger.info(f"Processando gioco {i}/{min(len(link_entries), 10)}: {entry['url']}")
                            driver.get(entry["url"])
                            
                            # Aspetta che la pagina del gioco si carichi
                            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.buy-box-item-information h1")))
                            
                            # Estrai dettagli
                            dettagli = self.estrai_dettagli_gioco(driver)
                            dettagli["link"] = entry["url"]
                            dettagli["immagine"] = entry.get("image")
                            
                            # Crea i dati del gioco
                            game_data = self.create_enhanced_game_data(dettagli)
                            if game_data:
                                giochi_dettagliati.append(game_data)
                                logger.info(f"Gioco aggiunto: {dettagli.get('titolo', 'N/D')}")
                            else:
                                logger.info(f"Gioco già presente in cache: {dettagli.get('titolo', 'N/D')}")

                        except Exception as e:
                            logger.warning(f"Errore durante l'estrazione del gioco {i}: {e}")
                            continue

                finally:
                    driver.quit()
                    logger.info("Browser chiuso.")

            # Aggiorna timestamp ultimo scraping
            self.cache_manager.update_last_scrape(self.platform_key)
            logger.info(f"Scraping Prime Gaming completato. Trovati {len(giochi_dettagliati)} nuovi giochi.")
            return giochi_dettagliati

        except Exception as e:
            logger.error(f"Errore generale nello scraping di Prime Gaming: {e}")
            return []
    
    async def close(self):
        """Metodo di cleanup (non necessario per Selenium ma manteniamo la consistenza)"""
        pass

# ==========================================

# scrapers/xbox_scraper.py - Scraper specifico per Xbox Game Pass con API
import aiohttp
import asyncio
from typing import List, Dict
import logging

logger = logging.getLogger("xbox_gamepass_bot.scraping")

class XboxGamePassScraper:
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.platform_name = "Xbox Game Pass"
        self.platform_key = "xbox_gamepass"
        
        # API Endpoints
        self.XBL_API_URL = "https://xbl.io/api/v2/gamepass-games"
        self.MS_DISPLAYCATALOG_URL = "https://displaycatalog.mp.microsoft.com/v7.0/products"
        
        # Configura qui la tua API Key di xbl.io
        self.XBL_API_KEY = "TUA_XBL_API_KEY_QUI"  # Sostituisci con la tua key
        
        self.session = None
    
    async def get_session(self):
        """Ottiene o crea una sessione aiohttp"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    def normalizza_genere(self, categorie: List[str]) -> str:
        """Normalizza le categorie in generi leggibili"""
        if not categorie:
            return "N/D"
        
        mapping_generi = {
            "Action & adventure": "Azione e Avventura",
            "Fighting": "Picchiaduro", 
            "Platformer": "Platform",
            "Puzzle & trivia": "Puzzle",
            "Racing & flying": "Corse",
            "Role playing": "RPG",
            "Shooter": "Sparatutto",
            "Simulation": "Simulazione",
            "Sports": "Sport",
            "Strategy": "Strategia"
        }
        
        generi_normalizzati = []
        for cat in categorie:
            genere = mapping_generi.get(cat, cat)
            if genere not in generi_normalizzati:
                generi_normalizzati.append(genere)
        
        return ", ".join(generi_normalizzati) if generi_normalizzati else "N/D"
    
    def normalizza_piattaforma(self, piattaforme_raw: List[str]) -> List[str]:
        """Normalizza i nomi delle piattaforme"""
        if not piattaforme_raw:
            return ["N/D"]
        
        mapping_piattaforme = {
            "Windows.Desktop": "PC",
            "Windows.Xbox": "Xbox",
            "Windows.Mobile": "Mobile",
            "Xbox.XboxOne": "Xbox One",
            "Xbox.Scarlett": "Xbox Series X|S"
        }
        
        piattaforme_normalizzate = []
        for plat in piattaforme_raw:
            piattaforma = mapping_piattaforme.get(plat, plat)
            if piattaforma not in piattaforme_normalizzate:
                piattaforme_normalizzate.append(piattaforma)
        
        return piattaforme_normalizzate if piattaforme_normalizzate else ["N/D"]
    
    async def fetch_game_ids(self) -> List[str]:
        """Recupera gli ID dei giochi da xbl.io API"""
        session = await self.get_session()
        headers = {
            "X-Authorization": self.XBL_API_KEY,
            "Accept": "application/json"
        }
        
        try:
            async with session.get(self.XBL_API_URL, headers=headers, timeout=15) as response:
                if response.status != 200:
                    logger.error(f"Errore API xbl.io: {response.status}")
                    return []
                
                data = await response.json()
                
        except Exception as e:
            logger.error(f"Errore nella richiesta a xbl.io: {e}")
            return []

        game_ids = []
        for game in data:
            product_id = game.get("id")
            if product_id:
                game_ids.append(product_id)

        logger.info(f"Trovati {len(game_ids)} ID di giochi validi.")
        return game_ids
    
    async def fetch_game_details(self, ids: List[str]) -> List[Dict]:
        """Recupera i dettagli dei giochi da Microsoft DisplayCatalog API"""
        if not ids:
            return []

        session = await self.get_session()
        params = {
            "bigIds": ",".join(ids),
            "market": "IT",
            "languages": "it-it",
            "MS-CV": "DGU1mcuYo0WMMp+F.1"
        }

        try:
            async with session.get(self.MS_DISPLAYCATALOG_URL, params=params, timeout=15) as response:
                if response.status != 200:
                    logger.error(f"Errore DisplayCatalog API: {response.status}")
                    return []
                
                data = await response.json()
                
        except Exception as e:
            logger.error(f"Errore nel recupero dei dettagli da displaycatalog: {e}")
            return []

        risultati = []

        for prodotto in data.get("Products", []):
            props = prodotto.get("LocalizedProperties", [{}])[0]
            titolo = props.get("ProductTitle", "N/D")
            descrizione = props.get("ShortDescription", "N/D")
            immagini = props.get("Images", [])
            image_url = next((img.get("Uri") for img in immagini if img.get("ImagePurpose") == "Poster"), "N/D")
            link = f"https://www.microsoft.com/it-it/p/{prodotto.get('ProductId', '')}"

            properties = prodotto.get("Properties", {})
            categorie = properties.get("Categories", [])
            genere = self.normalizza_genere(categorie)

            data_rilascio = "N/D"
            data_ultima_modifica = prodotto.get("RevisionId", "N/D")

            prezzo = "N/D"
            valuta = "N/D"
            piattaforme_raw = []
            start_date = "N/D"
            end_date = "N/D"

            display_skus = prodotto.get("DisplaySkuAvailabilities", [])
            if display_skus:
                sku = display_skus[0]
                market_props = sku.get("MarketProperties", [])
                if market_props:
                    data_rilascio = market_props[0].get("FirstAvailableDate", "N/D")

                availabilities = sku.get("Availabilities", [])
                if availabilities:
                    av = availabilities[0]
                    conditions = av.get("Conditions", {})
                    client_conditions = conditions.get("ClientConditions", {})
                    allowed_platforms = client_conditions.get("AllowedPlatforms", [])
                    piattaforme_raw = [p.get("PlatformName", "N/D") for p in allowed_platforms]

                    start_date = conditions.get("StartDate", "N/D")
                    end_date = conditions.get("EndDate", "N/D")

                    order_data = av.get("OrderManagementData", {})
                    price_info = order_data.get("Price", {})
                    list_price = price_info.get("ListPrice", None)
                    currency_code = price_info.get("CurrencyCode", None)
                    if list_price is not None and currency_code is not None:
                        prezzo = f"{list_price} {currency_code}"

            piattaforme = self.normalizza_piattaforma(piattaforme_raw)

            publisher = "N/D"
            rating = "N/D"
            attributes = properties.get("Attributes", [])
            for attr in attributes:
                if attr.get("Name") == "Publisher" and "Value" in attr:
                    publisher = attr["Value"]
                if attr.get("Name") == "ContentRating" and "Value" in attr:
                    rating = attr["Value"]

            risultati.append({
                "titolo": titolo,
                "descrizione": descrizione,
                "genere": genere,
                "publisher": publisher,
                "data_rilascio": data_rilascio,
                "data_ultima_modifica": data_ultima_modifica,
                "prezzo": prezzo,
                "rating": rating,
                "piattaforme": ", ".join(piattaforme),
                "start_date": start_date,
                "end_date": end_date,
                "link": link,
                "immagine": image_url
            })

        logger.info(f"Recuperati dettagli per {len(risultati)} giochi.")
        return risultati
    
    def create_enhanced_game_data(self, dettagli: Dict) -> Dict:
        """Crea i dati del gioco con tutte le informazioni estratte"""
        titolo = dettagli.get("titolo", "").strip()
        if not titolo or titolo == "N/D":
            return None
            
        game_hash = self.cache_manager.get_content_hash(titolo, self.platform_name)
        
        if self.cache_manager.is_duplicate(self.platform_key, game_hash):
            return None  # È un duplicato
        
        # Nuovo gioco trovato
        self.cache_manager.add_to_cache(self.platform_key, game_hash)
        
        return {
            'title': titolo,
            'descrizione': dettagli.get("descrizione", ""),
            'genere': dettagli.get("genere", "N/D"),
            'publisher': dettagli.get("publisher", "N/D"),
            'data_rilascio': dettagli.get("data_rilascio", "N/D"),
            'prezzo': dettagli.get("prezzo", "N/D"),
            'rating': dettagli.get("rating", "N/D"),
            'piattaforme': dettagli.get("piattaforme", "N/D"),
            'start_date': dettagli.get("start_date", "N/D"),
            'end_date': dettagli.get("end_date", "N/D"),
            'image_url': dettagli.get("immagine", ""),
            'platform': self.platform_name,
            'url': dettagli.get("link", ""),
            'hash': game_hash
        }
    
    async def scrape(self) -> List[Dict]:
        """Scraping specifico per Xbox Game Pass usando API"""
        logger.info("Avvio scraping Xbox Game Pass...")
        
        try:
            # Step 1: Recupera gli ID dei giochi
            game_ids = await self.fetch_game_ids()
            if not game_ids:
                logger.warning("Nessun ID di gioco trovato")
                return []
            
            # Step 2: Recupera i dettagli per batch di 20 giochi
            all_games = []
            batch_size = 20
            
            for i in range(0, len(game_ids), batch_size):
                batch_ids = game_ids[i:i + batch_size]
                logger.info(f"Processando batch {i//batch_size + 1}: {len(batch_ids)} giochi")
                
                game_details = await self.fetch_game_details(batch_ids)
                
                # Processa ogni gioco nel batch
                for dettagli in game_details:
                    game_data = self.create_enhanced_game_data(dettagli)
                    if game_data:
                        all_games.append(game_data)
                        logger.info(f"Gioco aggiunto: {dettagli.get('titolo', 'N/D')}")
                    else:
                        logger.debug(f"Gioco già presente in cache: {dettagli.get('titolo', 'N/D')}")
                
                # Pausa tra i batch per evitare rate limiting
                await asyncio.sleep(1)
            
            # Aggiorna timestamp ultimo scraping
            self.cache_manager.update_last_scrape(self.platform_key)
            logger.info(f"Scraping Xbox Game Pass completato. Trovati {len(all_games)} nuovi giochi.")
            return all_games
            
        except Exception as e:
            logger.error(f"Errore generale nello scraping di Xbox Game Pass: {e}")
            return []
    
    async def close(self):
        """Chiude la sessione aiohttp"""
        if self.session and not self.session.closed:
            await self.session.close()

# ==========================================

# scrapers/ps_plus_scraper.py - Scraper specifico per PlayStation Plus
from .base_scraper import BaseScraper  
from typing import List, Dict

class PSPlusScraper(BaseScraper):
    def __init__(self, cache_manager):
        super().__init__(cache_manager)
        self.platform_name = "PlayStation Plus"
        self.platform_key = "ps_plus"
        self.base_url = "https://www.playstation.com"
    
    async def scrape(self) -> List[Dict]:
        """Scraping specifico per PlayStation Plus"""
        try:
            url = f"{self.base_url}/it-it/ps-plus/"
            soup = await self.fetch_page(url)
            
            if not soup:
                return []
            
            games = []
            
            # Selettori per PlayStation Plus
            game_containers = soup.select('[data-testid="game-card"], .game-item, .product-item')
            
            for container in game_containers[:10]:
                try:
                    # Cerca il titolo
                    title_element = (
                        container.select_one('[data-testid="game-title"]') or
                        container.select_one('.game-title') or
                        container.select_one('.product-title') or
                        container.select_one('h3')
                    )
                    
                    if not title_element:
                        continue
                    
                    title = title_element.get_text(strip=True)
                    
                    # Cerca l'immagine
                    image_element = container.select_one('img')
                    image_url = image_element.get('src', '') if image_element else ''
                    
                    game_data = self.create_game_data(title, image_url, url)
                    if game_data:
                        games.append(game_data)
                        
                except Exception as e:
                    print(f"Errore nell'elaborazione di un elemento PS Plus: {e}")
                    continue
            
            self.cache_manager.update_last_scrape(self.platform_key)
            return games
            
        except Exception as e:
            print(f"Errore nello scraping di PlayStation Plus: {e}")
            return []

# ==========================================

# discord_bot.py - Bot Discord principale
import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime
from config import CONFIG
from cache_manager import CacheManager
from scrapers.prime_gaming_scraper import PrimeGamingScraper
from scrapers.xbox_scraper import XboxGamePassScraper
from scrapers.ps_plus_scraper import PSPlusScraper

class GamingBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        # Inizializza cache e scrapers
        self.cache_manager = CacheManager(CONFIG.cache_file)
        self.scrapers = {
            'prime_gaming': PrimeGamingScraper(self.cache_manager),
            'xbox_gamepass': XboxGamePassScraper(self.cache_manager),
            'ps_plus': PSPlusScraper(self.cache_manager)
        }
    
    async def setup_hook(self):
        """Chiamato quando il bot si avvia"""
        print(f"Bot avviato come {self.user}")
        self.scraping_task.start()
    
    @tasks.loop(seconds=CONFIG.scrape_interval)
    async def scraping_task(self):
        """Task periodico per lo scraping"""
        print(f"Avvio scraping alle {datetime.now()}")
        
        for platform_key, scraper in self.scrapers.items():
            try:
                channel_id = CONFIG.channels.get(platform_key)
                if not channel_id:
                    continue
                
                channel = self.get_channel(channel_id)
                if not channel:
                    print(f"Canale non trovato per {platform_key}")
                    continue
                
                # Effettua lo scraping
                new_games = await scraper.scrape()
                
                # Invia i nuovi giochi trovati
                for game in new_games:
                    embed = self.create_game_embed(game)
                    try:
                        await channel.send(embed=embed)
                        await asyncio.sleep(1)  # Evita rate limiting
                    except Exception as e:
                        print(f"Errore nell'invio del messaggio: {e}")
                
                print(f"{platform_key}: {len(new_games)} nuovi giochi trovati")
                
            except Exception as e:
                print(f"Errore nello scraping di {platform_key}: {e}")
        
        # Salva la cache
        self.cache_manager.save_cache()
        print("Scraping completato")
    
    @scraping_task.before_loop
    async def before_scraping_task(self):
        """Aspetta che il bot sia pronto prima di iniziare lo scraping"""
        await self.wait_until_ready()
    
    def create_game_embed(self, game_data: dict) -> discord.Embed:
        """Crea un embed Discord per un gioco"""
        title = game_data.get('title', 'Gioco sconosciuto')
        platform = game_data.get('platform', 'Piattaforma sconosciuta')
        
        # Descrizione base
        description = f"Nuovo gioco disponibile su **{platform}**!"
        if game_data.get('descrizione') and game_data['descrizione'] != "N/D":
            # Limita la descrizione a 200 caratteri
            desc_text = game_data['descrizione'][:200]
            if len(game_data['descrizione']) > 200:
                desc_text += "..."
            description += f"\n\n*{desc_text}*"
        
        embed = discord.Embed(
            title=f"🎮 {title}",
            description=description,
            color=self.get_platform_color(platform),
            timestamp=datetime.now()
        )
        
        # Immagine del gioco
        if game_data.get('image_url'):
            embed.set_thumbnail(url=game_data['image_url'])
        
        # Campi specifici per piattaforma
        if platform == "Prime Gaming":
            if game_data.get('launcher') and game_data['launcher'] != "N/D":
                embed.add_field(name="📱 Launcher", value=game_data['launcher'], inline=True)
            
            if game_data.get('genere') and game_data['genere'] != "N/D":
                embed.add_field(name="🎯 Genere", value=game_data['genere'], inline=True)
            
            if game_data.get('modalita') and game_data['modalita'] != "N/D":
                embed.add_field(name="👥 Modalità", value=game_data['modalita'], inline=True)
            
            if game_data.get('piattaforma') and game_data['piattaforma'] != "N/D":
                embed.add_field(name="💻 Piattaforma", value=game_data['piattaforma'], inline=True)
            
            if game_data.get('scadenza') and game_data['scadenza'] != "N/D":
                embed.add_field(name="⏰ Scadenza", value=game_data['scadenza'], inline=True)
        
        elif platform == "Xbox Game Pass":
            if game_data.get('genere') and game_data['genere'] != "N/D":
                embed.add_field(name="🎯 Genere", value=game_data['genere'], inline=True)
            
            if game_data.get('publisher') and game_data['publisher'] != "N/D":
                embed.add_field(name="🏢 Publisher", value=game_data['publisher'], inline=True)
            
            if game_data.get('piattaforme') and game_data['piattaforme'] != "N/D":
                embed.add_field(name="💻 Piattaforme", value=game_data['piattaforme'], inline=True)
            
            if game_data.get('rating') and game_data['rating'] != "N/D":
                embed.add_field(name="🔞 Rating", value=game_data['rating'], inline=True)
            
            if game_data.get('data_rilascio') and game_data['data_rilascio'] != "N/D":
                # Formatta la data se possibile
                try:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(game_data['data_rilascio'].replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime("%d/%m/%Y")
                    embed.add_field(name="📅 Data Rilascio", value=formatted_date, inline=True)
                except:
                    embed.add_field(name="📅 Data Rilascio", value=game_data['data_rilascio'], inline=True)
            
            if game_data.get('prezzo') and game_data['prezzo'] != "N/D":
                embed.add_field(name="💰 Prezzo", value=game_data['prezzo'], inline=True)
        
        # Link al gioco
        if game_data.get('url'):
            embed.add_field(name="🔗 Link", value=f"[Vai al gioco]({game_data['url']})", inline=False)
        
        embed.set_footer(text=f"Scraping Bot • {platform}")
        
        return embed
    
    def get_platform_color(self, platform: str) -> int:
        """Restituisce un colore specifico per ogni piattaforma"""
        colors = {
            "Prime Gaming": 0x00A8FF,      # Blu Amazon
            "Xbox Game Pass": 0x107C10,    # Verde Xbox
            "PlayStation Plus": 0x003087   # Blu PlayStation
        }
        return colors.get(platform, 0x7289DA)  # Default Discord blurple
    
    @commands.command(name='scrape')
    async def manual_scrape(self, ctx):
        """Comando per avviare manualmente lo scraping"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Solo gli amministratori possono usare questo comando!")
            return
        
        await ctx.send("🔄 Avvio scraping manuale...")
        await self.scraping_task()
        await ctx.send("✅ Scraping completato!")
    
    @commands.command(name='status')
    async def bot_status(self, ctx):
        """Mostra lo stato del bot e dell'ultima scansione"""
        embed = discord.Embed(title="📊 Status Bot", color=0x00FF00)
        
        last_updates = self.cache_manager.cache_data.get('last_update', {})
        
        for platform_key, scraper in self.scrapers.items():
            last_update = last_updates.get(platform_key, "Mai")
            if last_update != "Mai":
                last_update = datetime.fromisoformat(last_update).strftime("%d/%m/%Y %H:%M")
            
            cache_size = len(self.cache_manager.cache_data.get(platform_key, []))
            embed.add_field(
                name=scraper.platform_name,
                value=f"Ultimo aggiornamento: {last_update}\nGames in cache: {cache_size}",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    async def close(self):
        """Pulizia quando il bot si chiude"""
        for scraper in self.scrapers.values():
            await scraper.close()
        await super().close()

# ==========================================

# main.py - File principale per avviare il bot
import asyncio
from discord_bot import GamingBot
from config import CONFIG

async def main():
    bot = GamingBot()
    
    try:
        await bot.start(CONFIG.token)
    except KeyboardInterrupt:
        print("Bot fermato dall'utente")
    except Exception as e:
        print(f"Errore nell'avvio del bot: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())

# ==========================================

# requirements.txt
"""
discord.py>=2.3.0
aiohttp>=3.8.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
selenium>=4.15.0
"""