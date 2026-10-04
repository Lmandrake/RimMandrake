#!/usr/bin/env python3
"""Builds Transient/desert_art_review_2026-10-03.html (DESERT_FAMILY_PORT_EXECUTION_1 fresh art sheet).
Regenerating the SHEET is safe; the decisions file is only created if absent (never overwritten)."""
import re, json, glob, collections, sys, os
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image

R = Path('/home/mandrake/rm/bench')
T = R/'Transient'
SID = 'desert_art_review_2026-10-03'
AS = T/SID
ART = Path('/mnt/d/Luke/dev/_artpipe')
TPL = Path.home()/'.claude/skills/review-sheets/assets/sheet_template.html'
OLD = T/'desert_family_review_2026-09-20.html'
THUMBS = T/'desert_family_review_thumbs_2026-09-20'
AS.mkdir(exist_ok=True)

h = OLD.read_text()
rows = json.loads([m.group(1) for m in re.finditer(r'<script id="ITEMS"[^>]*>(.*?)</script>', h, re.S) if m.group(1).strip().startswith('[')][0])
rowby = {r['id']: r for r in rows}

# ---- render groups from done jobs of this item
groups = collections.defaultdict(dict)
for f in glob.glob(str(ART/'done/*.json')):
    if f.endswith('manifest.json'): continue
    d = json.load(open(f))
    if d.get('rimflow_item_id') != 'DESERT_FAMILY_PORT_EXECUTION_1': continue
    m = re.match(r'(.*)_(east|north|south)$', d['id'])
    if m: groups[m.group(1)][m.group(2)] = d['id']
    else: groups[d['id']]['single'] = d['id']
low = {g.lower(): g for g in groups}
cen = (T/'desert_art_census.md').read_text()
aa = {m.group(2).lower(): m.group(1) for m in re.finditer(r'\| `(RSW_\w+)` \| `[^`]*?(AA_\w+)/', cen)}

# pairings made by reading descriptions (renamed ports) -- flagged on the sheet as inferred
PAIR = {
 'A_Terrorworm':'RSW_Ashworm','A_VFEI2_Fuelmite':'RSW_Cindermite','A_AA_BoulderMit':'RSW_Korrum',
 'P_RG_Plant_CrimsonCushion':'RSW_EmberCarpet','P_RG_Plant_CreepStern':'RSW_Starvine',
 'P_AB_Aaklac':'RSW_VellaraBloom','P_AB_DessertTree':'RSW_SweetbarkTree','P_RG_Plant_Dervish':'RSW_Whirlbloom',
 'P_Plant_HealrootWild':'rut_wildhealroot','P_AB_HardyGrass':'RSW_Dunegrass','P_RG_Plant_AridGrass':'RSW_Scrubgrass',
 'P_Plant_Brambles':'rut_grellspine','P_Plant_Bush':'rut_grellbush',
}
mp, ported, inferred = {}, {}, set()
for r in rows:
    rid = r['id']; n = rid[2:]; nl = n.lower()
    if rid in PAIR:
        mp[rid] = PAIR[rid]; inferred.add(rid); continue
    cands = []
    if nl in aa: cands.append(aa[nl].lower())
    base = re.sub(r'^(rsw_|aa_|joe_|rg_|ab_|plant_)', '', nl)
    for b in {nl, base, re.sub(r'^rsw_', '', nl)}:
        cands += ['desert_swaca_'+b, 'desertportb_'+b, 'rsw_'+b, 'rut_'+b, 'desertportb_plant_'+b]
    for c in cands:
        if c in low: mp[rid] = low[c]; break
    if nl in aa: ported[rid] = aa[nl]
    else: ported[rid] = n if n.startswith(('RSW_','JOE_','RUT_')) else ('RSW_'+n)
for rid, g in PAIR.items():
    ported[rid] = g

