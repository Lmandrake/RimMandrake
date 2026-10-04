#!/usr/bin/env python3
"""Summarise census_summary.jsonl -> Transient/art_census_desert_2026-10-04.md + contact sheet index.html."""
import json, re, html, collections, sys
from pathlib import Path
R = Path('/home/mandrake/rm/bench'); T = R/'Transient'
SP = Path('/tmp/claude-1000/-home-mandrake-rm-bench/7ed5ddfd-542a-4415-93da-a0a2b9afe519/scratchpad')
SID = 'art_census_desert_2026-10-04'; OUT = T/SID
S = [json.loads(l) for l in open(SP/'census_summary.jsonl')]
ITEMS = {i['id']: i for i in json.load(open(SP/'items.json'))}
D103 = json.load(open(T/'desert_art_review_2026-10-03.decisions.json'))['decisions']
ARTF = re.compile(r'art|legib|toyfig|canon|keyline|misroute|identity|pyrelands')
KEEP = {'keep', 'approve', 'good', 'adopt-b', 'works', 'ok', 'better', 'right'}
def ham(a, b): return sum(x != y for x, y in zip(a, b)) if a and b else 999
def fshort(f): p = f.split('/'); return p[-2] if p[-1] in ('decisions.json', 'sheet.decisions.json') else p[-1].replace('.decisions.json', '')

rows = []
for s in S:
    it = ITEMS[s['rid']]; V = s['V']
    live = [v for v in V if v['source'] == 'repo-current' and v.get('live_repo') == 'y']
    livedep = [v for v in V if v.get('live_dep') == 'y']
    donors = [v for v in V if v['source'].startswith('donor')]
    def kind(v):
        if v.get('mod', '').endswith('ArtOverride'): return 'own (ArtOverride mod)'
        d = min((ham(v.get('hash'), x.get('hash')) for x in donors), default=999)
        if d <= 10: return f'donor copy (dist {d})'
        return 'own/regenerated' if d < 999 else 'unknown (no donor to compare)'
    live_kind = sorted({kind(v) for v in live})
    arts = [r for r in s['RUL'] if ARTF.search(r['file']) and 'desert_art_review_2026-10-03' not in r['file']]
    kept = [r for r in arts if r['decision'] in KEEP and r['review'] != 'prefill' and 'desert_art_verdict' not in r['file']]
    differs = [v for v in V if 'DIFFERS' in v['source'] or 'no repo twin' in v['source']]
    overw = [v for v in V if v['source'].startswith('git-history')]
    jobsets = [v for v in V if v.get('jobset')]
    other_jobs = [v for v in jobsets if not re.match(r'(desert_swaca_|desertportb_)', v['jobset'])]
    canon_y = [v for v in other_jobs if str(v.get('canon', '')).startswith('y')]
    d = D103.get(s['rid'], {})
    cur_tag = it['meta'].get('currentTag', '')
    rows.append(dict(s=s, it=it, live=live, livedep=livedep, live_kind=live_kind, kept=kept, arts=arts, differs=differs,
                     overw=overw, other_jobs=other_jobs, canon_y=canon_y, d103=d, dess='dessicated' in cur_tag.lower(), cur_tag=cur_tag))

# ---------- headline sets ----------
own_live = [r for r in rows if any(k.startswith('own') for k in r['live_kind'])]
dess = [r for r in rows if r['dess']]
dess_own = [r for r in dess if any(k.startswith('own') for k in r['live_kind'])]
would_replace_kept = [r for r in rows if r['kept'] and r['d103'].get('decision') == 'keep' and any(k.startswith('own') for k in r['live_kind'])]
kept_then_overwritten = []
for r in rows:
    if not r['kept'] or not r['overw']: continue
    kept_then_overwritten.append(r)
alt_better = [r for r in rows if r['other_jobs'] or any(k.startswith('own') for k in r['live_kind'])]
nv = sum(len(r['s']['V']) for r in rows)
src_ct = collections.Counter(v['source'].split(' ')[0] for r in rows for v in r['s']['V'])

L = []
A = L.append
A('# Desert-family art version census, 2026-10-04 (ART_VERSION_WRANGLING_1)\n')
A(f'Rows: **{len(rows)}** (92 creatures, 17 plants) from `Transient/desert_art_review_2026-10-03.html`. Variants found: **{nv}** '
  f'({", ".join(f"{k} {v}" for k, v in src_ct.most_common())}). One row per variant in `Transient/{SID}.csv`; '
  f'every variant side by side in `Transient/{SID}/index.html` (thumbnails 256px). Builder: `Transient/art_census_desert_build_2026-10-04.py` + `Transient/art_census_desert_report_2026-10-04.py`.\n')
