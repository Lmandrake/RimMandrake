"""RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN, live state read: a pit cut deeper past 2 m re-meshes its walls,
and so does its neighbour across a section edge (his stepped pit, walk 2026-11-20, drew as one flat floor because the walls
layer re-meshed only on a floor TERRAIN change, and every floor past 2 m is one terrain).

Why a live row: the selftest (selftest_flowworks_pit_relative_terrain.py, the C# PitRelief_* cases) proves the source and the
call sites; only the game shows that the DLL it loaded marks the right sections dirty when the engine's own Deepen cuts.

What it reads (every value from the running game):
  staging  RM_NorthstarProofs.ProofStageBasin "x;z;w;h;levels;0;RM_Fluid_Water" (the engine's Deepen; dry).
  mesh     RM_NorthstarProofs.ProofWallFacesStale "x,z": the built walls mesh's fingerprint, whether the section is dirty for
           the layer, then a fresh build's fingerprint. A mesh that is stale (built != fresh) and NOT dirty is the bug.

Scene (3x3 from --origin x,z; z must be a section's top row, 17k - 1, so the pit's south row lies in one section and its
middle row in the section north of it): rows south z, middle z+1, north z+2.
  1. dig all nine to 7 notches (3.5 m), step 2 ticks, read the south-west square twice (the second read must find the mesh
     the first built: the instrument can see).
  2. cut the south row to 11 (5.5 m): his pit. Read the south-west square           -> RELIEF_CUT_REDRAWS_ITS_SQUARE
  3. cut the middle row to 11: the south row's inner face goes; its section is the other one. Read the south-west square
                                                                                    -> RELIEF_CUT_REDRAWS_ACROSS_SECTION_EDGE
  Each read must change the fresh fingerprint from the read before it (the art did change), else the scene proves nothing:
  SITE, never PASS.
LIES: a refused proof is HARNESS; a pit that did not dig is SITE. Exit 0 only when every row PASSes; 1 on any FAIL; 2 otherwise.

    python.exe src\\RimMandrake\\FlowWorks\\northstar\\pit_relief_live.py <out.json> [--origin 60,67]
    python3 src/RimMandrake/FlowWorks/northstar/pit_relief_live.py --mock [--mock-faults no_redraw]
"""
import argparse
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)

NPROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"
ITEM = "RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN"
ROW_IDS = ["RELIEF_CUT_REDRAWS_ITS_SQUARE", "RELIEF_CUT_REDRAWS_ACROSS_SECTION_EDGE"]
SECTION = 17          # Verse.Section.Size


def parse(txt):
    out = {}
    for tok in (txt or "").split()[1:]:
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


