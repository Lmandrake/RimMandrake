#!/usr/bin/env python3
"""RIMMANDRAKE_FIX_DRAFTED_MOVE_IN_BIG_PIT_WALKS_SOUTH (offline, no game).

The owner, 2026-11-13: "when you click on a drafted pawn to go to a place in a large pit like this: it shows you where you
can go correctly, but then they go to a different place usually more south than intended." 1.6's drafted right-click goes
through MultiPawnGotoController (RecomputeDestinations -> dests; Draw puts an UNSUNK ghost on each dest; IssueGotoJobs sends
the pawn to that dest), so the pawn reached the previewed square and was then drawn its pit sink further south. The
PIT_CLICK_FIX_SHIFTED_ONE_DOWN remap covered only the float menu (FloatMenuOptionProvider_DraftedMove.GetSingleOption).
Reads the comment-blanked RM_PitDepthDraw.cs and checks:
  1  a RecomputeDestinations postfix, gated by pitDepthDrawOffsetEnabled, rewrites each valid dest through DrawnRowCell;
  2  DrawnRowCell picks the row with RM_PitDrawMath.PickRowForDrawnClick over RestingSinkAt, aiming at the pointed square's
     centre (c.z + 0.5f), and keeps a row only if standable, unclaimed and reachable, else falls back toward c;
  3  a Draw prefix draws the ghost AND its circle sunk by RestingSinkAt on the dest, and leaves vanilla's draw alone when
     no dest is sunk (return true);
  4  the float-menu remap is still there.
Named MUTANTS must each turn a check red. NOT proven here: the live walk (pawn.Position == the previewed dest, drawn where
the ghost stood), which is the item's in-game acceptance read.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CS = os.path.join(HERE, "Source", "Superdeep", "RM_PitDepthDraw.cs")


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def body_of(src, sig):
    i = src.find(sig)
    if i < 0:
        return ""
    j = src.find("{", i)
    d = 0
    for k in range(j, len(src)):
        d += {"{": 1, "}": -1}.get(src[k], 0)
        if d == 0:
            return src[j:k + 1]
    return ""


def checks(t):
    fails = []

    def check(n, ok, why):
        if not ok:
            fails.append("%s: %s" % (n, why))

    post = body_of(t, "public static void Postfix(RimWorld.MultiPawnGotoController __instance)")
    check(1, "[HarmonyPatch(typeof(RimWorld.MultiPawnGotoController), nameof(RimWorld.MultiPawnGotoController.RecomputeDestinations))]" in t
          and "if (!RimMandrakeFlowWorksSettings.pitDepthDrawOffsetEnabled)" in post
          and "dests[i] = DrawnRowCell(p, dests[i], dests);" in post, "RecomputeDestinations postfix rewrites each dest")
    cell = body_of(t, "internal static IntVec3 DrawnRowCell(Pawn p, IntVec3 c,")
    check(2, "RM_PitDrawMath.PickRowForDrawnClick(c.z, c.z + 0.5f," in cell and "RM_Patch_PitDepthDrawOffset.RestingSinkAt(p, q)" in cell
          and "n.Standable(map) && !taken.Contains(n) && p.CanReach(n, PathEndMode.OnCell, Danger.Deadly)" in cell
          and "n.z > c.z; n.z--" in cell and cell.rstrip("} \n\t").endswith("return c;"),
          "DrawnRowCell aims at the pointed square's centre, keeps only a standable, free, reachable row, else c")
    pre = body_of(t, "public static bool Prefix(RimWorld.MultiPawnGotoController __instance)")
    check(3, "[HarmonyPatch(typeof(RimWorld.MultiPawnGotoController), nameof(RimWorld.MultiPawnGotoController.Draw))]" in t
          and "float sink = RM_Patch_PitDepthDrawOffset.RestingSinkAt(pawn, c);" in pre
          and pre.count("-= sink;") == 2 and "if (!sunk)\n\t\t\t{\n\t\t\t\treturn true;" in pre
          and "RenderPawnAt(at, Rot4.South)" in pre, "the ghost and its circle drawn sunk; vanilla when nothing is sunk")
    check(4, "[HarmonyPatch(typeof(RimWorld.FloatMenuOptionProvider_DraftedMove), \"GetSingleOption\")]" in t
          and "RM_PitDrawMath.PickRowForDrawnClick(c.z, context.clickPosition.z" in t, "the float-menu remap stays")
    return fails


MUTANTS = [
    ("postfix ungated", "if (!RimMandrakeFlowWorksSettings.pitDepthDrawOffsetEnabled)\n\t\t\t{\n\t\t\t\treturn;\n\t\t\t}\n\t\t\tSystem.Collections.Generic.List<Pawn> pawns = PawnsRef",
     "System.Collections.Generic.List<Pawn> pawns = PawnsRef"),
    ("dests not rewritten", "dests[i] = DrawnRowCell(p, dests[i], dests);", "DrawnRowCell(p, dests[i], dests);"),
    ("aims at the square's south edge", "PickRowForDrawnClick(c.z, c.z + 0.5f,", "PickRowForDrawnClick(c.z, c.z + 0f,"),
    ("a wall square kept", "n.Standable(map) && !taken", "!taken"),
    ("two pawns on one square", "&& !taken.Contains(n) &&", "&&"),
    ("unreachable row kept", " && p.CanReach(n, PathEndMode.OnCell, Danger.Deadly)", ""),
    ("ghost left unsunk", "\t\t\t\t\tat.z -= sink;\n", ""),
    ("circle left unsunk", "\t\t\t\t\tpos.z -= sink;\n", ""),
    ("vanilla draw skipped outside pits", "if (!sunk)\n\t\t\t{\n\t\t\t\treturn true;", "if (!sunk)\n\t\t\t{\n\t\t\t\treturn false;"),
    ("float-menu remap gone", "[HarmonyPatch(typeof(RimWorld.FloatMenuOptionProvider_DraftedMove), \"GetSingleOption\")]", ""),
]


def main():
    if not os.path.isfile(CS):
        print("FAIL missing %s" % CS)
        return 1
    raw = open(CS, encoding="utf-8").read()
    fails = checks(strip_comments(raw))
    for name, a, b in MUTANTS:
        if a not in raw:
            fails.append("CAN-IT-FAIL: mutant '%s' no longer applies (source moved: update the mutant)" % name)
        elif not checks(strip_comments(raw.replace(a, b, 1))):
            fails.append("CAN-IT-FAIL: mutant '%s' passed every check" % name)
    for f in fails:
        print("FAIL", f)
    print("PASS selftest_flowworks_drafted_move_pit (4 checks, %d mutants red)" % len(MUTANTS) if not fails else "FAILED %d" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
