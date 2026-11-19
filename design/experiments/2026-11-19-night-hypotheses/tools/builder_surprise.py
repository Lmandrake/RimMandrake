#!/usr/bin/env python3
"""Read-only replay for 05-builder-surprise.md: mark each detached run's report for an admitted doubt, then gather
what later acts touched the same item or files within 48 hours.

    builder_surprise.py <repo_root> <detached_dir> <conductor_log.md> <since_epoch> <out_dir> [--verdicts <file>]

Pass 1 (no --verdicts): writes <out_dir>/runs.json (marks, hidden from the judge) and <out_dir>/candidates.txt
(the fault-word hits, shuffled, with no mark shown) for a hand verdict. Pass 2 (--verdicts <json {cand_id: true|
false}>): joins and prints the 2x2. VERDICT line last. Exit 0 measured, 3 could not look.
"""
import glob, json, os, random, re, subprocess, sys, time
from datetime import datetime, timezone

MARKS = {
    "UNTESTED": r"\buntested\b|\bUNRUN\b|\bnot (?:yet )?(?:been )?(?:tested|run|verified|checked|exercised)\b|"
                r"\bcould not (?:verify|test|run|check|reproduce)\b|\bunverified\b|\bdid not (?:test|run|verify|check)\b",
    "SLIP": r"\bmy (?:own )?(?:mistake|error|slip)\b|\bI (?:was wrong|missed|broke|forgot)\b|"
            r"\bfirst (?:attempt|try|close|publish|run) (?:failed|was refused)\b|\bhad to (?:redo|re-do|fix)\b|\bcorrected\b",
    "DOUBT": r"\bnot sure\b|\bunsure\b|\buncertain\w*|\bunclear\b|\bmight not\b|\[guess",
    "SURPRISE": r"\bsurpris\w*|\bunexpected\w*|\bturned out\b|\bcontrary to\b",
}
# The first, broad word list (fail, refus..., bug) drew 631 candidates from 149 runs: this repo's own vocabulary
# ("refuses by name", "fails loudly") is full of it. The gate is phrases that say earlier work was wrong.
FAULT = re.compile(r"\b(?:not true|(?:was|is|were|are) (?:wrong|stale|false|incorrect)|stale (?:test|check|claim|count)s?|"
                   r"went red|(?:still|now) (?:fails?|red|broken)|left \w+(?: \w+)? red|broke\b|broken by|regress\w*|"
                   r"slip(?:ped|s)? past|did not (?:catch|work|fix|hold)|does not (?:catch|work|hold)|never (?:fired|ran|worked)|"
                   r"missed|overcount\w*|double[- ]count\w*|counted (?:twice|again)|false (?:pass|green|claim|clean)|"
                   r"reopen\w*|revert\w*|undid|gap(?:s)? (?:found|left)|found \w+ (?:more )?(?:gaps|holes|faults|defects|bugs)|"
                   r"fails? (?:on main|after|since)|(?:a|the) (?:defect|bug|fault) in)", re.I)
WINDOW = 48 * 3600
SKIP_EV = {"lease", "bridge", "seat", "TRACKED", "game", "guard"}
MACHINE_WHY = {"detached run clone returned", "detached run ended", "pipe stop"}   # the launcher's own bookkeeping
MACHINE_LOG = re.compile(r"^\S+ — (?:DETACHED RUN ENDED|DISPATCHER ESCALATION|LEFT OPEN CONTINUE)")  # later runs come in via run:
NOISE_PATH = re.compile(r"^(?:infrastructure/state/|conversations/|Transient/|journal/)")


def epoch(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        try:
            return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
        except ValueError:
            return None


def own_tokens(runs, RL):
    """Each run's own part of its session's weighted tokens: session total minus the largest earlier total."""
    by = {}
    for r in runs:
        by.setdefault(r["session"], []).append(r)
    for rs in by.values():
        rs.sort(key=lambda r: r["ended"])
        hi = 0
        for r in rs:
            t = r["total"]
            r["tokens"] = None if t is None else max(0, t - hi)
            hi = max(hi, t or 0)


def load_runs(repo, folder, since):
    sys.path.insert(0, os.path.join(repo, "src", "RimMandrake", "rimflow"))
    import role_launch as RL
    runs = []
    for p in glob.glob(os.path.join(folder, "*.json")):
        if p.endswith(".out.json"):
            continue
        try:
            rec = json.load(open(p))
            res = json.load(open(rec["out"]))
        except Exception:
            continue
        at, end = epoch(rec.get("at")), epoch(rec.get("ended"))
        if at is None or at < since or end is None or rec.get("status") != "finished":
            continue
        try:
            total = RL.run_tokens(res, rec.get("model"))
        except Exception:
            total = None
        runs.append(dict(unit=rec["unit"], item=rec["item"], at=at, ended=end, model=rec.get("model"),
                         session=res.get("session_id") or rec["unit"], total=total,
                         text=str(res.get("result") or ""), result=rec.get("result")))
    own_tokens(runs, RL)
    return runs


def ledger(repo):
    out = []
    for p in glob.glob(os.path.join(repo, "infrastructure/state/ledger/events/*.jsonl")):
        for line in open(p, errors="replace"):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            t = epoch(e.get("ts"))
            if t is not None:
                e["_t"] = t
                out.append(e)
    return out


def log_entries(path):
    head = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ) — ")
    ents, cur = [], None
    for line in open(path, errors="replace"):
        m = head.match(line)
        if m:
            cur = [epoch(m.group(1)), line]
            ents.append(cur)
        elif cur is not None:
            cur[1] += line
    return ents


