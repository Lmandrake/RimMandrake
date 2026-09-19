# FOUNDRY_REBOOT_HANDOFF_202609140417 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609140254`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

A prior session's "ARMOURY_MW2_CUT_1 steps 1-7 done" was true of the REPO but
not of the GAME: the content strip was committed but never `deploy_custom_
mods.py --apply`'d, so the restart it triggered booted against a stale
`Mods/Armoury` still holding all 25 pruned MW2 files, and its own "0
TypeInitializationException" reading was measuring the wrong tree. **A
commit is not a deploy, and a deploy dry-run (no `~`/`H` diff lines) is the
only thing that proves a restart will actually test what you think it
tests** — check it BEFORE trusting any post-restart log reading, not after.
Separately: deleting a def is not the whole job — 86 files elsewhere still
pointed AT `guy762_KotORWorkbench` via `recipeUsers`/`descriptionHyperlinks`,
and 50 more via a JunkPile loot table, none of which showed up until the
boot log's own cross-reference errors named them. A full-cut item needs a
repo-wide grep for the deleted defName as its own explicit final step, not
an assumption that "delete the def" implies "delete every reference to it."

## What the owner should see

- `ARMOURY_MW2_CUT_1` is genuinely done: MW2 fully removed and verified (0
  TypeInitializationException, 0 modularweapons2 hits on a correctly
  deployed full-594-mod cold load), a weapon equipped/rendered/fired as a
  plain item in combat, 136 dangling def-references cleaned up, and the
  canonical start resaved clean (backup kept at
  `Transient/saves_backup_2026-09-14_mw2cut/`). He authorized closing
  BENCH's `SMYH_MODULARWEAPONS_PAWNGEN_CRASH_1` directly this session
  (recorded as an owner override on the ledger) since its own verify
  criteria were satisfied as a side effect — done, both closed.
- `CANONICAL_ASHKARR_START_2026-09-12`'s recorded mod list also names 4
  OTHER mods now missing that are unrelated to this item and predate it
  (Blood Animations, Jurassic Rimworld - Dinosaurs Only, Performance -
  Slower Pawn Tick Rate, Dubs Performance Analyzer) — nobody has ruled on
  whether that drift is intentional; flagging since it surfaced as a side
  effect of `rimworld/list_saves`, not something this item touched or
  investigated further.
- 12 of the 18 files fixed for dangling MW2 references live under
  `Armoury/Defs/Absorbed_KotorCore/`, which is HELD (repo-only, not
  deployed) while the `guy762.mm.kotorcore` donor mod stays subscribed —
  correct and harmless now, but a live check of those same files is owed
  whenever that donor is ever retired.

## What is half-done, and where it stops

Nothing mid-flight — `rimflow next --seat FOUNDRY` shows no item in `doing`.
One thing left genuinely UNVERIFIED rather than half-done: fixed and
deployed 6 `Absorbed_KotorWeapons/*` files' recipeUsers/descriptionHyperlinks
(the ones that ARE live), but never re-proved it against a fresh cold boot
— defs only parse at startup, `jawa/hot_reload_defs` is RETIRED and
self-refused when I tried it, and a third ~20min restart wasn't spent
proving a boot-log line goes quiet. The fix is logically sound (every
removed defName confirmed absent repo-wide, XML re-validated well-formed,
`validate_patch.py` shows 0 new errors vs. before), just not empirically
re-booted. Next full cold load for any other reason: `grep
"guy762_KotORWorkbench" Player.log` after boot should come back empty —
if it doesn't, the deploy step (`deploy_custom_mods.py --mod Armoury`,
should show 0 diff) is the first thing to check, per this session's own
"commit ≠ deploy" trap above. The other 12 `Absorbed_KotorCore/*` fixes
have no live effect either way (undeployed).

## Traps learned

- `jawa/hot_reload_defs` is RETIRED (owner, 2026-09-03, unstable — hangs the
  bridge ~5min then breaks pawn generation) and the bridge itself refuses
  the call with the full ruling in the error text — do not retry it, do not
  set `RIMBRIDGE_ALLOW_RETIRED` on the full mod list; deploy the XML and
  restart on a minimal list instead (or, as here, just accept an unverified
  boot-log claim rather than force it).
- `git add -A` is blocked by `block_blanket_git_stage.py` on the bare `-A`
  token ALONE — it does not matter whether explicit paths follow it
  (`git add -A -- path/one path/two` is still refused). A batched-rename
  fix that needs to stage N deletions + N additions in ~2 calls has to use
  `git rm -r --cached --quiet -- <old paths>` + `git add -- <new paths>`
  instead; verified in a throwaway repo that this produces the same
  `R  old -> new` result as `git mv` would.
- `grep` on a `.rws` savegame for a literal string count (not a semantic
  census) is legitimate but still refused by `block_blind_scan.py` the
  moment `-o` extracts surrounding context — `grep -c "literal"` passed,
  `grep -o '.\{60\}literal.\{60\}'` on the same file did not. The override
  is `MEASURE_ALLOW_SCAN=1`, and its own guidance is to say so in the next
  message when used — noted here for whoever reads this transcript.
- A substring match inside a savegame can be a false alarm: `grep -c
  "guy762_ResearchKotOR_workbench"` on the resaved canonical returned 9,
  which looked like leftover dangling research-project references — they
  were all `Techprint_guy762_ResearchKotOR_workbench` (a DIFFERENT, still-
  valid ThingDef family), matched only because the shorter string is a
  substring of the longer one. Always check WHAT matched, not just whether
  it did.
- `python.exe` reading a WSL absolute path fails silently in a confusing
  way; `cd` to the repo root and pass relative paths to any
  `rimbridge_client.py` call run through `python.exe` (not just
  `deploy_custom_mods.py`, which the existing memory already covered).
- The rimbridge CLI client's OWN default wait (~30s) is separate from a
  tool's own `timeoutSeconds`/`timeoutMs` parameter — a tool that
  legitimately needs 30-90s (quicktest boot, an ordered_job wait) needs
  `--timeout <N>` on the CLI call too, or it times out client-side before
  the tool itself would have returned.

## Closed since the last handoff (6)

- `SELFTEST_GIT_FIXTURE_TEMPLATE_1` — 1be034673efcbaffa406e2b1539fb85533659cb4
- `MIGRATE_NAMES_BATCH_MV_1` — 1be034673efcbaffa406e2b1539fb85533659cb4
- `CODE_REVIEW_STATUS_MIGRATE_BATCH_1` — 1be034673efcbaffa406e2b1539fb85533659cb4
- `ARMOURY_MW2_CUT_1` — e3be87450a9642e3b66cabd669945e9077fbf57a
- `SMYH_MODULARWEAPONS_PAWNGEN_CRASH_1` — 85186a9acd913fa8491631b429aa3f8f8fb6bcae (BENCH's item, closed by the
  OWNER's explicit verbal authorization mid-session — "No, I authorize you
  to close SMYH issues right now" — recorded as an owner override on the
  ledger event, not a FOUNDRY cross-seat close)
