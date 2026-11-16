#!/usr/bin/env python3
"""coverage_calibration.py - the coverage judge's planted cases (RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS).

A gate is only a gate if its judge is trustworthy both ways (his card 2026-11-14, spec Q7 "Keep both"). This is the
`model_check` of the `coverage_judge` row in infrastructure/state/judge_calibration.json: it stages small planted concepts
in a temp tree (the real role files copied in), puts each to the coverage judge with its real prompt and schema
(coverage_judge.prompt, SCHEMA, MODEL), and writes one result row per case to $RM_CALIBRATION_RESULTS:

  good_lanterns           every capability and leaf has a contract scene and the flagship showcase is his pick ->
                          must pass. It also plants the noise kinds an independent read found in Pyrelands round 6
                          (g17, g18: a gap that asks for documentation or another showcase and names no wrong behaviour
                          a check would accept): the sheet does not restate each scene's thresholds and there is one
                          showcase only. A judge that refuses on those is not calibrated.
  bad_leaf_no_scene       the oil leaf and its capability have no scene -> must be refused
  bad_scene_no_control    the light scene has no control and no asserted start -> must be refused

It spends (one Opus judge per case, each capped at CASE_BUDGET_USD): it runs only from
`refusal_contract.py calibrate --model coverage_judge`, never on a schedule.

    python3 src/RimMandrake/rimflow/coverage_calibration.py run        judge every case, print one line each
    python3 src/RimMandrake/rimflow/coverage_calibration.py stage <dir>  write the planted concepts there, judge none
"""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import coverage_judge as CJ  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ROLES = ("src/RimMandrake/rimflow/roles/designer_scene_contract.md", "src/RimMandrake/rimflow/roles/designer_lock.md")
CASE_BUDGET_USD = 1.25
CASE_TIMEOUT_S = 1200

LEAF = {"by": "concept", "root": ["lantern_root"], "leaf_kind": "experience", "clause_kind": "preserve",
        "tier_proposed": "live", "owner_part": "lantern_root"}
