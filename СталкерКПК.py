import asyncio
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# ==================== НАСТРОЙКИ ====================
TOKEN = "7657570493:AAFqKUxdGQIcLRMGEkenDKaciqOoYv7K1QI"  # Замените на токен вашего бота

# Интервалы отправки (в секундах)
DEATH_MIN_INTERVAL = 8 * 60 * 60      # 8 часов между смертями
DEATH_MAX_INTERVAL = 24 * 60 * 60     # 24 часа между смертями
EMISSION_INTERVAL = 48 * 60 * 60      # 48 часов между выбросами
ARTIFACT_INTERVAL = 4 * 60 * 60       # 4 часа между находками артефактов
QUEST_INTERVAL = 12 * 60 * 60         # 12 часов между квестами
GUIDE_INTERVAL = 6 * 60 * 60          # 6 часов между предложениями проводников

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
    "Док", "Варяг", "Гвоздь", "Студент", "Шахтер", "Фантом", "Монгол",
    "Боцман", "Шептун", "Гоблин", "Кубик", "Псих", "Фикс"
]

# Клички (прозвища)
STALKER_NICKNAMES = [
    "Снайпер", "Буйный", "Тихий", "Гром", "Косой", "Бродяга", "Ворон",
    "Седой", "Рваный", "Хромой", "Шептун", "Долговязый", "Пулеметчик",
    "Злой", "Добряк", "Кошатник", "Гитарист", "Барыга", "Сапер",
    "Кузнец", "Шахтер", "Медведь", "Лиса", "Шакал", "Барсук",
    "Волкодав", "Гладиатор", "Клык", "Коготь", "Вихрь"
]

# Группировки
FACTIONS = ["сталкер", "бандит", "военный", "наемник", "монолит", "долг", "свобода", "эколог"]