def mesh_verdict(before, after):
    """before / after: parsed WALLSTALE reads round one cut. -> (status, cls, why)."""
    if not after or "stale" not in after or not before or "fresh" not in before:
        return "UNMEASURED", "HARNESS", "a mesh read is missing"
    if after.get("fresh") == before.get("fresh"):
        return "UNMEASURED", "SITE", "the cut did not change the art (fresh %s both times): the scene proves nothing" % after.get("fresh")
    if after.get("stale") == "True" and after.get("dirty") != "True":
        return "FAIL", "MOD", "the walls mesh is stale and its section is not marked for re-mesh (built %s, fresh %s)" % (
            after.get("built"), after.get("fresh"))
    return "PASS", "MOD", "re-meshed or marked dirty (stale=%s dirty=%s)" % (after.get("stale"), after.get("dirty"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="60,67")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--mock-faults", default="", help="comma list: " + ",".join(FakeBridge.FAULTS))
    a = ap.parse_args(argv)
    faults = [f for f in a.mock_faults.split(",") if f]
    if set(faults) - set(FakeBridge.FAULTS):
        ap.error("unknown --mock-faults %s" % ",".join(sorted(set(faults) - set(FakeBridge.FAULTS))))
    ox, oz = (int(v) for v in a.origin.split(","))
    if (oz + 1) % SECTION != 0:
        ap.error("--origin z must be a section's top row (17k - 1) so the middle row lies in the next section")
    if a.mock:
        B = FakeBridge(faults)
    else:
        import validation_core as V      # noqa: E402  (bridge-side imports only on a live run)
        import proof_hose as PH          # noqa: E402
        B = V.guard(PH.PB())
    out = a.out or os.path.join(tempfile.gettempdir(), "pit_relief_%s_%s.json" % ("mock" if a.mock else "live", time.strftime("%Y%m%dT%H%M%S")))
    rows = []
    res = {"script": "pit_relief_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    def row(rid, st, cls, why, det=None):
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": dict(det or {}, why=why)})
        print("%-42s %-10s %-8s %s" % (rid, st, cls, why[:200]), flush=True)
        save()

    def call(method, arg):
        r = B.call("jawa/static_call", type=NPROOF, method=method, args=arg, _answer=True) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        return (r.get("success") is True and not txt.startswith("REFUSED")), txt

    def stage(x, z, w, h, levels):
        ok, txt = call("ProofStageBasin", "%d;%d;%d;%d;%d;0;RM_Fluid_Water" % (x, z, w, h, levels))
        B.call("rimworld/step_game_ticks", ticks=2, pauseFirst=True, timeoutMs=60000)
        return ok and parse(txt).get("maxDepth") == str(levels), txt

    def read():
        ok, txt = call("ProofWallFacesStale", "%d,%d" % (ox, oz))
        return parse(txt) if ok and txt.startswith("WALLSTALE") else None, txt

    def all_rows(why, cls):
        for rid in ROW_IDS:
            row(rid, "UNMEASURED", cls, why)
        return 2

    ok, txt = call("ProofResetRect", "%d;%d;%d;%d" % (ox - 2, oz - 2, 7, 7))
    if not ok:
        return all_rows("ProofResetRect refused: %s" % txt[:160], "HARNESS")
    ok, txt = stage(ox, oz, 3, 3, 7)
    if not ok:
        return all_rows("the 3x3 did not dig to 7 notches: %s" % txt[:160], "SITE")
    r0, t0 = read()
    if r0 is None:
        return all_rows("ProofWallFacesStale is not in the loaded FlowWorks: %s" % t0[:160], "HARNESS")
    r1, _ = read()
    res["control"] = r1
    if not r1 or r1.get("stale") != "False":
        return all_rows("the instrument is blind: a read right after a fresh build reads stale (%s)" % r1, "HARNESS")
    if r1.get("dirty") != "False":
        return all_rows("the instrument cannot clear the mark it read (dirty after its own rebuild: %s)" % r1, "HARNESS")
    ok, txt = stage(ox, oz, 3, 1, 11)
    if not ok:
        return all_rows("the south row did not cut to 11: %s" % txt[:160], "SITE")
    r2, _ = read()
    st, cls, why = mesh_verdict(r1, r2)
    row(ROW_IDS[0], st, cls, why, {"before": r1, "after": r2})
    r2b, _ = read()                      # clean before the next cut, so its mark cannot be this cut's
    if not r2b or r2b.get("dirty") != "False" or r2b.get("stale") != "False":
        row(ROW_IDS[1], "UNMEASURED", "HARNESS", "the square was not clean before the second cut: %s" % r2b)
        save()
        return 2
    ok, txt = stage(ox, oz + 1, 3, 1, 11)
    if not ok:
        row(ROW_IDS[1], "UNMEASURED", "SITE", "the middle row did not cut to 11: %s" % txt[:160])
    else:
        r3, _ = read()
        st, cls, why = mesh_verdict(r2b, r3)
        row(ROW_IDS[1], st, cls, why, {"before": r2b, "after": r3})
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    fails = [r for r in rows if r["status"] == "FAIL"]
    print("pit relief: %d rows, %d FAIL, %d not PASS -> %s" % (len(rows), len(fails), sum(r["status"] != "PASS" for r in rows), out))
    return 1 if fails else (2 if any(r["status"] != "PASS" for r in rows) else 0)


# ====================================================================== offline stand-in
class FakeBridge(object):
    """A small world model answering in ProofStageBasin / ProofWallFacesStale's line formats, the redraw rule of the rebuild
    (a cut dirties its square's section and its 8 neighbours'). It proves the script's control flow and its MOD/SITE/HARNESS
    split only. Faults, one wrong thing each:
      old_deploy   ProofWallFacesStale missing                                  -> both rows UNMEASURED/HARNESS
      no_redraw    MOD: the pre-rebuild layer: a cut past 2 m dirties nothing    -> both rows FAIL
      two_arg      MOD: the 2-argument MapMeshDirty: the cut's own section only  -> ACROSS_SECTION_EDGE FAIL
      no_dig       the south row refuses to deepen                              -> UNMEASURED/SITE
      blind        the instrument reads stale even on a fresh build             -> both rows UNMEASURED/HARNESS"""
    FAULTS = ("old_deploy", "no_redraw", "two_arg", "no_dig", "blind")

    def __init__(self, faults=()):
        self.f = set(faults)
        self.depth = {}
        self.built = {}                    # section -> depth snapshot it was built from
        self.dirty = set()

    def _sec(self, x, z):
        return (x // SECTION, z // SECTION)

    def _art(self, sec):
        return hash(tuple(sorted((k, v) for k, v in self.depth.items() if self._sec(*k) == sec or
                                 any(self._sec(k[0] + dx, k[1] + dz) == sec for dx in (-1, 0, 1) for dz in (-1, 0, 1)))))

    def stage(self, arg):
        x, z, w, h, levels, _w, _fl = arg.split(";")
        x, z, w, h, levels = (int(v) for v in (x, z, w, h, levels))
        if "no_dig" in self.f and levels == 11 and h == 1 and z % SECTION == SECTION - 1:
            return "BASIN cells=%d dug=0 filled=0 refused=%d maxDepth=7" % (w, w)
        for i in range(w):
            for j in range(h):
                c = (x + i, z + j)
                before = self.depth.get(c, 0)
                self.depth[c] = levels
                crosses_band = min(before, 4) != min(levels, 4)
                if "no_redraw" in self.f and not crosses_band:
                    continue
                if "two_arg" in self.f and not crosses_band:
                    self.dirty.add(self._sec(*c))
                    continue
                for dx in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        self.dirty.add(self._sec(c[0] + dx, c[1] + dz))
        return "BASIN cells=%d dug=%d filled=0 refused=0 maxDepth=%d" % (w * h, w * h, levels)

    def stale(self, arg):
        x, z = (int(v) for v in arg.split(","))
        sec = self._sec(x, z)
        built = self.built.get(sec, "none")
        dirty = sec in self.dirty
        fresh = "%016x" % (self._art(sec) & 0xffffffffffffffff)
        self.built[sec] = fresh
        self.dirty.discard(sec)            # the proof rebuilds the layer and clears its Dirty
        shown = "0" * 16 if "blind" in self.f else built
        return "WALLSTALE built=%s fresh=%s stale=%s dirty=%s verts=12" % (shown, fresh, shown != fresh, dirty)

    def tick(self):
        # nothing re-meshes off camera in this model: a dirty section stays dirty until a read rebuilds it
        pass

    def call(self, tool, **kw):
        if tool == "jawa/static_call":
            m = kw.get("method")
            if m == "ProofResetRect":
                self.depth.clear()
                return {"success": True, "result": "RESET cells=0"}
            if m == "ProofStageBasin":
                return {"success": True, "result": self.stage(kw.get("args") or "")}
            if m == "ProofWallFacesStale":
                if "old_deploy" in self.f:
                    return {"success": False, "error": "Method not found: ProofWallFacesStale"}
                return {"success": True, "result": self.stale(kw.get("args") or "")}
            return {"success": False, "error": "unknown"}
        return {"success": True}


if __name__ == "__main__":
    sys.exit(main())
