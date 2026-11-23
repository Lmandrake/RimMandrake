# History: old counts, corrected lines and their evidence

The active files hold the lessons. This file holds the old counts, the old lines that were wrong, and what showed it
(2026-11-23). Each engine fact was read in the decompiled 1.6 source through RimSage. No live game was driven.

## The old counts of `SKILL.md`

- **The 2026-08-14 dump** had 585 mods and 136 memes. Impact: 35 at 0, 27 at 1, 50 at 2, 24 at 3. 20 of 136 memes
  guaranteed a refusal. 54 precepts carried `classic`, 33 had `visible: false`, 52 had `enabledForNPCFactions: false`.
  The `IdeoPresetDef` field set was verified against that dump (46 defs, 2026-08-14). The `TreeCutting_Prohibited` and
  `Mining_Prohibited` fields, and the `classic` and `visible` counts, were measured 2026-08-14.
- **The 2026-11-23 dump** has 314 mods, 139 memes (36 structure) and 46 presets. Four normal memes have impact 4:
  `AM_NonViolence`, `AM_DeepDevotion`, `AM_PainIsDivine`, `AM_NakedTruth`. 50 precepts carry `classic`, 31 have
  `visible: false`, 36 have `enabledForNPCFactions: false`. 20 of 139 memes guarantee a refusal.
- **Validator codes.** `SKILL.md` said 28 finding codes, 15 of them ERROR-capable. A count of the `r.add` calls gives 33
  and 17, as `validation.md` §3 says.
- **The `<def>` scrape.** CHECK, a retired seat, hit the trap of §4b on 2026-08-15 (71 false missing precepts).
- **Empty def types.** In the 2026-08-15 dump, 79 of the 529 def-type files were empty, `AbilityDef` among them. So all 16
  ideo-role ability references came back `UNMEASURABLE`. The cause was a file-name collision in the dump tool, fixed
  2026-08-21. A run on `The Salvation.rid` on 2026-11-23 had no `UNMEASURABLE` reference.
- **`The Salvation.rid`** carried 585 mod ids, of which 11 no longer loaded. The repo copy carries 572 today. The run of
  2026-11-23 resolved 227/251 references; 24 dangle, because several donor mods left the mod list.
- **The collisions in our specs.** On 2026-08-14 the specs held `Loyalist` + `Supremacist` and `Transhumanist` +
  `VME_Fleshcrafters`. On 2026-11-23 `validate_ideoligion.py` reads 11/11 VALID for the spec and for the shipped XML.

## Lines that were wrong

- **"None of these produce a red error."** `DirectXmlCrossRefLoader.TryResolveDef` calls `Log.Error` for a name that does
  not resolve. A list entry whose `MayRequire` mod is off is tried in silence.
- **"Two memes sharing a tag cannot coexist", "one is dropped".** `IdeoUtility.GenerateRandomMemes` adds `requiredMemes`
  and `forcedMemes` with no exclusion check. Only `CanAdd` (the random draw) and `Dialog_ChooseMemes` test the tags.
- **"A deityPreset on a `deityCount 0` structure" is a silent failure; "only if structure deityCount > 0".** The XML comment
  had those words (`deityCount > 0`). `IdeoGenerator.MakeFixedIdeo` sets the deities after the generator ran, and
  `IdeoFoundation_Deity.DoInfo` draws every deity in the list. But only `MakeFixedIdeo` reads `deityPresets`.
- **"`enabledForNPCFactions: false` silently excludes 52 precepts from any faction religion", every `Violence_*` and every
  `Nomadism_*`; `Mining_Prohibited` "is impossible outright".** `CanAdd` and `CanAddForFaction` do not read the field.
  `PreceptComp_UnwillingToDo`, `PreceptComp_KnowsMemoryThought`, `ThoughtWorker_Precept` and `FoodUtility` do.
  `Nomadism_Horrible` and `Nomadism_Disapproved` do not have the field.
- **"An NPC faction will effectively never generate" `TreeCutting_Prohibited`.** `AddPreceptsOfImpact` draws by
  `selectionWeight` (1), not by `defaultSelectionWeight`, from the precepts whose `associatedMemes` hold the meme. With
  `NaturePrimacy` that is one of nine High precepts, and a religion draws 0 to 2 of them.
- **"`requiredPreceptsOnly` means take *only* those", "needs `fixedIdeo`".** `RandomizePrecepts` also runs
  `AddSpecialPrecepts` and `InitPrecepts`. `FactionGenerator` passes the field with and without `fixedIdeo`.
- **"The enforced ceiling is a COUNT".** Only `Dialog_ChooseMemes` enforces it. `forcedMemes` is added whole.
- **"Nothing else in this project has that property"** (the ideo bakes at world creation). Root `CLAUDE.md` says the same of
  a faction and a setting.
- **The `.rid` loader drops precepts "quietly".** `Ideo.ExposeData` logs one red line for the set. A ritual precept whose
  `behavior` is null is dropped too. The NRE comes from a null `sourcePattern` (`Precept_Ritual.ExposeData`) or a null outcome def
  (`RitualOutcomeEffectWorker.ExposeData`). No such path was found for a null behavior def. `Class` was not checked.
- **`validate_ideoligion.py <spec-or-faction-xml>`.** The script refuses a bare path: `--spec`, `--md` or `--xml` is needed.
- **"A clean-looking exit that has checked nothing."** On a `.rid` the script prints `no religions found in the input` and
  exits 1. It reads no `IdeoPresetDef`, though the old line named one.
- **"246/251 files".** The tool counts references, not files.
- **"I had this backwards"** (impact is a rating, not a budget) was narration of the first author.
