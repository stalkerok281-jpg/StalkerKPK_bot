import asyncio
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ChatMemberUpdated
from aiogram.utils.markdown import bold

# ==================== НАСТРОЙКИ ====================
TOKEN = "7657570493:AAFqKUxdGQIcLRMGEkenDKaciqOoYv7K1QI"  # Замените на токен вашего бота

# Интервалы отправки (в секундах)
DEATH_MIN_INTERVAL = 8 * 60 * 60      # 8 часов между смертями
DEATH_MAX_INTERVAL = 24 * 60 * 60     # 24 часа между смертями
EMISSION_INTERVAL = 48 * 60 * 60      # 48 часов между выбросами

# Вероятность выброса в момент отправки (10%)
EMISSION_PROBABILITY = 0.1

# Настройки логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище активных чатов
active_chats: Dict[int, Dict] = {}

# ==================== ДАННЫЕ ДЛЯ ГЕНЕРАЦИИ ====================
# Имена сталкеров
STALKER_NAMES = [
    "Валик", "Лис", "Шустрый", "Кузьма", "Скелет", "Борода", "Веном",
    "Призрак", "Махно", "Филин", "Грей", "Клещ", "Шрам", "Волк",
    "Лед", "Малыш", "Профессор", "Сыч", "Лысый", "Рыжий", "Химик",
    "Док", "Варяг", "Гвоздь", "Студент", "Шахтер", "Фантом", "Монгол"
]

# Клички (прозвища)
STALKER_NICKNAMES = [
    "Снайпер", "Буйный", "Тихий", "Гром", "Косой", "Бродяга", "Ворон",
    "Седой", "Рваный", "Хромой", "Шептун", "Долговязый", "Пулеметчик",
    "Злой", "Добряк", "Кошатник", "Гитарист", "Барыга", "Сапер",
    "Кузнец", "Шахтер", "Медведь", "Лиса", "Шакал", "Барсук"
]

# Причины смерти
DEATH_REASONS = [
    "воронка", "аномалия 'трамплин'", "аномалия 'жарка'", "аномалия 'карусель'",
    "кровосос", "бюрер", "псевдогигант", "снорк", "кабан", "плоть",
    "слепой пес", "контролер", "полтергейст", "химера", "псевдособака",
    "бандюки", "долг", "свобода", "монолит", "наемники", "зомби",
    "выброс", "радиация", "голод", "мутанты", "мародеры"
]

# Локации
LOCATIONS = [
    "Кордон", "Свалка", "Темная долина", "Агропром", "Янтарь",
    "Болота", "Бар", "Радар", "ЧАЭС", "Припять", "Затон",
    "Юпитер", "ЗАТО Янтарь", "Лиманск", "Красный лес", "Мертвый город",
    "Рыжий лес", "Армейские склады", "Дикая территория"
]

# ==================== ФУНКЦИИ ГЕНЕРАЦИИ ====================
def generate_death_message() -> str:
    """Генерирует сообщение о смерти сталкера"""
    name = random.choice(STALKER_NAMES)
    nickname = random.choice(STALKER_NICKNAMES)
    location = random.choice(LOCATIONS)
    reason = random.choice(DEATH_REASONS)
    
    templates = [
        f"⚠️ Погиб сталкер {name} '{nickname}', {location}, {reason}.",
        f"💀 Сталкер {name} {nickname} мертв, {location}, {reason}.",
        f"☠️ Не вернулся с ходки {name} '{nickname}', {location}, {reason}.",
        f"⚰️ Похоронили сталкера {name} '{nickname}', {location}, причина смерти: {reason}.",
        f"📻 Внимание! {name} '{nickname}' погиб в {location}, {reason}."
    ]
    
    return random.choice(templates)

def generate_emission_sequence() -> List[str]:
    """Генерирует серию сообщений о выбросе"""
    locations = [
        "Кордон", "Свалка", "Темная долина", "Агропром", "Янтарь",
        "Бар", "Радар", "ЧАЭС", "Припять", "Затон", "Юпитер"
    ]
    target_location = random.choice(locations)
    
    return [
        "⚠️ ВНИМАНИЕ! ЗАРЕГИСТРИРОВАНА СЕЙСМИЧЕСКАЯ АКТИВНОСТЬ!",
        f"🌪️ По данным экологов, в районе {target_location} начинается выброс!",
        "🏃 Срочно укрыться в ближайшем убежище! Повторяю, всем укрыться!",
        "📡 Прогнозируемая мощность: {} МЭр. Берегите себя, сталкеры!".format(random.randint(3, 7)),
        "⏱️ До прихода волны: {} минут".format(random.randint(5, 15))
    ]

