import logging
import random
from typing import Dict, Any
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ================== НАСТРОЙКИ ==================
TOKEN = "8746611426:AAF0_TEb7YMWtesWGidU5c3QhTNIQ9VsycY"
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================== ХРАНИЛИЩЕ ДАННЫХ ==================
active_games: Dict[int, Dict[str, Any]] = {}
user_stats: Dict[int, Dict[str, int]] = {}

# ================== КОНСТАНТЫ ИГР ==================
GAMES = {
    "coin": {"name": "🪙 Орёл или Решка", "emoji": "🪙"},
    "dice": {"name": "🎲 Кости", "emoji": "🎲"},
    "rps": {"name": "✂️ Камень-Ножницы-Бумага", "emoji": "✂️"},
    "number": {"name": "🔢 Угадай число", "emoji": "🔢"}
}

# ================== КОМАНДЫ ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие"""
    user = update.effective_user
    await update.message.reply_text(
        f"🎮 Привет, {user.first_name}!\n"
        f"Я игровой бот! Напиши /games чтобы начать!"
    )

async def games_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню игр"""
    keyboard = []
    for game_id, game_info in GAMES.items():
        keyboard.append([InlineKeyboardButton(
            f"{game_info['emoji']} {game_info['name']}", 
            callback_data=f"game_{game_id}"
        )])
    
    await update.message.reply_text(
        "🎮 Выбери игру:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика"""
    user_id = update.effective_user.id
    stats = user_stats.get(user_id, {"wins": 0, "games_played": 0})
    await update.message.reply_text(
        f"📊 Твоя статистика:\n"
        f"Игр: {stats['games_played']}\n"
        f"Побед: {stats['wins']}"
    )

# ================== ИГРЫ ==================
async def coin_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Орёл или Решка"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🦅 Орёл", callback_data="coin_heads"),
         InlineKeyboardButton("🪙 Решка", callback_data="coin_tails")]
    ])
    
    if update.callback_query:
        await update.callback_query.edit_message_text("🪙 Выбери сторону:", reply_markup=keyboard)
    else:
        await update.message.reply_text("🪙 Выбери сторону:", reply_markup=keyboard)

