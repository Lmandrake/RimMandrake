#!/usr/bin/env python3
"""selftest_art_calibration.py - the art judge brief's calibration check (RIMMANDRAKE_BUILD_ART_BRIEF_CALIBRATION_NOTHING_TO_RUN)
and the contract fix it needed (RIMMANDRAKE_TEACH_CONTRACT_CHECK_PICTURES_ARE_NOT_TEXT). No model, no network: the
pictures are small fakes in a temp source run, the judge is a fake runner. The real run is
`refusal_contract.py calibrate --model art_judge_brief`, which spends."""
import hashlib
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import refusal_contract as RC  # noqa: E402

FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def png(path, rgb, size=(64, 64)):
    from PIL import Image
    Image.new("RGBA", size, rgb + (255,)).save(path)


def fake_source(src, AC):
    """One card dir per case card, small coloured PNGs, and the pins that match them."""
    pins = {}
    for i, c in enumerate(AC.cases()):
        d = os.path.join(src, c["card"])
        if os.path.isdir(d):
            continue
        os.makedirs(d)
        plant = c["card"].split("__")[0] in ("RM_Shadefern", "RM_Dewblade")
        files = ("single.png", "scale.png") if plant else ("south.png", "east.png", "north.png", "scale.png")
        for j, f in enumerate(files):
            png(os.path.join(d, f), (10 + i * 7 % 200, 20 + j * 40, 30))
        card = {"subject": c["card"].split("__")[0], "label": "x", "template": "plant" if plant else "creature",
                "module": "bush" if plant else "walker", "candidate": c["card"].split("__")[1],
                "provenance": "owner PURGED this; owner REDO; owner kept B", "description": "A test creature.",
                "tier": "RM_", "invented": True, "size": {"drawSize": [0.9, 0.9]}, "owner_kept": False,
                "body_plan": None if plant else "walker", "departures": []}
        with open(os.path.join(d, "card.json"), "w") as f:
            json.dump(card, f)
        pins[c["card"]] = {f: hashlib.sha256(open(os.path.join(d, f), "rb").read()).hexdigest() for f in files}
    return pins


def answer(verdicts, refusals=(), passed=None, item="x", sha="s"):
    return {"judge_model": "opus", "subject": "RM_X", "verdicts": list(verdicts), "proposals": [],
            "contract": {"item": item, "family": "art_judge_brief", "sha": sha, "passed": passed or [],
                         "refusals": list(refusals)}}


def c1_refusal(fix="Redraw north.png as a rear view of the same subject, preserving its proportions, palette and scale."):
    return {"clause": "C1", "evidence": ["north.png"], "observed": "two eyes and a snout drawn on the north facing",
            "would_pass": "the north facing shows the back of the head and tail with no eyes, snout or mouth visible",
            "smallest_fix": {"what": fix, "attainable": "yes", "cost": "rerun"}, "criterion_verdict": "sound",
            "criterion_why": "North is the rear by the game's convention, and a back view is drawable for this body.",
            "new_since": "first"}


REDO_N = {"picture": "north.png", "facing": "north", "verdict": "REDO", "violated": "C1",
          "quote": "North is the creature's rear (no face, no eyes)", "seen": "two eyes on the north facing",
          "redo_brief": "a rear view"}
KEEP_S = {"picture": "south.png", "facing": "south", "verdict": "KEEP", "notes": "fine"}


def contract_cases():
    """RIMMANDRAKE_TEACH_CONTRACT_CHECK_PICTURES_ARE_NOT_TEXT: a picture cannot be word-matched; text still is."""
    crit = {"C1": "North is the creature's rear (no face, no eyes)"}
    with tempfile.TemporaryDirectory() as d:
        png(os.path.join(d, "north.png"), (200, 40, 40))
        with open(os.path.join(d, "notes.md"), "w") as f:
            f.write("the lantern hangs in the hall\n")
        rec = dict(c1_refusal(), criterion_hash=RC.criterion_hash(crit["C1"]))
        v = {"item": "x", "family": "art_judge_brief", "sha": "s", "passed": [], "refusals": [rec]}
        errs = RC.check(v, {"criteria": crit, "inputs": ["north.png"], "root": d})
        check("contract: a refusal citing a real PNG is well formed", errs == [], errs)
        v["refusals"][0] = dict(rec, evidence=["notes.md"])
        errs = RC.check(v, {"criteria": crit, "inputs": ["notes.md"], "root": d})
        check("contract: text evidence keeps its observed-words check",
              any("observed quotes" in e for e in errs), errs)