def get_next_death_time() -> int:
    """Возвращает случайный интервал до следующей смерти в секундах"""
    return random.randint(DEATH_MIN_INTERVAL, DEATH_MAX_INTERVAL)

def get_next_emission_time() -> int:
    """Возвращает интервал до следующего выброса (фиксированный 48ч)"""
    return EMISSION_INTERVAL

# ==================== ОБРАБОТЧИКИ СОБЫТИЙ ====================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    chat_id = message.chat.id
    chat_name = message.chat.title or f"чат {chat_id}"
    
    # Добавляем чат в активные
    if chat_id not in active_chats:
        active_chats[chat_id] = {
            'name': chat_name,
            'added_date': datetime.now(),
            'message_count': 0
        }
        logger.info(f"Чат добавлен: {chat_name} (ID: {chat_id})")
    
    await message.answer(
        "👋 Сталкер, добро пожаловать в Единую сталкерскую сеть!\n\n"
        "Я буду присылать сводки о происшествиях в Зоне.\n"
        "Команды:\n"
        "/status - статус сети\n"
        "/test_death - тестовая смерть\n"
        "/test_emission - тестовый выброс\n"
        "/chats - список активных чатов"
    )

@dp.message(Command("status"))
async def cmd_status(message: Message):
    """Обработчик команды /status"""
    chat_id = message.chat.id
    
    if chat_id not in active_chats:
        active_chats[chat_id] = {
            'name': message.chat.title or f"чат {chat_id}",
            'added_date': datetime.now(),
            'message_count': 0
        }
    
    chat_info = active_chats[chat_id]
    
    await message.answer(
        f"📡 Единая сталкерская сеть активна\n"
        f"🟢 Связь с Зоной устойчивая\n"
        f"📊 Режим: автоматическая рассылка\n"
        f"👥 Активных чатов: {len(active_chats)}\n"
        f"📨 Отправлено сообщений: {chat_info['message_count']}"
    )

@dp.message(Command("chats"))
async def cmd_chats(message: Message):
    """Показывает список активных чатов"""
    if not active_chats:
        await message.answer("❌ Нет активных чатов")
        return
    
    chats_list = "\n".join([
        f"• {info['name']} (ID: {chat_id}) - {info['message_count']} сообщ."
        for chat_id, info in active_chats.items()
    ])
    
    await message.answer(f"📋 Активные чаты:\n{chats_list}")

@dp.message(Command("test_death"))
async def cmd_test_death(message: Message):
    """Тестовая отправка сообщения о смерти"""
    await message.answer(generate_death_message())
    
    # Обновляем счетчик
    if message.chat.id in active_chats:
        active_chats[message.chat.id]['message_count'] += 1

@dp.message(Command("test_emission"))
async def cmd_test_emission(message: Message):
    """Тестовая отправка серии сообщений о выбросе"""
    for msg in generate_emission_sequence():
        await message.answer(msg)
        await asyncio.sleep(2)  # Пауза между сообщениями
    
    # Обновляем счетчик
    if message.chat.id in active_chats:
        active_chats[message.chat.id]['message_count'] += len(generate_emission_sequence())

@dp.message(Command("stop"))
async def cmd_stop(message: Message):
    """Остановка рассылки в текущем чате"""
    chat_id = message.chat.id
    if chat_id in active_chats:
        del active_chats[chat_id]
        await message.answer("🛑 Рассылка остановлена в этом чате")
        logger.info(f"Чат удален из рассылки: {chat_id}")
    else:
        await message.answer("❓ Этот чат не был в списке рассылки")

@dp.message()
async def handle_any_message(message: Message):
    """Обработчик любого сообщения - автоматически добавляет чат"""
    chat_id = message.chat.id
    
    # Добавляем чат в активные, если его там нет
    if chat_id not in active_chats:
        active_chats[chat_id] = {
            'name': message.chat.title or f"чат {chat_id}",
            'added_date': datetime.now(),
            'message_count': 0
        }
        logger.info(f"Чат автоматически добавлен: {message.chat.title} (ID: {chat_id})")
        
        # Отправляем приветственное сообщение (только при первом добавлении)
        await message.answer(
            "👋 Приветствую, сталкер! Этот чат добавлен в Единую сталкерскую сеть.\n"
            "Я буду присылать сводки о происшествиях в Зоне.\n"
            "Используй /start для получения информации."
        )

