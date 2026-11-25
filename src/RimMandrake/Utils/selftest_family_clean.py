#!/usr/bin/env python3
"""selftest_family_clean.py — family_clean.py's rules on planted fixtures (never the real places).

  transient_old_unpinned_removed   a 15-day-old file in a temp Transient/ is listed REMOVE, and --apply removes it
  transient_pinned_kept            a 15-day-old pinned file, a decisions file and a file a live item cites are KEEP
  transient_young_kept             a 1-day-old file is YOUNG
  saves_canonical_never_listed     no row names a canonical save or a backup of one; an old debug save is REMOVE
  d_uncited_old_removed            an old uncited backup is REMOVE, and --apply removes only it
  d_unlanded_clone_refused         an old backup holding a clone with a commit on no remote is REFUSE
  d_canonical_only_copy_refused    an old backup holding a guarded save the live Saves folder lacks is REFUSE
  d_protected_and_young_kept       scratch/save_keepers is KEEP; a new backup is YOUNG
  every_family_has_a_reader        a whole dry run gives each family rows, and each row names the reader checked
  check_reads_the_last_apply       `check` fails with no --apply run, holds after one, and fails when it is stale
  shots_old_uncited_removed        an 8-day-old screenshot that no result names is REMOVE, and --apply removes it
  shots_result_named_kept          a 20-day-old screenshot that a live result names (escaped Windows path) is KEEP
  shots_young_kept                 a 2-hour-old screenshot is YOUNG, whatever the budget
  shots_budget_newest_kept         past the young line, the newest shots within the budget stay; the older go
  shots_blind_results_unmeasured   a results folder that cannot be read makes the would-remove rows UNMEASURED
  check_reads_host_families        on a host whose family set is `screenshots`, check holds after one --apply run
Items: RIMMANDRAKE_EXTEND_CLEANER_TO_FAMILIES_NO_CLEANER_COVERS_265_GB_ON_D,
RIMMANDRAKE_PRUNE_STEVE_LANE_SCREENSHOTS_HALF_GIG_A_DAY_ONTO_FULL_C (screenshots).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "family_clean.py"
sys.path.insert(0, str(HERE))
import transient_pin  # noqa: E402

DAY = 86400
# Fixture names are made per run: a name written in this file is cited by this file, and a cited unit is (rightly) kept.
TAG = "zzfc" + uuid.uuid4().hex[:10]


def age(p: Path, days: float):
    t = time.time() - days * DAY
    os.utime(p, (t, t))


def put(p: Path, days: float, data: bytes = b"x") -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    age(p, days)
    return p


def run(env: dict, *args) -> tuple[int, dict | None, str]:
    r = subprocess.run([sys.executable, str(TOOL), "--json", *args], capture_output=True, text=True,
                       env=dict(os.environ, **env))
    try:
        return r.returncode, json.loads(r.stdout), r.stderr
    except ValueError:
        return r.returncode, None, r.stdout[-800:] + r.stderr[-800:]


def git(repo: Path, *a):
    subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True,
                   env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                            GIT_COMMITTER_EMAIL="t@t"))


def verdicts(data: dict, family: str) -> dict[str, str]:
    return {r["path"]: r["verdict"] for r in data["rows"] if r["family"] == family}


def fixture_cases() -> list[str]:
    """The first ten promises, on one planted clone, data root, Saves folder and projects dir."""
    fails: list[str] = []
    with tempfile.TemporaryDirectory(prefix="selftest_family_clean_") as td:
        td = Path(td)
        # ---- a temp clone with a Transient/ that uses the real pin header
        repo = td / "repo"
        repo.mkdir()
        git(repo, "init", "-q", "-b", "main")
        (repo / "Transient").mkdir()
        (repo / "Transient" / ".gitignore").write_text(transient_pin.HEADER + "%s\n!/pinned_old.txt\n%s\n" % (
            transient_pin.BEGIN, transient_pin.END))
        T = repo / "Transient"
        old_unpinned = put(T / "run_20261101" / "old_unpinned.png", 15)
        pinned = put(T / "pinned_old.txt", 15)
        decisions = put(T / "sheet" / "x.decisions.json", 40)
        cited = put(T / "cited_dir" / "evidence.md", 30)
        young = put(T / "young.txt", 1)
        items = repo / "infrastructure" / "state" / "items"
        items.mkdir(parents=True)
        (items / "SELFTEST_LIVE_ITEM.md").write_text("evidence: Transient/cited_dir/evidence.md\n")
        git(repo, "add", "Transient/.gitignore", "Transient/pinned_old.txt", "infrastructure")
        git(repo, "commit", "-q", "-m", "fixture")
        age(pinned, 15)
        # ---- a temp data root, Saves folder and projects dir
        data = td / "data"
        saves = td / "Saves"
        saves.mkdir()
        canon = ["CANONICAL_ASHKARR_START_2026-09-12.rws", "CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-x-20260927",
                 "ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws",
                 "ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws.bak-pre-selftest"]
        for n in canon:
            put(saves / n, 60)
        debug = put(saves / (TAG + "_debug.rws"), 10)
        b = data / "backups"
        old_backup = put(b / (TAG + "_old_backup") / "f.txt", 20)
        age(old_backup.parent, 20)
        clone = b / (TAG + "_clone_backup") / "c"
        clone.mkdir(parents=True)
        git(clone, "init", "-q", "-b", "main")
        (clone / "a.txt").write_text("unique work")
        git(clone, "add", "a.txt")
        git(clone, "commit", "-q", "-m", "unique")
        for dp, dns, fns in os.walk(clone.parent.parent):
            for n in dns + fns:
                age(Path(dp) / n, 20)
        age(clone.parent.parent, 20)
        only = put(b / (TAG + "_canon_backup") / ("CANONICAL_" + TAG + ".rws"), 20)
        age(only.parent, 20)
        young_backup = put(b / (TAG + "_young_backup") / "f.txt", 2)
        keeper = put(data / "scratch" / "save_keepers" / "k.rws", 50)
        age(keeper.parent, 50)
        (data / "dispatcher" / "detached").mkdir(parents=True)
        claude = td / "projects"
        put(claude / "-p" / "s.jsonl", 3)
        env = {"FAMILY_CLEAN_REPOS": str(repo), "FAMILY_CLEAN_DATA": str(data), "FAMILY_CLEAN_SAVES": str(saves),
               "FAMILY_CLEAN_CLAUDE": str(claude), "FAMILY_CLEAN_STATE": str(td / "state")}

        # ---- one whole dry run
        rc, d, err = run(env)
        if d is None:
            return ["fixture: dry run gave no JSON (rc %s): %s" % (rc, err)]
        tv = verdicts(d, "transient")
        if tv.get(str(old_unpinned)) != "REMOVE":
            fails.append("transient_old_unpinned_removed: %s is %s" % (old_unpinned.name, tv.get(str(old_unpinned))))
        for p in (pinned, decisions, cited):
            if tv.get(str(p)) != "KEEP":
                fails.append("transient_pinned_kept: %s is %s" % (p.relative_to(T), tv.get(str(p))))
        if tv.get(str(young)) != "YOUNG":
            fails.append("transient_young_kept: young.txt is %s" % tv.get(str(young)))
        sv = verdicts(d, "saves")
        listed = [p for p in sv if any(c.split(".rws")[0] in p for c in canon)]
        if listed:
            fails.append("saves_canonical_never_listed: listed %s" % listed)
        if sv.get(str(debug)) != "REMOVE":
            fails.append("saves_canonical_never_listed: the old debug save is %s" % sv.get(str(debug)))
        bv = verdicts(d, "backups")
        want = {old_backup.parent: "REMOVE", clone.parent: "REFUSE", only.parent: "REFUSE",
                young_backup.parent: "YOUNG"}
        names = {old_backup.parent: "d_uncited_old_removed", clone.parent: "d_unlanded_clone_refused",
                 only.parent: "d_canonical_only_copy_refused", young_backup.parent: "d_protected_and_young_kept"}
        for p, v in want.items():
            if bv.get(str(p)) != v:
                fails.append("%s: %s is %s, want %s" % (names[p], p.name, bv.get(str(p)), v))
        kr = next((r for r in d["rows"] if r["path"] == str(keeper.parent)), {})
        if kr.get("verdict") != "KEEP" or "save_guard" not in (kr.get("reader") or ""):   # by the family rule, not by luck
            fails.append("d_protected_and_young_kept: save_keepers is %s (%s)" % (kr.get("verdict"), kr.get("reader")))
        fams = {r["family"] for r in d["rows"]}
        need = {"transient", "saves", "backups", "scratch", "detached", "claude_projects"}
        if need - fams:
            fails.append("every_family_has_a_reader: no rows for %s" % sorted(need - fams))
        blank = [r["path"] for r in d["rows"] if not r.get("reader")]
        if blank:
            fails.append("every_family_has_a_reader: rows with no reader: %s" % blank[:3])

        chk = lambda: subprocess.run([sys.executable, str(TOOL), "check"], capture_output=True, text=True,  # noqa: E731
                                     env=dict(os.environ, FAMILY_CLEAN_SKIP_TIMER="1", **env))
        if chk().returncode != 1:
            fails.append("check_reads_the_last_apply: check held after a dry run only")
        # ---- --apply removes exactly the REMOVE rows
        rc, d2, err = run(env, "--apply")
        if d2 is None:
            fails.append("apply gave no JSON (rc %s): %s" % (rc, err))
        else:
            gone = [p for p in (old_unpinned, debug, old_backup.parent) if p.exists()]
            if gone:
                fails.append("d_uncited_old_removed/transient_old_unpinned_removed: --apply left %s" % gone)
            kept = [p for p in [pinned, decisions, cited, young, clone, only, young_backup, keeper] +
                    [saves / n for n in canon] if not p.exists()]
            if kept:
                fails.append("--apply removed a kept unit: %s" % kept)
            lr = td / "state" / "last_run.json"
            if not lr.is_file():
                fails.append("--apply wrote no last_run.json")
            elif chk().returncode != 0:
                fails.append("check_reads_the_last_apply: check failed after an --apply run: %s" % chk().stdout)
            else:
                j = json.loads(lr.read_text())
                j["at_epoch"] -= 31 * 3600
                lr.write_text(json.dumps(j))
                if chk().returncode != 1:
                    fails.append("check_reads_the_last_apply: check held on a 31 h old run")
    return fails


def shots_cases() -> list[str]:
    """The screenshots family (SteveDesktop's test lane), on a planted Screenshots folder and results folder."""
    fails: list[str] = []
    H = 3600
    with tempfile.TemporaryDirectory(prefix="selftest_family_clean_shots_") as td:
        td = Path(td)
        shots, res = td / "Screenshots", td / "outbox" / "acked"
        res.mkdir(parents=True)
        old = put(shots / ("%s_old_1795000000000_1.png" % TAG), 8)
        named = put(shots / ("%s_named_1794000000000_2__cell_rect.png" % TAG), 20)
        young = put(shots / ("%s_young_1795600000000_3.png" % TAG), 2 * H / DAY, b"y" * 400)
        in_budget = put(shots / ("%s_inbudget_1795500000000_4.png" % TAG), 2, b"b" * 400)
        over = put(shots / ("%s_over_1795400000000_5.png" % TAG), 3, b"o" * 400)
        # a result names its shot as worker.py writes it: a Windows path inside JSON, so its backslashes are escaped
        (res / "J1.a1.json").write_text(json.dumps({"rows": [{"png": "C:\\Users\\x\\Screenshots\\" + named.name}]}))
        env = {"FAMILY_CLEAN_FAMILIES": "screenshots", "FAMILY_CLEAN_SCREENSHOTS": str(shots),
               "FAMILY_CLEAN_RESULTS": str(td / "outbox"), "FAMILY_CLEAN_SHOT_BUDGET": "1000",
               "FAMILY_CLEAN_STATE": str(td / "state")}
        # every old root on an empty fixture too: a tool that ignores FAMILY_CLEAN_FAMILIES (the red run) must still
        # see no real place, or its --apply runs on them
        for k in ("FAMILY_CLEAN_DATA", "FAMILY_CLEAN_REPOS", "FAMILY_CLEAN_SAVES", "FAMILY_CLEAN_CLAUDE"):
            (td / "empty" / k).mkdir(parents=True)
            env[k] = str(td / "empty" / k)
        rc, d, err = run(env)
        if d is None:
            return ["shots: dry run gave no JSON (rc %s): %s" % (rc, err)]
        v = verdicts(d, "screenshots")
        want = [("shots_old_uncited_removed", old, "REMOVE"), ("shots_result_named_kept", named, "KEEP"),
                ("shots_young_kept", young, "YOUNG"), ("shots_budget_newest_kept", in_budget, "YOUNG"),
                ("shots_budget_newest_kept", over, "REMOVE")]
        for name, p, w in want:
            if v.get(str(p)) != w:
                fails.append("%s: %s is %s, want %s" % (name, p.name, v.get(str(p)), w))
        blank = [r["path"] for r in d["rows"] if not r.get("reader")]
        if blank:
            fails.append("shots: rows with no reader: %s" % blank[:3])
        # a results folder that cannot be read: nothing is "no reader"
        rc, db, err = run(dict(env, FAMILY_CLEAN_RESULTS=str(td / "no_such_outbox")))
        vb = verdicts(db, "screenshots") if db else {}
        if not db or vb.get(str(old)) != "UNMEASURED" or vb.get(str(over)) != "UNMEASURED":
            fails.append("shots_blind_results_unmeasured: old is %s, over is %s" % (vb.get(str(old)), vb.get(str(over))))
        chk = lambda: subprocess.run([sys.executable, str(TOOL), "check"], capture_output=True, text=True,  # noqa: E731
                                     env=dict(os.environ, FAMILY_CLEAN_SKIP_TIMER="1", **env))
        rc, d2, err = run(env, "--apply")
        if d2 is None:
            return fails + ["shots: --apply gave no JSON (rc %s): %s" % (rc, err)]
        if old.exists() or over.exists():
            fails.append("shots_old_uncited_removed: --apply left %s" % [p.name for p in (old, over) if p.exists()])
        lost = [p.name for p in (named, young, in_budget) if not p.exists()]
        if lost:
            fails.append("shots: --apply removed a kept shot: %s" % lost)
        c = chk()
        if c.returncode != 0:
            fails.append("check_reads_host_families: check failed after a screenshots --apply run: %s" % c.stdout.strip())
    return fails


# The promises of design/specs/2026-11-25-family-clean/boundary.md, each bound to the case run that checks it.
t_transient_old_unpinned_removed = t_transient_pinned_kept = t_transient_young_kept = fixture_cases
t_saves_canonical_never_listed = t_d_uncited_old_removed = t_d_unlanded_clone_refused = fixture_cases
t_d_canonical_only_copy_refused = t_d_protected_and_young_kept = t_every_family_has_a_reader = fixture_cases
t_check_reads_the_last_apply = fixture_cases
t_shots_old_uncited_removed = t_shots_result_named_kept = t_shots_young_kept = shots_cases
t_shots_budget_newest_kept = t_shots_blind_results_unmeasured = t_check_reads_host_families = shots_cases


def main() -> int:
    fails = fixture_cases() + shots_cases()
    for f in fails:
        print("FAIL:", f)
    print("selftest_family_clean: %s" % ("FAIL (%d)" % len(fails) if fails else "OK (16/16)"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
