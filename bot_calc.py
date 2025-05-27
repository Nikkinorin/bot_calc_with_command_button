import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

TOKEN = os.getenv('TOKEN')  # Читаем токен из окружения

PRICE, WEIGHT, FREIGHT, DUTY, VAT = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['Начать расчет']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Привет! Я калькулятор для расчета себестоимости продукции. Нажмите кнопку ниже, чтобы начать расчет.",
        reply_markup=markup
    )
    return PRICE

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['price'] = float(update.message.text)
    await update.message.reply_text('Введите общий вес продукции (в кг):')
    return WEIGHT

async def weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['weight'] = float(update.message.text)
    await update.message.reply_text('Введите стоимость фрахта (USD):')
    return FREIGHT

async def freight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['freight'] = float(update.message.text)
    await update.message.reply_text('Введите процент пошлины (%):')
    return DUTY

async def duty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['duty'] = float(update.message.text)
    await update.message.reply_text('Введите процент НДС (%):')
    return VAT

async def vat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vat'] = float(update.message.text)

    price = context.user_data['price']
    weight = context.user_data['weight']
    freight = context.user_data['freight']
    duty = context.user_data['duty']
    vat = context.user_data['vat']
    extra_cost = 90  # Дополнительные расходы за тонну

    freight_per_kg = freight / weight
    duty_per_kg = price * duty / 100
    vat_per_kg = price * vat / 100
    total_per_kg = price + freight_per_kg + duty_per_kg + vat_per_kg
    total_per_ton = total_per_kg * 1000 + extra_cost

    result = (
        f"Результаты расчета:
"
        f"Цена за кг: {price:.2f} USD
"
        f"Общий вес: {weight:.2f} кг
"
        f"Фрахт: {freight:.2f} USD
"
        f"Пошлина: {duty:.1f}%
"
        f"НДС: {vat:.1f}%
"
        f"Фрахт за кг: {freight_per_kg:.4f} USD
"
        f"Пошлина за кг: {duty_per_kg:.4f} USD
"
        f"НДС за кг: {vat_per_kg:.4f} USD
"
        f"Итого за кг: {total_per_kg:.4f} USD
"
        f"Итого за тонну (+90 USD): {total_per_ton:.2f} USD
"
        "Нажмите /start для нового расчета."
    )
    await update.message.reply_text(result)
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price)],
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, weight)],
            FREIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, freight)],
            DUTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, duty)],
            VAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, vat)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == '__main__':
    main()
