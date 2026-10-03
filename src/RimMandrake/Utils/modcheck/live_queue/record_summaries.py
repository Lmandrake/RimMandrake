"""WSL-side recorder for situational_rerun summaries.

    python3 src/RimMandrake/Utils/modcheck/live_queue/record_summaries.py Mod1 Mod2 ...   (or --all)

situational_rerun runs under python.exe, which CANNOT write infrastructure/state/modcheck_status.json from the WSL
path (PermissionError, LIVE 2026-10-03: "RECORDING FAILED" for all four mods), so its per-mod status_recording note
reads failed and nothing lands. The per-mod <Mod>_summary.json it wrote is complete; this records them from WSL with the
same record_summary() call. It records a RED honestly (never invents a PASS).
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))
import situational_rerun as sr   # noqa: E402
from common import ROOT           # noqa: E402

D = os.path.join(ROOT, "Transient", "modcheck", "live_queue", "situational_rerun")


def main(argv):
    mods = [a for a in argv if not a.startswith("--")]
    if "--all" in argv:
        mods = sorted(f[:-len("_summary.json")] for f in os.listdir(D) if f.endswith("_summary.json"))
    if not mods:
        print(__doc__)
        return 2
    for m in mods:
        p = os.path.join(D, m + "_summary.json")
        if not os.path.isfile(p):
            print("%-24s no summary at %s" % (m, p))
            continue
        with open(p, encoding="utf-8") as f:
            summ = json.load(f)
        print("%-24s %s" % (m, sr.record_summary(m, summ, p, False)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