# Причины смерти
DEATH_REASONS = [
    "воронка", "аномалия трамплин", "аномалия жарка", "аномалия карусель",
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

# Артефакты
ARTIFACTS = [
    "Медуза", "Грави", "Пузырь", "Каменный цветок", "Слизень",
    "Коготь", "Глаз", "Золотая рыбка", "Ночная звезда", "Капля",
    "Лунный свет", "Выверт", "Кровь камня", "Душа", "Плоть",
    "Щупальце", "Пленка", "Ведьмино желе", "Бенгальский огонь", "Морской еж"
]

# Задания и квесты
QUESTS = [
    "Принести артефакт Медуза с Темной долины. Награда: 5000 RU",
    "Зачистить подземелья Агропрома от мутантов. Награда: 8000 RU",
    "Найти пропавшую группу сталкеров на Янтаре. Награда: 3000 RU",
    "Сопроводить ученого до Янтаря. Награда: 10000 RU",
    "Уничтожить банду на Свалке. Награда: 7000 RU",
    "Доставить детектор на Кордон. Награда: 2000 RU",
    "Разведать обстановку на Радаре. Награда: 15000 RU",
    "Найти и доставить артефакт Коготь. Награда: 12000 RU",
    "Устранить контролера в подземельях. Награда: 20000 RU",
    "Собрать образцы крови мутантов. Награда: 6000 RU"
]

# Предложения проводников
GUIDE_OFFERS = [
    "Проведу до Бара. Цена: 3000 RU",
    "Группа на Янтарь, нужен еще один. Место сбора: Кордон",
    "Иду на Радар, нужны попутчики. Оплата: проводка бесплатно",
    "Срочно нужен проводник до ЧАЭС. Оплата: артефакт",
    "Провожу до Лиманска. Знаю безопасный путь",
    "Ищем опытного проводника на Юпитер. Оплата 5000 + хабар",
    "На Армейские склады, идем завтра утром. Два места",
    "Провожу группу через Выжигатель мозгов. Нужны добровольцы",
    "На Припять, выдвигаемся через час. Снаряжение при себе",
    "В Темную долину, плата 2000. Гарантирую безопасность"
]

# ==================== ФУНКЦИИ ГЕНЕРАЦИИ ====================
def generate_death_message() -> str:
    """Генерирует сообщение о смерти сталкера"""
    name = random.choice(STALKER_NAMES)
    nickname = random.choice(STALKER_NICKNAMES)
    faction = random.choice(FACTIONS)
    location = random.choice(LOCATIONS)
    reason = random.choice(DEATH_REASONS)
    
    templates = [
        f"Погиб {faction} {name} '{nickname}', {location}, {reason}.",
        f"{faction} {name} {nickname} мертв, {location}, {reason}.",
        f"Не вернулся с ходки {faction} {name} '{nickname}', {location}, {reason}.",
        f"Похоронили {faction} {name} '{nickname}', {location}, причина смерти: {reason}.",
        f"Внимание! {faction} {name} '{nickname}' погиб в {location}, {reason}."
    ]
    
    return random.choice(templates)

def generate_emission_sequence() -> List[str]:
    """Генерирует серию сообщений о выбросе"""
    minutes = random.randint(5, 15)
    power = random.randint(3, 7)
    
    return [
        f"ВНИМАНИЕ! ЗАРЕГИСТРИРОВАНА СЕЙСМИЧЕСКАЯ АКТИВНОСТЬ!",
        f"Прогнозируется выброс! Мощность: {power} МЭр",
        f"Срочно укрыться в ближайшем убежище! Повторяю, всем укрыться!",
        f"До прихода волны: {minutes} минут. Берегите себя, сталкеры!"
    ], minutes

def generate_emission_start(minutes_passed: int) -> str:
    """Генерирует сообщение о начале выброса"""
    templates = [
        f"ВЫБРОС НАЧАЛСЯ! Волна накрыла Зону через {minutes_passed} минут после предупреждения!",
        f"Начало выброса! Зона содрогается, мощность зашкаливает!",
        f"Выброс! Всем сидеть в укрытиях! Повторяю - выброс начался!",
        f"Зона просыпается! Выброс достиг поверхности!"
    ]
    return random.choice(templates)

def generate_emission_end() -> str:
    """Генерирует сообщение о конце выброса"""
    templates = [
        f"Выброс закончился. Можно выходить из укрытий, но будьте осторожны - аномалии активизировались.",
        f"Выброс завершен. Зона успокаивается. Много погибших...",
        f"Отбой выброса. Осторожно - возможны новые аномалии на старых местах.",
        f"Выброс прошел. Кто выжил - выходите, Зона снова ждет сталкеров."
    ]
    return random.choice(templates)

def generate_artifact_message() -> str:
    """Генерирует сообщение о находке артефакта (от первого или третьего лица)"""
    name = random.choice(STALKER_NAMES)
    nickname = random.choice(STALKER_NICKNAMES)
    faction = random.choice(FACTIONS)
    artifact = random.choice(ARTIFACTS)
    location = random.choice(LOCATIONS)
    price = random.randint(3, 15) * 1000
    
    # 50% шанс на первое лицо
    if random.random() < 0.5:
        templates = [
            f"{faction} {name} '{nickname}': Нашел артефакт '{artifact}' в {location}. Продаю за {price} RU",
            f"{faction} {name} {nickname}: Есть артефакт '{artifact}' с {location}. Цена {price} RU, торг уместен",
            f"{faction} {name} '{nickname}': Толкну '{artifact}' за {price}. Сам нашел в {location}",
            f"Свежий артефакт! {faction} {name} '{nickname}': {artifact}, {location}. Отдам за {price}"
        ]
    else:
        templates = [
            f"{faction} {name} '{nickname}' нашел артефакт '{artifact}' в {location}. Продает за {price} RU",
            f"Свежий артефакт! {faction} {name} {nickname} нашел '{artifact}' в {location}. Торг уместен",
            f"Внимание! В {location} найден артефакт '{artifact}'. Обращаться к {faction} {name} '{nickname}'",
            f"{faction} {name} '{nickname}' продает редкий артефакт '{artifact}', найденный в {location}. Цена: {price} RU"
        ]
    
    return random.choice(templates)

def generate_quest_message() -> str:
    """Генерирует сообщение с заданием (от первого или третьего лица)"""
    quest = random.choice(QUESTS)
    customer = random.choice(["ученый", "торговец", "сталкер", "бандит", "военный"])
    customer_name = random.choice(STALKER_NAMES)
    customer_nick = random.choice(STALKER_NICKNAMES)
    
    # 40% шанс на первое лицо
    if random.random() < 0.4:
        templates = [
            f"{customer} {customer_name} '{customer_nick}': Ищу сталкеров для задания. {quest}",
            f"{customer} {customer_name} {customer_nick}: Срочно нужны люди. {quest}",
            f"{customer} {customer_name} '{customer_nick}': Оплачу выполнение. {quest}",
            f"Сам {customer} {customer_name} дает задание: {quest}"
        ]
    else:
        templates = [
            f"Задание от {customer} {customer_name} '{customer_nick}': {quest}",
            f"Срочное задание ({customer} {customer_name}): {quest}",
            f"Внимание сталкеры! {customer} {customer_name} '{customer_nick}' дает задание: {quest}",
            f"Доска объявлений ({customer} {customer_name} {customer_nick}): {quest}"
        ]
    
    return random.choice(templates)

def generate_guide_message() -> str:
    """Генерирует предложение проводника (от первого или третьего лица)"""
    offer = random.choice(GUIDE_OFFERS)
    guide_name = random.choice(STALKER_NAMES)
    guide_nick = random.choice(STALKER_NICKNAMES)
    
    # 70% шанс на первое лицо (проводники чаще пишут сами)
    if random.random() < 0.7:
        return f"Проводник {guide_name} '{guide_nick}': {offer}"
    else:
        return f"Предложение от проводника {guide_name} '{guide_nick}': {offer}"

def generate_random_message() -> str:
    """Генерирует случайное атмосферное сообщение"""
    messages = [
        "На базе слышна гитара... Кто-то поет про Зону.",
        "Приехал торговец с свежим хлебом. Будьте вежливы.",
        "Аномальная активность сегодня выше обычного.",
        "Говорят, в полнолуние мутанты особенно злые.",
        "У Сидоровича свежий кофе. Заходите погреться.",
        "Сталкерское радио передает музыку прошлого.",
        "В баре идет игра в покер. Кто смелый?",
        "Аптечки закончились у торговца. Будьте осторожны в ходке.",
        "Кто-то потерял фонарь на Кордоне. Спросите у Сидоровича.",
        "Слепые псы сегодня особенно активны. Держитесь группой.",
        "Ожидается дождь. Проверьте герметичность костюмов.",
        "Маскировочные халаты в наличии у Бармена.",
        "Говорят, на Янтаре видели контролера. Будьте осторожны.",
        "Слышал, на Армейских складах нашли склад боеприпасов.",
        "Погода портится, чувствую - будет гроза.",
        "На Свалке опять бандиты шалят. Обходите стороной.",
        "Кровососы мигрируют к северу. Инфа от разведки.",
        "На Кордоне тихо. Слишком тихо...",
        "В баре сегодня наливают за помин погибших.",
        "Долг и Свобода опять не поделили территорию."
    ]
    return random.choice(messages)

def get_next_interval(min_interval: int, max_interval: int) -> int:
    """Возвращает случайный интервал в секундах"""
    return random.randint(min_interval, max_interval)

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
        "Сталкер, добро пожаловать в Единую сталкерскую сеть!\n\n"
        "Я буду присылать сводки о происшествиях в Зоне:\n"
        "- Смерти сталкеров\n"
        "- Предупреждения о выбросах\n"
        "- Находки артефактов\n"
        "- Квесты и задания\n"
        "- Предложения проводников\n\n"
        "Команды:\n"
        "/status - статус сети\n"
        "/test - тестовые сообщения\n"
        "/stop - остановить рассылку"
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
        f"Единая сталкерская сеть активна\n"
        f"Связь с Зоной устойчивая\n"
        f"Режим: автоматическая рассылка\n"
        f"Отправлено сообщений: {chat_info['message_count']}"
    )

