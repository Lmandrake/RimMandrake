# STAT_NORM_WAVE3_RETIRE_1

Owner ruled 2026-09-11 (Wave 3, `STAT_NORMALIZATION_AUDIT_1`): retire
`gravenwitch.VSRexamined` + `jellypowered.survivaltools` TOGETHER; counter-patch
`iforgotmysocks.CaravanAdventures`' stat edits to neutral while its quest layer
stays fully live; `frozensnowfox.complexjobs` is a RULED KEEP (work
*assignment*, not work *speed* — recorded in `mod_config_rulings.md`, not
touched here). A same-day scope add (Wave 4 ruling) folded
`tidal.morevanilla.textures`' 15 drawSize replaces into this item's
counter-patch bucket too. The research trio (steppingstones + gravtech x2) is
explicitly NOT this item — `RESEARCH_TRIO_RETIRE_1` owns it.

## spec

1. Retire `gravenwitch.VSRexamined` (Vanilla Skills Rexamined) and
   `jellypowered.survivaltools` (Survival Tools Reborn) together — remove both
   from the live `ModsConfig.xml`, clean the campaign save of any placed
   instances of either mod's own things, and fix any live in-repo reference to
   either mod's defNames.
2. Counter-patch `iforgotmysocks.CaravanAdventures`' armour/bodySize/
   combatPower edits back to neutral, without removing the mod or touching its
   quest defs (QuestScriptDefs, FactionDefs, the Story world objects).
3. Counter-patch `tidal.morevanilla.textures`' drawSize replaces back to
   neutral, keeping its retextures.
4. Do not touch `frozensnowfox.complexjobs` (ruled keep) or the research trio
   (separate item).

## What was found and done

### VSRexamined + Survival Tools Reborn — retired

- **VSRexamined** (`Gravenwitch.VSRexamined`, workshop `3235834179`) adds only
  5 `StatDef`s (mechanitor offset stats) — zero `ThingDef`s, so zero placed
  instances possible. Confirmed absent from the campaign save.
