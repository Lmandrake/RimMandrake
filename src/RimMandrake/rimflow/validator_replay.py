#!/usr/bin/env python3
"""validator_replay.py -- the replay bank: tonight's validation cases, run through the REAL supervisor transitions, each with
the classification, routing and close behaviour it must show (VALIDATOR_REPLAY_BUILD_GOOD_AND_BAD; spec
design/RimMandrake/test_tolerance_gpt_advice_2026-11-04.md, rank 5, "Validate validators against both good and bad worlds").

    python3 src/RimMandrake/rimflow/validator_replay.py measure [CASE ...]    # what each case does today, one JSON line each
    python3 src/RimMandrake/rimflow/validator_replay.py gaps                  # the owed behaviours, by the item that owes them

THE BANK is validator_replay/bank.json. A case is one recorded world handed to one layer of the supervisor:
  layer "live":  a proof's exit code and log (a real log from <RELENTLESS_ROOT>/live, kept under validator_replay/logs) go
                 through relentless_live.run (the classifier, verify or note), and the row it writes goes through
                 relentless.tick's game phase (relentless_game.step: back to a worker, restage, wait, close);
  layer "check": a Marker verdict (word, reasons, structured defects/unreached) goes through relentless.tick's check
                 branch (relentless_wall.read_as, fail(), unmeasured(), the close).
Nothing is faked above the effects: no units, no game, no ledger (selftest_relentless.FakeWorld and
selftest_relentless_game.GW stand for the world, as in their own selftests).

MEASURED PROPERTIES (measure() returns them; a case's `expect` and `owed` name them):
  outcome, verdict, verified, harness   the live row: PASS/FAIL/UNMEASURED, PASS/FAIL/INFRA, a `rimflow verify` written,
                                        the harness flag (relentless_game charges no strike for it)
  acted                                 the check: the word the supervisor acts on (relentless_wall.read_as)
  gen_bump                              the generation moved: a new worker will be sent, the candidate is abandoned
  route                                 where the item went: last_fail's class (game_fail, blind_fail, ...), or its status
                                        when nothing failed (game, candidate, held, done, closing)
  candidate_kept                        the candidate sha still stands as the thing to check (no rebuild of it)
  closes                                the transition can end in a close (done, or the close path started)
  unresolved_kept                       a clause the run could not reach is still on record beside a defect: in the row
                                        (live), or in what the next worker reads / the standing check (check)
  rewoken                               after `unhold` (the box repaired) the SAME candidate is checked again, same gen

OWED BEHAVIOUR. The owner, 2026-11-03: broken tests are expected; inability to measure is reported up. Where today's
supervisor does not yet do what the spec's table requires, the case says so instead of pretending: an `owed` entry names
the property, the value the spec wants, the value today gives, and the item that owes it (REWORK_GATE_..., ...). The
selftest asserts today's value, so a gap is never a silent pass and never a red sweep; and a gap that closes (today's
value now equals `want`) fails the selftest until the bank moves `want` into `expect`, so the bank never lags its code.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BANK = os.path.join(HERE, "validator_replay", "bank.json")
LOGS = os.path.join(HERE, "validator_replay", "logs")
PROPS = ("outcome", "verdict", "verified", "harness", "acted", "gen_bump", "route", "candidate_kept", "closes",
         "unresolved_kept", "rewoken")
SHA = "sha1"


def load(path=BANK):
    with open(path, encoding="utf-8") as f:
        bank = json.load(f)
    ids = [c["id"] for c in bank["cases"]]
    if len(set(ids)) != len(ids):
        raise ValueError("bank: a case id repeats")
    for c in bank["cases"]:
        if c.get("layer") not in ("live", "check"):
            raise ValueError("%s: layer is live or check" % c.get("id"))
        for k in list(c.get("expect") or {}) + [o["prop"] for o in c.get("owed") or ()]:
            if k not in PROPS:
                raise ValueError("%s: %s is not a measured property" % (c["id"], k))
        for o in c.get("owed") or ():
            if not (o.get("by") and "want" in o and "today" in o) or o["want"] == o["today"]:
                raise ValueError("%s: an owed entry names by, want and today, and want differs from today" % c["id"])
    return bank


def log_text(case):
    if case.get("log"):
        with open(os.path.join(LOGS, case["log"]), encoding="utf-8", errors="replace") as f:
            return f.read()
    return case.get("text", "")


# ---- layer "live": relentless_live.run, then the row through relentless.tick's game phase ----

def _live_row(case, root, rules=None):
    import relentless_live as L
    import selftest_relentless_live as SL
    text, proof = log_text(case), case.get("proof", "python.exe probe.py")
    codes = {proof.split()[0] + " ": (case["exit"], text)}
    for prefix, code, said in case.get("also") or ():     # another interpreter's answer: the python.exe rerun of a WSL proof
        codes.setdefault(prefix, (code, said))
    kw = dict(case.get("fx") or {})
    if "later" in kw:
        kw["later"] = [tuple(x) for x in kw["later"]]
    fx = SL.ScriptFx(codes, **kw)
    row = L.run(fx, root, "ROT_X", "A2", proof, "--compose biomes", rules or {}, now=1_800_000_000)
    verified = any(c[:2] == ("rimflow", "verify") for c in fx.calls)
    return row, verified


def _game_route(row):
    """The row as the supervisor's game phase reads it: an item in its prove phase on SHA, the row lands, one tick."""
    import relentless as R
    import selftest_relentless_game as SG
    sink = []
    x = SG.rig(1)
    try:
        SG.to_game(x, "I0")
        x.tick()
        x.tick()
        before = x.st("I0")
        gen, cand = before["gen"], (before.get("candidate") or {}).get("sha")
        x.w.rows = [dict(row, at="2099-01-01T00:00:00Z", item="I0", criterion="A2", sha=SHA)]
        x.tick()
        st = x.st("I0")
        if st["status"] == "game" and row.get("outcome") == "PASS":
            x.w.led["I0"]["state"] = "done"         # the ledger's own done, written by the verify a PASS row carries
            x.tick()
            st = x.st("I0")
        lf = st.get("last_fail") or {}
        moved = st["gen"] != gen
        return {"gen_bump": moved, "route": lf.get("class") if moved and lf else st["status"],
                "candidate_kept": not moved and (st.get("candidate") or {}).get("sha", cand) == cand,
                "closes": st["status"] in ("done", "closing")}
    finally:
        sink.append(R)
        x.done()


