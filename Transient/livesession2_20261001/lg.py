"""python3 lg.py mark NAME | python3 lg.py since NAME [pattern...]  -- Player.log slice since a named mark"""
import sys, json, os, re
L = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
M = os.path.join(os.path.dirname(os.path.abspath(__file__)), "marks.json")
marks = json.load(open(M)) if os.path.exists(M) else {}
lines = open(L, encoding="utf-8", errors="replace").read().splitlines()
if sys.argv[1] == "mark":
    marks[sys.argv[2]] = len(lines); json.dump(marks, open(M, "w")); print(sys.argv[2], len(lines))
else:
    sl = lines[marks[sys.argv[2]]:]
    print("lines since", sys.argv[2], len(sl))
    for p in sys.argv[3:]:
        print(sum(1 for l in sl if p in l), "|", p)
    if len(sys.argv) == 3:
        for i, l in enumerate(sl):
            if re.search(r"Exception|^Error|error in GenStep|Could not", l): print(i, l[:220])
