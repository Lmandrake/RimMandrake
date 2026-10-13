"""Probe D (WATCH_WAIT_WIRE_SMALL_STEPS): the harness's governed step stops on a latched trigger and the governor
judges the row as a disturbance, not a FAIL. One colonist's Food set to 0 (Starving category, harmless for minutes),
then a 2000-tick governed step through suite.wait_ticks' own primitive (clockgate.advance_chunk); Food restored after."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("src/RimMandrake/Utils", "src/RimMandrake/Utils/modcheck"):
    sys.path.insert(0, os.path.join(HERE, *p.split("/")))
import clockgate as cg  # noqa: E402
import governor as G  # noqa: E402
from northstar_driver.session import FastSession  # noqa: E402

OUT = {}
s = FastSession(strict=False)
with s:
    pawns = s.call("jawa/list_pawns", faction="player", limit=20).get("pawns") or []
    pid = pawns[0]["id"]
    num = int("".join(ch for ch in str(pid) if ch.isdigit()))
    c = G.RowContract("probe_d_starve", about=("mechanism",), actors=(num,), budget_ticks=5000)
    gov = G.RowGovernor(s, c, log=lambda m: OUT.setdefault("log", []).append(m))
    OUT["arm"] = gov.arm(ttl_min=20).get("success")
    t0 = s.call("jawa/time_clock").get("ticksGame")
    OUT["food0"] = s.call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=0.0).get("success")
    try:
        OUT["executed"] = cg.advance_chunk(s, 2000)
        OUT["stopped"] = False
    except cg.GovernorStop as e:
        OUT["stopped"] = True
        OUT["stop"] = {"msg": str(e), "surprise": e.is_surprise_abort, "stopBy": e.result.get("stopBy"),
                       "executed": e.result.get("executed")}
    OUT["moved"] = s.call("jawa/time_clock").get("ticksGame") - t0
    v = gov.verdict(G.PASS)
    OUT["verdict"] = {k: v.get(k) for k in ("outcome", "validity", "reasons", "env_items")}
    for need in ("Food", "Rest"):
        s.call("jawa/pawn_need", pawn=pid, action="need", need=need, level=1.0)
    gov.disarm()
    OUT["paused"] = s.call("jawa/time_clock").get("paused")
print(json.dumps(OUT, indent=1, default=str)[:4000])
with open(os.path.join(HERE, "probe_d.json"), "w") as f:
    json.dump(OUT, f, indent=1, default=str)
