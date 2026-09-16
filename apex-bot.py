import telebot
from telebot import types
import json
import os
from datetime import datetime

BOT_TOKEN = "8933383298:AAGIVO89LhPeTfRwSd_X7vMQ1eKURBdsnSM"
ADMIN_ID = 8485844128
ADMIN_USERNAME = "@M4mmmmmmmmmmm"
CHANNEL_USERNAME = "@Apex_0Vpn"
CHANNEL_LINK = "https://t.me/Apex_0Vpn"
CARD_NUMBER = "5054161706012493"
CARD_OWNER = "رابیه آرام"

bot = telebot.TeleBot(BOT_TOKEN)

# ===== دیتابیس =====
DB_FILE = "users.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "configs": [], "receipts": [], "temp_configs": {}}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

db = load_db()

# ===== بررسی عضویت =====
def is_member(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID)

# ===== منوی اصلی =====
def show_main_menu(cid, user_id=None):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🎁 اکانت تست", callback_data="test"),
        types.InlineKeyboardButton("🛒 خرید اشتراک", callback_data="buy"),
        types.InlineKeyboardButton("👥 دعوت دوستان", callback_data="referral"),
        types.InlineKeyboardButton("💳 واریز", callback_data="deposit"),
        types.InlineKeyboardButton("📊 وضعیت", callback_data="status"),
        types.InlineKeyboardButton("📞 پشتیبانی", callback_data="support"),
    )
    if user_id and is_admin(user_id):
        markup.add(types.InlineKeyboardButton("👑 پنل ادمین", callback_data="admin_panel"))
    bot.send_message(cid, "🔥 **به ربات APEX VPN خوش آمدید**\n\nاز دکمه‌های زیر استفاده کنید:", reply_markup=markup, parse_mode="Markdown")

