# SCARLANDS_RELOAD_MIDSTATE_1 — SC-5: Scarlands: save-and-reload checks for half-finished states (settling sweep mid-way, ring repair parts in a hauler, cradle mid-wake, pool mid-phase, chotrix mid-drag)

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row SC-5 (belt hygiene pass 2 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). Scope: Validation chain steps using the bridge save/load. Scarlands/validation.py has one save/load leg only (lacquered cloak); WARSCAR_VALIDATION_FIDELITY_1 does not cover reloads. Write the steps and their state reads offline; the run itself is an acceptance sitting.

The row:

| SC-5 | *(hygiene)* Save-and-reload checks for half-finished states: a Settling sweep mid-way, ring repair parts in a hauler's hands, a cradle mid-wake, a pool mid-phase, a chotrix mid-drag. | validation chain steps using the bridge save/load | M | low | Scarlands | `Scarlands/validation.py` has no save/load step; WARSCAR_VALIDATION_FIDELITY_1 covers settings list, compile claims, restore and proof hooks, not reloads |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: validation.py gains five reload steps, each with a stated state read before and after; selftest of the file passes. Live run owed as L1.
