#!/usr/bin/env python3
"""Selftest for fauna_drive.py: test runs never supply a decision, run-name classification, install sha gate (pure)."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fauna_drive as FD  # noqa: E402
import round_series as RS  # noqa: E402

FAILS = []


def check(name, ok, detail=None):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok or detail is None else f"  -> {detail}"))
    if not ok:
        FAILS.append(name)


def main():
    # (3 of FAUNA_DRIVE_FIX_TEST_RUNS_COUNTED / 2) candidate vs first-pass run names
    check("_r1_ is a candidate run", bool(FD.CAND_RUN.search("t_r1_00")))
    check("series tag s1r1 is a candidate run", bool(FD.CAND_RUN.search("t_s1r1_00")))
    check("biome glass_reef is first pass", not FD.CAND_RUN.search("glass_reef_00"))
    check("plain first pass", not FD.CAND_RUN.search("t_00"))

    # 1: a --test run is invisible to production(); latest() on production data ignores its newer ACCEPT
    with tempfile.TemporaryDirectory() as td:
        runs = Path(td)
        for name, test, dec, at in (("fauna_t_r1_00", False, "REGEN", "2026-10-23T10:00:00+00:00"),
                                    ("fauna_t_r1_01", True, "ACCEPT", "2026-10-24T10:00:00+00:00")):
            d = runs / name
            d.mkdir()
            (d / "run.json").write_text(json.dumps({"test": test}))
            (d / "decisions.jsonl").write_text(json.dumps({"subject": "D", "decision": dec, "at": at}) + "\n")
        orig = RS.production_decisions
        RS.production_decisions = lambda: orig(runs)
        try:
            recs = FD.production()
            check("test run excluded from production()", [r for r, _ in recs] == ["fauna_t_r1_00"])
            check("latest ignores the newer test ACCEPT", (FD.latest("D", True) or {}).get("decision") == "REGEN")
        finally:
            RS.production_decisions = orig

    # RIMMANDRAKE_FIX_ART_JUDGE_TIMER_IDLE_SINCE_NOV_EIGHT: a first pass judged under an adopted run is still a first
    # pass, and its redraw's render is found under <DEF>__live_<tag> when <DEF>_<tag> was never drawn
    with tempfile.TemporaryDirectory() as td:
        ad = [("gptredo_t", {"subject": "D", "decision": "REGEN", "candidate": "live", "at": "2026-10-24T10:00:00+00:00"})]
        check("an adopted first pass ('live') is not a candidate record",
              FD.latest("D", False, ad) is not None and FD.latest("D", True, ad) is None)
        saved = FD.ART
        FD.ART = Path(td)
        try:
            def render(job):
                (Path(td) / "done").mkdir(exist_ok=True)
                (Path(td) / "done" / f"{job}.manifest.json").write_text(json.dumps({"status": "ok"}))
                (Path(td) / "_artsrc" / job).mkdir(parents=True)
                (Path(td) / "_artsrc" / job / f"{job}.png").write_bytes(b"x")
            for f in ("south", "east", "north"):
                render(f"arteval_D__live_r1_{f}")
            check("the __live render is the def's r1", FD.job_stem("D", "r1") == "arteval_D__live_r1")
            check("another round is not", FD.job_stem("D", "r2") == "arteval_D_r2")
            render("arteval_D_r1_south")
            check("a render under the def's own name wins", FD.job_stem("D", "r1") == "arteval_D_r1")
            # a finished render the daemon pruned from _artsrc (14 days) is in the art store under its ledger sha
            import shutil
            shutil.rmtree(Path(td) / "_artsrc")
            import os
            os.environ["ARTSTORE"] = str(Path(td) / "store")
            sha = "ab" * 32
            (Path(td) / "store" / "ab").mkdir(parents=True)
            (Path(td) / "store" / "ab" / f"{sha}.png").write_bytes(b"x")
            FD._STORED = {"arteval_D__live_r1_south": sha, "arteval_D__live_r1_north": "cd" * 32}
            got = FD.job_png("arteval_D__live_r1_south")
            check("a pruned render is read from the art store", got is not None and got.name == f"{sha}.png", got)
            check("a render the store does not hold, or no ledger names, is None",
                  FD.job_png("arteval_D__live_r1_north") is None and FD.job_png("arteval_D__live_r1_east") is None)
            FD._STORED["arteval_undone"] = sha
            check("a job with no ok manifest is None even when the store holds it", FD.job_png("arteval_undone") is None)
        finally:
            FD.ART, FD._STORED = saved, None
            os.environ.pop("ARTSTORE", None)

    # a render on a whole multiple of the shipping canvas is brought down to it; any other size is named, never sent on
    with tempfile.TemporaryDirectory() as td:
        sys.path.insert(0, str(HERE.parent))
        import image_skills
        image_skills.add_to_path()
        import pnglib
        big, odd, right = Path(td) / "big.png", Path(td) / "odd.png", Path(td) / "right.png"
        for f, n in ((big, 1024), (odd, 700), (right, 256)):
            pnglib.write_rgba(str(f), n, n, bytes([9, 8, 7, 255]) * (n * n))
        saved, FD.job_png = FD.job_png, lambda j: {"big": big, "odd": odd, "right": right}.get(j)
        saved_fit, FD.FIT = FD.FIT, Path(td) / "fit"
        try:
            got = FD.shipping_png("big", [2.0, 2.0])
            check("1024 for a 256 canvas is brought down to 256", pnglib.read_png(str(got))[:2] == (256, 256), got)
            first = got.read_bytes()
            got.unlink()
            check("the same picture gives the same bytes (the installer matches the judged sha)",
                  FD.shipping_png("big", [2.0, 2.0]).read_bytes() == first)
            check("a right-sized render is itself", FD.shipping_png("right", [2.0, 2.0]) == right)
            check("a size that is no whole multiple stays itself", FD.shipping_png("odd", [2.0, 2.0]) == odd)
            check("a size that cannot be fitted is named before the judge",
                  "odd 700x700" in (FD.off_canvas({"odd": odd, "south": right}, 2.0) or "")
                  and FD.off_canvas({"south": right}, 2.0) is None and FD.off_canvas({"odd": odd}, None) is None)
            check("no render is None", FD.shipping_png("none", [2.0, 2.0]) is None)
        finally:
            FD.job_png, FD.FIT = saved, saved_fit
    check("a canvas hold is no verdict: the candidate stays owed",
          FD.judged_set([("r", {"subject": "D", "candidate": "r1", "decision": "HOLD_CANVAS"})]) == set())

    # ARTEVAL_FILE_REGENS_JOBID_FIX_SERIES_TAG: a candidate judged under an adopted non-fauna run counts; an
    # unadopted audit run does not; a HOLD_ERROR (transport failure, no verdict) is not "judged"
    with tempfile.TemporaryDirectory() as td:
        runs, ad = Path(td) / "runs", Path(td) / "adopt.jsonl"
        for name, cand, dec, at in (("fauna_t_00", None, "REGEN", "2026-10-27T10:00:00+00:00"),
                                    ("judgestall_t", "s2r1", "REGEN", "2026-10-28T10:00:00+00:00"),
                                    ("audit_t", "r1", "ACCEPT", "2026-10-28T11:00:00+00:00")):
            (runs / name).mkdir(parents=True)
            (runs / name / "run.json").write_text(json.dumps({"test": False}))
            (runs / name / "decisions.jsonl").write_text(json.dumps({"subject": "D", "decision": dec, "candidate": cand,
                                                                     "at": at}) + "\n")
        ad.write_text(json.dumps({"run": "judgestall_t", "why": "t"}) + "\n")
        orig, orig_ad = RS.production_decisions, RS.ADOPTIONS
        RS.production_decisions, RS.ADOPTIONS = (lambda: orig(runs)), ad
        try:
            got = sorted(r for r, _ in FD.production())
            check("production() = fauna_* + adopted, not audit", got == ["fauna_t_00", "judgestall_t"], got)
            check("latest candidate comes from the adopted run", (FD.latest("D", True) or {}).get("candidate") == "s2r1")
            check("first pass latest stays the fauna_ run", (FD.latest("D", False) or {}).get("candidate") is None
                  and (FD.latest("D", False) or {}).get("decision") == "REGEN")
        finally:
            RS.production_decisions, RS.ADOPTIONS = orig, orig_ad
    js = FD.judged_set([("r", {"subject": "D", "candidate": "r1", "decision": "HOLD_ERROR"}),
                        ("r", {"subject": "E", "candidate": "r1", "decision": "HOLD_INPUT"}),
                        ("r", {"subject": "F", "candidate": "r2", "decision": "REGEN"})])
    check("HOLD_ERROR is not judged; other decisions are", js == {("E", "r1"), ("F", "r2")}, js)

    # FAUNA_INSTALL_CHECK_RENDER_IS_JUDGED: the render sha must equal the judged source sha
    j = {"south": "a" * 64}
    check("matching sha passes", FD.render_is_judged(j, "south", "a" * 64))
    check("re-rendered (different) sha refused", not FD.render_is_judged(j, "south", "b" * 64))
    check("record without that facing's sha refused", not FD.render_is_judged(j, "east", "a" * 64))
    check("record with no shas refused", not FD.render_is_judged(None, "south", "a" * 64))
    # ARTEVAL_REGEN_ROWS_FIX_MISSING_TARGET: a flyer's regen row must name its body texPath or fill_queue refuses it
    tp = lambda d: {"RM_Fly": "Things/Pawn/Animal/Fly/Fly"}.get(d)
    check("row with no target gets the body texPath", FD.bind_texpath({"target_def": "RM_Fly"}, tp).get("target_texpath") == "Things/Pawn/Animal/Fly/Fly")
    check("row's own texPath is kept", FD.bind_texpath({"target_def": "RM_Fly", "target_texpath": "X/Y"}, tp)["target_texpath"] == "X/Y")
    check("row with install_to is left alone", "target_texpath" not in FD.bind_texpath({"target_def": "RM_Fly", "install_to": "a.png"}, tp))
    check("unresolvable def stays unbound (fill_queue refuses loudly)", "target_texpath" not in FD.bind_texpath({"target_def": "RM_None"}, tp))
    check("real flyer resolves its adult body", FD.bind_texpath({"target_def": "RM_FireHawk"}).get("target_texpath", "").endswith("/FireHawk/FireHawk"))
    # FURNACEBEAST_ART_INSTALL_OWNER_KEPT_IT: an ACCEPTed art-eval redraw of kept art is installable whatever the
    # first-pass band (owner card 2026-10-23 06:42, shown to him after with a revert); only a keep he made AFTER the
    # first pass is his newer word
    check("kept art, WEAK first pass: gate lets the ACCEPT through", FD.kept_refusal("RM_X", [], {"at": "t"}) is None)
    check("a keep newer than the first pass still blocks", "newer word" in (FD.kept_refusal("RM_X", [{"id": "k1"}], {"at": "t"}) or ""))
    kw = FD.install_provenance(True, "v")
    check("kept install carries the card and a delegated digest why", "--by-card" in kw and any(str(x).startswith("delegated: art-eval redraw of kept art") for x in kw))
    uw = FD.install_provenance(False, "v")
    check("unkept install keeps its delegated why", any(str(x).startswith("delegated:") for x in uw) and "--by-card" not in uw)
    # a failed Sonnet rewrite (session limit) must never become the prompt: Flamefang/Ashwallow/Sytheclaw r2 were
    # rendered from "You've hit your session limit ..." (ARTEVAL_REGEN_PROMPT_FIX_LIMIT_TEXT)
    real = FD.R.call_claude
    try:
        FD.R.call_claude = lambda *a, **k: ("You've hit your session limit · resets 1:10pm", {"error": "limit"})
        p, by = FD.neutral_prompt("A red beast. Seen from the side view. Transparent background.")
        check("rewrite error falls back to sentence-drop", by == "sentence-drop" and "session limit" not in p and "red beast" in p)
        FD.R.call_claude = lambda *a, **k: ("", {"error": "timeout"})
        check("empty rewrite falls back", FD.neutral_prompt("A red beast. Seen from the side view.")[1] == "sentence-drop")
    finally:
        FD.R.call_claude = real
    # an auto-judge run (fauna_auto_<stamp>) has no _rN_ in its name: its records' candidate tag says it is a candidate
    recs = [("fauna_auto_20261028_1101", {"subject": "D", "candidate": "r2", "decision": "ACCEPT", "at": "2026-10-28T11:04:59-07:00"}),
            ("fauna_D_r1_00", {"subject": "D", "candidate": "r1", "decision": "REGEN", "at": "2026-10-23T10:15:58-07:00"}),
            ("fauna_glass_reef_00", {"subject": "D", "candidate": "live", "decision": "REGEN", "at": "2026-10-23T09:43:10-07:00"})]
    check("latest candidate reads an auto run's candidate tag", (FD.latest("D", True, recs) or {}).get("candidate") == "r2")
    check("a first-pass 'live' record stays first pass", (FD.latest("D", False, recs) or {}).get("candidate") == "live")
    # FRESH_SERIES_STOP_FIX_AFTER_OWNER_KEEP: he kept Crustweevil/Dustflutter/Fuzzrunner's live art while s1 ran and
    # the series went on; an owner keep of the live art newer than the reset halts it until a newer reset (re-ask)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        live = td / "Crust_south.png"
        live.write_bytes(b"x")
        spec = {"images": {"south": str(live), "scale": str(live)}}
        rl = td / "round_resets.jsonl"
        rl.write_text(json.dumps({"at": "2026-10-24T06:30:00-07:00", "def": "RM_Crust", "series": 1, "source_run": "r"}) + "\n")
        keeps = {"S": [{"id": "keep_new", "ts": "2026-10-24T07:00:00-07:00"}]}
        prot, sha = (lambda h: keeps.get(h, [])), (lambda p: "S")
        why = FD.halted("RM_Crust", spec, RS.resets(rl), prot, sha)
        check("keep of live art after the reset halts the series", bool(why) and "keep_new" in why, why)
        keeps["S"] = [{"id": "keep_old", "ts": "2026-10-23T07:00:00-07:00"}]
        check("keep older than the reset does not halt", FD.halted("RM_Crust", spec, RS.resets(rl), prot, sha) is None)
        keeps["S"] = [{"id": "keep_nots"}]
        check("unstamped keep cannot be shown newer", FD.halted("RM_Crust", spec, RS.resets(rl), prot, sha) is None)
        keeps["S"] = [{"id": "keep_new", "ts": "2026-10-24T07:00:00-07:00"}]
        with rl.open("a") as fh:
            fh.write(json.dumps({"at": "2026-10-25T06:30:00-07:00", "def": "RM_Crust", "series": 2, "source_run": "r", "owner_said": "redo it"}) + "\n")
        check("a newer reset (he re-asks) lifts the halt", FD.halted("RM_Crust", spec, RS.resets(rl), prot, sha) is None)
        check("no series, no halt", FD.halted("RM_Other", spec, RS.resets(rl), prot, sha) is None)
        with rl.open("a") as fh:
            fh.write(json.dumps({"at": "2026-10-25T07:00:00-07:00", "def": "RM_Crust", "stop": True, "series": 2, "why": "kept"}) + "\n")
        check("an explicit stop still halts", "STOPPED" in (FD.halted("RM_Crust", spec, RS.resets(rl), prot, sha) or ""))
        # the commands honour it: install refuses with rc 2 before touching the ledger
        (td / "specs").mkdir()
        (td / "specs" / "RM_Crust.spec.json").write_text(json.dumps(spec))
        rl.write_text(json.dumps({"at": "2026-10-24T06:30:00-07:00", "def": "RM_Crust", "series": 1, "source_run": "r"}) + "\n")
        orig_res, orig_halt = RS.resets, FD.halted
        try:
            RS.resets = lambda path=rl: orig_res(rl)
            FD.halted = lambda d, sp, rs=None: orig_halt(d, sp, rs, prot, sha)
            import argparse
            rc = FD.cmd_install(argparse.Namespace(defname="RM_Crust", specs=str(td / "specs"), round=1, dry_run=True))
            check("install refuses a def he kept after the reset", rc == 2, rc)
        finally:
            RS.resets, FD.halted = orig_res, orig_halt
    print("FAILED: " + ", ".join(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
