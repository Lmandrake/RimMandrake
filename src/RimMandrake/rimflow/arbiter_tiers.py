"""arbiter_tiers.py - no-AI triage of done claims into the Arbiter's tiers.

Design: design/RimMandrake/rimflow_v3_arbiter_tiers_2026-10-27.md (item ARBITER_REDESIGN_RISK_TIERED_VERDICTS).

  tier 0  deterministic gates over evidence already recorded (ledger verify/implemented/finding/note events, the
          code-review shards, close_evidence records). Outcome BOUNCE (a recorded hard failure), PASS0 (every gate
          clear, an independent pass recorded, no risk flag) or OPEN.
  tier 1  OPEN claims that carry machine evidence are ranked by audit_prescreen's rarity-weighted risk score; those
          in the risky slice (a forced flag, or score at/above the slice cut) go to tier 2; the rest PASS1.
  tier 2  AI judgment by a judge that never built the work: the risky slice; every claim with NO machine evidence
          (T2_NOEVIDENCE: never passed by code, whatever its score); every claim a gate could not measure
          (T2_UNMEASURED); plus a calibration sample of PASS0/PASS1 claims (keyed per-claim draw, 1 in CALIB_EVERY).
          A tier-2 claim with no AI verdict is HOLD (`--ai-refused` writes it so), never a pass.

Advisory while the schedule says `verdicts: "advisory"`: a bounce is a record in bounces.json, nothing is sent back
to the builder and nothing blocks.

Outputs (the Arbiter reads only the two judge-facing files; the tier labels stay out of its reach):
  judge-facing  D:\\ClaudeWork\\rimmandrake\\arbiter\\judge_list.json   item + sha only, keyed-hash order (T2 and
                calibration interleaved, no tier, no calibration flag)
                D:\\ClaudeWork\\rimmandrake\\arbiter\\bounces.json      item, sha, failing gates and their evidence
  measurement   D:\\ClaudeWork\\rimmandrake\\arbiter_tiers\\tiers.json, tiers_<ts>.json, tiers_history.jsonl
                (Auditor and Operations); `join` writes verdicts_tiered.jsonl (the Arbiter's verdicts + tier).

    python3 src/RimMandrake/rimflow/arbiter_tiers.py [--days 7] [--now ISO] [--ai-refused] [--past-audits PATH]
    python3 src/RimMandrake/rimflow/arbiter_tiers.py join [--verdicts PATH]

Any unreadable input (ledger, code-review shards, past audits, close evidence, calibration salt) => UNMEASURED,
exit 2, nothing written.
"""
import argparse, calendar, glob, hashlib, hmac, json, os, re, secrets, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
from rimflow import audit_prescreen as ap                                  # noqa: E402
import close_evidence as ce                                                # noqa: E402

REPO = ap.REPO
# A claim's sha may live only in the other seat's clone until it is pushed and fetched: look in both.
REPOS = tuple(dict.fromkeys([REPO] + [p for p in (os.environ.get("ARBITER_TIERS_REPOS") or
                                                    "/home/mandrake/rm/bench:/home/mandrake/rm/foundry").split(":")
                                       if p and os.path.isdir(p)]))
DATA = "/mnt/d/ClaudeWork/rimmandrake/arbiter_tiers"        # measurement records: not read by the Arbiter
JUDGE_DIR = "/mnt/d/ClaudeWork/rimmandrake/arbiter"         # what the Arbiter reads
REVIEW_GLOB = os.path.join(REPO, "infrastructure", "state", "code_review", "*.jsonl")
SALT_ENV = "ARBITER_CALIB_SALT"
GIT_ERROR = "GIT_ERROR"   # git could not answer (timeout, crash): not the same as "the sha does not resolve"

# Files code review covers (code_review_status scans .py/.cs/.xml; shell and project files are code too).
REVIEW_EXTS = (".py", ".cs", ".xml", ".sh", ".csproj", ".ps1", ".js", ".ts")
# Any of these flags sends an OPEN claim to tier 2 whatever its score.
FORCE_T2 = ("gate_or_harness_path", "flowworks_or_live", "past_audit_failed", "reopened_before",
            "owner_words_after_close", "finding_against_item")
