# ==========================================
# main_app.py - Applicazione Desktop Principale
# ==========================================

import sys
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import webbrowser

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QPushButton, QLabel, QTextEdit, QTabWidget,
    QGroupBox, QScrollArea, QFrame, QProgressBar, QCheckBox,
    QSpinBox, QLineEdit, QComboBox, QMessageBox, QSystemTrayIcon,
    QMenu, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt, QUrl
from PyQt6.QtGui import QIcon, QPixmap, QFont, QAction
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

# Importa i nostri moduli del bot
from config import CONFIG
from cache_manager import CacheManager
from scrapers.prime_gaming_scraper import PrimeGamingScraper
from scrapers.xbox_scraper import XboxGamePassScraper
from scrapers.ps_plus_scraper import PSPlusScraper

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScrapingThread(QThread):
    """Thread per eseguire lo scraping in background"""
    progress_updated = pyqtSignal(str, int)  # platform, progress
    game_found = pyqtSignal(dict)  # game_data
    scraping_finished = pyqtSignal(str, int)  # platform, count
    error_occurred = pyqtSignal(str, str)  # platform, error

    def __init__(self, platform: str, scraper, parent=None):
        super().__init__(parent)
        self.platform = platform
        self.scraper = scraper
        self._stop_requested = False

    def run(self):
        """Esegue lo scraping in un thread separato"""
        try:
            self.progress_updated.emit(self.platform, 0)
            
            # Crea un nuovo event loop per questo thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                self.progress_updated.emit(self.platform, 50)
                games = loop.run_until_complete(self.scraper.scrape())
                
                self.progress_updated.emit(self.platform, 100)
                
                # Emette segnale per ogni gioco trovato
                for game in games:
                    if not self._stop_requested:
                        self.game_found.emit(game)
                
                self.scraping_finished.emit(self.platform, len(games))
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Errore nello scraping di {self.platform}: {e}")
            self.error_occurred.emit(self.platform, str(e))

    def stop(self):
        """Ferma il thread di scraping"""
        self._stop_requested = True

