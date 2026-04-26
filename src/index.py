"""
Точка входа для Yandex Cloud Function.
Обрабатывает входящие webhook-запросы от Telegram.
"""
import json
import logging
import os
from typing import Dict, Any

from .telegram_api import send_message, send_typing_action, send_inline_keyboard, answer_callback_query
from .ai_router import get_ai_response
from .conversation_manager import get_conversation_history, add_to_conversation, get_system_prompt, clear_conversation
from .config import Config

# Настройка логирования для Yandex Cloud Functions
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Команды бота
COMMANDS = {
    "/start": "Приветствие и начало работы",
    "/help": "Справка по возможностям бота",
    "/clear": "Очистить историю диалога",
    "/daichi": "Информация о бренде Daichi",
    "/select_ai": "Выбор AI-модели (DeepSeek / YandexGPT)"
}


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Основной обработчик Yandex Cloud Function.
    
    Args:
        event: HTTP-запрос от API Gateway
        context: Контекст выполнения функции
    
    Returns:
        HTTP-ответ
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Получаем тело запроса
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        body = {}
    
    # Проверяем, что это сообщение от Telegram
    if 'message' not in body and 'callback_query' not in body:
        return {'statusCode': 200, 'body': 'OK'}
    
    # Обработка callback_query (нажатие inline-кнопок)
    if 'callback_query' in body:
        return handle_callback_query(body['callback_query'])
    
    # Обработка обычного сообщения
    message = body['message']
    chat_id = message['chat']['id']
    text = message.get('text', '').strip()
    
    # Обработка команд
    if text.startswith('/'):
        return handle_command(chat_id, text, message)
    
    # Обработка обычного текстового сообщения через AI
    return handle_text_message(chat_id, text)


def handle_command(chat_id: int, command: str, message: Dict[str, Any]) -> Dict[str, Any]:
    """Обработка команд бота."""
    logger.info(f"Command received: {command} from chat {chat_id}")
    
    if command == '/start':
        # Отправляем индикатор набора текста
        send_typing_action(chat_id)
        
        welcome_msg = """
🤖 *Добро пожаловать в «Ваш Консул»!*

Я — ваш профессиональный технико-коммерческий консультант по климатическому оборудованию.

*Что я умею:*
✅ Подбирать оборудование Daichi под ваши задачи
✅ Консультировать по техническим характеристикам
✅ Сравнивать модели разных линеек
✅ Давать коммерческие рекомендации
✅ Отвечать на вопросы по монтажу и эксплуатации

*Как задать вопрос:*
Просто напишите мне текстом! Например:
• "Подбери кондиционер для комнаты 25 кв.м."
• "Какая у Daichi Peak энергоэффективность?"
• "Что лучше для офиса 100 кв.м.?"

*Команды:*
/help — подробная справка
/daichi — информация о бренде Daichi
/clear — очистить историю диалога
/select_ai — выбрать AI-модель

*Специализация:*
Daichi — бытовые, полупромышленные и промышленные системы. Линейки Peak, Carbon, City Line, мульти-сплиты, кассетные и канальные блоки.

Чем могу помочь?
        """
        send_message(chat_id, welcome_msg)
        
    elif command == '/help':
        help_msg = """
📚 *Справка по боту «Ваш Консул»*

*Как использовать:*
Напишите боту вопрос на русском языке в свободной форме.

*Примеры вопросов:*
• "Подбери сплит-систему Daichi для дома 35 кв.м. с бюджетом до 50000 руб."
• "Какие модели Daichi работают на обогрев при -15°C?"
• "Технические характеристики Daichi Carbon 35"
• "Сравни Daichi Peak и Carbon"
• "Что выбрать для серверной комнаты?"

*Возможности AI:*
Бот использует DeepSeek (по умолчанию) или YandexGPT для генерации ответов с учётом контекста диалога.

*Команды:*
/start — начать диалог заново
/daichi — информация о бренде
/clear — очистить историю
/select_ai — сменить AI-провайдера
        """
        send_message(chat_id, help_msg)
        
    elif command == '/clear':
        clear_conversation(chat_id)
        send_message(chat_id, "✅ История диалога очищена! Можете задать новый вопрос.")
        
    elif command == '/daichi':
        daichi_info = """
🏭 *О бренде Daichi*

Daichi (Даичи) — российский бренд климатического оборудования на рынке с 2019 года.

*Продуктовые линейки:*
• *Peak* — бытовые настенные, энергоэффективность А++, работа от -15°C на обогрев
• *Carbon* — премиум-дизайн, ионизатор воздуха, уровень шума от 25 дБА
• *City Line* — полупромышленные канальные блоки
• *Мульти-сплит-системы* — для нескольких комнат
• *Кассетные и напольно-потолочные* — для офисов и больших помещений

*Особенности:*
• Инверторное управление на большинстве моделей
• Хладагент R-32 (экологичный)
• Зимние комплекты до -40°C для серверных
• Классы энергоэффективности А и А++
• Wi-Fi управление (опционально)

*Сайт:* www.daichi.ru
        """
        send_message(chat_id, daichi_info)
        
    elif command == '/select_ai':
        buttons = [
            {"text": "DeepSeek", "callback_data": "ai_deepseek"},
            {"text": "YandexGPT", "callback_data": "ai_yandexgpt"}
        ]
        send_inline_keyboard(chat_id, "Выберите AI-модель:", buttons)
        
    else:
        send_message(chat_id, "Неизвестная команда. Используйте /help для списка команд.")
    
    return {'statusCode': 200, 'body': 'OK'}


