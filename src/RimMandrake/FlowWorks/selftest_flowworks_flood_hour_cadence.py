"""BRIDGE_FLOOD_FIX_RUNS_EVERY_THREE_HOURS: bridge flood damage is advertised per in-game hour, but its check sat
behind MapComponentTick's 60-tick gate as `now % 2500 == 0`, so it fired only every lcm(60, 2500) = 7500 ticks.
Offline: sweeps ten days of ticks through a Python port of RM_SuspensionMath.IsHourTick behind the same gate (one
fire per hour, none missed, none doubled), shows the old expression fails the same sweep, and pins that the C#
source holds that function and that MapComponentTick calls it behind the 60-tick gate."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MATH = os.path.join(HERE, "Source", "RM_SuspensionMath.cs")
COMP = os.path.join(HERE, "Source", "Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs")
TPH = 2500
GATE = 60


def is_hour_tick(now, gate):  # port of RM_SuspensionMath.IsHourTick
    g = max(1, gate)
    return (now % TPH) < g


def fires_per_hour(pred, days=10, gate=GATE):
    hours = {}
    for now in range(0, days * 24 * TPH, gate):  # only ticks that pass the 60-tick gate reach the check
        if pred(now):
            hours[now // TPH] = hours.get(now // TPH, 0) + 1
    return [hours.get(h, 0) for h in range(days * 24)]


def main():
    fails = []
    got = fires_per_hour(lambda n: is_hour_tick(n, GATE))
    if any(c != 1 for c in got):
        fails.append("IsHourTick behind the 60-tick gate: hours with %s fires" % sorted(set(got)))
    old = fires_per_hour(lambda n: n % TPH == 0)
    if sum(old) * 3 != len(old):  # can-fail: the instrument sees the defect it was filed for
        fails.append("sanity: the old expression should fire every third hour, fired %d of %d" % (sum(old), len(old)))
    for gate in (1, 7, 60, 250, 2500):
        c = fires_per_hour(lambda n, g=gate: is_hour_tick(n, g), days=2, gate=gate)
        if any(x != 1 for x in c):
            fails.append("gate %d: fires per hour %s" % (gate, sorted(set(c))))

    m = open(MATH, encoding="utf-8").read()
    fn = re.search(r"public static bool IsHourTick\(int now, int gate\)\s*\{(.*?)\n\t\t\}", m, re.S)
    if not fn:
        fails.append("RM_SuspensionMath.IsHourTick(int now, int gate) missing")
    else:
        body = re.sub(r"\s+", " ", fn.group(1))
        for want in ("int m = now % TicksPerHour;", "return m < g;"):
            if want not in body:
                fails.append("IsHourTick body lacks %r (the Python port no longer matches)" % want)
    c = open(COMP, encoding="utf-8").read()
    tick = c[c.index("public override void MapComponentTick()"):]
    gate_at = tick.find("now % 60 != 0")
    call_at = tick.find("RM_SuspensionMath.IsHourTick(now, 60)")
    flood_at = tick.find("RM_SuspensionWaters.FloodHour(map, bridges)")
    if gate_at < 0 or call_at < 0 or not (gate_at < call_at < flood_at):
        fails.append("MapComponentTick must gate FloodHour on IsHourTick(now, 60) after the 60-tick gate")
    if "now % RM_SuspensionMath.TicksPerHour == 0" in tick:
        fails.append("MapComponentTick still holds the every-7500-ticks check")

    for f in fails:
        print("FAIL", f)
    print("selftest_flowworks_flood_hour_cadence:", "FAIL" if fails else "PASS (240 hours, 1 fire each; old = every 3rd)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
