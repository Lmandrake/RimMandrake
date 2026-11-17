#!/usr/bin/env python3
"""maturation.py: the Maturation Pipeline's spine. Where each mod version stands, what its next step is, and the one
door it moves through.

Item RIMMANDRAKE_BUILD_MATURATION_SPINE_WHILE_DESIGN_STILL_MOVES; plan design/plans/2026-11-14-maturation-pipeline-build.md
(slice 1); spec design/specs/2026-11-13-maturation-pipeline.md. The owner, 2026-11-14: "I suspect it would be wise to start
a builder on the maturation pipeline even as we develop its components together now. Just so it's ready faster."

    python3 src/RimMandrake/rimflow/maturation.py seed [MOD ...]      write version/stage_record.json for each mod that has
                                                                      none, from its journal, VERSION.json and the detached-run
                                                                      records (--no-live: not the run records); never overwrites
    python3 src/RimMandrake/rimflow/maturation.py show MOD            the record, and spend per stage
    python3 src/RimMandrake/rimflow/maturation.py next MOD [--json]   the current stage's exit tests, its hand steps, one NEXT
    python3 src/RimMandrake/rimflow/maturation.py advance MOD --to STAGE --by SEAT --why "..."
            [--steward-confirms "..."] [--conductor-decision "..."] [--owner-said "..."] [--waits-on "..."] [--json]
    python3 src/RimMandrake/rimflow/maturation.py next-version MOD --by SEAT --why "..."   the record of VERSION.json's new version
    python3 src/RimMandrake/rimflow/maturation.py spend MOD --stage STAGE --tokens N [--usd X] [--wall-s S] --source RUN
            [--estimate]
        --root DIR   read and write design/concepts under DIR instead of this repo (the selftest's temp tree)

Stages are words, the spec's numbers beside them: intake, designer (Stage 1), preflight (2), offline_build (3),
blind_challenge (Stages 4 and 5, one stage, tests first), in_game (6), pre_human (7), his_walk (8), passed.

advance refuses (exit 1) an out-of-order move (forward one stage, back only along the spec's roads), a move while the
journal holds the stage (a "kind hold" intervention line with no later "kind release" for it), a record whose version is
not VERSION.json's, a failing exit test, a missing hand step, and a 4th blind cycle in one visit without
--conductor-decision. Every refusal is a refusal-contract verdict (refusal_contract.check runs on it before it is printed;
a malformed one exits 3). A move writes the record, appends one dated entry to the journal's history (what moved, why,
what was confirmed, the "Stage now" and "Waiting on" lines it replaced) and writes a new "Stage now" line that
maturation_now.py reads back to the same stage. --conductor-decision also writes the spec §5 intervention line.

    python3 src/RimMandrake/rimflow/maturation.py brief MOD [--out F]  slice 4: the mechanical half of an offline-build
                                                                      brief (refusals, bars not runnable, UNRUN scenes, the
                                                                      journal's Waiting on / Next, standing rules)
    python3 src/RimMandrake/rimflow/maturation.py launch MOD --budget-usd X --item ID [--model opus] [--seat BENCH]
            one capped detached builder on an offline-build mod with build work owed (detached_helper.py launch)

At the blind challenge (item RIMMANDRAKE_BUILD_BLIND_CHALLENGE_LAUNCHER_FOUR_MODS_PARKED): `brief` writes a blind-challenge
brief for cycle N (N = the record's cycles.total; the cycle_N folder is its record), from the mod's own test table and
files, its sealed "Steward's decisions" from the journal's intervention lines since the last cycle; `next` reads cycle
N's exit block and checks it against the record's files (read_exit; FORMAT_NOTES.md), names the launch when no cycle_N
folder exists, and keeps steward_confirms a hand step; `launch` launches one judge (opus or fable) when cycle N is owed.

At in-game acceptance (item RIMMANDRAKE_BUILD_IN_GAME_STAGE_LAUNCHER_PYRELANDS_ARRIVED_FIRST): `brief` writes the live
driver's brief for visit N (N = the moves into in_game; the visit_N folder is its record): every stage-6 check of the
test table with its exact command, what the newest blind cycle left owed to Stage 6, the bridge rules; `next` reads
visit N's exit block against its files (read_ingame_exit) and names the launch when no visit_N folder exists; `launch`
launches one live driver (opus) when visit N is owed and `rimflow bridge idle` says the bridge is takeable, and never
takes the bridge itself.

What is settled and tested here, and what stays a hand step (the open question named), is the plan's section 3 table.
This program has no timer and never retries; `launch` is the only way it starts work, through detached_helper.py with
--budget-usd (no default cap). Its caller on a timer is maturation_dispatch.py (the Dispatch step, its guard rails).
A blank "Steward's decisions" section does not refuse an offline-build launch (the owner, 2026-11-14 ~9 PM PST); the
brief carries a standing default, or version/steward_decisions.md when the Conductor writes one. MATURATION_DETACHED_HELPER
names a stand-in launcher (the selftest's fake). Holds are read from the journal only; a hold written only in a ledger
note is not seen (slice 2).
MATURATION_CLOCK (a unix time) pins the clock for the selftest. Selftest: selftest_maturation.py.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import time
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import maturation_now as MN     # noqa: E402  the journal readers: one parser, never a second one
import refusal_contract as RC   # noqa: E402
import judge_certificate as JC   # noqa: E402  the pre-judgement certificate (PRE_JUDGEMENT_CERTIFICATE)

UNM = "UNMEASURED"
RECORD = "version/stage_record.json"
# his Evidence-for-Ask ruling (2026-11-15): a new mod's first Design Version is 0.1.0 unless recorded evidence says
# otherwise, and the pipeline locks it itself (locked_by "pipeline", per_ruling this id)
EVIDENCE_FOR_ASK = "RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME"
PAC = MN.PAC

# (word, maturation_now column, the spec's number, plain name, the words a "Stage now" line uses)
STAGES = (
    ("intake", "intake", "Intake", "ideas waiting", "Intake, ideas waiting"),
    ("designer", "1", "Stage 1", "Designer", "Stage 1, the Designer"),
    ("preflight", "2", "Stage 2", "Preflight", "Stage 2, preflight"),
    ("offline_build", "3", "Stage 3", "Offline build", "Stage 3, offline build"),
    ("blind_challenge", "4+5", "Stages 4 and 5", "Blind challenge, tests first",
     "Stages 4 and 5, the blind challenge (tests first)"),
    ("in_game", "6", "Stage 6", "In-game acceptance", "Stage 6, in-game acceptance"),
    ("pre_human", "7", "Stage 7", "Pre-human check", "Stage 7, the pre-human check"),
    ("his_walk", "8", "Stage 8", "His live walk", "Stage 8, his live walk"),
    ("passed", "passed", "Passed", "Version passed", "Version passed on his word"),
)
WORDS = [s[0] for s in STAGES]
COL = {s[0]: s[1] for s in STAGES}
WORD_OF_COL = {s[1]: s[0] for s in STAGES}
NUM = {s[0]: s[2] for s in STAGES}
NAME = {s[0]: s[3] for s in STAGES}
LINE = {s[0]: s[4] for s in STAGES}
# The roads back the spec draws (§3 map; rule 2 of validation_map_and_rules.md, carried). Forward is one stage only.
ROADS_BACK = {
    "preflight": ("designer",),
    "blind_challenge": ("blind_challenge",),
    # in_game -> in_game: a failed line only the game can show stays Stage 6 work and opens the next visit (spec Stage 6
    # road back, "the lowest stage that can show the fault"; RIMMANDRAKE_CLOSE_OFFLINE_STAGE_ITEMS_OFFLINE_GAME_WAS_DEMANDED)
    "in_game": ("offline_build", "blind_challenge", "in_game"),
    "pre_human": ("preflight", "offline_build", "blind_challenge", "in_game"),
    "his_walk": ("offline_build", "blind_challenge", "in_game"),
}
# "Offline stages never wait for a game" (spec §5). Only a Stage 6 record's runs may take the bridge or the game (Stage 8
# is his walk on his machine); every other stage's holder, fixer and steward is offline
# (RIMMANDRAKE_CLOSE_OFFLINE_STAGE_ITEMS_OFFLINE_GAME_WAS_DEMANDED).
OFFLINE_STAGES = ("intake", "designer", "preflight", "offline_build", "blind_challenge")
LIVE_NEEDS = ("game-up", "bridge")      # the model.NEEDS windows only a live game opens


def game_takeable(stage):
    """True only at in-game acceptance (Stage 6): the one stage whose runs may take the bridge and the game."""
    return stage == "in_game"


def game_only_cmd(mod, ids):
    """-> the move that returns a record parked at an offline stage to Stage 6 when its open road-back items are all
    faults only the game can show."""
    return ("python3 src/RimMandrake/rimflow/maturation.py advance %s --to in_game --game-only %s --by <SEAT> --why "
            "\"every open road-back item is a fault only the game can show\"" % (mod, ",".join(ids)))


CYCLE_LIMIT = 3     # his words, 2026-11-13: after three cycles the Conductor decides; a fourth never starts on its own


def label(w):
    return "%s (%s)" % (NAME[w], NUM[w]) if w in NAME else str(w)


def col_of(w):
    return COL.get(w, UNM)


def now_ts():
    v = os.environ.get("MATURATION_CLOCK")
    return float(v) if v else dt.datetime.now(dt.timezone.utc).timestamp()


def iso(t):
    return dt.datetime.fromtimestamp(t, PAC).isoformat(timespec="seconds")


def pac_heading(t):
    d = dt.datetime.fromtimestamp(t, PAC)
    return "%s %s %s" % (d.strftime("%Y-%m-%d"), d.strftime("%I:%M %p").lstrip("0"), d.strftime("%Z"))


def mod_dir(root, mod):
    return os.path.join(root, "design", "concepts", mod)


def rel(mod, p):
    return "design/concepts/%s/%s" % (mod, p)


def read_text(root, mod, p):
    try:
        with open(os.path.join(mod_dir(root, mod), p), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def read_json(root, mod, p):
    t = read_text(root, mod, p)
    if t is None:
        return None, "no file"
    try:
        return json.loads(t), None
    except ValueError:
        return None, "unreadable JSON"


def write_text(root, mod, p, text):
    path = os.path.join(mod_dir(root, mod), p)
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)   # a concept seeded before its Lock has no version/ yet
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def dump(rec):
    return json.dumps(rec, indent=2, ensure_ascii=False) + "\n"


def load(root, mod):
    rec, _ = read_json(root, mod, RECORD)
    return rec


# ---- seeding: the record from what the hand-runs already wrote ------------------------------------------------------

def _since(hist, col):
    """-> (iso or UNMEASURED, how it was read): the earliest dated journal heading naming the stage, else the newest one
    naming the stage before it (that stage's end), else UNMEASURED."""
    named = [(t, h) for t, h in hist if col in MN.stages_named(h)]
    if named:
        t, h = min(named, key=lambda x: x[0])
        return t.isoformat(timespec="seconds"), "the earliest journal heading naming it: %s" % h
    i = WORDS.index(WORD_OF_COL[col]) if col in WORD_OF_COL else 0
    if i > 0:
        prev = COL[WORDS[i - 1]]
        named = [(t, h) for t, h in hist if prev in MN.stages_named(h)]
        if named:
            t, h = max(named, key=lambda x: x[0])
            return t.isoformat(timespec="seconds"), "the end of the stage before it, journal heading: %s" % h
    return UNM, "no dated journal heading names it"


def _spend_row(r, stages):
    """One detached run (a maturation_now run view) -> its spend entry, under the stage words it worked in."""
    usd = r.get("usd") if isinstance(r.get("usd"), (int, float)) else r.get("said_usd")
    return {"stage": stages[0], "stages": stages, "tokens": r.get("tokens") if isinstance(
        r.get("tokens"), int) else UNM, "usd": usd if isinstance(usd, (int, float)) else UNM,
        "usd_from": "run record" if isinstance(r.get("usd"), (int, float)) else
        ("the run's own words" if isinstance(r.get("said_usd"), (int, float)) else UNM),
        "wall_s": round(r["wall_s"]) if isinstance(r.get("wall_s"), (int, float)) else UNM,
        "cap_usd": r.get("cap") if isinstance(r.get("cap"), (int, float)) else UNM,
        "unit": r.get("unit"), "source": "detached run %s (item %s)" % (r.get("unit"), r.get("item")),
        "kind": "measured"}


def _run_spend(m):
    """The detached runs maturation_now placed on this mod's stages -> spend entries (one per run, never twice)."""
    out, seen = [], set()
    for col, box in sorted((m.get("boxes") or {}).items()):
        for r in box.get("runs") or []:
            u = r.get("unit")
            if not u or u in seen:
                continue
            seen.add(u)
            stages = [WORD_OF_COL[c] for c in (r.get("stages") or [col]) if c in WORD_OF_COL] or [WORD_OF_COL.get(col)]
            out.append(_spend_row(r, stages))
    return out


def seed_mod(root, mod, live=True, gathered=None):
    """-> (record, made). An existing record is returned untouched (made False): seeding never retypes state."""
    have = load(root, mod)
    if have is not None:
        return have, False
    m = None
    if gathered is not None:
        m = next((x for x in gathered.get("mods", []) if x["name"] == mod), None)
    if m is None:
        m = MN.read_mod(root, mod, MN.designer_names())
    col = m.get("column")
    if col not in WORD_OF_COL:
        raise ValueError("%s: its stage cannot be read (%s); write the journal's Stage now line first" % (mod, col))
    jtext = read_text(root, mod, "journal.md")
    hist = MN.parse_journal(jtext)["history"] if jtext else []
    since, since_from = _since(hist, col)
    v, _ = read_json(root, mod, "version/VERSION.json")
    v = v or {}
    t = now_ts()
    rec = {
        "schema": 1, "mod": mod, "version": m.get("version", UNM), "stage": WORD_OF_COL[col],
        "stage_label": label(WORD_OF_COL[col]), "since": since, "since_from": since_from,
        "at_door": bool(m.get("at_door")),
        "seeded": {"at": iso(t), "by": "maturation.py seed", "stage_read_from": m.get("stage_from", UNM),
                   "stage_line": m.get("stage_text", UNM)},
        "cycles": {"visit": 0, "total": 0}, "pre_human_arrivals": 0, "moves": [], "spend": [],
    }
    if isinstance(v.get("tokens_spent"), int):
        rec["spend"].append({"stage": "designer", "stages": ["designer"], "tokens": v["tokens_spent"], "usd": UNM,
                             "wall_s": UNM, "source": rel(mod, "version/VERSION.json") + " tokens_spent",
                             "kind": "mixed: measured and estimated charges, see VERSION.json measured_from"})
    if live:
        rec["spend"] += _run_spend(m)
        rec["seeded"]["run_records"] = "read" if isinstance(m.get("runs"), list) else UNM
    else:
        rec["seeded"]["run_records"] = "not read (--no-live)"
    write_text(root, mod, RECORD, dump(rec))
    return rec, True


# ---- the journal: holds, the Stage now line, the history entry -----------------------------------------------------

def held(jtext, stage):
    """True when the journal's last hold or release line for the stage is a hold (spec §5 item 5)."""
    ivs, _ = MN.parse_interventions(jtext or "", "journal")
    last = None
    for iv in ivs:
        if iv["stage"] == col_of(stage) and iv["kind"] in ("hold", "release"):
            last = iv["kind"]
    return last == "hold"


def _bullet(text, field):
    """-> (start, end) line indexes of the "- **<field>:**" bullet and its indented continuation, or None."""
    lines = text.split("\n")
    rx = re.compile(r"^\s*-\s*\*\*%s[^*]*:?\*\*" % re.escape(field))
    for i, ln in enumerate(lines):
        if rx.match(ln):
            j = i + 1
            while j < len(lines) and lines[j].startswith("  ") and not lines[j].lstrip().startswith("- **"):
                j += 1
            return i, j
    return None


def replace_bullet(text, field, new):
    """-> (text, the old bullet's text or None). A missing bullet is added under "## The mod as it stands"."""
    lines = text.split("\n")
    span = _bullet(text, field)
    if span:
        i, j = span
        old = " ".join(x.strip() for x in lines[i:j])
        return "\n".join(lines[:i] + [new] + lines[j:]), old
    for i, ln in enumerate(lines):
        if ln.startswith("## The mod as it stands"):
            k = i + 1
            while k < len(lines) and not lines[k].strip():
                k += 1
            return "\n".join(lines[:k] + [new] + lines[k:]), None
    return new + "\n" + text, None


def add_intervention(text, line):
    """The line goes at the end of the "### Conductor interventions" list (the first part of the history)."""
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("### Conductor interventions"):
            j, last = i + 1, i
            while j < len(lines) and not lines[j].startswith("#"):
                if lines[j].strip():
                    last = j
                j += 1
            at = last + 1
            pad = [""] if last == i else []
            return "\n".join(lines[:at] + pad + [line] + lines[at:])
    return text.rstrip("\n") + "\n\n### Conductor interventions\n\n" + line + "\n"


# ---- the exit tests --------------------------------------------------------------------------------------------------

LOCKED_BARS = "version/locked_bars.json"


def locked_bars(root, mod, v=None):
    """-> (ids, None) from version/locked_bars.json, the bar ids recorded at Lock (maturation.py lock-bars); (None, None)
    when it is absent (a version locked before the record existed reads as before); (None, why) when it is unreadable or
    is another version's than VERSION.json's."""
    lb, err = read_json(root, mod, LOCKED_BARS)
    if lb is None:
        return None, (None if err == "no file" else "%s: %s" % (LOCKED_BARS, err))
    ids = lb.get("ids") if isinstance(lb, dict) else None
    if not isinstance(ids, list) or not ids or not all(isinstance(i, str) and i for i in ids) or len(set(ids)) != len(ids):
        return None, "%s holds no list of unique bar ids" % LOCKED_BARS
    if isinstance(v, dict) and lb.get("version") != v.get("version"):
        return None, ("%s records version %s's bars; VERSION.json names %s: record them with `maturation.py lock-bars "
                      "%s`" % (LOCKED_BARS, lb.get("version"), v.get("version"), mod))
    return ids, None


def _table_runnable(tt, v=None, locked=None):
    bars = tt.get("bars") if isinstance(tt, dict) else None
    if not isinstance(bars, list) or not bars:
        return None, "the table has no bars list"
    # RIMMANDRAKE_DERIVE_CHECKS_FROM_LOCKED_BARS: the table holds the locked version's bars, each once, and when the
    # lock recorded them (locked_bars.json) exactly those: a table that drops or invents a bar is no table of the version
    ids = [b.get("id") for b in bars if isinstance(b, dict)]
    if len(set(ids)) != len(ids) or None in ids:
        return None, "the table's bar ids are not unique (or one has none)"
    if locked is not None:
        miss, extra = [i for i in locked if i not in ids], [i for i in ids if i not in locked]
        if miss or extra:
            return None, ("the table's bars are not the %d locked bars: missing %s, not locked %s; remake the table from "
                          "the locked bars, or when his card changed them, `maturation.py lock-bars <Mod> --add/--remove "
                          "<id> --source OWNER:<tsn>`" % (len(locked), ", ".join(miss) or "none",
                                                           ", ".join(extra) or "none"))
    flags = [b.get("every_decider_runnable_today") for b in bars if isinstance(b, dict)]
    if len(flags) != len(bars) or not all(isinstance(f, bool) for f in flags):
        return None, "a bar lacks a true/false every_decider_runnable_today"
    return [b.get("id", "?") for b in bars if b.get("every_decider_runnable_today") is not True], len(bars)


def owed_scene_parts(root, mod, tt):
    """-> {bar id: [item ids]} for bars a scene decides whose scenes.json entry names an owed_parts_item still open on
    the ledger (not closed, dropped or superseded): those reads are not built yet, so the table's stored
    every_decider_runnable_today cannot say the check runs (RIMMANDRAKE_REFUSE_EXIT_ON_OWED_SCENE_PARTS_STALE_FLAG)."""
    sc, _ = read_json(root, mod, "scenes.json")
    scenes = sc.get("scenes") if isinstance(sc, dict) else None
    owes = {}
    for s in scenes if isinstance(scenes, list) else []:
        v = s.get("owed_parts_item") if isinstance(s, dict) else None
        ids = [v] if isinstance(v, str) else [x for x in v if isinstance(x, str)] if isinstance(v, list) else []
        if ids and s.get("id"):
            owes[s["id"]] = ids
    if not owes or not isinstance(tt, dict):
        return {}
    ended = ledger_ended(root, {i for ids in owes.values() for i in ids})
    out = {}
    for b in tt.get("bars") or []:
        if isinstance(b, dict) and b.get("id"):
            open_ = sorted({i for d in b.get("decides") or [] for i in owes.get(d, []) if i not in ended})
            if open_:
                out[b["id"]] = open_
    return out


def bar_fingerprints(tt):
    """-> {bar id: hash of its deciders' test entries}: a refused bar that turns runnable with its checks unchanged is a
    flag flipped, not progress (RIMMANDRAKE_DERIVE_CHECKS_FROM_LOCKED_BARS)."""
    import hashlib
    tests = (tt or {}).get("tests") or {} if isinstance(tt, dict) else {}
    out = {}
    for b in (tt or {}).get("bars") or [] if isinstance(tt, dict) else []:
        if isinstance(b, dict) and b.get("id"):
            ds = sorted(str(x) for x in (b.get("decides") or []))
            out[b["id"]] = hashlib.sha256(json.dumps([ds, [tests.get(x) for x in ds]], sort_keys=True,
                                                     default=str).encode()).hexdigest()[:16]
    return out


def _walk_deciders(tt, bar_ids):
    """-> the bars among bar_ids that a stage-8 look (his walk) decides. The throwaway table scripts disagree on such a
    look: Pyrelands' leaves it out of "runnable", Gimme Some Slack's counts it as never runnable, so such a bar's false
    flag cannot tell whether its other deciders run. Those bars are a hand step, never a refusal or a guess."""
    tests = (tt or {}).get("tests") or {}
    looks = {k for k, t in tests.items() if isinstance(t, dict) and t.get("kind") == "look" and str(t.get("stage")) == "8"}
    out = []
    for b in tt.get("bars") or []:
        if isinstance(b, dict) and b.get("id") in bar_ids and looks & set(b.get("decides") or []):
            out.append(b["id"])
    return out


def ledger_implemented(root, ids):
    """-> {id: sha} for these ledger items whose newest `implemented` event (rimflow refuses one whose sha is not on
    origin/main) has no later reopen (a `live` event with result broken), in time order as ledger_needs reads."""
    d = os.path.join(root, "infrastructure", "state", "ledger", "events")
    want, seen = set(ids), []
    for f in sorted(os.listdir(d)) if os.path.isdir(d) and want else []:
        if not f.endswith(".jsonl"):
            continue
        with open(os.path.join(d, f), encoding="utf-8") as fh:
            for ln in fh:
                if '"implemented"' not in ln and '"live"' not in ln:
                    continue
                try:
                    e = json.loads(ln)
                except ValueError:
                    continue
                k, i = e.get("event"), e.get("id")
                if i in want and (k == "implemented" and e.get("sha") or k == "live" and e.get("result") == "broken"):
                    seen.append((str(e.get("ts") or ""), e.get("tsn") or 0, i, e.get("sha") if k == "implemented" else None))
    out = {}
    for _, _, i, sha in sorted(seen, key=lambda x: (x[0], x[1])):
        if sha:
            out[i] = sha
        else:
            out.pop(i, None)
    return out


def live_known_red_owed(root, tt, bar_ids):
    """-> {bar id: [(test id, known-red item, why)]} for the bars among bar_ids whose only unrunnable deciders are live
    stage-6 checks whose entry exists and whose known red is cured (closed) or implemented with a remainder that needs
    the live game (ledger needs game-up or bridge). Such a check runs: it is UNRUN with its command and owed to Stage 6,
    which runs every decider (RIMMANDRAKE_ROUTE_LIVE_ONLY_DECIDER_STAGE_THREE_NO_ROAD; the owner's 2026-11-13 rule, an
    unrun live test is recorded UNRUN with its command). Any decider of another shape, an offline known red, an
    unlanded fix or an offline remainder keeps the bar refused: the bar itself is never loosened."""
    tests = (tt or {}).get("tests") or {} if isinstance(tt, dict) else {}
    bars = {b.get("id"): b for b in (tt or {}).get("bars") or [] if isinstance(b, dict)} if isinstance(tt, dict) else {}
    reds = {t.get("known_red") for t in tests.values() if isinstance(t, dict) and isinstance(t.get("known_red"), str)}
    if not reds or not bar_ids:
        return {}
    need, ended, impl = ledger_needs(root, reds), ledger_ended(root, reds), ledger_implemented(root, reds)
    out = {}
    for bid in bar_ids:
        dec, owe, fine = (bars.get(bid) or {}).get("decides") or [], [], True
        for d in dec:
            t = tests.get(d)
            if not isinstance(t, dict):
                fine = False
            elif t.get("kind") == "offline":
                rt = t.get("runs_today") or {}
                fine = fine and not t.get("known_red") and rt.get("ran") is True and rt.get("result") == "PASS"
            elif t.get("kind") in ("live_minimal", "live_full") and str(t.get("stage")) == "6" \
                    and t.get("entry_exists") is True:
                k = t.get("known_red")
                if not k:
                    continue
                if k in ended:
                    owe.append((d, k, "closed"))
                elif k in impl and need.get(k) in LIVE_NEEDS:
                    owe.append((d, k, "implemented at %s, needs %s" % (impl[k], need[k])))
                else:
                    fine = False
            else:
                fine = False
        if dec and fine and owe:
            out[bid] = owe
    return out


def _reached(root, stage):
    """Mods (other than none) whose record has ever stood at `stage`."""
    out = []
    croot = os.path.join(root, "design", "concepts")
    for f in sorted(os.listdir(croot)) if os.path.isdir(croot) else []:
        r = load(root, f)
        if r and (r.get("stage") == stage or any(mv.get("to") == stage for mv in r.get("moves") or [])):
            out.append(f)
    return out


PASS_REFUSED = re.compile(r"\b(not|n't|never|don'?t|do not)\b[^.]{0,30}\bpass", re.I)


def owner_event(root, owner):
    """RIMMANDRAKE_REQUIRE_OWNER_EVENT_TO_PASS: --owner-said for a pass is OWNER:<tsn>, an event of his on the OWNER
    shard carrying byCard or ownerSaid that does not refuse the pass. -> (event, observed) or (None, why not)."""
    import concept_tree as CT
    m = re.match(r"^OWNER:(\d+)$", str(owner or "").strip())
    if not m:
        return None, "%r is not OWNER:<tsn> (his event on the OWNER shard)" % (owner or "none")
    ev = CT.owner_events(root, REPO).get(m.group(1))
    if not isinstance(ev, dict):
        return None, "OWNER:%s is not on the OWNER shard" % m.group(1)
    words = str(ev.get("ownerSaid") or ev.get("byCard") or "").strip()
    if not words:
        return None, "OWNER:%s carries no byCard or ownerSaid" % m.group(1)
    if PASS_REFUSED.search(words):
        return None, "OWNER:%s's words refuse the pass: %r" % (m.group(1), words[:80])
    return ev, "OWNER:%s: %s" % (m.group(1), words[:80])


def certificate(root, mod, to="blind_challenge"):
    """judge_certificate.certify, never raising: a guard that cannot look says did not run and lets the work through."""
    try:
        return JC.certify(root, mod, to)
    except Exception as e:  # noqa: BLE001
        return {"ok": True, "rows": [], "to": to, "mod": mod,
                "did_not_run": ["the certificate did not run: %s: %s; the mod goes through on this guard" % (
                    type(e).__name__, e)]}


def evaluate(root, mod, to, steward=None, conductor=None, owner=None, by=None, why=None, check_by=False, game_only=None):
    """-> {"ok", "verdict", "hand_steps"}: every clause of the move, passed or refused, as a refusal-contract verdict."""
    rec = load(root, mod) or {}
    cur = rec.get("stage", UNM)
    request = ("advance %s from %s to %s by %s; why: %s; steward_confirms: %s; conductor_decision: %s; owner_said: %s"
               % (mod, cur, to, by or "none", why or "none", steward or "none", conductor or "none", owner or "none"))
    rec_ref, req_ref = rel(mod, RECORD), "request"
    inputs = {req_ref: request, rec_ref: dump(rec)}
    crit, passed, refusals, hand = {}, [], [], []

    def refs(*names):
        for n in names:
            if n not in inputs:
                p = n.split("design/concepts/%s/" % mod, 1)[-1]
                inputs[n] = read_text(root, mod, p) or "(no file at %s)" % n
        return list(names)

    def clause(cid, text, good, evidence, observed=None, would_pass=None, fix=None, cost="edit", attainable="yes",
               why_sound=None):
        crit[cid] = text
        if good:
            passed.append({"clause": cid, "evidence": refs(*evidence)})
            return
        refusals.append({
            "clause": cid, "criterion_hash": RC.criterion_hash(text), "evidence": refs(*evidence),
            "observed": observed, "would_pass": would_pass,
            "smallest_fix": {"what": fix, "attainable": attainable, "cost": cost},
            "criterion_verdict": "sound", "criterion_why": why_sound or "it is the spec's settled rule for this move",
            "new_since": "first"})

    # order: forward one stage, or back along a drawn road
    i_cur = WORDS.index(cur) if cur in WORDS else -1
    forward = i_cur >= 0 and to in WORDS and WORDS.index(to) == i_cur + 1
    back = to in ROADS_BACK.get(cur, ())
    # the game-only road: a record sent to an offline stage from Stage 6 goes back to Stage 6 when every open item of its
    # road back is a fault only the game can show (its `game_only` clause below checks the items)
    back = back or bool(game_only and to == "in_game" and cur in OFFLINE_STAGES)
    nxt = WORDS[i_cur + 1] if 0 <= i_cur < len(WORDS) - 1 else None
    clause("order", "a mod moves forward one stage at a time, or back only along a road the spec draws",
           forward or back, [req_ref, rec_ref],
           observed="asked %s to %s; the record stands at %s" % (cur, to, cur),
           would_pass="advance --to %s (the next stage)%s" % (nxt or "nothing", (" or back to " + ", ".join(
               ROADS_BACK[cur])) if cur in ROADS_BACK else ""),
           fix="run advance with --to %s, finishing %s first" % (nxt or cur, label(cur)),
           why_sound="the eight stages, their order and the roads back are his and carried rulings (spec §3)")
    if game_only and to == "in_game" and cur in OFFLINE_STAGES:
        ids = [str(i) for i in game_only]
        need, ended = ledger_needs(root, ids), ledger_ended(root, ids)
        offline = [i for i in ids if need.get(i) not in LIVE_NEEDS]
        shut = [i for i in ids if i in ended]
        was6 = any(m.get("from") == "in_game" for m in rec.get("moves") or [])
        # every open sibling (same caused_by) is named: an offline item of the same road back keeps the record here
        unnamed = [x["id"] for x in ledger_items_caused_by(root, sorted(set(ledger_caused_by(root, ids).values())))
                   if x["id"] not in ids]
        clause("game_only", "every item the move names is open and needs the live game (ledger needs game-up or "
               "bridge), it names every open item of its road back, and the record came to this stage from Stage 6",
               bool(ids) and not offline and not shut and not unnamed and was6, [req_ref, rec_ref],
               observed="items %s; needs %s; closed %s; open and not named %s; a move from in_game on the record: %s"
               % (", ".join(ids), ", ".join("%s=%s" % (i, need.get(i)) for i in ids), ", ".join(shut) or "none",
                  ", ".join(unnamed) or "none", was6),
               would_pass="--game-only naming every open item of the road back, each with needs game-up or bridge, on "
                          "a record sent here from Stage 6",
               fix="work an item an offline test can show here (its offline test first, its in-game check recorded "
                   "UNRUN with `maturation.py unrun`), or set its needs (`rimflow needs <ID> game-up`) only when no "
                   "offline test can show it", cost="edit",
               why_sound="the spec's Stage 6 road back: a failed line goes to the lowest stage that can show it, and "
                         "offline stages never wait for a game")
    # by: RIMMANDRAKE_REQUIRE_OWNER_EVENT_TO_PASS: the move names the seat that makes it (a ledger seat's name)
    if check_by:     # a move (advance) names its mover; next and brief ask what a move needs, by no seat
        clause("by", "the move names the seat that makes it", bool(re.match(r"^[A-Z][A-Z0-9_]{2,}$", str(by))),
               [req_ref], observed="advance %s from %s to %s by %s" % (mod, cur, to, by or "nobody"),
               would_pass="--by naming a ledger seat in capitals (BENCH, CONDUCTOR, RUNNER)",
               fix="pass --by with the seat that makes the move", cost="edit")
    # version: the record is for the Design Version VERSION.json names
    v, verr = read_json(root, mod, "version/VERSION.json")
    vv = (v or {}).get("version", UNM)
    clause("version", "the stage record is for the Design Version that version/VERSION.json names",
           v is not None and vv == rec.get("version"), [rec_ref, rel(mod, "version/VERSION.json")],
           observed="the record says version %s; VERSION.json says %s" % (rec.get("version"), vv if v else verr),
           would_pass="a stage_record.json whose version field equals VERSION.json's version %s" % vv,
           fix="open the new version with `maturation.py next-version` (the Conductor's ordering call against the other "
               "mods, delegation_policy.md §1 and Evidence-for-Ask; a Divergent-or-not call stays his at filing), "
               "which seeds a fresh stage record for it", cost="edit")
    # hold: the journal holds the stage
    jref = rel(mod, "journal.md")
    jtext = read_text(root, mod, "journal.md") or ""
    clause("hold", "no Conductor hold stands on the current stage (a kind hold line with no later kind release)",
           not held(jtext, cur), [jref],
           observed="the journal's last hold or release line for stage %s is a hold" % col_of(cur),
           would_pass="a CONDUCTOR INTERVENED line of kind release for stage %s after the hold" % col_of(cur),
           fix="the Conductor writes the release line in the journal's Conductor interventions list when the hold's "
               "reason has ended", cost="owner", why_sound="a hold stands until its release (the Conductor's rule, spec §5 item 5)")

    if forward:
        if cur == "intake":
            walked = _reached(root, "his_walk")
            # his words in the request admit this one mod before any walk (owner, 2026-11-15)
            clause("intake_closed", "no mod enters the Designer until one of the advancing mods has reached his walk, "
                   "unless his words in the request admit it", bool(walked) or bool(owner), [req_ref],
                   observed="no stage record has reached his_walk and owner_said is empty; this request is for %s" % mod,
                   would_pass="one of the advancing mods has a record that reached his_walk, or --owner-said quoting "
                              "his order to add this mod", fix="wait for a walk, or pass his words admitting the mod",
                   attainable="yes", cost="rerun", why_sound="his card of 2026-11-14: wait for one full pass; "
                   "his order of 2026-11-15 adds a mod when the pipeline is not busy")
            # after the first walk a waiting mod enters in queue order with no ask: his card of 2026-11-14 picked only
            # "Wait for one full pass" (the "asked again then" was our note), so nothing argues against the obvious
            # answer (his Evidence-for-Ask ruling, 2026-11-15)
        elif cur == "designer":
            st = str((v or {}).get("state") or "")
            # RIMMANDRAKE_REQUIRE_OWNER_EVENT_TO_PASS: "locked" as a word (a date may follow), locked by him, or by the
            # pipeline under his Evidence-for-Ask ruling (a new mod's 0.1.0 with no recorded evidence against it)
            by_ = str((v or {}).get("locked_by") or "")
            lk = bool(re.match(r"^locked(\s|$)", st)) and (by_ == "owner" or (
                by_ == "pipeline" and (v or {}).get("per_ruling") == EVIDENCE_FOR_ASK))
            clause("locked", "the Design Version is locked (VERSION.json state locked, by him or by the pipeline "
                   "under the Evidence-for-Ask ruling)",
                   lk, [rel(mod, "version/VERSION.json")],
                   observed="VERSION.json state is %s, locked_by %s" % (st or UNM, by_ or UNM),
                   would_pass="VERSION.json state reads locked, locked_by owner (his words in owner_words) or "
                              "locked_by pipeline with per_ruling %s" % EVIDENCE_FOR_ASK,
                   fix="finish the Designer pass; the Dispatch step then locks a new mod at 0.1.0 itself, or asks him "
                       "with the recorded evidence against 0.1.0", cost="rerun",
                   why_sound="the Design Versions ruling, and his Evidence-for-Ask ruling of 2026-11-15 (the obvious "
                             "answer is taken unless evidence says otherwise)")
        elif cur == "preflight":
            pf, perr = read_json(root, mod, "version/preflight.json")
            pref = rel(mod, "version/preflight.json")
            clause("preflight_record", "a preflight record exists for this Design Version",
                   pf is not None and str(pf.get("version")) == str(rec.get("version")), [req_ref, rec_ref],
                   observed="the request moves from preflight; version/preflight.json: %s"
                   % (perr or "for version %s" % pf.get("version")),
                   would_pass="version/preflight.json written by a preflight run for version %s" % rec.get("version"),
                   fix="run the mod's preflight program and write version/preflight.json", cost="rerun",
                   why_sound="Stage 2 is a Python check of the build spec before a token is spent (carried)")
            if pf is not None and str(pf.get("verdict")) != "pass":
                hand.append("steward_confirms")
                clause("steward_confirms", "when the preflight refuses, the steward says the refusals left are "
                       "offline-build work, not a spec fault", bool(steward), [pref, req_ref],
                       observed="preflight verdict %s with %s refusals; steward_confirms: none in the request"
                       % (pf.get("verdict"), pf.get("refusals")),
                       would_pass="--steward-confirms naming each remaining refusal as unbuilt check or behaviour",
                       fix="the Conductor reads the preflight's refusals and passes --steward-confirms, or sends the "
                           "spec back to the Designer", cost="owner",
                       why_sound="no common preflight marks build work apart from spec faults (plan, open question 2)")
        elif cur == "offline_build":
            tt, terr = read_json(root, mod, "version/test_table.json")
            tref = rel(mod, "version/test_table.json")
            lk, lerr = locked_bars(root, mod, v)
            res = (None, lerr) if lerr else _table_runnable(tt, v, lk) if tt is not None else (None, terr)
            bad, n = res
            walk = _walk_deciders(tt, bad) if isinstance(bad, list) else []
            owed = {}
            live_red = {}
            if isinstance(bad, list):
                bad = [x for x in bad if x not in walk]
                live_red = live_known_red_owed(root, tt, bad)
                bad = [x for x in bad if x not in live_red]
                owed = {b: i for b, i in owed_scene_parts(root, mod, tt).items() if b not in bad}
                bad += sorted(owed)
            owed_txt = ("; the table flags these runnable but a deciding scene in scenes.json still owes script parts "
                        "to an open item: %s" % "; ".join("%s (%s)" % (b, ", ".join(i)) for b, i in sorted(owed.items()))
                        ) if owed else ""
            owed_txt += ("; counted runnable, UNRUN and owed to Stage 6 (a live known red with its fix landed): %s"
                         % "; ".join("%s (%s)" % (b, ", ".join("%s: %s %s" % x for x in r))
                                     for b, r in sorted(live_red.items()))) if live_red else ""
            clause("every_bar_has_a_check_that_runs", "every bar has every deciding check runnable "
                   "(an in-game scene may be UNRUN with its command, not with its script parts still owed)",
                   isinstance(bad, list) and not bad,
                   [tref] + ([rel(mod, "scenes.json")] if owed else []),
                   observed=("%d of %d bars not runnable: %s%s" % (len(bad), n, ", ".join(bad), owed_txt))
                   if isinstance(bad, list) else "test_table.json: %s" % n,
                   would_pass="a test table whose every bar reads every_decider_runnable_today true",
                   fix="build the missing checks or scene entries for the listed bars, then remake the test table" + (
                       "; for a scene that owes script parts, work and close the owed item (%s)"
                       % ", ".join(sorted({i for ids in owed.values() for i in ids})) if owed else ""),
                   cost="new instrument",
                   why_sound="the lock rule (his, by agreement 2026-11-14): no mod moves past Stage 3 until every bar "
                             "has a check that runs")
            if walk:
                hand.append("walk_bars_confirmed")
                clause("walk_bars_confirmed", "for a bar his walk decides, the steward says its other deciding checks "
                       "run (the table's flag counts his walk itself)", bool(steward), [tref, req_ref],
                       observed="bars decided in part by his stage-8 look and flagged not runnable: %s; "
                                "steward_confirms: none in the request" % ", ".join(walk),
                       would_pass="--steward-confirms saying each listed bar's scene entry exists and only the look waits",
                       fix="the Conductor reads those bars' deciders in the test table and passes --steward-confirms",
                       cost="owner", why_sound="the table scripts disagree on whether a stage-8 look counts as "
                                               "runnable (plan, open question 3)")
            clause("table_version", "the test table is for this Design Version",
                   tt is not None and str(tt.get("version")) == str(rec.get("version")), [tref],
                   observed="test_table.json version %s" % ((tt or {}).get("version") or terr),
                   would_pass="test_table.json remade with version %s" % rec.get("version"),
                   fix="remake the test table for this Design Version", cost="rerun")
        elif cur in ("blind_challenge", "in_game", "pre_human"):
            hand.append("steward_confirms")
            what = {"blind_challenge": "the blind judge's cycle record (maturation.py next reads its exit block; "
                                       "the exit itself is a proposal)",
                    "in_game": "the visit's in-game record (maturation.py next reads its exit block; the exit "
                               "itself is carried plus a proposal)",
                    "pre_human": "the fresh reader's verdict and the walk brief"}[cur]
            clause("steward_confirms", "the steward has read %s and says the stage's exit is met" % what,
                   bool(steward), [req_ref], observed="steward_confirms: none in the request",
                   would_pass="--steward-confirms naming the run and the verdict read",
                   fix="the Conductor reads the stage's evidence and passes --steward-confirms", cost="owner",
                   why_sound="the stage's exit is not settled as a program check (plan section 3)")
        elif cur == "his_walk":
            hand.append("owner_said")
            oe, owhy = owner_event(root, owner)
            clause("owner_said", "the version passes on his words alone", oe is not None, [req_ref],
                   observed="owner_said: %s" % owhy,
                   would_pass="--owner-said OWNER:<tsn>, his event on the OWNER shard passing the version",
                   fix="his walk ends with his words; pass them verbatim", cost="owner",
                   why_sound="the pass is his alone (carried, spec Stage 8)")
    if forward and to == "blind_challenge" or (back and cur == to == "blind_challenge"):
        visit = (rec.get("cycles") or {}).get("visit", 0) if cur == "blind_challenge" else 0
        if visit >= CYCLE_LIMIT:
            hand.append("conductor_decision")
        clause("fourth_cycle", "after three blind cycles in one visit the Conductor decides; a fourth judge never "
               "starts on its own", visit < CYCLE_LIMIT or bool(conductor), [rec_ref, req_ref],
               observed="cycles visit %d of %d; conductor_decision: none in the request" % (visit, CYCLE_LIMIT),
               would_pass="--conductor-decision saying what the Conductor chose (defer a bar, repair a criterion, "
                          "a design fault, or one more cycle)",
               fix="bring the Conductor the three cycles' findings and pass its decision", cost="owner",
               why_sound="his words of 2026-11-13: after three cycles the Conductor is brought in")
    if forward and cur in ("offline_build", "blind_challenge") or (back and cur == to == "blind_challenge"):
        # PRE_JUDGEMENT_CERTIFICATE (RIMMANDRAKE_CERTIFY_BARS_BEFORE_JUDGE_RED_TEST_WENT_IN): no judge or visit goes in
        # while a program can see a bar's offline decider unregistered, run on another build, or red
        cv = certificate(root, mod, to)
        ref = [r for r in cv["rows"] if r["status"] == "REFUSED"]
        clause("judge_certificate", "every bar's offline deciders are registered, ran on this build and are green "
               "(maturation.py certificate)", cv["ok"], [rel(mod, "version/test_table.json")],
               observed="%s%s" % (JC.summary(cv), "".join("; %s/%s %s: %s" % (r["bar"], r["test"], r["clause"],
                                                                               r["observed"]) for r in ref[:3])),
               would_pass="maturation.py certificate %s --to %s exits 0" % (mod, to),
               fix=JC.first_fix(cv), cost="rerun",
               why_sound="his question of 2026-11-15: no reason to send it in knowing it will fail (spec "
                         "2026-11-15-cheap-guards-at-every-door.md section 4)")
    sha = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True,
                         timeout=60).stdout.strip()
    verdict = {"item": "%s@%s" % (mod, rec.get("version")), "family": "maturation_advance:%s->%s" % (cur, to),
               "sha": sha or UNM, "given": {"criteria": crit, "inputs": inputs}, "passed": passed,
               "refusals": refusals}
    return {"ok": not refusals, "verdict": verdict, "hand_steps": hand, "from": cur, "to": to}


