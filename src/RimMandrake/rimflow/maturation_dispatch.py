#!/usr/bin/env python3
"""maturation_dispatch.py: the Dispatch step of the Maturation Pipeline. It launches capped offline builders for the
advancing mods that stand at the offline build with build work owed, and nothing else. No model, no tokens of its own.

Item RIMMANDRAKE_WIRE_DISPATCH_TO_LAUNCH_BUILDERS_MODS_SAT_IDLE. The owner, 2026-11-14 ~9 PM PST, at the keyboard: "So can
we wire up Operations/Dispatch such that they do advance on these offline builders? This was pretty inefficient and
pointlessly it seems, if I'm reading correctly. As long as we don't have automated loops rejecting/cycling things, we
can't get into too much trouble." (Measured that evening: all four advancing mods sat at Stage 3 for 6 to 9 hours with
no builder on them, because every launch was a Conductor hand step.)

    python3 src/RimMandrake/rimflow/maturation_dispatch.py tick [--apply] [--page]
            one pass: decide per mod, launch (only with --apply), write the reading. MATURATION_NOW is built by its own
            unit, rm-maturation-page.timer, never inside the tick's cgroup; --page also builds it here, by hand
    python3 src/RimMandrake/rimflow/maturation_dispatch.py status        the last reading, one line per mod
    python3 src/RimMandrake/rimflow/maturation_dispatch.py clear MOD --why "..."
            the Conductor lifts a stop on MOD (the next tick may launch on it once)
    python3 src/RimMandrake/rimflow/maturation_dispatch.py releases      every release: spend, amount, why, spent or not
    python3 src/RimMandrake/rimflow/maturation_dispatch.py release MOD --stage STAGE --read-usd X --usd R --why "..."
            the Conductor releases MOD past the ceiling at STAGE by USD R, having read USD X spent there: one more
            launch, then the mod pauses at the next ceiling (item RIMMANDRAKE_RELEASE_STAGE_CEILING_PER_MOD_ONLY_GLOBAL_KNOB)
    python3 src/RimMandrake/rimflow/maturation_dispatch.py pause [MOD] --why "..." [--until +2h|HH:MM|--until-release]
            [--stop-live]      the pipeline's pause (pipeline_pause.py): nothing in the launch-path census starts on
            MOD (default: anything) from the next tick; live runs finish unless --stop-live; a planned stop, no alarm
    python3 src/RimMandrake/rimflow/maturation_dispatch.py resume [MOD] --why "..."
    python3 src/RimMandrake/rimflow/maturation_dispatch.py next [--within 30m]
            UP NEXT: what WILL start if nobody acts, by this tick's own code in its dry pass on a moving clock
            (item RIMMANDRAKE_ADD_PAUSE_ALL_AND_UP_NEXT_HOLD_LEAKED; the same verbs: `rimflow pipeline pause|resume|next`)

Runs on rm-maturation-dispatch.timer (every 60 s, from the dispatch clone); its own timer, not the Dispatcher's tick,
so a slow ledger read never cuts a Dispatcher beat. Settings: maturation_dispatch.json beside this file.

Per mod on the advancing list, in order, one decision:
  not_offline   the mod's record is at none of the offline build, the blind challenge and in-game acceptance (no record,
                the Designer, any later stage): nothing here; the Designer stays his
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
                written on an empty refused set lifts itself (RIMMANDRAKE_SKIP_BUILDER_STOP_ON_ZERO_REFUSED_BARS); nor is
                a run the tick did not launch as a builder (no launches or pilot_launches entry: a hand design run, an
                exam retake), and a stop written on one lifts itself
                (RIMMANDRAKE_SPARE_HAND_RUNS_FROM_BUILDER_STOP_REWORD_RAN)
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
  test pilot    a live road-back item at Stage 6 with Relentless's count (run_rules.json pilot_after_live_fails)
                of LEFT OPEN endings since its last sitting gets an rm-testpilot sitting on the pilot model as its next
                run, booked in fixers as ITEM|pilot|<tsn> (maturation_autonomy._pilot_step;
                RIMMANDRAKE_ROUTE_SPENT_LIVE_FIXER_PILOT_BY_HAND: both Explosive Knockback sittings were launched by hand)
  slots_full    max_live live runs on advancing mods already (the Conductor's included)
  account_hold  the Dispatcher's account pick holds role launches (its rule's `hold` list): nothing
  launch        spawn a ledger item under this one (seat RUNNER, as ops_watch files), publish the shard, `maturation.py launch` it (opus, the cap)
At the blind challenge (item RIMMANDRAKE_BUILD_BLIND_CHALLENGE_LAUNCHER_FOUR_MODS_PARKED), per advancing mod, one of:
  launch        cycle N (the record's cycles.total) is owed (no cycle_N folder), nothing live or just ended, no blind run
                since it opened, and an automatic cycle of this visit left: one judge (opus, blind_cap_usd), item
                RIMMANDRAKE_JUDGE_<MOD>_BLIND_CYCLE_<N>_TESTS_FIRST spawned the same way as a build item
  live | settling   a run is live on it, or one ended under settle_s ago: nothing
  exit_met | exit_not_met | cycle_unfinished   cycle N is recorded (maturation.read_exit): a Needs Conductor line each;
                the steward confirms or opens the next cycle by hand, never the program
  stopped | auto_spent | hand_run_seen   the visit's automatic cycle ended with no record or failed to launch, or was
                already spent (blind_auto_cycles_per_visit), or a hand-launched blind run worked on the cycle and wrote
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

_HERE_GN = os.path.dirname(os.path.abspath(__file__))
if _HERE_GN not in sys.path:
    sys.path.insert(0, _HERE_GN)
import game_names as _GN  # noqa: E402  (the one map: a game's letter -> ArchBig, ArchSmall, Steve1, Steve2)
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import maturation as M          # noqa: E402
import judge_certificate as JC  # noqa: E402  the pre-judgement certificate, read before a judge or visit launch
import maturation_now as MN     # noqa: E402
import maturation_autonomy as AUT   # noqa: E402
import own_cgroup               # noqa: E402  landings outside the tick's memory limit
import detached_helper as DH    # noqa: E402
import modledger                # noqa: E402  the mod ledger: stage runs from its packet; holder sessions (resume_plan)
import pipeline_pause as PP          # noqa: E402  the pipeline's pause: one switch, a file (pause.json in sdir)
import pipeline_control as PC       # noqa: E402  the one control store (`pipe`): counts, limits, switches, queue
import mod_owner_hold as OH          # noqa: E402  the owner's hold: a held mod is never decided (mod_owner_hold.json)
import run_void as RV            # noqa: E402  a VOID run spends no trial (RIMMANDRAKE_VOID_SYSTEM_KILLED_RUNS_NO_TRIAL_SPENT)
import mod_model as MM           # noqa: E402  one mod's builders on a pinned model, caps scaled (`pipe model`)
import form_fault as FF          # noqa: E402  a fault of form is repaired where it is found, never counted

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
    return RV.sync_dispatch(st)     # every reader honours the standing voids (run_void.py)


def pac(t):
    return dt.datetime.fromtimestamp(t, MN.PAC).strftime("%Y-%m-%d %I:%M %p %Z").replace(" 0", " ")


def word(n):
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("" if n % 10 == 0 else "_" + ONES[n % 10])
    return "MANY"


def item_id(mod, count, known):
    """-> a rimflow name for a Stage 3 build item: RIMMANDRAKE_AUTOBUILD_<MOD>_<N>_BARS_LEFT (fit_name)."""
    return fit_name(["RIMMANDRAKE", "AUTOBUILD", "@" + mod, nword(count or 0), "?BARS", "LEFT"], known)


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
        try:
            f = M.build_facts(root, mod)
        except PC.Unreadable as e:
            # the counts live in the control store (slice 2): an unreadable store is a fact of the mod, and the hold
            # read in _tick then holds every mod as UNREADABLE, never a crash
            # (RIMMANDRAKE_HOLD_UNREADABLE_STORE_TICK_CRASH_BACK_SLICE_TWO)
            f = {"mod": mod, "control_unreadable": "CONTROL UNREADABLE: %s" % e}
        f["arrived"] = arrivals(M.load(root, mod))
        m = by.get(mod) or {}
        runs = m.get("runs", UNM) if m else []
        if isinstance(runs, list):
            # a lane run holds its mod only once it is on the mod's files (lane_on_mod_files); one on pipeline code
            # that names the mod by a title word held FlowWorks with ArchBig free (2026-11-25 9:05 AM PST,
            # RIMMANDRAKE_FIND_WHY_ARCHSMALL_SITS_FREE_TWO_MODS_AT_IN_GAME)
            beside = [r["unit"] for r in runs if r.get("live") and r.get("lane") == LIST_LANE
                      and _beside(lane_on_mod_files(r["unit"], mod))]
            f["live_units"] = [r["unit"] for r in runs if r.get("live") and r["unit"] not in beside]
            f["lane_units"] = [r["unit"] for r in runs if r.get("live") and r.get("lane") == LIST_LANE
                               and r["unit"] not in beside]
            if beside:
                f["lane_beside"] = beside
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
            f["runs_seen"] = [{"unit": r["unit"], "item": r.get("item"), "at": r.get("at"), "end": r.get("end"),
                               "ran": ran(r)} for r in runs if r.get("unit")]
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


def game_hold(game):
    """-> why game `game` is held by `pipe off game:<g>` (control.game_held), or None. A store that cannot be read holds
    the game: could not look is never "not held"."""
    import control as C
    try:
        return C.game_held(game)
    except C.Unreadable as e:
        return "the control store could not be read, so a hold on game %s cannot be ruled out: %s" % (game, e)


def full_list_only(f):
    """-> the visit's full-list checks when EVERY stage-6 check of it needs his full list, else []. Such a visit cannot
    run on game b beside game a: a full list on b does not fit in memory beside a (about 17.5 GB against 19.6 GB of
    headroom over a 12 GB floor, MEASURED 2026-11-20), so it waits for game a and says so. A visit with any tier check
    may go to b; its full-list checks are UNMEASURED there (game_instance.brief). The checks the visit OWES decide
    (to_run, when the facts carry it), not every check of the table: a visit owing sc_walk alone, with the other rows
    counted, ran on b and left it UNMEASURED again (RIMMANDRAKE_SEND_WALK_ONLY_VISIT_TO_ARCHBIG_NOT_ARCHSMALL)."""
    full = list(f.get("full_list") or [])
    checks = [k for k in f["to_run"] if k in (f.get("checks") or f["to_run"])] if "to_run" in f \
        else list(f.get("checks") or [])
    return [k for k in checks if k in full] if checks and set(checks) <= set(full) else []


STEVE_GAMES = "SteveDesktop (Steve1, Steve2)"


def steve_takes(f, mod):
    """-> the clause a visit's wait for ArchBig or ArchSmall adds about SteveDesktop's two games: what of the owed checks
    the visit feed sends to the lane (a check goes there only with a testq block, testq/visit_feed.py), or that it takes
    none and the command that says why per check. Checks that could not be read read UNMEASURED, never "none". Page
    design/specs/2026-11-23-tick-names-steve-games/boundary.md (RIMMANDRAKE_SEND_MOD_VISITS_TO_STEVEDESKTOP_TICK_SEES_
    TWO_OF_FOUR_GAMES: the line named two of four games, 2026-11-23)."""
    owed = f.get("to_run") if isinstance(f.get("to_run"), list) else f.get("checks")
    if not isinstance(owed, list) or not owed or not isinstance(f.get("testq"), list):
        return "%s: UNMEASURED, the visit's owed checks or their testq blocks could not be read" % STEVE_GAMES
    tq = set(f["testq"])
    lane = [k for k in owed if k in tq]
    if lane:
        return ("%s: the visit feed sends the lane %d of its %d checks (those with a testq block); the other %d need a "
                "Claude driver on ArchBig or ArchSmall" % (STEVE_GAMES, len(lane), len(owed), len(owed) - len(lane)))
    return ("%s: takes none of its %d checks, since none carries a testq block (why, per check: python3 "
            "src/RimMandrake/Utils/testq/testq_blocks.py derive %s)" % (STEVE_GAMES, len(owed), mod))


def lock_says(game, query=None):
    """-> "; the lock now: <its line>" for game `game`, read from its lock at this moment (game_lock.py), or "" when no
    lock is readable here (a test tree, another machine). The tick's words about a game come from the lock."""
    import game_lock as GL
    try:
        path = GL.lock_path(game)
        if not path and query is None:
            return ""
        return "; the lock now: %s" % (query or GL.query)(game, pipe=False, path=path)["line"]
    except Exception as e:  # noqa: BLE001  (a reading that fails is said, never dropped)
        return "; the lock now: COULD NOT LOOK (%s: %s)" % (type(e).__name__, e)


def pick_game(cfg, bridge, purpose, held=None, hold=None, only=None):
    """-> (the first free game, or None; [why not, per game]). A game is free when no live driver holds it (held:
    {game: unit}) and its own bridge reading says takeable. The games are cfg game_instances (else a); a reading that
    cannot name a game (a one-argument stand-in) reads game a only. RIMMANDRAKE_LAUNCH_BOTH_GAMES_STEAM_REFUSES_A_BESIDE_B:
    the owner, 2026-11-16, "don't forget we have two Rimworld games, so I don't want to hear any 'waiting for game'".
    hold: the per-game hold reader (game_hold: `pipe off game:a` for his walk); a held game is never picked, whoever
    holds its bridge, so his walk is kept even when the Conductor's bridge hold lapses. only: {game: why not} for games
    this run cannot use (a full-list-only visit on game b)."""
    read = bridge or (lambda p, game="a": M.bridge_idle(p, cfg.get("seat", "BENCH"), game=game))
    named = M.takes_game(read)
    games = [g for g in (cfg.get("game_instances") or ["a"])] if named else ["a"]
    whys = []
    import game_names as GN             # each reason names its game: ArchBig, ArchSmall (the one map)
    hold = hold or game_hold
    for g in games:
        if g in (only or {}):
            whys.append("%s: %s" % (GN.show(g), GN.name_text(only[g])))
            continue
        if g in (held or {}):
            # the run record says who; the lock, read now, says whether that is still so (the tick named a dead run
            # as live on 2026-11-21, RIMMANDRAKE_BUILD_ONE_GAME_LOCK_CLAIM_FOUR_RECORDS_DISAGREE)
            whys.append("%s: driven by %s%s" % (GN.show(g), held[g], lock_says(g)))
            continue
        h = hold(g)
        if h:
            whys.append("%s: %s" % (GN.show(g), h))
            continue
        go, why = read(purpose, game=g) if named else read(purpose)
        if go:
            return g, whys
        whys.append("%s: %s" % (GN.show(g), GN.name_text(why)))
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
    void = RV.active()      # a VOID run is no kill to retry: it counts nothing (run_void.py)
    for r in runs or []:
        u = r.get("unit")
        if not u or r.get("live") or u in void or not (_is_blind_item(r.get("item")) or _is_ingame_item(r.get("item"))):
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


TRIED_RX = re.compile(r"LAUNCH (?:FAILED|UNCONFIRMED) (rm-[\w.@-]+?):")


def tried_unit(text):
    """-> the unit a failed or unconfirmed launch tried, read from detached_helper's own failure line ("LAUNCH FAILED
    <unit>: ..." / "LAUNCH UNCONFIRMED <unit>: ..."), or None when the text names none. A tick launch that failed is
    booked unit=None, but its launch record exists under this unit; booked as `tried`, the hand-act reader knows it as
    the tick's own (RIMMANDRAKE_BOOK_FAILED_TICK_LAUNCHES_THREE_FALSE_HANDS: Gimme Some Slack's in-game launches
    1794831340 and 1794834319 read as hand launches)."""
    m = TRIED_RX.search(str(text or ""))
    return m.group(1) if m else None


def ran(r):
    """False for a run record whose launch failed (systemd-run never started a unit): it worked on nothing, so it is
    neither an in-game or blind run of the visit nor a dead run whose finish never ran (2026-11-16: Gimme Some Slack
    paused hand_run_seen on its own failed launch). Nor did one control refused at launch: no unit was started
    (2026-11-21: slow_chores reaped refused records as "killed: unknown", and their returns bundled the clone the next
    launch had reused; RIMMANDRAKE_FIX_OFFLINE_STEWARD_REFUSED_BY_GAME_A_WALK_HOLD)."""
    return r.get("state") not in ("launch_failed", "refused")


def add_ingame(root, mod, f, runs):
    """ingame_live (every mod): the live runs whose item names an in-game run (_is_ingame_item), for the one-driver rule.
    At in-game acceptance also maturation.ingame_facts (visit, exit reading, owed) and ingame_runs, the in-game runs
    started since the visit opened (10 min of slack, as for the blind challenge)."""
    f["ingame_live"] = [r.get("unit") for r in runs or [] if r.get("live") and _is_ingame_item(r.get("item"))]
    f["ingame_games"] = {r.get("unit"): run_game(r) for r in runs or [] if r.get("live") and _is_ingame_item(r.get("item"))}
    if f.get("stage") != "in_game":
        return f
    f.update(M.ingame_facts(root, mod, deploy_stamp=True))
    f["certificate"] = M.certificate(root, mod, "in_game")
    f["known_red"] = known_red(root, mod)          # cert_wait's red-decider route reads which items owe them
    f["cert_rerun_result"] = rerun_result(mod)     # cert_wait's zero-token rerun reads its last result
    f["cert_rerun_landed"] = rerun_landed(root, f["cert_rerun_result"])
    t0 = _ts(f.get("opened"))
    void = RV.active()      # a VOID run worked on nothing the visit counts (run_void.py)
    f["ingame_runs"] = [r.get("unit") for r in runs or [] if _is_ingame_item(r.get("item")) and ran(r)
                        and r.get("unit") not in void
                        and isinstance(r.get("at"), (int, float)) and t0 is not None and r["at"] >= t0 - 600]
    return f


def known_red(root, mod):
    """-> the test table's known_red marks {test: item} (cert_red_decide reads which red deciders an item already owes)."""
    tt, _ = JC.read_table(root, mod)
    return {tid: t["known_red"] for tid, t in ((tt or {}).get("tests") or {}).items()
            if isinstance(t, dict) and isinstance(t.get("known_red"), str)}


def add_cert(root, mod, f):
    """At the offline build waiting on its certificate: the certificate's rows and the test table's known_red marks."""
    f["certificate"] = M.certificate(root, mod, "blind_challenge")
    f["known_red"] = known_red(root, mod)
    f["cert_rerun_result"] = rerun_result(mod)
    f["cert_rerun_landed"] = rerun_landed(root, f["cert_rerun_result"])
    return f


def add_blind(root, mod, f, runs):
    """At the blind challenge: maturation.blind_facts (cycle, visit, exit reading, owed) and blind_runs, the runs whose
    item names a blind run (_is_blind_item) that started since the cycle opened (10 min of slack for a launch that beat
    its own advance to origin/main). Any other stage: f unchanged."""
    if f.get("stage") != "blind_challenge":
        return f
    f.update(M.blind_facts(root, mod))
    f["certificate"] = M.certificate(root, mod, "blind_challenge")
    f["known_red"] = known_red(root, mod)          # cert_wait's red-decider route reads which items owe them
    f["cert_rerun_result"] = rerun_result(mod)     # cert_wait's zero-token rerun reads its last result
    f["cert_rerun_landed"] = rerun_landed(root, f["cert_rerun_result"])
    f["cycle_decision"] = cycle_decision(M.load(root, mod) or {})
    t0 = _ts(f.get("opened"))
    void = RV.active()      # a VOID run worked on nothing the cycle counts (run_void.py)
    f["blind_runs"] = [r.get("unit") for r in runs or [] if _is_blind_item(r.get("item")) and ran(r)
                       and r.get("unit") not in void
                       and isinstance(r.get("at"), (int, float)) and t0 is not None and r["at"] >= t0 - 600]
    f["blind_run_at"] = {r.get("unit"): r.get("at") for r in runs or [] if r.get("unit") in f["blind_runs"]}
    if isinstance(f.get("void_run"), dict):     # a voided judge's own session, to resume (decide_blind)
        try:
            f["void_session"] = DH.run_session(f["void_run"]["unit"])
        except Exception as e:      # noqa: BLE001  could not look: the cycle then opens fresh, said
            f["void_session"] = (None, None, "the session could not be read: %s: %s" % (type(e).__name__, e))
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
    """-> the steward, fixers or holder_road_back book that launched `unit` for this mod, else None.
    RIMMANDRAKE_EXEMPT_STEWARD_RUNS_FROM_BUILDER_PROGRESS_STOP: Graffiti's preflight steward moved it into the offline
    build while still live, and its end was judged as a builder's ("stopped, 33 -> 33")."""
    if not unit:
        return None
    for book in ("steward", "fixers"):
        for e in (s.get(book) or {}).values():
            if isinstance(e, dict) and e.get("unit") == unit:
                return book
    if any(e.get("unit") == unit for e in s.get("holder_road_back") or []):
        return "holder_road_back"
    return None


def tick_builder(s, unit):
    """-> True when `unit` is a builder the tick launched for this mod (its `launches` or `pilot_launches` book). The
    builder-progress stop guards the tick's own automatic tries; a run launched by another hand (a design reword, an
    exam retake) is no builder of the stage, and its end says nothing about build work
    (RIMMANDRAKE_SPARE_HAND_RUNS_FROM_BUILDER_STOP_REWORD_RAN: ExplosiveKnockback 2026-11-25)."""
    return bool(unit) and any(isinstance(x, dict) and x.get("unit") == unit
                              for book in ("launches", "pilot_launches") for x in s.get(book) or [])


_STOP_RUN = re.compile(r"^run (\S+) ended and ")


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


def control_env(mod, stage):
    """-> the env that records a launch's mod and stage in its run record: maturation_now.runs_for_mods places the run
    by it, so the next tick reads the mod live whatever the item is called. The red-decider builder records no stage:
    it works the offline build while the row may stand at a later stage, and a stage switch refusing that launch after
    the tick's own switch check would be booked as its one spent try."""
    return dict({"RM_CONTROL_MOD": mod}, **({"RM_CONTROL_STAGE": stage} if stage else {}))


def own_live(st, facts, record, status=None):
    """-> facts (copied) with each mod's un-ended ledger runs (s["ledger_runs"]) counted live, whatever placement read:
    one live run per mod, as pilot_launch holds it (RIMMANDRAKE_REFUSE_SECOND_HOLDER_WHILE_FIRST_LIVES_FENCED_AGAIN: a
    holder on an item naming no mod read as nothing live, and the next launch's lease fenced it). A voided trial can
    still have a live unit while a cooperative stop is pending. A record that is absent, unreadable or without a
    status is never an end: its unit is live, and named in live_unread."""
    status = status or DH.live_status
    out = dict(facts)
    for mod, f in facts.items():
        if not isinstance(f, dict) or not isinstance(f.get("live_units"), list):
            continue        # an unreadable reading stays one: nothing launches on it already
        live, unread, own = list(f["live_units"]), [], []
        s = (st.get("mods") or {}).get(mod) or {}
        voided = [m["entry"] for m in s.get("voided") or [] if m.get("book") == "ledger_runs"]
        for r in (s.get("ledger_runs") or []) + voided:
            u = r.get("unit")
            if not u or r.get("ended") or u in own:
                continue
            if u in live:
                own.append(u)
                continue
            try:
                rec = record(u)
            except Exception:       # noqa: BLE001  could not look is never "ended"
                rec = None
            if rec is None and r in voided:     # an old void whose record is pruned holds no mod for good
                continue
            if not isinstance(rec, dict) or not rec.get("status"):
                unread.append(u)
            elif status(rec) not in ("launching", "running"):
                continue
            live.append(u)
            own.append(u)
        out[mod] = dict(f, live_units=live, **dict({"own_live": own} if own else {},
                                                  **({"live_unread": unread} if unread else {})))
    return out


