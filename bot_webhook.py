import os, logging
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler
)
from handlers import start, help_cmd, faq_cmd, faq_router

# ===== LOG =====
logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s | %(message)s", level=logging.INFO)
log = logging.getLogger("mundovapo-bot")

# ===== ENV =====
TOKEN = os.getenv("BOT_TOKEN", "")
BASE_URL = os.getenv("BASE_URL", "")  # p.ej. https://mv-bienvenida-web-bot.onrender.com
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "mv-secret")
PORT = int(os.getenv("PORT", "8080"))

if not TOKEN or not BASE_URL:
    raise SystemExit("⚠️ Define BOT_TOKEN y BASE_URL en variables de entorno.")

# ===== TELEGRAM APP =====
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help",  help_cmd))
application.add_handler(CommandHandler("faq",   faq_cmd))
application.add_handler(CallbackQueryHandler(faq_router, pattern="^faq"))

# ===== AIOHTTP SERVER =====
routes = web.RouteTableDef()

@routes.post("/telegram")
async def telegram(request: web.Request):
    # Valida el secret header
    if WEBHOOK_SECRET and request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        return web.Response(status=401, text="Unauthorized")

    data = await request.json()
    update = Update.de_json(data, application.bot)
    # Entrega el update a la cola del Application (ya inicializado y arrancado en on_startup)
    await application.update_queue.put(update)
    return web.Response(text="OK")

async def on_startup(app: web.Application):
    # Orden correcto en PTB 21.x embebido
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(
        url=f"{BASE_URL}/telegram",
        secret_token=WEBHOOK_SECRET,
        drop_pending_updates=True,
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

