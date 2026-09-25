# BENCH_REBOOT_HANDOFF_202609250325 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609242251`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**All 20 `*_RM_MOD_BUILD` biome items are FOUNDRY-claimable with ZERO open gates — do not
rediscover blockers from stale item prose.** The 7 that read PARTIAL were cleared at the
2026-09-24 sitting (each item's newest ledger notes are the authority): Slime's "merge donor
rows?" was doc rot citing a superseded §4b; Rot/Forge/Stillsand/RustCathedral/LanternDeeps/
TerminalBiomes each got their one decision. And the sitting loop itself is now a repeatable
machine: Fable draft (skeleton-first) → parent verifies every load-bearing claim → owner cards
→ apply + mechanical name gates (`check_pseudo_sw_name.py` + repo grep + Wookieepedia probe
with a positive control) → check artpipe for existing art BEFORE filing regen jobs. Fever Wood
and the Rot both went design-complete in one evening on that loop.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
Nothing pending his eye — every ruling this wave was his, live (typed or by card): Fever Wood
cast + wave-1 scope (split+F8+F9), Rot migration (thozzik/illoth/brullith/brogg), Slime
donor-free + seed pass, Forge our-own red fog, Propane two-biome design input. Heads-up only:
**71 art jobs** filed this session (53 `feverwood_*` + 18 `rot_*`) will fill `artpipe/done/`
over the coming days — a review sheet is owed when they land.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `TERMINALBIOMES_RM_MOD_BUILD_1` -- owner said YES to the Terminal-seas sitting as the next
  one; a Fable cast draft (per-sea floor+catch casts, Propane two-biome structure) was launched
  at handoff time, skeleton-first, output
  `design/Jawa/worldbuilding/biomes/terminal_seas_cast_proposal_2026-09-25.md`; NEXT: read that
  file — if complete, verify its claims and card the owner; if absent/partial, relaunch a Fable
  draft on the Rot-proposal brief pattern (see `rot_rm_cast_proposal_2026-09-24.md` provenance).
- `FEVERWOOD_RM_MOD_BUILD_1` -- design COMPLETE (cast ratified+named, wave-1 = split+F8+F9, art
  in pipe); NEXT: FOUNDRY claims and builds.
- `THEROT_RM_MOD_BUILD_1` -- design COMPLETE (migration ratified+named, RM_ allergy pair in
  scope, art in pipe); NEXT: FOUNDRY claims and builds.
- `GREENTIDE_RM_MOD_BUILD_1` -- flagged `needs game-up`: its Utinni fauna patch has never been
  verified against a load; NEXT: FOUNDRY folds the verify into its next load round.
- Fever Wood + Rot art review sheet -- NEXT: when `feverwood_*`/`rot_*` jobs land in done/,
  build the review sheet (review-sheets skill).

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `sed 's/\bname\b/new/'` misses `RM_Name` (underscore is a word char) AND the verifying
  `grep '\bname\b'` shares the same blindness — two instruments, one blind spot (filed: LESSONS_INBOX).
- A Wookieepedia `list=search` HIT is not an occurrence: "brogg" hit the Chak page whose
  wikitext contains zero "brogg" — probe the page (`action=parse`) before calling a collision
  (filed: LESSONS_INBOX).
- fandom's API 403s python-urllib's default UA; plain `curl` with a browser UA works — and the
  search instrument needs a positive control (`dewback` → 3 hits) before any zero counts (filed: LESSONS_INBOX).
- An item's blocker can cite a DOC REVISION that no longer exists: GELATINOUSSLIME's "§4b says
  merge" blocked a decision the owner had already ruled the other way in that same §4b a day
  earlier (see: the item's 2026-09-24 correction).

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (2) — the next seat's queue

- `POISONFOREST_SHIPPING_NAMES_1` — Owner card: poison_forest working names (vent stalker, dark crust)
- `SCARLANDS_SHIPPING_NAMES_1` — Owner naming: Scarlands mortuary crawler (COMMISSION_LEDGER_CLEANUP_1)

## Commits

```
248390e93 Ledger sync: COMMISSION_LEDGER_CLEANUP_1 wave 10 note + queue re-render
b431cb4a3 COMMISSION_LEDGER_CLEANUP_1 wave 10: the_cracked_lands, 4 commissions
9cb8cc265 Rot sitting ruled: migration ratified, names applied, 18 art jobs
fb6e71959 Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 88 note + queue re-render
9e6a3ae3f DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 88: mark 10 UtinniPatches/StarWarsRaces files CLEAN
af13f4632 Ledger sync: COMMISSION_LEDGER_CLEANUP_1 wave 9 note + queue re-render
9c035dc7c DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 88: fix broken StatModifier XML in RUT_Tarred_Hediffs.xml
4b94a2da6 COMMISSION_LEDGER_CLEANUP_1 wave 9: the_scald welcome-blanket flora + fall_line feral-survivor re-file
9f30170a2 Slime seed pass ruled in: 3-5 pre-slimified visitors at map gen
fa63801ef Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 87 note + queue re-render
e6ef78f49 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 87: mark 10 DesertPort/StructureInjectionsSW/StarWarsRaces files CLEAN
2096b7306 Biome build sweep: all 20 items now FOUNDRY-claimable
32a8f920c Ledger sync: GREENTIDE_MECHANICS_2 M3 Roil-spawn wave note + queue re-render
1d50f06c9 GREENTIDE_MECHANICS_2: M3's Roil-condition steam devil spawn route
26b17b0d6 Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 86 note + queue re-render
16003687a DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 86: mark 12 ResearchRetag/RustCathedralHum/ShokkweaveEconomy/UtinniPatches files CLEAN
33550ddc7 Ledger sync: COMMISSION_LEDGER_CLEANUP_1 wave 8 (the_blue_desert/the_webwork/the_pyrelands) + PYRELANDS_BURROWER_GRAZER_1 filing + queue re-render
5bf731e03 FeverWood cast art: 53 jobs filed (16 fauna x3 + 5 flora)
55dae716a Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 85 note + queue re-render
d70591c5a LESSONS_INBOX: \b rename sweeps miss RM_ defName forms
... 118 more: git log --oneline ac4828bbd..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-09-25T01:33:23Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   health publisher's auto-rebuild — FOUNDRY loop's
 M Transient/codebase_health.json   health publisher's auto-rebuild — FOUNDRY loop's
 M Transient/codebase_health_artifact.html   health publisher's auto-rebuild — FOUNDRY loop's
 D infrastructure/artpipe/active/desertportb_feralgrazer_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/active/desertportb_feralnerf_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/active/desertportb_feralnerf_north.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_feralgrazer_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_feralnerf_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_feralnerf_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_feralnerf_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_horax_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_horax_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_horax_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kraytdragon_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kraytdragon_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_krykna_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_krykna_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_krykna_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetle_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetle_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetle_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_nerf_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_nerf_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_nerf_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_pikobis_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_pikobis_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_pikobis_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_plant_bloddle.manifest.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_graniteslug_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_graniteslug_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_graniteslug_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_grank_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_grank_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_grank_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_horax_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_horax_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_horax_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_jakobeast_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_jakobeast_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_jakobeast_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kraytdragon_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kraytdragon_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kraytdragon_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_krykna_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_krykna_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_krykna_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetle_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetle_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetle_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_nerf_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_nerf_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_nerf_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_pikobis_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_pikobis_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_pikobis_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_bloddle.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_porg_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_porg_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_porg_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_qormot_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_qormot_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_qormot_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_runyip_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_runyip_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_runyip_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_shaak_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_shaak_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_shaak_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_strill_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_strill_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_strill_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_teemuss_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_teemuss_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_teemuss_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_uvak_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_uvak_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_uvak_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_varactyl_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_varactyl_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_varactyl_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_voorpak_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_voorpak_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_voorpak_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_vulptex_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_vulptex_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_vulptex_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_warwyrm_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_warwyrm_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_warwyrm_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_whisperbird_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_whisperbird_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_whisperbird_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_zeer_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_zeer_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_zeer_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_brakkel_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_brunnock_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_cundral_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_gorbeleth_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_kaddrath_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_maddrick_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_mirrelbole_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_mourvel_v1.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/registry.jsonl   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/throughput.jsonl   artpipe daemon's churn — never commit mid-flight
 M infrastructure/dashboards/hub/data/health.json   health publisher's auto-rebuild — FOUNDRY loop's
 M infrastructure/state/codebase_health_last.json   health publisher's auto-rebuild — FOUNDRY loop's
 M src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll   FOUNDRY's build outputs mid-flight — leave alone
 M src/RimUtinni/LanternDeeps/Assemblies/RimMandrake.Utinni.LanternDeeps.dll   FOUNDRY's build outputs mid-flight — leave alone
 M src/RimUtinni/UtinniPatches/Assemblies/RimMandrake.Utinni.UtinniPatches.dll   FOUNDRY's build outputs mid-flight — leave alone
?? deployed/config/ModsConfig.before-tier-firehawk.xml   FOUNDRY's tier-swap backups
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   FOUNDRY's tier-swap backups
?? infrastructure/artpipe/done/bluedesert_dovvik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brakkel_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brakkel_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brunnock_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brunnock_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_cundral_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_cundral_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_gorbeleth_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_gorbeleth_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_kaddrath_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_kaddrath_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_maddrick_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_maddrick_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mirrelbole_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mirrelbole_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mourvel_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mourvel_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_pellorax_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_pellorax_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_zhool_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_zhool_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_brekkugar_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_brekkugar_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_brekkugar_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_dhukk_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_dhukk_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_dhukk_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ghorrumak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ghorrumak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ghorrumak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_gruzz_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_gruzz_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_gruzz_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_hulggarok_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_hulggarok_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_hulggarok_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_kessik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_kessik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_kessik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_shekkur_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_shekkur_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_shekkur_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_thrizzik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_thrizzik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_thrizzik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ulkhorr_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ulkhorr_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ulkhorr_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_vrakk_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_vrakk_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_vrakk_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zekkra_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zekkra_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zekkra_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zhurrakor_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zhurrakor_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zhurrakor_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_mahllik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_mahllik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_mahllik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_zhissa_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_zhissa_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_zhissa_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_bezzul_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_bezzul_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_bezzul_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_greateroomb_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_greateroomb_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_greateroomb_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_hennul_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_hennul_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_hennul_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_mubbaro_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_mubbaro_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_mubbaro_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_oomb_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_oomb_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_oomb_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_thummorak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_thummorak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_thummorak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_vohhm_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_vohhm_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_vohhm_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuppik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuppik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuppik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuum_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuum_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuum_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_yollum_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_yollum_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_yollum_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   owner's Desktop tooling backups — his to commit or cull
?? infrastructure/state/handoffs/FOUNDRY_REBOOT_HANDOFF_202609250325.md   FOUNDRY's own handoff — its to commit
?? infrastructure/state/ledger/events/OWNER.jsonl   UNATTRIBUTED — investigate before touching
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   owner's Desktop tooling backups — his to commit or cull
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   owner's Desktop tooling backups — his to commit or cull
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   owner's Desktop tooling backups — his to commit or cull
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   owner's Desktop tooling backups — his to commit or cull
```

