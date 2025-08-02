import telebot
from telebot import types

API_TOKEN = 'YOUR_BOT_TOKEN'
ADMIN_IDS = [123456789]

bot = telebot.TeleBot(API_TOKEN)

CHANNEL_USERNAME = None
users = {}
referrals = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global CHANNEL_USERNAME
    user_id = message.from_user.id
    if str(user_id) not in users:
        users[str(user_id)] = {'score': 0}
    if CHANNEL_USERNAME:
        if not is_user_in_channel(user_id):
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton("عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME}")
            markup.add(btn)
            bot.reply_to(message, "برای استفاده از ربات ابتدا در کانال عضو شو", reply_markup=markup)
            return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🎲 تاس بنداز")
    btn2 = types.KeyboardButton("👥 زیرمجموعه‌گیری")
    btn3 = types.KeyboardButton("🎁 جایزه بگیر")
    markup.add(btn1, btn2, btn3)
    bot.reply_to(message, "به ربات خوش آمدید!", reply_markup=markup)
    check_referral(message)

def check_referral(message):
    if len(message.text.split()) > 1:
        ref_id = message.text.split()[1]
        if ref_id != str(message.from_user.id) and ref_id in users:
            referrals.setdefault(ref_id, set()).add(str(message.from_user.id))
            users[ref_id]['score'] = len(referrals[ref_id])
            bot.send_message(ref_id, f"کاربر {message.from_user.first_name} با لینک شما عضو شد! امتیاز شما: {users[ref_id]['score']}")

def is_user_in_channel(user_id):
    try:
        member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ['member', 'creator', 'administrator']
    except:
        return False

@bot.message_handler(func=lambda message: message.text == "🎲 تاس بنداز")
def roll_dice(message):
    dice1 = bot.send_dice(message.chat.id).dice.value
    dice2 = bot.send_dice(message.chat.id).dice.value
    dice3 = bot.send_dice(message.chat.id).dice.value
    if dice1 == dice2 == dice3:
        bot.send_message(message.chat.id, "شما برنده شدید! به پیوی ادمین پیام دهید.")
    else:
        bot.send_message(message.chat.id, "متاسفم، شما بازنده شدید. دوباره تلاش کنید!")

@bot.message_handler(func=lambda message: message.text == "👥 زیرمجموعه‌گیری")
def referral_link(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, f"لینک دعوت شما:
https://t.me/{bot.get_me().username}?start={user_id}
تعداد زیرمجموعه‌ها: {users[str(user_id)]['score']}")

@bot.message_handler(func=lambda message: message.text == "🎁 جایزه بگیر")
def gift_game(message):
    user_id = str(message.from_user.id)
    if users[user_id]['score'] >= 5:
        dice = bot.send_dice(message.chat.id).dice.value
        bot.send_message(message.chat.id, f"شما عدد {dice} آوردید و برنده شدید! به پیوی ادمین پیام دهید.")
        users[user_id]['score'] -= 5
    else:
        bot.send_message(message.chat.id, "شما نیاز به 5 امتیاز برای استفاده از این بخش دارید.")

@bot.message_handler(commands=['setchannel'])
def set_channel(message):
    if message.from_user.id in ADMIN_IDS:
        global CHANNEL_USERNAME
        CHANNEL_USERNAME = message.text.split()[1].replace("@", "")
        bot.reply_to(message, f"کانال جوین اجباری تنظیم شد: @{CHANNEL_USERNAME}")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id in ADMIN_IDS:
        msg = message.text.split(' ', 1)[1]
        for uid in users.keys():
            try:
                bot.send_message(uid, msg)
            except:
                pass
        bot.reply_to(message, "پیام به همه کاربران ارسال شد.")

@bot.message_handler(commands=['pm'])
def private_message(message):
    if message.from_user.id in ADMIN_IDS:
        parts = message.text.split(' ', 2)
        uid = parts[1]
        msg = parts[2]
        bot.send_message(uid, msg)
        bot.reply_to(message, "پیام ارسال شد.")

bot.polling()