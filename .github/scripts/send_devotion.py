#!/usr/bin/env python3
"""
Morning and evening devotion emails for the monthly planner.

Run by .github/workflows/devotion-reminders.yml. Standard library only.

  EDITION              morning | evening
  GMAIL_ADDRESS        the Gmail account that sends
  GMAIL_APP_PASSWORD   a Gmail app password for that account (not the login password)
  DEVOTION_RECIPIENTS  comma-separated list of addresses
  DEVOTION_DATE        optional, e.g. "13 Oct" — send that day instead of today
  DRY_RUN              optional, "1" writes the email to devotion-preview.html and sends nothing
"""

import datetime as dt
import html
import json
import os
import smtplib
import sys
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "map" / "october2026.json"
PLANNER = "https://thesecuredanalyst.github.io/map/"
EXAM = dt.date(2026, 10, 13)

E = html.escape
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

THEME_COLOUR = {"mind": "#0d9488", "womb": "#be185d", "lead": "#1e3a8a", "encounter": "#7c3aed"}


def lagos_today() -> dt.date:
    # Africa/Lagos is UTC+1 all year, no DST.
    return (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1)).date()


def key(d: dt.date) -> str:
    return f"{d.day} {MONTHS[d.month - 1]}"


def countdown(today: dt.date) -> str:
    left = (EXAM - today).days
    if left > 1:
        return f"SecAI+ exam in {left} days"
    if left == 1:
        return "SecAI+ exam is tomorrow"
    if left == 0:
        return "SecAI+ exam today"
    return ""


# ── building blocks (inline styles only — Gmail and Outlook strip <style>) ──
def p(text, style=""):
    return f'<p style="margin:0 0 14px;font-size:16px;line-height:1.65;color:#1f2937;{style}">{text}</p>'


def label(text, colour="#b45309"):
    return (f'<div style="font-family:Consolas,Menlo,monospace;font-size:11px;letter-spacing:2px;'
            f'text-transform:uppercase;color:{colour};margin:0 0 8px;">{text}</div>')


def box(inner, bg, border, pad="18px 20px"):
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;">'
            f'<tr><td style="background:{bg};border-left:4px solid {border};padding:{pad};">{inner}</td></tr></table>')


