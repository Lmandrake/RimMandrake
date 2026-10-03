# UTINNI_STATUES_SKELETON_BUILD_1 — Utinni statues, step 1

Child of `STATUE_ART_EXPANSION_1`; spec `design/RimMandrake/statue_mods_spec.md` §1 and §3 step 1.

## built

- New mod `src/RimUtinni/UtinniStatues/` (`mandrake.rut.utinnistatues`): `RUT_StatueSmall` (3 votives),
  `RUT_Statue` (the nine gods), `RUT_StatueGrand` (Ohm/Rekko/Sh'kaar grands + the crawler relief), made at the
  sculptor's table like vanilla sculptures (stats copy the vanilla tier).
- `RUT_CompStatuePicker` + `RUT_Building_Statue`: a "Dedicate…" button on a placed player statue picks
  its carving; label, "Honours" line, description and graphic follow. Placeholder = vanilla sculpture art
  until the carving's PNG exists at `Textures/Things/Building/Art/RUT_UtinniIdols/<carving id>.png`.
- Mod Settings: `statuesCraftable` (restart). First script `validation.py` + walk
  `design/validation_walks/RimUtinni/UtinniStatues.md`.
- Art wave one queued (16 jobs, `infrastructure/artpipe/art_lists/utinni_statues_wave1_2026-10-03.csv`).

## engineering call reported to the owner (spec §6, first bullet)

R8 asked for ONE statue with a picker. A def has one footprint and the carvings span 1x1 and 2x2, so the one
statue is three tiers that mirror vanilla's small/large/grand sculptures, each with the picker. The subject is
chosen on the placed statue, not in a 16-entry list. If he wants a single entry, a `designatorDropdown` cannot
apply (sculptures are crafted, not designated); the fallback is one recipe with a size choice, which is new C#.

## verify

- [ ] Live: `modcheck run UtinniStatues` GREEN (needs the companion carrying `jawa/static_call`).
- [ ] The mod is in a modset tier and deployed.