# Flags that stop a claim being low-risk (so it cannot PASS0, only rank in tier 1).
NOT_LOW_RISK = FORCE_T2 + ("many_files", "no_check_evidence", "verify_not_pass", "closed_by_maker_only",
                           "short_claim_to_close", "sha_touches_nothing", "review_by_closing_seat_only")
SLICE_QUANTILE = 0.75     # evidenced OPEN claims scoring at/above this quantile go to tier 2
CALIB_EVERY = 10          # each gate/rank pass has a 1 in 10 keyed chance of also getting an AI verdict
TIERS = ("T0_BOUNCE", "T0_PASS", "T1_PASS", "T2_RISK", "T2_NOEVIDENCE", "T2_UNMEASURED")

# A path is local only when nothing host-like ("stevedesktop:") sits right before it; remote paths are not checked.
_PATH_RX = re.compile(r"(?<![\w.-]:)(?<![\w.-])([A-Za-z]:\\[^;,\s]+|/(?:mnt|home)/[^;,\s]+)")
_UNRESOLVED_RX = re.compile(r"bad object|unknown revision|ambiguous argument|bad revision|invalid object name|"
                            r"not a valid object|not a tree", re.I)


def to_posix(p):
    p = p.rstrip(":.)]'\"")
    m = re.match(r"^([A-Za-z]):\\(.*)$", p)
    if m:
        return "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/"))
    return p


def cited_paths(text):
    return [to_posix(m) for m in _PATH_RX.findall(text or "")]


def load_clean_hashes(pattern=REVIEW_GLOB):
    """{(path, sha256): {seats that marked it clean}}, replaying every record in state order (ts, seat, shard,
    line) as code_review_status does: a later `dirty` at the same content removes the clean mark, a later clean
    restores it. An unparsable line raises ValueError (it could be the dirty record that matters)."""
    recs = []
    for f in sorted(glob.glob(pattern)):
        with open(f, encoding="utf-8") as fh:
            for i, line in enumerate(fh):
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    raise ValueError("%s line %d is not JSON" % (f, i + 1))
                recs.append(((d.get("ts") or "", d.get("seat") or "", os.path.basename(f), i), d))
    recs.sort(key=lambda t: t[0])
    out = {}
    for _, d in recs:
        key = (d.get("path"), d.get("sha256"))
        if not key[0] or not key[1]:
            continue
        if d.get("verdict") == "clean":
            out.setdefault(key, set()).add(d.get("seat") or "?")
        elif d.get("verdict") == "dirty":
            out.pop(key, None)
    return out


def _git_status_one(sha, repo):
    try:
        r = subprocess.run(["git", "-C", repo, "diff-tree", "--no-commit-id", "--name-status", "--no-renames", "-r",
                            "--root", sha], capture_output=True, text=True, timeout=30)
    except Exception:
        return GIT_ERROR
    if r.returncode == 0:
        out = {}
        for l in r.stdout.splitlines():
            if "\t" in l:
                st, p = l.split("\t", 1)
                out[p] = st[:1]
        return out
    return None if _UNRESOLVED_RX.search(r.stderr or "") else GIT_ERROR


def git_files_any(sha, repos=REPOS):
    """{path: status letter} a commit touches, from the first clone that has it; None when no clone has the sha;
    GIT_ERROR when no clone has it and at least one could not answer."""
    err = False
    for r in repos:
        f = _git_status_one(sha, r)
        if isinstance(f, dict):
            return f
        err = err or f == GIT_ERROR
    return GIT_ERROR if err else None


def blob_sha256(sha, path, repos=REPOS):
    """sha256 of path's bytes at commit sha; None when no clone could read it (the caller has already excluded
    files the commit deleted, so None here is a read failure)."""
    for repo in repos:
        try:
            r = subprocess.run(["git", "-C", repo, "show", "%s:%s" % (sha, path)], capture_output=True, timeout=30)
        except Exception:
            continue
        if r.returncode == 0:
            return hashlib.sha256(r.stdout).hexdigest()
    return None


