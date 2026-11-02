#!/usr/bin/env python3
"""Turn the planner (map/index.html) into a new month.

Rewrites the title, Home, Map (rhythm, calendar, goals) and Tracker sections and the
month constants in the script. The Devotional section is month-aware already: it loads
map/<month><year>.json by date.

    python3 map/build_month.py            # writes map/index.html in place

For a new month: copy the MONTH block below, change the dates, weeks and plan, run it.
"""
import calendar
import datetime as dt
import html
import json
import re
from pathlib import Path

E = html.escape
PAGE = Path(__file__).resolve().parent / "index.html"

# ── November 2026 ──────────────────────────────────────────────────────────
YEAR, MONTH = 2026, 11
NAME = calendar.month_name[MONTH]                       # "November"
STATE_ID = f"{NAME.lower()}{YEAR}"                      # "november2026"
POSTURE = ("Romans 12:2", "Do not conform to the pattern of this world, but be transformed by the renewing of your mind.")
MANDATE = "“Few things are needed—or indeed only one.” Luke 10:42"
HOME_TITLE = "Faith First.<br><span>One Thing.</span>"

EXAM = dt.date(2026, 11, 14)          # SecAI+
PAPERS_DUE = dt.date(2026, 11, 30)    # PhD term papers
ARCH_FROM = dt.date(2026, 11, 15)     # architecture track starts

PRIORITY = (f"Faith first, then one thing a day. <b>SecAI+ exam: Saturday 14 November.</b> "
            f"<b>PhD term papers due Monday 30 November</b>, written on Wednesdays and Sundays. "
            f"The <b>MSc push happens every Monday</b> until the department moves. From 15 November, "
            f"30 minutes of <b>architecture</b> a day. The Daily Anchor gates on the laptop hold the line.")

THIS_WEEK = ("Start the 60-day run",
             "Seal the devotion gate every morning. Monday: send the MSc week-1 email (the template is ready). "
             "Every evening: one SecAI+ objective. Wednesday and Sunday: term paper, 90 minutes each.")

MSC_STEPS = {2: "MSc week 1: formal email to supervisor", 9: "MSc week 2: written follow-up + department visit",
             16: "MSc week 3: write to the Programme Coordinator", 23: "MSc week 4: request a meeting with the HOD",
             30: "MSc week 5: formal application if nothing has moved"}

WEEKLY_ONCE = {
    1: [("start-run", "Install the Daily Anchor and seal the first devotion", "2 Nov — the 60-day run begins"),
        ("msc-1", MSC_STEPS[2], "Mon 2 Nov — template in Documents/MSc Escalation"),
        ("exam-check", "Confirm SecAI+ booking, time and ID", "Do it this week, not on the 13th"),
        ("paper-outline", "Outline each term paper: sections and evidence needed", "By Wed 4 Nov")],
    2: [("msc-2", MSC_STEPS[9], "Mon 9 Nov"),
        ("mock", "Full SecAI+ mock in the Simulate arena", "Tue 10 Nov — timed, phone away, score by domain"),
        ("exam", "🎯 Sit the SecAI+ exam", "Sat 14 Nov — steady mind, result met with thanks")],
    3: [("msc-3", MSC_STEPS[16], "Mon 16 Nov — attach the dated log"),
        ("arch-start", "Choose the system design resource and start", "DDIA or the System Design Primer"),
        ("paper-draft", "Term papers: full first drafts", "By Sun 22 Nov")],
    4: [("msc-4", MSC_STEPS[23], "Mon 23 Nov — ask what the PG regulations allow"),
        ("paper-revise", "Term papers: revise, format, check every reference", "By Sun 29 Nov"),
        ("dec-plan", "Set December: Architecture 2 (AWS Well-Architected)", "Sat 28 Nov goal review")],
    5: [("msc-5", MSC_STEPS[30], "Mon 30 Nov"),
        ("papers-submit", "📤 Submit the PhD term papers", "Mon 30 Nov"),
        ("score", "Score November honestly and give thanks", "Mon 30 Nov — 60-day grid: how consistent?")],
}


