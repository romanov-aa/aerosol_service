import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
import math
from datetime import datetime
import sqlite3

TOKEN = '6707926596:AAF1M9CdFQAtBwA75Dbd4Evpd7oQCnjV26k'

# URL Flask API
API_URL = 'http://127.0.0.1:5000/predict'

DB_FILE = 'statistic.db'

(
    AOT,
    PDR,
    LR,
) = range(3)

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS statistic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aod_870 REAL,
            aod440 REAL,
            aod675 REAL,
            aod1020 REAL,
            angstrom REAL,
            lidar REAL,
            depolar REAL,
            latitude REAL,
            longtitude REAL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def save_to_db(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO statistic (aod_870, aod440, aod675, aod1020, angstrom, lidar, depolar, latitude, longtitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            data['aot_870'],
            data['aot_440'],
            data['aot_675'],
            data['aot_1040'],
            data['angstrom'],
            data['lidar'],
            data['depolar'],
            data['latitude'],
            data['longitude'],
        ))

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Ошибка при сохранении в базу данных: {e}")
        return False

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Пожалуйста, введите значения аэрозольной оптической толщи (440 нм, 675 нм, 870 нм, 1040 нм) через запятую.\n"
        "если ошиблись, введите /reset"
    )
    return AOT

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Этот бот помогает рассчитать эффективный радиус частиц аэрозоля.\n\n"
        "Используйте следующие команды:\n"
        "/start - начать ввод данных для расчета.\n"
        "/reset - сбросить текущий ввод и начать заново.\n"
        "/cancel - отменить текущий диалог.\n"
        "/help - показать это сообщение.\n\n"
        "После команды /start вам нужно будет ввести:\n"
        "1. Значения аэрозольной оптической толщи (440 нм, 675 нм, 870 нм, 1040 нм) через запятую.\n"
        "2. Линейное деполяризационное отношение (PDR).\n"
        "3. Лидарное отношение (LR).\n\n"
        "Пример ввода значений аэрозольной оптической толщи: 0.1, 0.2, 0.3, 0.4"
    )
    await update.message.reply_text(help_text)

async def get_aot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        aot_values = [float(x.strip()) for x in update.message.text.split(',')]
        if len(aot_values) != 4:
            await update.message.reply_text(
                "Ошибка: Пожалуйста, введите ровно 4 значения через запятую (440 нм, 675 нм, 870 нм, 1040 нм)."
            )
            return AOT

        context.user_data['aot_440'] = aot_values[0]
        context.user_data['aot_675'] = aot_values[1]
        context.user_data['aot_870'] = aot_values[2]
        context.user_data['aot_1040'] = aot_values[3]

        await update.message.reply_text("Введите линейное деполяризационное отношение (PDR).")
        return PDR

    except ValueError:
        await update.message.reply_text(
            "Ошибка: Пожалуйста, введите числовые значения через запятую."
        )
        return AOT


async def get_pdr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        pdr_value = float(update.message.text)
        context.user_data['pdr'] = pdr_value

        await update.message.reply_text("Введите лидарное отношение (LR).")
        return LR

    except ValueError:
        await update.message.reply_text("Ошибка: Пожалуйста, введите числовое значение для PDR.")
        return PDR


async def get_lr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        lr_value = float(update.message.text)
        context.user_data['lr'] = lr_value

        await update.message.reply_text("Выполняется расчет...")

        data = {
            "aot": {
                "440nm": context.user_data['aot_440'],
                "675nm": context.user_data['aot_675'],
                "870nm": context.user_data['aot_870'],
                "1020nm": context.user_data['aot_1040'],
            },
            "ang": 1.0,
            "lr": context.user_data['lr'],
            "dpr": context.user_data['pdr'],
            "coord": {"lat": 0.0, "lon": 0.0},
        }

        response = requests.post(API_URL, json=data, headers={'Content-Type': 'application/json'})

        if response.status_code == 200:
            result = response.json()['result']
            truncated_result = str(result)[:5]
            await update.message.reply_text(f"Эффективный радиус частиц аэрозоля: {truncated_result}] микрометра")

            db_data = {
                'aot_440': context.user_data['aot_440'],
                'aot_675': context.user_data['aot_675'],
                'aot_870': context.user_data['aot_870'],
                'aot_1040': context.user_data['aot_1040'],
                'angstrom': 1.0,
                'lidar': context.user_data['lr'],
                'depolar': context.user_data['pdr'],
                'latitude': 43.1056,
                'longitude': 131.874,
            }
            if save_to_db(db_data):
                await update.message.reply_text("Данные успешно сохранены в базу данных.")
            else:
                await update.message.reply_text("Ошибка при сохранении данных в базу данных.")
        else:
            await update.message.reply_text(f"Ошибка API: {response.status_code} - {response.text}")

        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("Ошибка: Пожалуйста, введите числовое значение для LR.")
        return LR
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    await update.message.reply_text(
        "Диалог отменен."
    )
    return ConversationHandler.END

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Resets the current input."""
    user = update.message.from_user
    await update.message.reply_text(
        "Ввод сброшен. Начните заново с команды /start"
    )
    context.user_data.clear()
    return ConversationHandler.END

def main():
    init_db()

    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AOT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_aot)],
            PDR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_pdr)],
            LR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_lr)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling()


if __name__ == '__main__':
    main()