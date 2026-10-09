# DEEPFIRE_FAMILY_SETTINGS_SAVE_LOAD_1 — keyed family settings survive a real Scribe save/load

65798d581 saves disabled families by key and migrates the legacy list. Fuzz and lint pass; the Scribe round trip was not unit tested.

## criteria
- [ ] Disable a family, save settings, reload: the same family is disabled by key.
- [ ] A settings file with the legacy list loads and migrates to keys.

## verify

Live settings write/read in game (L1/L2). Origin: DEEPFIRE_FAMILY_SETTINGS_KEYED_1.

## Watch out

Filed by the 2026-10-09 upkeep pass: the originating item was closed `implemented --none-owed` with only offline evidence. Mechanism-never-seen line: the offline fix changed the harness/mod code path itself, and that path has not been observed running since.
