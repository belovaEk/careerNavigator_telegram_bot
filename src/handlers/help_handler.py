from bot import bot
from keyboards.inline_keyboards import get_main_keyboard
from messages.text_messages import messages

@bot.message_handler(commands=['help'])
def help_bot(message):
    """Обработчик команды /help"""
   
    bot.send_message(
        chat_id=message.chat.id,
        text=messages.help(),
        parse_mode='markdown',
        reply_markup=get_main_keyboard()
    )