# BENCH_REBOOT_HANDOFF_202609242130 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609242041`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**Vanilla's infestation event now has ONE planetary home — the Dune Sea — and is
BANNED everywhere else at the Utinni scenario layer** (owner, 2026-09-24, at the
Nightside sitting; `dune_sea.md` amendment). The insects become **sand busters**
(erupt, never swim), rebuilt to the sheet's giant-or-grain-scale law. No other
biome sitting may re-grant the incident, and any doc implying infestations fire
elsewhere is now false on sight.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
Nothing pending his eye — every ruling this wave was his, made live in the
sitting. For reading pleasure only: the two research briefs behind the ice design,
`D:\Luke\dev\Rimworld\Transient\nightside_ice_research_rimworld_prior_art.md` and
`D:\Luke\dev\Rimworld\Transient\nightside_ice_research_starwars_canon.md` (~14-day
shelf life).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `NIGHTSIDEICE_RM_MOD_BUILD_1` -- filed, design input COMPLETE (sheet §4c + roster); NEXT: FOUNDRY claims and builds — the novel C# is the rumble-tell tracker and the continuous heat→breach dial.
- `STILLSAND_RM_MOD_BUILD_1` -- filed; carries the sand-buster ruling (castes + biome-gated incident) and UtinniPatches owes the planet-wide incident ban; NEXT: unchanged — waits for its own sitting/build order.
- `WEEPINGSTONES_RM_MOD_BUILD_1` -- filed; gained the canyon-filling crab (AA_SummitCrab adaptation, new_defs row); NEXT: unchanged.
- `FORCE_DISTURBANCE_REFLAVOR_1` -- filed for FOUNDRY (psychic storms → Force disturbances, RSW tier); NEXT: FOUNDRY claims; draft text must card past the owner.
- `NONCANON_BEAST_RENAME_1` -- still owner-gated; batch 3b (Nightside) rewritten to 2 rows after the eviction — zhissa + mahllik renames/refashions still owed on the creatures; NEXT: card the remaining batches to the owner when he next sits.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- zsh treats a bare `=word` argument as command-path expansion, so `echo ===` errors with "== not found" and kills the whole compound command — quote it (filed: LESSONS_INBOX).
- `block_forged_owner_said.py` can refuse a genuine typed owner ruling when the quote arrived mid-tool-turn; the prescribed exit (drop the flag, note under own seat naming whose call it was) worked cleanly (see: using-rimflow skill, already recorded).

## Closed since the last handoff (1)

- `NIGHTSIDE_ICE_DESIGN_SITTING_1` — 53ab8ca3a

## Filed and still open (1) — the next seat's queue

- `FORCE_DISTURBANCE_REFLAVOR_1` — Reflavor vanilla psychic assault/drone storm events as disturbances in the Force at the RimStarWars tier

## Commits

