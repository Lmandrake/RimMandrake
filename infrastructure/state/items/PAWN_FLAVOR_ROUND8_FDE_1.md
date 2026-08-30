# PAWN_FLAVOR_ROUND8_FDE_1 — FDE droid grouping set

## Shipped
Seven entries per `pawn_flavor_design.md` round-8 (Assembly=Childhood,
Service=Adulthood), new file `Defs/Backstories_FDE_Droids.xml`: CATHEDRAL 3
(Congregation-Consecrated childhood, Cathedral-Whispered + Cathedral-Mason
adulthood) and NIGHTSIDE 3 (Cold-Forged childhood, Pipe-Keeper + Dirty-Burner
adulthood), plus shared trait `Jawa_FreedomScarred` and two supporting traits
(`Jawa_NightsideHardy`, `Jawa_DirtyBurnerAffinity`) in
`Traits_JawaPawnFlavor.xml`.

Wired onto all four existing FDE `PawnKindDef`s (`Jawa_Droid_Grunt/Heavy/
Specialist/Leader`, `defaultFactionDef Jawa_FreeDroidEnclaves`) via
`backstoryFilters` — both Cathedral and Nightside categories on all four (the
owner's geography ruling names two settlements, no kind-to-settlement split;
inventing one would be a guess). Droidworks' `DW_` kinds carry no FDE faction
assignment yet (wave 1 assigned none — checked `gen_droidworks_defs.py`'s own
printed note), so the DW_ half of "wire both" genuinely cannot be done until
wave 2 assigns them; noted as owed then, not silently dropped.

Register guard respected: read `canon.yml`'s `assailant_reveal_arc` and
`free_droid_enclaves.geography` before writing Cathedral entries — whispered
voices/listening/trance stay sensory flavor (already-sanctioned ambient fact),
never who/what/why, which stays the arc's own reveal.

Real vanilla stat mappings verified via RimSage before use:
`ComfyTemperatureMin/Max` + `MoveSpeed` (Nightside-Hardy — the heat-break-weight
piece is NOT stubbed; lowering `ComfyTemperatureMax` feeds the existing vanilla
heat-discomfort-thought pipeline honestly) and `ToxicResistance` (Dirty-Burner).
Five mechanics honestly stubbed (foreign-memory-flicker, listening-trance,
unease-aura-for-organics, mood-near-Forsaken-ruins/sacrilege-on-deconstruction,
hoards-charge/low-power-mood, Freedom-Scarred's opinion-penalty — this last
ties naturally to Droidworks' `DW_RestrainingBolt`/`DW_BoltResentment`, noted
for whoever builds the C#). Pipe-Keeper's tireless/permanent-mood-debuff left
undone rather than half-implemented: `RestRateMultiplier` could cover tireless,
but vanilla `TraitDegreeData` has no flat always-on mood field for the debuff
half.

## Verify
`validate_patch.py`: 0 errors across all files (same 8 pre-existing warnings;
`JawaFactionRoster.xml` itself 0 errors, 0 warnings). `deploy_custom_mods.py
--mod Jawa_PawnFlavor`: in sync. Plain def additions — offline validation is
the verification here per CHARTER.

## criteria
- [x] Seven entries shipped per the design doc's round-8 block.
- [x] Wired onto all four existing FDE PawnKindDefs; DW_ half explicitly
      deferred to wave 2 (no faction assignment exists yet to wire onto).
- [x] Register guard respected — no reveal-arc content leaked.
- [x] Real vanilla stats verified before use; stubs and honest omissions
      documented rather than faked.
- [x] validate_patch.py clean against the live mod set.
- [x] Deployed, in sync.
