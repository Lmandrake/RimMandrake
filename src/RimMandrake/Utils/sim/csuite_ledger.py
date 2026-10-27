#!/usr/bin/env python3
"""csuite_ledger: measure the rimflow ledger for the C-suite evidence pass.

Reads the sharded ledger (infrastructure/state/ledger/events/*.jsonl plus the legacy ledger/events.jsonl) read-only and prints:
  kinds      item kinds filed
  flow       FlowWorks + GSS items (lane patterns from flowworks_lane.json): weekly filed/closed,
             bug share, repeat clusters (same id stem, or title-token overlap >= 0.5)
  rework     verify results by week; items verified fail; files caused_by an already-closed item;
             titles that say again/still/regress/redo
  flap       supersede / drop / retarget / reassign by week and by id prefix
  open       items neither closed, dropped nor superseded: age buckets, oldest per seat and target
Usage: csuite_ledger.py [section ...]   (default all). Env RM_LEDGER overrides the events dir.
"""
import collections, datetime as dt, glob, json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__)).split("/src/RimMandrake/")[0]
EV = os.environ.get("RM_LEDGER", os.path.join(ROOT, "infrastructure/state/ledger/events"))
LANE = os.path.join(ROOT, "infrastructure/state/flowworks_lane.json")


def load():
    out = []
    legacy = os.path.join(os.path.dirname(EV), "events.jsonl")  # pre-shard ledger, still read by rimflow
    for f in sorted(glob.glob(os.path.join(EV, "*.jsonl"))) + ([legacy] if os.path.exists(legacy) else []):
        for line in open(f, encoding="utf-8"):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("ts"):
                out.append(e)
    out.sort(key=lambda e: e["ts"])
    return out


def week(ts):
    d = dt.date.fromisoformat(ts[:10])
    return (d - dt.timedelta(days=d.weekday())).isoformat()


def stem(i):
    return re.sub(r"(_\d+)+$", "", i or "")


def toks(t):
    return {w for w in re.findall(r"[a-z]{4,}", (t or "").lower())}


