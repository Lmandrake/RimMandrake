#!/usr/bin/env python3
"""The live-proof measurement protocol: a proof says what it measured, the supervisor stops guessing from its log.

LIVE_ROWS_FIX_STOP_GUESSING_LOGS (GPT test-tolerance advice 2026-11-04, rank 4, design/RimMandrake/
test_tolerance_gpt_advice_2026-11-04.md: "Replace log guessing with a measurement protocol, retaining regexes as a
migration aid"). Owner 2026-11-03: broken tests are expected; inability to measure is reported up.

A proof run by relentless_live gets RM_LIVE_RUN_ID (and RM_LIVE_CLAUSE) in its environment and prints one line per
observation:

    RMOBS {"run": "<RM_LIVE_RUN_ID>", "clause": "A2", "stage": "evaluation", "result": "VIOLATED",
           "expected": ">= 1 RM_Chittik", "observed": 0, "absence": true, "unit": "pawns", "threshold": 1,
           "prereqs": {"map": "RM_Stillsand"}, "identity": {"site": "...", "deploy": "...", "session": "..."},
           "evidence": ["/mnt/d/.../x.json"], "note": "..."}

`emit()` writes one. `read(text, run_id, clause)` turns a whole log into a Reading. Rules:
  - every RMOBS line is read, the whole log, never a tail;
  - a row for another run id is INVALID (stale or foreign evidence), a row that is not a JSON object, or lacks a field
    its result needs, is INVALID;
  - SATISFIED and VIOLATED need `expected` and `observed`; an `observed` of null is a measurement only with
    `"absence": true` (a valid query that found nothing): without it the row is UNKNOWN;
  - one valid VIOLATED decides VIOLATED: no later PASS, SATISFIED, malformed row or inability erases it;
  - else any INVALID row -> INVALID; any UNREACHED or UNKNOWN row -> that; SATISFIED only when every row is SATISFIED
    and the clause reached stage "result" (the proof says it finished);
  - no RMOBS line at all -> NONE: the caller falls back to the regex classifier (relentless_live.could_not_ask);
  - a clause with RMOBS lines but none for this clause -> UNKNOWN.
`stage` is where execution got to (STAGES); it is evidence, not attribution: a stop at launch or transport is told to
the harness, any other non-verdict to the worker."""
import json
import os
import sys

TAG = "RMOBS "
RUN_ENV = "RM_LIVE_RUN_ID"
CLAUSE_ENV = "RM_LIVE_CLAUSE"
STAGES = ("launch", "transport", "setup", "stimulus", "observation", "evaluation", "result")
RESULTS = ("SATISFIED", "VIOLATED", "UNREACHED", "UNKNOWN")
NONE, INVALID = "NONE", "INVALID"
MEASURED = ("SATISFIED", "VIOLATED")
HARNESS_STAGES = ("launch", "transport")     # a stop before the proof reached the game: the box's, never the mod's
LOG_MAX = 32 * 1024 * 1024      # a log larger than this is read head and tail, and the Reading says it was cut


def emit(clause, result, stage, expected=None, observed=None, absence=False, run=None, out=None, **extra):
    """Print one RMOBS row for this run (RM_LIVE_RUN_ID unless `run` is given). -> the row."""
    row = dict(extra, run=run if run is not None else os.environ.get(RUN_ENV, ""), clause=clause, result=result,
               stage=stage, expected=expected, observed=observed, absence=bool(absence))
    (out or sys.stdout).write(TAG + json.dumps(row, sort_keys=True, default=str) + "\n")
    (out or sys.stdout).flush()
    return row


class Reading:
    def __init__(self, status, why, stage=None, rows=(), problems=(), cut=False):
        self.status, self.why, self.stage, self.cut = status, why, stage, cut
        self.rows, self.problems = list(rows), list(problems)

    def summary(self):
        """The runs.jsonl field: small, every decision input named."""
        return {"status": self.status, "why": self.why[:300], "stage": self.stage, "rows": len(self.rows),
                "problems": [p[:160] for p in self.problems[:5]], "cut": self.cut}


