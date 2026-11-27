#!/usr/bin/env python3
"""rows.py: the measured rows behind design/specs/2026-11-26-script-candidates/one_page.md.

Run (about 1 minute, reads the Conductor transcripts of the last 7 days and the detached run records):
    cd design/specs/2026-11-26-script-candidates/measure
    SCAN_DIR=/some/scratch/dir python3 -I extract.py      # transcripts -> calls.jsonl, turns.jsonl
    SCAN_DIR=/some/scratch/dir python3 -I rows.py         # prints the rows

Definitions (read these before you trust a number):
  call      one tool_use of a Conductor window (a session whose agent-name is CONDUCTOR, mtime within 7.2 days).
  dur       seconds from the tool_use to its tool_result: the wall time that the window waited for the tool.
  gen       seconds from the previous user/assistant event to the tool_use: what the model took to produce that call
            (thinking and writing). A lower bound: a final text reply with no tool call is not counted.
  episode   one turn (a human message, a Stop-hook run-end wake, a task notification, a restart prompt) and the calls
            until the next turn.
A compound Bash command that names two tools counts once per category it matches, so category sums overlap.
"""
import os
import re
import statistics
import sys
import json
import glob
import time
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import calls, turns, episodes, bcmd, cats, P  # noqa: E402


def med(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else None


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(len(xs) * q))] if xs else None


def H(title):
    print("\n=== " + title)


def isb(c):
    return c["name"] == "Bash"


H("BASE: what the window did in the 7 days")
sess = set(c["sid"] for c in calls)
print("conductor sessions", len(sess), "tool calls", len(calls))
print("episodes by kind", collections.Counter(e["turn"]["k"] for e in episodes))
print("tool wait h (all calls)", round(sum(c["dur"] for c in calls) / 3600, 1),
      "| of which AskUserQuestion (owner thinking) h", round(sum(c["dur"] for c in calls if c["name"] == "AskUserQuestion") / 3600, 1))
print("model gen h (calls only)", round(sum(c["gap"] or 0 for c in calls) / 3600, 1))

# ---------------------------------------------------------------- G1
H("G1 owner ruling carried into the rules")
RULEF = re.compile(r"standing_rulings\.md|CLAUDE\.md|biome_rulings\.md|GUIDING_PRINCIPLES|roles/\w+\.md|CONDUCTOR\.md|CHARTER\.md|Agent_Policy\.md|delegation_policy\.md")


def touches_rules(c):
    if c["name"] in ("Edit", "Write"):
        return bool(RULEF.search(c["inp"].get("file_path", "")))
    if isb(c):
        cmd = bcmd(c)
        return bool(RULEF.search(cmd)) and bool(re.search(r"\./publish|git commit|python3? - |sed -i|apply_", cmd))
    return False


bysid = collections.defaultdict(list)
for t in sorted(turns, key=lambda t: (t["sid"], t["t"])):
    bysid[t["sid"]].append(t)
cby = collections.defaultdict(list)
for c in calls:
    cby[c["sid"]].append(c)
rul = []
for sid, ts in bysid.items():
    hum = [t for t in ts if t["k"] == "human"]
    cs = sorted(cby[sid], key=lambda c: c["t"])
    for i, h in enumerate(hum):
        end = hum[i + 1]["t"] if i + 1 < len(hum) else 1e18
        seg = [c for c in cs if h["t"] <= c["t"] < end]
        said = [c for c in seg if isb(c) and "--owner-said" in bcmd(c)]
        rt = [c for c in seg if touches_rules(c)]
        if said and rt:
            span = max(c["t"] + c["dur"] for c in rt) - h["t"]
            greps = [c for c in seg if isb(c) and re.search(r"\b(grep|rg)\b|owner_rulings\.py", bcmd(c))]
            rul.append(dict(span=span, n=len(seg), gen=sum(c["gap"] or 0 for c in seg), tool=sum(c["dur"] for c in seg),
                            greps=len(greps), ggen=sum(c["gap"] or 0 for c in greps), ts=h["ts"]))
