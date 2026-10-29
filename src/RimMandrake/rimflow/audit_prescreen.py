"""audit_prescreen.py - no-AI risk pre-screen of recent closes for the Auditor.

Reads closes from the merged ledger (model.read), scores each with cheap signals
weighted by audit_prescreen_rules.json, writes the ranked list to prescreen.json.
Unreadable ledger => UNMEASURED: no file written, exit 2.

    python3 src/RimMandrake/rimflow/audit_prescreen.py [--days N] [--out PATH] [--now ISO]
"""
import argparse, datetime, json, math, os, random, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
RULES = os.path.join(HERE, "audit_prescreen_rules.json")
OUT = "/mnt/d/ClaudeWork/rimmandrake/auditor/prescreen.json"
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def load_rules(path=RULES):
    with open(path) as f:
        return json.load(f)


def _epoch(ts):
    """ISO-8601 UTC ('...Z', optional fractional seconds) -> epoch seconds. Never local time: mktime applied DST."""
    return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()


def git_files(sha, repo=REPO):
    """Files a commit touches, or None if the sha does not resolve."""
    try:
        r = subprocess.run(["git", "-C", repo, "diff-tree", "--no-commit-id", "--name-only", "-r",
                            "--root", sha], capture_output=True, text=True, timeout=30)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return [l for l in r.stdout.splitlines() if l]


def _checked(evs, close, rules):
    """True if the item shows any sign it was checked: a verify event, or text (close reason/why,
    notes, finding) naming a test, selftest, review or measurement."""
    if any(e.get("event") in ("verify", "finding") for e in evs):
        return True
    rx = re.compile(rules["check_evidence_regex"], re.I)
    for e in evs:
        if e.get("event") in ("close", "note", "implemented", "reconcile"):
            if rx.search(" ".join(str(e.get(k) or "") for k in ("reason", "why", "text", "note"))):
                return True
    return False


def _rank(rows, rules):
    """Weight each signal by its rarity over this window: mult * min(cap, -log2(rate)).
    A signal with rate > max_signal_rate carries no weight and is never a hard flag."""
    n = len(rows)
    rate = {}
    for r in rows:
        for f in set(r["flags"]):
            rate[f] = rate.get(f, 0) + 1
    for f in rate:
        rate[f] = rate[f] / n if n >= rules["min_sample"] else rules["prior_rate"]
    mult, cap, mx = rules["weights"], rules["info_cap_bits"], rules["max_signal_rate"]
    for r in rows:
        r["score"] = round(sum(mult.get(f, 1) * min(cap, -math.log2(rate[f]))
                               for f in r["flags"] if rate[f] <= mx), 1)
        r["hard"] = [f for f in r["flags"] if f in rules["hard_flags"] and rate[f] <= mx]
    rows.sort(key=lambda r: (-r["score"], r["closed_at"], r["item"]))
    return rows


def signal_rates(rows):
    n = len(rows) or 1
    c = {}
    for r in rows:
        for f in set(r["flags"]):
            c[f] = c.get(f, 0) + 1
    return {f: [k, round(k / n, 3)] for f, k in sorted(c.items(), key=lambda x: -x[1])}


