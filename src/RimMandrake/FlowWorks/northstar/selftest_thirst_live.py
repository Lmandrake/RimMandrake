#!/usr/bin/env python3
"""Offline selftest of the thirst live driver (thirst_live.py): --dry-run and --mock against thirst_fake.ThirstFakeBridge.

Proves (1) --dry-run prints the plan and never builds a bridge; (2) a clean mock run emits EXACTLY the declared rows, every
one with a verdict (PASS, except T1/T18 which are UNMEASURED by design), writes mode "mock" (never "live": validation.py must
not read it) and restores the settings; (3) each injected fault flips the row it is meant to flip, so the rows can fail;
(4) the 2026-10-18 harness branches run: a slow Ingest is waited out (PASS), one that never ends is UNMEASURED, refused
colonists are replaced (and six refusals raise), a Store tank's in-flight pour is drained before the baseline.
A mock verdict is evidence about the DRIVER only, never about the mod.
"""
# selftest temp containment (BENCH, FLOWWORKS_SELFTESTS_FIX_TMPDIR_LEAKS): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_thirst_live_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
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
# review 2026-10-26: main ends on validation_core.rows_exit, so an UNMEASURED-only run exits 2 (FAIL keeps 1)
check("clean mock: exit code 2 (T1/T18 are UNMEASURED, nothing FAILs)", code == 2, code)

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
    # review 2026-10-27 F17: each refusal row alone, so each one meets its own refused workers
    ("refused pawns are replaced (T24)", "T24", ["refuse_first_2"], [("T24", "PASS")]),
    ("refused pawns are replaced (T23)", "T23", ["refuse_first_2"], [("T23", "PASS")]),
    ("refused pawns are replaced (T25)", "T25", ["refuse_first_2"], [("T25", "PASS")]),
    ("store tank still fills", "T23", ["store_still_fills"], [("T23", "FAIL")]),
    ("in-flight pour is drained", "T23", ["inflight_pour"], [("T23", "PASS")]),
    ("snow never melts", "T25", ["no_melt"], [("T25", "FAIL")]),
    ("stock over-fills", "T29", ["stock_overfill"], [("T29", "FAIL")]),
    ("xenotype ignored", "T28", ["no_xenotype"], [("T28", "UNMEASURED")]),
    ("Dubs need on every colonist", "T2", ["dubs_need"], [("T2", "FAIL")]),
    ("biomes mod absent", "T15,T16,T27", ["no_biomes"], [("T15", "UNMEASURED"), ("T16", "UNMEASURED"), ("T27", "UNMEASURED")]),
    ("stale terrain mark across reload", "T15R", ["stale_mark"], [("T15R", "FAIL")]),
    ("clean reload", "T15R", [], [("T15R", "PASS")]),
    ("draft refused: a free pawn could drink, so no vacuous PASS", "T3,T6", ["draft_refused"], [("T3", "UNMEASURED"), ("T6", "UNMEASURED")]),
    ("Home area not painted", "T24", ["zones_refused"], [("T24", "UNMEASURED")]),
    ("snow not laid", "T25", ["snow_refused"], [("T25", "UNMEASURED")]),
    # job 832567 (2026-10-27): a refilled leftover bucket took drinks 11-14 and was read as the part-drunk one
    ("a stray fresh bucket is not the row's bucket", "T20", ["stray_fresh_bucket"], [("T20", "PASS")]),
    # THIRST_ROWS_HARDEN_FALSE_PASS_ROUTES (GPT review 2026-10-27): every case below is a route the OLD row read as PASS
    # (before/after evidence: D:\ClaudeWork\rimmandrake\thirst_t20\harden_evidence\batch_out.txt); the hardened row must not
    ("F3 leftover bottles, animals ingest them", "T9", ["leftover_bottle_x2", "no_animal_terrain"], [("T9", "FAIL")]),
    ("F3 leftover bottle, native animal ingests it", "T14", ["leftover_bottle", "no_animal_terrain"], [("T14", "FAIL")]),
    ("F4 far bottle packed, never drunk", "T12", ["no_far_bottle", "packer"], [("T12", "FAIL")]),
    ("F6 one drink uses the bucket up", "T19", ["single_use_bucket"], [("T19", "FAIL")]),
    ("F6 bottle ingest cancelled", "T19", ["ingest_cancelled"], [("T19", "UNMEASURED")]),
    ("F7 the 10th drink hydrates nothing", "T20", ["last_drink_empty"], [("T20", "FAIL")]),
    ("F1 a Fill tank never receives the pour", "T23", ["no_pour"], [("T23", "FAIL")]),
    ("F8 Store still fills inside the settle", "T23", ["store_fill_settle"], [("T23", "FAIL")]),
    ("F8 an old brine bucket off the plot is not the row's", "T23", ["old_brine_offplot"], [("T23", "PASS")]),
    # live J20261028T014816Z-d2e098 (THIRST_STORE_TANK_DIAGNOSE_LATE_BRINE): a bystander drafted ~10,000 ticks earlier
    # is freed by the AutoUndrafter mid-T23 (a re-draft re-arms nothing), fills brine and lands it in the settle
    ("auto-undraft must not free a bystander mid-T23", "T23", ["auto_undraft"], [("T23", "PASS")]),
    # GPT review 2026-10-28: the T23-only case ends before the first timer deadline; this long run crosses several
    ("auto-undraft long run: periodic re-arm keeps every draft", "T3,T6,T9,T10,T12", ["auto_undraft"],
     [("T3", "PASS"), ("T6", "PASS"), ("T12", "PASS")]),
    ("F9 snow carried off, an unrelated fresh bucket lands", "T25", ["carry_snow"], [("T25", "FAIL")]),
    ("F10 the pond arm fills nothing", "T25", ["no_bucket_fill"], [("T25", "FAIL")]),
    ("F11 no bill, an old wooden snow bucket melts", "T26", ["no_bill", "leftover_wood_snow"], [("T26", "FAIL")]),
    ("F12 packed starting stock is cleared and measured", "T29", ["packed_stock"], [("T29", "PASS")]),
    ("F12 packed stock hid a one-trip fill", "T29", ["packed_stock", "one_trip"], [("T29", "FAIL")]),
    ("F12 inventories cannot be cleared", "T29", ["gear_refused"], [("T29", "UNMEASURED")]),
    ("F13 OFF arm drinks between samples (T10)", "T10", ["sneak_off_drink"], [("T10", "FAIL")]),
    ("F13 OFF arm drinks between samples (T16)", "T16", ["sneak_off_drink"], [("T16", "FAIL")]),
    ("F13 the 0.05 pawn drinks between samples", "T15", ["sneak_005_drink"], [("T15", "FAIL")]),
    ("F14 the salt break never ends", "T17", ["break_never_ends"], [("T17", "FAIL")]),
    ("F14 the salt break poisons nothing", "T17", ["no_poisoning"], [("T17", "FAIL")]),
    ("F5 a baseliner's hemogen ingest outlasts the window", "T28", ["base_slow_hemogen"], [("T28", "UNMEASURED")]),
    # GPT round 2 (THIRST_ROWS_HARDEN_GPT_ROUND2)
    ("R2#1 T13: the 0.05 pawn drinks toxic water between samples", "T13", ["sneak_005_drink"], [("T13", "FAIL")]),
    ("R2#3 T26: the bill eats the ice and makes nothing (no crash)", "T26", ["ice_eaten"], [("T26", "FAIL")]),
    ("R2#4 T28: a baseliner's hemogen ingest is cancelled (pack not consumed)", "T28", ["base_cancel_hemogen"], [("T28", "UNMEASURED")]),
    ("R2#5 T19: the bucket cannot be read", "T19", ["bucket_unreadable"], [("T19", "UNMEASURED")]),
    ("F2 reload canal water masked the stale mark", "T15R", ["stale_mark", "canal_on_reload"], [("T15R", "FAIL")]),
    ("F2 reload canal water is dried (clean)", "T15R", ["canal_on_reload"], [("T15R", "PASS")]),
    # live J20261028T005149Z-1f7ee6: a governor stop mid-T6 refilled the T6 pawn (T3's row cleared UNDER_TEST)
    ("T6 governor stop must not refill the dehydrating pawn", "T3,T6", ["governor_stop_t6"],
     [("T3", "PASS"), ("T6", "PASS")]),
]
# GPT round 2 #7: a save that starts with the setting OFF must not make the ON arm a false MOD FAIL, and the run must
# put the saved (OFF) value back at the end
for lbl, rid, fault, key in (("T10", "T10", "start_terrain_off", "drinkFromTerrain"), ("T16", "T16", "start_lastresort_off", "lastResortDrinking")):
    code, res, B, _ = run(rid, [fault])
    expect("R2#7 %s: save starts with %s OFF" % (lbl, key), res, rid, "PASS")
    check("R2#7 %s: %s restored to the saved OFF" % (lbl, key), B.settings[key] is False, B.settings[key])