A('## Headline\n')
A(f'1. **The 2026-10-03 sheet\'s "current art" column was the CORPSE texture for {len(dess)} of {len(rows)} rows.** Its builder took the *last* `texPath` in the def, '
  'which is `dessicatedBodyGraphicData` (`..._Dessicated`) - the skeleton. That is the "crude skeletons" the owner saw. '
  f'For **{len(dess_own)}** of those rows the live art is actually our own regenerated/approved art (an ArtOverride mod or a wired artpipe render), which the sheet never showed.')
kc = collections.Counter(('own' if any(k.startswith('own') for k in r['live_kind']) else ('donor copy' if any(k.startswith('donor') for k in r['live_kind']) else ('unknown' if r['live_kind'] else 'no live texture resolved'))) for r in rows)
A(f'2. **{len(own_live)} rows already have own (non-donor) art live in the repo.** Live-art kind across all rows: ' + ', '.join(f'{k} {v}' for k, v in kc.most_common()) + ' (donor copy = live PNG hash-matches the donor sprite, mostly mlie SWAC ported by MLIE_FAUNA_ABSORPTION_1; unknown = no donor art found to compare).')
A(f'3. **{len(would_replace_kept)} rows where the owner previously KEPT art (earlier review sheet) and the 2026-10-03 "Keep render" would now REPLACE that live own art** with the uninformed desert_swaca/desertportb render: '
  + ', '.join(r['it']['label'].split(' [')[0] for r in would_replace_kept) + '. Do not wire these without a side-by-side.')
A(f'4. **{len(kept_then_overwritten)} rows where owner-kept art exists AND the live path was overwritten by later commits** (timelines below) - this is "older art I liked being replaced".')
A('5. **The desert renders were not canon-informed.** Every `desert_swaca_*` / `desertportb_*` job (DESERT_FAMILY_PORT_EXECUTION_1, 2026-09-20) has `reference: null`, a generic prompt (Wookieepedia one-liner + "painterly game-art style") and style note "our own art (not the donor mod\'s)" - no canon-library brief, no `## Must show`, no biome context. '
  'Compare PYRELANDS_CREATURE_RERENDER_1 / ART_REGEN_WAVE4 / canon_regen jobs, which cite the canon library or the owner\'s identity rulings.')
nd = sum(1 for r in rows if r['differs'])
A(f'6. **Repo vs deployed:** {nd} rows have a deployed texture that differs from the repo or has no repo twin; every matched texture in the game Mods folder is byte-identical to its repo file (MD5). Rows whose def texPaths differ between the repo def and the deployed def: '
  + (', '.join(r['s']['rid'] for r in rows if r['s']['live_rp'] != r['s']['live_dp']) or 'none') + '.\n')
A('Method caveats: "live" = file at the def\'s texPath in the latest-loading active mod (ModsConfig order); variants matched by name tokens of donor name, ported defName and render job, so a renamed set under an unrelated name can be missed. '
  '`likely_from_job` is a 16x16 average-hash nearest neighbour (<=20/256), a hint not provenance. "owner ruling" lists every decisions file ever committed (incl. deleted) whose key matches; prefill-state files are agent guesses, not his. '
  'Droids (7), Rat and three vanilla-art plants have no variants: Outer Rim droid art is bundled under names this pass did not resolve.\n')

def tl(r):
    out = []
    for k in r['kept']:
        out.append(f"  - owner {k['decision']} in `{fshort(k['file'])}` key `{k['key']}`" + (f" @ {k['at'][:10]}" if k['at'] else '') + (f" - \"{k['note'][:160]}\"" if k['note'] else ''))
    for v in sorted(r['overw'], key=lambda v: v['date']):
        out.append(f"  - {v['date']} {v['source']}: `{v['path'].split('/Textures/')[-1]}` <- {v['origin'][:140]}")
    for v in r['live']:
        out.append(f"  - LIVE now: `{v['path']}` ({v['date']}, {v['origin'][:90]}) [{', '.join(r['live_kind'])}]")
    if r['d103']:
        out.append(f"  - 2026-10-03 sheet: **{r['d103'].get('decision')}**" + (f" - \"{r['d103'].get('note', '')[:160]}\"" if r['d103'].get('note') else ''))
    return '\n'.join(out)

A('## Owner-kept art later overwritten, or about to be (worst first)\n')
for r in sorted(kept_then_overwritten, key=lambda r: -(len(r['overw']) + 3*(r in would_replace_kept))):
    A(f"- **{r['it']['label']}**" + (' - WOULD BE REPLACED AGAIN by the 10-03 keep' if r in would_replace_kept else ''))
    A(tl(r))
A('')
A('## Rows whose best candidate is probably NOT the desert render\n')
A('Provenance only (owner-kept, canon-informed, or own art already live) - eyes decide, on the contact sheet.\n')
A('| row | live art | other render sets | canon-informed sets | owner earlier kept | 10-03 decision |')
A('|---|---|---|---|---|---|')
for r in alt_better:
    A(f"| {r['it']['label']} | {'; '.join(r['live_kind']) or '-'} | {len(r['other_jobs'])}: {', '.join(v['jobset'] for v in r['other_jobs'][:5])} | {len(r['canon_y'])} | "
      f"{'; '.join(sorted({fshort(k['file']) for k in r['kept']})) or '-'} | {r['d103'].get('decision', '-')} |")
