#!/usr/bin/env python3
"""joint_check.py -- the JOINT CHECK: every hose/link joint on a live map, measured (HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES).

Owner, 2026-10-22 walkthrough: "I can't even tell what's going on here with the connnectors. Just look at them! Obviously not
even checked before showing us." This is the mechanical half of looking: it must pass before any hose is shown to him (the
REBUILD procedure in the walk notes runs it as a hard step; a FAIL stops the showing).

It asks HoseProbe "joints" (Source/Hose/HoseJointProbe.cs) on each map, which walks every reel and measures, on the pose the
hose is DRAWN with, the distance from each drawn end / fitting face to the point it must meet:
  reel_end            laid hose: coupling face on the measured nozzle tip; drawn strand starts under that coupling + wrap
  free_port_end       a free end coupled to a tank / pipe / pump: coupling face on the port (tank flange, else the shared edge)
  free_on_port        an end lying on a pipe: within half a cell of its centre
  relay_end           a hose feeding a relay reel: drawn end on the relay's drawn inlet
  feed_port_end       a link from a port beside a reel starts in a cell that port really occupies (else: an end at no port)
  feed_nozzle         a link into a stored reel's nozzle meets it, and the reel prints the stored art
  feed_nozzle_shared  a LAID reel whose port stands in front of its nozzle (two hoses from one nozzle) -- a FAIL: turn it
  feed_under_reel     a link that runs in under the reel to its centre (PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE): passes
  pose                a laid hose never drawn (off screen): UNMEASURED, never a pass
Tolerance: HoseJoints.Tolerance (0.05 cell, ~6 px at the closest zoom), reported by the probe itself.

    python.exe src/RimMandrake/FlowWorks/northstar/joint_check.py                 # current map
    python.exe src/RimMandrake/FlowWorks/northstar/joint_check.py --all-maps      # every map (walkthrough: C and R)
    python.exe src/RimMandrake/FlowWorks/northstar/joint_check.py --out FILE.json
Exit 0 = every joint within tolerance and nothing unmeasured; 1 = a gap, a non-port end or a shared nozzle; 2 = UNMEASURED
(probe missing, bridge down, or a laid hose with no drawn pose: pan the camera over it and run again). Read-only.
The offline halves: HoseJointChecks (C# SelfTest, port geometry) and validation_hose_offline.py HO9 (art vs the constants).
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
HP = "RimMandrake.FlowWorks.Hose.HoseProbe"


def judge(answer):
    """Pure: a probe answer (dict) -> (verdict, lines). verdict PASS | FAIL | UNMEASURED."""
    if not isinstance(answer, dict) or not answer.get("success"):
        return "UNMEASURED", ["probe did not answer: %s" % str(answer)[:200]]
    joints = answer.get("joints") or []
    tol = answer.get("tolerance")
    bad = [j for j in joints if j.get("ok") is False]
    unm = [j for j in joints if j.get("ok") is None]
    lines = ["%d joints on %d reels, tolerance %s cell: %d gap(s), %d unmeasured"
             % (len(joints), answer.get("reels", 0), tol, len(bad), len(unm))]
    for j in bad + unm:
        lines.append("  %-4s reel %s at %s rot %s %-18s gap %.3f at %s -- %s"
                     % ("FAIL" if j.get("ok") is False else "UNM", j.get("reel"), j.get("at"), j.get("rot"), j.get("kind"),
                        float(j.get("gap") or 0), j.get("where"), j.get("note")))
    if answer.get("reels", 0) and not joints:
        return "UNMEASURED", lines + ["reels but no joints measured: the probe saw nothing"]
    if bad:
        return "FAIL", lines
    if unm:
        return "UNMEASURED", lines
    return "PASS", lines


def _bridge():
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
    from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
    h, p, t = resolve_endpoint()
    return RimBridge(h, p, t)


def _probe(B, cmd, wait=30.0):
    def call(n, **kw):
        try:
            return B.call(n, kw) or {}
        except Exception as e:  # noqa: BLE001
            return {"success": False, "error": str(e)[:300]}
    before = call("jawa/mod_settings_field", typeName=HP, action="get", field="serial").get("value")
    call("jawa/mod_settings_field", typeName=HP, action="set", field="request", value=cmd)
    t0 = time.time()
    while time.time() - t0 < wait:
        if call("jawa/mod_settings_field", typeName=HP, action="get", field="serial").get("value") != before:
            raw = call("jawa/mod_settings_field", typeName=HP, action="get", field="result").get("value")
            try:
                return json.loads(str(raw))
            except ValueError:
                return {"success": False, "error": "unparsable probe answer: %s" % str(raw)[:200]}
        time.sleep(0.25)
    return {"success": False, "error": "probe timeout (is the game unpaused enough to tick, and FlowWorks deployed?)"}


def main(argv):
    all_maps = "--all-maps" in argv
    out = argv[argv.index("--out") + 1] if "--out" in argv else None
    results, worst = [], "PASS"
    rank = {"PASS": 0, "UNMEASURED": 1, "FAIL": 2}
    with _bridge() as B:
        maps = [None]
        if all_maps:
            info = B.call("rimworld/get_game_info", {}) or {}
            ids = [m.get("id", m.get("uniqueID")) for m in (info.get("maps") or []) if isinstance(m, dict)]
            maps = [i for i in ids if i is not None] or [None]
            cur = (B.call("rimworld/get_camera_state", {}) or {}).get("mapId")
        for mid in maps:
            if mid is not None:
                B.call("jawa/set_current_map", {"mapId": int(mid)})
                time.sleep(1.0)
            ans = _probe(B, "joints")
            verdict, lines = judge(ans)
            print("map %s: %s" % ("current" if mid is None else mid, verdict))
            for ln in lines:
                print(ln)
            results.append({"map": mid, "verdict": verdict, "answer": ans})
            worst = max(worst, verdict, key=lambda v: rank[v])
        if all_maps and cur is not None:
            B.call("jawa/set_current_map", {"mapId": int(cur)})
    print("JOINT CHECK: %s" % worst)
    if out:
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"verdict": worst, "maps": results}, f, indent=1)
    return {"PASS": 0, "FAIL": 1, "UNMEASURED": 2}[worst]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
