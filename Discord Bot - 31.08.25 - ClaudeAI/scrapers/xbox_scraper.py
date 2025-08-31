# scrapers/xbox_scraper.py - Scraper specifico per Xbox Game Pass  
from .base_scraper import BaseScraper
from typing import List, Dict

class XboxGamePassScraper(BaseScraper):
    def __init__(self, cache_manager):
        super().__init__(cache_manager)
        self.platform_name = "Xbox Game Pass"
        self.platform_key = "xbox_gamepass"
        self.base_url = "https://www.xbox.com"
    
    async def scrape(self) -> List[Dict]:
        """Scraping specifico per Xbox Game Pass"""
        try:
            url = f"{self.base_url}/it-IT/xbox-game-pass/games"
            soup = await self.fetch_page(url)
            
            if not soup:
                return []
            
            games = []
            
            # Selettori per Xbox Game Pass
            game_containers = soup.select('.gameDiv, [data-testid="game-item"], .game-card')
            
            for container in game_containers[:10]:
                try:
                    # Cerca il titolo
                    title_element = (
                        container.select_one('.gameDivTitle') or
                        container.select_one('[data-testid="game-title"]') or
                        container.select_one('.game-title') or
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
                    print(f"Errore nell'elaborazione di un elemento Xbox: {e}")
                    continue
            
            self.cache_manager.update_last_scrape(self.platform_key)
            return games
            
        except Exception as e:
            print(f"Errore nello scraping di Xbox Game Pass: {e}")
            return []