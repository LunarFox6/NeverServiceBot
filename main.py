import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from mcstatus import BedrockServer
from aiohttp import web

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

SERVER_IP = "mc.neverbox.su"
SERVER_PORT = 19132

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def check_bedrock_status():
    try:
        server = BedrockServer(SERVER_IP, SERVER_PORT)
        status = await server.async_status(timeout=5.0)
        
        online = status.players.online
        max_players = status.players.max
        
        msg = (
            f"🎮 **Статус сервера NeverBox**\n\n"
            f"🟢 **Состояние:** Онлайн\n"
            f"👥 **Игроки:** `{online}/{max_players}`\n"
            f"🌐 **IP:** `{SERVER_IP}:{SERVER_PORT}`"
        )
        return msg
    except Exception as e:
        return (
            f"🔴 **Сервер недоступен**\n"
            f"🌐 **IP:** `{SERVER_IP}:{SERVER_PORT}`\n"
            f"⚠️ *Сервер выключен или превышено время ожидания.*"
        )

@dp.message(Command("start", "online", "status"))
async def cmd_status(message: types.Message):
    wait_msg = await message.answer("⏳ Проверяю статус сервера...")
    text = await check_bedrock_status()
    await wait_msg.edit_text(text, parse_mode="Markdown")

# Заглушка для Render, чтобы он видел открытый порт
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def main():
    # Запускаем фейковый веб-сервер для Render на порту 10000 (или PORT из env)
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print("Бот и фейк-сервер успешно запущены!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
