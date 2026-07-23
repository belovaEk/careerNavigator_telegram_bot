import io
import os
import tempfile

from huggingface_hub import login
from gradio_client import Client, handle_file

from config import config

######################################################################
login(token=config.HF_TOKEN)
#######################################################################

_client = Client("black-forest-labs/FLUX.1-Kontext-Dev")

# ключ -> (текст на кнопке, промпт для модели)
PROFESSIONS = {
    "doctor": ("Врач", "This exact same person, wearing a white doctor's coat and a stethoscope around theneck, standing in a bright hospital room. The face, hairstyle, jawline, nose, eyes, and all facial features remain completely identical to the original person. Neutral expression. Photorealistic, 8k, sharp focus on face."),
    "pilot": ("Пилот", "This exact same person, wearing a pilot's uniform with shoulder epaulets and a peaked cap worn slightly back to show the full face, standing in an airplane cockpit. The face, hairstyle, jawline, nose, eyes, and all facial features remain completely identical to the original person. Neutral expression. Photorealistic, 8k, sharp focus on face."),
    "chef": ("Повар", "This exact same person, wearing a chef's white double-breasted jacket and a tall toque blanche hat, standing in a professional kitchen with stainless steel surfaces. The face, hairstyle, jawline, nose, eyes, and all facial features remain completely identical to the original person. Neutral expression. Photorealistic, 8k, sharp focus on face."),
    "developer": ("IT-специалист", "This exact same person, wearing smart casual clothing (a collared shirt or dark turtleneck), sitting at a desk with multiple monitors showing code, in a modern open-space office. The face, hairstyle, jawline, nose, eyes, and all facial features remain completely identical to the original person. Neutral expression. Photorealistic, 8k, sharp focus on face."),
    "lawyer": ("Юрист", "This exact same person, wearing a formal dark business suit with a tie, standing in a classic law office with wooden bookshelves. The face, hairstyle, jawline, nose, eyes, and all facial features remain completely identical to the original person. Neutral expression. Photorealistic, 8k, sharp focus on face."),
    "police": ("Полицейский", "This exact same person, wearing a dark blue police uniform with a badge on the chest and a peaked cap worn slightly back to show the full face, standing outdoors near a patrol car. The face, hairstyle, jawline, nose, eyes, and all facial features remain completely identical to the original person. Neutral expression. Photorealistic, 8k, sharp focus on face."),
}


def generate_career_image(photo_bytes: bytes, profession_key: str) -> io.BytesIO:
    """Отправляет фото пользователя в бесплатный Space и возвращает готовое изображение в буфере."""
    _label, prompt = PROFESSIONS[profession_key]

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

    result_path = result["path"] if isinstance(result, dict) else result

    buffer = io.BytesIO()
    with open(result_path, "rb") as f:
        buffer.write(f.read())
    buffer.seek(0)
    return buffer