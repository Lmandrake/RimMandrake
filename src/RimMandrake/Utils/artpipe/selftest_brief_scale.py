#!/usr/bin/env python3
"""selftest_brief_scale.py — every artpipe brief states its subject's in-game size (ART_SHEETS_SCALE_CELLS_WIDEN_TOO_LATE).

Owner, 2026-10-14: "I note your sheets have no scale information nor cell width information, that's a problem."
The sheets are gated by art/scaled_review_gate.py; this proves the BRIEF half: fill_queue.row_to_jobs measures the
target def's draw quad and footprint through the sheets' own resolver (art/scale_panel.Resolver), stamps it on the job,
and artpiped.build_job_prompt puts it in the prompt the image model reads. The resolver runs over a SYNTHETIC def dump
(a sqlite file in the shape scale_panel reads), so the test sees fixed numbers whatever the live dump holds today.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "art"))
import artpiped  # noqa: E402
import common  # noqa: E402
import fill_queue  # noqa: E402
import scale_panel  # noqa: E402

FAILS: list[str] = []


def check(ok: bool, what: str) -> None:
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def fixture_db(path: Path) -> None:
    db = sqlite3.connect(str(path))
    db.execute("create table provenance (key text, value text)")
    db.executemany("insert into provenance values (?, ?)",
                   [("captured_utc", "2026-11-03T00:00:00Z"), ("modlist_fingerprint", "selftest")])
    db.execute("create table mods (load_order int, name text, package_id text, root_dir text)")
    db.execute("insert into mods values (0, 'Fixture', 'test.fixture', ?)", (str(path.parent / "no_such_mod"),))
    db.execute("create table defs (def_name text, def_type text, json text)")
    mcp = {"packageId": "test.fixture"}
    defs = [
        # a 10-cell creature on a wide quad: the Aiwha case
        ("RSW_TestWhale", "ThingDef", {"race": {"baseBodySize": 6}, "modContentPack": mcp}),
        ("RSW_TestWhaleKind", "PawnKindDef", {"race": "RSW_TestWhale", "modContentPack": mcp, "fileName": "x.xml",
                                              "lifeStages": [{"bodyGraphicData": {"drawSize": "(4,4)"}},
                                                             {"bodyGraphicData": {"drawSize": "(10,5)"}}]}),
        ("RM_TestStill", "ThingDef", {"category": "Building", "size": {"x": 2, "z": 3}, "modContentPack": mcp,
                                      "graphicData": {"texPath": "Things/TestStill", "drawSize": "(2,3.5)"}}),
        ("RM_TestShrub", "ThingDef", {"category": "Plant", "plant": {"visualSizeRange": "0.4~1.5"},
                                      "modContentPack": mcp,
                                      "graphicData": {"texPath": "Plants/TestShrub", "drawSize": "(2,2)"}}),
        ("RM_TestUiOnly", "ResearchProjectDef", {}),
    ]
    db.executemany("insert into defs values (?, ?, ?)", [(n, t, json.dumps({"fields": f})) for n, t, f in defs])
    db.commit()
    db.close()


def job(r, target, cw=1024, ch=512, **extra):
    row = dict(id="t_" + target, rimflow_item_id="ART_SHEETS_SCALE_CELLS_WIDEN_TOO_LATE", prompt="a subject",
               canvas_w=cw, canvas_h=ch, target_def=target, biome_neutral="1", **extra)
    return fill_queue.row_to_jobs(row, world=False, size_resolver=r)[0]


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        dbp = Path(td) / "defs.sqlite"
        fixture_db(dbp)
        r = scale_panel.Resolver(dbp)

        # 1. an animal named by its PawnKindDef: adult drawSize 10×5, measured; drawsize taken from the def
        j = job(r, "RSW_TestWhaleKind")
        s = j["in_game_size"]
        check(s["status"] == "measured" and s["quad"] == [10.0, 5.0], f"animal quad measured 10x5 (got {s})")
        check(j["drawsize"] == 10.0 and j["drawsize_from"] == "def", "blank row drawsize takes the def's 10 cells")
        p = artpiped.build_job_prompt(j)
        check("10 x 5-cell quad" in p, "prompt names the 10 x 5-cell quad")
        check("102 canvas px = 1 cell" in p, "prompt gives canvas px per cell (1024/10)")
        check(common.HUMAN_SCALE_LINE in p, "prompt carries the human-for-scale line")
        check("UNMEASURED" not in p, "a measured size never says UNMEASURED")

        # 2. a building: footprint 2×3 under a 2×3.5 quad
        j = job(r, "RM_TestStill", cw=512, ch=896)
        p = artpiped.build_job_prompt(j)
        check(j["in_game_size"].get("footprint") == [2, 3], "building footprint 2x3 recorded")
        check("2 x 3.5-cell quad" in p and "2 x 3-cell footprint" in p, "prompt names quad and footprint")

        # 3. a plant: square quad drawSize.x × visualSizeRange.max = 3
        j = job(r, "RM_TestShrub", cw=512, ch=512)
        check(j["in_game_size"].get("quad") == [3.0, 3.0], f"plant quad 3x3 (got {j['in_game_size'].get('quad')})")

        # 4. a def the dump cannot see: UNMEASURED in the brief, never a guessed number
        j = job(r, "RM_NoSuchDefSelftest", cw=256, ch=256)
        p = artpiped.build_job_prompt(j)
        check(j["in_game_size"]["status"] != "measured" and "In-game size: UNMEASURED" in p,
              "an unseen def says UNMEASURED")
        check("filing states drawSize" not in p, "a defaulted drawsize is not reported as the filing's")
        j = job(r, "RM_NoSuchDefSelftest", cw=256, ch=256, drawsize="2")
        check("filing states drawSize 2 cells" in artpiped.build_job_prompt(j), "a stated drawsize is reported as stated")

        # 5. UI-only def and no-subject art: no world size, said plainly
        j = job(r, "RM_TestUiOnly", cw=256, ch=256)
        check(j["in_game_size"]["status"] == "none" and "In-game size: none" in artpiped.build_job_prompt(j),
              "a UI-only def says it has no world size")
        row = dict(id="glyph", rimflow_item_id="X", prompt="a glyph", canvas_w=256, canvas_h=256, biome_neutral="1")
        j = fill_queue.row_to_jobs(row, no_subject="a UI glyph", world=False)[0]
        check("In-game size: none" in artpiped.build_job_prompt(j), "no-subject art says it has no world size")

        # 6. warnings: a stated drawsize that disagrees with the def, and a canvas whose aspect the quad stretches
        w = common.size_warnings({"status": "measured", "quad": [10.0, 5.0]}, {"width": 512, "height": 512}, "1")
        check(any("disagrees" in x for x in w) and any("stretch" in x for x in w), f"both mismatches warned ({w})")
        check(common.size_warnings({"status": "measured", "quad": [10.0, 5.0]}, {"width": 1024, "height": 512},
                                   "10") == [], "a matching filing warns nothing")

        # 7. an old job (filed before this change) still gets a size sentence, marked UNMEASURED
        old = {"id": "old", "prompt": "x", "canvas": {"width": 256, "height": 256}, "drawsize": 1.0}
        check("In-game size: UNMEASURED" in artpiped.build_job_prompt(old), "a pre-change job says UNMEASURED")

        # 8. no dump reachable: UNMEASURED, never an exception
        class Broken:
            def _def(self, *a):
                raise sqlite3.OperationalError("no such table: defs")
        s = common.measure_in_game_size("RSW_TestWhaleKind", resolver=Broken())
        check(s["status"] == "unmeasured" and "UNMEASURED" in s["source"], "a broken dump yields UNMEASURED")

        # 9. the PRODUCTION path: no size_resolver argument and world left at its default (the real art/subject.World),
        #    as fill_queue's CLI files a row. The size must come from common._size_resolver() — here pointed at the
        #    fixture dump — never be skipped as 'sizing not run' (blind-check mutant, gen 3).
        saved = common._SIZE_RESOLVER
        common._SIZE_RESOLVER = r
        try:
            row = dict(id="t_default", rimflow_item_id="ART_SHEETS_SCALE_CELLS_WIDEN_TOO_LATE", prompt="a subject",
                       canvas_w=1024, canvas_h=512, target_def="RSW_TestWhaleKind", biome_neutral="1")
            j = fill_queue.row_to_jobs(row)[0]
            s = j["in_game_size"]
            check(s.get("status") == "measured" and s.get("quad") == [10.0, 5.0],
                  f"default-path filing (no resolver, default world) measures the 10x5 quad (got {s})")
            p = artpiped.build_job_prompt(j)
            check("10 x 5-cell quad" in p and "UNMEASURED" not in p,
                  "default-path brief names the measured quad, not UNMEASURED")
        finally:
            common._SIZE_RESOLVER = saved
        r.db.close()
    print(f"RESULT: {'FAIL' if FAILS else 'PASS'} ({len(FAILS)} failing)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
