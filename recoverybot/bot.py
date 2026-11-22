import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from database import init_db, add_note, get_notes, get_device

log = logging.getLogger("recoverybot")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = os.getenv("ADMIN_TELEGRAM_ID", "")


def is_admin(update: Update) -> bool:
    user = update.effective_user
    return bool(user and ADMIN_ID and str(user.id) == ADMIN_ID)


async def deny(update: Update):
    if update.message:
        await update.message.reply_text("دسترسی مجاز نیست.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return await deny(update)
    await update.message.reply_text(
        "RecoveryBot فعال است.\n\n"
        "/status - وضعیت عامل گوشی\n"
        "/note متن - ثبت یادداشت غیرمحرمانه\n"
        "/history - آخرین یادداشت‌ها\n"
        "/help - راهنما\n\n"
        "برای امنیت، رمز عبور یا کد ورود را در ربات ارسال نکن."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return await deny(update)
    await update.message.reply_text(
        "این ربات برای ثبت روند بازیابی مجاز است.\n"
        "رمزها را دریافت یا حدس نمی‌زند و روی صفحه ورود تلاش خودکار انجام نمی‌دهد.\n"
        "یادداشت: /note بررسی نسخه پشتیبان انجام شد"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return await deny(update)
    row = get_device("huawei-android")
    if row is None:
        await update.message.reply_text(
            "هنوز گزارشی از گوشی دریافت نشده است. عامل گوشی را اجرا کن."
        )
        return
    await update.message.reply_text(
        "آخرین وضعیت گوشی:\n"
        f"دستگاه: {row['device_id']}\n"
        f"Android: {row['android_version']}\n"
        f"Python: {row['python_version']}\n"
        f"ADB: {row['adb_status']}\n"
        f"آخرین ارتباط (UTC): {row['last_seen']}"
    )


async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return await deny(update)
    value = " ".join(context.args).strip()
    if not value:
        await update.message.reply_text("نمونه: /note بررسی نسخه پشتیبان انجام شد")
        return
    add_note(update.effective_user.id, value)
    await update.message.reply_text("یادداشت ثبت شد؛ هیچ رمز یا اطلاعات ورود ذخیره نشد.")


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return await deny(update)
    rows = get_notes(update.effective_user.id)
    if not rows:
        await update.message.reply_text("هنوز یادداشتی ثبت نشده است.")
        return
    lines = [f"• {r['created_at']} — {r['note']}" for r in rows]
    await update.message.reply_text("\n".join(lines)[:3900])


def build_application():
    if not BOT_TOKEN or not ADMIN_ID:
        raise RuntimeError("Set BOT_TOKEN and ADMIN_TELEGRAM_ID environment variables.")
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("note", note))
    application.add_handler(CommandHandler("history", history))
    return application


def main():
    logging.basicConfig(level=logging.INFO)
    init_db()
    build_application().run_polling()


if __name__ == "__main__":
    main()
