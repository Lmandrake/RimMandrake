"""close_shots.py <root> x,z,w,h:name ... : labels hidden, closest zoom, one capture each. python.exe."""
import os, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"); sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(REPO, "src", "RimMandrake", "Utils")]
import validation as V, validation_aerial as VA
B = VA.A(); OUT = r"D:\ClaudeWork\rimmandrake\scratch\gss_020_v2\shots"; root = float(sys.argv[1])
print(str(B.call("jawa/review_label", action="hide"))[:120]); B.call("jawa/clear_ui")
try:
    for a in sys.argv[2:]:
        r, n = a.split(":"); r = tuple(int(v) for v in r.split(","))
        B.call("rimworld/jump_camera_to_cell", x=r[0] + r[2] // 2, z=r[1] + r[3] // 2)
        B.call("rimworld/set_camera_zoom", rootSize=root)
        log = []; d = V.shot(B, n, r, log, pad=0, root=root); print(n, d)
        if d and os.path.exists(str(d)): shutil.copy(str(d), os.path.join(OUT, n + ".png"))
finally:
    print(str(B.call("jawa/review_label", action="show"))[:120])
