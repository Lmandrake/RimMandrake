#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_CERTIFY_BARS_BEFORE_JUDGE_RED_TEST_WENT_IN and, with --red-seen, for
RIMMANDRAKE_RECORD_RED_SEEN_PER_TEST_OR_PASSED_GREEN (spec: design/specs/2026-11-15-cheap-guards-at-every-door.md,
guard PRE_JUDGEMENT_CERTIFICATE). Written by the filing seat; the builder does not edit it.

    python3 src/RimMandrake/rimflow/acceptance/guard_judge_certificate_accept.py              # "PASS 18/18" when built
    python3 src/RimMandrake/rimflow/acceptance/guard_judge_certificate_accept.py --red-seen   # "PASS 28/28" (second ticket)

THE CONTRACT IT FIXES: `src/RimMandrake/rimflow/judge_certificate.py`. No model is called anywhere in it.
  build_id(root, paths) -> str      a hash of the CONTENT of those repo-relative files (a missing one hashes as missing)
  run_offline(root, mod, runner=subprocess.run, now=None) -> {"ran": n, "failed": [ids]}
      runs every test of design/concepts/<mod>/version/test_table.json whose kind is "offline" (its `command`, cwd
      root) and writes back runs_today = {"ran": True, "rc", "seconds", "last", "at", "result": "PASS"|"FAIL",
      "build": build_id(root, test["reads"] + [test["file"]])}
  certify(root, mod, to="blind_challenge") -> {"ok": bool, "rows": [...], "did_not_run": [...]}
      one row per (bar, offline decider, clause): {"bar", "test", "clause", "status", "observed", "would_pass",
      "smallest_fix"}; status PASS / REFUSED / WARN. ok is False when any row is REFUSED. Clauses:
        registered         the decider is in the table with a file that exists and a command
        ran_on_this_build  runs_today.ran and runs_today.build == build_id now (a table with no build field refuses,
                           the fix being `maturation.py certificate <Mod> --run`)
        green              runs_today.rc == 0 and result PASS, and the test carries no `known_red`
        red_seen           first ticket: always WARN "UNPROVEN" (never refuses). Second ticket (--red-seen):
                           PASS when version/evidence/red_seen.json[test] has rc != 0 and test_blob == the test
                           file's content hash now; WARN "grandfathered" when
                           version/evidence/red_seen_grandfather.json[test] == that hash; else REFUSED.
      a bar's offline deciders are bar["offline_decides"]. A table that cannot be read: ok True and one did_not_run
      line (a guard that cannot look lets the mod through and says so).
  CLI  maturation.py --root R certificate <Mod> [--to STAGE] [--run] [--json] [--grandfather]: exit 0 ok, 1 refused;
       each refusal prints observed, would_pass and smallest_fix. `maturation.evaluate` carries the clause
       `judge_certificate` on offline_build -> blind_challenge and blind_challenge -> in_game.
  second ticket: red_seen(root, mod, test_id, patch=None, runner=subprocess.run, now=None) -> {"ok", "why"}
      applies the patch (git apply, in root), runs the test, wants rc != 0, reverses the patch and proves the files
      are byte-identical again; ok records red_seen.json[test]; a test that stays green under the fault returns
      ok False ("stayed green") and records nothing. grandfather(root, mod) writes the grandfather file once.
      CLI: maturation.py red-seen <Mod> <TEST> --patch FILE.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
sys.path.insert(0, RIMFLOW)
RESULTS = []
MOD = "Fix"


def check(ok, what):
    RESULTS.append(bool(ok))
    print(("ok    " if ok else "FAIL  ") + what)


def attempt(fn, default):
    try:
        return fn()
    except Exception as e:  # noqa: BLE001
        print("      raised %r" % (e,))
        return default


def git(root, *a):
    return subprocess.run(["git", "-C", root] + list(a), capture_output=True, text=True)


