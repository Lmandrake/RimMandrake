#!/usr/bin/env python3
"""window.py: the agent-work census over any window of days, from the transcripts, in one command. No model, no tokens.

Item RIMMANDRAKE_FILL_COMMANDS_INTO_BRIEFS_HELP_ASKED_2807_TIMES, second part. The contract is the head of
../acceptance/census_window_accept.py. The scan is scan3.py's; the counting rules are those of p3.py, p5.py, p6.py, cond.py,
pure.py and pure2.py, moved here as they were (a rule's home is named beside it). `cache_rebuilt_after_gap` is the rule of
the table on RIMMANDRAKE_LENGTHEN_WAITS_UNDER_ONE_HOUR_CACHE_DIES_AFTER.

    python3 census/window.py --end <ISO time> [--days 7] --out DIR [--projects DIR]

It writes DIR/rates.json. Exit 0: value or empty; 2: could not look, or a refused --out.
"""
import argparse
import datetime
import json
import os
import re
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))

KEYS = ("help", "help_ledger_verbs", "show", "raw_ledger", "wait", "wait_repeat", "fetch_result", "report_after_fetch",
        "wake_reading", "state_reads", "progress_note", "lease_renew", "wrong_flag", "pure_landing", "publish_refused",
        "one_test", "red_green", "cache_rebuilt_after_gap")
FMT = "%Y-%m-%dT%H:%M:%S"


# ---- the scan (scan3.py) --------------------------------------------------------------------------------------------
def weights():
    """-> {model: {field: weight}}: role_launch.MODEL_PRICES over the price of one uncached reference input token."""
    import role_launch as rl
    ref = rl.MODEL_PRICES[rl.REF_MODEL]["input_tokens"]
    return {m: {k: float(v / ref) for k, v in p.items()} for m, p in rl.MODEL_PRICES.items()}


def cost(w, model, u):
    """-> weighted tokens of one turn, None when the model has no price."""
    m = w.get(model) or w.get(re.sub(r"\[.*\]", "", model or ""))
    if not m:
        return None
    cc = u.get("cache_creation") or {}
    w5 = cc.get("ephemeral_5m_input_tokens", 0) or 0
    w1 = cc.get("ephemeral_1h_input_tokens", 0) or 0
    tot = u.get("cache_creation_input_tokens", 0) or 0
    if w5 + w1 != tot:
        w5, w1 = 0, tot
    return ((u.get("input_tokens") or 0) * m["input_tokens"] + w5 * m["cache_write_5m"] + w1 * m["cache_write_1h"]
            + (u.get("cache_read_input_tokens") or 0) * m["cache_read_input_tokens"]
            + (u.get("output_tokens") or 0) * m["output_tokens"])


def _text_of(content):
    if isinstance(content, str):
        return content
    return " ".join(y.get("text", "") for y in (content or []) if isinstance(y, dict))


def scan(job):
    """(path, its project folder, window start, window end) -> one transcript's turns in the window, torn lines counted;
    {"unread": why} when the file could not be read."""
    p, k, start, end = job
    w = weights()
    msgs, order, results, unk, torn, first = {}, [], {}, set(), 0, None
    try:
        with open(p, errors="replace") as fh:
            lines = fh.readlines()
    except OSError as e:
        return {"p": p, "unread": "%s: %s" % (type(e).__name__, e)}
    for line in lines:
        if not line.strip() or ('"assistant"' not in line and first is not None and '"tool_result"' not in line):
            continue
        try:
            d = json.loads(line)
            t = d.get("type")
            m = d.get("message") or {}
        except (ValueError, AttributeError):
            torn += 1
            continue
        if t == "user":
            c = m.get("content")
            if first is None and c:
                first = True
            for x in c if isinstance(c, list) else ():
                if isinstance(x, dict) and x.get("type") == "tool_result":
                    tx = _text_of(x.get("content"))
                    results[x.get("tool_use_id")] = tx if len(tx) < 900 else tx[:450] + " ... " + tx[-450:]
        elif t == "assistant":
            ts = d.get("timestamp") or ""
            if not start <= ts < end:
                continue
            i, u = m.get("id"), m.get("usage") or {}
            if i not in msgs:
                msgs[i] = {"model": m.get("model"), "u": u, "tools": [], "text": "", "ts": ts}
                order.append(i)
            r = msgs[i]
            if (u.get("output_tokens") or 0) >= (r["u"].get("output_tokens") or 0):
                r["u"] = u
            for x in m.get("content") or []:
                if not isinstance(x, dict):
                    continue
                if x.get("type") == "tool_use":
                    inp = x.get("input") or {}
                    r["tools"].append((x.get("name"), inp.get("command") or inp.get("file_path") or inp.get("skill")
                                       or inp.get("description") or "", x.get("id")))
                elif x.get("type") == "text":
                    r["text"] += x.get("text", "")[:300]
    turns = []
    for i in order:
        r = msgs[i]
        if r["model"] in (None, "<synthetic>"):
            continue
        c = cost(w, r["model"], r["u"])
        if c is None:
            unk.add(r["model"])
            continue
        u = r["u"]
        turns.append((c, r["model"], [(n, str(cmd)[:6000], 0, 0, results.get(tid, "")) for n, cmd, tid in r["tools"]],
                      r["text"][:300], r["ts"], u.get("output_tokens") or 0, u.get("cache_creation_input_tokens") or 0,
                      u.get("cache_read_input_tokens") or 0))
    return {"p": p, "k": k, "turns": turns, "unk": sorted(unk), "torn": torn}


