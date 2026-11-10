import asyncio
import logging
import sys
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Вставте сюди свій токен, отриманий від @BotFather
TOKEN = "9091910549:AAHDCMsJsiFXhynKffyGi6gq0YORTz1G_Fk"

# Створюємо об'єкти бота та диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# Словник для збереження активних чатів та ID їх останніх повідомлень
active_users = {} # {chat_id: message_id}

# Функція отримання даних для с. Прибірськ
def get_current_data():
    # Тут ви можете змінювати текст статусу під реальний стан
    status = "Світло є за графіком 🟢 (Черга: 3.1)"
    current_time = datetime.now().strftime("%H:%M:%S")
    
    return (
        "📍 **Моніторинг світла: с. Прибірськ**\n\n"
        f"Стан: {status}\n"
        f"Останнє оновлення: {current_time}"
    )

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    chat_id = message.chat.id
    initial_text = get_current_data()
    
    # Відправляємо первинне повідомлення
    sent_message = await message.answer(initial_text, parse_mode="Markdown")
    
    # Зберігаємо ID повідомлення для цього користувача
    active_users[chat_id] = sent_message.message_id
    
    # Видаляємо команду /start для чистоти чату
    try:
        await message.delete()
    except Exception:
        pass

# Функція фонового оновлення, яка виконується за розкладом
async def update_status_task():
    if not active_users:
        return
    
    new_text = get_current_data()
    
    # Проходимо по всіх підписаних користувачах і оновлюємо їхні повідомлення
    for chat_id, message_id in list(active_users.items()):
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=new_text,
                parse_mode="Markdown"
            )
        except Exception as e:
            # Якщо користувач заблокував бота — видаляємо його з розсилки
            print(f"Не вдалося оновити повідомлення для {chat_id}: {e}")
            active_users.pop(chat_id, None)

async def main():
    # Налаштовуємо планувальник: запускати оновлення кожні 30 секунд
    scheduler.add_job(update_status_task, "interval", seconds=30)
    scheduler.start()
    
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    print("Бот запущено і готовий до роботи!")
    
    # Запуск polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
