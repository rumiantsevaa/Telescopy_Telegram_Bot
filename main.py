import os
import telebot
from config import *
import subprocess

bot = telebot.TeleBot(TELEGRAM_TOKEN)


# Запуск бота по команде
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(chat_id=message.chat.id, text='Добрый день, я бот @TelescopyRBot и я умею делать кружочки.'
                                                   'Отправьте видео для обработки')
    bot.register_next_step_handler(message, handle_video)


# Команда помощи и информации
@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_message(chat_id=message.chat.id, text='Просто пришлите видео для обработки и получите его в виде видео '
                                                   'сообщения. Конвертация может занять некоторое время, пожалуйста '
                                                   'дождитесь окончания.\n'
                                                   'Есть некоторые требования к видео, от которых будет зависить '
                                                   'качество конвертации.\n'
                                                   'Больше информации ищите в моем репозитории https://github.com/rumiantsevaa/Telescopy_Telegram_Bot')

    bot.register_next_step_handler(message, handle_video)


# Получение видео от пользователя и его сохранение для конвертации
@bot.message_handler(content_types=['video'])
def handle_video(message):
    chat_id = message.chat.id
    # Проверка прислал ли пользователь видео
    if not message.video:
        bot.send_message(chat_id, "Пожалуйста, отправьте видео.")
        return
    # Получение file_id видео
    file_id = message.video.file_id

    # Получение размеров видео для будущей проверки
    video = message.video
    video_w = video.width
    video_h = video.height

    # Получение file path используя file_id
    # Скачивание видео в папку video_storage
    file_path = bot.get_file(file_id).file_path
    downloaded_file = bot.download_file(file_path)

    # Формирование полного пути к файлу для сохранения
    file_absolute_path = os.path.join(video_storage, file_path)

    # Сохранение видео в папку video_storage и уведомление пользователя об успехе
    with open(file_absolute_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.reply_to(message, "Видео сохранено. Дождитесь окончания конвертации.")

    # Получение имени файла
    file_name_only = os.path.basename(file_absolute_path)

    # Путь к папке для результатов
    output_folder = os.path.dirname(file_absolute_path)

    # Редактирование видео ffmpeg из папки чтобы оно стало подходить под критерии: короче 60 сек, скругленное квадратное
    # 512 * 512

    # Создание имен для входного и выходного файлов
    input_file = file_name_only
    output_file = f"output_{file_name_only}"
    chat = message.chat.id

    # Проверка размеров видео(если больше 512 * 512)
    if video_h > 512 and video_w > 512:

        # Запуск консоли с параметрами
        batch_content_normal = f"""
        cd "{output_folder}"
        ffmpeg -y -i "{input_file}" -vf crop=512:512 -t 59 -c:v libx264 -c:a copy "{output_file}"
        """

        with open("my_script.bat", "w+") as file:
            file.write(batch_content_normal)
            file.close()

        subprocess.call("my_script.bat", shell=True)

        # Отправка видео в виде видео-заметки
        with open(f"{output_folder}/{output_file}", 'rb') as video_file:
            bot.send_video_note(
                chat,
                video_file,
                duration=59,  # Вы можете указать продолжительность видео в секундах
                length=512 * 512,  # Размер видео (диаметр) в пикселях
                # Другие необязательные параметры, если нужно
            )
    else:
        # Если видео меньше 512 * 512 конвертация через ffmpeg scale опцию
        bot.send_message(chat_id, "Видео слишком маленькое. Пропорции могут быть искажены. Рекомендуем увеличить"
                                  " размер видео: минимальные размеры 512 х 512 пикселей. Подождите...")
        batch_content_small = f"""
                cd "{output_folder}"
                ffmpeg -y -i "{input_file}" -vf scale=512:512 -t 59 -c:v libx264 -c:a copy "{output_file}"
                """

        with open("my_script.bat", "w+") as file:
            file.write(batch_content_small)
            file.close()

        subprocess.call("my_script.bat", shell=True)

        # Отправка видео в виде видео-заметки
        with open(f"{output_folder}/{output_file}", 'rb') as video_file:
            bot.send_video_note(
                chat,
                video_file,
                duration=59,  # Вы можете указать продолжительность видео в секундах
                length=512 * 512,  # Размер видео (диаметр) в пикселях
            )
    os.remove("my_script.bat")
    os.remove(f"{file_absolute_path}")
    os.remove(f"{output_folder}/{output_file}")
    continue_handler(message)


# Спрашиваем, хочет ли пользователь выполнить повторную конвертацию
def continue_handler(message):
    bot.send_message(chat_id=message.chat.id, text="Если желаете выполнить повторную конвертацию, отправьте новое "
                                                   "видео."
                                                   "Или нажмите /start.")


# Обработка любых текстовых сообщений
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    if message.text == '/start':
        start_handler(message)
    if message.video:
        handle_video(message)
    elif message.text == '/help':
        help_handler(message)
    else:
        bot.send_message(message.chat.id, "Я вас не понимаю. Нажмите /start для списка команд.")


if __name__ == '__main__':
    bot.polling()
