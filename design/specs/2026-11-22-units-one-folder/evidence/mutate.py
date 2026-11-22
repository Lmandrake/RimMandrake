import subprocess, sys, shutil
from pathlib import Path
R = Path.cwd()
OC = R / "src/RimMandrake/Utils/ops_clocks.py"; DM = R / "src/RimMandrake/Utils/deadman_check.py"
T = ["python3", "src/RimMandrake/Utils/selftest_units_one_folder.py"]
M = [
 (OC, '        elif f != i:\n', '        elif False:\n', "a differing text is never named"),
 (OC, '        elif i is MASK:\n', '        elif False:\n', "a mask is judged as text"),
 (OC, '            and not any(fnmatch.fnmatchcase(base, g) for g in THROWAWAY))', '            and True)', "throwaways are judged"),
 (OC, '    return path.name.startswith(("selftest_", "test_")) or "tests" in path.parts', '    return True', "every source counts as a test"),
 (OC, '    except OSError:\n        return None\n', '    except OSError:\n        return {}\n', "an unreadable dir reads as empty"),
 (OC, '        if apply and not same:\n', '        if not same:\n', "a plan writes"),
 (OC, '        if inst.get(n) is MASK:\n', '        if False:\n', "install writes over a mask"),
 (OC, '        elif f is None:\n', '        elif False:\n', "a machine-only unit is not named"),
 (OC, '        if n not in installed:\n', '        if False:\n', "a folder unit not installed is not named"),
 (DM, '        probs = ["units: could not look (%s: %s)" % (type(e).__name__, e)]', '        probs = []', "a failed look is clean"),
 (DM, '    arms.update(units_arm())\n', '', "the arm is not called"),
]
caught = 0
for path, old, new, name in M:
    s = path.read_text(); assert old in s, name
    path.write_text(s.replace(old, new, 1))
    try:
        r = subprocess.run(T, capture_output=True, text=True, timeout=120)
    finally:
        path.write_text(s)
    red = r.returncode != 0
    caught += red
    print("%-7s %s" % ("CAUGHT" if red else "MISSED", name))
print("%d of %d mutants caught" % (caught, len(M)))
r = subprocess.run(T, capture_output=True, text=True); print("unmutated:", r.stdout.strip().splitlines()[-1])
