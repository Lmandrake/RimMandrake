#!/usr/bin/env python3
"""Testing census (TESTING_BENCHMARK_MONTE_CARLO): MEASURE where defects come from and what tests cost, from the
ledger, git, the testq job store, the nightly selftest log and today's GPT review files. Writes one JSON that
testing_investment_sim.py reads as its MEASURED inputs. Read-only on every source.

Classifiers here are keyword heuristics (an item's id/title/why text, plus the paths its close commit touched).
Every aggregate carries its `unknown` share so a reader can see how much the classifier could not place; the
selftest probes each classifier on hand-written rows so a blind regex cannot pass as a measurement.

usage: testing_census.py [--repo R] [--days 30] [--out PATH]
"""
import argparse
import collections
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TESTQ_DEFAULT = os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq")
REVIEWS_DEFAULT = "/mnt/d/ClaudeWork/rimmandrake/reviews"
OUT_DEFAULT = "/mnt/d/ClaudeWork/rimmandrake/testing_sim/census.json"

INTENT_BANK = set((
    "ABSORB ASK AUDIT BALANCE BENCHMARK BISECT BUILD CENSUS CHASE CODE CORRECT CULL DEBUG DECIDE DEDUPE DELETE "
    "DEPLOY DESIGN DIAGNOSE DOCUMENT DRAIN ENFORCE EXCISE EXPLAIN FILL FINISH FIX HARDEN HARVEST HUNT INSTALL "
    "JUDGE MEASURE MEND MERGE MIGRATE MONITOR POLISH POPULATE PROBE PROVE PRUNE REBUILD RECONCILE REDESIGN REDRAW "
    "REMEASURE RENAME REPAIR RESCUE RESKIN RESTORE RETHINK RETIRE RETRY REVIVE REWIRE SALVAGE SHRINK SILENCE "
    "SKETCH SYNC TAME TUNE UNBLOCK UNIFY UNSTICK UNTANGLE VERIFY VET WIDEN WIRE").split())
DEFECT_INTENTS = {"FIX", "REPAIR", "MEND", "CORRECT", "DEBUG", "DIAGNOSE", "RESCUE", "RESTORE", "UNSTICK",
                  "SALVAGE", "REVIVE", "UNTANGLE"}
DEFECT_KINDS = {"bug", "defect", "fix", "finding"}

# code kinds ------------------------------------------------------------------------------------------------
CODE_KINDS = ("csharp", "xml", "python_tooling", "machinery", "art", "mod_unspecified", "unknown")
MACHINERY_WORDS = ("RIMFLOW", "TESTQ", "DISPATCH", "ARBITER", "LEDGER", "MODCHECK", "HOOK",
                   "SELFTEST", "DIGEST", "RUNNER", "STEWARD", "HANDOFF", "SEAT", "LEASE", "NORTHSTAR",
                   "PROOF_ALL", "VALIDATION", "HARNESS", "CLOSE_EVIDENCE", "ROLES", "QUEUE")
TOOLING_WORDS = ("DEPLOY", "WINBUILD", "ARTPIPE", "ART_SHEET", "SHEET", "SAVEMAP", "DEFDUMP", "REFRESH",
                 "MODLIST", "BRIDGE", "COMPANION", "JAWABENCH", "SCRIPT", "LINT", "PLANNER", "TOOL")
CS_WORDS = ("HARMONY", "TRANSPILER", "DLL", "NRE", "C#", "POSTFIX", "PREFIX", "TICK", "COMP", "JOBDRIVER",
            "MAPCOMPONENT", "EXCEPTION", "NULLREF", "SPIKE", "PERF")
XML_WORDS = ("XML", "XPATH", "DEF", "PATCH", "PARENTNAME", "LABEL", "STATBASES", "RECIPE", "BIOME", "TEXPATH",
             "DESCRIPTION", "KEYED", "TRANSLATION")
ART_WORDS = ("ART", "SPRITE", "TEXTURE", "REDRAW", "RESKIN", "ICON", "PNG", "RENDER")


