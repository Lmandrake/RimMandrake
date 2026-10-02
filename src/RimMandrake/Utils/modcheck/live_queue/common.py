"""Shared plumbing for the northstar live job queue (design/RimMandrake/northstar_live_queue_2026-10-01.md).

Every job is one file `jN_*.py` with a `body(session, job)` and runs as
    python.exe src/RimMandrake/Utils/modcheck/live_queue/jN_x.py [--dry-run]
It prints exactly one verdict line, `MEASURED PASS|FAIL <job> ...` or `UNMEASURED <job> ...`, and appends one
JSON line to the results file. `--dry-run` drives rimdrive.fake.FakeWorld instead of the bridge and writes to a
separate dry-run results file, so a rehearsal can never mark a live job done.

MEASURED means the job read the game and every check it needed was answered; its verdict is PASS only if every
check passed. UNMEASURED means it could not ask (bridge down, tool missing, setup refused) -- that is never a
FAIL against anything, and run_next.py offers the job again.
"""
import contextlib
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
MODCHECK = os.path.dirname(HERE)
UTILS = os.path.dirname(MODCHECK)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(UTILS)))
for _p in (UTILS, MODCHECK):
    if _p not in sys.path:
        sys.path.insert(0, _p)

OUTDIR = os.path.join(ROOT, "Transient", "modcheck", "live_queue")
RESULTS_LIVE = os.path.join(ROOT, "Transient", "modcheck", "live_queue_results.jsonl")
RESULTS_DRY = os.path.join(OUTDIR, "dryrun_results.jsonl")

MEASURED, UNMEASURED = "MEASURED", "UNMEASURED"
PASS, FAIL = "PASS", "FAIL"


def results_path(dry_run):
    env = os.environ.get("LIVE_QUEUE_RESULTS")
    if env:
        return env
    return RESULTS_DRY if dry_run else RESULTS_LIVE


def read_results(dry_run=False, path=None):
    path = path or results_path(dry_run)
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except ValueError:
                        pass
    except OSError:
        pass
    return out


class Unmeasurable(Exception):
    """Raised by a job body when it cannot ask the game the question (not a verdict)."""


class Job(object):
    def __init__(self, job_id, dry_run=False):
        self.id, self.dry_run = job_id, dry_run
        self.checks = []          # {"name","ok","detail"}
        self.evidence = {}
        self.unmeasured_reason = None
        self.started = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.outdir = os.path.join(OUTDIR, ("dry_" if dry_run else "") + job_id)
        os.makedirs(self.outdir, exist_ok=True)

    def check(self, name, ok, detail=""):
        self.checks.append({"name": name, "ok": bool(ok), "detail": str(detail)[:600]})
        print("  %s %s%s" % ("ok  " if ok else "FAIL", name, ("  -- " + str(detail)[:300]) if detail and not ok else ""))
        return bool(ok)

    def note(self, key, value):
        self.evidence[key] = value

    def unmeasured(self, reason):
        self.unmeasured_reason = str(reason)[:800]

    def finish(self):
        if self.unmeasured_reason is None and not self.checks:
            self.unmeasured_reason = "job asserted nothing"
        status = UNMEASURED if self.unmeasured_reason else MEASURED
        verdict = None if status == UNMEASURED else (PASS if all(c["ok"] for c in self.checks) else FAIL)
        rec = {"job": self.id, "status": status, "verdict": verdict, "dry_run": self.dry_run,
               "started": self.started, "finished": time.strftime("%Y-%m-%dT%H:%M:%S"),
               "checks_passed": sum(c["ok"] for c in self.checks), "checks_total": len(self.checks),
               "failed": [c["name"] for c in self.checks if not c["ok"]],
               "unmeasured_reason": self.unmeasured_reason, "checks": self.checks,
               "evidence": self.evidence, "outdir": os.path.relpath(self.outdir, ROOT)}
        path = results_path(self.dry_run)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, default=str) + "\n")
        if status == UNMEASURED:
            print("UNMEASURED %s -- %s" % (self.id, self.unmeasured_reason))
        else:
            print("MEASURED %s %s -- %d/%d checks%s" % (verdict, self.id, rec["checks_passed"], rec["checks_total"],
                                                     (" ; failed: " + ", ".join(rec["failed"])) if rec["failed"] else ""))
        print("  results: %s" % path)
        return rec


def call(s, tool, **p):
    """session.call that always returns a dict (Session already parses; FakeWorld returns dicts)."""
    r = s.call(tool, **p)
    if isinstance(r, dict) and r.get("content") and isinstance(r["content"], list):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:                                       # noqa: BLE001
            pass
    return r if isinstance(r, dict) else {"success": False, "message": "non-dict result %r" % (r,)}


def tool_present(s, name):
    tools = getattr(s, "tools", None)
    if tools:
        return name in tools
    return hasattr(s, "_t_" + name.replace("/", "_"))       # FakeWorld


@contextlib.contextmanager
def open_session(dry_run, fake_builder=None):
    if dry_run:
        from rimdrive.fake import FakeWorld, pawn_row
        w = fake_builder() if fake_builder else FakeWorld(pawns=[pawn_row("Col1"), pawn_row("Col2", x=103),
                                                                 pawn_row("Col3", x=106)])
        yield w
        return
    from rimdrive import Session
    with Session(lock=None) as s:
        yield s


def main(job_id, body, fake_builder=None, argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    dry = "--dry-run" in argv
    job = Job(job_id, dry_run=dry)
    print("== %s%s" % (job_id, " (DRY RUN on FakeWorld)" if dry else ""))
    try:
        with open_session(dry, fake_builder) as s:
            body(s, job)
    except Unmeasurable as e:
        job.unmeasured(e)
    except Exception as e:                                      # noqa: BLE001
        job.note("traceback", traceback.format_exc()[-2000:])
        job.unmeasured("%s: %s" % (type(e).__name__, e))
    rec = job.finish()
    if rec["status"] == UNMEASURED:
        return 2
    return 0 if rec["verdict"] == PASS else 1
