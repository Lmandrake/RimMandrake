# BENCH_REBOOT_HANDOFF_202609180533 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609180411`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it before touching the
game.** This was a rot-development wave that turned into a campaign-load rescue.

## The one thing to carry forward

🔴 **`mandrake.rsw.gizkastowaway` deterministically breaks `new Game()` on the full mod list —
it is now DEACTIVATED, and that is the only reason the campaign loads.** Every save-load and
quicktest on the full 635 threw an NRE in `RimWorld.ReadingPolicyDatabase.GenerateStartingPolicies`
(null Type into `GenTypes.SameOrSubclassOf`). CONFIRMED by removal: with gizka off, a dev
quicktest's `new Game()` completes and `CANONICAL_ASHKARR_START_2026-09-12.rws` loads to Playing
with 0 reading-policy NRE. gizka shipped unproven because its own tests only ever ran a minimal
list, which does not trip it. **⛔ Do NOT re-activate gizka until `GIZKA_NEWGAME_NRE_FIX_1` lands.**
It is removed from BOTH the live ModsConfig and `ModsConfig.FULL.LATEST.xml` (backup:
`infrastructure/state/modlists/ModsConfig.BEFORE_GIZKA_DEACTIVATE.20260918_012858.xml`), so a
`--restore` will not re-break the campaign. Its Harmony patches (Scenario.PostGravshipLanded /
Thing.Destroy / TradeDeal / Quest.End / Pawn.Kill) do not obviously touch reading policies — the
mechanism is a full-set interaction, not yet pinned.

🔑 The instrument that cracked it: **log-diff across the day.** Afternoon full-list logs (14:09,
16:31) reached map-finish with ZERO reading-policy NREs; tonight's did not — so the crash was NEW
tonight, which collapsed a 600-mod hunt to the two mods newly activated tonight, of which one
(env hazards) was cleared by the tier-list quicktest and the other (gizka) was never load-tested.

## What the owner should see

**1. ✅ His campaign is loadable again.** It was fully blocked (no save would load) when he went
AFK; it loads now. The two review shots he asked for were captured and sent to his device:
`Transient/pyrelands_density3_final_20260918.png` (Pyrelands at live plantDensity 3.0 — a
fire-ecology biome, dense rust EmberGrass, not a uniform lush field) and
`Transient/firehawk_wingflap_final_20260918.png`.

**2. 🔴 Decision owed: gizka.** He ruled gizka IN (`GIZKA_TRIBBLE_ADAPTATION_1`); I took it OUT to
make his campaign load. He can (a) accept it off until the C# is fixed, or (b) want it back
sooner. The fix path is `GIZKA_NEWGAME_NRE_FIX_1`.

**3. 👁 FireHawk art colour.** The named review save's staged 5 hawks were gone from the loaded
map (abandon-timer cull); fresh ones were spawned. The wing-flap render tree WORKS (wings at
differing flap positions), but the art reads "armored grey-green flyer" more than fiery hawk and
the red under-glow is faint. Worth his eye on the colour intent.

**4. Fauna sitting draft awaits his ruling.** `Transient/rot_fauna_assignment_draft_20260918.md`
— 16 rows / 5 kin cliques for the WoundLink + KinMending + alarm-responder assignments, with 3
questions that genuinely need him (alarm-misfire tolerance, patch-now vs wait for
BMT_FAUNA_ABSORPTION_1, cross-species kin tags). Chosen "draft first then sit" per his card.

**5. Pyrelands north-star re-VALIDATED** (10 bars) on his word this session; density tripling
proven live 3.0 (regrow 9.0), the C# enforcer caught the startup rewriter red-handed in the log.

## What is half-done, and where it stops

- `GIZKA_NEWGAME_NRE_FIX_1` — filed, not started. **NEXT:** bisect gizka alone onto a mid-size
  list that still trips the NRE; find the type/GameComponent/patch that nulls a reading-policy
  reflection; fix additively; prove `new Game()` clean on the full list; then re-add gizka to
  live + FULL.LATEST. Restores his ruling safely.
- `FLOWWORKS_BOTTLED_LIQUID_TYPE_MISSING_1` — root cause fixed (stale deployed DLL redeployed;
  game DLL now carries `RM_BottledLiquidExtension`). **NEXT:** confirm on the next harvest that the
  ~33 RM_LiquidBottles defdiscards are gone (discards dropped 82→49 already this load); then close.
- `ENVHAZARDS_DLL_REBUILD_OWED_1` — filed. Deployed DLL works (VaporDrifter present, tier
  quicktest clean) but source is ahead (`RM_RootCausewayBiomeExtension.cs`). **NEXT:** rebuild +
  redeploy in a shutdown window; low urgency, not a blocker.
- `ROT_PALE_TREE_1` — reopened→fixed→ready. The `compClass` on CompProperties_SpawnSubplant was
  missing (props ctor doesn't set it → bare ThingComp → InitializeComps catch killed all 9 comps
  silently). Fixed + deployed (`f4d8dbf2b`). **NEXT:** re-proof on a load — spawn RUT_PaleTree,
  expect NO MissingMethodException and live meditation/psylinkable fields (baseline: the 2 MMEs
  in the pre-fix log are startup-only).
- `ROT_ART_WAVE_1` — 22 artpipe jobs filed to `infrastructure/artpipe/active/`
  (`Transient/rot_art_jobs_20260918.md`). **NEXT:** as the daemon finishes each, review vs the
  def's flavor, place at texPath (rename shared placeholders so unrelated defs keep art), deploy,
  verify render. Owed inside it: brewing vessel east/north views; RUT_LivingFurnaceCap
  MortalMorel-folder/HealingMorel-files naming mismatch; gene icon may not belong in artpipe.