A('')
A('## Per row\n')
A('| row | variants | repo-current | git versions | artpipe sets | donor | live (repo) | deployed differs | sheet showed corpse | owner art rulings (earlier) |')
A('|---|---|---|---|---|---|---|---|---|---|')
for r in rows:
    c = collections.Counter(v['source'].split(' ')[0] for v in r['s']['V'])
    A(f"| {r['it']['label']} | {len(r['s']['V'])} | {c['repo-current']} | {c['git-history']} | {c['artpipe']} | {c['donor-loose'] + c['donor-bundle']} | "
      f"{'; '.join(r['live_kind']) or 'none resolved'} | {len(r['differs'])} | {'YES' if r['dess'] else ''} | "
      f"{'; '.join(sorted({fshort(k['file']) + '=' + k['decision'] for k in r['arts']}))[:200]} |")
(T/(SID + '.md')).write_text('\n'.join(L) + '\n')

# ---------- contact sheet ----------
H = ['<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Desert art versions</title><style>',
     ':root{--bg:#211a14;--fg:#eadbc8;--dim:#a8957e;--card:#2d241c;--live:#6fcf7f;--kept:#e8b64c;--warn:#e07a5f}',
     'body{background:var(--bg);color:var(--fg);font:13px system-ui,sans-serif;margin:0;padding:16px}h2{margin:22px 0 4px;font-size:16px}',
     '.row{display:flex;flex-wrap:wrap;gap:8px}.v{background:var(--card);border:2px solid #3b3026;border-radius:6px;width:180px;padding:4px;font-size:10.5px;color:var(--dim)}',
     '.v img{width:172px;height:172px;object-fit:contain;background:#4a4038;display:block;image-rendering:auto}.v b{color:var(--fg)}',
     '.live{border-color:var(--live)}.kept{box-shadow:0 0 0 2px var(--kept)}.dess{color:var(--warn)}.tag{display:inline-block;padding:0 4px;border-radius:3px;margin:1px;background:#3b3026}',
     '.tl{color:var(--live)}.tk{color:var(--kept)}</style></head><body>',
     '<h1>Desert-family art: every version, side by side</h1><p>Green frame = live in repo def now. Gold glow = an earlier owner keep/approve names this job set. '
     'Order per creature: live repo files, deployed-only, git history (overwritten / deleted), artpipe job sets, donor art, canon-library reference. Source: ART_VERSION_WRANGLING_1, 2026-10-04.</p>']
for r in rows:
    s = r['s']
    keptsets = {k['key'].lower() for k in r['kept']}
    H.append(f"<h2 id='{s['rid']}'>{html.escape(r['it']['label'])} <span class='tag'>10-03: {html.escape(r['d103'].get('decision', '-'))}</span>"
             + (" <span class='tag dess'>sheet showed corpse texture</span>" if r['dess'] else '') + '</h2><div class="row">')
    for v in s['V']:
        cls = 'v' + (' live' if v.get('live_repo') == 'y' else '') + (' kept' if v.get('jobset') and any(k.startswith(v['jobset'].lower()) for k in keptsets) else '')
        img = f"<img loading='lazy' src='{html.escape(v['thumb'])}'>" if v.get('thumb') else "<div style='height:172px;display:flex;align-items:center;justify-content:center'>no image on disk</div>"
        p = v['path'].split('/Textures/')[-1].split('/_artsrc/')[-1]
        H.append(f"<div class='{cls}'>{img}<b>{html.escape(v['source'])}</b><br>{html.escape(v['date'])} {html.escape(p[-70:])}<br>{html.escape(v['origin'][:110])}"
                 + (f"<br><span class='tl'>live repo:{v.get('live_repo')} dep:{v.get('live_dep')}</span>" if v.get('live_repo') not in ('', 'n') or v.get('live_dep') not in ('', 'n', None) else '')
                 + (f"<br>canon: {html.escape(str(v.get('canon')))}" if v.get('canon') else '')
                 + ''.join(f"<br><span class='tk'>{html.escape(fshort(x['file']))}: {html.escape(x['decision'])}</span>" for x in v.get('rul', [])[:2]) + '</div>')
    H.append('</div>')
H.append('</body></html>')
(OUT/'index.html').write_text('\n'.join(H))
print('rows', len(rows), 'variants', nv, 'dess', len(dess), 'dess_own', len(dess_own), 'own_live', len(own_live), 'would_replace_kept', len(would_replace_kept),
      'kept_overwritten', len(kept_then_overwritten), 'alt', len(alt_better), 'differs', nd)
print([r['s']['rid'] for r in would_replace_kept])