def measure_live(case):
    root = tempfile.mkdtemp(prefix="vr_live_")
    try:
        row, verified = _live_row(case, root)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    out = {"outcome": row["outcome"], "verdict": row.get("verdict"), "verified": verified,
           "harness": bool(row.get("harness")), "why": (row.get("why") or "")[:160],
           "unresolved_kept": bool(row.get("unresolved"))}
    out.update(_game_route(row))
    return out


# ---- layer "check": a Marker verdict through relentless.tick's check branch ----

def measure_check(case):
    import relentless as R
    import relentless_wall as W
    import selftest_relentless as S
    x = S.Rig(n=1, share=1.0)
    try:
        x.run_one("I0")
        st = x.st("I0")
        R.contract(x.s, "I0", st["gen"], "proof", live="once: replay bank")
        R.finish(x.s, "I0", st["gen"], SHA, "evidence")
        x.w.up[st["run"]["unit"]] = False
        x.tick()
        x.tick()
        out = {}
        for n, v in enumerate(case["verdicts"]):
            st = x.st("I0")
            if st["status"] != "checking":
                for _ in range(8):      # an unmeasured candidate waits recheck_at, then is checked again
                    x.tick(dt=4000)
                    st = x.st("I0")
                    if st["status"] == "checking":
                        break
            if st["status"] != "checking":
                out["stopped_before_verdict"] = n
                break
            gen, cand = st["gen"], (st.get("candidate") or {}).get("sha")
            R.verdict(x.s, "I0", st["check"]["nonce"], v["word"], v.get("reasons", ""), defects=v.get("defects"),
                      unreached=v.get("unreached"), strict=False)
            out["acted"] = W.read_as(v["word"], v.get("reasons"), W.clean_list(v.get("defects")),
                                     W.clean_list(v.get("unreached")))[0]
            x.w.up[st["check"]["run"]["unit"]] = False
            x.tick()
            x.tick()
            st = x.st("I0")
            lf = st.get("last_fail") or {}
            moved = st["gen"] != gen
            told = x.s.learned("I0") if moved else json.dumps(st.get("check") or {})
            unreached = W.clean_list(v.get("unreached")) or []
            out.update(gen_bump=moved, route=lf.get("class") if moved and lf else st["status"],
                       candidate_kept=not moved and (st.get("candidate") or {}).get("sha") == cand,
                       closes=st["status"] in ("done", "closing") or bool(x.w.closes),
                       # what the next reader (a worker's learned file, or the standing check) still says of the clause
                       # the run could not reach
                       unresolved_kept=bool(unreached) and all(u[:60] in told for u in unreached))
        if case.get("unhold"):      # the box was repaired: the same candidate is checked again, no worker is sent
            st = x.st("I0")
            gen, cand = st["gen"], (st.get("candidate") or {}).get("sha")
            R.unhold(x.s, "I0", "replay bank: the box is repaired")
            x.tick()
            st = x.st("I0")
            out["rewoken"] = st["status"] in ("candidate", "checking") and st["gen"] == gen and (
                (st.get("candidate") or {}).get("sha") == cand)
        return out
    finally:
        x.done()


