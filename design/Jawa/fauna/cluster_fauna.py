#!/usr/bin/env python3
"""Group ~1,260 creatures without a human looking at each one, then CHECK whether the
grouping is any good.

The check is the point. 462 creatures already carry biome assignments made by their own
mod authors; 798 carry none. So the 462 are a labelled test set: if a visual clustering
predicts real biome co-occurrence better than chance on them, it is worth trusting on the
798. If it does not, it is decoration and should be said so.
"""
import csv, json, math, os, sys, collections
import numpy as np

FA = os.path.dirname(os.path.abspath(__file__))
FEAT = os.path.join(FA, 'sprite_features.csv')
rows = list(csv.DictReader(open(FEAT, encoding='utf-8')))
print(f"{len(rows)} sprites with features")

def fnum(r, k, d=0.0):
    try: return float(r[k])
    except (ValueError, TypeError, KeyError): return d

# ---------- feature blocks ----------
def hue_xy(r):
    """Hue as a 2-vector so 359 deg and 1 deg are neighbours, scaled by how concentrated it is."""
    h = fnum(r,'hue'); c = fnum(r,'hue_conc'); s = fnum(r,'sat')
    m = c * s
    return [m*math.cos(2*math.pi*h), m*math.sin(2*math.pi*h)]

COLOUR = lambda r: hue_xy(r) + [fnum(r,'sat'), fnum(r,'val'), fnum(r,'contrast')] + \
                   [float(x) for x in r['hist'].split()]
SHAPE  = lambda r: [math.log(max(fnum(r,'aspect'),1e-3)), fnum(r,'fill'),
                    fnum(r,'spiky'), fnum(r,'symmetry'),
                    math.log(max(fnum(r,'bodySize'),1e-3))]

def zscore(M):
    M = np.asarray(M, dtype=float)
    mu = M.mean(0); sd = M.std(0); sd[sd == 0] = 1
    return (M - mu) / sd

def kmeans(X, k, iters=60, seed=0):
    rng = np.random.default_rng(seed)
    # k-means++ init
    C = [X[rng.integers(len(X))]]
    for _ in range(k-1):
        d = np.min(((X[:,None,:]-np.array(C)[None,:,:])**2).sum(-1), axis=1)
        p = d/ (d.sum() or 1)
        C.append(X[rng.choice(len(X), p=p)])
    C = np.array(C)
    for _ in range(iters):
        lab = np.argmin(((X[:,None,:]-C[None,:,:])**2).sum(-1), axis=1)
        new = np.array([X[lab==i].mean(0) if (lab==i).any() else C[i] for i in range(k)])
        if np.allclose(new, C): break
        C = new
    return lab, C

# ---------- ecological ground truth ----------
biomes = {r['defName']: set(x for x in (r.get('biomes_now') or '').split('|') if x) for r in rows}
known = [i for i,r in enumerate(rows) if biomes[r['defName']]]
print(f"  of those, {len(known)} carry biome assignments (the labelled test set); "
      f"{len(rows)-len(known)} are dormant")

def jaccard(a,b):
    if not a or not b: return 0.0
    return len(a&b)/len(a|b)

def eco_score(lab):
    """Mean biome-overlap of same-cluster pairs minus that of random pairs, on the labelled set.
    >0 means the grouping recovers real ecology. 0 means it is decoration."""
    rng = np.random.default_rng(7)
    same, diff = [], []
    idx = known
    for _ in range(30000):
        i, j = rng.choice(idx, 2, replace=False)
        s = jaccard(biomes[rows[i]['defName']], biomes[rows[j]['defName']])
        (same if lab[i]==lab[j] else diff).append(s)
    if not same or not diff: return 0.0, 0.0, 0.0
    return float(np.mean(same)), float(np.mean(diff)), float(np.mean(same)-np.mean(diff))

APPROACHES = {
    'A colour only':      lambda r: COLOUR(r),
    'B colour + shape':   lambda r: COLOUR(r) + SHAPE(r),
    'C shape + size':     lambda r: SHAPE(r),
}
K = int(sys.argv[1]) if len(sys.argv)>1 else 24
results = {}
for name, fn in APPROACHES.items():
    X = zscore([fn(r) for r in rows])
    lab, C = kmeans(X, K, seed=1)
    s, d, lift = eco_score(lab)
    sizes = collections.Counter(lab.tolist())
    results[name] = dict(lab=lab, lift=lift, same=s, diff=d,
                         biggest=max(sizes.values()), smallest=min(sizes.values()))
    print(f"\n{name}:  same-cluster biome overlap {s:.4f} vs random {d:.4f}  "
          f"=> LIFT {lift:+.4f}   cluster sizes {min(sizes.values())}-{max(sizes.values())}")

best = max(results, key=lambda k: results[k]['lift'])
print(f"\nbest by ecological lift: {best}")
np.save(os.path.join(FA,'cluster_labels.npy'), results[best]['lab'])
with open(os.path.join(FA,'cluster_assignments.csv'),'w',newline='',encoding='utf-8') as fh:
    w=csv.writer(fh); w.writerow(['defName','label','mod','bodySize','status','cluster','hue','sat','val','aspect','spiky'])
    for r,c in zip(rows, results[best]['lab'].tolist()):
        w.writerow([r['defName'],r['label'],r['mod'],r['bodySize'],r['status'],int(c),
                    r['hue'],r['sat'],r['val'],r['aspect'],r['spiky']])
print(f"wrote cluster_assignments.csv using {best}")

# describe each cluster of the winner
lab = results[best]['lab']
print(f"\n--- clusters under {best} ---")
for c in range(K):
    mem=[rows[i] for i in range(len(rows)) if lab[i]==c]
    if not mem: continue
    hu=np.mean([fnum(r,'hue') for r in mem]); sa=np.mean([fnum(r,'sat') for r in mem])
    va=np.mean([fnum(r,'val') for r in mem]); bs=np.median([fnum(r,'bodySize') for r in mem])
    dom=collections.Counter(r['mod'] for r in mem).most_common(1)[0]
    ex=', '.join(r['label'] or r['defName'] for r in mem[:4])
    print(f"  c{c:02d} n={len(mem):4} hue={hu:.2f} sat={sa:.2f} val={va:.2f} med_size={bs:5.2f} "
          f"| {dom[0][:22]:22} | {ex[:58]}")
