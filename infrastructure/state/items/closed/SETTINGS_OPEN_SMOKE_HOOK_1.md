# SETTINGS_OPEN_SMOKE_HOOK_1

## spec

Add a debug hook that instantiates each Mod subclass from our assemblies and calls DoSettingsWindowContents on an off-screen rect, returning opened=<N> failed=<list>, readable via jawa/static_call. MOD_OPTIONS_RETROFIT_1.A1 (Mod Settings opens for each of our mods with no red errors) has no bridge instrument: a log grep alone proves nothing about pages nobody opened.

Filed from the 2026-10-09 acceptance-check pass (Transient/belt_acceptance_checks_20261009.md).

## verify

A state read through `jawa/static_call` on a loaded quicktest map returns the named fields; the owning acceptance criterion records the result.

## note

Built 2026-10-09 (source 1b7fbe441): JawaBenchSettingsSmoke and jawa/map_comp_read are in the companion SOURCE only; the companion DLL is NOT deployed - a game-down window must run `build.py --gm --apply` before either answers. Hediff lists already exist as jawa/pawn_health, inspect strings as jawa/inspect_string.