def _norm_files(files):
    if isinstance(files, (list, tuple)):
        return {p: "M" for p in files}
    return files


def _latest_by_criterion(verifies):
    last = {}
    for v in sorted(verifies, key=lambda e: e["ts"]):
        last[v.get("criterion") or "*"] = v
    return last


def builder_seats(evs, close):
    """Seats the ledger names as having BUILT the claim: claim/start/reclaim/implemented events before the close.
    OWNER is never the builder of agent work (it relays and closes). Empty = the builder is unknown (review AA7: true
    of 1202 of 2983 closes), and then nothing can be shown independent of it."""
    return {e.get("seat") for e in evs if e.get("event") in ("claim", "start", "reclaim", "implemented")
            and e["ts"] <= close["ts"] and e.get("seat") and e.get("seat") != "OWNER"}


def maker_seats(evs, close):
    """Seats that built or closed the claim: the close seat plus builder_seats()."""
    return {x for x in {close.get("seat")} | builder_seats(evs, close) if x}


#: Where a record's seat may come from for it to count as independent: what whoami() reads. A seat given by a caller,
#: shipped through the `record` CLI or missing is the writer's word only.
SEAT_SOURCES = ("RIMFLOW_SEAT", "AGENT_SEAT", "session role file")


def commit_session(sha, repos=REPOS):
    """The commit's `Claude-Session:` trailer (the bridge session that made it), or None when no clone says."""
    for repo in repos:
        try:
            r = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%(trailers:key=Claude-Session,valueonly)",
                                sha], capture_output=True, text=True, timeout=30)
        except Exception:
            continue
        if r.returncode == 0:
            m = re.search(r"session_[A-Za-z0-9]+", r.stdout or "")
            return m.group(0) if m else None
    return None


def lookup_close_evidence(sha, item, paths, folder=None, days=45):
    """close_evidence.lookup for the claim: runs at the sha covering its paths. Runs tagged with the item but
    covering none of them are added only when they FAIL or are UNMEASURED: a tag never supplies a PASS (review AA2)."""
    hits = ce.lookup(sha=sha, paths=list(paths), folder=folder, days=days) if paths else []
    seen = {json.dumps(h, sort_keys=True, default=str) for h in hits}
    for h in ce.lookup(sha=sha, item=item, folder=folder, days=days):
        if h.get("result") == "PASS":
            continue
        if json.dumps(h, sort_keys=True, default=str) not in seen:
            hits.append(h)
    return hits


