"""Run a mod's modcheck validation suite against the ALREADY-RUNNING game: no ModsConfig swap, no deploy, no restore.
Usage (Windows python.exe, repo root): python.exe Transient/acc_biomes/run_live_suite.py <ModFolder> [--debug]
Mirrors modcheck.runner.run() minus swap_to_test_list/compose_test_list/restore_full/emit_verify/record_run."""
import sys, os, json
sys.path.insert(0, r"src\RimMandrake\Utils"); sys.path.insert(0, r"src\RimMandrake\Utils\modcheck")
import runner
mod = sys.argv[1]; dbg = "--debug" in sys.argv
mod_dir = runner.find_mod_dir(mod)
suite = runner.load_validation(mod_dir)
for a in sys.argv:
    if a.startswith("--chains="):
        keep = set(a.split("=",1)[1].split(","))
        suite.chains = [(n, f) for (n, f) in suite.chains if n in keep]
        print("chains:", [n for n, _ in suite.chains])
print("ensure_playing_map:", runner.ensure_playing_map())
from rimdrive import Session
with Session(lock=None) as s:
    if "--reset-settings" in sys.argv:
        G = suite.chains[0][1].__globals__
        for cls, fields in (G.get("SETTINGS") or {}).items():
            for f, v in fields.items():
                r = s.call("jawa/mod_settings_field", typeName=cls, action="set", field=f, value=str(v))
                if not (r or {}).get("success"): print("RESET FAIL", cls, f, str(r)[:120])
        print("settings reset to shipped defaults")
    summary = runner.run_suite(suite, s, debug=dbg, mod=mod)
sheet = runner.write_sheet(mod, summary)
print("SHEET", sheet)
for c in summary.get("chains", []):
    comps = c.get("components") or []
    print("CHAIN", c.get("name"), c.get("verdict") or c.get("status"), json.dumps({k: c[k] for k in c if k not in ("components",)}, default=str)[:200])
    for k in comps:
        print("   ", json.dumps(k, default=str)[:260])
print("ALL_GREEN", summary.get("all_green"), "FINDINGS", len(summary.get("findings", [])))
