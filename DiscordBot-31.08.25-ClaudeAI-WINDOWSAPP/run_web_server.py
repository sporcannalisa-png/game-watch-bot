# ==========================================
# run_web_server.py - Avvia il server web
# ==========================================

def run_web_server():
    """Avvia il server web per l'interfaccia React"""
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
    
    # Crea e avvia il server web
    web_interface = WebInterface(cache_manager, scrapers)
    
    print("🌐 Avvio server web su http://localhost:5000")
    print("💡 L'API è disponibile su /api/")
    print("📱 Interfaccia React (se disponibile) su /")
    
    web_interface.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    run_web_server()