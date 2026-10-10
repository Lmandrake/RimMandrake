#!/usr/bin/env python3
"""ROT_RM_CAST_MIGRATION_1 generator (Q12): copies the ten ratified Rot residents and their full
def closure out of RimStarWars/SWBestiary (BiomesTeamPort) into this free-tier mod as RM_ defs,
repoints texture / sound paths at this mod, rewrites the franchise-bearing descriptions (sheet
bans 2 and 7), gives the illoth real 1.6 flight, and deploys the redrawn art.
Re-runnable: it rewrites Defs/Fauna/*.xml and Sounds/RM_TheRot/Fauna; Textures/RM_TheRot/Fauna is
written through the art ledger (owner-kept pictures stay; stale ones are retired, archived).
Run from anywhere:  python3 port_fauna.py

Shared-closure defs the LanternDeeps port also carries get an RM_Rot prefix instead of RM_ (two
free mods must never declare the same defName). Defs TheRot already owns are reused, not copied.
"""
import xml.etree.ElementTree as ET, glob, re, os, shutil, subprocess, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SRCROOT = os.path.join(HERE, '..')
SW = os.path.join(SRCROOT, '..', 'RimStarWars', 'SWBestiary')
SRC = os.path.join(SW, 'Defs', 'BiomesTeamPort')
ART = os.environ.get('ARTSRC', '/mnt/d/Luke/dev/_artpipe/_artsrc')

CREATURES = {
    'RSW_PustuleHornet': 'RM_Thozzik', 'RSW_ColonyPustuleHornet': 'RM_ThozzikColony',
    'RSW_PustuleHornetQueen': 'RM_ThozzikQueen',  # RM_ThozzikSpawned deleted (owner card 2026-10-10)
    'RSW_ColonyPustuleHornetQueen': 'RM_ThozzikColonyQueen', 'RSW_SmogMoth': 'RM_Illoth',
    'RSW_Thrumbungus': 'RM_Brullith', 'RSW_Yooka': 'RM_Brogg',
    'RSW_FungalWeevil': 'RM_Grellik', 'RSW_FungalMantis': 'RM_Skerrith',
}
SEEDS = list(CREATURES)
# franchise-flavoured support names, renamed so no hornet / moth name survives
RENAME = {
    'RSW_SmogMothLarvae': 'RM_IllothLarvae', 'RSW_SmogMothEggFertilized': 'RM_IllothEggFertilized',
    'RSW_SmogMothEggUnfertilized': 'RM_IllothEggUnfertilized', 'RSW_PustuleHornetStinger': 'RM_ThozzikStinger',
    'RSW_PustuleHornets': 'RM_Thozziks', 'RSW_PustuleHornetRaidLootMaker': 'RM_ThozzikRaidLootMaker',
    'RSW_Biomes_Yooka_Angry': 'RM_Brogg_Angry', 'RSW_Biomes_Yooka_Call': 'RM_Brogg_Call',
    'RSW_Biomes_Yooka_Death': 'RM_Brogg_Death', 'RSW_Biomes_Yooka_Wounded': 'RM_Brogg_Wounded',
}
# TheRot already owns these (the spore kit): reuse them, do not copy
REUSE = {
    'RSW_ChitinStuff': 'RM_ChitinStuff', 'RSW_ThrumbungusShroom': 'RM_ThrumbungusShroom',
    'RSW_Proj_ThrumbungusShroom': 'RM_Proj_ThrumbungusShroom', 'RSW_StunningSpores': 'RM_StunningSpores',
    'RSW_ToxicSpores': 'RM_ToxicSpores',
}
# redrawn / finished art: new creature -> (artpipe job prefix, deployed folder)
ART_SETS = {
    'RM_Thozzik': 'rot_thozzik_b', 'RM_ThozzikColony': 'rot_thozzik_b',
    'RM_ThozzikQueen': 'rot_thozzikqueen', 'RM_ThozzikColonyQueen': 'rot_thozzikqueen',
    'RM_Illoth': 'rot_illoth_b', 'RM_Brogg': 'rot_brogg_b', 'RM_Brullith': 'rot_brullith',
    'RM_Skerrith': 'rot_skerrith', 'RM_Grellik': 'rot_fungalweevil_v2',
}
SET_DIR = {'rot_thozzik_b': 'Thozzik', 'rot_thozzikqueen': 'ThozzikQueen', 'rot_illoth_b': 'Illoth',
           'rot_brogg_b': 'Brogg', 'rot_brullith': 'Brullith', 'rot_skerrith': 'Skerrith',
           'rot_fungalweevil_v2': 'Grellik'}

