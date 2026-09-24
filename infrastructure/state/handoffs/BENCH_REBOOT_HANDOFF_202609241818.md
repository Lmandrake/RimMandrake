# BENCH_REBOOT_HANDOFF_202609241818 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609240404`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

**Q16 (owner, 2026-09-24, `biome_mod_architecture.md` §7): a top-level `RM_` biome mod
MAY require other mods — "free" means free of the Utinni scenario and Star Wars
entanglement, nothing else.** Two roster docs carried a false "the standalone mod
cannot depend on X" rationale within hours of that ruling and had to be corrected;
any doc or brief still arguing donor-replacement from dependency-freedom is arguing
from deleted doctrine. Donor replacement remains ruled per sitting as an IDENTITY
call. Corollary shipped the same day: the Sump leans on Vanilla Helixien Gas
Expanded, and the Utinni layer renames the gas Sumpgas.

## What the owner should see

- **Two autocorrect readings of his typed rulings are BENCH's, flagged in place,
  unconfirmed by him**: "channel or astrofuel" read as *chemfuel* or astrofuel
  (`flowworks_liquid_matrix.md`, pump section) and "rain solution" read as *weak
  solution* (`BIOME_NUISANCE_NORMALIZATION_1`). One line from him settles each.
- **The next biome sitting is his pick to confirm**: BENCH recommended the Rust
  Cathedral or Nightside Ice (thinnest rosters after the Sump); no ruling yet.
- FOUNDRY built the Sump walkways + all four nastiness mechanics offline this same
  session — deployed, validated, **live proof owed next bridge session** (item
  build-status sections list the exact checks). Nothing needs his hands there yet.

## What is half-done, and where it stops

- `BIOME_MOD_SPLIT_EXECUTION_1` — doing (BENCH); the per-biome sitting cadence IS
  this item moving. NEXT: pick/confirm the next biome sitting with the owner
  (recommendation above) and run it Sump-style.
- `SEA_FLOOR_AND_CATCH_PASS_1` — doing (BENCH); NEXT: when authoring floor+catch,
  apply the MEASURED note on the item — fishing zones refuse terrain whose
  `waterBodyType` is None, so every custom sea terrain needs it set.
- `SUMP_WALKWAYS_1` / `SUMP_TAR_NASTINESS_1` — FOUNDRY, offline-complete; NEXT:
  live-proof list in each item's build-status section, first bridge session.
- `SUMP_GASLIGHT_1` — FOUNDRY mid-flight (uncommitted `RM_Comp_WarblingGlow.cs`
  pair in the tree at wrap); NEXT: theirs — do not touch those files.
- `infrastructure/state/ledger/events/OWNER.jsonl` — untracked owner-tooling shard
  nobody has committed; NEXT: whichever seat writes it next commits it by path.

## Traps learned

- `git commit <dir>` by pathspec commits a deletion inside the dir but silently
  skips an UNTRACKED new file there — bit the `rimflow close` prose move to
  `items/closed/`, caught one close later (filed: LESSONS_INBOX).
- `block_forged_owner_said` refused a genuine multi-sentence quote typed this
  session; the guard's own prescribed exit (drop flag, own seat, name whose call)
  costs nothing and the ruling still landed verbatim in prose (filed:
  LESSONS_INBOX).
- Two backgrounded design agents share this window's git index — `index.lock`
  contention is normal during their commit windows; a 5s-sleep retry loop clears
  it, never delete the lock (see: `.claude/skills/git-efficiency`).

## Closed since the last handoff (5)

- `EVENTS_JSONL_SHARDING_1` — 2b5947555
- `WEBWORK_DESIGN_SITTING_1` — 1868e1928
- `WEBWORK_EGG_BLACKMARKET_1` — f50288aad
- `SUMP_DESIGN_SITTING_1` — d4eea8de2
- `FLOWWORKS_LIQUID_FACES_1` — 0161e37f1

## Filed and still open (24) — the next seat's queue