# ---- the move --------------------------------------------------------------------------------------------------------

def ledger_stage_move(root, mod, cur, to, by):
    """A mod that has a ledger keeps its stage equal to the stage record's: one DISPATCH stage.accepted per move (a
    backfill alone left ExplosiveKnockback's ledger at offline_build after it moved to in_game). -> the event id, or
    None for a mod with no ledger."""
    import modledger
    if not os.path.isdir(os.path.join(root, "design", "concepts", mod, "ledger")) and not modledger.read(root, mod):
        return None
    return modledger.append(root, mod, "DISPATCH", "stage.accepted", "stage",
                            body={"from": cur, "to": to, "by": by}, env_writer=None)


def advance(root, mod, to, by, why, steward=None, conductor=None, owner=None, waits_on=None, game_only=None):
    res = evaluate(root, mod, to, steward=steward, conductor=conductor, owner=owner, by=by, why=why, check_by=True,
                   game_only=game_only)
    errs = RC.check(res["verdict"])
    if errs:
        res["malformed"] = errs
        res["ok"] = False
        return res
    if not res["ok"]:
        return res
    rec = load(root, mod)
    cur, t = rec["stage"], now_ts()
    when = pac_heading(t)
    uncounted = None
    if to == "blind_challenge":
        c = rec.setdefault("cycles", {"visit": 0, "total": 0})
        k = c.get("total") or 0
        if cur == "blind_challenge" and k >= 1 and not os.path.isdir(os.path.join(mod_dir(root, mod), BLIND_DIR,
                                                                                  "cycle_%d" % k)):
            # RIMMANDRAKE_SEND_FIXES_TO_NEW_BLIND_JUDGE: the counter counts judge runs; cycle k has no record yet
            uncounted = "cycle %d has no record (no judge ran it), so the cycle counter stays at %d" % (k, k)
        else:
            c["visit"] = c["visit"] + 1 if cur == "blind_challenge" else 1
            c["total"] += 1
    if to == "pre_human":
        rec["pre_human_arrivals"] = rec.get("pre_human_arrivals", 0) + 1
    # the detached or role run that made the move; a move with no unit was made by a hand (maturation_hands.py)
    move = {"from": cur, "to": to, "at": iso(t), "by": by, "why": why, "unit": os.environ.get("RM_ROLE_UNIT") or None,
            "confirmed": {k: v for k, v in (("steward_confirms", steward), ("conductor_decision", conductor),
                                            ("owner_said", owner), ("game_only", ", ".join(game_only or ()))) if v},
            "checks_passed": [p["clause"] for p in res["verdict"]["passed"]]}
    if uncounted:
        move["cycle_not_counted"] = uncounted
        res["cycle_not_counted"] = uncounted
    rec.setdefault("moves", []).append(move)
    rec["stage"], rec["stage_label"], rec["since"], rec["since_from"] = to, label(to), iso(t), "advance by %s" % by
    rec["at_door"] = False
    jtext = read_text(root, mod, "journal.md")
    if jtext is not None:
        jtext, old_stage = replace_bullet(jtext, "Stage now", "- **Stage now:** %s, since %s (`%s`)."
                                          % (LINE[to], when, RECORD))
        jtext, old_wait = replace_bullet(jtext, "Waiting on", "- **Waiting on:** %s" % (
            waits_on or "not yet written for this stage; the steward writes it (the earlier line is in the history "
                        "entry of %s)." % when))
        if conductor:
            jtext = add_intervention(jtext, "- CONDUCTOR INTERVENED (stage %s, %s, kind decision): %s. Source: "
                                            "maturation.py advance by %s, cycle %d." % (
                                                col_of(to), when, conductor.rstrip("."), by, rec["cycles"]["visit"]))
        entry = ["### %s, stage change: %s to %s (by %s)" % (when, label(cur), label(to), by), "",
                 "- Why: %s" % why,
                 "- Checks passed: %s." % ", ".join(move["checks_passed"])]
        for k, v in move["confirmed"].items():
            entry.append("- %s: %s" % (k.replace("_", " ").capitalize(), v))
        if to == "blind_challenge":
            entry.append("- Blind cycle %d of this visit (%d in all)." % (rec["cycles"]["visit"], rec["cycles"]["total"]))
        entry.append("- Was, \"Stage now\": %s" % (old_stage or "none"))
        entry.append("- Was, \"Waiting on\": %s" % (old_wait or "none"))
        entry.append("- Record: `%s`." % RECORD)
        jtext = jtext.rstrip("\n") + "\n\n" + "\n".join(entry) + "\n"
    commit_move(root, mod, rec, jtext)
    ledger_stage_move(root, mod, cur, to, by)
    return res


