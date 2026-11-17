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
import validation_core as vc  # noqa: E402

SAVE = "GSS_OWNER_LOOK_20261116"
PROBE = "RimMandrake.GimmeSomeSlack.GimmeSomeSlackProbe"


def probe_of(B, cmd, wait_s=60.0):
    """Post cmd to GimmeSomeSlackProbe through validation_core's probe_of (jawa/mod_settings_fields). Never the single-field
    `mod_settings_field set`: the companion refuses it for a probe class (not a Settings class), and a refused post used to
    be read as "the mod stopped answering after the save loaded" (measured 2026-11-16, selftest_live_stub_joins_probe.py)."""
    return B.probe_of(PROBE, cmd, wait_s, 0.3)


def main(argv, bridge=None):
    B = bridge if bridge is not None else vc.Bridge()

    def call(tool, **kw):
        return B.call(tool, **kw)

    def probe(cmd, wait_s=60.0):
        return probe_of(B, cmd, wait_s)

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
        and r.get("empty") == 0 and r.get("liveOffSlope") == 0 and r.get("livePinched") == 0 and r.get("wallTerminalsLoose") == 0 \
        and r.get("liveUnlaid", 0) == 0   # a live end the lay could not place (absent on a build before the field: not read)
    out = {"row": "sc_stub_joins", "result": "PASS" if ok else "FAIL", "save": SAVE if "--load" in argv else "(map on screen)",
           "rect": rect, "probe": r, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if "--out" in argv:
        with open(argv[argv.index("--out") + 1], "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
    print(json.dumps({k: r.get(k) for k in ("success", "error", "stubs", "taken", "offLine", "offSlope", "empty", "byKind", "liveTails",
                                            "liveOffSlope", "livePinched", "liveUnlaid", "liveStill", "wallTerminalsLoose", "bad")}, indent=1))
    print("sc_stub_joins", out["result"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
