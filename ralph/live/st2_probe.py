"""ST2 diagnosis: what the overhead span's texture is before and after each style switch, on the loaded proof site.
python.exe ralph/live/st2_probe.py"""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.getcwd(), "ralph", "live"))
import lived_in as LI  # noqa: E402
R = LI.Run()
B = R.B
def show(tag):
    sp = B.probe("styles")
    print(tag, "current", sp.get("currentKey"), "built", sp.get("builtKey"), "span", sp.get("aerialSpanTex"), "strand", sp.get("strandTex"), "rebuilds", sp.get("rebuilds"))
show("start")
for st in ["Cybertek", "StarWarsJawa", "StarWars", "StarWarsJawa", "ExtensionCord", "StarWarsJawa"]:
    B.probe("set:style=%s" % st)
    B.ticks(1)
    time.sleep(0.5)
    show("after " + st)
    time.sleep(2)
    show("   +2s " + st)
