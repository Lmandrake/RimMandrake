# STACKCOUNT_FILEPATH_REDX_SWEEP_1

228 live "Collection cannot init" errors from a full-load Player.log: defs pointing a
`Graphic_StackCount`/`Graphic_Random`/`Graphic_Collection` `texPath` at a FILE, not a
folder, render red-X. `860b9e0f9` (SCALD_FLOOR_PASS_1) fixed the pattern for the Scald
fish tables: owned art moves into a real folder (numbered/lettered variants), a
borrowed single-file placeholder gets `graphicClass` overridden to `Graphic_Single`.
This item is the wider sweep the title asked for.

## census (measured)

Source: `Transient/Player.log.geneticrim_ctor_nre_2026-09-25` (36,595 lines, last
written 2026-09-25 00:20:36, full load on 627 active mods — `harvest_log.py --stale-ok`
confirms build 1.6.4871 rev591, no exit marker). The other two logs named in the task
were checked and ruled out: `Player.log.before_COLD_LOAD_RUN_SHEET_4_2026-09-23` is a
1,625-line partial/aborted log with only 40 hits (too short — not a full load); the
live `/mnt/c/.../Player.log` (24,407 lines, mtime 2026-09-25 10:37, still growing) is a
narrower dev/quicktest session with 145 hits and was avoided both because it may be
mid-session for another seat and because it is not a full-load census.

Instrument: `measure count-errors` does not bucket this message (it groups
Exception/stack-trace errors, not this Warn-shaped one-liner), so the literal count
came from a direct-read Python script (not grep — the `block_blind_scan.py` hook
correctly refused a bare `grep -n`), reading every line and printing exact-text
literal matches, which is a legitimate "does this string occur, and where" search per
`measuring-large-artifacts`, not a severity scan.

**MEASURED 228** literal `Collection cannot init: No textures found at path X` lines,
**117 distinct texPaths**, occurrence counts 1–7 each (full list:
`/tmp` scratchpad, not committed — texPaths and defNames are all reproduced below).

## what "228" actually contains

Cross-referencing every distinct texPath against the current worktree (which already
contains 39 commits after the log was captured, including `860b9e0f9` and a wider
wave of the same fix applied since) split the 117 into three real categories:

1. **Already fixed before this pass** (~65 of 117 texPaths — the whole Scald/GreySea/
   PropaneLake/TwilightSea/Weeping-Stones/Cracked-Lands/Greentide fish-catch borrowed-
   placeholder cluster: ToxicMeat_a/b/c, Echeveria A–F, Schlumbergera A–D, JadePlant
   A–C, AloeVera A–C, SnakePlant A–C, PincushionPlant A–C, SweetheartPlant A–B, Peyote
   A, BloddleA, JawaClaimRumour, plus `RUT_ScaldWreckHull/Tank/Frame`'s folder+`_A`
   convention). The log predates these fixes (00:20 vs `860b9e0f9` at 08:00 the same
   day, plus later same-pattern fixes across the other fish tables) — confirmed on
   disk, every one of these now carries `graphicClass>Graphic_Single` or the correct
   `_A`-suffixed folder. **No action needed**; do not re-"discover" these.

2. **Genuinely broken, fixed this pass** — 28 defs across 14 files, all the same
   pattern: `graphicClass` StackCount/Random (explicit or inherited from
   `FishBase`/`ResourceBase`/`BaseFilth`) left un-overridden while `texPath` points at
   one borrowed or owned single PNG. See "fixed" below.

3. **Owed art, out of scope for this item** (~50 of 117 texPaths) — `texPath` names a
   folder that does not exist at all yet (no file, no folder, confirmed by filesystem
   walk of every `Textures/` root in the worktree). This is the same shape as a biome
   at zero tiles: absence of generated art is not a texPath-vs-graphicClass
   misconfiguration, and forcing a fix here would mean inventing placeholder art this
   item was never asked to generate. Full list below, for whoever picks it up.

## fixed (28 defs, 14 files, all `graphicClass` → `Graphic_Single`)

