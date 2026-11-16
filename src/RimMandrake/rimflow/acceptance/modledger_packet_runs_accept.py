#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_START_PILOT_STAGE_RUNS_FROM_LEDGER_PACKET (plan
design/plans/2026-11-15-holder-pipeline-fusion-build.md step 5; spec §3.1 "the launcher records each run", §3.3, §3.4).
Written by the filing seat; the builder does not edit it (a wrong clause goes to the Conductor).

    python3 src/RimMandrake/rimflow/acceptance/modledger_packet_runs_accept.py      # "PASS 10/10" when built

THE CONTRACT (offline, on a temp root; no claude is started):
  modledger.json `pilot_mods` lists ExplosiveKnockback, GimmeSomeSlack and FlowWorks (his card 2026-11-15: all three).
  modledger.launch(root, mod, lease, role) -> {"token", "run", "brief"}: grants `lease` (its token above every earlier
    one), appends a DISPATCH `run.start` whose body names the lease, the role and packet_tokens, and returns a brief
    that begins with the mod's packet text (the run starts from the ledger, not from ticket prose). The run.start body
    names the `stage` the ledger is at now (his plan change 2026-11-16T05:57:46Z: "It should roughly start where it
    last was in the pipeline"; never a restart from stage 1).
  modledger.end_run(root, mod, run, status) -> [flags]: appends a DISPATCH `run.end` with the status and the flags; the
    flags hold "NO_CHECKPOINT" when that run's holder wrote no session.checkpoint with non-empty done, next and
    ruled_out after its run.start, and are empty when it did.
  The dispatcher launches pilot-mod stage runs through it: src/RimMandrake/rimflow/maturation_dispatch.py calls
    modledger.launch( and modledger.end_run(.
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
sys.path.insert(0, RIMFLOW)
import modledger as M                                            # noqa: E402

res = []


def check(name, ok, detail=""):
    res.append(bool(ok))
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))


def attempt(fn):
    try:
        return fn(), None
    except Exception as e:                       # noqa: BLE001 — an unbuilt contract is a FAIL, not a crash
        return None, "%s: %s" % (type(e).__name__, e)


check("pilot_mods names all three", set(M.config().get("pilot_mods") or []) >=
      {"ExplosiveKnockback", "GimmeSomeSlack", "FlowWorks"}, M.config().get("pilot_mods"))
root = tempfile.mkdtemp(prefix="ml_runs_acc_")
MOD = "AccMod"
os.makedirs(os.path.join(root, "design", "concepts", MOD))
M.append(root, MOD, "DISPATCH", "version.open", "version", body={"version": "0.1.0"}, version="0.1.0")
M.append(root, MOD, "DISPATCH", "stage.enter", "stage", body={"stage": "blind_challenge"})
M.grant(root, MOD, lease="EARLY")
out, err = attempt(lambda: M.launch(root, MOD, "L1", "builder"))
check("launch returns token, run and brief", isinstance(out, dict) and {"token", "run", "brief"} <= set(out), err or out)
out = out or {}
check("the new lease's token is above every earlier one", out.get("token") == 2, out.get("token"))
evs = M.read(root, MOD)
rs = [e for e in evs if e.get("kind") == "run.start" and e.get("writer") == "DISPATCH"]
check("a DISPATCH run.start names the lease, role and packet size", rs and rs[-1]["body"].get("lease") == "L1" and
      rs[-1]["body"].get("role") == "builder" and isinstance(rs[-1]["body"].get("packet_tokens"), int), rs[-1:])
check("the run starts at the stage the ledger is at, not stage 1", rs and rs[-1]["body"].get("stage") == "blind_challenge",
      rs[-1:])
check("the brief begins with the packet", str(out.get("brief", "")).startswith("# %s — mod ledger packet" % MOD),
      str(out.get("brief", ""))[:80])
flags, err = attempt(lambda: M.end_run(root, MOD, out.get("run"), "ok"))
check("a run that wrote no checkpoint is flagged NO_CHECKPOINT", flags is not None and "NO_CHECKPOINT" in flags,
      err or flags)
out2, err = attempt(lambda: M.launch(root, MOD, "L2", "builder"))
if out2:
    M.append(root, MOD, "HOLDER.L2", "session.checkpoint", "checkpoint", token=out2["token"],
             body={"done": "built", "next": "judge", "ruled_out": "the tick cause"})
flags2, err2 = attempt(lambda: M.end_run(root, MOD, (out2 or {}).get("run"), "ok"))
check("a run that wrote a full checkpoint ends with no flags", flags2 == [], err or err2 or flags2)
check("run.end is recorded with its status", any(e.get("kind") == "run.end" and e["body"].get("status") == "ok"
                                                 for e in M.read(root, MOD)))
src = open(os.path.join(RIMFLOW, "maturation_dispatch.py"), encoding="utf-8").read()
check("the dispatcher launches and ends pilot runs through the ledger", "modledger.launch(" in src and
      "modledger.end_run(" in src)
shutil.rmtree(root, ignore_errors=True)
print("PASS %d/%d" % (sum(res), len(res)) if all(res) else "FAIL %d of %d" % (res.count(False), len(res)))
sys.exit(0 if all(res) else 1)
