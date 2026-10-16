#!/usr/bin/env python3
"""selftest_canon_check.py — canon_check.py's parsing/grading/CLI and artpiped's canon ADVISOR (never a gate),
with a MOCKED vision call. Never invokes codex.exe.

    python3 selftest_canon_check.py
"""
from __future__ import annotations

import json
import queue
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artpiped  # noqa: E402
import canon_check  # noqa: E402
import common  # noqa: E402
import selftest_artpipe as sa  # noqa: E402 — Queue/make_job fixtures (mock worker, temp queue)

FAILED: list[str] = []


def ok(name, cond, detail=""):
    print(("ok    " if cond else "FAIL  ") + name + ("" if cond else f"\n      {detail}"))
    if not cond:
        FAILED.append(name)


def reply(*verdicts, summary="s"):
    return json.dumps({"lines": [{"n": i, "verdict": v, "reason": f"r{i}"} for i, v in enumerate(verdicts, 1)],
                       "summary": summary})


class MockVision:
    """Returns queued replies in order; records every call's prompt + images."""
    def __init__(self, *replies):
        self.replies, self.calls = list(replies), []

    def __call__(self, prompt, images, **kw):
        self.calls.append({"prompt": prompt, "images": [str(p) for p in images], "kw": kw})
        r = self.replies.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


OWNER_JOB = {"id": "t_owner", "facing": "south",
             "prompt": "RimWorld creature sprite: a glassy grazer. Previous attempt was rejected because it ate a "
                       "plant. RULE (owner, 2026-10-04): pale blue body. The creature is ALONE."}


def test_parsing():
    sec = "- [ ] Green skin\n- [x] Six legs radiating\n  from a small body\n* plain bullet\n1. numbered\nprose line\n"
    ok("must_show_lines: checkbox, wrapped continuation, bullet, numbered; prose ignored",
       canon_check.must_show_lines(sec) == ["Green skin", "Six legs radiating from a small body", "plain bullet",
                                            "numbered"], canon_check.must_show_lines(sec))
    lines = canon_check.owner_note_lines(OWNER_JOB)
    ok("owner_note_lines: prompt tail from the first owner/rejection sentence",
       lines[0].startswith("Previous attempt was rejected") and len(lines) == 3, lines)
    ok("owner_note_lines: explicit owner_note list wins",
       canon_check.owner_note_lines(dict(OWNER_JOB, owner_note=["a", " ", "b"])) == ["a", "b"])
    ok("owner_note_lines: no owner marker -> none",
       canon_check.owner_note_lines({"prompt": "a small weathered supply crate."}) == [])
    retried = dict(OWNER_JOB, prompt=OWNER_JOB["prompt"] + f" {canon_check.CORRECTIONS_HEAD} (old retry): (1) MUST: x")
    ok("owner_note_lines: appended CANON CORRECTIONS are not re-read as owner lines",
       canon_check.owner_note_lines(retried) == lines)


def test_resolve_and_gather():
    acklay = canon_check.CANON_ROOT / "acklay"
    if not (acklay / "description.md").is_file():
        ok("fixture: acklay canon entry present", False, str(acklay))
        return
    s, how = canon_check.resolve_slug({"target_canon": "acklay"}, use_subject=False)
    ok("resolve_slug: target_canon", s == "acklay" and how == "target_canon")
    img = next(p for p in acklay.iterdir() if p.suffix == ".jpg")
    s, how = canon_check.resolve_slug({"canon_reference": [str(img)]}, use_subject=False)
    ok("resolve_slug: canon_reference image's entry dir", s == "acklay", how)
    s, how = canon_check.resolve_slug({"prompt": "x", "style_notes": "brief (design/RimStarWars/canon_references/"
                                       "acklay/description.md): green"}, use_subject=False)
    ok("resolve_slug: canon_references/<slug>/ named in style_notes", s == "acklay", how)
    ok("resolve_slug: nothing -> None", canon_check.resolve_slug({"prompt": "crate"}, use_subject=False)[0] is None)
    spec = canon_check.gather({"target_canon": "acklay", "prompt": "p", "facing": "east"}, use_subject=False)
    ok("gather: canon spec carries Must show lines, brief, non-donor images",
       spec["kind"] == "canon" and len(spec["lines"]) >= 3 and spec["brief"]
       and spec["images"] and not any("donor_" in Path(p).name for p in spec["images"]), spec and spec["images"])
    ok("gather: owner-only job -> owner spec", canon_check.gather(OWNER_JOB, use_subject=False)["kind"] == "owner")
    ok("gather: neither -> None", canon_check.gather({"prompt": "a crate."}, use_subject=False) is None)


