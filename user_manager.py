"""user_manager.py — User Management for HOSTABHI"""

import os
import logging
import sqlite3
import datetime

from telebot import types

log = logging.getLogger("user_mgr")
PAGE_SIZE = 10

_name_cache = {}


def _get_name(bot, uid):
    """Fetch display name from Telegram, cached."""
    if uid in _name_cache:
        return _name_cache[uid]
    try:
        c = bot.get_chat(uid)
        parts = [c.first_name or "", c.last_name or ""]
        n = " ".join(p for p in parts if p).strip()
        if not n:
            n = c.title or (f"@{c.username}" if c.username else None)
        _name_cache[uid] = n
        return n
    except Exception:
        _name_cache[uid] = None
        return None


def _db():
    d = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(d, "inf", "bot_data.db")
    c = sqlite3.connect(p, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def _all_users():
    c = _db()
    try:
        act = [dict(r) for r in c.execute("SELECT user_id FROM active_users").fetchall()]
        ban = [dict(r) for r in c.execute(
            "SELECT user_id, reason, banned_at FROM banned_users").fetchall()]
        ban_ids = {b["user_id"] for b in ban}
        seen = set()
        out = []
        for a in act:
            uid = a["user_id"]
            if uid in seen: continue
            seen.add(uid)
            out.append({"user_id": uid, "banned": uid in ban_ids})
        for b in ban:
            if b["user_id"] in seen: continue
            seen.add(b["user_id"])
            out.append({"user_id": b["user_id"], "banned": True})
        out.sort(key=lambda x: x["user_id"], reverse=True)
        return out
    except Exception as e:
        log.exception("all_users: %s", e); return []
    finally:
        c.close()


def _is_banned(uid):
    c = _db()
    try:
        return c.execute("SELECT 1 FROM banned_users WHERE user_id=?", (uid,)).fetchone() is not None
    except Exception:
        return False
    finally:
        c.close()


def _ban_info(uid):
    c = _db()
    try:
        r = c.execute("SELECT reason, banned_at FROM banned_users WHERE user_id=?",
                      (uid,)).fetchone()
        return (r["reason"] or "—", r["banned_at"] or "—") if r else ("—", "—")
    except Exception:
        return ("—", "—")
    finally:
        c.close()


def _files(uid):
    c = _db()
    try:
        return [dict(r) for r in c.execute(
            "SELECT file_name, file_type FROM user_files WHERE user_id=?",
            (uid,)).fetchall()]
    except Exception:
        return []
    finally:
        c.close()


def _file_path(uid, fname):
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "upload_bots", str(uid))
    if not os.path.isdir(base):
        return None
    direct = os.path.join(base, fname)
    if os.path.isfile(direct):
        return direct
    for root, _, fs in os.walk(base):
        if fname in fs:
            return os.path.join(root, fname)
    return None


def _sub(uid):
    c = _db()
    try:
        r = c.execute("SELECT expiry FROM subscriptions WHERE user_id=?", (uid,)).fetchone()
        return r["expiry"] if r else None
    except Exception:
        return None
    finally:
        c.close()


def _sub_active(uid):
    exp = _sub(uid)
    if not exp: return False
    try:
        return datetime.datetime.fromisoformat(exp.replace("Z", "")) > datetime.datetime.now()
    except Exception:
        return False


def _ban(uid, reason="Banned by admin"):
    c = _db()
    try:
        now = datetime.datetime.now().isoformat()
        c.execute("INSERT OR REPLACE INTO banned_users(user_id, reason, banned_at) "
                  "VALUES(?,?,?)", (uid, reason, now))
        c.commit(); return True
    except Exception as e:
        log.exception("ban: %s", e); return False
    finally:
        c.close()


UNBAN_MSG = (
    "<blockquote>"
    "✅  <b>Access Restored</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "Your access to this bot has been restored by the owner.\n\n"
    "◈  Your ban has been lifted\n"
    "◈  Your previous warnings have been cleared\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "<i>Please remain a member of both required channels\n"
    "to avoid any further restrictions.</i>\n"
    "━━━━━━━━━━━━━━━━━━━━━━"
    "</blockquote>"
)


def _unban(uid):
    c = _db()
    try:
        c.execute("DELETE FROM banned_users WHERE user_id=?", (uid,))
        c.commit(); return True
    except Exception:
        return False
    finally:
        c.close()


