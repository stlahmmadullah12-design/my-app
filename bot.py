import os
import asyncio

from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, WEBHOOK_URL
from database import (
    init_database,
    create_user,
    get_user,
    get_products
)

app = Flask(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# =========================
# HOME MENU
# =========================

def home_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛍️ Products",
                    callback_data="products"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📦 My Orders",
                    callback_data="orders"
                ),
                InlineKeyboardButton(
                    text="👤 My Account",
                    callback_data="account"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Balance",
                    callback_data="balance"
                ),
                InlineKeyboardButton(
                    text="🎁 Offers",
                    callback_data="offers"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💬 Support",
                    callback_data="support"
                )
            ]
        ]
    )


# =========================
# /START
# =========================

@dp.message(CommandStart())
async def start_handler(message: types.Message):

    user = message.from_user

    create_user(
        telegram_id=user.id,
        username=user.username or "",
        first_name=user.first_name or ""
    )

    await message.answer(
        f"👋 Welcome, {user.first_name}!\n\n"
        "🛍️ Welcome to Salman Premium Store\n\n"
        "Choose an option below:",
        reply_markup=home_keyboard()
    )


# =========================
# CALLBACK HANDLER
# =========================

@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):

    data = callback.data
    user_id = callback.from_user.id

    # PRODUCTS
    if data == "products":

        products = get_products()

        if not products:
            await callback.message.edit_text(
                "🛍️ Products\n\n"
                "বর্তমানে কোনো product available নেই।",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🔙 Back",
                                callback_data="home"
                            )
                        ]
                    ]
                )
            )
            await callback.answer()
            return

        buttons = []

        for product in products:
            product_id, name, description, price, stock = product

            buttons.append([
                InlineKeyboardButton(
                    text=f"🛍️ {name} — ৳{price}",
                    callback_data=f"product_{product_id}"
                )
            ])

        buttons.append([
            InlineKeyboardButton(
                text="🔙 Back",
                callback_data="home"
            )
        ])

        await callback.message.edit_text(
            "🛍️ Available Products\n\n"
            "আপনার পছন্দের product নির্বাচন করুন:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=buttons
            )
        )

    # ACCOUNT
    elif data == "account":

        user = get_user(user_id)

        if user:
            _, telegram_id, username, first_name, balance = user

            text = (
                "👤 My Account\n\n"
                f"Name: {first_name}\n"
                f"Username: @{username if username else 'Not set'}\n"
                f"Balance: ৳{balance}"
            )
        else:
            text = "❌ Account পাওয়া যায়নি। আবার /start দিন।"

        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔙 Back",
                            callback_data="home"
                        )
                    ]
                ]
            )
        )

    # BALANCE
    elif data == "balance":

        user = get_user(user_id)
        balance = user[4] if user else 0

        await callback.message.edit_text(
            f"💰 Your Balance\n\n"
            f"Available Balance: ৳{balance}\n\n"
            "💳 Balance add করতে Support-এ যোগাযোগ করুন।",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="💬 Support",
                            callback_data="support"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🔙 Back",
                            callback_data="home"
                        )
                    ]
                ]
            )
        )

    # ORDERS
    elif data == "orders":

        await callback.message.edit_text(
            "📦 My Orders\n\n"
            "আপনার কোনো order এখনো নেই।",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🛍️ Products",
                            callback_data="products"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🔙 Back",
                            callback_data="home"
                        )
                    ]
                ]
            )
        )

    # OFFERS
    elif data == "offers":

        await callback.message.edit_text(
            "🎁 Special Offers\n\n"
            "🔥 নতুন offers শীঘ্রই আসছে!",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔙 Back",
                            callback_data="home"
                        )
                    ]
                ]
            )
        )

    # SUPPORT
    elif data == "support":

        await callback.message.edit_text(
            "💬 Support\n\n"
            "যেকোনো সমস্যার জন্য Admin-এর সাথে যোগাযোগ করুন।",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔙 Back",
                            callback_data="home"
                        )
                    ]
                ]
            )
        )

    # HOME
    elif data == "home":

        await callback.message.edit_text(
            "🏠 Salman Premium Store\n\n"
            "আপনার প্রয়োজনীয় option নির্বাচন করুন:",
            reply_markup=home_keyboard()
        )

    await callback.answer()


# =========================
# PRODUCT DETAILS
# =========================

@dp.callback_query(lambda c: c.data.startswith("product_"))
async def product_handler(callback: types.CallbackQuery):

    product_id = int(callback.data.split("_")[1])

    products = get_products()

    selected = None

    for product in products:
        if product[0] == product_id:
            selected = product
            break

    if not selected:
        await callback.answer("Product পাওয়া যায়নি!", show_alert=True)
        return

    _, name, description, price, stock = selected

    await callback.message.edit_text(
        f"🛍️ {name}\n\n"
        f"{description}\n\n"
        f"💰 Price: ৳{price}\n"
        f"📦 Stock: {stock}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🛒 Buy Now",
                        callback_data=f"buy_{product_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔙 Products",
                        callback_data="products"
                    )
                ]
            ]
        )
    )

    await callback.answer()


# =========================
# BUY
# =========================

@dp.callback_query(lambda c: c.data.startswith("buy_"))
async def buy_handler(callback: types.CallbackQuery):

    await callback.answer(
        "🛒 Order system পরের ধাপে চালু করা হবে!",
        show_alert=True
    )


# =========================
# WEBHOOK
# =========================

@app.route("/webhook", methods=["POST"])
def webhook():

    try:
        update_data = request.get_json()

        if not update_data:
            return jsonify({"ok": False}), 400

        update = types.Update.model_validate(update_data)

        asyncio.run(
            dp.feed_update(
                bot,
                update
            )
        )

        return jsonify({"ok": True})

    except Exception as e:
        print("Webhook error:", e)
        return jsonify({"ok": False}), 500


# =========================
# HEALTH CHECK
# =========================

@app.route("/", methods=["GET"])
def home():

    return "Salman Premium Store Bot is running! ✅"


# =========================
# START SERVER
# =========================

if __name__ == "__main__":

    init_database()

    port = int(os.getenv("PORT", 10000))

    if BOT_TOKEN and WEBHOOK_URL:

        try:
            asyncio.run(
                bot.set_webhook(
                    url=WEBHOOK_URL
                )
            )

            print("Webhook set successfully!")

        except Exception as e:
            print("Webhook error:", e)

    app.run(
        host="0.0.0.0",
        port=port
)
