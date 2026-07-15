import logging

from bot import bot
from keyboards.inline_keyboards import get_main_keyboard, get_back_keyboard
from messages.text_messages import messages
from gradio_client.exceptions import AppError

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
            text="Выберите интересующий вас раздел:",
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

        # Обработка ошибки превышения лимита
        except AppError as e:
            error_msg = str(e)
            if "exceeded your ZeroGPU quota" in error_msg:
                logger.warning(f"Превышена ZeroGPU квота для пользователя {chat_id}")
                bot.send_message(
                    chat_id,
                    "⚠️ К сожалению, лимит генерации изображений на сегодня исчерпан.\n\n"
                    "Пожалуйста, попробуйте позже или воспользуйтесь другими функциями бота.\n"
                    "А пока можете изучить информацию о профессиях в главном меню! 📚"
                )
            else:
                # Другие ошибки AppError
                logger.error(f"Ошибка AppError: {error_msg}")
                bot.send_message(
                    chat_id,
                    "⚠️ Произошла ошибка при генерации изображения. Попробуйте позже."
                )
                
        except Exception as e:
            # Обработка всех остальных ошибок
            logger.exception("Ошибка генерации изображения в примерке карьеры")
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                bot.send_message(
                    chat_id,
                    "⏰ Превышено время ожидания. Попробуйте ещё раз или выберите другую профессию."
                )
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                bot.send_message(
                    chat_id,
                    "🌐 Проблемы с подключением к сервису генерации. Проверьте интернет-соединение и попробуйте позже."
                )
            else:
                bot.send_message(
                    chat_id,
                    "❌ Что-то пошло не так при генерации. Попробуй ещё раз чуть позже."
                )
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

        bot.send_message(
            chat_id=call.message.chat.id,
            text=response_text,
            parse_mode='markdown',
            reply_markup=get_back_keyboard()
        )
        bot.answer_callback_query(call.id)

# Обработчик для кнопки "Назад" можно добавить отдельно