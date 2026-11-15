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

Runs on rm-maturation-dispatch.timer (every 60 s, from the dispatch clone); its own timer, not the Dispatcher's tick,
so a slow ledger read never cuts a Dispatcher beat. Settings: maturation_dispatch.json beside this file.

Per mod on the advancing list, in order, one decision:
  not_offline   the mod's record is at neither the offline build nor the blind challenge (no record, the Designer, any
                later stage): nothing; the Designer stays his and the stages after the blind challenge are hand steps
  live          a detached run is live on the mod (maturation_now maps runs to mods by item id): nothing; the run is
                watched, and its refused count when first seen is kept
  stopped       the last run on the mod ended and the count of refused bars did NOT fall, or the mod's dollars at the
                stage passed stage_ceiling_usd, or a launch failed: nothing, and one "Needs Conductor" line. It stays
                stopped while the refused set is the one it stopped on (never a second automatic try at the same
                refusals); `clear` or a change to the refused set by someone else lifts it
  held | blocked a Conductor hold or another non-build refusal (a version mismatch): nothing
  hand_step     only hand steps are left (a steward confirmation): a "Needs Conductor" line
  ready         every exit test passes: "ready to advance" for the Conductor; the program never advances
  blind         the run records or the test table cannot be read: nothing (never launch on a blind reading)
  no_cap        the settings have no positive cap_usd: nothing launches anywhere
  slots_unknown an advancing mod's live runs cannot be read: no launch anywhere (an unknown occupancy is never 0)
  ceiling       blind or in-game: the stage's dollars plus the run's cap pass stage_ceiling_usd (the cap is reserved)
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

UNM = "UNMEASURED"
CFG_PATH = os.path.join(HERE, "maturation_dispatch.json")
ALARM_NAME = "OPS_MATURATION_IDLE_ADVANCING_MOD"
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
        else:
            f["live_units"] = UNM
        out[mod] = add_ingame(root, mod, add_blind(root, mod, f, runs if isinstance(runs, list) else []),
                              runs if isinstance(runs, list) else [])
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


def stage_spent(f, stage, ours):
    """-> USD spent at this stage: every run the status page placed in its box (measured dollars, else its cap), plus
    this step's own launches there not yet placed (at their cap)."""
    spent = dict((f.get("box_runs") or {}).get(M.COL[stage]) or {})
    for x in ours or []:
        if x.get("unit") and x["unit"] not in spent:
            spent[x["unit"]] = (f.get("run_usd") or {}).get(x["unit"], x.get("cap") or 0.0)
    return round(sum(spent.values()), 2)


def reserve_refused(cfg, f, row, put, cap, stage, ours):
    """The ceiling at the blind challenge and in-game acceptance, as at the offline build: True (the row put) when the
    stage's spend plus this run's cap passes stage_ceiling_usd. Read every tick, never stored: raising the ceiling or a
    Conductor's word on the spend lifts it."""
    usd = stage_spent(f, stage, ours)
    row["stage_usd"] = usd
    over = over_ceiling(usd, cap, cfg.get("stage_ceiling_usd"), M.label(stage))
    if over:
        put("ceiling", over, "the ceiling, %s; nothing more launches on it until the Conductor reads the spend" % over)
        return True
    return False


