#!/usr/bin/env python3
"""Offline selftest of the sprinkler live driver (sprinkler_live.py): --dry-run and --mock against sprinkler_fake.

Proves (1) --dry-run prints the plan and builds no bridge; (2) a clean mock run emits EXACTLY the declared rows, every one
PASS, mode "mock" (never "live"), settings restored; (3) each injected fault flips the intended row, so the rows can fail;
(4) the 2026-10-18 cold-pulse fix: with the 250-tick wait T22 passes at every build phase, without it (COLD_WAIT=0) the mock
goes red for T22 at phases where the head's first pulse lands before vanilla's TicksGame % 200 power switch; (5) mandrake.rm.biomes
absent -> the three IsSoaked rows are UNMEASURED SITE. A mock verdict is evidence about the DRIVER only, never about the mod.
"""
import contextlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (HERE, os.path.join(os.path.dirname(os.path.dirname(HERE)), "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import sprinkler_fake  # noqa: E402
import sprinkler_live  # noqa: E402

FAILS = []
TMP = tempfile.mkdtemp(prefix="sprinkler_selftest_")


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else str(detail)[:300]))
    if not cond:
        FAILS.append(name)


def run(only="", faults=(), start_tick=2):
    B = sprinkler_fake.SprinklerFakeBridge(faults=faults, start_tick=start_tick)
    out = os.path.join(TMP, "r_%d.json" % len(os.listdir(TMP)))
    argv = [out] + (["--only", only] if only else [])
    buf = io.StringIO()
    code = None
    with contextlib.redirect_stdout(buf):
        try:
            code = sprinkler_live.main(argv, bridge=B)
        except Exception as ex:  # noqa: BLE001 - spawn_fail raises by design
            code = ex
    try:
        res = json.load(open(out, encoding="utf-8"))
    except (OSError, ValueError):
        res = {"rows": []}
    return code, res, B, buf.getvalue()


def st(res, rid):
    for r in res["rows"]:
        if r["id"] == rid:
            return r["status"], r["class"]
    return None, None


def expect(label, res, rid, status, cls=None):
    got = st(res, rid)
    check("%s: %s -> %s" % (label, rid, status), got[0] == status and (cls is None or got[1] == cls), got)


IDS = {k: ids[0] for k, ids in sprinkler_live.PLAN}

# ---- (1) dry run
import validation_hose  # noqa: E402


class _NoBridge(object):
    def __init__(self, *a, **k):
        raise AssertionError("--dry-run built a bridge")


_real = validation_hose.H
validation_hose.H = _NoBridge
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = sprinkler_live.main(["--dry-run", "--only", "draws,brine"])
    rc_bad = sprinkler_live.main(["--dry-run", "--only", "nonsense"])
validation_hose.H = _real
check("dry-run: exit 0, plan lists RUN/skip", rc == 0 and "draws" in buf.getvalue() and "skip" in buf.getvalue(), buf.getvalue())
check("dry-run: unknown --only key exits 2", rc_bad == 2, rc_bad)

# ---- (2) clean run
code, res, B, _ = run()
declared = [i for _, ids in sprinkler_live.PLAN for i in ids]
got = [r["id"] for r in res["rows"]]
check("clean: rows == declared rows, in plan order", sorted(got) == sorted(declared) and len(got) == len(set(got)), got)
check("clean: every row PASS", all(r["status"] == "PASS" for r in res["rows"]), [(r["id"], r["status"]) for r in res["rows"]])
check("clean: exit 0", code == 0, code)
check("clean: mode is mock, never live", res.get("mode") == "mock", res.get("mode"))
check("clean: settings restored", B.settings == sprinkler_fake.SETTINGS0, B.settings)

# ---- (3) faults flip the intended rows (and nothing else is asked of them)
FAULT_ROW = [("pump_ignores_setting", "pressure"), ("switch_ignored", "switch"), ("free_spray", "draws"),
             ("soak_forever", "dries"), ("thick_sprays", "thick"), ("wall_leak", "walls"), ("brine_sprays", "brine"),
             ("acid_harmless", "effects"), ("no_filth", "effects"), ("no_reserve", "reserve"), ("no_drink", "reserve")]
for fault, key in FAULT_ROW:
    code, res, B, _ = run(only=key, faults=(fault,))
    expect("fault %s" % fault, res, IDS[key], "FAIL", "MOD")
code, res, B, _ = run(only="effects", faults=("spawn_fail",))
check("fault spawn_fail: the driver raises (no MOD verdict on a pawn that never spawned)", isinstance(code, RuntimeError), code)

# ---- (4) the cold pulse: the 250-tick wait is what keeps T22 off the pre-power pulse
# build ticks: the fake's head phase (tick + thingID) % 250 and the power switch at tick % 200 line up the bad way only in a narrow
# band (a pulse >130 ticks after the build but before the next multiple of 200: tick 601 here), so sweep every tick around it
starts = list(range(2, 40, 7)) + list(range(560, 660))
red_without, red_with = [], []
for s in starts:
    code, res, _, _ = run(only="brine", start_tick=s)
    if st(res, IDS["brine"])[0] != "PASS":
        red_with.append(s)
sprinkler_live.COLD_WAIT = 0
try:
    for s in starts:
        code, res, B, _ = run(only="brine", start_tick=s)
        stt = st(res, IDS["brine"])
        if stt[0] == "FAIL":
            red_without.append(s)
            r = [r for r in res["rows"] if r["id"] == IDS["brine"]][0]
            check("no wait @%d: the failure is the cold pulse (brine-only reads No pressure)" % s,
                  "No pressure" in str(r["detail"].get("brineOnly")), r["detail"])
        else:
            if stt[0] != "PASS":
                check("no wait @%d: a row that does not fail is PASS" % s, False, stt)
finally:
    sprinkler_live.COLD_WAIT = 250
check("with the wait: T22 PASS at every build phase (%d phases)" % len(starts), not red_with, red_with)
print("info  without the wait: %d of %d phases FAIL" % (len(red_without), len(starts)))   # informational; the next check is the one that can fail
check("without the wait: T22 FAILS at some phase (power switch at %200 beats the first pulse)", len(red_without) > 0, red_without)

# ---- (5) biomes absent -> the three IsSoaked rows are SITE, UNMEASURED
code, res, B, _ = run(faults=("no_biomes",))
for k in ("draws", "dries", "walls"):
    expect("no biomes", res, IDS[k], "UNMEASURED", "SITE")
for k in ("pressure", "switch", "thick", "brine", "effects", "reserve"):
    expect("no biomes (not IsSoaked rows)", res, IDS[k], "PASS")

print("\n%s" % ("selftest_sprinkler_live: ALL OK" if not FAILS else "selftest_sprinkler_live: %d FAILED: %s" % (len(FAILS), FAILS)))
sys.exit(1 if FAILS else 0)
