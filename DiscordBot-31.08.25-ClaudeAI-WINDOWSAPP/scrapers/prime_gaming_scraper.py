# scrapers/prime_gaming_scraper.py - Scraper specifico per Prime Gaming
from .base_scraper import BaseScraper
from typing import List, Dict
import re
import logging

logger = logging.getLogger("prime_gaming_bot.scraping")

class PrimeGamingScraper(BaseScraper):
    def __init__(self, cache_manager):
        super().__init__(cache_manager)
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
    
    async def scrape(self) -> List[Dict]:
        """Scraping specifico per Prime Gaming usando selettori testati"""
        try:
            url = f"{self.base_url}/home"
            soup = await self.fetch_page(url)
            
            if not soup:
                return []
            
            games = []
            
            # Usa i selettori CSS che hai testato
            game_links = soup.select("#offer-section-FGWP_FULL a")
            
            for link_element in game_links[:10]:  # Limita a 10 risultati
                try:
                    game_url = link_element.get('href')
                    if not game_url:
                        continue
                    
                    # Assicurati che sia un URL completo
                    if not game_url.startswith('http'):
                        game_url = f"{self.base_url}{game_url}"
                    
                    # Filtra solo i link validi come nel tuo codice
                    if not any(x in game_url for x in ('/offer/', '/dp/', '/product/')):
                        continue
                    
                    # Estrai immagine dal link principale
                    image_url = ""
                    try:
                        image_tag = link_element.select_one("figure picture img")
                        if image_tag:
                            image_url = image_tag.get('src', '')
                    except Exception:
                        image_url = ""
                    
                    # Ora scarica la pagina del gioco per i dettagli
                    game_soup = await self.fetch_page(game_url)
                    if not game_soup:
                        continue
                    
                    # Estrai dettagli usando i tuoi selettori testati
                    dettagli = self.estrai_dettagli_gioco(game_soup)
                    
                    if not dettagli.get("titolo") or dettagli["titolo"] == "N/D":
                        continue
                    
                    # Aggiungi URL e immagine ai dettagli
                    dettagli["link"] = game_url
                    dettagli["immagine"] = image_url
                    
                    # Crea i dati del gioco con tutte le informazioni
                    game_data = self.create_enhanced_game_data(dettagli)
                    if game_data:
                        games.append(game_data)
                        
                except Exception as e:
                    print(f"Errore nell'elaborazione di un elemento Prime Gaming: {e}")
                    continue
            
            self.cache_manager.update_last_scrape(self.platform_key)
            return games
            
        except Exception as e:
            print(f"Errore nello scraping di Prime Gaming: {e}")
            return []
    
    def estrai_dettagli_gioco(self, soup) -> Dict:
        """Estrae i dettagli del gioco usando i selettori testati"""
        def estrai(selector: str, descrizione: str) -> str:
            try:
                element = soup.select_one(selector)
                if element:
                    testo = element.get_text(strip=True)
                    logger.debug(f"Estrazione {descrizione}: {testo!r}")
                    return testo
            except Exception as e:
                logger.warning(f"Errore estrazione {descrizione} con selettore {selector}: {e}")
            return "N/D"

        # Usa i tuoi selettori testati
        titolo = estrai("div.detail-page-base__buy-box div.buy-box-item-information > div.tw-mg-b-1 > h1", "titolo")
        descrizione = estrai("div.detail-page-base__buy-box div.buy-box-item-information > div.tw-mg-b-2.tw-mg-t-1 > p", "descrizione")
        scadenza = estrai("div.availability-callout span.tw-bold", "scadenza")
        launcher_text = estrai("div.tw-border-radius-medium > div > div.tw-lg-mg-t-3.tw-mg-t-2 > div > p", "launcher_text")
        piattaforma = estrai("div.about-the-game__grid > div:nth-child(3) > div:nth-child(2) > p", "piattaforma")
        modalita = estrai("div.about-the-game__grid > div:nth-child(2) > div:nth-child(2) > p", "modalita")
        genere = estrai("div.about-the-game__grid > div:nth-child(1) > div:nth-child(2) > p", "genere")
        
        # Estrai launcher usando la tua funzione
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