import os
import logging

from dotenv import load_dotenv
from groq import Groq
from docx import Document
from pypdf import PdfReader

load_dotenv()

logger = logging.getLogger(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DOCUMENTS_DIR = os.path.join("assets", "documents")

# Все файлы, из которых модель должна черпать знания при ответе на вопросы.
# Список независим от SECTION_ASSETS в callback_query.py — это отдельная,
# полная база знаний для свободных вопросов пользователя.
KNOWLEDGE_FILES = [
    "resume_template.docx",
    "resume_recommendations.docx",
    "interview_recommendations.docx",
    "practice_recommendations.docx",
    "application_form.docx",
    "about_company.pdf",
    "employment_docs_list.pdf",
]


def _extract_docx_text(path: str) -> str:
    document = Document(path)
    return "\n".join(p.text for p in document.paragraphs if p.text.strip())


def _extract_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _load_knowledge_base() -> str:
    """Извлекает текст из всех файлов один раз и склеивает в единую базу знаний."""
    parts = []
    for filename in KNOWLEDGE_FILES:
        path = os.path.join(DOCUMENTS_DIR, filename)
        try:
            if filename.endswith(".docx"):
                text = _extract_docx_text(path)
            elif filename.endswith(".pdf"):
                text = _extract_pdf_text(path)
            else:
                continue
            parts.append(f"### Документ: {filename}\n{text}")
        except FileNotFoundError:
            logger.warning(f"Файл базы знаний не найден: {path}")
            continue

    return "\n\n".join(parts)


# Текст документов извлекается один раз при импорте модуля (то есть при старте бота),
# а не при каждом вопросе пользователя — это и есть избежание лишних затрат ресурсов
# на парсинг файлов. Сам текст переиспользуется во всех последующих запросах.
KNOWLEDGE_BASE = _load_knowledge_base()

SYSTEM_PROMPT = f"""Ты — ИИ-ассистент, встроенный в Telegram-бота для студентов, которые хотят пройти стажировку и трудоустроиться в Социальное казначейство.

Твоя задача — отвечать на вопросы пользователей бота, опираясь только на информацию из документов ниже: про резюме, собеседование, практику и трудоустройство.

Правила ответа:
- Отвечай вежливо, дружелюбно и по делу, обращайся на "ты".
- Используй только факты из документов ниже. Если ответа в документах нет — честно скажи, что не располагаешь такой информацией, и предложи обратиться к кадровой службе через раздел "Вопросы и обратная связь".
- Не придумывай факты, которых нет в документах.
- Пиши обычным текстом, без Markdown-разметки (никаких *, **, _, #, `) и без эмодзи — в этом канале они не форматируются корректно.
- Отвечай по существу, без лишних вступлений и повторов вопроса пользователя.
- Если спросят кто ты, то ты ИИ-ассистент от Социального казначейства города Москвы.
- После каждого сообщения можешь предлагать воспользоваться встроенным меню для работы с ботом или продолжить диалог здесь
- Ты можешь писать немного вольнее, если вопрос пользователя распологает к шутливому дружескому диалогу

Документы:
{KNOWLEDGE_BASE}"""


def response_func(user_message: str) -> str | None:
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": str(user_message)},
        ],
        model="openai/gpt-oss-120b",
    )
    return chat_completion.choices[0].message.content