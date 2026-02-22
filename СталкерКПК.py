import telebot
import time
import random
import threading
from datetime import datetime, timedelta

# Ваш токен бота (замените на реальный)
TOKEN = '7657570493:AAFqKUxdGQIcLRMGEkenDKaciqOoYv7K1QI'

# Создаём экземпляр бота
bot = telebot.TeleBot(TOKEN)
bot.set_webhook()

PHRASES1 = [
    "Умер сталкер ",
    "Погиб сталкер ",
    "Потерян в зоне ",
    "Не выжил ",
    "Скончался ",
]
Name1 = [
    "Валик Сталкер, ",
    "Юрий Семецкий, ",
    "Гоша Снегоступ, ",
    "Евгений Штопанный, ",
    "Петя Перец, ",
    "Артем Порох, ",
    "Ваня Тополь, ",
    "Рома Кинолог, ",
    "Тимоха Колиматор, ",
    "Илья Топор"
]
Loka2 = [
    "Кордон, ",
    "Свалка, ",
    "НИИ Агропром, ",
    "Радар, ",
    "Припять, ",
    "Завод Росток, ",
    "Дикая территория, ",
    "Темная долина, ",
    "Предбанник, ",
    "Армейские склады, "
]
Prizin3 = [
    "Воронка",
    "Кабан",
    "Огнестрельное ранение",
    "Плоть",
    "Кот баюн",
    "Кровоизлеяние",
    "Электра",
    "Трамплин",
    "Жарка",
    "Жгучий пух"
]

def send_random_daily_messages():

    """Отправляет от 1 до 7 сообщений в день с интервалом ≥1 часа. Количество и время отправки случайны."""

    while True:
        # Опред текущее время
        now = datetime.now()
        
        # Случайное количество сообщений на сегодня от 1 до 7
        num_messages = random.randint(1, 7)
        
        # Генерируем времена отправки
        send_times = []
        for _ in range(num_messages):
            # Случайное смещение в секундах от начала дня (00:00:00)
            seconds = random.randint(0, 86399)  # 0..23:59:59
            candidate_time = (now.replace(hour=0, minute=0, second=0, microsecond=0) +
                             timedelta(seconds=seconds))
            
            # Проверяем, что интервал с предыдущими ≥1 часа (3600 сек)
            if send_times:
                last_time = send_times[-1]
                if (candidate_time - last_time).total_seconds() < 3600:
                    # Если меньше часа — сдвигаем на 1 час вперёд
                    candidate_time = last_time + timedelta(hours=1)
            
            send_times.append(candidate_time)
        
        # Сортируем по времени
        send_times.sort()
        
        # Ждём и отправляем каждое сообщение
        for send_time in send_times:
            # Если время уже прошло (например, из‑за долгого цикла), пропускаем
            if send_time <= now:
                continue
            
            # Время ожидания в секундах
            wait_time = (send_time - now).total_seconds()
            time.sleep(wait_time)
            
            # Текст сообщения (оставьте пустым или заполните)
            message_text1 = random.choice(PHRASES1),random.choice(Name1),random.choice(Loka2),random.choice(Prizin3)
            
            try:
                bot.send_message(message_text1)
                print(f"[{datetime.now()}] Отправлено случайное сообщение в {send_time.time()}")
            except Exception as e:
                print(f"[{datetime.now()}] Ошибка при отправке случайного сообщения: {e}")
        
        # Ждём до следующего дня
        tomorrow = now.date() + timedelta(days=1)
        midnight = datetime.combine(tomorrow, datetime.min.time())
        wait_until_tomorrow = (midnight - now).total_seconds()
        time.sleep(wait_until_tomorrow)

def send_daily_random_time_message():

    """Отправляет одно сообщение в день в случайное время."""

    while True:
        now = datetime.now()
        
        # Генерируем случайное время в течение текущих суток
        random_hour = random.randint(0, 23)
        random_minute = random.randint(0, 59)
        random_second = random.randint(0, 59)
        
        send_time = now.replace(
            hour=random_hour,
            minute=random_minute,
            second=random_second,
            microsecond=0
        )
        
        # Если время уже прошло — на завтра
        if send_time <= now:
            send_time += timedelta(days=1)
        
        # Время ожидания
        wait_time = (send_time - now).total_seconds()
        time.sleep(wait_time)
        
        # Текст сообщения
        message_text = ""
        
        try:
            bot.send_message(message_text)
            print(f"[{datetime.now()}] Отправлено ежедневное сообщение в {send_time.time()}")
        except Exception as e:
            print(f"[{datetime.now()}] Ошибка при отправке ежедневного сообщения: {e}")
        
        # Ждём до следующего дня
        tomorrow = now.date() + timedelta(days=1)
        midnight = datetime.combine(tomorrow, datetime.min.time())
        wait_until_tomorrow = (midnight - now).total_seconds()
        time.sleep(wait_until_tomorrow)

if __name__ == '__main__':
    print("Бот запущен...")
    
    # Запускаем потоки
    threading.Thread(target=send_random_daily_messages, daemon=True).start()
    threading.Thread(target=send_daily_random_time_message, daemon=True).start()
    
    # Основной цикл бота (для команд, если нужно)
    bot.infinity_polling()
