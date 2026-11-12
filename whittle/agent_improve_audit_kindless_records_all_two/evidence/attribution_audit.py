#!/usr/bin/env python3
"""Is the first item a lesson names really the item it was learned on? For every lesson ever filed whose text names a
parsable item, check the ledger: did the lesson's own seat write an event on that item within WINDOW of filing it?
Compared for lessons kinded by the first line (the old rule) and those kinded only by the whole text (the new one).
Corroborated is a proxy, not proof: an uncorroborated lesson may still be right (a seat that worked without ledger
events), so the two rates are compared with each other, not read as accuracy. Read-only."""
import calendar, collections, glob, json, os, random, subprocess, sys, time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src/RimMandrake/Utils"))
import agent_improve as A  # noqa: E402
WINDOW = 3 * 3600

def ep(s):
    try:
        return calendar.timegm(time.strptime(str(s)[:19], "%Y-%m-%dT%H:%M:%S"))
    except ValueError:
        return None

touch = collections.defaultdict(list)   # (seat, item) -> [ts]
for shard in glob.glob(os.path.join(REPO, "infrastructure/state/ledger/events/*.jsonl")):
    for ln in open(shard, errors="replace"):
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        t = ep(r.get("ts"))
        if t and r.get("id") and r.get("seat"):
            touch[(r["seat"], r["id"])].append(t)

def first_item(text):
    import re
    for tok in A.ITEM_TOKEN.findall(text or ""):
        if A.model.parse_name(re.sub(r"_\d+$", "", tok)):
            return tok
    return None

out = subprocess.run(["git", "log", "--all", "--diff-filter=A", "--format=@%h", "--name-only", "--",
                      "infrastructure/state/lessons/"], cwd=REPO, capture_output=True, text=True).stdout
first_add, cur = {}, None
for ln in out.splitlines():
    if ln.startswith("@"):
        cur = ln[1:]
    elif ln.endswith(".md") and not ln.endswith("README.md"):
        first_add.setdefault(ln, cur)
rows = {"first line": [0, 0], "whole text only": [0, 0]}
samples = {"first line": [], "whole text only": []}
for f, c in first_add.items():
    t, seat = A.lessons.parse_name(f)
    if t is None:
        continue
    body = subprocess.run(["git", "show", "%s:%s" % (c, f)], cwd=REPO, capture_output=True, text=True).stdout
    i1, i2 = first_item(A.first_line(body)), first_item(body)
    if not i2:
        continue
    k = "first line" if i1 else "whole text only"
    item = i1 or i2
    ok = any(abs(x - t) <= WINDOW for x in touch.get((seat, item), []) + touch.get((seat, item.rsplit("_", 1)[0]), []))
    rows[k][0] += 1
    rows[k][1] += ok
    samples[k].append((ok, os.path.basename(f), item))
print("# %s  WINDOW +-%d h; corroborated = the lesson's own seat wrote a ledger event on that item in the window"
      % (time.strftime("%Y-%m-%d %H:%M %z"), WINDOW // 3600))
for k, (n, ok) in rows.items():
    print("%-16s lessons %4d  corroborated %4d (%.0f%%)" % (k, n, ok, 100.0 * ok / max(n, 1)))
rng = random.Random(7)
for k in samples:
    print("\nsample of 8, %s:" % k)
    for ok, f, item in rng.sample(samples[k], min(8, len(samples[k]))):
        print("  %-5s %-70s %s" % ("yes" if ok else "no", f[:70], item))
