import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils"); sys.path.insert(0, "src/RimMandrake/Utils/modcheck")
from rimdrive.session import Session
import runner
mod = sys.argv[1]; policy = sys.argv[2] if len(sys.argv) > 2 else "abort"
suite = runner.load_validation(runner.find_mod_dir(mod))
t0 = time.time()
with Session(strict=False, quiet=True, focus=False) as s:
    out = runner.run_suite(suite, s, situational=True, policy=policy)
print("elapsed %.1fs  all_green=%s" % (time.time()-t0, out["all_green"]))
for ch in out["chains"]:
    print("CHAIN", ch["name"], "|", {k: ch["situational"][k] for k in ("bland","sweeps","ticks_spent","policy")}, "| problems:", ch["situational"]["bland_problems"])
    for c in ch["components"]:
        print("   ", c["verdict"], "|", c["name"], "|", (c["detail"] or "")[:260])
    for sp in ch["situational"]["surprises"]:
        print("    SURPRISE evidence:", sp["sidecar"], sp["png"])
    seen = [h for h in ch["situational"]["hits_seen"]]
    print("    hits seen:", sorted(set((h["detector"], h["severity"]) for h in seen)))
json.dump(out, open("Transient/northstar_probe/pilot_%s_%s.json" % (mod, policy), "w"), indent=1, default=str)
