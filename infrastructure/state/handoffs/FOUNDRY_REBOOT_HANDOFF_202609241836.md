# FOUNDRY_REBOOT_HANDOFF_202609241836 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609241247`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

`code_review_status.py list` (bare) silently omits every never-entered file — only
`--show-untracked` shows the true pool. This was already a filed lesson
(`LESSONS_INBOX.md`, 2026-09-13) but the standing loop's own protocol never adopted
it, so 43 waves reported "0 DIRTY" milestones while 346 files sat invisible before
wave 44 rediscovered it the hard way. **Fixed in place this session**: the item's own
`## the loop` header now says `--show-untracked` explicitly (commit `b3f9729fb`) so
this can't be missed again. General lesson: a filed lesson that never made it into
the thing that actually enforces it is not learned, it's just recorded.

## What the owner should see

- **8 build items are staged and waiting on a restart+shutdown-window to prove live**:
  `BACTA_TANK_CORE_1`, `BACTA_REVIVAL_MECHANIC_1`, `BACTA_SIDE_ITEMS_1`,
  `JAWA_MESS_IMMUNITY_1`, `FEVERWOOD_BOUGH_SOIL_TERRAIN_1`, `SUMP_WALKWAYS_1`,
  `SUMP_TAR_NASTINESS_1`, `SUMP_GASLIGHT_1` — all offline-validated and deployed
  (XML side), all needing an assembly redeploy at the next game-down window before
  any of their new C# is live. This is a genuinely large batch riding one restart;
  worth doing deliberately rather than piecemeal.
- **A real, serious bridge bug was found and cost 4 pawn deaths this session** (3
  colonists + 1 pet, during `BACTA_TANK_CORE_1` live testing): `jawa/pawn_health`
  adding `WoundInfection` at severity 1.0 kills the pawn synchronously, reports
  `success:true`, no warning. **Nothing was saved** — `save_game` was never called,
  so the canonical save is untouched — but this is a standing trap for the next
  bridge session testing anything infection-related. Filed to
  `skills/rimbridge/references/silent-failures.md`.
- Bacta Tank's remaining live-verify bar (missing-organ, brain, infection-assist,
  scar erasure) was deliberately NOT pushed further this session because of that
  trap — I asked whether to continue and got no answer before the session wrapped.
  Whoever picks it up next should read `BACTA_TANK_CORE_1.md`'s live-test section
  before touching infection mechanics via the bridge.
- The code-review loop (waves 1-54 this session) found and fixed ~25 real bugs,
  several systemic (12 creatures with silently broken combat/death sounds from a
  missing SoundDef prefix; 6 files with a misspelled `MayRequire="...Odysse"`
  gating an eating restriction that never applied). None are ship-blocking on
  their own but the pattern (a whole class of def silently misconfigured) is worth
  knowing about if similar reports come up in play.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `BACTA_REVIVAL_MECHANIC_1` — offline-complete, DLL deploy blocked by running game; NEXT: redeploy at next game-down window, then live-test corpse-carry + revival per the item's own checklist (avoid `jawa/pawn_health`+`WoundInfection`, see traps).
