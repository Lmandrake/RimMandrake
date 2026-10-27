#!/usr/bin/env python3
"""Old-vs-new reader replay and the 100k commissioning run (CONTRACTS_BUILD_COMMON_READER_FIVE_RECORDS).

    python3 src/RimMandrake/contracts/replay.py fixtures            # the fixture corpus: old / new / strict per line
    python3 src/RimMandrake/contracts/replay.py real                # today's real stores through old and new readers
    python3 src/RimMandrake/contracts/replay.py commission [-n 100000] [--seed 1]
        all three write a JSON report under D:\\ClaudeWork\\rimmandrake\\contracts\\ and print a summary;
        exit 0 = every old/new difference is one the fixture manifest names as intended, 1 = an unexplained one.

OLD = each program's module as it was at --base (default the commit before contracts were wired), loaded from git;
NEW = the working tree. A decision is accept / refuse / skip / crash per line (or per document for sessions).
STRICT = the pydantic contract (contracts.models) on the decoded value, in shadow: it decides nothing in production.
"""
import argparse
import collections
import contextlib
import datetime
import importlib.util
import io
import json
import os
import random
import subprocess
import sys
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
RM = os.path.dirname(HERE)                                   # src/RimMandrake
REPO = os.path.dirname(os.path.dirname(RM))
BASE = "c8d1d12855"                                          # HEAD before the contracts wiring (2026-10-27)
OUT = "/mnt/d/ClaudeWork/rimmandrake/contracts"
if RM not in sys.path:
    sys.path.append(RM)
from contracts import compat as CC, jsonl as CJ, models as CM  # noqa: E402
from contracts.fixtures import make_fixtures as FX  # noqa: E402

A, R, S, C = "accept", "refuse", "skip", "crash"
REL = {"close_evidence": "src/RimMandrake/Utils/close_evidence.py", "audits": "src/RimMandrake/rimflow/audits.py",
       "arbiter_pending": "src/RimMandrake/rimflow/arbiter_pending.py",
       "dispatcher": "src/RimMandrake/rimflow/dispatcher.py", "testq": "src/RimMandrake/Utils/testq/testq.py"}
for d in ("Utils", "rimflow", os.path.join("Utils", "testq")):
    if os.path.join(RM, d) not in sys.path:
        sys.path.append(os.path.join(RM, d))


def load_module(name, rel, base=None):
    """The module at `rel`, from git `base` (old) or the working tree (new), under a private name."""
    path = os.path.join(REPO, rel)
    if base:
        src = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (base, rel)], capture_output=True, text=True,
                             check=True).stdout
    else:
        with open(path, encoding="utf-8") as f:
            src = f.read()
    mod = types.ModuleType(name)
    mod.__file__ = path
    sys.modules[name] = mod
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(src, path, "exec"), mod.__dict__)
    return mod


