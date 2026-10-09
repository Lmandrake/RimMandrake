# MAP_SILENCE_SINGLE_OWNER_1 — FV-3: one owner for the map ambient-sound hush

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` (remaining rows, helper pass 2026-10-09; owner 'Queue all' card 2026-10-08). Row FV-3 there is the spec; its 'Checked' column says what was read to confirm it is unbuilt. Re-check src before building.

| FV-3 | **One owner for the map's silence.** The sentinel hushes the biome's ambient sound itself, and CreatureBehaviors' silence cue does the same independently. When either one ends, it restores the sound even if the other still wants quiet; the code already notes this as an "accepted overlap". Have both register a reason with one silence service that restores sound only when no reason is left. Silence is this biome's scariest cue, so it should never break early. | small shared service, probably in CreatureBehaviors | S–M | low | FeverWood, CreatureBehaviors | `RM_MapComponent_TentacleWatch.cs:540-560` (known overlap in `HushChorus`/`RestoreChorus`); `CreatureBehaviors/Source/RM_MapComponent_SilenceCue.cs`; no item covers it |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.
