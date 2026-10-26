#!/usr/bin/env python3
r"""leather_amount_lint.py -- fail any race of ours that sets a leather amount but names no leather.

WHY. Pawn.ButcherProducts reads only RaceProps.leatherDef (Pawn.cs:3002); RaceProperties.ResolveReferences sets no
default and vanilla AnimalThingBase carries none. A race with statBases LeatherAmount > 0 and no race.leatherDef (or
race.useLeatherFrom) butchers to NO leather, silently -- the info card still advertises the amount. Found on
RM_Shokka/RM_Shirrel (18063c93f0) and then six more (RACES_FIX_LEATHER_AMOUNT_WITHOUT_LEATHERDEF, 2026-10-26).
Lesson: infrastructure/state/lessons/20261026T114229Z-FOUNDRY-leatheramount-needs-leatherdef.md.

    python3 src/RimMandrake/Utils/leather_amount_lint.py            # the repo's src/, exit 1 on any offender
    python3 src/RimMandrake/Utils/leather_amount_lint.py <root> --json out.json

WHAT IT READS. Every .xml under a Defs/ or Patches/ folder below the root, except FlowWorks and GimmeSomeSlack (BENCH
owns those). ParentName is resolved across the whole root (first Name wins), then through VANILLA_PARENTS below for
the vanilla abstracts; Inherit="False" on <race> or <statBases> stops the walk for that node.

RULE. An offender is a non-abstract ThingDef with a <race> whose effective LeatherAmount is > 0 where that value was
SET BY US (in the def, in one of our ancestors, or by one of our patches), and whose effective race has no leatherDef
and no useLeatherFrom (from the def, an ancestor, a vanilla parent, or a patch naming the def). A race whose only
LeatherAmount is the 40 vanilla AnimalThingBase hands every animal is vanilla's own convention (BaseInsect does the
same: insects butcher no leather by design) and is COUNTED, not failed. A race whose parent chain leaves our tree for
a parent this tool does not know (a donor abstract) is COUNTED as unresolved, not passed or failed.

PATCHES. Only the plain case is modelled: an op whose xpath names defName="X" and whose <value> carries leatherDef /
useLeatherFrom covers X; one whose <value> carries LeatherAmount sets it. Custom-class ops and xpaths that select by
anything other than defName are not modelled (counted as patch_ops_unmodelled when they mention leather at all).

STRICT CLASSES (RACES_AUDIT_INHERITED_40_NO_LEATHERDEF). The vanilla-40 count is a census, not a pass: by body a
quadruped, pinniped, monkey or bird of ours that drops no hide is usually a missed leatherDef, and an insect or crab
of ours that drops no chitin breaks the one chitin ladder every producer points at (canon_materials_design 3.10);
turtle-bodied and soft-bodied (slug, jelly, moth) races were audited the same way, and those with no shell are
exempt by name.
Each class below was audited race by race (leather picked, or LeatherAmount 0 where vanilla's own convention gives
none, e.g. small birds <= 0.35 like Sparrow/Chicken/Duck; arthropods by size: <= 0.2 swarm bodies 0, 0.25-0.9
RM_WeakChitin x25, hard shells near 1 RM_GrayChitin, 1.5-3 RM_MediumChitin; snake-bodied fish by the owner's card
"Only big fish drop it" (2026-10-26): fish from body size about 0.5 up name RM_Fishskin / RSW_Fishskin, smaller ones
and the hideless non-fish on the Snake body LeatherAmount 0), and once FINISHED a race of that body that again
inherits the bare 40 with no leather FAILS, unless STRICT_EXEMPT names it with the reason it deliberately yields no
hide.

    --strict-classes bird,monkey     # check only these; 'none' turns strict checking off; default FINISHED_CLASSES

SANITY. main() refuses to report a clean tree unless it saw at least MIN_RACES races and at least one known-good race
with an explicit leather amount AND a leatherDef (PROBE_GOOD): a zero from a walker that saw nothing is not a pass.
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DEFAULT_ROOT = os.path.join(REPO, 'src')
SKIP_DIRS = {'.git', 'FlowWorks', 'GimmeSomeSlack', 'obj', 'bin', 'Source', 'Textures', 'Sounds'}

# Vanilla abstract race parents (Data/{Core,Royalty,Ideology,Biotech,Anomaly,Odyssey}/Defs, 1.6), measured
# 2026-10-26 by parsing every Named ThingDef there that has a <race>, a race.leatherDef or a LeatherAmount
# (31 of 333 Named ThingDefs). name -> (ParentName, leatherDef, LeatherAmount). Only fields that bear on this rule.
VANILLA_PARENTS = {
    'BasePawn': (None, None, None),
    'AnimalThingBase': ('BasePawn', None, 40.0),
    'BaseBear': ('AnimalThingBase', 'Leather_Bear', None),
    'BaseDrone': ('BasePawn', None, None),
    'BaseFleshbeast': ('BasePawn', None, None),
    'BaseHare': ('AnimalThingBase', 'Leather_Light', None),
    'BaseInsect': ('AnimalThingBase', None, None),
    'BaseMechanoid': ('BasePawn', None, None),
    'BaseMechanoidWalker': ('BaseMechanoid', None, None),
    'BigBirdThingBase': ('AnimalThingBase', 'Leather_Bird', None),
    'BigCatThingBase': ('AnimalThingBase', 'Leather_Panthera', None),
    'BoomalopeThingBase': ('AnimalThingBase', 'Leather_Plain', None),
    'DryadBase': ('AnimalThingBase', None, 0.0),
    'HeavyMechanoid': ('BaseMechanoid', None, None),
    'Human': ('BasePawn', 'Leather_Human', 75.0),
    'LancerMechanoidWalker': ('BaseMechanoidWalker', None, None),
    'LightMechanoid': ('BaseMechanoid', None, None),
    'MechCentipede': ('BaseMechanoid', None, None),
    'MechCenturion': ('SuperHeavyMechanoid', None, None),
    'MechDiabolus': ('SuperHeavyMechanoid', None, None),
    'MechWarqueen': ('SuperHeavyMechanoid', None, None),
    'MiscBirdBase': ('BigBirdThingBase', None, None),
    'MysteriousSphereEntityBase': ('BasePawn', None, None),
    'Nociosphere': ('MysteriousSphereEntityBase', None, None),
    'RatThingBase': ('AnimalThingBase', 'Leather_Light', None),
    'Revenant': ('BasePawn', None, None),
    'SmallBirdThingBase': ('AnimalThingBase', None, 0.0),
    'SuperHeavyMechanoid': ('HeavyMechanoid', None, None),
    'ThingBaseFox': ('AnimalThingBase', 'Leather_Fox', None),
    'ThingBaseWolf': ('AnimalThingBase', 'Leather_Wolf', None),
    'WaterBirdThingBase': ('BigBirdThingBase', None, None),
}

CLASS_BODIES = {
    'bird': {'Bird'},
    'monkey': {'Monkey'},
    'pinniped': {'Pinniped', 'PinnipedWithTusks'},
    'quadruped': {'QuadrupedAnimalWithPaws', 'QuadrupedAnimalWithPawsAndTail', 'QuadrupedAnimalWithHooves',
                  'QuadrupedAnimalWithHoovesAndHump', 'QuadrupedAnimalWithHoovesAndHorn',
                  'QuadrupedAnimalWithHoovesAndTusks', 'QuadrupedAnimalWithClawsTailAndJowl'},
    'insect': {'BeetleLike', 'BeetleLikeWithClaw'},
    'crab': {'Crab'},
    'turtle': {'TurtleLike'},
    'softbody': {'RM_JellyfishBody', 'RM_TentacledSlug', 'RM_ClawedSlug', 'RM_Butterfly', 'RM_Slug'},
    'fish': {'Snake'},   # fish, eels and the other slithering swimmers of ours all ride vanilla's Snake body
}
# classes audited to the end; their regressions fail
FINISHED_CLASSES = ('bird', 'monkey', 'pinniped', 'quadruped', 'insect', 'crab', 'turtle', 'softbody', 'fish')
# defName -> why it deliberately butchers to no hide (audited, left as it is; see the item note).
STRICT_EXEMPT = {
    'RM_Skellarn': 'bird: butchers to its own RM_SkellarnChitin (butcherProducts); a hide on top is a design call',
    'RUT_EmperorVulture': 'bird body only: "nothing about an ulvassk is a bird", a translucent gas sac on bone spars',
    'RM_Hesuun': 'quadruped body only: a wax colony, no hide; what it butchers to is a design call',
    'RUT_Vhessk': 'quadruped body only: a wet muscle slab with sacs; hide undecided',
    'RM_Kethrel': 'quadruped body only: boneless, its shell is bound-on scrap; hide undecided',
    'RM_TarBeast': 'quadruped body only: a tar hill with insectoid flesh; hide undecided',
    'RM_Thrummel': 'butchers to its own RM_ThrummelChitin (one chitin ladder, canon_materials_design 3.10)',
    'RM_ThrummelWarden': 'butchers to its own RM_ThrummelChitin (one chitin ladder, canon_materials_design 3.10)',
    'RM_ThrummelBroodmother': 'butchers to its own RM_ThrummelChitin (one chitin ladder, canon_materials_design 3.10)',
    'RM_ShadeMite': 'grain-scale mite: no hide to take; LeatherAmount 0 vs a mite product is a design call',
    'RM_Siidda': 'grain-scale desiccated dust creature: no hide; product undecided',
    'RM_Quarrok': 'insect: butchers to its own RM_QuarrokChitin (butcherProducts), as RM_Thrummel does',
    'RM_Gallowroot': 'insect body only: a knot of woody vine and thorn, no shell or hide; its yield is a design call',
    'RM_Dredgel': 'crab: butchers to its own RM_DredgelChitin (butcherProducts), as RM_Thrummel does',
    'RM_Gelatid': 'turtle body only: a lobe of the slime biome that leaks rather than bleeds; no shell, no hide',
    'RM_Loomu': 'turtle body only: boneless, slick wet skin, no shell; no hide to take',
    'RM_Ivvol': 'turtle body only: a flat pool floor-dweller with a dorsal eye-ridge, no shell named; hide undecided',
    'RM_Bulloo': 'jelly: a floating gas bag that weeps fuel gel; nothing to skin',
    'RM_Metallovore': 'slug: soft tentacled metal-eater, no shell or hide; its yield is a design call',
    'RM_TunnelSnake': 'Snake body, not a fish: a 1.2 insectoid-fleshed corridor snake; fishskin is wrong, its hide a '
                      'design call',
    'RM_Fessk': 'Snake body, not a fish: a man-sized bone-white long-limbed picker; its hide is a design call',
    'RM_Gharrek': 'Snake body, not a fish: a 0.6 gilled crawler under slate plates; plates vs chitin is a design call',
}

MIN_RACES = 300          # src/ held 667 race ThingDefs when measured 2026-10-26; far fewer means a blind walk
PROBE_GOOD = 'RM_Shokka'   # LeatherAmount 45 in its own statBases, leatherDef set (18063c93f0)
DEFNAME_RE = re.compile(r'defName\s*=\s*["\']([^"\']+)["\']')


def _num(text):
    try:
        return float((text or '').strip())
    except ValueError:
        return None


def iter_files(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = sorted(d for d in dn if d not in SKIP_DIRS)
        parts = dp.replace('\\', '/').split('/')
        kind = 'Defs' if 'Defs' in parts else ('Patches' if 'Patches' in parts else None)
        if not kind:
            continue
        for f in sorted(fn):
            if f.lower().endswith('.xml'):
                yield kind, os.path.join(dp, f)


def scan(root, strict=()):
    """Return a result dict. Pure: reads files under root, writes nothing. strict: class names of CLASS_BODIES."""
    named, concrete, parse_fail = {}, [], []
    patch_cover, patch_amount, unmodelled = set(), {}, 0
    for kind, path in iter_files(root):
        try:
            top = ET.parse(path).getroot()
        except ET.ParseError as e:
            parse_fail.append('%s: %s' % (os.path.relpath(path, root), e))
            continue
        rel = os.path.relpath(path, root)
        if kind == 'Defs':
            for el in top:
                if el.tag != 'ThingDef':
                    continue
                n = el.get('Name')
                if n and n not in named:
                    named[n] = (el, rel)
                if el.get('Abstract', '').lower() != 'true' and el.findtext('defName'):
                    concrete.append((el, rel))
        else:
            for op in top.iter():
                xp = op.find('xpath')
                if xp is None or xp.text is None:
                    continue
                val = op.find('value')
                blob = ET.tostring(val, encoding='unicode') if val is not None else ''
                if 'eather' not in blob:
                    continue
                names = DEFNAME_RE.findall(xp.text)
                if not names:
                    unmodelled += 1
                    continue
                has_def = val.tag in ('leatherDef', 'useLeatherFrom') or val.find('.//leatherDef') is not None \
                    or val.find('.//useLeatherFrom') is not None
                amt = None
                for la in val.iter('LeatherAmount'):
                    amt = _num(la.text)
                if xp.text.rstrip().endswith('LeatherAmount') and amt is None:
                    amt = _num(''.join(val.itertext()))
                for nm in names:
                    if has_def:
                        patch_cover.add(nm)
                    if amt is not None:
                        patch_amount[nm] = amt

    def chain(el):
        """[(element|None, vanilla_tuple|None)] from the def up; ends 'unresolved' when a parent is unknown."""
        out, seen, cur = [(el, None)], set(), el.get('ParentName')
        while cur and cur not in seen:
            seen.add(cur)
            if cur in named:
                pel = named[cur][0]
                out.append((pel, None))
                cur = pel.get('ParentName')
            elif cur in VANILLA_PARENTS:
                v = VANILLA_PARENTS[cur]
                out.append((None, v))
                cur = v[0]
            else:
                return out, cur
        return out, None

    def effective(links, node, leaf_names, vanilla_idx):
        """First value of node/leaf walking up; honours Inherit="False" on node. Returns (value, ours)."""
        for el, van in links:
            if el is not None:
                sub = el.find(node)
                if sub is not None:
                    for leaf in leaf_names:
                        t = sub.findtext(leaf)
                        if t is not None and t.strip():
                            return t.strip(), True
                    if sub.get('Inherit', '').lower() == 'false':
                        return None, True
            else:
                v = van[vanilla_idx]
                if v is not None:
                    return v, False
        return None, False

    races, offenders, vanilla40, unresolved, good = [], [], [], [], []
    leather_of = {}  # defName -> effective leatherDef / useLeatherFrom (None when it names none)
    body_counts = {}  # body -> concrete races of it; the strict classes' non-blind floor
    for el, rel in concrete:
        links, missing = chain(el)
        if not any(e is not None and e.find('race') is not None for e, _ in links) and \
                not any(v is not None for _, v in links):
            continue
        dn = el.findtext('defName').strip()
        races.append(dn)
        amt_txt, amt_ours = effective(links, 'statBases', ('LeatherAmount',), 2)
        amt = amt_txt if isinstance(amt_txt, float) else _num(amt_txt)
        if dn in patch_amount:
            amt, amt_ours = patch_amount[dn], True
        leather, _ = effective(links, 'race', ('leatherDef', 'useLeatherFrom'), 1)
        if dn in patch_cover:
            leather = leather or '(patched)'
        body = next((e.findtext('race/body').strip() for e, _ in links
                     if e is not None and (e.findtext('race/body') or '').strip()), None)
        body_counts[body] = body_counts.get(body, 0) + 1
        row = {'defName': dn, 'file': rel, 'leatherAmount': amt, 'leather': leather, 'body': body}
        leather_of[dn] = leather
        if leather and amt and amt > 0 and amt_ours:
            good.append(dn)
        if leather or not amt or amt <= 0:
            continue
        if missing:
            row['unresolvedParent'] = missing
            unresolved.append(row)
        elif amt_ours:
            offenders.append(row)
        else:
            vanilla40.append(row)
    strict_bodies = set()
    for c in strict:
        strict_bodies |= CLASS_BODIES[c]
    strict_fail = [o for o in vanilla40 if o['body'] in strict_bodies and o['defName'] not in STRICT_EXEMPT]
    v40 = {o['defName'] for o in vanilla40}
    stale_exempt = sorted(n for n in STRICT_EXEMPT if n not in v40)
    return {'races': len(races), 'offenders': offenders, 'vanilla_inherited_amount': vanilla40,
            'strict_failures': strict_fail, 'strict_classes': list(strict), 'stale_exempt': stale_exempt,
            'unresolved_parent': unresolved, 'good_explicit': good, 'parse_failures': parse_fail,
            'patch_ops_unmodelled': unmodelled, 'race_names': races, 'body_counts': body_counts,
            'leather_of': leather_of}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    out_json = None
    if '--json' in argv:
        i = argv.index('--json')
        out_json = argv[i + 1]
        del argv[i:i + 2]
    strict = list(FINISHED_CLASSES)
    if '--strict-classes' in argv:
        i = argv.index('--strict-classes')
        txt = argv[i + 1]
        del argv[i:i + 2]
        strict = [] if txt == 'none' else [c.strip() for c in txt.split(',') if c.strip()]
        unknown = [c for c in strict if c not in CLASS_BODIES]
        if unknown:
            print('unknown class(es) %s; known: %s' % (', '.join(unknown), ', '.join(sorted(CLASS_BODIES))))
            return 2
    root = os.path.abspath(argv[0]) if argv else DEFAULT_ROOT
    probe = PROBE_GOOD if root == DEFAULT_ROOT else None
    r = scan(root, strict)
    if out_json:
        with open(out_json, 'w', encoding='utf-8') as fh:
            json.dump({k: v for k, v in r.items() if k not in ('race_names', 'leather_of')}, fh, indent=1)
    for o in r['offenders']:
        print('FAIL %s (%s): LeatherAmount %g, no race.leatherDef / useLeatherFrom'
              % (o['defName'], o['file'], o['leatherAmount']))
    for o in r['strict_failures']:
        print('FAIL-STRICT %s (%s): body %s is in a finished class but inherits vanilla LeatherAmount 40 with no '
              'leatherDef; name a leather, set LeatherAmount 0, or add it to STRICT_EXEMPT with the reason'
              % (o['defName'], o['file'], o['body']))
    for n in r['stale_exempt']:
        print('NOTE STRICT_EXEMPT names %s, which no longer inherits the bare 40 (drop the entry)' % n)
    for p in r['parse_failures']:
        print('PARSE %s' % p)
    blind = []
    if root == DEFAULT_ROOT and r['races'] < MIN_RACES:
        blind.append('saw %d races, floor %d' % (r['races'], MIN_RACES))
    if probe and probe not in r['good_explicit']:
        blind.append('probe %s not seen as a good race' % probe)
    print('MEASURED races=%d offenders=%d vanilla_inherited_amount=%d strict_failures=%d strict_classes=%s '
          'unresolved_parent=%d good_explicit=%d parse_failures=%d patch_ops_unmodelled=%d root=%s'
          % (r['races'], len(r['offenders']), len(r['vanilla_inherited_amount']), len(r['strict_failures']),
             ','.join(strict) or 'none', len(r['unresolved_parent']), len(r['good_explicit']),
             len(r['parse_failures']), r['patch_ops_unmodelled'], root))
    if blind:
        print('BLIND: %s -- UNMEASURED, not a pass or a fail' % '; '.join(blind))
        return 2
    return 1 if r['offenders'] or r['strict_failures'] else 0


if __name__ == '__main__':
    sys.exit(main())
