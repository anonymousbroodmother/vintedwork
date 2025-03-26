import logging
import random
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


fish_data = {
    "🐟 Карп": {"image": "https://carptoday.ru/wp-content/uploads/2022/02/1000x600-text-kopiya-kopiya-kopiya-kopiya-768x461.png", "chance": 20, "price": 5},
    "🐠 Форель": {"image": "https://lh6.googleusercontent.com/proxy/iOVst3UJmJdtp0dsYjePgJyK9iKJ7QZ2jxKZYJV3h-24rzAm5F9z5aZA_etRq-koZpnqR1XcEuroAVoYvbgPmY5QXsAd3DBvOtRnJInMM0njVoFWA8AHkZdptnuG4WThffPWNydv1g", "chance": 25, "price": 10},
    "🐡 Рыба-шар": {"image": "https://wildfauna.ru/wp-content/uploads/2019/03/ryba-shar-33.jpg", "chance": 20, "price": 15},
    "🦈 Акула": {"image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/White_shark.jpg/800px-White_shark.jpg", "chance": 10, "price": 50},
    "🐙 Осьминог": {"image": "https://upload.wikimedia.org/wikipedia/commons/0/0c/Octopus_vulgaris_02.JPG", "chance": 8, "price": 20},
    "🦀 Краб": {"image": "https://www.pharmocean.ru/sites/default/files/article/11_07_krab.jpg", "chance": 5, "price": 30},
    "💎 Алмаз": {"image": "https://sunlight.net/wiki/wp-content/uploads/2017/05/brilliant-5-400x267.jpg", "chance": 1, "price": 100},
}


rods = {
    "Удочка (обычная)": {"price": 50, "bonus": 1.0},
    "Удочка (улучшенная)": {"price": 100, "bonus": 1.5},
    "Удочка (превосходная)": {"price": 200, "bonus": 2.0},
}


inventory = {}
balances = {}
user_rods = {}

reply_keyboard = [["Рыбачить", "Инвентарь"], ["Магазин", "Продать рыбу"]]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    inventory[user_id] = {}
    balances[user_id] = 0
    user_rods[user_id] = "Удочка (обычная)"
    await update.message.reply_text(
        'Добро пожаловать на рыбалку! Используйте кнопки ниже, чтобы начать ловить рыбу или посмотреть инвентарь.',
        reply_markup=markup
    )

async def handle_fish(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    if user_id not in inventory:
        inventory[user_id] = {}

    rod_bonus = rods[user_rods[user_id]]["bonus"]
    items = list(fish_data.keys())
    weights = [fish_data[item]["chance"] * rod_bonus for item in items]
    catch = random.choices(items, weights=weights, k=1)[0]

    if catch in inventory[user_id]:
        inventory[user_id][catch] += 1
    else:
        inventory[user_id][catch] = 1

    await update.message.reply_photo(
        fish_data[catch]["image"],
        caption=f'{user_name}, вы поймали: {catch}!',
        reply_markup=markup
    )

async def handle_inventory(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    if user_id not in inventory or not inventory[user_id]:
        await update.message.reply_text(f'{user_name}, ваш инвентарь пуст.', reply_markup=markup)
    else:
        items = list(inventory[user_id].items())
        inventory_text = "\n".join([f"{item}: {count} шт." for item, count in items])
        await update.message.reply_text(f"Ваш инвентарь:\n{inventory_text}", reply_markup=markup)

async def handle_shop(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    shop_text = "Магазин удочек:\n"
    shop_text += "\n".join([f"{rod}: {data['price']} монет (Бонус: x{data['bonus']})" for rod, data in rods.items()])
    shop_text += "\n\nЧтобы купить удочку, используйте команду /buy <название удочки>."
    await update.message.reply_text(shop_text, reply_markup=markup)

async def buy_rod(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    try:
        rod_name = " ".join(context.args)
        if rod_name not in rods:
            await update.message.reply_text("Такой удочки нет в магазине.", reply_markup=markup)
            return

        rod_price = rods[rod_name]["price"]
        if balances.get(user_id, 0) < rod_price:
            await update.message.reply_text("Недостаточно монет для покупки.", reply_markup=markup)
            return

        balances[user_id] -= rod_price
        user_rods[user_id] = rod_name
        await update.message.reply_text(f"Вы купили {rod_name}!", reply_markup=markup)
    except Exception as e:
        await update.message.reply_text("Ошибка при покупке. Попробуйте снова.", reply_markup=markup)

async def sell_fish(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    if user_id not in inventory or not inventory[user_id]:
        await update.message.reply_text(f'{user_name}, у вас нет рыбы для продажи.', reply_markup=markup)
        return

    total_earned = 0
    for fish, count in inventory[user_id].items():
        total_earned += fish_data[fish]["price"] * count

    balances[user_id] = balances.get(user_id, 0) + total_earned
    inventory[user_id] = {}
    await update.message.reply_text(f'Вы продали всю рыбу и заработали {total_earned} монет!', reply_markup=markup)

async def show_balance(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    balance = balances.get(user_id, 0)
    await update.message.reply_text(f'Ваш баланс: {balance} монет.', reply_markup=markup)

async def unknown(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Извините, я не понимаю эту команду.", reply_markup=markup)

def main() -> None:
    application = Application.builder().token("8029476647:AAHxrpRVyK-osNrapg5F-BWmyngcGPwqSHM").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Text("Рыбачить"), handle_fish))
    application.add_handler(MessageHandler(filters.Text("Инвентарь"), handle_inventory))
    application.add_handler(MessageHandler(filters.Text("Магазин"), handle_shop))
    application.add_handler(MessageHandler(filters.Text("Продать рыбу"), sell_fish))
    application.add_handler(CommandHandler("balance", show_balance))
    application.add_handler(CommandHandler("buy", buy_rod))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    application.run_polling()

if __name__ == '__main__':
    main()