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
  gate          null (modcheck default) or on/off/shadow: passed to modcheck run --gate
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
import sys

JOB_SCHEMA = "testq.job/1"
RESULT_SCHEMA = "testq.result/1"
PURPOSES = ("fix", "guard", "sweep", "sensitivity", "flake", "commission")
GATE_BYPASS = ("sweep", "sensitivity", "flake", "commission")
PROFILES = ("targeted", "full-list")
GATES = ("on", "off", "shadow")  # modcheck run --gate choices; None = modcheck default
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
            "timeout_s": 2700, "row_items": {}, "gate": None}


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
            raise SchemaError("job %s: %s" % (job.get("id") if isinstance(job, dict) else None, msg))
    need(isinstance(job, dict), "not an object")
    need(job.get("schema") == JOB_SCHEMA, "schema must be %s" % JOB_SCHEMA)
    need(isinstance(job.get("id"), str) and JOB_ID_RE.match(job["id"]), "bad id")
    need(isinstance(job.get("mod"), str) and NAME_RE.match(job["mod"]), "bad mod folder name")
    sel = job.get("selector")
    need(isinstance(sel, dict) and set(sel) <= {"item", "chains", "rows", "full"}, "selector keys: item/chains/rows/full")
    for k in ("item", "chains", "rows"):
        need(isinstance(sel.get(k, []), list) and all(isinstance(x, str) and NAME_RE.match(x) for x in sel.get(k, [])),
             "selector.%s must be a list of names" % k)
    need(sel.get("full") in (None, True, False), "selector.full must be a boolean")
    need(any(sel.get(k) for k in ("item", "chains", "rows", "full")), "selector selects nothing (no --full by default)")
    need(job.get("purpose") in PURPOSES, "purpose must be one of %s" % ", ".join(PURPOSES))
    need(not sel.get("full") or job["purpose"] == "sweep", "selector.full is for purpose=sweep only")
    need(job.get("profile") in PROFILES, "profile must be one of %s" % ", ".join(PROFILES))
    need(job.get("gate") in (None,) + GATES, "gate must be one of %s" % ", ".join(GATES))
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
    for k in ("canary", "validity"):
        need(isinstance(job.get(k), bool), "%s must be a boolean" % k)
    need(isinstance(job.get("timeout_s"), int) and 60 <= job["timeout_s"] <= 6 * 3600, "timeout_s 60..21600")
    return job


# ---- deploy names: what `--deploy` / job["mod"] may be, and how deploy_custom_mods.py is asked for each --------------
_SRC_TIERS = ("RimMandrake", "RimStarWars", "RimUtinni", "SPLIT_Phase3")


def deploy_catalog(src_root):
    """-> (known {mod folder name}, folded {source folder -> composed target}, composed {target names}).

    `deploy_custom_mods.py --mod X` takes a mod folder that carries About/About.xml and REFUSES a folder a compose
    manifest folds in (Pyrelands is folded into RimMandrake.Biomes, which is not a folder at all: it is built by
    `--compose biomes`). A job that names either spelling must reach the right flag (RIVER_STEAM_BUILD_PYRELANDS_SWEEP_SITE:
    `--deploy RimMandrake.Biomes` died as INVALID/DEPLOY on a booked Steve slot)."""
    folded, composed = {}, set()
    mp = os.path.join(src_root, "RimMandrake", "Biomes.compose.json")
    if os.path.isfile(mp):
        try:
            with open(mp, encoding="utf-8") as fh:
                m = json.load(fh)
            wave = m.get("compose_wave", 0)
            composed.add(m["target"])
            for e in m["entries"]:
                if e.get("wave", 99) <= wave:
                    folded[e["source"]] = m["target"]
        except (OSError, ValueError, KeyError):
            pass
    known = set()
    for t in _SRC_TIERS:
        d = os.path.join(src_root, t)
        if os.path.isdir(d):
            for n in os.listdir(d):
                if os.path.isfile(os.path.join(d, n, "About", "About.xml")) and not (t == _SRC_TIERS[0] and n in folded):
                    known.add(n)
    return known, folded, composed


def deploy_problem(names, src_root):
    """-> a refusal sentence for the first name no deploy route can serve, else None. A source tree with no mod folders
    at all (a synthetic tree) is not judged."""
    known, folded, composed = deploy_catalog(src_root)
    if not known and not composed:
        return None
    for n in names:
        if n not in known and n not in folded and n not in composed:
            near = sorted(k for k in known | set(folded) | composed if n.lower() in k.lower() or k.lower() in n.lower())
            return "%r is not a deployable mod folder under src/ (%s)" % (
                n, ("did you mean " + ", ".join(near[:5])) if near else "run deploy_custom_mods.py with no args to list them")
    return None


