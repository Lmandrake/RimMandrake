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
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import maturation_now as MN     # noqa: E402  the journal readers: one parser, never a second one
import refusal_contract as RC   # noqa: E402

UNM = "UNMEASURED"
RECORD = "version/stage_record.json"
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
    "in_game": ("offline_build", "blind_challenge"),
    "pre_human": ("preflight", "offline_build", "blind_challenge", "in_game"),
    "his_walk": ("offline_build", "blind_challenge", "in_game"),
}
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

def _table_runnable(tt):
    bars = tt.get("bars") if isinstance(tt, dict) else None
    if not isinstance(bars, list) or not bars:
        return None, "the table has no bars list"
    flags = [b.get("every_decider_runnable_today") for b in bars if isinstance(b, dict)]
    if len(flags) != len(bars) or not all(isinstance(f, bool) for f in flags):
        return None, "a bar lacks a true/false every_decider_runnable_today"
    return [b.get("id", "?") for b in bars if b.get("every_decider_runnable_today") is not True], len(bars)


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


def _reached(root, stage):
    """Mods (other than none) whose record has ever stood at `stage`."""
    out = []
    croot = os.path.join(root, "design", "concepts")
    for f in sorted(os.listdir(croot)) if os.path.isdir(croot) else []:
        r = load(root, f)
        if r and (r.get("stage") == stage or any(mv.get("to") == stage for mv in r.get("moves") or [])):
            out.append(f)
    return out


