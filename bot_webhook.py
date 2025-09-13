import os, logging
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
from handlers import start, help_cmd, faq_cmd, faq_router

# ===== LOG =====
logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s | %(message)s", level=logging.INFO)
log = logging.getLogger("mundovapo-bot")

# ===== ENV =====
TOKEN = os.getenv("BOT_TOKEN", "")
BASE_URL = os.getenv("BASE_URL", "")  # ej: https://mv-bienvenida-web-bot.onrender.com
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "mv-secret")
PORT = int(os.getenv("PORT", "8080"))

if not TOKEN or not BASE_URL:
    raise SystemExit("⚠️ Define BOT_TOKEN y BASE_URL en variables de entorno.")

# ===== TELEGRAM APP =====
application = ApplicationBuilder().token(TOKEN).build()

async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.exception("Unhandled error in handler", exc_info=context.error)

application.add_error_handler(on_error)
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help",  help_cmd))
application.add_handler(CommandHandler("faq",   faq_cmd))
application.add_handler(CallbackQueryHandler(faq_router, pattern="^faq"))

# ===== AIOHTTP SERVER =====
routes = web.RouteTableDef()

@routes.get("/")
async def health(request: web.Request):
    return web.Response(text="ok")

# Acepta GET solo para evitar 404 (Telegram o probes). Debe responder 200.
@routes.get("/telegram")
@routes.get("/telegram/")
async def telegram_get(request: web.Request):
    return web.Response(text="OK")

@routes.post("/telegram")
@routes.post("/telegram/")
async def telegram_post(request: web.Request):
    # Valida secret
    header_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if WEBHOOK_SECRET and header_secret != WEBHOOK_SECRET:
        log.warning("Webhook secret mismatch. Got header=%r", header_secret)
        return web.Response(status=401, text="Unauthorized")

    data = await request.json()
    log.info("Incoming update: %s", data)  # confir­ma que llega /start
    update = Update.de_json(data, application.bot)
    await application.update_queue.put(update)
    return web.Response(text="OK")

async def on_startup(app: web.Application):
    await application.initialize()
    await application.start()
    # Registra webhook exactamente en /telegram (sin slash final)
    await application.bot.set_webhook(
        url=f"{BASE_URL}/telegram",
        secret_token=WEBHOOK_SECRET,
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"]
    )
    log.info("✅ Webhook registrado en %s/telegram", BASE_URL)

async def on_cleanup(app: web.Application):
    await application.bot.delete_webhook()
    await application.stop()
    await application.shutdown()

app = web.Application()
app.add_routes(routes)
app.on_startup.append(on_startup)
app.on_cleanup.append(on_cleanup)

if __name__ == "__main__":
    web.run_app(app, port=PORT)

