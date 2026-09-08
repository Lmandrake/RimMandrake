import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

for i in range(60):
    try:
        with rb() as b:
            lp = b.call("jawa/list_pawns", {"limit": 3})
        n = lp.get("totalOnMap")
        print(i, "totalOnMap", n, lp.get("message"))
        if n and n > 40:
            break
    except Exception as e:
        print(i, "poll", type(e).__name__, str(e)[:90])
    time.sleep(10)