def handle_text_message(chat_id: int, text: str) -> Dict[str, Any]:
    """Обработка текстового сообщения через AI."""
    logger.info(f"Processing text message: {text[:50]}... from chat {chat_id}")
    
    # Отправляем индикатор набора текста
    send_typing_action(chat_id)
    
    # Получаем историю диалога
    history = get_conversation_history(chat_id)
    
    # Формируем список сообщений для AI
    messages = [{"role": "system", "content": get_system_prompt()}]
    
    # Добавляем историю (до 10 последних сообщений)
    for msg in history[-Config.MAX_HISTORY_MESSAGES*2:]:
        messages.append(msg)
    
    # Добавляем текущее сообщение
    messages.append({"role": "user", "content": text})
    
    # Получаем ответ от AI
    response, metadata = await get_ai_response(messages)
    
    # Сохраняем в историю
    add_to_conversation(chat_id, "user", text)
    add_to_conversation(chat_id, "assistant", response)
    
    # Отправляем ответ пользователю
    send_message(chat_id, response)
    
    # Логируем метаданные для мониторинга
    logger.info(f"AI response from {metadata.get('provider')}: success={metadata.get('success')}")
    
    return {'statusCode': 200, 'body': 'OK'}


def handle_callback_query(callback_query: Dict[str, Any]) -> Dict[str, Any]:
    """Обработка нажатий на inline-кнопки."""
    query_id = callback_query['id']
    chat_id = callback_query['message']['chat']['id']
    data = callback_query.get('data', '')
    
    if data == 'ai_deepseek':
        # Сохраняем выбор провайдера (можно расширить для постоянного хранения)
        response = "✅ Вы выбрали AI-модель *DeepSeek*.\n\nТеперь все вопросы будут обрабатываться с её использованием."
        answer_callback_query(query_id, "Выбран DeepSeek")
        send_message(chat_id, response)
        
    elif data == 'ai_yandexgpt':
        response = "✅ Вы выбрали AI-модель *YandexGPT*.\n\nТеперь все вопросы будут обрабатываться с её использованием."
        answer_callback_query(query_id, "Выбран YandexGPT")
        send_message(chat_id, response)
    
    return {'statusCode': 200, 'body': 'OK'}