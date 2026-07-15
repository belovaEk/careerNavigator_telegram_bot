import io
import os
import tempfile

from gradio_client import Client, handle_file


# Подключаемся к публичному Space с FLUX.1 Kontext (анонимно, без токена).
_client = Client("black-forest-labs/FLUX.1-Kontext-Dev")

# ключ -> (текст на кнопке, промпт для модели)
PROFESSIONS = {
    "doctor": ("Врач", "the same person wearing a white doctor's coat and stethoscope, "
                        "standing in a hospital room, keep the face and identity unchanged, photorealistic"),
    "pilot": ("Пилот", "the same person wearing a pilot uniform with cap, standing in an airplane cockpit, "
                        "keep the face and identity unchanged, photorealistic"),
    "chef": ("Повар", "the same person wearing a chef's white jacket and toque hat, standing in a professional kitchen, "
                       "keep the face and identity unchanged, photorealistic"),
    "developer": ("IT-специалист", "the same person wearing casual smart clothing, sitting at a desk with multiple monitors "
                                    "showing code, modern office, keep the face and identity unchanged, photorealistic"),
    "lawyer": ("Юрист", "the same person wearing a formal business suit, standing in a law office with bookshelves, "
                         "keep the face and identity unchanged, photorealistic"),
    "police": ("Полицейский", "the same person wearing a police uniform, standing outdoors near a patrol car, "
                               "keep the face and identity unchanged, photorealistic"),
}


def generate_career_image(photo_bytes: bytes, profession_key: str) -> io.BytesIO:
    """Отправляет фото пользователя в бесплатный Space и возвращает готовое изображение в буфере."""
    _label, prompt = PROFESSIONS[profession_key]

    # gradio_client ждёт путь к файлу на диске, а не сырые байты — поэтому сохраняем во временный файл
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(photo_bytes)
        tmp_path = tmp.name

    try:
        result, _seed = _client.predict(
            input_image=handle_file(tmp_path),
            prompt=prompt,
            seed=0,
            randomize_seed=True,
            guidance_scale=2.5,
            steps=28,
            api_name="/infer",
        )
    finally:
        os.remove(tmp_path)

    # В разных версиях gradio_client результат приходит либо словарём с полем "path",
    # либо сразу строкой — путём к скачанному локально файлу. Поддерживаем оба варианта.
    result_path = result["path"] if isinstance(result, dict) else result

    buffer = io.BytesIO()
    with open(result_path, "rb") as f:
        buffer.write(f.read())
    buffer.seek(0)
    return buffer