import os
import httpx
from typing import Dict, Any, Optional

BASE_URL = f"https://api.telegram.org/bot{os.environ.get('BOT_TOKEN', '')}"

def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Универсальный вызов Telegram Bot API."""
    try:
        with httpx.Client() as client:
            resp = client.post(f"{BASE_URL}/{method}", json=kwargs, timeout=30.0)
            return resp.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def send_message(chat_id: int, text: str, reply_markup: Optional[Dict] = None, 
                 parse_mode: str = "HTML") -> Dict[str, Any]:
    """Отправка текстового сообщения."""
    params = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        params["reply_markup"] = reply_markup
    return _call("sendMessage", **params)

def send_typing_action(chat_id: int) -> Dict[str, Any]:
    """Отправка индикатора набора текста."""
    return _call("sendChatAction", chat_id=chat_id, action="typing")

def send_inline_keyboard(chat_id: int, text: str, buttons: list) -> Dict[str, Any]:
    """Отправка сообщения с Inline-клавиатурой."""
    reply_markup = {
        "inline_keyboard": [[{"text": btn["text"], "callback_data": btn["callback_data"]}] 
                           for btn in buttons]
    }
    return send_message(chat_id, text, reply_markup)

def answer_callback_query(callback_query_id: str, text: Optional[str] = None) -> Dict[str, Any]:
    """Ответ на callback-запрос от inline-кнопок."""
    params = {"callback_query_id": callback_query_id}
    if text:
        params["text"] = text
    return _call("answerCallbackQuery", **params)