def gates(evs, close, files, clean, blob=blob_sha256, exists=os.path.exists, evidence=(), session_of=lambda sha: None):
    """Tier-0 gate results for one claim: {gate: PASS|FAIL|OPEN|PARTIAL|NONE|UNMEASURED} plus the evidence each read.
    FAIL is a recorded hard failure; NONE means nothing recorded to read; UNMEASURED means an input could not be read.
    `files`: {path: status} | list | None (sha does not resolve) | GIT_ERROR. `clean`: {(path, sha256): {seats}}.
    `evidence`: close_evidence records already matched to this claim (lookup_close_evidence). `session_of(sha)`: the
    commit's Claude-Session (commit_session), so a run by the session that made the commit is never independent.
    Independence is UNMEASURED, never PASS, when the ledger names no builder (builder_seats empty)."""
    g, ev = {}, {}
    files = _norm_files(files)
    sha = (close.get("sha") or "").strip()
    makers = maker_seats(evs, close)
    builder_known = bool(builder_seats(evs, close))
    # G1 build identity: the claim names a commit that resolves
    if not sha or sha.upper() == "HEAD" or files is None:
        g["G1_sha"] = "FAIL"
    elif files == GIT_ERROR:
        g["G1_sha"] = "UNMEASURED"
    else:
        g["G1_sha"] = "PASS"
    # G2 recorded verification: latest verify per criterion; a fail not superseded by a later pass is hard.
    # G2_independent: a latest passing verify came from a seat that did not build or close the claim.
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
    pass_seats = sorted({v.get("seat") or "?" for v in last.values() if v.get("result") == "pass"})
    g["G2_independent"] = ("NONE" if not pass_seats else "UNMEASURED" if not builder_known else
                           "PASS" if any(s not in makers and s != "?" for s in pass_seats) else "FAIL")
    if pass_seats:
        ev["G2_verify_seats"] = pass_seats
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
    # G4 cited evidence exists on disk, read on the LATEST verify per criterion only: every path a verify cites gone
    # => FAIL; some gone => UNMEASURED (part of the evidence cannot be read); all present => PASS.
    gone_all, gone_some, seen_any = [], [], False
    for v in last.values():
        ps = cited_paths(v.get("evidence"))
        if not ps:
            continue
        seen_any = True
        missing = [p for p in ps if not exists(p)]
        if missing and len(missing) == len(ps):
            gone_all += missing
        elif missing:
            gone_some += missing
    g["G4_evidence"] = ("NONE" if not seen_any else "FAIL" if gone_all else "UNMEASURED" if gone_some else "PASS")
    if gone_all or gone_some:
        ev["G4_evidence"] = gone_all + gone_some
    # G5 code review: every code file the commit touched (and did not delete) is clean at exactly that content
    if not isinstance(files, dict):
        g["G5_review"] = "UNMEASURED"
    else:
        code = [f for f, st in sorted(files.items()) if st != "D" and f.endswith(REVIEW_EXTS)]
        if not code:
            g["G5_review"] = "NONE"
        else:
            dirty, unread, seats = [], [], set()
            for f in code:
                h = blob(sha, f)
                if h is None:
                    unread.append(f)
                elif (f, h) not in clean:
                    dirty.append(f)
                else:
                    seats |= set(clean[(f, h)])
            g["G5_review"] = "UNMEASURED" if unread else ("OPEN" if dirty else "PASS")
            if unread:
                ev["G5_unreadable"] = unread[:10]
            if dirty:
                ev["G5_review"] = dirty[:10]
            if g["G5_review"] == "PASS":
                ev["G5_review_seats"] = sorted(seats)
                if not (seats - makers - {"?"}):
                    ev["G5_review_by_closing_seat_only"] = True
    # G6 close evidence (selftests, builds, validators at this sha). FAIL/UNMEASURED: the latest run per (tool, paths)
    # anywhere in the claim's evidence. PASS only when every touched, non-deleted path is covered by a passing run of
    # the full tool (no variant: a static validate_patch never stands in for --defs); otherwise OPEN (review AA2/AA3).
    g["G6_independent"] = "NONE"
    if not isinstance(files, dict):
        g["G6_close_evidence"] = "UNMEASURED"
    elif not evidence:
        g["G6_close_evidence"] = "NONE"
    else:
        need = sorted(f for f, st in files.items() if st != "D")
        summ = ce.summarize(list(evidence))
        res = set(summ.values())
        full = [r for r in evidence if r.get("result") == "PASS" and not r.get("variant")]
        uncov = ce.uncovered(full, need) if need else ["(the commit only deletes: nothing to cover)"]
        g["G6_close_evidence"] = ("FAIL" if "FAIL" in res else "UNMEASURED" if "UNMEASURED" in res else
                                  "OPEN" if uncov else "PASS")
        ev["G6_close_evidence"] = summ
        if uncov and g["G6_close_evidence"] == "OPEN":
            ev["G6_uncovered"] = uncov[:10]
        eseats = sorted({r.get("seat") or "?" for r in evidence})
        ev["G6_seats"] = eseats       # "?" = the record names no seat ($RIMFLOW_SEAT unset when it ran)
        csess = session_of(sha) if sha else None

        def who_of(r):
            return r.get("who") if isinstance(r.get("who"), dict) else {}

        def seat_sure(r):        # the seat whoami() read in the writing process, not one a caller supplied
            o = r.get("origin") if isinstance(r.get("origin"), dict) else {}
            return bool(r.get("seat")) and who_of(r).get("seat_from") in SEAT_SOURCES and o.get("who") == "whoami"
        ind = [r for r in full if seat_sure(r) and r["seat"] not in makers
               and not (csess and who_of(r).get("bridge_session") == csess)]
        unsure = [r for r in full if not seat_sure(r)]
        if not full:
            pass                                       # no passing full run: nothing to be independent
        elif not builder_known:
            g["G6_independent"] = "UNMEASURED"
            ev["G6_independent"] = "the ledger names no builder (no claim/start/implemented before the close)"
        elif need and full and not ce.uncovered(ind, need):
            g["G6_independent"] = "PASS"
        elif unsure:
            g["G6_independent"] = "UNMEASURED"
            ev["G6_independent"] = "a run names no seat, or a seat its writer only asserted"
        else:
            g["G6_independent"] = "FAIL"
    return g, ev


