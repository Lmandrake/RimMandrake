"""Run ONLY the DivingInteraction suite's Grey floor chains live, on the list already loaded (no mod-list swap).

    python.exe src/RimMandrake/DivingInteraction/northstar/run_grey_floor_live.py   (from the repo root, bridge held)

modcheck.run would swap ModsConfig to MINIMAL; this calls runner.run_suite directly, the way the Pits pilot ran.
Writes src/RimMandrake/DivingInteraction/northstar/grey_floor_live_<ts>.json."""
import json, os, sys, time
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the mod folder
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
sys.path.insert(0, os.path.join(HERE, "..", "Utils", "modcheck"))
import runner  # noqa: E402

CHAINS = ("per_sea_floor_biomes", "seabed_floor_generators", "seabed_floor_ambient_carryover", "grey_floor_is_a_place")

suite = runner.load_validation(HERE)
suite.chains = [(n, f) for n, f in suite.chains if n in CHAINS]
print("chains:", [n for n, _ in suite.chains], "| map:", runner.ensure_playing_map())
from rimdrive import Session  # noqa: E402
with Session(lock=None) as s:
    summary = runner.run_suite(suite, s, mod="DivingInteraction")
out = os.path.join(HERE, "northstar", "grey_floor_live_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(summary, open(out, "w"), indent=1, default=str)
for ch in summary.get("chains", []):
    for c in ch.get("components", []):
        print("%-10s %s/%s  %s" % (c.get("verdict"), ch.get("name"), c.get("name"), (c.get("detail") or "")[:160]))
print("all_green:", summary.get("all_green"), "->", out)
