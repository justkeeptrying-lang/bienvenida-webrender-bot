
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import ContextTypes

CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/+jS_YKiiHgcw3OTRh")
GROUP_URL   = os.getenv("GROUP_URL",   "https://t.me/+kL7eSPE27805ZGRh")
SORTEO_URL  = os.getenv("SORTEO_URL",  "https://www.mundovapo.cl")
FORM_URL    = os.getenv("FORM_URL",    "https://docs.google.com/forms/d/e/1FAIpQLSct9QIex5u95sdnaJdXDC4LeB-WBlcdhE7GXoUVh3YvTh_MlQ/viewform")
WHATSAPP_TXT= os.getenv("WHATSAPP_TXT","+56 9 9324 5860")
WHATSAPP_URL= os.getenv("WHATSAPP_URL","https://www.mundovapo.cl")

def kb_principal():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📣 Canal", url=CHANNEL_URL),
         InlineKeyboardButton("💬 Chat",  url=GROUP_URL)],
        [InlineKeyboardButton("📋 Bases del sorteo", url=SORTEO_URL)],
        [InlineKeyboardButton("❓ Preguntas frecuentes", callback_data="faq_menu")],
        [InlineKeyboardButton("🟢📱 Atención por WhatsApp", url=WHATSAPP_URL)]
    ])

def kb_faq_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚚 Envíos", callback_data="faq_envios")],
        [InlineKeyboardButton("🛠️ Garantías", callback_data="faq_garantias")],
        [InlineKeyboardButton("⬅️ Volver al inicio", callback_data="faq_home")]
    ])

async def safe_edit(cq, text, markup):
    try:
        await cq.edit_message_text(text, reply_markup=markup,
                                   disable_web_page_preview=True, parse_mode=ParseMode.HTML)
    except BadRequest as e:
        if "message is not modified" in str(e).lower():
            await cq.answer("Ya estás en este menú.", show_alert=False)
        else:
            raise

def texto_bienvenida(nombre):
    return (
        f"👋 ¡Bienvenid@, {nombre}!

"
        "Nos alegra mucho tenerte por aquí 🌿
"
        "En plataformas como Instagram es muy difícil mantener una cuenta dedicada a vaporizadores, "
        "por eso decidimos crear esta comunidad exclusiva para quienes confían en nosotros 💚

"
        "📣 <b>En el canal</b> podrás estar al tanto de:
"
        "— Nuevos lanzamientos
— Descuentos especiales
— Sorteos mensuales
— Y más

"
        "💬 <b>En el chat</b> puedes resolver dudas y participar en una comunidad respetuosa (+18, sin spam).

"
        "Gracias por tu compra 🤝 Ya estás participando en el sorteo mensual.
"
        "Revisa las bases y formulario en el enlace 👇"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = (update.effective_user.first_name or "amig@") if update.effective_user else "amig@"
    await update.message.reply_text(
        texto_bienvenida(nombre),
        reply_markup=kb_principal(),
        disable_web_page_preview=True, parse_mode=ParseMode.HTML
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Aquí tienes el menú 👇",
        reply_markup=kb_principal(),
        disable_web_page_preview=True, parse_mode=ParseMode.HTML
    )

async def faq_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ <b>Preguntas frecuentes</b>

Selecciona una categoría:",
        reply_markup=kb_faq_menu(),
        disable_web_page_preview=True, parse_mode=ParseMode.HTML
    )

async def faq_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cq = update.callback_query
    await cq.answer()
    data = cq.data or "faq_menu"
    nombre = (cq.from_user.first_name or "amig@") if cq.from_user else "amig@"

    if data == "faq_home":
        await safe_edit(cq, texto_bienvenida(nombre), kb_principal()); return

    if data == "faq_menu":
        await safe_edit(cq, "❓ <b>Preguntas frecuentes</b>

Selecciona una categoría:", kb_faq_menu()); return

    if data == "faq_envios":
        texto = (
            "✈️ <b>Envíos</b>

"
            "Envíos a todo Chile por courier. Despacho en máximo 48 h hábiles.
"
            "Al enviar, te llegará el tracking por correo.

"
            f"📩 ¿No recibiste el tracking? Escríbenos por WhatsApp: {WHATSAPP_TXT}"
        )
        await safe_edit(cq, texto, kb_faq_menu()); return

    if data == "faq_garantias":
        texto = (
            "🛠️ <b>Garantías</b>

"
            "Cada artículo tiene garantía original del fabricante (ver descripción del producto).

"
            "No cubre daños por mal uso. Para evaluación, completa el formulario y espera respuesta (≤ 48 h hábiles):
"
            f"🔗 <a href=\"{FORM_URL}\">Formulario de garantía</a>

"
            "📬 Soporte: <a href=\"mailto:soporte@mundovapo.cl\">soporte@mundovapo.cl</a> o WhatsApp."
        )
        await safe_edit(cq, texto, kb_faq_menu()); return