def registry_cases(AC):
    reg = json.load(open(os.path.join(REPO, "infrastructure/state/judge_calibration.json")))
    row = reg["families"].get("art_judge_brief") or {}
    check("registry: art_judge_brief names art_calibration.py as its model_check",
          row.get("model_check") == ["python3", "src/RimMandrake/rimflow/art_calibration.py", "run"], row.get("model_check"))
    check("registry: its planted cases are the check's own", row.get("planted") == AC.planted(), row.get("planted"))
    check("registry: its timeout is set for thirteen image judges", int(row.get("timeout_s") or 0) >= 1800,
          row.get("timeout_s"))


def planted_cases(AC):
    p = {c["id"]: c["expect"] for c in AC.planted()}
    rows = [json.loads(l) for l in open(os.path.join(REPO, "infrastructure/state/art_eval/regression.jsonl")) if l.strip()]
    check("planted: at least 11 cases", len(p) >= 11, len(p))
    check("planted: both ways", set(p.values()) == {"pass", "refuse"}, sorted(set(p.values())))
    taste = [r for r in rows if str(r.get("taste") or "").strip()]
    want = {AC.case_id(r): {"ACCEPT": "pass", "NOT_ACCEPT": "refuse"}[r["expect"]] for r in rows if r not in taste}
    check("planted: every regression.jsonl row he did not rule for taste is a case with his verdict",
          all(p.get(k) == v for k, v in want.items()), {k: (v, p.get(k)) for k, v in want.items() if p.get(k) != v})
    check("planted: a row he ruled for taste (his words in `taste`) is no planted case",
          all(AC.case_id(r) not in p for r in taste), [AC.case_id(r) for r in taste])
    kinds = {c.get("plant"): c for c in AC.cases()}
    check("planted: an owner-kept subject that must pass (E3)",
          (kinds.get("owner_kept") or {}).get("expect") == "pass", kinds.get("owner_kept"))
    b2 = {c["id"]: c for c in AC.cases() if c["id"].startswith("variant_")}
    check("planted: B2 is tested both ways (two refused on B2, one plain sprite passed)",
          sorted((c["expect"], c.get("route") or "") for c in b2.values())
          == [("pass", ""), ("refuse", "b2"), ("refuse", "b2")], b2)
    check("planted: a north facing whose fix must be a rear-view redraw",
          (kinds.get("north_from_south") or {}).get("expect") == "refuse"
          and (kinds.get("north_from_south") or {}).get("route") == "north_rear", kinds.get("north_from_south"))


def criteria_cases(AC):
    crit = AC.criteria()
    import re
    text = open(os.path.join(REPO, "design/RimMandrake/art_judge_brief.md"), encoding="utf-8").read()
    n = len(re.findall(r"^- [A-F]\d+a?\. ", text, re.M))
    check("criteria: every lettered constraint of the brief", {"A1", "B1a", "C1", "C5a", "C6", "D4", "E3", "F1"} <= set(crit)
          and len(crit) == n, (n, sorted(crit)))
    check("criteria: a sub-bullet stays with its constraint", "RM_LadderPortable" in crit.get("D4", ""), crit.get("D4"))
    check("criteria: C1 is the brief's own line", crit.get("C1", "").startswith(
        "North is the creature's rear (no face, no eyes); south looks at the camera"), crit.get("C1"))
    # RIMMANDRAKE_STEADY_ART_JUDGE_DANGLEMAW_NORTH_KEPT_ONE_RUN_IN_FOUR: a judge kept Danglemaw r1's toothed ring on north
    # because "C1 only bans a face or eyes"; the line says a mouth is face and the back of a head is closed
    c1 = crit.get("C1", "").lower()
    check("criteria: C1 counts a mouth and teeth as face, and the back of the head as closed",
          "mouth" in c1 and "teeth" in c1 and "closed" in c1, crit.get("C1"))
    # RIMMANDRAKE_RECONCILE_ART_BRIEF_SIZE_RULE_THREE_PICKS_REFUSED: his DecayDrake r2 pick (CL-035) carries mash mounds
    # its description says it makes; D4 names that ground matter as the subject, and still refuses every other prop
    d4 = crit.get("D4", "")
    check("criteria: D4 keeps every refused kind", all(w in d4 for w in ("backdrop", "halo", "ground shadow", "scenery")), d4)
    check("criteria: D4 names description-made ground matter, with his pick", "description" in d4 and "CL-035" in d4, d4)