WORDS = [('pustule hornets', 'thozziks'), ('pustule hornet', 'thozzik'), ('pustule queen', 'thozzik queen'),
         ('smog caterpillar', 'illoth larva'), ('smog moth', 'illoth'), ('Pustule Hornets', 'Thozziks'),
         ('thrumbungus', 'brullith'), ('Thrumbungus', 'Brullith'), ('yooka', 'brogg'), ('Yooka', 'Brogg'),
         ('fungal weevil', 'grellik'), ('fungal mantis', 'skerrith')]

THOZZIK = ("A hive creature built on the kurreth's armoured, segmented ant body, its forward mandibles held "
           "ready. Its toxin sacs are fruiting bodies of a fungus it farms inside itself, and the gas it vents "
           "when hurt or killed is that fungus's spore cloud. It defends its hive and its queen with "
           "considerable ferocity, stings laced with potent neurotoxin.\\n\\nIt does not reproduce outside its "
           "hive and gives very little meat or chitin.")
DESC = {
    'RM_Thozzik': THOZZIK,
    'RM_ThozzikColony': THOZZIK + " This variety is loyal to the domesticated queen.",
    'RM_ThozzikQueen': ("The hive's matriarch, the kurreth's armoured body swollen around a spore-bearing "
                        "brood chamber. Very dangerous: nearly as fast as her spawn and her stings inject a more "
                        "potent form of the neurotoxin, so her swarm quickly overpowers anything living in "
                        "its way. Her bulk demands long rests between flights."),
    'RM_ThozzikColonyQueen': ("A domesticated matriarch, the kurreth's armoured body swollen around a "
                              "spore-bearing brood chamber. Nearly as fast as her spawn, with a more potent "
                              "neurotoxin sting; the colony's thozzik answer to her alone."),
    'RM_Illoth': ("A flat, kite-bodied skimmer built on the vrisk, its wing membranes fungal gills dusted "
                  "with spore powder. A living fungal lantern hangs from its underside and glows faintly in the "
                  "dark: the lure that draws prey in."),
    'RM_Thozziks': ("Giant segmented hive creatures that attack without hesitation should humanoids approach. "
                    "Each hive conceals a queen that can produce more of their kind, and the fungus they farm "
                    "lets them live in the most toxic of environments."),
    'RM_IllothLarvae': ("The larval form of the illoth. To deter predators it wears the toxic colours of the "
                        "fungus it hosts."),
    'RM_Brogg': ("A heavy, plated, six-legged grazer built on the dorrak, its back a mound of mycelial store "
                 "under layered bracket fungus and its edges shaggy with hanging hyphae. With little to no "
                 "natural predators, it grazes among the taller fungi with an unconcerned grace."),
    'RM_Brullith': ("A gigantic, fungal amalgam creature: a natural blend of beast and fungus, the fungus "
                    "that fed on its kind long ago now growing in its hide.\\n\\nWhile gentle by nature, it is "
                    "dangerous when enraged. The strange hide that covers much of it is extremely beautiful "
                    "and incredibly resistant to damage."),
}

# ---------------------------------------------------------------- closure
defs = defaultdict(list)
for f in sorted(glob.glob(os.path.join(SRC, '*', '*.xml'))):
    grp = os.path.basename(os.path.dirname(f))
    for d in ET.parse(f).getroot():
        n = d.findtext('defName')
        if n: defs[n].append((grp, d))
        if d.get('Name'): defs['@' + d.get('Name')].append((grp, d))

seen, stack = set(), list(SEEDS)
while stack:
    n = stack.pop()
    if n in seen or n not in defs or n in REUSE: continue
    seen.add(n)
    for grp, d in defs[n]:
        if d.get('ParentName'): stack.append('@' + d.get('ParentName'))
        for t in set(re.findall(r'[A-Za-z_][A-Za-z0-9_]*', ET.tostring(d, encoding='unicode'))):
            if t in defs and t not in seen: stack.append(t)


def taken_elsewhere(name):
    """RM_ name already declared (defName or Name) by some other RimMandrake mod, or by TheRot's own non-Fauna files."""
    pat = r'(<defName>%s</defName>|Name="%s")' % (re.escape(name), re.escape(name))
    out = subprocess.run(['git', 'grep', '-l', '-E', pat, '--', 'src/RimMandrake', ':!src/RimMandrake/TheRot/Defs/Fauna'],
                         capture_output=True, text=True, cwd=os.path.join(HERE, '..', '..', '..')).stdout.split()
    return bool(out)


