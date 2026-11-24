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
import inspect
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
import raid_pause as RP          # noqa: E402  raid tests are paused (owner, 2026-11-23)
import scene_size as SZ          # noqa: E402  an oversized live scene carries its evidence (owner, 2026-11-24)
import live_kinds as LK          # noqa: E402  the kinds of a live scene and the outcomes of its runs
import refusal_contract as RC   # noqa: E402
import judge_certificate as JC   # noqa: E402  the pre-judgement certificate (PRE_JUDGEMENT_CERTIFICATE)
import own_cgroup               # noqa: E402  a history read is file cache outside the tick's memory limit
import build_match as BM         # noqa: E402  the Stage 6 exit's build match (owner, 2026-11-17)

UNM = "UNMEASURED"
RECORD = "version/stage_record.json"
# his Evidence-for-Ask ruling (2026-11-15): a new mod's first Design Version is 0.1.0 unless recorded evidence says
# otherwise, and the pipeline locks it itself (locked_by "pipeline", per_ruling this id)
EVIDENCE_FOR_ASK = "RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME"
# RIMMANDRAKE_COUNT_ADVANCE_REFUSALS_SO_A_LOOP_RINGS: the one brief `advance` judges with, and the row
# infrastructure/state/judge_calibration.json carries for it. ALARM-ONLY (RIMMANDRAKE_TUNE_ADVANCE_REFUSAL_ALARM_BLOCKS_
# NOTHING_AS_CODED): a trip tells the Conductor; `advance` never asks refusal_contract.may_judge, so it blocks nothing.
# Its counts run in a rolling 24 h and skip hand steps waiting on a person (refusal_contract.FAMILY_TUNING)
ADVANCE_FAMILY = "maturation_advance"
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
    ("pre_human", "7", "Stage 7", "Walk brief", "Stage 7, the walk brief"),
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
# Stage 7 has none: it writes his walk brief and judges nothing (owner, 2026-11-17, RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_
# BRIEF_NO_VETO); what it notices goes into the brief or onto a ticket.
ROADS_BACK = {
    "preflight": ("designer",),
    "blind_challenge": ("blind_challenge",),
    # in_game -> in_game: a failed line only the game can show stays Stage 6 work and opens the next visit (spec Stage 6
    # road back, "the lowest stage that can show the fault"; RIMMANDRAKE_CLOSE_OFFLINE_STAGE_ITEMS_OFFLINE_GAME_WAS_DEMANDED)
    "in_game": ("offline_build", "blind_challenge", "in_game"),
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


# The token unit of a spend row is role_launch.stored_unit's, the one reader of a stored figure's unit
# (design/specs/2026-11-22-run-spend-and-model-alias/boundary.md).
TOKEN_UNIT = "weighted_v2"
UNSTATED = "unstated"


def row_unit(row):
    """-> the token unit of a spend row: its token_unit, else weighted_v1 (role_launch.stored_unit)."""
    import role_launch as RL
    return RL.stored_unit(row)


def _spend_row(r, stages):
    """One detached run (a maturation_now run view, which carries its record's token_unit) -> its spend entry, under
    the stage words it worked in, in its run's own unit (row_unit)."""
    usd = r.get("usd") if isinstance(r.get("usd"), (int, float)) else r.get("said_usd")
    return {"stage": stages[0], "stages": stages, "token_unit": row_unit(r),
            "model": r.get("model") or UNM, "tokens": r.get("tokens") if isinstance(
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


def _designer_seed_row(v, mod):
    """VERSION.json's tokens_spent -> the seed's designer spend row, in the unit VERSION.json names, else unstated (the
    Designer's stage.json budget names no unit)."""
    u = v.get("token_unit")
    return {"stage": "designer", "stages": ["designer"], "tokens": v["tokens_spent"],
            "token_unit": u if isinstance(u, str) and u else UNSTATED, "usd": UNM,
            "wall_s": UNM, "source": rel(mod, "version/VERSION.json") + " tokens_spent",
            "kind": "mixed: measured and estimated charges, see VERSION.json measured_from"}


def seed_mod(root, mod, live=True, gathered=None):
    """-> (record, made). An existing record is returned untouched (made False): seeding never retypes state. One that
    exists but cannot be read raises ValueError and is left as it is
    (RIMMANDRAKE_KEEP_UNREADABLE_RECORD_WHEN_SEEDING_SAYS_NEVER)."""
    have = load(root, mod)
    if have is not None:
        return have, False
    if not _absent(os.path.join(mod_dir(root, mod), RECORD)):
        raise ValueError("%s: %s exists or cannot be looked at, and cannot be read; seeding writes over no record"
                         % (mod, rel(mod, RECORD)))
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
        rec["spend"].append(_designer_seed_row(v, mod))
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
PASS_RECORD_DIR = "version/passes"          # <version>.json, written once by the move to passed (spec section 3.7)


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


def _str_head(node):
    """-> (the literal text a message expression starts with, whether that is the whole message), or None: "x", f"x{y}",
    "x" + "y", "x" + y, "x %s" % y, "x{}".format(y). Any other expression has no known head."""
    import ast
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value, True
    if isinstance(node, ast.JoinedStr):
        acc = ""
        for v in node.values:
            if not (isinstance(v, ast.Constant) and isinstance(v.value, str)):
                return acc, False
            acc += v.value
        return acc, True
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _str_head(node.left)
        if left is None or not left[1]:
            return left
        right = _str_head(node.right)
        return (left[0] + right[0], right[1]) if right else (left[0], False)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        left = _str_head(node.left)
        return (left[0].split("%")[0], False) if left else None
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format":
        left = _str_head(node.func.value)
        return (left[0].split("{")[0], False) if left else None
    return None


def _is_missing_tool(node):
    """True when the raise's first message argument provably starts "MISSING TOOL"."""
    import ast
    if not isinstance(node, ast.Call):
        return False
    args = list(node.args) + [k.value for k in node.keywords]
    head = _str_head(args[0]) if args else None
    return bool(head) and head[0].lstrip().startswith("MISSING TOOL")


def _missing_tool_scan(path):
    """-> ({function key: [line of each `raise ...("MISSING TOOL...")` in its own body]}, {function key: keys it calls}),
    read with ast, nothing imported or run; raises OSError/SyntaxError/ValueError when the file cannot be read. A key is a
    module-level function's name (or a nested one's "outer.inner"); an edge is a name called, or passed to a call as a
    callback, that resolves to a nested function in scope or a module-level one. A lambda's body is its enclosing
    function's; a class body is not read. A module-level `name = f(..., helper)` is a key whose edges are its arguments."""
    import ast
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=path)
    fdefs = (ast.FunctionDef, ast.AsyncFunctionDef)
    top = {n.name for n in tree.body if isinstance(n, fdefs)}
    raises, edges = {}, {}

    def named(call):
        return [x.id for x in [call.func] + list(call.args) + [k.value for k in call.keywords] if isinstance(x, ast.Name)]

    def visit(fn, key, scope):
        local, nested, lines, calls = dict(scope), [], [], set()
        a = fn.args     # a parameter or a local binding shadows a module-level function of that name
        bound = {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs + [a.vararg, a.kwarg] if x is not None}
        stack = list(ast.iter_child_nodes(fn))
        while stack:
            n = stack.pop()
            if isinstance(n, fdefs):
                nested.append(n)
                local[n.name] = key + "." + n.name
                continue
            if isinstance(n, ast.ClassDef):
                continue
            if isinstance(n, ast.Raise) and _is_missing_tool(n.exc):
                lines.append(n.lineno)
            if isinstance(n, ast.Call):
                calls.update(named(n))
            elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                bound.add(n.id)
            stack.extend(ast.iter_child_nodes(n))
        raises[key] = lines
        edges[key] = {local.get(c) or (c if c in top and c not in bound else None) for c in calls} - {None}
        for n in nested:
            visit(n, local[n.name], local)

    for n in tree.body:
        if isinstance(n, fdefs):
            visit(n, n.name, {})
        elif isinstance(n, ast.Assign) and isinstance(n.value, ast.Call):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id not in raises:
                    raises[t.id], edges[t.id] = [], {c for c in named(n.value) if c in top}
    return raises, edges


def undeclared_stops(root, mod, tt, ended=None):
    """-> {bar id: [reason, ...]} for bars an in-game scene decides whose entry (or a function of the same file it reaches
    by name) raises "MISSING TOOL..." with no open owed_parts_item in scenes.json to say so: the scene stops at a missing
    probe, so its check cannot run (RIMMANDRAKE_REFUSE_MISSING_TOOL_SCENES_GRAFFITI_READS_READY). A scene whose declared
    item is open is owed_scene_parts' to count; one whose every item is in `ended` (default: the ledger) with the raise
    still there is listed. Only .py entry files are read. A file that cannot be read or parsed is reported under
    "__did_not_run__" and lists no bar."""
    tests = tt.get("tests") if isinstance(tt, dict) else None
    if not isinstance(tests, dict) or not tests:
        return {}
    sc, serr = read_json(root, mod, "scenes.json")
    if serr and serr != "no file":     # the declarations could not be read: an absent owed item is not established
        return {"__did_not_run__": ["%s: %s" % (rel(mod, "scenes.json"), serr)]}
    owes = {}
    for s in (sc.get("scenes") if isinstance(sc, dict) else None) or []:
        v = s.get("owed_parts_item") if isinstance(s, dict) else None
        ids = [v] if isinstance(v, str) else [x for x in v if isinstance(x, str)] if isinstance(v, list) else []
        if ids and s.get("id"):
            owes[s["id"]] = ids
    if ended is None:
        ended = ledger_ended(root, {i for ids in owes.values() for i in ids})
    scans, stops, dnr = {}, {}, []
    for tid, t in sorted(tests.items()):
        if not isinstance(t, dict) or not t.get("file") or not t.get("entry") or not str(t["file"]).endswith(".py"):
            continue    # a C# proof method or a look is no Python scene this scan reads
        f = t["file"]
        if f not in scans:
            try:
                scans[f] = _missing_tool_scan(os.path.join(root, f))
            except (OSError, SyntaxError, ValueError) as e:
                scans[f] = None
                dnr.append("%s: %s" % (f, type(e).__name__ if not str(e) else str(e).splitlines()[0][:160]))
        if scans[f] is None:
            continue
        raises, edges = scans[f]
        seen, todo, lines = set(), [t["entry"]], []
        while todo:
            n = todo.pop()
            if n in seen or n not in raises:
                continue
            seen.add(n)
            lines += raises[n]
            todo += sorted(edges.get(n, ()))
        if not lines:
            continue
        where = "%s:%d stops at MISSING TOOL" % (f, min(lines)) + (
            " (and %d more)" % (len(set(lines)) - 1) if len(set(lines)) > 1 else "")
        items = owes.get(tid, [])
        if not items:
            stops[tid] = "%s; declare owed_parts_item in scenes.json or build the probe" % where
        elif all(i in ended for i in items):
            stops[tid] = "%s; its owed item %s is closed but the raise remains" % (where, ", ".join(items))
    out = {}
    for b in tt.get("bars") or []:
        if isinstance(b, dict) and b.get("id"):
            why = ["%s: %s" % (d, stops[d]) for d in b.get("decides") or [] if d in stops]
            if why:
                out[b["id"]] = why
    if dnr:
        out["__did_not_run__"] = dnr
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


CONDUCTOR_ACTS = "RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS"     # = conductor_acts.RULING


def _conductor_lock_problem(root, v):
    """None when VERSION.json's lock is the Conductor window's act (owner 2026-11-19, conductor_acts.lock_problem)."""
    import concept_tree as CT
    import conductor_acts as CA
    return CA.lock_problem(v, CT.owner_events(root, REPO))


def owner_event(root, owner, may_refuse_pass=False):
    """RIMMANDRAKE_REQUIRE_OWNER_EVENT_TO_PASS: --owner-said for a pass is OWNER:<tsn>, an event of his on the OWNER
    shard carrying byCard or ownerSaid that does not refuse the pass. -> (event, observed) or (None, why not).
    may_refuse_pass: the event ends a walk that did not pass (walk_result), so words refusing the pass are his answer."""
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
    if PASS_REFUSED.search(words) and not may_refuse_pass:
        return None, "OWNER:%s's words refuse the pass: %r" % (m.group(1), words[:80])
    return ev, "OWNER:%s: %s" % (m.group(1), words[:80])


def _record_time(root, mod, base):
    """-> the newest time the evidence under base (a cycle or visit folder) was written: its last commit, or the mtime of
    a file of it git sees changed or new; None when nothing can be read. A reading is as new as its newest file."""
    d = os.path.join(mod_dir(root, mod), base)
    if not os.path.isdir(d):
        return None
    times = []
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%ct", "--", "."], cwd=d, capture_output=True, text=True,
                           timeout=60)
        if r.returncode == 0 and r.stdout.strip().isdigit():
            times.append(float(r.stdout.strip()))
        st = subprocess.run(["git", "status", "--porcelain", "-z", "--untracked-files=all", "--", "."], cwd=d,
                            capture_output=True, timeout=60)
        if st.returncode != 0:
            raise OSError("git status rc %s" % st.returncode)
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=d, capture_output=True, text=True, timeout=60)
        for e in st.stdout.decode("utf-8", "surrogateescape").split("\0"):
            fp = os.path.join(top.stdout.strip(), e[3:]) if len(e) > 3 else None
            if fp:      # a changed file counts at its mtime; one deleted (or unreadable) since, at this moment
                times.append(_mtime_or_now(fp))
    except (OSError, subprocess.SubprocessError):     # no git here: every file's mtime, the newest counts
        times = [_mtime_or_now(os.path.join(a, f)) for a, _, fs in os.walk(d) for f in fs]
    return max(times) if times else None


def _mtime_or_now(fp):
    try:
        return os.path.getmtime(fp)
    except OSError:
        return time.time()