def want_exit(res):
    """validation_core.rows_exit: any FAIL -> 1, else any UNMEASURED -> 2, else 0 (review F20: the code is read too)."""
    ss = [r["status"] for r in res["rows"]]
    return 1 if "FAIL" in ss else (2 if "UNMEASURED" in ss else 0)


def settings_back(B):
    return all(str(B.settings[k]).lower() == str(thirst_fake.SETTINGS0[k]).lower() for k in thirst_fake.SETTINGS0)


for label, only, faults, wants in CASES:
    code, res, B, _ = run(only, faults)
    for rid, status in wants:
        expect(label, res, rid, status)
    check("%s: exit code %s follows the rows" % (label, code), res["rows"] and code == want_exit(res), (code, want_exit(res)))
    check("%s: settings restored" % label, settings_back(B), B.settings)
    if label == "in-flight pour is drained":
        check("in-flight pour: the late stop and its landing really happened", getattr(B, "late_stops", 0) >= 1 and getattr(B, "late_drops", 0) >= 1,
              (getattr(B, "late_stops", 0), getattr(B, "late_drops", 0)))
        det = next(r["detail"] for r in res["rows"] if r["id"].startswith("T23"))
        # review F8: the one fill in flight at the switch is allowed (and only it); its landing is not a Store order
        check("in-flight pour: one fill was in flight at the switch and only it landed in the settle",
              det.get("inFlightAllowance") == 1 and len(det.get("landedInSettle") or []) == 1,
              (det.get("inFlightAllowance"), det.get("landedInSettle")))
    if label.startswith("auto-undraft long run"):
        check("auto-undraft long run: nobody was freed and the periodic re-arm fired",
              getattr(B, "auto_undrafts", None) == 0 and res.get("draftRearms", 0) > 12, (getattr(B, "auto_undrafts", None), res.get("draftRearms")))
    elif label.startswith("auto-undraft"):
        det = next(r["detail"] for r in res["rows"] if r["id"].startswith("T23"))
        check("auto-undraft: the driver re-armed the drafts and no bystander came free",
              res.get("draftRearms", 0) >= 1 and getattr(B, "auto_undrafts", None) == 0 and not det.get("othersInSettle"),
              (res.get("draftRearms"), getattr(B, "auto_undrafts", None), det.get("othersInSettle")))
    if label.startswith("T6 governor stop"):
        check("T6 governor stop: the stop really fired mid-T6", getattr(B, "_gov_fired", False) and res.get("governorStops"),
              res.get("governorStops"))
    if label.startswith("refused pawns are replaced"):
        # review F17: the refusals land on the row's spawned workers; each was drafted out of the way and replaced
        check("%s: two spawned workers were refused" % label, len(B.refused_ids) >= 2, B.refused_ids)
        check("%s: every refused worker was drafted" % label, all(B.pawns[i].drafted for i in B.refused_ids if i in B.pawns),
              [(i, B.pawns[i].drafted) for i in B.refused_ids if i in B.pawns])
    if label == "F12 packed starting stock is cleared and measured":
        det = next(r["detail"] for r in res["rows"] if r["id"].startswith("T29"))
        check("F12: the stock was measured from empty packs", det.get("stockBefore") == 0, det.get("stockBefore"))
    if label == "snow never melts":
        det = next(r["detail"] for r in res["rows"] if r["id"].startswith("T25"))
        check("snow never melts: the row followed the bucket for the whole 7,000", det.get("meltTicks") is None and len(det.get("meltTrace") or []) == 14, det.get("meltTrace"))