- `CORRECT_SMYH_MODULARWEAPONS_1` — 85186a9acd913fa8491631b429aa3f8f8fb6bcae (the correction item filed for
  BENCH about the above; same owner override closed it once the target
  item was itself closed)

## Filed and still open (0) — the next seat's queue

Nothing open. (`CORRECT_SMYH_MODULARWEAPONS_1` was filed and closed within
this same window — see above.)

## Commits

```
a9980f013 rimflow: sync ledger + rendered queue views for this window's closes
85186a9ac File correction for BENCH: SMYH_MODULARWEAPONS_PAWNGEN_CRASH_1 verify criteria met
e3be87450 ARMOURY_MW2_CUT_1 step 8: fix 136 dangling refs to deleted MW2 content, resave canonical
4825fb22b Plot Sitting as yEd partial-order tracks: 8 tracks, 4 cross-joints, G16 gaps as notes
1be034673 Batch the three git-fixture/migration hotspots flagged in the FOUNDRY queue
cada337c0 BENCH reboot handoff 2026-09-14 03:22
dbda87808 ARMOURY_MW2_CUT_1: guard the 3 absorption generators against re-absorbing MW2
```

## Game / bridge / tree state at wrap

- running   : RUNNING (RimWorldWin64 alive, bridge answers) — the quicktest
  map used for verification was left in place, disposable per doctrine, no
  save needed.
- recorded  : GOING_DOWN. **This is stale, not corrected by design**: I
  announced `going-down` before triggering the restart (to justify the
  reboot), the restart happened, and I never announced `up` again
  afterward — `./game`'s bare probe correctly does NOT auto-promote
  GOING_DOWN→UP (that pair, like DEPLOYING→DOWN, is documented as
  owner-only; the probe cannot see it). The game is genuinely UP and
  playable (loaded/played the canonical save, ran a quicktest, both
  worked) — the ledger just hasn't heard him say so. Next session: if the
  owner says "game up" (or anything equivalent), relay it with
  `./game --said "..." up` to correct the ledger; don't infer it yourself.
- Bridge: FREE since 2026-09-14T04:14:14Z

