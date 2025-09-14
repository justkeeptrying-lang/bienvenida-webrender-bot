import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import ContextTypes

# =========================
# 🔗 ENLACES CONFIGURABLES
# =========================
CHANNEL_URL  = os.getenv("CHANNEL_URL",  "https://t.me/+jS_YKiiHgcw3OTRh")
GROUP_URL    = os.getenv("GROUP_URL",    "https://t.me/+kL7eSPE27805ZGRh")
SORTEO_URL   = os.getenv("SORTEO_URL",   "https://mundovapo.cl/content/20-bases-de-sorteo")
FORM_URL     = os.getenv("FORM_URL",     "https://docs.google.com/forms/d/e/1FAIpQLSct9QIex5u95sdnaJdXDC4LeB-WBlcdhE7GXoUVh3YvTh_MlQ/viewform")
WHATSAPP_TXT = os.getenv("WHATSAPP_TXT", "+56 9 9324 5860")
WHATSAPP_URL = os.getenv("WHATSAPP_URL", "https://www.mundovapo.cl")

# Nuevos enlaces configurables (puedes cambiarlos fácilmente aquí)
MANTENCION_URL = os.getenv("MANTENCION_URL", "https://mundovapo.cl/content/18-recomendaciones-de-uso")
GUIAS_URL      = os.getenv("GUIAS_URL",      "https://mundovapo.cl/content/10-guias")

# =========================
# 🧩 TECLADOS
# =========================
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
        [InlineKeyboardButton("💨 Recomendaciones de Uso", callback_data="faq_mantencion")],
        [InlineKeyboardButton("📘 Guías y blogs", callback_data="faq_guias")],
        [InlineKeyboardButton("⬅️ Volver al inicio", callback_data="faq_home")]
    ])

# =========================
# ⚙️ FUNCIONES ÚTILES
# =========================
async def safe_edit(cq, text, markup):
    try:
        await cq.edit_message_text(
            text,
            reply_markup=markup,
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML
        )
    except BadRequest as e:
        if "message is not modified" in str(e).lower():
            await cq.answer("Ya estás en este menú.", show_alert=False)
        else:
            raise

def texto_bienvenida(nombre: str) -> str:
    return (
        f"👋 ¡Bienvenid@, {nombre}!\n\n"
        "Nos alegra mucho tenerte por aquí 🌿\n"
        "En plataformas como Instagram nuestras cuentas suelen ser restringidas o eliminadas, "
        "por eso decidimos crear esta comunidad exclusiva para quienes confían en nosotros 💚\n\n"
        "📣 <b>En el canal</b> podrás mantenerte al día con:\n"
        "— Nuevos lanzamientos\n— Descuentos especiales\n— Sorteos mensuales\n— Y mucho más\n\n"
        "💬 <b>En el chat</b> podrás resolver dudas y compartir con una comunidad respetuosa (+18, sin spam).\n\n"
        "🤝 Con tus compras ya estás a medio camino para participar en nuestros sorteos mensuales; "
        "solo necesitas completar el formulario en <b>'Bases del Sorteo'</b>.\n"
    )


# =========================
# 🤖 HANDLERS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = (update.effective_user.first_name or "amig@") if update.effective_user else "amig@"
    await update.message.reply_text(
        texto_bienvenida(nombre),
        reply_markup=kb_principal(),
        disable_web_page_preview=True,
        parse_mode=ParseMode.HTML
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Aquí tienes el menú 👇",
        reply_markup=kb_principal(),
        disable_web_page_preview=True,
        parse_mode=ParseMode.HTML
    )

async def faq_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ <b>Preguntas frecuentes</b>\n\nSelecciona una categoría:",
        reply_markup=kb_faq_menu(),
        disable_web_page_preview=True,
        parse_mode=ParseMode.HTML
    )

async def faq_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cq = update.callback_query
    await cq.answer()
    data = cq.data or "faq_menu"
    nombre = (cq.from_user.first_name or "amig@") if cq.from_user else "amig@"

    if data == "faq_home":
        await safe_edit(cq, texto_bienvenida(nombre), kb_principal())
        return

    if data == "faq_menu":
        await safe_edit(
            cq,
            "❓ <b>Preguntas frecuentes</b>\n\nSelecciona una categoría:",
            kb_faq_menu()
        )
        return

    if data == "faq_envios":
        texto = (
            "✈️ <b>Envíos</b>\n\n"
            "Envíos a todo Chile por courier. Despacho en máximo 48 hrs hábiles.\n"
            "Al enviar, te llegará el tracking por correo.\n\n"
            f"📩 ¿No recibiste el tracking? Escríbenos por WhatsApp: {WHATSAPP_TXT}"
        )
        await safe_edit(cq, texto, kb_faq_menu())
        return

    if data == "faq_garantias":
        texto = (
            "🛠️ <b>Garantías</b>\n\n"
            "Cada artículo tiene garantía de 6 meses en Chile y una garantia internacional dependiendo del fabricante.\n\n"
            "No se cubren daños por mal uso. Para evaluación, completa el formulario y espera respuesta (≤ 48 h hábiles):\n"
            f"🔗 <a href=\"{FORM_URL}\">Formulario de garantía</a>\n\n"
        )
        await safe_edit(cq, texto, kb_faq_menu())
        return

    if data == "faq_mantencion":
        texto = (
            "💨 <b>Recomendaciones de Uso</b>\n\n"
            "Si es tu primera vez, revisa nuestras guías básicas de uso para cada tipo de vaporizador en el siguiente enlace:\n"
            f"🔗 <a href=\"{MANTENCION_URL}\">Guías de mantención</a>"
        )
        await safe_edit(cq, texto, kb_faq_menu())
        return

    if data == "faq_guias":
        texto = (
            "📘 <b>Guías y blogs</b>\n\n"
            "Si necesitas saber más sobre la vaporización en general, no dudes en revisar nuestras guías completas:\n"
            f"🔗 <a href=\"{GUIAS_URL}\">Blog y guías completas</a>"
        )
        await safe_edit(cq, texto, kb_faq_menu())
        return

