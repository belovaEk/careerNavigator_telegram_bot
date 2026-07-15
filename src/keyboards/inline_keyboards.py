from telebot import types


def get_main_keyboard():
    """Главная клавиатура с кнопками"""
    markup = types.InlineKeyboardMarkup(row_width=2)

    button_resume = types.InlineKeyboardButton(
        text='📄 Резюме',
        callback_data='resume'
    )
    button_interview = types.InlineKeyboardButton(
        text='🎯 Собеседование',
        callback_data='interview'
    )
    button_practice = types.InlineKeyboardButton(
        text='💼 Практика',
        callback_data='practice'
    )
    button_employment = types.InlineKeyboardButton(
        text='🏢 Трудоустройство',
        callback_data='employment'
    )
    button_questions = types.InlineKeyboardButton(
        text='❓ Вопросы',
        callback_data='questions'
    )

    button_career_tryon = types.InlineKeyboardButton(
        text='🎭 Примерка карьеры',
        callback_data='career_tryon'
    )

    markup.add(
        button_resume,
        button_interview,
        button_practice,
        button_employment,
        button_questions
    )

    markup.add(button_career_tryon)

    return markup


def get_back_keyboard():
    """Клавиатура с кнопкой 'Назад'"""
    markup = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton(
        text='🔙 Назад',
        callback_data='back_to_main'
    )
    markup.add(back_button)
    return markup



def get_professions_keyboard():
    """Клавиатура со списком профессий для примерки"""
    from services.image_generator import PROFESSIONS

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text=label, callback_data=f"prof:{key}")
        for key, (label, _prompt) in PROFESSIONS.items()
    ]
    markup.add(*buttons)
    return markup