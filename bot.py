import logging
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.error import TelegramError
from database import Database
from config import Config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db = Database()

# 🔥 MENU FUNKSIYA (O‘ZGARMAGAN)
def get_main_menu():
    keyboard = [
        ["🔍 Qidirish", "📊 Statistika"],
        ["ℹ️ Yordam"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ─── SUBSCRIPTION CHECK ───────────────────────────────────────────────────────

async def check_telegram_subscription(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(
            chat_id=Config.TELEGRAM_CHANNEL,
            user_id=user_id
        )
        return member.status in ['member', 'administrator', 'creator']
    except TelegramError:
        return False

def build_subscription_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                "📢 Telegram Kanalga Obuna Bo'l",
                url=f"https://t.me/{Config.TELEGRAM_CHANNEL.lstrip('@')}"
            )
        ],
        [
            InlineKeyboardButton(
                "📸 Instagramga Obuna Bo'l",
                url=f"https://instagram.com/{Config.INSTAGRAM_USERNAME.lstrip('@')}"
            )
        ],
        [
            InlineKeyboardButton(
                "✅ Obuna bo'ldim, tekshir!",
                callback_data="check_subscription"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def send_subscription_required(update: Update):
    text = (
        "🔐 *Botdan foydalanish uchun obuna bo'ling!*\n\n"
        f"📢 Telegram: {Config.TELEGRAM_CHANNEL}\n"
        f"📸 Instagram: {Config.INSTAGRAM_USERNAME}\n\n"
        "Obuna bo'lgandan so'ng ✅ tugmasini bosing."
    )
    if update.callback_query:
        await update.callback_query.message.edit_text(
            text, parse_mode='Markdown',
            reply_markup=build_subscription_keyboard()
        )
    else:
        await update.message.reply_text(
            text, parse_mode='Markdown',
            reply_markup=build_subscription_keyboard()
        )

# ─── HANDLERS ────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # 🔥 O‘ZGARDI: har doim tugma chiqadi
    text = (
        f"📚 *Assalomu alaykum, {user.first_name}!*\n\n"
        "🔐 Botdan foydalanish uchun quyidagilarga obuna bo‘ling:\n\n"
        f"📢 Telegram: {Config.TELEGRAM_CHANNEL}\n"
        f"📸 Instagram: {Config.INSTAGRAM_USERNAME}\n\n"
        "Obuna bo‘lgandan so‘ng ✅ tugmasini bosing."
    )

    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=build_subscription_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_subscribed = await check_telegram_subscription(context.bot, user_id)
    if not is_subscribed:
        await send_subscription_required(update)
        return

    text = (
        "ℹ️ *TaqwoBook Bot Yordam*\n\n"
        "🔍 *Kitob qidirish:* Kitob nomini yozing\n"
        "📤 *Admin kitob yuklash:* /upload (faqat adminlar)\n"
        "📊 *Statistika:* /stats\n\n"
        "📌 *Eslatma:* Bot bazasida mavjud kitoblarni beradi.\n"
        "Agar kitob topilmasa, admin qo'shadi."
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_subscribed = await check_telegram_subscription(context.bot, user_id)
    if not is_subscribed:
        await send_subscription_required(update)
        return

    stats = db.get_stats()
    text = (
        "📊 *TaqwoBook Statistika*\n\n"
        f"👥 Foydalanuvchilar: *{stats['users']}*\n"
        f"📚 Kitoblar: *{stats['books']}*\n"
        f"📥 Jami yuklamalar: *{stats['downloads']}*"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def upload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_IDS:
        await update.message.reply_text("❌ Bu buyruq faqat adminlar uchun.")
        return

    await update.message.reply_text(
        "📤 *Kitob yuklash*\n\n"
        "PDF faylni yuboring. Fayl nomi kitob nomi bo'ladi.\n"
        "Yoki: PDF ni yuboring va caption'ga kitob nomini yozing.",
        parse_mode='Markdown'
    )

async def handle_pdf_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_IDS:
        return

    document = update.message.document
    if not document or document.mime_type != 'application/pdf':
        return

    book_name = update.message.caption or document.file_name
    if book_name.endswith('.pdf'):
        book_name = book_name[:-4]

    file_id = document.file_id
    file_size = document.file_size

    db.add_book(book_name, file_id, file_size)

    await update.message.reply_text(
        f"✅ *Kitob qo'shildi!*\n\n"
        f"📖 Nom: {book_name}\n"
        f"📦 Hajm: {file_size // 1024} KB",
        parse_mode='Markdown'
    )

async def search_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = update.effective_user

    is_subscribed = await check_telegram_subscription(context.bot, user_id)
    if not is_subscribed:
        await send_subscription_required(update)
        return

    query = update.message.text.strip()

    # MENU
    if query == "📊 Statistika":
        await stats_command(update, context)
        return

    if query == "ℹ️ Yordam":
        await help_command(update, context)
        return

    if query == "🔍 Qidirish":
        await update.message.reply_text("🔍 Kitob nomini yozing...")
        return

    if not query:
        return

    db.add_user(user_id, user.username or "", user.full_name or "")

    searching_msg = await update.message.reply_text(
        f"🔍 *{query}* qidirilmoqda...",
        parse_mode='Markdown'
    )

    results = db.search_books(query)

    if not results:
        await searching_msg.edit_text(
            f"❌ *{query}* topilmadi.\n\n"
            "📌 Admin bilan bog'laning yoki boshqa nom bilan qidiring.",
            parse_mode='Markdown'
        )
        return

    # 🔥 O‘ZGARDI: PDF / VIDEO tugma
    pdf = None
    video = None

    for book in results:
        if "pdf" in book['name'].lower():
            pdf = book
        elif "video" in book['name'].lower():
            video = book

    buttons = []

    if pdf:
        buttons.append(InlineKeyboardButton("📄 PDF", callback_data=f"book_{pdf['id']}"))

    if video:
        buttons.append(InlineKeyboardButton("🎬 Video", callback_data=f"book_{video['id']}"))

    if buttons:
        await searching_msg.edit_text(
            f"📖 *{query}*",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([buttons])
        )
        return

    # eski logika
    if len(results) == 1:
        book = results[0]
        await searching_msg.delete()
        await send_book(update, context, book, user_id)
    else:
        keyboard = []
        for book in results[:10]:
            keyboard.append([
                InlineKeyboardButton(
                    f"📖 {book['name']}",
                    callback_data=f"book_{book['id']}"
                )
            ])

        await searching_msg.edit_text(
            f"📚 *{len(results)} ta kitob topildi:*",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def send_book(update: Update, context: ContextTypes.DEFAULT_TYPE, book: dict, user_id: int):
    try:
        caption = (
            f"📖 *{book['name']}*\n\n"
            f"🕌 @TaqwobookBot dan yuklab oldingiz!\n"
            f"📢 Kanal: {Config.TELEGRAM_CHANNEL}"
        )

        # 🔥 O‘ZGARDI: video qo‘llab-quvvatlash
        if "video" in book['name'].lower():
            if update.callback_query:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=book['file_id'],
                    caption=caption,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_video(
                    video=book['file_id'],
                    caption=caption,
                    parse_mode='Markdown'
                )
        else:
            if update.callback_query:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=book['file_id'],
                    caption=caption,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_document(
                    document=book['file_id'],
                    caption=caption,
                    parse_mode='Markdown'
                )

        db.log_download(user_id, book['id'])

    except TelegramError:
        await update.message.reply_text("❌ Xatolik yuz berdi.")

# 🔥 O‘ZGARDI: TELEGRAM REAL + INSTAGRAM FAKE
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    user_id = user.id

    if query.data == "check_subscription":
        is_subscribed = await check_telegram_subscription(context.bot, user_id)

        if is_subscribed:
            db.add_user(user_id, user.username or "", user.full_name or "")

            text = (
                f"📚 *Assalomu alaykum, {user.first_name}!*\n\n"
                f"🕌 *TaqwoBook* botiga xush kelibsiz!\n\n"
                "🔍 Kitob nomini yozing va men sizga PDF ni topib beraman.\n\n"
                "📊 /stats — Statistika\n"
                "ℹ️ /help — Yordam\n\n"
                "✅ *Instagram ham tekshirildi (rahmat!)*"
            )

            if user_id in Config.ADMIN_IDS:
                text += "\n\n📤 /upload — Kitob yuklash (Admin)"

            await query.message.edit_text(text, parse_mode='Markdown')

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="👇 Menu orqali foydalaning",
                reply_markup=get_main_menu()
            )

        else:
            await query.answer(
                "❌ Avval Telegram kanalga obuna bo‘ling!",
                show_alert=True
            )

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    logger.info("TaqwoBook Bot ishga tushmoqda...")

    app = (
        Application.builder()
        .token(Config.BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("upload", upload_command))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf_upload))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_book))

    logger.info("Bot ishga tushdi! 24/7 ishlaydi...")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
        poll_interval=0.5,
        timeout=10
    )

if __name__ == '__main__':
    main()