def stage_cases(AC):
    with tempfile.TemporaryDirectory() as tmp:
        src, root = os.path.join(tmp, "src"), os.path.join(tmp, "root")
        os.makedirs(src)
        pins = fake_source(src, AC)
        staged = {c["id"]: (c, d, err) for c, d, err in AC.stage(root, source=src, pins=pins, sources={})}
        check("stage: every case staged", all(d for _c, d, _e in staged.values()),
              {k: e for k, (_c, d, e) in staged.items() if not d})
        n = next(v for v in staged.values() if v[0].get("plant") == "north_from_south")
        nd = n[1] or tmp
        check("stage: the north case's north.png is its south picture",
              os.path.exists(os.path.join(nd, "north.png")) and
              open(os.path.join(nd, "north.png"), "rb").read() == open(os.path.join(nd, "south.png"), "rb").read())
        k = next(v for v in staged.values() if v[0].get("plant") == "owner_kept")
        kf = json.load(open(os.path.join(k[1] or tmp, "subject.json"))) if k[1] else {}
        check("stage: the kept case says the owner kept it", "KEPT" in str(kf.get("owner_kept")), kf.get("owner_kept"))
        leaks = []
        for cid, (c, d, _e) in staged.items():
            if not d or c.get("plant"):
                continue
            text = open(os.path.join(d, "subject.json")).read()
            if "PURGED" in text or "REDO" in text or "owner kept B" in text or "regression" in text:
                leaks.append(cid)
        check("stage: a regression case's facts carry no verdict or provenance", not leaks, leaks)
        any_d = next(d for _c, d, _e in staged.values() if d)
        zoom = [f for f in os.listdir(any_d) if f.startswith("playzoom_")]
        from PIL import Image
        check("stage: a 32 px/cell play-zoom copy (drawSize 0.9 -> 29 px)",
              zoom and Image.open(os.path.join(any_d, zoom[0])).size[0] == 29, zoom)
        g = AC.given(any_d)
        check("stage: the given inputs are the staged files", set(g["inputs"]) == set(
            f for f in os.listdir(any_d) if f.endswith(".png") or f == "subject.json"), g["inputs"])
        text = AC.prompt(any_d)
        brief = open(os.path.join(REPO, "design/RimMandrake/art_judge_brief.md"), encoding="utf-8").read()
        check("prompt: carries the brief's real text whole", brief.strip() in text)
        check("prompt: tells the judge no expectation and no spend",
              "expect" not in text.lower().replace("expected", "") and "usd" not in text.lower() and "$" not in text)
        # a changed picture is a case that did not run, never a substitute
        victim = next(c for c in AC.cases() if not c.get("plant"))
        png(os.path.join(src, victim["card"], "scale.png"), (1, 2, 3))
        again = {c["id"]: (d, err) for c, d, err in AC.stage(os.path.join(tmp, "root2"), source=src, pins=pins, sources={})}
        check("stage: a picture off its pin is not staged", again[victim["id"]][0] is None
              and "sha" in str(again[victim["id"]][1]), again[victim["id"]])


