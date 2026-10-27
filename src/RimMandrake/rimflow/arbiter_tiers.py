"""arbiter_tiers.py - no-AI triage of done claims into the Arbiter's tiers.

Design: design/RimMandrake/rimflow_v3_arbiter_tiers_2026-10-27.md (item ARBITER_REDESIGN_RISK_TIERED_VERDICTS).

  tier 0  deterministic gates over evidence already recorded (ledger verify/implemented/finding/note events, the
          code-review shards, close_evidence records). Outcome BOUNCE (a recorded hard failure), PASS0 (every gate
          clear, every touched path covered by a passing close_evidence run from an independent seat in an isolated
          checkout of the sha -- a ledger verify never substitutes, review AB1 -- no risk flag) or OPEN.
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
import argparse, calendar, contextlib, glob, hashlib, hmac, json, os, re, secrets, subprocess, sys, tempfile, time

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


#: commit_session() could not read the commit in any clone (review AC4): distinct from None (read, no trailer), so a
#: lookup failure never lets a same-session run pass as independent.
SESSION_UNREADABLE = "?unreadable"


def commit_session(sha, repos=REPOS):
    """The commit's `Claude-Session:` trailer (the bridge session that made it); None when a clone read the commit
    and it has no trailer; SESSION_UNREADABLE when no clone could read it (timeout, missing clone, unknown sha)."""
    for repo in repos:
        try:
            r = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%(trailers:key=Claude-Session,valueonly)",
                                sha], capture_output=True, text=True, timeout=30)
        except Exception:
            continue
        if r.returncode == 0:
            m = re.search(r"session_[A-Za-z0-9]+", r.stdout or "")
            return m.group(0) if m else None
    return SESSION_UNREADABLE


_HEX_SHA = re.compile(r"[0-9a-fA-F]{7,40}")


def _rev_one(sha, repo):
    """The full commit sha `sha` names in `repo`; None when it names none there; GIT_ERROR when git could not answer
    or the prefix is ambiguous inside the clone. No `--quiet`: it silences the ambiguity message (rc 1, empty stderr),
    which made an ambiguous prefix read as "not here" (review AD F6)."""
    if not os.path.isdir(repo):
        return GIT_ERROR
    try:
        r = subprocess.run(["git", "-C", repo, "rev-parse", "--verify", "%s^{commit}" % sha],
                           capture_output=True, text=True, timeout=30, env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"))
    except Exception:
        return GIT_ERROR
    out, err = (r.stdout or "").strip(), (r.stderr or "")
    if r.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", out):
        return out
    if "ambiguous" in err.lower():
        return GIT_ERROR
    if r.returncode != 0 and re.search(r"Needed a single revision|unknown revision|bad revision", err):
        return None
    return GIT_ERROR


def resolve_sha_any(sha, repos=REPOS, rev=_rev_one):
    """The ONE full commit sha a claim's sha names across every clone (review AC2): None when it is not a hex sha
    (a rev expression like `child^` is not a build identity) or no clone has it; GIT_ERROR when clones disagree (a
    short sha naming different commits), when an ABBREVIATED sha met an error or ambiguity in any clone, or none could
    answer while none had it."""
    sha = (sha or "").strip()
    if not _HEX_SHA.fullmatch(sha):
        return None
    found, err = set(), False
    for repo in repos:
        f = rev(sha, repo)
        if f == GIT_ERROR:
            err = True
        elif f:
            found.add(f.lower())
    if len(found) > 1:
        return GIT_ERROR
    if err and len(sha) < 40:     # review AD F6: a prefix unique here may be ambiguous there -- not one identity
        return GIT_ERROR
    if found:
        return found.pop()
    return GIT_ERROR if err else None


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
    # G6 close evidence (selftests, builds, validators at this sha). FAIL/UNMEASURED: per tool, the latest run covering
    # each path anywhere in the claim's evidence (ce.summarize, by actual coverage -- review AB4). PASS only when every touched, non-deleted path is covered by a passing run of
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
        # review AB4: per touched path, only the LATEST run of each full tool that actually covers it may vouch for
        # it -- an older broad PASS superseded on that path by a FAIL never counts for coverage or independence
        latest = {f: [r for r in ce.latest_covering(list(evidence), f).values()
                      if r.get("result") == "PASS" and not r.get("variant")] for f in need}
        full = [r for rs in latest.values() for r in rs]
        uncov = [f for f in need if not latest[f]] if need else ["(the commit only deletes: nothing to cover)"]
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
        def indep(r):
            return seat_sure(r) and r["seat"] not in makers and not (csess and who_of(r).get("bridge_session") == csess)
        ind_all = need and all(any(indep(r) for r in latest[f]) for f in need)
        unsure = [r for r in full if not seat_sure(r)]
        if not full:
            pass                                       # no passing full run: nothing to be independent
        elif not builder_known:
            g["G6_independent"] = "UNMEASURED"
            ev["G6_independent"] = "the ledger names no builder (no claim/start/implemented before the close)"
        elif ind_all and csess == SESSION_UNREADABLE:
            g["G6_independent"] = "UNMEASURED"
            ev["G6_independent"] = "the commit's Claude-Session could not be read: a same-session run cannot be ruled out"
        elif ind_all:
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
    # review AB1: PASS0 needs independent, clean-ISOLATED-tree runs covering every touched path (G6). A ledger verify
    # carries no sha, cleanliness or path provenance, so however independent it is it can only add, never substitute.
    independent = g6 == "PASS" and g.get("G6_independent") == "PASS" and g["G2_verify"] in ("PASS", "NONE")
    clear = (independent and g["G1_sha"] == "PASS" and g["G3_criteria"] in ("PASS", "NONE")
             and g["G4_evidence"] in ("PASS", "NONE") and g["G5_review"] in ("PASS", "NONE")
             and g6 == "PASS")
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
             ai_refused=False, session_of=lambda sha: None, resolve=None):
    """resolve(sha) -> the one full sha the close names (resolve_sha_any; with an injected `git` and no resolve, the
    close's sha is taken as written)."""
    if resolve is None:
        resolve = resolve_sha_any if git is git_files_any else (lambda s: s)
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
        full = resolve(sha) if sha and sha.upper() != "HEAD" else None      # review AC2: one full sha, used throughout
        files = git_c(full) if isinstance(full, str) and full != GIT_ERROR else (GIT_ERROR if full == GIT_ERROR else None)
        if files == GIT_ERROR and "sha_unresolvable" in r["flags"]:
            r["flags"] = [f for f in r["flags"] if f != "sha_unresolvable"] + ["git_unreadable"]
        evid = (evidence_lookup(full, r["item"], sorted(p for p, st in files.items() if st != "D"))
                if isinstance(files, dict) and full else [])
        r["gates"], r["gate_evidence"] = gates(evs, close, files, clean, blob=lambda _s, f, _f=full: blob(_f, f),
                                               exists=exists, evidence=evid,
                                               session_of=lambda _s, _f=full: session_of(_f))
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
        # review AB8: a calibration pick needs an AI verdict like a tier-2 claim; with no AI run it is HOLD, never a
        # silent PASS whose audit vanished from an empty judge list
        needs_ai = r["tier"].startswith("T2") or r["calibration"]
        r["decision"] = ("BOUNCE" if r["tier"] == "T0_BOUNCE" else
                         ("HOLD" if ai_refused else "AI") if needs_ai else "PASS")
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
    """Items with a DEFECT audit, read via audits.py against audits.schema.json (AUDITOR_BUILD_AUDITS_FILE). A missing
    or unreadable file, or a line that breaks the schema (it could be the DEFECT that matters), raises OSError: no
    file is not 'nothing failed'. `audits.py ensure` creates the empty file."""
    from rimflow import audits
    try:
        return audits.past_failed(audits.read(path))
    except ValueError as ex:
        raise OSError(str(ex))


def load_salt(data_dir):
    s = (os.environ.get(SALT_ENV) or "").strip()
    if s:
        return s
    p = os.path.join(data_dir, ".calib_salt")
    if not os.path.exists(p):
        ce.publish_once(p, secrets.token_hex(32))   # review AB9: one complete salt wins; racers read the winner's
    with open(p) as f:
        s = f.read().strip()
    if not s:
        raise ValueError("%s is empty" % p)
    return s


def _write_json(path, doc):
    """Atomic replace through a tmp file unique to this writer (review AB10: a shared `.tmp` name let one writer
    publish another's half-written document and then crash on os.replace)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(path) + ".", suffix=".tmp", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(doc, f, indent=1, default=sorted)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


@contextlib.contextmanager
def _locked(data_dir, shared=False):
    """The batch lock (review AB10): a run publishes tiers.json, its history lines, judge_list.json and bounces.json
    under an EXCLUSIVE flock on <data>/tiers_history.jsonl.lock, so two runs never interleave and the judge list and
    bounces always come from one run; `join` reads the history under a SHARED lock (drvfs appends are not atomic)."""
    import fcntl
    os.makedirs(data_dir, exist_ok=True)
    fd = os.open(os.path.join(data_dir, "tiers_history.jsonl.lock"), os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_SH if shared else fcntl.LOCK_EX)
        yield
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def _unique(path):
    """`path`, or `path` with -2, -3 ... before the extension when it exists: a per-run snapshot is never
    overwritten by a second run in the same second (history is kept). Call under _locked()."""
    if not os.path.exists(path):
        return path
    stem, ext = os.path.splitext(path)
    k = 2
    while os.path.exists("%s-%d%s" % (stem, k, ext)):
        k += 1
    return "%s-%d%s" % (stem, k, ext)


def join(argv):
    """verdicts.jsonl (the Arbiter's lines) + tiers_history.jsonl -> verdicts_tiered.jsonl, by (item, sha)."""
    a = argparse.ArgumentParser(prog="arbiter_tiers.py join")
    a.add_argument("--verdicts", default=os.path.join(JUDGE_DIR, "verdicts.jsonl"))
    a.add_argument("--data", default=DATA)
    a = a.parse_args(argv)
    hist = {}
    try:
        with _locked(a.data, shared=True), open(os.path.join(a.data, "tiers_history.jsonl")) as fh:
            lines = fh.readlines()
        for line in lines:
            if line.strip():
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
    fd, tmp = tempfile.mkstemp(prefix="verdicts_tiered.jsonl.", suffix=".tmp", dir=a.data)
    with os.fdopen(fd, "w") as f:
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
            raise ValueError("past audits unreadable (%s): past_audit_failed would never fire. Create it with "
                             "`python3 src/RimMandrake/rimflow/audits.py ensure` (an empty file = no audits yet); or "
                             "pass --past-audits" % ex)
        efolder = a.evidence_dir or str(ce.evidence_dir())
        if not os.path.isdir(efolder):
            raise ValueError("close-evidence folder %s missing" % efolder)
        ce._key()          # raises when the mac key is missing: no line could be verified -- UNMEASURED, not "none"
        evid = ce.read_all(days=int(a.days) + 31, folder=efolder)
        salt = load_salt(a.data)
    except Exception as ex:
        print("UNMEASURED: %s; nothing written" % ex, file=sys.stderr)
        return 2
    kw = dict(clean=clean, past_failed=past_failed, salt=salt,
              evidence_lookup=lambda sha, item, paths: lookup_close_evidence(
                  sha, item, paths, folder=efolder, days=int(a.days) + 31),
              ai_refused=a.ai_refused, session_of=commit_session)
    kw.update({k: v for k, v in (_inject or {}).items() if k != "clean"})
    try:
        rows, cut = classify(events, rules, since, **kw)
    except Exception as ex:        # review AC5: an evidence read failing mid-classification is UNMEASURED, not a crash
        print("UNMEASURED: classification could not read its evidence (%s: %s); nothing written"
              % (type(ex).__name__, ex), file=sys.stderr)
        return 2
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
    with _locked(a.data):
        _write_json(os.path.join(a.data, "tiers.json"), doc)
        _write_json(_unique(os.path.join(a.data, "tiers_%s.json" % gen.replace(":", "").replace("-", ""))), doc)
        hist = "".join(json.dumps({"generated": gen, "item": r["item"], "sha": r["sha"], "tier": r["tier"],
                                   "calibration": r["calibration"], "decision": r["decision"]}) + "\n" for r in rows)
        with open(os.path.join(a.data, "tiers_history.jsonl"), "a") as f:
            f.write(hist)
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
