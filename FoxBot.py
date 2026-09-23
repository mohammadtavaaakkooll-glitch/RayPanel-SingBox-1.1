import telebot
from telebot import types
import json
import os
from datetime import datetime

BOT_TOKEN = "8977274217:AAEHl5-eq0jyuPsv7zNHjlIr4NOtA0uRtNc"
ADMIN_ID = 7438569833
SUPPORT = "@GenralIran"
CHANNEL = "@FoxShop_IRAN"
CHANNEL_LINK = "https://t.me/FoxShop_IRAN"
CARD = "5054161706012493"
CARD_OWNER = "رابیه آرام"

bot = telebot.TeleBot(BOT_TOKEN)

DB_FILE = "foxshop.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"orders": [], "users": {}}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

db = load_db()

GIFTS = {
    "gol":       ("🌹 گیفت گل",              "130,920"),
    "kado":      ("🎁 گیفت کادو",             "130,920"),
    "khers":     ("🧸 گیفت عروسک خرس",        "90,550"),
    "ghalb":     ("💜 گیفت قلب بنفش",         "90,550"),
    "noshidani": ("🥤 گیفت نوشیدنی",          "231,830"),
    "moshak":    ("🚀 گیفت موشک",             "231,830"),
    "dasgol":    ("💐 گیفت دسته گل",          "231,830"),
    "cake":      ("🎂 گیفت کیک",              "231,830"),
    "jam":       ("🏆 گیفت جام",              "433,650"),
    "almas":     ("💎 گیفت الماس",            "433,650"),
    "angoshtar": ("💍 گیفت انگشتر",           "433,650"),
}

def is_admin(uid):
    return str(uid) == str(ADMIN_ID)

def is_member(uid):
    try:
        member = bot.get_chat_member(CHANNEL, uid)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def check_join(cid, uid):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK))
    markup.add(types.InlineKeyboardButton("✅ عضو شدم", callback_data="check_join"))
    bot.send_message(cid,
        f"⚠️ **برای استفاده از ربات، ابتدا در کانال زیر عضو شوید:**\n\n"
        f"📢 {CHANNEL}\n\n"
        f"سپس روی «عضو شدم» بزنید.",
        reply_markup=markup, parse_mode="Markdown")

