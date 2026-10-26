"""testq/schema.py - the job and result records shared by the queue, the dispatcher, the SteveDesktop worker
and modcheck (plan design/RimMandrake/test_orchestration_two_machines_2026-10-25.md, section 3).

This file is the INTERFACE between helper H-A (testq, dispatcher, worker) and helper H-B (modcheck, the known-good
gate). It is plain stdlib so the worker can import it from the runner clone on SteveDesktop.

JOB (immutable once submitted; a change is a new job that names the old one in `supersedes`):
  schema        "testq.job/1"
  id            "J<UTC yyyymmddThhmmssZ>-<6 hex>"; unique, the key for every result (never a sha)
  item          rimflow item the run is FOR (findings and verify land there), or null
  mod           mod folder name, e.g. "FlowWorks"
  selector      {"item": [ids], "chains": [names], "rows": [ids], "full": bool}; at least one of them.
                Passed to `modcheck run <mod>` as --item/--chains/--rows/--full. "full" only for purpose=sweep.
  profile       "targeted" (modcheck's own minimal-list swap) or "full-list" (the owner's whole list); the
                dispatcher groups jobs of one host+profile into a train so a load is shared
  purpose       fix | guard | sweep | sensitivity | flake | commission.  sweep/sensitivity/flake/commission bypass
                the known-good gate (modcheck --reuse off); fix/guard use --reuse on
  priority      int, higher runs sooner (default 50)
  not_before    ISO UTC or null
  requested_by  seat that submitted it (BENCH, FOUNDRY, ...)
  source_sha    the commit whose code the run must include: the worker refuses (SOURCE_SHA_MISSING) when the
                runner's pinned HEAD does not contain it. Never taken as the deployed identity.
  supersedes    job id this one replaces (the old one is cancelled if still pending), or null
  owner_gate    null, or the reason it waits for the owner; such a job never dispatches until cleared
  lane          "stevedesktop" (default) | "archmagi" | "any"
  deploy        extra mod folders to deploy with `mod` (list)
  canary        bool (default true): modcheck --canary
  validity      bool (default true): modcheck --validity
  timeout_s     the run phase's watchdog (default 2700)

RESULT (written once per ATTEMPT by the worker into its outbox; the dispatcher keeps the last one per job):
  schema        "testq.result/1"
  job, attempt  job id; attempt id "<job id>.a<n>"
  host          the machine that ran it;  runner_sha  the runner clone's HEAD the attempt was pinned to
  outcome       DONE (modcheck ran to completion; rows say what passed) | INVALID (no usable verdict:
                `cause` says why) | INTERRUPTED (killed mid-run: watchdog or signal) | REFUSED (never started)
  cause         null | GUARD_HELD | SOURCE_SHA_MISSING | SYNC | DEPLOY | LOAD | CANARY | HANG | HARNESS |
                BLOCKED_SELECTION | CRASH | GAME_DIED (the game the attempt loaded was gone or replaced after the run)
  deployed      {"mods": {name: {"dll_sha256", "defs_sha256", "files"}}, "modsconfig_sha256_prerun"}
                what was ON DISK in the game's Mods folder when the run started - the attested identity
  rows          [{"chain", "row", "verdict", "validity", "freshness", "detail"}]; verdict is PASS | FAIL |
                UNMEASURED | NOT_RUN | SKIP (anything else is kept verbatim); validity/freshness null when
                modcheck did not say (H-B's gate fills freshness="reused@<run>")
  counts        {verdict: n}
  phase_s       {"sync": s, "load": s, "run": s, ...}
  retries       how many clean restarts the watchdog spent (at most 1)
  modcheck_exit int or null
  artifacts     [{"name", "path", "sha256", "bytes"}]  (sheet HTML/JSON, modcheck log; paths on `host`)
  started, finished   ISO UTC
  note          one line, human-readable
"""
import datetime
import json
import os
import re
import secrets

