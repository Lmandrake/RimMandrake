#!/usr/bin/env python3
"""selftest_relentless_live_tier.py -- an exact-tier proof runs on SteveDesktop through testq (LANE_TIER_WIRE_A_WHOLE_LIST_LOAD).

Owner by card 2026-11-05, "What should SteveDesktop spend its time on now? -> Exact-mod-list tests": a clause whose proof
needs one exact list (VITALS A1 on ratchet_pilot, GIZKA A2 on gizkastowaway) is a testq job on SteveDesktop, and
"No exact-tier proof triggers an Archmagi mod-list swap". What must hold, on selftest_relentless_game's fake world:
  routing: live_tiers reads a file-level and a per-clause tier and refuses two tiers for one clause; the live round skips a
  tier clause; a tier item's game phase submits ONE testq job (profile tier:<name>, lane stevedesktop, its open clauses)
  and stages nothing on Archmagi: no bridge take, no staging prompt, no enable, no list write; a plain item stages on
  Archmagi and submits nothing; a mixed item sends its tier clause to testq and stages the rest; nothing in
  relentless_game writes a tier list (no modset_builder --apply, no --restore-own);
  results: a counted result's PASS/FAIL is verified per criterion and lands as a runs.jsonl row (source testq); a
  result whose load was not the tier (tier_load exact false), an exit-1 inability, or an UNMEASURED row judges nothing
  and resubmits, held after steve_tries; fault_monitor.gate quarantine judges nothing and resubmits without spending a
  try, hold waits; a pending job waits; a FAIL returns the item like any live FAIL;
  and the two halves outside rimflow, run here as part of this proof: selftest_testq_tier.py (schema, submit, admission
  stays on a tier) and selftest_steve_worker_tier.py (the worker's tier-exact load check and proofs run).
"""
import inspect
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                 # noqa: E402
import relentless_game as G            # noqa: E402
import relentless_live_round as LR     # noqa: E402
import selftest_relentless_game as T   # noqa: E402

FAILS = T.FAILS
ok = T.ok
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TIER_PROOF = "live-tier: ratchet_pilot\n" + T.PROOF
MIXED = ("live-tier A1: ratchet_pilot\nlive-proof A1: python.exe src/RimMandrake/Utils/perf/test_vitals_tier_makeup.py\n"
         + T.PROOF)


def staged(x):
    return [l for l in x.w.launches if "STAGING" in l[2]]


def in_stage(x, item="I0", proof=TIER_PROOF, clauses=("A2",), running=False):
    T.to_game(x, item)
    x.w.proofs[(item, ".txt")] = proof
    with x.s.lock():
        st = x.s.load(item)
        st["game"].update(phase="stage", clauses=list(clauses))
        x.s.save(st)
    x.w.running = running


def step(x, item="I0"):
    acts = []
    G.step(x.s, x.w, x.r, item, x.now, acts, R)
    return acts


def finish_job(x, jid, verdicts, exact=True, gate=("count", None), outcome="DONE", detail="exit 0: PASS"):
    job = x.w.testq[jid]["job"]
    res = {"attempt": jid + ".a1", "outcome": outcome, "cause": None if outcome == "DONE" else "LOAD",
           "running": ["a", "b", "c"], "note": "",
           "tier": {"exact": exact, "why": None if exact else "WRONG_TIER: the running load is not tier ratchet_pilot"},
           "rows": [{"chain": "proofs", "row": k, "verdict": v, "detail": detail} for k, v in verdicts.items()]}
    x.w.testq[jid].update(state="done", rec={"job": job, "result": res}, gate=gate)


def only_job(x):
    return sorted(getattr(x.w, "testq", {}))[-1]


