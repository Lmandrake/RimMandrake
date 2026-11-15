#!/usr/bin/env python3
"""Offline half of sc_cords_under_items (GimmeSomeSlack 0.1.0, bar cords_draw_under_things, owner by card 2026-11-14). No game:
the scene's entry imports and is wired (validation.scene_cords_under_items, scene_rows.cords_under_items in proof_all's scenes
block, the probe verb under: in GimmeSomeSlackProbe.cs), and its verdict reads planted probe answers the right way: a thing
drawn above the cord PASSes; a cord drawn above an item, a battery queued under the strand, a cell with no cord and a junction
cell with no piece do not. The live half is UNRUN until Stage 6:
    python.exe src\\RimMandrake\\GimmeSomeSlack\\northstar\\proof_all.py --live --no-shots
    python3 src/RimMandrake/GimmeSomeSlack/validation.py --scenes-from <proof result json>

    python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_cords_under_items.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import scene_rows  # noqa: E402
import validation  # noqa: E402


def read(things, strands=1, pieces=0, alt=0.1, sq=2000, pq=2001):
    return {"success": True, "cord": {"strands": strands, "pieces": pieces, "altitude": alt, "strandQueue": sq, "pieceQueue": pq, "seen": 1},
            "things": [dict(zip(("def", "altitude", "queue"), t)) for t in things] + [{"def": "PowerConduit", "altitude": 0.05, "queue": 2000}]}


def main():
    fails = []

    def check(ok, msg):
        print(("ok   " if ok else "FAIL ") + msg)
        if not ok:
            fails.append(msg)

    src = open(os.path.join(os.path.dirname(HERE), "Source", "GimmeSomeSlackProbe.cs"), encoding="utf-8").read()
    check(callable(getattr(validation, "scene_cords_under_items", None)), "validation.scene_cords_under_items exists")
    check(callable(getattr(scene_rows, "cords_under_items", None)), "scene_rows.cords_under_items exists")
    check("cords_under_items(B, V, rows)" in open(scene_rows.__file__, encoding="utf-8").read().split("def run(", 1)[1].split("\ndef ", 1)[0],
          "proof_all's scenes block (scene_rows.run) stages it")
    check('cmd.StartsWith("under:")' in src and "UnderAt(" in src, "the probe answers under:x,z")
    check(all(r in scene_rows.ROWS for r in scene_rows.UNDER_ROWS), "its rows are declared in scene_rows.ROWS")
    st = scene_rows.under_verdict(read([("Battery", 0.6, 2450)]))[0]
    check(st == "PASS", "a battery above the cord passes (%s)" % st)
    st = scene_rows.under_verdict(read([("Steel", 0.05, 2450)], alt=0.1))[0]
    check(st == "FAIL", "planted: a cord drawn above a steel stack fails (%s)" % st)
    st = scene_rows.under_verdict(read([("Battery", 0.6, 1990)]))[0]
    check(st == "FAIL", "planted: a battery queued before the strand fails (%s)" % st)
    st = scene_rows.under_verdict(read([("Bed", 0.6, 2450)], strands=0))[0]
    check(st == "UNMEASURED", "a cell with no cord is unmeasured, never a pass (%s)" % st)
    st = scene_rows.under_verdict(read([("Steel", 0.4, 2450)]), want_piece=True)[0]
    check(st == "UNMEASURED", "a junction cell with no piece is unmeasured (%s)" % st)
    st = scene_rows.under_verdict(read([("Steel", 0.4, 2000)], pieces=1, pq=2001), want_piece=True)[0]
    check(st == "FAIL", "planted: a junction piece queued after the steel fails (%s)" % st)
    st = scene_rows.under_verdict({"success": False})[0]
    check(st == "UNMEASURED", "no probe reading is unmeasured (%s)" % st)
    rows = [{"id": r, "status": "PASS"} for r in scene_rows.UNDER_ROWS]
    st, _ = validation.scene_verdict("sc_cords_under_items", rows, want=list(scene_rows.UNDER_ROWS))
    check(st == "PASS", "the scene passes when every row passes (%s)" % st)
    st, _ = validation.scene_verdict("sc_cords_under_items", rows[:-1], want=list(scene_rows.UNDER_ROWS))
    check(st == "UNMEASURED", "a missing row (the pit) leaves the scene unmeasured (%s)" % st)
    # the scenes.json entry (written 2026-11-14 for his card "the cords bar gets a scene"): contract-valid, its own rows decide it
    import json
    repo = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
    concept = os.path.join(repo, "design", "concepts", "GimmeSomeSlack")
    sys.path.insert(0, os.path.join(repo, "src", "RimMandrake", "rimflow"))
    import concept_tree  # noqa: E402
    import designer_stage  # noqa: E402
    scn = json.load(open(os.path.join(concept, "scenes.json"), encoding="utf-8"))
    mine = [s for s in scn["scenes"] if s.get("id") == "sc_cords_under_items"]
    check(len(mine) == 1, "scenes.json holds sc_cords_under_items once (%d)" % len(mine))
    errs = designer_stage.scene_errors(scn, concept_tree.load(concept), repo)
    check(not errs, "scenes.json with the entry meets the scene contract against the tree (%s)" % "; ".join(errs))
    check(designer_stage.entry_point_exists(repo, (mine or [{}])[0].get("entry_point")), "its entry point is in validation.py")
    check(validation.scene_rows_for("sc_cords_under_items") == list(scene_rows.UNDER_ROWS),
          "its verdict reads UNDER_ROWS only, not every drawing_true_to_grid row")
    check(any(c.get("capability") == "cords_draw_under_things" and "sc_cords_under_items" in c.get("by", [])
              for c in scn.get("coverage_rest") or []), "coverage_rest covers cords_draw_under_things by it")
    bad = dict(mine[0], control={"case": "x"}) if mine else {}
    check(bool(designer_stage.scene_errors({"scenes": [bad]}, None, repo)), "planted: the entry without a full control is refused")
    print("FAIL" if fails else "PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
