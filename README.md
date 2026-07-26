# Clever Minds Mafia — نسخه 0.3

این نسخه شامل موارد زیر است:

- ساخت بازی با کد چهاررقمی
- سناریوهای بازپرس، مذاکره و عقرب
- ثبت درخواست ورود بازیکن
- تأیید یا رد بازیکن توسط گرداننده
- اختصاص خودکار شماره صندلی
- یک پنل زنده برای گرداننده
- انتقال گردانندگی به بازیکن تأییدشده
- شروع بازی فقط با ۱۰ بازیکن تأییدشده
- ساختار ماژولار و قابل توسعه

## تنظیمات Render

Environment Variables:

- `BOT_TOKEN`
- `WEBHOOK_URL=https://clevermindsbot.onrender.com`
- `PYTHON_VERSION=3.11.9`

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
python bot.py
```

## نکته مهم

اطلاعات فعلاً داخل حافظه موقت ذخیره می‌شوند؛ بنابراین با ری‌استارت Render بازی‌ها پاک می‌شوند.
مرحله بعد اتصال PostgreSQL است.