def _mod_lock(root, mod):
    import fcntl
    os.makedirs(mod_dir(root, mod), exist_ok=True)
    f = open(os.path.join(mod_dir(root, mod), ".stage_move.lock"), "w")
    fcntl.flock(f, fcntl.LOCK_EX)
    return f


def commit_move(root, mod, rec, jtext=None, extra=None):
    """RIMMANDRAKE_WRITE_STAGE_MOVES_ATOMICALLY: one move is one locked write. Under the mod's lock the record is
    written first (a failed record write leaves no journal line), then the journal and any extra {path: text}; a later
    write that fails puts every file already written back as it was and raises."""
    lk = _mod_lock(root, mod)
    try:
        todo = [(RECORD, dump(rec))] + ([("journal.md", jtext)] if jtext is not None else []) + sorted(
            (extra or {}).items())
        done = []
        try:
            for p, text in todo:
                was = read_text(root, mod, p)
                write_text(root, mod, p, text)
                done.append((p, was))
        except Exception:
            for p, was in reversed(done):
                if was is None:
                    try:
                        os.remove(os.path.join(mod_dir(root, mod), p))
                    except OSError:
                        pass
                else:
                    write_text(root, mod, p, was)
            raise
    finally:
        lk.close()


def _semver(v):
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?$", str(v or ""))
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4) is None) if m else None


def _git_show(root, commit, path):
    r = subprocess.run(["git", "-C", root, "show", "%s:%s" % (commit, path)], capture_output=True, text=True, timeout=120)
    if r.returncode:
        return None
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None


LOCK_PINNED = ("tree.json", "sheet.md", "scenes.json", "floor.json", "exam.json", "record.json", "plan.md", "stage.json",
               "coverage_verdict.json")


def _git_blob(root, commit, path):
    r = subprocess.run(["git", "-C", root, "rev-parse", "%s:%s" % (commit, path)], capture_output=True, text=True,
                       timeout=120)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def pin_bars_md(root, mod, v, ids, blob=None):
    """RIMMANDRAKE_PIN_BARS_MD_WHEN_PIPELINE_LOCKS_A_MOD: write version/bars.md, the git blob of each locked file at
    VERSION.json's locked_from_commit, when no bars.md exists (a hand lock wrote one; the pipeline's lock did not, and
    the re-pin rule, the judges' inputs and every preflight's pin check read it). Never rewrites one. -> path or None."""
    if os.path.exists(os.path.join(mod_dir(root, mod), "version", "bars.md")):
        return None
    blob = blob or (lambda c, p: _git_blob(root, c, p))
    c = v.get("locked_from_commit")
    rows = [(f, blob(c, rel(mod, f))) for f in LOCK_PINNED]
    rows = [(f, b) for f, b in rows if b]
    L = ["# %s %s: the bars, locked as they stood on %s" % (mod, v.get("version"), v.get("locked_on") or "UNMEASURED"),
         "", "Locked by %s (%s). Nothing here edits a bar: this file points at the bars and pins their bytes. State: %s."
         % (v.get("locked_by") or "UNMEASURED", v.get("per_ruling") or v.get("why") or "no ruling recorded",
            v.get("state")), "",
         "Lock commit: `%s`. Written by `maturation.py lock-bars` with the first record of the locked bars." % c, "",
         "## The locked files", "", "| file | git blob at the lock commit | role |", "|---|---|---|"]
    L += ["| `%s` | `%s` | locked input |" % (rel(mod, f), b) for f, b in rows]
    L += ["", "## Counts at the lock", "", "- Bars: **%d**, the ids in `locked_bars.json`." % len(ids),
          "- A locked file changed after the lock ONLY in test text, check wording or bookkeeping fields is re-pinned "
          "here with a journal line; a changed bar is his card (re-pin rule, 2026-11-14).", ""]
    write_text(root, mod, "version/bars.md", "\n".join(L))
    return rel(mod, "version/bars.md")


