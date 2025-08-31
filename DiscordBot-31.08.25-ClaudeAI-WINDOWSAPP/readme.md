# ==========================================
# README.md - Documentazione completa
# ==========================================

README_CONTENT = '''
# 🎮 Game Watch Bot - Desktop & Web Application

Applicazione completa per monitorare giochi gratuiti su Prime Gaming, Xbox Game Pass e PlayStation Plus con interfaccia desktop e web.

## ✨ Caratteristiche

### 🖥️ Applicazione Desktop (PyQt6)
- Interface grafica moderna e intuitiva  
- Scraping automatico e manuale
- System tray integration
- Salvataggio dati persistente
- Progress tracking in tempo reale
- Visualizzazione dettagli giochi con card

### 🌐 Interfaccia Web (React Integration)
- API REST complete
- Interfaccia reattiva
- Compatibile con il frontend React del repository originale
- Cross-platform web access

### 🤖 Bot Discord (Opzionale) 
- Notifiche automatiche sui canali Discord
- Embed personalizzati per ogni piattaforma
- Comandi di controllo

## 🚀 Installazione Rapida

### 1. Setup Automatico
```bash
python setup_desktop.py
```

### 2. Installazione Manuale
```bash
# Clona/scarica i file
git clone <repository>
cd game-watch-bot

# Installa dipendenze  
pip install PyQt6 aiohttp beautifulsoup4 lxml selenium requests flask flask-cors

# Installa ChromeDriver per Prime Gaming
# Ubuntu/Debian:
sudo apt install chromium-chromedriver
# Windows: scarica da https://chromedriver.chromium.org/
```

### 3. Configurazione
```python
# Modifica config.py
CONFIG = BotConfig(
    token="TUO_DISCORD_TOKEN",  # Opzionale per Discord
    guild_id=123456789,
    channels={
        "prime_gaming": 123456789,
        "xbox_gamepass": 123456789,
        "ps_plus": 123456789
    }
)

# Configura Xbox API Key in scrapers/xbox_scraper.py
self.XBL_API_KEY = "TUA_XBL_API_KEY"  # Da https://xbl.io/
```

## 🎯 Utilizzo

### Modalità Desktop
```bash
python hybrid_launcher.py --mode desktop
```

### Modalità Web Server
```bash  
python hybrid_launcher.py --mode web --port 5000
```

### Modalità Discord Bot
```bash
python hybrid_launcher.py --mode discord
```

### Launcher Semplificato
```bash
# Desktop
python run_desktop_app.py

# Web
python run_web_server.py
```

## 🔧 Creazione Eseguibile Windows

### Con PyInstaller
```bash
pip install pyinstaller
python build_executable.py
```

### Installer Professionale  
```bash
# 1. Crea eseguibile con PyInstaller
python build_executable.py

# 2. Installa Inno Setup
# 3. Compila installer.iss
```

## 📁 Struttura File

```
game-watch-bot/
├── main_app.py              # App desktop principale
├── hybrid_launcher.py       # Launcher multi-modalità  
├── web_interface.py         # Server web + API REST
├── config.py               # Configurazione
├── cache_manager.py        # Gestione cache
├── scrapers/               # Moduli scraping
│   ├── base_scraper.py    
│   ├── prime_gaming_scraper.py  # Selenium
│   ├── xbox_scraper.py          # API Microsoft  
│   └── ps_plus_scraper.py       # Web scraping
├── discord_bot.py          # Bot Discord opzionale
├── setup_desktop.py        # Setup automatico
├── build_executable.py     # Builder eseguibile
└── installer.iss          # Script Inno Setup
```

## 🌐 API REST Endpoints

```
GET  /api/games            # Lista giochi
GET  /api/games?platform=xbox  # Giochi per piattaforma  
GET  /api/platforms        # Lista piattaforme
GET  /api/stats           # Statistiche
POST /api/scrape          # Avvia scraping
POST /api/clear           # Pulisci dati
```

## 💡 Integrazione React Frontend

L'app espone API REST compatibili con il frontend React del repository originale:

```javascript
// Esempio integrazione React
const response = await fetch('http://localhost:5000/api/games');
const games = await response.json();
```

## 🔑 API Keys Necessarie

### Xbox Game Pass
1. Vai su https://xbl.io/
2. Registrati e ottieni API key
3. Configura in `scrapers/xbox_scraper.py`

### Discord Bot (Opzionale)
1. Vai su https://discord.com/developers/applications
2. Crea nuova applicazione
3. Copia token in `config.py`

## 🐛 Troubleshooting

### ChromeDriver Issues
```bash
# Verifica installazione
which chromedriver
google-chrome --version

# Ubuntu fix
sudo apt update && sudo apt install chromium-chromedriver
```

### PyQt6 Installation
```bash
# Se problemi con PyQt6
pip install --upgrade pip
pip install PyQt6 --no-cache-dir
```

### Selenium Issues  
```bash
# Headless Chrome issues
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
```

## 📊 Funzionalità Avanzate

### Desktop App
- ✅ Multi-threading per scraping parallelo
- ✅ System tray con notifiche
- ✅ Auto-save configurazione
- ✅ Progress tracking real-time
- ✅ Card layout responsive per giochi
- ✅ Log integrato per debugging

### Web Interface
- ✅ API REST complete per integrazioni
- ✅ CORS abilitato per frontend esterni
- ✅ Compatibilità React/Vue/Angular
- ✅ WebSocket support (future)

### Scrapers
- ✅ **Prime Gaming**: Selenium + selettori testati
- ✅ **Xbox Game Pass**: API Microsoft ufficiali
- ✅ **PlayStation Plus**: Web scraping tradizionale
- ✅ Cache intelligente anti-duplicati
- ✅ Rate limiting e retry logic

## 🤝 Contribuire

1. Fork del repository
2. Crea feature branch
3. Commit modifiche  
4. Push e crea Pull Request

## 📄 Licenza

MIT License - vedi LICENSE file

## 🆘 Supporto

- Issues: [GitHub Issues](https://github.com/sporcannalisa-png/game-watch-bot/issues)
- Discussions: [GitHub Discussions](https://github.com/sporcannalisa-png/game-watch-bot/discussions)
'''

def create_readme():
    """Crea il file README.md"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(README_CONTENT)
    
    print("📖 Creato README.md completo")