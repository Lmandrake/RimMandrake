#!/usr/bin/env python3
"""Folder-time shortcuts keep scratch safe and dry runs account for child time."""

import contextlib
import io
import json
import os
import subprocess
import tempfile
import time
import traceback
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import scratch_reap as reap


@contextlib.contextmanager
def sandbox():
    with tempfile.TemporaryDirectory(prefix="selftest_scratch_reap_folder_time_") as base:
        root = Path(base)
        tmp = root / "tmp"
        tmp.mkdir()
        (root / "transcripts").mkdir()
        env = {
            "SCRATCH_REAP_ROOTS": str(tmp),
            "SCRATCH_REAP_TMP": str(tmp),
            "SCRATCH_REAP_SCAN": str(tmp),
            "SCRATCH_REAP_STATE": str(root / "state"),
            "SCRATCH_REAP_CORPUS": "",
            "SCRATCH_REAP_MIRRORS": "",
            "SCRATCH_REAP_PROTECTED": "",
            "SCRATCH_REAP_TRANSCRIPTS": str(root / "transcripts"),
            "SCRATCH_REAP_SAVE_REPO": str(root),
            "GIT_CEILING_DIRECTORIES": str(root.parent),
            "SCRATCH_REAP_TMP_IDLE_HOURS": "1",
            "SCRATCH_REAP_TMP_PRESSURE_IDLE_HOURS": "1",
            "LEFTOVERS_ARCHIVE_ROOT": str(root / "archive"),
            "RM_RUN_TMP_ROOT": str(root / "runs"),
        }
        with patch.dict(os.environ, env), patch.object(reap, "proc_entries", return_value=[]):
            yield root, tmp


def tree(tmp, name, files=1):
    top = tmp / name
    deep = top / "one" / "two"
    deep.mkdir(parents=True)
    for i in range(files):
        (deep / f"file-{i}").write_text("original")
    return top, deep / "file-0"


def t_an_old_folder_is_judged_without_walking_each_file():
    with sandbox() as (_, tmp):
        busy, _ = tree(tmp, "busy", files=100)
        recent, _ = tree(tmp, "recent", files=100)
        idle, _ = tree(tmp, "idle")
        repo, _ = tree(tmp, "repo", files=100)
        (repo / ".git").mkdir()
        fixture, _ = tree(tmp, "selftest_recent", files=100)
        ctx = reap.Ctx(time.time() + reap.FIXTURE_TTL_S + 7200)
        assert ctx.now - max(reap.touched(busy.stat())) >= 3600
        os.utime(recent, (ctx.now, ctx.now))
        os.utime(fixture, (ctx.now, ctx.now))
        ctx.live = SimpleNamespace(blind=[], users=lambda p: ["process in use"] if p == busy else [])
        with patch.object(reap.os, "scandir", wraps=os.scandir) as scan:
            counts, rows = reap.sweep_tmp(ctx, apply=False, deadline=0)
            fixtures = reap.sweep_fixtures(ctx, apply=False, deadline=0)
        visited = [Path(call.args[0]) for call in scan.call_args_list]
        assert counts["held"] == 1 and counts["young"] == 1 and counts["work"] == 1, counts
        assert fixtures["young"] == 1 and fixtures["removed"] == 0, fixtures
        assert [row["path"] for row in rows] == [str(idle)], rows
        for top in (busy, recent, repo, fixture):
            assert not any(p == top or top in p.parents for p in visited), f"walked retained folder {top}"


def t_a_young_file_deep_in_an_old_folder_is_never_reaped():
    with sandbox() as (_, tmp):
        top, payload = tree(tmp, "old")
        idle, _ = tree(tmp, "idle")
        ctx = reap.Ctx(time.time() + 7200)
        parents = [top, payload.parent.parent, payload.parent]
        before = [reap.touched(p.stat()) for p in parents]
        with patch.object(reap.time, "time", return_value=ctx.now):
            _, planned = reap.sweep_tmp(ctx, apply=False, deadline=0)
            assert {row["path"] for row in planned} == {str(top), str(idle)}, planned

            # Overwrite an existing file. None of its ancestors receives a new timestamp.
            payload.write_text("new work")
            os.utime(payload, (ctx.now, ctx.now))
            assert [reap.touched(p.stat()) for p in parents] == before
            assert all(ctx.now - max(stamps) >= 3600 for stamps in before)
            _, planned = reap.sweep_tmp(ctx, apply=False, deadline=0)
            assert [row["path"] for row in planned] == [str(idle)], planned
            counts, removed = reap.sweep_tmp(ctx, apply=True, deadline=0)
        assert counts["young"] == 1 and counts["removed"] == 1, counts
        assert [row["path"] for row in removed] == [str(idle)], removed
        assert payload.read_text() == "new work" and not idle.exists()


def t_the_dry_run_names_its_child_commands_with_their_seconds():
    with sandbox() as (root, tmp), patch.object(reap, "_COMMITTED_SAVES", None):
        # A loose save forces the tracked-save git lookup. Ctx also runs the real borrower find.
        (tmp / "work.rws").write_text("save")
        subprocess.run(["git", "init", "-q", str(tmp / "repo")], check=True)
        later = time.time() + reap.ttl_s() + 60
        with patch.object(reap.time, "time", return_value=later), contextlib.redirect_stdout(io.StringIO()) as output:
            assert reap.main(["--json"]) == 0
        assert [row["path"] for row in json.loads(output.getvalue())] == [str(tmp / "repo")]
        record = json.loads((root / "state" / "last_dry_run.json").read_text())
        children = record.get("child_commands", {})
        for name in ("find", "git ls-tree"):
            assert name in children, record
            assert children[name]["calls"] == 1 and children[name]["seconds"] > 0, children
        assert children["git rev-parse"]["calls"] == 3 and children["git rev-parse"]["seconds"] > 0, children


if __name__ == "__main__":
    tests = (
        t_an_old_folder_is_judged_without_walking_each_file,
        t_a_young_file_deep_in_an_old_folder_is_never_reaped,
        t_the_dry_run_names_its_child_commands_with_their_seconds,
    )
    failures = 0
    for test in tests:
        try:
            test()
        except Exception:
            traceback.print_exc()
            failures += 1
            print(f"FAIL {test.__name__}")
        else:
            print(f"PASS {test.__name__}")
    print(f"{failures} FAIL" if failures else "ALL PASS")
    raise SystemExit(bool(failures))
