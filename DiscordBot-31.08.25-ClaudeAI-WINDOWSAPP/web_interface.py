# ==========================================
# web_interface.py - Interfaccia web opzionale (integrazione con React)
# ==========================================

"""
Interfaccia web opzionale che espone API REST per integrare con il frontend React
del repository GitHub originale
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
from datetime import datetime
from pathlib import Path
import threading
import asyncio

class WebInterface:
    """Interfaccia web per integrare con il frontend React"""
    
    def __init__(self, cache_manager, scrapers):
        self.app = Flask(__name__)
        CORS(self.app)  # Abilita CORS per il frontend React
        
        self.cache_manager = cache_manager
        self.scrapers = scrapers
        self.games_data = self.load_games_data()
        
        self.setup_routes()
    
    def setup_routes(self):
        """Configura le route API"""
        
        @self.app.route('/api/games', methods=['GET'])
        def get_games():
            """Restituisce tutti i giochi"""
            platform = request.args.get('platform')
            
            if platform and platform in self.games_data:
                return jsonify(self.games_data[platform])
            else:
                # Restituisci tutti i giochi
                all_games = []
                for platform_games in self.games_data.values():
                    all_games.extend(platform_games)
                return jsonify(all_games)
        
        @self.app.route('/api/platforms', methods=['GET'])
        def get_platforms():
            """Restituisce le piattaforme disponibili"""
            platforms = []
            for key, scraper in self.scrapers.items():
                platforms.append({
                    'key': key,
                    'name': scraper.platform_name,
                    'game_count': len(self.games_data.get(key, []))
                })
            return jsonify(platforms)
        
        @self.app.route('/api/scrape', methods=['POST'])
        def start_scraping():
            """Avvia lo scraping"""
            data = request.json
            platform = data.get('platform', 'all')
            
            if platform == 'all':
                # Avvia scraping per tutte le piattaforme
                threading.Thread(target=self.run_all_scraping, daemon=True).start()
                return jsonify({'status': 'started', 'message': 'Scraping avviato per tutte le piattaforme'})
            elif platform in self.scrapers:
                # Avvia scraping per una piattaforma specifica
                threading.Thread(target=self.run_platform_scraping, args=(platform,), daemon=True).start()
                return jsonify({'status': 'started', 'message': f'Scraping avviato per {platform}'})
            else:
                return jsonify({'status': 'error', 'message': 'Piattaforma non valida'}), 400
        
        @self.app.route('/api/stats', methods=['GET'])
        def get_stats():
            """Restituisce le statistiche"""
            stats = {}
            
            for platform_key, games in self.games_data.items():
                scraper = self.scrapers.get(platform_key)
                platform_name = scraper.platform_name if scraper else platform_key
                
                # Calcola statistiche
                total_games = len(games)
                recent_games = len([g for g in games if self.is_recent_game(g)])
                
                stats[platform_key] = {
                    'name': platform_name,
                    'total_games': total_games,
                    'recent_games': recent_games,
                    'last_update': self.cache_manager.cache_data.get('last_update', {}).get(platform_key, 'Mai')
                }
            
            return jsonify(stats)
        
        @self.app.route('/api/clear', methods=['POST'])
        def clear_data():
            """Pulisce i dati"""
            data = request.json
            platform = data.get('platform')
            
            if platform and platform in self.games_data:
                self.games_data[platform] = []
            else:
                # Pulisci tutti i dati
                for key in self.games_data:
                    self.games_data[key] = []
            
            self.save_games_data()
            return jsonify({'status': 'success', 'message': 'Dati puliti'})
        
        # Serve i file statici del frontend React (se compilato)
        @self.app.route('/', defaults={'path': ''})
        @self.app.route('/<path:path>')
        def serve_react_app(path):
            """Serve l'app React"""
            react_build_dir = Path('frontend/build')
            if react_build_dir.exists():
                if path != "" and (react_build_dir / path).exists():
                    return send_from_directory(react_build_dir, path)
                else:
                    return send_from_directory(react_build_dir, 'index.html')
            else:
                return jsonify({'message': 'Game Watch Bot API', 'version': '1.0.0'})
    
    def is_recent_game(self, game_data):
        """Controlla se un gioco è recente (ultime 24 ore)"""
        # Implementa logica per determinare se il gioco è recente
        # Per ora ritorna sempre True
        return True
    
    def run_all_scraping(self):
        """Esegue lo scraping per tutte le piattaforme"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            for platform_key, scraper in self.scrapers.items():
                games = loop.run_until_complete(scraper.scrape())
                self.games_data[platform_key].extend(games)
            
            self.save_games_data()
        finally:
            loop.close()
    
    def run_platform_scraping(self, platform_key):
        """Esegue lo scraping per una piattaforma specifica"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            scraper = self.scrapers[platform_key]
            games = loop.run_until_complete(scraper.scrape())
            self.games_data[platform_key].extend(games)
            self.save_games_data()
        finally:
            loop.close()
    
    def load_games_data(self):
        """Carica i dati dei giochi"""
        try:
            data_file = Path("games_data.json")
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Errore nel caricamento dati: {e}")
        
        # Dati di default
        return {
            'prime_gaming': [],
            'xbox_gamepass': [],
            'ps_plus': []
        }
    
    def save_games_data(self):
        """Salva i dati dei giochi"""
        try:
            with open("games_data.json", 'w', encoding='utf-8') as f:
                json.dump(self.games_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Errore nel salvataggio dati: {e}")
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        """Avvia il server web"""
        self.app.run(host=host, port=port, debug=debug)