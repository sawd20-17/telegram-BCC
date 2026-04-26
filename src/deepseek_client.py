import os
import httpx
import json
from typing import List, Dict, Any

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

async def deepseek_chat_completion(messages: List[Dict[str, str]], 
                                    temperature: float = 0.3,
                                    max_tokens: int = 2000) -> str:
    """
    Вызов DeepSeek API для чат-комплетаций.
    
    Args:
        messages: Список сообщений в формате [{"role": "system/user/assistant", "content": "..."}]
        temperature: Температура генерации (0-1)
        max_tokens: Максимальное количество токенов в ответе
    
    Returns:
        Ответ от модели
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            DEEPSEEK_API_URL, 
            headers=headers, 
            json=payload, 
            timeout=60.0
        )
        
        if response.status_code != 200:
            raise Exception(f"DeepSeek API error: {response.status_code} - {response.text}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"]