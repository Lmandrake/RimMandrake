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
  <checkout>_*.json beside the checkout script or in its northstar/ (walk header `checkout:`;
      GimmeSomeSlack proof_all_*.json, FlowWorks validation_v2_result_*.json): the newest LIVE result
      per mod, bound to the current mod hash and the repo DLL's .srchash (stale -> never proven)

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
          "precondition", "unverified-calls", "stale-result", "other")
# unknown-reasons: evidence MIGHT hold, but nothing recorded proves it does.
DEPLOY_UNRECORDED = "deploy-fresh-unrecorded"
DEPLOY_UNPROVEN = "deploy-fingerprint-unproven"   # a fingerprint exists but cannot prove freshness (not drift)
MODAL_UNCHECKED = "modal-check-failed"
RUN_UNKNOWN = "run-identity-unknown"
DETECTORS_UNRECORDED = "detector-coverage-unrecorded"
DLL_UNRECORDED = "dll-identity-unrecorded"       # the result names no running assembly hash
SRCHASH_MISMATCH = "srchash-mismatch"            # the repo DLL is not the one its .srchash stamp names


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


def fingerprint_verdict(mod, ri):
    """(proven, why, hard_stale). hard_stale: the fingerprint itself shows the deployed code was not the repo's
    (drift at start/end, or content changed mid-run) -- that is a stale-deploy taint, not a mere unknown."""
    import run_identity as RI
    st, en = ri.get("deploy_start"), ri.get("deploy_end")
    if not isinstance(st, dict) or st.get("mod") != mod:
        return False, "fingerprint names a different mod", False
    ok, why = RI.proves_fresh(st, en, ri.get("git"))
    if ok:
        return True, why, False
    drifted = any(isinstance(f, dict) and f.get("state") == "drift" for f in (st, en)) or \
        (isinstance(en, dict) and st.get("state") == en.get("state") == "in-sync" and
         (st.get("src_hash"), st.get("deployed_hash")) != (en.get("src_hash"), en.get("deployed_hash")))
    return False, why, bool(drifted)


def modal_by_chain(summary):
    """{chain index: (no, unknown)} from the runner's per-chain modal_check. A dialog found open when the
    NEXT chain began (or after the last one) was up during the chain before it -> modal-open. A failed
    sweep is unknown, never clean. Records with no modal_check at all add nothing (old records)."""
    chains = (summary or {}).get("chains", [])
    out = {i: (set(), set()) for i in range(len(chains))}
    probes = [(i - 1, c.get("modal_check")) for i, c in enumerate(chains) if i > 0]
    probes.append((len(chains) - 1, (summary or {}).get("modal_check_final")))
    for idx, mc in probes:
        if idx < 0 or not isinstance(mc, dict):
            continue
        if mc.get("found_open"):
            out[idx][0].add("modal-open")
        if mc.get("errors"):
            out[idx][1].add(MODAL_UNCHECKED)
    return out


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


