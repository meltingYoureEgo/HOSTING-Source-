

def _cfg_owner_live(fallback=0):
    """Return current owner from bot_config DB."""
    try:
        import bot_config as _bc
        o = _bc.current_owner()
        if o and o > 0:
            return o
    except Exception:
        pass
    return fallback

"""
upload_approval.py
Owner approval gate for uploaded files.
- User uploads file → saved → approval request sent to OWNER
- Owner taps ✅ Approve → script runs
- Owner taps ❌ Reject → file deleted
"""

import os
import time
import logging
import threading

from telebot import types


def _record_user_file(user_id, file_name, file_ext):
    """Insert into user_files table for Check Files + Statistics."""
    try:
        import sqlite3, os
        db = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'inf', 'bot_data.db')
        c = sqlite3.connect(db, check_same_thread=False)
        # Ensure table exists (matches HOSTABHI schema)
        c.execute('''CREATE TABLE IF NOT EXISTS user_files (
            user_id INTEGER, file_name TEXT, file_type TEXT)''')
        # Avoid duplicate records
        exists = c.execute(
            'SELECT 1 FROM user_files WHERE user_id=? AND file_name=?',
            (user_id, file_name)).fetchone()
        if not exists:
            c.execute('INSERT INTO user_files(user_id, file_name, file_type) '
                      'VALUES (?, ?, ?)',
                      (user_id, file_name, file_ext.lstrip('.')))
            c.commit()
            print(f'[UF] recorded {file_name} for user {user_id}', flush=True)
        c.close()
        return True
    except Exception as e:
        print(f'[UF] record error: {e}', flush=True)
        return False


log = logging.getLogger("approval")

# uid -> list of pending dicts
#   {approval_id, user_id, chat_id, file_path, file_name, file_ext,
#    user_folder, message_obj, created_at}
_PENDING = {}
_LOCK = threading.Lock()
_NEXT_ID = [1]


def _new_id():
    with _LOCK:
        i = _NEXT_ID[0]
        _NEXT_ID[0] += 1
        return i


def request_approval(bot, owner_id, user, chat_id, file_path, file_name,
                     file_ext, user_folder, message_obj):
    """Send approval request to owner. Returns True if queued."""
    try:
        # Record file in user_files table
        _record_user_file(user.id, file_name, file_ext)

        aid = _new_id()
        rec = {
            "approval_id": aid,
            "user_id": user.id,
            "user_name": user.first_name or "User",
            "user_username": user.username or "—",
            "chat_id": chat_id,
            "file_path": file_path,
            "file_name": file_name,
            "file_ext": file_ext,
            "user_folder": user_folder,
            "message_obj": message_obj,
            "created_at": time.time(),
        }
        with _LOCK:
            _PENDING[aid] = rec

        size_kb = 0
        try:
            size_kb = round(os.path.getsize(file_path) / 1024, 1)
        except Exception:
            pass

        text = (
            f"<blockquote>🔔 <b>ɴᴇᴡ ᴜᴘʟᴏᴀᴅ — ᴀᴘᴘʀᴏᴠᴀʟ ʀᴇQᴜɪʀᴇᴅ</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 ᴜꜱᴇʀ    : <a href='tg://user?id={user.id}'>{user.first_name}</a>\n"
            f"🔗 ᴜꜱᴇʀɴᴀᴍᴇ: @{user.username or '—'}\n"
            f"🆔 ɪᴅ      : <code>{user.id}</code>\n\n"
            f"📄 ꜰɪʟᴇ    : <code>{file_name}</code>\n"
            f"📊 ꜱɪᴢᴇ    : <b>{size_kb} KB</b>\n"
            f"🧩 ᴛʏᴘᴇ    : <b>{file_ext}</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"ᴀᴘᴘʀᴏᴠᴇ ᴋᴀʀɴᴇ ᴩᴀʀ ꜱᴄʀɪᴩᴛ ᴄʜᴀʟᴇɢɪ.\n"
            f"ʀᴇᴊᴇᴄᴛ ᴋᴀʀɴᴇ ᴩᴀʀ ꜰɪʟᴇ ᴅᴇʟᴇᴛᴇ ʜᴏɢɪ.</blockquote>"
        )

        mk = types.InlineKeyboardMarkup(row_width=2)
        mk.row(
            types.InlineKeyboardButton("✅ Approve", callback_data=f"appr_ok:{aid}"),
            types.InlineKeyboardButton("❌ Reject",  callback_data=f"appr_no:{aid}"),
        )

        bot.send_message(owner_id, text, reply_markup=mk, parse_mode="HTML",
                         disable_web_page_preview=True)
        log.info("Approval #%d requested for %s from %s", aid, file_name, user.id)
        return aid
    except Exception as e:
        log.error("request_approval failed: %s", e)
        return None


