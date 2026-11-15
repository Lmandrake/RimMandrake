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

What is settled and tested here, and what stays a hand step (the open question named), is the plan's section 3 table.
This program launches nothing: no timer, no helper. A later slice launches only through detached_helper.py with
--budget-usd. Holds are read from the journal only; a hold written only in a ledger note is not seen (slice 2).
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
        return t.isoformat(timespec="seconds"), "the earliest journal heading naming it: %s" % h[:120]
    i = WORDS.index(WORD_OF_COL[col]) if col in WORD_OF_COL else 0
    if i > 0:
        prev = COL[WORDS[i - 1]]
        named = [(t, h) for t, h in hist if prev in MN.stages_named(h)]
        if named:
            t, h = max(named, key=lambda x: x[0])
            return t.isoformat(timespec="seconds"), "the end of the stage before it, journal heading: %s" % h[:120]
    return UNM, "no dated journal heading names it"


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
            usd = r.get("usd") if isinstance(r.get("usd"), (int, float)) else r.get("said_usd")
            out.append({"stage": stages[0], "stages": stages, "tokens": r.get("tokens") if isinstance(
                r.get("tokens"), int) else UNM, "usd": usd if isinstance(usd, (int, float)) else UNM,
                "usd_from": "run record" if isinstance(r.get("usd"), (int, float)) else
                ("the run's own words" if isinstance(r.get("said_usd"), (int, float)) else UNM),
                "wall_s": round(r["wall_s"]) if isinstance(r.get("wall_s"), (int, float)) else UNM,
                "cap_usd": r.get("cap") if isinstance(r.get("cap"), (int, float)) else UNM,
                "source": "detached run %s (item %s)" % (u, r.get("item")), "kind": "measured"})
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
            clause("intake_closed", "no mod enters the Designer until one of the advancing mods has reached his walk",
                   bool(walked), [req_ref], observed="no stage record has reached his_walk; this request is for %s" % mod,
                   would_pass="one of Explosive Knockback, FlowWorks, Gimme Some Slack or Pyrelands has a record "
                              "that reached his_walk", fix="wait: advance one of the four mods to his walk first",
                   attainable="yes", cost="rerun", why_sound="his card of 2026-11-14: wait for one full pass")
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
            what = {"blind_challenge": "the blind judge's verdict (no verdict format exists; the exit is a proposal)",
                    "in_game": "the in-game rows (no common row format exists across mods)",
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
        return {"mod": mod, "stage": UNM, "next": "NEXT: seed its record: maturation.py seed %s" % mod, "refusals": []}
    cur = rec["stage"]
    if cur == "passed":
        return {"mod": mod, "stage": cur, "refusals": [], "hand_steps": [],
                "next": "NEXT (hand step): decide with him whether to open the next version (spec §3.8, a portfolio "
                        "decision); nothing here opens one"}
    to = WORDS[WORDS.index(cur) + 1]
    res = evaluate(root, mod, to, by="next", why="what is the next step")
    prog = [r for r in res["verdict"]["refusals"] if r["clause"] not in res["hand_steps"]]
    hand = [r for r in res["verdict"]["refusals"] if r["clause"] in res["hand_steps"]]
    if prog:
        nxt = "NEXT: %s; then maturation.py advance %s --to %s (%s refuses it now: %s)" % (
            prog[0]["smallest_fix"]["what"], mod, to, prog[0]["clause"], prog[0]["observed"][:300])
    elif hand:
        flag = {"steward_confirms": "--steward-confirms", "walk_bars_confirmed": "--steward-confirms",
                "owner_said": "--owner-said",
                "conductor_decision": "--conductor-decision"}
        nxt = "NEXT (hand step): %s; then maturation.py advance %s --to %s --by <SEAT> --why \"...\" %s \"...\"" % (
            hand[0]["smallest_fix"]["what"], mod, to, flag.get(hand[0]["clause"], ""))
    else:
        nxt = "NEXT: maturation.py advance %s --to %s --by <SEAT> --why \"...\" (every exit test passes)" % (mod, to)
    return {"mod": mod, "version": rec.get("version"), "stage": cur, "stage_label": label(cur),
            "since": rec.get("since"), "to": to, "passed": [p["clause"] for p in res["verdict"]["passed"]],
            "refusals": [{k: r[k] for k in ("clause", "observed", "would_pass", "smallest_fix")} for r in prog + hand],
            "hand_steps": res["hand_steps"], "cycles": rec.get("cycles"), "spend": spend_by_stage(rec),
            "launch": "none: this slice launches nothing (a later slice launches only via detached_helper.py "
                      "--budget-usd)", "next": nxt}


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
        for st, t in spend_by_stage(rec).items():
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
            print("  refused %s: %s" % (r["clause"], r["observed"][:400]))
        print("  launch: %s" % nx.get("launch", "none"))
        print(nx["next"])
        return 0
    if o.cmd == "advance":
        if load(root, o.mod) is None:
            print("REFUSED: %s has no stage record; run maturation.py seed %s first" % (o.mod, o.mod))
            return 1
        res = advance(root, o.mod, o.to, by=o.by, why=o.why, steward=o.steward_confirms,
                      conductor=o.conductor_decision, owner=o.owner_said, waits_on=o.waits_on)
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
    return 2


if __name__ == "__main__":
    sys.exit(main())