# ---- the rules ------------------------------------------------------------------------------------------------------
FRM = re.compile(r"(grep|cat|tail|head|jq|awk)\b[^|;&\n]*ledger/events|glob\([^)]*ledger/events")     # p6.py
SEG = re.compile(r"(?:;|&&|\|\||\n)")                                                                # pure2.py
RD = {"show", "queue", "next", "status", "incidents", "namecheck"}                                   # pure2.py


def pure_ll(c):     # pure2.py
    c = re.sub(r'--(text|why|evidence|reason|title|spec|criteria|verify|owner-said|m)\s+("([^"\\]|\\.)*"|\'[^\']*\'|"\$\(cat <<.*)',
               '', c, flags=re.S)
    c = re.sub(r'-m\s+("([^"\\]|\\.)*"|\'[^\']*\')', '', c, flags=re.S)
    hit = False
    for s in SEG.split(c):
        s = re.sub(r'\|.*', '', s).strip()
        if not s:
            continue
        if re.match(r'(timeout \d+ )?(python3 \S*cli\.py|rimflow|\./publish|\./sync|git (add|commit|pull|push|fetch|merge-base|status|log -1|rev-parse)|\./mirror)', s):
            hit = True
            continue
        if re.match(r'(cd |echo|date|set -o|set -e|rc=|[A-Z_a-z]+=|true$|tail|head|grep|cat /tmp|\#|done$|fi$|then|printf|export |sleep \d$|wc )', s):
            continue
        return False
    return hit


def verbs(c):       # pure2.py
    v = set(m.group(1) for m in re.finditer(r'(?:cli\.py"?|rimflow) (\w+)', c))
    if './publish' in c:
        v.add('publish')
    if re.search(r'\./sync|git (pull|fetch)', c):
        v.add('sync')
    if re.search(r'git (add|commit)', c):
        v.add('commit')
    return v


def _epoch(ts):
    return datetime.datetime.strptime(ts[:19], FMT).replace(tzinfo=datetime.timezone.utc).timestamp()


def conductor(T, add):
    """cond.py, over a Conductor window's turns with the repeated ones taken out (it read scan2.pkl: 1,500 characters of a
    command). The branches stand in its order: a turn is one thing."""
    for i, t in enumerate(T):
        cmds = ' ;; '.join((q or '')[:1500] for _, q, *_ in t[2])
        if i and re.search(r'detached/|\.out\.json', cmds) and re.search('python3 -c|jq|cat', cmds):
            add("fetch_result", t[0])
            if i + 1 < len(T) and not T[i + 1][2]:
                add("report_after_fetch", T[i + 1][0])
        elif i and re.search('seat_restart|handoff|queue CONDUCTOR|owed', cmds):
            add("wake_reading", t[0])
        elif i and re.search(r'\./pipe (show|why|log)|game_lock.*query|detached_helper\.py status|account_usage|switching_plan|MATURATION_NOW', cmds):
            add("state_reads", t[0])


