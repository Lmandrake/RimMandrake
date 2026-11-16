#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_RUN_LAUNCH_CHECKS_FIVE_STEWARDS_HIT_GATES (spec:
design/specs/2026-11-15-cheap-guards-at-every-door.md, guard GATE_FIRST). Written by the filing seat; the builder does
not edit it (a clause believed wrong goes to the Conductor).

    python3 src/RimMandrake/rimflow/acceptance/guard_launch_checks_accept.py     # exit 0 and "PASS 21/21" when built

THE CONTRACT IT FIXES
1. `src/RimMandrake/rimflow/launch_checks.py`
   parse(text) -> [{"kind": "must-pass"|"must-fail"|"unknown", "cmd": str, "line": str}]
       reads only the item's `## launch-checks` section, one `must-pass: <command>` or `must-fail: <command>` per line;
       no section -> []. Prose elsewhere is never read.
   run(checks, cwd, timeout_s=120, runner=subprocess.run) -> {"ok": bool, "refusals": [...], "did_not_run": [...], "ms": int}
       must-pass exits 0, or must-fail exits non-zero: passed.
       must-pass exits non-zero: a refusal. must-fail exits 0: a refusal ("already passes").
       exit 126/127, a timeout, an OSError, kind unknown: did_not_run (NEVER a refusal; ok stays true).
       a refusal is {"check", "kind", "evidence" (the command's last output), "would_pass", "smallest_fix"}, all non-empty.
       runner is called as runner(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout_s).
   block_for("advance", mod=, to=) -> "## launch-checks\nmust-pass: python3 src/RimMandrake/rimflow/maturation.py gate <mod> --to <to>\n"
   block_for("fix_red", cmd=)     -> "## launch-checks\nmust-fail: <cmd>\n"
2. `detached_helper.launch_check_refusal(item_text, cwd, runner=subprocess.run, timeout_s=120) -> (refusal or None, notes)`
       refusal: text starting "refused: launch check" that carries the evidence, would_pass and smallest_fix.
       notes: one "launch check did not run: ..." line per check that could not run (the launch goes ahead).
   `detached_helper.py launch` calls it in the run's clone before the unit starts, and takes
   `--skip-launch-checks "<why>"` (the Conductor's bypass, recorded on the run record).
3. `maturation.py gate <Mod> --to <stage>`: exit 0 when evaluate() refuses nothing but the clauses in its own
   hand_steps (what the launched steward supplies); exit 1 otherwise, printing each refusal. Read-only.
4. `maturation_autonomy.py` writes the block into the items it files for stewards that advance a mod
   (launch_checks.block_for is called there).
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RIMFLOW, "..", "..", ".."))
sys.path.insert(0, RIMFLOW)
RESULTS = []


def check(ok, what):
    RESULTS.append(bool(ok))
    print(("ok    " if ok else "FAIL  ") + what)


def attempt(fn, default=None):
    try:
        return fn()
    except Exception as e:  # noqa: BLE001
        return default if default is not None else "raised %r" % (e,)


ITEM = """## spec
An advance. must-pass: echo this prose line is not a check

## launch-checks
must-pass: exit 0
must-fail: exit 3
maybe: exit 0

## verify
must-fail: exit 0
"""


def main():
    try:
        import launch_checks as LC
    except Exception as e:  # noqa: BLE001
        LC = None
        print("FAIL  import launch_checks: %r" % (e,))
    ck = attempt(lambda: LC.parse(ITEM), [])
    check(isinstance(ck, list) and [c.get("kind") for c in ck] == ["must-pass", "must-fail", "unknown"],
          "parse reads the three lines of ## launch-checks and nothing else (%s)" % [c.get("kind") for c in ck or []])
    check(attempt(lambda: LC.parse("## spec\nno block here\n"), None) == [], "no section parses to []")
    with tempfile.TemporaryDirectory() as tmp:
        def run(lines):
            return attempt(lambda: LC.run(LC.parse("## launch-checks\n" + "\n".join(lines) + "\n"), tmp, timeout_s=5), {})
        r = run(["must-pass: exit 0", "must-fail: exit 3"])
        check(r.get("ok") is True and r.get("refusals") == [] and r.get("did_not_run") == [], "good checks pass")
        r = run(["must-pass: echo the gate refuses: 28 of 42 bars not runnable; exit 1"])
        ref = (r.get("refusals") or [{}])[0]
        check(r.get("ok") is False and "28 of 42" in str(ref.get("evidence")), "a failing must-pass refuses with its output")
        check(all(str(ref.get(k) or "").strip() for k in ("check", "kind", "evidence", "would_pass", "smallest_fix")),
              "the refusal carries evidence, would_pass and smallest_fix")
        r = run(["must-fail: echo 14 tests pass; exit 0"])
        ref = (r.get("refusals") or [{}])[0]
        check(r.get("ok") is False and "already passes" in str(ref).lower(), "a must-fail that passes refuses: already passes")
        r = run(["must-pass: /no/such/tool --x"])
        check(r.get("ok") is True and len(r.get("did_not_run") or []) == 1 and not r.get("refusals"),
              "a command that cannot run (exit 127) is did_not_run, never a refusal")
        r = run(["must-fail: /no/such/tool --x"])
        check(r.get("ok") is True and len(r.get("did_not_run") or []) == 1, "a must-fail that cannot run is did_not_run, not a pass")
        r = run(["must-pass: sleep 30"])
        check(r.get("ok") is True and len(r.get("did_not_run") or []) == 1, "a timeout is did_not_run")
        r = run(["maybe: exit 1"])
        check(r.get("ok") is True and len(r.get("did_not_run") or []) == 1, "an unknown key is did_not_run")
        r = run(["must-pass: test -f marker.txt"])
        open(os.path.join(tmp, "marker.txt"), "w").close()
        r2 = run(["must-pass: test -f marker.txt"])
        check(r.get("ok") is False and r2.get("ok") is True, "checks run in cwd (the run's clone)")
        check(isinstance(r2.get("ms"), int), "the run reports its time in ms")
        b = attempt(lambda: LC.block_for("advance", mod="Pyrelands", to="blind_challenge"), "")
        check(b == "## launch-checks\nmust-pass: python3 src/RimMandrake/rimflow/maturation.py gate Pyrelands --to blind_challenge\n",
              "block_for advance writes the gate line")
        b = attempt(lambda: LC.block_for("fix_red", cmd="python3 x/selftest_y.py"), "")
        check(b == "## launch-checks\nmust-fail: python3 x/selftest_y.py\n", "block_for fix_red writes the must-fail line")
        # 2. the door
        try:
            import detached_helper as DH
            ref, notes = DH.launch_check_refusal("## launch-checks\nmust-fail: echo green; exit 0\n", tmp, timeout_s=5)
            ok_ref, ok_notes = DH.launch_check_refusal("## launch-checks\nmust-pass: exit 0\nmust-pass: /no/such/tool\n", tmp, timeout_s=5)
            none_ref, none_notes = DH.launch_check_refusal("## spec\nplain item\n", tmp, timeout_s=5)
        except Exception as e:  # noqa: BLE001
            ref, notes, ok_ref, ok_notes, none_ref, none_notes = "raised %r" % (e,), [], "x", [], "x", ["x"]
        check(isinstance(ref, str) and ref.startswith("refused: launch check") and "green" in ref and "already passes" in ref.lower(),
              "the door refuses a launch whose must-fail already passes, with the evidence")
        check(ok_ref is None and len(ok_notes) == 1 and ok_notes[0].startswith("launch check did not run"),
              "a check that cannot run lets the launch through with one did-not-run line")
        check(none_ref is None and none_notes == [], "an item with no block launches as before")
    src = attempt(lambda: open(os.path.join(RIMFLOW, "detached_helper.py"), encoding="utf-8").read(), "")
    check("--skip-launch-checks" in src and "launch_check_refusal(" in src.split("def launch(", 1)[-1],
          "launch() calls the check and takes --skip-launch-checks")
    r = subprocess.run([sys.executable, os.path.join(RIMFLOW, "maturation.py"), "gate", "--help"], capture_output=True, text=True)
    check(r.returncode == 0, "maturation.py has the gate verb")
    agree, seen = True, 0
    try:
        import maturation as M
        for mod in M.versioned(REPO):
            rec = M.load(REPO, mod) or {}
            cur = rec.get("stage")
            if cur not in M.WORDS or M.WORDS.index(cur) + 1 >= len(M.WORDS):
                continue
            to = M.WORDS[M.WORDS.index(cur) + 1]
            res = M.evaluate(REPO, mod, to)
            want = 0 if all(x.get("clause") in res["hand_steps"] for x in res["verdict"]["refusals"]) else 1
            got = subprocess.run([sys.executable, os.path.join(RIMFLOW, "maturation.py"), "gate", mod, "--to", to],
                                 capture_output=True, text=True).returncode
            seen += 1
            agree = agree and got == want
    except Exception as e:  # noqa: BLE001
        agree = False
        print("      gate/evaluate comparison raised %r" % (e,))
    check(agree and seen > 0, "gate's exit code agrees with evaluate() for every versioned mod (%d read)" % seen)
    asrc = attempt(lambda: open(os.path.join(RIMFLOW, "maturation_autonomy.py"), encoding="utf-8").read(), "")
    check("block_for(" in asrc, "maturation_autonomy writes the block into the steward items it files")
    n = sum(RESULTS)
    print("%s %d/%d" % ("PASS" if n == len(RESULTS) else "FAIL", n, len(RESULTS)))
    return 0 if n == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