def test_grade():
    spec = canon_check.gather(OWNER_JOB, use_subject=False)
    mv = MockVision(reply("pass", "na", "pass"))
    v = canon_check.grade(Path("/x/render.png"), spec, vision=mv)
    ok("grade: PASS, na lines excluded from the score", v["verdict"] == "PASS" and v["score"] == "2/2"
       and v["na"] == 1, v)
    ok("grade: render is image 1, prompt numbers every line",
       mv.calls[0]["images"][0] == "/x/render.png" and "3. " in mv.calls[0]["prompt"])
    v = canon_check.grade(Path("/x/r.png"), spec, vision=MockVision(reply("pass", "fail", "pass")))
    ok("grade: any fail -> FAIL", v["verdict"] == "FAIL" and v["score"] == "2/3")
    try:
        canon_check.grade(Path("/x/r.png"), spec, vision=MockVision(reply("pass", "pass")))
        ok("grade: a skipped line raises", False)
    except canon_check.CanonCheckError:
        ok("grade: a skipped line raises (never silently counted)", True)
    ok("grade: advisory verdict carries the flagged line and its reason",
       v["advisory"] and v["flags"] == [{"line": spec["lines"][1], "reason": "r2"}], v.get("flags"))
    a = canon_check.advisory_text(v)
    ok("advisory_text: names the flagged line, reason and score", "advisory" in a and "2/3" in a
       and spec["lines"][1] in a and "r2" in a, a)
    v0 = canon_check.grade(Path("/x/r.png"), spec, vision=MockVision(reply("na", "na", "na")))
    ok("grade: 0/0 (every line n/a) is UNGRADED, never PASS", v0["verdict"] == "UNGRADED" and v0["score"] == "0/0", v0)
    ok("advisory_text: UNGRADED says nothing was checked", "UNGRADED" in canon_check.advisory_text(v0))
    old = {"status": "graded", "verdict": "PASS", "score": "0/0", "graded": 0, "lines": []}
    ok("normalize: an old stored 0/0 PASS reads UNGRADED", canon_check.normalize(old)["verdict"] == "UNGRADED")
    old_fail = {"status": "graded", "verdict": "FAIL", "score": "1/2", "graded": 2,
                "lines": [{"line": "L1", "verdict": "pass", "reason": "a"}, {"line": "L2", "verdict": "fail", "reason": "b"}]}
    ok("normalize: Python-repr string and missing flags are read", canon_check.normalize(repr(old_fail))["flags"]
       == [{"line": "L2", "reason": "b"}])
    ok("normalize: unreadable -> None", canon_check.normalize("not a dict {") is None)


def test_facing_tags():
    lf = canon_check.line_facings
    ok("tag [not:north] -> every facing but north, stripped",
       lf("Big round eyes [not:north]") == ("Big round eyes", frozenset({"east", "south", "west"}), None))
    ok("tag [only:east,west]", lf("[only:east, west] long tail in profile")[1] == frozenset({"east", "west"}))
    ok("tag [east-only]", lf("Tail visible [east-only]")[:2] == ("Tail visible", frozenset({"east"})))
    ok("no tag -> None", lf("Green skin") == ("Green skin", None, None))
    t, al, err = lf("Eyes [not:nroth]")
    ok("unknown facing: line untouched, untagged, error reported", t == "Eyes [not:nroth]" and al is None and err, err)
    job = {"id": "t", "facing": "north", "prompt": "p",
           "owner_note": ["Big round eyes [not:north].", "Forked tail.", "Eyes [not:nroth]."]}
    spec = canon_check.gather(job, use_subject=False)
    ok("gather: tags stripped from lines, kept parallel", spec["lines"][0] == "Big round eyes." and
       spec["line_facings"][1] is None and spec["tag_errors"], spec)
    mv = MockVision(reply("fail", "pass", "pass"))
    v = canon_check.grade(Path("/x/r.png"), spec, vision=mv)
    ok("grade: a tagged line on a facing it excludes is n/a in CODE, overriding the model",
       v["lines"][0]["verdict"] == "na" and v["lines"][0].get("facing_na") and v["verdict"] == "PASS"
       and v["score"] == "2/2" and v["tag_errors"], v)
    ok("grade: the prompt tells the model line 1 is n/a", "N/A for this job" in mv.calls[0]["prompt"] and ": 1" in mv.calls[0]["prompt"])
    v = canon_check.grade(Path("/x/r.png"), dict(spec, facing="south"), vision=MockVision(reply("fail", "pass", "pass")))
    ok("grade: the same line on an allowed facing is graded", v["verdict"] == "FAIL" and v["score"] == "2/3", v)
    v = canon_check.grade(Path("/x/r.png"), dict(spec, facing=None), vision=MockVision(reply("fail", "pass", "pass")))
    ok("grade: a job with no facing ignores tags", v["lines"][0]["verdict"] == "fail")
    gspec = dict(spec, kind="canon", images=[])
    mv = MockVision(json.dumps({"canon_description": "", "render_description": "R"}),
                    reply("pass", "pass", "fail", "pass", "pass"))
    v = canon_check.grade(Path("/x/r.png"), gspec, vision=mv, mode="v2")
    ok("v2: facing tags shift past the gate lines", v["lines"][2]["verdict"] == "na" and v["verdict"] == "PASS", v)


