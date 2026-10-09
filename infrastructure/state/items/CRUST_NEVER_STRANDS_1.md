
## spec

Owner answered 'Queue all' on a question card 2026-10-08 (decision taken by question card) for the remaining work of `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md`. Row TB-6 there is the spec:

| TB-6 | **(owner question, safeguard)** Make sure the crust can never trap a colony on the Grey sea floor: the ship is the only way out, and launch is refused while crust remains. If some crust is unreachable (behind a salted door, sealed space) or no one can work, either name exactly which cells block launch and why, or allow a costly "tear free" launch that damages the hull. | owner ruling on a tear-free launch | M | med (touches a ruled launch gate) | TerminalBiomes | `RM_Patch_GravEngineLaunchGate.cs:8-46` "never-strand guarantee" is argued, not tested ("no selftest harness … exercises gravship launch"); GREYSEA_HULL_CRUST_BUILD_1 (closed) and TERMINALBIOMES_REVIEW_FIXES_1 (live, null-guard only) don't cover blocked access. |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.

## owner card (ask before building)

Header: `Crust trap` · Question: *If salt crust on the Grey sea floor can't be cleared (behind a sealed door, or nobody able to work), how should the ship get out?*
1. **Name the blockers** — launch stays refused, but the refusal lists exactly which crust cells hold the deck and why each is unreachable. No new escape route.
2. **Tear-free launch** — a costly forced launch that rips the ship loose and damages the hull. Always an exit; costs repairs.
3. **Both** — name the blockers first; offer tear-free only when some crust is provably unreachable.
(Free-text answer always allowed.)

## verify
Built 2026-10-09 (all numbers PROVISIONAL): engine gizmo "Tear free" on the Grey Sea floor (`RM_GreyTearFree`, TerminalBiomes `RM_GreyHullCrust.cs`); strips hull crust, unsalts doors, damages every hull building by `greyTearFreeDamage` (default 30% of max HP, never lethal). Mod Settings toggle `greyTearFreeEnabled` + damage slider.
- Offline: `RM_CrustKernel.TearDamage` selftest check (never lethal).
- Live (needs bridge): `validation.py` chain `grey_hull_crust` calls `RM_GreyHullCrustProof.ProofTearFree` and asserts `crust=0`, `gate=accepted`, `tearFreeOffered=True`. State read, no screenshots.
