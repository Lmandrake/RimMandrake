"""arbiter_tiers.py - no-AI triage of done claims into the Arbiter's three tiers.

Design: design/RimMandrake/rimflow_v3_arbiter_tiers_2026-10-27.md (item ARBITER_REDESIGN_RISK_TIERED_VERDICTS).

  tier 0  deterministic gates over evidence already recorded (ledger verify/implemented/finding/note events,
          the code-review shards). Outcome BOUNCE (a hard failure: back to the builder with the failing
          evidence), PASS0 (every gate clear on a low-risk claim) or OPEN (neither).
  tier 1  audit_prescreen's rarity-weighted risk score ranks every claim not bounced. OPEN claims in the
          risky slice (a forced flag, or score at/above the slice cut) go to tier 2; the rest PASS1.
  tier 2  AI judgment by a judge that never built the work: the risky slice plus a seeded calibration
          sample of the PASS0/PASS1 claims (1 in CALIB_EVERY).

Cold run over the last N days of closes (writes JSON, prints the tier mix):

    python3 src/RimMandrake/rimflow/arbiter_tiers.py [--days 7] [--out PATH] [--now ISO]

Unreadable ledger => UNMEASURED, exit 2, nothing written.
"""
import argparse, glob, hashlib, json, os, random, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import audit_prescreen as ap                                  # noqa: E402

REPO = ap.REPO
# A claim's sha may live only in the other seat's clone until it is pushed and fetched: look in both.
REPOS = tuple(dict.fromkeys([REPO] + [p for p in (os.environ.get("ARBITER_TIERS_REPOS") or
                                                    "/home/mandrake/rm/bench:/home/mandrake/rm/foundry").split(":")
                                       if p and os.path.isdir(p)]))
OUT = "/mnt/d/ClaudeWork/rimmandrake/arbiter/tiers.json"
REVIEW_GLOB = os.path.join(REPO, "infrastructure", "state", "code_review", "*.jsonl")

# Files code review covers (code_review_status scans .py/.cs/.xml; shell and project files are code too).
REVIEW_EXTS = (".py", ".cs", ".xml", ".sh", ".csproj", ".ps1", ".js", ".ts")
# Any of these flags sends an OPEN claim to tier 2 whatever its score.
FORCE_T2 = ("gate_or_harness_path", "flowworks_or_live", "past_audit_failed", "reopened_before",
            "owner_words_after_close", "finding_against_item")
# Flags that stop a claim being low-risk (so it cannot PASS0, only rank in tier 1).
NOT_LOW_RISK = FORCE_T2 + ("many_files", "no_check_evidence", "verify_not_pass", "closed_by_maker_only",
                           "short_claim_to_close", "sha_touches_nothing")
SLICE_QUANTILE = 0.75     # OPEN claims scoring at/above this quantile of OPEN scores go to tier 2
CALIB_EVERY = 10          # 1 in 10 gate/rank passes also gets an AI verdict (calibration)

# A path is local only when nothing host-like ("stevedesktop:") sits right before it; remote paths are not checked.
_PATH_RX = re.compile(r"(?<![\w.-]:)(?<![\w.-])([A-Za-z]:\\[^;,\s]+|/(?:mnt|home)/[^;,\s]+)")


def to_posix(p):
    p = p.rstrip(":.)]'\"")
    m = re.match(r"^([A-Za-z]):\\(.*)$", p)
    if m:
        return "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/"))
    return p


def cited_paths(text):
    return [to_posix(m) for m in _PATH_RX.findall(text or "")]