def test_canon_na():
    job = dict(OWNER_JOB, canon_na=[2, "pale blue body"], canon_na_reason="subspecies differs")
    job["owner_note"] = ["Line one.", "Pale blue body.", "Line three."]
    job["canon_na"] = [2, "line three."]
    spec = canon_check.gather(job, use_subject=False)
    mv = MockVision(reply("pass", "fail", "fail"))
    v = canon_check.grade(Path("/x/r.png"), spec, vision=mv)
    ok("canon_na: marked lines forced n/a with reason, not counted",
       v["verdict"] == "PASS" and v["score"] == "1/1" and v["na"] == 2
       and v["lines"][1]["verdict"] == "na" and "subspecies differs" in v["lines"][1]["reason"], v)
    ok("canon_na: prompt tells the grader which lines", "marked N/A" in mv.calls[0]["prompt"])
    ok("canon_na: owner_note field is used as the lines (not the prompt)", spec["lines"][0] == "Line one.")
    try:
        canon_check.grade(Path("/x/r.png"), canon_check.gather(dict(job, canon_na=[99]), use_subject=False),
                          vision=MockVision(reply("pass", "pass", "pass")))
        ok("canon_na: unmatched mark raises", False)
    except canon_check.CanonCheckError:
        ok("canon_na: unmatched mark raises", True)


def test_v2_mode():
    job = {"id": "t_c", "facing": "south", "prompt": "a creature", "target_canon": "t",
           "owner_note": ["Pale body."]}
    spec = {"kind": "canon", "slug": "t", "slug_via": "x", "lines": ["Has a tail", "Two horns"], "brief": "", "engine_limits": "",
            "images": ["/c/1.png"], "owner_note": [], "facing": "south", "prompt": "p", "na_marks": [1], "na_reason": ""}
    desc = json.dumps({"canon_description": "CANONTEXT", "render_description": "RENDERTEXT"})
    mv = MockVision(desc, reply("pass", "fail", "pass", "pass"))
    v = canon_check.grade(Path("/x/r.png"), spec, vision=mv, mode="v2")
    ok("v2: two calls, describe first with the descriptions schema",
       len(mv.calls) == 2 and mv.calls[0]["kw"].get("schema") is canon_check.DESCRIBE_SCHEMA
       and "CANON" in mv.calls[0]["prompt"] and "MUST SHOW" not in mv.calls[0]["prompt"], mv.calls[0]["prompt"][:200])
    p2 = mv.calls[1]["prompt"]
    ok("v2: grading prompt carries both descriptions and the gate lines before the Must-show lines",
       "CANONTEXT" in p2 and "RENDERTEXT" in p2 and p2.index("GATE: OVERALL BODY PLAN") < p2.index("Has a tail")
       and "GATE: COLOUR LAYOUT" in p2)
    ok("v2: a failed gate line fails the verdict and is flagged; Must-show numbering shifted past the gates",
       v["verdict"] == "FAIL" and v["gate_failed"] and v["mode"] == "v2" and v["lines"][0]["gate"]
       and v["lines"][2]["line"] == "Has a tail", v)
    ok("v2: canon_na int mark shifts with the gates (mark 1 -> original line 1 'Has a tail')",
       v["lines"][2]["verdict"] == "na", v["lines"][2])
    mv = MockVision(desc, reply("pass", "pass", "pass", "pass"))
    ok("v2: all pass -> PASS", canon_check.grade(Path("/x/r.png"), dict(spec, na_marks=[]), vision=mv, mode="v2")["verdict"] == "PASS")
    ospec = canon_check.gather(OWNER_JOB, use_subject=False)
    mv = MockVision(json.dumps({"canon_description": "", "render_description": "R"}), reply("pass", "pass", "pass"))
    v = canon_check.grade(Path("/x/r.png"), ospec, vision=mv, mode="v2")
    ok("v2: owner-note jobs get no gate lines", v["graded"] == 3 and not any(r.get("gate") for r in v["lines"]), v)
    try:
        canon_check.grade(Path("/x/r.png"), spec, vision=MockVision(json.dumps({"render_description": ""})), mode="v2")
        ok("v2: empty render description raises", False)
    except canon_check.CanonCheckError:
        ok("v2: empty render description raises", True)
    mv = MockVision(reply("pass", "pass", "pass", "pass"))
    canon_check.grade(Path("/x/r.png"), dict(spec, na_marks=[]), vision=mv)
    ok("default mode is v1: one call, no gate lines", len(mv.calls) == 1 and "GATE:" not in mv.calls[0]["prompt"])
    try:
        canon_check.grade(Path("/x/r.png"), spec, vision=MockVision(), mode="v3")
        ok("unknown mode raises", False)
    except canon_check.CanonCheckError:
        ok("unknown mode raises", True)