def has_machine_evidence(g):
    """Recorded, machine-readable evidence: a verify event from a seat independent of the builder or citing evidence
    that exists (a builder's bare self-verify is not -- review AA6), a clean code review at the claimed content, or a
    close_evidence run at the sha. Prose in a close reason is a claim, not evidence."""
    g2 = g["G2_verify"] != "NONE" and (g["G2_independent"] == "PASS" or g["G4_evidence"] == "PASS")
    return g2 or g["G5_review"] == "PASS" or g.get("G6_close_evidence", "NONE") != "NONE"


def extra_flags(evs, close, ev=None):
    f = []
    if any(e.get("event") == "finding" for e in evs):
        f.append("finding_against_item")
    if any(e.get("event") == "note" and e.get("ownerSaid") and e["ts"] > close["ts"] for e in evs):
        f.append("owner_words_after_close")
    if ev and ev.get("G5_review_by_closing_seat_only"):
        f.append("review_by_closing_seat_only")
    return f


def tier0(g, flags):
    if (g["G1_sha"] == "FAIL" or g["G2_verify"] == "FAIL" or g["G4_evidence"] == "FAIL"
            or g.get("G6_close_evidence") == "FAIL"):
        return "BOUNCE"
    g6 = g.get("G6_close_evidence", "NONE")
    independent = ((g["G2_verify"] == "PASS" and g["G2_independent"] == "PASS") or
                   (g6 == "PASS" and g.get("G6_independent") == "PASS" and g["G2_verify"] in ("PASS", "NONE")))
    clear = (independent and g["G1_sha"] == "PASS" and g["G3_criteria"] in ("PASS", "NONE")
             and g["G4_evidence"] in ("PASS", "NONE") and g["G5_review"] in ("PASS", "NONE")
             and g6 in ("PASS", "NONE"))
    if clear and not any(x in NOT_LOW_RISK for x in flags):
        return "PASS0"
    return "OPEN"


def rank_evidenced(ranked, rules):
    """Rarity rank of the evidenced OPEN claims, with no rarity zeroing (review Y F1): a gap shared by most of them
    (a review only the closing seat recorded, say) still weighs -log2(rate) > 0; only a flag on every claim weighs 0."""
    return ap._rank(ranked, dict(rules, max_signal_rate=1.0))


