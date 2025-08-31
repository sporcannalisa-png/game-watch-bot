import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useElectron } from "@/hooks/useElectron";
import { 
  Minimize2, 
  Settings, 
  Download,
  Upload,
  Wifi,
  WifiOff,
  Play,
  Square
} from "lucide-react";

interface DesktopHeaderProps {
  onStartScraping?: () => void;
  onStopScraping?: () => void;
  isScrapingActive?: boolean;
}

export const DesktopHeader = ({ 
  onStartScraping, 
  onStopScraping, 
  isScrapingActive = false 
}: DesktopHeaderProps) => {
  const { 
    isElectron, 
    minimizeToTray, 
    getAppVersion,
    onExportConfig,
    onImportConfig,
    onTestDiscordConnection,
    showNotification
  } = useElectron();
  
  const [version, setVersion] = useState<string>('1.0.0');
  const [discordConnected, setDiscordConnected] = useState(false);

  useEffect(() => {
    if (isElectron) {
      getAppVersion().then(setVersion);
      
      // Listen to Electron menu events
      const unsubscribeExport = onExportConfig(() => {
        handleExportConfig();
      });
      
      const unsubscribeImport = onImportConfig(() => {
        handleImportConfig();
      });

      const unsubscribeTestDiscord = onTestDiscordConnection(() => {
        handleTestDiscordConnection();
      });

      return () => {
        unsubscribeExport();
        unsubscribeImport();
        unsubscribeTestDiscord();
      };
    }
  }, [isElectron]);

  const handleMinimizeToTray = async () => {
    await minimizeToTray();
    await showNotification(
      'Gaming Bot', 
      'App minimizzata nel system tray. Click sull\'icona per riaprire.'
    );
  };

  const handleExportConfig = () => {
    // Implement config export logic
    console.log('Exporting configuration...');
    showNotification('Configurazione', 'Configurazione esportata con successo');
  };

  const handleImportConfig = () => {
    // Implement config import logic
    console.log('Importing configuration...');
    showNotification('Configurazione', 'Configurazione importata con successo');
  };

  const handleTestDiscordConnection = async () => {
    // Simulate Discord connection test
    const connected = Math.random() > 0.5; // Random for demo
    setDiscordConnected(connected);
    
    await showNotification(
      'Test Connessione Discord',
      connected ? 'Connessione riuscita!' : 'Errore di connessione'
    );
  };

  const handleScrapingToggle = async () => {
    if (isScrapingActive) {
      onStopScraping?.();
      await showNotification('Scraping', 'Scraping interrotto');
    } else {
      onStartScraping?.();
      await showNotification('Scraping', 'Scraping avviato');
    }
  };

  // Show desktop header only in Electron
  if (!isElectron) {
    return null;
  }

  return (
    <header className="border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
      <div className="container flex h-14 items-center justify-between px-4">
        <div className="flex items-center space-x-4">
          <h1 className="text-lg font-semibold bg-gradient-to-r from-primary to-gaming-accent bg-clip-text text-transparent">
            Gaming Bot Dashboard
          </h1>
          <Badge variant="secondary" className="text-xs">
            v{version}
          </Badge>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Discord Status */}
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-md bg-background/50">
            {discordConnected ? (
              <Wifi className="h-4 w-4 text-green-500" />
            ) : (
              <WifiOff className="h-4 w-4 text-destructive" />
            )}
            <span className="text-xs text-muted-foreground">
              {discordConnected ? 'Connesso' : 'Disconnesso'}
            </span>
          </div>

          {/* Scraping Controls */}
          <Button
            variant={isScrapingActive ? "destructive" : "default"}
            size="sm"
            onClick={handleScrapingToggle}
            className="flex items-center space-x-2"
          >
            {isScrapingActive ? (
              <>
                <Square className="h-4 w-4" />
                <span>Stop</span>
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                <span>Start</span>
              </>
            )}
          </Button>

          {/* Quick Actions */}
          <Button
            variant="ghost"
            size="sm"
            onClick={handleExportConfig}
            title="Esporta Configurazione"
          >
            <Download className="h-4 w-4" />
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleImportConfig}
            title="Importa Configurazione"
          >
            <Upload className="h-4 w-4" />
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleTestDiscordConnection}
            title="Test Connessione Discord"
          >
            <Settings className="h-4 w-4" />
          </Button>

          {/* Minimize to Tray */}
          <Button
            variant="ghost"
            size="sm"
            onClick={handleMinimizeToTray}
            title="Minimizza nel System Tray"
          >
            <Minimize2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  );
};