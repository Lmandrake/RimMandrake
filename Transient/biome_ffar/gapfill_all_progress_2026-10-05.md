# Gapfill-all progress 2026-10-05 (BIOME_FLORAFAUNA_ART_REVIEW_1)

Owner rule (2026-10-05, verbatim): "any remaining MLIE, donor, alpha animals, alpha biomes, etc. art MUST be regenerated at least once for me tonight and wired into the sheets ... I DO want to see donor art in 'past art' so I can see where something came from though ... I just don't want it to be all there is."
Donor art stays on every sheet as history; each donor row must also carry a render of ours.

Jobs: `Transient/biome_ffar/gapfill_all_jobs_2026-10-05.json` — 94 rows, 196 jobs (per facing) queued, ids `gapall_<def>_v1`, priority 20 (class a) / 30 (class b). Excludes Abyss, BlueDesert, LongShade, Stillsand.
Classes: (a) donor-only rows with no render of ours = 89; (b) missing facing = 5 (Miasma scuttlers, live art south only; re-rendered as full 3-facing sets); (c) failed_canon renders: 42, all on the four excluded sheets, none here; (d) magenta/missing texture: 0 flagged by census.
Rows whose census shows donor art but already have a done render in artpipe by name (121) count as satisfied; the rebuild's census re-join will confirm.
Flying rows with donor flip-book frames (not renderable as facing jobs; need an 8-frame set): RM_Cauldron 2, RM_FeverWood 4, RM_FloodedCanyon 3, RM_Greentide 9, RM_LeaningScrub 9, RM_Miasma 2, RM_Pyrelands 1, RM_TheForge 2, RM_Wasteland 3, RM_WeepingStones 2

Drain: throughput ~20-25 ok jobs/hr (53 in 3h, 25 in 1h); pending 246 at queueing incl. other agents' priority-10 work => roughly 10-12 h for all, so NOT tonight. Rows owed rendering per biome (donor rows still awaiting a render, all of them as of queueing):

| biome | donor rows awaiting render (a) | missing facings (b) |
|---|---|---|
| RM_Cauldron | 18 | 0 |
| RM_FeverWood | 3 | 0 |
| RM_FloodedCanyon | 2 | 0 |
| RM_GelatinousSlime | 1 | 0 |
| RM_Greentide | 4 | 0 |
| RM_LanternDeeps | 10 | 0 |
| RM_LeaningScrub | 4 | 0 |
| RM_Miasma | 4 | 5 |
| RM_NightsideIce | 2 | 0 |
| RM_Pyrelands | 2 | 0 |
| RM_RustCathedral | 2 | 0 |
| RM_TheForge | 9 | 0 |
| RM_TheRot | 3 | 0 |
| RM_TheScald | 1 | 0 |
| RM_TheSump | 1 | 0 |
| RM_TwilightSea | 1 | 0 |
| RM_Warscar | 6 | 0 |
| RM_Wasteland | 2 | 0 |
| RM_Webwork | 1 | 0 |
| RM_WeepingStones | 13 | 0 |

Sheets rebuilt: see below (none until renders land).
