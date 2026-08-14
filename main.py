import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

# Получаем токен из переменных окружения Render
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройки сервера
SERVER_IP = "mc.neverbox.su"
SERVER_PORT = 19132

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def check_bedrock_status():
    # Используем HTTP API для обхода блокировок UDP на облачных серверах
    url = f"https://api.mcsrvstat.us/bedrock/2/{SERVER_IP}:{SERVER_PORT}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5.0) as resp:
                data = await resp.json()
                
                if data.get("online"):
                    online = data.get("players", {}).get("online", 0)
                    max_players = data.get("players", {}).get("max", 0)
                    
                    return (
                        f"🎮 **Статус сервера NeverBox**\n\n"
                        f"🟢 **Состояние:** Онлайн\n"
                        f"👥 **Игроки:** `{online}/{max_players}`\n"
                        f"🌐 **IP:** `{SERVER_IP}:{SERVER_PORT}`"
                    )
                else:
                    return (
                        f"🔴 **Сервер недоступен**\n"
                        f"🌐 **IP:** `{SERVER_IP}:{SERVER_PORT}`\n"
                        f"⚠️ *Сервер выключен или не отвечает.*"
                    )
    except Exception as e:
        return (
            f"🔴 **Сервер недоступен**\n"
            f"🌐 **IP:** `{SERVER_IP}:{SERVER_PORT}`\n"
            f"⚠️ *Ошибка запроса к статусу.*"
        )

@dp.message(Command("start", "online", "status"))
async def cmd_status(message: types.Message):
    wait_msg = await message.answer("⏳ Проверяю статус сервера...")
    text = await check_bedrock_status()
    await wait_msg.edit_text(text, parse_mode="Markdown")

# Заглушка для Render, чтобы он видел открытый порт и не выдавал ошибку
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def main():
    # Запуск микро-веб-сервера для Render
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
