import logging
import random
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


conn = sqlite3.connect('fishing_bot.db', check_same_thread=False)
cursor = conn.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    rod TEXT DEFAULT 'Удочка (обычная)'
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS inventory (
    user_id INTEGER,
    item TEXT,
    count INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
)
''')
conn.commit()


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


reply_keyboard = [["Рыбачить", "Инвентарь"], ["Магазин", "Продать рыбу"]]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

def get_user(user_id):
    """Получение данных пользователя из базы данных."""
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
        conn.commit()
        return {"user_id": user_id, "balance": 0, "rod": "Удочка (обычная)"}
    return {"user_id": user[0], "balance": user[1], "rod": user[2]}

def update_user(user_id, balance=None, rod=None):
    """Обновление данных пользователя в базе данных."""
    if balance is not None:
        cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (balance, user_id))
    if rod is not None:
        cursor.execute('UPDATE users SET rod = ? WHERE user_id = ?', (rod, user_id))
    conn.commit()

def get_inventory(user_id):
    """Получение инвентаря пользователя."""
    cursor.execute('SELECT item, count FROM inventory WHERE user_id = ?', (user_id,))
    return {item: count for item, count in cursor.fetchall()}

def update_inventory(user_id, item, count):
    """Обновление инвентаря пользователя."""
    cursor.execute('SELECT count FROM inventory WHERE user_id = ? AND item = ?', (user_id, item))
    current_count = cursor.fetchone()
    if current_count:
        new_count = current_count[0] + count
        if new_count <= 0:
            cursor.execute('DELETE FROM inventory WHERE user_id = ? AND item = ?', (user_id, item))
        else:
            cursor.execute('UPDATE inventory SET count = ? WHERE user_id = ? AND item = ?', (new_count, user_id, item))
    else:
        cursor.execute('INSERT INTO inventory (user_id, item, count) VALUES (?, ?, ?)', (user_id, item, count))
    conn.commit()

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    get_user(user_id) 
    await update.message.reply_text(
        'Добро пожаловать на рыбалку! Используйте кнопки ниже, чтобы начать ловить рыбу или посмотреть инвентарь.',
        reply_markup=markup
    )

async def handle_fish(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    user = get_user(user_id)
    rod_bonus = rods[user["rod"]]["bonus"]
    items = list(fish_data.keys())
    weights = [fish_data[item]["chance"] * rod_bonus for item in items]
    catch = random.choices(items, weights=weights, k=1)[0]

    
    if catch == "🦈 Акула":
        update_user(user_id, balance=0)  
        cursor.execute('DELETE FROM inventory WHERE user_id = ?', (user_id,))
        conn.commit()
        await update.message.reply_photo(
            fish_data[catch]["image"],
            caption=f'{user_name}, вы поймали акулу... но она вас утащила под воду! 🦈💀\n'
                    f'Вы потеряли все свои монеты и рыбу!',
            reply_markup=markup
        )
        return

    update_inventory(user_id, catch, 1)
    await update.message.reply_photo(
        fish_data[catch]["image"],
        caption=f'{user_name}, вы поймали: {catch}!',
        reply_markup=markup
    )

async def handle_inventory(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    inventory = get_inventory(user_id)
    if not inventory:
        await update.message.reply_text(f'{user_name}, ваш инвентарь пуст.', reply_markup=markup)
    else:
        inventory_text = "\n".join([f"{item}: {count} шт." for item, count in inventory.items()])
        await update.message.reply_text(f"Ваш инвентарь:\n{inventory_text}", reply_markup=markup)

async def handle_shop(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user = get_user(user_id)

    keyboard = []
    shop_text = f"Магазин удочек:\nВаш баланс: {user['balance']} 💰\n\n"
    for rod, data in rods.items():
        shop_text += f"{rod}: {data['price']} монет (Бонус: x{data['bonus']})\n"
        keyboard.append([InlineKeyboardButton(rod, callback_data=f"buy_{rod}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(shop_text, reply_markup=reply_markup)

async def handle_buy_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    rod_name = query.data.split("_", 1)[1]

    if rod_name not in rods:
        await query.edit_message_text("Такой удочки нет в магазине.")
        return

    rod_price = rods[rod_name]["price"]
    user = get_user(user_id)
    if user["balance"] < rod_price:
        await query.edit_message_text("Недостаточно монет для покупки.")
        return

    update_user(user_id, balance=user["balance"] - rod_price, rod=rod_name)
    await query.edit_message_text(f"Вы купили {rod_name}!")

async def sell_fish(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    inventory = get_inventory(user_id)
    if not inventory:
        await update.message.reply_text(f'{user_name}, у вас нет рыбы для продажи.', reply_markup=markup)
        return

    total_earned = 0
    for item, count in inventory.items():
        if item in fish_data:
            total_earned += fish_data[item]["price"] * count

    update_user(user_id, balance=get_user(user_id)["balance"] + total_earned)
    cursor.execute('DELETE FROM inventory WHERE user_id = ?', (user_id,))
    conn.commit()
    await update.message.reply_text(f'Вы продали всю рыбу и заработали {total_earned} монет!', reply_markup=markup)

async def show_balance(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user = get_user(user_id)
    await update.message.reply_text(f'Ваш баланс: {user["balance"]} монет.', reply_markup=markup)

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
    application.add_handler(CallbackQueryHandler(handle_buy_callback, pattern="^buy_"))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    application.run_polling()

if __name__ == '__main__':
    main()