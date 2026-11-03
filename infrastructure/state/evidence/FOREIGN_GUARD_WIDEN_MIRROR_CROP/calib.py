# Frozen copy from D:\ClaudeWork\rimmandrake\guard_vet\mirrorcrop; it reads thumbs2.pkl and artpipe\done there. Judged offline by check_calib.py.
# Census calibration of FOREIGN_GUARD_WIDEN_MIRROR_CROP: which pairs do the NEW transforms (mirror of the
# placed file; centre square of a non-square candidate) bring inside FOREIGN_NEAR that the plain check did
# not, and which of those survive detail confirmation (= would now be refused)?
import sys, pickle, json
from pathlib import Path
import numpy as np
sys.path.insert(0, '/home/mandrake/rm/relentless/clones/FOREIGN_GUARD_WIDEN_MIRROR_CROP/skills/generating-images/scripts')
import codex_image as ci
D = Path('/mnt/d/ClaudeWork/rimmandrake/artpipe/done')
def info(i):
    s = m = {}
    try: s = json.loads((D / f'{i}.json').read_text())
    except Exception: pass
    try: m = json.loads((D / f'{i}.manifest.json').read_text())
    except Exception: pass
    return {'spec': bool(s), 'channel': s.get('channel') or m.get('channel'), 'mode': m.get('mode'),
            'ref': s.get('reference'), 'source_file': s.get('source_file')}
def gen(x): return x['spec'] and not x['source_file'] and x['mode'] == 'generate' and not x['ref'] and x['channel'] == 'codex'

data = pickle.loads(Path(__file__).with_name('thumbs2.pkl').read_bytes())
items = [(p,) + v for p, v in data.items() if v and v[3] is not None]
outs = [it for it in items if it[1] == 'out']
print('items', len(items), 'outputs', len(outs), 'cache', len(items) - len(outs),
      'non-square', sum(it[5] is not None for it in items))
A = lambda b: np.frombuffer(b, np.uint8).astype(np.int16)
# candidate variants: (item index, centre?)
cv, cvec = [], []
for j, it in enumerate(items):
    cv.append((j, False)); cvec.append(A(it[4]))
    if it[5] is not None:
        cv.append((j, True)); cvec.append(A(it[5]))
C = np.stack(cvec)
oidx = [j for j, it in enumerate(items) if it[1] == 'out']
hits = []   # (q, cand j, mirrored, centre, d)
for q in oidx:
    t = items[q][4]
    P = A(t); M = A(ci._mirror_thumb(t))
    dp = np.abs(C - P).mean(1); dm = np.abs(C - M).mean(1)
    plain_near = {cv[k][0] for k in np.nonzero(dp <= ci.FOREIGN_NEAR)[0] if not cv[k][1]}
    for arr, mir in ((dp, False), (dm, True)):
        for k in np.nonzero(arr <= ci.FOREIGN_NEAR)[0]:
            j, cen = cv[k]
            if j == q or (not mir and not cen) or j in plain_near:
                continue
            hits.append((q, j, mir, cen, float(arr[k])))
# one row per (q, j): best transform
best = {}
for h in hits:
    k = (h[0], h[1])
    if k not in best or h[4] < best[k][4]: best[k] = h
print('new coarse pairs', len(best), ' mirror', sum(h[2] and not h[3] for h in best.values()),
      ' centre', sum(h[3] and not h[2] for h in best.values()), ' both', sum(h[2] and h[3] for h in best.values()))
rows = []
for (q, j), h in sorted(best.items(), key=lambda kv: kv[1][4]):
    qp, cp = Path(items[q][0]), Path(items[j][0])
    dq = ci._detail(qp)
    if dq is not None and h[2]: dq = ci._mirror_grid(dq, ci.FOREIGN_DETAIL_N, 1)
    dc = ci._detail(cp, centre=h[3])
    c = ci._detail_corr(dq, dc) if dq is not None and dc is not None else None
    refused = c is None or c >= ci.FOREIGN_DETAIL_CORR
    kind = items[j][1]
    indep = gen(info(qp.stem)) and (kind == 'out' and gen(info(cp.stem)))
    rows.append((h[4], c, refused, h[2], h[3], kind, indep, items[j][3] - items[q][3], qp.stem, str(cp)))
with open(Path(__file__).with_name('calib.tsv'), 'w') as f:
    f.write('dist\tdetail_corr\twould_refuse\tmirrored\tcentre\tcand_kind\tboth_independent_generate\tcand_minus_out_mtime_s\toutput\tcandidate\n')
    for r in rows: f.write('\t'.join(map(str, r)) + '\n')
ref = [r for r in rows if r[2]]
print('survive detail (would refuse):', len(ref), ' of which both-independent:', sum(r[6] for r in ref))
cs = sorted(r[1] for r in rows if r[1] is not None)
print('detail corr of new coarse pairs: n=%d max=%.2f  >=0.3: %d  >=0.5: %d' % (len(cs), cs[-1] if cs else 0, sum(c >= .3 for c in cs), sum(c >= .5 for c in cs)))
for r in ref[:40]: print('  %.2f corr=%s mir=%s cen=%s %s indep=%s dt=%.0fs %s <- %s' % (r[0], None if r[1] is None else round(r[1], 2), r[3], r[4], r[5], r[6], r[7], r[8], r[9]))