def files_of(repo, sha):
    try:
        o = subprocess.run(["git", "-C", repo, "show", "--name-only", "--format=", sha], capture_output=True,
                           text=True, timeout=60).stdout
    except Exception:
        return []
    return [f for f in o.split("\n") if f and not NOISE_PATH.match(f)]


def later_commits(repo, since):
    o = subprocess.run(["git", "-C", repo, "log", "origin/main", "--since=@%d" % int(since), "--name-only",
                        "--format=\x01%H\x02%ct\x02%s %b"], capture_output=True, text=True, timeout=300).stdout
    out = []
    for blk in o.split("\x01")[1:]:
        head, _, names = blk.partition("\n")
        h, ct, msg = head.split("\x02", 2)
        out.append((h, float(ct), msg, set(n for n in names.split("\n") if n and not NOISE_PATH.match(n))))
    return out


def snip(text, m, w=160):
    a, b = max(0, m.start() - w), min(len(text), m.end() + w)
    return re.sub(r"\s+", " ", text[a:b])


def main(a):
    if len(a) < 6:
        print(__doc__)
        return 2
    repo, folder, logp, since, outd = a[1], a[2], a[3], float(a[4]), a[5]
    verd = json.load(open(a[a.index("--verdicts") + 1])) if "--verdicts" in a else None
    now = time.time()
    try:
        runs = load_runs(repo, folder, since)
        evs = ledger(repo)
        ents = log_entries(logp)
        commits = later_commits(repo, since)
    except Exception as e:
        print("VERDICT could-not-look: %r" % (e,))
        return 3
    if not runs:
        print("VERDICT could-not-look: no finished run with a readable result since %s" % since)
        return 3
    os.makedirs(outd, exist_ok=True)
    known = {h[:10]: (h, ct, names) for h, ct, msg, names in commits}
    for r in runs:                       # what each run landed: its close/verify shas, and shas its report cites
        shas = {str(e["sha"])[:10] for e in evs if e.get("role_unit") == r["unit"] and e.get("sha")
                and e.get("event") in ("close", "verify")}
        for m in re.finditer(r"\b[0-9a-f]{10,40}\b", r["text"]):
            k = known.get(m.group(0)[:10])
            if k and r["at"] - 60 <= k[1] <= r["ended"] + 600:
                shas.add(m.group(0)[:10])
        r["shas"] = sorted(s for s in shas if s in known)
        r["files"] = sorted(set().union(*[known[s][2] for s in r["shas"]]) if r["shas"] else [])
        r["closed_ids"] = sorted({e["id"] for e in evs if e.get("role_unit") == r["unit"] and e.get("event") == "close"})
    used_by = {}
    for r in runs:
        for f in r["files"]:
            used_by.setdefault(f, set()).add(r["unit"])
    cands = []
    for r in runs:
        r["marks"] = sorted(k for k, pat in MARKS.items() if re.search(pat, r["text"], re.I))
        lo, hi = r["ended"], min(r["ended"] + WINDOW, now)
        r["window_h"] = round((hi - lo) / 3600, 1)
        iid, looks = r["item"], []
        ids = set(r["closed_ids"]) | {iid}
        r["close_sha"] = r["shas"][0] if r["shas"] else None
        distinct = {f for f in r["files"] if len(used_by[f]) <= 3}
        names = {os.path.basename(f) for f in distinct if len(os.path.basename(f)) >= 8}
        anchors = sorted(ids) + [s[:8] for s in r["shas"]] + sorted(names)
        hit = lambda t: [x for x in anchors if x in t]
        for e in evs:
            if not (lo < e["_t"] <= hi) or e.get("role_unit") == r["unit"] or e.get("event") in SKIP_EV \
                    or (e.get("why") or "") in MACHINE_WHY:
                continue
            txt = " ".join("%s=%s" % (k, str(e[k])[:600]) for k in ("event", "seat", "id", "kind", "title", "text", "why",
                                                                      "result", "reason") if e.get(k))
            if e.get("id") in ids or e.get("caused_by") in ids:
                looks.append(("ledger:%s:%s" % (e.get("event"), e.get("id")), e["_t"], txt, None))
            elif hit(json.dumps(e)):
                looks.append(("ledger:%s:%s" % (e.get("event"), e.get("id")), e["_t"], txt, hit(json.dumps(e))))
        for t, body in ents:
            if lo < t <= hi and not MACHINE_LOG.match(body) and hit(body):
                looks.append(("log", t, body, hit(body)))
        for o in runs:
            if o["unit"] != r["unit"] and lo < o["ended"] <= hi:
                if o["item"] in ids:
                    looks.append(("run(same item):%s" % o["item"], o["ended"], o["text"], hit(o["text"]) or None))
                elif hit(o["text"]):
                    looks.append(("run:%s" % o["item"], o["ended"], o["text"], hit(o["text"])))
        for h, ct, msg, fnames in commits:
            if lo < ct <= hi and h[:10] not in r["shas"]:
                touched = distinct & fnames
                if touched or hit(msg):
                    looks.append(("commit:%s" % h[:10], ct, msg + " [files: %s]" % ", ".join(sorted(touched)),
                                  None if touched else hit(msg)))
        r["n_looks"] = len(looks)
        r["look_kinds"] = sorted({k.split(":")[0] for k, _, _, _ in looks})
        r["cands"] = []
        seen = set()
        for i, (kind, t, txt, anch) in enumerate(looks):
            if anch:      # a fault word must sit within 400 characters of where the later text names this run's work
                ms = [m for m in FAULT.finditer(txt)
                      if any(abs(m.start() - j.start()) <= 400 for x in anch for j in re.finditer(re.escape(x), txt))]
            else:
                ms = list(FAULT.finditer(txt))
            if not ms or (kind, txt[:300]) in seen:
                continue
            seen.add((kind, txt[:300]))
            cid = "%s#%d" % (r["unit"][-10:], i)
            r["cands"].append(cid)
            show = " … ".join(snip(txt, m, 220) for m in ms[:3])
            cands.append("%s | item %s | landed %s | via %s, %.1f h later | anchors %s\n  %s\n" % (
                cid, iid, ",".join(r["shas"]) or "-", kind, (t - lo) / 3600, ",".join(anch or ["same item"]),
                show[:1100]))
    if verd is None:
        random.Random(7).shuffle(cands)
        open(os.path.join(outd, "candidates.txt"), "w").write("\n".join(cands))
        json.dump([{k: v for k, v in r.items() if k != "text"} for r in runs], open(os.path.join(outd, "runs.json"), "w"),
                  indent=1)
        print("VERDICT measured: %d runs, %d fault-word candidates in %s/candidates.txt (judge them blind)"
              % (len(runs), len(cands), outd))
        return 0
    missing = [c for r in runs for c in r["cands"] if c not in verd]
    if missing:
        print("VERDICT could-not-look: %d candidates have no verdict (first: %s)" % (len(missing), missing[0]))
        return 3
    cell = {}
    for r in runs:
        r["outcome"] = ("FAULT" if any(verd[c] is True or (verd[c] == "unclear" and "--unclear-as-fault" in a)
                                        for c in r["cands"]) else "LOOKED_CLEAN") if r["n_looks"] else "NOT_LOOKED"
        for markname, flagged in (("any", bool(r["marks"])),
                                  ("strict", bool(set(r["marks"]) - {"DOUBT"}))):
            for sub in ("all", "closed"):
                if sub == "closed" and not r["close_sha"]:
                    continue
                k = (markname, sub, flagged, r["outcome"])
                c = cell.setdefault(k, [0, 0])
                c[0] += 1
                c[1] += r["tokens"] or 0
    json.dump([{k: v for k, v in r.items() if k != "text"} for r in runs], open(os.path.join(outd, "runs_final.json"),
              "w"), indent=1)
    for markname in ("any", "strict"):
        for sub in ("all", "closed"):
            print("mark=%s population=%s" % (markname, sub))
            for flagged in (True, False):
                row = [cell.get((markname, sub, flagged, o), [0, 0]) for o in ("FAULT", "LOOKED_CLEAN", "NOT_LOOKED")]
                looked = row[0][0] + row[1][0]
                print("  %-9s fault %3d  looked-clean %3d  not-looked %3d   fault rate among looked: %s   tokens %s"
                      % ("flagged" if flagged else "unflagged", row[0][0], row[1][0], row[2][0],
                         "%d/%d = %.0f%%" % (row[0][0], looked, 100 * row[0][0] / looked) if looked else "n/a",
                         "/".join("%.1fM" % (x[1] / 1e6) for x in row)))
    print("VERDICT measured: %d runs joined with %d hand verdicts" % (len(runs), len(verd)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
