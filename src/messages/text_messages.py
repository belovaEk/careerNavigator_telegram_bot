from dataclasses import dataclass

@dataclass
class Messages:
    """Класс для хранения текстов сообщений"""
    
    @staticmethod
    def welcome(name: str) -> str:
        return f"""<b>{name}</b>, привет! 👋

Я твой личный карьерный ассистент в Социальном казначействе.

Давай превратим твою учебу в первую работу.
Выбери, чем займемся сегодня:"""
    
    @staticmethod
    def resume() -> str:
        return """📄 **Резюме** бла бла"""
    
    @staticmethod
    def interview() -> str:
        return """🎯 **Собеседование**"""
    
    @staticmethod
    def practice() -> str:
        return """💼 **Практика**"""
    
    @staticmethod
    def employment() -> str:
        return """🏢 **Трудоустройство**"""
    
    @staticmethod
    def questions() -> str:
        return """❓ **Вопросы и обратная связь**"""
    
    @staticmethod
    def back_to_main() -> str:
        return "🔙 Возвращаемся в главное меню. Выберите интересующий вас раздел:"

# Создаём экземпляр для удобного импорта
messages = Messages()