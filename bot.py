import asyncio
import os

from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher
from aiogram.types import (
    Update,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import BOT_TOKEN, WEBHOOK_URL

app = Flask(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛍️ Products",
                    callback_data="products"
                ),
                InlineKeyboardButton(
                    text="📦 My Orders",
                    callback_data="orders"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👤 My Account",
                    callback_data="account"
                ),
                InlineKeyboardButton(
                    text="💰 Balance",
                    callback_data="balance"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🎁 Offers",
                    callback_data="offers"
                ),
                InlineKeyboardButton(
                    text="📞 Support",
                    callback_data="support"
                ),
            ],
        ]
    )


@dp.message()
async def handle_message(message: Message):
    if message.text == "/start":
        await message.answer(
            "👋 <b>Welcome to Salman Premium Store!</b>\n\n"
            "🛍️ এখানে Premium Products ও Services পাওয়া যাবে।\n\n"
            "নিচের Menu থেকে একটি option নির্বাচন করুন 👇",
            reply_markup=main_keyboard(),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            "👇 নিচের Menu ব্যবহার করুন:",
            reply_markup=main_keyboard(),
        )


@dp.callback_query()
async def handle_callback(callback):
    await callback.answer()

    if callback.data == "products":
        text = (
            "🛍️ <b>Products</b>\n\n"
            "এখনো কোনো Product যোগ করা হয়নি।\n"
            "Admin Panel থেকে Product যোগ করা যাবে।"
        )

    elif callback.data == "orders":
        text = "📦 <b>My Orders</b>\n\nআপনার কোনো Order নেই।"

    elif callback.data == "account":
        user = callback.from_user

        text = (
            "👤 <b>My Account</b>\n\n"
            f"Name: {user.first_name}\n"
            f"Username: @{user.username or 'Not set'}\n"
            f"Telegram ID: <code>{user.id}</code>"
        )

    elif callback.data == "balance":
        text = "💰 <b>Balance</b>\n\nCurrent Balance: ৳0.00"

    elif callback.data == "offers":
        text = "🎁 <b>Offers</b>\n\nবর্তমানে কোনো Active Offer নেই।"

    elif callback.data == "support":
        text = "📞 <b>Support</b>\n\nSupport system খুব শিগগিরই যুক্ত করা হবে।"

    else:
        text = "Unknown option."

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Main Menu",
                        callback_data="home"
                    )
                ]
            ]
        ),
        parse_mode="HTML",
    )


@dp.callback_query(lambda c: c.data == "home")
async def home_callback(callback):
    await callback.answer()

    await callback.message.edit_text(
        "🏪 <b>Salman Premium Store</b>\n\n"
        "আপনার পছন্দের option নির্বাচন করুন 👇",
        reply_markup=main_keyboard(),
        parse_mode="HTML",
    )


@app.get("/")
def home():
    return "Salman Premium Store Bot is running."


@app.post("/webhook")
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.model_validate(data)

        await dp.feed_update(bot, update)

        return jsonify({"ok": True})

    except Exception as e:
        print("Webhook error:", e)
        return jsonify({"ok": False}), 500


async def set_webhook():
    if WEBHOOK_URL:
        await bot.set_webhook(
            WEBHOOK_URL,
            drop_pending_updates=True
        )
        print("Webhook set:", WEBHOOK_URL)
    else:
        print("WEBHOOK_URL is not configured.")


async def startup():
    await set_webhook()


@app.before_request
def before_request():
    pass


if __name__ == "__main__":
    asyncio.run(startup())

    port = int(os.getenv("PORT", "10000"))

    app.run(
        host="0.0.0.0",
        port=port
    )
