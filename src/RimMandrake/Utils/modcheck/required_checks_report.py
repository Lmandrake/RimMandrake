"""required_checks_report -- per mod: how many REQUIRED checks have a TRUSTWORTHY pass/fail.

Owner ruling 2026-10-03 (question card): a run report LEADS with "required checks proven"
-- per mod, the must-have checks with a trustworthy pass/fail. checks/sec, commands/min and
checks passed are diagnostics in the footer, never targets.

Rules (labels ran / result / evidence-holds, taint classes, what "trustworthy" means):
design/RimMandrake/bridge_validation_observatory.md section 2.4. This file implements them;
change the rules there first, then here, by commit with a reason -- never mid-run.

Inputs, all READ-ONLY:
  required_checks.json                                 the manifest (required_checks.py)
  Transient/modcheck/live_queue/*/<Mod>_summary.json    latest suite record per mod
  Transient/modcheck/live_queue_results.jsonl          job rows (run identity + window)
  Transient/modcheck/obs_amendments.jsonl              recorded taints / attestations

    python3 required_checks_report.py [--since 2026-10-03] [--mod X] [--detail] [--json]
"""
import argparse
import datetime as _dt
import glob
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
MANIFEST = os.path.join(_HERE, "required_checks.json")
RECORDS = os.path.join(ROOT, "Transient", "modcheck")
AMEND = os.path.join(RECORDS, "obs_amendments.jsonl")

TAINTS = ("modal-open", "stale-deploy", "log-blind", "focus-lost", "upstream-failure",
          "precondition", "unverified-calls", "other")
# unknown-reasons: evidence MIGHT hold, but nothing recorded proves it does.
DEPLOY_UNRECORDED = "deploy-fresh-unrecorded"
RUN_UNKNOWN = "run-identity-unknown"
DETECTORS_UNRECORDED = "detector-coverage-unrecorded"


def _t(s):
    return _dt.datetime.fromisoformat(s) if s else None


# ------------------------------------------------------------------ inputs

def load_runs(path):
    rows = []
    if not os.path.isfile(path):
        return rows
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        mods = [d.get("mod") for d in (r.get("evidence") or {}).get("digests", [])]
        rows.append({"job": r.get("job"), "started": _t(r.get("started")),
                     "finished": _t(r.get("finished")), "mods": mods,
                     "status": r.get("status"), "row": r})
    return rows


def load_amendments(path):
    out = []
    if not os.path.isfile(path):
        return out
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("//"):
            a = json.loads(line)
            a["_from"], a["_to"] = _t(a.get("from")), _t(a.get("to"))
            out.append(a)
    return out


def latest_summaries(records_dir, since=None):
    """{mod: (path, mtime)} -- the newest summary per mod across job dirs."""
    best = {}
    for p in glob.glob(os.path.join(records_dir, "live_queue", "*", "*_summary.json")):
        mod = os.path.basename(p)[:-len("_summary.json")]
        mt = _dt.datetime.fromtimestamp(os.path.getmtime(p))
        if since and mt < since:
            continue
        if mod not in best or mt > best[mod][1]:
            best[mod] = (p, mt)
    return best


def match_run(mod, when, runs, slack_s=120):
    """The job row whose window holds `when` and whose digests name `mod`, or None.
    A killed job writes no row, so its records stay identity-unknown -- by design."""
    for r in runs:
        if r["started"] and r["finished"] and mod in r["mods"] and \
                r["started"] <= when <= r["finished"] + _dt.timedelta(seconds=slack_s):
            return r
    return None


def _applies(a, mod, t0, t1):
    mods = a.get("mods", "*")
    if mods != "*" and mod not in mods:
        return False
    if a["_from"] is None or a["_to"] is None:
        return False
    if a.get("kind") == "attest":      # an attestation must COVER the whole run
        return a["_from"] <= t0 and t1 <= a["_to"]
    return t0 <= a["_to"] and a["_from"] <= t1   # a taint needs only to overlap


# ------------------------------------------------------------------ classification

