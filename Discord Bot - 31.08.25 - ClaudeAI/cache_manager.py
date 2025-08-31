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