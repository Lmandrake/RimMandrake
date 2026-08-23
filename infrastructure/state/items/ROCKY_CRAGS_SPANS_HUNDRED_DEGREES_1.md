## ✅ CLOSED 2026-08-23 on the owner's instruction — the decision was made and applied

He answered it with a fourth option none of the three listed below anticipated:
*"we will use HorrorWastes instead of RockyCrags for any tile above 0C"* — and told DECIDE
to close this item immediately.

**Applied the same day**, `ashkarr_warm_crags_to_horror.py --apply`, committed `eb7da875`:
**339 tiles** moved, across `Knuckles` (78), `Tallow Ground` (58), `Glass Reach` (55),
`Grinding Floor` (44), `Rimewall` (41), `Sunreach` (35).
`AB_RockyCrags` **4,155 → 3,816**, span **101.8 → 82.0 °C**.

⭐ **It also dissolved the `HorrorWastes` shell defect for free** — that biome's own def is a
*dry region* with `Sand`/`Soil`/`SoilRich` terrain and `Plant_Agave`, i.e. a hot dry biome,
which is exactly what the warm band is. It fits there with no def change at all.

## ⚠️ What this item does NOT claim to have solved

`HorrorWastes` now spans **94.7 °C** (−74.9 … +19.8), because it holds the warm band AND the
468 cold nightside pockets. **The thermal problem moved; it did not go.**

🔑 **That residual is NOT lost — it lives on `HORROR_WASTES_ON_NIGHTSIDE_1`**, which owns the
468 pockets and is the item REP's incoming note bears on. ⛔ Do not re-file it here.

⚠️ **And `AB_RockyCrags`' creature cast is re-opened by this**, since every tile it had above
freezing now belongs to another biome. Also carried on the HorrorWastes item.

---

## 🔴 THE OWNER ANSWERED THIS, 2026-08-23 — and picked none of the three options

> *"we will use HorrorWastes instead of RockyCrags for any tile above 0C"*

**Applied the same day** by `src/RimMandrake/Utils/ashkarr_warm_crags_to_horror.py --apply`:
**339 tiles** moved, across `Knuckles` (78), `Tallow Ground` (58), `Glass Reach` (55),
`Grinding Floor` (44), `Rimewall` (41), `Sunreach` (35).

⭐ **It also dissolves the `HorrorWastes` shell defect for free.** That biome describes
itself as *"a dry region"*, its terrain is `Sand`/`Soil`/`SoilRich` and its one plant is
`Plant_Agave` — every field of it is a HOT DRY biome, which is exactly what the warm band
is. On this ground it fits with no def change at all.

## ⚠️ BUT THE THERMAL PROBLEM MOVED; IT DID NOT GO AWAY

| | tiles | span |
|---|---:|---|
| `AB_RockyCrags` | 4155 → **3816** | 101.8 → **82.0 °C** (−82.0 … −0.0) |
| `HorrorWastes` | 468 → **807** | 41.0 → **94.7 °C** (−74.9 … +19.8) ⚠️ **wider** |

🔑 **Both still span more than 80 °C**, because `HorrorWastes` now holds the warm band AND
the 468 cold nightside pockets at −74.9 … −33.9. **The open question is the 468 pockets**,
and REP's incoming note on the horror wastes is expected to bear on it. ⛔ Nothing was done
to them: the owner ruled on the warm tiles and only on the warm tiles.

⚠️ **This re-opens `AB_RockyCrags`' creature cast**, which was already worked. 339 of its
tiles — every one it had above freezing — now belong to another biome.

---

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
