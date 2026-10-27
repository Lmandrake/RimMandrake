"""audit_prescreen.py - no-AI risk pre-screen of recent closes for the Auditor.

Reads closes from the merged ledger (model.read), scores each with cheap signals
weighted by audit_prescreen_rules.json, writes the ranked list to prescreen.json.
Unreadable ledger => UNMEASURED: no file written, exit 2.

    python3 src/RimMandrake/rimflow/audit_prescreen.py [--days N] [--out PATH] [--now ISO]
"""
import argparse, json, os, random, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
RULES = os.path.join(HERE, "audit_prescreen_rules.json")
OUT = "/mnt/d/ClaudeWork/rimmandrake/auditor/prescreen.json"
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def load_rules(path=RULES):
    with open(path) as f:
        return json.load(f)


def _epoch(ts):
    return time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")) - time.timezone


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


def score(events, rules, since_epoch, git=git_files, past_failed=frozenset(), exists=os.path.exists):
    by = {}
    for e in events:
        if e.get("id"):
            by.setdefault(e["id"], []).append(e)
    w = rules["weights"]
    rows = []
    for iid, evs in by.items():
        closes = [e for e in evs if e.get("event") == "close" and _epoch(e["ts"]) >= since_epoch]
        if not closes:
            continue
        c = closes[-1]
        flags = []
        sha = (c.get("sha") or "").strip()
        verifies = [e for e in evs if e.get("event") == "verify"]
        files = None
        if not verifies:
            flags.append("no_verify_event")
        elif verifies[-1].get("result") != "pass":
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
        for v in verifies:
            p = v.get("evidence") or ""
            if p.startswith("/") and ":" not in p.split("/")[0] and not exists(p):
                flags.append("evidence_path_absent")
                break
        claims = [e for e in evs if e.get("event") == "claim" and e["ts"] <= c["ts"]]
        if claims and c.get("seat") == claims[-1].get("seat") and not any(
                v.get("seat") != c.get("seat") for v in verifies):
            flags.append("closed_by_maker_only")
        if claims and _epoch(c["ts"]) - _epoch(claims[-1]["ts"]) < rules["short_claim_seconds"]:
            flags.append("short_claim_to_close")
        if len([e for e in evs if e.get("event") == "close"]) > 1 or any(
                e.get("event") in ("claim", "start", "reclaim") and e["ts"] > c["ts"] for e in evs):
            flags.append("reopened_before")
        if any(m in iid for m in rules["flowworks_id_markers"]):
            flags.append("flowworks_or_live")
        if iid in past_failed:
            flags.append("past_audit_failed")
        rows.append({"item": iid, "sha": sha, "closed_at": c["ts"], "closed_by": c.get("seat"),
                     "flags": flags, "score": sum(w.get(f, 0) for f in flags),
                     "hard": [f for f in flags if f in rules["hard_flags"]],
                     "files_changed": None if files is None else len(files)})
    rows.sort(key=lambda r: (-r["score"], r["closed_at"], r["item"]))
    return rows


def build(rows, rules, seed):
    rnd = random.Random(seed)
    n = len(rows)
    k = n // rules["calibration_every"] if n else 0
    calib = sorted(r["item"] for r in rnd.sample(rows, k)) if k else []
    return {"closes_seen": n, "ranked": rows, "calibration_picks": calib,
            "hard_flagged": [r["item"] for r in rows if r["hard"]]}


def past_failed_items(path):
    out = set()
    try:
        for line in open(path):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("verdict") == "DEFECT" and d.get("item"):
                out.add(d["item"])
    except OSError:
        pass
    return out


def main(argv=None, events=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=float)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--now")
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
    rows = score(events, rules, since, past_failed=past_failed_items(rules["past_audits_file"]))
    doc = build(rows, rules, seed=int(since // 86400))
    doc["generated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
    doc["since"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(since))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    tmp = a.out + ".tmp"
    with open(tmp, "w") as f:
        json.dump(doc, f, indent=1)
    os.replace(tmp, a.out)
    print("closes seen: %d; hard-flagged: %d" % (doc["closes_seen"], len(doc["hard_flagged"])))
    for r in rows[:5]:
        print("%4d  %s  %s" % (r["score"], r["item"], ",".join(r["flags"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