sys.path.insert(0, str(R/'src/RimMandrake/Utils'))
import pickle
from animal_contact_sheet import resolve_texture, TextureIndex, load_bundle_index
TEXIDX = TextureIndex(pickle.load(open('/tmp/claude-1000/-home-mandrake-rm-bench/7ed5ddfd-542a-4415-93da-a0a2b9afe519/scratchpad/texidx.pkl','rb')))
BUNDLES, _nb = load_bundle_index('/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures')
print('bundle entries', _nb, flush=True)
DONOR_DEFS = json.load(open('/tmp/claude-1000/-home-mandrake-rm-bench/7ed5ddfd-542a-4415-93da-a0a2b9afe519/scratchpad/donor_defs.json')) if os.path.isfile('/tmp/claude-1000/-home-mandrake-rm-bench/7ed5ddfd-542a-4415-93da-a0a2b9afe519/scratchpad/donor_defs.json') else {}
AAMAP = {}
for x in (R/'src/RimStarWars/SWBestiary/Defs').rglob('*.xml'):
    for m in re.finditer(r'Alpha Animals (AA_\w+) -> (RSW_\w+)', x.read_text(errors='ignore')): AAMAP['A_'+m.group(1)] = m.group(2)
for k, v in AAMAP.items():
    if k in rowby: ported[k] = v
# ---- our own def texPaths
defs_tex = collections.defaultdict(list)
EXTRA_XML = json.load(open('/tmp/claude-1000/-home-mandrake-rm-bench/7ed5ddfd-542a-4415-93da-a0a2b9afe519/scratchpad/donorfiles.json')) if os.path.isfile('/tmp/claude-1000/-home-mandrake-rm-bench/7ed5ddfd-542a-4415-93da-a0a2b9afe519/scratchpad/donorfiles.json') else []
for p in list((R/'src/RimStarWars/SWBestiary/Defs').rglob('*.xml')) + list((R/'src/RimUtinni').rglob('*.xml')) + [Path(x) for x in EXTRA_XML]:
    try: root = ET.parse(p).getroot()
    except Exception: continue
    for td in root.iter('ThingDef'):
        dn = td.findtext('defName')
        if dn:
            for t in td.iter('texPath'):
                if t.text: defs_tex[dn].append(t.text.strip())
    for pk in root.iter('PawnKindDef'):
        race = pk.findtext('race')
        if race:
            for t in pk.iter('texPath'):
                if t.text: defs_tex[race].append(t.text.strip())
texroots = list((R/'src').glob('*/*/Textures')) + list((R/'src').glob('*/Textures'))
def own_png(defname):
    for tp in reversed(defs_tex.get(defname, [])):
        for root in texroots:
            for suf in ('_south', '', 'A', '_east'):
                f = root/(tp+suf+'.png')
                if f.is_file(): return tp, f
    return (defs_tex.get(defname) or [None])[-1], None

import glob as _g
def _texdirs():
    out = []
    for base in ('/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/*', '/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/*'):
        for d in _g.glob(base):
            for sub in ('Textures', '1.6/Textures', 'Common/Textures', 'Common_Old/Textures'):
                out.append(f'{d}/{sub}')
    return out
TEXDIRS = _texdirs()
_PRI = ('3536598972', '1841354677', '3309003431', '3096501398', 'Droidworks', 'UtinniPatches')
PRI_DIRS = [d for d in TEXDIRS if any(k in d for k in _PRI)]
print('texdirs', len(TEXDIRS), len(PRI_DIRS), flush=True)
_FB = {}
def fs_fallback(tp):
    if tp not in _FB: _FB[tp] = _fs_fallback(tp)
    return _FB[tp]
def _fs_fallback(tp):
    pd, _, stem = tp.rpartition('/')
    for tr in (TEXDIRS if 'Terrorworm' in tp else PRI_DIRS):
        d = f'{tr}/{pd}'
        if not os.path.isdir(d): continue
        fs = sorted(x for x in os.listdir(d) if x.lower().endswith('.png') and not re.search(r'm\.png$', x.lower()) and 'dess' not in x.lower())
        if not fs: continue
        pref = [x for x in fs if x.lower().startswith(stem.lower())] or fs
        for key in ('_south', '_east', 'a.png', ''):
            for x in pref:
                if key == '' or key in x.lower(): return os.path.join(d, x)
    return None

DONOR_TEX = {
 'A_Terrorworm': ['Things/Pawn/Animal/Terrorworm/TerrorWorm'],
 'A_VFEI2_Fuelmite': ['Things/Pawn/Animal/Fuelmite/Fuelmite'],
 'A_OuterRim_SalvageAssistDroid': ['OuterRim/Droid/SalvageAssist'],
 'P_AB_Aaklac': ['Things/Plants/AB_Aaklac/AB_Aaklac'],
 'P_AB_DessertTree': ['Things/Plants/AB_DessertTree/AB_DessertTree'],
 'P_AB_GiantStikehr': ['Things/Plants/AB_GiantStikehr/AB_GiantStikehr'],
}