def _remove(uid):
    c = _db()
    try:
        n = 0
        for t in ("active_users", "banned_users", "user_files", "subscriptions"):
            try:
                r = c.execute(f"DELETE FROM {t} WHERE user_id=?", (uid,))
                n += max(0, r.rowcount)
            except Exception:
                continue
        c.commit(); return n
    except Exception:
        return 0
    finally:
        c.close()


def _kb_menu():
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        types.InlineKeyboardButton("👥  All Users",  callback_data="um:list:all:0"),
        types.InlineKeyboardButton("✅  Active",     callback_data="um:list:active:0"),
    )
    mk.add(
        types.InlineKeyboardButton("🚫  Banned",     callback_data="um:list:banned:0"),
        types.InlineKeyboardButton("💎  Subscribed", callback_data="um:list:sub:0"),
    )
    mk.add(types.InlineKeyboardButton("📊  Statistics", callback_data="um:stats"))
    mk.add(types.InlineKeyboardButton("🔍  Search by User ID", callback_data="um:search"))
    mk.add(types.InlineKeyboardButton("✖  Close", callback_data="um:close"))
    return mk


def _kb_list(bot, rows, page, total, mode):
    mk = types.InlineKeyboardMarkup(row_width=1)
    for u in rows:
        uid = u["user_id"]
        name = _get_name(bot, uid) or f"User {uid}"
        if len(name) > 18:
            name = name[:17] + "…"
        fc = len(_files(uid))
        flag = "🚫 " if u["banned"] else ""
        sub = "💎 " if _sub_active(uid) else ""
        mk.add(types.InlineKeyboardButton(
            f"{flag}{sub}👤 {name}  ·  📁 {fc}\n🆔 {uid}",
            callback_data=f"um:view:{uid}:{mode}:{page}"))
    nav = []
    if page > 0:
        nav.append(types.InlineKeyboardButton(
            "⬅  Prev", callback_data=f"um:list:{mode}:{page-1}"))
    if (page + 1) * PAGE_SIZE < total:
        nav.append(types.InlineKeyboardButton(
            "Next  ➡", callback_data=f"um:list:{mode}:{page+1}"))
    if nav:
        mk.row(*nav)
    mk.add(types.InlineKeyboardButton("🔙  Main Menu", callback_data="um:menu"))
    return mk


def _kb_user(uid, mode, page):
    mk = types.InlineKeyboardMarkup(row_width=2)
    if _is_banned(uid):
        mk.add(types.InlineKeyboardButton("✅  Unban User",
            callback_data=f"um:unban:{uid}:{mode}:{page}"))
    else:
        mk.add(types.InlineKeyboardButton("🚫  Ban User",
            callback_data=f"um:ban:{uid}:{mode}:{page}"))
    mk.add(types.InlineKeyboardButton("🗑  Remove User",
        callback_data=f"um:remove:{uid}:{mode}:{page}"))
    mk.add(
        types.InlineKeyboardButton("📁  View Files",
            callback_data=f"um:files:{uid}:{mode}:{page}"),
        types.InlineKeyboardButton("💎  Subscription",
            callback_data=f"um:sub:{uid}:{mode}:{page}"),
    )
    mk.add(types.InlineKeyboardButton("🔙  Back to List",
        callback_data=f"um:list:{mode}:{page}"))
    return mk


def _kb_files_list(uid, mode, page):
    files = _files(uid)
    mk = types.InlineKeyboardMarkup(row_width=2)
    for i, f in enumerate(files[:25]):
        name = f.get("file_name") or "—"
        mk.row(
            types.InlineKeyboardButton(
                f"📄 {name[:28]}",
                callback_data=f"um:vfile:{uid}:{i}:{mode}:{page}"),
            types.InlineKeyboardButton(
                "📥  Get",
                callback_data=f"um:gfile:{uid}:{i}:{mode}:{page}"),
        )
    mk.add(types.InlineKeyboardButton("🔙  Back to User",
        callback_data=f"um:view:{uid}:{mode}:{page}"))
    return mk


def _kb_confirm(action, uid, mode, page):
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        types.InlineKeyboardButton("✅  Yes, Confirm",
            callback_data=f"um:{action}_yes:{uid}:{mode}:{page}"),
        types.InlineKeyboardButton("❌  Cancel",
            callback_data=f"um:view:{uid}:{mode}:{page}"),
    )
    return mk


def _t_menu(total, banned, active, subs):
    return ("<blockquote>"
            "👥  <b>User Management</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"◈  Total Users     : <b>{total}</b>\n"
            f"◈  Active Users    : <b>{active}</b>\n"
            f"◈  Banned Users    : <b>{banned}</b>\n"
            f"◈  Subscribed      : <b>{subs}</b>\n\n"
            "Select an option below."
            "</blockquote>")


