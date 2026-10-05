#!/usr/bin/env python3
"""selftest_canon_check.py — CANON_RENDER_GATE_1: canon_check.py's parsing/grading/CLI and artpiped's canon gate,
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
    retried = canon_check.with_corrections(OWNER_JOB, {"kind": "owner", "lines": [
        {"line": "pale blue body.", "verdict": "fail", "reason": "it is red"}]})
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
    c = canon_check.corrections_text(v)
    ok("corrections_text: names only the failed line and its reason",
       "RULE (owner" in c and "r2" in c and "Previous attempt" not in c, c)
    j2 = canon_check.with_corrections(canon_check.with_corrections(OWNER_JOB, v), v)
    ok("with_corrections: replaces (never stacks) earlier corrections; counts retries",
       j2["prompt"].count(canon_check.CORRECTIONS_HEAD) == 1 and j2["canon_retry"] == 2)


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


def _ctx(vision, tmp: Path):
    slots = queue.Queue()
    slots.put(0)
    return SimpleNamespace(canon_vision=vision, canon_model="mock", slots=slots,
                           codex_home_for_slot=lambda s: tmp / "home")


def test_gate_in_process():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        out = tmp / "t_owner.png"

        def rerun_writer(calls):
            def rerun(job):
                calls.append(job)
                out.write_bytes(b"retry")
                return {"id": job["id"], "channel": "codex", "status": "ok", "elapsed_s": 2}
            return rerun

        out.write_bytes(b"first")
        r = artpiped.canon_gate(OWNER_JOB, "t_owner", {"status": "ok"}, out,
                                _ctx(MockVision(reply("pass", "pass", "pass")), tmp), rerun=None)
        ok("gate: PASS stores verdict, job stays ok", r["status"] == "ok" and r["canon_check"]["score"] == "3/3")

        calls = []
        r = artpiped.canon_gate(OWNER_JOB, "t_owner", {"status": "ok", "elapsed_s": 1}, out,
                                _ctx(MockVision(reply("fail", "pass", "pass"), reply("pass", "pass", "pass")), tmp),
                                rerun=rerun_writer(calls))
        ok("gate: FAIL -> one corrected re-render -> PASS is ok",
           r["status"] == "ok" and r["canon_check"]["verdict"] == "PASS" and len(calls) == 1
           and canon_check.CORRECTIONS_HEAD in calls[0]["prompt"] and calls[0]["canon_retry"] == 1, r)
        first = tmp / "t_owner.canon_attempt1.png"
        ok("gate: first render kept as canon_attempt1 with its verdict",
           first.read_bytes() == b"first" and r["canon_first_attempt"]["canon_check"]["verdict"] == "FAIL")

        out.write_bytes(b"first")
        calls = []
        r = artpiped.canon_gate(OWNER_JOB, "t_owner", {"status": "ok"}, out,
                                _ctx(MockVision(reply("fail", "pass", "pass"), reply("fail", "fail", "pass")), tmp),
                                rerun=rerun_writer(calls))
        ok("gate: FAIL twice -> failed_canon with the second verdict",
           r["status"] == "failed" and r["worker_status"] == "failed_canon" and r["canon_check"]["score"] == "1/3"
           and len(calls) == 1, r)

        r = artpiped.canon_gate(dict(OWNER_JOB, canon_retry=1), "t_owner", {"status": "ok"}, out,
                                _ctx(MockVision(reply("fail", "pass", "pass")), tmp), rerun=rerun_writer([]))
        ok("gate: a job already retried once is not retried again", r["worker_status"] == "failed_canon")

        r = artpiped.canon_gate(OWNER_JOB, "t_owner", {"status": "ok"}, out,
                                _ctx(MockVision(RuntimeError("codex down")), tmp), rerun=None)
        ok("gate: grader outage keeps the render ok, records error",
           r["status"] == "ok" and r["canon_check"]["status"] == "error")
        r = artpiped.canon_gate({"id": "c", "prompt": "a crate."}, "c", {"status": "ok"}, out,
                                _ctx(MockVision(), tmp), rerun=None)
        ok("gate: nothing to grade -> skipped", r["canon_check"]["status"] == "skipped")
        r = artpiped.canon_gate(OWNER_JOB, "t", {"status": "failed"}, out, _ctx(MockVision(), tmp), rerun=None)
        ok("gate: a render that failed earlier gates is never graded", "canon_check" not in r)
        r = artpiped.canon_gate(OWNER_JOB, "t", {"status": "ok"}, out, _ctx(None, tmp), rerun=None)
        ok("gate: canon_vision None -> gate off", "canon_check" not in r)


def test_daemon_end_to_end():
    for name, mock, want_dir, want_status in (
            ("retry-pass", {"first": json.loads(reply("fail", "pass", "pass")),
                            "retry": json.loads(reply("pass", "pass", "pass"))}, "done", "ok"),
            ("retry-fail", {"first": json.loads(reply("fail", "pass", "pass")),
                            "retry": json.loads(reply("fail", "pass", "pass"))}, "failed", "failed_canon")):
        with tempfile.TemporaryDirectory() as td:
            q = sa.Queue(Path(td))
            sa.make_job(q.pending, "t_owner", q.reference, prompt=OWNER_JOB["prompt"])
            mock_path = Path(td) / "vision.json"
            mock_path.write_text(json.dumps(mock))
            import os
            os.environ["ARTPIPE_CANON_VISION_MOCK"] = str(mock_path)
            try:
                proc = q.run({}, "--once", "-N", "1", timeout=120)
            finally:
                del os.environ["ARTPIPE_CANON_VISION_MOCK"]
            mp = getattr(q, want_dir) / "t_owner.manifest.json"
            m = json.loads(mp.read_text()) if mp.is_file() else {}
            got = m.get("status") if want_status == "ok" else m.get("worker_status")
            ok(f"daemon {name}: filed to {want_dir}/ as {want_status}, both verdicts on the manifest",
               got == want_status and m.get("canon_check", {}).get("status") == "graded"
               and m.get("canon_first_attempt", {}).get("canon_check", {}).get("verdict") == "FAIL",
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
        dst = canon_check.requeue(r["job"], r["check"], pending)
        j = json.loads(dst.read_text())
        ok("cli: --requeue files the job to pending/ with corrections and canon_retry=1",
           canon_check.CORRECTIONS_HEAD in j["prompt"] and j["canon_retry"] == 1)
        r3 = canon_check.check_one("t_owner", vision=MockVision(), **dict(kw, dry_run=True, force=True))
        ok("cli: --dry-run writes nothing", r3["status"] == "dry"
           and json.loads((done / "t_owner.manifest.json").read_text())["canon_check"]["score"] == "1/2")


def main():
    for t in (test_parsing, test_resolve_and_gather, test_grade, test_canon_na, test_gate_in_process, test_daemon_end_to_end,
              test_cli):
        try:
            t()
        except Exception as exc:  # noqa: BLE001
            ok(f"{t.__name__} raised", False, f"{type(exc).__name__}: {exc}")
    print(f"\n{'FAILED: ' + ', '.join(FAILED) if FAILED else 'all passed'}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
