# discord_bot.py - Bot Discord principale
import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime
from config import CONFIG
from cache_manager import CacheManager
from scrapers.prime_gaming_scraper import PrimeGamingScraper
from scrapers.xbox_scraper import XboxGamePassScraper
from scrapers.ps_plus_scraper import PSPlusScraper

class GamingBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        # Inizializza cache e scrapers
        self.cache_manager = CacheManager(CONFIG.cache_file)
        self.scrapers = {
            'prime_gaming': PrimeGamingScraper(self.cache_manager),
            'xbox_gamepass': XboxGamePassScraper(self.cache_manager),
            'ps_plus': PSPlusScraper(self.cache_manager)
        }
    
    async def setup_hook(self):
        """Chiamato quando il bot si avvia"""
        print(f"Bot avviato come {self.user}")
        self.scraping_task.start()
    
    @tasks.loop(seconds=CONFIG.scrape_interval)
    async def scraping_task(self):
        """Task periodico per lo scraping"""
        print(f"Avvio scraping alle {datetime.now()}")
        
        for platform_key, scraper in self.scrapers.items():
            try:
                channel_id = CONFIG.channels.get(platform_key)
                if not channel_id:
                    continue
                
                channel = self.get_channel(channel_id)
                if not channel:
                    print(f"Canale non trovato per {platform_key}")
                    continue
                
                # Effettua lo scraping
                new_games = await scraper.scrape()
                
                # Invia i nuovi giochi trovati
                for game in new_games:
                    embed = self.create_game_embed(game)
                    try:
                        await channel.send(embed=embed)
                        await asyncio.sleep(1)  # Evita rate limiting
                    except Exception as e:
                        print(f"Errore nell'invio del messaggio: {e}")
                
                print(f"{platform_key}: {len(new_games)} nuovi giochi trovati")
                
            except Exception as e:
                print(f"Errore nello scraping di {platform_key}: {e}")
        
        # Salva la cache
        self.cache_manager.save_cache()
        print("Scraping completato")
    
    @scraping_task.before_loop
    async def before_scraping_task(self):
        """Aspetta che il bot sia pronto prima di iniziare lo scraping"""
        await self.wait_until_ready()
    
    def create_game_embed(self, game_data: dict) -> discord.Embed:
        """Crea un embed Discord per un gioco"""
        embed = discord.Embed(
            title=f"🎮 {game_data['title']}",
            description=f"Nuovo gioco disponibile su **{game_data['platform']}**!",
            color=self.get_platform_color(game_data['platform']),
            timestamp=datetime.now()
        )
        
        if game_data.get('image_url'):
            embed.set_thumbnail(url=game_data['image_url'])
        
        if game_data.get('url'):
            embed.add_field(name="Link", value=f"[Vai al gioco]({game_data['url']})", inline=False)
        
        embed.set_footer(text=f"Scraping Bot • {game_data['platform']}")
        
        return embed
    
    def get_platform_color(self, platform: str) -> int:
        """Restituisce un colore specifico per ogni piattaforma"""
        colors = {
            "Prime Gaming": 0x00A8FF,      # Blu Amazon
            "Xbox Game Pass": 0x107C10,    # Verde Xbox
            "PlayStation Plus": 0x003087   # Blu PlayStation
        }
        return colors.get(platform, 0x7289DA)  # Default Discord blurple
    
    @commands.command(name='scrape')
    async def manual_scrape(self, ctx):
        """Comando per avviare manualmente lo scraping"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Solo gli amministratori possono usare questo comando!")
            return
        
        await ctx.send("🔄 Avvio scraping manuale...")
        await self.scraping_task()
        await ctx.send("✅ Scraping completato!")
    
    @commands.command(name='status')
    async def bot_status(self, ctx):
        """Mostra lo stato del bot e dell'ultima scansione"""
        embed = discord.Embed(title="📊 Status Bot", color=0x00FF00)
        
        last_updates = self.cache_manager.cache_data.get('last_update', {})
        
        for platform_key, scraper in self.scrapers.items():
            last_update = last_updates.get(platform_key, "Mai")
            if last_update != "Mai":
                last_update = datetime.fromisoformat(last_update).strftime("%d/%m/%Y %H:%M")
            
            cache_size = len(self.cache_manager.cache_data.get(platform_key, []))
            embed.add_field(
                name=scraper.platform_name,
                value=f"Ultimo aggiornamento: {last_update}\nGames in cache: {cache_size}",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    async def close(self):
        """Pulizia quando il bot si chiude"""
        for scraper in self.scrapers.values():
            await scraper.close()
        await super().close()