class Readers:
    """One family -> decision function, for the old and the new module set."""

    def __init__(self, base, tmp):
        self.tmp = tmp
        self.old = {k: load_module("old_" + k, v, base) for k, v in REL.items()}
        self.new = {k: load_module("new_" + k, v, None) for k, v in REL.items()}
        self.day = datetime.datetime.now(datetime.timezone.utc).date().isoformat()

    # each reader takes one raw line (str; surrogateescape for undecodable bytes) and returns a decision
    def close_evidence(self, which, line):
        m = getattr(self, which)["close_evidence"]
        folder = os.path.join(self.tmp, "ce")
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, self.day + ".jsonl"), "wb") as f:
            f.write(line.encode("utf-8", "surrogateescape") + b"\n")
        bad = []
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                rows = m.read_all(days=1, folder=folder, bad_out=bad)
        except BaseException as e:  # noqa: BLE001 - a crash is a decision here
            return C, type(e).__name__
        return (A if rows else R if bad else S), None

    def audits(self, which, line):
        m = getattr(self, which)["audits"]
        try:
            rows = m.parse(line + "\n")
        except ValueError:
            return R, None
        except BaseException as e:  # noqa: BLE001
            return C, type(e).__name__
        return (A if rows else S), None

    def verdicts(self, which, line):
        m = getattr(self, which)["arbiter_pending"]
        p = os.path.join(self.tmp, "verdicts.jsonl")
        with open(p, "wb") as f:
            f.write(line.encode("utf-8", "surrogateescape") + b"\n")
        try:
            got = m.read_stores(verdicts=p, history=os.path.join(self.tmp, "absent_history.jsonl"),
                                cutoff=os.path.join(self.tmp, "absent_cutoff.json"))
        except ValueError:
            return R, None
        except BaseException as e:  # noqa: BLE001
            return C, type(e).__name__
        return (A if got["verdicts"] else S), None

    def ledger_events(self, which, line):
        m = getattr(self, which)["dispatcher"]
        shard = os.path.join(self.tmp, "clone", "infrastructure", "state", "ledger", "events")
        os.makedirs(shard, exist_ok=True)
        with open(os.path.join(shard, "BENCH.jsonl"), "wb") as f:
            f.write(line.encode("utf-8", "surrogateescape") + b"\n")
        try:
            got = m.seat_events_since(os.path.join(self.tmp, "clone"), "BENCH", "2026-10-27T00:00:00Z")
        except BaseException as e:  # noqa: BLE001
            return C, type(e).__name__
        return (A if got else S), None

    def sessions(self, which, line):
        m = getattr(self, which)["dispatcher"]
        try:                    # as observe_agents: any parse failure (RecursionError too) is UNMEASURED == refuse
            data = json.loads(line)
        except Exception:  # noqa: BLE001
            return R, None
        try:
            return (A if m.sessions_ok(data) else R), None
        except BaseException as e:  # noqa: BLE001
            return C, type(e).__name__

    def testq_results(self, which, line):
        r = CJ.decode(line, need_object=False)
        if not r.ok:
            return R, None
        res = r.value
        if which == "old":            # testq.py at BASE, lines 242 and 316: the schema tag on a dict
            try:
                return (A if res.get("schema") == "testq.result/1" else R), None
            except AttributeError as e:
                return C, type(e).__name__
        return (A if CC.testq_result_readable(res) else R), None


def strict(family, line):
    """-> (accept|refuse|skip, reason): the strict contract in shadow, on the leniently decoded value."""
    need_obj = family not in ("sessions",)
    r = CJ.decode(line.encode("utf-8", "surrogateescape").decode("utf-8", "replace"), need_object=need_obj)
    if not r.ok:
        return (S, r.code) if r.code == CJ.BLANK else (R, r.code)
    v = r.value
    if family == "close_evidence":
        kind, e = CM.close_evidence_kind(v)
        return (R, "; ".join(e[:2])) if kind == "fault" else (A, kind)
    if family == "audits":
        e = CM.errors(CM.AuditRecord, v)
    elif family == "verdicts":
        e = CM.errors(CM.ArbiterVerdict, v)
    elif family == "tiers_history":
        e = CM.errors(CM.TiersHistoryRow, v)
    elif family == "ledger_events":
        e = CM.errors(CM.LedgerEventMin, v)
    elif family == "sessions":
        e = CM.sessions_problems(v)
    elif family == "testq_results":
        e = CM.errors(CM.TestqResult, v)
    else:
        raise KeyError(family)
    return (R, "; ".join(e[:2])) if e else (A, "")


FAMILIES = ("close_evidence", "audits", "verdicts", "ledger_events", "sessions", "testq_results")


def judge(readers, family, line):
    fn = getattr(readers, family)
    old, oe = fn("old", line)
    new, ne = fn("new", line)
    st, why = strict(family, line)
    return {"old": old, "new": new, "strict": st, "old_exc": oe, "new_exc": ne, "strict_why": why}


