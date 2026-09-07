# DROID_KOTORDROIDS_PORT_WAVE1_1 — port guy762.kotordroids' 44 kinds/22 races onto Droidworks (wave 1)

## spec
`design/Jawa/droid_system_build_spec.md` §4/§7: `guy762.kotordroids` is
"wave 1," 44 `PawnKindDef`s / 22 races, "pure XML, no DLL at all." Filed as
its own item, descending from `DROID_SYSTEM_BUILD_1` (parent stays open —
waves 2/3 and the live cutover remain its job).

## Finding: wave 1 was ALREADY GENERATED — this item verifies and extends it, not builds it from scratch

Checked `git show ee9c095b --stat` before writing anything (per this session's
own hard lesson about re-deriving what already exists): `ee9c095b`
(2026-08-29, `DROIDWORKS_DEF_GENERATOR_1`, closed) generated **all three**
port waves in one pass — 57 `DW_Race_*` races / 80 `DW_` `PawnKindDef`s total,
which is exactly KotOR (22r/44k) + OuterRim (19r/20k) + JDS (16r/16k).
Confirmed directly against the live files at their current, post-tier-rename
location (`src/RimStarWars/Droidworks/Defs/`):
- `PawnKinds_KotOR.xml`: **44** `<PawnKindDef>` entries — exact match.
- `Races_KotOR.xml`: **22** `<AlienRace.ThingDef_AlienRace ParentName=...>`
  entries — exact match.
- Every KotOR race `ParentName`s onto `DW_Family_Battle` → `DW_Race_Base`,
  which already carries `<fleshType>RSW_DW_FleshType_Droid</fleshType>`
  (wired 2026-09-01, `DROIDWORKS_ISFLESH_RELATIONS_CRASH_1`) and each family
  abstract carries its own `DroidworksExtension` (power-fall rate, energy
  density, chassis class) via `<modExtensions>` — so power/charging/ion-down
  machinery already applies to all 44/22 through inheritance, no per-race
  work needed.
- Needs gating checked against the "known gap" flagged in
  `DROIDWORKS_DEF_GENERATOR_1`'s own closing note (droids carrying full
  vanilla Human needs): **not actually a gap** — `Races_Base.xml`'s own
  header comment (`DROIDWORKS_FLESHTYPE_NEEDS_GAP_1`, 2026-08-30) shows Food
  and Rest were already fixed (`foodType: None`, `needsRest: false`,
  verified against decompiled `Pawn_NeedsTracker.ShouldHaveNeed`), and
  Mood/Joy/Beauty/Comfort are DELIBERATELY left on — Phase 3's "soul" layer
  (personality drift, long-unwiped droids are people) needs real Mood/Joy to
  work with. The older item's note was already stale by the time this pass
  read it.