def shell(preheader, header_html, body_html):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light only"><title>Encounter</title></head>
<body style="margin:0;padding:0;background:#f3efe7;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">{E(preheader)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f3efe7;">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#fdfbf7;border:1px solid #e5ddd0;">
{header_html}
<tr><td style="padding:28px 28px 8px;font-family:Georgia,'Times New Roman',serif;">{body_html}</td></tr>
<tr><td style="padding:18px 28px 26px;border-top:1px solid #e5ddd0;font-family:Arial,Helvetica,sans-serif;font-size:12px;line-height:1.6;color:#94a3b8;">
Encounter · October 2026 · Gbenga Ogungbemi<br>
Faith · Growth · Work · Excellence · Family<br>
<a href="{PLANNER}" style="color:#b45309;">Open the planner</a></td></tr>
</table></td></tr></table></body></html>"""


def header(kicker, title, sub, chip, bg):
    chip_html = (f'<span style="display:inline-block;background:#f97316;color:#fff;font-family:Arial,Helvetica,sans-serif;'
                 f'font-size:11px;font-weight:bold;letter-spacing:1px;text-transform:uppercase;padding:4px 10px;border-radius:12px;">{E(chip)}</span>'
                 if chip else "")
    solid = bg.split("#")[1][:6]
    return f"""<tr><td style="background-color:#{solid};background-image:{bg};padding:26px 28px 24px;">
<div style="font-family:Consolas,Menlo,monospace;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#f59e0b;margin-bottom:10px;">{kicker}</div>
<div style="font-family:Georgia,'Times New Roman',serif;font-size:26px;line-height:1.2;font-weight:bold;color:#ffffff;margin-bottom:8px;">{E(title)}</div>
<div style="font-family:Georgia,'Times New Roman',serif;font-style:italic;font-size:15px;color:#cbd5e1;margin-bottom:{12 if chip else 0}px;">{E(sub)}</div>
{chip_html}</td></tr>"""


def button(text, href):
    return (f'<table role="presentation" cellpadding="0" cellspacing="0" style="margin:6px 0 22px;"><tr>'
            f'<td style="background:#f59e0b;"><a href="{href}" style="display:inline-block;padding:12px 22px;'
            f'font-family:Arial,Helvetica,sans-serif;font-size:13px;font-weight:bold;letter-spacing:1px;'
            f'text-transform:uppercase;color:#1a0d05;text-decoration:none;">{text}</a></td></tr></table>')


def day_name(d):
    return "Threshold" if d["day"] == 0 else f"Day {d['day']}"


def subject_tag(d):
    return "Special" if d["day"] == 0 else f"Day {d['day']}"


# ── the two editions ──
def morning(d, themes, today):
    chip = countdown(today)
    head = header(f"☀ Morning · {E(d['dow'])} {E(d['date'])} · {day_name(d)} · {E(themes[d['theme']])}",
                  d["title"], d["verse"], chip, "linear-gradient(135deg,#0d1526,#1e2d4a)")
    body = box(label("Today's focus") + p(E(d["focus"]), "margin:0;font-family:Arial,Helvetica,sans-serif;font-size:15px;"),
               "#fdf3e2", "#f59e0b")
    body += box(label("📖 " + E(d["verse"])) +
                p(E(d["verseText"]), "margin:0;font-style:italic;font-size:18px;color:#111827;"),
                "#f8f2e6", "#d97706", "20px 22px")
    body += label("Reflection", "#64748b")
    body += "".join(p(E(para)) for para in d["reflection"].split("\n\n"))
    body += box(label("Declaration", "#f59e0b") +
                p(E(d["declaration"]), "margin:0;font-style:italic;color:#ffffff;font-size:17px;"),
                "#1e2d4a", "#f59e0b", "20px 22px")
    body += p("Tonight at 8:30 you’ll get the study questions and the prayer. Until then — carry the declaration into the day.",
              "font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#64748b;")
    body += button("Open today in the planner →", PLANNER)
    subject = f"☀ {subject_tag(d)} · {d['title']} — {d['verse']}"
    pre = f"{d['verse']} · {d['focus']}"
    text = (f"{day_name(d)} · {d['dow']} {d['date']}\n{d['title']}\n\n{d['verse']}\n{d['verseText']}\n\n"
            f"TODAY'S FOCUS\n{d['focus']}\n\n{d['reflection']}\n\nDECLARATION\n{d['declaration']}\n\n{PLANNER}\n")
    return subject, shell(pre, head, body), text


def evening(d, nxt, themes, today):
    head = header(f"🌙 Evening · 9pm Prayer · {E(d['dow'])} {E(d['date'])} · {day_name(d)}",
                  d["title"], "Close the day the same way, whatever it delivered.", "", "linear-gradient(135deg,#1a0635,#0d1526)")
    qs = "".join(f'<li style="margin:0 0 10px;font-size:16px;line-height:1.55;color:#1f2937;">{E(q)}</li>' for q in d["questions"])
    body = label("Study questions — answer one honestly", "#64748b")
    body += f'<ol style="margin:0 0 22px;padding-left:22px;">{qs}</ol>'
    body += box(label("Prayer", "#fecdd3") + p(E(d["prayer"]), "margin:0;color:#ffffff;font-family:Arial,Helvetica,sans-serif;"),
                "#9f1239", "#e11d48", "20px 22px")
    body += box(label("Before you sleep") +
                p("☐ Night prayer + Bible&nbsp;&nbsp; ☐ Duolingo Dutch&nbsp;&nbsp; ☐ Tick today in the tracker",
                  "margin:0;font-family:Arial,Helvetica,sans-serif;font-size:15px;"),
                "#fdf3e2", "#f59e0b")
    if nxt:
        body += box(label("Tomorrow", "#64748b") +
                    p(f"<b>{E(nxt['title'])}</b> — {E(nxt['verse'])}", "margin:0 0 6px;") +
                    p(E(nxt["focus"]), "margin:0;font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#64748b;"),
                    "#ffffff", "#cbd5e1")
    body += button("Tick today in the tracker →", PLANNER)
    subject = f"🌙 Tonight’s prayer · {subject_tag(d)} · {d['title']}"
    pre = d["questions"][0]
    text = (f"{day_name(d)} · {d['dow']} {d['date']} · 9pm\n{d['title']}\n\nSTUDY QUESTIONS\n" +
            "\n".join(f"{i}. {q}" for i, q in enumerate(d["questions"], 1)) +
            f"\n\nPRAYER\n{d['prayer']}\n\n" + (f"TOMORROW\n{nxt['title']} — {nxt['verse']}\n\n" if nxt else "") + PLANNER + "\n")
    return subject, shell(pre, head, body), text


def main():
    edition = os.environ.get("EDITION", "morning").strip().lower()
    data = json.loads(DATA.read_text(encoding="utf-8"))
    days = data["days"]
    today = lagos_today()
    want = os.environ.get("DEVOTION_DATE", "").strip() or key(today)

    idx = next((i for i, d in enumerate(days) if d["date"] == want), None)
    if idx is None:
        print(f"No devotion for {want} in {DATA.name} — nothing to send.")
        return
    d = days[idx]
    nxt = days[idx + 1] if idx + 1 < len(days) else None

    if edition == "evening":
        subject, body_html, body_text = evening(d, nxt, data["themes"], today)
    else:
        subject, body_html, body_text = morning(d, data["themes"], today)

    if os.environ.get("DRY_RUN") == "1":
        out = Path(os.environ.get("PREVIEW_PATH", "devotion-preview.html"))
        out.write_text(body_html, encoding="utf-8")
        print(f"[dry run] {subject}\n  -> {out}")
        return

    sender = os.environ["GMAIL_ADDRESS"].strip()
    password = os.environ["GMAIL_APP_PASSWORD"].replace(" ", "").strip()
    to = [a.strip() for a in os.environ["DEVOTION_RECIPIENTS"].split(",") if a.strip()]
    if not to:
        sys.exit("DEVOTION_RECIPIENTS is empty")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=60) as smtp:
        smtp.login(sender, password)
        for rcpt in to:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = formataddr(("Encounter · Daily Devotion", sender))
            msg["To"] = rcpt
            msg["Message-ID"] = make_msgid(domain=sender.split("@")[-1])
            msg.set_content(body_text)
            msg.add_alternative(body_html, subtype="html")
            smtp.send_message(msg)
            print(f"{edition} · {want} -> {rcpt} ok")


if __name__ == "__main__":
    main()
