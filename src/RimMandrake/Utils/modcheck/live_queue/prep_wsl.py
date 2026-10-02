"""WSL-side session setup for the northstar live queue (python3, NOT python.exe: modlist_swap/deploy need fcntl).

    python3 src/RimMandrake/Utils/modcheck/live_queue/prep_wsl.py            plan only
    python3 src/RimMandrake/Utils/modcheck/live_queue/prep_wsl.py --apply    MINIMAL + every suite mod, deployed
    python3 src/RimMandrake/Utils/modcheck/live_queue/prep_wsl.py --restore  the owner's full list back

--apply = runner.run()'s own setup half, once for ALL suites, so every job runs in ONE game session:
modlist_swap --minimal --apply (captures FULL first), deploy_custom_mods --mod <M> --apply per suite mod, then
compose every packageId onto the end of activeMods. Refuses while RimWorld is running (ModsConfig names the
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
    pids = {}
    for m in mods:
        pids[m] = runner.mod_package_id(runner.find_mod_dir(m))
    print("suite mods (%d): %s" % (len(mods), ", ".join("%s=%s" % kv for kv in sorted(pids.items()))))
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
    for m in mods:
        r = subprocess.run(["python3", os.path.join(UTILS, "deploy_custom_mods.py"), "--mod", m, "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            print("deploy %s FAILED: %s" % (m, (r.stdout + r.stderr).strip()[-400:]))
            runner.restore_full()
            print("full list restored after the failed deploy")
            return 1
        print("deployed %s" % m)
    added = runner.compose_test_list(list(pids.values()))
    print("composed into ModsConfig: %d added (%d already present)" % (len(added), len(pids) - len(added)))
    print("next: launch through Steam -- powershell.exe -NoProfile -Command \"Start-Process 'steam://rungameid/294100'\"")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
