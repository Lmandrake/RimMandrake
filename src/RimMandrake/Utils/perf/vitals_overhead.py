#!/usr/bin/env python3
r"""VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL: the test-state monitor's (`jawa/vitals`) cost, armed vs off, on one tier.

GPT review 2026-10-13 §5 (design/RimMandrake/test_control/test_control_review_gpt_20261013.md): "Measure both the
23-mod tier and full list. Compare armed/off repeated workloads, including busy pawn maps, arrivals, health changes,
paused UI, and long stepping. Each source keeps its own measured cost ... An unexercised hook remains UNMEASURED."

Workloads, each run as ABBA-ordered off/armed repetitions on ONE quicktest map (ABBA balances drift):
  long      2 x 6,000 ticks per arm on the bare quicktest map
  busy      4 x 1,500 ticks per arm after spawning --busy wild animals (a busy pawn map)
  arrivals  4 x 1,200 ticks per arm, a trader caravan and a visitor group fired once before the first rep
  health    4 x 800 ticks per arm, --hurt animals scratched before EACH rep (both arms)
  paused    2 x --paused-s wall seconds per arm, paused with Dialog_Options open (no tick runs; the ui/heartbeat
            wall passes are what is measured)
Stepping is `rimworld/step_game_ticks` in BOTH arms: `jawa/safe_advance` auto-arms the monitor, so it cannot be the
"off" mover. "off" is disarmed with the DoSingleTick hook installed (the state after any test session) once the
first arm has run; the first off rep of `long` runs before any arm and is recorded as `hooks` = its real status.
Armed reps arm with specimens (steel stacks) so the `subjects` channel runs; `heartbeat` runs every 5 s while armed.

Numbers per workload: median wall ms per tick off and armed and the A/B delta (end-to-end, noisy), and the monitor's
own meters (`channels.totalMs` delta over the armed reps) as a share of the metered span, status read to status
read (direct, quiet). Rep counts are even so the ABBA order is balanced.
Budget: the owner's 10 % campaign budget (skills/telemetry/SKILL.md) is reported as WITHIN/OVER; it does not decide
the exit — this is a measurement item.

Exit 0 = MEASURED: right tier, the setup landed (>=80 % of --busy animals, an arrival fired, a scratch landed),
every rep ran exactly its workload's ticks, every channel of the six measured (calls > 0) with its
switch on. Exit 1 = WRONG_LIST, BLIND (a rep ran no ticks, no status) or UNMEASURED (a channel never ran or is off).
The verdict is a pure function, selftested offline (selftest_vitals_overhead.py).

Live (Windows Python; the bridge is the supervisor's to lease; starts a fresh quicktest map, never touches a save):
  python.exe vitals_overhead.py --tier minimal|full [--out <dir>]
"""
import argparse, json, os, statistics, sys, time

CHANNELS = ("pawns", "threats", "clock", "ui", "subjects", "heartbeat")
BUDGET_PCT = 10.0
TIERS = {"minimal": (10, 80), "full": (300, 100000)}   # running-mod count bounds; the 23-mod tier sits in minimal
WORKLOADS = {  # name: (reps per arm, ticks per rep); paused has ticks 0 (wall seconds instead)
    "long": (2, 6000),
    "busy": (4, 1500),         # even rep counts: ABBA is balanced only over whole cycles
    "arrivals": (4, 1200),
    "health": (4, 800),
    "paused": (2, 0),
}


def abba(reps):
    """The arm order for `reps` reps per arm: off,armed, armed,off, ... (False = off). Balanced under linear drift
    only when reps is even (selftest)."""
    return [armed for i in range(reps) for armed in ((False, True) if i % 2 == 0 else (True, False))]


def _delta(after, before):
    """channels{} (status) after minus before -> {ch: {calls, totalMs}}; a channel absent from either is None."""
    out = {}
    for ch in CHANNELS:
        a, b = (after or {}).get(ch), (before or {}).get(ch)
        if not isinstance(a, dict) or not isinstance(b, dict):
            out[ch] = None
            continue
        out[ch] = {"calls": int(a.get("calls") or 0) - int(b.get("calls") or 0),
                   "totalMs": float(a.get("totalMs") or 0.0) - float(b.get("totalMs") or 0.0),
                   "on": bool(a.get("on"))}
    return out