def learning_for(d: dt.date) -> tuple[str, str]:
    """(label, detail) for the main learning slot on a day."""
    if d == EXAM:
        return "🎯 SecAI+ exam", "Sit the exam. Tonight: 10-minute reflection"
    if d.weekday() in (2, 6) and d <= PAPERS_DUE:
        return "PhD term paper", "90 min · one section, then teach back what you argued"
    if d < EXAM:
        return "SecAI+", "30 min · one objective, then 20 Review cards"
    if d >= ARCH_FROM:
        return "Architecture 1", "30 min · one system design section, applied to NHF Reconciler"
    return "Learning", "30 min"


def cal_note(d: dt.date) -> tuple[str, str]:
    """(css class, short note) for the calendar cell."""
    if d == EXAM:
        return "blk", "🎯 SecAI+ EXAM"
    if d == PAPERS_DUE:
        return "blk", "📤 Papers due · score November"
    if d.day == 1:
        return "grn", "Encounter begins"
    if d.weekday() == 0:
        return "", "MSc push + " + learning_for(d)[0]
    if d.weekday() in (2, 6):
        return "", "Term paper"
    if d.weekday() == 3:
        return "grn", "Family Reading"
    if d.weekday() == 4:
        return "pur", "Movie Night"
    if d.weekday() == 5:
        return "", "Goal review · " + learning_for(d)[0]
    return "", learning_for(d)[0]


# ── builders ───────────────────────────────────────────────────────────────
DAYS = [dt.date(YEAR, MONTH, n) for n in range(1, calendar.monthrange(YEAR, MONTH)[1] + 1)]
DOW = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def short(d: dt.date) -> str:
    return f"{d.day} {d:%b}"


def weeks() -> list[list[dt.date]]:
    out, cur = [], []
    for d in DAYS:
        cur.append(d)
        if len(cur) == 7:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def tag(cls, text, sub=""):
    s = f'<br><span style="font-size:0.6rem">{sub}</span>' if sub else ""
    return f'<span class="tag {cls}">{text}{s}</span>'


def rhythm_table() -> str:
    cols = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    rows = [
        ("8:00 – 9:00am", [tag("bible", "Morning Word")] * 6 + [tag("bible", "Morning Word") + '<br><span style="font-size:0.62rem;color:var(--muted)">+ Church prep</span>']),
        ("Morning drive", [tag("mind", "🎧 Business book")] * 5 + [tag("goal", "9:30 – 10:15am<br>Goal Review"), tag("rest", "Church")]),
        ("9:00am – 6:00pm", [tag("work", "FMBN / ARX AMANI")] * 5 + [tag("secai", "10:00am", "Learning · 30 min"), tag("rest", "Church + Rest")]),
        ("6:00 – 6:30pm", [tag("secai", "Learning", "30 min") + '<br><span style="font-size:0.58rem;color:var(--muted)">+ MSc push</span>',
                           tag("secai", "Learning", "30 min"), tag("reading", "Term paper", "6:00 – 7:30pm"),
                           tag("secai", "Learning", "30 min"), tag("secai", "Learning", "30 min"),
                           tag("reading", "3:00 – 5:00pm<br>Family Reading"), tag("reading", "Term paper", "4:00 – 5:30pm")]),
        ("7:00 – 9:00pm", [tag("rest", "Free / Arx Amani"), tag("rest", "Free / Arx Amani"), tag("rest", "Wind down"),
                           tag("reading", "7:00 – 9:00pm<br>Family Reading"), tag("movie", "7:00 – 8:30pm<br>🎬 Movie Night"),
                           tag("rest", "Family"), tag("rest", "Rest")]),
        ("9:00pm", [tag("prayer", "🙏 Prayer + Bible")] * 7),
        ("11:00pm", [tag("rest", "😴 Lights out")] * 7),
    ]
    head = "".join(f'<th{" class=\"fri-head\"" if c == "Fri" else " class=\"weekend\"" if c in ("Sat", "Sun") else ""}>{c}</th>' for c in cols)
    body = "".join(f'<tr><td class="time-cell">{t}</td>{"".join(f"<td>{c}</td>" for c in cells)}</tr>\n' for t, cells in rows)
    return (f'<div class="table-scroll"><table class="daily-table"><thead><tr><th class="col-time">Time</th>{head}</tr></thead>'
            f'<tbody>\n{body}</tbody></table></div>')


