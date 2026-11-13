#!/usr/bin/env python3
"""Two bridge-callable state readers for the owner-look regressions (owner_look_regressions.py rows BLOCKED ON HOOK).

  RM_Patch_MouseoverDepth.ProofPitLabel("x,z")  RIMMANDRAKE_ADD_PIT_LABEL_STATE_READER_MOUSEOVER_HAS_NONE: the readout's
      terrain line for a square, from the SAME LineAt the mouseover prefix prints (so the reader cannot drift from the screen).
  RM_SubmergeDraw.ProofOverlays("x,z")  RIMMANDRAKE_ADD_OVERLAY_PROOF_HOOK_LAW_CANNOT_SEE_ICONS (first half): per thing, the
      realtime gate's verdict (RealtimeRead, shared with BeginRealtime), the flame gate, the overlay alpha, and the floor
      cords' FloorSeen, all read only.
  RM_NorthstarProofs.ProofResetRect  RIMMANDRAKE_INVALIDATE_SWIMSET_ON_PROOF_RESET: re-derives and publishes the swim set
      whole before it returns, so a restaged pit never reads stale swum squares until the next refresh tick.
No behaviour change in play: the prefix and the gate call the extracted helpers; FloorSeen keeps its (Map, int, int) signature
(Gimme Some Slack finds it by name) and still notes the cell; the proof reads with noteIt false.

CAN IT FAIL: each wire taken out of a copy of the source must go red (run at the end).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "Source"
sys.path.insert(0, str(HERE))
from selftest_flowworks_underliquid_parity import mask_comments, method_body  # noqa: E402

FILES = {"mouse": SRC / "RM_MouseoverDepth.cs", "draw": SRC / "Superdeep" / "RM_SubmergeDraw.cs",
         "proofs": SRC / "RM_NorthstarProofs.cs"}


def checks(t: dict) -> list[tuple[str, bool]]:
    mouse, draw = mask_comments(t["mouse"]), mask_comments(t["draw"])
    prefix = method_body(mouse, r"public static void Prefix\(MouseoverReadout __instance\)")
    line_at = method_body(mouse, r"public static string LineAt\(Map map, IntVec3 c, out TerrainDef terrain, out bool polluted\)")
    label = method_body(mouse, r"public static string ProofPitLabel\(string arg\)")
    begin = method_body(draw, r"internal static bool BeginRealtime\(Thing t, DrawPhase phase\)")
    read = method_body(draw, r"internal static RealtimeVerdict RealtimeRead\(Thing t, out float share, out float levelM, out float clarity, out float h\)")
    over = method_body(draw, r"public static string ProofOverlays\(string arg\)")
    reset = method_body(mask_comments(t["proofs"]), r"public static string ProofResetRect\(string arg\)")
    seen_at = method_body(draw, r"private static float FloorSeenAt\(Map map, int x, int z, bool noteIt\)")
    return [
        ("LineAt builds the line from PitLabelAt", "PitLabelAt(c)" in line_at),
        ("the mouseover prefix prints LineAt's line", "LineAt(map, c," in prefix and "cachedTerrainString(__instance) = line;" in prefix),
        ("ProofPitLabel exists and reads LineAt", bool(label) and "LineAt(map, c," in label),
        ("ProofPitLabel reports fog as the player sees it", '"fogged"' in label),
        ("BeginRealtime decides through RealtimeRead", "RealtimeRead(t," in begin and "RM_UnderLiquid.LabelAlpha(" not in begin),
        ("RealtimeRead holds the gate (opaque top hidden, body cover, split)", "RM_UnderLiquid.LabelAlpha(" in read
         and "RealtimeVerdict.Hidden" in read and "RealtimeVerdict.BodyCover" in read and "RealtimeVerdict.Split" in read),
        ("ProofOverlays exists and reads the gate, flame and overlay", bool(over) and "RealtimeRead(t," in over
         and "OverlayAlpha(t)" in over and "flame=" in over),
        ("ProofOverlays reads cords without noting the cell", "FloorSeenAt(map, x, z, false)" in over and "submergeDrawn" not in over),
        ("FloorSeen keeps its signature and notes the cell",
         "public static float FloorSeen(Map map, int x, int z) => FloorSeenAt(map, x, z, true);" in draw
         and "if (noteIt)" in seen_at and "submergeDrawn[" in seen_at),
        ("ProofResetRect publishes the swim set whole after the release",
         "eng.RefreshDugSwim(true)" in reset and reset.find("eng.RefreshDugSwim(true)") > reset.find("ReleaseRect(")),
    ]


def run(rows) -> int:
    bad = 0
    for name, ok in rows:
        print(("PASS " if ok else "FAIL ") + name)
        bad += not ok
    return bad


def main() -> int:
    t = {k: p.read_text(encoding="utf-8") for k, p in FILES.items()}
    bad = run(checks(t))
    plants = [
        ("prefix composes its own line", "mouse", "cachedTerrainString(__instance) = line;", "cachedTerrainString(__instance) = other;"),
        ("proof notes the cell", "draw", "FloorSeenAt(map, x, z, false)", "FloorSeenAt(map, x, z, true)"),
        ("FloorSeen stops noting", "draw", "if (noteIt)", "if (false)"),
        ("gate keeps its own copy", "draw", "RealtimeVerdict v = RealtimeRead(t, out float share, out float levelM, out float clarity, out float h);",
         "RealtimeVerdict v = RM_UnderLiquid.LabelAlpha(0f, 0f, 0f) > 0 ? RealtimeVerdict.Whole : RealtimeVerdict.Hidden; float share = 0f, levelM = 0f, clarity = 0f, h = 0f;"),
        ("reset leaves the swim set stale", "proofs", "int swum = eng.RefreshDugSwim(true);", "int swum = 0;"),
        ("label proof ignores fog", "mouse", '"fogged"', '"seen"'),
    ]
    for name, key, old, new in plants:
        t2 = dict(t)
        t2[key] = t[key].replace(old, new)
        caught = t2[key] != t[key] and any(not ok for _, ok in checks(t2))
        print(("PASS " if caught else "FAIL ") + "can-fail: " + name + " goes red")
        bad += not caught
    print("RESULT", "GREEN" if not bad else "RED %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
