import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.ia_filterdb import get_search_results, get_file_details
from database.config_db import mdb
from database.users_chats_db import db

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_search(client, message):
    """Handles private chat searches and displays results as inline buttons."""

    await mdb.update_top_messages(message.from_user.id, message.text)
    bot_id = client.me.id

    if str(message.text).startswith('/'):
        return

    if await db.get_pm_search_status(bot_id):
        search_query = message.text.lower()
        files, _, total = await get_search_results(search_query, offset=0)

        if not files:
            await message.reply_text("<b>No results found! ❌</b>")
            return
        
        # Show a maximum of 10 results as buttons
        buttons = []
        for file in files[:10]:  # Limit to 10 results
            buttons.append([
                InlineKeyboardButton(
                    text=f"🎬 {file.file_name[:40]}...",
                    callback_data=f"movie#{file.file_id}"
                )
            ])

        # Send buttons instead of a text file
        await message.reply_text(
            f"<b>Found {min(10, total)} results for:</b> <code>{message.text}</code>\n\n<b>Select a movie:</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await message.reply_text(
            "<b>I'm not working here. Search in our movie search group.</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📽 Movie Search Group", url="https://t.me/learning_bots")]
            ])
        )

@Client.on_callback_query(filters.regex(r"^movie#"))
async def send_movie_file(client, query: CallbackQuery):
    """Handles button clicks to send selected movie file."""

    _, file_id = query.data.split("#")
    files_ = await get_file_details(file_id)

    if not files_:
        await query.answer("❌ Movie file not found!", show_alert=True)
        return

    movie_file = files_[0]

    await query.message.reply_document(
        document=movie_file.file_id,
        caption=f"<b>🎬 {movie_file.file_name}</b>"
    )
    await query.answer()