def run_fixtures(readers):
    rows, bad = [], []
    for fam in FAMILIES:
        for i, (line, exp) in enumerate(FX.load(fam), 1):
            got = judge(readers, fam, line)
            row = {"family": fam, "n": i, "class": exp["class"], "where": exp["where"], "why": exp["why"], **got}
            for k in ("old", "new", "strict"):
                if got[k] != exp[k]:
                    bad.append("%s#%d %s: %s %s, expected %s" % (fam, i, exp["class"], k, got[k], exp[k]))
            rows.append(row)
    diffs = [r for r in rows if r["old"] != r["new"]]
    unexplained = [r for r in diffs if "DISAGREEMENT" not in r["why"]]
    return {"lines": len(rows), "expectation_misses": bad, "old_new_diffs": diffs, "unexplained": unexplained,
            "strict_vs_new": [r for r in rows if r["strict"] != r["new"] and r["new"] != S]}


# ------------------------------------------------------------------ real stores

def run_real(readers):
    rep = {}
    # close_evidence: the whole live store through old and new read_all (rows and bad lines must be identical)
    ev = "/mnt/d/ClaudeWork/rimmandrake/evidence"
    outs = {}
    for w in ("old", "new"):
        bad = []
        with contextlib.redirect_stderr(io.StringIO()):
            rows = getattr(readers, w)["close_evidence"].read_all(days=400, folder=ev, bad_out=bad)
        outs[w] = (rows, bad)
    kinds = collections.Counter()
    strict_faults = collections.Counter()
    for r in outs["new"][0]:
        k, e = CM.close_evidence_kind(r)
        kinds[k] += 1
        if k == "fault":
            strict_faults["; ".join(e[:2])] += 1
    shaped = sum(1 for r in outs["new"][0] if r.get("v") == 4 and
                 (CM.close_evidence_kind(r)[0] == "v4" and CM.CloseEvidenceV4.model_validate(r).evidence_shaped)
                 != (readers.new["close_evidence"].schema_problems(r) == []))
    rep["close_evidence"] = {"rows": len(outs["new"][0]), "bad": len(outs["new"][1]),
                             "old_equals_new": outs["old"] == outs["new"], "strict_kinds": dict(kinds),
                             "strict_faults": dict(strict_faults), "shape_vs_schema_problems_disagree": shaped}
    # audits: the live file (may be empty; the size says the instrument looked)
    ap = "/mnt/d/ClaudeWork/rimmandrake/auditor/audits.jsonl"
    try:
        size = os.path.getsize(ap)
        o = readers.old["audits"].read(ap)
        n = readers.new["audits"].read(ap)
        rep["audits"] = {"bytes": size, "rows": len(n), "old_equals_new": o == n}
    except (OSError, ValueError) as e:
        rep["audits"] = {"error": "%s: %s" % (type(e).__name__, e)}
    # arbiter verdicts + tiers_history
    vp = readers.new["arbiter_pending"].VERDICTS
    th = "/mnt/d/ClaudeWork/rimmandrake/review_v3_Y/remeasure_data/tiers_history.jsonl"
    o = readers.old["arbiter_pending"].read_jsonl(th, ("item", "sha", "decision"))
    n = readers.new["arbiter_pending"].read_jsonl(th, ("item", "sha", "decision"))
    tf = collections.Counter()
    for d in n:
        e = CM.errors(CM.TiersHistoryRow, d)
        if e:
            tf["; ".join(e[:2])] += 1
    rep["arbiter"] = {"verdicts_file_exists": os.path.exists(vp), "tiers_history_rows": len(n),
                      "tiers_old_equals_new": o == n, "tiers_strict_faults": dict(tf)}
    # dispatcher: the captured `claude agents --json`, and every seat shard of this clone
    cap = "/mnt/d/ClaudeWork/rimmandrake/contracts/agents_capture_2026-10-27.json"
    data = json.load(open(cap, encoding="utf-8")) if os.path.exists(cap) else None
    seats = {}
    shard_dir = os.path.join(REPO, "infrastructure", "state", "ledger", "events")
    for fn in sorted(os.listdir(shard_dir)):
        if fn.endswith(".jsonl"):
            seat = fn[:-6]
            o = readers.old["dispatcher"].seat_events_since(REPO, seat, "2026-10-20T00:00:00Z")
            n = readers.new["dispatcher"].seat_events_since(REPO, seat, "2026-10-20T00:00:00Z")
            seats[seat] = {"events": len(n), "old_equals_new": o == n}
    rep["dispatcher"] = {"capture": cap if data is not None else None,
                         "sessions_ok_old": readers.old["dispatcher"].sessions_ok(data) if data is not None else None,
                         "sessions_ok_new": readers.new["dispatcher"].sessions_ok(data) if data is not None else None,
                         "strict_problems": CM.sessions_problems(data) if data is not None else None,
                         "seat_events_since_2026-10-20": seats}
    # testq: every done/ and orphans/ result, and records() of every state, old vs new
    q = os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq")
    res, rf, sv = collections.Counter(), collections.Counter(), collections.Counter()
    for sub in ("done", "orphans"):
        d = os.path.join(q, sub)
        for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if not fn.endswith(".json"):
                continue
            with open(os.path.join(d, fn), encoding="utf-8") as f:
                doc = json.load(f)
            r = doc.get("result", doc) if sub == "done" else doc
            old = r.get("schema") == "testq.result/1"
            new = CC.testq_result_readable(r)
            res["same" if old == new else "differ"] += 1
            e = CM.errors(CM.TestqResult, r)
            if e:
                rf["; ".join(e[:2])] += 1
            try:
                readers.new["testq"].S.validate_result(r)
                sv["validate_result ok"] += 1
            except Exception as ex:  # noqa: BLE001
                sv["validate_result: %s" % ex] += 1
    states = {}
    for st in ("pending", "running", "done", "cancelled"):
        with contextlib.redirect_stderr(io.StringIO()):
            o = readers.old["testq"].records(st)
            n = readers.new["testq"].records(st)
        states[st] = {"records": len(n), "old_equals_new": o == n}
    rep["testq"] = {"queue": q, "results": dict(res), "strict_faults": dict(rf), "validate_result": dict(sv),
                    "records": states}
    return rep