def load_clean_hashes(pattern=REVIEW_GLOB):
    """{(path, sha256)} for every record ever marked clean."""
    out = set()
    for f in glob.glob(pattern):
        for line in open(f, errors="replace"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("verdict") == "clean" and d.get("sha256") and d.get("path"):
                out.add((d["path"], d["sha256"]))
    return out


def git_files_any(sha, repos=REPOS):
    """Files a commit touches, from the first clone that has the commit; None if none does."""
    for r in repos:
        f = ap.git_files(sha, repo=r)
        if f is not None:
            return f
    return None


def blob_sha256(sha, path, repos=REPOS):
    """sha256 of path's bytes at commit sha; None if absent (deleted by the commit) or unreadable."""
    for repo in repos:
        try:
            r = subprocess.run(["git", "-C", repo, "show", "%s:%s" % (sha, path)], capture_output=True, timeout=30)
        except Exception:
            continue
        if r.returncode == 0:
            return hashlib.sha256(r.stdout).hexdigest()
    return None


def _latest_by_criterion(verifies):
    last = {}
    for v in sorted(verifies, key=lambda e: e["ts"]):
        last[v.get("criterion") or "*"] = v
    return last


def gates(evs, close, files, clean, blob=blob_sha256, exists=os.path.exists):
    """Tier-0 gate results for one claim: {gate: PASS|FAIL|NONE|UNMEASURED} plus the evidence each read.
    FAIL is a recorded hard failure; NONE means the gate has nothing recorded to read."""
    g, ev = {}, {}
    sha = (close.get("sha") or "").strip()
    # G1 build identity: the claim names a commit that resolves
    if not sha or sha.upper() == "HEAD" or files is None:
        g["G1_sha"] = "FAIL"
    else:
        g["G1_sha"] = "PASS"
    # G2 recorded verification: latest verify per criterion; a fail not superseded by a later pass is hard
    verifies = [e for e in evs if e.get("event") == "verify" and e["ts"] <= close["ts"]]
    last = _latest_by_criterion(verifies)
    if not verifies:
        g["G2_verify"] = "NONE"
    elif any(v.get("result") == "fail" for v in last.values()):
        g["G2_verify"] = "FAIL"
        ev["G2_verify"] = [v.get("evidence") for v in last.values() if v.get("result") == "fail"]
    elif all(v.get("result") == "pass" for v in last.values()):
        g["G2_verify"] = "PASS"
    else:
        g["G2_verify"] = "PARTIAL"
    # G3 acceptance coverage: every criterion the builder declared has a passing verify
    impl = [e for e in evs if e.get("event") == "implemented" and e["ts"] <= close["ts"]]
    crit = [c.get("id") for c in (impl[-1].get("criteria") or [])] if impl else []
    crit = [c for c in crit if c]
    if not crit:
        g["G3_criteria"] = "NONE"
    else:
        missing = [c for c in crit if (last.get(c) or {}).get("result") != "pass"]
        g["G3_criteria"] = "PASS" if not missing else "OPEN"
        if missing:
            ev["G3_criteria"] = missing
    # G4 cited evidence exists on disk (every passing verify must cite at least one path that still exists)
    absent = []
    seen_any = False
    for v in verifies:
        ps = cited_paths(v.get("evidence"))
        if not ps:
            continue
        seen_any = True
        if not any(exists(p) for p in ps):
            absent.append(ps[0])
    g["G4_evidence"] = "NONE" if not seen_any else ("FAIL" if absent else "PASS")
    if absent:
        ev["G4_evidence"] = absent
    # G5 code review: every code file the commit touched was marked clean at exactly that content
    if files is None:
        g["G5_review"] = "UNMEASURED"
    else:
        code = [f for f in files if f.endswith(REVIEW_EXTS)]
        if not code:
            g["G5_review"] = "NONE"
        else:
            dirty = []
            for f in code:
                h = blob(sha, f)
                if h is not None and (f, h) not in clean:
                    dirty.append(f)
            g["G5_review"] = "PASS" if not dirty else "OPEN"
            if dirty:
                ev["G5_review"] = dirty[:10]
    return g, ev


def extra_flags(evs, close):
    f = []
    if any(e.get("event") == "finding" for e in evs):
        f.append("finding_against_item")
    if any(e.get("event") == "note" and e.get("ownerSaid") and e["ts"] > close["ts"] for e in evs):
        f.append("owner_words_after_close")
    return f


def tier0(g, flags):
    if g["G1_sha"] == "FAIL" or g["G2_verify"] == "FAIL" or g["G4_evidence"] == "FAIL":
        return "BOUNCE"
    clear = (g["G2_verify"] == "PASS" and g["G3_criteria"] in ("PASS", "NONE")
             and g["G5_review"] in ("PASS", "NONE"))
    if clear and not any(x in NOT_LOW_RISK for x in flags):
        return "PASS0"
    return "OPEN"


def _quantile(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def classify(events, rules, since_epoch, git=git_files_any, clean=frozenset(), blob=blob_sha256,
             exists=os.path.exists, past_failed=frozenset(), seed=0):
    cache = {}

    def git_c(sha):
        if sha not in cache:
            cache[sha] = git(sha)
        return cache[sha]

    rows = ap.score(events, rules, since_epoch, git=git_c, past_failed=past_failed, exists=exists)
    by = {}
    for e in events:
        if e.get("id"):
            by.setdefault(e["id"], []).append(e)
    for r in rows:
        evs = by[r["item"]]
        close = [e for e in evs if e.get("event") == "close"][-1]
        r["flags"] = r["flags"] + extra_flags(evs, close)
        sha = (close.get("sha") or "").strip()
        files = git_c(sha) if sha and sha.upper() != "HEAD" else None
        r["gates"], r["gate_evidence"] = gates(evs, close, files, clean, blob=blob, exists=exists)
        r["tier0"] = tier0(r["gates"], r["flags"])
    ap._rank(rows, rules)               # re-rank: the extra flags carry rarity weight too
    open_scores = [r["score"] for r in rows if r["tier0"] == "OPEN"]
    cut = _quantile(open_scores, SLICE_QUANTILE)
    for r in rows:
        if r["tier0"] == "BOUNCE":
            r["tier"] = "T0_BOUNCE"
        elif r["tier0"] == "PASS0":
            r["tier"] = "T0_PASS"
        elif any(x in FORCE_T2 for x in r["flags"]) or (cut is not None and r["score"] >= cut and r["score"] > 0):
            r["tier"] = "T2_RISK"
        else:
            r["tier"] = "T1_PASS"
    passes = sorted(r["item"] for r in rows if r["tier"] in ("T0_PASS", "T1_PASS"))
    k = len(passes) // CALIB_EVERY
    calib = set(random.Random(seed).sample(passes, k)) if k else set()
    for r in rows:
        r["calibration"] = r["item"] in calib
    return rows, cut


def mix(rows):
    n = len(rows) or 1
    out = {}
    for t in ("T0_BOUNCE", "T0_PASS", "T1_PASS", "T2_RISK"):
        k = sum(1 for r in rows if r["tier"] == t)
        out[t] = [k, round(k / n, 3)]
    k = sum(1 for r in rows if r["tier"] == "T2_RISK" or r["calibration"])
    out["AI_VERDICTS(T2+calibration)"] = [k, round(k / n, 3)]
    return out


def main(argv=None, events=None):
    a = argparse.ArgumentParser()
    a.add_argument("--days", type=float, default=7)
    a.add_argument("--out", default=OUT)
    a.add_argument("--now")
    a = a.parse_args(argv)
    rules = ap.load_rules()
    try:
        if events is None:
            from rimflow import model
            events = model.read()
        if not events:
            raise ValueError("ledger read returned no events")
    except Exception as ex:
        print("UNMEASURED: ledger unreadable (%s); nothing written" % ex, file=sys.stderr)
        return 2
    now = ap._epoch(a.now) if a.now else time.time()
    since = now - 86400 * a.days
    clean = load_clean_hashes()
    if not clean:
        print("UNMEASURED: no clean code-review records readable; G5 would be blind", file=sys.stderr)
        return 2
    rows, cut = classify(events, rules, since, clean=clean,
                         past_failed=ap.past_failed_items(rules["past_audits_file"]), seed=int(since // 86400))
    gate_counts = {}
    for r in rows:
        for gname, v in r["gates"].items():
            gate_counts.setdefault(gname, {}).setdefault(v, 0)
            gate_counts[gname][v] += 1
    doc = {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
           "since": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(since)),
           "closes_seen": len(rows), "slice_cut_score": cut, "mix": mix(rows), "gate_counts": gate_counts,
           "signal_counts_rates": ap.signal_rates(rows), "rows": rows}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    tmp = a.out + ".tmp"
    with open(tmp, "w") as f:
        json.dump(doc, f, indent=1)
    os.replace(tmp, a.out)
    print("closes seen: %d  (since %s)  slice cut score: %s" % (len(rows), doc["since"], cut))
    for t, (k, rt) in doc["mix"].items():
        print("  %-28s %4d  %5.1f%%" % (t, k, 100 * rt))
    for gname in sorted(gate_counts):
        print("  %-12s %s" % (gname, json.dumps(gate_counts[gname], sort_keys=True)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
