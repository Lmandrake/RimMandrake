# PAWN_FLAVOR_ROUND9_FUEL_1 — Junkers fuel economy

## Shipped
Three defs per `pawn_flavor_design.md` round-9: `Jawa_ShoreRat` (Childhood),
`Jawa_StillMaster` + `Jawa_PipeTapper` (Adulthood), appended to
`Backstories_Moot_Wildsteam_Junkers.xml`, same `JawaBSC_Junkers` spawnCategory
already wired to `Jawa_Junkers` — no new wiring needed. Three supporting traits
in `Traits_JawaPawnFlavor.xml`.

Two real vanilla stat mappings, verified via RimSage before use:
`ToxicResistance` (Shore-Rat's `Jawa_ShoreHardened`, +0.3) and
`ComfyTemperatureMin` (Pipe-Tapper's `Jawa_LineTapper`, -8, cold resistance).
Two mechanics honestly stubbed per the item's own instruction rather than
faked: Still-Master's mood-buff-at-high-fuel-stores and rage-break-when-
stills-idle both need a StatPart/MentalBreak hook reading live colony state;
Pipe-Tapper's opinion-penalty-from-FDE-droids needs a relational ThoughtDef
keyed to the other pawn's kind — no TraitDegreeData field expresses that, so
it's prose-only, not an invented always-on number. Shore-Rat's
swimming/hauling floors and permanent low expectations don't map to any real
vanilla skill or stat (swimming/hauling aren't RimWorld skills at all) — left
as prose for the same reason, not bent to fit a wrong lever.

## Verify
`validate_patch.py`: 0 errors against the live 585-mod set (same 8
pre-existing warnings, unrelated file, unchanged). `deploy_custom_mods.py
--mod Jawa_PawnFlavor`: in sync. Plain def additions — offline validation is
the verification here per CHARTER.

## criteria
- [x] Three defs shipped per the design doc's round-9 block.
- [x] Wired into the existing spawn category, no new wiring patch needed.
- [x] Two real mechanics mapped to verified vanilla stats; remaining
      mechanics honestly left as prose/stubs where no real hook exists.
- [x] validate_patch.py clean against the live mod set.
- [x] Deployed, in sync.