# ------------------------------------------------------------------ 100k commissioning

def _mutate(rng, line):
    """-> (mutated line, mutation name). Damage the way the reviews saw it."""
    k = rng.randrange(8)
    if k == 0 or not line:
        return line, "none"
    if k == 1:
        return line[: rng.randrange(len(line))], "truncate"
    if k == 2:
        i = rng.randrange(len(line))
        return line[:i] + chr(rng.choice((0x22, 0x7b, 0x5d, 0x2c, 0xfffd, 0x41))) + line[i + 1:], "char_flip"
    if k == 3 and line.endswith("}"):
        return line[:-1] + ', "ts": "2026-10-27T12:00:00Z"}', "dup_key"
    try:
        d = json.loads(line)
    except (ValueError, RecursionError):
        return line, "none"
    if not isinstance(d, dict) or not d:
        return line, "none"
    key = rng.choice(sorted(d))
    if k == 4:
        d.pop(key)
        return json.dumps(d), "drop_field"
    if k == 5:
        d[key] = rng.choice((None, 0, 1.5, True, [], {}, "", "x" * 3, [None]))
        return json.dumps(d), "retype_field"
    if k == 6:
        return json.dumps(d) + json.dumps(d), "two_objects_glued"
    return json.dumps([d]), "wrap_list"


