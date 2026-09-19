## Spec
`design/Jawa/droid_system_build_spec.md` §1: "Flesh type: our own
`DW_FleshType_Droid`, `isOrganic: false` from birth." This does not exist —
grepped the whole `src/Jawa/Droidworks/` tree, zero hits for `FleshType` or
`DW_FleshType_Droid`. `DW_Race_Base` (`Defs/Races_Base.xml`) sets only
`<race><body>Human</body></race>`, inheriting vanilla `Normal` fleshType from
`ParentName="Human"`. The generator's own closing note
(`DROIDWORKS_DEF_GENERATOR_1.md`) already flags this: "organic needs
(Food/Rest/Joy/Beauty/Comfort/...) are not blacklisted on this base... this
was never wired, not silently dropped." This item formalizes that flagged
follow-up with live confirmation.

## Live confirmation (quicktest, 2026-08-30, DW_OuterRim_GNKDroid pilot)
`jawa/list_pawns` / `jawa/pawn_get` on freshly-spawned pilot chassis pawns:
- `fleshType: 'Normal'`, `isFlesh: True` — not droid flesh.
- `hasGenes: True`, random xenotype assigned per spawn (`Starjack`,
  `Neanderthal` across a 6-pawn batch) — a droid should not carry a Biotech
  genome at all.
- Full human backstory/ideo/traits/needs: `Food 0.8`, `Rest 0.93`, `Mood 0.5`
  alongside `DW_Power` — the droid eats, sleeps and has moods like an ordinary
  colonist.

Mechanically this pawn IS a human wearing a droid's kindDef and blank head.
It does not block Phase 0's own mechanics (ion buildup, death, detonation all
fired correctly regardless — see `DROID_SYSTEM_BUILD_1`'s note), but it means
none of the "droid identity" promises in spec §1/§2 (no food need, corpse
does not rot, isOrganic-false EMP/ion eligibility argued in
`DamageWorker_IonBuildup.cs`'s own comment) are actually true yet for any
ported race.

## Verify
1. Author `DW_FleshType_Droid` (`FleshTypeDef`, `isOrganic: false`) and set
   `<race><fleshType>DW_FleshType_Droid</fleshType></race>` on `DW_Race_Base`.
2. Blacklist organic needs (`Food`, `Rest`, `Joy`, `Beauty`, `Comfort` at
   minimum) the way `DroidsAreMachines.xml` already does for the packs it
   retro-patches — read that file's pattern before inventing a new one.
3. Set `hasGenes: false` (or an equivalent xenotype exclusion) so droids stop
   getting a random human xenotype at spawn.
4. Quicktest re-check: spawn a fresh pilot, `jawa/pawn_get`, expect
   `fleshType: DW_FleshType_Droid`, no `Food`/`Rest` need rows, no xenotype.

## Done (2026-08-30, live-verified, 10/10 batch)
- Food and Rest needs removed (`<foodType>None</foodType>`,
  `<needsRest>false</needsRest>` on `DW_Race_Base`). Verified:
  `jawa/pawn_get` on a fresh pilot reads `needs: [Mood, DW_Power]` — no Food,
  no Rest.
- `PawnKindDef.xenotypeSet` (forcing Baseliner) added to all 80 generated
  kinds. Works for the realistic case (player-faction spawns, no meme
  override); does NOT override a hostile faction's own ideo-meme xenotype
  weighting (engine quirk: `PawnGenerator.XenotypesAvailableFor`'s
  `AddOrAdjust` treats a Baseliner entry as a no-op and assigns it only the
  weight left over after faction/meme contributions — there is no PawnKindDef
  field that can force Baseliner outright against a meme). Low-priority,
  cosmetic-only; not pursued further this session.

## NOT done — moved to DROIDWORKS_ISFLESH_RELATIONS_CRASH_1
`DW_FleshType_Droid` (`isOrganic: false`) is authored in
`Defs/Races_Base.xml` but deliberately **not wired** onto `DW_Race_Base`.
Wiring it in triggered a real, reproducible `NullReferenceException` on pawn
generation for any faction with an ideoligion — and confirmed, live, that the
identical crash already exists on the shipped `OuterRim_BattleDroid`
(`isOrganic:false` since `DroidsAreMachines.xml`, 2026-08-11). That is a
bigger, pre-existing engine-interaction bug, not scoped to this item — see
`DROIDWORKS_ISFLESH_RELATIONS_CRASH_1` for the full root cause and fix plan.

## criteria
- [x] Organic needs no longer appear on a droid pawn (live-verified, 10/10).
- [x] No random xenotype/genes assigned at spawn for the realistic
      (player-faction) case — partial for hostile-faction-with-meme case,
      documented above as a known, low-priority engine limitation.
- [x] `validate_patch.py` clean against the live def dump.
- [ ] `DW_FleshType_Droid` exists but is NOT wired on `DW_Race_Base` —
      superseded by `DROIDWORKS_ISFLESH_RELATIONS_CRASH_1`, not closeable
      here.