def fixture(root):
    os.makedirs(os.path.join(root, "design/concepts", MOD, "version"))
    os.makedirs(os.path.join(root, "src"))
    with open(os.path.join(root, "src/kernel.py"), "w") as f:
        f.write("LIMIT = 5\n")
    for name, body in (("t_good.py", "import kernel, sys\nsys.exit(0 if kernel.LIMIT == 5 else 1)\n"),
                       ("t_red.py", "import sys\nprint('1 of 3 checks failed')\nsys.exit(1)\n"),
                       ("t_blind.py", "import sys\nsys.exit(0)\n")):
        with open(os.path.join(root, "src", name), "w") as f:
            f.write("import os, sys\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n" + body)

    def t(tid, f):
        return {"id": tid, "kind": "offline", "stage": "4-5", "file": "src/" + f, "reads": ["src/kernel.py"],
                "command": "%s src/%s" % (sys.executable, f)}
    table = {"mod": MOD, "version": "0.1.0",
             "tests": {"T_GOOD": t("T_GOOD", "t_good.py"), "T_RED": t("T_RED", "t_red.py"),
                       "T_BLIND": t("T_BLIND", "t_blind.py"),
                       "sc_live": {"id": "sc_live", "kind": "live_minimal", "stage": "6", "file": "src/t_good.py",
                                   "entry": "x", "runs_today": {"ran": False}}},
             "bars": [{"id": "bar_good", "decides": ["T_GOOD", "sc_live"], "offline_decides": ["T_GOOD"]},
                      {"id": "bar_blind", "decides": ["T_BLIND"], "offline_decides": ["T_BLIND"]}]}
    save(root, table)
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "-c", "user.email=a@b", "-c", "user.name=t", "commit", "-qm", "base")
    return table


def tpath(root):
    return os.path.join(root, "design/concepts", MOD, "version/test_table.json")


def save(root, table):
    with open(tpath(root), "w") as f:
        json.dump(table, f, indent=1)


def load(root):
    return json.load(open(tpath(root)))


def refused(v, clause, test=None):
    return [r for r in (v or {}).get("rows") or [] if r.get("status") == "REFUSED" and r.get("clause") == clause
            and (test is None or r.get("test") == test)]


def cli(root, *a):
    return subprocess.run([sys.executable, os.path.join(RIMFLOW, "maturation.py"), "--root", root] + list(a),
                          capture_output=True, text=True)


