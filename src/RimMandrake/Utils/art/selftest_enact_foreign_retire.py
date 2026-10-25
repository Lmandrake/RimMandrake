#!/usr/bin/env python3
"""selftest_enact_foreign_retire.py — retire_replaced never plans the retirement of a live file whose texPath is named
only by ANOTHER def (RSW_TunnelSnake sharing RM_TunnelSnake's bytes). ENACT_KEPT_CONFLICT_FIX_PARTIAL_PLAN."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enact as E  # noqa: E402

FAILS = []


def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        FAILS.append(m)


class FakeIdx:
    def __init__(self, live):
        self.live = {k: {"sha": v} for k, v in live.items()}

    def live_anywhere(self, sha):
        return [f"{m}/Textures/{r}" for (m, r), ev in self.live.items() if ev["sha"] == sha]


def d(name, tp):
    return f"<ThingDef><defName>{name}</defName><graphicData><texPath>{tp}</texPath></graphicData></ThingDef>\n"


def main():
    with tempfile.TemporaryDirectory() as t:
        src = Path(t)
        (src / "Defs").mkdir()
        (src / "Defs" / "a.xml").write_text("<Defs>" + d("RM_Snake", "Things/Snake/RM_Snake")
                                            + d("RSW_Snake", "Things/Snake/RSW_Snake") + "</Defs>")
        E.reset_caches()
        M, M2 = "RimMandrake/A", "SWBestiary"
        idx = FakeIdx({(M, "Things/Snake/RM_Snake_east.png"): "a1", (M2, "Things/Snake/RSW_Snake_east.png"): "a1",
                       (M, "Things/Snake/RM_Snake_north.png"): "b1"})
        cols = {"A": {"east": "a1"}, "B": {"north": "b1"}}
        g = "Things/Snake/RM_Snake"
        v = {"retire": {g: ["A"]}}
        out = E.retire_replaced(idx, "RM_Snake", v, cols, {g: "B"}, set(), [], src, {"RM_Snake"})
        rels = sorted(x["rel"] for x in out)
        check(rels == ["Things/Snake/RM_Snake_east.png"], f"only the row's own copy is retired ({rels})")
        out = E.retire_replaced(idx, "RM_Snake", v, cols, {g: "B"}, set(), [])
        check(len(out) == 2, "without src the old behaviour is unchanged")
    sys.exit(1 if FAILS else 0)


main()
