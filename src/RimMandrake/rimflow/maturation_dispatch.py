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
                live-game driver at a time across all mods), and `rimflow bridge idle` says takeable: one live driver
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
import datetime as dt
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
import maturation_now as MN     # noqa: E402
import maturation_autonomy as AUT   # noqa: E402
import detached_helper as DH    # noqa: E402

UNM = "UNMEASURED"
RELEASE_STAGES = ("offline_build", "blind_challenge", "in_game")
READ_SLACK = 0.5        # USD: a release read at this spend, give or take, is still a reading of it
CFG_PATH = os.path.join(HERE, "maturation_dispatch.json")
ALARM_NAME = "OPS_MATURATION_IDLE_ADVANCING_MOD"
CLONE_ALARM_NAME = "OPS_DISPATCH_CLONE_BEHIND_UNSTICK"     # ops_watch_rules.json: maturation.clone_behind_min > 5
ITEM = "RIMMANDRAKE_WIRE_DISPATCH_TO_LAUNCH_BUILDERS_MODS_SAT_IDLE"
OWED = ("build", "hand step", "ready to advance")
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


def pac(t):
    return dt.datetime.fromtimestamp(t, MN.PAC).strftime("%Y-%m-%d %I:%M %p %Z").replace(" 0", " ")


def word(n):
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("" if n % 10 == 0 else "_" + ONES[n % 10])
    return "MANY"


def item_id(mod, count, known):
    base = "RIMMANDRAKE_AUTOBUILD_%s_%s_BARS_LEFT" % (mod.upper(), word(count))
    if base not in known:
        return base
    for k in range(2, 20):
        cand = "%s_RUN_%s" % (base, ONES[k])
        if cand not in known:
            return cand
    return None


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
            f["dead_unfinished"] = [r["unit"] for r in runs if r.get("unit") and not r.get("live") and r.get("end") is None]
        else:
            f["live_units"] = UNM
        out[mod] = add_ingame(root, mod, add_blind(root, mod, f, runs if isinstance(runs, list) else []),
                              runs if isinstance(runs, list) else [])
        out[mod]["killed"] = killed_runs(runs if isinstance(runs, list) else [])
    return out


def killed_runs(runs, read=None, runner=subprocess.run):
    """-> {unit: {why, state, returned, return_going, kept}} for the ended blind and in-game runs that were KILLED before
    they wrote a result (detached_helper.killed), read from their run records."""
    import role_launch as RL
    read = read or DH.read_record
    out = {}
    for r in runs or []:
        u = r.get("unit")
        if not u or r.get("live") or not ("BLIND" in str(r.get("item") or "").upper() or _is_ingame_item(r.get("item"))):
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


def add_ingame(root, mod, f, runs):
    """ingame_live (every mod): the live runs whose item names an in-game run (_is_ingame_item), for the one-driver rule.
    At in-game acceptance also maturation.ingame_facts (visit, exit reading, owed) and ingame_runs, the in-game runs
    started since the visit opened (10 min of slack, as for the blind challenge)."""
    f["ingame_live"] = [r.get("unit") for r in runs or [] if r.get("live") and _is_ingame_item(r.get("item"))]
    if f.get("stage") != "in_game":
        return f
    f.update(M.ingame_facts(root, mod))
    t0 = _ts(f.get("opened"))
    f["ingame_runs"] = [r.get("unit") for r in runs or [] if _is_ingame_item(r.get("item"))
                        and isinstance(r.get("at"), (int, float)) and t0 is not None and r["at"] >= t0 - 600]
    return f


