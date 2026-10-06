"""Selftest for required_checks_report (observatory S0 rules, bridge_validation_observatory.md 2.4).

Every rule is paired with a CONTROL: the same fixture with the taint removed must count,
so a rule that silently stops firing turns this red instead of passing vacuously.
Also a sanity probe on the committed manifest: every mod with owner bars has a VALIDATED walk with that many
must-show lines, and at least one exists, so the manifest instrument can see owner bars at all.
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
    # a manifest mod with no live_queue record is NAMED, with its own checkout results, never silently dropped
    mdir = os.path.join(d, "src", "N")
    os.makedirs(os.path.join(mdir, "northstar"))
    json.dump({"rows": [{"id": "x"}, {"id": "y"}]}, open(os.path.join(mdir, "northstar", "proof_all_1.json"), "w"))
    old_root, R.ROOT = R.ROOT, d
    try:
        rep, runs = R.build_report({"mods": {"M": man("c/a"), "N": dict(man("n/a", "n/b"), script="src/N/validation.py")}}, d, ap)
        out = R.render(rep, runs, None)
    finally:
        R.ROOT = old_root
    un = [e for e in rep if e.get("unread")]
    check("unrecorded manifest mod is listed, outside the total", len(un) == 1 and un[0]["required"] == 2
          and "NOT IN THE TOTAL: 1 mods (2 required checks)" in out and "of 1 required" in out, out[-400:])
    check("its checkout result file is named with its row count",
          "src/N/northstar/proof_all_1.json" in out and "2 rows" in out, out[-300:])

# 12. sanity probe on the committed manifest
try:
    m = json.load(open(R.MANIFEST, encoding="utf-8"))["mods"]
    # owner bars exist only for a VALIDATED walk; which walks are VALIDATED moves (FlowWorks was released to DRAFT
    # 2026-10-05), so the probe reads them from the walks rather than naming one mod
    import northstar as _ns
    want = {}
    for mod, row in m.items():
        nb = [c for c in row["checks"] if c["source"] == "north_star_bar"]
        if nb:
            want[mod] = len(nb)
    check("sanity: manifest carries owner bars for at least one VALIDATED walk", bool(want), want)
    bad = {}
    for mod, n in want.items():
        hits = [p for p in __import__("glob").glob(os.path.join(os.path.dirname(R.MANIFEST), "..", "..", "..", "..",
                                                                 "design", "validation_walks", "*", mod + ".md"))]
        ns = _ns.parse(hits[0]) if hits else None
        if not ns or ns.get("state") != "VALIDATED" or len(ns["must_show"]) != n:
            bad[mod] = (n, ns and ns.get("state"), ns and len(ns["must_show"]))
    check("sanity: each owner-bar count equals its VALIDATED walk's must-show count", not bad, bad)
except (OSError, KeyError, ValueError) as e:
    check("sanity: manifest readable", False, e)


# 13. S1: a recorded DEPLOY FINGERPRINT can make a result proven (no amendment needed), and a stale one cannot
def fp(state="in-sync", sh="aa", dh=None, dirty=False, mod="M"):
    return {"mod": mod, "state": state, "src_hash": sh, "deployed_hash": sh if dh is None else dh, "src_dirty": dirty}


def with_ri(start, end, git=None, **extra):
    d = dict(S_OK)
    d["run_identity"] = {"run_id": "x", "git": git or {"source": "mirror", "sha": "abc"},
                         "deploy_start": start, "deploy_end": end}
    d.update(extra)
    return d


r, h, _ = one(with_ri(fp(), fp()), amend=())
check("fingerprint in-sync at start+end on mirror => proven with NO amendment", h["proven"] == 1 and r["holds"] == "yes", r)
r, h, _ = one(with_ri(fp(state="drift", dh="bb"), fp()), amend=())
check("STALE fingerprint (drift at start) => not proven, stale-deploy", h["proven"] == 0 and "stale-deploy" in r["no"], r)
r, h, _ = one(with_ri(fp(sh="aa"), fp(sh="cc")), amend=())
check("content moved mid-run => not proven, stale-deploy", h["proven"] == 0 and "stale-deploy" in r["no"], r)
r, h, _ = one(with_ri(fp(dirty=True), fp(dirty=True), git={"source": "git", "sha": "abc"}), amend=())
check("dirty tree vs HEAD => unproven (unknown), not pending-deploy", h["proven"] == 0 and r["holds"] == "unknown" and not r["pending_deploy"], r)
r, h, _ = one(with_ri(fp(), None), amend=())
check("missing end fingerprint => not proven", h["proven"] == 0, r)
r, h, _ = one(with_ri(fp(mod="Other"), fp(mod="Other")), amend=())
check("fingerprint for a different mod => not proven", h["proven"] == 0, r)
r, h, _ = one(S_OK, amend=())
check("no fingerprint, no amendment => pending deploy proof (control)", h["proven"] == 0 and r["pending_deploy"], r)
r, h, _ = one(with_ri(fp(), fp()), amend=(taint("stale-deploy"),))
check("a stale-deploy amendment still beats a good fingerprint", h["proven"] == 0 and "stale-deploy" in r["no"], r)

# 14. S1: per-chain modal check
S2 = {"chains": [dict(chain("c", [comp("a")]), modal_check={"found_open": False, "dialogs": {}, "errors": []}),
                 dict(chain("d", [comp("b")]), modal_check={"found_open": True, "dialogs": {"X": 1}, "errors": []})],
      "modal_check_final": {"found_open": False, "dialogs": {}, "errors": []}}
S2["run_identity"] = with_ri(fp(), fp())["run_identity"]
rows, _ = R.judge_mod("M", man("c/a", "d/b"), S2, RUN, [], WHEN)
byid = {x["id"]: x for x in rows}
check("dialog found open when chain d began taints the PREVIOUS chain c", "modal-open" in byid["c/a"]["no"] and not byid["c/a"]["trustworthy"], byid["c/a"])
check("chain d itself (modal closed before it, none after) stays proven", byid["d/b"]["trustworthy"], byid["d/b"])
S3 = dict(S2, modal_check_final={"found_open": True, "dialogs": {"X": 1}, "errors": []})
rows, _ = R.judge_mod("M", man("c/a", "d/b"), S3, RUN, [], WHEN)
check("dialog still open after the LAST chain taints the last chain", "modal-open" in {x["id"]: x for x in rows}["d/b"]["no"])
S4 = dict(S2, modal_check_final={"found_open": False, "dialogs": {"X": None}, "errors": ["X: boom"]})
rows, _ = R.judge_mod("M", man("c/a", "d/b"), S4, RUN, [], WHEN)
d4 = {x["id"]: x for x in rows}["d/b"]
check("a FAILED modal sweep is unknown, never clean", d4["holds"] == "unknown" and not d4["trustworthy"], d4)

print("ALL PASS" if not FAILS else "FAILED: %s" % FAILS)
sys.exit(1 if FAILS else 0)