def one_run_fence(facts, rows, launches):
    """The last word on one live ledger run per mod, whatever layer asked for the launch: a run taking a slot on a mod
    whose own ledger run is live (own_live) waits for its end. Before it, a live run that advanced its own mod's stage
    met the next stage's steward there, whose lease fenced it (the steward stages read no live run). -> launches."""
    for row in rows:
        own = (facts.get(row["mod"]) or {}).get("own_live")
        if own and takes_slot(row) and (row["mod"] in launches or row.get("decision") == "slots_full"):
            row.update(decision="live", aut=None, waits_on=", ".join(own), why="%s is live on it: one ledger run per "
                       "mod; it was: %s" % (", ".join(own), row.get("why")))
            row.pop("need", None)
            launches = [m for m in launches if m != row["mod"]]
        unread = (facts.get(row["mod"]) or {}).get("live_unread")
        if unread and row.get("decision") == "live":
            row["why"] = "%s; the run record of %s cannot be read: counted live, never ended" % (
                row.get("why"), ", ".join(unread))
    return launches


LIST_LANE = "list_dispatch"     # detached_helper's next_act_owner on every Workshop Pipeline run


def _beside(answer):
    """True only for a looked answer of False: a lane run that could not be read is held, never free."""
    return bool(answer.ok and answer.value is False)


def _mod_paths(paths, mod):
    import mod_work as MW
    hits = []
    for p in paths:
        m = MW.PATH_RX.match(str(p).strip().strip('"').replace("\\", "/"))
        if m and MW.place(m.groups(), {mod}) == mod:
            hits.append(p)
    return hits


def lane_on_mod_files(unit, mod, record=None, run=None):
    """-> probe_result value(True) when the Workshop Pipeline run `unit` is on `mod`'s files (src/<Tier>/<mod>/, design/concepts/<mod>/): its
    clone's working tree, its commits not on origin/main, or its commits since launch that name its item touch one.
    value(False) when it touches none; could_not_look(cause) for no record, no clone or a git error: held, never free.
    A lane run names its mod by a title word (list_dispatch.mod_of), so one on pipeline code held the mod for nothing.
    The lane launches beside a live mod run with no such guard, so the window a lane run opens before its first mod
    edit is the one it already has (design/specs/2026-11-23-list-dispatch/boundary.md, a-lane-run-on-a-mod-takes-no-mod-slot)."""
    import probe_result as PR
    import time_budget as TB
    run = run or subprocess.run
    try:
        rec = (record or DH.read_record)(unit)
    except Exception as e:       # noqa: BLE001  could not look is held
        return PR.could_not_look("the run record of %s could not be read (%s: %s)" % (unit, type(e).__name__, e))
    clone, item, at = (rec or {}).get("clone"), (rec or {}).get("item"), (rec or {}).get("at")
    if not (clone and os.path.isdir(os.path.join(str(clone), ".git")) and item):
        return PR.could_not_look("%s has no record, no item or no clone on disk (%s)" % (unit, clone))
    reads = [["status", "--porcelain", "--untracked-files=all"],
             ["log", "--format=", "--name-only", "origin/main..HEAD"],
             ["log", "--format=", "--name-only", "--fixed-strings", "--grep", str(item), "HEAD"]
             + (["--since=@%d" % int(at - 3600)] if isinstance(at, (int, float)) else [])]
    paths = []
    for a in reads:
        try:
            r = run(["git", "-C", str(clone)] + a, capture_output=True, text=True, timeout=TB.CALL_S,
                    stdin=subprocess.DEVNULL)
        except (OSError, subprocess.SubprocessError) as e:
            return PR.could_not_look("git %s in %s: %s: %s" % (a[0], clone, type(e).__name__, e))
        if r.returncode:
            return PR.could_not_look("git %s in %s exited %d: %s" % (a[0], clone, r.returncode, (r.stderr or "")[:200]))
        for ln in (r.stdout or "").splitlines():
            ln = ln[3:] if a[0] == "status" else ln
            paths += [x for x in ln.split(" -> ") if x.strip()]
    return PR.value(bool(_mod_paths(paths, mod)))


def occupancy(facts):
    """-> the live runs on advancing mods, or None when any mod's live runs cannot be read: an unknown occupancy is
    never counted as zero (RIMMANDRAKE_RESERVE_CAP_BEFORE_LAUNCH; it used to skip a non-list and launch). A Workshop Pipeline
    run on a mod's list item keeps the mod's files (it is live on the mod) and takes no mod slot: that lane has its own
    (design/specs/2026-11-23-list-dispatch/boundary.md, a-lane-run-on-a-mod-takes-no-mod-slot)."""
    occ = [f.get("live_units") for f in facts.values()]
    if not all(isinstance(x, list) for x in occ):
        return None
    return sum(len(set(f["live_units"]) - set(f.get("lane_units") or ())) for f in facts.values())


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


def stage_spend(cfg, mod, stage, usd):
    """-> (the stage's spend, its ceiling) in dollars, through the mod's weighted-token account for the stage in the
    control store (`pipe set|add|reset|limit <Mod> spend_<stage> ...`, PC.SPEND_RES): every ceiling reader (the gate,
    the killed-run refund, a pilot holder's cap) asks this, never stage_ceiling_usd itself. A stage with no account, no
    ceiling or no readable spend reads the pipeline's own numbers."""
    ceiling = cfg.get("stage_ceiling_usd")
    if stage not in PC.SPEND_RES or not _usd_ok(ceiling, True) or not _usd_ok(usd):
        return usd, ceiling
    return (from_wt(PC.used(mod, PC.SPEND_RES[stage], to_wt(usd))),
            from_wt(PC.limit(mod, PC.SPEND_RES[stage], to_wt(ceiling))))


def ceiling_gate(cfg, s, mod, stage, usd, cap, where, releases):
    """-> (why the next run may not start, or None; the release record id that lets it start past the ceiling, or
    None). releases: read_releases()'s (records, malformed); s: the mod's state (its releases_used)."""
    usd, ceiling = stage_spend(cfg, mod, stage, usd)
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


def void_units(f, s):
    """-> the units whose spend does not count toward the stage ceiling: a standing hand void, an entry the mod's
    `voided` list holds (hand or void_system), and a run killed before it wrote a result (f["killed"]). The owner, by
    card 2026-11-18 11:06 AM PST (design/specs/2026-11-18-pipeline-control-surface/03-merged.md, Rulings 1): a void
    run's spend "Does not count": the ceiling measures what the mod cost on its merits; the system-fault alarm
    catches a fault loop (run_void.py)."""
    out = set(RV.active()) | set((f or {}).get("killed") or {})
    out |= {m.get("unit") for m in (s or {}).get("voided") or [] if m.get("unit")}
    return out


def arrivals(rec):
    """-> {stage: epoch} the mod's latest arrival at each stage: its newest move into it from another stage (a cycle or
    visit opened inside the stage, a road back from == to, is not an arrival), else the record's since for its stage."""
    out = {}
    for mv in (rec or {}).get("moves") or []:
        t = _ts(mv.get("at"))
        if t is not None and mv.get("to") and mv.get("from") != mv.get("to"):
            out[mv["to"]] = max(out.get(mv["to"], t), t)
    t = _ts((rec or {}).get("since"))
    if t is not None and (rec or {}).get("stage") and rec["stage"] not in out:
        out[rec["stage"]] = t
    return out


def _off_ceiling(f, s, spent, stage=None):
    """Drop the void units, and every run started before the mod's latest arrival at the stage (it was spent on an
    earlier pass: RIMMANDRAKE_TRACE_SLACK_STAGE_SIX_SPEND_BEFORE_FIRST_VISIT), from {unit: usd}; -> (kept usd, void
    usd), each rounded. An unread arrival counts every run."""
    came, at = (f.get("arrived") or {}).get(stage), {r.get("unit"): r.get("at") for r in f.get("runs_seen") or []}
    if came is not None:
        spent = {u: v for u, v in spent.items() if not (isinstance(at.get(u), (int, float)) and at[u] < came)}
    void = void_units(f, s)
    v = round(sum(u_usd for u, u_usd in spent.items() if u in void), 2)
    return round(sum(u_usd for u, u_usd in spent.items() if u not in void), 2), v


def stage_spent(f, stage, ours, s=None, both=False):
    """-> USD spent at this stage on the mod's merits: every run the status page placed in its box (measured dollars,
    else its cap), plus this step's own launches there not yet placed (at their cap), less every VOID run (void_units;
    shown apart as void spend). both=True -> (counted, void)."""
    spent = dict((f.get("box_runs") or {}).get(M.COL[stage]) or {})
    for x in ours or []:
        # with the killed attempts a retry replaced (counted here, then taken off as void below)
        for u in [x.get("unit")] + list(x.get("killed_before") or []):
            if u and u not in spent:
                spent[u] = (f.get("run_usd") or {}).get(u, x.get("cap") or 0.0)
    kept, void = _off_ceiling(f, s, spent, stage)
    return (kept, void) if both else kept


REFUND_STAGE = {"blind_challenge": "4+5", "in_game": "6"}       # maturation_convergence's stage keys


def refund(cfg, s, f, stage, usd, cap, unit):
    """-> (refund, why not). The Conductor's judgement of 2026-11-15 12:25 PM PST, as a rule: "cycle 3 was killed
    mid-run by the account switch, not failed ... The mod is converging." A run KILLED from outside before it wrote a
    result (f["killed"]) bought no judging, yet its dollars stay charged to the stage; when they alone hold its own
    retry at the ceiling, the tick gives them back once: the amount still missing, never more than that run spent,
    never twice for one run, and not while the stage reads DIVERGING. Any other release stays the Conductor's hand."""
    if not unit or unit not in (f.get("killed") or {}):
        return None, ""
    if unit in void_units(f, s):    # its dollars are already off the ceiling (void spend): nothing to give back
        return None, ""
    if unit in (s.get("refunds") or {}):
        return None, "; the killed run %s was refunded once already" % unit
    usd, ceiling = stage_spend(cfg, f.get("mod"), stage, usd)
    spent = (f.get("run_usd") or {}).get(unit)
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
    usd, vusd = stage_spent(f, stage, ours, s, both=True)
    row["stage_usd"] = usd
    if vusd:
        row["void_usd"] = vusd      # shown apart: off the ceiling by his card of 2026-11-18
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
    base = cfg
    mods = st.setdefault("mods", {})
    live_total = occupancy(facts)
    drivers = live_drivers(facts)
    games_of = driver_games(facts)
    deploying = game_deploy_drivers(st)     # a deploy unit drives its game too
    drivers += list(deploying)
    games_of.update(deploying)
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
            # every tick line names a game by its name, ArchBig or ArchSmall (game_names.name_text), never "game a"
            row["decision"], row["why"] = decision, _GN.name_text(why) if isinstance(why, str) else why
            if need:
                row["need"] = "%s: %s" % (mod, _GN.name_text(need))
        put.row = row

        try:    # the mod's own settings: a pinned mod's builders on its model, their caps scaled (mod_model.for_mod)
            cfg = MM.for_mod(base, mod)
        except KeyError as e:       # role_launch.UnknownModel: a pin it cannot price launches nothing, said by name
            put("model_unknown", str(e), "its builder model pin cannot be priced (%s); `pipe model %s default` lifts it"
                % (e, mod))
            continue
        cap = cfg.get("cap_usd")
        cap_ok = isinstance(cap, (int, float)) and not isinstance(cap, bool) and cap > 0
        if cfg.get("_pin"):
            row["pin"] = cfg["_pin"]
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
                if row.get("cert_reds"):            # the offline builder on red deciders: a run slot, no game
                    live_total += 1
                elif not row.get("cert_rerun_key"):     # a zero-token rerun takes no run slot and drives no game
                    live_total += 0 if row.get("game_deploy_start") else 1      # a deploy unit drives a game, no slot
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
            if book:    # the steward, fixer and road-back holder books govern their own retries
                s["last_run"]["autonomy"] = book
            prog, pwhy = progressed(w, ids, f.get("bar_fp"))
            # a run first seen with no refused bars had no build work to resolve: it was no builder (a hand-launched
            # fix on a mod standing here read "0 -> 0, none resolved", and a stop on an empty set could never lift)
            idle = was == 0 and not w.get("ids")
            if idle:
                s["last_run"]["not_judged"] = "no build work was owed when it started (0 refused bars)"
            hand = not book and not idle and not tick_builder(s, w.get("unit"))
            if hand:
                s["last_run"]["not_judged"] = "not a builder the tick launched (no launches or pilot_launches entry)"
            # a VOID run (hand, or killed / timed out / no result of its own: run_void.py) is never judged: it spends
            # no try at these refusals (RIMMANDRAKE_VOID_SYSTEM_KILLED_RUNS_NO_TRIAL_SPENT)
            vwhy = void_why(w.get("unit"))
            if vwhy:
                s["last_run"]["not_judged"] = "VOID: %s" % vwhy
            elif not prog and not book and not idle and not hand:
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
            # a stop written before the progress test exempted this book
            s.pop("stopped")
            row["stop_lifted"], stop = "it judged the %s run %s as a builder" % (
                autonomy_book(s, lr["unit"]), lr["unit"]), None
        sm = _STOP_RUN.match(str((stop or {}).get("why") or ""))
        if (stop and sm and stop.get("ids") != [] and not stop.get("ceiling") and not stop.get("launch_failed")
                and not autonomy_book(s, sm.group(1)) and not tick_builder(s, sm.group(1))):
            # a stop written before the progress test spared runs the tick did not launch as builders
            s.pop("stopped")
            row["stop_lifted"], stop = "it judged run %s, not a builder the tick launched, as a builder" % (
                sm.group(1)), None
        if (stop and stop.get("ids") == [] and str(stop.get("why")).startswith("run ") and not stop.get("ceiling")
                and " 0 -> " in str(stop.get("why"))):
            # written before a run seen with no refused bars stopped being judged as a builder: nothing shrinks an
            # empty set, so it held the mod for good
            s.pop("stopped")
            row["stop_lifted"], stop = "it was written on a run that had no refused bars to resolve", None
        if (stop and stop.get("launch_failed") and stop.get("code") and cfg.get("_code")
                and stop["code"] != cfg["_code"] and AUT.tries_left(cfg, mod, stop.get("tries"))):
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
    return _off_ceiling(f, s, spent, "offline_build")[0]     # less every VOID run: his card of 2026-11-18 (void_units)


def stale_red(cv):
    """-> the deciders a certificate refuses on ran_on_this_build: their recorded run (red or green) is of an older build
    or command, so only a rerun can say what they read now (design/specs/2026-11-23-stale-red-rerun-first/boundary.md)."""
    return {r.get("test") for r in (cv.get("rows") or [] if isinstance(cv, dict) else [])
            if r.get("status") == "REFUSED" and r.get("clause") == "ran_on_this_build" and r.get("test")}


def red_deciders(f):
    """-> the offline deciders the certificate refuses as recorded red (clause green) on THIS build, sorted. A red run that
    is also stale is the zero-token rerun's, never a builder's (stale_key;
    RIMMANDRAKE_RERUN_STALE_RED_DECIDER_BEFORE_ANY_BUILDER_RUNS: Explosive Knockback's T_SETTINGS_SCREEN was red on its
    old unscoped command)."""
    cv = f.get("certificate")
    if not isinstance(cv, dict):
        return []
    stale = stale_red(cv)
    return sorted({r.get("test") for r in cv.get("rows") or [] if r.get("status") == "REFUSED"
                   and r.get("clause") == "green" and r.get("test") and r.get("test") not in stale})


def red_seen_owed(f):
    """-> the deciders a certificate refuses on red_seen ALONE (every refused row is clause red_seen: an edited decider
    owes its planted-fault proof), sorted; [] when it refuses anything else too, or nothing. Measured 2026-11-20: Gimme
    Some Slack sat about 2.5 h on such a certificate, because stale_key drops red_seen and cert_red_decide read only
    green (RIMMANDRAKE_RESUME_WRONG_CHECK_WORKER_WITH_MOD_FIX_EXTENSION)."""
    cv = f.get("certificate")
    ref = [r for r in (cv.get("rows") or [] if isinstance(cv, dict) else []) if r.get("status") == "REFUSED"]
    if not ref or any(r.get("clause") != "red_seen" for r in ref):
        return []
    return sorted({r.get("test") for r in ref if r.get("test")})


CERT_BOOK = {"red": "cert_red", "red_seen": "cert_red_seen"}     # the state each kind books its one try in


