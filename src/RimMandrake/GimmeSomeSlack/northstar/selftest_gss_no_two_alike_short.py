#!/usr/bin/env python3
# selftest-timeout: 30
"""SC_no_two_cords_alike exempts cords shorter than 3 cells (owner, by card 2026-11-13: "Short cords → exempt cords shorter
than 3 cells from SC_no_two_cords_alike"; OWNER:1794594173709591776).

The row is driven through scene_rows.slack_and_shapes with a fake bridge that returns a shapetable, and a fake V.row that
keeps what was written. The shapetable's `length` is the C# length class (CordShape.Table: path length rounded to
ClassWidth), so "shorter than 3 cells" is a class below 3. Cases:
  the measured run (J20261113T075443Z-3da526: one 2-cell pair too alike, 38 pairs) -> PASS
  a too-alike pair in the 4-cell class, the 2-cell one too                         -> FAIL
  a too-alike pair in a 3-cell class (3 is not shorter than 3)                     -> FAIL
  every class under 3 cells, one too alike                                        -> UNMEASURED (nothing left to judge)
  no classes                                                                      -> UNMEASURED, HARNESS
The detail names the exempt classes, so a reader sees what was skipped. Exit 0 green, 1 red.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scene_rows  # noqa: E402


class FakeB:
    def __init__(self, classes):
        self.classes = classes

    def probe(self, what):
        if what == "slack":
            return {"strands": 3, "under115": 0}
        if what == "shapetable":
            return {"classes": self.classes}
        raise AssertionError("unexpected probe %s" % what)


class FakeV:
    @staticmethod
    def row(rows, rid, status, cls, detail):
        rows.append({"id": rid, "status": status, "class": cls, "detail": detail})


def c(length, cords, pairs, alike):
    return {"length": length, "cords": cords, "pairs": pairs, "tooAlike": alike}


MEASURED = [c(2, 4, 6, 1), c(4, 8, 28, 0), c(6, 3, 3, 0), c(8, 2, 1, 0)]
CASES = [
    ("measured run: the one alike pair is 2-cell", MEASURED, "PASS", "MOD"),
    ("4-cell pair alike", [c(2, 4, 6, 1), c(4, 8, 28, 1)], "FAIL", "MOD"),
    ("3-cell class is judged", [c(3, 3, 3, 1)], "FAIL", "MOD"),
    ("only short classes", [c(2, 4, 6, 1)], "UNMEASURED", "MOD"),
    ("no classes", [], "UNMEASURED", "HARNESS"),
]


def main():
    bad = []
    for name, classes, want, want_cls in CASES:
        rows = []
        scene_rows.slack_and_shapes(FakeB(classes), FakeV, rows)
        r = [x for x in rows if x["id"] == "SC_no_two_cords_alike"]
        got = (r[0]["status"], r[0]["class"]) if r else ("NO ROW", None)
        ok = got == (want, want_cls)
        if ok and classes and any(x["length"] < 3 for x in classes):
            det = r[0]["detail"]
            ok = isinstance(det, dict) and det.get("exemptShorterThan") == 3 and \
                sorted(x["length"] for x in det.get("exempt") or []) == sorted(x["length"] for x in classes if x["length"] < 3)
            if not ok:
                got = got + ("detail does not name the exempt classes: %s" % str(det)[:200],)
        print("%-4s %-44s want %-10s got %s" % ("ok" if ok else "BAD", name, want, got))
        if not ok:
            bad.append(name)
    print("RED: %s" % bad if bad else "GREEN: %d cases" % len(CASES))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
