import logging
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Список возможных уловов
fish_list = [
    "🐟 Карп",
    "🐠 Форель",
    "🐡 Рыба-шар",
    "🦈 Акула",
    "🐙 Осьминог",
    "🦀 Краб",
    "👢 Ботинок",
    "🗑️ Мусор",
    "💎 Алмаз",
    "🧦 Носок"
]

# Команда /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Добро пожаловать на рыбалку! Используйте команду /fish, чтобы начать ловить рыбу.')

# Команда /fish
async def fish(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    catch = random.choice(fish_list)
    await update.message.reply_text(f'{user.first_name}, вы поймали: {catch}!')

# Обработка неизвестных команд
async def unknown(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Извините, я не понимаю эту команду.")

def main() -> None:
    # Вставьте сюда ваш токен
    application = Application.builder().token("8029476647:AAHxrpRVyK-osNrapg5F-BWmyngcGPwqSHM").build()

    # Регистрация команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("fish", fish))

    # Обработка неизвестных команд
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()