def _t_card(bot, uid):
    files = _files(uid)
    sub = _sub(uid) or "—"
    sa = "✅ Active" if _sub_active(uid) else "❌ Expired / None"
    banned = _is_banned(uid)
    status = "🚫 Banned" if banned else "✅ Active"
    name = _get_name(bot, uid) or "—"

    t = ("<blockquote>"
         "👤  <b>User Details</b>\n"
         "━━━━━━━━━━━━━━━━━━━━━━\n\n"
         f"👤  Name        : <b>{name}</b>\n"
         f"🆔  User ID     : <code>{uid}</code>\n"
         f"📌  Status      : {status}\n"
         f"💎  Subscription: {sa}\n"
         f"⏳  Expires     : <code>{sub}</code>\n\n"
         f"📁  Files       : <b>{len(files)}</b>\n")
    if banned:
        reason, at = _ban_info(uid)
        t += (f"\n🚫  <b>Ban Info</b>\n"
              f"◈  Reason : {reason}\n"
              f"◈  Banned : {str(at)[:19]}\n")
    t += "━━━━━━━━━━━━━━━━━━━━━━</blockquote>"
    return t


def _t_stats(total, active, banned, subs, files):
    return ("<blockquote>"
            "📊  <b>User Statistics</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👥  Total Users   : <b>{total}</b>\n"
            f"✅  Active Users  : <b>{active}</b>\n"
            f"🚫  Banned Users  : <b>{banned}</b>\n"
            f"💎  Subscribed    : <b>{subs}</b>\n"
            f"📁  Total Files   : <b>{files}</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
            "</blockquote>")


def _send(bot, chat_id, msg_id, text, kb):
    if msg_id:
        try:
            bot.edit_message_text(text, chat_id, msg_id,
                                  reply_markup=kb, parse_mode="HTML")
            return
        except Exception:
            pass
    try:
        bot.send_message(chat_id, text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass


def _view_menu(bot, chat_id, msg_id=None):
    u = _all_users()
    tot = len(u)
    ban = sum(1 for x in u if x["banned"])
    act = tot - ban
    subs = sum(1 for x in u if _sub_active(x["user_id"]))
    _send(bot, chat_id, msg_id, _t_menu(tot, ban, act, subs), _kb_menu())


def _view_list(bot, chat_id, msg_id, mode, page):
    u = _all_users()
    if mode == "banned":  rows = [x for x in u if x["banned"]]
    elif mode == "active": rows = [x for x in u if not x["banned"]]
    elif mode == "sub":    rows = [x for x in u if _sub_active(x["user_id"])]
    else:                  rows = u
    tot = len(rows)
    start = page * PAGE_SIZE
    page_rows = rows[start:start + PAGE_SIZE]
    tp = max(1, (tot + PAGE_SIZE - 1) // PAGE_SIZE)
    title = {"all":"All Users","active":"Active Users",
             "banned":"Banned Users","sub":"Subscribed Users"}.get(mode, "Users")
    txt = (f"<blockquote>👥  <b>{title}</b>\n"
           f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
           f"◈  Total : <b>{tot}</b>\n"
           f"◈  Page  : <b>{page+1}</b> / {tp}\n\n"
           "Tap a user to manage."
           "</blockquote>")
    _send(bot, chat_id, msg_id, txt, _kb_list(bot, page_rows, page, tot, mode))


def _view_user(bot, chat_id, msg_id, uid, mode, page):
    _send(bot, chat_id, msg_id, _t_card(bot, uid), _kb_user(uid, mode, page))


def _view_stats(bot, chat_id, msg_id):
    u = _all_users()
    tot = len(u)
    ban = sum(1 for x in u if x["banned"])
    act = tot - ban
    subs = sum(1 for x in u if _sub_active(x["user_id"]))
    files = sum(len(_files(x["user_id"])) for x in u)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙  Main Menu", callback_data="um:menu"))
    _send(bot, chat_id, msg_id, _t_stats(tot, act, ban, subs, files), kb)


def _view_files(bot, chat_id, msg_id, uid, mode, page):
    files = _files(uid)
    if not files:
        txt = (f"<blockquote>📁  <b>User Files</b>\n"
               f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
               f"No files for <code>{uid}</code>."
               f"</blockquote>")
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔙  Back",
            callback_data=f"um:view:{uid}:{mode}:{page}"))
        _send(bot, chat_id, msg_id, txt, kb)
        return
    txt = (f"<blockquote>📁  <b>Files — <code>{uid}</code></b>\n"
           f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
           f"◈  Total   : <b>{len(files)}</b>\n"
           f"◈  Action  : <b>View name</b>  |  <b>Download</b>\n\n"
           "◈  Tap 📄 to view details\n"
           "◈  Tap 📥 Get to download to chat\n"
           "━━━━━━━━━━━━━━━━━━━━━━"
           "</blockquote>")
    _send(bot, chat_id, msg_id, txt, _kb_files_list(uid, mode, page))


