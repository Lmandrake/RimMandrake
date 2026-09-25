# BENCH_REBOOT_HANDOFF_202609250541 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609250325`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**The whole biome-mod wave shipped and load-proved in one session — but the owner's standing
instruction (typed mid-turn, recorded on `BIOME_MOD_SPLIT_EXECUTION_1`) is that SHELLS DO NOT
FINISH A BIOME.** Eight RM_ biome mods (TheRot, FeverWood, TerminalBiomes×4-seas, Greentide,
NightsideIce, Stillsand, LongShade, Wasteland) are built, deployed, load-proved (4 sweeps,
18/18 sentinels via `jawa/get_defs`) and ENABLED in the owner's full list (now 626,
`FULL.LATEST` recaptured, therot swapped for rotsporekit in place). No wave 3 of shells:
next work is per-biome beautification+robustness passes, and for the seas he ordered a whole
pass per sea INDIVIDUALLY — Scald first (his card), one completes before the next begins:
`SCALD_FLOOR_PASS_1` → `GREYSEA_FLOOR_PASS_1`/`TWILIGHTSEA_FLOOR_PASS_1`/`PROPANELAKE_FLOOR_PASS_1`.
The terminal-seas cast is fully RULED (2026-09-25 sitting, all six verdicts in
`design/Jawa/worldbuilding/biomes/terminal_seas_cast_proposal_2026-09-25.md` Status block).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- The full list is now **626 mods** with the 7 new biome mods enabled and
  **mandrake.rut.rotsporekit replaced by mandrake.rm.therot in place** — his veto point; next
  cold launch loads it (~15 min). The game left RUNNING is on the 24-mod TEST list.
- **86 art jobs** filed this session (42 terminal-seas cast + 2 barbslinger v5 correction at
  priority 40 + the backlog it joined) — review sheets owed as they land. Barbslinger south/north
  were re-filed per his 2026-09-24 verdict (claws near mouth); east is approved, wire nothing
  until he looks.
- `PROPANELAKES_SHIPPING_NAMES_1`: only the **Burner Ascendant** name still needs his word
  (V-Wake half superseded by the sitting — ships as vaunoom).
- Stillsand's live biome label still reads "the Extreme Desert" — cosmetic, flagged for its pass.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `SCALD_FLOOR_PASS_1` -- ordered FIRST (his card), not started; NEXT: run the Scald whole
  pass (terrain/features per frozen sheet, dive experience, ruled cast with real art as jobs
  land, settings wired, ends in a live review sitting with him).
- `TERMINALBIOMES_RM_MOD_BUILD_1` -- steps 1-5 done incl. cast wiring + fish retier; NEXT:
  reconciliation rows for the sea sittings — pre-existing RUT_Sallik/RUT_Fessu fish tables
  (now MayRequire-gated) vs the ruled sparse catches; coexistence is a sheet row for each
  sea's pass, not a build call.
- `FEVERWOOD_RM_MOD_BUILD_1` -- loads clean but NOT standalone (6 honest config errors: its 3
  hazard extensions bind UtinniPatches-only defs); NEXT: its robustness pass decides the
  F-mechanics packaging (move content in, or gate).
- `THEROT_RM_MOD_BUILD_1` -- built+deployed; NEXT: wire `RM_TheRotSettings` to the
  environmentalhazards gates (flagged in-code); ground-terrain art owed.
- `WASTELAND_RM_MOD_BUILD_1` -- built+deployed; NEXT: robustness pass — unguarded donor
  terrainsByFertility (pink standalone), RM_Drazz/RM_BrinePlate donor texPath,
  RM_DosimeterLawn/RM_VaultRoot texPaths resolve to no PNG, ScorchedStars Q13 divergence.
- `LONGSHADE_RM_MOD_BUILD_1` -- built+deployed; NEXT: deploy the already-rendered vorrel art
  (sitting unused in `_artsrc/` since before the move); `biome_flora.py` FAMILIES dict names
  two nonexistent defs — regenerate needs `defs.sqlite`.
- `FLOWWORKS_DONOR_AFFORDANCE_GAP_1` -- filed, unclaimed; 57 standalone crossrefs
  (BMT_DeepWaterBridgeable/TST_TerrainForMeditationStone); NEXT: FOUNDRY claims it and fixes
  inside a deliberate FlowWorks sitting (the mod is CLEAN-marked, a drive-by edit dirties it).