- `BACTA_SIDE_ITEMS_1` — offline-complete, DLL deploy blocked by running game; NEXT: redeploy at next game-down window, then live-test the medical-droid facility link, patch/spray consumables, and trader stock per the item's checklist.
- `BACTA_TANK_CORE_1` — wound-heal mechanism live-proven this session, 4 remaining checks (organ/brain/infection-assist/scar) NOT attempted after the pawn-death trap was found; NEXT: re-test those 4 checks live, using a plain damage kill or `jawa/damage` (NOT `jawa/pawn_health`+`WoundInfection`) to set up test wounds.
- `FEVERWOOD_BOUGH_SOIL_TERRAIN_1` — offline-complete, deployed (XML-only, no DLL block); NEXT: live quicktest that bough-soil paints correctly near boughway anchors without overwriting pool/lane cells, and that a plant actually roots on it.
- `JAWA_MESS_IMMUNITY_1` — offline-complete, deployed (XML-only, no DLL block); NEXT: live quicktest a Jawa and non-Jawa pawn in the same filthy room — confirm `NeedBeauty` absent for the Jawa, present/negative for the other, and no pawn anywhere gains positive mood from mess.
- `SUMP_GASLIGHT_1` — pieces 1-4 (reaction/light/lamp/statue) offline-complete, DLL deploy BLOCKED by running game (new C# classes not live yet); pieces 5-7 (natural flames/discovery/ship-buildable) deliberately deferred, not stubbed where unverified; NEXT: redeploy DLL at next game-down window, then live-test per the item's checklist (scrubbing spawns Sumpgas, lamp visibly warbles, statue flame scales with quality, both research gates work).
- `SUMP_TAR_NASTINESS_1` — all 4 pieces offline-complete, deployed; NEXT: live quicktest the hediff is given/staged correctly, `RUT_ScrubTarred` appears and cures on the health tab, the bench recipe appears once seepwax is spawned, and the two new BiomeDef ModExtensions resolve at load.
- `SUMP_WALKWAYS_1` — offline-complete, deployed; NEXT: live quicktest tar tracks onto and slows duckboards, glasswalk reads ~80% speed and never fouls, the slip-and-fall comp fires rarely and harmlessly.

## Traps learned

- `jawa/pawn_health` adding `WoundInfection` at severity 1.0 kills the pawn synchronously, `success:true`, no warning — cost 4 pawn deaths isolating it this session, nothing saved (see: `skills/rimbridge/references/silent-failures.md`).
- `rimworld/start_debug_game_ready` on the owner's full ~620-mod list crashed the whole process (Vehicle Framework NRE in `Game.Dispose()`) — confirmed reproducible, matches existing doctrine to use a minimal/target tier for quicktest work instead of the full list (see: `rimworld-debug-testing` skill, memory `quicktest-crashes-full-modlist-use-cheap-mechanism-list`).
- Right after a fresh RimWorld launch, `Player.log` can briefly still hold the PREVIOUS session's full content (including a stale `"Bridge token:"` line) before the new process truncates and starts writing — a naive `grep` for the ready signal gives an instant false positive. Check the log's mtime is genuinely fresh (seconds old, not the old session) before trusting a match (filed: LESSONS_INBOX 2026-09-24).
- `code_review_status.py list` (bare) omits never-entered files; only `--show-untracked` shows them — was already filed (LESSONS_INBOX 2026-09-13) but never adopted by the standing loop's own protocol until this session (see: `DIRTY_CODE_REVIEW_STANDING_LOOP_1.md`'s `## the loop` header, fixed commit `b3f9729fb`).
- Subagents given ANY backgrounded command (not just bridge cold-loads) will sometimes end their own turn "to wait for the result" and park permanently, since only the parent session receives background-task notifications — recurred 6+ times this session, each needing an explicit parent correction (filed: LESSONS_INBOX 2026-09-24, proposed home `efficient-subagents`).

## Closed since the last handoff (2)

- `KORRUM_ART_REGEN_1` — 124ac564e0aaaec263b5ba68bdbc3d3364544f8e
- `SETTLEMENT_VISIT_LOOP_1` — 124ac564e0aaaec263b5ba68bdbc3d3364544f8e

## Filed and still open (13) — the next seat's queue