def add_blind(root, mod, f, runs):
    """At the blind challenge: maturation.blind_facts (cycle, visit, exit reading, owed) and blind_runs, the runs whose
    item names a blind run (BLIND in it) that started since the cycle opened (10 min of slack for a launch that beat
    its own advance to origin/main). Any other stage: f unchanged."""
    if f.get("stage") != "blind_challenge":
        return f
    f.update(M.blind_facts(root, mod))
    t0 = _ts(f.get("opened"))
    f["blind_runs"] = [r.get("unit") for r in runs or [] if "BLIND" in str(r.get("item") or "").upper()
                       and isinstance(r.get("at"), (int, float)) and t0 is not None and r["at"] >= t0 - 600]
    return f


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
        return "USD %.2f spent at %s, at or past the %g ceiling" % (usd, where, ceiling)
    if usd + cap > ceiling:
        return "USD %.2f spent at %s plus the next run's USD %g cap passes the %g ceiling" % (usd, where, cap, ceiling)
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
    return ('python3 src/RimMandrake/rimflow/maturation_dispatch.py release %s --stage %s --read-usd %.2f --usd %d '
            '--why "..."' % (mod, stage, usd, need))


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
        notes.append("a release read USD %.2f, the spend is now USD %.2f" % (stale[-1]["read_usd"], usd))
    if len(fresh) > len(stale):
        notes.append("a release of USD %g does not cover the next run's cap" % [r for r in fresh if r not in stale][-1]
                     ["release_usd"])
    if bad:
        notes.append("%d malformed release line(s) ignored" % bad)
    return "%s%s; release it: %s" % (over, " (%s)" % "; ".join(notes) if notes else "",
                                     release_cmd(mod, stage, usd, cap, ceiling)), None


def stage_spent(f, stage, ours):
    """-> USD spent at this stage: every run the status page placed in its box (measured dollars, else its cap), plus
    this step's own launches there not yet placed (at their cap)."""
    spent = dict((f.get("box_runs") or {}).get(M.COL[stage]) or {})
    for x in ours or []:
        if x.get("unit") and x["unit"] not in spent:
            spent[x["unit"]] = (f.get("run_usd") or {}).get(x["unit"], x.get("cap") or 0.0)
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
        return None, "; the killed run %s spent USD %.2f, less than the USD %.2f missing" % (unit, spent, need)
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
                      "failed run); USD %.2f of the USD %.2f charged for it is given back once so the same %s can "
                      "finish; the stage's convergence reads %s (the Conductor's rule of 2026-11-15, "
                      "RIMMANDRAKE_REFUND_KILLED_RUN_DOLLARS_AT_THE_CEILING)" % (
                          ref["unit"], ref["usd"], ref["spent"],
                          "cycle" if ref["stage"] == "blind_challenge" else "visit", ref["word"])}
        rec["id"] = "rel-%s" % hashlib.sha1(json.dumps(rec, sort_keys=True).encode()).hexdigest()[:12]
        with open(path or releases_path(), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
        s = st["mods"][r["mod"]]
        s.setdefault("releases_used", {})[rec["id"]] = {"at": now, "stage": ref["stage"], "usd": ref["read_usd"],
                                                         "unit": r.get("unit")}
        s.setdefault("refunds", {})[ref["unit"]] = {"at": now, "usd": rec["release_usd"], "release": rec["id"]}
        r["why"] = "%s; killed-run refund %s (USD %.2f)" % (r.get("why"), rec["id"], rec["release_usd"])
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
    drivers = [u for f in facts.values() for u in (f.get("ingame_live") or [])]
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
                live_total += 1
                launches.append(mod)
            continue
        if f.get("stage") == "in_game":
            s.pop("owed_since", None)
            s.pop("watch", None)
            if decide_ingame(cfg, s, f, row, put, now, account, live_total, drivers, bridge, releases):
                live_total += 1
                drivers.append("(this tick: %s)" % mod)
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
        spent = dict(f.get("stage_runs") or {})
        for x in s.get("launches") or []:
            if x.get("stage") == "offline_build" and x.get("unit") not in spent:
                spent[x["unit"]] = (f.get("run_usd") or {}).get(x["unit"], x.get("cap") or 0.0)
        usd = round(sum(spent.values()), 2)
        row["stage_usd"] = usd
        over, rid = ceiling_gate(cfg, s, mod, "offline_build", usd, cap if cap_ok else 0, "the offline build", releases)
        stop = s.get("stopped")
        if stop and (stop.get("ceiling") or "ceiling" in str(stop.get("why"))) and rid:
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
        put("launch", "%d bars refused as build work, nothing live on it (%s)" % (n, account[1]))
        launches.append(mod)
    return rows, launches


def retriable(cfg, x, killed=None):
    """-> True when a blind or in-game book entry is a launch that NEVER STARTED on a transient fault (a git lock, its
    item not yet on origin/main: maturation_autonomy.transient) with tries left (launch_tries, 3). Such a launch judged
    nothing, so it is not the visit's automatic run; one that started, or failed any other way, is
    (RIMMANDRAKE_RETRY_JUDGE_LAUNCH_GIT_LOCK_SPENT_THE_CYCLE). An older entry without tries reads as its first try.
    killed ({unit: ...}, killed_runs): a run that started and was KILLED before it wrote a result is retried the same
    way (RIMMANDRAKE_RETRY_RUN_KILLED_BY_ACCOUNT_SWITCH_CYCLE_KEPT); one that ended by itself with no record is not."""
    if not isinstance(x, dict) or int(x.get("tries") or 1) >= int(cfg.get("launch_tries", 3)):
        return False
    if x.get("unit"):
        return not x.get("failed") and x["unit"] in (killed or {})
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
        int(retry.get("tries") or 1) + 1, int(cfg.get("launch_tries", 3)),
        "a run killed before it wrote a result (%s)" % retry["unit"] if retry.get("unit")
        else "a failed launch, the pipeline's code having changed since" if code_changed(cfg, retry)
        and not AUT.transient(str(retry.get("failed") or ""))
        else "a launch that never started on a transient fault")) if retry else ""


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
    if len([x for x in ours if x is not retry]) >= per:
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


