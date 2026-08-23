#!/usr/bin/env python3
"""Adapt the six AUTHORED xenotypes to Ash'karr, by gene, leaving vanilla Human alone.

🔴 **DECIDE's ruling, 2026-08-23** — the xenotype third of `NORMALIZE_TEMPERATURE_TOLERANCES_1`.
The other two are `plant_tolerances.py` and `../fauna/animal_tolerances.py`.

## Why this third is NOT like the other two

**Measured, not assumed. Three facts changed the design:**

1. ⭐ **Every one of our pawnkinds is `race=Human`** — all 72 of them, `xenotype` unset. A pawn's
   band is therefore Human's shipped **16 … 26 °C** plus the **gene** offsets its xenotype brings.
   There is no per-species race def to patch.
2. ⛔ **There is NO temperature spawn gate for pawns.** `SeasonAndOutdoorTemperatureAcceptableFor`
   is wired to animals, trader stock, manhunter packs and a few incidents — never to a humanlike
   pawnkind. So unlike plants and animals, nothing silently fails to exist; pawns simply suffer.
   **That is why this pass is small and surgical rather than sweeping.**
3. ⭐ **The droids are already fine** — `OuterRim_*` ship ±250 °C and the KotOR droids ±100…±200.
   They need nothing, and touching them would be narrowing.

🔑 **So vanilla `Human` is deliberately NOT patched.** Widening it would adapt every offworlder,
every raider and every visitor at once and delete the clothing-and-heaters survival loop that is
the core of RimWorld. Native species are adapted; outsiders still have to dress for the planet.
That is both the better game and the better story.

## What it does

For each authored xenotype, force the widest REALISTIC vanilla adaptation:

    MinTemp_LargeDecrease   −20 °C      exclusionTag MinTemperature — only one may apply
    MaxTemp_LargeIncrease   +20 °C      exclusionTag MaxTemperature — only one may apply

⇒ **16 … 26 becomes −4 … 46 °C**, and the Wookiee reaches **−14 … 46** because `Furskin` sits in
the `Fur` exclusion group and so stacks with a `MinTemperature` gene.

⚠️ **Two of our xenotypes carried `MinTemp_SmallIncrease`, a +4.5 °C cold PENALTY** — MandrakeJawa
and RimMandrakeTusken were authored as desert dwellers who suffer in cold. On a tidally locked
world with a −82 °C nightside that gene punishes them for the planet they live on, so it is
replaced. Replacing a narrowing gene with a widening one obeys the owner's widen-only ruling.

## Two costs, stated rather than buried

⚠️ **METABOLISM.** Both genes are `biostatMet −2`. Every adapted xenotype loses metabolic
efficiency and therefore eats more — and for MandrakeJawa and RimMandrakeTusken the swing is −3,
because the `+1` penalty gene they shed was *paying* for itself. On a scavenger world where food
is scarce this is a real balance change, and it is the reason not to reach for a bigger gene.

⚠️ **−4 … 46 °C does NOT cover Ash'karr.** The planet runs −82 … +66 and the habitable p05…p95 is
−64 … +57. Vanilla's realistic tier caps out here. Going further means either `MinTemp_HugeDecrease`
(−300 °C, which makes our species simply immune to cold) or a **custom GeneDef** — and a new def is
CONTENT, which is BUILD's, not DECIDE's. Filed as a decision for the owner rather than taken here.
"""
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biome_flora as bf                                            # noqa: E402  ROOT + DB

PATCH = os.path.join(bf.ROOT, 'src', 'Jawa', 'Jawa_Patches', 'Patches',
                     'XenotypeTolerances_Ashkarr.xml')

OURS = ['MandrakeJawa', 'RimMandrakeJawa', 'RimMandrakeHutt',
        'RimMandrakeTusken', 'RimMandrakeWookiee', 'Jawa_Xeno_Gamorrean']
WANT = {'MinTemperature': 'MinTemp_LargeDecrease',      # −20
        'MaxTemperature': 'MaxTemp_LargeIncrease'}      # +20
HUMAN = (16.0, 26.0)                                    # measured off the Human def


def load():
    con = sqlite3.connect(f'file:{bf.DB}?mode=ro', uri=True)
    genes, xenos = {}, {}
    for (j,) in con.execute("SELECT json FROM defs WHERE def_type='GeneDef'"):
        d = json.loads(j)
        f = d['fields']
        off = {m['stat']: float(m['value']) for m in (f.get('statOffsets') or [])
               if isinstance(m, dict) and 'ComfyTemperature' in str(m.get('stat', ''))}
        genes[d['defName']] = {'off': off, 'tags': f.get('exclusionTags') or [],
                               'met': f.get('biostatMet') or 0}
    for (j,) in con.execute("SELECT json FROM defs WHERE def_type='XenotypeDef'"):
        d = json.loads(j)
        if d['defName'] in OURS:
            g = d['fields'].get('genes') or []
            xenos[d['defName']] = [x if isinstance(x, str) else x.get('defName', str(x))
                                   for x in g]
    return genes, xenos