BASE = {
    "sheet.md": "# Lanterns: a hanging lantern lights a small room and needs oil\n\n## his words\n"
                "- 2026-11-01: \"A lantern should light the room around it, and go out when it runs dry.\" OWNER:1\n"
                "- 2026-11-02, the face: \"Show me a lantern lighting a dark room and then going out.\" OWNER:2\n\n"
                "## does\n- [leaf:light] At night a lit lantern lights the cells around it\n"
                "- [leaf:oil_out] A lantern nobody refuels goes dark when its oil is gone\n\n"
                "## does not\n- No colour, no heat, no fire risk: a lantern is light and an oil counter only\n",
    "tree.json": {"schema_version": 1, "subject": "Lanterns", "kind": "mod", "authored_by": "concept",
                  "root_ref": "design/validation_walks/RimMandrake/Lanterns.md#north-star", "root_state": "VALIDATED",
                  "waived": [], "advisory": [], "exam_waived": None,
                  "leaves": [dict(LEAF, id="light",
                                  experience="At night the player sees the cells within two of a lit lantern lit",
                                  scenario="a dark roofed room at midnight, one fuelled lantern hung in its centre",
                                  false_pass=["light measured in daylight or from another lamp"],
                                  red="a lantern that reads lit and leaves its cells dark"),
                             dict(LEAF, id="oil_out",
                                  experience="A lantern left unfuelled goes dark once its last oil is burnt",
                                  scenario="a lit lantern with exactly one oil left, a day passing",
                                  false_pass=["a lantern that goes dark at dawn whatever its oil"],
                                  red="a lantern that burns forever on an empty tank")]},
    "record.json": {"mod": "Lanterns", "packageId": "mandrake.rm.lanterns", "scope": [],
                    "decisions": [{"id": "d_flagship", "kind": "ruling", "speaker": "owner", "source": "OWNER:2",
                                   "date": "2026-11-02", "what": "the flagship: a lantern lighting a dark room, then going "
                                   "out", "flagship": "lantern_night"}],
                    "asks": [],
                    "inventory": [{"id": "inv_light", "what": "A lit lantern raises light to at least 50% on every cell "
                                   "within 2 cells of it", "impl": "present", "impl_evidence": [
                                       "src/RimMandrake/Lanterns/Source/CompLanternGlow.cs"], "proof": "current",
                                   "scope": "approved", "source": ["OWNER:1"]},
                                  {"id": "inv_oil", "what": "A lit lantern burns one oil per day; at zero oil it goes "
                                   "dark", "impl": "present", "impl_evidence": [
                                       "src/RimMandrake/Lanterns/Source/CompLanternFuel.cs"], "proof": "current",
                                   "scope": "approved", "source": ["OWNER:1"]}]},
    "scenes.json": {"scenes": [
        {"id": "sc_light", "kind": "acceptance", "requirement": ["light"], "staged_by": "script",
         "entry_point": "src/RimMandrake/Lanterns/validation.py::scene_light",
         "start": ["quicktest map at midnight, a 7x7 roofed room with no other light source: glow 0 on every room cell "
                   "(asserted)", "one lantern with 3 oil hung at the room's centre, unlit (asserted)"],
         "action": "light the lantern and wait 60 ticks",
         "expect": "glow is at least 50% on every cell within 2 cells of the lantern and at most 10% at 3 cells",
         "control": {"case": "the same room with the same lantern hung but holding 0 oil, ordered lit",
                     "expect": "glow stays 0 on every room cell",
                     "rules_out": "light from the room, the time of day or another source rather than the burning lantern"},
         "restore": "destroy the quicktest map; nothing persistent changed", "hold": "immediate"},
        {"id": "sc_oil_out", "kind": "acceptance", "requirement": ["oil_out"], "staged_by": "script",
         "entry_point": "src/RimMandrake/Lanterns/validation.py::scene_oil_out",
         "start": ["the sc_light room, the lantern lit with exactly 1 oil (asserted)",
                   "a second room alike with a lantern lit with 2 oil (asserted)"],
         "action": "advance one day and one hour",
         "expect": "the first lantern holds 0 oil and its cells read glow 0",
         "control": {"case": "the second lantern, advanced the same day and hour",
                     "expect": "it holds 1 oil and its cells still read at least 50% within 2 cells",
                     "rules_out": "the lantern going dark from elapsed time or the day cycle rather than an empty tank"},
         "restore": "destroy the quicktest map; nothing persistent changed", "hold": "immediate"}],
        "showcases": [{"id": "lantern_night", "scenes": ["sc_light", "sc_oil_out"], "exercises": ["inv_light", "inv_oil"],
                       "source": ["OWNER:2"], "decision": "d_flagship"}],
        "coverage_rest": []},
    "floor.json": {"lines": {"log": {"status": "applicable"}, "mod_settings": {"status": "applicable"},
                             "flight": {"status": "not_applicable", "evidence": "a lantern does not fly"},
                             "biome_scope": {"status": "not_applicable", "evidence": "the mod adds no BiomeDef"}}},
    "exam.json": {"scenarios": [
        {"id": "e1", "text": "A lit lantern in a dark room leaves the cell next to it dark.", "expect": "reject: leaf light",
         "expect_source": "leaf:light"},
        {"id": "e2", "text": "A lantern with oil left goes dark at dawn.", "expect": "reject: leaf oil_out",
         "expect_source": "leaf:oil_out"}],
        "reader_verdicts": {"reader1": {"e1": {"verdict": "reject", "leaf": "light"},
                                        "e2": {"verdict": "reject", "leaf": "oil_out"}}}},
}


def _no_oil_scene(c):
    s = c["scenes.json"]
    s["scenes"] = [x for x in s["scenes"] if x["id"] != "sc_oil_out"]
    s["showcases"][0].update(scenes=["sc_light"], exercises=["inv_light"])


