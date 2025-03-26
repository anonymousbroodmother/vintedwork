# 🎣 Fishing Bot для Telegram

Добро пожаловать в **Fishing Bot** — увлекательного Telegram-бота, где вы можете ловить рыбу, покупать удочки, продавать добычу и соревноваться с друзьями! Погрузитесь в мир рыбалки и попробуйте поймать как можно больше сокровищ.

---

## 🌟 Возможности бота

- **Рыбалка**: Ловите рыбу, сокровища и даже опасных акул!
  - Используйте свою удочку, чтобы поймать карпа, форель, осьминога и многое другое.
  - Осторожно: если вы поймаете акулу, вы потеряете все свои монеты и инвентарь! 🦈💀

- **Инвентарь**: Отслеживайте все пойманные предметы.
  - В любой момент вы можете посмотреть свой инвентарь и узнать, что у вас есть.

- **Рынок**: Продавайте рыбу и сокровища за монеты.
  - Используйте кнопку "Продать рыбу", чтобы продать все свои предметы разом и получить монеты.

- **Магазин удочек**: Улучшайте свою удочку, чтобы увеличить шансы на поимку редких предметов.
  - Покупайте новые удочки за монеты.
  - Каждая удочка имеет бонусный множитель, который увеличивает ваши шансы на поимку редкой рыбы.

- **Баланс**: Отслеживайте свои монеты.
  - Проверяйте свой баланс с помощью команды `/balance` или прямо в магазине.

- **Сохранение данных**: Все ваши достижения сохраняются в базе данных.
  - Даже если бот перезапустится, ваши данные останутся нетронутыми.

---

## 🛠️ Как использовать бота

1. Начните взаимодействие с ботом, отправив команду `/start`.
2. Используйте кнопки для управления:
   - **Рыбачить**: Попробуйте поймать рыбу или другие предметы.
   - **Инвентарь**: Посмотрите, что у вас есть в инвентаре.
   - **Магазин**: Купите новую удочку для улучшения шансов на успех.
   - **Продать рыбу**: Продайте всю рыбу из инвентаря за монеты.
3. Следите за своим балансом и старайтесь не попасться на акулу! 🦈

---

## 📚 Команды бота

- `/start` — Запуск бота и создание нового профиля.
- `/balance` — Проверка текущего баланса монет.
- `/buy <название удочки>` — Покупка удочки (альтернатива кнопкам в магазине).

---

## 💻 Техническая информация

- **Язык программирования**: Python
- **Библиотека**: [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- **База данных**: SQLite (для хранения данных о пользователях, их балансе, удочках и инвентаре)

---

## 🤝 Как запустить бота локально

1. **Клонируйте репозиторий**:
   ```bash
   git clone [https://github.com/anonymousbroodmother/vintedwork.git]
   cd vintedwork
   2. Установка зависимостей
   Установите необходимые библиотеки из файла requirements.txt:
    pip install -r requirements.txt
    Если у вас нет файла requirements.txt, создайте его и добавьте следующие зависимости:
    python-telegram-bot==20.5
    sqlite3
    Затем выполните команду:
    pip install python-telegram-bot==20.5
    3. Настройка токена бота
    Создайте файл .env в корневой директории проекта:
    touch .env
    Добавьте в файл .env токен вашего бота:
    BOT_TOKEN=токен бота
    4. Запуск бота
    Запустите бота с помощью команды:
    python bot.py
    Если всё настроено правильно, бот начнёт работать, и вы сможете взаимодействовать с ним через Telegram.


