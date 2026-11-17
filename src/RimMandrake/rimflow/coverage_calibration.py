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
  good_lanterns_tuning    good_lanterns plus the pedantry the Contagion judge refused on (owner 2026-11-16, bar_rule.py):
                          an inventory row that pins a burn rate, a MarketValue and three graphic variants no scene
                          reads -> must pass: a judge that blocks on a tuning number or a variant count is not calibrated
  bad_leaf_no_scene       the oil leaf and its capability have no scene -> must be refused
  bad_scene_no_control    the light scene has no control and no asserted start -> must be refused
  bad_conflict_routing    his own words twice, with no precedence between them: "go out when it runs dry" (oil_out) and
                          "never goes dark, oil or none" (never_dark) -> must be refused AND routed to criteria review (a
                          flawed or unattainable criterion, the neutral fixer) or to his answer (return_to 2), never to
                          the Designer's rework. (First plant, 2026-11-17 run at 5f9fdb20: never_dark had no words of his,
                          so his words took precedence and the judge rightly sent the Designer to fix that leaf.)
  bad_mixed_row           an inventory row pinning numbers (3 oil, 120 ticks) beside an experience no scene tests (a pawn
                          refuels the lantern) -> must be refused on the experience; the number alone is waived
  bad_late_serious        a round-2 look after a refusing round-1 verdict that passed oil_out on an acceptance scene that
                          asserts the leaf's own red (lit at zero oil) -> the late gap must block: a serious Problem the
                          second reader confirms (owner by card 2026-11-16, point 26)
  good_round2_repaired    a round-2 look after round 1 refused the light scene's missing control, now repaired -> must
                          pass: later rounds only check named repairs (owner by card 2026-11-16, point 14)