JOB_SCHEMA = "testq.job/1"
RESULT_SCHEMA = "testq.result/1"
PURPOSES = ("fix", "guard", "sweep", "sensitivity", "flake", "commission")
GATE_BYPASS = ("sweep", "sensitivity", "flake", "commission")
PROFILES = ("targeted", "full-list")
LANES = ("stevedesktop", "archmagi", "any")
OUTCOMES = ("DONE", "INVALID", "INTERRUPTED", "REFUSED")
CAUSES = (None, "GUARD_HELD", "SOURCE_SHA_MISSING", "SYNC", "DEPLOY", "LOAD", "CANARY", "HANG", "HARNESS",
          "BLOCKED_SELECTION", "CRASH", "GAME_DIED")
VERDICTS = ("PASS", "FAIL", "UNMEASURED", "NOT_RUN", "SKIP")
JOB_ID_RE = re.compile(r"^J\d{8}T\d{6}Z-[0-9a-f]{6}$")
NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
DEFAULTS = {"item": None, "profile": "targeted", "priority": 50, "not_before": None, "supersedes": None,
            "owner_gate": None, "lane": "stevedesktop", "deploy": [], "canary": True, "validity": True,
            "timeout_s": 2700, "row_items": {}}


class SchemaError(ValueError):
    pass


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_ts(s):
    """ISO UTC 'YYYY-MM-DDTHH:MM:SSZ' -> epoch seconds (timezone-safe: never mktime)."""
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc).timestamp()


def new_job_id():
    return "J%s-%s" % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"), secrets.token_hex(3))


def make_job(mod, selector, purpose, requested_by, source_sha, **kw):
    """A complete, validated job dict. Unknown keyword arguments are refused."""
    unknown = set(kw) - set(DEFAULTS)
    if unknown:
        raise SchemaError("unknown job fields: %s" % ", ".join(sorted(unknown)))
    job = {"schema": JOB_SCHEMA, "id": new_job_id(), "mod": mod, "selector": selector, "purpose": purpose,
           "requested_by": requested_by, "source_sha": source_sha, "submitted": utcnow()}
    for k, v in DEFAULTS.items():
        job[k] = kw.get(k, list(v) if isinstance(v, list) else dict(v) if isinstance(v, dict) else v)
    validate_job(job)
    return job


def validate_job(job):
    """Raise SchemaError on the first problem; return the job unchanged when it is sound."""
    def need(cond, msg):
        if not cond:
            raise SchemaError("job %s: %s" % (job.get("id"), msg))
    need(isinstance(job, dict), "not an object")
    need(job.get("schema") == JOB_SCHEMA, "schema must be %s" % JOB_SCHEMA)
    need(isinstance(job.get("id"), str) and JOB_ID_RE.match(job["id"]), "bad id")
    need(isinstance(job.get("mod"), str) and NAME_RE.match(job["mod"]), "bad mod folder name")
    sel = job.get("selector")
    need(isinstance(sel, dict) and set(sel) <= {"item", "chains", "rows", "full"}, "selector keys: item/chains/rows/full")
    for k in ("item", "chains", "rows"):
        need(isinstance(sel.get(k, []), list) and all(isinstance(x, str) and NAME_RE.match(x) for x in sel.get(k, [])),
             "selector.%s must be a list of names" % k)
    need(any(sel.get(k) for k in ("item", "chains", "rows", "full")), "selector selects nothing (no --full by default)")
    need(job.get("purpose") in PURPOSES, "purpose must be one of %s" % ", ".join(PURPOSES))
    need(not sel.get("full") or job["purpose"] == "sweep", "selector.full is for purpose=sweep only")
    need(job.get("profile") in PROFILES, "profile must be one of %s" % ", ".join(PROFILES))
    need(job.get("lane") in LANES, "lane must be one of %s" % ", ".join(LANES))
    need(isinstance(job.get("priority"), int), "priority must be an int")
    need(isinstance(job.get("requested_by"), str) and NAME_RE.match(job["requested_by"]), "requested_by must be a seat")
    need(isinstance(job.get("source_sha"), str) and SHA_RE.match(job["source_sha"]), "source_sha must be a hex sha")
    for k in ("not_before",):
        if job.get(k) is not None:
            try:
                parse_ts(job[k])
            except (TypeError, ValueError):
                need(False, "%s must be YYYY-MM-DDTHH:MM:SSZ" % k)
    need(job.get("supersedes") is None or JOB_ID_RE.match(str(job["supersedes"])), "supersedes must be a job id")
    need(job.get("item") is None or NAME_RE.match(str(job["item"])), "item must be an item id")
    ri = job.get("row_items", {})
    need(isinstance(ri, dict) and all(isinstance(k, str) and NAME_RE.match(k) and isinstance(v, str) and NAME_RE.match(v)
                                      for k, v in ri.items()), "row_items must map a row id or chain name to an item id")
    need(isinstance(job.get("deploy"), list) and all(NAME_RE.match(str(m)) for m in job["deploy"]),
         "deploy must be a list of mod folder names")
    need(isinstance(job.get("timeout_s"), int) and 60 <= job["timeout_s"] <= 6 * 3600, "timeout_s 60..21600")
    return job


