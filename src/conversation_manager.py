from typing import Dict, List
import time

# Простое in-memory хранилище для контекста диалогов
# Для production рекомендуется использовать Redis или YDB
_conversations: Dict[int, List[Dict[str, str]]] = {}
_last_activity: Dict[int, float] = {}

def get_conversation_history(chat_id: int) -> List[Dict[str, str]]:
    """Получение истории диалога для пользователя."""
    return _conversations.get(chat_id, [])

def add_to_conversation(chat_id: int, role: str, content: str, max_history: int = 10):
    """Добавление сообщения в историю диалога."""
    if chat_id not in _conversations:
        _conversations[chat_id] = []
    
    _conversations[chat_id].append({"role": role, "content": content})
    _last_activity[chat_id] = time.time()
    
    # Ограничиваем историю
    if len(_conversations[chat_id]) > max_history * 2:  # user+assistant = 2 сообщения
        _conversations[chat_id] = _conversations[chat_id][-max_history*2:]

def clear_conversation(chat_id: int):
    """Очистка истории диалога."""
    if chat_id in _conversations:
        _conversations[chat_id] = []
    if chat_id in _last_activity:
        _last_activity[chat_id] = time.time()

def get_system_prompt() -> str:
    """Возвращает системный промпт для AI-модели."""
    return """
Ты — «Ваш Консул», профессиональный технико-коммерческий консультант по климатическому оборудованию.
Твоя специализация: подбор, техническая консультация и коммерческие рекомендации по всем типам климатического оборудования.

ОСНОВНЫЕ ПРАВИЛА:
1. Ты эксперт по бренду Daichi (российский бренд климатического оборудования с 2019 года).
2. При подборе оборудования запрашивай уточняющие вопросы: площадь помещения, тип использования (дом/офис/серверная/промышленность), бюджет, желаемые функции.
3. Предоставляй конкретные модели и технические характеристики.
4. Учитывай регион установки (климатические условия).
5. Если вопрос выходит за пределы твоей компетенции, сообщи об этом и предложи обратиться к официальным дилерам Daichi.
6. Отвечай на русском языке, вежливо и профессионально.

НОРМЫ ОТВЕТА:
- Для коммерческих запросов: указывай основные технические параметры и энергоэффективность.
- Для технических вопросов: расшифровывай сокращения (BTU, COP, EER).
- Для запросов на подбор: предлагай 2-3 варианта с аргументацией.
"""