def _ctx(vision, tmp: Path):
    slots = queue.Queue()
    slots.put(0)
    return SimpleNamespace(canon_vision=vision, canon_model="mock", slots=slots,
                           codex_home_for_slot=lambda s: tmp / "home")


def test_gate_in_process():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        out = tmp / "t_owner.png"
        out.write_bytes(b"first")
        r = artpiped.canon_gate(OWNER_JOB, "t_owner", {"status": "ok"}, out,
                                _ctx(MockVision(reply("pass", "pass", "pass")), tmp))
        ok("advisor: PASS stores verdict + advisory line, job stays ok",
           r["status"] == "ok" and r["canon_check"]["score"] == "3/3" and "PASS" in r["canon_advisory"])
        mv = MockVision(reply("fail", "pass", "pass"))
        r = artpiped.canon_gate(OWNER_JOB, "t_owner", {"status": "ok", "elapsed_s": 1}, out, _ctx(mv, tmp))
        ok("advisor: FAIL never fails the job, never re-renders, attaches the flagged line",
           r["status"] == "ok" and "worker_status" not in r and r["canon_check"]["verdict"] == "FAIL"
           and len(mv.calls) == 1 and "r1" in r["canon_advisory"] and "canon_first_attempt" not in r
           and out.read_bytes() == b"first" and not (tmp / "t_owner.canon_attempt1.png").exists(), r)
        r = artpiped.canon_gate(dict(OWNER_JOB, canon_retry=1), "t_owner", {"status": "ok"}, out,
                                _ctx(MockVision(reply("fail", "fail", "fail")), tmp))
        ok("advisor: an old retried job with every line failing is still ok", r["status"] == "ok")
        r = artpiped.canon_gate(OWNER_JOB, "t_owner", {"status": "ok"}, out,
                                _ctx(MockVision(reply("na", "na", "na")), tmp))
        ok("advisor: 0/0 -> UNGRADED, ok", r["status"] == "ok" and r["canon_check"]["verdict"] == "UNGRADED")
        r = artpiped.canon_gate(OWNER_JOB, "t_owner", {"status": "ok"}, out,
                                _ctx(MockVision(RuntimeError("codex down")), tmp))
        ok("advisor: grader outage keeps the render ok, records error",
           r["status"] == "ok" and r["canon_check"]["status"] == "error")
        r = artpiped.canon_gate(dict(OWNER_JOB, canon_na=[99]), "t_owner", {"status": "ok"}, out,
                                _ctx(MockVision(reply("pass", "pass", "pass")), tmp))
        ok("advisor: a bad canon_na mark is an error record, never a failed job",
           r["status"] == "ok" and r["canon_check"]["status"] == "error", r)
        r = artpiped.canon_gate({"id": "c", "prompt": "a crate."}, "c", {"status": "ok"}, out, _ctx(MockVision(), tmp))
        ok("advisor: nothing to grade -> skipped", r["canon_check"]["status"] == "skipped")
        r = artpiped.canon_gate(OWNER_JOB, "t", {"status": "failed"}, out, _ctx(MockVision(), tmp))
        ok("advisor: a render that failed earlier gates is never graded", "canon_check" not in r)
        r = artpiped.canon_gate(OWNER_JOB, "t", {"status": "ok"}, out, _ctx(None, tmp))
        ok("advisor: canon_vision None -> off", "canon_check" not in r)