def _unmeasured_cause(detail):
    d = detail or ""
    if d.startswith("upstream failed"):
        return "cascade", "upstream-failure"
    if d.startswith("a surprise ended this chain"):
        return "cascade", "upstream-failure(surprise)"
    if d.startswith("surprise:"):
        m = re.match(r"surprise:\s*([a-z_]+)", d)
        return "aborted", "surprise:" + (m.group(1) if m else "?")
    if d.startswith("harness:"):
        return "aborted", "harness"
    if "BudgetExceeded" in d:
        return "aborted", "budget"
    return "completed", "precondition"   # the script itself declared the check unmeasurable


def chain_taints(chain, digest):
    """(no_reasons, unknown_reasons) that hold for EVERY check in this chain."""
    no, unknown = set(), set()
    sit = chain.get("situational")
    if not isinstance(sit, dict):
        unknown.add(DETECTORS_UNRECORDED)
    else:
        if sit.get("bland") is False or sit.get("bland_problems"):
            no.add("precondition")
        if sit.get("companion") is False:
            no.add("log-blind")
        for s in sit.get("surprises") or []:
            if "modal" in json.dumps(s):
                no.add("modal-open")
    for c in chain.get("components", []):
        if "modal_open" in (c.get("detail") or ""):
            no.add("modal-open")
    if digest and chain.get("name") in (digest.get("unbland_chains") or []):
        no.add("precondition")
    return no, unknown


def judge_component(comp, chain_no, chain_unknown, run_no, run_unknown):
    v = comp.get("verdict") or ""
    no, unknown = set(chain_no) | set(run_no), set(chain_unknown) | set(run_unknown)
    if v.startswith("PASS"):
        ran, result, cause = "completed", "PASS", None
        if "UNVERIFIED" in v:
            no.add("unverified-calls")
    elif v == "FAIL":
        ran, result, cause = "completed", "FAIL", None
    else:
        ran, cause = _unmeasured_cause(comp.get("detail"))
        result = "UNMEASURED"
    return _finish(ran, result, cause, no, unknown)


def _finish(ran, result, cause, no, unknown):
    if ran == "completed" and result in ("PASS", "FAIL"):
        if no:
            holds = "no"
        elif unknown:
            holds = "unknown"
        else:
            holds = "yes"
    else:
        holds = "n/a"
    return {"ran": ran, "result": result, "cause": cause, "holds": holds,
            "no": sorted(no), "unknown": sorted(unknown),
            "trustworthy": holds == "yes",
            "pending_deploy": holds == "unknown" and set(unknown) == {DEPLOY_UNRECORDED}}


def judge_mod(mod, mrow, summary, run, amendments, when):
    """Per required check of `mod`: the ran/result/evidence-holds triple. Returns
    (rows, extras) -- extras = components observed in the record but absent from the
    manifest (script changed since the run, or declared only on a live branch)."""
    run_no, run_unknown = set(), set()
    if run is None:
        run_unknown.add(RUN_UNKNOWN)
        t0 = t1 = when
    else:
        t0, t1 = run["started"], run["finished"]
    attested = False
    for a in amendments:
        if not _applies(a, mod, t0, t1):
            continue
        if a.get("kind") == "taint":
            run_no.add(a.get("reason") if a.get("reason") in TAINTS else "other")
        elif a.get("kind") == "attest" and a.get("what") == "deploy-fresh" and run is not None:
            attested = True
    if not attested:
        run_unknown.add(DEPLOY_UNRECORDED)
    digest = None
    if run is not None:
        for d in run["row"].get("evidence", {}).get("digests", []):
            if d.get("mod") == mod:
                digest = d

    seen = {}
    for ch in (summary or {}).get("chains", []):
        cno, cunk = chain_taints(ch, digest)
        counts = {}
        for comp in ch.get("components", []):
            cid = "%s/%s" % (ch.get("name"), comp.get("name"))
            counts[cid] = counts.get(cid, 0) + 1
            if counts[cid] > 1:
                cid = "%s#%d" % (cid, counts[cid])
            seen[cid] = judge_component(comp, cno, cunk, run_no, run_unknown)
    visual = {}
    for v in (summary or {}).get("visual", []) or []:
        if v.get("polarity", "must") == "must":
            visual[v.get("id")] = v

    rows, manifest_ids = [], set()
    for chk in mrow["checks"]:
        if not chk.get("required"):
            continue
        manifest_ids.add(chk["id"])
        base = {"id": chk["id"], "source": chk["source"], "owner": chk["owner"]}
        if chk["source"] == "script_check":
            j = seen.get(chk["id"])
            if j is None:
                j = _finish("not_reached", "NONE", "not in record", set(), set())
            rows.append(dict(base, **j))
            continue
        # a must-show line: judged from the screenshot verdict, valid only if every
        # claiming component's evidence holds
        claimers = [seen[c] for c in chk.get("claimed_by", []) if c in seen]
        if not chk.get("claimed_by"):
            rows.append(dict(base, **_finish("not_reached", "NONE", "no component claims it", set(), set())))
            continue
        if not claimers or not any(c["ran"] == "completed" for c in claimers):
            rows.append(dict(base, **_finish("not_reached", "NONE", "claiming component not run", set(), set())))
            continue
        no = set().union(*[c["no"] for c in claimers])
        unk = set().union(*[c["unknown"] for c in claimers])
        if any(c["result"] == "UNMEASURED" for c in claimers):
            no.add("upstream-failure")
        vid = chk["id"][3:]
        v = visual.get(vid)
        if v is None:
            rows.append(dict(base, **_finish("completed", "UNMEASURED", "no screenshot judgement recorded", no, unk)))
            continue
        verdict = (v.get("verdict") or "").upper()
        result = {"YES": "PASS", "NO": "FAIL"}.get(verdict, "UNMEASURED")
        rows.append(dict(base, **_finish("completed", result,
                                         None if result != "UNMEASURED" else "unjudgeable", no, unk)))
    extras = sorted(set(seen) - manifest_ids)
    return rows, extras


