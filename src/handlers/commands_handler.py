from bot import bot
from messages.text_messages import messages

@bot.message_handler(commands=['commands'])
def list_commands(message):
    """Обработчик команды /commands"""
    bot.send_message(
        chat_id=message.chat.id,
        text=messages.commands(),
        parse_mode='markdown'
    )
