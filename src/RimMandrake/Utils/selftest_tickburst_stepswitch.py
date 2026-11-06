"""TICKBURST_PROVE_MANY_TICKS_ONE_FRAME acceptance 6/9 groundwork offline: the --step {play,step,safe} switch.
tickburst_step.Stepper re-reads ticksGame and reports ok only when the clock moved exactly (play: reached its target);
each of the three proofs routes its direct clock steps through it and resolves its default from the adoption record
(acceptance 9: `gate` = clockgate.advance_chunk once adopted, `step` with no record or not adopted), and
FlowWorks v2 keeps the flyer landing step (FLYER_LAND_TICKS) on step_game_ticks; lines_proof and validation_v2 still pass
their own --mock runs with the switch in place."""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import tickburst_step as TS  # noqa: E402
import tickburst_bench as TB  # noqa: E402

fails = []


def check(ok, name, why=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", name, why))
    if not ok:
        fails.append(name)


for mode, budget, cap in (("step", 40, 0), ("safe", 40, 0), ("safe", 200, 0), ("safe", 200, 61)):
    g = TB.MockGame()
    r = TS.Stepper(g, mode, budget, cap, log_path="").advance(600)
    check(r["ok"] and r["moved"] == 600, "stepper_%s_%g_%d_exact" % (mode, budget, cap), str(r.get("moved")))
g = TB.MockGame(faults=["short_safe"])
r = TS.Stepper(g, "safe", 40, 0, log_path="").advance(600)
check(not r["ok"] and r.get("unmeasured"), "stepper_short_run_not_ok")
TS.PLAY_POLL_S = 0.0
r = TS.Stepper(TB.MockGame(), "play", log_path="").advance(30)
check(r["ok"] and r["moved"] >= 30 and r["overshoot"] >= 0 and r["readback"]["ultraSpeedBoost"] is False, "stepper_play_reaches_target",
      str(r))
TS.PLAY_STALL_S = 0.05
r = TS.Stepper(TB.MockGame(faults=["stall_play"]), "play", log_path="").advance(30)
check(not r["ok"] and "did not move" in (r.get("unmeasured") or ""), "stepper_play_stall_unmeasured")
TS.PLAY_STALL_S = 5.0
r = TS.Stepper(lambda tool, **kw: {"success": True}, "step", log_path="").advance(10)
check(r["ok"] and r.get("clock") == "unread", "stepper_step_on_clockless_mock_keeps_old_behaviour")
import tempfile  # noqa: E402
log = os.path.join(tempfile.mkdtemp(prefix="tb_step_"), "tb_log.jsonl")
TS.Stepper(TB.MockGame(), "safe", log_path=log).advance(60)
check(os.path.exists(log) and open(log).read().count("\n") == 1, "stepper_appends_one_log_line")

proofs = {"lines": "src/RimMandrake/FlowWorks/northstar/lines_proof.py",
          "v2": "src/RimMandrake/FlowWorks/northstar/validation_v2.py",
          "glow": "src/RimMandrake/LuminousPigment/live_probes/lp_glowtank_seed_sow.py"}
for k, rel in proofs.items():
    src = open(os.path.join(REPO, rel), encoding="utf-8").read()
    direct = [m.start() for m in re.finditer(r'call\("rimworld/step_game_ticks"', src)]
    check("import tickburst_step as TS" in src and "TS.take_args(" in src, "%s_takes_step_args" % k)
    check(('proof="%s"' % k) in src, "%s_default_from_adoption_record" % k)
    if k == "v2":
        lines = [src[:i].count("\n") + 1 for i in direct]
        only_flyer = len(direct) == 1 and "FLYER_LAND_TICKS" in src[direct[0]:direct[0] + 120]
        check(only_flyer, "v2_only_flyer_landing_stays_direct", str(lines))
    else:
        check(not direct, "%s_no_direct_step_calls" % k, str(len(direct)))
import json  # noqa: E402
d = tempfile.mkdtemp(prefix="tb_adopt_")
none, rec = os.path.join(d, "absent.json"), os.path.join(d, "adoption.json")
json.dump({"proofs": {"lines": {"adopt": True}, "v2": {"adopt": False}}}, open(rec, "w"))
saved = {k: os.environ.pop(k, None) for k in (TS.ENV_MODE, TS.ENV_ADOPTION)}
try:
    os.environ[TS.ENV_ADOPTION] = none
    check(TS.take_args([], proof="lines")[1]["mode"] == "step" and TS.take_args([])[1]["mode"] == "step", "no_record_default_is_step")
    os.environ[TS.ENV_ADOPTION] = rec
    check(TS.take_args([], proof="lines")[1]["mode"] == "gate" and TS.take_args([], proof="v2")[1]["mode"] == "step"
          and TS.take_args([], proof="glow")[1]["mode"] == "step", "record_adopts_only_matched_proofs")
    os.environ[TS.ENV_MODE] = "safe"
    check(TS.take_args([], proof="lines")[1]["mode"] == "safe", "env_mode_overrides_record")
finally:
    for k, v in saved.items():
        os.environ.pop(k, None)
        if v is not None:
            os.environ[k] = v
r = TS.Stepper(TB.MockGame(), "gate", log_path="").advance(600)
check(r["ok"] and r["moved"] == 600 and r["reply"].get("path") == "safe_advance", "stepper_gate_exact_via_clockgate", str(r.get("reply")))
for k in ("lines", "v2"):
    for mode in ("step", "gate"):
        p = subprocess.run([sys.executable, os.path.join(REPO, proofs[k]), "--mock", "--step", mode], cwd=REPO,
                           capture_output=True, text=True, timeout=400, env=dict(os.environ, TICKBURST_STEP=""))
        check(p.returncode == 0, "%s_mock_passes_%s" % (k, mode), (p.stdout[-300:] + p.stderr[-300:]).replace("\n", " | "))
print("RESULT: %s" % ("PASS" if not fails else "FAIL %d" % len(fails)))
sys.exit(1 if fails else 0)