def lock_bars(root, mod, by, why, add=(), remove=(), source=None, show=None, blob=None):
    """RIMMANDRAKE_DERIVE_CHECKS_FROM_LOCKED_BARS: record the locked version's bar ids in version/locked_bars.json, the
    list the test table is compared with. The first record derives them from the lock itself: coverage_judge's
    required_ids (record.json inventory, then tree.json leaves) at VERSION.json's locked_from_commit, less
    bars_moved_to_next_version, plus bars_added_after_lock. Any --add/--remove (a bar his card added or moved) cites his
    event, OWNER:<tsn>; an agent never changes a bar on its own word. -> {"ok", "why", "ids"}."""
    import concept_tree as CT
    show = show or (lambda c, p: _git_show(root, c, p))
    v, verr = read_json(root, mod, "version/VERSION.json")
    if not isinstance(v, dict):
        return {"ok": False, "why": "version/VERSION.json: %s" % verr}
    if not str(v.get("state") or "").startswith("locked"):
        return {"ok": False, "why": "VERSION.json state is %r: the bars are recorded at Lock" % v.get("state")}
    add, remove = [x for x in add if x], [x for x in remove if x]
    if add or remove:
        m = re.match(r"^OWNER:(\d+)$", str(source or "").strip())
        ev = CT.owner_events(root, REPO).get(m.group(1)) if m else None
        if not isinstance(ev, dict) or not str(ev.get("ownerSaid") or ev.get("byCard") or "").strip():
            return {"ok": False, "why": "--source %r is not one of his OWNER events with his words: a bar is added or "
                    "removed only on his card" % source}
    cur, _ = read_json(root, mod, LOCKED_BARS)
    hist = list(cur.get("history") or []) if isinstance(cur, dict) else []
    if isinstance(cur, dict) and cur.get("version") == v.get("version") and isinstance(cur.get("ids"), list):
        ids, how = list(cur["ids"]), "changed by his card"
        if not add and not remove:
            return {"ok": False, "why": "%s already records %d bars for %s; a change needs --add/--remove with --source "
                    "OWNER:<tsn>" % (LOCKED_BARS, len(ids), v.get("version"))}
    else:
        c = v.get("locked_from_commit")
        if not c:
            return {"ok": False, "why": "VERSION.json has no locked_from_commit to derive the locked bars from"}
        rec, tree = show(c, rel(mod, "record.json")), show(c, rel(mod, "tree.json"))
        if not isinstance(tree, dict):
            return {"ok": False, "why": "tree.json at %s cannot be read" % c}
        rows = ((rec or {}).get("inventory") or [] if isinstance(rec, dict) else []) + (tree.get("leaves") or [])
        ids = list(dict.fromkeys(x["id"] for x in rows if isinstance(x, dict) and isinstance(x.get("id"), str)))
        moved = [x for x in v.get("bars_moved_to_next_version") or [] if isinstance(x, str)]
        later = [x for x in v.get("bars_added_after_lock") or [] if isinstance(x, str)]
        how = ("required_ids at locked_from_commit %s (%d), less bars_moved_to_next_version (%d), plus "
               "bars_added_after_lock (%d)" % (c, len(ids), len(moved), len(later)))
        ids = [i for i in ids if i not in moved] + [a for a in later if a not in ids]
    gone = [r for r in remove if r not in ids]
    if gone:
        return {"ok": False, "why": "--remove %s: not a locked bar" % ", ".join(gone)}
    ids = [i for i in ids if i not in remove] + [a for a in add if a not in ids]
    hist.append({"at": dt.datetime.fromtimestamp(now_ts(), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "by": by, "why": why, "how": how, "source": source, "added": add, "removed": remove,
                 "count": len(ids)})
    out = {"schema": 1, "mod": mod, "version": v.get("version"), "locked_from_commit": v.get("locked_from_commit"),
           "ids": ids, "history": hist}
    write_text(root, mod, LOCKED_BARS, json.dumps(out, indent=1) + "\n")
    if not (isinstance(cur, dict) and cur.get("version") == v.get("version") and isinstance(cur.get("ids"), list)):
        pin_bars_md(root, mod, v, ids, blob)
    return {"ok": True, "why": how, "ids": ids}


def next_version(root, mod, by, why):
    """RIMMANDRAKE_WRITE_STAGE_MOVES_ATOMICALLY: open the record of the version VERSION.json now names. Allowed when the
    record's version has passed, or VERSION.json names a newer version (the Designer opened it; locked or not). The old
    record is kept as version/stage_record_<version>.json; the new one starts at the Designer, or at preflight when
    VERSION.json is already locked (Stage 1's exit). -> {"ok", "why", "from", "to", "stage"}."""
    rec = load(root, mod)
    if rec is None:
        return {"ok": False, "why": "%s has no stage record; seed it first" % mod}
    v, verr = read_json(root, mod, "version/VERSION.json")
    if not isinstance(v, dict):
        return {"ok": False, "why": "version/VERSION.json: %s" % verr}
    old, new = rec.get("version"), v.get("version")
    a, b = _semver(old), _semver(new)
    if b is None:
        return {"ok": False, "why": "VERSION.json names no semantic version (%r)" % new}
    if a is not None and b <= a:
        return {"ok": False, "why": "VERSION.json says %s, not newer than the record's %s: the Designer opens the next "
                "version in VERSION.json first" % (new, old)}
    if rec.get("stage") != "passed" and a is not None and b[:3] == a[:3]:
        return {"ok": False, "why": "the record's %s has not passed" % old}
    if not CT_txt(why):
        return {"ok": False, "why": "a version move says why"}
    t = now_ts()
    stage = "preflight" if str(v.get("state", "")).startswith("locked") else "designer"
    keep = "version/stage_record_%s.json" % re.sub(r"[^0-9A-Za-z.-]", "_", str(old))
    nrec = {"schema": 1, "mod": mod, "version": new, "stage": stage, "stage_label": label(stage), "since": iso(t),
            "since_from": "next-version by %s" % by, "at_door": False,
            "seeded": {"at": iso(t), "by": "maturation.py next-version", "from_version": old, "previous": keep},
            "cycles": {"visit": 0, "total": 0}, "pre_human_arrivals": 0, "spend": [],
            "moves": [{"from": "%s at %s" % (old, rec.get("stage")), "to": stage, "at": iso(t), "by": by, "why": why,
                       "version_from": old, "version_to": new}]}
    jtext = read_text(root, mod, "journal.md")
    if jtext is not None:
        when = pac_heading(t)
        jtext, was = replace_bullet(jtext, "Stage now", "- **Stage now:** %s, since %s (`%s`)." % (LINE[stage], when,
                                                                                                    RECORD))
        jtext = jtext.rstrip("\n") + "\n\n" + "\n".join([
            "### %s, version change: %s to %s (by %s)" % (when, old, new, by), "", "- Why: %s" % why,
            "- The %s record (at %s) is kept as `%s`." % (old, label(rec.get("stage")), keep),
            "- Was, \"Stage now\": %s" % (was or "none"), "- Record: `%s`." % RECORD]) + "\n"
    commit_move(root, mod, nrec, jtext, extra={keep: dump(rec)})
    return {"ok": True, "why": why, "from": old, "to": new, "stage": stage, "kept": rel(mod, keep)}


def CT_txt(x):
    return isinstance(x, str) and bool(x.strip())


# ---- spend -----------------------------------------------------------------------------------------------------------

def add_spend(root, mod, stage, tokens, usd=None, wall_s=None, source=None, estimate=False):
    if stage not in WORDS:
        raise ValueError("no stage %r; stages are %s" % (stage, ", ".join(WORDS)))
    rec = load(root, mod)
    if rec is None:
        raise ValueError("%s has no stage record; run seed first" % mod)
    rec.setdefault("spend", []).append({
        "stage": stage, "stages": [stage], "tokens": tokens if isinstance(tokens, int) else UNM,
        "usd": usd if isinstance(usd, (int, float)) else UNM, "wall_s": wall_s if isinstance(wall_s, (int, float))
        else UNM, "source": source or UNM, "kind": "estimate" if estimate else "measured", "at": iso(now_ts())})
    write_text(root, mod, RECORD, dump(rec))
    return rec


RUN_SPEND = "version/run_spend.jsonl"


def _unit_of(row):
    u = row.get("unit")
    if u:
        return str(u)
    m = re.match(r"detached run (\S+)", str(row.get("source") or ""))
    return m.group(1) if m else None


def read_run_spend(root, mod):
    """-> the spend rows the Dispatch step wrote for ended runs (RUN_SPEND, one JSON object a line; a bad line skipped)."""
    out = []
    for line in (read_text(root, mod, RUN_SPEND) or "").splitlines():
        try:
            x = json.loads(line)
        except ValueError:
            continue
        if isinstance(x, dict):
            out.append(x)
    return out


def spend_rows(root, mod, rec):
    """-> the record's spend entries plus the Dispatch step's run rows for units the record does not already hold."""
    rows = list((rec or {}).get("spend") or [])
    have = {_unit_of(x) for x in rows} - {None}
    for x in read_run_spend(root, mod):
        u = _unit_of(x)
        if u and u not in have:
            have.add(u)
            rows.append(x)
    return rows


def record_run_spend(root, mod, runs, stage_of):
    """RIMMANDRAKE_RESERVE_CAP_BEFORE_LAUNCH: write one spend row per ENDED run on this mod that neither the record nor
    RUN_SPEND holds yet (the blind and in-game stages had none: one blind reconcile measured 3,013,781 tokens and was
    never recorded). runs: maturation_now run views; stage_of(run) -> its stage words, [] to skip. RUN_SPEND has one
    writer (the Dispatch step), so landing it never overwrites a steward's record. -> the rows written."""
    rec = load(root, mod)
    if rec is None:
        return []
    have = {_unit_of(x) for x in spend_rows(root, mod, rec)} - {None}
    new = []
    for r in runs or []:
        u = r.get("unit")
        if not u or u in have or r.get("live") or not isinstance(r.get("end"), (int, float)):
            continue
        stages = stage_of(r)
        if not stages:
            continue
        have.add(u)
        new.append(dict(_spend_row(r, stages), at=iso(r["end"])))
    if new:
        text = read_text(root, mod, RUN_SPEND) or ""
        if text and not text.endswith("\n"):
            text += "\n"
        write_text(root, mod, RUN_SPEND, text + "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in new))
    return new


def spend_by_stage(rec):
    """-> {stage: {tokens, usd, wall_s, entries, estimates, unmeasured}}. A run that worked in several stages is
    counted once, under the joined key ("designer+preflight"), never split by a guess. usd is UNMEASURED when no
    entry of that stage measured it."""
    out = {}
    for s in rec.get("spend") or []:
        key = "+".join(s.get("stages") or [s.get("stage")])
        t = out.setdefault(key, {"tokens": 0, "usd": 0.0, "wall_s": 0, "entries": 0, "estimates": 0,
                                 "unmeasured": 0, "usd_known": 0})
        if isinstance(s.get("usd"), (int, float)):
            t["usd_known"] += 1
        t["entries"] += 1
        if s.get("kind") == "estimate":
            t["estimates"] += 1
        for k in ("tokens", "usd", "wall_s"):
            if isinstance(s.get(k), (int, float)):
                t[k] += s[k]
            else:
                t["unmeasured"] += 1
    for t in out.values():
        if not t.pop("usd_known"):
            t["usd"] = UNM
    return out


# ---- next ------------------------------------------------------------------------------------------------------------

DISPATCH_READING_MAX_AGE_S = 1800   # ops_watch's MATURATION_READING_MAX_AGE_S: the tick runs every 60 s; 30 missed is dead


def dispatch_reading():
    """-> (the Dispatch tick's last reading, or None; its path). maturation_dispatch.sdir(), imported late (it imports us)."""
    import maturation_dispatch as MD
    p = os.path.join(MD.sdir(), "reading.json")
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f), p
    except (OSError, ValueError):
        return None, p


def dispatch_overlay(mod, nxt, rd, path, now):
    """-> {"line", "next"}: what the Dispatch tick's own reading says of MOD, and the NEXT line to print. Item
    RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS: next_step reads the stage record alone, so it printed
    "automatic: the Dispatch tick launches it" for six hours while the tick had paused the mod at the ceiling. An
    "automatic" claim is the tick's: a paused or held decision replaces it with the tick's why (its release command
    included), a stale, unreadable or silent reading makes it UNMEASURED; a waiting decision keeps it."""
    auto = nxt.startswith("NEXT (automatic")
    rest = nxt.split("): ", 1)[1] if "): " in nxt else nxt
    if not isinstance(rd, dict):
        why = "no readable Dispatch tick reading at %s" % path
        return {"line": "  dispatch tick: %s" % why, "decision": UNM,
                "next": "NEXT (UNMEASURED whether the Dispatch tick launches it: %s): %s" % (why, rest) if auto else nxt}
    try:
        age = now - float(rd.get("at"))
    except (TypeError, ValueError):
        age = None
    if age is None or age > DISPATCH_READING_MAX_AGE_S:
        why = ("the Dispatch tick's reading is %d min old (the step is not ticking)" % (age / 60) if age is not None
               else "the Dispatch tick's reading has no time")
        return {"line": "  dispatch tick: %s" % why, "decision": UNM,
                "next": "NEXT (UNMEASURED whether the Dispatch tick launches it: %s): %s" % (why, rest) if auto else nxt}
    row = (rd.get("mods") or {}).get(mod)
    at = rd.get("at_pac", UNM)
    if not isinstance(row, dict):
        why = "%s is not on the Dispatch tick's list at %s (maturation_dispatch.json advancing): nothing launches it" % (mod, at)
        return {"line": "  dispatch tick: %s" % why, "decision": None,
                "next": "NEXT (a hand step: %s): %s" % (why, rest) if auto else nxt}
    dec, klass, why = row.get("decision", UNM), row.get("klass"), row.get("why") or row.get("status") or ""
    since = (" for %s min" % row["for_min"]) if isinstance(row.get("for_min"), int) else ""
    out = {"line": "  dispatch tick (%s): %s (%s)%s: %s" % (at, dec, klass, since, why), "decision": dec, "klass": klass,
           "why": why, "for_min": row.get("for_min"), "at_pac": at, "next": nxt}
    if auto and klass in ("paused", "held"):
        out["next"] = "NEXT (%s by the Dispatch tick: %s%s, at %s): %s; the record's step, once it launches: %s" % (
            "PAUSED" if klass == "paused" else "HELD", dec, since, at, why, rest)
    return out


def next_step(root, mod):
    rec = load(root, mod)
    if rec is None:
        return {"mod": mod, "stage": UNM, "next": "NEXT (automatic: the Dispatch tick seeds a Designer concept's record): maturation.py seed %s" % mod, "refusals": []}
    cur = rec["stage"]
    if cur == "passed":
        return {"mod": mod, "stage": cur, "refusals": [], "hand_steps": [],
                "next": "NEXT (OWNER, a card in the Conductor log): decide with him whether to open the next version (spec §3.8, a portfolio "
                        "decision); nothing here opens one"}
    to = WORDS[WORDS.index(cur) + 1]
    res = evaluate(root, mod, to, by="next", why="what is the next step")
    prog = [r for r in res["verdict"]["refusals"] if r["clause"] not in res["hand_steps"]]
    hand = [r for r in res["verdict"]["refusals"] if r["clause"] in res["hand_steps"]]
    blind = blind_facts(root, mod) if cur == "blind_challenge" else None
    ing = ingame_facts(root, mod) if cur == "in_game" else None
    if ing and ing.get("owed") == "blocked":
        nxt = "NEXT (PAUSED, OPS_MATURATION_MOD_PAUSED): in-game acceptance is blocked: %s" % "; ".join(ing["blocked"])
    elif ing and ing.get("owed") == "run":
        nxt = ("NEXT (automatic: the Dispatch tick launches it when the game is free, queued fairly): in-game visit %d (maturation.py launch %s --budget-usd <cap> --item "
               "RIMMANDRAKE_DRIVE_%s_IN_GAME_ACCEPTANCE_VISIT_<N as a word: ONE>, filed first; or the Dispatch step); its record goes "
               "in %s" % (ing["visit"], mod, mod.upper(), ing["exit"]["record"]))
    elif ing and ing.get("owed") == "no exit block":
        nxt = ("NEXT (wait on its live run, else PAUSED): visit %d is recorded without an exit block: its run writes one, "
               "or (nothing live) the mod is PAUSED until someone reads %s/SUMMARY.md" % (ing["visit"], ing["exit"]["record"]))
    elif ing and ing.get("owed") == "exit met":
        nxt = ("NEXT (automatic: one steward run): visit %d: exit met (a program's reading of its record: %s); the steward reads "
               "%s/SUMMARY.md and confirms: maturation.py advance %s --to pre_human --by <SEAT> --why \"...\" "
               "--steward-confirms \"...\"" % (ing["visit"], ing["exit"]["why"][0], ing["exit"]["record"], mod))
    elif ing:
        nxt = ("NEXT (automatic: one steward run, then a fixer per item): visit %d: exit not met (%s); the steward reads "
               "%s/SUMMARY.md, files each failed line as a named item and sends the mod down its road back (maturation.py "
               "advance %s --to offline_build or --to blind_challenge); the next visit launches when they close" % (
                   ing["visit"], "; ".join(ing["exit"]["why"][:3]), ing["exit"]["record"], mod))
    elif blind and blind.get("owed") == "blocked":
        nxt = "NEXT (PAUSED, OPS_MATURATION_MOD_PAUSED): the blind challenge is blocked: %s" % "; ".join(blind["blocked"])
    elif blind and blind.get("owed") == "cycle":
        nxt = ("NEXT (automatic: the Dispatch tick launches it): blind cycle %d (maturation.py launch %s --budget-usd <cap> --item <ID>, or the Dispatch "
               "step); its record goes in %s" % (blind["cycle"], mod, blind["exit"]["record"]))
    elif blind and blind.get("owed") == "no exit block":
        nxt = ("NEXT (wait on its live run, else PAUSED): cycle %d is recorded without an exit block: its run writes one, "
               "or (nothing live) the mod is PAUSED until someone reads %s/SUMMARY.md" % (blind["cycle"], blind["exit"]["record"]))
    elif blind and blind.get("owed") == "exit met":
        nxt = ("NEXT (automatic: one steward run): cycle %d: exit met (a program's reading of its record: %s); the steward reads "
               "%s/SUMMARY.md and confirms: maturation.py advance %s --to in_game --by <SEAT> --why \"...\" "
               "--steward-confirms \"...\"" % (blind["cycle"], blind["exit"]["why"][0], blind["exit"]["record"], mod))
    elif blind:
        nxt = ("NEXT (%s): cycle %d: exit not met (%s); the steward reads %s/SUMMARY.md, files the failures as named "
               "items and opens the next blind cycle (maturation.py advance %s --to blind_challenge%s) or another road" % (
                   "PAUSED: three cycles, the Conductor decides" if (blind.get("visit") or 0) >= CYCLE_LIMIT else
                   "automatic: one steward run", blind["cycle"], "; ".join(blind["exit"]["why"][:3]), blind["exit"]["record"], mod,
                   " --conductor-decision \"...\": three cycles in this visit" if (blind.get("visit") or 0) >= CYCLE_LIMIT
                   else ""))
    elif prog:
        tag = ("OWNER or the Designer's own launcher: maturation_dispatch.py status says which" if cur in (
                   "intake", "designer") else
               "automatic: the Dispatch tick launches a capped builder" if prog[0]["clause"] in BUILD_CLAUSES else
               "automatic: one steward run" if cur in ("preflight", "pre_human") else
               "PAUSED, OPS_MATURATION_MOD_PAUSED: %s refuses it" % prog[0]["clause"])
        nxt = "NEXT (%s): %s; then maturation.py advance %s --to %s (%s refuses it now: %s)" % (
            tag, prog[0]["smallest_fix"]["what"], mod, to, prog[0]["clause"], prog[0]["observed"])
    elif hand:
        flag = {"steward_confirms": "--steward-confirms", "walk_bars_confirmed": "--steward-confirms",
                "owner_said": "--owner-said",
                "conductor_decision": "--conductor-decision"}
        nxt = "NEXT (%s): %s; then maturation.py advance %s --to %s --by <SEAT> --why \"...\" %s \"...\"" % (
            "OWNER, a card in the Conductor log" if hand[0]["clause"] == "owner_said" else
            "PAUSED: three cycles, the Conductor decides" if hand[0]["clause"] == "conductor_decision" else
            "automatic: one steward run", hand[0]["smallest_fix"]["what"], mod, to, flag.get(hand[0]["clause"], ""))
    else:
        nxt = ("NEXT (automatic: one steward run advances it): maturation.py advance %s --to %s --by <SEAT> --why \"...\" "
               "(every exit test passes)" % (mod, to))
    return {"mod": mod, "version": rec.get("version"), "stage": cur, "stage_label": label(cur),
            "since": rec.get("since"), "to": to, "passed": [p["clause"] for p in res["verdict"]["passed"]],
            "refusals": [{k: r[k] for k in ("clause", "observed", "would_pass", "smallest_fix")} for r in prog + hand],
            "hand_steps": res["hand_steps"], "cycles": rec.get("cycles"),
            "spend": spend_by_stage({"spend": spend_rows(root, mod, rec)}),
            "launch": ("maturation.py launch %s --budget-usd <cap> --item <ID> (or the Dispatch step, "
                       "maturation_dispatch.py)" % mod) if cur == "offline_build" and prog else
            ("maturation.py launch %s --budget-usd <cap> --item <ID> (blind cycle %d; or the Dispatch step, "
             "maturation_dispatch.py)" % (mod, blind["cycle"])) if blind and blind.get("owed") == "cycle" else
            ("none: blind cycle %d is %s" % (blind["cycle"], blind.get("owed"))) if blind else
            ("maturation.py launch %s --budget-usd <cap> --item <ID naming IN_GAME_ACCEPTANCE> (in-game visit %d, "
             "a live driver, opus; refused "
             "while the bridge is held; or the Dispatch step, maturation_dispatch.py, when ingame_enabled)" % (
                 mod, ing["visit"])) if ing and ing.get("owed") == "run" else
            ("none: in-game visit %s is %s" % (ing.get("visit"), ing.get("owed"))) if ing else "none at this stage",
            "blind": blind, "ingame": ing, "next": nxt}


# ---- slice 4: the offline-build brief and its capped launch ---------------------------------------------------------
#
# The owner, 2026-11-14 ~9 PM PST, at the keyboard: "So can we wire up Operations/Dispatch such that they do advance on
# these offline builders? ... As long as we don't have automated loops rejecting/cycling things, we can't get into too
# much trouble." So a blank "Steward's decisions" section no longer refuses an offline-build launch: the brief carries
# the standing default below, and the Conductor's decisions, when written, go in version/steward_decisions.md.

OWNER_WIRE = ("So can we wire up Operations/Dispatch such that they do advance on these offline builders? This was pretty "
              "inefficient and pointlessly it seems, if I'm reading correctly. As long as we don't have automated loops "
              "rejecting/cycling things, we can't get into too much trouble.")
# The owner's self-fixing ruling (2026-11-15, item RIMMANDRAKE_HARDEN_PIPELINE_WHERE_HANDS_CLEANED_UP): the one line every
# brief this pipeline launches carries (builder, blind judge, in-game driver here; steward and fixer in
# maturation_autonomy). Written once; the full text lives in standing_rulings.md. selftest_self_fix_rule.py.
SELF_FIX_RULE = ("- The pipeline fixes its own defects (owner, 2026-11-15): a defect you find in the pipeline itself (its "
                 "code, tools, records, tests, status page) with a clear cause and a known fix is yours: file it (its "
                 "acceptance test in the body), fix it in this run, tests first, publish, and name the ticket and sha in "
                 "your report. Hand it off only when the fix is unknown, outside your tools, or would change a "
                 "north-star bar, with the evidence and what you tried on the ticket. Never work around it by hand. A "
                 "mod's own gaps still go through the stages. Full text: `design/RimMandrake/standing_rulings.md` "
                 "§The pipeline fixes its own defects.")
# The night of 2026-11-14 three judges' records read "not met" for format alone (a missing file, a key spelled another
# way, a placeholder command) and each cost a reconcile run (one measured 3.0M tokens). The run that wrote the record
# reads it with the pipeline's own reader before it stops. In the blind judge's and the in-game driver's briefs.
SELF_CHECK_RULE = ("**Before you stop, read your own record the way the pipeline will:** run `python3 "
                   "src/RimMandrake/rimflow/maturation.py next %s` and read every reason it gives. A reason about "
                   "FORM (a missing file, a key it cannot find, a row with no command, a placeholder, a result saved in "
                   "the wrong folder) is yours to repair now: fix the record's format, never a verdict, a row's "
                   "result or a bar, and rerun it. A reason about SUBSTANCE (a FAIL, an open Problem, an UNMEASURED "
                   "row) stays exactly as it is. Paste the reader's last lines into your report.")
STEWARD_FILE = "version/steward_decisions.md"
STANDING_DEFAULT = ("No Conductor decisions are written for this run, so the standing default holds: build the missing "
                    "checks for the bars listed above, offline, and nothing else. Do not change a bar, its wording, the "
                    "Design Version or the stage. A bar that cannot get a check offline is written up in a note on your "
                    "item as a question to the Conductor, never guessed around.")
BUILD_CLAUSES = ("every_bar_has_a_check_that_runs", "table_version")    # refusals a builder can work off, offline


def build_facts(root, mod):
    """-> what the offline-build stage owes, read through evaluate(): refused_bars (not runnable, his-walk bars left
    out: those are a hand step), build_refusals, hand_steps, other_refusals (a hold, a version mismatch: not build
    work), and owed: "build" | "hand step" | "blocked" | "ready to advance". Any other stage: stage only."""
    rec = load(root, mod)
    if rec is None:
        return {"mod": mod, "stage": UNM, "why": "no stage record"}
    cur = rec["stage"]
    out = {"mod": mod, "version": rec.get("version"), "stage": cur, "since": rec.get("since")}
    if cur != "offline_build":
        return out
    res = evaluate(root, mod, "blind_challenge", by="maturation.py brief", why="what the offline build owes")
    refs = res["verdict"]["refusals"]
    tt, _ = read_json(root, mod, "version/test_table.json")
    v, _ = read_json(root, mod, "version/VERSION.json")
    lk, lerr = locked_bars(root, mod, v)
    bad, n = (None, lerr) if lerr else _table_runnable(tt, v, lk) if tt is not None else (None, None)
    if bad is None and n:
        out["table_error"] = n
    out["bar_fp"] = bar_fingerprints(tt)
    walk = _walk_deciders(tt, bad) if isinstance(bad, list) else []
    live_red = live_known_red_owed(root, tt, [b for b in bad if b not in walk]) if isinstance(bad, list) else {}
    out.update({
        "refused_bars": [b for b in bad if b not in walk and b not in live_red] if isinstance(bad, list) else UNM,
        "live_red_owed": sorted(live_red),
        "bars_total": n if isinstance(n, int) else UNM, "walk_bars": walk,
        "build_refusals": [r["clause"] for r in refs if r["clause"] in BUILD_CLAUSES],
        "hand_steps": [r["clause"] for r in refs if r["clause"] in res["hand_steps"]],
        "other_refusals": [r["clause"] for r in refs if r["clause"] not in BUILD_CLAUSES
                           and r["clause"] not in res["hand_steps"] and r["clause"] != "judge_certificate"],
        "observed": {r["clause"]: r["observed"] for r in refs}})
    cert = [r for r in refs if r["clause"] == "judge_certificate"]
    if cert:    # PRE_JUDGEMENT_CERTIFICATE: its own wait, with its path to pass (a stale build is one command away)
        out["certificate_why"] = cert[0]["observed"]
        out["certificate_fix"] = cert[0]["smallest_fix"]["what"]
    out["owed"] = ("blocked" if out["other_refusals"] else "build" if out["build_refusals"] else
                   "certificate" if cert else "hand step" if out["hand_steps"] else "ready to advance")
    return out


def refused_ids(f):
    """The refusals a builder can work off, as one comparable list (None when the table cannot be read)."""
    if not isinstance(f.get("refused_bars"), list):
        return None
    return sorted(f["refused_bars"]) + (["table_version"] if "table_version" in f.get("build_refusals", []) else [])


def _bar_lines(tt, ids):
    tests = (tt or {}).get("tests") or {}
    out = []
    for b in (tt or {}).get("bars") or []:
        if not isinstance(b, dict) or b.get("id") not in ids:
            continue
        out.append("- **%s** (%s, proves at stage %s)" % (b["id"], b.get("kind", "?"), b.get("proves_at", "?")))
        for d in b.get("decides") or []:
            t = tests.get(d) or {}
            r = t.get("runs_today")
            # the table's own runnable rule (make_table.py): ran today, or an in-game entry written and recorded UNRUN
            if r is True or (isinstance(r, dict) and (r.get("ran") or r.get("entry_exists"))):
                continue
            out.append("  - decider `%s` (%s, stage %s) does not run today: %s" % (
                d, t.get("kind", "no entry in the table"), t.get("stage", "?"),
                ("command `%s`" % t["command"]) if t.get("command") else "no command written"))
    return out


def brief_text(root, mod, cap_usd=None, bars=None):
    """-> (the mechanical half of an offline-build brief, build_facts). Never refuses for a blank steward section.
    A mod at the blind challenge gets blind_brief_text instead, one at in-game acceptance ingame_brief_text. bars: this
    run's batch of the refused bars (the Dispatch step's split, RIMMANDRAKE_SIZE_DISPATCH_BUILDS_THIRTY_THREE_BARS_ONE_RUN);
    only those are listed as the run's work, the rest named as later runs'."""
    stage = (load(root, mod) or {}).get("stage")
    if stage == "blind_challenge":
        return blind_brief_text(root, mod, cap_usd)
    if stage == "in_game":
        return ingame_brief_text(root, mod, cap_usd)
    f = build_facts(root, mod)
    tt, _ = read_json(root, mod, "version/test_table.json")
    jtext = read_text(root, mod, "journal.md") or ""
    when = pac_heading(now_ts())
    L = ["# Offline build (Stage 3): %s %s" % (mod, f.get("version", UNM)), "",
         "Written by `maturation.py brief %s` at %s: the mechanical half (plan "
         "design/plans/2026-11-14-maturation-pipeline-build.md, slice 4; spec §4 Stage 3)." % (mod, when), "",
         "The owner, 2026-11-14 ~9 PM PST: \"%s\"" % OWNER_WIRE, "",
         "## What the exit tests refuse now", ""]
    for k, v in sorted((f.get("observed") or {}).items()):
        L.append("- `%s`: %s" % (k, v))
    if not f.get("observed"):
        L.append("- nothing (stage %s, owed: %s)" % (f.get("stage"), f.get("owed", UNM)))
    ids = f.get("refused_bars") if isinstance(f.get("refused_bars"), list) else []
    mine = [b for b in ids if b in set(bars)] if bars else list(ids)
    if len(mine) < len(ids):
        L += ["", "## Bars with a deciding check that does not run (this run's batch: %d of the %d refused; %s bars in "
              "the table)" % (len(mine), len(ids), f.get("bars_total", UNM)), ""]
        L += _bar_lines(tt, set(mine)) or ["- none"]
        L += ["", "Left for later runs, not yours (the Dispatch step launches the next batch once this run ends and "
              "has resolved at least one refused bar): %s." % ", ".join("`%s`" % b for b in ids if b not in mine)]
    else:
        L += ["", "## Bars with a deciding check that does not run (%d of %s)" % (len(ids), f.get("bars_total", UNM)), ""]
        L += _bar_lines(tt, set(ids)) or ["- none"]
    if f.get("walk_bars"):
        L += ["", "Bars his Stage 8 walk helps decide (a hand step for the Conductor, not yours): %s."
              % ", ".join(f["walk_bars"])]
    live = sorted(k for k, t in ((tt or {}).get("tests") or {}).items()
                  if isinstance(t, dict) and str(t.get("kind", "")).startswith("live"))
    L += ["", "## In-game checks (UNRUN until Stage 6): %d in the table" % len(live), "",
          "Each in-game check you write is listed UNRUN with its exact command; you never run one (no game, no bridge)."]
    L += ["", "## The journal says", ""]
    for field in ("Waiting on", "Next"):
        span = _bullet(jtext, field)
        L.append(" ".join(x.strip() for x in jtext.split("\n")[span[0]:span[1]]) if span else "- %s: (no line)" % field)
    steward = (read_text(root, mod, STEWARD_FILE) or "").strip()
    L += ["", "## Steward's decisions", "", steward or STANDING_DEFAULT]
    L += ["", "## Standing rules for this build", "",
          "- Offline only: no bridge, no game, no deploy, no ModsConfig change. Whittle and Relentless stay off.",
          "- The test is built with the item (owner, 2026-11-13): each missing check is watched failing where the "
          "behaviour is missing, then passing; an in-game check is written with its exact command and recorded UNRUN.",
          "- Remake `design/concepts/%s/version/test_table.json` with the table's own maker (its `made_by` names it) "
          "and run `python3 src/RimMandrake/rimflow/maturation.py next %s`; say the count of bars not runnable "
          "before (%d) and after in your last note." % (mod, mod, len(ids)),
          "- Never run `maturation.py advance`, never judge or send the mod back: the Conductor moves stages.",
          "- One dated line in the journal's history for what you built. Every file you touch stays DIRTY until "
          "`code_review_status.py check` says CLEAN.",
          "- Never guess a defName, field or namespace (RimSage, the def, or `measure`).",
          SELF_FIX_RULE]
    return "\n".join(L) + "\n", f


def detached_helper_path():
    return os.environ.get("MATURATION_DETACHED_HELPER") or os.path.join(HERE, "detached_helper.py")


def brief_dir():
    d = os.environ.get("MATURATION_BRIEF_DIR")
    if not d:
        import doorbell
        d = os.path.join(doorbell.state_dir(), "maturation", "briefs")
    os.makedirs(d, exist_ok=True)
    return d


def resume_text(f, unit):
    """The section a relaunch after a KILLED run puts at the top of its brief (RIMMANDRAKE_RETRY_RUN_KILLED_BY_ACCOUNT_SWITCH_
    CYCLE_KEPT): the same cycle or visit, begun by a run killed from outside before it finished."""
    blind = f.get("stage") == "blind_challenge"
    what = "cycle %s" % f.get("cycle") if blind else "visit %s" % f.get("visit")
    rec = (f.get("exit") or {}).get("record") or "its record folder"
    return ["## Resume: this %s was begun by a run that was killed" % what.split()[0], "",
            "Run `%s` worked on %s and was killed from outside before it finished (an account switch stops every Claude "
            "process; it wrote no result). This is the SAME %s, not a new one. What it committed and published stands; "
            "nothing it did not commit exists." % (unit, what, what), "",
            "- If `%s` exists on origin/main, read its SUMMARY.md and the files beside it first, then continue from the "
            "first step not recorded there. Do not redo a recorded step%s." % (
                rec, " (a recorded lane 1 stays as it is: you are past the blind part, so the blind list below no "
                     "longer binds you)" if blind else ""),
            "- If it holds nothing recorded, do the whole %s as written below." % what, ""]


def resumed_text(mod, session):
    """The opening of a resumed holder's brief (spec §3.4, Option B): the ledger, not its memory, is the truth."""
    return ("**You are %s's holder, resumed (session %s).** Your conversation so far is yours, but the ledger wins any "
            "disagreement with it: re-read `python3 src/RimMandrake/rimflow/modledger.py packet --mod %s` before you "
            "act; never chase a cause it lists as refuted, never re-ask a question it lists as answered. The stage's "
            "instructions follow.\n" % (mod, session, mod))


def reconcile_text(mod, why):
    """The reconcile step a killed or lost holder run owes before anything resumes (spec §3.4, Option B)."""
    return ("**Reconcile first: %s.** Before any other work: (1) in this clone, `git status` and `git log "
            "origin/main..HEAD`; publish what the ledger and tests support, else drop it, and say which in a `note`; "
            "(2) `python3 src/RimMandrake/rimflow/cli.py bridge who`: release a hold your earlier run left; (3) re-read "
            "`python3 src/RimMandrake/rimflow/modledger.py packet --mod %s` for what landed while it was down. Repeat "
            "nothing it already did.\n" % (why, mod))


def launch_mod(root, mod, budget_usd, item, model="opus", seat="BENCH", runner=subprocess.run, bridge=None,
               resume=None, bars=None, preface=None, env=None, session=None, reconcile=None):
    """-> (exit code, text, unit or None). Refuses (2) a missing or non-positive cap, a missing item, a mod at neither
    the offline build nor the blind challenge, one with no build work owed, and at the blind challenge a model below
    opus or a cycle already recorded or blocked, and at in-game acceptance a model other than opus, a visit already
    recorded or blocked, or a bridge `rimflow bridge idle` does not call takeable (bridge: a stand-in for bridge_idle);
    otherwise writes the brief and calls detached_helper.py launch --budget-usd <cap>. It launches nothing else and
    never retries; it never takes the bridge itself (the launched driver does, with --idle-ok). resume (a killed run's
    unit, from the Dispatch step's retry): the cycle or visit that run began may already have a record with no exit
    block; it is resumed, the brief opening with resume_text. bars: an offline build's batch of its refused bars (the
    Dispatch step's split); a bar not refused now is refused. preface (a pilot mod's ledger packet and holder lines,
    modledger.launch): the brief opens with it, then the stage's own brief; env: RM_ variables the run's unit carries
    (the holder's RM_MODLEDGER_WRITER). session: the mod's holder session to resume
    (modledger.resume_plan, `--resume`); reconcile: why the last run was killed or lost, so the brief opens with the
    reconcile step (RIMMANDRAKE_RESUME_HOLDER_SESSIONS_TO_400K_KILL_AND_RESUME)."""
    if not isinstance(budget_usd, (int, float)) or isinstance(budget_usd, bool) or budget_usd <= 0:
        return 2, "REFUSED: a spend cap is required (--budget-usd > 0); there is no default", None
    if not item:
        return 2, "REFUSED: --item is required (a ledger item filed on origin/main)", None
    text, f = brief_text(root, mod, budget_usd, bars=bars)
    ok_owed = ("cycle", "run") + (("no exit block",) if resume else ())
    if resume and f.get("stage") in ("blind_challenge", "in_game"):
        head, _, rest = text.partition("\n\n")
        text = "\n".join([head, ""] + resume_text(f, resume)) + "\n" + rest
    if f.get("stage") == "blind_challenge":
        if model not in JUDGE_MODELS:
            return 2, "REFUSED: a blind judge is a judging role; %s is below the floor (opus or fable)" % model, None
        if f.get("owed") not in ok_owed:
            return 2, "REFUSED: %s owes no blind cycle: cycle %s is %s (%s)" % (
                mod, f.get("cycle"), "recorded" if f.get("owed") != "blocked" else "blocked",
                "; ".join(f.get("blocked") or (f.get("exit") or {}).get("why") or [f.get("owed", UNM)])), None
    elif f.get("stage") == "in_game":
        if model not in LIVE_MODELS:
            return 2, "REFUSED: a live driver runs on %s (Agent_Policy.md, rm-bridge); not %s" % (
                " or ".join(LIVE_MODELS), model), None
        if f.get("owed") not in ok_owed:
            return 2, "REFUSED: %s owes no in-game visit: visit %s is %s (%s)" % (
                mod, f.get("visit"), "recorded" if f.get("owed") != "blocked" else "blocked",
                "; ".join(f.get("blocked") or (f.get("exit") or {}).get("why") or [f.get("owed", UNM)])), None
        go, why = (bridge or bridge_idle)("%s in-game acceptance visit %s" % (mod, f.get("visit")), seat)
        if not go:
            return 2, "REFUSED: the bridge is not takeable for %s's in-game visit %s: %s" % (mod, f.get("visit"), why), None
    elif f.get("stage") != "offline_build":
        return 2, ("REFUSED: %s stands at %s; only an offline build, a blind challenge or an in-game acceptance "
                   "launches from here" % (mod, f.get("stage"))), None
    elif f.get("owed") != "build":
        return 2, "REFUSED: %s owes no build work (%s)" % (mod, f.get("owed")), None
    elif bars and set(bars) - set(f.get("refused_bars") or []):
        return 2, "REFUSED: the batch names bars %s is not refusing: %s" % (
            mod, ", ".join(sorted(set(bars) - set(f.get("refused_bars") or []))[:6])), None
    if preface:
        text = preface.rstrip("\n") + "\n\n---\n\n" + text
    if reconcile:
        text = reconcile_text(mod, reconcile) + "\n" + text
    if session:
        text = resumed_text(mod, session) + "\n" + text
    path = os.path.join(brief_dir(), "%s-%d.md" % (mod, int(now_ts())))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    argv = [sys.executable, detached_helper_path(), "launch", "--seat", seat, "--item", item, "--brief-file", path,
            "--model", model, "--budget-usd", "%g" % budget_usd] + (["--resume", session] if session else [])
    for k, v in sorted((env or {}).items()):
        argv += ["--env", "%s=%s" % (k, v)]
    r = runner(argv, capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    m = re.search(r"^DETACHED (\S+)", r.stdout or "", re.M)
    return r.returncode, out, (m.group(1) if m and not r.returncode else None)


# ---- the blind challenge (Stages 4 and 5): brief, exit reading, launch ---------------------------------------------
#
# Item RIMMANDRAKE_BUILD_BLIND_CHALLENGE_LAUNCHER_FOUR_MODS_PARKED. Measured 2026-11-14 11:37 PM PST: four mods sat at the
# blind challenge with nothing running, because `next` said "launch: none at this stage" and `brief` wrote a Stage 3
# brief; the Conductor wrote four briefs by hand. This half writes what those hand briefs said, per mod, from the mod's
# own files, and reads the exit the pilot's FORMAT_NOTES.md proposes from the newest cycle record. The exit stays the
# steward's to confirm (spec Stages 4 and 5, Exit: PROPOSAL); this reading is evidence for that confirmation, never a move.

BLIND_DIR = "version/blind_challenge"
FORMAT_NOTES = "design/concepts/ExplosiveKnockback/version/blind_challenge/FORMAT_NOTES.md"
OFFLINE_PROVES = ("2", "4-5")       # FORMAT_NOTES: the offline bars are those proving at stage 2 or 4-5
JUDGE_MODELS = ("opus", "fable")    # a judging role: Agent_Policy.md forbids a cheaper tier
BLIND_DEFAULT = ("No Conductor decisions are written for this cycle, so the standing default holds: judge every bar as "
                 "locked, fix each Problem in place red first, write every bar or criterion you believe wrong up as "
                 "NOTED_FOR_CONDUCTOR, and build no verdict on it. Nothing here asks you to change a bar, its wording, "
                 "the Design Version or the stage.")
EXIT_KEYS = ("offline_bars", "problems_open", "exit_met")
LANE1_AFTER_FIX = "lane2/lane1_rows_after_fix.jsonl"   # lane 1 rerun at the fix sha, same rows; lane1_rows.jsonl stays blind


def cycle_numbers(root, mod):
    d = os.path.join(mod_dir(root, mod), BLIND_DIR)
    out = []
    for f in os.listdir(d) if os.path.isdir(d) else []:
        m = re.match(r"cycle_(\d+)$", f)
        if m and os.path.isdir(os.path.join(d, f)):
            out.append(int(m.group(1)))
    return sorted(out)


def offline_bars(tt):
    """-> [(bar id, [deciders])] for the bars that prove offline (proves_at 2 or 4-5)."""
    out = []
    for b in (tt or {}).get("bars") or []:
        if isinstance(b, dict) and str(b.get("proves_at")) in OFFLINE_PROVES:
            out.append((b.get("id", "?"), list(b.get("offline_decides") or b.get("decides") or [])))
    return out


def _jsonl(path):
    """-> list of rows, or None when the file is absent. A line that is not JSON is kept as {"_bad": line}."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = [x for x in f.read().splitlines() if x.strip()]
    except OSError:
        return None
    out = []
    for x in lines:
        try:
            out.append(json.loads(x))
        except ValueError:
            out.append({"_bad": x[:120]})  # cut-ok: in-memory marker of a bad line
    return out


def _rcs(v):
    """-> the rcs of a fixes.jsonl `red` or `green`: one run {`rc`: n or [n, ...]} or a list of runs, one rc each (a run
    with no rc counts as None, so a green list with one unrecorded run is not green)."""
    if isinstance(v, list):
        return [c for x in v for c in (_rcs(x) if isinstance(x, dict) and "rc" in x else [None])]
    v = v.get("rc") if isinstance(v, dict) else None
    return v if isinstance(v, list) else [v] if v is not None else []


# a fixes.jsonl command naming a stand-in for a path (`<parent Source>`, `<copy with Flame 0.7>`) cannot be rerun
PLACEHOLDER = re.compile(r"<[A-Za-z][\w .,/-]*>")


def fault_class(x):
    """-> a faults.json record's class: `class`, or `cls` (FlowWorks cycle 1 wrote it so); '' when neither is set."""
    return str(x.get("class") or x.get("cls") or "")


def _polish_rows(faults, ids):
    """-> {lane-1 row id: Polish fault id} for each row of ids that a Polish fault names in its `evidence`."""
    out = {}
    for x in faults:
        if isinstance(x, dict) and fault_class(x).startswith("Polish"):
            ev = " ".join(str(e) for e in (x.get("evidence") if isinstance(x.get("evidence"), list) else [x.get("evidence")]))
            for i in ids:
                if i not in out and re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(str(i)), ev):
                    out[i] = x.get("id", "?")
    return out


def _cmds(fx):
    """-> every command string of a fixes.jsonl row's red and green runs (`cmd`, or the older `command`)."""
    out = []
    for side in ("red", "green"):
        v = fx.get(side)
        for run in v if isinstance(v, list) else [v]:
            if isinstance(run, dict):
                out += [str(run[k]) for k in ("cmd", "command") if run.get(k)]
    return out


def _side_cmds(fx, side):
    """-> True when every run of a fixes.jsonl row's red or green side names its command (`cmd` or `command`)."""
    v = fx.get(side)
    runs = [r for r in (v if isinstance(v, list) else [v]) if r is not None]
    return bool(runs) and all(isinstance(r, dict) and any(str(r.get(k) or "").strip() for k in ("cmd", "command"))
                              for r in runs)


LANE1_OK = ("PASS", "INFO")


def _lane1_deferred(r, tt):
    """A lane-1 row the blind exit defers to Stage 6 (not a pass, not a block): a `not_kernel` UNSETTLED row naming at
    least one bar, every one of them in the test table and proving outside OFFLINE_PROVES. The blind brief asks lane 1 to
    write a game-side bar this way; it proves live through its stage-6 checks (ingame_debts carries it there). A row
    naming an offline bar, or a bar the table does not hold, still blocks (RIMMANDRAKE_DEFER_BLIND_EXIT_STAGE_SIX_ROWS_
    NEVER_OFFLINE; the loophole ef6a38dbb6 closed stays closed)."""
    if not isinstance(r, dict) or "_bad" in r or str(r.get("kind", "")).lower() != "not_kernel" or \
            str(r.get("verdict", "")).upper() != "UNSETTLED":
        return False
    at = {b.get("id"): str(b.get("proves_at")) for b in (tt or {}).get("bars") or [] if isinstance(b, dict)}
    bars = _split_bars(r.get("bars"))
    return bool(bars) and all(b in at and at[b] not in OFFLINE_PROVES for b in bars)


def _planted_caught(r):
    """A planted_results.jsonl row caught its fault: `caught` true at the top, on any suite/result, or by deciders/lane 1."""
    if any(r.get(k) is True for k in ("caught", "caught_by_deciders", "caught_by_lane1")):
        return True
    for k in ("results", "suites"):
        v = r.get(k)
        if isinstance(v, dict) and any(isinstance(x, dict) and x.get("caught") is True for x in v.values()):
            return True
    return False


def _is_baseline(r):
    return "baseline" in r or str(r.get("id", "")).lower() == "baseline"


def exit_block(summary):
    """-> ({key: value} for the keys found in the SUMMARY.md Exit section, or None when it has no Exit heading)."""
    lines = (summary or "").split("\n")
    start = next((i for i, ln in enumerate(lines) if re.match(r"^##\s+Exit\b", ln)), None)
    if start is None:
        return None
    end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
    sec = "\n".join(lines[start + 1:end])
    got = {}
    m = re.search(r"offline_bars\s*[:=]\s*\{([^}]*)\}", sec)
    if m:
        got["offline_bars"] = {k: v.lower() for k, v in re.findall(
            r"[`\"']?([A-Za-z0-9_]+)[`\"']?\s*:\s*[`\"']?(green|red|GREEN|RED)\b", m.group(1))}
    m = re.search(r"problems_open\s*[:=]\s*`?(\d+)", sec)
    if m:
        got["problems_open"] = int(m.group(1))
    m = re.search(r"exit_met\s*[:=]\s*`?(true|false)\b", sec, re.I)
    if m:
        got["exit_met"] = m.group(1).lower() == "true"
    return got


def read_exit(root, mod, n, tt=None):
    """-> {cycle, state, why[], claimed, checks}: the program's reading of cycle n's exit.

    state: absent (no cycle_n folder) | no_exit_block (no Exit block with the three keys yet: a cycle in progress, or
    one that ended without writing it) | met | not_met. met needs the judge's block to say exit_met true AND every file
    check of FORMAT_NOTES to agree: each offline bar green in the block and each of its deciders PASS on the cycle's own
    rerun (reruns_after_fix.jsonl rows over reruns.jsonl), no Problem whose status is not FIXED, a fixes.jsonl row for
    each FIXED Problem shown red (an rc non-zero) then green (every rc zero), no FAIL row in lane 1, tests_edited.json
    present, and the planted-fault results ending tree_clean_after true. A lane-1 FAIL (recorded blind, before the
    fixes) clears only when LANE1_AFTER_FIX has no FAIL and shows it PASS, or when a Polish fault names that row in its
    evidence (Polish is not part of passing; the reading prints each such row for the steward to confirm). Every fault
    must carry a class, Problem or Polish: an unclassed one could hide an open Problem. Any doubt reads not_met."""
    if tt is None:
        tt, _ = read_json(root, mod, "version/test_table.json")
    base = "%s/cycle_%d" % (BLIND_DIR, n)
    d = os.path.join(mod_dir(root, mod), base)
    out = {"cycle": n, "record": rel(mod, base), "why": [], "checks": {}}
    if not os.path.isdir(d):
        out["state"] = "absent"
        return out
    blk = exit_block(read_text(root, mod, base + "/SUMMARY.md"))
    out["claimed"] = blk
    if not blk or not all(k in blk for k in EXIT_KEYS):
        out["state"] = "no_exit_block"
        out["why"].append("%s/SUMMARY.md has no Exit block with offline_bars, problems_open and exit_met%s" % (
            rel(mod, base), "" if blk is None else " (found: %s)" % (", ".join(sorted(blk)) or "none")))
        return out
    why = out["why"]
    if not blk["exit_met"]:
        why.append("the judge's block says exit_met false")
    bars = offline_bars(tt)
    # zero offline bars is a locked table whose every bar proves live (Graffiti 0.1.0): "every offline bar green" holds
    # with nothing to rerun, and the exit rests on the Problems and the file checks below. It was a block, so such a
    # version could never leave the stage (RIMMANDRAKE_PASS_BLIND_EXIT_ZERO_OFFLINE_BARS_GRAFFITI_STUCK)
    out["checks"]["offline_bars"] = len(bars)
    for b, _ in bars:
        v = blk["offline_bars"].get(b)
        if v != "green":
            why.append("offline bar %s reads %s in the block" % (b, v or "nothing (left out)"))
    reruns = {}
    rr = _jsonl(os.path.join(d, "lane2", "reruns.jsonl"))
    if rr is None:
        why.append("lane2/reruns.jsonl is missing")
    for r in (rr or []) + (_jsonl(os.path.join(d, "lane2", "reruns_after_fix.jsonl")) or []):
        t = r.get("test") or r.get("id")
        if t:
            v = str(r.get("result", "")).upper()
            # a PASS counts only with its run: the command rerun and its rc 0 (a bare "result" is the worker's word)
            if v == "PASS" and not str(r.get("command") or r.get("cmd") or "").strip():
                v = "PASS with no command"
            elif v == "PASS" and not (r.get("rc") == 0 and not isinstance(r.get("rc"), bool)):
                v = "PASS with rc %s (a rerun PASS needs its rc 0)" % r.get("rc", "unrecorded")
            reruns[t] = v
    tests = (tt or {}).get("tests") or {}
    for b, deciders in bars:
        for t in deciders:
            if reruns.get(t) != "PASS":
                x = tests.get(t) if isinstance(tests.get(t), dict) else {}
                why.append("decider %s of offline bar %s %s on this cycle's rerun%s" % (
                    t, b, ("reads " + reruns[t]) if t in reruns else "has no row",
                    "; it is a record with no command to rerun: give it one in test_table.json (a check that the "
                    "record is still there, unchanged: rimflow/record_check.py), then rerun it" if x.get("kind") == "record"
                    and not x.get("command") else ""))
    fj, ferr = read_json(root, mod, base + "/lane2/faults.json")
    faults = (fj.get("faults") if isinstance(fj, dict) else fj) if fj is not None else None
    if not isinstance(faults, list):
        why.append("lane2/faults.json: %s" % (ferr or "no faults list"))
        faults = []
    fixes = {}
    for r in _jsonl(os.path.join(d, "lane2", "fixes.jsonl")) or []:
        if r.get("fault"):
            fixes[r["fault"]] = r
    unclassed = [x.get("id", "?") if isinstance(x, dict) else repr(x)[:40] for x in faults
                 if not (isinstance(x, dict) and re.match(r"(Problem|Polish)", fault_class(x)))]
    if unclassed:
        why.append("%d fault(s) in lane2/faults.json have no class Problem or Polish: %s (an unclassed fault is never "
                   "counted, so it could hide an open Problem)" % (len(unclassed), ", ".join(unclassed[:8])))
    problems = [x for x in faults if isinstance(x, dict) and fault_class(x).startswith("Problem")]
    open_ = [x.get("id", "?") for x in problems if not str(x.get("status", "")).startswith("FIXED")]
    out["checks"]["problems_open"] = len(open_)
    if open_:
        why.append("%d Problem(s) not FIXED: %s" % (len(open_), ", ".join(open_)))
    if blk["problems_open"] != len(open_):
        why.append("the block says problems_open %d; faults.json has %d" % (blk["problems_open"], len(open_)))
    for x in problems:
        if str(x.get("status", "")).startswith("FIXED"):
            fx = fixes.get(x.get("id"))
            red, green = _rcs((fx or {}).get("red")), _rcs((fx or {}).get("green"))
            if not fx or not any(isinstance(c, int) and c != 0 for c in red) or not green or any(c != 0 for c in green):
                inverted = bool(red) and bool(green) and all(c == 0 for c in red) and all(
                    isinstance(c, int) and c != 0 for c in green)
                why.append("FIXED Problem %s has no fixes.jsonl row shown red (an rc non-zero) then green (rc 0)%s"
                           % (x.get("id"), "; its row is inverted (red rc 0, green rc non-zero: a check whose rc 0 is "
                              "the failure): rerun it on the parent and the fix as a test whose rc 0 means the fix "
                              "holds (for a test that must catch a planted fault: the catching run, rc 0 when caught)"
                              if inverted else ""))
            elif not _side_cmds(fx, "red") or not _side_cmds(fx, "green"):
                why.append("FIXED Problem %s: its fixes.jsonl row names no command for its %s run(s) (an rc with no "
                           "command cannot be rerun)" % (x.get("id"), " and ".join(
                               k for k in ("red", "green") if not _side_cmds(fx, k))))
            else:
                held = sorted({m for c in _cmds(fx) for m in PLACEHOLDER.findall(c)})
                if held:
                    why.append("FIXED Problem %s: its fixes.jsonl command holds the placeholder %s, not a rerunnable "
                               "record: name the path and run it at both shas" % (x.get("id"), ", ".join(held)))
    l1 = _jsonl(os.path.join(d, "lane1", "lane1_rows.jsonl"))
    if l1 is None:
        why.append("lane1/lane1_rows.jsonl is missing")
    if l1 is not None and not l1:
        why.append("lane1/lane1_rows.jsonl has no rows (lane 1 judged nothing)")
    # UNSETTLED (or any verdict but PASS and INFO) is not a pass: it clears the way a FAIL does, except a not_kernel row
    # on Stage-6-or-later bars only, which is deferred to Stage 6 (_lane1_deferred)
    deferred = sorted({r.get("id", "?") for r in l1 or [] if _lane1_deferred(r, tt)})
    fails = [r.get("id", "?") for r in l1 or [] if (str(r.get("verdict", "")).upper() not in LANE1_OK or "_bad" in r)
             and not _lane1_deferred(r, tt)]
    if deferred:
        out["checks"]["lane1_deferred_to_stage6"] = deferred
    if l1 and not fails:
        out["checks"]["lane1_fail_cleared_after_fix"] = True     # nothing to clear: no row blocks
    if fails:
        # lane 1 is recorded blind, before the fixes, and stays as recorded: a FAIL there is how a Problem is found. It
        # clears only when lane 1 rerun after the fixes (LANE1_AFTER_FIX) has no FAIL and shows each of those rows PASS.
        after = _jsonl(os.path.join(d, LANE1_AFTER_FIX))
        bad_after = [r.get("id", "?") for r in after or [] if (str(r.get("verdict", "")).upper() not in LANE1_OK
                     or "_bad" in r) and not _lane1_deferred(r, tt)]
        passed = {r.get("id") for r in after or [] if str(r.get("verdict", "")).upper() == "PASS"}
        # a FAIL a Polish fault owns is not passing's; a row that PASSes after the fixes is cleared, not left as Polish
        polish = _polish_rows(faults, sorted((set(fails) - passed) | set(bad_after)))
        out["checks"]["lane1_fail_left_as_polish"] = polish
        bad_after = [f for f in bad_after if f not in polish]
        left = [f for f in fails if f not in passed and f not in polish]
        # a cycle with no fixes has no lane 1 after them: the FAILs a Polish fault owns still clear, and only those
        # (RIMMANDRAKE_CLEAR_POLISH_LANE1_FAIL_WITHOUT_ANY_FIX)
        out["checks"]["lane1_fail_cleared_after_fix"] = not bad_after and not left
        if after is None and left:
            why.append("lane 1 has %d FAIL, UNSETTLED or unreadable row(s): %s, and no %s shows them PASS after the fixes"
                       % (len(fails), ", ".join(fails[:8]), LANE1_AFTER_FIX))
        elif bad_after or left:
            why.append("lane 1 has %d FAIL, UNSETTLED or unreadable row(s): %s; after the fixes %s still fails %s%s" % (
                len(fails), ", ".join(fails[:8]), LANE1_AFTER_FIX, ", ".join(bad_after[:8]) or "nothing",
                (" and does not show PASS for %s" % ", ".join(left[:8])) if left else ""))
    te, terr = read_json(root, mod, base + "/tests_edited.json")
    if not os.path.exists(os.path.join(d, "tests_edited.json")):
        why.append("tests_edited.json is missing (an empty list is written, never left out)")
    elif not (isinstance(te, list) or (isinstance(te, dict) and isinstance(te.get("edited"), list))):
        why.append("tests_edited.json is not a list of edits (a list, or {\"edited\": [...]}): %s" % (
            terr or "it holds %s" % type(te).__name__))
    pr = _jsonl(os.path.join(d, "lane2", "planted_results.jsonl"))
    planted = [r for r in pr or [] if not _is_baseline(r) and (r.get("id") or r.get("file"))]   # a fault, not a tally
    if not pr or pr[-1].get("tree_clean_after") is not True:
        why.append("lane2/planted_results.jsonl %s" % ("is missing" if pr is None else
                                                       "does not end with tree_clean_after true"))
    elif any(r.get("tree_clean_after") is False or "_bad" in r for r in pr):
        why.append("lane2/planted_results.jsonl has a row left the tree not clean (tree_clean_after false) or unreadable")
    if pr is not None and not planted:
        why.append("lane2/planted_results.jsonl plants no fault (only a baseline): the tests were never shown to catch one")
    elif pr is not None and not any(_planted_caught(r) for r in planted):
        why.append("lane2/planted_results.jsonl: none of its %d planted fault(s) was caught" % len(planted))
    fixed = [x.get("id", "?") for x in problems if str(x.get("status", "")).startswith("FIXED")]
    out["checks"]["fixed_this_cycle"] = fixed
    if fixed and not why:
        # RIMMANDRAKE_SEND_FIXES_TO_NEW_BLIND_JUDGE: his road back (spec s4 Stages 4 and 5): fix it, "then send it back
        # to just before Stage 4 again for a new blind judgement pass". A cycle's own fixes never pass its exit.
        out["checks"]["judge_owed"] = True
        why.append("a new blind judge is owed: %d Problem(s) were FIXED in this cycle (%s), and a fixed mod goes back "
                   "to a new blind judgement pass (advance --to blind_challenge opens cycle %d; file nothing new)" % (
                       len(fixed), ", ".join(fixed[:6]), n + 1))
    out["state"] = "not_met" if why else "met"
    if not why:
        pol = out["checks"].get("lane1_fail_left_as_polish") or {}
        why.append("the block says exit_met true and every file check agrees (%d offline bars, %d deciders rerun PASS)%s%s"
                   % (len(bars), sum(len(x[1]) for x in bars), "; lane-1 FAIL left as Polish, not part of passing (the "
                      "steward confirms the move): %s" % ", ".join("%s (%s)" % kv for kv in sorted(pol.items()))
                      if pol else "", "; lane-1 not_kernel UNSETTLED row(s) deferred to Stage 6, owed there: %s" % ", ".join(
                          deferred[:8]) if deferred else ""))
    return out


def cycle_openings(rec):
    """-> {cycle number: iso time} for the moves into the blind challenge (cycle k is the k-th in all)."""
    moves = [m for m in rec.get("moves") or [] if m.get("to") == "blind_challenge"]
    total = (rec.get("cycles") or {}).get("total", 0) or 0
    off = total - len(moves)
    return {i + 1 + off: m.get("at") for i, m in enumerate(moves)}


def cycle_open_sha(mod, k):
    """-> the commit whose stage record first reads cycles.total == k (the advance that opened cycle k), or None."""
    path = "design/concepts/%s/%s" % (mod, RECORD)
    r = subprocess.run(["git", "-C", REPO, "log", "--format=%H", "--", path], capture_output=True, text=True,
                       timeout=60)
    found = None
    for sha in r.stdout.split():
        g = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (sha, path)], capture_output=True, text=True,
                           timeout=60)
        try:
            t = (json.loads(g.stdout).get("cycles") or {}).get("total")
        except ValueError:
            continue
        if t == k:
            found = sha
        elif isinstance(t, int) and t < k:
            break
    return found