def t_parse():
    ok(LR.live_tiers(TIER_PROOF) == {LR.ALL: "ratchet_pilot"}, "a file-level live-tier is every clause's")
    t = LR.live_tiers(MIXED)
    ok(t == {"A1": "ratchet_pilot"} and LR.clause_tier(MIXED, "A1") == "ratchet_pilot"
       and LR.clause_tier(MIXED, "A2") is None, "a per-clause live-tier is that clause's only: %s" % t)
    ok(LR.live_tiers("`live-tier: gizkastowaway` # the A2 set\n") == {LR.ALL: "gizkastowaway"}, "backticks, a comment")
    ok(LR.live_tiers("live-tier A1, A2: x\n") == {"A1": "x", "A2": "x"}, "two clauses on one line")
    for bad in ("live-tier: a b\n", "live-tier: a\nlive-tier: b\n", "live-tier:\n", "live-tier A1: a\nlive-tier A1: b\n"):
        try:
            LR.live_tiers(bad)
            ok(False, "refused: %r" % bad)
        except ValueError:
            ok(True, "refused: %r" % bad)
    ok(G.tier_clauses(MIXED, ["A1", "A2"]) == {"ratchet_pilot": ["A1"]}, "tier_clauses groups by tier")


def t_round_skips_tier_clauses():
    it = {"id": "I0", "state": "built", "built_sha": T.SHA, "outstanding": ["A1", "A2"],
          "criteria": [{"id": "A1", "level": "L1"}, {"id": "A2", "level": "L1"}]}
    todo, counts = LR.candidates([it], lambda i: MIXED, {}, 0, 0)
    ok([t[1] for t in todo] == ["A2"] and counts.get(LR.EXACT_TIER) == 1,
       "Archmagi's round runs A2 and skips the tier clause A1: %s %s" % (todo, counts))
    todo, counts = LR.candidates([it], lambda i: "live-tier: a b\n" + MIXED, {}, 0, 0)
    ok(not todo, "a malformed tier runs nowhere on Archmagi: %s" % counts)


def t_no_archmagi_swap_in_code():
    src = inspect.getsource(G)
    ok("modset_builder.py\"" not in src and "modset_builder.py --tier" not in src and "--restore-own" not in src
       and "tier_cmd" not in src and "modlist_tier" not in src,
       "relentless_game holds no command that writes a tier list on Archmagi")
    ok("SteveDesktop" in " ".join(G.BRIEF) and "never swapped" in " ".join(G.BRIEF), "the brief says where a tier runs")


def t_tier_item_goes_to_testq_not_staging():
    x = T.rig(1)
    in_stage(x)
    acts = step(x)
    st = x.st("I0")
    ev = x.w.events
    ok("testq_submit:I0:ratchet_pilot:A2" in ev, "the tier clause is submitted to testq: %s" % ev)
    ok("take" not in ev and not staged(x) and not x.w.enabled and "enable" not in ev,
       "no bridge, no staging prompt, no enable on Archmagi: %s" % ev)
    job = x.w.testq[only_job(x)]["job"]
    ok(job["profile"] == "tier:ratchet_pilot" and job["lane"] == "stevedesktop" and job["selector"] == {"proofs": ["A2"]},
       "the job: profile tier:ratchet_pilot, lane stevedesktop, the open clause: %s" % job)
    ok(st["game"]["phase"] == "prove" and st["game"]["testq"]["ratchet_pilot"]["job"] == only_job(x),
       "the item waits in prove with its job: %s" % st["game"].get("testq"))
    n = len(x.w.testq)
    for _ in range(2):
        acts = step(x)
    ok(len(x.w.testq) == n and any(a["do"] == "game_steve_wait" for a in acts) and "take" not in x.w.events,
       "a pending job waits; no second job, still no staging: %s" % acts)
    x.done()


def t_plain_item_stages_on_archmagi():
    x = T.rig(1)
    in_stage(x, proof=T.PROOF)
    step(x)
    ok(not any(e.startswith("testq_submit") for e in x.w.events) and "take" in x.w.events and staged(x),
       "a plain item stages on Archmagi and submits nothing: %s" % x.w.events)
    x.done()


def t_mixed_item_splits():
    x = T.rig(1)
    in_stage(x, proof=MIXED, clauses=("A1", "A2"))
    step(x)
    ok("testq_submit:I0:ratchet_pilot:A1" in x.w.events and "take" in x.w.events and staged(x),
       "A1 goes to testq, A2 stages on Archmagi: %s" % x.w.events)
    p = staged(x)[-1][2] if staged(x) else ""
    ok("modset_builder" not in p, "and the Archmagi staging prompt writes no tier list")
    x.done()