def decide(cfg, st, facts, now, account=(True, ""), bridge=None):
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

        if f.get("stage") == "blind_challenge":
            s.pop("owed_since", None)
            s.pop("watch", None)
            if decide_blind(cfg, s, f, row, put, now, account, live_total):
                live_total += 1
                launches.append(mod)
            continue
        if f.get("stage") == "in_game":
            s.pop("owed_since", None)
            s.pop("watch", None)
            if decide_ingame(cfg, s, f, row, put, now, account, live_total, drivers, bridge):
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
            prog, pwhy = progressed(w, ids, f.get("bar_fp"))
            if not prog:
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
        stop = s.get("stopped")
        # a stop lifts only when refused bars were resolved (the set shrank); a renamed id is not a resolution
        if stop and not (isinstance(ids, list) and isinstance(stop.get("ids"), list)
                         and set(ids) < set(stop["ids"])):
            put("stopped", stop.get("why"), "stopped, %s; never a second automatic try at the same refusals "
                "(`maturation_dispatch.py clear %s --why ...` lifts it)" % (stop.get("why"), mod))
            continue
        if stop:
            s.pop("stopped")
            row["stop_lifted"] = "the refused set changed since the stop (%s)" % stop.get("why")
        spent = dict(f.get("stage_runs") or {})
        for x in s.get("launches") or []:
            if x.get("stage") == "offline_build" and x.get("unit") not in spent:
                spent[x["unit"]] = (f.get("run_usd") or {}).get(x["unit"], x.get("cap") or 0.0)
        usd = round(sum(spent.values()), 2)
        row["stage_usd"] = usd
        ceiling = cfg.get("stage_ceiling_usd")
        over = over_ceiling(usd, cap if cap_ok else 0, ceiling, "the offline build")
        if over:
            s["stopped"] = {"ids": ids, "at": now, "why": over}
            put("stopped", s["stopped"]["why"], "stopped, %s" % s["stopped"]["why"])
            continue
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


def decide_blind(cfg, s, f, row, put, now, account, live_total):
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
    if owed == "no exit block":
        put("cycle_unfinished", "nothing is live and %s has no exit block" % summ,
            "blind cycle %s has a record (%s) with no exit block and nothing live on it; nothing launches: the "
            "Conductor reads it" % (n, summ))
        return False
    if owed != "cycle":
        put("blind", "the blind challenge's state cannot be read (%s)" % owed,
            "the blind challenge's state cannot be read (%s); nothing launches" % owed)
        return False
    mine = [x for x in ours if x.get("cycle") == n]
    if mine:
        x = mine[-1]
        why = ("the automatic launch of cycle %s failed: %s" % (n, x.get("failed")) if x.get("failed") else
               "the automatic cycle %s (%s) ended and wrote no record" % (n, x.get("unit")))
        put("stopped", why, "stopped, %s; never a second automatic try" % why)
        return False
    per = int(cfg.get("blind_auto_cycles_per_visit", 1))
    if len(ours) >= per:
        put("auto_spent", "the visit's %d automatic cycle(s) are spent (cycle %s)" % (
            per, ", ".join(str(x.get("cycle")) for x in ours)),
            "blind cycle %s is open; the Dispatch step runs %d automatic cycle(s) per visit (cycle %s was), so launch "
            "it by hand: maturation.py launch %s --budget-usd <cap> --item <ID>" % (
                n, per, ", ".join(str(x.get("cycle")) for x in ours), mod))
        return False
    if f.get("blind_runs"):
        put("hand_run_seen", "blind run(s) %s worked on cycle %s and wrote no cycle_%s folder" % (
            ", ".join(f["blind_runs"]), n, n),
            "blind run(s) %s worked on cycle %s since it opened and wrote no record; nothing launches: the Conductor "
            "reads what it left" % (", ".join(f["blind_runs"]), n))
        return False
    if not cfg.get("blind_enabled"):
        put("blind_off", "blind_enabled is off in maturation_dispatch.json",
            "blind cycle %s is owed with nothing live; the Dispatch step's blind launches are off" % n)
        return False
    cap = cfg.get("blind_cap_usd")
    if not (isinstance(cap, (int, float)) and not isinstance(cap, bool) and cap > 0):
        put("no_cap", "the settings have no positive blind_cap_usd; no judge launches without a cap")
        return False
    if reserve_refused(cfg, f, row, put, cap, "blind_challenge", s.get("blind_auto")):
        return False
    if not account[0]:
        put("account_hold", account[1])
        return False
    if no_slot(cfg, live_total, put):
        return False
    row.update(cap=cap, visit_id=vid)
    put("launch", "blind cycle %s owed, nothing live or recorded on it, the visit's first automatic cycle (%s)" % (
        n, account[1]))
    return True


