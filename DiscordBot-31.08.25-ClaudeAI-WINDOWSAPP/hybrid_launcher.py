# ==========================================
# hybrid_launcher.py - Launcher che supporta sia desktop che web
# ==========================================

import sys
import argparse
from pathlib import Path

def main():
    """Launcher principale che supporta diverse modalità"""
    
    parser = argparse.ArgumentParser(description='Game Watch Bot - Multi-mode Launcher')
    parser.add_argument('--mode', choices=['desktop', 'web', 'discord'], default='desktop',
                       help='Modalità di esecuzione (default: desktop)')
    parser.add_argument('--port', type=int, default=5000,
                       help='Porta per il server web (default: 5000)')
    parser.add_argument('--host', default='127.0.0.1',
                       help='Host per il server web (default: 127.0.0.1)')
    
    args = parser.parse_args()
    
    # Aggiungi percorso corrente al PYTHONPATH
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    if args.mode == 'desktop':
        print("🖥️  Avvio modalità Desktop...")
        from PyQt6.QtWidgets import QApplication
        from main_app import GameWatchMainWindow
        
        app = QApplication(sys.argv)
        app.setApplicationName("Game Watch Bot")
        
        main_window = GameWatchMainWindow()
        main_window.show()
        
        sys.exit(app.exec())
        
    elif args.mode == 'web':
        print("🌐 Avvio modalità Web...")
        from web_interface import WebInterface
        from cache_manager import CacheManager
        from scrapers.prime_gaming_scraper import PrimeGamingScraper
        from scrapers.xbox_scraper import XboxGamePassScraper
        from scrapers.ps_plus_scraper import PSPlusScraper
        from config import CONFIG
        
        # Inizializza componenti
        cache_manager = CacheManager(CONFIG.cache_file)
        scrapers = {
            'prime_gaming': PrimeGamingScraper(cache_manager),
            'xbox_gamepass': XboxGamePassScraper(cache_manager),
            'ps_plus': PSPlusScraper(cache_manager)
        }
        
        web_interface = WebInterface(cache_manager, scrapers)
        web_interface.run(host=args.host, port=args.port, debug=True)
        
    elif args.mode == 'discord':
        print("🤖 Avvio modalità Discord Bot...")
        import asyncio
        from discord_bot import GamingBot
        from config import CONFIG
        
        async def run_discord_bot():
            bot = GamingBot()
            try:
                await bot.start(CONFIG.token)
            except KeyboardInterrupt:
                print("Bot fermato dall'utente")
            finally:
                if not bot.is_closed():
                    await bot.close()
        
        asyncio.run(run_discord_bot())
    
    else:
        print(f"❌ Modalità non supportata: {args.mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()