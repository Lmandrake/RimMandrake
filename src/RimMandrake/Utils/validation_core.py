"""validation_core.py -- the mod-neutral half of a live bridge validation script (hose port step 2, design FINAL §3.10, G5.1).

Extracted from GimmeSomeSlack/validation.py so a script of another mod (FlowWorks/validation_hose.py) can drive the bridge
without importing Gimme Some Slack's harness. Nothing here names a mod: the probe a Bridge talks to is the `probe_type`
attribute of its subclass, and the mod/package/tier constants live in each script.

    import validation_core as V
    class B(V.Bridge): probe_type = "RimMandrake.FlowWorks.Hose.HoseProbe"

Contents: REPO / UTILS / SAVES / PLAYER_LOG paths; row/hrow (with the SHARED one-session switch a proof driver sets);
_BridgeBase / Bridge (own socket) / SuiteBridge (a modcheck Session); ops/perimeter cell helpers; save helpers
_saves_stat / _wait_saved / _wait_playing.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = HERE
SAVES = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "LocalLow", "Ludeon Studios",
                     "RimWorld by Ludeon Studios", "Saves")
PLAYER_LOG = os.path.join(os.path.dirname(SAVES), "Player.log")

# SHARED (set by a proof driver): one session, one map. A harness/site row is then written only when it is NOT PASS (a
# fault still surfaces under its own id; a green one becomes a site note).
SHARED = False
SITE_NOTES = []


class Row(dict):
    pass


def row(rows, rid, status, cls, detail):
    rows.append({"id": rid, "status": status, "class": cls, "detail": detail})
    print("%-28s %-9s %s" % (rid, status, str(detail)[:150]), flush=True)


def hrow(rows, rid, status, cls, detail):
    """A harness/site row: a row of its own standalone; in SHARED mode only when it is not PASS."""
    if SHARED and status == "PASS":
        SITE_NOTES.append({"id": rid, "detail": detail})
        return
    row(rows, rid, status, cls, detail)


class _BridgeBase(object):
    """call / probe / ticks over a raw transport (`_raw`): the standalone socket or the suite's Session. `probe` talks to
    the static request/result/serial fields of the type named by the subclass's `probe_type`."""
    probe_type = None

    def _raw(self, tool, kw):
        raise NotImplementedError

    def call(self, tool, **kw):
        r = self._raw(tool, kw) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:  # noqa: BLE001
                pass
        return r if isinstance(r, dict) else {"success": False, "raw": r}

    def probe_of(self, probe_type, cmd, wait_s=20.0, poll_s=0.3):
        before = self.call("jawa/mod_settings_field", typeName=probe_type, action="get", field="serial").get("value")
        s = self.call("jawa/mod_settings_field", typeName=probe_type, action="set", field="request", value=cmd)
        if not s.get("success"):
            return {"success": False, "error": "probe set failed", "raw": s}
        t0 = time.time()
        while time.time() - t0 < wait_s:
            now = self.call("jawa/mod_settings_field", typeName=probe_type, action="get", field="serial").get("value")
            if now != before:
                res = self.call("jawa/mod_settings_field", typeName=probe_type, action="get", field="result").get("value")
                try:
                    return json.loads(res)
                except Exception:  # noqa: BLE001
                    return {"success": False, "raw": res}
            time.sleep(poll_s)
        return {"success": False, "error": "probe timed out (no frame serviced it)"}

    def probe(self, cmd, wait_s=20.0):
        if not self.probe_type:
            return {"success": False, "error": "no probe_type on this bridge class"}
        return self.probe_of(self.probe_type, cmd, wait_s)

    def ticks(self, n):
        return self.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=120000)


class Bridge(_BridgeBase):
    """Standalone: its own socket to the bridge."""

    def __init__(self):
        if UTILS not in sys.path:
            sys.path.insert(0, UTILS)
        import rimbridge_client as rb  # noqa: E402
        host, port, token = rb.resolve_endpoint()
        self.S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
        self.S.connect()

    def _raw(self, tool, kw):
        return self.S.call(tool, kw, check=False)


class SuiteBridge(_BridgeBase):
    """Suite: calls ride the runner's Session; game time goes through t.wait_ticks (clock-verified)."""

    def __init__(self, t):
        self.t = t

    def _raw(self, tool, kw):
        return self.t.session.call(tool, **kw)

    def ticks(self, n):
        self.t.wait_ticks(n)
        return {"success": True}


def perimeter(x0, z0, x1, z1):
    out = []
    for x in range(x0, x1 + 1):
        out += [(x, z0), (x, z1)]
    for z in range(z0 + 1, z1):
        out += [(x0, z), (x1, z)]
    return out


def ops(defn, cells, rot=None):
    return ";".join("%s:%d,%d%s" % (defn, c[0], c[1], "" if rot is None else ",%d" % rot) for c in cells)


