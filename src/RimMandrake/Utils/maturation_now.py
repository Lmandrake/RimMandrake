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

Round 2 (the owner, 2026-11-14 ~12:25 PM PST: "Put some yellow arrows where Conductor has intervened along the process so
far. Make sure I can see what's operationally going on, and especially focus on any cycling or multiple restaging ...
I'm moving to the phone now, so communicate with me in phone-friendly ways."):
  - a box per stage on each mod's card: the live run on it (unit, since when), every run of that stage from the
    detached-run records (outcome, wall time, tokens, dollars where the out file still holds them), CYCLED xN when a
    stage ran more than once, the Designer's inner loop counts from stage.json, the last result in a few words;
  - a yellow arrow on every stage where the Conductor stepped in: "CONDUCTOR INTERVENED (stage N, <time>, kind K): ..."
    lines in the journal or in a ledger note (the form is the spec's §5), plus one derived relaunch per extra run;
  - "Needs Mandrake" and "Needs Conductor" at the top: open journal questions, his queue's questions, held stages,
    a current stage run 3+ times, a run live over an hour, a run that ended badly, a run over its cap, an unreadable
    intervention line, files that disagree;
  - phone images (PIL, local, no network): MATURATION_NOW_phone/00_overview.png and <Mod>.png, 1080 px wide portrait.
    --no-phone skips them. MATURATION_NOW_CLOCK (a unix time) pins the clock, for the selftest's two-run check.

Rules. Anything it cannot read prints UNMEASURED, never a guess or a zero. Two runs on an unchanged tree differ only in
the "**Measured" line: no "minutes ago", only Pacific clock times. Typora: every HTML block is ONE line with no blank line
in it (a blank line ends the block and spills the rest as text), no <details>, and the picture paints its own dark card
so it reads the same in a light or dark theme. Colour is never alone: every chip carries its word. Stdlib only for
the pages (PIL for the phone images), no network, no model. Selftest: selftest_maturation_now.py (the item's seven acceptance points).
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
# the stage record's words (maturation.STAGES) -> columns; kept here so this reader never imports maturation
RECORD_COL = {"intake": "intake", "designer": "1", "preflight": "2", "offline_build": "3", "blind_challenge": "4+5",
              "in_game": "6", "pre_human": "7", "his_walk": "8", "passed": "passed"}
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
    if not m:      # "Stage 1 finished ...; Stage 2 by a throwaway program" stands at the highest stage it names
        m = max(re.finditer(r"\bstages?\s*(\d)", low), key=lambda x: int(x.group(1)), default=None)
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
    m["versionless"] = not os.path.exists(os.path.join(c, "version", "VERSION.json"))
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
    rec, _ = read_json(os.path.join(c, "version", "stage_record.json"))
    rcol = RECORD_COL.get(str((rec or {}).get("stage"))) if isinstance(rec, dict) else None
    if rcol:
        # RIMMANDRAKE_WRITE_STAGE_MOVES_ATOMICALLY: the stage record is the stage; the journal line is its echo
        m["column"], m["at_door"] = rcol, bool(rec.get("at_door"))
        m["stage_text"] = j.get("stage") or "%s (the stage record)" % rec.get("stage")
        m["stage_from"] = "stage record (version/stage_record.json)"
    elif j.get("stage"):
        col, door = stage_from_text(j["stage"])
        m["column"], m["at_door"] = col or UNM, door
        m["stage_text"], m["stage_from"] = j["stage"], "journal"
    elif m["versionless"]:
        # no Design Version named: it stands at its Designer step, from stage.json
        m["column"], m["at_door"] = "1", False
        m["stage_text"] = "Designer step %s %s, status %s" % (m["designer_step"], m.get("designer_step_name", UNM), m["designer_status"])
        m["stage_from"] = "Designer record (stage.json); no Design Version named yet"
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
    m["owner_lock"] = bool(m["versionless"] and str(m["designer_status"]).lower().startswith("locked"))
    m["waits_on"] = j.get("waits_on") or (m["state"] if m["held"] else UNM)
    if m["versionless"]:
        m["waits_on"] = ("the owner's lock: the Designer tree is locked, no Design Version is named yet" if m["owner_lock"]
                         else (m["designer_why"] or "the Designer; no Design Version named yet"))
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
    m["ivs"], m["iv_bad"] = parse_interventions(jtext, "journal")
    m["jquestions"] = journal_questions(jtext)
    m["dcycles"] = designer_cycles(s) if s is not None else UNM
    m["_journal"] = j
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
    """-> {"intake": int|UNM, "intake_why", "questions": [{item, q}], "records": [rec]|None, "notes": [ev]|None,
    "errors": [..]}. A record carries "live_state", its unit's state as detached_helper.live_status reads it."""
    out = {"intake": UNM, "intake_why": "", "questions": None, "records": None, "notes": None, "errors": []}
    sys.path.insert(0, HERE)
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
    try:
        import fleet_mods  # noqa: E402
        import owner_queue  # noqa: E402
        evs, world = fleet_mods.ledger()
        out["notes"] = [e for e in evs if isinstance(e, dict) and e.get("event") == "note"]
        rel = fleet_mods.relentless_states(strict=True)
        n = owner_queue.needs_you(world.items, rel, evs=evs, turns=owner_queue.designer_turns())
        out["intake"] = len(n["awaiting_designer"])
        out["questions"] = n["lines"]
    except Exception as e:      # noqa: BLE001  a ledger it cannot read leaves these fields UNMEASURED, named
        out["errors"].append("ledger: %s: %s" % (e.__class__.__name__, str(e)))
    try:
        import detached_helper as DH  # noqa: E402
        recs = []
        for rec in DH.all_records():
            rec = dict(rec)
            rec["live_state"] = DH.live_status(rec) if rec.get("status") in ("running", "launching") else rec.get("status")
            recs.append(rec)
        out["records"] = recs
    except Exception as e:      # noqa: BLE001
        out["errors"].append("run records: %s: %s" % (e.__class__.__name__, str(e)))
    return out


# ---- runs, interventions and what needs a reaction ---------------------------------------------------------------
#
# A run (a detached-run record, detached_helper.py) is a mod's when its item id names the mod: the folder name squashed,
# its initials when 3+ letters (GSS), or one of its CamelCase words of 7+ letters (KNOCKBACK); a longer token wins, a
# tie names no mod. An item that names no mod is the mod's whose "design/concepts/<Folder>/" its ledger notes cite most.
# A run's stages: the journal's dated "### " headings inside its time window that name a stage ("row 2 done: Stage 1
# finished"); else its own ledger notes (role_unit); a run older than the journal is Stage 1 when its item is a DESIGN
# item, else "before the pipeline". A live run that has written no stage yet sits in the mod's current box, uncounted.
# An intervention is a line "CONDUCTOR INTERVENED (stage N, <date time PST>, kind K): what" in the journal or in a ledger
# note on the mod's items (spec §5); a stage run more than once adds one derived "relaunch" per extra run.

YELLOW = "#ffd23f"
IV_KINDS = ("decision", "re-pin", "hold", "release", "relaunch", "brief", "bar-added")
IV_RX = re.compile(r"CONDUCTOR INTERVENED\s*\(\s*stage\s+(intake|4\s*\+\s*5|[1-8])\s*"
                   r"(?:,\s*(\d{4}-\d{2}-\d{2})\s+(\d{1,2}):(\d{2})\s*(AM|PM)?\s*(?:PST|PDT)?)?\s*"
                   r"(?:,\s*kind\s+([a-z-]+))?\s*\)\s*:\s*(\S.*)$", re.I)
LONG_RUN_S = 3600
CYCLE_ALARM = 3


def col_of_stage(s):
    s = str(s).replace(" ", "").lower()
    return "4+5" if s in ("4", "5", "4+5") else s


def pac_time(t, now=None):
    """'12:15 PM PST' for an aware datetime or a unix time; 'Fri 9:54 AM PST' when not on now's Pacific day."""
    if isinstance(t, (int, float)):
        t = dt.datetime.fromtimestamp(t, dt.timezone.utc)
    t = t.astimezone(PAC)
    day = ""
    if now is not None and dt.datetime.fromtimestamp(now, PAC).date() != t.date():
        day = t.strftime("%a ")
    return "%s%s %s" % (day, t.strftime("%I:%M %p").lstrip("0"), t.strftime("%Z"))


def minutes(s):
    if not isinstance(s, (int, float)):
        return UNM
    s = int(s)
    return "%d min" % round(s / 60) if s < 5400 else "%.1f h" % (s / 3600)


def parse_interventions(text, source):
    """-> (interventions, unparsed lines). Each: {stage, at (unix|None), when, kind, what, source}."""
    good, bad = [], []
    for ln in (text or "").splitlines():
        if "CONDUCTOR INTERVENED" not in ln.upper():
            continue
        body = re.sub(r"^\W*", "", ln.strip())
        m = IV_RX.search(body)
        kind = (m.group(6) or "decision").lower() if m else None
        if not m or kind not in IV_KINDS:
            bad.append({"source": source, "line": clip(ln.strip(), 200)})
            continue
        at = None
        if m.group(2):
            h, mi = int(m.group(3)), int(m.group(4))
            if (m.group(5) or "").upper() == "PM" and h < 12:
                h += 12
            if (m.group(5) or "").upper() == "AM" and h == 12:
                h = 0
            try:
                at = dt.datetime.strptime(m.group(2), "%Y-%m-%d").replace(hour=h, minute=mi, tzinfo=PAC).timestamp()
            except ValueError:
                at = None
        good.append({"stage": col_of_stage(m.group(1)), "at": at, "when": pac_time(at) if at else UNM, "kind": kind,
                     "what": strip_md(m.group(7)), "source": source})
    return good, bad


def mod_tokens(folder):
    """-> {token: score}: the squashed name scores highest, then initials (3+ letters) and 7+ letter words by length."""
    words = re.findall(r"[A-Z][a-z0-9]*|[a-z0-9]+", folder)
    out = {folder.upper().replace("_", ""): 100 + len(folder)}
    ini = "".join(w[0] for w in words).upper()
    if len(ini) >= 3:
        out.setdefault(ini, len(ini))
    for w in words:
        if len(w) >= 7:
            out.setdefault(w.upper(), len(w))
    return out


def item_mod(item, folders, notes=None):
    """The mod an item id names, else the one its ledger notes cite most by concept path, else None."""
    words = [w for w in str(item).upper().split("_") if w]
    cands = {"".join(words[i:i + n]) for i in range(len(words)) for n in (1, 2, 3) if i + n <= len(words)}
    score = {}
    for f in folders:
        s = max([v for k, v in mod_tokens(f).items() if k in cands] or [0])
        if s:
            score[f] = s
    if score:
        top = max(score.values())
        win = [f for f, s in score.items() if s == top]
        return win[0] if len(win) == 1 else None
    cites = {}
    for e in notes or []:
        if e.get("id") != item:
            continue
        for f in folders:
            n = str(e.get("text") or "").count("design/concepts/%s/" % f)
            if n:
                cites[f] = cites.get(f, 0) + n
    if cites:
        top = max(cites.values())
        win = [f for f, n in cites.items() if n == top]
        return win[0] if len(win) == 1 else None
    return None


def stages_named(s):
    """The stage columns a heading or note names ("Stage 1 finished", "Stages 4 and 5"); never one it is "before"."""
    s = re.sub(r"(?i)\b(before|until|ahead of|door of|stopped before)\s+stages?\s*\d", "", str(s))
    out = []
    for m in re.finditer(r"(?i)\bstages?\s+(\d)(?:\s*(?:and|to|-|\+)\s*(\d))?", s):
        for g in m.groups():
            if g and 1 <= int(g) <= 8:
                c = col_of_stage(g)
                if c not in out:
                    out.append(c)
    return out


def read_spend(rec):
    """-> (usd measured|UNM, the run's own dollar word|None, over its cap: True|False|UNM). Reads the run's out file:
    claude's total_cost_usd when the file still holds it, a max-budget stop, and the run's own "spent about $N"."""
    try:
        with open(rec.get("out") or "", encoding="utf-8", errors="replace") as f:
            t = f.read()
    except OSError:
        t = ""
    m = re.search(r'"total_cost_usd"\s*:\s*([0-9.]+)', t)
    usd = float(m.group(1)) if m else UNM
    w = [x for x in (re.search(r"(?i)(?:spent|spend|cost)\s+(?:was\s+|about\s+|roughly\s+|~)*\$\s?(\d+(?:\.\d+)?)", t),
                     re.search(r"(?i)\$\s?(\d+(?:\.\d+)?)\s+(?:of model spend|of spend|spent|in spend)", t)) if x]
    said = float(min(w, key=lambda x: x.start()).group(1)) if w else None
    cap = rec.get("budget_usd")
    if re.search(r"error_max_budget|max_budget_usd exceeded|exceeded.{0,20}budget", t, re.I):
        over = True
    elif isinstance(cap, (int, float)) and (usd != UNM or said is not None):
        over = (usd if usd != UNM else said) > cap
    else:
        over = UNM
    return usd, said, over


def run_view(rec, now, spend=read_spend):
    at, end = rec.get("at"), rec.get("ended")
    st = rec.get("live_state") or rec.get("status")
    live = st in ("running", "launching")
    res = str(rec.get("result") or "")
    if live:
        outcome, ok = "running now", None
    elif st == "dead":
        outcome, ok = "its unit died and its finish never ran", False
    elif res.startswith("success"):
        outcome, ok = "finished OK", True
    elif res.startswith("timeout"):
        outcome, ok = "killed at its time limit", False
    elif "claude-error" in res:
        outcome, ok = "ended in a model error", False
    elif res.startswith("unknown"):
        outcome, ok = "ended with no exit status", False
    elif res:
        outcome, ok = "ended: " + res, False
    else:
        outcome, ok = UNM, None
    num_at = isinstance(at, (int, float))
    wall = (end - at) if (num_at and isinstance(end, (int, float))) else ((now - at) if (live and num_at) else UNM)
    usd, said, over = spend(rec) if not live else (UNM, None, UNM)
    tok = rec.get("tokens")
    return {"unit": str(rec.get("unit") or UNM), "item": str(rec.get("item") or UNM), "model": rec.get("model") or UNM,
            "at": at if num_at else None, "end": end if isinstance(end, (int, float)) else None,
            "start": pac_time(at, now) if num_at else UNM, "stop": pac_time(end, now) if isinstance(end, (int, float)) else "",
            "live": live, "state": st or UNM, "outcome": outcome, "ok": ok, "wall_s": wall, "wall": minutes(wall),
            "tokens": tok if isinstance(tok, int) else UNM, "usd": usd, "said_usd": said,
            "cap": rec.get("budget_usd") if isinstance(rec.get("budget_usd"), (int, float)) else UNM, "over_cap": over,
            "stages": [], "placed": ""}


def runs_for_mods(folders, records, notes, journals, now, spend=read_spend):
    """-> {folder: [run]} with each run's stages placed (see the block comment above)."""
    out = {f: [] for f in folders}
    notes = notes or []
    by_unit = {}
    for e in notes:
        if e.get("role_unit"):
            by_unit.setdefault(str(e["role_unit"]), []).append(e)
    cache = {}
    for rec in records or []:
        item = str(rec.get("item") or "")
        if item not in cache:
            cache[item] = item_mod(item, folders, notes)
        f = cache[item]
        if not f:
            continue
        r = run_view(rec, now, spend)
        hist = journals.get(f, {}).get("history") or []
        start = min((t.timestamp() for t, _ in hist), default=None)
        if r["at"] is not None and start is not None and r["at"] < start - 900:
            if "DESIGN" in item.upper().split("_"):
                r["stages"], r["placed"] = ["1"], "a Designer run before the journal"
            else:
                r["placed"] = "before the pipeline"
        elif r["at"] is not None:
            hi = (r["end"] if r["end"] is not None else float("inf")) + 120
            for t, h in hist:
                if r["at"] - 120 <= t.timestamp() <= hi:
                    for c in stages_named(h):
                        if c not in r["stages"]:
                            r["stages"].append(c)
            if r["stages"]:
                r["placed"] = "journal headings in its time"
            else:
                for e in by_unit.get(r["unit"], []):
                    for c in stages_named(e.get("text")):
                        if c not in r["stages"]:
                            r["stages"].append(c)
                r["placed"] = "its ledger notes" if r["stages"] else "no stage written yet"
        else:
            r["placed"] = "no start time"
        r["notes"] = [str(e.get("text") or "") for e in by_unit.get(r["unit"], [])]
        out[f].append(r)
    for f in out:
        out[f].sort(key=lambda r: r["at"] or 0)
    return out


def last_words(run, notes):
    """The run's last result in a few words: its "ended ... Result:" note, else its newest own note."""
    for e in reversed(notes or []):
        t = str(e.get("text") or "")
        if t.startswith("DETACHED run %s ended" % run["unit"]):
            m = re.search(r"Result:\s*(.+)", t)
            return clip(strip_md(re.sub(r"\s*\[\+\d+ chars.*$", "", (m.group(1) if m else t).split("\n")[0])), 150)
    if run.get("notes"):
        return clip(strip_md(run["notes"][-1].split("\n")[0]), 150)
    return UNM


def designer_cycles(s):
    """stage.json's history -> {"opens": {step: n}, "retry": n, "over_budget": n, "invalidated": n} or UNM."""
    h = (s or {}).get("history") if isinstance(s, dict) else None
    if not isinstance(h, list):
        return UNM
    out = {"opens": {}, "retry": 0, "over_budget": 0, "invalidated": 0}
    for e in h:
        if not isinstance(e, dict):
            continue
        w = e.get("what")
        if w == "open" and isinstance(e.get("stage"), int):
            out["opens"][e["stage"]] = out["opens"].get(e["stage"], 0) + 1
        elif w in ("retry", "over_budget", "invalidated"):
            out[w] += 1
    return out


def journal_questions(text):
    """The numbered items under any "### Questions" heading -> [{n, who, text, answered}]. "for the Conductor" in an
    item routes it to the Conductor; "answers question N" anywhere in the journal marks N answered."""
    if not text:
        return []
    answered = {int(x) for x in re.findall(r"(?i)answer(?:s|ed|ing)?\s+questions?\s+(\d+)", text)}
    out = []
    for sec in re.finditer(r"^###\s+Questions[^\n]*\n(.*?)(?=^#{2,3}\s|\Z)", text, re.M | re.S):
        for q in re.finditer(r"^(\d+)\.\s+(.+?)(?=^\d+\.\s|\Z)", sec.group(1), re.M | re.S):
            body = " ".join(q.group(2).split())
            b = re.match(r"\*\*(.+?)\*\*", body)
            title = strip_md(b.group(1)).rstrip(":") if b else clip(strip_md(body), 110)
            out.append({"n": int(q.group(1)), "who": "conductor" if re.search(r"(?i)for the Conductor", body) else "mandrake",
                        "text": clip(title, 140), "answered": int(q.group(1)) in answered})
    return out


def stage_boxes(m, runs, ivs, cur):
    """-> {col: {"runs": [...], "ivs": [...], "cycled": n, "held": iv|None, "unplaced_live": [...]}} for every column
    with something in it, plus the current one."""
    order = {c: i for i, c in enumerate(COLUMNS)}
    box = {}

    def b(c):
        return box.setdefault(c, {"runs": [], "ivs": [], "cycled": 0, "held": None, "unplaced_live": []})
    for r in runs if isinstance(runs, list) else []:
        for c in r["stages"]:
            b(c)["runs"].append(r)
        if not r["stages"] and r["live"] and cur in COLUMNS:
            b(cur)["unplaced_live"].append(r)
    for iv in ivs:
        b(iv["stage"])["ivs"].append(iv)
    for c, x in box.items():
        x["cycled"] = len(x["runs"])
        for k, r in enumerate(x["runs"][1:], 2):
            x["ivs"].append({"stage": c, "at": r["at"], "when": r["start"], "kind": "relaunch", "derived": True,
                             "what": "ran this stage again: run %d of %d (from the run records)" % (k, len(x["runs"])),
                             "source": r["unit"]})
        holds = [i for i in x["ivs"] if i["kind"] in ("hold", "release")]
        holds.sort(key=lambda i: i["at"] or 0)
        x["held"] = holds[-1] if holds and holds[-1]["kind"] == "hold" else None
        x["ivs"].sort(key=lambda i: i["at"] or 0)
    if cur in COLUMNS:
        b(cur)
    return dict(sorted(box.items(), key=lambda kv: order.get(kv[0], 99)))


def reactions(mods, now):
    """-> {"mandrake": [line], "conductor": [line]}: only things on disk, each with the mod and the stage."""
    me, co = [], []
    order = {c: i for i, c in enumerate(COLUMNS)}
    for m in mods:
        L = m["label"]
        for q in m.get("jquestions") or []:
            if q["answered"]:
                continue
            line = "%s: question %d, %s" % (L, q["n"], q["text"])
            (co if q["who"] == "conductor" else me).append(line)
        if isinstance(m.get("his"), list):
            for x in m["his"]:
                me.append("%s: %s on his list: %s" % (L, x["item"], clip(x["q"], 140)))
        cur = order.get(m["column"], -1)
        for c, x in (m.get("boxes") or {}).items():
            sname = "Stage %s" % c if c not in ("intake", "passed") else c
            if x["held"]:
                co.append("%s: %s is HELD (since %s): %s" % (L, sname, x["held"]["when"], clip(x["held"]["what"], 160)))
            if x["cycled"] >= CYCLE_ALARM and order.get(c, -1) >= cur:
                co.append("%s: %s has run %d times" % (L, sname, x["cycled"]))
        for r in m["runs"] if isinstance(m["runs"], list) else []:
            if r["placed"] == "before the pipeline":
                continue
            st = ", ".join("Stage %s" % c for c in r["stages"]) or "stage not yet written"
            if r["live"] and isinstance(r["wall_s"], (int, float)) and r["wall_s"] > LONG_RUN_S:
                co.append("%s: a run has been live %s (%s, since %s)" % (L, r["wall"], st, r["start"]))
            if r["ok"] is False:
                co.append("%s: the run of %s ended %s (%s)" % (L, r["start"], r["outcome"], st))
            if r["over_cap"] is True:
                co.append("%s: the run of %s went over its $%s cap" % (L, r["start"], r["cap"]))
        for x in m.get("iv_bad") or []:
            co.append("%s: an intervention line the page cannot read (%s): %s" % (L, x["source"], x["line"]))
        for x in m["disagree"]:
            co.append("%s: files disagree: %s" % (L, x))
    return {"mandrake": me, "conductor": co}


def his_questions_for(folder, questions):
    if questions is None:
        return UNM
    up = folder.upper()
    pat = re.compile(r"^\W*%s\b" % re.escape(folder))
    return [x for x in questions if up in x["item"].replace("_", "") or pat.match(x["q"] or "")]


# ---- gather ------------------------------------------------------------------------------------------------------

def time_now():
    """The clock the page measures against; MATURATION_NOW_CLOCK (a unix time) pins it for the selftest."""
    v = os.environ.get("MATURATION_NOW_CLOCK")
    return float(v) if v else dt.datetime.now(dt.timezone.utc).timestamp()


def dispatch_needs(now, errors):
    """The Dispatch step's "Needs Conductor" lines (rimflow/maturation_dispatch.py's reading, item
    RIMMANDRAKE_WIRE_DISPATCH_TO_LAUNCH_BUILDERS_MODS_SAT_IDLE): a stop, a hand step, a mod ready to advance. A reading
    over 30 min old is named as stale, never read as current."""
    try:
        sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
        import maturation_dispatch as MD  # noqa: E402
        rd, _ = read_json(os.path.join(MD.sdir(), "reading.json"))
    except Exception as e:      # noqa: BLE001
        errors.append("dispatch step reading: %s: %s" % (e.__class__.__name__, str(e)))
        return []
    if not isinstance(rd, dict):
        return ["The Dispatch step (maturation_dispatch.py) has no reading yet: nothing launches offline builders"]
    if now - float(rd.get("at") or 0) > 1800:
        return ["The Dispatch step's reading is %d min old (rm-maturation-dispatch.timer is not ticking)"
                % ((now - float(rd.get("at") or 0)) / 60)]
    return ["Dispatch step, %s: %s" % (rd.get("at_pac"), x) for x in rd.get("needs_conductor") or []]


def dispatch_pipeline(now, errors):
    """Per mod, what the Dispatch tick made of it (maturation_autonomy.py, item
    RIMMANDRAKE_AUTOMATE_MATURATION_HAND_STEPS_MODS_SAT_WAITING): moving / waiting on <unit> / PAUSED <why> / OWNER
    <card>, and for how long. A stale reading says so and lists nothing as current."""
    try:
        sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
        import maturation_dispatch as MD  # noqa: E402
        rd, _ = read_json(os.path.join(MD.sdir(), "reading.json"))
    except Exception as e:      # noqa: BLE001
        errors.append("dispatch pipeline reading: %s: %s" % (e.__class__.__name__, str(e)))
        return []
    if not isinstance(rd, dict) or now - float(rd.get("at") or 0) > 1800:
        return []
    out = []
    for mod, r in sorted((rd.get("mods") or {}).items()):
        if r.get("status"):
            out.append("%s: %s (%s min)%s" % (mod, r["status"], r.get("for_min", "?"),
                                              " STALLED" if mod in (rd.get("stalled") or []) else ""))
    return out


def gather(root, live=True):
    names = designer_names()
    croot = os.path.join(root, "design", "concepts")
    try:
        folders = sorted(f for f in os.listdir(croot) if not f.startswith("_") and os.path.isdir(os.path.join(croot, f)))
    except OSError:
        folders = []
    # RIMMANDRAKE_SHOW_VERSIONLESS_MOD_GRAFFITI_ON_MAP: a readable Designer record (stage.json) puts a mod on the map even
    # while no Design Version is named; a folder with neither stays in the plain list
    versioned = [f for f in folders if os.path.exists(os.path.join(croot, f, "version", "VERSION.json"))
                 or read_json(os.path.join(croot, f, "stage.json"))[0] is not None]
    others = [f for f in folders if f not in versioned]
    mods = [read_mod(root, f, names) for f in versioned]
    held = held_statements(root, versioned)
    lf = live_facts(versioned) if live else {"intake": UNM, "questions": None, "records": None, "notes": None,
                                             "errors": ["live reads off (--no-live)"]}
    now = time_now()
    journals = {m["name"]: m.pop("_journal") for m in mods}
    runs = None if lf["records"] is None else runs_for_mods(versioned, lf["records"], lf["notes"], journals, now)
    for m in mods:
        m["held_statements"] = held["per_mod"].get(m["name"], UNM)
        if m["held_statements"] == UNM and m["table"] and isinstance(m["table"].get("held"), int):
            m["held_statements"] = m["table"]["held"]
        m["his"] = his_questions_for(m["name"], lf["questions"])
        m["runs"] = UNM if runs is None else runs.get(m["name"], [])
        for e in lf["notes"] or []:        # the same line form in a ledger note on one of the mod's items
            if "CONDUCTOR INTERVENED" in str(e.get("text") or "").upper() and \
                    item_mod(e.get("id"), versioned, lf["notes"]) == m["name"]:
                g, b = parse_interventions(e.get("text"), "ledger note on %s" % e.get("id"))
                m["ivs"] += g
                m["iv_bad"] += b
        m["boxes"] = stage_boxes(m, m["runs"], m["ivs"], m["column"])
        for r in m["runs"] if isinstance(m["runs"], list) else []:
            r["last"] = last_words(r, lf["notes"]) if lf["notes"] is not None else UNM
        live_runs = [r for r in m["runs"] if r["live"]] if isinstance(m["runs"], list) else []
        if m["column"] == UNM:
            m["status"] = "unknown"
        elif m["held"]:
            m["status"] = "held"
        elif live_runs:
            m["status"] = "helper"
        else:
            m["status"] = "waiting"
    order = {c: i for i, c in enumerate(COLUMNS)}
    mods.sort(key=lambda m: (m["held"], -order.get(m["column"], -1), m["label"].lower()))
    other = []
    for f in others:
        has = sorted(os.listdir(os.path.join(croot, f)))
        other.append({"name": f, "files": has})
    needs = reactions(mods, now)
    if live:
        needs["conductor"] += dispatch_needs(now, lf["errors"])
        needs["pipeline"] = dispatch_pipeline(now, lf["errors"])
    return {"mods": mods, "others": other, "held": held, "needs": needs, "now": now,
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
    row_h, top = 78, 150
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
    p.append(arrow_mark(14, 64) + t_(32, 74.5, "the Conductor stepped in at this stage (count beside it)", 10.5, YELLOW, 700))
    p.append(t_(390, 74.5, "×N  the stage ran N times (cycled when N > 1)", 10.5, TEXT, 700))
    p.append(t_(700, 74.5, "●  a run is live on it now", 10.5, STATUS["helper"][0], 700))
    p.append(t_(880, 74.5, "HELD  a hold stands", 10.5, YELLOW, 700))
    # column heads with arrows
    for i, c in enumerate(COLUMNS):
        cx = COL_X0 + i * COLW
        p.append('<rect x="%.1f" y="88" width="%.1f" height="52" rx="6" fill="%s"/>' % (cx + 2, COLW - 4, CARD))
        p.append(t_(cx + COLW / 2, 108, COL_NUM[c], 15, TEXT, 800, "middle"))
        p.append(t_(cx + COLW / 2, 122, COL_NAME[c], 11, TEXT, 600, "middle"))
        p.append(t_(cx + COLW / 2, 134.5, clip(COL_LONG[c], 18), 10.5, FAINT, None, "middle"))
        if i:
            p.append('<path d="M%.1f 110 l4 4 l-4 4" stroke="%s" stroke-width="1.5" fill="none"/>' % (cx - 2, DIM))
    p.append(t_(LBL_X, 110, "MOD", 10.5, DIM, 700))
    p.append(t_(LBL_X, 124, "Design Version, state", 10.5, FAINT))
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


def arrow_mark(x, y, n=None):
    """The yellow arrow: a right-pointing block arrow 14 px wide whose tip touches x+14, top at y."""
    s = ('<path d="M%.1f %.1f h7 v-3.5 l7 7.5 l-7 7.5 v-3.5 h-7 z" fill="%s" stroke="%s" stroke-width=".8"/>'
         % (x, y + 4, YELLOW, INK, ))
    if n and n > 1:
        s += t_(x + 16, y + 10.5, str(n), 10.5, YELLOW, 800)
    return s


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
    p.append(t_(LBL_X + 4, y + 36, "no Design Version yet" if m["versionless"] else "%s · %s" % (m["version"], clip(st, 22)), 11, DIM))
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
        x = (m.get("boxes") or {}).get(c)
        if x:
            ivs = [i for i in x["ivs"] if not i.get("derived")]
            notes = []
            if x["held"]:
                notes.append(("HELD", YELLOW))
            if x["cycled"] > 1:
                notes.append(("×%d" % x["cycled"], YELLOW if x["cycled"] >= CYCLE_ALARM else TEXT))
            elif x["cycled"] == 1:
                notes.append(("×1", DIM))
            if any(r["live"] for r in x["runs"] + x["unplaced_live"]):
                notes.append(("●", STATUS["helper"][0]))
            if ivs or x["cycled"] > 1:
                p.append(arrow_mark(cx - 2, y + 33, len(ivs) + max(0, x["cycled"] - 1)))
            tx = cx + (24 if (ivs or x["cycled"] > 1) else 2)
            for word, col in notes:
                p.append(t_(tx, y + 44, word, 10, col, 700))
                tx += len(word) * 6 + 6
    line = "waits on: " + (m["waits_on"] if m["waits_on"] != UNM else "UNMEASURED (no journal line)")
    p.append(t_(COL_X0 + 6, y + 64, clip(line, 128), 10.5, DIM if m["waits_on"] != UNM else ALERT))
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
            chip("no Design Version named yet" if m["versionless"] else
                 (m["version"] if m["version"] != UNM else "version UNMEASURED"), "#dfe3ea"),
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
    if m["versionless"]:
        rows.append(row("Design Version", "no Design Version named yet" + (
            "; the Designer tree is locked, and the lock is the owner's to give" if m["owner_lock"] else "")))
    else:
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
    elif any(r["live"] for r in m["runs"]):
        runs = "<br>".join("%s run on <b>%s</b>, since %s (unit <code>%s</code>)" % (
            esc(r["model"]), esc(r["item"]), esc(r["start"]), esc(r["unit"])) for r in m["runs"] if r["live"])
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
            '%s%s%s</div>' % (esc(m["label"]), BG, TEXT, EDGE, fill if fill != "hatch" else "#7d8796", FONT,
                              " ".join(head), strip_html(m), boxes_html(m), "".join(rows)))


def stage_title(c):
    return {"intake": "Intake", "passed": "Passed"}.get(c, "Stage %s · %s" % (c, COL_NAME.get(c, c)))


def run_line(r, k):
    """One run in plain words; every number measured or UNMEASURED."""
    span = r["start"] + (" to " + r["stop"] if r["stop"] else "")
    usd = ("$%.2f" % r["usd"]) if r["usd"] != UNM else "dollars UNMEASURED"
    said = (" (it said about $%g" % r["said_usd"] + (" of a $%g cap)" % r["cap"] if r["cap"] != UNM else ")")) \
        if r["said_usd"] is not None else ""
    tok = (tokens_word(r["tokens"]) + " tokens") if r["tokens"] != UNM else "tokens UNMEASURED"
    wall = r["wall"] + (" so far" if r["live"] else "")
    return "run %d: %s, %s, %s, %s, %s%s" % (k, span, wall, r["outcome"], tok, usd, said)


def box_lines(m, c, x):
    """-> [(kind, text)] for one stage box: kind is live | runs | run | last | iv | cycle | note."""
    out = []
    lives = [r for r in x["runs"] + x["unplaced_live"] if r["live"]]
    for r in lives:
        out.append(("live", "LIVE NOW: %s (%s), since %s, %s so far%s" % (
            r["unit"], r["model"], r["start"], r["wall"],
            "; it has not written its stage yet" if r in x["unplaced_live"] else "")))
    if m["runs"] == UNM:
        out.append(("runs", "Runs at this stage: UNMEASURED (the run records were not read)"))
    else:
        n = x["cycled"]
        out.append(("cycle" if n > 1 else "runs", ("CYCLED: this stage has run %d times" % n) if n > 1 else
                    ("Runs at this stage: %d" % n)))
        for k, r in enumerate(x["runs"], 1):
            out.append(("run", run_line(r, k)))
        if x["runs"]:
            last = x["runs"][-1].get("last", UNM)
            out.append(("last", "Last result: " + (last if last != UNM else "UNMEASURED (no result note)")))
    if c == "1" and m.get("dcycles") not in (None, UNM):
        dc = m["dcycles"]
        names = designer_names()
        opens = ", ".join("%s %d×" % (names.get(s, s), n) for s, n in sorted(dc["opens"].items()))
        out.append(("cycle", "Designer inner loop (stage.json): opened %s; %d retries, %d over budget, %d invalidated"
                    % (opens or "nothing", dc["retry"], dc["over_budget"], dc["invalidated"])))
    elif c == "1" and m.get("dcycles") == UNM:
        out.append(("note", "Designer inner loop: UNMEASURED (no stage.json)"))
    for i in x["ivs"]:
        out.append(("iv", "Conductor, %s, %s: %s" % (i["when"], i["kind"], i["what"])))
    return out


def boxes_html(m):
    order = {c: i for i, c in enumerate(COLUMNS)}
    cur = order.get(m["column"], -1)
    parts = []
    for c, x in (m.get("boxes") or {}).items():
        ivs = [i for i in x["ivs"] if not i.get("derived")]
        edge = YELLOW if (ivs or x["cycled"] > 1 or x["held"]) else EDGE
        chips = []
        if x["held"]:
            chips.append(chip("HELD", YELLOW))
        if x["cycled"] > 1:
            chips.append(chip("CYCLED ×%d" % x["cycled"], YELLOW))
        if any(r["live"] for r in x["runs"] + x["unplaced_live"]):
            chips.append(chip("● RUN LIVE", STATUS["helper"][0]))
        if ivs:
            chips.append(chip("➤ Conductor stepped in: %d" % len(ivs), YELLOW))
        where = "now" if order.get(c, -1) == cur else ("behind it" if order.get(c, -1) < cur else "ahead")
        lines = []
        for kind, text in box_lines(m, c, x):
            if kind == "iv":
                lines.append('<div style="color:%s"><b>➤</b> %s</div>' % (YELLOW, esc(text)))
            elif kind in ("live", "cycle"):
                lines.append('<div style="color:%s;font-weight:700">%s</div>' % (
                    STATUS["helper"][0] if kind == "live" else YELLOW, esc(text)))
            elif kind == "run":
                lines.append('<div style="color:%s;padding-left:14px">%s</div>' % (DIM, esc(text)))
            else:
                lines.append("<div>%s</div>" % (esc(text).replace("UNMEASURED", val(UNM))))
        parts.append('<div style="border:1px solid %s;border-left:5px solid %s;border-radius:6px;padding:5px 10px;'
                     'margin:6px 0"><div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center"><b>%s</b>'
                     '<span style="color:%s;font-size:12px">(%s)</span> %s</div>%s</div>'
                     % (EDGE, edge, esc(stage_title(c)), DIM, where, " ".join(chips), "".join(lines)))
    early = [r for r in m["runs"] if r["placed"] == "before the pipeline"] if isinstance(m["runs"], list) else []
    if early:
        parts.append('<div style="color:%s;font-size:12px;margin:4px 0 8px">Before its journal began: %d more runs on '
                     'this mod\'s items (%s), not placed on a stage.</div>' % (
                         DIM, len(early), esc(", ".join(sorted({r["item"] for r in early})))))
    return "".join(parts)


def needs_md(d):
    out = []
    for key, title in (("mandrake", "Needs Mandrake"), ("conductor", "Needs Conductor"),
                       ("pipeline", "Pipeline now (the Dispatch tick)")):
        L = d["needs"].get(key) or []
        out += ["## %s (%d)" % (title, len(L)), ""] + (["- " + md_cell(x) for x in L] or ["- nothing on disk asks"]) + [""]
    return out


def needs_html(d):
    out = []
    for key, title, col in (("mandrake", "Needs Mandrake", ALERT), ("conductor", "Needs Conductor", YELLOW),
                            ("pipeline", "Pipeline now (the Dispatch tick)", YELLOW)):
        L = d["needs"].get(key) or []
        out.append('<h2 style="color:%s">%s (%d)</h2><ul>%s</ul>' % (col, title, len(L), "".join(
            "<li>%s</li>" % esc(x) for x in L) or "<li>nothing on disk asks</li>"))
    return "".join(out)


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
    niv = sum(1 for m in mods for x in (m.get("boxes") or {}).values() for i in x["ivs"] if not i.get("derived"))
    out.append(chip("➤ %d Conductor interventions" % niv, YELLOW))
    ncy = sum(1 for m in mods for x in (m.get("boxes") or {}).values() if x["cycled"] > 1)
    if all(m["runs"] != UNM for m in mods):
        out.append(chip("%d stage%s cycled" % (ncy, "" if ncy == 1 else "s"), YELLOW if ncy else "#3a4250", INK if ncy else TEXT))
    else:
        out.append(chip("cycles UNMEASURED", "#6b7380", TEXT))
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
        if m.get("versionless"):
            rows.append((m["label"], "no Design Version named yet" + (" (the lock is the owner's)" if m["owner_lock"] else ""),
                         where_word(m), clip(m["waits_on"], 110),
                         UNM if m["his"] == UNM else (", ".join(x["item"] for x in m["his"]) if m["his"] else "nothing"),
                         m["last_move"]))
            continue
        rows.append((m["label"], "%s, %s" % (m["version"], "locked" if m["state"].startswith("locked") else clip(m["state"], 30)),
                     where_word(m), clip(m["waits_on"], 110), needs, m["last_move"]))
    return rows


HEADS = ("mod", "Design Version", "stands at", "waits on", "needs you", "last movement")


def unread_lines(d):
    out = ["Any mod's position inside Stages 2 to 8 beyond what its journal's \"Stage now\" line says: those stages are not "
           "built and keep no record of their own yet (spec §6, \"the mod record\").",
           "Dollars per run: the run's result file loses its first bytes when its finish line is written over it, so "
           "claude's total_cost_usd is gone; the tokens in the run record are measured, and a run's own \"spent about "
           "$N\" is shown as its word, not a measurement. A live run's spend is unknown until it ends.",
           "His minutes per stage: nothing records them.",
           "A brief's \"Steward's decisions\" are not kept with the run record; they reach this page only through a "
           "\"CONDUCTOR INTERVENED\" journal line (spec §5).",
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
    parts_md += ["# " + title, "", measured, ""] + needs_md(d) + [top_chips(d), "", lead, "",
                                                                 "<div>" + picture(d) + "</div>", ""]
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
                  "<h1>%s</h1>" % title, "<p>%s</p>" % inline_md(measured), needs_html(d), "<p>%s</p>" % top_chips(d),
                  "<p class='m'>%s</p>" % inline_md(lead), picture(d),
                  "<h2>Every mod, one line</h2>", tbl, "<h2>Each mod</h2>"] + [card(m) for m in d["mods"]]
    if others:
        parts_html += ["<h2>Concept folders with no Design Version</h2><ul>%s</ul>" % others]
    parts_html += ["<h2>What this page cannot say</h2><ul>%s</ul>" % cant,
                   "<p class='m'>Regenerate: <code>python3 src/RimMandrake/Utils/maturation_now.py</code>. "
                   "Markdown twin: <code>%s\\MATURATION_NOW.md</code>.</p></div></body></html>" % esc(NATIVE_OUT)]
    return md, "\n".join(parts_html)


# ---- the phone images ----------------------------------------------------------------------------------------------
#
# He reads these on a phone that cannot open the HTML: 1080 px wide portrait PNGs, shown about 400 px wide, so body
# text is 38 px (about 14 px on his screen). One overview and one per mod. PIL draws them (a local library, no network).

PH_W, PH_M = 1080, 44
PH_FONTS = {"r": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "b": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"}
PH_SIZES = {"h1": 66, "h2": 50, "h3": 42, "body": 38, "small": 32}


class Phone:
    """A portrait page laid out top to bottom, drawn at the end at its measured height."""

    def __init__(self):
        from PIL import ImageFont
        self.F = {}
        for k, s in PH_SIZES.items():
            self.F[k + "r"] = ImageFont.truetype(PH_FONTS["r"], s)
            self.F[k + "b"] = ImageFont.truetype(PH_FONTS["b"], s)
        self.ops, self.y = [], PH_M

    def font(self, size, bold):
        return self.F[size + ("b" if bold else "r")]

    def wrap(self, text, font, width):
        words, lines, cur = [], [], ""
        for w in str(text).split():         # a word wider than the line (an item id) breaks after "_" or anywhere
            while font.getlength(w) > width:
                k = len(w)
                while k > 1 and font.getlength(w[:k]) > width:
                    k -= 1
                cut = w.rfind("_", 0, k) + 1 or k
                words.append(w[:cut])
                w = w[cut:]
            words.append(w)
        for w in words:
            t = (cur + " " + w).strip()
            if font.getlength(t) <= width or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = w
        return lines + ([cur] if cur else [])

    def text(self, s, size="body", bold=False, fill=TEXT, indent=0, gap=10, bullet=None):
        f = self.font(size, bold)
        x0 = PH_M + indent + (f.getlength(bullet + " ") if bullet else 0)
        lines = self.wrap(s, f, PH_W - PH_M - x0)
        lh = int(PH_SIZES[size] * 1.28)
        if bullet:
            self.ops.append(("t", PH_M + indent, self.y, bullet, f, fill))
        for ln in lines:
            self.ops.append(("t", x0, self.y, ln, f, fill))
            self.y += lh
        self.y += gap

    def rule(self, fill=EDGE, gap=24):
        self.ops.append(("r", PH_M, self.y, PH_W - PH_M, self.y + 3, fill, None))
        self.y += gap

    def strip(self, m):
        """The nine stage boxes, a big number in each, the yellow arrow and the run count under each."""
        n = len(COLUMNS)
        gap = 8
        w = (PH_W - 2 * PH_M - gap * (n - 1)) / n
        cur = COLUMNS.index(m["column"]) if m["column"] in COLUMNS else None
        f, fs = self.font("h3", True), self.font("small", True)
        low = 84
        for i, c in enumerate(COLUMNS):
            x = PH_M + i * (w + gap)
            if cur is None:
                fill, ink, outline = "#2a2f38", DIM, None
            elif i == cur:
                fill = STATUS[m["status"]][0]
                fill, ink = ("#5d6675", TEXT) if fill == "hatch" else (fill, STATUS[m["status"]][1])
                outline = TEXT if m["at_door"] else None
            elif i < cur:
                fill, ink, outline = DONE, "#9fd8c0", None
            else:
                fill, ink, outline = None, FAINT, EDGE
            self.ops.append(("r", x, self.y, x + w, self.y + 78, fill, outline))
            self.ops.append(("c", x + w / 2, self.y + 39, COL_NUM[c], f, ink))
            x_ = (m.get("boxes") or {}).get(c)
            if x_:
                ivs = len([k for k in x_["ivs"] if not k.get("derived")]) + max(0, x_["cycled"] - 1)
                if ivs:
                    self.ops.append(("a", x + w / 2, self.y + 86, ivs, fs))
                    low = max(low, 134)
                bits = []
                if x_["held"]:
                    bits.append(("HELD", YELLOW))
                if x_["cycled"]:
                    bits.append(("×%d" % x_["cycled"], YELLOW if x_["cycled"] > 1 else DIM))
                if any(r["live"] for r in x_["runs"] + x_["unplaced_live"]):
                    bits.append(("●", STATUS["helper"][0]))
                yy = self.y + (148 if ivs else 104)
                for word, col in bits:
                    self.ops.append(("c", x + w / 2, yy, word, fs, col))
                    yy += 40
                low = max(low, yy - self.y)
        self.y += low + 10

    def save(self, path):
        from PIL import Image, ImageDraw
        h = max(int(self.y + PH_M), PH_W * 5 // 4)     # portrait even when there is little to say
        im = Image.new("RGB", (PH_W, h), BG)
        g = ImageDraw.Draw(im)
        for op in self.ops:
            if op[0] == "t":
                g.text((op[1], op[2]), op[3], font=op[4], fill=op[5])
            elif op[0] == "c":
                g.text((op[1], op[2]), op[3], font=op[4], fill=op[5], anchor="mm")
            elif op[0] == "r":
                g.rounded_rectangle((op[1], op[2], op[3], op[4]), radius=8, fill=op[5], outline=op[6],
                                    width=3 if op[6] else 0)
            elif op[0] == "a":     # the yellow arrow, pointing right, with its count
                cx, y, n, f = op[1], op[2], op[3], op[4]
                x = cx - 34
                g.polygon([(x, y + 12), (x + 20, y + 12), (x + 20, y), (x + 40, y + 22), (x + 20, y + 44),
                           (x + 20, y + 32), (x, y + 32)], fill=YELLOW, outline=INK)
                g.text((x + 46, y + 22), str(n), font=f, fill=YELLOW, anchor="lm")
        tmp = path + ".tmp.png"
        im.save(tmp, "PNG", optimize=True)
        os.replace(tmp, path)
        return im.size


def phone_overview(d, now):
    P = Phone()
    P.text("Maturation now", "h1", True, gap=4)
    P.text("Measured %s. No model, no tokens." % pac(now), "small", fill=DIM, gap=24)
    for key, title, col in (("mandrake", "NEEDS MANDRAKE", ALERT), ("conductor", "NEEDS CONDUCTOR", YELLOW)):
        L = d["needs"][key]
        P.text("%s (%d)" % (title, len(L)), "h2", True, fill=col, gap=12)
        for x in L or ["nothing on disk asks"]:
            P.text(x, "body", bullet="•", gap=12)
        P.y += 14
    P.rule()
    for m in d["mods"]:
        P.text(m["label"], "h2", True, gap=2)
        P.text("%s · %s · %s" % (m["version"], where_word(m), STATUS[m["status"]][2]), "small", fill=DIM, gap=14)
        P.strip(m)
        for c, x in (m.get("boxes") or {}).items():
            for r in [r for r in x["runs"] + x["unplaced_live"] if r["live"]]:
                P.text("● LIVE %s since %s, %s so far" % (("at " + stage_title(c)) if r in x["runs"] else
                                                          "on this mod (its stage not yet written)", r["start"], r["wall"]),
                       "body", True,
                       fill=STATUS["helper"][0], gap=8)
            ivs = [i for i in x["ivs"] if not i.get("derived")]
            if ivs:
                P.text("➤ %s: the Conductor stepped in %d time%s" % (stage_title(c), len(ivs), "" if len(ivs) == 1 else "s"),
                       "body", fill=YELLOW, gap=8)
            if x["held"]:
                P.text("HELD at %s: %s" % (stage_title(c), clip(x["held"]["what"], 110)), "body", True, fill=YELLOW, gap=8)
            if x["cycled"] > 1:
                P.text("%s ran %d times (cycled)" % (stage_title(c), x["cycled"]), "body", fill=YELLOW, gap=8)
        if m["runs"] == UNM:
            P.text("Runs: UNMEASURED (the run records were not read)", "body", fill=ALERT, gap=8)
        P.text("Waits on: " + clip(m["waits_on"], 200), "small", fill=DIM, gap=10)
        P.rule()
    P.text("One image per mod sits beside this one. Made by maturation_now.py.", "small", fill=FAINT, gap=0)
    return P


def phone_mod(m, now):
    P = Phone()
    P.text(m["label"], "h1", True, gap=4)
    P.text("%s · %s · %s" % (m["version"], where_word(m), STATUS[m["status"]][2]), "body", fill=DIM, gap=4)
    P.text("Measured %s" % pac(now), "small", fill=FAINT, gap=20)
    P.strip(m)
    his = [q for q in m.get("jquestions") or [] if not q["answered"]]
    if his:
        P.text("OPEN QUESTIONS (%d)" % len(his), "h3", True, fill=ALERT, gap=10)
        for q in his:
            P.text("%d. %s%s" % (q["n"], q["text"], " (for the Conductor)" if q["who"] == "conductor" else ""),
                   "body", bullet="•", gap=8)
        P.y += 10
    P.rule()
    for c, x in (m.get("boxes") or {}).items():
        P.text(stage_title(c), "h2", True, fill=YELLOW if (x["ivs"] or x["held"]) else TEXT, gap=10)
        for kind, text in box_lines(m, c, x):
            if kind == "iv":
                P.text(text, "body", fill=YELLOW, bullet="➤", gap=10)
            elif kind == "live":
                P.text(text, "body", True, fill=STATUS["helper"][0], gap=10)
            elif kind == "cycle":
                P.text(text, "body", True, fill=YELLOW, gap=10)
            elif kind == "run":
                P.text(text, "small", fill=DIM, indent=24, gap=8)
            else:
                P.text(text, "body", fill=ALERT if UNM in text else TEXT, gap=10)
        P.rule()
    P.text("Waits on: " + str(m["waits_on"]), "body", fill=DIM, gap=10)
    P.text("Next: " + str(m["next"]), "body", fill=DIM, gap=0)
    return P


def write_phone(d, outdir, now):
    """-> [(path, size)]; PNGs that no longer belong to a mod are removed. PIL missing -> a named refusal, no images."""
    try:
        import PIL  # noqa: F401
    except ImportError:
        return [("PIL is not installed: no phone images", None)]
    os.makedirs(outdir, exist_ok=True)
    out = [(os.path.join(outdir, "00_overview.png"), None)]
    out[0] = (out[0][0], phone_overview(d, now).save(out[0][0]))
    for m in d["mods"]:
        p = os.path.join(outdir, "%s.png" % m["name"])
        out.append((p, phone_mod(m, now).save(p)))
    keep = {os.path.basename(p) for p, _ in out}
    for f in os.listdir(outdir):
        if f.endswith(".png") and f not in keep:
            os.remove(os.path.join(outdir, f))
    return out


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
    ap.add_argument("--no-phone", action="store_true", help="write no phone images")
    a = ap.parse_args(argv)
    d = gather(os.path.abspath(a.root), live=not a.no_live)
    if a.json:
        print(json.dumps(d, indent=1, default=str))
        return 0
    now = dt.datetime.fromtimestamp(d["now"], dt.timezone.utc)
    md, page = build(d, now)
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
    if not a.no_phone:
        imgs = write_phone(d, os.path.join(a.out, "MATURATION_NOW_phone"), now)
        print("phone images: %s" % ", ".join("%s %s" % (os.path.basename(p), "%dx%d" % s if s else "") for p, s in imgs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