def count(S):
    """[scan()'s rows] -> ({KEY: [turns, weighted]}, weighted tokens of the window). A turn that a resumed session repeats
    is counted once, over the whole window."""
    A = {k: [0, 0.0] for k in KEYS}
    seen, total = set(), 0.0

    def add(key, c):
        A[key][0] += 1
        A[key][1] += c

    for x in S:
        T = []      # (index in the transcript's window, turn), repeats out
        for i, t in enumerate(x["turns"]):
            key = (t[4], round(t[0], 3))
            if key in seen:
                continue
            seen.add(key)
            T.append((i, t))
        total += sum(t[0] for _, t in T)
        sub = "/subagents/" in x["p"]
        if "rm-bench" in x["k"] and not x["k"].endswith("-det") and not sub:
            conductor([t for _, t in T], add)
        prev_wait, before = False, None
        for j, (i, t) in enumerate(T):
            if x["k"].endswith("-det") and not sub:
                if before and _epoch(t[4]) - _epoch(before) >= 660 and t[6] > t[7] and t[6] > 20000:
                    add("cache_rebuilt_after_gap", t[0])
                before = t[4]
            if i == 0 or not t[2]:
                prev_wait = False
                continue
            cm = ' ;; '.join(c or '' for _, c, *_ in t[2])
            hd = ' '.join(h or '' for *_, h in t[2])
            # p6.py
            if FRM.search(cm) and './publish' not in cm:
                add("raw_ledger", t[0])
            if re.search(r'(cli\.py"?|rimflow) show ', cm) and './publish' not in cm:
                add("show", t[0])
            if re.search(r'(cli\.py"?|rimflow) note ', cm) and re.search(r'PROGRESS|STATE', cm) and './publish' not in cm:
                add("progress_note", t[0])
            if re.search(r'lease\.renew', cm):
                add("lease_renew", t[0])
            if re.search(r'--help\b', cm):
                add("help", t[0])
                if re.search(r'(cli\.py|rimflow) (file|close|note|verify|drop|supersede|wait|spawn)|maturation\.py|red-seen|detached_helper|lessons|publish', cm):
                    add("help_ledger_verbs", t[0])
            # p3.py
            w = bool(re.search(r'waitfor\.py (job|line|unit|pid|file)|\bsleep \d\d|until .{0,120}sleep|while .{0,160}sleep|/tasks/', cm)) and not re.search(r'write\(|<<', cm)
            if w:
                add("wait", t[0])
                if prev_wait:
                    add("wait_repeat", t[0])
            prev_wait = w
            # p5.py and pure.py (one rule): the cost runs from the refusal to the next PUBLISHED, at most 7 turns
            if './publish' in cm and 'PUBLISHED' not in hd and re.search(r'REFUSED|usage: publish|failed to push|Blocked by project|pathspec', hd):
                c = t[0]
                for q in range(j + 1, min(j + 8, len(T))):
                    tt = T[q][1]
                    c += tt[0]
                    if 'PUBLISHED' in ' '.join(h or '' for *_, h in tt[2]):
                        break
                add("publish_refused", c)
            # p5.py
            if re.search(r'python3? [^\n;|&]*(selftest_|run_selftests)', cm):
                if len(set(re.findall(r'(selftest_\w+)', cm))) == 1 and not re.search(r'write\(|<<|publish', cm):
                    add("one_test", t[0])
            # pure.py
            if re.search(r'python3? [^\n;|&]*selftest_', cm) and re.search(
                    r'\bplant|git apply|\.patch|mutant|git show [^ ]*:|worktree|parent', cm):
                add("red_green", t[0])
            if re.search(r'usage: |unrecognized arguments|are required: |invalid choice', hd) and '--help' not in cm:
                add("wrong_flag", t[0])
            # pure2.py
            cs = [c for nm, c, *_ in t[2] if nm == 'Bash']
            v = set().union(*[verbs(c or '') for c in cs]) if cs else set()
            if len(cs) == len(t[2]) and all(pure_ll(c or '') for c in cs) and v and not v <= RD | {'sync'}:
                add("pure_landing", t[0])
    return A, total


