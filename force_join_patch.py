"""force_join_patch.py — STRICT v17 FINAL
- Contact Owner button works
- Unban detection — state auto reset when admin unbans
- FJ messages cleaned up on verify
- Ban spam fixed
- DM only, group silent
"""
import os
import time
import sqlite3
import datetime
import logging

from telebot import types

log = logging.getLogger("force_join")

CHANNELS = [
    ("@meltingYoureEgo",  "Melting Ego"),
    ("@meltingYoureEgoo", "Melting Egoo"),
]

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "inf", "bot_data.db")

_state = {}


def _get_state(uid):
    s = _state.get(uid)
    if s is None:
        s = {
            "joined": None,
            "warns": 0,
            "ban_msg_sent": False,
            "verify_lock": 0.0,
            "verified_msg_sent": False,
            "start_prompt_at": 0.0,
            "fj_msg_ids": [],
            "was_banned": False,
        }
        _state[uid] = s
    return s


def _db():
    c = sqlite3.connect(_DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def _is_db_banned(uid):
    try:
        c = _db()
        r = c.execute("SELECT 1 FROM banned_users WHERE user_id=?", (uid,)).fetchone()
        c.close()
        return r is not None
    except Exception:
        return False


def _add_db_ban(uid, reason):
    try:
        c = _db()
        now = datetime.datetime.now().isoformat()
        c.execute("INSERT OR REPLACE INTO banned_users(user_id, reason, banned_at) "
                  "VALUES(?,?,?)", (uid, reason, now))
        c.commit(); c.close()
        return True
    except Exception as e:
        log.exception("db ban: %s", e); return False


FJ_MSG = (
    "<blockquote>"
    "🔒  <b>Access Restricted</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "To use this bot, you must join <b>both channels</b> listed below.\n\n"
    "◈  Tap each channel to join\n"
    "◈  Then tap <b>Verify Membership</b>\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "<i>Access will be granted immediately after verification.</i>"
    "</blockquote>"
)

VERIFIED_MSG = (
    "<blockquote>"
    "✅  <b>Verification Successful</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "Your access has been granted.\n\n"
    "◈  Send <b>/start</b> to open the menu\n"
    "◈  Thank you for joining\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━"
    "</blockquote>"
)

WARN_1_MSG = (
    "<blockquote>"
    "⚠️  <b>First Warning Issued</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "You have left one or both of our required channels.\n\n"
    "◈  Rejoin <b>both channels</b> immediately\n"
    "◈  Then tap <b>Verify Membership</b>\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "This is warning <b>1 of 2</b>.\n"
    "One more leave will trigger the final warning.\n"
    "━━━━━━━━━━━━━━━━━━━━━━"
    "</blockquote>"
)

WARN_2_MSG = (
    "<blockquote>"
    "⚠️  <b>Final Warning Issued</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "You have left the required channels again.\n\n"
    "◈  Rejoin <b>both channels</b> immediately\n"
    "◈  Then tap <b>Verify Membership</b>\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "This is warning <b>2 of 2</b>.\n"
    "If you leave <b>one more time</b>, your access will be "
    "<b>permanently blocked</b>.\n"
    "━━━━━━━━━━━━━━━━━━━━━━"
    "</blockquote>"
)

BANNED_MSG = (
    "<blockquote>"
    "🚫  <b>Access Permanently Revoked</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "You have left the required channels after multiple warnings.\n\n"
    "◈  Your access has been permanently blocked\n"
    "◈  This action cannot be undone\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "<i>If you believe this is a mistake, tap Contact Owner below.</i>"
    "</blockquote>"
)


def _is_member(bot, ch, uid):
    try:
        m = bot.get_chat_member(ch, uid)
        return m.status in ("creator", "administrator", "member")
    except Exception as e:
        log.warning("get_chat_member %s uid=%s: %s", ch, uid, e)
        return False


def _check_joined(bot, uid):
    for ch, _ in CHANNELS:
        if not _is_member(bot, ch, uid):
            return False
    return True


def _kb_join():
    mk = types.InlineKeyboardMarkup(row_width=1)
    for ch, name in CHANNELS:
        un = ch.lstrip("@")
        mk.add(types.InlineKeyboardButton(
            f"📢  Join {name}", url=f"https://t.me/{un}"))
    mk.add(types.InlineKeyboardButton(
        "✅  Verify Membership", callback_data="fj_verify"))
    return mk


def _kb_banned(owner_username=None):
    """Contact Owner button. Uses bot_config if available."""
    try:
        import bot_config as _bc
        cfg_un = _bc.get_contact_username()
        if cfg_un:
            owner_username = cfg_un
    except Exception:
        pass
    mk = types.InlineKeyboardMarkup(row_width=1)
    if owner_username:
        un = owner_username.lstrip("@")
        mk.add(types.InlineKeyboardButton(
            "📩  Contact Owner",
            url=f"https://t.me/{un}"))
    return mk


def _safe_delete(bot, chat_id, msg_ids):
    for mid in msg_ids:
        try:
            bot.delete_message(chat_id, mid)
        except Exception:
            pass


def install_fj(bot, owner_id, admin_ids, owner_username=None):
    if isinstance(admin_ids, (list, tuple, set)):
        admin_set = set(admin_ids) | {owner_id}
    else:
        admin_set = {owner_id}

    # Normalize owner username
    if owner_username:
        owner_username = owner_username.lstrip("@").strip()
    else:
        try:
            oc = bot.get_chat(owner_id)
            if oc.username:
                owner_username = oc.username
        except Exception:
            pass

    try:
        me = bot.get_me()
        print(f"[FJ] Bot @{me.username} (id={me.id})", flush=True)
        for ch, _ in CHANNELS:
            try:
                cm = bot.get_chat_member(ch, me.id)
                if cm.status in ("administrator", "creator"):
                    print(f"[FJ] ✅ bot admin in {ch}", flush=True)
                else:
                    print(f"[FJ] ⚠️  bot NOT admin in {ch} ({cm.status})", flush=True)
            except Exception as e:
                print(f"[FJ] ❌ cannot check {ch}: {e}", flush=True)
    except Exception as e:
        print(f"[FJ] get_me error: {e}", flush=True)

    print(f"[FJ] Contact Owner button target: @{owner_username or 'NONE'}", flush=True)

    # ── Verify button ──
    @bot.callback_query_handler(func=lambda c: c.data == "fj_verify")
    def _verify(c):
        uid = c.from_user.id
        st = _get_state(uid)

        now = time.time()
        if now - st["verify_lock"] < 3:
            try: bot.answer_callback_query(c.id)
            except Exception: pass
            return
        st["verify_lock"] = now

        if _is_db_banned(uid):
            try: bot.answer_callback_query(c.id, "🚫 Access revoked", show_alert=True)
            except Exception: pass
            return

        if _check_joined(bot, uid):
            st["joined"] = True

            if not st["verified_msg_sent"]:
                st["verified_msg_sent"] = True

                try:
                    _safe_delete(bot, uid, st["fj_msg_ids"])
                except Exception:
                    pass
                st["fj_msg_ids"] = []

                try:
                    bot.delete_message(c.message.chat.id, c.message.message_id)
                except Exception:
                    pass

                try: bot.answer_callback_query(c.id, "✅ Verified")
                except Exception: pass

                try:
                    bot.send_message(uid, VERIFIED_MSG, parse_mode="HTML")
                except Exception: pass
            else:
                try: bot.answer_callback_query(c.id, "✅ Already verified")
                except Exception: pass
        else:
            try:
                bot.answer_callback_query(c.id,
                    "❌ Please join both channels first.",
                    show_alert=True)
            except Exception: pass

    # ── Update gate ──
    _orig = bot.process_new_updates

    def _patched(updates):
        allowed = []
        for u in updates:
            msg = getattr(u, "message", None) or getattr(u, "edited_message", None)
            cb  = getattr(u, "callback_query", None)

            chat = None
            if msg: chat = msg.chat
            elif cb and cb.message: chat = cb.message.chat

            is_private = (chat and chat.type == "private")

            if chat and chat.type in ("group", "supergroup", "channel"):
                allowed.append(u)
                continue

            user = msg.from_user if msg else (cb.from_user if cb else None)
            if not user:
                allowed.append(u); continue

            if user.id in admin_set:
                allowed.append(u); continue

            if cb and cb.data == "fj_verify":
                allowed.append(u); continue

            # ── DEBUG ──
            _txt = (msg.text[:30] if msg and msg.text else (cb.data if cb else '?'))
            print(f"[FJ-DBG] uid={user.id} chat={chat.type if chat else '?'} "
                  f"text={_txt!r}", flush=True)

            uid = user.id
            st = _get_state(uid)

            # ── Unban detection: was banned, DB no longer has ban ──
            if st.get("was_banned") and not _is_db_banned(uid):
                st["warns"] = 0
                st["ban_msg_sent"] = False
                st["verified_msg_sent"] = False
                st["joined"] = None
                st["was_banned"] = False
                print(f"[FJ] uid={uid} → UNBANNED — state reset", flush=True)

            # ── DB ban check ──
            if _is_db_banned(uid):
                st["was_banned"] = True
                if cb and is_private:
                    try: bot.answer_callback_query(cb.id, "🚫 Access revoked", show_alert=True)
                    except Exception: pass
                elif msg and is_private and not st["ban_msg_sent"]:
                    st["ban_msg_sent"] = True
                    try:
                        bot.send_message(uid, BANNED_MSG,
                                         reply_markup=_kb_banned(owner_username),
                                         parse_mode="HTML")
                    except Exception:
                        pass
                continue

            joined_now = _check_joined(bot, uid)

            # ══════ JOINED ══════
            if joined_now:
                if st["joined"] is False:
                    st["verified_msg_sent"] = False
                    st["start_prompt_at"] = 0
                    print(f"[FJ] uid={uid} → REJOINED (warns={st['warns']})", flush=True)
                st["joined"] = True
                allowed.append(u)
                continue

            # ══════ NOT JOINED ══════

            # Real leave transition
            if st["joined"] is True:
                st["joined"] = False
                st["warns"] += 1
                st["verified_msg_sent"] = False
                w = st["warns"]

                if w >= 3:
                    _add_db_ban(uid, f"Left required channels {w} times")
                    st["ban_msg_sent"] = True
                    st["was_banned"] = True
                    print(f"[FJ] uid={uid} → BANNED (leave #{w})", flush=True)
                    if is_private:
                        try:
                            bot.send_message(uid, BANNED_MSG,
                                             reply_markup=_kb_banned(owner_username),
                                             parse_mode="HTML")
                        except Exception: pass
                elif w == 2:
                    print(f"[FJ] uid={uid} → WARN 2", flush=True)
                    if is_private:
                        try: bot.send_message(uid, WARN_2_MSG,
                                             reply_markup=_kb_join(), parse_mode="HTML")
                        except Exception: pass
                else:
                    print(f"[FJ] uid={uid} → WARN 1", flush=True)
                    if is_private:
                        try: bot.send_message(uid, WARN_1_MSG,
                                             reply_markup=_kb_join(), parse_mode="HTML")
                        except Exception: pass
                continue

            # Still not joined — only /start in DM gets FJ prompt
            if is_private and msg and msg.text:
                t = msg.text.strip().lower()
                if t.startswith("/start"):
                    now = time.time()
                    if now - st["start_prompt_at"] > 60:
                        st["start_prompt_at"] = now
                        try:
                            sent = bot.send_message(uid, FJ_MSG,
                                                    reply_markup=_kb_join(),
                                                    parse_mode="HTML")
                            if sent:
                                st["fj_msg_ids"].append(sent.message_id)
                                if len(st["fj_msg_ids"]) > 5:
                                    st["fj_msg_ids"] = st["fj_msg_ids"][-5:]
                        except Exception:
                            pass
            continue

        return _orig(allowed)

    bot.process_new_updates = _patched
    print("[FJ] ✅ STRICT v17 FINAL — clean, unban-aware", flush=True)