NEW = dict(CREATURES); NEW.update(RENAME); NEW.update(REUSE)
for n in sorted(seen):
    b = n.lstrip('@')
    if b in NEW: continue
    cand = 'RM_' + b[4:]
    NEW[b] = 'RM_Rot' + b[4:] if taken_elsewhere(cand) else cand
names = sorted({n.lstrip('@') for n in seen} | set(REUSE), key=len, reverse=True)
rx = re.compile(r'\b(' + '|'.join(re.escape(n) for n in names) + r')\b')
unres = {t for n in seen for _, d in defs[n]
         for t in re.findall(r'RSW_[A-Za-z0-9_]+', ET.tostring(d, encoding='unicode')) if t not in names}
print('free-string RSW_ tags (not defs), renamed RM_:', sorted(unres))
rx2 = re.compile(r'RSW_[A-Za-z0-9_]+')
sub = lambda s: rx2.sub(lambda m: m.group(0).replace('RSW_', 'RM_', 1), rx.sub(lambda m: NEW[m.group(1)], s))

# ---------------------------------------------------------------- assets
tex_src = os.path.join(SW, 'Textures'); snd_src = os.path.join(SW, 'Sounds')
out_defs = os.path.join(HERE, 'Defs', 'Fauna')
out_tex = os.path.join(HERE, 'Textures', 'RM_TheRot', 'Fauna')
out_snd = os.path.join(HERE, 'Sounds', 'RM_TheRot', 'Fauna')
for p in (out_defs, out_snd):
    shutil.rmtree(p, ignore_errors=True); os.makedirs(p)
# Textures go through the art ledger (ART_VERSION_WRANGLING_1): no rmtree; stale PNGs are
# retired by tw.sync() after the run, and an owner-kept picture is never overwritten.
sys.path.insert(0, os.path.join(HERE, '..', 'Utils', 'art'))
from artwrite import TextureWriter
tw = TextureWriter(__file__)
copied = {'tex': 0, 'snd': 0, 'art': 0}
missing_art = []


def tex_new(path):
    return 'RM_TheRot/Fauna/' + path.replace('swanimals/BiomesTeam/', '')


def copy_tex(path):
    base = os.path.join(tex_src, path)
    rel = tex_new(path)[len('RM_TheRot/Fauna/'):]
    if os.path.isdir(base):
        os.makedirs(os.path.join(out_tex, rel), exist_ok=True)
        for f in os.listdir(base):
            tw.copy(os.path.join(base, f), os.path.join(out_tex, rel, f)); copied['tex'] += 1
        return True
    d, b = os.path.split(base)
    if not os.path.isdir(d): return False
    hits = [f for f in os.listdir(d) if f == b + '.png' or f.startswith(b + '_')]
    if not hits: return False
    os.makedirs(os.path.join(out_tex, os.path.dirname(rel)), exist_ok=True)
    for f in hits:
        tw.copy(os.path.join(d, f), os.path.join(out_tex, os.path.dirname(rel), f)); copied['tex'] += 1
    return True


def copy_snd(path):
    base = os.path.join(snd_src, path)
    assert os.path.isdir(base), base
    rel = path.replace('BiomesTeam/', '')
    os.makedirs(os.path.join(out_snd, rel), exist_ok=True)
    for f in os.listdir(base):
        shutil.copy2(os.path.join(base, f), os.path.join(out_snd, rel, f)); copied['snd'] += 1


def deploy_art(job):
    """3 facings of a finished artpipe set -> Textures/RM_TheRot/Fauna/Redrawn/<Dir>/<Dir>_<facing>.png"""
    d = SET_DIR[job]; dst = os.path.join(out_tex, 'Redrawn', d)
    os.makedirs(dst, exist_ok=True)
    for fc in ('south', 'east', 'north'):
        s = os.path.join(ART, '%s_%s' % (job, fc), '%s_%s.png' % (job, fc))
        if os.path.exists(s):
            tw.copy(s, os.path.join(dst, '%s_%s.png' % (d, fc))); copied['art'] += 1
        else:
            missing_art.append('%s_%s' % (job, fc))
    return 'RM_TheRot/Fauna/Redrawn/%s/%s' % (d, d)


art_path = {}
for new, job in ART_SETS.items():
    if job not in art_path: art_path[job] = deploy_art(job)