@dp.message(Command("test"))
async def cmd_test(message: Message):
    """Тестовая отправка всех типов сообщений"""
    await message.answer("Тестовые сообщения:")
    await asyncio.sleep(1)
    await message.answer(generate_death_message())
    await asyncio.sleep(1)
    await message.answer(generate_artifact_message())
    await asyncio.sleep(1)
    await message.answer(generate_quest_message())
    await asyncio.sleep(1)
    await message.answer(generate_guide_message())
    await asyncio.sleep(1)
    await message.answer(generate_random_message())

@dp.message(Command("stop"))
async def cmd_stop(message: Message):
    """Остановка рассылки в текущем чате"""
    chat_id = message.chat.id
    if chat_id in active_chats:
        del active_chats[chat_id]
        await message.answer("Рассылка остановлена в этом чате")
        logger.info(f"Чат удален из рассылки: {chat_id}")
    else:
        await message.answer("Этот чат не был в списке рассылки")

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
        
        # Отправляем приветственное сообщение
        await message.answer(
            "Приветствую, сталкер! Этот чат добавлен в Единую сталкерскую сеть.\n"
            "Используй /start для получения информации."
        )

# ==================== ФОНОВЫЕ ЗАДАЧИ ====================
async def message_scheduler():
    """Планировщик отправки всех типов сообщений"""
    last_death_time = datetime.now()
    last_emission_time = datetime.now()
    last_artifact_time = datetime.now()
    last_quest_time = datetime.now()
    last_guide_time = datetime.now()
    last_random_time = datetime.now()
    
    # Для отслеживания активного выброса
    active_emission = None  # (chat_id, end_time)
    
    while True:
        try:
            if not active_chats:
                logger.info("Нет активных чатов, ждем...")
                await asyncio.sleep(60)
                continue
            
            current_time = datetime.now()
            
            # Проверяем активный выброс
            if active_emission:
                chat_id, end_time = active_emission
                if current_time >= end_time and chat_id in active_chats:
                    try:
                        await bot.send_message(chat_id, generate_emission_end())
                        active_chats[chat_id]['message_count'] += 1
                        logger.info(f"Отправлено окончание выброса в чат {chat_id}")
                    except Exception as e:
                        logger.error(f"Ошибка отправки окончания выброса: {e}")
                    active_emission = None
            
            messages_to_send = []
            
            # Проверяем интервалы для каждого типа сообщений
            if (current_time - last_death_time).total_seconds() > get_next_interval(DEATH_MIN_INTERVAL, DEATH_MAX_INTERVAL):
                messages_to_send.append(("смерть", generate_death_message()))
                last_death_time = current_time
                
                # Проверяем вероятность выброса
                if random.random() < EMISSION_PROBABILITY and not active_emission:
                    await asyncio.sleep(random.randint(30, 300))
                    emission_msgs, minutes = generate_emission_sequence()
                    
                    # Отправляем предупреждение о выбросе
                    for msg in emission_msgs:
                        for chat_id in list(active_chats.keys()):
                            try:
                                await bot.send_message(chat_id, msg)
                                active_chats[chat_id]['message_count'] += 1
                                logger.info(f"Отправлено предупреждение о выбросе в чат {chat_id}")
                            except Exception as e:
                                logger.error(f"Ошибка отправки в чат {chat_id}: {e}")
                                if "Forbidden" in str(e) or "chat not found" in str(e):
                                    active_chats.pop(chat_id, None)
                        await asyncio.sleep(random.randint(30, 120))
                    
                    # Запускаем таймер начала выброса
                    async def start_emission(chat_id, minutes):
                        await asyncio.sleep(minutes * 60)
                        if chat_id in active_chats:
                            try:
                                await bot.send_message(chat_id, generate_emission_start(minutes))
                                active_chats[chat_id]['message_count'] += 1
                                logger.info(f"Отправлено начало выброса в чат {chat_id}")
                                # Устанавливаем окончание выброса через 2-5 минут
                                global active_emission
                                active_emission = (chat_id, datetime.now() + timedelta(minutes=random.randint(2, 5)))
                            except Exception as e:
                                logger.error(f"Ошибка отправки начала выброса: {e}")
                    
                    # Запускаем для каждого чата
                    for chat_id in list(active_chats.keys()):
                        asyncio.create_task(start_emission(chat_id, minutes))
            
            if (current_time - last_emission_time).total_seconds() > EMISSION_INTERVAL and not active_emission:
                emission_msgs, minutes = generate_emission_sequence()
                
                # Отправляем предупреждение о выбросе
                for msg in emission_msgs:
                    for chat_id in list(active_chats.keys()):
                        try:
                            await bot.send_message(chat_id, msg)
                            active_chats[chat_id]['message_count'] += 1
                            logger.info(f"Отправлено плановое предупреждение о выбросе в чат {chat_id}")
                        except Exception as e:
                            logger.error(f"Ошибка отправки в чат {chat_id}: {e}")
                            if "Forbidden" in str(e) or "chat not found" in str(e):
                                active_chats.pop(chat_id, None)
                    await asyncio.sleep(random.randint(30, 120))
                
                # Запускаем таймер начала выброса
                async def start_emission(chat_id, minutes):
                    await asyncio.sleep(minutes * 60)
                    if chat_id in active_chats:
                        try:
                            await bot.send_message(chat_id, generate_emission_start(minutes))
                            active_chats[chat_id]['message_count'] += 1
                            logger.info(f"Отправлено начало выброса в чат {chat_id}")
                            # Устанавливаем окончание выброса через 2-5 минут
                            global active_emission
                            active_emission = (chat_id, datetime.now() + timedelta(minutes=random.randint(2, 5)))
                        except Exception as e:
                            logger.error(f"Ошибка отправки начала выброса: {e}")
                
                # Запускаем для каждого чата
                for chat_id in list(active_chats.keys()):
                    asyncio.create_task(start_emission(chat_id, minutes))
                
                last_emission_time = current_time
            
            if (current_time - last_artifact_time).total_seconds() > ARTIFACT_INTERVAL:
                messages_to_send.append(("артефакт", generate_artifact_message()))
                last_artifact_time = current_time
            
            if (current_time - last_quest_time).total_seconds() > QUEST_INTERVAL:
                messages_to_send.append(("квест", generate_quest_message()))
                last_quest_time = current_time
            
            if (current_time - last_guide_time).total_seconds() > GUIDE_INTERVAL:
                messages_to_send.append(("проводник", generate_guide_message()))
                last_guide_time = current_time
            
            # Случайные атмосферные сообщения (раз в 2-4 часа)
            if random.random() < 0.3:  # 30% шанс при каждой проверке
                messages_to_send.append(("атмосфера", generate_random_message()))
            
            # Отправляем все накопившиеся сообщения
            for msg_type, msg_text in messages_to_send:
                for chat_id in list(active_chats.keys()):
                    try:
                        await bot.send_message(chat_id, msg_text)
                        active_chats[chat_id]['message_count'] += 1
                        logger.info(f"Отправлено {msg_type} в чат {chat_id}")
                    except Exception as e:
                        logger.error(f"Ошибка отправки в чат {chat_id}: {e}")
                        if "Forbidden" in str(e) or "chat not found" in str(e):
                            logger.info(f"Удаляем чат {chat_id} из активных")
                            active_chats.pop(chat_id, None)
            
            # Ждем перед следующей проверкой
            await asyncio.sleep(300)  # Проверка каждые 5 минут
            
        except Exception as e:
            logger.error(f"Ошибка в message_scheduler: {e}")
            await asyncio.sleep(60)

# ==================== ЗАПУСК БОТА ====================
async def main():
    """Главная функция запуска"""
    logger.info("Бот Единой сталкерской сети запускается...")
    logger.info("Ожидание добавления в чаты...")
    
    # Запускаем планировщик как фоновую задачу
    asyncio.create_task(message_scheduler())
    
    # Запускаем поллинг
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
if __name__ == "__main__":
    asyncio.run(main())

