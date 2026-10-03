# ABYSS_GHARREK_BUILD_1 — gharrek: the gust-feeder (new creature, RM_Gharrek)

Biome: the Abyss (`RM_Abyss` in `src/RimMandrake/Abyss/`, composed into `mandrake.rm.biomes`; campaign twin `RUT_Abyss`). Review/spec: `design/Jawa/worldbuilding/biomes/blackcrags_bedazzle_review_2026-09-30.md` (written under the old names Forsaken Crags / Black Crags; paths there predate the rename). Owner rulings of volley turn 1 (2026-09-30): the sitting item `BLACKCRAGS_BEDAZZLE_SITTING_1` and the report's 'Turn 1 rulings' section. Rule: every mod ships Mod Settings; the free `RM_` tier carries invented content, canon only through Utinni (Q11a).

## spec

Admitted by question card 2026-09-30. Report §4 row 1 (`RM_Gharrek`, ~0.6 commonality, alternate name krovvak): a flat, many-gilled crawler that lies dormant and cold in the still and bursts open across the map at every gust to feed on the air; the base of the web. Reads a shared gust signal (report §5 item 8 `RM_GustController`; build the signal minimally if the controller does not exist yet). Cheap to build; wire `RM_Abyss` `<wildAnimals>` (element form, not `<li>`). Art: none exists (checked `artpipe/done/`, `_artsrc/`, 2026-10-01); queue via the artpipe `fill_queue.py` conventions, 3 facings. One home only (the Abyss).

## criteria

- ThingDef + PawnKindDef + race, rostered at ~0.6 in `RM_Abyss`.
- Dormant/feeding behaviour keyed to gusts.
- Art generated and reviewed.

## verify

Offline build + selftests green; live proof is a joint session, never an unattended flyer/visual hunt.