- 14 more `*_RM_MOD_BUILD_1` shells unbuilt (BlueDesert, Contagion, ForsakenCrags, LeaningScrub,
  Miasma, PoisonForest, RustCathedral, TheForge, TheSump, Webwork, +partials) -- deliberately
  NOT launched per the don't-rush ruling; NEXT: hold until the owner asks or the quality
  passes catch up — quality outranks shell count.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `block_forged_owner_said.py` cannot see MID-TURN owner messages, and pairs stray apostrophes
  in the note text as quote spans — record such rulings without the flag, provenance in prose,
  and write the note apostrophe-free (see: BIOME_MOD_SPLIT_EXECUTION_1's 2026-09-25 note).
- A builder agent claimed "dotnet is Windows-native, not runnable here" and shipped no DLL —
  the user-local SDK builds fine from WSL by full path (`/mnt/c/Users/Mandrake/.dotnet/dotnet.exe`);
  the toolchain memory already said so. Grade the claim, not the report (filed: LESSONS_INBOX).
- A load-log triage by top-N error buckets fixed only what it read: three sweeps each surfaced
  a tail the previous grep's `head` had cut (Teeth after FrontLeftPaw, then oovanam's paw,
  then deposits). Bucket the WHOLE distribution before fixing, or budget one more sweep than
  you think (filed: LESSONS_INBOX).
- `handoff.py --check` passes on the PREDECESSOR's filled handoff — it does not know a new
  session happened. Run bare `handoff.py` to force a fresh skeleton before filling (filed: LESSONS_INBOX).

## Closed since the last handoff (2)

- `POISONFOREST_SHIPPING_NAMES_1` — cc905a6e197fc3fa50292d649356e76824fbeeec
- `SCARLANDS_SHIPPING_NAMES_1` — cc905a6e197fc3fa50292d649356e76824fbeeec

## Filed and still open (5) — the next seat's queue

- `SCALD_FLOOR_PASS_1` — Whole individual pass for the Scald floor biome: terrain+features, dive experience, ruled cast wired with real art, catch, weather, settings, robustne
- `GREYSEA_FLOOR_PASS_1` — Whole individual pass for the Grey Sea floor biome: terrain+features, dive experience, ruled cast wired with real art, catch, weather, settings, robus
- `TWILIGHTSEA_FLOOR_PASS_1` — Whole individual pass for the Twilight Sea floor biome: terrain+features, dive experience, ruled cast wired with real art, catch, weather, settings, r
- `PROPANELAKE_FLOOR_PASS_1` — Whole individual pass for the Propane Lake floor biome: terrain+features, dive experience, ruled cast wired with real art, catch, weather, settings, r
- `FLOWWORKS_DONOR_AFFORDANCE_GAP_1` — FlowWorks liquid terrains reference donor TerrainAffordanceDefs (BMT_DeepWaterBridgeable x38, TST_TerrainForMeditationStone x19) that break standalone

## Commits

