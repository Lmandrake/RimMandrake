# BENCH_REBOOT_HANDOFF_202609242251 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609242130`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**Two naming laws and one fauna law landed today and bind every future batch.**
(1) Syllable VARIETY: no wall of two-syllable coinages — mix one/two/three.
(2) PLANET-WIDE slime law: every slime/goo/gel creature takes a long-vowel
MONOSYLLABLE (ghaaz, zhool, wuum, oomb, vohhm). Both recorded in
`design/Jawa/worldbuilding/biomes/noncanon_beast_names_crags_nightside_contagion_slime.md`
style rules + `NONCANON_BEAST_RENAME_1`. (3) `VANILLA_BEAST_EXCISION_1`:
vanilla/DLC animals are CUT at the Utinni scenario layer, never renamed,
biome-by-biome as each biome's own cast is ready — the RM_ tier is untouched.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
Nothing pending his eye — every ruling this wave was his, live (typed or by
card). Heads-up only: **126 art jobs** queued today (batch-3 renames + Blue
Desert depth cast) will fill `artpipe/done/` over the coming days — a review
sheet will be owed when they land. And `AA_Razorjack` skezzar/sytheclaw was
left DELIBERATELY unresolved on his warning (sytheclaw was mistakenly removed
from the Pyrelands) — it settles at the Pyrelands sitting, never by renaming
razorjack.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `BLUEDESERT_RM_MOD_BUILD_1` -- design input COMPLETE at `da0bc8a45` (weather by card, depth cast, epochs, cold-hold ship row); NEXT: FOUNDRY claims and builds — the owner's typed gate: the drift test must prove sand piles DEEP against structures.
- `NONCANON_BEAST_RENAME_1` -- doing; batch 3 applied at `d9b150ab5`; NEXT: draft the remaining batches per Appendix A (desert/miasma/poison-forest tail; sea batch waits on `TERMINALBIOMES_RM_MOD_BUILD_1`), applying the two new laws.
- `VANILLA_BEAST_EXCISION_1` -- proposed for FOUNDRY; NEXT: FOUNDRY censuses vanilla/DLC animal routes and stages per-biome cuts (pack-animal slot needs an owned beast first).
- `THEY_MOD_REPLICATION_1` -- proposed for FOUNDRY, ~a day; NEXT: FOUNDRY re-authors the ant surface + one JobGiver, then unwinds the About.xml dependency.
- `NIGHTSIDEICE_RM_MOD_BUILD_1` -- filed, design complete; NEXT: FOUNDRY claims (unchanged from last handoff).
- `STILLSAND_RM_MOD_BUILD_1` -- filed, carries the sand-buster ruling; NEXT: waits for its own sitting/build order (unchanged).
- `WEEPINGSTONES_RM_MOD_BUILD_1` -- Phase A split landed at `106b0dc16` (FOUNDRY); NEXT: FOUNDRY continues its waves.
- `FORCE_DISTURBANCE_REFLAVOR_1` -- filed; NEXT: FOUNDRY claims; draft text must card past the owner (unchanged).
- `BLUE_DESERT` art: 11 pre-existing plant/dessicated jobs + 12 new depth-cast jobs sit in `pending/`; NEXT: nothing — daemon churns them.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `fill_queue.py` expands each input row by its `facings` list — per-facing input rows file N× jobs with doubled suffixes (`_south_east`), and the dry-run count is the only tell; 36 malformed jobs filed and deleted same minute (filed: LESSONS_INBOX).
- `block_forged_owner_said.py` refused a genuine typed owner quote twice (apostrophe/transcript mismatch); the prescribed exit — drop the flag, file under own seat, name whose call in a note — worked cleanly (see: using-rimflow skill, already recorded).

## Closed since the last handoff (1)

- `BLUEDESERT_DESIGN_SITTING_1` — da0bc8a45

## Filed and still open (2) — the next seat's queue