def thumb(src, dst, side=256):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert('RGBA'); w, hh = im.size
        s = min(1.0, side/max(w, hh))
        if s < 1: im = im.resize((max(1, round(w*s)), max(1, round(hh*s))), Image.LANCZOS)
        elif max(w, hh) < 128: im = im.resize((w*2, hh*2), Image.NEAREST)
        im.save(dst, optimize=True)
    return str(dst.relative_to(T))

def clean_desc(eff):
    for sep in ('(last lifeStage). ', 'entry) ', ' cells. '):
        if sep in eff: eff = eff.split(sep, 1)[1] if sep != ' cells. ' else eff
    eff = re.sub(r'^[—\- ]*⚠ UNGUARDED[^)]*\)\s*', '', eff).strip()
    return eff[:240] + ('…' if len(eff) > 240 else '')

for _r in rows:
    _n = _r['id'][2:]
    if _n.startswith('AA_') and _r['id'] not in DONOR_TEX: DONOR_TEX[_r['id']] = [f'Things/Pawn/Animal/{_n}/{_n}']
items, nodonor, norender = [], [], []
for r in rows:
    rid = r['id']; name = r['label'].split(' [')[0]
    g = mp.get(rid); dn = ported.get(rid)
    it = {'id': rid, 'label': r['label'], 'prefill': '', 'group': '',
          'effect': clean_desc(r['effect']), 'meta': {}}
    # current art: the texture the def resolves to in the live load set
    cur = {}; ctag = ''; own_tp = None
    cands = []
    if dn: cands.append(dn)
    n0 = rid[2:]
    cands += [x for x in dict.fromkeys([n0, re.sub(r'^(OuterRim_|RSW_|JOE_)', '', n0), re.sub(r'^(AB_|RG_)', '', n0), n0.replace('Plant_', 'Plant_', 1)])]
    for dd in cands + (['__tex'] if rid in DONOR_TEX else []):
        tps = DONOR_TEX[rid] if dd == '__tex' else defs_tex.get(dd, [])
        if dd == dn: own_tp = (tps or [None])[-1]
        for tp in reversed(tps):
            path, suf = resolve_texture(tp, TEXIDX, BUNDLES, own_pkg=None)
            if not path and TEXIDX.dir_entries(tp.lower()):
                path = TEXIDX[TEXIDX.dir_entries(tp.lower())[0]]
            if not path: path = fs_fallback(tp)
            if path:
                cur['south'] = thumb(path, AS/rid/'current.png')
                ctag = ('ours: ' if dd == dn else ('donor texture: ' if dd == '__tex' else 'donor def ' + dd + ': ')) + tp
                break
        if cur: break
    if own_tp and not (cur and ctag.startswith('ours')): ownmiss = f'our def points at {own_tp}, which has no file yet'
    else: ownmiss = ''
    if ownmiss and cur: ctag = 'donor art shown for reference; ' + ownmiss + ' (' + ctag + ')'
    elif ownmiss: ctag = ''
    if not cur: nodonor.append(rid)
    # renders
    rend = {}
    if g:
        for fc, jid in groups[g].items():
            src = ART/'_artsrc'/jid/(jid+'.png')
            if src.is_file(): rend[fc] = thumb(src, AS/rid/f'render_{fc}.png')
    extra = {}
    if rid == 'A_RSW_MossBeetle' and 'desertportb_mossbeetlepupa' in groups:
        for fc, jid in groups['desertportb_mossbeetlepupa'].items():
            src = ART/'_artsrc'/jid/(jid+'.png')
            if src.is_file(): extra[fc] = thumb(src, AS/rid/f'pupa_{fc}.png')
    renderB = {}
    if rid == 'A_AA_Terramorph':
        for fc in ('south', 'east'):
            src = ART/'_artsrc'/f'aa_terramorph_{fc}'/f'aa_terramorph_{fc}.png'
            if src.is_file(): renderB[fc] = thumb(src, AS/rid/f'renderB_{fc}.png')
    if not rend: norender.append(rid)
    kind = 'Plants' if rid.startswith('P_') else ('Droids' if 'Droid' in rid else 'Creatures')
    it['group'] = f'{kind} — {"renders ready" if rend else "NO RENDER YET"}'
    it['meta'] = {'ported': dn or '(none yet)', 'origin': r['meta'].get('origin', ''), 'biomes': r['meta'].get('biomes', ''),
                  'rendersetJob': g or '', 'currentTag': ctag, 'ownMissing': ownmiss, 'ourTexPath': own_tp or '',
                  'cur': cur, 'rend': rend, 'extra': extra, 'rendB': renderB}
    if rid in inferred: it['inferred'] = True
    items.append(it)
    print('row', rid, 'render' if rend else 'NORENDER', 'cur' if cur else 'NOCUR', flush=True)

