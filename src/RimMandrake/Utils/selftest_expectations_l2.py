#!/usr/bin/env python3
"""selftest_expectations_l2.py - offline proof of the L2 half of the one manifest format
(expectations_l2.py) and of `run_expectations.py --l2 --plan-only` over the real manifests.

Every verdict branch is driven with synthetic readbacks/log entries; the magenta counter is
run on a real PNG written to a temp dir; the CLI is run as a subprocess against
infrastructure/state/expectations/. MASS_VALIDATION_LADDER_1.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
import expectations_l2 as l2  # noqa: E402
import expectations_manifest as em  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s%s" % ("PASS" if cond else "FAIL", name, ("  -- %s" % (detail,)) if not cond else ""))
    if not cond:
        FAILS.append(name)


def raises(fn, *a):
    try:
        fn(*a)
    except (ValueError, em.ManifestError):
        return True
    return False


# ---- parse_l2
spec = l2.parse_l2({"spawn": [{"pawnKind": "RM_A", "count": 2}, {"thing": "RM_B"}], "ticks": 900})
check("parse: kinds, counts, ticks", [(s.kind, s.defName, s.count) for s in spec.spawn] == [("pawn", "RM_A", 2), ("thing", "RM_B", 1)] and spec.ticks == 900)
check("parse: ticks default", l2.parse_l2({"spawn": [{"thing": "X"}]}).ticks == l2.DEFAULT_TICKS)
for bad, why in [([], "not an object"), ({"spawn": []}, "empty spawn"), ({"spawn": [{"pawnKind": "A", "thing": "B"}]}, "two kinds"),
                 ({"spawn": [{"count": 1}]}, "no kind"), ({"spawn": [{"thing": "A b"}]}, "not a defName"),
                 ({"spawn": [{"thing": "A", "count": 0}]}, "count 0"), ({"spawn": [{"thing": "A", "count": True}]}, "count bool"),
                 ({"spawn": [{"thing": "A", "cnt": 1}]}, "unknown spawn key"), ({"spawn": [{"thing": "A"}], "ticks": 0}, "ticks 0"),
                 ({"spawn": [{"thing": "A"}], "ticks": l2.MAX_TICKS + 1}, "ticks over max"), ({"spawn": [{"thing": "A"}], "tick": 5}, "unknown key")]:
    check("parse refuses: " + why, raises(l2.parse_l2, bad))

# ---- manifest integration: a bad l2 section fails the manifest LOUD
base = {"item": "X_1", "checks": [{"defType": "ThingDef", "defName": "A", "path": "label", "expected": "a"}]}
check("manifest without l2 -> l2 None", em.parse_manifest(dict(base)).l2 is None)
check("manifest with l2 parsed", em.parse_manifest(dict(base, l2={"spawn": [{"pawnKind": "A"}]})).l2.spawn[0].defName == "A")
check("manifest with bad l2 -> ManifestError", raises(em.parse_manifest, dict(base, l2={"spawn": "A"})))

# ---- plan_batch / batch_rect / batch_ticks
m1 = em.parse_manifest(dict(base, item="M1", l2={"spawn": [{"pawnKind": "P%d" % i} for i in range(10)], "ticks": 300}))
m2 = em.parse_manifest(dict(base, item="M2", l2={"spawn": [{"thing": "T"}], "ticks": 800}))
m3 = em.parse_manifest(dict(base, item="M3"))
plan = l2.plan_batch([m1, m2, m3], (250, 250))
check("plan: one cell per op across manifests", len(plan) == 11 and plan[-1].item == "M2" and plan[-1].kind == "thing")
check("plan: cells distinct", len({(p.x, p.z) for p in plan}) == 11)
check("plan: 8 columns then wrap", plan[8].z == plan[0].z + 6 and plan[8].x == plan[0].x)
check("plan: centred", abs((min(p.x for p in plan) + max(p.x for p in plan)) / 2 - 125) <= 3)
check("plan: inside margins", all(10 <= p.x <= 240 and 10 <= p.z <= 240 for p in plan))
check("plan: does not fit -> ValueError", raises(l2.plan_batch, [m1, m2], (40, 40)))
check("plan: no l2 -> empty", l2.plan_batch([m3], (250, 250)) == [])
x, z, w, h = l2.batch_rect(plan)
check("rect covers every cell", all(x <= p.x < x + w and z <= p.z < z + h for p in plan))
check("batch ticks = longest", l2.batch_ticks([m1, m2, m3]) == 800)

# ---- attribute_logs
ents = [{"Level": "Error", "Message": "Exception ticking RSW_Moornak123: NRE"},
        {"Level": "Error", "Message": "Exception in RSW_MoornakUnsettled.Tick"},
        {"Level": "Warning", "Message": "RSW_Moornak could not find path"},
        {"Level": "Warning", "Message": "Some vanilla warning"},
        {"Level": "Exception", "Message": "NullReferenceException at Verse.Foo"},
        {"Level": "Warning", "Message": "[proof log sentinel] revive 1"}]
by_def, un = l2.attribute_logs(ents, ["RSW_Moornak", "RSW_MoornakUnsettled"])
check("logs: word boundary keeps RSW_Moornak off RSW_MoornakUnsettled", by_def.get("RSW_MoornakUnsettled") == ["Exception in RSW_MoornakUnsettled.Tick"]
      and by_def.get("RSW_Moornak") == ["RSW_Moornak could not find path"], by_def)
check("logs: unattributed errors kept, warnings and sentinel dropped",
      un == ["Exception ticking RSW_Moornak123: NRE", "NullReferenceException at Verse.Foo"], un)

# ---- magenta
check("magenta: pure magenta yes, pink-ish no", l2.is_magenta(255, 0, 255) and not l2.is_magenta(255, 120, 255) and not l2.is_magenta(120, 0, 255))
try:
    from PIL import Image
    with tempfile.TemporaryDirectory() as td:
        pth = os.path.join(td, "m.png")
        im = Image.new("RGB", (50, 50), (40, 90, 40))
        for i in range(10):
            for j in range(10):
                im.putpixel((i, j), (255, 0, 255))
        im.save(pth)
        check("magenta_in_png counts a 10x10 block", l2.magenta_in_png(pth) == 100)
except ImportError:
    check("Pillow present for the magenta counter", False, "pip install pillow")

# ---- count_on_map
pawns = [{"kind": "A", "spawned": True, "dead": False}, {"kind": "A", "spawned": True, "dead": True},
         {"kind": "A", "spawned": False}, {"kind": "B"}]
check("count: alive spawned pawns of the kind only", l2.count_on_map(pawns, "pawn", "A") == 1)
check("count: things sum stackCount", l2.count_on_map([{"def": "T", "stackCount": 4}, {"def": "T"}, {"def": "U", "stackCount": 9}], "thing", "T") == 5)

# ---- verdict
P = [l2.Planned("I1", "pawn", "A", 1, 0, 0), l2.Planned("I1", "pawn", "B", 2, 6, 0),
     l2.Planned("I2", "pawn", "C", 1, 12, 0), l2.Planned("I2", "thing", "T", 3, 18, 0), l2.Planned("I2", "pawn", "D", 1, 24, 0)]
before = {("pawn", "A"): 0, ("pawn", "B"): 1, ("pawn", "C"): 0, ("thing", "T"): 0, ("pawn", "D"): 0}
placed = {("pawn", "A"): 1, ("pawn", "B"): 2, ("pawn", "C"): 1, ("thing", "T"): 3, ("pawn", "D"): 1}
after = {("pawn", "A"): 1, ("pawn", "B"): 2, ("pawn", "C"): 0, ("thing", "T"): 3, ("pawn", "D"): 1}
rows = l2.verdict(P, before, placed, after, {"D": ["NRE in D"]}, [], log_alive=True, tap_lost=0, magenta=3, restarted=None)
st = {r.subject: r.status for r in rows}
check("verdict: A PASS", st["pawn:A"] == "PASS", st)
check("verdict: B NOT-SPAWNED (pre-existing pawn not counted)", st["pawn:B"] == "NOT-SPAWNED", st)
check("verdict: C GONE after ticks", st["pawn:C"] == "GONE", st)
check("verdict: T PASS by stack readback", st["thing:T"] == "PASS", st)
check("verdict: D LOG", st["pawn:D"] == "LOG", st)
check("verdict: batch rows PASS when clean", st["one-sitting"] == "PASS" and st["log"] == "PASS" and st["art"] == "PASS", st)
st2 = {r.subject: r.status for r in l2.verdict(P[:1], before, placed, after, {}, ["NRE"], log_alive=True, tap_lost=0, magenta=500, restarted="map changed 1 -> 2")}
check("verdict: RESTARTED / LOG-UNATTRIBUTED / ART", (st2["one-sitting"], st2["log"], st2["art"]) == ("RESTARTED", "LOG-UNATTRIBUTED", "ART"), st2)
st3 = {r.subject: r.status for r in l2.verdict(P[:1], before, placed, after, {}, ["NRE"], log_alive=False, tap_lost=0, magenta=None, restarted=None)}
check("verdict: dead log -> LOG-BLIND (beats unattributed), no shot -> ART-BLIND", (st3["log"], st3["art"]) == ("LOG-BLIND", "ART-BLIND"), st3)
st4 = {r.subject: r.status for r in l2.verdict(P[:1], before, placed, after, {}, [], log_alive=True, tap_lost=7, magenta=0, restarted=None)}
check("verdict: lost journal entries -> LOG-BLIND", st4["log"] == "LOG-BLIND", st4)
check("verdict: only PASS rows are ok", all(r.ok == (r.status == "PASS") for r in rows))

# ---- sitting_broken
check("sitting: same map, clock forward -> None", l2.sitting_broken({"mapId": 1, "ticksGame": 100}, {"mapId": 1, "ticksGame": 700}) is None)
check("sitting: new map -> broken", l2.sitting_broken({"mapId": 1, "ticksGame": 100}, {"mapId": 2, "ticksGame": 700}) is not None)
check("sitting: clock backwards -> broken", l2.sitting_broken({"mapId": 1, "ticksGame": 900}, {"mapId": 1, "ticksGame": 10}) is not None)

check("sitting: clock short of the asked ticks -> broken", l2.sitting_broken({"mapId": 1, "ticksGame": 100}, {"mapId": 1, "ticksGame": 400}, want_ticks=600) is not None)
check("sitting: unreadable clock or map -> broken", l2.sitting_broken({"mapId": None, "ticksGame": 1}, {"mapId": None, "ticksGame": 2}) is not None
      and l2.sitting_broken({"mapId": 1, "ticksGame": None}, {"mapId": 1, "ticksGame": 5}) is not None)
bd, un2 = l2.attribute_logs([{"Level": "Info", "Message": "spawned RM_A"}, {"Level": "Info", "Message": "boom"}], ["RM_A"])
check("logs: info lines are never faults", bd == {} and un2 == [], (bd, un2))

# ---- flyer_refusals
kf = {"Walk": {"race": "WalkRace"}, "Fly": {"race": "FlyRace"}, "Lost": None, "NoStats": {"race": "Bare"}}
rf = {"WalkRace": {"statBases": [{"stat": "MoveSpeed", "value": 4}]}, "FlyRace": {"statBases": [{"stat": "MaxFlightTime", "value": 120}]},
      "Bare": {"statBases": None}}
fr = {r.subject: r.status for r in l2.flyer_refusals(kf, rf)}
check("flyers: flyer refused, walker passes, unreadable refused",
      fr == {"pawn:Fly": "FLYER", "pawn:Lost": "FLYER-UNKNOWN", "pawn:NoStats": "FLYER-UNKNOWN"}, fr)

# ---- CLI over the real manifests (offline plan) and flag guards
RUN = [sys.executable, str(HERE / "run_expectations.py")]
GLOB = str(REPO / "infrastructure/state/expectations/*.expectations.json")
r = subprocess.run(RUN + ["--l2", "--glob", GLOB, "--plan-only"], capture_output=True, text=True, timeout=60)
check("cli: --l2 --plan-only over the real manifests exits 0", r.returncode == 0, r.stdout[-400:] + r.stderr[-400:])
check("cli: plan names no flyer (RSW_Hawkbat)", "RSW_Hawkbat" not in r.stdout)
check("cli: every real manifest parses", "0 manifest(s) unparsable" in r.stdout, r.stdout[-300:])
for argv in (["--l2", "--glob", GLOB], ["--l2", "--glob", GLOB, "--plan-only", "--live"], ["--glob", GLOB, "--plan-only"]):
    r = subprocess.run(RUN + argv, capture_output=True, text=True, timeout=60)
    check("cli refuses %s" % " ".join(a for a in argv if a.startswith("--")), r.returncode == 2, r.returncode)
with tempfile.TemporaryDirectory() as td:
    pth = Path(td) / "bad.expectations.json"
    pth.write_text('{"item": "B_1", "checks": [{"defType": "ThingDef", "defName": "A", "path": "label", "expected": 1}], "l2": {"spawn": "x"}}')
    r = subprocess.run(RUN + ["--l2", "--manifest", str(pth), "--plan-only"], capture_output=True, text=True, timeout=60)
    check("cli: a bad l2 section exits 1 and says MANIFEST-ERROR", r.returncode == 1 and "MANIFEST-ERROR" in r.stdout, r.stdout[-300:])

print("\n%d failing" % len(FAILS))
sys.exit(1 if FAILS else 0)