def decide_ingame(cfg, s, f, row, put, now, account, live_total, drivers, bridge, releases=None):
    """One decision for an advancing mod at in-game acceptance -> True to launch its live driver. At most
    ingame_auto_runs_per_visit (1) automatic runs per visit (keyed by the version and the visit number), one live-game
    driver at a time across all mods (drivers: the live in-game runs), only when the bridge is takeable, and only with
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
            "in-game visit %s: exit met (a program's reading of %s); the steward reads it and confirms: maturation.py "
            "advance %s --to pre_human --steward-confirms \"...\" (a Conductor step; the program never advances)"
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
    if drivers:
        put("driver_busy", "an in-game run is live (%s): one live-game driver at a time across all mods" % (
            ", ".join(drivers)))
        return False
    if no_slot(cfg, live_total, put):
        return False
    go, why = (bridge or (lambda p: M.bridge_idle(p, cfg.get("seat", "BENCH"))))(
        "%s in-game acceptance visit %s" % (mod, n))
    if not go:
        put("bridge_held", "the bridge is not takeable: %s" % why)
        return False
    row.update(cap=cap, visit_id=vid)
    if retry:
        row["retry_of"] = dict(retry)
    put("launch", "in-game visit %s owed, nothing live or recorded on it, the visit's automatic run%s, bridge %s (%s)" % (
        n, retried(cfg, retry), why, account[1]))
    return True


def ingame_item_id(mod, visit, known):
    """-> a rimflow name for the live driver's item: RIMMANDRAKE_DRIVE_<MOD>_IN_GAME_ACCEPTANCE_VISIT_<N> (64 at most)."""
    base = "RIMMANDRAKE_DRIVE_%s_IN_GAME_ACCEPTANCE_VISIT_%s" % (mod.upper(), word(visit or 0))
    if len(base) > 64:
        base = "RIMMANDRAKE_DRIVE_%s_IN_GAME_VISIT_%s" % (mod.upper(), word(visit or 0))
    if base not in known:
        return base
    for k in range(2, 20):
        cand = "%s_RUN_%s" % (base, ONES[k])
        if cand not in known and len(cand) <= 64:
            return cand
    return None


def blind_item_id(mod, cycle, known):
    """-> a rimflow name for the judge's item: RIMMANDRAKE_JUDGE_<MOD>_BLIND_CYCLE_<N>_TESTS_FIRST (64 chars at most)."""
    base = "RIMMANDRAKE_JUDGE_%s_BLIND_CYCLE_%s_TESTS_FIRST" % (mod.upper(), word(cycle or 0))
    if len(base) > 64:
        base = "RIMMANDRAKE_JUDGE_%s_BLIND_CYCLE_%s" % (mod.upper(), word(cycle or 0))
    if base not in known:
        return base
    for k in range(2, 20):
        cand = "%s_RUN_%s" % (base, ONES[k])
        if cand not in known and len(cand) <= 64:
            return cand
    return None


