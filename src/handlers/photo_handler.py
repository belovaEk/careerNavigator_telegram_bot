from bot import bot
from state import user_states
from keyboards.inline_keyboards import get_professions_keyboard


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """Ловит фото, но реагирует, только если пользователь сейчас в сценарии 'Примерка карьеры'."""
    chat_id = message.chat.id
    state = user_states.get(chat_id)

    if not state or state.get("step") != "waiting_photo":
        # Фото прислано не в рамках примерки карьеры — просто игнорируем
        return

    # Берём фото в максимальном разрешении
    file_info = bot.get_file(message.photo[-1].file_id)
    photo_bytes = bot.download_file(file_info.file_path)

    state["photo_bytes"] = photo_bytes
    state["step"] = "waiting_profession"

    bot.send_message(
        chat_id,
        "Отлично! Теперь выбери профессию:",
        reply_markup=get_professions_keyboard()
    )