def row_problem(row, run_id):
    """-> why this parsed row is INVALID, or None."""
    if not isinstance(row, dict):
        return "not a JSON object"
    if not run_id:
        return "the supervisor gave no run id, so no row can be tied to this run"
    if row.get("run") != run_id:
        return "run %r is not this run (%s): stale or foreign evidence" % (row.get("run"), run_id)
    if not isinstance(row.get("clause"), str) or not row["clause"]:
        return "no clause"
    if row.get("result") not in RESULTS:
        return "result %r is none of %s" % (row.get("result"), "/".join(RESULTS))
    if row.get("stage") not in STAGES:
        return "stage %r is none of %s" % (row.get("stage"), "/".join(STAGES))
    if row["result"] in MEASURED:
        for k in ("expected", "observed"):
            if k not in row:
                return "%s without %r" % (row["result"], k)
        if row.get("expected") is None:
            return "%s with no expected value" % row["result"]
    for k in ("prereqs", "identity"):
        if k in row and not isinstance(row[k], dict):
            return "%s is not an object" % k
    if "evidence" in row and not isinstance(row["evidence"], list):
        return "evidence is not a list"
    return None


def effective(row):
    """A valid row -> its result as a measurement: an observed null is a measurement only when the row says absence."""
    if row["result"] in MEASURED and row.get("observed") is None and not row.get("absence"):
        return "UNKNOWN"
    return row["result"]


def whole(text):
    """-> (the text to read, cut?) Never a tail: up to LOG_MAX whole, past it head and tail halves."""
    if len(text) <= LOG_MAX:
        return text, False
    return text[:LOG_MAX // 2] + "\n" + text[-LOG_MAX // 2:], True


def read(text, run_id, clause):
    """A proof's whole log -> Reading for `clause` of run `run_id`."""
    text, cut = whole(text or "")
    rows, problems, mine_bad, others = [], [], [], 0
    for n, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s.startswith(TAG.strip()):
            continue
        body = s[len(TAG.strip()):].strip()
        try:
            row = json.loads(body)
        except ValueError as e:
            problems.append("line %d: malformed RMOBS (%s)" % (n, str(e)[:60]))
            mine_bad.append(n)
            continue
        why = row_problem(row, run_id)
        if why:
            problems.append("line %d: %s" % (n, why))
            # a valid-shaped row of another clause is not this clause's problem; anything else might be
            if not (isinstance(row, dict) and row.get("clause") not in (None, clause) and row.get("run") == run_id):
                mine_bad.append(n)
            continue
        if row["clause"] == clause:
            rows.append(row)
        else:
            others += 1
    if not rows and not problems and not others:
        return Reading(NONE, "no RMOBS rows: the regex classifier reads this log (migration aid)", cut=cut)
    stage = max((STAGES.index(r["stage"]) for r in rows), default=-1)
    stage = STAGES[stage] if stage >= 0 else None
    viol = [r for r in rows if effective(r) == "VIOLATED"]
    if viol:
        r = viol[0]
        return Reading("VIOLATED", "%s VIOLATED at %s: expected %s, observed %s%s" % (
            clause, r["stage"], _v(r.get("expected")), _v(r.get("observed")), " (a measured absence)" if r.get("absence")
            else ""), stage, rows, problems, cut)
    if mine_bad:
        return Reading(INVALID, "%s: %s" % (clause, problems[0]), stage, rows, problems, cut)
    if not rows:
        return Reading("UNKNOWN", "%s: the proof wrote RMOBS rows but none for this clause" % clause, stage, rows,
                       problems, cut)
    for want in ("UNREACHED", "UNKNOWN"):
        hit = [r for r in rows if effective(r) == want]
        if hit:
            r = hit[0]
            what = (r.get("note") or ("observed null without absence: a blind read, not a measurement"
                                      if r["result"] in MEASURED else "no reason given"))
            return Reading(want, "%s %s at %s: %s" % (clause, want, r["stage"], str(what)[:200]), stage, rows,
                           problems, cut)
    if stage != "result":
        return Reading("UNKNOWN", "%s: every row SATISFIED but the proof stopped at %s, never reporting its result"
                       % (clause, stage), stage, rows, problems, cut)
    r = rows[-1]
    return Reading("SATISFIED", "%s SATISFIED: expected %s, observed %s" % (clause, _v(r.get("expected")),
                                                                            _v(r.get("observed"))),
                   stage, rows, problems, cut)


def _v(x):
    return json.dumps(x, default=str)[:80]


def read_log(path, run_id, clause):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return read(f.read(), run_id, clause)
    except OSError as e:     # no log: nothing was said in RMOBS, and the exit-code reading has nothing either
        return Reading(NONE, "the proof's log could not be read: %s" % e)


def run_id_of(log):
    """The run id the supervisor gives a proof: its log's file name without .log (unique per run, retries included)."""
    b = os.path.basename(log)
    return b[:-len(".log")] if b.endswith(".log") else b