print("owner turns with --owner-said AND a rule-file touch:", len(rul))
print("  span min: median %.1f p90 %.1f | calls: median %d | model gen min: median %.1f sum %.0f" % (
    med([r["span"] for r in rul]) / 60, pct([r["span"] for r in rul], .9) / 60, med([r["n"] for r in rul]),
    med([r["gen"] for r in rul]) / 60, sum(r["gen"] for r in rul) / 60))
print("  sum of those spans h (an upper bound: a turn also holds other work):", round(sum(r["span"] for r in rul) / 3600, 1))
print("  turns with >=1 grep/owner_rulings search inside:", sum(1 for r in rul if r["greps"]), "greps total", sum(r["greps"] for r in rul),
      "gen min on them", round(sum(r["ggen"] for r in rul) / 60, 1))

# ---------------------------------------------------------------- G2
H("G2 helper brief written by hand")
fs = [f for f in glob.glob("/mnt/d/ClaudeWork/rimmandrake/conductor/*_brief_*.md") if time.time() - os.path.getmtime(f) < 7.5 * 86400]
perfile = {}
lc = collections.Counter()
for f in fs:
    s = set(l.strip() for l in open(f, errors="replace") if len(l.strip()) >= 25)
    perfile[f] = s
    lc.update(s)
tot = sum(len(s) for s in perfile.values())
print("brief files written in the 7 days", len(fs), "median bytes", med([os.path.getsize(f) for f in fs]))
for k in (2, 3, 5):
    rep = sum(1 for s in perfile.values() for l in s if lc[l] >= k)
    print("  lines (>=25 chars) that appear in >=%d briefs: %d of %d = %d%%" % (k, rep, tot, round(100 * rep / tot)))
bw = [c for c in calls if c["name"] == "Write" and "_brief_" in c["inp"].get("file_path", "")]
be = [c for c in calls if c["name"] == "Edit" and "_brief_" in c["inp"].get("file_path", "")]
hd = [c for c in calls if isb(c) and re.search(r"cat\s*>\s*\S*brief\S*\s*<<|cat\s*>\s*\$\w+/\S*brief", bcmd(c))]
print("Write of a brief file:", len(bw), "model gen min", round(sum(c["gap"] or 0 for c in bw) / 60, 1),
      "| Edit of a brief file:", len(be), "gen min", round(sum(c["gap"] or 0 for c in be) / 60, 1),
      "| heredoc brief in Bash:", len(hd), "gen min", round(sum(c["gap"] or 0 for c in hd) / 60, 1))

# ---------------------------------------------------------------- G3
H("G3 launch returned by the prose check")
LAUNCH = re.compile(r"detached_helper(\.py)?\s+launch")
ret = [i for i, c in enumerate(calls) if isb(c) and LAUNCH.search(bcmd(c)) and "RETURNED BEFORE THE START" in c["rhead"]]
okl = [c for c in calls if isb(c) and LAUNCH.search(bcmd(c)) and "DETACHED rm-detached" in c["rfull"]]
print("launch commands whose result holds 'DETACHED rm-detached' (a run started):", len(okl), "| returned before the start:", len(ret))
edit = noedit = 0
gens = []
walls = []
kinds = collections.Counter()
for i in ret:
    x = calls[i]
    m = re.search(r"--item[ =]+(\S+)", bcmd(x))
    item = m.group(1) if m else None
    for k, w in re.findall(r"\[(\w+)\]\s+'([^']{0,40})'", x["rfull"]):
        kinds[k] += 1
    for j in range(i + 1, min(i + 40, len(calls))):
        y = calls[j]
        if y["sid"] != x["sid"]:
            break
        if isb(y) and item and item in bcmd(y) and LAUNCH.search(bcmd(y)) and "DETACHED" in y["rhead"]:
            between = calls[i + 1:j]
            ed = any(b["name"] in ("Edit", "Write") or (isb(b) and re.search(r"sed -i|python3? - <<|cat\s*>", bcmd(b))) for b in between)
            edit += ed
            noedit += (not ed)
            walls.append(y["t"] + y["dur"] - (x["t"] + x["dur"]))
            gens.append(sum(b["gap"] or 0 for b in between) + (y["gap"] or 0))
            break
