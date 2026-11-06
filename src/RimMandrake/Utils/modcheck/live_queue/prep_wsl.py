"""WSL-side session setup for the northstar live queue (python3, NOT python.exe: modlist_swap/deploy need fcntl).

    python3 src/RimMandrake/Utils/modcheck/live_queue/prep_wsl.py            plan only
    python3 src/RimMandrake/Utils/modcheck/live_queue/prep_wsl.py --apply    MINIMAL + every suite mod, deployed
    python3 src/RimMandrake/Utils/modcheck/live_queue/prep_wsl.py --restore  the owner's full list back

--apply = runner.run()'s own setup half, once for ALL suites, so every job runs in ONE game session:
modlist_swap --minimal --apply (captures FULL first), deploy_custom_mods with each suite's suite_set.deploy_plans,
then compose every suite's suite_set.closure (dependencies first, through our own mods) onto the end of activeMods. The suites
are suite_set.py's disk-derived set. Refuses while RimWorld is running (ModsConfig names the
NEXT load, and a deploy cannot overwrite a loaded DLL). The game is launched afterwards, through Steam.
"""
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from common import ROOT, UTILS   # noqa: E402


def game_running():
    try:
        out = subprocess.run(["tasklist.exe", "/FI", "IMAGENAME eq RimWorldWin64.exe"], capture_output=True,
                             text=True, timeout=20).stdout
    except Exception:                                           # noqa: BLE001
        return None
    return "RimWorldWin64.exe" in out


def main(argv):
    import runner
    from jobs import suite_mods
    apply_, restore = "--apply" in argv, "--restore" in argv
    mods = suite_mods()
    if restore:
        runner.restore_full()
        print("restored the full mod list (modlist_swap --restore --apply)")
        return 0
    import suite_set
    pids, plans = [], {}
    for m in mods:      # deps first (through our own mods), the mod (its composed mod's id when folded), its tier closure
        try:
            pids.extend(p for p in suite_set.closure(m) if p not in pids)
            plans[m] = suite_set.deploy_plans(m)
        except Exception as e:                                  # noqa: BLE001
            print("REFUSED: %s has no readable closure (%s: %s); nothing swapped or deployed" % (m, type(e).__name__, e))
            return 1
    print("suite mods (%d), %d packageIds composed: %s" % (len(mods), len(pids), ", ".join(mods)))
    if not apply_:
        print("plan only; --apply swaps to MINIMAL, deploys these, composes them into ModsConfig")
        return 0
    running = game_running()
    if running is None:
        print("REFUSED: cannot ask tasklist.exe whether RimWorld is running")
        return 2
    if running:
        print("REFUSED: RimWorld is running; quit it first (the deploy and ModsConfig both need it down)")
        return 2
    runner.swap_to_test_list()
    done = set()
    for m in mods:      # each suite's transitive deploy closure (suite_set.deploy_plans), every argv deployed once
        for argv in plans[m]:
            if tuple(argv) in done:
                continue
            done.add(tuple(argv))
            r = subprocess.run(["python3", os.path.join(UTILS, "deploy_custom_mods.py")] + argv + ["--apply"],
                               cwd=ROOT, capture_output=True, text=True)
            if r.returncode != 0:
                print("deploy %s (%s) FAILED: %s" % (m, " ".join(argv), (r.stdout + r.stderr).strip()[-400:]))
                runner.restore_full()
                print("full list restored after the failed deploy")
                return 1
        print("deployed %s" % m)
    added = runner.compose_test_list(pids)
    print("composed into ModsConfig: %d added (%d already present)" % (len(added), len(pids) - len(added)))
    print("next: launch through Steam -- powershell.exe -NoProfile -Command \"Start-Process 'steam://rungameid/294100'\"")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
