#!/usr/bin/env python3
"""ART_VERSION_WRANGLING_1: every art variant for the 109 desert-family rows.
Writes Transient/art_census_desert_2026-10-04.{csv,md,html} + thumbs dir. Resumable (thumb cache)."""
import re, os, json, csv, glob, subprocess, collections, io, hashlib, sys, time
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

R = Path('/home/mandrake/rm/bench'); T = R/'Transient'
SP = Path('/tmp/claude-1000/-home-mandrake-rm-bench/7ed5ddfd-542a-4415-93da-a0a2b9afe519/scratchpad')
SID = 'art_census_desert_2026-10-04'
OUT = T/SID; OUT.mkdir(exist_ok=True)
CSVP = T/(SID+'.csv'); MDP = T/(SID+'.md'); HTMLP = OUT/'index.html'
ART = Path('/mnt/d/Luke/dev/_artpipe')
MODS = Path('/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods')
WS = Path('/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100')
MCFG = '/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml'
BUND = Path('/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures')
t0 = time.time()
def log(*a): print(f'[{time.time()-t0:6.0f}s]', *a, flush=True)

COLS = ['creature', 'row_id', 'variant_id', 'source', 'path', 'date', 'origin', 'canon_informed',
        'owner_ruling', 'is_live_repo', 'is_live_deployed', 'likely_from_job', 'thumb']
if not CSVP.exists() or '--fresh' in sys.argv:
    with open(CSVP, 'w', newline='') as f: csv.writer(f).writerow(COLS)
if not MDP.exists() or '--fresh' in sys.argv:
    MDP.write_text('# Desert-family art version census, 2026-10-04 (ART_VERSION_WRANGLING_1)\n\n_building..._\n')
if '--fresh' in sys.argv and (SP/'census_summary.jsonl').exists(): (SP/'census_summary.jsonl').unlink()
done_rows = {r['row_id'] for r in csv.DictReader(open(CSVP))}

items = json.load(open(SP/'items.json'))
log('rows', len(items))

# ---------- load order ----------
active = [e.text.strip().lower() for e in ET.parse(MCFG).getroot().find('activeMods')]
ORDER = {p: i for i, p in enumerate(active)}
def pkg_of(d):
    try: return (ET.parse(Path(d)/'About/About.xml').getroot().findtext('packageId') or '').strip().lower()
    except Exception: return ''

# ---------- texture indexes (cached) ----------
def walk_tex(root_dirs):
    out = []
    for d in root_dirs:
        for sub in ('Textures', '1.6/Textures', 'Common/Textures'):
            base = Path(d)/sub
            if not base.is_dir(): continue
            for dp, dn, fn in os.walk(base):
                for x in fn:
                    if x.lower().endswith('.png'):
                        out.append((str(d), str(Path(dp, x).relative_to(base)).replace('\\', '/')))
    return out
cache = SP/'census_cache.json'
if cache.exists(): C = json.load(open(cache))
else:
    C = {}
    log('walking deployed Mods textures')
    mods = [str(p) for p in MODS.iterdir() if p.is_dir()]
    C['dep_pkg'] = {m: pkg_of(m) for m in mods}
    C['dep_tex'] = walk_tex(mods)
    log('deployed pngs', len(C['dep_tex']))
    want = ('starwarsanimal', 'alphaanimals', 'alphabiomes', 'regrowth', 'insectoid', 'outerrim', 'horrors', 'swac')
    ws = {}
    for d in WS.iterdir():
        p = pkg_of(d)
        if any(w in p.replace('.', '').replace('_', '') for w in want): ws[str(d)] = p
    C['ws_pkg'] = ws
    C['ws_tex'] = walk_tex(list(ws))
    log('donor workshop dirs', len(ws), 'pngs', len(C['ws_tex']))
    json.dump(C, open(cache, 'w'))
src_mods = {str(p.parent.parent): None for p in (R/'src').glob('*/*/About/About.xml')}
SRC_PKG = {m: pkg_of(m) for m in src_mods}
SRC_TEX = walk_tex(list(SRC_PKG))
log('src pngs', len(SRC_TEX))

