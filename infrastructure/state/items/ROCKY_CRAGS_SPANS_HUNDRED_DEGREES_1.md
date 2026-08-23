## spec

🔴 **`AB_RockyCrags` runs from −82 °C to +19.8 °C. One biome, one creature cast, one plant
roster, across 102 degrees.** Measured 2026-08-23 off `world/ASHKARR_WORLDMAP_tiles.csv`:

| band | tiles |
|---|---:|
| below −70 °C | 428 |
| −70 … −50 | 1,154 |
| −50 … −30 | 1,116 |
| −30 … −10 | 742 |
| −10 … 0 | 371 |
| 0 … +19.8 | 344 |
| **total** | **4,155** — the biggest biome on the planet |

**It is not a habitat. It is a band running from deep nightside to near-terminator**, and
casting it as one creature list puts a lizard and a snow-thing on the same ground.

## 🔴 Carving HorrorWastes out of it did NOT fix this, and the record said it had

`HORROR_WASTES_ON_NIGHTSIDE_1` gave thermal coherence as the second reason for the carve and
then recorded *"`AB_RockyCrags` 4,703 → 3,423 and its thermal span narrows."* **All three
numbers are wrong as the world now stands:**

| the item says | measured 2026-08-23 |
|---|---|
| 1,200 tiles moved (arc ≥ 140) | **468** — it was redone as scattered pockets |
| `AB_RockyCrags` = 3,423 | **4,155** |
| its thermal span narrows | **unchanged: −82 … +19.8** |

🔑 **HorrorWastes did not take the cold end.** Of the **coldest 500 tiles on the planet, 383
are still `AB_RockyCrags`** and only 63 are `HorrorWastes` — and **177 `AB_RockyCrags` tiles
are colder than the coldest `HorrorWastes` tile** (−74.9 °C). The pockets were cut from
*within* the cold band, not off its end.

⇒ **This is a different problem from HorrorWastes and must not be welded to it again.**
HorrorWastes at 468 nightside pockets satisfies the owner's brief and is not the defect here.

## what to decide

**Split `AB_RockyCrags` by temperature.** The obvious cut is around **−50 °C**, which divides
it 1,582 / 2,573 and gives each side a ~30–50 °C working range instead of 102.

⚠️ **DECIDE owes the owner a proposal, not a fait accompli** — this is 4,155 tiles, 19% of the
planet, and it changes what he sees. Options, for him to pick by looking:
1. **Two biomes** — a deep-cold crags and a temperate crags. Needs a second BiomeDef.
2. **Give the cold half to an existing cold biome** — `IceSheet` (80 tiles today) or
   `AB_PropaneLakes` (554) are both already cold and already placed.
3. **Accept it** and cast `AB_RockyCrags` with cold-tolerant creatures only, losing the warm
   end's identity. Cheapest, and honest if he does not want more biomes.

## verify

    python3 - <<'PY'
    import csv, collections
    t=[x for x in csv.DictReader(open('world/ASHKARR_WORLDMAP_tiles.csv',encoding='utf-8'))]
    rc=[x for x in t if x['biome']=='AB_RockyCrags']
    tc=sorted(float(x['temp_c']) for x in rc)
    print(len(rc), tc[0], tc[-1], tc[-1]-tc[0])
    PY

**PASS =** no surviving biome spans more than ~60 °C, and `AB_PropaneLakes` /
`BMT_CrystalCaverns` are untouched unless the owner chose option 2.

## criteria

- [ ] The owner has picked an option by looking at a render, not from this table.
- [ ] No biome on Ash'karr spans more than ~60 °C.
- [ ] `HORROR_WASTES_ON_NIGHTSIDE_1`'s stale "span narrows" claim is struck in that item.
- [ ] `canon.yml` re-measured — biome tile counts are canon-adjacent.

## watch out

- ⚠️ **A biome edit is a `biome` column edit and does NOT move elevation**, so nothing becomes
  water or land by doing it. That constraint from the HorrorWastes item still holds.
- 🔴 **This re-opens `AB_RockyCrags`' creature cast**, which is the one already worked
  (`BIOME_CAST_APPLY_1`). Do this BEFORE re-casting it, or the cast is thrown away twice.
- ⛔ **`BiomeDef.wildAnimals` cannot be read from the def dump.** All 80 BiomeDefs report
  exactly 1024 entries, byte-identical and alphabetically sorted — a truncation artifact, not
  a roster. Any per-biome animal count taken from that field is UNMEASURED.
