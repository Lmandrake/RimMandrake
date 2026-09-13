# SCALD_MECHANICS_1 — the Scald C# kit

## spec — the C# kit

Per `design/Jawa/worldbuilding/biomes/the_scald.md` (FROZEN,
`BIOME_FREEZE_FABLE_REVIEW_1`): steam-catch industry · margin fishing + bath
recreation · bubble-sailor and bottom-walker set-pieces · geyser fields ·
boiling-lift integration (R-B spec ruled, terrains shipped) · burning-shallows
wreck salvage.

**The engine mapping is drafted**:
`design/Jawa/worldbuilding/biomes/kits/scald_kit_spec.md` (2026-09-11) — 6
mechanics (S1 boil layer/steam sky, S2 steam-catch, S3 margin fishing + baths,
S4 geyser fields, S5 sail/walker set-pieces, S6 wreck salvage), heavy reuse
(ruled `RM_GameCondition_EnvironmentalWeather`, the miasma kit's
scatterer/anchor generics, vanilla 1.6 fishing/swimming/geysers), only 3 new
classes, hard-ban compliance table for the sheet's six 🔴 bans, build order,
and 2 open owner cards (the third — Scald salinity/fishing bucket — is
already open at `design/RimMandrake/RM_liquid_types_mod.md` §9 CARD-1 and is
consumed, not duplicated).

Governing rules from the sheet: the Scald is **never potable** (only its
distilled breath); **no boiling-immune traversal for free** (the shipped
burn values stand); **no macro-life in the boil itself** (walkers surface as
a set-piece, sails ride the carve-out); **no drained, cooled, or tamed
Scald**.

## verify

- [x] The 2 owner cards in the kit spec are ruled — **2026-09-13 (FOUNDRY)**:
      `scald_kit_spec.md`'s own §"Owner cards" shows both RULED 2026-09-12
      (card 2: item water default + dbh_water toggle behind Mod Settings;
      card 3: diving interaction ships as v1 content, filed
      `SCALD_DIVING_MOD_1`) — header fixed, was stale "Open owner cards"
      with no ruled/unruled marker. `RM_liquid_types_mod.md` §9 CARD-1
      (Scald salinity → FRESHWATER, rivers flow OUT) is also ruled, and
      `LIQUID_TYPES_MOD_1` (the mod itself) shipped its full roster
      tonight — `RUT_TheScald.fishTypes` wiring is now unblocked on both
      fronts.
- [ ] Every ❓ engine claim in the kit spec is re-checked against the live
      1.6 assembly before its C# is spent (in particular: the thirst-mod
      `dbh_water` drink route on burn terrain, geothermal's geyser
      PlaceWorker name, post-hoc TileMutator application on fixed tiles,
      `KnownDangerAt` vs burn terrain for swim paths, stock scatterer
      terrain predicates).
- [ ] Build lands per the spec's build order, after `ALPHA_MECHANICS_KIT_1`,
      the miasma kit's RM_ generics, `LIQUID_TYPES_MOD_1`, and
      `FISH_BESTIARY_COMMISSION_1`.
- [ ] A quicktest map in the biome shows: forced steam weather with clear
      spells; a condenser producing on a vent and refusing placement off
      one; a pawn swimming the margin ring and never pathing through boil
      cells; a fishable water body once the bucket is ruled; wrecks in
      shallows salvageable at burn cost; sails anchored to vents.

## criteria

- Every mechanic traces to a sheet section; no lore invented outside
  **INVENTED** tuning values.
- All six §6 hard bans hold in the shipped defs (linter-checkable where the
  sheet says so: no drink/ingredient route on scald water, no burn-immunity
  def, no pawn spawner on wreck defs, no shared defs with the terminator
  seas).
- Naming per `design/NAMING_SCHEME_PLAN.md`: mechanisms `RM_`, Scald content
  `RUT_`; "Jawa" is lore text only.