```
e7b37b531 Biome load round CLOSED: 8 mods proven, full list now 626 with therot swapped for rotsporekit
1de454556 Third load-round residue: oovanam paw group, deposit compressibility, BrinePlate graphicClass
4bcbb3fba TerminalBiomes: second load-round residue — gate Utinni fish rows, Teeth->Mouth on Snake bodies, renderPrecedence <400
c3a90013b Fix the four defects the biome load round measured live
5ddd4082b VANILLA_BEAST_EXCISION_1 wave 1: census, no vanilla left in biome-roster wiring
8b034f4e9 FALL_LINE_FERAL_SURVIVOR_PAWNKIND_1: investigate, block on unlanded sibling
3b262776c rimflow: PYRELANDS_BURROWER_GRAZER_1 needs owner, not offline
5578d4c98 rimflow: close STOCKED_POOL_BUILD_1
bf8820260 STOCKED_POOL_BUILD_1 wave 4: HARVEST, CULL, vhorrin emergence, vizhik escape
9ad86d101 COMMISSION_LEDGER_CLEANUP_1 wave 13: weeping_stones (8) all already built, other 6 groups still contended
0cff76f55 BACTA_SIDE_ITEMS_1: block, not close — bridge held by another live FOUNDRY window
788abd4cc COMMISSION_LEDGER_CLEANUP_1 wave 12: dune_sea+deep_desert, all 8 slugs resolved
4bb18c27d Ledger: GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 wave-3 note (seam stub landed, art pending)
dc8dde59c GRAFFITI_PUNK_IDEOLIGION_SCOPE_1: RM/RUT seam-test stub (criterion 4)
e8a2d8bb9 FIREHAWK_FLIGHT_BEHAVIOR_1: owner repeated the no-unattended-flight-test ruling a 3rd time
5ce286bb5 CLAUDE.md: never live-test a flyer without the owner present (said 3x)
aefaa70e9 Paint-list row for RM_Wasteland; ledger notes — wiring landed, vaunoom reconciled, shipping-names half-superseded
0e1d4c149 TerminalBiomes: build RM_Vaunoom as Q13 duplicate of campaign RUT_VWake
457cb9b47 Paint-list row for RM_LongShade; ledger build/deploy note
23c42766e WASTELAND_RM_MOD_BUILD_1: compile RimMandrake.Wasteland.dll
... 54 more: git log --oneline bc1606eb1..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : DOWN  → corrected to UP, measured now
- Bridge: FREE    since 2026-09-25T05:40:08Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   health publisher’s auto-rebuild — FOUNDRY loop’s
 M Transient/codebase_health.json   health publisher’s auto-rebuild — FOUNDRY loop’s
 M Transient/codebase_health_artifact.html   health publisher’s auto-rebuild — FOUNDRY loop’s
 D infrastructure/artpipe/_artsrc/lockjaw_improve_a_r7/lockjaw_improve_a_r7.png   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/_artsrc/lockjaw_improve_b_r7/lockjaw_improve_b_r7.png   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/active/desertportb_feralgrazer_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/active/desertportb_feralnerf_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/active/desertportb_feralnerf_north.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_feralgrazer_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_feralnerf_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_feralnerf_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_feralnerf_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_horax_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_horax_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_horax_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kraytdragon_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kraytdragon_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_krykna_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_krykna_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_krykna_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetle_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetle_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetle_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_nerf_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_nerf_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_nerf_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_pikobis_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_pikobis_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_pikobis_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_plant_bloddle.manifest.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_graniteslug_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_graniteslug_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_graniteslug_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_grank_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_grank_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_grank_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_horax_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_horax_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_horax_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_jakobeast_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_jakobeast_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_jakobeast_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kraytdragon_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kraytdragon_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kraytdragon_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_krykna_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_krykna_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_krykna_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetle_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetle_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetle_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_nerf_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_nerf_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_nerf_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_pikobis_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_pikobis_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_pikobis_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_bloddle.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_porg_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_porg_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_porg_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_qormot_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_qormot_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_qormot_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_runyip_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_runyip_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_runyip_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_shaak_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_shaak_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_shaak_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_strill_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_strill_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_strill_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_teemuss_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_teemuss_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_teemuss_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_uvak_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_uvak_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_uvak_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_varactyl_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_varactyl_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_varactyl_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_voorpak_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_voorpak_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_voorpak_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_vulptex_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_vulptex_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_vulptex_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_warwyrm_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_warwyrm_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_warwyrm_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_whisperbird_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_whisperbird_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_whisperbird_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_zeer_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_zeer_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_zeer_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_brakkel_v1.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_brunnock_v1.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_cundral_v1.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_gorbeleth_v1.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_kaddrath_v1.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_maddrick_v1.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_mirrelbole_v1.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_mourvel_v1.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rut_wildhealroot.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutbloomcrop_v1.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutdarkcrust_v1.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutdeltaloam_v1.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutemperorvulture_v1_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutemperorvulture_v1_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutemperorvulture_v1_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutfleetflier_v1_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutfleetflier_v1_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutfleetflier_v1_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutfuzz_v1.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutglower_v1.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutglowercrust_v1.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutkarrathil_v1_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutkarrobel_v1_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutmortuarycrawler_v1_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutmortuarycrawler_v1_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutmortuarycrawler_v1_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutsealedsleeper_v1_east.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutsealedsleeper_v1_north.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutsealedsleeper_v1_south.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutstaggerseed_v1.json   artpipe daemon’s churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutstaggerseeddish_v1.json   artpipe daemon’s churn — never commit mid-flight
 M infrastructure/dashboards/hub/data/health.json   health publisher’s auto-rebuild — FOUNDRY loop’s
 M infrastructure/state/codebase_health_last.json   health publisher’s auto-rebuild — FOUNDRY loop’s
 M infrastructure/state/queue/BENCH.md   not mine — investigate before touching
 M src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll   FOUNDRY’s build outputs / tier backups — leave alone
 M src/RimMandrake/Utils/modset_builder.py   not mine — investigate before touching
 M src/RimUtinni/LanternDeeps/Assemblies/RimMandrake.Utinni.LanternDeeps.dll   FOUNDRY’s build outputs / tier backups — leave alone
D  src/RimUtinni/UtinniPatches/Patches/RotSpecies_NamesAndSizes.xml   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/AgaricusDomeCap.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Agarilux/Agarilux_A.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/AgariluxPrime.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Agaripawn/Agaripawn_east.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Agaripawn/Agaripawn_north.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Agaripawn/Agaripawn_south.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/ArbuscularMycorrhiza/ArbuscularMycorrhiza_A.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Bryolux/Bryolux_A.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/DribblingCap/DribblingCap_A.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/GiantAgarilux/GiantAgarilux_A.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/GlowingAgarilux/GlowingAgarilux_A.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Glowstool/Glowstool_A.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/LilacBeacon/LilacBeacon_A.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/MycoidColossus/MycoidColossus_east.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/MycoidColossus/MycoidColossus_north.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/MycoidColossus/MycoidColossus_south.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/RecurvedStropharia.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/SlimyPholiota/SlimyPholiota_A.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Swarmling/Swarmling_east.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Swarmling/Swarmling_north.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Swarmling/Swarmling_south.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpawn/Wildpawn_east.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpawn/Wildpawn_north.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpawn/Wildpawn_south.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpod/Wildpod_east.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpod/Wildpod_north.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpod/Wildpod_south.png   not mine — investigate before touching
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/WitchesOyster.png   not mine — investigate before touching
?? deployed/config/ModsConfig.before-tier-firehawk.xml   FOUNDRY’s build outputs / tier backups — leave alone
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   FOUNDRY’s build outputs / tier backups — leave alone
?? infrastructure/artpipe/done/bluedesert_dovvik_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brakkel_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brakkel_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brunnock_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brunnock_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_cundral_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_cundral_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_gorbeleth_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_gorbeleth_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_kaddrath_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_kaddrath_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_maddrick_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_maddrick_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mirrelbole_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mirrelbole_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mourvel_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mourvel_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_wildhealroot.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_wildhealroot.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutbloomcrop_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutbloomcrop_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdarkcrust_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdarkcrust_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdeltaloam_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdeltaloam_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutfuzz_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutfuzz_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutglower_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutglower_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutglowercrust_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutglowercrust_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutstaggerseed_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutstaggerseed_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutvaultroot_v1.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/done/rutvaultroot_v1.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_pellorax_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_pellorax_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_zhool_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_zhool_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutkarrathil_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutkarrathil_v1_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutkarrobel_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutkarrobel_v1_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_east.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_north.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_south.manifest.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_brekkugar_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_brekkugar_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_brekkugar_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_dhukk_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_dhukk_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_dhukk_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ghorrumak_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ghorrumak_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ghorrumak_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_gruzz_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_gruzz_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_gruzz_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_hulggarok_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_hulggarok_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_hulggarok_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_kessik_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_kessik_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_kessik_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_shekkur_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_shekkur_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_shekkur_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_thrizzik_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_thrizzik_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_thrizzik_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ulkhorr_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ulkhorr_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ulkhorr_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_vrakk_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_vrakk_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_vrakk_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zekkra_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zekkra_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zekkra_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zhurrakor_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zhurrakor_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zhurrakor_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_essarn_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_essarn_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_essarn_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_fessk_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_fessk_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_fessk_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_otheska_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_otheska_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_otheska_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_sorruth_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_sorruth_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_sorruth_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_mahllik_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_mahllik_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_mahllik_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_zhissa_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_zhissa_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_zhissa_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_heemin_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_heemin_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_heemin_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_noohm_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_noohm_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_noohm_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_shulla_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_shulla_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_shulla_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_bezzul_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_bezzul_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_bezzul_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_greateroomb_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_greateroomb_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_greateroomb_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_hennul_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_hennul_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_hennul_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_mubbaro_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_mubbaro_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_mubbaro_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_oomb_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_oomb_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_oomb_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_thummorak_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_thummorak_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_thummorak_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_vohhm_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_vohhm_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_vohhm_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuppik_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuppik_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuppik_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuum_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuum_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuum_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_yollum_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_yollum_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_yollum_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_east.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_north.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_south.json   artpipe daemon’s churn — never commit mid-flight
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   owner’s Desktop tooling backups — his to commit or cull
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   owner’s Desktop tooling backups — his to commit or cull
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   owner’s Desktop tooling backups — his to commit or cull
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   owner’s Desktop tooling backups — his to commit or cull
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   owner’s Desktop tooling backups — his to commit or cull
?? src/RimMandrake/Utils/firehawk_flight_probe.py   not mine — investigate before touching
?? src/RimUtinni/PropaneLakeMechanics/   not mine — investigate before touching
```

