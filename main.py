import os
import telebot
from config import *
from telebot import types
import subprocess
import secrets

# Initializing Limits Database
init_usage_db()

class AccessDeniedError(Exception):
    pass

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Centralized access check

def check_access(message) -> bool:
    try:
        # min age
        if not is_account_older_than_1_year(message.from_user.id):
            print("[access] FAIL: is_account_older_than_1_year")
            raise AccessDeniedError(
                "@TelescopyRBot не поддерживает подозрительную активность и мошенническую деятельность!\n"
                "Для использования бота необходим минимум 1 год с момента регистрации 🕜\n"
                "Если вы верите, что были ограничены по ошибке, вы можете create 👁 issue на GitHub.")

        # anti fraud
        if not anti_fraud_validation(message):
            print("[access] FAIL: anti_fraud_validation")
            raise AccessDeniedError("Заблокировано политикой безопасности.")

        # black list
        if not if_trusted_user(message):
            print("[access] FAIL: if_trusted_user")
            raise AccessDeniedError("В списке заблокированных.")

        # limit 1 video/day
        if not check_usage_limit(message.from_user.id):
            print("[access] FAIL: check_usage_limit")
            raise AccessDeniedError("Достигнут лимит (1 видео в сутки).")

        print("[access] PASS")
        return True

    except Exception as e:
        bot.reply_to(message, str(e))
        return False

# Command handlers

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
                     text='Просто пришлите видео и получите его в виде видео‑сообщения. '
                          'Конвертация может занять некоторое время, пожалуйста, дождитесь окончания ⌛️\n'
                          'Подробнее: https://github.com/rumiantsevaa/Telescopy_Telegram_Bot')
    bot.register_next_step_handler(message, handle_video)


# Telegram Limit Constants

MAX_TG_FILE_SIZE = 20 * 1024 * 1024   # 20MB
MAX_DURATION = 60

# Video processor

@bot.message_handler(content_types=['video'])
def handle_video(message):
    chat_id = message.chat.id

    # Access check
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

    # New size check BEFORE calling get_file
    if file_size > MAX_TG_FILE_SIZE:
        bot.send_message(
            chat_id,
            f"Видео слишком большое: {file_size/1024/1024:.1f} МБ. Максимум — 20 МБ.\n"
            "Пожалуйста, пришлите файл меньшего размера."
        )
        # Remain waiting for a new file
        bot.register_next_step_handler(message, handle_video)
        return

    # Additional Duration Notice
    if duration > MAX_DURATION:
        bot.send_message(chat_id, "Видео длиннее 1 минуты, оно будет автоматически обрезано до 60 секунд ✂️")

    # Uploading video
    try:
        file_info = bot.get_file(video.file_id)
    except telebot.apihelper.ApiTelegramException as e:
        # Сatching a Telegram error if it occurs
        bot.send_message(chat_id, f"Не удалось получить файл: {e}")
        bot.register_next_step_handler(message, handle_video)
        return

    downloaded_file = bot.download_file(file_info.file_path)

    # Create safe paths
    safe_name = secrets.token_hex(8) + ".mp4"
    input_file = os.path.join(video_storage, safe_name)
    output_file = os.path.join(video_storage, "output_" + safe_name)

    os.makedirs(video_storage, exist_ok=True)

    # Save the file
    with open(input_file, 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.reply_to(message, "Видео сохранено. Дождитесь окончания конвертации ⌛️")

    try:
        cut_duration = min(duration, MAX_DURATION)

        # Creating size filter
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
                duration=cut_duration,
                length=512
            )

        register_usage(message.from_user.id)

    except subprocess.CalledProcessError as e:
        bot.send_message(chat_id, f"Ошибка при обработке видео: {e}")
    except Exception as e:
        bot.send_message(chat_id, f"Непредвиденная ошибка: {e}")
    finally:
        # Delete temporary files
        for f in [input_file, output_file]:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception as cleanup_error:
                print(f"[WARN] Не удалось удалить файл: {f} — {cleanup_error}")

    continue_handler(message)

# Text fallback

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

# Service functions

def continue_handler(message):
    bot.send_message(chat_id=message.chat.id,
                     text="Если желаете выполнить повторную конвертацию, отправьте новое видео или нажмите /start.")

if __name__ == '__main__':
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"[ERROR] {e}")
