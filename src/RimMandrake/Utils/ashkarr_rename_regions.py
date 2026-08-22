#!/usr/bin/env python3
"""Strip the definite article from the region names.

Owner, 2026-08-22: "Please take 'The' off of almost all the placenames. It's unnecessary
clutter. The Ashen Waste -> Ashen Wastes. 'The Verge' needs to keep it. 'The Chalk March'
-> 'Chalk Marches', Sunreach can just be Sunreach. Cinderdark can just be Cinderdark. etc."

Two rules, from his own examples:
  1. Drop "The " - that is the default and it applies to 70 of the 71 regions.
  2. Where he pluralised, pluralise: Waste -> Wastes, March -> Marches. Those are the only
     two he demonstrated, so they are the only two applied. Inventing more plurals would be
     guessing at his ear.
KEEP: "The Verge" exactly, named explicitly. ⚠️ "The Hollow Verge" is a DIFFERENT region and
      is not covered by that exemption - it loses the article like everything else.
"""
import argparse, csv, json, os, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
KEEP = {'The Verge'}
PLURAL = [(re.compile(r'\bWaste$'), 'Wastes'), (re.compile(r'\bMarch$'), 'Marches')]

def rename(name):
    if not name or name in KEEP or not name.startswith('The '):
        return name
    out = name[4:]
    for pat, rep in PLURAL:
        out = pat.sub(rep, out)
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()
    W = os.path.join(ROOT, 'world')
    tiles_p = os.path.join(W, 'ASHKARR_WORLDMAP_tiles.csv')
    with open(tiles_p, encoding='utf-8') as f:
        rd = csv.DictReader(f); tiles = list(rd); cols = rd.fieldnames
    regs = sorted({r['region'] for r in tiles if r['region']})
    mapping = {r: rename(r) for r in regs}
    changed = {k: v for k, v in mapping.items() if k != v}
    print(f"{len(regs)} regions, {len(changed)} renamed, {len(regs)-len(changed)} kept")
    for k, v in sorted(changed.items()):
        mark = ' (pluralised)' if not v == k[4:] else ''
        print(f"   {k:26} -> {v}{mark}")
    for k, v in mapping.items():
        if k == v: print(f"   {k:26} -> KEPT")

    if not a.apply:
        print("\nDRY RUN - nothing written. Re-run with --apply")
        return
    for r in tiles:
        r['region'] = mapping.get(r['region'], r['region'])
    with open(tiles_p, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(tiles)
    print(f"WROTE {tiles_p}")

    # the meta json carries the gazetteer too
    meta_p = os.path.join(W, 'ASHKARR_WORLDMAP_meta.json')
    if os.path.exists(meta_p):
        txt = open(meta_p, encoding='utf-8').read()
        n = 0
        for k, v in sorted(changed.items(), key=lambda kv: -len(kv[0])):
            c = txt.count(f'"{k}"')
            txt = txt.replace(f'"{k}"', f'"{v}"'); n += c
        open(meta_p, 'w', encoding='utf-8').write(txt)
        print(f"WROTE {meta_p} ({n} name occurrences)")

    # and the design gazetteer
    for doc in ('design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md',
                'design/Jawa/worldbuilding/named_places_draft.md'):
        p = os.path.join(ROOT, doc)
        if not os.path.exists(p): continue
        txt = open(p, encoding='utf-8').read(); n = 0
        for k, v in sorted(changed.items(), key=lambda kv: -len(kv[0])):
            n += txt.count(k); txt = txt.replace(k, v)
        open(p, 'w', encoding='utf-8').write(txt)
        print(f"WROTE {doc} ({n} occurrences)")

if __name__ == '__main__':
    main()
