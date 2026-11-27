#!/usr/bin/env python3
"""selftest_clone_pack.py - the promises of design/specs/2026-11-27-timer-clone-packing/boundary.md.

Real git in temporary repos, with the user's and the system's git config shut out, a fake clock for the age of the
temporary files, and lowered pack thresholds. Item: RIMMANDRAKE_UNHOOK_GIT_PACKING_FROM_TICK_TOOK_13_MIN.

    python3 src/RimMandrake/Utils/selftest_clone_pack.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ["GIT_CONFIG_NOSYSTEM"] = "1"
os.environ["GIT_CONFIG_GLOBAL"] = os.devnull
for k in [k for k in os.environ if k.startswith("GIT_CONFIG_") and k not in ("GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL")]:
    del os.environ[k]
import clone_pack as CP  # noqa: E402
import time_budget as TB  # noqa: E402

FAILS = []


def ok(cond, what):
    print("%s  %s" % ("PASS" if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


def git(repo, *a, check=True):
    r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, timeout=TB.CALL_S,
                       stdin=subprocess.DEVNULL)
    if check and r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr.strip()))
    return r.stdout.strip()


def make_repo(path, commits=3):
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "main")
    for k, v in (("user.name", "selftest"), ("user.email", "selftest@example.invalid"), ("commit.gpgsign", "false")):
        git(path, "config", k, v)
    for i in range(commits):
        (path / ("f%d.txt" % i)).write_text("line %d\n" % i)
        git(path, "add", "f%d.txt" % i)
        git(path, "commit", "-q", "-m", "c%d" % i)
    return path


def add_loose(repo, n, tag):
    """n loose blobs, written by git itself (hash-object -w)."""
    d = Path(tempfile.mkdtemp(prefix="cp_blobs_"))
    try:
        paths = []
        for i in range(n):
            p = d / ("b%d" % i)
            p.write_text("%s blob %d\n" % (tag, i))
            paths.append(str(p))
        subprocess.run(["git", "-C", str(repo), "hash-object", "-w", "--stdin-paths"], input="\n".join(paths) + "\n",
                       capture_output=True, text=True, check=True, timeout=TB.CALL_S)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def add_packs(repo, n):
    """n small packs: each one blob packed alone."""
    for i in range(n):
        sha = subprocess.run(["git", "-C", str(repo), "hash-object", "-w", "--stdin"], input="pack blob %d\n" % i,
                             capture_output=True, text=True, check=True, timeout=TB.CALL_S).stdout.strip()
        subprocess.run(["git", "-C", str(repo), "pack-objects", "-q", ".git/objects/pack/pack"], input=sha + "\n",
                       capture_output=True, text=True, check=True, timeout=TB.CALL_S)
    git(repo, "prune-packed")


def counts(repo):
    out = {}
    for ln in git(repo, "count-objects", "-v").splitlines():
        k, _, v = ln.partition(":")
        out[k.strip()] = int(v.strip()) if v.strip().isdigit() else v.strip()
    return out


def held_cfg(repo):
    """-> True when the clone's own config holds the hold, as git reads it (not the reading's own word)."""
    return (git(repo, "config", "--local", "gc.auto", check=False) == "0"
            and git(repo, "config", "--local", "maintenance.auto", check=False) == "false")


def t_hold_stops_auto_packing(tmp):
    before = make_repo(tmp / "before")
    held = make_repo(tmp / "held")
    for r in (before, held):
        add_packs(r, 51)            # past git's gc.autoPackLimit (50): gc --auto then repacks
    CP.hold(held)
    ok(git(held, "config", "--local", "gc.auto") == "0" and git(held, "config", "--local", "maintenance.auto") == "false",
       "hold_stops_auto_packing: the clone's own config has gc.auto=0 and maintenance.auto=false")
    for r in (before, held):
        git(r, "-c", "gc.autoDetach=false", "-c", "maintenance.autoDetach=false", "maintenance", "run", "--auto",
            "--quiet", check=False)
        git(r, "-c", "gc.autoDetach=false", "gc", "--auto", "--quiet", check=False)
    cb, ch = counts(before), counts(held)
    ok(cb["packs"] < 51, "hold_stops_auto_packing: fixture: with no hold, git's auto packing repacks the 51 packs "
       "(packs %d)" % cb["packs"])
    ok(ch["packs"] == 51,
       "hold_stops_auto_packing: after hold, maintenance --auto and gc --auto pack nothing (packs %d)" % ch["packs"])
    CP.hold(held)
    ok(git(held, "config", "--local", "--get-all", "gc.auto").splitlines() == ["0"],
       "hold_stops_auto_packing: a second hold writes no second line")


def t_timer_clones_from_unit_files(tmp):
    root = tmp / "rm"
    a = make_repo(root / "dispatch", 1)
    b = make_repo(root / "roles" / "artpiped", 1)
    c = make_repo(root / "pulse-deploy", 1)     # named only by an ExecStart= path inside it, as rm-deploy-update names it
    bare = root / "mirror.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True, timeout=TB.CALL_S)
    outside = make_repo(tmp / "elsewhere", 1)
    units = tmp / "units"
    units.mkdir()
    (units / "rm-one.service").write_text(
        "[Service]\nWorkingDirectory=%s\nExecStart=/usr/bin/python3 %s/src/x.py tick\n" % (a, a))
    (units / "rm-two.service").write_text(
        "[Service]\nWorkingDirectory=%s\nExecStartPre=/bin/bash -lc './sync'\n" % b)
    (units / "rm-three.service").write_text(
        "[Service]\nExecStart=/usr/bin/git -C %s fetch\nExecStart=-/usr/bin/python3 %s/gone/x.py\n"
        "ExecStart=/usr/bin/python3 %s/x.py\n" % (bare, root, outside))
    (units / "rm-three.timer").write_text("[Timer]\nOnUnitInactiveSec=1h\n")
    (units / "rm-four.service").write_text("[Service]\nExecStart=/usr/bin/python3 %s/src/tools/deploy.py --apply\n" % c)
    got = CP.timer_clones([units, tmp / "no-such-dir"], root=root)
    ok(got == sorted([a, b, c]), "timer_clones_from_unit_files: names each work tree once, no bare repo, no missing or "
       "outside path (got %s)" % [str(p) for p in got])
    ok(c in got, "timer_clones_from_unit_files: an ExecStart= path inside a work tree, with no WorkingDirectory=, "
       "names that work tree")


def t_dead_temp_files_go_live_ones_stay(tmp):
    r = make_repo(tmp / "temps")
    git(r, "repack", "-a", "-d", "-q")
    CP.hold(r)
    pack_dir = r / ".git/objects/pack"
    now = time.time()
    old_pack = pack_dir / "tmp_pack_OLD123"
    new_pack = pack_dir / "tmp_pack_NEW456"
    (r / ".git/objects/ab").mkdir(exist_ok=True)
    old_obj = r / ".git/objects/ab/tmp_obj_OLD789"
    for p in (old_pack, new_pack, old_obj):
        p.write_bytes(b"x" * 100)
    for p in (old_pack, old_obj):
        os.utime(p, (now - 7 * 3600, now - 7 * 3600))
    os.utime(new_pack, (now - 5 * 3600, now - 5 * 3600))      # under the 6 h line, so a shorter line is caught
    real = sorted(p.name for p in pack_dir.iterdir() if p.name.startswith("pack-"))
    reading = CP.run([r], apply=True, now=now, state=tmp / "state_temps")
    ok(not old_pack.exists() and not old_obj.exists(),
       "dead_temp_files_go_live_ones_stay: a tmp_pack_* and a tmp_obj_* older than 6 h are deleted")
    ok(new_pack.exists(), "dead_temp_files_go_live_ones_stay: a tmp_pack_* 5 h old stays")
    ok(sorted(p.name for p in pack_dir.iterdir() if p.name.startswith("pack-")) == real,
       "dead_temp_files_go_live_ones_stay: every real pack stays")
    row = reading["clones"][0]
    ok(sorted(Path(x).name for x in row["deleted"]) == ["tmp_obj_OLD789", "tmp_pack_OLD123"],
       "dead_temp_files_go_live_ones_stay: the reading names the deleted files (%s)" % row["deleted"])
    plan = make_repo(tmp / "temps_plan")
    stale = plan / ".git/objects/pack/tmp_pack_PLAN"
    stale.write_bytes(b"x")
    os.utime(stale, (now - 7 * 3600, now - 7 * 3600))
    CP.run([plan], apply=False, now=now, state=tmp / "state_plan")
    ok(stale.exists() and git(plan, "config", "--local", "gc.auto", check=False) == "",
       "dead_temp_files_go_live_ones_stay: without --apply nothing is deleted or written")


def t_pack_when_git_would_have(tmp):
    loose = make_repo(tmp / "loose")
    add_loose(loose, 300, "loose")
    many = make_repo(tmp / "many")
    add_packs(many, 6)
    tidy = make_repo(tmp / "tidy")
    add_loose(tidy, 20, "tidy")
    state = tmp / "state_pack"
    reading = CP.run([loose, many, tidy], apply=True, loose_at=200, packs_at=5, state=state)
    rows = {Path(r["clone"]).name: r for r in reading["clones"]}
    cl, cm, ct = counts(loose), counts(many), counts(tidy)
    ok(rows["loose"]["packed"] and cl["count"] < 200,
       "pack_when_git_would_have: a clone over the loose threshold is packed (loose %d)" % cl["count"])
    ok(rows["many"]["packed"] and cm["packs"] < 6,
       "pack_when_git_would_have: a clone over the pack threshold is packed (packs %d)" % cm["packs"])
    ok(not rows["tidy"]["packed"] and ct["count"] >= 20,
       "pack_when_git_would_have: a clone under both thresholds is left unpacked (loose %d)" % ct["count"])
    for r in (loose, many):
        fs = subprocess.run(["git", "-C", str(r), "fsck", "--connectivity-only", "--no-progress"], capture_output=True,
                            text=True, timeout=TB.CALL_S)
        ok(fs.returncode == 0 and git(r, "rev-list", "--count", "HEAD") == "3",
           "pack_when_git_would_have: %s still reads its whole history (fsck rc %d)" % (r.name, fs.returncode))
    on_disk = json.loads((state / "reading.json").read_text())
    ok(on_disk["clones"] == reading["clones"] and all(r["held"] for r in on_disk["clones"]),
       "pack_when_git_would_have: reading.json holds each clone, each held")
    ok(all(held_cfg(r) for r in (loose, many, tidy)),
       "pack_when_git_would_have: run --apply writes the hold into each clone's own config")


def t_one_failure_does_not_stop_the_rest(tmp):
    broken = tmp / "broken"
    broken.mkdir()
    (broken / ".git").write_text("gitdir: /nonexistent/elsewhere\n")
    good = make_repo(tmp / "good")
    add_loose(good, 300, "good")
    reading = CP.run([broken, good], apply=True, loose_at=200, packs_at=5, state=tmp / "state_fail")
    rows = {Path(r["clone"]).name: r for r in reading["clones"]}
    ok(rows["broken"].get("failed"), "one_failure_does_not_stop_the_rest: the broken clone is reported failed (%s)"
       % rows["broken"].get("failed"))
    ok(rows["good"]["packed"] and rows["good"]["held"] and held_cfg(good) and not rows["good"].get("failed"),
       "one_failure_does_not_stop_the_rest: the good clone is still held and packed")
    ok(CP.exit_code(reading) == 1, "one_failure_does_not_stop_the_rest: the command exits 1")
    ok(CP.exit_code(CP.run([], apply=False, state=tmp / "state_empty")) == 3,
       "one_failure_does_not_stop_the_rest: no clone named is its own answer (exit 3), never a pass")


def main():
    tmp = Path(tempfile.mkdtemp(prefix="selftest_clone_pack_"))
    try:
        for t in (t_hold_stops_auto_packing, t_timer_clones_from_unit_files, t_dead_temp_files_go_live_ones_stay,
                  t_pack_when_git_would_have, t_one_failure_does_not_stop_the_rest):
            try:
                t(tmp)
            except Exception as e:     # a test that raises is a failure of that test, the others still run
                ok(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failed" % ("FAIL" if FAILS else "OK", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
