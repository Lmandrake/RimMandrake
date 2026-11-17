#!/usr/bin/env python3
"""maturation_dispatch.py: the Dispatch step of the Maturation Pipeline. It launches capped offline builders for the
advancing mods that stand at the offline build with build work owed, and nothing else. No model, no tokens of its own.

Item RIMMANDRAKE_WIRE_DISPATCH_TO_LAUNCH_BUILDERS_MODS_SAT_IDLE. The owner, 2026-11-14 ~9 PM PST, at the keyboard: "So can
we wire up Operations/Dispatch such that they do advance on these offline builders? This was pretty inefficient and
pointlessly it seems, if I'm reading correctly. As long as we don't have automated loops rejecting/cycling things, we
can't get into too much trouble." (Measured that evening: all four advancing mods sat at Stage 3 for 6 to 9 hours with
no builder on them, because every launch was a Conductor hand step.)

    python3 src/RimMandrake/rimflow/maturation_dispatch.py tick [--apply] [--no-page]
            one pass: decide per mod, launch (only with --apply), write the reading, regenerate MATURATION_NOW
    python3 src/RimMandrake/rimflow/maturation_dispatch.py status        the last reading, one line per mod
    python3 src/RimMandrake/rimflow/maturation_dispatch.py clear MOD --why "..."
            the Conductor lifts a stop on MOD (the next tick may launch on it once)
    python3 src/RimMandrake/rimflow/maturation_dispatch.py releases      every release: spend, amount, why, spent or not
    python3 src/RimMandrake/rimflow/maturation_dispatch.py release MOD --stage STAGE --read-usd X --usd R --why "..."
            the Conductor releases MOD past the ceiling at STAGE by USD R, having read USD X spent there: one more
            launch, then the mod pauses at the next ceiling (item RIMMANDRAKE_RELEASE_STAGE_CEILING_PER_MOD_ONLY_GLOBAL_KNOB)

Runs on rm-maturation-dispatch.timer (every 60 s, from the dispatch clone); its own timer, not the Dispatcher's tick,
so a slow ledger read never cuts a Dispatcher beat. Settings: maturation_dispatch.json beside this file.

Per mod on the advancing list, in order, one decision:
  not_offline   the mod's record is at neither the offline build nor the blind challenge (no record, the Designer, any
                later stage): nothing; the Designer stays his and the stages after the blind challenge are hand steps
  live          a detached run is live on the mod (maturation_now maps runs to mods by item id): nothing; the run is
                watched, and its refused count when first seen is kept
  stopped       the last run on the mod ended and the count of refused bars did NOT fall, or the mod's dollars at the
                stage passed stage_ceiling_usd, or a launch failed (one that never started on a transient fault is
                launch_retry instead, the same item, up to launch_tries): nothing, and one "Needs Conductor" line. It stays
                stopped while the refused set is the one it stopped on (never a second automatic try at the same
                refusals); `clear` or a change to the refused set by someone else lifts it
  held | blocked a Conductor hold or another non-build refusal (a version mismatch): nothing
  hand_step     only hand steps are left (a steward confirmation): a "Needs Conductor" line
  ready         every exit test passes: "ready to advance" for the Conductor; the program never advances
  blind         the run records or the test table cannot be read: nothing (never launch on a blind reading)
  no_cap        the settings have no positive cap_usd: nothing launches anywhere
  slots_unknown an advancing mod's live runs cannot be read: no launch anywhere (an unknown occupancy is never 0)
  ceiling       blind or in-game: the stage's dollars plus the run's cap pass stage_ceiling_usd (the cap is reserved)
                and no unspent release fits (below)
Ceiling releases (item RIMMANDRAKE_RELEASE_STAGE_CEILING_PER_MOD_ONLY_GLOBAL_KNOB; the owner by card 2026-11-15: the
Conductor may release a stopped mod without asking, each release in his daily digest with the spend). `release` appends
one record to <state dir>/releases.jsonl: mod, stage, who (--by, else the seat), the spend read, the dollars released,
why. At that mod and stage a record lets ONE launch past the ceiling when the spend it read is still the spend (within
READ_SLACK) and the spend plus the run's cap fits the ceiling plus the release; the launch spends it (state
releases_used), so the next tick pauses at the ceiling again. Another mod's or stage's record, a spent one, a stale read
or a malformed line releases nothing; every ceiling pause names the release command that would lift it.
delegated_digest.py reads the same file (source "release": mod, stage and who; its page is token-blind, so the dollars
and the why are listed by `releases`, not printed there).
The Conductor's hand judgements of 2026-11-13 to 11-15, applied by the tick (census:
design/RimMandrake/pipeline_interventions_census_2026-11-15.md; selftest_maturation_hands.py):
  no stop       a run first seen with 0 refused bars had no build work to resolve and is never judged as a builder; a stop
                written on an empty refused set lifts itself (RIMMANDRAKE_SKIP_BUILDER_STOP_ON_ZERO_REFUSED_BARS)
  code retry    a launch that failed on a defect (not a transient fault) records the pipeline code it failed on
                (pipeline_code: the git tree of src/RimMandrake/rimflow at this clone's HEAD) and is tried again once
                that code changes, within launch_tries: at Stage 3 the stop lifts, a blind, in-game, steward or fixer
                entry is retriable (RIMMANDRAKE_RETRY_FAILED_LAUNCH_ONCE_CODE_CHANGES)
  refund        a blind or in-game run KILLED from outside keeps its dollars charged to the stage; when those dollars
                alone hold its own retry at the ceiling, the tick gives back what is missing, once per killed run, never
                while the stage reads DIVERGING, as a release record marked auto (by RUNNER, a delegated call the daily
                digest reads). Every other release stays the Conductor's (RIMMANDRAKE_REFUND_KILLED_RUN_DOLLARS_AT_THE_CEILING)
  slow chores   every 30 min: `detached_helper.py backfill-cost --apply`, and finish and return a run on an advancing mod
                dead 10 min with its finish never run (RIMMANDRAKE_SWEEP_RUN_DOLLARS_AND_DEAD_RUNS_ON_TICK)
  hand acts     maturation_hands.observe records every hand act on the pipeline; the reading's hand_acts block counts
                the ones with no follow-up, and one open a day is a Needs Conductor line and the alarm
                OPS_MATURATION_HAND_ACT_UNFOLDED (RIMMANDRAKE_RECORD_HAND_ACTS_TICK_ONLY_SAW_ITS_OWN)
  pilot hands   the Conductor's `pilot-launch` acts of 2026-11-15/16, applied by the tick
                (RIMMANDRAKE_DISPATCH_PILOT_HOLDER_RUN_ITSELF_HAND_LAUNCHED_TWICE; selftest_dispatch_pilot_holder.py): a
                Conductor decision on the move that opened blind cycle N launches cycle N past the visit's automatic
                count (cycle_decision); a pilot whose road-back fixers are spent gets ONE holder run on all its open
                road-back items, another only once that set shrank (pilot_holders); red deciders with no open item at
                the certificate get an item each and one builder (cert_red_decide, never twice at the same reds); a
                certificate refusing only stale stamps gets one zero-token `certificate --run` unit per build key, never a
                builder and never a loop (cert_rerun_decide; RIMMANDRAKE_RERUN_STALE_CERTIFICATE_STAMPS_NOBODY_OWNS_IT); a
                blind judge on a pilot writes JUDGE.<run>, starts with no packet and never in the holder's session,
                and is sealed at its end (judge_open, end_judge_run; `judge-verify MOD` is its verification list);
                the ledger part of a launch fits packet_budget_tokens or is refused (modledger.launch)
  slots_full    max_live live runs on advancing mods already (the Conductor's included)
  account_hold  the Dispatcher's account pick holds role launches (its rule's `hold` list): nothing
  launch        spawn a ledger item under this one (seat RUNNER, as ops_watch files), publish the shard, `maturation.py launch` it (opus, the cap)
At the blind challenge (item RIMMANDRAKE_BUILD_BLIND_CHALLENGE_LAUNCHER_FOUR_MODS_PARKED), per advancing mod, one of:
  launch        cycle N (the record's cycles.total) is owed (no cycle_N folder), nothing live or just ended, no blind run
                since it opened, and no automatic cycle yet this visit: one judge (opus, blind_cap_usd), item
                RIMMANDRAKE_JUDGE_<MOD>_BLIND_CYCLE_<N>_TESTS_FIRST spawned the same way as a build item
  live | settling   a run is live on it, or one ended under settle_s ago: nothing
  exit_met | exit_not_met | cycle_unfinished   cycle N is recorded (maturation.read_exit): a Needs Conductor line each;
                the steward confirms or opens the next cycle by hand, never the program
  stopped | auto_spent | hand_run_seen   the visit's automatic cycle ended with no record or failed to launch, or was
                already spent (blind_auto_cycles_per_visit, 1), or a hand-launched blind run worked on the cycle and wrote
                nothing: a Needs Conductor line, never a second automatic cycle
  launch_retry  the launch never started on a transient fault (a git lock, its item not yet on origin/main): not the
                visit's cycle; the next tick publishes the filed item again and launches it, up to launch_tries (3),
                then stopped naming the count (RIMMANDRAKE_RETRY_JUDGE_LAUNCH_GIT_LOCK_SPENT_THE_CYCLE; in-game alike).
                A run KILLED from outside before it wrote its result (an account switch SIGTERMs every Claude process:
                detached_helper.killed) is the same: not the cycle. The tick first finishes it (its finish never ran)
                and starts its return, waits for the clone to come back, then relaunches the same item, within the same
                launch_tries; its dollars stay charged to the stage (RIMMANDRAKE_RETRY_RUN_KILLED_BY_ACCOUNT_SWITCH_CYCLE_KEPT)
  held | blocked | blind_off | no_cap | account_hold | slots_full   as for the offline build
At in-game acceptance (item RIMMANDRAKE_BUILD_IN_GAME_STAGE_LAUNCHER_PYRELANDS_ARRIVED_FIRST), per advancing mod, one of:
  launch        visit N (the moves into in_game) is owed (no visit_N folder), nothing live or just ended on it, no
                in-game run since it opened, no automatic run yet this visit, no in-game run live on ANY mod (one
                live-game driver per game, across all mods), and a game is free: one live driver
                (opus, ingame_cap_usd), item RIMMANDRAKE_DRIVE_<MOD>_IN_GAME_ACCEPTANCE_VISIT_<N> (needs game-up)
  ingame_off    ingame_enabled is false: a Needs Conductor line. It ships false: the timer starts no live run until
                the Conductor has run the first one by hand and set it true
  driver_busy | bridge_held   an in-game run is live on some mod, or the bridge is not takeable (another seat, a live
                driver lock, his OWNER hold): nothing this tick
  exit_met | exit_not_met | visit_unfinished   visit N is recorded (maturation.read_ingame_exit): a Needs Conductor line
  stopped | auto_spent | hand_run_seen | live | settling | held | blocked | no_cap | account_hold | slots_full
                as for the blind challenge (ingame_auto_runs_per_visit, 1)
The program never judges, rejects or sends a mod back, never takes the bridge or a game, never runs `advance`.

The reading (<RM_DISPATCHER_STATE>/maturation/reading.json, RM_MATURATION_DISPATCH_DIR overrides the folder) carries
idle_owed_max_min: the longest an advancing mod at the offline build has had work owed (build, a hand step, or ready to
advance) with nothing running on it. ops_watch's maturation family reads it; OPS_MATURATION_IDLE_ADVANCING_MOD is its one
fixed alarm (over 60 min). A mod first seen owed counts its idle time from its last run's end, else its stage's since.
Selftest: selftest_maturation_dispatch.py (fake launcher, temp tree); selftest_maturation.py --launch for slice 4.
"""
import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import maturation as M          # noqa: E402
import judge_certificate as JC  # noqa: E402  the pre-judgement certificate, read before a judge or visit launch
import maturation_now as MN     # noqa: E402
import maturation_autonomy as AUT   # noqa: E402
import detached_helper as DH    # noqa: E402
import modledger                # noqa: E402  the mod ledger: stage runs from its packet; holder sessions (resume_plan)
import mod_owner_hold as OH          # noqa: E402  the owner's hold: a held mod is never decided (mod_owner_hold.json)

UNM = "UNMEASURED"
RELEASE_STAGES = ("offline_build", "blind_challenge", "in_game")
READ_SLACK = 0.5        # USD: a release read at this spend, give or take, is still a reading of it
# The owner, 2026-11-16 1:08 PM PST: "Please speak in terms of weighted tokens not money. The money quotes don't
# translate meaningfully." Every line a person reads states spend in weighted tokens, unit weighted_v2 (role_launch
# MODEL_PRICES: each field at its model's list price / the Opus 5.5 input price; the owner, 2026-11-16: "I want you to
# properly weight tokens by the model as well so they are more comparable"). The ceiling and the caps are still KEPT
# in list dollars inside, and a list dollar is exactly 1e6 / that input price weighted_v2 tokens for every model, so
# wt() is exact, not a median (until 2026-11-16 it was 350,303 weighted_v1 per dollar, the Opus median of 172 runs,
# reading Sonnet stages high). A cost_usd the CLI marks costBasis other than "list" is not list-priced
# (RIMMANDRAKE_WEIGH_TOKENS_BY_MODEL_OPUS_INPUT_UNIT). Moving the ceiling and caps themselves to tokens is
# RIMMANDRAKE_KEEP_STAGE_CEILING_IN_TOKENS_NOT_LIST_DOLLARS.
def _wt_per_usd():
    import role_launch as RL
    return int(round(1e6 / RL.MODEL_PRICES[RL.REF_MODEL]["input_tokens"]))


WT_PER_USD = _wt_per_usd()      # 250,000 at Opus 5.5's $4/MTok input


def to_wt(usd):
    """List dollars -> weighted tokens at WT_PER_USD (an int: a release command's exact argument)."""
    return int(round(float(usd) * WT_PER_USD))


def from_wt(tokens):
    return float(tokens) / WT_PER_USD


def wt(usd):
    """List dollars -> the words a person reads: '≈17.5M weighted tokens'."""
    n = to_wt(usd)
    return "≈%s weighted tokens" % ("%.1fM" % (n / 1e6) if n >= 1e6 else "%dk" % round(n / 1e3) if n >= 1e3 else n)
CFG_PATH = os.path.join(HERE, "maturation_dispatch.json")
ALARM_NAME = "OPS_MATURATION_IDLE_ADVANCING_MOD"
CLONE_ALARM_NAME = "OPS_DISPATCH_CLONE_BEHIND_UNSTICK"     # ops_watch_rules.json: maturation.clone_behind_min > 5
ITEM = "RIMMANDRAKE_WIRE_DISPATCH_TO_LAUNCH_BUILDERS_MODS_SAT_IDLE"
OWED = ("build", "certificate", "hand step", "ready to advance")
ONES = ("ZERO ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE TEN ELEVEN TWELVE THIRTEEN FOURTEEN FIFTEEN SIXTEEN "
        "SEVENTEEN EIGHTEEN NINETEEN").split()
TENS = "_ _ TWENTY THIRTY FORTY FIFTY SIXTY SEVENTY EIGHTY NINETY".split()


