#!/usr/bin/env python3
"""selftest_flowworks_gpt_b.py — the FlowWorks pre-release GPT-consult fixes, builder B (terrain, pits, rivers).

WHY: `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` confirmed bugs whose fix lives in Verse-bound code
(MapComponent ticks, WorkGiver gates, a ThingComp scan, a flood's spread gate) that the C# SelfTest cannot compile.
The pocket-grid arithmetic of the same push is tested behaviourally in Source/SelfTest/CliffMaskChecks.cs. Each case
here reads the PRODUCTION .cs (comments masked) and asserts the fixed shape; the swim patch's xpath is run with lxml
against FlowWorks' own Defs (a count, so a renamed fill ladder goes red).

CAN IT FAIL: every C# case carries `undo`, a (fixed, old) splice that restores the shape GPT found; each run applies it
to an in-memory copy and the case must go RED there. A case whose undo stays green fails.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_gpt_b.py
"""
from __future__ import annotations

import glob
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "Source"
FAILS: list[str] = []


def mask_comments(text: str) -> str:
    """Blank // and /* */ comments (strings kept) so a fix that survives only in a comment is gone."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1]); i = j + 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i)); i = j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("".join(ch if ch == "\n" else " " for ch in text[i:j])); i = j
        else:
            out.append(c); i += 1
    return "".join(out)


def squash(s: str) -> str:
    return " ".join(s.split())


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + detail))
    if not ok:
        FAILS.append(name)


# (item, file, must-contain snippets (whitespace-insensitive, comments masked), undo (fixed, old))
CASES = [
    ("FERRY_ROPE_FIX_BUILT_ONLY_WHEN_ASKED C6-F1: the river tick rebuilds dirty works before anything else",
     "Rivers/RM_MapComponent_RiverCurrent.cs",
     ["public override void MapComponentTick() { if (worksDirty) { EnsureWorks(); } if (!RM_RiversSettings.CurrentActive)"],
     ("if (worksDirty) { EnsureWorks(); } if (!RM_RiversSettings.CurrentActive)", "if (!RM_RiversSettings.CurrentActive)")),
    ("RIVER_CURRENT_PROBE_LATE_GRAB C6-F10: a steam vent puffs only while its cell is still river",
     "ManyWaters/RiverSteamHook.cs",
     ["if (!cell.Fogged(map) && cell.GetTerrain(map).IsRiver)"],
     ("if (!cell.Fogged(map) && cell.GetTerrain(map).IsRiver)", "if (!cell.Fogged(map))")),
    ("PANNING_SPOT_VERIFY_EMPTY_RIVER C5-F7: panning is skipped once no placer rock is left to draw",
     "Quarry/RM_PlacerWorks.cs",
     ["return stock == null || stock.Stock < 1f || !stock.PoolAny;", "poolAny = RM_PlacerDraw.Pool(map).Count > 0;"],
     ("return stock == null || stock.Stock < 1f || !stock.PoolAny;", "return stock == null || stock.Stock < 1f;")),
    ("COVER_DECK_TUNE_QUADRATIC_CENSUS C4-F3: a cover beside a lower-id cover is not the lead and floods nothing",
     "Pits/Trigger/CompPitCoverTrigger.cs",
     ["Building_PitCover n = RM_PitCoverUtility.CoverAt(map, self.Position + GenAdj.CardinalDirections[i]); "
      "if (n != null && n.thingIDNumber < self.thingIDNumber) return; } List<Building_PitCover> deck = RM_PitCoverUtility.Deck(self);"],
     ("if (n != null && n.thingIDNumber < self.thingIDNumber) return;", "")),
    ("COVER_DECK_TUNE_QUADRATIC_CENSUS C4-F5: a mixed deck gives way at its weakest cover",
     "Pits/Trigger/CompPitCoverTrigger.cs",
     ["float kg = c.CoverTier.TriggerMassKg(); if (kg < tierKg) tierKg = kg;",
      "float threshold = tierKg * RimMandrakeFlowWorksSettings.trapSensitivityMultiplier;"],
     ("float threshold = tierKg *", "float threshold = Pit.CoverTier.TriggerMassKg() *")),
    ("COVER_DECK_TUNE_QUADRATIC_CENSUS C4-F6: the deck flood has no size cap",
     "Pits/Building_PitCover.cs",
     ["while (open.Count > 0) {"],
     ("while (open.Count > 0) {", "while (open.Count > 0 && deck.Count < 400) {")),
    ("FLOOD_RELEASE_PROBE_FORGOTTEN_REFUSALS C5-F11: a wet DUG cell is left to the engine, not refused at the gate",
     "Flood_FlowWorks.cs",
     ["if (t == null || (t.IsWater && !(excavation != null && excavation.IsExcavated(c))))"],
     ("if (t == null || (t.IsWater && !(excavation != null && excavation.IsExcavated(c))))", "if (t == null || t.IsWater)")),
    ("PIT_FALL_MEND_SAVED_MIDAIR C3-F1: a jump takes its fall at once, not on the unsaved detector's next pass",
     "Superdeep/RM_SuperdeepTrap.cs",
     ["IntVec3 from = p.Position; p.Position = cell; p.Notify_Teleported(true, true); "
      "eng.SuperdeepTrap.ResolveArrivalNow(p.Map, eng, p, from); return true;",
      "RM_SuperdeepTrap.OnForcedDescent(p, pos, this,"],
     ("eng.SuperdeepTrap.ResolveArrivalNow(p.Map, eng, p, from);", "")),
]


def run_cases() -> None:
    for name, rel, musts, (fixed, old) in CASES:
        path = SRC / rel
        text = squash(mask_comments(path.read_text(encoding="utf-8")))
        missing = [m for m in musts if squash(m) not in text]
        check(name, not missing, "missing: %r" % missing[:1])
        mutant = text.replace(squash(fixed), squash(old), 1)
        red = mutant != text and any(squash(m) not in mutant for m in musts)
        check(name + " [undo goes red]", red, "the undo splice did not turn the case red")


def run_swim_patch() -> None:
    """CANAL_SWIM_VERIFY_POISON_POOL_PARTY C9-F8: the no-swim marker reaches every hazardous fill ladder, never water."""
    try:
        from lxml import etree
    except ImportError:
        check("swim patch: lxml importable", False, "pip install lxml")
        return
    patch = etree.parse(str(HERE / "Patches" / "Canals" / "FlowWorks_NoRecreationalSwim.xml"))
    op = patch.find("Operation")
    check("swim patch: one AddModExtension", op is not None and op.get("Class") == "PatchOperationAddModExtension")
    li = op.find("value/li") if op is not None else None
    cls = li.get("Class") if li is not None else ""
    check("swim patch: the marker class the JoyGiver veto reads", cls == "RimMandrake.FlowWorks.ManyWaters.RM_NoRecreationalSwimExtension")
    ext_src = (SRC / "ManyWaters" / "RM_NoRecreationalSwimExtension.cs").read_text(encoding="utf-8")
    veto_src = (SRC / "ManyWaters" / "RM_Patch_NoRecreationalSandSwim.cs").read_text(encoding="utf-8")
    check("swim patch: marker class exists in namespace RimMandrake.FlowWorks.ManyWaters",
          "namespace RimMandrake.FlowWorks.ManyWaters" in ext_src and "class RM_NoRecreationalSwimExtension" in ext_src)
    check("swim patch: the veto reads the marker", "HasModExtension<RM_NoRecreationalSwimExtension>()" in veto_src)
    root = etree.Element("Defs")
    for f in glob.glob(str(HERE / "Defs" / "**" / "*.xml"), recursive=True):
        for d in etree.parse(f).getroot():
            if isinstance(d.tag, str):
                root.append(d)
    xp = op.findtext("xpath")
    assert xp.startswith("Defs/")
    hits = root.xpath(xp[len("Defs/"):])
    names = {h.findtext("defName") for h in hits}
    fills = {d.findtext("defName") for d in root.findall("TerrainDef") if (d.findtext("defName") or "").startswith("RM_Fill_")}
    check("sanity: FlowWorks declares the fill ladders", len(fills) >= 50, "found %d" % len(fills))
    want = {n for n in fills if not n.startswith(("RM_Fill_Water_", "RM_Fill_IcyWater_"))}
    check("swim patch: every hazardous fill tier is marked (44)", names == want and len(names) == 44,
          "hits %d, missing %s, extra %s" % (len(names), sorted(want - names)[:4], sorted(names - want)[:4]))
    check("swim patch: plain and icy water stay swimmable",
          not any(n.startswith(("RM_Fill_Water_", "RM_Fill_IcyWater_")) for n in names))


def main() -> int:
    run_cases()
    run_swim_patch()
    print("\n%s" % ("PASS: 0 failure(s)" if not FAILS else "FAIL: %d failure(s): %s" % (len(FAILS), FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
