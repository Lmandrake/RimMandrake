"""sc_stub_joins (RIMMANDRAKE_BIND_SLACK_STUB_ANGLE_RULE_FOURTH_ASK, owner 2026-11-16): the position-and-slope rule read from the RUNNING game.

"The position-slope rule should be hard wired into the mod and be part of its acceptance checks." On his review map (save
GSS_OWNER_LOOK_20261116, human_review.py's stations), the probe "joins:" runs the same instrument as the offline sweep
(Core/StubJoinAudit.cs; SelfTest/StubJoinChecks.cs) on the live pieces: every cord on a stubbed piece on the stub's line and slope,
no bare stub, the live end continuing its cord over its frames, no loose or sparking end on a wall or rock dead end.

    python.exe src\\RimMandrake\\GimmeSomeSlack\\northstar\\live_stub_joins.py [--load] [--rect x,z,w,h] [--out result.json]

--load loads the save first (else the map on screen is read). Game up on the gimmesomeslack tier, bridge held. Exit 0 = PASS.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

SAVE = "GSS_OWNER_LOOK_20261116"
PROBE = "RimMandrake.GimmeSomeSlack.GimmeSomeSlackProbe"


def main(argv):
    h, p, t = rb.resolve_endpoint()
    S = rb.RimBridge(host=h, port=p, token=t, timeout=240.0)
    S.connect()

    def call(tool, **kw):
        r = S.call(tool, kw) or {}
        return json.loads(r["content"][0]["text"]) if isinstance(r, dict) and r.get("content") else r

    def probe(cmd, wait_s=60.0):
        before = call("jawa/mod_settings_field", typeName=PROBE, action="get", field="serial").get("value")
        call("jawa/mod_settings_field", typeName=PROBE, action="set", field="request", value=cmd)
        t0 = time.time()
        while time.time() - t0 < wait_s:
            if call("jawa/mod_settings_field", typeName=PROBE, action="get", field="serial").get("value") != before:
                res = call("jawa/mod_settings_field", typeName=PROBE, action="get", field="result").get("value")
                try:
                    return json.loads(res)
                except (TypeError, ValueError):
                    return {"success": False, "raw": res}
            time.sleep(0.3)
        return {"success": False, "error": "probe timed out"}

    if "--load" in argv:
        print("load:", str(call("rimworld/load_game_ready", saveName=SAVE))[:200], flush=True)
    rect = argv[argv.index("--rect") + 1] if "--rect" in argv else "0,0,400,400"
    probe("poll")
    probe("rebuild")
    for _ in range(3):
        call("rimworld/step_game_ticks", ticks=2, pauseFirst=True, timeoutMs=60000)
        time.sleep(0.5)
    r = probe("joins:" + rect)
    ok = bool(r.get("success")) and (r.get("taken") or 0) >= 20 and r.get("offLine") == 0 and r.get("offSlope") == 0 \
        and r.get("empty") == 0 and r.get("liveOffSlope") == 0 and r.get("livePinched") == 0 and r.get("wallTerminalsLoose") == 0
    out = {"row": "sc_stub_joins", "result": "PASS" if ok else "FAIL", "save": SAVE if "--load" in argv else "(map on screen)",
           "rect": rect, "probe": r, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if "--out" in argv:
        with open(argv[argv.index("--out") + 1], "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
    print(json.dumps({k: r.get(k) for k in ("success", "error", "stubs", "taken", "offLine", "offSlope", "empty", "byKind", "liveTails",
                                            "liveOffSlope", "livePinched", "wallTerminalsLoose", "bad")}, indent=1))
    print("sc_stub_joins", out["result"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
