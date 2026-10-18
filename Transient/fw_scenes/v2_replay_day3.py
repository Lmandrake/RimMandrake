"""Ran against validation_v2 at e23ef031a (the day-3 harness; level_water with pond_key). Replay day 3's flow rows offline: the mock game runs EXACT-level water (shipped levelExactEnabled) over ponds with the
P11 floor (0.5 m shore shelf on the outer ring, painted WaterShallow 1 m inside), the harness's oracle unchanged.
If the mock's flow rows read like the live day-3 rows, the flow FAILs are the stale oracle + the site's floors."""
import json
import os
import sys

NS = "/home/mandrake/rm/scratch/FOUNDRY/v2triage/src/RimMandrake/FlowWorks/northstar"
sys.path.insert(0, NS)
import validation_v2 as V  # noqa: E402
import level_water as LW  # noqa: E402

SHELF = "--no-shelf" not in sys.argv
EXACT_HARNESS = "--exact-harness" in sys.argv


class Day3Game(V.MockBridge):
    def __init__(self, faults=()):
        V.MockBridge.__init__(self, faults)
        self.o = V.PulseOracle(V.MAP_W, V.MAP_H, {}, {}, sink_band=V.SINK_BAND, algo="fixed", recession=True,
                               level_exact=True, **V.CREEP_LIVE)

    def classify(self, c):
        if c in self.classified:
            return self.classified[c]
        name = V.MockBridge.classify(self, c)
        if name is None:
            return None
        b = self.o.bodies[name]
        cells = set(b["cells"])
        beds = {}
        for x in cells:
            ring = any((x[0] + dx, x[1] + dz) not in cells for dx in (-1, 0, 1) for dz in (-1, 0, 1))
            beds[x] = 1 if (SHELF and ring) else 2
        self.o.beds.update(beds)
        if not b["limitless"]:
            cap = float(sum(beds.values()))
            b["capacity"] = cap
            b["stock"] = cap
        return name

    def do_pulse(self):
        self.sync()
        d0 = self.o.drained
        self.o.pulse()
        self.sink_total += (self.o.drained - d0) / float(LW.U)


class A(object):
    mock, fresh_map, reset_settings, progress, max_job_ticks = True, False, False, None, 6000
    fault = []


so = sys.stdout
sys.stdout = open(os.devnull, "w")
try:
    res = V.run_live(A, B=Day3Game())
finally:
    sys.stdout = so
day3 = {r["id"]: r for r in json.load(open(os.path.join(NS, "validation_v2_result_20261017T180214.json")))["rows"]}
print("mock(exact%s) summary %s" % (" + shelf" if SHELF else "", res["summary"]))
for r in res["rows"]:
    d = day3.get(r["id"], {})
    if r["status"] != "PASS" or d.get("status") != "PASS":
        print("%-34s mock %-10s day3 %-10s | %s" % (r["id"], r["status"], d.get("status"), r["detail"][:150]))
