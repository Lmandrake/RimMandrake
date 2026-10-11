# Off-tone mods: deep dive before the cut

Owner order (card C19, click "Study first", 2026-10-10): before cutting the off-tone mods, find out what each
gives and what depends on it. Offline study (no bridge, no game). FOUNDRY, 2026-10-10. Proposed ticket names
pass `rimflow namecheck`; none is filed. Torment Master (`vlvop.tormentmaster.expansion`) is not installed and
leaves the list with no study.

## Summary

| mod | what the player actually gets | ours depends on it? | in the canonical save | verdict |
|---|---|---|---|---|
| Metal Pipe `flangopink.metalpipe` | 4 smithable blunt clubs that can also be **thrown** (a ranged verb) with the meme clang; the "supermassive" one explodes | **yes, by design note**: our Jawa roster comment counts on it, but the tag has 18 other weapon carriers | 1 pipe in a dead world pawn's inventory; filters/price history | **cut-now** (fix the roster comment in the same commit) |
| Metal Pipe Horseshoe `flangopink.metalpipehorseshoe` | the clang replaces the vanilla horseshoe-pitch sound and sprite | no | nothing | **cut-now** with Metal Pipe |
| AuthenticTantrumNoises `kshtantrumsounds.mod` | "Angry German Kid" audio plays on every tantrum | no | nothing | **cut-now** |
| Medieval Melee Sounds `bonible.medievalmeleesounds` | replaces 7 vanilla melee impact/dodge/deflect sound folders with comedy clangs | no | nothing | **cut-now** |
| FancyRats `armoredampharos.fancyrats` | 1 pet-rat animal (26 coat variants), wild in temperate/tropical biomes and Arid Shrubland | 1 inert eviction patch | filters, 1 auto-slaughter row; no rat | **cut-now** (pair) |
| FancyRats+ `tyrannidae.fancyratsplus` | 0 defs; reskins FancyRat **and vanilla `Rat`** ("brown rat", new art) and Advanced Biomes' poison rat | no | nothing | **cut-now** (pair) |
| Dark Ages: Crypts `van.dacrypts` | 2 research projects and ~25 grave-goods buildings (coffins, sarcophagi, wall tombs, candles, braziers, gargoyle/demon statues, skull walls) | ResearchRetag moves its 2 research projects to our tab | 2 research-progress keys; filters | **cut-now** (prune 2 retag rows first) |
| Dark Ages: Beasts, **troll line only** `van.beasts` | 2 troll animals, 6 troll incidents incl. the two letters, burrows, troll goods | **yes**: our `RM_Uttaqar` renders with this mod's rock-troll texture; yield patches; faction zeroing | filters/price history; no troll, no troll faction | **cut-at-biome-sitting** by Cherry Picker; the mod stays |
| Dredge Aberrations `aqued.dredgeaberrations` | 7 rare fish catches; eating one gives a **permanent** buff (one grants a teleport ability). It adds **no creatures** | no | filters, price history | **absorb-then-cut** (the idea only; cut now) |
| Ideology Virtues `dimonsever000.ideologyvirtues` | a "preferred traits" and a "disapproved traits" precept, with mood for believers who have or lack them | no def use by us | **41 live precepts across 11 of our 13 faction ideoligions** | **absorb-then-cut**, after a save load probe |