def main(argv):
    want = set(argv) or {"kinds", "flow", "rework", "flap", "open"}
    evs = load()
    lane = json.load(open(LANE))["id_patterns"] + ["GIMME", "SLACK"]
    is_fw = lambda i: any(re.search(p, i or "") for p in lane)
    filed, closed, ended = {}, {}, {}
    for e in evs:
        i, k = e.get("id"), e.get("event")
        if k == "file" and i not in filed:
            filed[i] = e
        elif k == "close":
            closed.setdefault(i, e)
            ended.setdefault(i, e)
        elif k in ("drop", "supersede"):
            ended.setdefault(i, e)
    now = dt.datetime.now(dt.timezone.utc)
    print("ledger events", len(evs), "items filed", len(filed), "span", evs[0]["ts"][:10], "..", evs[-1]["ts"][:10])

    if "kinds" in want:
        print("\n## kinds", collections.Counter(e.get("kind") for e in filed.values()).most_common())
        print("needs owner at file:", sum(1 for e in filed.values() if e.get("needs") == "owner"))

    if "flow" in want:
        fw = {i: e for i, e in filed.items() if is_fw(i)}
        print("\n## flow: FlowWorks+GSS items", len(fw))
        wk = collections.defaultdict(collections.Counter)
        for i, e in fw.items():
            wk[week(e["ts"])]["filed"] += 1
            if e.get("kind") in ("bug", "finding"):
                wk[week(e["ts"])]["bugs"] += 1
        for i, e in closed.items():
            if i in fw:
                wk[week(e["ts"])]["closed"] += 1
        print("week       filed bugs closed")
        for w in sorted(wk):
            c = wk[w]
            print(f"{w} {c['filed']:5d} {c['bugs']:4d} {c['closed']:6d}")
        stems = collections.Counter(stem(i) for i in fw)
        rep = {s: n for s, n in stems.items() if n > 1}
        print("id stems filed more than once:", len(rep), "items in them", sum(rep.values()))
        for s, n in sorted(rep.items(), key=lambda x: -x[1])[:10]:
            print("  ", n, s)
        bugs = [(i, toks(e.get("title"))) for i, e in fw.items() if e.get("kind") in ("bug", "finding")]
        pairs = []
        for a in range(len(bugs)):
            for b in range(a + 1, len(bugs)):
                x, y = bugs[a][1], bugs[b][1]
                if x and y and len(x & y) / len(x | y) >= 0.5:
                    pairs.append((bugs[a][0], bugs[b][0]))
        inpair = {p for pr in pairs for p in pr}
        print("FW bugs", len(bugs), "near-duplicate title pairs (jaccard>=0.5)", len(pairs), "bugs involved", len(inpair))
        for p in pairs[:8]:
            print("  ", p)
        opn = [i for i in fw if i not in ended]
        print("FW open now", len(opn))

    if "rework" in want:
        print("\n## rework")
        vr = collections.defaultdict(collections.Counter)
        vfail = set()
        for e in evs:
            if e.get("event") == "verify":
                vr[week(e["ts"])][e.get("result")] += 1
                if e.get("result") not in ("pass", None):
                    vfail.add(e.get("id"))
        for w in sorted(vr):
            print(" verify", w, dict(vr[w]))
        print("items with a non-pass verify:", len(vfail))
        cb_closed = 0
        cb = 0
        for i, e in filed.items():
            p = e.get("caused_by")
            if p:
                cb += 1
                if p in closed and closed[p]["ts"] < e["ts"]:
                    cb_closed += 1
        print("files with caused_by", cb, "of which parent already closed (follow-up/rework after close)", cb_closed)
        rw = re.compile(r"\b(again|still|regress\w*|redo|re-?fix|reopen\w*|broke|broken again|not fixed|didn'?t take)\b", re.I)
        rwi = [i for i, e in filed.items() if rw.search(e.get("title") or "")]
        print("titles saying again/still/regress/redo/broke:", len(rwi), "of", len(filed))
        wk = collections.Counter(week(filed[i]["ts"]) for i in rwi)
        print("  by week", sorted(wk.items()))

    if "flap" in want:
        print("\n## flap")
        wk = collections.defaultdict(collections.Counter)
        pre = collections.Counter()
        for e in evs:
            k = e.get("event")
            if k in ("supersede", "drop", "retarget", "reassign"):
                wk[week(e["ts"])][k] += 1
                if k in ("supersede", "drop", "retarget"):
                    pre[(e.get("id") or "").split("_")[0]] += 1
        for w in sorted(wk):
            print(" ", w, dict(wk[w]))
        print(" top prefixes:", pre.most_common(12))
        stems = collections.Counter(stem(i) for i in filed)
        print(" item stems filed >=3 times (ledger-wide):", sum(1 for n in stems.values() if n >= 3))

    if "open" in want:
        print("\n## open")
        opn = {i: e for i, e in filed.items() if i not in ended}
        age = lambda e: (now - dt.datetime.fromisoformat(e["ts"].replace("Z", "+00:00"))).days
        b = collections.Counter()
        for e in opn.values():
            a = age(e)
            b["<7d" if a < 7 else "7-14d" if a < 14 else "14-21d" if a < 21 else ">=21d"] += 1
        print("open", len(opn), dict(b))
        started = {e.get("id") for e in evs if e.get("event") in ("start", "claim", "implemented")}
        ns = [i for i in opn if i not in started]
        print("open and never claimed/started/implemented:", len(ns))
        print("open by seat:", collections.Counter(e.get("for") for e in opn.values()).most_common())
        print("open by target:", collections.Counter(e.get("target") for e in opn.values()).most_common())
        print("open needing owner:", sum(1 for i, e in opn.items() if e.get("needs") == "owner"))
        bys = collections.defaultdict(list)
        for i, e in opn.items():
            bys[e.get("for")].append((e["ts"][:10], i))
        for s, l in bys.items():
            l.sort()
            print(" oldest", s, l[:3])
        pref = collections.Counter(i.split("_")[0] for i in ns)
        print(" never-started by prefix:", pref.most_common(15))


if __name__ == "__main__":
    main(sys.argv[1:])