def commission(readers, n, seed):
    rng = random.Random(seed)
    pool = {fam: [ln for ln, e in FX.load(fam) if ln != FX.DEEP_LINE] for fam in FAMILIES}
    # real lines join the pool: live close_evidence, tiers_history shaped as verdicts, real testq results
    ev = "/mnt/d/ClaudeWork/rimmandrake/evidence"
    for fn in sorted(os.listdir(ev)):
        if fn.endswith(".jsonl"):
            with open(os.path.join(ev, fn), encoding="utf-8", errors="replace") as f:
                pool["close_evidence"] += [ln.rstrip("\n") for ln in f if ln.strip()]
    q = "/mnt/d/ClaudeWork/rimmandrake/testq/done"
    for fn in sorted(os.listdir(q))[:60]:
        with open(os.path.join(q, fn), encoding="utf-8") as f:
            pool["testq_results"].append(json.dumps(json.load(f)["result"]))
    acct = collections.Counter()
    diffs = collections.Counter()
    examples = {}
    errors = 0
    t0 = time.time()
    for i in range(n):
        fam = FAMILIES[i % len(FAMILIES)]
        line, mut = _mutate(rng, rng.choice(pool[fam]))
        if "\n" in line:
            line = line.replace("\n", " ")
        if i % 997 == 0:
            line, mut = FX.DEEP_LINE, "deep"
        try:
            g = judge(readers, fam, line)
        except BaseException as e:  # noqa: BLE001 - the harness itself; counted, never hidden
            errors += 1
            acct[(fam, "HARNESS_ERROR", type(e).__name__)] += 1
            continue
        acct[(fam, "new=" + g["new"], "strict=" + g["strict"])] += 1
        if g["old"] != g["new"]:
            key = (fam, g["old"], g["new"], g["old_exc"] or "", mut)
            diffs[key] += 1
            examples.setdefault(key, line[:200])
    dt = time.time() - t0
    total = sum(acct.values())
    return {"n": n, "seed": seed, "seconds": round(dt, 1), "accounted": total, "harness_errors": errors,
            "outcomes": {"|".join(k): v for k, v in sorted(acct.items())},
            "old_new_diffs": [{"family": k[0], "old": k[1], "new": k[2], "old_exc": k[3], "mutation": k[4],
                               "count": v, "example": examples[k]} for k, v in sorted(diffs.items())]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("what", choices=("fixtures", "real", "commission"))
    ap.add_argument("--base", default=BASE)
    ap.add_argument("-n", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    sys.setrecursionlimit(1000)
    with tempfile.TemporaryDirectory(prefix="contracts_replay_") as tmp:
        rd = Readers(a.base, tmp)
        if a.what == "fixtures":
            rep = run_fixtures(rd)
            ok = not rep["expectation_misses"] and not rep["unexplained"]
            summary = "fixtures: %d lines, %d expectation misses, %d old/new diffs (%d unexplained)" % (
                rep["lines"], len(rep["expectation_misses"]), len(rep["old_new_diffs"]), len(rep["unexplained"]))
        elif a.what == "real":
            rep = run_real(rd)
            eq = [k for k, v in _flat_eq(rep)]
            ok = all(v for k, v in _flat_eq(rep))
            summary = "real: %d old/new comparisons, %d differ" % (len(eq), sum(1 for k, v in _flat_eq(rep) if not v))
        else:
            rep = commission(rd, a.n, a.seed)
            unexplained = [d for d in rep["old_new_diffs"] if not (d["old"] == C and d["new"] in (R, S))]
            rep["unexplained"] = unexplained
            ok = rep["accounted"] == a.n and not rep["harness_errors"] and not unexplained
            summary = "commission: %d records, %d accounted, %d harness errors, %d old/new diff kinds " \
                      "(%d unexplained), %.1fs" % (a.n, rep["accounted"], rep["harness_errors"],
                                                   len(rep["old_new_diffs"]), len(unexplained), rep["seconds"])
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "replay_%s_%s.json" % (a.what, time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1, default=str)
    print("%s -> %s %s" % (summary, path, "OK" if ok else "UNEXPLAINED"))
    return 0 if ok else 1


def _flat_eq(rep, prefix=""):
    for k, v in rep.items():
        if isinstance(v, dict):
            yield from _flat_eq(v, prefix + k + ".")
        elif "equals" in k:
            yield prefix + k, v


if __name__ == "__main__":
    sys.exit(main())
