# SALT_TRAVELS_WITH_DOOR_1 — TB-2: door salt stored on the door, survives flight/minify

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` (remaining rows, helper pass 2026-10-09; owner 'Queue all' card 2026-10-08). Row TB-2 there is the spec; its 'Checked' column says what was read to confirm it is unbuilt. Re-check src before building.

| TB-2 | Salt on a door should travel with the door. Today the salt is a list of door ids pruned once a day from buildings on loaded maps, so a door that is mid-flight on the gravship (or minified) at midnight silently loses its salt. Put the salt on the door itself. | nothing | S | low | TerminalBiomes | `RM_GreyHullCrust.cs:148-165` daily prune over `Find.Maps … allBuildingsColonist`; gravship contents are off-map during travel. Not in VERDICTS (#3 is the settings gate only). |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.

## verify

- Offline: build clean; daily prune drops a salted id only after two consecutive misses, and minified doors count as alive; new saved set saltedDoorMissedOnce (old saves load empty).
- L2 (owed, bridge): salt a door, fly the gravship across midnight, door still salted.
