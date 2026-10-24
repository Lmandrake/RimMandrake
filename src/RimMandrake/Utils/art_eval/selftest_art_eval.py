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
    check("kept art without a revert record is held", P.after_opus("REALLY_BAD", {"owner_kept": True}) == "HOLD_KEPT")
    kc = {"owner_kept": True, "kept_install": [{"mod": "SWBestiary", "rel": "a/b_south.png", "sha": "f" * 64}]}
    check("kept art with a revert record is redrawn when really bad", P.after_opus("REALLY_BAD", kc) == "REGEN")
    check("kept art weak goes to GPT", P.after_opus("WEAK", kc) == "GPT")
    rc = P.revert_commands(kc, "x → REVERT")
    check("revert is art.py install of the kept sha with --by-card", rc and rc[0][2] == "install" and "f" * 64 in rc[0] and "--by-card" in rc[0], rc)
    check("replaces_kept only on REGEN", P.replaces_kept(kc, "REGEN") and not P.replaces_kept(kc, "ACCEPT"))
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

    check("wall-mounted needs wall context", P.pre_route({"module": "wall_mounted", "panels": {"south": 1, "facings": 1, "scale": 1}}, mtpl, None) == "HOLD_INPUT")
    mids = {i["id"] for i in P.checklist_for(mtpl, "wall_mounted", P.card_facts({"ports": ["east side"]}))}
    check("wall lean + ports checked", {"WALL_LEAN", "PORTS_DRAWN"} <= mids, mids)
    check("ports item absent without ports", "PORTS_DRAWN" not in {i["id"] for i in P.checklist_for(mtpl, "reel", P.card_facts({}))})

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
            check("dry run: kept without revert record held", dec.get("RM_DryKept") == "HOLD_KEPT", dec)
            kr = next(r for r in res if r["subject"] == "RM_DryKeptRevertible")
            check("dry run: revertible kept art routed to REGEN", kr["decision"] == "REGEN", kr["decision"])
            check("dry run: flagged replaces_kept with revert + card", kr.get("replaces_kept") and kr.get("revert") and kr.get("install_by_card") == P.KEPT_ART_CARD, kr.get("reasons"))
            import shadow as SH
            why, _ = SH.row_line(kr)
            check("shadow row says REPLACED YOUR KEPT ART", why.startswith("REPLACED YOUR KEPT ART"), why)
            check("shadow offers revert", any(o[0] == "revert" for o in SH.OPTIONS))
            jobs = runner.regen_jobs(res, "selftest")
            check("regen job carries the install card", any(j.get("replaces_kept") and j.get("install_by_card") == P.KEPT_ART_CARD for j in jobs), jobs)
            check("dry run logs prompt versions + image shas", all(r.get("prompt_versions") and r.get("image_sha256") is not None for r in res), res[0])
    except ImportError as e:
        check("runner importable", False, str(e))

    # --- shadow sheet shows the judged candidate files, not only what is installed (SHADOW_SHEET_FIX_SHOWS_ONLY_THE_INSTALLED)
    try:
        import shadow as SH
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            f1, f2, f3 = td / "south.png", td / "assembled_1.png", td / "scale.png"
            for f, b in ((f1, b"a"), (f2, b"b"), (f3, b"c")):
                f.write_bytes(b)
            rec = {"subject": "RM_X", "source_files": {"south": str(f1), "assembled_1": str(f2), "scale": str(f3)},
                   "source_sha256": {"south": "S" * 64}}
            refs = SH.reference_map([rec])
            check("shadow references the candidate files as columns (not the scale composite)",
                  refs == {"RM_X": [str(f1), str(f2)]}, refs)
            check("shadow: a judged picture shown only as a reference is on the row",
                  SH.judged_on_row(rec, set(), {"S" * 64}) is True)
            check("shadow: a judged picture shown nowhere is still NOT on the row",
                  SH.judged_on_row(rec, set(), set()) is False)
            check("shadow: an installed match still counts", SH.judged_on_row(rec, {"S" * 64}, set()) is True)
            check("shadow: a run without source_files has no references", SH.reference_map([{"subject": "RM_Y"}]) == {})
    except (ImportError, AttributeError) as e:
        check("shadow candidate columns", False, repr(e))

    # --- cards.py (ART_EVAL_PROVE_CARDS_PY_UNTESTED, ART_EVAL_FIX_CARD_SOURCES_OMIT_CONTEXT)
    from PIL import Image, ImageDraw
    import cards as CD
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)

        def spr(name, h, color=(120, 90, 60, 255), opaque=False):
            im = Image.new("RGBA", (200, 200), (0, 0, 0, 0 if not opaque else 255))
            ImageDraw.Draw(im).rectangle([50, 200 - h, 150, 199], fill=color)
            p = td / name
            im.save(p)
            return str(p)

        s_, e_, n_ = spr("s.png", 100), spr("e.png", 150), spr("n.png", 100)
        g = CD.gates({"south": s_, "east": e_, "north": n_})
        check("gates: heights measured at visible alpha", g["visible_height_px"] == {"south": 100, "east": 150, "north": 100}, g)
        check("gates: spread 50% flagged", g["height_spread"] == 0.5 and g["height_spread_flag"] is True, g)
        check("gates: identical pictures reported as duplicates", g["duplicates"] == [["south", "north"]], g)
        check("gates: real alpha seen", g["alpha"]["south"] is True, g)
        g2 = CD.gates({"south": spr("o.png", 100, opaque=True)})
        check("gates: opaque picture has no alpha, one facing has no spread", g2["alpha"]["south"] is False and "height_spread" not in g2, g2)
        halo = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
        halo.putpixel((10, 10), (255, 255, 255, 8))
        check("visible_bbox ignores a sub-visible halo", CD.visible_bbox(halo) is None)
        st = CD.strip([s_, e_], ["a", "b"], tile=128)
        check("strip: one tile per image at one shared scale", st.size == (256, 128 + 30), st.size)
        check("canon_for: non-RSW subject has none", CD.canon_for("RM_Huldu") is None)
        check("canon_for: unknown RSW subject has none", CD.canon_for("RSW_NoSuchCreatureEver") is None)
        cb = CD.canon_for("RSW_Boarwolf")
        check("canon_for: Boarwolf must_show read from its entry", bool(cb and cb["must_show"] and cb["source"].endswith("description.md")), cb)
        wall, liv_a, liv_b, sib = spr("wall.png", 120), spr("la.png", 90), spr("lb.png", 80), spr("sib.png", 70)
        spec = {"subject": "RM_CardProbe", "label": "probe", "template": "creature", "module": "walker", "candidate": "A",
                "description": "a probe", "images": {"south": s_, "east": e_, "north": n_, "scale": spr("sc.png", 60),
                                                     "wall_context": wall, "living_reference": {"south": liv_a, "east": liv_b},
                                                     "siblings": [sib]}}
        sf = CD.source_files(spec)
        check("source_files names the wall context picture", sf.get("wall_context") == wall, sf)
        check("source_files names every living-reference picture", sf.get("living_reference_south") == liv_a and sf.get("living_reference_east") == liv_b, sf)
        check("source_files names the sibling pictures", sf.get("siblings_sib") == sib, sf)
        card = CD.build_card(spec, td / "card")
        for pn in ("south", "east", "north", "scale", "wall_context", "living_reference", "siblings", "facings"):
            check(f"build_card writes panel {pn}", pn in card["panels"] and (td / "card" / f"{pn}.png").is_file(), card["panels"])
        check("build_card: card.md carries the measured gates", "Measured by code" in (td / "card/card.md").read_text())
        check("build_card: every image sha recorded", set(card["image_sha256"]) >= {"south.png", "facings.png", "wall_context.png"})
        check("build_card: source shas cover wall and living pictures",
              {"wall_context", "living_reference_south", "south"} <= set(card["source_sha256"]), card["source_sha256"])
        check("card_sha stable for the same inputs", CD.build_card(spec, td / "card")["card_sha"] == card["card_sha"])
        try:
            CD.build_card(dict(spec, subject="RM_X", images={"south": s_}), td / "card2")
        except Exception as ex:   # a one-facing creature card must still build (gates skip the spread)
            check("build_card: one-facing card builds", False, repr(ex))

    # --- two candidates of one subject do not collide (ART_EVAL_FIX_SAME_SUBJECT_CANDIDATES_COLLIDE)
    try:
        import runner as RN
        check("spec_key: no candidate -> the subject", RN.spec_key({"subject": "RM_A"}) == "RM_A")
        check("spec_key: candidate joins the subject", RN.spec_key({"subject": "RM_A", "candidate": "C"}) == "RM_A__C")
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            im = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
            ImageDraw.Draw(im).ellipse([20, 20, 100, 120], fill=(100, 80, 60, 255))
            ps = {}
            for f in ("south", "east", "north", "scale"):
                ps[f] = str(td / f"{f}.png"); im.save(ps[f])
            tpl_ = P.load_template("creature")

            class Clean(RN.Reviewers):
                def opus(self, prompt, card_dir):
                    its = P.checklist_for(tpl_, "walker", P.card_facts({"invented": True}))
                    return json.dumps({"schema": "rm-art-eval/opus@v1", "subject": "RM_Two", "observed": {},
                                       "checklist": {i["id"]: {"status": "ok", "seen": "-"} for i in its},
                                       "findings": [], "overall": "good"}), {"models_reported": ["mock"]}
            two = [{"subject": "RM_Two", "candidate": c, "template": "creature", "module": "walker", "invented": True,
                    "description": "a beast", "images": ps} for c in ("A", "B")]
            recs = RN.run(two, "two", rev=Clean(), test=True, work_root=td / "w", state_root=td / "s")
            check("two candidates, two records", len(recs) == 2 and {r["candidate"] for r in recs} == {"A", "B"}, recs)
            check("two candidates keep two card dirs", (td / "w/two/RM_Two__A/card.json").is_file() and (td / "w/two/RM_Two__B/card.json").is_file())
            recs2 = RN.run(two, "two", rev=Clean(), test=True, work_root=td / "w", state_root=td / "s")
            lines = (td / "s/two/decisions.jsonl").read_text().splitlines()
            check("resume skips both candidates, not just the first", len(lines) == 2 and len(recs2) == 2, len(lines))
            old_root, RN.ROOT = RN.ROOT, td / "repo"
            try:
                RN.write_delegated(recs)
            finally:
                RN.ROOT = old_root
            names = sorted(p.name for p in (td / "repo/infrastructure/state/delegated").glob("*/*.json"))
            check("delegated verdicts do not overwrite each other", names == ["RM_Two__A.json", "RM_Two__B.json"], names)
            jobs = RN.regen_jobs([dict(r, decision="REGEN", round=1, regen={"request": {"prompt": "p"}, "findings": []}) for r in recs], "two")
            check("regen job ids differ per candidate", len({j["id"] for j in jobs}) == 2, [j["id"] for j in jobs])

        # --- file_regens no longer swallows a failed filing (ART_EVAL_HARDEN_FILE_REGENS_SILENT_FAILURE)
        class Done:
            def __init__(self, rc, err=""):
                self.returncode, self.stdout, self.stderr = rc, "", err
        check("filing ok on exit 0", RN.file_regen_jobs(Path("x.json"), runner=lambda *a, **k: Done(0))["ok"] is True)
        bad = RN.file_regen_jobs(Path("x.json"), runner=lambda *a, **k: Done(1, "REFUSED duplicate: arteval_x_r1"))
        check("filing failure is reported with the exit code and output", bad["ok"] is False and bad["rc"] == 1 and "duplicate" in bad["tail"], bad)

        def boom(*a, **k):
            import subprocess as sp
            raise sp.TimeoutExpired("fill_queue", 120)
        check("filing timeout is reported", RN.file_regen_jobs(Path("x.json"), runner=boom)["ok"] is False)
    except ImportError as e:
        check("runner importable (candidates)", False, str(e))

    # --- art_sheet: --subjects + --textures keeps --references; letters run out loudly (ART_SHEET_FIX_COMBINED_MODE_DROPS_REFERENCES)
    try:
        sys.path.insert(0, str(HERE.parent / "art"))
        import art_sheet as AS
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            mp = td / "m.json"
            mp.write_text(json.dumps({"rows": [{"key": "T_Leaf", "label": "leaf", "part": "Leaf", "look": "Timber", "section": "T",
                                                "resources": ["Mod/T/Leaf"], "size": {"drawSize": [1.0, 2.0], "footprint": [1, 2], "source": "L.cs:1"}}]}))
            old_out, AS.BIOME_OUT = AS.BIOME_OUT, td
            try:
                cp, key = AS.subjects_with_textures("ref_probe", mp, ["RM_SuspensionDeck_Steel"], label="x",
                                                    references={"RM_SuspensionDeck_Steel": ["/a/cand.png"]})
            finally:
                AS.BIOME_OUT = old_out
            rows = {r["key"]: r for r in json.loads(Path(cp).read_text())["biomes"][key]["rows"]}
            check("combined mode keeps --references on the def row", rows["RM_SuspensionDeck_Steel"].get("reference_textures") == ["/a/cand.png"], rows["RM_SuspensionDeck_Steel"].keys())
        n = len(AS.LETTERS)
        check("pick_options at the letter limit works", len(AS.pick_options(n)) == n + 2)
        try:
            AS.pick_options(n + 1)
            check("pick_options past the letters refuses by name", False)
        except SystemExit as ex:
            check("pick_options past the letters refuses by name", "letters" in str(ex))
    except (ImportError, AttributeError) as e:
        check("art_sheet importable", False, repr(e))

    print(f"{'PASS' if not FAILS else 'FAIL'}: art_eval selftest, {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