# ===== Start =====
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    args = message.text.split()
    
    if not is_member(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📡 عضویت در کانال", url=CHANNEL_LINK))
        markup.add(types.InlineKeyboardButton("✅ عضو شدم", callback_data="check_join"))
        bot.send_message(message.chat.id, f"⚠️ برای استفاده از ربات، ابتدا در کانال زیر عضو شوید:\n\n📡 {CHANNEL_USERNAME}\n\nسپس روی «عضو شدم» بزنید.", reply_markup=markup)
        return
    
    if uid not in db["users"]:
        ref_by = None
        if len(args) > 1 and args[1].startswith("ref_"):
            ref_by = args[1].replace("ref_", "")
        
        db["users"][uid] = {
            "name": message.from_user.first_name,
            "username": message.from_user.username or "",
            "joined": str(datetime.now()),
            "test_used": False,
            "refs": 0,
            "ref_by": ref_by
        }
        
        if ref_by and ref_by in db["users"]:
            db["users"][ref_by]["refs"] = db["users"][ref_by].get("refs", 0) + 1
            refs = db["users"][ref_by]["refs"]
            if refs % 5 == 0:
                bot.send_message(int(ref_by), f"🎉 **تبریک!**\n\nشما به **{refs}** دعوت رسیدید!\n🎁 **۱۰ گیگ رایگان** به شما تعلق گرفت!\n\nبرای دریافت، با پشتیبانی تماس بگیرید: {ADMIN_USERNAME}")
        save_db(db)
    
    show_main_menu(message.chat.id, message.from_user.id)

# ===== Callbacks =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    cid = call.message.chat.id
    uid = str(call.from_user.id)

    if call.data == "check_join":
        if is_member(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ عضویت تایید شد!")
            bot.delete_message(cid, call.message.message_id)
            if uid not in db["users"]:
                db["users"][uid] = {
                    "name": call.from_user.first_name,
                    "username": call.from_user.username or "",
                    "joined": str(datetime.now()),
                    "test_used": False,
                    "refs": 0,
                    "ref_by": None
                }
                save_db(db)
            show_main_menu(cid, call.from_user.id)
        else:
            bot.answer_callback_query(call.id, "❌ هنوز عضو نشدی!", show_alert=True)
        return

    # ===== اکانت تست =====
    if call.data == "test":
        if db["users"].get(uid, {}).get("test_used", False):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back"))
            bot.edit_message_text("❌ **شما قبلاً از اکانت تست استفاده کرده‌اید!**\n\nهر کاربر فقط یک بار می‌تواند اکانت تست دریافت کند.", cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
            return

        if not db["configs"]:
            bot.answer_callback_query(call.id, "❌ در حال حاضر کانفیگ تست موجود نیست!", show_alert=True)
            return

        config = db["configs"][0]
        db["configs"].pop(0)
        db["users"][uid]["test_used"] = True
        save_db(db)

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back"))
        bot.edit_message_text(
            f"🎁 **اکانت تست شما:**\n\n"
            f"`{config}`\n\n"
            f"📌 حجم: **۵۰۰ مگابایت**\n"
            f"⏳ مدت: **۲۴ ساعت**\n\n"
            f"📱 کانفیگ رو کپی کن و توی **V2Ray** یا **NPV Tunnel** ایمپورت کن.\n"
            f"⚠️ این اکانت فقط یک بار قابل دریافت است.",
            cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown"
        )

    # ===== پنل ادمین =====
    elif call.data == "admin_panel":
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "❌ شما ادمین نیستید!", show_alert=True)
            return

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📤 ارسال کانفیگ جدید", callback_data="admin_send_config"),
            types.InlineKeyboardButton("📊 آمار ربات", callback_data="admin_stats"),
            types.InlineKeyboardButton("📦 تعداد کانفیگ‌ها", callback_data="admin_config_count"),
            types.InlineKeyboardButton("🗑️ حذف همه کانفیگ‌ها", callback_data="admin_clear_configs"),
            types.InlineKeyboardButton("📨 ارسال پیام همگانی", callback_data="admin_broadcast"),
            types.InlineKeyboardButton("🔙 بازگشت", callback_data="back"),
        )
        bot.edit_message_text("👑 **پنل ادمین APEX VPN**\n\nاز دکمه‌های زیر استفاده کنید:", cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    # ===== شروع ارسال کانفیگ =====
    elif call.data == "admin_send_config":
        if not is_admin(call.from_user.id):
            return
        
        # ===== پاک کردن لیست موقت =====
        db["temp_configs"][str(call.from_user.id)] = []
        save_db(db)
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("✅ تایید و ذخیره", callback_data="admin_confirm_configs"),
            types.InlineKeyboardButton("❌ لغو", callback_data="admin_cancel_configs"),
        )
        
        bot.edit_message_text(
            "📤 **ارسال کانفیگ جدید**\n\n"
            "کانفیگ‌ها را **یکی‌یکی** بفرستید.\n"
            "هر کانفیگ رو که فرستادید، ربات ذخیره میکنه.\n"
            "وقتی همه رو فرستادید، روی **✅ تایید و ذخیره** بزنید.\n\n"
            "⚠️ هر کانفیگ باید **توی یه پیام جدا** باشه.",
            cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown"
        )
        bot.register_next_step_handler_by_chat_id(cid, handle_single_config)

    # ===== تایید کانفیگ‌ها =====
    elif call.data == "admin_confirm_configs":
        if not is_admin(call.from_user.id):
            return
        
        temp = db["temp_configs"].get(str(call.from_user.id), [])
        
        if not temp:
            bot.answer_callback_query(call.id, "❌ هیچ کانفیگی ذخیره نشده!", show_alert=True)
            return
        
        db["configs"].extend(temp)
        db["temp_configs"][str(call.from_user.id)] = []
        save_db(db)
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("👑 بازگشت به پنل ادمین", callback_data="admin_panel"))
        
        bot.edit_message_text(
            f"✅ **{len(temp)} کانفیگ با موفقیت ذخیره شد!**\n\n"
            f"📦 مجموع کانفیگ‌ها: **{len(db['configs'])}**",
            cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown"
        )

    # ===== لغو کانفیگ‌ها =====
    elif call.data == "admin_cancel_configs":
        if not is_admin(call.from_user.id):
            return
        
        db["temp_configs"][str(call.from_user.id)] = []
        save_db(db)
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("👑 بازگشت به پنل ادمین", callback_data="admin_panel"))
        
        bot.edit_message_text(
            "❌ **ارسال کانفیگ لغو شد.**",
            cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown"
        )

    # ===== آمار =====
    elif call.data == "admin_stats":
        if not is_admin(call.from_user.id):
            return
        total_users = len(db["users"])
        total_configs = len(db["configs"])
        total_receipts = len(db.get("receipts", []))
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel"))
        bot.edit_message_text(
            f"📊 **آمار ربات:**\n\n"
            f"👥 کاربران: **{total_users}**\n"
            f"📦 کانفیگ‌های تست: **{total_configs}**\n"
            f"📨 رسیدها: **{total_receipts}**",
            cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown"
        )

    # ===== تعداد کانفیگ =====
    elif call.data == "admin_config_count":
        if not is_admin(call.from_user.id):
            return
        count = len(db["configs"])
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel"))
        bot.edit_message_text(f"📦 **تعداد کانفیگ‌های تست:** **{count}**", cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    # ===== حذف همه کانفیگ‌ها =====
    elif call.data == "admin_clear_configs":
        if not is_admin(call.from_user.id):
            return
        count = len(db["configs"])
        db["configs"] = []
        save_db(db)
        bot.answer_callback_query(call.id, f"✅ {count} کانفیگ حذف شد!", show_alert=True)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel"))
        bot.edit_message_text(f"🗑️ **{count} کانفیگ حذف شد!**", cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    # ===== پیام همگانی =====
    elif call.data == "admin_broadcast":
        if not is_admin(call.from_user.id):
            return
        bot.edit_message_text("📨 **ارسال پیام همگانی**\n\nپیام خود را ارسال کنید:", cid, call.message.message_id)
        bot.register_next_step_handler_by_chat_id(cid, handle_broadcast)

    # ===== خرید =====
    elif call.data == "buy":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📦 ۵ گیگ - ۱۰,۰۰۰ تومان", callback_data="plan_5"),
            types.InlineKeyboardButton("📦 ۲۰ گیگ - ۱۰۰,۰۰۰ تومان", callback_data="plan_20"),
            types.InlineKeyboardButton("📦 ۵۰ گیگ - ۲۰۰,۰۰۰ تومان", callback_data="plan_50"),
            types.InlineKeyboardButton("♾️ نامحدود - ۳۵۰,۰۰۰ تومان", callback_data="plan_unlimited"),
            types.InlineKeyboardButton("🔙 بازگشت", callback_data="back")
        )
        bot.edit_message_text("🛒 **پلن‌های اشتراک:**\n\nیک پلن را انتخاب کنید:", cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("plan_"):
        plan = call.data.split("_")[1]
        plans = {
            "5": ("۵ گیگ", "۱۰,۰۰۰"),
            "20": ("۲۰ گیگ", "۱۰۰,۰۰۰"),
            "50": ("۵۰ گیگ", "۲۰۰,۰۰۰"),
            "unlimited": ("نامحدود", "۳۵۰,۰۰۰")
        }
        name, price = plans.get(plan, ("نامشخص", "۰"))
        text = (
            f"✅ **پلن انتخابی:** {name}\n"
            f"💰 **مبلغ:** {price} تومان\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💳 **شماره کارت:**\n"
            f"`{CARD_NUMBER}`\n"
            f"به نام: **{CARD_OWNER}**\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"📸 پس از واریز، **رسید خود را همینجا ارسال کنید.**"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📤 ارسال رسید", callback_data="send_receipt"))
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="buy"))
        bot.edit_message_text(text, cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    # ===== رفرال =====
    elif call.data == "referral":
        refs = db["users"].get(uid, {}).get("refs", 0)
        remaining = 5 - (refs % 5)
        text = (
            f"👥 **سیستم دعوت دوستان**\n\n"
            f"🔗 **لینک دعوت شما:**\n"
            f"`https://t.me/{(bot.get_me()).username}?start=ref_{uid}`\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎁 **پاداش:**\n"
            f"• هر ۵ نفر دعوت = **۱۰ گیگ رایگان**\n\n"
            f"📊 **تعداد دعوت‌های شما:** {refs}\n"
            f"⏳ **مانده تا پاداش بعدی:** {remaining} نفر\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back"))
        bot.edit_message_text(text, cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    # ===== واریز =====
    elif call.data == "deposit":
        text = (
            "💳 **واریز به حساب**\n\n"
            f"شماره کارت:\n`{CARD_NUMBER}`\n\n"
            f"به نام: **{CARD_OWNER}**\n\n"
            "📸 پس از واریز، رسید خود را ارسال کنید."
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📤 ارسال رسید", callback_data="send_receipt"))
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back"))
        bot.edit_message_text(text, cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "send_receipt":
        bot.send_message(cid, "📸 **لطفاً عکس رسید خود را ارسال کنید.**")
        bot.register_next_step_handler_by_chat_id(cid, handle_receipt)

    # ===== وضعیت =====
    elif call.data == "status":
        text = (
            "📊 **وضعیت سرور:**\n\n"
            "🟢 سرور: **آنلاین**\n"
            "⚡️ سرعت: **بالا**\n"
            "👥 کاربران: **فعال**"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back"))
        bot.edit_message_text(text, cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    # ===== پشتیبانی =====
    elif call.data == "support":
        text = (
            "📞 **پشتیبانی APEX VPN**\n\n"
            f"🆔 {ADMIN_USERNAME}\n\n"
            "⏳ پاسخگویی: **۲۴ ساعته**"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back"))
        bot.edit_message_text(text, cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    # ===== بازگشت =====
    elif call.data == "back":
        bot.delete_message(cid, call.message.message_id)
        show_main_menu(cid, call.from_user.id)

# ===== هندلر دریافت کانفیگ یکی‌یکی =====
def handle_single_config(message):
    if not is_admin(message.from_user.id):
        return
    
    config = message.text.strip() if message.text else ""
    
    if not config:
        bot.reply_to(message, "❌ کانفیگ خالی است! دوباره بفرست:")
        bot.register_next_step_handler(message, handle_single_config)
        return
    
    uid = str(message.from_user.id)
    if uid not in db["temp_configs"]:
        db["temp_configs"][uid] = []
    
    db["temp_configs"][uid].append(config)
    save_db(db)
    
    count = len(db["temp_configs"][uid])
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ تایید و ذخیره", callback_data="admin_confirm_configs"),
        types.InlineKeyboardButton("❌ لغو", callback_data="admin_cancel_configs"),
    )
    
    bot.reply_to(
        message,
        f"✅ **کانفیگ شماره {count} ذخیره شد!**\n\n"
        f"می‌تونی کانفیگ بعدی رو بفرستی، یا روی **✅ تایید و ذخیره** بزنی.",
        reply_markup=markup
    )
    
    bot.register_next_step_handler(message, handle_single_config)

# ===== هندلر پیام همگانی =====
def handle_broadcast(message):
    if not is_admin(message.from_user.id):
        return
    text = message.text or message.caption or ""
    if not text:
        bot.reply_to(message, "❌ پیام خالی است!")
        return
    count = 0
    for uid in db["users"].keys():
        try:
            bot.send_message(int(uid), text)
            count += 1
        except:
            pass
    bot.reply_to(message, f"✅ پیام به **{count}** کاربر ارسال شد!")

# ===== هندلر رسید =====
def handle_receipt(message):
    if message.content_type in ['photo', 'document']:
        bot.send_message(message.chat.id, "✅ **رسید شما دریافت شد!**\n\n⏳ پس از بررسی، اکانت شما ارسال می‌شود.")
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        bot.send_message(ADMIN_ID, f"📸 رسید جدید از {message.from_user.first_name} (@{message.from_user.username})")
        db.setdefault("receipts", []).append({
            "user_id": message.from_user.id,
            "username": message.from_user.username or "",
            "date": str(datetime.now())
        })
        save_db(db)
    else:
        bot.send_message(message.chat.id, "❌ لطفاً **عکس رسید** ارسال کنید.")

# ===== دستور /admin =====
@bot.message_handler(commands=['admin'])
def admin_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ شما ادمین نیستید!")
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📤 ارسال کانفیگ", callback_data="admin_send_config"),
        types.InlineKeyboardButton("📊 آمار", callback_data="admin_stats"),
        types.InlineKeyboardButton("📦 تعداد کانفیگ", callback_data="admin_config_count"),
        types.InlineKeyboardButton("🗑️ حذف کانفیگ‌ها", callback_data="admin_clear_configs"),
        types.InlineKeyboardButton("📨 پیام همگانی", callback_data="admin_broadcast"),
    )
    bot.send_message(message.chat.id, "👑 **پنل ادمین APEX VPN**\n\nاز دکمه‌های زیر استفاده کنید:", reply_markup=markup, parse_mode="Markdown")

# ===== اجرا =====
print("🔥 APEX VPN Bot is running...")
print(f"👑 Admin ID: {ADMIN_ID}")
bot.infinity_polling()
