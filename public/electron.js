const { app, BrowserWindow, Menu, Tray, shell, ipcMain, Notification } = require('electron');
const path = require('path');
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;
let tray = null;

// Enable live reload for Electron in development
if (isDev) {
  require('electron-reload')(__dirname, {
    electron: path.join(__dirname, '../node_modules', '.bin', 'electron'),
    hardResetMethod: 'exit'
  });
}

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
      webSecurity: false
    },
    icon: path.join(__dirname, 'assets/icon.png'), // Add your app icon
    titleBarStyle: 'default',
    show: false // Don't show until ready
  });

  // Load the app
  const startUrl = isDev 
    ? 'http://localhost:8080' 
    : `file://${path.join(__dirname, '../dist/index.html')}`;
  
  mainWindow.loadURL(startUrl);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Focus on window creation
    if (isDev) {
      mainWindow.webContents.openDevTools();
    }
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle minimize to tray
  mainWindow.on('minimize', (event) => {
    event.preventDefault();
    mainWindow.hide();
    
    if (!tray) {
      createTray();
    }
  });

  // Handle close button (minimize to tray instead of quit)
  mainWindow.on('close', (event) => {
    if (!app.isQuiting) {
      event.preventDefault();
      mainWindow.hide();
      
      if (!tray) {
        createTray();
      }
      
      return false;
    }
  });

  // Open external links in default browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

function createTray() {
  // Create tray icon (you'll need to add an icon file)
  const iconPath = path.join(__dirname, 'assets/tray-icon.png');
  tray = new Tray(iconPath);
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Mostra Gaming Bot',
      click: () => {
        mainWindow.show();
        mainWindow.focus();
      }
    },
    {
      label: 'Avvia Scraping',
      click: () => {
        // Send IPC message to start scraping
        mainWindow.webContents.send('start-scraping');
        showNotification('Scraping Avviato', 'Il bot ha iniziato la ricerca di nuovi giochi');
      }
    },
    {
      label: 'Stop Scraping',
      click: () => {
        // Send IPC message to stop scraping
        mainWindow.webContents.send('stop-scraping');
        showNotification('Scraping Fermato', 'Il bot ha interrotto la ricerca');
      }
    },
    { type: 'separator' },
    {
      label: 'Impostazioni',
      click: () => {
        mainWindow.show();
        mainWindow.focus();
        // Navigate to settings
        mainWindow.webContents.send('navigate-to-settings');
      }
    },
    { type: 'separator' },
    {
      label: 'Esci',
      click: () => {
        app.isQuiting = true;
        app.quit();
      }
    }
  ]);

  tray.setContextMenu(contextMenu);
  tray.setToolTip('Gaming Bot Dashboard');
  
  // Show window on tray click
  tray.on('click', () => {
    if (mainWindow.isVisible()) {
      mainWindow.focus();
    } else {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

function showNotification(title, body) {
  if (Notification.isSupported()) {
    new Notification({
      title: title,
      body: body,
      icon: path.join(__dirname, 'assets/icon.png')
    }).show();
  }
}

// This method will be called when Electron has finished initialization
app.whenReady().then(() => {
  createWindow();
  
  // Create application menu
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Esporta Configurazione',
          accelerator: 'CmdOrCtrl+E',
          click: () => {
            mainWindow.webContents.send('export-config');
          }
        },
        {
          label: 'Importa Configurazione',
          accelerator: 'CmdOrCtrl+I',
          click: () => {
            mainWindow.webContents.send('import-config');
          }
        },
        { type: 'separator' },
        {
          label: 'Esci',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.isQuiting = true;
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Bot',
      submenu: [
        {
          label: 'Avvia Scraping',
          accelerator: 'CmdOrCtrl+S',
          click: () => {
            mainWindow.webContents.send('start-scraping');
            showNotification('Scraping Avviato', 'Il bot ha iniziato la ricerca di nuovi giochi');
          }
        },
        {
          label: 'Stop Scraping',
          accelerator: 'CmdOrCtrl+Shift+S',
          click: () => {
            mainWindow.webContents.send('stop-scraping');
          }
        },
        { type: 'separator' },
        {
          label: 'Test Connessione Discord',
          click: () => {
            mainWindow.webContents.send('test-discord-connection');
          }
        }
      ]
    },
    {
      label: 'Visualizza',
      submenu: [
        {
          label: 'Ricarica',
          accelerator: 'CmdOrCtrl+R',
          click: () => {
            mainWindow.reload();
          }
        },
        {
          label: 'Toggle Developer Tools',
          accelerator: process.platform === 'darwin' ? 'Alt+Cmd+I' : 'Ctrl+Shift+I',
          click: () => {
            mainWindow.webContents.toggleDevTools();
          }
        },
        { type: 'separator' },
        {
          label: 'Zoom Avanti',
          accelerator: 'CmdOrCtrl+Plus',
          click: () => {
            const currentZoom = mainWindow.webContents.getZoomFactor();
            mainWindow.webContents.setZoomFactor(currentZoom + 0.1);
          }
        },
        {
          label: 'Zoom Indietro',
          accelerator: 'CmdOrCtrl+-',
          click: () => {
            const currentZoom = mainWindow.webContents.getZoomFactor();
            mainWindow.webContents.setZoomFactor(Math.max(0.5, currentZoom - 0.1));
          }
        },
        {
          label: 'Reset Zoom',
          accelerator: 'CmdOrCtrl+0',
          click: () => {
            mainWindow.webContents.setZoomFactor(1);
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
});

// Quit when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// IPC handlers for communication with renderer process
ipcMain.handle('show-notification', (event, title, body) => {
  showNotification(title, body);
});

ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('minimize-to-tray', () => {
  mainWindow.hide();
  if (!tray) {
    createTray();
  }
});

// Handle app updates (for future implementation)
ipcMain.handle('check-for-updates', () => {
  // Implement auto-updater logic here
  return { updateAvailable: false };
});

// Security: Prevent new window creation
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
    shell.openExternal(navigationUrl);
  });
});