def main():
    red = "--red-seen" in sys.argv
    try:
        import judge_certificate as JC
    except Exception as e:  # noqa: BLE001
        JC = None
        print("FAIL  import judge_certificate: %r" % (e,))
    with tempfile.TemporaryDirectory() as root:
        fixture(root)
        if red:      # part one is about the first three clauses: grandfather the fixture so red_seen only warns here
            attempt(lambda: JC.grandfather(root, MOD), None)
        a = attempt(lambda: JC.build_id(root, ["src/kernel.py", "src/t_good.py"]), None)
        v0 = attempt(lambda: JC.certify(root, MOD), {})
        check(v0.get("ok") is False and refused(v0, "ran_on_this_build", "T_GOOD"),
              "a table with no recorded build refuses ran_on_this_build (the Pyrelands case: a stored flag is not a run)")
        fix = str((refused(v0, "ran_on_this_build", "T_GOOD") or [{}])[0].get("smallest_fix"))
        check("certificate" in fix and "--run" in fix, "that refusal names the command that passes it")
        s = attempt(lambda: JC.run_offline(root, MOD), {})
        t = load(root)["tests"]
        check(s.get("ran") == 3 and t["T_GOOD"].get("runs_today", {}).get("build") == a and a,
              "run_offline runs the offline tests and stamps each with its build")
        check(t["T_GOOD"].get("runs_today", {}).get("rc") == 0 and t["T_RED"].get("runs_today", {}).get("rc") == 1
              and t["sc_live"]["runs_today"] == {"ran": False}, "it records rc and leaves in-game tests alone")
        v = attempt(lambda: JC.certify(root, MOD), {})
        check(v.get("ok") is True and not [r for r in v.get("rows") or [] if r.get("status") == "REFUSED"],
              "green deciders run on this build certify (T_RED decides no bar, so it does not refuse)")
        warn = [r for r in v.get("rows") or [] if r.get("clause") == "red_seen"]
        if not red:
            check(len(warn) == 2 and all(r.get("status") == "WARN" for r in warn), "red_seen rows are WARN, never a refusal")
        table = load(root)
        table["bars"].append({"id": "bar_red", "decides": ["T_RED"], "offline_decides": ["T_RED"]})
        save(root, table)
        v = attempt(lambda: JC.certify(root, MOD), {})
        r = (refused(v, "green", "T_RED") or [{}])[0]
        check(v.get("ok") is False and r.get("bar") == "bar_red" and "1 of 3" in str(r.get("observed")),
              "a red deciding test refuses its bar with the test's own last line (the ExplosiveKnockback cycle 1 case)")
        check(all(str(r.get(k) or "").strip() for k in ("observed", "would_pass", "smallest_fix")),
              "the refusal carries observed, would_pass and smallest_fix")
        table["bars"] = table["bars"][:2]
        save(root, table)
        with open(os.path.join(root, "src/kernel.py"), "w") as f:
            f.write("LIMIT = 6\n")
        b = attempt(lambda: JC.build_id(root, ["src/kernel.py", "src/t_good.py"]), None)
        v = attempt(lambda: JC.certify(root, MOD), {})
        check(a and b and a != b and v.get("ok") is False and refused(v, "ran_on_this_build", "T_GOOD"),
              "a source change after the run makes the recorded run stale")
        with open(os.path.join(root, "src/kernel.py"), "w") as f:
            f.write("LIMIT = 5\n")
        check(attempt(lambda: JC.certify(root, MOD), {}).get("ok") is True, "the same content certifies again (content, not time)")
        table = load(root)
        table["tests"]["T_GOOD"]["known_red"] = "SOME_OPEN_ITEM"
        save(root, table)
        v = attempt(lambda: JC.certify(root, MOD), {})
        check(v.get("ok") is False and "SOME_OPEN_ITEM" in json.dumps(refused(v, "green", "T_GOOD")),
              "a known-red mark refuses and names its item")
        del table["tests"]["T_GOOD"]["known_red"]
        table["bars"][0]["offline_decides"] = ["T_GOOD", "T_GONE"]
        save(root, table)
        v = attempt(lambda: JC.certify(root, MOD), {})
        check(v.get("ok") is False and refused(v, "registered", "T_GONE"), "a decider the table does not hold refuses registered")
        table["bars"][0]["offline_decides"] = ["T_GOOD"]
        table["tests"]["T_GOOD"]["file"] = "src/moved_away.py"
        save(root, table)
        check(refused(attempt(lambda: JC.certify(root, MOD), {}), "registered", "T_GOOD"), "a decider whose file is gone refuses registered")
        table["tests"]["T_GOOD"]["file"] = "src/t_good.py"
        save(root, table)
        r = cli(root, "certificate", MOD)
        check(r.returncode == 0, "CLI: a certifying mod exits 0 (%s)" % r.returncode)
        table["bars"].append({"id": "bar_red", "decides": ["T_RED"], "offline_decides": ["T_RED"]})
        save(root, table)
        r = cli(root, "certificate", MOD)
        check(r.returncode == 1 and "bar_red" in r.stdout and "would_pass" in r.stdout.replace(" ", "_"),
              "CLI: a refused mod exits 1 and prints the refusal's path to pass")
        table["bars"] = table["bars"][:2]
        save(root, table)
        with open(tpath(root), "w") as f:
            f.write("{ not json")
        v = attempt(lambda: JC.certify(root, MOD), {})
        check(v.get("ok") is True and len(v.get("did_not_run") or []) == 1,
              "an unreadable table is did_not_run and lets the mod through")
        save(root, table)
    if red:
        with tempfile.TemporaryDirectory() as root2:
            fixture(root2)
            attempt(lambda: JC.run_offline(root2, MOD), {})
            red_part(JC, root2)
    msrc = attempt(lambda: open(os.path.join(RIMFLOW, "maturation.py"), encoding="utf-8").read(), "")
    check("judge_certificate" in msrc.split("def evaluate(", 1)[-1].split("\ndef advance(", 1)[0],
          "maturation.evaluate carries the judge_certificate clause")
    dsrc = attempt(lambda: open(os.path.join(RIMFLOW, "maturation_dispatch.py"), encoding="utf-8").read(), "")
    check("judge_certificate" in dsrc or "certify(" in dsrc, "the Dispatch tick reads the certificate before a judge or visit launch")
    n = sum(RESULTS)
    print("%s %d/%d" % ("PASS" if n == len(RESULTS) else "FAIL", n, len(RESULTS)))
    return 0 if n == len(RESULTS) else 1


