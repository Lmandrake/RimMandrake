#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_RESUME_HOLDER_SESSIONS_TO_400K_KILL_AND_RESUME (plan
design/plans/2026-11-15-holder-pipeline-fusion-build.md step 6; spec §3.4, Option B; his card 2026-11-15: "Resumed
session per mod" and "Try 400k first."). Written by the filing seat; the builder does not edit it.

    python3 src/RimMandrake/rimflow/acceptance/modledger_resume_accept.py      # "PASS 8/8" when built

THE CONTRACT (offline, temp root, no claude started; the live half, a real resumed detached systemd run, is the item's
own live test and stays UNRUN until it runs):
  modledger.resume_plan(root, mod) -> {"action": "packet"|"resume"|"rotate", "session_id", "reconcile": bool, "why"}
    - no holder session.id recorded                       -> "packet"
    - last session.id under holder_context_ceiling_tokens  -> "resume", with that session_id
    - at or over the ceiling (read from modledger.json at call time, never a literal) -> "rotate"
    - the last DISPATCH run.end has status "killed" or "lost" -> reconcile True (clone, unpublished commits, bridge are
      reconciled before anything resumes)
    - a version.open of the next Design Version does not end the holder: still "resume", same session_id
  The packet a rotating holder starts from still lists the refuted cause and his answer (nothing it must not chase or
  re-ask is lost at rotation).
  The dispatcher resumes through it: src/RimMandrake/rimflow/maturation_dispatch.py calls modledger.resume_plan( and
  passes "--resume".
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


def plan(root, mod):
    try:
        return M.resume_plan(root, mod), None
    except Exception as e:                       # noqa: BLE001 — an unbuilt contract is a FAIL
        return {}, "%s: %s" % (type(e).__name__, e)


root = tempfile.mkdtemp(prefix="ml_resume_acc_")
MOD = "AccMod"
os.makedirs(os.path.join(root, "design", "concepts", MOD))
M.append(root, MOD, "DISPATCH", "version.open", "version", body={"version": "0.1.0"}, version="0.1.0")
p, err = plan(root, MOD)
check("no session recorded: start from the packet", p.get("action") == "packet", err or p)
tok = M.grant(root, MOD, lease="H1")
M.append(root, MOD, "HOLDER.H1", "cause.refuted", "C_TICK", token=tok, body={"text": "not the tick"})
M.append(root, MOD, "OWNER", "question.answer", "Q_R", body={"text": "radius 4"}, authority={"owner_said": "radius 4"})
M.append(root, MOD, "HOLDER.H1", "session.id", "session", token=tok, body={"session_id": "s-1", "context_tokens": 120000})
p, err = plan(root, MOD)
check("under the ceiling: resume that session", p.get("action") == "resume" and p.get("session_id") == "s-1", err or p)
M.append(root, MOD, "DISPATCH", "run.end", "run", body={"status": "killed", "run": "r1"})
p, err = plan(root, MOD)
check("after a killed run: reconcile before resuming", p.get("reconcile") is True, err or p)
M.append(root, MOD, "DISPATCH", "version.open", "version", body={"version": "0.2.0"}, version="0.2.0")
p, err = plan(root, MOD)
check("the next Design Version keeps the same holder session", p.get("action") == "resume" and
      p.get("session_id") == "s-1", err or p)
ceiling = M.config()["holder_context_ceiling_tokens"]
M.append(root, MOD, "HOLDER.H1", "session.id", "session", token=tok,
         body={"session_id": "s-1", "context_tokens": ceiling})
p, err = plan(root, MOD)
check("at the configured ceiling: rotate", p.get("action") == "rotate", err or p)
M.config()["holder_context_ceiling_tokens"] = ceiling * 2
p, err = plan(root, MOD)
check("the ceiling is read from the config at call time", p.get("action") == "resume", err or p)
M.config()["holder_context_ceiling_tokens"] = ceiling
txt, _ = M.packet(root, MOD)
check("the rotating holder's packet keeps the refuted cause and his answer", "C_TICK" in txt and "radius 4" in txt)
src = open(os.path.join(RIMFLOW, "maturation_dispatch.py"), encoding="utf-8").read()
check("the dispatcher resumes through resume_plan with --resume", "modledger.resume_plan(" in src and "--resume" in src)
shutil.rmtree(root, ignore_errors=True)
print("PASS %d/%d" % (sum(res), len(res)) if all(res) else "FAIL %d of %d" % (res.count(False), len(res)))
sys.exit(0 if all(res) else 1)