def register_handlers(bot, owner_id):
    """Register approve/reject callback handlers."""

    @bot.callback_query_handler(func=lambda c: c.data.startswith("appr_ok:"))
    def _approve(c):
    # NO_CHECK_PATCH
        try:
            aid = int(c.data.split(":")[1])
        except Exception:
            bot.answer_callback_query(c.id, "Invalid", show_alert=True)
            return

        with _LOCK:
            rec = _PENDING.pop(aid, None)
        if not rec:
            bot.answer_callback_query(c.id, "⚠️ Already handled", show_alert=True)
            try:
                bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id,
                                              reply_markup=None)
            except Exception:
                pass
            return

        bot.answer_callback_query(c.id, "✅ Approved — running")
        try:
            bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id,
                                          reply_markup=None)
        except Exception:
            pass

        # Notify user
        try:
            bot.send_message(rec["chat_id"],
                f"<blockquote>✅ <b>ᴀᴘᴘʀᴏᴠᴇᴅ</b>\n\n"
                f"ᴏᴡɴᴇʀ ɴᴇ ᴛᴇʀɪ ꜰɪʟᴇ <code>{rec['file_name']}</code> ᴀᴘᴘʀᴏᴠᴇ ᴋᴀʀ ᴅɪ.\n"
                f"ꜱᴄʀɪᴩᴛ ᴄʜᴀʟ ʀᴀʜɪ ʜᴀɪ…</blockquote>",
                parse_mode="HTML")
        except Exception:
            pass

        # Run it
        try:
            # Imported lazily so this module can be loaded before HOSTABHI handlers exist
            from HOSTABHI import handle_py_file, handle_js_file  # noqa
        except Exception:
            handle_py_file = handle_js_file = None

        # Fallback: use attributes monkey-patched onto bot
        if not handle_py_file:
            handle_py_file = getattr(bot, "_hostabhi_handle_py", None)
        if not handle_js_file:
            handle_js_file = getattr(bot, "_hostabhi_handle_js", None)

        try:
            ext = rec["file_ext"]
            if ext == ".py" and handle_py_file:
                handle_py_file(rec["file_path"], rec["user_id"], rec["user_folder"],
                               rec["file_name"], rec["message_obj"])
            elif ext == ".js" and handle_js_file:
                handle_js_file(rec["file_path"], rec["user_id"], rec["user_folder"],
                               rec["file_name"], rec["message_obj"])
            else:
                bot.send_message(owner_id,
                    f"⚠️ Could not run <code>{rec['file_name']}</code> — "
                    f"handler for {ext} missing.", parse_mode="HTML")
        except Exception as e:
            log.error("Approved run failed: %s", e)
            try:
                bot.send_message(owner_id,
                    f"❌ Run error for <code>{rec['file_name']}</code>: "
                    f"<code>{str(e)[:200]}</code>", parse_mode="HTML")
            except Exception:
                pass

    @bot.callback_query_handler(func=lambda c: c.data.startswith("appr_no:"))
    def _reject(c):
    # NO_CHECK_PATCH
        try:
            aid = int(c.data.split(":")[1])
        except Exception:
            bot.answer_callback_query(c.id, "Invalid", show_alert=True)
            return

        with _LOCK:
            rec = _PENDING.pop(aid, None)
        if not rec:
            bot.answer_callback_query(c.id, "⚠️ Already handled", show_alert=True)
            try:
                bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id,
                                              reply_markup=None)
            except Exception:
                pass
            return

        # Delete file
        try:
            if os.path.exists(rec["file_path"]):
                os.remove(rec["file_path"])
        except Exception:
            pass

        bot.answer_callback_query(c.id, "❌ Rejected — file deleted")
        try:
            bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id,
                                          reply_markup=None)
        except Exception:
            pass

        try:
            bot.send_message(rec["chat_id"],
                f"<blockquote>❌ <b>ʀᴇᴊᴇᴄᴛᴇᴅ</b>\n\n"
                f"ᴏᴡɴᴇʀ ɴᴇ ᴛᴇʀɪ ꜰɪʟᴇ <code>{rec['file_name']}</code> ʀᴇᴊᴇᴄᴛ ᴋᴀʀ ᴅɪ.\n"
                f"ꜰɪʟᴇ ᴅᴇʟᴇᴛᴇ ʜᴏ ɢᴀɪ.</blockquote>",
                parse_mode="HTML")
        except Exception:
            pass

    log.info("Approval handlers registered")