def plan(genes, xenos):
    out = []
    for x in OURS:
        have = xenos.get(x)
        if have is None:
            out.append((x, None, None, None, None))
            continue
        drop, add = [], []
        for tag, target in WANT.items():
            occupying = [g for g in have if tag in genes.get(g, {}).get('tags', [])]
            if target in occupying:
                continue                                    # already the widest tier
            drop += occupying                               # only one may apply — shed the rest
            add.append(target)
        before = _band(genes, have)
        after = _band(genes, [g for g in have if g not in drop] + add)
        met = sum(genes.get(g, {}).get('met', 0) for g in add) - \
            sum(genes.get(g, {}).get('met', 0) for g in drop)
        out.append((x, drop, add, (before, after), met))
    return out


def _band(genes, names):
    lo, hi = HUMAN
    for g in names:
        off = genes.get(g, {}).get('off', {})
        lo += off.get('ComfyTemperatureMin', 0.0)
        hi += off.get('ComfyTemperatureMax', 0.0)
    return (round(lo, 1), round(hi, 1))


def emit(rows):
    o = ['<?xml version="1.0" encoding="utf-8"?>', '<Patch>',
         '  <!-- GENERATED by design/Jawa/mods/xenotype_tolerances.py - do not hand-edit.',
         '',
         '       The six AUTHORED xenotypes adapted to Ash\'karr with vanilla temperature genes.',
         '       Every one of our pawnkinds is race=Human, so a pawn\'s band is Human\'s 16..26 °C',
         '       plus the gene offsets its xenotype brings - there is no species race def.',
         '',
         '       🔑 vanilla Human is DELIBERATELY NOT PATCHED. Widening it would adapt every',
         '       offworlder and raider at once and delete the clothing-and-heaters survival loop.',
         '       Natives are adapted; outsiders still dress for the planet.',
         '',
         '       ⚠️ MinTemperature and MaxTemperature are exclusionTags: only ONE gene of each may',
         '       apply, so a lesser tier is REMOVED before the larger one is added. Furskin is in',
         '       the Fur group and stacks, which is why the Wookiee reaches -14 rather than -4.',
         '',
         '       XenotypeDef.genes is a plain List<GeneDef>, so <li> is correct here - this is NOT',
         '       the LoadDataFromXmlCustom field where an <li> discards the whole def. -->', '']
    for x, drop, add, bands, met in rows:
        if drop is None:
            continue
        (b4, af) = bands
        o.append(f'  <!-- {x}: {b4[0]:g}..{b4[1]:g} -> {af[0]:g}..{af[1]:g} °C   '
                 f'metabolism {met:+d}'
                 + (f'   sheds {", ".join(drop)}' if drop else '') + ' -->')
        for g in drop:
            o += ['  <Operation Class="PatchOperationConditional">',
                  f'    <xpath>/Defs/XenotypeDef[defName="{x}"]/genes/li[text()="{g}"]</xpath>',
                  '    <match Class="PatchOperationRemove">',
                  f'      <xpath>/Defs/XenotypeDef[defName="{x}"]/genes/li[text()="{g}"]</xpath>',
                  '    </match>', '  </Operation>']
        for g in add:
            o += ['  <Operation Class="PatchOperationConditional">',
                  f'    <xpath>/Defs/XenotypeDef[defName="{x}"]/genes/li[text()="{g}"]</xpath>',
                  '    <nomatch Class="PatchOperationAdd">',
                  f'      <xpath>/Defs/XenotypeDef[defName="{x}"]/genes</xpath>',
                  f'      <value><li>{g}</li></value>',
                  '    </nomatch>', '  </Operation>']
        o.append('')
    o.append('</Patch>')
    os.makedirs(os.path.dirname(PATCH), exist_ok=True)
    open(PATCH, 'w', encoding='utf-8').write('\n'.join(o) + '\n')
    return PATCH


def main() -> int:
    genes, xenos = load()
    rows = plan(genes, xenos)
    print(f"\nHuman base {HUMAN[0]:g} … {HUMAN[1]:g} °C — deliberately NOT patched\n")
    n = 0
    for x, drop, add, bands, met in rows:
        if drop is None:
            print(f"  ⚠️  {x:22s} ABSENT from the def dump — SKIPPED")
            continue
        n += 1
        (b4, af) = bands
        print(f"  {x:22s} {b4[0]:6g}..{b4[1]:<5g} -> {af[0]:6g}..{af[1]:<5g} °C  "
              f"met {met:+d}  +{','.join(add) or '-'}"
              + (f"  −{','.join(drop)}" if drop else ''))
    if '--write' not in sys.argv:
        print("\n(pass --write to emit the patch)")
        return 0
    print(f"\nwrote {emit(rows)}  ({n} xenotypes)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
