from bot import bot
from keyboards.inline_keyboards import get_main_keyboard
from messages.text_messages import messages

@bot.message_handler(commands=['start'])
def start_bot(message):
    """Обработчик команды /start"""
    user_name = message.from_user.first_name
    welcome_text = messages.welcome(user_name)

    bot.send_message(
        chat_id=message.chat.id,
        text=welcome_text,
        parse_mode='html',
        reply_markup=get_main_keyboard()
    )