def summarize(wl):
    """One workload's reps -> numbers. A rep: {arm: off|armed, ticks_req, ticks_run, wall_ms, meters (delta) or None}."""
    off = [r for r in wl if r["arm"] == "off"]
    arm = [r for r in wl if r["arm"] == "armed"]
    s = {"reps_off": len(off), "reps_armed": len(arm)}
    per = lambda rs: [r["wall_ms"] / r["ticks_run"] for r in rs if r.get("ticks_run") and (r.get("wall_ms") or 0) > 0]
    po, pa = per(off), per(arm)
    if po and pa:
        mo, ma = statistics.median(po), statistics.median(pa)
        s["off_ms_per_tick"], s["armed_ms_per_tick"] = round(mo, 4), round(ma, 4)
        s["ab_delta_pct"] = round(100.0 * (ma - mo) / mo, 2) if mo > 0 else None
        s["off_spread_pct"] = round(100.0 * (max(po) - min(po)) / mo, 2) if len(po) > 1 and mo > 0 else None
    ch_ms, ch_calls = {c: 0.0 for c in CHANNELS}, {c: 0 for c in CHANNELS}
    for r in arm:
        for c, m in (r.get("meters") or {}).items():
            if m:
                ch_ms[c] += m["totalMs"]
                ch_calls[c] += m["calls"]
    wall = sum((r.get("span_ms") or r.get("wall_ms") or 0) for r in arm)   # meters cover the span, not just the step
    s["channel_ms"] = {c: round(v, 3) for c, v in ch_ms.items()}
    s["channel_calls"] = ch_calls
    s["meter_share_pct"] = round(100.0 * sum(ch_ms.values()) / wall, 3) if wall > 0 else None
    return s


def verdict(result, tier):
    """(exit code, word, text, summary). Pure: no bridge."""
    lo, hi = TIERS[tier]
    mods = result.get("mods")
    if not isinstance(mods, int) or not (lo <= mods <= hi):
        return 1, "WRONG_LIST", "running mods %r outside %s tier bounds %d..%d" % (mods, tier, lo, hi), {}
    wls = result.get("workloads") or {}
    summary, problems, calls = {}, [], {c: 0 for c in CHANNELS}
    off_switch = set()
    for name, (reps, ticks) in WORKLOADS.items():
        wl = wls.get(name)
        if not wl:
            problems.append("BLIND: workload %s absent" % name)
            continue
        for r in wl:
            if r.get("ticks_req") != ticks or r.get("ticks_run") != ticks or not (r.get("wall_ms") or 0) > 0:
                problems.append("BLIND: %s %s rep ran %r of %r ticks (wants %d) in %r ms"
                                % (name, r.get("arm"), r.get("ticks_run"), r.get("ticks_req"), ticks, r.get("wall_ms")))
            want = r.get("arm") == "armed"
            if r.get("armed_state") != [want, want]:
                problems.append("BLIND: %s %s rep: monitor armed state was %r" % (name, r.get("arm"), r.get("armed_state")))
            if not ticks and r.get("paused_ok") is not True:
                problems.append("BLIND: paused %s rep: pause or Dialog_Options did not take" % r.get("arm"))
            if r.get("arm") == "armed":
                if not isinstance(r.get("meters"), dict):
                    problems.append("BLIND: %s armed rep has no vitals status" % name)
                    continue
                for c in CHANNELS:
                    m = r["meters"].get(c)
                    if m is None:
                        problems.append("BLIND: %s armed rep: channel %s missing from status" % (name, c))
                        continue
                    calls[c] += m["calls"]
                    if not m["on"]:
                        off_switch.add(c)
        s = summarize(wl)
        if s["reps_off"] < reps or s["reps_armed"] < reps:
            problems.append("BLIND: %s ran %d off / %d armed reps, wants %d each" % (name, s["reps_off"], s["reps_armed"], reps))
        summary[name] = s
    setup = result.get("setup") or {}
    busy = setup.get("busy") or {}
    if not (busy.get("wild_pawns") or 0) >= 0.8 * (busy.get("asked") or 1):
        problems.append("BLIND: busy map has %r of %r wild animals" % (busy.get("wild_pawns"), busy.get("asked")))
    if not (setup.get("arrivals_fired") or 0) >= 1:
        problems.append("BLIND: no arrival incident fired")
    if not (setup.get("hurt_ok") or 0) >= 1:
        problems.append("BLIND: no health change landed")
    for c in CHANNELS:
        if c in off_switch:
            problems.append("UNMEASURED: channel %s switched off (vitals_settings.json)" % c)
        elif calls[c] <= 0:
            problems.append("UNMEASURED: channel %s never ran while armed" % c)
    if problems:
        word = "BLIND" if any(p.startswith("BLIND") for p in problems) else "UNMEASURED"
        return 1, word, "; ".join(problems), summary
    over = [n for n, s in summary.items() if (s.get("meter_share_pct") or 0) > BUDGET_PCT
            or (n != "paused" and (s.get("ab_delta_pct") or 0) > BUDGET_PCT)]
    budget = "OVER %g%% in %s" % (BUDGET_PCT, ",".join(over)) if over else "WITHIN %g%%" % BUDGET_PCT
    text = "%s tier, %d mods; budget %s; " % (tier, mods, budget) + "; ".join(
        "%s: A/B %s%% meters %s%%" % (n, s.get("ab_delta_pct"), s.get("meter_share_pct")) for n, s in summary.items())
    return 0, "MEASURED", text, summary


