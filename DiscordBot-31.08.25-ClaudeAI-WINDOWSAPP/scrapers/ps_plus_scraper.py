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