# ---------- tokens ----------
PFX = r'^(aa_|rg_|ab_|plant_|vfei2_|outerrim_|rsw_|joe_|rut_|rm_|desert_swaca_|desertportb_plant_|desertportb_)+'
STOP = {'bush', 'brambles', 'rat', 'grass', 'plant', 'tree', 'mite', 'worm', 'droid', 'healrootwild', 'wild'}
PRODUCT = {'milk', 'meat', 'leather', 'hide', 'wool', 'egg', 'eggs', 'corpse', 'horn', 'tusk', 'fur', 'skin',
           'icon', 'fertilized', 'unfertilized', 'carved', 'item', 'items', 'apparel', 'weapon', 'weapons',
           'building', 'buildings', 'trophy', 'jerky', 'steak', 'gland', 'silk', 'chitin', 'ui', 'menu',
           'sculpture', 'statue', 'trophies', 'ideoligions', 'dessicated', 'desiccated', 'pelt', 'rug', 'bone', 'bones', 'saddle', 'meal', 'blood', 'feather', 'feathers'}
def stems_for(it):
    s = set()
    for raw in (it['id'][2:], it['meta'].get('ported', ''), it['meta'].get('rendersetJob', '')):
        if not raw or raw.startswith('('): continue
        x = re.sub(PFX, '', raw.lower())
        if x and x not in STOP and len(x) >= 4: s.add(x)
    return s
def toks(name):
    l = name.lower(); return set(re.split(r'[^a-z0-9]+', l)), re.sub(r'[^a-z0-9]', '', l)
def match(name, stems):
    tk, comp = toks(name)
    if tk & PRODUCT: return False
    if re.search(r'pack(_|$)|dessicated', name.lower().rsplit('/',1)[-1]): return False
    return any(st in tk or (len(st) >= 6 and st in comp) for st in stems)

def split_face(rel):
    m = re.match(r'^(.*?)(?:_(south|east|north|west))?\.png$', rel, re.I)
    return (m.group(1), (m.group(2) or 'single').lower()) if m else (rel, 'single')
def is_mask(rel): return bool(re.search(r'(south|east|north|west)m\.png$', rel, re.I))

# ---------- defs: texPaths in repo + deployed ----------
def def_texpaths(xml_text, defname):
    """bodyGraphicData/graphicData texPaths for ThingDef defname + PawnKindDefs racing it; no dessicated."""
    out = []
    try: root = ET.fromstring(xml_text)
    except Exception: return out
    for td in root:
        dn = td.findtext('defName'); race = td.findtext('race')
        if not (dn == defname or (td.tag == 'PawnKindDef' and race == defname)): continue
        for gd in td.iter():
            if gd.tag in ('graphicData', 'bodyGraphicData', 'femaleGraphicData'):
                t = gd.findtext('texPath')
                if t: out.append(t.strip())
    return out
DEFIDX = collections.defaultdict(list)   # defName -> [xml file]
for p in (R/'src').rglob('*.xml'):
    if '/Defs/' not in str(p) and '/Patches/' not in str(p): continue
    try: txt = p.read_text(errors='ignore')
    except Exception: continue
    for m in re.finditer(r'<(?:defName|race)>([^<]+)</(?:defName|race)>', txt): DEFIDX[m.group(1).strip()].append(p)
log('def index', len(DEFIDX))
def mod_root(p):
    p = Path(p)
    for a in [p] + list(p.parents):
        if (a/'About/About.xml').is_file(): return a
    return None

# ---------- artpipe ----------
JOBS = {}
for f in glob.glob(str(ART/'done/*.json')):
    if f.endswith('.manifest.json'): continue
    try: JOBS[Path(f).stem] = json.load(open(f))
    except Exception: pass
ARTSRC = set(os.listdir(ART/'_artsrc'))
log('artpipe done jobs', len(JOBS), 'artsrc dirs', len(ARTSRC))
def jobset(jid):
    return re.sub(r'_(south|east|north|west)(_eyelevel_v\d+)?$', '', jid)

# ---------- decisions (latest version of every decisions file ever, incl. deleted) ----------
def git(*a, binary=False):
    r = subprocess.run(['git', '-C', str(R)] + list(a), capture_output=True)
    return r.stdout if binary else r.stdout.decode('utf-8', 'replace')