def judge_mod(mod, mrow, summary, run, amendments, when, checkout=None):
    """Per required check of `mod`: the ran/result/evidence-holds triple. Returns
    (rows, extras) -- extras = components observed in the record but absent from the
    manifest (script changed since the run, or declared only on a live branch).
    `checkout` ({row id: judgement} from judge_checkout) judges every check the manifest marks
    `checkout_row`; a declared row missing from the result is not reached."""
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
    ri = (summary or {}).get("run_identity")
    if isinstance(ri, dict) and ri.get("deploy_start") is not None:
        ok, why, hard = fingerprint_verdict(mod, ri)
        if ok:
            attested = True
        elif hard:
            run_no.add("stale-deploy")       # recorded drift / content moved mid-run: the tested code was not the repo's
        else:
            run_unknown.add(DEPLOY_UNPROVEN)
    if not attested and not any(u in run_unknown for u in (DEPLOY_UNPROVEN,)) and "stale-deploy" not in run_no:
        run_unknown.add(DEPLOY_UNRECORDED)
    digest = None
    if run is not None:
        for d in run["row"].get("evidence", {}).get("digests", []):
            if d.get("mod") == mod:
                digest = d

    seen = {}
    modal = modal_by_chain(summary)
    for ci, ch in enumerate((summary or {}).get("chains", [])):
        cno, cunk = chain_taints(ch, digest)
        cno, cunk = cno | modal[ci][0], cunk | modal[ci][1]
        counts = {}
        for comp in ch.get("components", []):
            cid = "%s/%s" % (ch.get("name"), comp.get("name"))
            counts[cid] = counts.get(cid, 0) + 1
            if counts[cid] > 1:
                cid = "%s#%d" % (cid, counts[cid])
            seen[cid] = judge_component(comp, cno, cunk, run_no, run_unknown)
    if checkout is not None:
        for chk in mrow["checks"]:
            rid = chk.get("checkout_row")
            if rid:
                seen[chk["id"]] = checkout.get(rid) or _finish("not_reached", "NONE", "not in checkout result",
                                                               set(), set())
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
        if chk["source"] in ("script_check", "checkout_row"):
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
    if checkout is not None:
        fed = {c.get("checkout_row") for c in mrow["checks"] if c.get("checkout_row")}
        extras += sorted("checkout/" + r for r in set(checkout) - fed)
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


# Result files beside a mod whose walk names NO `checkout:` script: the report cannot join their rows to the
# manifest, so it NAMES them, never counts them -- a manifest mod with evidence it cannot read is listed, not left
# out of the table and the denominator silently. A mod with a `checkout:` header is read by checkout_results().
RESULT_GLOBS = ("northstar/*.json", "*_result_*.json", "proof_all_*.json")
RESULT_WORDS = re.compile(r"result|proof|matrix|validation", re.I)


def results_elsewhere(mrow):
    """[(path relative to ROOT, mtime, rows or None)] newest first: checkout result files beside the mod's script."""
    script = (mrow or {}).get("script") or ""
    if not script:
        return []
    d = os.path.dirname(os.path.join(ROOT, script))
    found = {}
    for g in RESULT_GLOBS:
        for f in glob.glob(os.path.join(d, g)):
            if RESULT_WORDS.search(os.path.basename(f)):
                found[f] = os.path.getmtime(f)
    out = []
    for f, mt in sorted(found.items(), key=lambda kv: -kv[1]):
        n = None
        try:
            r = json.load(open(f, encoding="utf-8"))
            n = len(r["rows"]) if isinstance(r, dict) and isinstance(r.get("rows"), list) else None
        except (OSError, ValueError, KeyError):
            pass
        out.append((os.path.relpath(f, ROOT), _dt.datetime.fromtimestamp(mt), n))
    return out


# ------------------------------------------------------------------ checkout results (NORTHSTAR_RESULTS_JOIN_1)
# A checkout (walk header `checkout:`, manifest row "checkout") writes ONE result JSON per run:
#   {mod, mode, started, mod_hash, env{assembly_sha256, ...}, rows[{id, status, block?, class|cls, detail}], aborted}
# The same section 2.4 rules apply, with the result itself as the run identity:
#   - only mode "live" counts (a partial/mock run is never a checkout record);
#   - mod_hash != the mod's CURRENT hash -> taint stale-result: the code tested is not the code in the repo;
#   - running DLL (env.assembly_sha256) != the repo DLL / its .srchash stamp -> taint stale-deploy (compared only
#     when mod_hash is current: mod_hash covers Assemblies/, so then the repo DLL is the one of the run);
#     no running hash recorded -> unknown; a repo DLL that disagrees with its own .srchash -> unknown;
#   - deploy freshness: a recorded fingerprint (result `run_identity`, the suite shape) or an attestation
#     amendment covering the run window, else unknown (deploy-fresh-unrecorded) -- the DLL match alone does
#     not prove the deployed Defs/Textures;
#   - detector coverage: a result `situational` record (the chain shape), else unknown;
#   - a preflight row not PASS (block "preflight", or a folded L<n>_ row) -> taint precondition on every row.