def calendar_grid() -> str:
    cells = ['<div class="cal-cell empty"></div>'] * DAYS[0].weekday()
    for d in DAYS:
        dots = ['<span class="cd b"></span>', '<span class="cd p"></span>']
        if d.weekday() == 5:
            dots.insert(0, '<span class="cd g"></span>')
        if d.weekday() in (3, 5):
            dots.append('<span class="cd r"></span>')
        if d.weekday() == 4:
            dots.append('<span class="cd m"></span>')
        if d.weekday() in (2, 6) and d <= PAPERS_DUE:
            dots.append('<span class="cd s" style="background:#0f766e"></span>')
        elif d != EXAM:
            dots.append('<span class="cd s"></span>')
        cls = "fri" if d.weekday() == 4 else "wknd" if d.weekday() >= 5 else ""
        style = ' style="background:#fff4e6;outline:2px solid var(--accent);outline-offset:-2px"' if d in (EXAM, PAPERS_DUE) else ""
        ncls, note = cal_note(d)
        cells.append(f'<div class="cal-cell {cls}"{style}><span class="cal-num">{d.day}</span><div class="dot-row">{"".join(dots)}</div>'
                     f'<div class="cal-note {ncls}"{" style=\"font-size:0.64rem\"" if ncls == "blk" else ""}>{E(note)}</div></div>')
    while len(cells) % 7:
        cells.append('<div class="cal-cell empty"></div>')
    heads = "".join(f'<div class="month-head">{h}</div>' for h in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    return f'<div class="month-grid">{heads}\n' + "\n".join(cells) + "\n</div>"


def map_section() -> str:
    def card(label, title, text):
        return f'<div class="spirit-card"><div class="s-label">{label}</div><h4>{title}</h4><p>{text}</p></div>'

    def learn(badge_cls, badge, title, text, target):
        return (f'<div class="learn-card"><span class="badge {badge_cls}">{badge}</span><h3>{title}</h3>'
                f'<p>{text}</p><div class="target">{target}</div></div>')

    def anchor(icon, title, text):
        return f'<div class="anchor"><div class="anchor-icon">{icon}</div><div><h4>{title}</h4><p>{text}</p></div></div>'

    def prove(label, text):
        return f'<div class="conf-item"><div class="label">{label}</div><p>{text}</p></div>'

    n = len(DAYS)
    return f"""<div class="site-section" id="section-map"><div class="page">
<div class="page">
  <div class="header">
    <div class="header-left">
      <h1>{NAME} {YEAR}</h1>
      <div class="subtitle">Monthly Map — Gbenga Ogungbemi &nbsp;·&nbsp; Faith first. One thing. Every day.</div>
    </div>
    <div class="mandate">{E(MANDATE)}</div>
  </div>

  <div class="esther-banner"><div class="cross">✝</div><div>
    <span>{NAME} Posture — {POSTURE[0]}</span><p>"{E(POSTURE[1])}"</p>
  </div></div>

  <div class="alert"><strong>⚡ {NAME} Priority</strong> {PRIORITY}</div>

  <div class="section-label">This Week — 2 to 7 {NAME}</div>
  <div class="week-one"><div class="num">01</div><div class="action-text">
    <h3>{E(THIS_WEEK[0])}</h3><p>{E(THIS_WEEK[1])}</p>
  </div></div>

  <div class="section-label">Daily Rhythm — Weekly Template</div>
  {rhythm_table()}

  <div class="section-label">Spiritual Architecture — Daily</div>
  <div class="spiritual">
    {card("Morning — 8 to 9am", "The Word First", "The devotion gate opens when the laptop does. Read the day's devotion, then write what God said and what you'll do. Nothing else opens first.")}
    {card("Night — 9pm", "Prayer & Night Bible", "The evening email brings the day's questions and prayer. Answer one honestly, pray, and tick the day. Close every day the same way.")}
    {card("Morning Drive", "Business Books", "The drive is Arx Amani's classroom. One book at a time on audio, tested on real clients the same week.")}
    {card("Weekly — Saturday 9:30am", "Goal Review + 60-Day Grid", "45 minutes. Look at the grid: devotion and learning, day by day. Consistency, not volume. Adjust and move.")}
  </div>

  <div class="section-label">Learning Stack — {NAME} Targets</div>
  <div class="learn-grid">
    {learn("secai-b", "Priority 1 · until 14 Nov", "SecAI+<br>CY0-001", "One objective a night in the SecAI app, then 20 Review cards. One full mock on Tuesday 10 November.", "▸ Mock: Tue 10 Nov<br>▸ Exam: Sat 14 Nov")}
    {learn("coursera-b", "Wed + Sun · due 30 Nov", "PhD<br>Term Papers", "90-minute writing sessions on Wednesdays and Sundays. Outline by the 4th, full drafts by the 22nd, revised and submitted by the 30th.", "▸ Drafts: Sun 22 Nov<br>▸ Submit: Mon 30 Nov")}
    {learn("thm-b", "From 15 Nov", "Architecture 1<br>System Design", "30 minutes a day: scaling, caching, queues, databases, consistency. Apply each section to a system you built. The road to a remote architecture role.", "▸ DDIA / System Design Primer<br>▸ Teach back daily")}
  </div>

  <div class="section-label">Fixed Anchors — Unmovable</div>
  <div class="anchors">
    {anchor("📖", "Word — Morning & Night", f"Every day. The devotion gate at login, prayer and Bible at 9pm. {n} mornings, {n} nights.")}
    {anchor("🎓", "MSc Push — Monday", "Every Monday, one written step up the ladder, logged and dated, until the department moves.")}
    {anchor("📚", "Family Reading — Thu & Sat", "Thursday 7–9pm. Saturday 3–5pm. Protected, exam week included.")}
    {anchor("📊", "Goal Review — Sat 9:30am", "45 minutes. Spiritual, learning, PhD, MSc, family, work. Score it honestly.")}
    {anchor("🎬", "Movie Night — Friday", "It stays. A rested mind learns more than a crammed one.")}
    {anchor("😴", "Lights Out — 11pm", "He grants sleep to those He loves. Rest is part of the race, not a break from it.")}
  </div>

  <div class="section-label">{NAME} {YEAR} — Full Month</div>
  {calendar_grid()}

  <div class="legend">
    <div class="legend-item"><div class="ld" style="background:var(--bible)"></div>Morning Word + night Bible</div>
    <div class="legend-item"><div class="ld" style="background:var(--gold)"></div>Prayer (9pm daily)</div>
    <div class="legend-item"><div class="ld" style="background:var(--green)"></div>Family Reading (Thu + Sat)</div>
    <div class="legend-item"><div class="ld" style="background:var(--accent)"></div>Goal Review (Sat 9:30)</div>
    <div class="legend-item"><div class="ld" style="background:var(--purple)"></div>Movie Night (Fri)</div>
    <div class="legend-item"><div class="ld" style="background:var(--steel-l)"></div>Learning (SecAI+, then architecture)</div>
    <div class="legend-item"><div class="ld" style="background:#0f766e"></div>PhD term paper (Wed + Sun)</div>
  </div>

  <div class="confession">
    <h2>What {NAME} Must Prove by {NAME} {DAYS[-1].day}</h2>
    <div class="conf-grid">
      {prove("The Spiritual Question", f"{n} devotions sealed in writing. {n} nights closed in prayer. Faith first on the hard days too.")}
      {prove("The Exam Question", "SecAI+ sat on 14 November with a steady mind, after a nightly objective and one full mock. The result met with thanks either way.")}
      {prove("The PhD Question", "Every Wednesday and Sunday session kept. Term papers submitted by 30 November, references checked.")}
      {prove("The MSc Question", "Every Monday push logged. If the supervisor stays silent, the Coordinator and HOD have the dated record by the 23rd.")}
      {prove("The Architecture Question", "From the 15th, a system design section a day, taught back in your own words. The first step toward the remote role.")}
      {prove("The Rest Question", "Family reading on Thursdays and Saturdays, movie night on Fridays, lights out by 11pm.")}
    </div>
  </div>

  <div class="footer"><span>Gbenga Ogungbemi — {NAME} {YEAR}</span><span>Faith · Growth · Work · Excellence · Family</span></div>
</div>
</div></div>
"""


def item(iid, text, tag_cls, tag_text, sub):
    return (f'      <div class="check-item" id="{iid}" onclick="toggle(this)"><div class="checkbox"></div><div class="item-body">'
            f'<div class="item-text">{E(text)} <span class="item-tag {tag_cls}">{E(tag_text)}</span></div>'
            f'<div class="item-sub">{E(sub)}</div></div></div>\n')


def section(head_cls, title, wk, key, items):
    if not items:
        return ""
    return (f'    <div class="section">\n      <div class="section-head {head_cls}"><span>{title} — Week {wk}</span>'
            f'<span class="sec-count" id="cnt-w{wk}-{key}"></span></div>\n{"".join(items)}    </div>\n\n')


def tracker_section() -> str:
    ws = weeks()
    tabs = "".join(f'<div class="tab{" active" if i == 1 else ""}" onclick="switchWeek({i})">Wk {i}<br>'
                   f'<span style="font-size:0.55rem">{w[0].day}–{w[-1].day} {w[0]:%b}</span></div>\n    '
                   for i, w in enumerate(ws, 1))
    panels = ""
    for i, w in enumerate(ws, 1):
        crit = [item(f"w{i}-{k}", t, "tag-once", "Once", s) for k, t, s in WEEKLY_ONCE.get(i, [])]
        spirit, learn, read, fam = [], [], [], []
        for d in w:
            dn, ds, k = DOW[d.weekday()], short(d), f"{d:%a}".lower() + str(d.day)
            spirit.append(item(f"w{i}-word-{k}", f"{dn} — Morning Word (gate sealed)", "tag-daily", "8–9am", ds))
            spirit.append(item(f"w{i}-prayer-{k}", f"{dn} — Night Prayer + Bible", "tag-daily", "9pm", ds))
            label, detail = learning_for(d)
            learn.append(item(f"w{i}-learn-{k}", f"{dn} — {label}", "tag-fire" if d in (EXAM, PAPERS_DUE) else "tag-daily", "Gate", f"{ds} — {detail}"))
            if d.weekday() < 5:
                read.append(item(f"w{i}-book-{k}", f"{dn} — Business book on the drive", "tag-daily", "Drive", ds))
            if d.weekday() == 3:
                fam.append(item(f"w{i}-family-{k}", "Thursday — Family Reading", "tag-daily", "7–9pm", ds))
            if d.weekday() == 4:
                fam.append(item(f"w{i}-movie-{k}", "Friday — Movie Night", "tag-daily", "7–8:30pm", ds))
            if d.weekday() == 5:
                fam.append(item(f"w{i}-goal-{k}", "Saturday — Goal Review + 60-day grid", "tag-daily", "9:30am", ds))
                fam.append(item(f"w{i}-family-{k}", "Saturday — Family Reading", "tag-daily", "3–5pm", ds))
        panels += (f'  <div class="week-panel{" active" if i == 1 else ""}" id="week-{i}">\n\n'
                   + section("goal-h", "🔴 Non-Negotiable", i, "crit", crit)
                   + section("bible-h", "✝ Spiritual", i, "spirit", spirit)
                   + section("learn-h", "📱 Learning", i, "learn", learn)
                   + section("spirit-h", "📖 Reading", i, "read", read)
                   + section("family-h", "🎬 Family", i, "fam", fam)
                   + "  </div>\n\n")
    return f"""<div class="site-section" id="section-checklist"><div class="page">
<div class="page">

  <div class="header">
    <h1>{NAME} {YEAR} Tracker</h1>
    <div class="sub">Gbenga Ogungbemi &nbsp;·&nbsp; Daily Accountability</div>
    <div class="esther">"{E(POSTURE[1])}" — {POSTURE[0]}</div>
  </div>

  <div class="score-card" id="scoreCard">
    <div class="score-item"><span class="score-num green" id="doneCount">0</span><span class="score-label">Completed</span></div>
    <div class="score-item"><span class="score-num gold" id="totalCount">0</span><span class="score-label">Total Items</span></div>
    <div class="score-item"><span class="score-num red" id="pctCount">0%</span><span class="score-label">{NAME} Score</span></div>
  </div>

  <div class="progress-label"><span>{NAME} Progress</span><span class="progress-pct" id="progressPct">0%</span></div>
  <div class="progress-wrap"><div class="progress-bar" id="progressBar"></div></div>

  <div class="tabs">
    {tabs}</div>

{panels}
  <div class="actions">
    <button class="btn btn-save" onclick="saveProgress()">💾 Save Progress</button>
    <button class="btn btn-reset" onclick="resetAll()">Reset All</button>
  </div>

  <div class="footer"><span>{NAME} {YEAR} — Gbenga Ogungbemi</span><span>Faith · Growth · Work · Excellence</span></div>

</div>

<!-- TOAST -->
<div class="toast" id="toast">Progress Saved</div>

</div></div>
"""


def main() -> None:
    t = PAGE.read_text(encoding="utf-8")
    old = re.search(r"const STATE_ID = '([a-z]+)(\d{4})';", t)
    old_name = old.group(1).capitalize()

    t = re.sub(r"<title>.*?</title>", f"<title>{NAME} {YEAR} — Gbenga Ogungbemi</title>", t, count=1)
    t = re.sub(r'(<span class="cross">✝</span><span>)[^<]*(</span>)', rf"\g<1>{NAME} {YEAR}\g<2>", t, count=1)
    t = re.sub(r'(<span class="tab-icon">🗓</span> )\w+ Map', rf"\g<1>{NAME} Map", t, count=1)
    t = re.sub(r'<p class="sub">Gbenga Ogungbemi · [^<]*</p>', f'<p class="sub">Gbenga Ogungbemi · {NAME} {YEAR}</p>', t, count=1)
    t = re.sub(r'(<div class="home-section">.*?<h1>).*?(</h1>)', rf"\g<1>{HOME_TITLE}\g<2>", t, count=1, flags=re.S)
    t = re.sub(r'<p class="tagline">Your complete \w+ —', f'<p class="tagline">Your complete {NAME} —', t, count=1)
    t = re.sub(r'<div class="home-esther">.*?</div>', f'<div class="home-esther">"{E(POSTURE[1])}" — {POSTURE[0]}</div>', t, count=1)
    t = re.sub(r"<h3>\w+ Map</h3>\s*<p>[^<]*</p>",
               f"<h3>{NAME} Map</h3>\n        <p>Your monthly rhythm — faith first, the learning stack, PhD and MSc milestones, fixed anchors and the full calendar.</p>", t, count=1)
    t = re.sub(r"<h3>\d+-Day Devotional</h3>\s*<p>[^<]*</p>",
               f"<h3>{len(DAYS)}-Day Devotional</h3>\n        <p>Encounter {NAME}. Opens with the devotion gate at login, and is emailed at 8am and 8:30pm.</p>", t, count=1)

    t = re.sub(r'<div class="site-section" id="section-map">.*?(?=<div class="site-section" id="section-checklist">)',
               lambda m: map_section(), t, count=1, flags=re.S)
    t = re.sub(r'<div class="site-section" id="section-checklist">.*?(?=<div class="site-section" id="section-devotional">)',
               lambda m: tracker_section(), t, count=1, flags=re.S)

    # Devotional cover: write the month's own text statically (dressCover() repeats it at runtime)
    dev = json.loads((PAGE.parent / f"{STATE_ID}.json").read_text(encoding="utf-8"))
    themes = "".join(f'\n      <span class="theme-tag">{E(v)}</span>' for v in dev["themes"].values())
    t = re.sub(r'(<div class="dev-cover-content">.*?<h1>Encounter<br><span>)[^<]*(</span></h1>)',
               rf"\g<1>{NAME} {YEAR}\g<2>", t, count=1, flags=re.S)
    t = re.sub(r'(<div class="dev-cover-content">.*?<p class="tagline">).*?(</p>)',
               lambda m: f"{m.group(1)}A {len(dev['days'])}-Day Personal Devotional<br>for Gbenga Ogungbemi{m.group(2)}",
               t, count=1, flags=re.S)
    t = re.sub(r'(<div class="dev-cover-content">.*?<div class="themes">).*?(\n    </div>)',
               lambda m: m.group(1) + themes + m.group(2), t, count=1, flags=re.S)
    t = re.sub(r'<span class="logo">✝ Encounter \w+</span>', f'<span class="logo">✝ Encounter {NAME}</span>', t, count=1)

    t = t.replace(f"const STATE_ID = '{old.group(0)[18:-2]}';", f"const STATE_ID = '{STATE_ID}';")
    t = re.sub(r"const STORAGE_KEY = '[a-z]+\d{4}_gbenga';", f"const STORAGE_KEY = '{STATE_ID}_gbenga';", t, count=1)
    t = t.replace(f"Reset all progress for {old_name}?", f"Reset all progress for {NAME}?")
    PAGE.write_text(t, encoding="utf-8")
    print(f"{old_name} → {NAME} {YEAR}: {t.count('class=\"check-item\"')} tracker items, STATE_ID={STATE_ID}")


if __name__ == "__main__":
    main()