def _view_file_detail(bot, chat_id, msg_id, uid, idx, mode, page):
    files = _files(uid)
    if idx < 0 or idx >= len(files):
        return
    f = files[idx]
    name = f.get("file_name") or "—"
    ftype = f.get("file_type") or "—"
    path = _file_path(uid, name)
    exists = "✅ On disk" if path else "❌ Missing on disk"
    size = "—"
    if path:
        try:
            b = os.path.getsize(path)
            size = f"{b/1024:.1f} KB" if b < 1024*1024 else f"{b/1024/1024:.2f} MB"
        except Exception:
            pass
    txt = (f"<blockquote>📄  <b>File Details</b>\n"
           f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
           f"👤  Owner   : <code>{uid}</code>\n"
           f"📛  Name    : <code>{name}</code>\n"
           f"🧩  Type    : <b>{ftype}</b>\n"
           f"📊  Size    : <b>{size}</b>\n"
           f"💾  Status  : {exists}\n\n"
           f"━━━━━━━━━━━━━━━━━━━━━━"
           f"</blockquote>")
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("📥  Download to Chat",
        callback_data=f"um:gfile:{uid}:{idx}:{mode}:{page}"))
    kb.add(types.InlineKeyboardButton("🔙  Back to Files",
        callback_data=f"um:files:{uid}:{mode}:{page}"))
    _send(bot, chat_id, msg_id, txt, kb)


def _send_file(bot, chat_id, uid, idx, mode, page):
    files = _files(uid)
    if idx < 0 or idx >= len(files):
        bot.send_message(chat_id, "❌ File not found.")
        return
    f = files[idx]
    name = f.get("file_name") or "file"
    path = _file_path(uid, name)
    if not path:
        bot.send_message(chat_id,
            f"<blockquote>❌  <b>File missing on disk</b>\n"
            f"<code>{name}</code></blockquote>",
            parse_mode="HTML")
        return
    try:
        with open(path, "rb") as fh:
            bot.send_document(
                chat_id, fh,
                caption=(f"<blockquote>📄  <b>File from <code>{uid}</code></b>\n"
                         f"◈  Name : <code>{name}</code>\n"
                         f"◈  Type : <b>{f.get('file_type') or '—'}</b>"
                         f"</blockquote>"),
                parse_mode="HTML")
    except Exception as e:
        bot.send_message(chat_id,
            f"<blockquote>❌  <b>Download failed</b>\n"
            f"<code>{str(e)[:120]}</code></blockquote>",
            parse_mode="HTML")


def _view_sub(bot, chat_id, msg_id, uid, mode, page):
    exp = _sub(uid)
    if not exp:
        txt = (f"<blockquote>💎  <b>Subscription</b>\n"
               f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
               f"No subscription for <code>{uid}</code>."
               f"</blockquote>")
    else:
        act = _sub_active(uid)
        txt = (f"<blockquote>💎  <b>Subscription</b>\n"
               f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
               f"🆔  User ID  : <code>{uid}</code>\n"
               f"📌  Status   : {'✅ Active' if act else '❌ Expired'}\n"
               f"⏳  Expires  : <code>{exp}</code>\n\n"
               f"━━━━━━━━━━━━━━━━━━━━━━</blockquote>")
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙  Back",
        callback_data=f"um:view:{uid}:{mode}:{page}"))
    _send(bot, chat_id, msg_id, txt, kb)


def _do_search(m, bot):
    if not m.text or not m.text.strip().isdigit():
        bot.send_message(m.chat.id, "❌ Send a numeric User ID.")
        return
    uid = int(m.text.strip())
    ids = {x["user_id"] for x in _all_users()}
    if uid not in ids:
        bot.send_message(m.chat.id,
            f"❌ User <code>{uid}</code> not found.", parse_mode="HTML")
        return
    bot.send_message(m.chat.id, _t_card(bot, uid),
                     reply_markup=_kb_user(uid, "all", 0), parse_mode="HTML")


