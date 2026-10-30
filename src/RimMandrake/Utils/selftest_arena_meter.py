#!/usr/bin/env python3
"""Selftest for per-arm metering (ARENA_METER_BUILD_SPEND_BY_CLONE_PATH): forced failures, all offline."""
import json, os, sys, tempfile, subprocess
from pathlib import Path
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "sim"))
import spend_census as S  # noqa: E402
import gpt_consult as G   # noqa: E402

fails = 0
def check(ok, name):
    global fails
    print(("PASS " if ok else "FAIL ") + name); fails += (not ok)

ROOT = "/home/mandrake/rm/arena"
T = tempfile.mkdtemp()
proj = os.path.join(T, "projects")
def transcript(slug, name, mid, out_tok, sub=False, model="claude-opus-4"):
    d = os.path.join(proj, slug, "sess", "subagents") if sub else os.path.join(proj, slug)
    os.makedirs(d, exist_ok=True)
    rec = {"type": "assistant", "timestamp": "2026-10-29T10:00:00Z", "isSidechain": sub,
           "message": {"id": mid, "model": model,
                       "usage": {"input_tokens": 100, "output_tokens": out_tok, "cache_read_input_tokens": 0,
                                 "cache_creation_input_tokens": 0}}}
    open(os.path.join(d, name), "w").write(json.dumps(rec) + "\n")
# known ITE: opus weight 1, 100 in + 5*out
transcript(S.path_slug(ROOT + "/ralph_a"), "a.jsonl", "m1", 200)                    # 100+1000 = 1100
transcript(S.path_slug(ROOT + "/ralph_a"), "h.jsonl", "m2", 20, sub=True)           # helper: 100+100 = 200
transcript(S.path_slug(ROOT + "/trio"), "t.jsonl", "m3", 40)                        # 300
transcript(S.path_slug(ROOT + "/judge"), "j.jsonl", "m4", 60)                       # 400 -> harness
transcript(S.path_slug("/home/mandrake/rm/foundry"), "f.jsonl", "m5", 10)           # not arena
arms = ["ralph_a", "trio"]
cl = S.claude_spend_by_arm(proj, arms, ROOT)
check(abs(cl["ralph_a"]["ite"] - 1300) < 1e-6, "sanity probe: known transcript + helper recovered from slug (1300 ITE) -> %s" % cl.get("ralph_a"))
check(cl["ralph_a"]["files"] == 2, "helper transcript attributed to the arm's clone path")
check(abs(cl["trio"]["ite"] - 300) < 1e-6, "second arm separate")
check(abs(cl.get(S.HARNESS, {}).get("ite", 0) - 400) < 1e-6 and "judge" not in cl, "judge path bills to harness, not an arm")
check(S.UNATTRIBUTED in cl and "ralph_a" not in S.UNATTRIBUTED, "non-arena cwd is UNATTRIBUTED, not an arm")
check(S.arm_of_slug(S.path_slug(ROOT + "/judge/sub"), arms, ROOT) == S.HARNESS, "judge subdir is harness")
check(S.arm_of_slug(S.path_slug(ROOT + "/ralph_a/src/x"), arms, ROOT) == "ralph_a", "deeper cwd still the arm")

# gpt_consult tagging: drive the real _log_call
def call(env):
    log = os.path.join(T, "gpt.jsonl")
    old = {k: os.environ.get(k) for k in ("RM_ARM", "RM_GPT_CALL_LOG")}
    os.environ.pop("RM_ARM", None); os.environ["RM_GPT_CALL_LOG"] = log
    os.environ.update(env)
    try:
        G._log_call("job", "m", "x" * 400, "y" * 40, 0)
    finally:
        for k, v in old.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
    return log
log = call({"RM_ARM": "trio"})
g = S.gpt_spend_by_arm(log)
check(g.get("trio", {}).get("calls") == 1 and abs(g["trio"]["ite"] - (100 + 5 * 10)) < 1e-6, "call under RM_ARM=trio billed to trio: %s" % g)
os.remove(log); log = call({})
g = S.gpt_spend_by_arm(log)
check("UNTAGGED" in g and "trio" not in g, "untagged call flagged UNTAGGED")
rep = S.arm_report(ran=["ralph_a"], arms=arms, projects=proj, arena_root=ROOT, gpt_log=log)
check(any("untagged" in f for f in rep["flags"]), "report carries the untagged flag")
check(rep["arms"]["ralph_a"]["ite"] >= 1300, "arm_report ITE nonzero for ran arm")
try:
    S.arm_report(ran=["ralph_a", "ghost"], arms=arms + ["ghost"], projects=proj, arena_root=ROOT, gpt_log=log)
    check(False, "zero spend for an arm that ran is refused")
except S.ZeroSpendRefused:
    check(True, "zero spend for an arm that ran is refused")
# a blind meter (wrong root): real arm transcripts land UNATTRIBUTED -> ran arm sees zero -> refused
try:
    S.arm_report(ran=["ralph_a"], arms=arms, projects=proj, arena_root="/elsewhere", gpt_log=os.path.join(T, "none"))
    check(False, "blind meter (wrong clone root) refused")
except S.ZeroSpendRefused:
    check(True, "blind meter (wrong clone root) refused")
print("FAILS", fails)
sys.exit(1 if fails else 0)
