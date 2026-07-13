from bot import bot
from keyboards.inline_keyboards import get_main_keyboard, get_back_keyboard
from messages.text_messages import messages

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