# SLIME_STREAM_ROWS_1 — R/G/W (+yellow) mucosal slime as viscous streams and pools

Filed by BENCH, 2026-09-13. The owner's #1 REALLY-want from the liquids
sitting (`design/RimMandrake/liquids_framework_design.md` §3, §4).

## spec

Four slime rows: RED, GREEN, WHITE as distinct liquids (distinct hazards +
cuisine tags each — not recolors); YELLOW = actual human snot, authored as the
documented example row others follow. Purple is DROPPED (owner 2026-09-13) —
do not add it. Each row: Heavy viscosityClass, canal FluidDef with slow
`ticksPerTile` (the oozing-stream look), terrain adoption from ManyWaters
`RM_Slime_*` + GelatinousSlime `RM_Slime_Liquid`, natural-source vents that
auto-prime reservoirs.

## criteria

Written by FOUNDRY 2026-09-18 (item was THIN — no criteria section existed).
Derived from the item's own `## spec`/`## verify` text above, not invented
fresh:

1. Exactly four new slime rows exist in the LiquidDef registry: RED, GREEN,
   WHITE, YELLOW. No PURPLE row anywhere (owner dropped it 2026-09-13).
2. Every row's terrain is ALWAYS-LOADED — no `MayRequire` gate, resolvable
   under "minimal list + FlowWorks alone" (the registry item's own verify
   bar) — because the only previously-known slime terrain donors are
   gated (ManyWaters' `RM_Slime_<Colour>` needs `sarg.alphabiomes`) or
   single-color and belong to a separate optional mod (GelatinousSlime's
   `RM_Slime_Liquid`). New terrain is authored in FlowWorks itself,
   recoloring a vanilla texture already in FlowWorks' own palette
   (`WaterShallowRamp`/`WaterDeepRamp`) rather than generating new art —
   the "colour with material, not paint" convention this codebase already
   uses for its own `RM_Water_<Colour>`/`RM_Tar` rows.
3. Every row carries `LiquidViscosityClass.Heavy` and a canal `FluidDef`
   whose `ticksPerTile` is slower than water's 60 and slower than tar's
   360 — visibly-slower-than-water oozing, per the spec.
4. Distinctness: the four rows differ from EACH OTHER in at least one
   recorded `RM_LiquidProperties`/`LiquidDef` field beyond `color` — a
   damage spec, `pH`, `corrodesApparel` or `flammable`, not a bare recolor.
5. Natural-source vents: a natural (non-excavated) placement of a row's own
   terrain auto-registers as a limitless source and auto-primes an adjacent
   dug channel, with no new C#. This falls out of the already-shipped
   `RM_MapComponent_Excavation.IsSourceCell`/`FillAt` (any natural,
   non-excavated cell whose `TerrainDef.IsWater` is true — i.e. carries the
   vanilla `Water` tag — reads as a full/limitless source) — the row's
   terrain must therefore inherit or carry that tag, same as every other
   FlowWorks liquid row already does.
6. YELLOW (human snot) ships as the most heavily-commented row in the
   table — a worked example a future contributor can copy field-for-field.
7. `validate_patch.py` clean, `dotnet build` clean (no C# touched, so this
   is a no-op check), and the generator's existing rows regenerate
   byte-identical (diff before commit) — this pass only adds new rows, it
   does not touch anything already shipped.
8. Live quicktest (owed if bridge time allows, not required to leave the
   item `doing` if it isn't reached): a stream fed from one of the four new
   vents advances slower than water, pools, and holds.

## verify

Quicktest: spawn a slime vent; watch a stream advance at visibly-slower-than-
water rate, pool, and hold. Distinctness check: the three colors differ in at
least one recorded property/tag, not only color. Blocked on
FLOOD_ENGINE_CORRECTIONS_1 landing first.

## Watch out

- ~~Depends on FLOOD_ENGINE_CORRECTIONS_1~~ — RE-VERIFIED 2026-09-19: that
  item is `superseded` (by FLOWWORKS_BUILD_PROGRAM_1, which has since
  landed and is the live engine); its own history already recorded all
  three named defects fixed 2026-09-02. Non-blocker, confirmed again before
  building on it.
- LIQUID_REGISTRY_CORE_1 (`doing`) is the registry these rows live in — its
  2026-09-18 note deferred slime specifically because the only
  always-loaded slime terrain (GelatinousSlime's single `RM_Slime_Liquid`)
  belongs to a separate, optional mod, and ManyWaters' tinted
  `RM_Slime_<Colour>` rows are `MayRequire="sarg.alphabiomes"`. SOLVED this
  pass by authoring four NEW FlowWorks-owned terrain suites (tinted vanilla
  `WaterShallowRamp`/`WaterDeepRamp`, no new art, no gate) rather than
  adopting either donor — see `Tools/generate_liquid_suite.py`'s
  `slime_red`/`slime_green`/`slime_white`/`slime_yellow` `LIQUID_ROWS`
  entries and matching `LIQUID_DEF_ROWS` rows.
- ManyWaters' own `RM_Slime_<Colour>` rows and GelatinousSlime's
  `RM_Slime_Liquid` are UNTOUCHED by this pass — this item did not adopt
  either, it authored parallel new terrain instead, so nothing about the
  existing MayRequire gate changed.