| texPath | defName | file |
|---|---|---|
| `Things/Plants/AB_CrystalHorn/AB_CrystalHornA` | RUT_LampBlack | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Items/RUT_TwilightFish_Niim.xml` |
| " | RUT_LampBlack | `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_TwilightFish_Niim.xml` |
| " | RUT_SaltCameo | `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_GreySeaFish_Items.xml` |
| " | RUT_AuroraGlass | `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_PropaneLakeCatch_Items.xml` |
| " | RUT_SeepStone | `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_WeepingStonesFish_Items.xml` |
| " | RUT_BrinePlate (had no override at all — added one) | `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_WastelandBrine_Items.xml` |
| `Things/Item/Resource/RUT_Greenwood` | RUT_Greenwood (own def) | `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_Greenwood.xml` |
| `Things/Item/Resource/RUT_Hardwood` | RUT_Hardwood (own def) | `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_Hardwood.xml` |
| `RotSporeKit/Things/Item/GlowGoo/GlowGoo_A` | RM_LiveIngredient_RegenerantVeil | `src/RimMandrake/TheRot/Defs/ThingDefs_Items/RM_RotSporeKit_GuardianGroves_Ingredients.xml` |
| `RotSporeKit/Things/Item/MushroomLog/MushroomlLog_a` (sic — real texPath, typo is upstream) | RM_LiveIngredient_AgelessCap | same file |
| `RotSporeKit/Things/Item/ThrumbungusShroom/ThrumbungusShroom` | RM_LiveIngredient_EuphoricCrown | same file |
| `RotSporeKit/Things/Item/GlowGoo/GlowGoo_A` | RM_Tea_AgeReversal, RM_Symbiont_Nightwake, RM_LivePrep_ToxicInjection | `src/RimMandrake/TheRot/Defs/ThingDefs_Items/RM_RotSporeKit_LivePreparations.xml` |
| `RotSporeKit/Things/Item/GlowGoo/GlowGoo_B` | RM_Tea_Bioregeneration, RM_Symbiont_Sheenblood | same file |
| `RotSporeKit/Things/Item/MushroomLog/MushroomlLog_a` | RM_Symbiont_Mycoid | same file |
| `RotSporeKit/Things/Item/MushroomLog/MushroomLog_b` | RM_Symbiont_Quickflesh | same file |
| `RotSporeKit/Things/Item/SpiderHead/SpiderHead` | RM_ChitinPlating | `src/RimMandrake/TheRot/Defs/ThingDefs_Items/RM_RotSporeKit_Resources.xml` |
| `Things/Plant/RM_GiantLeaf/RM_GiantLeaf_a` | RM_GiantLeaf (RM_RawGiantLeaf inherits `PlantFoodRawBase`'s own Single default and was never broken — left alone) | `src/RimMandrake/FeverWood/Defs/ThingDefs_Plants/RM_GiantLeaf.xml` |
| `Things/Item/Resource/RM_Tekk` | RM_Tekk (had no override at all — added one) | `src/RimMandrake/Wasteland/Defs/ThingDefs_Items/RM_WastelandBrine_Items.xml` |
| `Things/Pawn/Animal/SeaBeasts/{Mee,Faa,Laa}/*_south` | RSW_MeeCatch, RSW_FaaCatch, RSW_LaaCatch | `src/RimStarWars/SWBestiary/Defs/ThingDefs_Items/RSW_ScalefishCatch_Items.xml` (also corrected the file's own header comment, which wrongly asserted FishBase's inherited StackCount "renders one texture fine" — it does not, that was the whole bug) |
| `Things/Filth/RSW_WhaleDung` | RSW_Filth_WhaleDung (had no override at all — added one) | `src/RimStarWars/SWBestiary/Defs/ThingDefs_Misc/RSW_Filth_WhaleDung.xml` |
| `Things/Item/Resource/RSW_OllimWood` | RSW_OllimWood (own def — real deployed art, just missing the override) | `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_ExtremeDesertSignatureFlora.xml` |
| `swresource/AbsorbedEggs/RSW_InsectEgg` | RSW_DuneCrawler | `src/RimStarWars/SWBestiary/Defs/ThingDefs_Items/RSW_SandSwimmer_Items.xml` |
| `swresource/Trophies/BanthaHorn` | RSW_GlassPearl | same file |

All 14 touched files pass `python3 skills/rimworld-modding/scripts/validate_patch.py`
individually at 0 errors (some carry pre-existing `info`/`WARN` noise about vanilla
texPaths not being loose files, which is expected and unrelated — see the skill's own
explanation of why that warning cannot distinguish a correct vanilla path from a typo
without `--defs`/`--live`). No `--defs`/`--live` dump was available in this worktree,
so only static checks ran; nothing here calls for a live-bridge check per the task's
offline-only constraint.

## left unfixed — flagged, not guessed

- **`Things/Item/Resource/Leather/Leather_Plain`** — `RM_ToxinSealant`
  (`src/RimMandrake/Greentide/Defs/ThingDefs/RM_Greentide_Items.xml`, explicit
  `Graphic_StackCount`) and `RSW_TelluroxShell`
  (`src/RimStarWars/SWBestiary/Defs/HelixTellurox/ThingDefs_Races/Races_Tellurox.xml`,
  inherits `LeatherBase`'s StackCount). Unlike every other entry in this census, this
  texPath is a genuine **vanilla** StackCount folder (Odyssey/Core ship real
  `Leather_Plain_a/b/c`-style variants packed in an AssetBundle) — this worktree ships
  no loose override at that path, so it is plausible the folder resolves fine for
  everyone else and something else is going on for these two defs specifically (wrong
  `thingClass`, or the error is from a *different* def not in this census sharing the
  path text). Forcing `Graphic_Single` here would be a guess that could visibly
  flatten a working three-variant stack art down to one texture. Needs either a live
  read of the actual failing def, or someone who can confirm whether vanilla's real
  Leather_Plain folder is present at load time. **Not fixed.**
- **`Buildings/Crystal_Formations/small_dyeable`** (KOTOR_SmallCrystal_red/orange/
  yellow/green/blue/purple/white,
  `src/RimStarWars/Armoury/Defs/Absorbed_KotorWeapons/ThingDefs_Mineables/
  Absorbed_KotorWeapons_KotORResource_CrystalFormations_Small.xml`) — this file is a
  GENERATED verbatim absorption of `guy762.KotORWeapons`, and its own header says not
  to touch it and **not to deploy it** until the donor pack retires (duplicate
  defNames otherwise). The live error is almost certainly coming from the *donor
  mod's own copy*, not this file — out of scope for a texPath/graphicClass fix here,
  and not ours to edit per the generated-file rule. **Not fixed, not ours.**

## owed art — not a texPath/graphicClass bug, no action taken

Confirmed by filesystem: `texPath` names a folder with **neither a file nor a
directory** anywhere under this worktree's `Textures/` roots. Same status as a
zero-tile biome — this is the art pipeline not having produced anything yet, not a
misconfiguration. Do not "fix" by inventing a placeholder texPath; that would just
move the defect.

- `Things/Plant/RSW_DommoTree`, `RSW_SurraGrass`, `RSW_Ultracactus`
- `Things/Plant/VaultRoot` (RM_VaultRoot + RUT_VaultRoot)
- `Things/Plant/RM_Venomvine` (RM_Venomvine + RM_VenomvineThicket)
- `Things/Plant/DosimeterLawn` (RM_DosimeterLawn + RUT_DosimeterLawn)
- `Things/Plant/RM_Leachmoss`
- `Things/Plant/RM_Palefloss/RM_Palefloss`, `RM_Glassfern/RM_Glassfern`,
  `RM_Chimeglobe/RM_Chimeglobe`
- `Things/Plant/RUT_BloomCrop`, `RUT_DarkCrust`, `RUT_Glower`, `RUT_YearningFruit`,
  `RUT_Grellbush`, `RUT_WildHealroot`, `RUT_Grellspine`, `RUT_Fuzz`
- `Things/Item/Resource/RUT_CrackWax`, `RUT_DeltaLoam`, `RUT_GlowerCrust`,
  `RUT_MetalSaltBezoar`
- `Things/Item/Meal/RM_VorrelSeedDish`, `Things/Plant/RM_Vorrel`
- `swresource/RSW_ZakkroEgg`
- ~35 distinct `Things/Filth/Art/RM_Graffiti_*` paths (Tag_A/B/C, ThrowUp_A/B,
  CrossOut, Stencil_Crown/Gear/Fist, Paste_Flyer/Wanted, SigilFrame_Halo, and ~22
  `Glyph_*` ideology-meme tags) in
  `src/RimMandrake/Graffiti/Defs/ThingDefs_Graffiti.xml` and
  `ThingDefs_GraffitiMemeGlyphs.xml` — note `RM_Graffiti_Vandal`/`Scratches`/
  `TallyMarks`/`WarningGlyph` in the *same file* already have real folders
  (`vandal_0..5.png` etc.) and do NOT error; this is a straightforward "some of this
  mod's glyphs have art, most don't yet" state, not a defect.

## criteria

- [x] Real census taken from a genuine full-load log, not guessed or scanned blind
- [x] Every distinct texPath cross-checked against current disk state before touching
      anything (avoided re-fixing already-fixed defs, avoided inventing art)
- [x] 28 confirmed-broken defs fixed with the TerminalBiomes `Graphic_Single` pattern
- [x] Every touched file passes `validate_patch.py` individually at 0 errors
- [ ] Live-bridge confirmation that the fixed defs no longer red-X — explicitly NOT
      done here (offline-only constraint on this pass); next FOUNDRY bridge session
      should grep a fresh full-load log for the same 28 defNames/texPaths
- [ ] `Leather_Plain` (RM_ToxinSealant/RSW_TelluroxShell) — needs a human or a live
      check, not a guess
- [ ] KOTOR crystal donor texture — not ours, needs the absorption item's own
      criteria (kotorcore/guy762.KotORWeapons retirement), not this item's
- [ ] ~50 owed-art texPaths above are real follow-on art-pipeline work, tracked here
      as a list so nobody re-derives the census; not filed as their own items since
      most trace back to already-known "OWED ART, DEPLOY_HOLD" comments in their own
      def files
