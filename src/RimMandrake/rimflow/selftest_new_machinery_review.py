#!/usr/bin/env python3
"""Offline promises of the new-machinery review boundary."""
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[3]
FLOW = "src/RimMandrake/rimflow/"
CONFIG = "src/RimMandrake/Utils/pipeline_tests.json"
SCRIPT = FLOW + "new_tool.py"
OTHER = FLOW + "new_helper.sh"
CLEAN = FLOW + "new_clean.py"
FLAGGED = FLOW + "new_flagged.py"
WRITER = "rm-detached-bench-writer-1795700000"
REVIEWER = "rm-detached-bench-reviewer-1795700001"


@contextmanager
def history():
    """A local origin/main with one new-script run, then an edit-only run and an unpublished addition."""
    with TemporaryDirectory(dir=REPO) as tmp:
        def git(*args, **kw):
            return subprocess.run(["git", *args], cwd=tmp, check=True, capture_output=True, text=True, **kw).stdout

        def changes(ref, paths, deleted=(), parent=None, content="x"):
            commands = [f"commit {ref}", "committer Fixture <fixture@example.invalid> 1 +0000", "data 0"]
            if parent:
                commands.append(f"from {parent}")
            commands += [f"M 100644 inline {p}\ndata 2\n{content}\n" for p in paths]
            commands += [f"D {p}" for p in deleted]
            git("fast-import", "--quiet", input="\n".join(commands) + "\n\n")
            return git("rev-parse", ref).strip()

        git("init", "-q")
        main = "refs/remotes/origin/main"
        edit = FLOW + "old.py"
        deleted = FLOW + "new_deleted.py"
        base = changes(main, [edit])
        first = changes(main, [SCRIPT, CLEAN, FLAGGED, deleted, "src/unmatched.py"], parent=base)
        second = changes(main, [OTHER], [deleted], parent=first)
        edited = changes(main, [edit], parent=second, content="y")
        unpublished = changes("refs/heads/unpublished", [FLOW + "new_unpublished.py"])
        cfg = Path(tmp, CONFIG)
        cfg.parent.mkdir(parents=True)
        cfg.write_text(json.dumps({"pipeline_files": [FLOW + "*.py", FLOW + "new_*.sh"]}), encoding="utf-8")
        yield tmp, first, second, edited, unpublished


def run_file(commits, root):
    import fresh_reader as FR
    import new_machinery_review as NR

    filed, ids = [], set()

    def submit(argv, root):
        filed.append(argv)
        ids.add(argv[3])
        return 0

    def review_status(argv):
        p = argv[-1]
        return subprocess.CompletedProcess(argv, int(p != CLEAN), f"{'DIRTY' if p != CLEAN else 'READ-CLEAN'} {p}")

    holds = FR.holds
    with (patch.object(NR, "submit", submit), patch.object(NR, "review_tickets", return_value=ids),
          patch.object(NR, "landed_refusal", return_value=None)):
        with patch.object(FR, "holds", side_effect=lambda sha, paths: holds(
                sha, paths, runner=review_status, flagged=lambda p: "older" if p == FLAGGED else None)):
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                args = ["file", *commits]
                result = NR.main(args, root=root, env={"RM_ROLE_UNIT": WRITER})
                repeated = NR.main(args, root=root, env={"RM_ROLE_UNIT": WRITER})
    return result, repeated, filed


def ticket(commits, root):
    rc, retry, filed = run_file(commits, root)
    assert (rc, retry, len(filed)) == (0, 0, 1), (rc, retry, filed)
    argv = filed[0]
    fields = dict(zip(argv[4::2], argv[5::2]))
    return argv[3], {"state": "proposed", "effect": fields["--effect"], "verdict": "fails",
                     "title": fields["--title"], "out": "DIRTY", "depth": 0, "waits_on": []}


def t_a_run_that_adds_a_pipeline_script_files_one_review_ticket():
    import brief_new as BN
    import detached_helper as DH
    import fixer_rule as rules
    import model
    import new_machinery_review as NR

    with history() as (root, first, second, _, _):
        iid, it = ticket([first, second], root)
    assert not model.mint_problems(iid, set()), iid
    assert NR.parse_title(it["title"]) == ([OTHER, SCRIPT], WRITER), it
    assert rules.NEW_MACHINERY_RULE in DH.FOOTER
    for kind in BN.KINDS:
        assert rules.NEW_MACHINERY_RULE in BN.skeleton(kind, iid), kind
    for path in ("CLAUDE.md", "design/RimMandrake/standing_rulings.md"):
        assert rules.NEW_MACHINERY_RULE in " ".join((REPO / path).read_text(encoding="utf-8").split()), path


def t_a_run_that_only_edits_files_none():
    with history() as (root, _, _, edited, unpublished):
        assert run_file([edited], root) == (0, 0, [])
        assert run_file([unpublished], root) == (2, 2, [])


