#!/usr/bin/env python3
"""selftest_facing_truth_gate.py — the art-eval runner holds a creature's facing set to the facing-scale truth.

Player truth: a creature is drawn the same size from every side and does not hop up or down when it turns
(facing_scale_lint.py, the gate that was green 2026-11-01). The 2026-11-05 facing redraw batch installed sets the
models judged ACCEPT that the gate then flagged (RM_Heemin, RM_Vizhik, RM_Murrin, ...: 15 of 16 open flags on
2026-11-13 were installed after the green gate). So runner.evaluate() runs the gate's own check on the candidate set
BEFORE any model call and sends a failing set back to redraw with the numbers (RIMMANDRAKE_EXTEND_PLAYER_TRUTH_SWEEP_LADDER_WAS_ONE),
the way 029034d0ef baked "a hung ladder meets its drawn wall face" into the submerge fix.

Synthetic PNGs, a stubbed reviewer and a stubbed def context: no models, no game, ~2 s.

    python3 src/RimMandrake/Utils/art_eval/selftest_facing_truth_gate.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import policy as P  # noqa: E402
import runner  # noqa: E402

FAILS: list[str] = []


def check(name, ok, detail=None):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else f"  -- {detail}"))
    if not ok:
        FAILS.append(name)


def body(path: Path, w: int, h: int, bottom: int, canvas: int = 256):
    """An opaque blob w x h px whose lowest row is `bottom`, centred, on a transparent canvas."""
    im = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    x0 = (canvas - w) // 2
    ImageDraw.Draw(im).ellipse([x0, bottom - h, x0 + w, bottom], fill=(120, 90, 60, 255), outline=(0, 0, 0, 255), width=3)
    im.save(path)
    return str(path)


class Good(runner.Reviewers):
    """Every model says GOOD; records whether it was asked at all."""
    def __init__(self):
        self.asked = 0

    def opus(self, prompt, card_dir):
        self.asked += 1
        card = json.loads((card_dir / "card.json").read_text())
        items = P.checklist_for(P.load_template("creature"), card.get("module", ""), P.card_facts(card))
        return json.dumps({"schema": "rm-art-eval/opus@v1", "subject": card["subject"], "observed": {},
                           "checklist": {i["id"]: {"status": "ok", "seen": "-"} for i in items},
                           "findings": [], "overall": "good"}), {"models_reported": ["stub-opus"]}

    def gpt(self, prompt, images, work):
        return "", {"error": "stub: not reached"}

    def regen(self, prompt, work):
        raise AssertionError("a model regen prompt is never asked for a deterministic facing-truth refusal")


def main() -> int:
    pol = P.load_policy()
    settings = {"max_regen_rounds": 3, "min_refute_evidence_chars": 15}
    real_ctx = getattr(runner, "facing_context", None)
    with tempfile.TemporaryDirectory() as t:
        td = Path(t)
        east = body(td / "e.png", 200, 80, 200)
        sets = {
            "level": {"east": east, "south": body(td / "s1.png", 90, 80, 200), "north": body(td / "n1.png", 90, 78, 200)},
            "tall_south": {"east": east, "south": body(td / "s2.png", 90, 150, 200), "north": body(td / "n2.png", 90, 78, 200)},
            "south_hops": {"east": east, "south": body(td / "s3.png", 90, 80, 150), "north": body(td / "n3.png", 90, 78, 200)},
        }

        def spec(kind, tex="Things/Pawn/Animal/RM_TruthProbe/RM_TruthProbe"):
            return {"subject": f"RM_TruthProbe__{kind}", "label": "truth probe", "template": "creature",
                    "module": "walker", "description": "a soft round probe creature", "target_texpath": tex,
                    "images": dict(sets[kind], scale=east)}

        ctx = {"view": "elevation", "plan": "blob"}
        runner.facing_context = lambda s: (ctx["view"], ctx["plan"], "stub")

        def run(kind, rounds=None, **kw):
            rev = Good()
            rec = runner.evaluate(spec(kind, **kw), td / f"card_{kind}_{len(FAILS)}", rev, pol, settings, {},
                                  rounds or {})
            return rec, rev

        rec, rev = run("tall_south")
        check("a south drawn ~1.9x east's height is refused before any model call (REGEN F_FACING_TRUTH)",
              rec["decision"] == "REGEN" and rev.asked == 0 and (rec.get("regen") or {}).get("findings") == ["F_FACING_TRUTH"],
              (rec.get("decision"), rev.asked, rec.get("regen"), rec.get("reasons")))
        req = ((rec.get("regen") or {}).get("request") or {}).get("prompt", "")
        check("the redraw request carries the measured fix (which facing, how far off)", "south" in req and "east" in req, req)

        rec, rev = run("south_hops")
        check("a south whose feet sit 0.2 of the canvas above east's is refused (the creature hops when it turns)",
              rec["decision"] == "REGEN" and rev.asked == 0 and "feet" in json.dumps(rec.get("facing_truth")),
              (rec.get("decision"), rev.asked, rec.get("facing_truth")))

        rec, rev = run("level")
        check("must stay green: a level, same-height set goes on to the models and is accepted",
              rec["decision"] == "ACCEPT" and rev.asked == 1 and (rec.get("facing_truth") or {}).get("verdict") == "ok",
              (rec.get("decision"), rev.asked, rec.get("facing_truth"), rec.get("reasons")))

        rec, rev = run("tall_south", rounds={"RM_TruthProbe__tall_south": 3})
        check("at the round cap a failing set escalates instead of redrawing forever",
              rec["decision"] == "ESCALATE" and rev.asked == 0, (rec.get("decision"), rec.get("reasons")))

        ctx["view"] = "topdown"
        rec, rev = run("tall_south")
        check("must stay green: a picture that is not ours (topdown view) is outside the gate, as in facing_scale_lint gate",
              rev.asked == 1 and rec["decision"] == "ACCEPT", (rec.get("decision"), rev.asked))
        ctx["view"] = "elevation"

        waived = next(iter(json.loads((runner.FACING_WAIVERS).read_text()))) if hasattr(runner, "FACING_WAIVERS") else "none"
        rec, rev = run("tall_south", tex=waived)
        check("must stay green: a texPath with a recorded waiver (facing_scale_waivers.json) is not refused",
              rev.asked == 1 and rec["decision"] == "ACCEPT", (waived, rec.get("decision"), rev.asked))

        # a spec with no target_texpath (458 of 1241 committed creature records): the texPath comes from an installed
        # facing beside the candidate, else the def's one texPath; never a silent skip
        runner._creature_texpaths = lambda: {}
        inst = td / "Textures/Things/Pawn/Animal/RM_TruthProbe"
        inst.mkdir(parents=True)
        sets["installed_east"] = dict(sets["tall_south"], east=body(inst / "RM_TruthProbe_east.png", 200, 80, 200))
        sp = spec("installed_east"); sp.pop("target_texpath")
        rev = Good()
        rec = runner.evaluate(sp, td / "card_noTT", rev, pol, settings, {}, {})
        check("no target_texpath, east installed under Textures/: the texPath is read off it and the set is refused",
              rec["decision"] == "REGEN" and rev.asked == 0
              and (rec.get("facing_truth") or {}).get("texpath") == "Things/Pawn/Animal/RM_TruthProbe/RM_TruthProbe",
              (rec.get("decision"), rec.get("facing_truth")))
        sp = spec("tall_south"); sp.pop("target_texpath")
        rev = Good()
        rec = runner.evaluate(sp, td / "card_noTT2", rev, pol, settings, {}, {})
        check("no target_texpath and no def texPath: UNMEASURED in the reasons, judged by the models",
              rev.asked == 1 and any("UNMEASURED" in r and "texPath" in r for r in rec.get("reasons", [])), rec.get("reasons"))
        runner._creature_texpaths = lambda: {"RM_TruthProbe": ["Things/Pawn/Animal/RM_TruthProbe/RM_TruthProbe"]}
        rev = Good()
        rec = runner.evaluate(sp, td / "card_noTT3", rev, pol, settings, {}, {})
        check("no target_texpath but the def draws one texPath: that texPath is judged and the set refused",
              rec["decision"] == "REGEN" and rev.asked == 0, (rec.get("decision"), rec.get("facing_truth")))

        check("a per-view subject (RM_Foo_ns, RM_Foo__dessicated_n) is judged with RM_Foo's body plan; a real _j def stays",
              runner.subject_def("RM_TruthProbe_ns") == "RM_TruthProbe" and runner.subject_def("RM_TruthProbe__x_n") == "RM_TruthProbe"
              and runner.subject_def("RM_TruthProbe_j") == "RM_TruthProbe_j",
              [runner.subject_def(x) for x in ("RM_TruthProbe_ns", "RM_TruthProbe__x_n", "RM_TruthProbe_j")])

        runner.facing_context = lambda s: (None, None, "def has no live texture")
        rec, rev = run("tall_south")
        check("an unresolvable view/plan reads UNMEASURED in the reasons and never blocks",
              rev.asked == 1 and any("UNMEASURED" in r for r in rec.get("reasons", [])), rec.get("reasons"))

        if real_ctx is not None:
            runner.facing_context = real_ctx
            view, plan, why = runner.facing_context({"subject": "RM_Heemin__x",
                                                    "target_texpath": "Things/Pawn/Animal/RM_Heemin/RM_Heemin"})
            check("the real context resolves an installed creature of ours (RM_Heemin: elevation, serpent)",
                  view == "elevation" and plan == "serpent", (view, plan, why))
        else:
            check("the real context resolves an installed creature of ours (RM_Heemin: elevation, serpent)", False,
                  "runner.facing_context missing")
    print(f"{'FAIL' if FAILS else 'PASS'}: {len(FAILS)} failing")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
