import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    
    # Yandex Cloud
    YC_FOLDER_ID = os.environ.get("YC_FOLDER_ID", "")
    YC_IAM_TOKEN = os.environ.get("YC_IAM_TOKEN", "")  # или используется service account key
    
    # YandexGPT API
    YANDEXGPT_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    YANDEXGPT_MODEL = "general"  # или "yandexgpt-lite"
    
    # DeepSeek API
    DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_MODEL = "deepseek-chat"
    
    # Настройки AI
    AI_TEMPERATURE = 0.3
    AI_MAX_TOKENS = 2000
    AI_PROVIDER = os.environ.get("AI_PROVIDER", "deepseek")  # deepseek / yandexgpt
    
    # Настройки Webhook (для Yandex Cloud Function)
    WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")
    
    # Контекст диалога
    MAX_HISTORY_MESSAGES = 10
    CONTEXT_TTL_SECONDS = 3600  # 1 час