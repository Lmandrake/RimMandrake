"""probe.py cmd ...: GimmeSomeSlackProbe commands (or a: AerialProbe ones), each result printed. python.exe."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"); sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(REPO, "src", "RimMandrake", "Utils")]
import validation_aerial as VA
B = VA.A()
for c in sys.argv[1:]:
    print(json.dumps(B.ap(c[2:]) if c.startswith("a:") else B.probe(c)))
