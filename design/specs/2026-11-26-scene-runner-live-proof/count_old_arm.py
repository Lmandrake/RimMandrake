"""Run knockback_runner.py with every RimBridge.call counted by tool; print the counts and wall time at exit.
usage: python.exe count_old_arm.py <repo> <out.json> -- <knockback_runner args>"""
import atexit, json, os, sys, time
repo, out = sys.argv[1], sys.argv[2]
args = sys.argv[sys.argv.index("--") + 1:]
sys.path.insert(0, os.path.join(repo, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(repo, "src", "RimMandrake", "ExplosiveKnockback"))
import rimbridge_client as RC
calls = {}
orig = RC.RimBridge.call
def counted(self, tool, *a, **k):
    calls[tool] = calls.get(tool, 0) + 1
    return orig(self, tool, *a, **k)
RC.RimBridge.call = counted
t0 = time.time()
def done():
    rec = {"bridge_calls": dict(calls, total=sum(calls.values())), "wall_s": round(time.time() - t0, 2)}
    print("OLD ARM time: total %s s; bridge calls %s" % (rec["wall_s"], rec["bridge_calls"]))
    with open(out, "w") as f: json.dump(rec, f, indent=1)
atexit.register(done)
sys.argv = ["knockback_runner.py"] + args
import knockback_runner
sys.exit(knockback_runner.main())