# ---- the command ----------------------------------------------------------------------------------------------------
def reading(projects, start, end):
    """-> the reading (without its window): status, why, runs, weighted, torn_lines, unpriced_models, counts."""
    r = {"status": "could_not_look", "why": "", "runs": None, "weighted": None, "torn_lines": None, "unpriced_models": [],
         "unread_files": [], "counts": None}
    if not os.path.isdir(projects):
        return dict(r, why="could not look: no projects folder %s" % projects)
    jobs, floor = [], _epoch(start)
    walk_errors = []
    for d, _, files in os.walk(projects, onerror=walk_errors.append):
        k = os.path.relpath(d, projects).split(os.sep)[0]
        for f in files:
            q = os.path.join(d, f)
            try:
                if f.endswith(".jsonl") and os.path.getmtime(q) >= floor:
                    jobs.append((q, k, start, end))
            except OSError as e:
                walk_errors.append(e)
    jobs.sort()
    if len(jobs) > 8:
        with Pool(8) as pool:
            rows = pool.map(scan, jobs, chunksize=4)
    else:
        rows = [scan(j) for j in jobs]
    r["unread_files"] = [x["p"] for x in rows if "unread" in x] + [str(e) for e in walk_errors]
    rows = [x for x in rows if "unread" not in x]
    r["torn_lines"] = sum(x["torn"] for x in rows)
    r["unpriced_models"] = sorted({m for x in rows for m in x["unk"]})
    S = [x for x in rows if x["turns"]]
    if not S and (r["unpriced_models"] or r["unread_files"]):
        return dict(r, why="could not look: no priced turn; models with no price: %s; files not read: %d"
                    % (", ".join(r["unpriced_models"]) or "none", len(r["unread_files"])))
    A, total = count(S)
    n = len(S)
    r.update(status="value" if S else "empty", why="" if S else "no turn in the window", runs=n, weighted=round(total),
             counts={k: {"turns": a, "weighted": round(b), "per_100_runs": round(100.0 * a / n, 1) if n else None,
                         "weighted_per_100_runs": round(100.0 * b / n) if n else None} for k, (a, b) in A.items()})
    return r


def out_refusal(out, window):
    """-> why DIR may not be written, None when it may: a census pickle, or another window's reading, is never lost."""
    if not os.path.exists(out):
        return None
    if not os.path.isdir(out):
        return "%s is not a folder" % out
    pk = [f for f in sorted(os.listdir(out)) if f.endswith(".pkl")]
    if pk:
        return "%s holds a census's data (%s); name a new folder" % (out, pk[0])
    p = os.path.join(out, "rates.json")
    if os.path.exists(p):
        try:
            with open(p, encoding="utf-8") as f:
                old = json.load(f).get("window")
        except (OSError, ValueError, AttributeError) as e:
            return "%s cannot be read (%s); name a new folder" % (p, type(e).__name__)
        if old != window:
            return "%s is the reading of another window (%s); name a new folder" % (p, old)
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--end", required=True, help="the end of the window, an ISO time with its zone")
    ap.add_argument("--days", type=float, default=7.0)
    ap.add_argument("--out", required=True, help="a folder for rates.json, not one that holds another reading")
    ap.add_argument("--projects", default=os.path.expanduser("~/.claude/projects"))
    a = ap.parse_args(argv)
    try:
        end = datetime.datetime.fromisoformat(a.end.replace("Z", "+00:00"))
    except ValueError as e:
        ap.error("--end: %s" % e)
    if end.tzinfo is None:
        ap.error("--end names no zone: write 2026-11-23T19:56:44-08:00")
    end = end.astimezone(datetime.timezone.utc)
    window = {"start": (end - datetime.timedelta(days=a.days)).strftime(FMT) + "Z", "end": end.strftime(FMT) + "Z"}
    why = out_refusal(a.out, window)
    if why:
        print("REFUSED --out: " + why, file=sys.stderr)
        return 2
    r = dict({"window": window}, **reading(a.projects, window["start"][:-1], window["end"][:-1]))
    os.makedirs(a.out, exist_ok=True)
    p = os.path.join(a.out, "rates.json")
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump(r, f, indent=1)
    os.replace(p + ".tmp", p)
    if r["status"] == "could_not_look":
        print("COULD NOT LOOK (%s): %s" % (p, r["why"]), file=sys.stderr)
        return 2
    print("%s %s: %d runs, %.1fM weighted, %d torn lines, unpriced: %s, files not read: %d" % (
        r["status"].upper(), p, r["runs"], r["weighted"] / 1e6, r["torn_lines"], ", ".join(r["unpriced_models"]) or "none",
        len(r["unread_files"])))
    for k in KEYS:
        c = r["counts"][k]
        print("  %-24s %6d turns %8.1fM  %s per 100 runs" % (k, c["turns"], c["weighted"] / 1e6, c["per_100_runs"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