def main_menu(cid, uid):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🎁 خرید گیفت", callback_data="buy"),
        types.InlineKeyboardButton("⭐ خرید استارز", callback_data="stars"),
        types.InlineKeyboardButton("📞 پشتیبانی", callback_data="support"),
        types.InlineKeyboardButton("📦 سفارشات من", callback_data="myorders"),
    )
    if is_admin(uid):
        markup.add(types.InlineKeyboardButton("👑 پنل ادمین", callback_data="admin"))
    
    bot.send_message(cid,
        "🦊 **به FoxShop خوش آمدید**\n\n"
        "⚡️ گیفت و استارز تلگرام\n"
        "✅ ارسال سریع و مطمئن\n"
        "✅ پشتیبانی ۲۴ ساعته\n\n"
        "از دکمه‌های زیر استفاده کنید:",
        reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    
    if not is_member(message.from_user.id):
        check_join(message.chat.id, message.from_user.id)
        return
    
    if uid not in db["users"]:
        db["users"][uid] = {
            "name": message.from_user.first_name,
            "username": message.from_user.username or "",
            "joined": str(datetime.now()),
            "carts": {}
        }
        save_db(db)
    
    main_menu(message.chat.id, message.from_user.id)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    cid = call.message.chat.id
    uid = str(call.from_user.id)

    if call.data == "check_join":
        if is_member(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ عضویت تایید شد!")
            try:
                bot.delete_message(cid, call.message.message_id)
            except:
                pass
            if uid not in db["users"]:
                db["users"][uid] = {
                    "name": call.from_user.first_name,
                    "username": call.from_user.username or "",
                    "joined": str(datetime.now()),
                    "carts": {}
                }
                save_db(db)
            main_menu(cid, call.from_user.id)
        else:
            bot.answer_callback_query(call.id, "❌ هنوز عضو نشدی!", show_alert=True)
        return

    if not is_member(call.from_user.id):
        check_join(cid, call.from_user.id)
        return

    if call.data == "buy":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, (name, price) in GIFTS.items():
            markup.add(types.InlineKeyboardButton(f"{name} - {price} تومان", callback_data=f"gift_{key}"))
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back"))
        bot.edit_message_text("🎁 **لیست گیفت‌ها:**\n\nیکی رو انتخاب کن:",
            cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("gift_"):
        key = call.data.replace("gift_", "")
        if key not in GIFTS:
            return
        name, price = GIFTS[key]
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("👤 شخصی", callback_data=f"user_{key}"),
            types.InlineKeyboardButton("📢 کانال", callback_data=f"channel_{key}"),
        )
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="buy"))
        
        bot.edit_message_text(
            f"🎁 **{name}**\n"
            f"💰 قیمت: **{price}** تومان\n\n"
            f"گیفت رو برای **شخصی** میخوای یا **کانال**؟",
            cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("user_") or call.data.startswith("channel_"):
        parts = call.data.split("_", 1)
        target_type = "شخصی" if parts[0] == "user" else "کانال"
        key = parts[1]
        name, price = GIFTS.get(key, ("نامشخص", "0"))
        
        bot.send_message(cid,
            f"🎁 **{name}**\n"
            f"💰 قیمت: **{price}** تومان\n"
            f"📬 نوع: **{target_type}**\n\n"
            f"لطفاً **آیدی عددی یا لینک** {target_type} رو بفرست:")
        
        bot.register_next_step_handler_by_chat_id(cid, lambda m: get_target(m, key, name, price, target_type))

    elif call.data == "stars":
        bot.send_message(cid, "⭐ **خرید استارز**\n\nتعداد استارز مورد نظر رو بفرست (مثلاً 500):")
        bot.register_next_step_handler_by_chat_id(cid, get_stars)

    elif call.data == "support":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back"))
        bot.edit_message_text(
            f"📞 **پشتیبانی FoxShop**\n\n"
            f"🆔 {SUPPORT}\n\n"
            f"⏳ پاسخگویی ۲۴ ساعته",
            cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "myorders":
        user_orders = [o for o in db["orders"] if o["user_id"] == uid]
        if not user_orders:
            text = "📦 **سفارشات شما:**\n\nهنوز سفارشی ثبت نکردید."
        else:
            text = "📦 **سفارشات شما:**\n\n"
            for i, o in enumerate(user_orders[-5:], 1):
                text += f"{i}. {o['gift']} | {o['price']} تومان | {o['status']}\n"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back"))
        bot.edit_message_text(text, cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "back":
        try:
            bot.delete_message(cid, call.message.message_id)
        except:
            pass
        main_menu(cid, call.from_user.id)

    elif call.data == "admin":
        if not is_admin(uid):
            bot.answer_callback_query(call.id, "❌ دسترسی ندارید!", show_alert=True)
            return
        admin_panel(cid, call.message.message_id)

    elif call.data.startswith("pay_"):
        key = call.data.replace("pay_", "")
        cart = db["users"].get(uid, {}).get("carts", {}).get(key)
        if not cart:
            bot.answer_callback_query(call.id, "❌ سبد خرید خالی!", show_alert=True)
            return
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📸 ارسال رسید", callback_data=f"receipt_{key}"),
            types.InlineKeyboardButton("❌ لغو", callback_data="back"),
        )
        
        bot.edit_message_text(
            f"💳 **پرداخت**\n\n"
            f"🎁 {cart['name']}\n"
            f"💰 مبلغ: **{cart['price']}** تومان\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💳 **شماره کارت:**\n"
            f"`{CARD}`\n"
            f"به نام: **{CARD_OWNER}**\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"⚠️ **مبلغ کاملاً باید درست باشه!**\n"
            f"هرگونه مبلغ اشتباه جواب داده نمیشود.\n\n"
            f"بعد از واریز، رسید رو ارسال کن:",
            cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("receipt_"):
        key = call.data.replace("receipt_", "")
        bot.send_message(cid, "📸 **لطفاً عکس رسید رو ارسال کن:**")
        bot.register_next_step_handler_by_chat_id(cid, lambda m: save_receipt(m, key))

    elif call.data.startswith("approve_") or call.data.startswith("reject_"):
        if not is_admin(uid):
            return
        parts = call.data.split("_")
        action = parts[0]
        order_index = int(parts[1])
        
        if order_index >= len(db["orders"]):
            return
        
        order = db["orders"][order_index]
        user_id = order["user_id"]
        
        if action == "approve":
            order["status"] = "تایید شده"
            save_db(db)
            bot.send_message(ADMIN_ID, f"✅ سفارش {order['gift']} تایید شد.\n\n🆔 آیدی: `{user_id}`", parse_mode="Markdown")
            try:
                bot.send_message(int(user_id),
                    f"✅ **سفارش شما تایید شد!**\n\n"
                    f"🎁 {order['gift']}\n"
                    f"📬 ارسال به: `{order['target']}`\n\n"
                    f"به زودی گیفت شما ارسال میشود.",
                    parse_mode="Markdown")
            except:
                pass
        else:
            order["status"] = "رد شده"
            save_db(db)
            bot.send_message(ADMIN_ID, f"❌ سفارش {order['gift']} رد شد.")
            try:
                bot.send_message(int(user_id), f"❌ سفارش شما رد شد.\n\n📞 پشتیبانی: {SUPPORT}")
            except:
                pass
        
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except:
            pass

def get_target(message, key, name, price, target_type):
    uid = str(message.from_user.id)
    target_id = message.text.strip()
    if not target_id:
        bot.send_message(message.chat.id, "❌ آیدی نامعتبر!")
        return
    
    if "carts" not in db["users"][uid]:
        db["users"][uid]["carts"] = {}
    
    db["users"][uid]["carts"][key] = {
        "name": name,
        "price": price,
        "target": target_id,
        "type": target_type
    }
    save_db(db)
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💳 پرداخت", callback_data=f"pay_{key}"),
        types.InlineKeyboardButton("❌ لغو", callback_data="back"),
    )
    
    bot.send_message(message.chat.id,
        f"✅ **آیدی ثبت شد!**\n\n"
        f"🎁 گیفت: **{name}**\n"
        f"💰 قیمت: **{price}** تومان\n"
        f"📬 نوع: **{target_type}**\n"
        f"🆔 آیدی: `{target_id}`\n\n"
        f"برای پرداخت روی دکمه زیر بزن:",
        reply_markup=markup, parse_mode="Markdown")

def get_stars(message):
    try:
        count = int(message.text.strip())
        price = count * 8073
        price_str = f"{price:,}"
        
        uid = str(message.from_user.id)
        if "carts" not in db["users"][uid]:
            db["users"][uid]["carts"] = {}
        
        db["users"][uid]["carts"]["stars"] = {
            "name": f"⭐ {count} استارز",
            "price": price_str,
            "target": uid,
            "type": "شخصی"
        }
        save_db(db)
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("💳 پرداخت", callback_data="pay_stars"),
            types.InlineKeyboardButton("❌ لغو", callback_data="back"),
        )
        
        bot.send_message(message.chat.id,
            f"⭐ **{count} استارز**\n"
            f"💰 قیمت: **{price_str}** تومان\n\n"
            f"برای پرداخت روی دکمه زیر بزن:",
            reply_markup=markup, parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, "❌ عدد نامعتبر!")

def save_receipt(message, key):
    if message.content_type not in ['photo', 'document']:
        bot.send_message(message.chat.id, "❌ لطفاً **عکس رسید** ارسال کن!")
        return
    
    uid = str(message.from_user.id)
    cart = db["users"].get(uid, {}).get("carts", {}).get(key)
    if not cart:
        return
    
    order = {
        "user_id": uid,
        "user_name": message.from_user.first_name,
        "username": message.from_user.username or "",
        "gift": cart["name"],
        "price": cart["price"],
        "target": cart["target"],
        "type": cart["type"],
        "status": "در انتظار تایید",
        "date": str(datetime.now())
    }
    db["orders"].append(order)
    del db["users"][uid]["carts"][key]
    save_db(db)
    
    bot.send_message(message.chat.id,
        "✅ **رسید شما دریافت شد!**\n\n"
        "⏳ پس از بررسی، سفارش شما انجام میشود.\n"
        f"📞 پشتیبانی: {SUPPORT}",
        parse_mode="Markdown")
    
    admin_text = (
        f"🔔 **سفارش جدید!**\n\n"
        f"👤 کاربر: {message.from_user.first_name}\n"
        f"🆔 آیدی عددی: `{uid}`\n"
        f"📛 یوزرنیم: @{message.from_user.username or 'ندارد'}\n\n"
        f"🎁 گیفت: **{cart['name']}**\n"
        f"💰 قیمت: **{cart['price']}** تومان\n"
        f"📬 نوع: **{cart['type']}**\n"
        f"🆔 آیدی هدف: `{cart['target']}`\n\n"
        f"⏳ منتظر تایید شما"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ تایید", callback_data=f"approve_{len(db['orders'])-1}"),
        types.InlineKeyboardButton("❌ رد", callback_data=f"reject_{len(db['orders'])-1}"),
    )
    
    try:
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        bot.send_message(ADMIN_ID, admin_text, reply_markup=markup, parse_mode="Markdown")
    except:
        pass

def admin_panel(cid, msg_id=None):
    total_orders = len(db["orders"])
    pending = len([o for o in db["orders"] if o["status"] == "در انتظار تایید"])
    approved = len([o for o in db["orders"] if o["status"] == "تایید شده"])
    users = len(db["users"])
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📦 سفارشات", callback_data="admin_orders"),
        types.InlineKeyboardButton("👥 کاربران", callback_data="admin_users"),
        types.InlineKeyboardButton("📊 آمار", callback_data="admin_stats"),
        types.InlineKeyboardButton("📨 پیام همگانی", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("🔙 بازگشت", callback_data="back"),
    )
    
    text = (
        f"👑 **پنل ادمین FoxShop**\n\n"
        f"📦 کل سفارشات: **{total_orders}**\n"
        f"⏳ در انتظار: **{pending}**\n"
        f"✅ تایید شده: **{approved}**\n"
        f"👥 کاربران: **{users}**"
    )
    
    if msg_id:
        bot.edit_message_text(text, cid, msg_id, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(cid, text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_callbacks(call):
    cid = call.message.chat.id
    uid = str(call.from_user.id)
    if not is_admin(uid):
        return
    
    if call.data == "admin_orders":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin"))
        text = "📦 **آخرین سفارشات:**\n\n"
        for o in db["orders"][-10:]:
            text += f"• {o['gift']} | {o['price']} | {o['status']}\n🆔 `{o['user_id']}`\n\n"
        if not db["orders"]:
            text = "📦 هیچ سفارشی ثبت نشده."
        bot.edit_message_text(text, cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    
    elif call.data == "admin_users":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin"))
        text = f"👥 **کاربران:** {len(db['users'])}\n\n"
        for uid_key, u in list(db["users"].items())[-10:]:
            text += f"• {u['name']} | `{uid_key}`\n"
        bot.edit_message_text(text, cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    
    elif call.data == "admin_stats":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin"))
        text = (
            f"📊 **آمار FoxShop**\n\n"
            f"👥 کاربران: **{len(db['users'])}**\n"
            f"📦 سفارشات: **{len(db['orders'])}**\n"
            f"⏳ در انتظار: **{len([o for o in db['orders'] if o['status'] == 'در انتظار تایید'])}**\n"
            f"✅ تایید شده: **{len([o for o in db['orders'] if o['status'] == 'تایید شده'])}**"
        )
        bot.edit_message_text(text, cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    
    elif call.data == "admin_broadcast":
        bot.send_message(cid, "📨 **پیام همگانی** رو بفرست:")
        bot.register_next_step_handler_by_chat_id(cid, do_broadcast)

def do_broadcast(message):
    if not is_admin(str(message.from_user.id)):
        return
    count = 0
    for uid in db["users"].keys():
        try:
            bot.send_message(int(uid), message.text)
            count += 1
        except:
            pass
    bot.send_message(message.chat.id, f"✅ پیام به **{count}** کاربر ارسال شد.")

@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    if not is_admin(str(message.from_user.id)):
        return
    admin_panel(message.chat.id)

print("🦊 FoxShop Bot is running...")
bot.infinity_polling()
