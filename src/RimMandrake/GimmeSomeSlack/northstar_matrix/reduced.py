"""The REDUCED live matrix (owner 2026-10-05 densification; numpy-free so python.exe can import it).

Source: design/RimMandrake/gimmesomeslack_verification_consolidation_2026-10-05.md section 2 (matrix rows) and
section 7 item 1 (floor 64 -> 16, owner-authorised 2026-10-05: "This is a full densification."). The full design
catalog (T16 x S4 floor, 109 scenes) stays behind `run_live.py --scenes full` for a design review.

  floor    64 -> 16  each T once; S and F each on exactly 4 scenes (Latin rotation); P both, V all 3, Z both also run.
                     Picked by a pair-coverage search over design_spec.floor_rows() (164 of the full set's factor pairs).
                     Lost: T x S pairs, proven offline only (C# SelfTest vs oracle, DeterminismChecks.cs floor replay).
                     The RING topology (T3) stays: D2 was RED on every ring board 2026-10-02.
  density  16 -> 4   one per n, S rotated (S is irrelevant to scale).
  aerial   18 -> 9   every N x R cell once. P (live/dead) is NOT in the scene id, so A00-A08 alone would have dropped
                     every dead-pole scene: the doc's own check ("if A09-A17 differ in a factor the id does not show,
                     rotate it into A00-A08") applied -- 4 dead + 5 live, all six P x St pairs kept.
  hose     9 -> 9    (L9 kept whole: it carries the cut validation_hose H3/H4/H5 predicates)
  controls 2 -> 1    C00 empty board kept (negative control); C01 master-off == core M7 (validation.py) -> cut.
"""

FLOOR = ["F00_T0_S0", "F04_T1_S0", "F11_T2_S3", "F13_T3_S1", "F18_T4_S2", "F21_T5_S1", "F25_T6_S1", "F30_T7_S2",
         "F33_T8_S1", "F39_T9_S3", "F42_T10_S2", "F47_T11_S3", "F51_T12_S3", "F54_T13_S2", "F56_T14_S0", "F60_T15_S0"]
DENSITY = ["D00_n1_S0", "D05_n10_S1", "D10_n100_S2", "D15_n1000_S3"]
AERIAL_PREFIX = ["A09_", "A10_", "A11_", "A12_", "A04_", "A05_", "A06_", "A07_", "A08_"]
HOSE_PREFIX = ["H0"]                        # all nine H00-H08
CONTROLS = ["C00_empty"]


def keep(scene_id):
    sid = scene_id
    return (sid in FLOOR or sid in DENSITY or sid in CONTROLS or any(sid.startswith(p) for p in AERIAL_PREFIX)
            or any(sid.startswith(p) for p in HOSE_PREFIX))


def reduce_spec(spec):
    """The same spec with only the reduced scenes; `reduced` records what was kept. Refuses if an id is missing."""
    scenes = [s for s in spec["scenes"] if keep(s["id"])]
    ids = {s["id"] for s in scenes}
    want = set(FLOOR) | set(DENSITY) | set(CONTROLS)
    missing = sorted(want - ids)
    if missing or len([s for s in scenes if s["group"] == "aerial"]) != 9 or len([s for s in scenes if s["group"] == "hose"]) != 9:
        raise SystemExit("reduced matrix: catalog does not hold the reduced ids (missing %s)" % missing)
    out = dict(spec, scenes=scenes)
    out["reduced"] = {"from": len(spec["scenes"]), "to": len(scenes),
                      "doc": "design/RimMandrake/gimmesomeslack_verification_consolidation_2026-10-05.md section 2"}
    return out