def steward_lines(rec, jtext, n):
    """The journal's CONDUCTOR INTERVENED lines since the last cycle: for cycle n >= 2 every line dated after cycle n-1
    opened; for cycle 1 every stage 4+5 line, and any other dated after the stage opened. -> (lines, undated count)."""
    ivs, _ = MN.parse_interventions(jtext or "", "journal")
    opens = cycle_openings(rec)
    since = _ts(opens.get(n - 1)) if n >= 2 else None
    first = _ts(opens.get(n)) or _ts(rec.get("since"))
    out, undated = [], 0
    for iv in ivs:
        if iv["at"] is None:
            undated += 1
            continue
        if n >= 2 and since is not None:
            keep = iv["at"] >= since
        else:
            keep = iv["stage"] == "4+5" or (first is not None and iv["at"] >= first)
        if keep:
            out.append(iv)
    return out, undated


def _ts(v):
    try:
        return dt.datetime.fromisoformat(str(v)).timestamp() if v else None
    except ValueError:
        return None


def blind_facts(root, mod):
    """-> what the blind challenge owes now: cycle (the cycle number for this visit: cycles.total, else the newest
    cycle_N folder), visit, exit (read_exit of cycle_N), and owed: "cycle" (no cycle_N folder: a judge is owed) |
    "no exit block" | "exit met" | "exit not met" | "blocked" (a hold, a version mismatch, a folder past the record)."""
    rec = load(root, mod)
    if rec is None:
        return {"mod": mod, "stage": UNM, "why": "no stage record"}
    cur = rec["stage"]
    out = {"mod": mod, "version": rec.get("version"), "stage": cur, "since": rec.get("since")}
    if cur != "blind_challenge":
        return out
    c = rec.get("cycles") or {}
    total, visit = c.get("total") or 0, c.get("visit") or 0
    have = cycle_numbers(root, mod)
    n = total if total >= 1 else (max(have) if have else 1)
    tt, terr = read_json(root, mod, "version/test_table.json")
    v, verr = read_json(root, mod, "version/VERSION.json")
    blocked = []
    if held(read_text(root, mod, "journal.md"), cur):
        blocked.append("a Conductor hold stands on stage 4+5 (a kind hold line with no later kind release)")
    if v is None or v.get("version") != rec.get("version"):
        blocked.append("the record says version %s; VERSION.json says %s" % (rec.get("version"),
                                                                          (v or {}).get("version", verr)))
    if tt is None:
        blocked.append("version/test_table.json: %s" % terr)
    past = [k for k in have if k > n]
    if past:
        blocked.append("cycle folder(s) %s are past the record's cycle %d" % (past, n))
    ex = read_exit(root, mod, n, tt)
    opened = cycle_openings(rec).get(n) or rec.get("since")
    out.update({"cycle": n, "visit": visit, "total": total, "visit_first": (total - visit + 1) if total and visit
                else n, "cycles_present": have, "exit": ex, "opened": opened, "blocked": blocked,
                "offline_bars": [b for b, _ in offline_bars(tt)]})
    out["owed"] = ("blocked" if blocked else "cycle" if ex["state"] == "absent" else
                   "no exit block" if ex["state"] == "no_exit_block" else
                   "exit met" if ex["state"] == "met" else "exit not met")
    return out


def _src_dir(root, mod):
    d = os.path.join(root, "src", "RimMandrake", mod)
    return "src/RimMandrake/%s" % mod if os.path.isdir(d) else None