def red_seen_paid(f, since):
    """-> the deciders refused on red_seen whose newest red proof was recorded after SINCE (epoch s): a try launched at
    SINCE was paid, so the refusal is of a later edit and is new work (Gimme Some Slack, 2026-11-23 7:20 PM PST: a try of
    2026-11-21 stopped the mod on deciders proved on 11-23 and edited after). An absent or unreadable time pays nothing."""
    paid, cv = set(), f.get("certificate")
    for r in (cv.get("rows") or [] if isinstance(cv, dict) else []):
        if r.get("status") != "REFUSED" or r.get("clause") != "red_seen" or not r.get("test"):
            continue
        try:
            at = dt.datetime.strptime(str(r.get("proof_at")), "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=dt.timezone.utc).timestamp()
        except ValueError:
            continue
        if at > since:
            paid.add(r["test"])
    return paid


def cert_red_decide(cfg, s, f, row, put, now, account, live_total, cap, releases=None, to="blind_challenge",
                    what="the move into the blind challenge"):
    """At the offline build waiting on its certificate, with deciders recorded red (FlowWorks, 2026-11-16 1:36 AM PST:
    "owes nothing launchable at offline_build (certificate) and has no open road-back item", reds
    T_FETCH_FALLEN_OFFLINE, T_LIQUID_COATING_OFFLINE, T_TOSS_FLAME_OFFLINE). -> "launch" (row["cert_reds"]: execute
    files the item that owes each red decider and launches ONE builder on them, cert_launch), "decided" (the row put:
    settling, stopped, or a gate), or None (no reds: the certificate wait stands; stale stamps alone are
    `certificate --run`). Never a second automatic try at the same reds: another only once the red set shrank, or a
    launch that never started on a transient fault, within launch_tries. The same route serves a red decider found at
    the blind cycle or in-game visit gate (cert_wait; TO and WHAT name the gate the certificate refuses): the builder is
    the offline build's, at its cap and ceiling, booked as offline_build spend, and the record does not move
    (RIMMANDRAKE_ROUTE_RED_DECIDER_AT_VISIT_AND_CYCLE_GATES). A try booked at another stage is not this gate's try."""
    mod = row["mod"]
    reds, kind = red_deciders(f), "red"
    if not reds:
        # a certificate that refuses on red_seen alone gets the same one run, whose brief records the proof
        reds, kind = red_seen_owed(f), "red_seen"
    if not reds:
        return None
    row["cert_reds"], row["cert_kind"] = reds, kind
    row["cert_gate"] = {"stage": f.get("stage"), "to": to, "what": what}
    clause = "green" if kind == "red" else "red_seen"
    row["certificate"] = {"rows": [r for r in (f.get("certificate") or {}).get("rows") or []
                                   if r.get("clause") == clause and r.get("test") in reds]}
    row["known_red"] = {t: (f.get("known_red") or {}).get(t) for t in reds if (f.get("known_red") or {}).get(t)} \
        if kind == "red" else {}
    prior = s.get(CERT_BOOK[kind]) if isinstance(s.get(CERT_BOOK[kind]), dict) else None
    if prior and prior.get("stage", "offline_build") != f.get("stage"):
        prior = None
    if prior and prior.get("unit") and 0 <= now - float(prior.get("at") or 0) < float(cfg.get("settle_s", 180)):
        put("settling", "the builder %s on red deciders %s started %d s ago" % (
            prior["unit"], ", ".join(prior.get("tests") or []), now - float(prior.get("at") or 0)))
        return "decided"
    # a launch that never started is tried again on a transient fault, or once the pipeline's code has changed since it
    # failed (FlowWorks' first was refused over the packet line before the packet builder learned to fit it), within
    # launch_tries (RIMMANDRAKE_RETRY_FAILED_LAUNCH_ONCE_CODE_CHANGES)
    retry = bool(prior and not prior.get("unit") and AUT.tries_left(cfg, mod, prior.get("tries"))
                 and (AUT.transient(str(prior.get("failed") or "")) or (
                     cfg.get("_code") and prior.get("code") != cfg["_code"])))
    # "the same reds" share a test with the last try; a disjoint set is new work that try never saw (Pyrelands' T_SITE
    # after a 2026-11-22 try on T_FUZZ and T_SETTINGS_SCREENS read as the same, 2026-11-23: test a-new-set-gets-its-own-try)
    same = set(reds) & set((prior or {}).get("tests") or [])
    if same and kind == "red_seen" and prior.get("unit"):
        same -= red_seen_paid(f, float(prior.get("at") or 0))
    if prior and not retry and same and not set(reds) < set(prior.get("tests") or []):
        # a red_seen set is green: its stop never says "red" (2026-11-23: the Conductor filed four red deciders to repair)
        on = "red deciders" if kind == "red" else "edited deciders (green, red proof owed)"
        why = ("the %s %s on %s %s ended and %s %s" % (
            "builder" if kind == "red" else "red-proof run", prior["unit"], on, ", ".join(prior.get("tests") or []),
            ", ".join(reds), "still red" if kind == "red" else
            "still owe a recorded red proof (maturation.py red-seen)") if prior.get("unit") else
            "the launch on %s %s failed: %s" % (on, ", ".join(prior.get("tests") or []), prior.get("failed")))
        put("stopped", why, "stopped, %s; never a second automatic try at the same deciders (items %s; "
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
        if row.get("decision") == "slots_full":
            row["waits_on"] = cert_red_waits(row)
        return "decided"
    row["cap"] = cap
    put("launch", "its certificate refuses %d %s (%s) and nothing is live on it: the item owing each and "
        "one %s on them%s (%s)" % (len(reds), "red decider(s)" if kind == "red" else
                                   "edited decider(s) on red_seen alone (no recorded red run)", ", ".join(reds),
                                   "builder" if kind == "red" else "run that records the proof (maturation.py red-seen)",
                                   ", a retry after a transient fault" if retry else "", account[1]))
    return "launch"


def cert_red_waits(row, ahead=()):
    """-> what a red-decider row past max_live waits on: the offline builder, never its certificate."""
    return "a free slot for one offline builder on red deciders %s (the road back to the offline build%s)%s" % (
        ", ".join(row.get("cert_reds") or []), ", from %s" % row["cert_gate"]["what"]
        if (row.get("cert_gate") or {}).get("stage") not in (None, "offline_build") else "",
        " (launch priority: %s first)" % ", ".join(ahead) if ahead else "")


# A visit stopped by its spend cap is continued once by detached_helper's own continuation, never left at
# visit_unfinished for a hand (RIMMANDRAKE_RESUME_CAPPED_VISIT_BY_TICK_PYRELANDS_SAT_IDLE: Pyrelands visit 2 had 42 of
# 46 rows when capped, 2026-11-20 9:37 PM PST, and sat 85 min). The 1 keeps the cap meaningful (danger: a runaway
# unattended burn, owner 2026-11-12): at most twice the visit's cap.
INGAME_CONTINUE_ON_CAP = 1

RERUN_MAX_S = 15 * 3600     # a certificate rerun unit's bound (RuntimeMaxSec); FlowWorks' C# suite alone ran 531 s # budget: danger=a hung rerun holds the one pool clone; longest=5325s (control.db, 31 cert_rerun runs, 14 days to 2026-11-24)


def stale_key(cv):
    """-> a key for a certificate whose every refusal is a stale stamp (clause ran_on_this_build): the stale deciders and
    the build each must carry now (would_pass names it), so a new build is a new key. None when it does not refuse, or
    refuses on anything a rerun cannot pass (a red decider on this build, an unregistered one, a bar with no decider). A red_seen
    refusal (an edited decider owes a planted-fault proof) neither starts nor blocks the rerun: the rerun clears the stale
    stamps and the red proof stays the certificate's own wait, with its fix (RIMMANDRAKE_RECORD_RED_SEEN_PER_TEST_OR_PASSED_GREEN)."""
    if not isinstance(cv, dict):
        return None
    stale = stale_red(cv)
    # a green refusal of a stale decider is a red read on an older build or command: the rerun decides it
    ref = [r for r in cv.get("rows") or [] if isinstance(r, dict) and r.get("status") == "REFUSED"
           and r.get("clause") != "red_seen" and not (r.get("clause") == "green" and r.get("test") in stale)]
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

    def wait(said):
        # never a wait for a hand (form_fault; RIMMANDRAKE_FILE_FLOWWORKS_TICK_NEVER_RERAN_ITS_OWN_CERTIFICATE: FlowWorks
        # sat on this line 80 min, 2026-11-20): the rerun is not repeated on this build, and one repair run is owed
        # with the evidence (form_repair_step starts it; the same evidence after a finished repair counts once)
        cert_put(put, mod, to, why or f.get("certificate_why"), fix or f.get("certificate_fix"), what)
        text = "%s; %s; the step never reruns the same build" % (row.pop("need", None) or "%s: certificate at %s" % (
            mod, what), said)
        held = FF.owe_repair(s, text, "%s certificate" % mod, now, book="cert_rerun", key=key)
        if held:
            s.setdefault("system_faults", []).append({"at": now, "book": "cert_rerun", "key": key, "unit": None,
                                                      "cause": held, "n": 1})
        row["why"] = "%s; repairing: %s" % (row.get("why") or "", FF.what_of(text))
        return "decided"
    age = now - float((prior or {}).get("at") or 0)
    if prior and prior.get("unit") and not mine and 0 <= age < RERUN_MAX_S:
        # still running, on this build or an older one: never a second worker beside it in the one pool clone
        put("live", "certificate rerun %s (zero tokens) started %d s ago on %s" % (
            prior["unit"], age, "this build" if prior.get("key") == key else "an older build; this build reruns after it"))
        # the rerun is the named wait: unnamed, the classifier read 'waiting on nothing running' and called the mod
        # stalled while the rerun worked (RIMMANDRAKE_NAME_CERT_RERUN_AS_THE_WAIT_NOT_A_STALL)
        row["waits_on"] = "%s (zero-token certificate rerun)" % prior["unit"]
        return "decided"
    void = None
    if prior and prior.get("key") == key:
        # a rerun that left no result of its own by its bound was killed or timed out: void_system, it spends no rerun
        # of this build, so it is started again within launch_tries (RIMMANDRAKE_CLOSE_VOID_GAPS_REVIEW_FOUND_SIX_MORE)
        if prior.get("unit") and not mine and AUT.tries_left(cfg, mod, prior.get("tries")):
            void = "the rerun %s left no result within %d s (killed or timed out): void_system" % (
                prior["unit"], RERUN_MAX_S)
        elif prior.get("unit") and mine and mine.get("published") and mine.get("key_after") != key \
                and f.get("cert_rerun_landed") is False:
            # the rerun cleared this key in its pool clone and published; this tree has not synced that commit, so the
            # certificate read here is older than the rerun: wait for the sync, never a repair (False only: an
            # unreadable tree keeps the route below, so this is never a silent wait)
            row["waits_on"] = "%s's published %s to reach this tree (zero-token certificate rerun)" % (
                prior["unit"], mine["published"])
            put("live", "certificate rerun %s published %s; this tree has not synced it yet, so the certificate read "
                "here predates it" % (prior["unit"], mine["published"]))
            return "decided"
        elif prior.get("unit") and mine and (mine.get("race") or AUT.wait_refusal(str(mine.get("error") or "")) or (
                "stopped on a conflict in: design/concepts/%s/version/test_table.json" % mod) in str(mine.get("error"))):
            # the rerun was refused a pool clone, a cause that ends by itself: it starts again, no try spent, never a
            # form repair (RIMMANDRAKE_UNBLOCK_PYRE_VISIT_SIX_HELD_BY_AN_ART_PICK_THAT_IS_HIS)
            void = "the rerun %s waited on a cause that ends by itself (no try spent): %s" % (
                prior["unit"], FF.what_of(mine["error"]))
            row["cert_rerun_wait"] = True
        elif prior.get("unit"):
            return wait("the zero-token certificate rerun %s on this build %s" % (prior["unit"], (
                "ended (ok %s, published %s%s)" % (mine.get("ok"), mine.get("published") or "nothing",
                                                   ", error: %s" % mine["error"] if mine.get("error") else "")
                if mine else "left no result within %d s" % RERUN_MAX_S)))
        retry = void or AUT.tries_left(cfg, mod, prior.get("tries")) and (
            AUT.transient(str(prior.get("failed") or "")) or code_changed(cfg, prior))
        if not retry:
            return wait("the certificate rerun on this build did not start (%s)" % prior.get("failed"))
    elif mine and mine.get("key_after") == key:
        return wait("the certificate rerun %s left its own build stale (a decider that changes what it reads?)"
                    % prior["unit"])
    row["cert_rerun_key"] = key
    if void:
        row["cert_rerun_void"] = void
    n = len({r.get("test") for r in (f.get("certificate") or {}).get("rows") or [] if r.get("status") == "REFUSED"})
    put("launch", "its certificate refuses only stale stamps (%d decider(s) last run on an older build), no decider "
        "red: one zero-token `maturation.py certificate %s --run`, detached, for this build%s" % (
            n, mod, "; again: %s" % void if void else ""))
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
                       "tries": int(prior.get("tries") or 1) if row.get("cert_rerun_wait") and prior.get("key") == key
                       else int(prior.get("tries") or 1) + 1 if prior.get("key") == key and (
                           not prior.get("unit") or row.get("cert_rerun_void")) else 1}
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


def rerun_landed(root, res):
    """-> True when the rerun's published commit is in root's HEAD, False when root is a git tree that does not hold it
    yet (the tick's tree syncs after the rerun's pool clone published), None when there is no published commit or the
    tree cannot be read. RIMMANDRAKE_REPAIR_FLOWWORKS_FORM_REFUSAL_AT_THE_RUN_THREE (2026-11-21): FlowWorks' rerun
    published b65672378c and the tick, 41 s later in a tree without it, read the old stale stamps and owed a repair."""
    sha = res.get("published") if isinstance(res, dict) else None
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{7,40}", sha):
        return None
    try:
        h = subprocess.run(["git", "-C", root, "rev-parse", "--verify", "-q", "HEAD"], capture_output=True, text=True,
                           timeout=60)
        if h.returncode != 0:
            return None
        c = subprocess.run(["git", "-C", root, "cat-file", "-e", sha + "^{commit}"], capture_output=True, text=True,
                           timeout=60)
        if c.returncode != 0:
            return False                     # not even fetched here yet
        a = subprocess.run(["git", "-C", root, "merge-base", "--is-ancestor", sha, "HEAD"], capture_output=True,
                           text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return {0: True, 1: False}.get(a.returncode)


def cert_rerun_unit(mod, key, runner=subprocess.run, now=None):
    """Start `maturation_dispatch.py cert-rerun MOD` as its own transient user unit (bounded by RERUN_MAX_S; the 60 s
    tick never waits on it). -> (rc, text, unit)."""
    unit = "rm-cert-rerun-%s-%d" % (re.sub(r"[^a-z0-9]+", "-", mod.lower()).strip("-"), int(now or time.time()))
    log = os.path.join(rerun_dir(), "%s.log" % mod)
    argv = ["--user", "--quiet", "--collect", "-p", "RuntimeMaxSec=%d" % RERUN_MAX_S,
            "-p", "StandardOutput=append:" + log, "-p", "StandardError=append:" + log, "--working-directory", REPO,
            "--setenv", "PATH=" + os.environ.get("PATH", "/usr/bin:/bin"), "--setenv", "RM_MATURATION_DISPATCH_DIR=" + sdir(),
            "--", sys.executable, os.path.abspath(__file__), "cert-rerun", mod, "--key", key, "--unit", unit]
    import control as C     # the one admission point (control.py)
    try:
        r = C.launch_unit(argv, {"family": "cert_rerun", "unit": unit, "mod": mod}, runner=runner, capture_output=True,
                          # budget: danger=a hung launch holds the dispatch tick; longest=1.3s (admission to start of 1057 runs,
                          # budget: control.db)
                          text=True, timeout=60, stdin=subprocess.DEVNULL)
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
                r.returncode, (r.stdout or "") + (r.stderr or "")))
        res.update(ok=bool(cv.get("ok")), key_after=stale_key(cv), ran=cv.get("run"))
        g = runner(["git", "status", "--porcelain", "--", rel], cwd=clone, timeout=120, **kw)  # budget: class=call
        if (g.stdout or "").strip():
            p = runner(["./publish", "-m", "maturation: %s certificate rerun on its build (dispatch, zero tokens)" % mod,
                        rel], cwd=clone, timeout=21600, **kw)  # budget: class=publish
            m = re.search(r"PUBLISHED ([0-9a-f]{7,40})", (p.stdout or "") + (p.stderr or ""))
            out = (p.stdout or "") + (p.stderr or "")
            hit = re.search(r"stopped on a conflict in: (\S+?)\.?\s", out + " ")
            if m:
                res["published"] = m.group(1)
            elif hit and hit.group(1).rstrip(".") == rel:
                # a newer table reached origin while the rerun worked (Pyrelands, 2026-11-22: a testq-blocks commit in
                # its 449 s): the stamp commit is derived and this clone has one owner, so it is dropped and the tick
                # starts the rerun again on the new table (cert_rerun_decide), never a hand merge
                runner(["git", "reset", "--hard", "origin/main"], cwd=clone, timeout=120, **kw)  # budget: class=call
                res.update(race=True, error="RERUN RACE: a newer %s reached origin while the rerun worked; its stamp "
                                            "commit was dropped and the rerun starts again" % rel)
            else:
                res["error"] = "publish exit %d: %s" % (p.returncode, out)
        else:
            res["note"] = "the table did not change"
    except Exception as e:      # noqa: BLE001  the result says what failed; the tick reads it
        res["error"] = "%s: %s" % (type(e).__name__, e)
    res["end"] = now()
    _write(os.path.join(rerun_dir(), "%s.json" % mod), res)
    return res


# ---- the deploy of a mod's game copy, in its own unit (RIMMANDRAKE_RUN_VISIT_DEPLOY_OUTSIDE_TICK_HELD_IT_FOURTEEN_MIN;
# design/specs/2026-11-24-game-deploy-own-unit/boundary.md): the plan, the --apply and the second plan held the tick 998 s
# on 2026-11-24, and no other mod could start. One book per mod, s["game_deploy"]: {unit, game, kind, key, at, tries,
# ended, result, stale}. Only the tick writes it; the unit writes its result file.

DEPLOY_MAX_S = 10 * 998    # the unit's hang guard: a hung deploy would hold the game's lock for good; the one measured ran 998 s  # budget: class=deploy


def game_deploy_dir():
    d = os.path.join(sdir(), "game_deploy")
    os.makedirs(d, exist_ok=True)
    return d


def game_deploy_result(mod):
    """-> the last deploy unit's result for mod (game_deploy_worker writes it), or None."""
    r = _read(os.path.join(game_deploy_dir(), "%s.json" % mod), None)
    return r if isinstance(r, dict) else None


def game_deploy_unit(mod, game, kind, purpose, seat="BENCH", now=None):
    """Start `maturation_dispatch.py game-deploy MOD` as its own transient user unit. -> (rc, text, unit)."""
    unit = "rm-game-deploy-%s-%d" % (re.sub(r"[^a-z0-9]+", "-", mod.lower()).strip("-"), int(now or time.time()))
    log = os.path.join(game_deploy_dir(), "%s.log" % mod)
    argv = ["--user", "--quiet", "--collect", "-p", "RuntimeMaxSec=%d" % DEPLOY_MAX_S, "-p", "Nice=10",
            "-p", "StandardOutput=append:" + log, "-p", "StandardError=append:" + log, "--working-directory", REPO,
            "--setenv", "PATH=" + os.environ.get("PATH", "/usr/bin:/bin"), "--setenv", "RM_MATURATION_DISPATCH_DIR=" + sdir(),
            "--", sys.executable, os.path.abspath(__file__), "game-deploy", mod, "--game", game, "--kind", kind,
            "--purpose", purpose, "--seat", seat, "--unit", unit]
    import control as C     # the one admission point (control.py)
    try:
        r = C.launch_unit(argv, {"family": "game_deploy", "unit": unit, "mod": mod}, capture_output=True, text=True,
                          timeout=1800, stdin=subprocess.DEVNULL)  # budget: class=call
    except (OSError, subprocess.SubprocessError) as e:
        return 1, "systemd-run failed: %s: %s" % (type(e).__name__, e), None
    if r.returncode:
        return r.returncode, "systemd-run exit %d: %s" % (r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()), None
    return 0, "STARTED %s: %s on %s, zero tokens (log %s)" % (unit, purpose, _GN.show(game), log), unit


def game_deploy_worker(mod, game, kind, purpose, unit, seat="BENCH", runner=subprocess.run, take=None, now=time.time):
    """The unit's body: in a pool clone synced to origin/main (the tick's own tree may sync under a deploy), one per game,
    `maturation.py game-repair`; its verdict is written for the tick (game_deploy_result). -> the result."""
    res = {"mod": mod, "unit": unit, "game": game, "kind": kind, "at": now(), "state": "fail", "text": UNM, "sha": None,
           "generation": None, "paths": []}
    try:
        clone, said = (take or DH.take_clone)("RIMMANDRAKE_DEPLOY_GAME_BUILD_TO_%s" % _GN.show(game).upper())
        res["clone"] = clone
        r = runner([sys.executable, os.path.join("src", "RimMandrake", "rimflow", "maturation.py"), "game-repair", mod,
                    "--game", game, "--kind", kind, "--purpose", purpose, "--seat", seat], cwd=clone,
                   capture_output=True, text=True, stdin=subprocess.DEVNULL)    # bounded by the unit's RuntimeMaxSec
        got = None
        for ln in reversed((r.stdout or "").strip().splitlines()):
            try:
                got = json.loads(ln)
                break
            except ValueError:
                continue
        if isinstance(got, dict) and got.get("state") in ("ok", "wait", "fail"):
            res.update({k: got.get(k) for k in ("state", "text", "sha", "generation", "paths")})
        else:
            res["text"] = "game-repair exit %d printed no verdict: %s" % (
                r.returncode, (r.stdout or "") + (r.stderr or ""))
    except Exception as e:      # noqa: BLE001  the result says what failed; the tick reads it
        res["text"] = "%s: %s" % (type(e).__name__, e)
        if AUT.wait_refusal(res["text"]):
            res["state"] = "wait"
    res["end"] = now()
    _write(os.path.join(game_deploy_dir(), "%s.json" % mod), res)
    return res


def unit_active(unit):
    """-> True when the unit runs, False when systemd says it ended or is not there, None when it could not look."""
    import role_launch as RL
    state = RL.unit_state(unit)
    return None if state == "unknown" else state not in ("inactive", "failed", "not-found")


def _generation(game):
    import game_lock as GL
    return GL.query(game, pipe=False).get("generation")


def deploy_stale(root, res, generation=None):
    """-> why an ended visit deploy no longer says what the game plays, or None. A source change under its paths, another
    run's hold of that game since (a helper may have deployed its own build), or a reading that could not be made. A tree
    that does not hold the deploy's commit yet is behind the game's copy, so it is not stale."""
    sha = res.get("sha")
    if not sha:
        return "the deploy recorded no commit"
    try:
        if (generation or _generation)(res.get("game")) != res.get("generation"):
            return "another run took a hold of %s since the deploy" % _GN.show(res.get("game") or "a")
        kw = {"capture_output": True, "text": True, "timeout": 60, "stdin": subprocess.DEVNULL}
        if subprocess.run(["git", "-C", root, "rev-parse", "--verify", "-q", "HEAD"], **kw).returncode:
            return "the tree's commit could not be read"
        if subprocess.run(["git", "-C", root, "cat-file", "-e", sha + "^{commit}"], **kw).returncode:
            return None
        if subprocess.run(["git", "-C", root, "merge-base", "--is-ancestor", sha, "HEAD"], **kw).returncode == 1:
            return None
        rc = subprocess.run(["git", "-C", root, "diff", "--quiet", sha, "HEAD", "--"] + list(res.get("paths") or ["src"]),
                            **kw).returncode
    except Exception as e:      # noqa: BLE001  could not look is never fresh
        return "the deploy's freshness could not be read (%s: %s)" % (type(e).__name__, e)
    return None if rc == 0 else "%s changed since %s" % (", ".join(res.get("paths") or ["src"]), sha[:10]) \
        if rc == 1 else "git diff exited %d" % rc


def game_deploy_running(s):
    gd = s.get("game_deploy")
    return gd if isinstance(gd, dict) and gd.get("unit") and not gd.get("ended") else None


def game_deploy_sync(root, st, now, fx=None):
    """Before the decision: each mod's running deploy unit is read. Its own result ends it; a unit that systemd says is
    gone with no result ended as `lost`; one that could not be looked at still runs. An ended visit deploy's freshness is
    read again (deploy_stale)."""
    fx = fx or {}
    active, stale = fx.get("unit_active") or unit_active, fx.get("deploy_stale") or deploy_stale
    for mod, s in (st.get("mods") or {}).items():
        gd = s.get("game_deploy") if isinstance(s, dict) else None
        if not isinstance(gd, dict):
            continue
        if game_deploy_running(s):
            res = game_deploy_result(mod)
            if not (res and res.get("unit") == gd["unit"]):
                if active(gd["unit"]) is not False:
                    continue
                res = game_deploy_result(mod)       # it may have written its result between the two reads
                if not (res and res.get("unit") == gd["unit"]):
                    res = {"unit": gd["unit"], "state": "lost", "game": gd.get("game"), "text":
                           "the deploy unit %s ended and left no result (killed, or it never ran)" % gd["unit"]}
            gd.update(ended=now, result=res)
        if (gd.get("result") or {}).get("state") == "ok" and gd.get("kind") == "visit":
            gd["stale"] = stale(root, gd["result"])


def game_deploy_drivers(st):
    """-> {unit: game} of the running deploy units: each drives its game as a live driver does (it may not hold the lock
    yet: its clone is synced first)."""
    out = {}
    for s in (st.get("mods") or {}).values():
        gd = game_deploy_running(s) if isinstance(s, dict) else None
        if gd:
            out[gd["unit"]] = gd.get("game") or "a"
    return out


def game_deploy_ended(cfg, mod, s, kind, key):
    """-> the ended deploy's result that this act may use, or None when a deploy is to be started (none yet, another act's,
    a wait, a stale one, or a lost one with a try left)."""
    gd = s.get("game_deploy")
    if not isinstance(gd, dict) or not gd.get("ended") or (gd.get("kind"), gd.get("key")) != (kind, key):
        return None
    res = gd.get("result") or {}
    if res.get("state") == "wait" or (res.get("state") == "ok" and gd.get("stale")):
        return None
    if res.get("state") == "lost" and AUT.tries_left(cfg, mod, gd.get("tries")):
        return None
    return res


def game_deploy_live(put, gd, what):
    """The row of a mod whose deploy unit runs: live, and the unit is what it waits on."""
    put("live", "the deploy unit %s (zero tokens) on %s: %s" % (gd["unit"], _GN.show(gd.get("game") or "a"), what))


def game_deploy_launch(cfg, st, row, kind, key, game, purpose, now, fx):
    """Start the deploy unit and book it. A start that failed for a cause that ends by itself is a wait; any other is the
    deploy's failure, which the act it serves reads on the next tick. -> True when up. Tries count the units that were
    lost or never started, for one act."""
    mod, s = row["mod"], st["mods"][row["mod"]]
    prior = s.get("game_deploy") if isinstance(s.get("game_deploy"), dict) else {}
    same = (prior.get("kind"), prior.get("key")) == (kind, key)
    tries = int(prior.get("tries") or 1) if same else 1
    if same and (prior.get("result") or {}).get("state") == "lost":
        tries += 1
    try:
        rc, text, unit = (fx.get("game_deploy") or game_deploy_unit)(mod, game, kind, purpose, cfg.get("seat", "BENCH"))
    except Exception as e:      # noqa: BLE001  a start that raised is a start that failed
        rc, text, unit = 1, "%s: %s" % (type(e).__name__, e), None
    unit = unit if rc == 0 else None
    gd = {"unit": unit, "game": game, "kind": kind, "key": key, "at": now, "tries": tries}
    for k in ("release", "refund"):     # the run these belong to has not started: its own launch spends them
        row.pop(k, None)
    if unit:
        s["game_deploy"] = gd
        row.update(decision="live", aut=None, waits_on="%s (zero-token deploy of its game copy)" % unit,
                   why="%s; the mod is live until it ends, and the act it serves runs on the next tick" % text)
        return True
    if AUT.wait_refusal(text):
        row.update(decision="launch_wait", aut=None, why="the deploy of %s waits on a cause that ends by itself: %s" % (
            mod, text))
        return False
    s["game_deploy"] = dict(gd, ended=now, result={"unit": None, "state": "fail", "game": game, "text":
                                                   "the deploy unit did not start: %s" % text})
    row.update(decision="launch_wait", aut=None, why="the deploy unit of %s did not start, and the next tick reads that: %s"
               % (mod, text))
    return False


def cert_item_id(mod, test, known, kind="red"):
    """-> a rimflow name for the item owing red decider `test`: RIMMANDRAKE_GREEN_<MOD>_<TEST words>_RED_DECIDER (kind
    red_seen: RIMMANDRAKE_PROVE_<MOD>_<TEST words>_RED_SEEN_OWED), test words dropped from the end until it fits
    (fit_name)."""
    words = ["?" + w for w in re.split(r"[^A-Z0-9]+", str(test).upper()) if w]
    head, tail = (["RIMMANDRAKE", "GREEN"], ["RED", "DECIDER"]) if kind == "red" else (
        ["RIMMANDRAKE", "PROVE"], ["RED", "SEEN", "OWED"])
    return fit_name(head + ["@" + mod] + words + tail, known)


RESUME_WARM_S = 55 * 60     # a resume within the 1 h prompt-cache TTL reads its context warm; measured 2026-11-20, 15 warm
                            # resumes cost 0.85M weighted against 13.8M for 18 cold ones (report, context-kept-not-reloaded)


def _decider_files(root, mod, tests):
    tt, _ = M.read_json(root, mod, "version/test_table.json")
    return {t: ((tt or {}).get("tests") or {}).get(t, {}).get("file") for t in tests}