def _no_control(c):
    sc = c["scenes.json"]["scenes"][0]
    sc.pop("control")
    sc["start"] = ["quicktest map", "one lantern hung at the room's centre"]


CASES = (("good_lanterns", "pass", None), ("bad_leaf_no_scene", "refuse", _no_oil_scene),
         ("bad_scene_no_control", "refuse", _no_control))


def planted():
    """The registry row's `planted` list (refusal_contract.judge_cases)."""
    return [{"id": cid, "expect": exp} for cid, exp, _m in CASES]


def stage(root):
    """Write the role files and one concept per case under root. -> [(case id, expect, concept dir)]."""
    for rel in ROLES:
        os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
        shutil.copyfile(os.path.join(REPO, rel), os.path.join(root, rel))
    out = []
    for cid, exp, mut in CASES:
        c = copy.deepcopy(BASE)
        if mut:
            mut(c)
        d = os.path.join(root, "design", "concepts", "Lanterns_%s" % cid)
        os.makedirs(d)
        for fn, body in c.items():
            with open(os.path.join(d, fn), "w", encoding="utf-8") as f:
                f.write(body if isinstance(body, str) else json.dumps(body, indent=1))
        out.append((cid, exp, d))
    return out


def judge(root, d):
    """One real coverage judge on a planted concept. -> (got, detail)."""
    tree = json.load(open(os.path.join(d, "tree.json"), encoding="utf-8"))
    text = CJ.prompt(d, root, CJ.required_ids(d, tree), False, 1)
    argv = [CJ.CLAUDE, "-p", text, "--model", CJ.MODEL, "--output-format", "json",
            "--json-schema", json.dumps(CJ.SCHEMA, separators=(",", ":")), "--dangerously-skip-permissions",
            "--max-budget-usd", "%g" % CASE_BUDGET_USD, "--name", "COVERAGE CALIBRATION %s" % os.path.basename(d)]
    try:
        p = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=CASE_TIMEOUT_S)
        res = json.loads(p.stdout or "null")
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return None, {"error": "%s: %s" % (type(e).__name__, e)}
    so = (res or {}).get("structured_output") if isinstance(res, dict) else None
    detail = {"cost_usd": (res or {}).get("total_cost_usd") if isinstance(res, dict) else None}
    if p.returncode != 0 or not isinstance(so, dict) or so.get("verdict") not in ("covered", "not_covered"):
        detail["error"] = "no well-formed verdict (exit %s)" % p.returncode
        return None, detail
    gaps = list(so.get("gaps") or []) + CJ.failed_part_gaps(so.get("checklist") or [], so.get("gaps") or [])
    detail.update(verdict=so["verdict"], gaps=[str(g.get("what"))[:200] for g in gaps if isinstance(g, dict)][:8])
    return ("pass" if so["verdict"] == "covered" and not gaps else "refuse"), detail


def run():
    with tempfile.TemporaryDirectory(prefix="rm-coverage-cal-") as root:
        staged = stage(root)
        with ThreadPoolExecutor(len(staged)) as ex:
            got = list(ex.map(lambda s: judge(root, s[2]), staged))
    rows = [dict({"id": cid, "expect": exp, "got": g}, **det) for (cid, exp, _d), (g, det) in zip(staged, got)]
    path = os.environ.get("RM_CALIBRATION_RESULTS")
    if path:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"cases": rows}, f, indent=1)
    for r in rows:
        print("%-22s expect %-6s got %-6s %s" % (r["id"], r["expect"], r["got"], r.get("error") or
                                                 "; ".join(r.get("gaps") or []) or r.get("verdict")))
    return 0 if all(r["got"] is not None for r in rows) else 1


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["run"]:
        return run()
    if argv[:1] == ["stage"] and len(argv) == 2:
        for cid, exp, d in stage(argv[1]):
            print(cid, exp, d)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
