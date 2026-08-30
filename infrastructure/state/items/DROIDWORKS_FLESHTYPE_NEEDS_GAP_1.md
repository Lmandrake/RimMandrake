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

## criteria
- [ ] `DW_FleshType_Droid` exists, `isOrganic: false`, wired on `DW_Race_Base`.
- [ ] Organic needs no longer appear on a droid pawn (live-verified).
- [ ] No random xenotype/genes assigned at spawn (live-verified).
- [ ] `validate_patch.py` clean against the live def dump.
