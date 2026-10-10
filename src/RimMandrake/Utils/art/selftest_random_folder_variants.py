#!/usr/bin/env python3
"""selftest_random_folder_variants.py — every picture the game can draw from a Graphic_Random folder is on the row.

Owner card 2026-10-10 ("Put them on the sheet"): Rot plant folders drew pictures the sheet never showed (CrimsonCap
b-f, Boomshroom B/C, ...) because a folder texPath matched no file and the deployed copy carried only its first
picture. Pure in-memory: a fake ledger index, no store, no game.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art_sheet as A  # noqa: E402
import refresh_sheets as RS  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


class Idx:
    def __init__(self, live, purged=()):
        self.live = {k: {"sha": v} for k, v in live.items()}
        self.variants = {v: [{"kind": "x"}] for v in live.values()}
        self.by_res = {}
        self._p = set(purged)

    def is_purged(self, s):
        return s in self._p


MOD = "src/RimMandrake/TheRot"
RES = "RotSporeKit/Things/Plant/CrimsonCap"


def main():
    live = {(MOD, f"{RES}/CrimsonCap_a.png"): "sa", (MOD, f"{RES}/CrimsonCap_b.png"): "sb",
            (MOD, f"{RES}/CrimsonCap_bm.png"): "mask_b", (MOD, f"{RES}/CrimsonCap_c_m.png"): "mask_c",
            (MOD, f"{RES}/CrimsonCap_c.png"): "sc", (MOD, f"{RES}/Sub/Deeper.png"): "deep",
            (MOD, "RotSporeKit/Things/Plant/Other/Other_a.png"): "other"}
    idx = Idx(live)
    fv = A.random_folder_variants(idx, RES)
    check(set(fv.get(MOD, {})) == {"CrimsonCap_a", "CrimsonCap_b", "CrimsonCap_c"},
          f"folder variants: every picture, masks and sub-folders excluded (got {sorted(fv.get(MOD, {}))})")
    row = A.build_row(idx, RES, {}, {})
    shas = [s for c in row["cols"] for s in c["faces"].values()]
    check({"sa", "sb", "sc"} <= set(shas), "build_row: an unshown folder picture (b, c) is a column on the row")
    check(not ({"mask_b", "mask_c", "deep", "other"} & set(shas)), "build_row: no mask, sub-folder or other folder")
    check(all(c.get("random_variant") for c in row["cols"]), "build_row: each folder column says which picture it is")
    # a picture the owner purged never comes back as a column
    row = A.build_row(Idx(live, purged={"sb"}), RES, {}, {})
    check("sb" not in [s for c in row["cols"] for s in c["faces"].values()], "build_row: a purged folder picture stays off")
    # a mod shipping a FILE at the texPath is not a folder there
    live2 = dict(live)
    live2[(MOD, f"{RES}.png")] = "single"
    check(A.random_folder_variants(Idx(live2), RES, skip_mods={MOD}) == {}, "a file at the texPath: not a folder")
    # the header line names the picture and says when it was never shown
    c = {"kind": "live", "winner": True, "random_variant": "CrimsonCap_b", "random_of": 3, "neverShown": True}
    check("NEVER SHOWN" in A._short(c) and "CrimsonCap_b" in A._short(c), "short label: in game now, never shown")
    # the refresh fingerprint sees a new picture dropped into the folder
    f1 = RS.fingerprint([["crimsoncap"]], [[RES]], Idx(live), set())
    live3 = dict(live)
    live3[(MOD, f"{RES}/CrimsonCap_d.png")] = "sd"
    f2 = RS.fingerprint([["crimsoncap"]], [[RES]], Idx(live3), set())
    check(f1 != f2, "fingerprint: a new folder picture rebuilds the sheet")
    # "never shown" is measured against the page he ruled on, and survives a rebuild of a sheet he never saved
    ruled = {"rows": {"R": {"columns": {"A": {"single": "sa"}}}}}
    check(A.shown_base("R", ruled, {"R": {"columns": {"A": {"single": "sa"}, "B": {"single": "sb"}}}}) == {"sa"},
          "shown_base: a ruled sheet's baseline is the snapshot he ruled on, not the latest build")
    check(A.shown_base("R", None, {"R": {"columns": {"B": {"single": "sb"}}, "shownBase": ["sa"]}}) == {"sa"},
          "shown_base: an unsaved sheet carries its baseline across rebuilds")
    print("ALL PASS" if not FAILS else f"{len(FAILS)} FAIL")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
