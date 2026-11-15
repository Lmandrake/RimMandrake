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
  not_offline   the mod's record is not at the offline build (no record, the Designer, any later stage): nothing; the
                Designer stays his and later stages are hand steps (plan §3: the blind challenge onward is not built)
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
  slots_full    max_live live runs on advancing mods already (the Conductor's included)
  account_hold  the Dispatcher's account pick holds role launches (its rule's `hold` list): nothing
  launch        spawn a ledger item under this one (seat RUNNER, as ops_watch files), publish the shard, `maturation.py launch` it (opus, the cap)
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
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import maturation as M          # noqa: E402
import maturation_now as MN     # noqa: E402

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
            f["run_usd"] = {r["unit"]: (r["usd"] if isinstance(r.get("usd"), (int, float)) else
                                        r.get("cap") if isinstance(r.get("cap"), (int, float)) else 0.0)
                            for r in runs if r.get("unit")}
        else:
            f["live_units"] = UNM
        out[mod] = f
    return out


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

def decide(cfg, st, facts, now, account=(True, "")):
    """-> (rows, launches). Pure over (cfg, st, facts): it mutates st (watch, stop, owed_since) and returns one row per
    advancing mod and the mods to launch, in list order. Never launches on a mod twice in one tick."""
    rows, launches = [], []
    cap = cfg.get("cap_usd")
    cap_ok = isinstance(cap, (int, float)) and not isinstance(cap, bool) and cap > 0
    mods = st.setdefault("mods", {})
    live_total = sum(len(f["live_units"]) for f in facts.values() if isinstance(f.get("live_units"), list))
    for mod in cfg.get("advancing") or []:
        f = facts.get(mod) or {"stage": UNM}
        s = mods.setdefault(mod, {})
        ids = M.refused_ids(f) if f.get("stage") == "offline_build" else None
        n = len(ids) if ids is not None else None
        row = {"mod": mod, "stage": f.get("stage", UNM), "owed": f.get("owed"), "refused": n,
               "refused_ids": ids, "live": f.get("live_units"), "hand_steps": f.get("hand_steps")}
        rows.append(row)

        def put(decision, why, need=None):
            row["decision"], row["why"] = decision, why
            if need:
                row["need"] = "%s: %s" % (mod, need)

        if f.get("stage") != "offline_build":
            s.pop("owed_since", None)
            s.pop("watch", None)
            put("not_offline", "stands at %s; only the offline build launches from here%s" % (
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
                s["watch"] = {"unit": live[0], "refused": n, "ids": ids, "at": now,
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
            if not (isinstance(was, int) and isinstance(n, int) and n < was):
                s["stopped"] = {"ids": ids, "at": now, "why": "run %s ended and the refused bars went %s -> %s, "
                                "not down" % (w.get("unit"), was, n)}
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
                    str(v)[:160] for k, v in (f.get("observed") or {}).items() if k in (f.get("hand_steps") or []))))
            continue
        if ids is None:
            put("blind", "the test table cannot be read", "the test table cannot be read; no builder launches on it")
            continue
        stop = s.get("stopped")
        if stop and stop.get("ids") == ids:
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
        if isinstance(ceiling, (int, float)) and usd >= ceiling:
            s["stopped"] = {"ids": ids, "at": now, "why": "USD %.2f spent at the offline build, at or past the %g "
                            "ceiling" % (usd, ceiling)}
            put("stopped", s["stopped"]["why"], "stopped, %s" % s["stopped"]["why"])
            continue
        if not cap_ok:
            put("no_cap", "the settings have no positive cap_usd; nothing launches without a cap")
            continue
        if not account[0]:
            put("account_hold", account[1])
            continue
        if live_total >= int(cfg.get("max_live", 2)):
            put("slots_full", "%d live runs on advancing mods, the most is %s" % (live_total, cfg.get("max_live", 2)))
            continue
        live_total += 1
        put("launch", "%d bars refused as build work, nothing live on it (%s)" % (n, account[1]))
        launches.append(mod)
    return rows, launches


# ---- the acts -------------------------------------------------------------------------------------------------------

def _ingest():
    import importlib.util
    path = os.path.join(REPO, "src", "RimMandrake", "Utils", "testq", "ingest.py")
    spec = importlib.util.spec_from_file_location("maturation_dispatch_ingest", path)
    ing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ing)
    return ing


