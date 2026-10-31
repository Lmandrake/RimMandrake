#!/usr/bin/env python3
"""selftest_arena_reader_pass.py — arena_reader_pass.py with a STUB reader (no GPT, no claude, no real pool).

A synthetic arena root (tasks/, judge/hidden/, judge/vet_cache.jsonl) over a two-commit temp git repo. Proves: the
packet holds the task text, every scored check body with its base tail and the fix diff, and no unscored check; the
prompt asks both questions; run writes one verdict per task, a rerun reads nothing, a changed packet is re-read, a
task with no base tail is never read; a bad reply writes nothing and is retried; apply turns verdicts into drop /
unscore (and refuses while a survivor is unread unless --partial); arena_trial reads the result; auto falls back to
claude when GPT fails; every default output path is judge-only.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_reader_pass as R  # noqa: E402
import arena_tasks as A  # noqa: E402
import arena_trial as T  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True,
                          env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                                   GIT_COMMITTER_EMAIL="t@t")).stdout.strip()


def fixture(d):
    repo = Path(d, "repo")
    (repo / "src").mkdir(parents=True)
    git(repo, "init", "-q")
    (repo / "src/tool.py").write_text("def f():\n    return 1\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD")
    (repo / "src/tool.py").write_text("def f():\n    return _private_two()\n\ndef _private_two():\n    return 2\n")
    (repo / "src/selftest_tool.py").write_text("from tool import f\nassert f() == 2\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fix: f returns 2")
    fix = git(repo, "rev-parse", "HEAD")
    p = A.paths(Path(d, "arena"))
    for k in ("tasks", "judge"):
        Path(p[k]).mkdir(parents=True)
    vet = []

    def task(tid, checks, unscored=False):
        Path(p["tasks"], tid + ".json").write_text(json.dumps({
            "id": tid, "source_item": tid[3:], "kind": "python-util", "prompt": "PROMPT-%s: make f return 2" % tid,
            "criteria": "CRITERIA-%s" % tid, "base_sha": base}))
        cs = []
        for i, (path, tail) in enumerate(checks):
            key = "%s-%d" % (tid, i)
            cs.append({"type": "fix_test", "path": path, "body": "BODY-%s-%d\nassert f() == 2\n" % (tid, i),
                       "command": "python3 " + path, "vet": {"key": key, "discriminates": True}})
            if tail is not None:
                vet.append({"key": key, "base_tail": tail, "base_result": "fail"})
        if unscored:
            cs.append({"type": "fix_test_unscored", "path": "src/UNSCORED.py", "body": "UNSCORED-BODY",
                       "vet": {"key": "u"}})
        Path(p["judge"], tid + ".json").write_text(json.dumps({"task": tid, "fix_sha": fix, "checks": cs}))

    task("RP_KEEP", [("src/selftest_tool.py", "AssertionError KEEP-TAIL")], unscored=True)
    task("RP_HALF", [("src/selftest_a.py", "tail a"), ("src/selftest_b.py", "tail b")])
    task("RP_ALLUN", [("src/selftest_c.py", "tail c")])
    task("RP_DROP", [("src/selftest_d.py", "tail d")])
    task("RP_NOTAIL", [("src/selftest_e.py", None)])
    Path(p["tasks"], "RP_NOHIDDEN.json").write_text(json.dumps({"id": "RP_NOHIDDEN", "source_item": "NOHIDDEN"}))
    A.vet_cache_path(p).write_text("".join(json.dumps(r) + "\n" for r in vet))
    return p, repo


PLAN = {"RP_KEEP": {"src/selftest_tool.py": "KEEP"},
        "RP_HALF": {"src/selftest_a.py": "KEEP", "src/selftest_b.py": "UNSCORE_CHECK"},
        "RP_ALLUN": {"src/selftest_c.py": "UNSCORE_CHECK"},
        "RP_DROP": {"src/selftest_d.py": "DROP_TASK"}}


class Stub:
    def __init__(self, plan=PLAN, bad=()):
        self.plan, self.bad, self.calls = plan, set(bad), []

    def __call__(self, prompt):
        tid = next(t for t in self.plan if ("PROMPT-%s:" % t) in prompt)
        self.calls.append(tid)
        rows = [{"path": pa, "tests_task": v == "KEEP", "solvable_from_text": v == "KEEP", "coupled": v != "KEEP",
                 "coupled_names": [] if v == "KEEP" else ["_private_two"], "verdict": v, "reason": "stub " + v}
                for pa, v in self.plan[tid].items()]
        if tid in self.bad:
            rows[0]["verdict"] = "KEEP"
            rows[0]["coupled"] = True                 # KEEP contradicting (b): must be refused
        return "Here you go:\n```json\n" + json.dumps({"checks": rows}) + "\n```\n", "stub"


def main():
    with tempfile.TemporaryDirectory() as d:
        p, repo = fixture(d)
        res = R.results_dir(p)
        check(R.survivors(p) == ["RP_ALLUN", "RP_DROP", "RP_HALF", "RP_KEEP", "RP_NOTAIL"],
              "survivors: tasks with a judge file holding a scored check (%s)" % R.survivors(p))
        pk = R.build_packet("RP_KEEP", p, repo)
        pr = R.render_prompt(pk)
        check("PROMPT-RP_KEEP" in pr and "CRITERIA-RP_KEEP" in pr, "packet/prompt holds the task text and criteria")
        check("BODY-RP_KEEP-0" in pr and "KEEP-TAIL" in pr, "packet holds the scored check body and its base tail")
        check("UNSCORED" not in pr and [c["path"] for c in pk["checks"]] == ["src/selftest_tool.py"],
              "an unscored check (fix_test_unscored) is not in the packet")
        check("fix: f returns 2" in pr and "_private_two" in pr and "src/tool.py" in pr,
              "packet holds the fix diff summary (stat + diff)")
        check("+assert f() == 2" not in pk["fix_diff"], "the fix diff leaves out the hidden check files themselves")
        check("(a)" in pr and "solvable_from_text" in pr and "(b)" in pr and "coupled" in pr,
              "prompt asks both questions per check")
        check(R.build_packet("RP_NOTAIL", p, repo)["missing_tails"] == ["src/selftest_e.py"],
              "a check with no vet-cache record is a missing tail")

        st = Stub(bad={"RP_HALF"})
        logs = []
        c = R.run(st, p, repo=repo, log=logs.append)
        check(c["read"] == 3 and c["errors"] == 1 and c["not_ready"] == 1,
              "run: 3 read, 1 bad reply refused, 1 not ready (%s)" % c)
        check(sorted(f.name for f in res.glob("*.json")) == ["RP_ALLUN.json", "RP_DROP.json", "RP_KEEP.json"],
              "one verdict file per task; none for the bad reply or the task without a tail")
        check("RP_NOTAIL" not in st.calls, "a not-ready task is never sent to the reader")
        v = json.loads((res / "RP_KEEP.json").read_text())
        check(v["schema"] == R.VERDICT_SCHEMA and v["task_verdict"] == "KEEP" and v["checks"][0]["reason"]
              and v["packet_sha256"] == R.packet_sha(pk), "verdict schema: per-check verdict + reason, packet hash")
        try:
            R.apply(p, repo=repo)
            check(False, "apply refuses while a survivor has no verdict")
        except R.ReaderError:
            check(True, "apply refuses while a survivor has no verdict")

        st2 = Stub()
        c = R.run(st2, p, repo=repo, log=logs.append)
        check(st2.calls == ["RP_HALF"] and c["skipped_done"] == 3, "rerun reads only the task not done (%s)" % st2.calls)
        st3 = Stub()
        R.run(st3, p, repo=repo, log=logs.append)
        check(st3.calls == [], "a third run reads nothing")
        hf = Path(p["judge"], "RP_KEEP.json")
        h = json.loads(hf.read_text())
        h["checks"][0]["body"] += "# changed\n"
        hf.write_text(json.dumps(h))
        check(R.state(p, repo=repo)["RP_KEEP"][0] == "stale", "a changed check body makes the verdict stale")
        st4 = Stub()
        R.run(st4, p, repo=repo, log=logs.append)
        check(st4.calls == ["RP_KEEP"], "a stale task is read again")
        st5 = Stub()
        R.run(st5, p, repo=repo, force=True, limit=2, log=logs.append)
        check(len(st5.calls) == 2, "--force re-reads; --limit caps the reads")

        try:
            R.apply(p, repo=repo)
            check(False, "apply still refuses while RP_NOTAIL is not ready")
        except R.ReaderError:
            check(True, "apply still refuses while RP_NOTAIL is not ready")
        doc = R.apply(p, repo=repo, partial=True)
        out = T.reader_exclusions_path(p)
        check(out.is_file() and doc["pending"] == ["RP_NOTAIL"], "apply --partial writes the default file, lists pending")
        check(set(doc["drop"]) == {"RP_ALLUN", "RP_DROP"} and "no scored check left" in doc["drop"]["RP_ALLUN"],
              "drop: a DROP_TASK check, or every scored check unscored (%s)" % doc["drop"])
        check(doc["unscore"] == {"RP_HALF": ["src/selftest_b.py"]} and doc["keep"] == ["RP_KEEP"],
              "unscore: the bad check of a task that keeps another; KEEP task in neither")
        rx = T.read_reader_exclusions(out)
        check(rx["drop"].keys() == doc["drop"].keys() and rx["unscore"] == doc["unscore"],
              "arena_trial.read_reader_exclusions reads the apply output")
        vf = res / "RP_KEEP.json"
        v = json.loads(vf.read_text())
        v["task_verdict"] = "KEEP"
        v["checks"][0]["verdict"] = "DROP_TASK"
        vf.write_text(json.dumps(v))
        check("RP_KEEP" in R.apply(p, repo=repo, partial=True)["drop"], "apply recomputes from per-check verdicts")

        for tgt in (res, out):
            check(A._inside(tgt, Path(p["freeze"]).parent) and not any(
                A._inside(tgt, r) for r in (p["tasks"], p["events"])),
                "default output %s is judge-only (not under tasks/ or events/)" % tgt.relative_to(p["root"]))

    def boom(pr):
        raise R.ReaderError("no login")
    name = R.make_reader("auto", gpt=boom, claude=lambda pr: "{}")("x")[1]
    check(name.startswith("claude-opus") and "no login" in name, "auto: GPT failure falls back to claude -p (%s)" % name)
    check(R.make_reader("auto", gpt=lambda pr: "{}", claude=boom)("x")[1] == "gpt", "auto prefers GPT")
    for bad in ("no json", '{"x": 1}'):
        try:
            R._extract_json(bad)
            check(False, "reply %r refused" % bad)
        except R.ReaderError:
            check(True, "reply %r refused" % bad)
    print("\n%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