- `WEBWORK_FLORA_ROSTER_1` — Build the 16 invented Webwork flora defs (webwork_flora_roster doc) + Utinni tooke-trap patch (ruled kept-low); the 6 donor cuts stay PROPOSED pending
- `WEBWORK_FAUNA_ROSTER_1` — Build the 5 invented Webwork fauna defs (Quarrok/Vennick/Skennet/Cravvet/Sivvern, Sivvern flies for real) + execute the 3 ruled donor cuts; JewelBeetl
- `OLLATHRIX_OWNER_SPECIES_1` — Build RM_Ollathrix (one race one kind, owner-and-nest doc S1) with mechanisms in mandrake.rm.webwork and the Wyyyschokk skin patch in mandrake.rsw.sho
- `WEBWORK_NEST_EGG_ECONOMY_1` — Build the Webwork nest + egg economy: nest on EVERY map, re-lay 20-30d while mother lives, RM_OllathrixEgg, Wildsteam egg bounty (S6 rulings 2,3,4)
- `SHOKK_SKIN_SHRINK_1` — Shrink mandrake.rsw.shokk to the Wyyyschokk skin patch; move bound/spit/sun-scald/emergent-spawn mechanisms into mandrake.rm.webwork (S6 ruling 1, inv
- `WEBWORK_EGG_WEAPON_VERSION_1` — Future: free-form egg-planting sabotage weapon (mechanism A hatcher-variant, must re-answer the farm ban) - filed by owner card 2026-09-24, S5 ruling 
- `WEBWORK_EGG_BLACKMARKET_BUILD_1` — Build the ruled egg black market: Cartel caravan kind + Bazaar broker channel, tradeability-All patch with leak check, The Reckoning quest family with
- `WEBWORK_TERRAIN_WEATHER_PASS_1` — Design sitting: the Webwork's signature terrain (silk-carpet floor, gutters) and weather (hard sun for the light-moat, webfall/silk-drift) + soundscap
- `WEBWORK_WEB_STRUCTURES_1` — Real art + build pass for the Anchor/Web/Gutter structures (placeholder Hive texture today) and the deferred commandable-adhesive slick/locked mechani
- `WEBWORK_SOUNDSCAPE_1` — Webwork SoundDefs: the hush (ambient near-silence bed) and the web-thrum when sense-web trips - Lantern Deeps precedent, 2-4 defs, small
- `SUMP_FLORA_ROSTER_1` — Build the 10 invented Sump flora defs per sump_flora_roster_2026-09-24.md (dorvel slow-growing by ruling)
- `SUMP_FAUNA_ROSTER_1` — Build the invented Sump fauna defs per sump_fauna_roster_2026-09-24.md (incl. the ruled spike-legged flier; wrissen deleted by ruling)
- `BIOME_NUISANCE_NORMALIZATION_1` — Nuisance/solvent normalization pass over ALL biomes, run at the end of the last biome detailing (owner ticket 2026-09-24): each biome's annoying mater
- `SUMP_TAR_NASTINESS_1` — Sump nastiness mechanics: sticky tar overlay on any terrain, tarred-pawn hediffs, weak solvent craftable in-biome, tar's own reward
- `SUMP_INHABITED_NOTES_1` — Sump Inhabited injection notes (owner, 2026-09-24, for later): junkers/Jawa/deep tribes/Black Star more present; tar-expedition ruins, refinery attemp
- `SUMP_WALKWAYS_1` — Sump walkways, two tiers: duckboards (cheap, foul with tar, burn) and glasswalk (never fouls, never full speed) with cap + rare harmless pratfalls
- `SUMP_TAR_VAULT_1` — Sump tar-vault: seal food/corpses/hides into tar for perfect preservation; extraction REQUIRES solvent or contents are useless (owner-ruled)
- `SUMP_GASLIGHT_1` — Sump gaslight: tar+acid reaction makes green gas (Helixien integration OK), warbling lamp light, flame statuary, natural flames, discovery-unlocked te
- `BIOME_ARRIVAL_NARRATION_1` — Biome arrival letters: RM-tier machinery in each biome mod fires one survival-reads letter at first gravship landing; Utinni patches the narrator voic
- `INDIGENOUS_TECH_REVISIT_1` — Indigenous-tech revisit per biome, GATED to after the last biome detailing (owner 2026-09-24): which specific techs each biome unlocks on meeting its 
- `SUMP_UTINNI_LAYER_1` — Sump campaign layer: rename the gas Sumpgas, flame-statue holy act to the evil sun god (ideoligion patch), Hssiss WildAnimals_Sump patch
- `JAWA_MESS_IMMUNITY_1` — Jawa are immune from messes (owner-ruled 2026-09-24): no filth/squalor mood penalties for the Jawa xenotype; other factions just live with it and suff
- `BIOME_SHIP_CONTRIBUTIONS_1` — Every-biome pass: how does each biome uniquely improve the SHIP - what players take aboard (owner 2026-09-24); running list per sitting, normalized at
- `SUMP_TAR_HYDROLOGY_1` — Sump tar hydrology on FlowWorks: belch floods with glass fronts, full canal-work, network fire with gate firebreaks, outflow seams, the Deep Black mer

## Commits

```
06953c82c DIRTY_CODE_REVIEW_STANDING_LOOP_1: wave 53 outcome appended
73a1b0b33 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 53: 8 files marked CLEAN
50a5f7f57 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 53: remove duplicate lifeExpectancy on RSW_Jimvu
7e4dc38a2 DIRTY_CODE_REVIEW_STANDING_LOOP_1: wave 52 outcome appended
22125e2f1 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 52: 8 files marked CLEAN
9432dfc5f SUMP_TAR_NASTINESS_1: tar coating, tarred hediff, weak-solvent cure, bitumen reward
27617d01a DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 51: 8 files marked CLEAN
8b0b715b5 Fix stale row count in WildAnimals_Greentide.xml comment (23 -> 22)
b54802090 Ledger sync: FLOWWORKS_LIQUID_FACES_1 closed, matrix ruled
0161e37f1 FLOWWORKS_LIQUID_FACES_1: all 10 open rulings landed — matrix RULED 2026-09-24
35fc929aa Ledger sync: liquid matrix rulings noted onto Contagion/Rot/TerminalBiomes/Forge/FlowWorks items
d1f726ce6 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 50 outcome recorded
148261324 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 50: 7 UtinniPatches/Patches files marked CLEAN
343257902 Merge remote-tracking branch 'origin/main'
dd857a4cc DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 49 outcome recorded
5308f97d8 Add Bridge station profile
b8690768e DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 49: 10 files marked CLEAN
609daf5ad Fix missing RSW_ prefix on self/cross-referenced sound defNames (12 species)
c08876092 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 48 outcome recorded
e2fbf310f SUMP_WALKWAYS_1: duckboards + glasswalk terrain, tar-tracking, glasswalk slip comp
... 160 more: git log --oneline c77ee2e5a..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-24T15:03:39Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   the health publisher (code_review_status auto-rebuild)
 M Transient/codebase_health.json   the health publisher (code_review_status auto-rebuild)
 M Transient/codebase_health_artifact.html   the health publisher (code_review_status auto-rebuild)
 D infrastructure/artpipe/active/desertportb_feralgrazer_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/active/desertportb_feralnerf_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/active/desertportb_feralnerf_north.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_feralgrazer_south.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_feralnerf_east.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_feralnerf_north.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_feralnerf_south.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_grank_east.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_grank_north.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_grank_south.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_horax_east.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_horax_north.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_horax_south.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_kraytdragon_north.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_kraytdragon_south.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_krykna_east.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_krykna_north.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_krykna_south.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_mossbeetle_east.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_mossbeetle_north.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_mossbeetle_south.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_nerf_east.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_nerf_north.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_nerf_south.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_pikobis_east.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_pikobis_north.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_pikobis_south.manifest.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/done/desertportb_plant_bloddle.manifest.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_graniteslug_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_graniteslug_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_graniteslug_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_grank_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_grank_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_grank_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_horax_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_horax_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_horax_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_jakobeast_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_jakobeast_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_jakobeast_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_kraytdragon_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_kraytdragon_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_kraytdragon_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_krykna_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_krykna_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_krykna_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_mossbeetle_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_mossbeetle_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_mossbeetle_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_nerf_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_nerf_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_nerf_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_pikobis_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_pikobis_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_pikobis_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_plant_bloddle.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_porg_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_porg_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_porg_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_qormot_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_qormot_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_qormot_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_runyip_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_runyip_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_runyip_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_shaak_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_shaak_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_shaak_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_strill_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_strill_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_strill_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_teemuss_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_teemuss_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_teemuss_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_uvak_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_uvak_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_uvak_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_varactyl_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_varactyl_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_varactyl_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_voorpak_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_voorpak_north.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_voorpak_south.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_vulptex_east.json   the artpipe daemon (queue churn, not a seat)
 D infrastructure/artpipe/pending/desertportb_vulptex_north.json   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/registry.jsonl   the artpipe daemon (queue churn, not a seat)
 M infrastructure/artpipe/throughput.jsonl   the artpipe daemon (queue churn, not a seat)
 M infrastructure/dashboards/hub/data/health.json   the health publisher (code_review_status auto-rebuild)
 M infrastructure/state/codebase_health_last.json   the health publisher (code_review_status auto-rebuild)
 M infrastructure/state/ledger/events/FOUNDRY.jsonl   FOUNDRY window, mid-session
 M infrastructure/state/queue/BENCH.md   FOUNDRY's rimflow renders since my last ledger sync
 M infrastructure/state/queue/FOUNDRY.md   FOUNDRY's rimflow renders since my last ledger sync
?? infrastructure/artpipe/active/desertportb_voorpak_north.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/active/desertportb_voorpak_south.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/active/desertportb_vulptex_east.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/active/desertportb_vulptex_north.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_porg_east.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_porg_east.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_porg_north.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_porg_north.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_porg_south.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_porg_south.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_qormot_east.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_qormot_east.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_qormot_north.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_qormot_north.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_qormot_south.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_qormot_south.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_runyip_east.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_runyip_east.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_runyip_north.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_runyip_north.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_runyip_south.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_runyip_south.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_shaak_east.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_shaak_east.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_shaak_north.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_shaak_north.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_shaak_south.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_shaak_south.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_strill_east.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_strill_east.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_strill_north.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_strill_north.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_strill_south.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_strill_south.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_teemuss_east.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_teemuss_east.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_teemuss_north.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_teemuss_north.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_teemuss_south.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_teemuss_south.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_uvak_east.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_uvak_east.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_uvak_north.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_uvak_north.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_uvak_south.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_uvak_south.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_varactyl_east.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_varactyl_east.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_varactyl_north.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_varactyl_north.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_varactyl_south.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_varactyl_south.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_voorpak_east.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/done/desertportb_voorpak_east.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.manifest.json   the artpipe daemon (queue churn, not a seat)
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   desktop tooling backups (pre-swap/enable), not a seat
?? infrastructure/state/items/closed/FLOWWORKS_LIQUID_FACES_1.md   mine — committed at 62c7aeb50 after this scan
?? infrastructure/state/ledger/events/OWNER.jsonl   owner-attributed tooling shard, uncommitted by its writer — whoever writes it next should commit it
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   desktop tooling backups (pre-swap/enable), not a seat
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   desktop tooling backups (pre-swap/enable), not a seat
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   desktop tooling backups (pre-swap/enable), not a seat
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   desktop tooling backups (pre-swap/enable), not a seat
?? src/RimMandrake/EnvironmentalHazards/Source/RM_CompProperties_WarblingGlow.cs   FOUNDRY in-flight (SUMP_GASLIGHT_1 warbling light)
?? src/RimMandrake/EnvironmentalHazards/Source/RM_Comp_WarblingGlow.cs   FOUNDRY in-flight (SUMP_GASLIGHT_1 warbling light)
```

