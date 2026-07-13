import telebot
from telebot import types
from config import config

bot = telebot.TeleBot(config.BOT_TOKEN)

@bot.message_handler(commands=['start'])
def startBot(message):
  first_mess = f"<b>{message.from_user.first_name} </b>, привет!\nЯ твой личный карьерный ассистент в Социальном казначействе.\nДавай превратим твою учебу в первую работу.\nВыбери, чем займемся сегодня:"
  markup = types.InlineKeyboardMarkup()
  button_resume = types.InlineKeyboardButton(text = 'Резюме', callback_data='resume')
  button_interview = types.InlineKeyboardButton(text = 'Собеседование', callback_data='interview')
  button_practice = types.InlineKeyboardButton(text = 'Практика', callback_data='practice')
  button_employment = types.InlineKeyboardButton(text = 'Трудоустройство', callback_data='employment')
  button_questions = types.InlineKeyboardButton(text = 'Вопросы', callback_data='questions')

  markup.add(button_resume, button_interview, button_practice, button_employment,button_questions)
  bot.send_message(message.chat.id, first_mess, parse_mode='html', reply_markup=markup)

# Чтобы бот крутился вечно
bot.infinity_polling()  