# main.py - File principale per avviare il bot
import asyncio
from discord_bot import GamingBot
from config import CONFIG

async def main():
    bot = GamingBot()
    
    try:
        await bot.start(CONFIG.token)
    except KeyboardInterrupt:
        print("Bot fermato dall'utente")
    except Exception as e:
        print(f"Errore nell'avvio del bot: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())