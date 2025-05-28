from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
import os

TOKEN = '8166412144:AAH6gFmQPOjGn3CSoDmwJuSBzSxEfbQ8x8M'
bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=0)

# Обработчик команды /start
def start(update: Update, context):
    update.message.reply_text("Бот работает через Webhook!")

# Обработчик текстовых сообщений
def echo(update: Update, context):
    update.message.reply_text(update.message.text)

# Добавляем обработчики в dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Webhook обработка
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)