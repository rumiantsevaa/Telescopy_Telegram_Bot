import os
import telebot
from config import *
from telebot import types
import subprocess
from datetime import datetime

init_usage_db()

class AccessDeniedError(Exception):
    pass

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def check_access(message) -> bool:
    """
    Centralized user access check
    Combines all restrictions: anti-fraud measures, limits
    """
    try:
        if not anti_fraud_validation(message):
            print("[access] FAIL: anti_fraud_validation")
            raise AccessDeniedError("Заблокировано политикой безопасности.")
        if not if_trusted_user(message):
            print("[access] FAIL: if_trusted_user")
            raise AccessDeniedError("В списке заблокированных.")
        if not check_usage_limit(message.from_user.id):
            print("[access] FAIL: check_usage_limit")
            raise AccessDeniedError("Достигнут лимит на использование (1 в сутки).")

        print("[access] PASS")
        return True

    except Exception as e:
        bot.reply_to(message, str(e))
        return False

@bot.message_handler(commands=['start'])
def start_handler(message):
    if not check_access(message):
        return

    bot.send_message(
        chat_id=message.chat.id,
        text='Добрый день, я бот @TelescopyRBot и я умею делать кружочки ⭕️'
             ' Отправьте видео для обработки.')
    bot.register_next_step_handler(message, handle_video)

@bot.message_handler(commands=['help'])
def help_handler(message):
    if not check_access(message):
        return
    bot.send_message(chat_id=message.chat.id,
                     text='Просто пришлите видео для обработки и получите его в виде видео-сообщения. '
                          'Конвертация может занять некоторое время, пожалуйста, дождитесь окончания ⌛️\n'
                          'Подробнее: https://github.com/rumiantsevaa/Telescopy_Telegram_Bot')
    bot.register_next_step_handler(message, handle_video)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    chat_id = message.chat.id
    if not check_access(message):
        return
    if not message.video:
        bot.send_message(chat_id, "Пожалуйста, отправьте видео 📼")
        return

    video = message.video
    duration = video.duration
    video_w = video.width
    video_h = video.height
    file_size = video.file_size

    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MB
    if file_size > MAX_VIDEO_SIZE:
        bot.send_message(chat_id, "Видео слишком большое. Максимальный размер — 100 МБ.")
        return

    if duration > 60:
        bot.send_message(chat_id, "Видео длиннее 1 минуты, оно будет автоматически обрезано до 60 секунд.")

    # Загружаем видео
    file_info = bot.get_file(video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Создаём безопасные пути
    import secrets
    safe_name = secrets.token_hex(8) + ".mp4"
    input_file = os.path.join(video_storage, safe_name)
    output_file = os.path.join(video_storage, "output_" + safe_name)

    os.makedirs(video_storage, exist_ok=True)

    # Сохраняем файл
    with open(input_file, 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.reply_to(message, "Видео сохранено. Дождитесь окончания конвертации.")

    try:
        cut_duration = min(duration, 60)

        # Создание фильтра
        if video_w > 512 and video_h > 512:
            vf_filter = "crop=512:512"
        else:
            bot.send_message(chat_id, "Видео слишком маленькое. Пропорции могут быть искажены. Подождите...")
            vf_filter = "crop='min(iw,ih)':'min(iw,ih)',scale=512:512"

        cmd = [
            "ffmpeg", "-y",
            "-i", input_file,
            "-vf", vf_filter,
            "-t", str(cut_duration),
            "-c:v", "libx264",
            "-c:a", "copy",
            output_file
        ]

        subprocess.run(cmd, check=True)

        with open(output_file, 'rb') as video_file:
            bot.send_video_note(
                chat_id,
                video_file,
                duration=59,
                length=512
            )

        register_usage(message.from_user.id)

    except subprocess.CalledProcessError as e:
        bot.send_message(chat_id, f"Ошибка при обработке видео: {e}")
    except Exception as e:
        bot.send_message(chat_id, f"Непредвиденная ошибка: {e}")
    finally:
        # Удаляем временные файлы
        for f in [input_file, output_file]:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception as cleanup_error:
                print(f"[WARN] Не удалось удалить файл: {f} — {cleanup_error}")

    continue_handler(message)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    if not check_access(message):
        return
    if message.text == '/start':
        start_handler(message)
    elif message.text == '/help':
        help_handler(message)
    else:
        bot.send_message(message.chat.id, "Я вас не понимаю. Нажмите /start для списка команд.")

def continue_handler(message):
    bot.send_message(chat_id=message.chat.id,
                     text="Если желаете выполнить повторную конвертацию, отправьте новое видео или нажмите /start.")

if __name__ == '__main__':
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"[ERROR] {e}")
