import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Bot, Key, Server, Hash, AlertCircle, CheckCircle } from "lucide-react";
import { useState } from "react";

export const BotConfigCard = () => {
  const [botStatus, setBotStatus] = useState<'online' | 'offline' | 'error'>('offline');
  const [config, setConfig] = useState({
    token: '',
    serverId: '',
    channelId: ''
  });

  const handleConnect = () => {
    // Simula connessione bot
    if (config.token && config.serverId && config.channelId) {
      setBotStatus('online');
    } else {
      setBotStatus('error');
    }
  };

  const getStatusBadge = () => {
    switch (botStatus) {
      case 'online':
        return (
          <Badge className="bg-success/20 text-success border-success/30">
            <CheckCircle className="w-3 h-3 mr-1" />
            Online
          </Badge>
        );
      case 'error':
        return (
          <Badge className="bg-destructive/20 text-destructive border-destructive/30">
            <AlertCircle className="w-3 h-3 mr-1" />
            Errore
          </Badge>
        );
      default:
        return (
          <Badge className="bg-muted/20 text-muted-foreground border-muted/30">
            <AlertCircle className="w-3 h-3 mr-1" />
            Offline
          </Badge>
        );
    }
  };

  return (
    <Card className="relative overflow-hidden bg-gradient-card backdrop-blur-sm border-border/50">
      <div className="absolute inset-0 bg-gradient-hero opacity-30" />
      <div className="relative p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-3 rounded-full bg-primary/10 border border-primary/20">
              <Bot className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Configurazione Bot</h3>
              <p className="text-sm text-muted-foreground">Connetti il tuo bot Discord</p>
            </div>
          </div>
          {getStatusBadge()}
        </div>

        <div className="space-y-4">
          <div>
            <Label htmlFor="token" className="flex items-center space-x-2">
              <Key className="w-4 h-4" />
              <span>Bot Token</span>
            </Label>
            <Input
              id="token"
              type="password"
              placeholder="Il tuo Discord Bot Token"
              value={config.token}
              onChange={(e) => setConfig(prev => ({ ...prev, token: e.target.value }))}
              className="mt-1"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="serverId" className="flex items-center space-x-2">
                <Server className="w-4 h-4" />
                <span>Server ID</span>
              </Label>
              <Input
                id="serverId"
                placeholder="ID del server Discord"
                value={config.serverId}
                onChange={(e) => setConfig(prev => ({ ...prev, serverId: e.target.value }))}
                className="mt-1"
              />
            </div>
            
            <div>
              <Label htmlFor="channelId" className="flex items-center space-x-2">
                <Hash className="w-4 h-4" />
                <span>Channel ID</span>
              </Label>
              <Input
                id="channelId"
                placeholder="ID del canale"
                value={config.channelId}
                onChange={(e) => setConfig(prev => ({ ...prev, channelId: e.target.value }))}
                className="mt-1"
              />
            </div>
          </div>
        </div>

        <div className="flex space-x-3 mt-6">
          <Button 
            onClick={handleConnect}
            className="flex-1"
            disabled={!config.token || !config.serverId || !config.channelId}
          >
            {botStatus === 'online' ? 'Riconnetti' : 'Connetti Bot'}
          </Button>
          <Button variant="outline" disabled={botStatus !== 'online'}>
            Test Connessione
          </Button>
        </div>
      </div>
    </Card>
  );
};