- `WEBWORK_WEB_STRUCTURES_1` — Real art + build pass for the Anchor/Web/Gutter structures (placeholder Hive texture today) and the deferred commandable-adhesive slick/locked mechani
- `WEBWORK_SOUNDSCAPE_1` — Webwork SoundDefs: the hush (ambient near-silence bed) and the web-thrum when sense-web trips - Lantern Deeps precedent, 2-4 defs, small
- `SUMP_TAR_BELCH_EVENT_1` — Sump tar-belch incident: a tar pit occasionally erupts, coating local terrain in tar (owner-ruled 2026-09-24)
- `SUMP_FLORA_ROSTER_1` — Build the 10 invented Sump flora defs per sump_flora_roster_2026-09-24.md (dorvel slow-growing by ruling)
- `SUMP_FAUNA_ROSTER_1` — Build the invented Sump fauna defs per sump_fauna_roster_2026-09-24.md (incl. the ruled spike-legged flier; wrissen deleted by ruling)
- `SUMP_TAR_NASTINESS_1` — Sump nastiness mechanics: sticky tar overlay on any terrain, tarred-pawn hediffs, weak solvent craftable in-biome, tar's own reward
- `SUMP_WALKWAYS_1` — Sump walkways, two tiers: duckboards (cheap, foul with tar, burn) and glasswalk (never fouls, never full speed) with cap + rare harmless pratfalls
- `SUMP_TAR_VAULT_1` — Sump tar-vault: seal food/corpses/hides into tar for perfect preservation; extraction REQUIRES solvent or contents are useless (owner-ruled)
- `SUMP_GASLIGHT_1` — Sump gaslight: tar+acid reaction makes green gas (Helixien integration OK), warbling lamp light, flame statuary, natural flames, discovery-unlocked te
- `BIOME_ARRIVAL_NARRATION_1` — Biome arrival letters: RM-tier machinery in each biome mod fires one survival-reads letter at first gravship landing; Utinni patches the narrator voic
- `SUMP_UTINNI_LAYER_1` — Sump campaign layer: rename the gas Sumpgas, flame-statue holy act to the evil sun god (ideoligion patch), Hssiss WildAnimals_Sump patch
- `JAWA_MESS_IMMUNITY_1` — Jawa are immune from messes (owner-ruled 2026-09-24): no filth/squalor mood penalties for the Jawa xenotype; other factions just live with it and suff
- `SUMP_TAR_HYDROLOGY_1` — Sump tar hydrology on FlowWorks: belch floods with glass fronts, full canal-work, network fire with gate firebreaks, outflow seams, the Deep Black mer

## Commits