def evaluate(root, mod, to, steward=None, conductor=None, owner=None, by=None, why=None):
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
    nxt = WORDS[i_cur + 1] if 0 <= i_cur < len(WORDS) - 1 else None
    clause("order", "a mod moves forward one stage at a time, or back only along a road the spec draws",
           forward or back, [req_ref, rec_ref],
           observed="asked %s to %s; the record stands at %s" % (cur, to, cur),
           would_pass="advance --to %s (the next stage)%s" % (nxt or "nothing", (" or back to " + ", ".join(
               ROADS_BACK[cur])) if cur in ROADS_BACK else ""),
           fix="run advance with --to %s, finishing %s first" % (nxt or cur, label(cur)),
           why_sound="the eight stages, their order and the roads back are his and carried rulings (spec §3)")
    # version: the record is for the Design Version VERSION.json names
    v, verr = read_json(root, mod, "version/VERSION.json")
    vv = (v or {}).get("version", UNM)
    clause("version", "the stage record is for the Design Version that version/VERSION.json names",
           v is not None and vv == rec.get("version"), [rec_ref, rel(mod, "version/VERSION.json")],
           observed="the record says version %s; VERSION.json says %s" % (rec.get("version"), vv if v else verr),
           would_pass="a stage_record.json whose version field equals VERSION.json's version %s" % vv,
           fix="open the new version by hand (a hand step: the spec's 'open the next version' is decided with him) "
               "and seed a fresh stage record for it", cost="owner")
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
            if walked:
                hand.append("owner_said")
                clause("owner_said", "how the waiting mods enter after the first walk is asked of him again",
                       bool(owner), [req_ref], observed="owner_said: none in the request",
                       would_pass="--owner-said quoting his answer on how waiting mods enter",
                       fix="ask him by card how the waiting mods enter, then pass his words", cost="owner",
                       why_sound="his card of 2026-11-14 says it is asked again at that point")
        elif cur == "designer":
            st = str((v or {}).get("state") or "")
            clause("locked", "the Design Version is locked on his word (VERSION.json state locked)",
                   st.startswith("locked"), [rel(mod, "version/VERSION.json")],
                   observed="VERSION.json state is %s" % (st or UNM),
                   would_pass="VERSION.json state reads locked, with his lock words in owner_words",
                   fix="finish the Designer pass and bring him the lock question", cost="owner",
                   why_sound="a Design Version is locked on his word (Design Versions ruling, carried)")
        elif cur == "preflight":
            pf, perr = read_json(root, mod, "version/preflight.json")
            pref = rel(mod, "version/preflight.json")
            clause("preflight_record", "a preflight record exists for this Design Version",
                   pf is not None and str(pf.get("version")) == str(rec.get("version")), [req_ref],
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
            res = _table_runnable(tt) if tt is not None else (None, terr)
            bad, n = res
            walk = _walk_deciders(tt, bad) if isinstance(bad, list) else []
            if isinstance(bad, list):
                bad = [x for x in bad if x not in walk]
            clause("every_bar_has_a_check_that_runs", "every bar has every deciding check runnable "
                   "(an in-game scene may be UNRUN with its command)", isinstance(bad, list) and not bad,
                   [tref], observed=("%d of %d bars not runnable: %s" % (len(bad), n, ", ".join(bad)))
                   if isinstance(bad, list) else "test_table.json: %s" % n,
                   would_pass="a test table whose every bar reads every_decider_runnable_today true",
                   fix="build the missing checks or scene entries for the listed bars, then remake the test table",
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
            clause("owner_said", "the version passes on his words alone", bool(owner), [req_ref],
                   observed="owner_said: none in the request", would_pass="--owner-said quoting his pass of the version",
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
    sha = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True,
                         timeout=60).stdout.strip()
    verdict = {"item": "%s@%s" % (mod, rec.get("version")), "family": "maturation_advance:%s->%s" % (cur, to),
               "sha": sha or UNM, "given": {"criteria": crit, "inputs": inputs}, "passed": passed,
               "refusals": refusals}
    return {"ok": not refusals, "verdict": verdict, "hand_steps": hand, "from": cur, "to": to}


# ---- the move --------------------------------------------------------------------------------------------------------

def advance(root, mod, to, by, why, steward=None, conductor=None, owner=None, waits_on=None):
    res = evaluate(root, mod, to, steward=steward, conductor=conductor, owner=owner, by=by, why=why)
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
    if to == "blind_challenge":
        c = rec.setdefault("cycles", {"visit": 0, "total": 0})
        c["visit"] = c["visit"] + 1 if cur == "blind_challenge" else 1
        c["total"] += 1
    if to == "pre_human":
        rec["pre_human_arrivals"] = rec.get("pre_human_arrivals", 0) + 1
    move = {"from": cur, "to": to, "at": iso(t), "by": by, "why": why,
            "confirmed": {k: v for k, v in (("steward_confirms", steward), ("conductor_decision", conductor),
                                            ("owner_said", owner)) if v},
            "checks_passed": [p["clause"] for p in res["verdict"]["passed"]]}
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
        write_text(root, mod, "journal.md", jtext)
    write_text(root, mod, RECORD, dump(rec))
    return res


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
    bad, n = _table_runnable(tt) if tt is not None else (None, None)
    walk = _walk_deciders(tt, bad) if isinstance(bad, list) else []
    out.update({
        "refused_bars": [b for b in bad if b not in walk] if isinstance(bad, list) else UNM,
        "bars_total": n if isinstance(n, int) else UNM, "walk_bars": walk,
        "build_refusals": [r["clause"] for r in refs if r["clause"] in BUILD_CLAUSES],
        "hand_steps": [r["clause"] for r in refs if r["clause"] in res["hand_steps"]],
        "other_refusals": [r["clause"] for r in refs if r["clause"] not in BUILD_CLAUSES
                           and r["clause"] not in res["hand_steps"]],
        "observed": {r["clause"]: r["observed"] for r in refs}})
    out["owed"] = ("blocked" if out["other_refusals"] else "build" if out["build_refusals"] else
                   "hand step" if out["hand_steps"] else "ready to advance")
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


def brief_text(root, mod, cap_usd=None):
    """-> (the mechanical half of an offline-build brief, build_facts). Never refuses for a blank steward section.
    A mod at the blind challenge gets blind_brief_text instead, one at in-game acceptance ingame_brief_text."""
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
          "- Never guess a defName, field or namespace (RimSage, the def, or `measure`)."]
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


def launch_mod(root, mod, budget_usd, item, model="opus", seat="BENCH", runner=subprocess.run, bridge=None):
    """-> (exit code, text, unit or None). Refuses (2) a missing or non-positive cap, a missing item, a mod at neither
    the offline build nor the blind challenge, one with no build work owed, and at the blind challenge a model below
    opus or a cycle already recorded or blocked, and at in-game acceptance a model other than opus, a visit already
    recorded or blocked, or a bridge `rimflow bridge idle` does not call takeable (bridge: a stand-in for bridge_idle);
    otherwise writes the brief and calls detached_helper.py launch --budget-usd <cap>. It launches nothing else and
    never retries; it never takes the bridge itself (the launched driver does, with --idle-ok)."""
    if not isinstance(budget_usd, (int, float)) or isinstance(budget_usd, bool) or budget_usd <= 0:
        return 2, "REFUSED: a spend cap is required (--budget-usd > 0); there is no default", None
    if not item:
        return 2, "REFUSED: --item is required (a ledger item filed on origin/main)", None
    text, f = brief_text(root, mod, budget_usd)
    if f.get("stage") == "blind_challenge":
        if model not in JUDGE_MODELS:
            return 2, "REFUSED: a blind judge is a judging role; %s is below the floor (opus or fable)" % model, None
        if f.get("owed") != "cycle":
            return 2, "REFUSED: %s owes no blind cycle: cycle %s is %s (%s)" % (
                mod, f.get("cycle"), "recorded" if f.get("owed") != "blocked" else "blocked",
                "; ".join(f.get("blocked") or (f.get("exit") or {}).get("why") or [f.get("owed", UNM)])), None
    elif f.get("stage") == "in_game":
        if model not in LIVE_MODELS:
            return 2, "REFUSED: a live driver runs on %s (Agent_Policy.md, rm-bridge); not %s" % (
                " or ".join(LIVE_MODELS), model), None
        if f.get("owed") != "run":
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
    path = os.path.join(brief_dir(), "%s-%d.md" % (mod, int(now_ts())))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    argv = [sys.executable, detached_helper_path(), "launch", "--seat", seat, "--item", item, "--brief-file", path,
            "--model", model, "--budget-usd", "%g" % budget_usd]
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
    if not bars:
        why.append("the test table names no offline bar (proves_at 2 or 4-5)")
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
            reruns[t] = str(r.get("result", "")).upper()
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
            else:
                held = sorted({m for c in _cmds(fx) for m in PLACEHOLDER.findall(c)})
                if held:
                    why.append("FIXED Problem %s: its fixes.jsonl command holds the placeholder %s, not a rerunnable "
                               "record: name the path and run it at both shas" % (x.get("id"), ", ".join(held)))
    l1 = _jsonl(os.path.join(d, "lane1", "lane1_rows.jsonl"))
    if l1 is None:
        why.append("lane1/lane1_rows.jsonl is missing")
    fails = [r.get("id", "?") for r in l1 or [] if str(r.get("verdict", "")).upper() == "FAIL" or "_bad" in r]
    if fails:
        # lane 1 is recorded blind, before the fixes, and stays as recorded: a FAIL there is how a Problem is found. It
        # clears only when lane 1 rerun after the fixes (LANE1_AFTER_FIX) has no FAIL and shows each of those rows PASS.
        after = _jsonl(os.path.join(d, LANE1_AFTER_FIX))
        bad_after = [r.get("id", "?") for r in after or [] if str(r.get("verdict", "")).upper() == "FAIL" or "_bad" in r]
        passed = {r.get("id") for r in after or [] if str(r.get("verdict", "")).upper() == "PASS"}
        # a FAIL a Polish fault owns is not passing's; a row that PASSes after the fixes is cleared, not left as Polish
        polish = _polish_rows(faults, sorted((set(fails) - passed) | set(bad_after)))
        out["checks"]["lane1_fail_left_as_polish"] = polish
        bad_after = [f for f in bad_after if f not in polish]
        left = [f for f in fails if f not in passed and f not in polish]
        out["checks"]["lane1_fail_cleared_after_fix"] = after is not None and not bad_after and not left
        if after is None:
            why.append("lane 1 has %d FAIL or unreadable row(s): %s, and no %s shows them PASS after the fixes"
                       % (len(fails), ", ".join(fails[:8]), LANE1_AFTER_FIX))
        elif bad_after or left:
            why.append("lane 1 has %d FAIL or unreadable row(s): %s; after the fixes %s still fails %s%s" % (
                len(fails), ", ".join(fails[:8]), LANE1_AFTER_FIX, ", ".join(bad_after[:8]) or "nothing",
                (" and does not show PASS for %s" % ", ".join(left[:8])) if left else ""))
    if not os.path.exists(os.path.join(d, "tests_edited.json")):
        why.append("tests_edited.json is missing (an empty list is written, never left out)")
    pr = _jsonl(os.path.join(d, "lane2", "planted_results.jsonl"))
    if not pr or pr[-1].get("tree_clean_after") is not True:
        why.append("lane2/planted_results.jsonl %s" % ("is missing" if pr is None else
                                                       "does not end with tree_clean_after true"))
    out["state"] = "not_met" if why else "met"
    if not why:
        pol = out["checks"].get("lane1_fail_left_as_polish") or {}
        why.append("the block says exit_met true and every file check agrees (%d offline bars, %d deciders rerun PASS)%s"
                   % (len(bars), sum(len(x[1]) for x in bars), "; lane-1 FAIL left as Polish, not part of passing (the "
                      "steward confirms the move): %s" % ", ".join("%s (%s)" % kv for kv in sorted(pol.items()))
                      if pol else ""))
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
    cap = ("$%g" % cap_usd) if cap_usd else "the --budget-usd the launch carries"
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
         "**Spend bound: %s.** The pilot's cycle 1 cost about $9 [measured, FORMAT_NOTES]. If you cannot see your spend, "
         "stop at 3 hours of wall time. At the bound, record where you are, commit, publish, and report what is owed."
         % cap, "",
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
                 "row; do not stretch a kernel to cover it." % (nk, (": " + ", ".join("`%s`" % x for x in ks) +
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
          "NOTED_FOR_CONDUCTOR. A Problem FIXED red-first is closed." % (
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
          "## Report (10 lines or fewer, plain words)", "",
          "Tag every number [measured] or [guess ~N%%]: lane 1 rows passing of total and how many UNSETTLED; lane 2 "
          "reruns matching of rerun; planted faults caught of planted; the Problem and Polish counts%s; shas; the tests "
          "you edited; what you could not settle; whether the exit is met; spend." % (
              " and how many are `miss_of`" if n >= 2 else "")]

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
    last = {}
    for r in rows or []:
        t = r.get("test") or r.get("id")
        if t:
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
        if r.get("site_checked") is not True:
            why.append("in-game check %s: its row does not say the site was checked first (site_checked)" % t)
        if str(r.get("game", "")).lower() not in GAMES:
            why.append("in-game check %s: its row names no game (%s)" % (t, " or ".join(GAMES)))
        if not r.get("mod_sha"):
            why.append("in-game check %s: its row names no mod_sha (the build it ran)" % t)
    st = _jsonl(os.path.join(d, "strange.jsonl"))
    if st is None:
        why.append("strange.jsonl is missing (an empty file says nothing strange was seen)")
    left = [x.get("what", x.get("_bad", "?")) for x in st or []
            if not (str(x.get("explained") or "").strip() or str(x.get("filed") or "").strip())]
    out["strange_open"] = len(left)
    if left:
        why.append("%d strange thing(s) neither explained nor filed: %s" % (len(left), "; ".join(str(x)[:60]
                                                                                             for x in left[:3])))
    if st is not None and blk["strange_open"] != len(left):
        why.append("the block says strange_open %d; strange.jsonl leaves %d" % (blk["strange_open"], len(left)))
    sv = blk["savegame"]
    if not os.path.isfile(native_to_here(sv)):
        why.append("the savegame %s is not on disk" % sv)
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


def ledger_items_caused_by(root, ids):
    """-> [{id, title}] for the ledger items filed (file or spawn) with caused_by one of ids and not closed, dropped or
    superseded since, read from every shard under infrastructure/state/ledger/events/."""
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
    return [{"id": k, "title": v} for k, v in sorted(filed.items()) if k not in ended]


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
    cap = ("$%g" % cap_usd) if cap_usd else "the --budget-usd the launch carries"
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
         "**Spend bound: %s.** If you cannot see your spend, stop at 3 hours of wall time. At the bound, record where "
         "you are, release the bridge, commit, publish, and report what is owed." % cap, "",
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
    a.add_argument("--json", action="store_true")
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
            print("  spend %s: %s tokens, USD %s, %s s wall, %d entries (%d estimates, %d unmeasured fields)"
                  % (" + ".join(label(x) for x in st.split("+")), t["tokens"], t["usd"] if t["usd"] == UNM else
                     "%.2f" % t["usd"], round(t["wall_s"]), t["entries"], t["estimates"], t["unmeasured"]))
        return 0
    if o.cmd == "next":
        nx = next_step(root, o.mod)
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
        print(nx["next"])
        return 0
    if o.cmd == "advance":
        if load(root, o.mod) is None:
            print("REFUSED: %s has no stage record; run maturation.py seed %s first" % (o.mod, o.mod))
            return 1
        res = advance(root, o.mod, o.to, by=o.by, why=o.why, steward=o.steward_confirms,
                      conductor=o.conductor_decision, owner=o.owner_said or (("per-ruling %s: %s" % (o.per_ruling, o.why)) if o.per_ruling else None), waits_on=o.waits_on)
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