Every refusal is routed as production routes it (owner by card 2026-11-16 on GPT's point 17, "Calibration must check
where a refusal goes"): the gaps the bar rule lets block go to the real second reader (coverage_judge.llm_reader), and
a refuse case counts as the planted refusal only when its route is the planted one (`outcome`): `designer` (a sound
criterion), `criteria` (the reader or the judge calls it flawed or unattainable) or `late` (a late gap the reader
confirmed serious). It spends (one Opus judge per case, each capped at CASE_BUDGET_USD, plus one reader per refusal): it runs only from
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


def _tuning_bait(c):
    """The Contagion pedantry kinds (RIMMANDRAKE_TEACH_JUDGES_BARS_HOLD_NO_TUNING_NUMBERS): numbers and a variant count
    that a renormalization or a new art variant changes, read by no scene. None of them is a bar."""
    c["record.json"]["inventory"].append({
        "id": "inv_lantern_def", "what": "The lantern def: fuel burn rate 1.0 per day, MarketValue 12, Mass 1.5, and "
        "three graphic variants (Lantern_a, Lantern_b, Lantern_c, Graphic_Random)", "impl": "present",
        "impl_evidence": ["src/RimMandrake/Lanterns/Defs/ThingDefs/Lantern.xml"], "proof": "current",
        "scope": "approved", "source": ["OWNER:1"]})
    c["scenes.json"]["coverage_rest"].append({
        "capability": "inv_lantern_def", "by": ["sc_light"],
        "why": "the lantern is drawn and lit in sc_light; its numbers and variants are tuning, not an experience"})


def _never_dark(c):
    """Two leaves that cannot both hold, each his words (GPT point 17, "a genuinely incompatible criterion set"):
    oil_out says an unfuelled lantern goes dark, never_dark says it never does. No precedence settles it, so no Designer
    rework can pass both: a correct refusal goes to criteria review or to him."""
    c["sheet.md"] = c["sheet.md"].replace(
        "\n\n## does", "\n- 2026-11-03: \"A hung lantern never goes dark, oil or none: nobody wants a dark room.\" "
        "OWNER:3\n\n## does", 1)
    c["record.json"]["inventory"].append({
        "id": "inv_never_dark", "what": "A hung lantern never goes dark, whether or not it holds oil", "impl": "present",
        "impl_evidence": ["src/RimMandrake/Lanterns/Source/CompLanternGlow.cs"], "proof": "current",
        "scope": "approved", "source": ["OWNER:3"]})
    c["tree.json"]["leaves"].append(dict(
        LEAF, id="never_dark", experience="A hung lantern never goes dark: its cells stay lit at every hour for as long "
        "as it hangs, whether or not it holds any oil", scenario="a lit lantern with 0 oil, a day passing",
        source=["OWNER:3"],
        false_pass=["a lantern refuelled during the day"], red="a hung lantern whose cells go dark"))
    c["sheet.md"] = c["sheet.md"].replace(
        "\n\n## does not", "\n- [leaf:never_dark] A hung lantern never goes dark, oil or none\n\n## does not")
    c["scenes.json"]["scenes"].append({
        "id": "sc_never_dark", "kind": "acceptance", "requirement": ["never_dark"], "staged_by": "script",
        "entry_point": "src/RimMandrake/Lanterns/validation.py::scene_never_dark",
        "start": ["the sc_light room, the lantern lit with 0 oil (asserted)"], "action": "advance one day",
        "expect": "the lantern's cells still read at least 50% within 2 cells",
        "control": {"case": "the same room with no lantern hung", "expect": "glow stays 0 on every room cell",
                    "rules_out": "light from the room rather than the lantern"},
        "restore": "destroy the quicktest map; nothing persistent changed", "hold": "immediate"})


def _refuel_row(c):
    """A mixed row (GPT point 17): an experience no scene tests (a pawn refuels a lantern) beside tuning numbers. The
    numbers are waived; the experience still blocks."""
    c["record.json"]["inventory"].append({
        "id": "inv_refuel", "what": "A pawn refuels a hung lantern from stockpiled oil, and the lantern lights again; "
        "each refuel adds 3 oil and takes 120 ticks", "impl": "present",
        "impl_evidence": ["src/RimMandrake/Lanterns/Source/CompLanternFuel.cs"], "proof": "current",
        "scope": "approved", "source": ["OWNER:1"]})


R1_JUDGE = "rm-coverage-judge-calibration-r1"


def _prior(gap, rows_ok):
    """A round-1 verdict that refused on `gap` and passed every other row (rows_ok: {id: scene})."""
    return {"verdict": "not_covered", "judge": R1_JUDGE, "round": 1, "gaps": [dict(gap, gid="g1", new_since="first")],
            "checklist": [{"id": i, "evidence": ["scenes.json", "tree.json"],
                           "parts": [{"what": "the %s experience" % i, "scene": sc, "ok": True}]}
                          for i, sc in rows_ok.items()]}


LIGHT_GAP = {"what": "sc_light has no control and its start asserts no dark", "where": "scenes.json sc_light",
             "ids": ["light", "inv_light"], "return_to": 3, "bar_kind": "experience", "severity": "problem",
             "evidence": ["scenes.json"], "observed": "sc_light has no `control`",
             "would_pass": "sc_light asserts a dark lamp-free room at midnight and a 0-oil control stays dark",
             "smallest_fix": {"what": "add a control and asserted start to sc_light", "attainable": "yes",
                              "cost": "edit"},
             "criterion_verdict": "sound", "criterion_why": "a lit room is checkable with a dark control"}


def _late_red(c):
    """Round 2 after round 1 refused sc_light and PASSED oil_out on sc_oil_out, whose expect is the leaf's own red (a
    lantern lit at zero oil): unchanged since, so a gap on it now is late, and a Problem a player would reject."""
    sc = c["scenes.json"]["scenes"][1]
    sc["expect"] = "the first lantern holds 0 oil and its cells still read at least 50% within 2 cells"
    sc["control"]["expect"] = "it holds 1 oil and its cells still read at least 50% within 2 cells"
    c["coverage_verdict.json"] = _prior(LIGHT_GAP, {"oil_out": "sc_oil_out", "inv_oil": "sc_oil_out"})


def _repaired(c):
    """Round 2 after round 1 refused sc_light's missing control; the BASE scene now has it: a later round checks the
    repair and finishes."""
    c["coverage_verdict.json"] = _prior(LIGHT_GAP, {"oil_out": "sc_oil_out", "inv_oil": "sc_oil_out"})


# id, expect, mutation, the route a refusal must take (`outcome`), and whether it is a later round (a prior verdict)
CASES = (("good_lanterns", "pass", None, None), ("good_lanterns_tuning", "pass", _tuning_bait, None),
         ("good_round2_repaired", "pass", _repaired, None),
         ("bad_leaf_no_scene", "refuse", _no_oil_scene, "designer"),
         ("bad_scene_no_control", "refuse", _no_control, "designer"),
         ("bad_conflict_routing", "refuse", _never_dark, ("criteria", "owner")),
         ("bad_mixed_row", "refuse", _refuel_row, "designer"),
         ("bad_late_serious", "refuse", _late_red, "late"))
ROUTE = {cid: route for cid, _e, _m, route in CASES}
FAULTED = ("flawed", "unattainable")


def planted():
    """The registry row's `planted` list (refusal_contract.judge_cases)."""
    return [{"id": cid, "expect": exp} for cid, exp, _m, _r in CASES]


def route_of(g):
    """Where production sends one blocking gap: the criteria (the neutral fixer: coverage_judge's criteria_suspect), his
    answer (return_to 2: stage 2 asks him) or the Designer's rework."""
    if g.get("criterion_verdict") in FAULTED or g.get("judge_criterion_verdict") in FAULTED:
        return "criteria"
    return "owner" if g.get("return_to") == 2 else "designer"


def outcome(route, blocking):
    """-> "pass" with no blocking gap; "refuse" when a blocking gap takes the planted route (any route for a pass case:
    its refusal is wrong anyway; a tuple of routes accepts any of them); else "refuse, misrouted (<routes>)", which is
    not the planted refusal."""
    if not blocking:
        return "pass"
    routes = {route_of(g) for g in blocking}
    if any(g.get("new_since") == "late" and g.get("late_confirmed") is True for g in blocking):
        routes.add("late")
    if route is None or set(route if isinstance(route, tuple) else (route,)) & routes:
        return "refuse"
    return "refuse, misrouted (%s)" % ", ".join(sorted(routes))


def stage(root):
    """Write the role files and one concept per case under root. -> [(case id, expect, concept dir)]."""
    for rel in ROLES:
        os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
        shutil.copyfile(os.path.join(REPO, rel), os.path.join(root, rel))
    out = []
    for cid, exp, mut, _route in CASES:
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


def judge(root, d, route=None, reader="auto"):
    """One real coverage judge on a planted concept, its blocking gaps read by the real second reader. -> (got,
    detail)."""
    tree = json.load(open(os.path.join(d, "tree.json"), encoding="utf-8"))
    prior = CJ.prior_verdict(d)
    text = CJ.prompt(d, root, CJ.required_ids(d, tree), prior is not None, 2 if prior else 1)
    argv = [CJ.CLAUDE, "-p", text, "--model", CJ.MODEL, "--output-format", "json",
            "--json-schema", json.dumps(CJ.SCHEMA, separators=(",", ":")), "--dangerously-skip-permissions",
            "--name", "COVERAGE CALIBRATION %s" % os.path.basename(d)]
    argv = CJ.spend_watchdog.wrap(argv, CASE_BUDGET_USD)     # the cap from outside: the judge is not told its spend
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
    gaps = [g for g in list(so.get("gaps") or []) + CJ.failed_part_gaps(so.get("checklist") or [], so.get("gaps") or [])
            if isinstance(g, dict)]
    if prior:   # what run() does on a later look: tag against the earlier gaps; a late gap is the refuser's miss
        CJ.tag_gaps(gaps, [g for g in prior.get("gaps") or [] if isinstance(g, dict)])
        for g in gaps:
            if g.get("new_since") == "late":
                g["miss_of"] = prior.get("judge")
    # the gate run() applies: only a gap the bar rule lets block refuses (bar_rule.blocks), after the second reader
    gaps, adv = CJ.BR.split(gaps)
    unread = None
    if gaps:
        rec = {"gaps": gaps}
        ent, crit = CJ.entries(d), {CJ.REST_CLAUSE: CJ.REST_TEXT}   # the criterion texts, as contract_verdict gives them
        for i in {i for g in gaps for i in g.get("ids") or []}:
            e = ent.get("inv:%s" % i) or ent.get("leaf:%s" % i)
            if e is not None:
                crit[i] = json.dumps(e, sort_keys=True)
        if reader == "auto":
            reader = CJ.llm_reader(d, root, "calibration-%s" % os.path.basename(d), charge=False)
        unread = CJ.second_read(rec, crit, reader)
        gaps, adv2 = CJ.BR.split(rec["gaps"])
        adv += adv2
    detail.update(verdict=so["verdict"], gaps=[str(g.get("what"))[:200] for g in gaps][:8],
                  advisory=[str(g.get("what"))[:200] for g in adv][:8],
                  routes=[{"what": str(g.get("what"))[:120], "route": route_of(g), "new_since": g.get("new_since"),
                           "ids": g.get("ids"), "return_to": g.get("return_to"),
                           "judge_criterion_verdict": g.get("judge_criterion_verdict"),
                           "criterion_verdict": g.get("criterion_verdict"), "severity": g.get("severity"),
                           "late_confirmed": g.get("late_confirmed")} for g in gaps][:8])
    if unread:   # no second read: the refusal binds nothing in production, so it is not the planted refusal either
        detail["unread"] = unread
        return "refuse, unread", detail
    if not gaps and so["verdict"] != "covered" and not adv:
        return "refuse", detail   # not_covered with no gap at all: a refusal that names nothing
    return outcome(route, gaps), detail


def run():
    with tempfile.TemporaryDirectory(prefix="rm-coverage-cal-") as root:
        staged = stage(root)
        with ThreadPoolExecutor(len(staged)) as ex:
            got = list(ex.map(lambda s: judge(root, s[2], ROUTE.get(s[0])), staged))
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