def headline(rows):
    h = {"required": len(rows), "proven": 0, "proven_pass": 0, "proven_fail": 0,
         "pending_deploy": 0, "tainted": {}, "unknown": {}, "unmeasured": {}, "not_reached": 0,
         "owner_bars": 0, "owner_bars_proven": 0}
    for r in rows:
        if r["owner"]:
            h["owner_bars"] += 1
            h["owner_bars_proven"] += r["trustworthy"]
        if r["trustworthy"]:
            h["proven"] += 1
            h["proven_pass" if r["result"] == "PASS" else "proven_fail"] += 1
        elif r["ran"] == "not_reached":
            h["not_reached"] += 1
        elif r["result"] == "UNMEASURED":
            k = r["cause"] or "?"
            h["unmeasured"][k] = h["unmeasured"].get(k, 0) + 1
        elif r["holds"] == "no":
            for k in r["no"]:
                h["tainted"][k] = h["tainted"].get(k, 0) + 1
        else:
            if r["pending_deploy"]:
                h["pending_deploy"] += 1
            for k in r["unknown"]:
                h["unknown"][k] = h["unknown"].get(k, 0) + 1
    return h


# ------------------------------------------------------------------ report

def _fmt_counts(d):
    return ", ".join("%s %d" % (k, n) for k, n in sorted(d.items(), key=lambda kv: -kv[1])) or "-"


def build_report(manifest, records_dir, amend_path, since=None, only=None):
    runs = load_runs(os.path.join(records_dir, "live_queue_results.jsonl"))
    amendments = load_amendments(amend_path)
    out = []
    for mod, (path, mt) in sorted(latest_summaries(records_dir, since).items()):
        if only and mod != only:
            continue
        mrow = manifest["mods"].get(mod)
        summary = json.load(open(path, encoding="utf-8"))
        run = match_run(mod, mt, runs)
        if mrow is None:
            out.append({"mod": mod, "when": mt, "run": run, "missing_manifest": True,
                        "summary": summary})
            continue
        rows, extras = judge_mod(mod, mrow, summary, run, amendments, mt)
        out.append({"mod": mod, "when": mt, "run": run, "rows": rows, "extras": extras,
                    "head": headline(rows), "summary": summary, "path": path})
    return out, runs


