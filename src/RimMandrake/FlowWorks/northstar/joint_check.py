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
JOINT_CHECK_WIDEN_PIPE_STUBS_UNSEEN (2026-10-22) adds two kinds measured here in Python from the bridge (no new C#):
  pipe_stub           every rigid pipe END (a pipe cell with at most one pipe beside it, N/E/S/W) must meet a port: a pipe
                      pole or a hose reel beside it, a hose's free end on or beside it, or a tank / liquid machine on or
                      8-way around it (the net's attach rule; HoseProbe "net:x,z" reads the live role, so modded machines
                      count). An end at none of these is a stub drawn into nothing: FAIL. A role read that never answered:
                      UNMEASURED.
  hose_crossing       two laid hoses whose centre lines (census centreCells) share a cell: a flat hose-over-hose crossing
                      (audit D11, no lift or shadow yet): FAIL. A relay pair is exempt within one cell of the relay reel.
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
    own = answer.get("joints") or []
    joints = own + list(answer.get("extra") or [])      # extra: pipe_stub / hose_crossing (extra_joints)
    tol = answer.get("tolerance")
    bad = [j for j in joints if j.get("ok") is False]
    unm = [j for j in joints if j.get("ok") is None]
    lines = ["%d joints on %d reels, tolerance %s cell: %d gap(s), %d unmeasured"
             % (len(joints), answer.get("reels", 0), tol, len(bad), len(unm))]
    for j in bad + unm:
        lines.append("  %-4s reel %s at %s rot %s %-18s gap %.3f at %s -- %s"
                     % ("FAIL" if j.get("ok") is False else "UNM", j.get("reel"), j.get("at"), j.get("rot"), j.get("kind"),
                        float(j.get("gap") or 0), j.get("where"), j.get("note")))
    if answer.get("reels", 0) and not own:
        return "UNMEASURED", lines + ["reels but no joints measured: the probe saw nothing"]
    if bad:
        return "FAIL", lines
    if unm:
        return "UNMEASURED", lines
    return "PASS", lines


PIPE_DEF_PREFIX, POLE_DEF_PREFIX = "RM_UniversalPipe", "RM_PipePole"
# Ports the net probe cannot see (JOINT_CHECK_FIX_TAPS_LOOK_LIKE_NOTHING, 2026-10-23): HoseProbe "net:x,z" takes the FIRST thing
# with a hydraulic role, so a sprinkler head standing ON a pipe cell answers as the pipe. Found by def (variants
# RM_SprinklerHead_Scrapper... share the prefix):
#   Sprinklers.CompRM_SprinklerBase  RM_SprinklerHead*      pipe-fed faucet  RM_PipeFaucet (Defs/Sprinklers/RM_PipeFaucet.xml)
# NOT ports: RM_LiquidTap (bleed well) and RM_LiquidDrill (Building_LiquidDrill) are OFF the pipe net -- they join no pipe at any
# adjacency, their only output is the dug-channel cell they face (delegated design ruling 2026-10-23, bleed_well_port.json).
# A pipe end beside one is a real stub.
PORT_DEF_PREFIXES = ("RM_SprinklerHead", "RM_PipeFaucet")
# Stubs known and kept on purpose: absolute cell -> why. They stay FAIL (ok False); the note says so.
KNOWN_STUBS = {(25, 130): "known FAIL: C7 pipe west end staged for the future faucet (PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE)"}
ORTHO = ((1, 0), (-1, 0), (0, 1), (0, -1))
RING8 = ORTHO + ((1, 1), (1, -1), (-1, 1), (-1, -1))


def _joint(kind, at, ok, where, note, reel=None):
    return {"reel": reel, "at": list(at), "rot": None, "look": None, "kind": kind, "ok": ok, "gap": 0.0, "where": where,
            "note": note}


def pipe_ends(pipes):
    """Pure: pipe cells with at most one pipe on an edge-neighbour (a lone pipe is one end)."""
    ps = set(map(tuple, pipes))
    return sorted(c for c in ps if sum((c[0] + dx, c[1] + dz) in ps for dx, dz in ORTHO) <= 1)


def _fp_cells(fp):
    x, z, w, h = fp
    return {(x + i, z + j) for i in range(w) for j in range(h)}


def stub_joints(pipes, poles, reel_fps, hose_ends, is_partner, port_cells=()):
    """Pure (is_partner injected): one pipe_stub joint per pipe end. is_partner(cell) -> True (a tank / liquid machine is
    there), False (nothing with a net role), None (the read did not answer). port_cells: cells of sprinkler heads / faucets (PORT_DEF_PREFIXES), on the end or 8-way around it, pipe cells included (a head stands on its pipe)."""
    pc = set(map(tuple, port_cells))
    ps, pl = set(map(tuple, pipes)), set(map(tuple, poles))
    reel_cells = set()
    for fp in reel_fps:
        reel_cells |= _fp_cells(fp)
    ends_h = set(map(tuple, hose_ends))
    out = []
    for e in pipe_ends(ps):
        edge = [(e[0] + dx, e[1] + dz) for dx, dz in ORTHO]
        if any(n in pl for n in edge):
            out.append(_joint("pipe_stub", e, True, "pipe pole", "pipe end meets a pipe pole"))
            continue
        if any(n in reel_cells for n in edge):
            out.append(_joint("pipe_stub", e, True, "hose reel", "pipe end meets a hose reel"))
            continue
        if e in ends_h or any(n in ends_h for n in edge):
            out.append(_joint("pipe_stub", e, True, "hose end", "pipe end meets a hose's free end"))
            continue
        near = [c for c in [e] + [(e[0] + dx, e[1] + dz) for dx, dz in RING8] if c in pc]
        if near:
            out.append(_joint("pipe_stub", e, True, "%d,%d" % near[0], "pipe end meets a sprinkler head / faucet"))
            continue
        seen = None
        for c in [e] + [(e[0] + dx, e[1] + dz) for dx, dz in RING8]:
            if c != e and c in ps:
                continue
            r = is_partner(c)
            if r:
                seen = c
                break
            if r is None:
                seen = seen or "unread"
        if isinstance(seen, tuple):
            out.append(_joint("pipe_stub", e, True, "%d,%d" % seen, "pipe end meets a tank / liquid machine"))
        elif seen == "unread":
            out.append(_joint("pipe_stub", e, None, "-", "the role read of a neighbour never answered"))
        else:
            out.append(_joint("pipe_stub", e, False, "-", KNOWN_STUBS.get(e, "pipe end at no port: a stub drawn into nothing")))
    return out


def _line_cells(h):
    """The cells a laid hose is DRAWN through: poseCells when the probe has them (CENTRE_CELLS_FIX_WALK_THROUGH_WALLS: the
    plan's centreCells crossed a wall the drawn pose went round), else the plan's centreCells of an older probe."""
    return h.get("poseCells") or h.get("centreCells")


def crossing_joints(hoses):
    """Pure: one hose_crossing joint per pair of laid hoses whose centre lines share a cell (relay pairs exempt within one
    cell of the relay reel's footprint)."""
    laid = [dict(h, centreCells=_line_cells(h)) for h in hoses or [] if h.get("laid") and _line_cells(h)]
    owner = {}
    for h in laid:
        for c in set(tuple(c) for c in h["centreCells"]):
            owner.setdefault(c, []).append(h)
    pairs = {}
    for c, hs in sorted(owner.items()):
        for i in range(len(hs)):
            for k in range(i + 1, len(hs)):
                a, b = hs[i], hs[k]
                relay = None
                if a.get("relayTo") and list(a["relayTo"]) == list(b.get("reel") or []):
                    relay = b
                elif b.get("relayTo") and list(b["relayTo"]) == list(a.get("reel") or []):
                    relay = a
                if relay is not None and relay.get("footprint"):
                    x, z, w, hh = relay["footprint"]
                    if x - 1 <= c[0] <= x + w and z - 1 <= c[1] <= z + hh:
                        continue
                pairs.setdefault((a.get("id"), b.get("id")), []).append(c)
    return [_joint("hose_crossing", cells[0], False, "%d cell(s)" % len(cells),
                   "laid hoses %s and %s cross flat (D11: no lift or shadow)" % ids, reel=list(ids))
            for ids, cells in sorted(pairs.items(), key=lambda kv: str(kv[0]))]


def _defs_with(prefixes):
    import glob
    import re
    names = set()
    for path in glob.glob(os.path.join(HERE, "..", "Defs", "**", "*.xml"), recursive=True):
        with open(path, encoding="utf-8", errors="replace") as f:
            names.update(re.findall(r"<defName>((?:%s)\w*)</defName>" % "|".join(prefixes), f.read()))
    return sorted(names)


def _pipe_defs():
    return _defs_with((PIPE_DEF_PREFIX, POLE_DEF_PREFIX))


def extra_joints(B, probe):
    """Live: the pipe_stub and hose_crossing joints of the current map (probe = lambda cmd: answer dict)."""
    census = probe("census")
    if not isinstance(census, dict) or not census.get("success"):
        return [_joint("pipe_stub", (0, 0), None, "-", "census unreadable: %s" % str(census)[:120])]
    hoses = census.get("hoses") or []
    defs = _pipe_defs()
    lt = B.call("jawa/list_things", {"defName": ",".join(defs), "limit": 20000}) or {}
    if not defs or not lt.get("success") or lt.get("countMatched", 0) > len(lt.get("things") or []):
        return [_joint("pipe_stub", (0, 0), None, "-", "pipe list unreadable or truncated: %s" % str(lt)[:120])] \
            + crossing_joints(hoses)
    pipes = [(t["x"], t["z"]) for t in lt.get("things") or [] if t.get("def", "").startswith(PIPE_DEF_PREFIX)]
    poles = [(t["x"], t["z"]) for t in lt.get("things") or [] if t.get("def", "").startswith(POLE_DEF_PREFIX)]
    fps = [h["footprint"] for h in hoses if h.get("footprint")]
    ends = [tuple(h["far"]) for h in hoses if h.get("laid") and h.get("far")]
    pipe_names = set(defs)
    pdefs = [d for d in _defs_with(PORT_DEF_PREFIXES) if not d.startswith("RM_Mote")]
    pl2 = B.call("jawa/list_things", {"defName": ",".join(pdefs), "limit": 20000}) or {}
    if not pl2.get("success") or pl2.get("countMatched", 0) > len(pl2.get("things") or []):
        return [_joint("pipe_stub", (0, 0), None, "-", "tap / sprinkler list unreadable or truncated: %s" % str(pl2)[:120])] \
            + crossing_joints(hoses)
    ports = [(t["x"], t["z"]) for t in pl2.get("things") or []]

    def is_partner(c):
        a = probe("net:%d,%d" % c)
        if not isinstance(a, dict) or ("success" not in a):
            return None
        if not a.get("success"):
            return None if "timeout" in str(a.get("error", "")) or "unparsable" in str(a.get("error", "")) else False
        return a.get("origin") not in pipe_names
    return stub_joints(pipes, poles, fps, ends, is_partner, ports) + crossing_joints(hoses)


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
        maps, cur = [None], None
        if all_maps:
            # rimworld/get_game_info carries no map list (only mapCount) and the camera's mapId is "Map_0", not an int
            # (2026-10-22 live: --all-maps silently read the current map only). jawa/set_current_map refuses an unknown
            # id WITHOUT switching and lists loadedMaps in the refusal (river_site.loaded_maps); jawa/map_info gives cur.
            r = B.call("jawa/set_current_map", {"mapId": -1}) or {}
            det = r.get("details") if isinstance(r.get("details"), dict) else {}
            lm = det.get("loadedMaps", r.get("loadedMaps"))
            ids = [m.get("mapId") for m in lm if isinstance(m, dict)] if isinstance(lm, list) and not r.get("success") else []
            maps = [i for i in ids if isinstance(i, int)]
            cur = (B.call("jawa/map_info", {}) or {}).get("mapId")
            if not maps:
                print("map list unreadable: %s" % str(r)[:200])
                print("JOINT CHECK: UNMEASURED")
                return 2
        for mid in maps:
            if mid is not None:
                B.call("jawa/set_current_map", {"mapId": int(mid)})
                time.sleep(1.0)
            ans = _probe(B, "joints")
            if isinstance(ans, dict) and ans.get("success"):
                ans = dict(ans, extra=extra_joints(B, lambda cmd: _probe(B, cmd)))
            verdict, lines = judge(ans)
            print("map %s: %s" % ("current" if mid is None else mid, verdict))
            for ln in lines:
                print(ln)
            results.append({"map": mid, "verdict": verdict, "answer": ans})
            worst = max(worst, verdict, key=lambda v: rank[v])
        if all_maps and isinstance(cur, int):
            B.call("jawa/set_current_map", {"mapId": int(cur)})
    print("JOINT CHECK: %s" % worst)
    if out:
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"verdict": worst, "maps": results}, f, indent=1)
    return {"PASS": 0, "FAIL": 1, "UNMEASURED": 2}[worst]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