order = {'Creatures — renders ready': 0, 'Plants — renders ready': 1, 'Creatures — NO RENDER YET': 2, 'Plants — NO RENDER YET': 3, 'Droids — NO RENDER YET': 4}
items.sort(key=lambda i: (order.get(i['group'], 9), i['label'].lower()))
(T/'_desert_art_review_items.json').write_text(json.dumps(items))
print('rows', len(items), 'no render', len(norender), norender, 'no current', nodonor)

# ================= assemble =================
npair = len(inferred)
cfg = {
 'sheetId': SID, 'title': 'Desert family art review',
 'subtitle': f'{len(items)} creatures/plants: current art vs the new artpipe renders (DESERT_FAMILY_PORT_EXECUTION_1)',
 'briefHtml': (
  '<p><b>What this is.</b> You ruled 2026-09-20: <i>“keep but replace with our own version of creature and art. Port. All of them.”</i> '
  'The defs are ported; the art is not wired because no render has ever been looked at by a person. '
  f'This sheet shows each of the {len(items)} desert-family rows with its <b>current in-game art</b> (left, grey frame) beside the '
  '<b>new artpipe renders</b> (south / east / north). Nothing is pre-selected.</p>'
  '<p><b>Per row pick one:</b> <b>Keep render</b> = wire the new art in · <b>Redo</b> = regenerate (say what is wrong in the note) · '
  '<b>Keep current</b> = leave the art as it is.</p>'
  '<p><b>Context, not decisions:</b> the older sheet <code>desert_art_verdict_2026-09-20</code> held only agent pre-fills (every row “keep”, no notes, never reviewed), '
  'so there are no earlier art rulings of yours to carry over. One standing ruling does bear on a row: <b>RSW_MossBeetle</b> was CUT on 2026-09-19 (Deeps sheet) the day before the blanket replace; it is shown here with its renders and the pupa renders, and both rulings are yours to reconcile.</p>'
  '<p><b>Grey “current” frame</b> means a donor texture the port still points at, or our own loose PNG where the def already uses one; a few plants have no current image resolved. '
  'Rows with no render yet (Rat, seven droids, two plants, Giant Stikehr which was cut from the Extreme Desert) are at the bottom: choose current / redo only.</p>'),
 'criterion': 'Nothing ranks these: rows are sorted by group then name, not by quality. Art fit is an eye judgment only; the validator passes were format checks (canvas, alpha, facing), not a look.',
 'invented': [
  'Row groups (Creatures / Plants / Droids x renders ready / no render yet) are my organisation, not your rule.',
  f'{npair} rows were paired to a render set by reading descriptions, because the port renamed them (e.g. Terrorworm to RSW_Ashworm, Fuel mite to RSW_Cindermite, Boulder mit to RSW_Korrum, several plants). They carry the "inferred" mark; check the pairing as well as the art.',
  'Current art for rows still on donor art is the texture thumbnail from the 2026-09-20 family sheet; where our def already points at a loose PNG in the repo, that PNG is shown instead.',
  'Ferroclaw (Khorrak) also had an earlier aa_terramorph job; its PNGs are no longer in _artsrc, so only this wave render is shown.',
  'The moss beetle pupa renders are attached to the MossBeetle row rather than given a row of their own.'],
 'posture': {'mode': 'verdict', 'explain': 'Nothing is stripped by posture. Each row is your verdict on the new render versus the current art. Undecided rows are not wired.'},
 'options': [
  {'key': 'keep', 'label': 'Keep render', 'hotkey': '1', 'color': '#5ac37f', 'counts': 'in'},
  {'key': 'redo', 'label': 'Redo', 'hotkey': '2', 'color': '#e8b64c', 'counts': 'out'},
  {'key': 'current', 'label': 'Keep current', 'hotkey': '3', 'color': '#6aa6e8', 'counts': 'out'}],
 'groupLabel': 'group', 'media': True, 'decisionsFile': f'{SID}.decisions.json', 'decisionsPath': '', 'sheetPath': ''}