def t_pass_is_verified_and_recorded():
    x = T.rig(1)
    in_stage(x)
    step(x)
    finish_job(x, only_job(x), {"A2": "PASS"})
    acts = step(x)
    ok("verify:I0:A2:pass" in x.w.events, "a counted PASS is verified per criterion: %s" % x.w.events)
    row = [r for r in x.w.rows if r.get("source") == G.STEVE]
    ok(len(row) == 1 and row[0]["outcome"] == "PASS" and row[0]["criterion"] == "A2" and row[0]["tier"] == "ratchet_pilot",
       "and lands as a runs.jsonl row: %s" % row)
    ok(not any(a["do"] == "game_steve_submit" for a in acts) and "take" not in x.w.events,
       "nothing resubmitted, nothing staged: %s" % acts)
    x.done()


def t_fail_returns():
    x = T.rig(1)
    in_stage(x)
    step(x)
    finish_job(x, only_job(x), {"A2": "FAIL"}, detail="exit 1: A2 FAIL MOD: 39 running mods, wanted 23")
    step(x)
    ok("verify:I0:A2:fail" in x.w.events and x.st("I0")["status"] != "game",
       "a Steve FAIL is verified and returns the item: %s %s" % (x.w.events, x.st("I0")["status"]))
    x.done()


def t_not_the_tier_is_unmeasured():
    x = T.rig(1)
    in_stage(x)
    step(x)
    for n in range(2, 4):
        finish_job(x, only_job(x), {"A2": "UNMEASURED"}, exact=False, outcome="INVALID")
        acts = step(x)
        ok(not any(e.startswith("verify") for e in x.w.events) and not [r for r in x.w.rows if r.get("source")],
           "a load that is not the tier judges nothing")
        ok(any(a["do"] == "game_steve_submit" for a in acts) and len(x.w.testq) == n,
           "and resubmits (job %d): %s" % (n, acts))
    finish_job(x, only_job(x), {"A2": "UNMEASURED"}, exact=False, outcome="INVALID")
    step(x)
    st = x.st("I0")
    ok(st["status"] == "held" and "WRONG_TIER" in st["hold"]["why"] and len(x.w.testq) == 3,
       "after steve_tries it is held with the reason: %s" % st.get("hold"))
    x.done()


def t_exit1_inability_is_no_fail():
    x = T.rig(1)
    in_stage(x)
    step(x)
    finish_job(x, only_job(x), {"A2": "FAIL"}, detail="exit 1: WRONG_TIER 39 running mods")
    acts = step(x)
    ok(not any(e.startswith("verify") for e in x.w.events) and any(a["do"] == "game_steve_submit" for a in acts),
       "an exit 1 that says WRONG_TIER is no FAIL: resubmitted: %s" % acts)
    x.done()


def t_quarantine_and_hold():
    x = T.rig(1)
    in_stage(x)
    step(x)
    jid = only_job(x)
    finish_job(x, jid, {"A2": "PASS"}, gate=("hold", "no clean canary cycle read since it finished"))
    acts = step(x)
    ok(not any(e.startswith("verify") for e in x.w.events) and len(x.w.testq) == 1
       and any(a["do"] == "game_steve_wait" for a in acts), "a held result waits: %s" % acts)
    finish_job(x, jid, {"A2": "PASS"}, gate=("quarantine", {"id": "W1"}))
    acts = step(x)
    tries = x.st("I0")["game"]["testq"]["ratchet_pilot"]["tries"]
    ok(not any(e.startswith("verify") for e in x.w.events) and len(x.w.testq) == 2 and tries == 1,
       "a quarantined PASS is never counted; resubmitted without spending a try: %s tries %s" % (acts, tries))
    x.done()


