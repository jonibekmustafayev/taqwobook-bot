# 📚 TaqwoBook Bot — To'liq O'rnatish Yo'riqnomasi

## 🗂️ Fayl tuzilmasi
```
taqwobook_bot/
├── bot.py           ← Asosiy bot kodi
├── database.py      ← Ma'lumotlar bazasi
├── config.py        ← Sozlamalar
├── requirements.txt ← Kutubxonalar
├── Procfile         ← Railway uchun
└── railway.toml     ← Railway konfiguratsiya
```

---

## 1️⃣ Bot Token olish (BotFather)

1. Telegramda **@BotFather** ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomi: `TaqwoBook`
4. Bot username: `TaqwobookBot` (yoki bo'sh bo'lsa)
5. **Token** ni nusxalab oling: `7xxxxxxxxx:AAF...`

---

## 2️⃣ O'z Telegram ID sini bilish

1. Telegramda **@userinfobot** ga yozing
2. `/start` bosing
3. **Id:** `123456789` — shu raqam sizning admin ID ingiz

---

## 3️⃣ Telegram kanalga bot qo'shish

1. **@mufarridbook** kanalingizga kiring
2. Kanal sozlamalari → Adminlar → Admin qo'shish
3. Botni admin qiling: `@TaqwobookBot`
4. **Faqat "Xabarlarni o'qish" ruxsati yetarli**

---

## 4️⃣ GitHub ga yuklash (bepul)

1. [github.com](https://github.com) ga kiring, akkaunt oching
2. "New repository" bosing: `taqwobook-bot` nomi bilan
3. Barcha fayllarni yuklang:
   - `bot.py`, `database.py`, `config.py`
   - `requirements.txt`, `Procfile`, `railway.toml`

---

## 5️⃣ Railway.app da deploy (24/7 bepul)

### A) Akkaunt ochish:
1. [railway.app](https://railway.app) → **GitHub bilan kiring**

### B) Project yaratish:
1. **"New Project"** bosing
2. **"Deploy from GitHub repo"** tanlang
3. `taqwobook-bot` repo ni tanlang

### C) Environment Variables qo'shish:
Railway dashboard → **Variables** bo'limiga kiring va qo'shing:

| Variable nomi | Qiymati |
|---------------|---------|
| `BOT_TOKEN` | `7xxxxxxxxx:AAF...` (BotFather dan) |
| `ADMIN_IDS` | `123456789` (sizning Telegram ID) |

### D) Deploy:
1. Variables saqlangandan keyin **"Deploy"** avtomatik boshlanadi
2. 2-3 daqiqa kutiladi
3. ✅ **Bot 24/7 ishlaydi!** Hech qanday noutbuk kerak emas!

---

## 6️⃣ Bot ga kitob qo'shish (Admin sifatida)

1. Botga `/upload` yozing
2. PDF faylni yuboring
3. Caption (izohat) ga kitob nomini yozing
4. ✅ Kitob bazaga qo'shildi!

**Misol:** PDF ni yuboring, caption: `Sahih Al-Buxoriy`

---

## 7️⃣ Bot funksiyalari

| Buyruq | Tavsif |
|--------|---------|
| `/start` | Botni boshlash |
| `/help` | Yordam |
| `/stats` | Statistika |
| `/upload` | Kitob yuklash (admin) |
| Kitob nomi | PDF qidirish va yuborish |

---

## ✅ Tekshirish

Bot ishlayaptimi:
1. Botga `/start` yuboring
2. Obuna so'ransa → obuna bo'ling → ✅ tugmasini bosing
3. Kitob nomini yozing → PDF kelishi kerak

---

## 🆘 Muammo bo'lsa

**Bot javob bermayapti:**
- Railway → Deployments → Logs ni tekshiring
- `BOT_TOKEN` to'g'ri ekanligini tekshiring

**"Bot kanal adminiga qo'shilmagan":**
- Botni @mufarridbook kanaliga admin sifatida qo'shing

**Kitob topilmayapti:**
- Admin sifatida `/upload` bilan PDF qo'shing
