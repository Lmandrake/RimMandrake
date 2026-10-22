#!/usr/bin/env python3
"""selftest_sheet_corpse_lanes.py — a corpse render a sheet NAMES (--jobs dessic_*) gets its own lane.

Owner, 2026-10-22, on picks_dessicated_sheet_2026-10-19 (built from 58 dessic_* jobs, DESSICATED_CORPSES_REDRAW_ONE_BY_ONE):
*"I just did picks 1 of 3: dessicated corpses... and yet I saw not a single dessicated corpse."* NOT_BODY_JOB kept every
corpse render off the body lane (right) and nothing put it anywhere else (wrong): the rows showed only the living body.

  corpse_lane_texpaths  a named job whose family is a corpse job and whose target_texpath is a corpse texture opens that
                        texture's lane; body jobs, unknown jobs and lanes the row already has open none
  build_row             on a corpse texture's own lane, the corpse renders joined by name are the candidates
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import art_sheet as AS  # noqa: E402

FAILS: list[str] = []


def check(ok: bool, what: str) -> None:
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


class _Idx:
    """The two things build_row reads for artpipe columns, plus no history."""
    def __init__(self, variants):
        self.variants = variants
        self.live = {}

    def is_purged(self, sha):
        return False


def main() -> int:
    AS._FAM_TEX = {"dessic_akk_dessicated_v1": "swanimals/Akk/Akk_Dessicated",
                   "dessic_frogdog_dessicated_v1": "swanimals/FrogDog/FrogDog_Dessicated",
                   "regen_akk_v2": "swanimals/Akk/Akk"}
    AS._FAM_SLOTS = {}
    got = AS.corpse_lane_texpaths(["dessic_akk_dessicated_v1", "regen_akk_v2_east", "nope_v1"])
    check(got == ["swanimals/Akk/Akk_Dessicated"], "a named dessic job opens its corpse texture's lane; body jobs do not")
    check(AS.corpse_lane_texpaths(["dessic_frogdog_dessicated_v1_east", "dessic_frogdog_dessicated_v1_north"])
          == ["swanimals/FrogDog/FrogDog_Dessicated"], "per-facing jobs of one family open ONE lane")
    check(AS.corpse_lane_texpaths(["dessic_akk_dessicated_v1"], {"swanimals/Akk/Akk_Dessicated"}) == [],
          "a lane the row already has is not opened twice")
    AS._FAM_TEX.update({"taozin_split_grub_v1": "Things/Pawn/Animal/RSW_TaozinGrub/RSW_TaozinGrub",
                        "donorart_taozin_j_v1": "swanimals/Taozin/Taozin_j", "donorart_taozin_v1": "swanimals/Taozin/Taozin",
                        "donorport_kaadu_v1": "swanimals/Kaadu/Kaadu"})
    check(AS.filed_for_other_texture("taozin_split_grub_v1", "RSW_Taozin"), "a grub render is not the adult's (Taozin)")
    check(AS.filed_for_other_texture("donorart_taozin_j_v1", "RSW_Taozin"), "a _j render is not the adult's")
    check(not AS.filed_for_other_texture("donorart_taozin_v1", "RSW_Taozin"), "the adult's own render (old path) stays")
    check(not AS.filed_for_other_texture("donorport_kaadu_v1", "Kaadu_m"), "a sexless render stays on a sexed lane")
    check(not AS.filed_for_other_texture("unknown_v1", "RSW_Taozin"), "a job with no target_texpath stays")
    # build_row on the corpse lane keeps the corpse render joined by name; the body lane still drops it
    v = {"kind": "artpipe", "job": "dessic_akk_dessicated_v1", "facing": "?", "date": "2026-10-16", "prompt": "p",
         "res": None}
    idx = _Idx({"a" * 64: [v]})
    orig_live, orig_fc = AS._live_res, AS.failed_canon_jobs
    AS._live_res = lambda _i: set()
    AS.failed_canon_jobs = lambda: set()
    try:
        def fams(res):
            try:
                br = AS.build_row(idx, res, {}, {})
            except Exception as e:          # a fixture gap is a FAIL with its reason, never a crash
                check(False, f"build_row({res}) ran: {e!r}")
                return set()
            return {c.get("label") for c in br["cols"] if c.get("kind") == "artpipe"}
        check(any("dessic_akk_dessicated_v1" in (x or "") for x in fams("swanimals/Akk/Akk_Dessicated")),
              "the corpse lane shows the corpse render")
        check(not any("dessic_akk" in (x or "") for x in fams("swanimals/Akk/Akk")),
              "the body lane still keeps the corpse render off")
    finally:
        AS._live_res, AS.failed_canon_jobs = orig_live, orig_fc
        AS._FAM_TEX = AS._FAM_SLOTS = None
    print(f"\n{'ALL PASS' if not FAILS else f'{len(FAILS)} FAILED'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
