# 🚀 Setup Gaming Bot Desktop App

## Passo 1: Aggiungere Script al package.json

Aggiungi questi script alla sezione `"scripts"` del tuo `package.json`:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build", 
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview",
    "electron:dev": "node scripts/electron-dev.js",
    "electron:build": "node scripts/electron-build.js",
    "electron:pack": "npm run build && npx electron-builder --config electron-builder.json"
  }
}
```

## Passo 2: Avvio App Desktop

### Modalità Sviluppo
```bash
npm run electron:dev
```

### Build Produzione
```bash
npm run electron:build
```

## ✨ Funzionalità Desktop Implementate

### 🖥️ Header Desktop
- Controlli scraping integrati nella barra superiore
- Indicatore stato connessione Discord
- Pulsanti rapidi per export/import configurazioni
- Minimizzazione nel system tray

### 🔔 Notifiche Native
- Notifiche desktop per eventi importanti
- Avvisi di stato scraping
- Conferme operazioni completate

### ⌨️ Shortcuts Tastiera
- `Ctrl/Cmd + S`: Avvia scraping
- `Ctrl/Cmd + Shift + S`: Ferma scraping
- `Ctrl/Cmd + E`: Esporta configurazione
- `Ctrl/Cmd + I`: Importa configurazione
- `Ctrl/Cmd + R`: Ricarica app

### 🖱️ System Tray
- Icona nel tray quando minimizzata
- Menu contestuale con azioni rapide
- Click per mostrare/nascondere finestra

### 📋 Menu Applicazione
- **File**: Export/Import configurazioni, Esci
- **Bot**: Controlli scraping, test Discord
- **Visualizza**: Zoom, ricarica, developer tools

## 🛠️ Build Distributivi

L'app supporta build per:
- **Windows**: .exe installer + portable
- **macOS**: .dmg per Intel e Apple Silicon  
- **Linux**: AppImage + .deb

## 🎯 Funzionalità Uniche Desktop

1. **Auto-Start**: Avvio automatico con sistema (configurabile)
2. **Background Mode**: Esecuzione in background senza finestra
3. **Desktop Notifications**: Sistema nativo per alerts
4. **File System Access**: Export/import configurazioni locali
5. **System Integration**: Integrazione completa con OS

## 📱 Compatibilità

- **Windows 10+** (x64)
- **macOS 10.15+** (Intel + Apple Silicon)  
- **Linux** (Ubuntu 18.04+, AppImage/DEB)

La dashboard ora è completamente trasformata in app desktop nativa! 🎮