- `VANILLA_BEAST_EXCISION_1` — No vanilla beasts in the Utinni scenario: cut every vanilla/DLC animal at the scenario layer, biome by biome as each biome's own cast is ready — never
- `THEY_MOD_REPLICATION_1` — Replicate They! (Giant Ants) in our own tier and retire the dependency — 1 race/2 kinds/hidden raid faction/carapace stuff+wall trivial XML, one small

## Commits

```
1d1388ff4 Blue Desert sitting working papers: cast gap-fill + weather feasibility
ece683f25 Ledger sync: BLUEDESERT_DESIGN_SITTING_1 closed at da0bc8a45
da0bc8a45 Blue Desert sitting ruled: depth cast, epochs, ship row, flora reaffirm
d2b982cb4 Fix stale aerofleet comment: fumerider was never ruled, bulloo is settled
0c1693f78 NONCANON_BEAST_RENAME_1: batch 3 recorded as ruled+applied
d9b150ab5 Apply batch-3 beast renames: 42 labels + descriptions across 4 biomes
4953827d2 Blue Desert 4b amended: drift/Haze/ice-fog mechanisms ruled at the sitting
1d92eb1c9 Batch 3 names ruled: syllable rebalance + planet-wide slime monosyllable law
b56656b75 rimflow: WEEPINGSTONES_RM_MOD_BUILD_1 wave 1 ledger note + queue re-render
106b0dc16 WEEPINGSTONES_RM_MOD_BUILD_1 Phase A: split RM_WeepingStones out of the RUT_ twin
78601b727 THEY_MOD_REPLICATION_1 filed: replicate They! and retire it
da5bcf10e VANILLA_BEAST_EXCISION_1 filed: no vanilla beasts in the Utinni scenario
82d021a2c rimflow: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 64 ledger note + queue re-render
2138aad8b DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 64: mark 8 files CLEAN
bf7b07033 rimflow: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 63 ledger note + queue re-render
ae807eebf Wave 63: mark 8 files CLEAN (7 selftest_deployed_biome_refs.py-class Utils selftests + the fix)
3e9f9b94e selftest_deployed_biome_refs.py: stop the Workshop scan lying with a zero on timeout
45c6493d8 Blue Desert picked as the next biome sitting; item filed and started
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-09-24T22:51:13Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.htmlhealth publisher's auto-rebuild — FOUNDRY loop's
 M Transient/codebase_health.jsonhealth publisher's auto-rebuild — FOUNDRY loop's
 M Transient/codebase_health_artifact.htmlhealth publisher's auto-rebuild — FOUNDRY loop's
 D infrastructure/artpipe/active/desertportb_feralgrazer_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/active/desertportb_feralnerf_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/active/desertportb_feralnerf_north.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_feralgrazer_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_feralnerf_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_feralnerf_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_feralnerf_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_horax_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_horax_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_horax_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kraytdragon_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kraytdragon_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_krykna_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_krykna_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_krykna_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetle_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetle_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetle_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_nerf_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_nerf_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_nerf_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_pikobis_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_pikobis_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_pikobis_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_plant_bloddle.manifest.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_graniteslug_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_graniteslug_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_graniteslug_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_grank_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_grank_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_grank_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_horax_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_horax_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_horax_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_jakobeast_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_jakobeast_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_jakobeast_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kraytdragon_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kraytdragon_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kraytdragon_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_krykna_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_krykna_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_krykna_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetle_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetle_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetle_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_nerf_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_nerf_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_nerf_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_pikobis_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_pikobis_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_pikobis_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_bloddle.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_porg_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_porg_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_porg_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_qormot_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_qormot_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_qormot_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_runyip_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_runyip_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_runyip_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_shaak_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_shaak_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_shaak_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_strill_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_strill_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_strill_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_teemuss_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_teemuss_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_teemuss_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_uvak_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_uvak_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_uvak_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_varactyl_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_varactyl_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_varactyl_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_voorpak_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_voorpak_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_voorpak_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_vulptex_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_vulptex_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_vulptex_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_warwyrm_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_warwyrm_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_warwyrm_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_whisperbird_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_whisperbird_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_whisperbird_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_zeer_east.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_zeer_north.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_zeer_south.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_brakkel_v1.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_brunnock_v1.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_cundral_v1.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_gorbeleth_v1.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_kaddrath_v1.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_maddrick_v1.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_mirrelbole_v1.jsonartpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_mourvel_v1.jsonartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/registry.jsonlartpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/throughput.jsonlartpipe daemon's churn — never commit mid-flight
 M infrastructure/dashboards/hub/data/health.jsonhealth publisher's auto-rebuild — FOUNDRY loop's
 M infrastructure/state/codebase_health_last.jsonhealth publisher's auto-rebuild — FOUNDRY loop's
 M infrastructure/state/ledger/events/FOUNDRY.jsonlFOUNDRY's live session — its own ledger sync
 M infrastructure/state/queue/BENCH.mdFOUNDRY's live session — its own ledger sync
 M infrastructure/state/queue/FOUNDRY.mdFOUNDRY's live session — its own ledger sync
 M src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_PyrelandsFauna.xmlFOUNDRY's — FIREHAWK_FLIGHT_BEHAVIOR_1 flip-book mid-flight, leave alone
?? deployed/config/ModsConfig.before-tier-firehawk.xmlFOUNDRY's — FIREHAWK_FLIGHT_BEHAVIOR_1 flip-book mid-flight, leave alone
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_east.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_north.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_south.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_east.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_north.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_south.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_east.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_north.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_south.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_east.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_north.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_south.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_east.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_north.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_south.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_east.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_north.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_south.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_east.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_north.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_south.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_east.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_north.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_south.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_east.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_north.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_south.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_east.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_north.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_south.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_east.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_north.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_south.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_east.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_north.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_south.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_east.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_north.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_north.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_south.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_south.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brakkel_v1.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brakkel_v1.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brunnock_v1.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brunnock_v1.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_cundral_v1.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_cundral_v1.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_gorbeleth_v1.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_gorbeleth_v1.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_kaddrath_v1.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_kaddrath_v1.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_maddrick_v1.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_maddrick_v1.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mirrelbole_v1.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mirrelbole_v1.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mourvel_v1.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mourvel_v1.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.manifest.jsonartpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/bluedesert_dovvik_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/bluedesert_dovvik_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/bluedesert_dovvik_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/bluedesert_utikka_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/bluedesert_utikka_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/bluedesert_utikka_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/bluedesert_vrisk_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/bluedesert_vrisk_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/bluedesert_vrisk_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/bluedesert_zhaaz_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/bluedesert_zhaaz_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/bluedesert_zhaaz_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_blisteredbulloo_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_blisteredbulloo_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_blisteredbulloo_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_brossak_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_brossak_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_brossak_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_fezzira_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_fezzira_larva_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_fezzira_larva_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_fezzira_larva_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_fezzira_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_fezzira_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_ghaaz_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_ghaaz_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_ghaaz_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_ghuvv_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_ghuvv_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_ghuvv_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_gollivra_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_gollivra_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_gollivra_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_greaterbulloo_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_greaterbulloo_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_greaterbulloo_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_pellorax_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_pellorax_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_pellorax_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_pibbo_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_pibbo_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_pibbo_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_vezzok_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_vezzok_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_vezzok_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_vulloth_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_vulloth_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_vulloth_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_zhirrik_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_zhirrik_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_zhirrik_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_zhool_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_zhool_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/contagion_zhool_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_brekkugar_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_brekkugar_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_brekkugar_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_dhukk_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_dhukk_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_dhukk_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_ghorrumak_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_ghorrumak_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_ghorrumak_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_gruzz_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_gruzz_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_gruzz_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_hulggarok_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_hulggarok_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_hulggarok_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_kessik_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_kessik_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_kessik_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_shekkur_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_shekkur_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_shekkur_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_thrizzik_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_thrizzik_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_thrizzik_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_ulkhorr_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_ulkhorr_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_ulkhorr_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_vrakk_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_vrakk_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_vrakk_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_zekkra_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_zekkra_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_zekkra_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_zhurrakor_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_zhurrakor_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/crags_zhurrakor_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/nightside_mahllik_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/nightside_mahllik_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/nightside_mahllik_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/nightside_zhissa_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/nightside_zhissa_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/nightside_zhissa_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_bezzul_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_bezzul_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_bezzul_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_greateroomb_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_greateroomb_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_greateroomb_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_hennul_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_hennul_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_hennul_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_mubbaro_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_mubbaro_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_mubbaro_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_oomb_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_oomb_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_oomb_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_thummorak_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_thummorak_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_thummorak_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_vohhm_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_vohhm_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_vohhm_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_wuppik_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_wuppik_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_wuppik_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_wuum_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_wuum_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_wuum_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_yollum_east.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_yollum_north.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/artpipe/pending/slime_yollum_south.jsonBENCH's (this session's 126 rename/depth-cast art jobs — daemon's sync commits them)
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xmlowner's Desktop tooling backups — his to commit or cull
?? infrastructure/state/ledger/events/OWNER.jsonlowner's Desktop tooling backups — his to commit or cull
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xmlowner's Desktop tooling backups — his to commit or cull
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xmlowner's Desktop tooling backups — his to commit or cull
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xmlowner's Desktop tooling backups — his to commit or cull
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xmlowner's Desktop tooling backups — his to commit or cull
?? src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_1_east.pngFOUNDRY's — FIREHAWK_FLIGHT_BEHAVIOR_1 flip-book mid-flight, leave alone
?? src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_1_north.pngFOUNDRY's — FIREHAWK_FLIGHT_BEHAVIOR_1 flip-book mid-flight, leave alone
?? src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_1_south.pngFOUNDRY's — FIREHAWK_FLIGHT_BEHAVIOR_1 flip-book mid-flight, leave alone
?? src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_2_east.pngFOUNDRY's — FIREHAWK_FLIGHT_BEHAVIOR_1 flip-book mid-flight, leave alone
?? src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_2_north.pngFOUNDRY's — FIREHAWK_FLIGHT_BEHAVIOR_1 flip-book mid-flight, leave alone
?? src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_2_south.pngFOUNDRY's — FIREHAWK_FLIGHT_BEHAVIOR_1 flip-book mid-flight, leave alone
?? src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_3_east.pngFOUNDRY's — FIREHAWK_FLIGHT_BEHAVIOR_1 flip-book mid-flight, leave alone
?? src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_3_north.pngFOUNDRY's — FIREHAWK_FLIGHT_BEHAVIOR_1 flip-book mid-flight, leave alone
?? src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_3_south.pngFOUNDRY's — FIREHAWK_FLIGHT_BEHAVIOR_1 flip-book mid-flight, leave alone
?? src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_4_east.pngFOUNDRY's — FIREHAWK_FLIGHT_BEHAVIOR_1 flip-book mid-flight, leave alone
?? src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_4_north.pngFOUNDRY's — FIREHAWK_FLIGHT_BEHAVIOR_1 flip-book mid-flight, leave alone
?? src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_4_south.pngFOUNDRY's — FIREHAWK_FLIGHT_BEHAVIOR_1 flip-book mid-flight, leave alone
?? src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_5_east.pngFOUNDRY's — FIREHAWK_FLIGHT_BEHAVIOR_1 flip-book mid-flight, leave alone
?? src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_5_north.pngFOUNDRY's — FIREHAWK_FLIGHT_BEHAVIOR_1 flip-book mid-flight, leave alone
?? src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_5_south.pngFOUNDRY's — FIREHAWK_FLIGHT_BEHAVIOR_1 flip-book mid-flight, leave alone
```

