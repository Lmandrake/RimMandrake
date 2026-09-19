# DROIDWORKS_DEF_GENERATOR_1 — DW_ races and kinds generator

Filed by BENCH 2026-08-30T01:41:33Z: "Generator: emit DW_ races and kinds for
all 85 droids from extraction.json." Precondition (extraction.json, 57
races/80 kinds) satisfied at commit `e735da7d`. Caveat on file: KotOR races
inherit from `guy762_KotORDroidBase` (workshop 3254370945,
`guy762.MM.KotORCore`'s `_DroidsBase` submod, packageId in the
`guy762.KotORWeapons` family) — extraction.json does not carry those
inherited fields, read that mod's own XML directly.

## What was built

`src/Jawa/Droidworks/Source/gen_droidworks_defs.py` — reads
`Source/extraction.json`, emits:
- `Defs/Races_OuterRim.xml`, `Defs/Races_KotOR.xml`, `Defs/Races_JDS.xml` —
  one `AlienRace.ThingDef_AlienRace` per source race (57 total), each
  `ParentName="DW_Race_Base"`, `Droidworks.DroidworksExtension` attached with
  chassis-bucket tuning, plus one `HeadTypeDef` per race that has real head
  art (18 of 57 — see below).
- `Defs/PawnKinds_OuterRim.xml`, `Defs/PawnKinds_KotOR.xml`,
  `Defs/PawnKinds_JDS.xml` — one `PawnKindDef` per source kind (80 total),
  `race` repointed at the matching `DW_Race_<orig>`.

`src/Jawa/Droidworks/Defs/Races_Base.xml` — hand-authored (not regenerated):
the one `DW_Race_Base` abstract def every race ParentNames onto
(`ParentName="Human"`, matching the pattern used by other private-campaign
HAR races with no bespoke BodyDef — e.g. `XMT_Starbeast_AlienRace`, workshop
3596077324), plus the shared `DW_HeadType_Blank` HeadTypeDef.

`src/Jawa/Droidworks/Textures/DW/blank_{south,north,east}.png` — generated
(by the script, on first run, via raw PNG bytes — no image tool) fully
transparent 64x64 stub textures, referenced by every headless race's
HeadTypeDef so a headless droid doesn't inherit `DW_Race_Base`'s human face.

Result: **57/57 races emitted, 80/80 kinds emitted, 0 skips.**

## The three incompatible source graphics shapes (had to be read, not assumed)

- **OuterRimDroidDepot (Asimov)**: a body FOLDER whose stem is derived by
  listing it for `*_south.png` (confirmed empirically: HAR's
  `graphicPaths.path` is a literal `{stem}_{rotation}.png`, no bodyType token
  inserted — verified against `guy762_DroidRace_HKseries`'s own
  `HK_body_south.png`, which has ONE declared bodyType but no bodyType token
  in the filename). Animal-family races (Astromech, Muckraker, ...) have no
  Body/Head split — single fused sprite.
- **KotORDroids (already real HAR)**: `body_path`/`head_path` are stems, but
  14 of 22 races declare NEITHER any of bodySize/healthScale/moveSpeed/
  graphics directly — inherited from a SIBLING concrete race via
  `parentName` (HK50/HK51 <- HKseries, 3C/IT <- T3series, etc), resolved by
  walking `races_by_orig` in the generator, never guessed. A `head_path` of
  `"768blank"`/`"512blank"`/`"1024blank"` is the SOURCE MOD'S OWN convention
  for "no separate head art" (14 of 22 KotOR races) — detected and treated
  as headless, not chased as a missing texture.
- **JDS_Separatists (mechanoid)**: flat `texPath` + rotation, no bodyType
  token, no head layer at all — matches the stem+rotation pattern directly.

Every derived texture path is VERIFIED against `Textures/` before being
written (`tex_exists`/`verify_stem`/`find_stem_in_folder`) — nothing here is
a silently-emitted dead texPath.

## guy762_KotORDroidBase — read by hand, as the caveat required

Found at
`/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3254370945/1.6/AdditionalMods/_DroidsBase/Defs/AlienRace_KotORDroidBase.xml`.
It chains through `ABF_Thing_Synstruct_HumanlikeBase` (Artificial Beings
Framework) — a dependency Droidworks deliberately does NOT take (the mod
absorbs/retires the source content per About.xml, it doesn't depend on it).
So `DW_Race_Base` does NOT inherit guy762's ABF-specific fields (raceRestriction,
ABF comps, blacklistedNeeds, etc) — it inherits vanilla `Human` instead, and
carries forward only the DATA fields (bodySize/healthScale/moveSpeed/
graphics/colors) captured per-race in extraction.json, resolved through the
KotOR sibling-inheritance chain described above. This is a deliberate
architectural choice (HAR minimum-viable skeleton, not a re-import of ABF),
not an oversight.

