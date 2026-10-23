#!/usr/bin/env python3
"""Selftest for the art-eval pipeline's pure parts: policy files parse, severity by policy (not model), the Opus
band, GPT strong-accept, routing, regen cap, catch dependency, kept art, incomplete cards, shadow streaks, and a
runner dry run with mocked reviewers. No model is called.

    python3 src/RimMandrake/Utils/art_eval/selftest_art_eval.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import policy as P  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    if not cond:
        FAILS.append(f"{name}: {detail}")
        print("FAIL", name, detail)


def opus_reply(items, fail=(), unreadable=(), findings=(), overall="good"):
    cl = {}
    for it in items:
        st = "fail" if it["id"] in fail else "unreadable" if it["id"] in unreadable else "ok"
        cl[it["id"]] = {"status": st, "seen": "x"}
    return {"schema": "rm-art-eval/opus@v1", "subject": "RM_Test", "observed": {}, "checklist": cl,
            "findings": list(findings), "overall": overall}


def main():
    pol = P.load_policy()
    check("policy version", pol["version"].startswith("severity@"), pol.get("version"))
    for t in P.TEMPLATES:
        tpl = P.load_template(t)
        check(f"template {t} parses", tpl["template"] == t and tpl["checklist"], t)
        for it in tpl["checklist"]:
            check(f"template {t} item {it['id']} code known", it["code"] in pol["codes"], it["code"])
        check(f"template {t} module text sent", "```json" not in tpl["module_text"], t)
    for name in ("preamble", "opus_first_pass", "gpt_targeted_second_look", "regen_prompt_edit"):
        v = P.prompt_version(P.REFS / "prompts" / f"{name}.md")
        check(f"prompt {name} versioned", v["tag"].startswith(name + "@"), v)

    # --- severity is policy's, with the pilot's tolerances
    inv = P.card_facts({"invented": True})
    check("earthly blocks invented", P.severity("STYLE_EARTHLY", inv, pol) == "blocking")
    check("earthly polish when earth body named", P.severity("STYLE_EARTHLY", P.card_facts({"invented": True, "earth_body_named": True}), pol) == "polish")
    check("topdown polish on wall clinger", P.severity("F_TOPDOWN", P.card_facts({"body_plan": "wall_clinger"}), pol) == "polish")
    check("topdown blocks a walker", P.severity("F_TOPDOWN", inv, pol) == "blocking")
    check("scale is polish", P.severity("SCALE_WRONG", inv, pol) == "polish")
    check("unknown code fails closed", P.severity("MADE_UP", inv, pol) == "blocking")

    tpl = P.load_template("creature")
    items = P.checklist_for(tpl, "walker", inv)
    ids = {i["id"] for i in items}
    check("walker gets facing items", {"SOUTH_FRONT", "NORTH_REAR", "ALIEN"} <= ids, ids)
    check("walker has no catch items", "CATCH_DEAD" not in ids, ids)
    citems = P.checklist_for(tpl, "catch", inv)
    cids = {i["id"] for i in citems}
    check("catch skips facings, has pose", "NORTH_REAR" not in cids and "CATCH_DEAD" in cids, cids)
    check("departures item only with departures", "DEPARTURES" in {i["id"] for i in P.checklist_for(tpl, "walker", P.card_facts({"invented": True, "departures": ["x"]}))})

    # --- the Opus band
    band, d = P.opus_band(opus_reply(items), items, inv, pol)
    check("clean -> GOOD", band == "GOOD", (band, d))
    band, d = P.opus_band(opus_reply(items, findings=[{"code": "SCALE_WRONG", "confidence": 0.9}]), items, inv, pol)
    check("polish only -> GOOD", band == "GOOD", band)
    # the pilot's Opus failure: sees the Earth animal, calls it minor, says good -> policy blocks
    r = opus_reply(items, findings=[{"code": "STYLE_EARTHLY", "confidence": 0.85, "model_severity": "polish"}])
    band, d = P.opus_band(r, items, inv, pol)
    check("model-minor earthly is REALLY_BAD by policy", band == "REALLY_BAD", band)
    check("severity disagreement recorded", "STYLE_EARTHLY" in d["severity_disagreements"], d)
    band, d = P.opus_band(opus_reply(items, findings=[{"code": "STYLE_EARTHLY", "confidence": 0.5}]), items, inv, pol)
    check("low-confidence blocking -> WEAK", band == "WEAK", band)
    band, d = P.opus_band(opus_reply(items, unreadable=("NORTH_REAR",)), items, inv, pol)
    check("unreadable item -> WEAK, never GOOD", band == "WEAK" and d["incomplete"], (band, d))
    band, d = P.opus_band(opus_reply(items, fail=("NORTH_REAR",)), items, inv, pol)
    check("checklist fail without finding -> synthetic blocking, WEAK", band == "WEAK" and d["blocking"][0]["code"] == "F_NORTH_FACE", (band, d))
    band, d = P.opus_band(opus_reply(items, overall="weak"), items, inv, pol)
    check("model doubt keeps it off GOOD", band == "WEAK", band)
    band, d = P.opus_band(opus_reply(items, findings=[{"code": "X_BLANK", "confidence": 0.2}]), items, inv, pol)
    check("gross at any confidence -> REALLY_BAD", band == "REALLY_BAD", band)

    # --- schema
    try:
        P.validate_opus({"schema": "rm-art-eval/opus@v1", "checklist": {}, "findings": [], "overall": "good"}, items)
        check("missing checklist answers refused", False)
    except P.SchemaError:
        pass
    check("parse fenced reply", P.parse_reply('note\n```json\n{"a": 1}\n```')["a"] == 1)

    # --- GPT targeted second look
    band, d = P.opus_band(opus_reply(items, findings=[{"code": "F_NORTH_FACE", "confidence": 0.5}]), items, inv, pol)
    ks = P.concerns_from(d)
    check("one concern per blocking finding", len(ks) == 1 and ks[0]["code"] == "F_NORTH_FACE", ks)
    good = {"schema": "rm-art-eval/gpt@v1", "verdict": "strong_accept", "findings": [],
            "concerns": [{"id": "K1", "answer": "refuted", "evidence": "north tile shows haunches and tail, no eyes"}]}
    check("strong accept with evidence -> ACCEPT", P.gpt_outcome(good, ks, inv, pol)[0] == "ACCEPT")
    bare = json.loads(json.dumps(good)); bare["concerns"][0]["evidence"] = "fine"
    check("refuted without evidence -> REGEN", P.gpt_outcome(bare, ks, inv, pol)[0] == "REGEN")
    own = json.loads(json.dumps(good)); own["findings"] = [{"code": "ALPHA_HALO", "confidence": 0.6}]
    check("strong accept with own blocking -> REGEN", P.gpt_outcome(own, ks, inv, pol)[0] == "REGEN")
    pol_only = json.loads(json.dumps(good)); pol_only["findings"] = [{"code": "LEGIB_32", "confidence": 0.9}]
    check("strong accept with polish only -> ACCEPT", P.gpt_outcome(pol_only, ks, inv, pol)[0] == "ACCEPT")
    unsure = json.loads(json.dumps(good)); unsure["verdict"] = "unsure"
    check("unsure -> REGEN", P.gpt_outcome(unsure, ks, inv, pol)[0] == "REGEN")
    check("doubt-only weak still asks GPT something", P.concerns_from({"blocking": [], "incomplete": [], "model_overall": "weak"}))

    # --- routing
    check("GOOD -> ACCEPT", P.after_opus("GOOD", {}) == "ACCEPT")
    check("REALLY_BAD -> REGEN", P.after_opus("REALLY_BAD", {}) == "REGEN")
    check("WEAK -> GPT", P.after_opus("WEAK", {}) == "GPT")
    check("owner-kept never replaced", P.after_opus("REALLY_BAD", {"owner_kept": True}) == "HOLD_KEPT")
    check("regen round 1", P.cap_regen("REGEN", 0, 3) == ("REGEN", 1))
    check("regen round 3 allowed", P.cap_regen("REGEN", 2, 3) == ("REGEN", 3))
    check("4th regen escalates", P.cap_regen("REGEN", 3, 3) == ("ESCALATE", 3))
    check("accept untouched by cap", P.cap_regen("ACCEPT", 5, 3) == ("ACCEPT", 5))
    card = {"module": "catch", "panels": {"single": 1, "scale": 1, "living_reference": 1}}
    check("catch follows living REGEN", P.pre_route(card, tpl, "REGEN") == "REGEN_AFTER_SOURCE")
    check("catch proceeds when living accepted", P.pre_route(card, tpl, "ACCEPT") is None)
    check("catch without living ref held", P.pre_route({"module": "catch", "panels": {"single": 1, "scale": 1}}, tpl, None) == "HOLD_INPUT")
    mtpl = P.load_template("machine")
    check("machine without capture held", P.pre_route({"module": "machine", "panels": {"south": 1, "facings": 1, "scale": 1}}, mtpl, None) == "HOLD_INPUT")

    # --- regen findings
    band, d = P.opus_band(opus_reply(items, findings=[{"code": "F_NORTH_FACE", "confidence": 0.5, "fix": "rear view"},
                                                      {"code": "STYLE_CARTOON", "confidence": 0.5, "fix": "realistic"}]), items, inv, pol)
    ks = P.concerns_from(d)
    g = {"schema": "rm-art-eval/gpt@v1", "verdict": "regen", "findings": [{"code": "ALPHA_HALO", "confidence": 0.7, "fix": "clean cut-out"}],
         "concerns": [{"id": ks[0]["id"], "answer": "refuted", "evidence": "the north tile shows the tail end only"},
                      {"id": ks[1]["id"], "answer": "confirmed", "evidence": "glossy eyes"}]}
    out, gd = P.gpt_outcome(g, ks, inv, pol)
    rf = {f["code"] for f in P.regen_findings(d, gd, g)}
    check("regen fixes confirmed + GPT's own, drops refuted", rf == {"STYLE_CARTOON", "ALPHA_HALO"}, rf)
    rp = P.deterministic_regen_prompt({"subject": "RM_Test", "description": "a beast", "departures": ["six legs"]},
                                      [{"code": "STYLE_EARTHLY", "fix": "six legs, three per side"}])
    check("anatomy regen drops the reference", rp["reference"] == "none" and "six legs" in rp["prompt"], rp)

    # --- shadow streaks
    s = json.loads(json.dumps(P.DEFAULT_SETTINGS)); s["shadow"]["creature"]["off_after_consecutive_clean"] = 3
    rows = [{"template": "creature", "at": "1", "override": True, "blocking": True}] + \
           [{"template": "creature", "at": str(i), "override": False} for i in range(2, 5)]
    st = P.shadow_status("creature", rows, s)
    check("3 clean after a blocking override -> eligible", st["eligible_to_turn_off"] and not st["shadow_owed"], st)
    rows.append({"template": "creature", "at": "9", "override": True, "blocking": True})
    check("blocking override resets", P.shadow_status("creature", rows, s)["consecutive_clean"] == 0)
    rows.append({"template": "creature", "at": "99", "override": True, "blocking": False})
    check("polish override does not reset", P.shadow_status("creature", rows, s)["consecutive_clean"] == 1)

    # --- criteria ledger: add -> fix -> regression row; overrides need his words
    import ledger as LG
    with tempfile.TemporaryDirectory() as td:
        lp, rp = Path(td) / "l.jsonl", Path(td) / "r.jsonl"
        cid = LG.add("RM_T", "plant", "owner_key", "missed x", "REGEN", path=lp)
        check("ledger ids start CL-001", cid == "CL-001", cid)
        check("second id increments", LG.add("RM_U", "plant", "agent_review", "y", "ACCEPT", path=lp) == "CL-002")
        LG.fix(cid, "moved code", ["a.md"], regression="RM_T:B", expect="ACCEPT", path=lp, reg_path=rp)
        e = LG.entries(lp)
        check("fix folds to fixed with versions", e[cid]["status"] == "fixed" and e[cid]["fixes"][0]["versions_after"].get("severity"), e[cid])
        check("regression row written", json.loads(rp.read_text().splitlines()[0])["expect"] == "ACCEPT")
        try:
            LG.add("RM_V", "plant", "owner_override", "z", "ACCEPT", path=lp)
            check("override without his words refused", False)
        except SystemExit:
            pass

    # --- runner dry run end to end on a synthetic card (mock reviewers, no model)
    try:
        import runner
        with tempfile.TemporaryDirectory() as td:
            res = runner.selftest_dry_run(Path(td))
            check("dry run decides every subject", res and all(r["decision"] in P.DECISIONS for r in res), res)
            dec = {r["subject"]: r["decision"] for r in res}
            check("dry run: good -> ACCEPT", dec.get("RM_DryGood") == "ACCEPT", dec)
            check("dry run: bad -> REGEN", dec.get("RM_DryBad") == "REGEN", dec)
            check("dry run: weak -> GPT -> ACCEPT", dec.get("RM_DryWeak") == "ACCEPT", dec)
            check("dry run: catch of a REGEN living waits", dec.get("RM_DryBadCatch") == "REGEN_AFTER_SOURCE", dec)
            check("dry run: kept held", dec.get("RM_DryKept") == "HOLD_KEPT", dec)
            check("dry run logs prompt versions + image shas", all(r.get("prompt_versions") and r.get("image_sha256") is not None for r in res), res[0])
    except ImportError as e:
        check("runner importable", False, str(e))

    print(f"{'PASS' if not FAILS else 'FAIL'}: art_eval selftest, {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
