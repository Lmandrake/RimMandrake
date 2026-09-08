import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

LONGITUDE = 19.3762436

with rb() as b:
    c = b.call("jawa/time_clock", {})
    print("CLOCK:", json.dumps({k: v for k, v in c.items() if k != "operation"})[:400])
    tg = c["ticksGame"] if "ticksGame" in c else c.get("TicksGame")
    ta = c.get("ticksAbs", c.get("TicksAbs"))
    off = ta - tg                                   # abs = game + off
    lon_ticks = LONGITUDE / 15.0 * 2500.0
    # want local hour 12  ->  (abs + lon_ticks) % 60000 == 12*2500
    cur = (ta + lon_ticks) % 60000
    want = 12 * 2500
    delta = int(round((want - cur) % 60000))
    newtg = tg + delta
    r = b.call("jawa/time_set_ticks", {"ticks": newtg})
    print("SET:", json.dumps({k: v for k, v in r.items() if k != "operation"})[:400])
    c2 = b.call("jawa/time_clock", {})
    ta2 = c2.get("ticksAbs", c2.get("TicksAbs"))
    print("new local hour:", ((ta2 + lon_ticks) % 60000) / 2500.0)
