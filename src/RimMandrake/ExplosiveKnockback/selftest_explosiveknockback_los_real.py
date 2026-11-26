#!/usr/bin/env python3
"""The situation map's sight lines, witnessed by the game's own code (RIMMANDRAKE_REPLAY_ENUMERATED_SITUATIONS_IN_HEADLESS_REAL_GAME).

The map (Source/SelfTest/KnockbackMap.cs) reaches things by assumption A5: a hand copy of Verse.GenSight.LineOfSight
(start, end, map, skipFirstCell: true). This check builds the map with Source/SelfTest/LosReal/, which links the game's
Assembly-CSharp, and asks the real GenSight.LineOfSight on a hand-built Map shell (walls, closed doors) of every sight line the
map asks: the enumerated lanes, the spared cases, the seeded rooms, the fixed cases and the settings flips.

  1. the witness calibrates: a wall and a closed door block the real line, open ground does not;
  2. the whole map runs with the witness: every bar holds and 0 of its sight lines differ (exit 1 otherwise, with examples);
  3. a dense sweep (2000 seeded layouts of walls and closed doors, every line within a blast radius) diffs the copy itself;
  4. two planted faults in the staged copy (the tie rule dropped, a closed door left out) must each be counted by the sweep:
     a witness that stays at 0 over a broken copy is blind.

Needs Windows dotnet and a RimWorld install's Managed folder (RIMWORLD_MANAGED, else the known installs). Without them it prints
UNMEASURED and exits 1.

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_los_real.py
"""
# selftest-timeout: 1500
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from winbuild import run_interop_captured, win  # noqa: E402  (WSL lost-launch retry and paths)
import fcntl
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_explosiveknockback_map as M  # noqa: E402  (its staging of the map: carrier probes, fresh mtimes)

M.STAGE = os.path.join(M.STAGE_ROOT, "ExplosiveKnockbackLosRealSelfTest")
LOSREAL = ("LosRealWitness.cs", "RimMandrakeExplosiveKnockback.LosReal.csproj")
MANAGED = [os.environ.get("RIMWORLD_MANAGED", ""),
           "/mnt/d/SteamLibrary/steamapps/common/RimWorld/RimWorldWin64_Data/Managed",
           "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/RimWorldWin64_Data/Managed"]
# each breaks the copied line one way; the sweep must count differences on each. (Over the map's own situations alone, the tie
# rule dropped changes 2 of ~1e6 lines and the door left out 14: the map seldom puts either on a sight line.)
FAULTS = [
    ("the line's tie rule dropped", "if (err > 0 || err == 0 && flag) { px += sx; err -= dz; }", "if (err > 0) { px += sx; err -= dz; }"),
    ("a closed door left out of the line", "(w.terr[px, pz] == KbCell.Wall || w.terr[px, pz] == KbCell.Door)) return false;",
     "w.terr[px, pz] == KbCell.Wall) return false;"),
]
SWEEP = re.compile(r"LOS SWEEP: (\d+) of (\d+) sight lines differ")
WITNESS = re.compile(r"LOS WITNESS: (\d+) of (\d+) sight lines differ")


def stage(fault=None):
    M.stage()
    dest = os.path.join(M.STAGE, "SelfTest", "LosReal")
    os.makedirs(dest, exist_ok=True)
    for f in LOSREAL:
        shutil.copy(os.path.join(HERE, "Source", "SelfTest", "LosReal", f), os.path.join(dest, f))
    if not fault:
        return True
    p = os.path.join(M.STAGE, "SelfTest", "KnockbackMap.cs")
    text = open(p, encoding="utf-8").read()
    if fault[1] not in text:
        return False
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text.replace(fault[1], fault[2], 1))
    return True


def run(dotnet, managed, extra):
    proj = os.path.join(M.STAGE, "SelfTest", "LosReal", "RimMandrakeExplosiveKnockback.LosReal.csproj")
    r = run_interop_captured([dotnet, "run", "--project", win(proj), "-c", "Release", "-p:RimWorldManaged=" + win(managed), "--"]
                             + list(extra), capture_output=True, text=True, stdin=subprocess.DEVNULL)
    return r.returncode, (r.stdout or "").replace("\r", "") + (r.stderr or "")


def counted(pattern, out):
    m = pattern.search(out)
    return (int(m.group(1)), int(m.group(2))) if m else None


def main(argv):
    dotnet = next((d for d in M.DOTNET if os.path.isfile(d)), None)
    managed = next((d for d in MANAGED if d and os.path.isfile(os.path.join(d, "Assembly-CSharp.dll"))), None)
    if dotnet is None or managed is None or not os.path.isdir(os.path.dirname(M.STAGE)):
        print("UNMEASURED: no Windows dotnet.exe, RimWorld Managed folder or staging root on this machine")
        return 1
    with open(M.STAGE + ".lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        for d in ("obj", "bin"):
            shutil.rmtree(os.path.join(M.STAGE, "SelfTest", "LosReal", d), ignore_errors=True)
        stage()
        rc, out = run(dotnet, managed, ["--map"])
        keep = [l for l in out.splitlines() if l.startswith(("LOS ", "KNOCKBACK MAP", "BREAKS", "knockback map", "    e.g. "))]
        print("\n".join(keep))
        got, swept = counted(WITNESS, out), counted(SWEEP, out)
        if "CALIBRATED" not in out or got is None or swept is None:
            print(out[-3000:])
            print("explosive knockback los real: FAIL (the witness did not calibrate or did not report)")
            return 1
        if rc != 0 or got[0] or swept[0] or not got[1] or not swept[1] or "every bar holds" not in out:
            print("explosive knockback los real: FAIL (map %d of %d, sweep %d of %d sight lines differ from the game's; rc %d)"
                  % (got + swept + (rc,)))
            return 1
        missed = []
        for fault in FAULTS:
            if not stage(fault):
                print("FAIL planted fault '%s' could not be planted (its line is gone from KnockbackMap.cs)" % fault[0])
                missed.append(fault[0])
                continue
            frc, fout = run(dotnet, managed, ["--map", "--map-rooms", "300"])
            fswept = counted(SWEEP, fout)
            if frc == 0 or fswept is None or not fswept[0]:
                print("FAIL planted fault NOT SEEN by the witness: %s (sweep %s)" % (fault[0], fswept))
                missed.append(fault[0])
            else:
                print("seen  %-36s sweep %d of %d sight lines differ" % ((fault[0],) + fswept))
        stage()
        if missed:
            print("explosive knockback los real: FAIL (%d of %d planted faults not seen)" % (len(missed), len(FAULTS)))
            return 1
    print("explosive knockback los real: PASS (map %d and sweep %d sight lines asked of Verse.GenSight.LineOfSight, 0 differ; %d of %d planted faults seen)"
          % (got[1], swept[1], len(FAULTS), len(FAULTS)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