def _mod_dir(mrow):
    s = (mrow or {}).get("script")
    return os.path.dirname(os.path.join(ROOT, s)) if s else None


def checkout_results(mod, mrow):
    """[(path, result dict)] newest first (by `started`, then mtime): result JSONs of the mod's checkout."""
    co = (mrow or {}).get("checkout") or {}
    script = co.get("script")
    if not script:
        return []
    d = os.path.dirname(os.path.join(ROOT, script))
    stem = os.path.splitext(os.path.basename(script))[0]
    out = []
    for f in set(glob.glob(os.path.join(d, stem + "_*.json")) + glob.glob(os.path.join(d, "northstar", stem + "_*.json"))):
        try:
            r = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(r, dict) and r.get("mod") == mod and isinstance(r.get("rows"), list):
            out.append((f, r))
    out.sort(key=lambda fr: (fr[1].get("started") or "", os.path.getmtime(fr[0])), reverse=True)
    return out


def _sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def repo_dll_identity(mod_dir):
    """[(dll basename, sha256 of the repo DLL or None, the .srchash `# dll:` stamp or None)] for Assemblies/."""
    out = []
    for sh in sorted(glob.glob(os.path.join(mod_dir or "", "Assemblies", "*.dll.srchash"))):
        dll = sh[:-len(".srchash")]
        stamp = None
        for line in open(sh, encoding="utf-8"):
            if line.startswith("# dll:"):
                stamp = line.split(":", 1)[1].strip()
                break
        out.append((os.path.basename(dll), _sha256(dll) if os.path.isfile(dll) else None, stamp))
    return out


def current_mod_hash(mod_dir):
    import status as _st
    return _st.mod_hash(mod_dir) if mod_dir and os.path.isdir(mod_dir) else None


def judge_checkout(mod, res, amendments, mod_dir, cur_hash=None, dlls=None):
    """({row id: judgement}, identity) for one checkout result. `cur_hash`/`dlls` default to the repo's."""
    no, unknown, ident = set(), set(), {}
    cur = cur_hash if cur_hash is not None else current_mod_hash(mod_dir)
    dlls = dlls if dlls is not None else repo_dll_identity(mod_dir)
    t0 = _t(res.get("started")) if res.get("started") else None
    t1 = t0 + _dt.timedelta(seconds=float(res.get("wall_s") or 0)) if t0 else None
    ident.update(started=t0, mod_hash=res.get("mod_hash"), current_hash=cur, mode=res.get("mode"),
                 aborted=res.get("aborted"))
    if t0 is None or not res.get("mod_hash"):
        unknown.add(RUN_UNKNOWN)
        ident["state"] = "unidentified"
    elif not cur:
        unknown.add(RUN_UNKNOWN)
        ident["state"] = "current mod hash unreadable"
    elif res["mod_hash"] != cur:
        no.add("stale-result")
        ident["state"] = "STALE"
    else:
        ident["state"] = "current"
    running = (res.get("env") or {}).get("assembly_sha256")
    ident["dll"] = "unrecorded"
    if ident["state"] == "STALE":
        # mod_hash covers Assemblies/, so the repo DLL may have moved since the run: comparing the running DLL with
        # TODAY's repo DLL would call a then-fresh deploy stale. The result is already untrusted (stale-result).
        ident["dll"] = "not compared (result is stale)"
    elif not running:
        unknown.add(DLL_UNRECORDED)
    elif not any(running == repo for _n, repo, _s in dlls):
        no.add("stale-deploy")
        ident["dll"] = "running DLL is not the repo's"
    else:
        ident["dll"] = "running == repo DLL"
        if not any(running == repo == stamp for _n, repo, stamp in dlls):
            unknown.add(SRCHASH_MISMATCH)
            ident["dll"] += ", but its .srchash names another"
    attested = False
    ri = res.get("run_identity")
    if isinstance(ri, dict) and ri.get("deploy_start") is not None:
        ok, why, hard = fingerprint_verdict(mod, ri)
        if ok:
            attested = True
        elif hard:
            no.add("stale-deploy")
        else:
            unknown.add(DEPLOY_UNPROVEN)
    if t0 is not None:
        for a in amendments:
            if not _applies(a, mod, t0, t1):
                continue
            if a.get("kind") == "taint":
                no.add(a.get("reason") if a.get("reason") in TAINTS else "other")
            elif a.get("kind") == "attest" and a.get("what") == "deploy-fresh":
                attested = True
    if not attested and DEPLOY_UNPROVEN not in unknown and "stale-deploy" not in no:
        unknown.add(DEPLOY_UNRECORDED)
    cno, cunk = chain_taints({"situational": res.get("situational"), "components": []}, None)
    no |= cno
    unknown |= cunk
    for r in res["rows"]:
        pre = r.get("block") == "preflight" or ("block" not in r and re.match(r"L\d+_", r.get("id") or ""))
        if pre and r.get("status") != "PASS":
            no.add("precondition")
    out = {}
    for r in res["rows"]:
        rid, st = r.get("id"), str(r.get("status") or "")
        rno = set(no)
        if st.startswith("PASS"):
            ran, result, cause = "completed", "PASS", None
            if "UNVERIFIED" in st:
                rno.add("unverified-calls")
        elif st == "FAIL":
            ran, result, cause = "completed", "FAIL", None
        else:
            harness = (r.get("class") or r.get("cls")) == "HARNESS"
            ran, result = ("aborted" if harness else "completed"), "UNMEASURED"
            cause = "harness" if harness else ("precondition" if st == "UNMEASURED" else st.lower() or "?")
        if rid not in out:
            out[rid] = _finish(ran, result, cause, rno, unknown)
    ident["no"], ident["unknown"] = sorted(no), sorted(unknown)
    return out, ident


