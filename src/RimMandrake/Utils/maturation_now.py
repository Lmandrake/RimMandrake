#!/usr/bin/env python3
"""maturation_now.py: the Maturation Pipeline's status page, regenerated from files with no model call.

The owner, 2026-11-14 ~11:25 AM PST: "I need MATURATION_NOW to be MUCH more beautiful, to the same level as the other
NOW.md. It's too coarse for me to get an intuitive understanding of the pipeline status and mod status."
Item RIMMANDRAKE_BUILD_MATURATION_PAGE_NO_TOKENS_SPENT; spec design/specs/2026-11-13-maturation-pipeline.md (§3 the map,
§6 what is tracked on each mod, §9 the pipeline's own bar 2: "He can see where every mod stands on one page that a
program regenerates without tokens").

Writes D:\\ClaudeWork\\rimmandrake\\conductor\\MATURATION_NOW.md (read in Typora) and MATURATION_NOW.html beside it.

    python3 src/RimMandrake/Utils/maturation_now.py            build and write both pages
    python3 src/RimMandrake/Utils/maturation_now.py --print    the Markdown page to stdout, write nothing
    python3 src/RimMandrake/Utils/maturation_now.py --json     the gathered facts to stdout, write nothing
        --root DIR   read design/ from DIR instead of this repo (the selftest's temp copies)
        --no-live    do not read the ledger or the detached-run records (their fields print UNMEASURED)
        --out DIR    write the two pages to DIR

WHAT IT READS, per mod (a mod is a design/concepts/<Folder>/ holding version/VERSION.json; folders starting "_" skip):
  version/VERSION.json   Design Version, its state, bars total and met by the last judge, judge rounds, tokens
  stage.json             the Designer record: its inner step (0 Read .. 5 Lock), status, budget charges, history times
  journal.md             the steward's journal (spec §5): "**Stage now:**", "**Waiting on:**", "**Next:**",
                         "**Open questions for him:**" lines in "The mod as it stands", and the dated "### " history
  version/test_table.json  the bars-to-tests table (pilot row 2): runnable and green counts, the stage each bar proves at
  src/RimMandrake/<Folder>/About/About.xml   the display name (else the folder name split at its capitals)
Pipeline stage: the journal's "Stage now" line when there is one; else a locked VERSION.json places the mod at the door
of Stage 2 (Stage 1's exit is the lock) and a "not started" one holds it at intake; else UNMEASURED. The page says which.
Live reads (off with --no-live): owner_queue.needs_you() for the intake count (its first-touch rows) and for his open
questions, a question counting for a mod when its item id or its first word names the mod; detached_helper's run
records (with systemd's unit state, local) for which mods have a helper on them.
Held look statements: the Contents table of design/RimMandrake/validation_holding/README.md; a file there whose name ends
in a mod's name is that mod's; a file the table does not count leaves the total UNMEASURED.

Rules. Anything it cannot read prints UNMEASURED, never a guess or a zero. Two runs on an unchanged tree differ only in
the "**Measured" line: no "minutes ago", only Pacific clock times. Typora: every HTML block is ONE line with no blank line
in it (a blank line ends the block and spills the rest as text), no <details>, and the picture paints its own dark card
so it reads the same in a light or dark theme. Colour is never alone: every chip carries its word. Stdlib only, no
network, no model. Selftest: selftest_maturation_now.py (the item's seven acceptance points).
"""

import argparse
import datetime as dt
import glob
import html
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT_DIR = os.environ.get("MATURATION_NOW_OUT", "/mnt/d/ClaudeWork/rimmandrake/conductor")
NATIVE_OUT = r"D:\ClaudeWork\rimmandrake\conductor"
NATIVE_REPO = r"D:\Luke\dev\RimMandrake"     # the read-only mirror of origin/main he opens files in
PAC = ZoneInfo("America/Los_Angeles")
UNM = "UNMEASURED"

# The map (spec §3; stage numbers are his; Stages 4 and 5 are one stage, tests first, his card 2026-11-13).
COLUMNS = ("intake", "1", "2", "3", "4+5", "6", "7", "8", "passed")
COL_NUM = {"intake": "IN", "1": "1", "2": "2", "3": "3", "4+5": "4+5", "6": "6", "7": "7", "8": "8", "passed": "✓"}
COL_NAME = {"intake": "Intake", "1": "Designer", "2": "Preflight", "3": "Offline build", "4+5": "Tests first",
            "6": "In-game", "7": "Pre-human", "8": "His walk", "passed": "Passed"}
COL_LONG = {"intake": "ideas waiting", "1": "vision, bars, lock", "2": "spec checked", "3": "code + tests",
            "4+5": "blind judge", "6": "dense maps", "7": "evidence check", "8": "Mandrake looks",
            "passed": "the mod rests"}
DESIGNER_STEPS = {0: "Read", 1: "Argue the idea", 2: "Argue the edge", 3: "Write", 4: "Exam", 5: "Lock"}  # fallback only

# Palette: running_now.py / artisan_now.py, so the NOW pages read as one family.
BG, CARD, EDGE, TEXT, DIM, FAINT = "#14171c", "#1f242c", "#3a4250", "#e8eaee", "#a2abb8", "#5d6675"
ALERT, INK = "#ff8a7a", "#0b0f14"
DONE = "#2f5f4c"
STATUS = {   # key: (fill, text colour, word on the chip, legend line)
    "helper": ("#2aa98a", INK, "helper on it", "a helper is on it now"),
    "waiting": ("#b28a00", INK, "waiting", "waiting for its next step"),
    "held": ("hatch", TEXT, "held", "held on purpose"),
    "unknown": ("#6b7380", TEXT, "stage unread", "its stage could not be read"),
}
FONT = "'Segoe UI',Helvetica,Arial,sans-serif"


# ---- small readers ----------------------------------------------------------------------------------------------