DEC = []   # (file, key, decision, note, at, reviewstate)
dpaths = sorted(set(x for x in git('log', '--all', '--name-only', '--format=', '--', '*decisions*.json').split('\n') if x))
for dp in dpaths:
    txt = None
    if (R/dp).is_file(): txt = (R/dp).read_text(errors='replace')
    else:
        h = git('log', '--all', '-1', '--format=%h', '--', dp).strip()
        for ref in (f'{h}:{dp}', f'{h}^:{dp}'):
            t = git('show', ref)
            if t.strip().startswith(('{', '[')): txt = t; break
    if not txt: continue
    try: d = json.loads(txt)
    except Exception: continue
    rsv = d.get('reviewStatus') if isinstance(d, dict) else None
    rs = rsv.get('state', '') if isinstance(rsv, dict) else str(rsv or '')
    dd = d.get('decisions', d) if isinstance(d, dict) else {}
    if not isinstance(dd, dict): continue
    for k, v in dd.items():
        if not isinstance(v, dict): continue
        dec = v.get('decision') or v.get('state') or v.get('art') or ''
        note = (v.get('note') or '').replace('\n', ' ')
        note = re.sub(r'\s+', ' ', note)
        DEC.append((dp, k, str(dec), note, v.get('at', ''), rs, v.get('prefill', '')))
log('decision files', len(dpaths), 'records', len(DEC))
CANON = R/'design/RimStarWars/canon_references'

# ---------- git png history ----------
HIST = collections.defaultdict(list)  # path -> [(hash,date,subj,status)]
cur = None
for line in git('log', '--all', '--format=C|%h|%ad|%s', '--date=short', '--name-status', '--', '*.png').split('\n'):
    if line.startswith('C|'):
        _, h, d, s = line.split('|', 3); cur = (h, d, s)
    elif line and cur and '\t' in line:
        st, *ps = line.split('\t'); HIST[ps[-1]].append((cur[0], cur[1], cur[2], st[0]))
log('png paths in history', len(HIST))
ITEM_RE = re.compile(r'\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+){2,}\b')

# ---------- image helpers ----------
def load_img(src):
    if isinstance(src, bytes): return Image.open(io.BytesIO(src)).convert('RGBA')
    return Image.open(src).convert('RGBA')
def ahash(im):
    bg = Image.new('RGBA', im.size, (0, 0, 0, 255)); bg.alpha_composite(im)
    g = bg.convert('L').resize((16, 16), Image.LANCZOS); px = list(g.getdata()); m = sum(px)/len(px)
    return ''.join('1' if p > m else '0' for p in px)
def ham(a, b): return sum(x != y for x, y in zip(a, b))
def thumb(src, dst):
    if dst.exists(): return str(dst.relative_to(OUT)), None
    try: im = load_img(src)
    except Exception: return '', None
    h = ahash(im)
    w, hh = im.size; s = min(1.0, 256/max(w, hh))
    t = im.resize((max(1, round(w*s)), max(1, round(hh*s))), Image.LANCZOS) if s < 1 else (im.resize((w*2, hh*2), Image.NEAREST) if max(w, hh) < 128 else im)
    t.quantize(colors=128, method=Image.FASTOCTREE).save(dst, optimize=True)
    return str(dst.relative_to(OUT)), h
HASHC = SP/'census_hash.json'
HC = json.load(open(HASHC)) if HASHC.exists() else {}

def canon_flag(j):
    blob = ' '.join(str(j.get(k) or '') for k in ('prompt', 'style_notes', 'reference')).lower()
    if 'canon_references' in blob or 'must show' in blob or 'canon library' in blob or 'visual brief' in blob: return 'y'
    if 'canon' in blob or 'wookieepedia' in blob: return 'partial (canon named in prompt, no library brief)'
    return 'n'

def rulings_for(stems, keys_extra=()):
    out = []
    for (f, k, dec, note, at, rs, pre) in DEC:
        if match(k, stems) or k in keys_extra:
            out.append({'file': f, 'key': k, 'decision': dec, 'note': note, 'at': at, 'review': rs, 'prefill': pre})
    return out

