import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from mcstatus import BedrockServer

# Получаем токен из переменных окружения Render
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ID Владельца
OWNER_ID = 7868300092

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

SERVER_IP = "mc.neverbox.su"
SERVER_PORT = 19132

async def check_bedrock_status():
    try:
        # Указываем хост и порт отдельно
        server = BedrockServer(SERVER_IP, SERVER_PORT)
        # Увеличиваем время ожидания ответа до 5 секунд
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
        # Если сервер не ответил за 5 секунд
        return (
            f"🔴 **Сервер недоступен**\n"
            f"🌐 **IP:** `{SERVER_IP}:{SERVER_PORT}`\n"
            f"⚠️ *Сервер выключен или превышено время ожидания.*"
        )

@dp.message(Command("start", "online", "status"))
async def cmd_status(message: types.Message):
    # Отправляем сообщение ожидания, так как запрос к серверу занимает пару секунд
    wait_msg = await message.answer("⏳ Проверяю статус сервера...")
    text = await check_bedrock_status()
    await wait_msg.edit_text(text, parse_mode="Markdown")

async def main():
    print("Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
