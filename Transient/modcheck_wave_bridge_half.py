"""Bridge half of MODCHECK_MATURE_WAVE_1 — runs under python.exe ONLY.
Loads each suite, drives it over one Session per mod, dumps a JSON summary
per mod to Transient/modcheck/<Mod>_summary.json. No modlist writes, no
rimflow, no sheets — the WSL half owns those."""
import sys, json, os, time
sys.path.insert(0, "src/RimMandrake/Utils/modcheck")
sys.path.insert(0, "src/RimMandrake/Utils")
import runner
from rimdrive import Session

MODS = sys.argv[1:]
os.makedirs(os.path.join("Transient", "modcheck"), exist_ok=True)
overall = []
for m in MODS:
    t0 = time.time()
    try:
        mod_dir = runner.find_mod_dir(m)
        suite = runner.load_validation(mod_dir)
        with Session(lock=None) as s:
            summary = runner.run_suite(suite, s, debug=False)
        summary["modDir"] = mod_dir
        summary["wallSeconds"] = round(time.time() - t0, 1)
        # findings hold Component objects; flatten to names for JSON
        summary["findings"] = [getattr(c, "name", str(c)) for c in summary.get("findings") or []]
        out = os.path.join("Transient", "modcheck", "%s_summary.json" % m)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=1, default=str)
        n = sum(len(c["components"]) for c in summary["chains"])
        npass = sum(1 for c in summary["chains"] for comp in c["components"]
                    if str(comp.get("verdict", "")).startswith("PASS"))
        line = "%-22s %s  %d/%d pass  %d findings  %.0fs" % (
            m, "GREEN" if summary["all_green"] else "RED", npass, n,
            len(summary["findings"]), summary["wallSeconds"])
        print(line, flush=True)
        overall.append(line)
    except Exception as e:
        print("%-22s LOAD/RUN ERROR: %r" % (m, e), flush=True)
        overall.append("%s ERROR %r" % (m, e))
print("\n==== BRIDGE HALF DONE: %d mods ====" % len(MODS))
