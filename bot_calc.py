from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes, ConversationHandler

TOKEN = '8166412144:AAH6gFmQPOjGn3CSoDmwJuSBzSxEfbQ8x8M'

PRICE, WEIGHT, FREIGHT, EXTRA, DUTY, VAT = range(6)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Начать расчёт", callback_data='start_calc')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Нажми кнопку ниже, чтобы начать расчёт.", reply_markup=reply_markup)
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'start_calc':
        await query.edit_message_text("Введите цену за кг (USD):")
        return PRICE
async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['price'] = float(update.message.text)
    await update.message.reply_text("Введите общий вес продукции (кг):")
    return WEIGHT
async def get_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['weight'] = float(update.message.text)
    await update.message.reply_text("Введите стоимость фрахта (USD):")
    return FREIGHT
async def get_freight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['freight'] = float(update.message.text)
    await update.message.reply_text("Введите доп. расходы (USD):")
    return EXTRA
async def get_extra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['extra'] = float(update.message.text)
    await update.message.reply_text("Введите процент пошлины (%):")
    return DUTY
async def get_duty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['duty'] = float(update.message.text)
    await update.message.reply_text("Введите процент НДС (%):")
    return VAT
async def get_vat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vat'] = float(update.message.text)
    result = calculate(context.user_data)
    keyboard = [[InlineKeyboardButton("/start", callback_data='start_calc')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(result, reply_markup=reply_markup, parse_mode='HTML')
    return ConversationHandler.END
def calculate(data):
    price, weight, freight, extra, duty, vat = data.values()
    total_freight_per_kg = (freight + extra) / weight
    total_price_per_kg = price + total_freight_per_kg
    duty_per_kg = (duty / 100) * price
    vat_per_kg = (vat / 100) * price
    total_per_kg = price + total_freight_per_kg + duty_per_kg + vat_per_kg
    total_per_ton = total_per_kg * 1000
    return f"<b>📊 Результаты расчёта:</b>\n💲 Цена за кг: {price:.2f} USD\n⚖ Вес: {weight:.2f} кг\n🚚 Фрахт: {freight:.2f} USD\n💼 Доп. расходы: {extra:.2f} USD\n💸 Пошлина: {duty:.1f}%\n💡 НДС: {vat:.1f}%\n---------------------\n🚚 Фрахт за кг: {total_freight_per_kg:.4f} USD\n💸 Пошлина за кг: {duty_per_kg:.4f} USD\n💡 НДС за кг: {vat_per_kg:.4f} USD\n---------------------\n💰 Итог за кг: {total_per_kg:.4f} USD\n💰 Итог за тонну: {total_per_ton:.2f} USD" 

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CallbackQueryHandler(button)],
        states={
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_weight)],
            FREIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_freight)],
            EXTRA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_extra)],
            DUTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_duty)],
            VAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_vat)]
        },
        fallbacks=[]
    )
    app.add_handler(conv_handler)
    app.run_polling()