def path_kind(p):
    """Code kind of one repo path."""
    if p.startswith(("infrastructure/state/", "conversations/", "Transient/")):
        return None
    if p.endswith((".png", ".psd", ".dds")):
        return "art"
    if p.endswith(".cs") or "/Assemblies/" in p:
        return "csharp"
    if p.endswith(".xml") and ("/Defs/" in p or "/Patches/" in p or "/Languages/" in p or p.endswith("About.xml")):
        return "xml"
    if p.endswith(".py") or p.startswith(".claude/hooks"):
        low = p.lower()
        if ("/rimflow/" in low or "/modcheck/" in low or "/testq/" in low or "northstar" in low or
                "close_evidence" in low or "arbiter" in low or "dispatch" in low or low.startswith(".claude/")):
            return "machinery"
        return "python_tooling"
    return None


def text_kind(text, mods=()):
    """Code kind from an item's words when its commit says nothing (fallback; noisier)."""
    up = text.upper()
    scores = collections.Counter()
    for w in MACHINERY_WORDS:
        if re.search(r"\b" + re.escape(w), up):
            scores["machinery"] += 2
    for w in TOOLING_WORDS:
        if re.search(r"\b" + re.escape(w), up):
            scores["python_tooling"] += 1
    for w in CS_WORDS:
        if re.search(r"\b" + re.escape(w), up):
            scores["csharp"] += 1
    for w in XML_WORDS:
        if re.search(r"\b" + re.escape(w), up):
            scores["xml"] += 1
    for w in ART_WORDS:
        if re.search(r"\b" + re.escape(w) + r"\b", up):
            scores["art"] += 1
    if not scores:
        return "mod_unspecified" if mods and any(m in up for m in mods) else "unknown"
    return scores.most_common(1)[0][0]


# detection channel -----------------------------------------------------------------------------------------
CHANNELS = ("owner", "review", "live", "testq", "offline", "unknown")


def channel_of(text):
    """Which stage found the defect, from the filing text. Order = most specific first."""
    t = text.lower()
    if re.search(r"\bowner\b.*\b(found|saw|said|review|report|noticed|walk)|owner review|owner-found|"
                 r"\bhe (saw|found|noticed)|owner_review", t):
        return "owner"
    if re.search(r"\b(gpt|codex|re-review|review wave|reviewer|code review|code_review|review r\d|w\d+ "
                 r"re-review|review)\b", t):
        return "review"
    if re.search(r"testq|stevedesktop|steve-targeted|\bsteve\b|filler|run-\d+@", t):
        return "testq"
    if re.search(r"\blive\b|player\.log|bridge|in[- ]game|sitting|quicktest|cold load|\br\d{1,2}\b|on the map", t):
        return "live"
    if re.search(r"selftest|offline|modcheck|validate_patch|lint|static|nightly|def dump|winbuild|compile", t):
        return "offline"
    return "unknown"


def intent_of(item_id):
    toks = item_id.split("_")
    return next((t for t in toks[1:] if t in INTENT_BANK), None)


def is_defect(file_ev):
    return (file_ev.get("kind") in DEFECT_KINDS) or (intent_of(file_ev["id"]) in DEFECT_INTENTS)


def parse_ts(s):
    return dt.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")


# sources ---------------------------------------------------------------------------------------------------
def load_ledger(repo):
    evs = []
    for f in sorted(glob.glob(os.path.join(repo, "infrastructure/state/ledger/events/*.jsonl"))):
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    evs.append(json.loads(line))
    return evs


def commit_paths(repo, shas):
    """sha -> list of paths, one git call per batch."""
    out = {}
    shas = [s for s in shas if re.fullmatch(r"[0-9a-f]{7,40}", s or "")]
    for i in range(0, len(shas), 200):
        batch = shas[i:i + 200]
        r = subprocess.run(["git", "-C", repo, "show", "--no-renames", "--name-only", "--format=@@%H"] + batch,
                           capture_output=True, text=True, timeout=300)
        cur = None
        for line in r.stdout.splitlines():
            if line.startswith("@@"):
                cur = line[2:]
                out[cur] = []
            elif line.strip() and cur:
                out[cur].append(line.strip())
    return out