def file_and_publish(item, title, why):
    """Spawn the build item as RUNNER under this item (the way ops_watch files its alarms: DISPATCHER only notes) and
    publish the RUNNER shard, under the dispatch clone's ingest lock; detached_helper refuses an item not filed on
    origin/main. -> (ok, text)."""
    import dispatcher as D
    lk = D.git_lock()
    if lk is None:
        return False, "ingest.lock stayed busy; nothing filed"
    try:
        ing = _ingest()
        rc, out = ing.rimflow("spawn", "--from", ITEM, "--for", "RELENTLESS", "--needs", "offline", "--name", item,
                              "--title", title, "--why", why)
        if rc:
            return False, "spawn refused: %s" % out[-400:]
        pub = ing.publish(1, message="ledger: maturation dispatch filed %s" % item)
        return True, "filed %s; publish: %s" % (item, str(pub)[-200:])
    finally:
        lk.close()


def known_items():
    import helper_checkpoint as HC
    return HC.known_items()


def execute(root, cfg, st, rows, launches, now, fx=None):
    fx = fx or {}
    do_file = fx.get("file", file_and_publish)
    do_launch = fx.get("launch", lambda mod, cap, item: M.launch_mod(root, mod, cap, item, model=cfg.get("model", "opus"),
                                                                     seat=cfg.get("seat", "BENCH")))
    known = fx["known"]() if "known" in fx else known_items()
    done = []
    for row in rows:
        if row["mod"] not in launches:
            continue
        mod, s = row["mod"], st["mods"][row["mod"]]
        item = item_id(mod, row["refused"], known)
        title = ("%s Stage 3: build the checks for the %d bars not runnable, offline (launched by the Dispatch step)"
                 % (mod, row["refused"]))
        why = ("delegated: maturation_dispatch.py; maturation.py refuses %d bars as build work (%s), nothing live on "
               "it, measured %s" % (row["refused"], ", ".join(row["refused_ids"][:12]), pac(now)))
        ok, text = do_file(item, title, why) if item else (False, "no free item name")
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
            s["watch"] = {"unit": unit, "refused": row["refused"], "ids": row["refused_ids"], "at": now, "ours": True}
            s.pop("owed_since", None)
            row.update(decision="launched", unit=unit, item=item, why=text[:400])
            known.add(item) if isinstance(known, set) else None
            done.append(row)
        else:
            s["stopped"] = {"ids": row["refused_ids"], "at": now, "why": "the launch failed: %s" % text[:300]}
            row.update(decision="launch_failed", why=text[:400],
                       need="%s: the launch failed (%s); the step will not retry it on its own" % (mod, text[:200]))
    return done


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
                                                       "idle_min", "stage_usd")} for r in rows}}


def tick(root, cfg, apply, fx=None, now=None, page=True):
    fx = fx or {}
    now = now or time.time()
    d = sdir()
    st = _read(os.path.join(d, "state.json"), {})
    facts = fx["facts"]() if "facts" in fx else gather(root, cfg)
    account = fx["account"]() if "account" in fx else account_gate()
    rows, launches = decide(cfg, st, facts, now, account)
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
    execute(root, cfg, st, rows, launches, now, fx)
    rd = reading(cfg, rows, now)
    if apply:
        _write(os.path.join(d, "state.json"), st)
        _write(os.path.join(d, "reading.json"), rd)
        with open(os.path.join(d, "ticks.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"at": now, "decisions": {r["mod"]: [r.get("decision"), r.get("refused")] for r in rows},
                                "launched": rd["launched"]}) + "\n")
    if page and apply:
        regen = fx.get("page") or (lambda: subprocess.run([sys.executable, os.path.join(
            REPO, "src", "RimMandrake", "Utils", "maturation_now.py")], capture_output=True, text=True, timeout=600))
        r = regen()
        rd["page"] = "regenerated" if getattr(r, "returncode", 0) == 0 else "page failed: %s" % (
            (getattr(r, "stdout", "") or "") + (getattr(r, "stderr", "") or ""))[-300:]
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
            print("%-20s %-13s %s" % (mod, r["decision"], r["why"]))
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
            print("%-20s %-13s %s" % (mod, r["decision"], r["why"]))
        return 0
    if o.cmd == "clear":
        p = os.path.join(sdir(), "state.json")
        st = _read(p, {})
        s = (st.get("mods") or {}).get(o.mod) or {}
        was = s.pop("stopped", None)
        s.setdefault("cleared", []).append({"at": time.time(), "why": o.why, "was": was})
        st.setdefault("mods", {})[o.mod] = s
        _write(p, st)
        print("CLEARED %s (was: %s)" % (o.mod, (was or {}).get("why", "not stopped")))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
