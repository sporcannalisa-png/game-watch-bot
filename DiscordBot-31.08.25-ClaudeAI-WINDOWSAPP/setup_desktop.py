# ==========================================
# setup_desktop.py - Script di setup automatico
# ==========================================

"""
Script di setup automatico per l'app desktop
"""

import os
import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Installa i requirements"""
    requirements = [
        "PyQt6>=6.6.0",
        "aiohttp>=3.8.0", 
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "selenium>=4.15.0",
        "requests>=2.31.0"
    ]
    
    for req in requirements:
        print(f"📦 Installando {req}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", req])

def setup_directories():
    """Crea le directory necessarie"""
    directories = ["logs", "data", "cache", "scrapers"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Creata directory: {directory}")

def create_config_files():
    """Crea i file di configurazione di esempio"""
    
    # config.py
    config_content = '''
import os
from dataclasses import dataclass
from typing import Dict

@dataclass
class BotConfig:
    token: str
    guild_id: int
    channels: Dict[str, int]
    cache_file: str = "games_cache.json"
    scrape_interval: int = 3600

# Configura qui i tuoi dati
CONFIG = BotConfig(
    token=os.getenv("DISCORD_TOKEN", "IL_TUO_BOT_TOKEN"),
    guild_id=123456789,
    channels={
        "prime_gaming": 123456789,
        "xbox_gamepass": 123456789,  
        "ps_plus": 123456789
    }
)
'''
    
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print("📝 Creato file config.py")

def main():
    """Funzione principale di setup"""
    print("🚀 Setup Game Watch Desktop App")
    print("=" * 40)
    
    try:
        print("1. Installazione dipendenze...")
        install_requirements()
        
        print("\n2. Creazione directories...")
        setup_directories()
        
        print("\n3. Creazione file di configurazione...")
        create_config_files()
        
        print("\n✅ Setup completato!")
        print("\n📋 Prossimi passi:")
        print("1. Configura le API key in config.py")
        print("2. Installa ChromeDriver per Selenium")
        print("3. Esegui: python run_desktop_app.py")
        print("4. (Opzionale) Crea eseguibile: python build_executable.py")
        
    except Exception as e:
        print(f"❌ Errore durante il setup: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()