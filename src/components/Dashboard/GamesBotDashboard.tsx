import { StatsCard } from "./StatsCard";
import { PlatformCard } from "./PlatformCard";
import { BotConfigCard } from "./BotConfigCard";
import { DiscordEmbedPreview } from "./DiscordEmbedPreview";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Bot, 
  GamepadIcon, 
  TrendingUp, 
  Clock, 
  Activity,
  Settings,
  RefreshCw,
  Download
} from "lucide-react";
import { useState } from "react";
import heroImage from "@/assets/hero-gaming-bot.jpg";

export const GamesBotDashboard = () => {
  const [platforms, setPlatforms] = useState([
    {
      id: 'steam',
      name: 'Steam',
      logo: '🎮',
      status: 'active' as const,
      lastUpdate: '5 min fa',
      gamesFound: 142,
      enabled: true
    },
    {
      id: 'epic',
      name: 'Epic Games',
      logo: '🎯',
      status: 'active' as const,
      lastUpdate: '12 min fa',  
      gamesFound: 89,
      enabled: true
    },
    {
      id: 'playstation',
      name: 'PlayStation',
      logo: '🎮',
      status: 'inactive' as const,
      lastUpdate: '2 ore fa',
      gamesFound: 67,
      enabled: false
    },
    {
      id: 'xbox',
      name: 'Xbox',
      logo: '🎮',
      status: 'error' as const,
      lastUpdate: '1 giorno fa',
      gamesFound: 23,
      enabled: true
    }
  ]);

  const togglePlatform = (id: string, enabled: boolean) => {
    setPlatforms(prev => 
      prev.map(p => p.id === id ? { ...p, enabled } : p)
    );
  };

  const configurePlatform = (id: string) => {
    console.log(`Configuring platform: ${id}`);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div 
        className="relative h-64 bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: `url(${heroImage})` }}
      >
        <div className="absolute inset-0 bg-background/80 backdrop-blur-sm" />
        <div className="absolute inset-0 bg-gradient-hero" />
        <div className="relative h-full flex items-center justify-center">
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center space-x-3">
              <div className="p-4 rounded-full bg-primary/20 backdrop-blur-sm border border-primary/30">
                <Bot className="w-8 h-8 text-primary" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-foreground">Gaming Bot Dashboard</h1>
                <p className="text-lg text-muted-foreground">Monitora i nuovi giochi su tutte le piattaforme</p>
              </div>
            </div>
            <div className="flex items-center justify-center space-x-4">
              <Badge className="bg-success/20 text-success border-success/30">
                <Activity className="w-3 h-3 mr-1" />
                Sistema Attivo
              </Badge>
              <Badge className="bg-primary/20 text-primary border-primary/30">
                4 Piattaforme Monitorate
              </Badge>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8 space-y-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Giochi Totali"
            value="321"
            change="+12 oggi"
            changeType="positive"
            icon={GamepadIcon}
            description="Giochi monitorati"
          />
          <StatsCard
            title="Nuovi Oggi"
            value="7"
            change="+3 vs ieri"
            changeType="positive"
            icon={TrendingUp}
            description="Nuove release"
          />
          <StatsCard
            title="Ultimo Update"
            value="5m"
            icon={Clock}
            description="Ago"
          />
          <StatsCard
            title="Status Bot"
            value="Online"
            icon={Activity}
            description="Funzionante"
          />
        </div>

        {/* Bot Configuration */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <BotConfigCard />
          </div>
          <Card className="bg-gradient-card backdrop-blur-sm border-border/50">
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Azioni Rapide</h3>
              <div className="space-y-3">
                <Button className="w-full justify-start" variant="outline">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Aggiorna Tutte le Piattaforme
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Esporta Configurazione
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  <Settings className="w-4 h-4 mr-2" />
                  Impostazioni Avanzate
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* Platforms Management */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Piattaforme Monitorate</h2>
            <Button>
              <Settings className="w-4 h-4 mr-2" />
              Gestisci Piattaforme
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {platforms.map((platform) => (
              <PlatformCard
                key={platform.id}
                {...platform}
                onToggle={(enabled) => togglePlatform(platform.id, enabled)}
                onConfigure={() => configurePlatform(platform.id)}
              />
            ))}
          </div>
        </div>

        {/* Discord Embed Preview */}
        <div>
          <h2 className="text-2xl font-bold mb-6">Preview Embed Discord</h2>
          <DiscordEmbedPreview />
        </div>

        {/* Recent Activity */}
        <Card className="bg-gradient-card backdrop-blur-sm border-border/50">
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4">Attività Recente</h3>
            <div className="space-y-3">
              {[
                { time: '5 min fa', action: 'Nuovo gioco trovato su Steam', game: 'Cyberpunk 2077: Phantom Liberty', status: 'success' },
                { time: '12 min fa', action: 'Aggiornamento Epic Games completato', game: '89 giochi controllati', status: 'info' },
                { time: '1 ora fa', action: 'Errore connessione Xbox Live', game: 'Riprovo automaticamente', status: 'error' },
                { time: '2 ore fa', action: 'Embed inviato su Discord', game: 'Dead Space (2023)', status: 'success' }
              ].map((activity, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-secondary/30 border border-border/30">
                  <div className="flex items-center space-x-3">
                    <div className={`w-2 h-2 rounded-full ${
                      activity.status === 'success' ? 'bg-success' :
                      activity.status === 'error' ? 'bg-destructive' : 'bg-accent'
                    }`} />
                    <div>
                      <p className="text-sm font-medium">{activity.action}</p>
                      <p className="text-xs text-muted-foreground">{activity.game}</p>
                    </div>
                  </div>
                  <span className="text-xs text-muted-foreground">{activity.time}</span>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};