def decide_ingame(cfg, s, f, row, put, now, account, live_total, drivers, bridge):
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
    if owed == "no exit block":
        put("visit_unfinished", "nothing is live and %s has no exit block" % summ,
            "in-game visit %s has a record (%s) with no exit block and nothing live on it; nothing launches: the "
            "Conductor reads it (and checks the game was left closed or healthy)" % (n, summ))
        return False
    if owed != "run":
        put("blind", "in-game acceptance's state cannot be read (%s)" % owed,
            "in-game acceptance's state cannot be read (%s); nothing launches" % owed)
        return False
    mine = [x for x in ours if x.get("visit") == n]
    if mine:
        x = mine[-1]
        why = ("the automatic launch of in-game visit %s failed: %s" % (n, x.get("failed")) if x.get("failed") else
               "the automatic in-game visit %s (%s) ended and wrote no record" % (n, x.get("unit")))
        put("stopped", why, "stopped, %s; never a second automatic try" % why)
        return False
    per = int(cfg.get("ingame_auto_runs_per_visit", 1))
    if len(ours) >= per:
        put("auto_spent", "the visit's %d automatic run(s) are spent" % per,
            "in-game visit %s is open and its automatic run is spent; launch it by hand: maturation.py launch %s "
            "--budget-usd <cap> --item <ID>" % (n, mod))
        return False
    if f.get("ingame_runs"):
        put("hand_run_seen", "in-game run(s) %s worked on visit %s and wrote no visit_%s folder" % (
            ", ".join(f["ingame_runs"]), n, n),
            "in-game run(s) %s worked on visit %s since it opened and wrote no record; nothing launches: the Conductor "
            "reads what it left (and checks the game was left closed or healthy)" % (", ".join(f["ingame_runs"]), n))
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
    if reserve_refused(cfg, f, row, put, cap, "in_game", s.get("ingame_auto")):
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
    put("launch", "in-game visit %s owed, nothing live or recorded on it, the visit's automatic run, bridge %s (%s)" % (
        n, why, account[1]))
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


def execute(root, cfg, st, rows, launches, now, fx=None):
    fx = fx or {}
    do_file = fx.get("file", file_and_publish)
    do_launch = fx.get("launch", lambda mod, cap, item: M.launch_mod(
        root, mod, cap, item, seat=cfg.get("seat", "BENCH"),
        model=cfg.get("ingame_model", "opus") if (M.load(root, mod) or {}).get("stage") == "in_game"
        else cfg.get("model", "opus")))
    known = fx["known"]() if "known" in fx else known_items()
    done = []
    for row in rows:
        if row["mod"] not in launches:
            continue
        mod, s = row["mod"], st["mods"][row["mod"]]
        blind = row.get("stage") == "blind_challenge"
        if row.get("stage") == "in_game":
            item = ingame_item_id(mod, row.get("visit"), known)
            title = ("%s Stage 6: in-game acceptance visit %s, one live driver on the bridge (launched by the Dispatch "
                     "step)" % (mod, row.get("visit")))
            why = ("delegated: maturation_dispatch.py; in-game visit %s is owed (no visit_%s folder), nothing live or "
                   "recorded on it, no other live-game driver, the bridge takeable, measured %s" % (
                       row.get("visit"), row.get("visit"), pac(now)))
            ok, text = do_file(item, title, why, needs="game-up") if item else (False, "no free item name")
            unit = None
            if ok:
                rc, text2, unit = do_launch(mod, row["cap"], item)
                text = "%s; %s" % (text, text2.splitlines()[0] if text2 else rc)
                ok = rc == 0 and bool(unit)
            # launched or failed, it is the visit's automatic run: never a second try (the owner's condition)
            s.setdefault("ingame_auto", []).append({"visit_id": row.get("visit_id"), "visit": row.get("visit"),
                                                    "unit": unit if ok else None, "item": item, "at": now,
                                                    "cap": row.get("cap"), "failed": None if ok else text})
            if ok:
                row.update(decision="launched", unit=unit, item=item, why=text)
                known.add(item) if isinstance(known, set) else None
                done.append(row)
            else:
                row.update(decision="launch_failed", why=text,
                           need="%s: the in-game launch failed (%s); the step will not retry it on its own" % (mod, text))
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
        ok, text = do_file(item, title, why) if item else (False, "no free item name")
        if ok:
            rc, text2, unit = do_launch(mod, row["cap"] if blind else cfg["cap_usd"], item)
            text = "%s; %s" % (text, text2.splitlines()[0] if text2 else rc)
            ok = rc == 0 and bool(unit)
        else:
            unit = None
        if blind:
            # launched or failed, it is the visit's automatic cycle: never a second try (the owner's condition)
            s.setdefault("blind_auto", []).append({"visit_id": row.get("visit_id"), "cycle": row.get("cycle"),
                                                   "unit": unit if ok else None, "item": item, "at": now,
                                                   "cap": row.get("cap"), "failed": None if ok else text})
            if ok:
                row.update(decision="launched", unit=unit, item=item, why=text)
                known.add(item) if isinstance(known, set) else None
                done.append(row)
            else:
                row.update(decision="launch_failed", why=text,
                           need="%s: the blind launch failed (%s); the step will not retry it on its own" % (mod, text))
            continue
        if ok:
            s.setdefault("launches", []).append({"unit": unit, "item": item, "at": now, "refused": row["refused"],
                                                 "ids": row["refused_ids"], "cap": cfg["cap_usd"],
                                                 "stage": "offline_build"})
            s["watch"] = {"unit": unit, "refused": row["refused"], "ids": row["refused_ids"], "at": now, "ours": True,
                          "fp": row.get("bar_fp")}
            s.pop("owed_since", None)
            row.update(decision="launched", unit=unit, item=item, why=text)
            known.add(item) if isinstance(known, set) else None
            done.append(row)
        else:
            s["stopped"] = {"ids": row["refused_ids"], "at": now, "why": "the launch failed: %s" % text}
            row.update(decision="launch_failed", why=text,
                       need="%s: the launch failed (%s); the step will not retry it on its own" % (mod, text))
    return done


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
                                                       "idle_min", "stage_usd", "cycle", "visit", "exit")} for r in rows}}


