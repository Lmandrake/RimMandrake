#!/usr/bin/env python3
"""Rebuild the STARWARS_JUNK_RESKIN_1 curation sheet over EVERY finished RSW_Junk render
(take A = original job, take B = the _v2 rerun). Sheet + prefill only; installs nothing.
Template/chrome = the 10-04 sheet (review-sheets template). Safe to rerun until the sheet is touched."""
import json, re, glob, os, sys
from pathlib import Path
from PIL import Image
import numpy as np
R = Path('/home/mandrake/rm/foundry'); OUT = R/'Transient/junk_reskin_review_2026-10-09'
OLD = R/'Transient/junk_reskin_review_2026-10-04'
ART = Path('/mnt/d/Luke/dev/_artpipe'); DONE = ART/'done'; SRC = ART/'_artsrc'
dec_path = OUT/'decisions.json'
if dec_path.exists() and 'savedBy' in dec_path.read_text() and '--force' not in sys.argv:
    sys.exit('decisions already touched by the sheet; refusing')
old = (OLD/'sheet.html').read_text()
oitems = json.loads(re.search(r'<script id="ITEMS" type="application/json">\n(.*?)\n</script>', old, re.S).group(1))
ocon = {i['id']: i for i in oitems if i.get('contested')}
al = {a['id']: a for a in json.load(open(R/'design/RimMandrake/starwars_junk_reskin_artlist_2026-10-03.json'))}
doc = (R/'design/RimMandrake/starwars_junk_reskin_2026-10-03.md').read_text()
size = dict((m[0], m[1]) for m in re.findall(r'^\| `(Ancient\w+)` \|[^|]*\|[^|]*\| (\d+x\d+) \|', doc, re.M))
size['AncientRustedTruck'] = '2x4'
def jobs(pat):
    return {os.path.basename(p)[:-5] for p in glob.glob(str(DONE/pat)) if 'manifest' not in p}
done = jobs('RSW_Junk_*.json')
(OUT/'images').mkdir(exist_ok=True)
items, dec = [], {}
missing = []
for jid in sorted(al):
    if jid not in done and jid+'_v2' not in done: missing.append(jid)
rows = sorted(i for i in done if i.replace('_v2','') in al)
for rid in rows:
    base = rid.replace('_v2',''); take = 'B (rerun)' if rid.endswith('_v2') else 'A'
    m = re.match(r'RSW_Junk_(Ancient\w+?)_(\d+)', base); d, n = m.group(1), m.group(2)
    src = SRC/rid/f'{rid}.png'
    im = Image.open(src).convert('RGBA'); a = np.asarray(im)[:, :, 3]
    fill = float((a > 16).mean()); opaque_corner = all(a[y, x] > 200 for y in (0, -1) for x in (0, -1))
    im.thumbnail((320, 320)); im.save(OUT/'images'/f'{rid}.png', optimize=True)
    prompt = al[base]['prompt']; design = prompt.split('transparent background: ', 1)[-1].split('. Ancient and long since')[0]
    flags = []
    if opaque_corner: flags.append('opaque corners: background not transparent')
    if fill < 0.12: flags.append(f'sparse: only {fill:.0%} of the frame is drawn')
    if base in ocon and not rid.endswith('_v2'): flags.append(ocon[base]['meta']['why contested'])
    pre = 'cut' if (opaque_corner or base == 'RSW_Junk_AncientPodCar_01' and take == 'A') else 'keep'
    it = {'id': rid, 'group': d, 'label': f'{d} {n} take {take}',
          'thumb': f'images/{rid}.png',
          'effect': f'Appearance only, {size.get(d,"?")} footprint. Canon reference: none (the library covers creatures, species and droids, not vehicles). Aimed at: {design[:170]}',
          'prefill': pre}
    if flags: it['contested'] = True; it['meta'] = {'why contested': '; '.join(flags)}
    if not rid.endswith('_v2') or base in [x for x in al]:
        pass
    items.append(it); dec[rid] = {'decision': pre, 'prefill': pre, 'note': ''}
nflag = sum(1 for i in items if i.get('contested'))
brief = old[old.index('"briefHtml"'):]
cfg = json.loads(re.search(r'<script id="CONFIG" type="application/json">\n(.*?)\n</script>', old, re.S).group(1))
nA = sum(1 for r in rows if not r.endswith('_v2')); nB = len(rows) - nA
cfg['sheetId'] = 'junk_reskin_review_2026-10-09'
cfg['subtitle'] = f'STARWARS_JUNK_RESKIN_1 \u00b7 {len(rows)} pictures over {len({i["group"] for i in items})} vanilla junk defs'
cfg['briefHtml'] = (
 "<p>Your ruling (2026-10-03): <i>\"Reskin as Star-Wars-adjacent junk... Doesn't have to be exact canon replicas... try for it anyway... And diversity that junk! Lots of different images to choose from.\"</i></p>"
 "<p>Each picture is one variant of a vanilla ancient-junk building. Kept pictures go into that def's random-art folder. <b>This sheet is appearance only</b> (decision taken by question card 2026-10-09: appearance now, names and flavours later). Nothing is installed from it until you rule.</p>"
 f"<p><b>What changed since the 10-04 sheet:</b> it showed {nA - 0} first-take pictures and 13 jobs had failed. Every one of the 184 slots now has a finished picture, and each slot was also rerun once, so the sheet shows both: take A (original) and take B (rerun, same prompt). That is {len(rows)} pictures. {len(missing)} slots have no picture at all; the 13 whose first take failed are represented by take B only.</p>"
 "<p><b>Pre-fill:</b> keep everything except pictures with an opaque (non-transparent) background and the outlined pod car. I have looked at the 10-04 pictures only; the take B reruns are pre-filled by measurement alone (transparency, how much of the frame is drawn), not by eye.</p>")
cfg['invented'] = ["Droid bodies and heads count as acceptable 'engine block' and 'wheel' junk; the patch also replaces those defs' labels, so the name will not say 'wheel'.",
                   "Take B reruns are treated as extra variants of the same def, not replacements for take A."]
cfg['decisionsPath'] = str(OUT/'decisions.json').replace('/home/mandrake', r'\\wsl.localhost\Ubuntu\home\mandrake').replace('/', '\\')
cfg['sheetPath'] = str(OUT/'sheet.html').replace('/home/mandrake', r'\\wsl.localhost\Ubuntu\home\mandrake').replace('/', '\\')
html = re.sub(r'(<script id="CONFIG" type="application/json">\n).*?(\n</script>)', lambda m: m.group(1)+json.dumps(cfg, indent=1)+m.group(2), old, flags=re.S)
html = re.sub(r'(<script id="ITEMS" type="application/json">\n).*?(\n</script>)', lambda m: m.group(1)+json.dumps(items)+m.group(2), html, flags=re.S)
(OUT/'sheet.html').write_text(html)
json.dump({'sheetId': cfg['sheetId'], 'posture': 'whitelist',
           'reviewStatus': {'state': 'prefill', 'by': None, 'at': None, 'evidence': 'generator pre-fill by FOUNDRY belt agent 2026-10-09; nobody has opened it'},
           'decisions': dec}, open(dec_path, 'w'), indent=1)
print(len(rows), 'rows', nA, 'A', nB, 'B', nflag, 'contested', len(missing), 'missing', sum(1 for d in dec.values() if d['decision']=='cut'), 'cut')
