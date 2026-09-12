# MOD_OPTIONS_RETROFIT_1 — superb mod-options support, every mod, forever

Owner, 2026-09-12 (verbatim on the filing event): every one of our mods gets
"superb mod options support to tailor behavior and turn certain options on and
off" — retrofit all mods so far, requirement on all future mods. Trigger case:
the Greentide standalone mod must let a player enable individual special
contents (the Greatbole, sinking mud/churnmud, etc.) in OTHER biomes without
inserting the whole biome.

## spec
- Inventory every shipped/in-progress mod under `src/RimMandrake/`,
  `src/RimStarWars/` (if any), `src/RimUtinni/` that has player-facing
  behavior. For each: a `Mod` subclass + `ModSettings` with a real settings UI
  (`DoSettingsWindowContents`), not a stub.
- Per mod, expose at minimum: on/off per major feature/mechanic, and tuning
  where a number is the experience (spawn rates, intervals, damage scalars).
  Defaults = current shipped behavior; all-off must degrade gracefully (no
  NREs, no orphaned defs — features gate at the comp/mapcomponent/patch level).
- Greentide (rides `GREENTIDE_STANDALONE_MOD_1`): per-feature biome opt-in —
  Greatbole spawning, churnmud/mire, buried caches, each enableable in other
  biomes via settings (biome allowlist or "everywhere" toggle) without the
  Greentide biome itself.
- Settings that alter map generation vs live behavior must say which they are
  in the UI (worldgen-frozen campaign: some toggles only affect new maps).
- The requirement is DOCTRINE for future mods — recorded in project CLAUDE.md
  (this change) and folded into the rimworld-modding skill at next curation
  (LESSONS_INBOX line filed).

## verify
Every mod in the inventory has a settings screen listing its features;
toggling a feature off provably disables it live or at next map-gen (say
which) with no errors; Greentide features work in a non-Greentide biome when
opted in.

## criteria
Owner can open Mod Settings on any of our mods and meaningfully tailor it.
