#!/usr/bin/env python3
"""live_world_stars_pinned.py - WORLD_STARS_REPAIR_STILL_SPINNING_FOR_NOBODY A3, decided by a state read.

The bar (A3): a day later, the planet-view sun disc and the lit side are in the same place, and the stars have turned
about 6 degrees (one turn per 60-day year).

Why a state read, not two screenshots (cheaper_why): the disc, the planet light and the starfield are drawn from two
values only, GenCelestial.CurSunPositionInWorldSpace() (GlobalDrawLayer_Sun, WorldRendererUtility's shader params)
and GlobalDrawLayer_Stars.Rotation. Reading those values decides the bar without the world view, a day of ticks, or
pixel comparison of two captures (which also see clouds, the camera and landmark icons).

What it reads, on the RUNNING game (never ModsConfig, which names the next load):
  R1 jawa/mod_inventory holds mandrake.rm.creaturebehaviors, and the game is Playing; else exit 2 (COULD NOT LOOK).
  R2 jawa/harmony_patches: GlobalDrawLayer_Stars.Rotation carries RM_WorldStarsPatch.Postfix_Rotation, and
     GenCelestial.CurSunPositionInWorldSpace carries RM_WorldSunPatch.Postfix_CurSunPositionInWorldSpace.
  R3 CurSunPositionInWorldSpace() == RM_WorldSunPatch.PinnedDirection() (a cached constant): the sun cannot move with
     the clock. The settings that switch the pin (worldSunPinned) are read, and must be on (the default).
  R4 DriftDegrees(TicksAbs + 60000) - DriftDegrees(TicksAbs) == 6 degrees with the drift setting on (0 when frozen),
     the turn the Rotation postfix applies (its body is proven offline by selftest_sun_heat.py, "world stars").
Exit 0 = the bar holds, 1 = a reading refutes it, 2 = no reading. Run under python.exe (the bridge binds Windows
loopback), with RM_DATA_ROOT set for the client's log.
"""
import json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

PKG = "mandrake.rm.creaturebehaviors"
NS = "RimMandrake.CreatureBehaviors."


def main():
    host, port, token = rb.resolve_endpoint()
    S = rb.RimBridge(host=host, port=port, token=token, timeout=120.0)
    S.connect()

    def call(tool, **p):
        r = S.call(tool, p) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:
                pass
        return r

    def static(type_, method, args=""):
        r = call("jawa/static_call", type=type_, method=method, args=args)
        if not r.get("success"):
            print("UNMEASURED: static_call %s.%s refused: %s" % (type_, method, r.get("message") or r))
            sys.exit(2)
        return str(r.get("result"))

    inv = json.dumps(call("jawa/mod_inventory")).lower()
    if '"%s"' % PKG not in inv:
        print("UNMEASURED: %s is not in the RUNNING mod list (jawa/mod_inventory); load a list that holds it" % PKG)
        return 2
    gi = call("rimworld/get_game_info")
    state = (gi.get("state") or {}).get("programState") or gi.get("programState")
    if state != "Playing":
        print("UNMEASURED: programState %s, not Playing (the pin acts only in play)" % state)
        return 2
    fails = []

    def postfix_of(type_name, method, patch):
        hp = call("jawa/harmony_patches", typeName=type_name)
        for m in hp.get("methods") or []:
            if method in str(m.get("method")):
                return any(patch in str(p.get("patchMethod")) for p in m.get("postfixes") or [])
        return False

    if not postfix_of("GlobalDrawLayer_Stars", "Rotation", "Postfix_Rotation"):
        fails.append("R2: no RM_WorldStarsPatch.Postfix_Rotation on GlobalDrawLayer_Stars.Rotation: the stars turn daily")
    if not postfix_of("GenCelestial", "CurSunPositionInWorldSpace", "Postfix_CurSunPositionInWorldSpace"):
        fails.append("R2: no RM_WorldSunPatch postfix on GenCelestial.CurSunPositionInWorldSpace: the sun turns daily")

    rp = call("jawa/read_paths", reads=json.dumps([
        {"of": "static:" + NS + "RM_CreatureBehaviorsSettings", "path": "worldSunPinned"},
        {"of": "static:" + NS + "RM_CreatureBehaviorsSettings", "path": "worldStarsPinned"},
        {"of": "static:" + NS + "RM_CreatureBehaviorsSettings", "path": "worldStarsYearlyDrift"}]))
    vals = {v.get("path"): v for v in rp.get("values") or []}
    for k in ("worldSunPinned", "worldStarsPinned", "worldStarsYearlyDrift"):
        if (vals.get(k) or {}).get("state") != "ok":
            print("UNMEASURED: setting %s not read: %s" % (k, vals.get(k) or rp.get("message")))
            return 2
    on = {k: str(vals[k].get("v")).lower() == "true" for k in vals}
    if not (on["worldSunPinned"] and on["worldStarsPinned"]):
        fails.append("R3: the pin is switched off in Mod Settings (worldSunPinned=%s, worldStarsPinned=%s); "
                     "the bar is read at the defaults" % (on["worldSunPinned"], on["worldStarsPinned"]))

    nums = lambda s: [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?(?:[eE]-?\d+)?", s)]
    sun = nums(static("RimWorld.GenCelestial", "CurSunPositionInWorldSpace"))
    pin = nums(static(NS + "RM_WorldSunPatch", "PinnedDirection"))
    if len(sun) != 3 or len(pin) != 3:
        print("UNMEASURED: vectors not parsed: sun %s, pinned %s" % (sun, pin))
        return 2
    if max(abs(a - b) for a, b in zip(sun, pin)) > 1e-3:
        fails.append("R3: the planet-view sun %s is not the pinned direction %s: it moves with the clock" % (sun, pin))

    t = int(nums(static("Verse.GenTicks", "get_TicksAbs"))[0])
    drift = "true" if on["worldStarsYearlyDrift"] else "false"
    d0 = nums(static(NS + "RM_WorldStarsMath", "DriftDegrees", "%d|%s" % (t, drift)))[0]
    d1 = nums(static(NS + "RM_WorldStarsMath", "DriftDegrees", "%d|%s" % (t + 60000, drift)))[0]
    turn = (d1 - d0) % 360.0
    want = 6.0 if on["worldStarsYearlyDrift"] else 0.0
    if abs(turn - want) > 0.01:
        fails.append("R4: the stars turn %.3f degrees in a day, not %.1f" % (turn, want))

    for f in fails:
        print("FAIL:", f)
    if fails:
        return 1
    print("PASS: sun %s = pinned direction (both postfixes live); stars turn %.2f deg a day (drift %s) at TicksAbs %d"
          % (sun, turn, drift, t))
    return 0


if __name__ == "__main__":
    sys.exit(main())
