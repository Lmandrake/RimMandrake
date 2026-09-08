import csv, json, collections, math

T = {int(r["tile"]): r for r in csv.DictReader(open("/mnt/d/Luke/dev/Rimworld/world/ASHKARR_WORLDMAP_tiles.csv"))}
objs = json.load(open("/mnt/d/Luke/dev/Rimworld/Transient/objects_raw.json"))
lms = json.load(open("/mnt/d/Luke/dev/Rimworld/Transient/landmarks_raw.json"))
settle = {o["tile"] for o in objs if o.get("isSettlement")}
lmk = {l["tile"] for l in lms}


def load(p):
    d = {}
    for r in csv.DictReader(open(p)):
        if r.get("kind") != "road":
            continue
        a, b = int(r["a"]), int(r["b"])
        d[(min(a, b), max(a, b))] = r["def"]
    return d


IMP = load("/mnt/d/Luke/dev/Rimworld/world/_roads/roads_import.csv")
WM = load("/mnt/d/Luke/dev/Rimworld/world/ASHKARR_WORLDMAP_links.csv")
links = json.load(open("/mnt/d/Luke/dev/Rimworld/Transient/links_raw.json"))
LIVE = {}
for r in links:
    t = r["tile"]
    for pr in (r.get("potentialRoads") or []):
        nb = pr.get("neighbor", pr.get("neighbour", pr.get("tile")))
        if nb is not None:
            LIVE[(min(t, nb), max(t, nb))] = pr.get("def") or pr.get("road")


def xyz(t):
    la = math.radians(float(T[t]["lat"]))
    lo = math.radians(float(T[t]["lon"]))
    return (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))


def straight_runs(adj):
    """Longest run of consecutive steps that hold the same bearing (cos > 0.93).
    This is the metric that matches what an eye reads as 'laser-straight'."""
    runs = []
    seen = set()
    for s in adj:
        if len(adj[s]) != 1 or s in seen:
            continue
        prev, cur = None, s
        run, best = 1, 1
        while True:
            seen.add(cur)
            nxt = [x for x in adj[cur] if x != prev]
            if len(nxt) != 1:
                break
            n = nxt[0]
            if prev is not None:
                a, b, c = xyz(prev), xyz(cur), xyz(n)
                v1 = [b[i] - a[i] for i in range(3)]
                v2 = [c[i] - b[i] for i in range(3)]
                m1 = math.sqrt(sum(x * x for x in v1)) or 1e-9
                m2 = math.sqrt(sum(x * x for x in v2)) or 1e-9
                cos = sum(v1[i] * v2[i] for i in range(3)) / (m1 * m2)
                run = run + 1 if cos > 0.93 else 1
                best = max(best, run)
            prev, cur = cur, n
        runs.append(best)
    return runs


def report(name, E):
    adj = collections.defaultdict(set)
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    seen, comps = set(), []
    for t in adj:
        if t in seen:
            continue
        st, c = [t], []
        seen.add(t)
        while st:
            x = st.pop()
            c.append(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    st.append(y)
        comps.append(c)
    comps.sort(key=len, reverse=True)
    ends = [t for t in adj if len(adj[t]) == 1]
    orph = [t for t in ends if t not in settle and t not in lmk]
    nos = [c for c in comps if not set(c) & settle]
    runs = straight_runs(adj)
    hidden = sum(1 for e in E if T.get(e[0], {}).get("biome") == "AB_PropaneLakes"
                 or T.get(e[1], {}).get("biome") == "AB_PropaneLakes")
    print("%-30s %5d %6d %6d %7d %8d %9d %8s %7s %8d" % (
        name, len(E), len(adj), len(comps), len(nos), len(orph),
        len(({t for e in E for t in e}) & settle),
        "%.1f" % (sum(runs) / len(runs)) if runs else "-",
        max(runs) if runs else "-", hidden))


print("=" * 118)
print("%-30s %5s %6s %6s %7s %8s %9s %8s %7s %8s" % (
    "network", "edges", "tiles", "comps", "no-sett", "deadends", "setts hit", "straight", "worst", "on-lake"))
print("-" * 118)
report("roads_import.csv  (Aug 25)", set(IMP))
report("ASHKARR_WORLDMAP_links.csv", set(WM))
report("LIVE (what is on the planet)", set(LIVE))
print("-" * 118)
report("  live: worldmap-CSV part", set(LIVE) & set(WM))
report("  live: import-only part", set(LIVE) & (set(IMP) - set(WM)))
report("  live: orphans, neither file", set(LIVE) - set(IMP) - set(WM))
print("=" * 118)
print("'straight' = mean longest same-bearing run per road strand; 'worst' = the longest anywhere.")
print("The road skill's own target at STRAIGHT_W 0.55 was mean 3.0 / max 5.")
print("'no-sett' = components reaching no settlement. 'on-lake' = edges on AB_PropaneLakes, which draws no road.")
