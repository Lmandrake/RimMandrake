"""Live proof A5 of BLUEDESERT_GPT_ENRICHMENT_1: the vhaulk walks off. On the current (disposable quicktest) map,
retiled to RM_BlueDesert at -30 C through modcheck.bland_world.retile, a wild RM_Vhaulk spawned near the west edge
stays (vhaulkStayDaysFactor at 0.01, which the C# clamps to 0.1: 2-5 days -> 12000-30000 ticks), then walks off a map
edge and the departure letter "The mountain moves on" arrives. It never silently despawns.

Why standalone (gen 11, 2026-11-03): the validation chain vhaulk_departs ran on an un-retiled 42 C RM_Webwork map, the
vhaulk died there of the heat (Corpse_RM_Vhaulk on the map), and the chain's "no longer a living pawn" test read the
death as a departure without a letter. This proof makes the map the vhaulk's own biome, and tells a death (a corpse
of THIS pawn) from a walk-off.
Exits 0 when the clause holds, 1 when it does not, 2 when unmeasured.

Run under Windows python.exe with the game up (it starts a debug quicktest map if none is playing):
    python.exe src/RimMandrake/BlueDesert/prove_vhaulk_departs.py < /dev/null   (from the repo root)
It cleans up: the setting restored, the tile's biome and temperature restored.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
sys.path.insert(0, UTILS)
sys.path.insert(0, os.path.join(UTILS, "modcheck"))
import rimbridge_client as rb       # noqa: E402
import bland_world as BW            # noqa: E402

SETTINGS = "RimMandrake.BlueDesert.RM_BlueDesertSettings"
KIND = "RM_Vhaulk"
LETTER = "The mountain moves on"            # RM_BlueDesertFauna.xml departureLetterLabel
STEP = 3000                                 # ticks between two reads
DEADLINE = 42000                            # max stay 30000 ticks plus the walk off a near edge


def judge(trace):
    """Reads -> (code, why). A read: {"ticks", "state": "alive"|"dead"|"gone", "letter": bool}. Pure (selftested).
    PASS: the pawn is gone (no living pawn, no corpse of it), the letter has arrived, and it was alive at every read
    before. A death is a FAIL (a vhaulk dying on its own cold biome with nothing hurting it), not a departure."""
    if not trace:
        return 2, "no reads"
    if any(r["letter"] for r in trace if r["state"] == "alive"):
        return 1, "the departure letter arrived while the vhaulk still stood on the map"
    last = trace[-1]
    if last["state"] == "dead":
        return 1, "the vhaulk died at tick %d instead of walking off" % last["ticks"]
    if last["state"] == "alive":
        return 1, "the vhaulk was still on the map %d ticks after it arrived: it never walks off" % last["ticks"]
    if not last["letter"]:
        return 1, "the vhaulk left the map but no '%s' letter arrived: a silent departure" % LETTER
    return 0, "walked off after %d ticks with the letter" % last["ticks"]


class Session(object):
    def __init__(self):
        host, port, token = rb.resolve_endpoint()
        self.b = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
        self.b.connect()

    def call(self, tool, **p):
        r = self.b.call(tool, p) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:
                pass
        return r


def ticks(s):
    return (s.call("rimworld/get_game_info") or {}).get("ticksGame")


def step_to(s, goal):
    for _ in range(12):
        now = ticks(s)
        if now is None or now >= goal:
            return now
        s.call("rimworld/step_game_ticks", ticks=int(min(goal - now, 2000)))
    return ticks(s)


def letter_labels(s):
    out = []
    for l in (s.call("jawa/letter_list") or {}).get("letters") or []:
        lab = l.get("label")
        out.append(lab.get("RawText") if isinstance(lab, dict) else lab)
    return out


def pawn_state(s, pid):
    """'alive' / 'dead' / 'gone' for one pawn id, or None when the read failed."""
    r = s.call("jawa/list_pawns", limit=500, includeCorpses=True)
    if not isinstance(r, dict) or "pawns" not in r:
        return None
    for p in r.get("pawns") or []:
        if p.get("id") == pid:
            return "dead" if p.get("dead") else "alive"
    return "gone"


def main():
    s = Session()
    if s.call("rimworld/get_ui_state").get("programState") != "Playing":
        s.call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
        for _ in range(120):
            if s.call("rimworld/get_ui_state").get("programState") == "Playing":
                break
            time.sleep(1)
    info = s.call("jawa/map_info")
    if info.get("sizeX") is None or info.get("tile") is None:
        print("UNMEASURED: no playing map: %r" % (info,))
        return 2
    sz = int(info["sizeZ"])
    old = (s.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="vhaulkStayDaysFactor") or {}).get("value")
    if old is None:
        print("UNMEASURED: vhaulkStayDaysFactor unreadable")
        return 2
    try:
        rec = BW.retile(s, "RM_BlueDesert", temperature=-30)
    except BW.BlandWorldError as ex:
        print("UNMEASURED: retile failed: %s" % ex)
        return 2
    trace, pid = [], None
    try:
        if (s.call("jawa/map_info") or {}).get("mapBiome") != "RM_BlueDesert":
            print("UNMEASURED: the map does not read RM_BlueDesert after the retile")
            return 2
        s.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="vhaulkStayDaysFactor", value="0.01")
        before = len(letter_labels(s))
        r = s.call("jawa/spawn_pawn", kindDef=KIND, x=6, z=sz // 2, faction="none", count=1)
        pid = (((r or {}).get("pawns") or [{}])[0]).get("id")
        t0 = ticks(s)
        if not pid or t0 is None:
            print("UNMEASURED: spawn_pawn returned no vhaulk: %r" % (r,))
            return 2
        while True:
            now = ticks(s)
            st = pawn_state(s, pid)
            if now is None or st is None:
                print("UNMEASURED: clock or pawn list unreadable at read %d" % len(trace))
                return 2
            trace.append({"ticks": now - t0, "state": st, "letter": LETTER in letter_labels(s)[before:]})
            if st != "alive" or now - t0 >= DEADLINE:
                break
            after = step_to(s, now + STEP)
            if after is None or after <= now:
                print("UNMEASURED: the clock did not move (%r -> %r)" % (now, after))
                return 2
    finally:
        s.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="vhaulkStayDaysFactor", value=str(old))
        problems = BW.restore_tile(s, rec)
        if problems:
            print("restore problems: %s" % problems)
    print(json.dumps({"pawn": pid, "trace": trace}))
    code, why = judge(trace)
    print(("PASS: " if code == 0 else "FAIL: " if code == 1 else "UNMEASURED: ") + why)
    return code


if __name__ == "__main__":
    sys.exit(main())
