import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Settings, ExternalLink } from "lucide-react";

interface PlatformCardProps {
  name: string;
  logo: string;
  status: 'active' | 'inactive' | 'error';
  lastUpdate: string;
  gamesFound: number;
  enabled: boolean;
  onToggle: (enabled: boolean) => void;
  onConfigure: () => void;
}

export const PlatformCard = ({
  name,
  logo,
  status,
  lastUpdate,
  gamesFound,
  enabled,
  onToggle,
  onConfigure
}: PlatformCardProps) => {
  const getStatusColor = () => {
    switch (status) {
      case 'active': return 'bg-success/20 text-success border-success/30';
      case 'error': return 'bg-destructive/20 text-destructive border-destructive/30';
      default: return 'bg-muted/20 text-muted-foreground border-muted/30';
    }
  };

  return (
    <Card className="relative overflow-hidden bg-gradient-card backdrop-blur-sm border-border/50 hover:shadow-card transition-smooth hover:-translate-y-1">
      <div className="absolute inset-0 bg-gradient-hero opacity-30" />
      <div className="relative p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center text-lg font-bold">
              {logo}
            </div>
            <div>
              <h3 className="font-semibold text-foreground">{name}</h3>
              <Badge className={`text-xs ${getStatusColor()}`}>
                {status}
              </Badge>
            </div>
          </div>
          <Switch checked={enabled} onCheckedChange={onToggle} />
        </div>
        
        <div className="space-y-2 mb-4">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Ultimo aggiornamento:</span>
            <span className="text-foreground">{lastUpdate}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Giochi trovati:</span>
            <span className="text-accent font-medium">{gamesFound}</span>
          </div>
        </div>

        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onConfigure}
            className="flex-1"
          >
            <Settings className="w-4 h-4 mr-2" />
            Configura
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="px-3"
          >
            <ExternalLink className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
};