def red_part(JC, root):
    ev = os.path.join(root, "design/concepts", MOD, "version/evidence")
    v = attempt(lambda: JC.certify(root, MOD), {})
    check(refused(v, "red_seen", "T_GOOD") and refused(v, "red_seen", "T_BLIND"),
          "with no proof and no grandfather list, red_seen refuses")
    fixtxt = str((refused(v, "red_seen", "T_GOOD") or [{}])[0].get("smallest_fix"))
    check("red-seen" in fixtxt, "that refusal names the red-seen verb")
    patch = os.path.join(root, "fault.patch")
    with open(patch, "w") as f:
        f.write("--- a/src/kernel.py\n+++ b/src/kernel.py\n@@ -1 +1 @@\n-LIMIT = 5\n+LIMIT = 50\n")
    r = attempt(lambda: JC.red_seen(root, MOD, "T_GOOD", patch=patch), {})
    rec = attempt(lambda: json.load(open(os.path.join(ev, "red_seen.json"))), {})
    check(r.get("ok") is True and rec.get("T_GOOD", {}).get("rc") not in (0, None), "a test that goes red under the fault is recorded")
    check(open(os.path.join(root, "src/kernel.py")).read() == "LIMIT = 5\n" and git(root, "status", "--porcelain", "src").stdout.strip() == "",
          "the fault is reversed and the source is byte-identical again")
    r = attempt(lambda: JC.red_seen(root, MOD, "T_BLIND", patch=patch), {})
    rec = attempt(lambda: json.load(open(os.path.join(ev, "red_seen.json"))), {})
    check(r.get("ok") is False and "stayed green" in str(r.get("why")) and "T_BLIND" not in rec,
          "a test that stays green under the fault is NOT recorded (the test that could not fail)")
    check(open(os.path.join(root, "src/kernel.py")).read() == "LIMIT = 5\n", "the source is restored after that too")
    v = attempt(lambda: JC.certify(root, MOD), {})
    row = [x for x in v.get("rows") or [] if x.get("clause") == "red_seen" and x.get("test") == "T_GOOD"]
    check(row and row[0].get("status") == "PASS" and refused(v, "red_seen", "T_BLIND"), "the proven test passes red_seen; the blind one still refuses")
    attempt(lambda: JC.grandfather(root, MOD), None)
    v = attempt(lambda: JC.certify(root, MOD), {})
    row = [x for x in v.get("rows") or [] if x.get("clause") == "red_seen" and x.get("test") == "T_BLIND"]
    check(row and row[0].get("status") == "WARN" and "grandfather" in str(row[0].get("observed")).lower() and v.get("ok") is True,
          "a grandfathered test warns and does not refuse")
    with open(os.path.join(root, "src/t_blind.py"), "a") as f:
        f.write("# edited after the grandfather list\n")
    attempt(lambda: JC.run_offline(root, MOD), {})
    v = attempt(lambda: JC.certify(root, MOD), {})
    check(refused(v, "red_seen", "T_BLIND"), "a test edited after grandfathering owes a red proof")
    before = attempt(lambda: open(os.path.join(ev, "red_seen_grandfather.json")).read(), "")
    attempt(lambda: JC.grandfather(root, MOD), None)
    check(before and before == attempt(lambda: open(os.path.join(ev, "red_seen_grandfather.json")).read(), ""),
          "the grandfather list is written once and never widened")
    r = cli(root, "red-seen", MOD, "T_GOOD", "--patch", patch)
    check(r.returncode == 0, "CLI: maturation.py red-seen exits 0 on a proven test")


if __name__ == "__main__":
    sys.exit(main())
