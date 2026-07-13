 import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import os

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Не задан BOT_TOKEN в переменных окружения!")

# Баланс в памяти (сбросится при полном рестарте сервера, но для старта идеально)
user_balances = {}

def get_or_create_balance(user_id: int) -> int:
    if user_id not in user_balances:
        user_balances[user_id] = 1000
    return user_balances[user_id]

def change_balance(user_id: int, delta: int) -> int:
    current = get_or_create_balance(user_id)
    new_balance = current + delta
    if new_balance < 0:
        return current
    user_balances[user_id] = new_balance
    return new_balance

SPIRITS = [
    {"name": "Ничего", "multiplier": 0.0},
    {"name": "Дух Амона", "multiplier": 1.5},
    {"name": "Дух Виверны", "multiplier": 2.0},
    {"name": "Дух Тайги", "multiplier": 5.0},
    {"name": "Дух Лисы", "multiplier": 10.0},
]
WEIGHTS = [60, 25, 10, 4, 1]

async def roll_spirit():
    return random.choices(SPIRITS, weights=WEIGHTS, k=1)[0]

def get_main_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="💰 Баланс"), KeyboardButton(text="🎲 /зов ставка")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 🎉\n"
        "Это игровой бот с внутренней валютой.\n"
        "Нажми кнопки ниже или используй команды.",
        reply_markup=get_main_keyboard()
    )

async def show_balance(message: types.Message):
    balance = get_or_create_balance(message.from_user.id)
    await message.answer(f"Твой баланс: {balance} монет 🪙")

async def cmd_roll(message: types.Message):
    user_id = message.from_user.id
    cost = 100

    balance = get_or_create_balance(user_id)
    if balance < cost:
        await message.answer(
            f"Недостаточно средств! Твой баланс: {balance} монет."
        )
        return

    change_balance(user_id,
   
 
