#!/usr/bin/env python3
"""contracts.replay_worker -- ONE side (old or new) of the old/new reader replay, in its own process.

    python3 -E -P replay_worker.py --tree TREE --input in.jsonl --output out.jsonl --tmp DIR

contracts/replay.py starts this twice: once against an isolated copy of the source tree at the base commit (OLD) and
once against an isolated copy of the working tree (NEW). The process imports ONLY from TREE (python -P: not even this
file's own directory), so an old reader can never borrow a new helper through a shared sys.path or sys.modules
(GPT review contracts #3). STDLIB ONLY here: what the readers import is their business.

Input, one JSON object per line:
  {"i": n, "family": F, "b64": raw bytes[, "seat": S]}  -- one record through family F's real reader path
  {"i": n, "whole": W, "arg": ...}                 -- a whole-store read (real mode), W in WHOLE
Output: first a header {"i": -1, "modules": {name: sha256 of the file each reader was imported from}} (the parent
checks it against git BASE / the working tree: the proof of which code ran), then one line per input line, same order:
  {"i": n, "d": accept|refuse|skip|crash, "exc": exception class or null, "out": sha256 of the reader's result or
   null, "why": short text}
A record the reader crashed on is a decision (crash + exc), never a worker failure; the parent counts lines and
refuses a short output file.
"""
import argparse
import base64
import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import types

A, R, S, C = "accept", "refuse", "skip", "crash"
SINCE = "2026-10-27T00:00:00Z"
JOB = "J20261027T120000Z-abcdef"


PATHS = []      # (path, placeholder): this side's private tmp/tree paths, which differ between the sides by design


def digest(obj):
    s = json.dumps(obj, sort_keys=True, default=repr, ensure_ascii=True)
    for p, ph in PATHS:
        s = s.replace(p, ph)
    return hashlib.sha256(s.encode("ascii")).hexdigest()[:20]


class FakeProc:
    def __init__(self, stdout_bytes):
        # subprocess.run(..., text=True) decodes stdout strictly (locale UTF-8): an undecodable byte raises there
        self.stdout = stdout_bytes.decode("utf-8")
        self.stderr = ""
        self.returncode = 0


def shim(answer):
    """-> a stand-in for the `subprocess` module whose run() answers `answer(argv) -> bytes` (stdout)."""
    def run(argv, **_kw):
        return FakeProc(answer(argv))
    return types.SimpleNamespace(run=run, TimeoutExpired=subprocess.TimeoutExpired, DEVNULL=subprocess.DEVNULL,
                                 PIPE=subprocess.PIPE, CalledProcessError=subprocess.CalledProcessError)


