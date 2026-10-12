"""bot_config.py — Settings panel with working callbacks (module-level dispatch)"""

import os
import sqlite3
import logging

from telebot import types
import builtins

log = logging.getLogger("bot_config")

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "inf", "bot_data.db")

_settings = {}
_RUNTIME = {"owner_id": 0, "admin_ids": builtins.set()}



def _db():
    c = sqlite3.connect(_DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def _load_cache():
    global _settings
    try:
        c = _db()
        rows = c.execute("SELECT key, value FROM bot_settings").fetchall()
        _settings = {r["key"]: r["value"] for r in rows}
        c.close()
    except Exception:
        _settings = {}


def init_config(defaults=None):
    try:
        c = _db()
        c.execute("""CREATE TABLE IF NOT EXISTS bot_settings (
            key TEXT PRIMARY KEY, value TEXT, updated_at TEXT)""")
        c.commit()
        if defaults:
            for k, v in defaults.items():
                cur = c.execute("SELECT value FROM bot_settings WHERE key=?", (k,)).fetchone()
                if cur is None:
                    c.execute("INSERT INTO bot_settings(key,value,updated_at) "
                              "VALUES(?,?,datetime('now'))", (k, str(v)))
                else:
                    existing = (cur["value"] or "").strip()
                    if existing in ("", "0", "None", "null"):
                        c.execute("UPDATE bot_settings SET value=?, updated_at=datetime('now') "
                                  "WHERE key=?", (str(v), k))
            c.commit()
        c.close()
        _load_cache()
        print(f"[CFG] Initialized: {_settings}", flush=True)
        return True
    except Exception as e:
        log.exception("init: %s", e)
        return False


def _db_get(key, default=None):
    """Read directly from DB — no cache."""
    try:
        c = _db()
        r = c.execute("SELECT value FROM bot_settings WHERE key=?", (key,)).fetchone()
        c.close()
        return r["value"] if r else default
    except Exception:
        return default

def get(key, default=None):
    val = _db_get(key, None)
    return val if val is not None else default

def get_int(key, default=0):
    val = _db_get(key, None)
    if val is None: return default
    try: return int(val)
    except: return default

def get_str(key, default=""):
    val = _db_get(key, None)
    return str(val) if val is not None else default

def set(key, value):
    try:
        c = _db()
        c.execute("INSERT OR REPLACE INTO bot_settings(key,value,updated_at) VALUES(?,?,datetime('now'))", (key, str(value)))
        c.commit(); c.close()
        _settings[key] = str(value)
        return True
    except Exception as e:
        log.exception("set: %s", e); return False

_GLOBALS = {"owner_id": 0, "admin_ids": builtins.set(), "get_owner_id_fn": None}

def set_globals(owner_id=None, admin_ids=None, get_owner_id_fn=None):
    if owner_id is not None:
        _GLOBALS["owner_id"] = owner_id
    if admin_ids is not None:
        _GLOBALS["admin_ids"] = builtins.set(admin_ids)
    if get_owner_id_fn is not None:
        _GLOBALS["get_owner_id_fn"] = get_owner_id_fn

def _runtime_owner():
    """Current owner id from DB, fallback to globals."""
    oid = get_owner_id()
    if oid and oid > 0:
        return oid
    return _GLOBALS.get("owner_id", 0)

def _runtime_admins():
    return _GLOBALS.get("admin_ids", set())

def list_admins():
    """Admins = runtime set minus owner."""
    oid = _runtime_owner()
    return [a for a in _runtime_admins() if a != oid]

def add_admin(uid):
    try:
        s = _GLOBALS.get("admin_ids")
        if s is not None:
            s.add(int(uid))
        return True
    except Exception:
        return False

def remove_admin(uid):
    try:
        s = _GLOBALS.get("admin_ids")
        if s is not None:
            s.discard(int(uid))
        return True
    except Exception:
        return False

def set_runtime(owner_id=None, admin_ids=None):
    if owner_id is not None:
        _RUNTIME["owner_id"] = int(owner_id) if owner_id else 0
    if admin_ids is not None:
        _RUNTIME["admin_ids"] = builtins.set(admin_ids)
    print(f"[CFG] Runtime set: owner={_RUNTIME['owner_id']} admins={_RUNTIME['admin_ids']}", flush=True)

def current_owner():
    """Live owner ID — DB first, then runtime."""
    oid = get_owner_id()
    if oid and oid > 0:
        return oid
    return _RUNTIME.get("owner_id", 0)

def runtime_admins():
    return builtins.set(_RUNTIME.get("admin_ids", builtins.set()))

def list_admins():
    oid = current_owner()
    return sorted([a for a in _RUNTIME.get("admin_ids", builtins.set()) if a != oid])

def add_admin(uid):
    try:
        _RUNTIME.setdefault("admin_ids", set()).add(int(uid))
        return True
    except Exception:
        return False

def remove_admin(uid):
    try:
        _RUNTIME.get("admin_ids", set()).discard(int(uid))
        return True
    except Exception:
        return False

def get_owner_id(): return get_int("owner_id", 0)
def get_contact_username(): return get_str("contact_username", "").lstrip("@").strip()
def get_support_username(): return get_str("support_username", "").lstrip("@").strip()


# ═══════════════════════════════════════════════════════════════
# KEYBOARDS
# ═══════════════════════════════════════════════════════════════

def _kb_settings():
    mk = types.InlineKeyboardMarkup(row_width=1)
    mk.add(types.InlineKeyboardButton("👑  Owner Settings", callback_data="cfg:owner"))
    mk.add(types.InlineKeyboardButton("👥  Admin Management", callback_data="cfg:admin"))
    mk.add(types.InlineKeyboardButton("📩  Contact Username", callback_data="cfg:contact"))
    mk.add(types.InlineKeyboardButton("🎧  Support Username", callback_data="cfg:support"))
    mk.add(types.InlineKeyboardButton("🔍  View All Settings", callback_data="cfg:view"))
    mk.add(types.InlineKeyboardButton("✖  Close", callback_data="cfg:close"))
    return mk


def _kb_back():
    mk = types.InlineKeyboardMarkup(row_width=1)
    mk.add(types.InlineKeyboardButton("◀  Back", callback_data="cfg:menu"))
    return mk


def _kb_admin_menu():
    mk = types.InlineKeyboardMarkup(row_width=1)
    mk.add(types.InlineKeyboardButton("➕  Add Admin", callback_data="cfg:admin_add"))
    mk.add(types.InlineKeyboardButton("➖  Remove Admin", callback_data="cfg:admin_rm"))
    mk.add(types.InlineKeyboardButton("📋  List Admins", callback_data="cfg:admin_list"))
    mk.add(types.InlineKeyboardButton("🚪  Leave Admin Role (Self-Remove)", callback_data="cfg:admin_self"))
    mk.add(types.InlineKeyboardButton("◀  Back", callback_data="cfg:menu"))
    return mk


def _kb_owner():
    mk = types.InlineKeyboardMarkup(row_width=1)
    mk.add(types.InlineKeyboardButton("🔄  Transfer Ownership", callback_data="cfg:owner_change"))
    mk.add(types.InlineKeyboardButton("◀  Back", callback_data="cfg:menu"))
    return mk


def _kb_confirm_owner(new_id):
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.row(
        types.InlineKeyboardButton("✅  Confirm Transfer",
                                   callback_data=f"cfg:owner_do:{new_id}"),
        types.InlineKeyboardButton("❌  Cancel", callback_data="cfg:owner"),
    )
    return mk


# ═══════════════════════════════════════════════════════════════
# TEXT
# ═══════════════════════════════════════════════════════════════

def _t_menu():
    owner = get_owner_id()
    contact = get_contact_username() or "—"
    support = get_support_username() or "—"
    return ("<blockquote>"
            "⚙️  <b>Bot Settings</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👑  Owner ID        : <code>{owner}</code>\n"
            f"📩  Contact Username: @{contact}\n"
            f"🎧  Support Username: @{support}\n\n"
            "Select an option below.\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
            "</blockquote>")


# ═══════════════════════════════════════════════════════════════
# SEND
# ═══════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════
# MODULE-LEVEL HANDLERS (called from HOSTABHI)
# ═══════════════════════════════════════════════════════════════

def open_menu(bot, chat_id, user_id):
    """Open the settings panel. Returns True if handled."""
    if user_id != get_owner_id():
        return False
    _load_cache()
    _send(bot, chat_id, None, _t_menu(), _kb_settings())
    return True


def _handle_owner_change_input(m, bot, is_owner_fn):
    """register_next_step_handler callback."""
    if not m.text:
        return
    txt = m.text.strip()
    if txt.lower() == "/cancel":
        bot.send_message(m.chat.id, "❌ Cancelled.")
        _send(bot, m.chat.id, None, _t_menu(), _kb_settings())
        return

    new_owner = None
    if txt.isdigit():
        new_owner = int(txt)
    elif txt.startswith("@") or txt.replace("_", "").isalnum():
        un = txt.lstrip("@")
        try:
            ch = bot.get_chat(f"@{un}")
            new_owner = ch.id
        except Exception:
            bot.send_message(m.chat.id,
                f"<blockquote>❌ Could not resolve @{un}.\n"
                f"Send numeric User ID instead.</blockquote>",
                parse_mode="HTML")
            return

    if not new_owner:
        bot.send_message(m.chat.id, "❌ Invalid input.")
        return

    try:
        ch = bot.get_chat(new_owner)
        name = ch.first_name or "—"
        un = ch.username or "—"
    except Exception:
        name = "—"
        un = "—"

    bot.send_message(m.chat.id,
        f"<blockquote>"
        f"👑  <b>Confirm Ownership Transfer</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤  New Owner : <b>{name}</b>\n"
        f"🆔  User ID   : <code>{new_owner}</code>\n"
        f"🔗  Username  : @{un}\n\n"
        f"⚠️  After confirming, restart the bot:\n"
        f"<code>sudo systemctl restart hostabhi</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
        f"</blockquote>",
        reply_markup=_kb_confirm_owner(new_owner), parse_mode="HTML")


def _handle_contact_input(m, bot):
    if not m.text:
        return
    txt = m.text.strip()
    if txt.lower() == "/cancel":
        bot.send_message(m.chat.id, "❌ Cancelled.")
        return
    un = txt.lstrip("@").strip()
    if not un:
        bot.send_message(m.chat.id, "❌ Invalid username.")
        return
    set("contact_username", un)
    bot.send_message(m.chat.id,
        f"<blockquote>"
        f"✅  <b>Contact Username Updated</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📩  New Value : @{un}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
        f"</blockquote>", parse_mode="HTML")


def _handle_support_input(m, bot):
    if not m.text:
        return
    txt = m.text.strip()
    if txt.lower() == "/cancel":
        bot.send_message(m.chat.id, "❌ Cancelled.")
        return
    un = txt.lstrip("@").strip()
    if not un:
        bot.send_message(m.chat.id, "❌ Invalid username.")
        return
    set("support_username", un)
    bot.send_message(m.chat.id,
        f"<blockquote>"
        f"✅  <b>Support Username Updated</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎧  New Value : @{un}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
        f"</blockquote>", parse_mode="HTML")


def _dispatch_cb(bot, c):
    """Handle cfg: callbacks. Called from HOSTABHI's dispatch."""
    if c.from_user.id != get_owner_id():
        try:
            bot.answer_callback_query(c.id, "Owner only.", show_alert=True)
        except Exception:
            pass
        return

    p = c.data.split(":")
    a = p[1] if len(p) > 1 else ""

    if a == "close":
        bot.answer_callback_query(c.id)
        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except Exception:
            pass
        return

    if a == "menu":
        bot.answer_callback_query(c.id)
        _load_cache()
        _send(bot, c.message.chat.id, c.message.message_id,
              _t_menu(), _kb_settings())
        return

    if a == "view":
        bot.answer_callback_query(c.id)
        _load_cache()
        lines = ["<blockquote>🔍  <b>All Settings</b>",
                 "━━━━━━━━━━━━━━━━━━━━━━\n"]
        for k, v in sorted(_settings.items()):
            lines.append(f"◈  <code>{k}</code> : <b>{v}</b>")
        lines.append("\n━━━━━━━━━━━━━━━━━━━━━━</blockquote>")
        _send(bot, c.message.chat.id, c.message.message_id,
              "\n".join(lines), _kb_back())
        return

    if a == "owner":
        bot.answer_callback_query(c.id)
        owner = get_owner_id()
        text = ("<blockquote>"
                "👑  <b>Owner Settings</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Current Owner ID : <code>{owner}</code>\n\n"
                "⚠️  <b>Warning</b>\n"
                "Transferring ownership is permanent.\n"
                "You will lose all admin access unless re-granted.\n\n"
                "Continue?\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
                "</blockquote>")
        _send(bot, c.message.chat.id, c.message.message_id, text, _kb_owner())
        return

    if a == "owner_change":
        bot.answer_callback_query(c.id)
        msg = bot.send_message(c.message.chat.id,
            "<blockquote>"
            "👑  <b>Transfer Ownership</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Send the new owner's <b>User ID</b>\n"
            "(or <b>@username</b>)\n\n"
            "◈  Type /cancel to abort\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
            "</blockquote>", parse_mode="HTML")
        bot.register_next_step_handler(msg, _handle_owner_change_input,
                                        bot, lambda uid: uid == get_owner_id())
        return

    if a == "owner_do":
        try:
            new_id = int(p[2])
        except Exception:
            bot.answer_callback_query(c.id, "Invalid")
            return
        ok = set("owner_id", new_id)
        bot.answer_callback_query(c.id, "✅ Owner updated" if ok else "❌ Failed")
        _send(bot, c.message.chat.id, c.message.message_id,
              f"<blockquote>"
              f"✅  <b>Ownership Transferred</b>\n"
              f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
              f"👑 New Owner ID : <code>{new_id}</code>\n\n"
              f"⚠️  <b>Restart the bot now</b>:\n"
              f"<code>sudo systemctl restart hostabhi</code>\n"
              f"━━━━━━━━━━━━━━━━━━━━━━"
              f"</blockquote>", _kb_settings())
        return

    if a == "contact":
        bot.answer_callback_query(c.id)
        cur = get_contact_username() or "—"
        msg = bot.send_message(c.message.chat.id,
            f"<blockquote>"
            f"📩  <b>Contact Username</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Current : @{cur}\n\n"
            f"Send new username (without @).\n"
            f"◈  Example: <code>CorrupttMind</code>\n"
            f"◈  /cancel to abort\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
            f"</blockquote>", parse_mode="HTML")
        bot.register_next_step_handler(msg, _handle_contact_input, bot)
        return

    if a == "support":
        bot.answer_callback_query(c.id)
        cur = get_support_username() or "—"
        msg = bot.send_message(c.message.chat.id,
            f"<blockquote>"
            f"🎧  <b>Support Username</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Current : @{cur}\n\n"
            f"Send new username (without @).\n"
            f"◈  /cancel to abort\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
            f"</blockquote>", parse_mode="HTML")
        bot.register_next_step_handler(msg, _handle_support_input, bot)
        return

    bot.answer_callback_query(c.id)
