"""CORD_STATIC_DYNAMIC_HANDOFF_1 A1 (L2): a lifted (wall-terminal) strand whose OWNER section differs from its PIN
section is drawn by exactly one path through every change that flips its eligibility:
  1. sway on, pin open      -> drawn per frame (dynamic), not in the static mesh
  2. roof the pin cell      -> static only (the roof lands in the PIN section; the owner section must still reprint)
  3. vanilla plant sway OFF -> every strand in the scene still drawn exactly once
  4. unroof, sway pref OFF  -> static;   5. sway pref ON again -> dynamic, not static
State read: GimmeSomeSlackProbe `strands:` (SectionLayer_RM_MessyCords.PrintedStatic joined with DrawMotion's own
predicates). The camera is parked on the scene so both sections regenerate. Prefs.PlantWindSway is restored.
python.exe, bridge held, any quicktest map >= 190 wide. argv "Z" row (default 60). Exit 0 = PASS."""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Utils"))
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=180.0); S.connect()
def call(tool, **kw):
    r = S.call(tool, kw) or {}
    return json.loads(r["content"][0]["text"]) if isinstance(r, dict) and r.get("content") else r
PROBE = "RimMandrake.GimmeSomeSlack.GimmeSomeSlackProbe"
def probe(cmd, wait_s=20.0):
    before = call("jawa/mod_settings_field", typeName=PROBE, action="get", field="serial").get("value")
    call("jawa/mod_settings_field", typeName=PROBE, action="set", field="request", value=cmd)
    t0 = time.time()
    while time.time() - t0 < wait_s:
        if call("jawa/mod_settings_field", typeName=PROBE, action="get", field="serial").get("value") != before:
            res = call("jawa/mod_settings_field", typeName=PROBE, action="get", field="result").get("value")
            try: return json.loads(res)
            except Exception: return {"success": False, "raw": res}
        time.sleep(0.3)
    return {"success": False, "error": "probe timed out"}
def pref(on):
    return call("jawa/static_call", type="Verse.Prefs", method="set_PlantWindSway", args="True" if on else "False")
def settle():
    for _ in range(3):
        call("rimworld/step_game_ticks", ticks=2, pauseFirst=True, timeoutMs=60000)
        time.sleep(0.5)
Z = int(sys.argv[1]) if len(sys.argv) > 1 else 60
X0, WALLX = 153, 171                                  # sections are 17 wide: x 153..169 | 170..186
SITE = (X0 - 1, Z - 3, WALLX - X0 + 4, 7)
R = lambda r: "%d,%d,%d,%d" % r
was = call("jawa/static_call", type="Verse.Prefs", method="get_PlantWindSway", args="").get("result")
fails, log = [], {}
try:
    probe("defaults")
    for kv in ("sway=True", "swayMode=SwayMode.CPU", "swayAmplitude=1", "floorRipple=False"):
        probe("set:" + kv)
    pref(True)
    call("jawa/clear_area", rect=R(SITE), dryRun=False)
    call("jawa/set_terrain_batch", ops="Soil:" + R(SITE))
    call("jawa/set_roof_batch", ops="None:" + R(SITE))
    call("jawa/set_fog", action="unfog", rect=R(SITE))
    call("jawa/build_batch", ops=";".join("Wall:%d,%d" % (WALLX, z) for z in (Z - 1, Z, Z + 1)), stuff="Steel", faction="player")
    call("jawa/build_batch", ops="Battery:%d,%d,0" % (X0 + 1, Z), faction="player")
    call("jawa/build_batch", ops=";".join("PowerConduit:%d,%d" % (x, Z) for x in range(X0 + 2, WALLX + 1)), faction="player", wipeExisting=False)
    call("rimworld/jump_camera_to_cell", x=(X0 + WALLX) // 2, z=Z)
    probe("rebuild"); settle()
    def lifted():
        r = probe("strands:" + R(SITE))
        rows = [s for s in r.get("strands") or [] if s.get("lifted")]
        return r, rows
    r1, L = lifted()
    cross = [s for s in L if s.get("ownerSection") != s.get("pinSection")]
    log["1_open"] = {"strandCount": r1.get("strandCount"), "badPaths": r1.get("badPaths"), "lifted": L, "swayMode": r1.get("swayMode")}
    if not cross:
        fails.append("UNMEASURED: no lifted strand whose owner section differs from its pin section (%s)" % json.dumps(L)[:400])
        raise SystemExit
    k = cross[0]["key"]
    def mine(r): return next((s for s in r.get("strands") or [] if s.get("key") == k), {})
    s1 = mine(r1)
    if not (s1.get("dynamic") and not s1.get("printedStatic") and s1.get("ownerPrinted")):
        fails.append("1 open: want dynamic only, got %s" % s1)
    px, pz = (int(v) for v in s1["pin"].split(","))
    call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,1,1" % (px, pz))
    settle()
    r2 = probe("strands:" + R(SITE)); s2 = mine(r2); log["2_roofed"] = s2
    if not (s2.get("pinRoofed") and s2.get("printedStatic") and not s2.get("dynamic")):
        fails.append("2 pin roofed: want static only, got %s" % s2)
    pref(False); settle()
    r3 = probe("strands:" + R(SITE)); log["3_prefOff_roofed"] = {"badPaths": r3.get("badPaths"), "mine": mine(r3)}
    if r3.get("badPaths") != 0 or mine(r3).get("paths") != 1:
        fails.append("3 pref off: badPaths %s, strand %s" % (r3.get("badPaths"), mine(r3)))
    call("jawa/set_roof_batch", ops="None:%d,%d,1,1" % (px, pz)); settle()
    r4 = probe("strands:" + R(SITE)); s4 = mine(r4); log["4_prefOff_open"] = s4
    if not (s4.get("printedStatic") and not s4.get("dynamic") and not s4.get("pinRoofed")):
        fails.append("4 unroofed, pref off: want static only, got %s" % s4)
    pref(True); settle()
    r5 = probe("strands:" + R(SITE)); s5 = mine(r5); log["5_prefOn_open"] = {"badPaths": r5.get("badPaths"), "mine": s5}
    if not (s5.get("dynamic") and not s5.get("printedStatic")) or r5.get("badPaths") != 0:
        fails.append("5 pref on again: want dynamic only and badPaths 0, got %s badPaths %s" % (s5, r5.get("badPaths")))
except SystemExit:
    pass
finally:
    pref(str(was) == "True")
    probe("defaults")
for kk, v in log.items():
    print(kk, json.dumps(v)[:700])
print("PASS" if not fails else "FAIL: " + "; ".join(fails))
sys.exit(1 if fails else 0)
