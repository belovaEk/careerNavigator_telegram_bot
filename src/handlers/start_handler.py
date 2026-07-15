import os
import logging

from bot import bot
from keyboards.inline_keyboards import get_main_keyboard
from messages.text_messages import messages

logger = logging.getLogger(__name__)


@bot.message_handler(commands=['start'])
def start_bot(message):
    """Обработчик команды /start"""
    user_name = message.from_user.first_name
    welcome_text = messages.welcome(user_name)

    photo_path = os.path.join("assets", "images", "start.png")

    try:
        if photo_path:
            with open(photo_path, "rb") as photo:
                bot.send_photo(
                    chat_id=message.chat.id,
                    photo=photo,
                    caption=welcome_text,
                    parse_mode="markdown",
                    reply_markup=get_main_keyboard(),
                )
        else:
            # Фото не задано — отправляем как обычный текст, чтобы не терять контент
            bot.send_message(
                chat_id=message.chat.id,
                text=welcome_text,
                parse_mode="markdown",
                reply_markup=get_main_keyboard(),
            )
    except FileNotFoundError:
        logger.error(f"Не найден файл фото: {photo_path}")
        bot.send_message(
            chat_id=message.chat.id,
            text=welcome_text,
            parse_mode="markdown",
            reply_markup=get_main_keyboard(),
        )