class GameCard(QFrame):
    """Widget per mostrare un singolo gioco"""
    
    def __init__(self, game_data: Dict, parent=None):
        super().__init__(parent)
        self.game_data = game_data
        self.setup_ui()
        
    def setup_ui(self):
        """Configura l'interfaccia della card del gioco"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                border: 2px solid #ddd;
                border-radius: 10px;
                background-color: #f9f9f9;
                margin: 5px;
                padding: 10px;
            }
            QLabel {
                color: #333;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Titolo del gioco
        title = QLabel(self.game_data.get('title', 'Gioco sconosciuto'))
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setWordWrap(True)
        layout.addWidget(title)
        
        # Piattaforma
        platform = QLabel(f"📱 {self.game_data.get('platform', 'N/D')}")
        platform.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(platform)
        
        # Descrizione (se presente)
        if self.game_data.get('descrizione'):
            desc = self.game_data['descrizione'][:100] + "..." if len(self.game_data['descrizione']) > 100 else self.game_data['descrizione']
            description = QLabel(desc)
            description.setWordWrap(True)
            description.setStyleSheet("font-size: 9px; color: #555;")
            layout.addWidget(description)
        
        # Informazioni specifiche per piattaforma
        self._add_platform_specific_info(layout)
        
        # Pulsante per aprire il link
        if self.game_data.get('url'):
            btn_open = QPushButton("🔗 Apri Link")
            btn_open.clicked.connect(self.open_game_link)
            btn_open.setStyleSheet("""
                QPushButton {
                    background-color: #007ACC;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #005a9e;
                }
            """)
            layout.addWidget(btn_open)
        
        self.setFixedSize(280, 200)
    
    def _add_platform_specific_info(self, layout):
        """Aggiunge informazioni specifiche per piattaforma"""
        platform = self.game_data.get('platform', '')
        
        if platform == "Prime Gaming":
            if self.game_data.get('launcher') and self.game_data['launcher'] != "N/D":
                layout.addWidget(QLabel(f"🎮 Launcher: {self.game_data['launcher']}"))
            if self.game_data.get('scadenza') and self.game_data['scadenza'] != "N/D":
                layout.addWidget(QLabel(f"⏰ Scadenza: {self.game_data['scadenza']}"))
                
        elif platform == "Xbox Game Pass":
            if self.game_data.get('publisher') and self.game_data['publisher'] != "N/D":
                layout.addWidget(QLabel(f"🏢 Publisher: {self.game_data['publisher']}"))
            if self.game_data.get('genere') and self.game_data['genere'] != "N/D":
                layout.addWidget(QLabel(f"🎯 Genere: {self.game_data['genere']}"))
    
    def open_game_link(self):
        """Apre il link del gioco nel browser"""
        if self.game_data.get('url'):
            webbrowser.open(self.game_data['url'])

class GameWatchMainWindow(QMainWindow):
    """Finestra principale dell'applicazione"""
    
    def __init__(self):
        super().__init__()
        self.cache_manager = CacheManager(CONFIG.cache_file)
        self.scrapers = {
            'prime_gaming': PrimeGamingScraper(self.cache_manager),
            'xbox_gamepass': XboxGamePassScraper(self.cache_manager),
            'ps_plus': PSPlusScraper(self.cache_manager)
        }
        self.scraping_threads = {}
        self.games_data = {
            'prime_gaming': [],
            'xbox_gamepass': [],
            'ps_plus': []
        }
        
        self.setup_ui()
        self.setup_system_tray()
        self.load_saved_games()
        
        # Timer per scraping automatico
        self.auto_scraping_timer = QTimer()
        self.auto_scraping_timer.timeout.connect(self.run_auto_scraping)
        
    def setup_ui(self):
        """Configura l'interfaccia utente principale"""
        self.setWindowTitle("Game Watch Bot - Desktop App")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon("icon.png"))  # Aggiungi un'icona se disponibile
        
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principale
        main_layout = QHBoxLayout(central_widget)
        
        # Pannello di controllo laterale
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, 0)
        
        # Area principale con tab per ogni piattaforma
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget, 1)
        
        # Crea tab per ogni piattaforma
        self.platform_tabs = {}
        for platform_key, scraper in self.scrapers.items():
            tab = self.create_platform_tab(platform_key, scraper.platform_name)
            self.platform_tabs[platform_key] = tab
            self.tab_widget.addTab(tab, scraper.platform_name)
    
    def create_control_panel(self) -> QWidget:
        """Crea il pannello di controllo laterale"""
        panel = QWidget()
        panel.setFixedWidth(300)
        panel.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-right: 2px solid #ccc;
            }
        """)
        
        layout = QVBoxLayout(panel)
        
        # Titolo
        title = QLabel("🎮 Game Watch Control")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Gruppo controlli scraping
        scraping_group = QGroupBox("Controlli Scraping")
        scraping_layout = QVBoxLayout(scraping_group)
        
        # Pulsanti per scraping manuale
        self.btn_scrape_all = QPushButton("🔄 Avvia Scraping Completo")
        self.btn_scrape_all.clicked.connect(self.start_full_scraping)
        scraping_layout.addWidget(self.btn_scrape_all)
        
        self.btn_scrape_prime = QPushButton("🎯 Scraping Prime Gaming")
        self.btn_scrape_prime.clicked.connect(lambda: self.start_platform_scraping('prime_gaming'))
        scraping_layout.addWidget(self.btn_scrape_prime)
        
        self.btn_scrape_xbox = QPushButton("🎮 Scraping Xbox Game Pass")
        self.btn_scrape_xbox.clicked.connect(lambda: self.start_platform_scraping('xbox_gamepass'))
        scraping_layout.addWidget(self.btn_scrape_xbox)
        
        self.btn_scrape_ps = QPushButton("🎮 Scraping PS Plus")
        self.btn_scrape_ps.clicked.connect(lambda: self.start_platform_scraping('ps_plus'))
        scraping_layout.addWidget(self.btn_scrape_ps)
        
        # Progress bars per ogni piattaforma
        self.progress_bars = {}
        for platform_key, scraper in self.scrapers.items():
            label = QLabel(f"{scraper.platform_name}:")
            progress = QProgressBar()
            progress.setRange(0, 100)
            progress.setValue(0)
            self.progress_bars[platform_key] = progress
            scraping_layout.addWidget(label)
            scraping_layout.addWidget(progress)
        
        layout.addWidget(scraping_group)
        
        # Gruppo configurazione
        config_group = QGroupBox("Configurazione")
        config_layout = QVBoxLayout(config_group)
        
        # Checkbox per scraping automatico
        self.cb_auto_scraping = QCheckBox("Scraping Automatico")
        self.cb_auto_scraping.toggled.connect(self.toggle_auto_scraping)
        config_layout.addWidget(self.cb_auto_scraping)
        
        # Intervallo scraping
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Intervallo (minuti):"))
        self.spin_interval = QSpinBox()
        self.spin_interval.setRange(5, 1440)  # 5 minuti - 24 ore
        self.spin_interval.setValue(60)
        interval_layout.addWidget(self.spin_interval)
        config_layout.addLayout(interval_layout)
        
        layout.addWidget(config_group)
        
        # Gruppo statistiche
        stats_group = QGroupBox("Statistiche")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_labels = {}
        for platform_key, scraper in self.scrapers.items():
            label = QLabel(f"{scraper.platform_name}: 0 giochi")
            self.stats_labels[platform_key] = label
            stats_layout.addWidget(label)
        
        layout.addWidget(stats_group)
        
        # Log area
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        layout.addStretch()
        
        return panel
    
    def create_platform_tab(self, platform_key: str, platform_name: str) -> QWidget:
        """Crea un tab per una piattaforma specifica"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Intestazione con info piattaforma
        header = QLabel(f"🎮 {platform_name}")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header)
        
        # Area scrollabile per le card dei giochi
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.games_layouts = getattr(self, 'games_layouts', {})
        self.games_layouts[platform_key] = QVBoxLayout(scroll_widget)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        return tab
    
    def setup_system_tray(self):
        """Configura il system tray"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon("icon.png"))
            
            tray_menu = QMenu()
            
            show_action = QAction("Mostra", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)
            
            quit_action = QAction("Esci", self)
            quit_action.triggered.connect(QApplication.quit)
            tray_menu.addAction(quit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
    
    def start_full_scraping(self):
        """Avvia lo scraping completo di tutte le piattaforme"""
        self.log_message("🔄 Avvio scraping completo...")
        for platform_key in self.scrapers.keys():
            self.start_platform_scraping(platform_key)
    
    def start_platform_scraping(self, platform_key: str):
        """Avvia lo scraping per una piattaforma specifica"""
        if platform_key in self.scraping_threads and self.scraping_threads[platform_key].isRunning():
            self.log_message(f"⚠️ Scraping di {platform_key} già in corso...")
            return
        
        scraper = self.scrapers[platform_key]
        thread = ScrapingThread(platform_key, scraper, self)
        
        # Connetti i segnali
        thread.progress_updated.connect(self.update_progress)
        thread.game_found.connect(self.add_game_to_ui)
        thread.scraping_finished.connect(self.on_scraping_finished)
        thread.error_occurred.connect(self.on_scraping_error)
        
        self.scraping_threads[platform_key] = thread
        thread.start()
        
        self.log_message(f"🚀 Avvio scraping per {scraper.platform_name}...")
    
    def update_progress(self, platform: str, progress: int):
        """Aggiorna la progress bar"""
        if platform in self.progress_bars:
            self.progress_bars[platform].setValue(progress)
    
    def add_game_to_ui(self, game_data: Dict):
        """Aggiunge un gioco all'interfaccia"""
        platform_key = game_data.get('platform_key', game_data.get('platform', '').lower().replace(' ', '_'))
        
        # Aggiungi ai dati
        if platform_key in self.games_data:
            self.games_data[platform_key].append(game_data)
        
        # Crea la card del gioco
        if platform_key in self.games_layouts:
            game_card = GameCard(game_data)
            self.games_layouts[platform_key].addWidget(game_card)
        
        # Aggiorna statistiche
        self.update_statistics()
        
        self.log_message(f"🎮 Nuovo gioco trovato: {game_data.get('title', 'N/D')} ({game_data.get('platform', 'N/D')})")
    
    def on_scraping_finished(self, platform: str, count: int):
        """Chiamato quando lo scraping è completato"""
        self.log_message(f"✅ Scraping {platform} completato: {count} giochi trovati")
        
        # Salva i dati
        self.save_games_data()
    
    def on_scraping_error(self, platform: str, error: str):
        """Chiamato quando si verifica un errore nello scraping"""
        self.log_message(f"❌ Errore scraping {platform}: {error}")
    
    def toggle_auto_scraping(self, enabled: bool):
        """Attiva/disattiva lo scraping automatico"""
        if enabled:
            interval_ms = self.spin_interval.value() * 60 * 1000  # Converti in millisecondi
            self.auto_scraping_timer.start(interval_ms)
            self.log_message(f"⏰ Scraping automatico attivato (ogni {self.spin_interval.value()} minuti)")
        else:
            self.auto_scraping_timer.stop()
            self.log_message("⏰ Scraping automatico disattivato")
    
    def run_auto_scraping(self):
        """Esegue lo scraping automatico"""
        self.log_message("⏰ Esecuzione scraping automatico...")
        self.start_full_scraping()
    
    def update_statistics(self):
        """Aggiorna le statistiche nell'interfaccia"""
        for platform_key, games in self.games_data.items():
            if platform_key in self.stats_labels:
                scraper = self.scrapers.get(platform_key)
                platform_name = scraper.platform_name if scraper else platform_key
                count = len(games)
                self.stats_labels[platform_key].setText(f"{platform_name}: {count} giochi")
    
    def log_message(self, message: str):
        """Aggiunge un messaggio al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)
        logger.info(message)
    
    def save_games_data(self):
        """Salva i dati dei giochi su file"""
        try:
            data_file = Path("games_data.json")
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(self.games_data, f, ensure_ascii=False, indent=2)
            self.log_message("💾 Dati salvati correttamente")
        except Exception as e:
            self.log_message(f"❌ Errore nel salvataggio: {e}")
    
    def load_saved_games(self):
        """Carica i dati salvati dei giochi"""
        try:
            data_file = Path("games_data.json")
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                
                for platform_key, games in saved_data.items():
                    if platform_key in self.games_data:
                        for game_data in games:
                            self.add_game_to_ui(game_data)
                
                self.log_message(f"📁 Caricati dati salvati: {sum(len(games) for games in saved_data.values())} giochi totali")
        except Exception as e:
            self.log_message(f"❌ Errore nel caricamento: {e}")
    
    def closeEvent(self, event):
        """Gestisce la chiusura dell'applicazione"""
        # Salva i dati prima di chiudere
        self.save_games_data()
        
        # Ferma tutti i thread di scraping
        for thread in self.scraping_threads.values():
            if thread.isRunning():
                thread.stop()
                thread.wait(3000)  # Aspetta max 3 secondi
        
        # Chiudi i scrapers
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            for scraper in self.scrapers.values():
                loop.run_until_complete(scraper.close())
        finally:
            loop.close()
        
        event.accept()