import logging

from bot import bot
from keyboards.inline_keyboards import get_main_keyboard, get_back_keyboard
from messages.text_messages import messages

# Импорты для примерки карьеры
from state import user_states
from services.image_generator import generate_career_image, PROFESSIONS

logger = logging.getLogger(__name__)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Обработчик нажатий на инлайн-кнопки"""

    # Обработка кнопки "Назад"
    if call.data == 'back_to_main':
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🔙 Возвращаемся в главное меню. Выберите интересующий вас раздел:",
            reply_markup=get_main_keyboard()
        )
        bot.answer_callback_query(call.id)
        return

    # Старт сценария "Примерка карьеры"
    if call.data == 'career_tryon':
        chat_id = call.message.chat.id
        user_states[chat_id] = {"step": "waiting_photo", "photo_bytes": None}
        bot.send_message(chat_id, "Пришли мне своё фото (желательно чёткое, лицо крупным планом).")
        bot.answer_callback_query(call.id)
        return

    # Пользователь выбрал профессию
    if call.data.startswith('prof:'):
        chat_id = call.message.chat.id
        state = user_states.get(chat_id)

        if not state or state.get("step") != "waiting_profession" or not state.get("photo_bytes"):
            bot.answer_callback_query(call.id, "Сначала пришли фото.")
            return

        profession_key = call.data.split(":", 1)[1]
        label, _prompt = PROFESSIONS[profession_key]

        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, f"Генерирую тебя в роли: {label}… это может занять до минуты ⏳")

        try:
            result_buffer = generate_career_image(state["photo_bytes"], profession_key)
            bot.send_photo(chat_id, result_buffer, caption=f"Вот ты в роли: {label} 🎉")
        except Exception:
            logger.exception("Ошибка генерации изображения в примерке карьеры")
            bot.send_message(chat_id, "Что-то пошло не так при генерации. Попробуй ещё раз чуть позже.")
        finally:
            user_states.pop(chat_id, None)
        return

    # Словарь для сопоставления callback_data с функциями-генераторами сообщений
    message_map = {
        'resume': messages.resume,
        'interview': messages.interview,
        'practice': messages.practice,
        'employment': messages.employment,
        'questions': messages.questions
    }

    if call.data in message_map:
        # Получаем текст сообщения
        response_text = message_map[call.data]()

        # Редактируем текущее сообщение (заменяем текст и клавиатуру)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response_text,
            parse_mode='markdown',
            reply_markup=get_back_keyboard()
        )
        bot.answer_callback_query(call.id)

# Обработчик для кнопки "Назад" можно добавить отдельно