def _quantile(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def _keyed(salt, *parts):
    return hmac.new(salt.encode(), "\0".join(parts).encode(), hashlib.sha256).hexdigest()


def calib_pick(item, sha, salt):
    """Per-claim draw, stable across runs and windows, unpredictable without the salt: P = 1/CALIB_EVERY."""
    return int(_keyed(salt, "calib", item, sha)[:12], 16) / float(16 ** 12) < 1.0 / CALIB_EVERY


def classify(events, rules, since_epoch, git=git_files_any, clean=None, blob=blob_sha256,
             exists=os.path.exists, past_failed=frozenset(), salt="selftest-salt", evidence_lookup=lambda sha, item, paths: [],
             ai_refused=False, session_of=lambda sha: None):
    cache = {}
    clean = {} if clean is None else (clean if isinstance(clean, dict) else {k: set() for k in clean})

    def git_c(sha):
        if sha not in cache:
            cache[sha] = _norm_files(git(sha))
        return cache[sha]

    def git_names(sha):                 # audit_prescreen wants a list or None
        f = git_c(sha)
        return sorted(f) if isinstance(f, dict) else None

    rows = ap.score(events, rules, since_epoch, git=git_names, past_failed=past_failed, exists=exists)
    by = {}
    for e in events:
        if e.get("id"):
            by.setdefault(e["id"], []).append(e)
    for r in rows:
        evs = by[r["item"]]
        close = [e for e in evs if e.get("event") == "close"][-1]
        sha = (close.get("sha") or "").strip()
        files = git_c(sha) if sha and sha.upper() != "HEAD" else None
        if files == GIT_ERROR and "sha_unresolvable" in r["flags"]:
            r["flags"] = [f for f in r["flags"] if f != "sha_unresolvable"] + ["git_unreadable"]
        evid = (evidence_lookup(sha, r["item"], sorted(p for p, st in files.items() if st != "D"))
                if isinstance(files, dict) and sha else [])
        r["gates"], r["gate_evidence"] = gates(evs, close, files, clean, blob=blob, exists=exists, evidence=evid,
                                               session_of=session_of)
        r["flags"] = r["flags"] + extra_flags(evs, close, r["gate_evidence"])
        r["machine_evidence"] = has_machine_evidence(r["gates"])
        if r["machine_evidence"] and "no_check_evidence" in r["flags"]:
            r["flags"] = [f for f in r["flags"] if f != "no_check_evidence"]   # the prose test missed a record
        if "PASS" in (r["gates"]["G2_independent"], r["gates"].get("G6_independent")):
            r["flags"] = [f for f in r["flags"] if f != "closed_by_maker_only"]   # a non-maker seat checked it
        r["tier0"] = tier0(r["gates"], r["flags"])
        r["unmeasured"] = sorted(k for k, v in r["gates"].items() if v == "UNMEASURED")
    # The rank orders ONLY evidenced OPEN claims that are not already decided (forced, unmeasured, no evidence):
    # rarity is computed over that set, so a gap that is common in the window can never weigh a claim down to 0.
    ranked = [r for r in rows if r["tier0"] == "OPEN" and r["machine_evidence"] and not r["unmeasured"]
              and not any(x in FORCE_T2 for x in r["flags"])]
    if ranked:
        rank_evidenced(ranked, rules)
    cut = _quantile([r["score"] for r in ranked], SLICE_QUANTILE)
    ranked_ids = {id(r) for r in ranked}
    for r in rows:
        if r["tier0"] == "BOUNCE":
            r["tier"] = "T0_BOUNCE"
        elif r["tier0"] == "PASS0":
            r["tier"] = "T0_PASS"
        elif r["unmeasured"]:
            r["tier"] = "T2_UNMEASURED"
        elif not r["machine_evidence"]:
            r["tier"] = "T2_NOEVIDENCE"
        elif any(x in FORCE_T2 for x in r["flags"]):
            r["tier"] = "T2_RISK"
        elif id(r) in ranked_ids and cut is not None and r["score"] >= cut and r["score"] > 0:
            r["tier"] = "T2_RISK"
        else:
            r["tier"] = "T1_PASS"
        r["calibration"] = r["tier"] in ("T0_PASS", "T1_PASS") and calib_pick(r["item"], r["sha"], salt)
        r["decision"] = ("BOUNCE" if r["tier"] == "T0_BOUNCE" else
                         ("HOLD" if ai_refused else "AI") if r["tier"].startswith("T2") else "PASS")
    return rows, cut


def mix(rows):
    n = len(rows) or 1
    out = {}
    for t in TIERS:
        k = sum(1 for r in rows if r["tier"] == t)
        out[t] = [k, round(k / n, 3)]
    k = sum(1 for r in rows if r["tier"].startswith("T2") or r["calibration"])
    out["AI_VERDICTS(T2+calibration)"] = [k, round(k / n, 3)]
    return out


def judge_list(rows, salt):
    """The Arbiter's list: item and sha only, every T2 and calibration claim, in keyed-hash order so calibration
    claims sit among the risky ones with nothing to tell them apart."""
    pick = [r for r in rows if r["tier"].startswith("T2") or r["calibration"]]
    pick.sort(key=lambda r: _keyed(salt, "order", r["item"], r["sha"]))
    return [{"item": r["item"], "sha": r["sha"]} for r in pick]


def bounce_list(rows):
    return [{"item": r["item"], "sha": r["sha"], "gates": {k: v for k, v in r["gates"].items() if v == "FAIL"},
             "gate_evidence": r["gate_evidence"]} for r in rows if r["tier"] == "T0_BOUNCE"]


def past_failed_strict(path):
    """Items with a DEFECT audit. A missing or unreadable file, or a line that is not JSON (it could be the DEFECT that
    matters), raises OSError: no file is not 'nothing failed'."""
    try:
        return ap.past_failed_items(path)
    except ValueError as ex:
        raise OSError(str(ex))


def load_salt(data_dir):
    s = (os.environ.get(SALT_ENV) or "").strip()
    if s:
        return s
    p = os.path.join(data_dir, ".calib_salt")
    if not os.path.exists(p):
        os.makedirs(data_dir, exist_ok=True)
        with open(p, "w") as f:
            f.write(secrets.token_hex(32))
    with open(p) as f:
        s = f.read().strip()
    if not s:
        raise ValueError("%s is empty" % p)
    return s


def _write_json(path, doc):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(doc, f, indent=1, default=sorted)
    os.replace(tmp, path)


def join(argv):
    """verdicts.jsonl (the Arbiter's lines) + tiers_history.jsonl -> verdicts_tiered.jsonl, by (item, sha)."""
    a = argparse.ArgumentParser(prog="arbiter_tiers.py join")
    a.add_argument("--verdicts", default=os.path.join(JUDGE_DIR, "verdicts.jsonl"))
    a.add_argument("--data", default=DATA)
    a = a.parse_args(argv)
    hist = {}
    try:
        with open(os.path.join(a.data, "tiers_history.jsonl")) as fh:
            for line in fh:
                d = json.loads(line)
                hist[(d["item"], d["sha"])] = d
        with open(a.verdicts) as fh:
            verdicts = [json.loads(l) for l in fh if l.strip()]
    except (OSError, ValueError) as ex:
        print("UNMEASURED: %s; nothing written" % ex, file=sys.stderr)
        return 2
    out = []
    for v in verdicts:
        h = hist.get((v.get("item"), v.get("sha")))
        out.append(dict(v, tier=h["tier"] if h else "UNKNOWN", calibration=h["calibration"] if h else None,
                        tiered_at=h["generated"] if h else None))
    tmp = os.path.join(a.data, "verdicts_tiered.jsonl.tmp")
    with open(tmp, "w") as f:
        f.writelines(json.dumps(r, sort_keys=True) + "\n" for r in out)
    os.replace(tmp, os.path.join(a.data, "verdicts_tiered.jsonl"))
    print("joined %d verdicts; %d with no tier record" % (len(out), sum(1 for r in out if r["tier"] == "UNKNOWN")))
    return 0


def main(argv=None, events=None, _inject=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["join"]:
        return join(argv[1:])
    a = argparse.ArgumentParser()
    a.add_argument("--days", type=float, default=7)
    a.add_argument("--data", default=DATA, help="measurement dir (tiers.json, history, salt)")
    a.add_argument("--judge-dir", default=JUDGE_DIR, help="the Arbiter's dir (judge_list.json, bounces.json)")
    a.add_argument("--now")
    a.add_argument("--past-audits", help="Auditor DEFECT log (default: rules past_audits_file)")
    a.add_argument("--evidence-dir", help="close_evidence folder (default: close_evidence.evidence_dir())")
    a.add_argument("--ai-refused", action="store_true", help="no AI run this batch: every tier-2 claim is HOLD")
    a = a.parse_args(argv)
    rules = ap.load_rules()
    now = calendar.timegm(time.strptime(a.now, "%Y-%m-%dT%H:%M:%SZ")) if a.now else time.time()
    since = now - 86400 * a.days
    try:
        if events is None:
            from rimflow import model
            events = model.read()
        if not events:
            raise ValueError("ledger read returned no events")
    except Exception as ex:
        print("UNMEASURED: ledger unreadable (%s); nothing written" % ex, file=sys.stderr)
        return 2
    try:
        clean = (_inject or {}).get("clean") or load_clean_hashes()
        if not clean:
            raise ValueError("no clean code-review records readable; G5 would be blind")
        past = a.past_audits or rules["past_audits_file"]
        try:
            past_failed = past_failed_strict(past)
        except OSError as ex:
            raise ValueError("past audits unreadable (%s): past_audit_failed would never fire. The Auditor creates "
                             "it (an empty file = no audits yet); or pass --past-audits" % ex)
        efolder = a.evidence_dir or str(ce.evidence_dir())
        if not os.path.isdir(efolder):
            raise ValueError("close-evidence folder %s missing" % efolder)
        ce._key()          # raises when the mac key is missing: no line could be verified -- UNMEASURED, not "none"
        evid = ce.read_all(days=int(a.days) + 31, folder=efolder)
        salt = load_salt(a.data)
    except Exception as ex:
        print("UNMEASURED: %s; nothing written" % ex, file=sys.stderr)
        return 2
    rows, cut = classify(events, rules, since, clean=clean, past_failed=past_failed, salt=salt,
                         evidence_lookup=lambda sha, item, paths: lookup_close_evidence(
                             sha, item, paths, folder=efolder, days=int(a.days) + 31),
                         ai_refused=a.ai_refused, session_of=commit_session,
                         **{k: v for k, v in (_inject or {}).items() if k != "clean"})
    gate_counts = {}
    for r in rows:
        for gname, v in r["gates"].items():
            gate_counts.setdefault(gname, {}).setdefault(v, 0)
            gate_counts[gname][v] += 1
    gen = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
    doc = {"generated": gen, "since": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(since)),
           "closes_seen": len(rows), "slice_cut_score": cut, "ai_refused": a.ai_refused, "mix": mix(rows),
           "gate_counts": gate_counts, "signal_counts_rates": ap.signal_rates(rows),
           "close_evidence_records": len(evid), "rows": rows}
    _write_json(os.path.join(a.data, "tiers.json"), doc)
    _write_json(os.path.join(a.data, "tiers_%s.json" % gen.replace(":", "").replace("-", "")), doc)
    with open(os.path.join(a.data, "tiers_history.jsonl"), "a") as f:
        for r in rows:
            f.write(json.dumps({"generated": gen, "item": r["item"], "sha": r["sha"], "tier": r["tier"],
                                "calibration": r["calibration"], "decision": r["decision"]}) + "\n")
    _write_json(os.path.join(a.judge_dir, "judge_list.json"),
                {"generated": gen, "claims": [] if a.ai_refused else judge_list(rows, salt)})
    _write_json(os.path.join(a.judge_dir, "bounces.json"), {"generated": gen, "advisory": True,
                                                             "bounces": bounce_list(rows)})
    print("closes seen: %d  (since %s)  slice cut score: %s  close-evidence records: %d"
          % (len(rows), doc["since"], cut, len(evid)))
    for t, (k, rt) in doc["mix"].items():
        print("  %-28s %4d  %5.1f%%" % (t, k, 100 * rt))
    for gname in sorted(gate_counts):
        print("  %-18s %s" % (gname, json.dumps(gate_counts[gname], sort_keys=True)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
