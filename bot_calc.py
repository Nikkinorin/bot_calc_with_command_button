from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

TOKEN = '8166412144:AAH6gFmQPOjGn3CSoDmwJuSBzSxEfBq8x8M'

# Шаги
PRICE, WEIGHT, FREIGHT, DUTY, VAT = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['Начать расчёт']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Привет! Я калькулятор для расчёта себестоимости продукции.\n"
        "Нажмите кнопку ниже, чтобы начать.",
        reply_markup=markup
    )
    return PRICE

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['price'] = float(update.message.text)
    await update.message.reply_text('Введите общий вес продукции (кг):')
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

    price_per_kg = price
    freight_per_kg = freight / weight
    duty_per_kg = price_per_kg * duty / 100
    vat_per_kg = price_per_kg * vat / 100
    total_per_kg = price_per_kg + freight_per_kg + duty_per_kg + vat_per_kg
    total_per_ton = total_per_kg * 1000 + extra_cost

    reply_text = (
        "📊 Результаты расчёта:\n"
        f"💲 Цена за кг: {price_per_kg:.2f} USD\n"
        f"📦 Вес: {weight:.2f} кг\n"
        f"🚢 Фрахт: {freight:.2f} USD\n"
        f"📈 Пошлина: {duty:.1f}%\n"
        f"💰 НДС: {vat:.1f}%\n"
        f"📉 Фрахт за кг: {freight_per_kg:.4f} USD\n"
        f"📉 Пошлина за кг: {duty_per_kg:.4f} USD\n"
        f"📉 НДС за кг: {vat_per_kg:.4f} USD\n"
        f"✅ Итого за кг: {total_per_kg:.4f} USD\n"
        f"✅ Итого за тонну (с доп. расходами): {total_per_ton:.2f} USD\n\n"
        "Нажмите /start для нового расчёта."
    )
    await update.message.reply_text(reply_text)
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