print("  relaunched after an edit:", edit, "| relaunched unchanged:", noedit, "| no relaunch seen:", len(ret) - edit - noedit)
print("  fault kinds in the returns:", dict(kinds))
print("  model gen min between return and start (sum):", round(sum(gens) / 60, 1), "| median wall s", round(med(walls) or 0))
print("  the returned launches' own wait min:", round(sum(calls[i]["dur"] for i in ret) / 60, 1))
print("  launch (started) wall s: median %d p90 %d" % (med([c["dur"] for c in okl]), pct([c["dur"] for c in okl], .9)))

# ---------------------------------------------------------------- G4
H("G4 card answers recorded by hand")
asks = [c for c in calls if c["name"] == "AskUserQuestion"]
nq = sum(len(c["inp"].get("questions", [])) for c in asks)
bc = [c for c in calls if isb(c) and "--by-card" in bcmd(c)]
print("AskUserQuestion calls", len(asks), "questions", nq, "| owner wait h", round(sum(c["dur"] for c in asks) / 3600, 1),
      "median min", round(med([c["dur"] for c in asks]) / 60, 1))
print("commands carrying --by-card:", len(bc), "tool min", round(sum(c["dur"] for c in bc) / 60, 1), "gen min", round(sum(c["gap"] or 0 for c in bc) / 60, 1))
w = 0
wg = 0
wd = 0
for a in asks:
    ans = a["t"] + a["dur"]
    seg = [y for y in calls if y["sid"] == a["sid"] and ans <= y["t"] < ans + 900 and isb(y)
           and re.search(r"--by-card|card_capture|(cli\.py|rimflow)\s+(note|file|close|wait)\b", bcmd(y))]
    w += len(seg)
    wg += sum(y["gap"] or 0 for y in seg)
    wd += sum(y["dur"] for y in seg)
print("ledger writes within 15 min after an answer:", w, "gen min", round(wg / 60, 1), "tool min", round(wd / 60, 1))

# ---------------------------------------------------------------- G5
H("G5 start of a window")
rs = [e for e in episodes if e["turn"]["k"] == "restart"]
print("restart prompts (fresh Conductor windows):", len(rs), "| calls per restart: mean %.1f" % (sum(len(e["calls"]) for e in rs) / len(rs)))
by = collections.defaultdict(lambda: [0, 0])
for e in rs:
    for c in e["calls"][:14]:
        if c["name"] == "Read":
            k = "Read " + os.path.basename(c["inp"].get("file_path", ""))
        elif isb(c):
            m = re.search(r"(seat_restart\.py\s+\w+|detached_helper\.py\s+\w+|cli\.py\s+\w+)", bcmd(c))
            k = m.group(1) if m else "bash other"
        else:
            k = c["name"]
        by[k][0] += 1
        by[k][1] += c["rlen"]
