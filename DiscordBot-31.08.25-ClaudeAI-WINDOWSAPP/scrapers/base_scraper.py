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