class Side:
    def __init__(self, tree, tmp):
        self.tree, self.tmp = tree, tmp
        rm = os.path.join(tree, "src", "RimMandrake")
        for d in (rm, os.path.join(rm, "Utils"), os.path.join(rm, "rimflow"), os.path.join(rm, "Utils", "testq")):
            sys.path.insert(0, d)
        os.environ["TESTQ_QUEUE"] = os.path.join(tmp, "testq_import")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            import close_evidence, audits, arbiter_pending, dispatcher, testq   # noqa: E401
        self.m = {"close_evidence": close_evidence, "audits": audits, "arbiter_pending": arbiter_pending,
                  "dispatcher": dispatcher, "testq": testq}
        for k, mod in self.m.items():       # the isolation proof: every reader was loaded from TREE
            if not os.path.realpath(mod.__file__).startswith(os.path.realpath(tree) + os.sep):
                raise SystemExit("isolation broken: %s from %s" % (k, mod.__file__))
        self.n = 0

    def fresh(self, name):
        self.n += 1
        d = os.path.join(self.tmp, "%s_%d" % (name, self.n))
        os.makedirs(d)
        return d

    # ---- one record (bytes) through the real reader path -> (decision, result object or None, why)
    def close_evidence(self, raw):
        folder = self.fresh("ce")
        import datetime
        day = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        with open(os.path.join(folder, day + ".jsonl"), "wb") as f:
            f.write(raw + b"\n")
        bad = []
        rows = self.m["close_evidence"].read_all(days=1, folder=folder, bad_out=bad)
        shutil.rmtree(folder, ignore_errors=True)
        return (A if rows else R if bad else S), [rows, bad], ""

    def audits(self, raw):
        """audits.read(): the real path (strict UTF-8 text file -> parse), not parse() on pre-decoded text."""
        return self._jsonl(raw, self.m["audits"].read)

    def _jsonl(self, raw, fn):
        p = os.path.join(self.tmp, "store.jsonl")
        with open(p, "wb") as f:
            f.write(raw + b"\n")
        try:
            got = fn(p)
        except ValueError as e:
            return R, None, str(e)[:120]
        return (A if got else S), got, ""

    def verdicts(self, raw):
        ap = self.m["arbiter_pending"]
        d, got, why = self._jsonl(raw, lambda p: ap.read_stores(
            verdicts=p, history=os.path.join(self.tmp, "absent_history.jsonl"),
            cutoff=os.path.join(self.tmp, "absent_cutoff.json")))
        return (d if d != A or got["verdicts"] else S), got, why

    def tiers_history(self, raw):
        ap = self.m["arbiter_pending"]
        return self._jsonl(raw, lambda p: ap.read_jsonl(p, ("item", "sha", "decision")))

    def ledger_events(self, raw, seat="BENCH"):
        clone = self.fresh("clone")
        shard = os.path.join(clone, "infrastructure", "state", "ledger", "events")
        os.makedirs(shard)
        with open(os.path.join(shard, seat + ".jsonl"), "wb") as f:
            f.write(raw + b"\n")
        try:
            got = self.m["dispatcher"].seat_events_since(clone, seat, SINCE)
        finally:
            shutil.rmtree(clone, ignore_errors=True)
        return (A if got else S), got, ""

    def sessions(self, raw):
        dp = self.m["dispatcher"]
        dp.subprocess = shim(lambda argv: raw)
        dp.claude_exe = lambda: "claude"
        got = dp.observe_agents()
        return (A if got.get("state") == "MEASURED" else R), got.get("sessions"), got.get("why") or ""

    def _testq(self, raw):
        tq = self.m["testq"]
        qd = self.fresh("q")
        tq.QHOME = qd
        for st in tq.STATES + ("orphans",):
            os.makedirs(os.path.join(qd, st))

        def answer(argv):
            cmd = argv[-1]
            if "worker.py status" in cmd:
                return json.dumps({"attempt": JOB + ".a1", "state": "done"}).encode()
            if "worker.py result" in cmd:
                return raw
            return b"{}"
        tq.subprocess = shim(answer)
        return tq, qd

    def testq_results(self, raw):
        """testq.reconcile(): the collect path for a running job whose worker says done."""
        tq, qd = self._testq(raw)
        job = {"schema": "testq.job/1", "id": JOB}
        rec = {"job": job, "attempt": JOB + ".a1", "attempts": [JOB + ".a1"], "host": "stevedesktop"}
        tq.S.dump(rec, os.path.join(qd, "running", JOB + ".json"))
        try:
            tq.reconcile(rec)
            done = tq.read_json(os.path.join(qd, "done", JOB + ".json"))
        finally:
            shutil.rmtree(qd, ignore_errors=True)
        if done is None:
            return R, None, ""
        done.pop("finished", None)                 # the wall clock, not a decision
        return A, done, ""

    def testq_orphans(self, raw):
        """testq.drain_outbox(): the orphan path for an attempt in the worker outbox that no job claims."""
        tq, qd = self._testq(raw)
        aid = JOB + ".a1"
        try:
            tq.drain_outbox([aid])
            kept = tq.read_json(os.path.join(qd, "orphans", aid + ".json"))
        finally:
            shutil.rmtree(qd, ignore_errors=True)
        return (A if kept is not None else R), kept, ""

    # ---- whole stores (real mode)
    def whole(self, w, arg):
        if w == "close_evidence_read_all":
            bad = []
            rows = self.m["close_evidence"].read_all(days=400, folder=arg, bad_out=bad)
            return A, [rows, bad], "%d rows %d bad" % (len(rows), len(bad))
        if w == "audits_read":
            rows = self.m["audits"].read(arg)
            return A, rows, "%d rows" % len(rows)
        if w == "tiers_read_jsonl":
            rows = self.m["arbiter_pending"].read_jsonl(arg, ("item", "sha", "decision"))
            return A, rows, "%d rows" % len(rows)
        if w == "verdicts_read_stores":
            got = self.m["arbiter_pending"].read_stores(verdicts=arg[0], history=arg[1], cutoff=arg[2])
            return A, got, "%d verdicts" % len(got["verdicts"])
        if w == "seat_events_since":
            got = self.m["dispatcher"].seat_events_since(arg[0], arg[1], arg[2])
            return A, got, "%d events" % len(got)
        if w == "testq_records":
            tq = self.m["testq"]
            tq.QHOME = arg[0]
            got = tq.records(arg[1])
            return A, got, "%d records" % len(got)
        raise KeyError(w)


FAMILIES = ("close_evidence", "audits", "verdicts", "tiers_history", "ledger_events", "sessions", "testq_results",
            "testq_orphans")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--tmp", required=True)
    a = ap.parse_args(argv)
    sys.setrecursionlimit(1000)
    side = Side(a.tree, a.tmp)
    for p, ph in ((os.path.realpath(a.tmp), "<TMP>"), (a.tmp, "<TMP>"), (os.path.realpath(a.tree), "<TREE>"),
                  (a.tree, "<TREE>")):
        PATHS.append((json.dumps(p)[1:-1], ph))
    PATHS.sort(key=lambda t: -len(t[0]))
    sink = io.StringIO()
    mods = {}
    for k, mod in side.m.items():
        with open(mod.__file__, "rb") as f:
            mods[k] = hashlib.sha256(f.read()).hexdigest()
    with open(a.input, encoding="utf-8") as fin, open(a.output, "w", encoding="utf-8") as fout:
        fout.write(json.dumps({"i": -1, "modules": mods}) + "\n")
        for ln in fin:
            job = json.loads(ln)
            exc, out, why = None, None, ""
            try:
                with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                    if "whole" in job:
                        d, res, why = side.whole(job["whole"], job["arg"])
                    else:
                        args = (base64.b64decode(job["b64"]),) + ((job["seat"],) if "seat" in job else ())
                        d, res, why = getattr(side, job["family"])(*args)
                out = digest(res) if res is not None else None
            except BaseException as e:  # noqa: BLE001 - a reader crash is a decision, recorded per record
                if isinstance(e, KeyboardInterrupt):
                    raise
                d, exc, why = C, type(e).__name__, str(e)[:120]
            sink.seek(0)
            sink.truncate()
            fout.write(json.dumps({"i": job["i"], "d": d, "exc": exc, "out": out, "why": why}) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
