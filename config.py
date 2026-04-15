import os

class Config:
    # ─── BOT TOKEN ──────────────────────────────────────────────────────────────
    # BotFather dan olingan token
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7991107536:AAF4V0ICumLY0d0iJgMOgl64LEebBLagGRE")

    # ─── KANALLAR ───────────────────────────────────────────────────────────────
    TELEGRAM_CHANNEL = "@mufarridbook"        # Telegram kanal
    INSTAGRAM_USERNAME = "@mufarrid_book"     # Instagram sahifa

    # ─── ADMIN IDs ──────────────────────────────────────────────────────────────
    # @userinfobot ga yozing va o'z ID ingizni qo'ying
    ADMIN_IDS = [
        int(x) for x in os.environ.get("ADMIN_IDS", "6722242402").split(",")
        if x.strip().isdigit()
    ]

    # ─── DATABASE ───────────────────────────────────────────────────────────────
    DB_PATH = "taqwobook.db"