# ==================== ФОНОВЫЕ ЗАДАЧИ ====================
async def death_scheduler():
    """Планировщик отправки сообщений о смерти"""
    while True:
        try:
            if not active_chats:
                logger.info("Нет активных чатов, ждем...")
                await asyncio.sleep(60)
                continue
            
            # Ждем случайное время до следующей смерти
            wait_time = get_next_death_time()
            next_death = datetime.now() + timedelta(seconds=wait_time)
            logger.info(f"Следующая смерть запланирована на {next_death.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"Активных чатов: {len(active_chats)}")
            
            await asyncio.sleep(wait_time)
            
            # Генерируем сообщение
            death_msg = generate_death_message()
            
            # Отправляем во все активные чаты
            for chat_id in list(active_chats.keys()):
                try:
                    await bot.send_message(chat_id, death_msg)
                    active_chats[chat_id]['message_count'] += 1
                    logger.info(f"Отправлено сообщение о смерти в чат {chat_id}")
                except Exception as e:
                    logger.error(f"Ошибка отправки в чат {chat_id}: {e}")
                    # Если бот заблокирован или удален из чата - удаляем из списка
                    if "Forbidden" in str(e) or "chat not found" in str(e):
                        logger.info(f"Удаляем чат {chat_id} из активных (бот удален)")
                        active_chats.pop(chat_id, None)
            
            # С вероятностью 10% отправляем выброс
            if random.random() < EMISSION_PROBABILITY:
                logger.info("Инициируем выброс...")
                await asyncio.sleep(random.randint(30, 300))  # Пауза 30сек-5мин
                
                emission_msgs = generate_emission_sequence()
                for msg in emission_msgs:
                    for chat_id in list(active_chats.keys()):
                        try:
                            await bot.send_message(chat_id, msg)
                            active_chats[chat_id]['message_count'] += 1
                        except Exception as e:
                            logger.error(f"Ошибка отправки выброса в чат {chat_id}: {e}")
                            if "Forbidden" in str(e) or "chat not found" in str(e):
                                active_chats.pop(chat_id, None)
                    await asyncio.sleep(random.randint(30, 120))  # Пауза между сообщениями
                logger.info("Серия сообщений о выбросе отправлена")
                
        except Exception as e:
            logger.error(f"Ошибка в death_scheduler: {e}")
            await asyncio.sleep(60)

async def emission_scheduler():
    """Планировщик отправки выбросов (раз в 2 дня)"""
    while True:
        try:
            if not active_chats:
                logger.info("Нет активных чатов, ждем...")
                await asyncio.sleep(60)
                continue
            
            # Ждем 48 часов до следующего выброса
            wait_time = get_next_emission_time()
            next_emission = datetime.now() + timedelta(seconds=wait_time)
            logger.info(f"Следующий плановый выброс запланирован на {next_emission.strftime('%Y-%m-%d %H:%M:%S')}")
            
            await asyncio.sleep(wait_time)
            
            # Отправляем серию сообщений о выбросе
            logger.info("Начинаем плановый выброс...")
            emission_msgs = generate_emission_sequence()
            
            for msg in emission_msgs:
                for chat_id in list(active_chats.keys()):
                    try:
                        await bot.send_message(chat_id, msg)
                        active_chats[chat_id]['message_count'] += 1
                    except Exception as e:
                        logger.error(f"Ошибка отправки выброса в чат {chat_id}: {e}")
                        if "Forbidden" in str(e) or "chat not found" in str(e):
                            active_chats.pop(chat_id, None)
                await asyncio.sleep(random.randint(45, 180))  # Пауза между сообщениями
            
            logger.info("Плановый выброс завершен")
            
        except Exception as e:
            logger.error(f"Ошибка в emission_scheduler: {e}")
            await asyncio.sleep(60)

# ==================== ЗАПУСК БОТА ====================
async def main():
    """Главная функция запуска"""
    logger.info("Бот Единой сталкерской сети запускается...")
    logger.info("Ожидание добавления в чаты...")
    
    # Запускаем планировщики как фоновые задачи
    asyncio.create_task(death_scheduler())
    asyncio.create_task(emission_scheduler())
    
    # Запускаем поллинг
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

