# инициализация бота

import telebot
from config import config

# Создаём экземпляр бота
bot = telebot.TeleBot(config.BOT_TOKEN)