def _globbed(root, sdir, rx, limit=None):
    """Files under sdir whose name matches rx, SelfTest folders left out, as repo paths."""
    out = []
    base = os.path.join(root, sdir)
    for dp, dn, fn in os.walk(base):
        dn[:] = [x for x in dn if not x.startswith("SelfTest") and x not in ("obj", "bin")]
        for f in fn:
            if re.search(rx, f):
                out.append(os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/"))
    out.sort()
    return out if limit is None else out[:limit], len(out)


def _kernel_files(tt, deciders, sdir):
    files = []
    for t in deciders:
        for r in ((tt.get("tests") or {}).get(t) or {}).get("reads") or []:
            b = os.path.basename(r)
            if (sdir and r.startswith(sdir + "/") and "/SelfTest" not in r and not b.startswith("selftest_")
                    and b != "validation.py" and b.endswith((".cs", ".py")) and r not in files):
                files.append(r)
    return files


def blind_brief_text(root, mod, cap_usd=None):
    """-> (the mechanical half of a blind-challenge brief, blind_facts). Never refuses; launch_mod does."""
    f = blind_facts(root, mod)
    rec = load(root, mod) or {}
    tt, _ = read_json(root, mod, "version/test_table.json")
    tt = tt or {}
    tests = tt.get("tests") or {}
    n, ver = f.get("cycle", 1), f.get("version", UNM)
    cdir = "design/concepts/%s/%s/cycle_%d" % (mod, BLIND_DIR, n)
    sdir = _src_dir(root, mod)
    bars = offline_bars(tt)
    when = pac_heading(now_ts())
    # no spend bound in the brief (owner 2026-11-16): the launch's --budget-usd is enforced by spend_watchdog.py
    L = ["# Blind challenge (Stages 4 and 5): %s %s, cycle %d" % (mod, ver, n), "",
         "Written by `maturation.py brief %s` at %s: the mechanical half, from the mod's own files (item "
         "RIMMANDRAKE_BUILD_BLIND_CHALLENGE_LAUNCHER_FOUR_MODS_PARKED; spec §4 Stages 4 and 5)." % (mod, when), "",
         "You are a helper of the Conductor; this brief carries the owner's authority. You are %s blind judge: you did "
         "not build this mod%s, and you are told nothing any earlier judge or builder found." % (
             "the" if n == 1 else "a NEW", "" if n == 1 else " and you did not judge an earlier cycle"), "",
         "- Offline only: no game, no bridge, no deploy, no ModsConfig change.",
         "- You start no helpers and no subagents.",
         "- Work in your own clone, and run `./sync` first.",
         "- Commit by explicit path. Land with `./publish`; load skill `clone-landing-commits` once, before your first "
         "commit.",
         "- Foreground commands only, each with a timeout of 540 s or less.",
         "- Write progress to your skeleton at least every 8 minutes.", "",
         "**Wall-time bound: 3 hours.** At the bound, record where you are, commit, publish, and report what is owed.",
         "",
         "## Precondition (check first; stop if it fails)", "",
         "```",
         "python3 -c \"import json;d=json.load(open('design/concepts/%s/%s'));print(d['stage'],d.get('cycles'))\""
         % (mod, RECORD), "```", "",
         "It must print `blind_challenge` with `total` %d (visit %s). Otherwise stop, report \"%s cycle %d not open on "
         "origin/main\", and do not advance it yourself." % (n, f.get("visit", UNM), mod, n), "",
         "## The stage (read first, follow exactly)", "",
         "1. `design/specs/2026-11-13-maturation-pipeline.md`, section \"Stages 4 and 5\": the whole table, the guards on "
         "fixing in place, and \"After three cycles\". This is cycle %d; the Conductor decides after three in a visit "
         "(this visit: cycle %s of it)." % (n, f.get("visit", UNM))]
    own_notes = FORMAT_NOTES.startswith("design/concepts/%s/" % mod)
    if own_notes:
        L.append("2. `%s` is the record format, but it names this mod's cycle-1 findings: it is CLOSED to you until "
                 "lane 1 is committed." % FORMAT_NOTES)
    else:
        L.append("2. `%s`: the pilot's record format and its traps. Use the same layout. It is about another mod and "
                 "carries no %s findings." % (FORMAT_NOTES, mod))
    if n >= 2:
        L += ["", "Its rule for you is **\"All once, then changes.\"** You read the changed files and the bars whose "
              "inputs changed. You are not told what the last judge found. A fault you find late in unchanged material "
              "is still fixed, and is logged as `miss_of: %d`." % (n - 1)]
    L += ["", "**Version facts.** %s has **%d bars** in `version/test_table.json`, %d of them offline (`proves_at` %s)."
          % (ver, len(tt.get("bars") or []), len(bars), " or ".join(OFFLINE_PROVES))]

    # ---- blind list
    closed = ["`design/concepts/%s/journal.md`" % mod, "`exam.json`", "`version/evidence/`",
              "`version/gaps_sorted.md` and `version/polish.md`", "`version/test_table.*`"]
    if sdir:
        st, _ = [], 0
        base = os.path.join(root, sdir, "Source")
        for x in sorted(os.listdir(base)) if os.path.isdir(base) else []:
            if x.startswith("SelfTest") and os.path.isdir(os.path.join(base, x)):
                st.append("`%s/Source/%s/`" % (sdir, x))
        closed += st
        if os.path.exists(os.path.join(root, sdir, "validation.py")):
            closed.append("`%s/validation.py`" % sdir)
    closed += ["any `selftest_*.py`", "any builder report", "the ledger notes on this mod"]
    if own_notes:
        closed.append("`%s`" % FORMAT_NOTES)
    base_sha = None
    if n >= 2:
        base_sha = cycle_open_sha(mod, n - 1)
        closed.insert(0, "anything under `version/blind_challenge/` except `cycle_%d/tests_edited.json`" % (n - 1))
        closed.append("commit messages after `%s`" % (base_sha[:10] if base_sha else UNM))
    closed.append("the section \"Steward's decisions\" at the end of this brief")
    L += ["", "**Stay blind until lane 1 is recorded.** Before then, do not open any of these:"] + \
         ["- %s" % x for x in closed]

    # ---- what changed (cycle >= 2)
    outside = sorted({t.get("file") for t in tests.values() if isinstance(t, dict) and t.get("file")
                      and os.path.isfile(os.path.join(root, str(t["file"])))
                      and not (sdir and t["file"].startswith(sdir + "/"))
                      and not t["file"].startswith("design/concepts/%s/" % mod)})
    if n >= 2:
        paths = ["design/concepts/%s" % mod] + ([sdir] if sdir else []) + outside
        L += ["", "## What changed (find it mechanically, without reading why)", ""]
        if base_sha:
            L += ["```", "git diff --name-only %s origin/main -- %s | grep -v '/blind_challenge/'" % (
                base_sha[:10], " ".join(paths)), "```", "",
                  "`%s` is the advance that opened cycle %d, before its judge ran. Map each changed file to the bars "
                  "whose inputs it touches, and write that map into SUMMARY.md: those bars are your lane-1 scope. If a "
                  "locked file changed (`tree.json`, `sheet.md`, `scenes.json`), the bars on the changed lines are in "
                  "scope too." % (base_sha[:10], n - 1)]
            g = subprocess.run(["git", "-C", REPO, "diff", "--name-only", base_sha, "HEAD", "--"] + paths,
                               capture_output=True, text=True, timeout=60)
            ch = [x for x in g.stdout.split() if "/blind_challenge/" not in x]
            L += ["", "At brief time (`HEAD` of the writer's clone) it lists %d file(s)%s" % (
                len(ch), ":" if ch else ".")] + ["- `%s`" % x for x in ch[:40]] + (
                     ["- ... and %d more" % (len(ch) - 40)] if len(ch) > 40 else [])
        else:
            L += ["The advance that opened cycle %d is not found in git (its stage record never read total %d): diff "
                  "from cycle %d's start time in its SUMMARY.md instead, and say so." % (n - 1, n - 1, n - 1)]

    # ---- lane 1
    L += ["", "## Lane 1 first: game logic from the bars alone", "",
          "Write your start time (UTC) in SUMMARY.md before you open anything.", "", "**Inputs allowed:**"]
    locked = [x for x in ("tree.json", "sheet.md", "plan.md", "version/VERSION.json", "version/bars.md")
              if os.path.exists(os.path.join(mod_dir(root, mod), x))]
    L.append("- Bars, under `design/concepts/%s/`: %s. Grep `scenes.json` for a bar id only when an oracle needs its "
             "numbers." % (mod, ", ".join("`%s`" % x for x in locked)))
    if sdir:
        sett, ns = _globbed(root, sdir, r"(Mod|Settings|Tuning|Gate)\.cs$", 8)
        L.append("- Settings as shipped (defaults and slider ranges): %s%s." % (
            ", ".join("`%s`" % x for x in sett) or "none found by name (find the ModSettings class)",
            " and %d more" % (ns - 8) if ns > 8 else ""))
        per = [x for x in ("Defs", "Patches") if os.path.isdir(os.path.join(root, sdir, x))]
        if per:
            L.append("- Per-type values: %s." % ", ".join("`%s/%s/`" % (sdir, x) for x in per))
    L += ["", "**Where to spend lane 1.** Start with the %d offline bars (`proves_at` %s), and give them most of it; the "
          "kernels below are the files their deciders read:" % (len(bars), " or ".join(OFFLINE_PROVES))]
    for b, deciders in bars:
        k = _kernel_files(tt, deciders, sdir)
        L.append("- `%s`: %s" % (b, ", ".join("`%s`" % x for x in k) if k else
                                 "no kernel named by the table: find it from the bar's words, or write one "
                                 "`not_kernel` row"))
    if sdir:
        ks, nk = _globbed(root, sdir, r"(Math|Kernel)\.cs$", 15)
        L.append("")
        L.append("After those, spend what is left on stage-6 bars whose logic plainly lives in a kernel (%d `*Math.cs` / "
                 "`*Kernel.cs` file(s) outside SelfTest%s). Write a bar whose logic is game-side as one `not_kernel` "
                 "row (verdict UNSETTLED, its `bars` naming only that bar's ids); do not stretch a kernel to cover it. "
                 "The exit defers such a row to Stage 6 when every bar it names proves at stage 6 or later; a "
                 "`not_kernel` row naming an offline bar still blocks the exit." % (nk, (": " + ", ".join("`%s`" % x for x in ks) +
                                                                  (", ..." if nk > 15 else "")) if ks else ""))
    lane1_scratch = "/mnt/d/ClaudeWork/rimmandrake/scratch/%s_blind_c%d_lane1/" % (mod.lower(), n)
    L += ["", "**Tests to write**, your own, from what the bars promise:",
          "- fixed cases",
          "- random cases: record the seed, and shrink a failing case to its smallest form",
          "- conservation checks (nothing created or lost)",
          "- the shipped settings swept through their ranges, every switch off included", "",
          "**How to compile and run.** Compile C# kernels with the per-user Windows dotnet. Stage under `%s`, because "
          "`dotnet.exe` cannot build from a WSL path. The pilot's `lane1/run_lane1.py` shows the pattern: copy the "
          "pattern, not its tests." % lane1_scratch, "",
          "**Rows.** Write `lane1/lane1_rows.jsonl`, one row per line: `id`, `bars`, `kind` (fixed | random | sweep | "
          "info | not_kernel), `verdict` (PASS | FAIL | INFO | UNSETTLED), `cases`, `detail` (with the seed and the "
          "shrunk form). A row you cannot decide is UNSETTLED, with its reason. **Commit lane 1 before you open "
          "anything else.**"]

    # ---- lane 2
    L += ["", "## Lane 2 second: the challenge", "",
          "Now open `version/test_table.json` (`tests.*.command`, `runs_today`, `kind`, `partial`, `known_red`; "
          "`bars.*.proves_at` and `offline_decides`), the code including the game-side callers of every kernel you "
          "tested (the pilot's two real Problems were both in callers), the journal's open questions and its oddities%s, "
          "and then the Steward's decisions at the end." % (", and `%s`" % FORMAT_NOTES if own_notes else ""), "",
          "**Reruns.** Rerun every decider of an offline bar with its recorded command, then as many of the other "
          "offline tests as the bound allows:"]
    seen = set()
    for b, deciders in bars:
        for t in deciders:
            if t in seen:
                continue
            seen.add(t)
            x = tests.get(t) or {}
            r = x.get("runs_today") if isinstance(x.get("runs_today"), dict) else {}
            if x.get("kind") == "record" and not x.get("command"):
                L.append("- `%s` (%s): a record (%s) with no command. A record is rerun too: check the event it names "
                         "with `python3 src/RimMandrake/rimflow/record_check.py --seat <SEAT> --tsn <tsn> --id <item> "
                         "--sha256 <its line's hash>` and write that command in the rerun row; `not_rerunnable` never "
                         "meets the exit" % (t, b, x.get("observes") or "no description"))
                continue
            L.append("- `%s` (%s): `%s`%s" % (t, b, x.get("command") or "no command recorded", (
                " — recorded %s" % (r.get("result") or ("rc %s" % r.get("rc")) if r else "")) if r else ""))
    red_other = []
    for t, x in sorted(tests.items()):
        if t in seen or not isinstance(x, dict) or x.get("kind") != "offline":
            continue
        r = x.get("runs_today") if isinstance(x.get("runs_today"), dict) else {}
        if x.get("known_red") or (r and (r.get("ran") is False or str(r.get("result", "PASS")).upper() != "PASS")):
            red_other.append(t)
    if red_other:
        L.append("- Red or unrun as recorded, deciding no offline bar (rerun them; do not count them against the exit): "
                 "%s." % ", ".join("`%s`" % t for t in red_other))
    slow = [t for t, x in sorted(tests.items()) if isinstance(x, dict) and isinstance(
        (x.get("runs_today") or {}).get("seconds") if isinstance(x.get("runs_today"), dict) else None, (int, float))
        and x["runs_today"]["seconds"] > 300]
    if slow:
        L.append("- Slow as recorded (over 300 s): %s. Never run a whole suite in one command; use the recorded "
                 "`--only` globs." % ", ".join("`%s`" % t for t in slow))
    L += ["- Write `lane2/reruns.jsonl` with `test`, `result`, `recorded_result`, `last`, `recorded_last` and `match`. "
          "Compare verdicts first, and accept a prefix of the last line (the recorded one may be cut short or come "
          "from stderr).", "",
          "**Planted faults.** List them in `lane2/planted_faults.json` (`id`, `file`, `old`, `new`, `bars`): at least "
          "two per offline bar's kernel and at least four in game-side callers or patches%s. Run them with "
          "`lane2/plant_faults.py`, with `WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/%s_blind_c%d_mut/`; "
          "restore on SIGTERM, SIGINT and SIGHUP, and end with `git diff --quiet -- %s`. Write "
          "`lane2/planted_results.jsonl`, baseline first and `{\"tree_clean_after\": true}` last. A fault is caught only "
          "when it makes a new failing row, never by a non-zero rc alone." % (
              ", and two per changed file" if n >= 2 else "", mod.lower(), n, sdir or "design/concepts/%s" % mod), "",
          "**Watch for this.** An offline test that reads source text, not behaviour, can stay green while the "
          "behaviour breaks. A planted behaviour fault that survives a green decider is a Problem against the test.", "",
          "**Faults.** Write each one to `lane2/faults.json` (`{\"faults\": [...]}`) as a refusal record: `id` (a "
          "rimflow name; `python3 src/RimMandrake/rimflow/cli.py namecheck`), `class` (Problem or Polish), `bar`, "
          "`criterion`, `evidence[]`, `would_pass`, `smallest_fix`, `verdict_on_criterion`, `status` (PENDING, FIXED "
          "<sha>, or NOTED_FOR_CONDUCTOR)%s. File each fault as a rimflow item (skill `using-rimflow`, `--why`)." % (
              ", `miss_of` (%d when the fault is in material unchanged since cycle %d)" % (n - 1, n - 1)
              if n >= 2 else "")]

    # ---- edits
    L += ["", "## What you may and may not edit", "",
          "You **may** fix mod code to fix a Problem, red first: the test fails on the parent sha and passes on the fix "
          "sha; record both in `lane2/fixes.jsonl` (`fault`, `red` {`on`, `cmd`, `rc`, `line`}, `green` {same}, `sha`; "
          "`red` or `green` may be a list of such runs, each with its own `rc`: red needs one rc non-zero, green every "
          "rc zero). The command is a test whose rc 0 means the fix holds, so red is an rc non-zero: when the fix is "
          "to a test that must now catch a planted fault, the command is the catching run (rc 0 when caught, "
          "non-zero when missed), never a check whose rc 0 is the failure. Run each command for real at both shas; a `cmd` holding a placeholder like `<parent>` is not a "
          "rerunnable record, so name the path. Leave `lane1/lane1_rows.jsonl` as recorded, blind; after the fixes, "
          "rerun lane 1 into `%s`: a lane-1 FAIL clears only when that file has no FAIL and shows it PASS, or when you "
          "class it Polish and that fault's `evidence` names the row id (Polish is not part of passing). "
          "You may add tests or extend existing ones; list every test you touch in `tests_edited.json` (write it even "
          "when empty). Build C# with `python3 src/RimMandrake/Utils/winbuild.py` and your private `WINBUILD_ROOT`; "
          "never deploy it." % LANE1_AFTER_FIX, "",
          "You **may not** edit any bar text or acceptance criterion; edit the locked tree (%s); weaken, skip or delete "
          "an assertion; change `proves_at` or `decides`; move a bar between versions; or run `maturation.py advance`."
          % ", ".join("`%s`" % x for x in ("tree.json", "sheet.md", "plan.md", "scenes.json", "record.json",
                                          "version/VERSION.json", "version/bars.md")), "",
          "When a fix needs bar text: if the code is wrong, fix the code; if the criterion is wrong but the bar keeps "
          "its meaning, mark it NOTED_FOR_CONDUCTOR (the steward re-pins it); if the bar's words are wrong, mark it "
          "NOTED_FOR_CONDUCTOR (the neutral fixer). Build no verdict on a NOTED bar."]

    # ---- output and exit
    heads = ["Start time"] + (["Changed files to bars"] if n >= 2 else []) + [
        "Lane 1", "Lane 2 reruns", "Planted", "Faults", "Fixes"] + (["Steward's decisions enacted"]) + [
        "Tests edited", "Unsettled", "Exit", "Owed"]
    L += ["", "## Output: skeleton first", "",
          "Your first write is `%s/SUMMARY.md`, with these headings: %s. Fill it as you go. The rest of `cycle_%d/` "
          "follows FORMAT_NOTES: `lane1/` (`BlindLane1.cs` or `.py`, `run_lane1.py --kernel <file>`, `lane1_rows.jsonl`), "
          "`lane2/` (`rerun_offline.py`, `reruns.jsonl`, `planted_faults.json`, `plant_faults.py`, "
          "`planted_results.jsonl`, `faults.json`, `fixes.jsonl`) and `tests_edited.json`." % (
              cdir, ", ".join(heads), n), "",
          "Before each commit run `python3 src/RimMandrake/Utils/code_review_status.py check <path>` on code you changed "
          "and `python3 src/RimMandrake/Utils/run_selftests.py --only <tests>` on the tests you touched. Commit lane 1, "
          "then the fixes, then the record; then `./publish`.", "",
          "## The exit, and who reads it", "",
          "**The exit condition:** every offline bar (%s) is green on your rerun, and no Problem is left PENDING or "
          "NOTED_FOR_CONDUCTOR, and no Problem was FIXED in this cycle. A Problem you FIXED red-first is closed as an item, "
          "but a cycle's own fixes never pass its exit: a new blind judge is owed (his road back: \"send it back to just "
          "before Stage 4 again for a new blind judgement pass\"), so a cycle that fixed any Problem writes "
          "exit_met: false." % (
              ", ".join("`%s`" % b for b, _ in bars) or "none in the table: say so in Exit"), "",
          "Write the Exit section as this block, exactly these three keys (a program reads it):", "",
          "```", "## Exit", "offline_bars: {%s}" % ", ".join("%s: green|red" % b for b, _ in bars),
          "problems_open: N", "exit_met: true|false", "```", "",
          "`python3 src/RimMandrake/rimflow/maturation.py next %s` reads that block and checks it against your files "
          "(each offline bar's deciders PASS in `reruns.jsonl` or `reruns_after_fix.jsonl`, no Problem not FIXED, each "
          "FIXED one red then green in `fixes.jsonl`, no FAIL row in lane 1 or, after the fixes, in `%s`, "
          "`tests_edited.json` present, "
          "`planted_results.jsonl` ending `tree_clean_after: true`). That reading is evidence for the steward, not a "
          "move: the Conductor reads your SUMMARY.md and either advances with `--to in_game --steward-confirms "
          "\"...\"` or opens the next cycle with `--to blind_challenge`. You run one cycle and stop." % (
              mod, LANE1_AFTER_FIX), "",
          SELF_CHECK_RULE % mod, "",
          "## Report (10 lines or fewer, plain words)", "",
          "Tag every number [measured] or [guess ~N%%]: lane 1 rows passing of total and how many UNSETTLED; lane 2 "
          "reruns matching of rerun; planted faults caught of planted; the Problem and Polish counts%s; shas; the tests "
          "you edited; what you could not settle; whether the exit is met; spend." % (
              " and how many are `miss_of`" if n >= 2 else "")]
    L += ["", "## Defects in the pipeline itself", "", SELF_FIX_RULE]

    # ---- steward's decisions
    lines, undated = steward_lines(rec, read_text(root, mod, "journal.md") or "", n)
    L += ["", "---", "", "## Steward's decisions (SEALED: read only after lane 1 is committed)", "",
          "These are the Conductor's decisions as steward, carrying the owner's authority: design inputs, not findings. "
          "Record each one you act on with `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` (that writes "
          "`infrastructure/state/ledger/events/OWNER.jsonl`: commit and publish it too).", ""]
    if lines:
        L.append("From the journal's Conductor interventions %s:" % (
            "since cycle %d opened" % (n - 1) if n >= 2 else "for stage 4+5, and any other since the stage opened"))
        L += ["- %s (stage %s, kind %s): %s" % (pac_heading(iv["at"]), iv["stage"], iv["kind"], iv["what"])
              for iv in lines]
    else:
        L.append(BLIND_DEFAULT)
    if undated:
        L += ["", "(%d intervention line(s) in the journal carry no date and are not shown.)" % undated]
    return "\n".join(L) + "\n", f


# ---- in-game acceptance (Stage 6): brief, exit reading, launch -------------------------------------------------------
#
# Item RIMMANDRAKE_BUILD_IN_GAME_STAGE_LAUNCHER_PYRELANDS_ARRIVED_FIRST. Measured 2026-11-15 1:47 AM PST: Pyrelands 0.1.0
# was advanced to in-game acceptance and `next` said "launch: none at this stage", the gap the blind challenge had an hour
# before. This half writes the in-game brief from the mod's own files (every stage-6 check of its test table with its
# exact command, the live tests the blind cycles left owed, the bridge rules), reads a machine-checkable exit from the
# visit's record, and launches one live driver when the visit is owed and the bridge is takeable. The exit stays the
# steward's to confirm (spec Stage 6, Exit: CARRIED plus PROPOSAL); this reading is evidence, never a move.
#
# The visit's record, design/concepts/<Mod>/version/in_game/visit_<N>/ (N = the moves into in_game so far):
#   rows.jsonl     one row per run of a stage-6 check: {"test", "verdict": PASS|FAIL|UNMEASURED, "site_checked": bool,
#                  "game": "archmagi"|"stevedesktop", "mod_sha", "command", "evidence"}; the last row per test counts (a
#                  rerun after a fix made in the sitting supersedes; the earlier FAIL stays as history)
#   strange.jsonl  one row per strange thing seen that no bar covers: {"what", "explained": "..."} or {"what", "filed": ID}
#   SUMMARY.md     its "## Exit" section holds the block: ingame_rows: {test: pass|fail|unmeasured, ...} / strange_open: N
#                  / savegame: <path> / exit_met: true|false
# met needs the driver's block to say exit_met true AND the files to agree: every stage-6 check of the table pass in the
# block and PASS in its last row, on a site checked first, with the game and the mod's sha named; every strange thing
# explained or filed, strange_open equal to the count left; the savegame on disk. Any doubt reads not_met, never met.

INGAME_DIR = "version/in_game"
INGAME_KEYS = ("ingame_rows", "strange_open", "savegame", "exit_met")
LIVE_MODELS = ("opus",)     # a live driver: Agent_Policy.md "Helpers in this repo" (rm-bridge, opus); Fable never waits
                            # on a live resource (the user-level model ladder)
GAMES = ("archmagi", "stevedesktop")
BRIDGE_RULES = (
    "- Take the bridge first, delegated: `python3 src/RimMandrake/rimflow/cli.py bridge take --idle-ok --for \"%s\" "
    "--seat %s`. Refused (another seat or a live driver holds it): stop, write a note, report \"bridge held\". Never "
    "`--force` a hold that is not stale, and never take his OWNER hold.",
    "- Keep the hold fresh: a ledger event at least every 40 minutes (a note on your item), or another window may take "
    "it as stale.",
    "- Release it the moment you stop, whatever the outcome: `python3 src/RimMandrake/rimflow/cli.py bridge release "
    "--seat %s`.",
    "- Never a flyer's flight: a flyer is read by its `Pawn_FlightTracker` state, paused; never watched, never captured "
    "in flight (owner: \"For the third time, do not do live testing of flyers without a human present.\").",
    "- Never leave a broken game running: a game that errors at load, hangs or holds a broken map when you stop is "
    "closed (`./game --why \"<why>\" down`). Never fullscreen or focus the game window.",
    "- Every mod list holds all five DLC (owner: \"ALL TEST MOD LISTS should include ALL THE EXPANSIONS\"). Use the "
    "smallest list a check names (the 13-mod minimal list plus what its command adds: ~22 s a load, against ~15 min "
    "on the full list); the full list only for a check whose `why_full_list` says why. "
    "`src/RimMandrake/Utils/modlist_swap.py` does the swap; never restore his list afterwards (owner, 2026-10-24).",
    "- Deploy before you test: `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod %s` (a dry run), then "
    "`--apply`. Writing a file is not deploying it.",
    "- Only the canonical world saves are precious (`infrastructure/state/CANONICAL_SAVE.md`): never overwrite one. Back "
    "up the Saves folder before you write the labelled savegame.",
    "- A site is asserted, never hoped: check each test site (open sky, no stray animals, the biome the check needs) "
    "before a row counts, and write `site_checked` on the row.",
    "- The game is never held for his look while he is away (owner, 2026-11-16: \"Do not hold live testing when I can't "
    "go to the desktop such as now.\"): a staged look is a kept save, re-staged from that save when he sits down, so "
    "never wait on one and never leave the game parked for one. Keep every save a look was staged on (`*OWNER_LOOK*` "
    "and any save his item's notes name): load your own site over it, never delete or overwrite it.",
)
INGAME_DEFAULT = ("No Conductor decisions are written for this visit, so the standing default holds: run every stage-6 "
                  "check above and the owed cases, look beyond them, and fix in the sitting what a small fix can fix. "
                  "Do not change a bar, its wording, the Design Version or the stage.")
OWNER_STAGE6 = ("In-game acceptance testing with setup maps, proper acceptance testing, and using the fastest methods "
                "available with dense, rich setups that test many items simultaneously + allowances to explore beyond "
                "the acceptance tests and plentiful screenshots to look for 'strange unexpected things.'")


def ingame_tests(tt):
    """-> [(test id, test)] for the table's stage-6 in-game checks (kind live*, stage 6), in table order."""
    return [(k, t) for k, t in ((tt or {}).get("tests") or {}).items()
            if isinstance(t, dict) and str(t.get("kind", "")).startswith("live") and str(t.get("stage")) == "6"]


def visit_numbers(root, mod):
    d = os.path.join(mod_dir(root, mod), INGAME_DIR)
    out = []
    for f in os.listdir(d) if os.path.isdir(d) else []:
        m = re.match(r"visit_(\d+)$", f)
        if m and os.path.isdir(os.path.join(d, f)):
            out.append(int(m.group(1)))
    return sorted(out)


def ingame_openings(rec):
    """-> {visit number: iso time} for the moves into in-game acceptance (visit k is the k-th)."""
    return {i + 1: m.get("at") for i, m in enumerate(m for m in rec.get("moves") or [] if m.get("to") == "in_game")}


def native_to_here(p):
    """A Windows path (C:\\...) as this machine reads it (/mnt/c/...); any other path unchanged."""
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", str(p or ""))
    return "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/")) if m else str(p or "")