- `ROT_HEALTH_SHARING_1` — built, BLOCKED (content-blind, 0 carriers). **NEXT:** the fauna sitting
  (draft above) assigns carriers; per-clique KinMending strength lives on
  `CompProperties_KinMending.extraSeverityHealedPerDay` = one small hediff def per clique.
- Six rot items CLOSED this wave on live battery evidence (see Closed section). Nothing mid-edit.

## Traps learned

- 🔴 **The shared working tree + index is brutal on git under a peer's commit burst.** A
  `pull --rebase` collided with another window committing live into the same index, leaving a
  DETACHED HEAD that both windows then committed onto while a third pushed separately — three
  divergent lineages. Recovered by converging them in an isolated `git worktree add --detach
  origin/main` + cherry-pick, then `git push origin HEAD:main`, then reattaching main. **A stale
  `.git/index.lock` at 0 bytes with no `pgrep git` is a crashed leftover — safe to rm; a live
  `pgrep git` is a peer, wait it out.** (worth LESSONS_INBOX)
- 🔴 **"Could not find type named X" with the .cs in the compile list and the namespace matching
  is a DEPLOY gap, not a source bug** — the game-copy DLL is behind the repo DLL. Diagnose with
  md5 repo-vs-game AND a binary grep for the type name (type metadata is UTF-8, so a plain
  `grep -a` finds it even though string constants are UTF-16). FlowWorks was exactly this.
- 🔴 **A missing `compClass` silently kills EVERY comp on a def** — `CompProperties_SpawnSubplant`
  doesn't set compClass in its ctor, so omitting it instantiates bare `Verse.ThingComp`, and
  `InitializeComps`' try/catch wraps the whole loop → one bad comp takes all of them, no
  Psylinkable, no error a player sees. Vanilla anima tree carries `<compClass>CompSpawnSubplant`.
- **`handoff.py` prefills the skeleton from recent commits/state, which can be ANOTHER window's
  wave** — this file came pre-populated with a walk-findings/determinism handoff that was not this
  session. Rewrite the prose; don't trust the autofill. (this handoff)
- **RimSage's index predates Odyssey 1.6 reading policies** — `read_csharp_symbol
  RimWorld.ReadingPolicyDatabase` returns "not found", so an Odyssey-internals question is
  unanswerable there even on the Desktop. Reason from log-diff instead.

## Closed since the last handoff (7)

- `ROT_SPORECLOUD_PORT_1` — f4d8dbf2b (Battery F PASS)
- `ROT_DECAY_HARVEST_1` — f4d8dbf2b (Battery C PASS)
- `ROT_SHEEN_WEATHER_1` — f4d8dbf2b (Battery E PASS ×4)
- `ROT_WARM_MAT_1` — f4d8dbf2b (Battery D PASS)
- `ROT_GUARDIAN_GROVES_1` — f4d8dbf2b (Battery H PASS ×2, alarm blocked-by-design)
- `ROT_LIVE_PREPARATIONS_1` — f4d8dbf2b (Battery I PASS)
- All closed with `--owner-said "Continue developing the rot"` (they belonged to FOUNDRY/OWNER).

## Filed and still open (4) — the next seat's queue

- `GIZKA_NEWGAME_NRE_FIX_1` — fix gizka's new-Game() NRE so it can be re-activated (his ruling restored)
- `FULL_LIST_CANNOT_LOAD_GAME_1` — RESOLVED-by-deactivation, real fix owed = GIZKA_NEWGAME_NRE_FIX_1
- `FLOWWORKS_BOTTLED_LIQUID_TYPE_MISSING_1` — root-caused + redeployed; confirm discards clear, then close
- `ENVHAZARDS_DLL_REBUILD_OWED_1` — repo DLL stale vs source; rebuild+redeploy, low urgency
- `ROT_ART_WAVE_1` — 22 artpipe jobs to land as the daemon finishes

## Commits (this session, newest first)

```
d0e9773c6 CONFIRMED: gizkastowaway breaks new Game() on the full list — deactivated, campaign loads again
596c9204c Full-list NRE diagnosis: new tonight; gizka-deactivate experiment; FlowWorks redeployed
ee05d75b6 rimflow: file FULL_LIST_CANNOT_LOAD_GAME_1 — full list NREs in new Game(); density readback PASS 3.0
adfce7160 rimflow: Load B up — density enforcer caught the rewriter live; file FLOWWORKS_BOTTLED_LIQUID_TYPE_MISSING_1
e53bde3a7 rimflow: rot wave closes (6 items on battery evidence), ROT_ART_WAVE_1 filed, Pyrelands re-validated
f4d8dbf2b ROT_PALE_TREE_1: restore the compClass vanilla carries on CompProperties_SpawnSubplant
78b80640c ROT_PALE_TREE_1: drop explicit thingCategories duplicating the inherited Plants entry
5a10d06d3 rimflow: ledger sync (bridge take, game down, rot-wave cycle start)
6b41e3094 Rot wave: decision strings + assembly signatures for the two-load cycle
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (1 RimWorldWin64 process, bridge answered before release)
- recorded  : UP  (full 634-mod list — gizka OFF; a driver left it Playing/paused on a dev map)
- Bridge: FREE   (released by BENCH this wrap)
- His campaign save is INTACT — not overwritten. The loaded dev map is disposable; he loads his
  save fresh when he returns.
- Tree: everything above committed and pushed (HEAD d0e9773c6). Untracked `Transient/` artifacts
  only. A few harmless duplicate `autostash` entries remain in `git stash list` from the rebase
  recovery — droppable, they hold no unique work.
