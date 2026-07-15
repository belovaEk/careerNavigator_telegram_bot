import logging
import os

from bot import bot
from keyboards.inline_keyboards import get_main_keyboard, get_back_keyboard
from messages.text_messages import messages
from gradio_client.exceptions import AppError

# Импорты для примерки карьеры
from state import user_states
from services.image_generator import generate_career_image, PROFESSIONS

logger = logging.getLogger(__name__)

# Папки с медиафайлами относительно точки запуска бота
IMAGES_DIR = os.path.join("assets", "images")
DOCUMENTS_DIR = os.path.join("assets", "documents")

# Для каждого раздела: имя файла-картинки (обязательно) и файла-документа (опционально)
# Если для раздела не нужен документ — просто не указывай ключ "document" или ставь None.
SECTION_ASSETS = {
    "resume": {
        "photo": "resume.png",
        "document": "resume_template.docx",
    },
    "interview": {
        "photo": "interview.png",
        "document": None,
    },
    "practice": {
        "photo": "practice.png",
        "document": "practice_recommendations.docx",
    },
    "employment": {
        "photo": "employment.png",
        "document": ["employment_docs_list.pdf", "application_form.docx"],
    },
    "questions": {
        "photo": "questions.png",
        "document": None,
    },
}

# Словарь для сопоставления callback_data с функциями-генераторами текста (caption)
message_map = {
    "resume": messages.resume,
    "interview": messages.interview,
    "practice": messages.practice,
    "employment": messages.employment,
    "questions": messages.questions,
}


def send_section(chat_id: int, section_key: str):
    """Отправляет раздел: фото с подписью, а следом документ, если он есть."""

    caption = message_map[section_key]()
    assets = SECTION_ASSETS.get(section_key, {})
    photo_filename = assets.get("photo")
    document_field = assets.get("document")

    # document может быть: None, одной строкой или списком строк.
    # Приводим всё к единому виду — списку, даже если он пустой.
    if not document_field:
        document_filenames = []
    elif isinstance(document_field, str):
        document_filenames = [document_field]
    else:
        document_filenames = list(document_field)

    # Кнопка "Назад" вешается на самое последнее сообщение в цепочке:
    # на фото, если документов нет, или на последний документ, если они есть.
    photo_reply_markup = None if document_filenames else get_back_keyboard()

    photo_path = os.path.join(IMAGES_DIR, photo_filename) if photo_filename else None

    try:
        if photo_path:
            with open(photo_path, "rb") as photo:
                bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=caption,
                    parse_mode="markdown",
                    reply_markup=photo_reply_markup,
                )
        else:
            # Фото не задано — отправляем как обычный текст, чтобы не терять контент
            bot.send_message(
                chat_id=chat_id,
                text=caption,
                parse_mode="markdown",
                reply_markup=photo_reply_markup,
            )
    except FileNotFoundError:
        logger.error(f"Не найден файл фото: {photo_path}")
        bot.send_message(
            chat_id=chat_id,
            text=caption,
            parse_mode="markdown",
            reply_markup=photo_reply_markup,
        )

    for index, document_filename in enumerate(document_filenames):
        is_last = index == len(document_filenames) - 1
        document_path = os.path.join(DOCUMENTS_DIR, document_filename)
        try:
            with open(document_path, "rb") as document:
                bot.send_document(
                    chat_id=chat_id,
                    document=document,
                    # Кнопку вешаем только на последний файл в цепочке
                    reply_markup=get_back_keyboard() if is_last else None,
                )
        except FileNotFoundError:
            logger.error(f"Не найден файл документа: {document_path}")
            bot.send_message(
                chat_id=chat_id,
                text="⚠️ Не удалось прикрепить файл. Попробуйте позже.",
                reply_markup=get_back_keyboard() if is_last else None,
            )


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Обработчик нажатий на инлайн-кнопки"""

    # Обработка кнопки "Назад"
    if call.data == "back_to_main":
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Выберите интересующий вас раздел:",
            reply_markup=get_main_keyboard(),
        )
        bot.answer_callback_query(call.id)
        return

    # Старт сценария "Примерка карьеры"
    if call.data == "career_tryon":
        chat_id = call.message.chat.id
        user_states[chat_id] = {"step": "waiting_photo", "photo_bytes": None}
        bot.send_message(chat_id, "Пришли мне своё фото (желательно чёткое, лицо крупным планом).")
        bot.answer_callback_query(call.id)
        return

    # Пользователь выбрал профессию
    if call.data.startswith("prof:"):
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

    # Разделы меню: резюме, собеседование, практика, трудоустройство, вопросы
    if call.data in message_map:
        send_section(chat_id=call.message.chat.id, section_key=call.data)
        bot.answer_callback_query(call.id)