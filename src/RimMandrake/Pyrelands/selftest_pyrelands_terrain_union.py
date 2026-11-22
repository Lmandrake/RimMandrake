#!/usr/bin/env python3
"""selftest_pyrelands_terrain_union: validation._terrain accepts a get_terrain_batch reply over overlapping rects and still
refuses a reply that read fewer cells than the rects cover.

jawa/get_terrain_batch keys its result by cell (JawaBenchTerrainTools.cs: "a cell read twice must appear in the output
once"), so over overlapping rects cellsRead is the union while cellsRequested is the summed areas. Pyrelands visit 5
(2026-11-22, ArchBig, site tile 1496): two ruin samples one cell apart overlapped by 2 cells and sc_ruins' ruins_scorched
failed 'read 88 of 90 cells' with every cell read. `--old` runs the cases against the parent's check (cellsRead ==
cellsRequested) and must fail. Offline, WSL python3."""
import os, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [H, os.path.join(H, "..", "Utils"), os.path.join(H, "..", "Utils", "modcheck")]
import validation  # noqa: E402

NAME = "selftest_pyrelands_terrain_union"
VISIT5 = "100,203,3,3;104,208,3,3;218,161,3,3;219,163,3,3;222,158,3,3;228,167,3,3;12,204,3,3;175,13,3,3;96,236,3,3;100,232,3,3"
# (rects, cellsRead the tool answers, cellsRequested it answers, want accepted)
CASES = [
    (VISIT5, 88, 90, True),            # the visit-5 site: overlap of 2, every cell read
    (VISIT5, 86, 90, False),           # two distinct cells genuinely not read
    ("0,0,3,3;10,10,3,3", 18, 18, True),   # disjoint, all read
    ("0,0,3,3;10,10,3,3", 17, 18, False),  # disjoint, one cell missing
    ("0,0,3,3;0,0,3,3", 9, 18, True),      # the same rect twice
    ("248,248,3,3", 4, 9, False),          # off the map edge: 5 cells outside, read short
]


class FakeT:
    session = object()
    upstream_failed = False

    def __init__(self, read, req):
        self.read, self.req = read, req

    def bridge_call(self, tool, **kw):
        return {"success": True, "ops": "RM_FE_DeepAsh:0,0,1,1", "cellsRead": self.read, "cellsRequested": self.req}


def accepted(rects, read, req, old=False):
    t = FakeT(read, req)
    if old:
        return read == req
    try:
        validation._terrain(t, rects)
        return True
    except validation.ExpectationFailed:
        return False


def main():
    old = "--old" in sys.argv
    bad = 0
    for i, (rects, read, req, want) in enumerate(CASES):
        got = accepted(rects, read, req, old)
        ok = got == want
        bad += not ok
        print("%s case %d: read %d of %d requested, accepted=%s want %s" % ("ok  " if ok else "FAIL", i, read, req, got, want))
    print("%s: %d of %d failed%s" % (NAME, bad, len(CASES), " (--old, the parent's check)" if old else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
