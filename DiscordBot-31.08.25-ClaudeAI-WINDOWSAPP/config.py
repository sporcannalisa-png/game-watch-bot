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