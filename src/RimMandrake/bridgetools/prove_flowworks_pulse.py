"""Live proof for the FlowWorks Northstar v2 owed tools (plan
design/RimMandrake/flowworks_northstar_script_plan_2026-10-02.md section 8, items 1-3):
jawa/flowworks_pulse, jawa/flowworks_excavation_rect, jawa/flowworks_pit_report.

Run under Windows python.exe against a live bridge whose mod list carries FlowWorks
(modset_builder tier `flowworks`). Starts a debug quicktest map if none is up.

Checks (each prints PASS/FAIL; exit 1 on any FAIL):
  P1  refusal path: count=0 and count=501 fail and run nothing
  P2  a 1x4 D=1 strip with F=1 at its west end; 3 pulses at 0 ticks:
      pulsesRun==3, ticksGame unchanged, nextPulseTick untouched, pulse-0 vector == [1,0,0,0]
  P3  second instrument: excavation_rect over the strip == the last pulse vector
  P4  engine toggle OFF -> pulse REFUSED (setting restored in finally)
  P5  pit_report: a D=4 cell has a holder (0 occupants); a D=1 strip cell has none
Each pulse's vector is printed so the flow itself can be eyeballed against the oracle.
"""
_RM_ROOT = __import__("pathlib").Path(__file__).resolve().parents[3]
import json
import sys
import time

sys.path.insert(0, str(_RM_ROOT / "src" / "RimMandrake" / "Utils"))
import rimbridge_client as rb  # noqa: E402

SETTINGS = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
S.connect()
FAILS = []


def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  " + str(detail)[:600]))
    if not ok:
        FAILS.append(name)


if call("rimworld/get_ui_state").get("programState") != "Playing":
    call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
    for _ in range(120):
        if call("rimworld/get_ui_state").get("programState") == "Playing":
            break
        time.sleep(1)

eng = call("jawa/flowworks_engine_state")
if not eng.get("success"):
    sys.exit("FlowWorks engine not reachable: %r" % eng)

# Find a dry, undug 1x5 strip (4 channel cells + a D=4 cell) near the map centre.
info = call("jawa/map_info")
cx, cz = (info.get("sizeX") or info.get("size", {}).get("x") or 250) // 2, (info.get("sizeZ") or info.get("size", {}).get("z") or 250) // 2
rect = call("jawa/flowworks_excavation_rect", x=cx - 15, z=cz - 15, w=30, h=30)
check("rect read on the search area", rect.get("success") and rect.get("cellsScanned") == 900, rect)
ok_cells = {(r["x"], r["z"]) for r in rect.get("rows", [])
            if r["d"] == 0 and r["f"] == 0 and not r["isSource"] and "Water" not in (r.get("terrain") or "")}
strip = None
for z in range(cz - 15, cz + 15):
    for x in range(cx - 15, cx + 9):
        if all((x + i, z) in ok_cells for i in range(6)):
            strip = [(x + i, z) for i in range(4)]
            deep = (x + 5, z)          # one dry gap cell between the strip and the D=4 cell
            break
    if strip:
        break
if not strip:
    sys.exit("no undug dry 1x6 strip near the centre - use a fresh map")

# P1 refusal path
for bad in (0, 501):
    r = call("jawa/flowworks_pulse", count=bad)
    check("P1 count=%d refused" % bad, r.get("success") is False, r)

# P2 strip + 3 pulses
for i, (x, z) in enumerate(strip):
    r = call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=1, setFill=1 if i == 0 else -1)
    check("P2 drive %s" % ((x, z),), r.get("success") and r.get("depth") == 1, r)
for _ in range(4):
    call("jawa/flowworks_excavation_drive", x=deep[0], z=deep[1], deepenLevels=1, setFill=-1)
p = call("jawa/flowworks_pulse", count=3, x=strip[0][0], z=strip[0][1], w=4, h=1)
check("P2 pulse call", p.get("success"), p)
pulses = p.get("pulses") or []
for row in pulses:
    print("   pulse %d  F=%s  D=%s  sumF=%s changed=%s" % (row["pulse"], row["fill"], row["depth"], row["sumFill"], row["cellsFillChanged"]))
check("P2 pulsesRun==3 and 4 records", p.get("pulsesRun") == 3 and len(pulses) == 4, p.get("pulsesRun"))
check("P2 zero ticks spent", p.get("ticksBefore") == p.get("ticksGame"), (p.get("ticksBefore"), p.get("ticksGame")))
check("P2 scheduler untouched", p.get("nextPulseTickUntouched") is True, p)
check("P2 pulse-0 vector == [1,0,0,0]", pulses and pulses[0]["fill"] == [1, 0, 0, 0], pulses[:1])
check("P2 something moved in 3 pulses", any(r["cellsFillChanged"] for r in pulses[1:]), pulses)

# P3 independent read
r = call("jawa/flowworks_excavation_rect", x=strip[0][0], z=strip[0][1], w=4, h=1)
check("P3 rect == last pulse vector", r.get("success") and pulses and [c["f"] for c in r["rows"]] == pulses[-1]["fill"],
      (r.get("rows"), pulses[-1:] if pulses else None))

# P4 engine OFF refuses
before = call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="depthEngineEnabled")
try:
    call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="depthEngineEnabled", value="False")
    r = call("jawa/flowworks_pulse", count=1)
    check("P4 engine OFF refused", r.get("success") is False and (r.get("details") or {}).get("refused") is True, r)
finally:
    call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="depthEngineEnabled",
         value=str(before.get("value", True)))
after = call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="depthEngineEnabled")
check("P4 toggle restored", str(after.get("value")) == str(before.get("value")), (before, after))

# P5 pit report
r = call("jawa/flowworks_pit_report", x=deep[0], z=deep[1])
check("P5 D=4 holder present, empty", r.get("success") and r.get("depthRaw") == 4 and r.get("holderPresent") is True
      and (r.get("holder") or {}).get("occupantCount") == 0, r)
r = call("jawa/flowworks_pit_report", x=strip[1][0], z=strip[1][1])
check("P5 D=1 no holder", r.get("success") and r.get("depthRaw") == 1 and r.get("holderPresent") is False, r)

print("\n%d FAIL(s): %s" % (len(FAILS), FAILS) if FAILS else "\nALL PASS")
sys.exit(1 if FAILS else 0)