render_js = r"""<script id="RENDER">
(function(){
  function img(src, cap, cls){
    if(!src) return '<div class="thumb" style="width:150px;height:150px;flex:0 0 150px;display:flex;align-items:center;justify-content:center;font-size:10px;color:#5f6b7a;text-align:center">no image</div>';
    return '<div class="thumb" style="width:150px;height:150px;flex:0 0 150px;'+(cls||'')+'" data-zoom="'+esc(src)+'" data-cap="'+esc(cap)+'"><img src="'+esc(src)+'" loading="lazy" decoding="async" alt=""></div>';
  }
  function cell(label, src, cap, cls){
    return '<div style="display:flex;flex-direction:column;gap:2px;align-items:center"><span style="font-size:10px;color:var(--dim);text-transform:uppercase">'+esc(label)+'</span>'+img(src,cap,cls)+'</div>';
  }
  function strip(title, d, keys, cap){
    var out=''; keys.forEach(function(k){ if(d[k]) out+=cell(k==='single'?'render':k, d[k], cap+' '+k); });
    return out ? '<div><div style="font-size:11px;color:var(--accent);margin-bottom:2px">'+esc(title)+'</div><div style="display:flex;gap:6px;flex-wrap:wrap">'+out+'</div></div>' : '';
  }
  window.itemBody = function(it){
    var m = it.meta||{}, F=['south','east','north','single'];
    var cur = cell('current', (m.cur||{}).south, it.label+' current', 'border-color:#5a6577;background:#1a1d22');
    var A = strip('NEW render'+(m.rendB&&Object.keys(m.rendB).length?' A':''), m.rend||{}, F, it.label);
    if(!A) A='<div style="align-self:center;color:var(--warn);font-size:12px">no new render exists yet</div>';
    var B = strip('render B (earlier aa_terramorph job)', m.rendB||{}, F, it.label+' B');
    var X = strip('pupa stage renders', m.extra||{}, F, it.label+' pupa');
    var meta = '<div class="marks"><span class="mark absent">port def: '+esc(m.ported)+'</span>'
      + (m.rendersetJob?'<span class="mark absent">render job: '+esc(m.rendersetJob)+'</span>':'')
      + (m.currentTag?'<span class="mark absent">current: '+esc(m.currentTag)+(m.ourTexPath?' ('+esc(m.ourTexPath)+')':'')+'</span>':(m.ownMissing?'<span class="mark contested">'+esc(m.ownMissing)+' — shows as the missing-texture placeholder in game</span>':'<span class="mark absent">current: not resolved (vanilla/bundled art not extractable offline)</span>'))
      + (m.biomes?'<span class="mark absent">'+esc(m.biomes)+'</span>':'')+'</div>';
    return '<div class="effect">'+esc(it.effect||'')+'</div>'+meta
      + '<div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:6px;align-items:flex-start">'+cur+A+B+X+'</div>';
  };
})();
</script>
"""
html = TPL.read_text(encoding='utf-8')
a = html.index('<script id="CONFIG" type="application/json">'); b = html.index('</script>', a) + 9
html = html[:a] + '<script id="CONFIG" type="application/json">\n' + json.dumps(cfg, indent=1) + '\n</script>' + html[b:]
a = html.index('<script id="ITEMS" type="application/json">'); b = html.index('</script>', a) + 9
html = html[:a] + '<script id="ITEMS" type="application/json">\n' + json.dumps(items, separators=(',', ':')).replace('</', '<\\/') + '\n</script>' + html[b:]
anchor = '<script>\n"use strict";'
assert anchor in html
html = html.replace(anchor, render_js + '\n' + anchor, 1)
(T/f'{SID}.html').write_text(html, encoding='utf-8')
dec = T/f'{SID}.decisions.json'
if not dec.is_file():
    dec.write_text(json.dumps({'decisions': {}, 'posture': 'verdict', 'criterion': cfg['criterion'],
        'reviewStatus': {'state': 'prefill', 'by': None, 'at': None,
                         'evidence': 'generated 2026-10-03; no row has a decision, nothing pre-selected, no human has ruled'}}, indent=2) + '\n')
print('wrote sheet', (T/f'{SID}.html').stat().st_size)
