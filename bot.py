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
    "🐟 Карп": {"image": "https://carptoday.ru/wp-content/uploads/2022/02/1000x600-text-kopiya-kopiya-kopiya-kopiya-768x461.png", "chance": 20},  
    "🐠 Форель": {"image": "https://lh6.googleusercontent.com/proxy/iOVst3UJmJdtp0dsYjePgJyK9iKJ7QZ2jxKZYJV3h-24rzAm5F9z5aZA_etRq-koZpnqR1XcEuroAVoYvbgPmY5QXsAd3DBvOtRnJInMM0njVoFWA8AHkZdptnuG4WThffPWNydv1g", "chance": 25},
    "🐡 Рыба-шар": {"image": "https://wildfauna.ru/wp-content/uploads/2019/03/ryba-shar-33.jpg", "chance": 20},
    "🦈 Акула": {"image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/White_shark.jpg/800px-White_shark.jpg", "chance": 10},
    "🐙 Осьминог": {"image": "https://upload.wikimedia.org/wikipedia/commons/0/0c/Octopus_vulgaris_02.JPG", "chance": 8},
    "🦀 Краб": {"image": "https://www.pharmocean.ru/sites/default/files/article/11_07_krab.jpg", "chance": 5},
    "👢 Ботинок": {"image": "https://images.selfedge.com/cache/catalog/20240215/Rick_Owens_DRKSHDW_Ramones_Dark_Dust_Milk_Milk_Cotton_Barre-01-680x1025.jpg", "chance": 10},
    "🗑️ Мусор": {"image": "https://vlv-mag.com/assets/img/Stil-zizni/2018/8-vipusk/adidas-ultra-boots/adidas-ultra-boost-003-min.jpg", "chance": 0.5},
    "💎 Алмаз": {"image": "https://sunlight.net/wiki/wp-content/uploads/2017/05/brilliant-5-400x267.jpg", "chance": 1},
    "🧦 Носок": {"image": "", "chance": 0.1}
}


inventory = {}


reply_keyboard = [["Рыбачить", "Инвентарь"]]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)


async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    inventory[user_id] = {}  
    await update.message.reply_text(
        'Добро пожаловать на рыбалку! Используйте кнопки ниже, чтобы начать ловить рыбу или посмотреть инвентарь.',
        reply_markup=markup
    )


async def handle_fish(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    
    if user_id not in inventory:
        inventory[user_id] = {}

    
    items = list(fish_data.keys())
    weights = [fish_data[item]["chance"] for item in items]
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
        context.user_data["inventory_page"] = 0  
        await show_inventory_page(update, context, items)


async def show_inventory_page(update: Update, context: CallbackContext, items: list) -> None:
    page = context.user_data.get("inventory_page", 0)
    start_index = page * 5
    end_index = start_index + 5
    page_items = items[start_index:end_index]

    
    inventory_text = "\n".join([f"{item}: {count} шт." for item, count in page_items])
    text = f"Ваш инвентарь (страница {page + 1}):\n{inventory_text}"

    
    keyboard = []
    if page > 0:
        keyboard.append(InlineKeyboardButton("⬅️ Назад", callback_data="prev_page"))
    if end_index < len(items):
        keyboard.append(InlineKeyboardButton("Вперед ➡️", callback_data="next_page"))
    reply_markup = InlineKeyboardMarkup([keyboard]) if keyboard else None

    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)


async def handle_inventory_pagination(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    items = list(inventory[user_id].items())

    if query.data == "prev_page":
        context.user_data["inventory_page"] -= 1
    elif query.data == "next_page":
        context.user_data["inventory_page"] += 1

    await show_inventory_page(update, context, items)


async def unknown(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Извините, я не понимаю эту команду.", reply_markup=markup)

def main() -> None:
    
    application = Application.builder().token("8029476647:AAHxrpRVyK-osNrapg5F-BWmyngcGPwqSHM").build()

    
    application.add_handler(CommandHandler("start", start))

    
    application.add_handler(MessageHandler(filters.Text("Рыбачить"), handle_fish))
    application.add_handler(MessageHandler(filters.Text("Инвентарь"), handle_inventory))

    
    application.add_handler(CallbackQueryHandler(handle_inventory_pagination, pattern="^(prev_page|next_page)$"))

    
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    
    application.run_polling()

if __name__ == '__main__':
    main()