def build_report(manifest, records_dir, amend_path, since=None, only=None, checkout_ident=None):
    """`checkout_ident(mod, mrow) -> (cur_hash, dlls)` overrides the repo reads (selftests)."""
    runs = load_runs(os.path.join(records_dir, "live_queue_results.jsonl"))
    amendments = load_amendments(amend_path)
    out = []
    summaries = latest_summaries(records_dir, since)
    for mod, mrow in sorted((manifest.get("mods") or {}).items()):
        if only and mod != only:
            continue
        co = None
        if mrow.get("checkout"):
            cands = checkout_results(mod, mrow)
            live = [(f, r) for f, r in cands if r.get("mode") == "live" and
                    not (since and r.get("started") and _t(r["started"]) < since)]
            co = {"script": mrow["checkout"].get("script"), "error": mrow["checkout"].get("error"),
                  "files": len(cands), "skipped_not_live": sum(1 for _f, r in cands if r.get("mode") != "live"),
                  "path": None}
            if live:
                f, r = live[0]
                cur, dlls = checkout_ident(mod, mrow) if checkout_ident else (None, None)
                judged, ident = judge_checkout(mod, r, amendments, _mod_dir(mrow), cur, dlls)
                co.update(path=os.path.relpath(f, ROOT), judged=judged, ident=ident)
        if mod not in summaries and not (co and co.get("path")):
            req = sum(1 for c in mrow.get("checks") or [] if c.get("required", True))
            out.append({"mod": mod, "unread": True, "required": req, "checkout": co,
                        "elsewhere": [] if co else results_elsewhere(mrow)})
            continue
        summary, run, path, mt = None, None, None, None
        if mod in summaries:
            path, mt = summaries[mod]
            summary = json.load(open(path, encoding="utf-8"))
            run = match_run(mod, mt, runs)
        judged = None
        if co and co.get("path"):
            ct = co["ident"]["started"]
            if mt is None or ct >= mt:          # the newer record judges the checks the checkout feeds
                judged = co["judged"]
        when = mt if judged is None else co["ident"]["started"]
        rows, extras = judge_mod(mod, mrow, summary, run, amendments, when, judged)
        out.append({"mod": mod, "when": when, "run": run, "rows": rows, "extras": extras,
                    "head": headline(rows), "summary": summary or {}, "path": path, "checkout": co})
    for mod, (path, mt) in sorted(summaries.items()):
        if (only and mod != only) or mod in (manifest.get("mods") or {}):
            continue
        out.append({"mod": mod, "when": mt, "run": match_run(mod, mt, runs), "missing_manifest": True,
                    "summary": json.load(open(path, encoding="utf-8"))})
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
    unread = [e for e in report if e.get("unread")]
    for e in report:
        if e.get("unread"):
            continue
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
        co = e.get("checkout")
        if co and co.get("path"):
            i = co["ident"]
            lines.append("    checkout %s  %s  mod_hash %s%s; DLL %s%s" % (
                co["path"], i["state"], (i["mod_hash"] or "-")[:12],
                "" if i["state"] == "current" else " (current %s)" % (i["current_hash"] or "?")[:12], i["dll"],
                "; ABORTED: %s" % i["aborted"] if i.get("aborted") else ""))
        if detail:
            for r in e["rows"]:
                lines.append("    %-60s %-12s %-10s holds=%-7s %s" % (
                    r["id"][:60], r["ran"], r["result"], r["holds"],
                    ",".join(r["no"] + r["unknown"]) or (r["cause"] or "")))
    lines.append("TOTAL proven %d of %d required (owner bars %d of %d); %d more would be proven if the "
                 "run's deploy were recorded fresh" % (tot["proven"], tot["required"],
                                                       tot["owner_bars_proven"], tot["owner_bars"],
                                                       tot["pending_deploy"]))
    stale = [e for e in report if (e.get("checkout") or {}).get("path") and e["checkout"]["ident"]["state"] != "current"]
    if stale:
        lines.append("STALE / UNIDENTIFIED checkout results (read, listed above, NOT proven -- the code they tested is not "
                     "the code in the repo, or cannot be shown to be):")
        for e in stale:
            i = e["checkout"]["ident"]
            lines.append("  %-22s %s  %s  result mod_hash %s, current %s" % (
                e["mod"][:22], e["checkout"]["path"], i["state"], (i["mod_hash"] or "-")[:12],
                (i["current_hash"] or "?")[:12]))
    if unread:
        nores = [e for e in unread if e.get("checkout")]
        if nores:
            lines.append("CHECKOUT DECLARED, NO LIVE RESULT READ: %d mods" % len(nores))
            for e in nores:
                c = e["checkout"]
                lines.append("  %-22s req %4d  checkout %s: %d result file(s), %d not live%s" % (
                    e["mod"][:22], e["required"], c["script"], c["files"], c["skipped_not_live"],
                    "; manifest enumeration failed: %s" % c["error"] if c.get("error") else ""))
        seen = [e for e in unread if e["elsewhere"]]
        lines.append("NOT IN THE TOTAL: %d mods (%d required checks) have a manifest row and no record this report "
                     "reads; %d of them hold result files but no walk `checkout:` header names their script:"
                     % (len(unread), sum(e["required"] for e in unread), len(seen)))
        for e in seen:
            f, mt, n = e["elsewhere"][0]
            lines.append("  %-22s req %4d  newest %s (%s%s), %d result file(s)" % (
                e["mod"][:22], e["required"], f, mt.strftime("%m-%d %H:%M"),
                ", %d rows" % n if n is not None else "", len(e["elsewhere"])))
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
        print(json.dumps([{"mod": e["mod"], "when": e["when"].isoformat() if e.get("when") else None,
                           "head": e.get("head"), "extras": e.get("extras"), "unread": bool(e.get("unread")),
                           "required": e.get("required"),
                           "checkout": {k: (v if k != "ident" else dict(v, started=v["started"].isoformat()
                                                                         if v.get("started") else None))
                                        for k, v in (e.get("checkout") or {}).items() if k != "judged"} or None,
                           "elsewhere": [(f, mt.isoformat(), n) for f, mt, n in e.get("elsewhere") or []]}
                          for e in report], indent=1))
    else:
        print(render(report, runs, since, a.detail))
    return 0


if __name__ == "__main__":
    sys.exit(main())
