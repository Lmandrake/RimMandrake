
## spec

Owner answered 'Queue all' on a question card 2026-10-08 (decision taken by question card) for the remaining work of `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md`. Row CB-8 there is the spec:

| CB-8 | A decoy shade tarp: a cheap painted awning that predators that hunt from shade read as real shade, though it gives no real cooling. Players use it to lure heat-driven predators into a killbox or pen. A mirrak-hide version is more convincing. | A building carrying a "reads as shade to seekers" extension, built on the creature-only false-shade read; research-gated, with a settings toggle. | M | med (balance: free predator control) | CreatureBehaviors, LongShade (mirrak hide) | `RM_FalseShade.cs` RM_FalseShadeExtension is on race defs only (used by `LongShade/.../RM_LongShade_Mirrak.xml`); `RM_ShadeClothExtension` deepens real shade only; no "decoy" item found in items/ or design/ |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.

## verify

Record each owed criterion with `rimflow verify DECOY_SHADE_TARP_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- A1 (L1): decoyShadeEnabled wired and gated (mechanic_toggles.decoyShade_wired_and_gated); tarp def and research resolve
- A2 (L2): a shade-seeking animal paths to a placed decoy tarp and the shade grid reads 0 under it (art owed: tent textur
Evidence is the Player.log line or bridge state read the criterion names.
