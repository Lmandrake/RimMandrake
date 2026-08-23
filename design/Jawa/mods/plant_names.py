#!/usr/bin/env python3
"""Earth crop and tree names become Star Wars names. Labels only.

🔴 **OWNER, 2026-08-23**, choosing from a menu: rename **crops + Earth trees + the harvested
goods**, in a **mixed register** — *canon for food, invented for flora* — and deploy it.
His worked example was *"Cotton could be Silkstrand"*.

🔑 **The register split, and why it is not arbitrary.** A name only pays for itself if it is
either RECOGNISED or FELT. Food is inspected, eaten, cooked and traded, so a player meets its
name repeatedly and canon earns recognition — `ardees` is the base of Huttese *"Jawa juice"*,
which is the single most on-brand word available to this campaign. Background flora is seen
and never read, so canon there is wasted on an audience that will not look it up; those get
invented desert-coded names that carry tone instead.

⛔ **LABELS ONLY. Never defNames.** A defName is the save key and the cross-reference target:
renaming `Plant_Corn` breaks every save, recipe, bill, stockpile filter and mod patch that
names it. A label is cosmetic and free. ⚠️ None of these 25 defs ships a `description`, so
there is no prose left contradicting the new names — checked, not assumed.

⛔ **The owner's four Cherry Picker cuts are EXCLUDED** — `Plant_TreePine`, `Plant_TreeBirch`,
`Plant_TreePoplar`, `RG_Plant_Raspberry`. Cherry Picker removes those defs at load, so a patch
against them is dead weight. Their VLE `_Auburn` cousins are separate defs and ARE renamed.

⚠️ Every operation is wrapped in `PatchOperationConditional` on the same xpath, because a
`PatchOperationReplace` that matches nothing is a RED ERROR, not a no-op.

    python3 design/Jawa/mods/plant_names.py --check
    python3 design/Jawa/mods/plant_names.py --write
"""
import argparse, json, os, sqlite3, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DB = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
      "RimWorld by Ludeon Studios/DefDump/defs.sqlite")
PATCH = os.path.join(ROOT, 'src', 'Jawa', 'Jawa_Patches', 'Patches', 'PlantNames_Ashkarr.xml')

# defName -> (new label, register, the note that justifies it)
RENAMES = {
 # ---- FOOD: canon-drawn, because it is inspected, cooked and traded ----------
 'Plant_Corn':      ('kessel grain',    'canon', 'Kessel - canon world, its spice runs are the most famous cargo in the setting'),
 'Plant_Rice':      ('kibla grain',     'canon', 'kibla greens - canon Star Wars produce'),
 'Plant_Potato':    ('koyo tuber',      'canon', 'koyo - canon fruit; "tuber" carries the crop role'),
 'Plant_Strawberry':('pallie berry',    'canon', 'pallie - canon Tatooine fruit, so it belongs on a desert world'),
 'Plant_Berry':     ('shuura bush',     'canon', 'shuura - canon Naboo fruit; kept distinct from pallie'),
 'Plant_Hops':      ('ardees vine',     'canon', '⭐ ardees is the base of Huttese "Jawa juice" - the most on-brand word in the setting for THIS clan'),
 'Plant_TreeCocoa': ('mimbanese cacao', 'canon', 'Mimban - canon jungle world'),
 'Plant_Haygrass':  ('bantha fodder',   'canon', '⭐ banthas are the beast of the Jawas and Tuskens; what you grow to feed them names itself'),
 # ---- FIBRE: invented. The owner named this one himself. --------------------
 'Plant_Cotton':      ('silkstrand',      'invented', "the owner's own example"),
 'Plant_Cotton_Wild': ('wild silkstrand', 'invented', "matches Plant_Cotton"),
 # ---- TREES: invented, desert-coded. Seen, never read. ----------------------
 'Plant_TreeOak':     ('ironbough tree',  'invented', 'hard, dark, slow'),
 'Plant_TreeMaple':   ('bloodleaf tree',  'invented', 'keeps the red-leaf reading of a maple'),
 'Plant_TreeWillow':  ('weepvine tree',   'invented', 'keeps the drooping silhouette'),
 'Plant_TreeCypress': ('duskspire tree',  'invented', 'keeps the narrow vertical spire'),
 'Plant_TreeTeak':    ('hardgrain tree',  'invented', 'teak is prized for grain; the name says why'),
 'Plant_TreeBamboo':  ('reed-cane',       'invented', 'jointed, fast, not a tree in feel'),
 'Plant_TreePalm':    ('fanleaf palm',    'invented', 'palm is generic enough to survive; the fan is the tell'),
 'VEE_Plant_TreeOak_Auburn':    ('auburn ironbough', 'invented', 'VLE variant of the above'),
 'VEE_Plant_TreeMaple_Auburn':  ('auburn bloodleaf', 'invented', 'VLE variant'),
 'VEE_Plant_TreeBirch_Auburn':  ('auburn palewood',  'invented', 'VLE variant; Core birch itself is CUT'),
 'VEE_Plant_TreePoplar_Auburn': ('auburn spirewood', 'invented', 'VLE variant; Core poplar itself is CUT'),
 # ---- THE HARVESTED GOODS. Renaming the plant and not its yield is half a job.
 'RawCorn':     ('kessel grain', 'canon', 'matches Plant_Corn'),
 'RawRice':     ('kibla grain',  'canon', 'matches Plant_Rice'),
 'RawPotatoes': ('koyo tubers',  'canon', 'matches Plant_Potato'),
 'RawHops':     ('ardees',       'canon', 'matches Plant_Hops'),
 'Chocolate':   ('mimbanese sweet', 'canon', 'matches Plant_TreeCocoa'),
}