def _aut(rows, mod):
    return any(r["mod"] == mod and r.get("aut") for r in rows)


def tick(root, cfg, apply, fx=None, now=None, page=True):
    fx = fx or {}
    now = now or time.time()
    d = sdir()
    st = _read(os.path.join(d, "state.json"), {})
    aut = fx.get("autonomy", True)      # False: the per-stage decision alone (selftest_maturation_dispatch's layer)
    cfg = AUT.widen(root, cfg, st, apply, fx) if aut else cfg   # Designer concepts seen and seeded; the game queue
    facts = fx["facts"]() if "facts" in fx else gather(root, cfg)
    account = fx["account"]() if "account" in fx else account_gate()
    rows, launches = decide(cfg, st, facts, now, account, bridge=fx.get("bridge"))
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
    execute(root, cfg, st, rows, [m for m in launches if not _aut(rows, m)], now, fx)
    AUT.execute(root, cfg, st, rows, [m for m in launches if _aut(rows, m)], now, fx)
    AUT.classify(cfg, st, rows, now)
    if apply and aut:
        AUT.post_cards(rows, st, now, fx)
    rd = AUT.annotate(reading(cfg, rows, now), rows)
    if apply:
        rd["spend_rows"] = record_spend(root, facts, fx)
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
        print("reading at %s" % rd["at_pac"])
        for mod, r in rd["mods"].items():
            print("%-20s %-7s %-13s %s (%s min)" % (mod, r.get("klass"), r["decision"], r.get("status") or r["why"],
                                                   r.get("for_min", "?")))
        for k in ("paused", "owner", "stalled"):
            if rd.get(k):
                print("%s: %s" % (k, "; ".join(rd[k])[:600]))
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
        s.setdefault("cleared", []).append({"at": time.time(), "why": o.why, "was": was, "released": released})
        st.setdefault("mods", {})[o.mod] = s
        _write(p, st)
        print("CLEARED %s (was: %s; released %d steward, %d fixer key(s))" % (
            o.mod, (was or {}).get("why", "not stopped"), len(released.get("steward") or {}),
            len(released.get("fixers") or {})))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
