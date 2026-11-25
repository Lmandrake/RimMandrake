#!/usr/bin/env python3
"""selftest for ops_clocks.py (OPS_CLOCKS_DEPLOY_ONE_PINNED_COPY): the unit parser and judge on fixtures, the shipped
unit files and installer templates against the one deploy, and the installers' --deploy default. Touches no live unit.

    python3 src/RimMandrake/Utils/selftest_ops_clocks_check.py
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.pop("RM_OPS_DEPLOY", None)
import ops_clocks as OC  # noqa: E402

FAILS = []
DEP = "/home/mandrake/rm/dispatch"


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


conf = OC.load_conf()
check(OC.deploy(conf) == DEP, "the deploy is the dispatch clone")
check(set(conf["clocks"]).isdisjoint(conf["outside"]), "no unit is both a clock and outside")

# --- judge on fixtures
ok_unit = "[Service]\nWorkingDirectory=%s\nExecStart=/usr/bin/python3 %s/src/RimMandrake/Utils/x.py run\n" % (DEP, DEP)
check(OC.judge(ok_unit, DEP) == [], "a unit on the deploy is clean")
check(OC.judge(ok_unit, DEP + "/") == [], "a trailing slash on the deploy does not matter")
bench = "[Service]\nExecStart=/usr/bin/python3 /home/mandrake/rm/bench/src/RimMandrake/Utils/memwatch.py --no-host\n"
check(OC.judge(bench, DEP) == ["runs code from /home/mandrake/rm/bench"], "a seat clone's script is caught")
post = ("[Service]\nExecStart=/usr/bin/python3 %s/src/RimMandrake/Utils/ops_watch.py run\n"
        "ExecStartPost=-/usr/bin/python3 /mnt/d/ClaudeWork/rimmandrake/pulse-deploy/src/RimMandrake/Utils/ops_memory.py\n"
        % DEP)
check(OC.judge(post, DEP) == ["runs code from /mnt/d/ClaudeWork/rimmandrake/pulse-deploy"],
      "an ExecStartPost from another checkout is caught")
wd = "[Service]\nWorkingDirectory=/home/mandrake/rm/bench\nExecStart=/usr/bin/python3 src/RimMandrake/Utils/x.py\n"
check(OC.judge(wd, DEP) == ["WorkingDirectory /home/mandrake/rm/bench is not the deploy"],
      "a relative script run in a seat clone is caught by its WorkingDirectory")
rel = "[Service]\nExecStart=/usr/bin/python3 src/RimMandrake/Utils/x.py\n"
check(OC.judge(rel, DEP) == ["relative script path with no WorkingDirectory"], "a relative script with no cwd is caught")
sh = ("[Service]\nWorkingDirectory=%s\nExecStart=/bin/sh -c 'cd /home/mandrake/rm/foundry/src/RimMandrake/Utils && "
      "python3 /home/mandrake/rm/foundry/src/RimMandrake/x.py'\n" % DEP)
check(OC.judge(sh, DEP) == ["runs code from /home/mandrake/rm/foundry"], "a path inside a shell line is caught once")
check(OC.judge("[Service]\nType=oneshot\n", DEP) == ["no ExecStart"], "a unit with nothing to run is a problem")

# --- drop-ins: an empty assignment resets, as systemd does (rm-artpiped's drop-in moved it foundry -> bench this way)
dropin = ("# /x/rm-foo.service\n[Service]\nWorkingDirectory=/home/mandrake/rm/foundry\n"
          "ExecStart=/usr/bin/python3 /home/mandrake/rm/foundry/src/RimMandrake/a.py\n"
          "# /x/rm-foo.service.d/override.conf\n[Service]\nWorkingDirectory=%s\nExecStart=\n"
          "ExecStart=/usr/bin/python3 %s/src/RimMandrake/a.py\n" % (DEP, DEP))
eff = OC.effective(dropin)
check(eff["ExecStart"] == ["/usr/bin/python3 %s/src/RimMandrake/a.py" % DEP], "ExecStart= clears earlier entries")
check(OC.judge(dropin, DEP) == [], "a drop-in that repoints the unit counts, the base file does not")

# --- the account plan reads the standard plan file: his rulings land in switching_plan.json, and on 2026-11-20 a
# week.conf drop-in left from 2026-11-05 still pointed account-plan at a week file that had none of them (order
# system>steven, steven line 25, no hard_pct_left: a dry pass at system 1% picked steven, and with a live run raised
# KeyError). Any RM_SWITCH_PLAN in a clock's unit is a problem; one in a single quoted Environment line too.
plan_unit = ("# /x/account-plan.service\n[Service]\nType=oneshot\n"
             "ExecStart=/usr/bin/python3 %s/src/RimMandrake/Utils/switching_plan.py check\n" % DEP)
check(OC.judge(plan_unit, DEP) == [], "the account plan with no RM_SWITCH_PLAN is clean")
week = plan_unit + ("# /x/account-plan.service.d/week.conf\n[Service]\n"
                    "Environment=RM_SWITCH_PLAN=%s/src/RimMandrake/Utils/switching_plan_week_2026-11-05.json\n" % DEP)
check(any("RM_SWITCH_PLAN" in p and "switching_plan_week_2026-11-05.json" in p for p in OC.judge(week, DEP)),
      "a drop-in pointing the account plan at another plan file is caught (got %r)" % OC.judge(week, DEP))
quoted = plan_unit + '[Service]\nEnvironment="A=1" "RM_SWITCH_PLAN=/tmp/p.json"\n'
check(any("RM_SWITCH_PLAN" in p for p in OC.judge(quoted, DEP)), "a quoted RM_SWITCH_PLAN among others is caught")
cleared = week + "[Service]\nEnvironment=\n"
check(OC.judge(cleared, DEP) == [], "Environment= after the drop-in clears it, as systemd does")
check(OC.judge(plan_unit + "[Service]\nEnvironment=RM_SWITCH_PLAN_DIR=/tmp/out\n", DEP) == [],
      "RM_SWITCH_PLAN_DIR (the output dir) is not the plan file")

# --- classify
units = {"rm-ops-watch", "rm-relentless-work-abc-g1", "testq-tick", "rm-new-thing", "rm-account-handover-x"}
check(OC.classify(units, conf, set(OC.owned_timers())) == ["rm-new-thing"],
      "an unclassified rm-* unit is named; globs in outside match; an owned old timer is classified")

# --- cut-over clocks (OPS_METRONOME_MIGRATE_CLOCKS_FENCED): the old timer a phase owns has no second life
owned = OC.owned_timers()
check(owned.get("rm-restart-reconcile.timer") == "raise", "the shipped table: raise owns rm-restart-reconcile.timer")
check(OC.classify({t[:-len(".timer")] for t in owned}, conf, set(owned)) == [], "every owned timer is classified by its phase")
check(OC.classify({"rm-x"}, conf, {"rm-x.timer"}) == [] and OC.classify({"rm-x"}, conf) == ["rm-x"],
      "an old timer a phase owns is classified only through that ownership")
check(OC.judge_owned(owned, lambda t: ("disabled", "inactive")) == [], "an owned timer disabled and stopped is clean")
two = OC.judge_owned({"rm-x.timer": "raise"}, lambda t: ("enabled", "inactive"))
check(len(two) == 1 and "two owners" in two[0] and "disable --now rm-x.timer" in two[0],
      "an owned timer still enabled is two owners, with the fix named")
check(len(OC.judge_owned({"rm-x.timer": "raise"}, lambda t: ("disabled", "active"))) == 1,
      "an owned timer disabled but still running is two owners")

# --- the shipped unit files of the one folder point at the deploy (every-folder-clock-runs-from-the-deploy is tested
# in selftest_units_one_folder.py; this keeps the old per-clock line)
for name in conf["clocks"]:
    p = OC.UNIT_DIR / (name + ".service")
    check(p.exists(), "clock %s has its unit in the one folder" % name)
    if p.exists():
        check(OC.judge(p.read_text(encoding="utf-8"), DEP) == [], "shipped %s runs from the deploy" % p.name)
check(OC.effective("ExecStart=/usr/bin/python3 \\\n  /x/src/RimMandrake/a.py\n")["ExecStart"][0].endswith("/x/src/RimMandrake/a.py"),
      "effective: a backslash-continued ExecStart keeps its continuation")

# --- the pinned clause: deploy_dirty and the snapshot a checker uses when it cannot read the deploy
import json  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from unittest.mock import patch  # noqa: E402


def git(d, *a):
    return subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          capture_output=True, text=True, check=True).stdout.strip()


with tempfile.TemporaryDirectory() as tmp:
    rep = Path(tmp) / "dep"
    (rep / "src/RimMandrake").mkdir(parents=True)
    (rep / "src/RimMandrake/a.py").write_text("x = 1\n")
    (rep / "notes.txt").write_text("n\n")
    git(tmp, "init", "-q", "-b", "main", str(rep))
    git(rep, "add", "src", "notes.txt")
    git(rep, "commit", "-q", "-m", "c1")
    head = git(rep, "rev-parse", "HEAD")
    git(rep, "update-ref", "refs/remotes/origin/main", "HEAD")   # c1 is published
    check(OC.deploy_dirty(str(rep)) == [], "deploy_dirty: a clean deploy has no local edit")
    (rep / "notes.txt").write_text("changed\n")
    check(OC.deploy_dirty(str(rep)) == [], "deploy_dirty: an edit outside src/ is not the pinned code")
    (rep / "src/RimMandrake/a.py").write_text("x = 2\n")
    (rep / "src/RimMandrake/new.py").write_text("y\n")
    d = OC.deploy_dirty(str(rep))
    check(len(d) == 2 and all(x.startswith("local edit in the deploy: ") for x in d),
          "deploy_dirty: an edited and an untracked file under src/ are each named (%s)" % d)
    check(OC.deploy_dirty(str(Path(tmp) / "nogit"))[0].startswith("git status in the deploy failed"),
          "deploy_dirty: a deploy git cannot read is a problem, not clean")
    snapf = Path(tmp) / "snap.json"
    s_dirty = OC.take_snapshot(str(rep), snapf)
    check(len(s_dirty["porcelain_src"]) == 2 and json.loads(snapf.read_text())["head"] == head
          and s_dirty["head_on_origin"] is True,
          "take_snapshot records HEAD, that it is on origin/main, and the src/ porcelain")
    git(rep, "checkout", "-q", "--", "src")
    (rep / "src/RimMandrake/new.py").unlink()
    snap = OC.take_snapshot(str(rep), snapf)
    now = time.time()
    check(OC.judge_snapshot(snap, str(rep), now, repo=rep) == [], "judge_snapshot: a fresh clean snapshot passes")
    check(any("local edit" in p for p in OC.judge_snapshot(s_dirty, str(rep), now, repo=rep)),
          "judge_snapshot: a snapshot with local edits fails")
    check(any("h old" in p for p in OC.judge_snapshot(snap, str(rep), now + 3600 * (OC.SNAPSHOT_MAX_H + 1), repo=rep)),
          "judge_snapshot: a stale snapshot fails")
    check(any("not the deploy" in p for p in OC.judge_snapshot(snap, "/elsewhere", now, repo=rep)),
          "judge_snapshot: a snapshot of another path fails")
    check(any("not a commit id" in p for p in OC.judge_snapshot(dict(snap, head="abc"), str(rep), now, repo=rep)),
          "judge_snapshot: a malformed HEAD fails")
    # a blind export: no git history at all. The recorded provenance carries it, and the note says so
    export = Path(tmp) / "export"
    export.mkdir()
    nb = []
    check(OC.judge_snapshot(snap, str(rep), now, repo=export, notes=nb) == [] and nb and "no git history" in nb[0],
          "judge_snapshot: a checkout with no history passes a clean on-origin snapshot and notes the gap (%s)" % nb)
    check(any("not on the deploy's origin/main" in p
              for p in OC.judge_snapshot(dict(snap, head_on_origin=False), str(rep), now, repo=export)),
          "judge_snapshot: a HEAD recorded as off origin/main fails even with no history here")
    check(any("not on the deploy's origin/main" in p
              for p in OC.judge_snapshot({k: v for k, v in snap.items() if k != "head_on_origin"}, str(rep), now,
                                         repo=export)),
          "judge_snapshot: a snapshot without head_on_origin is not taken as published")
    # the deploy commits locally: the taker records it off origin, and a checker holding the commit disproves it too
    (rep / "src/RimMandrake/a.py").write_text("x = 3\n")
    git(rep, "commit", "-q", "-am", "local")
    s_local = OC.take_snapshot(str(rep), snapf)
    check(s_local["head_on_origin"] is False and s_local["porcelain_src"] == [],
          "take_snapshot: a local commit in the deploy is recorded as off origin/main")
    other = Path(tmp) / "checker"
    git(tmp, "clone", "-q", str(rep), str(other))
    git(other, "checkout", "-q", "--detach", head)
    check(any("not an ancestor" in p for p in OC.judge_snapshot(dict(s_local, head_on_origin=True), str(rep), now,
                                                                repo=other)),
          "judge_snapshot: a checker that holds the commit but not as an ancestor fails it")
    check(any("local edit" in p for p in OC.judge_snapshot({k: v for k, v in snap.items() if k != "porcelain_src"},
                                                           str(rep), now, repo=rep)),
          "judge_snapshot: a snapshot with no porcelain field is not taken as clean")
    # Drive the real snapshot routing with an unreadable deploy and a matching installed-unit fixture.
    lock = Path(tmp) / "locked"
    lock.mkdir()
    units = shutil.copytree(OC.UNIT_DIR, Path(tmp) / "installed")
    env = {"RM_OPS_DEPLOY": str(lock), "RM_OPS_SNAPSHOT": str(Path(tmp) / "missing.json"),
           "RM_UNIT_INSTALL_DIR": str(units)}
    with patch.dict(os.environ, env), patch.object(OC, "readable", return_value=False), \
            patch.object(OC, "_sc", return_value=subprocess.CompletedProcess([], 0, "", "")):
        empty = dict(conf, clocks={}, outside=["*"])
        r = OC.check(empty)
        check(len(r) == 1 and "snapshot" in r[0] and "cannot be read" in r[0],
              "check: an unreadable deploy with no snapshot fails by name, not 'holds no src'")
        snapf.write_text(json.dumps(dict(snap, deploy=str(lock))))
        os.environ["RM_OPS_SNAPSHOT"] = str(snapf)
        notes = []
        r = OC.check(empty, notes)
        check(r == [] and any("judged from snapshot" in n for n in notes),
              "check: an unreadable deploy is judged from the snapshot, and says so (%s %s)" % (r, notes))

# the committed snapshot is a reading of the real deploy
real = json.loads(OC.SNAPSHOT.read_text(encoding="utf-8"))
check(real["deploy"] == DEP and set(real) >= {"head", "head_on_origin", "porcelain_src", "taken", "uid"},
      "the committed snapshot is of the dispatch deploy and carries head, head_on_origin, porcelain, time and uid")

print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
