# DEEPFIRE_HEALTH_CHECK_1 — LP-9: Deepfire health check: debug action listing orphan light proxies, pawn lights on the wrong map and cluster members outside their light, plus validation lines locking in the fixed bugs

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row LP-9 (belt hygiene pass 2 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). Scope: New debug action beside DeepfireStatusDebugActions.cs plus validation.py chain additions: split keeps coats, a failed paint eats no pigment, a departed pawn leaves no light. Read-only.

The row:

| LP-9 | *(hygiene)* A "deepfire health" check that lists orphan light proxies, pawn lights left on the wrong map and cluster members outside their light, plus validation lines that lock in the 30 fixed bugs (split keeps coats, a failed paint eats no pigment, a departed pawn leaves no light). | debug action + validation.py chain additions | M | low | LuminousPigment | `DeepfireStatusDebugActions.cs`, `validation.py` (no orphan/split/departure checks found) |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: LuminousPigment builds; the action lists the three orphan classes (zero on a clean map); validation.py gains the three lines.