# ---- the acts -------------------------------------------------------------------------------------------------------

def _ingest():
    import importlib.util
    path = os.path.join(REPO, "src", "RimMandrake", "Utils", "testq", "ingest.py")
    spec = importlib.util.spec_from_file_location("maturation_dispatch_ingest", path)
    ing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ing)
    return ing


def file_and_publish(item, title, why, needs="offline"):
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
                              "--title", title, "--why", why)
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
        if retry.get("unit"):
            entry["killed_before"] = list(retry.get("killed_before") or []) + [retry["unit"]]
        lst[:] = [x for x in lst if (x.get("unit") and x.get("unit") != retry.get("unit"))
                  or any(x.get(k) != v for k, v in where.items())]
    lst.append(entry)
    return ok, item, unit, text, entry


def execute(root, cfg, st, rows, launches, now, fx=None):
    fx = fx or {}
    do_file = fx.get("file", file_and_publish)
    do_publish = fx.get("publish", publish_filed)
    do_launch = fx.get("launch", lambda mod, cap, item, **kw: M.launch_mod(
        root, mod, cap, item, seat=cfg.get("seat", "BENCH"),
        model=cfg.get("ingame_model", "opus") if (M.load(root, mod) or {}).get("stage") == "in_game"
        else cfg.get("model", "opus"), **kw))
    known = fx["known"]() if "known" in fx else known_items()
    done = []
    for row in rows:
        if row["mod"] not in launches:
            continue
        mod, s = row["mod"], st["mods"][row["mod"]]
        blind = row.get("stage") == "blind_challenge"
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
                lambda it: do_launch(mod, row["cap"], it, **resume_kw(row)))
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
            title = ("%s Stage 3: build the checks for the %d bars not runnable, offline (launched by the Dispatch step)"
                     % (mod, row["refused"]))
            why = ("delegated: maturation_dispatch.py; maturation.py refuses %d bars as build work (%s), nothing live on "
                   "it, measured %s" % (row["refused"], ", ".join(row["refused_ids"][:12]), pac(now)))
        if blind:
            # launched or failed, it is the visit's automatic cycle (the owner's condition), unless it never started on
            # a transient fault: then the next tick tries the same item again, up to launch_tries
            ok, item, unit, text, entry = launch_counted(
                cfg, s, row, now, "blind_auto", {"visit_id": row.get("visit_id"), "cycle": row.get("cycle")},
                lambda: item, lambda it: do_file(it, title, why), do_publish,
                lambda it: do_launch(mod, row["cap"], it, **resume_kw(row)))
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
            rc, text2, unit = do_launch(mod, cfg["cap_usd"], item)
            text = "%s; %s" % (text, text2.splitlines()[0] if text2 else rc)
            ok = rc == 0 and bool(unit)
        else:
            unit = None
        if ok:
            s.setdefault("launches", []).append({"unit": unit, "item": item, "at": now, "refused": row["refused"],
                                                 "ids": row["refused_ids"], "cap": cfg["cap_usd"],
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
    if "BLIND" in str(r.get("item") or "").upper():
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
    r = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=120)
    if r.returncode != 0 or os.path.realpath(r.stdout.strip()) != os.path.realpath(root):
        return "skipped: %s is not a clone's top" % root
    import designer_stage as DS
    p = subprocess.run([DS.LAND, "-m", "maturation: spend rows of ended runs (Dispatch step)"] + paths, cwd=root,
                       capture_output=True, text=True, timeout=300, env=dict(os.environ, LAND_REPO=root))
    if p.returncode and "nothing to land" not in p.stderr:
        return "land.sh exited %d: %s" % (p.returncode, p.stderr.strip()[-300:])
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
            and r.get("decision") not in ("launched",)]
    mx = max([r.get("idle_min") or 0 for r in owed] or [0])
    over = [r["mod"] for r in owed if (r.get("idle_min") or 0) > cfg.get("idle_alarm_min", 60)]
    return {"schema": 1, "at": now, "at_pac": pac(now), "enabled": bool(cfg.get("enabled")),
            "idle_owed_max_min": mx, "idle_owed_mods": over, "idle_alarm_min": cfg.get("idle_alarm_min", 60),
            "launched": [{"mod": r["mod"], "unit": r.get("unit"), "item": r.get("item")} for r in rows
                         if r.get("decision") == "launched"],
            "needs_conductor": [r["need"] for r in rows if r.get("need")],
            "mods": {r["mod"]: {k: r.get(k) for k in ("decision", "why", "stage", "owed", "refused", "live",
                                                       "idle_min", "stage_usd", "cycle", "visit", "exit",
                                                       "stop_lifted")} for r in rows}}


