## spec
`design/Jawa/fauna/EARTH_FAUNA_EXCLUDED.txt` is the owner's no-Earth-animals rule as
data, but it lists **Core/Odyssey defNames only**. A mod that reskins one of those same
Earth species ships it under its own defName, and the allocator lets it straight through.

Five are cast on Ash'karr today. The first four have vanilla twins already banned in
that very file:

| written | biomes | banned twin |
|---|---|---|
| `GRimTortoise` | BiomeCypreJungle, LavaField | `Tortoise` |
| `GRimCobra` | AB_FeraliskInfestedJungle, AB_MiasmicMangrove | `Cobra` |
| `GRimMonitorLizard` | AB_MiasmicMangrove | `MonitorLizard` |
| `GRimBullfrog` | SeaIce | `Bullfrog` |
| `Wolf_Great` (Odyssey greatwolf) | AB_MycoticJungle | — never listed |

## verify
```
python3 - <<'PY'
import re
excl={l.split('#')[0].strip() for l in open('design/Jawa/fauna/EARTH_FAUNA_EXCLUDED.txt') if l.split('#')[0].strip()}
src=open('src/Jawa/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml').read()
for m in re.finditer(r'defName="(\w+)"\]/wildAnimals</xpath>\s*<value>\s*<wildAnimals>(.*?)</wildAnimals>', src, re.S):
    bad=[e for e in re.findall(r'<(\w+)>[\d.]+</\1>', m.group(2)) if e in excl]
    if bad: print(m.group(1), bad)
PY
```

## criteria
- [ ] The five names are in `EARTH_FAUNA_EXCLUDED.txt`.
- [ ] The cast is **re-generated** and the verify above prints nothing.
- [ ] Every biome that lost an entry still has a full roster — a removal must be
      refilled, not left as a hole.

## Watch out
- 🔑 **Adding a name changes nothing on its own.** The list is an allocator input; the
  deployed artifact is `src/Jawa/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml`, and it
  only moves when the generator runs and the file is re-deployed.
- ⚠️ **Do not re-allocate the whole cast to fix five entries.** A small input change
  that churns most of the output is the failure this project has already paid for —
  generate to a temp path, diff, and patch only the biomes that must move.
- ⚠️ **The list is BUILD-seeded, not owner-authored**, by its own header. Five more
  candidates read as Earth-analogue and are judgement calls, not obvious bans:
  `ColossusToad` · `Pufferpig` · `MA_Hellboar` · `MA_Deermoss` · `DA_Snaptoad`.
  The ~65 GR_* chimeras (bearcat, chickenhorse) are **not** Earth animals; leave them.
- 🔑 Found offline by CHECK 2026-08-27 while pre-answering
  `CAST_LIVE_SPAWN_CHECK_1`, whose criterion 2 names BiomeCypreJungle — the biome with
  the tortoise in it. That live check will "fail" on this and it is not a live defect.