def _commit_time(root, path):
    """-> a probe_result answer: the commit time of the last change to path on HEAD (value, epoch seconds), empty when
    no commit touched it, or could_not_look naming why."""
    import probe_result as PR
    try:
        r = subprocess.run(["git", "-C", root, "log", "-1", "--format=%ct", "--", path], capture_output=True, text=True,
                           timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        return PR.could_not_look("git log %s: %s" % (path, e))
    if r.returncode != 0:
        return PR.could_not_look("git log %s exited %d" % (path, r.returncode))
    out = r.stdout.strip()
    return PR.value(float(out)) if out.isdigit() else PR.empty()


def editing_session(root, mod, tests, now, fx=None):
    """-> (session, unit, why): the one detached run whose window [at, ended] holds the last commit to a decider's
    file, when it ended under RESUME_WARM_S ago and recorded its session; else (None, None, why it starts fresh). The run
    that edited the test holds the knowledge of the fault it planted (report, context-kept-not-reloaded, change 5)."""
    fx = fx or {}
    files = (fx.get("decider_files") or _decider_files)(root, mod, tests)
    read = [(fx.get("commit_time") or _commit_time)(root, p) for p in sorted({p for p in files.values() if p})]
    times = [float(t.value) for t in read if getattr(t, "kind", None) == "value"]
    if not times:
        return None, None, "no decider file with a commit git can read (%s)" % (
            "; ".join(str(t) for t in read) or "the test table names no file")
    try:
        import detached_helper as DH
        recs = fx["records"]() if "records" in fx else list(DH.all_records())
    except Exception as e:      # noqa: BLE001  the records cannot be read: start fresh, and say so
        return None, None, "the run records could not be read (%s: %s)" % (type(e).__name__, e)
    ct = max(times)
    hits = [r for r in recs if isinstance(r.get("at"), (int, float)) and isinstance(r.get("ended"), (int, float))
            and r["at"] <= ct <= r["ended"] + 60]
    if len(hits) != 1:
        return None, None, "%d runs were live at the decider's last commit" % len(hits)
    r = hits[0]
    if not r.get("session"):
        return None, None, "the run %s recorded no session" % r.get("unit")
    if now - r["ended"] >= RESUME_WARM_S:
        return None, None, "the run %s ended %d min ago (its cache is cold)" % (r.get("unit"), (now - r["ended"]) // 60)
    return r["session"], r.get("unit"), "the run %s that edited the decider ended %d min ago" % (
        r.get("unit"), (now - r["ended"]) // 60)


def red_seen_brief(mod, chosen, cap, bars, gate=None):
    """The brief of the one run that records the red_seen proof a certificate refuses on alone."""
    g = gate or {}
    lines = ["# Record the red run each edited decider of %s owes (its certificate refuses on red_seen alone)" % mod, "",
             "Items: %s. Seat BENCH. Offline only: no game, no bridge, no helpers." % ", ".join(sorted(set(
                 chosen.values()))), "",
             "`maturation.py certificate %s --to %s` refuses these deciders on `red_seen`: each one's test file changed "
             "after its last recorded red run, so nobody has seen it fail since. Every other clause passes." % (
                 mod, g.get("to") or "blind_challenge"), ""]
    lines += ["- `%s` (bars %s): item %s" % (t, ", ".join(bars.get(t) or []) or "-", it) for t, it in sorted(
        chosen.items())]
    lines += ["", "For each test: write a planted fault as a patch to the CODE the test reads (never the test itself: "
              "red-seen refuses that), and run `python3 src/RimMandrake/rimflow/maturation.py red-seen %s <test> "
              "--patch <the patch>` for each one, e.g. `python3 src/RimMandrake/rimflow/maturation.py red-seen %s %s "
              "--patch <the patch>`. It applies the fault, wants the test red, and reverses it; only a red run is "
              "recorded in `design/concepts/%s/version/evidence/red_seen.json`. A planted fault the test does not "
              "catch is a real finding about the test: repair the test (red first), then record again." % (
                  mod, mod, sorted(chosen)[0] if chosen else "<test>", mod),
              "", "Land `version/evidence/red_seen.json` with `./publish -m ... <paths>`, rerun the certificate "
              "(`python3 src/RimMandrake/rimflow/maturation.py certificate %s --to %s`), and close each item with the "
              "published sha." % (mod, g.get("to") or "blind_challenge"), "", M.RED_SEEN_RULE, "", M.SELF_FIX_RULE]
    return "\n".join(lines) + "\n"


def cert_brief(mod, chosen, cap, bars, gate=None):
    """GATE (row["cert_gate"]): where the certificate refuses; None or the offline build -> the move into the blind
    challenge."""
    g = gate or {}
    to, what = g.get("to") or "blind_challenge", g.get("what") or "the move into the blind challenge"
    later = g.get("stage") not in (None, "offline_build")
    lines = ["# Find why %s's offline deciders are red, and make each one hold (%s)" % (
                 mod, "the certificate before %s; the road back to the offline build" % what if later else
                 "Stage 3: the certificate before the blind challenge"), "",
             "Items: %s. Seat BENCH. Offline only: no game, no bridge, no helpers." % (
                 ", ".join(sorted(set(chosen.values()))),), "",
             "`maturation.py certificate %s --to %s` refuses %s: these offline deciders are recorded red, and the "
             "Dispatch step routes them to you (items RIMMANDRAKE_DISPATCH_PILOT_HOLDER_RUN_ITSELF_HAND_LAUNCHED_TWICE"
             "%s):" % (mod, to, what, ", RIMMANDRAKE_ROUTE_RED_DECIDER_AT_VISIT_AND_CYCLE_GATES" if later else ""), ""]
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
              "3. Rerun `certificate %s --run`, land the table, and end with `maturation.py certificate %s --to %s` "
              "exiting 0, or a note starting `LEFT OPEN:` on each item still red: what remains, what you tried, and the "
              "map or the experiment that would settle it." % (mod, mod, to), "", M.HOW_A_BAR_HOLDS, "", M.RED_SEEN_RULE]
    return "\n".join(lines) + "\n"


def cert_launch(root, cfg, st, row, now, fx, known, do_file):
    """execute's act for cert_red_decide's launch: reuse the open item a red decider already has (its known_red, or
    the one filed for it before, or an open item under the exact name this route would file: one filed by hand), file
    one for each other, then ONE builder on all of them (a pilot's from its ledger packet as its holder). Booked in
    s["cert_red"]: the reds, the items, the unit, the stage it was found at. -> True when it started."""
    mod, s = row["mod"], st["mods"][row["mod"]]
    cfg = MM.for_mod(cfg, mod)      # its builder on red deciders: the mod's pin (idempotent on execute's own view)
    reds, kr, kind = row["cert_reds"], row.get("known_red") or {}, row.get("cert_kind") or "red"
    mine = s.setdefault("cert_red_items" if kind == "red" else "cert_red_seen_items", {})
    own = {t: cert_item_id(mod, t, set(), kind) for t in reds}
    cand = {t: kr.get(t) or mine.get(t) or (own[t] if own[t] in known else None) for t in reds}
    ended = (fx.get("ended") or (lambda ids: M.ledger_ended(root, ids)))([v for v in cand.values() if v])
    bars = {}
    for r in ((row.get("certificate") or {}).get("rows") or []):
        if r.get("test") in reds and r.get("clause") == ("green" if kind == "red" else "red_seen"):
            bars.setdefault(r["test"], []).append(r.get("bar"))
    chosen, failed = {}, None
    gate = row.get("cert_gate") or {}
    prior = s.get(CERT_BOOK[kind]) if isinstance(s.get(CERT_BOOK[kind]), dict) else {}
    if prior.get("stage", "offline_build") != gate.get("stage", "offline_build"):
        prior = {}
    for t in reds:
        if cand.get(t) and cand[t] not in ended:
            chosen[t] = cand[t]
            continue
        name = cert_item_id(mod, t, known, kind)
        title = ("%s Stage 3: offline decider %s is recorded red; make it green, offline (filed by the Dispatch step)"
                 % (mod, t) if kind == "red" else "%s: decider %s was edited and has no recorded red run; record it "
                 "with maturation.py red-seen (filed by the Dispatch step)" % (mod, t))
        why = ("delegated: maturation_dispatch.py; the certificate refuses %s as %s with no open item owing it, "
               "measured %s" % (t, "recorded red" if kind == "red" else "red_seen alone", pac(now)))
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
        brief = (cert_brief if kind == "red" else red_seen_brief)(mod, chosen, cap, bars, gate)
        do_brief = fx.get("launch_brief") or AUT.launch_brief
        # the red_seen proof: resume the run that edited the decider while its context is warm, else start fresh
        sess, sunit, swhy = editing_session(root, mod, reds, now, fx) if kind == "red_seen" else (None, None, None)
        if sess:
            do_brief = (lambda b, sid: lambda *a, **k: b(*a, session=sid, **k))(do_brief, sess)
        if (fx.get("pilot") or pilot_ledger)(root, mod):
            try:
                led = ledger_open(root, mod, "builder", brief, stage="offline_build", now=now, fx=fx)
            except Exception as e:      # noqa: BLE001  a refused grant is a launch that never started
                led, text = None, "REFUSED: %s's ledger launch failed: %s: %s" % (mod, type(e).__name__, e)
            if led:
                rc, text, unit = do_brief(item, led["brief"], cfg.get("model", "opus"), cap, cfg.get("seat", "BENCH"),
                                          env=dict(led["env"], **control_env(mod, None)))
                unit = unit if rc == 0 else None
                text = "%s; %s" % ((text or "").splitlines()[0] if text else rc,
                                   ledger_after(root, st, mod, led, unit, item, now, fx))
        else:
            rc, text, unit = do_brief(item, brief, cfg.get("model", "opus"), cap, cfg.get("seat", "BENCH"),
                                      env=control_env(mod, None))
            unit = unit if rc == 0 else None
        if unit:
            s.setdefault("launches", []).append({"unit": unit, "item": item, "at": now, "cap": cap,
                                                 "stage": "offline_build", "cert_reds": reds})
    s[CERT_BOOK[kind]] = {"tests": reds, "items": chosen, "unit": unit, "at": now, "failed": None if unit else text,
                          "code": cfg.get("_code"), "stage": gate.get("stage", "offline_build"),
                          "tries": int(prior.get("tries") or 0) + 1 if not prior.get("unit") and prior else 1}
    if kind == "red_seen" and not failed:
        s[CERT_BOOK[kind]].update(resumed=sunit if sess else None, resume_why=swhy)
    if unit:
        row.update(decision="launched", unit=unit, item=sorted(set(chosen.values()))[0], why=text,
                   items=sorted(set(chosen.values())))
        return True
    row.update(decision="launch_failed", why=str(text), need="%s: the launch on red deciders %s failed (%s); the step "
               "will not retry it on its own" % (mod, ", ".join(reds), text))
    return False


def retriable(cfg, x, killed=None, mod=None):
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
        return not x.get("failed") and x["unit"] in (killed or {}) and AUT.tries_left(cfg, mod, kills)
    if x.get("wait") and x.get("failed"):  # a wait refusal (AUT.wait_refusal) spent nothing: always tried again
        return True
    if not AUT.tries_left(cfg, mod, x.get("tries")):
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


def retried(cfg, retry, mod=None):
    return (", try %d of %d after %s" % (
        len(retry.get("killed_before") or []) + 2 if retry.get("unit") else int(retry.get("tries") or 1) + 1,
        AUT.tries_most(cfg, mod),
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


def cert_wait(f, put, mod, to, what, rerun=None, red=None):
    """PRE_JUDGEMENT_CERTIFICATE (RIMMANDRAKE_CERTIFY_BARS_BEFORE_JUDGE_RED_TEST_WENT_IN): True (the row put) when the
    certificate refuses; read before every judge or visit launch, since a mod can go red between cycles. A certificate
    that did not run lets the launch through. RERUN (cfg, s, row, now): a certificate refusing only stale stamps gets
    cert_rerun_decide's one zero-token rerun per build key -> "launch" (row["cert_rerun_key"]) or "decided"
    (RIMMANDRAKE_RERUN_STALE_CERTIFICATE_AT_VISIT_AND_CYCLE_GATES). RED (account, live_total, releases), with RERUN:
    a certificate refusing a decider recorded red takes the offline build's red-decider route first (cert_red_decide at
    the offline cap) -> "launch" (row["cert_reds"]) or "decided" (RIMMANDRAKE_ROUTE_RED_DECIDER_AT_VISIT_AND_CYCLE_GATES)."""
    cv = f.get("certificate")
    if not isinstance(cv, dict) or cv.get("ok", True):
        return False
    ref = [r for r in cv.get("rows") or [] if r.get("status") == "REFUSED"]
    why = JC.summary(cv) + "".join("; %s/%s %s: %s" % (r["bar"], r["test"], r["clause"], r["observed"]) for r in ref[:2])
    if rerun:
        cfg, s, row, now = rerun
        if red:
            account, live_total, releases = red
            cap = cfg.get("cap_usd")
            cap = cap if isinstance(cap, (int, float)) and not isinstance(cap, bool) and cap > 0 else 0
            got = cert_red_decide(cfg, s, f, row, put, now, account, live_total, cap, releases, to, what)
            if got:
                return got
        got = cert_rerun_decide(cfg, s, f, row, put, now, to, what, why, JC.first_fix(cv))
        if got:
            return got
    cert_put(put, mod, to, why, JC.first_fix(cv), what)
    return True


def decide_blind(cfg, s, f, row, put, now, account, live_total, releases=None):
    """One decision for an advancing mod at the blind challenge -> True to launch its judge. The owner's condition, 2026-11-14
    ~9 PM PST: "As long as we don't have automated loops rejecting/cycling things, we can't get into too much trouble."
    So at most blind_auto_cycles_per_visit automatic cycles per visit (a visit is keyed by the version and the visit's
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
    if owed == "resume":
        return decide_void_resume(cfg, s, f, row, put, n, vid, account, live_total, releases)
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
    retry = mine[-1] if mine and retriable(cfg, mine[-1], f.get("killed"), mod) else None
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
    per = PC.limit(mod, "blind_cycles_visit", int(cfg.get("blind_auto_cycles_per_visit", 1)))
    dec = f.get("cycle_decision")
    if dec:     # the Conductor's recorded decision opened this cycle: it allows this one, past the visit's count
        row["conductor_decision"] = "%s: %s" % (dec.get("at"), str(dec.get("text")))
    if PC.used(mod, "blind_cycles_visit", len([x for x in ours if x is not retry])) >= per and not dec:
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
    cw = cert_wait(f, put, mod, "blind_challenge", "blind cycle %s" % n, (cfg, s, row, now),
                   (account, live_total, releases))
    if cw:
        return cw == "launch"   # the offline builder on red deciders (row["cert_reds"]), a zero-token rerun
        # (row["cert_rerun_key"]), or the certificate's wait
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
        n, retried(cfg, retry, mod), account[1]))
    return True


def decide_void_resume(cfg, s, f, row, put, n, vid, account, live_total, releases=None):
    """Blind cycle n's newest booked judge run was VOIDED (maturation.blind_facts owed "resume"): it gave no verdict,
    so its exit block is interim and nothing is handed to the Conductor. The SAME judge resumes its own session
    (row["judge_resume"]: its ledger run, session and unit); with no session, or one at or past
    holder_context_ceiling_tokens, a fresh judge opens the cycle (row["judge_fresh"]). It is the cycle's own run, not a
    new automatic cycle, and it is past the certificate (which gates a cycle's opening); a blind run that started
    after the void stops it (design/specs/2026-11-23-resume-voided-blind-judge/boundary.md). -> True to launch."""
    vr = f.get("void_run") or {}
    unit = vr.get("unit")
    entry = dict(vr.get("entry") or {})
    at = entry.get("at") if isinstance(entry.get("at"), (int, float)) else 0
    after = [u for u in f.get("blind_runs") or [] if u != unit and u not in (f.get("killed") or {})
             and isinstance((f.get("blind_run_at") or {}).get(u), (int, float)) and f["blind_run_at"][u] > at]
    if after:
        put("hand_run_seen", "blind run(s) %s worked on cycle %s after its voided judge %s" % (
            ", ".join(after), n, unit),
            "blind run(s) %s worked on cycle %s after its judge %s was voided; nothing launches: the Conductor reads "
            "what they left" % (", ".join(after), n, unit))
        return False
    sid, ctx, how = (list(f.get("void_session") or ()) + [None, None, "no session reading"])[:3]
    ceiling = modledger.config()["holder_context_ceiling_tokens"]
    if sid and isinstance(ctx, int) and not isinstance(ctx, bool) and ctx < ceiling:
        row["judge_resume"] = {"run": vr.get("run"), "session": sid, "unit": unit, "context_tokens": ctx}
        what = "resume its session %s (%d of %d context tokens; %s)" % (sid, ctx, ceiling, how)
    else:
        why = (how if not sid else "session %s at %s context tokens, at or past the %d ceiling" % (
            sid, ctx if isinstance(ctx, int) else UNM, ceiling))
        row["judge_fresh"] = {"unit": unit, "why": why}
        what = "open the cycle fresh, its session cannot be resumed: %s" % why
    if not cfg.get("blind_enabled"):
        put("blind_off", "blind_enabled is off in maturation_dispatch.json",
            "blind cycle %s's voided judge is owed its resume with nothing live; the Dispatch step's blind launches "
            "are off" % n)
        return False
    cap = cfg.get("blind_cap_usd")
    if not (isinstance(cap, (int, float)) and not isinstance(cap, bool) and cap > 0):
        put("no_cap", "the settings have no positive blind_cap_usd; no judge launches without a cap")
        return False
    if reserve_refused(cfg, f, row, put, cap, "blind_challenge", s.get("blind_auto"), s, releases, killed=unit):
        return False
    if not account[0]:
        put("account_hold", account[1])
        return False
    if no_slot(cfg, live_total, put):
        return False
    row.update(cap=cap, visit_id=vid, retry_of=entry, void_run=unit)
    put("launch", "blind cycle %s: its judge %s was voided (%s), so its exit block is interim, no verdict; %s (%s)" % (
        n, unit, vr.get("void") or vr.get("class"), what, account[1]))
    return True


# The Needs Conductor line after a visit whose exit is not met (RIMMANDRAKE_REFUSE_OWN_MOD_HANDOFF_DRIVER_RENAMED_NOTHING;
# the owner, 2026-11-25: "I want Option (3) absolutely."; maturation.FIX_IN_SITTING_RULE). selftest_wrong_check_fixed_in_sitting.py.
INGAME_NOT_MET = (
    "in-game visit %s ended, exit not met (%s); nothing more launches on it: the Conductor reads %s. Only two kinds of "
    "line go down a road back, each with its red deciding test or its open hunt item: a mod fault whose cause stays "
    "unknown after a sincere attempt by the driver (its row names each thing tried), and an undecided bar. A mod fault "
    "with a known fix that the driver left is a defect of that visit: the next act is a run that fixes it on a free game "
    "(red test first, then the checks that the fix touches), not a road back. A wrong check or scene never goes back")


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
    gd = game_deploy_running(s)
    if gd:      # its game copy is half written: no exit is read from it, and nothing launches
        row["waits_on"] = "%s (zero-token deploy of its game copy)" % gd["unit"]
        game_deploy_live(put, gd, "in-game visit %s" % n)
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
    stamp = ((ex.get("build_match") or {}).get("walk") or {}).get("deploy_stamp")
    forecast = (" Dispatch used the last composed deploy's build. Verify the current build with maturation.py next %s."
                % mod) if stamp else ""
    if owed == "exit met":
        put("exit_met", "in-game visit %s: exit met (%s)" % (n, (ex.get("why") or ["-"])[0]),
            "in-game visit %s: exit met (a program's reading of %s, its build match counting every check on the walk "
            "build); the steward reads it and confirms: maturation.py advance %s --to pre_human --steward-confirms "
            "\"...\" (a Conductor step; the program never advances)"
            % (n, summ, mod) + forecast)
        return False
    if owed == "exit not met":
        failed = "; ".join((ex.get("why") or [])[:3])
        put("exit_not_met", failed, INGAME_NOT_MET % (n, failed, summ) + forecast)
        return False
    mine = [x for x in ours if x.get("visit") == n]
    retry = mine[-1] if mine and retriable(cfg, mine[-1], f.get("killed"), mod) else None
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
    per = PC.limit(mod, "ingame_runs_visit", int(cfg.get("ingame_auto_runs_per_visit", 1)))
    if PC.used(mod, "ingame_runs_visit", len([x for x in ours if x is not retry])) >= per:
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
    cw = cert_wait(f, put, mod, "in_game", "in-game visit %s" % n, (cfg, s, row, now),
                   (account, live_total, releases))
    if cw:
        return cw == "launch"   # the offline builder on red deciders (row["cert_reds"]), a zero-token rerun
        # (row["cert_rerun_key"]), or the certificate's wait
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
        put("driver_busy", "an in-game run is live on every game (%s): one live-game driver per game across all mods; %s"
            % (", ".join("%s: %s" % (_GN.show(g), held[g]) for g in games), steve_takes(f, mod)))
        return False
    if no_slot(cfg, live_total, put):
        return False
    full = full_list_only(f)
    only = {g: "every check of visit %s needs his full list (%s), which %s cannot hold beside %s" % (
        n, ", ".join(full), _GN.show(g), _GN.show("a")) for g in games if g != "a"} if full else None
    gd = s.get("game_deploy") if isinstance(s.get("game_deploy"), dict) else {}
    ended = game_deploy_ended(cfg, mod, s, "visit", vid)
    if ended and gd.get("game") in games:       # the game the copy was deployed to comes first
        games = [gd["game"]] + [g for g in games if g != gd["game"]]
    game, whys = pick_game(dict(cfg, game_instances=games), bridge, "%s in-game acceptance visit %s" % (mod, n), held,
                           only=only)
    if not game:
        put("bridge_held", "%sno game is free: %s; %s" % (
            "WAITS FOR %s, full list (%s): " % (_GN.show("a"), ", ".join(full)) if full else "", "; ".join(whys),
            steve_takes(f, mod)))
        return False
    row.update(cap=cap, visit_id=vid, game=game)
    if cfg.get("_deploy_unit"):
        # the visit plays a copy that was read and deployed in its own unit, never in the tick
        if ended and gd.get("game") == game:
            row["game_repaired"] = ended
        else:
            row["game_deploy_start"] = True
            old = "; the deploy %s is read again: %s" % (gd.get("unit"), gd["stale"]) if gd.get("stale") else ""
            put("launch", "in-game visit %s owed: the game copy on %s is read and deployed first, in its own unit%s (%s)" % (
                n, _GN.show(game), old, account[1]))
            return True
    if retry:
        row["retry_of"] = dict(retry)
    put("launch", "in-game visit %s owed, nothing live or recorded on it, the visit's automatic run%s, on %s%s (%s)" % (
        n, retried(cfg, retry, mod), _GN.show(game), " (%s)" % "; ".join(whys) if whys else "", account[1]))
    return True


NAME_MAX_LEN, NAME_MAX_WORDS = 64, 9     # rimflow model's name grammar (`rimflow namecheck`); `file` only warns now
# budget: danger=an endless search on a wrong known set; ends no work: a count of names, no time
RUN_MAX = 99    # runs tried per name. Danger: an endless search on a wrong known set. Evidence: boundary page LIMITS


def nword(n):
    """-> the number as ONE name word (TWENTYTHREE, not TWENTY_THREE, which costs two of the nine words)."""
    return word(n).replace("_", "")


def mod_words(mod):
    return [w for w in re.split(r"[^A-Z0-9]+", str(mod).upper()) if w]


def short_mod(mod, room):
    """-> the mod as one word of at most `room` chars: whole when it fits, else a prefix + 4 hex of its SHA-1, so two
    long mods with one prefix still differ. None when even the hash has no room."""
    m = "".join(mod_words(mod))
    if len(m) <= room:
        return m
    if room < 4:
        return None
    return m[:room - 4] + hashlib.sha1(str(mod).encode("utf-8")).hexdigest()[:4].upper()


def _fit_one(words, run):
    tail = ["RUN", nword(run)] if run else []

    def render(ws, room=None):
        out = []
        for w in ws:
            if w.startswith("@"):
                out += mod_words(w[1:]) if room is None else [short_mod(w[1:], room)]
            else:
                out.append(w.lstrip("?"))
        return None if None in out else out + tail

    def fits(ps):
        return ps is not None and len(ps) <= NAME_MAX_WORDS and len("_".join(ps)) <= NAME_MAX_LEN

    ws = list(words)
    ps = render(ws)
    while not fits(ps) and any(w.startswith("?") for w in ws):
        del ws[max(i for i, w in enumerate(ws) if w.startswith("?"))]
        ps = render(ws)
    if fits(ps):
        return "_".join(ps)
    mod = next((w[1:] for w in ws if w.startswith("@")), None)
    if mod is None:
        return None
    full = render(ws, room=10 ** 6)
    room = len("".join(mod_words(mod))) - max(0, len("_".join(full)) - NAME_MAX_LEN)
    ps = render(ws, room=room)
    return "_".join(ps) if fits(ps) else None


def fit_name(words, known=(), runs=RUN_MAX):
    """THE tick's naming rule (RIMMANDRAKE_FIX_TICK_NAMER_RUN_THREE_NAME_TOO_LONG;
    design/specs/2026-11-20-tick-names-never-refused/boundary.md) -> the first of the name, then the name + RUN_<N> for
    N = 2..runs, that fits rimflow's grammar (9 words, 64 chars) and is not in `known`; None past `runs`.
    words: the name's words in order. "?W" may be dropped, "@Mod" is the mod; every other word is always kept. A
    candidate too long drops its "?" words right to left, then shortens the mod (short_mod). The old namers cut the
    base and added _RUN_<N> unchecked: GimmeSomeSlack's ..._VISIT_ONE_FAILURES_BACK_RUN_THREE was 66 chars and was
    refused three times (2026-11-20, about 11 PM PST)."""
    for run in [None] + list(range(2, runs + 1)):
        n = _fit_one(words, run)
        if n and n not in known:
            return n
    return None


def ingame_item_id(mod, visit, known):
    """-> a rimflow name for the live driver's item: RIMMANDRAKE_DRIVE_<MOD>_IN_GAME_ACCEPTANCE_VISIT_<N> (fit_name).
    Every name carries its visit word: the RUNNER spawn guard (model.RUNNER_INGAME_NAME) refuses a bare
    ..._IN_GAME_VISIT (2026-11-20 7:11 PM PST, Pyrelands after a clear)."""
    return fit_name(["RIMMANDRAKE", "DRIVE", "@" + mod, "IN", "GAME", "?ACCEPTANCE", "VISIT", nword(visit or 0)], known)


def blind_item_id(mod, cycle, known):
    """-> a rimflow name for the judge's item: RIMMANDRAKE_JUDGE_<MOD>_BLIND_CYCLE_<N>_TESTS_FIRST (fit_name)."""
    return fit_name(["RIMMANDRAKE", "JUDGE", "@" + mod, "BLIND", "CYCLE", nword(cycle or 0), "?TESTS", "?FIRST"], known)


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
    wait = not ok and AUT.wait_refusal(text)
    if wait:        # a wait spends no try: the entry keeps the tries before it
        tries = int(retry.get("tries") or 0)
    entry = dict(where, unit=unit if ok else None, item=item, at=now, cap=row.get("cap"), failed=None if ok else text,
                 tries=tries, filed=filed, never_started=not unit, tried=None if ok else tried_unit(text))
    if wait:
        entry["wait"] = True
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
    # budget: danger=a hung ledger test holds the dispatch tick; longest=0.2s (the docstring's reading, 2026-11-16)
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
    and land.sh's push is caught by land_ledger, which rebuilds and lands again (views_differ)."""
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
                           # budget: class=call
                           timeout=180)
    except (OSError, subprocess.SubprocessError) as e:
        return "views not landed: fetch failed: %s: %s" % (type(e).__name__, e)
    if f.returncode:
        return "views not landed: git fetch origin main exited %d: %s" % (f.returncode, f.stderr.strip())
    try:
        tmp = tempfile.mkdtemp(prefix="dispatch_views_")
    except OSError as e:
        return "views not landed: no temp dir: %s" % e
    try:
        for mod in mods:
            d = modledger.ledger_dir(root, mod)
            rel = os.path.relpath(d, root).replace(os.sep, "/")
            ls = subprocess.run(["git", "-C", root, "ls-tree", "--name-only", "origin/main", rel + "/"],
                                capture_output=True, text=True, timeout=120)
            if ls.returncode:       # an unreadable listing is no empty ledger
                return "views not landed: cannot list origin/main:%s (git ls-tree exited %d)" % (rel, ls.returncode)
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


LAND_VIEW_TRIES = 3


def land_ledger(root, mods, what, fx=None):
    """Land the DISPATCH shard and views of these mods' ledgers (land.sh, as land_spend does). The views landed are
    rebuilt from origin/main's shards plus this root's DISPATCH shard first (origin_views). After a landing the views
    are rebuilt again from a fresh fetch: a peer shard that landed between the fetch and the push leaves them unlike
    origin's, and they land again, up to LAND_VIEW_TRIES landings (RIMMANDRAKE_REBUILD_DISPATCH_VIEWS_ON_EACH_LAND_RETRY:
    before, land.sh's retry re-landed the same views and origin read VIEW_STALE until the next Dispatch landing)."""
    if (fx or {}).get("land_ledger"):
        paths = ledger_paths(root, mods)
        return fx["land_ledger"](paths) if paths else "nothing to land"
    if (fx or {}).get("land_spend"):
        paths = ledger_paths(root, mods)
        return land_spend(root, paths, dict(fx, land_msg="modledger: %s (Dispatch step)" % what)) if paths \
            else "nothing to land"
    out = None
    for n in range(LAND_VIEW_TRIES + 1):
        refused = origin_views(root, mods)
        if refused:
            return refused if out is None else "%s; then %s" % (out, refused)
        paths = ledger_paths(root, mods)
        if not paths:
            return out or "nothing to land"
        if out is not None:
            if not views_differ(root, paths):
                return out
            if n == LAND_VIEW_TRIES:
                return "%s; views still unlike origin's after %d landings (a peer kept landing): the next Dispatch " \
                       "landing repairs them" % (out, LAND_VIEW_TRIES)
        if (fx or {}).get("after_views"):       # the selftest's race seam: a peer lands between the fetch and the push
            fx["after_views"]()
        got = land_spend(root, paths, dict(fx or {}, land_msg="modledger: %s (Dispatch step)%s" % (
            what, "" if out is None else ", views rebuilt after a peer landing")))
        out = got if out is None else "%s; again: %s" % (out, got)
        if not str(got).startswith("PUBLISHED"):
            return out
    return out


def views_differ(root, paths):
    """-> True when these paths in the root's worktree (views just rebuilt by origin_views from a fresh fetch) differ
    from origin/main's, blob by blob (the index is never consulted: a file land.sh published through its temp index may
    be untracked here); an unreadable read is True (land again rather than leave them stale)."""
    for rel in paths:
        try:
            o = subprocess.run(["git", "-C", root, "rev-parse", "--verify", "-q", "origin/main:%s" % rel],
                               capture_output=True, text=True, timeout=120)
            here = os.path.exists(os.path.join(root, rel))
            w = subprocess.run(["git", "-C", root, "hash-object", "--", rel], capture_output=True, text=True,
                               timeout=120) if here else None
        except (OSError, subprocess.SubprocessError):
            return True
        if w is not None and w.returncode:
            return True
        if (o.stdout.strip() if o.returncode == 0 else None) != (w.stdout.strip() if w is not None else None):
            return True
    return False


def ledger_open(root, mod, role, brief, stage=None, now=None, fx=None):
    """A pilot holder's run begins: modledger.launch grants the lease and records run.start, and the ledger lands
    before any launch cuts the holder's clone from origin/main (RIMMANDRAKE_LAND_HOLDER_GRANT_BEFORE_LAUNCH_CLONE_BLIND:
    landed after, the clone lacks its own grant and the holder's first append is refused "lease never granted");
    -> {"brief": the packet and holder lines, then `brief`, "env": the unit's RM_MODLEDGER_WRITER/TOKEN, "run",
    "stage", "landed"}."""
    now = now or time.time()
    lease = "run-%d" % int(now)
    import run_alive    # the timer renews a detached run's lease from its process; the brief asks only while no timer lives
    by_program = run_alive.timer_live()
    out = modledger.launch(root, mod, lease, role, stage=stage, by_program=by_program)
    landed = land_ledger(root, [mod], "run %s on %s granted" % (lease, mod), fx)
    return {"run": lease, "stage": out["stage"], "packet": out["brief"], "landed": landed,
            "brief": out["brief"].rstrip("\n") + (
                "" if by_program else "\n\n" + renew_line(mod, out["writer"], out["token"])) + (
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


def judge_reopen(root, mod, run, stage=None, why="", fx=None):
    """A voided blind judge resumes its own session: DISPATCH reopens the seal of its JUDGE.<run> (modledger.unseal),
    so its lines land; no new judge run starts. Its run end seals the shard again (end_ledger_runs). -> the dict
    judge_open returns, with "reopened": True."""
    w = "JUDGE.%s" % run
    lines = judge_lines(mod, run, stage)
    modledger.unseal(root, mod, run, why)
    landed = land_ledger(root, [mod], "judge run %s on %s reopened" % (run, mod), fx)
    return {"run": run, "stage": stage, "packet": lines, "landed": landed, "brief": lines, "judge": True,
            "writer": w, "env": {"RM_MODLEDGER_WRITER": w}, "reopened": True}


def void_judge_runs(s):
    """-> {ledger run: its void record} for the judge runs of one mod's Dispatch state that are VOID (their
    `ledger_runs` entry moved to `voided`, or a unit that a standing hand void names)."""
    out = {}
    hand = RV.active()
    for m in (s or {}).get("voided") or []:
        e = (m or {}).get("entry") or {}
        if m.get("book") == "ledger_runs" and str(e.get("writer") or "").startswith("JUDGE.") and e.get("run"):
            out[e["run"]] = m
    for e in (s or {}).get("ledger_runs") or []:
        if isinstance(e, dict) and e.get("unit") in hand and str(e.get("writer") or "").startswith("JUDGE."):
            out.setdefault(e["run"], {"unit": e["unit"], "void": hand[e["unit"]].get("id"), "class": "void_hand"})
    return out


def reopen_void_judge(root, st, mod, run, lines_file=None, why=""):
    """`judge-reopen MOD --run R [--lines FILE]`: a VOIDED judge's sealed shard takes its own lines. Refuses a run that
    is not void. Reopens the seal, appends from FILE only the lines whose writer is JUDGE.<run> and whose run is R
    (skipping one the shard holds already), then seals it again. -> (rc, text, [repo paths written])."""
    v = void_judge_runs(((st or {}).get("mods") or {}).get(mod))
    if run not in v:
        return 2, ("REFUSED: %s's judge run %s is not void (no voided ledger_runs entry, no standing hand void): only "
                   "a voided run's seal reopens" % (mod, run)), []
    shard = "JUDGE.%s" % run
    path = os.path.join(modledger.ledger_dir(root, mod), shard + ".jsonl")
    keep, skipped = [], 0
    if lines_file:
        for ln in open(lines_file, encoding="utf-8").read().splitlines():
            try:
                ev = json.loads(ln)
            except ValueError:
                ev = None
            if isinstance(ev, dict) and ev.get("writer") == shard and ev.get("run") == run:
                keep.append(ln)
            elif ln.strip():
                skipped += 1
    have = set(open(path, encoding="utf-8").read().splitlines()) if os.path.exists(path) else set()
    new = [ln for ln in keep if ln not in have]
    eid = modledger.unseal(root, mod, run, why or "run %s was voided (%s)" % (run, (v[run] or {}).get("void")),
                           void=(v[run] or {}).get("void"))
    if new:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("".join(ln + "\n" for ln in new))
    seal_id = modledger.seal(root, mod, run)
    bad = [x for x in modledger.lint(root, mod)[0] if str(x[1]).endswith(shard + ".jsonl")]
    paths = [os.path.relpath(p, root) for p in [path] if os.path.exists(p)] + ledger_paths(root, [mod])
    return (1 if bad else 0), ("%s: seal %s reopened (%s), %d line(s) of its own landed, %d other line(s) refused, "
                               "sealed again (%s)%s" % (
                                   shard, "was" if eid else "was not", eid or "nothing to reopen", len(new), skipped,
                                   seal_id, "; LINT: %s" % bad if bad else "")), paths


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
    cfg = MM.for_mod(cfg, mod)      # its builders' pin; the judge and the live driver keep theirs
    model = (cfg.get("ingame_model", "opus") if stage == "in_game" else MM.judge_model(cfg)
             if stage == "blind_challenge" else cfg.get("model", "opus"))
    jr = kw.pop("judge_resume", None)       # a voided judge's own session (decide_void_resume)
    if jr and jr.get("session"):
        kw["session"] = jr["session"]
    if not pilot_ledger(root, mod):
        return launch(root, mod, cap, item, seat=cfg.get("seat", "BENCH"), model=model, **kw)
    now = now or time.time()
    try:
        if stage == "blind_challenge" and jr and jr.get("run"):     # the same judge writes its own reopened shard
            led = judge_reopen(root, mod, jr["run"], stage=stage, why="its run %s was voided; the same judge resumes "
                               "session %s" % (jr.get("unit"), jr.get("session")), fx=fx)
        elif stage == "blind_challenge":      # a judge is never the holder: it writes JUDGE.<run>, blind (spec §3.6)
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
        opened = AUT.road_back_open(s, rb, fx.get("open_items") or (
            lambda ids, **kw: M.ledger_items_caused_by(root, ids, **kw))) if rb else []
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


def road_back_holder(root, cfg, st, mod, stage, opened, item, cap, now, fx, game=None):
    """One pilot holder run on every open road-back item together (`opened`, [{id, needs}]), from the ledger packet:
    pilot-launch's road back, and the tick's once the fixers are spent (pilot_holders). Items only a game can show get
    no run at an offline stage, unless `game` names the free game pilot_holders picked for them (the version's offline
    Problems are spent: design/specs/2026-11-20-tick-game-only-exit/boundary.md); at Stage 6 a live-only set gets the
    live brief on the first free game (pick_game).
    -> (rc, text, unit, item); rc None is a refusal before any launch, said in its words, nothing booked. Booked in s["holder_road_back"] with
    the item set it ran on (holder_spent reads it)."""
    have = M.ledger_needs(root, [x["id"] for x in opened if not x.get("needs")])
    opened = [dict(x, needs=x.get("needs") or have.get(x["id"])) for x in opened]
    # offline stages never wait for a game: at one, an item only the game can show is Stage 6 work, given no
    # run here (RIMMANDRAKE_CLOSE_OFFLINE_STAGE_ITEMS_OFFLINE_GAME_WAS_DEMANDED)
    given = game
    game6 = [x["id"] for x in opened if x["needs"] in M.LIVE_NEEDS] if not (M.game_takeable(stage) or given) else []
    ids = [x["id"] for x in opened if x["id"] not in game6]
    if not ids:
        return None, ("REFUSED: %s stands at %s, an offline stage, and every open road-back item (%s) needs a "
                   "game: no offline run can close one, and no game was picked for them. They are Stage 6 "
                   "work; return the record there: %s" % (mod, stage, ", ".join(game6),
                                                          M.game_only_cmd(mod, game6))), None, item
    # an item a live run is working in its own <ITEM>.det is that run's: the holder neither takes its clone nor works
    # it (RIMMANDRAKE_REPAIR_FLOWWORKS_FORM_REFUSAL_AT_THE_RUN_FIVE); every item busy is a wait, nothing booked
    live_on = fx.get("item_live", item_live_run)
    seen = {i: live_on(i) for i in ids}
    busy = {i: u for i, u in seen.items() if isinstance(u, str) and u}
    blind = ["%s (%s)" % (i, u) for i, u in sorted(seen.items()) if u is not None and not isinstance(u, str)]
    ids = [i for i in ids if i not in busy]
    if not ids:
        return None, ("%s every open road-back item of %s has its own live run (%s); the holder runs once they end"
                      % (M.WAIT_MARK, mod, ", ".join("%s: %s" % kv for kv in sorted(busy.items())))), None, item
    item = item if item and item not in game6 and item not in busy else ids[0]
    # at Stage 6, every open item needs the live game: the holder takes the bridge and the game, one holder at a
    # time (RIMMANDRAKE_LET_HOLDER_TAKE_BRIDGE_ALL_ITEMS_NEED_GAME)
    live = (M.game_takeable(stage) or bool(given)) and AUT.live_only(opened)
    game = given if live else None
    if live and not game:   # a free game (pick_game), its bridge takeable; none free is a refusal with each reason
        game, whys = pick_game(cfg, fx.get("bridge"), "%s live holder run" % mod)
        if not game:
            return None, ("REFUSED: %s's open items all need a game and no game is free (%s); "
                          "one bridge holder per game" % (mod, "; ".join(whys))), None, item
    # the holder is the mod's one work bundle: its road back and its ready tickets with a test (work_bundle.py; design
    # design/specs/2026-11-24-work-bundles section 6); a live bundle of the mod is a wait, nothing booked
    import work_bundle as WB
    bundle, bnote, bcause = None, "", None
    try:
        extra = (fx.get("bundle_extra") or (lambda m, ex: WB.mod_members(m, ex, now)))(mod, set(ids) | set(game6) | set(busy))
        brc, bundle = WB.holder_bundle(mod, item, ids, extra, now)
        if brc:
            return None, "%s %s" % (M.WAIT_MARK, bundle), None, item
        w_items = WB.world().items if extra else {}
        bnote = WB.holder_note(bundle, w_items, WB.tests_text(extra, w_items, WB.prose_reader()) if extra else {})
    except Exception as e:  # noqa: BLE001 - could not look: the holder runs as before, and its line says so
        bundle, bcause = None, "work bundle UNMEASURED (%s: %s)" % (type(e).__name__, e)
    plan = modledger.resume_plan(root, mod)     # the holder's recorded session is resumed, not restarted
    rkw = {"session": plan["session_id"]} if plan.get("action") == "resume" and plan.get("session_id") else {}
    try:
        led = ledger_open(root, mod, "fixer", AUT.fixer_brief(item, mod, cap, live=live) + (
            "\nReconcile first: %s.\n" % plan["why"] if plan.get("reconcile") else "") + (
            "\nThis is the mod's %sholder run: work every open road-back item together, from the packet above: %s. "
            "Close each one its acceptance test passes; a note starting LEFT OPEN: on each that is not.\n"
            % ("live " if live else "", ", ".join(ids)) + (
            "Not yours: %s need%s a game, Stage 6 work; work none of them here.\n" % (
                ", ".join(game6), "s" if len(game6) == 1 else "") if game6 else "") + (
            "\n" + M.game_brief(game) if game else "") + (
            "Not yours: %s, each worked by its own live run; work none of them here.\n" % ", ".join(
                "%s (%s)" % kv for kv in sorted(busy.items())) if busy else "") + bnote), stage=stage, now=now, fx=fx)
        rc, text, unit = (fx.get("launch_brief") or AUT.launch_brief)(
            item, led["brief"], MM.for_mod(cfg, mod).get("steward_model", "opus"), cap, cfg.get("seat", "BENCH"),
            env=dict(led["env"], **control_env(mod, stage), **({"RM_GAME_INSTANCE": game} if game else {}),
                     **({WB.ENV: bundle["id"]} if bundle else {})), **rkw)
    except BaseException as e:      # a raise leaves no `launching` bundle record: that state blocks the mod
        if bundle:
            WB.holder_launched(bundle["id"], None, now, "the holder launch raised %s: %s" % (type(e).__name__, e))
        raise
    unit = unit if rc == 0 else None
    if bundle:
        WB.holder_launched(bundle["id"], unit, now, text)
    text = "%s%s%s; %s%s" % ("live holder on %s (bridge and game allowed): " % _GN.show(game) if live else "",
                             "%s; " % plan["why"] if rkw else "",
                             (text or "").splitlines()[0] if text else rc,
                             ledger_after(root, st, mod, led, unit, item, now, fx),
                             "; live run UNMEASURED on %s: worked as free, the launcher's clone gate decides" % (
                                 ", ".join(blind)) if blind else "") + ("; " + bcause if bcause else "")
    if not unit and AUT.wait_refusal(text):     # a wait is no try at the items: nothing booked, the next tick decides
        return rc, text, unit, item
    st.setdefault("mods", {}).setdefault(mod, {}).setdefault("holder_road_back", []).append(
        dict({"at": now, "ids": sorted(ids), "item": item, "unit": unit, "stage": stage,
              "tried": None if unit else tried_unit(text)}, **({} if unit else {"failed": str(text)})))
    return rc, text, unit, item


def item_live_run(item):
    """-> the unit of a live run (launching or running) in <ITEM>.det; None when it looked and none is live; a
    probe_result could_not_look(cause) when the run records cannot be read (road_back_holder says it, and the launcher's
    own clone gate, detached_helper.hold_until_returned, still refuses a held clone, as a wait)."""
    import probe_result as PR
    try:
        return (DH.live_holders(os.path.join(DH.pool_root(), "clones", item + ".det")) or [None])[0]
    except Exception as e:  # noqa: BLE001
        return PR.could_not_look("run records of %s.det: %s: %s" % (item, type(e).__name__, e))


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
    open_items = fx.get("open_items", lambda ids, **kw: M.ledger_items_caused_by(root, ids, **kw))
    account = fx["account"]() if "account" in fx else account_gate()
    base = occupancy(facts)
    for row in rows:
        mod = row["mod"]
        s = st.setdefault("mods", {}).setdefault(mod, {})
        # a pilot's holder runs FIRST on all the open road-back items, before any one-fixer-per-item run (the report
        # context-kept-not-reloaded, change 4: FlowWorks' road back ran a router and four fresh fixers, 2.20M of 4.20M
        # weighted spent reading the same mod again); a per-item fixer row whose holder already ran on the same set
        # keeps its fixer
        first = row.get("decision") == "fixer" and row.get("aut") == "fixer"
        if row.get("decision") != "fixer_spent" and not first or not s.get("road_back") or (
                facts.get(mod) or {}).get("live_units"):
            continue
        # only the launches ahead of it on the advancing list count against it: a later mod's launch is evicted by
        # prioritise, never the other way round (RIMMANDRAKE_LAUNCH_PYRELANDS_FIRST_AT_ONE_SLOT)
        planned = None if base is None else base + slots_ahead(rows, launches, mod)
        if not (fx.get("pilot") or pilot_ledger)(root, mod):
            continue
        items = AUT.road_back_open(s, s["road_back"], open_items)
        if not items:
            continue
        game_set = not M.game_takeable(row.get("stage")) and all((x or {}).get("needs") in M.LIVE_NEEDS for x in items)
        if game_set and row.get("decision") != "fixer_spent":
            # every item needs a game, the stage is offline and the version's own Problem fixer is owed: it goes first,
            # it may change the build the game-only items test (RIMMANDRAKE_UNPARK_FLOWWORKS_STUCK_AT_OFFLINE_STAGE_
            # EIGHT_HOURS). Once those fixers are spent no pipeline act changes the build: the items go to a free game
            # below (RIMMANDRAKE_DEFINE_BOTH_GAMES_EVERYWHERE_WAITING_SAID_AGAIN; FlowWorks sat behind one spent owner
            # look with game b free, 2026-11-20)
            continue
        ids = sorted(x["id"] for x in items)

        def put(decision, why, need=None):
            row.update(decision=decision, why=_GN.name_text(why) if isinstance(why, str) else why, aut=None)
            if need:
                row["need"] = "%s: %s" % (mod, _GN.name_text(need))
        spent = holder_spent(s, ids)
        if spent and first:
            continue        # the holder ran on this set: the per-item fixers take it from here, as before
        if spent:
            put("holder_spent", spent, "PAUSED, %s; the pipeline gives one holder run per set of open road-back items "
                "(pilot-launch %s --why ... starts another by hand)" % (spent, mod))
            continue
        if not account[0]:
            put("account_hold", account[1])
            continue
        if no_slot(cfg, planned, put):
            continue
        game, whys = None, []
        if game_set:        # the game-only items, on the first free game: a driven game, or one taken this tick, is not
            taken = {g: u for u, g in driver_games(facts).items() if u in live_drivers(facts)}
            taken.update({g: u for u, g in game_deploy_drivers(st).items()})
            taken.update({r.get("game") or r.get("holder_game"): "a launch of this tick (%s)" % r["mod"]
                          for r in rows if r["mod"] in launches and (r.get("game") or r.get("holder_game"))})
            game, whys = pick_game(cfg, fx.get("bridge"), "%s live holder run on its game-only road-back items" % mod,
                                   taken, hold=fx.get("hold"))
            if not game:
                put("no_game_free", "every open road-back item (%s) needs a game, %s's offline Problems are spent, and "
                    "no game is free: %s" % (", ".join(ids), mod, "; ".join(whys)))
                row.pop("need", None)   # a wait that ends by itself when a game frees: no hand is asked for
                row["waits_on"] = _GN.name_text("a free game: %s" % "; ".join(whys))
                continue
            row.pop("need", None)       # the PAUSED hold of fixer_spent is lifted: the run goes to a game
        row.update(holder_items=items, cap=MM.for_mod(cfg, mod).get("cap_usd"),
                   **({"holder_game": game} if game else {}))
        put("launch", "%s and its ledger is ready: one holder run on all %d open items (%s)%s, nothing live on it (%s)"
            % ("its road back opened (the holder goes first, before any per-item fixer)" if first else
               "its road-back fixers are spent" if not game else
               "every open road-back item needs a game and its offline Problems are spent", len(ids), ", ".join(ids),
               " on %s%s" % (_GN.show(game), " (%s)" % "; ".join(whys) if whys else "") if game else "", account[1]))
        launches = [m for m in launches if m != mod] + [mod]
    return rows, launches


NO_SLOT_AUT = AUT.ACTS     # the pipeline's acts on a concept, not runs: no slot (one list, so a new act is never a run)


def takes_slot(row):
    """True when ROW's launch takes a run slot: a zero-token certificate rerun or deploy unit and the pipeline's acts take
    none."""
    return not row.get("cert_rerun_key") and not row.get("game_deploy_start") and row.get("aut") not in NO_SLOT_AUT


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
            row.update(decision="slots_full", aut=None, waits_on=cert_red_waits(row, ahead) if row.get("cert_reds")
                       else "a free slot%s" % (" (launch priority: %s first)" % ", ".join(ahead) if ahead else ""),
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
    base = cfg
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
        cfg = MM.for_mod(base, mod)     # decide priced this pin already; the closures above read this binding
        blind = row.get("stage") == "blind_challenge"
        if row.get("holder_items"):     # pilot_holders: one holder run on the open road-back items
            rc, text, unit, item = road_back_holder(root, cfg, st, mod, row.get("stage"), row["holder_items"], None,
                                                    row.get("cap") or cfg["cap_usd"], now, fx,
                                                    game=row.get("holder_game"))
            if unit:
                s.setdefault("launches", []).append({"unit": unit, "item": item, "at": now, "cap": row.get("cap"),
                                                     "stage": row.get("stage"), "holder": True})
                row.update(decision="launched", unit=unit, item=item, why=text)
                done.append(row)
            elif AUT.wait_refusal(text):     # a cause that ends by itself: no try spent, the next tick decides again
                row.update(decision="launch_wait", why="the holder run waits on a cause that ends by itself (no fault, "
                           "no try spent); the next tick tries it again: %s" % text)
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
        if row.get("game_deploy_start"):    # the visit's game copy is read and deployed in its own unit first
            game_deploy_launch(cfg, st, row, "visit", row.get("visit_id"), row.get("game", "a"),
                               "deploy %s before its in-game visit %s" % (mod, row.get("visit")), now, fx)
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
                lambda it: launch_holder(mod, s, row, row["cap"], it, **dict(
                    resume_kw(row), game=row.get("game", "a"),
                    **({"continue_on_cap": INGAME_CONTINUE_ON_CAP} if _takes(do_launch, "continue_on_cap") else {}),
                    **({"repaired": row["game_repaired"]} if row.get("game_repaired") else {}))))
            if row.get("game_repaired") and not entry.get("wait"):
                s.pop("game_deploy", None)      # used: a launch that waits keeps it for the next tick
            if ok:
                row.update(decision="launched", unit=unit, item=item, why=text)
                known.add(item) if isinstance(known, set) else None
                done.append(row)
            elif entry.get("wait"):
                row.update(decision="launch_wait", why="the in-game launch waits on a cause that ends by itself (no "
                           "fault, no try spent); the next tick tries it again: %s" % text)
            elif retriable(cfg, entry, mod=mod):
                row.update(decision="launch_retry", why="the in-game launch never started on a transient fault (try %d "
                           "of %d), the next tick tries it again: %s" % (entry["tries"], AUT.tries_most(cfg, mod),
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
            elif retriable(cfg, entry, mod=mod):
                row.update(decision="launch_retry", why="the blind launch never started on a transient fault (try %d "
                           "of %d), the next tick tries it again: %s" % (entry["tries"], AUT.tries_most(cfg, mod),
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
        elif not unit and AUT.transient(text) and AUT.tries_left(cfg, mod, tries):
            s["launch_retry"] = {"item": item, "filed": filed, "tries": tries, "at": now, "refused": row["refused"],
                                 "failed": text}
            row.update(decision="launch_retry", why="the Stage 3 launch never started on a transient fault (try %d of "
                       "%d), the next tick tries it again: %s" % (tries, AUT.tries_most(cfg, mod), text))
        else:
            # a launch that never started is a fault of form (form_fault): never counted, never `stopped`; the tick
            # starts a repair run on it; the same refusal after a finished repair counts once
            s.pop("launch_retry", None)
            if FF.fault_class(text) == "wait":
                row.update(decision="launch_wait", why="the Stage 3 launch waits on a cause that ends by itself (no "
                           "fault): %s" % text)
                continue
            held = FF.owe_repair(s, text, "%s stage 3 launch" % mod, now, book="launches", key=item)
            if held:
                s.setdefault("system_faults", []).append({"at": now, "book": "launches", "key": item,
                                                          "unit": None, "cause": held, "n": 1})
            row.update(decision="repairing", why="repairing: %s (the Stage 3 launch never started; a repair run "
                       "starts)" % FF.what_of(text))
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
    killed = None if row.get("judge_fresh") else (row.get("retry_of") or {}).get("unit")
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
    usd, ceiling = stage_spend(cfg, mod, row.get("stage"), row.get("stage_usd"))
    if _usd_ok(ceiling, True) and _usd_ok(usd):
        cap = row["cap"] = holder_cap(cfg, row, cap)
    return cap, kw


def holder_cap(cfg, row, cap):
    """A pilot holder's cap is per mod and stage, not per run: what is left of stage_ceiling_usd at this stage, never
    less than the run cap (holder_launch; launch_kind reads the same rule for the forecast)."""
    usd, ceiling = stage_spend(cfg, row.get("mod"), row.get("stage"), row.get("stage_usd"))
    if _usd_ok(ceiling, True) and _usd_ok(usd):
        return max(cap, round(ceiling - usd, 2))
    return cap


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
    """The launch's resume argument for a retry of a KILLED run (its unit), else none. A voided blind judge
    (decide_void_resume) also carries judge_resume (its own session and ledger run), or only fresh_of (a fresh judge:
    no resume section)."""
    if row.get("judge_fresh"):
        return {"fresh_of": dict(row["judge_fresh"])}
    u = (row.get("retry_of") or {}).get("unit")
    kw = {"resume": u} if u else {}
    if row.get("judge_resume"):
        kw["judge_resume"] = dict(row["judge_resume"])
    return kw


def reap_run(unit):
    """A killed run's finish (never run: its unit vanished) and its return, started as the unit's own ExecStopPost
    would: -> one line of what happened."""
    me = os.path.join(HERE, "detached_helper.py")
    said = []
    rec = DH.read_record(unit) or {}
    if rec.get("status") != "finished":
        r = subprocess.run([sys.executable, me, "finish", "--unit", unit], capture_output=True, text=True, timeout=21600,  # budget: class=publish
                           stdin=subprocess.DEVNULL)
        said.append("finish exit %d" % r.returncode)
        rec = DH.read_record(unit) or {}
    if rec.get("status") == "finished" and not rec.get("returned"):
        # budget: danger=a hung start of the return unit holds the dispatch tick; never reached in the 14 days to 2026-11-24; no
        # budget: record of its run
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
        p = own_cgroup.run([DS.LAND, "-m", (fx or {}).get("land_msg") or "maturation: spend rows of ended runs (Dispatch step)"]
                           + paths, cwd=root,
                           capture_output=True, text=True, timeout=21600, env=dict(os.environ, LAND_REPO=root))  # budget: class=publish
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
# budget: danger=the tick finishes a run whose own finish still runs; ends no work: the tick leaves the run for a later tick
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
            and r.get("decision") not in ("launched",) and r.get("klass") not in ("paused", "owner", "planned")
            and not r.get("pipeline_paused")]     # a paused mod is idle by plan: no idle alarm
    mx = max([r.get("idle_min") or 0 for r in owed] or [0])
    over = [r["mod"] for r in owed if (r.get("idle_min") or 0) > cfg.get("idle_alarm_min", 60)]
    return {"schema": 1, "at": now, "at_pac": pac(now), "enabled": bool(cfg.get("enabled")),
            "idle_owed_max_min": mx, "idle_owed_mods": over, "idle_alarm_min": cfg.get("idle_alarm_min", 60),
            "launched": [{"mod": r["mod"], "unit": r.get("unit"), "item": r.get("item")} for r in rows
                         if r.get("decision") == "launched"],
            "needs_conductor": [r["need"] for r in rows if r.get("need")],
            "mods": {r["mod"]: {k: r.get(k) for k in ("decision", "why", "stage", "owed", "refused", "live",
                                                       "idle_min", "stage_usd", "cycle", "visit", "exit",
                                                       "stop_lifted", "batch", "launch", "pipeline_paused")}
                     for r in rows}}


CLONE_FETCH_S = 30          # the tick's fetch of its own clone
# budget: danger=the tick launches from a clone that is behind origin; ends no work: the tick launches nothing and says so; the
# budget: next tick reads again
CLONE_STALE_MIN = 5.0     # the OPS_DISPATCH_CLONE_BEHIND_UNSTICK alarm's threshold: past it the tick launches nothing
# budget: danger=a refused fetch read as level with origin; ends no work: the reading says: could not look
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


def clone_head(root):
    """-> probe_result value(HEAD's sha), or could_not_look(why) when git cannot say. The tick passes a blind answer
    to clone_reading as head=None, which never restarts the clock."""
    import probe_result as PR
    try:
        r = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as e:
        return PR.could_not_look("git rev-parse HEAD: %s" % e)
    sha = r.stdout.strip()
    if r.returncode or not sha:
        return PR.could_not_look("git rev-parse HEAD: rc %s %s" % (r.returncode, r.stderr.strip()))
    return PR.value(sha)


def _head_sha(answer):
    """clone_head's answer as clone_reading's head: the sha, or None for a blind read (unknown never resets)."""
    return answer.value if getattr(answer, "ok", False) else (answer if isinstance(answer, str) else None)


def clone_reading(st, now, got, head=None):
    """The clone's distance from origin/main and how long it has been behind, carried in state.json between ticks:
    behind_since is the first tick that saw THIS HEAD behind, level_at the last tick that saw it level (its last good
    sync). The danger is old code, and the code is as old as HEAD's last move: under steady origin churn the clone
    fast-forwards every ~90 s and still reads behind on every tick, which crossed CLONE_STALE_MIN on a healthy clone
    (RIMMANDRAKE_MEASURE_CLONE_LAG_FROM_LAST_PULL_CHURN_TRIPS, 2026-11-19). So a known HEAD that moved since the last
    tick, with nothing of its own (ahead 0: a fast-forward), restarts the clock; an unknown HEAD (None) never does, and
    a clone whose HEAD moves by local commits (ahead > 0) keeps counting. Minutes count from behind_since, not from
    commit dates: a commit pushed hours after it was made is new here."""
    c = st.setdefault("clone", {})
    behind, ahead = got
    out = {"at": now, "level_at": c.get("level_at"), "level_pac": pac(c["level_at"]) if c.get("level_at") else None}
    if behind is None:
        return dict(out, measured=False, why=ahead)
    moved = bool(head and c.get("head") and head != c["head"] and not ahead)
    if head:
        c["head"] = head
    if behind:
        if moved:
            c["behind_since"] = now
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
    out += rd.get("voids") or []
    return out


def void_why(unit, record=None):
    """-> why a run is VOID (a standing hand void, or a system cause on its record), or "" (it counts; or its record
    cannot be read: UNMEASURED, judged as before)."""
    if not unit:
        return ""
    v = RV.active().get(unit)
    if v:
        return "hand void %s: %s" % (v.get("id"), v.get("why"))
    return RV.system_cause((record or DH.read_record)(unit))


def still_retried(cfg, book, x, mod=None):
    """-> True for a never-started launch the tick still tries again (its tries are the retry's own, not a trial):
    a blind or in-game one by retriable, a steward or fixer one by the gate's own rule (maturation_autonomy._gate)."""
    if book in ("blind_auto", "ingame_auto"):
        return retriable(cfg, x, mod=mod)
    if book in ("steward", "fixers"):
        if isinstance(x, dict) and x.get("wait") and x.get("failed"):
            return True
        return bool((AUT.transient(x.get("failed")) or code_changed(cfg, x)) and AUT.tries_left(cfg, mod, x.get("tries")))
    return book != "holder_road_back"    # a holder run that never started is no try at its items


def kill_resumed(cfg, book, x, why, mod=None):
    """-> True for a KILLED blind or in-game run the tick still resumes (retriable: fewer than launch_tries kills)."""
    return (book in ("blind_auto", "ingame_auto") and str(why).startswith(("killed", "its unit died"))
            and not x.get("failed") and AUT.tries_left(cfg, mod, len(x.get("killed_before") or []) + 1))


def entry_mods(st):
    """-> {id(entry): mod} for every book entry in the tick's state (a list's dicts, a dict's dict values)."""
    out = {}
    for mod, s in ((st or {}).get("mods") or {}).items():
        for v in (s.values() if isinstance(s, dict) else ()):
            for x in (v if isinstance(v, list) else v.values() if isinstance(v, dict) else ()):
                if isinstance(x, dict):
                    out[id(x)] = mod
    return out


def system_fault_stop(cfg, st, rows, launches):
    """A mod with run_void.SYSTEM_FAULT_LIMIT system faults since its last clear launches nothing and reads
    system_fault (alarm OPS_MATURATION_SYSTEM_FAULT_LOOP): an endless relaunch is stopped without spending a trial."""
    most = int(cfg.get("system_fault_limit", RV.SYSTEM_FAULT_LIMIT))
    for r in rows:
        s = (st.get("mods") or {}).get(r["mod"]) or {}
        n = RV.faults(s)
        if n >= most and r["mod"] in launches:
            last = ([f for f in s.get("system_faults") or [] if RV.counted_fault(f)] or [{}])[-1]
            r.update(decision="system_fault", why="%s: %d system faults since the last clear (limit %d), the last %s: "
                     "%s; no trial is spent; read the cause, then `maturation_dispatch.py clear %s --why ...`" % (
                         RV.ALARM_ID, n, most, last.get("unit") or "a launch", last.get("cause"), r["mod"]))
            launches = [m for m in launches if m != r["mod"]]
    return launches


# rows the repair gate leaves as they are: a run live on the mod, or a stop someone chose
REPAIR_KEEP = {"live", "owner_hold", "pipeline_paused", "control_off", "disabled", "stale_clone", "system_fault"}
REPAIR_LAUNCH_MOST = 3      # a repair launcher refused this many times names the Conductor (danger: the repair launch
                            # itself refused forever, each tick re-sending it; evidence: the night of 2026-11-20, where
                            # every refused launch was re-sent until a hand came)
# budget: danger=a launch is sent again every tick into the same refusal (the night of 2026-11-20); ends no work: a wait before
# budget: the next try
VOID_REPAIR_WAIT_S = 3600   # after a killed repair run (danger and evidence: as REPAIR_LAUNCH_MOST, a launch re-sent each tick)
FAULT_REPAIRS_MOST = 2      # boundary page LIMITS: two repair runs that did not hold mean the fix is unknown


def repair_launch(root, cfg, mod, records, kind="form", item=None):
    """The tick's repair run: file one item for it (fit_name), publish, and launch form_fault.repair_brief on it through
    detached_helper (opus, fix_cap_usd). -> (ok, text, unit). A launcher that repaired the input in place returns
    (True, how, None): the repair is done at once and the mod goes on in the same tick."""
    what = FF.what_of(records[0].get("text") or records[0].get("cause") or "", 120)
    if item:        # a try that filed its item and then failed: the same item again, published, never a new one
        ok, text = publish_filed(item)
        text = "retry of %s, filed earlier; %s" % (item, text)
    else:
        item = fit_name(["RIMMANDRAKE", "REPAIR", "@" + mod, "FORM" if kind == "form" else "FAULT",
                         "REFUSAL" if kind == "form" else "LOOP", "?AT", "?THE", "?GATE"], known_items())
        if not item:
            return False, "no free item name", None
        ok, text = file_and_publish(item, "Repair %s's %s refusal where it was found: %s" % (
            mod, "form" if kind == "form" else "fault-loop", what), "the tick's repair run (form_fault): %s" % what)
    if not ok:
        return False, text, None
    cap = cfg.get("fix_cap_usd") or 10
    rc, out, unit = AUT.launch_brief(item, FF.repair_brief(mod, records, kind), "opus", cap)
    return bool(rc == 0 and unit), "%s; %s" % (text, (out or "").splitlines()[0] if out else rc), unit


def repair_launcher(fx):
    """-> the repair launcher for this tick: fx["repair_launch"]; the real repair_launch ONLY when the tick runs with no
    fixtures at all (fx empty: the live tick). A tick with stand-ins (a selftest) and no repair launcher gets None and
    launches nothing real (2026-11-21 12:48 AM PST: the first draft fell back to the real launcher inside selftests,
    which filed 4 real items and started 3 real runs)."""
    if "repair_launch" in (fx or {}):
        return fx["repair_launch"]
    return None if fx else repair_launch


def repair_sync(st, now, fx=None):
    """At the tick's start, before the fault loop reads its count: each running repair run (form and fault-loop) whose
    run ended is marked done (form_fault.sync_repairs); an ended fault-loop repair resets the count."""
    fx = fx or {}
    return FF.sync_repairs(st, fx.get("record") or DH.read_record, now, live=fx.get("live", DH.live_status))


def form_repair_step(root, cfg, st, rows, launches, now, apply, fx=None):
    """A mod that owes a form repair (form_fault.owe_repair) launches nothing of its own: the tick never re-sends a
    refused input unchanged. It starts ONE repair run with the refusals as its brief (apply only), and the mod's row
    reads `repairing: <what>`. A running repair whose run ended is marked done first; the mod then launches again.
    -> the launches left."""
    fx = fx or {}
    do = repair_launcher(fx)
    mods = st.get("mods") or {}
    for r in rows:
        s = mods.get(r["mod"])
        # an owed record whose refusal ends by itself (a pool clone refused: AUT.wait_refusal) is no fault of form: it
        # owes no repair run, and the mod's act is tried again (RIMMANDRAKE_UNBLOCK_PYRE_VISIT_SIX_HELD_BY_AN_ART_PICK_
        # THAT_IS_HIS). State "wait" is neither open nor done, so its fingerprint never reads as a repair that did not hold
        for x in (s.get("form_repairs") or []) if isinstance(s, dict) else []:
            if isinstance(x, dict) and x.get("state") == "owed" and FF.fault_class(x.get("text")) == "wait":
                x.update(state="wait", ended_at=now, how="a cause that ends by itself, no repair owed")
        rep = FF.open_repair(s) if isinstance(s, dict) else None
        if not rep:
            continue
        owed = [x for x in s.get("form_repairs") or [] if isinstance(x, dict) and x.get("state") == "owed"]
        if apply and do and owed and not any(x.get("state") == "running" for x in s.get("form_repairs") or []):
            if int(rep.get("repair_tries") or 0) >= REPAIR_LAUNCH_MOST:
                r["need"] = ("%s: the repair run for %s was refused %d times (the last: %s); the Conductor reads it" % (
                    r["mod"], rep["what"], rep["repair_tries"], FF.what_of(rep.get("launch_failed"))))
            else:
                filed = next((x.get("item") for x in owed if x.get("item")), None)
                try:
                    ok, text, unit = do(root, cfg, r["mod"], owed, kind="form",
                                        **({"item": filed} if filed and _takes(do, "item") else {}))
                except Exception as e:      # noqa: BLE001  the repair launcher failing is that row's line, never a crash
                    ok, text, unit = False, "%s: %s" % (type(e).__name__, e), None
                m = re.search(r"\bfiled (RIMMANDRAKE_[A-Z0-9_]+)", str(text)) if not ok else None
                for x in owed:
                    if m:
                        x["item"] = m.group(1)
                    if ok and not unit:     # the launcher repaired it in place (route 1): done, the mod goes on now
                        x.update(state="done", started_at=now, ended_at=now, how=text)
                    elif ok:
                        x.update(state="running", unit=unit, started_at=now)
                    elif FF.fault_class(text) == "wait":     # a cause that ends by itself: no try spent
                        x.update(launch_failed=text)
                    else:
                        x.update(launch_failed=text, repair_tries=int(x.get("repair_tries") or 0) + 1)
        rep = FF.open_repair(s)
        if not rep:
            continue
        how = ("repair run %s" % rep["unit"]) if rep.get("unit") else (
            "the repair launch was refused: %s" % FF.what_of(rep.get("launch_failed")) if rep.get("launch_failed")
            else "a repair run starts" if apply and do else "would start a repair run")
        line = "repairing: %s (%s)" % (rep["what"], how)
        r["repairing"] = line
        if r["mod"] in launches:
            launches = [m for m in launches if m != r["mod"]]
            r.update(decision="repairing", why="%s; it would have launched: %s" % (line, r.get("why") or "-"))
        elif r.get("decision") not in REPAIR_KEEP:
            r.update(decision="repairing", why=line)
    return launches


def fault_repair_step(root, cfg, st, rows, now, apply, fx=None):
    """When the fault loop trips (a row reads system_fault), the tick starts the repair itself: ONE repair run with the
    faults' causes as its brief, said on the row. When it ends, form_fault.sync_repairs resets the count (auto_cleared).
    A trip after FAULT_REPAIRS_MOST repair runs since the last hand clear names the Conductor and starts none."""
    fx = fx or {}
    do = repair_launcher(fx)
    mods = st.get("mods") or {}
    for r in rows:
        s = mods.get(r["mod"])
        if r.get("decision") != "system_fault" or not isinstance(s, dict):
            continue
        hand = max([c.get("at") or 0 for c in s.get("cleared") or [] if isinstance(c, dict)] or [0])
        reps = [x for x in s.get("fault_repairs") or [] if isinstance(x, dict) and (x.get("at") or 0) > hand]
        dead = reps[-1] if reps and reps[-1].get("state") == "void" else None
        reps = [x for x in reps if x.get("state") != "void"]     # a killed repair run is none of them (failure_class)
        live = next((x for x in reps if x.get("state") == "running"), None)
        if live:
            r["why"] += "; repairing: repair run %s is on it" % live.get("unit")
            continue
        if len(reps) >= FAULT_REPAIRS_MOST:
            r["need"] = ("%s: the fault loop tripped again after %d repair runs (%s): the fix is unknown; the Conductor "
                         "reads it" % (r["mod"], len(reps), ", ".join(str(x.get("unit")) for x in reps)))
            r["why"] += "; " + r["need"]
            continue
        if dead and now < (dead.get("ended_at") or 0) + VOID_REPAIR_WAIT_S:
            r["why"] += "; repair run %s did not count (%s): the next one in %d min" % (
                dead.get("unit"), dead.get("void"), ((dead.get("ended_at") or 0) + VOID_REPAIR_WAIT_S - now) / 60)
            continue
        if not (apply and do):
            r["why"] += "; would start a repair run"
            continue
        t0 = max([hand] + [x.get("at") or 0 for x in s.get("auto_cleared") or [] if isinstance(x, dict)])
        causes = [{"where": "%s %s" % (f.get("book"), f.get("unit") or f.get("key") or ""), "text": f.get("cause")}
                  for f in s.get("system_faults") or [] if RV.counted_fault(f) and (f.get("at") or 0) > t0]
        try:
            ok, text, unit = do(root, cfg, r["mod"], causes or [{"text": r.get("why")}], kind="fault")
        except Exception as e:      # noqa: BLE001
            ok, text, unit = False, "%s: %s" % (type(e).__name__, e), None
        if ok and not unit:     # repaired in place: the count resets now
            s.setdefault("fault_repairs", []).append({"at": now, "unit": None, "state": "done", "n": RV.faults(s),
                                                      "ended_at": now, "how": text})
            s.setdefault("auto_cleared", []).append({"at": now, "why": "the tick's repair on the fault loop: %s" % text})
            r["why"] += "; repaired in place: %s" % text
        elif ok:
            s.setdefault("fault_repairs", []).append({"at": now, "unit": unit, "state": "running", "n": RV.faults(s)})
            r["why"] += "; repairing: the tick started repair run %s on it" % unit
        else:
            r["why"] += "; the repair run did not start (%s): the next tick tries again" % FF.what_of(text)
    return rows


def form_repair_rows(st, rows, now):
    """After execute: a launch this tick refused for a fault of form owes its repair now (form_fault.owe_repair) and its
    row reads `repairing:`, never launch_failed (a launch_failed row has no retry left); a wait keeps its wait."""
    for r in rows:
        if r.get("decision") != "launch_failed":
            continue
        text = str(r.get("why") or "")
        if FF.fault_class(text) != "form":
            continue
        s = (st.get("mods") or {}).get(r["mod"])
        if not isinstance(s, dict):
            continue
        held = FF.owe_repair(s, text, "%s %s" % (r["mod"], r.get("stage") or "launch"), now)
        if held:
            s.setdefault("system_faults", []).append({"at": now, "book": "launch", "key": r.get("item"), "unit": None,
                                                      "cause": held, "n": 1})
        r.update(decision="repairing", why="repairing: %s (refused for a fault of form; the next tick starts a repair "
                 "run)" % FF.what_of(text), need=None)


def drain_gate(rows, launches, drain):
    """While the account drains before a planned switch (detached_helper.drain_refusal's text, or None), nothing
    launches: each row that would have launched reads account_hold, "waiting: account switch", a wait that counts no
    fault (RIMMANDRAKE_STOP_COUNTING_DRAIN_REFUSALS_AS_SYSTEM_FAULTS: three drain refusals paused FlowWorks). -> the
    launches left."""
    if not drain:
        return launches
    for r in rows:
        if r["mod"] in launches:
            r.update(decision="account_hold", why="waiting: account switch: %s; it would have launched: %s" % (
                drain, r.get("why") or "-"))
    return []


def _aut(rows, mod):
    return any(r["mod"] == mod and r.get("aut") for r in rows)


def ingame_testq(root, facts, holds):
    """-> {mod: entry} for every in-game mod this tick read (the reading's `ingame_testq` block; page
    design/specs/2026-11-22-steve-idle-takeable/boundary.md): visit, opened, owed, blocked, held (the owner's hold),
    hold_unreadable, ran_in_visit (testq checks with a row in this visit's own folder) and checks {id: [chains]}: the
    checks the visit runs (to_run) that carry a testq block with chains, less those with a row of this visit; scripts {id: {tier, build}}: those that go by
    their own script (testq/stage6_checks.py). bridge_checks lists checks with no testq block and no row in this visit.
    ops_watch reads this block (ingame_facts costs 5-16 s a mod, measured 2026-11-22; the tick already pays it).
    A mod that could not be read carries `error`, never an empty list."""
    out = {}
    for mod, f in sorted((facts or {}).items()):
        if not isinstance(f, dict) or f.get("stage") != "in_game":
            continue
        try:
            n = f.get("visit")
            tt, terr = M.read_json(root, mod, "version/test_table.json")
            tests = (tt or {}).get("tests") or {}
            ran = {t for t, r in M.BM.carried_rows(root, mod, n).items()
                   if t and isinstance(r, dict) and r.get("_visit") == n and not M.BM.LK.spoiled(r)}
            tq = set(f.get("testq") or [])
            waiting, scripts = {}, {}
            for k in f.get("to_run") or []:
                q = (tests.get(k) or {}).get("testq") if isinstance(tests.get(k), dict) else None
                if k in tq and isinstance(q, dict) and k not in ran:
                    ch = [c for c in q.get("chains") or [] if isinstance(c, str) and c]
                    if ch:
                        waiting[k] = ch
                    elif isinstance(q.get("check"), dict) and q["check"].get("tier"):
                        scripts[k] = {"tier": str(q["check"]["tier"]), "build": str(q["check"].get("build") or "release")}
            h = (holds or {}).get(OH.key(mod))
            out[mod] = {"visit": n, "opened": f.get("opened"), "owed": f.get("owed"),
                        "blocked": list(f.get("blocked") or []), "held": bool(h),
                        "hold_unreadable": bool(h and h.get("unreadable")), "ran_in_visit": sorted(ran & tq),
                        "checks": waiting, "scripts": scripts}
            if tt is None:
                out[mod]["error"] = "version/test_table.json: %s" % terr
                continue
            try:
                bridge = [k for k in f["to_run"] if "testq" not in tests[k]]
                if bridge:
                    path = os.path.join(M.mod_dir(root, mod), M.INGAME_DIR, "visit_%s" % n, "rows.jsonl")
                    try:
                        with open(path, encoding="utf-8") as rows:
                            recorded = M.BM.last_rows(json.loads(line) for line in rows if line.strip())
                    except FileNotFoundError:
                        recorded = {}     # a visit without rows has yet to record its checks
                    bridge = [k for k in bridge if k not in recorded]
                out[mod]["bridge_checks"] = bridge
            except (OSError, ValueError, KeyError, AttributeError, TypeError) as e:
                out[mod]["bridge_checks_error"] = "%s: %s" % (type(e).__name__, e)
        except Exception as e:      # noqa: BLE001  one mod unread is said, the others still read
            out[mod] = {"error": "%s: %s" % (type(e).__name__, e)}
    return out


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


def paused_rows(pz, mods, facts):
    """One row per mod paused alone (pipeline_pause.py): decision pipeline_paused, class planned (no alarm), the why,
    who and until; a run live on it is named and left to finish."""
    out = []
    for mod in mods:
        f = facts.get(mod) or {}
        live = [u for u in f.get("live_units") or [] if isinstance(u, str)]
        txt = PP.reason(pz, mod) + ("; %s live on it, allowed to finish" % ", ".join(live) if live else "")
        out.append({"mod": mod, "stage": f.get("stage", UNM), "live": live, "decision": "pipeline_paused",
                    "klass": "planned", "pipeline_paused": txt, "status": txt, "why": txt})
    return out


def tick(root, cfg, apply, fx=None, now=None, page=False):
    """One tick; with apply, under the state lock from its read of state.json to its write."""
    if not apply:
        return _tick(root, cfg, apply, fx, now, page)
    with state_lock():
        return _tick(root, cfg, apply, fx, now, page)


def _tick(root, cfg, apply, fx=None, now=None, page=False):
    fx = fx or {}
    now = now or time.time()
    d = sdir()
    st = read_state(os.path.join(d, "state.json"))
    record = fx.get("record") or DH.read_record
    mod_of = entry_mods(st)     # sync_system's callbacks name no mod: each entry's own, for its launch_tries account
    RV.sync_system(st, record, keep_failed=lambda b, x: still_retried(cfg, b, x, mod_of.get(id(x))),
                   kills_left=lambda b, x, why: kill_resumed(cfg, b, x, why, mod_of.get(id(x))), now=now)
    repair_sync(st, now, fx)
    aut = fx.get("autonomy", True)      # False: the per-stage decision alone (selftest_maturation_dispatch's layer)
    shipped = cfg                       # the file's own values, before widen adds discovered mods (maturation_hands)
    cfg = AUT.widen(root, cfg, st, apply, fx) if aut else cfg   # Designer concepts seen and seeded; the game queue
    cfg = dict(cfg, _code=(fx["code"]() if "code" in fx else pipeline_code(REPO)))   # the code this tick runs
    # a caller that stands in for the launch stands in for its deploy too, unless it gives a stand-in unit
    cfg["_deploy_unit"] = "game_deploy" in fx or "launch" not in fx
    facts = own_live(st, fx["facts"]() if "facts" in fx else gather(root, cfg), record)
    game_deploy_sync(root, st, now, fx)
    account = fx["account"]() if "account" in fx else account_gate()
    releases = fx["releases"]() if "releases" in fx else read_releases()
    # The owner's hold (mod_owner_hold.py): a held mod is read (its live run finishes, its spend and ledger rows are still
    # recorded below) but never decided, so nothing launches on it and it joins no idle, paused or stalled list.
    try:
        holds = OH.load()
        if apply:       # the live tick read the control store: its heartbeat (the item's --live reading)
            import control as C
            C.heartbeat("tick_read")
    except OH.Unreadable as e:
        # the control store (or his hold file) cannot be read: every mod is held, said, and nothing launches
        # (control.py: an unreadable store admits nothing; "could not look" is never "no holds")
        holds = {OH.key(m): {"mod": OH.key(m), "date": "", "said": str(e), "unreadable": True}
                 for m in cfg.get("advancing") or []}
    import control as C     # `pipe queue` (slice 3): the store's order and membership of the advancing list
    try:
        cfg = dict(cfg, advancing=C.queue_apply(cfg.get("advancing") or []))
    except C.Unreadable:    # the shipped order stands: the hold read above already holds every mod as UNREADABLE
        pass
    # `pipe model` (mod_model.py): the builder model pins, read once for this tick's decide and execute; pins that
    # cannot be read hold every mod, said, so a pinned mod never launches on the shipped model by a blind read
    try:
        cfg = dict(cfg, **{MM.PINS_KEY: fx["pins"]() if "pins" in fx else MM.read_pins()})
    except C.Unreadable as e:
        for m in cfg.get("advancing") or []:
            holds.setdefault(OH.key(m), {"mod": OH.key(m), "date": "", "said": "model pins: %s" % e, "unreadable": True})
    cfg = dict(cfg, advancing=[m for m in cfg.get("advancing") or [] if OH.key(m) not in holds])
    # The pipeline's pause (pipeline_pause.py; RIMMANDRAKE_ADD_PAUSE_ALL_AND_UP_NEXT_HOLD_LEAKED), read at the moment of
    # deciding, no git hop; an --until that has passed resumes by itself (an applying tick moves it to history and says
    # so). A mod paused alone leaves the advancing list before any slot is granted (its live runs still count: facts
    # keep it), so it never takes a slot from a mod behind it; under a pause of everything every row is decided and
    # its launch withheld below.
    pause_said = PP.expire(now) if apply else []
    pz = fx["pause"](now) if "pause" in fx else PP.state(now)
    paused_alone = [] if PP.reason(pz) else [m for m in cfg.get("advancing") or [] if PP.reason(pz, m)]
    cfg = dict(cfg, advancing=[m for m in cfg.get("advancing") or [] if m not in paused_alone])
    rows, launches = decide(cfg, st, facts, now, account, bridge=fx.get("bridge"), releases=releases)
    if aut:
        rows, launches = AUT.resolve(root, cfg, st, facts, rows, launches, now, fx)
        rows, launches = pilot_holders(root, cfg, st, facts, rows, launches, now, dict(fx, account=lambda: account))
    launches = one_run_fence(facts, rows, launches)     # before the slots: a mod that waits on its own run takes none
    launches = prioritise(cfg, st, facts, rows, launches, root)     # one slot order over every layer: the list's
    # the pause's gate on every layer's launch row: pipeline_paused (class planned: no alarm); a live run is left alone
    for r in rows:
        why = PP.reason(pz, r["mod"])
        if why:
            r["pipeline_paused"] = why
            if r["mod"] in launches:
                r.update(decision="pipeline_paused", why="%s; it would have launched: %s" % (why, r.get("why") or "-"))
    launches = [m for m in launches if not PP.reason(pz, m)]
    ctl = PC.state()    # `pipe off all|item:<ID>|stage:<S>` (a mod's own switch reads as a hold, above): nothing launches
    for r in rows:
        if r["mod"] in launches:
            why = PC.off(item=r.get("item") or r.get("fix_item"), stage=r.get("stage"), st=ctl)
            if why:
                r.update(decision="control_off", klass="held", why=why, status=why)
                launches = [m for m in launches if m != r["mod"]]
    launches = system_fault_stop(cfg, st, rows, launches)
    # the account drain (drain_gate); a caller that stands in for the account gate (a selftest) stands in for this too
    launches = drain_gate(rows, launches, fx["drain"](now) if "drain" in fx else
                          None if "account" in fx else DH.drain_refusal(now))
    # the fault loop's own repair, and the form repairs owed: the tick never re-sends a refused input unchanged
    fault_repair_step(root, cfg, st, rows, now, apply, fx)
    launches = form_repair_step(root, cfg, st, rows, launches, now, apply, fx)
    if not cfg.get("enabled"):
        for r in rows:
            if r["mod"] in launches:
                r.update(decision="disabled", why="the step is disabled in maturation_dispatch.json")
        launches = []
    # measured before any launch: a clone behind past the alarm's threshold read an old tree, so it launches nothing
    # (RIMMANDRAKE_HOLD_TICK_LAUNCHES_ON_STALE_CLONE_GHOST_STEWARD: 51 min behind, it launched a steward run for a
    # blind record whose exit block had landed 5 min before)
    # the dry pass (the forecast) gates on the counts the last applying tick measured (fx clone_seen), aged to its own
    # clock by the same clone_reading (counts held, behind_since kept), so it refuses where the applying tick would
    seen = fx.get("clone_seen")
    clone = (clone_reading(st, now, (fx.get("clone") or (lambda: clone_counts(root)))(),
                           head=_head_sha((fx.get("clone_head") or (lambda: clone_head(root)))())) if apply else
             clone_reading({"clone": {k: seen.get(k) for k in ("behind_since", "level_at") if seen.get(k)}}, now,
                           (seen.get("behind"), seen.get("ahead"))) if isinstance(seen, dict) and seen.get("measured")
             else seen)
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
    if apply:
        form_repair_rows(st, rows, now)
    for r in rows:      # a release lets one launch: the launch spends it
        if r.get("release") and r.get("decision") == "launched":
            st["mods"][r["mod"]].setdefault("releases_used", {})[r["release"]] = {
                "at": now, "stage": r.get("stage"), "usd": r.get("stage_usd"), "unit": r.get("unit")}
    if apply:
        book_refunds(st, rows, now)
    AUT.classify(cfg, st, rows, now)
    for r in rows:      # the forecast's and the status's word for what a launch row starts (launch_kind)
        if r.get("decision") in ("would_launch", "launched"):
            r["launch"] = launch_kind(cfg, r, root)
    rows += paused_rows(pz, paused_alone, facts)
    rows += held_rows(holds, facts)
    if apply and aut:
        AUT.post_cards(rows, st, now, fx)
    rd = AUT.annotate(reading(cfg, rows, now), rows)
    rd["pipeline_pause"] = PP.summary(pz)
    for x in pause_said:
        if x not in rd["pipeline_pause"]["said"]:
            rd["pipeline_pause"]["said"].append(x)
    rd["voids"] = RV.status_lines(st, record)
    try:    # in-game checks owed to SteveDesktop and the Arch drivers (ops_watch reads this block)
        rd["ingame_testq"] = ingame_testq(root, facts, holds)
    except Exception as e:      # noqa: BLE001  this reading failing never costs the tick; ops_watch reads UNMEASURED
        rd["ingame_testq_error"] = "%s: %s" % (e.__class__.__name__, str(e))
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
        try:        # a scene short of its X of Y: the Conductor is asked, once (shortfall.py; owner, 2026-11-23)
            import shortfall as SF      # noqa: E402
            SF.observe(facts, st, now, rd, dict({"holds": {OH.key(m) for m in holds}}, **(fx.get("shortfall") or {})))
        except Exception as e:      # noqa: BLE001  this reading failing never costs the tick
            rd["shortfall_error"] = "%s: %s" % (e.__class__.__name__, e)
        _write(os.path.join(d, "state.json"), st)
        _write(os.path.join(d, "reading.json"), rd)
        with open(os.path.join(d, "ticks.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"at": now, "decisions": {r["mod"]: [r.get("decision"), r.get("refused"), r.get("klass")]
                                                         for r in rows},
                                "launched": rd["launched"]}) + "\n")
    # The page is built by its own unit (rm-maturation-page.timer), not here: as a child of the tick it ran in the tick's
    # cgroup, ~326 MB beside the tick's ~340 MB and 46 s of each tick's wall; the unit read 1G peaks and a 5 min tick at
    # its 1G MemoryMax (journal 2026-11-23 02:15-02:31 PST; RIMMANDRAKE_SLIM_TICK_MEMORY_PAGE_BUILD_HITS_ONE_GIG_TICK_TOOK_FIVE_MIN,
    # boundary design/specs/2026-11-23-tick-page-own-unit/boundary.md). page=True (`tick --page`) is a hand tick's.
    if page and apply:
        regen = fx.get("page") or (lambda: subprocess.run([sys.executable, os.path.join(
            # budget: danger=a hung page build holds a hand tick; longest=124s (1228 rm-maturation-page runs, user journal, 14
            # budget: days to 2026-11-24)
            REPO, "src", "RimMandrake", "Utils", "maturation_now.py")], capture_output=True, text=True, timeout=1800))
        r = regen()
        rd["page"] = "regenerated" if getattr(r, "returncode", 0) == 0 else "page failed: %s" % (
            (getattr(r, "stdout", "") or "") + (getattr(r, "stderr", "") or ""))
    return rd


# ---- the pipeline's pause and its "up next" forecast (RIMMANDRAKE_ADD_PAUSE_ALL_AND_UP_NEXT_HOLD_LEAKED) ---------------
# The owner, 2026-11-18 ~10:27 AM PST: "perhaps some kind of "up next" feature we can ping that says what WILL happen in
# some amount of time if we do nothing, so we can confirm using its own code..."
VOID_ITEM = "RIMMANDRAKE_VOID_SYSTEM_KILLED_RUNS_NO_TRIAL_SPENT"


def launch_kind(cfg, r, root=None):
    try:
        cfg = MM.for_mod(cfg, r.get("mod"))
    except Exception as e:      # noqa: BLE001  unknown is said, never the shipped model shown as the truth
        return {"kind": r.get("aut") or r.get("stage") or "run", "model": "%s (%s)" % (UNM, e), "cap_usd": None,
                "rule": "model pin"}
    return _launch_kind(cfg, r, root)


def _launch_kind(cfg, r, root=None):
    """-> {"kind", "model", "cap_usd", "rule"}: what a launch row starts, read from the row the tick hands execute (a
    stage run on a pilot mod is its holder: its cap is holder_cap's, as execute will set it)."""
    if r.get("aut") in NO_SLOT_AUT:
        return {"kind": r["aut"], "model": "none (an act: one landing, no run)", "cap_usd": 0,
                "rule": "maturation_autonomy %s" % r["aut"]}
    if r.get("aut"):
        return {"kind": r["aut"], "model": cfg.get("steward_model", "opus"),
                "cap_usd": cfg.get("fix_cap_usd" if r["aut"] == "fixer" else "steward_cap_usd"),
                "rule": "maturation_autonomy %s%s" % (r["aut"], " on %s" % r["fix_item"] if r.get("fix_item") else "")}
    if r.get("holder_items"):
        return {"kind": "holder", "model": cfg.get("steward_model", "opus"), "cap_usd": r.get("cap") or cfg.get("cap_usd"),
                "rule": "pilot_holders on %s" % ", ".join(
                    str(x.get("id") if isinstance(x, dict) else x) for x in r["holder_items"])}
    if r.get("game_deploy_start"):
        return {"kind": "game copy deploy", "model": "none (zero tokens)", "cap_usd": 0, "rule": "decide_ingame"}
    if r.get("cert_rerun_key"):
        return {"kind": "certificate rerun", "model": "none (zero tokens)", "cap_usd": 0, "rule": "cert_rerun_decide"}
    if r.get("cert_reds"):
        return {"kind": "builder on red deciders", "model": cfg.get("model", "opus"), "cap_usd": r.get("cap") or
                cfg.get("cap_usd"), "rule": "cert_red_decide"}
    stage = r.get("stage")
    cap = r.get("cap") or cfg.get({"blind_challenge": "blind_cap_usd", "in_game": "ingame_cap_usd"}.get(stage, "cap_usd"))
    if root is not None and isinstance(cap, (int, float)) and pilot_ledger(root, r["mod"]):
        cap = holder_cap(cfg, r, cap)
    return {"kind": ROLE_OF_STAGE.get(stage, "run"),
            "model": (cfg.get("ingame_model", "opus") if stage == "in_game" else MM.judge_model(cfg)
                      if stage == "blind_challenge" else cfg.get("model", "opus")),
            "cap_usd": cap, "rule": {"blind_challenge": "decide_blind", "in_game": "decide_ingame"}.get(
                stage, "decide (offline build)")}


STOP_RUNNER = [subprocess.run]     # stop_live's runner (a selftest swaps it; nothing else does)


def stop_live(root, cfg, mod=None, facts=None, runner=None):
    """--stop-live: stop every live run on the advancing mods (mod: on that one). -> [{"mod", "unit", "rc", "said"}].
    Each stopped run is recorded for voiding (VOID_ITEM's mechanism when it lands: a system-killed run spends no
    trial); until then the record is the pause store's history, act stop_live, void_owed true."""
    facts = facts if facts is not None else gather(root, cfg)
    runner = runner or STOP_RUNNER[0]
    out = []
    for m, f in sorted(facts.items()):
        if mod and OH.key(m) != OH.key(mod):
            continue
        if not isinstance(f.get("live_units"), list):     # unknown occupancy is never "nothing live"
            out.append({"mod": m, "unit": None, "rc": 2, "said": "its live runs cannot be read (UNMEASURED): nothing "
                        "was stopped on it and nothing proves none is live"})
            continue
        for u in f.get("live_units"):
            if not isinstance(u, str):
                continue
            try:
                r = runner(["systemctl", "--user", "stop", u], capture_output=True, text=True, timeout=120)
                rc, said = r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()
            except Exception as e:      # noqa: BLE001  a stop that fails is said, never read as stopped
                rc, said = 1, "%s: %s" % (type(e).__name__, e)
            out.append({"mod": m, "unit": u, "rc": rc, "said": said})
    return out


def forecast(root, cfg, within_s=1800, step_s=None, fx=None, now=None):
    """What WILL start within within_s if nobody acts, by the tick's own code: _tick in its dry pass (apply False)
    over ONE observation of the world (the facts, account, releases and code read once), the clock moved step by
    step, so settle timers, waits on time and a pause's --until end as they will. -> {"at", "within_s", "launches":
    [{"mod", "at", "at_pac", "launch", "why"}], "blocked": [{"mod", "decision", "why"}], "unmeasured": [why],
    "roles": [line]}. A launch is the mod's FIRST one; what follows a launch is not forecast (it depends on the
    run). A live run's end cannot be forecast: its mod reads UNMEASURED, never "nothing"."""
    fx = dict(fx or {})
    now = time.time() if now is None else now
    step = float(TICK_S if step_s is None else step_s)
    if not (step > 0 and step == step and step != float("inf")):
        raise ValueError("--step must be a positive number of seconds, not %r" % step_s)
    unmeasured = []
    if "facts" not in fx:
        st0 = read_state(os.path.join(sdir(), "state.json"))
        wcfg = AUT.widen(root, cfg, st0, False, fx) if fx.get("autonomy", True) else cfg
        f0 = gather(root, wcfg)
        fx["facts"] = lambda: f0
    if "account" not in fx:
        a0 = account_gate()
        fx["account"] = lambda: a0
    if "releases" not in fx:
        r0 = read_releases()
        fx["releases"] = lambda: r0
    if "code" not in fx:
        c0 = pipeline_code(REPO)
        fx["code"] = lambda: c0
    if "clone_seen" not in fx:      # the stale-clone gate reads what the last applying tick measured
        fx["clone_seen"] = (_read(os.path.join(sdir(), "reading.json"), None) or {}).get("clone")
    first, last, t = {}, {}, now
    while t <= now + within_s + 1e-6:
        rd = _tick(root, cfg, False, fx=fx, now=t, page=False)
        for mod, r in (rd.get("mods") or {}).items():
            if mod in first:
                continue
            if r.get("decision") == "would_launch":
                first[mod] = {"mod": mod, "at": t, "at_pac": pac(t), "launch": r.get("launch") or {}, "why": r.get("why")}
            else:
                last[mod] = {"mod": mod, "decision": r.get("decision"), "why": r.get("status") or r.get("why"),
                             "live": r.get("live")}
        t += step
    blocked = [v for m, v in sorted(last.items()) if m not in first]
    for b in blocked:
        if isinstance(b.get("live"), list) and b["live"]:
            unmeasured.append("%s: UNMEASURED after its live run(s) %s end: a run's end cannot be forecast, so what "
                              "starts then is not read here" % (b["mod"], ", ".join(map(str, b["live"]))))
        elif b.get("live") is not None and not isinstance(b.get("live"), list):
            unmeasured.append("%s: UNMEASURED, its live runs cannot be read" % b["mod"])
    if not isinstance(fx.get("clone_seen"), dict):
        unmeasured.append("the dispatch clone's distance from origin/main has no reading: a stale clone launches "
                          "nothing, and this forecast could not check it")
    return {"at": now, "at_pac": pac(now), "within_s": within_s, "step_s": step,
            "launches": sorted(first.values(), key=lambda x: x["at"]), "blocked": blocked, "unmeasured": unmeasured,
            "roles": forecast_roles(now, within_s, fx.get("schedule"))}


def forecast_roles(now, within_s, sched=None):
    """The Dispatcher's pipeline roles (chain_stages: Designer, DesignerCodex) and red_dispatch, in the same
    forecast: blocked by the pause (pipeline_pause.reason, the gate role_launch reads), off, disabled, or a scheduled
    slot inside the window. A chain or sweep run starts when a Designer stage closes or a concept sits orphaned: that
    depends on a run's end and reads UNMEASURED, never as nothing."""
    out = []
    try:
        if sched is None:
            with open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8") as f:
                sched = json.load(f)
        import role_launch as RL
    except Exception as e:      # noqa: BLE001
        return ["Dispatcher roles: UNMEASURED, the schedule cannot be read (%s: %s)" % (type(e).__name__, e)]
    pz = PP.state(now)
    for role in sched.get("roles") or []:
        if not isinstance(role, dict) or role.get("chain_stages") is not True:
            continue
        name = role.get("name", "?")
        why = PP.reason(pz)
        ends = (pz.get("all") or {}).get("until") if not pz.get("error") else None
        if why and not (ends and ends <= now + within_s):
            out.append("%s: nothing starts in the window, %s" % (name, why))
            continue
        if why:
            why = "nothing starts until the pause ends at %s (%s); after that" % (pac(ends), why)
        if not role.get("enabled"):     # decide_roles still sweeps a disabled chain role and launches its run-now
            out.append("%s: no scheduled slot (the role is disabled in dispatcher_schedule.json); a run-now its chain "
                       "sweep or a person asks still launches: UNMEASURED here; paused concepts: %s" % (
                           name, ", ".join(sorted(pz.get("mods") or {})) or "none")
                       if not why else "%s: %s no scheduled slot (the role is disabled); a run-now its chain sweep or "
                       "a person asks then launches: UNMEASURED here" % (name, why))
            continue
        off = RL.off_switch(RL.wsl_path(role.get("off_file") or ""))
        if off is not None:
            out.append("%s: nothing (off switch %s: %s)" % (name, role.get("off_file"), off or "no reason given"))
            continue
        try:
            due = [(sl, RL.slot_epoch(now + d, sl)) for d in (0, 86400) for sl, _m, _c in RL.slots(
                dict(RL.ROLE_DEFAULTS, **role), now + d)]
            due = [(sl, t) for sl, t in due if now <= t <= now + within_s]
        except Exception as e:      # noqa: BLE001
            out.append("%s: UNMEASURED, its slots cannot be read (%s)" % (name, e))
            continue
        def at(sl, t):
            w = PP.reason(PP.state(t))      # the pause as it will stand at the slot (an --until may have ended)
            return "%s at %s%s" % (sl, pac(t), " (paused then: it will not start)" if w else "")
        out.append("%s: %s%s; chained and swept runs (a stage closing, an orphaned concept, a run-now) are UNMEASURED: "
                   "they start on a run's end, which this forecast cannot see; paused concepts: %s" % (
                       name, "%s: " % why if why else "",
                       "scheduled slot(s) %s" % ", ".join(at(sl, t) for sl, t in due) if due
                       else "no scheduled slot in the window", ", ".join(sorted(pz.get("mods") or {})) or "none"))
    why = PP.reason(pz)
    ends = (pz.get("all") or {}).get("until") if not pz.get("error") else None
    out.append(("red_dispatch: nothing starts until %s (%s); after that UNMEASURED here" % (pac(ends), why))
               if why and ends and ends <= now + within_s else "red_dispatch: nothing starts, %s" % why if why else
               "red_dispatch: UNMEASURED here (its own dry pass: `red_dispatch.py tick`)")
    return out


def forecast_lines(fc):
    mins = int(fc["within_s"] // 60)
    out = ["UP NEXT from %s, the next %d min, by the tick's own decision code (dry, the clock moved every %d s%s):" % (
        fc["at_pac"], mins, fc["step_s"], "" if fc["step_s"] <= TICK_S else
        "; coarser than the %d s tick, so each time is approximate, up to %d s late" % (TICK_S, fc["step_s"]))]
    if fc["launches"]:
        for x in fc["launches"]:
            k = x.get("launch") or {}
            out.append("  WILL START %s (+%d min): %s %s (model %s, cap %s), by %s; %s" % (
                x["at_pac"], (x["at"] - fc["at"]) // 60, x["mod"], k.get("kind", "run"), k.get("model", UNM),
                wt(k["cap_usd"]) if isinstance(k.get("cap_usd"), (int, float)) and k["cap_usd"] > 0 else "none",
                k.get("rule", UNM), x.get("why") or ""))
    else:
        out.append("  NOTHING WILL START in the tick's layers in the next %d min%s" % (
            mins, " (but see UNMEASURED below)" if fc["unmeasured"] else ""))
    for b in fc["blocked"]:
        out.append("  not starting: %-20s %s: %s" % (b["mod"], b["decision"], b["why"]))
    for u in fc["unmeasured"]:
        out.append("  %s" % u)
    for r in fc["roles"]:
        out.append("  %s" % r)
    return out


def _within(text):
    m = PP.REL.match(str(text).strip().lower().lstrip("+")) or PP.REL.match("+" + str(text).strip().lower())
    if not m:
        raise ValueError("--within %r: give 30m, 2h or 1d" % text)
    return float(m.group(1)) * {"m": 60, "min": 60, "h": 3600, "hr": 3600, "d": 86400}[m.group(2)]


def _by(o):
    import doorbell
    import model
    return model.canonical((getattr(o, "by", None) or doorbell.seat_name() or "").strip()) or "unknown"


HAND_NOTE = ("This is a hand act on the pipeline (id %s): the tick records it, and one with no follow-up within a day "
             "alarms. Name the item that makes this hand unnecessary in --why, or `maturation_hands.py fold <id> --item "
             "<ID>` once it is filed.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=REPO)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tick")
    t.add_argument("--apply", action="store_true", help="launch and write state; without it, a dry pass")
    t.add_argument("--page", action="store_true", help="also build MATURATION_NOW (by hand; the timed tick never does: "
                   "rm-maturation-page.timer builds it in its own cgroup)")
    t.add_argument("--no-page", action="store_true", help=argparse.SUPPRESS)    # the default now; kept for old callers
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
    jr = sub.add_parser("judge-reopen", help="a VOIDED judge's sealed shard takes its own lines: reopen the seal, "
                                             "append FILE's lines of that run, seal again; prints the paths to land")
    jr.add_argument("mod")
    jr.add_argument("--run", required=True, help="the judge's ledger run (judge-<epoch>)")
    jr.add_argument("--lines", help="a JSONL file holding the run's own shard lines (a bundle's copy)")
    jr.add_argument("--why", default="")
    cr = sub.add_parser("cert-rerun", help="the certificate rerun unit's body: certificate MOD --run in a pool clone, "
                                           "publish the table, write the result the tick reads (zero tokens)")
    cr.add_argument("mod")
    cr.add_argument("--key", required=True)
    cr.add_argument("--unit", required=True)
    gu = sub.add_parser("game-deploy", help="the game copy deploy unit's body: game-repair MOD in a pool clone, the result "
                                            "written for the tick (zero tokens)")
    gu.add_argument("mod")
    for k in ("--game", "--kind", "--purpose", "--unit"):
        gu.add_argument(k, required=True)
    gu.add_argument("--seat", default="BENCH")
    pz = sub.add_parser("pause", help="pause the whole pipeline (or MOD): nothing starts until resume or --until; live "
                                      "runs finish unless --stop-live")
    pz.add_argument("mod", nargs="?", help="one mod only (default: every pipeline path)")
    pz.add_argument("--why", required=True)
    g = pz.add_mutually_exclusive_group()
    g.add_argument("--until", help="+90m, +2h, HH:MM (local), an ISO date-time or an epoch: then it resumes by itself")
    g.add_argument("--until-release", action="store_true", help="until `resume` (the default)")
    pz.add_argument("--stop-live", action="store_true", help="also stop the runs live on it now, recorded for voiding")
    pz.add_argument("--by", default=None, help="who pauses (default: this window's seat)")
    rs_ = sub.add_parser("resume", help="lift the pause on the whole pipeline (or on MOD)")
    rs_.add_argument("mod", nargs="?")
    rs_.add_argument("--why", required=True)
    rs_.add_argument("--by", default=None)
    nx = sub.add_parser("next", help="what WILL start if nobody acts, by the tick's own decision code (a dry pass "
                                     "on a moving clock)")
    nx.add_argument("--within", default="30m", help="the window: 30m, 2h, 1d (default 30m)")
    nx.add_argument("--step", type=float, default=None, help="seconds between simulated ticks (default within/30, "
                                                                "at least 60)")
    nx.add_argument("--json", action="store_true")
    for name, hlp in (("void", "a run that died of a system cause, or that the owner or Conductor stopped or declares "
                               "void, spends no trial (run_void.py): one line per run, its Designer runs and judges"),
                      ("unvoid", "reverse a void: the run counts again")):
        vp = sub.add_parser(name, help=hlp)
        vp.add_argument("units", nargs="*", help="run units (rm-detached-..., rm-coverage-judge-..., rm-role-...)")
        if name == "void":
            vp.add_argument("--item", help="every run of this item")
            vp.add_argument("--mod", help="with --since: every run on this mod since then")
            vp.add_argument("--since", help="ISO time, or local Pacific 'YYYY-MM-DD HH:MM'")
        vp.add_argument("--why", required=True)
        vp.add_argument("--owner-said", help="his words, when it is his call")
        vp.add_argument("--by", default=None, help="who (default: this window's seat)")
        vp.add_argument("--no-land", action="store_true", help="write the repo files, do not ./publish them")
    sub.add_parser("voids", help="every void and unvoid line, and what stands")
    o = ap.parse_args(argv)
    if o.cmd in ("void", "unvoid"):
        with state_lock():
            return _void(o)
    if o.cmd == "voids":
        return _voids()
    if o.cmd in ("pause", "resume"):
        return _pause_verb(o)
    if o.cmd == "next":
        try:
            within = _within(o.within)
        except ValueError as e:
            print("REFUSED: %s" % e)
            return 2
        try:
            fc = forecast(os.path.abspath(o.root), load_cfg(), within, o.step)
        except ValueError as e:
            print("REFUSED: %s" % e)
            return 2
        print(json.dumps(fc, indent=1, default=str) if o.json else "\n".join(forecast_lines(fc)))
        return 0
    if o.cmd == "cert-rerun":
        res = cert_rerun_worker(o.mod, o.key, o.unit)
        print(json.dumps(res, indent=1))
        return 1 if res.get("error") else 0
    if o.cmd == "game-deploy":
        res = game_deploy_worker(o.mod, o.game, o.kind, o.purpose, o.unit, seat=o.seat)
        print(json.dumps(res, indent=1))
        return {"ok": 0, "wait": 75}.get(res["state"], 1)
    cfg = load_cfg()
    if o.cmd == "tick":
        rd = tick(os.path.abspath(o.root), cfg, o.apply, page=o.page and not o.no_page)
        for mod, r in rd["mods"].items():
            print("%-20s %-7s %-13s %s" % (mod, r.get("klass"), r["decision"], r.get("status") or r["why"]))
        print("idle owed max %s min%s; launched %d; page %s" % (
            rd["idle_owed_max_min"], (" (over %s: %s)" % (rd["idle_alarm_min"], ", ".join(rd["idle_owed_mods"])))
            if rd["idle_owed_mods"] else "", len(rd["launched"]), rd.get("page", "built by rm-maturation-page.timer")))
        return 0
    if o.cmd == "judge-verify":
        print(judge_verify_text(os.path.abspath(o.root), o.mod), end="")
        return 0
    if o.cmd == "judge-reopen":
        rc, text, paths = reopen_void_judge(os.path.abspath(o.root), read_state(os.path.join(sdir(), "state.json")),
                                            o.mod, o.run, o.lines, o.why)
        print(text)
        print("PATHS %s" % " ".join(paths) if paths else "PATHS none")
        return rc
    if o.cmd == "pilot-launch":
        rc, text = pilot_launch(os.path.abspath(o.root), cfg, o.mod, o.why, item=o.item, usd=o.usd)
        print(text)
        return rc
    if o.cmd == "status":
        for x in PP.status_lines(PP.state()):    # the switch as it stands now, ahead of the last reading
            print(x)
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


def _pause_verb(o):
    """`pause` / `resume`: write the pause store (pipeline_pause.py); the next tick (within 60 s) reads it, with no
    git hop. --stop-live stops the live runs and records them for voiding."""
    by = _by(o)
    if not o.why.strip():
        print("REFUSED: --why is empty")
        return 2
    scope = OH.key(o.mod) if o.mod else "the whole pipeline"
    import control as C     # the one control store: `pause` IS `pipe off all|<Mod>`, binding the moment it commits
    cscope = "mod:" + OH.key(o.mod) if o.mod else "all"
    if o.cmd == "resume":
        try:
            r = C.switch(cscope, False, o.why)
        except C.Unreadable as e:
            print("REFUSED: the control store cannot be read, so nothing is resumed over it (it reads PAUSED): %s" % e)
            return 1
        fwas = None
        try:        # pause.json is retired; an old entry still standing there is lifted too, so it stops holding
            d = PP.load()
            if (d["mods"].get(OH.key(o.mod)) if o.mod else d["all"]):
                fwas = PP.resume(o.mod, o.why, by)
        except PP.Unreadable:
            pass
        still = PP.reason(PP.state(), o.mod)
        tick = C.tick_now() if not still else None
        print("RESUMED %s by %s: %s (was: %s)%s%s" % (scope, by, o.why.strip(), "paused" if r.get("had") or fwas
                                                    else "not paused", "; STILL %s" % still if still else "",
                                                    "; " + tick if tick else ""))
        return 0
    try:
        until = PP.parse_until(o.until) if o.until else None
    except ValueError as e:
        print("REFUSED: %s" % e)
        return 2
    try:
        r = C.switch(cscope, True, o.why, until=until)
    except C.Unreadable as err:
        print("NOTHING STARTS ALREADY: the control store cannot be read, so it admits no launch; the pause is not "
              "written (repair: pipe doctor): %s" % err)
        return 1
    e = {"why": o.why.strip(), "by": by, "at": r["act"]["ts"], "until": until, "until_release": until is None}
    print("PAUSED %s: %s. It binds now: every launch reads the control store at the moment it starts (`pipe show`)%s"
          % (scope, PP.line(e), "; cancelled before start: %s" % ", ".join(r["cancelled"]) if r["cancelled"] else ""))
    if o.stop_live:
        # the launch scope the tick decides over: the shipped list widened by the concepts it discovers, plus MOD
        cfg = load_cfg()
        try:
            cfg = AUT.widen(os.path.abspath(o.root), cfg, read_state(os.path.join(sdir(), "state.json")), False, {})
        except Exception as err:    # noqa: BLE001  the shipped list still stops; the gap is said
            print("  WARNING the discovered concepts could not be read (%s): only the shipped list is stopped" % err)
        if o.mod and OH.key(o.mod) not in [OH.key(m) for m in cfg.get("advancing") or []]:
            cfg = dict(cfg, advancing=list(cfg.get("advancing") or []) + [OH.key(o.mod)])
        stopped = stop_live(os.path.abspath(o.root), cfg, o.mod)
        C.note("stop_live", cscope, o.why, {"units": stopped, "void_owed": True, "void_item": VOID_ITEM, "by": by})
        for x in stopped:
            print("  %s %s on %s (rc %s)%s" % ("STOPPED" if x["rc"] == 0 else "STOP FAILED", x["unit"], x["mod"],
                                               x["rc"], ": " + x["said"] if x["said"] else ""))
        print("  %s; recorded in the control store for voiding (`pipe log`); the three stop modes are `pipe stop <scope> "
              "--write-now | --at-easy-spot | --kill`" % (
                  "%d live run(s) stopped" % sum(1 for x in stopped if x["rc"] == 0) if stopped else "no run was live"))
        if any(x["rc"] != 0 for x in stopped):
            return 1
    else:
        live = [u for f in gather(os.path.abspath(o.root), load_cfg()).values() for u in f.get("live_units") or []
                if isinstance(u, str)] if not o.mod else []
        if live:
            print("  live runs finish (no --stop-live): %s" % ", ".join(live))
    return 0


def _voids():
    """`voids`: every void and unvoid line, the ones that stand marked."""
    recs, bad = RV.read()
    cur = RV.active(recs=recs)
    for r in recs:
        print("%s %s %-6s %s %s (%s, by %s%s): %s%s" % (
            r["ts"], r.get("id"), r["act"].upper(), r["unit"], r.get("mod") or "-", r.get("item") or "-",
            r.get("by"), ", his words: %s" % r["owner_said"] if r.get("owner_said") else "", r["why"],
            " [STANDS]" if r["act"] == "void" and (cur.get(r["unit"]) or {}).get("id") == r.get("id") else ""))
    print("%d line(s), %d standing void(s), %d malformed line(s) in %s" % (len(recs), len(cur), bad, RV.path()))
    return 0


def _void(o):
    """`void` / `unvoid`, under the state lock: the void lines, then state.json and each touched concept's stage.json
    (and a void judge's verdict file) made to agree, then the repo files landed with ./publish."""
    import doorbell
    import model
    import designer_stage as DS
    by = model.canonical((o.by or doorbell.seat_name() or "").strip()) or RV.UNM
    p = os.path.join(sdir(), "state.json")
    try:
        st = read_state(p)
    except RuntimeError as e:
        print("REFUSED: %s" % e)
        return 1
    root = os.path.abspath(o.root)
    if o.cmd == "void":
        since = None
        if o.since or o.mod:
            since = RV.parse_time(o.since) if o.since else None
            if since is None or not o.mod:
                print("REFUSED: --mod and --since go together (--since an ISO time or 'YYYY-MM-DD HH:MM' Pacific)")
                return 2
        if not (o.units or o.item or o.mod):
            print("REFUSED: name the runs: units, --item ID, or --mod MOD --since TIME")
            return 2
        lines, bad = RV.void(root, st, o.units, o.item, o.mod, since, o.why, by, o.owner_said)
    else:
        if not o.units:
            print("REFUSED: name the units to unvoid")
            return 2
        lines, bad = RV.unvoid(o.units, o.why, by, o.owner_said)
    if bad:
        print("REFUSED: %s" % bad)
        return 2
    cur = RV.active()
    RV.sync_dispatch(st, cur)
    _write(p, st)
    paths = []
    for mod in sorted({ln.get("mod") for ln in lines if ln.get("mod")}):
        d = os.path.join(root, "design", "concepts", mod)
        if os.path.isfile(DS.state_path(d)):
            DS.write_json(DS.state_path(d), DS.load_state(d))    # load_state syncs it: the committed file agrees
            paths.append(os.path.relpath(DS.state_path(d), root))
        for ln in lines:
            if ln.get("mod") == mod and str(ln["unit"]).startswith("rm-coverage-judge-"):
                paths += RV.swap_verdict(root, mod, ln["unit"], back=o.cmd == "unvoid")
    for ln in lines:
        print("%s %s %s (%s, %s): %s" % (ln["act"].upper(), ln["unit"], ln.get("mod") or "-", ln.get("item") or "-",
                                          ln["id"], ln["why"]))
    for x in RV.status_lines(st):
        print(x)
    paths = list(dict.fromkeys(paths))
    keep = RV.landable(root, paths)
    same = [p for p in paths if p not in keep]
    if same:    # a rewritten file equal to HEAD is nothing to land, not a failed landing
        print("nothing to land (equal to HEAD): %s" % " ".join(same))
        paths = [p for p in paths if p not in same]
    if paths and not o.no_land:
        r = subprocess.run([os.path.join(root, "publish"), "-m", "%s: %d run(s), %s" % (
            o.cmd, len(lines), o.why[:80])] + paths, cwd=root, capture_output=True, text=True, timeout=21600)  # budget: class=publish
        last = [x for x in (r.stdout or "").splitlines() if x.startswith("PUBLISHED")]
        if r.returncode != 0 or not last:
            print("%s WRITTEN, NOT LANDED: ./publish exited %d; land these by hand: %s\n%s" % (
                o.cmd.upper(), r.returncode, " ".join(paths), ((r.stdout or "") + (r.stderr or ""))[-800:]))  # cut-ok: terminal display
            return 1
        print(last[-1])
    elif paths:
        print("not landed (--no-land): %s" % " ".join(paths))
    return 0


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
    for book in CERT_BOOK.values():     # a stop on red deciders or on red proofs owed (cert_red_decide) lifts the same way
        if s.get(book):
            gone = s.pop(book)
            was = was or {book: gone}
    if s.get("cert_rerun"):     # a certificate rerun spent on a build (cert_rerun_decide) may run once more
        was = was or {"cert_rerun": s.pop("cert_rerun")}
        s.pop("cert_rerun", None)
    if (s.get("game_deploy") or {}).get("ended"):       # an ended deploy is read again; a running one keeps its game
        s.pop("game_deploy")
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