# ---- the mock never answers a call it does not model with a cheerful success (a clean full run leaves none unmodelled)
code, res, B, _ = run("")
check("clean mock: every tool the driver called is modelled (unmodelled = %s)" % sorted(B.unmodelled), not B.unmodelled, B.unmodelled)
check("clean mock: no draft was refused", not res.get("draftRefused"), res.get("draftRefused"))
check("clean mock: no settings_restored row (the restore read back)", st(res, "settings_restored")[0] is None)

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
# review F15: the exception headline names no mod; its stack frames do (the old line test read this as clean)
ml_log = os.path.join(TMP, "multiline.log")
with open(ml_log, "w") as f:
    f.write("[FlowWorks] thirst provider: Own (x)\nNullReferenceException: Object reference not set to an instance of an object\n"
            "  at RimMandrake.FlowWorks.Thirst.RM_Thirst.NeedInterval () [0x00012] in <abc>:0\n"
            "  at Verse.Pawn.Tick () [0x00000] in <def>:0\n")
code, res, B, _ = run("T7", log=ml_log)
expect("multiline exception whose frames name RM_Thirst", res, "T7", "FAIL")
ok_log = os.path.join(TMP, "unrelated.log")
with open(ok_log, "w") as f:
    f.write("[FlowWorks] thirst provider: Own (x)\nNullReferenceException: Object reference not set\n"
            "  at SomeOtherMod.Thing.Tick () [0x0] in <a>:0\nRM_Thirst need ticked fine\n")
