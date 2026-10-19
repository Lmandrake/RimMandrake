"""Census of which review-sheet controls the owner actually sets. Read-only."""
import json, glob, collections, sys, os, re
ROOT = '/home/mandrake/rm/foundry/Transient'
files = [f for f in glob.glob(ROOT + '/**/*.decisions.json', recursive=True)
         if 'decisions_snapshot_' not in f and 'premigration' not in f and '.gate.tmp' not in f and '.bak' not in f]
keyc = collections.Counter(); slotstate = collections.Counter(); asks = collections.Counter()
c = collections.Counter(); assign_vals = collections.Counter(); qvals = collections.Counter()
notes = []; per_sheet = []
def walk(prefix, v):
    if isinstance(v, dict):
        for k, x in v.items():
            if prefix.endswith('slots') or prefix.endswith('pool') or prefix.endswith('assign') or prefix.endswith('setIds') or prefix.endswith('reject') or prefix.endswith('retire'):
                walk(prefix + '.*', x)
            else:
                walk(prefix + '.' + k, x)
    else:
        nonempty = v not in (None, '', [], {}, False)
        keyc[(prefix, nonempty)] += 1
for f in files:
    try: d = json.load(open(f))
    except Exception as e: print('BAD', f, e, file=sys.stderr); continue
    dec = d.get('decisions')
    if not isinstance(dec, dict): continue
    rows = touched = 0
    for k, r in dec.items():
        if not isinstance(r, dict): continue
        rows += 1
        walk('row', r)
        human = bool(r.get('decidedAt') or r.get('at'))
        if human: touched += 1
        c['rows'] += 1; c['rows_touched'] += human
        n = (r.get('note') or '').strip()
        if n: c['note'] += 1; notes.append((os.path.basename(f), k, n))
        for gk, s in (r.get('slots') or {}).items():
            if isinstance(s, dict): slotstate[s.get('state')] += 1
        for gk, p in (r.get('pool') or {}).items():
            if p.get('add'): c['pool_add'] += 1
            if p.get('remove'): c['pool_remove'] += 1
        if any((r.get('reject') or {}).values()) if isinstance(r.get('reject'), dict) else r.get('reject'): c['reject'] += 1
        if any((r.get('retire') or {}).values()) if isinstance(r.get('retire'), dict) else r.get('retire'): c['retire'] += 1
        for L, v in (r.get('assign') or r.get('assigned') or {}).items():
            assign_vals['not_needed' if v == 'not_needed' else ('slot' if v else 'blank')] += 1
        for ak, av in (r.get('asks') or {}).items():
            if av not in (None, '', [], {}, False): asks[ak] += 1
        for qk, qv in (r.get('q') or {}).items(): qvals[(qk, qv)] += 1
        if r.get('legacyConfirm') or r.get('legacy'): c['legacy_answer'] += 1
        if r.get('decision') and r.get('prefill') and r['decision'] != r['prefill']: c['decision_differs_from_prefill'] += 1
        if r.get('decision') and r.get('prefill') and r['decision'] == r['prefill']: c['decision_equals_prefill'] += 1
        if 'cut' in str(r.get('decision', '')).lower(): c['decision_cut'] += 1
        if n and not r.get('decision') and not any(isinstance(s, dict) and s.get('state') for s in (r.get('slots') or {}).values()): c['note_only_row'] += 1
    per_sheet.append((os.path.relpath(f, ROOT), rows, touched))
out = sys.argv[1]
with open(out, 'w') as o:
    print(f'files {len(files)}', file=o)
    print('counts', dict(c), file=o)
    print('slot states', dict(slotstate), file=o)
    print('asks (Requests panel) non-empty', dict(asks), file=o)
    print('this-is assign values', dict(assign_vals), file=o)
    print('question answers', dict(qvals), file=o)
    print('\nfield census (path, nonempty) -> n', file=o)
    for (p, ne), n in sorted(keyc.items()): print(f'  {p:60s} {"SET" if ne else "empty"} {n}', file=o)
    print('\nper sheet rows/touched', file=o)
    for s in sorted(per_sheet): print('  ', *s, file=o)
    print('\nNOTES', len(notes), file=o)
    for s, k, n in notes: print(f'  [{s}] {k}: {n[:300]}', file=o)
print(out)
