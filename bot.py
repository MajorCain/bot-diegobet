import asyncio
from telegram import Bot

# Seu token e chat_id
TOKEN = "7516769955:AAGGmyqQ5-jNtxuzVNXU3iSQrzS8p5adzTo"
chat_id = "1306578324"  # ou o ID numérico do canal ou grupo

bot = Bot(token=TOKEN)

async def main():
    await bot.send_message(chat_id=chat_id, text="Aposta interessante disponível!")

asyncio.run(main())
