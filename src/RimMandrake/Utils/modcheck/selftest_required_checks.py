"""Selftest for required_checks_report (observatory S0 rules, bridge_validation_observatory.md 2.4).

Every rule is paired with a CONTROL: the same fixture with the taint removed must count,
so a rule that silently stops firing turns this red instead of passing vacuously.
Also a sanity probe on the committed manifest: FlowWorks carries 38 owner bars
(`modcheck floor --all`), so the manifest instrument can see owner bars at all.
"""
import datetime as dt
import json
import os
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import required_checks_report as R  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("PASS" if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


T0 = dt.datetime(2026, 10, 3, 12, 0, 0)
T1 = dt.datetime(2026, 10, 3, 12, 30, 0)
WHEN = dt.datetime(2026, 10, 3, 12, 20, 0)


def man(*ids, bars=()):
    checks = [{"id": i, "source": "script_check", "owner": False, "required": True} for i in ids]
    for b, claimer in bars:
        checks.append({"id": "ns:" + b, "source": "north_star_bar", "owner": True,
                       "required": True, "polarity": "must", "claimed_by": [claimer]})
    return {"checks": checks}


def chain(name, comps, **sit):
    s = {"bland": True, "companion": True, "bland_problems": [], "surprises": []}
    s.update(sit)
    return {"name": name, "components": comps, "situational": s}


def comp(name, verdict="PASS", detail=""):
    return {"name": name, "verdict": verdict, "detail": detail, "evidence": []}


RUN = {"job": "situational_rerun", "started": T0, "finished": T1, "mods": ["M"],
       "row": {"evidence": {"digests": [{"mod": "M", "unbland_chains": []}]}}}
ATTEST = {"kind": "attest", "what": "deploy-fresh", "mods": "*", "_from": T0 - dt.timedelta(hours=1),
          "_to": T1 + dt.timedelta(hours=1)}


def taint(reason):
    return {"kind": "taint", "reason": reason, "mods": ["M"], "_from": WHEN, "_to": WHEN}


def one(summary, amend=(ATTEST,), run=RUN, m=None):
    rows, extras = R.judge_mod("M", m or man("c/a"), summary, run, list(amend), WHEN)
    return rows[0], R.headline(rows), extras


S_OK = {"chains": [chain("c", [comp("a")])]}

# 1. control: a clean PASS on an attested-fresh, identified run counts
r, h, _ = one(S_OK)
check("clean attested PASS is proven", h["proven"] == 1 and r["holds"] == "yes", r)

# 2. a tainted PASS must not count (one per recorded taint class)
for reason in ("modal-open", "stale-deploy", "focus-lost", "log-blind"):
    r, h, _ = one(S_OK, amend=(ATTEST, taint(reason)))
    check("PASS tainted by %s not counted" % reason,
          h["proven"] == 0 and reason in r["no"] and h["tainted"].get(reason) == 1, r)

# 3. a taint OUTSIDE the run window must not taint it (control for 2)
far = {"kind": "taint", "reason": "modal-open", "mods": ["M"],
       "_from": T1 + dt.timedelta(hours=2), "_to": T1 + dt.timedelta(hours=3)}
r, h, _ = one(S_OK, amend=(ATTEST, far))
check("taint outside the run window ignored", h["proven"] == 1, r)

# 4. a PASS whose precondition was unmet must not count
r, h, _ = one({"chains": [chain("c", [comp("a")], bland=False)]})
check("PASS on a non-bland map (precondition unmet) not counted",
      h["proven"] == 0 and "precondition" in r["no"], r)
r, h, _ = one({"chains": [chain("c", [comp("a")], bland_problems=["corpses present: 7"])]})
check("PASS with bland_problems not counted", h["proven"] == 0 and "precondition" in r["no"], r)
run_unbland = dict(RUN, row={"evidence": {"digests": [{"mod": "M", "unbland_chains": ["c"]}]}})
r, h, _ = one(S_OK, run=run_unbland)
check("PASS in a chain the job listed as unbland not counted", h["proven"] == 0, r)

# 5. recorded contaminants inside the record itself
r, h, _ = one({"chains": [chain("c", [comp("a")], companion=False)]})
check("PASS with companion detectors off (log-blind) not counted",
      h["proven"] == 0 and "log-blind" in r["no"], r)
r, h, _ = one({"chains": [chain("c", [comp("x", "UNMEASURED", "surprise: modal_open: Dialog_ModSettings"),
                                      comp("a")])]})
check("PASS in a chain with a modal_open surprise not counted",
      h["proven"] == 0 and "modal-open" in r["no"], r)
r, h, _ = one({"chains": [chain("c", [comp("a", "PASS(UNVERIFIED 2)")])]})
check("PASS(UNVERIFIED n) not counted", h["proven"] == 0 and "unverified-calls" in r["no"], r)

# 6. upstream failure: a cascade is not a result
r, h, _ = one({"chains": [chain("c", [comp("a", "UNMEASURED", "upstream failed -- meaningless")])]})
check("cascade UNMEASURED is not proven and names upstream-failure",
      h["proven"] == 0 and r["ran"] == "cascade" and h["unmeasured"].get("upstream-failure") == 1, r)

# 7. unknown is not clean
r, h, _ = one(S_OK, amend=())
check("no deploy attestation -> unknown, pending, not proven",
      h["proven"] == 0 and r["holds"] == "unknown" and h["pending_deploy"] == 1, r)
r, h, _ = one(S_OK, run=None)
check("no job row (killed run) -> run identity unknown, not proven, not pending",
      h["proven"] == 0 and R.RUN_UNKNOWN in r["unknown"] and h["pending_deploy"] == 0, r)
r, h, _ = one({"chains": [{"name": "c", "components": [comp("a")]}]})
check("no situational block -> detector coverage unknown, not proven",
      h["proven"] == 0 and R.DETECTORS_UNRECORDED in r["unknown"], r)

# 8. a clean FAIL is proven information
r, h, _ = one({"chains": [chain("c", [comp("a", "FAIL", "ExpectationFailed: x")])]})
check("clean FAIL is proven (as FAIL)", h["proven"] == 1 and h["proven_fail"] == 1, r)

# 9. missing check -> not reached; extra component -> reported
r, h, ex = one({"chains": [chain("c", [comp("other")])]})
check("required check absent from record -> not reached", h["not_reached"] == 1 and h["proven"] == 0, r)
check("component not in manifest is reported", ex == ["c/other"], ex)

# 10. owner bars inherit the claiming component's evidence
M2 = man("c/a", bars=[("bar1", "c/a")])
S_BAR = {"chains": [chain("c", [comp("a")])], "visual": [{"id": "bar1", "polarity": "must", "verdict": "YES"}]}
rows, _ = R.judge_mod("M", M2, S_BAR, RUN, [ATTEST], WHEN)
h = R.headline(rows)
check("bar judged YES on a clean claimer is proven", h["owner_bars_proven"] == 1 and h["owner_bars"] == 1, h)
rows, _ = R.judge_mod("M", M2, S_BAR, RUN, [ATTEST, taint("modal-open")], WHEN)
h = R.headline(rows)
check("bar judged YES on a tainted claimer not counted", h["owner_bars_proven"] == 0, h)
S_UJ = dict(S_BAR, visual=[{"id": "bar1", "polarity": "must", "verdict": "UNJUDGEABLE"}])
rows, _ = R.judge_mod("M", M2, S_UJ, RUN, [ATTEST], WHEN)
check("UNJUDGEABLE bar is not proven", R.headline(rows)["owner_bars_proven"] == 0)

# 11. end to end through files (loaders, run join, mtime) in a temp records dir
with tempfile.TemporaryDirectory() as d:
    os.makedirs(os.path.join(d, "live_queue", "situational_rerun"))
    sp = os.path.join(d, "live_queue", "situational_rerun", "M_summary.json")
    json.dump(S_OK, open(sp, "w"))
    os.utime(sp, (WHEN.timestamp(), WHEN.timestamp()))
    with open(os.path.join(d, "live_queue_results.jsonl"), "w") as f:
        f.write(json.dumps({"job": "situational_rerun", "started": T0.isoformat(), "finished": T1.isoformat(),
                            "evidence": {"digests": [{"mod": "M", "verdicts": {"PASS": 1}}]}}) + "\n")
    ap = os.path.join(d, "amend.jsonl")
    with open(ap, "w") as f:
        f.write("// comment\n")
        f.write(json.dumps({"kind": "attest", "what": "deploy-fresh", "mods": "*",
                            "from": "2026-10-03T11:00:00", "to": "2026-10-03T13:00:00"}) + "\n")
    rep, runs = R.build_report({"mods": {"M": man("c/a")}}, d, ap)
    check("file path: summary joined to its job and proven",
          len(rep) == 1 and rep[0]["run"] is not None and rep[0]["head"]["proven"] == 1, rep and rep[0].get("head"))
    with open(ap, "a") as f:
        f.write(json.dumps({"kind": "taint", "reason": "stale-deploy", "mods": "*",
                            "from": "2026-10-03T12:10:00", "to": "2026-10-03T12:15:00"}) + "\n")
    rep, runs = R.build_report({"mods": {"M": man("c/a")}}, d, ap)
    check("file path: appended taint removes the proof", rep[0]["head"]["proven"] == 0)
    out = R.render(rep, runs, None)
    check("render leads with the proven headline", out.startswith("REQUIRED CHECKS PROVEN"), out[:60])

# 12. sanity probe on the committed manifest
try:
    m = json.load(open(R.MANIFEST, encoding="utf-8"))["mods"]
    fw = [c for c in m["FlowWorks"]["checks"] if c["source"] == "north_star_bar"]
    check("sanity: manifest sees FlowWorks' 38 owner bars", len(fw) == 38, len(fw))
except (OSError, KeyError, ValueError) as e:
    check("sanity: manifest readable", False, e)

print("ALL PASS" if not FAILS else "FAILED: %s" % FAILS)
sys.exit(1 if FAILS else 0)
