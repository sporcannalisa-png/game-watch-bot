import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Palette, Copy, Send } from "lucide-react";
import { useState } from "react";

interface EmbedData {
  title: string;
  description: string;
  color: string;
  thumbnail: string;
  footer: string;
}

export const DiscordEmbedPreview = () => {
  const [embedData, setEmbedData] = useState<EmbedData>({
    title: "🎮 Nuovo Gioco Disponibile!",
    description: "**Cyberpunk 2077: Phantom Liberty**\n\nUn'espansione epica per il mondo di Night City. Immergiti in una nuova storia ricca di azione e intrigo.\n\n💰 **Prezzo:** €29,99\n🏷️ **Sconto:** -20%\n📅 **Disponibile:** Ora",
    color: "#5865F2",
    thumbnail: "🎮",
    footer: "Bot Gaming • Oggi alle 14:30"
  });

  const handleInputChange = (field: keyof EmbedData, value: string) => {
    setEmbedData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Configurazione Embed */}
      <Card className="bg-gradient-card backdrop-blur-sm border-border/50">
        <div className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Palette className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold">Personalizza Embed</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Titolo</Label>
              <Input
                id="title"
                value={embedData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                className="mt-1"
              />
            </div>
            
            <div>
              <Label htmlFor="description">Descrizione</Label>
              <Textarea
                id="description"
                value={embedData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                rows={6}
                className="mt-1"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="color">Colore</Label>
                <div className="flex space-x-2 mt-1">
                  <Input
                    id="color"
                    value={embedData.color}
                    onChange={(e) => handleInputChange('color', e.target.value)}
                    className="flex-1"
                  />
                  <div 
                    className="w-10 h-10 rounded border"
                    style={{ backgroundColor: embedData.color }}
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="thumbnail">Thumbnail</Label>
                <Input
                  id="thumbnail"
                  value={embedData.thumbnail}
                  onChange={(e) => handleInputChange('thumbnail', e.target.value)}
                  className="mt-1"
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="footer">Footer</Label>
              <Input
                id="footer"
                value={embedData.footer}
                onChange={(e) => handleInputChange('footer', e.target.value)}
                className="mt-1"
              />
            </div>
          </div>
        </div>
      </Card>

      {/* Preview Embed */}
      <Card className="bg-gradient-card backdrop-blur-sm border-border/50">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Preview Discord</h3>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm">
                <Copy className="w-4 h-4 mr-2" />
                Copia
              </Button>
              <Button size="sm">
                <Send className="w-4 h-4 mr-2" />
                Test
              </Button>
            </div>
          </div>
          
          {/* Discord-style embed preview */}
          <div className="bg-[#2f3136] rounded-lg p-4 text-white font-mono text-sm">
            <div className="flex items-start space-x-3 mb-3">
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-xs font-bold">
                GB
              </div>
              <div>
                <div className="font-semibold">Gaming Bot</div>
                <div className="text-xs text-gray-400">Oggi alle 14:30</div>
              </div>
            </div>
            
            <div 
              className="border-l-4 pl-4 rounded-r bg-[#36393f] p-4"
              style={{ borderLeftColor: embedData.color }}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <div className="text-lg font-bold text-white mb-2">
                    {embedData.title}
                  </div>
                  <div className="text-gray-300 whitespace-pre-line text-sm leading-relaxed">
                    {embedData.description}
                  </div>
                </div>
                {embedData.thumbnail && (
                  <div className="ml-4 text-2xl">
                    {embedData.thumbnail}
                  </div>
                )}
              </div>
              <div className="text-xs text-gray-400 mt-3 border-t border-gray-600 pt-2">
                {embedData.footer}
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};