def _handle_callback(bot, c):
    p = c.data.split(":")
    a = p[1]
    if a == "menu":
        bot.answer_callback_query(c.id)
        _view_menu(bot, c.message.chat.id, c.message.message_id)
    elif a == "close":
        bot.answer_callback_query(c.id)
        try: bot.delete_message(c.message.chat.id, c.message.message_id)
        except: pass
    elif a == "stats":
        bot.answer_callback_query(c.id)
        _view_stats(bot, c.message.chat.id, c.message.message_id)
    elif a == "list":
        bot.answer_callback_query(c.id)
        _view_list(bot, c.message.chat.id, c.message.message_id, p[2], int(p[3]))
    elif a == "view":
        bot.answer_callback_query(c.id)
        _view_user(bot, c.message.chat.id, c.message.message_id,
                   int(p[2]), p[3], int(p[4]))
    elif a == "ban":
        bot.answer_callback_query(c.id)
        _send(bot, c.message.chat.id, c.message.message_id,
              "<blockquote>🚫  <b>Confirm Ban</b>\n"
              "━━━━━━━━━━━━━━━━━━━━━━\n\n"
              f"Ban user <code>{p[2]}</code>?\n\n"
              "All access will be revoked.</blockquote>",
              _kb_confirm("ban", int(p[2]), p[3], int(p[4])))
    elif a == "ban_yes":
        ok = _ban(int(p[2]))
        bot.answer_callback_query(c.id, "✅ Banned" if ok else "❌ Failed")
        _view_user(bot, c.message.chat.id, c.message.message_id,
                   int(p[2]), p[3], int(p[4]))
    elif a == "unban":
        ok = _unban(int(p[2]))
        bot.answer_callback_query(c.id, "✅ Unbanned" if ok else "❌ Failed")
        _view_user(bot, c.message.chat.id, c.message.message_id,
                   int(p[2]), p[3], int(p[4]))
    elif a == "remove":
        bot.answer_callback_query(c.id)
        _send(bot, c.message.chat.id, c.message.message_id,
              "<blockquote>🗑  <b>Confirm Remove</b>\n"
              "━━━━━━━━━━━━━━━━━━━━━━\n\n"
              f"Permanently remove <code>{p[2]}</code>?\n\n"
              "⚠️ Files, subscription, ban — all deleted.\n"
              "This cannot be undone.</blockquote>",
              _kb_confirm("remove", int(p[2]), p[3], int(p[4])))
    elif a == "remove_yes":
        n = _remove(int(p[2]))
        bot.answer_callback_query(c.id, f"🗑 Removed ({n} records)")
        _view_list(bot, c.message.chat.id, c.message.message_id, p[3], int(p[4]))
    elif a == "files":
        bot.answer_callback_query(c.id)
        _view_files(bot, c.message.chat.id, c.message.message_id,
                    int(p[2]), p[3], int(p[4]))
    elif a == "vfile":
        bot.answer_callback_query(c.id)
        _view_file_detail(bot, c.message.chat.id, c.message.message_id,
                          int(p[2]), int(p[3]), p[4], int(p[5]))
    elif a == "gfile":
        bot.answer_callback_query(c.id, "📥 Sending…")
        _send_file(bot, c.message.chat.id, int(p[2]), int(p[3]), p[4], int(p[5]))
    elif a == "sub":
        bot.answer_callback_query(c.id)
        _view_sub(bot, c.message.chat.id, c.message.message_id,
                  int(p[2]), p[3], int(p[4]))
    elif a == "search":
        bot.answer_callback_query(c.id)
        msg = bot.send_message(c.message.chat.id,
            "<blockquote>🔍  Send the <b>User ID</b> to search.</blockquote>",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, _do_search, bot)
    else:
        bot.answer_callback_query(c.id)


def register(bot, is_admin_fn):
    @bot.message_handler(
        func=lambda m: m.text and "user management" in m.text.lower()
        and is_admin_fn(m.from_user.id))
    def _open_btn(m):
        try:
            _view_menu(bot, m.chat.id)
        except Exception as e:
            log.exception("btn: %s", e)

    @bot.message_handler(commands=["users"])
    def _open_cmd(m):
        if not is_admin_fn(m.from_user.id):
            return
        try:
            _view_menu(bot, m.chat.id)
        except Exception as e:
            log.exception("cmd: %s", e)

    print("[UM] User Management installed", flush=True)
