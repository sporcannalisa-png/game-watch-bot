# Gaming Bot Desktop App

Trasformazione della dashboard in applicazione desktop utilizzando Electron.

## 🚀 Avvio Rapido

### Modalità Sviluppo
```bash
# Installa le dipendenze
npm install

# Avvia l'app desktop in modalità sviluppo
node scripts/electron-dev.js
```

### Build Produzione
```bash
# Build completo per distribuzione
node scripts/electron-build.js
```

Gli eseguibili saranno generati nella cartella `dist-electron/`.

## 🔧 Configurazione

### Struttura Files
```
public/
  electron.js          # Main process Electron
  assets/             # Icone app e tray
scripts/
  electron-dev.js     # Script sviluppo
  electron-build.js   # Script build
src/
  hooks/
    useElectron.ts    # Hook per funzionalità Electron
  components/
    Desktop/
      DesktopHeader.tsx # Header specifico desktop
```

### Configurazione Build
Il file `electron-builder.json` configura:
- **Windows**: Installer NSIS + Portable
- **macOS**: DMG universale (Intel + Apple Silicon)
- **Linux**: AppImage + DEB

## 🎯 Funzionalità Desktop

### System Tray
- Icona nel system tray quando minimizzata
- Menu contestuale con azioni rapide
- Click per mostrare/nascondere finestra

### Notifiche Native
- Notifiche desktop per nuovi giochi trovati
- Avvisi di stato scraping
- Conferme operazioni

### Menu Applicazione
- **File**: Export/Import configurazioni
- **Bot**: Controlli scraping, test Discord
- **Visualizza**: Zoom, ricarica, dev tools

### Shortcuts Tastiera
- `Ctrl+S`: Avvia scraping
- `Ctrl+Shift+S`: Ferma scraping  
- `Ctrl+E`: Esporta config
- `Ctrl+I`: Importa config
- `Ctrl+R`: Ricarica app

### IPC Communication
Comunicazione tra processo principale e interfaccia:
```javascript
// Invia notifica desktop
await showNotification('Titolo', 'Messaggio');

// Minimizza nel tray
await minimizeToTray();

// Ascolta eventi menu
onScrapingStart(() => {
  // Avvia scraping
});
```

## 📱 Compatibilità

### Piattaforme Supportate
- **Windows 10+** (x64)
- **macOS 10.15+** (Intel + Apple Silicon)
- **Linux** (Ubuntu 18.04+, AppImage/DEB)

### Requisiti Sistema
- RAM: 512MB minimo
- Spazio: 200MB per installazione
- Connessione internet per scraping

## 🔒 Sicurezza

### Configurazione Sicura
- Context isolation abilitata in produzione
- Web security per link esterni
- IPC validation per messaggi

### Aggiornamenti Automatici
Struttura preparata per sistema auto-update:
```javascript
// Check updates
const update = await checkForUpdates();
if (update.updateAvailable) {
  // Handle update
}
```

## 🛠️ Sviluppo

### Debug
- Dev Tools disponibili in sviluppo
- Console logs del main process
- IPC message debugging

### Hot Reload
Il sistema supporta hot reload in sviluppo:
- Modifiche React → reload automatico
- Modifiche Electron → restart necessario

### Customizzazione Icone
Sostituire i files in `public/assets/`:
- `icon.png`: Icona principale (512x512)
- `tray-icon.png`: Icona tray (16x16, 32x32)
- Generare `.ico` per Windows, `.icns` per macOS

## 📊 Performance

### Ottimizzazioni
- Lazy loading componenti React
- Memory management per IPC
- Background process ottimizzato

### Monitoraggio
L'app include metriche per:
- Uso memoria
- Performance scraping
- Statistiche notifiche

## 🔧 Troubleshooting

### Problemi Comuni

**App non si avvia:**
```bash
# Verifica dipendenze
npm install
# Rebuild moduli nativi
npm run electron:rebuild
```

**Icone mancanti:**
- Aggiungere files icone in `public/assets/`
- Verificare percorsi in `electron-builder.json`

**Errori build:**
```bash
# Pulisci cache
rm -rf node_modules dist dist-electron
npm install
```

### Log Debug
```bash
# Avvia con debug
DEBUG=electron* node scripts/electron-dev.js
```

## 📦 Distribuzione

### Pubblicazione
1. Aggiorna versione in `package.json`
2. Esegui build completo
3. Test su piattaforme target
4. Pubblica release su GitHub

### Firma Digitale
Per distribuzione sicura:
- Windows: Certificato code signing
- macOS: Developer ID certificate
- Configurare in `electron-builder.json`

L'app desktop è pronta per essere utilizzata localmente con tutte le funzionalità native del sistema operativo!