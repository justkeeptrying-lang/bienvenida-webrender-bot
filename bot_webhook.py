
import os, logging
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler
)
from handlers import start, help_cmd, faq_cmd, faq_router

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s | %(message)s", level=logging.INFO)
log = logging.getLogger("mundovapo-bot")

TOKEN = "8375588470:AAHM8HX5_Z0wq4qHEglmB9sJ6el3DTy5dEM"
BASE_URL = "https://mv-bienvenida-web-bot.onrender.com"
WEBHOOK_SECRET = "wee895623"
PORT = int(os.getenv("PORT", "8080"))

application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help",  help_cmd))
application.add_handler(CommandHandler("faq",   faq_cmd))
application.add_handler(CallbackQueryHandler(faq_router, pattern="^faq"))

routes = web.RouteTableDef()

@routes.post("/telegram")
async def telegram(request: web.Request):
    if WEBHOOK_SECRET and request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        return web.Response(status=401, text="Unauthorized")
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.update_queue.put(update)
    return web.Response(text="OK")

async def on_startup(app: web.Application):
    await application.start()
    await application.bot.set_webhook(
        url=f"{BASE_URL}/telegram",
        secret_token=WEBHOOK_SECRET,
        drop_pending_updates=True,
    )
    log.info("✅ Webhook registrado.")

async def on_cleanup(app: web.Application):
    await application.bot.delete_webhook()
    await application.stop()

app = web.Application()
app.add_routes(routes)
app.on_startup.append(on_startup)
app.on_cleanup.append(on_cleanup)

if __name__ == "__main__":
    web.run_app(app, port=PORT)
