#!/usr/bin/env python3
"""Offline selftest of SHEETRAIN_DOPULSE_TAME_DELUGE_SPIKE. No bridge, no game.

1. sheetrain_deluge_window.verdict: the r18 sheet-ON reading (DoPulse 30.8 ms) is a SPIKE, a tamed reading is TAMED,
   and a window that cannot show the path (no pocket rain, the sheet took nothing, too few ticks, refused names, wrong
   scene) is never TAMED.
2. The production shape, over the real RM_MapComponent_Excavation.cs (comments stripped): the kernel's walk only queues
   a pocket's overflow (no sheet offer inside DoPulse), the quiet ticks drain RM_RainOfferQueue.PerTick offers, the
   sheet's pulse has a tick of its own before the pulse is due (DoPulse runs it only as the fallback), the guard is
   scribed, and a save drains every offer. Each rule is proven able to fail: a copy with that line spliced out must go red.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sheetrain_deluge_window as W

REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "Source")
FAILS = []


def check(name, got, want):
    if got != want:
        FAILS.append("%s: got %r want %r" % (name, got, want))


# ── 1. the verdict ──
FIVE = ["ludeon.rimworld", "Ludeon.RimWorld.Royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
        "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey", "mandrake.rm.flowworks"]
DP, CP, EP, DR = W.JUDGED
PR = W.K + ":PocketRain"


def prof(dp=3100.0, cp=5000.0, ep=9000.0, dr=2000.0, pr=2200.0, as_dict=False, drop=(), refused=None):
    ms = []
    for name, mx, calls in ((DP, dp, 17), (CP, cp, 161), (EP, ep, 17), (DR, dr, 300), (PR, pr, 310)):
        if name in drop:
            continue
        ms.append({"method": name, "calls": calls, "meanUs": "100 us", "maxUs": "%.1f us" % mx})
    p = {"methods": {m.pop("method"): m for m in ms} if as_dict else ms}
    if refused is not None:
        p["refused"] = refused
    return p


ok = dict(ticks=2025, package_ids=FIVE, map_size=325, rain_before=9_000_000, rain_after=12_777_002)
check("tamed", W.verdict(prof(), **ok)[:2], (0, "TAMED"))
check("tamed dict-shaped profile", W.verdict(prof(as_dict=True), **ok)[:2], (0, "TAMED"))
# live r18 RAIN_C_A_SHEET (prof_RAIN_C_A_SHEET.txt): DoPulse 30796.2 us, ContinuePulse 13994.6 us -> SPIKE
check("r18 sheet ON", W.verdict(prof(dp=30796.2, cp=13994.6, pr=9287.8), **ok)[:2], (1, "SPIKE"))
check("bar is inclusive", W.verdict(prof(ep=20000.0), **ok)[:2], (1, "SPIKE"))
check("just under the bar", W.verdict(prof(ep=19999.0), **ok)[:2], (0, "TAMED"))
check("drain spike", W.verdict(prof(dr=25000.0), **ok)[:2], (1, "SPIKE"))
check("continue spike", W.verdict(prof(cp=21000.0), **ok)[:2], (1, "SPIKE"))
check("DoPulse untimed", W.verdict(prof(drop=(DP,)), **ok)[:2], (1, "BLIND"))
check("sheet pulse never ran", W.verdict(prof(drop=(EP,)), **ok)[:2], (1, "BLIND"))
check("no pocket rain", W.verdict(prof(drop=(PR,)), **ok)[:2], (1, "UNEXERCISED"))
check("sheet took nothing", W.verdict(prof(), **dict(ok, rain_after=9_000_000))[:2], (1, "UNEXERCISED"))
check("ledger unread", W.verdict(prof(), **dict(ok, rain_before=None))[:2], (1, "BLIND"))
check("too few ticks", W.verdict(prof(), **dict(ok, ticks=900))[:2], (1, "BLIND"))
check("judged name refused", W.verdict(prof(refused=[EP]), **ok)[:2], (1, "BLIND"))
check("shown name refused is fine", W.verdict(prof(refused=["Verse.TickManager:DoSingleTick"]), **ok)[:2], (0, "TAMED"))
check("refusal text", W.verdict(prof(refused="patch failed"), **ok)[:2], (1, "BLIND"))
check("no FlowWorks", W.verdict(prof(), **dict(ok, package_ids=FIVE[:-1]))[:2], (1, "WRONG_SCENE"))
check("an expansion missing", W.verdict(prof(), **dict(ok, package_ids=[i for i in FIVE if "odyssey" not in i]))[:2], (1, "WRONG_SCENE"))
check("mods unread", W.verdict(prof(), **dict(ok, package_ids=None))[:2], (1, "WRONG_SCENE"))
check("small map", W.verdict(prof(), **dict(ok, map_size=250))[:2], (1, "WRONG_SCENE"))
check("us str", W.us("8507.6 us"), 8507.6)
check("us unavailable", W.us("unavailable: no calls timed"), None)
check("us bool", W.us(True), None)
check("inRain", W.in_rain("SHEETLEDGER enabled=T in=5 inPump=0 inRain=12777002 inFlood=0"), 12777002)
check("inRain refused", W.in_rain("REFUSED: no current map"), None)


# ── 2. the production shape ──
def strip(cs):
    cs = re.sub(r"/\*.*?\*/", " ", cs, flags=re.S)
    return re.sub(r"//[^\n]*", " ", cs)


def body(cs, signature):
    """The brace block of the first method whose signature line matches, or '' when absent."""
    m = re.search(signature, cs)
    if not m:
        return ""
    i = cs.index("{", m.end())
    depth = 0
    for j in range(i, len(cs)):
        if cs[j] == "{":
            depth += 1
        elif cs[j] == "}":
            depth -= 1
            if depth == 0:
                return cs[i:j + 1]
    return ""


RULES = (
    # (name, method signature, pattern that must be in its body, pattern that must NOT be)
    ("the walk queues, it never offers", r"private void DoPulse\(\)",
     r"rainOverflow = rainOverflowCb \?\?= \(idx, dl, fl\) => rainOffersOwed\.Add\(idx, dl, fl\);", r"RainOverflowDl\("),
    ("DoPulse runs the sheet only as the fallback", r"private void DoPulse\(\)",
     r"if \(sheetPulsedFor != pulseDueTick\)\s*\{\s*sheetPulsedFor = pulseDueTick;\s*map\.GetComponent<Sheet\.RM_MapComponent_Sheet>\(\)\?\.EnginePulse\(\);", None),
    ("the sheet pulse has a quiet tick of its own", r"public override void MapComponentTick\(\)",
     r"if \(sheetPulsedFor != nextPulseTick && !PulseInFlight && now >= nextPulseTick - SheetPulseLeadTicks\)\s*\{\s*sheetPulsedFor = nextPulseTick;\s*map\.GetComponent<Sheet\.RM_MapComponent_Sheet>\(\)\?\.EnginePulse\(\);\s*return;", None),
    ("the quiet ticks drain a few offers", r"public override void MapComponentTick\(\)",
     r"DrainRainOffers\(RM_RainOfferQueue\.PerTick\);\s*return;", None),
    ("the drain makes the sheet offer and counts what it took", r"private void DrainRainOffers\(int max\)",
     r"pocketRainAcceptedDl \+= rainOffersOwed\.Drain\(max, rainOfferCb \?\?= \(idx, dl, fl\) =>\s*Sheet\.RM_MapComponent_Sheet\.RainOverflowDl\(", None),
    ("a save makes every offer", r"public void FinishPulse\(\)", r"DrainRainOffers\(int\.MaxValue\);", None),
    ("the guard is scribed", r"public override void ExposeData\(\)",
     r"Scribe_Values\.Look\(ref sheetPulsedFor, \"RM_sheetPulsedFor\", int\.MinValue\);", None),
)


def shape(cs):
    """-> the names of the rules the source breaks."""
    cs = strip(cs)
    bad = []
    for name, sig, must, mustnt in RULES:
        b = body(cs, sig)
        if not re.search(must, b) or (mustnt and re.search(mustnt, b)):
            bad.append(name)
    return bad


def queue_shape(cs):
    cs = strip(cs)
    bad = []
    if not re.search(r"public const int PerTick = [1-9]\d*;", cs):
        bad.append("PerTick is a small positive count")
    if not re.search(r"if \(index\.TryGetValue\(\(cell, fluid\), out int at\)\)\s*\{\s*amounts\[at\] \+= dl;", cs):
        bad.append("an offer waiting at the same lip grows")
    if not re.search(r"for \(int n = 0; n < max && next < cells\.Count; n\+\+\)", cs):
        bad.append("at most max offers, oldest first")
    if not re.search(r"index\.Remove\(\(cell, fluid\)\);\s*next\+\+;\s*got \+= offer\(cell, dl, fluid\);", cs):
        bad.append("an offer leaves the queue before it is made")
    if not re.search(r"else if \(next >= CompactAfter && next \* 2 >= cells\.Count\)\s*\{\s*Compact\(\);", cs):
        bad.append("the drained head is compacted")
    return bad


ex_path = os.path.join(SRC, "RM_MapComponent_Excavation.cs")
q_path = os.path.join(SRC, "RM_TerrainWriteBudget.cs")
ex = open(ex_path, encoding="utf-8").read()
q = open(q_path, encoding="utf-8").read()
check("production excavation shape", shape(ex), [])
check("production queue shape", queue_shape(q), [])
# can it fail: splice each rule's line out (or the old offer back in) and the rule must go red
SPLICES = (
    ("the walk queues, it never offers", "(idx, dl, fl) => rainOffersOwed.Add(idx, dl, fl);",
     "(idx, dl, fl) => pocketRainAcceptedDl += Sheet.RM_MapComponent_Sheet.RainOverflowDl(map, map.cellIndices.IndexToCell(idx), dl, fl as FluidDef);"),
    ("the sheet pulse has a quiet tick of its own", "&& now >= nextPulseTick - SheetPulseLeadTicks)", "&& false)"),
    ("the quiet ticks drain a few offers", "DrainRainOffers(RM_RainOfferQueue.PerTick);", ";"),
    ("a save makes every offer", "DrainRainOffers(int.MaxValue);", ";"),
    ("the guard is scribed", 'Scribe_Values.Look(ref sheetPulsedFor, "RM_sheetPulsedFor", int.MinValue);', ";"),
    ("DoPulse runs the sheet only as the fallback", "if (sheetPulsedFor != pulseDueTick)", "if (true)"),
)
for name, old, new in SPLICES:
    if ex.count(old) < 1:
        FAILS.append("probe %r: the line to splice is gone from the source" % name)
        continue
    check("probe goes red: " + name, name in shape(ex.replace(old, new)), True)
check("probe goes red: queue grows", "an offer waiting at the same lip grows" in queue_shape(q.replace("amounts[at] += dl;", "")), True)
check("probe goes red: offered before dequeued", "an offer leaves the queue before it is made" in queue_shape(
    q.replace("next++;\n\t\t\t\tgot += offer(cell, dl, fluid);", "got += offer(cell, dl, fluid);\n\t\t\t\tnext++;")), True)
check("probe goes red: no compaction", "the drained head is compacted" in queue_shape(q.replace("Compact();", ";")), True)

if FAILS:
    print("FAIL selftest_sheetrain_tame_deluge: %d" % len(FAILS))
    for f in FAILS:
        print("  " + f)
    sys.exit(1)
print("PASS selftest_sheetrain_tame_deluge: verdict cases, %d shape rules, %d splices proven red" % (len(RULES) + 5, len(SPLICES) + 3))