# ---------------------------------------------------------------------------------------------------------- live
def _live(a):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rimbridge_client import RimBridge, resolve_endpoint

    def say(*x):
        print(" ".join(str(i) for i in x), flush=True)

    h, p, t = resolve_endpoint()
    with RimBridge(h, p, t, timeout=900.0) as B:
        def c(tool, **args):
            r = B.call(tool, args, check=False) or {}
            if isinstance(r, dict) and r.get("content"):
                try:
                    r = json.loads(r["content"][0]["text"])
                except Exception:
                    pass
            return r

        def ticks():
            v = c("jawa/time_clock").get("ticksGame")
            if not isinstance(v, int):
                raise SystemExit("BLIND: jawa/time_clock gave no ticksGame")
            return v

        def status():
            st = c("jawa/vitals")
            ch = st.get("channels")
            return st, (ch if isinstance(ch, dict) else None)

        rm = c("jawa/running_mods")
        mods = rm.get("count") if rm.get("count") is not None else len(rm.get("packageIds") or []) or None
        say("RUNNING_MODS", mods)
        res = {"tier": a.tier, "mods": mods, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "workloads": {}}

        # a fresh quicktest map: the run spawns animals and fires arrivals, so it never runs on a loaded save
        c("jawa/vitals", action="disarm", why="vitals_overhead: start off")
        c("rimworld/go_to_main_menu")
        for _ in range(120):
            if c("rimworld/get_ui_state").get("programState") == "Entry":
                break
            time.sleep(1)
        else:
            raise SystemExit("BLIND: never reached the main menu; refusing to spawn into a loaded game")
        r = c("rimworld/start_debug_game_ready", timeoutMs=900000, readiness="mapData", pauseIfNeeded=True)
        for _ in range(600):
            if c("rimworld/get_ui_state").get("programState") == "Playing":
                break
            time.sleep(1)
        else:
            raise SystemExit("BLIND: quicktest never reached Playing: %s" % json.dumps(r, default=str)[:300])
        time.sleep(5)
        c("jawa/debug_settings", action="set", field="enableStoryteller", value="false")   # no surprise raid mid-A/B
        mi = c("jawa/map_info")
        sx, sz = int(mi.get("sizeX") or 250), int(mi.get("sizeZ") or 250)
        cx, cz = sx // 2, sz // 2
        res["map"] = {"sizeX": sx, "sizeZ": sz}
        specimens = []
        for k in range(3):
            c("rimworld/spawn_thing", defName="Steel", stackCount=10, x=cx + 6 + k, z=cz + 6)
            th = c("jawa/list_things", defName="Steel", rect="%d,%d,1,1" % (cx + 6 + k, cz + 6)).get("things") or []
            specimens += [str(x.get("id") or x.get("thingID") or "") for x in th if (x.get("id") or x.get("thingID"))]
        res["specimens"] = specimens
        say("SPECIMENS", specimens)
        animals = []
        setup = res["setup"] = {"arrivals_fired": 0, "hurt_ok": 0}

        def arm():
            r = c("jawa/vitals", action="arm", ttlMin=60, row="vitals_overhead_" + a.tier, timeException=True,
                  specimens=",".join(specimens) or None, why="VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL A/B")
            if not r.get("armed"):
                raise SystemExit("BLIND: arm refused: %s" % json.dumps(r, default=str)[:300])

        def disarm():
            c("jawa/vitals", action="disarm", why="VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL A/B off rep")

        def before_rep(name):
            if name == "health":
                for pid in animals[: a.hurt]:
                    if c("jawa/damage", thingId=pid, amount=3, damageDef="Scratch").get("success"):
                        setup["hurt_ok"] += 1

        def rep(name, armed, n_ticks):
            before_rep(name)
            if armed:
                arm()
            else:
                disarm()
            if not n_ticks:     # the window opens BEFORE the metered span, closes after it
                pz = c("rimworld/pause_game", pause=True)
                ow = c("rimworld/open_window_by_type", windowType="RimWorld.Dialog_Options")
            t0 = ticks()
            s0 = time.perf_counter()       # span: the meters' interval, status read to status read
            st0, ch0 = status()
            row = {"arm": "armed" if armed else "off", "ticks_req": n_ticks, "hooks": st0.get("hooks")}
            w0 = time.perf_counter()
            if n_ticks:
                c("rimworld/step_game_ticks", ticks=n_ticks, pauseFirst=True)
            else:
                time.sleep(a.paused_s)
            row["wall_ms"] = round((time.perf_counter() - w0) * 1000.0, 1)
            st1, ch1 = status()
            row["span_ms"] = round((time.perf_counter() - s0) * 1000.0, 1)
            # the monitor's real state at both ends of the span (a failed disarm must not pass as an off rep)
            row["armed_state"] = [st0.get("armed"), st1.get("armed")]
            row["ticks_run"] = ticks() - t0
            if not n_ticks:
                row["paused_ok"] = bool(pz.get("success") is not False and ow.get("success") and st1.get("paused") is not False)
                c("rimworld/close_window", windowType="RimWorld.Dialog_Options")
            row["meters"] = _delta(ch1, ch0) if (ch0 is not None and ch1 is not None) else None
            if armed:
                disarm()
            say("REP", name, row["arm"], "ticks", row.get("ticks_run"), "wall_ms", row["wall_ms"],
                "meters_ms", {k: (v or {}).get("totalMs") for k, v in (row["meters"] or {}).items()} if armed else "-")
            return row

        for name, (reps, n_ticks) in WORKLOADS.items():
            if name == "busy":
                r = c("jawa/spawn_pawn", kindDef=a.animal, x=cx - 10, z=cz - 10, faction="none", count=a.busy)
                al = c("jawa/list_pawns", faction="nonplayer").get("pawns") or []
                animals[:] = [str(x.get("id")) for x in al if x.get("id") and not x.get("dead") and x.get("kind") == a.animal]
                setup["busy"] = {"asked": a.busy, "success": r.get("success"), "wild_pawns": len(animals)}
                say("BUSY", setup["busy"])
            if name == "arrivals":
                # once per workload, not per rep: per-rep firing grew the workload under the later arm
                for inc in ("TraderCaravanArrival", "VisitorGroup"):
                    if c("jawa/fire_incident", incidentDef=inc, dryRun=False).get("success"):
                        setup["arrivals_fired"] += 1
            rows = []
            for armed in abba(reps):
                rows.append(rep(name, armed, n_ticks))
            res["workloads"][name] = rows
            say("WORKLOAD", name, json.dumps(summarize(rows))[:400])
        c("jawa/debug_settings", action="set", field="enableStoryteller", value="true")
        return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tier", choices=sorted(TIERS), required=True)
    ap.add_argument("--out", default=None, help="directory for vitals_overhead_<tier>.json")
    ap.add_argument("--busy", type=int, default=60, help="wild animals spawned for the busy workload")
    ap.add_argument("--animal", default="Muffalo")
    ap.add_argument("--hurt", type=int, default=10, help="animals scratched before each health rep")
    ap.add_argument("--paused-s", type=float, default=12.0)
    ap.add_argument("--judge", default=None, help="offline: judge a saved result JSON instead of running live")
    a = ap.parse_args()
    if a.judge:
        with open(a.judge, encoding="utf-8") as f:
            res = json.load(f)
    else:
        res = _live(a)
    code, word, text, summary = verdict(res, a.tier)
    res["verdict"] = {"exit": code, "word": word, "text": text, "summary": summary}
    if a.out and not a.judge:
        os.makedirs(a.out, exist_ok=True)
        path = os.path.join(a.out, "vitals_overhead_%s.json" % a.tier)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        print("WROTE", path)
    print(word, text)
    return code


if __name__ == "__main__":
    sys.exit(main())