```
8fb118681 Ledger sync: SUMP_GASLIGHT_1 note (pieces 1-4 built, DLL deploy pending shutdown)
53687b094 SUMP_GASLIGHT_1: tar+acid->Sumpgas reaction, warbling glow comp, gaslight lamp, flame statuary
dbf522d71 WEEPING_STONES_DESIGN_SITTING_1 filed: Weeping Stones is the next full-mod biome
87f37ba26 DIRTY_CODE_REVIEW_STANDING_LOOP_1: wave 54 outcome appended
487168757 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 54: 8 files marked CLEAN
f07f3a1fb Handoff: cite the index.lock trap's durable home
c8b02d637 BENCH handoff 202609241818: Sump sitting + liquid matrix wave wrapped
0c0282d70 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 54: fix RSW_LavaFlea Odyssey/Biotech MayRequire mismatch
62c7aeb50 FLOWWORKS_LIQUID_FACES_1 prose to items/closed (missed by pathspec commit on close)
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
... 142 more: git log --oneline a2fc0005a..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-24T15:03:39Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   ambient, health-publisher regen output, nobody's edit
 M Transient/codebase_health.json   ambient, health-publisher regen output, nobody's edit
 M Transient/codebase_health_artifact.html   ambient, health-publisher regen output, nobody's edit
 D infrastructure/artpipe/active/desertportb_feralgrazer_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/active/desertportb_feralnerf_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/active/desertportb_feralnerf_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_feralgrazer_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_feralnerf_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_feralnerf_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_feralnerf_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_grank_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_grank_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_grank_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_horax_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_horax_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_horax_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_kraytdragon_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_kraytdragon_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_krykna_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_krykna_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_krykna_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_mossbeetle_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_mossbeetle_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_mossbeetle_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_nerf_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_nerf_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_nerf_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_pikobis_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_pikobis_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_pikobis_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/done/desertportb_plant_bloddle.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_graniteslug_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_graniteslug_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_graniteslug_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_grank_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_grank_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_grank_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_horax_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_horax_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_horax_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_jakobeast_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_jakobeast_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_jakobeast_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_kraytdragon_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_kraytdragon_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_kraytdragon_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_krykna_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_krykna_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_krykna_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_mossbeetle_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_mossbeetle_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_mossbeetle_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_nerf_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_nerf_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_nerf_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_pikobis_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_pikobis_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_pikobis_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_plant_bloddle.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_porg_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_porg_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_porg_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_qormot_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_qormot_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_qormot_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_runyip_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_runyip_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_runyip_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_shaak_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_shaak_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_shaak_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_strill_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_strill_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_strill_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_teemuss_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_teemuss_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_teemuss_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_uvak_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_uvak_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_uvak_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_varactyl_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_varactyl_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_varactyl_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_voorpak_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_voorpak_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_voorpak_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_vulptex_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_vulptex_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_vulptex_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_warwyrm_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_warwyrm_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_warwyrm_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_whisperbird_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_whisperbird_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_whisperbird_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_zeer_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_zeer_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/desertportb_zeer_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/rm_brakkel_v1.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/rm_brunnock_v1.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/rm_cundral_v1.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/rm_gorbeleth_v1.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/rm_kaddrath_v1.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/rm_maddrick_v1.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/rm_mirrelbole_v1.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 D infrastructure/artpipe/pending/rm_mourvel_v1.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/registry.jsonl   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/artpipe/throughput.jsonl   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
 M infrastructure/dashboards/hub/data/health.json   ambient, health-publisher regen output, nobody's edit
 M infrastructure/state/codebase_health_last.json   ambient, health-publisher regen output, nobody's edit
?? design/Jawa/worldbuilding/biomes/weeping_stones_fauna_roster_2026-09-24.md   BENCH's WEEPING_STONES_DESIGN_SITTING_1, not mine
?? design/Jawa/worldbuilding/biomes/weeping_stones_flora_roster_2026-09-24.md   BENCH's WEEPING_STONES_DESIGN_SITTING_1, not mine
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_porg_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_porg_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_porg_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_porg_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_porg_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_porg_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_qormot_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_qormot_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_qormot_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_qormot_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_qormot_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_qormot_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_runyip_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_runyip_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_runyip_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_runyip_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_runyip_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_runyip_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_shaak_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_shaak_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_shaak_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_shaak_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_shaak_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_shaak_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_strill_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_strill_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_strill_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_strill_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_strill_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_strill_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_teemuss_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_teemuss_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_teemuss_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_teemuss_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_teemuss_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_teemuss_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_uvak_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_uvak_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_uvak_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_uvak_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_uvak_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_uvak_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_varactyl_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_varactyl_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_varactyl_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_varactyl_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_varactyl_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_varactyl_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_voorpak_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_voorpak_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_voorpak_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_voorpak_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_voorpak_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_voorpak_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_vulptex_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_vulptex_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_vulptex_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_vulptex_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_vulptex_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_vulptex_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_warwyrm_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_warwyrm_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_warwyrm_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_warwyrm_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_warwyrm_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_warwyrm_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_whisperbird_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_whisperbird_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_whisperbird_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_whisperbird_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_whisperbird_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_whisperbird_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_zeer_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_zeer_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_zeer_north.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_zeer_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_zeer_south.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/desertportb_zeer_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/rm_brakkel_v1.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/rm_brakkel_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/rm_brunnock_v1.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/rm_brunnock_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/rm_cundral_v1.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/rm_cundral_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/rm_gorbeleth_v1.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/rm_gorbeleth_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/rm_kaddrath_v1.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/rm_kaddrath_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/rm_maddrick_v1.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/rm_maddrick_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/rm_mirrelbole_v1.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/rm_mirrelbole_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/rm_mourvel_v1.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/done/rm_mourvel_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining/reharvesting the requeued desertportb/rm_* batch from earlier this session
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing (2026-09-11), not this window
?? infrastructure/state/ledger/events/OWNER.jsonl   new ledger shard, likely owner-side game-state events, not mine to touch
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   pre-existing, not this window
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   pre-existing, not this window
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   mine -- backup taken before this session's bacta-tier ModsConfig swap
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   pre-existing, not this window
```

