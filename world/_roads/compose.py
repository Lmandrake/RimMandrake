"""Compose the new road network: reroute + class + spurs + strays + the dead highway.

🔴 THE PALETTE IS "HEAT IS THE STORY" - owner, 2026-08-25. All five RoadDefs carry
`movementCostMultiplier: 0.5` identically (read live off the defs), so the class is pure
narrative and costs the player nothing. What it says:

    StoneRoad   DAY ROAD    shaded, watered or simply cool - walkable in the light
    DirtRoad    DUSK ROAD   passable, but you will suffer. the ordinary caravan net
    DirtPath    NIGHT TRAIL crossed only in the dark - nothing grows, nothing shades you
    AncientAsphaltHighway   laid by people who did not care about shade. it is why it is dead

🔑 The class is MEASURED off the route, not chosen for it. A road became a day road because
it FOUND shade and water; a night trail is straight because there was nothing to bend
toward. That is why the story cannot disagree with the map.
"""
import sys, json, collections
sys.path.insert(0,'/mnt/d/Luke/dev/Rimworld/world/_roads')
from rcommon import *
from field import build, RUIN_LM
from route import Router
from waypoint import insert

DAY, DUSK, NIGHT = 'StoneRoad', 'DirtRoad', 'DirtPath'
ANCIENT = 'AncientAsphaltHighway'
PRIORITY = {'DirtPath':10, 'DirtRoad':20, 'StoneRoad':30, 'AncientAsphaltRoad':40,
            ANCIENT:50}

F = build(); tiles, nb, setts, lm = F['tiles'], F['nb'], F['setts'], F['lm']
C = F['comfort']
forbid = {o['tile'] for o in setts if o['faction']=='TribeCivil'}
forbid |= {o['tile'] for o in setts if o['faction']=='Jawa_FreeDroidEnclaves' and o['tile']!=19350}
rt = Router(F, forbid=forbid)
runs = json.load(open(R+'rerouted.json'))

def classify(p):
    cf = sum(C[t] for t in p)/len(p)
    tm = sum(tiles[t]['tmax'] for t in p)/len(p)
    if cf >= 0.40 or tm <= 20.0: return DAY
    if cf < 0.16 and tm >= 45.0: return NIGHT
    return DUSK

edges = {}                      # (lo,hi) -> def
def lay(path, d):
    for i in range(len(path)-1):
        k = (min(path[i],path[i+1]), max(path[i],path[i+1]))
        if k not in edges or PRIORITY[d] > PRIORITY[edges[k]]: edges[k] = d

for r in runs:
    lay(r['new'], classify(r['new']))
print("rerouted runs laid: %d edges" % len(edges))
byd = collections.Counter(edges.values())
print("  classes: %s" % dict(byd))

# ---- 2. reconnect the strays the owner asked for -------------------------
STRAYS = {17310:'Greenshadow', 19371:'Kettle Deep', 9451:'Deepwater Hold',
          21576:'The Godmouth', 8497:'Hollow Hive', 5500:'The Coil', 21037:'Quiet Lab'}
net = {t for e in edges for t in e}
for tid, nm in STRAYS.items():
    src = min(net, key=lambda t: gcdeg(tiles, t, tid))
    p, wp = insert(rt, F, src, tid, ceiling=1.9, max_wp=2)
    if p is None:
        print("  ⚠️  %s: no route" % nm); continue
    d = classify(p); lay(p, d)
    print("  + %-15s %2d steps from %-6d  %-10s via %s" % (nm, len(p)-1, src, d,
          [lm[t] for t in wp] or '-'))

# ---- 3. No Master: the canon road that ends one tile short ---------------
# ⚠️ It CANNOT reach the settlement: tile 19350 is AB_MechanoidIntrusion, allowRoads=FALSE,
# so a link there is stored and never drawn. Ending at 6486 is the maximum achievable.
print("  = No Master left at its jungle railhead 6486 (its own tile forbids roads)")