def exit_met_clause(root, mod, rec, cur, owner, clause, rec_ref, req_ref, game_only_bars=None):
    """RIMMANDRAKE_BIND_ADVANCE_TO_EXIT_READINGS: a forward move out of the blind challenge or the in-game stage needs
    the program's exit reading met (read_exit of the current cycle, read_ingame_exit of the current visit) with nothing
    blocking it; a steward's word alone no longer moves a mod past either. The only override is his OWNER event
    (--owner-said OWNER:<tsn>) newer than the reading it overrides (the newest of the cycle or visit's opening and its
    evidence files). A reading that cannot be made is not met; a reader that is itself wrong is repaired, never waved
    past. game_only_bars ({bar: [item ids]}, given only when the move is game-only and its `game_only` clause passed)
    reads the blind exit the game-only way (read_exit; RIMMANDRAKE_UNBLOCK_GAME_ONLY_ADVANCE_AT_BLIND_EXIT)."""
    tt, terr = read_json(root, mod, "version/test_table.json")
    blocked = [] if tt is not None else ["version/test_table.json: %s" % terr]
    try:
        if cur == "blind_challenge":
            bf = blind_facts(root, mod)
            n, ex, opened = bf.get("cycle"), bf.get("exit") or {}, bf.get("opened")
            blocked += [b for b in bf.get("blocked") or [] if not b.startswith("version/test_table.json")]
            if bf.get("owed") == "resume":
                blocked.append(void_resume_text(bf))
            if game_only_bars is not None and n is not None:
                ex = read_exit(root, mod, n, tt, game_only_bars=game_only_bars)
            what, reader, base = "blind cycle %s" % n, "read_exit", "%s/cycle_%s" % (BLIND_DIR, n)
        else:
            n = max(1, len(ingame_openings(rec)))
            ex, opened = read_ingame_exit(root, mod, n, tt), ingame_openings(rec).get(n)
            what, reader, base = "in-game visit %d" % n, "read_ingame_exit", "%s/visit_%d" % (INGAME_DIR, n)
    except Exception as e:  # noqa: BLE001  evidence the reader cannot parse: no reading, so not met
        n, ex, opened, base = None, {"state": "unreadable", "why": ["the exit reader raised %s: %s" % (
            type(e).__name__, str(e)[:200])]}, None, None
        what, reader = "the %s exit" % cur, "the exit reader"
    met = ex.get("state") == "met" and not blocked
    over, ohow = None, "none in the request"
    if not met and owner:
        ev, ohow = owner_event(root, owner)
        t_ev = int(ev["tsn"]) / 1e9 if ev is not None and str(ev.get("tsn") or "").isdigit() else None
        try:
            t_rec = _record_time(root, mod, base) if base else None
        except Exception:  # noqa: BLE001  the evidence's time cannot be read: then nothing can be shown older
            t_rec = time.time()
        t_read = [t for t in (_ts(opened), t_rec) if t is not None]
        if ev is not None and t_ev is None:
            ohow = "%s; its time cannot be read, so it cannot be shown newer than %s's reading" % (ohow, what)
        elif ev is not None and not t_read:     # no opening and no evidence: no dated reading for his word to predate
            over, ohow = ev, "%s (%s has no dated evidence)" % (ohow, what)
        elif ev is not None and t_ev <= max(t_read):
            ohow = "%s; it predates %s's reading (newest evidence %s)" % (
                ohow, what, dt.datetime.fromtimestamp(max(t_read), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        else:
            over = ev
    clause("exit_met", "the stage's exit reading (%s, a program check) is met with nothing blocking it, or his OWNER "
           "event newer than that reading overrides it" % reader, met or over is not None, [rec_ref, req_ref],
           observed="%s exit %s: %s%s; owner override: %s" % (what, ex.get("state"), "; ".join(
               (ex.get("why") or [])[:3]) or "no reading", "; blocked: %s" % "; ".join(blocked) if blocked else "",
               ohow),
           would_pass="maturation.py next %s reads %s's exit met, or --owner-said OWNER:<tsn> naming his event newer "
                      "than its reading" % (mod, what),
           fix="work the reading's listed gaps through the stage's own road (a new cycle or visit); a reader that is "
               "wrong is repaired as a Convergent fix of the reader", cost="rerun",
           why_sound="decision of 2026-11-15 under RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME: a "
                     "not-met exit goes back, it does not go forward (spec section 4, his Stage 4/5 words)")


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
    walk_id = None                  # the walk build a pass was validated on: advance() writes exactly this reading
    revision = (rec.get("stage"), rec.get("version"), len(rec.get("moves") or []))     # what was evaluated

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
    # Stage 7 judges nothing and has no road back of its own; a check that a landed change owes a game sends it back to
    # Stage 6 (design/specs/2026-11-24-walk-owes-its-checks/boundary.md)
    wo = walk_owed(root, mod, rec) if cur == "pre_human" and to in ("his_walk", "in_game") else None
    back = back or bool(wo and wo["owed"] and to == "in_game")
    nxt = WORDS[i_cur + 1] if 0 <= i_cur < len(WORDS) - 1 else None
    clause("order", "a mod moves forward one stage at a time, or back only along a road the spec draws",
           forward or back, [req_ref, rec_ref],
           observed="asked %s to %s; the record stands at %s" % (cur, to, cur),
           would_pass="advance --to %s (the next stage)%s" % (nxt or "nothing", (" or back to " + ", ".join(
               ROADS_BACK[cur])) if cur in ROADS_BACK else ""),
           fix="run advance with --to %s, finishing %s first" % (nxt or cur, label(cur)),
           why_sound="the eight stages, their order and the roads back are his and carried rulings (spec §3)")
    go_bars = None      # {bar: [item ids]} once the game_only clause below passes; the blind exit reads it (read_exit)
    if game_only and to == "in_game" and cur in OFFLINE_STAGES:
        ids = [str(i) for i in game_only]
        need, ended = ledger_needs(root, ids), ledger_ended(root, ids)
        offline = [i for i in ids if need.get(i) not in LIVE_NEEDS]
        shut = [i for i in ids if i in ended]
        was6 = any(m.get("from") == "in_game" for m in rec.get("moves") or [])
        # every open sibling (same caused_by) is named: an offline item of the same road back keeps the record here
        unnamed = [x["id"] for x in ledger_items_caused_by(root, sorted(set(ledger_caused_by(root, ids).values())))
                   if x["id"] not in ids]
        go_ok = bool(ids) and not offline and not shut and not unnamed and was6
        if go_ok:
            go_bars = bars_named_by(root, mod, ids)
        clause("game_only", "every item the move names is open and needs the live game (ledger needs game-up or "
               "bridge), it names every open item of its road back, and the record came to this stage from Stage 6",
               go_ok, [req_ref, rec_ref],
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
               "mods, delegation_policy.md §1 and Evidence-for-Ask; the Conductor also decides current or next at filing, "
               "card 2026-11-23), "
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
                by_ == "pipeline" and (v or {}).get("per_ruling") == EVIDENCE_FOR_ASK) or (
                by_ == "conductor" and _conductor_lock_problem(root, v) is None))
            clause("locked", "the Design Version is locked (VERSION.json state locked, by him or by the pipeline "
                   "under the Evidence-for-Ask ruling)",
                   lk, [rel(mod, "version/VERSION.json")],
                   observed="VERSION.json state is %s, locked_by %s" % (st or UNM, by_ or UNM),
                   would_pass="VERSION.json state reads locked, locked_by owner (his words in owner_words), "
                              "locked_by pipeline with per_ruling %s, or locked_by conductor with per_ruling %s and "
                              "conductor_event OWNER:<tsn> (the Conductor window's act, owner 2026-11-19)"
                              % (EVIDENCE_FOR_ASK, CONDUCTOR_ACTS),
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
            stops, stops_dnr = {}, []
            if isinstance(bad, list):
                bad = [x for x in bad if x not in walk]
                live_red = live_known_red_owed(root, tt, bad)
                bad = [x for x in bad if x not in live_red]
                owed = {b: i for b, i in owed_scene_parts(root, mod, tt).items() if b not in bad}
                bad += sorted(owed)
                stops = undeclared_stops(root, mod, tt)
                stops_dnr = stops.pop("__did_not_run__", [])
                bad += sorted(b for b in stops if b not in bad)
            owed_txt = ("; the table flags these runnable but a deciding scene in scenes.json still owes script parts "
                        "to an open item: %s" % "; ".join("%s (%s)" % (b, ", ".join(i)) for b, i in sorted(owed.items()))
                        ) if owed else ""
            owed_txt += ("; a deciding scene stops at MISSING TOOL with no open owed item: %s"
                         % "; ".join("%s (%s)" % (b, " | ".join(r)) for b, r in sorted(stops.items()))) if stops else ""
            owed_txt += ("; the MISSING TOOL scan did not run on %s" % "; ".join(stops_dnr)) if stops_dnr else ""
            owed_txt += ("; counted runnable, UNRUN and owed to Stage 6 (a live known red with its fix landed): %s"
                         % "; ".join("%s (%s)" % (b, ", ".join("%s: %s %s" % x for x in r))
                                     for b, r in sorted(live_red.items()))) if live_red else ""
            clause("every_bar_has_a_check_that_runs", "every bar has every deciding check runnable "
                   "(an in-game scene may be UNRUN with its command, not with its script parts still owed)",
                   isinstance(bad, list) and not bad,
                   [tref] + ([rel(mod, "scenes.json")] if owed or stops else []),
                   observed=("%d of %d bars not runnable: %s%s" % (len(bad), n, ", ".join(bad), owed_txt))
                   if isinstance(bad, list) else "test_table.json: %s" % n,
                   would_pass="a test table whose every bar reads every_decider_runnable_today true",
                   fix="build the missing checks or scene entries for the listed bars, then remake the test table" + (
                       "; for a scene that owes script parts, work and close the owed item (%s)"
                       % ", ".join(sorted({i for ids in owed.values() for i in ids})) if owed else "") + (
                       "; for a scene that stops at MISSING TOOL, build the probe and drop the raise, or name its "
                       "probe ticket as the scene's owed_parts_item in scenes.json" if stops else ""),
                   cost="new instrument",
                   why_sound="the lock rule (his, by agreement 2026-11-14): no mod moves past Stage 3 until every bar "
                             "has a check that runs")
            if stops_dnr and passed and passed[-1]["clause"] == "every_bar_has_a_check_that_runs":
                passed[-1]["did_not_run"] = "the MISSING TOOL scan did not run on %s" % "; ".join(stops_dnr)
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
        elif cur in ("blind_challenge", "in_game"):
            hand.append("steward_confirms")
            what = {"blind_challenge": "the blind judge's cycle record (maturation.py next reads its exit block; "
                                       "the exit itself is a proposal)",
                    "in_game": "the visit's in-game record (maturation.py next reads its exit block; the exit "
                               "itself is carried plus a proposal)"}[cur]
            clause("steward_confirms", "the steward has read %s and says the stage's exit is met" % what,
                   bool(steward), [req_ref], observed="steward_confirms: none in the request",
                   would_pass="--steward-confirms naming the run and the verdict read",
                   fix="the Conductor reads the stage's evidence and passes --steward-confirms", cost="owner",
                   why_sound="the stage's exit is not settled as a program check (plan section 3)")
            if forward:
                exit_met_clause(root, mod, rec, cur, owner, clause, rec_ref, req_ref, game_only_bars=go_bars)
            if cur == "in_game":
                # the BUILD MATCH (owner, 2026-11-17, narrowed 2026-11-21): a row counts on the build he walks when its
                # game build and list match and the change since its commit touches nothing its check reads or
                # exercises (rerun_relation.py); only the touched checks run again (build_match.py, read by
                # read_ingame_exit)
                n = max(1, len(ingame_openings(rec)))
                bm = read_ingame_exit(root, mod, n).get("build_match")
                clause("build_match", "every in-game check's last row counts on the build he walks: its game build "
                       "equals the walk's, its mod list is his walk's (a full-list test) or its tier's (a minimal-list "
                       "test), and its mod hash equals the walk's or the change since its commit touches nothing it "
                       "reads or exercises; the walk folder is the current source (build_match.py)",
                       bool(bm) and bm["read"] > 0 and not bm["rerun"] and not bm.get("deploy"),
                       [rec_ref], observed=BM.summary(bm) if bm else "visit %d has no Exit block to read" % n,
                       would_pass="python3 src/RimMandrake/rimflow/build_match.py check --mod %s --visit %d exits 0"
                       % (mod, n),
                       fix="run only the listed checks on the walk build (each row carrying the fields `build_match.py "
                           "identity` prints)%s" % ("; first %s" % bm["deploy"] if bm and bm.get("deploy") else ""),
                       cost="rerun",
                       why_sound="his ruling of 2026-11-17 (RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_BRIEF_NO_VETO), "
                                 "narrowed by his of 2026-11-21 (RIMMANDRAKE_RERUN_ONLY_CHECKS_THE_CHANGE_TOUCHES_NOT_ALL_203): "
                                 "only the checks the change touches run again")
                tt6_, _ = read_json(root, mod, "version/test_table.json")
                known6 = dict(ingame_tests(tt6_))
                uo = [u for u in unrun_owed(root, mod, tt6_) if u.get("check") in known6]
                uref = rel(mod, UNRUN_FILE)
                clause("unrun_run", "every in-game check recorded UNRUN has run on a commit that holds its change",
                       not uo, [uref, rec_ref], observed="still UNRUN: %s" % "; ".join(
                           "%s (%s)" % (r.get("check"), r.get("owed_why")) for r in uo),
                       would_pass="a row for each on a commit that contains its UNRUN row's sha",
                       fix="run only these checks (%s) and write their rows" % ", ".join(
                           dict.fromkeys(str(r.get("check")) for r in uo)), cost="rerun",
                       why_sound="spec Stage 3 exit: an in-game check is UNRUN until Stage 6 runs it")
        elif cur == "pre_human":
            clause("walk_checks_stand", "no in-game check is owed on the build he walks: no UNRUN row is left, and no "
                   "change since a check's last row touches it or cannot be related to it (walk_owed)",
                   not wo["owed"] and not wo["why"], [rec_ref, rel(mod, UNRUN_FILE)],
                   observed="; ".join(["owed: %s (%s)" % (t, w) for t, w in wo["owed"].items()] +
                                      ["could not look: %s" % w for w in wo["why"]]),
                   would_pass="python3 src/RimMandrake/rimflow/build_match.py check --mod %s names no check to run" % mod,
                   fix="the tick sends the mod back to Stage 6 for only these checks (autovisit); by hand: maturation.py "
                       "advance %s --to in_game" % mod if wo["owed"] else "repair what could not be read, then advance again",
                   cost="rerun", why_sound="root CLAUDE.md, After a change, only the checks that the change touches run "
                   "again: those checks run before he walks the build (Pyrelands, 2026-11-24)")
            wb = read_walk_brief(root, mod, rec)
            clause("walk_brief", "his walk brief for this arrival is written (%s), by an agent that made none of the "
                   "evidence writes" % ", ".join(WALK_BRIEF_HEADINGS), not wb["why"], [wb["path"], rec_ref],
                   observed="; ".join(wb["why"]) or "the brief %s is written by %s" % (wb["path"], wb.get("by")),
                   would_pass="%s with its four headings filled and a written_by line naming a unit that made no move "
                              "and no in-game row of this version" % wb["path"],
                   fix="a fresh reader writes it per src/RimMandrake/rimflow/roles/walk_brief.md", cost="rerun",
                   why_sound="his ruling of 2026-11-17 (RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_BRIEF_NO_VETO): one "
                             "fresh read writes the walk brief; it has no veto, so this is the stage's only exit check")
            # RIMMANDRAKE_ROUTE_FLOWWORKS_WALK_TWO_FINDINGS_BACK_ELEVEN_FILED: his last walk's findings close first
            wo = walk_items_open(root, mod)
            wref = wo["path"] or rel(mod, WALK_BRIEF_DIR)
            inputs[wref] = json.dumps(wo, sort_keys=True)
            clause("walk_items_closed", "every item his last walk sent back (its walk result's fix, pick and scene "
                   "lists) is closed, dropped or superseded before he walks again", not wo["why"] and not wo["open"],
                   [wref, rec_ref],
                   observed="; ".join(wo["why"]) or "open from %s: %s" % (wo["path"], ", ".join(wo["open"])),
                   would_pass="each item of %s's fix, pick and scene lists closed on the ledger" % wref,
                   fix="the road back's fixers close the fix and scene items; a pick item closes on his pick",
                   cost="rerun", why_sound="spec Stage 8 road back: his objection stays in this version until fixed; "
                   "the walk of 2026-11-22 came back to him with his 2026-11-20 findings unfixed")
        elif cur == "his_walk":
            hand.append("owner_said")
            oe, owhy = owner_event(root, owner)
            clause("owner_said", "the version passes on his words alone", oe is not None, [req_ref],
                   observed="owner_said: %s" % owhy,
                   would_pass="--owner-said OWNER:<tsn>, his event on the OWNER shard passing the version",
                   fix="his walk ends with his words; pass them verbatim", cost="owner",
                   why_sound="the pass is his alone (carried, spec Stage 8)")
            if to == "passed":
                wid = walk_id = walk_identity(root, mod, rec)
                inputs["walk_build"] = json.dumps(wid, sort_keys=True)      # the reading the clause rests on
                clause("walk_build", "the pass names the one build he walked: the visit's mod source sha, the deployed "
                       "folder hash, the active mod list in order and the game build (build_match.py)", not wid["why"],
                       ["walk_build", rec_ref], observed="; ".join(wid["why"]) or "walk build: %s" % ", ".join(
                           "%s %s" % (k, str(wid.get(k))[:40]) for k in WALK_FIELDS),
                       would_pass="the last in-game visit's rows name one mod_sha and build_match.py reads the walk "
                                  "savegame's mod hash, game build and mod list on %s" % BM.WALK_HOST,
                       fix="read the walk build on the walk machine (build_match.py check --mod %s); a visit whose rows "
                           "name no single build is re-run" % mod, cost="rerun",
                       why_sound="RIMMANDRAKE_BIND_STAGE_EVIDENCE_TO_ONE_BUILD: a pass record names the build it passed "
                                 "(skeptical review 2026-11-15, claims_checked.md A12)")
                tt6, _ = read_json(root, mod, "version/test_table.json")
                rb_ok, rb_why = raid_bars_decided(root, mod, max(1, len(ingame_openings(rec))), tt6, conductor)
                clause("raid_bars_decided", "no bar that a raid scene decides is open when the version passes", rb_ok,
                       [req_ref, rec_ref], observed=rb_why,
                       would_pass="the raid scene, or the cheaper test that replaces it, passes; or --conductor-decision "
                                  "names each open bar and says what becomes of it",
                       fix="lift the raid pause when the tools can hold a raid still, and run the scene", cost="rerun",
                       why_sound="his ruling of 2026-11-23: raid tests wait for the tools; a paused scene is no pass "
                                 "(standing_rulings.md, The cheapest test that decides the bar)")
                prp = "%s/%s.json" % (PASS_RECORD_DIR, rec.get("version"))
                clause("pass_record_new", "this version has no pass record yet (a pass record is written once, never "
                       "rewritten)", not os.path.lexists(os.path.join(mod_dir(root, mod), prp)), [rec_ref, rel(mod, prp)],
                       observed="%s %s version %s already has %s" % (
                           mod, rec.get("stage"), rec.get("version"), rel(mod, prp)),
                       would_pass="no %s" % rel(mod, prp), fix="a passed version opens its next version instead "
                       "(maturation.py next-version)", cost="owner",
                       why_sound="Design Versions draft section 3.7: the pass record of each passed version")
    if forward and to == "blind_challenge" or (back and cur == to == "blind_challenge"):
        visit = (rec.get("cycles") or {}).get("visit", 0) if cur == "blind_challenge" else 0
        import pipeline_control as PC       # the one control store (`pipe add <Mod> blind_cycles_total -1`)
        visit, lim = PC.used(mod, "blind_cycles_total", visit), PC.limit(mod, "blind_cycles_total", CYCLE_LIMIT)
        if visit >= lim:
            hand.append("conductor_decision")
        clause("fourth_cycle", "after three blind cycles in one visit the Conductor decides; a fourth judge never "
               "starts on its own", visit < lim or bool(conductor), [rec_ref, req_ref],
               observed="cycles visit %d of %d; conductor_decision: none in the request" % (visit, lim),
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
    # the family is the brief, not the move: judge_calibration.json is an exact lookup, so a family carrying the
    # transition could never match a calibrated row (the transition stays in `request`, and in from/to below)
    verdict = {"item": "%s@%s" % (mod, rec.get("version")), "family": ADVANCE_FAMILY,
               "sha": sha or UNM, "given": {"criteria": crit, "inputs": inputs}, "passed": passed,
               "refusals": refusals}
    return {"ok": not refusals, "verdict": verdict, "hand_steps": hand, "from": cur, "to": to, "walk_identity": walk_id,
            "revision": revision}


# ---- the move --------------------------------------------------------------------------------------------------------

def ledger_stage_move(root, mod, cur, to, by, move=None, at=None):
    """A mod that has a ledger keeps its stage equal to the stage record's: one DISPATCH stage.accepted per move (a
    backfill alone left ExplosiveKnockback's ledger at offline_build after it moved to in_game). -> the event id, or
    None for a mod with no ledger."""
    import modledger
    if not os.path.isdir(os.path.join(root, "design", "concepts", mod, "ledger")) and not modledger.read(root, mod):
        return None
    # move (its number on the record) and at keep a transition made a second time from reading as a duplicate of the
    # first: the idempotency key is derived from the body (FlowWorks his_walk -> in_game, 2026-11-21 and 2026-11-22)
    body = {"from": cur, "to": to, "by": by}
    if move is not None:
        body.update(move=move, at=at)
    return modledger.append(root, mod, "DISPATCH", "stage.accepted", "stage", body=body, env_writer=None)


def ledger_version_open(root, mod, new, by, why):
    """A mod that has a ledger opens each new Design Version in it when next-version opens the record: one DISPATCH
    version.open (RIMMANDRAKE_OPEN_MOD_LEDGER_VERSION_WITH_ITS_NEXT_VERSION: GimmeSomeSlack's ledger still read 0.1.0
    after 0.1.1 opened, so its 0.1.1 stage moves were tagged 0.1.0). -> the event id, or None for a mod with no ledger."""
    import modledger
    if not os.path.isdir(os.path.join(root, "design", "concepts", mod, "ledger")) and not modledger.read(root, mod):
        return None
    return modledger.append(root, mod, "DISPATCH", "version.open", "version",
                            body={"version": str(new), "text": "opened by next-version (%s): %s" % (by, str(why)[:300])},
                            version=str(new), env_writer=None)


def tag_new_since(verdict):
    """RIMMANDRAKE_COUNT_ADVANCE_REFUSALS_SO_A_LOOP_RINGS: say what is new in each refusal since the item's earlier
    counted ones, MEASURED from the contract's counters (as coverage_judge.tag_gaps does), never guessed; the record
    the gate builds says "first", which the contract refuses once a refusal is counted. -> the prior refused count.
    Raises OSError/ValueError when the counters cannot be read: an unknown prior is not a prior of zero."""
    it = RC.counters()["items"].get(verdict["item"]) or {}
    prior, seen = int(it.get("refused") or 0), it.get("clauses") or {}
    for rec in verdict["refusals"]:
        c = rec["clause"]
        # `late` is never written: the gate reads every clause of the move every time, so it cannot miss one and
        # then bring it late
        rec["new_since"] = "first" if not prior else (
            "unfixed:%s" % c if seen.get(c) else "regression:%s" % c)
    return prior


def submit_line(res):
    """One line saying what the refusal contract did with this verdict, or None when it was not submitted at all.
    Four answers, never collapsed: counted / submitted but not counted (with why) / the count could not be written
    (which is not a count of zero) / malformed (the caller prints that one)."""
    if res.get("submit_error"):
        return "COUNT NOT WRITTEN: %s. The refusal count is UNREADABLE, not zero: the %s alarm cannot ring until " \
               "the store is reachable again." % (res["submit_error"], RC.ALARM_ID)
    s = res.get("submit")
    if not s:
        return None
    if s.get("counted"):
        why = ["counted: %s" % res["verdict"]["item"]]
        if s.get("repair_due"):
            why.append("clause %s refused %d times: criteria repair due" % (", ".join(s["repair_due"]),
                                                                            RC.CLAUSE_REPAIR_AT))
        for a in s.get("alarms") or []:
            why.append("%s raised on %s: %s" % (RC.ALARM_ID, a.get("subject"), a.get("why")))
        return "; ".join(why)
    why = ("the brief %s is %s, so a refusal is stored and shown only" % (res["verdict"]["family"],
                                                                          s.get("calibration"))
           if s.get("advisory") else "nothing has changed since the stored refusal of clause %s"
           % ", ".join(s.get("cached") or []))
    return "SUBMITTED BUT NOT COUNTED (%s)" % why


def advance(root, mod, to, by, why, steward=None, conductor=None, owner=None, waits_on=None, game_only=None,
            first_files=None, confirmed_extra=None, expect_stage=None):
    """first_files {path: text}: NEW files written once in the move's locked write (a walk result); confirmed_extra:
    more fields for the move's `confirmed`; expect_stage: refuse unless the record stands there (walk_result)."""
    if expect_stage is not None:
        here = load(root, mod)
        if here is None or here.get("stage") != expect_stage:
            return {"ok": False, "why": "the record stands at %s, not %s" % (
                "no stage record" if here is None else here.get("stage"), expect_stage), "verdict": {"refusals": []}}
    res = evaluate(root, mod, to, steward=steward, conductor=conductor, owner=owner, by=by, why=why, check_by=True,
                   game_only=game_only)
    res["submit"], res["submit_error"], prior, errs = None, None, 0, []
    try:
        prior = tag_new_since(res["verdict"])
    except (OSError, ValueError) as e:
        # the count could not be LOOKED at: with the prior unknown the new_since tags cannot be trusted, so nothing
        # is submitted (a submit would store a malformed row and alarm the brief for the store's own fault)
        res["submit_error"] = "the refusal counters could not be read (%s: %s)" % (type(e).__name__, e)
    if not res["submit_error"]:
        try:
            sub = RC.submit(res["verdict"], now=now_ts())
        except (OSError, ValueError) as e:
            res["submit_error"] = "the refusal store could not be written (%s: %s)" % (type(e).__name__, e)
        else:
            res["submit"] = {k: sub.get(k) for k in ("ok", "counted", "cached", "advisory", "calibration",
                                                     "repair_due", "alarms", "may_judge", "pointer")}
            errs = sub["errors"]
    if res["submit"] is None:
        # the store is unreachable: the verdict is still checked here, against the prior the counters gave (0 when
        # they could not be read), so a malformed verdict is never excused by the store's silence
        errs = RC.check(res["verdict"], prior=prior)
    if errs:
        res["malformed"] = errs
        res["ok"] = False
        return res
    if not res["ok"]:
        return res
    rec = load(root, mod)
    cur, t = rec["stage"], now_ts()
    if (cur, rec.get("version"), len(rec.get("moves") or [])) != res["revision"]:
        # another move landed between the evaluation and this write: what was checked is not what would be moved
        res["ok"], res["moved_meanwhile"] = False, "the record is %s now, not the %s evaluated" % (
            (cur, rec.get("version"), len(rec.get("moves") or [])), res["revision"])
        return res
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
    move["confirmed"].update(confirmed_extra or {})
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
    first = None
    if cur == "his_walk" and to == "passed":
        # RIMMANDRAKE_BIND_STAGE_EVIDENCE_TO_ONE_BUILD: the pass record goes in the same lock, written BEFORE the stage
        # record (a stage that reads passed always has its record) and only where no file stands yet
        wid = res.get("walk_identity")
        if not wid or wid.get("why"):
            res["ok"] = False
            res["moved_meanwhile"] = "no validated walk build to record: %s" % ((wid or {}).get("why") or "none read")
            return res
        taken = pass_tag_taken(root, mod, rec.get("version"))
        if taken:      # RIMMANDRAKE_TAG_EACH_PASSED_MOD_VERSION_PIPELINE_DOES_IT: refused before any write
            res["ok"], res["tag_taken"] = False, taken
            return res
        prp, pr = pass_record(root, mod, rec, owner, res["verdict"].get("sha"), t, wid)
        first = {prp: json.dumps(pr, indent=1, sort_keys=True) + "\n"}
        res["pass_record"] = rel(mod, prp)
    try:
        new_files = {}
        for part in (first, first_files):
            if part:
                new_files.update(part)
        commit_move(root, mod, rec, jtext, first=new_files if new_files else None, expect=res["revision"])
    except MovedMeanwhile as e:
        res["ok"], res["moved_meanwhile"] = False, str(e)
        return res
    ledger_stage_move(root, mod, cur, to, by, move=len(rec["moves"]), at=move["at"])
    if first:
        # the pass is made and stays made; landing and tagging it can only add res["tag"] or res["untagged"]
        res.update(tag_pass(root, mod, rec.get("version"), paths=pass_paths(root, mod, list(first),
                                                                             jtext is not None)))
    return res


def _mod_lock(root, mod):
    import fcntl
    os.makedirs(mod_dir(root, mod), exist_ok=True)
    f = open(os.path.join(mod_dir(root, mod), ".stage_move.lock"), "w")
    fcntl.flock(f, fcntl.LOCK_EX)
    return f


class MovedMeanwhile(RuntimeError):
    """The record on disk is not the one the move was evaluated on: another move landed first."""


def _absent(path):
    """True only when the path is measured absent; a stat that fails any other way is not absence."""
    try:
        os.lstat(path)
    except FileNotFoundError:
        return True
    except OSError:
        return False
    return False


class RollbackIncomplete(OSError):
    """A move's write failed and at least one put-back failed too: the files named are left as the move wrote them."""


def commit_move(root, mod, rec, jtext=None, extra=None, first=None, expect=None):
    """RIMMANDRAKE_WRITE_STAGE_MOVES_ATOMICALLY: one move is one locked write. Under the mod's lock the record is
    written first (a failed record write leaves no journal line), then the journal and any extra {path: text}; a later
    write that fails puts every file already written back as it was and raises; every put-back is tried even when one
    fails, and then RollbackIncomplete names each file left unrestored. An existing file that cannot be read is never
    written over (its old text could not be put back). `first` {path: text} are NEW files
    written before the record (a pass record): one that already exists, even unreadable, raises before any write.
    expect (stage, version, number of moves): the record on disk must still read so under the lock, else
    MovedMeanwhile before any write."""
    lk = _mod_lock(root, mod)
    try:
        if expect is not None:
            now = load(root, mod) or {}
            got = (now.get("stage"), now.get("version"), len(now.get("moves") or []))
            if got != tuple(expect):
                raise MovedMeanwhile("the record is %s under the lock, not the %s evaluated" % (got, tuple(expect)))
        for p in sorted(first or {}):
            if os.path.lexists(os.path.join(mod_dir(root, mod), p)):
                raise FileExistsError("%s already exists: it is written once, never replaced" % rel(mod, p))
        todo = sorted((first or {}).items()) + [(RECORD, dump(rec))] + (
            [("journal.md", jtext)] if jtext is not None else []) + sorted((extra or {}).items())
        done = []
        try:
            for p, text in todo:
                was = read_text(root, mod, p)
                if was is None and not _absent(os.path.join(mod_dir(root, mod), p)):
                    raise OSError("%s exists or cannot be looked at, and cannot be read: its text could not be put "
                                  "back" % rel(mod, p))
                write_text(root, mod, p, text)
                done.append((p, was))
        except Exception as e:
            left = []
            for p, was in reversed(done):
                try:
                    if was is None:
                        try:
                            os.remove(os.path.join(mod_dir(root, mod), p))
                        except FileNotFoundError:
                            pass
                    else:
                        write_text(root, mod, p, was)
                except Exception as be:
                    left.append("%s (%s)" % (rel(mod, p), be))
            if left:
                raise RollbackIncomplete("the move failed (%s) and %d file(s) are left as it wrote them: %s"
                                         % (e, len(left), "; ".join(left))) from e
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
    event, OWNER:<tsn>, or the Conductor window's act under the five-acts ruling (owner 2026-11-19; a removal names
    lost: and undo:); an agent never changes a bar on its own word. -> {"ok", "why", "ids"}."""
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
        his = isinstance(ev, dict) and bool(str(ev.get("ownerSaid") or ev.get("byCard") or "").strip())
        if not his:
            # owner 2026-11-19: the Conductor window may add a bar, and remove one mindfully (lost: / undo: in its why)
            import conductor_acts as CA
            ok, cwhy = CA.is_conductor_event(ev, act="loosen a bar" if remove else "add a bar")
            if not ok:
                return {"ok": False, "why": "--source %r is neither one of his OWNER events with his words nor the "
                        "Conductor's act under %s (%s): an agent never changes a bar on its own word"
                        % (source, CA.RULING, cwhy)}
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
    # the old version's numbered evidence is set aside first: the new counters start at 0, and a cycle_2 or visit_1
    # left in place reads as the new version's (design/specs/2026-11-19-maturation-record/boundary.md)
    aside = "%s/%s" % (PREVIOUS_DIR, re.sub(r"[^0-9A-Za-z.-]", "_", str(old)))
    moves = [(p, aside + "/" + p[len("version/"):]) for p in numbered_evidence(root, mod)]
    taken = [b for _, b in moves if not _absent(os.path.join(mod_dir(root, mod), b))]
    if taken:
        return {"ok": False, "why": "the previous version's evidence cannot be set aside: %s already exist(s)"
                % ", ".join(rel(mod, b) for b in taken)}
    jtext = read_text(root, mod, "journal.md")
    if jtext is not None:
        when = pac_heading(t)
        jtext, was = replace_bullet(jtext, "Stage now", "- **Stage now:** %s, since %s (`%s`)." % (LINE[stage], when,
                                                                                                    RECORD))
        jtext = jtext.rstrip("\n") + "\n\n" + "\n".join([
            "### %s, version change: %s to %s (by %s)" % (when, old, new, by), "", "- Why: %s" % why,
            "- The %s record (at %s) is kept as `%s`." % (old, label(rec.get("stage")), keep)] + (
            ["- Its numbered evidence (%d cycle, visit and arrival paths) is set aside in `%s`." % (len(moves), aside)]
            if moves else []) + [
            "- Was, \"Stage now\": %s" % (was or "none"), "- Record: `%s`." % RECORD]) + "\n"
    done = []
    try:
        for a, b in moves:
            os.makedirs(os.path.dirname(os.path.join(mod_dir(root, mod), b)), exist_ok=True)
            os.rename(os.path.join(mod_dir(root, mod), a), os.path.join(mod_dir(root, mod), b))
            done.append((a, b))
        commit_move(root, mod, nrec, jtext, extra={keep: dump(rec)})
    except Exception as e:
        left = []
        for a, b in reversed(done):
            try:
                os.rename(os.path.join(mod_dir(root, mod), b), os.path.join(mod_dir(root, mod), a))
            except OSError as be:
                left.append("%s (%s)" % (rel(mod, b), be))
        if left:
            raise OSError("next-version failed (%s) and %d set-aside path(s) could not be moved back: %s"
                          % (e, len(left), "; ".join(left))) from e
        raise
    ledger_version_open(root, mod, new, by, why)   # after the record is committed: never rolls the move back
    return {"ok": True, "why": why, "from": old, "to": new, "stage": stage, "kept": rel(mod, keep),
            "archived": [rel(mod, a) for a, _ in moves], "aside": rel(mod, aside) if moves else None}


PREVIOUS_DIR = "version/previous"


def numbered_evidence(root, mod):
    """-> the version's numbered evidence present (paths under the mod's folder): blind cycle folders, in-game visit
    folders and walk-brief arrival files, each numbered by a record counter next_version starts again at 0."""
    out = []
    for d, rx in ((BLIND_DIR, r"cycle_\d+$"), (INGAME_DIR, r"visit_\d+$"), (WALK_BRIEF_DIR, r"arrival_\d+\.md$")):
        full = os.path.join(mod_dir(root, mod), d)
        out += ["%s/%s" % (d, f) for f in sorted(os.listdir(full) if os.path.isdir(full) else []) if re.match(rx, f)]
    return out


def CT_txt(x):
    return isinstance(x, str) and bool(x.strip())


# ---- spend -----------------------------------------------------------------------------------------------------------

def add_spend(root, mod, stage, tokens, usd=None, wall_s=None, source=None, estimate=False):
    if stage not in WORDS:
        raise ValueError("no stage %r; stages are %s" % (stage, ", ".join(WORDS)))
    lk = _mod_lock(root, mod)     # read, change and write under the lock: a move landing in between is never erased
    try:
        rec = load(root, mod)
        if rec is None:
            raise ValueError("%s has no stage record; run seed first" % mod)
        rec.setdefault("spend", []).append({
            "stage": stage, "stages": [stage], "tokens": tokens if isinstance(tokens, int) else UNM,
            "token_unit": TOKEN_UNIT,
            "usd": usd if isinstance(usd, (int, float)) else UNM, "wall_s": wall_s if isinstance(wall_s, (int, float))
            else UNM, "source": source or UNM, "kind": "estimate" if estimate else "measured", "at": iso(now_ts())})
        write_text(root, mod, RECORD, dump(rec))
    finally:
        lk.close()
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


def version_spend_rows(root, mod, rec):
    """-> spend_rows scoped to this version: the record's own entries, plus the Dispatch run rows that ended on or
    after the record's seeded.at. RUN_SPEND outlives next-version and its rows name no version, so an earlier
    version's runs would otherwise count as this one's (RIMMANDRAKE_SCOPE_RUN_SPEND_TO_VERSION_OLD_RUNS_LINGER). Every
    place spend is REPORTED reads this; record_run_spend reads spend_rows whole, so an old unit is never re-added."""
    own = len((rec or {}).get("spend") or [])
    since = _instant(((rec or {}).get("seeded") or {}).get("at"))
    rows = spend_rows(root, mod, rec)
    # compared as instants: iso() writes Pacific time with its offset, so strings misorder the fall-back hour
    return rows[:own] + [x for x in rows[own:] if since is None or (_instant(x.get("at")) or -1e18) >= since]


def _instant(s):
    """An ISO time (any offset, or Z) -> epoch seconds, or None when absent or unreadable."""
    try:
        t = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return (t if t.tzinfo else t.replace(tzinfo=PAC)).timestamp()


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


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def spend_by_stage(rec):
    """-> {stage: {tokens, tokens_other, unit, usd, wall_s, entries, estimates, unmeasured}}. A run that worked in
    several stages is counted once, under the joined key ("designer+preflight"), never split by a guess. tokens, usd and
    wall_s are each UNMEASURED when no entry of that stage measured it, never 0. tokens sums weighted_v2 rows only;
    tokens_other sums every other unit apart, by unit (row_unit), never converted or mixed in
    (design/specs/2026-11-19-maturation-record/boundary.md)."""
    out, known = {}, {}
    for s in rec.get("spend") or []:
        key = "+".join(s.get("stages") or [s.get("stage")])
        t = out.setdefault(key, {"tokens": 0, "tokens_other": {}, "unit": TOKEN_UNIT, "usd": 0.0, "wall_s": 0,
                                 "entries": 0, "estimates": 0, "unmeasured": 0})
        kn = known.setdefault(key, set())
        t["entries"] += 1
        if s.get("kind") == "estimate":
            t["estimates"] += 1
        for k in ("tokens", "usd", "wall_s"):
            if not _num(s.get(k)):
                t["unmeasured"] += 1
            elif k == "tokens" and row_unit(s) != TOKEN_UNIT:
                u = row_unit(s)
                t["tokens_other"][u] = t["tokens_other"].get(u, 0) + s[k]
            else:
                t[k] += s[k]
                kn.add(k)
    for key, t in out.items():
        for k in ("tokens", "usd", "wall_s"):
            if k not in known[key]:
                t[k] = UNM
    return out


# ---- tuning tripwire T1: a builder diff that changes only numbers -----------------------------------------------------
#
# RIMMANDRAKE_FLAG_NUMBER_ONLY_DIFFS_IN_MATURATION_NEXT (the owner, 2026-11-16; Slack had 21 of 37 edits that changed only
# numbers). `next`, which every builder runs on itself before it stops (SELF_CHECK_RULE), prints a note; it never refuses.
# Page: design/specs/2026-11-19-maturation-tripwires/boundary.md.

NUM_RX = re.compile(r"(?<![A-Za-z_])[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?[fFdDmM]?(?![A-Za-z_])")
NAME_RX = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*(?:=|:)(?!=)")
TAG_RX = re.compile(r"<([A-Za-z_][A-Za-z0-9_.]*)[^>]*>")
TRIPWIRE_NOTE = ("this diff changes only numbers in %d constants; this item has had %d such diffs on the same check. Map "
                 "where each bar holds before the next one.")


def _const_name(line, lineno):
    m = NAME_RX.search(line)
    if m:
        return m.group(1)
    m = TAG_RX.search(line)
    return m.group(1) if m else "line %d" % lineno


def number_only_constants(diff):
    """A unified diff -> the sorted "file:NAME" keys it changes when every changed line differs from its pair only in
    numeric literals; None when any change is more (a line added or removed alone, a word changed); [] when it changes
    nothing. NAME: the identifier before = or :, else the XML tag, else the line number."""
    keys, path, minus, plus, newline = set(), None, [], [], 0

    def flush():
        if len(minus) != len(plus):
            return False
        for (_, a), (n, b) in zip(minus, plus):
            if a == b or NUM_RX.sub("#", a) != NUM_RX.sub("#", b):
                return False
            keys.add("%s:%s" % (path, _const_name(b, n)))
        minus.clear()
        plus.clear()
        return True
    for ln in str(diff or "").splitlines():
        if ln.startswith("+++ "):
            path = ln[4:].strip()
            path = path[2:] if path.startswith("b/") else path
            continue
        if ln.startswith("--- ") or ln.startswith("diff ") or ln.startswith("index "):
            continue
        if ln.startswith("@@"):
            if not flush():
                return None
            m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", ln)
            newline = int(m.group(1)) if m else 0
            continue
        if ln.startswith("-"):
            minus.append((newline, ln[1:]))
        elif ln.startswith("+"):
            plus.append((newline, ln[1:]))
            newline += 1
        else:
            if not flush():
                return None
            newline += 1
    return sorted(keys) if flush() else None


def tripwire_history(item):
    import doorbell
    return os.path.join(doorbell.state_dir(), "maturation", "number_diffs", "%s.jsonl" % re.sub(r"[^\w.-]", "_", item))


def tripwire(diff, item, hist):
    """-> None for a diff that is not number-only (nothing recorded), else {"constants", "count", "note"}: count is the
    number-only diffs this item has had on any of the same constants, this one included, each diff once (by its
    hash) however often `next` reads it. hist: the item's history file (tripwire_history)."""
    import hashlib
    keys = number_only_constants(diff)
    if not keys:
        return None
    h = hashlib.sha256(str(diff).encode("utf-8")).hexdigest()[:16]
    rows = []
    try:
        with open(hist, encoding="utf-8") as f:
            for ln in f:
                try:
                    rows.append(json.loads(ln))
                except ValueError:
                    continue
    except FileNotFoundError:
        pass
    if not any(r.get("hash") == h for r in rows):
        rows.append({"hash": h, "constants": keys, "at": iso(now_ts())})
        os.makedirs(os.path.dirname(hist), exist_ok=True)
        with open(hist, "a", encoding="utf-8") as f:
            f.write(json.dumps(rows[-1]) + "\n")
    n = sum(1 for r in rows if set(r.get("constants") or []) & set(keys))
    return {"constants": keys, "count": n, "note": TRIPWIRE_NOTE % (len(keys), n)}


def run_diff(root, mod):
    """-> (the diff of MOD's files since this detached run began, item) or (None, cause): read from RM_DETACHED_UNIT's
    record (its launch time and item) against the last origin/main commit before it. (None, None) outside a run."""
    unit = os.environ.get("RM_DETACHED_UNIT")
    if not unit:
        return None, None
    try:
        import detached_helper as DH
        rec = DH.read_record(unit)
    except Exception as e:  # noqa: BLE001
        return None, "the run record of %s could not be read: %s" % (unit, e)
    if not isinstance(rec, dict):
        return None, "no readable run record for %s" % unit
    at, item = rec.get("at"), rec.get("item")
    if not isinstance(at, (int, float)) or not item:
        return None, "the run record of %s names no launch time or item" % unit
    paths = ["src/RimMandrake/%s" % mod, "design/concepts/%s" % mod]
    try:
        base = subprocess.run(["git", "-C", root, "rev-list", "-1", "--before=@%d" % int(at), "origin/main"],
                              capture_output=True, text=True, timeout=60).stdout.strip()
        if not base:
            return None, "no origin/main commit before the run began"
        # errors="replace": a diffed evidence log may hold Windows bytes (a cp1252 dash), which must not kill the reader
        r = subprocess.run(["git", "-C", root, "diff", base, "--"] + paths, capture_output=True, text=True, encoding="utf-8",
                           # budget: class=call
                           errors="replace", timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return None, "git could not run: %s" % e
    if r.returncode:
        return None, "git diff failed: %s" % (r.stderr.strip()[:200] or r.returncode)
    return r.stdout, item


# ---- next ------------------------------------------------------------------------------------------------------------

def next_step(root, mod, now=None, src=None):
    """-> what MOD does next and whether it may run now: mod_next.next_for, the one home
    (design/specs/2026-11-22-mod-next/boundary.md). gate_step below is its stage-record part."""
    import mod_next     # imported late: it imports us
    return mod_next.next_for(root, mod, now=now, src=src)


def gate_step(root, mod, _reread=False):
    """-> the stage record's next step alone (its exit tests): no hold, switch, pause or tick reading. Read through
    next_step (mod_next.next_for) for what may run."""
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
    moved = [f["stage"] for f in (blind, ing) if f is not None and f.get("stage") != cur]
    if moved:   # a move landed between the two loads (design/specs/2026-11-21-next-step-stage-moved/boundary.md)
        if not _reread:
            return gate_step(root, mod, _reread=True)
        return {"mod": mod, "stage": UNM, "refusals": [], "hand_steps": [],
                "next": "NEXT (read again): the stage record moved during the read twice (%s, then %s); "
                        "maturation.py next %s reads it again" % (cur, moved[0], mod)}
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
        nxt = ("NEXT (automatic: one steward run): visit %d: exit met (a program's reading of its record, the build "
               "match with it: %s); the steward reads "
               "%s/SUMMARY.md and confirms: maturation.py advance %s --to pre_human --by <SEAT> --why \"...\" "
               "--steward-confirms \"...\"" % (ing["visit"], ing["exit"]["why"][0], ing["exit"]["record"], mod))
    elif ing:
        nxt = ("NEXT (automatic: one steward run, then a fixer per item): visit %d: exit not met (%s); the steward reads "
               "%s/SUMMARY.md, files a named item for each mod-wrong line (and each wrong check a bar needs that the driver "
               "could not repair) and sends the mod down its road back only for those or an undecided bar (maturation.py "
               "advance %s --to offline_build or --to blind_challenge, or --to in_game for a check only to re-run, as "
               "one made on another build than his walk's); the next visit launches when they close" % (
                   ing["visit"], "; ".join(ing["exit"]["why"][:3]), ing["exit"]["record"], mod))
    elif blind and blind.get("owed") == "blocked":
        nxt = "NEXT (PAUSED, OPS_MATURATION_MOD_PAUSED): the blind challenge is blocked: %s" % "; ".join(blind["blocked"])
    elif blind and blind.get("owed") == "cycle":
        nxt = ("NEXT (automatic: the Dispatch tick launches it): blind cycle %d (maturation.py launch %s --budget-usd <cap> --item <ID>, or the Dispatch "
               "step); its record goes in %s" % (blind["cycle"], mod, blind["exit"]["record"]))
    elif blind and blind.get("owed") == "resume":
        nxt = "NEXT (automatic: the Dispatch tick resumes it): %s" % void_resume_text(blind)
    elif blind and blind.get("owed") == "no exit block":
        nxt = ("NEXT (wait on its live run, else PAUSED): cycle %d is recorded without an exit block: its run writes one, "
               "or (nothing live) the mod is PAUSED until someone reads %s/SUMMARY.md" % (blind["cycle"], blind["exit"]["record"]))
    elif blind and blind.get("owed") == "exit met":
        nxt = ("NEXT (automatic: one steward run): cycle %d: exit met (a program's reading of its record: %s); the steward reads "
               "%s/SUMMARY.md and confirms: maturation.py advance %s --to in_game --by <SEAT> --why \"...\" "
               "--steward-confirms \"...\"" % (blind["cycle"], blind["exit"]["why"][0], blind["exit"]["record"], mod))
    elif blind:
        import pipeline_control as PC       # the same count and limit the advance reads (`pipe show <Mod>`)
        at_limit = (PC.used(mod, "blind_cycles_total", blind.get("visit") or 0)
                    >= PC.limit(mod, "blind_cycles_total", CYCLE_LIMIT))
        nxt = ("NEXT (%s): cycle %d: exit not met (%s); the steward reads %s/SUMMARY.md, files the failures as named "
               "items and opens the next blind cycle (maturation.py advance %s --to blind_challenge%s) or another road" % (
                   "PAUSED: three cycles, the Conductor decides" if at_limit else
                   "automatic: one steward run", blind["cycle"], "; ".join(blind["exit"]["why"][:3]), blind["exit"]["record"], mod,
                   " --conductor-decision \"...\": three cycles in this visit" if at_limit else ""))
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
            "spend": spend_by_stage({"spend": version_spend_rows(root, mod, rec)}),
            "launch": ("maturation.py launch %s --budget-usd <cap> --item <ID> (or the Dispatch step, "
                       "maturation_dispatch.py)" % mod) if cur == "offline_build" and prog else
            ("maturation.py launch %s --budget-usd <cap> --item <ID> (blind cycle %d; or the Dispatch step, "
             "maturation_dispatch.py)" % (mod, blind["cycle"])) if blind and blind.get("owed") == "cycle" else
            ("the Dispatch step resumes blind cycle %d: %s" % (blind["cycle"], void_resume_text(blind)))
            if blind and blind.get("owed") == "resume" else
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
# The owner's rulings of 2026-11-20 (RIMMANDRAKE_ENACT_WRONG_CHECK_FIXED_IN_SITTING_NOT_RETURNED and
# RIMMANDRAKE_RESUME_WRONG_CHECK_WORKER_WITH_MOD_FIX_EXTENSION): a wrong check is repaired or removed in the sitting, a
# mod fault the judge or driver can fix is fixed there with one fresh reader of the fix, and any role takes a free game.
# Carried by the blind judge, the in-game driver, the steward (router) and the road-back fixer; read_ingame_exit and
# read_exit enforce it. Full text: standing_rulings.md §Touching code has a cost. selftest_wrong_check_fixed_in_sitting.py.
# The red-seen proof had no owner (measured 2026-11-20: two fixers edited Gimme Some Slack's deciding test file, saw
# planted faults go red, and did not record it; the certificate refused 18 bars on red_seen and the mod sat about 2.5 h).
# Carried by every brief whose run may edit a deciding test: builder, certificate builder, fixer, blind judge, driver.
RED_SEEN_RULE = (
    "- **A run that edits a deciding test records its red run before it closes:** `python3 "
    "src/RimMandrake/rimflow/maturation.py red-seen <Mod> <test id> --patch <the planted fault's patch>`, for each decider "
    "in a file you changed (one edit to a shared test file invalidates every decider in it). A certificate refuses an "
    "edited decider with no recorded red run, and the mod waits until one is recorded.")
# Any role that needs the live game to finish a fix takes it when it is free (owner, 2026-11-20: "if a live game is
# available, of course a judge (or any role!) should be able to just grab it"). Carried by the briefs whose fix can need
# the game: the in-game driver, the blind judge and the live fixer (maturation_autonomy.live_rules). An offline-stage
# fixer gets only offline items (a game-only item goes back to Stage 6), so its brief keeps "Never take the bridge".
FREE_GAME_RULE = (
    "- **A fix that needs the live game takes it when it is free** (owner, 2026-11-20): there are several games, each "
    "with its own bridge holder: ArchBig (Steam's install on Archmagi), ArchSmall (its own install on "
    "Archmagi), and Steve1 and Steve2 on SteveDesktop. Take any game whose bridge is free, ours, or stale by the "
    "45-minute rule, with `python3 "
    "src/RimMandrake/rimflow/cli.py bridge take --idle-ok --for \"<what>\" --seat BENCH` and `./game --idle-ok --why "
    "\"<what>\" up`; for ArchSmall run `eval \"$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)\"` first (a bare `RM_GAME_INSTANCE=b` does not reach a `python.exe` tool, which then drives ArchBig; deploy with `--instance ArchSmall`) and start it if "
    "it is down (`python3 src/RimMandrake/Utils/game_instance.py launch ArchSmall --wait`). If ArchBig is busy or held, use "
    "ArchSmall; no check needs one game rather than another. Release it the moment the "
    "work stops (`python3 src/RimMandrake/rimflow/cli.py bridge release --seat BENCH`). His OWNER hold, the `./bridge` "
    "override, no flyer flight, and never fullscreen or focus a game still bind. A mod does not wait a stage for a game "
    "that sits unused, and no line says \"waiting for the live game\": name the game and why no other game can take "
    "the work.")


def _gn(game):
    """-> the name people read for game letter `game` on this machine: ArchBig, ArchSmall (game_names.py, the one map)."""
    import game_names
    return game_names.show(game)


WRONG_CHECK_RULE = "\n".join([
    "**Class each failed or UNMEASURED line first** (owner, 2026-11-20; `design/RimMandrake/standing_rulings.md` "
    "§Touching code has a cost): mod wrong (`class` MOD: the mod's code, defs or settings), check wrong (`class` HARNESS: "
    "the script, the instrument, the criterion) or scene wrong (`class` SITE: the staged scene). Then:",
    "- Test 1, the worth of the touch: a wrong check or scene is worth repair only if a bar would go undecided without "
    "it. \"A failure happened\" does not make it worth the touch by itself: the failure was the check's. A check that no "
    "bar needs is not kept: remove it from the test table (and delete it when nothing else names it), with one line on "
    "the polish list as the record of the removal. No ticket. A needless check left in place meets the next judge again.",
    "- Test 2, if you see it, do it: the agent that classes a check or scene wrong repairs it in the same sitting and runs "
    "it again. \"My verdict must stay independent\" and \"my assigned work would not finish\" do not excuse a wrong "
    "check or scene: its repair does not touch the mod.",
    "- The guard: a repaired check counts only after it is seen to FAIL on a planted fault (or on a state known bad) and "
    "PASS on the real build, in that sitting, with both readings recorded beside the row. A needed check whose repair "
    "cannot be shown both ways stays not counted (UNMEASURED), never PASS, and keeps an owner: this run, or a filed item "
    "with the evidence. To plant, use what exists: a planted case of the blind challenge (`lane2/planted_faults.json`, "
    "`plant_faults.py`), the check's own `--old` or mutant switch, or a save or state known bad. Build no new framework.",
    "- A repair never weakens what the check observes, and never touches the mod.",
    "- **Mod wrong, and you can fix it: fix it in the sitting.** Write a before/after test (red on the parent, green on "
    "the fix), fix the mod, and show the check passing on the fixed build. Then one fresh reader, a run that did not "
    "make the fix, reads only that fix, once (owner, 2026-11-20). Only a mod fault you could not fix in the sitting goes "
    "down the road back, with the evidence why (no tools, the fix is not known, another run holds the files, it needs one "
    "of his five acts or a north-star bar).",
    RED_SEEN_RULE,
    "- A wrong check or scene never sends the mod back a stage. Only a mod wrong line not fixed in the sitting, or a bar "
    "left undecided, does."])
# The three kinds of live test and the seven outcomes of a run (owner, 2026-11-23; standing_rulings.md §Live tests have
# three kinds). Carried by the in-game driver's brief. live_kinds.py reads the kinds and the outcomes at the exit.
LIVE_KINDS_RULE = "\n".join([
    "Full text: `design/RimMandrake/standing_rulings.md` §Live tests have three kinds. How to write each row: "
    "`skills/live-debugging-proof-harness/SKILL.md` §The scene contract.",
    "- The cheapest test that decides the bar is the test, and no run stages a raid (standing_rulings.md §The cheapest test "
    "that decides the bar). A scene that turns out to stage a raid gets no row: tag its test-table entry `stages_raid` (what "
    "it stages), say in its `cheaper_why` why a cheaper test cannot decide the bar, or write that cheaper test.",
    "- A scene with no tag is kind A: one valid run decides PASS or FAIL. Never repeat an unchanged run to get a PASS.",
    "- Kind B (stochastic) and kind C (an intermittent hunt) carry their evidence on the scene. Kind B passes on one "
    "SUCCESS, with no MOD FAILURE and no UNRESOLVED run on the same claim and build. A result that is random by design "
    "passes on its written X of Y. When its runs end short of X, stop: the scene is held, the pipeline asks the Conductor, "
    "and nobody else changes X or Y. All budgeted runs done with no SUCCESS: the verdict is INCONCLUSIVE. A hunt is never "
    "part of the exit. The tag is on the scene in the test table: `test_kind` (\"A\", \"B\", \"C\"; absent is A), "
    "`tag_evidence`, `budget` (runs, kind B) and `x_of_y` ([X, Y], a result that is random by design).",
    "- Write `outcome` on every row: SUCCESS, MOD FAILURE, RANDOM MISS, ENVIRONMENT FAULT, APPARATUS FAULT, UNRESOLVED or "
    "COULD NOT LOOK. Only SUCCESS speaks for the mod. No other outcome needs a later pass to cancel it. One row per run. "
    "Beside it: `spoiled_by` on an ENVIRONMENT FAULT (what spoiled the run, and the record that shows it) and "
    "`forbidden` (the list of forbidden effects seen; `[]` for none). SUCCESS goes with verdict PASS. MOD FAILURE goes "
    "with FAIL and class MOD. Every other outcome goes with UNMEASURED; add class HARNESS or SITE to an APPARATUS FAULT "
    "only when the check or the scene itself is wrong.",
    "- ENVIRONMENT FAULT only when the record shows that something outside the tested behaviour spoiled the opportunity. "
    "If the mod could have spoiled it: UNRESOLVED. A forbidden effect is a MOD FAILURE in any run. An UNRESOLVED run "
    "holds the scene's pass until someone classes it: that person adds to the row `classed`: `{\"outcome\", \"why\" (six "
    "words at least), \"by\"}`.",
    "- A serious fault (one sighting), or a fault seen again, opens a hunt. A hunt never opens silently: a note "
    "`HUNT OPENED:` on your item and a line in the Conductor log. One command writes both: `python3 "
    "src/RimMandrake/rimflow/hunt_open.py <your item> --what ... --why-it-matters ... --next-step ... --cost ...`.",
    "- When a run names a thing that spoiled it, try to remove that thing. Lean towards building the control.",
    "- No exit asks for every scene in one visit, or for one scene several times in a row."])
# What the Gimme Some Slack and Pyrelands rescues taught (2026-11-16; owner: "let's make these changes to the
# builder/fixers so they act better from now on too"): green on the suite's examples was taken for green everywhere,
# builders tuned between bars that want opposite things, and a rescue ended with open cases as a footnote. Carried by
# every builder and fixer brief: the offline build (brief_text), the certificate (maturation_dispatch.cert_brief) and the
# road-back fixer (maturation_autonomy.fixer_brief). The positive steps are the owner's words, kept verbatim.
# selftest_bar_holds_rule.py. Page: D:\ClaudeWork\rimmandrake\conductor\role_prompt_upgrades_20261116.md.
HOW_A_BAR_HOLDS = "\n".join([
    "## How a bar is shown to hold (owner, 2026-11-16)",
    "",
    "Hunt parameter regimes and regions, not examples. A bar holds over every situation the game can produce for it, "
    "not over the scenes in the suite.",
    "",
    "- Before you change any code, write down that whole range of situations: what the game can vary for this bar "
    "(what the thing connects to, what surrounds it, the player's settings, seeds and time), the regimes and regions "
    "those make, and what you leave out and why. Read that whole range with the bar's own check. A sweep that shows any "
    "failure is swept again densely around those failures before you conclude anything from it.",
    "- Every check you run or write prints its worst value, its limit and how many cases it read. A pass by a hair, "
    "where one more seed or frame could flip it, is a finding to explain, not a pass to bank.",
    "- Before you change a check or the code it reads, search the tests for every check that reads the same thing, and "
    "run them all after each change. A fix that turns one green and another red is two bars in conflict, not a bug in "
    "either.",
    "- The tuning tripwire: the second time you nudge the same number, or when a check you had made pass fails again, "
    "stop tuning. Two bars want different things in the same place. Map where each bar holds across the range of "
    "situations you wrote down, and why; then resolve the two into one thing, or invent something that satisfies both. "
    "In every \"it cannot be done\" claim, tag each limit \"bar\" (the owner's) or \"our own rule\" (code, habit, an "
    "earlier builder's choice), and challenge our own rules first. Relaxing a bar is never yours: it is a question to "
    "the Conductor, with the map and a picture you have looked at.",
    "- The owner's positive steps: Get inventive. Innovate; do not just tune, and do not just diagnose: provide or "
    "repair what is broken. Provide bars where they are missing: that is not cheating, it is making it harder on "
    "yourself. Create instruments to prove your diagnoses. Think outside the box: collapse classes into one or invent new ones as needed to find a way "
    "around the problem.",
    "- Every number you add says where it comes from: a bar, or a fact you measured.",
    "- An old check that turns red when you change something is evidence about your change: find out why. Never edit "
    "it to pass.",
    "- You may not end with open cases. A case your own notes or report list as failing, unlaid, untested but testable "
    "offline, or unexplained is fixed; or proved unreachable by a check you land; or written as a question to the "
    "Conductor with its picture. Only what truly needs the live game or the owner may stay open, each with its command "
    "or its question.",
    RP.RULE,
])
# The offline model, from a mod's first build (owner, 2026-11-17 ~10:50 AM PST: "it feels like the Fable Rescuer again
# found that offline modeling is REALLY informative and useful. Sounds like something that should be instructed to the
# mod builder in general, yes, from the get-go?"). One source: the marked block in roles/fable_rescue.md step 2, which
# the rescue reads in place; the offline build (brief_text) and the road-back fixer (maturation_autonomy.fixer_brief)
# carry it read from there. Item RIMMANDRAKE_TEACH_OFFLINE_MODEL_FIRST_BUILD; selftest_offline_model_rule.py.
OFFLINE_MODEL_SOURCE = os.path.join(HERE, "roles", "fable_rescue.md")


def read_offline_model(path=OFFLINE_MODEL_SOURCE):
    """-> the text between the offline-model markers in fable_rescue.md. A missing file or marker gives a pointer to
    the file instead (the selftest goes red on that; a brief is never refused for it)."""
    try:
        with open(path, encoding="utf-8") as fh:
            t = fh.read()
        a = t.index("-->", t.index("<!-- offline-model: begin")) + 3     # the begin comment spans two lines
        return t[a:t.index("<!-- offline-model: end -->", a)].strip()
    except (OSError, ValueError):
        return ("**The offline model.** Read `src/RimMandrake/rimflow/roles/fable_rescue.md` step 2 (the block "
                "\"The offline model\") before any fix or tuning.")


OFFLINE_MODEL = read_offline_model()
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
    stops, owed = {}, {}
    if isinstance(bad, list):     # a scene that stops at MISSING TOOL undeclared is build work too (as evaluate counts it)
        stops = {k: v for k, v in undeclared_stops(root, mod, tt).items() if k != "__did_not_run__"}
        # a scene still owing script parts to an open item refuses its bar past the walk and live-red exemptions, as
        # evaluate counts it (design/specs/2026-11-19-maturation-record/boundary.md)
        owed = owed_scene_parts(root, mod, tt)
        bad = bad + sorted(b for b in set(stops) | set(owed) if b not in bad)
    out.update({
        "refused_bars": [b for b in bad if b in stops or b in owed or b not in walk and b not in live_red]
        if isinstance(bad, list) else UNM,
        "owed_scene_parts": owed,
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
    sp = {b: i for b, i in (f.get("owed_scene_parts") or {}).items() if b in set(mine)}
    if sp:
        L += ["", "Of these, a deciding scene still owes script parts to an open item (scenes.json `owed_parts_item`); "
              "work and close it: %s." % "; ".join("`%s` (%s)" % (b, ", ".join(i)) for b, i in sorted(sp.items()))]
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
          "- Every offline test you add or edit that decides a bar is proven able to fail before the judge: plant a "
          "fault it must catch and run `python3 src/RimMandrake/rimflow/maturation.py red-seen %s <TEST> --patch "
          "<fault.patch>` (applied, run, reversed; recorded only when it goes red), then commit "
          "`version/evidence/red_seen.json`." % mod,
          "- Remake `design/concepts/%s/version/test_table.json` with the table's own maker (its `made_by` names it) "
          "and run `python3 src/RimMandrake/rimflow/maturation.py next %s`; say the count of bars not runnable "
          "before (%d) and after in your last note." % (mod, mod, len(ids)),
          "- Never run `maturation.py advance`, never judge or send the mod back: the Conductor moves stages.",
          "- One dated line in the journal's history for what you built. Every file you touch stays DIRTY until "
          "`code_review_status.py check` says CLEAN.",
          "- Never guess a defName, field or namespace (RimSage, the def, or `measure`).",
          SELF_FIX_RULE, "", HOW_A_BAR_HOLDS, "", RED_SEEN_RULE, "", OFFLINE_MODEL]
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


def judge_resumed_text(f, session):
    """The opening of a voided blind judge's own session, resumed: the same judge continues its own cycle (no blind
    boundary is crossed), and its run counted nothing."""
    rec = (f.get("exit") or {}).get("record") or "the cycle record"
    return ("**You are the same blind judge, resumed (session %s).** Your run on cycle %s was killed from outside by a "
            "system fault and voided: it spent no trial, and the exit block you left in %s/SUMMARY.md is interim, no "
            "verdict. Your clone is new, from origin/main: what you published stands; check what did not land. Continue "
            "from where you stopped, finish the cycle, and replace the interim block with your final exit block. Your "
            "ledger shard is reopened for your own lines.\n" % (session, f.get("cycle"), rec))


def fresh_cycle_text(f, void):
    """The section a FRESH judge's brief opens with when a voided judge's session cannot be resumed: the old run's
    record is moved aside unread, and this judge starts with no context of it."""
    rec = (f.get("exit") or {}).get("record") or "the cycle record"
    tag = str((void or {}).get("unit") or "void").rsplit("-", 1)[-1]
    return ["## First: open cycle %s fresh" % f.get("cycle"), "",
            "A judge run on this cycle was voided (a system fault; it gave no verdict), and its session cannot be "
            "resumed (%s). Its record is in `%s`. Do NOT open or read it. First move it aside unread: `git mv %s "
            "%s.void-%s`, commit and publish that path alone. Then do the whole cycle as written below, blind." % (
                (void or {}).get("why") or "-", rec, rec, rec, tag), ""]


def reconcile_text(mod, why):
    """The reconcile step a killed or lost holder run owes before anything resumes (spec §3.4, Option B)."""
    return ("**Reconcile first: %s.** Before any other work: (1) in this clone, `git status` and `git log "
            "origin/main..HEAD`; publish what the ledger and tests support, else drop it, and say which in a `note`; "
            "(2) `python3 src/RimMandrake/rimflow/cli.py bridge who`: release a hold your earlier run left; (3) re-read "
            "`python3 src/RimMandrake/rimflow/modledger.py packet --mod %s` for what landed while it was down. Repeat "
            "nothing it already did.\n" % (why, mod))


def _takes_kw(fn, name):
    """Does stand-in fn take keyword `name`? (a selftest's (root, mod) deployed stand-in predates the game.)"""
    return any(p.name == name or p.kind == p.VAR_KEYWORD for p in inspect.signature(fn).parameters.values())


def takes_game(fn):
    """Can this bridge reading name a game (a `game` parameter)? A stand-in that cannot reads game a only."""
    try:
        return "game" in inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return False


COMPANION_ENV = "MATURATION_COMPANION_DLL"     # names the companion DLL to read instead of the game folder's (selftests)
COMPANION_FIX = ("rebuild and deploy it while the game is down: `python3 src/RimMandrake/bridgetools/build.py --gm` "
                 "(plan), then `python3 src/RimMandrake/bridgetools/build.py --gm --apply`")
COMPANION_BUILD_ENV = "MATURATION_COMPANION_BUILD"  # a command run in place of bridgetools/build.py (selftests)


def _companion_cmd(game):
    """The companion rebuild COMPANION_FIX names, for the visit's game: build.py --gm --apply --instance <game>."""
    return (os.environ.get(COMPANION_BUILD_ENV, "").split() or [
        sys.executable, os.path.join(os.path.dirname(HERE), "bridgetools", "build.py")]) + [
        "--gm", "--apply", "--instance", game or "a"]


def companion_current(game="a"):
    """-> (current, why): does the game folder's JawaBench companion hold the companion sources of this tree's HEAD?
    (RIMMANDRAKE_REFUSE_INGAME_VISIT_ON_STALE_COMPANION: on 2026-11-17 GSS visit 2 was owed with the walk's fixed checks
    committed but the deployed DLL STALE, and nothing refused it.) companion_identity.verdict with cover on (a clean build of
    a later commit holding the same sources counts); anything but FRESH (STALE, UNSTAMPED, MISSING, UNMEASURED) is not
    current. game: whose companion; each game has its own install, so a named game's DLL is under its own BridgeTools
    (game_instance.game_dir; RIMMANDRAKE_SPLIT_SECOND_GAME_MODS_FOLDER_SHARED_WITH_FIRST)."""
    bt = os.path.join(os.path.dirname(HERE), "bridgetools")
    if bt not in sys.path:
        sys.path.insert(0, bt)
    import companion_identity as CI
    dll = os.environ.get(COMPANION_ENV)
    if not dll:
        utils = os.path.join(os.path.dirname(HERE), "Utils")
        if utils not in sys.path:
            sys.path.insert(0, utils)
        import game_instance
        dll = os.path.join(game_instance._native(game_instance.game_dir(game or "a")), "BridgeTools", "JawaBench",
                           CI.DLL_NAME)
    v = CI.verdict(dll, REPO, "HEAD", cover=True)
    return v.get("state") == "FRESH", CI.describe(v)


DEPLOY_PLAN_ENV = "MATURATION_DEPLOY_PLAN"     # a command run in place of deploy_custom_mods.py (selftests)
# A launch refused for a cause that ends by itself (a held bridge, his hold on the game): the tick waits, counts no
# fault and spends no try (maturation_autonomy.wait_refusal; design/specs/2026-11-20-launch-refusal-wait-and-deploy)
WAIT_MARK = "REFUSED (a wait, not a fault):"
# The parts of a mod folder RimWorld reads at load: About, LoadFolders.xml, and in each load folder these folders.
# A drift line outside them (a .sh, Source/, a README) cannot change what the game plays.
LOADED_DIRS = ("about", "assemblies", "defs", "patches", "languages", "textures", "sounds", "assetbundles")
ASSET_DIRS = ("textures", "sounds")
# budget: danger=a game that ignores its close holds the repair (it is stopped with /F after this); never reached in the 14 days
# budget: to 2026-11-24; no record of its run
REPAIR_STOP_S = 120     # the boundary page's LIMITS: a game that ignores the close is stopped with /F after this


def _plan_cmd(args):
    return (os.environ.get(DEPLOY_PLAN_ENV, "").split() or [
        sys.executable, os.path.join(os.path.dirname(HERE), "Utils", "deploy_custom_mods.py")]) + list(args)


def _loaded_part(rel):
    """-> the loaded folder a plan path lies in ("defs", "textures", ...; "loadfolders" for LoadFolders.xml), or None
    for a file the game never reads."""
    parts = [x.lower() for x in rel.replace("\\", "/").split("/") if x]
    if parts and parts[-1] == "loadfolders.xml":
        return "loadfolders"
    return next((x for x in parts[:-1] if x in LOADED_DIRS), None)


def _asset_names(rel):
    """-> the paths a def or C# would name for a texture or sound file: its path under Textures/Sounds without the
    extension (and without a facing or mask suffix), and its folder (a Graphic_Random's texPath)."""
    parts = rel.replace("\\", "/").split("/")
    i = next(i for i, x in enumerate(parts) if x.lower() in ASSET_DIRS)
    sub = parts[i + 1:]
    stem = "/".join(sub)[:-len(os.path.splitext(sub[-1])[1]) or None]
    out = {stem, re.sub(r"_(north|south|east|west|m|northm|southm|eastm|westm)$", "", stem)}
    if len(sub) > 1:
        out.add("/".join(sub[:-1]))
    return sorted(x for x in out if x)


def _named_in_repo(names, runner=subprocess.run):
    """-> (the subset of names some def, patch or C# file in the repo names as a whole path, None) or (None, cause).
    A path counts as named when it stands between > < or quotes, as a texPath or a C# string does."""
    if not names:
        return set(), None
    pats = []
    for n in names:
        pats += ["-e", r"[>\"']%s[<\"']" % re.escape(n)]
    try:
        r = runner(["git", "-C", REPO, "grep", "-h", "-o", "-E"] + pats + ["--", "src/*.xml", "src/*.cs"],
                   capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        return None, "%s: %s" % (type(e).__name__, e)
    if r.returncode not in (0, 1):
        return None, "git grep exited %s: %s" % (r.returncode, (r.stderr or "").strip()[:160])
    hits = r.stdout or ""
    return {n for n in names if re.search(r"[>\"']%s[<\"']" % re.escape(n), hits)}, None


def deploy_state(root, mod, runner=subprocess.run, game="a"):
    """-> {state, why, loaded, ignored, args, fix}: the deploy plan of the game's copy of `mod` read for what the game
    LOADS (design/specs/2026-11-20-launch-refusal-wait-and-deploy/boundary.md). deploy_custom_mods.py's plan (never
    --apply), for Baroque Biomes when Biomes.compose.json composes the mod, with --instance <game> for a named game.
    state: current (no drift line in a loaded folder; lines outside one, and game-only textures or sounds no repo
    file names, are `ignored`), drift (loaded drift a plain --apply cures: +, ~, and - lines the repo deleted), stuck
    (a game-only loaded file the repo never deleted: --pull or --prune is a hand's choice), could_not_look (the plan
    did not run, printed neither last line, or the name search failed)."""
    args = ["--compose", "biomes"] if BM.composed_into(root, mod) else ["--mod", mod]
    if game and game != "a":
        args += ["--instance", game]
    fix = "python3 src/RimMandrake/Utils/deploy_custom_mods.py %s --apply" % " ".join(args)
    out = {"state": "could_not_look", "loaded": [], "ignored": [], "args": args, "fix": fix}
    try:
        r = runner(_plan_cmd(args), capture_output=True, text=True, timeout=10800, stdin=subprocess.DEVNULL)  # budget: class=deploy
    except (OSError, subprocess.SubprocessError) as e:
        return dict(out, why="the deploy plan could not read the game copy (%s: %s)" % (type(e).__name__, e))
    text = ((r.stdout or "") + (r.stderr or "")).strip()
    if r.returncode == 0 and "Everything in sync." in text:
        return dict(out, state="current", why="the game's copy of %s matches the repo" % mod)
    if "Drift found." not in text:
        return dict(out, why="the deploy plan could not read the game copy (exit %s: %s)" % (
            r.returncode, (text.splitlines() or ["no output"])[-1][:200]))
    lines = [x.strip() for x in text.splitlines() if x.strip()[:3] in ("~  ", "+  ", "-  ")]
    loaded, ignored, stuck, assets = [], [], [], {}
    for ln in lines:
        sign, rest = ln[0], ln[3:].strip()
        rel, _, note = rest.partition("   (")
        rel = rel.strip()
        part = _loaded_part(rel)
        if part is None:
            ignored.append(ln)
        elif sign == "-" and part in ASSET_DIRS:
            assets[ln] = (rel, note)
        else:
            loaded.append(ln)
            if sign == "-" and "--apply prunes it" not in note:
                stuck.append(rel)
    if assets:
        names = {ln: _asset_names(rel) for ln, (rel, _) in assets.items()}
        named, err = _named_in_repo(sorted({n for v in names.values() for n in v}))
        if named is None:
            return dict(out, why="game-only textures or sounds (%s) could not be checked against the repo's defs: %s"
                        % (", ".join(sorted(rel for rel, _ in assets.values()))[:200], err))
        for ln, (rel, note) in assets.items():
            if set(names[ln]) & named:
                loaded.append(ln)
                if "--apply prunes it" not in note:
                    stuck.append(rel)
            else:
                ignored.append(ln)
    out.update(loaded=loaded, ignored=ignored)
    say = lambda xs: "%s%s" % (", ".join(xs[:4]), " and %d more" % (len(xs) - 4) if len(xs) > 4 else "")  # noqa: E731
    if not loaded:
        return dict(out, state="current", why="the game's copy of %s matches the repo in every file the game loads "
                    "(not loaded or named by nothing, so ignored: %s)" % (mod, say(ignored)))
    if stuck:
        return dict(out, state="stuck", why="the game's copy of %s holds loaded files the repo does not ship and never "
                    "deleted (%s): rescue them with `deploy_custom_mods.py --pull <Mod>` or delete them with `%s "
                    "--prune`, a hand's choice" % (mod, say(stuck), fix))
    return dict(out, state="drift", why="the game's copy of %s differs from the repo in files the game loads (%s); %s"
                % (mod, say(loaded), fix))


def mod_deployed(root, mod, runner=subprocess.run, game="a"):
    """-> (current, why): does the game's copy of `mod` match the repo in every file the game loads? (deploy_state.)
    (2026-11-19: GSS visit 2 was owed with the game's DLL and .srchash older than the repo build; the brief told the
    driver to deploy, and nothing in code checked. 2026-11-20: Pyrelands visit 2 was refused three times on a dev
    script of another member mod and nine textures no def names.) game: whose copy; the plan runs with --instance
    <game>, so game b's own Mods folder is read, never a's."""
    st = deploy_state(root, mod, runner=runner, game=game)
    return st["state"] == "current", st["why"]


def _game_ops():
    utils = os.path.join(os.path.dirname(HERE), "Utils")
    if utils not in sys.path:
        sys.path.insert(0, utils)
    import game_instance
    return game_instance


def _STANDIN_LOCK(game, purpose, seat):
    """A stand-in game (the selftests' game_ops) is never guarded by a real game's lock."""
    return "ok", "stand-in game: no real lock", lambda: None


def _repair_lock(game, purpose, seat):
    """-> (state, text, release): hold game `game`'s driver lock for this process for a repair's game-down window
    (RIMMANDRAKE_REPAIR_PYRELANDS_FORM_REFUSAL_AT_THE_RUN_EIGHT: on 2026-11-22 at 21:07 PST the tick read ArchBig free,
    stopped it and began the companion rebuild without holding it; another run claimed the free lock mid-rebuild, and
    build.py then refused the deploy under that hold). state: ok (held, or no lock on this machine: none to hold), held
    (another live run or his hold: a wait), blind (the lock could not be looked at: a fault). The holder is this
    process, never its parent: the systemd tick's parent never exits, and its hold would never free. While held, this
    process and its children carry RM_HOST_GUARD_GEN (host_guard's inherited take), RM_DRIVER_PID (driver_lock's owner
    of a take) and a seat, so game_instance.stop, build.py and the deploy read the take as their own. release() frees what this call took, and restores the env."""
    import game_lock as GL
    import driver_lock as DL
    try:
        path = GL.lock_path(game)
    except Exception as e:  # noqa: BLE001
        return "blind", "could not find %s's driver lock (%s: %s)" % (_gn(game), type(e).__name__, e), lambda: None
    if not path:
        return "ok", "no driver lock for %s on this machine: none to hold" % _gn(game), lambda: None
    me = dict(DL.my_identity(), pid=os.getpid(), start=DL._proc_start(os.getpid())) if os.name != "nt" else None
    r = GL.claim(game, purpose, seat=seat, identity=me, path=path)
    if not r.get("ok"):
        return ("held" if r.get("code") in (GL.EX_HELD, GL.EX_HIS) else "blind"), r.get("line") or "", lambda: None
    keys = ("RM_HOST_GUARD_GEN", "RIMFLOW_SEAT", "RM_DRIVER_PID")
    was = {k: os.environ.get(k) for k in keys}
    os.environ["RM_HOST_GUARD_GEN"] = str(r.get("generation"))
    os.environ.setdefault("RIMFLOW_SEAT", seat)
    if not r.get("reentrant") and me:
        # driver_lock's owner of a take: `rimflow bridge idle` (game_instance.stop's gate) and build.py compare it with
        # the holder; measured 2026-11-22: without it, the stop's gate called this process's own take NOT TAKEABLE
        os.environ["RM_DRIVER_PID"] = str(os.getpid())

    def release():
        for k, v in was.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        if not r.get("reentrant"):          # a take this tree already held (its window's) is not ours to free
            GL.release(game, seat=seat, path=path)
    return "ok", r.get("line") or "", release


def deploy_repair(root, mod, game, reading, gi, purpose, runner=subprocess.run, sleep=time.sleep, clock=time.time,
                  seat="BENCH", companion=None, lock=None):
    """Holds the game's driver lock across the whole repair (lock: a _repair_lock stand-in, the selftests'); a lock
    another run holds is a wait, nothing done. Then _deploy_repair_held."""
    held = gi.hold_refusal(game)
    if held:
        what = " and ".join(x for x in ("the game copy of %s needs a deploy" % mod if reading else "",
                                         "its JawaBench companion needs a rebuild" if companion else "") if x)
        return "wait", "%s %s and %s" % (WAIT_MARK, what, held.splitlines()[0])
    state, ltxt, release = (lock or _repair_lock)(game, purpose, seat)
    if state == "held":
        return "wait", "%s %s is held by another run, so it cannot go down for the repair: %s" % (
            WAIT_MARK, _gn(game), ltxt)
    if state != "ok":
        return "fail", "could not hold %s for the repair: %s; nothing done" % (_gn(game), ltxt)
    try:
        return _deploy_repair_held(root, mod, game, reading, gi, purpose, runner, sleep, clock, seat, companion)
    finally:
        release()


def _deploy_repair_held(root, mod, game, reading, gi, purpose, runner=subprocess.run, sleep=time.sleep,
                        clock=time.time, seat="BENCH", companion=None):
    """-> (state, text): cure a deploy_state reading of `drift`, a stale JawaBench companion, or both, before an in-game
    visit launches. state: ok (repaired, read again current), wait (his hold on the game: WAIT_MARK, nothing done), fail
    (the cause named). Game down first when it is up (a DLL cannot be written under a running game, and a def is only
    read at startup), the companion rebuild (_companion_cmd) when `companion` (its reader) is given, the plan's --apply
    for the visit's game when `reading` is given, the game up again when it was up, and each read again: one stop and
    one start for both. seat: the launch's, handed to the stop's bridge reading (the tick's env names none)."""
    held = gi.hold_refusal(game)
    if held:
        what = " and ".join(x for x in ("the game copy of %s needs a deploy" % mod if reading else "",
                                         "its JawaBench companion needs a rebuild" if companion else "") if x)
        return "wait", "%s %s and %s" % (WAIT_MARK, what, held.splitlines()[0])
    try:
        was_up = gi.running(game)
    except Exception as e:  # noqa: BLE001  Blind: could not look, nothing is done on a guess
        return "fail", "could not read whether %s is running (%s: %s); nothing deployed" % (_gn(game), type(e).__name__, e)
    done = []
    if was_up:
        try:
            # The wait reads the stopped pids by pid: a closing game reads an empty command line, and pids() raised
            # Blind on our own stopped game (RIMMANDRAKE_REPAIR_PYRELANDS_FORM_REFUSAL_AT_THE_RUN_SIX). The /F stop
            # still goes through stop(), which attributes again.
            stopped = gi.pids(game)
            rc, txt = gi.stop(name=game, purpose=purpose, seat=seat)
            t0 = clock()
            while gi.alive(stopped) and clock() - t0 < REPAIR_STOP_S:
                sleep(2)
            if gi.alive(stopped):
                rc, txt = gi.stop(name=game, purpose=purpose, force=True, seat=seat)
                sleep(3)
            if gi.alive(stopped):
                return "fail", "%s did not stop for the deploy (%s)" % (_gn(game), txt)
        except Exception as e:  # noqa: BLE001  Refused (a hold or a bridge read) or Blind
            msg = "%s: %s" % (type(e).__name__, e)
            if "held" in str(e) or "TAKEABLE" in str(e):
                return "wait", "%s %s could not be stopped for the deploy: %s" % (WAIT_MARK, _gn(game), msg)
            return "fail", "%s could not be stopped for the deploy: %s" % (_gn(game), msg)
        done.append("%s stopped" % _gn(game))

    def run(cmd):
        try:
            r = runner(cmd, capture_output=True, text=True, timeout=10800, stdin=subprocess.DEVNULL)  # budget: class=deploy
            return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()
        except (OSError, subprocess.SubprocessError) as e:
            return 1, "%s: %s" % (type(e).__name__, e)
    if companion:
        cmd = _companion_cmd(game)
        rc, txt = run(cmd)
        if rc:
            last = [x.strip() for x in txt.splitlines() if x.strip()]
            bad = [x for x in last if x.startswith(("CANNOT", "REFUSING", "DEPLOY", "ERROR", "error", "FAIL"))]
            return "fail", "the JawaBench companion rebuild failed (`%s`, exit %s: %s)%s" % (
                " ".join(cmd[-5:]), rc, "; ".join(bad[:3]) or (last or ["no output"])[-1][:200],
                "; %s, left down" % done[0] if done else "")
        done.append("companion rebuilt and deployed (build.py --gm --apply --instance %s)" % game)
    if reading:
        rc, txt = run(_plan_cmd(reading["args"] + ["--apply"]))
        if rc:
            bad = [x.strip() for x in txt.splitlines() if x.strip().startswith(("!", "STILL", "NOTHING", "DEF GUARD"))]
            return "fail", "the deploy failed (`%s`, exit %s: %s)%s" % (
                reading["fix"], rc, "; ".join(bad[:3]) or (txt.splitlines() or ["no output"])[-1][:200],
                "; %s, left down" % done[0] if done and not done[0].startswith("companion") else "")
        done.append("deployed (%s)" % reading["fix"])
    if was_up:
        try:
            rc, txt = gi.launch(name=game, wait=False)
        except Exception as e:  # noqa: BLE001
            rc, txt = 1, "%s: %s" % (type(e).__name__, e)
        if rc:
            return "fail", "deployed, but %s did not start again: %s" % (_gn(game), txt)
        done.append("%s started (%s)" % (_gn(game), txt))
    if companion:
        cur, cwhy = companion(game=game)
        if not cur:
            return "fail", "after the rebuild the JawaBench companion is still not current: %s" % cwhy
    if reading:
        again = deploy_state(root, mod, runner=runner, game=game)
        if again["state"] != "current":
            return "fail", "after the deploy the game copy of %s still differs: %s" % (mod, again["why"])
    return "ok", "; ".join(done)


def deploy_paths(root, mod):
    """-> the repo paths whose change makes a deploy of `mod` old: the mod's own folder, or for a composed mod every
    folder Biomes.compose.json folds in, and the companion's sources (design/specs/2026-11-24-game-deploy-own-unit)."""
    base, comp = "src/RimMandrake/", BM.composed_into(root, mod)
    if comp is None:
        return [base + mod, base + "bridgetools"]
    try:
        with open(BM.compose_file(root), encoding="utf-8") as f:
            d = json.load(f)
        names = {e["source"] for e in d.get("entries") or ()} | {(d.get("shell") or {}).get("source") or mod, mod}
    except (OSError, ValueError, AttributeError, TypeError, KeyError):
        return ["src"]          # which folders are composed is unknown: any source change makes it old
    return [base + n for n in sorted(names)] + [base + "Biomes.compose.json", base + "bridgetools"]


def game_repair(root, mod, game, kind, purpose, seat="BENCH", game_ops=None, companion=None, lock=None):
    """The body of the Dispatch step's deploy unit (game_deploy_worker runs it as `game-repair`), so that the plan, the
    --apply and the second plan hold no tick. kind: visit (the companion, when not current, is rebuilt too; a copy that
    is current needs nothing) or walk (the walk build's deploy, for drift only). The game's driver lock is held from
    before the first plan until the game is up again. -> {state: ok | wait | fail, text, game, kind, sha (of this tree),
    generation (of the hold), paths}."""
    gi = game_ops or _game_ops()
    out = {"mod": mod, "game": game, "kind": kind, "generation": None, "sha": None, "paths": deploy_paths(root, mod)}
    try:
        r = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=1800)  # budget: class=call
        r.check_returncode()
    except (OSError, subprocess.SubprocessError) as e:
        return dict(out, state="fail", text="could not read this tree's commit, so nothing is deployed: %s: %s" % (
            type(e).__name__, e))
    out["sha"] = r.stdout.strip()
    held = gi.hold_refusal(game)
    if held:
        return dict(out, state="wait", text="%s the game copy of %s needs a reading and %s" % (
            WAIT_MARK, mod, held.splitlines()[0]))
    state, ltxt, release = (lock or _repair_lock)(game, purpose, seat)
    if state == "held":
        return dict(out, state="wait", text="%s %s is held by another run, so the deploy of %s cannot start: %s" % (
            WAIT_MARK, _gn(game), mod, ltxt))
    if state != "ok":
        return dict(out, state="fail", text="could not hold %s for the deploy: %s; nothing done" % (_gn(game), ltxt))
    try:
        gen = os.environ.get("RM_HOST_GUARD_GEN")
        out["generation"] = int(gen) if gen and gen.isdigit() else None
        creader = (companion or companion_current) if kind == "visit" else None
        ccur, cwhy = creader(game=game) if creader else (True, "")
        reading = deploy_state(root, mod, game=game)
        if reading["state"] not in ("current", "drift"):
            return dict(out, state="fail", text=reading["why"])
        if kind == "walk" and reading["state"] != "drift":
            return dict(out, state="fail", text=reading["why"])
        if reading["state"] == "current" and ccur:
            return dict(out, state="ok", text="nothing to deploy: %s" % reading["why"])
        state, text = _deploy_repair_held(root, mod, game, reading if reading["state"] == "drift" else None, gi, purpose,
                                          seat=seat, companion=None if ccur else creader)
        return dict(out, state=state, text=text)
    finally:
        release()


def game_brief(game, full_list=None):
    """The brief's section naming the run's game: game_instance.brief (RIMMANDRAKE_LAUNCH_BOTH_GAMES_STEAM_REFUSES_A_BESIDE_B);
    full_list: the visit's full-list checks, which a run on a named game records UNMEASURED."""
    utils = os.path.join(os.path.dirname(HERE), "Utils")
    if utils not in sys.path:
        sys.path.insert(0, utils)
    import game_instance
    return game_instance.brief(game, full_list)


def live_twins(mod, stage, item, status=None):
    """-> (the live detached runs a launch of MOD's STAGE under ITEM would twin, None) or (None, cause) when the
    record folder cannot be listed (could not look is never "no twin"). A twin: a launching or running record
    (detached_helper.live_status) whose env names this mod and stage, or whose item is this item. [] is looked, none
    (design/specs/2026-11-19-maturation-launch-twin/boundary.md)."""
    import detached_helper as DH
    status = status or DH.live_status
    try:
        d = DH.runs_dir()
        names = sorted(os.listdir(d))
    except OSError as e:
        return None, "%s: %s" % (type(e).__name__, e)
    out = []
    for n in names:
        if not n.endswith(".json") or n.endswith(".out.json"):
            continue
        rec = DH.read_record(n[:-5])
        if not rec or not rec.get("unit"):
            continue
        env = rec.get("env") if isinstance(rec.get("env"), dict) else {}
        same = env.get("RM_CONTROL_MOD") == mod and env.get("RM_CONTROL_STAGE") == stage
        if (same or (item and rec.get("item") == item)) and status(rec) in ("launching", "running"):
            out.append({"unit": rec["unit"], "stage": env.get("RM_CONTROL_STAGE") or UNM, "item": rec.get("item") or UNM,
                        "at": rec.get("at")})
    return out, None


def _twins_reader(runner, twins):
    """The twin reader a launch uses: the one given, else live_twins for a real launch; a stand-in runner starts no
    unit, so it has no twin to guard against and reads no records."""
    if twins is not None:
        return twins
    return live_twins if runner is subprocess.run else None


def _visit_repair(root, mod, f, game, seat, companion, deployed, game_ops, repair_lock):
    """A hand launch's companion reading, deploy plan and repair before an in-game visit (launch_mod's own arguments; the
    Dispatch step's run in their own unit and reach launch_mod as `repaired`). -> None when the game plays the repo, else
    the refusal."""
    creader = companion or companion_current
    ccur, cwhy = creader(game=game)
    # a stale companion is cured as drift is (RIMMANDRAKE_REPAIR_FLOWWORKS_FORM_REFUSAL_AT_THE_RUN_FOUR): the real
    # game, or a stand-in game_ops; a companion stand-in or fixture DLL with no game_ops refuses as before
    cfix = not ccur and (game_ops or (companion is None and not os.environ.get(COMPANION_ENV)))
    if not ccur and not cfix:
        return ("REFUSED: %s's in-game visit %s would drive an old JawaBench companion, so its checks would not be "
                "the ones committed: %s; %s" % (mod, f.get("visit"), cwhy, COMPANION_FIX))
    if deployed:
        cur, dwhy = deployed(root, mod) if not _takes_kw(deployed, "game") else deployed(root, mod, game=game)
        reading = None
    else:
        reading = deploy_state(root, mod, game=game)
        cur, dwhy = reading["state"] == "current", reading["why"]
    dfix = not cur and reading and reading["state"] == "drift" and (game_ops or not os.environ.get(DEPLOY_PLAN_ENV))
    if not cur and not dfix:
        return "REFUSED: %s's in-game visit %s would play a game copy not checked against the repo: %s" % (
            mod, f.get("visit"), dwhy)
    if dfix or cfix:
        # the launch cures what --apply cures, and a stale companion, for the game the visit drives, in one game-down
        # window (design question 3 of RIMMANDRAKE_DEPLOY_BEFORE_GAME_VISIT_PYRELANDS_REFUSED_THRICE)
        what = " and ".join(x for x in ("deploy %s" % mod if dfix else "", "rebuild the companion" if cfix else "")
                            if x)
        state, rwhy = deploy_repair(root, mod, game, reading if dfix else None, game_ops or _game_ops(),
                                    "%s before its in-game visit %s" % (what, f.get("visit")), seat=seat,
                                    companion=creader if cfix else None,
                                    lock=repair_lock or (_STANDIN_LOCK if game_ops else None))
        if state == "wait":
            return rwhy
        if state != "ok":
            return "REFUSED: %s's in-game visit %s needed a repair first (%s), and it failed: %s" % (
                mod, f.get("visit"), what, rwhy)
    return None


def launch_mod(root, mod, budget_usd, item, model="opus", seat="BENCH", runner=subprocess.run, bridge=None,
               resume=None, bars=None, preface=None, env=None, session=None, reconcile=None, game=None, companion=None,
               deployed=None, twins=None, game_ops=None, continue_on_cap=0, repair_lock=None, fresh_of=None,
               repaired=None):
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
    reconcile step (RIMMANDRAKE_RESUME_HOLDER_SESSIONS_TO_400K_KILL_AND_RESUME). game: the game an in-game run drives
    (the Dispatch step's free choice): it reaches the unit as RM_GAME_INSTANCE and the brief, and the bridge read is
    that game's. companion: a stand-in for companion_current (an in-game visit refuses a companion not current);
    deployed: a stand-in for mod_deployed (an in-game visit refuses a game copy of the mod that differs from the repo).
    twins: a stand-in for live_twins: a live run on the same mod and stage, or the same item, refuses the launch
    (RIMMANDRAKE_GUARD_HAND_LAUNCH_AGAINST_DISPATCHER_TWIN_RUN: a hand launch twinned the Dispatch step's cycle 6).
    game_ops: a stand-in for game_instance (running, hold_refusal, stop, pids, alive, launch) for the deploy before a visit
    (deploy_repair); with a stand-in deploy plan (MATURATION_DEPLOY_PLAN) and none given, drift refuses as before. A
    refusal whose cause ends by itself (the bridge not takeable, his hold on the game) starts with WAIT_MARK. At the
    blind challenge, a session (a voided judge's own, the Dispatch step's judge_resume) opens with
    judge_resumed_text, and fresh_of (a voided judge whose session cannot resume) opens with fresh_cycle_text; either
    launches on owed "resume" (design/specs/2026-11-23-resume-voided-blind-judge/boundary.md). repaired: the result of
    the deploy unit the Dispatch step ran for this visit (game_repair's); with it, an in-game launch reads no plan, deploys
    nothing and rebuilds nothing here (design/specs/2026-11-24-game-deploy-own-unit/boundary.md)."""
    if game:
        env = dict(env or {}, RM_GAME_INSTANCE=game)
    game = (env or {}).get("RM_GAME_INSTANCE") or "a"
    if not isinstance(budget_usd, (int, float)) or isinstance(budget_usd, bool) or budget_usd <= 0:
        return 2, "REFUSED: a spend cap is required (--budget-usd > 0); there is no default", None
    if not item:
        return 2, "REFUSED: --item is required (a ledger item filed on origin/main)", None
    text, f = brief_text(root, mod, budget_usd, bars=bars)
    ok_owed = ("cycle", "run") + (("no exit block",) if resume else ()) + (("resume",) if resume or fresh_of else ())
    if fresh_of and f.get("stage") == "blind_challenge":
        head, _, rest = text.partition("\n\n")
        text = "\n".join([head, ""] + fresh_cycle_text(f, fresh_of)) + "\n" + rest
    elif resume and f.get("stage") in ("blind_challenge", "in_game"):
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
        read, purpose = bridge or bridge_idle, "%s in-game acceptance visit %s" % (mod, f.get("visit"))
        if takes_game(read):
            go, why = read(purpose, seat, game=game)
        else:
            go, why = read(purpose, seat) if game == "a" else (False, "this bridge reading cannot name %s" % _gn(game))
        if not go:
            return 2, "%s the bridge of %s is not takeable for %s's in-game visit %s: %s" % (
                WAIT_MARK, _gn(game), mod, f.get("visit"), why), None
        if repaired is not None:
            if repaired.get("state") != "ok":
                why = str(repaired.get("text") or UNM)
                return 2, why if why.startswith(WAIT_MARK) else (
                    "REFUSED: %s's in-game visit %s needed its game copy read or deployed first, and it failed: %s" % (
                        mod, f.get("visit"), why)), None
        else:
            why = _visit_repair(root, mod, f, game, seat, companion, deployed, game_ops, repair_lock)
            if why:
                return 2, why, None
        text = text.rstrip("\n") + "\n\n" + game_brief(game, f.get("full_list"))
    elif f.get("stage") != "offline_build":
        return 2, ("REFUSED: %s stands at %s; only an offline build, a blind challenge or an in-game acceptance "
                   "launches from here" % (mod, f.get("stage"))), None
    elif f.get("owed") != "build":
        return 2, "REFUSED: %s owes no build work (%s)" % (mod, f.get("owed")), None
    elif bars and set(bars) - set(f.get("refused_bars") or []):
        return 2, "REFUSED: the batch names bars %s is not refusing: %s" % (
            mod, ", ".join(sorted(set(bars) - set(f.get("refused_bars") or []))[:6])), None
    read = _twins_reader(runner, twins)
    if read is not None:
        got, why = read(os.path.basename(os.path.normpath(mod)), f.get("stage"), item)
        if got is None:
            return 2, ("REFUSED: could not read the detached run records, so a twin run of %s's %s cannot be ruled out: "
                       "%s" % (mod, f.get("stage"), why)), None
        if got:
            return 2, ("REFUSED: %s's %s already has a live run: %s; launch again when it ends (or stop it)" % (
                mod, f.get("stage"), "; ".join("%s (stage %s, item %s)" % (x["unit"], x["stage"], x["item"])
                                               for x in got))), None
    if preface:
        text = preface.rstrip("\n") + "\n\n---\n\n" + text
    if reconcile:
        text = reconcile_text(mod, reconcile) + "\n" + text
    if session:
        text = (judge_resumed_text(f, session) if f.get("stage") == "blind_challenge" else
                resumed_text(mod, session)) + "\n" + text
    path = os.path.join(brief_dir(), "%s-%d.md" % (mod, int(now_ts())))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    argv = [sys.executable, detached_helper_path(), "launch", "--seat", seat, "--item", item, "--brief-file", path,
            "--model", model, "--budget-usd", "%g" % budget_usd] + (["--resume", session, "--planned-resume"] if session else []) + (
        # a run stopped by its spend cap gets detached_helper's own continuation, this many times (left_open_continue)
        ["--continue-on-cap", str(int(continue_on_cap))] if continue_on_cap else [])
    env = dict(env or {}, RM_CONTROL_MOD=os.path.basename(os.path.normpath(mod)),
               **({"RM_CONTROL_STAGE": f["stage"]} if f.get("stage") else {}))     # admission's scopes (control.py)
    for k, v in sorted((env or {}).items()):
        argv += ["--env", "%s=%s" % (k, v)]
    r = runner(argv, capture_output=True, text=True, timeout=10800, stdin=subprocess.DEVNULL)  # budget: class=launch
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


def _lane1_deferred(r, tt, named=None):
    """A lane-1 row the blind exit defers to Stage 6 (not a pass, not a block): a `not_kernel` UNSETTLED row naming at
    least one bar, every one of them in the test table and proving outside OFFLINE_PROVES. The blind brief asks lane 1 to
    write a game-side bar this way; it proves live through its stage-6 checks (ingame_debts carries it there). A row
    naming an offline bar, or a bar the table does not hold, still blocks (RIMMANDRAKE_DEFER_BLIND_EXIT_STAGE_SIX_ROWS_
    NEVER_OFFLINE; the loophole ef6a38dbb6 closed stays closed). named ({bar: [item ids]}, a game-only move's bars that
    its items name) also defers an offline bar that a named game-only item carries to Stage 6."""
    if not isinstance(r, dict) or "_bad" in r or str(r.get("kind", "")).lower() != "not_kernel" or \
            str(r.get("verdict", "")).upper() != "UNSETTLED":
        return False
    at = {b.get("id"): str(b.get("proves_at")) for b in (tt or {}).get("bars") or [] if isinstance(b, dict)}
    bars = _split_bars(r.get("bars"))
    return bool(bars) and all(b in at and (at[b] not in OFFLINE_PROVES or bool((named or {}).get(b))) for b in bars)


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


JUDGE_SAYS_FALSE = "the judge's block says exit_met false"
AGAINST_WRONG = ("check", "scene")


def _commit_paths(root, sha):
    """-> a probe_result answer: the paths commit sha changed (value), none (empty), or could_not_look naming why."""
    import probe_result as PR
    try:
        p = subprocess.run(["git", "-C", root, "diff-tree", "--no-commit-id", "--name-only", "-r", str(sha)],
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        return PR.could_not_look("git diff-tree %s: %s" % (sha, e))
    if p.returncode != 0:
        return PR.could_not_look("git diff-tree %s exited %d: %s" % (sha, p.returncode, p.stderr.strip()[:120]))
    paths = [x for x in p.stdout.split("\n") if x.strip()]
    return PR.value(paths) if paths else PR.empty()


EDIT_KEYS = ("edited", "tests_edited")      # the brief names no shape; both keys are on disk (EK cycle 6 wrote the second)


def edit_rows(te):
    """-> the edits list of a tests_edited.json: a list, or a dict's "edited" or "tests_edited" list; None when it holds
    none. Reading either key is the fault-of-form rule: a shape the brief never fixed is read, never refused
    (RIMMANDRAKE_READ_TESTS_EDITED_KEY_JUDGE_NAMED_ITS_OWN)."""
    if isinstance(te, list):
        return te
    if isinstance(te, dict):
        for k in EDIT_KEYS:
            if isinstance(te.get(k), list):
                return te[k]
    return None


def _edited_paths(te):
    rows = edit_rows(te)
    return {str(x.get("path") if isinstance(x, dict) else x) for x in rows or [] if x}


def check_repair(root, x, fx, edited):
    """-> (True, None) when FIXED Problem x is a wrong check or scene repaired, not a mod fix: `against` check or scene,
    its fixes.jsonl row fx names its `plant` (red: the repaired check on that plant; green: on the real build; read_exit
    checks the rcs), and the fix commit changes only paths in tests_edited.json or the cycle's record. Else (False, why):
    a mod fix, which owes one fresh reader. A commit git cannot read counts as a mod fix, and why names the cause
    (owner, 2026-11-20, RIMMANDRAKE_ENACT_WRONG_CHECK_FIXED_IN_SITTING_NOT_RETURNED)."""
    if str(x.get("against", "")).lower() not in AGAINST_WRONG:
        return False, "against %s, not check or scene" % (x.get("against") or "nothing")
    if not isinstance(fx, dict) or not str(fx.get("plant") or "").strip():
        return False, "its fixes.jsonl row names no plant"
    sha = fx.get("sha") or (str(x.get("status", "")).split() + [""])[1]
    if not sha:
        return False, "no fix sha"
    paths = _commit_paths(root, sha)
    if not paths.ok:
        return False, str(paths)
    if not paths:
        return False, "commit %s changed no file" % sha
    rec = "design/concepts/%s/%s/" % (x.get("_mod", ""), BLIND_DIR)
    other = [p for p in paths if p not in edited and not p.startswith(rec)]
    return (False, "commit %s changes %s, not in tests_edited.json" % (sha, ", ".join(other[:3]))) if other else (True,
                                                                                                                  None)


def read_exit(root, mod, n, tt=None, game_only_bars=None):
    """-> {cycle, state, why[], claimed, checks}: the program's reading of cycle n's exit.

    state: absent (no cycle_n folder) | no_exit_block (no Exit block with the three keys yet: a cycle in progress, or
    one that ended without writing it) | met | not_met. met needs the judge's block to say exit_met true AND every file
    check of FORMAT_NOTES to agree: each offline bar green in the block and each of its deciders PASS on the cycle's own
    rerun (reruns_after_fix.jsonl rows over reruns.jsonl), no Problem whose status is not FIXED, a fixes.jsonl row for
    each FIXED Problem shown red (an rc non-zero) then green (every rc zero), no FAIL row in lane 1, tests_edited.json
    present, and the planted-fault results ending tree_clean_after true. A lane-1 FAIL (recorded blind, before the
    fixes) clears only when LANE1_AFTER_FIX has no FAIL and shows it PASS, or when a Polish fault names that row in its
    evidence (Polish is not part of passing; the reading prints each such row for the steward to confirm). Every fault
    must carry a class, Problem or Polish: an unclassed one could hide an open Problem. Any doubt reads not_met. A
    FIXED Problem that is a check repair (check_repair) owes nothing more; a FIXED mod Problem owes one fresh reader's
    sound review in lane2/fix_reviews.jsonl (review_sound), and with every review sound and every other file check
    agreeing, a judge's exit_met false is read as that owed reader (owner, 2026-11-20).

    game_only_bars ({bar: [item ids]}): given only for a game-only move whose `game_only` clause passed. Then two
    things do not count, and nothing else changes: a lane-1 not_kernel UNSETTLED row whose every bar a named game-only
    item carries (_lane1_deferred), and the fresh reader owed only for the cycle's own FIXED Problems (with every
    file check agreeing, the judge's exit_met false is that owed reader). An unfixed Problem, any other file check, or a
    judge's false in a cycle that fixed nothing still reads not_met (RIMMANDRAKE_UNBLOCK_GAME_ONLY_ADVANCE_AT_BLIND_EXIT)."""
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
        why.append(JUDGE_SAYS_FALSE)
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
    named = game_only_bars or {}
    deferred = sorted({r.get("id", "?") for r in l1 or [] if _lane1_deferred(r, tt, named)})
    fails = [r.get("id", "?") for r in l1 or [] if (str(r.get("verdict", "")).upper() not in LANE1_OK or "_bad" in r)
             and not _lane1_deferred(r, tt, named)]
    by_item = {r.get("id", "?"): sorted({i for b in _split_bars(r.get("bars")) for i in named.get(b) or ()})
               for r in l1 or [] if _lane1_deferred(r, tt, named) and not _lane1_deferred(r, tt)}
    if deferred:
        out["checks"]["lane1_deferred_to_stage6"] = deferred
    if by_item:
        out["checks"]["lane1_deferred_to_game_only_items"] = by_item
    if l1 and not fails:
        out["checks"]["lane1_fail_cleared_after_fix"] = True     # nothing to clear: no row blocks
    if fails:
        # lane 1 is recorded blind, before the fixes, and stays as recorded: a FAIL there is how a Problem is found. It
        # clears only when lane 1 rerun after the fixes (LANE1_AFTER_FIX) has no FAIL and shows each of those rows PASS.
        after = _jsonl(os.path.join(d, LANE1_AFTER_FIX))
        bad_after = [r.get("id", "?") for r in after or [] if (str(r.get("verdict", "")).upper() not in LANE1_OK
                     or "_bad" in r) and not _lane1_deferred(r, tt, named)]
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
    elif edit_rows(te) is None:
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
    edited = _edited_paths(te)
    read = {x.get("id", "?"): check_repair(root, dict(x, _mod=mod), fixes.get(x.get("id")), edited)
            for x in problems if str(x.get("status", "")).startswith("FIXED")}
    repairs = [i for i, (ok, _) in read.items() if ok]
    out["checks"]["mod_fixes_why"] = {i: w for i, (ok, w) in read.items() if not ok}
    out["checks"]["fixed_this_cycle"] = [x.get("id", "?") for x in problems if str(x.get("status", "")).startswith("FIXED")]
    # a wrong check repaired and shown on its plant and the real build owes no new judge: the mod did not change
    out["checks"]["check_repairs"] = repairs
    fixed = [i for i in out["checks"]["fixed_this_cycle"] if i not in repairs]
    if fixed and game_only_bars is not None and all(w == JUDGE_SAYS_FALSE for w in why):
        # a game-only move: the owed judge is not counted (the Conductor's act on
        # RIMMANDRAKE_UNBLOCK_GAME_ONLY_ADVANCE_AT_BLIND_EXIT); each fix was shown red then green above
        out["checks"]["judge_owed_not_counted_game_only"] = fixed
        del why[:]
    elif fixed:
        # the blind judge fixes the mod in the sitting, and ONE fresh reader that did not make the fix checks only that
        # fix, once (owner, 2026-11-20: "I agree with your blind judge -> fresh reader argument."); this replaces the
        # whole new blind cycle RIMMANDRAKE_SEND_FIXES_TO_NEW_BLIND_JUDGE sent a fixed mod to
        rv = fix_reviews(os.path.join(d, "lane2", FIX_REVIEWS))
        read_rv = {i: review_sound(rv, i, (fixes.get(i) or {}).get("unit")) for i in fixed}
        owed = [i for i in fixed if not read_rv[i][0]]
        if owed:
            out["checks"]["fix_reader_owed"] = owed
        if all(w == JUDGE_SAYS_FALSE for w in why):
            del why[:]          # a judge that fixed the mod wrote false: the reader below decides
            if owed:
                why.append("one fresh reader is owed for %d mod fix(es) made in this cycle (%s): a run that did not make "
                           "the fix reads only that fix, once, and writes %s/lane2/%s; the steward run is that reader "
                           "(file nothing new)" % (len(owed), "; ".join("%s: %s" % (i, read_rv[i][1]) for i in owed[:6]),
                                                   rel(mod, base), FIX_REVIEWS))
            else:
                out["checks"]["fix_readers_sound"] = fixed
    out["state"] = "not_met" if why else "met"
    if not why:
        pol = out["checks"].get("lane1_fail_left_as_polish") or {}
        why.append("the block says exit_met %s and every file check agrees (%d offline bars, %d deciders rerun PASS)%s%s"
                   % ("true" if blk["exit_met"] else "false (read as the owed fix reader, now done)"
                      if out["checks"].get("fix_readers_sound") else "false (the owed judge, not counted on a game-only "
                      "move)", len(bars), sum(len(x[1]) for x in bars), "; lane-1 FAIL left as Polish, not part of passing (the "
                      "steward confirms the move): %s" % ", ".join("%s (%s)" % kv for kv in sorted(pol.items()))
                      if pol else "", "; lane-1 not_kernel UNSETTLED row(s) deferred to Stage 6, owed there: %s" % ", ".join(
                          deferred[:8]) if deferred else ""))
        if out["checks"].get("judge_owed_not_counted_game_only"):
            why.append("game-only move: the fresh reader owed for %d FIXED Problem(s) (%s) is not counted; each fix "
                       "was shown red then green in lane2/fixes.jsonl" % (len(fixed), ", ".join(fixed[:6])))
        if out["checks"].get("fix_readers_sound"):
            why.append("%d mod fix(es) made in this cycle, each read sound by one fresh reader: %s" % (
                len(fixed), ", ".join(fixed[:6])))
        if by_item:
            why.append("game-only move: lane-1 row(s) on offline bars carried by named game-only items: %s" % "; ".join(
                "%s -> %s" % (k, ", ".join(v)) for k, v in sorted(by_item.items())))
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
    if out["owed"] in ("no exit block", "exit met", "exit not met"):
        # a VOID judge run gave no verdict: its block is interim, and the cycle resumes (design/specs/
        # 2026-11-23-resume-voided-blind-judge/boundary.md)
        vr = void_judge_run(mod, "%s#%s" % (out["version"], out["visit_first"]), n)
        if isinstance(vr, dict):
            out.update(void_run=vr, owed="resume")
        elif vr:
            blocked.append("whether blind cycle %d's last judge run was voided is UNMEASURED: %s" % (n, vr))
            out["owed"] = "blocked"
    return out


def void_resume_text(bf):
    """-> the line that says a voided judge run's block is no verdict and what the tick does with the cycle."""
    vr = bf.get("void_run") or {}
    return ("its last judge run %s was voided (%s: %s), so its exit block in %s/SUMMARY.md is interim, no verdict; "
            "the tick resumes that judge's own session (ledger run %s), or opens the cycle fresh when the session "
            "cannot be resumed" % (vr.get("unit"), vr.get("void") or vr.get("class"), str(vr.get("why") or "-")[:160],
                                   (bf.get("exit") or {}).get("record", "the cycle record"), vr.get("run") or UNM))


def void_judge_run(mod, vid, n):
    """-> run_void.voided_cycle_run read from the Dispatch tick's state (None: no void, or no state yet), or a text
    naming why that state could not be read."""
    import run_void as RV
    d = os.environ.get("RM_MATURATION_DISPATCH_DIR")
    try:
        if not d:
            import doorbell
            d = os.path.join(doorbell.state_dir(), "maturation")
        with open(os.path.join(d, "state.json"), encoding="utf-8") as fh:
            st = json.load(fh)
        st = RV.sync_dispatch(st) if isinstance(st, dict) else None
    except FileNotFoundError:
        return None
    except Exception as e:  # noqa: BLE001  could not look: said, never read as "no void"
        return "%s/state.json: %s: %s" % (d, type(e).__name__, str(e)[:160])
    if not isinstance(st, dict):
        return "%s/state.json is not an object" % d
    return RV.voided_cycle_run((st.get("mods") or {}).get(mod), vid, n)


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
         "- Offline by default: no game, no bridge, no deploy, no ModsConfig change, unless a fix needs the live "
         "game: then take it when it is free (the rule under \"What you may and may not edit\"), and release it.",
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
    L += ["", "**Where lane 1 starts.** Start with the %d offline bars (`proves_at` %s); they are the main work. The "
          "kernels below are the files their deciders read:" % (len(bars), " or ".join(OFFLINE_PROVES))]
    for b, deciders in bars:
        k = _kernel_files(tt, deciders, sdir)
        L.append("- `%s`: %s" % (b, ", ".join("`%s`" % x for x in k) if k else
                                 "no kernel named by the table: find it from the bar's words, or write one "
                                 "`not_kernel` row"))
    if sdir:
        ks, nk = _globbed(root, sdir, r"(Math|Kernel)\.cs$", 15)
        L.append("")
        L.append("After those, take the stage-6 bars whose logic plainly lives in a kernel (%d `*Math.cs` / "
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
          "shrunk form). A FAIL row names the violated bar, the reproducing case and the attainable result that would pass "
          "it. An UNSETTLED row states what remains undecided and the specific case, evidence or instrument that would "
          "settle it. **Commit lane 1 before you open "
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
          "from stderr). After a fix of yours, run again only the deciders the fix touches (`python3 "
          "src/RimMandrake/rimflow/rerun_relation.py --mod %s --tests all --old <the fix's parent>` names them) and "
          "write those rows to `lane2/reruns_after_fix.jsonl`; every other decider keeps its `reruns.jsonl` row (root "
          "CLAUDE.md, After a change, only the checks that the change touches run again)." % mod, "",
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
          "<sha>, or NOTED_FOR_CONDUCTOR), `against` (mod, check or scene: which one is wrong)%s. File a fault as a rimflow "
          "item (skill `using-rimflow`, `--why`) only when it passes test 1 below and you do not fix it in this cycle." % (
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
          "NOTED_FOR_CONDUCTOR (the neutral fixer). Build no verdict on a NOTED bar.", "",
          WRONG_CHECK_RULE, FREE_GAME_RULE, "",
          "Here: a Problem `against` check or scene that you repair is FIXED with a `fixes.jsonl` row that names `plant` "
          "(what you planted), `red` (the repaired check run on that plant: an rc non-zero) and `green` (the repaired "
          "check run on the real build: rc 0), both at the fix sha; the fix commit changes only files you list in "
          "`tests_edited.json`. Such a repair owes no reader (`read_exit` lists it under `check_repairs`). A check that "
          "no bar needs: remove it from the test table, with one line on the polish list; no fix, no item.",
          "A Problem `against` mod: fix it in the sitting (the fix rules above, red first), and write `unit` (your unit) "
          "on its `fixes.jsonl` row. Then one fresh reader, a run that did not make the fix, reads only that fix, once, "
          "and writes `lane2/%s` (`{\"fault\": <id>, \"reader\": <its unit>, \"verdict\": \"sound\"|\"unsound\", "
          "\"why\"}`); the steward run that reads this cycle is that reader. Never write that file yourself. A Problem "
          "you could not fix stays PENDING with `unfixed` (why: no tools, the fix is not known, another run holds the "
          "files, one of his five acts, a north-star bar) and goes down the road back." % FIX_REVIEWS]

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
          "NOTED_FOR_CONDUCTOR, and each mod fix you made is shown red then green with your `unit` on its row. Write "
          "exit_met: true when that holds, also when you fixed the mod: the reader then waits only for the one fresh "
          "reader of each mod fix (owner, 2026-11-20, in place of a whole new blind cycle). A check or scene repair "
          "shown on its plant and on the real build owes no reader." % (
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
          "you edited; what you could not settle; whether the exit is met." % (
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
#                  "game": "archmagi"|"stevedesktop", "mod_sha", "command", "evidence", "held": [...], and the fields
#                  `build_match.py identity` prints: "mod_hash", "game_build", "active_mods", "tier" or "full_list",
#                  "unit"}; the last row per test counts, never past an earlier MOD or unclassed FAIL unless the
#                  row carries the mod fix made in the sitting (a mod fault not fixed goes down its road back, spec
#                  Stage 6, and a new visit reruns it), and only on the build he
#                  walks (the build match, read_ingame_exit). "class" (MOD | HARNESS | SITE), "repair", "mod_fix",
#                  "unrepaired" and "owner" class a failed line (line_class; owner, 2026-11-20); fix_reviews.jsonl holds
#                  the fresh reader's review of each mod fix made in the sitting.
#                  "held" names what the site switched off or locked for the run ("fire", "weather", ...; [] when the whole
#                  mod ran): maturation_rescue.py's C5 reads a bar whose every decider ran held as untested by the real
#                  mechanic, and a row without "held" as UNMEASURED (RIMMANDRAKE_PROPOSE_RESCUE_WHEN_MOD_CIRCLES_BOTH_HAND_LAUNCHED)
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
    "smallest list a check names (the 13-mod minimal list plus what its command adds: ~22 s a load). Never the full "
    "list: full-list testing is retired until the integration phase (owner, 2026-11-24, standing_rulings.md §Mod "
    "development runs on small lists). "
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
                  "check above and the owed cases, look beyond them, and diagnose each FAIL while the game is up. "
                  "Do not change a bar, its wording, the Design Version or the stage.")
OWNER_STAGE6 = ("In-game acceptance testing with setup maps, proper acceptance testing, and using the fastest methods "
                "available with dense, rich setups that test many items simultaneously + allowances to explore beyond "
                "the acceptance tests and plentiful screenshots to look for 'strange unexpected things.'")


def ingame_tests(tt):
    """-> [(test id, test)] for the table's stage-6 in-game checks (kind live*, stage 6), in table order. A kind C scene
    (a hunt) is never one (owner, 2026-11-23; live_kinds.table_flaws names a bar that this would leave undecided), nor is
    a raid scene while raid tests are paused (raid_pause.py): the exit reads it apart (`paused_raids`)."""
    return [(k, t) for k, t in ((tt or {}).get("tests") or {}).items()
            if isinstance(t, dict) and str(t.get("kind", "")).startswith("live") and str(t.get("stage")) == "6"
            and LK.kind(t) != "C" and not (RP.stages(t) and RP.paused())]


def paused_lines(root, mod, n, tt):
    """-> the driver's brief lines for the raid scenes: what each reads, and that a paused one is not started."""
    return ["- **`%s`** (%s): %s%s; decides %s. %s" % (
        t, x["stages"], x["read"] or "owed", " (%s)" % x["why"] if x["why"] else "", ", ".join(x["bars"]) or "no bar",
        "Do not start it and write no row for it." if x["read"] == RP.WORD else "It is not owed.")
        for t, x in RP.read_scenes(root, mod, n, tt).items() if x["read"]]


def raid_bars_decided(root, mod, n, tt, conductor):
    """-> (ok, why): no bar that a raid scene decides is open, or the Conductor's decision names each open one."""
    bars = RP.open_bars(RP.read_scenes(root, mod, n, tt))
    left = sorted(b for b in bars if not re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(b), str(conductor or "")))
    return not left, "; ".join("bar %s is open: raid scene %s has no standing pass" % (b, ", ".join(bars[b])) for b in left) or \
        ("no open raid bar" if not bars else "the Conductor's decision names each open raid bar: %s" % ", ".join(sorted(bars)))


def walk_brief_raid_why(root, mod, n, tt, text):
    """-> [why] a walk brief does not name a raid bar that is open (he reads it under what is known, not fixed)."""
    return ["the brief does not name the open raid bar %s (scene %s; %s): say so under \"Known, not fixed\"" % (
        b, ", ".join(s), RP.WORD) for b, s in sorted(RP.open_bars(RP.read_scenes(root, mod, n, tt)).items())
        if not re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(b), text or "")]


def moved_to_next(root, mod, what):
    """-> the ids of `bars_moved_to_next_version` or `scenes_moved_to_next_version` (what: "bars" | "scenes") of VERSION.json,
    the parts of the version that left it by his word; [] when it names none or cannot be read (nothing moved: each scene
    and bar stays owed)."""
    v, _ = read_json(root, mod, "version/VERSION.json")
    got = v.get("%s_moved_to_next_version" % what) if isinstance(v, dict) else None
    return [x for x in got if isinstance(x, str)] if isinstance(got, list) else []


def walk_brief_moved_why(root, mod, text):
    """-> [why] a walk brief does not name a bar that moved to the next version (he does not look for it on this walk)."""
    left = [b for b in moved_to_next(root, mod, "bars")
            if not re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(b), text or "")]
    return ["the brief does not name %s as moved to the next version (VERSION.json bars_moved_to_next_version): say so under "
            "\"Known, not fixed\"" % ", ".join(left)] if left else []


def visit_numbers(root, mod):
    d = os.path.join(mod_dir(root, mod), INGAME_DIR)
    out = []
    for f in os.listdir(d) if os.path.isdir(d) else []:
        m = re.match(r"visit_(\d+)$", f)
        if m and os.path.isdir(os.path.join(d, f)):
            out.append(int(m.group(1)))
    return sorted(out)


def visit_cited_items(root, mod, n):
    """-> [item ids] that the failed lines (verdict not PASS) of visit n's rows.jsonl name in `owner` or `filed` (a name
    or a list of names; only rimflow item names count), in order, once each; None when rows.jsonl cannot be read. A
    row that names its old item only as `owner` is cited too (RIMMANDRAKE_FIX_VISIT_CITE_SKIPS_OWNER_GRASS_FOIL_MISSED:
    Pyrelands visit 5, sc_grass_regreens on RIMMANDRAKE_BUILD_PYRE_GRASS_FOIL_SAME_SEED_DENSITY_ONE). A driver may
    put a failed line on an item filed long before the visit, so caused_by does not find it; the road back waits on
    these too (RIMMANDRAKE_FIX_VISIT_WAIT_MISSES_FAILURE_CITED_ON_OLD_ITEM: FlowWorks visit 5, sc_hung_bridge on
    GRATE_FIRE_FIX_SOLID_DECK_BURNS_TOO)."""
    rows = _jsonl(os.path.join(mod_dir(root, mod), INGAME_DIR, "visit_%s" % n, "rows.jsonl"))
    if rows is None:
        return None
    out, moved = [], moved_to_next(root, mod, "scenes")
    for r in rows:
        if not isinstance(r, dict) or str(r.get("verdict") or "").upper() == "PASS" or (r.get("test") or r.get("id")) in moved:
            continue        # a scene that moved to the next version holds nothing of this one
        names = []
        for f in (r.get("owner"), r.get("filed")):
            names += f if isinstance(f, list) else [f]
        for x in names:
            x = str(x or "").strip()
            if ITEM_RE.match(x) and x not in out:
                out.append(x)
    return out


def paused_scene_items(root, mod, ids, path=None):
    """-> [the ids whose every citing failed row, over all visits, is of a raid scene that is paused now, or of a scene that
    moved to the next version]: such an item
    makes no road back (raid-tests-paused page, tagged-scene and paused-is-its-own-word; FlowWorks visit 9's moat item).
    A row cites an item as visit_cited_items reads it. [] when the pause is off and no scene moved, or when a table or a
    visit's rows cannot be read (could not look is never free)."""
    tagged = set(moved_to_next(root, mod, "scenes"))
    if RP.switch(path)["paused"]:
        tt, _ = read_json(root, mod, "version/test_table.json")
        tagged |= {k for k, _ in RP.scenes(tt)} if isinstance(tt, dict) else set()
    if not tagged:
        return []
    base = os.path.join(mod_dir(root, mod), INGAME_DIR)
    cites = {i: set() for i in ids}
    for v in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        p = os.path.join(base, v, "rows.jsonl")
        if not v.startswith("visit_") or not os.path.exists(p):
            continue
        rows = _jsonl(p)
        if rows is None:
            return []
        for r in rows:
            if not isinstance(r, dict) or str(r.get("verdict") or "").upper() == "PASS":
                continue
            named = []
            for f in (r.get("owner"), r.get("filed")):
                named += f if isinstance(f, list) else [f]
            for i in set(str(x or "").strip() for x in named) & set(cites):
                cites[i].add(str(r.get("test") or ""))
    return [i for i in ids if cites[i] and cites[i] <= tagged]


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
    text = x.get("explained")
    if not text and str(x.get("status") or "").strip().lower() == "explained":
        # the shape drivers of three mods wrote: {"status": "explained", "why"|"note": ...}; the word floor still binds
        # (RIMMANDRAKE_ACCEPT_STRANGE_EXPLAINED_AS_STATUS_THREE_MODS_WROTE)
        text = x.get("why") or x.get("note")
    return len(str(text or "").split()) >= EXPLAIN_WORDS


def _known_game(g):
    """True when a row names a game: a machine (GAMES), or one of the four games by name or key (game_names.py)."""
    t = str(g or "").strip().lower()
    import game_names as GN
    return t in GAMES or any(t in (n.lower(), k) for n, k, _m, _l in GN.GAMES)


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


WALK_FIELDS = ("mod_sha", "mod_hash", "game_build", "active_mods")


def walk_identity(root, mod, rec):
    """The build he walked, for the pass record: the last in-game visit's one mod_sha (read_ingame_exit's `build`) and
    the walk savegame's mod hash, game build and mod list in order (build_match.walk_build). -> {fields..., visit,
    visit_record, savegame, game, standin, why[]}; why non-empty: no build identity, so no pass."""
    n = max(1, len(ingame_openings(rec)))
    out = {"visit": n, "visit_record": rel(mod, "%s/visit_%d" % (INGAME_DIR, n)), "why": []}
    try:
        ex = read_ingame_exit(root, mod, n)
    except Exception as e:      # a reading that cannot run names no build
        out["why"].append("the walk build could not be read (%s: %s)" % (type(e).__name__, e))
        return out
    out["savegame"] = (ex.get("claimed") or {}).get("savegame")
    out["mod_sha"] = ex.get("build")
    bm = ex.get("build_match")
    walk = dict((bm or {}).get("walk") or {}, why=(bm or {}).get("walk_why") or [])   # the reading the match checked
    if not bm or not bm.get("read"):
        out["why"].append("visit %d's build match did not run, so its mod_sha is not known to be the walk build" % n)
    elif bm.get("rerun"):
        # a change since Stage 6 that touches checks: only those run again (owner, 2026-11-21)
        out["why"].append("visit %d's checks %s do not count on the walk build as deployed now (%s): run only those on "
                          "it" % (n, ", ".join(bm["rerun"][:12]), bm.get("worst")))
    elif bm.get("deploy"):
        out["why"].append("%s%s" % (STALE_WALK, bm["deploy"]))
    for k in ("mod_hash", "game_build", "active_mods", "game", "standin", "deployed_folder"):
        if walk.get(k) is not None:
            out[k] = walk[k]
    out["why"].extend(walk.get("why") or [])
    if not out["mod_sha"]:
        out["why"].append("visit %d's rows name no single mod_sha (the build it ran)" % n)
    out["why"].extend("the walk build names no %s" % k for k in WALK_FIELDS[1:] if not out.get(k)
                      and "the stand-in names no %s" % k not in out["why"])
    return out


def pass_cost(root, mod, rec):
    """A pass's cost: this version's spend rows (the record's and the Dispatch run rows since it was seeded, spend_rows)
    in weighted tokens. Tokens no row measured read UNMEASURED, never 0."""
    rows = version_spend_rows(root, mod, rec)     # an earlier version's Dispatch run rows are its cost, not this one's
    known = [x["tokens"] for x in rows if _num(x.get("tokens")) and row_unit(x) == TOKEN_UNIT]
    other = {}
    for x in rows:
        if _num(x.get("tokens")) and row_unit(x) != TOKEN_UNIT:
            other[row_unit(x)] = other.get(row_unit(x), 0) + x["tokens"]
    return {"weighted_tokens": sum(known) if known else UNM, "tokens_other": other, "entries": len(rows),
            "tokens_unmeasured": sum(1 for x in rows if not _num(x.get("tokens"))),
            "by_stage": spend_by_stage({"spend": rows}), "unit": TOKEN_UNIT}


def pass_record(root, mod, rec, owner, sha, t, wid):
    """The pass record of a version (Design Versions draft section 3.7): date, commit, his words, bars, evidence, cost
    in weighted tokens, cycles and the build he walked (wid: the walk_identity evaluate() validated, never a second
    reading). -> (relative path under the mod, dict)."""
    ev, _ = owner_event(root, owner)
    ids, ierr = locked_bars(root, mod)
    wb = "%s/arrival_%d.md" % (WALK_BRIEF_DIR, rec.get("pre_human_arrivals") or 0)
    return "%s/%s.json" % (PASS_RECORD_DIR, rec.get("version")), {
        "mod": mod, "version": rec.get("version"), "passed_on": iso(t), "commit": sha or UNM,
        "owner_said": {"event": str(owner), "tsn": str((ev or {}).get("tsn") or ""), "words": (ev or {}).get("ownerSaid")
                       or (ev or {}).get("byCard")},
        "bars": {"locked": ids, "read": ierr or ("no %s" % LOCKED_BARS if ids is None else None),
                 "record": rel(mod, LOCKED_BARS)},
        "evidence": [rel(mod, RECORD), wid["visit_record"], rel(mod, wb), rel(mod, "version/test_table.json")],
        "cost": pass_cost(root, mod, rec),
        "cycles": dict(rec.get("cycles") or {}, pre_human_arrivals=rec.get("pre_human_arrivals", 0)),
        "build": {k: v for k, v in wid.items() if k not in ("why",)}}


# ---- the pass tag (owner, 2026-11-20: "Make sure we TAG each finished version of a mod so we can easily come precisely
# back to it, please. This should become policy."; item RIMMANDRAKE_TAG_EACH_PASSED_MOD_VERSION_PIPELINE_DOES_IT).
# Boundary: design/specs/2026-11-20-maturation-pass-tag/boundary.md. The pass is written once and never replaced, so a
# tag that cannot be made or pushed is RETRIED (`tag-pass`), reported as res["untagged"], never a silent success.

PASS_TAG = "mod/%s/v%s"


def _g(root, *a, timeout=120):  # budget: class=call
    return subprocess.run(["git", "-C", root] + list(a), capture_output=True, text=True, timeout=timeout)


def _not_own_repo(root):
    """-> None when root is itself the top of a git clone, else why not (never a folder inside some other clone; a git
    that cannot run is named, so the untagged pass says so)."""
    try:
        r = _g(root, "rev-parse", "--show-toplevel", timeout=30)
    except (OSError, subprocess.TimeoutExpired) as e:
        return "git could not run in %s: %r" % (root, e)
    if r.returncode:
        return "%s is not inside a git clone" % root
    top = os.path.realpath(r.stdout.strip())
    return None if top == os.path.realpath(root) else "%s is inside the clone %s, not its top" % (root, top)


def pass_tag_taken(root, mod, version):
    """-> the tag name when it already exists in root's clone (the pass is then refused before any write), else None."""
    name = PASS_TAG % (mod, version)
    if _not_own_repo(root):
        return None          # nothing to read: tag_pass then names the cause as untagged, step land
    return name if _g(root, "rev-parse", "-q", "--verify", "refs/tags/" + name, timeout=30).returncode == 0 else None


def pass_paths(root, mod, first, journal):
    """The repo-relative files one pass move wrote: the pass record(s), the stage record, the journal, and the mod's
    own ledger/ files that changed (ledger_stage_move)."""
    base = os.path.join("design", "concepts", mod)
    out = [os.path.join(base, p) for p in sorted(first)] + [os.path.join(base, RECORD)]
    if journal:
        out.append(os.path.join(base, "journal.md"))
    if not _not_own_repo(root):
        st = _g(root, "status", "--porcelain", "-z", "--untracked-files=all", "--", os.path.join(base, "ledger"))
        out += [e[3:] for e in st.stdout.split("\0") if len(e) > 3 and e[3:] not in out] if st.returncode == 0 else []
    return out


def _remote_tag(root, name):
    """-> (commit the tag peels to on origin or None, error text or None), read with ls-remote."""
    try:
        r = _g(root, "ls-remote", "origin", "refs/tags/%s^{}" % name, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, repr(e)
    if r.returncode:
        return None, (r.stderr or "").strip()[-300:]
    return (r.stdout.split()[0] if r.stdout.strip() else None), None


def tag_pass(root, mod, version, paths=None):
    """Land (when paths are given) and tag one passed version: the annotated tag mod/<Mod>/v<version> on the commit
    that records the pass, pushed to origin and read back with ls-remote. -> {"tag": {name, commit, pushed}} (with
    "already": True when origin had it), or {"untagged": {name, step, why, retry}}, step land/tag/push/verify."""
    name = PASS_TAG % (mod, version)
    retry = "python3 src/RimMandrake/rimflow/maturation.py tag-pass %s --version %s" % (mod, version)

    def fail(step, why):
        return {"untagged": {"name": name, "step": step, "why": why, "retry": retry}}
    why = _not_own_repo(root)
    if why:
        return fail("land", "%s: nothing is committed, tagged or pushed" % why)
    prp = os.path.join("design", "concepts", mod, PASS_RECORD_DIR, "%s.json" % version)
    if paths:
        pub = os.path.join(root, "publish")
        if not os.access(pub, os.X_OK):
            return fail("land", "no executable publish at %s" % pub)
        add = _g(root, "add", "--", *paths)       # a new pass record must be known to git before publish
        if add.returncode:
            return fail("land", "git add: %s" % (add.stderr or "").strip()[-300:])
        try:
            r = subprocess.run([pub, "-m", "%s %s PASSED: pass record, stage record and journal (maturation.py)"
                                % (mod, version)] + list(paths), cwd=root, capture_output=True, text=True, timeout=21600)  # budget: class=publish
        except (OSError, subprocess.TimeoutExpired) as e:
            return fail("land", "publish: %r" % (e,))
        m = re.search(r"^PUBLISHED ([0-9a-f]{7,40})", r.stdout or "", re.M)
        if r.returncode or not m:
            tail = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-3:]
            return fail("land", "publish exit %d: %s" % (r.returncode, " | ".join(tail)))
        sha = _g(root, "rev-parse", m.group(1) + "^{commit}").stdout.strip()
    else:
        # budget: class=call
        _g(root, "fetch", "-q", "origin", "main", timeout=180)     # best effort: a stale origin/main only misses
        added = _g(root, "log", "--diff-filter=A", "--format=%H", "origin/main", "--", prp)
        sha = (added.stdout.split() or [""])[0] if added.returncode == 0 else ""
        if not sha:
            return fail("land", "no commit on origin/main adds %s" % prp)
    if not sha:
        return fail("land", "the PUBLISHED commit could not be read back")
    have = _g(root, "rev-parse", "-q", "--verify", "refs/tags/%s^{commit}" % name)
    made = have.returncode != 0
    if not made and have.stdout.strip() != sha:
        return fail("tag", "the clone's tag %s names %s, not the pass commit %s" % (name, have.stdout.strip()[:10],
                                                                                    sha[:10]))
    if made:
        t = _g(root, "tag", "-a", "-m", "%s %s passed: the commit that records the pass (%s)" % (mod, version, prp),
               name, sha)
        if t.returncode:
            return fail("tag", "git tag: %s" % (t.stderr or "").strip()[-300:])
    on, _ = _remote_tag(root, name)
    if on == sha:
        return {"tag": {"name": name, "commit": sha, "pushed": True}, "already": not made}
    if on:
        return fail("push", "origin's tag %s names %s, not the pass commit %s" % (name, on[:10], sha[:10]))
    try:
        # budget: danger=a hung push holds the pass; never reached in the 14 days to 2026-11-24; no record of its run
        p = _g(root, "push", "origin", "refs/tags/" + name, timeout=240)
    except (OSError, subprocess.TimeoutExpired) as e:
        return fail("push", repr(e))
    if p.returncode:
        return fail("push", " | ".join((p.stderr or "").strip().splitlines()[-3:]))
    on, err = _remote_tag(root, name)
    if on != sha:
        return fail("verify", "after the push origin shows %s for %s (%s)" % (on, name, err or "read"))
    return {"tag": {"name": name, "commit": sha, "pushed": True}}


def tag_line(res):
    """One line for a CLI, or None: TAGGED ..., or PASSED BUT NOT TAGGED ... with the retry command."""
    if res.get("untagged"):
        u = res["untagged"]
        return "PASSED BUT NOT TAGGED: %s, step %s: %s. Retry: %s" % (u["name"], u["step"], u["why"], u["retry"])
    if res.get("tag"):
        t = res["tag"]
        return "TAGGED %s on %s, on origin (ls-remote)%s" % (t["name"], t["commit"][:10],
                                                              ", already there" if res.get("already") else "")
    return None


# ---- a failed or unmeasured line is classed (owner, 2026-11-20, RIMMANDRAKE_ENACT_WRONG_CHECK_FIXED_IN_SITTING_NOT_
# RETURNED and RIMMANDRAKE_RESUME_WRONG_CHECK_WORKER_WITH_MOD_FIX_EXTENSION; standing_rulings §Touching code has a cost):
# the mod is wrong (MOD), the check is wrong (HARNESS) or the staged scene is wrong (SITE), the classes of skill
# live-debugging-proof-harness. A wrong check or scene a bar needs is repaired in the sitting and counts only when seen
# FAIL on a plant and PASS on the real build; one no bar needs is removed from the test table. A mod fault the driver
# can fix is fixed in the sitting with a before/after test, and one fresh reader checks that fix. Only a mod fault not
# fixed, or a bar left undecided, sends the mod back. Boundary: design/specs/2026-11-20-wrong-check-fixed-in-sitting/

WRONG_CLASSES = ("HARNESS", "SITE")
FIX_REVIEWS = "fix_reviews.jsonl"
STALE_WALK = "the walk build is not the current source: "   # the exit reason the tick's autodeploy act cures
BLIND_MATCH = "the build match could not look "   # a read that ends by itself (ENOMEM): the tick waits and reads again


def _commit_words(v):
    """-> the commit hashes in v (one, or several space- or comma-separated); [] when v is empty or any word is not a
    commit hash."""
    words = str(v or "").replace(",", " ").split()
    return words if words and all(SHA_RE.match(w) for w in words) else []


def repair_shown(r):
    """-> None when row r's `repair` shows the repaired check both ways: the repair commit, and a planted reading (what
    was planted, its command, verdict FAIL). The row's own verdict is the real-build reading. Else -> why not."""
    rp = r.get("repair")
    if not isinstance(rp, dict):
        return "its `repair` is not a record"
    pl = rp.get("planted") if isinstance(rp.get("planted"), dict) else {}
    miss = [w for w, bad in (
        ("class HARNESS (check wrong) or SITE (scene wrong)", str(rp.get("class", "")).upper() not in WRONG_CLASSES),
        # a repair made in two commits names both (RIMMANDRAKE_ACCEPT_REPAIR_RECORD_NAMING_TWO_COMMITS_NOT_ONE); every
        # word must still be a commit hash
        ("repair commit", not _commit_words(rp.get("commit"))),
        ("planted reading", not pl),
        ("plant (what was planted)", pl and not str(pl.get("plant") or "").strip()),
        ("command for the planted reading", pl and not str(pl.get("command") or "").strip()),
        ("planted reading that reads FAIL", pl and str(pl.get("verdict", "")).upper() != "FAIL")) if bad]
    return ("its repair names no %s" % ", no ".join(miss)) if miss else None


def mod_fix_shown(r):
    """-> None when row r's `mod_fix` shows the mod fixed in the sitting: its commit, and a before/after test (red: an rc
    non-zero, green: every rc 0, each side naming its command). Else -> why not."""
    mf = r.get("mod_fix")
    if not isinstance(mf, dict):
        return "its `mod_fix` is not a record"
    red, green = _rcs(mf.get("red")), _rcs(mf.get("green"))
    miss = [w for w, bad in (
        ("fix commit", not SHA_RE.match(str(mf.get("commit") or ""))),
        ("red run (an rc non-zero before the fix)", not any(isinstance(c, int) and c != 0 for c in red)),
        ("green run (rc 0 after the fix)", not green or any(c != 0 for c in green)),
        ("command for each run", not (_side_cmds(mf, "red") and _side_cmds(mf, "green")))) if bad]
    return ("its mod fix names no %s" % ", no ".join(miss)) if miss else None


def review_sound(reviews, key, maker):
    """-> (True, None) when the last `fix_reviews.jsonl` row for fix key (its `fix` commit or blind `fault` id) reads
    `sound` by a reader that is not maker (the unit that made the fix). Else (False, why). One fresh reader checks only
    that fix, once (owner, 2026-11-20: "I agree with your blind judge -> fresh reader argument.")."""
    mine = [x for x in reviews or [] if isinstance(x, dict) and key and key in (x.get("fix"), x.get("fault"))]
    if not mine:
        return False, "no fresh reader has read it"
    x = mine[-1]
    if not maker:
        return False, "the fix names no unit, so its reader cannot be shown to be another"
    if not str(x.get("reader") or "").strip() or str(x.get("reader")).strip() == str(maker).strip():
        return False, "its review names no reader, or the unit that made the fix (%s)" % maker
    if str(x.get("verdict", "")).lower() != "sound":
        return False, "its reader %s read it %s: %s" % (x.get("reader"), x.get("verdict") or "with no verdict",
                                                         x.get("why") or "no reason given")
    return True, None


def fix_reviews(path):
    """-> the rows of a fix_reviews.jsonl: [] when no reader has written the file yet (each fix then reads owed). A
    file that is there and cannot be read raises, so the exit reads not met by name (evaluate turns a raise into a
    refusal), never as "no review"."""
    if not os.path.exists(path):
        return []
    rows = _jsonl(path)
    if rows is None:
        raise ValueError("%s is there and cannot be read" % path)
    return rows


def _said(r, field):
    return len(str(r.get(field) or "").split()) >= EXPLAIN_WORDS


def line_class(r, earlier, tt=None):
    """-> how a check's last row r counts at the exit: pass | mod (the mod is wrong and not fixed in the sitting: the
    road back) | not_counted (a needed check or scene that is repaired and not shown both ways, or said unrepaired, and
    keeps an `owner`: it blocks through its undecided bar) | unclassed (a FAIL or UNMEASURED with no class) | unhandled
    (classed wrong, and neither repaired nor owned). read_ingame_exit turns a wrong line that no bar needs into
    needless. earlier: the classes of the check's earlier real FAIL rows (never HARNESS or SITE)."""
    v, cls = str(r.get("verdict", "")).upper(), str(r.get("class", "")).upper()
    if earlier:
        if set(earlier) == {"MOD"} and v == "PASS" and mod_fix_shown(r) is None:
            return "pass"           # fixed in the sitting; its fresh reader is read separately
        return "mod" if "MOD" in earlier else "unclassed"
    if "repair" in r:
        if v == "PASS" and repair_shown(r) is None:
            return "pass"
        return "not_counted" if str(r.get("owner") or "").strip() else "unhandled"
    if v == "PASS":
        return "pass"
    if cls == "MOD":
        return "mod"
    if cls in WRONG_CLASSES:
        return "not_counted" if _said(r, "unrepaired") and str(r.get("owner") or "").strip() else "unhandled"
    return "unclassed"


def _not_counted_why(r):
    if "repair" in r:
        return "repaired and not shown both ways: %s; owner %s" % (
            repair_shown(r) or "its re-run reads %s" % r.get("verdict"), r.get("owner"))
    return "unrepaired: %s; owner %s" % (r.get("unrepaired"), r.get("owner"))


LANE_ROWS_BY = "testq/visit_rows.py"    # the `by` that the test lane writes on its rows (Utils/testq/visit_rows.py)


def lane_rows_only(d):
    """True when a visit folder holds nothing but the test lane's rows: the lane may write them before any driver opens the
    visit, so the folder is no driver's record (FlowWorks visit 10, 2026-11-24: 3 rows from Steve1 read as a visit that
    ended without its exit block, and no driver launched). A row of another writer, a torn row, another file: False."""
    if os.listdir(d) != ["rows.jsonl"]:
        return False
    rows = _jsonl(os.path.join(d, "rows.jsonl"))
    return bool(rows) and all(isinstance(r, dict) and r.get("by") == LANE_ROWS_BY for r in rows)


# Owner, 2026-11-24 ("go"): full-list testing is retired until the integration phase, and a walk save stands on the mod's small
# list. The rule binds a visit that opens after it: a save staged before keeps its list.
SMALL_LIST_FROM = "2026-11-24T10:20:00-08:00"      # the first briefs that say so landed at 9:55 AM (f99cf6b71e)


def walk_small_list_why(root, mod, n, walk):
    """-> None, or why the mod's small list lacks a mod it needs, or visit n's walk savegame is not on that list (small_list.py). A visit that opened before
    SMALL_LIST_FROM, a stand-in walk and a mod with no small_list.json are not judged; a list that cannot be read is said."""
    if not walk or walk.get("standin") or not walk.get("active_mods"):
        return None
    rec = load(root, mod)
    at = ingame_openings(rec).get(n) or rec.get("since")
    try:
        if dt.datetime.fromisoformat(at) < dt.datetime.fromisoformat(SMALL_LIST_FROM):
            return None
    except (TypeError, ValueError) as e:
        return "when visit %d opened could not be read (%r: %s), so the walk savegame's list is not checked" % (n, at, e)
    try:
        import small_list as SL
        faults = SL.list_faults(root, mod)
        return "; ".join(faults) if faults else SL.walk_save_why(root, mod, walk["active_mods"])
    except Exception as e:      # noqa: BLE001  (a list that cannot be read counts nothing)
        return "the mod's small list could not be read (%s: %s), so the walk savegame's list is not checked" % (
            type(e).__name__, e)


def walk_letter(root, mod):
    """-> the letter of the game he walks the mod on: the game that holds the last in-game visit's walk savegame
    (build_match.walk_letter), else "a"."""
    ns = visit_numbers(root, mod)
    for k in reversed(ns):
        blk = ingame_exit_block(read_text(root, mod, "%s/visit_%d/SUMMARY.md" % (INGAME_DIR, k)))
        if blk and blk.get("savegame"):
            return BM.walk_letter(blk["savegame"])
    return "a"


def read_ingame_exit(root, mod, n, tt=None):
    """-> {visit, state, why[], claimed, rows}: the program's reading of visit n's exit. state: absent (no visit_n folder,
    or one that holds only the test lane's rows, lane_rows_only: its driver is still owed) | no_exit_block (no Exit block with the four keys: a visit in progress, or one that ended without writing it) | met |
    not_met. See the record layout above this section."""
    if tt is None:
        tt, _ = read_json(root, mod, "version/test_table.json")
    base = "%s/visit_%d" % (INGAME_DIR, n)
    d = os.path.join(mod_dir(root, mod), base)
    out = {"visit": n, "record": rel(mod, base), "why": [], "rows": {}}
    if not os.path.isdir(d) or lane_rows_only(d):
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
    for t, f in LK.table_flaws(tt).items():
        why.append("%s%s: %s" % ("" if t.startswith("bar ") else "in-game check ", t, "; ".join(f)))
    rows = _jsonl(os.path.join(d, "rows.jsonl"))
    if rows is None:
        why.append("rows.jsonl is missing")
    # a check this visit did not run keeps the last row of the latest earlier visit that ran it (owner, 2026-11-21:
    # only the checks a change touches run again); the build match below decides whether that row still counts
    # (a spoiled run speaks for nobody: a check with only spoiled runs here keeps its earlier row too, live_kinds.py)
    ran_here = {r.get("test") or r.get("id") for r in rows or [] if not LK.spoiled(r)}
    here = {r.get("test") or r.get("id") for r in rows or []}
    carried = {t: r for t, r in (BM.carried_rows(root, mod, n - 1).items() if n > 1 else ()) if t and t not in ran_here
               and not (t in here and LK.spoiled(r))}
    rows = [carried[t] for t in sorted(carried)] + list(rows or [])
    # an earlier row counts against its check only as a real FAIL: an UNMEASURED row (a run the 540 s command bound
    # split) or a FAIL the driver classed HARNESS or SITE (the check or the scene was wrong) spends nothing (standing_
    # rulings, No trial is spent by a system failure, and §Touching code has a cost); the last row decides (line_class)
    # what the kind of the scene and the outcomes of its runs say (live_kinds.py; None: old rows, read as they always were)
    last, earlier, specs = {}, {}, dict(checks)
    for r in rows or []:
        t = r.get("test") or r.get("id")
        if t:
            p = LK.as_old(last.get(t) or {})
            if str(p.get("verdict", "")).upper() == "FAIL" and str(p.get("class", "")).upper() not in WRONG_CLASSES \
                    and LK.earlier_fail(p, specs.get(t)) and LK.later(p, r) is r:
                earlier.setdefault(t, []).append(str(p.get("class", "")).upper() or "unclassed")
            last[t] = LK.later(last.get(t), r)
    try:
        runs = BM.check_runs(root, mod, n)
    except ValueError as e:     # not read: an UNRESOLVED run may stand there, so the exit is not met, by name
        runs = {}
        why.append("the rows of every visit could not be read (%s): no run's outcome is known to be clear" % e)
    kinds = {t: LK.reading(x, runs.get(t)) for t, x in checks}
    out["paused_raids"] = RP.read_scenes(root, mod, n, tt)
    lines_ = out["lines"] = {}
    for t, _ in checks:
        r, k = last.get(t), kinds[t]
        if r is not None and k is not None:
            r = last[t] = LK.as_old(k["use"])
            if k["mod"] and "MOD" not in earlier.get(t, ()):
                earlier.setdefault(t, []).append("MOD")
        cnt = line_class(r, earlier.get(t)) if r is not None else "no_row"
        if k is not None and r is not None and k["count"] in LK.HOLDS and cnt != "mod":
            cnt = k["count"]
        rp = r.get("repair") if r is not None and isinstance(r.get("repair"), dict) else {}
        cls = str(r.get("class") or rp.get("class") or "").upper() if r is not None else ""
        lines_[t] = {"count": cnt, "class": cls or None, "bars": _bars_of(tt, t)}
    # a wrong check or scene that no bar needs (every bar it decides has another decider that reads a counted PASS or a
    # MOD FAIL) is removed from the test table, never kept as not counted (owner, 2026-11-20: "How does that help if
    # there's a needless test present? The next judge will hit it again...")
    # a check a held owner statement names as its test is needed even when it decides no bar (FlowWorks visit 4,
    # 2026-11-21: OL_OWNER_LOOK_READS is the test of 31 held look approvals and read "needless")
    for t, ln in lines_.items():
        if ln["count"] in ("not_counted", "unhandled") and ln["class"] in WRONG_CLASSES and not _held_names(tt, t) and all(
                any(lines_[k]["count"] in ("pass", "mod") for k, _ in checks if k != t and b in _bars_of(tt, k))
                for b in ln["bars"]):
            ln["count"] = "needless"
    reviews = fix_reviews(os.path.join(d, FIX_REVIEWS))
    owed = out["fix_readers_owed"] = []
    out["shortfalls"] = []
    try:
        for c in landed_at_walk(root, mod, load(root, mod), n):
            # the reader may have read it before this visit opened (ExplosiveKnockback db80fab783: visit 5's file)
            seen = [dict(x, fix=c) for k in visit_numbers(root, mod) if k <= n for x in fix_reviews(os.path.join(
                mod_dir(root, mod), INGAME_DIR, "visit_%d" % k, FIX_REVIEWS))
                if SHA_RE.match(str(x.get("fix") or "")) and c.startswith(x["fix"])]
            good, rwhy = review_sound(seen, c, "the run that landed %s" % c)
            if not good:
                owed.append({"check": None, "fix": c, "why": rwhy})
                why.append("the mod change %s landed while the mod stood at his walk and owes one fresh reader (%s): a run "
                           "that did not make it reads only that commit, once, and writes %s/%s" % (
                               c, rwhy, rel(mod, base), FIX_REVIEWS))
    except OSError as e:
        why.append("the changes that landed while the mod stood at his walk could not be read (%s): whether a fresh "
                   "reader is owed is unknown" % e)
    out["carried"] = sorted(carried)
    for t, _ in checks:
        claim = blk["ingame_rows"].get(t)
        r = last.get(t)
        if claim is None and t in carried and str((r or {}).get("verdict", "")).upper() == "PASS":
            claim = "pass"          # carried from visit r["_visit"]: this visit's block need not list it
        k = kinds[t]
        if k is not None and k["claim_free"] and lines_[t]["count"] == "pass":
            claim = "pass"          # the block writes the last run's word; that run does not decide this check
        v = str((r or {}).get("verdict", "")).upper()
        out["rows"][t] = v or "NO ROW"
        ln = lines_[t]
        cnt = ln["count"]
        if r is not None and isinstance(r.get("repair"), dict):
            ln["repair"], ln["real"] = r["repair"], v
        if cnt == "pass" and earlier.get(t):
            ln["mod_fix"] = r["mod_fix"]
            mf = r["mod_fix"]
            good, rwhy = review_sound(reviews, mf.get("commit"), mf.get("unit") or r.get("unit"))
            ln["review"] = "sound" if good else rwhy
            if not good:
                owed.append({"check": t, "fix": mf.get("commit"), "why": rwhy})
                why.append("in-game check %s: the mod fix %s made in the sitting owes one fresh reader (%s): a run that "
                           "did not make the fix reads only that fix, once, and writes %s/%s" % (
                               t, mf.get("commit"), rwhy, rel(mod, base), FIX_REVIEWS))
        if k is not None:
            why.extend("in-game check %s: %s" % (t, w) for w in k["why"])
            if k["short"] and cnt == "inconclusive":        # the tick asks the Conductor (shortfall.py)
                out["shortfalls"].append(dict(k["short"], test=t))
            if cnt in LK.HOLDS:     # nothing here sends the mod back, and no class is owed: the scene, or the words, are
                out["rows"][t] = k["rows"] or v
                ln["why"] = "; ".join(k["why"])
                continue
        if cnt == "needless":
            why.append("in-game check %s is classed %s and no bar needs it (another check decides each of its bars "
                       "%s): remove it from the test table (and delete it when nothing else names it), with one line "
                       "on the polish list as the record" % (t, ln["class"], ", ".join(ln["bars"]) or "(none)"))
            continue
        if cnt == "not_counted":
            ln["why"] = _not_counted_why(r)
            out["rows"][t] = "UNMEASURED" if "repair" in r else v
            if claim == "pass":
                why.append("in-game check %s reads pass in the block, but it is not counted (%s)" % (t, ln["why"]))
            continue        # it decides nothing; its bars are read below
        if claim != "pass":
            why.append("in-game check %s reads %s in the block" % (t, claim or "nothing (left out)"))
        if r is None:
            why.append("in-game check %s has no row in rows.jsonl" % t)
            continue
        if v != "PASS" or cnt == "unhandled":
            why.append("in-game check %s: its last row reads %s%s" % (t, v or "no verdict", {
                "mod": " (classed MOD: the mod is wrong; fix it in the sitting with a before/after test, or it goes "
                       "down its road back with the evidence why not)",
                "unclassed": " with no class: class it MOD (the mod is wrong), HARNESS (the check is wrong) or SITE "
                             "(the scene is wrong)",
                "unhandled": " (classed %s: the check or scene is wrong, and a bar needs it) and is neither repaired "
                             "(`repair`, seen FAIL on a plant and PASS on the real build) nor said `unrepaired` with "
                             "its `owner` (the run or the filed item that keeps it)" % ln["class"]}.get(cnt, "")))
        if earlier.get(t) and cnt != "pass":
            why.append("in-game check %s: an earlier row reads FAIL (classed %s); a later PASS does not hide it unless "
                       "the row carries the mod fix made in the sitting (`mod_fix`, red then green)" % (
                           t, ", ".join(earlier[t])))
        if r.get("site_checked") is not True:
            why.append("in-game check %s: its row does not say the site was checked first (site_checked)" % t)
        elif not _site_shown(root, r):
            why.append("in-game check %s: site_checked true with nothing to show it (a non-empty `site` reading, or an "
                       "`evidence` file on disk)" % t)
        if not _known_game(r.get("game")):
            why.append("in-game check %s: its row names no game (%s)" % (t, " or ".join(GAMES)))
        if not r.get("mod_sha"):
            why.append("in-game check %s: its row names no mod_sha (the build it ran)" % t)
        elif not SHA_RE.match(str(r.get("mod_sha"))):
            why.append("in-game check %s: its mod_sha %r is not a commit hash (7 to 40 hex)" % (t, r.get("mod_sha")))
    # a check not counted sends nothing back unless its bar is left undecided: no other in-game check of that bar reads
    # a counted PASS or a MOD FAIL (a FAIL decides its bar too)
    undecided = {}
    for t, ln in lines_.items():
        if ln["count"] == "not_counted":
            for b in ln["bars"]:
                if not any(lines_.get(k, {}).get("count") in ("pass", "mod") for k, _ in checks
                           if k != t and b in _bars_of(tt, k)):
                    undecided.setdefault(b, []).append(t)
    out["undecided_bars"] = sorted(undecided)
    for b in sorted(undecided):
        why.append("bar %s is undecided: its in-game check(s) %s are not counted (%s) and no other in-game check of it "
                   "counts: repair one in the sitting, seen FAIL on a plant and PASS on the real build, and re-run it" % (
                       b, ", ".join(undecided[b]), "; ".join(lines_[t]["why"] for t in undecided[b])))
    # RIMMANDRAKE_BIND_STAGE_EVIDENCE_TO_ONE_BUILD: a short hash agrees with a long one it starts
    # rows made on several builds (a check rerun after a change, beside rows carried from before it) are judged each from
    # its own commit by the build match below (owner, 2026-11-21); the build is then the mod's source now
    shas = sorted({str(last[t].get("mod_sha")) for t, _ in checks if t in last and lines_[t]["count"] != "needless"
                   and SHA_RE.match(str(last[t].get("mod_sha") or ""))}, key=len)
    one = all(b.startswith(a) for i, a in enumerate(shas) for b in shas[i + 1:])
    out["build"] = shas[-1] if shas and one else None
    # the BUILD MATCH (owner, 2026-11-17, RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_BRIEF_NO_VETO): a check's last row counts
    # only when its mod hash and game build equal the build he walks (the labelled savegame's, read on Archmagi) and its
    # mod list is his walk's (a full-list test) or its tier's (a minimal-list test); one that does not is re-run
    try:
        bm = BM.check_visit(root, mod, n, tt, blk["savegame"])
    except Exception as e:      # a build match that cannot run counts nothing
        bm = None
        why.append("%s(%s: %s): no in-game check counts until it does" % (
            BLIND_MATCH if BM.could_not_look(e) else "the build match could not run ", type(e).__name__, e))
    out["build_match"] = bm
    if bm and not one and not bm.get("rerun") and not bm.get("deploy"):
        out["build"] = BM.source_sha(root, mod)       # every row counts on the source now: that is the build
    elif not one and not bm:
        why.append("the rows name more than one build (mod_sha %s) and no build match read them" % ", ".join(shas))
    if bm and bm.get("deploy"):
        why.append("%s%s" % (STALE_WALK, bm["deploy"]))
    if bm and bm.get("walk_why"):
        why.append("the walk build is unreadable (%s): no in-game check counts until build_match.py reads it" % "; ".join(
            bm["walk_why"]))
    elif bm:
        why.extend("in-game check %s does not count on the walk build (%s): re-run it" % (t, bm["rows"][t]["why"])
                   for t in bm["rerun"])
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
    elif not (bm and bm.get("walk_why")):      # an unreadable walk is said above, once
        small = walk_small_list_why(root, mod, n, (bm or {}).get("walk"))
        if small:
            why.append(small)
    out["state"] = "not_met" if why else "met"
    if not why:
        nc = sorted(t for t, ln in lines_.items() if ln["count"] == "not_counted")
        rep = sorted(t for t, ln in lines_.items() if ln["count"] == "pass" and ln.get("repair"))
        why.append("%d of %d in-game checks PASS on checked sites%s%s; strange things all explained or filed; savegame %s%s"
                   % (len(checks) - len(nc), len(checks), "; repaired in the sitting and shown both ways: %s" % ", ".join(
                       rep) if rep else "", "; not counted, every bar still decided: %s" % ", ".join(
                       "%s (%s)" % (t, lines_[t]["why"]) for t in nc) if nc else "", sv,
                   "; " + RP.said(out["paused_raids"]) if RP.said(out["paused_raids"]) else ""))
    return out


# ---- the walk brief (Stage 7) ----------------------------------------------------------------------------------------
#
# Owner, 2026-11-17 (RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_BRIEF_NO_VETO): Stage 7 judges nothing. One fresh read, by an
# agent that made none of the evidence writes, writes his walk brief; it has no veto (what it notices goes into the brief
# or onto a ticket), so the brief written is the stage's only exit. Its role: src/RimMandrake/rimflow/roles/walk_brief.md.

WALK_BRIEF_DIR = "version/walk_brief"
WALK_BRIEF_HEADINGS = ("What to open", "What changed since his last look",
                       "Known, not fixed: you need not report these", "What I noticed first")


# ---- a Stage 8 walk that did not pass (design/specs/2026-11-22-walk-result/boundary.md) ----------------------------
WALK_RESULT_RX = re.compile(r"^walk_(\d+)_result\.json$")
WALK_LISTS = ("fix", "pick", "scene", "next_version")
WALK_HOLDS = ("fix", "pick", "scene")       # the lists that hold his next walk; next_version items never do


def walk_result_rel(n, ext="json"):
    """-> the mod-relative path of walk N's result (N = the walk brief arrival he walked)."""
    return "%s/walk_%d_result.%s" % (WALK_BRIEF_DIR, n, ext)


def read_walk_result(root, mod):
    """-> {path, data, why[]}: the newest version/walk_brief/walk_<N>_result.json. data None and why [] when no walk
    result exists (no walk sent this version back); why names the file when it cannot be listed, read or parsed, which
    is never read as no items."""
    d = os.path.join(mod_dir(root, mod), WALK_BRIEF_DIR)
    try:
        names = os.listdir(d)
    except FileNotFoundError:
        return {"path": None, "data": None, "why": []}
    except OSError as e:
        return {"path": rel(mod, WALK_BRIEF_DIR), "data": None,
                "why": ["%s cannot be listed (%s)" % (rel(mod, WALK_BRIEF_DIR), e)]}
    ns = sorted(int(m.group(1)) for m in (WALK_RESULT_RX.match(n) for n in names) if m)
    if not ns:
        return {"path": None, "data": None, "why": []}
    p = walk_result_rel(ns[-1])
    data, err = read_json(root, mod, p)
    if err or not isinstance(data, dict):
        return {"path": rel(mod, p), "data": None, "why": ["%s: %s" % (rel(mod, p), err or "not a JSON object")]}
    return {"path": rel(mod, p), "data": data, "why": []}


def walk_items_open(root, mod):
    """-> {path, open[], why[]}: the items of the newest walk result's fix, pick and scene lists still open on the
    ledger. why is non-empty when the result or the ledger cannot be read (could not look, never no items)."""
    wr = read_walk_result(root, mod)
    out = {"path": wr["path"], "open": [], "why": list(wr["why"])}
    if wr["why"] or not wr["data"]:
        return out
    ids = [str(i) for k in WALK_HOLDS for i in wr["data"].get(k) or []]
    try:
        live = {x["id"] for x in ledger_items_caused_by(root, [], named=ids)}
    except Exception as e:      # noqa: BLE001  a ledger that cannot be read is a refusal that says so
        out["why"].append("the ledger cannot be read (%s: %s)" % (type(e).__name__, e))
        return out
    out["open"] = [i for i in dict.fromkeys(ids) if i in live]
    return out


def _owner_words_by_item(root, ids):
    """-> {item: [his words, in ledger order]} from the OWNER shard; {} when it cannot be read."""
    import concept_tree as CT
    out = {i: [] for i in ids}
    evs = CT.owner_events(root, REPO)
    for _tsn, ev in sorted(evs.items(), key=lambda kv: int(kv[0]) if str(kv[0]).isdigit() else 0):
        w = str(ev.get("ownerSaid") or ev.get("byCard") or "").strip()
        if ev.get("id") in out and w and w not in out[ev["id"]]:
            out[ev["id"]].append(w)
    return out


def walk_result_md(mod, ver, n, data, titles, words):
    """-> the plain record of walk N for him and the next reader: the verdict, his passes, each list with each item's
    title and his own words quoted, and the fixer groups."""
    head = {"fix": "Code defects: fixers run on the road back", "scene": "Scene defects: fixers run on the road back",
            "pick": "Waiting for his pick: no fixer runs; each holds his next walk",
            "next_version": "Next version: not this one; holds nothing"}
    L = ["# %s %s: walk %d result, NOT PASSED" % (mod, ver, n), "",
         "- Walked: %s." % data.get("walked", "not written"),
         "- His words ending the walk: \"%s\" (OWNER:%s)." % (data["owner_said"].get("words"),
                                                             data["owner_said"].get("tsn"))
         if data.get("owner_said") else "- Ended by a Conductor decision: %s." % data.get("conductor_decision"),
         "- Road back: %s to %s, recorded %s by %s (`maturation.py walk-result`)." % (
             label("his_walk"), label(data["to"]), data["at"], data["by"]),
         "- Route item: `%s`." % data.get("item"), "- Why: %s" % data.get("why"), ""]
    if data.get("passes"):
        L += ["## Passes he stated", ""] + ["- %s" % p for p in data["passes"]] + [""]
    for k in ("fix", "scene", "pick", "next_version"):
        if not data.get(k):
            continue
        L += ["## %s" % head[k], ""]
        for i in data[k]:
            L.append("- `%s`: %s" % (i, (titles.get(i) or "").strip()[:400]))
            for w in words.get(i) or []:
                L.append("  - He said: \"%s\"" % w.replace("\n", " "))
        L.append("")
    if data.get("groups"):
        L += ["## Fixer groups (one run fixes and closes every item of its group)", ""]
        L += ["- %s" % " + ".join("`%s`" % i for i in g) for g in data["groups"]] + [""]
    return "\n".join(L)


def walk_result(root, mod, to, by, why, owner=None, conductor=None, item=None, fix=(), pick=(), scene=(),
                next_version=(), groups=(), passes=(), walked=None):
    """Record a Stage 8 walk that did NOT pass and take the road back in one locked write: writes
    version/walk_brief/walk_<N>_result.json and .md once (N = pre_human_arrivals) and moves the record his_walk -> to.
    -> {ok, why, path, move result}. Refuses, writing nothing, off his_walk, on an id with no ledger event, on a
    result already written, or with neither his event nor a Conductor decision."""
    rec = load(root, mod)
    if rec is None or rec.get("stage") != "his_walk":
        return {"ok": False, "why": "%s stands at %s, not his_walk: only a Stage 8 walk has a walk result" % (
            mod, "no stage record" if rec is None else rec.get("stage"))}
    n = int(rec.get("pre_human_arrivals") or 0)
    lists = {"fix": list(fix or ()), "pick": list(pick or ()), "scene": list(scene or ()),
             "next_version": list(next_version or ())}
    ids = list(dict.fromkeys([i for k in WALK_LISTS for i in lists[k]] + [i for g in groups or () for i in g]))
    if not [i for k in WALK_HOLDS for i in lists[k]]:
        return {"ok": False, "why": "a walk that did not pass names at least one fix, pick or scene item"}
    stray = [i for g in groups or () for i in g if i not in lists["fix"] + lists["scene"]]
    if stray:
        return {"ok": False, "why": "a fixer group takes only fix or scene items: %s" % ", ".join(stray)}
    try:
        known = {x["id"]: x for x in ledger_items_caused_by(root, [], ended_too=True, named=ids + ([item] if item
                                                                                                    else []))}
    except Exception as e:      # noqa: BLE001
        return {"ok": False, "why": "the ledger cannot be read (%s: %s): nothing written" % (type(e).__name__, e)}
    unknown = [i for i in ids + ([item] if item else []) if i not in known]
    if unknown:
        return {"ok": False, "why": "no ledger event names %s: file each item first" % ", ".join(unknown)}
    ev = None
    if owner:
        ev, owhy = owner_event(root, owner, may_refuse_pass=True)
        if ev is None:
            return {"ok": False, "why": "his walk ends on his event: %s" % owhy}
    elif not conductor:
        return {"ok": False, "why": "a walk result needs --owner-said OWNER:<tsn> (his words ending the walk), or the "
                                    "Conductor's route: --per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM, or "
                                    "--conductor-decision"}
    p = walk_result_rel(n)
    if not _absent(os.path.join(mod_dir(root, mod), p)):
        return {"ok": False, "why": "%s already exists: a walk result is written once" % rel(mod, p)}
    t = now_ts()
    data = dict(lists, schema=1, mod=mod, version=rec.get("version"), arrival=n, verdict="not_passed", at=iso(t),
                by=by, why=why, to=to, item=item, walked=walked, passes=list(passes or ()),
                groups=[list(g) for g in groups or ()], conductor_decision=conductor,
                owner_said={"tsn": str(owner).split(":", 1)[-1], "words": str(ev.get("ownerSaid") or ev.get("byCard"))}
                if ev else None)
    md = walk_result_md(mod, rec.get("version"), n, data, {i: known[i].get("title") for i in known},
                        _owner_words_by_item(root, ids))
    res = advance(root, mod, to, by=by, why="walk %d not passed: %s" % (n, why), conductor=conductor, owner=owner,
                  first_files={p: json.dumps(data, indent=1, sort_keys=True) + "\n", walk_result_rel(n, "md"): md},
                  confirmed_extra={"walk_result": rel(mod, p)}, expect_stage="his_walk")
    res["path"] = rel(mod, p)
    if not res.get("ok"):
        res.setdefault("why", "; ".join("%s: %s" % (r.get("clause"), r.get("observed"))
                                        for r in (res.get("verdict") or {}).get("refusals") or []) or
                       res.get("moved_meanwhile") or "the move was refused")
    return res


def evidence_writers(root, mod, rec):
    """The units (and, for a move no unit made, the seat) that wrote this version's evidence: every move's, and every
    in-game row's `unit`."""
    out = set()
    for m in rec.get("moves") or []:
        out.add(str(m.get("unit") or m.get("by") or "").strip().lower())
    for n in visit_numbers(root, mod):
        for r in _jsonl(os.path.join(mod_dir(root, mod), INGAME_DIR, "visit_%d" % n, "rows.jsonl")) or []:
            out.add(str(r.get("unit") or "").strip().lower())
    out.discard("")
    return out


def read_walk_brief(root, mod, rec):
    """-> {path, by, why[]}: this arrival's walk brief (version/walk_brief/arrival_<N>.md, N = pre_human_arrivals) with
    each heading of WALK_BRIEF_HEADINGS non-empty and a `written_by: <unit>` line naming no evidence writer."""
    p = "%s/arrival_%d.md" % (WALK_BRIEF_DIR, rec.get("pre_human_arrivals") or 0)
    out = {"path": rel(mod, p), "why": []}
    text = read_text(root, mod, p)
    if text is None:
        out["why"].append("no walk brief at %s" % out["path"])
        return out
    lines = text.split("\n")
    for h in WALK_BRIEF_HEADINGS:
        at = next((i for i, ln in enumerate(lines) if re.match(r"^##\s+%s\s*$" % re.escape(h), ln, re.I)), None)
        if at is None:
            out["why"].append("the brief has no heading \"## %s\"" % h)
            continue
        end = next((j for j in range(at + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
        if not "".join(lines[at + 1:end]).strip():
            out["why"].append("the brief's \"%s\" is empty" % h)
    m = re.search(r"^written_by:\s*`?([^`\s]+)`?\s*$", text, re.M)
    out["by"] = m.group(1) if m else None
    if not m:
        out["why"].append("the brief has no written_by: <unit> line")
    elif m.group(1).lower() in evidence_writers(root, mod, rec):
        out["why"].append("written_by %s made evidence writes for this version (a move or an in-game row): the brief "
                          "is a fresh read" % m.group(1))
    tt, _ = read_json(root, mod, "version/test_table.json")
    out["why"] += walk_brief_raid_why(root, mod, max(1, len(ingame_openings(rec))), tt, text)
    out["why"] += walk_brief_moved_why(root, mod, text)
    return out


def _held_names(tt, tid):
    """-> the held owner statements whose test text names check tid as a whole word ("T_UNDERLIQUID + OL_... (row)")."""
    pat = re.compile(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(tid))
    return [h for h in (tt or {}).get("held_statements") or [] if isinstance(h, dict) and pat.search(str(h.get("test") or ""))]


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


def ledger_items_caused_by(root, ids, ended_too=False, named=()):
    """-> [{id, title, needs}] for the ledger items filed (file or spawn) with caused_by one of ids and not closed,
    dropped or superseded since (ended_too: those as well), read from every shard under
    infrastructure/state/ledger/events/. `needs` is the item's current window (ledger_needs), None when it never had
    one. named: item ids taken as well, whatever their caused_by, when any ledger event names them (the items a visit's
    failed lines cite, visit_cited_items; design/specs/2026-11-21-visit-wait-cited-items/boundary.md)."""
    d = os.path.join(root, "infrastructure", "state", "ledger", "events")
    want, filed, ended, named = set(ids), {}, set(), set(named or ())
    for f in sorted(os.listdir(d)) if os.path.isdir(d) and (want or named) else []:
        if not f.endswith(".jsonl"):
            continue
        with open(os.path.join(d, f), encoding="utf-8") as fh:
            for ln in fh:
                if '"caused_by"' not in ln and '"close"' not in ln and '"drop"' not in ln and '"supersede"' not in ln \
                        and not (named and any(n in ln for n in named)):
                    continue
                try:
                    e = json.loads(ln)
                except ValueError:
                    continue
                if e.get("id") in named and (e.get("id") not in filed or e.get("event") in ("file", "spawn")):
                    filed[e.get("id")] = e.get("title") or filed.get(e.get("id")) or ""
                if e.get("event") in ("file", "spawn") and e.get("caused_by") in want:
                    filed[e.get("id")] = e.get("title") or ""
                elif e.get("event") in ("close", "drop", "supersede"):
                    ended.add(e.get("id"))
    live = [k for k in sorted(filed) if ended_too or k not in ended]
    needs = ledger_needs(root, live)
    return [{"id": k, "title": filed[k], "needs": needs.get(k)} for k in live]


def ledger_live_endings(root, ids):
    """-> {id: {"sat": tsn, "ends": [{"tsn", "unit"}]}} for these ledger items: the tsn of the item's last TESTPILOT_SAT
    note (0 when none) and its LEFT OPEN endings after it, one per run (a note's role_unit; a note with none, a hand
    note, counts alone), ordered by tsn; None when the ledger folder cannot be read (UNMEASURED, never zero endings).
    The Maturation tick's Test Pilot step counts these (RIMMANDRAKE_ROUTE_SPENT_LIVE_FIXER_PILOT_BY_HAND)."""
    d = os.path.join(root, "infrastructure", "state", "ledger", "events")
    if not os.path.isdir(d):
        return None
    want, notes = set(ids), {i: [] for i in ids}
    try:
        for f in sorted(os.listdir(d)) if want else []:
            if not f.endswith(".jsonl"):
                continue
            with open(os.path.join(d, f), encoding="utf-8") as fh:
                for ln in fh:
                    if '"note"' not in ln or ("LEFT OPEN:" not in ln and "TESTPILOT_SAT" not in ln):
                        continue
                    try:
                        e = json.loads(ln)
                    except ValueError:
                        continue
                    text = e.get("text") or ""
                    if e.get("event") == "note" and e.get("id") in want and str(e.get("tsn") or "").isdigit() and \
                            text.startswith(("LEFT OPEN:", "TESTPILOT_SAT")):
                        notes[e["id"]].append((int(e["tsn"]), text.startswith("TESTPILOT_SAT"), e.get("role_unit")))
    except (OSError, UnicodeDecodeError):     # a shard that cannot be read: no partial count
        return None
    out = {}
    for i, got in notes.items():
        got.sort()
        sat = max([t for t, is_sat, _ in got if is_sat] or [0])
        ends, seen = [], set()
        for t, is_sat, unit in got:
            if t > sat and not is_sat and (unit is None or unit not in seen):
                seen.add(unit) if unit else None
                ends.append({"tsn": t, "unit": unit})
        out[i] = {"sat": sat, "ends": ends}
    return out


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


def ledger_titles(root, ids):
    """-> {id: title} for these ledger items: the title of the newest event that carries one (file, spawn or a later
    edit), in time order. An item with no titled event is absent."""
    d = os.path.join(root, "infrastructure", "state", "ledger", "events")
    want, seen = set(ids), []
    for f in sorted(os.listdir(d)) if os.path.isdir(d) and want else []:
        if not f.endswith(".jsonl"):
            continue
        with open(os.path.join(d, f), encoding="utf-8") as fh:
            for ln in fh:
                if '"title"' not in ln:
                    continue
                try:
                    e = json.loads(ln)
                except ValueError:
                    continue
                if e.get("id") in want and e.get("title"):
                    seen.append((str(e.get("ts") or ""), e.get("tsn") or 0, e["id"], str(e["title"])))
    return {i: t for _, _, i, t in sorted(seen, key=lambda x: (x[0], x[1]))}


def bars_named_by(root, mod, ids):
    """-> {bar: [item ids]}: each bar of the mod's test table whose id one of these items' ledger titles names as a
    whole word. The game-only blind exit reads it (read_exit); a bar no title names is absent."""
    tt, _ = read_json(root, mod, "version/test_table.json")
    titles = ledger_titles(root, ids)
    out = {}
    for b in (tt or {}).get("bars") or []:
        bid = b.get("id") if isinstance(b, dict) else None
        if not bid:
            continue
        pat = re.compile(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(str(bid)))
        got = sorted(i for i in ids if pat.search(titles.get(i, "")))
        if got:
            out[bid] = got
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


def unrun_owed(root, mod, tt=None, carried=None, git=None):
    """-> the UNRUN rows still owed a run, each with `owed_why`. A row is met when its check's deciding row (carried_rows:
    {check: row}) ran on a commit that contains the UNRUN row's sha; when git cannot resolve either commit, when that row
    is of a visit that opened after the UNRUN row was written. design/specs/2026-11-24-walk-owes-its-checks/boundary.md."""
    rows = unrun_live(read_unrun(root, mod), tt if tt is not None else read_json(root, mod, "version/test_table.json")[0],
                      moved_to_next(root, mod, "scenes"))
    if not rows:
        return []
    last = BM.carried_rows(root, mod) if carried is None else carried
    rec = load(root, mod)
    opened = ingame_openings(rec) if rec else {}
    g = git or BM.RR.Git(root)
    held_, out = {}, []
    for u in rows:
        r = last.get(u.get("check"))
        if not r or LK.spoiled(r):
            out.append(dict(u, owed_why="no run of it speaks for the mod"))
            continue
        a, b = g.rev(u.get("sha")), g.rev(r.get("mod_sha"))
        if a and b:
            if (a, b) not in held_:
                held_[(a, b)] = a == b or g._git("merge-base", "--is-ancestor", a, b) is not None
            if not held_[(a, b)]:
                out.append(dict(u, owed_why="its last row ran on %s, which does not hold %s" % (
                    r.get("mod_sha"), u.get("sha"))))
            continue
        t_open, t_row = _ts(opened.get(r.get("_visit"))), _ts(u.get("at"))
        if t_open is None or t_row is None or t_open <= t_row:
            out.append(dict(u, owed_why="git cannot resolve %s or %s, and its last row is of no later visit" % (
                u.get("sha"), r.get("mod_sha"))))
    return out


def _git_log(root, since, until, path):
    """-> [(commit, [files])] oldest first, committed in (since, until] under path; raises OSError when git cannot say."""
    try:
        # --since ends git's walk: the whole history of a path reads 900 MB of pack. A day early, for commit clocks that
        # run back; the exact line is drawn below.
        r = own_cgroup.run(["git", "-C", root, "log", "--reverse", "--no-merges", "--format=%x00%H %ct", "--name-only",
                            "--since=%d" % (int(since) - 86400), "--", path], capture_output=True, text=True, timeout=120)
    except subprocess.SubprocessError as e:
        raise OSError("git cannot list the commits of %s: %s" % (path, e)) from e
    if r.returncode:
        raise OSError("git cannot list the commits of %s: %s" % (path, r.stderr.strip()[-200:]))
    out = []
    for blk in r.stdout.split("\0")[1:]:
        head, _, names = blk.partition("\n")
        sha, t = head.split()
        if since < int(t) <= until:
            out.append((sha, [x for x in names.split("\n") if x]))
    return out


def landed_at_walk(root, mod, rec, n):
    """-> the commits that changed the mod's shipped C# or XML while it stood at Stage 7 or 8 before visit n opened: each
    owes one fresh reader (a fix made outside any sitting, which no other reader sees). [] when visit n opened from
    another stage, or by his walk's own result (its fixes come after it). Raises OSError when git cannot list them."""
    moves = [m for m in (rec or {}).get("moves") or [] if isinstance(m, dict)]
    into = [i for i, m in enumerate(moves) if m.get("to") == "in_game"]
    if n < 1 or n > len(into):
        return []
    mv = moves[into[n - 1]]
    if mv.get("from") not in ("pre_human", "his_walk") or (mv.get("confirmed") or {}).get("walk_result"):
        return []
    left = next((m for m in reversed(moves[:into[n - 1]]) if m.get("to") == "pre_human"), None)
    t1, t2 = _ts((left or {}).get("at")), _ts(mv.get("at"))
    if t1 is None or t2 is None:
        raise OSError("the moves around visit %d carry no time that reads" % n)
    base = BM.RR.mod_root(mod)
    log = _git_log(root, t1, t2, base + "/")
    if not log:
        return []
    ships = BM.RR.Relation(root, mod, {}).shipped_cs("HEAD")[0]
    return [sha for sha, files in log if any(f in ships or f.endswith(".xml") for f in files)]


def walk_owed(root, mod, rec=None):
    """-> {owed: {check: why}, why: [cause]}: the in-game checks that must run before he walks (Stage 7 and 8). Owed: an
    UNRUN row not met, or a row the build match no longer counts because the change touches its check or cannot be related
    to it. why: what could not be read; then nothing is known to be clean. It never raises."""
    out = {"owed": {}, "why": []}
    try:
        rec = rec or load(root, mod)
        tt, terr = read_json(root, mod, "version/test_table.json")
        if tt is None:
            out["why"].append("version/test_table.json: %s" % terr)
            return out
        tests, last = dict(ingame_tests(tt)), BM.carried_rows(root, mod)
        for u in unrun_owed(root, mod, tt, carried=last):
            if u.get("check") in tests:     # a check outside the table has no row a program knows: it holds nothing
                out["owed"].setdefault(u["check"], "UNRUN: %s" % u["owed_why"])
        # the relation first: with nothing touched no row of a check can stop counting for a change, and the walk folder
        # (about 30 s of Windows reads for Pyrelands) is not read by every tick
        rel_ = BM.RR.relate(root, mod, tests, {t: r for t, r in last.items() if t})
        if not (rel_["touched"] or rel_["unreadable"]):
            return out
        n = max(1, len(ingame_openings(rec)))
        ex = read_ingame_exit(root, mod, n, tt)
        bm = ex.get("build_match")
        if not bm:
            out["why"].append("visit %d gives no build match (its exit reads %s)" % (n, ex.get("state")))
        elif bm.get("walk_why"):
            out["why"].append("the walk build cannot be read: %s" % "; ".join(bm["walk_why"]))
        else:
            for t in bm["rerun"]:
                x = bm["rows"][t]
                if x.get("relation") in ("touched", "unreadable"):
                    out["owed"].setdefault(t, x["why"])
    except Exception as e:      # noqa: BLE001  a reading that cannot be made is named, never read as clean
        out["why"].append("the in-game checks owed could not be read (%s: %s)" % (type(e).__name__, e))
    return out


def unrun_lines(root, mod):
    """-> the Stage 6 brief's lines for the in-game checks still UNRUN (unrun_owed): a met one is not run again."""
    tt = read_json(root, mod, "version/test_table.json")[0]
    return unrun_lines_of(unrun_owed(root, mod, tt), tt, moved_to_next(root, mod, "scenes"))


def unrun_live(rows, tt, moved=()):
    """-> those UNRUN rows without the check of a paused raid scene, of one that another check of the table replaces, or
    of one that moved to the next version."""
    tests = (tt or {}).get("tests") or {}
    gone = {x for t in tests.values() if isinstance(t, dict) for x in t.get("replaces") or []} | set(moved)
    return [r for r in rows or [] if r.get("check") not in gone and not (RP.paused() and RP.stages(tests.get(r.get("check"))))]


def unrun_lines_of(rows, tt, moved=()):
    """-> those lines, one per row of unrun_live."""
    rows = unrun_live(rows, tt, moved)
    if not rows:
        return ["- none recorded"]
    return ["- Item `%s` (closed offline on `%s` at %s): in-game check `%s` is UNRUN; run `%s`." % (
        r.get("item"), r.get("offline"), r.get("sha"), r.get("check"), r.get("command")) for r in rows]


def ingame_facts(root, mod):
    """-> what in-game acceptance owes now: visit (the moves into in_game so far), exit (read_ingame_exit of visit_N),
    checks (the stage-6 ids), testq (those carrying a testq block: what SteveDesktop's queue may admit), and owed:
    "run" (no visit_N folder, or only the test lane's rows in it: a live driver is owed) | "no exit block" | "exit met" | "exit not met" | "blocked" (a
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
                "tag_flaws": LK.table_flaws(tt),
                "full_list": [k for k, t in checks if BM.is_full(t)],
                "testq": [k for k, t in checks if isinstance(t.get("testq"), dict)]})
    try:
        out["to_run"], out["counted_earlier"] = ingame_to_run(root, mod, n, tt)
    except Exception as e:      # a relation that cannot be read relates nothing: every check runs
        out["to_run"], out["counted_earlier"] = [k for k, _ in checks], []
        out["to_run_why"] = "the change relation could not be read (%s: %s)" % (type(e).__name__, e)
    out["owed"] = ("blocked" if blocked else "run" if ex["state"] == "absent" else
                   "no exit block" if ex["state"] == "no_exit_block" else
                   "exit met" if ex["state"] == "met" else "exit not met")
    return out


def bridge_idle(purpose, seat="BENCH", runner=subprocess.run, game=None, lock=None):
    """-> (takeable, text): may a NEW run take game `game` (None: a)? Read from the game's lock, the one record of who
    drives it (game_lock.py, RIMMANDRAKE_BUILD_ONE_GAME_LOCK_CLAIM_FOUR_RECORDS_DISAGREE): any live holder, this
    shell's own window included, is a hold; a holder whose process is gone holds nothing; a lock that cannot be read is
    not takeable; a flyer's flight never is. Only his OWNER lock, whose rule needs his interactions measured, and a
    machine with no lock readable here, ask `rimflow bridge idle` (the delegated take's own verdict, read-only).
    MATURATION_BRIDGE_IDLE names a stand-in command (the selftests'); a reading that fails is not takeable.
    lock: a game_lock.query stand-in (the selftests')."""
    cmd = os.environ.get("MATURATION_BRIDGE_IDLE")
    if not cmd:
        import game_lock as GL
        g = game or "a"
        if GL.flight_purpose(purpose):
            return False, "NOT TAKEABLE  refused: flyer flight is never delegated (needs a human present)"
        path = GL.lock_path(g)
        if path or lock:
            r = (lock or GL.query)(g, pipe=False, path=path)
            if r["state"] == "UNKNOWN":
                return False, "NOT TAKEABLE  " + r["line"]
            if r.get("seat") != "OWNER":
                if r["state"] == "HELD":
                    return False, "NOT TAKEABLE  " + r["line"]
                return True, "TAKEABLE  " + r["line"]
    argv = ([sys.executable, cmd] if cmd else [sys.executable, os.path.join(HERE, "cli.py")]) + [
        "bridge", "idle", "--for", purpose, "--seat", seat]
    import game_instance as GI
    env = GI.child_env(game or "a")
    try:
        r = runner(argv, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL, env=env)  # budget: class=rimflow
    except (OSError, subprocess.SubprocessError) as e:
        return False, "the bridge reading failed: %s" % e
    text = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()
    line = next((x for x in reversed(text) if x.startswith(("TAKEABLE", "NOT TAKEABLE"))), text[-1] if text else "")
    go = r.returncode == 0 and line.startswith("TAKEABLE")
    if go and not cmd:      # seat BENCH reads another BENCH run's hold as ours: a live holder process is that run's
        import host_guard   # new_run: the question is for a NEW run, so this shell's own window hold is a hold too
        with host_guard.instance_env(game if game and game != "a" else None):
            held = host_guard.crossing(new_run=True)
        if held:
            return False, "NOT TAKEABLE  %s: %s" % (_gn(game or "a"), held)
    return go, line or "no reading (rc %s)" % r.returncode


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
        if x.get("cheaper_why"):
            out.append("  - no cheaper test decides it, because: %s" % x["cheaper_why"])
        if LK.kind(x) != "A":
            xy = LK.x_of_y(x)
            out.append("  - kind %s: budget %s run(s)%s; evidence: %s%s" % (
                LK.kind(x), LK.budget(x) or "NONE", "; passes on %d of %d" % xy if xy else "",
                x.get("tag_evidence") or "NONE", "".join("; NOT USABLE: %s" % w for w in LK.tag_flaws(x))))
    return out


def ingame_to_run(root, mod, n, tt):
    """-> (to_run, counted): the stage-6 checks visit n runs, and those it does not because an earlier visit's last row
    is a PASS that the change since its commit does not touch (rerun_relation.py; owner, 2026-11-21: only the checks a
    change touches run again). A check with no earlier row, a last row that is not a PASS (a spoiled or INCONCLUSIVE
    scene, live_kinds.py), a touched check and one whose relation cannot be read all run. The Stage 6 exit's build match reads the walk build and decides for good."""
    checks = ingame_tests(tt or {})
    if n <= 1:
        return [k for k, _ in checks], []
    last = BM.carried_rows(root, mod, n - 1)
    runs = BM.check_runs(root, mod, n - 1)
    rel = BM.RR.relate(root, mod, dict(checks), {t: r for t, r in last.items() if t})
    unrun = {u.get("check") for u in unrun_owed(root, mod, tt, carried=last)}
    run, counted = [], []
    for k, spec in checks:
        r = last.get(k)
        st = (rel["rows"].get(k) or {}).get("state")
        x = LK.reading(spec, runs.get(k)) if r else None
        if x is not None:       # the kind and the outcomes say whether the scene passes on its runs
            r = dict(x["use"], verdict="PASS" if x["passes"] else "FAIL")
        if r and str(r.get("verdict", "")).upper() == "PASS" and r.get("site_checked") is True and st == "untouched" \
                and k not in unrun:
            counted.append(k)
        else:
            run.append(k)
    return run, counted


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
    every = f.get("checks") or []
    checks = list(f["to_run"]) if f.get("to_run") is not None else list(every)     # ingame_facts read the relation
    counted = list(f.get("counted_earlier") or [])
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
         "scripted verdict; exploring and screenshots run on Archmagi. SteveDesktop's queue takes any mod's token-free "
         "checks whatever its stage (the owner dropped the 2026-11-14 pipeline-only limit on 2026-11-17); it refuses only "
         "a mod on his hold (`src/RimMandrake/Utils/testq/pipeline_admit.py`). It runs what a stage-6 entry's `testq` block "
         "names (modcheck chains, or the check's own script: `testq.py submit --checks`): %s." % (
             "%d of %d of this mod's checks carry one (%s); queue those with `testq.py submit` if SteveDesktop is "
             "free, and run the rest here" % (len(f.get("testq") or []), len(checks), ", ".join(f["testq"]))
             if f.get("testq") else "none of this mod's %d checks carries one, so this visit runs them on Archmagi "
             "through the bridge" % len(checks)), "",
         "## The bridge and the game (rules; each one binds)", ""]
    L += [r % tuple(x for x in ((purpose, seat) if "take --idle-ok" in r else (seat,) if "release" in r else
                                (mod,) if "deploy_custom_mods" in r else ()))
          for r in BRIDGE_RULES]
    L += ["", "## The checks to run: %d of the %d stage-6 in-game checks of `design/concepts/%s/version/test_table.json`"
          % (len(checks), len(every), mod), "",
          "Only the checks a change touches run again (root CLAUDE.md, After a change, only the checks that the change "
          "touches run again). %s" % (
              "%d check(s) keep their PASS from an earlier visit, because the change since that row's commit touches "
              "nothing they read or exercise (`python3 src/RimMandrake/rimflow/rerun_relation.py --mod %s` names "
              "them and the change). Do not run them. If you change the mod in the sitting, run "
              "`python3 src/RimMandrake/rimflow/build_match.py check --mod %s` and run only the checks it names."
              % (len(counted), mod, mod) if counted else
              "This is the first visit, or no earlier row still counts, so every check runs. If you change the mod in "
              "the sitting, run `python3 src/RimMandrake/rimflow/build_match.py check --mod %s` and run again only "
              "the checks it names." % mod) + (" %s" % f["to_run_why"] if f.get("to_run_why") else ""), "",
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
    raids = paused_lines(root, mod, n, tt)
    if raids:
        L += ["", "## Raid scenes: paused", "", "No run stages a raid (standing_rulings.md §The cheapest test that decides the "
              "bar). The bridge client refuses the calls."] + raids
    try:
        big = SZ.brief_lines(root, mod, tt)
    except Exception as e:  # noqa: BLE001 - a size that could not be read never stops a brief; the line says so
        big = ["- could not look at the scenes' size: %s: %s" % (type(e).__name__, e)]
    if big:
        L += ["", "## Oversized scenes: shrink one before you run it again", "", "Each of these owes its evidence that no "
              "cheaper test decides its bar (standing_rulings.md §The cheapest test that decides the bar; "
              "`src/RimMandrake/rimflow/scene_size.py`). A row that stands is not run again for this."] + big
    L += ["", "## Beyond the checks", "",
          "Explore past the bars on the same maps: plentiful screenshots (`src/RimMandrake/Utils/system_screenshot.py` "
          "for the desktop, the bridge's capture for the map), looked at, not only taken. Every strange thing no bar "
          "covers is a row of `strange.jsonl`: explained (what it is and why it is fine) or filed (a rimflow item, its "
          "id in the row). Screenshots go in `%s/screenshots/` only if under 1 MB each; else name their paths." % vdir,
          "", "## A live test declares its kind", "", LIVE_KINDS_RULE,
          "", "## A FAIL is diagnosed and classed in the sitting", "",
          "A FAIL or UNMEASURED is not a verdict to carry home bare: diagnose it by experiment while the game is up "
          "(change one thing, watch the row), and class it.", "", WRONG_CHECK_RULE, FREE_GAME_RULE, "",
          "What each class does here (`read_ingame_exit` reads these row fields):",
          "- **Mod wrong, and you can fix it** (`class: \"MOD\"` on the failed row): fix it in the sitting. Write the "
          "before/after test first and see it red on the parent, fix the mod, see it green, commit, redeploy, and re-run "
          "the checks that the fix touches on the fixed build (`build_match.py check` names them; every other row still "
          "counts). Write the re-run row of this check with `mod_fix`: `{\"commit\": <sha>, \"unit\": "
          "<your unit>, \"red\": {\"cmd\": ..., \"rc\": <non-zero>, \"on\": <parent>}, \"green\": {\"cmd\": ..., "
          "\"rc\": 0, \"on\": <sha>}}`. Then one fresh reader, a run that did not make the fix, reads only that fix, "
          "once, and writes `%s/%s` (`{\"fix\": <sha>, \"reader\": <its unit>, \"verdict\": \"sound\"|\"unsound\", "
          "\"why\"}`); the steward run that reads this visit is that reader. Never write that file yourself." % (
              vdir, FIX_REVIEWS),
          "- **Mod wrong, and you cannot fix it in the sitting**: the row stays FAIL; say why on the row (`unfixed`: no "
          "tools, the fix is not known, another run holds the files, one of his five acts, a north-star bar). It goes "
          "down its road back (spec Stage 6: the lowest stage that can show it, an offline test that fails on the old "
          "code first), and a new visit reruns it on the fixed build.",
          "- **Check or scene wrong, and a bar needs it** (`class: \"HARNESS\"` or `\"SITE\"` on the failed row): repair "
          "the check or the scene, commit the repair, keep the deployed build (the rows keep its `mod_sha`), plant the "
          "fault and run the repaired check on it, then run it on the real build. Write the re-run row with `repair`: "
          "`{\"class\": \"HARNESS\"|\"SITE\", \"commit\": <sha>, \"planted\": {\"plant\": <what you planted>, "
          "\"command\": ..., \"verdict\": \"FAIL\", \"evidence\": <path>}}`; that row's own PASS is the real-build "
          "reading. The earlier HARNESS or SITE row spends nothing. No item. When no plant exists, or you cannot repair "
          "it, the row says `unrepaired` (why) and `owner` (your item, or the item you file with the evidence): the "
          "check is not counted and its bar reads undecided.",
          "- **Check or scene wrong, and no bar needs it** (another check decides each of its bars): remove it from the "
          "test table (`design/concepts/%s/version/test_table.json`: the entry, and its id in each bar's `decides`), "
          "delete its code when nothing else names it, and write one line on `%s/polish.md` as the record. No item. The "
          "exit reads a needless check left in the table as not met." % (mod, vdir),
          "- A FAIL or UNMEASURED row with no class never passes: the exit reads it not met. A spoiled run needs no class and no "
          "later PASS: with no valid run beside it, its line reads `spoiled` and the scene runs again.",
          "- **File your own failures before you end**, while you hold them: each line that still goes back (a mod "
          "fault you could not fix, a needed check not counted) is one named rimflow item, `--caused-by` your item, with "
          "its acceptance test (red now, green on a fix) and what you found; write its id on the row as `filed`. The "
          "road back starts from your items; no router run rebuilds them.", "",
          "Run the remaining checks all the same.", "",
          "## The record (skeleton first: create it before the first live call)", "",
          "`%s/`:" % vdir,
          "- `rows.jsonl`: one row per run: `{\"test\": id, \"verdict\": \"PASS\"|\"FAIL\"|\"UNMEASURED\", "
          "\"outcome\": one of the seven, \"spoiled_by\": ..., \"forbidden\": [...], "
          "\"site_checked\": true, \"game\": \"archmagi\"|\"stevedesktop\", \"mod_sha\": <sha of the deployed source>, "
          "\"command\": ..., \"evidence\": <path>, \"held\": [what the site switched off or locked for this run, e.g. "
          "\"fire\", \"weather\"; [] when the whole mod ran]}`, merged with the one JSON line `python3 "
          "src/RimMandrake/rimflow/build_match.py identity --mod %s --tier <the tier you loaded>` prints, run on the game machine after the deploy and the list "
          "swap: `mod_hash` (the deployed folder), `game_build`, `active_mods` (ModsConfig.xml, parsed, in order), "
          "`tier`, `unit`. The BUILD MATCH (owner, 2026-11-17, narrowed 2026-11-21) counts a row when its "
          "game build equals the build he walks (on the game that holds the labelled savegame below), its list is the "
          "list modset_builder.py builds for its tier, and its mod hash equals the walk's or the change since its `mod_sha` touches nothing its check reads or "
          "exercises. A row without the fields, or one the change touches, runs again; no other row does. Redeploying "
          "changes the hash: identity again after every deploy." % mod,
          "- `strange.jsonl`: as above; an empty file when nothing strange was seen.",
          "- the labelled savegame for his walk (dense, labelled scenes; spec rule 5), its path in the block. Stage it on the "
          "mod's small list, never the full list (`python3 src/RimMandrake/Utils/small_list.py show %s` prints the tier and "
          "its mods); the game whose Saves folder holds it is the game he walks on, ArchBig or ArchSmall." % mod,
          "- `SUMMARY.md`: what ran, what failed and what you did about it, the owed cases one by one, then this block "
          "(the program reads it):", "",
          "```", "## Exit", "```", "ingame_rows: {%s}" % ", ".join("%s: pass|fail|unmeasured" % k for k in checks[:3])
          + (" ... every one of the %d" % len(checks) if len(checks) > 3 else ""),
          "strange_open: <count neither explained nor filed>", "savegame: <its full path>", "exit_met: true|false",
          "```", "```", "",
          "`python3 src/RimMandrake/rimflow/maturation.py next %s` reads it and checks it against the files: met needs "
          "every counted check pass in the block AND PASS in its last row with the site checked, the game and mod_sha "
          "named (a needed check not counted, said unrepaired or repaired and not shown both ways, reads unmeasured "
          "in the block and leaves its bar undecided; a mod fix made in the sitting needs its fresh reader's review), "
          "every row on the walk build (`build_match.py check --mod %s` reads that part alone), every strange thing "
          "explained or filed, and the savegame on disk. That reading is evidence for the steward, "
          "not a move: the Conductor reads your SUMMARY.md and advances with `--to pre_human --steward-confirms "
          "\"...\"`, or sends a line item down its road back. Never run `maturation.py advance`." % (mod, mod), "",
          SELF_CHECK_RULE % mod, "",
          "## Report (10 lines or fewer, plain words)", "",
          "Tag every number [measured] or [guess ~N%%]: checks PASS of %d, FAIL, UNMEASURED; each owed case's outcome; "
          "each failed line's class; each mod-wrong FAIL's filed item; each repaired check's commit and its planted and "
          "real readings; each mod fix made in the sitting and its before/after test; each check removed; each item you "
          "filed; strange things seen, explained, filed; the savegame path; the mod list "
          "and game; whether the exit is met; bridge released." % len(checks)]
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


def build_parser():
    """The parser of main(), apart so that brief_commands.py fills a run's command lines from it."""
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
        if c == "next":     # tuning tripwire T1; inside a detached run both default to the run's own diff and item
            p.add_argument("--diff-file", help="a unified diff to read for the tuning tripwire")
            p.add_argument("--item", help="the item whose number-only diffs are counted")
    tp = sub.add_parser("tag-pass", help="tag a passed version again: mod/<Mod>/v<version> on the commit that "
                                         "records its pass, pushed (the retry of a PASSED BUT NOT TAGGED)")
    tp.add_argument("mod")
    tp.add_argument("--version", help="default: the stage record's version")
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
    w = sub.add_parser("walk-result", help="record a Stage 8 walk that did NOT pass and take its road back "
                                           "(design/specs/2026-11-22-walk-result/boundary.md)")
    w.add_argument("mod")
    w.add_argument("--to", required=True, choices=ROADS_BACK["his_walk"])
    w.add_argument("--by", required=True)
    w.add_argument("--why", required=True)
    w.add_argument("--owner-said", help="OWNER:<tsn>, his event ending the walk")
    w.add_argument("--conductor-decision")
    w.add_argument("--per-ruling", help="CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: the Conductor's instruction, carried as his words; --why holds its text")
    w.add_argument("--item", help="the route item that records the walk (the tick's road back is caused by it)")
    for k in ("fix", "pick", "scene", "next"):
        w.add_argument("--" + k, default="", help="ID[,ID...]")
    w.add_argument("--group", action="append", default=[], help="A+B[+C]: one fixer run for these fix/scene items")
    w.add_argument("--pass", dest="passes", action="append", default=[], help="a pass he stated (repeatable)")
    w.add_argument("--walked", help="when and where he walked")
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
    c.add_argument("--resume", action="store_true", help="with --run: the default since 2026-11-21, kept so old "
                   "callers still parse (a decider already green on its current build and command is kept, unrun)")
    c.add_argument("--all", metavar="WHY", help="with --run: a full pass, every offline test, as a named act with its "
                   "reason (owner, 2026-11-21: only the checks a change touches run again; a full pass is never a "
                   "default)")
    c.add_argument("--json", action="store_true")
    c.add_argument("--grandfather", action="store_true", help="write the mod's red_seen grandfather list once (every test "
                   "as it is now owes no red proof until edited); a list already written is never widened")
    rs = sub.add_parser("red-seen", help="prove a deciding test can fail: apply a planted fault, run it, want red, "
                        "reverse it; only a red run is recorded (version/evidence/red_seen.json)")
    rs.add_argument("mod")
    rs.add_argument("test")
    rs.add_argument("--patch", required=True, help="the planted fault, a unified diff applied with git apply in the root")
    la = sub.add_parser("launch")
    la.add_argument("mod")
    la.add_argument("--budget-usd", type=float, required=True, help="the spend cap; required, no default")
    la.add_argument("--item", required=True, help="the ledger item the run works under (filed on origin/main)")
    la.add_argument("--model", default="opus", choices=("fable", "opus", "sonnet"))
    la.add_argument("--seat", default="BENCH")
    gr = sub.add_parser("game-repair", help="the Dispatch step's deploy unit's body: read, deploy and read again a mod's "
                        "game copy under the game's driver lock (one JSON line; the Dispatch step reads it)")
    gr.add_argument("mod")
    gr.add_argument("--game", required=True)
    gr.add_argument("--kind", required=True, choices=("visit", "walk"))
    gr.add_argument("--purpose", required=True)
    gr.add_argument("--seat", default="BENCH")
    return ap


def main(argv=None):
    ap = build_parser()
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
        print("%s %s: %s since %s; blind cycles %s; arrivals at the walk brief %s; moves %d"
              % (o.mod, rec["version"], label(rec["stage"]), rec["since"], rec.get("cycles"),
                 rec.get("pre_human_arrivals"), len(rec.get("moves") or [])))
        for st, t in spend_by_stage({"spend": version_spend_rows(root, o.mod, rec)}).items():
            # weighted tokens only (the owner, 2026-11-16: "Please speak in terms of weighted tokens not money.")
            # weighted_v2 only in the sum; older units are labelled apart, never added in (RELABEL_SPEND_PRINTERS_STILL_V1)
            other = "".join(", plus %s %s tokens not converted" % (n, u) for u, n in sorted(t["tokens_other"].items()))
            print("  spend %s: %s weighted tokens (%s)%s, %s s wall, %d entries (%d estimates, %d unmeasured fields)"
                  % (" + ".join(label(x) for x in st.split("+")), t["tokens"], t["unit"], other,
                     round(t["wall_s"]) if isinstance(t["wall_s"], (int, float)) else t["wall_s"], t["entries"],
                     t["estimates"], t["unmeasured"]))
        return 0
    if o.cmd == "next":
        nx = next_step(root, o.mod)
        # tuning tripwire T1: a note, never a refusal; the exit code stays next's own
        if o.diff_file:
            try:
                with open(o.diff_file, encoding="utf-8", errors="replace") as fh:
                    dtext, item, dwhy = fh.read(), o.item, None
            except OSError as e:
                dtext, item, dwhy = None, o.item, "%s: %s" % (type(e).__name__, e)
        else:
            dtext, item = run_diff(root, o.mod)
            dwhy = item if dtext is None else None
            item = o.item or (item if dtext is not None else None)
        if dtext is not None:
            tw = tripwire(dtext, item, tripwire_history(item)) if item else None
            nx["tripwire"] = tw if tw else {"note": None, "read": True}
        elif dwhy:
            nx["tripwire"] = {"note": None, "read": False, "why": dwhy}
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
            if g.get("to_run") is not None:
                print("  checks to run in visit %s: %d (%s); %d keep their PASS from an earlier visit (the change since "
                      "touches nothing they read or exercise)%s" % (
                          g.get("visit"), len(g["to_run"]), ", ".join(g["to_run"]) or "none",
                          len(g.get("counted_earlier") or []),
                          "; %s" % g["to_run_why"] if g.get("to_run_why") else ""))
        print("  launch: %s" % nx.get("launch", "none"))
        tw = nx.get("tripwire") or {}
        if tw.get("note"):
            print("  tuning tripwire: %s (%s)" % (tw["note"], ", ".join(tw["constants"])))
        elif tw.get("read") is False:
            print("  tuning tripwire: diff UNMEASURED (%s)" % tw.get("why"))
        print("  may run: %s (%s)" % (nx["may_run"]["result"], nx["may_run"]["why"]))
        print("  " + nx["tick"]["line"])
        print(nx["next"])
        return 0
    if o.cmd == "tag-pass":
        ver = o.version
        if not ver:
            rec = load(root, o.mod)
            ver = rec.get("version") if rec else None
        if not ver:
            print("REFUSED: %s has no stage record and no --version" % o.mod)
            return 1
        tr = tag_pass(root, o.mod, ver)
        print(tag_line(tr).replace("PASSED BUT NOT TAGGED", "NOT TAGGED"))
        return 5 if tr.get("untagged") else 0
    if o.cmd == "advance":
        if load(root, o.mod) is None:
            print("REFUSED: %s has no stage record; run maturation.py seed %s first" % (o.mod, o.mod))
            return 1
        if o.per_ruling == CONDUCTOR_ACTS:      # owner 2026-11-19: the Conductor window's act, never a helper's
            import conductor_acts as CA
            ok, txt = CA.check("advance %s" % o.mod, o.why)
            if not ok:
                print("REFUSED: %s" % txt)
                return 1
        res = advance(root, o.mod, o.to, by=o.by, why=o.why, steward=o.steward_confirms,
                      conductor=o.conductor_decision, owner=o.owner_said or (("per-ruling %s: %s" % (o.per_ruling, o.why)) if o.per_ruling else None), waits_on=o.waits_on,
                      game_only=[x.strip() for x in (o.game_only or "").split(",") if x.strip()] or None)
        if res.get("malformed"):
            print("MALFORMED REFUSAL (a bug in maturation.py): %s" % "; ".join(res["malformed"]))
            return 3
        said = submit_line(res)
        if o.json:
            v = dict(res["verdict"])
            v["given"] = {"criteria": v["given"]["criteria"], "inputs": sorted(v["given"]["inputs"])}
            print(json.dumps({"ok": res["ok"], "verdict": v, "submit": res.get("submit"),
                              "submit_error": res.get("submit_error"), "tag": res.get("tag"),
                              "untagged": res.get("untagged"), "tag_taken": res.get("tag_taken")},
                             indent=2, ensure_ascii=False))
        elif res["ok"]:
            print("ADVANCED %s: %s to %s; journal and %s written" % (o.mod, label(res["from"]), label(o.to), RECORD))
            if said:
                print("- refusal contract: %s" % said)
            if tag_line(res):
                print(tag_line(res))
        else:
            print_refusal(res)
            if res.get("tag_taken"):
                print("- the tag %s already exists, so this pass cannot be tagged; nothing was written"
                      % res["tag_taken"])
            if said:
                print("- refusal contract: %s" % said)
        if res["ok"] and res.get("untagged"):
            return 5        # passed, but not tagged: never the plain success code
        # a refusal nobody could count is not a refusal counted zero times: its own exit code, above the plain
        # refusal's 1, so a caller in a loop cannot read "not counted yet" as "counted and under the limit"
        if res.get("submit_error") and not res["ok"]:
            return 4
        return 0 if res["ok"] else 1
    if o.cmd == "walk-result":
        sp = lambda v: [x.strip() for x in (v or "").split(",") if x.strip()]    # noqa: E731
        res = walk_result(root, o.mod, o.to, o.by, o.why, owner=o.owner_said,
                          conductor=o.conductor_decision or (("per-ruling %s: %s" % (o.per_ruling, o.why)) if o.per_ruling else None),
                          item=o.item, fix=sp(o.fix), pick=sp(o.pick), scene=sp(o.scene), next_version=sp(o.next),
                          groups=[[x.strip() for x in g.split("+") if x.strip()] for g in o.group],
                          passes=o.passes, walked=o.walked)
        if res.get("ok"):
            print("WALK RECORDED %s: not passed; %s written; %s to %s" % (o.mod, res["path"], label("his_walk"),
                                                                       label(o.to)))
            return 0
        print("REFUSED: %s" % res.get("why"))
        return 1
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
    if o.cmd == "red-seen":
        r = JC.red_seen(root, o.mod, o.test, patch=o.patch)
        print(("RED SEEN %s %s: %s" % (o.mod, o.test, r["why"])) if r["ok"] else "NOT RECORDED %s %s: %s" % (
            o.mod, o.test, r["why"]))
        return 0 if r["ok"] else 2 if str(r["why"]).startswith("did not run") else 1
    if o.cmd == "certificate":
        ran = None
        g = JC.grandfather(root, o.mod) if o.grandfather else None
        if g is not None and not o.json:
            print("GRANDFATHER %s: %s" % (o.mod, g["why"]))
        if o.run:
            t0 = time.time()
            # only the tests whose reads or file changed (or that are red or unstamped) run; --all is a named full pass
            ran = JC.run_offline(root, o.mod, resume=not o.all)
            if o.all:
                ran["full_pass_why"] = o.all
                print("FULL PASS (named act): %s" % o.all)
            ran["wall_s"] = round(time.time() - t0, 1)
        cv = certificate(root, o.mod, o.to)
        if o.json:
            if ran is not None:
                rows, none, unread = JC.margin_rows(JC.read_table(root, o.mod)[0] or {})
                ran["margins"] = {"thinnest_first": rows, "not_printed": none, "unmeasured": unread}
            print(json.dumps(dict(cv, run=ran, **({"grandfather": g} if g is not None else {})), indent=2,
                             ensure_ascii=False))
        else:
            if ran is not None:
                print("RAN %s: %d offline tests in %.1f s%s%s" % (o.mod, ran["ran"], ran["wall_s"], (
                    "; kept %d already green on this build" % ran["skipped"]) if ran.get("skipped") else "", (
                    "; failed: %s" % ", ".join(ran["failed"])) if ran["failed"] else "") + (
                    "; %s" % ran["error"] if ran.get("error") else ""))
            JC.print_certificate(cv)
            if ran is not None:     # tuning tripwire T2: the thinnest margins first; the verdict above is unchanged
                tt, _ = JC.read_table(root, o.mod)
                rows, none, unread = JC.margin_rows(tt or {})
                print("MARGINS %s (thinnest first; |worst - limit| / |limit|):" % o.mod)
                for r in rows:
                    print("  %s: worst %s against limit %s over %d cases%s" % (
                        r["test"], r["worst"], r["limit"], r["cases"], (" (%s)" % r["name"]) if r.get("name") else ""))
                for t in none:
                    print("  %s: margin not printed" % t)
                for t in unread:
                    print("  %s: margin UNMEASURED (its run did not finish, or was kept from before margins were read)"
                          % t)
                if not (rows or none or unread):
                    print("  no offline test ran")
        return 0 if cv["ok"] else 1
    if o.cmd == "lock-bars":
        r = lock_bars(root, o.mod, o.by, o.why, o.add, o.remove, o.source)
        print(("LOCKED BARS %s: %d recorded in %s (%s)" % (o.mod, len(r["ids"]), rel(o.mod, LOCKED_BARS), r["why"]))
              if r["ok"] else "REFUSED: %s" % r["why"])
        return 0 if r["ok"] else 2
    if o.cmd == "next-version":
        r = next_version(root, o.mod, o.by, o.why)
        print(("NEXT VERSION %s: %s -> %s, at %s (old record kept as %s%s)" % (
            o.mod, r["from"], r["to"], label(r["stage"]), r["kept"], "; evidence set aside in %s, land it and the old paths: %s" % (
                r["aside"], ", ".join(r["archived"])) if r["archived"] else "")) if r["ok"] else "REFUSED: %s" % r["why"])
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
    if o.cmd == "game-repair":
        res = game_repair(root, o.mod, o.game, o.kind, o.purpose, seat=o.seat)
        print(json.dumps(res))
        return {"ok": 0, "wait": 75}.get(res["state"], 1)
    if o.cmd == "launch":
        rc, text, _ = launch_mod(root, o.mod, o.budget_usd, o.item, model=o.model, seat=o.seat)
        print(text)
        return rc
    return 2


if __name__ == "__main__":
    sys.exit(main())
