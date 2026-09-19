# PYRELANDS_FIRE_WEB_COMMISSION_1

Owner sitting ruling, 2026-09-10 (four-card batch, `decisions_propagated.json`
round2, `BIOME_FAUNA_ASSIGNMENT_SITTING_1.md` §9a): "commission the fire-hawk
+ furnace-beast (irreplaceable igniters); recast Razorjack as fire-follower,
route Barbslinger as ash-grazer; burrower from homeless or third commission."

Full design brief: `design/Jawa/worldbuilding/biomes/the_pyrelands.md` §4.

## Scope — what this item is and isn't

The sheet's `new_defs` entries for fire-hawk and furnace-beast both carry a
`mechanic_load` note (C# twig-carrying fire-spread; C# heat aura and bed-down
ignition). That mechanics work has its own owed, unfiled item name
(`PYRELANDS_MECHANICS_1`) and is explicitly **not** this item's scope — this
item commissions the roster-level def (stats, art, biome placement) only.
Both new creatures behave as ordinary wild animals until that mechanic work
lands; said so in both the def file's header comment and the roster.

## What was built

**`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_PyrelandsFauna.xml`**
— two new ThingDef+PawnKindDef pairs:

- `RUT_FireHawk` — raptor (Bird body), predator, fire-adapted (ComfyTemperatureMax
  65, ArmorRating_Heat 0.3), tameable (ban 5 doesn't apply to this one).
- `RUT_FurnaceBeast` — megafauna (QuadrupedAnimalWithHoovesAndHorn), herd,
  non-predator grazer, heavy heat/armor stats, **enforced untameable** per
  hard ban 5 ("no tame furnace-beast") via
  `VEF.AnimalBehaviours.CompProperties_Untameable`
  (MayRequire=`oskarpotocki.vanillafactionsexpanded.core`) — the same
  mechanism Alpha Animals itself uses for `AA_FeraliskClutchMother`, verified
  in that mod's own source before reuse, not guessed.

Both are real generated art, not placeholders: filed through the live
`artpipe` daemon, `background: transparent`, one east-facing 256x256/320x320
sprite each. Records: `infrastructure/artpipe/done/pyrelands_firehawk_v1.*`
and `pyrelands_furnacebeast_v1.*`. Copied into
`src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/{FireHawk,FurnaceBeast}/`.
Single texPath reused across all three lifeStage graphics (no directional
facing set) — same lightweight pattern already used by this campaign's own
sea-beast defs (`SWBestiary/Defs/SeaBeasts`), not an invented shortcut.

**Razorjack recast, Barbslinger routed**: both are existing Alpha Animals
defs (`AA_Razorjack`, `AA_Barbslinger`) — no new art, just a roster/biome-cast
reassignment. Razorjack was not previously in this roster at all; added as
`fire-follower`. Barbslinger was in the roster's `evictions` list ("large
predator with no fire story"); moved to `fauna` as `ash-grazer`, reversing
that eviction per this ruling. Both wired into `ZBiome_Grasslands`'s
wildAnimals list in `BiomeCast_Ashkarr.xml` (the donor biome — Pyrelands has
no dedicated `RUT_Pyrelands.xml` biome-ownership file yet, so this follows
the same donor-cast pattern already used for every other not-yet-owned
biome in that file, e.g. how `RUT_TheForge`/`RUT_ExtremeDesert` were cast
before they got their own BiomeDef).

**The burrower — left open, not forced.** Checked `FrogDog`
(`mlie.starwarsanimalcollection`, sitting homeless from `the_contagion.json`)
as the obvious candidate: its eviction note claimed a "burrows-when-hungry"
special matching the sheet's burrower-grazer need. Read the live def
(`Races_Animal_SW.xml`) before trusting that note — it's a docile 70-year pet
species (petness 0.75, Wildness 0.10, `comps` empty), no burrow field or
comp anywhere. The note was simply wrong (confused with something else), not
a real candidate. **Corrected that note in `the_contagion.json`** rather
than leaving it to mislead the next pass. No other verified non-Earth
burrower-grazer turned up in the time this item had. `Orray` already covers
the roster's `burrowers` band (MEASURED "burrows underground when hungry"
special) but is a predator hybrid, not the sheet's pure grazer archetype —
left as-is; the dedicated grazer-burrower slot stays open for a third
commission if the owner wants one distinct from Orray. Recorded in the
roster's `new_defs` note rather than guessed at.

## Files changed

- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_PyrelandsFauna.xml` (new)
- `src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/**` (new art)
- `src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml` (wildAnimals additions)
- `design/Jawa/worldbuilding/biomes/rosters/the_pyrelands.json` (fauna/evictions/new_defs)
- `design/Jawa/worldbuilding/biomes/rosters/the_contagion.json` (FrogDog note correction)

## verify

Next full-list game load, on a map painted `ZBiome_Grasslands` (Pyrelands):
`RUT_FireHawk` and `RUT_FurnaceBeast` spawn as wild animals with real art
(not a missing-texture magenta placeholder); furnace-beast cannot be tamed
(Tame designator refuses or the comp's message fires); `AA_Razorjack` and
`AA_Barbslinger` spawn there too. No `Could not resolve cross-reference`
naming any of the four new wildAnimals entries.