code, res, B, _ = run("T7", log=ok_log)
expect("an unrelated exception followed by a plain RM_Thirst line", res, "T7", "PASS")

# ---- review F16: row() discards the pawns under test, so the next row drafts them as bystanders
_row_src = open(os.path.join(HERE, "thirst_live.py"), encoding="utf-8").read()
_row_src = _row_src[_row_src.find("    def row(rid, st, cls, det):"):]
check("F16: row() clears UNDER_TEST before it records", "UNDER_TEST.clear()" in _row_src[:_row_src.find("\n    def ", 10)])

# ---- review F18: the stray refill really fires when its conditions hold (undrafted, not thirsty, water, an empty bucket)
_B = thirst_fake.ThirstFakeBridge(faults=["stray_fresh_bucket"])
_B.call("jawa/set_terrain_batch", ops="WaterShallow:30,30,2,2")
for _p in _B.pawns.values():
    _p.need, _p.prio = 0.9, {"Hauling": 1}
_B.ticks(3000)
check("F18: an undrafted hauler refilled the stray bucket", _B.stray_refills >= 1 and _B.of("RM_Bucket_FreshWater"),
      (_B.stray_refills, [t["def"] for t in _B.things.values()]))

# ---- THIRST_FIX_SALT_DRUNK_ROUTINELY / THIRST_FIX_DESPERATE_SKIPS_BOTTLE: the freshwater depth ladder is potable and dried
import re  # noqa: E402
_src = os.path.join(os.path.dirname(HERE), "Source")
with open(os.path.join(_src, "RM_WaterLadder.cs"), encoding="utf-8") as f:
    _ladder = re.search(r"FreshwaterDefNames\s*=\s*\{(.*?)\}", f.read(), re.S)
_rungs = re.findall(r'"([A-Za-z_]+)"', _ladder.group(1)) if _ladder else []
check("ladder table parsed (sanity: 5 wet rungs)", len(_rungs) == 5, _rungs)
check("every freshwater ladder terrain is in POTABLE_TERRAIN (dry_all paints it)",
      all(r in thirst_live.POTABLE_TERRAIN for r in _rungs), [r for r in _rungs if r not in thirst_live.POTABLE_TERRAIN])
with open(os.path.join(_src, "RM_LiquidStock.cs"), encoding="utf-8") as f:
    _stock = f.read()
_dma = _stock[_stock.find("public bool DepthModelApplies"):]
_dma = _dma[:_dma.find("return body.depthExempt == 0;")]
check("DepthModelApplies exempts a non-fresh liquid's body (salt/brine never restaged onto the fresh ladder)",
      "IsOtherLiquidTerrain(t)" in _dma and "canalFluid != RimMandrakeFlowWorks_DefOf.RM_Fluid_Water" in _stock)

print()
if FAILS:
    print("selftest_thirst_live: %d FAILED: %s" % (len(FAILS), FAILS))
    sys.exit(1)
print("selftest_thirst_live: OK")
