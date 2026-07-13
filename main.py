import telebot
from telebot import types
import random
import json
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Не задан BOT_TOKEN! Проверьте переменные окружения.")

bot = telebot.TeleBot(TOKEN)
DB_FILE = "users_balance.json"

def load_balances():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_balances(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

balances = load_balances()

def get_balance(user_id: int) -> int:
    return balances.get(str(user_id), 100)

def set_balance(user_id: int, amount: int):
    balances[str(user_id)] = amount
    save_balances(balances)

def add_balance(user_id: int, amount: int):
    current = get_balance(user_id)
    set_balance(user_id, current + amount)

# Шансы: 0x — 60%, 1x — 25%, 1.5x — 10%, 2x — 4%, 5x — 1%
def roll_multiplier():
    options = [0, 1, 1.5, 2, 5]
    weights = [60, 25, 10, 4, 1]
    return random.choices(options, weights=weights, k=1)[0]

@bot.message_handler(commands=["start"])
def cmd_start(message):
    user_id = message.from_user.id
    if str(user_id) not in balances:
        balances[str(user_id)] = 100
        save_balances(balances)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("💰 Мой баланс")
    btn2 = types.KeyboardButton("🎲 Ставка (/зов)")
    btn3 = types.KeyboardButton("❓ Помощь")
    markup.add(btn1, btn2, btn3)
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}!\n"
        "У тебя есть внутренняя валюта. Попробуй ставку или проверь баланс.",
        reply_markup=markup
    )

@bot.message_handler(commands=["зов"])
def cmd_zov(message):
    play_game(message)

@bot.message_handler(func=lambda m: m.text == "🎲 Ставка (/зов)")
def handle_bet_btn(message):
    play_game(message)

def play_game(message):
    user_id = message.from_user.id
    cost = 10
    balance = get_balance(user_id)

    if balance < cost:
        bot.send_message(message.chat.id, f"Недостаточно валюты! Твой баланс: {balance}. Нужно минимум {cost}.")
        return

    set_balance(user_id, balance - cost)
    multiplier = roll_multiplier()
    win_amount = int(cost * multiplier)

    if multiplier == 0:
        text = f"😕 Увы, ты ничего не выиграл. Множитель: {multiplier}x. Твой баланс: {get_balance(user_id)}"
    else:
        add_balance(user_id, win_amount)
        text = (f"🎉 Победа! Множитель: {multiplier}x\n"
                f"Ты выиграл {win_amount} валюты.\n"
                f"Твой баланс: {get_balance(user_id)}")

    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "💰 Мой баланс")
def handle_balance(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, f"Твой баланс: {get_balance(user_id)} валюты.")

@bot.message_handler(func=lambda m: m.text == "❓ Помощь")
def handle_help(message):
    bot.send_message(
        message.chat.id,
        "Команды:\n"
        "/start — запустить бота и получить стартовый баланс\n"
        "/зов или кнопка «Ставка» — сделать ставку (стоит 10 валюты)\n"
        "💰 Мой баланс — посмотреть текущий баланс\n"
        "❓ Помощь — показать это меню"
    )

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
