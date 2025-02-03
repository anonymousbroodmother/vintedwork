import logging
import random
from telegram import Update, ReplyKeyboardMarkup  
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


fish_data = {
    "🐟 Карп": "https://carptoday.ru/wp-content/uploads/2022/02/1000x600-text-kopiya-kopiya-kopiya-kopiya-768x461.png",  
    "🐠 Форель": "https://lh6.googleusercontent.com/proxy/iOVst3UJmJdtp0dsYjePgJyK9iKJ7QZ2jxKZYJV3h-24rzAm5F9z5aZA_etRq-koZpnqR1XcEuroAVoYvbgPmY5QXsAd3DBvOtRnJInMM0njVoFWA8AHkZdptnuG4WThffPWNydv1g",
    "🐡 Рыба-шар": "https://wildfauna.ru/wp-content/uploads/2019/03/ryba-shar-33.jpg",
    "🦈 Акула": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/White_shark.jpg/800px-White_shark.jpg",
    "🐙 Осьминог": "https://upload.wikimedia.org/wikipedia/commons/0/0c/Octopus_vulgaris_02.JPG",
    "🦀 Краб": "https://www.pharmocean.ru/sites/default/files/article/11_07_krab.jpg",
    "👢 Ботинок": "https://images.selfedge.com/cache/catalog/20240215/Rick_Owens_DRKSHDW_Ramones_Dark_Dust_Milk_Milk_Cotton_Barre-01-680x1025.jpg",
    "🗑️ Мусор": "https://vlv-mag.com/assets/img/Stil-zizni/2018/8-vipusk/adidas-ultra-boots/adidas-ultra-boost-003-min.jpg",
    "💎 Алмаз": "https://sunlight.net/wiki/wp-content/uploads/2017/05/brilliant-5-400x267.jpg",
    "🧦 Носок": ""
}


inventory = {}


reply_keyboard = [["Рыбачить", "Инвентарь"]]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)


async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    inventory[user_id] = []  
    await update.message.reply_text(
        'Добро пожаловать на рыбалку! Используйте кнопки ниже, чтобы начать ловить рыбу или посмотреть инвентарь.',
        reply_markup=markup
    )


async def handle_fish(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

   
    if user_id not in inventory:
        inventory[user_id] = []

    
    catch, image_url = random.choice(list(fish_data.items()))
    inventory[user_id].append(catch)  

    
    await update.message.reply_photo(image_url, caption=f'{user_name}, вы поймали: {catch}!', reply_markup=markup)


async def handle_inventory(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

   
    if user_id not in inventory or not inventory[user_id]:
        await update.message.reply_text(f'{user_name}, ваш инвентарь пуст.', reply_markup=markup)
    else:
        
        inventory_text = "\n".join(inventory[user_id])
        await update.message.reply_text(f'{user_name}, ваш инвентарь:\n{inventory_text}', reply_markup=markup)

       
        for item in inventory[user_id]:
            if item in fish_data:
                await update.message.reply_photo(fish_data[item], caption=item)


async def unknown(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Извините, я не понимаю эту команду.", reply_markup=markup)

def main() -> None:
    
    application = Application.builder().token("8029476647:AAHxrpRVyK-osNrapg5F-BWmyngcGPwqSHM").build()

    
    application.add_handler(CommandHandler("start", start))

   
    application.add_handler(MessageHandler(filters.Text("Рыбачить"), handle_fish))
    application.add_handler(MessageHandler(filters.Text("Инвентарь"), handle_inventory))

    
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    application.run_polling()

if __name__ == '__main__':
    main()