# ---- 4. spurs that go to a hint and stop --------------------------------
net = {t for e in edges for t in e}
ruin_t = sorted(t for t in lm if set(lm[t]) & RUIN_LM)
def bfsd(seed, maxd):
    d = {t:0 for t in seed}; fr=list(seed)
    for k in range(1,maxd+1):
        nx=[]
        for t in fr:
            for n in nb[t]:
                if n not in d: d[n]=k; nx.append(n)
        fr=nx
        if not fr: break
    return d
dnet = bfsd(net, 12)
spurs = 0
for t in ruin_t:
    d = dnet.get(t, 99)
    if not (2 <= d <= 7): continue
    if not rt.passable(t, {t}): continue
    # ⛔ leave gaps on purpose - a spur to EVERY hint reads as generated. Deterministic
    # by tile id, never RNG: a seed is a knob that could roll a second planet.
    if (t * 2654435761) % 100 >= 55: continue
    src = min(net, key=lambda x: gcdeg(tiles, x, t))
    p, _ = insert(rt, F, src, t, ceiling=2.0, max_wp=1)
    if p is None or len(p) < 3: continue
    lay(p, classify(p)); spurs += 1
print("spurs to a hint: %d  (total edges now %d)" % (spurs, len(edges)))

json.dump({'%d,%d'%k: v for k,v in edges.items()}, open(R+'edges.json','w'))
print("\nFINAL  %d edges over %d tiles" % (len(edges), len({t for e in edges for t in e})))
print("  %s" % dict(collections.Counter(edges.values())))

# ---- 5. THE ASHFALL ROAD: a highway laid by people who did not care ------
# 🔑 It is straight because its builders had machines and no interest in shade, and it is
# DEAD because that is what the straight line across the Anvil costs. It connects nothing
# alive: an ancient launch site to a quarry to a garrison, through 71 C ground.
# ⛔ Not routed over the comfort field at all - comfort_w 0 and a heavy turn penalty.
# It survives only on HARD ground; where it crossed sand the sand has it.
ANCHORS = [4000, 14470, 20514]          # AncientLaunchSite - AncientQuarry - AncientGarrison
# 🔑 WHERE THE SAND TAKES IT. Not a hash and not a biome list - the mechanism. Sand
# accumulates in HOLLOWS and is scoured off RISES, so the highway survives on ground that
# stands above its neighbours and is buried where it dips below them. Deterministic,
# terrain-driven, and the gap lengths come out the length the dune fields actually are.
def buried(t):
    m = sum(tiles[n]['elev'] for n in nb[t]) / len(nb[t])
    return tiles[t]['elev'] < m - 5.0
trunk = [ANCHORS[0]]
for i in range(len(ANCHORS)-1):
    leg = rt.route(ANCHORS[i], ANCHORS[i+1], turn_w=2.5, comfort_w=0.0, pad=10.0,
                   straight_w=0.0)   # ⭐ the ancient road is SUPPOSED to hold its bearing
    if leg is None:
        print("  ⚠️  highway leg %d->%d refused" % (ANCHORS[i], ANCHORS[i+1])); continue
    trunk += leg[1:]
frag, cur, kept = [], [], 0
for t in trunk:
    if not buried(t):
        cur.append(t)
    else:
        if len(cur) >= 3: frag.append(cur)
        cur = []
if len(cur) >= 3: frag.append(cur)
for seg in frag:
    lay(seg, ANCIENT); kept += len(seg)-1
print("the Ashfall Road: %d tiles laid, %d fragments totalling %d edges survive the sand"
      % (len(trunk), len(frag), kept))
for seg in frag:
    print("    %2d tiles  %-16s -> %-16s" % (len(seg), tiles[seg[0]]['region'], tiles[seg[-1]]['region']))

json.dump({'%d,%d'%k: v for k,v in edges.items()}, open(R+'edges.json','w'))
cnt = collections.Counter(edges.values())
print("\nFINAL  %d edges over %d tiles" % (len(edges), len({t for e in edges for t in e})))
for d in (ANCIENT, DAY, DUSK, NIGHT):
    if cnt[d]: print("   %-22s %4d edges" % (d, cnt[d]))
