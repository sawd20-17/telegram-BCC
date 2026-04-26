import os
from typing import List, Dict, Any
from . import deepseek_client, yandexgpt_client, knowledge_base
from .config import Config

async def get_ai_response(messages: List[Dict[str, str]], 
                          provider: str = None) -> tuple[str, Dict[str, Any]]:
    """
    Маршрутизация запроса к выбранному AI-провайдеру.
    
    Args:
        messages: Список сообщений диалога
        provider: deepseek / yandexgpt
    
    Returns:
        tuple: (ответ модели, метаданные о вызове)
    """
    provider = provider or Config.AI_PROVIDER
    metadata = {"provider": provider, "success": False}
    
    try:
        if provider == "deepseek":
            response = await deepseek_client.deepseek_chat_completion(
                messages, 
                temperature=Config.AI_TEMPERATURE,
                max_tokens=Config.AI_MAX_TOKENS
            )
            metadata["success"] = True
            return response, metadata
            
        elif provider == "yandexgpt":
            response = await yandexgpt_client.yandexgpt_chat_completion(
                messages,
                temperature=Config.AI_TEMPERATURE,
                max_tokens=Config.AI_MAX_TOKENS
            )
            metadata["success"] = True
            return response, metadata
            
        else:
            raise ValueError(f"Unknown AI provider: {provider}")
            
    except Exception as e:
        metadata["error"] = str(e)
        return _get_fallback_response(), metadata

def _get_fallback_response() -> str:
    """Ответ при недоступности AI-сервисов."""
    return """
⚠️ *Временно недоступен AI-модуль*

Приношу извинения за временные неполадки. Вы можете:

1. Обратиться к официальному сайту Daichi: www.daichi.ru
2. Связаться со службой поддержки Daichi
3. Написать вопрос позже — я обязательно отвечу

Для срочных консультаций по подбору оборудования:
- Общая информация Daichi: 8-800-555-XX-XX
- Техническая поддержка: support@daichi.ru
"""