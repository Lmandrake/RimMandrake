# LIQUID_LOGISTICS_MOD_1 — hoses, portable pumps, the universal cargo tank, the tanker raid

Filed by BENCH, 2026-09-13 (owner pillar: the tanker ship —
`design/RimMandrake/liquids_framework_design.md` §4 "Tanker raid" +
"Universal tank interop" + "Liquid trade", §5).

## spec

NEW mod `RimMandrake: Liquid Logistics`. Build order inside the item (each
step already useful alone): (1) universal cargo tank — minifiable, holds any
(LiquidDef, amount); (2) universal pump — pulsed transfers, no per-tick flow,
draws from any cell whose terrain belongs to a row; (3) `RM_HoseSpool` —
fast-deploy, cheap, fragile conduit-style hose with a length cap (NOT terrain,
NOT a VE pipe), conduit-style network linking pump→tank; (4) the tanker loop:
fly to a typed body, deploy, pump, retrieve, leave; (5) the BULK BROKER
interface (owner-ruled 2026-09-13, both directions — nothing like it exists
in game): a custom dialog on the tank/manifold, trader-in-range or
settlement-docked → pump-to-sell AND pay-to-fill, price = row marketValue ×
amount, weighted by settlement world tag. NO vanilla trade-window Harmony —
rejected as the most conflict-prone patch surface on the 599-mod list; the
vanilla-native route is barrels (LIQUID_BOTTLE_LOOP_1).
ADAPTERS, owner-ruled: every supported pipe net (VE PipeSystem chemfuel/
deepchem, VGE astrofuel) can feed FROM our tank and draw INTO it, and their
pumps can pump from it. Adopt existing tank families — ship no other storage.

## verify

Quicktest per step. End-to-end: a gravship lands at a tagged brine sea,
pumps N units, flies, sells from the tank. Adapter check: a VE chemfuel net
fills from our tank holding chemfuel. Pump refuses a cell whose terrain
belongs to no row.

## Watch out

- model: opus — the heaviest new C# in the framework (hose network comp, pump
  metering, tank contents typing, trade UI).
- Depends on LIQUID_REGISTRY_CORE_1 and WORLDMAP_LIQUID_TAGS_1 (the raid
  targets tags).
- VE PipeSystem interop: read VanillaExpandedFramework's PipeSystem source
  before writing the adapter — never guess its net registration.
- Set-pieces stock the stealable pumps/tanks (LIQUID_INDUSTRY_SETPIECES_1) —
  keep the defs here, the placement there.