def outcome_cases(AC):
    o = AC.outcome
    for name, route, ans, errs, want in (
            ("all KEEP is a pass", None, answer([KEEP_S]), [], "pass"),
            ("an UNSURE and no REDO is not a pass", None, answer([KEEP_S, {"facing": "east", "verdict": "UNSURE",
                                                                         "why": "x"}]), [], "unsure"),
            ("a quoted REDO is a refusal", None, answer([KEEP_S, REDO_N], [c1_refusal()]), [], "refuse"),
            ("a REDO without a quote is invalid", None, answer([dict(REDO_N, quote="")], [c1_refusal()]), [],
             "refuse, invalid"),
            ("a malformed record does not send work back", None, answer([REDO_N], [c1_refusal()]), ["bad"],
             "refuse, malformed"),
            ("a refusal record with no REDO verdict is still a refusal", None, answer([KEEP_S], [c1_refusal()]), [],
             "refuse"),
            ("north: C1 on north.png with a rear-view redraw", "north_rear", answer([REDO_N], [c1_refusal()]), [],
             "refuse"),
            ("north: a rotate-the-south fix is misdirected", "north_rear",
             answer([REDO_N], [c1_refusal("Rotate the south picture 180 degrees and use it as north.png.")]), [],
             "refuse, misdirected"),
            # RIMMANDRAKE_FIX_REAR_CHECK_NEGATED_FLIP_READ_AS_ROTATION: the 2026-11-17 08:33Z judge's own words
            ("north: a rear redraw that forbids a flip is not misdirected", "north_rear",
             answer([REDO_N], [c1_refusal("Redraw north.png as a rear view of the same subject at 512x512 real alpha, "
                                          "keeping south.png's proportions, palette, scale and footprint (mash mounds "
                                          "optional). Do not copy or flip south.png.")]), [], "refuse"),
            ("north: a rear redraw that says never rotate is not misdirected", "north_rear",
             answer([REDO_N], [c1_refusal("Draw a new rear view for north.png, never a rotation of the south.")]), [],
             "refuse"),
            ("north: a flip-then-repaint fix is still misdirected", "north_rear",
             answer([REDO_N], [c1_refusal("Flip south.png and paint over the face as the rear view; do not keep the eyes.")]),
             [], "refuse, misdirected"),
            ("north: a rear view rotated 180 is still misdirected", "north_rear",
             answer([REDO_N], [c1_refusal("Use a rear view: rotate south.png 180 degrees, not a new drawing.")]), [],
             "refuse, misdirected"),
            ("north: a refusal on another clause only is misdirected", "north_rear",
             answer([dict(REDO_N, violated="B2")], [dict(c1_refusal(), clause="B2")]), [], "refuse, misdirected"),
            # RIMMANDRAKE_ANSWER_SEVEN_TERMS_NO_SOURCE_DEFINES_GREY_MUD: a B2 plant is caught on B2, not on another line
            ("b2: a B2 refusal is the planted refusal", "b2",
             answer([dict(REDO_N, violated="B2")], [dict(c1_refusal(), clause="B2")]), [], "refuse"),
            ("b2: a refusal on another clause only is misdirected", "b2", answer([REDO_N], [c1_refusal()]), [],
             "refuse, misdirected")):
        got = o(route, ans, errs)
        check("outcome: %s" % name, got == want if want != "refuse, misdirected" else got.startswith(want), got)


def judge_cases(AC):
    """The production path: a malformed record is re-asked once (the brief's rule), then counted."""
    with tempfile.TemporaryDirectory() as tmp:
        src, root = os.path.join(tmp, "src"), os.path.join(tmp, "root")
        os.makedirs(src)
        pins = fake_source(src, AC)
        staged = [(c, d) for c, d, _e in AC.stage(root, source=src, pins=pins, sources={})]
        c, d = next((c, d) for c, d in staged if c.get("plant") == "north_from_south")
        g = AC.given(d)
        good = answer([REDO_N] + [{"picture": f, "facing": f[:-4], "verdict": "KEEP", "notes": "ok"}
                                  for f in ("south.png", "east.png")], [c1_refusal()],
                      passed=[{"clause": k, "evidence": sorted(g["inputs"])} for k in g["criteria"] if k != "C1"],
                      item=c["id"], sha=g["sha"])
        bad = json.loads(json.dumps(good))
        bad["contract"]["refusals"][0]["smallest_fix"]["cost"] = "cheap"
        calls = []

        def runner(argv, cwd, script=[bad, good]):
            calls.append(argv)
            so = script[min(len(calls) - 1, len(script) - 1)]
            return 0, json.dumps({"structured_output": so, "total_cost_usd": 0.5, "session_id": "sess-1",
                                  "usage": {"input_tokens": 10, "output_tokens": 5}, "modelUsage": {}})
        got, det = AC.judge(c, d, runner=runner)
        check("judge: a malformed first answer is re-asked once, on the same session",
              len(calls) == 2 and "--resume" in calls[1] and "sess-1" in calls[1], [a[:6] for a in calls])
        check("judge: the re-asked well-formed answer is the planted refusal", got == "refuse", (got, det))
        check("judge: no spend cap is passed to the agent", not any("--max-budget-usd" in a for a in calls))
        calls.clear()
        got, det = AC.judge(c, d, runner=lambda a, w: (calls.append(a), (0, json.dumps(
            {"structured_output": bad, "total_cost_usd": 0.4, "session_id": "s2"})))[1])
        check("judge: malformed twice is not the planted refusal", got == "refuse, malformed", (got, det.get("errors")))


