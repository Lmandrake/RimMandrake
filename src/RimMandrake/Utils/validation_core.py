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
        tap_after(tool)
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


# Verse.Log stops ALL managed logging after 10,000 messages ("Reached max messages limit"; skills/rimbridge traps.md), and on
# the owner's full list a chatty conversation mod reaches that inside one session: every later Log.Warning/Error is dropped,
# so RimBridge's journal goes silent and a log-budget row reads "0 errors" while seeing nothing (2026-10-11: proof_hose Z
# read otherErrors 0 and v2's E9 sanity warning vanished, both after the cap). The only reset is Log.Clear (the debug log
# window's Clear button), reachable through jawa/static_call (test profile).
LOG_SENTINEL = "[proof log sentinel]"


def log_alive(B, tag="check"):
    """Emit one fresh warning and read it back: {"alive": bool, "sentinel": text}. A log budget is evidence only when alive."""
    s = "%s %s %d" % (LOG_SENTINEL, tag, int(time.time() * 1000))
    w = B.call("jawa/static_call", type="Verse.Log", method="Warning", args=s)
    lg = B.call("rimbridge/list_logs", limit=50, minimumLevel="warning") or {}
    seen = any(s in str(e.get("Message", "")) for e in lg.get("logs") or [])
    return {"alive": seen, "sentinel": s, "emitted": bool(w.get("success")), "why": None if seen else (w.get("error") or w.get("message"))}


class LogTap(object):
    """Keeps every warn+/error journal entry of a run, and says whether any were lost.

    RimBridge's journal is a RING of the last 1,000 entries of ALL levels. On the owner's full list an intimacy mod logs
    ~0.3 info lines per tick (MEASURED 2026-10-11: 176 per 600 ticks, "X cannot currently do lovin'"), so a warning
    is evicted ~3,400 ticks after it is written: a log budget read once at the end of a 10-minute proof saw only its last
    blocks (v2's E9 found "0 warn+ lines since base" though E7b's warning had fired). The tap is polled after every
    step_game_ticks a bridge makes (tap_after) and at block boundaries; `lost` counts journal entries that scrolled out
    between two polls -- a budget with lost > 0 is not evidence."""

    def __init__(self, B):
        self.B = B
        self.entries = {}
        self.lost = 0
        self.polls = 0
        self.gaps = []     # (first lost seq, last lost seq, poll #, the call that preceded the poll)
        self.trigger = None
        lg = B.call("rimbridge/list_logs", limit=1, minimumLevel="trace") or {}
        self.last = max([x.get("Sequence", 0) for x in lg.get("logs") or []] or [0])
        self.base = self.last

    def poll(self):
        self.polls += 1
        lg = self.B.call("rimbridge/list_logs", afterSequence=self.last, limit=1000, minimumLevel="trace") or {}
        logs = lg.get("logs") or []
        if not logs:
            return
        # an entry repeated N times is ONE journal row carrying the sequence of its LATEST occurrence and RepeatCount N: it
        # covers seq-N+1..seq (measured 2026-10-11: rows 22138 x4, 22142 x4, ... with nothing between), so coverage starts there
        lo = min(int(x.get("Sequence", 0)) - max(1, int(x.get("RepeatCount") or 1)) + 1 for x in logs)
        hi = max(int(x.get("Sequence", 0)) for x in logs)
        if lo > self.last + 1:
            self.lost += lo - self.last - 1
            if len(self.gaps) < 20:
                self.gaps.append((self.last + 1, lo - 1, self.polls, self.trigger))
        for x in logs:
            if str(x.get("Level", "")).lower() in ("warning", "error", "exception"):
                self.entries[x.get("Sequence", 0)] = x
        self.last = max(self.last, hi)

    def since(self, seq=None):
        self.poll()
        b = self.base if seq is None else seq
        return [self.entries[k] for k in sorted(self.entries) if k > b]


TAP = []


def tap_start(B):
    """Start the run's journal tap (replacing any earlier one); bridges poll it after each tick step."""
    del TAP[:]
    TAP.append(LogTap(B))
    return TAP[0]


# the calls after which the journal can have moved by a lot: a tick step, and a load/save/new game and the state polls a
# caller makes while one runs (a full-list save load writes ~1,000 lines; polled every couple of seconds it is kept whole)
TAP_TOOLS = ("rimworld/step_game_ticks", "rimworld/load_game", "rimworld/save_game", "rimworld/get_ui_state", "jawa/map_info",
             "rimworld/start_debug_game_ready", "rimworld/go_to_main_menu", "jawa/order_pawn")


def tap_after(tool):
    """Bridge hook: poll the tap after a call that lets the journal scroll (TAP_TOOLS)."""
    if TAP and tool in TAP_TOOLS:
        try:
            TAP[0].trigger = tool
            TAP[0].poll()
        except Exception:  # noqa: BLE001 - the tap must never break the call it rides on
            pass


def log_revive(B):
    """Reset Verse.Log's message cap (Log.Clear) before a run, then prove logging is live."""
    c = B.call("jawa/static_call", type="Verse.Log", method="Clear")
    return dict(log_alive(B, "revive"), cleared=bool(c.get("success")))


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


def clear_huge_plants(B, margin=6, tile=16):
    """Remove every huge plant whose footprint is on the map, so no test site inherits its trunk blockers.

    2026-10-11 (full list, RM_TheRot quicktest map): Huge Things' MapComponent_HugeFootprints keeps a giant plant's footprint
    as RM_HugeTrunkBlocker buildings and RE-PLANS any blocker that vanishes while its plant stands -- so a site prep that
    destroyed the blockers inside its rect got them back from a giant standing OUTSIDE it, and a reel build there read
    "CanDesignateCell refused: Space already occupied" (style_hose R1-R6 FAIL, a site fault). The plant is found through its
    blockers: every plant within `margin` of a blocker cell goes (it is cheap: test maps only). Returns counts."""
    lt = B.call("jawa/list_things", defName="RM_HugeTrunkBlocker", limit=5000) or {}
    cells = [(t.get("x"), t.get("z")) for t in lt.get("things") or [] if t.get("x") is not None]
    tiles = sorted({(x // tile, z // tile) for x, z in cells})
    for tx, tz in tiles:
        B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (tx * tile - margin, tz * tile - margin, tile + 2 * margin,
                                                             tile + 2 * margin), categories="Plant")
    if tiles:
        B.ticks(2)
    left = (B.call("jawa/list_things", defName="RM_HugeTrunkBlocker", limit=5000) or {}).get("things") or []
    return {"blockers": len(cells), "tiles": len(tiles), "blockersLeft": len(left)}


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
            if re.search(r"Granite|Sandstone|Limestone|Marble|Slate|Rock|Chunk|Plant_|Tree|Bush|Grass|Ruin|TrunkBlocker", str(d))]
    if left:
        why.append("rock/plants/ruins still standing in the site: %s" % left[:8])
    if why:
        row(rows, rid, "UNMEASURED", "SITE", {"rect": list(rect), "blocked": why,
            "meaning": "the quicktest terrain still blocks the site after clearing; this is environmental, not a mod result"})
        return False
    return True