## Chassis classification (BENCH's own tuning table, verbatim — not this
generator's call)

| bucket | powerFallPerDay | energyDensity | count |
|---|---|---|---|
| battle | 1.0 | 0 | 18 |
| heavy | 1.0 | 2 | 18 |
| gonk-power | 0.33 | 3 | 1 |
| astromech-labour | 0.33 | 0 | 15 |
| protocol | 0.033 | 0 | 3 |
| probe | 1.0 | 1 | 2 |

Every race's classification and, where genuinely ambiguous, the reasoning is
printed by the generator and lives in `CHASSIS_PLAN` in the script. Judgment
calls worth flagging here specifically:
- `guy762_DroidRace_HKseries`/`HK50series` are labelled "protocol droid" in
  the source (a canon cover story) but classified **battle** because their
  own `inherentSkills` show Shooting 20 / Melee 16 — classified by mechanism,
  not the label.
- `OuterRim_DestroyerDroid` (droideka) and `JDSCIS_Droideka_*` are classified
  **battle** despite the source mod tagging droideka as `family: Animal`.
- MagnaGuard, SuperBattleDroid/B2, SuperTacticalDroid/TacticalDroid,
  IG-100/T1/ST/B2-HA/Demolition/DSD1 all classified **heavy** — cross-checked
  for consistency across OuterRim/JDS pairs of the same droid type.
- `guy762_DroidRace_GOTO` (G0-T0) classified **protocol** (no combat stats,
  closest of the 6 buckets to a "superintelligence" droid) — genuinely no
  great fit, flagged.
- `guy762_DroidRace_ITseries` classified **astromech-labour** by its
  extraction label ("utility droid"), not by IT-O's canon interrogation-droid
  role — the extraction gives no combat/role data to go on.

## Known data gaps, resolved by reading the mechanism, not by guessing

