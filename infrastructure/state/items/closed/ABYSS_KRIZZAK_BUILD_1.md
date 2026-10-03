# ABYSS_KRIZZAK_BUILD_1 — krizzak: the light-thief (new flying creature, RM_Krizzak)

Biome: the Abyss (`RM_Abyss` in `src/RimMandrake/Abyss/`, composed into `mandrake.rm.biomes`; campaign twin `RUT_Abyss`). Review/spec: `design/Jawa/worldbuilding/biomes/blackcrags_bedazzle_review_2026-09-30.md` (written under the old names Forsaken Crags / Black Crags; paths there predate the rename). Owner rulings of volley turn 1 (2026-09-30): the sitting item `BLACKCRAGS_BEDAZZLE_SITTING_1` and the report's 'Turn 1 rulings' section. Rule: every mod ships Mod Settings; the free `RM_` tier carries invented content, canon only through Utinni (Q11a).

## spec

Admitted by question card 2026-09-30. Report §4 row 3 (`RM_Krizzak`, ~0.3, alternate drekkis): a dark moth with a lamp-glass mouth that **eats light**; swarms settle on glow plants and dim them, and cluster on powered lamps so perimeter lamps go dark one by one. It attacks light, not power or hull.
🔴 **It flies, so it gets real flight** (owner standing rule 2026-09-19): `MaxFlightTime`/`FlightCooldown` stats, race flight flags, and the PawnKindDef flip-book (`flyingAnimationFramePathPrefix` + frame count) per the Chicken/Sparrow template in CLAUDE.md; never block flight on frames. Never live-test flight unattended; verify with a `Pawn_FlightTracker` state-read `[Tool]`. Neighbour mechanism: `CompLightAversion` and the lamp comps; search src/ first. Art: none exists (checked 2026-10-01); queue via artpipe, ground facings + flight frames. One home (the Abyss).

## criteria

- Def set with MaxFlightTime>0 and flight flags; roster row in `RM_Abyss`.
- Light-eating behaviour on lamps and glow plants, settings toggle.
- Flight verified by state read, not screenshot.
- Art generated and reviewed.

## verify

Offline build + selftests green; live proof is a joint session, never an unattended flyer/visual hunt.