**Surprises.**
1. **Ideology Virtues is not dead weight.** The registry's "no precept use found" checked only our authored
   export. The canonical save's NPC ideoligions carry 41 `IdeologyVirtues.Precept_Virtue` instances: The Contract,
   The Ascendant Genome, The Balance, The Continuity Protocol, Meckgin, The Reckoning of Debts, The Weight, The Green Oath,
   The Sun-Debt, The Covenant of Free Wells and The Rising Order. Only The Salvation (the player's) and Astropolitan
   have none. These are serialized C# types.
2. **Our `RM_Uttaqar` (FloodedCanyon and the Cracked Lands roster) draws `van.beasts`' rock-troll texture** as a
   temporary placeholder (`texPath Animal/RockTroll/...`). Uninstalling `van.beasts` would leave it with no texture.
   Trimming the troll defs with Cherry Picker does not affect it.
3. **Metal Pipe is wired into our Jawa faction by name.** `JawaFactionRoster.xml` (BAREHANDED_MELEE_FALLBACK_1)
   explains `NeolithicMeleeBasic` as "the scrap metal-pipe cluster". The tag has 18 other weapon carriers, so the
   Jawa still get weapons, but the comment becomes false.
4. **Dredge Aberrations never reaches our seas.** It patches vanilla's `RareFishingCatches_*` tables. Every one of our
   sea and shore biomes points `rareCatchesSetMaker` at its own `RM_Rare*Catches` / `RUT_Rare*Catches` table, so
   its catches appear only in vanilla or donor biomes.
5. **The troll letters cannot fire on the recorded planet.** Every troll incident and the burrow map-spawn are
   limited to Tundra, BorealForest, ColdBog, GlacialShield and GlacialPlain. The tiles CSV (exported 2026-09-12; a
   record, not the live planet) has 0 tiles of any of them. That still has to be checked against the live planet,
   and against the repaint.

## Method and instruments

- **Disk.** Read each mod's About.xml, LoadFolders.xml, Defs and Patches from workshop 294100, keeping only the 1.6 folders
  plus root and `Common`. Assembly names and sizes were listed. Script `/home/mandrake/.seat-tmp/odd/inv.py`, output
  `inv.txt` (scratch, not committed).
- **Defs at runtime.** `measure` over the def dump (`defs.sqlite`, 638 mods, fingerprint `95728f758cebfdc8`, captured
  2026-10-04). Per-mod def sets include generated defs (blueprints, frames, corpses, meat).
- **Our references.** All 8 off-tone defName sets plus texture paths were matched against every XML under `src/` at
  `origin/main` `cb715492a`, using `refs.py`. Sanity probe: `korrum` occurs 44 times in the same XML. Every
  `packageId` mention was also found with `git grep`. Besides the patches below, the 8 hits per mod are mod-list
  copies: `src/Jawa/ideoligion/{MandrakeJawa.xtp,The Salvation.rid,witness/*.rid}`, which list the mods of the
  exporting game but use no def from them, and 5 GimmeSomeSlack northstar result JSONs. Neither is a dependency.
- **Save.** A streaming `iterparse` of a copy of `Saves\CANONICAL_ASHKARR_START_2026-09-12.rws` (sha256 prefix
  `1ff329161abeaa8c`, mtime 2026-10-09). Every text node was matched exactly against each mod's def set. Sanity
  probes: `Human` 864, `Steel` 917, `Rat` 4. The save's `modIds` lists all ten mods. No Thing is placed on a map
  from any of the ten mods. Hit classes: ThingFilter `allowedDefs` (food restrictions, pack-up/goods/journey
  filters), `priceHistoryRecorders`, auto-slaughter configs, drug policies, and the cases named per mod.
  **Effect of removal on load**, MEASURED in the engine for precepts (`Ideo.ExposeData` removes a null precept and logs
  "Some ideoligion precepts were null after loading."). For filters and price keys it is INFERRED from the standard
  Scribe behaviour: the dead reference is dropped with a "Could not load reference" error, and a re-save cleans it.
- **Cherry Picker.** The live config `Config\Mod_3521312241_Mod_CherryPicker.xml` (2026-09-24) holds 2,133 cuts. Of these,
  11 are `van.beasts` (owlcats, silver mole and their eggs/meat/leather) and none is from the other nine mods.
  It already cuts 9 IncidentDefs and 8 FactionDefs, so cutting incidents is established practice.
- **Uninstall test.** The `GPT_REVIEW_DISPOSITION.md` G7.22 rule: a mod may be uninstalled when it has no retained
  behaviour, no consumer and no saved state. Otherwise Cherry Picker trims it.

## Per-mod sections

### Metal Pipe (`flangopink.metalpipe`) and Metal Pipe Horseshoe (`flangopink.metalpipehorseshoe`)

**Gives.** `Melee_MetalPipe`, `Melee_MetalPipeValved`, `Melee_MetalPipeLong` and `Melee_MetalPipeSupermassive`. They are
medieval blunt weapons, smithable after Smithing, tagged `NeolithicMeleeBasic` and `MedievalMeleeBasic`. Each also has
a `Verb_Shoot` that throws the pipe about 12 tiles. The projectile classes in `MetalPipe.dll` (6 KB, one
`[StaticConstructorOnStartup]`) play the clang on impact, and the supermassive one explodes. The descriptions are
meme text ("This weapon is part of human biology..."). The Horseshoe add-on is a 1-def SoundDef plus 2 patches that
replace the vanilla `Horseshoe` fleck's land sound and texture.

**Player experience.** Tribal and medieval raiders, our Jawa among them, carry pipes. Every hit or throw plays the
meme sound.

**Ours.** `src/RimUtinni/UtinniPatches/Defs/PawnKindDefs/JawaFactionRoster.xml`: the `RUT_Jawa_TradeMoot_Heavy` and
`RUT_Jawa_Junkers_Grunt` kinds list `NeolithicMeleeBasic`, and the comment explains it as the metal-pipe cluster.
Those kinds do not depend on the pipe: the dump has about 18 other ThingDefs with that tag outside Metal Pipe, among them
Core `MeleeWeapon_Club`, `MeleeWeapon_Knife` and `MeleeWeapon_BreachAxe`, Jawa Armoury `GS_Gaffi`, and VFE Tribals
`VFET_Chunk` and `VFET_Stake`. Nothing else of ours references either mod.

**Save.** 1 `Melee_MetalPipe` in a dead world pawn's inventory, 2 `rememberedWeapons`, and filters and price history.
All of it is dropped on load with errors, and none is on a map.

**Useful despite the tone?** The weapon idea (a scrap melee weapon you can also throw) suits a Jawa salvage culture.
It is done in XML by putting a `Verb_Shoot` beside the `tools`. Only the clang and the explosion need the DLL. That
is a design note, not a reason to keep the mod.

**Cut.** Uninstall both. Neither passes the uninstall test because of anything retained: no consumer, and the saved
state is one dead pawn's item. In the same commit, rewrite the roster comment so that it names a carrier that is
staying (`GS_Gaffi` or the Core club), or name a Jawa scrap club we would make ourselves.
**Verdict: cut-now.** Ticket `METALPIPE_PAIR_RETIRE_WITH_ROSTER_NOTE`.

### AuthenticTantrumNoises (`kshtantrumsounds.mod`)

**Gives.** `SoundDef kshTantrum` (13 ogg clips) and `EffecterDef kshTantrum`. A conditional patch adds or replaces
`stateEffecter` on the vanilla `MentalStateDef Tantrum`. No code.
**Experience.** A real child's screaming plays over every tantrum. **Ours.** No use. **Save.** Nothing.
**Absorb?** No. A tantrum audio cue is worth having only with our own, in-world voice.
**Cut.** Uninstall. **Verdict: cut-now.** Ticket `OFFTONE_SOUND_MODS_RETIRE_FROM_LIST` (shared with the next mod).

### Medieval Melee Sounds (`bonible.medievalmeleesounds`)

**Gives.** 0 defs. Ten 1.6 patch operations repoint the `clipFolderPath` of seven vanilla SoundDefs to its own 65 ogg
clips: `MeleeHit_Metal_Sharp`, `MeleeHit_Metal_Blunt`, `MeleeHit_Wood`, `MeleeHit_Stone`, `Pawn_Melee_Punch_Miss`,
`Pawn_MeleeDodge`, `Pawn_Melee_Punch_HitPawn` and `Deflect_Metal`. No code.
**Experience.** Every melee exchange in the game, whatever the weapon's own sounds, plays "Monty Python-esque" clangs.
**Ours.** No use. **Save.** Nothing. **Cut.** Uninstall. The vanilla sounds come back.
**Verdict: cut-now**, in `OFFTONE_SOUND_MODS_RETIRE_FROM_LIST`.

### FancyRats (`armoredampharos.fancyrats`) and FancyRats+ (`tyrannidae.fancyratsplus`)

**Gives.** FancyRats adds `ThingDef`/`PawnKindDef FancyRat`, a 0.15-body-size pet rat with 26 coat variants. Its
`wildBiomes` are TemperateForest, TemperateSwamp, TropicalRainforest, TropicalSwamp and AridShrubland. FancyRats+ adds
0 defs and requires FancyRats. Its 17 patch operations replace FancyRat's art, label and description and add the
`AnimalPet` trade tag. They also **replace vanilla `Rat`'s label ("brown rat") and its PawnKind `lifeStages` art**,
and reskin Advanced Biomes' `PoisonRat` (FindMod-guarded).
**Experience.** Pet rats in traders' stock and in vanilla temperate wilds, and every vanilla wild rat drawn with the
"plus" art.
**Ours.** `UtinniPatches/Patches/BiomeCastEvictions_WildBiomes.xml` holds 2 conditional removals of
`FancyRat`/`Corpse_FancyRat` × AridShrubland. They are inert once the def is gone. `UtinniPatches/About.xml` has a
`loadAfter` for ordering only. Our uses of vanilla `Rat` are `RUT_LabRat`, which brings its own white `lifeStages` on
Core's texture, `RM_Lirrith` (`useMeatFrom Rat`) and the Rust Cathedral genstep. After the cut, the cathedral's wild
rats look like vanilla rats again, and the lab rat does not change.
**Save.** Filters, price history, 1 auto-slaughter row. No rat.
**Roster.** None of our biome rosters names `FancyRat`. On the recorded planet its `wildBiomes` match 0 tiles, so a
biome sitting is not needed for it.
**Absorb?** No. "Rats as pests" is already ours (`RUT_LabRat` falling in pods; `RM_CompVerminBreeder` vermin).
**Cut.** Uninstall both together. FancyRats+ goes first, or both in one commit. Delete the 2 FancyRat eviction
operations and the `loadAfter` in the same change, so that no live doc points at a gone mod.
**Verdict: cut-now.** Ticket `FANCYRATS_PAIR_RETIRE_FROM_LIST`.

### Dark Ages: Crypts and Tombs (`van.dacrypts`)

**Gives.** Research `DA_Catacombs` and `DA_BloodflameCatacomb` on a "Dark Ages" tab. Buildings: coffin, grand sarcophagus,
wall tomb (`WallTombs.dll`, 7 KB, source included under `Source/`), burial urn, heroic memorial, skeleton, imp,
gargoyle and demon statues, ossuary skull wall, sepulchral braziers, statues and reliquaries (the reliquaries are
Ideology-gated), candles and candelabras in plain, darklight and bloodflame variants, and a skull torch (VFE-gated).
5 ThoughtDefs, mostly for bloodfeeders near bloodflame light. Patches add its graves to the meditation-focus
`NearbyGraves` lists and to Royalty throne-room requirements. **It adds no ruins, loot sites or map generation.**
**Experience.** A gothic funerary build menu.
**Ours.** `src/RimUtinni/ResearchRetag/Patches/RUT_ResearchTabAssign.xml` moves both research projects onto
`RUT_Tree_Scavenging`. They are conditional and go inert if the defs are absent. Its `About.xml` has a `loadAfter`.
The facts' `def_ref` edge from `dizzy.candlesandmeditation` is false: the word "Candles" is a label there, not a reference.
**Save.** 2 research-progress keys and 134 filter or price-history entries. No building is placed.
**Absorb?** Crypts as ruin loot sites, no: the mod has no site content. A Jawa memorial or burial-urn
building could come from our own art if wanted, and nothing has to be ported for that.
**Cut.** Uninstall. It retains no behaviour we use, has no consumer once the 2 retag rows go, and its saved state is
research keys only. Prune the 2 operations and the `loadAfter` first.
**Verdict: cut-now.** Ticket `DACRYPTS_RESEARCHRETAG_PRUNE_UNTICK`.

### Dark Ages: Beasts and Monsters (`van.beasts`), troll line only

Scope, per C19: the `DA_Troll` faction is already decided (zeroed at world creation by
`UtinniPatches/Patches/FactionSlate/OnlyOurFactions.xml`; the save has no troll faction, only one `ignoredFactions`
entry). The rest of the mod, about 20 other creatures with 273 patch references from 5 of our mods, is outside this
study and stays.

**The troll line.**
- Animals: `DA_BeardedTroll`, wild in Tundra, ColdBog, BorealForest, IceSheet, GlacialPlain, GlacialShield and Dark
  Forest, and `DA_RockTroll`, which has no `wildBiomes` and arrives only through incidents. There is also
  `DA_HibernatingRockTroll`, a rock that a troll bursts out of.
- Incidents: `DA_TrollOutbreak_Incident` ("pale scourge", a ThreatBig game condition), `DA_TrollBurrow_Incident`,
  `DA_TrollWander_Incident` (baseChance 0), `DA_HibernatingTroll` and `DA_MigratingRockTroll`. Plus a VEF
  `ObjectSpawnsDef` that places burrows at map generation.
- Goods: `DA_TrollMeat`, `DA_Leather_Troll`, `DA_Leather_RockTroll`, `DA_Sangonite`, `DA_TrollRug`, and the two burrows.
- The two letters named in the card are the pale scourge condition text and the burrow letter
  ("Trolls have dug their way out from underground...").
- All of it is driven by `Bestiary.dll` and `EmergingAnimals.dll`.

**Ours.**
- `src/RimMandrake/FloodedCanyon/Defs/ThingDefs_Races/RM_MuttavaqUttaqar.xml`: `RM_Uttaqar` is our port of the rock
  troll, already cast in `RM_FloodedCanyon_Biome.xml` and `WildAnimals_CrackedLands.xml`. It has no def dependency on
  the donor, but **its texPaths point at the donor's `Animal/RockTroll/*` textures** as a temporary placeholder.
- `src/RimUtinni/Doctrine/Patches/MegafaunaYield.xml`: 4 conditional blocks setting the two trolls' Meat and Bone
  amounts. They go inert if the defs are absent.
- `OnlyOurFactions.xml`: the `DA_Troll` zeroing.
- `design/Jawa/fauna/cast_assignment.csv` row 58 still assigns `DA_RockTroll` to `RUT_CrackedLands`.
  `cracked_lands_bedazzle_cast_2026-09-28.md` superseded that ("donor `DA_RockTroll` row leaves, ours replaces"), and no
  live roster names either troll.

**Save.** No troll pawn, no burrow, no condition. Only filters, price history, 2 auto-slaughter rows and the one
`ignoredFactions` entry.

**Roster consequence.** None today. Neither troll is in any of our wildAnimals rosters. Bearded-troll habitat is 0
tiles on the record, and the rock troll is already replaced by `RM_Uttaqar` in the Cracked Lands roster. Under the
eviction rulings this still goes to a biome sitting rather than a sweep. Its natural sitting is the Cracked Lands /
Flooded Canyon one that already ruled the uttaqar port.

**Cheapest safe cut.** Use Cherry Picker, never an uninstall, because the mod has 273 references from 5 of our mods.
Cut `DA_BeardedTroll`, `DA_RockTroll`, `DA_HibernatingRockTroll`, the 5 troll IncidentDefs, the 2 burrows, `DA_TrollRug`
and the troll goods, following the owlcat and silver-mole precedent. Before that:
1. The uttaqar gets its own art. A trim does not delete textures, so this is needed for the uninstall that the
   port-everything ruling (C01) eventually brings, not for the trim.
2. Prune the 4 MegafaunaYield troll blocks in the same commit.

Until the trim lands, the letters are already unreachable on the recorded planet (surprise 5).
**Verdict: cut-at-biome-sitting** (Cherry Picker trim; the mod stays for its other creatures).
Tickets: `TROLL_LINE_CULL_BY_CHERRY_PICKER`, `VAN_BEASTS_PRUNE_TROLL_PATCH_ROWS`, `UTTAQAR_REDRAW_OFF_DONOR_TEXTURE`.
Add `TROLL_LETTERS_SILENCE_UNTIL_CULL` only if a live check finds a troll-eligible biome on the planet.

**Absorb.** The petrification hediff is already ported. Still owed, already noted in the uttaqar header: the
dormant-disguise ("a strange stone formation wakes up") mechanic from `EmergingAnimals`, which is C#. It is a strong
fit for crag giants and belongs in `CRACKEDLANDS_MECHANICS_BUILD_1`.

### Dredge Aberrations (`aqued.dredgeaberrations`)

**Gives.** Category `Aqued_Aberrations`; 7 fish items (`Fish_AllSeeingCod`, `Fish_AstralIcefish`, `Fish_CursedFangtooth`,
`Fish_GrotesqueMaquerel`, `Fish_NightwingCatfish`, `Fish_Voideye`, `Fish_VoltaicGrouper`). Each grants, when eaten, a
**permanent** hediff: shooting accuracy, meditation focus, melee damage with a curse, beauty, night combat, psychic
sensitivity plus the `Aqued_Teleportation` ability, or move speed. 5 patch operations add them to Odyssey's
`RareFishingCatches_Temperate/Tropical/Hot/Cold/Glowforest`. No C#, and **no creatures**. The audit card's
"aberrant sea catch for the sea floor" premise does not hold: there is nothing to put on a floor map. The
descriptions are jokey ("you sicken me"), and the name and theme come from the game *Dredge*.
**Ours.** No reference. Every `rareCatchesSetMaker` under `src/` names one of our own tables (`RM_RareGreyCatches`, `RM_RareChillCatches`,
`RM_RareScaldCatches`, `RM_RareTwilightCatches`, `RM_RareGreentideCatches`, `RM_RareSandCatches`,
`RM_RareOasisCatches`, and the RUT/RSW twins), all parented on `RareFishingCatchesBase` and not on the patched tables.
So the aberrations can be caught only in vanilla or donor biomes.
**Save.** Filters and price history only.
**Useful?** The **mechanic** is good and needs no code: a rare catch that changes the eater for good. It fits the
fishing-and-floor rulings (each sea owes floor residents and a catch) as a rare "deep catch" tier in our own voice,
one per sea, using stock `IngestionOutcomeDoer_GiveHediff` with a stage-less permanent hediff. Not the content and
not the jokes. Only the teleport one needs Royalty's skip ability, which every player has by the all-DLC ruling.
**Cut.** Uninstall now. Nothing waits on it. **Verdict: absorb-then-cut**, where the absorb is a design note, so
the cut does not wait. Tickets `DREDGE_ABERRATIONS_UNTICK_ABSORB_IDEA` and `RARE_CATCH_DESIGN_PERMANENT_BUFF_EATING`.
Take the second to the sea sittings.

### Ideology Virtues (`dimonsever000.ideologyvirtues`)

**Gives.** `IssueDef`/`PreceptDef PreferredTraits` and `DisapprovedTraits`, plus `ThoughtDef PreferredTrait` and
`PreferredTrait_Self`. `IdeologyVirtues.dll` (18 KB, Harmony, a settings screen) defines `Precept_Virtue`, which holds
one trait, and `DefModExtension_MemeDefVirtues`. 28 patch operations attach that extension to 20 vanilla and DLC
memes, so that generated ideoligions roll virtue precepts that fit their memes. Believers get mood for having the
preferred trait or lacking the disapproved one, and opinion of others by the same test.
**Experience.** NPC faction ideoligions show lines such as "Traits: disapproved Jealous" or "preferred Masochist",
and their converts carry those moods.
**Ours.** No def use. The authored ideoligion export lists the mod in its mod list only. **But the world's ideoligions
use it**: the save holds 41 `IdeologyVirtues.Precept_Virtue` precepts on 11 of the 13 ideoligions, each one the
ideoligion of one of our `RUT_Jawa_Culture_*` factions (named in Surprise 1). For example, The Weight has 5. The
player's The Salvation has none.
**What removal does to the save.** MEASURED from `Ideo.ExposeData`: the unresolvable precepts load as null, are
removed, and "Some ideoligion precepts were null after loading." is logged once per ideo. The ideos survive, minus
those precepts. No thoughts are saved (both ThoughtDefs are situational; the census found 0).
**Useful?** Yes, in principle. A Jawa faith that **prefers Greedy** and **disapproves of** Ascetic or Kind is
characterful scavenger ethics, and the faction ideoligions already roll them. That would be our own small precept
pair. Vanilla Ideology has no trait-preference precept; Biotech's xenotype preferences are a different axis.
**Cut.** Uninstall after one load probe of the canonical save without the mod (the minimal list is fine), confirming
the 11 ideos load clean apart from the expected error, then re-save. Or let the world remake regenerate the ideos.
Do not trim with Cherry Picker. A cut PreceptDef leaves the same nulls and keeps the DLL's Harmony patches running.
**Verdict: absorb-then-cut.** First judge whether our faction ideoligions should carry authored trait virtues.
Tickets `TRAIT_VIRTUE_PRECEPT_ABSORB_JUDGE` and `IDEOLOGY_VIRTUES_RETIRE_AFTER_SAVE_PROBE`. If the judgement is no, the
cut needs only the probe.

## Order of work

1. One commit: untick the sound pair, the Metal Pipe pair (with the roster comment fix) and the FancyRats pair
   (with their eviction rows). There is no consumer and no placed state.
2. Prune the 2 Crypts ResearchRetag rows, then untick Crypts.
3. Untick Dredge. File the rare-catch design note for the sea sittings.
4. Ideology Virtues: the trait-virtue judgement, then the save load probe, then untick.
5. The troll line: at the Cracked Lands / Flooded Canyon sitting, Cherry Picker trim plus the MegafaunaYield prune.
   Uttaqar art is owed before any future uninstall of `van.beasts`.

Every untick follows RETIREMENT WAVE 1 step 0 in `mod_audit/ACTIONS_NOW.md` (back up FULL.LATEST, the Cherry Picker
config and the canonical save). This census stands in for `DOOMED_MODS_CENSUS_SAVE_PLACEMENTS` for these ten mods. It
was offline and it decides nothing live.

## Review disposition

(pending)