def load_cfg(path=CFG_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sdir():
    d = os.environ.get("RM_MATURATION_DISPATCH_DIR")
    if not d:
        import doorbell
        d = os.path.join(doorbell.state_dir(), "maturation")
    os.makedirs(d, exist_ok=True)
    return d


def _read(p, default):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _write(p, obj):
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    os.replace(p + ".tmp", p)


STATE_LOCK = "state.lock"


@contextlib.contextmanager
def state_lock(d=None):
    """One writer of state.json at a time: the tick holds it from its read to its write, `clear` likewise
    (RIMMANDRAKE_LOCK_DISPATCH_STATE_CLEAR_LOST_TICK_WRITES: a clear during a tick was overwritten, or resurrected)."""
    with open(os.path.join(d or sdir(), STATE_LOCK), "a+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def read_state(p):
    """-> state.json, {} when there is none. One that cannot be read raises: an empty state would drop every stop,
    retry count and spent release (RIMMANDRAKE_REFUSE_UNREADABLE_DISPATCH_STATE_RESET_STOPS)."""
    try:
        with open(p, encoding="utf-8") as f:
            st = json.load(f)
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as e:
        raise RuntimeError("%s cannot be read (%s: %s); nothing runs on a lost state: repair or move it aside" % (
            p, type(e).__name__, e))
    if not isinstance(st, dict):
        raise RuntimeError("%s is not an object; nothing runs on a lost state: repair or move it aside" % p)
    return st


def pac(t):
    return dt.datetime.fromtimestamp(t, MN.PAC).strftime("%Y-%m-%d %I:%M %p %Z").replace(" 0", " ")


def word(n):
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("" if n % 10 == 0 else "_" + ONES[n % 10])
    return "MANY"


def item_id(mod, count, known):
    """-> a rimflow name for a Stage 3 build item: RIMMANDRAKE_AUTOBUILD_<MOD>_<N>_BARS_LEFT, else shorter forms
    (free_name), the last without the count so a long mod name still has room for _RUN_<N>."""
    m, n = mod.upper(), word(count)
    return free_name(["RIMMANDRAKE_AUTOBUILD_%s_%s_BARS_LEFT" % (m, n), "RIMMANDRAKE_AUTOBUILD_%s_%s_LEFT" % (m, n),
                      "RIMMANDRAKE_AUTOBUILD_%s_BARS_LEFT" % m], known)


def batch_of(bars, size):
    """-> this run's batch of the refused bars: the whole list at or under size (or size unset), else the first of
    ceil(n / size) even batches (33 at 6 -> 6, 13 -> 5, 7 -> 4). RIMMANDRAKE_SIZE_DISPATCH_BUILDS_THIRTY_THREE_BARS_ONE_RUN:
    one builder given all 33 refused Graffiti bars spent USD 7.15 of its 8 and stalled on its helpers; the steward split
    them by hand into items of about six."""
    bars = list(bars or [])
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0 or len(bars) <= size:
        return bars
    groups = -(-len(bars) // size)
    return bars[:-(-len(bars) // groups)]


# ---- what is true now -----------------------------------------------------------------------------------------------

def _ts(iso_s):
    try:
        return dt.datetime.fromisoformat(str(iso_s)).timestamp()
    except ValueError:
        return None


def _usd(r):
    return (r["usd"] if isinstance(r.get("usd"), (int, float)) else
            r.get("cap") if isinstance(r.get("cap"), (int, float)) else 0.0)


def gather(root, cfg, live=True):
    """-> {mod: facts}: maturation.build_facts plus, from maturation_now's run placement, the live units, the last run's
    end and the dollars the stage has spent."""
    g = MN.gather(root, live=live)
    by = {m["name"]: m for m in g["mods"]}
    out = {}
    # the one live-game driver is counted over every mod the page reads, not the advancing ones only
    # (RIMMANDRAKE_COUNT_EVERY_MOD_INGAME_DRIVER_NOT_ADVANCING_ONLY)
    other = [r.get("unit") for m in g["mods"] if m.get("name") not in (cfg.get("advancing") or [])
             for r in (m.get("runs") if isinstance(m.get("runs"), list) else []) if r.get("live")
             and _is_ingame_item(r.get("item"))]
    for mod in cfg.get("advancing") or []:
        f = M.build_facts(root, mod)
        m = by.get(mod) or {}
        runs = m.get("runs", UNM) if m else []
        if isinstance(runs, list):
            f["live_units"] = [r["unit"] for r in runs if r.get("live")]
            ends = [r["end"] for r in runs if isinstance(r.get("end"), (int, float))]
            f["last_end"] = max(ends) if ends else None
            box3 = ((m.get("boxes") or {}).get("3") or {}).get("runs") or []
            f["stage_runs"] = {r["unit"]: (r["usd"] if isinstance(r.get("usd"), (int, float)) else
                                           r.get("cap") if isinstance(r.get("cap"), (int, float)) else 0.0)
                               for r in box3 if r.get("unit")}
            f["box_runs"] = {c: {r["unit"]: _usd(r) for r in (b.get("runs") or []) if r.get("unit")}
                             for c, b in (m.get("boxes") or {}).items()}
            f["ended_runs"] = [r for r in runs if not r.get("live") and isinstance(r.get("end"), (int, float))
                               and r.get("unit")]
            f["run_usd"] = {r["unit"]: (r["usd"] if isinstance(r.get("usd"), (int, float)) else
                                        r.get("cap") if isinstance(r.get("cap"), (int, float)) else 0.0)
                            for r in runs if r.get("unit")}
            # for maturation_hands (who launched what) and slow_chores (a dead run whose finish never ran)
            f["runs_seen"] = [{"unit": r["unit"], "item": r.get("item"), "at": r.get("at"), "end": r.get("end")}
                              for r in runs if r.get("unit")]
            f["dead_unfinished"] = [r["unit"] for r in runs if r.get("unit") and not r.get("live") and r.get("end") is None
                                    and ran(r)]
        else:
            f["live_units"] = UNM
        out[mod] = add_ingame(root, mod, add_blind(root, mod, f, runs if isinstance(runs, list) else []),
                              runs if isinstance(runs, list) else [])
        if f.get("stage") == "offline_build" and f.get("owed") == "certificate":
            add_cert(root, mod, f)
        out[mod]["killed"] = killed_runs(runs if isinstance(runs, list) else [])
        out[mod]["ingame_live_other"] = list(other)
    return out


def _takes(fn, name):
    """Does fn take keyword `name` (by name or **kw)?"""
    import inspect
    try:
        ps = inspect.signature(fn).parameters.values()
    except (TypeError, ValueError):
        return True
    return any(p.name == name or p.kind == p.VAR_KEYWORD for p in ps)


def run_game(r):
    """The game a run drives: its own `game`, else RM_GAME_INSTANCE in its unit's record (the env it was launched
    with), else a: a hand launch with no game named drives today's game."""
    g = r.get("game") or (((DH.read_record(r.get("unit")) if r.get("unit") else None) or {}).get("env") or {}).get(
        "RM_GAME_INSTANCE")
    return (g or "a").strip().lower()


def driver_games(facts):
    """-> {unit: game} for the live in-game runs, on any mod."""
    out = {}
    for f in facts.values():
        out.update(f.get("ingame_games") or {})
    return out


def pick_game(cfg, bridge, purpose, held=None):
    """-> (the first free game, or None; [why not, per game]). A game is free when no live driver holds it (held:
    {game: unit}) and its own bridge reading says takeable. The games are cfg game_instances (else a); a reading that
    cannot name a game (a one-argument stand-in) reads game a only. RIMMANDRAKE_LAUNCH_BOTH_GAMES_STEAM_REFUSES_A_BESIDE_B:
    the owner, 2026-11-16, "don't forget we have two Rimworld games, so I don't want to hear any 'waiting for game'"."""
    read = bridge or (lambda p, game="a": M.bridge_idle(p, cfg.get("seat", "BENCH"), game=game))
    named = M.takes_game(read)
    games = [g for g in (cfg.get("game_instances") or ["a"])] if named else ["a"]
    whys = []
    for g in games:
        if g in (held or {}):
            whys.append("game %s: driven by %s" % (g, held[g]))
            continue
        go, why = read(purpose, game=g) if named else read(purpose)
        if go:
            return g, whys
        whys.append("game %s: %s" % (g, why))
    return None, whys


def live_drivers(facts):
    """-> the live in-game runs, on any mod: the one-driver rule's list."""
    return list(dict.fromkeys(u for f in facts.values() for u in list(f.get("ingame_live") or []) +
                              list(f.get("ingame_live_other") or [])))


def killed_runs(runs, read=None, runner=subprocess.run):
    """-> {unit: {why, state, returned, return_going, kept}} for the ended blind and in-game runs that were KILLED before
    they wrote a result (detached_helper.killed), read from their run records."""
    import role_launch as RL
    read = read or DH.read_record
    out = {}
    for r in runs or []:
        u = r.get("unit")
        if not u or r.get("live") or not (_is_blind_item(r.get("item")) or _is_ingame_item(r.get("item"))):
            continue
        rec = read(u)
        why = DH.killed(rec, runner) if rec else ""
        if why:
            out[u] = {"why": why, "state": rec.get("status"), "returned": bool(rec.get("returned")),
                      "kept": any(str(x).startswith("KEPT") for x in rec.get("return_steps") or []),
                      "return_going": (not rec.get("returned") and rec.get("status") == "finished"
                                       and RL.unit_state(u + "-return", runner=runner) not in DH.DEAD_STATES)}
    return out


def _is_ingame_item(item):
    """An in-game run's item names IN_GAME_ACCEPTANCE or IN_GAME_VISIT (this step's names, and the one `maturation.py
    next` suggests for a hand launch); a bare IN_GAME is not enough (this launcher's own build item has one)."""
    return bool(re.search(r"IN_GAME_(ACCEPTANCE|VISIT)", str(item or "").upper()))


JUDGE_VERBS = ("JUDGE", "CHALLENGE", "PILOT")


def _is_blind_item(item):
    """A blind run's item has BLIND in it and, when it is a RIMMANDRAKE_<VERB>_... name, a judge's verb (JUDGE as this
    step names it, CHALLENGE and PILOT as the hand launches named it). A builder or fixer whose subject merely mentions
    BLIND is not one (RIMMANDRAKE_PAUSE_HAND_RUN_ONLY_ON_JUDGE_VERB_ITEMS, 2026-11-17: Pyrelands paused hand_run_seen
    416 min on UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS, Graffiti 545 min on BUILD_GRAFFITI_..._BLIND_FOUND_ZERO_
    HITS). A name without the RIMMANDRAKE_ prefix names no verb, so BLIND alone still decides."""
    s = str(item or "").upper()
    if "BLIND" not in s:
        return False
    if not s.startswith("RIMMANDRAKE_"):
        return True
    return s[len("RIMMANDRAKE_"):].split("_", 1)[0] in JUDGE_VERBS


def ran(r):
    """False for a run record whose launch failed (systemd-run never started a unit): it worked on nothing, so it is
    neither an in-game or blind run of the visit nor a dead run whose finish never ran (2026-11-16: Gimme Some Slack
    paused hand_run_seen on its own failed launch)."""
    return r.get("state") != "launch_failed"


def add_ingame(root, mod, f, runs):
    """ingame_live (every mod): the live runs whose item names an in-game run (_is_ingame_item), for the one-driver rule.
    At in-game acceptance also maturation.ingame_facts (visit, exit reading, owed) and ingame_runs, the in-game runs
    started since the visit opened (10 min of slack, as for the blind challenge)."""
    f["ingame_live"] = [r.get("unit") for r in runs or [] if r.get("live") and _is_ingame_item(r.get("item"))]
    f["ingame_games"] = {r.get("unit"): run_game(r) for r in runs or [] if r.get("live") and _is_ingame_item(r.get("item"))}
    if f.get("stage") != "in_game":
        return f
    f.update(M.ingame_facts(root, mod))
    f["certificate"] = M.certificate(root, mod, "in_game")
    f["cert_rerun_result"] = rerun_result(mod)     # cert_wait's zero-token rerun reads its last result
    t0 = _ts(f.get("opened"))
    f["ingame_runs"] = [r.get("unit") for r in runs or [] if _is_ingame_item(r.get("item")) and ran(r)
                        and isinstance(r.get("at"), (int, float)) and t0 is not None and r["at"] >= t0 - 600]
    return f


def add_cert(root, mod, f):
    """At the offline build waiting on its certificate: the certificate's rows and the test table's known_red marks
    (cert_red_decide reads which red deciders an item already owes)."""
    f["certificate"] = M.certificate(root, mod, "blind_challenge")
    tt, _ = JC.read_table(root, mod)
    f["known_red"] = {tid: t["known_red"] for tid, t in ((tt or {}).get("tests") or {}).items()
                      if isinstance(t, dict) and isinstance(t.get("known_red"), str)}
    f["cert_rerun_result"] = rerun_result(mod)
    return f


def add_blind(root, mod, f, runs):
    """At the blind challenge: maturation.blind_facts (cycle, visit, exit reading, owed) and blind_runs, the runs whose
    item names a blind run (_is_blind_item) that started since the cycle opened (10 min of slack for a launch that beat
    its own advance to origin/main). Any other stage: f unchanged."""
    if f.get("stage") != "blind_challenge":
        return f
    f.update(M.blind_facts(root, mod))
    f["certificate"] = M.certificate(root, mod, "blind_challenge")
    f["cert_rerun_result"] = rerun_result(mod)     # cert_wait's zero-token rerun reads its last result
    f["cycle_decision"] = cycle_decision(M.load(root, mod) or {})
    t0 = _ts(f.get("opened"))
    f["blind_runs"] = [r.get("unit") for r in runs or [] if _is_blind_item(r.get("item")) and ran(r)
                       and isinstance(r.get("at"), (int, float)) and t0 is not None and r["at"] >= t0 - 600]
    return f


def cycle_decision(rec):
    """-> {"at", "text"} when the move that opened the blind cycle now open (the record's last move into the blind
    challenge) carries a recorded Conductor decision (`maturation.py advance <Mod> --to blind_challenge
    --conductor-decision ...`), else None. That decision allows that one cycle, past the visit's automatic cycles
    (RIMMANDRAKE_DISPATCH_PILOT_HOLDER_RUN_ITSELF_HAND_LAUNCHED_TWICE: GimmeSomeSlack read "auto_spent (cycle 2, 3, 4)"
    after the Conductor opened cycle 5, and the cycle was launched by hand)."""
    if not isinstance(rec, dict) or rec.get("stage") != "blind_challenge":
        return None
    moves = [m for m in rec.get("moves") or [] if isinstance(m, dict) and m.get("to") == "blind_challenge"]
    text = ((moves[-1].get("confirmed") or {}).get("conductor_decision") if moves else None)
    return {"at": moves[-1].get("at"), "text": str(text)} if text else None


def account_gate(sched_path=None, dstate=None):
    """-> (go, why): the Dispatcher's own account pick (its state.json `account_pick`), held only when its rule's `hold`
    list names role_launch and the pick is SWITCH or HOLD, the way the Dispatcher holds a role launch."""
    try:
        sch = _read(sched_path or os.path.join(HERE, "dispatcher_schedule.json"), {})
        rule = sch.get("account_pick") or {}
        if dstate is None:
            import doorbell
            dstate = _read(os.path.join(doorbell.state_dir(), "state.json"), {})
        key = str((dstate.get("account_pick") or {}).get("key") or UNM)
        state = key.split()[0]
        if rule.get("enabled") and "role_launch" in (rule.get("hold") or []) and state in ("SWITCH", "HOLD"):
            return False, "the Dispatcher's account pick reads %s and its rule holds role launches" % key
        return True, "the Dispatcher's account pick reads %s (hold list %s)" % (key, rule.get("hold"))
    except Exception as e:  # noqa: BLE001
        return True, "account pick unreadable (%s): the Dispatcher holds nothing on it either" % e


# ---- the decision ---------------------------------------------------------------------------------------------------

def autonomy_book(s, unit):
    """-> "steward" or "fixers" when `unit` is a run the autonomy layer launched for this mod, else None.
    RIMMANDRAKE_EXEMPT_STEWARD_RUNS_FROM_BUILDER_PROGRESS_STOP: Graffiti's preflight steward moved it into the offline
    build while still live, and its end was judged as a builder's ("stopped, 33 -> 33")."""
    if not unit:
        return None
    for book in ("steward", "fixers"):
        for e in (s.get(book) or {}).values():
            if isinstance(e, dict) and e.get("unit") == unit:
                return book
    return None


def progressed(w, ids, fp_now):
    """-> (progress?, why). RIMMANDRAKE_DERIVE_CHECKS_FROM_LOCKED_BARS: progress is a refused bar resolved, by ids, not
    a fall in the count: no id may appear that was not refused before (a rename), and a resolved bar whose checks are
    unchanged is a flag flipped. A watch with no ids (an older state) falls back to the count."""
    was, before = w.get("refused"), w.get("ids")
    n = len(ids) if isinstance(ids, list) else None
    if not isinstance(before, list) or not isinstance(ids, list):
        ok = isinstance(was, int) and isinstance(n, int) and n < was
        return ok, "the refused bars went %s -> %s%s" % (was, n, "" if ok else ", not down")
    new = sorted(set(ids) - set(before))
    gone = sorted(set(before) - set(ids))
    if new:
        return False, "refused bar(s) %s appeared that were not refused before (a rename is not progress)" % ", ".join(
            new[:6])
    if not gone:
        return False, "the refused bars went %s -> %s, none resolved" % (was, n)
    fp0 = w.get("fp") or {}
    flipped = [b for b in gone if fp0.get(b) and (fp_now or {}).get(b) == fp0.get(b)]
    if flipped and len(flipped) == len(gone):
        return False, "bar(s) %s turned runnable with their checks unchanged (a flag flipped, not a check built)" % (
            ", ".join(flipped[:6]))
    return True, "refused bars resolved: %s" % ", ".join(gone[:6])


def occupancy(facts):
    """-> the live runs on advancing mods, or None when any mod's live runs cannot be read: an unknown occupancy is
    never counted as zero (RIMMANDRAKE_RESERVE_CAP_BEFORE_LAUNCH; it used to skip a non-list and launch)."""
    occ = [f.get("live_units") for f in facts.values()]
    if not all(isinstance(x, list) for x in occ):
        return None
    return sum(len(x) for x in occ)


def no_slot(cfg, live_total, put):
    """True (the row put) when no launch slot is free: max_live reached, or the occupancy unknown (fails closed)."""
    if live_total is None:
        put("slots_unknown", "the live runs of an advancing mod cannot be read, so the live count is unknown; nothing "
            "launches on an unknown occupancy")
        return True
    if live_total >= int(cfg.get("max_live", 2)):
        put("slots_full", "%d live runs on advancing mods, the most is %s" % (live_total, cfg.get("max_live", 2)))
        return True
    return False


def over_ceiling(usd, cap, ceiling, where):
    """-> why the next run may not start, or None. The cap is reserved before launch: spent plus the run's cap must fit
    the ceiling (RIMMANDRAKE_RESERVE_CAP_BEFORE_LAUNCH: `usd >= ceiling` let USD 59 of 60 launch a USD 15 run)."""
    if not (isinstance(ceiling, (int, float)) and not isinstance(ceiling, bool)):
        return None
    if usd >= ceiling:
        return "%s spent at %s, at or past the %s ceiling" % (wt(usd), where, wt(ceiling))
    if usd + cap > ceiling:
        return "%s spent at %s plus the next run's %s cap passes the %s ceiling" % (wt(usd), where, wt(cap), wt(ceiling))
    return None


def releases_path():
    return os.path.join(sdir(), "releases.jsonl")


def _usd_ok(v, positive=False):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and (v > 0 if positive else v >= 0)


def release_ok(r):
    """Is one parsed releases.jsonl line a whole release record?"""
    return (isinstance(r, dict) and all(isinstance(r.get(k), str) and r[k].strip() for k in ("id", "ts", "mod", "by", "why"))
            and r.get("stage") in RELEASE_STAGES and _usd_ok(r.get("read_usd")) and _usd_ok(r.get("release_usd"), True))


def read_releases(path=None):
    """-> (records, malformed count). No file is no release; a line that is not a whole record is counted, never used."""
    recs, bad = [], 0
    try:
        with open(path or releases_path(), encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except FileNotFoundError:
        return recs, 0
    for line in lines:
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError:
            r = None
        if release_ok(r):
            recs.append(r)
        else:
            bad += 1
    return recs, bad


def release_cmd(mod, stage, usd, cap, ceiling):
    need = max(1, int(-(-(usd + cap - ceiling) // 1)))
    return ('python3 src/RimMandrake/rimflow/maturation_dispatch.py release %s --stage %s --read-tokens %d --tokens %d '
            '--why "..."' % (mod, stage, to_wt(usd), to_wt(need)))


# over_ceiling's words, in dollars before 2026-11-16 and in weighted tokens since: a stop written before the flag
CEILING_WHY = re.compile(r"^(USD [0-9.]+|≈[0-9.]+[kM]? weighted tokens) spent at ")


def ceiling_stop(stop):
    """Is this stop the ceiling's (lifted by a release)? By its flag, or a legacy stop in over_ceiling's words; never a
    substring: a progress stop naming a bar with "ceiling" in it is not one (RIMMANDRAKE_MATCH_CEILING_STOP_BY_FLAG_NOT_SUBSTRING)."""
    return bool(stop) and bool(stop.get("ceiling") or CEILING_WHY.match(str(stop.get("why") or "")))


def ceiling_gate(cfg, s, mod, stage, usd, cap, where, releases):
    """-> (why the next run may not start, or None; the release record id that lets it start past the ceiling, or
    None). releases: read_releases()'s (records, malformed); s: the mod's state (its releases_used)."""
    ceiling = cfg.get("stage_ceiling_usd")
    over = over_ceiling(usd, cap, ceiling, where)
    if not over:
        return None, None
    recs, bad = releases or ([], 0)
    used = s.get("releases_used") or {}
    mine = [r for r in recs if r["mod"] == mod and r["stage"] == stage]
    fresh = [r for r in mine if r["id"] not in used]
    stale = [r for r in fresh if abs(r["read_usd"] - usd) > READ_SLACK]
    fit = [r for r in fresh if r not in stale and usd + cap <= ceiling + r["release_usd"]]
    if fit:
        return None, fit[-1]["id"]
    notes = []
    if mine and not fresh:
        notes.append("its release is spent")
    if stale:
        notes.append("a release read %s, the spend is now %s" % (wt(stale[-1]["read_usd"]), wt(usd)))
    if len(fresh) > len(stale):
        notes.append("a release of %s does not cover the next run's cap" % wt([r for r in fresh if r not in stale][-1]
                                                                             ["release_usd"]))
    if bad:
        notes.append("%d malformed release line(s) ignored" % bad)
    return "%s%s; release it: %s" % (over, " (%s)" % "; ".join(notes) if notes else "",
                                     release_cmd(mod, stage, usd, cap, ceiling)), None


def stage_spent(f, stage, ours):
    """-> USD spent at this stage: every run the status page placed in its box (measured dollars, else its cap), plus
    this step's own launches there not yet placed (at their cap)."""
    spent = dict((f.get("box_runs") or {}).get(M.COL[stage]) or {})
    for x in ours or []:
        # with the killed attempts a retry replaced: their dollars stay charged (RIMMANDRAKE_CHARGE_KILLED_ATTEMPTS_RETRY_DROPPED_DOLLARS)
        for u in [x.get("unit")] + list(x.get("killed_before") or []):
            if u and u not in spent:
                spent[u] = (f.get("run_usd") or {}).get(u, x.get("cap") or 0.0)
    return round(sum(spent.values()), 2)


REFUND_STAGE = {"blind_challenge": "4+5", "in_game": "6"}       # maturation_convergence's stage keys


def refund(cfg, s, f, stage, usd, cap, unit):
    """-> (refund, why not). The Conductor's judgement of 2026-11-15 12:25 PM PST, as a rule: "cycle 3 was killed
    mid-run by the account switch, not failed ... The mod is converging." A run KILLED from outside before it wrote a
    result (f["killed"]) bought no judging, yet its dollars stay charged to the stage; when they alone hold its own
    retry at the ceiling, the tick gives them back once: the amount still missing, never more than that run spent,
    never twice for one run, and not while the stage reads DIVERGING. Any other release stays the Conductor's hand."""
    if not unit or unit not in (f.get("killed") or {}):
        return None, ""
    if unit in (s.get("refunds") or {}):
        return None, "; the killed run %s was refunded once already" % unit
    ceiling, spent = cfg.get("stage_ceiling_usd"), (f.get("run_usd") or {}).get(unit)
    if not (_usd_ok(spent, True) and _usd_ok(ceiling, True)):
        return None, ""
    need = round(usd + cap - ceiling, 2)
    if need > spent + READ_SLACK:
        return None, "; the killed run %s spent %s, less than the %s missing" % (unit, wt(spent), wt(need))
    word = (s.get("convergence") or {}).get(REFUND_STAGE.get(stage)) or UNM
    if word == "DIVERGING":
        return None, "; no refund of the killed run %s's dollars while the stage reads DIVERGING" % unit
    return {"unit": unit, "stage": stage, "read_usd": usd, "usd": max(need, 0.01), "spent": spent, "word": word}, ""


def book_refunds(st, rows, now, path=None):
    """Each refund a launch used becomes one release record (marked auto, by RUNNER, a delegated call: the daily
    digest reads the same file), spent at once; the killed run is marked refunded. -> the record ids."""
    out = []
    for r in rows:
        ref = r.get("refund")
        if not ref or r.get("decision") != "launched":
            continue
        rec = {"ts": dt.datetime.fromtimestamp(now, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "mod": r["mod"],
               "stage": ref["stage"], "by": "RUNNER", "read_usd": round(ref["read_usd"], 2),
               "release_usd": round(ref["usd"], 2), "auto": True,
               "why": "delegated: killed-run refund: run %s was killed from outside before it wrote a result (not a "
                      "failed run); %s of the %s charged for it is given back once so the same %s can "
                      "finish; the stage's convergence reads %s (the Conductor's rule of 2026-11-15, "
                      "RIMMANDRAKE_REFUND_KILLED_RUN_DOLLARS_AT_THE_CEILING)" % (
                          ref["unit"], wt(ref["usd"]), wt(ref["spent"]),
                          "cycle" if ref["stage"] == "blind_challenge" else "visit", ref["word"])}
        rec["id"] = "rel-%s" % hashlib.sha1(json.dumps(rec, sort_keys=True).encode()).hexdigest()[:12]
        with open(path or releases_path(), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
        s = st["mods"][r["mod"]]
        s.setdefault("releases_used", {})[rec["id"]] = {"at": now, "stage": ref["stage"], "usd": ref["read_usd"],
                                                         "unit": r.get("unit")}
        s.setdefault("refunds", {})[ref["unit"]] = {"at": now, "usd": rec["release_usd"], "release": rec["id"]}
        r["why"] = "%s; killed-run refund %s (%s)" % (r.get("why"), rec["id"], wt(rec["release_usd"]))
        out.append(rec["id"])
    return out


def reserve_refused(cfg, f, row, put, cap, stage, ours, s=None, releases=None, killed=None):
    """The ceiling at the blind challenge and in-game acceptance, as at the offline build: True (the row put) when the
    stage's spend plus this run's cap passes stage_ceiling_usd. Read every tick, never stored: raising the ceiling or a
    Conductor's release (`release`) lifts it, the release once. killed: the killed run this launch retries, if any
    (refund)."""
    usd = stage_spent(f, stage, ours)
    row["stage_usd"] = usd
    over, rid = ceiling_gate(cfg, s or {}, row["mod"], stage, usd, cap, M.label(stage), releases)
    if over:
        ref, why_not = refund(cfg, s or {}, f, stage, usd, cap, killed)
        if ref:
            row["refund"] = ref
            return False
        over += why_not
        put("ceiling", over, "the ceiling, %s; nothing more launches on it until the Conductor reads the spend" % over)
        return True
    if rid:
        row["release"] = rid
    return False


def decide(cfg, st, facts, now, account=(True, ""), bridge=None, releases=None):
    """-> (rows, launches). Pure over (cfg, st, facts): it mutates st (watch, stop, owed_since) and returns one row per
    advancing mod and the mods to launch, in list order. Never launches on a mod twice in one tick, and at most one
    in-game run in all. bridge(purpose) -> (takeable, why) is asked only for an in-game launch otherwise decided."""
    rows, launches = [], []
    cap = cfg.get("cap_usd")
    cap_ok = isinstance(cap, (int, float)) and not isinstance(cap, bool) and cap > 0
    mods = st.setdefault("mods", {})
    live_total = occupancy(facts)
    drivers = live_drivers(facts)
    games_of = driver_games(facts)
    for mod in cfg.get("advancing") or []:
        f = facts.get(mod) or {"stage": UNM}
        s = mods.setdefault(mod, {})
        ids = M.refused_ids(f) if f.get("stage") == "offline_build" else None
        n = len(ids) if ids is not None else None
        row = {"mod": mod, "stage": f.get("stage", UNM), "owed": f.get("owed"), "refused": n,
               "refused_ids": ids, "live": f.get("live_units"), "hand_steps": f.get("hand_steps"),
               "bar_fp": f.get("bar_fp")}
        rows.append(row)

        def put(decision, why, need=None):
            row["decision"], row["why"] = decision, why
            if need:
                row["need"] = "%s: %s" % (mod, need)
        put.row = row

        if f.get("stage") == "blind_challenge":
            s.pop("owed_since", None)
            s.pop("watch", None)
            if decide_blind(cfg, s, f, row, put, now, account, live_total, releases):
                live_total += 0 if row.get("cert_rerun_key") else 1     # a zero-token rerun takes no run slot
                launches.append(mod)
            continue
        if f.get("stage") == "in_game":
            s.pop("owed_since", None)
            s.pop("watch", None)
            if decide_ingame(cfg, s, f, row, put, now, account, live_total, drivers, bridge, releases, games_of):
                if not row.get("cert_rerun_key"):   # a zero-token rerun takes no run slot and drives no game
                    live_total += 1
                    drivers.append("(this tick: %s)" % mod)
                    games_of[drivers[-1]] = row.get("game", "a")
                launches.append(mod)
            continue
        if f.get("stage") != "offline_build":
            s.pop("owed_since", None)
            s.pop("watch", None)
            put("not_offline", "stands at %s; only the offline build, the blind challenge and in-game acceptance "
                "launch from here%s" % (
                f.get("stage"), " (the Designer stays his)" if f.get("stage") in (UNM, "designer", "intake") else ""))
            continue
        live = f.get("live_units")
        if not isinstance(live, list):
            put("blind", "the detached-run records could not be read; nothing launches on a blind reading",
                "the run records are unreadable, so the Dispatch step launches nothing on it")
            continue
        if live:
            w = s.get("watch")
            if not w or w.get("unit") not in live:
                s["watch"] = {"unit": live[0], "refused": n, "ids": ids, "at": now, "fp": f.get("bar_fp"),
                              "ours": any(x.get("unit") == live[0] for x in s.get("launches") or [])}
            s.pop("owed_since", None)
            put("live", "%s is live on it (refused bars %s when first seen)" % (", ".join(live), s["watch"]["refused"]))
            continue
        le = f.get("last_end")
        settle = float(cfg.get("settle_s", 180))
        if s.get("watch") and isinstance(le, (int, float)) and 0 <= now - le < settle:
            # a 60 s tick can land seconds after the unit ends, before its published files reach this clone: the refused
            # count read now may still be the old one. Keep the watch, judge it on a later tick.
            put("settling", "run %s ended %d s ago; its result is judged %d s after the end, not before" % (
                s["watch"].get("unit"), now - le, settle))
            continue
        w = s.pop("watch", None)
        if w:       # a run ended since the last tick: did the refused count fall?
            was = w.get("refused")
            s["last_run"] = {"unit": w.get("unit"), "refused_before": was, "refused_after": n, "ended_seen": now}
            book = autonomy_book(s, w.get("unit"))
            if book:    # a steward or fixer is not a builder: its own book and cap govern its retries
                s["last_run"]["autonomy"] = book
            prog, pwhy = progressed(w, ids, f.get("bar_fp"))
            # a run first seen with no refused bars had no build work to resolve: it was no builder (a hand-launched
            # fix on a mod standing here read "0 -> 0, none resolved", and a stop on an empty set could never lift)
            idle = was == 0 and not w.get("ids")
            if idle:
                s["last_run"]["not_judged"] = "no build work was owed when it started (0 refused bars)"
            if not prog and not book and not idle:
                s["stopped"] = {"ids": ids, "at": now, "why": "run %s ended and %s" % (w.get("unit"), pwhy)}
        owed = f.get("owed")
        if owed in OWED:
            if not s.get("owed_since"):
                cands = [x for x in (f.get("last_end"), _ts(f.get("since"))) if isinstance(x, (int, float))]
                s["owed_since"] = max(cands) if cands else now
        else:
            s.pop("owed_since", None)
        row["idle_min"] = round((now - s["owed_since"]) / 60) if s.get("owed_since") else 0
        if owed == "blocked":
            what = ", ".join(f.get("other_refusals") or [])
            put("held" if "hold" in (f.get("other_refusals") or []) else "blocked", "refused by %s, not build work" % what)
            continue
        if owed == "certificate":
            got = cert_red_decide(cfg, s, f, row, put, now, account, live_total, cap if cap_ok else 0, releases)
            got = got or cert_rerun_decide(cfg, s, f, row, put, now)
            if got == "launch":
                live_total += 0 if row.get("cert_rerun_key") else 1     # a zero-token rerun takes no builder slot
                launches.append(mod)
            elif not got:
                cert_put(put, mod, "blind_challenge", f.get("certificate_why"), f.get("certificate_fix"),
                         "the move into the blind challenge")
            continue
        if owed == "ready to advance":
            put("ready", "every exit test passes", "ready to advance: every Stage 3 exit test passes "
                "(maturation.py advance %s --to blind_challenge, a Conductor step)" % mod)
            continue
        if owed == "hand step":
            put("hand_step", "only hand steps are left: %s" % ", ".join(f.get("hand_steps") or []),
                "hand step %s (%s)" % (", ".join(f.get("hand_steps") or []), "; ".join(
                    str(v) for k, v in (f.get("observed") or {}).items() if k in (f.get("hand_steps") or []))))
            continue
        if ids is None:
            te = (": %s" % f["table_error"]) if f.get("table_error") else ""
            put("blind", "the test table cannot be read" + te, "the test table cannot be read%s; no builder launches on "
                "it" % te)
            continue
        usd = offline_usd(f, s)
        row["stage_usd"] = usd
        over, rid = ceiling_gate(cfg, s, mod, "offline_build", usd, cap if cap_ok else 0, "the offline build", releases)
        stop = s.get("stopped")
        if ceiling_stop(stop) and rid:
            s.pop("stopped")
            row["stop_lifted"], stop = "a ceiling release (%s)" % rid, None
        lr = s.get("last_run") or {}
        if (stop and lr.get("unit") and str(stop.get("why")).startswith("run %s ended and " % lr["unit"])
                and autonomy_book(s, lr["unit"])):
            # a stop written before the progress test learned that a steward or fixer run is not a builder's
            s.pop("stopped")
            row["stop_lifted"], stop = "it judged the %s run %s as a builder" % (
                autonomy_book(s, lr["unit"]), lr["unit"]), None
        if (stop and stop.get("ids") == [] and str(stop.get("why")).startswith("run ") and not stop.get("ceiling")
                and " 0 -> " in str(stop.get("why"))):
            # written before a run seen with no refused bars stopped being judged as a builder: nothing shrinks an
            # empty set, so it held the mod for good
            s.pop("stopped")
            row["stop_lifted"], stop = "it was written on a run that had no refused bars to resolve", None
        if (stop and stop.get("launch_failed") and stop.get("code") and cfg.get("_code")
                and stop["code"] != cfg["_code"] and int(stop.get("tries") or 1) < int(cfg.get("launch_tries", 3))):
            # the launch failed on a defect, not a transient fault, and the pipeline's code has changed since: one more
            # try on the same item (the Conductor's hand `clear` after a fix landed, 2026-11-15 12:18 PM PST)
            s["launch_retry"] = {"item": stop.get("item"), "filed": bool(stop.get("filed")),
                                 "tries": int(stop.get("tries") or 1), "at": now, "refused": n,
                                 "failed": stop.get("why")}
            s.pop("stopped")
            row["stop_lifted"], stop = "the pipeline's code changed since the failed launch (%s -> %s)" % (
                str(stop["code"])[:10], str(cfg["_code"])[:10]), None
        # a stop lifts only when refused bars were resolved (the set shrank); a renamed id is not a resolution
        if stop and not (isinstance(ids, list) and isinstance(stop.get("ids"), list)
                         and set(ids) < set(stop["ids"])):
            put("stopped", stop.get("why"), "stopped, %s; never a second automatic try at the same refusals "
                "(`maturation_dispatch.py clear %s --why ...` lifts it)" % (stop.get("why"), mod))
            continue
        if stop:
            s.pop("stopped")
            row["stop_lifted"] = "the refused set changed since the stop (%s)" % stop.get("why")
        if over:
            s["stopped"] = {"ids": ids, "at": now, "why": over, "ceiling": True}
            put("stopped", s["stopped"]["why"], "stopped, %s" % s["stopped"]["why"])
            continue
        if rid:
            row["release"] = rid
        if not cap_ok:
            put("no_cap", "the settings have no positive cap_usd; nothing launches without a cap")
            continue
        if not account[0]:
            put("account_hold", account[1])
            continue
        if no_slot(cfg, live_total, put):
            continue
        live_total += 1
        bars = [i for i in ids if i != "table_version"]
        batch = batch_of(bars, cfg.get("build_batch_bars"))
        if len(batch) < len(bars):
            row["batch"] = batch
        put("launch", "%d bars refused as build work%s, nothing live on it (%s)" % (
            n, ", this run takes a batch of %d" % len(batch) if row.get("batch") else "", account[1]))
        launches.append(mod)
    return rows, launches


def offline_usd(f, s):
    """-> the mod's measured dollars at the offline build: the runs the status page places there, plus this step's
    launches there it does not place yet (at their measured dollars, else their cap)."""
    spent = dict(f.get("stage_runs") or {})
    for x in s.get("launches") or []:
        if x.get("stage") == "offline_build" and x.get("unit") not in spent:
            spent[x["unit"]] = (f.get("run_usd") or {}).get(x["unit"], x.get("cap") or 0.0)
    return round(sum(spent.values()), 2)


def red_deciders(f):
    """-> the offline deciders the certificate refuses as recorded red (clause green), sorted."""
    cv = f.get("certificate")
    if not isinstance(cv, dict):
        return []
    return sorted({r.get("test") for r in cv.get("rows") or [] if r.get("status") == "REFUSED"
                   and r.get("clause") == "green" and r.get("test")})


def cert_red_decide(cfg, s, f, row, put, now, account, live_total, cap, releases=None):
    """At the offline build waiting on its certificate, with deciders recorded red (FlowWorks, 2026-11-16 1:36 AM PST:
    "owes nothing launchable at offline_build (certificate) and has no open road-back item", reds
    T_FETCH_FALLEN_OFFLINE, T_LIQUID_COATING_OFFLINE, T_TOSS_FLAME_OFFLINE). -> "launch" (row["cert_reds"]: execute
    files the item that owes each red decider and launches ONE builder on them, cert_launch), "decided" (the row put:
    settling, stopped, or a gate), or None (no reds: the certificate wait stands; stale stamps alone are
    `certificate --run`). Never a second automatic try at the same reds: another only once the red set shrank, or a
    launch that never started on a transient fault, within launch_tries."""
    mod = row["mod"]
    reds = red_deciders(f)
    if not reds:
        return None
    row["cert_reds"] = reds
    row["certificate"] = {"rows": [r for r in (f.get("certificate") or {}).get("rows") or []
                                   if r.get("clause") == "green" and r.get("test") in reds]}
    row["known_red"] = {t: (f.get("known_red") or {}).get(t) for t in reds if (f.get("known_red") or {}).get(t)}
    prior = s.get("cert_red") if isinstance(s.get("cert_red"), dict) else None
    if prior and prior.get("unit") and 0 <= now - float(prior.get("at") or 0) < float(cfg.get("settle_s", 180)):
        put("settling", "the builder %s on red deciders %s started %d s ago" % (
            prior["unit"], ", ".join(prior.get("tests") or []), now - float(prior.get("at") or 0)))
        return "decided"
    # a launch that never started is tried again on a transient fault, or once the pipeline's code has changed since it
    # failed (FlowWorks' first was refused over the packet line before the packet builder learned to fit it), within
    # launch_tries (RIMMANDRAKE_RETRY_FAILED_LAUNCH_ONCE_CODE_CHANGES)
    retry = bool(prior and not prior.get("unit") and int(prior.get("tries") or 1) < int(cfg.get("launch_tries", 3))
                 and (AUT.transient(str(prior.get("failed") or "")) or (
                     cfg.get("_code") and prior.get("code") != cfg["_code"])))
    if prior and not retry and not set(reds) < set(prior.get("tests") or []):
        why = ("the builder %s on red deciders %s ended and %s still red" % (
            prior["unit"], ", ".join(prior.get("tests") or []), ", ".join(reds)) if prior.get("unit") else
            "the launch on red deciders %s failed: %s" % (", ".join(prior.get("tests") or []), prior.get("failed")))
        put("stopped", why, "stopped, %s; never a second automatic try at the same reds (items %s; "
            "`maturation_dispatch.py clear %s --why ...` lifts it)" % (
                why, ", ".join(sorted(set((prior.get("items") or {}).values()))) or "none filed", mod))
        return "decided"
    usd = offline_usd(f, s)
    row["stage_usd"] = usd
    over, rid = ceiling_gate(cfg, s, mod, "offline_build", usd, cap, "the offline build", releases)
    if over:
        put("stopped", over, "stopped, %s" % over)
        return "decided"
    if rid:
        row["release"] = rid
    if not cap:
        put("no_cap", "the settings have no positive cap_usd; nothing launches without a cap")
        return "decided"
    if not account[0]:
        put("account_hold", account[1])
        return "decided"
    if no_slot(cfg, live_total, put):
        return "decided"
    row["cap"] = cap
    put("launch", "its certificate refuses %d red decider(s) (%s) and nothing is live on it: the item owing each and "
        "one builder on them%s (%s)" % (len(reds), ", ".join(reds), ", a retry after a transient fault" if retry
                                       else "", account[1]))
    return "launch"


RERUN_MAX_S = 4 * 3600     # a certificate rerun unit's bound (RuntimeMaxSec); FlowWorks' C# suite alone ran 531 s


def stale_key(cv):
    """-> a key for a certificate whose every refusal is a stale stamp (clause ran_on_this_build): the stale deciders and
    the build each must carry now (would_pass names it), so a new build is a new key. None when it does not refuse, or
    refuses on anything a rerun cannot pass (a red decider, an unregistered one, a bar with no decider)."""
    if not isinstance(cv, dict):
        return None
    ref = [r for r in cv.get("rows") or [] if isinstance(r, dict) and r.get("status") == "REFUSED"]
    if not ref or any(r.get("clause") != "ran_on_this_build" for r in ref):
        return None
    want = sorted({(str(r.get("test")), str(r.get("would_pass"))) for r in ref})
    return hashlib.sha1(json.dumps(want).encode("utf-8")).hexdigest()[:12]


def cert_rerun_decide(cfg, s, f, row, put, now, to="blind_challenge", what="the move into the blind challenge",
                      why=None, fix=None):
    """At the offline build waiting on a certificate that refuses only stale stamps (no red decider: cert_red_decide
    returned None) -> "launch" (row["cert_rerun_key"]: execute starts ONE detached zero-token `certificate <Mod> --run`,
    cert_rerun_unit), "decided" (the row put), or None (not stale-only: the certificate wait stands). Once per build key,
    never a loop: the same key again is a Needs Conductor line once its run ended; a run whose own result left the new
    key stale (a decider that rewrites what it reads) is one too. A start that failed is tried again on a transient
    fault or once the pipeline's code changed, within launch_tries (RIMMANDRAKE_RERUN_STALE_CERTIFICATE_STAMPS_NOBODY_OWNS_IT:
    Explosive Knockback waited for a hand on 11 stale bars, 2026-11-16 12:28 PM PST). The same rerun runs at the blind
    cycle and in-game visit gates (cert_wait: TO and WHAT name the gate, WHY and FIX its certificate's reading;
    RIMMANDRAKE_RERUN_STALE_CERTIFICATE_AT_VISIT_AND_CYCLE_GATES: Gimme Some Slack sat 137 min at in-game visit 2 on 29
    stale stamps, 2026-11-17 11:45 AM PST)."""
    key = stale_key(f.get("certificate"))
    if not key:
        return None
    mod = row["mod"]
    row["stale_key"] = key
    prior = s.get("cert_rerun") if isinstance(s.get("cert_rerun"), dict) else None
    res = f.get("cert_rerun_result") if isinstance(f.get("cert_rerun_result"), dict) else None
    mine = res if res and prior and prior.get("unit") and res.get("unit") == prior["unit"] else None
    lift = "`maturation_dispatch.py clear %s --why ...` lets it run once more" % mod

    def wait(said):
        cert_put(put, mod, to, why or f.get("certificate_why"), fix or f.get("certificate_fix"), what)
        row["need"] = "%s; %s, and the step never reruns the same build (%s)" % (row.get("need"), said, lift)
        return "decided"
    age = now - float((prior or {}).get("at") or 0)
    if prior and prior.get("unit") and not mine and 0 <= age < RERUN_MAX_S:
        # still running, on this build or an older one: never a second worker beside it in the one pool clone
        put("live", "certificate rerun %s (zero tokens) started %d s ago on %s" % (
            prior["unit"], age, "this build" if prior.get("key") == key else "an older build; this build reruns after it"))
        return "decided"
    if prior and prior.get("key") == key:
        if prior.get("unit"):
            return wait("the zero-token certificate rerun %s on this build %s" % (prior["unit"], (
                "ended (ok %s, published %s%s)" % (mine.get("ok"), mine.get("published") or "nothing",
                                                   ", error: %s" % mine["error"] if mine.get("error") else "")
                if mine else "left no result within %d s" % RERUN_MAX_S)))
        retry = int(prior.get("tries") or 1) < int(cfg.get("launch_tries", 3)) and (
            AUT.transient(str(prior.get("failed") or "")) or code_changed(cfg, prior))
        if not retry:
            return wait("the certificate rerun on this build did not start (%s)" % prior.get("failed"))
    elif mine and mine.get("key_after") == key:
        return wait("the certificate rerun %s left its own build stale (a decider that changes what it reads?)"
                    % prior["unit"])
    row["cert_rerun_key"] = key
    n = len({r.get("test") for r in (f.get("certificate") or {}).get("rows") or [] if r.get("status") == "REFUSED"})
    put("launch", "its certificate refuses only stale stamps (%d decider(s) last run on an older build), no decider "
        "red: one zero-token `maturation.py certificate %s --run`, detached, for this build" % (n, mod))
    return "launch"


def cert_rerun_launch(cfg, st, row, now, fx):
    """execute's act for cert_rerun_decide's launch: start the unit, book it against the build key. -> True when up."""
    mod, s, key = row["mod"], st["mods"][row["mod"]], row["cert_rerun_key"]
    prior = s.get("cert_rerun") if isinstance(s.get("cert_rerun"), dict) else {}
    try:
        rc, text, unit = (fx.get("cert_rerun") or cert_rerun_unit)(mod, key)
    except Exception as e:      # noqa: BLE001  a start that raised is a start that failed
        rc, text, unit = 1, "%s: %s" % (type(e).__name__, e), None
    unit = unit if rc == 0 else None
    s["cert_rerun"] = {"key": key, "unit": unit, "at": now, "failed": None if unit else str(text), "code": cfg.get("_code"),
                       "tries": int(prior.get("tries") or 1) + 1 if prior.get("key") == key and not prior.get("unit")
                       else 1}
    if unit:
        row.update(decision="launched", unit=unit, why=text)
        return True
    row.update(decision="launch_failed", why=str(text), need="%s: the zero-token certificate rerun did not start (%s)"
               % (mod, text))
    return False


def rerun_dir():
    d = os.path.join(sdir(), "cert_rerun")
    os.makedirs(d, exist_ok=True)
    return d


def rerun_result(mod):
    """-> the last certificate rerun's result for mod (cert_rerun_worker writes it), or None."""
    r = _read(os.path.join(rerun_dir(), "%s.json" % mod), None)
    return r if isinstance(r, dict) else None


def cert_rerun_unit(mod, key, runner=subprocess.run, now=None):
    """Start `maturation_dispatch.py cert-rerun MOD` as its own transient user unit (bounded by RERUN_MAX_S; the 60 s
    tick never waits on it). -> (rc, text, unit)."""
    unit = "rm-cert-rerun-%s-%d" % (re.sub(r"[^a-z0-9]+", "-", mod.lower()).strip("-"), int(now or time.time()))
    log = os.path.join(rerun_dir(), "%s.log" % mod)
    argv = ["systemd-run", "--user", "--quiet", "--collect", "--unit", unit, "-p", "RuntimeMaxSec=%d" % RERUN_MAX_S,
            "-p", "StandardOutput=append:" + log, "-p", "StandardError=append:" + log, "--working-directory", REPO,
            "--setenv", "PATH=" + os.environ.get("PATH", "/usr/bin:/bin"), "--setenv", "RM_MATURATION_DISPATCH_DIR=" + sdir(),
            "--", sys.executable, os.path.abspath(__file__), "cert-rerun", mod, "--key", key, "--unit", unit]
    try:
        r = runner(argv, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        return 1, "systemd-run failed: %s: %s" % (type(e).__name__, e), None
    if r.returncode:
        return r.returncode, "systemd-run exit %d: %s" % (r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()), None
    return 0, "STARTED %s: certificate %s --run, zero tokens (log %s)" % (unit, mod, log), unit


def cert_rerun_worker(mod, key, unit, runner=subprocess.run, take=None, now=time.time):
    """The unit's body: in its own pool clone (synced to origin/main), `maturation.py certificate MOD --run --resume`,
    publish the table by path when it changed, and write the result the tick reads (rerun_result). -> the result."""
    res = {"mod": mod, "unit": unit, "key": key, "at": now(), "ok": None, "key_after": None, "published": None,
           "error": None}
    rel = "design/concepts/%s/version/test_table.json" % mod
    kw = {"capture_output": True, "text": True, "stdin": subprocess.DEVNULL}
    try:
        clone, said = (take or DH.take_clone)("RIMMANDRAKE_RERUN_%s_CERTIFICATE" % mod.upper())
        res["clone"] = clone
        r = runner([sys.executable, os.path.join("src", "RimMandrake", "rimflow", "maturation.py"), "certificate", mod,
                    "--run", "--resume", "--json"], cwd=clone, timeout=RERUN_MAX_S, **kw)
        try:
            cv = json.loads(r.stdout or "")
        except ValueError:
            raise RuntimeError("certificate --run exit %d printed no verdict: %s" % (
                r.returncode, ((r.stdout or "") + (r.stderr or ""))[-300:]))
        res.update(ok=bool(cv.get("ok")), key_after=stale_key(cv), ran=cv.get("run"))
        g = runner(["git", "status", "--porcelain", "--", rel], cwd=clone, timeout=120, **kw)
        if (g.stdout or "").strip():
            p = runner(["./publish", "-m", "maturation: %s certificate rerun on its build (dispatch, zero tokens)" % mod,
                        rel], cwd=clone, timeout=900, **kw)
            m = re.search(r"PUBLISHED ([0-9a-f]{7,40})", (p.stdout or "") + (p.stderr or ""))
            if m:
                res["published"] = m.group(1)
            else:
                res["error"] = "publish exit %d: %s" % (p.returncode, ((p.stdout or "") + (p.stderr or ""))[-300:])
        else:
            res["note"] = "the table did not change"
    except Exception as e:      # noqa: BLE001  the result says what failed; the tick reads it
        res["error"] = "%s: %s" % (type(e).__name__, e)
    res["end"] = now()
    _write(os.path.join(rerun_dir(), "%s.json" % mod), res)
    return res


def cert_item_id(mod, test, known):
    """-> a rimflow name for the item owing red decider `test`: RIMMANDRAKE_GREEN_<MOD>_<TEST words>_RED_DECIDER, test
    words dropped from the end until it fits 9 words and 64 chars (rimflow namecheck)."""
    words = [w for w in re.split(r"[^A-Z0-9]+", str(test).upper()) if w]
    while True:
        parts = ["RIMMANDRAKE", "GREEN", mod.upper()] + words + ["RED", "DECIDER"]
        name = "_".join(parts)
        if (len(parts) <= 9 and len(name) <= 64) or not words:
            break
        words = words[:-1]
    if name not in known:
        return name
    for k in range(2, 20):
        cand = "%s_AGAIN_%s" % (name[:-len("_DECIDER")], ONES[k])
        if cand not in known and len(cand) <= 64 and cand.count("_") <= 8:
            return cand
    return None


def cert_brief(mod, chosen, cap, bars):
    lines = ["# Find why %s's offline deciders are red, and make each one hold (Stage 3: the certificate before the "
             "blind challenge)" % mod, "",
             "Items: %s. Seat BENCH. Offline only: no game, no bridge, no helpers." % (
                 ", ".join(sorted(set(chosen.values()))),), "",
             "`maturation.py certificate %s` refuses the move into the blind challenge: these offline deciders are "
             "recorded red, and no open item owed them until the Dispatch step filed these (item "
             "RIMMANDRAKE_DISPATCH_PILOT_HOLDER_RUN_ITSELF_HAND_LAUNCHED_TWICE):" % mod, ""]
    lines += ["- `%s` (bars %s): item %s" % (t, ", ".join(bars.get(t) or []) or "-", it) for t, it in sorted(
        chosen.items())]
    lines += ["", "1. First run `python3 src/RimMandrake/rimflow/maturation.py certificate %s --run` (zero tokens): it "
              "reruns every offline decider and stamps its build. A decider that turns green needs nothing more: land "
              "`design/concepts/%s/version/test_table.json` and close its item with that sha." % (mod, mod),
              "2. For each decider still red, first learn what it is telling you. Was it green before the last change? "
              "Then it is evidence about that change. Search for every other check that reads the same thing. If the "
              "fix that greens it would redden another, two bars are in conflict: map where each holds and use the "
              "moves of \"How a bar is shown to hold\" below, not a new number (on Gimme Some Slack this certificate's "
              "red was such a pair). Otherwise fix the mod, or the test where the test is wrong (never loosen a "
              "north-star bar); the failing test first, seen failing; land with `./publish -m ... <paths>`; close its "
              "item with the published sha.",
              "3. Rerun `certificate %s --run`, land the table, and end with `maturation.py certificate %s` exiting 0, "
              "or a note starting `LEFT OPEN:` on each item still red: what remains, what you tried, and the map or "
              "the experiment that would settle it." % (mod, mod), "", M.HOW_A_BAR_HOLDS]
    return "\n".join(lines) + "\n"


def cert_launch(root, cfg, st, row, now, fx, known, do_file):
    """execute's act for cert_red_decide's launch: reuse the open item a red decider already has (its known_red, or
    the one filed for it before), file one for each other, then ONE builder on all of them (a pilot's from its ledger
    packet as its holder). Booked in s["cert_red"]: the reds, the items, the unit. -> True when it started."""
    mod, s = row["mod"], st["mods"][row["mod"]]
    reds, kr = row["cert_reds"], row.get("known_red") or {}
    mine = s.setdefault("cert_red_items", {})
    cand = {t: kr.get(t) or mine.get(t) for t in reds}
    ended = (fx.get("ended") or (lambda ids: M.ledger_ended(root, ids)))([v for v in cand.values() if v])
    bars = {}
    for r in ((row.get("certificate") or {}).get("rows") or []):
        if r.get("test") in reds and r.get("clause") == "green":
            bars.setdefault(r["test"], []).append(r.get("bar"))
    chosen, failed = {}, None
    prior = s.get("cert_red") if isinstance(s.get("cert_red"), dict) else {}
    for t in reds:
        if cand.get(t) and cand[t] not in ended:
            chosen[t] = cand[t]
            continue
        name = cert_item_id(mod, t, known)
        title = ("%s Stage 3: offline decider %s is recorded red; make it green, offline (filed by the Dispatch step)"
                 % (mod, t))
        why = ("delegated: maturation_dispatch.py; the certificate refuses %s as recorded red with no open item owing "
               "it, measured %s" % (t, pac(now)))
        ok, text = do_file(name, title, why) if name else (False, "no free item name")
        if not ok:
            failed = text
            break
        mine[t] = name
        chosen[t] = name
        known.add(name) if isinstance(known, set) else None
    unit, text = None, failed
    if not failed:
        cap = row.get("cap") or cfg["cap_usd"]
        item = sorted(set(chosen.values()))[0]
        brief = cert_brief(mod, chosen, cap, bars)
        do_brief = fx.get("launch_brief") or AUT.launch_brief
        if (fx.get("pilot") or pilot_ledger)(root, mod):
            try:
                led = ledger_open(root, mod, "builder", brief, stage="offline_build", now=now, fx=fx)
            except Exception as e:      # noqa: BLE001  a refused grant is a launch that never started
                led, text = None, "REFUSED: %s's ledger launch failed: %s: %s" % (mod, type(e).__name__, e)
            if led:
                rc, text, unit = do_brief(item, led["brief"], cfg.get("model", "opus"), cap, cfg.get("seat", "BENCH"),
                                          env=led["env"])
                unit = unit if rc == 0 else None
                text = "%s; %s" % ((text or "").splitlines()[0] if text else rc,
                                   ledger_after(root, st, mod, led, unit, item, now, fx))
        else:
            rc, text, unit = do_brief(item, brief, cfg.get("model", "opus"), cap, cfg.get("seat", "BENCH"))
            unit = unit if rc == 0 else None
        if unit:
            s.setdefault("launches", []).append({"unit": unit, "item": item, "at": now, "cap": cap,
                                                 "stage": "offline_build", "cert_reds": reds})
    s["cert_red"] = {"tests": reds, "items": chosen, "unit": unit, "at": now, "failed": None if unit else text,
                     "code": cfg.get("_code"),
                     "tries": int(prior.get("tries") or 0) + 1 if not prior.get("unit") and prior else 1}
    if unit:
        row.update(decision="launched", unit=unit, item=sorted(set(chosen.values()))[0], why=text,
                   items=sorted(set(chosen.values())))
        return True
    row.update(decision="launch_failed", why=str(text), need="%s: the launch on red deciders %s failed (%s); the step "
               "will not retry it on its own" % (mod, ", ".join(reds), text))
    return False


def retriable(cfg, x, killed=None):
    """-> True when a blind or in-game book entry is a launch that NEVER STARTED on a transient fault (a git lock, its
    item not yet on origin/main: maturation_autonomy.transient) with tries left (launch_tries, 3). Such a launch judged
    nothing, so it is not the visit's automatic run; one that started, or failed any other way, is
    (RIMMANDRAKE_RETRY_JUDGE_LAUNCH_GIT_LOCK_SPENT_THE_CYCLE). An older entry without tries reads as its first try.
    killed ({unit: ...}, killed_runs): a run that started and was KILLED before it wrote a result is retried the same
    way (RIMMANDRAKE_RETRY_RUN_KILLED_BY_ACCOUNT_SWITCH_CYCLE_KEPT); one that ended by itself with no record is not."""
    if not isinstance(x, dict):
        return False
    if x.get("unit"):
        # a started run's retries count its KILLS (killed_before plus this one), not the launch faults before it
        # started: Gimme Some Slack's visit 1 started on launch try 3, was stopped for his look, and stood stopped
        # (RIMMANDRAKE_ENACT_TOKENS_NOT_DOLLARS_NO_LIVE_HOLD, 2026-11-16)
        kills = len(x.get("killed_before") or []) + 1
        return not x.get("failed") and x["unit"] in (killed or {}) and kills < int(cfg.get("launch_tries", 3))
    if int(x.get("tries") or 1) >= int(cfg.get("launch_tries", 3)):
        return False
    if not (x.get("failed") and x.get("never_started", True)):
        return False
    # a launch that failed on a defect (a rule that refused the spawn, say) is tried again once the pipeline's code
    # has changed since: the fix may have landed. Before this the Conductor fixed the cause, then cleared by hand.
    return AUT.transient(x["failed"]) or code_changed(cfg, x)


def code_changed(cfg, x):
    return bool(x.get("code") and cfg.get("_code") and x["code"] != cfg["_code"])


def pipeline_code(root):
    """-> the git tree id of src/RimMandrake/rimflow at this clone's HEAD (the code the tick is running), or None."""
    try:
        r = subprocess.run(["git", "-C", root, "rev-parse", "HEAD:src/RimMandrake/rimflow"], capture_output=True,
                           text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def reap_wait(f, retry, put, n, what):
    """A retry of a KILLED run waits for its clone: -> True (decided, nothing launches) while the run is not finished or
    its return has not given the clone back. row["reap"] asks the tick to run the missing steps."""
    k = (f.get("killed") or {}).get((retry or {}).get("unit"))
    if not k or k.get("returned"):
        return False
    u = retry["unit"]
    if k.get("kept"):
        put("stopped", "%s %s was killed (%s) and its return KEPT its clone" % (what, n, k["why"]),
            "%s %s was killed (%s); its return kept the clone, so the relaunch would be refused: detached_helper.py "
            "return --unit %s (or read what it left), then the next tick relaunches" % (what, n, k["why"], u))
        return True
    if k.get("return_going"):
        put("launch_retry", "%s %s was killed (%s); its return is giving the clone back, then it relaunches" % (
            what, n, k["why"]))
        return True
    put("launch_retry", "%s %s was killed (%s); this tick %s, the next relaunches it" % (
        what, n, k["why"], "finishes it and starts its return" if k.get("state") != "finished" else "starts its return"))
    put.row["reap"] = u
    return True


def spent_tries(x):
    """-> ' N times on a transient fault, the last' for an entry whose transient tries ran out, else ''."""
    if x.get("failed") and not x.get("unit") and AUT.transient(x["failed"]):
        return " %d times on a transient fault, the last" % int(x.get("tries") or 1)
    return ""


def retried(cfg, retry):
    return (", try %d of %d after %s" % (
        len(retry.get("killed_before") or []) + 2 if retry.get("unit") else int(retry.get("tries") or 1) + 1,
        int(cfg.get("launch_tries", 3)),
        "a run killed before it wrote a result (%s)" % retry["unit"] if retry.get("unit")
        else "a failed launch, the pipeline's code having changed since" if code_changed(cfg, retry)
        and not AUT.transient(str(retry.get("failed") or ""))
        else "a launch that never started on a transient fault")) if retry else ""


def cert_put(put, mod, to, why, fix, what):
    if getattr(put, "row", None) is not None:
        put.row["waits_on"] = "its certificate (smallest fix: %s)" % fix
    put("certificate", "waiting on its certificate: %s" % why,
        "%s: waiting on its certificate, which refuses (%s); nothing goes in until `maturation.py certificate %s --to %s` "
        "exits 0. Smallest fix: %s" % (what, why, mod, to, fix))


def cert_wait(f, put, mod, to, what, rerun=None):
    """PRE_JUDGEMENT_CERTIFICATE (RIMMANDRAKE_CERTIFY_BARS_BEFORE_JUDGE_RED_TEST_WENT_IN): True (the row put) when the
    certificate refuses; read before every judge or visit launch, since a mod can go red between cycles. A certificate
    that did not run lets the launch through. RERUN (cfg, s, row, now): a certificate refusing only stale stamps gets
    cert_rerun_decide's one zero-token rerun per build key -> "launch" (row["cert_rerun_key"]) or "decided"
    (RIMMANDRAKE_RERUN_STALE_CERTIFICATE_AT_VISIT_AND_CYCLE_GATES)."""
    cv = f.get("certificate")
    if not isinstance(cv, dict) or cv.get("ok", True):
        return False
    ref = [r for r in cv.get("rows") or [] if r.get("status") == "REFUSED"]
    why = JC.summary(cv) + "".join("; %s/%s %s: %s" % (r["bar"], r["test"], r["clause"], r["observed"]) for r in ref[:2])
    if rerun:
        cfg, s, row, now = rerun
        got = cert_rerun_decide(cfg, s, f, row, put, now, to, what, why, JC.first_fix(cv))
        if got:
            return got
    cert_put(put, mod, to, why, JC.first_fix(cv), what)
    return True


def decide_blind(cfg, s, f, row, put, now, account, live_total, releases=None):
    """One decision for an advancing mod at the blind challenge -> True to launch its judge. The owner's condition, 2026-11-14
    ~9 PM PST: "As long as we don't have automated loops rejecting/cycling things, we can't get into too much trouble."
    So at most blind_auto_cycles_per_visit (1) automatic cycles per visit (a visit is keyed by the version and the visit's
    first cycle number); a cycle already in a cycle_N folder, live, ended under settle_s ago, or worked by a blind run
    that wrote nothing is never launched again; every ended cycle (exit met, not met, or no exit block) is a Needs
    Conductor line, and the program never advances: the steward's confirmation stays a hand step."""
    mod, n = f.get("mod"), f.get("cycle")
    ex = f.get("exit") or {}
    vid = "%s#%s" % (f.get("version"), f.get("visit_first"))
    ours = [x for x in s.get("blind_auto") or [] if x.get("visit_id") == vid]
    row.update(cycle=n, exit=ex.get("state"))
    summ = "%s/SUMMARY.md" % ex.get("record", "the cycle record")
    live = f.get("live_units")
    if not isinstance(live, list):
        put("blind", "the detached-run records could not be read; nothing launches on a blind reading",
            "the run records are unreadable, so the Dispatch step launches nothing on it")
        return False
    if live:
        put("live", "%s is live on it (blind cycle %s)" % (", ".join(live), n))
        return False
    le, settle = f.get("last_end"), float(cfg.get("settle_s", 180))
    if isinstance(le, (int, float)) and 0 <= now - le < settle:
        put("settling", "a run ended %d s ago; blind cycle %s is read %d s after the end, not before" % (now - le, n, settle))
        return False
    owed = f.get("owed")
    if owed == "blocked":
        b = "; ".join(f.get("blocked") or [])
        put("held" if "hold" in b else "blocked", b)
        return False
    if owed == "exit met":
        put("exit_met", "blind cycle %s: exit met (%s)" % (n, (ex.get("why") or ["-"])[0]),
            "blind cycle %s: exit met (a program's reading of %s); the steward reads it and confirms: maturation.py "
            "advance %s --to in_game --steward-confirms \"...\" (a Conductor step; the program never advances)"
            % (n, summ, mod))
        return False
    if owed == "exit not met":
        put("exit_not_met", "; ".join((ex.get("why") or [])[:3]),
            "blind cycle %s ended, exit not met (%s); nothing more launches on it: the Conductor reads %s and decides "
            "(maturation.py advance %s --to blind_challenge opens cycle %s)" % (
                n, "; ".join((ex.get("why") or [])[:3]), summ, mod, (n or 0) + 1))
        return False
    mine = [x for x in ours if x.get("cycle") == n]
    retry = mine[-1] if mine and retriable(cfg, mine[-1], f.get("killed")) else None
    resume = bool(retry and retry.get("unit"))     # a killed judge's half-written cycle is resumed, not unfinished
    if owed == "no exit block" and not resume:
        put("cycle_unfinished", "nothing is live and %s has no exit block" % summ,
            "blind cycle %s has a record (%s) with no exit block and nothing live on it; nothing launches: the "
            "Conductor reads it" % (n, summ))
        return False
    if owed != "cycle" and not (resume and owed == "no exit block"):
        put("blind", "the blind challenge's state cannot be read (%s)" % owed,
            "the blind challenge's state cannot be read (%s); nothing launches" % owed)
        return False
    if mine and not retry:
        x = mine[-1]
        why = ("the automatic launch of cycle %s failed%s: %s" % (n, spent_tries(x), x.get("failed"))
               if x.get("failed") else "the automatic cycle %s (%s) ended and wrote no record" % (n, x.get("unit")))
        put("stopped", why, "stopped, %s; never a second automatic try" % why)
        return False
    per = int(cfg.get("blind_auto_cycles_per_visit", 1))
    dec = f.get("cycle_decision")
    if dec:     # the Conductor's recorded decision opened this cycle: it allows this one, past the visit's count
        row["conductor_decision"] = "%s: %s" % (dec.get("at"), str(dec.get("text"))[:160])
    if len([x for x in ours if x is not retry]) >= per and not dec:
        put("auto_spent", "the visit's %d automatic cycle(s) are spent (cycle %s)" % (
            per, ", ".join(str(x.get("cycle")) for x in ours)),
            "blind cycle %s is open; the Dispatch step runs %d automatic cycle(s) per visit (cycle %s was), so launch "
            "it by hand: maturation.py launch %s --budget-usd <cap> --item <ID>" % (
                n, per, ", ".join(str(x.get("cycle")) for x in ours), mod))
        return False
    hand = [u for u in f.get("blind_runs") or [] if u not in (f.get("killed") or {})]
    if hand:
        put("hand_run_seen", "blind run(s) %s worked on cycle %s and wrote no cycle_%s folder" % (
            ", ".join(hand), n, n),
            "blind run(s) %s worked on cycle %s since it opened and wrote no record; nothing launches: the Conductor "
            "reads what it left" % (", ".join(hand), n))
        return False
    if reap_wait(f, retry, put, n, "blind cycle"):
        return False
    cw = cert_wait(f, put, mod, "blind_challenge", "blind cycle %s" % n, (cfg, s, row, now))
    if cw:
        return cw == "launch"   # a zero-token rerun (row["cert_rerun_key"]) or the certificate's wait
    if not cfg.get("blind_enabled"):
        put("blind_off", "blind_enabled is off in maturation_dispatch.json",
            "blind cycle %s is owed with nothing live; the Dispatch step's blind launches are off" % n)
        return False
    cap = cfg.get("blind_cap_usd")
    if not (isinstance(cap, (int, float)) and not isinstance(cap, bool) and cap > 0):
        put("no_cap", "the settings have no positive blind_cap_usd; no judge launches without a cap")
        return False
    if reserve_refused(cfg, f, row, put, cap, "blind_challenge", s.get("blind_auto"), s, releases,
                       killed=retry["unit"] if resume else None):
        return False
    if not account[0]:
        put("account_hold", account[1])
        return False
    if no_slot(cfg, live_total, put):
        return False
    row.update(cap=cap, visit_id=vid)
    if retry:
        row["retry_of"] = dict(retry)
    put("launch", "blind cycle %s owed, nothing live or recorded on it, the visit's first automatic cycle%s (%s)" % (
        n, retried(cfg, retry), account[1]))
    return True


def decide_ingame(cfg, s, f, row, put, now, account, live_total, drivers, bridge, releases=None, games_of=None):
    """One decision for an advancing mod at in-game acceptance -> True to launch its live driver. At most
    ingame_auto_runs_per_visit (1) automatic runs per visit (keyed by the version and the visit number), one live-game
    driver per game across all mods (drivers: the live in-game runs; games_of: the game each drives, a when unknown),
    only on a FREE game (pick_game: no live driver on it, its own bridge takeable), set as row["game"], and only with
    ingame_enabled true (it ships false: the Conductor runs the first visit by hand). Every ended visit is a Needs
    Conductor line; the program never advances and never takes the bridge itself."""
    mod, n = f.get("mod"), f.get("visit")
    ex = f.get("exit") or {}
    vid = "%s#%s" % (f.get("version"), n)
    ours = [x for x in s.get("ingame_auto") or [] if x.get("visit_id") == vid]
    row.update(visit=n, exit=ex.get("state"))
    summ = "%s/SUMMARY.md" % ex.get("record", "the visit record")
    live = f.get("live_units")
    if not isinstance(live, list):
        put("blind", "the detached-run records could not be read; nothing launches on a blind reading",
            "the run records are unreadable, so the Dispatch step launches nothing on it")
        return False
    if live:
        put("live", "%s is live on it (in-game visit %s)" % (", ".join(live), n))
        return False
    le, settle = f.get("last_end"), float(cfg.get("settle_s", 180))
    if isinstance(le, (int, float)) and 0 <= now - le < settle:
        put("settling", "a run ended %d s ago; in-game visit %s is read %d s after the end, not before" % (
            now - le, n, settle))
        return False
    owed = f.get("owed")
    if owed == "blocked":
        b = "; ".join(f.get("blocked") or [])
        put("held" if "hold" in b else "blocked", b)
        return False
    if owed == "exit met":
        put("exit_met", "in-game visit %s: exit met (%s)" % (n, (ex.get("why") or ["-"])[0]),
            "in-game visit %s: exit met (a program's reading of %s, its build match counting every check on the walk "
            "build); the steward reads it and confirms: maturation.py advance %s --to pre_human --steward-confirms "
            "\"...\" (a Conductor step; the program never advances)"
            % (n, summ, mod))
        return False
    if owed == "exit not met":
        put("exit_not_met", "; ".join((ex.get("why") or [])[:3]),
            "in-game visit %s ended, exit not met (%s); nothing more launches on it: the Conductor reads %s and sends "
            "each failed line item down its road back" % (n, "; ".join((ex.get("why") or [])[:3]), summ))
        return False
    mine = [x for x in ours if x.get("visit") == n]
    retry = mine[-1] if mine and retriable(cfg, mine[-1], f.get("killed")) else None
    resume = bool(retry and retry.get("unit"))     # a killed driver's half-written visit is resumed, not unfinished
    if owed == "no exit block" and not resume:
        put("visit_unfinished", "nothing is live and %s has no exit block" % summ,
            "in-game visit %s has a record (%s) with no exit block and nothing live on it; nothing launches: the "
            "Conductor reads it (and checks the game was left closed or healthy)" % (n, summ))
        return False
    if owed != "run" and not (resume and owed == "no exit block"):
        put("blind", "in-game acceptance's state cannot be read (%s)" % owed,
            "in-game acceptance's state cannot be read (%s); nothing launches" % owed)
        return False
    if mine and not retry:
        x = mine[-1]
        why = ("the automatic launch of in-game visit %s failed%s: %s" % (n, spent_tries(x), x.get("failed"))
               if x.get("failed") else "the automatic in-game visit %s (%s) ended and wrote no record" % (n, x.get("unit")))
        put("stopped", why, "stopped, %s; never a second automatic try" % why)
        return False
    per = int(cfg.get("ingame_auto_runs_per_visit", 1))
    if len([x for x in ours if x is not retry]) >= per:
        put("auto_spent", "the visit's %d automatic run(s) are spent" % per,
            "in-game visit %s is open and its automatic run is spent; launch it by hand: maturation.py launch %s "
            "--budget-usd <cap> --item <ID>" % (n, mod))
        return False
    hand = [u for u in f.get("ingame_runs") or [] if u not in (f.get("killed") or {})]
    if hand:
        put("hand_run_seen", "in-game run(s) %s worked on visit %s and wrote no visit_%s folder" % (
            ", ".join(hand), n, n),
            "in-game run(s) %s worked on visit %s since it opened and wrote no record; nothing launches: the Conductor "
            "reads what it left (and checks the game was left closed or healthy)" % (", ".join(hand), n))
        return False
    if reap_wait(f, retry, put, n, "in-game visit"):
        return False
    cw = cert_wait(f, put, mod, "in_game", "in-game visit %s" % n, (cfg, s, row, now))
    if cw:
        return cw == "launch"   # a zero-token rerun (row["cert_rerun_key"]) or the certificate's wait
    if not cfg.get("ingame_enabled"):
        put("ingame_off", "ingame_enabled is off in maturation_dispatch.json",
            "in-game visit %s is owed; the Dispatch step's live launches are off until the Conductor has run the first "
            "by hand (maturation.py launch %s --budget-usd <cap> --item <ID>, then ingame_enabled true)" % (n, mod))
        return False
    cap = cfg.get("ingame_cap_usd")
    if not (isinstance(cap, (int, float)) and not isinstance(cap, bool) and cap > 0):
        put("no_cap", "the settings have no positive ingame_cap_usd; no live driver launches without a cap")
        return False
    if reserve_refused(cfg, f, row, put, cap, "in_game", s.get("ingame_auto"), s, releases,
                       killed=retry["unit"] if resume else None):
        return False
    if not account[0]:
        put("account_hold", account[1])
        return False
    held = {(games_of or {}).get(u, "a"): u for u in drivers}
    games = (cfg.get("game_instances") or ["a"]) if (bridge is None or M.takes_game(bridge)) else ["a"]
    if all(g in held for g in games):
        put("driver_busy", "an in-game run is live on every game (%s): one live-game driver per game across all mods"
            % ", ".join("game %s: %s" % (g, held[g]) for g in games))
        return False
    if no_slot(cfg, live_total, put):
        return False
    game, whys = pick_game(cfg, bridge, "%s in-game acceptance visit %s" % (mod, n), held)
    if not game:
        put("bridge_held", "no game is free: %s" % "; ".join(whys))
        return False
    row.update(cap=cap, visit_id=vid, game=game)
    if retry:
        row["retry_of"] = dict(retry)
    put("launch", "in-game visit %s owed, nothing live or recorded on it, the visit's automatic run%s, on game %s%s (%s)" % (
        n, retried(cfg, retry), game, " (%s)" % "; ".join(whys) if whys else "", account[1]))
    return True


NAME_MAX_LEN, NAME_MAX_WORDS = 64, 9     # rimflow model's name grammar: `file` refuses anything longer


def free_name(bases, known):
    """-> the first of each base, then each base + _RUN_<N>, that is not in `known` and that rimflow `file` takes
    (64 chars, 9 words at most), or None. A long base is still tried before a short one: its _RUN_<N> was over the
    cap for every N while the short form had room (RIMMANDRAKE_UNSTICK_DISPATCH_CLONE_PUBLISH_LINT_REFUSES_HEAD: Gimme
    Some Slack's visit 1 read "no free item name" with its first item filed)."""
    def fits(n):
        return len(n) <= NAME_MAX_LEN and len(n.split("_")) <= NAME_MAX_WORDS and n not in known
    cands = [b for b in bases] + ["%s_RUN_%s" % (b, ONES[k]) for b in bases for k in range(2, 20)]
    return next((c for c in cands if fits(c)), None)


def ingame_item_id(mod, visit, known):
    """-> a rimflow name for the live driver's item: RIMMANDRAKE_DRIVE_<MOD>_IN_GAME_ACCEPTANCE_VISIT_<N>, else the
    shorter ..._IN_GAME_VISIT_<N>, each with _RUN_<N> once taken."""
    m, n = mod.upper(), word(visit or 0)
    return free_name(["RIMMANDRAKE_DRIVE_%s_IN_GAME_ACCEPTANCE_VISIT_%s" % (m, n),
                      "RIMMANDRAKE_DRIVE_%s_IN_GAME_VISIT_%s" % (m, n), "RIMMANDRAKE_DRIVE_%s_IN_GAME_VISIT" % m], known)


def blind_item_id(mod, cycle, known):
    """-> a rimflow name for the judge's item: RIMMANDRAKE_JUDGE_<MOD>_BLIND_CYCLE_<N>_TESTS_FIRST, else the shorter
    ..._BLIND_CYCLE_<N>, each with _RUN_<N> once taken."""
    m, n = mod.upper(), word(cycle or 0)
    return free_name(["RIMMANDRAKE_JUDGE_%s_BLIND_CYCLE_%s_TESTS_FIRST" % (m, n),
                      "RIMMANDRAKE_JUDGE_%s_BLIND_CYCLE_%s" % (m, n), "RIMMANDRAKE_JUDGE_%s_BLIND_CYCLE" % m], known)


# ---- the acts -------------------------------------------------------------------------------------------------------

def _ingest():
    import importlib.util
    path = os.path.join(REPO, "src", "RimMandrake", "Utils", "testq", "ingest.py")
    spec = importlib.util.spec_from_file_location("maturation_dispatch_ingest", path)
    ing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ing)
    return ing


def file_and_publish(item, title, why, needs="offline", spec=None):
    """Spawn the build item as RUNNER under this item (the way ops_watch files its alarms: DISPATCHER only notes) and
    publish the RUNNER shard, under the dispatch clone's ingest lock; detached_helper refuses an item not filed on
    origin/main. -> (ok, text)."""
    import dispatcher as D
    lk = D.git_lock()
    if lk is None:
        return False, "ingest.lock stayed busy; nothing filed"
    try:
        ing = _ingest()
        rc, out = ing.rimflow("spawn", "--from", ITEM, "--for", "RELENTLESS", "--needs", needs, "--name", item,
                              "--title", title, *(["--spec", spec] if spec else []), "--why", why)
        if rc:
            return False, "spawn refused: %s" % out
        pub = ing.publish(1, message="ledger: maturation dispatch filed %s" % item)
        return True, "filed %s; publish: %s" % (item, str(pub))
    finally:
        lk.close()


def publish_filed(item):
    """Publish the RUNNER shard again for an item filed on an earlier tick whose publish or launch failed on a
    transient fault (a git index.lock): under the same ingest lock as file_and_publish. -> (ok, text); the launch that
    follows tells the truth if the item is still not on origin/main."""
    import dispatcher as D
    lk = D.git_lock()
    if lk is None:
        return False, "ingest.lock stayed busy; nothing published"
    try:
        return True, "publish: %s" % _ingest().publish(0, message="ledger: maturation dispatch filed %s" % item)
    finally:
        lk.close()


def known_items():
    import helper_checkpoint as HC
    return HC.known_items()


def launch_counted(cfg, s, row, now, book, where, new_item, do_file, do_publish, launch):
    """The blind and in-game act: file the item (or, retrying a launch that never started after it was filed, publish
    it again and reuse it), launch, and write ONE book entry for the cycle or visit (a retry replaces its never-started
    entry, so a retry never counts as a second run). -> (ok, item, unit, text, entry)."""
    retry = row.get("retry_of") or {}
    tries = int(retry.get("tries") or 1) + 1 if retry else 1
    if retry.get("item") and retry.get("filed", str(retry.get("failed") or "").startswith("filed ")):
        item, filed = retry["item"], True
        ok, text = do_publish(item)
        text = "retry %d of %s, filed earlier; %s" % (tries, item, text)
    else:
        item = new_item()
        ok, text = do_file(item) if item else (False, "no free item name")
        filed = ok
    unit = None
    if ok:
        rc, text2, unit = launch(item)
        text = "%s; %s" % (text, text2.splitlines()[0] if text2 else rc)
        ok = rc == 0 and bool(unit)
    entry = dict(where, unit=unit if ok else None, item=item, at=now, cap=row.get("cap"), failed=None if ok else text,
                 tries=tries, filed=filed, never_started=not unit)
    if not ok and cfg.get("_code"):
        entry["code"] = cfg["_code"]        # the pipeline code it failed on: retriable() tries again once it changes
    lst = s.setdefault(book, [])
    if retry:
        kb = list(retry.get("killed_before") or []) + ([retry["unit"]] if retry.get("unit") else [])
        if kb:      # a never-started retry carries them on
            entry["killed_before"] = kb
        lst[:] = [x for x in lst if (x.get("unit") and x.get("unit") != retry.get("unit"))
                  or any(x.get(k) != v for k, v in where.items())]
    lst.append(entry)
    return ok, item, unit, text, entry


ROLE_OF_STAGE = {"offline_build": "builder", "blind_challenge": "blind_judge", "in_game": "live_driver"}


READY_TEST = os.path.join(HERE, "acceptance", "modledger_backfill_accept.py")


def ledger_ready(root, mod):
    """-> (ready, its last line): the mod's ledger passes its backfill acceptance (plan step 3; ~0.2 s)."""
    r = subprocess.run([sys.executable, READY_TEST, mod], capture_output=True, text=True, timeout=300,
                       stdin=subprocess.DEVNULL, cwd=root)
    return r.returncode == 0, ((r.stdout or "").strip().splitlines() or ["no output"])[-1]


def pilot_ledger(root, mod):
    """-> True for a pilot mod (modledger.json pilot_mods) whose ledger is ready (ledger_ready): its stage runs start
    from the packet. A half-built ledger (a backfill still running) launches the old way, never from a wrong packet."""
    try:
        return (mod in (modledger.config().get("pilot_mods") or []) and bool(modledger.read(root, mod))
                and ledger_ready(root, mod)[0])
    except Exception:       # noqa: BLE001  an unreadable ledger launches the old way, never not at all
        return False


def ledger_paths(root, mods):
    """-> the DISPATCH shard and every view of each mod's ledger (closed_<version>.md too: landing only the three
    fixed views left a closed view stale on origin/main, RIMMANDRAKE_LAND_EVERY_LEDGER_VIEW_CLOSED_WENT_STALE),
    repo-relative, that exist."""
    out = []
    for mod in mods:
        d = modledger.ledger_dir(root, mod)
        try:
            views = sorted(set(modledger.VIEWS) | set(os.listdir(os.path.join(d, "views"))))
        except OSError:
            views = list(modledger.VIEWS)
        for rel in ["DISPATCH.jsonl"] + ["views/" + v for v in views]:
            if os.path.exists(os.path.join(d, rel)):
                out.append(os.path.relpath(os.path.join(d, rel), root))
    return out


def origin_views(root, mods):
    """Rebuild these mods' views in the root's worktree from origin/main's shards (fetched now) plus the root's own
    DISPATCH shard, so a landed view never drops a peer's shard the root has not pulled
    (RIMMANDRAKE_FIX_DISPATCH_VIEWS_LANDED_BLIND_TO_PEER_SHARDS). No peer shard is written into the root: the shards
    are assembled in a temp dir; only the derived views are rewritten. -> None, or the refusal line (nothing landed).
    A root that is not a clone's top (a selftest) or RM_STAGE_LAND=0 is left as is. A peer landing between this fetch
    and land.sh's push still races (land.sh retries the push but re-lands these views); the next landing repairs it."""
    import shutil
    import tempfile
    if os.environ.get("RM_STAGE_LAND") == "0":
        return None
    try:
        r = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                           timeout=120)
        if r.returncode != 0 or os.path.realpath(r.stdout.strip()) != os.path.realpath(root):
            return None
        f = subprocess.run(["git", "-C", root, "fetch", "-q", "origin", "main"], capture_output=True, text=True,
                           timeout=180)
    except (OSError, subprocess.SubprocessError) as e:
        return "views not landed: fetch failed: %s: %s" % (type(e).__name__, e)
    if f.returncode:
        return "views not landed: git fetch origin main exited %d: %s" % (f.returncode, f.stderr.strip())
    tmp = tempfile.mkdtemp(prefix="dispatch_views_")
    try:
        for mod in mods:
            d = modledger.ledger_dir(root, mod)
            rel = os.path.relpath(d, root).replace(os.sep, "/")
            ls = subprocess.run(["git", "-C", root, "ls-tree", "--name-only", "origin/main", rel + "/"],
                                capture_output=True, text=True, timeout=120)
            td = modledger.ledger_dir(tmp, mod)
            os.makedirs(td)
            for name in ls.stdout.split():
                name = name.rsplit("/", 1)[-1]
                if not name.endswith(".jsonl"):
                    continue
                g = subprocess.run(["git", "-C", root, "show", "origin/main:%s/%s" % (rel, name)],
                                   capture_output=True, timeout=120)
                if g.returncode:
                    return "views not landed: cannot read origin/main:%s/%s" % (rel, name)
                with open(os.path.join(td, name), "wb") as fh:
                    fh.write(g.stdout)
            mine = os.path.join(d, "DISPATCH.jsonl")
            if os.path.exists(mine):
                with open(mine, "rb") as fh:
                    data = fh.read()
                theirs = os.path.join(td, "DISPATCH.jsonl")
                if os.path.exists(theirs):
                    with open(theirs, "rb") as fh:
                        if not data.startswith(fh.read()):
                            return ("views not landed: origin/main's %s/DISPATCH.jsonl is not a prefix of this root's "
                                    "(another Dispatch wrote it): pull before landing" % rel)
                with open(theirs, "wb") as fh:
                    fh.write(data)
            if not modledger.shard_names(tmp, mod):
                continue
            vd = modledger.views_dir(root, mod)
            os.makedirs(vd, exist_ok=True)
            for name, text in modledger.render_views(tmp, mod).items():
                p = os.path.join(vd, name)
                with open(p + ".tmp%d" % os.getpid(), "w", encoding="utf-8") as fh:
                    fh.write(text)
                os.replace(p + ".tmp%d" % os.getpid(), p)
    except (OSError, subprocess.SubprocessError, modledger.ModLedgerError) as e:
        return "views not landed: %s: %s" % (type(e).__name__, e)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return None


def land_ledger(root, mods, what, fx=None):
    """Land the DISPATCH shard and views of these mods' ledgers (land.sh, as land_spend does). The views landed are
    rebuilt from origin/main's shards plus this root's DISPATCH shard first (origin_views)."""
    if (fx or {}).get("land_ledger"):
        paths = ledger_paths(root, mods)
        return fx["land_ledger"](paths) if paths else "nothing to land"
    if not (fx or {}).get("land_spend"):
        refused = origin_views(root, mods)
        if refused:
            return refused
    paths = ledger_paths(root, mods)
    if not paths:
        return "nothing to land"
    return land_spend(root, paths, dict(fx or {}, land_msg="modledger: %s (Dispatch step)" % what))


def ledger_open(root, mod, role, brief, stage=None, now=None, fx=None):
    """A pilot holder's run begins: modledger.launch grants the lease and records run.start, and the ledger lands
    before any launch cuts the holder's clone from origin/main (RIMMANDRAKE_LAND_HOLDER_GRANT_BEFORE_LAUNCH_CLONE_BLIND:
    landed after, the clone lacks its own grant and the holder's first append is refused "lease never granted");
    -> {"brief": the packet and holder lines, then `brief`, "env": the unit's RM_MODLEDGER_WRITER/TOKEN, "run",
    "stage", "landed"}."""
    now = now or time.time()
    lease = "run-%d" % int(now)
    out = modledger.launch(root, mod, lease, role, stage=stage)
    landed = land_ledger(root, [mod], "run %s on %s granted" % (lease, mod), fx)
    return {"run": lease, "stage": out["stage"], "packet": out["brief"], "landed": landed,
            "brief": out["brief"].rstrip("\n") + "\n\n" + renew_line(mod, out["writer"], out["token"]) + (
                "\n\n---\n\n" + brief if brief else ""),
            "env": {"RM_MODLEDGER_WRITER": out["writer"], "RM_MODLEDGER_TOKEN": str(out["token"])}}


def renew_line(mod, writer, token):
    """-> the holder's lease-renewal instruction: a lease idle past lease_idle_minutes lapses, and every later append,
    the closing checkpoint included, is refused (GimmeSomeSlack blind cycle 5, 2026-11-16 1:03 AM PST)."""
    idle = modledger.config()["lease_idle_minutes"]
    return ("Your lease lapses after %d minutes with no append from you, and then every append is refused, your closing "
            "checkpoint included. Renew it at least every %d minutes of work (and before a long build or test):\n\n"
            "    python3 src/RimMandrake/rimflow/modledger.py append --mod %s --writer %s --token %d --kind lease.renew "
            "--subject lease" % (idle, max(5, idle * 2 // 3), mod, writer, token))


JUDGE_ME = "python3 src/RimMandrake/rimflow/modledger.py"


def judge_open(root, mod, stage=None, now=None, fx=None):
    """A blind judge's run on a pilot mod begins (spec §3.6): DISPATCH records run.start naming role blind_judge and the
    writer JUDGE.<run>; no holder lease is granted (a judge holds none, so none lapses), and the brief carries NO ledger
    packet: the judge is told nothing an earlier judge or the holder found. It writes its findings and its verdicts on
    claimed fixes to its own shard, sealed at its end (end_ledger_runs). The ledger lands before the launch, as a
    holder's grant does. -> the dict ledger_open returns, with "judge": True and "writer"."""
    now = now or time.time()
    run = "judge-%d" % int(now)
    w = "JUDGE.%s" % run
    lines = judge_lines(mod, run, stage)
    modledger.append(root, mod, "DISPATCH", "run.start", "run", run=run,
                     body={"run": run, "role": "blind_judge", "writer": w, "stage": stage,
                           "packet_tokens": modledger.tokens(lines)})
    landed = land_ledger(root, [mod], "judge run %s on %s started" % (run, mod), fx)
    return {"run": run, "stage": stage, "packet": lines, "landed": landed, "brief": lines, "judge": True,
            "writer": w, "env": {"RM_MODLEDGER_WRITER": w}}


def judge_lines(mod, run, stage):
    w = "JUDGE.%s" % run
    a = "%s append --mod %s --writer %s --run %s" % (JUDGE_ME, mod, w, run)
    return "\n".join([
        "## You judge %s blind: run %s, stage %s; you write the mod ledger as `%s`" % (mod, run, stage or "-", w), "",
        "You hold no lease and are not the mod's holder. You are told nothing an earlier judge or the holder found: "
        "until your lane 1 is recorded, do not open `design/concepts/%s/ledger/` (its shards and views) and do not run "
        "`modledger.py packet`, `find`, `show` or `since` on %s." % (mod, mod), "",
        "**Discovery (blind).** Each fault you find goes in as you find it, with the precise fix you would make (it goes "
        "back to the holder fully informed):", "",
        "    %s --kind finding.open --subject finding:<NAME> --text \"<what fails>\" \\" % a,
        "      --fix \"<file: the change>\" --accept \"<command and its expected result>\" --bars <ids> "
        "--evidence <ref>", "",
        "**Verification (after your lane 1 is recorded).** Only then print the findings the holder claims fixed (each "
        "finding's text, reproduction and the claim's test, never the holder's story):", "",
        "    python3 src/RimMandrake/rimflow/maturation_dispatch.py judge-verify %s" % mod, "",
        "and rule on each, against the commit you judged:", "",
        "    %s --kind finding.verified --subject <finding> --code-sha <sha> --text \"<how you checked>\"" % a,
        "    %s --kind finding.reopened --subject <finding> --code-sha <sha> --text \"<what still fails>\"" % a, "",
        "Tests you run go in as `--kind test.run` (result, command). Your shard is sealed when your run ends: write "
        "every verdict before you stop."])


def judge_verify_text(root, mod):
    """-> `judge-verify MOD`: the mod's findings the holder claims fixed, for a judge's verification phase: each one's
    finding text, its accept command, its bars and the test the claim names, never the claim's text (the holder's
    story, spec §3.6). 'none' when there are none."""
    events = modledger.read(root, mod)
    st = modledger.reduce(events)
    tests = {}
    for e in events:
        if e.get("kind") == "finding.claimed_fixed":
            tests[e.get("subject")] = (e.get("body") or {}).get("test")
    out = ["# %s: findings claimed fixed, to verify (judge-verify)" % mod, ""]
    n = 0
    for subj, f in sorted((st.get("findings") or {}).items()):
        if f.get("status") != "claimed_fixed":
            continue
        n += 1
        out += ["- `%s` (%s; bars %s)" % (subj, f.get("class") or "-", ", ".join(f.get("bars") or []) or "none"),
                "  finding: %s" % f.get("text"), "  reproduce: %s" % (f.get("accept") or "none recorded"),
                "  the claim's test: %s" % (tests.get(subj) or "none named"),
                "  claimed at code %s" % (f.get("code_sha") or UNM)]
    out.append("" if n else "none: no finding is claimed fixed")
    return "\n".join(out) + "\n"


def ledger_after(root, st, mod, led, unit, item, now, fx=None):
    """After the launch: remember a started run for its end (end_ledger_runs), or record run.end at once for one that
    never started; land the ledger. -> one line for the launch text."""
    if unit:
        st.setdefault("mods", {}).setdefault(mod, {}).setdefault("ledger_runs", []).append(
            {"run": led["run"], "unit": unit, "item": item, "at": now, "stage": led["stage"],
             "writer": led.get("writer") or led["env"].get("RM_MODLEDGER_WRITER")})
    elif led.get("judge"):
        end_judge_run(root, mod, led["run"], "never_started")
    else:
        modledger.end_run(root, mod, led["run"], "never_started")
    land_ledger(root, [mod], "run %s on %s %s" % (led["run"], mod, "started" if unit else "never started"), fx)
    return "ledger run %s (packet %d tokens)" % (led["run"], modledger.tokens(led["packet"]))


def launch_stage(root, cfg, st, mod, cap, item, now=None, fx=None, launch=None, **kw):
    """The Dispatch step's stage launch. A pilot mod's run starts from its ledger (plan step 5): modledger.launch grants
    the holder lease and records run.start at the stage the mod stands at, the brief opens with the packet, then the
    stage's own brief, and the unit carries RM_MODLEDGER_WRITER=HOLDER.<lease>; a launch that never started records
    its run.end at once. Any other mod launches as before. -> (rc, text, unit)."""
    launch = launch or M.launch_mod
    stage = (M.load(root, mod) or {}).get("stage")
    model = cfg.get("ingame_model", "opus") if stage == "in_game" else cfg.get("model", "opus")
    if not pilot_ledger(root, mod):
        return launch(root, mod, cap, item, seat=cfg.get("seat", "BENCH"), model=model, **kw)
    now = now or time.time()
    try:
        if stage == "blind_challenge":      # a judge is never the holder: it writes JUDGE.<run>, blind (spec §3.6)
            led = judge_open(root, mod, stage=stage, now=now, fx=fx)
        else:
            led = ledger_open(root, mod, ROLE_OF_STAGE.get(stage, "holder"), "", stage=stage, now=now, fx=fx)
    except Exception as e:      # noqa: BLE001  a refused grant is a launch that never started, said in its words
        return 2, "REFUSED: %s's ledger launch failed: %s: %s" % (mod, type(e).__name__, e), None
    game = kw.pop("game", None)
    rc, text, unit = launch(root, mod, cap, item, seat=cfg.get("seat", "BENCH"), model=model, preface=led["brief"],
                            env=dict(led["env"], **({"RM_GAME_INSTANCE": game} if game else {})), **kw)
    unit = unit if rc == 0 else None
    return rc, "%s; %s" % (text, ledger_after(root, st, mod, led, unit, item, now, fx)), unit


def live_units_on(root, mod):
    """-> the units maturation_now places on `mod` that are live, or UNM when the run records cannot be read."""
    try:
        g = MN.gather(root, live=True)
    except Exception as e:      # noqa: BLE001  an unreadable record is a refusal, said, never a launch
        return "%s: %s" % (UNM, type(e).__name__)
    m = next((x for x in g.get("mods") or [] if x.get("name") == mod), None)
    runs = (m or {}).get("runs", [] if m is None else UNM)
    return [r["unit"] for r in runs if r.get("live") and r.get("unit")] if isinstance(runs, list) else UNM


def pilot_launch(root, cfg, mod, why, item=None, usd=None, fx=None, now=None):
    """`pilot-launch MOD`: start one pilot holder run from the ledger packet at the stage the mod stands at, through
    the Dispatch step's own launches (the Conductor's act, on a mod the tick has paused or not reached). Refuses a mod
    that is not a pilot, a ledger its backfill acceptance does not pass, and a mod owing nothing launchable. At a
    stage with work owed (a build, a blind cycle, a visit) it is that stage's launch for `item` (required: a filed
    item); on an open road back whose fixers are spent it is one holder run on all the open road-back items together
    (`item` or the first of them). -> (rc, text)."""
    fx = fx or {}
    now = now or time.time()
    if mod not in (modledger.config().get("pilot_mods") or []):
        return 2, "REFUSED: %s is not a pilot mod (modledger.json pilot_mods)" % mod
    ok, line = (fx.get("ready") or ledger_ready)(root, mod)
    if not ok:
        return 2, "REFUSED: %s's ledger is not ready: %s (%s)" % (mod, line, READY_TEST)
    cap = usd or cfg["cap_usd"]
    with state_lock():
        p = os.path.join(sdir(), "state.json")
        st = read_state(p)
        s = st.setdefault("mods", {}).setdefault(mod, {})
        # one run per mod: the tick launched GimmeSomeSlack's cycle-6 judge at 01:53 PST 2026-11-16 and a hand
        # pilot-launch started a second on the same cycle at 01:54 (RIMMANDRAKE_DISPATCH_PILOT_HOLDER_RUN_ITSELF_HAND_
        # LAUNCHED_TWICE)
        rec_of = fx.get("record") or DH.read_record
        live = [r["unit"] for r in s.get("ledger_runs") or [] if r.get("unit") and not r.get("ended")
                and (rec_of(r["unit"]) or {}).get("status") != "finished"]
        if live:
            return 2, ("REFUSED: %s already has a ledger run live (%s); one run per mod. Its end is recorded by the "
                       "tick, which launches what is owed next" % (mod, ", ".join(live)))
        _, f = M.brief_text(root, mod, cap)
        stage, owed = f.get("stage"), f.get("owed")
        rb = s.get("road_back")
        opened = (fx.get("open_items") or (lambda ids: M.ledger_items_caused_by(root, ids)))(
            AUT._road_back_ids(s, rb)) if rb else []
        if owed == "build" or (stage in ("blind_challenge", "in_game") and owed in ("cycle", "run")):
            if not item:
                return 2, "REFUSED: %s owes %s at %s; name the filed item it runs under: --item <ID>" % (mod, owed, stage)
            if stage in ("blind_challenge", "in_game"):
                # one judge per cycle, one driver per visit: a run the tick launched a moment ago has not written its
                # cycle_N folder yet, so "owed" still reads open (RIMMANDRAKE_GUARD_PILOT_LAUNCH_TWO_JUDGES_ONE_CYCLE)
                live = (fx.get("live_units") or live_units_on)(root, mod)
                if not isinstance(live, list) or live:
                    return 2, ("REFUSED: %s at %s: %s; a second %s on the same %s is never started (stop it first, "
                               "or wait for its end)" % (
                                   mod, stage, "run(s) %s are live on it" % ", ".join(live) if isinstance(live, list)
                                   else "the run records cannot be read (%s), so nothing launches on a blind reading" % live,
                                   "judge" if stage == "blind_challenge" else "driver",
                                   "cycle" if stage == "blind_challenge" else "visit"))
            gkw = {}
            if stage == "in_game":      # a free game of the two, never "waiting for game" while one is free
                game, whys = pick_game(cfg, fx.get("bridge"), "%s in-game visit (pilot-launch)" % mod)
                if not game:
                    return 2, "REFUSED: %s at in_game: no game is free: %s" % (mod, "; ".join(whys))
                gkw["game"] = game
            rc, text, unit = launch_stage(root, cfg, st, mod, cap, item, now, fx, launch=fx.get("launch"), **gkw)
        elif opened:
            rc, text, unit, item = road_back_holder(root, cfg, st, mod, stage, opened, item, cap, now, fx)
            if rc is None:      # refused before any launch
                return 2, text
        else:
            return 2, "REFUSED: %s owes nothing launchable at %s (%s) and has no open road-back item" % (mod, stage, owed)
        s.setdefault("pilot_launches", []).append({"at": now, "item": item, "unit": unit, "why": why, "stage": stage})
        _write(p, st)
    return (0 if unit else 1), "%s %s: %s" % ("LAUNCHED" if unit else "NOT STARTED", mod, text)


def road_back_holder(root, cfg, st, mod, stage, opened, item, cap, now, fx):
    """One pilot holder run on every open road-back item together (`opened`, [{id, needs}]), from the ledger packet:
    pilot-launch's road back, and the tick's once the fixers are spent (pilot_holders). Items only the live game can
    show get no run at an offline stage; at Stage 6 a live-only set gets the live brief when the bridge is takeable.
    -> (rc, text, unit, item); rc None is a refusal before any launch, said in its words, nothing booked. Booked in s["holder_road_back"] with
    the item set it ran on (holder_spent reads it)."""
    have = M.ledger_needs(root, [x["id"] for x in opened if not x.get("needs")])
    opened = [dict(x, needs=x.get("needs") or have.get(x["id"])) for x in opened]
    # offline stages never wait for a game: at one, an item only the game can show is Stage 6 work, given no
    # run here (RIMMANDRAKE_CLOSE_OFFLINE_STAGE_ITEMS_OFFLINE_GAME_WAS_DEMANDED)
    game6 = [x["id"] for x in opened if x["needs"] in M.LIVE_NEEDS] if not M.game_takeable(stage) else []
    ids = [x["id"] for x in opened if x["id"] not in game6]
    if not ids:
        return None, ("REFUSED: %s stands at %s, an offline stage, and every open road-back item (%s) needs the "
                   "live game: no offline run can close one, and none is given the game. They are Stage 6 "
                   "work; return the record there: %s" % (mod, stage, ", ".join(game6),
                                                          M.game_only_cmd(mod, game6))), None, item
    item = item if item and item not in game6 else ids[0]
    # at Stage 6, every open item needs the live game: the holder takes the bridge and the game, one holder at a
    # time (RIMMANDRAKE_LET_HOLDER_TAKE_BRIDGE_ALL_ITEMS_NEED_GAME)
    live = M.game_takeable(stage) and AUT.live_only(opened)
    game = None
    if live:        # a free game of the two (pick_game), its bridge takeable; none free is a refusal with each reason
        game, whys = pick_game(cfg, fx.get("bridge"), "%s live holder run" % mod)
        if not game:
            return None, ("REFUSED: %s's open items all need the live game and no game is free (%s); "
                          "one bridge holder per game" % (mod, "; ".join(whys))), None, item
    plan = modledger.resume_plan(root, mod)     # the holder's recorded session is resumed, not restarted
    rkw = {"session": plan["session_id"]} if plan.get("action") == "resume" and plan.get("session_id") else {}
    led = ledger_open(root, mod, "fixer", AUT.fixer_brief(item, mod, cap, live=live) + (
        "\nReconcile first: %s.\n" % plan["why"] if plan.get("reconcile") else "") + (
        "\nThis is the mod's %sholder run: work every open road-back item together, from the packet above: %s. "
        "Close each one its acceptance test passes; a note starting LEFT OPEN: on each that is not.\n"
        % ("live " if live else "", ", ".join(ids)) + (
        "Not yours: %s need%s the live game, Stage 6 work; work none of them here.\n" % (
            ", ".join(game6), "s" if len(game6) == 1 else "") if game6 else "") + (
        "\n" + M.game_brief(game) if game else "")), stage=stage, now=now, fx=fx)
    rc, text, unit = (fx.get("launch_brief") or AUT.launch_brief)(
        item, led["brief"], cfg.get("steward_model", "opus"), cap, cfg.get("seat", "BENCH"),
        env=dict(led["env"], **({"RM_GAME_INSTANCE": game} if game else {})), **rkw)
    unit = unit if rc == 0 else None
    text = "%s%s%s; %s" % ("live holder (bridge and game allowed): " if live else "",
                           "%s; " % plan["why"] if rkw else "",
                           (text or "").splitlines()[0] if text else rc,
                           ledger_after(root, st, mod, led, unit, item, now, fx))
    st.setdefault("mods", {}).setdefault(mod, {}).setdefault("holder_road_back", []).append(
        {"at": now, "ids": sorted(ids), "item": item, "unit": unit, "stage": stage})
    return rc, text, unit, item


def holder_spent(s, open_ids):
    """-> why no automatic holder run goes on these open road-back items, or None. The last holder run on the road back
    (the tick's or a hand pilot-launch since it opened) ran on a set of items; it ended with those still open (the
    set did not shrink) or it never started: never a second automatic try at the same items. A hand launch recorded
    before the set was booked counts as having run on today's open set plus its own item."""
    rb = s.get("road_back") or {}
    t0 = rb.get("at") if isinstance(rb.get("at"), (int, float)) else 0
    runs = [dict(x, ids=x["ids"]) for x in s.get("holder_road_back") or [] if (x.get("at") or 0) >= t0]
    runs += [dict(x, ids=sorted(set(open_ids) | {x.get("item")}), hand=True) for x in s.get("pilot_launches") or []
             if (x.get("at") or 0) >= t0 and x.get("item") and not any(
                 abs((y.get("at") or 0) - (x.get("at") or 0)) < 1 for y in s.get("holder_road_back") or [])]
    if not runs:
        return None
    last = max(runs, key=lambda x: x.get("at") or 0)
    if not last.get("unit"):
        return "the last holder run on them (%s) never started" % last.get("item")
    if set(open_ids) < set(last["ids"]):
        return None
    return "%sholder run %s on %s ended with them still open" % ("the hand " if last.get("hand") else "the ",
                                                                  last.get("unit"), ", ".join(last["ids"]))


def pilot_holders(root, cfg, st, facts, rows, launches, now, fx=None):
    """After the autonomy layer: a PILOT mod whose road-back fixers are spent (fixer_spent), whose ledger is ready
    (pilot_ledger) and with nothing live on it gets ONE holder run on every open road-back item together, from the
    tick (it was the Conductor's `pilot-launch` by hand on 2026-11-15/16: Explosive Knockback and FlowWorks). Another
    only once the open set has shrunk (holder_spent); within max_live and the account gate; a non-pilot is untouched.
    -> (rows, launches); a launched row carries holder_items and no aut, so execute starts it."""
    fx = fx or {}
    open_items = fx.get("open_items", lambda ids: M.ledger_items_caused_by(root, ids))
    account = fx["account"]() if "account" in fx else account_gate()
    base = occupancy(facts)
    for row in rows:
        mod = row["mod"]
        s = st.setdefault("mods", {}).setdefault(mod, {})
        if row.get("decision") != "fixer_spent" or not s.get("road_back") or (facts.get(mod) or {}).get("live_units"):
            continue
        # only the launches ahead of it on the advancing list count against it: a later mod's launch is evicted by
        # prioritise, never the other way round (RIMMANDRAKE_LAUNCH_PYRELANDS_FIRST_AT_ONE_SLOT)
        planned = None if base is None else base + slots_ahead(rows, launches, mod)
        if not (fx.get("pilot") or pilot_ledger)(root, mod):
            continue
        items = open_items(AUT._road_back_ids(s, s["road_back"]))
        if not items:
            continue
        ids = sorted(x["id"] for x in items)

        def put(decision, why, need=None):
            row.update(decision=decision, why=why, aut=None)
            if need:
                row["need"] = "%s: %s" % (mod, need)
        spent = holder_spent(s, ids)
        if spent:
            put("holder_spent", spent, "PAUSED, %s; the pipeline gives one holder run per set of open road-back items "
                "(pilot-launch %s --why ... starts another by hand)" % (spent, mod))
            continue
        if not account[0]:
            put("account_hold", account[1])
            continue
        if no_slot(cfg, planned, put):
            continue
        row.update(holder_items=items, cap=cfg.get("cap_usd"))
        put("launch", "its road-back fixers are spent and its ledger is ready: one holder run on all %d open items "
            "(%s), nothing live on it (%s)" % (len(ids), ", ".join(ids), account[1]))
        launches = [m for m in launches if m != mod] + [mod]
    return rows, launches


NO_SLOT_AUT = ("autolock", "autorepin")     # the pipeline's acts on a concept, not runs: they take no slot


def takes_slot(row):
    """True when ROW's launch takes a run slot: a zero-token certificate rerun and the pipeline's acts take none."""
    return not row.get("cert_rerun_key") and row.get("aut") not in NO_SLOT_AUT


def slots_ahead(rows, launches, mod):
    """-> the slot-taking launches in LAUNCHES on mods ahead of MOD in ROWS (ROWS run in advancing-list order)."""
    order = [r["mod"] for r in rows]
    cut = order.index(mod) if mod in order else len(order)
    return sum(1 for r in rows[:cut] if r["mod"] in launches and takes_slot(r))


def prioritise(cfg, st, facts, rows, launches, root=None):
    """Launch priority is the advancing list's order across every layer (item
    RIMMANDRAKE_LAUNCH_PYRELANDS_FIRST_AT_ONE_SLOT; the owner by card 2026-11-17, "Which mod gets the next run" ->
    "Pyrelands"). decide grants slots in list order, but the steward and fixer runs maturation_autonomy.resolve adds
    were gated on every launch of the tick, a later mod's included: at max_live 1 a later mod's build or blind cycle
    took the slot from an earlier mod's fixer (measured 2026-11-17). One pass, in list order: a mod whose run just
    ended (settling, read again in settle_s) keeps its slot; a steward or fixer run refused only for a slot a later
    mod took is granted again; a launch past max_live is put back to slots_full. -> launches."""
    base = occupancy(facts)
    if base is None:
        return launches
    most = int(cfg.get("max_live", 2))
    taken, ahead = base, []
    for row in rows:
        mod = row["mod"]
        if mod in launches:
            if not takes_slot(row):
                continue
            if taken < most:
                taken += 1
                ahead.append(mod)
                continue
            launches = [m for m in launches if m != mod]
            row.update(decision="slots_full", aut=None, waits_on="a free slot%s" % (
                " (launch priority: %s first)" % ", ".join(ahead) if ahead else ""),
                why="%d live runs on advancing mods%s, the most is %d; it was: %s" % (
                    base, " plus %s ahead of it on the advancing list (launch priority)" % ", ".join(ahead)
                    if ahead else "", most, row.get("why")))
            continue
        if row.get("decision") == "settling" and not (facts.get(mod) or {}).get("live_units"):
            if taken < most:
                taken += 1
                ahead.append("%s (settling)" % mod)
            continue
        w = str(row.get("waits_on") or "")
        aut = next((a for a in ("fixer", "steward") if w.startswith("a free slot for the %s run" % a)), None)
        if row.get("decision") == "slots_full" and aut and taken < most:
            s = st.setdefault("mods", {}).setdefault(mod, {})
            f = facts.get(mod) or {}
            ver = f.get("version") or ((M.load(root, mod) or {}).get("version") if root else None)
            trial = dict(row, aut=aut)
            ok, why = AUT._gate(cfg, s, trial, taken, ver)
            if ok:
                trial.pop("waits_on", None)
                trial.update(decision=aut, why="its %s run on %s, first on the advancing list for the slot%s" % (
                    aut, trial.get("fix_item") or trial.get("steward_kind"),
                    "; it was for: %s" % trial["steward_why"] if trial.get("steward_why") else ""))
                row.clear()
                row.update(trial)
                taken += 1
                ahead.append(mod)
                launches = launches + [mod]
    return launches


def end_ledger_runs(root, st, facts, now, fx=None):
    """A pilot run whose unit has ended -> its run.end, with the run record's result and the flags
    (modledger.end_run: NO_CHECKPOINT when its holder wrote none). -> {mod: ["<run> <status> <flags>"]}."""
    fx = fx or {}
    rec_of = fx.get("record") or DH.read_record
    out, mods = {}, []
    for mod, s in (st.get("mods") or {}).items():
        for r in s.get("ledger_runs") or []:
            if r.get("ended"):
                continue
            rec = rec_of(r["unit"]) or {}
            done = {x.get("unit") for x in (facts.get(mod) or {}).get("ended_runs") or []}
            if rec.get("status") != "finished" and r["unit"] not in done:
                continue
            status = rec.get("result") or rec.get("status") or "ended"
            judge = str(r.get("writer") or "").startswith("JUDGE.")
            try:
                flags = end_judge_run(root, mod, r["run"], status) if judge else modledger.end_run(
                    root, mod, r["run"], status)
            except Exception as e:      # noqa: BLE001  said in the reading; the next tick tries again
                out.setdefault(mod, []).append("%s: run.end failed: %s: %s" % (r["run"], type(e).__name__, e))
                continue
            r.update(ended=now, status=status, flags=flags)
            if judge:       # a judge's session is never the holder's: the next holder never resumes a judge
                out.setdefault(mod, []).append("%s %s %s" % (r["run"], status, ",".join(flags) or "sealed"))
                mods.append(mod)
                continue
            try:        # Option B: the holder's session, resumed by the next launch (holder_launch)
                r["session"] = record_holder_session(root, mod, r, fx)
            except Exception as e:      # noqa: BLE001  said in the reading; the next launch starts from the packet
                r["session"] = "session.id failed: %s: %s" % (type(e).__name__, e)
            out.setdefault(mod, []).append("%s %s %s" % (r["run"], status, ",".join(flags) or "checkpointed"))
            mods.append(mod)
    if mods:
        out["_land"] = land_ledger(root, sorted(set(mods)), "run.end of ended pilot runs", fx)
    return out


def end_judge_run(root, mod, run, status):
    """A judge run's end: DISPATCH seals JUDGE.<run> (its hash and lines) and records run.end. -> its flags: NO_VERDICTS
    when the shard holds nothing (a judge holds no lease and writes no checkpoint, so NO_CHECKPOINT never applies)."""
    seal_id = modledger.seal(root, mod, run, views=False)
    lines = [e for e in modledger.read(root, mod) if e.get("_shard") == "JUDGE.%s" % run]
    flags = [] if lines else ["NO_VERDICTS"]
    modledger.append(root, mod, "DISPATCH", "run.end", "run", run=run,
                     body={"run": run, "writer": "JUDGE.%s" % run, "status": str(status), "flags": flags,
                           "sealed": seal_id})
    return flags


def execute(root, cfg, st, rows, launches, now, fx=None):
    fx = fx or {}
    do_file = fx.get("file", file_and_publish)
    do_publish = fx.get("publish", publish_filed)
    do_launch = fx.get("launch", lambda mod, cap, item, **kw: launch_stage(root, cfg, st, mod, cap, item, now, fx, **kw))
    known = fx["known"]() if "known" in fx else known_items()

    def launch_holder(mod, s, row, cap, item, **kw):     # a pilot mod's run is its holder (holder_launch)
        hcap, hkw = holder_launch(root, cfg, s, row, cap, fx)
        if kw.get("game") == "a" and not _takes(do_launch, "game"):     # a one-game launcher: game a is its only game
            kw.pop("game")
        return do_launch(mod, hcap, item, **dict(hkw, **kw))
    done = []
    for row in rows:
        if row["mod"] not in launches:
            continue
        mod, s = row["mod"], st["mods"][row["mod"]]
        blind = row.get("stage") == "blind_challenge"
        if row.get("holder_items"):     # pilot_holders: one holder run on the open road-back items
            rc, text, unit, item = road_back_holder(root, cfg, st, mod, row.get("stage"), row["holder_items"], None,
                                                    row.get("cap") or cfg["cap_usd"], now, fx)
            if unit:
                s.setdefault("launches", []).append({"unit": unit, "item": item, "at": now, "cap": row.get("cap"),
                                                     "stage": row.get("stage"), "holder": True})
                row.update(decision="launched", unit=unit, item=item, why=text)
                done.append(row)
            else:
                row.update(decision="launch_failed", why=text, need="%s: the holder run on its road-back items did not "
                           "start (%s); never retried on its own" % (mod, text))
            continue
        if row.get("cert_rerun_key"):   # stale stamps only: one zero-token certificate rerun (cert_rerun_launch)
            if cert_rerun_launch(cfg, st, row, now, fx):
                done.append(row)
            continue
        if row.get("cert_reds"):        # red deciders: their items and one builder (cert_launch)
            if cert_launch(root, cfg, st, row, now, fx, known, do_file):
                done.append(row)
            continue
        if row.get("stage") == "in_game":
            title = ("%s Stage 6: in-game acceptance visit %s, one live driver on the bridge (launched by the Dispatch "
                     "step)" % (mod, row.get("visit")))
            why = ("delegated: maturation_dispatch.py; in-game visit %s is owed (no visit_%s folder), nothing live or "
                   "recorded on it, no other live-game driver, the bridge takeable, measured %s" % (
                       row.get("visit"), row.get("visit"), pac(now)))
            # launched or failed, it is the visit's automatic run (the owner's condition), unless it never started on a
            # transient fault: then the next tick tries the same item again, up to launch_tries
            ok, item, unit, text, entry = launch_counted(
                cfg, s, row, now, "ingame_auto", {"visit_id": row.get("visit_id"), "visit": row.get("visit")},
                lambda: ingame_item_id(mod, row.get("visit"), known),
                lambda it: do_file(it, title, why, needs="game-up"), do_publish,
                lambda it: launch_holder(mod, s, row, row["cap"], it, **dict(resume_kw(row), game=row.get("game", "a"))))
            if ok:
                row.update(decision="launched", unit=unit, item=item, why=text)
                known.add(item) if isinstance(known, set) else None
                done.append(row)
            elif retriable(cfg, entry):
                row.update(decision="launch_retry", why="the in-game launch never started on a transient fault (try %d "
                           "of %d), the next tick tries it again: %s" % (entry["tries"], int(cfg.get("launch_tries", 3)),
                                                                         text))
            else:
                row.update(decision="launch_failed", why=text,
                           need="%s: the in-game launch failed%s (%s); the step will not retry it on its own" % (
                               mod, spent_tries(entry), text))
            continue
        if blind:
            item = blind_item_id(mod, row.get("cycle"), known)
            title = ("%s Stages 4 and 5: blind challenge cycle %s, tests first, offline (launched by the Dispatch step)"
                     % (mod, row.get("cycle")))
            why = ("delegated: maturation_dispatch.py; blind cycle %s is owed (no cycle_%s folder), nothing live or "
                   "recorded on it, the visit's first automatic cycle, measured %s" % (
                       row.get("cycle"), row.get("cycle"), pac(now)))
        else:
            item = item_id(mod, row["refused"], known)
            nb = len([i for i in row["refused_ids"] if i != "table_version"])
            title = ("%s Stage 3: build the checks for %s bars not runnable, offline (launched by the Dispatch step)"
                     % (mod, "%d of the %d" % (len(row["batch"]), nb) if row.get("batch") else "the %d" % row["refused"]))
            why = ("delegated: maturation_dispatch.py; maturation.py refuses %d bars as build work (%s), nothing live on "
                   "it, measured %s" % (row["refused"], ", ".join(row["refused_ids"][:12]), pac(now)))
        if blind:
            # launched or failed, it is the visit's automatic cycle (the owner's condition), unless it never started on
            # a transient fault: then the next tick tries the same item again, up to launch_tries
            ok, item, unit, text, entry = launch_counted(
                cfg, s, row, now, "blind_auto", {"visit_id": row.get("visit_id"), "cycle": row.get("cycle")},
                lambda: item, lambda it: do_file(it, title, why), do_publish,
                lambda it: launch_holder(mod, s, row, row["cap"], it, **resume_kw(row)))
            if ok:
                row.update(decision="launched", unit=unit, item=item, why=text)
                known.add(item) if isinstance(known, set) else None
                done.append(row)
            elif retriable(cfg, entry):
                row.update(decision="launch_retry", why="the blind launch never started on a transient fault (try %d "
                           "of %d), the next tick tries it again: %s" % (entry["tries"], int(cfg.get("launch_tries", 3)),
                                                                         text))
            else:
                row.update(decision="launch_failed", why=text,
                           need="%s: the blind launch failed%s (%s); the step will not retry it on its own" % (
                               mod, spent_tries(entry), text))
            continue
        # a Stage 3 launch that never started on a transient fault (a git lock, its item not yet on origin/main) retries
        # the same item on the next tick, up to launch_tries, like the blind and in-game launches
        # (RIMMANDRAKE_RETRY_STAGE_THREE_LAUNCH_TRANSIENT_FAULT_NOT_STOPPED)
        retry = s.get("launch_retry") if isinstance(s.get("launch_retry"), dict) else {}
        if retry.get("refused") != row["refused"]:
            retry = {}
        tries = int(retry.get("tries") or 0) + 1
        if retry.get("item") and retry.get("filed"):
            item, filed = retry["item"], True
            ok, text = do_publish(item)
            text = "retry %d of %s, filed earlier; %s" % (tries, item, text)
        else:
            ok, text = do_file(item, title, why) if item else (False, "no free item name")
            filed = ok
        if ok:
            hcap, hkw = holder_launch(root, cfg, s, row, cfg["cap_usd"], fx)
            rc, text2, unit = do_launch(mod, hcap, item, **dict(hkw, **({"bars": row["batch"]} if row.get("batch") else {})))
            text = "%s; %s" % (text, text2.splitlines()[0] if text2 else rc)
            ok = rc == 0 and bool(unit)
        else:
            unit = None
        if ok:
            s.setdefault("launches", []).append({"unit": unit, "item": item, "at": now, "refused": row["refused"],
                                                 "ids": row["refused_ids"], "cap": hcap,
                                                 "stage": "offline_build"})
            s["watch"] = {"unit": unit, "refused": row["refused"], "ids": row["refused_ids"], "at": now, "ours": True,
                          "fp": row.get("bar_fp")}
            s.pop("owed_since", None)
            s.pop("launch_retry", None)
            row.update(decision="launched", unit=unit, item=item, why=text)
            known.add(item) if isinstance(known, set) else None
            done.append(row)
        elif not unit and AUT.transient(text) and tries < int(cfg.get("launch_tries", 3)):
            s["launch_retry"] = {"item": item, "filed": filed, "tries": tries, "at": now, "refused": row["refused"],
                                 "failed": text}
            row.update(decision="launch_retry", why="the Stage 3 launch never started on a transient fault (try %d of "
                       "%d), the next tick tries it again: %s" % (tries, int(cfg.get("launch_tries", 3)), text))
        else:
            s.pop("launch_retry", None)
            spent = (" %d times on a transient fault, the last" % tries) if tries > 1 and AUT.transient(text) else ""
            s["stopped"] = {"ids": row["refused_ids"], "at": now, "why": "the launch failed%s: %s" % (spent, text),
                            "launch_failed": True, "code": cfg.get("_code"), "tries": tries, "item": item,
                            "filed": filed}
            row.update(decision="launch_failed", why=text,
                       need="%s: the launch failed%s (%s); the step will not retry it on its own" % (mod, spent, text))
    return done


def holder_launch(root, cfg, s, row, cap, fx=None):
    """Option B (RIMMANDRAKE_RESUME_HOLDER_SESSIONS_TO_400K_KILL_AND_RESUME; spec §3.4): a pilot mod's run is its holder.
    modledger.resume_plan decides from the last `session.id` (end_ledger_runs records it): resume that session
    (`--resume`), rotate at or past holder_context_ceiling_tokens, or start from the packet; after a killed or lost run
    (its run.end, or this launch retrying a killed unit) the brief opens with the reconcile step. The holder's cap is per
    mod and stage, not per run: what is left of stage_ceiling_usd at this stage (never less than the run cap).
    -> (cap, launch_mod keyword arguments). A mod outside modledger.json's pilot_mods, or with no ledger: (cap, {})."""
    mod = row["mod"]
    if not pilot_ledger(root, mod):
        return cap, {}
    plan = modledger.resume_plan(root, mod)
    killed = (row.get("retry_of") or {}).get("unit")
    if killed and not plan["reconcile"]:
        plan = dict(plan, reconcile=True, why="%s; this launch retries killed run %s: reconcile the clone, unpublished "
                    "commits and the bridge first" % (plan["why"], killed))
    if row.get("stage") == "blind_challenge" and plan["action"] == "resume":
        # a blind judge never resumes the holder's warm session (spec §3.6): it starts cold, from its own brief
        plan = dict(plan, action="packet", session_id=None, why="a blind judge starts cold, never in the holder's "
                    "session %s" % plan.get("session_id"))
    row["holder"] = plan
    kw = {}
    if plan["action"] == "resume":
        kw["session"] = plan["session_id"]
    if plan["reconcile"]:
        kw["reconcile"] = plan["why"]
    ceiling, usd = cfg.get("stage_ceiling_usd"), row.get("stage_usd")
    if _usd_ok(ceiling, True) and _usd_ok(usd):
        cap = max(cap, round(ceiling - usd, 2))
        row["cap"] = cap
    return cap, kw


def record_holder_session(root, mod, r, fx=None):
    """An ended pilot run's claude session and its context (detached_helper.session_of) -> a `session.id` under that
    run's lease, so the next launch can resume it. -> a reading line, or None when the run left no session."""
    sid, ctx = (fx or {}).get("session_of", DH.session_of)(r["unit"])
    if not sid:
        return None
    got = modledger.record_session(root, mod, sid, ctx, lease=r["run"])
    return "session %s (%s context tokens)%s" % (sid, ctx if isinstance(ctx, int) else UNM,
                                                 "" if got else ": no lease to record it under")


def resume_kw(row):
    """The launch's resume argument for a retry of a KILLED run (its unit), else none."""
    u = (row.get("retry_of") or {}).get("unit")
    return {"resume": u} if u else {}


def reap_run(unit):
    """A killed run's finish (never run: its unit vanished) and its return, started as the unit's own ExecStopPost
    would: -> one line of what happened."""
    me = os.path.join(HERE, "detached_helper.py")
    said = []
    rec = DH.read_record(unit) or {}
    if rec.get("status") != "finished":
        r = subprocess.run([sys.executable, me, "finish", "--unit", unit], capture_output=True, text=True, timeout=600,
                           stdin=subprocess.DEVNULL)
        said.append("finish exit %d" % r.returncode)
        rec = DH.read_record(unit) or {}
    if rec.get("status") == "finished" and not rec.get("returned"):
        r = subprocess.run(DH.return_argv(rec), capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
        said.append("return started exit %d" % r.returncode)
    return "reaped %s: %s" % (unit, ", ".join(said) or "nothing owed")


def run_stages(r):
    """-> the stage words an ended run worked in: where the status page placed it, else its item's name (a blind or
    in-game item of this step's naming), else [] (not recorded: a guess is never a spend row)."""
    st = [M.WORD_OF_COL[c] for c in (r.get("stages") or []) if c in M.WORD_OF_COL]
    if st:
        return st
    if _is_blind_item(r.get("item")):
        return ["blind_challenge"]
    if _is_ingame_item(r.get("item")):
        return ["in_game"]
    return []


def land_spend(root, paths, fx=None):
    """Land the RUN_SPEND files just written (land.sh -m: a temp index from origin/main; one writer, so nothing of a
    steward's is overwritten). A root that is not a git clone (a selftest) or RM_STAGE_LAND=0 lands nothing."""
    if (fx or {}).get("land_spend"):
        return fx["land_spend"](paths)
    if os.environ.get("RM_STAGE_LAND") == "0":
        return "skipped: RM_STAGE_LAND=0"
    try:    # a hung git or push is a line in the reading, never a lost tick: the launches are already made
        # (RIMMANDRAKE_CATCH_SPEND_LANDING_TIMEOUT_TICK_LOST_LAUNCHES); the rows stay and land with the next tick's
        r = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                           timeout=120)
        if r.returncode != 0 or os.path.realpath(r.stdout.strip()) != os.path.realpath(root):
            return "skipped: %s is not a clone's top" % root
        import designer_stage as DS
        p = subprocess.run([DS.LAND, "-m", (fx or {}).get("land_msg") or "maturation: spend rows of ended runs (Dispatch step)"]
                           + paths, cwd=root,
                           capture_output=True, text=True, timeout=300, env=dict(os.environ, LAND_REPO=root))
    except (OSError, subprocess.SubprocessError) as e:
        return "land failed: %s: %s" % (type(e).__name__, e)
    if p.returncode and "nothing to land" not in p.stderr:
        return "land.sh exited %d: %s" % (p.returncode, p.stderr.strip())
    return (p.stdout.strip().splitlines() or ["nothing to land"])[-1]


def record_spend(root, facts, fx=None):
    """Every advancing mod's ended runs not yet recorded -> RUN_SPEND rows, then one landing. -> {mod: rows written}."""
    wrote, paths = {}, []
    for mod, f in facts.items():
        try:
            rows = M.record_run_spend(root, mod, f.get("ended_runs") or [], run_stages)
        except (OSError, ValueError) as e:
            wrote[mod] = "failed: %s" % e
            continue
        if rows:
            wrote[mod] = len(rows)
            paths.append("design/concepts/%s/%s" % (mod, M.RUN_SPEND))
    if paths:
        wrote["_land"] = land_spend(root, paths, fx)
    return wrote


CHORES_S = 1800         # the slow chores run this often, not every 60 s tick
DEAD_WAIT_S = 600       # a dead run is finished by the tick only after this long dead (its own finish may be running)


def slow_chores(st, facts, now, fx=None):
    """Two hand chores of 2026-11-13 to 11-15, done by the tick every CHORES_S: read back the dollars of finished runs
    that recorded none (`detached_helper.py backfill-cost --apply`), and finish and return a run on an advancing mod
    whose unit died with its finish never run (`detached_helper.py finish --unit`: it read "running" for good). A
    killed blind or in-game run is left to its retry path (reap_wait). -> what was said, or None between passes. A
    chore that fails says so and never costs the tick."""
    fx = fx or {}
    c = st.setdefault("chores", {})
    dead = {u: mod for mod, f in facts.items() for u in (f.get("dead_unfinished") or [])
            if u not in (f.get("killed") or {})}
    seen = c.get("dead") or {}
    c["dead"] = {u: seen.get(u, now) for u in dead}
    if now - float(c.get("at") or 0) < CHORES_S:
        return None
    c["at"] = now
    said = []
    try:
        said.append(str((fx.get("backfill") or (lambda: DH.backfill_cost(apply=True)[1].splitlines()[0]))()))
    except Exception as e:      # noqa: BLE001
        said.append("backfill-cost failed: %s: %s" % (e.__class__.__name__, str(e)))
    for u, since in sorted(c["dead"].items()):
        if now - since < DEAD_WAIT_S:
            continue
        try:
            said.append(str((fx.get("reap") or reap_run)(u)))
        except Exception as e:  # noqa: BLE001
            said.append("finishing dead run %s failed: %s: %s" % (u, e.__class__.__name__, e))
    c["said"] = said[-8:]
    return said


def reading(cfg, rows, now):
    owed = [r for r in rows if r.get("stage") == "offline_build" and r.get("owed") in OWED and not r.get("live")
            and r.get("decision") not in ("launched",) and r.get("klass") not in ("paused", "owner")]
    mx = max([r.get("idle_min") or 0 for r in owed] or [0])
    over = [r["mod"] for r in owed if (r.get("idle_min") or 0) > cfg.get("idle_alarm_min", 60)]
    return {"schema": 1, "at": now, "at_pac": pac(now), "enabled": bool(cfg.get("enabled")),
            "idle_owed_max_min": mx, "idle_owed_mods": over, "idle_alarm_min": cfg.get("idle_alarm_min", 60),
            "launched": [{"mod": r["mod"], "unit": r.get("unit"), "item": r.get("item")} for r in rows
                         if r.get("decision") == "launched"],
            "needs_conductor": [r["need"] for r in rows if r.get("need")],
            "mods": {r["mod"]: {k: r.get(k) for k in ("decision", "why", "stage", "owed", "refused", "live",
                                                       "idle_min", "stage_usd", "cycle", "visit", "exit",
                                                       "stop_lifted", "batch")} for r in rows}}


CLONE_FETCH_S = 30          # the tick's fetch of its own clone
CLONE_STALE_MIN = 5.0     # the OPS_DISPATCH_CLONE_BEHIND_UNSTICK alarm's threshold: past it the tick launches nothing
CLONE_BLIND_S = 900         # a refused fetch with origin/main's ref unmoved this long is no reading, not "level"


def clone_counts(root):
    """-> (behind, ahead) of this clone's HEAD against origin/main after a fetch, or (None, why). The timers run from
    this clone (/home/mandrake/rm/dispatch), so behind origin they run stale code with every other reading sane: it sat
    ahead 7 / behind 49 for 40 min on 2026-11-15 (RIMMANDRAKE_UNJAM_DISPATCH_CLONE_TWO_WRITERS_BLOCK_EACH_REBASE). A
    refused fetch leaves the old ref, which reads 0 behind however far origin went: past CLONE_BLIND_S that is blind."""
    def git(*a, t=60):
        return subprocess.run(["git", "-C", root, *a], capture_output=True, text=True, timeout=t)
    try:
        got = git("fetch", "-q", "origin", "main", t=CLONE_FETCH_S)
        if got.returncode:
            gd = git("rev-parse", "--absolute-git-dir").stdout.strip()
            try:
                age = time.time() - os.stat(os.path.join(gd, "logs", "refs", "remotes", "origin", "main")).st_mtime
            except OSError:
                age = None
            if age is None or age > CLONE_BLIND_S:
                return None, "fetch refused and origin/main %s: %s" % (
                    "has no reflog" if age is None else "unmoved for %d min" % (age // 60), got.stderr.strip())
        r = git("rev-list", "--left-right", "--count", "HEAD...origin/main")
    except (OSError, subprocess.SubprocessError) as e:
        return None, "clone unreadable: %s" % e
    n = r.stdout.split()
    if r.returncode or len(n) != 2:
        return None, "clone unreadable: %s" % (r.stderr.strip() or r.stdout.strip())
    return int(n[1]), int(n[0])


def clone_reading(st, now, got):
    """The clone's distance from origin/main and how long it has been behind, carried in state.json between ticks:
    behind_since is the first tick that saw it behind, level_at the last tick that saw it level (its last good sync).
    Minutes behind count from behind_since, not from commit dates: a commit pushed hours after it was made is new here."""
    c = st.setdefault("clone", {})
    behind, ahead = got
    out = {"at": now, "level_at": c.get("level_at"), "level_pac": pac(c["level_at"]) if c.get("level_at") else None}
    if behind is None:
        return dict(out, measured=False, why=ahead)
    if behind:
        c.setdefault("behind_since", now)
    else:
        c.pop("behind_since", None)
        c["level_at"] = now
    since = c.get("behind_since")
    return dict(out, measured=True, behind=behind, ahead=ahead, behind_since=since,
                behind_min=round((now - since) / 60.0, 1) if since else 0.0,
                level_at=c.get("level_at"), level_pac=pac(c["level_at"]) if c.get("level_at") else None)


TICK_UNIT, TICK_S = "rm-maturation-dispatch.timer", 60     # the timer that writes the reading, and its interval
UNIT_RX = re.compile(r"\brm-[A-Za-z0-9_@-]+(?:\.service)?")


def clone_line(c):
    if not c.get("measured"):
        return "clone: UNMEASURED (%s); last level %s" % (c.get("why"), c.get("level_pac") or "never seen")
    if c.get("behind"):
        return "clone: BEHIND origin/main by %d (ahead %d) for %s min; last level %s: its timers run old code" % (
            c["behind"], c.get("ahead") or 0, c.get("behind_min"), c.get("level_pac") or "never seen")
    return "clone: level with origin/main%s" % (" (ahead %d, not yet pushed)" % c["ahead"] if c.get("ahead") else "")


def status_lines(rd, now, unit_state=None):
    """`status`: the reading's age leads when it is older than two ticks (then nothing below it is current), and a
    "waiting on <unit>" whose unit has ended says DEAD, so a stopped tick cannot leave a dead run reading as live."""
    if unit_state is None:
        import role_launch as RL
        unit_state = RL.unit_state
    age = now - float(rd.get("at") or 0)
    if age > 2 * TICK_S:
        t = unit_state(TICK_UNIT)
        head = "reading is %d min old: the tick is %s; nothing below is current (reading at %s)" % (
            age // 60, "paused/stopped (%s %s)" % (TICK_UNIT, t) if t in DH.DEAD_STATES else
            "not writing it (%s %s; see journalctl --user -u rm-maturation-dispatch)" % (TICK_UNIT, t), rd["at_pac"])
    else:
        head = "reading at %s" % rd["at_pac"]
    out = [head] + ([clone_line(rd["clone"])] if rd.get("clone") else [])
    for mod, r in rd["mods"].items():
        txt = r.get("status") or r["why"]
        if r.get("klass") == "wait" or "waiting on" in (txt or ""):
            units = list(dict.fromkeys(UNIT_RX.findall(txt or "") + [u for u in (r.get("live") or [])
                                                                    if isinstance(u, str)]))
            dead = ["%s %s" % (u, st) for u, st in ((u, unit_state(u)) for u in units) if st in DH.DEAD_STATES]
            if dead:
                txt = "%s [DEAD: %s; the wait is over, the next tick re-decides]" % (txt, ", ".join(dead))
        out.append("%-20s %-7s %-13s %s (%s min)" % (mod, r.get("klass"), r["decision"], txt, r.get("for_min", "?")))
    for k in ("paused", "owner", "stalled"):
        if rd.get(k):
            out.append("%s: %s" % (k, "; ".join(rd[k])))
    return out


def _aut(rows, mod):
    return any(r["mod"] == mod and r.get("aut") for r in rows)


def held_rows(holds, facts):
    """One row per mod the owner holds (mod_owner_hold.py): decision owner_hold, klass held, status HELD BY OWNER with his
    words, date and lift command. A run live on it is named and left to finish."""
    out = []
    for mod, h in sorted(holds.items()):
        f = next((v for k, v in facts.items() if OH.key(k) == mod), None) or {}
        live = [u for u in f.get("live_units") or [] if isinstance(u, str)]
        txt = OH.status(h) + ("; %s live on it, allowed to finish" % ", ".join(live) if live else "")
        out.append({"mod": mod, "stage": f.get("stage", UNM), "live": live, "decision": "owner_hold", "klass": "held",
                    "status": txt, "why": txt})
    return out


def tick(root, cfg, apply, fx=None, now=None, page=True):
    """One tick; with apply, under the state lock from its read of state.json to its write."""
    if not apply:
        return _tick(root, cfg, apply, fx, now, page)
    with state_lock():
        return _tick(root, cfg, apply, fx, now, page)


def _tick(root, cfg, apply, fx=None, now=None, page=True):
    fx = fx or {}
    now = now or time.time()
    d = sdir()
    st = read_state(os.path.join(d, "state.json"))
    aut = fx.get("autonomy", True)      # False: the per-stage decision alone (selftest_maturation_dispatch's layer)
    shipped = cfg                       # the file's own values, before widen adds discovered mods (maturation_hands)
    cfg = AUT.widen(root, cfg, st, apply, fx) if aut else cfg   # Designer concepts seen and seeded; the game queue
    cfg = dict(cfg, _code=(fx["code"]() if "code" in fx else pipeline_code(REPO)))   # the code this tick runs
    facts = fx["facts"]() if "facts" in fx else gather(root, cfg)
    account = fx["account"]() if "account" in fx else account_gate()
    releases = fx["releases"]() if "releases" in fx else read_releases()
    # The owner's hold (mod_owner_hold.py): a held mod is read (its live run finishes, its spend and ledger rows are still
    # recorded below) but never decided, so nothing launches on it and it joins no idle, paused or stalled list.
    holds = OH.load()
    cfg = dict(cfg, advancing=[m for m in cfg.get("advancing") or [] if OH.key(m) not in holds])
    rows, launches = decide(cfg, st, facts, now, account, bridge=fx.get("bridge"), releases=releases)
    if aut:
        rows, launches = AUT.resolve(root, cfg, st, facts, rows, launches, now, fx)
        rows, launches = pilot_holders(root, cfg, st, facts, rows, launches, now, dict(fx, account=lambda: account))
    launches = prioritise(cfg, st, facts, rows, launches, root)     # one slot order over every layer: the list's
    if not cfg.get("enabled"):
        for r in rows:
            if r["mod"] in launches:
                r.update(decision="disabled", why="the step is disabled in maturation_dispatch.json")
        launches = []
    # measured before any launch: a clone behind past the alarm's threshold read an old tree, so it launches nothing
    # (RIMMANDRAKE_HOLD_TICK_LAUNCHES_ON_STALE_CLONE_GHOST_STEWARD: 51 min behind, it launched a steward run for a
    # blind record whose exit block had landed 5 min before)
    clone = clone_reading(st, now, (fx.get("clone") or (lambda: clone_counts(root)))()) if apply else None
    stale = bool(clone and clone.get("measured") and (clone.get("behind_min") or 0) > CLONE_STALE_MIN)
    if stale:
        for r in rows:
            if r["mod"] in launches:
                r.update(decision="stale_clone", why="this clone is %s; nothing launches on its reading" % clone_line(
                    clone)[len("clone: "):])
        launches = []
    if not apply:
        for r in rows:
            if r["mod"] in launches:
                r.update(decision="would_launch")
        launches = []
    for r in rows:      # a killed run's missing stop steps, before its retry (RIMMANDRAKE_RETRY_RUN_KILLED_BY_ACCOUNT_SWITCH_CYCLE_KEPT)
        if r.get("reap"):
            r["why"] += "; " + ((fx.get("reap") or reap_run)(r["reap"]) if apply else "would reap %s" % r["reap"])
    execute(root, cfg, st, rows, [m for m in launches if not _aut(rows, m)], now, fx)
    AUT.execute(root, cfg, st, rows, [m for m in launches if _aut(rows, m)], now, fx)
    for r in rows:      # a release lets one launch: the launch spends it
        if r.get("release") and r.get("decision") == "launched":
            st["mods"][r["mod"]].setdefault("releases_used", {})[r["release"]] = {
                "at": now, "stage": r.get("stage"), "usd": r.get("stage_usd"), "unit": r.get("unit")}
    if apply:
        book_refunds(st, rows, now)
    AUT.classify(cfg, st, rows, now)
    rows += held_rows(holds, facts)
    if apply and aut:
        AUT.post_cards(rows, st, now, fx)
    rd = AUT.annotate(reading(cfg, rows, now), rows)
    try:    # a DIVERGING stage is a Needs Conductor line; it pauses nothing (maturation_convergence.py)
        conv = fx.get("convergence")    # a selftest's fixture source (RIMMANDRAKE_ISOLATE_DISPATCH_SELFTEST_FROM_CONVERGENCE)
        if conv is None:
            import maturation_convergence as MC     # noqa: E402
            conv = MC.annotate_reading
        conv(root, rd)
    except Exception as e:      # noqa: BLE001  this reading failing never costs the tick
        rd["convergence_error"] = "%s: %s" % (e.__class__.__name__, str(e))
    for mod, c in (rd.get("convergence") or {}).items():    # the next tick's refund rule reads the word per stage
        if mod in st.get("mods", {}) and isinstance(c, dict):
            st["mods"][mod]["convergence"] = {k: (v or {}).get("verdict") for k, v in c.items()}
    if apply:
        rd["clone"] = clone
        if stale:
            rd.setdefault("needs_conductor", []).append(
                "stale_clone: nothing launched; %s (OPS_DISPATCH_CLONE_BEHIND_UNSTICK)" % clone_line(clone))
        if stale:       # both are idempotent: the first level tick writes what these held back
            rd["spend_rows"] = rd["ledger_runs"] = "held: the clone reads an old tree (stale_clone)"
        else:
            rd["spend_rows"] = record_spend(root, facts, fx)
            rd["ledger_runs"] = end_ledger_runs(root, st, facts, now, fx)
        if aut:
            rd["chores"] = slow_chores(st, facts, now, fx)
        try:        # every hand act on the pipeline, recorded; one left a day with no follow-up alarms
            import maturation_hands as MH       # noqa: E402
            MH.observe(root, shipped, st, facts, now, rd, fx.get("hands"))
        except Exception as e:      # noqa: BLE001  this reading failing never costs the tick
            rd["hand_acts_error"] = "%s: %s" % (e.__class__.__name__, e)
        try:        # a mod going round the same ground: a Fable Rescue PROPOSED to the Conductor, never launched
            import maturation_rescue as MR      # noqa: E402  (RIMMANDRAKE_PROPOSE_RESCUE_WHEN_MOD_CIRCLES_BOTH_HAND_LAUNCHED)
            MR.observe(root, cfg, st, facts, rows, now, rd, fx.get("rescue"))
        except Exception as e:      # noqa: BLE001  this reading failing never costs the tick
            rd["rescue_error"] = "%s: %s" % (e.__class__.__name__, e)
        _write(os.path.join(d, "state.json"), st)
        _write(os.path.join(d, "reading.json"), rd)
        with open(os.path.join(d, "ticks.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"at": now, "decisions": {r["mod"]: [r.get("decision"), r.get("refused"), r.get("klass")]
                                                         for r in rows},
                                "launched": rd["launched"]}) + "\n")
    if page and apply:
        regen = fx.get("page") or (lambda: subprocess.run([sys.executable, os.path.join(
            REPO, "src", "RimMandrake", "Utils", "maturation_now.py")], capture_output=True, text=True, timeout=600))
        r = regen()
        rd["page"] = "regenerated" if getattr(r, "returncode", 0) == 0 else "page failed: %s" % (
            (getattr(r, "stdout", "") or "") + (getattr(r, "stderr", "") or ""))
    return rd


HAND_NOTE = ("This is a hand act on the pipeline (id %s): the tick records it, and one with no follow-up within a day "
             "alarms. Name the item that makes this hand unnecessary in --why, or `maturation_hands.py fold <id> --item "
             "<ID>` once it is filed.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=REPO)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tick")
    t.add_argument("--apply", action="store_true", help="launch and write state; without it, a dry pass")
    t.add_argument("--no-page", action="store_true")
    sub.add_parser("status")
    c = sub.add_parser("clear")
    c.add_argument("mod")
    c.add_argument("--why", required=True)
    r = sub.add_parser("release", help="release MOD past the stage ceiling at STAGE once (the Conductor, told after)")
    r.add_argument("mod")
    r.add_argument("--stage", required=True, choices=RELEASE_STAGES)
    r.add_argument("--read-tokens", type=int, help="the stage's spend you read, in the pause line's weighted tokens")
    r.add_argument("--tokens", type=int, help="weighted tokens released past the ceiling, for one more run")
    r.add_argument("--read-usd", type=float, help="the same reading in list dollars (the form before 2026-11-16)")
    r.add_argument("--usd", type=float, help="the same release in list dollars (the form before 2026-11-16)")
    r.add_argument("--why", required=True)
    r.add_argument("--by", default=None, help="who releases (default: this window's seat)")
    pl = sub.add_parser("pilot-launch", help="start one pilot holder run from MOD's ledger packet at its current stage "
                                              "(the Conductor's act; the run's end is recorded by the tick)")
    pl.add_argument("mod")
    pl.add_argument("--why", required=True)
    pl.add_argument("--item", help="the filed item the run works under (default on a road back: its first open item)")
    pl.add_argument("--usd", type=float, help="the run's spend cap (default maturation_dispatch.json cap_usd)")
    sub.add_parser("releases", help="every ceiling release with its spend, amount and why, and whether a launch spent it")
    jv = sub.add_parser("judge-verify", help="a blind judge's verification list: MOD's findings claimed fixed (finding "
                                             "text, reproduction, the claim's test; never the holder's story)")
    jv.add_argument("mod")
    cr = sub.add_parser("cert-rerun", help="the certificate rerun unit's body: certificate MOD --run in a pool clone, "
                                           "publish the table, write the result the tick reads (zero tokens)")
    cr.add_argument("mod")
    cr.add_argument("--key", required=True)
    cr.add_argument("--unit", required=True)
    o = ap.parse_args(argv)
    if o.cmd == "cert-rerun":
        res = cert_rerun_worker(o.mod, o.key, o.unit)
        print(json.dumps(res, indent=1))
        return 1 if res.get("error") else 0
    cfg = load_cfg()
    if o.cmd == "tick":
        rd = tick(os.path.abspath(o.root), cfg, o.apply, page=not o.no_page)
        for mod, r in rd["mods"].items():
            print("%-20s %-7s %-13s %s" % (mod, r.get("klass"), r["decision"], r.get("status") or r["why"]))
        print("idle owed max %s min%s; launched %d; page %s" % (
            rd["idle_owed_max_min"], (" (over %s: %s)" % (rd["idle_alarm_min"], ", ".join(rd["idle_owed_mods"])))
            if rd["idle_owed_mods"] else "", len(rd["launched"]), rd.get("page", "not regenerated")))
        return 0
    if o.cmd == "judge-verify":
        print(judge_verify_text(os.path.abspath(o.root), o.mod), end="")
        return 0
    if o.cmd == "pilot-launch":
        rc, text = pilot_launch(os.path.abspath(o.root), cfg, o.mod, o.why, item=o.item, usd=o.usd)
        print(text)
        return rc
    if o.cmd == "status":
        rd = _read(os.path.join(sdir(), "reading.json"), None)
        if not rd:
            print("no reading yet")
            return 1
        print("\n".join(status_lines(rd, time.time())))
        return 0
    if o.cmd == "release":
        import doorbell
        import model
        # a ledger seat key ("CONDUCTOR" -> BENCH): the digest's closed seat set drops any other name, losing "who"
        by = model.canonical((o.by or doorbell.seat_name() or "").strip())
        # the pause line's weighted tokens, or the older dollar form; the record keeps dollars (the ceiling's unit)
        pair = ("--read-tokens and --tokens" if (o.read_tokens is None) != (o.tokens is None) else
                "--read-usd and --usd" if (o.read_usd is None) != (o.usd is None) else None)
        if o.tokens is not None and o.usd is not None:
            pair = "either --read-tokens/--tokens or --read-usd/--usd, not both"
        elif o.tokens is None and o.usd is None and not pair:
            pair = "--read-tokens and --tokens (the pause line's release command)"
        if pair:
            print("REFUSED: pass %s" % pair)
            return 2
        if o.tokens is not None:
            o.read_usd, o.usd = from_wt(o.read_tokens), from_wt(o.tokens)
        bad = ("%s is not on the advancing list" % o.mod if o.mod not in (cfg.get("advancing") or []) else
               "--by %s is not a ledger seat (%s)" % (by, ", ".join(model.SEATS)) if by and by not in model.SEATS else
               "--usd must be above 0" if not _usd_ok(o.usd, True) else
               "--read-usd must be 0 or more" if not _usd_ok(o.read_usd) else
               "--why is empty" if not o.why.strip() else
               "no seat: pass --by" if not by else None)
        if bad:
            print("REFUSED: %s" % bad)
            return 2
        rec = {"ts": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "mod": o.mod, "stage": o.stage,
               "by": by, "read_usd": round(o.read_usd, 2), "release_usd": round(o.usd, 2), "why": o.why.strip()}
        rec["id"] = "rel-%s" % hashlib.sha1(json.dumps(rec, sort_keys=True).encode()).hexdigest()[:12]
        with open(releases_path(), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, sort_keys=True) + "\n")
        last = ((_read(os.path.join(sdir(), "reading.json"), None) or {}).get("mods") or {}).get(o.mod) or {}
        seen = last.get("stage_usd") if last.get("stage") == o.stage else None
        print("RELEASED %s at %s by %s (read %s, by %s; %s): the next tick may launch on it once%s" % (
            o.mod, o.stage, wt(o.usd), wt(o.read_usd), by, rec["id"],
            "" if seen is None or abs(seen - o.read_usd) <= READ_SLACK else
            "; WARNING the last reading shows %s there, so this release reads stale and frees nothing" % wt(seen)))
        print(HAND_NOTE % rec["id"])
        return 0
    if o.cmd == "releases":
        recs, bad = read_releases()
        st = _read(os.path.join(sdir(), "state.json"), {})
        for r in recs:
            u = ((st.get("mods") or {}).get(r["mod"]) or {}).get("releases_used", {}).get(r["id"])
            print("%s %s %-18s %-15s read %s, released %s, by %s: %s [%s]" % (
                r["ts"], r["id"], r["mod"], r["stage"], wt(r["read_usd"]), wt(r["release_usd"]), r["by"], r["why"],
                "spent by %s" % (u.get("unit") or "a launch") if u else "unspent"))
        print("%d release(s), %d malformed line(s) in %s" % (len(recs), bad, releases_path()))
        return 0
    if o.cmd == "clear":
        with state_lock():
            return _clear(o)
    return 2


def _clear(o):
    """`clear`, under the state lock; an unreadable state.json refuses (nothing is written over it)."""
    p = os.path.join(sdir(), "state.json")
    try:
        st = read_state(p)
    except RuntimeError as e:
        print("REFUSED: %s" % e)
        return 1
    s = (st.get("mods") or {}).get(o.mod) or {}
    was = s.pop("stopped", None)
    if s.get("cert_red"):       # a stop on red deciders (cert_red_decide) lifts the same way
        was = was or {"cert_red": s.pop("cert_red")}
        s.pop("cert_red", None)
    if s.get("cert_rerun"):     # a certificate rerun spent on a build (cert_rerun_decide) may run once more
        was = was or {"cert_rerun": s.pop("cert_rerun")}
        s.pop("cert_rerun", None)
    # a steward or fixer key that never launched, or ended outside an open road back, is released: the next tick
    # may run it once more (RIMMANDRAKE_RETRY_STEWARD_LAUNCH_GIT_LOCK_COUNTED_AS_SPENT: clear left those spent)
    released = {}
    for book in ("steward", "fixers"):
        for k, x in list((s.get(book) or {}).items()):
            if AUT.releasable(s, k, x):
                released.setdefault(book, {})[k] = s[book].pop(k)
    # so is a blind or in-game launch that never started (refused at the spawn, say): it judged nothing, and left
    # in its book it stops the next tick again (RIMMANDRAKE_ADMIT_INGAME_SPAWN_RUNNER_REFUSES_GAME_UP); and so is a
    # run that started and has ENDED with no record: the tick derives `stopped` from it on every pass, so leaving it
    # made clear answer "was: not stopped" and lift nothing (RIMMANDRAKE_ENACT_TOKENS_NOT_DOLLARS_NO_LIVE_HOLD). A run
    # still live (or whose record cannot be read) stays the visit's automatic run.
    ended = []
    for book in ("blind_auto", "ingame_auto"):
        gone = [x for x in s.get(book) or [] if isinstance(x, dict) and (
            (x.get("failed") and not x.get("unit"))
            or (x.get("unit") and ((DH.read_record(x["unit"]) or {}).get("status") == "finished")))]
        if gone:
            s[book] = [x for x in s[book] if not any(x is g for g in gone)]
            released[book] = gone
            ended += [x["unit"] for x in gone if x.get("unit")]
    if ended and not was:
        was = {"why": "the automatic run(s) %s ended and wrote no record" % ", ".join(ended)}
    s.setdefault("cleared", []).append({"at": time.time(), "why": o.why, "was": was, "released": released})
    st.setdefault("mods", {})[o.mod] = s
    _write(p, st)
    print("CLEARED %s (was: %s; released %d steward, %d fixer key(s), %d blind/in-game launch(es) that never started "
          "or ended with no record)" % (
              o.mod, (was or {}).get("why", "not stopped"), len(released.get("steward") or {}),
              len(released.get("fixers") or {}),
              len(released.get("blind_auto") or []) + len(released.get("ingame_auto") or [])))
    print(HAND_NOTE % ("clear-%s-%d" % (o.mod, s["cleared"][-1]["at"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