# Deliberately untouched, and each for a reason a reader would otherwise ask about.
LEFT_ALONE = {
 'Cloth': 'already generic - it is what cotton YIELDS, and nothing about it says Earth',
 'WoodLog': 'generic, and renaming it touches every construction recipe in the game',
 'Hay': 'generic',
 'MedicineHerbal': 'generic',
 'Dye': 'generic',
 'RawBerries': 'generic, and shared by three bushes that now have three different names',
 'Plant_Healroot': 'Ludeon invention, not an Earth species',
 'Plant_Devilstrand': 'Ludeon invention',
 'Plant_Psychoid': 'Ludeon invention',
 'Plant_Smokeleaf': 'Ludeon invention',
 'Plant_Tinctoria': 'Ludeon invention',
 'Plant_Agave': 'an Earth species, but it is the signature plant of THIS desert and reads right',
 'Plant_TreePine': "CUT by the owner - Cherry Picker removes the def",
 'Plant_TreeBirch': "CUT by the owner",
 'Plant_TreePoplar': "CUT by the owner",
 'RG_Plant_Raspberry': "CUT by the owner",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    if not os.path.exists(DB):
        print(f'UNMEASURED no defs.sqlite at {DB} — run `measure build`'); return 2
    con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    live = {}
    for (j,) in con.execute("SELECT json FROM defs WHERE def_type='ThingDef'"):
        d = json.loads(j)
        if d['defName'] in RENAMES:
            live[d['defName']] = d
    bad = sorted(set(RENAMES) - set(live))
    for n in bad:
        print(f"🔴 NOT IN THE LIVE DEF SET: {n}")
    dup = {}
    for n, (lab, _, _) in RENAMES.items():
        dup.setdefault(lab, []).append(n)
    for lab, ns in dup.items():
        if len(ns) > 1 and not all(n.startswith('Raw') or n == 'Chocolate' for n in ns) \
           and not any(n.startswith('Raw') or n == 'Chocolate' for n in ns):
            print(f"⚠️  two different things would both be called '{lab}': {ns}")
    print(f"\n{len(RENAMES)} renames · {sum(1 for v in RENAMES.values() if v[1]=='canon')} canon, "
          f"{sum(1 for v in RENAMES.values() if v[1]=='invented')} invented · "
          f"{len(LEFT_ALONE)} defs deliberately left alone")
    if bad:
        print("\n🔴 nothing written."); return 1
    print("✅ every defName resolves in the live def set")
    for n, d in sorted(live.items()):
        if d.get('description'):
            print(f"⚠️  {n} HAS a description that may still name the Earth species — read it")
    if not a.write:
        print("\n(pass --write to emit the patch)"); return 0

    out = ['<?xml version="1.0" encoding="utf-8"?>', '<Patch>',
           '  <!-- GENERATED by design/Jawa/mods/plant_names.py - do not hand-edit.', '',
           "       Earth crop and tree names become Star Wars names. LABELS ONLY - a defName is",
           '       the save key and renaming one breaks every save, recipe and cross-reference.',
           '',
           '       Register, on the owner\'s ruling: CANON for food, because it is inspected,',
           '       cooked and traded and so earns recognition; INVENTED for background flora,',
           '       which is seen and never read and so wants tone instead.', '',
           '       Every op is wrapped in a Conditional: a Replace that matches nothing is a',
           '       RED ERROR, not a no-op. -->', '']
    for reg in ('canon', 'invented'):
        out.append(f'  <!-- ============ {reg} ============ -->')
        for n, (lab, r, why) in sorted(RENAMES.items()):
            if r != reg:
                continue
            old = live[n].get('label')
            out += [f'  <Operation Class="PatchOperationConditional">',
                    f'    <xpath>/Defs/ThingDef[defName="{n}"]/label</xpath>',
                    f'    <match Class="PatchOperationReplace">',
                    f'      <xpath>/Defs/ThingDef[defName="{n}"]/label</xpath>',
                    f'      <value><label>{lab}</label></value>',
                    f'    </match>',
                    f'  </Operation>  <!-- {old} -> {lab} · {why} -->', '']
    out.append('</Patch>')
    os.makedirs(os.path.dirname(PATCH), exist_ok=True)
    open(PATCH, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print(f"\nwrote {PATCH}  ({len(RENAMES)} operations)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