tot_chars = sum(v[1] for v in by.values())
print("first 14 calls of each restart read %d chars in total (%d per restart)" % (tot_chars, tot_chars // len(rs)))
for k, (n, s) in sorted(by.items(), key=lambda kv: -kv[1][1])[:6]:
    print("   %-40s n=%3d chars=%8d (%d avg)" % (k, n, s, s // n))
span = [max(c["t"] + c["dur"] for c in e["calls"]) - e["turn"]["t"] for e in rs if e["calls"]]
print("restart -> last call of its episode: median %d s, sum h %.1f" % (med(span), sum(span) / 3600))
print("restart episode model gen min (sum):", round(sum(c["gap"] or 0 for e in rs for c in e["calls"]) / 60, 1))
print("the part printed more than once: see evidence.md (exact repeated lines of >=40 chars: 2.2%; repeated meaning UNMEASURED)")

# ---------------------------------------------------------------- G6
H("G6 waiting for a launch, a publish, a run")
PUB = re.compile(r"(^|[;&|\s])\./publish\b")
pubs = [c for c in calls if isb(c) and PUB.search(bcmd(c)) and ("PUBLISHED" in c["rfull"] or "PUBLISHED" in c["rtail"])]
print("publish commands that landed (result holds PUBLISHED):", len(pubs), "wall s: median %d p90 %d max %d | sum h %.1f" % (
    med([c["dur"] for c in pubs]), pct([c["dur"] for c in pubs], .9), max(c["dur"] for c in pubs), sum(c["dur"] for c in pubs) / 3600))
pubf = [c for c in calls if isb(c) and re.match(r"(cd [^;]+;\s*)?\./publish", bcmd(c).strip()) and not ("PUBLISHED" in c["rfull"] or "PUBLISHED" in c["rtail"])]
print("publish commands that start with ./publish and did not land:", len(pubf))
for pat, nm in [(r"detached_helper(\.py)?\s+status", "helper status poll"), (r"\./pipe why", "pipe why"), (r"\./pipe show", "pipe show"),
                (r"\bsleep\s+\d|waitalive|waitfor|\buntil\b", "sleep / wait loop")]:
    cs = [c for c in calls if isb(c) and re.search(pat, bcmd(c))]
    print("%-20s n=%3d wall h %.2f median s %d p90 s %d gen min %.1f" % (nm, len(cs), sum(c["dur"] for c in cs) / 3600, med([c["dur"] for c in cs]), pct([c["dur"] for c in cs], .9), sum(c["gap"] or 0 for c in cs) / 60))
bg = [c for c in calls if isb(c) and c["inp"].get("run_in_background")]
print("background Bash calls", len(bg))

# ---------------------------------------------------------------- G7
H("G7 a worker's report: acts after a run-end wake")
W = [e for e in episodes if e["turn"]["k"] == "wake_run_end"]
print("run-end wakes:", len(W), "| zero-call replies:", sum(1 for e in W if not e["calls"]))
ver = [e for e in W if any(isb(c) and (re.search(r"\bgit\s+(-C\s+\S+\s+)?(log|show|cat-file|diff|ls-remote|branch|merge-base)", bcmd(c)) or re.search(r"(cli\.py|rimflow)\s+show", bcmd(c))) for c in e["calls"])]
print("wake episodes that contain a git log/show/cat-file/diff or a rimflow show:", len(ver))
vc = [c for e in ver for c in e["calls"] if isb(c) and (re.search(r"\bgit\s+(-C\s+\S+\s+)?(log|show|cat-file|diff|ls-remote|branch|merge-base)", bcmd(c)) or re.search(r"(cli\.py|rimflow)\s+show", bcmd(c)))]
print("  verification calls in them:", len(vc), "tool min", round(sum(c["dur"] for c in vc) / 60, 1), "gen min", round(sum(c["gap"] or 0 for c in vc) / 60, 1))
spans = [max(c["t"] + c["dur"] for c in e["calls"]) - e["turn"]["t"] for e in W if e["calls"]]
print("all wake episodes: wall h", round(sum(spans) / 3600, 1), "median s", round(med(spans)), "calls mean %.1f" % (sum(len(e["calls"]) for e in W) / len(W)),
      "gen min", round(sum(c["gap"] or 0 for e in W for c in e["calls"]) / 60, 1))
first = collections.Counter()
for e in W:
    if e["calls"]:
        c = e["calls"][0]
        first[cats(bcmd(c))[0] if isb(c) else c["name"]] += 1
print("  first call after a wake:", first.most_common(8))
txt = [t["len"] for t in turns if t["k"] == "wake_run_end"]
print("  wake text chars: median", med(txt), "p90", pct(txt, .9))

# ---------------------------------------------------------------- G8
H("G8 reading old tickets / asks")
shows = [c for c in calls if isb(c) and re.search(r"(cli\.py|rimflow)\s+show\b", bcmd(c))]
print("rimflow show calls:", len(shows), "wall h %.2f" % (sum(c["dur"] for c in shows) / 3600), "median s %d p90 s %d" % (med([c["dur"] for c in shows]), pct([c["dur"] for c in shows], .9)), "gen min %.1f" % (sum(c["gap"] or 0 for c in shows) / 60))
print("  result chars: median %d p90 %d" % (med([c["rlen"] for c in shows]), pct([c["rlen"] for c in shows], .9)))
bursts = 0
bc_calls = 0
for sid, cs in cby.items():
    cs = sorted(cs, key=lambda c: c["t"])
    run = []
    for c in cs:
        if c in shows and (not run or c["t"] - run[-1]["t"] < 300):
            run.append(c)
        else:
            if len(run) >= 4:
                bursts += 1
                bc_calls += len(run)
            run = [c] if c in shows else []
    if len(run) >= 4:
        bursts += 1
        bc_calls += len(run)
print("bursts of >=4 shows within 5 min:", bursts, "calls in them", bc_calls)
stale = [e for e in episodes if e["turn"]["k"] == "human" and re.search(r"\b(stale|still stuck|why is .* still|old ticket|outdated|already done)\b", e["turn"]["head"], re.I)]
print("human turns whose first 300 chars say stale/stuck/old:", len(stale))
print("whether a show was meant to judge staleness: UNMEASURED (the call does not say)")

# ---------------------------------------------------------------- G9
H("G9 many tickets parked / re-homed / closed")
V = re.compile(r"(?:cli\.py|rimflow)\s+(close|drop|wait|supersede|park|rehome|home|note|release|ack|needs|target|unpark|reopen)\s+([A-Z][A-Za-z0-9_]{8,})")
big = []
for e in episodes:
    ids = set()
    for c in e["calls"]:
        if isb(c):
            ids.update((v, i) for v, i in V.findall(bcmd(c)))
    if len(ids) >= 5:
        big.append(len(ids))
print("episodes with >=5 distinct hand ledger acts (close/drop/wait/home/note...):", len(big))
loops = [c for c in calls if isb(c) and re.search(r"\bfor\s+\w+\s+in\b", bcmd(c)) and re.search(r"(cli\.py|rimflow|\$R)\s+(close|drop|wait|home|note|park)\b", bcmd(c))]
print("shell loops that write the ledger:", len(loops))
verbs = collections.Counter()
for c in calls:
    if isb(c):
        for v, i in V.findall(bcmd(c)):
            verbs[v] += 1
print("hand ledger writes by verb:", dict(verbs))
D = "/mnt/d/ClaudeWork/rimmandrake/dispatcher/detached/"
now = time.time()
recs = []
for f in glob.glob(D + "*.json"):
    if f.endswith(".out.json"):
        continue
    try:
        d = json.load(open(f))
    except Exception:
        continue
    if now - d.get("at", 0) > 7.2 * 86400:
        continue
    try:
        o = json.load(open(f[:-5] + ".out.json"))
    except Exception:
        o = None
    recs.append((d, o))
bulk = collections.Counter()
for d, o in recs:
    it = d.get("item", "")
    p = it.split("_")
    verb = p[1] if len(p) > 1 and p[0] in ("RIMMANDRAKE", "RIMMASTER") else p[0]
    bulk[verb] += 1
print("detached runs in the 7 days:", len(recs), "| bulk-style verbs:", {k: bulk[k] for k in ("SWEEP", "CLEAR", "ROUTE", "PARK", "REHOME", "RESCOPE", "FOLD", "TRIAGE", "AUDIT") if bulk[k]})

# ---------------------------------------------------------------- G10
H("G10 searching for lines that say the opposite of a new ruling")
GR = [c for c in calls if isb(c) and re.search(r"\b(grep|rg)\b", bcmd(c)) and re.search(r"(?<![\w-])-[a-zA-Z]*[rR][a-zA-Z]*\s|--include|-rn|-rl", bcmd(c))
      and re.search(r"CLAUDE\.md|standing_rulings|roles/|design/|skills/|infrastructure/agents|\bsrc/", bcmd(c))]
print("recursive grep over rule / design / code trees:", len(GR), "wall min", round(sum(c["dur"] for c in GR) / 60, 1), "gen min", round(sum(c["gap"] or 0 for c in GR) / 60, 1))
print("inside the %d ruling-carrying turns: see G1 (greps counted there)" % len(rul))
print("whether a grep hunted a contradiction: UNMEASURED (the call does not say)")
print("owner_rulings.py --grep calls:", len([c for c in calls if isb(c) and "owner_rulings.py" in bcmd(c)]))

# ---------------------------------------------------------------- G11
H("G11 sizing a spend cap")
rows = []
for d, o in recs:
    it = d.get("item", "")
    p = it.split("_")
    verb = p[1] if len(p) > 1 and p[0] in ("RIMMANDRAKE", "RIMMASTER") else p[0]
    rows.append(dict(verb=verb, budget=d.get("budget_usd"), cost=(o or {}).get("total_cost_usd"), sub=(o or {}).get("subtype"), model=d.get("model")))
done = [r for r in rows if r["cost"] is not None]
hit = [r for r in rows if r["sub"] == "error_max_budget_usd"]
print("run records", len(rows), "with a cost", len(done), "ended at the cap (error_max_budget_usd):", len(hit), "(dollar figures are cost_usd fields of the run records)")
byv = collections.defaultdict(list)
for r in done:
    byv[r["verb"]].append(r["cost"])
below = 0
for r in hit:
    cs = byv[r["verb"]]
    p90 = pct(cs, .9)
    below += (r["budget"] or 0) < p90
    print("   cap hit: verb %-9s cap %5.0f  verb p90 %5.1f  (n=%d)" % (r["verb"], r["budget"] or 0, p90, len(cs)))
print("caps hit that sat below the verb's p90 cost:", below, "of", len(hit))
lv = [c for c in calls if isb(c) and LAUNCH.search(bcmd(c)) and "--budget-usd" in bcmd(c)]
print("launch commands carrying --budget-usd:", len(lv))
cap_ref = [c for c in calls if isb(c) and "a spend cap is required" in c["rfull"]]
print("launches refused for a missing cap:", len(cap_ref))
print("distinct caps used by the 1018 records:", collections.Counter(r["budget"] for r in rows).most_common(8))

# ---------------------------------------------------------------- G12
H("G12 closing an item")
cl = [i for i, c in enumerate(calls) if isb(c) and re.search(r"(cli\.py|rimflow)\s+close\s+[A-Z]", bcmd(c))]
pat = re.compile(r"has not earned its close|close: refused|cannot close")
ref = [i for i in cl if pat.search(calls[i]["rfull"])]
redo = 0
sec = []
for i in ref:
    c = calls[i]
    it = re.findall(r"close\s+([A-Z][A-Z0-9_]{8,})", bcmd(c))[0]
    for j in range(i + 1, min(i + 40, len(calls))):
        y = calls[j]
        if y["sid"] != c["sid"]:
            break
        if re.search(r"close\s+" + re.escape(it), bcmd(y)):
            redo += 1
            sec.append(y["t"] - c["t"])
            break
print("close commands:", len(cl), "refused:", len(ref), "redone in the window:", redo, "redo after s:", [round(s) for s in sec])
print("close wall min", round(sum(calls[i]["dur"] for i in cl) / 60, 1), "gen min", round(sum(calls[i]["gap"] or 0 for i in cl) / 60, 1))

# ---------------------------------------------------------------- NEW KINDS
H("NEW kinds the data shows")
pys = [c for c in calls if isb(c) and re.search(r"python3?\s+(-\w+\s+)*-\s*(<<|\s|$)|python3?\s+(-\w+\s+)*-c\b|python3? <<", bcmd(c))]
print("inline python one-offs:", len(pys), "gen min", round(sum(c["gap"] or 0 for c in pys) / 60, 1), "wall min", round(sum(c["dur"] for c in pys) / 60, 1))
topics = [("run records: out.json cost / turns / result", r"\.out\.json|total_cost_usd|num_turns"),
          ("ledger events jsonl", r"ledger/events"), ("window transcripts (.claude/projects)", r"\.claude/projects"),
          ("conductor log.md", r"conductor/log\.md"), ("item prose / queue", r"infrastructure/state/items|/queue/")]
for nm, rx in topics:
    cs = [c for c in pys if re.search(rx, bcmd(c))]
    print("  %-48s n=%3d gen min %.1f wall min %.1f" % (nm, len(cs), sum(c["gap"] or 0 for c in cs) / 60, sum(c["dur"] for c in cs) / 60))
find_item = [c for c in calls if isb(c) and re.search(r"(ls\s+\S*items/?\s*\|\s*grep|git ls-files\s*\|\s*grep|ls\s+-t?\s*\S*items\S*\s*\|\s*grep|grep\s+-\w*l\w*\s+.*infrastructure/state/items)", bcmd(c))]
print("finding an item or file by words (ls | grep, git ls-files | grep):", len(find_item), "gen min", round(sum(c["gap"] or 0 for c in find_item) / 60, 1), "wall min", round(sum(c["dur"] for c in find_item) / 60, 1))
sy = [c for c in calls if isb(c) and re.search(r"\./sync\b", bcmd(c))]
print("./sync in the command:", len(sy), "wall min of those commands", round(sum(c["dur"] for c in sy) / 60, 1))
pw = [c for c in calls if isb(c) and re.search(r"\./pipe\s+(why|show|log)\b|detached_helper(\.py)?\s+status|cli\.py\s+(queue|next|incidents|seat)\b|game_lock\.py query|accounts\.py|\./acct", bcmd(c))]
print("state polls (pipe why/show/log, helper status, queue/next/incidents/seat, game_lock query, accounts, acct):", len(pw),
      "wall h", round(sum(c["dur"] for c in pw) / 3600, 2), "gen min", round(sum(c["gap"] or 0 for c in pw) / 60, 1), "result chars sum", sum(c["rlen"] for c in pw))
print("  polls per window-hour of tool time: n/a; polls by kind:", collections.Counter(
    (re.search(r"\./pipe\s+(\w+)|detached_helper(?:\.py)?\s+(\w+)|cli\.py\s+(\w+)|game_lock\.py (\w+)|accounts\.py|\./acct", bcmd(c)).group(0)[:34]) for c in pw).most_common(10))
hp = [c for c in calls if isb(c) and re.search(r"python3 src/RimMandrake/rimflow/cli\.py\s+(file|spawn)\s", bcmd(c))]
okf = [c for c in hp if re.search(r"filed|FILED|PUBLISHED", c["rfull"])]
print("rimflow file commands:", len(hp), "wall min", round(sum(c["dur"] for c in hp) / 60, 1), "gen min", round(sum(c["gap"] or 0 for c in hp) / 60, 1),
      "title/text chars mean", int(sum(len(bcmd(c)) for c in hp) / max(1, len(hp))))
nc = [c for c in calls if isb(c) and "namecheck" in bcmd(c)]
print("namecheck calls", len(nc), "gen min", round(sum(c["gap"] or 0 for c in nc) / 60, 1))

# ---------------------------------------------------------------- EXTRA rows used by one_page.md
H("EXTRA publish by kind of path, file bursts, hand reads of a run result, cap-hit spend")
import bisect  # noqa: E402
pubs = [c for c in calls if isb(c) and PUB.search(bcmd(c)) and ("PUBLISHED" in c["rfull"] or "PUBLISHED" in c["rtail"])]
groups = {"ledger-only": [], "md/json/txt only": [], "has a code path": []}
for c in pubs:
    m = re.search(r"\./publish\b(.*?)(?:2>&1|\||;|$)", bcmd(c).replace("\n", " "))
    args = m.group(1) if m else ""
    paths = re.findall(r'(?:"|\s)((?:[\w\.\-/]+/)?[\w\.\-]+\.(?:md|json|jsonl|py|cs|xml|sh|txt|html))(?:"|\s|$)', args)
    if "--ledger" in args or (paths and all(p.endswith(".jsonl") for p in paths)):
        groups["ledger-only"].append(c["dur"])
    elif paths and all(p.endswith((".md", ".json", ".txt", ".html")) for p in paths):
        groups["md/json/txt only"].append(c["dur"])
    elif paths:
        groups["has a code path"].append(c["dur"])
for k, v in groups.items():
    print("publish %-18s n=%3d median s %3d p90 s %3d sum min %.0f" % (k, len(v), med(v) or 0, pct(v, .9) or 0, sum(v) / 60))
fl = [c for c in calls if isb(c) and re.search(r"(cli\.py|rimflow)\s+file\s", bcmd(c))]
adj = 0
prev = None
for c in sorted(fl, key=lambda c: (c["sid"], c["t"])):
    if prev and prev["sid"] == c["sid"] and c["t"] - prev["t"] < 180:
        adj += 1
    prev = c
print("rimflow file commands:", len(fl), "median s", round(med([c["dur"] for c in fl])), "p90 s", round(pct([c["dur"] for c in fl], .9)),
      "| within 3 min of another file command:", adj, "| carrying --publish:", sum(1 for c in fl if "--publish" in bcmd(c)))
rr = [c for c in calls if isb(c) and re.search(r"python3?[^\n]*(-c|<<|-\s)", bcmd(c)) and ".out.json" in bcmd(c)
      and re.search(r"\['result'\]|get\('result'|\.result|\"result\"", bcmd(c))]
wk = collections.defaultdict(list)
for t in turns:
    if t["k"] == "wake_run_end":
        wk[t["sid"]].append(t["t"])
inw = 0
for c in rr:
    ts = sorted(wk[c["sid"]])
    i = bisect.bisect_right(ts, c["t"]) - 1
    if i >= 0 and c["t"] - ts[i] < 600:
        inw += 1
print("hand reads of a run's result (inline python on *.out.json, reads 'result'):", len(rr), "gen min", round(sum(c["gap"] or 0 for c in rr) / 60, 1),
      "wall min", round(sum(c["dur"] for c in rr) / 60, 1), "| within 10 min after a run-end wake:", inw)
tot = 0
n = 0
its = collections.Counter()
allc = 0
for d, o in recs:
    if o and o.get("total_cost_usd"):
        allc += o["total_cost_usd"]
    if o and o.get("subtype") == "error_max_budget_usd":
        tot += o.get("total_cost_usd") or 0
        n += 1
        its[d.get("item")] += 1
print("cap-hit runs", n, "cost_usd sum", round(tot), "of all run cost_usd", round(allc), "| items hit twice or more:", sum(1 for v in its.values() if v > 1))

H("EXTRA wake: exact repeated lines in the first 14 tool results + SessionStart text of each window")
sids = set(c["sid"] for c in calls)
rootp = os.path.expanduser("~/.claude/projects/-home-mandrake-rm-bench/")
tot_c = 0
dup_c = 0
for f in glob.glob(rootp + "*.jsonl"):
    if os.path.basename(f)[:8] not in sids:
        continue
    seen = set()
    n_res = 0
    for l in open(f):
        d = json.loads(l)
        texts = []
        a = d.get("attachment")
        if a and a.get("type") == "hook_success" and a.get("hookEvent") == "SessionStart":
            texts.append(a.get("stdout", ""))
        if d.get("type") == "user":
            m = d["message"]["content"]
            if isinstance(m, str):
                texts.append(m)
            else:
                for b in m:
                    if b.get("type") == "text":
                        texts.append(b["text"])
                    if b.get("type") == "tool_result":
                        r = b.get("content")
                        r = " ".join(x.get("text", "") for x in r if isinstance(x, dict)) if isinstance(r, list) else (r or "")
                        texts.append(r)
                        n_res += 1
        for t in texts:
            if n_res > 14:
                break
            for ln in t.split("\n"):
                ln = ln.strip()
                if len(ln) < 40:
                    continue
                tot_c += len(ln)
                if ln in seen:
                    dup_c += len(ln)
                seen.add(ln)
        if n_res > 14:
            break
print("chars in lines >=40 chars:", tot_c, "of which an exact repeat of an earlier line in the same window:", dup_c, "= %.1f%%" % (100 * dup_c / tot_c))
