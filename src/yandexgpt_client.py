import os
import httpx
import json
from typing import List, Dict, Any

YC_FOLDER_ID = os.environ.get("YC_FOLDER_ID", "")
YC_IAM_TOKEN = os.environ.get("YC_IAM_TOKEN", "")
YANDEXGPT_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

async def yandexgpt_chat_completion(messages: List[Dict[str, str]], 
                                     temperature: float = 0.3,
                                     max_tokens: int = 2000) -> str:
    """
    Вызов YandexGPT API для чат-комплетаций.
    
    YandexGPT использует другой формат запроса: требуется конкатенация всей истории
    в поле instructionText (system) + requestText (user).
    """
    # Формируем системный промпт и историю
    system_prompt = next((m["content"] for m in messages if m["role"] == "system"), "")
    user_messages = [m["content"] for m in messages if m["role"] == "user"]
    assistant_messages = [m["content"] for m in messages if m["role"] == "assistant"]
    
    # Конкатенируем историю диалога
    full_history = ""
    for i in range(max(len(user_messages), len(assistant_messages))):
        if i < len(user_messages):
            full_history += f"User: {user_messages[i]}\n"
        if i < len(assistant_messages):
            full_history += f"Assistant: {assistant_messages[i]}\n"
    
    headers = {
        "Authorization": f"Bearer {YC_IAM_TOKEN}",
        "Content-Type": "application/json",
        "x-folder-id": YC_FOLDER_ID
    }
    
    payload = {
        "modelUri": f"gpt://{YC_FOLDER_ID}/yandexgpt-lite/latest",
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
            "maxTokens": max_tokens
        },
        "messages": [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": full_history + "\nUser: " + (user_messages[-1] if user_messages else "")}
        ]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            YANDEXGPT_API_URL,
            headers=headers,
            json=payload,
            timeout=60.0
        )
        
        if response.status_code != 200:
            raise Exception(f"YandexGPT API error: {response.status_code} - {response.text}")
        
        result = response.json()
        return result["result"]["alternatives"][0]["message"]["text"]