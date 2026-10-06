# WYYYSCHOKK_IDENTITY_COLLISION_1 — two things named "wyyyschokk" once mandrake.rsw.shokk loads

## What this is

Filed by SHOKK_SKIN_SHRINK_1 (2026-09-26), which was explicitly told not to
resolve this by guessing. It moved the Shokk mod's mechanisms (bound/spit/
sun-scald/emergent-spawn) onto `RM_Ollathrix`'s own def in
`mandrake.rm.webwork` and shrank `mandrake.rsw.shokk` to a single skin patch
(`RSW_Shokk_OllathrixSkin.xml`, from `OLLATHRIX_OWNER_SPECIES_1`) that
overlays the canon Wyyyschokk label/description/art onto `RM_Ollathrix`'s
SAME defName. That mechanism move is done and closed; this item is the
separate identity question it surfaced but did not adjudicate.

## The two "wyyyschokk"s

| | `RSW_Wyyyschokk` | `RM_Ollathrix` (skinned) |
|---|---|---|
| home | `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Wyyyschokk.xml` (`MLIE_FAUNA_ABSORPTION_1` Wave C, 2026-09-18) | `src/RimMandrake/Webwork/Defs/ThingDefs_Races/RM_Ollathrix.xml` (`OLLATHRIX_OWNER_SPECIES_1`) + `RSW_Shokk_OllathrixSkin.xml` |
| body | own `RSW_Wyyyschokk` BodyDef | `BeetleLikeWithClaw` (shared) |
| tameable? | yes — `trainability Advanced`, `manhunterOnTameFailChance 0.80` | **no** — `wildness 1.0`, `trainability None` (ban 1: no tamed/traded/negotiated Ollathrix) |
| reproduction | `CompProperties_EggLayer` (real eggs, fertilized/unfertilized, hatch) | none — the nest/egg economy is a separate world Building, not this race's own reproduction |
| shearable | yes, `RSW_WoolWyyyschokk` | no |
| combatPower | 600 | 160 |
| `wildBiomes` | `TropicalRainforest 0.8`, `TropicalSwamp 0.4`, `TemperateSwamp 0.2`, others near-zero — NOT the Webwork/Ash'karr specifically | none set here — wired into `RM_Webwork`'s own `wildAnimals` at 0.15 |
| wired into any biome's `wildAnimals`? | **no** — homeless per its own build note | yes, `RM_Webwork` |
| other consumers | `TrophyCraft`'s fang-drop recipe (`RSW_TrophyCraft_WyyyschokkFangDrop.xml`), `UtinniPatches/AnimalTolerances_Ashkarr.xml` | the Webwork's own mechanics (mouth-loom spit, sun-scald, ambush, web-sense once built) |

They are **not the same creature under two names** in any mechanical sense —
`RSW_Wyyyschokk` is a generic, tameable, egg-laying Star Wars bestiary entry
built for use across any Star Wars scenario/biome (the `SWBestiary` catalog's
own shape), while `RM_Ollathrix` is the Webwork's bespoke, untameable owner
species with its own ambush/venom/loom mechanics. They are also not a
`defName` collision — the game loads both fine, nothing crashes. What exists
is a **label/identity collision**: once `mandrake.rsw.shokk` is loaded, a
player's bestiary/animals tab shows two different, unrelated creatures both
labelled "wyyyschokk" (`RSW_Wyyyschokk` and `RM_Ollathrix` wearing the skin
patch), and `RSW_Wyyyschokk` itself is unwired into any biome (dormant dead
weight, not currently seen by anyone) while other mods (TrophyCraft,
AnimalTolerances) already reference it by defName.

## Options, not a recommendation

1. **Leave both.** `RSW_Wyyyschokk`'s own `wildBiomes` are weighted to
   tropical biomes Ash'karr (a desert world, CLAUDE.md) does not have, so in
   practice it may never spawn in this campaign at all — the label collision
   is a bestiary/dev-mode curiosity, not a live gameplay collision. Cheapest,
   does nothing.
2. **Retire `RSW_Wyyyschokk`** (Cherry Picker cut or full removal) now that
   the Webwork has its own owner species wearing the same name. Breaks
   `TrophyCraft`'s fang-drop patch and `AnimalTolerances_Ashkarr.xml`'s
   reference — both would need their own retarget/removal pass first.
3. **Rename `RSW_Wyyyschokk`'s label** to something else (it stays a
   legitimate generic Star Wars bestiary port, just not called "wyyyschokk"
   any more) — avoids the collision without touching its mechanics or its
   consumers, but needs a new label the owner picks (this is exactly the
   kind of naming call this campaign routes through him, not a generator).
4. **Wire `RSW_Wyyyschokk` into a different biome under a different label**
   as a distinct tropical Star Wars creature, keeping "wyyyschokk" as
   `RM_Ollathrix`'s sole claim to the name.

## Watch out

- Whoever picks this up should re-verify `RSW_Wyyyschokk`'s `wildBiomes`
  against whatever the eventual world-paint pass puts on the map — CLAUDE.md's
  "a biome with zero tiles is not a defect" applies the same way here: don't
  treat "not currently spawning" as proof it's safe to ignore forever.
- `TrophyCraft`'s fang-drop recipe and `AnimalTolerances_Ashkarr.xml` both
  reference `RSW_Wyyyschokk` by defName — any retire/rename must update or
  explicitly retarget both, not just delete the race def.
- This is a naming/identity call in the same family as the Sekkulaath/dianoga
  and other "owner picks the name" precedents this sitting already set — not
  a mechanical bug, a decision for a card.

## caused-by
SHOKK_SKIN_SHRINK_1
