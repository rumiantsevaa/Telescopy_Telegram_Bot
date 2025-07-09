# Telescopy Telegram Bot — [@TelescopyRBot](https://t.me/TelescopyRBot)

![image](https://github.com/rumiantsevaa/Telescopy_Telegram_Bot/assets/89034072/77f644fc-5c6f-4bbb-83fc-33ba45036789)

> _This page is also available in [Russian version](https://github.com/rumiantsevaa/Telescopy_Telegram_Bot/wiki/README.ru)_

---

### 🌀 Overview

[@TelescopyRBot](https://t.me/TelescopyRBot) is a privacy-first Telegram bot that converts user-uploaded videos into **circular video messages** (video notes) suitable for Telegram chats.

- 🎥 Accepts standard video files  
- 🟠 Converts them into round video notes  
- ✂️ Automatically crops or scales to 512×512 px  
- ⏱️ Trims video to max 59 seconds  
- 🔒 Enforces **1 conversion per day per user**

The bot is designed with **simplicity**, **privacy**, and **ethical use** in mind — no ads, no tracking, no payments.

---

### 🔧 Updates (July 2025)

#### 🚀 Hosting & Deployment
- Deployed to [PythonAnywhere](https://www.pythonanywhere.com/) for **24/7 uptime**
- Added `pythonanywhere_starter.py` for seamless hosting

#### ⏳ Daily Conversion Limit
- Users can perform **1 conversion per day**
- Limit resets after 24h and is tracked in a local SQLite database
- Limit is applied **after** successful conversion

#### 🔐 Security & Validation
- `security.py` checks user and blocks potentially abusive patterns.
- Blocked users are stored in `blocked_users.db`  
- Only trusted users can access the bot

#### 📁 Project Structure Highlights
- `main.py` — core bot logic and video handling
- `config.py` — stores tokens, paths, and usage control
- `security.py` — implements anti-fraud and block logic
- `requirements.txt` — lists dependencies
- `pythonanywhere_starter.py` — clean launch for hosted environment

---

### ⚙️ How It Works

![image](https://github.com/rumiantsevaa/Telescopy_Telegram_Bot/assets/89034072/c587861a-343d-477a-8e50-23cad746824c)

1. User sends a video
2. Bot downloads it and inspects dimensions
3. If needed, crops or scales to 512x512
4. Trims video to 59 seconds
5. Sends back a video note (circular message)

![image](https://github.com/rumiantsevaa/Telescopy_Telegram_Bot/assets/89034072/43459275-8212-40d0-8167-8c141be0848c)

---

### 💬 Commands

- `/start` — start the interaction and receive instructions

  ![image](https://github.com/rumiantsevaa/Telescopy_Telegram_Bot/assets/89034072/876fb656-e01a-419f-a1c7-1f6fc4e8653b)

- `/help` — view bot features and usage instructions

  ![image](https://github.com/rumiantsevaa/Telescopy_Telegram_Bot/assets/89034072/f9053978-d601-4d3f-8899-1b769dd7f21d)

After sending a video, the bot immediately starts processing. When finished, it prompts the user to send another or use `/start`.

![image](https://github.com/rumiantsevaa/Telescopy_Telegram_Bot/assets/89034072/5eee4a3c-a8ed-4b8c-906a-5d63a0d79260)

---

### 📂 Deployment

To run the bot yourself:

1. Install dependencies:

    ```bash
    git clone https://github.com/rumiantsevaa/Telescopy_Telegram_Bot.git
    ```

    ```bash
    pip install -r requirements.txt
    ```

3. Create the SQLite databases (limits and blocked users)

4. Set your `TELEGRAM_TOKEN` in `config.py`

5. Launch the bot:

    ```bash
    python main.py
    ```

---

### 🔒 Privacy & Ethics

The bot was built with a strong stance on **user privacy**, **no surveillance**, and **free access**.

- ✅ No ads, tracking, or telemetry
- ✅ No cloud storage — all files are processed locally and deleted
- ✅ No user profiling or data sharing
- ✅ No payments or freemium traps
- ✅ Simple purpose: video → video note, nothing else

---

### 🧠 Philosophy

The core motivation behind @TelescopyRBot is:

> "To make a useful tool without exploiting users, cluttering their experience, or compromising trust."

If you're tired of bloated bots with ads, fees, and dark patterns — this one is for you ❤️

---