- **Survival Tools Reborn** (`jellypowered.survivaltools`, workshop
  `3554664966`) adds 22 tool `ThingDef`s. A save cross-reference
  (`grep -c '<def>NAME</def>'` per defName, `MEASURE_ALLOW_SCAN=1` override,
  per the `rimworld-savegame` skill) found exactly **4 placed instances** in
  `CANONICAL_ASHKARR_2026-09-09.rws`: `SurvivalTools_Axe` (ground, forbidden,
  133,124), `SurvivalTools_Hammer` (ground, forbidden, 135,125),
  `SurvivalTools_Pickaxe` (ground, forbidden, 145,121), and
  `SurvivalTools_Multitool` (inside an `AncientHermeticCrate`'s loot list).
  Each Thing's only other occurrences in the file were self-contained
  `CompEquippable`/verb `loadID` children of its own block — no external
  pawn-inventory or quest reference anywhere else in the save.
- **Save cleanup**: backed up the live save to
  `CANONICAL_ASHKARR_2026-09-09.rws.bak-pre-wave3-tool-cleanup-2026-09-11`
  (byte-identical size check passed), then deleted the 4 `<thing>`/`<li>`
  blocks by exact line-range match (183 lines total), and removed both
  packageIds from the save's `<meta><modIds>`/`<modSteamIds>`/`<modNames>`
  parallel arrays (index-aligned, 575→573 entries each) so the save doesn't
  carry a stale `<meta>` mismatch the way `lumi.doorsexpanded` did
  (`DOORSEXPANDED_SAVE_COMPAT_REGRESSION_1`). Re-parsed with
  `xml.etree.ElementTree` after each edit — parses clean. Zero remaining
  `<def>SurvivalTools_*</def>` placed instances for any of the 22 defNames.
  Same `<meta>` cleanup applied to `src/Jawa/ideoligion/MandrakeJawa.xtp` and
  `src/Jawa/ideoligion/The Salvation.rid` (both startup-deserialized, same
  three-array shape) — the dated `witness/` snapshot copy was deliberately
  left untouched as a point-in-time record.
- **Live in-repo dependents found and fixed** (a genuine dependency sweep, not
  a guess — grepped `src/` and `design/` for both packageIds and every
  `SurvivalTools_*`/`VSR*` token):
  - `src/RimMandrake/Inhabited/Defs/CastRosters/CastRoster_EMPIRE.xml` gave
    "Fitter Kobbo Vunt" a starting `SurvivalTools_Multitool` — removed the
    dead `<items>` block.
  - `src/RimStarWars/StructureInjectionsSW/Templates/mining_site.txt` placed a
    `SurvivalTools_Pickaxe` prop in its tool-shed room — removed the line, and
    the same line + a stale comment removed from its generator source,
    `design/Jawa/templates/mining_site.lua`, so a future regen doesn't
    reintroduce it.
  - `neolithic_floor_roster.py`'s `EXCLUDE_SUBSTR` already excludes
    `SurvivalTools_` — no change needed there, it was already defensive.
- **Workshop-wide dependency sweep**: neither packageId appears in any
  `modDependencies`/`loadAfter`/`MayRequire`/`PatchOperationFindMod` of any of
  the other ~1,268 installed workshop mods (`grep -rli` across the whole
  workshop content tree, 0 hits outside each mod's own folder).
- **ModsConfig.xml**: backed up to
  `infrastructure/state/modlists/ModsConfig_before_STAT_NORM_WAVE3_RETIRE_1_2026-09-11.xml`
  (584 active at backup time), then both `<li>` entries removed by exact-tag
  match (confirmed 0 occurrences of either string afterward).
  ⚠️ **Concurrent-edit note**: while this item was in flight, another FOUNDRY
  worktree executing `STAT_NORM_WAVE2_RETIRE_1` removed its own 9 mods from
  the same live file (`dizzyeevee.bettercrossbreeding`, `dizzyeevee.rheng`,
  `erin.ffanimals`, `joe.cephaloids`, `spino.megafauna`,
  `tyrannidae.littlecritters`, `vanillaexpanded.vaewaste`,
  `vanillaexpanded.vplantsesucculents`,
  `veterano.mythicages.megafaunabestiary`). Diffed the file before/after this
  item's own edit and confirmed those 9 plus this item's own 2 are the ONLY
  changes — no collision, no lost work. Live count: 584 → 573.

### CaravanAdventures — counter-patched, mod stays live

New file `src/RimUtinni/UtinniPatches/Patches/StatNorm_CaravanAdventures_BossStatsNeutral.xml`.
The mod's only ArmorRating/baseBodySize/combatPower content in its **live 1.6**
folder (its CEPatches folder is Combat-Extended-gated, not in our list; its
`Expansions/RM/UnusedDefs` is dead by its own folder name) is the five
`generateCommonality=0` story bosses in `BossBodyAndRaceDefs/BossRaceDefs.xml`
— they never enter normal point-based raid generation, they exist only for the
mod's own hand-triggered boss fights. Reset to each boss's own vanilla-body
analog (CADevourer/CAEndBossMech use `body=MechanicalCentipede` → vanilla
`Mech_CentipedeBlaster`'s own ArmorRating 0.22/0.72, baseBodySize 3,
combatPower 400; CACrystalScythe/CAHarbinger/CAHavoc use `body=Scyther` →
vanilla `Mech_Scyther`'s own combatPower 150, their armor/bodySize already
matched vanilla). The Sacrileg Hunters faction pawns (combatPower 35-100, in
ordinary human range) and the mech-chip hediff stat *offsets* (an optional
installable augment, ±0.2-0.5) are quest-layer content, not the inflated base
numbers this ruling targets, and were deliberately left alone. Every operation
is `PatchOperationConditional`-wrapped on its own target so the file is a true
no-op if the donor is ever retired later. `validate_patch.py --defs` (Data +
Mods + workshop): **0 errors, 0 warnings**, all 9 targets resolved to exactly
1 live match each.

### More Vanilla Textures — counter-patched, retextures stay

New file `src/RimUtinni/UtinniPatches/Patches/StatNorm_MoreVanillaTextures_DrawSizeNeutral.xml`.
Its only real drawSize overrides in the live 1.6 folder are 6 vanilla-core egg
`ThingDef`s shrunk from vanilla's own 1.3 (ostrich) / 1.2 (emu, cassowary) down
to a flat 1.0 (`Races_Animal_BigBirds.xml`) — reset to their vanilla values.
Its Gazelle female-graphic addition (`Races_Animal_PigGroup.xml`) already uses
vanilla Gazelle's own per-life-stage drawSize (1.3/1.65) — already neutral,
nothing to touch. `validate_patch.py`: 0 errors, 6 advisory warnings (unwrapped
`PatchOperationReplace`, harmless here since every target is a core vanilla
def that always exists regardless of MVT's presence).

### Not touched, as scoped

`frozensnowfox.complexjobs` — untouched (ruled keep). Research trio
(`petetimessix.researchreinvented.steppingstones`, `als.gravtech`,
`als.gravtech.bc`) — untouched, belongs to `RESEARCH_TRIO_RETIRE_1`.

## verify

- `validate_patch.py` on both new patch files: 0 errors (ran above).
- `run_selftests.py`: 46/47 (the 1 failure is the pre-existing, unrelated
  `selftest_tool_metadata.py` companion-DLL-not-built skip, not caused by this
  change).
- Live `ModsConfig.xml`: `gravenwitch.vsrexamined` / `jellypowered.survivaltools`
  absent (`grep -c`, 0).
- Campaign save: 0 placed `<def>SurvivalTools_*</def>` instances for all 22
  defNames; XML re-parses clean; `<meta>` arrays stay index-aligned (573/573/573).

## criteria

VSRexamined + Survival Tools Reborn retired from the live mod list with their
4 placed tools and every live in-repo dependent cleaned up; CaravanAdventures
and More Vanilla Textures counter-patched to neutral with their non-stat
content (quests, retextures) untouched; complexjobs and the research trio
left alone. Cold-load proof is OWED to the next natural full-list load — not a
dedicated restart for this alone, per this audit's own established practice
(`STAT_NORM_WAVE1_RETIRE_1`).
