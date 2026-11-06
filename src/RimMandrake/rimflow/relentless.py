#!/usr/bin/env python3
"""relentless: the Relentless Pipeline. The item is the owner, workers are replaceable. RELENTLESS_OWNER_DESIGN_NEVER_LETS_GO.

Naming (owner, 2026-11-03, PIPELINE_RENAME_WORKERS_NOW_SWAPPABLE): this program is the Relentless Pipeline; each worker in
its places is a Relentless-style Builder/Judge from MandrakeWorkflows (relentless/workers/BUILDER_JUDGE.md), run as the
agents named by worker_agent and checker_agent in relentless_rules.json. Swapping workers leaves the pipeline's design.

Design: design/RimMandrake/relentless_owner_design_2026-10-31.md. Limits: relentless_rules.json (data). A program, no AI.
`tick` runs from rm-relentless.timer, out of the supervisor's own clone (<root>/books), which it fast-forwards itself,
so a push to main deploys it and nothing here depends on the FOUNDRY tree.

Threat model: a worker is honest but may be STALE (a process that outlived its lease, or a resumed session). Fencing
stops such a process from completing, reporting or pushing by accident. It is not a sandbox against a hostile agent.

Exit codes for worker verbs: 0 done, 2 usage or refused, 3 FENCED (your lease is gone: stop now).
"""
import argparse
import calendar
import contextlib
import copy
import fcntl
import filecmp
import glob
import hashlib
import importlib
import json
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import circling  # noqa: E402
import conductor_log_guard  # noqa: E402
import relentless_account  # noqa: E402
import relentless_books_left  # noqa: E402
import relentless_disk  # noqa: E402
import relentless_integrity  # noqa: E402
import relentless_packet  # noqa: E402
import relentless_usage  # noqa: E402
import relentless_tickprof  # noqa: E402
import relentless_wall  # noqa: E402
import relentless_reach  # noqa: E402
import relentless_reachfix  # noqa: E402
import relentless_game  # noqa: E402
import relentless_expedite  # noqa: E402
import relentless_repair_slot  # noqa: E402
import relentless_binding  # noqa: E402
import relentless_block  # noqa: E402
import relentless_boxrun  # noqa: E402
import relentless_dispute  # noqa: E402
import relentless_breakers  # noqa: E402
import relentless_incident  # noqa: E402
import relentless_strikes  # noqa: E402
import relentless_answer  # noqa: E402
import relentless_attrib  # noqa: E402
import relentless_explain  # noqa: E402
import relentless_live  # noqa: E402
import relentless_showing  # noqa: E402
import run_tmp  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.join(HERE, "relentless_rules.json")
ALARM_PREFIXES = ("OPS_", "LIVE_RESTORE_")       # rimflow close refuses these without a live line (cli._live_gate)
DEFAULT_ROOT = "/home/mandrake/rm/relentless"
# the seats' auto-memory index: a worker's clone is a new project path, so Claude Code never loads it (0 of 263 measured
# 2026-11-02); the brief points at it instead (TRANSFER_AUDIT, BENCH)
MEMORY_INDEX = os.path.expanduser("~/.claude/projects/-home-mandrake-rm-bench/memory/MEMORY.md")
FENCED = 3
LEASED = ("running", "stopping", "candidate", "checking", "closing", "retiring", relentless_game.GAME)   # a worker or the supervisor owns the item
OPEN = ("queued",) + LEASED + ("held",)
MAX_WAIT_HOURS = 6     # a worker's word cannot park an item for longer
HOLDS_A_PLACE = ("running", "checking", "candidate", "stopping", "retiring")    # a run that may be live counts
# What a run is live in. A candidate waits on its judge, a resource like any other: it is put down and holds no worker
# place (owner 2026-11-02, RELENTLESS_SLOTS_UNSTICK_BLOCKED_PUT_DOWN: "put down blocked items once they become blocked
# and go do something else"). Its check takes a place when it starts; its mods stay held, its FAIL comes back to them.
RUNS_A_PLACE = ("running", "checking", "stopping", "retiring")
# Parked the moment they wait: their clone goes back at once, its WIP in the bundle (release_parked)
PUT_DOWN = ("held", "blocked", relentless_game.GAME)
SUPERVISOR_WHY = "relentless supervisor"    # ledger_needs' provenance; ledger_hold_to_seat reads it back
SEAT_QUEUE = "seat"     # a tooling hold's reader: the Conductor, by owner_queue.py --seat; never needs=owner
ENDED = ("done", "retired")
SHARD = "infrastructure/state/ledger/events/%s.jsonl"
BRIDGE_HOLDER = "RELENTLESS"    # model.RELENTLESS_HOLDER: items are the seat's, a bridge hold is Relentless's own
NOTE_MAX = 400
NOT_READ = object()
ALLOCATION_FRESH_S = 1800
SLUG_RX = re.compile(r"[^a-z0-9_]+")
POOL_REFUSED = "POOL REFUSED"        # scratch_clone's word: the pool said no, the launch path is healthy
CAUSE_TOKEN = re.compile(r"\S*[\d/_]\S*")   # a run name, a path, a number, an item id: what changes between tries of one fault
POOL_FULL = ("pool full", "pool at")  # make_room's holds: what the staffing reading looks for in the tick's acts
# dirt no worker made on purpose: session dumps and ledger shards the seats' projection rewrites. Bundled, never restored
POOL_STATE = ("infrastructure/state/lessons/",)     # records a worker commits as it finishes; the bundle carries them, a fresh clone re-applies them
POOL_NOISE = ("conversations/", "infrastructure/state/ledger/events/", "infrastructure/state/code_review/")
POOL_ORPHAN_IDLE_S = 3600
# What a usable clone must hold: every launch runs claude_bounded.sh from it. A clone released for room while its item
# waited, or a checkout cut short, failed BLUEDESERT_FLORA_PLANT_REFUSAL_1's stage with "missing claude_bounded.sh".
CLONE_PROBE = (".git", "src/RimMandrake/Utils/claude_bounded.sh")


def clone_gap(c):
    """-> the first path a usable clone holds that `c` lacks, or None when it is whole."""
    return next((p for p in CLONE_PROBE if not os.path.exists(os.path.join(c, p))), None)
POOL_IGNORED_MAX = 2 * 10**9
# RELENTLESS_BUNDLES_FIX_FOURTEEN_GIG_PATCHES: a bundle holds a worker's WIP, never a tree. Over these it raises (the clone
# is kept and alarmed, bundle_failed) instead of writing 14 GB, as three bundles did on 2026-11-04/05.
BUNDLE_PATCH_MAX = 500 * 10**6
BUNDLE_MAX = POOL_IGNORED_MAX + 2 * BUNDLE_PATCH_MAX


def restore_deleted(bundle, c):
    """A bundle's `deleted` paths go from the fresh clone `c`, each only while upstream still holds the very blob the worker
    removed (and the file is that blob). -> what was not removed, named."""
    path = os.path.join(bundle, "deleted")
    if not os.path.exists(path):
        return []

    def out(*a):
        return subprocess.run(["git", "-C", c, *a], capture_output=True, text=True, timeout=120,
                              stdin=subprocess.DEVNULL).stdout.strip()
    with open(os.path.join(bundle, "HEAD"), encoding="utf-8") as f:
        head = f.read().strip()
    with open(path, encoding="utf-8") as f:
        names = [x for x in f.read().split("\0") if x]
    bad = []
    for p in names:
        if not os.path.lexists(os.path.join(c, p)):
            continue
        was, now = (out("rev-parse", "--verify", "-q", "%s:%s" % (rev, p)) for rev in (head, "HEAD"))
        if was and was == now and out("hash-object", "--", p) == now:
            os.unlink(os.path.join(c, p))
        else:
            bad.append("deleted %s kept: upstream changed it since" % p)
    return bad


def bundle_bytes(d):
    """-> bytes under d, each inode once (real.patch is a hard link to diff.patch)."""
    seen, n = set(), 0
    for dp, _dirs, files in os.walk(d):
        for x in files:
            st = os.lstat(os.path.join(dp, x))
            if (st.st_dev, st.st_ino) not in seen:
                seen.add((st.st_dev, st.st_ino))
                n += st.st_size
    return n
LEDGER_DIR = "infrastructure/state/ledger/events/"
ITEMS_DIR = "infrastructure/state/items/"
BOOKS_DERIVED = (LEDGER_DIR, ITEMS_DIR)
# append-only shards outside the ledger whose writers (code_review_status, artledger) hold the directory flock SHARED per
# append: level_books holds it EXCLUSIVE while it restores and git replaces them, as model.append does for the ledger
APPEND_ONLY_DIRS = ("infrastructure/state/code_review/", "infrastructure/state/art/events/")
# a live site build run from the books clone rewrites its registry there; the save is on disk, the file is a run artefact
BOOKS_RUN_ARTEFACTS = ("src/RimMandrake/Utils/modcheck/test_site_saves.json",)
# a proof run from the books clone also writes these. Not in the way: they stay as they are. 32 of 70 ticks on 2026-11-03
# would not level on them, so the engine ran old code (TICK_SPEED_FIX_GAME_IDLES_WAITING). One origin moved is set aside
# for the reset and handed back (the registry merged by key, the rest kept in books_dirt): relentless_books_left.py
# validation_v2 run from the books clone writes its triplet report beside the northstar (OPS_JAM_CLASS_FIX_AGAIN_HJWN)
BOOKS_LEFT_IN_PLACE = ("Transient/", "infrastructure/state/modcheck_status.json",
                       "src/RimMandrake/GimmeSomeSlack/northstar/validation_triplet_")
GUARDED_VERBS = ("close", "implemented", "renew", "release", "reclaim", "claim", "start")
PROOF_ENDS = ("proof_weak", "proof_rework", "proof_unchanged", relentless_attrib.PROOF_OWED)     # one road: strengthen the proof, never redesign the code
PROOF_DEFECT = "proof_found_defect"     # a worker's stronger proof went red on the held code: back to ordinary work
REJECT_ENDS = ("blind_fail", "proof_weak")
SUPERVISOR_ENDS = PROOF_ENDS + ("blind_fail",)     # set by a checker verdict only; a worker's snag with one is refused
NOT_AN_APPROACH = ("worker_lost", "checker_lost")
# LIVE_WORKERS_DIAGNOSE_BEFORE_THEY_REBUILD (owner 2026-11-04: "Why aren't the agents that encounter difficulties in the live
# game check recognizing what's going wrong?"): an ending read off a live proof or a checker is a reading the supervisor took
# from an exit code and a regex. No agent had read its log before the next worker was told the mod FAILED and to work it, so
# generations changed code against a broken site or instrument (live churn triage 2026-11-04: of 30 game_fail items, 5
# HARNESS and 6 SITE). After one of these the next worker owes a written explanation (`explain`, relentless_explain:
# expected, observed, mechanism, evidence per step, theories ruled out, one open follow-up item per cause) before
# `finish` is taken; a CLASSIFY line is recorded as a label only (LIVE_FAILURES_EXPLAIN_MORE_THAN_A_LABEL).
DIAGNOSE_ENDS = ("game_fail", "game_unmeasured", "game_proof_unmeasured", "checker_lost", "unmeasured")
# TEST_PILOT_WIRE_INTO_THE_PIPELINE_EARLY (owner 2026-11-04: "We may need Test Pilots to be able to be called in the
# Pipeline too, not just Relentless. Though I'd want to know what Test Pilot did that we might teach Relentless' live
# testing mode."): a REPEATED live failure is a pipeline step of its own. Before, a pilot sat only as a late rung of the
# approach ladder (after a redesign); now rules.pilot_after_live_fails live endings since the last sitting make the next
# worker an rm-testpilot sitting (st["pilot_step"]), whatever the approach. The sitting explains (relentless_explain), and
# what pilots do that a builder does not is taught to every live worker in LIVE_MOVES.
LIVE_ENDS = ("game_fail", "game_unmeasured", "game_proof_unmeasured")
# the moves the 2026-11-04 LEANINGSCRUB pilot sitting reported under "What Relentless's live mode should learn" (ledger
# note on TEST_PILOT_WIRE_INTO_THE_PIPELINE_EARLY, 2026-11-04T13:14Z): every brief that touches the running game carries them
LIVE_MOVES = (
    "read the proof's LAST verdict line, not its exit code: NOT REPRODUCED is not a game failure",
    "compare the failing rows across items before assuming a shared cause, and before assuming none",
    "sort each failing row MOD / SITE / TOOL / HOST before rerunning anything",
    "N misses of N on the right site means the criterion is wrong, not the mod: question the contract",
    "read the item's history and every earlier pilot note (TESTPILOT_SAT) first",
    "before taking the bridge, ask whether another run could change a decision; if not, do not run it",
)
CLASSIFY_RX = re.compile(r"^\s*CLASSIFY:\s*(MOD|SITE|HARNESS|CONTRACT)\b(?![|/])[\s:;,.\u2014-]*([^\s<|].{9,})", re.S)
INSTRUMENT = "instrument"   # snag class: the site or the instrument is broken, not the work - a block on its repair item
HISTORY_MAX = 10            # endings the brief lists, newest last       # a dead process or a silent checker tried nothing


def pkg(name):
    """A rimflow module as the package imports it: priority and friends use relative imports."""
    if os.path.dirname(HERE) not in sys.path:      # once: a call per ledger item grew sys.path past what a forkserver child takes
        sys.path.insert(0, os.path.dirname(HERE))
    return importlib.import_module("rimflow." + name)


def root():
    return os.environ.get("RELENTLESS_ROOT") or DEFAULT_ROOT


def rules(path=None):
    with open(path or os.environ.get("RELENTLESS_RULES") or RULES, encoding="utf-8") as f:
        return json.load(f)


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


# ---------------------------------------------------------------- the store (host-wide, ext4, one flock)

ALARM_TOLD_EVERY_S = 6 * 3600     # inside incident.py event_quiet_min, so a standing alarm keeps its incident open


class Store:
    on_alarm = None     # the real Fx sets it: an alarm on the journal is a signal on the told ledger

    def __init__(self, base=None):
        self.root = base or root()
        self.dir = os.path.join(self.root, "store")
        os.makedirs(os.path.join(self.dir, "items"), exist_ok=True)

    def p(self, *a):
        return os.path.join(self.dir, *a)

    def item_dir(self, item):
        return self.p("items", item)

    @contextlib.contextmanager
    def lock(self):
        """Every transition holds this. Never held across a blocking effect (a stop, a launch, a publish)."""
        fd = os.open(self.p(".lock"), os.O_CREAT | os.O_RDWR, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            os.close(fd)

    def _write(self, path, text):
        tmp = "%s.tmp.%d" % (path, os.getpid())
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        d = os.open(os.path.dirname(path), os.O_RDONLY)
        try:
            os.fsync(d)
        finally:
            os.close(d)

    def _append(self, path, line):
        with open(path, "a+b") as f:
            f.seek(0, os.SEEK_END)
            head = b""
            if f.tell():            # a torn last line (no newline) would glue this record onto it and lose both
                f.seek(-1, os.SEEK_END)
                head = b"" if f.read(1) == b"\n" else b"\n"
            f.write(head + (line.rstrip("\n") + "\n").encode("utf-8"))
            f.flush()
            os.fsync(f.fileno())

    def load(self, item):
        try:
            with open(os.path.join(self.item_dir(item), "state.json"), encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def save(self, st):
        os.makedirs(os.path.join(self.item_dir(st["item"]), "receipts"), exist_ok=True)
        self._write(os.path.join(self.item_dir(st["item"]), "state.json"), json.dumps(st, indent=1, sort_keys=True))

    def items(self):
        return sorted(os.listdir(self.p("items")))

    def states(self):
        return [s for s in (self.load(i) for i in self.items()) if s]

    def journal(self, rec):
        self._append(self.p("journal.jsonl"), json.dumps(rec, sort_keys=True))
        if self.on_alarm and rec.get("do") == "alarm":
            self.on_alarm(rec)

    def attempts(self, item):
        try:
            with open(os.path.join(self.item_dir(item), "attempts.jsonl"), encoding="utf-8") as f:
                lines = f.readlines()
        except (OSError, ValueError):
            return []
        out = []
        for ln in lines:        # one torn line loses that line, never the record around it
            try:
                out.append(json.loads(ln))
            except ValueError:
                pass
        return out

    def attempt(self, item, rec):
        self._append(os.path.join(self.item_dir(item), "attempts.jsonl"), json.dumps(rec, sort_keys=True))

    def learn(self, item, text):
        self._append(os.path.join(self.item_dir(item), "learned.md"), text)

    def learned(self, item):
        try:
            with open(os.path.join(self.item_dir(item), "learned.md"), encoding="utf-8") as f:
                return f.read()
        except OSError:
            return ""

    def receipt_path(self, item, gen):
        return os.path.join(self.item_dir(item), "receipts", "gen%d.json" % gen)

    def read_receipt(self, item, gen):
        try:
            with open(self.receipt_path(item, gen), encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return None


def new_state(item, now, why):
    return {"item": item, "status": "queued", "gen": 0, "enrolled_at": now, "why": why, "returned_at": None,
            "returns": 0, "failures": {}, "total_failures": 0, "approach": "build", "approach_changes": 0,
            "spent": 0, "attempts": 0, "unit": None, "scope": None, "clone": None, "started_at": None,
            "last_beat": None, "stopping_since": None, "contract": None, "candidate": None, "check": None,
            "hold": None, "last_fail": None, "last_sha": None, "sha_at_change": None, "run": None,
            "not_before": 0, "ledger_started": False, "start_intent": False, "done_at": None, "quarantined": []}


def queue_order(states, plan=None, first=None):
    """An expedited item first (relentless_expedite), then system items (`first`: {item: place}, Operations' verdict,
    PIPELINE_BUDGET_ENFORCE_HEAL_THYSELF), then the priority list (`plan`: {item: place}, DI3), then returned items, oldest return first, then fresh in enrol order. Pure."""
    plan, first = plan or {}, first or {}
    q = [s for s in states if s["status"] == "queued"]
    return sorted(q, key=lambda s: (-2, relentless_expedite.rank(s["expedite"]), s["item"]) if s.get("expedite")
                  else (-1, first[s["item"]], s["item"]) if s["item"] in first
                  else (0, plan[s["item"]], s["item"]) if s["item"] in plan
                  else (1, s["returned_at"], s["item"]) if s["returned_at"] is not None
                  else (2, s["enrolled_at"], s["item"]))


def health_order(verdict, why, fallback):
    """Operations' health verdict (Utils/ops_health.py, health.json) as Relentless obeys it; it judges nothing itself.
    The owner, 2026-11-03: "I want it to ask "the system" for its health assessment, and that belongs to the operations
    component." -> {first: {item: place}, degraded, fresh, unmeasured, why}. An `unmeasured` verdict (unusable health
    rules) is an assessment broken, never healthy: fresh False, its `repair` items placed before every other system item, and its
    `pause` global (pause_scope). With no fresh verdict every open system item is first
    at once, by Operations' own classifier (`fallback`), and content is never paused (owner card 2026-11-03: "System
    work immediately but existing non system work continues")."""
    ids = verdict.get("system_items") if verdict else None
    said = "%s: %s" % (why, verdict.get("why") or "") if verdict else why
    if ids is None:     # no verdict, or one whose pass had no ledger: Operations' classifier names the items
        try:
            ids, said = list(fallback() or []), "%s; every open system item first, at once" % said
        except Exception as e:  # noqa: BLE001  no classifier: ordinary order, said aloud
            ids, said = [], "%s; system items unknown (%s: %s): ordinary order" % (said, type(e).__name__, str(e)[:120])
    unmeasured = bool(verdict) and verdict.get("state") == "unmeasured"
    if unmeasured:      # the assessment is broken, not healthy: its measurement repair goes first; pause_scope: global
        rep = [i for i in verdict.get("repair") or () if isinstance(i, str)]
        ids = rep + [i for i in ids if i not in rep]
        said = "ASSESSMENT BROKEN (state unmeasured): %s; repair first: %s" % (said, ", ".join(rep) or "none filed yet")
    degraded = bool(verdict) and verdict.get("state") == "degraded"
    return {"first": {i: n for n, i in enumerate(ids)}, "degraded": degraded,
            "fresh": bool(verdict) and not unmeasured, "unmeasured": unmeasured, "why": said,
            "pause": pause_scope(verdict) if degraded or unmeasured else None}


def pause_scope(verdict):
    """What a degraded or unmeasured verdict pauses (DEGRADED_PAUSE_FIX_STOPS_ONLY_WHAT_BROKE; owner card 2026-11-05,
    "What should happen to mod work while the system is unhealthy? -> Pause only what it touches"; spec
    design/RimMandrake/relentless_recovery_plan_2026-11-05.md section 3) -> {global: why or None, lanes: [lane]}.
    Global when a shared integrity resource is impaired: the assessment is unmeasured, or a spent SLI's scope is
    integrity/all (storage headroom), or the verdict names no scopes (an older collector: the old, whole pause). The
    account circuit and a suspect store are Relentless's own readings, added in content_pause. Otherwise the lanes the
    spent SLIs reach (`game`: content that needs the live game); scope `system` pauses no content lane. Pure."""
    if verdict.get("state") == "unmeasured":
        return {"global": "health assessment unmeasured", "lanes": []}
    scopes = verdict.get("spent_scope")
    if not isinstance(scopes, dict) or not scopes:
        return {"global": "verdict names no SLI scope (spent: %s)" % (", ".join(verdict.get("spent") or ()) or "?"), "lanes": []}
    wide = sorted(k for k, v in scopes.items() if v not in ("game", "system"))
    if wide:
        return {"global": "shared resource SLI spent: " + ", ".join("%s (%s)" % (k, scopes[k]) for k in wide), "lanes": []}
    return {"global": None, "lanes": sorted({v for v in scopes.values() if v != "system"})}


def pilot_count(store, st, klass, detail, r, now):
    """Under the lock. One more live ending; at rules.pilot_after_live_fails since the last sitting the next worker is an
    rm-testpilot sitting (TEST_PILOT_WIRE_INTO_THE_PIPELINE_EARLY). 0 or unset turns the step off."""
    n = int(r.get("pilot_after_live_fails") or 0)
    if st.get("pilot_step") or st["approach"] == "pilot":     # a pilot is owed or sitting: this ending is its to explain
        st["live_since_pilot"] = 0
        return
    st["live_since_pilot"] = (st.get("live_since_pilot") or 0) + 1
    if n <= 0 or st["live_since_pilot"] < n:
        return
    st["pilot_step"] = {"at": now, "after": st["live_since_pilot"], "class": klass, "detail": (detail or "")[:600]}
    st["live_since_pilot"] = 0
    store.journal({"at": iso(now), "do": "pilot_step", "item": st["item"], "after": st["pilot_step"]["after"], "class": klass})
    store.learn(st["item"], "- %s %d live endings since the last pilot sitting (last %s): the next worker is a Test Pilot sitting (%s), to "
                "explain them before any rebuild" % (iso(now), st["pilot_step"]["after"], klass, r.get("pilot_agent")))


def piloting(st):
    """Is the worker leased for this gen a Test Pilot? The ladder's pilot rung, or a pending/sitting pilot step."""
    ps = st.get("pilot_step") or {}
    return st["approach"] == "pilot" or (bool(ps) and ps.get("sat_gen") in (None, st["gen"]))


def pilot_sat(st, klass):
    """Under the lock, from fail() before gen moves: a pilot step's sitting has ended with this ending. A lost worker
    sat nothing: the step stays pending for the next lease."""
    ps = st.get("pilot_step")
    if not ps or ps.get("sat_gen") is None:
        return
    if klass in NOT_AN_APPROACH:
        ps.pop("sat_gen", None)
        return
    st.pop("pilot_step", None)
    st["piloted"] = (st.get("piloted") or 0) + 1


def fail(store, st, klass, detail, r, now, time_not_work=False, attributed=None):
    """Under the lock. Fence first: gen moves here, before anything is stopped. The item goes to the TOP.
    A validation ending (relentless_attrib.GATED) is blamed before anything is rebuilt: with no PRODUCT attribution it
    earns no strike, no gen and no builder; the candidate waits for a read-only diagnosis -> "gated"/"routed"."""
    klass = SLUG_RX.sub("_", (klass or "snag").lower()).strip("_")[:40] or "snag"
    if attributed is None and klass in LIVE_ENDS:      # counted once, at the reading: an attributed re-entry is the same one
        pilot_count(store, st, klass, detail, r, now)
    if (attributed is not None and klass in relentless_attrib.GATED
            and "PRODUCT" not in (attributed.get("targets") or [])):
        # CHECKER_VERDICT_BUILD_CAUSE_BEFORE_RETURN: a validation ending returns or strikes only on a PRODUCT attribution;
        # anything else handed in here is blamed afresh, never a builder by default
        attributed = None
    if attributed is None and klass in relentless_attrib.GATED:
        attributed = relentless_attrib.gate(store, st, klass, detail, r, now, sys.modules[__name__])
        if attributed in ("gated", "routed"):
            store.save(st)
            return attributed
    st.pop("live_iter", None)       # a live iteration ends with its worker; the game phase sets a new one on its FAIL
    st.pop("live_wait_since", None)     # a wait on the live line belongs to the candidate this ending puts down
    pilot_sat(st, klass)
    st["gen"] += 1
    st["status"] = "stopping"
    st["stopping_since"] = now
    st["returned_at"] = now
    st["returns"] += 1
    st["failures"][klass] = st["failures"].get(klass, 0) + 1
    st["total_failures"] += 1
    if time_not_work:   # a wait is no failed approach: it counts toward its own class's wait, never the unchanged tally
        st["total_at_change"] = (st.get("total_at_change") or 0) + 1
    st["last_fail"] = {"class": klass, "detail": (detail or "")[:2000], "at": now}
    limit = r["same_failure_limit"]
    if klass in ("proof_weak", relentless_attrib.PROOF_OWED):
        st["proof_only"] = {"sha": st["candidate"]["sha"], "at": now,
                            "contract": copy.deepcopy(st.get("contract"))}     # what proof_gate compares a re-finish with
        if klass == "proof_weak":
            st["proof_only"]["weak"] = (detail or "")[:600]     # the verdict that set it, re-read under today's WEAK rule
        if "CONTRACT" in ((attributed or {}).get("targets") or []):
            st["proof_only"]["binding"] = True      # the binding may live off the sha (the contract, a ledger criterion)
            # every live row on this sha was read under the binding just found wrong: the repaired binding is judged
            # fresh, never by the old REFUSED/FAIL (or PASS) rows (relentless_live_round.history keys rows by sha)
            relentless_game.void_rows(store.root, st["item"], st["candidate"]["sha"],
                                      "binding attributed CONTRACT: %s" % ((attributed or {}).get("evidence") or "")[:200], now)
    elif klass in ("blind_fail", PROOF_DEFECT):     # the work itself is in doubt again: the code may move
        st["proof_only"] = None
        for k in PROOF_ENDS:
            st["failures"].pop(k, None)
    if klass in PROOF_ENDS:
        st.pop("warrant_owed", None)    # the checker's named gaps are the proof-only worker's warrant
        # WEAK is not good code, it is unproven code: the road is a stronger proof, not a redesign. Enough tries stop and say so, open
        st["total_at_change"] = (st.get("total_at_change") or 0) + 1
        n = sum(st["failures"].get(k, 0) for k in PROOF_ENDS)
        if n >= limit:
            relentless_strikes.hold(st, "%d returns and the proof still reads weak" % n, "proof_weak", now)
        store.attempt(st["item"], {"at": iso(now), "gen": st["gen"] - 1, "end": klass, "detail": (detail or "")[:600],
                                   "sha": (st.get("candidate") or {}).get("sha")})
        store.learn(st["item"], "- %s gen %d ended %s: %s" % (iso(now), st["gen"] - 1, klass, (detail or "")[:600]))
        store.save(st)
        return
    # rotating slugs cannot dodge this: enough returns with no new sha also change the approach
    unchanged = st["total_failures"] - (st.get("total_at_change") or 0) >= r.get("unchanged_returns_limit", limit * 3)
    # CONTRACT_WALL_REPLACE_NEXT_GEN: a worker that found the SET contract itself wrong (a contract_* snag) cannot replace
    # it on a build attempt (contract(): only a redesign or a proof-only worker may). Waiting for same_failure_limit returns
    # of one slug cost TESTQ_WORKER_MIGRATE_PYDANTIC_CONTRACT, DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO and
    # GUBBRA_GOURD_FIX_WONT_SELECT two or three wasted builds each, and their workers' rotating slugs dodged the count:
    # the next attempt is the redesign at once, the one road that may change the contract (never pilot: it may not)
    wall = klass.startswith("contract") and bool(st.get("contract")) and st["approach"] != "redesign"
    if (((st["failures"][klass] >= limit and not time_not_work) or unchanged or wall)
            and relentless_strikes.out_of_tacks(st, r)):
        # the ladder has been climbed: a person decides the next tack (RELENTLESS_STRIKES_HARDEN_CHANGE_TACK)
        relentless_strikes.hold(st, "%d strikes of %s after %d approach changes: split it, redesign it, or drop it"
                                % (st["failures"][klass], klass, st["approach_changes"]), "strikes", now)
    elif (st["failures"][klass] >= limit and not time_not_work) or unchanged or wall:
        st["failures"][klass] = 0
        st["total_at_change"] = st["total_failures"]
        st["approach_changes"] += 1
        wanted = "pilot" if st.get("pilot_wanted") else "redesign"
        st["approach"] = ("redesign" if wall or st["approach"] == "pilot" else
                          "pilot" if st["approach"] == "redesign" else wanted)
    rec = {"at": iso(now), "gen": st["gen"] - 1, "end": klass, "detail": (detail or "")[:600], "approach_next": st["approach"]}
    if time_not_work:
        rec["wait"] = True
    store.attempt(st["item"], rec)
    store.learn(st["item"], "- %s gen %d ended %s: %s" % (iso(now), st["gen"] - 1, klass, (detail or "")[:600]))
    # loop breakers that redirect (CHURN_BREAKER_BUILD_RETRY_NEEDS_A_WARRANT): the next worker owes a retry warrant; one
    # capability failing many items is one incident; the same signature on three builds suspends rebuilding
    relentless_breakers.owe_warrant(st, klass, time_not_work)
    if not time_not_work:
        relentless_breakers.note(store, st["item"], klass, detail, r, now)
    if not st.get("hold") and not time_not_work:
        why = relentless_breakers.same_signature_hold(store.attempts(st["item"]), klass, detail, r, st.get("sig_since", 0))
        if why:
            relentless_strikes.hold(st, why, "signature", now)
    if klass in DIAGNOSE_ENDS and not attributed:
        st["diagnose_owed"] = {"class": klass, "detail": (detail or "")[:600], "at": now, "gen": st["gen"]}
    if klass == "circling":     # under this lock, so no tick can lease the next worker ahead of the consult
        st["circling_hits"] = st.get("circling_hits", 0) + 1
        force_help(store, st, r, now)
    store.save(st)


def unmeasured(store, st, said, blind, r, now):
    """Under the lock. The Marker could not reach the evidence (CHECKER_SANDBOX_FIX_BLIND_TO_STEVE): an inability, not a red
    proof. No gen, no return, no approach change, nothing goes back to a worker: the same candidate is checked again after a
    wait, and the same blindness twice running on one sha holds the item for repair of the box. Kind `unmeasured` is not his:
    the held branch routes it to the seat queue and the Conductor. -> the ledger line, written by the caller out of the lock."""
    sha = (st.get("candidate") or {}).get("sha")
    chk = dict(st["check"] or {})
    reasons = chk.get("reasons") or ""
    prev = st.get("blind") or {}
    n = prev.get("n", 0) + 1 if prev.get("sha") == sha else 1
    st["blind"] = {"n": n, "sha": sha, "at": now, "said": said, "what": (blind or reasons)[:600],
                   "box": relentless_reach.fingerprint(r, st.get("contract"))}     # what a repair of the box would change
    st["check"] = None
    store.attempt(st["item"], {"at": iso(now), "gen": st["gen"], "end": "unmeasured", "said": said,
                               "detail": reasons[:600], "sha": sha})
    if relentless_reachfix.on(r):
        # BLIND_JUDGE_BUILD_FIXES_OWN_EYES: the first blind check ends the checking; the Judge's proposal is probed,
        # applied by the supervisor and the same sha checked once (relentless_reachfix.py). No clock re-check.
        st["_blind_check"] = chk
        try:
            said_line = relentless_reachfix.on_blind(store, st, r, now, said, blind)
        finally:
            st.pop("_blind_check", None)
        store.save(st)
        return said_line
    limit = r.get("unmeasured_limit", 2)
    if n >= limit:
        # legacy route, rule reach_repair false only
        relentless_strikes.hold(st, "the checker could not reach the evidence on %d checks running of %s, so the box needs "
                                "repair, not the work: %s. Fix the box, or unhold --offbox NAME with a supervisor adapter (relentless_rules.json offbox_adapters) that reads it from outside; "
                                "either way unhold checks this sha again" % (n, sha, (blind or reasons)[:300]), "unmeasured", now)
        st["status"] = "held"
        st.pop("recheck_at", None)
    else:
        st["status"] = "candidate"
        st["recheck_at"] = now + r.get("unmeasured_recheck_s", 1800)
    store.save(st)
    return ("blind check at %s: UNMEASURED (Marker said %s), the checker could not reach the evidence; no work goes back, "
            "%s: %s" % (sha, said, "held for repair of the box" if n >= limit else "checked again in %d s"
                        % r.get("unmeasured_recheck_s", 1800), (blind or reasons)[:400]))


def account_lost(store, st, lost, r, now):
    """Under the lock. The account ended this run, not the item (relentless_account.py): no strike, no return, no change of
    approach; its clone and its place stay. What it spent was spent and stays charged. An empty account also counts on the
    launch breaker, so a belt on it stops launching; a change-over is over by the time this runs."""
    st.pop("live_iter", None)
    st["gen"] += 1
    st["run"] = None
    st["status"] = "held" if st["hold"] else "blocked" if st.get("block_pending") or st.get("wait") else "queued"
    st["returned_at"] = st["returned_at"] or now
    ps = st.get("pilot_step") or {}
    if ps.get("sat_gen") == st["gen"] - 1:      # the pilot sitting the account cut stays owed (Codex r5 part0 #5)
        if lost.get("session"):
            ps["sat_gen"] = st["gen"]           # its resumed session goes on sitting it
        else:
            ps.pop("sat_gen", None)             # pending for the next lease, as pilot_sat leaves a lost worker's
    if lost.get("session"):     # it did real work: the next launch resumes that session instead of starting over
        st["resume"] = {"session": lost["session"], "gen": st["gen"], "at": now}
    else:
        st.pop("resume", None)
    store.attempt(st["item"], {"at": iso(now), "gen": st["gen"] - 1, "end": "account_lost", "detail": lost["why"][:600],
                               **({"session": lost["session"]} if lost.get("session") else {})})
    store.learn(st["item"], "- %s gen %d ended account_lost, no strike%s: %s" % (
        iso(now), st["gen"] - 1, ", its session is resumed" if lost.get("session") else "", lost["why"][:600]))
    store.save(st)
    if lost["kind"] == "account_error":
        launch_failed(store, r, now, lost["why"])


RESUME_WORDS = "Tokens are back; continue where you were."


def tree_present(path):
    """The tree a resumed checker or consult goes back into is still there (the selftest plants this)."""
    return os.path.isdir(path)


def resume_prompt(st, kind):
    """The message a resumed session gets (claude -p --resume). A worker's lease moved on when the account cut it: the
    gen it remembers is fenced, so it is told the new one."""
    if kind == "work":
        return ("%s The account cut your run, not your work: no strike was charged. Your lease is now generation %d of "
                "%s: use --gen %d in every relentless.py call from here on; the old generation is fenced."
                % (RESUME_WORDS, st["gen"], st["item"], st["gen"]))
    return RESUME_WORDS


def day_key(now):
    return time.strftime("%Y%m%d", time.gmtime(now))


def _day(store, now):
    try:
        with open(store.p("spend-%s.json" % day_key(now)), encoding="utf-8") as f:
            d = json.load(f)
        num = lambda v: type(v) is int and v >= 0       # noqa: E731  (a bool is an int; a negative charge understates)
        if not isinstance(d, dict) or not isinstance(d.get("runs"), dict) or not num(d.get("spent")) or \
                not all(num(v) for v in d["runs"].values()) or \
                not isinstance(d.get("basis", {}), dict):
            raise ValueError("spend record has the wrong shape")
        return d
    except FileNotFoundError:
        return {"spent": 0, "runs": {}}         # a new day has no file; a file that is there and unreadable is not a new day


UNREADABLE_SPEND = 10 ** 15      # an accounting record we cannot read blocks spending; it never reads as an empty day


def spent_today(store, now):
    try:
        _day(store, now - 86400)        # yesterday's record is read by charge(): if it is damaged, nothing today can be charged
        return int(_day(store, now).get("spent", 0))
    except (OSError, ValueError, TypeError, AttributeError):
        return UNREADABLE_SPEND


class SpendUnreadable(ValueError):
    """charge() met a damaged day record: nothing was booked and nothing on the item moved."""


def charge(store, st, tokens, now, r, unit, basis=None):
    """Under the lock. A run with no measured usage (no tokens, basis absent or "estimated") is charged the reserve,
    never less; a measured zero (basis "result", RELENTLESS_SPEND_FIX_ZERO_USAGE_RESERVE) is charged 0. The day file
    is keyed by run, so a crash before the item's own marker is saved cannot count a run twice."""
    measured = basis != "estimated" and (bool(tokens) or (tokens is not None and basis is not None))
    # an "estimated" basis is never a measurement, whatever number rides with it (Codex, ..._TEN_MORE #1)
    n = int(tokens) if measured else r["run_reserve"]
    try:
        d = _day(store, now)
        new = unit not in d["runs"] and unit not in _day(store, now - 86400)["runs"]
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as e:
        # never replace a damaged day file with a partial history, and never raise st["spent"] past a run the day did
        # not book: the item's step raises before it saves, keeps the run uncharged, and charges it on the first tick
        # after the record is repaired (spent_today refuses all work meanwhile). Before, the item counted the run and
        # the repaired day never did (Codex r4 part0 #1).
        raise SpendUnreadable("spend record unreadable (%s: %s): run %s stays uncharged until it is repaired"
                              % (type(e).__name__, e, unit)) from e
    if not new:     # a replay after a crash: the item takes what the day booked, never a second figure (r5 part0 #2)
        booked = d["runs"].get(unit, _day(store, now - 86400)["runs"].get(unit))
        n = int(booked) if isinstance(booked, (int, float)) else n
    if new:
        d["runs"][unit] = n
        d["spent"] += n
        if basis and basis != "result":     # how a charge not read from the result object was reached
            d["basis"] = dict(d.get("basis") or {}, **{unit: basis if measured else "estimated"})
        store._write(store.p("spend-%s.json" % day_key(now)), json.dumps(d))
        # a failed write raises: a charge we could not book must not leave spent_today reading low (Codex r3)
    st["spent"] += n
    return n


def run_fixture_cmd(cmd, cwd, timeout):
    """-> (exit, tail). The fixture runs in its own session and its whole process group is killed when it ends or times
    out: a backgrounded child never outlives it to keep writing the books tree (Codex, ..._TEN_MORE #2)."""
    try:
        p = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             stdin=subprocess.DEVNULL, start_new_session=True)
    except (OSError, subprocess.SubprocessError) as e:
        return None, "%s: %s" % (type(e).__name__, e)
    import threading
    tail = bytearray()

    def drain():        # only a bounded tail is kept: a fixture that floods its output never grows our memory (r5 #8)
        for chunk in iter(lambda: p.stdout.read(65536), b""):
            tail.extend(chunk)
            del tail[:-8192]
    reader = threading.Thread(target=drain, daemon=True)
    reader.start()

    def kill_group():
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
    try:
        p.wait(timeout=timeout)
    except subprocess.TimeoutExpired as e:
        kill_group()
        try:
            p.wait(timeout=10)
        except subprocess.SubprocessError:
            pass
        reader.join(10)
        return None, "TimeoutExpired: %s" % e
    finally:
        kill_group()        # the shell is done; a child it left running is not part of the answer
    reader.join(10)         # the group is dead, so the pipe ends
    return p.returncode, bytes(tail).decode("utf-8", errors="replace")[-600:]


# ---------------------------------------------------------------- what a worker may call (all fenced)

class Fenced(Exception):
    pass


def _fence(st, item, gen, stage_ok=False):
    """stage_ok: the game phase's staging worker (relentless_game) may beat, learn and snag too."""
    if st is None:
        raise Fenced("%s is not enrolled" % item)
    if stage_ok and relentless_game.staging(st, gen):
        return
    if st["gen"] != gen or st["status"] != "running":
        raise Fenced("%s: your lease gen %d is gone (now gen %d, %s). Stop now." % (item, gen, st["gen"], st["status"]))


def beat(store, item, gen, now=None):
    with store.lock():
        st = store.load(item)
        _fence(st, item, gen, stage_ok=True)
        st["last_beat"] = time.time() if now is None else now
        store.save(st)


def learn(store, item, gen, text, now=None):
    with store.lock():
        st = store.load(item)
        _fence(st, item, gen, stage_ok=True)
        st["last_beat"] = time.time() if now is None else now
        m = CLASSIFY_RX.match(text or "")
        if m and st.get("diagnose_owed"):     # a label, recorded whole; only `explain` pays the debt
            store.attempt(item, {"at": iso(st["last_beat"]), "gen": gen, "classified": m.group(1),
                                 "evidence": m.group(2)[:4000]})      # whole: the next role reads the attribution, not a cut
        w = relentless_breakers.take_warrant(st, text, gen, st["last_beat"])
        if w:
            store.attempt(item, {"at": iso(st["last_beat"]), "gen": gen, "warrant": w})
        store.learn(item, "- %s gen %d: %s" % (iso(st["last_beat"]), gen, text))
        store.save(st)


def explain(store, item, gen, klass, a, now=None, state_of=None, note=None):
    """A worker's written explanation of the last ending (relentless_explain): what the proof expected, what the game
    did, the mechanism, evidence per step, theories ruled out, and the one open follow-up item for its cause. It pays
    the debt a DIAGNOSE ending leaves (diagnose_owed); a CLASSIFY label does not. `state_of(id)` -> ledger state (the
    cause must be filed and open); `note(id, text)` puts the explanation on the cause item's ledger history."""
    klass = (klass or "").strip().upper()
    if klass not in relentless_explain.CLASSES:
        raise ValueError("--class must be one of %s" % "|".join(relentless_explain.CLASSES))
    rec = relentless_explain.validate(a, [klass], item, a.get("cause"))
    relentless_explain.check_cause(rec["cause"], state_of)
    now = time.time() if now is None else now
    with store.lock():
        st = store.load(item)
        _fence(st, item, gen, stage_ok=True)
        st["last_beat"] = now
        owed = st.pop("diagnose_owed", None)
        ending = (owed or st.get("last_fail") or {}).get("class")
        if owed:
            st["diagnosed"] = {"class": klass, "evidence": rec["mechanism"][:4000], "gen": gen, "at": now, "of": owed,
                               "cause": rec["cause"]}
        new = relentless_explain.keep(store, item, gen, rec, ending, (st.get("candidate") or {}).get("sha"),
                                      "worker gen %d" % gen, now)
        store.save(st)
    if note:
        note(item, "relentless: %s explained (%s): %s | follow-up: %s" % (ending or "the last ending", klass,
                                                                          rec["mechanism"][:600], rec["cause"]))
        if new and rec["cause"] != item:
            note(rec["cause"], relentless_explain.note_text(item, dict(rec, ending=ending)))
    return rec["cause"]


def reload_needed(store, item, gen, text, now=None):
    """A worker iterating on the running game (live_iter) records its proof that only a rebuild and a reload go further
    (owner 2026-11-02: work the item on the live game "until it provably needs a rebuild and reload"). It frees the game
    for the next item at once; the worker goes on offline, and its build waits for the one batched reload."""
    if not (text or "").strip():
        raise ValueError("reload-needed takes its proof: what needs the reload and why the running game cannot take it")
    now = time.time() if now is None else now
    with store.lock():
        st = store.load(item)
        _fence(st, item, gen)
        li = st.pop("live_iter", None) or st.get("live_lapsed")     # a lapsed hold (lapse_holds) still takes its proof
        if li is None:
            raise ValueError("%s is not iterating on the running game (no live_iter): nothing to free" % item)
        st["reload_needed"] = {"at": now, "gen": gen, "why": text[:1000], "session": li.get("started")}
        st["last_beat"] = now
        store.learn(item, "- %s gen %d: RELOAD NEEDED: %s" % (iso(now), gen, text))
        store.save(st)
    relentless_game.session_note(store, li.get("started"), item, reload_why=text, now=now)


def reach_hold(store, r, item, now):
    """The candidate branch's gate before any clone or Marker (CHECKER_REACH_PROBE_BEFORE_PAYING_TWICE). -> why it held, or
    None. Two cases cost a Marker to learn nothing: a proof that names what the box hides with nothing routing it (a contract
    set before the contract-time probe), and an UNMEASURED recheck on the same sha with the same box. Held kind unmeasured:
    the seat's to repair; `unhold --offbox NAME` routes it, a plain unhold is the Conductor's why (reach_ok) or a recheck."""
    with store.lock():
        st = store.load(item)
        if not st or st["status"] != "candidate":
            return None
        found = relentless_reach.uncovered(st.get("contract"), r)
        if found:
            why = "held before launch, no Marker paid: %s" % relentless_reach.refusal(found, relentless_wall.adapters(r))
        elif relentless_reach.repays(st, r):
            why = ("held before the recheck, no Marker paid: %s was UNMEASURED and the box is unchanged since (walls, adapters "
                   "and contract fingerprint %s), so a second Marker would buy the same answer: %s. Fix the box, or unhold "
                   "--offbox NAME" % (st["blind"]["sha"], st["blind"]["box"], (st["blind"].get("what") or "")[:300]))
        else:
            return None
        relentless_strikes.hold(st, why, "unmeasured", now)
        st["hold"]["reach"] = bool(found)
        st["status"] = "held"
        st.pop("recheck_at", None)
        store.attempt(item, {"at": iso(now), "gen": st["gen"], "end": "reach_held", "detail": why[:600],
                             "sha": (st.get("candidate") or {}).get("sha")})
        store.save(st)
    return why


def contract(store, item, gen, proof, live=None, why=None, now=None, game=None, offbox=None, reach_ok=None, r=None,
             obligation=None, scenario=None, fixtures=None, freshness=None):
    """Set by the first worker before it edits; only a redesign may change it, and says why. One exception: any worker
    may add a live line the contract lacks with the proof unchanged, since that only asks more of the work. Three
    workers of CLOSE_GATE_ENFORCE_DONE_IS_EARNED died on the lock before a redesign could add it. `offbox`: adapter names
    (relentless_rules.json offbox_adapters) the supervisor runs outside the Marker's wall at check time; adding them with the proof
    unchanged also widens, since the Marker still judges whether each one measures its clause. Outside a redesign the offbox
    adapters and game clauses already set are kept: a change names more, never fewer. `reach_ok`: the worker's why for a
    proof that names what the walled Marker's box hides (relentless_reach.needs); without it or an adapter such a proof is
    refused here, before a Marker is paid to say CANNOT REACH (CHECKER_REACH_PROBE_BEFORE_PAYING_TWICE). `r`: the rules.
    `obligation`: what must be true, in the item's words (relentless_binding); only a redesign changes it, version + 1.
    `scenario`, `fixtures`, `freshness`: the rest of the binding. A binding repair outside a redesign is `rebind`."""
    r = rules() if r is None else r
    offbox = relentless_wall.check_offbox_names(offbox, r)    # names of supervisor adapters only: no worker shell
    import live_line
    if live:
        live_line.parse(live)
    now = time.time() if now is None else now
    with store.lock():
        st = store.load(item)
        _fence(st, item, gen)
        widens = st["contract"] and live and not st["contract"].get("live") and proof == st["contract"]["proof"]
        # naming game clauses with the proof unchanged also only asks more (relentless_game): one more phase to pass
        widens = widens or (st["contract"] and game and proof == st["contract"]["proof"] and not st["contract"].get("game")
                            and live in (None, st["contract"].get("live")))
        widens = widens or (st["contract"] and offbox and proof == st["contract"]["proof"] and not st["contract"].get("offbox")
                            and live in (None, st["contract"].get("live")))
        if st["contract"] and not widens and st["approach"] != "redesign" and not st.get("proof_only"):
            raise ValueError("the contract is set; only a redesign attempt or a proof-only worker may change it (any worker may "
                             "add a missing --live with the same --proof)")
        if st["contract"] and not why:
            raise ValueError("changing the contract needs --why")
        if st["contract"] and st["approach"] != "redesign":  # a widening or a proof-only change asks more, never less:
            if live and st["contract"].get("live") and live != st["contract"]["live"]:
                raise ValueError("the live line is set (%r): only a redesign replaces it (Codex r5 part0 #1)"
                                 % st["contract"]["live"])
            live = live or st["contract"].get("live")       # an obligation it leaves out is the one already set, and
            old_game = st["contract"].get("game")           # naming fewer adapters or game clauses drops none (GPT
            if old_game and game:                           # pass 10): the sets are merged, never replaced
                game = dict(old_game, **game)
                game["clauses"] = sorted(set(old_game.get("clauses") or []) | set(game.get("clauses") or []))
            game = game or old_game
            had = list(st["contract"].get("offbox") or [])
            offbox = had + [x for x in (offbox or []) if x not in had]
            if len(offbox) > relentless_wall.OFFBOX_MAX:
                raise ValueError("at most %d offbox adapters (the contract already names %s)"
                                 % (relentless_wall.OFFBOX_MAX, ", ".join(had)))
        old_ob = relentless_binding.obligation_of(st["contract"], item) if st["contract"] else None
        if (st["contract"] and st["approach"] != "redesign" and obligation is not None
                and obligation.strip() != old_ob["text"].strip()):
            raise ValueError("the obligation (what must be true) moves only in a redesign; a broken way of measuring it "
                             "is a binding repair: `rebind` (relentless_binding)")
        if st["contract"] and st["approach"] != "redesign":     # a proof-only change: no typed number for a reading
            typed = relentless_binding.typed_numbers(proof)
            if typed and typed != relentless_binding.typed_numbers(st["contract"].get("proof")):
                raise ValueError("the new proof %s (relentless_binding)" % "; ".join(typed))
        reach_ok = (reach_ok or "").strip() or (None if st["approach"] == "redesign" else   # a redesign's new proof
                                                  (st["contract"] or {}).get("reach_ok"))   # earns its own why
        found = relentless_reach.uncovered({"proof": proof, "offbox": offbox, "reach_ok": reach_ok}, r)
        if found:
            raise ValueError(relentless_reach.refusal(found, relentless_wall.adapters(r)))
        prev = st["contract"]
        st["contract"] = {"proof": proof, "live": live, "by_gen": gen, "why": why}
        ob = obligation.strip() if obligation and obligation.strip() else None
        if prev and (ob is None or (old_ob and ob == old_ob["text"].strip())):
            if prev.get("obligation"):
                st["contract"]["obligation"] = prev["obligation"]
        elif ob:
            st["contract"]["obligation"] = {"text": ob[:relentless_binding.TEXT_MAX],
                                            "version": (old_ob["version"] + 1) if prev else 1}
        keep = prev and st["approach"] != "redesign"       # outside a redesign the binding only gains: a fixture
        if keep and scenario and prev.get("scenario") and scenario != prev["scenario"]:     # r5 part0 #3
            raise ValueError("the scenario is set (%r): changing it is a binding repair, `rebind`" % prev["scenario"])
        if keep and freshness and prev.get("freshness") and freshness != prev["freshness"]:   # set is merged, and a
            raise ValueError("the freshness rule is set (%r): changing it is a binding repair, `rebind`"   # freshness
                             % prev["freshness"])                                                 # moves only by rebind
        if keep:
            fixtures = list(prev.get("fixtures") or []) + [x for x in (fixtures or []) if x not in (prev.get("fixtures") or [])]
        for k, v in (("scenario", scenario), ("fixtures", fixtures), ("freshness", freshness)):
            v = v if v else ((prev or {}).get(k) if keep else None)
            if v:
                st["contract"][k] = v
        if reach_ok:
            st["contract"]["reach_ok"] = reach_ok[:400]
        if game:
            st["contract"]["game"] = game
        if offbox:
            st["contract"]["offbox"] = offbox
        if prev:    # counted on the whole binding, once every field is written back
            st["contract"]["binding_version"] = int(prev.get("binding_version") or 1) + (
                relentless_binding.binding_hash(prev) != relentless_binding.binding_hash(st["contract"]))
        st["last_beat"] = now
        store.attempt(item, {"at": iso(now), "gen": gen, "contract": st["contract"]})
        store.save(st)
    if not prev:    # the first contract, before the builder edits: a Setter (not this builder) owes the acceptance exam
        import relentless_exam      # RELENTLESS_BUILD_EXAM_BEFORE_BUILDER, shadow: detached unit, never raises or gates
        relentless_exam.on_contract(store, item, st.get("base"), now=now, clone=st.get("clone"))


def rebind(store, item, gen, binding, comparison, obligation=None, now=None, r=None):
    """Any worker's proposal to repair HOW its obligation is measured (relentless_binding): `binding` holds the new
    binding keys (proof, live, game, offbox, reach_ok, scenario, fixtures, freshness; one left out is kept), `comparison`
    {before, after, behaviour, defect}. The contract does not move: the proposal waits for an independent Setter/Judge
    (`bind-judge`). A weakening on its face is refused here. -> the judge's packet."""
    r = rules() if r is None else r
    now = time.time() if now is None else now
    if binding.get("offbox"):
        binding["offbox"] = relentless_wall.check_offbox_names(binding["offbox"], r)
    if binding.get("live"):
        import live_line
        live_line.parse(binding["live"])
    with store.lock():
        st = store.load(item)
        _fence(st, item, gen)
        if not st.get("contract"):
            raise ValueError("no contract is set: set one with `contract`; a repair needs a binding to repair")
        p = st.get("binding_proposal")
        if p:
            raise ValueError("a binding repair already waits for its judge (%s, by %s%s): one at a time, so a refusal or "
                             "an AMBIGUOUS is never written over by a fresh proposal"
                             % (p["at"], p["by"], ", ruled AMBIGUOUS" if p.get("ambiguous") else ""))
        old = relentless_binding.binding_of(st["contract"])
        new = {k: v for k, v in old.items() if k != "version"}
        new.update({k: v for k, v in binding.items() if v not in (None, "", [])})
        if binding.get("fixtures"):     # merged: dropping one is the screen's to refuse, never a silent replace
            new["fixtures"] = list(binding["fixtures"])
        if new.get("game") and old.get("game") and binding.get("game"):     # clauses merged, never replaced
            g = dict(old["game"], **new["game"])
            g["clauses"] = sorted(set(old["game"].get("clauses") or []) | set(new["game"].get("clauses") or []))
            new["game"] = g
        why = relentless_binding.screen(st["contract"], new, comparison, item, obligation)
        if relentless_binding.binding_hash(new) in (st.get("bindings_rejected") or []):
            why.append("this exact binding was REJECTED by a judge before: propose a different one or snag")
        found = relentless_reach.uncovered(new, r)
        if found:
            why.append(relentless_reach.refusal(found, relentless_wall.adapters(r)))
        if why:
            store.attempt(item, {"at": iso(now), "gen": gen, "end": "rebind_refused", "detail": "; ".join(why)[:1200]})
            raise ValueError("binding repair refused: " + "; ".join(why))
        st["binding_proposal"] = {
            "by": "gen %d of %s" % (gen, item), "gen": gen, "at": iso(now), "binding": new,
            "comparison": {k: (comparison.get(k) or "")[:relentless_binding.TEXT_MAX] for k in ("before", "after",
                                                                                              "behaviour", "defect")},
            "obligation_hash": relentless_binding.obligation_hash(st["contract"], item),
            "from_binding_hash": relentless_binding.binding_hash(st["contract"])}
        st["last_beat"] = now
        store.attempt(item, {"at": iso(now), "gen": gen, "end": "rebind_proposed", "proposal": st["binding_proposal"]})
        store.learn(item, "- %s gen %d proposed a binding repair (waits for bind-judge): %s"
                    % (iso(now), gen, (comparison.get("defect") or "")[:300]))
        store.save(st)
    store.journal({"at": iso(now), "do": "rebind_proposed", "item": item, "gen": gen})
    return relentless_binding.packet(st)


def bind_judge(store, item, judge, verdict, why, env=None, now=None, r=None, cwd=None):
    """The independent Setter/Judge's ruling on a pending binding repair. Never a worker session (RELENTLESS_GEN set) and
    never the proposer. approve: the binding moves (binding_version + 1), the obligation does not; reject: the proposal
    is dropped; ambiguous: it stays pending and unapplied, because ambiguity blocks. -> one line for the caller."""
    r = rules() if r is None else r
    env = os.environ if env is None else env
    now = time.time() if now is None else now
    judge, why = (judge or "").strip(), (why or "").strip()
    if verdict not in relentless_binding.VERDICTS:
        raise ValueError("--verdict must be one of %s" % "|".join(relentless_binding.VERDICTS))
    if not judge or not why:
        raise ValueError("a ruling names its judge (--as) and says why (--why): the semantic comparison it read")
    if env.get("RELENTLESS_GEN") or env.get("RELENTLESS_HELP_NONCE"):
        raise ValueError("a worker or consult session may not judge a binding repair: the judge is independent of the "
                         "work (a Setter/Judge outside the item's lease)")
    if re.search(r"(?i)\bgen\s*\d+\b|\b(?:worker|builder)\w*", judge) or item.lower() in judge.lower():
        raise ValueError("--as %r names a worker of the work: the judge is a Setter/Judge, the Conductor or Operations, "
                         "never a generation of the item" % judge)
    with store.lock():
        st = store.load(item)
        if not st:
            raise ValueError("%s is not enrolled" % item)
        p = st.get("binding_proposal")
        if not p:
            raise ValueError("%s has no binding repair waiting" % item)
        if judge.lower() == p["by"].lower():
            raise ValueError("the proposer may not judge its own binding repair")
        here = os.path.realpath(cwd or os.getcwd())
        for c in [st.get("clone")] + [x.get("clone") for x in (st.get("quarantined") or []) if isinstance(x, dict)]:
            if c and (here + os.sep).startswith(os.path.realpath(c) + os.sep):
                raise ValueError("a binding repair is not judged from the item's own clone (%s): the judge stands outside "
                                 "the work" % c)
        rec = {"at": iso(now), "end": "rebind_" + verdict, "judge": judge, "why": why[:1200],
               "proposal": p, "before": relentless_binding.split(st["contract"], item)}
        if verdict == "approve":
            stale = []
            if relentless_binding.obligation_hash(st["contract"], item) != p["obligation_hash"]:
                stale.append("the obligation changed since the proposal")
            if relentless_binding.binding_hash(st["contract"]) != p["from_binding_hash"]:
                stale.append("the binding changed since the proposal")
            again = relentless_binding.screen(st["contract"], p["binding"], p["comparison"], item)
            again += ["needs: %s" % x for x in relentless_reach.uncovered(p["binding"], r)]
            if stale or again:
                raise ValueError("cannot approve: %s" % "; ".join(stale + again))
            c = {k: v for k, v in st["contract"].items() if k not in relentless_binding.BINDING_KEYS}
            c.update(p["binding"])
            c["binding_version"] = relentless_binding.binding_of(st["contract"])["version"] + 1
            c["why"] = ("binding repair approved by %s: %s" % (judge, why))[:600]
            st["contract"] = c
            rec["after"] = relentless_binding.split(c, item)
            if st.get("proof_only"):    # the held sha is judged again under the repaired binding, never the old rows
                st["proof_only"]["binding"] = True
            st.pop("binding_proposal", None)
        elif verdict == "reject":
            st["bindings_rejected"] = (st.get("bindings_rejected") or []) + [relentless_binding.binding_hash(p["binding"])]
            st.pop("binding_proposal", None)
        else:
            p["ambiguous"] = {"judge": judge, "why": why[:600], "at": iso(now)}
        store.attempt(item, rec)
        store.learn(item, "- %s binding repair %s by %s: %s" % (iso(now), verdict.upper(), judge, why[:300]))
        store.save(st)
    store.journal({"at": iso(now), "do": "rebind_" + verdict, "item": item, "judge": judge})
    tail = ""
    if verdict == "approve" and st["status"] == "blocked":
        tail = "; the item waits on a ledger block: `rimflow unblock %s` lets it back in line" % item
    return "%s: binding repair %s%s" % (item, verdict.upper(), tail)


def snag(store, item, gen, klass, detail, r, section=None, now=None, wait_hours=0, on=None, blocker=None):
    """`wait_hours`: what stopped the worker is time, not work (a metric's sample filling); no worker starts before then,
    and the wait is no failed approach. The same class again waits even when the worker named no wait, longer each time:
    a worker costs a million tokens to read that nothing has changed, and CLOSE_GATE_ENFORCE_DONE_IS_EARNED paid three."""
    if wait_hours is not None and (not math.isfinite(wait_hours) or wait_hours < 0):
        raise ValueError("--wait-hours must be a finite, non-negative number: %r" % (wait_hours,))
    if SLUG_RX.sub("_", (klass or "snag").lower()).strip("_")[:40] in SUPERVISOR_ENDS:
        raise ValueError("--class %s is the supervisor's verdict, not a worker's snag: name what stopped you" % klass)
    now = time.time() if now is None else now
    with store.lock():
        st = store.load(item)
        _fence(st, item, gen, stage_ok=True)
        if (klass or "").lower() == "binding_repair" and not st.get("binding_proposal"):
            raise ValueError("no binding repair is waiting: propose it first with `rebind` (relentless_binding)")
        if relentless_game.staging(st, gen):    # the supervisor releases the bridge first, then returns the item
            st["game"]["snag"] = {"class": klass, "detail": (detail or "")[:2000], "at": now}
            store.save(st)
            return
        if klass == "owner_call" and section:
            st["gen"] += 1
            st["status"] = "stopping"
            st["stopping_since"] = now
            qid = relentless_answer.question_id(item, gen, now)     # the answer cites it; a tick releases on it
            st["hold"] = {"why": "delegation_policy section 2: %s: %s %s" % (section, (detail or "")[:600],
                                                                            relentless_answer.ask_line(qid)),
                          "kind": "owner_call", "delivered": False, "at": now, "question_id": qid}
            store.attempt(item, {"at": iso(now), "gen": gen, "end": "owner_call", "detail": st["hold"]["why"]})
            store.save(st)
            return
        if (klass or "").lower() == INSTRUMENT:
            if not on or not (detail or "").strip():
                raise ValueError("--class instrument takes the repair item and the evidence: `rimflow namecheck`, `rimflow "
                                 "file <NAME> --for BENCH` (or reuse the open one), then `snag --class instrument --on <NAME> "
                                 "\"<the log line showing the site or instrument, not the work, is broken>\"`")
            if wait_hours:
                raise ValueError("--class instrument waits on its repair item (--on), never on a clock: drop --wait-hours")
            if st.get("diagnose_owed"):     # the explanation names the cause; the snag waits on it
                raise ValueError("explain the ending first (its --cause is the repair item this snag waits --on): "
                                 + relentless_explain.ask("relentless.py", item, gen))
            blocker = "item"
        blk = None if wait_hours else relentless_block.from_snag(klass, detail, r, on, blocker)
        if blk:     # a blocker, not a failed approach: out of the line until the ledger block ends (relentless_block)
            st["gen"] += 1
            st["status"] = "stopping"
            st["stopping_since"] = now
            st["block_pending"] = blk
            if (klass or "").lower() == INSTRUMENT:     # one incident per shared fault; the item rejoins on its close
                relentless_attrib.snag_incident(store, st, blk["on"], detail, now)
            store.attempt(item, {"at": iso(now), "gen": gen, "end": "blocked", "detail": (detail or "")[:600],
                                 "kind": blk["kind"], "on": blk["on"], "class": klass})
            store.learn(item, "- %s gen %d blocked (%s%s): %s" % (iso(now), gen, blk["kind"], " on " + ", ".join(blk["on"])
                                                                  if blk["on"] else "", (detail or "")[:600]))
            store.save(st)
            return
        again = st["failures"].get(SLUG_RX.sub("_", (klass or "snag").lower()).strip("_")[:40] or "snag", 0)
        wait = max(wait_hours or 0, again * r.get("snag_again_wait_h", 0))
        st["not_before"] = now + min(wait, MAX_WAIT_HOURS) * 3600
        fail(store, st, klass, detail, r, now, time_not_work=bool(wait_hours))


def canonical_commit(name):
    """The commit a worker names, as its full id now: a ref that moves later cannot change what was checked."""
    try:
        r = subprocess.run(["git", "rev-parse", "--verify", "--quiet", "%s^{commit}" % name], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as e:
        raise ValueError("cannot resolve %r to a commit: %s" % (name, e))
    out = r.stdout.strip()
    if r.returncode or not re.fullmatch(r"[0-9a-f]{40,64}", out):
        raise ValueError("%r is not a commit in this clone" % (name,))
    return out


CLOSE_RETRY_MAX = 12     # rules.close_retry_max overrides: closing attempts before close_stuck (design rule 6.2)
LANDED_DEPTH = 5000      # origin/main commits searched for a candidate that landed under another hash


def _run_git(cwd, *args, timeout=60, stdin=None):
    try:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout,
                              input=stdin, stdin=None if stdin is not None else subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        return None


def _patch_ids(cwd, *log_args, timeout=120):
    """-> {patch-id: [commit, ...]} newest first, for `git log -p <log_args>` (merges and empty commits carry none)."""
    r = _run_git(cwd, "log", "-p", "--no-color", "--no-textconv", "--no-ext-diff", "--format=commit %H", *log_args, timeout=timeout)
    if not r or r.returncode:
        return {}
    p = _run_git(cwd, "patch-id", "--stable", stdin=r.stdout, timeout=timeout)
    out = {}
    for line in (p.stdout.splitlines() if p and p.returncode == 0 else []):
        f = line.split()
        if len(f) == 2:
            out.setdefault(f[0], []).append(f[1])
    return out


def landing_key(cwd, sha):
    """What survives a rebase of `sha`: its patch-id, subject and author stamp. None when `sha` is not readable here.
    CANDIDATE_SHA_REPAIR_LANDED_UNDER_NEW_HASH: a landing rebases a worker's commit, so its hash dies with the clone."""
    r = _run_git(cwd, "show", "-s", "--format=%s%x00%an <%ae> %at", sha + "^{commit}")
    if not r or r.returncode or "\0" not in r.stdout:
        return None
    subject, author = r.stdout.rstrip("\n").split("\0", 1)
    ids = _patch_ids(cwd, "-1", sha)
    return {"patch_id": next(iter(ids), None), "subject": subject, "author": author}


def find_landed(cwd, key, item, base=None, until=None, since=None, ref="origin/main"):
    """-> (commit, how) on `ref` holding the work of a commit `ref` does not hold, or (None, why). In order: the
    newest commit with the key's subject, author stamp and patch-id; the newest with its patch-id alone (a reworded
    landing); the newest with subject and author when the commit carries no patch (empty); with no key at all (the
    object and its clone are gone), the newest commit since `base` whose subject names `item`, authored between
    `since` (the finishing run's start) and `until` (the finish): a rebase keeps the author date, so this is the tip
    that run had when it finished, never an earlier run's landed half."""
    span = ["%s..%s" % (base, ref)] if base and _ok(_run_git(cwd, "cat-file", "-e", base + "^{commit}")) else [ref]
    span += ["-n", str(LANDED_DEPTH)]       # origin/main took 419 commits in six hours, 2026-11-06
    r = _run_git(cwd, "log", "--format=%H%x00%s%x00%an <%ae> %at", *span)
    rows = [x.split("\0") for x in (r.stdout.splitlines() if _ok(r) else []) if x.count("\0") == 2]
    if key:
        same = [h for h, subject, author in rows if subject == key.get("subject") and author == key.get("author")]
        pid = key.get("patch_id")
        for h in same:
            if not pid or pid in _patch_ids(cwd, "-1", h):
                return h, "patch-id %s" % pid[:12] if pid else "subject and author stamp"
        hit = _patch_ids(cwd, *span).get(pid) if pid else None
        if hit:
            return hit[0], "patch-id %s" % pid[:12]
        return None, "no commit on %s carries its patch-id or its subject and author stamp" % ref
    for h, subject, author in rows:
        try:
            at = int(author.rsplit(" ", 1)[1])
        except (IndexError, ValueError):
            continue
        if re.search(r"(^|[^A-Z0-9_])%s([^A-Z0-9_]|$)" % re.escape(item), subject) and (until is None or at <= until) \
                and (since is None or at >= since):
            return h, "newest commit naming %s authored by the finish" % item
    return None, "no commit on %s since the base names %s" % (ref, item)


def _ok(r):
    return bool(r) and r.returncode == 0


def landed_commit(sha, cwd=None):
    """-> (sha to record, note or None). The worker's sha when origin/main holds it (or origin cannot be asked);
    the landed commit when a landing rebased it onto origin/main under another hash."""
    if not _ok(_run_git(cwd, "fetch", "--quiet", "origin", "main", timeout=180)):
        return sha, None
    if _ok(_run_git(cwd, "merge-base", "--is-ancestor", sha, "origin/main")):
        return sha, None
    found, how = find_landed(cwd, landing_key(cwd, sha), None)
    if not found:
        return sha, None
    return found, "%s is not on origin/main; it landed as %s (%s): recording %s" % (sha[:10], found[:10], how, found[:10])


def ledger_only_refusal(sha, prof, cwd=None):
    """-> the refusal text when `sha` changes ONLY paths the Marker's box replays from the candidate's parent
    (walls.marker.tree_from_parent: the ledger, code_review), else None. Such a commit's change is invisible to the
    checker: change.diff is empty and the ledger reads as before it (OPS_CHURN_DIAGNOSE_STALE_EDEN_EOCX:
    STALE_BLOCKS_UNBLOCK_GATES_ALREADY_OPEN blind-failed twice on ledger-only a8d05bca). A git error refuses nothing."""
    snap = list(prof.get("tree_from_parent") or ())
    if not snap:
        return None
    try:
        r = subprocess.run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", "-m", "--first-parent", sha],
                           cwd=cwd, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode:
        return None
    paths = [p for p in r.stdout.splitlines() if p.strip()]
    under = lambda p, s: p == s.rstrip("/") or p.startswith(s.rstrip("/") + "/")    # noqa: E731
    if not paths or not all(any(under(p, s) for s in snap) for p in paths):
        return None
    return ("%s changes only %s, which the blind checker reads from the candidate's PARENT (walls.marker.tree_from_parent):"
            " it would see an empty change and the ledger as before your events. Land those events, then finish on a LATER"
            " commit that names the item and changes a file outside them (a lesson, a test, the live_proofs line)."
            % (sha[:10], ", ".join(s for s in snap if any(under(p, s) for p in paths))))


REV_EXPR = re.compile(r"[\s/:~^@{}*?\[\\]|\.\.|^-")


def contract_hash(contract):
    """The contract a check is bound to, as one id (design relentless_verdict_identity_design_2026-11-02.md rule 6.1)."""
    return hashlib.sha256(json.dumps(contract or {}, sort_keys=True).encode()).hexdigest()


clock = time.time      # the arrival clock of finish/verdict/help_answer; a selftest rig points it at its fake time


def past_deadline(rec, now):
    """Rule 6.3: a result that arrives after the deadline persisted at its launch is no result, whoever delivers it.
    -> the reason, or None. A record launched before deadlines were persisted carries none and is judged as before."""
    d = (rec or {}).get("deadline")
    if isinstance(d, (int, float)) and now > d:
        return "arrived %d s after its deadline" % (now - d)
    return None


def bind_moved(st):
    """Rule 6.1: -> why the check's verdict no longer judges this candidate (sha, gen or contract moved since its launch),
    or None. A check launched before binding carries no `bind` and is read as before."""
    b = ((st or {}).get("check") or {}).get("bind")
    if not b:
        return None
    now_is = {"sha": (st.get("candidate") or {}).get("sha"), "gen": st.get("gen"), "hash": contract_hash(st.get("contract"))}
    moved = ["%s %s -> %s" % (k, str(b.get(k))[:12], str(now_is[k])[:12]) for k in ("sha", "gen", "hash") if b.get(k) != now_is[k]]
    return ("the check judged another candidate: " + ", ".join(moved)) if moved else None


def finish(store, item, gen, sha, evidence, now=None, root=None):
    """The durable receipt. The result never depends on a notification: the tick finds it here. `root`: the worker's
    tree, where a repair item's incident fixtures are linted for the verdict line (relentless_incident.owed_by)."""
    now = clock() if now is None else now
    with store.lock():
        st = store.load(item)
        _fence(st, item, gen)
        late = past_deadline(st.get("run"), now)
        if late:
            raise Fenced("%s: this run's time is up (%s; run_max_s). Stop now." % (item, late))
        if not st["contract"]:
            raise ValueError("no contract: set it with `contract` before finishing")
        if st.get("diagnose_owed"):
            raise ValueError("the last ending (%s) was read off a live proof or a checker and nobody has explained it: "
                             "read its log, then %s before finishing (a CLASSIFY label is not an explanation)"
                             % (st["diagnose_owed"]["class"], relentless_explain.ask("relentless.py", item, gen)))
        owed = relentless_breakers.warrant_refusal(st) or relentless_incident.owed_by(store, item, root or os.getcwd())
        if owed:
            raise ValueError(owed)
        if not isinstance(sha, str) or REV_EXPR.search(sha) or sha.upper().startswith(("HEAD", "FETCH_HEAD")) or sha in ("main", "master"):
            raise ValueError("sha must be one commit id, not a ref or revision expression that can move: %r" % (sha,))
        owed = (live_owed(root or os.getcwd(), st, item, sha) or proof_text_owed(root or os.getcwd(), item, sha)
                or unlanded_owed(root or os.getcwd()))
        if owed:
            raise ValueError(owed)
        snap, contract, base = contract_hash(st["contract"]), st["contract"], dict(st)
    # RELENTLESS_BUILD_BOXRUN_AT_FINISH: the proof runs in the Marker's box OUTSIDE store.lock (minutes must not freeze a
    # tick), then the lease and the contract are re-fenced before the receipt; a red proof under enforce refuses here
    ran = relentless_boxrun.at_finish(store, item, gen, sha, contract, root or os.getcwd(), rules(), st=base, evidence=evidence)
    with store.lock():
        st = store.load(item)
        _fence(st, item, gen)
        relentless_boxrun.refence(st, snap)
        rec = {"item": item, "gen": gen, "sha": sha, "evidence": evidence, "at": iso(now), "contract": st["contract"],
               "hash": snap}
        if ran:
            rec["boxrun"] = ran
        key = landing_key(root or os.getcwd(), sha)
        if key:     # lets the supervisor find this work if a later landing rebases it (..._LANDED_UNDER_NEW_HASH)
            rec["key"] = key
        store._write(store.receipt_path(item, gen), json.dumps(rec, indent=1, sort_keys=True))
        pilot_sat(st, "finish")
        _take_receipt(store, st, rec, now)


def unlanded(cwd):
    """-> [commit] HEAD holds that origin/main has under no hash (a landing that rebased is matched by patch), or None when
    the clone cannot say (no origin/main, not a git tree): nothing is refused on what cannot be read."""
    r = _run_git(cwd, "rev-list", "--right-only", "--cherry-pick", "--no-merges", "origin/main...HEAD")
    if not r or r.returncode:
        return None
    return r.stdout.split()


def unlanded_owed(cwd):
    """-> why `finish` refuses, or None. GAMELANE_LAND_FIX_SEVEN_STRANDINGS: once `finish` moves the item on (candidate, then
    the game lane, held or blocked) the pre-push fence refuses the old lease, so a commit still unlanded here waits in a
    bundle that only the item's NEXT clone restores, and an item that goes done never gets one: land it first."""
    left = unlanded(cwd)
    if left:
        return ("this clone holds %d commit(s) origin/main does not (%s): land them with ./publish (or drop them) before "
                "finish; after finish your lease can push lessons and ledger lines only" % (len(left), ", ".join(c[:10] for c in left[:5])))
    return None


def state_only_push(toplevel):
    """True when every commit HEAD holds beyond the remotes touches only records (POOL_STATE lessons, POOL_NOISE ledger
    shards, code review, transcripts). A finished worker may still land those: they change no code under check."""
    r = _run_git(toplevel, "rev-list", "HEAD", "--not", "--remotes")
    if not r or r.returncode:
        return False
    for sha in r.stdout.split():
        parents = _run_git(toplevel, "rev-list", "--parents", "-n1", sha)
        files = _run_git(toplevel, "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", sha)
        if not parents or parents.returncode or len(parents.stdout.split()) > 2 or not files or files.returncode:
            return False
        names = [f for f in files.stdout.split("\n") if f]
        if not names or any(not f.startswith(POOL_STATE + POOL_NOISE) for f in names):
            return False
    return True


def live_owed(cwd, st, item, sha):
    """-> why `finish` refuses, or None. The check refuses a sha whose paths need a live line the contract lacks
    (bad_candidate), and that return costs a whole attempt; CONTRACT_LIVE_FIX_MISSED_FLAG_COSTS_RETURNS: say so here,
    while the worker can still add the line (contract --live, the same --proof). The same paths the check reads:
    the commit plus every commit since base naming the item. An unreadable tree refuses nothing (the check still runs)."""
    if (st.get("contract") or {}).get("live"):
        return None
    import live_line
    r = _run_git(cwd, "show", "--format=", "--name-only", "--diff-merges=first-parent", sha)
    if not r or r.returncode:
        return None
    paths = set(x for x in r.stdout.splitlines() if x.strip())
    if st.get("base"):
        r = _run_git(cwd, "log", "--format=", "--name-only", "--diff-merges=first-parent", "--grep=" + item,
                     "%s..%s" % (st["base"], sha))
        if r and not r.returncode:
            paths |= set(x for x in r.stdout.splitlines() if x.strip())
    paths = sorted(paths)
    need = live_line.needs_line(paths)
    if not need and not (item.startswith(ALARM_PREFIXES) and paths and not live_line.prose_only(paths)):
        return None
    return ("%s needs a live line in the contract (%s), so the check would return it: add one first with "
            "`relentless.py contract --item %s --gen %s --proof <the same proof> --live \"<live line>\" --why ...`, then "
            "finish again" % (sha, (need or ["alarm item"])[0], item, st.get("gen")))


def proof_refusals(text, r=None):
    """-> ["<cid>: why"] for every `live-proof` line of a live_proofs text the live lane would refuse to run
    (relentless_live.refused_proof: a `$` or backtick expansion, eval, a brace list, a load or a mutation). A flyer's
    line is the lane's to put down, and a line reading his ledger (OWNER.jsonl) is his look, which the game lane skips
    (owner_looks), so neither is the worker's to rewrite or named here. Pure but for the rules read."""
    import relentless_game
    import relentless_live
    lr = relentless_live.live_rules(rules() if r is None else r)
    out = []
    for cid, proof in sorted(relentless_game.proof_lines(text or "").items()):
        why = relentless_live.refused_proof(lr, "", "", proof)
        if why and not why.startswith(("flyer:", "owner act:")):
            out.append("%s: %s" % (cid, why))
    return out


def proof_text_owed(cwd, item, sha, r=None):
    """-> why `finish` refuses, or None. LIVEPROOF_DOLLAR_FIX_REFUSED_AT_FILING: 9 of 17 live runs that measured nothing
    in one window were a proof line the live gate refuses (`$`, backtick), caught only at game_implemented, after a blind
    check was paid for, or on the live lane itself. The line is read at the finished sha, the bytes the lane will run;
    an unreadable tree or no file refuses nothing (the game phase still gates it)."""
    path = "infrastructure/state/live_proofs/%s.txt" % item
    g = _run_git(cwd, "show", "%s:%s" % (sha, path))
    if not g or g.returncode:
        return None
    bad = proof_refusals(g.stdout, r)
    if not bad:
        return None
    return ("%s at %s holds live-proof lines the live lane will refuse: %s. Write each as a literal command (no `$`, "
            "backtick, eval or brace list; put any computed value inside the proof script), commit, and finish again"
            % (path, sha[:10], "; ".join(bad)))


def _take_receipt(store, st, rec, now):
    st["candidate"] = {"sha": rec["sha"], "gen": rec["gen"], "evidence": rec["evidence"], "at": now}
    if rec.get("key"):
        st["candidate"]["key"] = rec["key"]
    words = relentless_packet.report(rec)
    if words:       # report-only: the packet lint reads the evidence prose and changes nothing (RA_S02)
        store.journal({"at": iso(now), "do": "packet_report", "item": st["item"], "gen": rec["gen"], "words": words})
    st["status"] = "candidate"
    st["last_sha"] = rec["sha"]
    store.attempt(st["item"], {"at": iso(now), "gen": rec["gen"], "end": "finish", "sha": rec["sha"]})
    relentless_breakers.probe_passed(store, st["item"], now)
    store.save(st)


# ---------------------------------------------------------------- calling for help (RW3, design relentless_agent 7)

def failed_approaches(store, item):
    """What was tried and ended in failure, from the record the supervisor wrote, never a worker's say-so."""
    return [a for a in store.attempts(item) if "approach_next" in a and a.get("end") not in NOT_AN_APPROACH]


def help_pending(st):
    return ((st or {}).get("help") or {}).get("status") in ("wanted", "running")


def help_cool_left(st, r, now):
    last = st.get("help_last_at")
    return max(0, last + r["circling"]["help_cool_h"] * 3600 - now) if last is not None else 0


def _want_help(store, st, why, by, now):
    """Any consult uses up the hits so far: a worker's own call and the forced one are not two. `round` counts consults,
    never launch tries: a retry of round one is still round one, and stays with the same vendor."""
    st["help_round"] = st.get("help_round", 0) + 1
    st["help"] = {"status": "wanted", "why": (why or "")[:600], "by": by, "at": now, "tries": 0, "gen": st["gen"],
                  "round": st["help_round"]}
    st["help_last_at"] = now
    st["help_hits_used"] = st.get("circling_hits", 0)
    store.journal({"at": iso(now), "do": "help_wanted", "item": st["item"], "by": by})


def force_help(store, st, r, now):
    """Under the lock; the caller saves. -> True when this call asked for the consult."""
    n = (r.get("circling") or {}).get("help_after_circling")
    if not n or st.get("circling_hits", 0) - st.get("help_hits_used", 0) < n:
        return False
    if help_pending(st) or help_cool_left(st, r, now) or not failed_approaches(store, st["item"]):
        return False
    _want_help(store, st, "forced: %d circling stops" % st["circling_hits"], "tick", now)
    return True


def ask_help(store, item, gen, why, r, now=None):
    """A worker's call, any time. `gen` None is someone outside the lease (an operator): nothing to fence."""
    now = time.time() if now is None else now
    with store.lock():
        st = store.load(item)
        if gen is not None:
            _fence(st, item, gen)
        elif st is None:
            raise ValueError("%s is not enrolled" % item)
        if st["status"] in ENDED:
            raise ValueError("%s is %s" % (item, st["status"]))
        if not failed_approaches(store, item):
            raise ValueError("%s has no failed approach on record: nothing for a fresh eye to read. Fail first." % item)
        if help_pending(st):
            raise ValueError("%s already has a consult %s" % (item, st["help"]["status"]))
        left = help_cool_left(st, r, now)
        if left:
            raise ValueError("%s had a consult; the next in %d min (help_cool_h)" % (item, left // 60 + 1))
        _want_help(store, st, why, "gen %d" % gen if gen is not None else "operator", now)
        if gen is not None:
            st["last_beat"] = now
        store.save(st)


def parse_options(options, r):
    """'idea | the one observation that confirms or kills it', each. A hypothesis with no test is refused."""
    most = r["circling"]["help_options_max"]
    if not options or len(options) > most:
        raise ValueError("give 1 to %d options" % most)
    out = []
    for o in options:
        idea, _, see = o.partition("|")
        if not idea.strip() or not see.strip():
            raise ValueError("an option is 'idea | the one observation that confirms or kills it': %s" % o[:80])
        out.append({"idea": idea.strip()[:600], "observe": see.strip()[:600]})
    return out


def help_vendor(st, r):
    """Design section 7: round one the same model, from round `help_vendor_from_round` on a second vendor (the gpt_consult
    port). -> the agent name to launch. Unset in the rules: always round one's agent."""
    if relentless_attrib.is_diagnose(st):     # an attribution, not a fresh idea: the read-only diagnostician
        return r.get("diagnose_agent") or r["help_agent"]
    n = (r.get("circling") or {}).get("help_vendor_from_round")
    rnd = ((st or {}).get("help") or {}).get("round") or 1
    return VENDOR_AGENT if n and rnd >= n else r["help_agent"]


VENDOR_AGENT = "gpt_consult"
VENDOR_FAST_TRIES, VENDOR_FAST_FAIL_S, VENDOR_RESERVE_S = 3, 90, 90    # reserve: the answer and unit exit
OPTION_RE = re.compile(r"^[ \t]*(?:[-*][ \t]*)?\**OPTION\**[ \t]*\d*[ \t]*[:.)]\**[ \t]*(\S.*)$", re.I | re.M)


def vendor_options(text, r):
    """A second vendor's answer -> the options it gave, each line `OPTION: idea | observation`. Nothing else is read."""
    got = [m.strip().strip("`*").strip() for m in OPTION_RE.findall(text or "")]
    return [o for o in got if all(x.strip() for x in o.partition("|")[::2]) and "|" in o][:r["circling"]["help_options_max"]]


def help_vendor_run(store, item, prompt_file, r, nonce=None, consult=None):
    """The second vendor's unit body: ask through gpt_consult, then answer by the same door a Claude consult uses.
    -> exit code. `consult(prompt_file, out_file, timeout)` -> text is the port, for tests."""
    nonce = nonce or os.environ.get("RELENTLESS_HELP_NONCE")
    if not nonce:
        print("help-vendor: no nonce (RELENTLESS_HELP_NONCE)", file=sys.stderr)
        return 2
    with store.lock():      # a stale or wrong-nonce unit spends no provider call
        h = ((store.load(item) or {}).get("help")) or {}
        if h.get("status") != "running" or h.get("nonce") != nonce or h.get("expired") or h.get("answered_at"):
            raise Fenced("%s: no consult is waiting for that nonce" % item)
    out = prompt_file + ".answer.md"
    consult = consult or gpt_consult
    deadline = time.monotonic() + r["circling"]["help_max_s"] - VENDOR_RESERVE_S     # one bound over every try
    text, got = "", []
    for _ in range(VENDOR_FAST_TRIES):
        left = int(deadline - time.monotonic())
        if left < 60:
            break
        t0 = time.monotonic()
        text = consult(prompt_file, out, left)
        got = vendor_options(text, r)
        if got or text or time.monotonic() - t0 > VENDOR_FAST_FAIL_S:
            break       # only an empty answer inside seconds is retried here: WSL interop's accept4 flake, a known lesson
    if not got:
        print("help-vendor: no OPTION lines in the answer (%d chars): %s" % (len(text or ""), (text or "")[-300:]),
              file=sys.stderr)
        return 3
    help_answer(store, item, nonce, got, r)
    print("help-vendor: %d option(s) answered for %s" % (len(got), item))
    return 0


def gpt_consult(prompt_file, out, timeout):
    """The Consult port's live adapter: src/RimMandrake/Utils/gpt_consult.py beside this file's tree. `timeout` bounds
    the whole call: codex gets 30 s less, so gpt_consult ends it and writes its job before this kill would."""
    tool = os.path.join(HERE, "..", "Utils", "gpt_consult.py")
    try:
        res = subprocess.run([sys.executable, tool, "--prompt-file", prompt_file, "--out", out,
                              "--timeout", str(max(30, timeout - 30))],
                             capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        print("help-vendor: gpt_consult over %d s" % timeout, file=sys.stderr)
        return ""
    print(res.stderr[-2000:], file=sys.stderr)
    if res.returncode:
        print("help-vendor: gpt_consult exit %d" % res.returncode, file=sys.stderr)
    try:
        with open(out, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return res.stdout


def help_answer(store, item, nonce, options, r, now=None):
    """The consult's return. Into the state file at once, so nothing past this line depends on the unit."""
    now = clock() if now is None else now
    got = parse_options(options, r)
    with store.lock():
        st = store.load(item)
        h = (st or {}).get("help") or {}
        if not h or h.get("status") != "running" or h.get("nonce") != nonce or h.get("expired") or h.get("answered_at"):
            raise Fenced("%s: no consult is waiting for that nonce" % item)
        if relentless_attrib.is_diagnose(st):
            raise Fenced("%s: this consult is a diagnosis: answer it with `relentless.py attribute`" % item)
        late = past_deadline(h, now)
        if late:
            raise Fenced("%s: this consult's answer %s" % (item, late))
        h["answered_at"] = now
        st["help_options"] = {"options": got, "at": now, "by_unit": h["run"]["unit"], "vendor": h.get("agent")}
        store.attempt(item, {"at": iso(now), "gen": st["gen"], "help": "answered", "options": len(got),
                             "round": h.get("round"), "agent": h.get("agent")})
        store.save(st)


def cause_fail(store, st, r, now):
    """Under the lock, the check being read: a structured FAIL routed on the causes of its defects
    (CHECKER_VERDICT_BUILD_CAUSE_BEFORE_RETURN; plan design/RimMandrake/relentless_recovery_plan_2026-11-05.md step 5).
    PRODUCT (validated: a control and a citation of the candidate) -> the builder with its strike; MEASUREMENT -> the proof
    road on the same sha, never the code; ENVIRONMENT -> an Operations alarm keyed on the dependency, and the candidate
    waits for its diagnosis; UNKNOWN (an unvalidated product claim included) -> the diagnosis, never a builder.
    -> the cause it was routed on."""
    chk = st["check"] or {}
    sha = st["candidate"]["sha"]
    reasons = chk.get("reasons") or ""
    changed = chk.get("changed")
    if changed is None:
        changed = relentless_wall.changed_paths(chk.get("box"))
    rows = relentless_wall.causes(chk.get("defects"), chk.get("controls"), changed, (st.get("contract") or {}).get("proof"))
    cause = relentless_wall.route(rows)
    st["cause"] = {"route": cause, "rows": rows, "sha": sha, "at": now}
    store.journal({"at": iso(now), "do": "cause_routed", "item": st["item"], "cause": cause, "sha": sha,
                   "causes": [x["acts"] for x in rows]})
    texts = "; ".join("%s: %s" % (x["cause"], x["text"]) for x in rows)[:1600]
    store.learn(st["item"], "- %s gen %d checker FAIL routed %s (%s)" % (iso(now), st["gen"], cause, texts[:600]))
    if cause == relentless_wall.PRODUCT:
        good = [x for x in rows if x["acts"] == relentless_wall.PRODUCT]
        rec = relentless_attrib.record(["PRODUCT"], texts, now, "checker verdict", sha, obligation=good[0]["text"][:600],
                                       observed=reasons[:600],
                                       why_product="control: %s" % "; ".join(chk.get("controls") or [])[:600])
        st["attribution"] = rec
        fail(store, st, "blind_fail", reasons, r, now, attributed=rec)
    elif cause == relentless_wall.MEASUREMENT:
        rec = relentless_attrib.record(["PROOF"], texts, now, "checker verdict", sha)
        st["attribution"] = rec
        fail(store, st, relentless_attrib.PROOF_OWED, "%s (checker: every defect is the measurement's: repair the proof or "
             "its binding on the same sha, not the code)" % texts, r, now, attributed=rec)
    elif cause == relentless_wall.ENVIRONMENT:
        deps = sorted({relentless_wall.dependency(x["text"]) for x in rows if x["acts"] == relentless_wall.ENVIRONMENT})
        for dep in deps:
            store.journal({"at": iso(now), "do": "alarm", "kind": "environment_defect", "item": st["item"],
                           "dependency": dep, "sha": sha, "why": texts[:400]})
        relentless_attrib.withhold(store, st, "blind_fail", "environment (%s): %s" % (", ".join(deps), texts), r, now,
                                   sys.modules[__name__])
        st["wait"].update(cause=relentless_wall.ENVIRONMENT, dependency=deps)
        store.save(st)
    else:
        fail(store, st, "blind_fail", reasons, r, now)      # relentless_attrib.gate: the diagnosis, never a builder
    return cause


QUARANTINE = "quarantine"
QUARANTINE_RETURNS = 2      # returns 2 is the board's "pass 3"


def quarantine_due(st, r, returns, spent):
    """Owner 2026-11-05 (CHECKING_BOUNCE_ENFORCE_QUARANTINE_HOLD): "Please watch carefully for dangerously expensive
    poorly passing items. Quarantine them if they bounce again from Checking." Due when the item came to this verdict at
    pass >= 3 or over its advisory item_spend_limit (the grace his yes bought included)."""
    return returns >= QUARANTINE_RETURNS or spent >= r["item_spend_limit"] + (st.get("spent_grace") or 0)


def quarantine(store, st, word, returns, spent, now):
    """Under the lock, after the Judge's non-PASS verdict was routed as usual (its record, its count): the item is held
    at once, over whatever the routing left (a stopping return settles to held; a hold it set is kept under this one), so
    no builder, consult or re-check starts. Released only by `unhold`, whose CLI demands --owner-said or a ruling.
    -> the Conductor attention line."""
    if st["status"] in ("done", "closing", "retiring"):
        return None
    back = st["status"]
    if back == "stopping":
        back = "blocked" if st.get("block_pending") or st.get("wait") else "queued"
    under = st.get("hold") or None      # a strikes hold fail() set on a stopping return included
    reasons = ((st.get("last_fail") or {}).get("detail") or (st.get("blind") or {}).get("what") or "")[:300]
    why = ("quarantine: bounced from checking at pass %d, %d tokens; the Judge said %s on %s: %s. No build, consult or "
           "check runs until a ruling unholds it" % (returns + 1, spent, word, (st.get("candidate") or {}).get("sha"), reasons))
    st["hold"] = {"why": why[:900], "kind": QUARANTINE, "at": now, "from": "checking", "back": back, "under": under,
                  "verdict": word, "pass": returns + 1, "spent": spent}
    if st["status"] != "stopping":
        st["status"] = "held"
    st.pop("recheck_at", None)
    store.attempt(st["item"], {"at": iso(now), "gen": st["gen"], "hold": QUARANTINE, "said": word, "pass": returns + 1,
                               "spent": spent, "sha": (st.get("candidate") or {}).get("sha")})
    store.save(st)
    return "%s %s. Look: relentless.py show %s; release: relentless.py unhold %s with a ruling" % (
        st["item"], why[:400], st["item"], st["item"])


def verdict(store, item, nonce, word, reasons, now=None, defects=None, unreached=None, strict=True, proposals=None,
            controls=None, changed=None):
    """defects / unreached: the Marker's structured findings (GPT review of 0135b04912). None = an old-format verdict, read
    from its prose by relentless_wall.read_as; a list, even empty, is read by structure. Both go through
    relentless_wall.clean_list, the one normalisation. strict (the CLI, a checker reading the answer) refuses a contradictory
    verdict; not strict (a verdict.json already on disk) records it and lets read_as read it - never a raise every tick."""
    now = clock() if now is None else now
    word = str(word or "").upper()
    if word not in relentless_wall.WORDS:
        raise ValueError("verdict is PASS, WEAK, FAIL or UNMEASURED")
    defects, unreached = relentless_wall.clean_list(defects), relentless_wall.clean_list(unreached)
    if defects is not None or unreached is not None:
        defects, unreached = defects or [], unreached or []
        why = relentless_wall.refusal(word, defects, unreached, controls) if strict else None
        if why:
            raise ValueError(why)
    with store.lock():
        st = store.load(item)
        chk = (st or {}).get("check") or {}
        if not st or st["status"] != "checking" or chk.get("nonce") != nonce or chk.get("expired"):
            raise Fenced("%s: no check is waiting for that nonce" % item)
        if chk.get("verdict") is not None:
            raise Fenced("%s: this check has already given its verdict" % item)
        late = past_deadline(chk, now)
        if late:
            raise Fenced("%s: this check's verdict %s" % (item, late))
        chk["verdict"] = word
        chk["reasons"] = (reasons or "")[:4000]
        if defects is not None:
            chk["defects"], chk["unreached"] = defects, unreached
            chk["controls"] = relentless_wall.clean_list(controls) or []
        if changed is not None:         # the candidate's diff paths, read from the box while it stands (cause validation)
            chk["changed"] = list(changed)[:200]
        if word == "UNMEASURED" and relentless_wall.clean_list(proposals):     # the Judge's own reach repair
            chk["proposals"] = relentless_wall.clean_list(proposals)[:relentless_reachfix.PROPOSE_MAX]
        chk["verdict_at"] = now
        store.save(st)
        store._append(store.p("shadow.jsonl"), json.dumps({      # shadow: recorded beside the verdict, read by nothing that acts
            "rule": relentless_wall.SHADOW, "item": item, "nonce": nonce, "at": now, "word": word,
            "shadow": relentless_wall.narrow_word(word, reasons)}, sort_keys=True))


def shadow_tally(store, rule=None):
    """-> counts of shadowed verdicts under one shadow rule: agree, differ, untagged, and the differing rows."""
    rule = rule or relentless_wall.SHADOW
    rows = []
    try:
        with open(store.p("shadow.jsonl"), encoding="utf-8") as f:
            for ln in f:
                try:
                    r = json.loads(ln)
                except ValueError:
                    continue
                if r.get("rule") == rule:
                    rows.append(r)
    except FileNotFoundError:
        pass
    untagged = sum(r["shadow"] == "UNTAGGED" for r in rows)
    differ = [r for r in rows if r["shadow"] not in (r["word"], "UNTAGGED")]
    return {"rule": rule, "verdicts": len(rows), "weak": sum(r["word"] == "WEAK" for r in rows), "untagged": untagged,
            "differ": len(differ), "agree": len(rows) - len(differ) - untagged,
            "differing": [(r["item"], r["word"], r["shadow"]) for r in differ]}


def weak_reads_pass(st, store=None):
    """-> True when the WEAK that set proof_only reads PASS under the live rule (acted_weak; owner by card 2026-11-03,
    "Narrow it now": GAP:OTHER is a PASS). Such a proof_only stands on a verdict that no longer holds. An older state has
    no `weak` on it: the proof_weak attempt at the held sha is read instead. A CONTRACT binding hold is never a WEAK."""
    held = st.get("proof_only") or {}
    if not held or held.get("binding"):
        return False
    d = held.get("weak")
    if d is None and store is not None:
        for a in reversed(store.attempts(st["item"])):
            if a.get("end") in ("proof_weak", relentless_attrib.PROOF_OWED) and a.get("sha") == held.get("sha"):
                d = a.get("detail") if a.get("end") == "proof_weak" else None     # the NEWEST hold-setting end
                break       # an older proof_weak never speaks for a later PROOF_OWED (Codex r3)
    return d is not None and relentless_wall.acted_weak("WEAK", d) == "PASS"


def proof_gate(fx, r, st, c):
    """-> (class, why) when a proof-only worker's candidate may not spend a Marker, else (None, None). A candidate
    that moved no proof changed nothing the check could read; one that moved code is the rework a WEAK forbids."""
    held = st.get("proof_only")
    if not held or weak_reads_pass(st):
        return None, None       # no WEAK, or one the live rule reads PASS: the Marker reads the sha afresh
    if c["sha"] == held["sha"] and held.get("binding"):
        return None, None       # a CONTRACT repair: the same code is validated again against the repaired binding
    bare = lambda k: {x: y for x, y in (k or {}).items() if x not in ("by_gen", "why")}     # noqa: E731  bookkeeping
    if c["sha"] == held["sha"]:
        if "contract" in held and bare(held["contract"]) != bare(st["contract"]):
            return None, None   # a contract-only proof repair: the checker runs the changed proof on the same code, as it
            # would on an empty commit carrying the same repair (Codex r4 part0 #2)
        return "proof_unchanged", "%s is the sha the proof was found weak at: no proof moved" % c["sha"]
    k = st["contract"] or {}
    named = set(re.split(r"[\s'\"=:,;()]+", " ".join([k.get("proof") or "", k.get("live") or ""]
                                                     + relentless_wall.offbox_cmds(k))))     # the commands, never the `why` prose
    named = named | {x[2:] for x in named if x.startswith("./")}
    # a named path is a proof asset only when the weak sha did not hold it: a proof script the proof-only worker wrote.
    # One the product already had is the code under test, and a proof-only worker may re-point the contract at any file
    # (Codex review, RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN #1). An unanswerable existence reads as existed: refused.
    moved = fx.changed(held["sha"], c["sha"], st["item"])
    if not moved and "contract" in held and bare(held["contract"]) == bare(st["contract"]) and not held.get("binding"):
        # an empty commit above the weak sha moved no proof and no contract (Codex #2): the same proof, read again
        return "proof_unchanged", "%s moves no file and the contract is the one found weak: no proof moved" % c["sha"]
    rework = [p for p in moved
              if not any(re.search(x, p) for x in r["proof_paths"])
              and (p not in named or fx.existed(held["sha"], p) is not False)]
    if rework:
        return "proof_rework", "proof-only worker moved code: %s" % ", ".join(rework[:10])
    return None, None


def fence_check(store, item, gen):
    """-> None when this generation may push, else why not. A generation in candidate or later has finished: the
    worker's unit is on its way out, so it may no longer land anything."""
    st = store.load(item)
    if st is None:
        return None if not item else "%s is not enrolled" % item
    if st["gen"] != gen or st["status"] != "running":
        return "%s: lease gen %d is gone (now gen %d, %s)" % (item, gen, st["gen"], st["status"])
    return None


def hook_fence(toplevel, store=None):
    """pre-push. No marker file in .git: not a relentless clone, nothing to say. A marker there but unreadable is a
    relentless clone whose lease nobody can name: it fails closed."""
    try:
        gd = os.path.join(toplevel, ".git")
        if os.path.isfile(gd):      # a linked worktree or submodule: `.git` names its git dir (Codex r5 part1 #3)
            with open(gd, encoding="utf-8") as f:
                line = f.read().strip()
            if not line.startswith("gitdir:"):
                raise ValueError(".git file names no gitdir")
            gd = os.path.join(toplevel, line[len("gitdir:"):].strip())
        with open(os.path.join(gd, "relentless.json"), encoding="utf-8") as f:
            m = json.load(f)
        item, mark = m["item"], int(m["gen"])
        gen = os.environ.get("RELENTLESS_GEN")     # set at launch, so a resumed old session cannot read the new marker
        gen = int(gen) if gen else mark
    except FileNotFoundError:
        return None
    except (OSError, ValueError, KeyError, TypeError) as e:
        return "fence marker unreadable, no push: %s" % str(e)[:120]
    store = store or Store()
    why = fence_check(store, item, gen)
    if why:     # GAMELANE_LAND_FIX_SEVEN_STRANDINGS: the generation that finished may still land its trailing records
        st = store.load(item)
        if st is not None and st["gen"] == gen and state_only_push(toplevel):
            return None
    return why


def _conductor_carried(argv):
    """True when argv cites --per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM with a non-empty --why."""
    def flag(name):
        for i, a in enumerate(argv):
            if a == name and i + 1 < len(argv):
                return argv[i + 1]
            if a.startswith(name + "="):
                return a.split("=", 1)[1]
        return None
    return (flag("--per-ruling") or "").strip() == "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM" and \
        bool((flag("--why") or "").strip())


def guard(verb, item, argv, env=None, store=None):
    """rimflow calls this. A leased item's ledger state belongs to the supervisor; his own word always passes.
    -> None, or why not."""
    env = os.environ if env is None else env
    if verb not in GUARDED_VERBS or not item or env.get("RELENTLESS_SUPERVISOR") == "1":
        return None
    if any(a == "--owner-said" or a.startswith("--owner-said=") for a in argv):
        return None
    if _conductor_carried(argv):             # the Conductor speaks with his authority (CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM)
        return None
    if store is None and not os.path.isdir(os.path.join(root(), "store")):
        return None
    st = (store or Store()).load(item)
    if st and st["status"] in LEASED:
        return ("%s is carried by relentless (gen %d, %s). `%s` belongs to its supervisor; a worker reports with "
                "relentless.py, and the owner's word (--owner-said) always passes." % (item, st["gen"], st["status"],
                                                                                       verb))
    return None


def _conductor_authority():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Utils"))
    import conductor_authority
    return conductor_authority


MANUAL_HOLD = "manual"      # a person's hold by `relentless.py hold`: the seat's own act, never routed back to it
HOLD_FROM = ("queued", "blocked", "candidate", "running")
HOLD_REFUSED = {"checking": "a check is running: hold it after its verdict",
                "stopping": "its run is settling: hold it once it reads queued, held or blocked",
                "closing": "it is closing: drop it on the ledger instead",
                "retiring": "it is retiring: the ledger already ended it",
                relentless_game.GAME: "it is in its game phase, holding the bridge lane: let the phase settle, then hold"}


def hold(store, item, said, now=None):
    """The Conductor's or Operations' hold (RELENTLESS_HOLD_BUILD_A_VERB_FOR_CONDUCTOR): out of the line, no worker, no
    re-check, until `unhold`. A candidate keeps its candidate (sha, evidence, contract): unhold sends that same sha to its
    check again, never a new builder. A running item is fenced (gen moves, so its worker's next report is refused); the
    tick's `stopping` step stops the run and settles it to held. No strike, no failed approach: the hold is a person's, not the item's fault.
    Delivered at once: the seat that held it needs no ledger note telling it so."""
    now = time.time() if now is None else now
    if not (said or "").strip():
        raise ValueError("hold needs a why")
    with store.lock():
        st = store.load(item)
        if not st:
            raise ValueError("%s is not in the Relentless store" % item)
        if st["status"] == "held":
            raise ValueError("%s is held already (%s): %s" % (item, (st.get("hold") or {}).get("kind"),
                                                              ((st.get("hold") or {}).get("why") or "")[:200]))
        if st["status"] in HOLD_REFUSED:
            raise ValueError("%s is %s: %s" % (item, st["status"], HOLD_REFUSED[st["status"]]))
        if st["status"] not in HOLD_FROM:
            raise ValueError("%s is %s, not open: nothing to hold" % (item, st["status"]))
        was = st["status"]
        back = "candidate" if was == "candidate" and (st.get("candidate") or {}).get("sha") else \
            "blocked" if was == "blocked" else "queued"     # a blocked item keeps its blocker (Codex r5 part1 #2)
        st["hold"] = {"why": ("hold: %s" % said)[:900], "kind": MANUAL_HOLD, "delivered": True, "routed": SEAT_QUEUE,
                      "at": now, "from": was, "back": back}
        if was == "running":
            st["gen"] += 1
            st["status"] = "stopping"
            st["stopping_since"] = now
        else:
            st["status"] = "held"
        st.pop("recheck_at", None)
        store.attempt(item, {"at": iso(now), "gen": st["gen"], "end": "hold", "said": said, "from": was})
        store.save(st)
        return was


def unhold(store, item, said, now=None, offbox=None):
    """`offbox`: the repair of an unmeasured hold from outside: supervisor adapter names (never commands) to run beyond the
    Marker's wall, added to the contract (the item has no worker to add them). A free-text entry left by an older contract
    is dropped here: it would be refused at run time anyway."""
    now = time.time() if now is None else now
    with store.lock():
        st = store.load(item)
        if not st or st["status"] != "held":
            raise ValueError("%s is not held" % item)
        if offbox:
            if not st.get("contract"):
                raise ValueError("%s has no contract to add --offbox to" % item)
            have = [x for x in relentless_wall.offbox_cmds(st["contract"]) if x in relentless_wall.adapters(rules())]
            cmds = relentless_wall.check_offbox_names(have + [x for x in offbox if x not in have], rules())
            st["contract"]["offbox"] = cmds
            store.attempt(item, {"at": iso(now), "contract": st["contract"], "said": said})
        if st["hold"].get("kind") == QUARANTINE:
            q = st["hold"]
            store.attempt(item, {"at": iso(now), "end": "unquarantine", "said": said, "pass": q.get("pass")})
            if q.get("under"):      # the hold the verdict's routing set is released as its own kind would be
                st["hold"] = q["under"]
            else:
                st["hold"] = None
                st["returned_at"] = now
                st["status"] = q.get("back") or "queued"
                if st["status"] == "queued":
                    st["spent_grace"] = st["spent"]
                store.attempt(item, {"at": iso(now), "end": "unhold", "said": said, "to": st["status"]})
                store.save(st)
                return
        if st["hold"].get("kind") == "proof_weak":
            for k in PROOF_ENDS:
                st["failures"].pop(k, None)
        elif st["hold"].get("kind") == "strikes":      # his yes is a fresh count; another full ladder holds again
            st["failures"] = {}
            st["total_at_change"] = st["total_failures"]
        elif st["hold"].get("kind") == "signature":    # his hypothesis is the change: the signature counts from here
            st["sig_since"] = len(store.attempts(item))
        elif st["hold"].get("kind") == "start_refused":    # what refused is fixed, or its wait starts over
            st.pop("start_refusals", None)
            st.pop("start_again_at", None)
        if st["hold"].get("kind") == MANUAL_HOLD and st["hold"].get("back") == "blocked" \
                and (st.get("block_pending") or st.get("wait")):
            # a person's hold of a blocked item lifts to the same block: its blocker still stands (relentless_block)
            st["hold"] = None
            st["returned_at"] = now
            st["status"] = "blocked"
            store.attempt(item, {"at": iso(now), "end": "unhold", "said": said, "to": "blocked"})
            store.save(st)
            return
        if st["hold"].get("kind") == MANUAL_HOLD and st["hold"].get("back") == "candidate" \
                and (st.get("candidate") or {}).get("sha"):
            # a person's hold of a candidate lifts to the same candidate: its check runs, no worker is sent
            st["hold"] = None
            st["returned_at"] = now
            st["status"] = "candidate"
            store.attempt(item, {"at": iso(now), "end": "unhold", "said": said, "to": "candidate"})
            store.save(st)
            return
        if st["hold"].get("kind") == relentless_attrib.WAIT_ATTRIB and (st.get("wait") or {}).get("sha"):
            # a person lifted an unattributed failure: the SAME sha is validated again, never a new builder
            st["hold"] = None
            st["returned_at"] = now
            relentless_attrib.resume(store, st, now, "unhold: %s" % said)
            store.attempt(item, {"at": iso(now), "end": "unhold", "said": said, "to": st["status"]})
            store.save(st)
            return
        game_back = (st["hold"].get("kind") == "game" and (st.get("game") or {}).get("sha")
                     and not relentless_game.flyer_hold(st["hold"].get("why")))
        blind_back = st["hold"].get("kind") == "unmeasured" or (      # a WEAK the live rule now reads as PASS: recheck it
            st["hold"].get("kind") == "proof_weak" and (st.get("last_fail") or {}).get("class") == "proof_weak"
            and relentless_wall.acted_weak("WEAK", (st.get("last_fail") or {}).get("detail")) == "PASS")
        if weak_reads_pass(st, store):      # whatever the hold kind (proof_unchanged since, a churn hold): the WEAK is void
            st["proof_only"] = None
            blind_back = blind_back or (st.get("candidate") or {}).get("sha") is not None
        was_his = hold_is_his(st["hold"])
        if st["hold"].get("reach") and st.get("contract") and not relentless_wall.offbox_cmds(st["contract"]):
            st["contract"]["reach_ok"] = ("unhold: %s" % said)[:400]    # the lift is the why; else it holds again next tick
        st["hold"] = None
        st["returned_at"] = now
        if game_back:       # a game hold back to its game phase, not a new worker: the offline proof stands on its sha
            st["status"] = relentless_game.GAME
            st["game"].update(phase="prove", stages=0, retry_at=None, ready=None, snag=None)
            st.pop("put_down", None)
            store.attempt(item, {"at": iso(now), "end": "unhold", "said": said, "to": "game"})
            store.save(st)
            return
        if blind_back and (st.get("candidate") or {}).get("sha"):
            # the box is repaired or the contract can now measure: the same sha is checked again, no worker is sent
            st["status"] = "candidate"
            st["blind"] = None
            st.pop("recheck_at", None)
            store.attempt(item, {"at": iso(now), "end": "unhold", "said": said, "to": "candidate"})
            store.save(st)
            return
        st["status"] = "queued"
        st["spent_grace"] = st["spent"]         # his yes buys another full limit from here
        st["needs_back"] = was_his      # a tooling hold never set needs=owner, and a built item keeps its derived needs
        store.attempt(item, {"at": iso(now), "end": "unhold", "said": said})
        store.save(st)


def no_room_hold(st):
    """An attribution hold whose diagnostic consult never started for lack of room: no diagnosis was tried, so nothing
    a seat must decide. The tick re-asks the diagnostician (RELENTLESS_ATTRIB_FIX_CONSULT_NO_ROOM_HOLDS)."""
    h = (st or {}).get("help") or {}
    return (st or {}).get("status") == "held" and ((st.get("hold") or {}).get("kind") == relentless_attrib.WAIT_ATTRIB
            and h.get("mode") == relentless_attrib.DIAGNOSE and (h.get("end") or "").startswith("no room in ")
            and ((st.get("wait") or {}).get("kind") == relentless_attrib.WAIT_ATTRIB) and (st.get("wait") or {}).get("sha")
            and not help_pending(st))


def rediagnose(store, item, said, now=None, r=None):
    """An `attribution` hold whose diagnostic consult failed (no room, the account, no answer): run the consult again.
    `unhold` re-validates the same sha, which can only say again what it said; this asks the diagnostician once more.
    The candidate and its wait stay exactly as they were (RELENTLESS_RESUME_BUILD_ACCOUNT_LOST_RUNS)."""
    now = time.time() if now is None else now
    with store.lock():
        st = store.load(item)
        if not st or st["status"] != "held" or (st.get("hold") or {}).get("kind") != relentless_attrib.WAIT_ATTRIB:
            raise ValueError("%s is not held for an attribution" % item)
        w = st.get("wait") or {}
        if w.get("kind") != relentless_attrib.WAIT_ATTRIB or not w.get("sha"):
            raise ValueError("%s has no attribution wait to diagnose: unhold it instead" % item)
        if not (r or rules()).get("circling"):
            raise ValueError("no consult machinery (rules.circling unset)")
        if help_pending(st):
            raise ValueError("%s already has a consult out" % item)
        st["hold"] = None
        st["status"] = "blocked"
        relentless_attrib.want(store, st, now)
        store.attempt(item, {"at": iso(now), "end": "rediagnose", "said": said, "sha": w["sha"]})
        store.save(st)


# ---------------------------------------------------------------- what the world does (the selftest plants these)

def refusal_words(r, cap=300):
    """A ledger refusal, its reason kept. The gate's reason is its FIRST line and the rest is advice, so a tail cut kept only
    the advice: 53 refused starts of EGROWTH_SWELL_DECIDE_FLIP_OR_GROAN read as a wrong prose file when its first line said
    "BENCH may not `start` it, it belongs to OWNER". A traceback ends in its reason, so the tail stays beside the head."""
    out = (r.stderr or r.stdout or "").strip()
    if len(out) <= cap:
        return out
    head = out.splitlines()[0][:cap // 2]
    return "%s ... %s" % (head, out[-(cap - len(head) - 5):])


def close_why(out):
    """The gate's reasons are at the top, but the caller finds a refusal by its words: keep them in the cut."""
    if "has not earned its close" in out:
        return (out if "has not earned its close" in out[:560] else "has not earned its close: " + out)[:600]
    return out[-400:]


def filed_needs(it, evs):
    """The needs people gave this item, the supervisor's own writes stepped over: a game item (bridge, game-up, deploy) is
    in the pool for that reason, and a lift that wrote offline lost it. That older write is stepped over too."""
    for i in reversed(getattr(it, "history", None) or []):
        e = evs[i] if 0 <= i < len(evs) else {}
        if e.get("event") == "needs":
            if e.get("why") != SUPERVISOR_WHY:
                return e.get("to")
        elif e.get("event") in ("file", "spawn", "implemented") and e.get("needs"):
            return e["needs"]
    return "offline"       # model's default for a filing that names none


def run_bounded(name, adapter, timeout, cap=None):
    """Run an offbox adapter's argv with its output bounded in memory and time. -> {cmd, exit, out, at}."""
    import selectors
    import tempfile
    cap = cap or relentless_wall.OFFBOX_OUT_MAX
    at = time.time()
    shown = "%s: %s" % (name, adapter.get("what") or " ".join(adapter.get("argv") or []))
    env = {k: v for k, v in os.environ.items() if k != "RELENTLESS_ROOT"}
    env["PATH"] = windows_path(env.get("PATH", ""))
    kept, why = bytearray(), None
    with tempfile.TemporaryDirectory(prefix="offbox-") as cwd:
        try:
            p = subprocess.Popen(adapter["argv"], cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, start_new_session=True)
        except (OSError, KeyError, TypeError) as e:
            return {"cmd": shown, "exit": "could not start: %s" % e, "out": "", "at": at}
        sel = selectors.DefaultSelector()
        sel.register(p.stdout, selectors.EVENT_READ)
        end = at + max(1, timeout)
        try:
            while True:
                left = end - time.time()
                if left <= 0:
                    why = "timeout after %d s" % timeout
                    break
                if not sel.select(min(left, 1.0)):
                    continue
                chunk = os.read(p.stdout.fileno(), 65536)
                if not chunk:
                    break
                kept += chunk[:cap + 1 - len(kept)]
                if len(kept) > cap:
                    why = "output over %d bytes, killed" % cap
                    break
        finally:
            sel.close()
            p.stdout.close()
            code = None
            if not why:         # EOF: the leader is ending - but only inside what is left of the shared deadline
                try:
                    code = p.wait(timeout=max(0.0, end - time.time()))
                except subprocess.TimeoutExpired:
                    why = "timeout after %d s" % timeout
            try:                # always: a helper the adapter left behind (its own stdio) dies with the group
                os.killpg(p.pid, 9)
            except OSError:
                pass
            if code is None:
                code = p.wait()
    return {"cmd": shown, "exit": why or code, "out": bytes(kept[:cap]).decode("utf-8", "replace"), "at": at}


def offbox_readings(fx, contract, r, values=None):
    """Every reading a check's contract names, sharing one deadline (offbox_max_s). A name that is not a supervisor adapter
    (an older free-text contract) is refused, never run. `values`: the supervisor's {sha}/{repo} for adapters that name them
    (relentless_wall.fill_argv); an adapter whose slots cannot be filled is reported, never run half-filled."""
    known = relentless_wall.adapters(r)
    end = time.time() + r.get("offbox_max_s", 120)
    out = []
    for name in relentless_wall.offbox_cmds(contract)[:relentless_wall.OFFBOX_MAX]:
        left = int(end - time.time())
        if name not in known:
            out.append({"cmd": str(name)[:200], "exit": "refused: not a supervisor offbox adapter, not run", "out": "",
                        "at": time.time()})
        elif left <= 0:
            out.append({"cmd": name, "exit": "not run: the check's offbox time was spent", "out": "", "at": time.time()})
        else:
            argv, why = relentless_wall.fill_argv(known[name]["argv"], values)
            if why:
                out.append({"cmd": "%s: %s" % (name, known[name].get("what") or ""), "exit": why, "out": "",
                            "at": time.time()})
            else:
                out.append(fx.run_offbox(name, dict(known[name], argv=argv), left))
    return out


# What `rimflow close --sha` calls no work (cli._LEDGER_ONLY, kept equal by selftest_relentless_nocode_close.py), and what a
# work-sha lookup also skips: a review mark is bookkeeping too, never the commit that did the work.
LEDGER_ONLY = ("infrastructure/state/ledger/", "infrastructure/state/items/", "infrastructure/state/queue/")
BOOKKEEPING = LEDGER_ONLY + ("infrastructure/state/code_review/",)
WORK_SHA_DEPTH = 60       # commits naming the item, newest first, read under the candidate


class Effects(relentless_game.GameFx):
    """The real one. Every method here blocks, so none is called under the store lock."""

    def __init__(self, r, store):
        self.r = r
        self.store = store
        self.owner_pause_rule = owner_pause_rule()     # his pipeline-only switch, read once a tick (owner_pause)
        self.base = store.root
        self.books = os.path.join(self.base, "books")
        self._ledger = None
        self._budget = self._helpers = NOT_READ
        self.bounce = set()
        self.marked = set()
        import role_launch as RL
        self.RL = RL

    # the ledger, through the books clone
    def rimflow(self, *args, timeout=60, seat=None):
        env = dict(os.environ, RIMFLOW_SEAT=seat or self.r["seat"], AGENT_SEAT=seat or self.r["seat"],
                   RIMFLOW_BRIDGE_SEAT=BRIDGE_HOLDER,
                   RELENTLESS_SUPERVISOR="1", CLAUDE_PROJECT_DIR=self.books)
        return subprocess.run(["python3", os.path.join(self.books, "src/RimMandrake/rimflow/cli.py"), *args],
                              cwd=self.books, env=env, capture_output=True, text=True, timeout=timeout,
                              stdin=subprocess.DEVNULL)

    def git(self, cwd, *args, timeout=120):
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout,
                              stdin=subprocess.DEVNULL)

    def sync(self):
        """The engine runs from books, so a clone that cannot move freezes the engine. -> None, or why it is behind.
        --ff-only fails without a word on one rimflow-moved item file or one landed ledger commit: 15 hours, 2026-11-01."""
        self._ledger = None
        self._budget = self._helpers = NOT_READ
        try:
            got = self.git(self.books, "fetch", "--quiet", "origin")
            if got.returncode:      # every check below reads origin/main: an old one passes them all and says nothing
                return "books cannot fetch: %s" % got.stderr[-300:]
            why = self.ignored_collision()
            if why:
                return why
            with self.append_dirs_locked(), self.shards_locked():   # as level_books: no code_review/art append either
                self.git(self.books, "merge", "--ff-only", "--quiet", "origin/main")    # while git replaces them
            return self.level_books()
        except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as e:
            return "books cannot level: %s" % str(e)[:300]

    @contextlib.contextmanager
    def shards_locked(self, extra=()):
        """Every ledger shard in books held under the flock model.append takes, while git replaces them: an event lands
        before git checks the file (git then refuses, the event stays) or after (model.append finds its inode moved and
        reopens the new file), never in between; the directory lock keeps a new shard from being created meanwhile.
        `extra`: books-relative shards outside the ledger held the same way (their writers flock and re-check the inode).
        Not re-entrant: a flock from a second open file blocks this process."""
        fds = []
        with self.ledger_dir_locked():
            try:
                for p in sorted(glob.glob(os.path.join(self.books, LEDGER_DIR, "*.jsonl"))) + \
                        [os.path.join(self.books, x) for x in extra]:
                    try:
                        fd = os.open(p, os.O_RDONLY)
                    except FileNotFoundError:
                        continue
                    fds.append(fd)
                    fcntl.flock(fd, fcntl.LOCK_EX)
                yield
            finally:
                for fd in fds:
                    os.close(fd)

    @contextlib.contextmanager
    def ledger_dir_locked(self):
        """The ledger dir EXCLUSIVE: model.append holds it SHARED for each append, so no shard is created or written
        meanwhile. Not re-entrant (a second flock on the dir from this process blocks)."""
        d = os.path.join(self.books, LEDGER_DIR)
        fd = os.open(d, os.O_RDONLY) if os.path.isdir(d) else None
        try:
            if fd is not None:
                fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            if fd is not None:
                os.close(fd)

    def ignored_collision(self):
        """-> why, when origin newly tracks a path the clone holds as an IGNORED file with other bytes. Neither a merge
        nor `reset --keep` protects it and `status` cannot see it, so the check is the only thing between it and loss."""
        new = self.git_ok(self.books, "diff", "--name-only", "--no-renames", "--diff-filter=A", "-z", "HEAD", "origin/main").split("\0")
        for p in filter(None, new):
            src = os.path.join(self.books, p)
            parts = p.split("/")
            for q in ("/".join(parts[:i]) for i in range(1, len(parts))):       # a file (or a link, r5 #14) where origin wants a folder
                at = os.path.join(self.books, q)
                if os.path.lexists(at) and (os.path.islink(at) or not os.path.isdir(at)) and \
                        self.git(self.books, "ls-files", "--error-unmatch", "--", q).returncode != 0:
                    return "books behind: ignored file %s stands where origin now tracks %s" % (q, p)
            if os.path.isdir(src) and not os.path.islink(src):                  # a folder where origin wants a file
                if self.git_ok(self.books, "ls-files", "--others", "-z", "--", p).strip("\0"):
                    return "books behind: ignored files under %s stand where origin now tracks a file" % p
                continue
            if not os.path.lexists(src) or self.git(self.books, "ls-files", "--error-unmatch", "--", p).returncode == 0:
                continue
            link = os.path.islink(src)      # dangling or not, its bytes are its target string
            if not link and not os.path.isfile(src):
                return "books behind: ignored %s is no file and origin now tracks a file there" % p
            if link:
                here = os.fsencode(os.readlink(src))
            else:
                with open(src, "rb") as f:
                    here = f.read()
            there = subprocess.run(["git", "-C", self.books, "show", "origin/main:" + p], capture_output=True,
                                   check=True, timeout=60).stdout
            mode = self.git_ok(self.books, "ls-tree", "origin/main", "--", p).split(" ")[0]
            if here != there or link != (mode == "120000"):
                return "books behind: ignored file %s differs from what origin now tracks there" % p
        return None

    def drop_stray_untracked(self, rows):
        """-> rows without the untracked files outside the books' derived dirs that origin/main does not track. A run
        started from the books clone writes a new report beside its script (validation_triplet_*, rail_walk_result_*, ...);
        a fast-forward cannot touch a path origin does not track, so each stays where it is. Naming them prefix by prefix
        let the class come back with every new runner (OPS_JAM_CLASS_FIX_AGAIN_HJWN). An untracked file at a path origin
        now tracks stays in the rows and refuses: the level would overwrite it."""
        loose = [p for st, p in rows if st == "??" and not p.startswith(BOOKS_DERIVED)]
        if not loose:
            return rows
        tracked = set()
        for i in range(0, len(loose), 200):
            tracked |= set(self.git_ok(self.books, "ls-tree", "-r", "-z", "--name-only", "origin/main", "--",
                                       *loose[i:i + 200]).split("\0"))
        loose = set(loose) - tracked
        return [(st, p) for st, p in rows if not (st == "??" and p in loose)]

    def shuffled_shards(self, rows):
        """-> the tracked *.jsonl outside the ledger dir whose lines are HEAD's lines in another order. Landing replays
        the append-only shards (code_review, art) with merge=union, which reorders them; nothing is lost, so it is no
        dirt. Set-equal multisets only: one added, dropped or changed line keeps the file alien. -> {path: the bytes
        compared}, so the restore can see a line appended after this look."""
        out = {}
        for st, p in rows:
            if not p.endswith(".jsonl") or p.startswith(BOOKS_DERIVED) or st.strip() != "M":
                continue
            if os.path.dirname(p) + "/" not in APPEND_ONLY_DIRS:     # only a merge=union shard's order is free (r5 #13)
                continue
            try:
                with open(os.path.join(self.books, p), "rb") as f:
                    raw = f.read()
                here = raw.splitlines()
                there = subprocess.run(["git", "-C", self.books, "show", "HEAD:" + p], capture_output=True,
                                       check=True, timeout=60).stdout.splitlines()
            except (OSError, subprocess.SubprocessError):
                continue
            if sorted(here) == sorted(there):
                out[p] = raw
        return out

    def level_books(self):
        """Behind origin: level the clone when all it holds is ledger already landed and item files rimflow rewrites."""
        behind = self.git_ok(self.books, "rev-list", "--count", "HEAD..origin/main").strip()
        if behind in ("0", ""):
            return None
        out = self.git_ok(self.books, "status", "--porcelain", "--no-renames", "-z", "--untracked-files=all")
        rows = [(x[:2], x[3:]) for x in out.split("\0") if x]
        left = relentless_books_left.moved_rows(self.books, rows, BOOKS_LEFT_IN_PLACE)  # origin moved them: set aside
        rows = [(s, p) for s, p in rows if not p.startswith(BOOKS_LEFT_IN_PLACE)]
        rows = self.drop_stray_untracked(rows)
        staged = self.git_ok(self.books, "diff", "--cached", "--name-only").split()
        if staged:      # the index is nobody's projection, and the checks below read the working tree
            return "books %s behind: staged: %s" % (behind, ", ".join(staged[:5]))
        shuffled = self.shuffled_shards(rows)
        alien =[p for _s, p in rows if not p.startswith(BOOKS_DERIVED) and p not in shuffled and p not in BOOKS_RUN_ARTEFACTS]
        if alien:
            return "books %s behind: dirty outside the ledger: %s" % (behind, ", ".join(alien[:5]))
        changed = self.git_ok(self.books, "diff", "--name-only", "origin/main...HEAD").split()
        alien = [p for p in changed if not p.startswith(BOOKS_DERIVED)]
        if alien:
            return "books %s behind: own commits outside the ledger: %s" % (behind, ", ".join(alien[:5]))
        read = {}
        for p in sorted({p for p in changed if p.startswith(LEDGER_DIR)} | {p for _s, p in rows if p.startswith(LEDGER_DIR)}):
            if not os.path.isfile(os.path.join(self.books, p)):     # a deleted shard: refused by name, before anything
                return "books %s behind: ledger shard %s is deleted" % (behind, p)      # moves (Codex #5)
            with open(os.path.join(self.books, p), "rb") as f:
                read[p] = f.read()
            lost = set(read[p].decode("utf-8").splitlines()) - set(self.git_ok(self.books, "show", "origin/main:" + p).splitlines())
            if lost:
                return "books %s behind: %d lines of %s not landed" % (behind, len(lost), p)
        keep = self.store.p("books_dirt", time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
        moved_out = {}      # untracked shards renamed into `keep`: a late event there is carried back after the reset
        restored = {}       # tracked shards cut back to HEAD: {path: HEAD's bytes}, put back if the reset never lands
        levelled = False
        try:
            with relentless_books_left.registry_locked(self.books):     # no run records while its file is set aside
                held = {}
                head_before = self.git_ok(self.books, "rev-parse", "HEAD")
                try:
                    relentless_books_left.set_aside(self.books, left, keep, held)
                    why = self._level_rows(rows, read, keep, moved_out, restored, behind, shuffled)
                    levelled = why is None
                finally:    # by whether HEAD moved, not by what returned: a raise after the reset landed (its journal
                    # line, a timeout git outlived) must not write books' old copies over origin's for flush to publish
                    if held and self.git_ok(self.books, "rev-parse", "HEAD") != head_before:
                        relentless_books_left.hand_back(self.books, held, keep, self.store.journal)
                    else:
                        relentless_books_left.put_back(self.books, held)
            return why
        finally:
            if not levelled:
                self._unlevel(read, moved_out, restored)
            self._carry_late(read, moved_out)

    def _unlevel(self, read, moved_out, restored):
        """A level that stopped part way (a shard moved, `reset --keep` refused, an error): the shards it cut back to HEAD
        get their landed events again, so the books' ledger never reads short while the clone stays behind."""
        for p, head in restored.items():
            with open(os.path.join(self.books, p), "r+b") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                cur = f.read()
                if not cur.startswith(head):    # the reset did run on it after all, or someone rewrote it: leave it
                    self.store.journal({"at": iso(time.time()), "do": "books_unlevel_skipped", "path": p})
                    continue
                f.seek(0)
                f.truncate()
                f.write(read[p] + cur[len(head):])
                f.flush()
                os.fsync(f.fileno())
        with self.ledger_dir_locked():      # no writer creates a shard between the look and the rename
            for p, kept in list(moved_out.items()):
                src = os.path.join(self.books, p)
                if not os.path.exists(src):
                    os.rename(kept, src)        # with whatever a late writer appended to it
                else:                           # a writer made a new one meanwhile: the kept events go after its own
                    with open(kept, "rb") as f:
                        back = f.read()
                    fd = os.open(src, os.O_WRONLY | os.O_APPEND)
                    try:
                        fcntl.flock(fd, fcntl.LOCK_EX)
                        os.write(fd, back)
                    finally:
                        os.close(fd)
                del moved_out[p]

    @contextlib.contextmanager
    def append_dirs_locked(self):
        """APPEND_ONLY_DIRS held EXCLUSIVE: no code_review or art line is appended, to a shard reordered or clean, while
        level_books compares, restores and lets git replace them (a writer that locked the old inode would follow git's
        new one into the middle of its checkout). The lock is on the directory's inode, so a reset that removed and
        recreated the directory would escape it: only an origin that deletes every file in one does that (each holds
        tracked shards and a tracked subfolder), the same footing the ledger dir stands on. Not re-entrant."""
        fds = []
        try:
            for d in APPEND_ONLY_DIRS:
                d = os.path.join(self.books, d)
                if os.path.isdir(d):
                    fds.append(os.open(d, os.O_RDONLY))
                    fcntl.flock(fds[-1], fcntl.LOCK_EX)
            yield
        finally:
            for fd in fds:
                os.close(fd)

    def _level_rows(self, rows, read, keep, moved_out, restored, behind, shuffled):
        with self.append_dirs_locked():
            return self._level_rows_locked(rows, read, keep, moved_out, restored, behind, shuffled)

    def _level_rows_locked(self, rows, read, keep, moved_out, restored, behind, shuffled):
        for p, seen in shuffled.items():    # an append since shuffled_shards looked is a real line: refuse before any write
            with open(os.path.join(self.books, p), "rb") as f:
                if f.read() != seen:
                    return "books %s behind: %s moved while levelling" % (behind, p)
        for state, p in rows:
            src = os.path.join(self.books, p)
            if p in shuffled:   # compare and restore under the flock its writers take (code_review_status, artledger)
                head = subprocess.run(["git", "-C", self.books, "show", "HEAD:" + p], capture_output=True, check=True,
                                      timeout=60).stdout
                with open(src, "r+b") as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    if f.read() != shuffled[p]:     # a line landed after the look: a real line, keep it and refuse
                        return "books %s behind: %s moved while levelling" % (behind, p)
                    os.makedirs(os.path.dirname(os.path.join(keep, p)), exist_ok=True)
                    shutil.copy2(src, os.path.join(keep, p))
                    f.seek(0)       # same lines as HEAD in another order: nothing to put back if the level stops
                    f.truncate()
                    f.write(head)
                    f.flush()
                    os.fsync(f.fileno())
                continue
            if p in read:   # a ledger shard: held under the flock model.append takes, so no event lands between check and restore
                head = b"" if state == "??" else \
                    subprocess.run(["git", "-C", self.books, "show", "HEAD:" + p], capture_output=True, check=True, timeout=60).stdout
                with open(src, "r+b") as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    if f.read() != read[p]:     # a writer came in behind the check
                        return "books %s behind: %s moved while levelling" % (behind, p)
                    os.makedirs(os.path.dirname(os.path.join(keep, p)), exist_ok=True)
                    if state == "??":   # renamed, not unlinked: a writer waiting on this lock appends to the backup
                        os.rename(src, os.path.join(keep, p))
                        moved_out[p] = os.path.join(keep, p)
                    else:
                        shutil.copy2(src, os.path.join(keep, p))
                        restored[p] = head
                        f.seek(0)
                        f.truncate()
                        f.write(head)
                        f.flush()
                        os.fsync(f.fileno())
                continue
            if os.path.isfile(src):
                os.makedirs(os.path.dirname(os.path.join(keep, p)), exist_ok=True)
                shutil.copy2(src, os.path.join(keep, p))
            if state == "??":
                os.remove(src)
            else:
                os.makedirs(os.path.dirname(src), exist_ok=True)
                with open(src, "wb") as f:
                    f.write(subprocess.run(["git", "-C", self.books, "show", "HEAD:" + p], capture_output=True, check=True, timeout=60).stdout)
        self.git(self.books, "update-index", "-q", "--refresh")   # same bytes, new stat: reset --keep reads that as dirt
        with self.shards_locked(extra=sorted(shuffled)):    # no append to a restored shard while git replaces it
            got = self.git(self.books, "reset", "--keep", "origin/main", timeout=300)
        if got.returncode:      # git names the file it would not overwrite: say so, not just "cannot level"
            return "books %s behind: reset --keep refused: %s" % (behind, " ".join(got.stderr.split())[-400:])
        if shuffled:    # only now: a level that refuses above restored nothing
            self.store.journal({"at": iso(time.time()), "do": "books_reorder_restored", "paths": sorted(shuffled)})
        return None

    def _carry_late(self, read, moved_out):
        """An event a writer appended to an untracked shard's inode after level_books renamed it away: back onto the
        shard, under the same flock, whole lines as written. Nothing appended: nothing to do."""
        for p, kept in moved_out.items():
            with open(kept, "rb") as f:
                late = f.read()[len(read[p]):]
            if not late:
                continue
            fd = os.open(os.path.join(self.books, p), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX)
                os.write(fd, late)
            finally:
                os.close(fd)
            self.store.journal({"at": iso(time.time()), "do": "books_late_event_carried", "path": p, "bytes": len(late)})

    def flush(self):
        """Publish the shard: retried each tick until it lands, so a close never stays local."""
        shards = [SHARD % self.r["seat"], SHARD % "RUNNER",     # RUNNER: the alarm's `live` line
                  SHARD % BRIDGE_HOLDER]                        # its bridge takes and releases
        # a run recorded in books lands too, but only from level books (BOOKS_REGISTRY_UNSTICK_MOVED_FILE): publish
        # replays it as text, so books' whole file over an origin that moved it conflicts and strands a registry commit
        # that level_books refuses by name every tick. Behind, level_books merges it by key first.
        if self.git(self.books, "rev-list", "--count", "HEAD..origin/main").stdout.strip() == "0":
            shards.append(relentless_books_left.REGISTRY)
        got = self.git(self.books, "status", "--porcelain", "--", *shards).stdout.strip()
        moved = self.prose_moves()
        ahead = self.git(self.books, "rev-list", "--count", "origin/main..HEAD").stdout.strip()
        if not got and not moved and ahead in ("0", ""):
            return None
        dirty = [x for x in shards if x in got] + moved
        a = ["./publish"] + (["-m", "ledger: relentless supervisor", *dirty] if dirty else [])
        try:
            r = subprocess.run(a, cwd=self.books, capture_output=True, text=True, timeout=90, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:       # a slow push is a retry next tick, not a failed unit (OPS_TIMER_REPAIR_PRXC)
            return "publish timed out after 90 s"
        return None if r.returncode == 0 else "publish exit %d: %s" % (r.returncode, (r.stderr or r.stdout)[-300:])

    def prose_moves(self):
        """-> both paths of each item whose prose `rimflow close` moved to items/closed/. The ledger line lands; unpublished,
        the move sits dirty here until level_books undoes it, and selftest_items_glob_live goes red on the done item.
        A pair only: a lone deletion or a lone new file is not a close, so it stays out of the commit."""
        rows = self.git(self.books, "status", "--porcelain", "--no-renames", "-z", "--untracked-files=all", "--",
                        ITEMS_DIR).stdout.split("\0")
        rows = [(x[:2], x[3:]) for x in rows if x]
        gone = {p[len(ITEMS_DIR):] for s, p in rows if "D" in s and "/" not in p[len(ITEMS_DIR):]}
        new = {p[len(ITEMS_DIR) + len("closed/"):] for s, p in rows if s == "??" and p.startswith(ITEMS_DIR + "closed/")}
        return [p for n in sorted(gone & new) for p in (ITEMS_DIR + n, ITEMS_DIR + "closed/" + n)]

    def ledger_items(self):
        if self._ledger is None:
            model = pkg("model")
            evs = model.read()
            self._ledger = (evs, model.replay(evs))
        return self._ledger

    def state_of(self, item):
        """An item's ledger state (None: never filed), from this tick's one replay: the cause book drops closed causes."""
        it = self.ledger_items()[1].items.get(item)
        return it.state if it else None

    def pool_order(self, r):
        """Open items in the pool, best first: Operations' system items (health()), the priority list, then Test Pilot
        bouncers, raised, then rank().
        A list that cannot be obeyed gives no order, and ops_watch's plan family reads that as distressed."""
        priority, testpilot_route, model = pkg("priority"), pkg("testpilot_route"), pkg("model")
        plist = pkg("priority_list")
        orders = plist.order_map(plist.load(self.books)["entries"])
        evs, w = self.ledger_items()
        bounce = self.bounce = {v["id"] for v in testpilot_route.routed(w, evs)}
        targets = r.get("pool_targets") or ["v1"]
        # not priority.rank(): `next` offers only what a seat already took up, and the pool is the proposed backlog.
        # The same sort, so raised work and the campaign rows still go first
        words = self.seat_words()
        pool = [it for it in w.items.values() if eligible(it, r, w) and it.target in (None, *targets)
                and (it.owner != foreign_seat(r) or (words is not None and it.id not in words))]
        pool.sort(key=lambda i: (plist.position(i, orders), i.id not in bounce, model.raise_key(i), not i.this_deployment,
                                 priority._row_key(i), i.created_at or "", i.id))
        pool = [i for i in pool if i.kind != "mod" or not self.concept_refusal(i.id)]   # no tree, no worker
        pool = [i for i in pool if not self.first_touch_hold(i.id)]     # a mod's first touch waits for the Designer
        h = self.health()       # the system's own items before content: first pick, never preemption (stable sort)
        self.first, self.degraded, self.pause_scope = h["first"], h["degraded"], h.get("pause")
        pool.sort(key=lambda i: (i.id not in self.first, self.first.get(i.id, 0)))
        self.plan = {i.id: plist.position(i, orders) for i in pool if plist.position(i, orders) <= plist.MAX_ENTRIES}
        return [i.id for i in pool], w

    def owner_ruled_at(self, item):
        """The epoch of the newest owner ruling on `item` (an OWNER-seat event carrying his words or his card), or None.
        A standing ruling cited by reference (perRuling) is not a ruling on this item. Indexed once per ledger read."""
        evs, _ = self.ledger_items()
        idx = self.__dict__.get("_ruled")
        if idx is None or idx[0] is not evs:
            got = {}
            for e in evs:
                if e.get("seat") == "OWNER" and (e.get("ownerSaid") or e.get("byCard")) and e.get("id"):
                    t = ts_epoch(e.get("ts"))
                    if t is not None and t > got.get(e["id"], -1.0):
                        got[e["id"]] = t
            idx = self._ruled = (evs, got)
        return idx[1].get(item)

    def health(self):
        """Operations' verdict, read once per tick (health_order). Relentless asks; it never assesses."""
        if self.__dict__.get("_health") is None:
            utils = os.path.join(os.path.dirname(HERE), "Utils")
            if utils not in sys.path:
                sys.path.insert(0, utils)
            import ops_health
            v, why = ops_health.read_verdict()

            def fallback():
                with open(os.path.join(utils, "ops_watch_rules.json"), encoding="utf-8") as f:
                    ops_rules = json.load(f)
                return ops_health.system_ids(self.ledger_items()[1], ops_rules, self.books)
            self._health = health_order(v, why, fallback)
        return self._health

    def concept_refusal(self, item):
        """Why this item may not reach a worker, or None: a mod needs a well-defined tree (concept_tree.gate), and a mod's
        first touch needs a Designer pass on record (first_touch_hold)."""
        _, w = self.ledger_items()
        it = w.items.get(item)
        return concept_refused(self.books, item, getattr(it, "kind", None)) or self.first_touch_hold(item)

    def first_touch_hold(self, item):
        """Why this item waits for a Designer pass (first_touch.hold), or None. A pass never filed is filed here, once
        per mod per tick, needs=owner: the Designer's sitting with him is where it is done."""
        if not self.r.get("first_touch_hold"):
            return None
        if item in (self.health().get("first") or {}):
            return None      # owner card 2026-11-05: system work is not held behind the design gate (repairs do not change a mod)
        ft = pkg("first_touch")
        memo = self.__dict__.setdefault("_first_touch", {})
        if item in memo:
            return memo[item]
        _, w = self.ledger_items()
        if "_ft_map" not in self.__dict__:
            try:
                self._ft_map = ft.pass_map(self.books, ft.load_passes(os.path.join(self.books, "src", "RimMandrake",
                                                                                   "rimflow", "designer_passes.json")))
            except (OSError, ValueError):
                self._ft_map = {}

        def state_of(i):
            x = w.items.get(i)
            return getattr(x, "state", None) if x else None
        why, owed = ft.hold(self.books, item, self.item_mods({"item": item, "last_sha": None}), state_of, self._ft_map)
        filed = self.__dict__.setdefault("_ft_filed", set())
        for mod, pid in owed:
            if pid in filed:
                continue
            filed.add(pid)
            r = self.rimflow("file", pid, "--for", self.r["seat"], "--kind", "task", "--needs", "owner",
                             "--title", ft.pass_title(mod), "--why",
                             "relentless: first touch of %s by %s; the owner 2026-11-03: the first time an item names a mod, "
                             "it gets a deep Designer pass" % (mod, item))
            if r.returncode != 0:
                why += " [filing %s failed: %s]" % (pid, (r.stderr or r.stdout)[-200:])
        memo[item] = why
        return why

    def mod_names(self):
        """{lowercase folder: tier/folder} of every game mod in the books: a folder with an About.xml."""
        if self.__dict__.get("_mods") is None:
            self._mods = {os.path.basename(os.path.dirname(os.path.dirname(p))).lower():
                          "/".join(p.split(os.sep)[-4:-2]) for p in glob.glob(os.path.join(self.books, "src", "*", "*", "About", "About.xml"))}
        return self._mods

    def item_mods(self, st):
        """The game mods an item is known to touch: named in its id or title, a src/ path in its prose, or changed by
        its commits so far. Tooling (Utils, rimflow) is shared and no mod. A wrong guess only delays a worker."""
        item, known = st["item"], self.mod_names()
        memo = self.__dict__.setdefault("_item_mods", {})
        key = (item, st.get("last_sha"))
        if key not in memo:
            _, w = self.ledger_items()
            it = w.items.get(item)
            # an ALL-CAPS token joined by underscores cites another item (LEANINGSCRUB_STALL_SHARED_MOVE_1), not a mod this
            # one touches; a lone capitalised word may BE the mod (FOOMOD), so it stays (Codex r5 part2 #3)
            title = re.sub(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b", " ", getattr(it, "title", "") or "")
            words = [x.lower() for x in re.split(r"[^A-Za-z0-9]+", "%s %s" % (item, title)) if x]
            names = set(words) | {a + b for a, b in zip(words, words[1:])}
            try:
                with open(os.path.join(self.books, "infrastructure", "state", "items", item + ".md"), encoding="utf-8") as f:
                    prose = f.read()
            except OSError:
                prose = ""
            names |= {x.lower() for x in re.findall(r"src/[A-Za-z]+/([A-Za-z0-9_]+)/", prose)}
            if st.get("last_sha"):
                names |= {p.split("/")[2].lower() for p in self.changed(st.get("base"), st["last_sha"], item)
                          if p.startswith("src/") and p.count("/") >= 3}
            memo[key] = sorted(known[n] for n in names if n in known)
        return memo[key]

    def item_state(self, item, fresh=False):
        """`fresh`: replay the ledger now instead of this tick's cached view (a fence after a long fixture run)."""
        _, w = (None, pkg("model").replay(pkg("model").read())) if fresh else self.ledger_items()
        it = w.items.get(item)
        if it is None:
            return None
        priority = pkg("priority")
        return {"state": it.state, "lease": getattr(it, "lease", None), "needs": it.needs, "owner": it.owner,
                "block_holds": priority.block_holds(w, it, int(time.time())), "block": priority.block_line(it),
                "guard_owed": pkg("model").guard_owed(it), "closed_sha": getattr(it, "closed_sha", None),
                "event": getattr(it, "done_index", None)}   # the close's receipt: a reclose moves it, a note does not

    # the other seat: read from its tree, never pulled, never written
    def seat_words(self):
        """Ids the other seat has said something about that the books have not heard: a claim, start or close it has
        not published. Raw lines, not a replay, so no reading of its state can go wrong. None when that tree cannot be
        read or a line is torn: then none of its items may be taken."""
        cfg = self.r.get("staffing") or {}
        out = set()
        if foreign_retired(self.r):     # no window writes that tree: nothing unpublished, and a gone tree blocks nothing
            return out
        try:
            for seat in (cfg["foreign_seat"], "OWNER"):
                rel = SHARD % seat
                with open(os.path.join(cfg["foreign_tree"], rel), encoding="utf-8") as f:
                    there = set(f)
                try:
                    with open(os.path.join(self.books, rel), encoding="utf-8") as f:
                        there -= set(f)
                except FileNotFoundError:
                    pass
                out.update(json.loads(ln).get("id") for ln in there)
        except (KeyError, OSError, ValueError, AttributeError):
            return None
        return out - {None}

    def seat_heard(self, item, since):
        """True once the other seat's tree holds this close of this item (`since` an iso time before it), so its own
        ledger shows the item gone. Parsed: a substring would answer for another id, an old event or a torn line."""
        cfg = self.r["staffing"]
        try:
            with open(os.path.join(cfg["foreign_tree"], SHARD % self.r["seat"]), encoding="utf-8") as f:
                for ln in f:
                    if item not in ln:
                        continue
                    try:
                        ev = json.loads(ln)
                    except ValueError:
                        continue
                    if ev.get("id") == item and ev.get("event") == "close" and str(ev.get("ts", "")) >= since:
                        return True
        except OSError:
            pass
        return False

    def foreign_fits(self, item):
        """The whole eligibility again at launch: what was true at enrol may have changed on the ledger."""
        _, w = self.ledger_items()
        it = w.items.get(item)
        return it is not None and eligible(it, self.r, w) and it.target in (None, *(self.r.get("pool_targets") or ["v1"]))

    def settle_wait(self, s):
        time.sleep(s)       # a claim that passed the guard just before the reservation reaches its shard in this time

    def ledger_take(self, item):
        r = self.rimflow("reassign", item, "--to", self.r["seat"], "--reason", "relentless staffs it",
                         "--why", "relentless filler takes a proposed item of the other seat")
        self._ledger = None
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]

    def focus_cap(self):
        """The Producer's WIP cap from the schedule (RO2), the number `next` holds: relentless's open work obeys it too.
        Absent: no limit. Damaged: 1, the lowest, like an unreadable budget."""
        try:
            c = pkg("priority").focus_config()
        except ValueError:
            return 1
        return c["per_seat"] if c else None

    # the staffing readings
    def budget(self):
        """The budget of the staffed seat as published; None when not trustworthy now."""
        if self._budget is NOT_READ:
            rec = pkg("helper_budget").read()
            self._budget = (rec or {}).get("seats", {}).get(self.r["staffing"]["seat"]) if rec else None
        return self._budget

    def allocation(self):
        """The allocator's last inputs, when fresh enough to mean now; {} otherwise. Both readers below degrade to
        None, which the reading shows."""
        try:
            with open(pkg("helper_budget")._sa().streams_dir() / "allocation.json", encoding="utf-8") as f:
                rec = json.load(f)
            return rec.get("inputs") or {} if time.time() - rec["t"] < ALLOCATION_FRESH_S else {}
        except (OSError, ValueError, KeyError, TypeError, ImportError):
            return {}

    def head_helpers(self):
        """Helpers the staffed seat's head runs itself: they are on the same budget. None unmeasured (counted 0)."""
        if self._helpers is NOT_READ:
            v = (self.allocation().get("helpers_running") or {}).get(self.r["staffing"]["seat"])
            self._helpers = v if isinstance(v, int) else None
        return self._helpers

    def burn(self):
        """The account's %/h as the allocator last measured it, or None."""
        v = self.allocation().get("rate_pct_per_h")
        return float(v) if isinstance(v, (int, float)) else None

    def oom_kills(self):
        """OOM kills inside a Relentless run's cgroup since boot (the kernel log); None unreadable. Not /proc/vmstat's
        host-wide count: other cgroups' kills (rm-harness caps, tool caps) are not a reason to staff less."""
        try:
            r = subprocess.run(["journalctl", "-k", "-b", "0", "--no-pager", "-o", "cat", "-g", "oom-kill:constraint"],
                               capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
        except (OSError, subprocess.SubprocessError):
            return None
        if r.returncode not in (0, 1):      # 1 is "no entries"
            return None
        return relentless_usage.own_oom_kills(r.stdout.splitlines())

    def staffing_alarm(self, item, text):
        """One fixed item: filed once, a note while open, reopened when it was closed. -> None, or why it did not land."""
        st = self.item_state(item)
        if st is None:
            r = self.rimflow("file", item, "--for", self.r["seat"], "--kind", "bug", "--needs", "offline",
                             "--title", text[:200], "--why", "relentless filler: staffing alarm")
        elif st["state"] in ("done", "built", "validated"):
            r = self.rimflow("live", item, "--result", "broken", "--detail", text[:300], seat="RUNNER")
        elif st["state"] in ("dropped", "superseded"):
            return "%s is %s: nowhere for the alarm to land" % (item, st["state"])
        else:
            r = self.rimflow("note", item, "--text", text[:NOTE_MAX], "--why", "relentless filler: staffing alarm")
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]

    def item_text(self, item):
        r = self.rimflow("show", item)
        return (r.stdout or "")[:12000]

    def ledger_start(self, item):
        r = self.rimflow("start", item, "--why", "relentless supervisor takes the item")
        return None if r.returncode == 0 else refusal_words(r)

    def ledger_reclaim(self, item):
        r = self.rimflow("reclaim", item, "--why", "relentless supervisor: excluded in the rules, back to the pool")
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]

    def ledger_close(self, item, sha, reason, live=None):
        # Idempotent: a close that already landed (a retry after a timeout, a crash between the ledger and the store)
        # writes nothing more. The doubled close lines of 2026-11-02 were not this: they are byte-identical lines that
        # git's merge=union writes twice on a rebase, and the reader collapses them (model.canonical_order).
        if self.closed(item):
            return None
        # A blind PASS on a ledger-only candidate (a guard re-recorded, a filing) names no work: `close --sha` refuses it
        # for ever (RELENTLESS_CLOSE_FIX_EMPTY_DIFF_SAYS_NOTHING). Close at the commit that did the work, or say there is none.
        work = self.work_sha(item, sha)
        if work is None:
            close_at = ("--no-code", "nothing but bookkeeping: no commit naming %s touches more than the ledger; "
                                     "blind PASS at %s" % (item, sha[:12]))
            mark = sha
        else:
            close_at = ("--sha", work)
            mark = work
            if work != sha:
                reason = "%s (work at %s)" % (reason, work[:12])
        # the blind PASS on that sha is the check `close` asks for; RUNNER may record it on any seat's item. Rewound to the
        # work, it is recorded on the candidate too, where it ran: a guard committed after the work (re-shown red, or written
        # by another item's commit) is found there (cli._guard_commit, CLOSE_SHA_FIX_REWINDS_PAST_GUARD)
        for at in ((sha, mark) if mark != sha else (mark,)):
            if (item, at) in self.marked:
                continue
            r = self.rimflow("verify", item, "--sha", at, "--result", "pass", "--level", "L0",
                             "--config", "marker:blind-check", "--evidence", reason[:300], seat="RUNNER")
            if r.returncode != 0:
                return (r.stderr or r.stdout)[-400:]
            self.marked.add((item, at))
        r = self.rimflow("close", item, *close_at, "--reason", reason, "--why", "relentless: blind check passed",
                         *(("--live", live) if live else ()),      # the sweep keeps checking what the contract promised
                         timeout=300)       # a recurring item's guard test reruns inside the close (repeat_guard.TIMEOUT_S)
        if r.returncode == 0:
            return None
        if self.closed(item):
            return None
        out = r.stderr or r.stdout
        return close_why(out)

    def touched(self, sha):
        """-> the paths `sha` changes, in books; None when git cannot read it."""
        r = self.git(self.books, "diff-tree", "--no-commit-id", "--name-only", "-r", "--root",
                     "--diff-merges=first-parent", sha)    # a merge lists what it brought in, not nothing (Codex #4)
        return r.stdout.split() if r.returncode == 0 else None

    def work_sha(self, item, sha):
        """-> the sha to close `item` at: `sha` when it changes more than bookkeeping (or git cannot say: the close's own
        gate decides then), else the newest commit at or under it whose subject names the item and changes more than
        bookkeeping, else None (a --no-code close). Every worker commit subject names its item (the brief's rule)."""
        paths = self.touched(sha)
        if paths is None or not all(p.startswith(BOOKKEEPING) for p in paths):
            return sha
        r = self.git(self.books, "log", "--format=%H\t%s", "-F", "--grep=" + item, "-n", str(WORK_SHA_DEPTH), sha)
        name = re.compile(r"(?<![A-Z0-9_])%s(?![A-Z0-9_])" % re.escape(item))
        for line in (r.stdout.splitlines() if r.returncode == 0 else ()):
            h, _, subject = line.partition("\t")
            if not name.search(subject):
                continue
            got = self.touched(h)
            if got and not all(p.startswith(BOOKKEEPING) for p in got):
                return h
        return sha if not all(p.startswith(LEDGER_ONLY) for p in paths) else None   # a clean mark is work to the gate

    def closed(self, item):
        self.sync()
        st = self.item_state(item)
        return bool(st and st["state"] == "done")

    def ledger_marker_fail(self, item, sha, reasons):
        """The Marker's FAIL verdict on the ledger, as the run the Close gate reads (MARKER_FAIL_WIRE_INTO_CLOSE_LOCK;
        operations_design_2026-11-01.md §6): a `verify` fail on the candidate sha, RUNNER's like the PASS in ledger_close.
        It locks a close only once model.MARKER_FAIL_LOCKS is on; a later blind PASS on a sha is newer and clears it."""
        r = self.rimflow("verify", item, "--sha", sha, "--result", "fail", "--level", "L0", "--config", "marker:blind-check",
                         "--evidence", ("blind check FAIL: %s" % (reasons or "no reasons given"))[:300], seat="RUNNER")
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]

    def ledger_note(self, item, text):
        r = self.rimflow("note", item, "--text", text[:NOTE_MAX], "--why", "relentless supervisor")
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]

    def run_fixture(self, cmd, timeout=180):
        """An incident's release fixture (relentless_incident.check), in the books tree. -> (exit, tail); exit None when it
        could not run or ran out of time, which never reads as a pass."""
        return run_fixture_cmd(cmd, self.books, timeout)

    def expedite_note(self, item, text):
        """One use of the lane on the ledger; the `delegated:` why is what puts it in the daily digest."""
        r = self.rimflow("note", item, "--text", text[:NOTE_MAX], "--why", "delegated: expedite lane, set by Operations or the Conductor")
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]

    def ledger_needs_owner(self, item, why):
        return self.ledger_needs(item, "owner", why)

    def ledger_answer(self, qid):
        """The ledger event in his authority that cites `qid` (relentless_answer), or None: this tick's one replay."""
        return relentless_answer.find(self.ledger_items()[0], qid)

    def ledger_hold_to_seat(self, item, hold):
        """A tooling hold goes to the seat, never to him. -> None, or why it did not land (the next tick retries).
        A hold an older supervisor routed to him has its needs put back, and only that: another needs=owner (an L4 look,
        a person's own routing) is not ours to move. A hold already delivered has been said once; only its needs moves."""
        evs, w = self.ledger_items()
        it = w.items.get(item)
        back = self._needs_back(it, evs)
        if back:
            err = self.ledger_needs(item, back, "relentless: a tooling hold is the seat's, not the owner's")
            self._ledger = None
            if err:
                return err
        if hold.get("delivered"):
            return None
        text = "Relentless hold (%s), the seat's to read: %s" % (hold.get("kind"), hold["why"])
        err = self.ledger_note(item, text)
        if err:
            return err
        self.conductor_attention("%s: %s" % (item, text))    # a failure to tell stays out of the way: the note landed
        return None

    def needs_after_hold(self, item):
        """What a lifted hold writes back on the ledger, read fresh: the lift came from another process. None writes nothing."""
        self._ledger = None
        evs, w = self.ledger_items()
        return self._needs_back(w.items.get(item), evs)

    @classmethod
    def _needs_back(cls, it, evs):
        """The needs an item returns to from the supervisor's needs=owner. None when nothing is ours to move: it left owner
        already, or a person sent it there. A built item owes its derived needs, any other its filed ones."""
        if it is None or it.needs != "owner" or not cls._owner_routing_is_ours(it, evs):
            return None
        back = pkg("model").needs_for_levels(it.owed_levels()) if it.state in ("built", "validated") else None
        back = back or filed_needs(it, evs)
        return None if back == "owner" else back

    @staticmethod
    def _owner_routing_is_ours(it, evs):
        """True when the event that last sent the item to him was this supervisor's."""
        for i in reversed(getattr(it, "history", None) or []):
            e = evs[i] if 0 <= i < len(evs) else {}
            if e.get("event") == "needs" and e.get("to") == "owner":
                return e.get("why") == SUPERVISOR_WHY
            if e.get("event") in ("file", "block") and "owner" in (e.get("needs"), e.get("kind")):
                return False
        return False

    def ledger_block(self, item, kind, ons, reason):
        a = ["block", item, "--kind", kind, "--reason", reason[:NOTE_MAX], "--why", "relentless supervisor: a worker's snag names a blocker"]
        for on in ons:
            a += ["--on", on]
        r = self.rimflow(*a)
        self._ledger = None
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]

    def ledger_needs(self, item, to, why):
        r = self.rimflow("needs", item, "--to", to, "--reason", why[:NOTE_MAX], "--why", SUPERVISOR_WHY)
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]

    # the clones
    def clone_path(self, item, q=0):
        return os.path.join(self.base, "clones", item + (".q%d" % q if q else ""))

    # the showing stage (relentless_showing): an item waiting only on his look is staged before he is asked
    show_root = None        # relentless_showing.SHOW_DIR

    @property
    def mods_root(self):
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
        return importlib.import_module("game_paths").LOCAL_MODS

    @property
    def saves_root(self):
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
        return importlib.import_module("game_paths").SAVES

    def showing_items(self):
        """[(item, ledger item, trigger, his question, (blocked on, why) or None)] of every open item waiting only on his look, Designer first-touch
        passes left out (a sign-off, not a showing). owner_queue.is_his is the same test NEEDS YOU reads."""
        utils = os.path.join(os.path.dirname(HERE), "Utils")
        if utils not in sys.path:
            sys.path.insert(0, utils)
        oq = importlib.import_module("owner_queue")
        ft = pkg("first_touch")
        evs, w = self.ledger_items()
        try:
            passes = ft.pass_map(self.books, ft.load_passes(os.path.join(self.books, "src", "RimMandrake", "rimflow",
                                                                         "designer_passes.json")))
        except (OSError, ValueError):
            passes = {}
        qs = oq.load_questions(os.path.join(self.books, "infrastructure", "state", "owner_questions.json"))
        mine = set(self.store.items())
        want = {}
        for iid, it in sorted(w.items.items()):
            if not getattr(it, "open", False):
                continue
            his = oq.is_his(it, self.store.load(iid) if iid in mine else None, evs)
            why = relentless_showing.wants(iid, it, his, lambda i: ft.is_pass_item(i, passes))
            if why:
                want[iid] = (it, why)
        now = time.time()
        return [(iid, it, why, (qs.get(iid) or it.title or iid).strip(),
                 relentless_showing.blockers(iid, it, w.items, evs, now, lambda i: i in want))
                for iid, (it, why) in sorted(want.items())]

    def showing_clone(self):
        """-> (the one clone every showing unit runs in, None) or (None, why)."""
        st = {"item": "SHOWINGS", "clone": self.clone_path("SHOWINGS"), "gen": 0}
        why = self.prepare(st) if not os.path.isdir(os.path.join(st["clone"], ".git")) or clone_gap(st["clone"]) else None
        return (None, why) if why else (st["clone"], None)

    def prepare(self, st):
        """The item's clone (made once, kept across workers) and its fence marker. Verified first: a clone missing what
        a launch needs is bundled (nothing of it lost), removed and made again."""
        c = st["clone"]
        gap = clone_gap(c) if os.path.isdir(c) else None
        if gap:
            if not os.path.abspath(c).startswith(os.path.join(self.base, "clones") + os.sep):
                return "clone %s lacks %s and is not the pool's to remake" % (c, gap)
            bundle = None
            if os.path.isdir(os.path.join(c, ".git")):
                try:
                    bundle = self.bundle_clone(st["item"], c)
                except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as e:
                    return "clone lacks %s and its bundle failed: %s" % (gap, str(e)[-200:])
            else:       # no git to bundle from: the tree itself is kept, moved aside whole (Codex #3)
                kept, why = self.keep_gitless(st["item"], c)
                if why:
                    return "clone lacks %s and %s" % (gap, why)
                if kept:
                    self.store.journal({"at": iso(time.time()), "do": "clone_kept_gitless", "clone": os.path.basename(c),
                                        "kept": kept})
            if bundle:
                st["bundle"] = bundle
                with self.store.lock():
                    cur = self.store.load(st["item"])
                    if cur is not None:     # the synthetic SHOWINGS clone has no item record: its bundle lives in
                        cur["bundle"] = bundle      # orphans/ and in the clone_remade journal line (Codex, ..._TEN_MORE #3)
                        self.store.save(cur)
            why = relentless_disk.remove_tree(c)
            self.store.journal({"at": iso(time.time()), "do": "clone_remade", "clone": os.path.basename(c),
                                "missing": gap, "bundle": bundle, "remove": why})
            if why:
                return "clone lacks %s and would not go: %s" % (gap, why)
        if not os.path.isdir(os.path.join(c, ".git")):
            env = dict(os.environ, RM_SCRATCH_ROOT=os.path.dirname(os.path.dirname(c)), RM_SEAT="clones")
            r = subprocess.run(["python3", os.path.join(self.books, "src/RimMandrake/Utils/scratch_clone.py"), "clone",
                                "relentless " + st["item"], "--name", os.path.basename(c), "--checkout", "--fetch"],
                               cwd=self.books, env=env, capture_output=True, text=True, timeout=400,
                               stdin=subprocess.DEVNULL)
            if r.returncode:
                return "clone failed: %s" % (r.stderr or r.stdout)[-300:]
            gap = clone_gap(c)
            if gap:
                return "clone failed: made without %s" % gap
        if st.get("bundle"):      # outside the clone's making: a tick that died between the two still restores
            self.restore_bundle(st["item"], st["bundle"], c)
            with self.store.lock():
                cur = self.store.load(st["item"])
                if cur is not None:     # SHOWINGS is a synthetic item with no store record (Codex r3)
                    cur.pop("bundle", None)
                    self.store.save(cur)
        # a worker must push to origin: a reused help-* consult clone kept pushurl=read-only-consult (help_checkout) and
        # its ./publish died (CLONE_REUSE_FIX_CONSULT_PUSHURL_LINGERS); scratch_clone.pool_reuse clears it, this whatever path
        self.git(c, "config", "--unset-all", "remote.origin.pushurl")
        self.store._write(os.path.join(c, ".git", "relentless.json"),     # atomic: the pre-push hook may be reading
                          json.dumps({"item": st["item"], "gen": st["gen"]}))
        return None

    def objstore(self):
        """The bare store every pool clone borrows objects from (scratch_clone's): the integrity gate reads its packs."""
        return str(self.scratch_clone().store_path())

    def scratch_clone(self):
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
        return importlib.import_module("scratch_clone")

    def pool_clones(self):
        return sorted(d for d in glob.glob(os.path.join(self.base, "clones", "*")) if self.clone_present(d))

    def clone_gap(self, c):
        return clone_gap(c)

    def clone_present(self, c):
        return os.path.isdir(c)   # a half-removed clone still takes its path and its bytes

    def pool_load(self):
        """-> (clones, bytes, cap on clones, cap on bytes). The caps are scratch_clone's, the owner's numbers."""
        sc = self.scratch_clone()
        got = self.pool_clones()
        cmax, bmax = sc.pool_cap()
        return len(got), sum(sc.clone_bytes(sc.Path(c)) for c in got), cmax, bmax

    def clone_busy(self, c):
        sc = self.scratch_clone()
        return sc.clone_in_use(sc.Path(c))

    def clone_idle_s(self, c):
        sc = self.scratch_clone()
        return sc.clone_idle_s(sc.Path(c))

    def clone_wip(self, c):
        """-> {"kept": commits or a stash no remote has, "real": changed paths a worker meant}. An unreadable clone is
        kept: nothing about it is known. "carry_real": commits or a stash that a bundle can carry back (restore_commits takes
        merges, side branches and stashes too), which a put-down item's clone must not sit on (POOL_STRANDS_SALVAGE_BLOCKED_HOLD_THE_BAG).
        Only an unreadable clone is kept and not carried; scratch_clone alarms on that one."""
        try:
            shas = self.git_ok(c, "rev-list", "HEAD", "--branches", "--tags", "--not", "--remotes").split()
            # POOL_UNLANDED_COMMITS_NEVER_RELEASE (2026-11-03): a worker's last commit is often a lesson or ledger record made after
            # its landing; "commits stay" then held 9 of 16 pool places for items parked on the game. Commits that touch only
            # state records are carried by the bundle and cherry-picked into the item's next clone, so they do not pin the clone.
            state, merge = bool(shas), False
            for sha in shas:
                files = self.git_ok(c, "diff-tree", "--no-commit-id", "--name-only", "-r", "-m", "--root", sha).split("\n")
                merge = merge or len(self.git_ok(c, "rev-list", "--parents", "-n1", sha).split()) > 2
                if merge or any(not f or not f.startswith(POOL_NOISE + POOL_STATE) for f in files if f) or not any(files):
                    state = False
            stashed = self.git_ok(c, "stash", "list").strip() != ""
            kept = (bool(shas) and not state) or stashed
            return {"kept": kept, "carry": bool(shas) and state, "carry_real": kept,
                    "real": [p for p in self.changed_paths(c) + self.ignored_paths(c) if not p.startswith(POOL_NOISE)]}
        except (RuntimeError, OSError, ValueError, subprocess.SubprocessError):
            return {"kept": True, "carry": False, "carry_real": False, "real": []}

    def git_ok(self, cwd, *args):
        r = self.git(cwd, *args, timeout=300)
        if r.returncode:
            raise RuntimeError("git %s: %s" % (args[0], r.stderr[-200:]))
        return r.stdout

    def changed_paths(self, c):
        out = self.git_ok(c, "--no-optional-locks", "status", "--porcelain", "--untracked-files=normal", "--no-renames", "-z")
        return [x[3:] for x in out.split("\0") if x]

    def ignored_paths(self, c):
        """Ignored files are nobody else's copy either. Bytecode is the one thing that is only ever derived."""
        out = self.git_ok(c, "ls-files", "-z", "--others", "--ignored", "--exclude-standard").split("\0")
        return [p for p in out if p and "__pycache__/" not in p and not p.endswith(".pyc")]

    def keep_gitless(self, item, c):
        """A clone folder with no .git has nothing to bundle from, and its untracked files are the only copy: moved whole
        beside the item's bundles (a rename, same disk). -> (where it went, None); (None, None) when it held no file;
        (None, why) when it could not move, and the caller then keeps it."""
        def unreadable(e):      # os.walk swallows a listing error by default: an unread folder is not empty (r5 #17)
            raise e
        try:
            empty = not any(files or any(os.path.islink(os.path.join(dp, x)) for x in dirs)    # a symlinked dir
                            for dp, dirs, files in os.walk(c, onerror=unreadable))  # is a thing to keep too (a dir to os.walk)
        except OSError as e:
            return None, "its tree could not be read: %s" % str(e)[:200]
        if empty:
            return None, None
        home = self.store.p("items", item) if item and os.path.isdir(self.store.p("items", item)) else self.store.p("orphans")
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        out, n = os.path.join(home, "gitless", "%s-%s" % (stamp, os.path.basename(c))), 1
        while os.path.lexists(out):
            out, n = os.path.join(home, "gitless", "%s-%s-%d" % (stamp, os.path.basename(c), n)), n + 1
        try:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            os.rename(c, out)
        except OSError as e:
            return None, "its git-less tree could not be kept aside: %s" % str(e)[:200]
        return out, None

    def bundle_clone(self, item, c):
        """Everything no remote has, on the store's disk, before a clone goes. -> the bundle dir, None when there is
        nothing. Raises when it cannot be sure: the caller then keeps the clone, and no half-written bundle stays.
        RELENTLESS_BUNDLES_FIX_FOURTEEN_GIG_PATCHES (2026-11-04): a scratch clone whose fetch failed after its `clone
        --no-checkout` had a .git, no index and no tree; every tracked file read as deleted, and three --binary patches each
        carried the whole 3.9 GB tree as preimage (14 GB a bundle, three bundles). So: no index means never checked out
        (missing files are not deletions); a deletion is a path in `deleted`, never a preimage (git apply refuses an
        --irreversible-delete patch); index.patch is kept only when it differs from diff.patch; and a bundle over
        BUNDLE_PATCH_MAX / BUNDLE_MAX raises instead of filling the disk."""
        unchecked = not os.path.exists(os.path.join(c, ".git", "index"))
        if unchecked:       # read-tree without -u writes only the index: present files then read as clean or changed
            self.git_ok(c, "read-tree", "HEAD")
        paths = self.changed_paths(c)
        commits = self.git_ok(c, "rev-list", "HEAD", "--branches", "--tags", "--not", "--remotes").strip()
        stash = self.git_ok(c, "stash", "list", "--format=%H").split()
        ignored = self.ignored_paths(c)
        deleted = [] if unchecked else [p for p in self.git_ok(c, "diff", "--name-only", "-z", "--no-renames",
                                                                     "--diff-filter=D", "HEAD").split("\0") if p]
        if unchecked:       # a file never checked out is not one a worker removed
            gone = set(p for p in self.git_ok(c, "diff", "--name-only", "-z", "--no-renames", "--diff-filter=D",
                                                "HEAD").split("\0") if p)
            paths = [p for p in paths if p not in gone]
        if not paths and not commits and not stash and not ignored:
            return None
        if sum(os.lstat(os.path.join(c, p)).st_size for p in ignored) > POOL_IGNORED_MAX:
            raise RuntimeError("ignored files over %d bytes: read them before this clone goes" % POOL_IGNORED_MAX)
        home = self.store.p("items", item) if os.path.isdir(self.store.p("items", item)) else self.store.p("orphans")
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        out, n = os.path.join(home, "bundles", "%s-%s" % (stamp, os.path.basename(c))), 1
        while os.path.exists(out):      # named by the second: never let an earlier bundle's files answer for this one
            out, n = os.path.join(home, "bundles", "%s-%s-%d" % (stamp, os.path.basename(c), n)), n + 1
        os.makedirs(out)
        try:
            self._bundle_write(c, out, paths, deleted, ignored, commits, stash)
        except BaseException:
            shutil.rmtree(out, ignore_errors=True)
            raise
        return out

    def _bundle_write(self, c, out, paths, deleted, ignored, commits, stash):
        real = [p for p in paths if not p.startswith(POOL_NOISE)]
        untracked = self.git_ok(c, "ls-files", "-z", "--others", "--exclude-standard").split("\0")
        untracked = [p for p in untracked if p]
        diff = ["git", "-C", c, "diff", "--binary", "--no-textconv", "--no-ext-diff", "--no-renames", "--diff-filter=d"]

        def write(name, argv, cap=BUNDLE_PATCH_MAX):
            path = os.path.join(out, name)
            with open(path, "wb") as f:
                if argv:
                    subprocess.run(argv, stdout=f, check=True, timeout=300)
            if os.path.getsize(path) > cap:
                raise RuntimeError("%s is %d bytes, over the bundle cap %d: read this clone before it goes"
                                   % (name, os.path.getsize(path), cap))
            return path
        with open(os.path.join(out, "HEAD"), "w", encoding="utf-8") as f:
            f.write(self.git_ok(c, "rev-parse", "HEAD"))
        whole = write("diff.patch", diff + ["HEAD"])
        index = write("index.patch", diff + ["--cached", "HEAD"])   # staged content the working file no longer shows
        if filecmp.cmp(index, whole, shallow=False):
            os.unlink(index)    # a second copy of diff.patch says nothing restore_bundle does not already know
        noisy = any(p.startswith(POOL_NOISE) for p in paths)
        if real and not noisy:
            os.link(whole, os.path.join(out, "real.patch"))     # the same bytes: one copy on disk
        else:   # noise excluded by prefix, never the paths listed: thousands of them overflow argv (E2BIG)
            write("real.patch", diff + ["HEAD", "--", ":(top)"] + [":(top,exclude)" + p for p in POOL_NOISE] if real else None)
        real_deleted = [p for p in deleted if not p.startswith(POOL_NOISE)]
        if real_deleted:        # a deletion's content is HEAD's: the path is all restore_bundle needs
            with open(os.path.join(out, "deleted"), "w", encoding="utf-8") as f:
                f.write("\0".join(real_deleted))
        for name, want in (("untracked.tar", untracked), ("ignored.tar", ignored),
                           ("real_untracked.tar", [p for p in untracked if not p.startswith(POOL_NOISE)])):
            if want:
                subprocess.run(["tar", "-C", c, "--null", "-T", "-", "-cf", os.path.join(out, name)],
                               input="\0".join(want).encode(), check=True, timeout=300)
        for i, sha in enumerate(stash):   # refs/stash names only the newest; the rest live in a reflog no bundle carries
            self.git_ok(c, "update-ref", "refs/rm-stash/%d" % i, sha)
        if commits or stash:
            open(os.path.join(out, "carry"), "w").close()
            r = self.git(c, "bundle", "create", os.path.join(out, "commits.bundle"), "HEAD", "--all", "--not", "--remotes")
            if r.returncode:
                raise RuntimeError("git bundle: %s" % r.stderr[-200:])
        size = bundle_bytes(out)
        if size > BUNDLE_MAX:
            raise RuntimeError("bundle is %d bytes, over the cap %d: read this clone before it goes" % (size, BUNDLE_MAX))

    def restore_bundle(self, item, bundle, c):
        """A fresh clone takes the WIP of the one evicted. What will not apply stays in the bundle and the record says so."""
        bad = []
        cb = os.path.join(bundle, "commits.bundle")
        if os.path.exists(os.path.join(bundle, "carry")) and os.path.exists(cb):     # carried commits come back as commits
            bad.extend(self.restore_commits(item, bundle, cb, c))
            if bad:
                self.store.journal({"at": iso(time.time()), "do": "alarm", "kind": "restore_incomplete", "item": item,
                                    "bundle": bundle, "why": "; ".join(bad)[:300]})
        patch = os.path.join(bundle, "real.patch")
        if os.path.exists(patch) and os.path.getsize(patch):
            r = self.git(c, "apply", "--3way", "--whitespace=nowarn", patch, timeout=300)
            if r.returncode:
                bad.append("patch: %s" % r.stderr[-200:])
        bad.extend(restore_deleted(bundle, c))
        index, whole = (os.path.join(bundle, x) for x in ("index.patch", "diff.patch"))
        if os.path.exists(index) and os.path.getsize(index):
            with open(index, "rb") as a, open(whole, "rb") as b:
                if a.read() != b.read():
                    bad.append("the index held content the working tree did not: see index.patch")
        for name in ("real_untracked.tar", "ignored.tar"):
            tar = os.path.join(bundle, name)
            if not os.path.exists(tar):
                continue
            listed = subprocess.run(["tar", "-tf", tar], capture_output=True, text=True, timeout=300)
            clash = [p for p in listed.stdout.splitlines()     # any non-directory member whose path is already taken
                     if not p.endswith("/") and os.path.lexists(os.path.join(c, p.rstrip("/")))]
            if clash:   # upstream has since tracked the name (a file, a directory, a link): never overwritten, and said
                #   (a directory used to be skipped by --skip-old-files in silence; Codex, ..._TEN_MORE #5)
                bad.append("%s kept in the bundle, upstream has them: %s" % (name, ", ".join(clash[:5])))
            r = subprocess.run(["tar", "--skip-old-files", "-C", c, "-xf", tar], capture_output=True, text=True, timeout=300)
            if r.returncode:
                bad.append("%s: %s" % (name, r.stderr[-200:]))
        if bad:
            self.store.learn(item, "\n%s relentless: your clone was evicted from a full pool and its WIP did not all "
                             "come back; it is in %s (%s)\n" % (iso(time.time()), bundle, "; ".join(bad)))
        return bad

    def restore_commits(self, item, bundle, cb, c):
        """Every commit and stash in the bundle comes back or is named. -> what did not. HEAD's line by cherry-pick along its
        first parents (a merge as one commit, -m 1, so a resolution made in the merge is kept); a branch or tag HEAD does not
        reach as that ref; each stash onto the stash list, oldest first so the order holds."""
        listed = self.git(c, "bundle", "list-heads", cb, timeout=300)
        heads = [ln.split(None, 1) for ln in listed.stdout.splitlines() if " " in ln]
        if listed.returncode or not heads:
            return ["commits.bundle: %s" % (listed.stderr[-200:] or "no refs in it")]
        temp = ["refs/rm-carried/%d" % i for i in range(len(heads))]
        r = self.git(c, "fetch", "-q", "--no-tags", cb, *("+%s:%s" % (h[1], t) for h, t in zip(heads, temp)), timeout=300)
        if r.returncode:
            return ["commits.bundle: %s" % r.stderr[-200:]]
        bad, picked, landed, side, stashes = [], 0, 0, [], []
        tip = next((sha for sha, ref in heads if ref == "HEAD"), None)
        shas = self.git(c, "rev-list", "--reverse", "--first-parent", tip, "--not", "--remotes", timeout=300).stdout.split() if tip else []
        for sha in shas:
            merge = len(self.git(c, "rev-list", "--parents", "-n1", sha, timeout=60).stdout.split()) > 2
            r = self.git(c, "-c", "user.name=relentless", "-c", "user.email=relentless@localhost", "cherry-pick", "--allow-empty",
                         *(("-m", "1") if merge else ()), sha, timeout=300)
            if not r.returncode:
                picked += 1
                continue
            started = self.git(c, "rev-parse", "-q", "--verify", "CHERRY_PICK_HEAD", timeout=60).returncode == 0
            if started and self.git(c, "diff", "--quiet", "HEAD", timeout=60).returncode == 0 \
                    and not self.git(c, "ls-files", "-u", timeout=60).stdout.strip():   # origin already holds it; an
                # unmerged path (a modify/delete conflict leaves the tree as HEAD) is no landing (Codex r5 part3 #3)
                self.git(c, "cherry-pick", "--skip", timeout=60)
                landed += 1
                continue
            self.git(c, "cherry-pick", "--abort", timeout=60)
            bad.append("commit %s did not re-apply: %s" % (sha[:10], r.stderr[-120:]))
            break
        for sha, ref in heads:
            if not ref.startswith(("refs/heads/", "refs/tags/")):
                continue
            if tip and self.git(c, "merge-base", "--is-ancestor", sha, tip, timeout=60).returncode == 0:
                continue        # on HEAD's line: it came back above
            area, name = ("refs/heads/", ref[11:]) if ref.startswith("refs/heads/") else ("refs/tags/", ref[10:])
            want, n = ref, 1        # a name already taken (by the clone or an earlier restore) gets a fresh one: never
            while self.git(c, "rev-parse", "-q", "--verify", want, timeout=60).returncode == 0:    # overwritten
                want = "%scarried/%s" % (area, name) if n == 1 else "%scarried/%s-%d" % (area, name, n)
                n += 1      # (Codex, ..._TEN_MORE #4)
            r = self.git(c, "update-ref", want, sha, "0" * 40, timeout=60)     # old value zero: refuses if it now exists
            if r.returncode:
                bad.append("%s did not come back: %s" % (ref, r.stderr[-120:]))
            else:
                side.append(want)
        for sha, ref in sorted((h for h in heads if h[1].startswith("refs/rm-stash/")), key=lambda h: -int(h[1].rsplit("/", 1)[1])):
            subject = self.git(c, "log", "-1", "--format=%s", sha, timeout=60).stdout.strip()
            r = self.git(c, "-c", "user.name=relentless", "-c", "user.email=relentless@localhost", "stash", "store", "-m", subject, sha, timeout=60)
            if r.returncode:
                bad.append("stash %s did not come back: %s" % (sha[:10], r.stderr[-120:]))
            else:
                stashes.append(sha)
        for t in temp:
            self.git(c, "update-ref", "-d", t, timeout=60)
        said = []
        if picked:
            said.append("%d unlanded commit(s) came back by cherry-pick: land them or drop them" % picked)
        if landed:
            said.append("%d already on origin, skipped" % landed)
        if side:
            said.append("off HEAD's line, unlanded: %s" % ", ".join(side))
        if stashes:
            said.append("%d stash(es) back on git stash list" % len(stashes))
        if said:
            self.store.learn(item, "\n%s relentless: your clone went back while the item was put down; %s (bundle: %s)\n" % (
                iso(time.time()), "; ".join(said), bundle))
        return bad

    def remove_clone(self, st, before=None):
        """Nothing leaves the pool unbundled. -> the bundle dir or None; a bundle that fails keeps the clone."""
        c = st.get("clone")
        if not c or not os.path.abspath(c).startswith(os.path.join(self.base, "clones") + os.sep):
            return None
        out = None
        if os.path.exists(os.path.join(c, ".git")):
            try:
                out = self.bundle_clone(st.get("item") or clone_item(c), c)
            except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as e:
                self.store.journal({"at": iso(time.time()), "do": "alarm", "kind": "bundle_failed", "clone": c, "why": str(e)[:300]})
                return None
        elif os.path.isdir(c):  # no git to bundle from: its files are moved aside whole, never deleted (Codex #3)
            kept, why = self.keep_gitless(st.get("item") or clone_item(c), c)
            if why:
                self.store.journal({"at": iso(time.time()), "do": "alarm", "kind": "bundle_failed", "clone": c, "why": why})
                return None
            if kept:
                self.store.journal({"at": iso(time.time()), "do": "clone_kept_gitless", "clone": os.path.basename(c),
                                    "kept": kept})
        if before and out:
            before(out)         # the record learns of the bundle while the clone still stands
        warm = relentless_disk.park(c, os.path.join(self.base, "clones"), self.r.get("warm_clones", 0),
                                    relentless_integrity.clone_damage) if os.path.isdir(os.path.join(c, ".git")) else None
        if warm:                # reused by the next clone instead of a fresh 3.6 GB checkout (DISK_CHURN_MEASURE_CLONES_EAT_THE_VHDX)
            self.store.journal({"at": iso(time.time()), "do": "clone_parked", "clone": os.path.basename(c),
                                "warm": os.path.basename(warm), "bundle": out})
            return out
        why = relentless_disk.remove_tree(c)
        if why:                 # still present, so still counted; the bundle stands. A clone already gone is removed.
            self.store.journal({"at": iso(time.time()), "do": "alarm", "kind": "remove_failed", "clone": c, "why": why})
        return out

    def warm_count(self):
        return len(relentless_disk.warm_clones(os.path.join(self.base, "clones")))

    def box_in_use(self, box):
        sc = self.scratch_clone()
        return sc.clone_in_use(sc.Path(box))

    def conductor_alarm(self, text):
        """The line the Conductor reads first. -> None, or why it did not land."""
        path = (self.r.get("staffing") or {}).get("conductor_log")
        if not path:
            return "no conductor_log in the rules"
        try:
            conductor_log_guard.refuse_if_test(path)
            with open(path, "a", encoding="utf-8") as f:
                f.write("\n%s — RELENTLESS JAM: %s\n  RAISE FIRST: relentless is stalled\n" % (iso(time.time()), text))
        except OSError as e:
            return str(e)[:200]
        return None

    def conductor_attention(self, text):
        """An advisory line for the Conductor: something crossed a threshold and nothing was stopped (owner
        2026-11-02, TOKEN_LIMITS_TAME_BARK_NO_BITE). -> None, or why it did not land."""
        path = (self.r.get("staffing") or {}).get("conductor_log")
        if not path:
            return "no conductor_log in the rules"
        try:
            conductor_log_guard.refuse_if_test(path)
            with open(path, "a", encoding="utf-8") as f:
                f.write("\n%s — RELENTLESS ATTENTION (advisory, nothing stopped): %s\n" % (iso(time.time()), text))
        except OSError as e:
            return str(e)[:200]
        return None

    def told(self, row):
        """One row of the told ledger (OP3), beside ops_watch's alarms.json. -> None, or why it did not land."""
        d = os.environ.get("RM_OPS_WATCH_DIR") or self.r["ops_watch_dir"]
        try:
            with open(os.path.join(d, "told.jsonl"), "a", encoding="utf-8") as f:
                f.write(json.dumps(row, sort_keys=True) + "\n")
        except OSError as e:
            return str(e)[:200]
        return None

    def alarm_signal(self, rec):
        """A journalled alarm joins the told ledger, each kind at most once in ALARM_TOLD_EVERY_S: step_raised can fire
        every tick. A failure stays on the journal and never stops the tick that alarmed."""
        import incident as IN
        kind = rec.get("kind") or "relentless_alarm"    # an alarm with no kind once raised out of journal() itself
        path, now = self.store.p("alarm_told.json"), time.time()
        try:
            try:
                with open(path, encoding="utf-8") as f:
                    said = json.load(f)
            except (OSError, ValueError):
                said = {}
            if now - said.get(kind, -1e18) < ALARM_TOLD_EVERY_S:
                return
            d = os.environ.get("RM_OPS_WATCH_DIR") or self.r["ops_watch_dir"]
            if IN.signal({"incident": {"enabled": True}}, kind, rec.get("why"), now, os.path.join(d, "told.jsonl")):
                said[kind] = now
                self.store._write(path, json.dumps(said))
        except Exception as e:  # noqa: BLE001
            self.store._append(self.store.p("journal.jsonl"), json.dumps({
                "at": iso(now), "do": "told_failed", "kind": kind, "why": "%s: %s" % (type(e).__name__, str(e)[:200])}))

    def check_path(self, st):
        """A new path per check: a quarantined checker may still be running in the last one."""
        return os.path.join(self.base, "clones", "check-%s-c%d" % (st["item"], (st.get("check_count") or 0) + 1))

    def old_checks(self, st):
        """This item's earlier check clones, less any an unreaped quarantined run is still in."""
        keep = {q.get("clone") for q in st["quarantined"] if not q.get("reaped")}
        got = glob.glob(os.path.join(self.base, "clones", "check-%s-c*" % st["item"]))
        return [d for d in got if d not in keep]

    def reach_probe(self, r, paths, adapter_names, values, store_root, grants=()):
        """BLIND_JUDGE_BUILD_FIXES_OWN_EYES: is a Judge's proposed repair readable from inside its wall? Each path is read
        in a throwaway unit carrying the Marker's own systemd properties with the path bound as at a launch; each adapter
        is run outside as at a check and must exit 0 with output; a git_history grant is made from values["repo"] at
        values["sha"] as at a launch and must read HEAD and the sha's commit inside the wall. -> (True|False, what it saw)."""
        import tempfile
        seen = []
        if relentless_wall.GIT_GRANT in (grants or ()):
            ok, what = self._probe_git(r, values, store_root)
            seen.append(what)
            if not ok:
                return False, "; ".join(seen)
        if relentless_wall.ITEM_GRANT in (grants or ()):
            ok, what = self._probe_items(r, values, store_root)
            seen.append(what)
            if not ok:
                return False, "; ".join(seen)
        if paths:
            prof = relentless_wall.profile(r)
            os.makedirs(prof["box_root"], exist_ok=True)
            box = tempfile.mkdtemp(prefix="reachprobe-", dir=prof["box_root"])
            try:
                for sub in ("projects", "tmp"):        # props() binds both into the unit
                    os.makedirs(os.path.join(box, sub), exist_ok=True)
                body = ('for p do if [ -d "$p" ]; then ls -- "$p" >/dev/null || { echo "UNREADABLE $p"; exit 3; }; '
                        'elif [ -r "$p" ]; then head -c 1 -- "$p" >/dev/null || { echo "UNREADABLE $p"; exit 3; }; '
                        'else echo "UNREADABLE $p"; exit 3; fi; echo "read $p"; done')
                argv = (["systemd-run", "--user", "--wait", "--pipe", "--collect", "--quiet"]
                        + relentless_wall.props(prof, box, [store_root], list(paths))
                        + ["--", "/bin/sh", "-c", body, "sh", *paths])
                try:
                    p = subprocess.run(argv, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
                except (OSError, subprocess.SubprocessError) as e:
                    return False, "probe unit: %s: %s" % (type(e).__name__, e)
                seen.append(("paths exit %d: %s" % (p.returncode, ((p.stdout or "") + (p.stderr or "")).strip()))[-400:])
                if p.returncode != 0:
                    return False, "; ".join(seen)
            finally:
                shutil.rmtree(box, ignore_errors=True)
        if adapter_names:
            for got in offbox_readings(self, {"offbox": list(adapter_names)}, r, values):
                seen.append("%s exit %s, %d chars" % (got["cmd"][:80], got["exit"], len(got.get("out") or "")))
                if got["exit"] != 0 or not (got.get("out") or "").strip():
                    return False, "; ".join(seen)
        return bool(seen), "; ".join(seen) or "nothing to probe"

    def _probe_git(self, r, values, store_root):
        """The git_history grant (relentless_wall.grant_git), made in a throwaway box and read from inside the wall."""
        import tempfile
        prof = relentless_wall.profile(r)
        sha, repo = values.get("sha") or "", values.get("repo") or self.books
        if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", sha):
            return False, "git_history: no candidate sha to probe at (%r)" % sha[:20]
        os.makedirs(prof["box_root"], exist_ok=True)
        box = tempfile.mkdtemp(prefix="reachprobe-", dir=prof["box_root"])
        try:
            for sub in ("projects", "tmp", "tree"):
                os.makedirs(os.path.join(box, sub), exist_ok=True)
            try:
                relentless_wall.grant_git(box, repo, sha)
            except (OSError, RuntimeError, subprocess.SubprocessError) as e:
                return False, "git_history: the grant could not be made at %s: %s" % (sha[:10], str(e)[-200:])
            body = 'h=$(git -C "$1" rev-parse HEAD) && git -C "$1" cat-file -e "$2^{commit}" && echo "HEAD $h"'
            argv = (["systemd-run", "--user", "--wait", "--pipe", "--collect", "--quiet"]
                    + relentless_wall.props(prof, box, [store_root])
                    + ["--", "/bin/sh", "-c", body, "sh", os.path.join(box, "tree"), sha])
            try:
                p = subprocess.run(argv, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
            except (OSError, subprocess.SubprocessError) as e:
                return False, "probe unit: %s: %s" % (type(e).__name__, e)
            out = ((p.stdout or "") + (p.stderr or "")).strip()
            good = p.returncode == 0 and ("HEAD " + sha) in out
            return good, ("git_history exit %d: %s" % (p.returncode, out))[-400:]
        finally:
            shutil.rmtree(box, ignore_errors=True)

    def _probe_items(self, r, values, store_root):
        """The item_prose grant (relentless_wall.grant_items), made in a throwaway box at the candidate and listed from
        inside the wall: an item file must read there, as it will in the Marker's tree."""
        import tempfile
        prof = relentless_wall.profile(r)
        sha, repo = values.get("sha") or "", values.get("repo") or self.books
        if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", sha):
            return False, "item_prose: no candidate sha to probe at (%r)" % sha[:20]
        os.makedirs(prof["box_root"], exist_ok=True)
        box = tempfile.mkdtemp(prefix="reachprobe-", dir=prof["box_root"])
        try:
            for sub in ("projects", "tmp", "tree"):
                os.makedirs(os.path.join(box, sub), exist_ok=True)
            try:
                relentless_wall.grant_items(box, repo, relentless_wall.item_rev(sha))
            except (OSError, RuntimeError, subprocess.SubprocessError) as e:
                return False, "item_prose: the grant could not be made at %s: %s" % (sha[:10], str(e)[-200:])
            # positional only: systemd substitutes $name in the command line (a named shell variable reads empty)
            body = 'set -- "$1"/*.md; [ -r "$1" ] && head -c 1 -- "$1" >/dev/null && echo "read $1"'
            argv = (["systemd-run", "--user", "--wait", "--pipe", "--collect", "--quiet"]
                    + relentless_wall.props(prof, box, [store_root])
                    + ["--", "/bin/sh", "-c", body, "sh", os.path.join(box, "tree", relentless_wall.ITEMS)])
            try:
                p = subprocess.run(argv, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
            except (OSError, subprocess.SubprocessError) as e:
                return False, "probe unit: %s: %s" % (type(e).__name__, e)
            out = ((p.stdout or "") + (p.stderr or "")).strip()
            return p.returncode == 0 and "read " in out, ("item_prose exit %d: %s" % (p.returncode, out))[-400:]
        finally:
            shutil.rmtree(box, ignore_errors=True)

    def reach_ticket(self, item, text):
        """The fallback when a Judge's own reach repair failed its probe: filed once, a note while open, reopened by a new
        live row once closed. -> None, or why it did not land (the next tick retries)."""
        st = self.item_state(item)
        if st is None:
            r = self.rimflow("file", item, "--for", self.r["seat"], "--kind", "bug", "--needs", "offline",
                             "--title", text[:200], "--why", "relentless supervisor: a blind Judge's reach repair failed its probe")
        elif st["state"] in ("done", "built", "validated"):
            r = self.rimflow("live", item, "--result", "broken", "--detail", text[:300], seat="RUNNER")
        elif st["state"] in ("dropped", "superseded"):
            return "%s is %s: nowhere for the reach ticket to land" % (item, st["state"])
        else:
            r = self.rimflow("note", item, "--text", text[:NOTE_MAX], "--why", "relentless supervisor: reach repair failed")
        self._ledger = None
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]

    def env_repair(self, item, title, text):
        """ENV_HOLDS_FIX_ROUTE_TO_BUILDERS: the repair item a game-lane environment cause waits on (relentless_game.
        repair_id), for this seat and needs offline so a builder takes it: filed once, a note per item it stops while
        open, reopened by a new live row once closed. -> None, or why it did not land (the next tick routes again)."""
        st = self.item_state(item)
        if st is None:
            r = self.rimflow("file", item, "--for", self.r["seat"], "--kind", "bug", "--needs", "offline",
                             "--title", title[:200], "--why", "relentless supervisor: a game-lane environment cause "
                                                            "no lane step can fix")
            if r.returncode == 0:
                r = self.rimflow("note", item, "--text", text[:NOTE_MAX], "--why", "relentless supervisor: env route")
        elif st["state"] in ("done", "built", "validated"):
            r = self.rimflow("live", item, "--result", "broken", "--detail", text[:300], seat="RUNNER")
        elif st["state"] in ("dropped", "superseded"):
            return "%s is %s: nowhere for the environment cause to land" % (item, st["state"])
        else:
            r = self.rimflow("note", item, "--text", text[:NOTE_MAX], "--why", "relentless supervisor: env route")
        self._ledger = None
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]

    def ledger_unblock(self, item, reason):
        r = self.rimflow("unblock", item, "--reason", reason[:NOTE_MAX], "--why", "relentless supervisor: reach repair probe passed")
        self._ledger = None
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-300:]

    def run_offbox(self, name, adapter, timeout):
        """One supervisor offbox adapter, run outside the Marker's wall (CHECKER_SANDBOX_FIX_BLIND_TO_STEVE): the reading of
        what the box cannot reach. GPT review of 0135b04912: argv from the rules (no shell, no worker text), from an empty
        folder (not the candidate tree), no store root in its env, and output read as it comes with at most OFFBOX_OUT_MAX
        bytes kept - the process is killed past the cap or the timeout. -> {cmd, exit, out, at}."""
        return run_bounded(name, adapter, timeout)

    def clean_checkout(self, st, sha):
        """A clean tree at exactly `sha`, for the checker. Tracked files only: no worker scratch leaks in."""
        d = self.check_path(st)
        for old in self.old_checks(st):
            self.remove_clone({"clone": old, "item": st["item"]})     # a clean checkout: parked warm, or removed
        return self._detached_clone(d, sha, "check", st["item"])

    def _detached_clone(self, d, sha, what, item, remade=False):
        env = dict(os.environ, RM_SCRATCH_ROOT=os.path.dirname(os.path.dirname(d)), RM_SEAT="clones")
        r = subprocess.run(["python3", os.path.join(self.books, "src/RimMandrake/Utils/scratch_clone.py"), "clone",
                            "relentless %s %s" % (what, item), "--name", os.path.basename(d), "--checkout", "--fetch"],
                           cwd=self.books, env=env, capture_output=True, text=True, timeout=400,
                           stdin=subprocess.DEVNULL)
        if r.returncode:
            return None, "%s clone failed: %s" % ({"check": "checker"}.get(what, what), (r.stderr or r.stdout)[-300:])
        r = self.git(d, "checkout", "--quiet", "--detach", sha)
        if r.returncode and self.git(d, "cat-file", "-e", sha + "^{tree}").returncode:
            # the sha or its tree is not in the clone yet (a lagging object store): ask origin once before calling it failed
            self.git(d, "fetch", "--quiet", "origin", sha, timeout=400)
            r = self.git(d, "checkout", "--quiet", "--detach", sha)
        if r.returncode and not remade:
            # RELENTLESS_BREAKER_DIAGNOSE_UNREADABLE_TREE: still unreadable after origin was asked. A fetch cannot heal an
            # object store that holds the commit but lost a tree under it (negotiation says "have it" and sends nothing),
            # so a tracked-files-only check/help tree is removed and made again once, never parked warm for the next taker.
            gone = relentless_disk.remove_tree(d)
            self.store.journal({"at": iso(time.time()), "do": "clone_remade", "clone": os.path.basename(d), "item": item,
                                "missing": "tree of %s" % sha[:12], "why": (r.stderr or "")[-200:], "remove": gone})
            if gone is None:
                return self._detached_clone(d, sha, what, item, remade=True)
        return (d, None) if r.returncode == 0 else (None, "checkout %s: %s" % (sha, r.stderr[-200:]))

    def help_path(self, st):
        """The first help-ITEM-cN folder nobody holds, from help_count + 1. A failed removal leaves the last try's folder
        behind, and a consult refused on it opened the breaker (jam class help_folder_left, 2026-11-04): skip it, never
        delete it here (the reaper owns leftovers)."""
        n = (st.get("help_count") or 0) + 1
        path = lambda k: os.path.join(self.base, "clones", "help-%s-c%d" % (st["item"], k))
        for k in range(n, n + 50):
            if not os.path.lexists(path(k)):
                return path(k)
        return path(n)      # fifty leftovers: let the clone refuse by name, so the jam is seen, not hidden

    def help_checkout(self, st, sha):
        """The consult's clean tree. Not the item's clone: its uncommitted work is the story being withheld."""
        d, why = self._detached_clone(self.help_path(st), sha, "help", st["item"])
        if d:
            self.git(d, "remote", "set-url", "--push", "origin", "read-only-consult")
        return d, why

    def published(self, sha):
        """True / False, or None when origin could not be asked: a cached answer is no answer."""
        if self.git(self.books, "fetch", "--quiet", "origin", "main").returncode != 0:
            return None
        rc = self.git(self.books, "merge-base", "--is-ancestor", sha, "origin/main").returncode
        if rc == 128 and self.git(self.books, "cat-file", "-e", sha + "^{commit}").returncode:
            return False    # origin/main was just fetched whole and holds no such object: absent, not unknown
        return True if rc == 0 else False if rc == 1 else None      # 128 otherwise is git failing

    def relanded(self, st):
        """-> (commit, how) when the candidate's sha is no object here but origin/main holds its work under another
        hash (a landing rebased it after the worker named it), else None. CANDIDATE_SHA_REPAIR_LANDED_UNDER_NEW_HASH:
        four built items waited 10 h on publish_unknown, 2026-11-06."""
        c = st["candidate"]
        readable = lambda: self.git(self.books, "cat-file", "-e", c["sha"] + "^{commit}").returncode == 0  # noqa: E731
        if readable() or self.git(self.books, "fetch", "--quiet", "origin", "main").returncode != 0 or readable():
            return None     # readable (published() answers for it), or origin cannot be asked
        key = c.get("key")
        clone = st.get("clone")
        if not key and clone and os.path.isdir(os.path.join(clone, ".git")):
            key = landing_key(clone, c["sha"])
        until, since = c.get("at"), st.get("started_at")
        num = lambda v, d: int(v) + d if isinstance(v, (int, float)) else None    # noqa: E731
        found, how = find_landed(self.books, key, st["item"], base=st.get("base"), until=num(until, 1),
                                 since=num(since, -1))
        return (found, how) if found else None

    def head(self):
        return self.git(self.books, "rev-parse", "origin/main").stdout.strip() or None

    def existed(self, sha, path):
        """True / False: `path` is in `sha`'s tree; None when git cannot say (the sha unreadable here)."""
        if self.git(self.books, "cat-file", "-e", sha + "^{commit}").returncode:
            return None
        return self.git(self.books, "cat-file", "-e", "%s:%s" % (sha, path)).returncode == 0

    def changed(self, base, sha, item):
        """Files of the final commit plus every commit since the item's base that names the item (the brief makes
        workers name it), so a hook change followed by a doc commit does not escape its live line."""
        r = self.git(self.books, "show", "--format=", "--name-only", "--diff-merges=first-parent", sha)   # Codex #4
        got = set(x for x in r.stdout.splitlines() if x.strip()) if r.returncode == 0 else set()
        if base:
            r = self.git(self.books, "log", "--format=", "--name-only", "--diff-merges=first-parent", "--grep=" + item,
                         "%s..%s" % (base, sha))
            got |= set(x for x in r.stdout.splitlines() if x.strip())
        return sorted(got)

    def commit_time(self, sha):
        r = self.git(self.books, "show", "-s", "--format=%ct", sha)
        return int(r.stdout.strip() or 0) if r.returncode == 0 else 0

    # the units
    def launch(self, st, run, prompt, agent, clone, max_s, extra_env, wall=()):
        """-> None, or why it did not start. The caller persisted `run` before this call. wall: systemd properties."""
        rl = self.RL
        role = {"name": "relentless", "seat": self.r["seat"], "clone": clone, "model": self.r["model"],
                "run_max_s": max_s}
        claude = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
        os.makedirs(os.path.dirname(run["out"]), exist_ok=True)
        relentless_usage.note_clone(run, clone)        # where its transcripts will be, should the run never print a result
        argv = rl.launch_argv(role, run["unit"], prompt, run["out"], run["err"], claude)
        if "TMPDIR" not in extra_env:   # a walled run brings its own, in its box: run_tmp's root is behind its wall
            try:        # the run's own TMPDIR; sweep_run_tmp deletes it once the unit and every process of it are gone
                tmpdir = run_tmp.prepare(run["unit"])
            except OSError as e:
                return "run tmp dir: %s" % e
            at = argv.index("--")
            argv[at:at] = sum((["--setenv", "%s=%s" % kv] for kv in run_tmp.env(tmpdir).items()), [])
        at = argv.index("--")
        argv[at:at] = ["--setenv", "RIMFLOW_BRIDGE_SEAT=" + BRIDGE_HOLDER,     # its worker's `bridge take` is Relentless's
                       "--setenv", "WSLENV=RIMFLOW_BRIDGE_SEAT"]               # and a python.exe preflight it runs reads the same name
        at = argv.index("--")
        if agent == relentless_game.STAGE_AGENT:    # STAGING_REWIRE_PYTHON_NOT_AN_LLM: the python stager, same unit shape
            fb = argv[at + 1:]
            o = fb.index("--output-format")
            fb[o:o] = ["--agent", self.r["pilot_agent"]]       # its one LLM road: exec'd on an unhandled exception only
            plan = dict(st.get("_stage_plan") or {}, clone=clone, fallback=fb)
            pf = os.path.splitext(run["out"])[0] + ".stage.json"
            with open(pf, "w", encoding="utf-8") as f:
                json.dump(plan, f)
            tool = os.path.join(clone, "src", "RimMandrake", "rimflow", "relentless_stage.py")
            argv = argv[:at] + list(wall) + sum((["--setenv", "%s=%s" % kv] for kv in extra_env.items()), []) + \
                ["--", sys.executable, tool, "run", "--plan", pf]
            r = subprocess.run(argv, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
            return ("systemd-run exit %d: %s" % (r.returncode, (r.stdout + r.stderr)[-200:])) if r.returncode else None
        if agent == VENDOR_AGENT:       # the Consult port: a python body in the same unit shape, so alive/stop/settle hold
            pf = os.path.splitext(run["out"])[0] + ".prompt.md"
            with open(pf, "w", encoding="utf-8") as f:
                f.write(prompt)
            tool = os.path.join(clone, "src", "RimMandrake", "rimflow", "relentless.py")
            argv = argv[:at] + list(wall) + sum((["--setenv", "%s=%s" % kv] for kv in extra_env.items()), []) + \
                ["--", sys.executable, tool, "help-vendor", "--item", st["item"], "--prompt-file", pf]
            r = subprocess.run(argv, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
            return ("systemd-run exit %d: %s" % (r.returncode, (r.stdout + r.stderr)[-200:])) if r.returncode else None
        env = []
        for k, v in extra_env.items():
            env += ["--setenv", "%s=%s" % (k, v)]
        argv = argv[:at] + list(wall) + env + argv[at:]
        o = argv.index("--output-format")
        argv[o:o] = ["--agent", agent] + (["--resume", run["resume"]] if run.get("resume") else [])
        r = subprocess.run(argv, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        return ("systemd-run exit %d: %s" % (r.returncode, (r.stdout + r.stderr)[-200:])) if r.returncode else None

    def sweep_run_tmp(self):
        """Every run dir whose run is over goes (run_tmp.sweep): each end path, a crash and a dead engine alike."""
        return run_tmp.sweep()

    def drop_run_tmp(self, run):
        return run_tmp.drop((run or {}).get("unit"))

    def account_loss(self, run, clone, since, box=None):
        """-> {"kind", "why"} when the account, not the item, ended this dead run; else None."""
        return relentless_account.loss(run, clone, since, box=box)

    def death_note(self, run):
        """-> the .err tail of a dead run that left no result object, else None. A Marker that dies at start (EACCES under
        its own wall, 2026-11-03) writes its reason there and nothing to .json: thirty such deaths read checker_lost, silent."""
        return death_note(run)

    def alive(self, run):
        """Unit, scope, or a marked process: any one of them means the run is not over."""
        if not run:
            return False
        rl = self.RL
        for u in (run.get("unit"), run.get("scope")):
            if u and rl.unit_state(u) in rl.ACTIVE:
                return True
        try:
            return bool(rl.scan_marked(run.get("marker"), since=run.get("at"))[0])
        except Exception:  # noqa: BLE001
            return True         # a failed look is not a death: keep the clone owned until a look succeeds

    def stop(self, run, force):
        self.RL.stop(run["unit"], run.get("scope"), marker=run.get("marker"), force=force, seat=self.r["seat"])

    def measure(self, run):
        """-> (weighted tokens, basis): the result object, else the run's transcripts, else (0, "estimated")."""
        if not run:
            return 0, "estimated"
        try:
            return relentless_usage.measure(self.RL, run)
        except Exception:  # noqa: BLE001
            return 0, "estimated"

    def tokens(self, run):
        return self.measure(run)[0]

    def circling_tree(self, st, outputs=()):
        return circling.tree_reading(st["clone"], st.get("base") or "HEAD", POOL_NOISE, outputs)

    def transcripts(self, st):
        return circling.transcript_paths(st["clone"], st["started_at"])

    def activity(self, st):
        """Newest write in the item's transcripts: a worker in a long test is not silent, only its beat is."""
        slug = re.sub(r"[^A-Za-z0-9]", "-", st["clone"] or "")
        d = os.path.expanduser("~/.claude/projects/" + slug)
        best = 0
        try:
            for e in os.scandir(d):
                best = max(best, e.stat().st_mtime)
        except OSError:
            pass
        return best

    def mem_gb(self):
        with open("/proc/meminfo") as f:
            for ln in f:
                if ln.startswith("MemAvailable:"):
                    return int(ln.split()[1]) / 1048576.0
        return 0.0

    def paused(self):
        try:
            import dispatcher
            return bool(dispatcher.paused_now())
        except Exception:  # noqa: BLE001
            return True         # the owner's pause cannot be read: that is not "not paused"

    def live_check(self, line, not_before=0, now=None):
        # relentless_reach.live_reading calls check(line, now=now): without `now` every live line read COULD NOT READ
        # (LIVECHECK_FIX_TYPEERROR_BLINDS_EVERY_LINE)
        import live_line
        return live_line.check(line, now=now, not_before=not_before)

    def live_round_alive(self, pid):
        """A live round still runs as `pid`: its argv is the script run with `round`, so a reused pid (a `tail -f` of the
        script included) is not it. Overlap itself is the round's flock; this only keeps the tick from launching twice."""
        try:
            with open("/proc/%d/cmdline" % int(pid), "rb") as f:
                argv = f.read().split(b"\0")
        except (OSError, ValueError):
            return False
        script = os.path.join(self.books, "src/RimMandrake/rimflow/relentless_live_round.py").encode()
        return len(argv) >= 3 and argv[1] == script and argv[2] == b"round"

    def live_round_launch(self):
        """Start one live round detached (its own session: the oneshot tick ends long before it). -> pid."""
        os.makedirs(os.path.join(self.base, "live"), exist_ok=True)
        with open(os.path.join(self.base, "live", "round.out"), "a", encoding="utf-8") as out:
            p = subprocess.Popen(["python3", os.path.join(self.books, "src/RimMandrake/rimflow/relentless_live_round.py"),
                                  "round"], cwd=self.books, env=dict(os.environ, RELENTLESS_ROOT=self.base, PATH=windows_path(os.environ.get("PATH", ""))),
                                 stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        return p.pid


WINDOWS_DIRS = relentless_live.WINDOWS_DIRS
windows_path = relentless_live.windows_path      # one rule: the tick, the round and game_started all take it


def clone_item(c):
    """The item a pool clone's folder is named for: ITEM, ITEM.qN, check-ITEM-cN or help-ITEM-cN."""
    name = os.path.basename(c.rstrip("/"))
    for pre in ("check-", "help-"):
        if name.startswith(pre):
            return name[len(pre):].rsplit("-c", 1)[0]
    return re.sub(r"\.q\d+$", "", name)


def foreign_seat(r):
    return (r.get("staffing") or {}).get("foreign_seat")


def foreign_retired(r):
    """The other seat has no window any more (FOUNDRY, owner card 2026-11-02): its tree will never hear a close and holds
    no unpublished word, so nothing waits on it (FOUNDRY_CLONE_RESCUE_GHOST_HOLDS_CLOSINGS: 36 closes held up to 48 h)."""
    return bool((r.get("staffing") or {}).get("foreign_retired"))


def foreign_ok(it, r):
    """An item of the other seat a worker may take. Only `proposed`: its `next` offers only `ready`, so a head reaches a
    proposed item through `claim`, which the guard refuses from the reservation on. The classes it must not take are
    in the rules; design section 13 says why each."""
    cfg = r["staffing"]
    return (it.state == "proposed" and getattr(it, "kind", None) not in cfg.get("foreign_kinds_exclude", [])
            and not re.search(cfg.get("foreign_exclude") or "(?!)", "%s %s" % (it.id, it.title or ""), re.I))


def parked_ids(r):
    """Items an owner ruling parked on a list (the paint list, BIOME_PAINT_ONCE_AT_THE_END_1: "done at the final world
    painting, not before"), by data: r["pool_parked_lists"] maps a list item to the ids it parks; the list item and each id
    are out of the line. Held in the rules, not read from item prose: the blind checker's tree has no items/, and a
    supervisor tick must never hinge on a prose file (RELENTLESS_FILLER_FIX_TOO_KEEN_ON_PARKED). The list is released
    by deleting its key when the list item closes."""
    out = set()
    for lst, ids in (r.get("pool_parked_lists") or {}).items():
        if lst.startswith("_"):
            continue
        out.add(lst)
        out.update(ids)
    return out


def pool_excluded(item, r):
    """Out of the line by data: pool_ids_exclude, or parked on a list (parked_ids). The pool, fill and retire ask this
    one question, so a parked item that comes back from a snag is handed back, never relaunched at the top."""
    return item in r.get("pool_ids_exclude", []) or item in parked_ids(r)


def eligible(it, r, world=None, now=None):
    """`world` given: a block counts only while it HOLDS (priority.block_holds: a finished predecessor or a passed
    date releases it); without one, any block keeps the item out."""
    if world is not None:
        blocked = pkg("priority").block_holds(world, it, int(time.time() if now is None else now))
    else:
        blocked = it.blocked
    return (it.owner in r["pool_seats"] and it.state in ("proposed", "ready") and not blocked
            and it.needs != "owner" and (it.needs in r["pool_needs"] or it.needs in relentless_game.pool_needs(r))
            and getattr(it, "kind", None) not in r.get("pool_kinds_exclude", [])
            and not pool_excluded(it.id, r) and not lease_live(it, now)
            and not hand_check(it, r)
            and (it.owner != foreign_seat(r) or foreign_ok(it, r)))


def lease_live(it, now=None):
    """Does a LIVE seat lease hold `it`? LAPSED_LEASES_REPAIR_GHOSTS_HOLD_THE_KEYS: a lease that expired or was released
    holds nothing (model.lease_status, judged from its own `expires`), so it never keeps an item out of the pool; the
    rank() side (priority.offerable_state) already read it this way."""
    if not getattr(it, "lease", None):
        return False
    return pkg("model").lease_status(it, int(time.time() if now is None else now)) == "live"


HAND_CHECK_SAID = ("check by hand, close with evidence")
HAND_CHECK_RULING_SHORT = "owner 2026-11-05: the pipeline does not bless a change in the game"


def hand_check(it, r):
    """-> why `it` is a hand check, or None. PIPELINE_BLESS_ENFORCE_HAND_CHECKS_SMALL: an item whose only remaining work
    is a small manual validation (installed art is his pick, a value reads back, a deploy landed) is never enrolled or
    rechecked; the agent that made the change checks it by hand and closes it with the evidence. Data, not judgment:
    rules hand_check.ids (an id the sweep judged, with its why) or a hand_check.title_rx match on its title."""
    hc = r.get("hand_check") or {}
    why = (hc.get("ids") or {}).get(getattr(it, "id", None))
    if why:
        return why
    title = getattr(it, "title", None) or ""
    for rx in hc.get("title_rx") or ():
        try:
            hit = re.search(rx, title)
        except (re.error, TypeError):
            continue        # a bad pattern is hand_check_lint's to report, never a crash of the tick (Codex r3)
        if hit:
            return "its title reads as a hand check (%s)" % rx
    return None


def hand_note(why, makers):
    """The bounce, one ledger note under NOTE_MAX: what to do first, so a cut never loses it, then who and why."""
    head = "%s (maker %s): Relentless will not enrol or recheck it, %s. Why: " % (
        HAND_CHECK_SAID, ", ".join(makers) or "unknown", HAND_CHECK_RULING_SHORT)
    return (head + why)[:NOTE_MAX]


def hand_check_lint(r, items):
    """-> [problem, ...] in rules hand_check: an id the ledger never filed, an empty why, a pattern that does not compile."""
    hc, out = r.get("hand_check") or {}, []
    for i, why in sorted((hc.get("ids") or {}).items()):
        if i not in items:
            out.append("hand_check.ids %s: not on the ledger" % i)
        if not (why or "").strip():
            out.append("hand_check.ids %s: no why" % i)
    for rx in hc.get("title_rx") or ():
        try:
            re.compile(rx)
        except re.error as e:
            out.append("hand_check.title_rx %r: %s" % (rx, e))
        except TypeError as e:  # a non-string entry hand_check skips: named, never a crash of the lint (Codex r4 part2 #2)
            out.append("hand_check.title_rx %r: not a pattern string (%s)" % (rx, e))
    return out


def hand_checks_cli(r, lint=False, bounce=False):
    """The 2026-11-05 sweep, re-runnable: every open item the rule matches; --bounce writes the note hand_back writes
    (once per item, through this tree's rimflow) for those never enrolled."""
    model = pkg("model")
    evs = model.read()
    w = model.replay(evs)
    rc = 0
    if lint:
        probs = hand_check_lint(r, w.items)
        for x in probs:
            print("LINT " + x)
        rc = 1 if probs else 0
    told = {ev.get("id") for ev in evs if ev.get("event") == "note" and HAND_CHECK_SAID in (ev.get("text") or "")}
    for it in sorted(w.items.values(), key=lambda x: x.id):
        if it.state not in ("proposed", "ready", "doing", "built"):
            continue
        why = hand_check(it, r)
        if not why:
            continue
        print("%-8s %-8s %s  %s%s" % (it.state, it.needs, it.id, why, "  (told)" if it.id in told else ""))
        if bounce and it.id not in told:
            makers = [m for m in dict.fromkeys(list(it.makers or []) + [it.built_by, it.owner]) if m]
            res = subprocess.run([sys.executable, os.path.join(HERE, "cli.py"), "note", it.id, "--text",
                                  hand_note(why, makers),
                                  "--why", "relentless hand-checks --bounce: the 2026-11-05 queue sweep"],
                                 capture_output=True, text=True, timeout=120)
            if res.returncode:
                print("  note refused: " + (res.stderr or res.stdout)[-300:])
                rc = 1
    return rc


HAND_BACK_FROM = ("queued", "candidate", "held", "blocked")


def hand_back(store, fx, r, now, acts):
    """A hand-check item already in the store (enrolled before the rule, or its title changed) is bounced, not run or
    rechecked: one ledger note to its makers, the ledger lease handed back if ours, then `retired`, which nothing enrols
    again. A running item is left to end; its candidate is bounced here before any check starts. A refused note or
    reclaim keeps the state as it is, so the next tick tries again."""
    if not (r.get("hand_check") or {}) or not hasattr(fx, "ledger_items"):
        return
    try:
        w = fx.ledger_items()[1]
    except Exception as e:  # noqa: BLE001  an unreadable ledger bounces nothing this tick
        acts.append({"do": "error", "item": None, "why": "hand_back %s: %s" % (type(e).__name__, e)})
        return
    for st in store.states():
        if st["status"] not in HAND_BACK_FROM:
            continue
        it = w.items.get(st["item"])
        why = hand_check(it, r) if it is not None else None
        if not why:
            continue
        makers = [m for m in dict.fromkeys(list(getattr(it, "makers", None) or []) + [getattr(it, "built_by", None),
                                                                                       it.owner]) if m]
        err = fx.ledger_note(st["item"], hand_note(why, makers))
        if not err and st.get("ledger_started") and it.state == "doing" and it.owner == r.get("seat"):
            err = fx.ledger_reclaim(st["item"])
        if err:
            acts.append({"do": "hand_back_waits", "item": st["item"], "why": err})
            continue
        with store.lock():
            cur = store.load(st["item"])
            if cur["status"] not in HAND_BACK_FROM:
                continue
            was = cur["status"]
            cur["status"] = "retired"
            cur.pop("recheck_at", None)
            store.save(cur)
            store.attempt(st["item"], {"at": iso(now), "gen": cur["gen"], "end": "hand_check", "said": why, "from": was})
            store.journal({"at": iso(now), "do": "hand_back", "item": st["item"], "why": why, "from": was})
        acts.append({"do": "hand_back", "item": st["item"], "from": was})


# ---------------------------------------------------------------- prompts

LIVE_FAIL_RX = re.compile(r"(?:^|;\s*)(\S+) FAIL on the running game")


def ending_history(attempts):
    """-> the endings on record, one short line each, oldest first: what each generation ended with and the code it
    stood on (its finish sha), and any classification a worker wrote. Generation ten of an item had seen one line of
    generation nine's ending, never that one through nine all changed code against the same broken instrument."""
    out, sha = [], None
    for a in attempts or []:
        if a.get("end") == "finish":
            sha = a.get("sha")
            continue
        if a.get("explained"):      # the explanation's mechanism whole, and the item that carries its follow-up
            out.append("gen %s explained it %s: %s (follow-up: %s)" % (a.get("gen"), a["explained"], a.get("mechanism") or "",
                                                                     a.get("cause")))
            continue
        if a.get("classified") or a.get("warrant"):     # attributions whole (CHURN_BREAKER_BUILD_RETRY_NEEDS_A_WARRANT)
            out += relentless_breakers.attributions_view([a])
            continue
        end = a.get("end")
        if not end or end in ("owner_call",):
            continue
        first = " ".join((a.get("detail") or a.get("said") or "").split())
        out.append("gen %s ended %s%s%s: %s" % (a.get("gen"), end, " (%s)" % a["class"] if a.get("class") else "",
                                               " on code %s" % sha[:10] if sha else "", first))
    return out[-HISTORY_MAX:]


def repeated_live(attempts):
    """-> {clause: [the shas it read FAIL on]} for each live clause that read FAIL on two or more different builds: the
    code changed between and the clause did not move, which is as likely the instrument as the work."""
    seen, sha = {}, None
    for a in attempts or []:
        if a.get("end") == "finish":
            sha = a.get("sha")
        elif a.get("end") == "game_fail":
            for c in LIVE_FAIL_RX.findall(a.get("detail") or ""):
                if sha and sha not in seen.setdefault(c, []):
                    seen[c].append(sha)
    return {c: v for c, v in seen.items() if len(v) >= 2}


def subagent_cap(st, r):
    """RELENTLESS_SUBAGENT_DECIDE_THREE_PER_BUILDER: how many subagents one builder run may start (rules
    worker_subagent_cap; a pilot sitting, whose agent has no Agent tool, none; an unset or bad rule, none). Their
    tokens are charged with the run's (relentless_usage.subagent_tokens)."""
    if piloting(st):
        return 0
    n = r.get("worker_subagent_cap", 0)
    return max(0, min(n, 3)) if type(n) is int else 0


def subagent_rule(st, r):
    n = subagent_cap(st, r)
    if not n:
        return "no subagents"
    return ("at most %s subagent%s in this run (the Agent tool; model sonnet or opus, never haiku; a narrow brief and a "
            "short report each; never one that commits, pushes or calls relentless.py; a subagent blocks you, so keep each "
            "under ~8 minutes and beat before and after; every token they spend is charged to this item)"
            % ({1: "one", 2: "two", 3: "three"}[n], "" if n == 1 else "s"))


def worker_prompt(st, text, learned, r, history=None, causes=None):
    i, g = st["item"], st["gen"]
    rc = "python3 src/RimMandrake/rimflow/relentless.py"
    head = ["You carry one item until it is proven. You are one worker in a line: others came before you and another "
            "follows if you stop. Everything you know must be on disk.",
            "Item %s, generation %d, attempt %d, approach %s." % (i, g, st["attempts"], st["approach"]),
            "Your cwd is this item's own clone; uncommitted work from earlier workers is yours to continue.",
            "Report ONLY with these (a refusal with exit 3 means your lease is gone: stop at once, push nothing):",
            "  %s beat --item %s --gen %d" % (rc, i, g),
            "  %s learn --item %s --gen %d \"what you found, what failed, what to try next\"" % (rc, i, g),
            "  %s contract --item %s --gen %d --proof \"the command or look that proves it\" "
            "[--live \"<live line>\"] [--game A2,B3 --game-why \"...\" [--no-offline \"...\"]] [--offbox ADAPTER] [--why ...]" % (rc, i, g),
            "  %s snag --item %s --gen %d --class <slug> \"what stopped you\"" % (rc, i, g),
            "  %s finish --item %s --gen %d --sha <published sha> --evidence \"<paths and results>\"" % (rc, i, g),
            "  %s help --item %s --gen %d \"what you need a fresh eye on\"" % (rc, i, g),
            "Set the contract BEFORE you edit, from the item's own words. A line of `learn` after every finding and "
            "at least every 20 minutes. Commit explicit paths and land with ./publish; every commit subject names the item id; `finish` names a sha on "
            "origin/main. Then a blind checker reruns your proof on that sha; it does not see your notes. Never run "
            "`rimflow close`, `implemented`, `release` or `claim` on this item: the supervisor owns its ledger state.",
            "A hook, systemd unit, dispatcher_schedule.json or ops_watch_rules.json change, or an OPS_ alarm item, needs --live with one of: "
            "`unit=rm-foo.timer reading=<path> max_age=6h`, `hook=block_foo.py`, `once: why`.",
            "The checker runs walled: no ssh or other machine; it has a read-only git history at your sha (no refs or remote), "
            "python3 with cv2/numpy and the Windows build stage (winbuild.py) (relentless_box.json); D:\\ClaudeWork and "
            "/mnt/d/ClaudeWork/rimmandrake read empty except the paths under them your contract, finish evidence or item text "
            "names (bound read only; a progress or handoff file never is), no other Windows program. `finish` first runs your "
            "contract's proof as written in that box (relentless_boxrun); `%s boxrun --item %s --gen %d` runs it at HEAD before "
            "you land. When the proof's truth lives there, add --offbox NAME naming a supervisor adapter from "
            "relentless_rules.json offbox_adapters (%s): the supervisor runs it outside the wall at check time and hands the "
            "checker its raw output. You cannot pass a command; a reading no adapter makes is a snag. A checker that still "
            "cannot reach the evidence says UNMEASURED, which sends nothing back to you. `contract` refuses a proof that "
            "names what the box hides (a masked path, git refs or a remote, ssh, a Windows program) unless --offbox routes it or "
            "--reach-ok says why the box can still show it; the live line is read for the checker outside the wall." % (rc, i, g, ", ".join(sorted(relentless_wall.adapters(rules()))) or "none yet"),
            "A contract with no live line may gain one from any worker: the same --proof plus --live and --why.",
            "Work done but the contract's proof broken (unrunnable, misnamed, measured where the box cannot reach)? Repair HOW, "
            "never WHAT: `%s rebind --item %s --gen %d --proof \"...\" --before \"what it measured\" --after \"what the new one "
            "measures\" --behaviour same --defect \"evidence it is broken\"`, then `snag --class binding_repair --blocker judge`: "
            "an independent judge applies or refuses it. A typed number, a dropped clause or a changed obligation is refused." % (rc, i, g),
            "An item whose fix died before (`rimflow show` says OWES A GUARD) closes only with a class guard test shown failing on "
            "the instance: `rimflow guard <ID> --test <selftest*.py>` before the fix lands, then commit the test and the ledger shard.",
            "Hit a wall? `snag` and exit: the item goes back to the top with your finding. Do not ask anyone. If "
            "what stopped you is time, not work (a sample filling), say so: `snag --wait-hours N`. Only a "
            "true design/RimMandrake/delegation_policy.md section 2 call goes up: `snag --class owner_call --section "
            "<what, quoted> ...`. Waiting on another item, a judge, the live game or something outside: `snag --class "
            "blocked_by_predecessor --on <ITEM>` (or `--blocker judge|live|external|owner`): the ledger records the "
            "block and no worker is sent until it ends. `help` sends a fresh agent the failed approaches on record (refused if there are "
            "none); its options land in the state file (`relentless.py show <item>`) and in the next worker's brief.",
            "What the seats already learned is in skills: load the one your step needs, once. `clone-landing-commits` "
            "before a commit; `rimworld-modding` for defs and patches; `rimworld-deploy` before testing anything in "
            "game (writing a file is not deploying it); `live-debugging-proof-harness` and `rimbridge` for a live proof; "
            "`measuring-large-artifacts` and infrastructure/state/facts/instrument_traps.md before you trust a count. "
            "Owner preferences no skill holds yet: %s (an index; read only the entries your item touches)." % MEMORY_INDEX,
            "Never live-test a flyer's flight. No worldgen. Foreground commands, timeouts under 540 s, %s, "
            "bulk output to files. src/RimMandrake/Utils/arena/ are not yours to touch." % subagent_rule(st, r)]
    if relentless_game.cfg(r)["enabled"]:
        head += relentless_game.BRIEF
    if st.get("proof_only"):
        head.append("PROOF ONLY: a blind checker read the code at %s as WEAK: the proof has holes, so the work is unproven, not "
                    "sound. The proof would stay green if it broke. The gaps are in the last ending below. Leave the code alone. Strengthen the proof until each "
                    "gap goes red when its clause is broken: show that with the mutant or probe the checker named, then "
                    "restore the code. Land proof files only: the supervisor refuses anything else, and refuses a finish "
                    "with no new commit. Never loosen or remove an existing check. The contract may change with --why, "
                    "only to reach more of the item. If the stronger proof is red on the code as it stands, the code "
                    "does not hold: land the proof, then `snag --class %s` with what went red, and the next worker may "
                    "fix the code." % (st["proof_only"]["sha"], PROOF_DEFECT))
    elif st["approach"] == "redesign":
        head.append("REDESIGN: the same failure came back too often. Read the record below, write a DIFFERENT approach "
                    "with `learn` before you edit anything, and change the contract with --why if it was the problem. "
                    "A different approach may be: deliver the item's own substance standalone; split it (file the parts "
                    "--for BENCH, then `snag --class blocked_by_predecessor --on <first part>`); or, if no approach is "
                    "left, `snag --class owner_call --section \"<the call>\"`. Retrying the same road is not one.")
        if ((st.get("last_fail") or {}).get("class") or "").startswith("contract"):
            head.append("CONTRACT WALL: the last worker found the set contract itself wrong (its ending is below). If the "
                        "code at hand is sound, the different approach is the contract: replace it with `contract --proof "
                        "... --why` so it measures the item from where the checker runs, prove it green, and finish; "
                        "redesign the code only if the new contract shows it does not hold.")
    ps = st.get("pilot_step")
    if piloting(st) and not st.get("proof_only"):
        head.append("PILOT: this needs eyes on the running thing. Run `python3 src/RimMandrake/rimflow/cli.py pilot %s`, "
                    "follow that brief yourself, and EXPLAIN what you saw (not only whether the test ran): `explain` with the "
                    "mechanism, evidence per step, theories ruled out and the follow-up item for its cause." % i)
        if ps:
            head.append("PILOT STEP: you were called as a pipeline step, not a late rung: %d live endings since the last pilot sitting (the last "
                        "%s: %s) and no rebuild has explained them. Your job is the explanation, not another build: record "
                        "it with `explain`, end the sitting with `python3 src/RimMandrake/rimflow/cli.py note %s --text "
                        "\"TESTPILOT_SAT: <what you saw>\"`, and add a `learn` line headed TEACH: naming any move you made "
                        "that a live builder's brief does not carry yet (below), so Relentless's live mode can learn it. Fix "
                        "the code only when the explanation names the mod (MOD) and the fix is small; otherwise snag on the "
                        "cause." % (ps["after"], ps["class"], ps.get("detail") or "", i))
    if piloting(st) or st.get("live_iter") or st.get("diagnose_owed"):
        head.append("LIVE MOVES (what the 2026-11-04 Test Pilot sitting did that live builders did not; do these before "
                    "any rerun or rebuild): " + "; ".join("(%d) %s" % (n + 1, m) for n, m in enumerate(LIVE_MOVES)) + ".")
    if st.get("live_iter"):
        li = st["live_iter"]
        head.append("LIVE: the running game (started %s) holds your build %s, and the proof of %s exited FAIL on it: "
                    "a reading, not yet a verdict on the mod (explain it first, below). Work it THERE as far "
                    "as it goes before any rebuild (owner 2026-11-02, to save game loads): take the bridge with `python3 "
                    "src/RimMandrake/rimflow/cli.py bridge take --idle-ok --for \"relentless live iteration %s\"`, renew "
                    "it while you work, release it (`bridge release --mine`) when you step away (with the bridge not held for "
                    "this item %d min your hold on the game lapses and the next item proves); read the failing proof's "
                    "log, run bridge experiments, hot-reloadable XML/def changes and reads (`rimbridge`, "
                    "`live-debugging-proof-harness`). You are the game's one live user until you finish, snag or record "
                    "`%s reload-needed --item %s --gen %d \"what needs the reload and why the running game cannot take it "
                    "(a DLL change, a def only a cold load reads)\"` — the proof is required, and it frees the game for "
                    "the next item; then go on offline and land the fix. If the game did not start at that time (`./game`), it no "
                    "longer runs your build: record reload-needed at once and work offline. Never restart, fullscreen or focus the game; "
                    "never a flyer." % (iso(li["started"]), (li.get("sha") or "")[:12], ", ".join(li.get("clauses") or []),
                                        i, relentless_game.cfg(r)["live_idle_s"] // 60, rc, i, g))
    if st["contract"]:
        head.append("Contract so far: %s" % json.dumps(st["contract"]))
    if st["last_fail"]:
        head.append("Last ending: %s: %s" % (st["last_fail"]["class"], st["last_fail"]["detail"]))
    spent, limit = st.get("spent") or 0, r.get("item_spend_limit")
    if spent:
        # owner 2026-11-05: "A high past token cost indicates that something is really wrong... either in the
        # validation or the work itself." The builder sees the bill; the blind Judge never does.
        head.append("COST SO FAR: %.1fM weighted tokens over %d generation(s), %d return(s)%s." % (
            spent / 1e6, st.get("gen", 0), st.get("total_failures", 0),
            " (advisory item limit %.1fM)" % (limit / 1e6) if limit else ""))
        if limit and spent * 2 >= limit:
            head.append("HIGH COST: this much spend means something is really wrong, in the validation or in the work. "
                        "Before any edit, decide which with evidence and record it with `learn`: a proof that cannot "
                        "go green on sound work is a contract or harness defect (repair it as the rules above say), "
                        "not a reason for another round of code.")
    if st.get("diagnose_owed"):
        head.append("DIAGNOSE FIRST: the last ending (%s) is the supervisor's reading of an exit code, not a diagnosis; no "
                    "agent has read its log. Your first job is to EXPLAIN it, not to rerun it (owner 2026-11-04: \"it needs "
                    "to write a coherent explanation of failures, not just indicate them\"). Before you edit any code, read "
                    "that log (`live-debugging-proof-harness`) and record %s; `finish` is refused until you do, and a "
                    "CLASSIFY label does not count. MOD (the proof asked and the mod's answer missed): fix the mod. CONTRACT "
                    "(the set proof cannot measure the item): `snag --class contract_wrong` and the next worker replaces "
                    "it. HARNESS in this item's own proof script: fix the proof, not the code. SITE or HARNESS outside it "
                    "(the bridge, the box, a shared tool, the staged world or load, a wrong tier or stale deploy): that is "
                    "not your work - explain it with the repair item as --cause, then `snag --class %s --on <that item> "
                    "\"<the log line>\"`: the item waits on the repair with no strike and comes back when it closes."
                    % (st["diagnose_owed"]["class"], relentless_explain.ask(rc, i, g), INSTRUMENT))
        if causes:
            head.append("Cause book: the open follow-up items other failures were explained by (join one when it is "
                        "the same cause):")
            head += causes
    at = st.get("attribution") or {}
    if at and at.get("at", 0) >= (st.get("last_fail") or {}).get("at", 0):
        head.append(relentless_attrib.brief_line(at))
    if st.get("warrant_owed") and not st.get("proof_only"):
        head.append(relentless_breakers.BRIEF)
    rep_live = repeated_live(history)
    if rep_live:
        head.append("SAME CLAUSE, NEW CODE, SAME FAIL: %s. Changing the code did not move it, which points at the site, "
                    "the instrument or the contract as much as at the mod. No code edit before the explanation above "
                    "names the line that rules them out." % "; ".join(
                        "%s read FAIL on %d builds (%s)" % (c, len(v), ", ".join(x[:10] for x in v)) for c, v in rep_live.items()))
    hist = ending_history(history)
    if len(hist) > 1:
        head.append("Endings on record (oldest first):")
        head += ["  " + x for x in hist]
    if st.get("help_options"):
        head.append("FRESH EYES: an agent with no history%s read the failed approaches and offers these hypotheses. Pick "
                    % (" (a second vendor)" if st["help_options"].get("vendor") == VENDOR_AGENT else "") +
                    "one, or refute each with evidence; record which with `learn` before you edit.")
        head += ["  %d. %s (confirm or kill by: %s)" % (n + 1, o["idea"], o["observe"])
                 for n, o in enumerate(st["help_options"]["options"])]
    return "\n".join(head + ["", "--- item ---", text, "", "--- learned so far ---", learned[-8000:]])


def attributions(tried):
    """The classifications and warrants on record, whole: a fresh pair of eyes reads what was established, not a cut."""
    rows = relentless_breakers.attributions_view(tried)
    return ["", "--- attributions on record ---"] + ["  " + x for x in rows] if rows else []


def help_prompt(st, text, tried, nonce, r, record=None):
    """Cold on purpose: the record of what ended and how, never learned.md, the story that drove the circling."""
    rc = "python3 src/RimMandrake/rimflow/relentless.py"
    most = r["circling"]["help_options_max"]
    rows = ["  gen %s ended %s: %s" % (a.get("gen"), a.get("end"), a.get("detail") or "") for a in tried[-12:]]
    return "\n".join([
        "You are a fresh pair of eyes. You have no history with this item and no stake in it. Workers tried, and the "
        "attempts below failed. Your cwd is a clean tree at origin/main. Read anything; change nothing: no edits, no "
        "push, no ledger.",
        "Give up to %d options the workers have not tried. Each is a hypothesis, never a verdict, and carries the "
        "single observation that would confirm or kill it." % most,
        "Then run this once and stop:",
        "  %s help-answer --item %s --nonce %s --option \"idea | the one observation\" [--option ...]" % (rc, st["item"], nonce),
        "", "Why you were called: %s" % st["help"]["why"], "Contract: %s" % json.dumps(st["contract"]),
        "", "--- failed approaches ---"] + rows + attributions(record or tried) + ["", "--- item ---", text])


def help_prompt_vendor(st, text, tried, r, record=None):
    """Round two's prompt, for a model that reads only this text: the same cold record, answered as OPTION lines."""
    most = r["circling"]["help_options_max"]
    rows = ["  gen %s ended %s: %s" % (a.get("gen"), a.get("end"), a.get("detail") or "") for a in tried[-12:]]
    return "\n".join([
        "You are a fresh pair of eyes from a second vendor. A first consult already gave options and the workers still "
        "failed. You have no history with this item and no stake in it; the record below is all you get.",
        "Give 1 to %d options the workers have not tried. Each is a hypothesis, never a verdict, and carries the single "
        "observation that would confirm or kill it." % most,
        "Answer with those lines only, each exactly:", "  OPTION: <idea> | <the one observation>",
        "", "Why you were called: %s" % st["help"]["why"], "Contract: %s" % json.dumps(st["contract"]),
        "", "--- failed approaches ---"] + rows + attributions(record or tried) + ["", "--- item ---", text])


def checker_prompt(st, text, nonce, readings=()):
    i = st["item"]
    c = st["candidate"]
    rc = "python3 src/RimMandrake/rimflow/relentless.py"
    return "\n".join([
        "You are a blind checker. You did not do this work and you have no record of how it went. Your cwd is a clean "
        "tree at exactly commit %s." % c["sha"],
        *relentless_wall.RULE,
        "Then run exactly one of:",
        "  %s verdict --item %s --nonce %s PASS \"what you ran and saw\"" % (rc, i, nonce),
        "  %s verdict --item %s --nonce %s WEAK \"the runs you made and what each showed, then each gap and the mutant or "
        "probe that shows it, so the next worker can pin it\"" % (rc, i, nonce),
        "  %s verdict --item %s --nonce %s FAIL \"what is wrong, so the next worker can fix it\" --defect \"CAUSE: one "
        "wrong thing\" [--defect ...] [--control \"how your instrument showed it can see\"] [--unreached \"what you "
        "also could not reach\"]" % (rc, i, nonce),
        "  %s verdict --item %s --nonce %s UNMEASURED \"%s what, and the command that showed it; then what you did "
        "check\" --unreached \"one thing out of reach, and the command that showed it\" [--unreached ...]"
        % (rc, i, nonce, relentless_wall.REACH_TAG),
        *relentless_game.checker_lines(st["contract"]),
        *["Off-box reading %d (the supervisor ran it just now; judge whether it measures its clause): $ %s -> exit %s\n%s"
          % (n, x["cmd"], x["exit"], (x["out"] or "")[-4000:]) for n, x in enumerate(readings, 1)],
        *relentless_wall.blind_lines(st),
        "See the change with: git show %s" % c["sha"], "", "--- item ---", text])


# ---------------------------------------------------------------- the tick

def short(item):
    return hashlib.sha1(item.encode()).hexdigest()[:10]


def run_desc(store, r, unit, now):
    """A run's whole identity, known and persisted before the unit exists (role_launch.role_scope's name)."""
    d = os.path.join(store.dir, "runs", "roles")
    return {"unit": unit, "marker": unit, "at": now, "charged": None, "out": os.path.join(d, unit + ".json"),
            "err": os.path.join(d, unit + ".err"), "scope": "claude-seat-%s-%s.scope" % (r["seat"], unit)}


def run_output(run):
    """-> {out_bytes, err_tail} of a run's out and err files (run_desc), for a checker_lost act: a checker that died at
    launch wrote nothing (out_bytes 0), and its err tail says why (EACCES). ops_watch reads a run of these across items
    (CHECKER_DEATHS_MONITOR_29_NOBODY_NOTICED). A path that cannot be read is out_bytes None, never 0."""
    got = {"out_bytes": None, "err_tail": None}
    if not isinstance(run, dict):
        return got
    try:
        got["out_bytes"] = os.path.getsize(run["out"]) if os.path.exists(run["out"]) else 0
    except (OSError, KeyError, TypeError):
        pass
    try:
        with open(run["err"], "rb") as f:
            f.seek(max(os.path.getsize(run["err"]) - 2048, 0))
            lines = [x for x in f.read().decode("utf-8", "replace").splitlines() if x.strip()]
        got["err_tail"] = lines[-1][:200] if lines else ""
    except (OSError, KeyError, TypeError):
        pass
    return got


def unit_name(kind, item, gen):
    return "rm-relentless-%s-%s-g%d" % (kind, short(item), gen)


def stage_load(store):
    try:
        with open(store.p("staffing_state.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def stage_places(store, fx, r):
    """What the current stage allows and what the budget leaves. -> (stage value, budget, head helpers, places)."""
    cfg = r["staffing"]
    stages = cfg["stages"]
    v = stages[min(stage_load(store).get("stage", 0), len(stages) - 1)]
    low = min((x for x in stages if x != "budget"), default=1)
    budget, head = fx.budget(), fx.head_helpers()
    if budget is None:          # unreadable: the lowest stage at any stage, and the reading says so
        v = low
    elif v == "budget":
        v = budget
    room = v if budget is None else min(v, max(budget - (head or 0), 0))
    if head is None:            # helpers nobody counted are not free places
        room = min(room, low)
    return v, budget, head, min(room, places_ceiling(fx, r))


def places_ceiling(fx, r):
    """max_workers under the WIP cap (RO2). A budget caps workers, not open focus, so the same number binds here; a
    `held` item is relentless's wait and holds no place. `extra` in worker_cap stays on top: a check always runs."""
    focus = getattr(fx, "focus_cap", lambda: None)()
    return r["max_workers"] if focus is None else min(r["max_workers"], focus)


def worker_cap(fx, r, extra=0, store=None):
    """The places a run may take now: the stage and the budget under max_workers, stepped back to 1 while available
    memory is under step_back_mem_gb. `extra` is the place a check gets on top (a check runs even at budget 0: it holds
    a place already, and finishing work is never what a budget cut stops)."""
    cap = stage_places(store, fx, r)[3] if store is not None and r.get("staffing") else places_ceiling(fx, r)
    if cap > 1 and fx.mem_gb() < r.get("step_back_mem_gb", 0):
        cap = 1
    return cap + extra


def admission(store, fx, r, now, active, extra=0):
    """-> None when one more run may start, else why not."""
    br = load_breaker(store)
    if br.get("until", 0) > now + r["breaker_cool_max_s"]:      # set under a higher cap: the rule binds what is on disk
        br["until"] = now + r["breaker_cool_max_s"]
        store._write(store.p("breaker.json"), json.dumps(br))
    if br.get("until", 0) > now:        # the cause, not only the state: the alarm quotes this line
        return "breaker open until %s: %s" % (iso(br["until"]), (br.get("why") or "no cause recorded").strip()[:200])
    if active >= worker_cap(fx, r, extra, store):
        return "max_workers"
    if fx.paused():
        return "paused"
    if fx.mem_gb() < r["min_mem_available_gb"]:
        return "memory"
    want = spent_today(store, now) + (active + 1 + unreaped(store)) * r["run_reserve"]
    if want > r["day_spend_limit"]:     # advisory (owner 2026-11-02): it calls attention, the run still starts
        attention(store, fx, "day_spend_limit", "day spend %d (spent + reserve for %d runs) over the advisory "
                  "day_spend_limit %d by %d weighted tokens; nothing stopped. Look: relentless staffing.json, "
                  "spend.jsonl" % (want, active + 1 + unreaped(store), r["day_spend_limit"], want - r["day_spend_limit"]),
                  now)
    return None


ATTENTION_EVERY_S = 6 * 3600     # one line per crossing kind per 6 h: a standing crossing does not flood the log


def spend_level(spent, limit):
    """Which doubling of `limit` `spent` has reached: 0 at the crossing, 1 at twice it, 2 at four times... None below it."""
    if limit <= 0 or spent < limit:
        return None
    n = 0
    while spent >= limit * 2 ** (n + 1):
        n += 1
    return n


def attention(store, fx, key, text, now, level=None):
    """A spend number over its advisory threshold. Owner 2026-11-02 (TOKEN_LIMITS_TAME_BARK_NO_BITE): "Please make
    token limits advisory at this time everywhere. Nothing gets killed or stopped for that, but it might call attention
    from another agent (Conductor, Operations) to investigate and THAT agent may determine it needs to be killed for
    evidence-based reasons." So this journals, writes one line to the Conductor log and the told ledger (Operations),
    each key at most once in ATTENTION_EVERY_S, and never holds, refuses or stops anything. A failure to tell stays on
    the journal.
    `level` (a [limit, doubling] pair) tells once per crossing instead of once per ATTENTION_EVERY_S: a standing
    per-item crossing re-told every 6 h kept its Operations incident (event_quiet_min 420) open for as long as the
    item stayed on the belt (SPEND_INCIDENT_FIX_BARKS_TILL_DONE). It tells again only at a higher doubling or a new limit."""
    path = store.p("attention.json")
    try:
        with open(path, encoding="utf-8") as f:
            said = json.load(f)
    except (OSError, ValueError):
        said = {}
    if level is None:
        if now - said.get(key, -1e18) < ATTENTION_EVERY_S:
            return False
        said[key] = now
    else:
        was = said.get("level:" + key)
        if isinstance(was, list) and len(was) == 2 and was[0] == level[0] and was[1] >= level[1]:
            return False
        said["level:" + key] = list(level)
    store._write(path, json.dumps(said, sort_keys=True))
    fails = []
    line = getattr(fx, "conductor_attention", None)
    why = line(text) if line else "no conductor_attention on this effects"
    if why:
        fails.append(why)
    sig = getattr(fx, "alarm_signal", None)
    if sig:
        sig({"kind": "relentless_attention_" + key, "why": text})
    store.journal({"at": iso(now), "do": "attention", "key": key, "why": text[:500], "advisory": True,
                   "told_failed": fails or None})
    return True


def load_breaker(store):
    try:
        with open(store.p("breaker.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def cause_key(why):
    """Same fault, same key: run names, paths and numbers differ between tries, the words do not. The tail, because
    launch and clone errors arrive cut to their last 200-300 characters, so their first words shift with a name's length."""
    return re.sub(r"\s+", " ", CAUSE_TOKEN.sub("#", why)).strip().lower()[-120:]


def death_note(run):
    """-> the last 300 characters of `run`'s .err when its .json holds no result object, else None (no .err text: a
    plain lost run, the checker_lost count's business)."""
    if not run:
        return None
    try:
        with open(run.get("out") or "", encoding="utf-8") as f:
            if json.load(f) is not None:
                return None
    except (OSError, ValueError):
        pass
    try:
        with open(run.get("err") or "", encoding="utf-8", errors="replace") as f:
            text = f.read().strip()
    except OSError:
        return None
    return text[-300:] or None


def launch_failed(store, r, now, why):
    """The launcher failed. A refusal is not that: the launch path is healthy and something else said no, so it charges
    nothing here, at any call site. `opens` counts by cause and outlives launch_ok: a flap between two opens is still one fault."""
    if any(w in why for w in r["breaker_refusal_words"]):
        return
    br = load_breaker(store)
    was_open = br.get("until", 0) > now
    br["fails"] = br.get("fails", 0) + 1
    if br["fails"] >= r["launch_breaker"]:
        n = br["fails"] - r["launch_breaker"]
        br["until"] = now + min(r["breaker_cool_s"] * (2 ** n), r["breaker_cool_max_s"])
        if not was_open:            # a second failure of the same tick extends this open, it is not another one
            c = br.setdefault("opens", {}).setdefault(cause_key(why), {"n": 0})
            # each opening's time, so the emergency counts openings INSIDE the window, never the incident's total
            # (0, 40 and 80 s with a 60 s window are two, not three: Codex r4 part2 #1)
            ts = [t for t in c.get("ts") or [] if now - t < r["breaker_same_cause_window_s"]] + [now]
            c.update(n=len(ts), ts=ts, last=now, why=why[:300])
    br["why"] = why[:300]
    br["at"] = now
    store._write(store.p("breaker.json"), json.dumps(br))


def launch_ok(store):
    br = load_breaker(store)
    if br.get("fails") or br.get("until"):
        store._write(store.p("breaker.json"), json.dumps({"opens": br["opens"]} if br.get("opens") else {}))


def launch_proved(store, now):
    """A worker started after the last failure has reported: the launcher works, the count starts over. launch_ok alone
    ran only when a worker died later on, so `fails` stood for days and one failure reopened the breaker at once for its
    longest cool, showing a cause fixed the day before (the 567b22f checkout, TICK_SPEED_FIX_GAME_IDLES_WAITING)."""
    br = load_breaker(store)
    if not br.get("fails") or br.get("until", 0) > now:     # an open breaker runs its cool
        return False
    for st in store.states():
        run = st.get("run") or {}
        if run.get("at", 0) > br.get("at", 0) and (st.get("last_beat") or 0) > run["at"]:
            launch_ok(store)
            return True
    return False


def breaker_emergency(store, fx, r, now, acts):
    """The same cause opened the breaker `breaker_same_cause_opens` times inside the window: one incident, told once on
    each road, a road that failed retried next tick. A cause silent for the window is forgotten and may be told again.
    Outside launch_failed because that runs under the lock and this blocks."""
    br = load_breaker(store)
    opens = {k: c for k, c in br.get("opens", {}).items() if now - c["last"] < r["breaker_same_cause_window_s"]}
    changed = len(opens) != len(br.get("opens", {}))
    item = (r.get("staffing") or {}).get("alarm_item")
    for key, c in opens.items():
        if "ts" in c:       # a record from before the opening times keeps its count
            live = [t for t in c["ts"] if now - t < r["breaker_same_cause_window_s"]]
            if live != c["ts"]:
                c.update(ts=live, n=len(live))
                changed = True
        if c["n"] < r["breaker_same_cause_opens"]:
            continue
        said = c.setdefault("said", [])
        text = "EMERGENCY: the breaker opened %d times on the same cause: %s" % (c["n"], c["why"][:200])
        row = {"class": "emergency", "cause": "relentless.breaker:" + key, "metric": "relentless.breaker_same_cause",
               "reader": r["breaker_reader"], "told_at": iso(now), "ack_due": iso(now + r["breaker_ack_min"] * 60),
               "recover_by": None, "item": item, "opens": c["n"], "why": c["why"]}
        roads = [("told", lambda: fx.told(row)), ("conductor", lambda: fx.conductor_alarm(text))]
        if item:
            roads.append(("item", lambda: fx.staffing_alarm(item, text)))
        for name, road in roads:
            if name in said:
                continue
            fail = road()
            if fail:
                acts.append({"do": "alarm_retry", "why": "%s: %s" % (name, fail)})
            else:
                said.append(name)
                changed = True
                acts.append({"do": "breaker_emergency", "road": name, "cause": key})
                store.journal({"at": iso(now), "do": "alarm", "kind": "breaker_emergency", "road": name, "why": c["why"]})
    if changed:
        br["opens"] = opens
        store._write(store.p("breaker.json"), json.dumps(br))


def pool_rows(store, fx, r):
    """Every pool clone and who holds it. -> [{clone, item, kind, state, rank}], rank 0 dead, 1 parked, 2 live.
    Dead: its item ended, a check that is not running, or nobody's and idle. Parked: nothing runs in it, a later run may
    want it (a fresh clone serves as well, with the bundle). Live: never touched."""
    own = {}
    for st in store.states():
        if st.get("clone"):
            own[os.path.abspath(st["clone"])] = ("work", st)
        if (st.get("check") or {}).get("clone"):
            own[os.path.abspath(st["check"]["clone"])] = ("check", st)
        if (st.get("help") or {}).get("clone"):
            own[os.path.abspath(st["help"]["clone"])] = ("help", st)
    for st in store.states():
        for q in st["quarantined"]:
            if q.get("clone") and not q.get("reaped"):
                own[os.path.abspath(q["clone"])] = ("quarantine", st)
    rows = []
    for c in fx.pool_clones():
        if relentless_disk.is_warm(c):      # the pool's spare stock: reused before anything is cloned, never evicted
            continue
        kind, st = own.get(os.path.abspath(c), (None, None))
        status = st["status"] if st else None
        if st is None:
            rank = 0 if fx.clone_idle_s(c) >= POOL_ORPHAN_IDLE_S else 2
        elif kind == "quarantine" or uncharged_alive(fx, run_of(st, "run" if kind == "work" else kind)):
            rank = 2
        elif kind == "help":
            rank = 2 if help_pending(st) else 0
        elif status in ENDED:
            rank = 0
        elif kind == "check":
            rank = 0 if status in ("queued", "held", "blocked", "candidate") else 2
        elif status == relentless_game.GAME:     # waiting on the game, the bridge or the owner: parked; a stage re-prepares
            rank = 2 if (st.get("game") or {}).get("phase") in relentless_game.ACTIVE else 1
        else:
            rank = 1 if status in ("queued", "held", "blocked", "candidate") else 2
        rows.append({"clone": c, "item": st["item"] if st else clone_item(c), "kind": kind, "status": status, "rank": rank})
    return rows


def uncharged_alive(fx, run):
    """An uncharged run pins its clone only while its unit is up. A worker that finishes or snags while its unit still runs
    moves its item to candidate or held, branches that never settle the run: 2026-11-06 the pool read "15 clones, cap 16,
    nothing to release" with five units up (OPS_JAM_CLASS_FIX_AGAIN_HJWN). A failed look keeps it (Effects.alive)."""
    return bool(run) and run.get("charged") is None and getattr(fx, "alive", lambda _r: True)(run)


def charge_dead_runs(store, fx, r, now, acts):
    """Charge the dead worker run of an item whose own branch does not settle it (candidate, held, blocked, the game
    lane, queued, ended): its tokens count and its clone is no longer taken for live. A live unit is left to its branch."""
    for st in store.states():
        run = st.get("run")
        if st["status"] in ("running", "stopping", "retiring") or not run or run.get("charged") is not None:
            continue
        try:
            if fx.alive(run):
                continue
            settle(store, fx, r, st["item"], "run", st.get("started_at") or now, now, acts)
            acts.append({"do": "dead_run_charged", "item": st["item"], "unit": run.get("unit")})
        except Exception as e:  # noqa: BLE001  bookkeeping never stops the belt
            acts.append({"do": "error", "item": st["item"], "why": "charge_dead_runs %s: %s" % (type(e).__name__, e)})


def evict(store, fx, row, now, acts, why, before=None):
    bundle = fx.remove_clone({"clone": row["clone"], "item": row["item"]}, before)
    gone = not fx.clone_present(row["clone"])
    if gone:
        rec = {"at": iso(now), "do": "clone_released", "clone": os.path.basename(row["clone"]), "why": why, "bundle": bundle}
        if bundle is None:      # a removal with no bundle says why (check-WALK_SAVE-c1, 2026-11-02, said nothing)
            rec["no_bundle"] = "nothing unpushed: no changed, untracked or ignored file, commit or stash"
        store.journal(rec)
        acts.append({"do": "clone_released", "clone": os.path.basename(row["clone"]), "why": why})
    return gone, bundle


def reclaim_dead(store, fx, r, now, acts):
    """A dead run gives its clone back on the next tick, whichever road it ended by."""
    for row in pool_rows(store, fx, r):
        if row["rank"] == 0 and not fx.clone_busy(row["clone"]):
            evict(store, fx, row, now, acts, "dead: %s %s" % (row["kind"] or "nobody's", row["status"] or ""))


def bundle_pointer(store, row, carry):
    """Records the bundle on the item, so its next clone restores it."""
    def point(bundle):
        if carry:
            with store.lock():
                cur = store.load(row["item"])
                cur["bundle"] = bundle
                store.save(cur)
    return point


def release_parked(store, fx, r, now, acts):
    """A parked item's idle clone goes back before scratch_clone's idle hour calls it stranded: FLYER_STABLE_BODY_GATE_1 and
    SEAT_MEMORY_STANDARD_FALLBACK_1 sat held on the owner with real WIP until disk.pool_breach fired, because only pool
    pressure ever moved them. WIP and state-only commits travel in the bundle. So does everything else a put-down item holds, merges, side branches and stashes
    included (POOL_STRANDS_SALVAGE_BLOCKED_HOLD_THE_BAG). What cannot go (an unreadable clone, a bundle that failed) stays, and past the idle hour
    scratch_clone alarms on it: a live item's clone is excused only while the item is not put down. A queued item's commits stay: its next worker lands them."""
    for row in pool_rows(store, fx, r):
        # put down (held, blocked, waiting on the game): its clone goes back at once, it waits on something else
        wait_s = 0 if row["kind"] == "work" and row["status"] in PUT_DOWN else r["pool_parked_release_s"]
        if row["rank"] != 1 or fx.clone_busy(row["clone"]) or fx.clone_idle_s(row["clone"]) < wait_s:
            continue
        wip = fx.clone_wip(row["clone"])
        put_down = row["kind"] == "work" and row["status"] in PUT_DOWN
        if not wip["kept"] or (put_down and wip.get("carry_real")):
            evict(store, fx, row, now, acts, "parked: %s %s" % (row["kind"], row["status"]),
                  bundle_pointer(store, row, (wip["real"] or wip.get("carry") or wip.get("carry_real")) and row["kind"] == "work"))


def make_room(store, fx, r, now, acts, reserve=0):
    """Room for one more clone, or the hold that names who has the pool. Parked clones go first with nothing of theirs
    at risk, then those whose WIP a bundle carries, a put-down item's commits and stashes included; a queued item's stay, and a live clone is never touched.
    `reserve`: places a builder may not take, so a finished item can always get its check."""
    n, size, cmax, bmax = fx.pool_load()
    reserve = min(reserve, cmax - 1)   # a pool of one still has to take a builder
    warm = getattr(fx, "warm_count", lambda: 0)()     # a warm clone is room: the next clone reuses it, no bytes added
    if n - warm < cmax - reserve and (size < bmax or warm):
        return None
    rows, order = pool_rows(store, fx, r), {"candidate": 0, "held": 1, "queued": 2}
    parked = []
    for row in rows:
        if row["rank"] == 2 or fx.clone_busy(row["clone"]):
            row["hold"] = "live"
            continue
        wip = fx.clone_wip(row["clone"])
        if wip["kept"] and row["rank"] and not (row["status"] in PUT_DOWN and wip.get("carry_real")):
            row["hold"] = "commits"
            continue
        parked.append((row["rank"], bool(wip["real"] or wip.get("carry") or wip.get("carry_real")), order.get(row["status"], 0), row, wip))
    for rank, real, _o, row, wip in sorted(parked, key=lambda p: p[:3]):
        gone, _b = evict(store, fx, row, now, acts, "for room: %s %s" % (row["kind"] or "nobody's", row["status"] or ""),
                         bundle_pointer(store, row, real and row["kind"] == "work" and rank))
        if not gone:
            row["hold"] = "bundle failed"
            continue
        n, size, cmax, bmax = fx.pool_load()
        warm = getattr(fx, "warm_count", lambda: 0)()     # an eviction may have parked it warm: room all the same
        if n - warm < cmax - reserve and (size < bmax or warm):
            return None
    held = ", ".join("%s (%s)" % (clone_item(x["clone"]), x.get("hold") or x["status"]) for x in rows if fx.clone_present(x["clone"]))
    if size >= bmax:
        return "pool at %.1f GB, cap %.0f GB, nothing to release: %s" % (size / 1e9, bmax / 1e9, held)
    return "pool full: %d clones, cap %d%s, nothing to release: %s" % (
        n, cmax, " (%d kept for checks)" % reserve if reserve else "", held)


def parked(store, fx, r, st, now, states=None):
    """A queued item that cannot start now (its mod is held by another item, its start was refused and is cooling, its
    wait has not run out, the consult its next brief needs is out, or the Designer's gate refuses it: a mod's first touch
    with no pass on record, or no well-defined tree) keeps its order but holds no max_queued place: the line is topped up
    with items that can run. 2026-11-04 22:25Z: 19 refused system items filled max_queued 8, so nothing enrolled and
    nothing leased (places_live 0). `states`, when the caller has them, saves a store read per queued item."""
    if now < st.get("start_again_at", 0) or st.get("not_before", 0) > now or help_pending(st):
        return True
    if getattr(fx, "concept_refusal", lambda _item: None)(st["item"]):     # lease() walks past it the same way
        return True
    if r.get("one_builder_per_mod") and hasattr(fx, "item_mods"):
        held = mods_held(store, fx, st["item"], states)
        return any(m in held for m in fx.item_mods(st))
    return False


def enrol(store, fx, r, now):
    """Top up to ceil(share x pool). Store-only: an enrolled item stays open to the seats until a lease is taken."""
    states = store.states()
    live = [s for s in states if s["status"] in OPEN]
    share = float(r["share"])
    if share <= 0:
        return []
    order, _ = fx.pool_order(r)
    # `done` is ours only while the ledger agrees: an item in the pool again was reopened there (a deadman `live --result
    # broken`, a fixed-id OPS_ alarm, a failed verify of the closed work) and takes a new life below, or it never returns
    ours = {s["item"] for s in states if s["status"] != "done"}
    pool = len(order) + sum(1 for s in live if s["item"] not in order)
    target = math.ceil(share * pool)
    in_turn = [s for s in live if in_line(s) and not parked(store, fx, r, s, now, live)]
    queued = len(in_turn)
    want = target - len(live)
    if r.get("staffing"):       # the filler: a free place is reason enough, whatever the share says of the backlog
        want = max(want, worker_cap(fx, r, 0, store) - sum(1 for s in live if s["status"] in RUNS_A_PLACE) - queued)
    room = min(want, r["enrol_per_tick"], r["max_queued"] - queued)
    took = []
    one_per_mod = bool(r.get("one_builder_per_mod")) and hasattr(fx, "item_mods")
    taken = set()       # mods held by a run, or by an item in the line able to start, or enrolled just now
    if one_per_mod:     # an item parked on a wait shuts nobody out: lease() would start another of its mod meanwhile
        for x in [s for s in live if s["status"] in HOLDS_A_PLACE] + in_turn:
            taken |= set(fx.item_mods(x))
    plan = getattr(fx, "plan", None) or {}      # a listed item never waits for room: the list holds under 30 (DI3)
    first = getattr(fx, "first", None) or {}    # Operations' system items: order puts them first (pool_order)
    # a system item waits for neither the share nor content in the line, only for the per-tick and line caps
    sys_room = min(r["enrol_per_tick"], r["max_queued"] - sum(1 for s in in_turn if s["item"] in first))
    pause = content_pause(fx, states, order, ours, refused=refusal_memo(fx), now=now, store=store)   # lease's own exemptions
    for i in order:
        if i in first and i not in plan and room <= 0:
            if sys_room <= 0 or i in ours:
                continue
        elif room <= 0 and i not in plan:
            break
        if i in ours:
            continue
        if pause_stops(pause, fx, {"item": i}, plan, now):     # global: nothing further enrols; scoped: the next may
            if pause["mode"] == "global" and not pause.get("owner"):    # his pause: pipeline items further down enrol
                break
            continue
        if owner_hold(r, i, first):
            continue
        if one_per_mod:     # a candidate whose mod is already taken would only park: walk on to work that can start
            mods = set(fx.item_mods({"item": i, "last_sha": None}))
            if mods & taken:
                continue
            taken |= mods
        if not enrol_put(store, fx, i, "share %.2f of %d" % (share, pool), now):
            continue
        took.append(i)
        room -= 1
        sys_room -= i in first
    slot = relentless_repair_slot.pick(fx, r, live, ours | set(took), now, order)     # one place past the caps (WP-06)
    if slot and enrol_put(store, fx, slot[0], "reserved repair slot: %d items wait on it" % slot[1], now, slot="repair"):
        took.append(slot[0])
    return took


def enrol_put(store, fx, i, why, now, slot=None):
    """enrol's write for one item: a new state, or a new life for one done in the store. -> True when it enrolled."""
    with store.lock():
        cur = store.load(i)
        if cur is None:
            st = new_state(i, now, why)
            st["pilot_wanted"] = i in getattr(fx, "bounce", ())
            store.save(st)
            store.journal(dict({"at": iso(now), "do": "enrol", "item": i}, **({"slot": slot} if slot else {})))
        elif cur["status"] == "done":
            try:
                reenrol(store, i, "reopened on the ledger after done", now, locked=True)
            except ValueError:      # an unsettled run of the old life: the next tick asks again
                return False
        else:
            return False
    return True


def owner_hold(r, item, first, st=None):
    """The owner's token pause (rules `only_system_and_live`): no new work on an item unless it is system (`first`),
    expedited, or iterating on a live failure. Running work, checks of finished builds and the game phase go on. Pure."""
    if not r.get("only_system_and_live") or item in (first or {}):
        return False
    return not (st and (st.get("expedite") or st.get("live_iter")))


def write_queue_next(store, fx, r, now, shown=8):
    """The next names in the line, for RUNNING_NOW: the order needs this tick's plan and Operations' verdict, so the page
    reads it here instead of recomputing it. `free` may start at the next room; `waiting` are next but stopped by the token
    pause, a degraded verdict or their own not_before (the same tests lease applies). A reading: nothing acts on it."""
    states = store.states()
    plan, first = getattr(fx, "plan", None) or {}, getattr(fx, "first", None) or {}
    pause = content_pause(fx, states, refused=refusal_memo(fx), now=now, store=store)
    free, waiting = [], []
    for st in queue_order(states, plan, first):
        i = st["item"]
        stopped = owner_hold(r, i, first, st) or st.get("not_before", 0) > now or bool(pause_stops(pause, fx, st, plan, now))
        (waiting if stopped else free).append(i)
    store._write(store.p("queue_next.json"), json.dumps({"t": now, "free": free[:shown], "waiting": waiting[:shown]}, indent=1))


FRESH_RULING_S = 48 * 3600     # content he ruled on this recently passes a scoped pause (section 3 of the spec)
PAUSE_ALARM_S = 6 * 3600        # runnable content held this long by the pause is told to the Conductor
GAME_LANE_NEEDS = ("deploy", "game-up", "bridge", "harvest")
PAUSED_WHY = "health degraded: content paused while system items wait"     # jam_classes content_paused_idle matches it


def ts_epoch(ts):
    """A ledger ts (2026-11-05T05:37:35Z) as epoch seconds, or None."""
    try:
        return calendar.timegm(time.strptime(str(ts)[:19], "%Y-%m-%dT%H:%M:%S"))     # UTC; mktime applied local DST
    except (TypeError, ValueError):
        return None


OWNER_PAUSE_WHY = "owner pause: pipeline items only"     # relentless_owner_pause.json (owner 2026-11-05)
OWNER_PAUSE = os.path.join(HERE, "relentless_owner_pause.json")


def owner_pause_rule(path=None):
    """The owner's pipeline-only switch as data (relentless_owner_pause.json), read once per tick by the real Effects
    (fx.owner_pause_rule; a test's Fx has none, so it reads off). No file: off. A file that cannot be read: on, said in
    its why, since his pause is the side that cannot start work against his word."""
    try:
        with open(path or OWNER_PAUSE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as e:
        return {"pipeline_only": True, "pipeline_prefixes": ["LIGHTSPEED_"], "unreadable": "%s: %s" % (type(e).__name__, e)}


def owner_pause(fx, states=()):
    """The owner's pipeline-only pause (fx.owner_pause_rule, `pipeline_only` true), or None: a global pause whatever
    the verdict, with owner True; `prefixes` are the ids that count as pipeline beside Operations' system items
    (fx.first, ops_health.is_system)."""
    rule = getattr(fx, "owner_pause_rule", None) or {}
    if not rule.get("pipeline_only"):
        return None
    pre = list(rule.get("pipeline_prefixes") or ())
    first = getattr(fx, "first", None) or {}
    held = [s["item"] for s in states if s["status"] == "queued"
            and (s["item"] in first or any(s["item"].startswith(p) for p in pre))]
    why = OWNER_PAUSE_WHY + (" (switch unreadable: %s)" % rule["unreadable"] if rule.get("unreadable") else "")
    return {"mode": "global", "owner": True, "why": why, "holding": held, "lanes": [], "prefixes": pre}


def owner_pipeline(pause, fx, item):
    """True for an item the owner's pause lets start: one of Operations' system items or a pipeline prefix."""
    return item in (getattr(fx, "first", None) or {}) or any(item.startswith(p) for p in pause.get("prefixes") or ())


def content_pause(fx, states, order=None, ours=None, refused=None, now=None, store=None):
    """-> None, or {mode: global|scoped, why, holding: [system items waiting for a place], lanes: [lane]}.
    The owner's pipeline-only switch (owner_pause, fx.owner_pause_rule) comes before everything below: while it is
    on the answer is that global pause (owner True), whatever the verdict says and whether or not a system item waits.
    A pause exists while Operations' verdict reads degraded (or unmeasured) and a system item still waits for a place: in
    the line, or in the pool not yet enrolled. When every system item is already being worked, content may start (owner
    card 2026-11-03). `refused(item)` -> a reason marks a system item the concept gate keeps from any worker: it waits on
    a Designer pass, not a place, so it holds no content back (21:06Z 2026-11-04: twenty refused items paused content with
    nothing live). A queued system item whose not_before is still ahead waits on the clock, not a place: lease skips it,
    so it holds no content back either (RELENTLESS_PAUSE_FIX_CLOCK_WAIT_STALLS_ALL, 2026-11-05: one item's 342 min
    wait-hours snag paused every content item with 2 places live of 8). It keeps its first pick: the tick its wait ends,
    it is placed before content. A start refused and cooling (start_again_at) or a consult out (help_pending) is the same
    wait on something not a place (parked; Codex review, RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN #6).
    Scoped (DEGRADED_PAUSE_FIX_STOPS_ONLY_WHAT_BROKE, owner card 2026-11-05 "Pause only what it touches"): the mode is
    global only when a shared integrity resource is impaired: the verdict's pause_scope says so (assessment unmeasured,
    storage headroom spent, no scopes named), the account circuit (breaker.json) is open, or the integrity gate's record
    reads blocked (the store is suspect). Otherwise it is scoped: only content in the spent SLIs' lanes waits, and lease
    reserves a place for each holding system item. An Fx with no pause_scope reads degraded as global (the old pause)."""
    op = owner_pause(fx, states)
    if op:
        return op
    first = getattr(fx, "first", None) or {}
    sc = getattr(fx, "pause_scope", "unset")
    if sc == "unset":
        sc = {"global": "degraded", "lanes": []} if getattr(fx, "degraded", False) else None
    if not first or not sc:
        return None
    now = time.time() if now is None else now
    waits = [s["item"] for s in states if s["status"] == "queued" and s["item"] in first
             and not (s.get("not_before") or 0) > now
             and not (s.get("start_again_at") or 0) > now and not help_pending(s)]  # cooling or on a consult (Codex #6)
    waits += [i for i in (order or ()) if i in first and i not in (ours or ())]
    holding = [i for i in dict.fromkeys(waits) if not (refused and refused(i))]
    if not holding:
        return None
    impaired = [sc["global"]] if sc.get("global") else []
    if store is not None:
        br = load_breaker(store)
        if br.get("until", 0) > now:
            impaired.append("account circuit open until %s" % iso(br["until"]))
        if (relentless_integrity.read_record(store) or {}).get("blocked"):
            impaired.append("store suspect: the integrity gate is blocking")
    if impaired:
        return {"mode": "global", "why": "; ".join(impaired), "holding": holding, "lanes": []}
    return {"mode": "scoped", "why": "lanes " + (", ".join(sc.get("lanes") or ()) or "none"), "holding": holding,
            "lanes": list(sc.get("lanes") or ())}


def content_paused(fx, states, order=None, ours=None, refused=None, now=None, store=None):
    """True while any content pause, global or scoped, stands (content_pause)."""
    return content_pause(fx, states, order, ours, refused, now, store) is not None


def item_lane(fx, st):
    """`game` for an item whose work needs the live game (a game clause on its contract, or ledger needs in
    GAME_LANE_NEEDS), else `offline`."""
    if (st.get("contract") or {}).get("game"):
        return "game"
    ask = getattr(fx, "item_state", None)
    led = ask(st["item"]) if ask else None
    return "game" if (led or {}).get("needs") in GAME_LANE_NEEDS else "offline"


def fresh_ruling(fx, item, now):
    """True when the owner ruled on this item (his words or card on the ledger) within FRESH_RULING_S."""
    ask = getattr(fx, "owner_ruled_at", None)
    t = ask(item) if ask else None
    return t is not None and now - t < FRESH_RULING_S


def pause_stops(pause, fx, st, plan=None, now=None):
    """-> why this item waits on the pause, or None. Expedited, system and priority-list items never wait; a global pause
    stops all other content; a scoped one stops content in a paused lane unless he ruled on it within 48 h (the ruling
    raises priority; every other check still applies). Reserved places are lease's (pause_reserve)."""
    if not pause:
        return None
    i = st["item"]
    if pause.get("owner"):      # his pause: only pipeline items start; an expedite or the list does not pass content
        return None if owner_pipeline(pause, fx, i) else pause["why"]
    if st.get("expedite") or i in (getattr(fx, "first", None) or {}) or i in (plan or {}):
        return None
    if pause["mode"] == "global":
        return "global: " + pause["why"]
    if fresh_ruling(fx, i, time.time() if now is None else now):
        return None
    lane = item_lane(fx, st)
    return "lane %s paused" % lane if lane in pause["lanes"] else None


def pause_reserve(store, pause):
    """The system items of a scoped pause still queued now: one free place is kept for each."""
    if not pause or pause["mode"] != "scoped":
        return []
    return [i for i in pause["holding"] if (store.load(i) or {}).get("status") == "queued"]


def pause_alarm(store, fx, seen, now, acts):
    """Runnable content held by the pause past PAUSE_ALARM_S: one line to the Conductor naming the system items that hold
    it (attention: once per 6 h). The clock starts the first tick content is held and clears the first tick none is."""
    if not seen.get("known"):
        return
    path = store.p("content_pause.json")
    if not seen["stopped"]:
        if os.path.exists(path):
            os.remove(path)
        return
    try:
        with open(path, encoding="utf-8") as f:
            rec = json.load(f)
    except (OSError, ValueError):
        rec = {"since": now}
    pause = seen["pause"] or {}
    rec.update({"holding": pause.get("holding", []), "stopped": seen["stopped"][:20], "mode": pause.get("mode"),
                "why": pause.get("why")})
    store._write(path, json.dumps(rec, sort_keys=True))
    held = now - rec["since"]
    if held > PAUSE_ALARM_S and not pause.get("owner"):     # his own pause holds content on purpose: no alarm
        text = ("runnable content paused %.1f h (> %d h, %s pause: %s): %d content items held (%s) by system items %s. "
                "Look: %s" % (held / 3600, PAUSE_ALARM_S // 3600, rec["mode"], rec["why"], len(seen["stopped"]),
                              ", ".join(seen["stopped"][:5]), ", ".join(rec["holding"][:8]) or "none", path))
        if attention(store, fx, "content_paused_6h", text, now):
            acts.append({"do": "content_paused_alarm", "hours": round(held / 3600, 1), "holding": rec["holding"][:8]})


def refusal_memo(fx):
    """fx.concept_refusal, asked once per item per call site: the content pause and the lease loop share the answer."""
    ask, seen = getattr(fx, "concept_refusal", None), {}
    if ask is None:
        return lambda _item: None

    def refused(item):
        if item not in seen:
            seen[item] = ask(item)
        return seen[item]
    return refused


def ledger_has(item):
    """The caller's own ledger, published or not: a typed id that names nothing never enters the line. Unreadable: yes."""
    try:
        # a spawn event names its child in `name`, not `id`: an item with only its birth is still filed
        return any(e.get("id") == item or (e.get("event") == "spawn" and e.get("name") == item)
                   for e in pkg("model").read())
    except Exception:  # noqa: BLE001
        return True


def ledger_state(item):
    """The caller's own ledger: an item's state, None when it was never filed. Unreadable: "?" (no refusal on a blind read)."""
    try:
        if _LEDGER_WORLD[0] is None:        # one replay per process: `causes` asks once per cause
            model = pkg("model")
            _LEDGER_WORLD[0] = model.replay(model.read())
        it = _LEDGER_WORLD[0].items.get(item)
    except Exception:  # noqa: BLE001
        return "?"
    return it.state if it else None


_LEDGER_WORLD = [None]


def concept_refused(repo, item, kind):
    """The Designer's gate, shut when it cannot read: None for anything that is not a mod and cites no tree."""
    tree = pkg("concept_tree")
    return tree.relentless_refusal(repo, item, kind, tree.item_file_text(repo, item))


def enrol_one(store, item, why, now):
    """A person's or the Conductor's pick. It queues in enrol order like any other and takes no lease by itself."""
    with store.lock():
        st = store.load(item)
        if st is None:
            st = new_state(item, now, why)
            store.save(st)
            store.journal({"at": iso(now), "do": "enrol", "item": item, "why": why})
        return st


def reenrol(store, item, why, now, locked=False):
    """Back in line after `retired`, which is otherwise for good: a named verb, journalled, for a retirement that was
    wrong; or after `done`, when the ledger reopened the item (enrol() calls it on sight; the cli refuses a done item the
    ledger still holds closed, which retire() would only end again). A fresh start with the old spend: `gen` moves on, so a run of the old life stays fenced, and `check_count`
    stays, so a new checker never lands in the path a quarantined one may still be running in; `help_count` likewise."""
    if not (why or "").strip():
        raise ValueError("reenrol: --why is required")
    with (contextlib.nullcontext() if locked else store.lock()):
        old = store.load(item)
        if not old or old["status"] not in ENDED:
            raise ValueError("%s is %s, only a retired or done item can be re-enrolled" % (
                item, old["status"] if old else "not enrolled"))
        live = [k for k in ("run", "check", "help") if (run_of(old, k) or {}).get("charged", 0) is None]
        if live:    # the new state would forget what they cost and could never stop them
            raise ValueError("%s still has an unsettled %s: re-enrol once it is over" % (item, ", ".join(live)))
        st = new_state(item, now, why)
        st.update(gen=old["gen"] + 1, spent=old.get("spent", 0), quarantined=old.get("quarantined", []),
                  attempts=old.get("attempts", 0), check_count=old.get("check_count", 0),
                  help_count=old.get("help_count", 0))
        store.save(st)
        store.journal({"at": iso(now), "do": "reenrol", "item": item, "why": why})
        return st


def expedite_cli(a, store, now, r, env=None):
    """`relentless.py expedite`. A request puts the item in line at once, past every cap (the owner set none); the tick
    folds it onto the state. Anything the line could never start is refused here, not left to wait 4 h."""
    env = os.environ if env is None else env
    if a.verb == "list":
        print("\n".join(relentless_expedite.listing(store, now)))
        return 0
    if not a.item:
        print("relentless: REFUSED: expedite %s needs an item" % a.verb, file=sys.stderr)
        return 2
    try:
        if a.verb == "set":
            st = store.load(a.item)
            why = expedite_refusal(a.item, st, r)
            if why:
                raise ValueError(why)
        e = relentless_expedite.request(store, a.verb, a.item, now, env, a.level, a.by, a.why)
        if a.verb == "set":
            if st is None:
                st = enrol_one(store, a.item, "expedite %s by %s: %s" % (a.level, a.by, a.why), now)
            elif st["status"] in ENDED:
                st = reenrol(store, a.item, "expedite %s by %s: %s" % (a.level, a.by, a.why), now)
    except ValueError as ex:
        print("relentless: REFUSED: %s" % ex, file=sys.stderr)
        return 2
    print("%s %s" % (a.item, "cleared" if e is None else "%s until %s (status %s)" % (
        e["level"], iso(e["until"]), (store.load(a.item) or {}).get("status"))))
    return 0


def done_still_closed(st, led_state):
    """-> why a store-done item may not come back, or None: only a ledger that reopened it (proposed/ready) brings it
    back; anything else would be ended again by retire(). Pure."""
    if st is None or st["status"] != "done" or led_state in ("proposed", "ready"):
        return None
    return "%s is done in the store and the ledger says %s: only a reopened item comes back" % (st["item"], led_state)


def expedite_refusal(item, st, r):
    """Why this item can never take the lane, or None."""
    if not ledger_has(item):
        return "%s has never been filed" % item
    if pool_excluded(item, r):
        return "%s is on pool_ids_exclude or a parked list: the line retires it on sight; take it off first" % item
    if done_still_closed(st, ledger_state(item)):
        return "%s is done in the store and not reopened on the ledger" % item
    filed = [e.get("kind") for e in pkg("model").read() if e.get("id") == item and e.get("event") == "file"]
    return concept_refused(pkg("concept_tree").REPO, item, filed[-1] if filed else None)


def run_of(st, key):
    return st.get("run") if key == "run" else (st.get(key) or {}).get("run")


def measure(fx, run):
    """-> (tokens, basis) of a finished run; a fixture without `measure` reads only the result object."""
    if hasattr(fx, "measure"):
        return fx.measure(run)
    tok = fx.tokens(run)
    return tok, ("result" if tok else "estimated")


def settle(store, fx, r, item, key, since, now, acts):
    """Bring one run to its end: stop it, force it, at last quarantine it (the reaper goes on trying and charges it).
    True when the run is over as far as the item is concerned. Blocking calls are outside the lock."""
    st = store.load(item)
    run = run_of(st, key)
    if not run or run.get("charged") is not None:
        return True
    age = now - (since or now)
    if fx.alive(run):
        if age < r["stop_quarantine_s"]:
            fx.stop(run, force=age >= r["stop_force_s"])
            return False
        with store.lock():
            cur = store.load(item)
            live = run_of(cur, key)
            cur["quarantined"].append({"run": dict(live), "at": now,
                                       "clone": cur["clone"] if key == "run" else (cur[key] or {}).get("clone"),
                                       "reaped": False})
            live["charged"] = 0
            if key == "run":
                cur["clone"] = None           # the next worker gets a new clone, from what was pushed
            store.journal({"at": iso(now), "do": "alarm", "kind": "quarantine", "item": item,
                           "why": "unit %s would not die" % run["unit"]})
            store.save(cur)
        fx.ledger_note(item, "relentless: unit %s would not die, quarantined; carrying on" % run["unit"])
        acts.append({"do": "quarantine", "item": item, "unit": run["unit"]})
        return True
    tok, basis = measure(fx, run)
    with store.lock():
        cur = store.load(item)
        live = run_of(cur, key)
        if live and live.get("charged") is None:
            live["charged"] = charge(store, cur, tok, now, r, live["unit"], basis)
            live["measured"] = tok
            live["basis"] = basis
            store.save(cur)
    return True


def reap_quarantined(store, fx, r, now, acts):
    for st in store.states():
        for i, q in enumerate(st["quarantined"]):
            if q.get("reaped"):
                continue
            if fx.alive(q["run"]):
                fx.stop(q["run"], force=True)
                continue
            tok, basis = measure(fx, q["run"])
            with store.lock():
                cur = store.load(st["item"])
                if not cur["quarantined"][i].get("reaped"):
                    cur["quarantined"][i]["reaped"] = True
                    charge(store, cur, tok, now, r, q["run"]["unit"], basis)
                    store.save(cur)
            fx.remove_clone({"clone": q.get("clone")})
            acts.append({"do": "reaped", "item": st["item"], "unit": q["run"]["unit"]})


def unreaped(store):
    return sum(1 for s in store.states() for q in s["quarantined"] if not q.get("reaped"))


def overdue(st, activity, now, r):
    """-> (class, why) when a live worker has run out of time or gone silent. Pure."""
    if now - st["started_at"] >= r["run_max_s"]:
        return "worker_full", "hit run_max_s"
    seen = max(st["started_at"] + r["launch_grace_s"], st["last_beat"] or 0, activity)
    if now - seen >= r["stale_s"]:
        return "worker_stale", "silent for %d s" % (now - seen)
    return None


def step(store, fx, r, item, now, acts):
    """One item, one transition. Crash anywhere and the next tick resumes from the persisted status."""
    st = store.load(item)
    s = st["status"]
    if s == "queued" and st.get("needs_back"):      # his hold lifted: the ledger still says owner
        back = fx.needs_after_hold(item)
        if not back or not fx.ledger_needs(item, back, "relentless: the owner lifted the hold"):
            with store.lock():
                st = store.load(item)
                st["needs_back"] = False
                store.save(st)
    if s in ENDED or s in ("queued", "blocked"):     # blocked: relentless_block.sweep moves it
        return
    if s == relentless_game.GAME:
        return relentless_game.step(store, fx, r, item, now, acts, sys.modules[__name__])

    if s == "retiring":
        since = st["stopping_since"]
        if settle(store, fx, r, item, "run", since, now, acts) and settle(store, fx, r, item, "check", since, now, acts):
            if st.get("release_bridge"):        # a dropped item's staging: its bridge goes back after its worker died
                fx.bridge_release()
            with store.lock():
                st = store.load(item)
                st["status"] = "retired"
                st.pop("release_bridge", None)
                store.save(st)
            fx.remove_clone(st)
            acts.append({"do": "retired", "item": item})
        return

    if s == "held":
        h = st["hold"]
        if relentless_answer.reconcile(store, fx, item, st, now, acts, iso):    # his answer cites its question_id
            return
        if hold_is_his(h):
            if not h.get("delivered") and not fx.ledger_needs_owner(item, h["why"]):
                _hold_routed(store, item, None)
                acts.append({"do": "held_delivered", "item": item})
        elif h.get("routed") != SEAT_QUEUE and not fx.ledger_hold_to_seat(item, h):
            _hold_routed(store, item, SEAT_QUEUE)
            acts.append({"do": "held_delivered", "item": item, "to": SEAT_QUEUE})
        return

    if s == "stopping":
        if not settle(store, fx, r, item, "run", st["stopping_since"], now, acts):
            return
        with store.lock():
            st = store.load(item)
            if st["status"] != "stopping":
                return
            st["run"] = None
            st["status"] = "held" if st["hold"] else "blocked" if st.get("block_pending") or st.get("wait") else "queued"
            store.save(st)
        acts.append({"do": "returned", "item": item, "to": st["status"]})
        return

    if s == "running" and st.get("reserving"):
        # a crash between the reservation and the launch: the item goes back to the line, its ledger as it stands
        with store.lock():
            st = store.load(item)
            st.pop("reserving", None)
            st["status"] = "queued"
            store.save(st)
        acts.append({"do": "reservation_returned", "item": item})
        return

    if s == "running":
        rec = store.read_receipt(item, st["gen"])
        if rec:         # a crash between the receipt and the status: the receipt wins
            with store.lock():
                st = store.load(item)
                if st["status"] == "running":
                    _take_receipt(store, st, rec, now)
            return
        run = st.get("run")
        if fx.alive(run):
            act = fx.activity(st)
            if overdue(st, act, now, r):
                with store.lock():
                    st = store.load(item)
                    late = overdue(st, act, now, r) if st["status"] == "running" else None
                    rec = store.read_receipt(item, st["gen"]) if late else None
                    if rec:
                        _take_receipt(store, st, rec, now)
                        return
                    if late:
                        fail(store, st, late[0], late[1], r, now)
                if late:
                    fx.stop(run, force=False)
                    acts.append({"do": late[0], "item": item})
            return
        if not settle(store, fx, r, item, "run", st["started_at"], now, acts):
            return
        lost = fx.account_loss(run, st.get("clone"), st["started_at"])     # file reads: outside the lock
        with store.lock():
            st = store.load(item)
            if st["status"] != "running":
                return
            rec = store.read_receipt(item, st["gen"])   # finish may have landed while the unit went down
            if rec:
                _take_receipt(store, st, rec, now)
                return
            tok = (st.get("run") or {}).get("measured")
            if not tok and not st["last_beat"] and now - st["started_at"] < r["launch_grace_s"]:
                # dead at once, nothing spent: auth or quota, not the item's fault. Its place is kept
                st["gen"] += 1
                st["status"] = "queued"
                st["returned_at"] = st["returned_at"] or now
                st["run"] = None
                store.attempt(item, {"at": iso(now), "gen": st["gen"] - 1, "end": "launch_fail"})
                store.save(st)
                launch_failed(store, r, now, "%s died at once with no usage" % (run or {}).get("unit"))
                acts.append({"do": "launch_fail", "item": item})
                return
            if lost:
                account_lost(store, st, lost, r, now)
                acts.append({"do": "account_lost", "item": item, "kind": lost["kind"]})
                return
            # a change-over logs its event only once the fleet is back up, minutes after the kill: judge after it could have
            seen = st["run"].setdefault("lost_seen", now)
            if now - seen < r.get("account_settle_s", 0):
                store.save(st)
                return
            launch_ok(store)
            fail(store, st, "worker_lost", "unit %s ended with no receipt" % (run or {}).get("unit"), r, now)
        acts.append({"do": "worker_lost", "item": item})
        return

    if s == "candidate":
        c = st["candidate"]
        green = relentless_game.green_stands(st, store.attempts(item))
        if green:       # PASS3_FLOOD_FIX_REJUDGE_GREEN_SHA: the Judge passed this sha already; the game step is owed, not a check
            with store.lock():
                st = store.load(item)
                if st["status"] == "candidate" and relentless_game.green_stands(st, store.attempts(item)):
                    relentless_game.reenter(store, st, now, green)
                    store.attempt(item, {"at": iso(now), "gen": st["gen"], "routed": "green_stands", "sha": c["sha"],
                                         "detail": green, "to": relentless_game.GAME})
                    acts.append({"do": "game_entered", "item": item, "sha": c["sha"], "why": green})
            return
        if now < (st.get("recheck_at") or 0):   # an unmeasured check waits before the same sha is checked again
            acts.append({"do": "check_waits", "item": item, "why": "re-check of an unmeasured sha"})
            return
        reach = reach_hold(store, r, item, now)
        if reach:
            acts.append({"do": "reach_held", "item": item, "why": reach})
            return
        moved = fx.relanded(st)
        if moved:
            with store.lock():
                st = store.load(item)
                if st["status"] != "candidate" or st["candidate"]["sha"] != c["sha"]:
                    return
                st["candidate"].update({"sha": moved[0], "landed_from": c["sha"]})
                st["last_sha"] = moved[0]
                store.attempt(item, {"at": iso(now), "gen": st["candidate"].get("gen"), "routed": "relanded",
                                     "sha": moved[0], "from": c["sha"], "detail": moved[1]})
                store.save(st)
            acts.append({"do": "sha_relanded", "item": item, "sha": moved[0], "from": c["sha"], "why": moved[1]})
            c = st["candidate"]
        why = None
        pub = fx.published(c["sha"])
        if pub is None:
            acts.append({"do": "publish_unknown", "item": item})
            return
        if not pub:
            why = "%s is not on origin/main" % c["sha"]
        else:
            import live_line
            paths = fx.changed(st.get("base"), c["sha"], item)
            if not paths:
                why = "%s changes nothing" % c["sha"]
            elif (live_line.needs_line(paths) or (item.startswith(ALARM_PREFIXES) and not live_line.prose_only(paths))) and not (st["contract"] or {}).get("live"):
                why = "%s needs a live line in the contract: %s" % (c["sha"], (live_line.needs_line(paths) or ["alarm item"])[0])
            elif (fx.item_state(item) or {}).get("guard_owed"):
                why = "%s: this fix died before, so the close will refuse it: `rimflow guard %s --test <selftest*.py>` first" % (c["sha"], item)
        klass, proof_why = proof_gate(fx, r, st, c) if not why else (None, None)
        if klass:
            with store.lock():
                st = store.load(item)
                if st["status"] == "candidate":
                    fail(store, st, klass, proof_why, r, now)
            acts.append({"do": klass, "item": item})
            return
        if why:
            with store.lock():
                st = store.load(item)
                if st["status"] == "candidate":
                    fail(store, st, "bad_candidate", why, r, now)
            acts.append({"do": "bad_candidate", "item": item})
            return
        # the finishing worker leaves first: nothing of its survives into the check
        if not settle(store, fx, r, item, "run", c["at"], now, acts):
            return
        # checks get a place, and a waiting candidate runs nothing: counted, two would wait on each other for good
        active = sum(1 for x in store.states() if x["status"] in RUNS_A_PLACE) + helps_running(store)
        hold = admission(store, fx, r, now, active, extra=1)
        if not hold and r.get("staffing") and clones_this_tick(acts, "check") >= r["staffing"]["launch_per_tick"]:
            hold = "clones per tick"
        hold = hold or ("memory after its last clone" if now < st.get("clone_again_at", 0) else None)
        hold = hold or make_room(store, fx, r, now, acts)
        if hold:
            acts.append({"do": "check_waits", "item": item, "why": hold})
            return
        acts.append({"do": "clone_try", "by": "check"})
        clean, why = fx.clean_checkout(st, c["sha"])
        if why:
            if POOL_REFUSED not in why:     # a full pool is a wait: the launch path is fine, the engine must not back off
                launch_failed(store, r, now, why)
            acts.append({"do": "check_waits", "item": item, "why": "pool full: " + why if POOL_REFUSED in why else why})
            return
        gb = fx.mem_gb()
        acts.append({"do": "mem_after_clone", "gb": gb})
        if gb < r["min_mem_available_gb"] or fx.paused():      # the clone itself costs gigabytes; admission saw the host before it
            fx.remove_clone({"clone": clean})
            with store.lock():                  # others go first: the same clone every tick would starve them
                st = store.load(item)           # make_room may have written this record since it was read
                st["clone_again_at"] = now + 600
                store.save(st)
            acts.append({"do": "check_waits", "item": item, "why": "memory after the clone"})
            return
        nonce = hashlib.sha256(os.urandom(16)).hexdigest()[:24]
        n = (st.get("check_count") or 0) + 1
        unit = unit_name("check", item, st["gen"]) + "-c%d" % n
        desc = run_desc(store, r, unit, now)
        box = None
        if relentless_wall.enforced(r):
            box = relentless_wall.make_box(relentless_wall.profile(r), clean, c["sha"], nonce,
                                           grants=list(dict.fromkeys(relentless_reachfix.grants(st) +
                                                  relentless_reach.box_grants(st.get("contract"), r, clean))),
                                           base=st.get("base"), item=item)
        gen0 = st["gen"]
        thru = relentless_wall.through(relentless_wall.profile(r), [json.dumps(st.get("contract") or {}),
                                       c.get("evidence") or "", fx.item_text(item) or ""]) if box else []
        if box:     # a passed reach repair's read paths (relentless_reachfix), re-read against the rules at every launch
            thru = thru + [p for p in relentless_reachfix.paths(st) if p not in thru
                           and not relentless_reachfix.refused(p, r, store.root)]
        with store.lock():              # the whole identity is on disk before the unit exists, and before any offbox run:
            st = store.load(item)       # a supervisor killed mid-reading leaves a check that dies as a lost checker
            if not st or st["status"] != "candidate" or st["gen"] != gen0 or (st.get("candidate") or {}).get("sha") != c["sha"]:
                # compare-and-set: ticks are serialised by tick.lock, but should two ever prepare the same candidate,
                # only the first installs its check; the other's clone and box go (GPT round 2)
                race = True
            else:
                race = False
                st["status"] = "checking"
                st["check_count"] = n
                st["check"] = {"nonce": nonce, "unit": unit, "at": now, "clone": clean, "run": desc,
                               "deadline": now + r["check_max_s"] + r["launch_grace_s"],
                               "bind": {"sha": c["sha"], "gen": gen0, "hash": contract_hash(st.get("contract"))}}
                if box:
                    st["check"]["box"] = box
                    st["check"]["through"] = thru       # the resume binds the same paths
                store.save(st)
        if race:
            fx.remove_clone({"clone": clean})
            if box:
                relentless_wall.remove_box(box)
            acts.append({"do": "check_race", "item": item})
            return
        readings = offbox_readings(fx, st["contract"], r, {"sha": c["sha"], "repo": clean, "item": st["item"]})
        if box and readings:        # what the box cannot reach, read outside it just now: raw output and exit, no worker words
            relentless_wall.write_offbox(box, readings)
        if box and (st["contract"] or {}).get("live"):     # the live line's reading, too: 33 of 60 CANNOT REACH were it
            relentless_reach.write_live(box, relentless_reach.live_reading(st["contract"]["live"],
                                                                           getattr(fx, "live_check", None), now))
        if box:
            why = fx.launch(st, desc, "\n".join([relentless_wall.marker_prompt(st, fx.item_text(item), box, relentless_wall.adapters(r))]
                                                + relentless_wall.through_lines(thru)
                                                + relentless_reach.live_lines(st["contract"], box)
                                                + relentless_game.checker_lines(st["contract"])), r["checker_agent"],
                            os.path.join(box, "tree"), r["check_max_s"],
                            relentless_wall.unit_env(relentless_wall.profile(r), box),
                            relentless_wall.props(relentless_wall.profile(r), box, [store.root], thru))
        else:
            why = fx.launch(st, desc, checker_prompt(st, fx.item_text(item), nonce, readings), r["checker_agent"], clean,
                            r["check_max_s"], {"RELENTLESS_ROOT": store.root})
        with store.lock():
            st = store.load(item)
            if why:
                st["status"] = "candidate"
                st["check"] = None
                launch_failed(store, r, now, why)
            store.save(st)
        if why:     # nothing ran in it: let it go now, or the pool holds it an hour as a fresh orphan
            remove_check_clone(fx, {"check": {"clone": clean}, "quarantined": st["quarantined"]})
        acts.append({"do": "check_started" if not why else "check_launch_failed", "item": item})
        return

    if s == "checking":
        chk = st["check"]
        if chk.get("resume"):
            check_resume(store, fx, r, item, now, acts)
            return
        got = relentless_wall.read_verdict(chk["box"]) if chk.get("box") and not chk.get("expired") else None
        if got and chk.get("verdict") is None:      # the box is the walled Marker's way out: the nonce is the store's own
            try:        # a file on disk is recorded, never refused (strict=False): read_as reads it
                verdict(store, item, chk["nonce"], got["word"], got["reasons"], now, got.get("defects"), got.get("unreached"),
                        strict=False, proposals=got.get("proposals"), controls=got.get("controls"),
                        changed=relentless_wall.changed_paths(chk["box"]))
            except Fenced:
                return
            except (ValueError, TypeError, KeyError) as e:      # malformed past all that: a lost check, once - never a raise a tick
                with store.lock():
                    cur = store.load(item)
                    if cur and cur["status"] == "checking" and cur["check"].get("nonce") == chk["nonce"]:
                        cur["check"]["expired"] = True
                        cur["check"]["malformed"] = str(e)[:300]
                        store.save(cur)
                acts.append({"do": "verdict_malformed", "item": item, "why": str(e)[:200]})
            chk = store.load(item)["check"]
        word = chk.get("verdict")
        if word is None and fx.alive(chk.get("run")) and now - chk["at"] < r["check_max_s"] + r["launch_grace_s"]:
            return
        if word is None and not chk.get("expired"):    # fence the nonce before the stop: late is no verdict
            with store.lock():
                cur = store.load(item)
                if cur["status"] == "checking":
                    cur["check"]["expired"] = cur["check"].get("verdict") is None
                    store.save(cur)
        since = chk.get("verdict_at") or chk["at"] + r["check_max_s"] + r["launch_grace_s"]
        if not settle(store, fx, r, item, "check", min(since, now), now, acts):
            return
        lost = fx.account_loss(chk.get("run"), chk.get("clone"), chk["at"], chk.get("box")) if word is None else None
        # its own death, not our stop at check_max_s (a stopped run may leave a line on .err too)
        died = fx.death_note(chk.get("run")) if word is None and not lost and \
            (chk.get("lost_seen") or now) - chk["at"] < r["check_max_s"] else None     # judged at first sighting (Codex r3)
        c = st["candidate"]
        drop = []      # a checker clone a retry lets go: removed out of the lock, or it sits an hour as an orphan
        told = []      # a quarantine's Conductor line, written out of the lock
        failed = None  # the Marker's FAIL (sha, reasons), written to the ledger out of the lock
        try:
            with store.lock():
                st = store.load(item)
                if st["status"] != "checking":
                    return
                returns0, spent0 = st["returns"], st["spent"]       # what it came to this verdict with
                due = quarantine_due(st, r, returns0, spent0)
                word = st["check"].get("verdict")
                if word is None and lost and lost.get("session"):
                    # it read the evidence before the cut: the same checker, clone, box and nonce resume once the breaker
                    # closes (check_resume), its context kept (RELENTLESS_RESUME_BUILD_ACCOUNT_LOST_RUNS)
                    st["check"]["resume"] = {"session": lost["session"], "at": now}
                    store.attempt(item, {"at": iso(now), "gen": st["gen"], "end": "account_lost", "detail": lost["why"][:600],
                                         "session": lost["session"]})
                    store.save(st)
                    if lost["kind"] == "account_error":
                        launch_failed(store, r, now, lost["why"])
                    acts.append({"do": "account_lost", "item": item, "kind": lost["kind"], "resume": "check"})
                    return
                if word is None and lost:       # the account's doing, not the checker's: same candidate, a new checker, no count
                    drop.append({"check": dict(st["check"]), "quarantined": list(st["quarantined"])})
                    st["status"] = "candidate"
                    st["check"] = None
                    store.attempt(item, {"at": iso(now), "gen": st["gen"], "end": "account_lost", "detail": lost["why"][:600]})
                    store.save(st)
                    if lost["kind"] == "account_error":
                        launch_failed(store, r, now, lost["why"])
                    acts.append({"do": "account_lost", "item": item, "kind": lost["kind"]})
                    return
                if word is None:
                    # as for a worker: a change-over logs its event minutes after the kill, so judge after it could have
                    seen = st["check"].setdefault("lost_seen", now)
                    if now - seen < r.get("account_settle_s", 0):
                        store.save(st)
                        return
                    if died:
                        # it died saying why on .err with no .json: the launch path, not the item. No count, same
                        # candidate; the breaker carries it, so repeats open it and one cause twice is the emergency
                        why = "checker %s died with no output: %s" % ((st["check"].get("run") or {}).get("unit"), died)
                        drop.append({"check": dict(st["check"]), "quarantined": list(st["quarantined"])})
                        st["status"] = "candidate"
                        st["check"] = None
                        store.attempt(item, {"at": iso(now), "gen": st["gen"], "end": "check_launch_fail", "detail": why[:600]})
                        store.save(st)
                        launch_failed(store, r, now, why)
                        acts.append({"do": "check_launch_fail", "item": item, "why": why[:200]})
                        return
                    n = st.get("check_lost", 0) + 1
                    st["check_lost"] = n
                    if n >= r["same_failure_limit"]:
                        st["check_lost"] = 0
                        fail(store, st, "checker_lost", "%d checkers gave no verdict" % n, r, now)
                    else:
                        drop.append({"check": dict(st["check"]), "quarantined": list(st["quarantined"])})
                        st["status"] = "candidate"
                        st["check"] = None
                        store.save(st)
                    acts.append({"do": "checker_lost", "item": item, **run_output(chk.get("run"))})
                    return
                moved = bind_moved(st)
                if moved:
                    # rule 6.1: a verdict is consumed only on the sha, gen and contract its checker launched on. Anything
                    # moved: the checker judged something else - no verdict, no strike, the candidate is checked afresh
                    drop.append({"check": dict(st["check"]), "quarantined": list(st["quarantined"])})
                    st["status"] = "candidate"
                    st["check"] = None
                    store.attempt(item, {"at": iso(now), "gen": st["gen"], "end": "check_rebound", "detail": moved[:600]})
                    store.save(st)
                    acts.append({"do": "check_rebound", "item": item, "why": moved[:200]})
                    return
                acted, blind = relentless_wall.read_as(word, st["check"].get("reasons"), st["check"].get("defects"),
                                                       st["check"].get("unreached"))
                if acted == relentless_wall.UNMEASURED:     # the box could not reach the evidence: no work goes back
                    gone = {"check": dict(st["check"]), "quarantined": st["quarantined"]}
                    said = unmeasured(store, st, word, blind, r, now)
                    acts.append({"do": "unmeasured", "item": item, "said": word, "held": st["status"] == "held"})
                    if due:
                        told.append(quarantine(store, st, word, returns0, spent0, now))
                else:
                    said = None
                    if "blind" in st or "recheck_at" in st:
                        st.pop("blind", None)
                        st.pop("recheck_at", None)
                        store.save(st)          # a real verdict ends the run of blind ones
                    if acted == "FAIL":     # an observed defect is a FAIL whatever word it came under
                        failed = (c["sha"], st["check"].get("reasons"))
                        if st["check"].get("defects"):      # structured: routed on its causes, a builder only for PRODUCT
                            routed = cause_fail(store, st, r, now)
                            acts.append({"do": "blind_fail", "item": item, "cause": routed})
                        else:       # old-format prose: blamed before rebuild (relentless_attrib.gate), as before
                            fail(store, st, "blind_fail", st["check"].get("reasons"), r, now)
                            acts.append({"do": "blind_fail", "item": item})
                        if due:
                            told.append(quarantine(store, st, word, returns0, spent0, now))
                weak = None
                if acted == "WEAK":     # read_as decides: a word it reads as UNMEASURED was handled above
                    reasons = st["check"].get("reasons")
                    fail(store, st, "proof_weak", reasons, r, now)
                    weak = "blind check at %s: WEAK, the proof has holes and the work is unproven; item stays open: %s" % (c["sha"], reasons or "")
                    acts.append({"do": "proof_weak", "item": item})
                    if due:
                        told.append(quarantine(store, st, word, returns0, spent0, now))
        finally:
            for d in drop:
                remove_check_clone(fx, d)
            for t in told:
                if t:       # one line per quarantine: the key is the item and its pass, never re-told on a timer
                    attention(store, fx, "quarantine:%s" % item, t, now, level=(QUARANTINE_RETURNS, returns0))
                    acts.append({"do": "quarantined", "item": item, "why": t[:200]})
        if failed:          # the verdict the Close gate reads, out of the store's lock (MARKER_FAIL_WIRE_INTO_CLOSE_LOCK)
            err = fx.ledger_marker_fail(item, *failed)
            if err:
                acts.append({"do": "marker_fail_unrecorded", "item": item, "why": err[:200]})
            return
        if said:            # the ledger's own write and the clone's removal, out of the store's lock
            remove_check_clone(fx, gone)
            fx.ledger_note(item, said)
            return
        if weak:        # the ledger's own write, out of the store's lock
            fx.ledger_note(item, weak)
            return
        live = (st["contract"] or {}).get("live")
        broken = fx.live_check(live, fx.commit_time(c["sha"])) if live else None
        if live_wait(store, fx, item, broken, now, acts, st):
            return
        pub = None if broken else fx.published(c["sha"])
        if pub is None and not broken:
            acts.append({"do": "publish_unknown", "item": item})
            return
        if not broken and not pub:
            broken = "%s left origin/main" % c["sha"]
        with store.lock():
            st = store.load(item)
            if st["status"] != "checking":
                return
            st.pop("live_wait_since", None)
            if broken:
                fail(store, st, "live_broken", broken, r, now)
                acts.append({"do": "live_broken", "item": item, "after_check": True})   # a checker PASSed: ends ops_watch's run of dead checkers
                return
            cur = st["check"] or {}     # read as above: a WEAK the live rule reads as PASS closes too (GPT pass 12)
            if not cur.get("verdict") or relentless_wall.read_as(cur["verdict"], cur.get("reasons"), cur.get("defects"),
                                                                 cur.get("unreached"))[0] != "PASS":
                return          # the verdict moved while the live line was read: the next tick reads it again
            if relentless_game.owes(st, c["sha"]):     # green offline on this sha: the game clauses are next, not close
                relentless_game.enter(store, st, c["sha"], now)
                game = True
            else:
                game = False
                st["status"] = "closing"
                st.pop("close_retry", None)
                st.pop("close_tries", None)
                store.save(st)
                acts.append({"do": "check_passed", "item": item, "sha": c["sha"]})  # a verdict: ops_watch's run of dead checkers ends here
        if game:
            remove_check_clone(fx, st)
            acts.append({"do": "game_entered", "item": item, "sha": c["sha"]})
            return
        s = "closing"

    if s == "closing":
        st = store.load(item)
        c = st["candidate"]
        if st.get("tomb_since"):
            # closed on the ledger; `closing` stays the guard's word until the other seat's stale tree shows it gone
            if (foreign_retired(r) or fx.seat_heard(item, iso(st["started_at"]))
                    or now - st["tomb_since"] >= r["staffing"]["tomb_max_s"]):
                finished(store, fx, item, c, now, acts)
            return
        retry = st.get("close_retry")
        tries = int(st.get("close_tries") or 0) + 1
        cap = int(r.get("close_retry_max", CLOSE_RETRY_MAX))
        if tries > cap:     # rule 6.2: a close that never lands hands the item back instead of retrying for ever
            with store.lock():
                cur = store.load(item)
                if cur["status"] != "closing":
                    return
                cur.pop("close_tries", None)
                fail(store, cur, "close_stuck", "%d closing attempts did not land the close on %s" % (cap, c["sha"]), r, now)
            acts.append({"do": "close_stuck", "item": item, "tries": cap})
            return
        with store.lock():  # persisted before the attempt, so a crash inside it is already a counted retry
            cur = store.load(item)
            cur["close_retry"] = True
            cur["close_tries"] = tries
            store.save(cur)
        if retry:       # a retry is a new decision: what authorized the first try is asked again
            live = (st["contract"] or {}).get("live")
            broken = fx.live_check(live, fx.commit_time(c["sha"])) if live else None
            if live_wait(store, fx, item, broken, now, acts, st):
                return          # close_retry stays set: the next tick asks the live line again
            pub = None if broken else fx.published(c["sha"])
            if pub is None and not broken:
                acts.append({"do": "publish_unknown", "item": item})
                return
            if broken or not pub:
                with store.lock():
                    st = store.load(item)
                    fail(store, st, "live_broken", broken or "%s left origin/main" % c["sha"], r, now)
                acts.append({"do": "live_broken", "item": item})
                return
        reason = "relentless: blind PASS at %s after %d return(s): %s" % (c["sha"], st["returns"],
                                                                         (st["check"].get("reasons") or "")[:220])
        why = fx.ledger_close(item, c["sha"], reason, (st["contract"] or {}).get("live"))
        if why and "has not earned its close" in why:    # a refusal is no transient: a retry would refuse for ever
            with store.lock():
                st = store.load(item)
                fail(store, st, "close_refused", why, r, now)
            acts.append({"do": "close_refused", "item": item, "why": why})
            return
        if why:
            led = fx.item_state(item)
            if led is not None and led["state"] in ("dropped", "superseded"):  # his drop while closing: no close will land
                with store.lock():
                    cur = store.load(item)
                    cur["gen"] += 1
                    cur["status"] = "retiring"
                    cur["stopping_since"] = now
                    store.save(cur)
                acts.append({"do": "retire", "item": item, "why": "ledger says %s while closing" % led["state"]})
                return
            acts.append({"do": "close_retry", "item": item, "why": why})
            return
        if st.get("foreign") and not foreign_retired(r):
            with store.lock():
                st = store.load(item)
                st["tomb_since"] = now
                store.attempt(item, {"at": iso(now), "end": "done", "sha": c["sha"]})
                store.save(st)
            remove_check_clone(fx, st)
            fx.remove_clone(st)
            acts.append({"do": "closed_waiting_for_seat", "item": item})
            return
        finished(store, fx, item, c, now, acts, attempt=True)


def check_resume(store, fx, r, item, now, acts):
    """A checker the account cut after real work: once a place and the breaker allow, `claude -p --resume` its session in
    the same clone and box with the same nonce, so what it read is not read again. A tree that is gone, or a launch that
    fails, falls back to the old road: the candidate waits for a fresh checker, no count."""
    st = store.load(item)
    chk = st["check"]
    active = sum(1 for x in store.states() if x["status"] in RUNS_A_PLACE) + helps_running(store)
    hold = admission(store, fx, r, now, active, extra=1)    # it holds a place already: never starved behind new work
    if hold:
        acts.append({"do": "check_waits", "item": item, "why": "resume: " + hold})
        return
    box = chk.get("box")
    cwd = os.path.join(box, "tree") if box else chk.get("clone")
    why = None if cwd and tree_present(cwd) else "its tree is gone"
    n = (st.get("check_count") or 0) + 1
    unit = unit_name("check", item, st["gen"]) + "-c%d" % n
    desc = run_desc(store, r, unit, now)
    desc["resume"] = chk["resume"]["session"]
    if not why:
        with store.lock():
            st = store.load(item)
            if st["status"] != "checking" or (st.get("check") or {}).get("nonce") != chk["nonce"]:
                return
            st["check_count"] = n
            st["check"].update(unit=unit, run=desc, at=now, expired=False)
            st["check"]["resumed"] = st["check"].pop("resume")["session"]
            st["check"].pop("lost_seen", None)
            store.save(st)
        if box:
            why = fx.launch(st, desc, resume_prompt(st, "check"), r["checker_agent"], cwd, r["check_max_s"],
                            relentless_wall.unit_env(relentless_wall.profile(r), box),
                            relentless_wall.props(relentless_wall.profile(r), box, [store.root], chk.get("through") or ()))
        else:
            why = fx.launch(st, desc, resume_prompt(st, "check"), r["checker_agent"], cwd, r["check_max_s"],
                            {"RELENTLESS_ROOT": store.root})
        if not why:
            store.attempt(item, {"at": iso(now), "gen": st["gen"], "check": unit, "resumed": desc["resume"]})
            acts.append({"do": "check_resumed", "item": item, "unit": unit})
            return
        launch_failed(store, r, now, why)
    with store.lock():
        st = store.load(item)
        if st["status"] != "checking" or (st.get("check") or {}).get("nonce") != chk["nonce"]:
            return
        gone = {"check": dict(st["check"]), "quarantined": list(st["quarantined"])}
        st["status"] = "candidate"
        st["check"] = None
        store.save(st)
    remove_check_clone(fx, gone)      # its box is an ended check's now: the reaper takes it, as on every other road
    acts.append({"do": "check_resume_dropped", "item": item, "why": why[:200]})


def help_over(store, fx, item, word, now, acts):
    """One consult done with, however. Under no lock on entry; removes its clone unless a quarantined run still sits in it."""
    with store.lock():
        st = store.load(item)
        h = st["help"]
        h["status"] = word
        keep = any(q.get("clone") == h.get("clone") and not q.get("reaped") for q in st["quarantined"])
        store.attempt(item, {"at": iso(now), "gen": st["gen"], "help": word, "round": h.get("round"),
                             "agent": h.get("agent"), **({"mode": h["mode"]} if h.get("mode") else {})})
        relentless_attrib.help_over(store, st, word, now, sys.modules[__name__])   # a diagnosis owed never falls to a builder
        store.save(st)
    if h.get("clone") and not keep:
        fx.remove_clone({"clone": h["clone"], "item": item})
    if word != "answered" and h.get("mode") == relentless_attrib.DIAGNOSE:
        fx.ledger_note(item, "relentless: the diagnosis of a validation ending gave no attribution (%s); the candidate is "
                             "held for the seat with no strike" % h.get("end", "no answer"))
    elif word == "failed":
        fx.ledger_note(item, "relentless: a consult gave no options (%s); the item carries on without" % h.get("end", "no answer"))
    acts.append({"do": "help_" + word, "item": item})


def help_retry(store, fx, item, why, r, now, acts):
    """No options from this try. Another, or the item carries on: a consult never holds a worker back for good."""
    with store.lock():
        st = store.load(item)
        h = st["help"]
        h["end"] = why[:200]
        again = h["tries"] < r["circling"]["help_launch_tries"]
        if again:
            h.update(status="wanted", run=None, nonce=None, clone=None)
        store.save(st)
    if again:
        acts.append({"do": "help_retry", "item": item, "why": why[:200]})
    else:
        help_over(store, fx, item, "failed", now, acts)


def help_start(store, fx, r, item, now, acts):
    """Launch the fresh agent. The shape of the check's launch: a place, room, a clean clone, identity on disk first."""
    st = store.load(item)
    h = st["help"]
    if now - h["at"] >= r["circling"]["help_wait_s"]:
        br = load_breaker(store)
        if br.get("until", 0) > now and relentless_account.breaker_on_account(br):
            # no room because the account is out, not because the consult failed: the wait starts over
            with store.lock():
                cur = store.load(item)
                cur["help"]["at"] = now
                store.save(cur)
            store.journal({"at": iso(now), "do": "help_account_wait", "item": item, "why": (br.get("why") or "")[:200]})
            acts.append({"do": "help_waits", "item": item, "why": "account: " + (br.get("why") or "")[:160]})
            return
        if h.get("mode") == relentless_attrib.DIAGNOSE:
            # RELENTLESS_ATTRIB_FIX_CONSULT_NO_ROOM_HOLDS: a diagnosis owed holds no worker back (the item waits blocked
            # either way), so a wait for room is no failed consult: it starts over and retries on a later tick
            with store.lock():
                cur = store.load(item)
                cur["help"]["at"] = now
                cur["help"]["room_waits"] = (cur["help"].get("room_waits") or 0) + 1
                store.save(cur)
            store.journal({"at": iso(now), "do": "help_room_wait", "item": item, "waited_s": int(now - h["at"])})
            acts.append({"do": "help_waits", "item": item, "why": "no room in %d s: the diagnosis waits on" % (now - h["at"])})
            return
        h_end = "no room in %d s" % (now - h["at"])
        with store.lock():
            cur = store.load(item)
            cur["help"]["end"] = h_end
            store.save(cur)
        help_over(store, fx, item, "failed", now, acts)
        return
    active = sum(1 for x in store.states() if x["status"] in RUNS_A_PLACE) + helps_running(store)
    hold = admission(store, fx, r, now, active, extra=1)
    if hold:
        acts.append({"do": "help_waits", "item": item, "why": hold})
        return
    res = h.get("resume")
    if res and not (h.get("clone") and tree_present(h["clone"]) and h.get("nonce")):
        with store.lock():      # its tree is gone: a fresh consult, as before resuming existed
            cur = store.load(item)
            cur["help"].pop("resume", None)
            cur["help"].update(nonce=None, clone=None)
            store.save(cur)
        res = None
    if res:     # resumed in its own clone, before any room is made: make_room could evict the very tree it resumes in
        help_resume(store, fx, r, item, now, acts)      # (Codex, ..._TEN_MORE #7)
        return
    if r.get("staffing") and clones_this_tick(acts, "check") >= r["staffing"]["launch_per_tick"]:
        hold = "clones per tick"
    hold = hold or ("memory after its last clone" if now < st.get("clone_again_at", 0) else None)
    hold = hold or make_room(store, fx, r, now, acts)
    if hold:
        acts.append({"do": "help_waits", "item": item, "why": hold})
        return
    acts.append({"do": "clone_try", "by": "check"})
    sha = fx.head()
    clean, why = fx.help_checkout(st, sha) if sha else (None, "origin/main not read")
    if why:
        if POOL_REFUSED not in why:
            launch_failed(store, r, now, why)
        acts.append({"do": "help_waits", "item": item, "why": "pool full: " + why if POOL_REFUSED in why else why})
        return
    gb = fx.mem_gb()
    acts.append({"do": "mem_after_clone", "gb": gb})
    if gb < r["min_mem_available_gb"] or fx.paused():
        fx.remove_clone({"clone": clean, "item": item})
        with store.lock():
            st = store.load(item)
            st["clone_again_at"] = now + 600
            store.save(st)
        acts.append({"do": "help_waits", "item": item, "why": "memory after the clone"})
        return
    nonce = hashlib.sha256(os.urandom(16)).hexdigest()[:24]
    n = (st.get("help_count") or 0) + 1
    desc = run_desc(store, r, unit_name("help", item, st["gen"]) + "-h%d" % n, now)
    with store.lock():              # the whole identity is on disk before the unit exists
        st = store.load(item)
        st["help_count"] = n
        h = st["help"]
        agent = help_vendor(st, r)
        h.update(status="running", nonce=nonce, clone=clean, run=desc, started_at=now, tries=h["tries"] + 1, agent=agent,
                 deadline=now + r["circling"]["help_max_s"] + r["launch_grace_s"])
        store.save(st)
    tried = failed_approaches(store, item)
    env = {"RELENTLESS_ROOT": store.root}
    if h.get("mode") == relentless_attrib.DIAGNOSE:
        prompt = relentless_attrib.prompt(st, fx.item_text(item), store.attempts(item), nonce, r)
    elif agent == VENDOR_AGENT:
        env["RELENTLESS_HELP_NONCE"] = nonce
        prompt = help_prompt_vendor(st, fx.item_text(item), tried, r, store.attempts(item))
    else:
        prompt = help_prompt(st, fx.item_text(item), tried, nonce, r, store.attempts(item))
    why = fx.launch(st, desc, prompt, agent, clean, r["circling"]["help_max_s"], env)
    if why:
        fx.remove_clone({"clone": clean, "item": item})
        launch_failed(store, r, now, why)
        help_retry(store, fx, item, why, r, now, acts)
        return
    acts.append({"do": "help_started", "item": item, "unit": desc["unit"]})


def help_resume(store, fx, r, item, now, acts):
    """help_start's road for a consult the account cut after real work: its clone, nonce and agent, `claude -p --resume`."""
    with store.lock():
        st = store.load(item)
        h = st["help"]
        n = (st.get("help_count") or 0) + 1
        desc = run_desc(store, r, unit_name("help", item, st["gen"]) + "-h%d" % n, now)
        desc["resume"] = h.pop("resume")["session"]
        st["help_count"] = n
        h.update(status="running", run=desc, started_at=now, tries=h["tries"] + 1, expired=False, resumed=desc["resume"])
        store.save(st)
    env = {"RELENTLESS_ROOT": store.root}
    why = fx.launch(st, desc, resume_prompt(st, "help"), h["agent"], h["clone"], r["circling"]["help_max_s"], env)
    if why:
        fx.remove_clone({"clone": h["clone"], "item": item})
        launch_failed(store, r, now, why)
        help_retry(store, fx, item, why, r, now, acts)
        return
    store.attempt(item, {"at": iso(now), "gen": st["gen"], "help": "resumed", "session": desc["resume"],
                         "agent": h["agent"], **({"mode": h["mode"]} if h.get("mode") else {})})
    acts.append({"do": "help_resumed", "item": item, "unit": desc["unit"]})


def help_account_lost(store, fx, r, item, lost, now, acts):
    """A consult the account cut: no try charged, its wait starts over. With real work done its clone and nonce stay for
    help_resume; with none it is simply wanted again."""
    with store.lock():
        st = store.load(item)
        h = st["help"]
        keep = bool(lost.get("session")) and h.get("agent") != VENDOR_AGENT
        drop = None if keep else h.get("clone")
        h["tries"] = max(0, h["tries"] - 1)
        h.update(status="wanted", run=None, at=now, expired=False)
        if keep:
            h["resume"] = {"session": lost["session"], "at": now}
        else:
            h.pop("resume", None)
            h.update(nonce=None, clone=None)
        store.attempt(item, {"at": iso(now), "gen": st["gen"], "help": "account_lost", "detail": lost["why"][:600],
                             **({"session": lost["session"]} if keep else {})})
        store.save(st)
    if drop and not any(q.get("clone") == drop for q in st["quarantined"]):
        fx.remove_clone({"clone": drop, "item": item})
    if lost["kind"] == "account_error":
        launch_failed(store, r, now, lost["why"])
    acts.append({"do": "account_lost", "item": item, "kind": lost["kind"], "resume": "help" if keep else None})


def help_step(store, fx, r, item, now, acts):
    """One item's consult, beside its run and independent of it. Pure lifecycle: the worker's status only ends it."""
    st = store.load(item)
    if not st or not r.get("circling"):
        return
    gone = st["status"] in ENDED or st["status"] == "retiring"
    if not help_pending(st):
        if gone:
            return
        if no_room_hold(st):    # held before a wait for room started over (RELENTLESS_ATTRIB_FIX_CONSULT_NO_ROOM_HOLDS)
            rediagnose(store, item, "auto: the diagnostic consult had only lacked room", now, r)
            acts.append({"do": "rediagnose", "item": item, "why": "no room hold"})
            return
        with store.lock():
            cur = store.load(item)
            if not force_help(store, cur, r, now):      # one held back by the cool, now over
                return
            store.save(cur)
        st = cur
    h = st["help"]
    if h["status"] == "wanted":
        if gone:
            help_over(store, fx, item, "dropped", now, acts)
        else:
            help_start(store, fx, r, item, now, acts)
        return
    limit = h["started_at"] + r["circling"]["help_max_s"]
    answered = h.get("answered_at")
    if not gone and not answered and fx.alive(h.get("run")) and now < limit:
        return
    if not answered and not h.get("expired"):       # fence the nonce before the stop: late is no answer
        with store.lock():
            cur = store.load(item)
            cur["help"]["expired"] = cur["help"].get("answered_at") is None
            store.save(cur)
    if not settle(store, fx, r, item, "help", min(answered or limit, now), now, acts):
        return
    cur = store.load(item)
    if cur["help"].get("answered_at"):
        help_over(store, fx, item, "answered", now, acts)
    elif gone:
        help_over(store, fx, item, "dropped", now, acts)
    else:
        sat = any(q.get("clone") == h.get("clone") and not q.get("reaped") for q in cur["quarantined"])
        # a quarantined helper may still run in that clone: no resume there with its nonce, a fresh try (Codex r5 part6 #1)
        lost = fx.account_loss(h.get("run"), h.get("clone"), h["started_at"]) \
            if h.get("agent") != VENDOR_AGENT and not sat else None
        if lost:
            help_account_lost(store, fx, r, item, lost, now, acts)
            return
        with store.lock():      # the next try is a new consult: its nonce must not read as expired
            cur = store.load(item)
            cur["help"]["expired"] = False
            store.save(cur)
        if not any(q.get("clone") == h.get("clone") for q in cur["quarantined"]):
            fx.remove_clone({"clone": h.get("clone"), "item": item})
        help_retry(store, fx, item, "no answer", r, now, acts)


def helps_running(store):
    return sum(1 for x in store.states() if (x.get("help") or {}).get("status") == "running")


def live_wait(store, fx, item, why, now, acts, st):
    """True when the live line is NOT YET (live_line.NotYet: its reading predates a commit still inside one cadence):
    the item keeps its status and the next tick reads the line again; never live_broken (LIVECHECK_FIX_JUMPS_THE_GUN).
    The first wait frees the checker's clone (a PASS needs it no more; the wait may run to max_age) and says so once."""
    import live_line
    if not live_line.not_yet(why):
        return False
    if st.get("live_wait_since") is None:
        with store.lock():
            cur = store.load(item)
            if cur["status"] != st["status"] or cur.get("live_wait_since") is not None:
                return True
            cur["live_wait_since"] = now
            store.save(cur)
        if cur["status"] == "checking":
            remove_check_clone(fx, cur)
        acts.append({"do": "live_waiting", "item": item, "why": str(why)[:200]})
    return True


def remove_check_clone(fx, st):
    """A quarantined checker still sits in its clone: the reaper removes it when the run is dead, nobody before."""
    c = (st.get("check") or {}).get("clone")
    if not any(q.get("clone") == c and not q.get("reaped") for q in st["quarantined"]):
        fx.remove_clone({"clone": c})


def finished(store, fx, item, c, now, acts, attempt=False):
    with store.lock():
        st = store.load(item)
        st["status"] = "done"
        st["done_at"] = now
        if attempt:
            store.attempt(item, {"at": iso(now), "end": "done", "sha": c["sha"]})
        store.save(st)
    remove_check_clone(fx, st)
    fx.remove_clone(st)
    try:            # its run's TMPDIR now, if the run is over; the tick's sweep takes it otherwise
        getattr(fx, "drop_run_tmp", lambda run: None)(st.get("run"))
    except Exception:  # noqa: BLE001
        pass
    store.journal({"at": iso(now), "do": "done", "item": item, "sha": c["sha"], "returns": st["returns"]})
    acts.append({"do": "done", "item": item})


def in_line(st):
    """Queued and able to start: an item the books have not heard of holds no place, or unpublished work stops enrolment."""
    return st["status"] == "queued" and not st.get("awaiting_ledger")


def retire(store, fx, states, now, acts, r=None):
    """The ledger closed an item from outside (his drop, a supersede): fence first, then step() drains the runs."""
    for st in states:
        if st["status"] not in OPEN or st["status"] in ("closing", "retiring", relentless_game.GAME):     # game: its own step
            continue
        led = fx.item_state(st["item"])
        if st.get("awaiting_ledger") and led is not None:       # published: it takes its place in the count again
            with store.lock():
                cur = store.load(st["item"])
                cur["awaiting_ledger"] = False
                store.save(cur)
        if r and st["status"] == "queued" and pool_excluded(st["item"], r):
            # started means the ledger says doing with no one on it: hand it back or it reads as worked on for good.
            # Back first: `retired` is never looked at again, so a refused hand-back must come round next tick.
            ours = st["ledger_started"] and led and led["state"] == "doing" and led.get("owner") == r.get("seat")
            why = fx.ledger_reclaim(st["item"]) if ours else None    # a reassigned item was handed back already
            if why:
                acts.append({"do": "retire_waits", "item": st["item"], "why": why})
                continue
            with store.lock():
                cur = store.load(st["item"])
                cur["status"] = "retired"
                store.save(cur)
            acts.append({"do": "retire", "item": st["item"], "why": "excluded in the rules"})
        elif led is None and st["status"] == "queued" and not st["ledger_started"]:
            # filed but not published yet: the books have not heard of it, and that is no close (five items ended
            # this way, 2026-11-01). It waits in line; the launch skips it until the ledger names it.
            if not st.get("awaiting_ledger"):
                with store.lock():
                    cur = store.load(st["item"])
                    cur["awaiting_ledger"] = True
                    store.save(cur)
                    store.journal({"at": iso(now), "do": "awaiting_ledger", "item": st["item"]})
                acts.append({"do": "awaiting_ledger", "item": st["item"]})
        elif led is None or led["state"] in ("done", "dropped", "superseded"):
            with store.lock():
                cur = store.load(st["item"])
                cur["gen"] += 1
                cur["status"] = "retiring"
                cur["stopping_since"] = now
                store.save(cur)
            acts.append({"do": "retire", "item": st["item"]})
        elif not st["ledger_started"] and st["status"] == "queued" and (
                led["state"] not in ("proposed", "ready") or led.get("lease")) and (
                not st.get("start_intent") or led.get("lease")):
            with store.lock():
                cur = store.load(st["item"])
                cur["status"] = "retired"           # a seat took it first; it was never ours
                store.save(cur)
            acts.append({"do": "retire", "item": st["item"], "why": "a seat took it"})


def spend_holds(store, fx, r, now, acts):
    """An item over item_spend_limit calls attention and keeps running: advisory since owner 2026-11-02 ("Nothing gets
    killed or stopped for that"; TOKEN_LIMITS_TAME_BARK_NO_BITE). One attention per item per crossing: at the limit, then
    at each doubling of it (SPEND_INCIDENT_FIX_BARKS_TILL_DONE), never again on a timer."""
    for st in store.states():
        limit = r["item_spend_limit"] + (st.get("spent_grace") or 0)
        owed = sum(1 for q in st["quarantined"] if not q.get("reaped")) * r["run_reserve"]   # charged when reaped
        if st["status"] in RUNS_A_PLACE + ("queued",) and st["spent"] + owed >= limit:
            if attention(store, fx, "item_spend_limit:%s" % st["item"],
                         "%s spent %d weighted tokens, over the advisory item_spend_limit %d by %d; nothing stopped. "
                         "Look: relentless.py show %s, its spend.jsonl rows" % (st["item"], st["spent"] + owed, limit,
                                                                              st["spent"] + owed - limit, st["item"]),
                         now, level=(limit, spend_level(st["spent"] + owed, limit))):
                acts.append({"do": "spend_attention", "item": st["item"], "spent": st["spent"] + owed, "limit": limit})


def clones_this_tick(acts, by=None):
    """A clone blocks the tick for minutes, and the tick has a timeout. Builders and checkers draw on separate budgets
    (`work` and `check`): one shared count let two checks starting in a tick stop every builder in it, so with runs
    shorter than a tick the belt ran one builder and one check against four places (2026-11-02, 16:36:58Z)."""
    return sum(1 for a in acts if a.get("do") == "clone_try" and (by is None or a.get("by", "check") == by))


def give_back(store, item, why, to="retired", reserved=None):
    """`retired`: the other seat's after all, never ours. `queued`: the ledger already says ours, so it must stay in
    the line: retired, nothing would ever pick it up again. `reserved`: the reserve_foreign token; the item moves only
    while that very reservation still stands (running, the same `reserving`), so a hold or fence that landed meanwhile
    is never overwritten (Codex r4 part4 #1). -> True when it moved."""
    with store.lock():
        cur = store.load(item)
        if reserved is not None and not still_reserved(cur, reserved):
            moved = False
        else:
            cur.pop("reserving", None)
            cur["status"] = to
            store.save(cur)
            moved = True
    store.journal({"at": iso(time.time()), "do": "give_back" if moved else "give_back_fenced", "item": item,
                   "why": why if moved else "%s; not given back: the reservation was overtaken (now %s)"
                   % (why, (cur or {}).get("status"))})
    return moved


def still_reserved(cur, reserved):
    return bool(cur) and cur["status"] == "running" and cur.get("reserving") == reserved


def reserve_foreign(store, fx, r, item, now, acts):
    """Take an item of the other seat without pulling its tree. Its old code reads `running` as leased, so from the
    write below its own claim, start and close are refused; then wait out a claim that passed the guard just before,
    look at what its tree has not published, and only then move the item. -> True when it is ours."""
    cfg = r["staffing"]
    with store.lock():
        cur = store.load(item)
        if cur["status"] != "queued":
            return False
        cur["status"] = "running"
        cur["reserving"] = now
        cur["started_at"] = now
        cur["run"] = None
        cur["foreign"] = True
        store.save(cur)
    fx.settle_wait(cfg["settle_s"])
    with store.lock():      # a hold or fence that landed during the wait wins: nothing here moves the item after it
        if not still_reserved(store.load(item), now):
            acts.append({"do": "reservation_overtaken", "item": item})
            return False
    words = fx.seat_words()
    theirs = (fx.item_state(item) or {}).get("owner") == foreign_seat(r)
    if words is None or item in words:
        why = "its tree is unreadable" if words is None else "its seat has an unpublished word on it"
        # a crash or a failed launch brings it back here already handed over: retired, it would strand as ours
        # and a word on it waits too: once published the ledger says what it was, and `retire` or the line acts on that
        give_back(store, item, why, "retired" if theirs and words is not None else "queued", reserved=now)
        acts.append({"do": "give_back", "item": item, "why": why})
        return False
    why = fx.ledger_take(item) if theirs else None
    if why:     # often a passing failure, and `retired` is for good: only a take that keeps failing ends the item here
        with store.lock():
            cur = store.load(item)
            cur["take_fails"] = fails = cur.get("take_fails", 0) + 1
            store.save(cur)
        give_back(store, item, why, "retired" if fails >= 3 else "queued", reserved=now)
        acts.append({"do": "give_back", "item": item, "why": why})
        return False
    return True


def mods_held(store, fx, item, states=None):
    """The mods some other item's worker or candidate holds: {mod: that item}. A candidate counts, its FAIL comes back."""
    return {m: x["item"] for x in (store.states() if states is None else states)
            if x["status"] in HOLDS_A_PLACE and x["item"] != item
            for m in fx.item_mods(x)}


def lease(store, fx, r, now, acts, wake=None):
    """Fill the free places, top of the queue first. An item the machine cannot run now keeps its place. Afterwards,
    content the health pause held is timed for the Conductor's alarm (pause_alarm). `wake`: the tick's serve_wake, called
    before each item, so a round or staging that ends while clones are made gets its proof now, not after the lease
    (STAGE_WAKE_TUNE_NAPS_AFTER_LOAD)."""
    seen = {"known": False, "pause": None, "stopped": []}
    try:
        return _lease(store, fx, r, now, acts, seen, wake)
    finally:
        try:
            pause_alarm(store, fx, seen, now, acts)
        except Exception as e:  # noqa: BLE001  the alarm's clock never stops a lease; said on the journal
            store.journal({"at": iso(now), "do": "pause_alarm_failed", "why": "%s: %s" % (type(e).__name__, str(e)[:200])})


def fenced_meanwhile(store, item, st):
    """True when the item's record moved past the lease `st` took (another gen, or no longer running)."""
    with store.lock():
        cur = store.load(item)
    return cur is None or cur["gen"] != st["gen"] or cur["status"] != "running"


def _lease(store, fx, r, now, acts, seen, wake=None):
    cfg = r.get("staffing") or {}
    launched = clones_this_tick(acts, "work")
    per_tick = cfg.get("work_launch_per_tick", cfg.get("launch_per_tick")) if cfg else None
    if float(r["share"]) <= 0:      # the off switch: nothing new starts, what runs finishes
        acts.append({"do": "wait", "why": "share 0"})
        return
    if cfg:
        waiting = sum(1 for x in store.states() if x["status"] == "candidate")
        if waiting > cfg["check_backlog_max"]:          # more builders would only lengthen the line at the checkers
            acts.append({"do": "wait", "why": "check_backlog"})
            return
    first = getattr(fx, "first", None) or {}
    refused = refusal_memo(fx)
    plan = getattr(fx, "plan", None) or {}
    pause = seen["pause"] = content_pause(fx, store.states(), refused=refused, now=now, store=store)
    seen["known"] = True
    said_reserve = said_lane = False
    no_room = None      # make_room's hold, once it said there is no room for a new clone this tick
    incidents = relentless_breakers.load(store)
    for st in queue_order(store.states(), getattr(fx, "plan", None), first):
        if wake:
            wake()
            cur = store.load(st["item"])     # the pass the wake ran may have moved this item since the order was read
            if not cur or cur["status"] != st["status"] or cur["gen"] != st["gen"]:
                continue
        inc = relentless_breakers.waits(store, st["item"], incidents)
        if inc:     # one capability incident, one probe: the rest wait for its evidence, not a tick
            acts.append({"do": "incident_wait", "item": st["item"], "key": inc})
            continue
        led = fx.item_state(st["item"])
        if relentless_block.ledger_holds(led):      # a run that ended this tick came back after the sweep looked
            relentless_block.leave_line(store, st["item"], led, now, acts, iso)
            continue
        if owner_hold(r, st["item"], first, st):
            continue
        stop = pause_stops(pause, fx, st, plan, now)
        if stop:
            # degraded: content waits, what runs finishes; the priority list is his word and still goes. Global: the line
            # stops here. Scoped: only this item's lane is paused, the next item may start
            if not st.get("not_before", 0) > now:
                seen["stopped"].append(st["item"])
            if pause.get("owner"):      # his pause holds content on purpose; a pipeline item behind it still starts
                if not said_lane:
                    said_lane = True
                    acts.append({"do": "content_paused", "item": st["item"], "why": stop})
                continue
            if pause["mode"] == "global":
                acts.append({"do": "wait", "why": "%s (%s)" % (PAUSED_WHY, stop)})
                return
            if not said_lane:       # once a tick: a long line of game-lane content would flood the acts
                said_lane = True
                acts.append({"do": "content_paused", "item": st["item"], "why": "%s (%s)" % (PAUSED_WHY, stop)})
            continue
        if not st["ledger_started"] and fx.item_state(st["item"]) is None:     # not published yet: see retire()
            continue
        if st.get("not_before", 0) > now:
            continue
        if help_pending(st):        # the next brief is the point of the consult; help_step bounds this wait
            continue
        if cfg and launched >= per_tick:   # prepare() blocks and the tick has a timeout; said, so a short belt reads why
            acts.append({"do": "wait", "why": "work clones per tick"})
            return
        if r.get("one_builder_per_mod") and hasattr(fx, "item_mods"):
            held = mods_held(store, fx, st["item"])
            taken = sorted(m for m in fx.item_mods(st) if m in held)
            if taken:       # keeps its place; the next item, on another mod, may start
                acts.append({"do": "mod_busy", "item": st["item"], "mod": taken[0], "by": held[taken[0]]})
                continue
        # a stopping item holds its place: its slot is not free for a fresh item while it returns to the top
        active = sum(1 for x in store.states() if x["status"] in RUNS_A_PLACE) + helps_running(store)
        if pause and pause["mode"] == "scoped" and st["item"] not in first and not st.get("expedite") \
                and st["item"] not in plan and not fresh_ruling(fx, st["item"], now):
            held = pause_reserve(store, pause)      # a place kept for each system item still in line
            if held and worker_cap(fx, r, 0, store) - active <= len(held):
                seen["stopped"].append(st["item"])
                if not said_reserve:
                    said_reserve = True
                    acts.append({"do": "wait", "why": "%s (%d places reserved for %s)" % (PAUSED_WHY, len(held), ", ".join(held[:5]))})
                continue
        why = admission(store, fx, r, now, active)
        if not why and not fx.clone_present(st["clone"] or fx.clone_path(st["item"], len(st["quarantined"]))):
            # no room for a NEW clone holds only the items that need one: one further down whose clone is still there
            # (its kept commits are what would free the pool) may start. Said once a tick.
            if not no_room:
                no_room = make_room(store, fx, r, now, acts, r.get("pool_check_reserve", 0))
                if no_room:
                    acts.append({"do": "wait", "why": no_room})
            if no_room:
                continue
        if why:
            acts.append({"do": "wait", "why": why})
            return
        item = st["item"]
        refusal = refused(item)
        if refusal:     # enrolled by hand, or its tree went stale in the line: it keeps its place, no worker starts
            acts.append({"do": "concept_refused", "item": item, "why": refusal})
            continue
        if st.get("needs_back"):       # the ledger still says owner: the next step() clears it first
            continue
        if pool_excluded(item, r):   # back from a stop (a snag) this tick: retire() takes it on the next
            continue
        if now < st.get("start_again_at", 0):
            continue
        reserved = False
        theirs = cfg and (fx.item_state(item) or {}).get("owner") == foreign_seat(r)
        if cfg and (theirs or st.get("foreign")):
            # also on the way back in line: the guard does not cover `queued`, so its seat may have reached it
            if theirs and not fx.foreign_fits(item):
                give_back(store, item, "no longer a kind of item the filler may take")
                acts.append({"do": "give_back", "item": item})
                continue
            reserved = reserve_foreign(store, fx, r, item, now, acts)
            if not reserved:
                continue
        if not st["ledger_started"]:
            with store.lock():      # said before the ledger hears it: a crash after `start` must not read as a seat's take
                cur = store.load(item)
                if cur["status"] != ("running" if reserved else "queued"):
                    continue
                cur["start_intent"] = True
                store.save(cur)
            why = fx.ledger_start(item)
            if why:
                if reserved:        # handed over, so it stays in line
                    give_back(store, item, "start refused", "queued", reserved=now)
                with store.lock():  # a ledger refusal is this item's, not the launcher's: it waits, the belt does not
                    cur = store.load(item)
                    cur["start_again_at"] = now + r["breaker_cool_s"]
                    cur["start_refusals"] = cur.get("start_refusals", 0) + 1
                    cur["start_refused_why"] = str(why)[:300]
                    # the same refusal again is a retry loop (53 of them on one item): held and told, never retired, which
                    # would drop work he ordered in silence. Unhold, once what refuses is fixed, gives a fresh count.
                    put_down = cur["status"] == "queued" and cur["start_refusals"] >= r.get("start_refused_put_down", 3)
                    if put_down:
                        relentless_strikes.hold(cur, "start refused %d times: %s" % (cur["start_refusals"], str(why)[:200]),
                                                "start_refused", now)
                        cur["status"] = "held"
                    store.save(cur)
                acts.append({"do": "start_refused", "item": item, "why": why})
                if put_down:
                    acts.append({"do": "start_refused_held", "item": item})
                continue
        with store.lock():
            st = store.load(item)
            if st["status"] != ("running" if reserved else "queued"):
                continue
            st.pop("reserving", None)
            st["gen"] += 1
            st["attempts"] += 1
            st["ledger_started"] = True
            st.pop("start_refusals", None)      # the count is of refusals in a row
            if not st["clone"]:
                q = len(st["quarantined"])
                st["clone"] = fx.clone_path(item, q)
            st["status"] = "running"
            st["started_at"] = now
            if st.get("live_iter"):     # the idle clock starts with this worker: the queue wait was no hold (other_active
                st["live_iter"]["bridge_seen"] = now    # skips it); OPS_RELENTLESS_GAME_HOLD_UNSTICK_DRDP read 31.6 min
            st["last_beat"] = None
            st["base"] = st.get("base") or fx.head()
            st["run"] = run_desc(store, r, unit_name("work", item, st["gen"]), now)
            st["run"]["deadline"] = now + r["run_max_s"]       # overdue()'s worker_full line, persisted for finish()
            res = st.pop("resume", None)
            if res and res.get("gen") == st["gen"] - 1 and not piloting(st):     # nothing ran between the cut and now
                st["run"]["resume"] = res["session"]
            store.save(st)
        acts.append({"do": "clone_try", "by": "work"})
        launched += 1       # the limit counts clones tried, as clones_this_tick does: a fence after prepare spent one (Codex r3)
        why = fx.prepare(st)
        if not why:
            gb = fx.mem_gb()
            acts.append({"do": "mem_after_clone", "gb": gb})
            if gb < r["min_mem_available_gb"]:      # the clone itself costs gigabytes
                why = "memory %.1f GB after the clone" % gb
            elif fx.paused():       # the pause may have come while the clone was prepared
                why = POOL_REFUSED + ": paused while the clone was prepared"
        if not why and fenced_meanwhile(store, item, st):
            # a hold (or any fence) landed while the clone was prepared outside the lock: no worker on stale state, and
            # its state is the hold's to settle, never put back to queued (Codex, ..._TEN_MORE #8)
            acts.append({"do": "lease_fenced", "item": item, "gen": st["gen"]})
            continue
        if not why:
            prompt = resume_prompt(st, "work") if st["run"].get("resume") else worker_prompt(
                st, fx.item_text(item), store.learned(item), r, store.attempts(item),
                relentless_explain.open_causes(store, getattr(fx, "state_of", None)) if st.get("diagnose_owed") else None)
            pilot = piloting(st)
            agent = r["pilot_agent"] if pilot else r["worker_agent"]
            why = fx.launch(st, st["run"], prompt, agent, st["clone"], r["run_max_s"],
                            {"RELENTLESS_ROOT": store.root, "RELENTLESS_GEN": str(st["gen"])})
        with store.lock():
            cur = store.load(item)
            if cur["gen"] != st["gen"] or cur["status"] != "running":
                # fenced during the launch: a launched unit is the `stopping` step's to stop (its run is on the record)
                acts.append({"do": "lease_fenced", "item": item, "gen": st["gen"], "launched": not why})
                continue
            if why:
                cur["gen"] += 1
                cur["status"] = "queued"
                cur["returned_at"] = cur["returned_at"] or now
                cur["run"] = None
                store.attempt(item, {"at": iso(now), "gen": cur["gen"] - 1, "end": "launch_fail", "detail": why[:300]})
                store.save(cur)
                if POOL_REFUSED not in why:
                    launch_failed(store, r, now, why)
                acts.append({"do": "launch_fail", "item": item, "why": "pool full: " + why if POOL_REFUSED in why else why})
                return
            start = {"at": iso(now), "gen": cur["gen"], "start": cur["run"]["unit"], "approach": cur["approach"]}
            if cur["run"].get("resume"):
                start["resumed"] = cur["run"]["resume"]
            if cur.get("pilot_step") and pilot:     # the sitting is this gen's: its ending (fail or finish) ends the step
                cur["pilot_step"]["sat_gen"] = cur["gen"]
                start["pilot_step"] = True
            store.attempt(item, start)
            store.save(cur)
        acts.append({"do": "lease", "item": item, "gen": st["gen"], "unit": st["run"]["unit"]})


def live_slis(store, now):
    """redesign_final 3.1: the live lane's four SLIs per load and per distinct key (relentless_live.live_slis)."""
    try:
        import relentless_live
        return relentless_live.live_slis(relentless_live.read_rows(os.path.join(store.root, "live", "runs.jsonl")), now,
                                         relentless_live.commit_time)
    except Exception as e:      # noqa: BLE001  an unread SLI is a reading that failed, never a dead tick
        return {"unread": "%s: %s" % (type(e).__name__, str(e)[:200])}


def reading(store, r, now, acts, clock=None, fx=None):
    """clock() -> the write time: `now` is the tick's start, and a stamp of that aged through the whole tick
    (RELENTLESS_TICK_TUNE_FIFTEEN_MINUTE_NAPS: files written 14:10:21Z carrying 13:55:04Z)."""
    states = store.states()
    counts = {}
    for s in states:
        counts[s["status"]] = counts.get(s["status"], 0) + 1
    br = load_breaker(store)
    rec = {"at": iso(clock() if clock else now), "share": r["share"], "counts": counts, "spent_today": spent_today(store, now),
           "breaker": br or None, "acts": acts[-20:], "circling": circling.summary(store, r, now),
           # the owner's pipeline-only switch (relentless_owner_pause.json): on, only pipeline items start
           "owner_pause": {k: op[k] for k in ("why", "prefixes")} if (op := owner_pause(fx)) else None,
           "items": [{"item": s["item"], "status": s["status"], "gen": s["gen"], "returns": s["returns"],
                      "approach": s["approach"], "spent": s["spent"]} for s in states if s["status"] in OPEN],
           # what runs, against what is put down and on what: none of the latter holds a place
           "places_live": sum(1 for s in states if s["status"] in RUNS_A_PLACE),
           "put_down": [{"item": s["item"], "status": s["status"], "on": put_down_on(s)}
                        for s in states if s["status"] in PUT_DOWN + ("candidate",)]}
    rec["live_slis"] = live_slis(store, now)
    import relentless_exam      # the exam shadow (RELENTLESS_BUILD_EXAM_BEFORE_BUILDER): returns the exam would have caught
    rec["exam_shadow"] = relentless_exam.summary(store)
    store._write(store.p("reading.json"), json.dumps(rec, indent=1, sort_keys=True))
    return rec


def hold_is_his(h):
    """Only he can lift this hold: a delegation_policy section 2 call, a flyer's flight (section 2.6), or his own look
    once every game clause has PASSed (RELENTLESS_FIX_GAME_LANE_OWNER_LOOK_FAILS). Every other hold (proof_weak,
    strikes, game, ...) is a tooling outcome, the seat's to read (RELENTLESS_HOLD_FIX_TOOLING_ISNT_OWNERS)."""
    h = h or {}
    return h.get("kind") == "owner_call" or (h.get("kind") == "game" and (
        relentless_game.flyer_hold(h.get("why")) or relentless_game.owner_look_hold(h.get("why"))))


def _hold_routed(store, item, to):
    with store.lock():
        st = store.load(item)
        if st["hold"]:
            st["hold"]["delivered"] = True
            if to:
                st["hold"]["routed"] = to
            store.save(st)


def put_down_on(st):
    """What a put-down item waits for, in words."""
    if st["status"] == "candidate":
        return "its check"
    if st["status"] == "held":
        return "%s: %s" % ("owner" if hold_is_his(st.get("hold")) else SEAT_QUEUE,
                           ((st.get("hold") or {}).get("why") or "")[:160])
    if st["status"] == "blocked":
        b = st.get("block_pending") or {}
        return "ledger block%s" % (": %s" % (b.get("detail") or "")[:160] if b else "")
    return ((st.get("put_down") or {}).get("on") or (st.get("game") or {}).get("phase") or "")[:200]


NO_ALARM = ("paused", "budget 0", "share 0")


def clean_window(store, s, fx, r, now):
    """-> None when the current stage has earned the next, else what it still lacks. The stage's own window only."""
    cfg = r["staffing"]
    since = iso(s["stage_since"])
    ends = []
    for st in store.states():
        got = [a for a in store.attempts(st["item"])
               if a.get("end") in ("done",) + REJECT_ENDS and str(a.get("at", "")) > since]
        ends += [a["end"] for a in got if a["end"] in REJECT_ENDS]
        # a crash in closing can write the same `done` twice; one sha is one pass
        ends += ["done"] * len({a.get("sha") for a in got if a["end"] == "done"})
    bad = sum(e in REJECT_ENDS for e in ends)
    if s.get("full_s", 0) < cfg["hold_s"]:
        return "held full for %d of %d s" % (s.get("full_s", 0), cfg["hold_s"])
    if len(ends) < cfg["min_verdicts"]:
        return "%d of %d verdicts" % (len(ends), cfg["min_verdicts"])
    if bad / len(ends) > cfg["max_reject_share"]:
        return "rejected %d of %d" % (bad, len(ends))
    if s["mem_min"] < r["step_back_mem_gb"]:
        return "memory touched %.1f GB" % s["mem_min"]
    if fx.budget() is None:
        return "budget unreadable"
    if fx.head_helpers() is None:
        return "head helpers unmeasured"
    if fx.oom_kills() is None:
        return "OOM count unreadable"
    b = fx.burn()
    if b is None:
        return "burn unmeasured"
    if b > cfg["burn_max_pct_h"]:
        return "burn %.2f%%/h" % b
    return None


def staffing(store, fx, r, now, acts, clock=None):
    """The no-AI filler's reading: budget, running, ready, minutes under; the staged rise; the one alarm. Its stamp is
    clock(), the write time (see reading); its own arithmetic stays on `now`."""
    cfg = r["staffing"]
    s = stage_load(store)
    if "stage_since" not in s:
        s = {"stage": 0, "stage_since": now, "full_s": 0, "mem_min": fx.mem_gb(), "oom": fx.oom_kills()}
    states = store.states()
    v, budget, head, room = stage_places(store, fx, r)
    k = sum(1 for x in states if x["status"] in RUNS_A_PLACE)
    live = sum(1 for x in states if x["status"] in ("running", "checking"))
    target = worker_cap(fx, r, 0, store)
    order, _ = fx.pool_order(r)
    ours = {x["item"] for x in states if x["status"] != "done"}     # a reopened done item is ready work, as in enrol()
    first = getattr(fx, "first", None) or {}
    # the owner's token pause (owner_hold) stops content on purpose: it is not ready, so it reads as no under-staffing
    # and so does his pipeline-only pause (owner_pause): held content is not ready work
    op = owner_pause(fx)

    def waits(i):
        return bool(op) and not owner_pipeline(op, fx, i)
    queued = sum(1 for x in states if in_line(x) and not owner_hold(r, x["item"], first, x) and not waits(x["item"]))
    ready = queued + sum(1 for i in order if i not in ours and not owner_hold(r, i, first) and not waits(i))
    stepped = 0 < target < room
    why = stuck = None
    if float(r["share"]) <= 0:
        why = "share 0"
    elif budget == 0:
        why = "budget 0"
    else:
        # whatever else stops a run, the places aside; a clone the pool cannot give stops it as surely
        stuck = next((a["why"] for a in acts if str(a.get("why", "")).startswith(POOL_FULL)), None) or admission(
            store, fx, r, now, k, extra=k + 1)   # pool first: a breaker flapping over it must not reset the jam's clock
        why = stuck
        if why is None and stepped:
            why = "memory step-back"
        elif why is None and head and room < v:
            why = "head helpers"
        elif why is None and head is None and room < v:
            why = "head helpers unmeasured"
    words_read = not foreign_seat(r) or fx.seat_words() is not None
    under = k < min(target, k + ready)
    if not words_read and k < target:       # taking fails closed; the reading must not show the pool as simply empty
        under, why = True, why or "the other seat's tree is unreadable"
    if stuck and any(x["status"] == "candidate" for x in states):   # a place held by a check that cannot start
        under = True
    dt = min(max(now - s.get("at", now), 0), cfg["tick_gap_max_s"])
    s["at"] = now
    if under:
        s["under_since"] = s.get("under_since") or now
        if why is None:
            last = [a["why"] for a in acts if a.get("do") == "wait"]
            why = last[-1] if last else "filling"
        if why not in NO_ALARM:             # minutes watched, so a stopped timer or a pause is not read as under
            s["under_s"] = s.get("under_s", 0) + dt
    else:
        s.pop("under_since", None)
        s.pop("under_s", None)
        s.pop("alarmed", None)
    minutes = round(s.get("under_s", 0) / 60.0, 1) if under else 0
    alarm_fail = None
    if under and minutes >= cfg["alarm_after_min"] and not s.get("alarmed") and why not in NO_ALARM:
        fail = fx.staffing_alarm(cfg["alarm_item"], "Under-staffed %.0f min: running %d of %d (budget %s), %d ready, "
                                 "why: %s" % (minutes, k, target, budget, ready, why))
        if fail:
            alarm_fail = fail
            acts.append({"do": "alarm_retry", "why": fail})
        else:
            s["alarmed"] = True
            store.journal({"at": iso(now), "do": "alarm", "kind": "understaffed", "minutes": minutes, "why": why})
            acts.append({"do": "alarm", "item": cfg["alarm_item"]})
    # a jam: nothing runs, or the pool refuses, while work waits. Named within minutes, in the log the Conductor reads
    pool_why = next((a["why"] for a in acts if str(a.get("why", "")).startswith(POOL_FULL)), None)
    why_jam = why if pool_why is None else pool_why
    if pool_why or (under and why not in NO_ALARM and live == 0):
        s["jam_since"] = s.get("jam_since") or now
        if now - s["jam_since"] >= cfg["jam_alarm_s"] and not s.get("jam_said"):
            fail = fx.conductor_alarm("%d live of %d wanted, %d checks waiting, %d ready, stalled %.0f min: %s" % (
                live, target, sum(1 for x in states if x["status"] == "candidate"), ready, (now - s["jam_since"]) / 60.0, why_jam))
            if fail:
                alarm_fail = fail
                acts.append({"do": "alarm_retry", "why": fail})
            else:
                s["jam_said"] = True
                store.journal({"at": iso(now), "do": "alarm", "kind": "jam", "why": why_jam})
                acts.append({"do": "jam_alarm", "why": why_jam})
    else:
        s.pop("jam_since", None)
        s.pop("jam_said", None)
    # the staged rise: each step only after a clean reading. An OOM kill anywhere on the host steps one back down
    s["mem_min"] = min([s["mem_min"], fx.mem_gb()] + [a["gb"] for a in acts if a.get("do") == "mem_after_clone"])
    if s["mem_min"] < r["step_back_mem_gb"]:        # a dip restarts the clean window; it does not end it for good
        s.update(stage_since=now, full_s=0, mem_min=fx.mem_gb(), was_full=False)
    full = k >= v and live > 0
    if full and s.get("was_full"):          # both ends full: a gap is not credited to workers launched just now
        s["full_s"] = s.get("full_s", 0) + dt
    s["was_full"] = full
    oom, top = fx.oom_kills(), len(cfg["stages"]) - 1
    moved = None
    if oom is not None and s.get("oom") is not None and oom > s["oom"]:
        moved, s["stage"] = "down: OOM kill", max(s["stage"] - 1, 0)
    elif oom is not None and s.get("oom") is None:
        moved = "restart: OOM count readable again, what it missed is unknown"
    if oom is not None:
        s["oom"] = oom
    lack = None
    if not moved and s["stage"] < top:
        lack = clean_window(store, s, fx, r, now)
        if lack is None:
            moved, s["stage"] = "up: clean reading", s["stage"] + 1
    if moved:
        s.update(stage_since=now, full_s=0, mem_min=fx.mem_gb())
        store.journal({"at": iso(now), "do": "stage", "stage": s["stage"], "why": moved})
        acts.append({"do": "stage", "stage": s["stage"], "why": moved})
    store._write(store.p("staffing_state.json"), json.dumps(s))
    cand = [x for x in states if x["status"] == "candidate"]
    written = clock() if clock else now
    rec = {"at": iso(written), "t": written, "budget": budget, "budget_measured": budget is not None, "head_helpers": head,
           "stage": cfg["stages"][s["stage"]], "target": target, "running": live, "places": k, "live": live, "ready": ready,
           "under": under, "foreign_tree_read": words_read, "alarm_fail": alarm_fail,
           "minutes_under": minutes, "why": why, "alarmed": bool(s.get("alarmed")), "rise_lacks": lack,
           "spent_today": spent_today(store, now), "day_spend_limit": r["day_spend_limit"],
           "checks": {"waiting": len(cand), "running": sum(1 for x in states if x["status"] == "checking"),
                      "oldest_wait_s": round(now - min((x.get("candidate") or {}).get("at", now) for x in cand)) if cand else 0}}
    store._write(store.p("staffing.json"), json.dumps(rec, indent=1, sort_keys=True))
    with open(store.p("staffing.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def books_alarm(store, fx, stale, now, acts, r):
    """Frozen books are a frozen engine however green its readings look: said once, and said to the Conductor."""
    path = store.p("books_stale.json")
    try:
        with open(path, encoding="utf-8") as f:
            was = json.load(f)
    except (OSError, ValueError):       # absent, or torn by a killed tick: a new count, never a dead supervisor
        was = None
    if not stale:
        if os.path.exists(path):
            os.remove(path)
        return
    was = was or {"since": now}
    acts.append({"do": "books_stale", "why": stale})
    if now - was["since"] >= ((r.get("staffing") or {}).get("jam_alarm_s") or 300) and not was.get("said"):
        was["said"] = not fx.conductor_alarm("the engine is not deploying, a push does nothing: %s" % stale)
        store.journal({"at": iso(now), "do": "alarm", "kind": "books_stale", "why": stale})
    with open(path, "w", encoding="utf-8") as f:
        json.dump(was, f)


def live_tick(store, fx, r, now, acts):
    """RA_S09_LIVE_WIRE_ONE_REAL_LEAF: start one live round when live.auto is on, none runs, and the last one began
    live.round_every_s ago. Pacing only: the round checks the game, takes the bridge with --idle-ok per proof and
    releases it at once, and refuses flyers, changed files and cut criteria (relentless_live_round.py)."""
    lr = r.get("live") or {}
    if not lr.get("auto"):
        return
    path = store.p("live_round.json")
    try:
        with open(path, encoding="utf-8") as f:
            last = json.load(f)
    except (OSError, ValueError):
        last = {}
    if last.get("pid") and fx.live_round_alive(last["pid"]):
        return
    if now - (last.get("at_s") or 0) < lr.get("round_every_s", 1800):
        return
    if relentless_game.other_active(getattr(store, "states", list)(), None) or relentless_game.showing_live(store):     # one live user at a time: a game phase has the game
        return
    pid = fx.live_round_launch()
    store._write(path, json.dumps({"pid": pid, "at_s": now, "at": iso(now)}))
    acts.append({"do": "live_round", "pid": pid})


def run_tmp_sweep(store, fx, now, acts, when):
    """Every run dir whose run is over goes (run_tmp.py): the one guarantee behind every end path, a killed engine and
    a restart included, because each tick is an engine start. A failure is journalled, never the tick's end."""
    f = getattr(fx, "sweep_run_tmp", None)
    if f is None:
        return
    try:
        out = f() or {}
    except Exception as e:  # noqa: BLE001  housekeeping never stops the belt
        acts.append({"do": "error", "item": None, "why": "run_tmp %s: %s" % (type(e).__name__, e)})
        return
    if out.get("removed") or out.get("errors"):
        store.journal({"at": iso(now), "do": "run_tmp", "when": when, "removed": out.get("removed", [])[:50],
                       "work": out.get("work", [])[:20], "errors": out.get("errors", [])[:5]})


SLOW_STEP_S = 20        # one item's step past this is named in the tick's journal row


def over_budget(r, spent):
    """The tick has spent its share on game steps -> True; rules keep this well inside the unit's kill."""
    budget = r.get("tick_game_budget_s")
    return bool(budget) and spent >= budget


GAME_WAKE = "game_wake"             # a round ended: relentless_live_round.wake_supervisor writes it, a game pass takes it
GAME_NEXT_ON = "game_next.on"       # game_next holds tick.lock: a tick waits for it instead of losing its turn
GAME_NEXT_WAIT_S = 1200             # the unit's own kill: past it the next tick serves the wake
TICK_WAITS_GAME_NEXT_S = 180
GAME_NEXT_FOLLOW_S = 90             # a pass that met a ready staging steps it again until its proof starts, this long
GAME_NEXT_FOLLOW_POLL_S = 3         # the staging unit exits seconds after its game-ready; the pass waits for it in these


def wake_taken(store):
    """-> True once per wake. Whoever takes it owes the game pass."""
    try:
        os.remove(store.p(GAME_WAKE))
        return True
    except FileNotFoundError:
        return False


def game_pass(store, fx, r, now, acts, began=None):
    """The game items' steps and nothing else, ended rounds first, until one holds the game again: what a round's end
    needs, so the next proof starts now and not at the next tick (RELENTLESS_TICK_TUNE_FIFTEEN_MINUTE_NAPS; the Conductor
    measured a proof row in 16 of 180 minutes with 35 items waiting). The caller holds tick.lock. `began`: the wall time
    the caller's game budget started at; a tick's wake spends the tick's remaining budget, never a fresh one (r5 #20)."""
    wall = getattr(fx, "wall", time.monotonic)
    began = wall() if began is None else began

    def rank(s):
        g = s.get("game") or {}
        return (g.get("phase") != "proving", not s.get("expedite"), g.get("entered_at") or 0, s["item"])

    for s in sorted((x for x in store.states() if x["status"] == relentless_game.GAME), key=rank):
        # every ended round is read before anyone starts; a staging is the holder itself, so its own step (stop, settle,
        # release) is never held back by busy: a game-ready's wake would otherwise only reach the next tick
        if (s.get("game") or {}).get("phase") not in ("proving", "staging"):
            if relentless_game.busy(store, None) or over_budget(r, wall() - began):
                break
        try:
            step(store, fx, r, s["item"], now, acts)
        except Exception as e:  # noqa: BLE001  one bad item never stops the others; the next tick resumes it
            acts.append({"do": "error", "item": s["item"], "why": "%s: %s" % (type(e).__name__, e)})
            store.journal({"at": iso(now), "do": "alarm", "kind": "step_raised", "item": s["item"], "why": str(e)[:300]})


def ready_staging(store):
    """-> the items whose staging said game-ready (or snagged) and wait only for their unit to go down."""
    return [s["item"] for s in store.states() if s["status"] == relentless_game.GAME
            and (s.get("game") or {}).get("phase") == "staging" and ((s["game"].get("ready") or s["game"].get("snag")))]


def follow_staging(store, fx, r, now, acts, wall, whole):
    """game-ready wakes this pass from inside the staging unit, so its first step only stops that unit: step again, at
    most game_next_follow_s, until the unit is down and the bridge released, then once more so the proof starts now and
    not at the next tick (STAGE_WAKE_TUNE_NAPS_AFTER_LOAD)."""
    until = wall() + r.get("game_next_follow_s", GAME_NEXT_FOLLOW_S)
    sleep = getattr(fx, "sleep", time.sleep)
    while ready_staging(store) and wall() < until:
        sleep(r.get("game_next_follow_poll_s", GAME_NEXT_FOLLOW_POLL_S))
        game_pass(store, fx, r, now + int(max(wall() - whole, 0)), acts)
        if not ready_staging(store):    # released this pass: the round it leads to starts in the next one
            game_pass(store, fx, r, now + int(max(wall() - whole, 0)), acts)
            acts.append({"do": "game_follow", "s": int(max(wall() - whole, 0))})
            return


def game_next(store=None, fx=None, r=None, now=None):
    """A round's own process calls this at its end. One holder of tick.lock at a time: under a running tick it waits, and
    that tick takes the wake between its steps; a wake the tick missed is served the moment the tick lets go. A wake with
    no spawn behind it (a killed round) is served by the next tick. It writes no reading: the tick's age stays the tick's."""
    r = r or rules()
    store = store or Store()
    if not r.get("enabled"):
        return [{"do": "disabled"}]
    with open(store.p("tick.lock"), "w") as lk:
        give_up = time.time() + GAME_NEXT_WAIT_S
        while True:
            try:
                fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                # a tick that took a game-ready's wake only stops the staging unit: wait it out and follow the staging
                if not os.path.exists(store.p(GAME_WAKE)) and not ready_staging(store):
                    return [{"do": "skip", "why": "the running tick took the wake"}]
                if time.time() >= give_up:
                    return [{"do": "skip", "why": "tick.lock busy for %d s: the next tick serves it" % GAME_NEXT_WAIT_S}]
                time.sleep(2)
        # the mark stands for the whole hold, flush included: a tick that meets the lock busy with no mark skips at once,
        # and two passes taking it down before their flush cost two ticks and 1009 s (OPS_RELENTLESS_READING_RESTORE_IUUR)
        with open(store.p(GAME_NEXT_ON), "w"):
            pass
        try:
            return _game_next_held(store, fx, r, now)
        finally:
            try:
                os.remove(store.p(GAME_NEXT_ON))
            except OSError:
                pass


def _game_next_held(store, fx, r, now):
    """game_next's body, under tick.lock and its mark."""
    if not wake_taken(store) and not ready_staging(store):
        return [{"do": "skip", "why": "no wake"}]
    if fx is None:
        os.environ["PATH"] = windows_path(os.environ.get("PATH", ""))
        fx = Effects(r, store)
        store.on_alarm = fx.alarm_signal
    now = time.time() if now is None else now
    why = relentless_integrity.due(store, fx, r, now)
    if why:     # only the tick may run the gate
        return [{"do": "skip", "why": "integrity gate due: %s" % why}]
    wall = getattr(fx, "wall", time.monotonic)
    whole, acts = wall(), []
    game_pass(store, fx, r, now, acts)
    follow_staging(store, fx, r, now, acts, wall, whole)
    why = fx.flush()        # what the steps wrote to the ledger; the next tick retries a failure
    if why:
        acts.append({"do": "flush_retry", "why": why})
    store.journal({"at": iso(now), "do": "game_next", "wall_s": int(wall() - whole), "acts": acts})
    return acts


def tick(store=None, fx=None, r=None, now=None):
    """One supervisor pass. Every child process it waits on is tallied into its journal row (relentless_tickprof)."""
    with relentless_tickprof.Tally() as prof, relentless_tickprof.Sampler() as samp:
        prof.samp = samp
        return _tick(store, fx, r, now, prof)


def _tick(store, fx, r, now, prof):
    r = r or rules()
    store = store or Store()
    now = time.time() if now is None else now
    real0 = time.time()

    def clock():
        """The write time, on the tick's own clock: a test's `now` plus what really passed, in whole seconds."""
        return now + int(max(time.time() - real0, 0))

    os.makedirs(store.dir, exist_ok=True)
    with open(store.p("tick.lock"), "w") as lk:
        waits = time.time() + r.get("tick_waits_game_next_s", TICK_WAITS_GAME_NEXT_S)
        while True:
            try:
                fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:     # a game pass is short; losing the turn to it costs the belt two more minutes
                if not os.path.exists(store.p(GAME_NEXT_ON)) or time.time() >= waits:
                    return [{"do": "skip", "why": "a tick is running"}]
                time.sleep(2)
        if fx is None:
            # the unit's PATH has no Windows tools: every game read from the tick (tasklist, netstat, powershell) and
            # every rimflow it runs measured "no game" while one ran (RELENTLESS_LIVE_REPAIR_QUITS_BEFORE_THE_LOAD)
            os.environ["PATH"] = windows_path(os.environ.get("PATH", ""))
            fx = Effects(r, store)
            store.on_alarm = fx.alarm_signal
        acts = []
        if not r.get("enabled"):
            reading(store, r, now, [{"do": "disabled"}], clock)
            return acts
        if not relentless_integrity.gate(store, fx, r, now, acts, getattr(fx, "objstore", lambda: None)()):
            try:                                # damaged state: nothing is staffed; the reading may not survive it
                reading(store, r, now, acts, clock, fx)
            except Exception as e:  # noqa: BLE001
                acts.append({"do": "error", "item": None, "why": "reading %s: %s" % (type(e).__name__, e)})
            store.journal({"at": iso(now), "do": "tick", "acts": acts})
            return acts
        wall = getattr(fx, "wall", time.monotonic)
        whole = wall()
        phases, slow, budget = {}, [], {}

        def serve_wake():
            """A round ended while this tick runs: the next proof does not wait for the rest of the tick."""
            if not wake_taken(store):
                return
            acts.append({"do": "game_wake"})
            try:
                game_pass(store, fx, r, clock(), acts, budget.get("began"))
            except Exception as e:  # noqa: BLE001  the next tick steps every game item anyway
                acts.append({"do": "error", "item": None, "why": "game_pass %s: %s" % (type(e).__name__, e)})

        def phase(name, since, wake=True):
            """Seconds this phase took, into the tick's journal row: the next slow tick names its own step. No wake is
            served after the final flush: its writes would go unflushed; game_next or the next tick takes it (r5 #21)."""
            if wake:
                serve_wake()
            at = wall()
            phases[name] = round(at - since, 1)
            return at

        books_alarm(store, fx, fx.sync(), now, acts, r)
        hand_back(store, fx, r, now, acts)       # before any check or launch of this tick: a hand check is never run
        retire(store, fx, store.states(), now, acts, r)
        relentless_block.sweep(store, fx, now, acts, iso)
        relentless_reachfix.sweep(store, fx, r, now, acts, iso)     # a blind Judge's repair: probe, apply, or ticket
        reclaim_dead(store, fx, r, now, acts)
        release_parked(store, fx, r, now, acts)
        run_tmp_sweep(store, fx, now, acts, "start")
        try:        # a detached job killed mid-run is marked lost and launched again (RELENTLESS_SHRINK_TICK_SLOW_PHASES_DETACHED)
            import relentless_jobs
            relentless_jobs.reconcile(store, acts, relentless_jobs.launcher(store, "mods_fp"))
        except Exception as e:  # noqa: BLE001  a torn job table costs a fresh answer, never the tick
            acts.append({"do": "error", "item": None, "why": "jobs reconcile %s: %s" % (type(e).__name__, e)})
        try:        # a holder that no longer uses the game frees it before anyone asks for it this tick
            relentless_game.lapse_holds(store, fx, r, now, acts)
        except Exception as e:  # noqa: BLE001  a failed read keeps the holds as they are; the steps still run
            acts.append({"do": "error", "item": None, "why": "lapse_holds %s: %s" % (type(e).__name__, e)})
            store.journal({"at": iso(now), "do": "alarm", "kind": "lapse_holds_raised", "why": str(e)[:300]})
        try:        # a returned stale build that carries now goes back to its game step before a worker is sent for it
            relentless_game.recarry_returned(store, fx, now, acts)
        except Exception as e:  # noqa: BLE001  a failed git read leaves the item queued, as before
            acts.append({"do": "error", "item": None, "why": "recarry_returned %s: %s" % (type(e).__name__, e)})
        began, skipped = phase("prelude", whole), 0
        budget["began"] = began     # the step loop's game budget: a wake in it spends what is left
        for final in (False, True):       # the second pass lets a return that ended this tick reach the top now
            for item in store.items():
                if final and (store.load(item) or {}).get("status") != "stopping":
                    continue
                # a game step can plan deploys over the Windows mount for minutes; a tick the unit kills never reaches
                # lease or flush, so it staffs nothing and says nothing. Game items wait for the next tick instead
                if over_budget(r, wall() - began) and (store.load(item) or {}).get("status") == "game":
                    skipped += 1
                    continue
                one = wall()
                try:
                    step(store, fx, r, item, now, acts)
                except Exception as e:  # noqa: BLE001  one bad item never stops the others; next tick resumes it
                    acts.append({"do": "error", "item": item, "why": "%s: %s" % (type(e).__name__, e)})
                    store.journal({"at": iso(now), "do": "alarm", "kind": "step_raised", "item": item,
                                   "why": str(e)[:300]})
                if wall() - one >= SLOW_STEP_S:
                    slow.append({"item": item, "s": round(wall() - one, 1)})
                serve_wake()
        if skipped:
            acts.append({"do": "tick_budget", "skipped": skipped, "after_s": int(wall() - began)})
        at = phase("steps", began)
        for item in store.items():
            try:
                help_step(store, fx, r, item, now, acts)
            except Exception as e:  # noqa: BLE001  a consult is an extra: it never costs the tick its workers
                acts.append({"do": "error", "item": item, "why": "help %s: %s" % (type(e).__name__, e)})
                store.journal({"at": iso(now), "do": "alarm", "kind": "help_raised", "item": item, "why": str(e)[:300]})
        try:
            circling.watch(store, fx, r, now, acts, fail)
        except Exception as e:  # noqa: BLE001  the watch never stops the belt
            acts.append({"do": "error", "item": None, "why": "circling %s: %s" % (type(e).__name__, e)})
        reap_quarantined(store, fx, r, now, acts)
        charge_dead_runs(store, fx, r, now, acts)
        try:
            relentless_disk.reap_boxes(store, r, now, getattr(fx, "box_in_use", lambda b: True), acts)
        except Exception as e:  # noqa: BLE001  disk housekeeping never stops the belt
            acts.append({"do": "error", "item": None, "why": "reap_boxes %s: %s" % (type(e).__name__, e)})
        try:
            relentless_disk.reap_bundles(store, r, now, acts)
        except Exception as e:  # noqa: BLE001  disk housekeeping never stops the belt
            acts.append({"do": "error", "item": None, "why": "reap_bundles %s: %s" % (type(e).__name__, e)})
        spend_holds(store, fx, r, now, acts)
        at = phase("after_steps", at)
        try:        # before the order is read; a broken log costs the lane, never the tick
            relentless_expedite.sync(store, fx, now, acts)
        except Exception as e:  # noqa: BLE001
            acts.append({"do": "error", "item": None, "why": "expedite %s: %s" % (type(e).__name__, e)})
            store.journal({"at": iso(now), "do": "alarm", "kind": "expedite_raised", "why": str(e)[:300]})
        enrol_acts = enrol(store, fx, r, now)
        acts += [{"do": "enrol", "item": i} for i in enrol_acts]
        h = getattr(fx, "_health", None)
        if h:       # what Relentless obeyed this tick; a missing or stale verdict is said here (Operations raises it)
            acts.append({"do": "health", "fresh": h["fresh"], "degraded": h["degraded"], "first": len(h["first"]),
                         "unmeasured": bool(h.get("unmeasured")), "pause": h.get("pause"),
                         "why": h["why"][:300]})
        try:        # after enrol, which reads the verdict the choice of victim needs
            active = sum(1 for x in store.states() if x["status"] in RUNS_A_PLACE) + helps_running(store)
            relentless_expedite.make_room(store, fx, r, now, acts, active, admission(store, fx, r, now, active), fail)
        except Exception as e:  # noqa: BLE001
            acts.append({"do": "error", "item": None, "why": "expedite interrupt %s: %s" % (type(e).__name__, e)})
            store.journal({"at": iso(now), "do": "alarm", "kind": "expedite_raised", "why": str(e)[:300]})
        try:        # after enrol, which sets this tick's plan; a broken reading costs the page its list, never the tick
            write_queue_next(store, fx, r, now)
        except Exception as e:  # noqa: BLE001
            acts.append({"do": "error", "item": None, "why": "queue_next %s: %s" % (type(e).__name__, e)})
        try:
            launch_proved(store, now)
            lease(store, fx, r, now, acts, wake=serve_wake)
        except Exception as e:  # noqa: BLE001  a hung rimflow must not lose the tick's flush; a reservation resumes next tick
            acts.append({"do": "error", "item": None, "why": "lease %s: %s" % (type(e).__name__, e)})
            store.journal({"at": iso(now), "do": "alarm", "kind": "lease_raised", "why": str(e)[:300]})
        try:
            breaker_emergency(store, fx, r, now, acts)
        except Exception as e:  # noqa: BLE001  a torn cause record must not lose the tick's flush
            acts.append({"do": "error", "item": None, "why": "breaker_emergency %s: %s" % (type(e).__name__, e)})
        try:
            relentless_breakers.tell(store, fx, now, acts)
        except Exception as e:  # noqa: BLE001
            acts.append({"do": "error", "item": None, "why": "incident tell %s: %s" % (type(e).__name__, e)})
        at = phase("enrol_lease", at)
        if r.get("staffing"):
            try:
                staffing(store, fx, r, now, acts, clock)
            except Exception as e:  # noqa: BLE001  the reading never stops the workers; a dead reading shows as stale
                acts.append({"do": "error", "item": None, "why": "staffing %s: %s" % (type(e).__name__, e)})
        try:
            live_tick(store, fx, r, now, acts)
        except Exception as e:  # noqa: BLE001  the live tier is an extra: it never costs the tick its flush
            acts.append({"do": "error", "item": None, "why": "live_tick %s: %s" % (type(e).__name__, e)})
        try:        # OWNER_REVIEW_BUILD_SHOWS_READY_BEFORE_ASKED: what waits on his look is staged before he is asked
            relentless_showing.tick(store, fx, r, now, acts, sys.modules[__name__])
        except Exception as e:  # noqa: BLE001  the showing stage never costs the tick its flush
            acts.append({"do": "error", "item": None, "why": "showings %s: %s" % (type(e).__name__, e)})
            store.journal({"at": iso(now), "do": "alarm", "kind": "showings_raised", "why": str(e)[:300]})
        run_tmp_sweep(store, fx, now, acts, "end")
        at = phase("staffing_live", at)
        why = fx.flush()
        if why:
            acts.append({"do": "flush_retry", "why": why})
        phase("flush", at, wake=False)
        reading(store, r, now, acts, clock, fx)
        if acts:
            store.journal({"at": iso(now), "do": "tick", "wall_s": int(wall() - whole), "phases": phases,
                           "slow_steps": sorted(slow, key=lambda x: -x["s"])[:5], "proc_s": prof.total(),
                           "proc": prof.top(), "py_calls": _samp_top(prof, "calls"),
                           "py_leaves": _samp_top(prof, "leaves"), "acts": acts})
        relentless_integrity.mark_clean(store, fx, now)
        return acts


def _samp_top(prof, which):
    samp = getattr(prof, "samp", None)
    return samp.top(which) if samp else []


def stats(store, fx=None):
    done = [s for s in store.states() if s["status"] == "done"]
    days = {}
    for s in done:
        d = day_key(s["done_at"])
        days[d] = days.get(d, 0) + 1
    rows = [{"day": d, "relentless_closed": n} for d, n in sorted(days.items())]
    return {"done": len(done), "by_day": rows, "mean_returns": (sum(s["returns"] for s in done) / len(done)) if done
            else None, "spent": sum(s["spent"] for s in done)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("tick")
    sub.add_parser("game-next")
    sub.add_parser("reading")
    sub.add_parser("stats")
    sub.add_parser("fence-hook")
    p = sub.add_parser("show")
    p.add_argument("item")
    p = sub.add_parser("boxrun", help="run the item's contract proof in the Marker's box at a commit (default HEAD)")
    p.add_argument("--item")
    p.add_argument("--gen", type=int)
    p.add_argument("--sha", default="HEAD")
    p.add_argument("--sli", action="store_true", help="print the boxrun verdict counts by kind/mode instead")
    relentless_dispute.add_parser(sub)
    for name in ("beat", "learn", "contract", "rebind", "snag", "finish"):
        p = sub.add_parser(name)
        p.add_argument("--item", required=True)
        p.add_argument("--gen", required=True, type=int)
        if name in ("learn", "snag"):
            p.add_argument("text")
        if name in ("contract", "rebind"):
            p.add_argument("--obligation", help="what must be true, in the item's words; only a redesign changes it")
            p.add_argument("--scenario", help="the binding's scenario: where and on what the proof is run")
            p.add_argument("--fixture", dest="fixtures", action="append", help="a fixture the proof reads (repeatable)")
            p.add_argument("--freshness", help="how fresh its evidence must be, e.g. 'same sha' or 'max_age=6h'")
        if name == "rebind":
            p.add_argument("--proof", help="the new proof; left out, the old one is kept")
            p.add_argument("--before", required=True, help="what the old binding measured")
            p.add_argument("--after", required=True, help="what the new binding measures")
            p.add_argument("--behaviour", required=True, help="'same' when no acceptable behaviour changes; else refused")
            p.add_argument("--defect", required=True, help="the evidence that the old binding is broken")
            p.add_argument("--live")
            p.add_argument("--game")
            p.add_argument("--game-why")
            p.add_argument("--no-offline")
            p.add_argument("--offbox", action="append")
            p.add_argument("--reach-ok", dest="reach_ok")
        if name == "contract":
            p.add_argument("--proof", required=True)
            p.add_argument("--live")
            p.add_argument("--game", help="criterion ids only the running game can show, e.g. A2,B3 (relentless_game)")
            p.add_argument("--game-why", help="why only the running game can show them")
            p.add_argument("--no-offline", help="why no offline proof is possible at all")
            p.add_argument("--offbox", action="append", help="an adapter NAME from relentless_rules.json offbox_adapters, which "
                           "the supervisor runs outside the Marker's wall at check time, its raw output and exit handed in: "
                           "for evidence the box cannot reach (repeatable). Never a command")
            p.add_argument("--reach-ok", dest="reach_ok", help="why the walled Marker can still show a proof that names "
                           "what its box hides (a masked path, git history, ssh, a Windows program); without it or --offbox "
                           "such a proof is refused")
            p.add_argument("--why")
        if name == "snag":
            p.add_argument("--class", dest="klass", required=True)
            p.add_argument("--section")
            p.add_argument("--wait-hours", type=float, default=0, help="time, not work: no worker before then (at most %g)" % MAX_WAIT_HOURS)
            p.add_argument("--on", action="append", help="a predecessor item it waits on (repeatable): a ledger block, out of the line")
            p.add_argument("--blocker", choices=relentless_block.KINDS, help="what it waits on, if not an item: owner, judge, live, external")
        if name == "finish":
            p.add_argument("--sha", required=True)
            p.add_argument("--evidence", required=True)
    p = sub.add_parser("bind-judge", help="the independent Setter/Judge's ruling on a pending binding repair "
                       "(relentless_binding); --packet prints what to compare")
    p.add_argument("--item", required=True)
    p.add_argument("--as", dest="judge")
    p.add_argument("--verdict", choices=relentless_binding.VERDICTS)
    p.add_argument("--why")
    p.add_argument("--packet", action="store_true")
    p = sub.add_parser("explain", help="the written explanation of the last ending (relentless_explain): expected, observed, "
                                       "mechanism, evidence per step, theories ruled out, and the open follow-up item")
    p.add_argument("--item", required=True)
    p.add_argument("--gen", required=True, type=int)
    p.add_argument("--class", dest="klass", required=True, help="|".join(relentless_explain.CLASSES))
    p.add_argument("--expected", required=True, help="what the proof expected to read")
    p.add_argument("--observed", required=True, help="what the game or the checker actually did")
    p.add_argument("--mechanism", required=True, help="how the one led to the other")
    p.add_argument("--step", action="append", required=True, help="claim :: the evidence that shows it (repeatable)")
    p.add_argument("--ruled-out", action="append", required=True, help="theory :: the reading that kills it (repeatable)")
    p.add_argument("--cause", required=True, help="the OPEN follow-up item for this cause (this item for MOD/CONTRACT)")
    p = sub.add_parser("causes", help="the cause book: open follow-up items failures were explained by, and their items")
    p = sub.add_parser("game-ready", help="the staging worker: the game runs the build; the supervisor reruns the proofs")
    p.add_argument("--item", required=True)
    p.add_argument("--gen", required=True, type=int)
    p.add_argument("text", nargs="?", default="")
    p = sub.add_parser("reload-needed", help="a live-iterating worker: the proof that only a rebuild+reload goes further")
    p.add_argument("--item", required=True)
    p.add_argument("--gen", required=True, type=int)
    p.add_argument("text")
    p = sub.add_parser("help", help="send a fresh agent the failed approaches; its options reach the next brief")
    p.add_argument("--item", required=True)
    p.add_argument("--gen", type=int, help="your lease; default RELENTLESS_GEN, set at launch")
    p.add_argument("text", nargs="?", default="")
    p = sub.add_parser("help-vendor", help="round two's unit body: ask gpt_consult, answer with its OPTION lines")
    p.add_argument("--item", required=True)
    p.add_argument("--prompt-file", required=True)
    p = sub.add_parser("help-answer", help="the consult's return")
    p.add_argument("--item", required=True)
    p.add_argument("--nonce", required=True)
    p.add_argument("--option", action="append", required=True, help="idea | the one observation that confirms or kills it")
    p = sub.add_parser("attribute", help="the diagnosis of a validation ending (relentless_attrib): PRODUCT goes to a "
                                         "builder, PROOF/CONTRACT to the proof road, HARNESS/SITE/CHECKER to an incident, "
                                         "DEPENDENCY to its predecessor; the candidate is kept")
    p.add_argument("--item", required=True)
    p.add_argument("--nonce", help="the diagnostic consult's; without it, --seat (a person or the seat attributing a hold)")
    p.add_argument("--seat", action="store_true", help="attribute as the seat, no consult nonce")
    p.add_argument("--target", action="append", required=True, help="|".join(relentless_attrib.TARGETS) + " (repeatable)")
    p.add_argument("--evidence", required=True)
    for k in ("obligation", "observed", "why-product", "repair", "component", "fixture-good", "fixture-bad", "on",
              "expected", "mechanism"):
        p.add_argument("--" + k)
    p.add_argument("--step", action="append", help="claim :: the evidence that shows it (repeatable; at least one)")
    p.add_argument("--ruled-out", action="append", help="theory :: the reading that kills it (repeatable; at least one)")
    p = sub.add_parser("incidents", help="ONE book of open incidents: capability (incidents.json) and instrument "
                                         "(instrument_incidents.json), the same fault in both as one row")
    p.add_argument("--json", action="store_true")
    p.add_argument("--all", action="store_true", help="released and still-counting ones too")
    p = sub.add_parser("incident-release", help="an operator's repair of a capability incident, with its evidence")
    p.add_argument("--key", required=True)
    p.add_argument("--evidence", required=True)
    sub.add_parser("wall", help="report only: what the Marker's wall would deny, from the checks' tool calls")
    p = sub.add_parser("hand-checks", help="the open items the hand_check rule keeps out of the pipeline (owner "
                                           "2026-11-05); --lint checks the rule, --bounce notes each one to its maker once")
    p.add_argument("--lint", action="store_true")
    p.add_argument("--bounce", action="store_true")
    p = sub.add_parser("trust")
    p.add_argument("--set", default="E1")
    p.add_argument("--arm", help="read results_<arm>, a changed Marker's run of the same set")
    p.add_argument("--against-step0", action="store_true",
                   help="step 3: the arm beside step 0's unwalled results, per class and paired (needs --arm)")
    sub.add_parser("shadow", help="report only: live verdicts beside what the narrower WEAK would have said")
    p = sub.add_parser("verdict")
    p.add_argument("--item", required=True)
    p.add_argument("--nonce", required=True)
    p.add_argument("word")
    p.add_argument("reasons")
    p.add_argument("--defect", action="append", default=None, help="one wrong thing your own run showed (repeatable); any makes it FAIL")
    p.add_argument("--unreached", action="append", default=None, help="one piece of evidence you could not reach (repeatable)")
    p.add_argument("--control", action="append", default=None,
                   help="how your instrument showed it can see (repeatable); a product: defect needs one")
    p = sub.add_parser("enrol", help="carry one named item, ahead of the share's next picks")
    p.add_argument("--item", required=True)
    p.add_argument("--why", required=True)
    p = sub.add_parser("expedite", help="the escalation route: Operations or the Conductor only; 4 h unless renewed")
    p.add_argument("verb", choices=["set", "renew", "clear", "list"])
    p.add_argument("item", nargs="?")
    p.add_argument("--level", choices=relentless_expedite.LEVELS, help="interrupt: very rare, an imminent threat to machine "
                   "safety or a panicked owner; may stop running work. expedited: the next available place")
    p.add_argument("--by", choices=relentless_expedite.SETTERS)
    p.add_argument("--why")
    p = sub.add_parser("reenrol", help="put a retired item, or a done one the ledger reopened, back in line; journals why")
    p.add_argument("--item", required=True)
    p.add_argument("--why", required=True)
    p = sub.add_parser("rediagnose", help="an attribution hold whose diagnostic consult failed: run the consult again "
                       "(unhold only re-checks the same sha)")
    p.add_argument("item")
    p.add_argument("--owner-said")
    p.add_argument("--per-ruling", help="with --why: a Conductor instruction (conductor_authority.RULING)")
    p.add_argument("--why")
    p = sub.add_parser("hold", help="take an item out of the line until unhold: no worker, no re-check; a candidate "
                       "keeps its sha and unhold checks it again; a running worker is fenced")
    p.add_argument("item")
    p.add_argument("--owner-said")
    p.add_argument("--per-ruling", help="with --why: a Conductor instruction (conductor_authority.RULING)")
    p.add_argument("--why")
    p = sub.add_parser("unhold")
    p.add_argument("item")
    p.add_argument("--owner-said")
    p.add_argument("--per-ruling", help="with --why: a Conductor instruction (conductor_authority.RULING)")
    p.add_argument("--why")
    p.add_argument("--offbox", action="append", help="an unmeasured hold's repair: an adapter NAME from relentless_rules.json "
                   "offbox_adapters, run by the supervisor outside the Marker's wall at check time, added to the contract (repeatable)")
    a = ap.parse_args(argv)
    store = Store()
    try:
        if a.cmd in ("tick", "game-next"):
            own = None
            try:        # the tick's own children (git, rimflow, gh) write their temp files here, not in /tmp
                own = run_tmp.pid_name(a.cmd)
                os.environ.update(run_tmp.env(run_tmp.prepare(own)))
            except OSError:
                own = None
            try:
                print(json.dumps(tick(store) if a.cmd == "tick" else game_next(store)))
            finally:
                if own:
                    try:
                        run_tmp.drop(own, mine=True)
                    except Exception:  # noqa: BLE001  the next tick's sweep takes it
                        pass
        elif a.cmd == "reading":
            print(open(store.p("reading.json"), encoding="utf-8").read())
            import relentless_live      # the SLIs read now, not at the last tick
            print("\n".join(relentless_live.sli_lines(live_slis(store, time.time()))))
        elif a.cmd == "stats":
            print(json.dumps(stats(store), indent=1))
        elif a.cmd == "show":
            print(json.dumps(store.load(a.item), indent=1))
        elif a.cmd == "fence-hook":
            top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
            why = hook_fence(top, store)
            if why:
                print("RELENTLESS_FENCE: %s" % why, file=sys.stderr)
                return 1
        elif a.cmd == "beat":
            beat(store, a.item, a.gen)
        elif a.cmd == "explain":
            fx = Effects(rules(), store)
            print("relentless: %s explained; follow-up %s" % (a.item, explain(
                store, a.item, a.gen, a.klass, vars(a), state_of=ledger_state, note=fx.ledger_note)))
        elif a.cmd == "causes":
            print("\n".join(relentless_explain.open_causes(store, ledger_state, limit=200)) or "no open causes on the book")
        elif a.cmd == "learn":
            learn(store, a.item, a.gen, a.text)
        elif a.cmd == "contract":
            contract(store, a.item, a.gen, a.proof, a.live, a.why,
                     game=relentless_game.parse_game(a.game, a.game_why, a.no_offline), offbox=a.offbox, reach_ok=a.reach_ok,
                     obligation=a.obligation, scenario=a.scenario, fixtures=a.fixtures, freshness=a.freshness)
        elif a.cmd == "rebind":
            game = relentless_game.parse_game(a.game, a.game_why, a.no_offline) if a.game else None
            print(rebind(store, a.item, a.gen, {"proof": a.proof, "live": a.live, "game": game, "offbox": a.offbox,
                                                "reach_ok": a.reach_ok, "scenario": a.scenario, "fixtures": a.fixtures,
                                                "freshness": a.freshness},
                         {"before": a.before, "after": a.after, "behaviour": a.behaviour, "defect": a.defect},
                         obligation=a.obligation))
        elif a.cmd == "bind-judge":
            if a.packet:
                st = store.load(a.item)
                if not st or not st.get("binding_proposal"):
                    raise ValueError("%s has no binding repair waiting" % a.item)
                print(relentless_binding.packet(st))
            else:
                if not a.verdict:
                    raise ValueError("--verdict approve|reject|ambiguous (or --packet)")
                print(bind_judge(store, a.item, a.judge, a.verdict, a.why))
        elif a.cmd == "game-ready":
            relentless_game.ready(store, a.item, a.gen, a.text)
            import relentless_live_round     # the round's own wake path: the proof starts now, not at the next tick
            relentless_live_round.wake_supervisor(store.root)
        elif a.cmd == "reload-needed":
            reload_needed(store, a.item, a.gen, a.text)
        elif a.cmd == "snag":
            snag(store, a.item, a.gen, a.klass, a.text, rules(), a.section, wait_hours=a.wait_hours, on=a.on, blocker=a.blocker)
        elif a.cmd == "boxrun":
            if a.sli or not a.item:
                print(json.dumps(relentless_boxrun.sli(store), indent=1, sort_keys=True))
                return 0
            try:                                    # an answer that landed after the challenge call (WP-08);
                relentless_dispute.deliver(store, a.item, a.gen)    # never lets a dispute fault stop the box run
            except Exception as e:  # noqa: BLE001
                print("relentless challenge: delivery failed (%s); `challenge --status` retries" % e)
            return relentless_boxrun.verb(store, a.item, a.gen, canonical_commit(a.sha), os.getcwd(), rules())
        elif a.cmd == "challenge":
            return relentless_dispute.verb(store, a)
        elif a.cmd == "finish":
            sha = canonical_commit(a.sha)
            sha, moved = landed_commit(sha)
            if moved:
                print("relentless: " + moved, file=sys.stderr)
            hidden = ledger_only_refusal(sha, rules().get("walls", {}).get("marker", {}))
            if hidden:
                raise ValueError(hidden)
            finish(store, a.item, a.gen, sha, a.evidence)
        elif a.cmd == "help":
            env_gen = os.environ.get("RELENTLESS_GEN")
            gen = a.gen if a.gen is not None else int(env_gen) if env_gen else None
            ask_help(store, a.item, gen, a.text, rules())
        elif a.cmd == "help-vendor":
            return help_vendor_run(store, a.item, a.prompt_file, rules())
        elif a.cmd == "help-answer":
            help_answer(store, a.item, a.nonce, a.option, rules())
        elif a.cmd == "attribute":
            if bool(a.nonce) == bool(a.seat):
                raise ValueError("give --nonce (the diagnostic consult) or --seat (a person), one of them")
            fx = Effects(rules(), store)
            store.on_alarm = fx.alarm_signal
            print("relentless: %s -> %s" % (a.item, relentless_attrib.answer(
                store, a.item, a.nonce, a.target, vars(a), rules(), time.time(), sys.modules[__name__],
                known=ledger_has, root=fx.books if os.path.isdir(fx.books) else None, note=fx.ledger_note,
                state_of=ledger_state)))
        elif a.cmd == "incidents":
            import relentless_incident
            rows = relentless_incident.book(store, everything=a.all)
            print(json.dumps(rows, indent=1) if a.json else relentless_incident.book_text(rows))
        elif a.cmd == "incident-release":
            inc = relentless_breakers.release_by_hand(store, a.key, a.evidence, time.time())
            print("released %s (%d items back in line)" % (a.key, len(inc.get("items") or {})))
        elif a.cmd == "enrol":
            if not ledger_has(a.item):
                print("relentless: REFUSED: %s has never been filed" % a.item, file=sys.stderr)
                return 2
            filed = [e.get("kind") for e in pkg("model").read() if e.get("id") == a.item and e.get("event") == "file"]
            refusal = concept_refused(pkg("concept_tree").REPO, a.item, filed[-1] if filed else None)
            if refusal:
                print("relentless: REFUSED: %s" % refusal, file=sys.stderr)
                return 2
            st = enrol_one(Store(), a.item, a.why, time.time())
            print("%s %s" % (a.item, st["status"]))
        elif a.cmd == "expedite":
            return expedite_cli(a, Store(), time.time(), rules())
        elif a.cmd == "reenrol":
            why = done_still_closed(Store().load(a.item), ledger_state(a.item))
            if why:
                raise ValueError(why)
            st = reenrol(Store(), a.item, a.why, time.time())
            print("%s %s gen %d" % (a.item, st["status"], st["gen"]))
        elif a.cmd == "hand-checks":
            return hand_checks_cli(rules(), lint=a.lint, bounce=a.bounce)
        elif a.cmd == "wall":
            import relentless_seeds

            def session(run):
                try:
                    with open((run or {}).get("out") or "", encoding="utf-8") as f:
                        return json.load(f).get("session_id")
                except (OSError, ValueError):
                    return None
            print(json.dumps(relentless_wall.audit(store, rules(), session, relentless_seeds.tool_inputs), indent=1))
        elif a.cmd == "trust":
            import relentless_trust
            if a.against_step0:
                if not a.arm:
                    raise SystemExit("--against-step0 compares an arm with step 0: name the arm")
                print(relentless_trust.compare_report(set_name=a.set, arm=a.arm)[1], end="")
            else:
                print(relentless_trust.report(store, set_name=a.set, arm=a.arm)[1], end="")
        elif a.cmd == "shadow":
            print(json.dumps(shadow_tally(store), indent=1))
        elif a.cmd == "verdict":
            verdict(store, a.item, a.nonce, a.word, a.reasons, defects=a.defect, unreached=a.unreached, controls=a.control)
        elif a.cmd == "rediagnose":
            said = _conductor_authority().words(a.owner_said, a.per_ruling, a.why)
            if not said:
                raise ValueError("rediagnose needs --owner-said or " + _conductor_authority().ROUTE)
            rediagnose(store, a.item, said)
            print("%s: a diagnostic consult is wanted again" % a.item)
        elif a.cmd == "hold":
            said = _conductor_authority().words(a.owner_said, a.per_ruling, a.why)
            if not said:
                raise ValueError("hold needs --owner-said or " + _conductor_authority().ROUTE)
            was = hold(store, a.item, said)
            print("%s: held (was %s)%s" % (a.item, was, "; its worker is fenced and settles to held"
                                           if was == "running" else ""))
        elif a.cmd == "unhold":
            said = _conductor_authority().words(a.owner_said, a.per_ruling, a.why)
            if not said:
                raise ValueError("unhold needs --owner-said or " + _conductor_authority().ROUTE)
            unhold(store, a.item, said, offbox=a.offbox)
    except Fenced as e:
        print("FENCED: %s" % e, file=sys.stderr)
        return FENCED
    except ValueError as e:
        print("refused: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    sys.exit(main())
