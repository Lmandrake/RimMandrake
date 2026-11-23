#!/usr/bin/env python3
"""list_effect_mutants.py: planted faults in list_effect.py; selftest_list_effect.py must go red on each.

Item RIMMANDRAKE_BUILD_LIST_OUTCOME_CHECKS_SEVEN_DONE_NEVER_CLOSED (mutate-your-checker). Each mutant is one realistic
fault; the selftest must FAIL on it by its own FAIL line, and the unmutated control must pass first. The file is mutated
IN PLACE (cli.py imports it from its own folder) and restored in `finally`; the run ends by proving the bytes are back.

    python3 src/RimMandrake/rimflow/acceptance/list_effect_mutants.py      exit 0: control green, every mutant caught
"""
import hashlib
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
TARGET = os.path.join(RIMFLOW, "list_effect.py")
TEST = os.path.join(RIMFLOW, "selftest_list_effect.py")

MUTANTS = [
    ("unmeasured closes", 'return {"holds": "close", "fails": "work"}.get(verdict, "blind")',
     'return {"holds": "close", "fails": "work"}.get(verdict, "close")'),
    ("a holding check is accepted with no reason", '    if holds_why and str(holds_why).strip():',
     '    if True:'),
    ("vacuous commands pass the gate", '    if p["kind"] == "cmd" and VACUOUS.match(p["cmd"]):',
     '    if False:'),
    ("the pause is ignored", '        if paused:\n            put("pipeline_paused", paused)',
     '        if False:\n            put("pipeline_paused", paused)'),
    ("pipe off is ignored", '        if off:\n            put("off", off)', '        if False:\n            put("off", off)'),
    ("an unreadable store reads as on", '            put("blind", "the control store could not be read',
     '            off = None\n            put("work", "the control store could not be read'),
    ("a refused close is sent again", '        if ref.get("fp") == fp:', '        if False:'),
    ("exit 2 reads fails", '        if r.returncode == 1:', '        if r.returncode in (1, 2):'),
    ("a missing page holds for path-lacks", '("unmeasured", "the file does not exist, so it cannot be read for the text")',
     '("holds", "gone")'),
    ("the close loses its unit", 'env["RM_ROLE_UNIT"] = os.environ.get("RM_ROLE_UNIT") or UNIT',
     'env.pop("RM_ROLE_UNIT", None)'),
    ("a dry beat writes state", '    if apply:\n        _write(os.path.join(d, "state.json"), st)',
     '    if True:\n        os.makedirs(d, exist_ok=True)\n        _write(os.path.join(d, "state.json"), st)'),
    ("the filing commit is never read", '        then, rev = at_commit(text, root, filed_ts)',
     '        then, rev = None, "skipped"'),
    ("the output is left off the close", '        text = "outcome check holds at %s: %s | output: %s | evidence %s" % (\n'
     '            head, eff, _one(out, OUT_IN_EVENT) or "(none)", epath)',
     '        text = "outcome check holds at %s: %s | evidence %s" % (head, eff, epath)'),
]


def run_test():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, TEST], capture_output=True, text=True, timeout=900, env=env,
                       stdin=subprocess.DEVNULL)
    out = r.stdout + r.stderr
    return r.returncode, [ln for ln in out.splitlines() if ln.startswith("FAIL ")], out


def main():
    orig = open(TARGET, encoding="utf-8").read()
    digest = hashlib.sha256(orig.encode()).hexdigest()
    shutil.rmtree(os.path.join(RIMFLOW, "__pycache__", "list_effect"), ignore_errors=True)
    rc, fails, out = run_test()
    if rc != 0:
        print("CONTROL RED: the unmutated selftest fails, so no mutant result means anything\n" + out[-2000:])
        return 3
    print("control  green")
    missed = []
    try:
        for name, old, new in MUTANTS:
            if orig.count(old) != 1:
                print("NOT APPLIED  %s: its anchor is %s" % (name, "absent" if not orig.count(old) else "not unique"))
                missed.append(name)
                continue
            with open(TARGET, "w", encoding="utf-8") as f:
                f.write(orig.replace(old, new))
            rc, fails, _ = run_test()
            caught = rc != 0 and bool(fails)
            print("%-8s %s%s" % ("CAUGHT" if caught else "MISSED", name, ("  -- " + fails[0][5:120]) if fails else ""))
            if not caught:
                missed.append(name)
    finally:
        with open(TARGET, "w", encoding="utf-8") as f:
            f.write(orig)
    back = hashlib.sha256(open(TARGET, encoding="utf-8").read().encode()).hexdigest() == digest
    print("restored %s" % ("byte-identical" if back else "NOT IDENTICAL: restore list_effect.py from git"))
    print("%d of %d mutants caught" % (len(MUTANTS) - len(missed), len(MUTANTS)))
    return 0 if back and not missed else 1


if __name__ == "__main__":
    sys.exit(main())
