#!/usr/bin/env python3
"""selftest_sheet_sibling_keeps.py — ART_SHEET_FIX_SIBLING_KEEPS_UNSEEN (Varactyl, 2026-10-21).

A row built from ONE texPath (Varactyl_m) must still show the species' other live/approved slots (Varactyl_f, a colour
variant, the desiccated corpse) as 'already approved' context, and a row whose every option is already ruled is dropped.
"""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


class FakeIdx:
    def __init__(self, live, prot, purged=()):
        self.live, self._prot, self._purged = live, set(prot), set(purged)

    def protected(self, sha):
        return [{"id": "k"}] if sha in self._prot else []

    def is_purged(self, sha):
        return sha in self._purged


def main():
    import art_sheet as A
    mod = "mods/SWBestiary"
    T = "swanimals/Varactyl/"
    live = {(mod, T + "Varactyl_m_south.png"): {"sha": "m1"},
            (mod, T + "Varactyl_f_south.png"): {"sha": "f1"}, (mod, T + "Varactyl_f_east.png"): {"sha": "f2"},
            (mod, T + "VaractylV_E_south.png"): {"sha": "e1"},
            (mod, T + "Varactyl_Dessicated.png"): {"sha": "d1"},
            (mod, "swanimals/Other/Other_south.png"): {"sha": "o1"}}
    idx = FakeIdx(live, prot={"f1", "f2", "e1"})
    slots = {T + "Varactyl_m": [{"subject": "RSW_Varactyl", "role": "body"}],
             T + "Varactyl_f": [{"subject": "RSW_Varactyl#f", "role": "body"}],
             T + "VaractylV_E": [{"subject": "RSW_Varactyl#v", "role": "body"}]}
    if not hasattr(A, "sibling_keeps"):
        check(False, "art_sheet.sibling_keeps exists (old behaviour: row shows its one slot only)")
        return
    sib = A.sibling_keeps(idx, {T + "Varactyl_m"}, ["RSW_Varactyl_m", "RSW_Varactyl"], slots)
    got = {s["label"]: s for s in sib}
    check({"Varactyl_f", "VaractylV_E", "Varactyl_Dessicated"} <= set(got), f"siblings found: {sorted(got)}")
    check("Varactyl_m" not in got and not any("Other" in s["res"] for s in sib), "own slot and other species excluded")
    check(got["Varactyl_f"]["protected"] and got["VaractylV_E"]["protected"] and not got["Varactyl_Dessicated"]["protected"],
          "protected flag follows the owner's keeps")
    check(set(got["Varactyl_f"]["faces"]) == {"south", "east"}, "all live facings of a sibling carried")
    src = (HERE / "art_sheet.py").read_text()
    check("Already approved / live art for this species" in src and "NOT options on this row" in src,
          "row markup labels siblings as context, not options")
    cols = [{"faces": {"south": "f1"}}, {"faces": {"south": "e1", "east": "f2"}}]
    check(A.all_options_ruled(cols, idx), "row whose options are all protected is dropped")
    check(not A.all_options_ruled(cols + [{"faces": {"south": "new"}}], idx), "row with one new option stays")
    check(A.all_options_ruled([{"faces": {"south": "p"}}], FakeIdx({}, [], purged={"p"})), "purged options count as ruled")
    check(not A.all_options_ruled([], idx), "row with no options is not 'ruled'")


main()
print(f"\n{'FAIL' if FAILS else 'PASS'}: {len(FAILS)} failure(s)")
sys.exit(1 if FAILS else 0)