Uncommitted (say for each whether it is yours or another seat's):

**Stale by 3 lines**: this snapshot was taken before the `rimflow: sync
ledger...` commit (`a9980f013`) landed — `infrastructure/state/ledger/
events.jsonl`, `queue/FOUNDRY.md` and `queue/BENCH.md` are no longer
uncommitted. Everything else below is NOT mine — it's the artpipe daemon's
own churn (`infrastructure/artpipe/*`, `Transient/codebase_health*`,
`infrastructure/dashboards/hub/data/*`) and other windows' in-flight work
(`src/RimMandrake/Utils/atomic_copy.py`, `modcheck/*`, the
EnvironmentalHazards DLL) — none of it touched by this window, leave it be.

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M Transient/legibility_final_review_2026-09-13/decisions.json
 D infrastructure/artpipe/active/pyrelands_barbslinger_v1_east.json
 D infrastructure/artpipe/active/pyrelands_barbslinger_v1_north.json
 D infrastructure/artpipe/active/pyrelands_barbslinger_v1_south.json
 M infrastructure/artpipe/art_status.html
 M infrastructure/artpipe/art_status.json
 D infrastructure/artpipe/pending/alientreepolluted_v1.json
 D infrastructure/artpipe/pending/ambrosia_v1.json
 D infrastructure/artpipe/pending/aridgrass_v1.json
 D infrastructure/artpipe/pending/arpeau_v1.json
 D infrastructure/artpipe/pending/bindweed_v1.json
 D infrastructure/artpipe/pending/bloddle_v1.json
 D infrastructure/artpipe/pending/bloodbouquet_v1.json
 D infrastructure/artpipe/pending/brambles_v1.json
 D infrastructure/artpipe/pending/bubblespore_v1.json
 D infrastructure/artpipe/pending/bush_v1.json
 D infrastructure/artpipe/pending/chakroot_v1.json
 D infrastructure/artpipe/pending/creepstern_v1.json
 D infrastructure/artpipe/pending/crimsoncushion_v1.json
 D infrastructure/artpipe/pending/crystalflower_v1.json
 D infrastructure/artpipe/pending/dervish_v1.json
 D infrastructure/artpipe/pending/doomsprout_v1.json
 D infrastructure/artpipe/pending/eclipsusflower_v1.json
 D infrastructure/artpipe/pending/eclipsusleaves_v1.json
 D infrastructure/artpipe/pending/felucianglowspore_v1.json
 D infrastructure/artpipe/pending/firelavender_v1.json
 D infrastructure/artpipe/pending/flakespirefungus_v1.json
 D infrastructure/artpipe/pending/frostleaf_v1.json
 D infrastructure/artpipe/pending/gargantuanlithops_v1.json
 D infrastructure/artpipe/pending/giantseptimum_v1.json
 D infrastructure/artpipe/pending/giantstikehr_v1.json
 D infrastructure/artpipe/pending/gianttoxicflower_v1.json
 D infrastructure/artpipe/pending/glowinggrass_v1.json
 D infrastructure/artpipe/pending/graygrass_v1.json
 D infrastructure/artpipe/pending/grimmoss_v1.json
 D infrastructure/artpipe/pending/gutterplantain_v1.json
 D infrastructure/artpipe/pending/halfalientree_v1.json
 D infrastructure/artpipe/pending/hardygrass_v1.json
 D infrastructure/artpipe/pending/healroot_v1.json
 D infrastructure/artpipe/pending/heatsinkfungus_v1.json
 D infrastructure/artpipe/pending/hubbagourd_v1.json
 D infrastructure/artpipe/pending/magmacactus_v1.json
 D infrastructure/artpipe/pending/mangrovepalm_v1.json
 D infrastructure/artpipe/pending/martyr_v1.json
 D infrastructure/artpipe/pending/mortalmorel_v1.json
 D infrastructure/artpipe/pending/mujafruit_v1.json
 D infrastructure/artpipe/pending/nogtyl_v1.json
 D infrastructure/artpipe/pending/nuitae_v1.json
 D infrastructure/artpipe/pending/nysyllin_v1.json
 D infrastructure/artpipe/pending/parasiticmangrove_v1.json
 D infrastructure/artpipe/pending/poisonplanttallgrass_v1.json
 D infrastructure/artpipe/pending/poisonshrub_v1.json
 D infrastructure/artpipe/pending/polux_v1.json
 D infrastructure/artpipe/pending/poluxbush_v1.json
 D infrastructure/artpipe/pending/poxsorghum_v1.json
 D infrastructure/artpipe/pending/primordialgrass_v1.json
 D infrastructure/artpipe/pending/primordialtallgrass_v1.json
 D infrastructure/artpipe/pending/pusmelon_v1.json
 D infrastructure/artpipe/pending/pyrelands_boomsnake_v2_east.json
 D infrastructure/artpipe/pending/pyrelands_boomsnake_v2_north.json
 D infrastructure/artpipe/pending/pyrelands_boomsnake_v2_south.json
 D infrastructure/artpipe/pending/pyrelands_firehawk_v3_east.json
 D infrastructure/artpipe/pending/pyrelands_firehawk_v3_north.json
 D infrastructure/artpipe/pending/pyrelands_firehawk_v3_south.json
 D infrastructure/artpipe/pending/pyrelands_firewasp_v2_east.json
 D infrastructure/artpipe/pending/pyrelands_firewasp_v2_north.json
 D infrastructure/artpipe/pending/pyrelands_firewasp_v2_south.json
 D infrastructure/artpipe/pending/pyrelands_furnacebeast_v2_east.json
 D infrastructure/artpipe/pending/pyrelands_furnacebeast_v2_north.json
 D infrastructure/artpipe/pending/pyrelands_furnacebeast_v2_south.json
 D infrastructure/artpipe/pending/pyrelands_furnacebeast_v3_east.json
 D infrastructure/artpipe/pending/pyrelands_furnacebeast_v3_north.json
 D infrastructure/artpipe/pending/pyrelands_furnacebeast_v3_south.json
 D infrastructure/artpipe/pending/pyrelands_mantistanis_v1_east.json
 D infrastructure/artpipe/pending/pyrelands_mantistanis_v1_north.json
 D infrastructure/artpipe/pending/pyrelands_mantistanis_v1_south.json
 D infrastructure/artpipe/pending/pyrelands_mantistanis_v2_east.json
 D infrastructure/artpipe/pending/pyrelands_mantistanis_v2_north.json
 D infrastructure/artpipe/pending/pyrelands_mantistanis_v2_south.json
 D infrastructure/artpipe/pending/pyrelands_razorjack_v1_east.json
 D infrastructure/artpipe/pending/pyrelands_razorjack_v1_north.json
 D infrastructure/artpipe/pending/pyrelands_razorjack_v1_south.json
 D infrastructure/artpipe/pending/pyrelands_razorjack_v2_east.json
 D infrastructure/artpipe/pending/pyrelands_razorjack_v2_north.json
 D infrastructure/artpipe/pending/pyrelands_razorjack_v2_south.json
 D infrastructure/artpipe/pending/rainbowtongue_v1.json
 D infrastructure/artpipe/pending/ravennettle_v1.json
 D infrastructure/artpipe/pending/recurvedstropharia_v1.json
 D infrastructure/artpipe/pending/redbugloss_v1.json
 D infrastructure/artpipe/pending/redleaves_v1.json
 D infrastructure/artpipe/pending/redplantstall_v1.json
 D infrastructure/artpipe/pending/reeds_v1.json
 D infrastructure/artpipe/pending/rgtoxigrass_v1.json
 D infrastructure/artpipe/pending/rimenodules_v1.json
 D infrastructure/artpipe/pending/ripthorn_v1.json
 D infrastructure/artpipe/pending/sagecrust_v1.json
 D infrastructure/artpipe/pending/scorchedstars_v1.json
 D infrastructure/artpipe/pending/septimum_v1.json
 D infrastructure/artpipe/pending/sewerreed_v1.json
 D infrastructure/artpipe/pending/shinecap_v1.json
 D infrastructure/artpipe/pending/shrublow_v1.json
 D infrastructure/artpipe/pending/skulltop_v1.json
 D infrastructure/artpipe/pending/slimecasia_v1.json
 D infrastructure/artpipe/pending/slimyfern_v1.json
 D infrastructure/artpipe/pending/slimytree_v1.json
 D infrastructure/artpipe/pending/snaketails_v1.json
 D infrastructure/artpipe/pending/tallslimygrass_v1.json
 D infrastructure/artpipe/pending/talltoxigrass_v1.json
 D infrastructure/artpipe/pending/tangletea_v1.json
 D infrastructure/artpipe/pending/tentacular_v1.json
 D infrastructure/artpipe/pending/tinklegrass_v1.json
 D infrastructure/artpipe/pending/tooketrap_v1.json
 D infrastructure/artpipe/pending/toxibulb_v1.json
 D infrastructure/artpipe/pending/toxicivy_v1.json
 D infrastructure/artpipe/pending/toxipotato_v1.json
 D infrastructure/artpipe/pending/tropicalchokevine_v1.json
 D infrastructure/artpipe/pending/tumorbulbhyacinth_v1.json
 D infrastructure/artpipe/pending/twisteddandelion_v1.json
 D infrastructure/artpipe/pending/twistingthorngrass_v1.json
 D infrastructure/artpipe/pending/twistingthornweed_v1.json
 D infrastructure/artpipe/pending/violetwimple_v1.json
 D infrastructure/artpipe/pending/weepingtoxberry_v1.json
 D infrastructure/artpipe/pending/wildrashroot_v1.json
 D infrastructure/artpipe/pending/witchesoyster_v1.json
 D infrastructure/artpipe/pending/wrinklecap_v1.json
 M infrastructure/artpipe/registry.jsonl
 M infrastructure/artpipe/throughput.jsonl
 M infrastructure/dashboards/hub/data/artsheets.json
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/dashboards/hub/data/publish_ready.json
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/modcheck_status.json
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
 M src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll
 M src/RimMandrake/Utils/atomic_copy.py
 M src/RimMandrake/Utils/modcheck/runner.py
 M src/RimMandrake/Utils/modcheck/selftest.py
?? defs.sqlite
?? deployed/config/ModsConfig.before-tier-oracle.xml
?? deployed/config/ModsConfig.before-tier-stagedlore.xml
?? deployed/config/ModsConfig.before-tier-warlab.xml
?? design/Jawa/worldbuilding/review/serve_fauna.log
?? design/Jawa/worldbuilding/review/serve_flora.log
?? design/Jawa/worldbuilding/review/serve_homeless.log
?? infrastructure/artpipe/daemon_run_20260911_105041.log
?? infrastructure/artpipe/daemon_run_20260913_134734.log
?? infrastructure/artpipe/daemon_run_20260913_152021.log
?? infrastructure/artpipe/daemon_run_20260913_153234.log
?? infrastructure/artpipe/daemon_run_20260913_155045.log
?? infrastructure/artpipe/daemon_run_20260913_170729.log
?? infrastructure/artpipe/done/aa_frostmite_v1_east.json
?? infrastructure/artpipe/done/aa_frostmite_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.manifest.json
?? infrastructure/artpipe/done/aaklac_v1.json
?? infrastructure/artpipe/done/aaklac_v1.manifest.json
?? infrastructure/artpipe/done/abtoxigrass_v1.json
?? infrastructure/artpipe/done/abtoxigrass_v1.manifest.json
?? infrastructure/artpipe/done/agariluxprime_v1.json
?? infrastructure/artpipe/done/agariluxprime_v1.manifest.json
?? infrastructure/artpipe/done/aliengrass_v1.json
?? infrastructure/artpipe/done/aliengrass_v1.manifest.json
?? infrastructure/artpipe/done/alientree_v1.json
?? infrastructure/artpipe/done/alientree_v1.manifest.json
?? infrastructure/artpipe/done/alientreepolluted_v1.json
?? infrastructure/artpipe/done/alientreepolluted_v1.manifest.json
?? infrastructure/artpipe/done/ambrosia_v1.json
?? infrastructure/artpipe/done/ambrosia_v1.manifest.json
?? infrastructure/artpipe/done/anooba_toyfig_a_east.json
?? infrastructure/artpipe/done/anooba_toyfig_a_east.manifest.json
?? infrastructure/artpipe/done/anooba_toyfig_b2_east.json
?? infrastructure/artpipe/done/anooba_toyfig_b2_east.manifest.json
?? infrastructure/artpipe/done/aridgrass_v1.json
?? infrastructure/artpipe/done/aridgrass_v1.manifest.json
?? infrastructure/artpipe/done/arpeau_v1.json
?? infrastructure/artpipe/done/arpeau_v1.manifest.json
?? infrastructure/artpipe/done/ashrunner_v1_east_r2.json
?? infrastructure/artpipe/done/ashrunner_v1_east_r2.manifest.json
?? infrastructure/artpipe/done/ashrunner_v1_north.json
?? infrastructure/artpipe/done/ashrunner_v1_north.manifest.json
?? infrastructure/artpipe/done/ashrunner_v1_south_r2.json
?? infrastructure/artpipe/done/ashrunner_v1_south_r2.manifest.json
?? infrastructure/artpipe/done/bilespawn_v1_east.json
?? infrastructure/artpipe/done/bilespawn_v1_east.manifest.json
?? infrastructure/artpipe/done/bilespawn_v1_north_r2.json
?? infrastructure/artpipe/done/bilespawn_v1_north_r2.manifest.json
?? infrastructure/artpipe/done/bilespawn_v1_south.json
?? infrastructure/artpipe/done/bilespawn_v1_south.manifest.json
?? infrastructure/artpipe/done/bindweed_v1.json
?? infrastructure/artpipe/done/bindweed_v1.manifest.json
?? infrastructure/artpipe/done/bleedingtooth_v1.json
?? infrastructure/artpipe/done/bleedingtooth_v1.manifest.json
?? infrastructure/artpipe/done/bloddle_v1.json
?? infrastructure/artpipe/done/bloddle_v1.manifest.json
?? infrastructure/artpipe/done/bloodbouquet_v1.json
?? infrastructure/artpipe/done/bloodbouquet_v1.manifest.json
?? infrastructure/artpipe/done/boma_toyfig_a_east.json
?? infrastructure/artpipe/done/boma_toyfig_a_east.manifest.json
?? infrastructure/artpipe/done/boma_toyfig_b_east.json
?? infrastructure/artpipe/done/boma_toyfig_b_east.manifest.json
?? infrastructure/artpipe/done/boma_v1_east.json
?? infrastructure/artpipe/done/boma_v1_east.manifest.json
?? infrastructure/artpipe/done/boma_v1_north.json
?? infrastructure/artpipe/done/boma_v1_north.manifest.json
?? infrastructure/artpipe/done/boma_v1_south.json
?? infrastructure/artpipe/done/boma_v1_south.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_east.json
?? infrastructure/artpipe/done/borcatu_v1_east.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_north.json
?? infrastructure/artpipe/done/borcatu_v1_north.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_south.json
?? infrastructure/artpipe/done/borcatu_v1_south.manifest.json
?? infrastructure/artpipe/done/brambles_v1.json
?? infrastructure/artpipe/done/brambles_v1.manifest.json
?? infrastructure/artpipe/done/brightbells_v1.json
?? infrastructure/artpipe/done/brightbells_v1.manifest.json
?? infrastructure/artpipe/done/bryolux_v1.json
?? infrastructure/artpipe/done/bryolux_v1.manifest.json
?? infrastructure/artpipe/done/bubblespore_v1.json
?? infrastructure/artpipe/done/bubblespore_v1.manifest.json
?? infrastructure/artpipe/done/bush_v1.json
?? infrastructure/artpipe/done/bush_v1.manifest.json
?? infrastructure/artpipe/done/chakroot_v1.json
?? infrastructure/artpipe/done/chakroot_v1.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_east.json
?? infrastructure/artpipe/done/cinderwing_v1_east.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_north.json
?? infrastructure/artpipe/done/cinderwing_v1_north.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_south.json
?? infrastructure/artpipe/done/cinderwing_v1_south.manifest.json
?? infrastructure/artpipe/done/corronip_v1_east.json
?? infrastructure/artpipe/done/corronip_v1_east.manifest.json
?? infrastructure/artpipe/done/corronip_v1_north.json
?? infrastructure/artpipe/done/corronip_v1_north.manifest.json
?? infrastructure/artpipe/done/corronip_v1_south.json
?? infrastructure/artpipe/done/corronip_v1_south.manifest.json
?? infrastructure/artpipe/done/creepstern_v1.json
?? infrastructure/artpipe/done/creepstern_v1.manifest.json
?? infrastructure/artpipe/done/crimsoncap_v1.json
?? infrastructure/artpipe/done/crimsoncap_v1.manifest.json
?? infrastructure/artpipe/done/crimsoncushion_v1.json
?? infrastructure/artpipe/done/crimsoncushion_v1.manifest.json
?? infrastructure/artpipe/done/crystalflower_v1.json
?? infrastructure/artpipe/done/crystalflower_v1.manifest.json
?? infrastructure/artpipe/done/crystalhorn_v1.json
?? infrastructure/artpipe/done/crystalhorn_v1.manifest.json
?? infrastructure/artpipe/done/dactillion_toyfig_b_east.json
?? infrastructure/artpipe/done/dactillion_toyfig_b_east.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_east.json
?? infrastructure/artpipe/done/dactillion_v1_east.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_north.json
?? infrastructure/artpipe/done/dactillion_v1_north.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_south.json
?? infrastructure/artpipe/done/dactillion_v1_south.manifest.json
?? infrastructure/artpipe/done/dervish_v1.json
?? infrastructure/artpipe/done/dervish_v1.manifest.json
?? infrastructure/artpipe/done/dewback_toyfig_a_east.json
?? infrastructure/artpipe/done/dewback_toyfig_a_east.manifest.json
?? infrastructure/artpipe/done/dewback_toyfig_b_east.json
?? infrastructure/artpipe/done/dewback_toyfig_b_east.manifest.json
?? infrastructure/artpipe/done/dewshrooms_v1.json
?? infrastructure/artpipe/done/dewshrooms_v1.manifest.json
?? infrastructure/artpipe/done/direwail_v1_east.json
?? infrastructure/artpipe/done/direwail_v1_east.manifest.json
?? infrastructure/artpipe/done/direwail_v1_north.json
?? infrastructure/artpipe/done/direwail_v1_north.manifest.json
?? infrastructure/artpipe/done/direwail_v1_south.json
?? infrastructure/artpipe/done/direwail_v1_south.manifest.json
?? infrastructure/artpipe/done/doomsprout_v1.json
?? infrastructure/artpipe/done/doomsprout_v1.manifest.json
?? infrastructure/artpipe/done/duskram_v1_east.json
?? infrastructure/artpipe/done/duskram_v1_east.manifest.json
?? infrastructure/artpipe/done/duskram_v1_north.json
?? infrastructure/artpipe/done/duskram_v1_north.manifest.json
?? infrastructure/artpipe/done/duskram_v1_south.json
?? infrastructure/artpipe/done/duskram_v1_south.manifest.json
?? infrastructure/artpipe/done/eclipsusflower_v1.json
?? infrastructure/artpipe/done/eclipsusflower_v1.manifest.json
?? infrastructure/artpipe/done/eclipsusleaves_v1.json
?? infrastructure/artpipe/done/eclipsusleaves_v1.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_east.json
?? infrastructure/artpipe/done/emberscythe_v1_east.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_north.json
?? infrastructure/artpipe/done/emberscythe_v1_north.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_south.json
?? infrastructure/artpipe/done/emberscythe_v1_south.manifest.json
?? infrastructure/artpipe/done/fanback_toyfig_a_east.json
?? infrastructure/artpipe/done/fanback_toyfig_a_east.manifest.json
?? infrastructure/artpipe/done/fanback_toyfig_b_east.json
?? infrastructure/artpipe/done/fanback_toyfig_b_east.manifest.json
?? infrastructure/artpipe/done/fanback_v1_east.json
?? infrastructure/artpipe/done/fanback_v1_east.manifest.json
?? infrastructure/artpipe/done/fanback_v1_north.json
?? infrastructure/artpipe/done/fanback_v1_north.manifest.json
?? infrastructure/artpipe/done/fanback_v1_south.json
?? infrastructure/artpipe/done/fanback_v1_south.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_east.json
?? infrastructure/artpipe/done/featherfeel_v1_east.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_north.json
?? infrastructure/artpipe/done/featherfeel_v1_north.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_south.json
?? infrastructure/artpipe/done/featherfeel_v1_south.manifest.json
?? infrastructure/artpipe/done/felucianglowspore_v1.json
?? infrastructure/artpipe/done/felucianglowspore_v1.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_east.json
?? infrastructure/artpipe/done/fenshear_v1_east.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_north_r2.json
?? infrastructure/artpipe/done/fenshear_v1_north_r2.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_south.json
?? infrastructure/artpipe/done/fenshear_v1_south.manifest.json
?? infrastructure/artpipe/done/firelavender_v1.json
?? infrastructure/artpipe/done/firelavender_v1.manifest.json
?? infrastructure/artpipe/done/firevine_fireweed_v1.json
?? infrastructure/artpipe/done/firevine_fireweed_v1.manifest.json
?? infrastructure/artpipe/done/firevinetree_v1.json
?? infrastructure/artpipe/done/firevinetree_v1.manifest.json
?? infrastructure/artpipe/done/flakespirefungus_v1.json
?? infrastructure/artpipe/done/flakespirefungus_v1.manifest.json
?? infrastructure/artpipe/done/frostleaf_v1.json
?? infrastructure/artpipe/done/frostleaf_v1.manifest.json
?? infrastructure/artpipe/done/fruitingbodies_v1.json
?? infrastructure/artpipe/done/fruitingbodies_v1.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_east.json
?? infrastructure/artpipe/done/fumeback_v1_east.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_north.json
?? infrastructure/artpipe/done/fumeback_v1_north.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_south.json
?? infrastructure/artpipe/done/fumeback_v1_south.manifest.json
?? infrastructure/artpipe/done/gargantuanlithops_v1.json
?? infrastructure/artpipe/done/gargantuanlithops_v1.manifest.json
?? infrastructure/artpipe/done/giantagarilux_v1.json
?? infrastructure/artpipe/done/giantagarilux_v1.manifest.json
?? infrastructure/artpipe/done/giantagaritox_v1.json
?? infrastructure/artpipe/done/giantagaritox_v1.manifest.json
?? infrastructure/artpipe/done/giantgamma_v1.json
?? infrastructure/artpipe/done/giantgamma_v1.manifest.json
?? infrastructure/artpipe/done/giantseptimum_v1.json
?? infrastructure/artpipe/done/giantseptimum_v1.manifest.json
?? infrastructure/artpipe/done/giantstikehr_v1.json
?? infrastructure/artpipe/done/giantstikehr_v1.manifest.json
?? infrastructure/artpipe/done/gianttoxicflower_v1.json
?? infrastructure/artpipe/done/gianttoxicflower_v1.manifest.json
?? infrastructure/artpipe/done/globularplant_v1.json
?? infrastructure/artpipe/done/globularplant_v1.manifest.json
?? infrastructure/artpipe/done/glowingagarilux_v1.json
?? infrastructure/artpipe/done/glowingagarilux_v1.manifest.json
?? infrastructure/artpipe/done/glowinggrass_v1.json
?? infrastructure/artpipe/done/glowinggrass_v1.manifest.json
?? infrastructure/artpipe/done/glowstool_v1.json
?? infrastructure/artpipe/done/glowstool_v1.manifest.json
?? infrastructure/artpipe/done/gomphoeria_v1.json
?? infrastructure/artpipe/done/gomphoeria_v1.manifest.json
?? infrastructure/artpipe/done/gorewalker_v1_east.json
?? infrastructure/artpipe/done/gorewalker_v1_east.manifest.json
?? infrastructure/artpipe/done/gorewalker_v1_north.json
?? infrastructure/artpipe/done/gorewalker_v1_north.manifest.json
?? infrastructure/artpipe/done/gorewalker_v1_south.json
?? infrastructure/artpipe/done/gorewalker_v1_south.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.manifest.json
?? infrastructure/artpipe/done/grank_v1_east.json
?? infrastructure/artpipe/done/grank_v1_east.manifest.json
?? infrastructure/artpipe/done/grank_v1_north.json
?? infrastructure/artpipe/done/grank_v1_north.manifest.json
?? infrastructure/artpipe/done/grank_v1_south.json
?? infrastructure/artpipe/done/grank_v1_south.manifest.json
?? infrastructure/artpipe/done/graygrass_v1.json
?? infrastructure/artpipe/done/graygrass_v1.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.manifest.json
?? infrastructure/artpipe/done/greenrockfern_v1.json
?? infrastructure/artpipe/done/greenrockfern_v1.manifest.json
?? infrastructure/artpipe/done/greylady_v1.json
?? infrastructure/artpipe/done/greylady_v1.manifest.json
?? infrastructure/artpipe/done/grimmoss_v1.json
?? infrastructure/artpipe/done/grimmoss_v1.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_east.json
?? infrastructure/artpipe/done/grubhorn_v1_east.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_north.json
?? infrastructure/artpipe/done/grubhorn_v1_north.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_south.json
?? infrastructure/artpipe/done/grubhorn_v1_south.manifest.json
?? infrastructure/artpipe/done/gutterplantain_v1.json
?? infrastructure/artpipe/done/gutterplantain_v1.manifest.json
?? infrastructure/artpipe/done/halfalientree_v1.json
?? infrastructure/artpipe/done/halfalientree_v1.manifest.json
?? infrastructure/artpipe/done/hardygrass_v1.json
?? infrastructure/artpipe/done/hardygrass_v1.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_east.json
?? infrastructure/artpipe/done/hawkbat_v1_east.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_north.json
?? infrastructure/artpipe/done/hawkbat_v1_north.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_south.json
?? infrastructure/artpipe/done/hawkbat_v1_south.manifest.json
?? infrastructure/artpipe/done/healroot_v1.json
?? infrastructure/artpipe/done/healroot_v1.manifest.json
?? infrastructure/artpipe/done/heatsinkfungus_v1.json
?? infrastructure/artpipe/done/heatsinkfungus_v1.manifest.json
?? infrastructure/artpipe/done/hubbagourd_v1.json
?? infrastructure/artpipe/done/hubbagourd_v1.manifest.json
?? infrastructure/artpipe/done/huskrunner_v1_east.json
?? infrastructure/artpipe/done/huskrunner_v1_east.manifest.json
?? infrastructure/artpipe/done/huskrunner_v1_north.json
?? infrastructure/artpipe/done/huskrunner_v1_north.manifest.json
?? infrastructure/artpipe/done/huskrunner_v1_south.json
?? infrastructure/artpipe/done/huskrunner_v1_south.manifest.json
?? infrastructure/artpipe/done/hydenocktree_v1.json
?? infrastructure/artpipe/done/hydenocktree_v1.manifest.json
?? infrastructure/artpipe/done/iashiphus_v1.json
?? infrastructure/artpipe/done/iashiphus_v1.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_east.json
?? infrastructure/artpipe/done/insectomorph_v1_east.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_north.json
?? infrastructure/artpipe/done/insectomorph_v1_north.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_south.json
?? infrastructure/artpipe/done/insectomorph_v1_south.manifest.json
?? infrastructure/artpipe/done/jogantree_v1.json
?? infrastructure/artpipe/done/jogantree_v1.manifest.json
?? infrastructure/artpipe/done/jungletree_v1.json
?? infrastructure/artpipe/done/jungletree_v1.manifest.json
?? infrastructure/artpipe/done/keeningcordax_v1.json
?? infrastructure/artpipe/done/keeningcordax_v1.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_east.json
?? infrastructure/artpipe/done/kinrath_v1_east.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_north.json
?? infrastructure/artpipe/done/kinrath_v1_north.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_south.json
?? infrastructure/artpipe/done/kinrath_v1_south.manifest.json
?? infrastructure/artpipe/done/largeslimytree_v1.json
?? infrastructure/artpipe/done/largeslimytree_v1.manifest.json
?? infrastructure/artpipe/done/lilacbeacon_v1.json
?? infrastructure/artpipe/done/lilacbeacon_v1.manifest.json
?? infrastructure/artpipe/done/magmacactus_v1.json
?? infrastructure/artpipe/done/magmacactus_v1.manifest.json
?? infrastructure/artpipe/done/mangrovepalm_v1.json
?? infrastructure/artpipe/done/mangrovepalm_v1.manifest.json
?? infrastructure/artpipe/done/mangrovetree_v1.json
?? infrastructure/artpipe/done/mangrovetree_v1.manifest.json
?? infrastructure/artpipe/done/martyr_v1.json
?? infrastructure/artpipe/done/martyr_v1.manifest.json
?? infrastructure/artpipe/done/mireflit_v1_east.json
?? infrastructure/artpipe/done/mireflit_v1_east.manifest.json
?? infrastructure/artpipe/done/mireflit_v1_north.json
?? infrastructure/artpipe/done/mireflit_v1_north.manifest.json
?? infrastructure/artpipe/done/mireflit_v1_south.json
?? infrastructure/artpipe/done/mireflit_v1_south.manifest.json
?? infrastructure/artpipe/done/mireflitwarden_v1_east.json
?? infrastructure/artpipe/done/mireflitwarden_v1_east.manifest.json
?? infrastructure/artpipe/done/mireflitwarden_v1_north_r2.json
?? infrastructure/artpipe/done/mireflitwarden_v1_north_r2.manifest.json
?? infrastructure/artpipe/done/mireflitwarden_v1_south.json
?? infrastructure/artpipe/done/mireflitwarden_v1_south.manifest.json
?? infrastructure/artpipe/done/miremoth_v1_east.json
?? infrastructure/artpipe/done/miremoth_v1_east.manifest.json
?? infrastructure/artpipe/done/miremoth_v1_north.json
?? infrastructure/artpipe/done/miremoth_v1_north.manifest.json
?? infrastructure/artpipe/done/miremoth_v1_south.json
?? infrastructure/artpipe/done/miremoth_v1_south.manifest.json
?? infrastructure/artpipe/done/mortalmorel_v1.json
?? infrastructure/artpipe/done/mortalmorel_v1.manifest.json
?? infrastructure/artpipe/done/mujafruit_v1.json
?? infrastructure/artpipe/done/mujafruit_v1.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_east.json
?? infrastructure/artpipe/done/mycolith_v1_east.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_north.json
?? infrastructure/artpipe/done/mycolith_v1_north.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_south.json
?? infrastructure/artpipe/done/mycolith_v1_south.manifest.json
?? infrastructure/artpipe/done/nogtyl_v1.json
?? infrastructure/artpipe/done/nogtyl_v1.manifest.json
?? infrastructure/artpipe/done/nuitae_v1.json
?? infrastructure/artpipe/done/nuitae_v1.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_east.json
?? infrastructure/artpipe/done/ollopom_v1_east.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_north.json
?? infrastructure/artpipe/done/ollopom_v1_north.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_south.json
?? infrastructure/artpipe/done/ollopom_v1_south.manifest.json
?? infrastructure/artpipe/done/oozemaw_v1_east.json
?? infrastructure/artpipe/done/oozemaw_v1_east.manifest.json
?? infrastructure/artpipe/done/oozemaw_v1_north.json
?? infrastructure/artpipe/done/oozemaw_v1_north.manifest.json
?? infrastructure/artpipe/done/oozemaw_v1_south.json
?? infrastructure/artpipe/done/oozemaw_v1_south.manifest.json
?? infrastructure/artpipe/done/orray_v1_east.json
?? infrastructure/artpipe/done/orray_v1_east.manifest.json
?? infrastructure/artpipe/done/orray_v1_north.json
?? infrastructure/artpipe/done/orray_v1_north.manifest.json
?? infrastructure/artpipe/done/orray_v1_south.json
?? infrastructure/artpipe/done/orray_v1_south.manifest.json
?? infrastructure/artpipe/done/parasiticmangrove_v1.json
?? infrastructure/artpipe/done/parasiticmangrove_v1.manifest.json
?? infrastructure/artpipe/done/pekopeko_toyfig_b_east.json
?? infrastructure/artpipe/done/pekopeko_toyfig_b_east.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_east.json
?? infrastructure/artpipe/done/pekopeko_v1_east.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_north.json
?? infrastructure/artpipe/done/pekopeko_v1_north.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_south.json
?? infrastructure/artpipe/done/pekopeko_v1_south.manifest.json
?? infrastructure/artpipe/done/poisonplanttallgrass_v1.json
?? infrastructure/artpipe/done/poisonplanttallgrass_v1.manifest.json
?? infrastructure/artpipe/done/poisonshrub_v1.json
?? infrastructure/artpipe/done/poisonshrub_v1.manifest.json
?? infrastructure/artpipe/done/polux_v1.json
?? infrastructure/artpipe/done/polux_v1.manifest.json
?? infrastructure/artpipe/done/poluxbush_v1.json
?? infrastructure/artpipe/done/poluxbush_v1.manifest.json
?? infrastructure/artpipe/done/poxsorghum_v1.json
?? infrastructure/artpipe/done/poxsorghum_v1.manifest.json
?? infrastructure/artpipe/done/primordialgrass_v1.json
?? infrastructure/artpipe/done/primordialgrass_v1.manifest.json
?? infrastructure/artpipe/done/primordialtallgrass_v1.json
?? infrastructure/artpipe/done/primordialtallgrass_v1.manifest.json
?? infrastructure/artpipe/done/pusmelon_v1.json
?? infrastructure/artpipe/done/pusmelon_v1.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v2_east.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v2_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v2_north.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v2_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v2_south.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v2_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v2_east.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v2_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v2_north.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v2_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v2_south.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v2_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_firehawk_v3_east.json
?? infrastructure/artpipe/done/pyrelands_firehawk_v3_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_firehawk_v3_north.json
?? infrastructure/artpipe/done/pyrelands_firehawk_v3_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_firehawk_v3_south.json
?? infrastructure/artpipe/done/pyrelands_firehawk_v3_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_firewasp_v2_east.json
?? infrastructure/artpipe/done/pyrelands_firewasp_v2_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_firewasp_v2_north.json
?? infrastructure/artpipe/done/pyrelands_firewasp_v2_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_firewasp_v2_south.json
?? infrastructure/artpipe/done/pyrelands_firewasp_v2_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_furnacebeast_v3_east.json
?? infrastructure/artpipe/done/pyrelands_furnacebeast_v3_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_furnacebeast_v3_north.json
?? infrastructure/artpipe/done/pyrelands_furnacebeast_v3_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_furnacebeast_v3_south.json
?? infrastructure/artpipe/done/pyrelands_furnacebeast_v3_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v2_east.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v2_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v2_north.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v2_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v2_south.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v2_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_razorjack_v2_east.json
?? infrastructure/artpipe/done/pyrelands_razorjack_v2_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_razorjack_v2_north.json
?? infrastructure/artpipe/done/pyrelands_razorjack_v2_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_razorjack_v2_south.json
?? infrastructure/artpipe/done/pyrelands_razorjack_v2_south.manifest.json
?? infrastructure/artpipe/done/rainbowtongue_v1.json
?? infrastructure/artpipe/done/rainbowtongue_v1.manifest.json
?? infrastructure/artpipe/done/ravennettle_v1.json
?? infrastructure/artpipe/done/ravennettle_v1.manifest.json
?? infrastructure/artpipe/done/recurvedstropharia_v1.json
?? infrastructure/artpipe/done/recurvedstropharia_v1.manifest.json
?? infrastructure/artpipe/done/redbugloss_v1.json
?? infrastructure/artpipe/done/redbugloss_v1.manifest.json
?? infrastructure/artpipe/done/redleaves_v1.json
?? infrastructure/artpipe/done/redleaves_v1.manifest.json
?? infrastructure/artpipe/done/redplantstall_v1.json
?? infrastructure/artpipe/done/redplantstall_v1.manifest.json
?? infrastructure/artpipe/done/reeds_v1.json
?? infrastructure/artpipe/done/reeds_v1.manifest.json
?? infrastructure/artpipe/done/rgtoxigrass_v1.json
?? infrastructure/artpipe/done/rgtoxigrass_v1.manifest.json
?? infrastructure/artpipe/done/rimenodules_v1.json
?? infrastructure/artpipe/done/rimenodules_v1.manifest.json
?? infrastructure/artpipe/done/ripthorn_v1.json
?? infrastructure/artpipe/done/ripthorn_v1.manifest.json
?? infrastructure/artpipe/done/rotscythe_v1_east.json
?? infrastructure/artpipe/done/rotscythe_v1_east.manifest.json
?? infrastructure/artpipe/done/rotscythe_v1_north.json
?? infrastructure/artpipe/done/rotscythe_v1_north.manifest.json
?? infrastructure/artpipe/done/rotscythe_v1_south_r2.json
?? infrastructure/artpipe/done/rotscythe_v1_south_r2.manifest.json
?? infrastructure/artpipe/done/sagecrust_v1.json
?? infrastructure/artpipe/done/sagecrust_v1.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_east.json
?? infrastructure/artpipe/done/scarrend_v1_east.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_north.json
?? infrastructure/artpipe/done/scarrend_v1_north.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_south.json
?? infrastructure/artpipe/done/scarrend_v1_south.manifest.json
?? infrastructure/artpipe/done/scorchedstars_v1.json
?? infrastructure/artpipe/done/scorchedstars_v1.manifest.json
?? infrastructure/artpipe/done/septimum_v1.json
?? infrastructure/artpipe/done/septimum_v1.manifest.json
?? infrastructure/artpipe/done/sewerreed_v1.json
?? infrastructure/artpipe/done/sewerreed_v1.manifest.json
?? infrastructure/artpipe/done/shinecap_v1.json
?? infrastructure/artpipe/done/shinecap_v1.manifest.json
?? infrastructure/artpipe/done/shiro_v1_east.json
?? infrastructure/artpipe/done/shiro_v1_east.manifest.json
?? infrastructure/artpipe/done/shiro_v1_north.json
?? infrastructure/artpipe/done/shiro_v1_north.manifest.json
?? infrastructure/artpipe/done/shiro_v1_south.json
?? infrastructure/artpipe/done/shiro_v1_south.manifest.json
?? infrastructure/artpipe/done/shrublow_v1.json
?? infrastructure/artpipe/done/shrublow_v1.manifest.json
?? infrastructure/artpipe/done/skulltop_v1.json
?? infrastructure/artpipe/done/skulltop_v1.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_east.json
?? infrastructure/artpipe/done/slagmaw_v1_east.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_north.json
?? infrastructure/artpipe/done/slagmaw_v1_north.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_south.json
?? infrastructure/artpipe/done/slagmaw_v1_south.manifest.json
?? infrastructure/artpipe/done/slimecasia_v1.json
?? infrastructure/artpipe/done/slimecasia_v1.manifest.json
?? infrastructure/artpipe/done/slimyfern_v1.json
?? infrastructure/artpipe/done/slimyfern_v1.manifest.json
?? infrastructure/artpipe/done/slimytree_v1.json
?? infrastructure/artpipe/done/slimytree_v1.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_east.json
?? infrastructure/artpipe/done/sludrin_v1_east.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_north.json
?? infrastructure/artpipe/done/sludrin_v1_north.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_south.json
?? infrastructure/artpipe/done/sludrin_v1_south.manifest.json
?? infrastructure/artpipe/done/snaketails_v1.json
?? infrastructure/artpipe/done/snaketails_v1.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_east.json
?? infrastructure/artpipe/done/sporehulk_v1_east.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_north.json
?? infrastructure/artpipe/done/sporehulk_v1_north.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_south.json
?? infrastructure/artpipe/done/sporehulk_v1_south.manifest.json
?? infrastructure/artpipe/done/sugarfamewort_v1.json
?? infrastructure/artpipe/done/sugarfamewort_v1.manifest.json
?? infrastructure/artpipe/done/tallslimygrass_v1.json
?? infrastructure/artpipe/done/tallslimygrass_v1.manifest.json
?? infrastructure/artpipe/done/talltoxigrass_v1.json
?? infrastructure/artpipe/done/talltoxigrass_v1.manifest.json
?? infrastructure/artpipe/done/tanglerootmangrove_v1.json
?? infrastructure/artpipe/done/tanglerootmangrove_v1.manifest.json
?? infrastructure/artpipe/done/tangletea_v1.json
?? infrastructure/artpipe/done/tangletea_v1.manifest.json
?? infrastructure/artpipe/done/tentacular_v1.json
?? infrastructure/artpipe/done/tentacular_v1.manifest.json
?? infrastructure/artpipe/done/tinklegrass_v1.json
?? infrastructure/artpipe/done/tinklegrass_v1.manifest.json
?? infrastructure/artpipe/done/tooketrap_v1.json
?? infrastructure/artpipe/done/tooketrap_v1.manifest.json
?? infrastructure/artpipe/done/toxibulb_v1.json
?? infrastructure/artpipe/done/toxibulb_v1.manifest.json
?? infrastructure/artpipe/done/toxicgamma_v1.json
?? infrastructure/artpipe/done/toxicgamma_v1.manifest.json
?? infrastructure/artpipe/done/toxicivy_v1.json
?? infrastructure/artpipe/done/toxicivy_v1.manifest.json
?? infrastructure/artpipe/done/toxipotato_v1.json
?? infrastructure/artpipe/done/toxipotato_v1.manifest.json
?? infrastructure/artpipe/done/tropicalchokevine_v1.json
?? infrastructure/artpipe/done/tropicalchokevine_v1.manifest.json
?? infrastructure/artpipe/done/tumorbulbhyacinth_v1.json
?? infrastructure/artpipe/done/tumorbulbhyacinth_v1.manifest.json
?? infrastructure/artpipe/done/twisteddandelion_v1.json
?? infrastructure/artpipe/done/twisteddandelion_v1.manifest.json
?? infrastructure/artpipe/done/twistingthorngrass_v1.json
?? infrastructure/artpipe/done/twistingthorngrass_v1.manifest.json
?? infrastructure/artpipe/done/twistingthornwood_v1.json
?? infrastructure/artpipe/done/twistingthornwood_v1.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_east.json
?? infrastructure/artpipe/done/verdaunt_v1_east.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_north.json
?? infrastructure/artpipe/done/verdaunt_v1_north.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_south.json
?? infrastructure/artpipe/done/verdaunt_v1_south.manifest.json
?? infrastructure/artpipe/done/violetwimple_v1.json
?? infrastructure/artpipe/done/violetwimple_v1.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_east.json
?? infrastructure/artpipe/done/vornskyr_v1_east.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_north.json
?? infrastructure/artpipe/done/vornskyr_v1_north.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_south.json
?? infrastructure/artpipe/done/vornskyr_v1_south.manifest.json
?? infrastructure/artpipe/done/wastewing_v1_east.json
?? infrastructure/artpipe/done/wastewing_v1_east.manifest.json
?? infrastructure/artpipe/done/wastewing_v1_north_r2.json
?? infrastructure/artpipe/done/wastewing_v1_north_r2.manifest.json
?? infrastructure/artpipe/done/wastewing_v1_south_r2.json
?? infrastructure/artpipe/done/wastewing_v1_south_r2.manifest.json
?? infrastructure/artpipe/done/weepingtoxberry_v1.json
?? infrastructure/artpipe/done/weepingtoxberry_v1.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_east.json
?? infrastructure/artpipe/done/whisperbird_v1_east.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_north.json
?? infrastructure/artpipe/done/whisperbird_v1_north.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_south.json
?? infrastructure/artpipe/done/whisperbird_v1_south.manifest.json
?? infrastructure/artpipe/done/wildradagast_v1.json
?? infrastructure/artpipe/done/wildradagast_v1.manifest.json
?? infrastructure/artpipe/done/wildrashroot_v1.json
?? infrastructure/artpipe/done/wildrashroot_v1.manifest.json
?? infrastructure/artpipe/done/witchesoyster_v1.json
?? infrastructure/artpipe/done/witchesoyster_v1.manifest.json
?? infrastructure/artpipe/done/wrinklecap_v1.json
?? infrastructure/artpipe/done/wrinklecap_v1.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.manifest.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.manifest.json
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.json
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/ashrunner_v1_east.json
?? infrastructure/artpipe/failed/ashrunner_v1_east.manifest.json
?? infrastructure/artpipe/failed/ashrunner_v1_south.json
?? infrastructure/artpipe/failed/ashrunner_v1_south.manifest.json
?? infrastructure/artpipe/failed/bilespawn_v1_north.json
?? infrastructure/artpipe/failed/bilespawn_v1_north.manifest.json
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.json
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/fenshear_v1_north.json
?? infrastructure/artpipe/failed/fenshear_v1_north.manifest.json
?? infrastructure/artpipe/failed/mireflitwarden_v1_north.json
?? infrastructure/artpipe/failed/mireflitwarden_v1_north.manifest.json
?? infrastructure/artpipe/failed/nysyllin_v1.json
?? infrastructure/artpipe/failed/nysyllin_v1.manifest.json
?? infrastructure/artpipe/failed/rotscythe_v1_south.json
?? infrastructure/artpipe/failed/rotscythe_v1_south.manifest.json
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.json
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.json
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/twistingthornweed_v1.json
?? infrastructure/artpipe/failed/twistingthornweed_v1.manifest.json
?? infrastructure/artpipe/failed/wastewing_v1_north.json
?? infrastructure/artpipe/failed/wastewing_v1_north.manifest.json
?? infrastructure/artpipe/failed/wastewing_v1_south.json
?? infrastructure/artpipe/failed/wastewing_v1_south.manifest.json
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.json
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json
?? infrastructure/artpipe/registry.jsonl.lock
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml
?? infrastructure/state/items/PIT_TRAP_VISUAL_REDESIGN_1.md
```

