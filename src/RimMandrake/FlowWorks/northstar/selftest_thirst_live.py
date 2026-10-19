#!/usr/bin/env python3
"""Offline selftest of the thirst live driver (thirst_live.py): --dry-run and --mock against thirst_fake.ThirstFakeBridge.

Proves (1) --dry-run prints the plan and never builds a bridge; (2) a clean mock run emits EXACTLY the declared rows, every
one with a verdict (PASS, except T1/T18 which are UNMEASURED by design), writes mode "mock" (never "live": validation.py must
not read it) and restores the settings; (3) each injected fault flips the row it is meant to flip, so the rows can fail;
(4) the 2026-10-18 harness branches run: a slow Ingest is waited out (PASS), one that never ends is UNMEASURED, refused
colonists are replaced (and six refusals raise), a Store tank's in-flight pour is drained before the baseline.
A mock verdict is evidence about the DRIVER only, never about the mod.
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
import thirst_fake  # noqa: E402
import thirst_live  # noqa: E402

FAILS = []
TMP = tempfile.mkdtemp(prefix="thirst_selftest_")
LOG = os.path.join(TMP, "Player.log")
with open(LOG, "w") as _f:
    _f.write("[FlowWorks] thirst provider: Own (no Dubs)\n")


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else str(detail)[:300]))
    if not cond:
        FAILS.append(name)


def run(only="", faults=(), extra=(), log=LOG):
    """-> (exit code, result dict, fake bridge, stdout). An exception from main() is returned as the code."""
    B = thirst_fake.ThirstFakeBridge(faults=faults)
    out = os.path.join(TMP, "r_%d.json" % len(os.listdir(TMP)))
    argv = [out, "--log", log] + (["--only", only] if only else []) + list(extra)
    buf = io.StringIO()
    code = None
    with contextlib.redirect_stdout(buf):
        try:
            code = thirst_live.main(argv, bridge=B)
        except Exception as ex:  # noqa: BLE001 - the refuse_all case raises by design
            code = ex
    try:
        res = json.load(open(out, encoding="utf-8"))
    except (OSError, ValueError):
        res = {"rows": []}
    return code, res, B, buf.getvalue()


def st(res, rid):
    for r in res["rows"]:
        if r["id"].startswith(rid):
            return r["status"], r["class"]
    return None, None


def expect(label, res, rid, status, cls=None):
    got = st(res, rid)
    check("%s: %s -> %s" % (label, rid, status), got[0] == status and (cls is None or got[1] == cls), got)


# ---- (1) dry run
class _NoBridge(object):
    def __init__(self, *a, **k):
        raise AssertionError("--dry-run built a bridge")


import validation_core as V  # noqa: E402
_real = V.Bridge
V.Bridge = _NoBridge
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = thirst_live.main(["--dry-run", "--only", "T4,T5"])
V.Bridge = _real
txt = buf.getvalue()
check("dry run: exit 0, plan lists T4 RUN and T3 skip, no bridge", rc == 0 and "T4    RUN" in txt and "T3    skip" in txt, txt[:200])
with contextlib.redirect_stdout(io.StringIO()):
    check("dry run: an unknown --only key is refused", thirst_live.main(["--dry-run", "--only", "T99"]) == 2)

# ---- (2) clean full mock run
code, res, B, _ = run()
declared = set(i for _, ids, _ in thirst_live.PLAN for i in ids)
emitted = [r["id"] for r in res["rows"]]
extra_ids = [i for i in emitted if i not in declared]
missing = sorted(i for k, ids, _ in thirst_live.PLAN if k != "T15R" for i in ids if i not in emitted)
check("clean mock: exactly the declared rows (none missing, none undeclared)", not extra_ids and not missing, (extra_ids, missing))
check("clean mock: no duplicate row ids", len(emitted) == len(set(emitted)), emitted)
by = {r["id"]: r["status"] for r in res["rows"]}
unexpected = {k: v for k, v in by.items() if v != "PASS" and k not in ("T1_provider_line", "T18_dubs_last_resort")}
check("clean mock: every row PASSes but T1/T18 (UNMEASURED by design)", not unexpected, unexpected)
check("clean mock: T1 and T18 are UNMEASURED", by.get("T1_provider_line") == "UNMEASURED" and by.get("T18_dubs_last_resort") == "UNMEASURED", by)
check("clean mock: result says mode mock, never live", res.get("mode") == "mock", res.get("mode"))
check("clean mock: settings restored to the shipped values",
      all(str(B.settings[k]).lower() == str(thirst_fake.SETTINGS0[k]).lower() for k in thirst_fake.SETTINGS0), B.settings)
check("clean mock: exit code 1 (T1/T18 are not PASS)", code == 1, code)

# ---- (3)(4) faults: (label, only, faults, [(row id, status)])
CASES = [
    ("slow ingest is waited out", "T4,T5", ["ingest_slow"], [("T4", "PASS"), ("T5", "PASS")]),
    ("ingest never ends", "T4,T5", ["ingest_never_ends"], [("T4", "UNMEASURED"), ("T5", "UNMEASURED")]),
    ("ordered job refused", "T4,T5", ["no_ordered_job"], [("T4", "UNMEASURED"), ("T5", "UNMEASURED")]),
    ("salt hydrates like fresh", "T4,T5", ["salt_ratio"], [("T4", "PASS"), ("T5", "FAIL")]),
    ("no dehydration hediff", "T6", ["no_dehydration"], [("T6", "UNMEASURED")]),
    ("dehydration too slow", "T6", ["slow_dehydration"], [("T6", "FAIL")]),
    ("need falls too fast", "T3", ["fast_decay"], [("T3", "FAIL")]),
    ("no terrain drink", "T10", ["no_terrain_drink"], [("T10", "FAIL")]),
    ("setting OFF ignored", "T10", ["terrain_when_off"], [("T10", "FAIL")]),
    ("salt drunk routinely", "T12", ["salt_routine"], [("T12", "FAIL")]),
    ("autofill takes salt", "T11", ["fill_salt"], [("T11", "FAIL")]),
    ("nobody douses", "T24", ["no_fire_job"], [("T24", "FAIL")]),
    ("douse puts out one fire", "T24", ["douse_single"], [("T24", "FAIL")]),
    ("fires do not take", "T24", ["no_fuel"], [("T24", "UNMEASURED")]),
    ("refused pawns are replaced", "T24,T23,T25", ["refuse_first_2"], [("T24", "PASS"), ("T23", "PASS"), ("T25", "PASS")]),
    ("store tank still fills", "T23", ["store_still_fills"], [("T23", "FAIL")]),
    ("in-flight pour is drained", "T23", ["inflight_pour"], [("T23", "PASS")]),
    ("snow never melts", "T25", ["no_melt"], [("T25", "FAIL")]),
    ("stock over-fills", "T29", ["stock_overfill"], [("T29", "FAIL")]),
    ("xenotype ignored", "T28", ["no_xenotype"], [("T28", "UNMEASURED")]),
    ("Dubs need on every colonist", "T2", ["dubs_need"], [("T2", "FAIL")]),
    ("biomes mod absent", "T15,T16,T27", ["no_biomes"], [("T15", "UNMEASURED"), ("T16", "UNMEASURED"), ("T27", "UNMEASURED")]),
    ("stale terrain mark across reload", "T15R", ["stale_mark"], [("T15R", "FAIL")]),
    ("clean reload", "T15R", [], [("T15R", "PASS")]),
]
for label, only, faults, wants in CASES:
    code, res, B, _ = run(only, faults)
    for rid, status in wants:
        expect(label, res, rid, status)
    if label == "in-flight pour is drained":
        check("in-flight pour: the late stop and its landing really happened", getattr(B, "late_stops", 0) >= 1 and getattr(B, "late_drops", 0) >= 1,
              (getattr(B, "late_stops", 0), getattr(B, "late_drops", 0)))
        det = next(r["detail"] for r in res["rows"] if r["id"].startswith("T23"))
        check("in-flight pour: the late bucket was cleared before the Store baseline", det.get("droppedAtSwitch") == 0, det.get("droppedAtSwitch"))
    if label == "refused pawns are replaced":
        check("refused pawns: two colonists were refused and replaced", B.refused_n >= 2, B.refused_n)
    if label == "snow never melts":
        det = next(r["detail"] for r in res["rows"] if r["id"].startswith("T25"))
        check("snow never melts: the row followed the bucket for the whole 7,000", det.get("meltTicks") is None and len(det.get("meltTrace") or []) == 14, det.get("meltTrace"))

# ---- refuse_all raises after six replacements, the finally still restores the settings
code, res, B, _ = run("T24", ["refuse_all"])
check("six refused colonists in a row raise", isinstance(code, RuntimeError) and "incapable" in str(code), code)
check("...and the settings are still restored (finally)", all(str(B.settings[k]).lower() == str(thirst_fake.SETTINGS0[k]).lower() for k in thirst_fake.SETTINGS0))

# ---- blocked site aborts with a SITE row, never a mod verdict
code, res, B, _ = run("T2", ["site_blocked"])
expect("blocked site", res, "site_ready", "UNMEASURED", "SITE")
check("blocked site: exit 2 and no T2 row", code == 2 and st(res, "T2_")[0] is None, code)

# ---- log rows
bad_log = os.path.join(TMP, "bad.log")
with open(bad_log, "w") as f:
    f.write("[FlowWorks] thirst provider: Own (x)\nException in RM_Thirst tick\n")
code, res, B, _ = run("T7", log=bad_log)
expect("exception naming RM_Thirst", res, "T7", "FAIL")
code, res, B, _ = run("T7", log=os.path.join(TMP, "missing.log"))
expect("no log given", res, "T7", "UNMEASURED")

print()
if FAILS:
    print("selftest_thirst_live: %d FAILED: %s" % (len(FAILS), FAILS))
    sys.exit(1)
print("selftest_thirst_live: OK")