def t_the_lane_offers_the_review_ticket():
    import item_packet
    import list_dispatch as LD
    import new_machinery_review as NR

    with history() as (root, first, second, _, _):
        iid, it = ticket([first, second], root)
    cfg = {"enabled": True, "max_live": 2, "opus_cap_usd": 12, "seat": "BENCH",
           "bundle_hold_h": 24, "sonnet_if_check_regex": "new_machinery_review"}
    facts = {"items": {iid: it}, "runs": {}, "systems": {iid: "pipeline:fixture"}}
    state, now, started = {}, 1_800_000_000.0, []
    rows, launches = LD.decide(cfg, state, facts, now)
    assert launches == [iid] and rows[0]["decision"] == "launch", rows
    assert not rows[0].get("bundle"), rows

    def launch(item, model, cap, brief, seat, mod, **kw):
        started.append((item, model, brief, kw.get("env")))
        return 0, "", REVIEWER

    page = "design/specs/example/boundary.md"
    tests = FLOW + "selftest_new_tool.py"
    assert NR.boundaries([NR.TOOL])[NR.TOOL] == [
        ("design/specs/2026-11-28-new-machinery-review/boundary.md", FLOW + "selftest_new_machinery_review.py")]
    with patch.object(NR, "boundaries", side_effect=lambda paths: {p: [(page, tests)] for p in paths}):
        LD.execute(cfg, state, rows, launches, facts, now, {"launch": launch})
    assert len(started) == 1 and rows[0]["unit"] == REVIEWER, rows
    item, model, brief, env = started[0]
    assert item == iid and model == "opus", started
    assert all(word in brief for word in (FLOW + "roles/code_review.md", WRITER, SCRIPT, OTHER, page, tests)), brief
    assert f"new_machinery_review.py independent {WRITER}" in brief, brief
    assert "Do not read the diff" in brief and "ITEM PACKET" not in brief, brief
    assert item_packet.role_of(brief, env), "the actual launch would receive item history"


def t_the_ticket_check_holds_on_a_review_record():
    import fresh_reader as FR
    import new_machinery_review as NR

    with history() as (root, first, second, _, _):
        _, it = ticket([first, second], root)
    words = shlex.split(it["effect"].removeprefix("cmd:"))
    assert words == ["python3", FLOW + "new_machinery_review.py", "holds", OTHER, SCRIPT], words
    holds = FR.holds
    records = {OTHER: "READ-CLEAN", SCRIPT: "DIRTY"}
    flagged = set()

    def review_status(argv):
        p = argv[-1]
        value = records[p]
        return subprocess.CompletedProcess(argv, int(value != "READ-CLEAN"), f"{value} {p}" if value else "")

    with patch.object(FR, "holds", side_effect=lambda sha, paths: holds(
            sha, paths, runner=review_status, flagged=lambda p: "older" if p in flagged else None)):
        with redirect_stdout(StringIO()):
            assert NR.main(words[2:]) == 1
            records[SCRIPT] = ""
            assert NR.main(words[2:]) == 2
            records[SCRIPT] = "DIRTY"
            flagged.add(SCRIPT)
            assert NR.main(words[2:]) == 0
            flagged.clear()
            records[SCRIPT] = "READ-CLEAN"
            assert NR.main(words[2:]) == 0


def t_the_writing_run_is_never_the_reviewer():
    import new_machinery_review as NR

    with history() as (root, first, second, _, _):
        _, it = ticket([first, second], root)
    _, maker = NR.parse_title(it["title"])
    with redirect_stdout(StringIO()):
        assert NR.main(["independent", maker], env={"RM_ROLE_UNIT": WRITER}) == 2
        assert NR.main(["independent", maker], env={"RM_DETACHED_UNIT": WRITER}) == 2
        assert NR.main(["independent", maker], env={}) == 2
        assert NR.main(["independent", maker], env={"RM_ROLE_UNIT": REVIEWER}) == 0


def main():
    tests = [t_a_run_that_adds_a_pipeline_script_files_one_review_ticket, t_a_run_that_only_edits_files_none,
             t_the_lane_offers_the_review_ticket, t_the_ticket_check_holds_on_a_review_record,
             t_the_writing_run_is_never_the_reviewer]
    failed = 0
    with TemporaryDirectory() as state, patch.dict(os.environ, {
        "RM_UNDER_SELFTEST": "1", "RM_LIST_DISPATCH_DIR": state, "RM_WORK_BUNDLE_DIR": state,
    }):
        for test in tests:
            try:
                test()
                print("PASS", test.__name__)
            except Exception as e:
                failed += 1
                print("FAIL", test.__name__, f"{type(e).__name__}: {e}")
    print(f"FAILED {failed} of {len(tests)}" if failed else f"ALL PASS ({len(tests)})")
    return int(bool(failed))


if __name__ == "__main__":
    sys.exit(main())