def _saves_stat():
    return {n: (os.path.getsize(os.path.join(SAVES, n)), int(os.path.getmtime(os.path.join(SAVES, n))))
            for n in os.listdir(SAVES) if os.path.isfile(os.path.join(SAVES, n))}


def _wait_saved(name, budget_s=60):
    """After rimworld/save_game: wait until <name>.rws exists and its size holds across two reads 1 s apart."""
    path = os.path.join(SAVES, name + ".rws")
    t0, last = time.time(), -1
    while time.time() - t0 < budget_s:
        time.sleep(1.0)
        size = os.path.getsize(path) if os.path.exists(path) else -1
        if size > 0 and size == last:
            return True
        last = size
    return False


def _wait_playing(B, budget_s=240, leave_s=30):
    """After rimworld/load_game: wait for the load to START, then for Playing (load_game answers "queued" and the old map
    stays Playing for ~3-8 s first, measured 2026-10-10 on the 550-mod list)."""
    st = None
    t0 = time.time()
    while time.time() - t0 < leave_s:
        if B.call("rimworld/get_ui_state").get("programState") != "Playing":
            break
        time.sleep(0.5)
    while time.time() - t0 < budget_s:
        st = B.call("rimworld/get_ui_state").get("programState")
        if st == "Playing" and B.call("jawa/map_info").get("success"):
            return True, int(time.time() - t0)
        time.sleep(2)
    return False, st


def reveal(B, rect, ticks=30):
    """Make a site DISCOVERED for every fog on the list, not only vanilla's: a colonist stands at its centre for `ticks`
    and goes back. 2026-10-10 (550-mod list): jawa/set_fog unfog did not stop "CanDesignateCell refused ...: Can't place in
    undiscovered area" for designator-placed runs; a colonist's sight did. Uses B's own probe ("colonists" and
    "pawn:<id>=draft|undraft|tp:x,z", answered by GimmeSomeSlackProbe and FlowWorks' HoseProbe alike)."""
    col = B.probe("colonists")
    pawns = [p for p in col.get("pawns") or [] if not p.get("downed") and p.get("pos")]
    if not pawns:
        return {"revealed": False, "why": "no free colonist"}
    p = pawns[0]
    x, z, w, h = rect
    B.probe("pawn:%d=draft" % p["id"])            # drafted, so he takes no job while he stands there (audit 2026-10-10)
    spots = [(x + w // 4, z + h // 2), (x + 3 * w // 4, z + h // 2)] if w > 30 else [(x + w // 2, z + h // 2)]
    for sx, sz in spots:
        B.probe("pawn:%d=tp:%d,%d" % (p["id"], sx, sz))
        B.ticks(ticks)
    B.probe("pawn:%d=tp:%d,%d" % ((p["id"],) + tuple(p["pos"])))
    if not p.get("drafted"):
        B.probe("pawn:%d=undraft" % p["id"])
    return {"revealed": True, "pawn": p["id"]}


def prepare_site(B, rect, rows, rid):
    """Make a site's cells independent of the quicktest map's random terrain (roofed ruins, rock, plants, non-soil floor).
    Clear everything, Soil, unfog, remove roof, then READ BACK: any roof or any thing still standing in the rect is an
    environmental block and is recorded UNMEASURED (never a mod FAIL). Returns True when the site is ready."""
    import re
    r = "%d,%d,%d,%d" % tuple(rect)
    why = []
    for tool, kw in (("jawa/destroy_batch", {"rects": r, "categories": "All"}),
                     ("jawa/set_terrain_batch", {"ops": "Soil:" + r}),
                     ("jawa/set_fog", {"action": "unfog", "rect": r}),
                     ("jawa/set_roof_batch", {"ops": "None:" + r})):
        res = B.call(tool, **kw)
        if isinstance(res, dict) and res.get("success") is False:
            why.append("%s refused: %s" % (tool, str(res)[:160]))
    reveal(B, rect)
    B.ticks(2)
    roof = B.call("jawa/get_roof_batch", rects=r) or {}
    roofs = [x for x in (roof.get("roofs") or []) if x not in (None, "None")]
    if roofs:
        why.append("roof still present over the site: %s" % roofs)
    elif roof.get("success") is False:
        why.append("get_roof_batch unreadable: %s" % str(roof)[:160])
    lt = B.call("jawa/list_things", rect=r, limit=20) or {}
    left = [d for d in ((t.get("defName") or t.get("def") or t.get("label") or "") for t in (lt.get("things") or []))
            if re.search(r"Granite|Sandstone|Limestone|Marble|Slate|Rock|Chunk|Plant_|Tree|Bush|Grass|Ruin", str(d))]
    if left:
        why.append("rock/plants/ruins still standing in the site: %s" % left[:8])
    if why:
        row(rows, rid, "UNMEASURED", "SITE", {"rect": list(rect), "blocked": why,
            "meaning": "the quicktest terrain still blocks the site after clearing; this is environmental, not a mod result"})
        return False
    return True