def t_steve_fail_in_stage_stages_nothing():
    x = T.rig(1)
    in_stage(x, proof=MIXED, clauses=("A1", "A2"))
    x.w.testq = {"J20261106T000000Z-0000aa": {"state": None}}
    with x.s.lock():
        st = x.s.load("I0")
        st["game"]["testq"] = {"ratchet_pilot": {"job": "J20261106T000000Z-0000aa", "sha": T.SHA, "tries": 1}}
        x.s.save(st)
    x.w.testq["J20261106T000000Z-0000aa"] = {"state": "pending", "rec": None, "gate": None,
                                             "job": {"id": "J20261106T000000Z-0000aa", "profile": "tier:ratchet_pilot"}}
    finish_job(x, "J20261106T000000Z-0000aa", {"A1": "FAIL"}, detail="exit 1: A1 FAIL MOD: 39 running")
    step(x)
    ok("verify:I0:A1:fail" in x.w.events and "take" not in x.w.events and not staged(x),
       "a Steve FAIL found in stage stages nothing on Archmagi: %s" % x.w.events)
    x.done()


def t_quarantine_loop_is_bounded():
    x = T.rig(1)
    in_stage(x)
    step(x)
    for _ in range(6):
        if x.st("I0")["status"] != "game":
            break
        finish_job(x, only_job(x), {"A2": "PASS"}, gate=("quarantine", {"id": "W1"}))
        step(x)
    st = x.st("I0")
    ok(st["status"] == "held" and "faulted" in st["hold"]["why"] and not any(e.startswith("verify") for e in x.w.events),
       "a host that keeps faulting holds the item, never counted: %s" % (st.get("hold") or {}).get("why"))
    x.done()


def t_green_full_never_goes_to_a_tier():
    ok(G.tier_clauses(TIER_PROOF + "live-proof F1: python3 x.py\n", ["A2", "F1"], {"A2": "L1", "F1": G.FINAL_LEVEL})
       == {"ratchet_pilot": ["A2"]}, "a file-wide tier leaves the GREEN-FULL clause to the full list")
    it = {"id": "I0", "state": "built", "built_sha": T.SHA, "outstanding": ["F1"], "criteria": [{"id": "F1", "level": G.FINAL_LEVEL}]}
    todo, _c = LR.candidates([it], lambda i: TIER_PROOF + "live-proof F1: python3 x.py\n", {}, 0, 0)
    ok([t[1] for t in todo] == ["F1"], "and Archmagi's round still runs it: %s" % todo)


def t_submit_refused_waits():
    x = T.rig(1)
    in_stage(x)
    x.w.submit_why = "REFUSED: tier:ratchet_pilot is no modset_builder.py tier"
    step(x)
    st = x.st("I0")
    ok("take" not in x.w.events and "testq" in (st.get("put_down") or {}).get("on", ""),
       "a refused submit puts the item down and stages nothing: %s" % st.get("put_down"))
    x.done()


def t_outer_halves():
    for rel in ("src/RimMandrake/Utils/testq/selftest_testq_tier.py",
                "infrastructure/stevedesktop/selftest_steve_worker_tier.py"):
        r = subprocess.run([sys.executable, os.path.join(REPO, rel)], cwd=REPO, capture_output=True, text=True,
                           timeout=300, stdin=subprocess.DEVNULL)
        tail = (r.stdout + r.stderr).strip().splitlines()[-3:]
        ok(r.returncode == 0, "%s passes: %s" % (rel, " | ".join(tail)))


TESTS = (t_parse, t_round_skips_tier_clauses, t_no_archmagi_swap_in_code, t_tier_item_goes_to_testq_not_staging,
         t_plain_item_stages_on_archmagi, t_mixed_item_splits, t_pass_is_verified_and_recorded, t_fail_returns,
         t_not_the_tier_is_unmeasured, t_exit1_inability_is_no_fail, t_quarantine_and_hold, t_submit_refused_waits,
         t_steve_fail_in_stage_stages_nothing, t_quarantine_loop_is_bounded, t_green_full_never_goes_to_a_tier,
         t_outer_halves)


def main(args):
    picked, ran = set(a for a in args if not a.startswith("--")), 0
    for t in TESTS:
        if picked and t.__name__ not in picked:
            continue
        ran += 1
        print("--", t.__name__)
        t()
    if picked and ran != len(picked):
        print("selftest_relentless_live_tier: FAIL ran %d of the %d named" % (ran, len(picked)))
        return 1
    print("selftest_relentless_live_tier: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