def modcheck_args(job):
    """The `modcheck run` argument list a job asks for (the mod first)."""
    sel = job["selector"]
    a = [job["mod"]]
    for i in sel.get("item", []):
        a += ["--item", i]
    if sel.get("chains"):
        a += ["--chains", ",".join(sel["chains"])]
    if sel.get("rows"):
        a += ["--rows", ",".join(sel["rows"])]
    if sel.get("full"):
        a.append("--full")
    if job.get("canary", True):
        a.append("--canary")
    if job.get("validity", True):
        a.append("--validity")
    a += ["--reuse", "off" if job["purpose"] in GATE_BYPASS else "on"]
    return a


# A 300-char cap hid the evidence of a FAIL (THIRST_FIX_AWKWARD_ACCESS_ROW_FAILS): keep enough for a whole driver row.
DETAIL_CAP = 4000


def rows_from_summary(summary):
    """modcheck's sheet JSON `summary` -> result rows (one per chain component)."""
    rows = []
    for ch in summary.get("chains") or []:
        for c in ch.get("components") or []:
            rows.append({"chain": ch.get("name"), "row": c.get("name"),
                         "verdict": str(c.get("verdict") or "UNMEASURED").upper(),
                         "validity": c.get("validity"), "freshness": c.get("freshness"),
                         "detail": (c.get("detail") or "")[:DETAIL_CAP]})
    return rows


def count_verdicts(rows):
    out = {}
    for r in rows:
        out[r["verdict"]] = out.get(r["verdict"], 0) + 1
    return out


def validate_result(res):
    def need(cond, msg):
        if not cond:
            raise SchemaError("result %s: %s" % (res.get("attempt"), msg))
    need(isinstance(res, dict) and res.get("schema") == RESULT_SCHEMA, "schema must be %s" % RESULT_SCHEMA)
    need(JOB_ID_RE.match(str(res.get("job"))), "bad job id")
    need(str(res.get("attempt", "")).startswith(res["job"] + ".a"), "attempt must be <job>.a<n>")
    need(res.get("outcome") in OUTCOMES, "outcome must be one of %s" % ", ".join(OUTCOMES))
    need(res.get("cause") in CAUSES, "unknown cause %r" % res.get("cause"))
    need(res["outcome"] == "DONE" or res.get("cause"), "a non-DONE outcome needs a cause")
    need(isinstance(res.get("rows"), list), "rows must be a list")
    for r in res["rows"]:
        need(set(("chain", "row", "verdict")) <= set(r), "a row needs chain/row/verdict")
    return res


def dump(obj, path):
    """Write JSON atomically (temp file + rename in the same directory)."""
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True, default=str)
        f.write("\n")
    os.replace(tmp, path)