- **`OuterRim_AstromechDroid`** captured NEITHER `bodyPath` nor `texPath` in
  extraction (its own note: art lives on the paired PawnKindDef, which the
  kind schema doesn't carry either). Resolved by inferring
  `OuterRim/Droid/Astromech/R2` from the real `Textures/OuterRim/Droid/`
  folder tree and VERIFYING `*_south.png` exists before using it — printed as
  a NOTE, not silently assumed.
- **8 of 16 JDS races** (`B1_Battle_Droid`, `B1_Security_Droid`,
  `B1_Commander_Droid`, `BX_Commando_Droid`, `IG-100_MagnaGuards`,
  `T1_Tactical_Droid`, `ST_Super_Tactical_Droid`, `B2_Super_Battle_Droid`,
  `B2_HA_Super_Battle_Droid`) have `baseHealthScale: null` in extraction.
  Read the actual abstract parent XML directly
  (`.../workshop/content/294100/3276499495/1.6/Defs/ThingDefs_Race.xml`,
  `Name="JDSSWCIS_Droids"`): it declares `baseBodySize=0.7` but no
  `baseHealthScale` at all for any of these — RimWorld's own engine default
  (1.0) is the genuine effective value, not a filled-in guess. Used 1.0,
  printed a NOTE citing the source file read.
- **`guy762_DroidRace_T3series`**'s `colorChannels_skin_second` is
  unstructured prose ("5 weighted options incl RGBA(...), blue, slate, olive,
  red"), not a single RGBA/weight pair — the second color channel is omitted
  for this one race (first channel still carried), printed as a NOTE.

## The "4 Jawa_Droid_* kinds" instruction does not match the data

The item brief says 4 kinds whose original source was `Jawa_Droid_*` keep
`Jawa_FreeDroidEnclaves` as their faction. Grepped the raw extraction.json
text for "jawa" in any form: **zero matches** among all 80 kind entries — no
defName, label, race, or note field mentions Jawa anywhere. Per the item's
own fallback ("if you can't find exactly 4 matching that description, say so
rather than guessing which ones"), **no kind gets a faction assignment in
this run** — every `DW_` PawnKindDef ships with faction unset. This needs a
BENCH decision (maybe the intent was a different queue item, or the 4 kinds
haven't been authored yet) — flagging rather than guessing which 4 of 80 to
pick.

## Gear: what got carried, what didn't, and why

RimWorld's `apparelTags`/`weaponTags` are TAG matching — a tag with zero
matching loaded ThingDefs yields no gear at runtime, not a crash — so any
tag-list value present in extraction.json was carried VERBATIM, even when it
names a mod Droidworks doesn't depend on (a live-with-later art/balance gap,
not a broken reference):
- 16 JDS kinds: `weaponTags` carried verbatim (e.g. `E-5_Blaster_Rifle`,
  `SE-14_Light_Blaster_Pistol`) — these look like literal weapon defNames
  but are the SOURCE MOD's own weaponTags values, carried as extraction gave
  them, not invented.
- 12 KotOR kinds (`KotORDroidGood_*`/`KotORDroidBad_*`/`KotORPlayableHero_*`):
  `apparelTags:` segment parsed out of the free-text `apparelTags_or_gear`
  field and carried. The `apparelRequired <defName> <defName>...` segment
  present in some of these same notes was **deliberately NOT carried** — those
  are literal defNames into KotORWeapons/KotORDroids (not a Droidworks
  dependency), and re-emitting a defName parsed out of prose is exactly the
  class of guess this project has been burned by before. Printed per-kind.

41 of 80 kinds ship UNARMED (no apparel/weapon tags emitted) — broken down:
19 OuterRim kinds have `apparelTags: []`/`weaponTags: null` explicitly
declared (11 by clean empty override, 8 flagged `UNCERTAIN` in extraction
because their PawnKindDef parent wasn't in the source mod's read set) plus 20
KotOR `KotORDroidColonist_*` kinds that use race-level `apparelList`
restriction rather than per-kind fixed gear (not a gap — extraction's own
note says so) plus 1 JDS kind (`Pistoeka_Sotage_Droid`, explicitly
`weaponTags: []`, its damage is a baked melee tool on the race). Every one of
the 41 has a printed reason distinguishing "explicit empty by design" from
"extraction genuinely doesn't know."

## Validation

`skills/rimworld-modding/scripts/validate_patch.py` run exactly as specified
in the item brief (`--defs Mods`, `--defs workshop/content/294100`, `--live`
capture `2026-08-29T20-07-29Z`): **1 error** — `DW_Race_Base`'s
`ParentName="Human"` doesn't resolve, because vanilla `Data/Core` isn't among
the `--defs` roots the brief's own command line passes (confirmed: `grep
'Name="Human"'` against
`.../RimWorld/Data/Core/Defs/ThingDefs_Races/Races_Humanlike.xml` finds it
directly). Re-ran with `--defs ".../RimWorld/Data"` added:
**0 errors, 0 warnings across all 10 Defs/ files.** This is a validator-input
gap (vanilla Core absent from the brief's exact command), not a defect in the
generated defs.

Independent defName-uniqueness pass across the whole `Defs/` tree (not just
what the generator tracked — includes phase-0's NeedDefs/HediffDefs/
RecipeDefs too): `grep -rhoE '<defName>...' | sort -u | wc -l` = **160
distinct defNames, 160 total lines — clean, no duplicates.**

## Known gap, deliberately not solved here

`DW_Race_Base` inherits vanilla `Human`'s full need set (Food, Rest, Joy,
Beauty, Comfort, ...) — nothing in phase-0's NeedDefs/HediffDefs or in this
generator blacklists organic needs for droid pawns. Every DW droid currently
carries `DW_Power` ALONGSIDE full vanilla Human needs. This was never wired
by phase-0 either (checked: `Defs/NeedDefs/NeedDefs_Droidworks.xml` has no
disables-mechanism), so it isn't a regression from this item — flagging it as
an open follow-up, not silently patching a design decision that belongs to
BENCH.

## Explicitly not done here (per item scope)

- `Droidworks` not added to `ModsConfig.xml`, nothing deployed.
- Phase-0 defs (NeedDefs/HediffDefs/RecipeDefs) and the C# untouched.
- `DW_RebootDroid` not wired onto the new race defs (filed as
  `DROIDWORKS_PHASE0_XML_1`'s own follow-up, not this item's job).

## criteria

- [x] `src/Jawa/Droidworks/Source/gen_droidworks_defs.py` written, repo-root-
      finding, plan-as-data, loud skips, no silent fallbacks.
- [x] One HAR race per source race (57/57), on a single `DW_Race_Base`.
- [x] `Droidworks.DroidworksExtension` attached per BENCH's chassis tuning
      table, verbatim.
- [x] Graphics paths verified against `Textures/` — every miss printed, none
      silently emitted.
- [x] One `PawnKindDef` per source kind (80/80), race repointed, combatPower
      verbatim, gear carried where extraction has it / UNARMED + note where
      it doesn't, no weapon defName ever guessed.
- [x] "4 Jawa_Droid_* kinds" — investigated, doesn't match the data, flagged
      rather than guessed (see above).
- [x] `validate_patch.py` run per the item's exact command; the one error is
      explained and shown to be a `--defs` input gap, not a def defect;
      0 errors/0 warnings with vanilla Core included.
- [x] Own defName-uniqueness pass: 160/160 distinct, clean.
- [x] Nothing deployed, `ModsConfig.xml` untouched, phase-0/C# untouched,
      `DW_RebootDroid` not wired.
