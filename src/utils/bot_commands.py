from telebot import types
from bot import bot

def set_bot_commands():
    """Устанавливает команды для меню бота"""
    
    commands = [
        types.BotCommand("start", "🚀 Запустить бота"),
        types.BotCommand("help", "❓ Показать справку"),
        types.BotCommand("commands", "📋 Список команд"),
    ]
    
    bot.set_my_commands(commands)