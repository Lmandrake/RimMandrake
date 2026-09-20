# BIOME_ROSTER_DEAD_SPECIES_REFS_1 — 23 species that silently never spawn

## why this was looked for

Owner, 2026-09-20: *"I feel like there were giant creatures in the extreme desert.
Like Krayt dragons etc. … I'm worried a mod retirement or something stripped
animals again."*

✅ **The Krayt dragons are fine** — `KraytDragon` 0.15 and `GreaterKraytDragon`
0.001 are both in `RUT_ExtremeDesert.xml`, and `mlie.starwarsanimalcollection` is
ACTIVE in the 621-mod list. Nothing stripped them.

🔴 **But the instinct was right.** Something else is silently gone.

## the defect, MEASURED 2026-09-20

Every owned `RUT_*` BiomeDef's `<wildPlants>`/`<wildAnimals>` parsed, each entry's
`MayRequire` packageId checked against the 621 ids in
`infrastructure/state/modlists/ModsConfig_full_plus_longhunger_2026-09-19.xml`:

| biome | dead entries |
|---|---:|
| `RUT_ExtremeDesert` | 7 |
| `RUT_Desert` | 7 |
| `RUT_AridShrubland` | 7 |
| `RUT_Greentide` | 1 |
| `RUT_FeverWood` | 1 |
| **total** | **23** |

| count | inactive mod |
|---:|---|
| 21 | `neronix17.outerrim.droiddepot` |
| 2 | `biomesteam.biomescaverns` |

⚠️ **Droid Depot specifically is absent while the rest of the Outer Rim family is
present** (`neronix17.outerrim.core`, `.galacticempire`, `.rebelalliance`,
`.furnitureanddecor` are all active). So this reads as a mod that was dropped,
not a family that was never installed.

🔑 **These are `MayRequire`-guarded, so there is NO crash and NO error.** They
simply never spawn. That is why it went unseen — and it is the opposite failure
mode from `BIOME_CAST_REFS_BREAK_MAPGEN_1`, where an UNGUARDED dead ref crashes
mapgen loudly. Guarded is safe and silent; silent is how a third of a roster
disappears without anyone noticing.

### what it actually costs

- **`RUT_ExtremeDesert`'s effective fauna is 16, not 23** — the 7 droids include
  entries at 0.1, 0.1, 0.08, 0.08, which are meaningful weights in a table whose
  top entry is 0.6.
- **`BMT_GiantLeaf` is the 4th-heaviest plant in `RUT_Greentide` at 1.0** (behind
  only AB_JungleTree 3.0, Hydenock 1.5, Jogan 1.2) and the 3rd in `RUT_FeverWood`
  at 0.8. A biome's headline flora, absent.

## separately found, NOT a retirement — three imports that never landed

Comparing `design/Jawa/worldbuilding/biomes/rosters/dune_sea_deep_desert.json`
(16 ruled fauna) against the shipped def:

| ruled import | commonality | git history |
|---|---:|---|
| `AA_SandLion` | 0.5 | **NEVER wired into any biome def** |
| `JOE_Cephalope` | 0.5 | **NEVER wired into any biome def** |
| `BMT_TruffleMole` | 0.5 | **NEVER wired** (and its mod is now inactive anyway) |
| `AA_Dunealisk` | 0.1 | wired, then correctly removed — see below |
| `AA_SpinedGow` | 0.15 | landed in `RUT_Scarlands` instead, not a loss |

Three of the card's biggest ruled imports, all at 0.5, were never put in the def
at all. That is not a retirement stripping them; it is the roster→def landing pass
being incomplete.

✅ **`AA_Dunealisk` ("giant-subsurface", 0.1) WAS deliberately removed** at
`7bad94185` (2026-09-10) when the owner retired Alpha Animals' whole `-lisk`
clade. That was correct — Cherry Picker cut the clade, and an unresolved
`wildAnimals` cross-ref is a known mapgen crash. ⚠️ But nothing replaced it, so
the Extreme Desert lost a giant and the card still expects one.

## also worth his eye — 12 unruled entries

`RUT_ExtremeDesert` carries 12 species the card's roster never ruled, including
plain **`Rat`** (unguarded, vanilla Core). The dune sea card bans
*"instantly-nameable Earth organisms"* outright as a standing recognizability
ban. `Rat` is exactly that.

## spec

1. **Decide per dead reference: restore the mod, port the species, or drop the
   row.** For Droid Depot this is really one question — do feral droids belong in
   the desert at all? They are very Jawa, and 21 entries is a deliberate-looking
   design choice that simply stopped working.
2. `BMT_GiantLeaf` → port to our own def (`DONOR_DEFS_PORT_TO_OURS_1`) or replace;
   Biomes! Caverns is retired for good and is not coming back.
3. Wire or formally drop `AA_SandLion` / `JOE_Cephalope`; decide whether the
   Extreme Desert gets a giant back in `AA_Dunealisk`'s place.
4. Rule on `Rat` and the other 11 unruled rows against the card's own bans.

⚠️ Most of this is absorbed by `DONOR_DEFS_PORT_TO_OURS_1` — do not solve it
twice. What is unique here is the **detection**, not the fix.

## 🔑 build the instrument, not just the fix

The real deliverable is a **lint that fails when a biome roster entry's
`MayRequire` names a mod outside the active list**, run in `run_selftests.py`.
Without it this recurs on the next retirement, exactly as the owner feared. The
check is ~20 lines and it is the only thing here that prevents a repeat.

⚠️ It must read the active list by PARSING `ModsConfig.xml`/a snapshot, never by
scanning it — `grep -c '<li>'` returns 48 against a real 631.

## verify

Zero biome roster entries name an inactive mod; the lint proves it and fails when
one is reintroduced.

## criteria

No species sits in a shipped biome table unable to spawn, and the next mod
retirement is caught by a test instead of by the owner's memory.