def deploy_flags(names, src_root):
    """-> [(flag, value)] for deploy_custom_mods.py: a folded source or its composed target becomes ONE `--compose biomes`.

    deploy_custom_mods.py refuses `--compose` beside `--mod` (argparse error, exit 2): with a compose, every ordinary
    mod rides along as `--with MOD` instead (TESTQ_FIX_COMPOSE_ROUTE_MOD_WITH: J20261026T095451Z-7220f2 and
    J20261026T100912Z-098e84 died INVALID/DEPLOY on `--mod FlowWorks --compose biomes`)."""
    _, folded, composed = deploy_catalog(src_root)
    ordinary, compose = [], False
    for n in names:
        if n in folded or n in composed:
            compose = True
        elif n not in ordinary:
            ordinary.append(n)
    if compose:
        return [("--compose", "biomes")] + [("--with", n) for n in ordinary]
    return [("--mod", n) for n in ordinary]


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
    if job.get("gate"):
        a += ["--gate", job["gate"]]
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
            raise SchemaError("result %s: %s" % (res.get("attempt") if isinstance(res, dict) else None, msg))
    need(isinstance(res, dict) and res.get("schema") == RESULT_SCHEMA, "schema must be %s" % RESULT_SCHEMA)
    need(JOB_ID_RE.match(str(res.get("job"))), "bad job id")
    need(str(res.get("attempt", "")).startswith(res["job"] + ".a"), "attempt must be <job>.a<n>")
    need(res.get("outcome") in OUTCOMES, "outcome must be one of %s" % ", ".join(OUTCOMES))
    need(res.get("cause") in CAUSES, "unknown cause %r" % res.get("cause"))
    need(res["outcome"] == "DONE" or res.get("cause"), "a non-DONE outcome needs a cause")
    need(isinstance(res.get("rows"), list), "rows must be a list")
    for r in res["rows"]:
        need(isinstance(r, dict) and set(("chain", "row", "verdict")) <= set(r), "a row needs chain/row/verdict")
    return res


SCHEMA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testq_schema.json")


def json_schema():
    """The committed machine-readable job + result schema (testq_schema.json), derived from the constants above so
    the two cannot drift: selftest_testq_schema fails when the file differs. Regenerate: python3 schema.py --emit."""
    name = {"type": "string", "pattern": NAME_RE.pattern}
    names = {"type": "array", "items": name}
    nullable_ts = {"type": ["string", "null"], "pattern": r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$"}
    job = {
        "type": "object", "additionalProperties": False,
        "required": ["schema", "id", "mod", "selector", "purpose", "requested_by", "source_sha"],
        "properties": {
            "schema": {"const": JOB_SCHEMA}, "id": {"type": "string", "pattern": JOB_ID_RE.pattern},
            "item": {"type": ["string", "null"]}, "mod": name,
            "selector": {"type": "object", "additionalProperties": False, "minProperties": 1,
                         "properties": {"item": names, "chains": names, "rows": names, "full": {"type": "boolean"}}},
            "profile": {"enum": list(PROFILES)}, "purpose": {"enum": list(PURPOSES)},
            "priority": {"type": "integer"}, "not_before": nullable_ts, "requested_by": name,
            "source_sha": {"type": "string", "pattern": SHA_RE.pattern},
            "supersedes": {"type": ["string", "null"], "pattern": JOB_ID_RE.pattern},
            "gate": {"enum": [None] + list(GATES)}, "owner_gate": {"type": ["string", "null"]}, "lane": {"enum": list(LANES)},
            "deploy": names, "canary": {"type": "boolean"}, "validity": {"type": "boolean"},
            "timeout_s": {"type": "integer", "minimum": 60, "maximum": 21600},
            "row_items": {"type": "object", "additionalProperties": name},
            "submitted": {"type": "string", "description": "UTC time make_job stamped"},
        },
        "defaults": DEFAULTS,
    }
    row = {"type": "object", "required": ["chain", "row", "verdict"],
           "properties": {"chain": {"type": ["string", "null"]}, "row": {"type": "string"},
                          "verdict": {"type": "string", "description": "usually one of " + ", ".join(VERDICTS)},
                          "validity": {}, "freshness": {}, "detail": {"type": "string", "maxLength": DETAIL_CAP}}}
    names_free = {"type": "array", "items": {"type": "string"}}     # claim-marker ids the Steve worker writes
    result = {
        "type": "object", "required": ["schema", "job", "attempt", "outcome", "cause", "rows"],
        "properties": {
            "schema": {"const": RESULT_SCHEMA}, "job": {"type": "string", "pattern": JOB_ID_RE.pattern},
            "attempt": {"type": "string"}, "host": {"type": "string"}, "runner_sha": {"type": ["string", "null"]},
            "outcome": {"enum": list(OUTCOMES)}, "cause": {"enum": list(CAUSES)},
            "deployed": {"type": "object"}, "rows": {"type": "array", "items": row},
            "counts": {"type": "object", "additionalProperties": {"type": "integer"}},
            "phase_s": {"type": "object"}, "retries": {"type": "integer"},
            "modcheck_exit": {"type": ["integer", "null"]},
            "artifacts": {"type": "array", "items": {"type": "object", "required": ["name", "path", "sha256", "bytes"]}},
            "started": {"type": "string"}, "finished": {"type": ["string", "null"]}, "note": {"type": "string"},
            "moot_markers": names_free, "bounced_for_markers": names_free,
        },
        "description": "a non-DONE outcome needs a cause; attempt is <job>.a<n>",
    }
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "testq job and result records",
            "description": "generated by schema.py --emit from the constants in schema.py; do not edit by hand",
            "$defs": {"job": job, "result": result}}


def dump(obj, path):
    """Write JSON atomically (temp file + rename in the same directory)."""
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True, default=str)
        f.write("\n")
    os.replace(tmp, path)


if __name__ == "__main__":
    if sys.argv[1:] == ["--emit"]:
        dump(json_schema(), SCHEMA_FILE)
        print("wrote " + SCHEMA_FILE)
    else:
        print("usage: schema.py --emit   (rewrite testq_schema.json from the constants)")