def commits_by_item(repo, days, ids):
    """item id -> repo paths touched by every commit whose message names the id (one git log pass).
    The close sha alone is often a ledger or handoff commit; the message naming the id is the better join."""
    r = subprocess.run(["git", "-C", repo, "log", "--since=%d.days" % days, "--no-merges", "--no-renames",
                        "--name-only", "--format=@@%H%n%B%n@@END"], capture_output=True, text=True, timeout=500)
    out = collections.defaultdict(list)
    msg, in_msg, named = [], False, set()
    for line in r.stdout.splitlines():
        if line.startswith("@@") and not line.startswith("@@END"):
            in_msg, msg, named = True, [], set()
            continue
        if line == "@@END":
            in_msg = False
            named = set(re.findall(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b", " ".join(msg))) & ids
            continue
        if in_msg:
            msg.append(line)
        elif line.strip() and named:
            for i in named:
                out[i].append(line.strip())
    return out


def kind_from_paths(paths):
    """Where the defect lived: the most-touched kind, ties and near-ties broken toward shipped code
    (a C# fix usually drags its selftest .py and the DLL along; the .py is the test, not the defect)."""
    c = collections.Counter(k for k in (path_kind(p) for p in paths) if k)
    if not c:
        return None
    for k in ("csharp", "xml"):
        if c.get(k) and c[k] * 3 >= max(c.values()):
            return k
    return c.most_common(1)[0][0]


MOD_ALIASES = {"GSS": "GIMMESOMESLACK", "FW": "FLOWWORKS"}


def mod_names(repo):
    """Upper-cased mod folder names (src/<tier>/<Mod>) plus aliases; words of 4+ letters only."""
    names = set(MOD_ALIASES)
    for d in glob.glob(os.path.join(repo, "src", "*", "*")):
        b = os.path.basename(d)
        if os.path.isdir(d) and b not in ("Utils",) and len(b) >= 4:
            names.add(b.upper())
    return tuple(sorted(names))


def ledger_census(repo, days):
    evs = load_ledger(repo)
    ts_all = [parse_ts(e["ts"]) for e in evs if e.get("ts")]
    t_end = max(ts_all)
    t0 = t_end - dt.timedelta(days=days)
    files = {}
    for e in evs:
        if e["event"] == "file" and e["id"] not in files:
            files[e["id"]] = e
    closes = {}
    for e in evs:
        if e["event"] == "close" and e["id"] not in closes:
            closes[e["id"]] = e
    id_paths = commits_by_item(repo, days + 5, set(files))

    def paths_for(item_id):
        return id_paths.get(item_id, [])

    mods = mod_names(repo)
    rows = []
    for i, e in files.items():
        if parse_ts(e["ts"]) < t0 or not is_defect(e):
            continue
        text = " ".join(str(e.get(k, "")) for k in ("id", "title", "why"))
        kind = kind_from_paths(paths_for(i))
        kind_src = "commit"
        if not kind:
            kind, kind_src = text_kind(" ".join(str(e.get(k, "")) for k in ("id", "title")), mods), "text"
        cb = e.get("caused_by")
        escape = False
        if cb and cb in closes and parse_ts(closes[cb]["ts"]) <= parse_ts(e["ts"]):
            escape = True
        rows.append({"id": i, "kind": kind, "kind_src": kind_src, "channel": channel_of(text),
                     "escape": escape, "caused_by": cb, "ts": e["ts"], "closed": i in closes})
    agg = collections.Counter((r["kind"], r["channel"]) for r in rows)
    by_kind = collections.Counter(r["kind"] for r in rows)
    esc_kind = collections.Counter(r["kind"] for r in rows if r["escape"])
    by_chan = collections.Counter(r["channel"] for r in rows)
    n_items = sum(1 for e in files.values() if parse_ts(e["ts"]) >= t0)
    # verify / findings
    ver = collections.Counter()
    for e in evs:
        if e["event"] == "verify" and parse_ts(e["ts"]) >= t0:
            cfg = str(e.get("config", ""))
            lane = ("testq" if cfg.startswith("steve") else "offline" if "offline" in cfg else
                    "full_list" if cfg.startswith("full") or re.search(r"\b3\d\d ?mods|613", cfg) else "live_min")
            ver[(lane, e["result"])] += 1
    fnd = collections.Counter(e.get("type") for e in evs if e["event"] == "finding" and parse_ts(e["ts"]) >= t0)
    return {
        "window": [t0.isoformat() + "Z", t_end.isoformat() + "Z"], "items_filed": n_items,
        "defects": len(rows), "defects_by_kind": dict(by_kind), "escapes_by_kind": dict(esc_kind),
        "defects_by_channel": dict(by_chan),
        "kind_x_channel": {"%s|%s" % k: v for k, v in sorted(agg.items())},
        "kind_source": dict(collections.Counter(r["kind_src"] for r in rows)),
        "verify": {"%s|%s" % k: v for k, v in sorted(ver.items())},
        "findings_by_type": dict(fnd),
        "sample": rows[:: max(1, len(rows) // 40)][:40],
    }


def git_volume(repo, days):
    """Commits in window touching each code kind (normaliser for defect rates)."""
    r = subprocess.run(["git", "-C", repo, "log", "--since=%d.days" % days, "--no-merges", "--no-renames",
                        "--name-only", "--format=@@%H"], capture_output=True, text=True, timeout=500)
    per = collections.Counter()
    commits = 0
    cur = set()

    def flush():
        for k in cur:
            per[k] += 1
    for line in r.stdout.splitlines():
        if line.startswith("@@"):
            flush()
            cur = set()
            commits += 1
        elif line.strip():
            k = path_kind(line.strip())
            if k:
                cur.add(k)
    flush()
    return {"commits": commits, "commits_touching": dict(per)}


def testq_census(qhome):
    jobs = []
    for f in glob.glob(os.path.join(qhome, "done", "*.json")):
        try:
            with open(f, encoding="utf-8") as fh:
                jobs.append(json.load(fh))
        except (OSError, ValueError):
            continue
    lane = collections.Counter()
    phase = collections.defaultdict(list)
    verdicts = collections.Counter()
    purpose = collections.Counter()
    chain_runs = collections.Counter()
    chain_measured = collections.Counter()
    chain_fail = collections.Counter()
    fnd_type = collections.Counter()
    job_s = []
    jobs_with_fail = 0
    for j in jobs:
        job = j.get("job", {})
        res = j.get("result") or {}
        lane[job.get("lane")] += 1
        purpose["filler" if job.get("requested_by", "").endswith("filler") else job.get("purpose")] += 1
        ps = res.get("phase_s") or {}
        for k, v in ps.items():
            phase[k].append(v)
        if ps:
            job_s.append(sum(ps.values()))
        rows = res.get("rows") or []
        per_chain = collections.defaultdict(collections.Counter)
        for r in rows:
            verdicts[r.get("verdict")] += 1
            per_chain[r.get("chain") or "?"][r.get("verdict")] += 1
        if any(r.get("verdict") == "FAIL" for r in rows):
            jobs_with_fail += 1
        for ch, c in per_chain.items():
            chain_runs[ch] += 1
            if c.get("PASS", 0) + c.get("FAIL", 0) > 0:
                chain_measured[ch] += 1
            if c.get("FAIL", 0):
                chain_fail[ch] += 1
        for fd in (j.get("ingested") or {}).get("findings") or []:
            fnd_type[(fd.get("type") if isinstance(fd, dict) else "?")] += 1

    def q(v, p):
        v = sorted(v)
        return v[min(len(v) - 1, int(p * len(v)))] if v else None
    dry = sorted(ch for ch in chain_runs if chain_measured[ch] == 0)
    return {
        "jobs": len(jobs), "lanes": dict(lane), "purpose": dict(purpose),
        "job_s": {"n": len(job_s), "sum_h": round(sum(job_s) / 3600, 1), "p50": q(job_s, .5), "p90": q(job_s, .9)},
        "phase_s": {k: {"n": len(v), "p50": q(v, .5), "p90": q(v, .9), "sum_h": round(sum(v) / 3600, 2)}
                    for k, v in phase.items()},
        "row_verdicts": dict(verdicts), "jobs_with_fail": jobs_with_fail,
        "chains": len(chain_runs), "chains_never_measured": dry,
        "chains_ever_failed": sorted(chain_fail), "findings_by_type": dict(fnd_type),
    }


TOOL_DIRS = {"Utils", "rimflow", "bridgetools", "Tools", "tools"}


def selftest_kind(p):
    """Selftest path -> area. A test under src/<tier>/<Mod>/ tests that mod (its C#/XML behaviour, offline),
    so it is mod_selftest, not python_tooling; rimflow/hooks keep the machinery label."""
    parts = p.replace("\\", "/").split("/")
    if len(parts) >= 4 and parts[0] == "src" and parts[2] not in TOOL_DIRS:
        return "mod_selftest"
    return path_kind(p) or "other"


def selftest_census(repo):
    out = {}
    log = os.path.join(repo, "Transient", "selftests_nightly.log")
    runs = []
    if os.path.exists(log):
        date = None
        for line in open(log, encoding="utf-8", errors="replace"):
            m = re.match(r"=== (\S+) nightly", line)
            if m:
                date = m.group(1)
            m = re.match(r"PASS (\d+)/(\d+)\s+FAIL (\d+)/\d+\s+UNMEASURED (\d+)/\d+\s+CRASH (\d+)/\d+\s+"
                         r"SKIPPED (\d+)/\d+\s+\(wall ([\d.]+)s\)", line)
            if m:
                runs.append({"date": date, "n": int(m.group(2)), "fail": int(m.group(3)), "crash": int(m.group(5)),
                             "wall_s": float(m.group(7))})
    out["nightly"] = runs
    tf = os.path.join(os.environ.get("TMPDIR", "/tmp"), "selftest_timings.json")
    if not os.path.exists(tf):
        tf = "/home/mandrake/.seat-tmp/BENCH/selftest_timings.json"
    if os.path.exists(tf):
        d = json.load(open(tf))
        v = sorted(float(x) for x in d.values() if isinstance(x, (int, float)))
        by = collections.Counter()
        for p, s in d.items():
            if isinstance(s, (int, float)):
                by[selftest_kind(p)] += s
        out["timings"] = {"n": len(v), "cpu_s": round(sum(v)), "p50": v[len(v) // 2], "p90": v[int(.9 * len(v))],
                          "max": v[-1], "top10_share": round(sum(v[-10:]) / sum(v), 3),
                          "cpu_s_by_kind": {k: round(x) for k, x in by.items()}}
    return out


REVIEW_AREA = {"arbiter": "machinery", "digest": "machinery", "dispatcher": "machinery", "evidence": "machinery",
               "isolated": "machinery", "roles": "machinery", "flowworks": "csharp", "foodpoison": "csharp",
               "thirst": "csharp"}


def review_census(rdir):
    out = collections.Counter()
    high = collections.Counter()
    files = 0
    for f in sorted(glob.glob(os.path.join(rdir, "gpt_review_*.md"))):
        files += 1
        area = next((v for k, v in REVIEW_AREA.items() if k in os.path.basename(f)), "unknown")
        for line in open(f, encoding="utf-8", errors="replace"):
            if re.match(r"\s*(\*\*)?\d+[.)] ", line):
                out[area] += 1
                if re.search(r"HIGH|High|CRIT|P0|P1|BLOCK", line):
                    high[area] += 1
    return {"files": files, "findings_by_area": dict(out), "high_by_area": dict(high)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO_DEFAULT)
    ap.add_argument("--testq", default=TESTQ_DEFAULT)
    ap.add_argument("--reviews", default=REVIEWS_DEFAULT)
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--out", default=OUT_DEFAULT)
    a = ap.parse_args(argv)
    res = {"generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "days": a.days,
           "ledger": ledger_census(a.repo, a.days), "git": git_volume(a.repo, a.days),
           "testq": testq_census(a.testq), "selftests": selftest_census(a.repo),
           "reviews": review_census(a.reviews)}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    L = res["ledger"]
    print("wrote", a.out)
    print("defects", L["defects"], "of", L["items_filed"], "items; by kind", L["defects_by_kind"])
    print("channels", L["defects_by_channel"], "kind_source", L["kind_source"])
    print("testq jobs", res["testq"]["jobs"], "rows", res["testq"]["row_verdicts"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
