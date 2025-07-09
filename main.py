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

    file_id = message.video.file_id
    video = message.video
    duration = video.duration
    video_w = video.width
    video_h = video.height

    if duration > 60:
        bot.send_message(chat_id, "Видео длиннее 1 минуты, оно будет автоматически обрезано до 60 секунд.")

    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    file_absolute_path = os.path.join(video_storage, file_info.file_path)
    os.makedirs(os.path.dirname(file_absolute_path), exist_ok=True)

    with open(file_absolute_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.reply_to(message, "Видео сохранено. Дождитесь окончания конвертации.")

    input_file = file_absolute_path
    output_file = os.path.join(os.path.dirname(input_file), f"output_{os.path.basename(input_file)}")

    try:
        cut_duration = min(duration, 60)

        if video_w > 512 and video_h > 512:
            cmd = f'ffmpeg -y -i "{input_file}" -vf "crop=512:512" -t {cut_duration} -c:v libx264 -c:a copy "{output_file}"'
        else:
            bot.send_message(chat_id, "Видео слишком маленькое. Пропорции могут быть искажены. Подождите...")
            filter_cmd = "crop='min(iw,ih)':'min(iw,ih)',scale=512:512"
            cmd = f'ffmpeg -y -i "{input_file}" -vf "{filter_cmd}" -t {cut_duration} -c:v libx264 -c:a copy "{output_file}"'

        subprocess.run(cmd, shell=True, check=True)

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
        if os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists(output_file):
            os.remove(output_file)

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
