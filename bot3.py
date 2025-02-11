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
    "🐟 Карп": {"image": "https://carptoday.ru/wp-content/uploads/2022/02/1000x600-text-kopiya-kopiya-kopiya-kopiya-768x461.png", "chance": 30, "price": 10},
    "🐠 Форель": {"image": "https://lh6.googleusercontent.com/proxy/iOVst3UJmJdtp0dsYjePgJyK9iKJ7QZ2jxKZYJV3h-24rzAm5F9z5aZA_etRq-koZpnqR1XcEuroAVoYvbgPmY5QXsAd3DBvOtRnJInMM0njVoFWA8AHkZdptnuG4WThffPWNydv1g", "chance": 25, "price": 20},
    "🐡 Рыба-шар": {"image": "https://wildfauna.ru/wp-content/uploads/2019/03/ryba-shar-33.jpg", "chance": 20, "price": 30},
    "🦈 Акула": {"image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/White_shark.jpg/800px-White_shark.jpg", "chance": 10, "price": 50},
    "🐙 Осьминог": {"image": "https://upload.wikimedia.org/wikipedia/commons/0/0c/Octopus_vulgaris_02.JPG", "chance": 8, "price": 40},
    "🦀 Краб": {"image": "https://www.pharmocean.ru/sites/default/files/article/11_07_krab.jpg", "chance": 5, "price": 15},
    "👢 Ботинок": {"image": "https://images.selfedge.com/cache/catalog/20240215/Rick_Owens_DRKSHDW_Ramones_Dark_Dust_Milk_Milk_Cotton_Barre-01-680x1025.jpg", "chance": 1, "price": 1},
    "🗑️ Мусор": {"image": "https://vlv-mag.com/assets/img/Stil-zizni/2018/8-vipusk/adidas-ultra-boots/adidas-ultra-boost-003-min.jpg", "chance": 0.5, "price": 1},
    "💎 Алмаз": {"image": "https://sunlight.net/wiki/wp-content/uploads/2017/05/brilliant-5-400x267.jpg", "chance": 0.5, "price": 100},
    "🧦 Носок": {"image": "https://main-cdn.sbermegamarket.ru/big2/hlr-system/-27/447/117/732/817/2/600007040015b0.jpeg", "chance": 0.1, "price": 5}
}


rods_shop = {
    "🎣 Обычная удочка": {"price": 0, "multiplier": 1},  
    "🎣 Удочка PRO": {"price": 100, "multiplier": 1.5},  
    "🎣 Удочка VIP": {"price": 300, "multiplier": 2}     
}


inventory = {}


balance = {}


current_rod = {}


reply_keyboard = [["Рыбачить", "Инвентарь"], ["Магазин удочек", "Рынок"]]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)


async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    inventory[user_id] = {}  
    balance[user_id] = 0     
    current_rod[user_id] = "🎣 Обычная удочка"  
    await update.message.reply_text(
        'Добро пожаловать на рыбалку! Используйте кнопки ниже, чтобы начать ловить рыбу, посмотреть инвентарь, '
        'купить удочку или продать улов.',
        reply_markup=markup
    )


async def handle_fish(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    
    if user_id not in inventory:
        inventory[user_id] = {}

    
    rod = current_rod.get(user_id, "🎣 Обычная удочка")
    multiplier = rods_shop[rod]["multiplier"]

    
    items = list(fish_data.keys())
    weights = [fish_data[item]["chance"] * multiplier for item in items]
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


async def handle_shop(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    
    shop_text = "Магазин удочек:\n"
    for rod, data in rods_shop.items():
        shop_text += f"{rod}: {data['price']} монет\n"

    
    shop_text += f"\nВаша текущая удочка: {current_rod.get(user_id, '🎣 Обычная удочка')}"

    
    keyboard = [
        [InlineKeyboardButton(rod, callback_data=f"buy_{rod}")] for rod in rods_shop.keys()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(shop_text, reply_markup=reply_markup)


async def handle_market(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    
    if user_id not in inventory or not inventory[user_id]:
        await update.message.reply_text(f'{user_name}, ваш инвентарь пуст.', reply_markup=markup)
    else:
        
        market_text = "Рынок:\n"
        for item, count in inventory[user_id].items():
            market_text += f"{item}: {count} шт. (цена: {fish_data[item]['price']} монет за шт.)\n"

        
        keyboard = [
            [InlineKeyboardButton(f"Продать {item}", callback_data=f"sell_{item}")] for item in inventory[user_id].keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(market_text, reply_markup=reply_markup)


async def handle_buy_rod(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    rod = query.data.replace("buy_", "")  

    
    if balance.get(user_id, 0) >= rods_shop[rod]["price"]:
        balance[user_id] -= rods_shop[rod]["price"]  
        current_rod[user_id] = rod  
        await query.edit_message_text(f"Вы купили {rod}! Теперь ваша удочка: {rod}.")
    else:
        await query.edit_message_text("У вас недостаточно монет для покупки этой удочки.")


async def handle_sell_item(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    item = query.data.replace("sell_", "") 

    
    if item in inventory[user_id]:
        count = inventory[user_id].pop(item)  
        total_price = count * fish_data[item]["price"]
        balance[user_id] = balance.get(user_id, 0) + total_price  
        await query.edit_message_text(f"Вы продали {item} x{count} за {total_price} монет!")
    else:
        await query.edit_message_text("У вас нет этого предмета в инвентаре.")


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
    application.add_handler(MessageHandler(filters.Text("Магазин удочек"), handle_shop))
    application.add_handler(MessageHandler(filters.Text("Рынок"), handle_market))

    
    application.add_handler(CallbackQueryHandler(handle_inventory_pagination, pattern="^(prev_page|next_page)$"))

   
    application.add_handler(CallbackQueryHandler(handle_buy_rod, pattern="^buy_"))

    
    application.add_handler(CallbackQueryHandler(handle_sell_item, pattern="^sell_"))

   
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

  
    application.run_polling()

if __name__ == '__main__':
    main()