def diagnostics(report, runs, since):
    """Footer only. Every number is a diagnostic within a fixed workload, never a target."""
    lines = []
    jobs = {}
    for e in report:
        if e.get("run"):
            jobs.setdefault(id(e["run"]), (e["run"], []))[1].append(e)
    for run, entries in sorted(jobs.values(), key=lambda x: x[0]["started"]):
        wall = (run["finished"] - run["started"]).total_seconds() or 1
        emitted = sum(sum((d.get("verdicts") or {}).values())
                      for d in run["row"]["evidence"].get("digests", []))
        passed = sum((d.get("verdicts") or {}).get("PASS", 0)
                     for d in run["row"]["evidence"].get("digests", []))
        calls = sum(len(c.get("evidence") or []) for e in entries
                    for ch in e["summary"].get("chains", []) for c in ch.get("components", []))
        lines.append("  job %s %s-%s  wall %ds  verdicts emitted %d (%.3f/s)  PASS %d  "
                     "evidenced calls %d (%.1f/min, lower bound: Suite._record only; %d of %d mods' summaries joined)"
                     % (run["job"], run["started"].strftime("%H:%M"), run["finished"].strftime("%H:%M"),
                        wall, emitted, emitted / wall, passed, calls, calls / (wall / 60.0),
                        len(entries), len(run["mods"])))
    lines.append("  per-mod time, bridge commands/min, latency: UNMEASURED (no per-call record; observatory S1)")
    return lines


def render(report, runs, since, detail=False):
    lines = ["REQUIRED CHECKS PROVEN  (rules: bridge_validation_observatory.md 2.4; "
             "proven = ran to completion, PASS/FAIL, evidence holds)"]
    lines.append("%-22s %-11s %5s %-16s %-8s %-9s  %s" % (
        "mod", "run", "req", "proven (P/F)", "bars", "deploy?", "why the rest is not proven"))
    tot = {"required": 0, "proven": 0, "pending_deploy": 0, "owner_bars": 0, "owner_bars_proven": 0}
    for e in report:
        when = e["when"].strftime("%m-%d %H:%M")
        if e.get("missing_manifest"):
            lines.append("%-22s %-11s  -- no manifest row (no validation.py/walk of that name)" % (e["mod"], when))
            continue
        h = e["head"]
        for k in tot:
            tot[k] += h[k]
        why = []
        if h["tainted"]:
            why.append("tainted: " + _fmt_counts(h["tainted"]))
        if h["unknown"]:
            why.append("unknown: " + _fmt_counts(h["unknown"]))
        if h["unmeasured"]:
            why.append("UNMEASURED: " + _fmt_counts(h["unmeasured"]))
        if h["not_reached"]:
            why.append("not reached %d" % h["not_reached"])
        if e["extras"]:
            why.append("observed-not-in-manifest %d" % len(e["extras"]))
        lines.append("%-22s %-11s %5d %4d (%d/%d)%s %-8s %-9s  %s" % (
            e["mod"][:22], when, h["required"], h["proven"], h["proven_pass"], h["proven_fail"],
            " " * max(0, 8 - len("%d/%d" % (h["proven_pass"], h["proven_fail"]))),
            "%d/%d" % (h["owner_bars_proven"], h["owner_bars"]) if h["owner_bars"] else "-",
            "pend %d" % h["pending_deploy"] if h["pending_deploy"] else "-",
            "; ".join(why)))
        if detail:
            for r in e["rows"]:
                lines.append("    %-60s %-12s %-10s holds=%-7s %s" % (
                    r["id"][:60], r["ran"], r["result"], r["holds"],
                    ",".join(r["no"] + r["unknown"]) or (r["cause"] or "")))
    lines.append("TOTAL proven %d of %d required (owner bars %d of %d); %d more would be proven if the "
                 "run's deploy were recorded fresh" % (tot["proven"], tot["required"],
                                                       tot["owner_bars_proven"], tot["owner_bars"],
                                                       tot["pending_deploy"]))
    lines.append("diagnostics (never targets):")
    lines.extend(diagnostics(report, runs, since))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--since", help="only records newer than this date/time (ISO)")
    ap.add_argument("--mod")
    ap.add_argument("--detail", action="store_true", help="one line per required check")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--manifest", default=MANIFEST)
    ap.add_argument("--records", default=RECORDS)
    ap.add_argument("--amend", default=AMEND)
    a = ap.parse_args(argv)
    since = _t(a.since) if a.since else None
    manifest = json.load(open(a.manifest, encoding="utf-8"))
    report, runs = build_report(manifest, a.records, a.amend, since, a.mod)
    if a.json:
        print(json.dumps([{"mod": e["mod"], "when": e["when"].isoformat(),
                           "head": e.get("head"), "extras": e.get("extras")} for e in report], indent=1))
    else:
        print(render(report, runs, since, a.detail))
    return 0


if __name__ == "__main__":
    sys.exit(main())
