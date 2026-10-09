#!/usr/bin/env python3
"""Offline S4 scan for ARTPIPE_FACING_COHERENCE_1 (BENCH 2026-10-09). No LLM, no queueing.
Output: JSON to argv[1]. Heuristics only -> a SHORTLIST for a human look."""
import json, sys, hashlib, re, collections, os
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np
R = Path('/home/mandrake/rm/bench')
ev = []
for f in ('BENCH', 'FOUNDRY'):
    for l in open(R/f'infrastructure/state/art/events/{f}.jsonl'):
        try: ev.append(json.loads(l))
        except Exception: pass
sha_date = {}
for e in ev:
    if e['type'] == 'variant' and e.get('sha') and e.get('date'):
        sha_date[e['sha']] = min(sha_date.get(e['sha'], '9999'), e['date'])
# owner keep/redo by sha, latest ruling wins
rul = {}
for e in sorted([e for e in ev if e['type'] == 'ruling' and e.get('by') == 'owner' and e.get('trust') in ('ruled', 'interpretation')], key=lambda e: e.get('at') or e['ts']):
    t = e['target']; shas = list(t.get('shas') or []) + ([t['sha']] if t.get('sha') else [])
    for s in shas: rul[s] = (e['verdict'], e.get('subject_key'), e.get('source_file'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
    im = Image.open(p).convert('RGBA'); a = np.array(im)[..., 3] > 32
    ys, xs = np.where(a)
    if not len(ys): return None
    box = (xs.min(), ys.min(), xs.max()+1, ys.max()+1)
    c = im.crop(box).convert('L').resize((48, 48))
    m = Image.fromarray((a[box[1]:box[3], box[0]:box[2]]*255).astype('uint8')).resize((48, 48))
    return np.array(c, float), np.array(m) > 127
def corr(a, b):
    a = a - a.mean(); b = b - b.mean(); d = np.sqrt((a*a).sum()*(b*b).sum())
    return float((a*b).sum()/d) if d else 0.0
def iou(a, b): return float((a & b).sum()/max(1, (a | b).sum()))
sets = collections.defaultdict(dict)
for p in R.glob('src/**/Textures/**/*_north.png'):
    sets[str(p)[:-10]]['north'] = p
for stem in list(sets):
    for f in ('south', 'east', 'west'):
        q = Path(f'{stem}_{f}.png')
        if q.exists(): sets[stem][f] = q
out = []
for stem, d in sets.items():
    if not {'north', 'south', 'east'} <= set(d): continue
    try:
        im = {k: load(v) for k, v in d.items()}
        sh = {k: sha(v) for k, v in d.items()}
    except Exception as ex:
        out.append(dict(stem=stem, error=str(ex))); continue
    if any(v is None for v in im.values()): out.append(dict(stem=stem, error='empty facing')); continue
    dates = [sha_date.get(sh[k]) for k in ('north', 'south', 'east')]
    gen = max(x for x in dates if x) if all(dates) else None
    rows = []
    # side-profile-clone: north ~ east (direct) or mirrored; north ~ south dup
    ne = max(corr(im['north'][0], im['east'][0]), corr(im['north'][0], im['east'][0][:, ::-1]))
    nei = max(iou(im['north'][1], im['east'][1]), iou(im['north'][1], im['east'][1][:, ::-1]))
    ns = corr(im['north'][0], im['south'][0]); nsi = iou(im['north'][1], im['south'][1])
    flags = []
    if sh['north'] == sh['south']: flags.append('N==S bytes')
    if sh['north'] == sh['east']: flags.append('N==E bytes')
    if sh['south'] == sh['east']: flags.append('S==E bytes')
    if ne > 0.93 and nei > 0.93: flags.append(f'N~E clone corr={ne:.2f} iou={nei:.2f}')
    if ns > 0.93 and nsi > 0.93: flags.append(f'N~S clone corr={ns:.2f} iou={nsi:.2f}')
    pre = bool(gen and gen < '2026-09-14')
    verd = {rul[sh[k]][0] for k in sh if sh[k] in rul}
    keep = [rul[sh[k]] for k in sh if sh[k] in rul and rul[sh[k]][0] == 'keep']
    out.append(dict(stem=str(Path(stem).relative_to(R)), gen=gen, pre_stamp=pre, undated=gen is None, flags=flags,
                    ne=round(ne, 3), ns=round(ns, 3), verdicts=sorted(verd), keep_src=sorted({k[2] for k in keep if k[2]})[:2]))
json.dump(out, open(sys.argv[1], 'w'), indent=0)
print(len(out), 'sets')