async def dice_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Кости"""
    keyboard = []
    row = []
    for i in range(1, 7):
        row.append(InlineKeyboardButton(f"{i}", callback_data=f"dice_{i}"))
        if i % 3 == 0:
            keyboard.append(row)
            row = []
    
    if update.callback_query:
        await update.callback_query.edit_message_text("🎲 Выбери число:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("🎲 Выбери число:", reply_markup=InlineKeyboardMarkup(keyboard))

async def rps_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Камень-Ножницы-Бумага"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗻 Камень", callback_data="rps_rock"),
         InlineKeyboardButton("✂️ Ножницы", callback_data="rps_scissors"),
         InlineKeyboardButton("📄 Бумага", callback_data="rps_paper")]
    ])
    
    if update.callback_query:
        await update.callback_query.edit_message_text("✂️ Выбери:", reply_markup=keyboard)
    else:
        await update.message.reply_text("✂️ Выбери:", reply_markup=keyboard)

async def number_game(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int = None):
    """Угадай число"""
    secret = random.randint(1, 10)
    active_games[chat_id] = {"secret": secret, "attempts": 0}
    
    keyboard = []
    row = []
    for i in range(1, 11):
        row.append(InlineKeyboardButton(f"{i}", callback_data=f"number_{i}"))
        if i % 5 == 0:
            keyboard.append(row)
            row = []
    
    if update.callback_query:
        await update.callback_query.edit_message_text("🔢 Я загадал число от 1 до 10:", 
                                                      reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("🔢 Я загадал число от 1 до 10:", 
                                        reply_markup=InlineKeyboardMarkup(keyboard))

# ================== ОБРАБОТКА КНОПОК ==================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка всех нажатий"""
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    data = query.data
    
    # Инициализация статистики
    if user_id not in user_stats:
        user_stats[user_id] = {"wins": 0, "games_played": 0}
    
    # Выбор игры из меню
    if data.startswith("game_"):
        game = data.replace("game_", "")
        if game == "coin":
            await coin_game(update, context)
        elif game == "dice":
            await dice_game(update, context)
        elif game == "rps":
            await rps_game(update, context)
        elif game == "number":
            await number_game(update, context, chat_id)
        return
    
    # Обработка игр
    if data.startswith("coin_"):
        result = random.choice(["heads", "tails"])
        win = (data == f"coin_{result}")
        text = "🦅 Орёл!" if result == "heads" else "🪙 Решка!"
        text += "\n\n✅ Ты выиграл!" if win else "\n\n❌ Ты проиграл!"
        if win:
            user_stats[user_id]["wins"] += 1
        user_stats[user_id]["games_played"] += 1
        await query.edit_message_text(text)
    
    elif data.startswith("dice_"):
        result = random.randint(1, 6)
        guess = int(data.split("_")[1])
        win = (guess == result)
        text = f"🎲 Выпало: {result}\n\n"
        text += "✅ Ты угадал!" if win else "❌ Не угадал!"
        if win:
            user_stats[user_id]["wins"] += 1
        user_stats[user_id]["games_played"] += 1
        await query.edit_message_text(text)
    
    elif data.startswith("rps_"):
        choices = {"rock": "🗻 Камень", "scissors": "✂️ Ножницы", "paper": "📄 Бумага"}
        user_choice = data.split("_")[1]
        bot_choice = random.choice(["rock", "scissors", "paper"])
        
        if user_choice == bot_choice:
            result = "🤝 Ничья!"
            win = False
        elif ((user_choice == "rock" and bot_choice == "scissors") or
              (user_choice == "scissors" and bot_choice == "paper") or
              (user_choice == "paper" and bot_choice == "rock")):
            result = "✅ Ты выиграл!"
            win = True
            user_stats[user_id]["wins"] += 1
        else:
            result = "❌ Я выиграл!"
            win = False
        
        user_stats[user_id]["games_played"] += 1
        await query.edit_message_text(
            f"Ты: {choices[user_choice]}\n"
            f"Я: {choices[bot_choice]}\n\n"
            f"{result}"
        )
    
    elif data.startswith("number_"):
        if chat_id not in active_games:
            await query.edit_message_text("❌ Игра не найдена!")
            return
        
        game = active_games[chat_id]
        guess = int(data.split("_")[1])
        game["attempts"] += 1
        
        if guess == game["secret"]:
            user_stats[user_id]["wins"] += 1
            user_stats[user_id]["games_played"] += 1
            await query.edit_message_text(
                f"🎉 Правильно! Это {game['secret']}!\n"
                f"Попыток: {game['attempts']}"
            )
            del active_games[chat_id]
        else:
            hint = "больше" if game["secret"] > guess else "меньше"
            await query.edit_message_text(
                f"❌ Не угадал! Загаданное число {hint} чем {guess}\n"
                f"Попробуй ещё:",
                reply_markup=query.message.reply_markup
            )

# ================== БЫСТРЫЕ КОМАНДЫ ==================
async def coin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await coin_game(update, context)

async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await dice_game(update, context)

async def rps_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await rps_game(update, context)

async def number_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await number_game(update, context, update.effective_chat.id)

# ================== ЗАПУСК ==================
def main():
    app = Application.builder().token(TOKEN).build()
    
    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("games", games_menu))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("coin", coin_command))
    app.add_handler(CommandHandler("dice", dice_command))
    app.add_handler(CommandHandler("rps", rps_command))
    app.add_handler(CommandHandler("number", number_command))
    
    # Кнопки
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("🤖 Бот запущен и готов к работе!")
    app.run_polling()

if __name__ == "__main__":
    main()
