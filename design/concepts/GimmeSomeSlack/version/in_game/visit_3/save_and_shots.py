"""save_and_shots.py <savename|-> rect:name ... : keeper save (Saves stat) then the game's render of each rect. python.exe."""
import os, sys, shutil, json
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"); sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(REPO, "src", "RimMandrake", "Utils")]
import validation as V, validation_aerial as VA
from modcheck import reviewmap as RM
B = VA.A(); OUT = r"D:\ClaudeWork\rimmandrake\scratch\gss_020_v3\shots"
if sys.argv[1] != "-":
    print(json.dumps(RM.save_keeper(B, sys.argv[1], saves=V.SAVES), default=str)[:600])
for a in sys.argv[2:]:
    r, n = a.split(":"); r = tuple(int(v) for v in r.split(","))
    V.frame_fit(B, r); log = []
    d = V.shot(B, n, r, log); print(n, d)
    if d and os.path.exists(str(d)): shutil.copy(str(d), os.path.join(OUT, n + ".png"))