CLONE_FETCH_S = 30          # the tick's fetch of its own clone
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
                    "has no reflog" if age is None else "unmoved for %d min" % (age // 60), got.stderr.strip()[-160:])
        r = git("rev-list", "--left-right", "--count", "HEAD...origin/main")
    except (OSError, subprocess.SubprocessError) as e:
        return None, "clone unreadable: %s" % e
    n = r.stdout.split()
    if r.returncode or len(n) != 2:
        return None, "clone unreadable: %s" % (r.stderr.strip()[-160:] or r.stdout.strip())
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
            out.append("%s: %s" % (k, "; ".join(rd[k])[:600]))
    return out


def _aut(rows, mod):
    return any(r["mod"] == mod and r.get("aut") for r in rows)


def tick(root, cfg, apply, fx=None, now=None, page=True):
    fx = fx or {}
    now = now or time.time()
    d = sdir()
    st = _read(os.path.join(d, "state.json"), {})
    aut = fx.get("autonomy", True)      # False: the per-stage decision alone (selftest_maturation_dispatch's layer)
    shipped = cfg                       # the file's own values, before widen adds discovered mods (maturation_hands)
    cfg = AUT.widen(root, cfg, st, apply, fx) if aut else cfg   # Designer concepts seen and seeded; the game queue
    cfg = dict(cfg, _code=(fx["code"]() if "code" in fx else pipeline_code(REPO)))   # the code this tick runs
    facts = fx["facts"]() if "facts" in fx else gather(root, cfg)
    account = fx["account"]() if "account" in fx else account_gate()
    releases = fx["releases"]() if "releases" in fx else read_releases()
    rows, launches = decide(cfg, st, facts, now, account, bridge=fx.get("bridge"), releases=releases)
    if aut:
        rows, launches = AUT.resolve(root, cfg, st, facts, rows, launches, now, fx)
    if not cfg.get("enabled"):
        for r in rows:
            if r["mod"] in launches:
                r.update(decision="disabled", why="the step is disabled in maturation_dispatch.json")
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
        rd["convergence_error"] = "%s: %s" % (e.__class__.__name__, str(e)[:120])
    for mod, c in (rd.get("convergence") or {}).items():    # the next tick's refund rule reads the word per stage
        if mod in st.get("mods", {}) and isinstance(c, dict):
            st["mods"][mod]["convergence"] = {k: (v or {}).get("verdict") for k, v in c.items()}
    if apply:
        rd["clone"] = clone_reading(st, now, (fx.get("clone") or (lambda: clone_counts(root)))())
        rd["spend_rows"] = record_spend(root, facts, fx)
        if aut:
            rd["chores"] = slow_chores(st, facts, now, fx)
        try:        # every hand act on the pipeline, recorded; one left a day with no follow-up alarms
            import maturation_hands as MH       # noqa: E402
            MH.observe(root, shipped, st, facts, now, rd, fx.get("hands"))
        except Exception as e:      # noqa: BLE001  this reading failing never costs the tick
            rd["hand_acts_error"] = "%s: %s" % (e.__class__.__name__, e)
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
    r.add_argument("--read-usd", type=float, required=True, help="the stage's spend you read (the pause line's USD)")
    r.add_argument("--usd", type=float, required=True, help="dollars released past the ceiling, for one more run")
    r.add_argument("--why", required=True)
    r.add_argument("--by", default=None, help="who releases (default: this window's seat)")
    sub.add_parser("releases", help="every ceiling release with its spend, amount and why, and whether a launch spent it")
    o = ap.parse_args(argv)
    cfg = load_cfg()
    if o.cmd == "tick":
        rd = tick(os.path.abspath(o.root), cfg, o.apply, page=not o.no_page)
        for mod, r in rd["mods"].items():
            print("%-20s %-7s %-13s %s" % (mod, r.get("klass"), r["decision"], r.get("status") or r["why"]))
        print("idle owed max %s min%s; launched %d; page %s" % (
            rd["idle_owed_max_min"], (" (over %s: %s)" % (rd["idle_alarm_min"], ", ".join(rd["idle_owed_mods"])))
            if rd["idle_owed_mods"] else "", len(rd["launched"]), rd.get("page", "not regenerated")))
        return 0
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
        print("RELEASED %s at %s by USD %g (read USD %.2f, by %s; %s): the next tick may launch on it once%s" % (
            o.mod, o.stage, o.usd, o.read_usd, by, rec["id"],
            "" if seen is None or abs(seen - o.read_usd) <= READ_SLACK else
            "; WARNING the last reading shows USD %.2f there, so this release reads stale and frees nothing" % seen))
        print(HAND_NOTE % rec["id"])
        return 0
    if o.cmd == "releases":
        recs, bad = read_releases()
        st = _read(os.path.join(sdir(), "state.json"), {})
        for r in recs:
            u = ((st.get("mods") or {}).get(r["mod"]) or {}).get("releases_used", {}).get(r["id"])
            print("%s %s %-18s %-15s read USD %.2f, released USD %g, by %s: %s [%s]" % (
                r["ts"], r["id"], r["mod"], r["stage"], r["read_usd"], r["release_usd"], r["by"], r["why"],
                "spent by %s" % (u.get("unit") or "a launch") if u else "unspent"))
        print("%d release(s), %d malformed line(s) in %s" % (len(recs), bad, releases_path()))
        return 0
    if o.cmd == "clear":
        p = os.path.join(sdir(), "state.json")
        st = _read(p, {})
        s = (st.get("mods") or {}).get(o.mod) or {}
        was = s.pop("stopped", None)
        # a steward or fixer key that never launched, or ended outside an open road back, is released: the next tick
        # may run it once more (RIMMANDRAKE_RETRY_STEWARD_LAUNCH_GIT_LOCK_COUNTED_AS_SPENT: clear left those spent)
        released = {}
        for book in ("steward", "fixers"):
            for k, x in list((s.get(book) or {}).items()):
                if AUT.releasable(s, k, x):
                    released.setdefault(book, {})[k] = s[book].pop(k)
        # so is a blind or in-game launch that never started (refused at the spawn, say): it judged nothing, and left
        # in its book it stops the next tick again (RIMMANDRAKE_ADMIT_INGAME_SPAWN_RUNNER_REFUSES_GAME_UP); a run that
        # started stays the visit's automatic run
        for book in ("blind_auto", "ingame_auto"):
            gone = [x for x in s.get(book) or [] if isinstance(x, dict) and x.get("failed") and not x.get("unit")]
            if gone:
                s[book] = [x for x in s[book] if not any(x is g for g in gone)]
                released[book] = gone
        s.setdefault("cleared", []).append({"at": time.time(), "why": o.why, "was": was, "released": released})
        st.setdefault("mods", {})[o.mod] = s
        _write(p, st)
        print("CLEARED %s (was: %s; released %d steward, %d fixer key(s), %d never-started blind/in-game launch(es))" % (
            o.mod, (was or {}).get("why", "not stopped"), len(released.get("steward") or {}),
            len(released.get("fixers") or {}), len(released.get("blind_auto") or []) + len(released.get("ingame_auto") or [])))
        print(HAND_NOTE % ("clear-%s-%d" % (o.mod, s["cleared"][-1]["at"])))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
