# Telescopy Telegram Bot @TelescopyRBot

_Russian version https://github.com/rumiantsevaa/Telescopy_Telegram_Bot/wiki/READme.russian_

The main goal of creating the bot was to make it simple yet useful for many users, providing essential functionality without any hidden motives or unethical actions. The bot was developed in a way that it doesn't steal user data, doesn't distract them with intrusive advertising, and doesn't require payment for basic features.

![image](https://github.com/rumiantsevaa/Telescopy_Telegram_Bot/assets/89034072/77f644fc-5c6f-4bbb-83fc-33ba45036789)

## @TelescopyRBot is a Telegram bot designed to process videos sent by users and convert them into circular video messages. 

# Let's start with requirements and limitations.

![image](https://github.com/rumiantsevaa/Telescopy_Telegram_Bot/assets/89034072/c587861a-343d-477a-8e50-23cad746824c)

## Upon receiving a video, the bot checks its dimensions, cropping it to a 512x512 pixel square if larger, or scaling it to fit those dimensions if smaller. Additionally, the bot limits the video duration to 59 seconds. The converted video is then sent back to the user as a video note.

![image](https://github.com/rumiantsevaa/Telescopy_Telegram_Bot/assets/89034072/43459275-8212-40d0-8167-8c141be0848c)

# The bot supports the following commands:

* /start - Begin interaction with the bot and receive a welcome message.

![image](https://github.com/rumiantsevaa/Telescopy_Telegram_Bot/assets/89034072/876fb656-e01a-419f-a1c7-1f6fc4e8653b)


* /help - Get information about the bot and instructions for usage.

![image](https://github.com/rumiantsevaa/Telescopy_Telegram_Bot/assets/89034072/f9053978-d601-4d3f-8899-1b769dd7f21d)


After sending a video, the bot automatically starts processing it. Once processing is complete, the user is prompted to send a new video or use the /start command to initiate processing again.

![image](https://github.com/rumiantsevaa/Telescopy_Telegram_Bot/assets/89034072/5eee4a3c-a8ed-4b8c-906a-5d63a0d79260)


## The bot is created using Python and the telebot, os, subprocess, and ffmpeg libraries. Configuration data such as the Telegram token is stored in a separate file called config.py.

# Data Privacy in @TelescopyRBot

* Avoiding the use of any third-party libraries or services that could collect or transmit user data, relying only on standard Python libraries and the Telegram Bot API.

* Eliminating mentions of advertisements or attempts to integrate them. The bot provides its functionality honestly and without any hidden motives.

* Not requesting any paid subscription or payment for using the bot. All features are available for free, and the bot doesn't push paid services.

* Focusing the bot's code solely on its main task - processing videos and converting them into circular video notes. There are no extra or hidden features that could compromise user privacy or trust.

* Providing clear and comprehensive /start and /help commands so that users can easily start using the bot and get necessary information about its capabilities.

## Thus, a bot was created that truly adheres to the principles of honesty, transparency, and respect for users, providing the necessary functionality without any hidden motives or unethical actions.