def read_json(path):
    """-> (data, None) or (None, reason)."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, "no file"
    except (OSError, ValueError) as e:
        return None, "unreadable (%s)" % e.__class__.__name__


def known(v):
    return v is not None and v != "" and v != UNM


def num(v):
    """An int read from a file, or UNMEASURED (a string such as "UNMEASURED" or a missing key is never a zero)."""
    return v if isinstance(v, int) and not isinstance(v, bool) else UNM


def spaced(folder):
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", folder)


def display_name(root, folder):
    p = os.path.join(root, "src", "RimMandrake", folder, "About", "About.xml")
    try:
        n = (ET.parse(p).getroot().findtext("name") or "").strip()
    except (OSError, ET.ParseError):
        n = ""
    n = re.sub(r"^RimMandrake:\s*", "", n)
    return n or spaced(folder)


def pac(t):
    """An aware datetime -> '11:21 AM PST, Sat Nov 14'."""
    t = t.astimezone(PAC)
    return "%s %s, %s" % (t.strftime("%I:%M %p").lstrip("0"), t.strftime("%Z"), t.strftime("%a %b ") + str(t.day))


def parse_utc(s):
    try:
        t = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def tokens_word(n):
    if not isinstance(n, int):
        return UNM
    return "%.1f M" % (n / 1e6) if n >= 1e6 else "{:,}".format(n)


# ---- the journal -------------------------------------------------------------------------------------------------

FIELD = {"stage": "Stage now", "waits_on": "Waiting on", "next": "Next", "questions": "Open questions for him",
         "version": "Design Version"}
HIST = re.compile(r"^###\s+(\d{4}-\d{2}-\d{2})\s+(\d{1,2}):(\d{2})\s*(AM|PM)?\s*(PST|PDT)?\s*[,:]?\s*(.*)$", re.M)


def strip_md(s):
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = re.sub(r"\*\*([^*]*)\*\*", r"\1", s)
    return s.strip().rstrip(".").strip()


def parse_journal(text):
    """-> {field: text} for the "**Field:**" lines of "The mod as it stands" (first occurrence each), plus
    "history": [(aware datetime, heading)]."""
    out = {}
    for key, word in FIELD.items():
        m = re.search(r"^\s*-\s*\*\*%s[^*]*:?\*\*:?\s*(.+)$" % re.escape(word), text, re.M)
        if m:
            out[key] = strip_md(m.group(1))
    hist = []
    for m in HIST.finditer(text):
        h, mi = int(m.group(2)), int(m.group(3))
        if m.group(4) == "PM" and h < 12:
            h += 12
        if m.group(4) == "AM" and h == 12:
            h = 0
        try:
            t = dt.datetime.strptime(m.group(1), "%Y-%m-%d").replace(hour=h, minute=mi, tzinfo=PAC)
        except ValueError:
            continue
        hist.append((t, strip_md(m.group(6))))
    out["history"] = hist
    return out


def stage_from_text(s):
    """A "Stage now" line -> (column, at_the_door) or (None, False) when it names no stage."""
    low = s.lower()
    if re.search(r"\bpassed\b|version passed", low) and "not passed" not in low:
        return "passed", False
    m = re.search(r"door of stages?\s*(\d)", low) or re.search(r"\bstages?\s*(\d)\s*(?:\([^)]*\)\s*)?(?:is\s+)?next\b", low)
    door = bool(m)        # "Stage 1 finished ...; Stage 2 next" stands at Stage 2's door
    if not m:
        m = re.search(r"\bstages?\s*(\d)", low)
    if m:
        n = int(m.group(1))
        return ("4+5" if n in (4, 5) else str(n)) if 1 <= n <= 8 else None, door
    if "intake" in low:
        return "intake", False
    return None, False


# ---- one mod -----------------------------------------------------------------------------------------------------

def designer_names():
    try:
        sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
        import designer_stage as DS  # noqa: E402
        return dict(DS.STAGE_NAMES)
    except Exception:       # noqa: BLE001  the page still builds; the fallback is the spec's own table
        return dict(DESIGNER_STEPS)


def read_mod(root, folder, names):
    c = os.path.join(root, "design", "concepts", folder)
    v, verr = read_json(os.path.join(c, "version", "VERSION.json"))
    v = v or {}
    s, serr = read_json(os.path.join(c, "stage.json"))
    tt, tterr = read_json(os.path.join(c, "version", "test_table.json"))
    try:
        jtext = open(os.path.join(c, "journal.md"), encoding="utf-8").read()
    except OSError:
        jtext = None
    j = parse_journal(jtext) if jtext is not None else {"history": []}
    m = {"name": folder, "label": display_name(root, folder), "unread": []}
    m["version"] = str(v["version"]) if known(v.get("version")) else UNM
    m["state"] = str(v["state"]) if known(v.get("state")) else UNM
    m["scope"] = str(v.get("scope") or "")
    m["bars_total"], m["bars_met"] = num(v.get("bars_total")), num(v.get("bars_met"))
    m["judge_rounds"], m["tokens"] = num(v.get("judge_rounds")), num(v.get("tokens_spent"))
    m["locked_on"] = v.get("locked_on") or ""
    # the Designer record
    if s is None:
        m["designer_step"], m["designer_status"], m["designer_why"] = UNM, UNM, ""
        m["unread"].append("stage.json: %s" % serr)
        m["estimates"] = UNM
    else:
        st = s.get("stage")
        m["designer_step"] = st if isinstance(st, int) else UNM
        m["designer_step_name"] = names.get(st, UNM) if isinstance(st, int) else UNM
        m["designer_status"] = str(s.get("status")) if known(s.get("status")) else UNM
        why = str(s.get("blocked_on") or "")
        why = re.sub(r"^REFUSAL_NOTHING_COULD_EVER_PASS:\s*", "", why)
        m["designer_why"] = why.split(";")[0].strip()
        ch = ((s.get("budget") or {}).get("charges")) or []
        m["estimates"] = sum(int(x.get("tokens") or 0) for x in ch if x.get("kind") == "unmeasured") if ch else UNM
    # the test table
    m["table"] = None
    if tt is not None:
        bars = tt.get("bars") if isinstance(tt.get("bars"), list) else None
        t = {"version": str(tt.get("version") or UNM), "made": str(tt.get("made") or "")}
        if bars is not None:
            t["bars"] = len(bars)
            for key in ("any_test_runnable_today", "every_decider_runnable_today", "offline_green_today"):
                vals = [b.get(key) for b in bars if isinstance(b, dict)]
                t[key] = sum(1 for x in vals if x is True) if vals and all(isinstance(x, bool) for x in vals) else UNM
            pa = {}
            for b in bars:
                if isinstance(b, dict) and known(b.get("proves_at")):
                    pa[str(b["proves_at"])] = pa.get(str(b["proves_at"]), 0) + 1
            t["proves_at"] = pa
            t["held"] = num(tt.get("held_statements"))
        m["table"] = t
    elif tterr != "no file":
        m["unread"].append("version/test_table.json: %s" % tterr)
    # where it stands on the map
    m["journal"] = jtext is not None
    m["at_door"], m["held"] = False, False
    if j.get("stage"):
        col, door = stage_from_text(j["stage"])
        m["column"], m["at_door"] = col or UNM, door
        m["stage_text"], m["stage_from"] = j["stage"], "journal"
    elif m["state"].startswith("locked"):
        m["column"], m["at_door"] = "2", True
        m["stage_text"] = "at the door of Stage 2: the version is locked, which is Stage 1's exit"
        m["stage_from"] = "version file (no journal yet)"
    elif m["state"].lower().startswith("not started"):
        m["column"], m["held"] = "intake", True
        m["stage_text"] = "held at intake: " + m["state"]
        m["stage_from"] = "version file (no journal yet)"
    else:
        m["column"], m["stage_text"], m["stage_from"] = UNM, UNM, "nothing on disk names it"
    if m["state"].lower().startswith("not started"):
        m["held"] = True
    m["waits_on"] = j.get("waits_on") or (m["state"] if m["held"] else UNM)
    m["next"] = j.get("next") or UNM
    m["questions"] = j.get("questions") or ""
    m["journal_version"] = j.get("version") or ""
    # last movement: the newest dated thing in the journal or the Designer record
    moves = [(t, "journal: " + h) for t, h in j.get("history", [])]
    for e in (s or {}).get("history") or []:
        t = parse_utc(e.get("at")) if isinstance(e, dict) else None
        if t:
            what = str(e.get("what") or "")
            moves.append((t, "Designer record: step %s %s" % (e.get("stage"), what.replace("_", " "))))
    if moves:
        t, what = max(moves, key=lambda x: x[0])
        m["last_move"], m["last_move_what"] = pac(t), what
    else:
        m["last_move"], m["last_move_what"] = UNM, ""
    m["disagree"] = disagreements(m, v, s, tt, j)
    m["files"] = [os.path.join("design", "concepts", folder, p) for p in
                  ("journal.md", "version/VERSION.json", "stage.json", "version/test_table.md")
                  if os.path.exists(os.path.join(c, p))]
    return m


def disagreements(m, v, s, tt, j):
    out = []
    if s is not None and v:
        vs, ss = str(v.get("state") or ""), str(s.get("status") or "")
        if vs.startswith("locked") and ss != "locked":
            out.append("VERSION.json says locked; stage.json still says %s at Designer step %s (%s)"
                       % (ss or UNM, s.get("stage"), m.get("designer_step_name", UNM)))
        if ss == "locked" and v.get("state") and not vs.startswith("locked"):
            out.append("stage.json says locked; VERSION.json says %s" % vs)
        vm, sm = str(v.get("mod") or ""), str(s.get("mod") or "").split("/")[-1]
        if vm and sm and vm != sm:
            out.append("VERSION.json names the mod %s; stage.json names it %s" % (vm, sm))
    if tt is not None and v:
        if known(tt.get("version")) and known(v.get("version")) and str(tt["version"]) != str(v["version"]):
            out.append("VERSION.json says version %s; the test table was made for %s" % (v["version"], tt["version"]))
        bars = tt.get("bars")
        if isinstance(bars, list) and isinstance(v.get("bars_total"), int) and len(bars) != v["bars_total"]:
            out.append("VERSION.json counts %d bars; the test table has %d" % (v["bars_total"], len(bars)))
    jv = re.match(r"(\d+\.\d+\.\d+)", j.get("version") or "")
    if jv and known(v.get("version")) and jv.group(1) != str(v["version"]):
        out.append("the journal says Design Version %s; VERSION.json says %s" % (jv.group(1), v["version"]))
    return out


# ---- held look statements ----------------------------------------------------------------------------------------

def held_statements(root, mods):
    """-> {"total": int|UNM, "counted_files": n, "uncounted": [file], "per_mod": {folder: int|UNM}}."""
    d = os.path.join(root, "design", "RimMandrake", "validation_holding")
    try:
        readme = open(os.path.join(d, "README.md"), encoding="utf-8").read()
        files = sorted(f for f in os.listdir(d) if f.startswith("owner_look_defects_") and f.endswith(".md"))
    except OSError:
        return {"total": UNM, "counted_files": 0, "uncounted": [], "per_mod": {k: UNM for k in mods}}
    counts = {}
    for m in re.finditer(r"^\|\s*`(owner_look_defects_[^`]+\.md)`\s*\|\s*(\d+)\s+statements?", readme, re.M):
        counts[m.group(1)] = int(m.group(2))
    uncounted = [f for f in files if f not in counts]
    present = {f: n for f, n in counts.items() if f in files}
    per = {}
    for k in mods:
        slug = k.lower()
        mine = [f for f in files if re.sub(r"[^a-z]", "", f[:-3].split("_", 4)[-1]) == slug]
        if mine and all(f in present for f in mine):
            per[k] = sum(present[f] for f in mine)
        else:
            per[k] = UNM
    total = sum(present.values()) if not uncounted else UNM
    return {"total": total, "counted": sum(present.values()), "counted_files": len(present), "uncounted": uncounted,
            "per_mod": per}


# ---- live reads (ledger, run records) ----------------------------------------------------------------------------

def live_facts(mods):
    """-> {"intake": int|UNM, "intake_why", "questions": [{item, q}], "runs": {folder: [run]}, "errors": [..]}."""
    out = {"intake": UNM, "intake_why": "", "questions": None, "runs": {}, "errors": []}
    sys.path.insert(0, HERE)
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
    try:
        import fleet_mods  # noqa: E402
        import owner_queue  # noqa: E402
        evs, world = fleet_mods.ledger()
        rel = fleet_mods.relentless_states(strict=True)
        n = owner_queue.needs_you(world.items, rel, evs=evs, turns=owner_queue.designer_turns())
        out["intake"] = len(n["awaiting_designer"])
        out["questions"] = n["lines"]
        out["items"] = world.items
    except Exception as e:      # noqa: BLE001  a ledger it cannot read leaves these fields UNMEASURED, named
        out["errors"].append("ledger: %s: %s" % (e.__class__.__name__, str(e)[:160]))
        out["items"] = {}
    try:
        import detached_helper as DH  # noqa: E402
        for rec in DH.all_records():
            st = DH.live_status(rec)
            if st not in ("running", "launching"):
                continue
            item = str(rec.get("item") or "")
            it = out["items"].get(item)
            title = str(getattr(it, "title", "") or "")
            for k in mods:
                if k.upper() in item.replace("_", "") or re.search(r"pilot (on|of) %s\b" % re.escape(spaced(k)), title):
                    out["runs"].setdefault(k, []).append({"item": item, "model": rec.get("model") or UNM,
                                                          "since": pac(dt.datetime.fromtimestamp(rec["at"], dt.timezone.utc))
                                                          if isinstance(rec.get("at"), (int, float)) else UNM})
    except Exception as e:      # noqa: BLE001
        out["errors"].append("run records: %s: %s" % (e.__class__.__name__, str(e)[:160]))
        out["runs"] = None
    out.pop("items", None)
    return out


def his_questions_for(folder, questions):
    if questions is None:
        return UNM
    up = folder.upper()
    pat = re.compile(r"^\W*%s\b" % re.escape(folder))
    return [x for x in questions if up in x["item"].replace("_", "") or pat.match(x["q"] or "")]


# ---- gather ------------------------------------------------------------------------------------------------------

def gather(root, live=True):
    names = designer_names()
    croot = os.path.join(root, "design", "concepts")
    try:
        folders = sorted(f for f in os.listdir(croot) if not f.startswith("_") and os.path.isdir(os.path.join(croot, f)))
    except OSError:
        folders = []
    versioned = [f for f in folders if os.path.exists(os.path.join(croot, f, "version", "VERSION.json"))]
    others = [f for f in folders if f not in versioned]
    mods = [read_mod(root, f, names) for f in versioned]
    held = held_statements(root, versioned)
    lf = live_facts(versioned) if live else {"intake": UNM, "questions": None, "runs": None,
                                             "errors": ["live reads off (--no-live)"]}
    for m in mods:
        m["held_statements"] = held["per_mod"].get(m["name"], UNM)
        if m["held_statements"] == UNM and m["table"] and isinstance(m["table"].get("held"), int):
            m["held_statements"] = m["table"]["held"]
        m["his"] = his_questions_for(m["name"], lf["questions"])
        runs = lf["runs"]
        m["runs"] = UNM if runs is None else runs.get(m["name"], [])
        if m["column"] == UNM:
            m["status"] = "unknown"
        elif m["held"]:
            m["status"] = "held"
        elif runs is not None and m["runs"]:
            m["status"] = "helper"
        else:
            m["status"] = "waiting"
    order = {c: i for i, c in enumerate(COLUMNS)}
    mods.sort(key=lambda m: (m["held"], -order.get(m["column"], -1), m["label"].lower()))
    other = []
    for f in others:
        has = sorted(os.listdir(os.path.join(croot, f)))
        other.append({"name": f, "files": has})
    return {"mods": mods, "others": other, "held": held,
            "intake": {"count": lf["intake"], "questions_total": UNM if lf["questions"] is None else len(lf["questions"])},
            "errors": lf["errors"]}


# ---- the picture -------------------------------------------------------------------------------------------------

W = 1040
LBL_X, COL_X0, COL_X1 = 14, 214, 1028
COLW = (COL_X1 - COL_X0) / len(COLUMNS)


def esc(s):
    return html.escape(str(s), quote=True)


def t_(x, y, s, size=11, fill=TEXT, weight=None, anchor=None, italic=False):
    a = ' font-weight="%s"' % weight if weight else ""
    a += ' text-anchor="%s"' % anchor if anchor else ""
    a += ' font-style="italic"' if italic else ""
    return '<text x="%.1f" y="%.1f" font-size="%s" fill="%s"%s>%s</text>' % (x, y, size, fill, a, esc(s))


def clip(s, n):
    s = str(s)
    return s if len(s) <= n else s[:n - 1].rstrip(" ,;:") + "…"


def chip_fill(status):
    f = STATUS[status][0]
    return "url(#mnHatch)" if f == "hatch" else f


def picture(d):
    mods = d["mods"]
    row_h, top = 60, 132
    h = top + 56 + row_h * len(mods) + 34
    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" role="img" aria-label="%s" '
         'style="max-width:%dpx;font-family:%s">' % (W, h, esc(aria(d)), W, FONT)]
    p.append('<defs><pattern id="mnHatch" patternUnits="userSpaceOnUse" width="7" height="7" '
             'patternTransform="rotate(45)"><rect width="7" height="7" fill="#2a2f38"/><rect width="2.5" height="7" '
             'fill="#7d8796"/></pattern></defs>')
    p.append('<rect width="%d" height="%d" rx="10" fill="%s"/>' % (W, h, BG))
    # floating above
    p.append('<rect x="12" y="10" width="%d" height="26" rx="6" fill="%s" stroke="%s"/>' % (W - 24, CARD, EDGE))
    p.append(t_(24, 27, "FLOATING ABOVE, THE WHOLE TIME", 10.5, DIM, 700))
    for x, a, b in ((236, "OPERATIONS", "system health"), (460, "DISPATCH", "games and builders"),
                    (700, "STEWARD", "the Conductor, always")):
        p.append(t_(x, 27, a, 11, TEXT, 700) + t_(x + 10 + len(a) * 7.8, 27, b, 10.5, DIM))
    # legend
    x = 14
    for k in ("helper", "waiting", "held"):
        p.append('<rect x="%d" y="46" width="12" height="12" rx="2" fill="%s"/>' % (x, chip_fill(k)))
        p.append(t_(x + 17, 56.5, STATUS[k][3], 10.5, DIM))
        x += 30 + len(STATUS[k][3]) * 5.6
    p.append('<rect x="%d" y="46" width="12" height="12" rx="2" fill="none" stroke="%s" stroke-dasharray="3 2"/>' % (x, TEXT))
    p.append(t_(x + 17, 56.5, "at the stage's door", 10.5, DIM))
    x += 30 + 20 * 5.6
    p.append('<rect x="%d" y="46" width="12" height="12" rx="2" fill="%s"/>' % (x, DONE))
    p.append(t_(x + 17, 56.5, "stage behind it", 10.5, DIM))
    x += 30 + 15 * 5.6
    p.append(t_(x, 56.5, "⚑ his questions   ⚠ files disagree", 10.5, ALERT, 600))
    # column heads with arrows
    for i, c in enumerate(COLUMNS):
        cx = COL_X0 + i * COLW
        p.append('<rect x="%.1f" y="70" width="%.1f" height="52" rx="6" fill="%s"/>' % (cx + 2, COLW - 4, CARD))
        p.append(t_(cx + COLW / 2, 90, COL_NUM[c], 15, TEXT, 800, "middle"))
        p.append(t_(cx + COLW / 2, 104, COL_NAME[c], 11, TEXT, 600, "middle"))
        p.append(t_(cx + COLW / 2, 116.5, clip(COL_LONG[c], 18), 10.5, FAINT, None, "middle"))
        if i:
            p.append('<path d="M%.1f 92 l4 4 l-4 4" stroke="%s" stroke-width="1.5" fill="none"/>' % (cx - 2, DIM))
    p.append(t_(LBL_X, 92, "MOD", 10.5, DIM, 700))
    p.append(t_(LBL_X, 106, "Design Version, state", 10.5, FAINT))
    # intake row
    y = top
    ic = d["intake"]["count"]
    p.append('<rect x="12" y="%d" width="%d" height="46" rx="6" fill="%s"/>' % (y, W - 24, CARD))
    p.append(t_(LBL_X + 4, y + 19, "Waiting to enter", 12, TEXT, 700))
    p.append(t_(LBL_X + 4, y + 35, "first-touch mods, no Designer pass", 10.5, DIM))
    p.append(t_(COL_X0 + COLW / 2, y + 30, ic, 20 if ic != UNM else 10.5, TEXT if ic != UNM else ALERT, 800, "middle"))
    p.append(t_(COL_X0 + COLW + 10, y + 19, "%s mods have a first-touch Designer item open and no Designer pass yet "
                "(owner_queue.py)." % ic, 11, TEXT))
    p.append(t_(COL_X0 + COLW + 10, y + 35, "Mod ideas sitting inside other tickets: UNMEASURED (nothing marks a ticket "
                "as a mod idea).", 10.5, DIM))
    # mod rows
    y = top + 56
    for m in mods:
        p.append(mod_row(m, y, row_h))
        y += row_h
    p.append(t_(LBL_X, h - 14, "Stage from each mod's journal (\"Stage now\"); with no journal, a locked version waits "
                "at Stage 2's door. Designer step is stage.json's own inner step inside Stage 1.", 10.5, FAINT))
    p.append("</svg>")
    return "".join(p)


def aria(d):
    return "; ".join("%s %s %s" % (m["label"], m["version"], where_word(m)) for m in d["mods"])


def where_word(m):
    c = m["column"]
    if c == UNM:
        return "stage UNMEASURED"
    base = "Intake" if c == "intake" else ("Passed" if c == "passed" else "Stage %s %s" % (c, COL_NAME[c]))
    return ("at the door of " + base) if m["at_door"] else ("held at " + base if m["held"] else base)


def mod_row(m, y, row_h):
    p = ['<line x1="12" y1="%d" x2="%d" y2="%d" stroke="#262b34"/>' % (y + row_h - 3, W - 12, y + row_h - 3)]
    flag = ""
    if m["disagree"]:
        flag += " ⚠"
    his = m["his"]
    if isinstance(his, list) and his:
        flag += " ⚑%d" % len(his)
    p.append(t_(LBL_X + 4, y + 20, m["label"], 14, TEXT, 700))
    if flag:
        p.append(t_(LBL_X + 10 + len(m["label"]) * 8.6, y + 20, flag.strip(), 12, ALERT, 700))
    st = m["state"]
    st = "locked" if st.startswith("locked") else ("not started" if st.lower().startswith("not started") else st)
    p.append(t_(LBL_X + 4, y + 36, "%s · %s" % (m["version"], clip(st, 22)), 11, DIM))
    cur = COLUMNS.index(m["column"]) if m["column"] in COLUMNS else None
    for i, c in enumerate(COLUMNS):
        cx = COL_X0 + i * COLW + 4
        w = COLW - 8
        if cur is None:
            p.append('<rect x="%.1f" y="%d" width="%.1f" height="22" rx="4" fill="url(#mnHatch)" opacity=".5"/>' % (cx, y + 8, w))
            continue
        before = i < cur
        if i == cur:
            fill = chip_fill(m["status"])
            ink = STATUS[m["status"]][1]
            dash = ' stroke="%s" stroke-width="1.5" stroke-dasharray="4 3"' % TEXT if m["at_door"] else ""
            p.append('<rect x="%.1f" y="%d" width="%.1f" height="22" rx="5" fill="%s"%s/>' % (cx, y + 8, w, fill, dash))
            word = "at the door" if m["at_door"] else STATUS[m["status"]][2]
            if m["at_door"] and m["status"] == "helper":
                word = "door, helper"
            p.append(t_(cx + w / 2, y + 23, word, 10.5, ink, 700, "middle"))
        elif before:
            p.append('<rect x="%.1f" y="%d" width="%.1f" height="22" rx="4" fill="%s"/>' % (cx, y + 8, w, DONE))
            p.append(t_(cx + w / 2, y + 23, "✓", 11, "#9fd8c0", 700, "middle"))
        else:
            p.append('<rect x="%.1f" y="%d" width="%.1f" height="22" rx="4" fill="none" stroke="%s"/>' % (cx, y + 8, w, EDGE))
    line = "waits on: " + (m["waits_on"] if m["waits_on"] != UNM else "UNMEASURED (no journal line)")
    p.append(t_(COL_X0 + 6, y + 46, clip(line, 128), 10.5, DIM if m["waits_on"] != UNM else ALERT))
    return "".join(p)


# ---- the cards ---------------------------------------------------------------------------------------------------

def chip(word, bg, fg=INK):
    return ('<span style="background:%s;color:%s;padding:1px 8px;border-radius:4px;font-weight:600;white-space:nowrap;'
            'font-size:12px">%s</span>' % (bg, fg, esc(word)))


def val(v):
    if v == UNM or v is None:
        return '<b style="color:%s">UNMEASURED</b>' % ALERT
    return esc(v)


def row(k, v_html):
    return ('<div style="display:flex;gap:10px;padding:3px 0;border-top:1px solid #262b34"><div style="flex:0 0 150px;'
            'color:%s;font-size:12px;padding-top:1px">%s</div><div style="flex:1">%s</div></div>' % (DIM, esc(k), v_html))


def strip_html(m):
    cells = []
    cur = COLUMNS.index(m["column"]) if m["column"] in COLUMNS else None
    for i, c in enumerate(COLUMNS):
        if cur is None:
            bg, fg, word = "#2a2f38", DIM, COL_NUM[c]
        elif i == cur:
            f = STATUS[m["status"]][0]
            bg = "repeating-linear-gradient(45deg,#2a2f38 0 4px,#7d8796 4px 6px)" if f == "hatch" else f
            fg, word = STATUS[m["status"]][1], COL_NUM[c]
        elif i < cur:
            bg, fg, word = DONE, "#9fd8c0", COL_NUM[c]
        else:
            bg, fg, word = "transparent", FAINT, COL_NUM[c]
        border = "1px dashed %s" % TEXT if (i == cur and m["at_door"]) else "1px solid %s" % (EDGE if bg == "transparent" else bg if not bg.startswith("repeat") else EDGE)
        cells.append('<span title="%s" style="flex:1;text-align:center;background:%s;color:%s;border:%s;border-radius:3px;'
                     'font-size:11px;font-weight:700;padding:1px 0">%s</span>' % (esc(COL_NAME[c]), bg, fg, border, esc(word)))
    return '<div style="display:flex;gap:3px;margin:6px 0 8px">%s</div>' % "".join(cells)


def card(m):
    fill, ink, word, _ = STATUS[m["status"]]
    head = ['<span style="font-size:18px;font-weight:800">%s</span>' % esc(m["label"]),
            chip(m["version"] if m["version"] != UNM else "version UNMEASURED", "#dfe3ea"),
            chip(where_word(m), "#4f97d6"),
            chip(word, fill if fill != "hatch" else "#5d6675", ink if fill != "hatch" else TEXT)]
    if m["disagree"]:
        head.append(chip("⚠ files disagree", ALERT))
    his = m["his"]
    if isinstance(his, list) and his:
        head.append(chip("⚑ needs you: %d" % len(his), ALERT))
    rows = []
    rows.append(row("Waits on", val(m["waits_on"])))
    if his == UNM:
        needs = val(UNM) + " (the ledger was not read)"
    elif his:
        needs = "<br>".join("<b>%s</b>: %s" % (esc(x["item"]), esc(clip(x["q"], 220))) for x in his)
    else:
        needs = "nothing on his list names this mod"
    if m["questions"]:
        needs += '<br><span style="color:%s">journal:</span> %s' % (DIM, esc(clip(m["questions"], 220)))
    rows.append(row("Needs you", needs))
    rows.append(row("Next", val(m["next"])))
    stage = "%s <span style='color:%s'>(from the %s)</span>" % (esc(m["stage_text"]) if m["stage_text"] != UNM else val(UNM),
                                                             DIM, esc(m["stage_from"]))
    rows.append(row("Stage", stage))
    st = m["state"]
    rows.append(row("Design Version", "%s, %s%s" % (val(m["version"]), val(st),
                                                    ("<br><span style='color:%s'>scope: %s</span>" % (DIM, esc(m["scope"])))
                                                    if m["scope"] else "")))
    if m["designer_step"] == UNM:
        dsg = val(UNM)
    else:
        dsg = "step %s %s, status %s" % (m["designer_step"], esc(m["designer_step_name"]), val(m["designer_status"]))
        if m["designer_why"]:
            dsg += "<br><span style='color:%s'>%s</span>" % (DIM, esc(clip(m["designer_why"], 200)))
    rows.append(row("Designer record", dsg))
    bars = "%s bars; %s met by the last judge; %s judge rounds" % (val(m["bars_total"]), val(m["bars_met"]),
                                                                   val(m["judge_rounds"]))
    t = m["table"]
    if t:
        if "bars" in t:
            pa = ", ".join("Stage %s: %d" % (k, n) for k, n in sorted(t["proves_at"].items()))
            bars += ("<br>test table (%s): %s bars; %s with a test runnable today; %s with every deciding test runnable; "
                     "%s green offline today<br>prove at: %s" % (esc(t["version"]), t["bars"],
                                                                 val(t["any_test_runnable_today"]),
                                                                 val(t["every_decider_runnable_today"]),
                                                                 val(t["offline_green_today"]), esc(pa) or val(UNM)))
        else:
            bars += "<br>test table: its bars list could not be read: " + val(UNM)
    else:
        bars += "<br>test table: none yet (<code>version/test_table.json</code>)"
    rows.append(row("Bars", bars))
    tok = val(tokens_word(m["tokens"]) if m["tokens"] != UNM else UNM)
    if m["tokens"] != UNM and isinstance(m["estimates"], int) and m["estimates"]:
        tok += " charged, %s of it estimates" % esc(tokens_word(m["estimates"]))
    elif m["tokens"] != UNM:
        tok += " charged"
    rows.append(row("Tokens so far", tok + " <span style='color:%s'>(Designer record; pipeline stages not yet costed)</span>" % DIM))
    rows.append(row("Held look statements", val(m["held_statements"])))
    if m["runs"] == UNM:
        runs = val(UNM)
    elif m["runs"]:
        runs = "<br>".join("%s run on <b>%s</b>, since %s" % (esc(r["model"]), esc(r["item"]), esc(r["since"]))
                           for r in m["runs"])
    else:
        runs = "no helper run is going"
    rows.append(row("Helper now", runs))
    lm = val(m["last_move"]) if m["last_move"] == UNM else "%s <span style='color:%s'>%s</span>" % (
        esc(m["last_move"]), DIM, esc(clip(m["last_move_what"], 160)))
    rows.append(row("Last movement", lm))
    if m["disagree"]:
        rows.append(row("Files disagree", "<br>".join('<span style="color:%s">⚠ %s</span>' % (ALERT, esc(x))
                                                      for x in m["disagree"])))
    if m["unread"]:
        rows.append(row("Could not read", "<br>".join(esc(x) for x in m["unread"])))
    if m["files"]:
        rows.append(row("Files", '<span style="font-size:11px;color:%s">%s</span>' % (
            DIM, "<br>".join(esc(NATIVE_REPO + "\\" + f.replace("/", "\\")) for f in m["files"]))))
    return ('<div data-mod="%s" style="background:%s;color:%s;border:1px solid %s;border-left:5px solid %s;'
            'border-radius:10px;padding:10px 16px;margin:0 0 12px;max-width:1040px;box-sizing:border-box;font-family:%s;'
            'font-size:13px;line-height:1.45"><div style="display:flex;flex-wrap:wrap;align-items:center;gap:8px">%s</div>'
            '%s%s</div>' % (esc(m["label"]), BG, TEXT, EDGE, fill if fill != "hatch" else "#7d8796", FONT,
                            " ".join(head), strip_html(m), "".join(rows)))


# ---- the page ----------------------------------------------------------------------------------------------------

def top_chips(d):
    mods = d["mods"]
    out = []
    adv = [m for m in mods if not m["held"]]
    out.append(chip("%d mods in the pipeline" % len(adv), "#4f97d6"))
    nh = sum(1 for m in mods if m["status"] == "helper")
    out.append(chip("%d with a helper on them" % nh, STATUS["helper"][0]) if all(m["runs"] != UNM for m in mods)
               else chip("helpers UNMEASURED", "#6b7380", TEXT))
    held = [m for m in mods if m["held"]]
    if held:
        out.append(chip("%d held" % len(held), "#5d6675", TEXT))
    ic = d["intake"]["count"]
    out.append(chip("%s waiting at intake" % ic, "#3a4250", TEXT))
    his = [x for m in mods if isinstance(m["his"], list) for x in m["his"]]
    if any(m["his"] == UNM for m in mods):
        out.append(chip("needs you: UNMEASURED", "#6b7380", TEXT))
    else:
        out.append(chip("%d of his questions name these mods" % len(his), ALERT if his else "#256b4c",
                        INK if his else "#fff"))
    nd = sum(1 for m in mods if m["disagree"])
    if nd:
        out.append(chip("⚠ files disagree on %d" % nd, ALERT))
    return " ".join(out)


def md_cell(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def summary_rows(d):
    rows = []
    for m in d["mods"]:
        his = m["his"]
        needs = UNM if his == UNM else (", ".join(x["item"] for x in his) if his else "nothing")
        rows.append((m["label"], "%s, %s" % (m["version"], "locked" if m["state"].startswith("locked") else clip(m["state"], 30)),
                     where_word(m), clip(m["waits_on"], 110), needs, m["last_move"]))
    return rows


HEADS = ("mod", "Design Version", "stands at", "waits on", "needs you", "last movement")


def unread_lines(d):
    out = ["Any mod's position inside Stages 2 to 8 beyond what its journal's \"Stage now\" line says: those stages are not "
           "built and keep no record of their own yet (spec §6, \"the mod record\").",
           "Cycles at Stages 4 and 5, cost per pipeline stage and his minutes: nothing records them yet.",
           "Mod ideas sitting inside other tickets: no marker says a ticket is a mod idea."]
    h = d["held"]
    if h["total"] == UNM:
        out.append("Held look statements in total: the holding README counts %d in %d files; %s %s not counted there."
                   % (h.get("counted", 0), h["counted_files"], ", ".join("`%s`" % f for f in h["uncounted"]) or "its folder",
                      "is" if len(h["uncounted"]) == 1 else "are"))
    for m in d["mods"]:
        miss = [k for k in ("waits_on", "next", "bars_met", "judge_rounds", "tokens", "last_move", "held_statements")
                if m.get(k) == UNM]
        if miss:
            out.append("%s: %s." % (m["label"], ", ".join(k.replace("_", " ") for k in miss)))
    for e in d["errors"]:
        out.append(e)
    return out


def build(d, now):
    measured = "**Measured from disk %s.** Made by `maturation_now.py`, no model, no tokens." % pac(now)
    parts_md, parts_html = [], []
    title = "Maturation now"
    lead = ("Where every mod stands in the Maturation Pipeline and what each one waits on. "
            "The map is the spec's (`%s\\design\\specs\\2026-11-13-maturation-pipeline.md`)." % NATIVE_REPO)
    parts_md += ["# " + title, "", measured, "", top_chips(d), "", lead, "", "<div>" + picture(d) + "</div>", ""]
    # summary table
    parts_md += ["## Every mod, one line", "", "| " + " | ".join(HEADS) + " |", "|" + "---|" * len(HEADS)]
    parts_md += ["| " + " | ".join(md_cell(c) for c in r) + " |" for r in summary_rows(d)]
    parts_md += ["", "## Each mod", ""]
    for m in d["mods"]:
        parts_md += [card(m), ""]
    if d["others"]:
        parts_md += ["## Concept folders with no Design Version", ""]
        for o in d["others"]:
            parts_md.append("- `%s` (%s): no `version/VERSION.json`, so not placed on the map." % (
                o["name"], ", ".join(o["files"][:6]) + (", …" if len(o["files"]) > 6 else "")))
        parts_md.append("")
    parts_md += ["## What this page cannot say", ""] + ["- " + x for x in unread_lines(d)] + [""]
    parts_md += ["---", "", "Regenerate: `python3 src/RimMandrake/Utils/maturation_now.py` (in a RimMandrake clone). "
                 "Selftest: `python3 src/RimMandrake/Utils/selftest_maturation_now.py`. Same view as a web page: "
                 "`%s\\MATURATION_NOW.html`." % NATIVE_OUT, ""]
    md = "\n".join(parts_md)
    # the html twin: the same pieces, the markdown bits rendered by hand
    tbl = ('<table><tr>%s</tr>%s</table>' % ("".join("<th>%s</th>" % esc(h) for h in HEADS), "".join(
        "<tr>%s</tr>" % "".join("<td>%s</td>" % (val(c) if c == UNM else esc(c)) for c in r) for r in summary_rows(d))))
    others = "".join("<li><code>%s</code>: no <code>version/VERSION.json</code>, so not placed on the map.</li>"
                     % esc(o["name"]) for o in d["others"])
    cant = "".join("<li>%s</li>" % inline_md(x) for x in unread_lines(d))
    parts_html = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Maturation now</title>'
                  '<meta name="viewport" content="width=device-width,initial-scale=1"><style>'
                  'body{background:#0e1014;color:%s;font:14px/1.5 %s;margin:0;padding:18px 22px}'
                  '.wrap{max-width:1040px;margin:0 auto}h1{font-size:26px;margin:4px 0 6px}'
                  'h2{font-size:17px;margin:22px 0 8px;color:%s}code{font-family:Consolas,monospace;font-size:12px}'
                  'table{border-collapse:collapse;width:100%%;font-size:13px;background:%s;border-radius:8px}'
                  'th{color:%s;text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.06em;'
                  'padding:6px 10px;border-bottom:1px solid %s}td{padding:6px 10px;border-bottom:1px solid #262b34;'
                  'vertical-align:top}li{margin:3px 0}.m{color:%s}</style></head><body><div class="wrap">'
                  % (TEXT, FONT, TEXT, CARD, DIM, EDGE, DIM),
                  "<h1>%s</h1>" % title, "<p>%s</p>" % inline_md(measured), "<p>%s</p>" % top_chips(d),
                  "<p class='m'>%s</p>" % inline_md(lead), picture(d),
                  "<h2>Every mod, one line</h2>", tbl, "<h2>Each mod</h2>"] + [card(m) for m in d["mods"]]
    if others:
        parts_html += ["<h2>Concept folders with no Design Version</h2><ul>%s</ul>" % others]
    parts_html += ["<h2>What this page cannot say</h2><ul>%s</ul>" % cant,
                   "<p class='m'>Regenerate: <code>python3 src/RimMandrake/Utils/maturation_now.py</code>. "
                   "Markdown twin: <code>%s\\MATURATION_NOW.md</code>.</p></div></body></html>" % esc(NATIVE_OUT)]
    return md, "\n".join(parts_html)


def inline_md(s):
    s = esc(s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s.replace("\\\\", "\\")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=REPO)
    ap.add_argument("--out", default=OUT_DIR)
    ap.add_argument("--print", action="store_true", dest="print_")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-live", action="store_true")
    a = ap.parse_args(argv)
    d = gather(os.path.abspath(a.root), live=not a.no_live)
    if a.json:
        print(json.dumps(d, indent=1, default=str))
        return 0
    md, page = build(d, dt.datetime.now(dt.timezone.utc))
    if a.print_:
        sys.stdout.write(md)
        return 0
    os.makedirs(a.out, exist_ok=True)
    for name, text in (("MATURATION_NOW.md", md), ("MATURATION_NOW.html", page)):
        p = os.path.join(a.out, name)
        with open(p + ".tmp", "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        os.replace(p + ".tmp", p)
    print("wrote %s\\MATURATION_NOW.md and .html (%d mods)" % (NATIVE_OUT if a.out == OUT_DIR else a.out, len(d["mods"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