def ingame_exit_block(summary):
    """-> ({key: value} for the keys found in the SUMMARY.md Exit section, or None when it has no Exit heading)."""
    lines = (summary or "").split("\n")
    start = next((i for i, ln in enumerate(lines) if re.match(r"^##\s+Exit\b", ln)), None)
    if start is None:
        return None
    end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
    sec = "\n".join(lines[start + 1:end])
    got = {}
    m = re.search(r"ingame_rows\s*[:=]\s*\{([^}]*)\}", sec)
    if m:
        got["ingame_rows"] = {k: v.lower() for k, v in re.findall(
            r"[`\"']?([A-Za-z0-9_]+)[`\"']?\s*:\s*[`\"']?(pass|fail|unmeasured)\b", m.group(1), re.I)}
    m = re.search(r"strange_open\s*[:=]\s*`?(\d+)", sec)
    if m:
        got["strange_open"] = int(m.group(1))
    m = re.search(r"^\s*savegame\s*[:=]\s*`?([^`\n]+?)`?\s*$", sec, re.M)
    if m:
        got["savegame"] = m.group(1).strip()
    m = re.search(r"exit_met\s*[:=]\s*`?(true|false)\b", sec, re.I)
    if m:
        got["exit_met"] = m.group(1).lower() == "true"
    return got


SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
EXPLAIN_WORDS = 6
ITEM_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+){2,}$")


def _strange_settled(x):
    """A strange.jsonl entry is settled when `filed` names an item (a rimflow name) or `explained` says why in
    EXPLAIN_WORDS words at least: "ok" or "yes" is not an explanation (RIMMANDRAKE_CLOSE_EXIT_READER_LOOPHOLES)."""
    if not isinstance(x, dict) or "_bad" in x:
        return False
    if ITEM_RE.match(str(x.get("filed") or "").strip()):
        return True
    return len(str(x.get("explained") or "").split()) >= EXPLAIN_WORDS


def _site_shown(root, r):
    """site_checked is backed by a non-empty `site` reading or an `evidence` file on disk (repo-relative or native)."""
    if isinstance(r.get("site"), dict) and r["site"]:
        return True
    ev = r.get("evidence")
    for e in ev if isinstance(ev, list) else [ev]:
        if isinstance(e, str) and e.strip():
            p = native_to_here(e.strip())
            if os.path.isfile(p if os.path.isabs(p) else os.path.join(root, p)):
                return True
    return False


def _is_savegame(path):
    """An .rws file whose first 4 KB hold XML and a <savegame> element."""
    if not path.lower().endswith(".rws"):
        return False
    try:
        with open(path, "rb") as f:
            head = f.read(4096)
    except OSError:
        return False
    head = head[3:] if head.startswith(b"\xef\xbb\xbf") else head    # RimWorld writes a UTF-8 BOM
    return head.lstrip().startswith(b"<") and b"<savegame" in head


def read_ingame_exit(root, mod, n, tt=None):
    """-> {visit, state, why[], claimed, rows}: the program's reading of visit n's exit. state: absent (no visit_n folder)
    | no_exit_block (no Exit block with the four keys: a visit in progress, or one that ended without writing it) | met |
    not_met. See the record layout above this section."""
    if tt is None:
        tt, _ = read_json(root, mod, "version/test_table.json")
    base = "%s/visit_%d" % (INGAME_DIR, n)
    d = os.path.join(mod_dir(root, mod), base)
    out = {"visit": n, "record": rel(mod, base), "why": [], "rows": {}}
    if not os.path.isdir(d):
        out["state"] = "absent"
        return out
    blk = ingame_exit_block(read_text(root, mod, base + "/SUMMARY.md"))
    out["claimed"] = blk
    if not blk or not all(k in blk for k in INGAME_KEYS):
        out["state"] = "no_exit_block"
        out["why"].append("%s/SUMMARY.md has no Exit block with %s%s" % (
            rel(mod, base), ", ".join(INGAME_KEYS), "" if blk is None else " (found: %s)" % (", ".join(sorted(blk))
                                                                                            or "none")))
        return out
    why = out["why"]
    if not blk["exit_met"]:
        why.append("the driver's block says exit_met false")
    checks = ingame_tests(tt)
    if not checks:
        why.append("the test table names no stage-6 in-game check (kind live*, stage 6)")
    rows = _jsonl(os.path.join(d, "rows.jsonl"))
    if rows is None:
        why.append("rows.jsonl is missing")
    last, earlier = {}, {}
    for r in rows or []:
        t = r.get("test") or r.get("id")
        if t:
            if t in last and str(last[t].get("verdict", "")).upper() != "PASS":
                earlier.setdefault(t, []).append(str(last[t].get("verdict", "")).upper() or "no verdict")
            last[t] = r
    for t, _ in checks:
        claim = blk["ingame_rows"].get(t)
        r = last.get(t)
        v = str((r or {}).get("verdict", "")).upper()
        out["rows"][t] = v or "NO ROW"
        if claim != "pass":
            why.append("in-game check %s reads %s in the block" % (t, claim or "nothing (left out)"))
        if r is None:
            why.append("in-game check %s has no row in rows.jsonl" % t)
            continue
        if v != "PASS":
            why.append("in-game check %s: its last row reads %s" % (t, v or "no verdict"))
        if earlier.get(t):
            why.append("in-game check %s: an earlier row reads %s; a later PASS does not hide it (the failure goes "
                       "down its road back, and a new visit reruns it)" % (t, ", ".join(earlier[t])))
        if r.get("site_checked") is not True:
            why.append("in-game check %s: its row does not say the site was checked first (site_checked)" % t)
        elif not _site_shown(root, r):
            why.append("in-game check %s: site_checked true with nothing to show it (a non-empty `site` reading, or an "
                       "`evidence` file on disk)" % t)
        if str(r.get("game", "")).lower() not in GAMES:
            why.append("in-game check %s: its row names no game (%s)" % (t, " or ".join(GAMES)))
        if not r.get("mod_sha"):
            why.append("in-game check %s: its row names no mod_sha (the build it ran)" % t)
        elif not SHA_RE.match(str(r.get("mod_sha"))):
            why.append("in-game check %s: its mod_sha %r is not a commit hash (7 to 40 hex)" % (t, r.get("mod_sha")))
    # RIMMANDRAKE_BIND_STAGE_EVIDENCE_TO_ONE_BUILD (the part that needs no ruling): one visit judges ONE build, so every
    # row's mod_sha names the same commit (a short hash agrees with a long one it starts)
    shas = sorted({str(r.get("mod_sha")) for r in rows or [] if SHA_RE.match(str(r.get("mod_sha") or ""))}, key=len)
    one = all(b.startswith(a) for i, a in enumerate(shas) for b in shas[i + 1:])
    if not one:
        why.append("the rows name more than one build (mod_sha %s): one visit judges one build" % ", ".join(shas))
    out["build"] = shas[-1] if shas and one else None
    st = _jsonl(os.path.join(d, "strange.jsonl"))
    if st is None:
        why.append("strange.jsonl is missing (an empty file says nothing strange was seen)")
    left = [x.get("what", x.get("_bad", "?")) for x in st or [] if not _strange_settled(x)]
    out["strange_open"] = len(left)
    if left:
        why.append("%d strange thing(s) neither explained nor filed (an explanation of %d words at least, or a named "
                   "item): %s" % (len(left), EXPLAIN_WORDS, "; ".join(str(x)[:60]
                                                                                             for x in left[:3])))
    if st is not None and blk["strange_open"] != len(left):
        why.append("the block says strange_open %d; strange.jsonl leaves %d" % (blk["strange_open"], len(left)))
    sv = blk["savegame"]
    if not os.path.isfile(native_to_here(sv)):
        why.append("the savegame %s is not on disk" % sv)
    elif not _is_savegame(native_to_here(sv)):
        why.append("the savegame %s is not a RimWorld save (an .rws file whose head is XML holding <savegame>)" % sv)
    out["state"] = "not_met" if why else "met"
    if not why:
        why.append("%d of %d in-game checks PASS on checked sites; strange things all explained or filed; savegame %s"
                   % (len(checks), len(checks), sv))
    return out


def _bars_of(tt, tid):
    return [b.get("id") for b in (tt or {}).get("bars") or [] if isinstance(b, dict) and tid in (b.get("decides") or [])]


def _stage6_of_bars(tt, bars):
    """-> the stage-6 checks that decide any of the bars, table order; when none decides them (a bar proved offline),
    the stage-6 checks that support them, each marked "(supports)"."""
    ids = dict(ingame_tests(tt))
    want = set(bars)
    out, sup = [], []
    for b in (tt or {}).get("bars") or []:
        if isinstance(b, dict) and b.get("id") in want:
            out += [t for t in b.get("decides") or [] if t in ids and t not in out]
            sup += [t for t in b.get("supports") or [] if t in ids and t not in sup]
    return out or ["%s (supports)" % t for t in sup]


def _split_bars(v):
    return [x.strip() for x in (v if isinstance(v, list) else str(v or "").split(",")) if x.strip()]


def _section(text, head):
    """-> the body of a '## <head>' section of a markdown text, stripped, or ''."""
    lines = (text or "").split("\n")
    start = next((i for i, ln in enumerate(lines) if re.match(r"^##\s+%s\b" % re.escape(head), ln)), None)
    if start is None:
        return ""
    end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
    return "\n".join(lines[start + 1:end]).strip()


def ledger_ended(root, ids):
    """-> the subset of ids whose newest close, drop, supersede or reopen (a `live` event with result broken) on any
    shard under infrastructure/state/ledger/events/ is not a reopen; ordered by tsn, file order where it is missing."""
    d = os.path.join(root, "infrastructure", "state", "ledger", "events")
    want, last, n = set(ids), {}, 0
    for f in sorted(os.listdir(d)) if os.path.isdir(d) and want else []:
        if not f.endswith(".jsonl"):
            continue
        with open(os.path.join(d, f), encoding="utf-8") as fh:
            for ln in fh:
                if not any(k in ln for k in ('"close"', '"drop"', '"supersede"', '"live"')):
                    continue
                try:
                    e = json.loads(ln)
                except ValueError:
                    continue
                kind, i = e.get("event"), e.get("id")
                if i not in want or kind not in ("close", "drop", "supersede", "live"):
                    continue
                if kind == "live" and e.get("result") != "broken":
                    continue
                n += 1
                key = (int(e["tsn"]) if str(e.get("tsn") or "").isdigit() else 0, n)
                if i not in last or key > last[i][0]:
                    last[i] = (key, kind != "live")
    return {i for i, (_, done) in last.items() if done}


def ledger_items_caused_by(root, ids):
    """-> [{id, title, needs}] for the ledger items filed (file or spawn) with caused_by one of ids and not closed,
    dropped or superseded since, read from every shard under infrastructure/state/ledger/events/. `needs` is the item's
    current window (ledger_needs), None when it never had one."""
    d = os.path.join(root, "infrastructure", "state", "ledger", "events")
    want, filed, ended = set(ids), {}, set()
    for f in sorted(os.listdir(d)) if os.path.isdir(d) and want else []:
        if not f.endswith(".jsonl"):
            continue
        with open(os.path.join(d, f), encoding="utf-8") as fh:
            for ln in fh:
                if '"caused_by"' not in ln and '"close"' not in ln and '"drop"' not in ln and '"supersede"' not in ln:
                    continue
                try:
                    e = json.loads(ln)
                except ValueError:
                    continue
                if e.get("event") in ("file", "spawn") and e.get("caused_by") in want:
                    filed[e.get("id")] = e.get("title") or ""
                elif e.get("event") in ("close", "drop", "supersede"):
                    ended.add(e.get("id"))
    live = [k for k in sorted(filed) if k not in ended]
    needs = ledger_needs(root, live)
    return [{"id": k, "title": filed[k], "needs": needs.get(k)} for k in live]


def ledger_caused_by(root, ids):
    """-> {id: caused_by} for these ledger items, from their file or spawn event (an item filed with none is absent)."""
    d = os.path.join(root, "infrastructure", "state", "ledger", "events")
    want, out = set(ids), {}
    for f in sorted(os.listdir(d)) if os.path.isdir(d) and want else []:
        if not f.endswith(".jsonl"):
            continue
        with open(os.path.join(d, f), encoding="utf-8") as fh:
            for ln in fh:
                if '"caused_by"' not in ln:
                    continue
                try:
                    e = json.loads(ln)
                except ValueError:
                    continue
                if e.get("id") in want and e.get("event") in ("file", "spawn") and e.get("caused_by"):
                    out[e["id"]] = e["caused_by"]
    return out


def ledger_needs(root, ids):
    """-> {id: needs} for these ledger items: the `needs` of their file/spawn event, then of each later `needs` event
    (`to`) or `implemented` event that sets one, in shard order (the fold model.replay does for this one field).
    An item that never had one is absent. needs says which window an item's work needs (model.NEEDS)."""
    d = os.path.join(root, "infrastructure", "state", "ledger", "events")
    want, out, seen = set(ids), {}, []
    for f in sorted(os.listdir(d)) if os.path.isdir(d) and want else []:
        if not f.endswith(".jsonl"):
            continue
        with open(os.path.join(d, f), encoding="utf-8") as fh:
            for ln in fh:
                if '"needs"' not in ln:
                    continue
                try:
                    e = json.loads(ln)
                except ValueError:
                    continue
                if e.get("id") not in want:
                    continue
                n = e.get("to") if e.get("event") == "needs" else e.get("needs")
                if n and e.get("event") in ("file", "spawn", "needs", "implemented"):
                    seen.append((str(e.get("ts") or ""), e.get("tsn") or 0, e["id"], n))
    for _, _, i, n in sorted(seen, key=lambda x: (x[0], x[1])):     # shards interleave: time order, not file order
        out[i] = n
    return out


def ingame_debts(root, mod, tt=None):
    """-> what the newest blind cycle left owed to Stage 6, from its own files: fixed Problems never run live, scene
    Polish, planted faults no offline test caught, lane 1's UNSETTLED rows, open ledger items caused by its faults, and
    its SUMMARY's Owed and Unsettled sections verbatim. Each entry names its bars and their stage-6 checks."""
    if tt is None:
        tt, _ = read_json(root, mod, "version/test_table.json")
    have = cycle_numbers(root, mod)
    out = {"cycle": max(have) if have else None, "fixed_problems": [], "scene_polish": [], "planted_misses": [],
           "lane1_unsettled": [], "items": [], "owed_text": "", "unsettled_text": ""}
    if not have:
        return out
    base = "%s/cycle_%d" % (BLIND_DIR, out["cycle"])
    d = os.path.join(mod_dir(root, mod), base)
    out["record"] = rel(mod, base)
    summ = read_text(root, mod, base + "/SUMMARY.md") or ""
    out["owed_text"], out["unsettled_text"] = _section(summ, "Owed"), _section(summ, "Unsettled")
    fj, _ = read_json(root, mod, base + "/lane2/faults.json")
    faults = fj if isinstance(fj, list) else (fj or {}).get("faults") or []
    for x in faults:
        if not isinstance(x, dict):
            continue
        bars = _split_bars(x.get("bar") or x.get("bars"))
        e = {"id": x.get("id"), "bars": bars, "checks": _stage6_of_bars(tt, bars), "status": x.get("status"),
             "fix": x.get("smallest_fix") or ""}
        cls = fault_class(x)
        if cls.startswith("Problem") and str(x.get("status", "")).startswith("FIXED") and e["checks"]:
            out["fixed_problems"].append(e)
        elif cls.startswith("Polish") and re.search(r"scene|live|stage 6", "%s %s" % (x.get("id"), e["fix"]), re.I):
            out["scene_polish"].append(e)
    pf, _ = read_json(root, mod, base + "/lane2/planted_faults.json")
    pf = {y.get("id"): y for y in (pf if isinstance(pf, list) else (pf or {}).get("faults") or [])
          if isinstance(y, dict)}
    for r in _jsonl(os.path.join(d, "lane2", "planted_results.jsonl")) or []:
        if r.get("id") and r.get("caught") is False:
            bars = _split_bars(r.get("bars") or (pf.get(r["id"]) or {}).get("bars"))
            out["planted_misses"].append({"id": r["id"], "file": r.get("file") or (pf.get(r["id"]) or {}).get("file"),
                                          "new": (pf.get(r["id"]) or {}).get("new"), "bars": bars,
                                          "checks": _stage6_of_bars(tt, bars)})
    l1 = _jsonl(os.path.join(d, "lane2", "lane1_rows_after_fix.jsonl"))
    for r in l1 if l1 is not None else _jsonl(os.path.join(d, "lane1", "lane1_rows.jsonl")) or []:
        if str(r.get("verdict", "")).upper() == "UNSETTLED":
            bars = _split_bars(r.get("bars"))
            out["lane1_unsettled"].append({"id": r.get("id"), "bars": bars, "detail": r.get("detail") or "",
                                           "checks": _stage6_of_bars(tt, bars)})
    out["items"] = ledger_items_caused_by(root, [x.get("id") for x in faults if isinstance(x, dict) and x.get("id")])
    return out


UNRUN_FILE = INGAME_DIR + "/unrun.jsonl"


def record_unrun(root, mod, item, check, command, offline, sha, by="BENCH"):
    """Appends one row to version/in_game/unrun.jsonl: road-back item `item` closed at an offline stage on its offline
    test (`offline`, green at `sha`); its in-game check `check` is UNRUN until Stage 6, with its exact `command` (spec
    §4 Stage 3 exit: "Every in-game check exists and is listed UNRUN with its exact command until Stage 6"). -> the row.
    Refuses (ValueError) a row missing any of them."""
    row = {"item": item, "check": check, "command": command, "offline": offline, "sha": sha, "result": "UNRUN",
           "by": by, "at": iso(now_ts())}
    gone = [k for k in ("item", "check", "command", "offline", "sha") if not str(row[k] or "").strip()]
    if gone:
        raise ValueError("an UNRUN record needs %s" % ", ".join(gone))
    p = os.path.join(mod_dir(root, mod), UNRUN_FILE)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def read_unrun(root, mod):
    """-> the UNRUN rows of version/in_game/unrun.jsonl (record_unrun), oldest first; [] when there is none."""
    rows = _jsonl(os.path.join(mod_dir(root, mod), UNRUN_FILE)) or []
    return [r for r in rows if isinstance(r, dict) and "_bad" not in r]


def unrun_lines(root, mod):
    """-> the Stage 6 brief's lines for the road-back items closed offline whose in-game check is still UNRUN."""
    rows = read_unrun(root, mod)
    if not rows:
        return ["- none recorded"]
    return ["- Item `%s` (closed offline on `%s` at %s): in-game check `%s` is UNRUN; run `%s`." % (
        r.get("item"), r.get("offline"), r.get("sha"), r.get("check"), r.get("command")) for r in rows]


def ingame_facts(root, mod):
    """-> what in-game acceptance owes now: visit (the moves into in_game so far), exit (read_ingame_exit of visit_N),
    checks (the stage-6 ids), testq (those carrying a testq block: what SteveDesktop's queue may admit), and owed:
    "run" (no visit_N folder: a live driver is owed) | "no exit block" | "exit met" | "exit not met" | "blocked" (a
    hold, a version mismatch, an unreadable table, no stage-6 check, a folder past the record)."""
    rec = load(root, mod)
    if rec is None:
        return {"mod": mod, "stage": UNM, "why": "no stage record"}
    cur = rec["stage"]
    out = {"mod": mod, "version": rec.get("version"), "stage": cur, "since": rec.get("since")}
    if cur != "in_game":
        return out
    n = max(1, len(ingame_openings(rec)))
    tt, terr = read_json(root, mod, "version/test_table.json")
    v, verr = read_json(root, mod, "version/VERSION.json")
    blocked = []
    if held(read_text(root, mod, "journal.md"), cur):
        blocked.append("a Conductor hold stands on stage 6 (a kind hold line with no later kind release)")
    if v is None or v.get("version") != rec.get("version"):
        blocked.append("the record says version %s; VERSION.json says %s" % (rec.get("version"),
                                                                          (v or {}).get("version", verr)))
    if tt is None:
        blocked.append("version/test_table.json: %s" % terr)
    checks = ingame_tests(tt)
    if tt is not None and not checks:
        blocked.append("the test table names no stage-6 in-game check")
    have = visit_numbers(root, mod)
    past = [k for k in have if k > n]
    if past:
        blocked.append("visit folder(s) %s are past the record's visit %d" % (past, n))
    ex = read_ingame_exit(root, mod, n, tt)
    out.update({"visit": n, "visits_present": have, "exit": ex, "opened": ingame_openings(rec).get(n) or rec.get("since"),
                "blocked": blocked, "checks": [k for k, _ in checks],
                "testq": [k for k, t in checks if isinstance(t.get("testq"), dict)]})
    out["owed"] = ("blocked" if blocked else "run" if ex["state"] == "absent" else
                   "no exit block" if ex["state"] == "no_exit_block" else
                   "exit met" if ex["state"] == "met" else "exit not met")
    return out


