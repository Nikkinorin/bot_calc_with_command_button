from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters
import os

TOKEN = '8166412144:AAH6gFmQPOjGn3CSoDmwJuSBzSxEfbQ8x8M'
PORT = int(os.environ.get('PORT', 5000))

PRICE, WEIGHT, FREIGHT, EXTRA_COST, DUTY, NDS = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("💲 Введите цену за кг (USD):", reply_markup=ReplyKeyboardRemove())
    return PRICE

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['price'] = float(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Ошибка: Введите число для цены за кг.")
        return PRICE
    await update.message.reply_text("⚖️ Введите общий вес продукции (кг):")
    return WEIGHT

async def weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        weight_kg = float(update.message.text.strip())
        if weight_kg == 0:
            await update.message.reply_text("Ошибка: Вес не может быть 0.")
            return WEIGHT
        context.user_data['weight'] = weight_kg
    except ValueError:
        await update.message.reply_text("Ошибка: Введите число для веса.")
        return WEIGHT
    await update.message.reply_text("🚚 Введите стоимость фрахта (USD):")
    return FREIGHT

async def freight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['freight'] = float(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Ошибка: Введите число для фрахта.")
        return FREIGHT
    await update.message.reply_text("📦 Введите доп. расходы (USD):")
    return EXTRA_COST

async def extra_cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['extra_cost'] = float(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Ошибка: Введите число для доп. расходов.")
        return EXTRA_COST
    await update.message.reply_text("🧾 Введите процент пошлины (%):")
    return DUTY

async def duty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['duty'] = float(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Ошибка: Введите число для пошлины.")
        return DUTY
    await update.message.reply_text("💰 Введите процент НДС (%):")
    return NDS

async def nds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['nds'] = float(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Ошибка: Введите число для НДС.")
        return NDS

    price_per_kg = context.user_data['price']
    weight_kg = context.user_data['weight']
    freight = context.user_data['freight']
    extra_costs = context.user_data['extra_cost']
    duty = context.user_data['duty']
    nds = context.user_data['nds']

    total_freight = freight + extra_costs
    freight_per_kg = total_freight / weight_kg
    base_price_per_kg = price_per_kg + freight_per_kg
    duty_amount = base_price_per_kg * (duty / 100)
    nds_amount = (base_price_per_kg + duty_amount) * (nds / 100)
    final_price_per_kg = base_price_per_kg + duty_amount + nds_amount
    final_price_per_ton = final_price_per_kg * 1000 + extra_costs

    keyboard = [["/start"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    result = (
        "📊 *Результаты расчёта:*\n\n"
        f"💲 *Цена за кг:* `{price_per_kg:.2f}` USD\n"
        f"⚖️ *Вес:* `{weight_kg:.2f}` кг\n"
        f"🚚 *Фрахт:* `{freight:.2f}` USD\n"
        f"📦 *Доп. расходы:* `{extra_costs:.2f}` USD\n"
        f"🧾 *Пошлина:* `{duty}%`\n"
        f"💰 *НДС:* `{nds}%`\n\n"
        f"📈 *Фрахт за кг:* `{freight_per_kg:.4f}` USD\n"
        f"📈 *Пошлина за кг:* `{duty_amount:.4f}` USD\n"
        f"📈 *НДС за кг:* `{nds_amount:.4f}` USD\n\n"
        f"✅ *Итог за кг:* `{final_price_per_kg:.4f}` USD\n"
        f"✅ *Итог за тонну:* `{final_price_per_ton:.2f}` USD\n\n"
        "_Нажми кнопку ниже или введи команду /start для нового расчёта._"
    )
    await update.message.reply_text(result, parse_mode="Markdown", reply_markup=reply_markup)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('❌ Расчёт отменён.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

app = ApplicationBuilder().token(TOKEN).build()
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price)],
        WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, weight)],
        FREIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, freight)],
        EXTRA_COST: [MessageHandler(filters.TEXT & ~filters.COMMAND, extra_cost)],
        DUTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, duty)],
        NDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, nds)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
app.add_handler(conv_handler)

if __name__ == '__main__':
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://bot-calc-with-command-button.onrender.com/{TOKEN}"
    )
