# FOUNDRY_REBOOT_HANDOFF_202609240213 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609212035`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

This repo currently has UNUSUALLY heavy concurrent LOCAL git activity — not just
remote pushes, but another live session (BENCH/Fable, `SEA_FLOOR_AND_CATCH_PASS_1`)
committing directly to this same local `main` while a `git pull --rebase
--autostash` was in flight. That produced a NEW failure mode beyond the documented
health-publisher trap: `git rebase --continue` refusing with `update_ref failed...
is at X but expected Y` because another local process advanced `main` mid-rebase.
Fix: `git rebase --abort` (safe, your own commits survive via reflog/todo), then
`git cat-file -t <the-commit-that-blocked-you>` to confirm it's a real, well-formed
commit (not corruption), then `git merge-base --is-ancestor HEAD <sha> &&
git merge --ff-only <sha>` to restore it losslessly, then re-run
`pull --rebase --autostash`. Expect to repeat the whole cycle 3-5+ times in one
sitting when both BENCH and FOUNDRY are actively committing simultaneously — this
is normal right now, not a sign something is broken. The health-publisher conflict
itself is *always* safe to resolve with `checkout --theirs` (purely derived,
regenerable); real content conflicts (events.jsonl, queue/*.md) need the
hash-object/update-index/checkout-index union method, never a blind `--ours`/
`--theirs` on those.

## What the owner should see

- **`UTINNI_WORLDMAP_FLIGHT_ICON_1`: the custom gravship world-map icon is NOT
  actually rendering live** — still vanilla's dome glyph, on a real authorized
  flight test, despite deploy checks passing clean across multiple prior
  sessions. A real regression that's been silently shipping; needs a fresh look
  at the patch/texPath, not another deploy re-check.
- **`RUST_CATHEDRAL_MECHANICS_1`: wall-tier content confirmed genuinely absent**
  even on a real player-founded map, resolving the earlier "test artifact vs
  real gap" ambiguity — it's a real gap.
- **`STARWARS_DONOR_PORT_LABEL_COLLISIONS_1` (new item, filed this session):**
  the new `label_collision_check.py` guard found 62 label collisions between
  donor Star-Wars-animal-collection defNames and our RSW_ ports (beyond the 4
  already fixed in `DUPLICATE_CANON_DEFNAME_PAIRS_1`). Most are a different
  shape — donor content cast into biomes we don't own — and need a design call,
  not a mechanical FOUNDRY fix.
- **Art pipeline: I raised the daemon's self-imposed Codex ceiling** (weekly
  90%→99%, 5h 90%→98%) on your word that this is the last reset before a plan
  change and you wanted it spent, not held back. This is a standing code change
  in `artpiped.py`, not a one-session flag — it persists until someone
  deliberately lowers it again.
- A real bridge-tooling gap was found: `jawa/pawn_use_verb` cannot see or fire
  any `CompTurretGun`-owned verb (separate verb tracker from `pawn.VerbTracker`)
  — relevant to testing any future turret-gun creature (Rust Cathedral/Forge/
  Scald kits may have more).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `COLD_LOAD_RUN_SHEET_4` — doing, 3 sub-items closed this session (MANYWATERS_COLOR_SUPPORT_1, NINEFOLD_MISSING_EVENT_HOOKS_1, TILEGEN_SILENT_REUSE_1), real partial progress on 5 more; NEXT: take the bridge and finish MIASMA_MECHANICS_1's M1/M2/M3/M5/M6 (single-biome session, not 3-concurrent-map — that timed out), or MODCHECK_DONOR_ENVIRONMENTS_1's min16+candidates bisection.
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` — doing, self-continuing, 2 waves this session (18+9 files marked CLEAN, 3 real bugs fixed and committed); NEXT: `code_review_status.py list`, pick a reachable un-reviewed file, full-file review it.
- `CANON_CREATURE_REGEN_1` — doing, wave 4 queued (21 jobs, 7 creatures x3 facings) into the art daemon; NEXT: check `infrastructure/artpipe/done/canon_{boma,dewback,insectomorph,shiro,vornskyr,whisperbird,zakkeg}_v1_*.json` (5/21 landed as of this handoff, blocked on the real Codex 5h rate ceiling — was 96-99% at 19:13 PDT, check `codex_grumpiness.read_meters()` before assuming it's cleared) — once the queue drains, run `Transient/canon_regen_wave4_2026-09-23/build_composites.py`, build the review sheet, commit.
- `CUT_FALLOUT_GENERATED_DATA_1` — doing, FOUNDRY's own scope is finished (animal tolerances regenerated+deployed+live-confirmed, cast_assignment.csv clean); NEXT: nothing FOUNDRY-side — remaining blocker (`biome_flora.py --write`) is externally gated on `BIOME_MOD_SPLIT_EXECUTION_1`/`TERMINALBIOMES_RM_MOD_BUILD_1`/etc. landing, not ours to force.
- `WYYYSCHOKK_FANG_PENDANT_1` — doing, social mechanism fully proven live; NEXT: trade-sell leg still unconfirmed after 3 different failed attempts (see item for exactly what broke each way) — needs a working live trader on the campaign map, which this session could not produce.

## Traps learned

- A subagent given a batch of N checklist items will sometimes spawn one child
  subagent per item on its own initiative even when not told to use `fill_queue`
  or similar — killing the PARENT does not kill the children, and they keep
  mutating live game/git state unsupervised for 10-20+ more minutes. Explicitly
  forbid Agent/Task-tool sub-spawning in every subagent brief from now on, not
  just for bridge-driving tasks (filed: LESSONS_INBOX, this session).
- `git rebase --continue` can say "You must edit all merge conflicts" while
  `git status` says "all conflicts fixed" — the real block is a re-dirtied
  tracked file (the health publisher fires constantly under concurrent load),
  not a remaining conflict (see: CLAUDE.md's own git section, already documented
  before this session — re-confirmed, not new).
- NEW this session: a rebase can also be blocked by another LOCAL session
  advancing `main` directly mid-rebase (`update_ref failed... is at X but
  expected Y`) — `(see: this handoff's 'one thing to carry forward')`.
- `git commit <path> -F -` fails with "pathspec did not match" if `-F -` comes
  AFTER a `--` pathspec separator — put `-F -` before `--`, or just don't use
  `--` at all when there's no ambiguous path (filed: LESSONS_INBOX).

## Closed since the last handoff (5)

- `MANYWATERS_COLOR_SUPPORT_1` — 960d71b6b
- `NINEFOLD_MISSING_EVENT_HOOKS_1` — 92fe0c00e
- `TILEGEN_SILENT_REUSE_1` — 8292bcd7e
- `QUICKTEST_RIVER_WATER_MISSING_1` — a8a1b92c2
- `DUPLICATE_CANON_DEFNAME_PAIRS_1` — 7562e534e

## Filed and still open (31) — the next seat's queue

- `ROSTER_DEAD_BMT_NAMES_SWEEP_1` — 14 ported-but-unwired BMT_ roster rows across 8 rosters: per-species wire-or-drop, never bulk-wire
- `KORRUM_ART_REGEN_1` — The korrum has no art of ours: texPath still points at Alpha Animals' own texture; 3 jobs re-keyed and quota-blocked to ~2026-09-26
- `STONEBACK_BOKKA_ART_STANDARD_1` — Judge the bokka's 2026-09-11 ported art against modern standards before regenerating (owner asked, did not order a regen)
- `SW_FAUNA_NEVER_IN_RM_TIER_1` — Route every Star Wars fauna row out of RM_-tier biome defs into the Utinni patch layer (97 rows, 12 biomes) — owner ruling Q11, taken by question card
- `GREENTIDE_JUNGLE_TREE_ROSTER_1` — The Greentide gets ten-plus jungle trees of our own, plus its signature giant
- `GREENTIDE_EXOTIC_JUNGLE_FISH_1` — The Greentide's catch becomes exotic jungle creatures, not base-game fish
- `HOSTILE_MOBILE_PLANTS_1` — Hostile mobile plants as animals - a new creature class
- `GREENTIDE_BIOME_DENSITY_1` — The Greentide is choked with foliage and brutal to cross
- `GREENTIDE_HUMMING_GROVE_1` — A grove that hums at differing pitches as you walk through it
- `GREENTIDE_RISK_REWARD_EXCHANGE_1` — The jungle is terrifying, and pays accordingly
- `GREENTIDE_GRENADE_WEAPONS_1` — Jungle grenades: stench, seeding and toxin
- `GREENTIDE_FRENZY_DISEASE_1` — The Frenzy - a disease you infect yourself with on purpose
- `CONTAGION_GENOME_ORGAN_GROWING_1` — Grow a colonist's organs inside a Contagion amoeba
- `FEVERWOOD_ANT_HIVE_DUNGEON_1` — Ant hives are reactive procedural dungeons
- `GREENTIDE_WASP_SWARM_1` — Jungle wasps: tiny, numerous, hives on plants, stings that stack
- `REACTION_MECHANISM_GENERALISE_1` — One reaction mechanism for four consumers: event object, shared budget, pluggable response, suppression
- `GREATBOLE_BARK_EDGE_ART_1` — The greatbole blob reads as bark at its edge and wood inside, and its real art is owed
- `GREATBOLE_HARVEST_LADDER_1` — The greatbole harvest: 40/60/70 thresholds, the fruit's three products, and the grubs that contest it
- `FEVERWOOD_FLORA_ROSTER_1` — The Fever Wood gets 18 invented plants of its own, replacing 7 donor placeholders
- `FEVERWOOD_BOUGH_SOIL_TERRAIN_1` — The crown cannot grow anything: boughway is fertility 0, so bough-soil is owed
- `FEVERWOOD_TENTACLE_BESTIARY_1` — Six tentacle types, the drive-off ladder, and a severed limb you can harvest
- `FEVERWOOD_SAP_SUCKER_GUILD_1` — Three sap-suckers, three defences, and the host plant that feeds them
- `FEVERWOOD_ALIEN_BIRD_CHORUS_1` — Alien birds whose chorus falls silent only for the water, and some of them steal
- `FEVERWOOD_TWO_FRONT_LURE_1` — Staked living bait, and two raiders who arrive one after the other
- `FEVERWOOD_DIANOGA_PRISON_1` — A prison tank, not a pen: it teaches, it produces, and it can get out
- `DEBUG_GAME_READY_WORLDUI_CRASH_1` — start_debug_game_ready leaves the game in a broken world/map-UI NullReferenceException loop at 623 mods, distinct from the closed NINEFOLD_DEBUG_GAME_
- `MIASMA_FLORA_ROSTER_1` — 19 invented Miasma plants: the rainbow blooms, our own mangals, and a carnivorous clade
- `MIASMA_FAUNA_FLOOR_ROSTER_1` — The Miasma arthropod floor, the fever-swarm, and the stranded as a condition
- `MLIE_ABSORPTION_BIOME_WIRING_1` — 98 live biome rows still name the bare donor for 73 creatures we already ported
- `STARWARS_DONOR_PORT_LABEL_COLLISIONS_1` — label_collision_check.py finds 62 label collisions between donor SW-animal-collection defNames and their RSW_ ports, both simultaneously cast -- DUPLI
- `WARDEN_MOTHER_BEFRIENDING_1` — The warden mother: lumbers in water, cannot reach land, befriended by freeing the young she cannot

## Commits

```
2017bdc1b SEA_FLOOR_AND_CATCH_PASS_1: remaining sea catch table edits (Twilight/Scald items+rare tables, Grey/Propane biome comments)
e09117c76 chore: health publisher artifacts regenerated (unblocks rebase, final)
766176ee0 Ledger/state sync: finish QUICKTEST_RIVER_WATER_MISSING_1 close-move, sync LESSONS_INBOX
9f3ecb17f SEA_FLOOR_AND_CATCH_PASS_1: four seas' catch tables built — 19 new catches, 2 new rare tables, RUT_PropaneShallow
449188bd9 SEA_FLOOR_AND_CATCH_PASS_1: sea catch rosters — four seas, seven-plus catches each (owner brief 2026-09-24)
497b0efed Connection to the sea is the gate, and that predicate shipped nine days ago
fa4e3358a No ships to sink, no time to grow up, and canals make her reach the player's
8e666ea10 She dies of age, and the young she could not reach inherit her
e3fb906aa chore: health publisher artifacts regenerated
435553401 The warden mother cannot reach her own young, and that is the whole mechanism
c29c8cec9 Bridge release: batch live-verify pass complete (items 1-8 + 11 real work, item 10 partial, item 9 untouched -- needs a multi-restart bisection out of scope for this session).
5c1aa709d MOD_OPTIONS_RETROFIT_1: live spot-check of 8 mods' Mod Settings (all 3 tiers) via jawa/mod_settings_field -- all 8 resolve cleanly, 5 round-trip toggle-verified. Real evidence the retrofit's settings layer is sound; not a full 46-mod census.
6e8f79dcd BARBSLINGER_SCORPION_REDESIGN_1: attempted live combat test, inconclusive (defenseless test colonist fled before engagement). Discovered and recorded a real bridge-tooling gap: jawa/pawn_use_verb cannot see/fire CompTurretGun-owned verbs at all (separate verb tracker from pawn.VerbTracker), relevant to any future turret-gun creature testing.
40d54e0b2 SEA_FLOOR_AND_CATCH_PASS_1: record that (a)-(c) shipped as mandrake.rm.seashores (fb352d7c6)
fb352d7c6 SEA_FLOOR_AND_CATCH_PASS_1: mandrake.rm.seashores — our seas become real coasts (mutator, IsCoastal, sea-keyed catch)
caa1f043d WYYYSCHOKK_FANG_PENDANT_1: three different attempts to produce a live trader on the campaign map to test the fang pendant's sale, all failed for different reasons (fire_incident silently doesn't fire; debug action produces no pawns; forcing the wrong pawn NREs inside a third-party trade mod). Trade-sell claim remains unconfirmed; documented why for the next pass.
1e7c1a305 Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave note (9 files clean, 1 fix)
f83ed91c5 CODE_REVIEW_STATUS sync: 9 files marked CLEAN (DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave)
f34c32a99 vivify_world.py: drop dead if-False ternary in diff()'s sort key
28b1fe9a8 WAR_LAB_CRATER_HOOK_1: first live proof of the ignition->crater mechanism on the real Ash'karr world (owner-authorized 2026-09-13). 57/57 propane lake tiles flipped correctly, 0 unexpected, confirmed persisting across a real save/load cycle on a separate test save. Idempotency and map-not-loaded edge cases remain untested.
... 209 more: git log --oneline 68fea67e0..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-24T01:17:37Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
?? infrastructure/artpipe/daemon_run_20260923_owner_100pct.log   FOUNDRY (this window) -- the daemon's own stdout log, live-appended, not meant to be committed as-is
?? infrastructure/artpipe/done/RSW_Cindermite_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Cindermite_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Cindermite_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Cindermite_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Cindermite_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Cindermite_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Dunegrass.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Dunegrass.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Dunestalker_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Dunestalker_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Dunestalker_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Dunestalker_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Dunestalker_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Dunestalker_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Ferroclaw_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Ferroclaw_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Ferroclaw_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Ferroclaw_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Ferroclaw_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Ferroclaw_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandhorn_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandhorn_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandhorn_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandhorn_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandhorn_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandhorn_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandmaw_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandmaw_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandmaw_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandmaw_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandmaw_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandmaw_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandstrider_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandstrider_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandstrider_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandstrider_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandstrider_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Sandstrider_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Spineroller_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Spineroller_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Spineroller_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Spineroller_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Spineroller_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Spineroller_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Stareling_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Stareling_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Stareling_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Stareling_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Stareling_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Stareling_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_SweetbarkTree.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_SweetbarkTree.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Tuskcoil_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Tuskcoil_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Tuskcoil_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Tuskcoil_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Tuskcoil_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Tuskcoil_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_VellaraBloom.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_VellaraBloom.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Voltmaw_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Voltmaw_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Voltmaw_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Voltmaw_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Voltmaw_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/RSW_Voltmaw_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/canon_boma_v1_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/canon_boma_v1_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/canon_boma_v1_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/canon_boma_v1_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/canon_boma_v1_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/canon_boma_v1_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/canon_dewback_v1_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/canon_dewback_v1_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/canon_dewback_v1_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/canon_dewback_v1_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_convor_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_convor_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_falumpaset_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_falumpaset_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_falumpaset_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_falumpaset_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_falumpaset_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_falumpaset_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_feralgrazer_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_feralgrazer_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_feralgrazer_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_feralgrazer_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_feralgrazer_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_feralgrazer_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_feralnerf_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_feralnerf_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_feralnerf_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_feralnerf_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_feralnerf_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_feralnerf_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_graniteslug_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_graniteslug_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_graniteslug_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_grank_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_grank_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_grank_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_grank_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_grank_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_grank_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_horax_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_horax_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_horax_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_horax_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_horax_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_horax_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_jakobeast_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_jakobeast_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_jakobeast_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_kraytdragon_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_kraytdragon_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_kraytdragon_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_kraytdragon_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_kraytdragon_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_kraytdragon_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_krykna_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_krykna_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_krykna_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_krykna_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_krykna_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_krykna_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_mossbeetle_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_mossbeetle_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_mossbeetle_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_mossbeetle_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_mossbeetle_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_mossbeetle_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_nerf_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_nerf_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_nerf_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_nerf_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_nerf_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_nerf_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_pikobis_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_pikobis_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_pikobis_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_pikobis_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_pikobis_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_pikobis_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_plant_bloddle.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/desertportb_plant_bloddle.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/rm_greatbole_v1.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/done/rm_greatbole_v1.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_dorrak_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_dorrak_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_dorrak_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_dorrak_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_dorrak_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_dorrak_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_krissek_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_krissek_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_krissek_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_krissek_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_krissek_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_krissek_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_vekkit_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_vekkit_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_vekkit_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_vekkit_north.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_vekkit_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/bluedesert_vekkit_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/canon_dewback_v1_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/canon_dewback_v1_south.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/canon_insectomorph_v1_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/failed/canon_insectomorph_v1_east.manifest.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/pending/canon_insectomorph_v1_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/pending/canon_insectomorph_v1_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/pending/canon_shiro_v1_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/pending/canon_shiro_v1_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/pending/canon_shiro_v1_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/pending/canon_vornskyr_v1_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/pending/canon_vornskyr_v1_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/pending/canon_vornskyr_v1_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/pending/canon_whisperbird_v1_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/pending/canon_whisperbird_v1_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/pending/canon_whisperbird_v1_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/pending/canon_zakkeg_v1_east.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/pending/canon_zakkeg_v1_north.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/artpipe/pending/canon_zakkeg_v1_south.json   art daemon's own operational output (no seat owns these individually; wired into a mod by whoever picks up that content next)
?? infrastructure/state/.rimflow_conc_97j8px_9/   rimflow's own internal concurrency-lock scratch dir, auto-generated, not meant to be committed
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing (present before this session started, 2026-09-11 dated) -- not this window's
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   pre-existing (present before this session started, 2026-09-21 dated) -- not this window's
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   FOUNDRY (this window's cold-load agent) -- deploy safety backup, keep until the load round it guards is fully closed
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   FOUNDRY (this window's cold-load agent) -- deploy safety backup, keep until RUST_CATHEDRAL_MECHANICS_1 closes
```