def bridge_idle(purpose, seat="BENCH", runner=subprocess.run):
    """-> (takeable, text): `rimflow bridge idle`, the delegated take's own verdict (the ledger holder, his OWNER hold,
    the shared lock across clones and the Archmagi driver lock), read-only. MATURATION_BRIDGE_IDLE names a stand-in
    command (the selftests'); a reading that fails is not takeable."""
    cmd = os.environ.get("MATURATION_BRIDGE_IDLE")
    argv = ([sys.executable, cmd] if cmd else [sys.executable, os.path.join(HERE, "cli.py")]) + [
        "bridge", "idle", "--for", purpose, "--seat", seat]
    try:
        r = runner(argv, capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        return False, "the bridge reading failed: %s" % e
    text = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()
    line = next((x for x in reversed(text) if x.startswith(("TAKEABLE", "NOT TAKEABLE"))), text[-1] if text else "")
    return r.returncode == 0 and line.startswith("TAKEABLE"), line or "no reading (rc %s)" % r.returncode


def _check_lines(tt, ids, root):
    tests = (tt or {}).get("tests") or {}
    out = []
    for t in ids:
        x = tests.get(t) or {}
        out.append("- **`%s`** (%s; decides %s): %s" % (t, x.get("kind", "?"), ", ".join(_bars_of(tt, t)) or "no bar",
                                                       x.get("observes", "no observation written")))
        out.append("  - command: `%s`" % (x.get("command") or "NONE WRITTEN: the table owes one; record the row "
                                                              "UNMEASURED and say so"))
        f = x.get("file")
        if f:
            out.append("  - entry `%s` in `%s`%s" % (x.get("entry") or "?", f, "" if os.path.exists(
                os.path.join(root, f)) else " (NOT ON DISK in this tree)"))
        if x.get("why_full_list"):
            out.append("  - full list, because: %s" % x["why_full_list"])
    return out


def ingame_brief_text(root, mod, cap_usd=None, seat="BENCH"):
    """-> (the mechanical half of an in-game acceptance brief, ingame_facts). Never refuses; launch_mod does."""
    f = ingame_facts(root, mod)
    rec = load(root, mod) or {}
    tt, _ = read_json(root, mod, "version/test_table.json")
    tt = tt or {}
    n, ver = f.get("visit", 1), f.get("version", UNM)
    vdir = "design/concepts/%s/%s/visit_%d" % (mod, INGAME_DIR, n)
    when = pac_heading(now_ts())
    # no spend bound in the brief (owner 2026-11-16): the launch's --budget-usd is enforced by spend_watchdog.py
    purpose = "%s in-game acceptance visit %d" % (mod, n)
    checks = f.get("checks") or []
    full = [k for k in checks if (tt.get("tests") or {}).get(k, {}).get("kind") == "live_full"]
    debts = ingame_debts(root, mod, tt)
    L = ["# In-game acceptance (Stage 6): %s %s, visit %d" % (mod, ver, n), "",
         "Written by `maturation.py brief %s` at %s: the mechanical half, from the mod's own files (item "
         "RIMMANDRAKE_BUILD_IN_GAME_STAGE_LAUNCHER_PYRELANDS_ARRIVED_FIRST; spec §4 Stage 6)." % (mod, when), "",
         "You are a helper of the Conductor; this brief carries the owner's authority. You are the live driver of one "
         "game for one visit. The owner's words for this stage: \"%s\"" % OWNER_STAGE6, "",
         "- You start no helpers and no subagents. Work in your own clone, and run `./sync` first.",
         "- Commit by explicit path. Land with `./publish`; load skill `clone-landing-commits` once, before your first "
         "commit. Load `live-debugging-proof-harness` and `rimbridge` before the first live call, "
         "`rimworld-live-review` before the first screenshot.",
         "- Foreground commands only, each with a timeout of 540 s or less. Never `pkill -f`.",
         "- Write progress to your skeleton (`%s/SUMMARY.md`) at least every 8 minutes, and a note on your item at "
         "least every 20." % vdir, "",
         "**Wall-time bound: 3 hours.** At the bound, record where you are, release the bridge, commit, publish, and "
         "report what is owed.", "",
         "## Precondition (check first; stop if it fails)", "",
         "```",
         "python3 -c \"import json;d=json.load(open('design/concepts/%s/%s'));print(d['stage'],d['version'])\""
         % (mod, RECORD), "```", "",
         "It must print `in_game %s`. Otherwise stop, report \"%s visit %d not open on origin/main\", and do not "
         "advance it yourself." % (ver, mod, n), "",
         "## Where it runs", "",
         "The spec (§4 Stage 6, \"Which game runs what\"; his card of 2026-11-14, 18a): either game may give a bar's "
         "scripted verdict; exploring and screenshots run on Archmagi. SteveDesktop's queue admits only a stage-6 entry "
         "with a `testq` block (`src/RimMandrake/Utils/testq/pipeline_admit.py`, his 18c \"Pipeline tests only\"): "
         "%s." % ("%d of %d of this mod's checks carry one (%s); queue those with `testq.py submit` if SteveDesktop is "
                  "free, and run the rest here" % (len(f.get("testq") or []), len(checks), ", ".join(f["testq"]))
                  if f.get("testq") else "none of this mod's %d checks carries one, so this visit runs on Archmagi "
                  "through the bridge" % len(checks)), "",
         "## The bridge and the game (rules; each one binds)", ""]
    L += [r % tuple(x for x in ((purpose, seat) if "take --idle-ok" in r else (seat,) if "release" in r else
                                (mod,) if "deploy_custom_mods" in r else ()))
          for r in BRIDGE_RULES]
    L += ["", "## The checks: every stage-6 in-game check of `design/concepts/%s/version/test_table.json` (%d)"
          % (mod, len(checks)), "",
          "Run each with its exact command. Batch them: one dense prepared map holds many checks at once (the mod's own "
          "proof script builds it). %s" % ("%d need%s the full list (%s); run %s last, in one load." % (
              len(full), "s" if len(full) == 1 else "", ", ".join(full), "it" if len(full) == 1 else "those")
              if full else "None needs the full list."), ""]
    L += _check_lines(tt, checks, root)
    L += ["", "## Owed from the blind challenge%s" % (" (cycle %d, `%s`)" % (debts["cycle"], debts["record"])
                                                      if debts.get("cycle") else ": no cycle on record"), "",
          "Each of these was proved offline at most; none has run in a game. Each is a case inside the check named, "
          "or a row of its own in `rows.jsonl` (`test` = its id) when no check covers it."]
    for e in debts["fixed_problems"]:
        L.append("- Problem `%s` (bars %s), %s, never run live: run %s and show the fixed behaviour in the game (%s)."
                 % (e["id"], ", ".join(e["bars"]), e["status"], ", ".join("`%s`" % c for c in e["checks"]),
                    e["fix"][:200]))  # cut-ok: report display line
    for e in debts["scene_polish"]:
        L.append("- Polish `%s` (bars %s): %s; scene %s." % (e["id"], ", ".join(e["bars"]), e["fix"][:200],  # cut-ok: report display line
                                                           ", ".join("`%s`" % c for c in e["checks"]) or "none named"))
    for e in debts["planted_misses"]:
        L.append("- Planted fault `%s` in `%s` (`%s`), missed by every offline test (bars %s): the in-game check %s "
                 "must see it. Say in its row whether it would have." % (
                     e["id"], e.get("file"), e.get("new"), ", ".join(e["bars"]),
                     ", ".join("`%s`" % c for c in e["checks"]) or "(none decides those bars: write the case)"))
    for e in debts["items"]:
        L.append("- Item `%s`: %s" % (e["id"], e["title"]))
    for e in debts["lane1_unsettled"]:
        L.append("- Lane 1 `%s` UNSETTLED (bars %s): %s; checks %s." % (
            e["id"], ", ".join(e["bars"]), e["detail"], ", ".join("`%s`" % c for c in e["checks"]) or "none"))
    if not any(debts[k] for k in ("fixed_problems", "scene_polish", "planted_misses", "items", "lane1_unsettled")):
        L.append("- nothing read from the cycle's files")
    if debts.get("owed_text"):
        L += ["", "The cycle's SUMMARY.md, \"Owed\", as written:", ""] + ["> " + x for x in debts["owed_text"].split("\n")]
    if debts.get("unsettled_text"):
        L += ["", "Its \"Unsettled\", as written:", ""] + ["> " + x for x in debts["unsettled_text"].split("\n")]
    L += ["", "## Owed from the road back (UNRUN until this visit, `design/concepts/%s/%s`)" % (mod, UNRUN_FILE), "",
          "Each item below closed at an offline stage on its offline test; its in-game check never ran. Run each "
          "command and give it a row in `rows.jsonl`."] + unrun_lines(root, mod)
    L += ["", "## Beyond the checks", "",
          "Explore past the bars on the same maps: plentiful screenshots (`src/RimMandrake/Utils/system_screenshot.py` "
          "for the desktop, the bridge's capture for the map), looked at, not only taken. Every strange thing no bar "
          "covers is a row of `strange.jsonl`: explained (what it is and why it is fine) or filed (a rimflow item, its "
          "id in the row). Screenshots go in `%s/screenshots/` only if under 1 MB each; else name their paths." % vdir,
          "", "## A FAIL is diagnosed in the sitting", "",
          "A FAIL is not a verdict to carry home: diagnose it by experiment while the game is up (change one thing, "
          "watch the row). A small fix is made on the spot: write the offline test that fails on the old code first, "
          "then the fix, deploy, rerun the row; the rerun's row supersedes the FAIL in `rows.jsonl` (the FAIL stays as "
          "history). A fix too big for the sitting is a filed item and the row stays FAIL. Never weaken a check to "
          "pass it; a check you judge wrong is a note to the Conductor, its row UNMEASURED.", "",
          "## The record (skeleton first: create it before the first live call)", "",
          "`%s/`:" % vdir,
          "- `rows.jsonl`: one row per run: `{\"test\": id, \"verdict\": \"PASS\"|\"FAIL\"|\"UNMEASURED\", "
          "\"site_checked\": true, \"game\": \"archmagi\"|\"stevedesktop\", \"mod_sha\": <sha of the deployed source>, "
          "\"command\": ..., \"evidence\": <path>}`, and in `evidence` or beside it the active mod list parsed from "
          "that game's `ModsConfig.xml` (`activeMods`, in order) and the game build (spec: a verdict counts only on the "
          "version and list he walks).",
          "- `strange.jsonl`: as above; an empty file when nothing strange was seen.",
          "- the labelled savegame for his walk (dense, labelled scenes; spec rule 5), its path in the block.",
          "- `SUMMARY.md`: what ran, what failed and what you did about it, the owed cases one by one, then this block "
          "(the program reads it):", "",
          "```", "## Exit", "```", "ingame_rows: {%s}" % ", ".join("%s: pass|fail|unmeasured" % k for k in checks[:3])
          + (" ... every one of the %d" % len(checks) if len(checks) > 3 else ""),
          "strange_open: <count neither explained nor filed>", "savegame: <its full path>", "exit_met: true|false",
          "```", "```", "",
          "`python3 src/RimMandrake/rimflow/maturation.py next %s` reads it and checks it against the files: met needs "
          "every check pass in the block AND PASS in its last row with the site checked, the game and mod_sha named, "
          "every strange thing explained or filed, and the savegame on disk. That reading is evidence for the steward, "
          "not a move: the Conductor reads your SUMMARY.md and advances with `--to pre_human --steward-confirms "
          "\"...\"`, or sends a line item down its road back. Never run `maturation.py advance`." % mod, "",
          SELF_CHECK_RULE % mod, "",
          "## Report (10 lines or fewer, plain words)", "",
          "Tag every number [measured] or [guess ~N%%]: checks PASS of %d, FAIL, UNMEASURED; each owed case's outcome; "
          "fixes made in the sitting (shas); strange things seen, explained, filed; the savegame path; the mod list "
          "and game; whether the exit is met; bridge released; spend." % len(checks)]
    steward = (read_text(root, mod, STEWARD_FILE) or "").strip()
    ivs, undated = MN.parse_interventions(read_text(root, mod, "journal.md") or "", "journal")
    first = _ts(f.get("opened"))
    lines = [iv for iv in ivs if iv["at"] is not None and (iv["stage"] == "6" or (first and iv["at"] >= first))]
    L += ["", "## Steward's decisions", "",
          "The Conductor's decisions as steward carry the owner's authority; record each one you act on with "
          "`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`.", ""]
    if lines:
        L += ["- %s (stage %s, kind %s): %s" % (pac_heading(iv["at"]), iv["stage"], iv["kind"], iv["what"])
              for iv in lines]
    if steward:
        L += ["", "From `design/concepts/%s/%s`:" % (mod, STEWARD_FILE), "", steward]
    if not lines and not steward:
        L.append(INGAME_DEFAULT)
    L += ["", "## Defects in the pipeline itself", "", SELF_FIX_RULE]
    return "\n".join(L) + "\n", f


# ---- the command line ------------------------------------------------------------------------------------------------

def versioned(root):
    croot = os.path.join(root, "design", "concepts")
    return sorted(f for f in os.listdir(croot) if not f.startswith("_")
                  and os.path.exists(os.path.join(croot, f, "version", "VERSION.json"))) if os.path.isdir(croot) else []


def print_refusal(res):
    print("REFUSED: %s to %s" % (label(res["from"]), label(res["to"]) if res["to"] in WORDS else res["to"]))
    for r in res["verdict"]["refusals"]:
        print("- %s: %s" % (r["clause"], r["observed"]))
        print("  would pass: %s" % r["would_pass"])
        print("  smallest fix (%s, %s): %s" % (r["smallest_fix"]["cost"], "attainable" if
                                              r["smallest_fix"]["attainable"] == "yes" else "not attainable",
                                              r["smallest_fix"]["what"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description="The Maturation Pipeline's spine: stage record, next step, advance.")
    ap.add_argument("--root", default=REPO)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("seed")
    s.add_argument("mods", nargs="*")
    s.add_argument("--no-live", action="store_true")
    for c in ("show", "next"):
        p = sub.add_parser(c)
        p.add_argument("mod")
        p.add_argument("--json", action="store_true")
    a = sub.add_parser("advance")
    a.add_argument("mod")
    a.add_argument("--to", required=True, choices=WORDS)
    a.add_argument("--by", required=True)
    a.add_argument("--why", required=True)
    a.add_argument("--steward-confirms")
    a.add_argument("--conductor-decision")
    a.add_argument("--owner-said")
    a.add_argument("--per-ruling", help="CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: the Conductor's instruction, carried as his words; --why holds its text")
    a.add_argument("--waits-on")
    a.add_argument("--game-only", help="ID[,ID...]: back to in_game from an offline stage; every named road-back item "
                                       "is open and needs the live game")
    a.add_argument("--json", action="store_true")
    u = sub.add_parser("unrun", help="record a road-back item's in-game check UNRUN for Stage 6 (it closed offline)")
    u.add_argument("mod")
    u.add_argument("--item", required=True)
    u.add_argument("--check", required=True, help="the test table's stage-6 check id")
    u.add_argument("--command", required=True, help="its exact live command")
    u.add_argument("--offline", required=True, help="the offline test it closed on")
    u.add_argument("--sha", required=True, help="the sha that test is green at")
    u.add_argument("--by", default="BENCH")
    g = sub.add_parser("gate", help="read-only: exit 0 when the move refuses nothing but its hand steps (a launch check)")
    g.add_argument("mod")
    g.add_argument("--to", required=True, choices=WORDS)
    p = sub.add_parser("lock-bars", help="record the locked version's bar ids (version/locked_bars.json)")
    p.add_argument("mod")
    p.add_argument("--by", required=True)
    p.add_argument("--why", required=True)
    p.add_argument("--add", action="append", default=[], help="a bar his card added (needs --source)")
    p.add_argument("--remove", action="append", default=[], help="a bar his card moved out (needs --source)")
    p.add_argument("--source", help="OWNER:<tsn>, his card that changed the bars")
    p = sub.add_parser("next-version")
    p.add_argument("mod")
    p.add_argument("--by", required=True)
    p.add_argument("--why", required=True)
    p = sub.add_parser("spend")
    p.add_argument("mod")
    p.add_argument("--stage", required=True, choices=WORDS)
    p.add_argument("--tokens", type=int, required=True)
    p.add_argument("--usd", type=float)
    p.add_argument("--wall-s", type=float)
    p.add_argument("--source", required=True)
    p.add_argument("--estimate", action="store_true")
    b = sub.add_parser("brief")
    b.add_argument("mod")
    b.add_argument("--out", help="write the brief here (default: print it)")
    c = sub.add_parser("certificate", help="read-only unless --run: exit 0 when every bar's offline deciders are "
                       "registered, ran on this build and green (PRE_JUDGEMENT_CERTIFICATE)")
    c.add_argument("mod")
    c.add_argument("--to", default="blind_challenge", choices=WORDS)
    c.add_argument("--run", action="store_true", help="rerun the offline deciders first and stamp their build (no tokens)")
    c.add_argument("--resume", action="store_true", help="with --run: keep a decider already green on its current build "
                   "and command (a rerun killed part way picks up where it stopped)")
    c.add_argument("--json", action="store_true")
    la = sub.add_parser("launch")
    la.add_argument("mod")
    la.add_argument("--budget-usd", type=float, required=True, help="the spend cap; required, no default")
    la.add_argument("--item", required=True, help="the ledger item the run works under (filed on origin/main)")
    la.add_argument("--model", default="opus", choices=("fable", "opus", "sonnet"))
    la.add_argument("--seat", default="BENCH")
    o = ap.parse_args(argv)
    root = os.path.abspath(o.root)

    if o.cmd == "seed":
        mods = o.mods or versioned(root)
        gathered = None
        if not o.no_live:
            gathered = MN.gather(root, live=True)
        bad = 0
        for mod in mods:
            try:
                rec, made = seed_mod(root, mod, live=not o.no_live, gathered=gathered)
            except ValueError as e:
                print("NOT SEEDED %s" % e)
                bad += 1
                continue
            print("%s %s %s: %s, since %s" % ("SEEDED" if made else "KEPT  ", mod, rec["version"],
                                              label(rec["stage"]), rec["since"]))
        return 1 if bad else 0
    if o.cmd == "show":
        rec = load(root, o.mod)
        if rec is None:
            print("%s: no stage record (maturation.py seed %s)" % (o.mod, o.mod))
            return 1
        if o.json:
            print(dump(rec), end="")
            return 0
        print("%s %s: %s since %s; blind cycles %s; arrivals at the pre-human check %s; moves %d"
              % (o.mod, rec["version"], label(rec["stage"]), rec["since"], rec.get("cycles"),
                 rec.get("pre_human_arrivals"), len(rec.get("moves") or [])))
        for st, t in spend_by_stage({"spend": spend_rows(root, o.mod, rec)}).items():
            # weighted tokens only (the owner, 2026-11-16: "Please speak in terms of weighted tokens not money.")
            print("  spend %s: %s weighted tokens, %s s wall, %d entries (%d estimates, %d unmeasured fields)"
                  % (" + ".join(label(x) for x in st.split("+")), t["tokens"], round(t["wall_s"]), t["entries"],
                     t["estimates"], t["unmeasured"]))
        return 0
    if o.cmd == "next":
        nx = next_step(root, o.mod)
        rd, rp = dispatch_reading()
        ov = dispatch_overlay(o.mod, nx["next"], rd, rp, time.time())
        nx["next"] = ov.pop("next")
        nx["dispatch"] = ov
        if o.json:
            print(json.dumps(nx, indent=2, ensure_ascii=False))
            return 0
        print("%s %s: %s since %s; next stage %s" % (o.mod, nx.get("version", UNM), nx.get("stage_label", nx["stage"]),
                                                     nx.get("since", UNM), label(nx.get("to", UNM))))
        if nx.get("passed"):
            print("  exit tests passing: %s" % ", ".join(nx["passed"]))
        for r in nx["refusals"]:
            print("  refused %s: %s" % (r["clause"], r["observed"]))
        b = nx.get("blind")
        if b and b.get("exit"):
            print("  blind cycle %s (visit %s, total %s): exit %s: %s" % (b.get("cycle"), b.get("visit"), b.get("total"),
                                                                       b["exit"]["state"], "; ".join(b["exit"]["why"])
                                                                       or "no record yet"))
        g = nx.get("ingame")
        if g and g.get("exit"):
            print("  in-game visit %s: %d stage-6 checks (%d with a testq block); exit %s: %s" % (
                g.get("visit"), len(g.get("checks") or []), len(g.get("testq") or []), g["exit"]["state"],
                "; ".join(g["exit"]["why"][:4]) or "no record yet"))
        print("  launch: %s" % nx.get("launch", "none"))
        print(ov["line"])
        print(nx["next"])
        return 0
    if o.cmd == "advance":
        if load(root, o.mod) is None:
            print("REFUSED: %s has no stage record; run maturation.py seed %s first" % (o.mod, o.mod))
            return 1
        res = advance(root, o.mod, o.to, by=o.by, why=o.why, steward=o.steward_confirms,
                      conductor=o.conductor_decision, owner=o.owner_said or (("per-ruling %s: %s" % (o.per_ruling, o.why)) if o.per_ruling else None), waits_on=o.waits_on,
                      game_only=[x.strip() for x in (o.game_only or "").split(",") if x.strip()] or None)
        if res.get("malformed"):
            print("MALFORMED REFUSAL (a bug in maturation.py): %s" % "; ".join(res["malformed"]))
            return 3
        if o.json:
            v = dict(res["verdict"])
            v["given"] = {"criteria": v["given"]["criteria"], "inputs": sorted(v["given"]["inputs"])}
            print(json.dumps({"ok": res["ok"], "verdict": v}, indent=2, ensure_ascii=False))
        elif res["ok"]:
            print("ADVANCED %s: %s to %s; journal and %s written" % (o.mod, label(res["from"]), label(o.to), RECORD))
        else:
            print_refusal(res)
        return 0 if res["ok"] else 1
    if o.cmd == "unrun":
        try:
            r = record_unrun(root, o.mod, o.item, o.check, o.command, o.offline, o.sha, by=o.by)
        except ValueError as e:
            print("REFUSED: %s" % e)
            return 2
        print("UNRUN %s %s: %s (closed offline on %s at %s); listed in %s" % (o.mod, r["check"], r["command"],
                                                                             r["offline"], r["sha"], UNRUN_FILE))
        return 0
    if o.cmd == "gate":     # GATE_FIRST (RIMMANDRAKE_RUN_LAUNCH_CHECKS_FIVE_STEWARDS_HIT_GATES): writes nothing
        if load(root, o.mod) is None:
            print("REFUSED: %s has no stage record; run maturation.py seed %s first" % (o.mod, o.mod))
            return 1
        res = evaluate(root, o.mod, o.to)
        prog = [r for r in res["verdict"]["refusals"] if r["clause"] not in res["hand_steps"]]
        if not prog:
            print("GATE OPEN %s: %s to %s%s" % (o.mod, label(res["from"]), label(o.to), "; the steward supplies: %s"
                                               % ", ".join(res["hand_steps"]) if res["hand_steps"] else ""))
            return 0
        print_refusal(dict(res, verdict=dict(res["verdict"], refusals=prog)))
        return 1
    if o.cmd == "certificate":
        ran = None
        if o.run:
            t0 = time.time()
            ran = JC.run_offline(root, o.mod, resume=o.resume)
            ran["wall_s"] = round(time.time() - t0, 1)
        cv = certificate(root, o.mod, o.to)
        if o.json:
            print(json.dumps(dict(cv, run=ran), indent=2, ensure_ascii=False))
        else:
            if ran is not None:
                print("RAN %s: %d offline tests in %.1f s%s%s" % (o.mod, ran["ran"], ran["wall_s"], (
                    "; kept %d already green on this build" % ran["skipped"]) if ran.get("skipped") else "", (
                    "; failed: %s" % ", ".join(ran["failed"])) if ran["failed"] else "") + (
                    "; %s" % ran["error"] if ran.get("error") else ""))
            JC.print_certificate(cv)
        return 0 if cv["ok"] else 1
    if o.cmd == "lock-bars":
        r = lock_bars(root, o.mod, o.by, o.why, o.add, o.remove, o.source)
        print(("LOCKED BARS %s: %d recorded in %s (%s)" % (o.mod, len(r["ids"]), rel(o.mod, LOCKED_BARS), r["why"]))
              if r["ok"] else "REFUSED: %s" % r["why"])
        return 0 if r["ok"] else 2
    if o.cmd == "next-version":
        r = next_version(root, o.mod, o.by, o.why)
        print(("NEXT VERSION %s: %s -> %s, at %s (old record kept as %s)" % (o.mod, r["from"], r["to"], label(r["stage"]),
                                                                           r["kept"])) if r["ok"] else
              "REFUSED: %s" % r["why"])
        return 0 if r["ok"] else 2
    if o.cmd == "spend":
        add_spend(root, o.mod, o.stage, o.tokens, o.usd, o.wall_s, o.source, o.estimate)
        print("SPEND %s %s: %d tokens recorded" % (o.mod, label(o.stage), o.tokens))
        return 0
    if o.cmd == "brief":
        text, _ = brief_text(root, o.mod)
        if o.out:
            with open(o.out, "w", encoding="utf-8") as fh:
                fh.write(text)
            print("BRIEF %s written to %s" % (o.mod, o.out))
        else:
            sys.stdout.write(text)
        return 0
    if o.cmd == "launch":
        rc, text, _ = launch_mod(root, o.mod, o.budget_usd, o.item, model=o.model, seat=o.seat)
        print(text)
        return rc
    return 2


if __name__ == "__main__":
    sys.exit(main())
