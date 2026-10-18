"""RAID_DETECTOR_REPAIR_FLOOD_NOT_A_RAID live half: an UNDECLARED jawa/fire_raid (dryRun false) inside a governed
modcheck suite must still surface as a raid_arrived detector hit.  python.exe Transient/bench_live_20261018/raid_detector_live.py"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(REPO, "src", "RimMandrake", "Utils"), os.path.join(REPO, "src", "RimMandrake", "Utils", "modcheck")):
    if p not in sys.path: sys.path.insert(0, p)
from modcheck import Suite
suite = Suite("RaidDetectorLive")
suite.toggles = []
SEEN = []

@suite.chain("real_raid_still_fires_detector")
def real_raid(t):
    with t.component("undeclared_real_raid", shows=[]):
        r = t.bridge_call("jawa/fire_raid", dryRun=False, points=150)
        print("fire_raid ->", json.dumps(r, default=str)[:400], flush=True)
        import watch as W
        try:
            hits = t.watch.check()
            SEEN.append(("no_abort", [(h.detector, h.severity, h.summary) for h in hits]))
        except W.SurpriseAbort as e:
            SEEN.append(("abort", [(h.detector, h.severity, h.summary) for h in e.hits]))
        print("sweep:", json.dumps(SEEN, default=str)[:900], flush=True)

def main():
    import runner
    from rimdrive import Session
    with Session(lock=None) as s:
        runner.ensure_playing_map()
        import helpers as H
        print('pre-clean:', json.dumps(H.kill_hostiles(s), default=str)[:300], flush=True)
        mi = s.call("jawa/map_info") or {}
        anchor = (int(mi.get("sizeX", 250)) // 2 - 12, int(mi.get("sizeZ", 250)) // 2 - 7)
        summ = runner.run_suite(suite, s, anchor=anchor, mod=None, situational=True, policy="abort")
        summ["sweep_seen"] = SEEN
        print("post-clean:", json.dumps(H.kill_hostiles(s), default=str)[:300], flush=True)
    out = os.path.join(HERE, "raid_detector_live_result2.json")
    json.dump(summ, open(out, "w"), indent=1, default=str)
    print("done ->", out)
main()