def test_daemon_end_to_end():
    with tempfile.TemporaryDirectory() as td:
        q = sa.Queue(Path(td))
        sa.make_job(q.pending, "t_owner", q.reference, prompt=OWNER_JOB["prompt"])
        mock_path = Path(td) / "vision.json"
        mock_path.write_text(json.dumps({"first": json.loads(reply("fail", "pass", "pass"))}))
        import os
        os.environ["ARTPIPE_CANON_VISION_MOCK"] = str(mock_path)
        try:
            proc = q.run({}, "--once", "-N", "1", timeout=120)
        finally:
            del os.environ["ARTPIPE_CANON_VISION_MOCK"]
        mp = q.done / "t_owner.manifest.json"
        m = json.loads(mp.read_text()) if mp.is_file() else {}
        ok("daemon: a canon FAIL files to done/ as ok with the verdict and advisory line on the manifest",
           m.get("status") == "ok" and m.get("canon_check", {}).get("verdict") == "FAIL"
           and "advisory" in m.get("canon_advisory", "") and not (q.failed / "t_owner.manifest.json").exists(),
           f"rc={proc.returncode} manifest={json.dumps(m)[:600]} stderr={proc.stderr[-800:]}")


def test_cli():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        done, failed, pending, artsrc = (tmp / d for d in ("done", "failed", "pending", "_artsrc"))
        for d in (done, failed, pending, artsrc / "t_owner"):
            d.mkdir(parents=True)
        common.atomic_write_json(done / "t_owner.json", dict(OWNER_JOB, created="2026-10-04T21:00:00Z"))
        common.atomic_write_json(done / "t_owner.manifest.json", {"id": "t_owner", "status": "ok"})
        (artsrc / "t_owner" / "t_owner.png").write_bytes(b"png")
        kw = dict(done=done, failed=failed, artsrc=artsrc, force=False, dry_run=False)
        r = canon_check.check_one("t_owner", vision=MockVision(reply("fail", "pass", "na")), **kw)
        m = json.loads((done / "t_owner.manifest.json").read_text())
        ok("cli: verdict written to the done manifest and a sidecar beside the render",
           m["canon_check"]["score"] == "1/2" and (artsrc / "t_owner" / "t_owner.canon_check.json").is_file())
        r2 = canon_check.check_one("t_owner", vision=MockVision(), **kw)
        ok("cli: an already-graded render is not re-graded without --force", r2["status"] == "already")
        ok("cli: nothing is requeued (advisor)", not list(pending.iterdir()) and not hasattr(canon_check, "requeue"))
        try:
            import contextlib
            import io
            with contextlib.redirect_stderr(io.StringIO()):
                canon_check.main(["t_owner", "--requeue"])
            ok("cli: --requeue is gone", False)
        except SystemExit:
            ok("cli: --requeue is gone", True)
        r3 = canon_check.check_one("t_owner", vision=MockVision(), **dict(kw, dry_run=True, force=True))
        ok("cli: --dry-run writes nothing", r3["status"] == "dry"
           and json.loads((done / "t_owner.manifest.json").read_text())["canon_check"]["score"] == "1/2")


def main():
    for t in (test_parsing, test_resolve_and_gather, test_grade, test_facing_tags, test_canon_na, test_v2_mode, test_gate_in_process, test_daemon_end_to_end,
              test_cli):
        try:
            t()
        except Exception as exc:  # noqa: BLE001
            ok(f"{t.__name__} raised", False, f"{type(exc).__name__}: {exc}")
    print(f"\n{'FAILED: ' + ', '.join(FAILED) if FAILED else 'all passed'}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
