# SETTINGS_OPEN_SMOKE_HOOK_1

## spec

Add a debug hook that instantiates each Mod subclass from our assemblies and calls DoSettingsWindowContents on an off-screen rect, returning opened=<N> failed=<list>, readable via jawa/static_call. MOD_OPTIONS_RETROFIT_1.A1 (Mod Settings opens for each of our mods with no red errors) has no bridge instrument: a log grep alone proves nothing about pages nobody opened.

Filed from the 2026-10-09 acceptance-check pass (Transient/belt_acceptance_checks_20261009.md).

## verify

A state read through `jawa/static_call` on a loaded quicktest map returns the named fields; the owning acceptance criterion records the result.