```
54ecefac8 Ledger sync: NIGHTSIDE_ICE_DESIGN_SITTING_1 closed at 53ab8ca3a
53ab8ca3a Nightside cast closed by card; Dune Sea gets the sand busters
489ed03cf Ledger sync: STOCKED_POOL_BUILD_1 claimed/started/wave-1-noted, queue re-rendered
28b55c323 Nightside Ice sitting: all six donor residents evicted; hoarfrost ice forms
86641f9a1 Ledger sync: queue 24 art jobs for STOCKED_POOL_BUILD_1's 8-species bestiary
2fb459d99 STOCKED_POOL_BUILD_1 wave 1: RM_WeepingStones mod scaffold, 8-row stocked-pool bestiary, doubt-meat mood economy, cuisine recipes
351526708 Ledger sync: OASIS_MAKER_BUILD_1 closed at bb984a61b
bb984a61b Build the Oasis Maker mod (OASIS_MAKER_BUILD_1)
e79c2f7f5 Nightside Ice 4c: wyrmlets + erupting nest extend the apex (owner, sitting)
c155b653d Nightside Ice sheet 4c: tunneler slate of 6 ruled in, with the hull rule
617ce9cfd Ledger sync: WATER_TRUCE_RETRIBUTION_1 closed at 7a61fc356
7a61fc356 Build water-truce retribution (WATER_TRUCE_RETRIBUTION_1)
195e0bc2c FORCE_DISTURBANCE_REFLAVOR_1 filed: psychic storm events become Force disturbances (RSW tier)
57b28a3f7 Nightside Ice picked as the next biome sitting; item filed and started
9bd761a64 Ledger sync: FOUNDRY seat idle for handoff
8e90ee7f2 Ledger sync: final queue projection refresh at handoff
0c1db0075 FOUNDRY handoff 202609242045: rulings acted on, census/census wrapped, wave 62 fixes
7bce6f5d1 rimflow: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 62 ledger note
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-24T15:03:39Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   — health publisher's rebuild artifacts — re-dirtied by every code_review_status call
 M Transient/codebase_health.json   — health publisher's rebuild artifacts — re-dirtied by every code_review_status call
 M Transient/codebase_health_artifact.html   — health publisher's rebuild artifacts — re-dirtied by every code_review_status call
 D infrastructure/artpipe/active/desertportb_feralgrazer_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/active/desertportb_feralnerf_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/active/desertportb_feralnerf_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_feralgrazer_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_feralnerf_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_feralnerf_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_feralnerf_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_grank_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_grank_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_grank_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_horax_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_horax_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_horax_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_kraytdragon_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_kraytdragon_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_krykna_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_krykna_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_krykna_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_mossbeetle_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_mossbeetle_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_mossbeetle_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_nerf_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_nerf_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_nerf_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_pikobis_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_pikobis_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_pikobis_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/done/desertportb_plant_bloddle.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_graniteslug_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_graniteslug_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_graniteslug_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_grank_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_grank_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_grank_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_horax_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_horax_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_horax_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_jakobeast_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_jakobeast_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_jakobeast_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_kraytdragon_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_kraytdragon_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_kraytdragon_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_krykna_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_krykna_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_krykna_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_mossbeetle_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_mossbeetle_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_mossbeetle_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_nerf_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_nerf_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_nerf_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_pikobis_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_pikobis_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_pikobis_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_plant_bloddle.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_porg_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_porg_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_porg_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_qormot_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_qormot_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_qormot_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_runyip_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_runyip_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_runyip_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_shaak_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_shaak_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_shaak_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_strill_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_strill_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_strill_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_teemuss_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_teemuss_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_teemuss_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_uvak_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_uvak_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_uvak_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_varactyl_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_varactyl_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_varactyl_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_voorpak_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_voorpak_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_voorpak_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_vulptex_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_vulptex_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_vulptex_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_warwyrm_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_warwyrm_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_warwyrm_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_whisperbird_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_whisperbird_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_whisperbird_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_zeer_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_zeer_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/desertportb_zeer_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/rm_brakkel_v1.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/rm_brunnock_v1.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/rm_cundral_v1.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/rm_gorbeleth_v1.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/rm_kaddrath_v1.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/rm_maddrick_v1.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/rm_mirrelbole_v1.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 D infrastructure/artpipe/pending/rm_mourvel_v1.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/artpipe/throughput.jsonl   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
 M infrastructure/dashboards/hub/data/health.json   — health publisher's rebuild artifacts — re-dirtied by every code_review_status call
 M infrastructure/state/codebase_health_last.json   — health publisher's rebuild artifacts — re-dirtied by every code_review_status call
 M src/RimMandrake/Utils/selftest_deployed_biome_refs.py   — another window's mid-edit (+33/-5 uncommitted on top of e0ca4e636; NOT this window's) — left in place
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_porg_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_porg_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_porg_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_porg_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_porg_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_porg_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_qormot_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_qormot_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_qormot_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_qormot_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_qormot_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_qormot_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_runyip_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_runyip_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_runyip_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_runyip_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_runyip_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_runyip_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_shaak_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_shaak_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_shaak_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_shaak_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_shaak_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_shaak_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_strill_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_strill_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_strill_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_strill_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_strill_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_strill_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_teemuss_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_teemuss_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_teemuss_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_teemuss_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_teemuss_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_teemuss_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_uvak_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_uvak_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_uvak_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_uvak_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_uvak_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_uvak_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_varactyl_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_varactyl_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_varactyl_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_varactyl_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_varactyl_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_varactyl_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_voorpak_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_voorpak_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_voorpak_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_voorpak_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_voorpak_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_voorpak_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_vulptex_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_vulptex_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_vulptex_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_vulptex_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_vulptex_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_vulptex_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_warwyrm_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_warwyrm_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_warwyrm_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_warwyrm_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_warwyrm_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_warwyrm_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_whisperbird_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_whisperbird_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_whisperbird_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_whisperbird_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_whisperbird_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_whisperbird_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_zeer_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_zeer_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_zeer_north.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_zeer_north.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_zeer_south.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/desertportb_zeer_south.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/rm_brakkel_v1.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/rm_brakkel_v1.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/rm_brunnock_v1.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/rm_brunnock_v1.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/rm_cundral_v1.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/rm_cundral_v1.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/rm_gorbeleth_v1.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/rm_gorbeleth_v1.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/rm_kaddrath_v1.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/rm_kaddrath_v1.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/rm_maddrick_v1.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/rm_maddrick_v1.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/rm_mirrelbole_v1.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/rm_mirrelbole_v1.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/rm_mourvel_v1.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/done/rm_mourvel_v1.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.manifest.json   — artpipe DAEMON's live churn — never commit mid-flight, its own sync handles it
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   — owner's Desktop live-test tooling backups — his to commit or cull
?? infrastructure/state/ledger/events/OWNER.jsonl   — the owner's own shard — his
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   — owner's Desktop live-test tooling backups — his to commit or cull
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   — owner's Desktop live-test tooling backups — his to commit or cull
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   — owner's Desktop live-test tooling backups — his to commit or cull
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   — owner's Desktop live-test tooling backups — his to commit or cull
```

