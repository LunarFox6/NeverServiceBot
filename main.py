import asyncio
import json
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from mcstatus import BedrockServer

# ---------------- НАСТРОЙКИ ----------------
# Токен считывается из переменных окружения хостинга
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    sys.exit("Ошибка: Переменная BOT_TOKEN не найдена!")

SERVER_IP = "mc.neverbox.su"
SERVER_PORT = 19132

OWNER_ID = 7868300092
CONFIG_FILE = "config.json"
# --------------------------------------------

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def load_config():
    if not os.path.exists(CONFIG_FILE):
        data = {"admins": [OWNER_ID], "chats": []}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

config = load_config()

# --- КОМАНДЫ УПРАВЛЕНИЯ (ТОЛЬКО ДЛЯ ВЛАДЕЛЬЦА) ---

@dp.message(Command("addadmin"))
async def add_admin(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return
    
    args = message.text.split()
    if len(args) < 2 or not args[1].removeprefix("-").isdigit():
        await message.answer("💚 Использование: /addadmin ID")
        return

    admin_id = int(args[1])
    if admin_id not in config["admins"]:
        config["admins"].append(admin_id)
        save_config(config)
        await message.answer(f"💚 Админ {admin_id} добавлен")
    else:
        await message.answer("💚 Админ уже добавлен")

@dp.message(Command("deladmin"))
async def del_admin(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].removeprefix("-").isdigit():
        await message.answer("💚 Использование: /deladmin ID")
        return

    admin_id = int(args[1])
    if admin_id == OWNER_ID:
        await message.answer("💚 Нельзя удалить владельца")
        return

    if admin_id in config["admins"]:
        config["admins"].remove(admin_id)
        save_config(config)
        await message.answer(f"💚 Админ {admin_id} удалён")
    else:
        await message.answer("💚 Админ не найден")

@dp.message(Command("addchat"))
async def add_chat(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].removeprefix("-").isdigit():
        await message.answer("💚 Использование: /addchat ID")
        return

    chat_id = int(args[1])
    if chat_id not in config["chats"]:
        config["chats"].append(chat_id)
        save_config(config)
        await message.answer(f"💚 Чат {chat_id} добавлен")
    else:
        await message.answer("💚 Чат уже в списке")

@dp.message(Command("delchat"))
async def del_chat(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].removeprefix("-").isdigit():
        await message.answer("💚 Использование: /delchat ID")
        return

    chat_id = int(args[1])
    if chat_id in config["chats"]:
        config["chats"].remove(chat_id)
        save_config(config)
        await message.answer(f"💚 Чат {chat_id} удалён")
    else:
        await message.answer("💚 Чат не найден")

# --- ОСНОВНАЯ КОМАНДА ОНЛАЙНА ---

@dp.message(Command("start", "online", "status"))
async def get_server_status(message: types.Message):
    if message.chat.id not in config["chats"] and message.from_user.id not in config["admins"]:
        return

    try:
        server = BedrockServer.lookup(f"{SERVER_IP}:{SERVER_PORT}")
        status = await server.async_status()

        if status.players.sample:
            players_list = "\n".join([f"• {player.name}" for player in status.players.sample])
        else:
            players_list = "Игроков нет в сети"

        text = (
            f"💚 Онлайн на сервере: {status.players.online}/{status.players.max}\n"
            f"{players_list}\n\n"
            f"💚 Айпи: `{SERVER_IP}`"
        )
    except Exception:
        text = (
            f"💚 Сервер недоступен\n\n"
            f"💚 Айпи: `{SERVER_IP}`"
        )

    await message.answer(text, parse_mode=ParseMode.MARKDOWN_V2)

async def main():
    print("Бот запущен.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