def measure(case):
    """-> the case's measured properties. The rigs' own progress lines go nowhere; a rig check that fails is raised."""
    import contextlib
    import io
    import selftest_relentless as S
    n = len(S.FAILS)
    with contextlib.redirect_stdout(io.StringIO()):
        got = measure_live(case) if case["layer"] == "live" else measure_check(case)
    if len(S.FAILS) > n:
        raise RuntimeError("%s: the rig itself failed: %s" % (case["id"], S.FAILS[n:]))
    return got


def judge(case, got):
    """-> [problems]: an expected property that differs, an owed gap whose today value moved (closed or regressed)."""
    bad = []
    for k, v in (case.get("expect") or {}).items():
        if got.get(k) != v:
            bad.append("%s: %s is %r, the bank expects %r" % (case["id"], k, got.get(k), v))
    for o in case.get("owed") or ():
        g = got.get(o["prop"])
        if g == o["want"]:
            bad.append("%s: the gap owed by %s closed (%s is now %r): move it into expect" % (
                case["id"], o["by"], o["prop"], g))
        elif g != o["today"]:
            bad.append("%s: %s is %r, neither today's %r nor the wanted %r (owed by %s)" % (
                case["id"], o["prop"], g, o["today"], o["want"], o["by"]))
    return bad


def gaps(bank):
    out = {}
    for c in bank["cases"]:
        for o in c.get("owed") or ():
            out.setdefault(o["by"], []).append("%s: %s wants %r, today %r (%s)" % (
                c["id"], o["prop"], o["want"], o["today"], c.get("row", "")))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("measure")
    p.add_argument("cases", nargs="*")
    sub.add_parser("gaps")
    a = ap.parse_args(argv)
    bank = load()
    if a.cmd == "gaps":
        print(json.dumps(gaps(bank), indent=1, sort_keys=True))
        return 0
    rc = 0
    for c in bank["cases"]:
        if a.cases and c["id"] not in a.cases:
            continue
        got = measure(c)
        bad = judge(c, got)
        rc = rc or (1 if bad else 0)
        print(json.dumps({"id": c["id"], "got": got, "problems": bad}, sort_keys=True))
    return rc


if __name__ == "__main__":
    sys.exit(main())
