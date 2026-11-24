#!/usr/bin/env python3
"""Plant one fault at a time in temporary copies and require the corresponding selftest failure."""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEST = "Utils/selftest_ingame_visit_owed.py"
OW = "Utils/ops_watch.py"
MD = "rimflow/maturation_dispatch.py"
RULES = "Utils/ops_watch_rules.json"
MUTANTS = (
    (OW, 'out[INGAME_VISIT_OWED_KEY] = ingame_visit_owed', 'out["unused"] = ingame_visit_owed',
     "only-owed-bridge-checks-wait: both Arch locks free"),
    (MD, 'if "testq" not in tests[k]', 'if k in tests',
     "only-owed-bridge-checks-wait: earlier PASS"),
    (MD, 'bridge = [k for k in bridge if k not in recorded]', 'bridge = list(bridge)',
     "only-owed-bridge-checks-wait: earlier PASS"),
    (OW, 'if e.get("blocked") or e.get("held") or e.get("owed") == "exit met":\n            continue\n        checks =',
     'if e.get("blocked") or e.get("owed") == "exit met":\n            continue\n        checks =',
     "only-owed-bridge-checks-wait: owner hold"),
    (OW, 'if g["state"] == "HELD" or g.get("owner_hold")', 'if g["game"] == "a" and g["state"] == "HELD"',
     "either-game-driving-the-mod-is-busy: ArchSmall"),
    (OW, 'return U(g.get("line") or "could not look at an Arch lock", unit)', 'continue',
     "could-not-look-is-unmeasured: unreadable ArchSmall"),
    (OW, 'if game_names.machine() != "archmagi":', 'if False:',
     "could-not-look-is-unmeasured: a different game host"),
    (OW, 'minutes = (now - waiting_since[mod]["at"]) / 60', 'minutes = (now - waiting[mod][0]) / 60',
     "undriven-clock: after a driver releases"),
    (OW, 'if "active" in lives.values():\n                del waiting[mod]',
     'if "active" in lives.values():\n                pass',
     "live-pipeline-visit-is-busy: an active in-game unit"),
    (RULES, '"key": "maturation.ingame_visit_owed_no_driver_min", "op": ">", "value": 30,',
     '"key": "maturation.ingame_visit_owed_no_driver_min", "op": ">", "value": 60,',
     "alarm-crosses-and-reopens: 60 min crosses"),
)


def run(root, tmp):
    return subprocess.run([sys.executable, str(root / TEST)], capture_output=True, text=True, timeout=90,
                          env=dict(os.environ, TMPDIR=str(tmp), PYTHONDONTWRITEBYTECODE="1"))


def main():
    with tempfile.TemporaryDirectory(prefix="mut_visit_owed_") as tmp:
        root = Path(tmp) / "src" / "RimMandrake"
        for src, dst, skip in ((HERE.parents[2], Path(tmp), {"src"}), (HERE.parent, root, {"Utils", "rimflow"}),
                               (HERE, root / "Utils", set()), (HERE.parent / "rimflow", root / "rimflow", set())):
            dst.mkdir(parents=True, exist_ok=True)
            for p in src.iterdir():
                if p.name not in skip and p.name not in (".git", "__pycache__"):
                    (dst / p.name).symlink_to(p)
        for rel in (TEST, OW, MD, RULES):
            (root / rel).unlink()
            shutil.copyfile(HERE.parent / rel, root / rel)
        r = run(root, tmp)
        if r.returncode or "selftest_ingame_visit_owed: PASS" not in r.stdout:
            print("control RED\n" + r.stdout + r.stderr)
            return 2
        print("control green")
        caught = 0
        for rel, old, new, fail in MUTANTS:
            path = root / rel
            original = path.read_text(encoding="utf-8")
            if original.count(old) != 1:
                print("NOT APPLIED %s in %s" % (fail, rel))
                continue
            path.write_text(original.replace(old, new), encoding="utf-8")
            r = run(root, tmp)
            path.write_text(original, encoding="utf-8")
            modules = "modules: %s %s" % (root / OW, root / MD)
            ok = r.returncode == 1 and modules in r.stdout.splitlines() and any(
                line.startswith("FAIL " + fail) for line in r.stdout.splitlines())
            caught += ok
            print("%s %s" % ("caught:" if ok else "ESCAPED:", fail))
            if not ok:
                print(r.stdout + r.stderr)
        print("mutate_ingame_visit_owed: %d of %d planted faults caught" % (caught, len(MUTANTS)))
        return int(caught != len(MUTANTS))


if __name__ == "__main__":
    sys.exit(main())
