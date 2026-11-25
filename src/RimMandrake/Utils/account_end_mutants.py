#!/usr/bin/env python3
"""Planted faults for selftest_account_end.py (page design/specs/2026-11-24-account-end/boundary.md): each is one
realistic fault in a COPY of the code, and the selftest must print FAIL lines naming the promise it breaks. A control (no
fault) must pass. A plant whose anchor is gone is an error by name, never a catch. Exit 0: every fault caught.

    python3 src/RimMandrake/Utils/account_end_mutants.py
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent
A, S, D, L, C, J = ("Utils/account_end.py", "Utils/switching_plan.py", "rimflow/detached_helper.py",
                    "rimflow/left_open_continue.py", "rimflow/control.py", "Utils/switching_plan.json")
# (promise its FAIL line must name, file, old, new)
PLANTS = [
    ("the-warning-fires-at-two-at-an-ordinary-burn", J, '"warn_pct": 2', '"warn_pct": 1'),
    ("the-warning-fires-at-three-at-a-fast-burn", A, 'burn["rate"] > fast_rate(base, cfg)', 'False'),
    ("the-warning-fires-at-three-at-a-fast-burn", A, 'or u > prev or (', 'or (' ),
    ("the-order-tells-the-numbers", A, '"%s%% of its week is left and the machine burns %.3f%% a minute" % (num(pct), b["rate"])',
     '"its week is nearly used"'),
    ("the-order-tells-the-numbers", A, '- ((burn or {}).get("age_s") or 0) / 60)', ')'),
    ("no-new-work-at-the-line", D, 'if carried and not n.get("account_end"):', 'if carried:'),
    ("no-new-work-at-the-line", S, '"account_end": bool(d.get("account_end")) and state == "soft",', '"account_end": False,'),
    # the fault of 2026-11-24 4:56 PM PST (RIMMANDRAKE_BURN_TO_LINE_WARNING_SWITCHED_AT_THREE): the live account was
    # no target at its warning line, so the switch went with no run live
    ("the-account-burns-to-its-line", S, '    cfg = plan["account_end"]\n    for n in elig:  # no switch lands',
     '    cfg = plan["account_end"]\n    if warn is not None and pl is not None and pl <= warn:\n        elig[live] = False\n'
     '    for n in elig:  # no switch lands'),
    ("the-account-burns-to-its-line", S, '"warn", "warn", d["warning_text"]', '"warn", "at_easy_spot", d["warning_text"]'),
    ("the-account-burns-to-its-line", S, '    elif d.get("warning"):      # the warning zone', '    elif False:      # the warning zone'),
    ("the-account-burns-to-its-line", D, '    w = n.get("warning")\n', '    w = None\n'),
    ("the-account-burns-to-its-line", A, 'then keep working: new work still starts', 'then end your turn: no new work starts'),
    ("the-account-burns-to-its-line", S, 'for _ in range(passes - 1):', 'for _ in ():'),
    ("the-account-burns-to-its-line", C, "state=CASE WHEN mode='warn' THEN 'delivered' ELSE 'seen' END", "state='seen'"),
    ("the-warning-is-latched", S, 'return max(w, ep["warn_line"]) if (ep.get', 'return w if (ep.get'),
    ("the-warning-is-latched", S, "        end_episode(state, d, orders, f\"{live} reads {d['pct_left']}%: it has reset\")", '        pass'),
    ("the-emergency-orders-pauses-then-switches", S, '        sleep(min(5, left_s))', '        break'),
    ("the-emergency-orders-pauses-then-switches", S, '"emergency", "write_now", text', '"emergency", "at_easy_spot", text'),
    ("the-emergency-orders-pauses-then-switches", S, '    em, first = ep.get("emergency"), False', '    em, first = None, False'),
    ("the-emergency-orders-pauses-then-switches", S, '            break       # the last run ended', '            pass       # the last run ended'),
    ("the-pause-keeps-the-chance-of-zero-under-ten-percent", J, '"pause_share": 0.2', '"pause_share": 0.5'),
    ("the-pause-keeps-the-chance-of-zero-under-ten-percent", A, '* 60 - (burn.get("age_s") or 0)', '* 60'),
    ("a-stale-reading-uses-the-safe-values", A, 'if burn is None or burn.get("stale") or burn.get("rate") is None or burn["rate"] >',
     'if burn and burn.get("rate") is not None and burn["rate"] >'),
    ("a-stale-reading-uses-the-safe-values", A, '    if not burn or burn.get("stale") or burn.get("rate") is None:\n        return cfg["pause_min_s"]',
     '    if not burn or burn.get("stale") or burn.get("rate") is None:\n        return cfg["pause_max_s"]'),
    ("a-stale-reading-uses-the-safe-values", A, 'if age > cfg["stale_min"] * 60:', 'if False:'),
    ("a-stale-reading-uses-the-safe-values", S, '        return AE.stale_burn("%s: %s" % (type(e).__name__, e))',
     '        return {"rate": 0.0, "stale": False, "age_s": 0, "why": ""}'),
    ("a-kept-account-has-no-emergency", A, 'return line is not None and line <= cfg["emergency_max_line"]', 'return True'),
    ("a-kept-account-has-no-emergency", S, '    if w is None or p > w:  ', '    if False:  '),
    ("the-last-account-goes-dark-and-comes-back", S, 'base.update(warning=True, last_account=not any(',
     'base.update(warning=True, last_account=False and any('),
    ("the-last-account-goes-dark-and-comes-back", S, "last = d.get(\"drain_of\") != \"switch\"", 'last = False'),
    ("a-one-percent-line-is-not-killed-unwarned", S, '        return {**d, "emergency": True} if AE.has_emergency(ln, cfg) else d', '        return d'),
    ("unreadable-runs-count-as-live", S, '    if live_runs is not None and not live_runs:\n        return d', '    if not live_runs:\n        return d'),
    ("unreadable-runs-count-as-live", S, 'if still_live is not None and not still_live:', 'if not still_live:'),
    ("each-step-is-recorded-once", S, 'todo = [u for u in units if step not in (seen.get(u) or {})]', 'todo = units'),
    ("each-step-is-recorded-once", S, '    state["account_end_events"] = left_over\n', '    state["account_end_events"] = []\n'),
    ("each-step-is-recorded-once", S, '                state.pop("account_end", None)\n                save_state(state)\n        rec["result"], rc = res, 0 if ok',
     '        rec["result"], rc = res, 0 if ok'),
    ("an-order-spends-no-trial-and-blocks-nothing", A, 'if r["family"] in FAMILIES]', ']'),
    ("an-order-spends-no-trial-and-blocks-nothing", C, '''                      (u, r["id"] if r else None, mode, act["id"], why.strip(), now, deadline))
''', '''                      (u, r["id"] if r else None, mode, act["id"], why.strip(), now, deadline))
            c.execute("INSERT OR IGNORE INTO voids VALUES (?,?,?,?,?,?)", (u, None, act["id"], why, None, now))
'''),
    ("a-wrapped-run-is-carried-on-after-the-switch", L, '    waits_for = account_end_wait(now)', '    waits_for = None'),
    ("a-wrapped-run-is-carried-on-after-the-switch", L, '    if not ok or account_end_wait(now):', '    if False:'),
    ("a-wrapped-run-is-carried-on-after-the-switch", L, '            r["continue_waits"] = kept', '            pass'),
    ("a-switch-never-lands-on-an-ending-account", S, '> AE.target_line(line[n], cfg)', '> 0'),
    ("no-new-work-at-the-line", D, 'if n.get("state") == "stop":', 'if False:'),
    ("no-new-work-at-the-line", S, '"drain": True, "account_end": True}, now)  # nothing starts', '}, now)  # nothing starts'),
    ("the-warning-is-latched", S, 'and not lowered(ep, line[live])) else w', ') else w'),
    ("a-stale-reading-uses-the-safe-values", S, '    if not usable(r) or (r.get("age_min")', '    if False or (r.get("age_min")'),
    ("a-stale-reading-uses-the-safe-values", S, '(r.get("age_min") is not None and r["age_min"] > cfg["stale_min"])', 'False'),
    ("the-pause-keeps-the-chance-of-zero-under-ten-percent", A, '(since is None or t >= since) and', ''),
    ("the-hold-file-stops-it", S, '    return not (OUT / "HOLD").exists()', '    return True'),
]


def run(plant=None):
    """-> (rc, output) of the selftest in a copy of src/RimMandrake's two folders, with the plant in."""
    tmp = Path(tempfile.mkdtemp(prefix="account_end_mutant_"))
    try:
        root = tmp / "src" / "RimMandrake"
        for d in ("Utils", "rimflow"):
            shutil.copytree(SRC / d, root / d, ignore=shutil.ignore_patterns("__pycache__", "*.png", "*.dll"))
        if plant:
            p = root / plant[1]
            s = p.read_text(encoding="utf-8")
            if s.count(plant[2]) != 1:
                return None, "anchor found %d times" % s.count(plant[2])
            p.write_text(s.replace(plant[2], plant[3]), encoding="utf-8")
        r = subprocess.run([sys.executable, str(root / "Utils" / "selftest_account_end.py")], capture_output=True, text=True,
                           timeout=600, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=""))
        return r.returncode, r.stdout + r.stderr
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    from concurrent.futures import ThreadPoolExecutor
    rc, out = run()
    if rc != 0 or "selftest_account_end: PASS" not in out:
        print("CONTROL RED: the harness proves nothing:\n" + out[-800:])  # cut-ok: test diagnostic display
        return 3
    bad = 0
    with ThreadPoolExecutor(4) as ex:     # each run has its own copy and its own scratch dirs
        for p, (rc, out) in zip(PLANTS, ex.map(run, PLANTS)):
            fails = [x for x in out.splitlines() if x.startswith("FAIL  ")]
            named = [x for x in fails if x[6:].startswith(p[0]) or x[6:].startswith("t_" + p[0].replace("-", "_"))]
            ok = rc == 1 and bool(named)
            bad += not ok
            print("%s %s: %s -> %s" % ("caught " if ok else "MISSED ", p[0], p[2].strip().splitlines()[0][:70],
                                       named[0][6:150] if named else (out[-160:] if rc is None else "%d other FAIL(s): %s" % (  # cut-ok: test diagnostic display
                                           len(fails), fails[:1]))))
    print("account_end_mutants: %s (%d of %d caught, control green)" % ("FAIL" if bad else "PASS", len(PLANTS) - bad, len(PLANTS)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
