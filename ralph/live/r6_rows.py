"""Round 6: print the unforced bend rows of a lab out.json with the strand around each apex. python3 ralph/live/r6_rows.py OUT.json [maxFromEnd]"""
import json, math, sys
d = json.load(open(sys.argv[1])); mx = float(sys.argv[2]) if len(sys.argv) > 2 else 99
pieces = {(p["a"], p["b"]): p for p in d["pieces"]}
for r in d["bends"]["rows"]:
    if r["why"] != "unforced" or r["fromEnd"] > mx: continue
    a, b = r["piece"].split("|")
    p = next((q for q in d["pieces"] if q["a"].startswith(a) and q["b"].startswith(b)), None)
    print("ROW", r["piece"], "apex", r["x"], r["z"], "turn", r["turn"], "sharp", r["sharp"], "fromEnd", r["fromEnd"])
    if not p: continue
    for s in p["strands"]:
        best = min(range(len(s)), key=lambda i: math.hypot(s[i][0]-r["x"], s[i][1]-r["z"]))
        if math.hypot(s[best][0]-r["x"], s[best][1]-r["z"]) > 0.3: continue
        lo, hi = max(0, best-14), min(len(s), best+15)
        print("  strand n=%d apex_i=%d pts:" % (len(s), best), " ".join("(%.2f,%.2f)" % tuple(q) for q in s[lo:hi:2]))
        print("  first/last:", s[0], s[-1])
    print("  decals:", p.get("decals"))
    for q in d["pieces"]:
        for dc in q.get("decals", []):
            if dc[0] == "PowerStrip" and abs(dc[1]-r["x"]) < 3 and abs(dc[2]-r["z"]) < 3: print("  strip", dc)
