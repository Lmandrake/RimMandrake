#!/usr/bin/env python3
"""Source-shape guards for two GSS findings whose code is Verse-bound (no offline C# harness can run it):

  GSS_MULTILINK_FIX_PIPE_POLE_RANGE   the cmultilink :plan probe must plan with CompAerialAnchor.AutoLinkPairs (per-kind
      grouping, AerialLineProfiles.RangeFor) -- the same helper the real "Auto-link selected" gizmo uses -- never the power
      AerialSettings.Range for every kind.
  GSS_FRESH_BUILD_ORACLE_FIX_TAP_CLAMPS   FreshPieces (the fresh/sameframe oracle) must set opt.StraightPlugIds from
      CordWorldAdapter.TapIds(map) before Build, exactly as production Rebuild does.

--mutate proves each guard can fail by running it on text with the original defect restored. Exit 0 PASS, 1 FAIL."""
import os
import re
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Source")


def read(*p):
    return open(os.path.join(SRC, *p), encoding="utf-8").read()


def body(text, header):
    i = text.index(header)
    j = text.index("\n        }\n", i)
    return text[i:j]


def check_plan(probe):
    out = []
    if "CompAerialAnchor.AutoLinkPairs(mine)" not in probe:
        out.append("ConduitStyleProbe :plan no longer uses CompAerialAnchor.AutoLinkPairs")
    if re.search(r"MinimumSpanningLinks\([^;]*AerialSettings\.Range\)", probe):
        out.append("ConduitStyleProbe plans with the power AerialSettings.Range for every kind")
    return out


def check_anchor(anchor):
    out = []
    if "AutoLinkPairs(sel)" not in anchor or "RangeFor(g.Key)" not in anchor:
        out.append("gizmo AutoLinkSelected/AutoLinkPairs no longer groups by kind with RangeFor")
    return out


def check_fresh(probe, prod):
    out = []
    fp = body(probe, "private static List<LaidPiece> FreshPieces(Map map)")
    a = fp.find("opt.StraightPlugIds = CordWorldAdapter.TapIds(map)")
    b = fp.find("b.Build(")
    if a < 0 or b < 0 or a > b:
        out.append("FreshPieces does not set StraightPlugIds = TapIds(map) before Build")
    if "opt.StraightPlugIds = CordWorldAdapter.TapIds(map)" not in prod:
        out.append("production Rebuild no longer sets StraightPlugIds (guard reference lost)")
    return out


def run(probe, anchor, cprobe, prod):
    return check_plan(cprobe) + check_anchor(anchor) + check_fresh(probe, prod) + check_cord_prints(prod)


def check_cord_prints(prod):
    """C#4: new extents can be visible while both the owner and old extent are off screen."""
    dirty = body(prod, "private void DirtySection(IntVec2 s)")
    flush = body(prod, "private void FlushCordPrints()")
    update = body(prod, "public override void MapComponentUpdate()")
    ok = ("pendingPrints.Add(s)" in dirty
          and "pendingPrints.Clear()" in flush
          and "RegenerateSingleLayer(layer)" in flush
          and "SectionLayer_RM_MessyCords" in flush
          and "view" not in flush.lower()
          and update.index("Rebuild(false)") < update.index("FlushCordPrints()") < update.index("DrawMotion()"))
    return [] if ok else ["changed cord owners are not independently printed after publication"]


def check_fallen_retirement(aerial):
    retire = body(aerial, "private void RetireFallenLay(FallenCord f)")
    removed = body(aerial, "public override void MapRemoved()")
    dirty = body(aerial, "private void DirtyCell(IntVec3 c)")
    ok = ("tailCursors.Remove(l)" in retire and "Destroy(mesh)" in retire
          and "tailMeshes.Remove(f)" in retire and "RetireFallenLay(kv.Key)" in dirty
          and "Destroy(m)" in removed and "tailMeshes.Clear()" in removed
          and "tailCursors.Clear()" in removed and "lays.Clear()" in removed)
    return [] if ok else ["fallen lay/cursor/native mesh lifetimes are not retired together"]


def main():
    probe = read("GimmeSomeSlackProbe.cs")
    anchor = read("Aerial", "CompAerialAnchor.cs")
    cprobe = read("Aerial", "ConduitStyleProbe.cs")
    prod = read("RM_MapComponent_CordGraph.cs")
    fails = run(probe, anchor, cprobe, prod)
    aerial = read("Aerial", "RM_MapComponent_Aerial.cs")
    fails += check_fallen_retirement(aerial)
    # can-fail: the original defects restored in memory must each be caught
    m1 = cprobe.replace("CompAerialAnchor.AutoLinkPairs(mine)",
                        "AerialMath.MinimumSpanningLinks(mine.Select(s => s.Info()).ToList(), AerialSettings.Range)")
    m4 = probe.replace("opt.StraightPlugIds = CordWorldAdapter.TapIds(map);\n            Dictionary<Cell, Aerial.CellStyle> styled",
                       "Dictionary<Cell, Aerial.CellStyle> styled", 1)
    if not check_plan(m1):
        fails.append("instrument blind: pipe-pole mutation not caught")
    if m4 == probe or not check_fresh(m4, prod):
        fails.append("instrument blind: tap-clamp mutation not caught")
    if not check_cord_prints(prod.replace("pendingPrints.Add(s);", "")):
        fails.append("instrument blind: omitted offscreen print queue not caught")
    if not check_fallen_retirement(aerial.replace("tailCursors.Remove(l)", "tailCursors.ContainsKey(l)")):
        fails.append("instrument blind: retained fallen-lay cursor not caught")
    for f in fails:
        print("FAIL", f)
    print("selftest_gss_weakclose_guards:", "FAIL" if fails else "PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
