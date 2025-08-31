import { useEffect, useState } from 'react';

// Type definitions for Electron IPC
declare global {
  interface Window {
    require?: any;
  }
}

export const useElectron = () => {
  const [isElectron, setIsElectron] = useState(false);
  const [ipc, setIpc] = useState<any>(null);

  useEffect(() => {
    // Check if running in Electron
    const userAgent = navigator.userAgent.toLowerCase();
    if (userAgent.indexOf(' electron/') > -1) {
      setIsElectron(true);
      
      // Get IPC renderer if available
      try {
        const { ipcRenderer } = window.require('electron');
        setIpc(ipcRenderer);
      } catch (error) {
        console.warn('Could not access Electron IPC:', error);
      }
    }
  }, []);

  // Utility functions for Electron features
  const showNotification = async (title: string, body: string) => {
    if (ipc) {
      await ipc.invoke('show-notification', title, body);
    } else {
      // Fallback to web notifications
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, { body });
      }
    }
  };

  const minimizeToTray = async () => {
    if (ipc) {
      await ipc.invoke('minimize-to-tray');
    }
  };

  const getAppVersion = async (): Promise<string> => {
    if (ipc) {
      return await ipc.invoke('get-app-version');
    }
    return '1.0.0';
  };

  const checkForUpdates = async () => {
    if (ipc) {
      return await ipc.invoke('check-for-updates');
    }
    return { updateAvailable: false };
  };

  // Listen to IPC messages from main process
  const onScrapingStart = (callback: () => void) => {
    if (ipc) {
      ipc.on('start-scraping', callback);
      return () => ipc.removeListener('start-scraping', callback);
    }
    return () => {};
  };

  const onScrapingStop = (callback: () => void) => {
    if (ipc) {
      ipc.on('stop-scraping', callback);
      return () => ipc.removeListener('stop-scraping', callback);
    }
    return () => {};
  };

  const onNavigateToSettings = (callback: () => void) => {
    if (ipc) {
      ipc.on('navigate-to-settings', callback);
      return () => ipc.removeListener('navigate-to-settings', callback);
    }
    return () => {};
  };

  const onExportConfig = (callback: () => void) => {
    if (ipc) {
      ipc.on('export-config', callback);
      return () => ipc.removeListener('export-config', callback);
    }
    return () => {};
  };

  const onImportConfig = (callback: () => void) => {
    if (ipc) {
      ipc.on('import-config', callback);
      return () => ipc.removeListener('import-config', callback);
    }
    return () => {};
  };

  const onTestDiscordConnection = (callback: () => void) => {
    if (ipc) {
      ipc.on('test-discord-connection', callback);
      return () => ipc.removeListener('test-discord-connection', callback);
    }
    return () => {};
  };

  return {
    isElectron,
    showNotification,
    minimizeToTray,
    getAppVersion,
    checkForUpdates,
    // Event listeners
    onScrapingStart,
    onScrapingStop,
    onNavigateToSettings,
    onExportConfig,
    onImportConfig,
    onTestDiscordConnection
  };
};