SUMMARY = []
LIM = int(os.environ.get('LIM', '0')) or len(items)
for n_it, it in enumerate(items[:LIM]):
    rid = it['id']; m = it['meta']
    name = it['label'].split(' [')[0]
    stems = stems_for(it)
    if rid in done_rows:
        continue
    ported = m.get('ported', '')
    # ---- live texPaths, repo vs deployed
    rp_tex, dp_tex, deffiles = set(), set(), []
    for dn in [ported, rid[2:]]:
        for f in DEFIDX.get(dn, []):
            tps = def_texpaths(f.read_text(errors='ignore'), dn)
            if not tps: continue
            deffiles.append(str(f.relative_to(R))); rp_tex.update(t.lower() for t in tps)
            mr = mod_root(f)
            if mr:
                dep = MODS/mr.name/f.relative_to(mr)
                if dep.is_file():
                    dp_tex.update(t.lower() for t in def_texpaths(dep.read_text(errors='ignore'), dn))
    def tex_bases(texset): return {t for t in texset if 'dessicated' not in t}
    live_rp, live_dp = tex_bases(rp_tex), tex_bases(dp_tex)
    V = []  # variants
    # ---- repo files (current) grouped by (mod, base)
    def group_files(entries, pkgmap, source):
        g = collections.defaultdict(dict)
        for mod, rel in entries:
            if is_mask(rel): continue
            base, face = split_face(rel)
            if base.lower() in live_rp or base.lower() in live_dp or match(rel, stems):
                g[(mod, base)][face] = rel
        return g
    rg = group_files(SRC_TEX, SRC_PKG, 'repo')
    winners_rp = {}
    for (mod, base), faces in rg.items():
        o = ORDER.get(SRC_PKG.get(mod, ''), -1)
        if base.lower() in live_rp and o > winners_rp.get(base.lower(), (-2,))[0]: winners_rp[base.lower()] = (o, mod)
    dg = group_files([tuple(x) for x in C['dep_tex']], C['dep_pkg'], 'deployed')
    winners_dp = {}
    for (mod, base), faces in dg.items():
        o = ORDER.get(C['dep_pkg'].get(mod, ''), -1)
        if base.lower() in live_dp and o > winners_dp.get(base.lower(), (-2,))[0]: winners_dp[base.lower()] = (o, mod)
    def pick(faces): return faces.get('south') or faces.get('single') or faces.get('east') or next(iter(faces.values()))
    for (mod, base), faces in sorted(rg.items()):
        rel = pick(faces); full = Path(mod)/'Textures'/rel
        if not full.is_file():
            full = next((Path(mod)/s/rel for s in ('1.6/Textures', 'Common/Textures') if (Path(mod)/s/rel).is_file()), full)
        rp = str(full.relative_to(R))
        hist = HIST.get(rp, [])
        V.append(dict(source='repo-current', path=rp, base=base, mod=Path(mod).name, file=full,
                      date=(hist[0][1] if hist else ''), origin=(f'{hist[0][0]} {hist[0][2]}' if hist else 'untracked'),
                      live_repo='y' if winners_rp.get(base.lower(), (0, None))[1] == mod else ('shadowed' if base.lower() in live_rp else 'n'),
                      live_dep=''))
    for (mod, base), faces in sorted(dg.items()):
        rel = pick(faces)
        full = next((Path(mod)/s/rel for s in ('Textures', '1.6/Textures', 'Common/Textures') if (Path(mod)/s/rel).is_file()), Path(mod)/'Textures'/rel)
        # byte-compare with repo counterpart
        twin = next((v for v in V if v['source'] == 'repo-current' and v['mod'] == Path(mod).name and v['base'] == base), None)
        same = ''
        if twin:
            try: same = 'identical-to-repo' if hashlib.md5(full.read_bytes()).digest() == hashlib.md5(twin['file'].read_bytes()).digest() else 'DIFFERS-from-repo'
            except Exception: same = 'unreadable'
        lv = 'y' if winners_dp.get(base.lower(), (0, None))[1] == mod else ('shadowed' if base.lower() in live_dp else 'n')
        if twin: twin['live_dep'] = lv
        if twin and same == 'identical-to-repo': twin['origin'] += ' | deployed identical'; continue
        V.append(dict(source='deployed' + (f' ({same})' if same else ' (no repo twin)'), path=str(full), base=base, mod=Path(mod).name,
                      file=full, date=time.strftime('%Y-%m-%d', time.localtime(full.stat().st_mtime)) if full.exists() else '',
                      origin='deployed folder', live_repo='', live_dep=lv))
    for v in V:
        if v['source'] == 'repo-current' and not v['live_dep']: v['live_dep'] = 'not deployed'
    # ---- git history versions (every add/modify of a matching path, incl deleted paths)
    seen_blob = set()
    for p, evs in HIST.items():
        if not p.startswith('src/') or '/Textures/' not in p: continue
        rel = p.split('/Textures/', 1)[1]
        if is_mask(rel): continue
        base, face = split_face(rel)
        if face not in ('south', 'single'): continue
        if not (base.lower() in live_rp or match(rel, stems)): continue
        for (h, d, s, st) in evs:
            if st == 'D': continue
            blob = git('rev-parse', f'{h}:{p}').strip()
            if not blob or blob in seen_blob: continue
            seen_blob.add(blob)
            headblob = git('rev-parse', f'HEAD:{p}').strip()
            ids = ','.join(sorted(set(ITEM_RE.findall(s))))
            if blob == headblob and any(x['source'] == 'repo-current' and x['path'] == p for x in V):
                for x in V:
                    if x['source'] == 'repo-current' and x['path'] == p: x['origin'] += f' | {len([e for e in evs if e[3] != "D"])} commits touch this path'
                continue
            V.append(dict(source='git-history' + (' (=HEAD)' if blob == headblob else (' (path deleted)' if not headblob or headblob.startswith('HEAD') else ' (overwritten)')),
                          path=p, base=base, mod=p.split('/')[2], file=('git', blob), date=d, origin=f'{h} {s}' + (f' [{ids}]' if ids else ''),
                          live_repo='', live_dep='', commits=[x for x in evs]))
    # ---- artpipe job sets
    sets = collections.defaultdict(dict)
    for jid, j in JOBS.items():
        if match(jid, stems): sets[jobset(jid)][j.get('facing') or 'single'] = jid
    for a in ARTSRC:
        if a not in JOBS and match(a, stems): sets[jobset(a)].setdefault('orphan', a)
    for sid, faces in sorted(sets.items()):
        jid = faces.get('south') or faces.get('single') or next(iter(faces.values()))
        j = JOBS.get(jid, {})
        png = ART/'_artsrc'/jid/(jid+'.png')
        if not png.is_file():
            alt = sorted(glob.glob(str(ART/'_artsrc'/jid/'*.png')))
            png = Path(alt[0]) if alt else png
        V.append(dict(source='artpipe' + ('' if png.is_file() else ' (png gone)'), path=str(png), base=sid, mod='', file=png if png.is_file() else None,
                      date=(j.get('created') or '')[:10], origin=f"{j.get('rimflow_item_id', '?')} | {(j.get('style_notes') or '')[:140]}",
                      canon=canon_flag(j) if j else 'unknown', jobset=sid, live_repo='n', live_dep='n'))
    # ---- donors
    for mod, rel in C['ws_tex']:
        if is_mask(rel) or not (match(rel, stems)): continue
        base, face = split_face(rel)
        if face not in ('south', 'single'): continue
        full = next((Path(mod)/s/rel for s in ('Textures', '1.6/Textures', 'Common/Textures') if (Path(mod)/s/rel).is_file()), None)
        V.append(dict(source='donor-loose', path=str(full or rel), base=base, mod=C['ws_pkg'].get(mod, mod), file=full, date='', origin=C['ws_pkg'].get(mod, ''),
                      canon='n', live_repo='n', live_dep='y' if base.lower() in live_dp and not winners_dp.get(base.lower()) else 'n'))
    try:
        for row in csv.DictReader(open(BUND/'index.csv', encoding='utf-8')):
            if match(row['m_Name'], stems) and not re.search(r'(south|east|north)m$', row['m_Name'], re.I) and not re.search(r'_(east|north)$', row['m_Name'], re.I):
                V.append(dict(source='donor-bundle', path=str(BUND/row['file']), base=row['m_Name'], mod=row['sourceKey'], file=BUND/row['file'],
                              date='', origin=row['sourceKey'], canon='n', live_repo='n', live_dep='?'))
    except FileNotFoundError: pass
    # canon library donor_current_sprite
    for st in stems:
        cd = CANON/st
        if cd.is_dir():
            for x in sorted(cd.glob('*.png')):
                V.append(dict(source='canon-library', path=str(x.relative_to(R)), base=x.stem, mod='', file=x, date='', origin='canon_references entry image', canon='y (reference)', live_repo='n', live_dep='n'))
    # ---- rulings
    keys = {rid, rid[2:], ported}
    RUL = rulings_for(stems, keys)
    canon_ruling = ''
    for st in stems:
        dm = CANON/st/'description.md'
        if dm.is_file():
            mm = re.search(r'^## ruling\s*\n(.*?)(?=^## |\Z)', dm.read_text(errors='ignore'), re.S | re.M)
            if mm: canon_ruling = re.sub(r'\s+', ' ', mm.group(1)).strip()[:300]
    # attach rulings to artpipe sets by key prefix
    for v in V:
        rs = []
        if v.get('jobset'):
            for r in RUL:
                kl = r['key'].lower()
                if kl == v['jobset'].lower() or kl.startswith(v['jobset'].lower() + '_') or kl.startswith(v['jobset'].lower()):
                    rs.append(r)
            if 'desert_swaca_' in v['jobset'] or 'desertportb_' in v['jobset']:
                rs += [r for r in RUL if 'desert_art_review_2026-10-03' in r['file'] and r['key'] == rid]
        v['rul'] = rs
    # ---- thumbs + hashes
    cdir = OUT/re.sub(r'[^A-Za-z0-9_]', '_', rid); cdir.mkdir(exist_ok=True)
    for i, v in enumerate(V):
        v['vid'] = f'{rid}#{i:02d}'
        f = v.get('file'); src = None
        if isinstance(f, tuple): src = git('cat-file', 'blob', f[1], binary=True)
        elif f and Path(f).is_file(): src = str(f)
        if src is None: v['thumb'] = ''; continue
        key = f[1] if isinstance(f, tuple) else str(f)
        tp, h = thumb(src, cdir/f'{i:02d}.png')
        if h: HC[key] = h
        elif key not in HC and tp:
            try: HC[key] = ahash(load_img(src))
            except Exception: pass
        v['thumb'] = tp; v['hash'] = HC.get(key)
    # link non-artpipe variants to nearest artpipe job
    aps = [v for v in V if v.get('jobset') and v.get('hash')]
    for v in V:
        if v.get('jobset') or not v.get('hash'): continue
        best = min(((ham(v['hash'], a['hash']), a['jobset']) for a in aps), default=None)
        if best and best[0] <= 20:
            v['from_job'] = f"{best[1]} (ahash dist {best[0]}/256, weak)"
            ja = next(a for a in aps if a['jobset'] == best[1]); v['canon'] = ja.get('canon', 'unknown')
    # ---- write rows
    with open(CSVP, 'a', newline='') as fh:
        w = csv.writer(fh)
        for v in V:
            rr = '; '.join(f"{'/'.join(Path(r['file']).parts[-2:])}:{r['key']}={r['decision']}" + (f" ({r['note'][:100]})" if r['note'] else '') for r in v['rul'])
            w.writerow([name, rid, v['vid'], v['source'], v['path'], v['date'], v['origin'][:300], v.get('canon', 'unknown'),
                        rr, v.get('live_repo', ''), v.get('live_dep', ''), v.get('from_job', ''), v['thumb']])
    SUMMARY.append(dict(rid=rid, name=name, ported=ported, stems=sorted(stems), deffiles=deffiles, live_rp=sorted(live_rp), live_dp=sorted(live_dp),
                        V=[{k: (str(x) if k == 'file' else x) for k, x in v.items() if k not in ('commits',)} for v in V],
                        RUL=RUL, canon_ruling=canon_ruling))
    json.dump(HC, open(HASHC, 'w'))
    with open(SP/'census_summary.jsonl', 'a') as fh: fh.write(json.dumps(SUMMARY[-1], default=str) + '\n')
    log(n_it, rid, 'variants', len(V), 'rulings', len(RUL))
log('done')