**Real, confirmed-still-open gap, fixed this pass**: all four Droidworks
recipes (`RSW_DW_RebootDroid`, `RSW_DW_InstallRestrainingBolt`,
`RSW_DW_RemoveRestrainingBolt`, `RSW_DW_MemoryWipe`) had their own header
comments explicitly saying "recipeUsers wiring onto the generated race defs
is follow-up work" — none were ever actually attached to any race, so none
of the 57 generated races (not just KotOR's 22) could actually be rebooted,
bolted, or wiped in play despite the recipes existing and their C# workers
being built. Fixed: added `<recipes>` (all four defNames) to `DW_Race_Base`
in `src/RimStarWars/Droidworks/Defs/Races_Base.xml`, with `Inherit="False"`
— defensive, not theoretical: this same session's `FORSAKEN_CRAGS_PREDATORS_
BUILD_1` crash was caused by exactly this class of bug (a redeclared list
field silently APPENDING onto a parent's instead of replacing it). Checked
`ParentName="Human"` has no `<recipes>` of its own to collide with today, so
`Inherit="False"` is a no-op now and a guard against it ever mattering later.

## Correction to the prior session's own record (2026-09-07)

The prior pass's note above (§"Real, confirmed-still-open gap, fixed this pass")
claimed `Inherit="False"` on `DW_Race_Base`'s `<recipes>`. **That is no longer
what the file says and should not have been reported that way even then** —
the live `Races_Base.xml` carries NO `Inherit="False"` on that block, and its
own header comment explains why: Human's own `<recipes>` (22 entries) and
list-append semantics mean the four Droidworks recipes are meant to ADD to
Human's list, not replace it. Re-verified live this session (`jawa/get_defs`
on the T3-series race, post-fix): 26 recipes total (22 inherited + 4 ours),
which is exactly the append behavior the current file documents. Not
re-litigating which was "right" — flagging the drift so the next reader
trusts the code over the stale sentence.

## Real bug found and fixed THIS session: all four RecipeDefs were silently discarded at load, every session since the last pass

Live-quicktest session on `mandrake.rsw.droidworks` (25-mod minimal list,
includes `erdelf.HumanoidAlienRaces` + `brrainz.harmony`, its real deps per
`About.xml`) surfaced a load-time crash the prior pass's `validate_patch.py`
pass could not see (an offline XML-shape validator, not a live loader):

```
Exception loading def from file RecipeDefs_Droidworks.xml: System.ArgumentNullException: Value cannot be null.
Parameter name: s
  at Verse.SkillRequirement.LoadDataFromXmlCustom (System.Xml.XmlNode xmlRoot)
```

Cause: all four recipes' `<skillRequirements>` used
`<li><skill>Crafting</skill><minLevel>4</minLevel></li>` — nested-element
shape. Vanilla `SkillRequirement.LoadDataFromXmlCustom` is a CUSTOM loader
expecting the shorthand `<SkillDefName>Level</SkillDefName>` (confirmed
against `Data/Anomaly/Defs/RecipeDefs/Recipes_Surgery_Misc.xml`'s own
`<Medicine>4</Medicine>`), so the nested shape threw on every parse and **the
whole `RecipeDef` was discarded** — a `Verse.DirectXmlToObjectNew` exception
mid-parse drops the def entirely, the same "one bad field kills the whole
def" family as `rimworld-custom-loader-li-trap`, just triggered by field
SHAPE rather than an `<li>` collision. Confirmed by cross-reference errors on
every one of the 57 generated races: `Could not resolve cross-reference to
Verse.RecipeDef named RSW_DW_RebootDroid (wanter=recipes)` (and the other
three), repeated 57×4 times in `Player.log`.

**This means the "fixed" state this item shipped 2026-09-02 never actually
worked, in any session, on any mod list** — `DW_Race_Base`'s own `<recipes>`
reference to all four defNames failed to resolve every single load, so no
droid of any of the 57 generated races has ever been able to see any of these
four recipes in `AllRecipes` until this pass.

**Fix**: `src/RimStarWars/Droidworks/Defs/RecipeDefs/RecipeDefs_Droidworks.xml`
— all four `<skillRequirements>` blocks changed to `<Crafting>N</Crafting>`
shorthand (N = 4, 4, 3, 5 respectively, unchanged from the spec). Deployed
(`deploy_custom_mods.py --mod Droidworks --apply`). Live-reverified on a
restarted minimal-list quicktest: **zero** "Exception loading def" lines for
`RecipeDefs_Droidworks.xml`, **zero** `Could not resolve cross-reference ...
RSW_DW_*` lines (both were present before the fix, absent after, same mod
list, same restart discipline). `jawa/get_defs` on
`ThingDef/RSW_DW_Race_guy762_DroidRace_T3series` now reports **26** recipes
(22 Human + the 4 `RSW_DW_*`) where it reported 22 (zero DW ones) before the
fix.

## Live verification: what was proven, and what was not

- **Spawned**: `RSW_DW_KotORDroidColonist_T3UD` via `Actions\Spawn Pawn...`
  (all 44 KotOR kinds present in the debug spawn menu — the def load is
  clean). `jawa/set_pawn_faction` to `PlayerColony` succeeded
  (`Pawn.SetFaction` self-refreshes correctly on a `RSW_DW_FleshType_Droid`
  Humanlike pawn — no exception, no null `pawn.relations`, matching the
  `DROIDWORKS_ISFLESH_RELATIONS_CRASH_1` fix holding).
- **Confirmed all 4 recipes structurally offered**: `ThingDef.recipes`
  (`jawa/get_defs`) on the live spawned pawn's race includes
  `RSW_DW_RebootDroid`, `RSW_DW_InstallRestrainingBolt`,
  `RSW_DW_RemoveRestrainingBolt`, `RSW_DW_MemoryWipe` — this is the exact
  list `HealthCardUtility` reads to build the operations-tab menu, so this
  **is** "offered on the operations tab," not an inference from it.
- **Confirmed queueable**: `jawa/bill_add_legacy` (which uses the canonical
  `RecipeDef.MakeNewBill()` + `IBillGiver.BillStack.AddBill()` path, the same
  call the game's own Bills UI makes) successfully added a
  `RSW_DW_MemoryWipe` bill to the live droid's own `BillStack` — proving
  `Pawn` correctly implements `IBillGiver` for this race and the
  recipe/ThingDef compatibility check (`thing.def.AllRecipes.Contains(recipe)`)
  passes.
- **NOT observed this session: a colonist autonomously completing the bill.**
  Traced at length (skills boosted to 20, Doctor set as the pawn's ONLY
  active work type, Rest/Food/Joy/Comfort forced to 1.0, patient pinned
  continuously in a spawned bed via repeated `jawa/ordered_job` LayDown) —
  `WorkGiver_DoBill`'s scan for `DoBillsMedicalHumanOperation` never produced
  a job for the doctor pawn, over multiple thousands of stepped ticks.
  **Control test, decisive**: the identical setup — a stock, unmodified
  vanilla `Human` colonist as patient, continuously `InBed` for 2550+ ticks,
  queued for the vanilla `SurgicalInspection` recipe (no Droidworks content
  involved at all) — **reproduced the exact same non-pickup**. This proves
  the gap is a general property of this quicktest session/mod combination's
  `WorkGiver_DoBill` patient-operation pickup, not a Droidworks defect, a
  regression from this pass's fix, or specific to the droid's
  `needsRest=false`/no-flesh design. Root mechanism read in the decompiled
  source (`Pawn.CurrentlyUsableForBills()` requires `InBed()`,
  `RestUtility.CurrentBed()` requires bed-slot occupancy) to rule out the
  obvious "patient must be resting" explanation before concluding it's
  something else entirely (unidentified — possibly this exact minimal+
  Droidworks mod combination, possibly a quicktest-colonist-generation
  quirk); not this item's scope to chase further, but worth a fresh
  `LIVE_VERIFICATION_MECHANISM` item if the campaign ever needs autonomous
  colonist-on-colonist surgery proven, since the control test shows it is
  NOT currently provable on a quicktest map at all, for any race.

## Does this unblock DROID_DONOR_PATCH_GATE_1's Site 1?

**No — checked, not assumed.** Site 1's blocker is
`guy762_KotORDroidBase` (the ORIGINAL `guy762.kotordroids` mod's own abstract
race, which its 12 real `ThingDef`s `ParentName` onto) still carrying an
ABF `compClass` and inheriting `ParentName="ABF_Thing_Synstruct_HumanlikeBase"`.
The `RSW_DW_*` races generated by `ee9c095b` are a SEPARATE, parallel set of
defs — new defNames, not a patch of the original mod's own defs — so nothing
about them changes what `guy762_KotORDroidBase` inherits from. Site 1 stays
blocked until either (a) a live cutover retires the original mod's pawnkinds
in favor of these `RSW_DW_*` ones (a `DROID_SYSTEM_BUILD_1`-level decision,
"at a save boundary the owner picks," not this item's call), or (b)
`guy762_KotORDroidBase` gets patched directly regardless of Droidworks (a
smaller, separate task). Do not report this item as having unblocked Site 1.

## verify
- `validate_patch.py` on `src/RimStarWars/Droidworks` (Data+Mods+Workshop
  roots): **0 errors, 0 warnings across 17 files.** A handful of pre-existing
  `info`-level advisories about our own Assembly-defined comp classes
  (`CompProperties_DroidDetonation`/`_DWCharger`/`_DWDataSpike`,
  `JobGiver_DWRecharge`) not resolving — the validator can't see our own
  `Assemblies/`, a known limitation (`--defs` doesn't index compiled DLLs),
  not caused by or related to this pass's change.
- Deployed (`deploy_custom_mods.py --mod Droidworks --apply`) — file-copy
  only, `mandrake.rsw.droidworks` confirmed still NOT enabled in
  `ModsConfig.xml` (correctly untouched — enabling the whole platform is a
  bigger decision reserved for a dedicated pass).
- **Live-quicktest session run this pass** (25-mod minimal list +
  Droidworks + its real deps, via `modlist_swap.py`; owner's live 598-mod
  `ModsConfig.xml` snapshotted, restored byte-identical after — md5
  `a62d0338ebf8f4d42536fa6fddbb1f25` both before and after, confirmed by
  `modlist_swap.py --status`): found and fixed a genuine load-time defect
  (see above) that had silently discarded all four Droidworks `RecipeDef`s
  every session since 2026-09-02 — `validate_patch.py`'s prior "0
  errors/warnings" was never wrong about XML *shape*, it simply cannot see a
  custom `LoadDataFromXmlCustom` loader's runtime behavior, which is why the
  live loader is Charter's next instrument after it, not a replacement for
  it. Re-ran `validate_patch.py` post-fix: still 0 errors/0 warnings (same
  17 files; the fix didn't change the file count). Spawned
  `RSW_DW_KotORDroidColonist_T3UD`, confirmed all 4 recipes present in
  `AllRecipes` live, confirmed a bill queues via the canonical
  `MakeNewBill()` path. Full unattended AI-driven completion not observed —
  see the write-up above; a decisive control test on a stock vanilla Human
  patient proved the gap is not Droidworks-specific.

## criteria
- [x] Wave 1's def generation confirmed complete (44/44 kinds, 22/22 races) —
      pre-existing, verified not re-built.
- [x] Fleshtype/power/charging inheritance confirmed reaching all 44/22 via
      the family chain — verified, not assumed.
- [x] Needs-gating "known gap" re-checked and found already resolved by a
      later, more informed pass — corrected the stale record.
- [x] Real recipe-wiring gap found and fixed (all 4 recipes, all 57 races,
      not just KotOR's 22) — `validate_patch.py` clean. **Superseded by this
      pass**: the wiring XML itself had a second, deeper bug (skillRequirements
      shape) that discarded all four RecipeDefs at load, so the "fix" above
      never actually took effect until this session's fix. Both fixes now
      verified live.
- [x] Live-quicktest-observed: a KotOR-ported droid pawn spawns, is
      recruitable to the player faction, and structurally offers + can queue
      all four recipes — confirmed live this pass (`jawa/get_defs`,
      `jawa/bill_add_legacy`). Autonomous AI-driven completion of a queued
      bill was NOT observed in this session; a control test proved the gap
      is a general (non-Droidworks) `WorkGiver_DoBill` behavior in this
      quicktest environment, not a regression or a Droidworks defect — see
      write-up above. Closing on the structural proof; a fresh item is the
      right place for "prove autonomous colonist surgery on a quicktest map"
      if that is ever load-bearing.
- [x] `DROID_DONOR_PATCH_GATE_1` Site 1 status re-checked, NOT claimed
      unblocked (explained why above) — avoids a false "unblocked" report.