def flyer_cases(AC):
    """The flyer rows (CL-047 FireHawk, CL-048 Porg) are cases like any other: their cards are pinned, their pictures
    come from the run that holds them, and the judge gets each flight frame and the parts sheet that C5a asks for."""
    cfg = AC.config()
    missing = [c["card"] for c in AC.cases() if c["card"] not in cfg["pins"]]
    check("config: every case's card is pinned (else it never runs and the brief stays UNTESTED)", not missing, missing)
    with tempfile.TemporaryDirectory() as tmp:
        runs = os.path.join(tmp, "runs")
        main_src, other = os.path.join(runs, "main_run"), os.path.join(runs, "flyer_run")
        os.makedirs(main_src)
        pins = fake_source(main_src, AC)
        card = "RM_TestFlyer__birdZ"
        d = os.path.join(other, card)
        os.makedirs(d)
        files = ("south.png", "east.png", "north.png", "scale.png", "flight_1.png", "flight_2.png", "parts_1.png")
        for j, f in enumerate(files):
            png(os.path.join(d, f), (200, 10 + j * 30, 40))
        with open(os.path.join(d, "card.json"), "w") as f:
            json.dump({"subject": "RM_TestFlyer", "template": "creature", "module": "flyer", "body_plan": "flyer",
                       "size": {"drawSize": [1.0, 1.0]}, "description": "A test flyer."}, f)
        pins = dict(pins, **{card: {f: hashlib.sha256(open(os.path.join(d, f), "rb").read()).hexdigest()
                                    for f in files}})
        orig = AC.cases
        AC.cases = lambda: orig() + [{"id": "regress_RM_TestFlyer_birdZ", "expect": "refuse", "card": card}]
        try:
            staged = {c["id"]: (dd, err) for c, dd, err in
                      AC.stage(os.path.join(tmp, "root"), source=main_src, pins=pins, sources={card: "flyer_run"})}
        finally:
            AC.cases = orig
        fd, err = staged.get("regress_RM_TestFlyer_birdZ", (None, "absent"))
        check("stage: a card named in card_sources is read from that run", fd is not None, err)
        check("stage: the other cards still come from the main run", all(v[0] for k, v in staged.items()),
              {k: v[1] for k, v in staged.items() if not v[0]})
        if fd:
            facts = json.load(open(os.path.join(fd, "subject.json")))
            check("stage: subject.json names the flight frames and the parts sheet",
                  facts.get("flight_frames") == ["flight_1.png", "flight_2.png"]
                  and facts.get("parts_sheet") == ["parts_1.png"], facts)
            text = AC.prompt(fd)
            check("prompt: each flight frame is named as a flight frame to look at alone",
                  "- flight_2.png: flight frame 2" in text and "one at a time" in text, text[:600])
            check("prompt: the parts sheet is named as the cut-out parts", "- parts_1.png: the cut-out parts sheet" in text)


def main():
    contract_cases()
    try:
        import art_calibration as AC
    except Exception as e:  # noqa: BLE001 - on the base the module is absent: a failure, not a crash
        check("art_calibration imports", False, "%s: %s" % (type(e).__name__, e))
        AC = None
    if AC:
        for f in (registry_cases, planted_cases, criteria_cases, stage_cases, flyer_cases, outcome_cases, judge_cases):
            try:
                f(AC)
            except Exception as e:  # noqa: BLE001
                check("%s ran" % f.__name__, False, "%s: %s" % (type(e).__name__, e))
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