TOLFILE = os.path.join(HERE, '..', '..', 'RimUtinni', 'UtinniPatches', 'Patches', 'AnimalTolerances_Ashkarr.xml')
_tol = open(TOLFILE, encoding='utf8').read()
def tol(n):
    return {k: v for k, v in re.findall(r'defName="%s"\]/statBases/(ComfyTemperature(?:Min|Max))</xpath>\s*<value><\w+>([-\d.]+)<' % n, _tol)}


# ---------------------------------------------------------------- emit
def retext(e):
    for w, r in WORDS:
        if e.text and w in e.text: e.text = e.text.replace(w, r)


groups = defaultdict(list)
for grp_file in sorted(glob.glob(os.path.join(SRC, '*', '*.xml'))):
    grp = os.path.basename(os.path.dirname(grp_file))
    for d in ET.parse(grp_file).getroot():
        n = d.findtext('defName'); a = d.get('Name')
        if not ((n and n in seen) or (a and '@' + a in seen)): continue
        newdef = NEW.get(n) if n else None
        is_kind = d.tag == 'PawnKindDef' and newdef in ART_SETS
        for e in d.iter():
            t = (e.text or '').strip()
            if e.tag == 'texPath' and t:
                if is_kind and not re.search(r'dessicated', t, re.I) and not t.startswith('Things/'):
                    e.text = art_path[ART_SETS[newdef]]
                elif t.startswith('Things/') or not copy_tex(t):
                    pass
                else:
                    e.text = tex_new(t)
            elif e.tag == 'clipFolderPath' and t.startswith('BiomesTeam/'):
                copy_snd(t); e.text = t.replace('BiomesTeam/', 'RM_TheRot/Fauna/')
            elif e.text and 'RSW_' in e.text:
                e.text = sub(e.text)
            if e.tag in names: e.tag = NEW[e.tag]
            for k, v in list(e.attrib.items()):
                if 'RSW_' in v: e.set(k, sub(v))
            if e.tag in ('label', 'labelPlural', 'description', 'fixedName', 'pawnSingular', 'pawnsPlural',
                         'leaderTitle', 'text', 'jobString', 'reportString'):
                retext(e)
        if is_kind:
            for fe in [x for x in d.iter() if x.tag.startswith('flyingAnimation')]:
                for par in d.iter():
                    if fe in list(par): par.remove(fe)
        if d.tag == 'ThingDef' and n in CREATURES:
            # bake in the comfy band the campaign's AnimalTolerances_Ashkarr patch pins on the RSW_ twin,
            # so the free def survives the same biome the campaign cast it into (temperature is a spawn gate)
            for k, v in tol(n).items():
                x = d.find('statBases/' + k)
                if x is not None: x.text = v
                else: ET.SubElement(d.find('statBases'), k).text = v
        if d.tag in ('ThingDef', 'FactionDef') and newdef in DESC:
            d.find('description').text = DESC[newdef]
        if d.tag == 'ThingDef' and newdef == 'RM_Illoth':
            race = d.find('race')
            for tag, val in (('flightStartChanceOnJobStart', '0.1'), ('flightSpeedFactor', '2.5'),
                             ('canFlyIntoMap', 'true'), ('canLeaveMapFlying', 'true')):
                x = race.find(tag)
                if x is None: x = ET.SubElement(race, tag)
                x.text = val
        groups[grp].append(d)

for grp, ds in groups.items():
    root = ET.Element('Defs')
    root.append(ET.Comment(' Generated by port_fauna.py (ROT_RM_CAST_MIGRATION_1) from SWBestiary '
                           'BiomesTeamPort/%s: RSW prefix to RM prefix, hybrid descriptions, redrawn art. '
                           'Edit the generator or hand-own this file; do not mix. ' % grp))
    for d in ds: root.append(d)
    ET.indent(root, space='  ')
    ET.ElementTree(root).write(os.path.join(out_defs, 'RM_TheRot_Fauna_%s.xml' % grp),
                               encoding='utf-8', xml_declaration=True)
bad = [p for p in glob.glob(out_defs + '/*.xml') if 'RSW_' in open(p, encoding='utf8').read()]
tw.sync(out_tex); tw.report()
print('defs', len(seen), 'groups', {g: len(v) for g, v in groups.items()}, 'copied', copied,
      'RSW left in', bad, 'MISSING ART', missing_art)
print('renamed non-creature:', {k: v for k, v in NEW.items() if k not in CREATURES and k not in RENAME and k not in REUSE and v.startswith('RM_Rot')})
