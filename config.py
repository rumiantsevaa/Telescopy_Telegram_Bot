import sqlite3
from datetime import datetime, timedelta
from security import if_trusted_user, anti_fraud_validation, is_account_older_than_1_year

TELEGRAM_TOKEN = 'SECRET'
video_storage = "./videos"
DB_PATH = "./limits.db"

def init_usage_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS UsageHistory (
        user_id INTEGER PRIMARY KEY,
        last_usage_time TEXT,
        usage_count INTEGER DEFAULT 0
    )
    ''')

    c.execute('CREATE INDEX IF NOT EXISTS idx_user_time ON UsageHistory(user_id, last_usage_time)')
    conn.commit()
    conn.close()

def check_usage_limit(user_id: int, max_attempts: int = 1) -> bool:
    now = datetime.utcnow()
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT last_usage_time, usage_count FROM UsageHistory WHERE user_id = ?', (user_id,))
        result = c.fetchone()

        if result:
            last_time, count = datetime.fromisoformat(result[0]), result[1]
            if (now - last_time < timedelta(days=1)) and (count >= max_attempts):
                return False
        return True  # Access allowed

def register_usage(user_id: int):
    now = datetime.utcnow()
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT last_usage_time, usage_count FROM UsageHistory WHERE user_id = ?', (user_id,))
        result = c.fetchone()

        if result:
            last_time, count = datetime.fromisoformat(result[0]), result[1]
            if (now - last_time) >= timedelta(days=1):
                new_count = 1
            else:
                new_count = count + 1
            c.execute('UPDATE UsageHistory SET last_usage_time = ?, usage_count = ? WHERE user_id = ?', (now.isoformat(), new_count, user_id))
        else:
            c.execute('INSERT INTO UsageHistory (user_id, last_usage_time, usage_count) VALUES (?, ?, ?)', (user_id, now.isoformat(), 1))

        conn.commit()

def validate_user(message):
    return (
        anti_fraud_validation(message) and
        if_trusted_user(message) and
        check_usage_limit(message.from_user.id)
    )

def get_access_error():
    return "Извините, @TelescopyRBot недоступен для вас."
