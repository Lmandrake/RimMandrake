"""probe_conv_mult.py -- does RM_MachinerySettings.converterRateMultiplier keep a value set over the bridge while governed
chunks run (sc_garden's window)? Prints ticksGame and the value after each chunk, then restores the prior.
    python.exe -u design/concepts/FlowWorks/version/in_game/visit_8/probe_conv_mult.py <chunks> <chunk_ticks> [pre_ticks]
pre_ticks: advance this much before the set (one-shot trigger at a fixed tick after load, or periodic?)"""
import os, sys, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
import validation_core as vc  # noqa: E402
MACH = 'RimMandrake.FlowWorks.Machinery.RM_MachinerySettings'
B = vc.Bridge()
B.stop_on = "none" if os.environ.get("PROBE_NOSTOP") else B.stop_on
def get():
    r = B.call('jawa/mod_settings_field', typeName=MACH, field='converterRateMultiplier', action='get')
    return r.get('value'), r.get('ticksGame')
n, step = int(sys.argv[1]), int(sys.argv[2])
pre = int(sys.argv[3]) if len(sys.argv) > 3 else 0
if pre:
    B.ticks(pre)
prior = get()[0]
B.call('jawa/mod_settings_field', typeName=MACH, field='converterRateMultiplier', action='set', value='4.1')
seen = [get()]
print("set", seen[0], flush=True)
try:
    for i in range(n):
        B.ticks(step)
        seen.append(get())
        print(i, seen[-1], flush=True)
        if str(seen[-1][0]) != '4.1':
            break
finally:
    B.call('jawa/mod_settings_field', typeName=MACH, field='converterRateMultiplier', action='set', value=str(prior))
print(json.dumps({"prior": prior, "pre": pre, "seen": seen, "kept": all(str(v[0]) == '4.1' for v in seen)}))
