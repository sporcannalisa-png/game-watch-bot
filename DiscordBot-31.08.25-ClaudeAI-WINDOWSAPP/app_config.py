# ==========================================
# app_config.py - Configurazione Desktop App
# ==========================================

import os
from dataclasses import dataclass
from typing import Dict

@dataclass
class DesktopAppConfig:
    """Configurazione per l'app desktop"""
    # Percorsi file
    cache_file: str = "games_cache.json"
    data_file: str = "games_data.json"
    log_file: str = "app.log"
    
    # Configurazione scraping
    default_scraping_interval: int = 60  # minuti
    max_concurrent_scrapers: int = 3
    scraping_timeout: int = 300  # secondi
    
    # Configurazione UI
    window_width: int = 1200
    window_height: int = 800
    games_per_row: int = 4
    card_width: int = 280
    card_height: int = 200
    
    # API Keys (da configurare)
    xbl_api_key: str = os.getenv("XBL_API_KEY", "")
    
    # Discord bot (opzionale - se vuoi anche il bot Discord)
    discord_enabled: bool = False
    discord_token: str = os.getenv("DISCORD_TOKEN", "")
    discord_channels: Dict[str, int] = None

DESKTOP_CONFIG = DesktopAppConfig()