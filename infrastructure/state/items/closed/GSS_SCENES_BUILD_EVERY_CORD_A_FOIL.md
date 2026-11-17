---
state: proposed
needs: game-up
---

# GSS_SCENES_BUILD_EVERY_CORD_A_FOIL

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

GSS proof scenes: named entry points in validation.py (and scene_walk in gss_playtest_runner.py) for every scenes.json scene, each with its asserted start, discriminating control, scene-begin/end snapshot restore, plus the two showcase stagings

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show GSS_SCENES_BUILD_EVERY_CORD_A_FOIL` history before building.

## latest ledger notes

- 2026-11-06: Coverage judge pass 2026-11-06: add entry points scene_owner_change and scene_fuel_ignition; scene_statics_new_game is now acceptance with a filled-state control; rebuilt controls for no_repeat, four_looks, spans, fallen_span, gravship (throwaway-save restore); sc_walk reads memory, save size, frame time, master off/on. Spec: design/concepts/GimmeSomeSlack/scenes.json

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify GSS_SCENES_BUILD_EVERY_CORD_A_FOIL --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=GSS_SCENES_BUILD_EVERY_CORD_A_FOIL` first: another commit may already do it.
