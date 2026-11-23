"""Print each finished chain's own component verdicts (python3, offline): peek.py [label ...]"""
import json, os, re, sys, glob
E = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "evidence")
labs = sys.argv[1:] or sorted(os.path.basename(p)[4:-5] for p in glob.glob(os.path.join(E, "pv6_*.json")))
for lab in labs:
    p = os.path.join(E, "pv6_%s.json" % lab)
    if not os.path.exists(p):
        print("%-34s (no result)" % lab); continue
    d = json.load(open(p))
    log = open(os.path.join(E, "run_%s.log" % lab), errors="replace").read() if os.path.exists(os.path.join(E, "run_%s.log" % lab)) else ""
    own = [c for c in d.get("components", []) if "skipped" not in str(c.get("name"))]
    det = {}
    for ln in log.splitlines():
        m = re.match(r"component ([^:]+): (\{.*)", ln)
        if m:
            try: det[m.group(1)] = json.loads(m.group(2)).get("detail")
            except ValueError: pass
    print("%-34s %s" % (lab, " ".join("%s=%s" % (c["name"], c["verdict"]) for c in own) or ("refused: %s" % d.get("refused"))))
    for c in own:
        if c["verdict"] != "PASS":
            print("    %s: %s" % (c["name"], str(det.get("%s/%s" % (c.get("chain"), c["name"])))[:400]))