def score(events, rules, since_epoch, git=git_files, past_failed=frozenset(), exists=os.path.exists, until=None):
    """Rank closes in [since_epoch, until]. Events after `until` (the audit's --now) are invisible; each item's events
    are taken in time order, not input order."""
    by, kids = {}, {}
    T = lambda e: _epoch(e["ts"])
    events = sorted((e for e in events if e.get("ts") and (until is None or T(e) <= until)), key=T)
    for e in events:
        if e.get("id"):
            by.setdefault(e["id"], []).append(e)
        # follow-up work filed against an item: `file --caused-by X` (id + caused_by) or `spawn --from X` (name + from)
        parent = e.get("caused_by") if e.get("event") == "file" else e.get("from") if e.get("event") == "spawn" else None
        if parent:
            kids.setdefault(parent, []).append(e)
    rows = []
    for iid, evs in by.items():
        closes = [e for e in evs if e.get("event") == "close" and T(e) >= since_epoch]
        if not closes:
            continue
        c = closes[-1]
        flags = []
        sha = (c.get("sha") or "").strip()
        verifies = [e for e in evs if e.get("event") == "verify"]
        files = None
        if not _checked(evs, c, rules):
            flags.append("no_check_evidence")
        if verifies and verifies[-1].get("result") != "pass":
            flags.append("verify_not_pass")
        if not sha:
            flags.append("sha_missing")
        elif sha.upper() == "HEAD":
            flags.append("sha_head_literal")
        else:
            files = git(sha)
            if files is None:
                flags.append("sha_unresolvable")
            else:
                if not files:
                    flags.append("sha_touches_nothing")
                if len(files) >= rules["many_files_threshold"]:
                    flags.append("many_files")
                if any(m in f for f in files for m in rules["gate_path_markers"]):
                    flags.append("gate_or_harness_path")
                if any(m in f for f in files for m in rules.get("flowworks_path_markers", [])):
                    flags.append("flowworks_or_live")
        for v in verifies:
            p = v.get("evidence") or ""
            if p.startswith("/") and ":" not in p.split("/")[0] and not exists(p):
                flags.append("evidence_path_absent")
                break
        # the maker: whoever last took the item before the close (`claim`, or `start`/`reclaim` with no lease)
        claims = [e for e in evs if e.get("event") in ("claim", "start", "reclaim") and T(e) <= T(c)]
        if claims and c.get("seat") == claims[-1].get("seat") and not any(
                v.get("seat") != c.get("seat") for v in verifies):
            flags.append("closed_by_maker_only")
        if claims and _epoch(c["ts"]) - _epoch(claims[-1]["ts"]) < rules["short_claim_seconds"]:
            flags.append("short_claim_to_close")
        if len([e for e in evs if e.get("event") == "close"]) > 1 or any(
                e.get("event") in ("claim", "start", "reclaim") and T(e) > T(c) for e in evs):
            flags.append("reopened_before")
        if any(m in iid for m in rules["flowworks_id_markers"]) and "flowworks_or_live" not in flags:
            flags.append("flowworks_or_live")
        # signs after the close, before this audit: work filed against it, or another seat writing on it
        if any(T(k) > T(c) for k in kids.get(iid, [])):
            flags.append("followup_after_close")
        if any(e.get("event") in ("note", "finding", "block") and T(e) > T(c)
               and e.get("seat") != c.get("seat") for e in evs):
            flags.append("noted_after_close")
        if iid in past_failed:
            flags.append("past_audit_failed")
        rows.append({"item": iid, "sha": sha, "closed_at": c["ts"], "closed_by": c.get("seat"),
                     "flags": flags,
                     "files_changed": None if files is None else len(files)})
    return _rank(rows, rules)


def build(rows, rules, seed):
    rnd = random.Random(seed)
    n = len(rows)
    k = n // rules["calibration_every"] if n else 0
    calib = sorted(r["item"] for r in rnd.sample(rows, k)) if k else []
    return {"closes_seen": n, "ranked": rows, "calibration_picks": calib,
            "hard_flagged": [r["item"] for r in rows if r["hard"]],
            "signal_counts_rates": signal_rates(rows)}


def past_failed_items(path):
    """Items with a DEFECT audit in the Auditor's audits.jsonl, read through audits.py (the schema's one reader). A
    missing or unreadable file raises OSError, a line that breaks audits.schema.json raises ValueError: no file is
    UNMEASURED, never 'no past failures' (review AA, brief AA8)."""
    from rimflow import audits
    return audits.past_failed(audits.read(path))


def main(argv=None, events=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=float)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--now")
    ap.add_argument("--past-audits", help="the Auditor's audits.jsonl (default: rules past_audits_file)")
    a = ap.parse_args(argv)
    rules = load_rules()
    try:
        if events is None:
            from rimflow import model
            events = model.read()
        if not events:
            raise ValueError("ledger read returned no events")
    except Exception as ex:
        print("UNMEASURED: ledger unreadable (%s); no list written" % ex, file=sys.stderr)
        return 2
    now = _epoch(a.now) if a.now else time.time()
    since = now - 86400 * (a.days or rules["window_days"])
    try:
        past_failed = past_failed_items(a.past_audits or rules["past_audits_file"])
    except (OSError, ValueError) as ex:
        print("UNMEASURED: past audits unreadable (%s): past_audit_failed would never fire. The Auditor creates the "
              "file (empty = no audits yet); no list written" % ex, file=sys.stderr)
        return 2
    rows = score(events, rules, since, past_failed=past_failed, until=now)
    doc = build(rows, rules, seed=int(since // 86400))
    doc["generated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
    doc["since"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(since))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    tmp = a.out + ".tmp"
    with open(tmp, "w") as f:
        json.dump(doc, f, indent=1)
    os.replace(tmp, a.out)
    print("closes seen: %d; hard-flagged: %d" % (doc["closes_seen"], len(doc["hard_flagged"])))
    for f, (k, rt) in doc["signal_counts_rates"].items():
        print("  %-24s %4d  %.1f%%" % (f, k, 100 * rt))
    for r in rows[:5]:
        print("%4d  %s  %s" % (r["score"], r["item"], ",".join(r["flags"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
