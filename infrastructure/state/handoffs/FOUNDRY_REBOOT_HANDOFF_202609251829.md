# FOUNDRY_REBOOT_HANDOFF_202609251829 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609251722`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**This shared tree's local `main` had silently drifted 10 commits behind `origin/main`** at wake
(confirmed via two-way `git diff --stat` before touching anything: origin held real shipped work
— the reaction-mechanism step-1 build, greatbole/fevertrunk marker fixes, fish items,
`scald_showcase.py` — invisible to this window's ledger reads, while local's 10 unique commits were
each already duplicated on origin under different shas). `rimflow next`/`show` were answering from
that stale base the whole time. Fixed by resetting to `origin/main` (safety branch
`backup-foundry-pre-reconcile-20260925T174257Z`), then recovering the real uncommitted delta on top
(union-merged the BENCH/FOUNDRY ledger jsonl shards and the artpipe registry/throughput logs,
verified every line still parses, re-deleted jobs the local daemon had already completed that
origin's copy hadn't caught up on). **Before trusting `rimflow next` cold, `git diff --stat HEAD
origin/main` both ways first** — a stale local ledger looks identical to an empty queue.

Second lesson, from the owner directly mid-session: *"DO NOT MAINTAIN THE PURITY OF TEST COLONIES!
This is a throw-away game. Do what you need and stop treating ANY game as important until told
otherwise."* I'd declined a live bridge quicktest because the loaded map had 37 NAMED colonists and
read as "the real campaign" — exactly the fallacy `[[map-state-is-disposable-debug]]` already warned
against, just in fancier clothes (named pawns, not just an established-looking colony). Saved as a
memory update. **A colony looking real is not evidence it is real — only an explicit announcement
is.**

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **GREATBOLE_BARK_EDGE_ART_1's real art shipped via a fallback image generator, not Codex.**
  Codex `$imagegen` was down repo-wide (shared `CODEX_HOME` refresh token invalidated, confirmed
  with 3 attempts including a fresh isolated worker home) when that subagent ran, so it used the
  sanctioned fallback (Nano Banana Pro / `gemini_image.py`) instead. Worth knowing if Codex art
  generation looks broken elsewhere too — this wasn't a one-off.
- **REACTION_MECHANISM_GENERALISE_1 step 2 shipped a brand-new minimal creature**
  (`RM_Gallowroot`, `mandrake.rm.hostileflora`) as scaffolding to host the propagation mechanism —
  invented name, RM tier, placeholder art, `manhunterOnDamageChance` 0 so aggression routes only
  through the new mechanism. It is NOT wired into any biome roster and was never meant as a
  finished creature — it exists to prove the mechanism, not to ship. Flag it before anyone assumes
  it's a real roster addition.
- Nothing else this wave needed his judgment or veto — the rest (artpipe daemon fix, 28 red-X
  texPath fixes, JAWA_MESS_IMMUNITY_1 close) are bug fixes with clean offline+live evidence.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `REACTION_MECHANISM_GENERALISE_1` — doing; NEXT: build step 3 (the ant hive,
  `FEVERWOOD_ANT_HIVE_DUNGEON_1`) OR finish out step 2's own owed edges first — `RM_Gallowroot`
  currently only triggers on damage (a colonist can walk up undisturbed; item wants a proximity
  trigger too), has no biome placement and no real art. Step 4 (migrate the shipped
  `RM_CompPlantAlarm` with NO behaviour change) is explicitly last per the item — do not do it
  before 3.
- `GREENTIDE_WASP_SWARM_1` — proposed, not doing; NEXT: unchanged from before this wave — wire the
  already-built `RM_SkerrelGall` onto real host plants once `RM_Sarquin`/`RM_Nemmer` exist as
  ThingDefs (they don't yet).
- `RIVER_STEAM_ANIMATION_1` — doing, BLOCKED; NEXT: needs a live bridge screenshot of a
  Pyrelands-river map, contested this wave by another live FOUNDRY window holding/wanting the
  bridge for its own work — take it when free and get the shot, offline preconditions are already
  clean.
- `FLORA_LEGIBILITY_BAR_1` — doing, BLOCKED; NEXT: genuinely needs the owner's eye on
  `Transient/flora_legibility_sheet_2026-09-17/` (still 100% synthetic prefill, confirmed unchanged
  across 3 waves now including this one) — do not re-verify a 4th time, it will still be prefill;
  escalate to him directly instead.
- `OFFBIOME_SHEET_RERENDERS_1` — doing; art for bolotaur/gualaar/fulgurite is fully built, wired
  and offline-validated. NEXT: a live look once a matching mod list loads — `mandrake.rsw.
  gualaarartoverride` (the new mod) is NOT in the current live `ModsConfig.xml`'s 627 active mods,
  so it needs adding before any restart would even show it; don't force a restart just for this,
  batch it with other game-up work per the standing rule.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A subagent claiming "no WSL dotnet toolchain, shipped uncompiled" is a known false negative, not
  a real blocker — `/mnt/c/Users/Mandrake/.dotnet/dotnet.exe build 'D:\...\Foo.csproj' -c Release`
  builds clean from WSL bash with zero setup; two subagents this wave independently hit this and
  both were wrong (see: `[[rimworld-csharp-toolchain]]`, already documents this exact recurrence).
- The bridge's `Outputs\Thoughts` debug action is a GLOBAL ThoughtDef reference table (every
  ThoughtDef in the game, defName/stages/mood values), NOT a per-pawn active-thought list —
  selecting a different pawn first changes nothing about its output. There is currently no bridge
  tool that reads a specific pawn's live situational-thought state; verify mood mechanisms via
  engine source (RimSage) instead, e.g. `Thought.MoodOffset()` checking
  `ThoughtUtility.ThoughtNullified()` for every `Thought` subclass including `Thought_Situational`
  (worked example: `JAWA_MESS_IMMUNITY_1`'s close note) (filed: LESSONS_INBOX).
- `rimworld/get_cell_info` and `rimworld/select_pawn` don't take a `mapIndex`/expect a bare pawn id
  respectively — `select_pawn` needs the `Thing_<id>` form even though `jawa/spawn_pawn` returns a
  bare id; the client's declared-parameter check catches the wrong-name case loudly, trust it over
  guessing a param name (filed: LESSONS_INBOX).

## Closed since the last handoff (4)

- `ARTPIPE_QUOTA_RESET_WEDGE_1` — fa8e676bd
- `GREATBOLE_BARK_EDGE_ART_1` — 6d0dbf802
- `STACKCOUNT_FILEPATH_REDX_SWEEP_1` — b8d6f227c
- `JAWA_MESS_IMMUNITY_1` — a9aef1bc1

## Filed and still open (0) — the next seat's queue

Nothing filed in this window.

## Commits

```
90733209c Health dashboard + queue render refresh
b066a1576 BENCH handoff: Scald showcase + two crash fixes live, statue/steam/dive specs ruled, Jawa hood built
ebcecf44a Ledger: JAWA_SWIM_HOOD_KEEP_1 built, deploy owed
580a39c7a Jawa hood node: move from StarWarsRaces into a JawaRules patch
71e013a4f JAWA_HOOD_ALWAYS_VISIBLE_1: Jawa never render bare-headed, in any state
5275333b3 Ledger: close JAWA_MESS_IMMUNITY_1 (live quicktest + engine verification)
304e32407 Ledger: bridge take/release, no game changes (JAWA_MESS_IMMUNITY_1 live quicktest deferred -- real campaign colony loaded, not a disposable quicktest map)
9b4b9af98 Ledger: close GREATBOLE_BARK_EDGE_ART_1, STACKCOUNT_FILEPATH_REDX_SWEEP_1
b8d6f227c Ledger: close ARTPIPE_QUOTA_RESET_WEDGE_1, note REACTION_MECHANISM_GENERALISE_1 step-2 progress
6d0dbf802 GREATBOLE_BARK_EDGE_ART_1: bark-edge atlas art + linked-tile def wiring + regrowth-rate tunable
c1e246b6f STACKCOUNT_FILEPATH_REDX_SWEEP_1: fix 28 collection-init red-X defs, census the rest
0131ec0ad Ledger: bridge release (BENCH wrap)
c99c25955 Rebuild RimMandrake.CreatureBehaviors.dll: verify REACTION_MECHANISM_GENERALISE_1 step 2 compiles
2a227f630 Ledger: close SHULLA_INVISIBLE_RENDER_1 (paused-staging transient), file JAWA_SWIM_HOOD_KEEP_1
109f54f6b REACTION_MECHANISM_GENERALISE_1 step 2: same-kind propagation under a minimal hostile mobile plant
fa8e676bd chore: regenerated codebase health artifacts (auto, blocking a rebase)
d5d3c8e5b artpiped: weekly quota wedge self-heals via reported reset time (ARTPIPE_QUOTA_RESET_WEDGE_1)
7ced2ec27 Wave 6: mark CLEAN the REACTION_MECHANISM_GENERALISE_1 step-1 cluster (7 files)
e137acf2b Ledger: SHULLA_INVISIBLE_RENDER_1 is not pinned; correct the over-claiming note
7374f9f82 Merge remote-tracking branch 'origin/main'
... 7 more: git log --oneline 26421a1a3..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-25T18:24:00Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
?? deployed/config/ModsConfig.before-tier-firehawk.xml   (another seat's modset_builder tier-swap backup; not this window's, not touched)
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   (another seat's modset_builder tier-swap backup; not this window's, not touched)
?? infrastructure/artpipe/done/bluedesert_dovvik_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_dovvik_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_dovvik_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_dovvik_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_dovvik_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_dovvik_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_utikka_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_utikka_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_utikka_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_utikka_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_utikka_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_utikka_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_vrisk_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_vrisk_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_vrisk_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_vrisk_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_vrisk_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_vrisk_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_brossak_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_brossak_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_brossak_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_brossak_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_brossak_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_brossak_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_fezzira_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghaaz_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghaaz_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghaaz_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghaaz_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghaaz_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghaaz_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghuvv_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghuvv_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghuvv_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghuvv_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghuvv_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_ghuvv_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_gollivra_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_gollivra_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_gollivra_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_gollivra_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_gollivra_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_gollivra_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pellorax_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pellorax_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pellorax_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pellorax_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pibbo_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pibbo_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pibbo_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pibbo_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pibbo_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_pibbo_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vezzok_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vezzok_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vezzok_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vezzok_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vezzok_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vezzok_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vulloth_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vulloth_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vulloth_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vulloth_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vulloth_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_vulloth_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhirrik_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhirrik_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhirrik_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhirrik_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhirrik_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhirrik_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhool_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhool_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhool_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/contagion_zhool_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_brekkugar_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_brekkugar_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_brekkugar_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_brekkugar_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_brekkugar_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_brekkugar_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_dhukk_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_dhukk_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_dhukk_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_dhukk_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_dhukk_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_dhukk_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_ghorrumak_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_ghorrumak_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_ghorrumak_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_ghorrumak_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_ghorrumak_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_ghorrumak_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_gruzz_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_gruzz_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_gruzz_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_gruzz_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_gruzz_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_gruzz_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_hulggarok_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_hulggarok_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_hulggarok_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_hulggarok_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_hulggarok_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/crags_hulggarok_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_porg_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_porg_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_porg_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_porg_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_porg_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_porg_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_qormot_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_qormot_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_qormot_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_qormot_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_qormot_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_qormot_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_runyip_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_runyip_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_runyip_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_runyip_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_runyip_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_runyip_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_shaak_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_shaak_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_shaak_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_shaak_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_shaak_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_shaak_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_strill_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_strill_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_strill_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_strill_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_strill_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_strill_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_teemuss_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_teemuss_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_teemuss_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_teemuss_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_teemuss_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_teemuss_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_uvak_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_uvak_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_uvak_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_uvak_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_uvak_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_uvak_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_varactyl_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_varactyl_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_varactyl_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_varactyl_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_varactyl_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_varactyl_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_voorpak_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_voorpak_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_voorpak_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_voorpak_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_voorpak_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_voorpak_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_vulptex_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_vulptex_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_vulptex_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_vulptex_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_vulptex_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_vulptex_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_warwyrm_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_warwyrm_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_warwyrm_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_warwyrm_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_warwyrm_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_warwyrm_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_whisperbird_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_whisperbird_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_whisperbird_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_whisperbird_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_whisperbird_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_whisperbird_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_zeer_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_zeer_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_zeer_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_zeer_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_zeer_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/desertportb_zeer_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_kurreth_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_kurreth_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_kurreth_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_kurreth_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_kurreth_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_kurreth_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_plant_ossagrel.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_plant_ossagrel.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_skreth_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_skreth_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_skreth_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_skreth_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_skreth_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_skreth_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_thornbug_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_thornbug_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_thornbug_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_thornbug_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_thornbug_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/feverwood_thornbug_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_brakkel_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_brakkel_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_brunnock_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_brunnock_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_cundral_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_cundral_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_gorbeleth_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_gorbeleth_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_kaddrath_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_kaddrath_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_maddrick_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_maddrick_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_mirrelbole_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_mirrelbole_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_mourvel_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rm_mourvel_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rut_wildhealroot.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rut_wildhealroot.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutbloomcrop_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutbloomcrop_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutdarkcrust_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutdarkcrust_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutdeltaloam_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutdeltaloam_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutfuzz_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutfuzz_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutglower_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutglower_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutglowercrust_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutglowercrust_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutstaggerseed_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutstaggerseed_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutvaultroot_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutvaultroot_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutwelcomeblanket_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/rutwelcomeblanket_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_bladderboilcatch_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_bladderboilcatch_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_noohm_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_noohm_v1_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_noohm_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_noohm_v1_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_noohm_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_noohm_v1_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_saalcatch_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_saalcatch_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_shulla_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_shulla_v1_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_shulla_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_shulla_v1_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_shulla_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_shulla_v1_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_shullacatch_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_shullacatch_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_steamcatchbuilding_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_steamcatchbuilding_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_ventbuilding_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_ventbuilding_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_wreckframe_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_wreckframe_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_wreckhull_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_wreckhull_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_wrecktank_v1.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/done/scald_wrecktank_v1.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/contagion_pellorax_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/contagion_pellorax_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/contagion_zhool_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/contagion_zhool_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/crags_kessik_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/crags_kessik_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutbrinebattery_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutbrinebattery_v1_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutbrinebattery_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutbrinebattery_v1_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutbrinebattery_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutbrinebattery_v1_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutfleetflier_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutfleetflier_v1_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutfleetflier_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutfleetflier_v1_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutfleetflier_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutfleetflier_v1_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutkarrathil_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutkarrathil_v1_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutkarrobel_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutkarrobel_v1_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutslimegrazer_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutslimegrazer_v1_east.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutslimegrazer_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutslimegrazer_v1_north.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutslimegrazer_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/failed/rutslimegrazer_v1_south.manifest.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_kessik_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_kessik_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_shekkur_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_shekkur_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_shekkur_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_thrizzik_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_thrizzik_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_thrizzik_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_ulkhorr_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_ulkhorr_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_ulkhorr_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_vrakk_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_vrakk_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_vrakk_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_zekkra_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_zekkra_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_zekkra_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_zhurrakor_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_zhurrakor_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/crags_zhurrakor_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_essarn_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_essarn_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_essarn_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_fessk_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_fessk_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_fessk_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_otheska_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_otheska_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_otheska_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_sorruth_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_sorruth_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/greysea_sorruth_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/nightside_mahllik_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/nightside_mahllik_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/nightside_mahllik_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/nightside_zhissa_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/nightside_zhissa_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/nightside_zhissa_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_heemin_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_heemin_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_heemin_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/rut_greentideant_body_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/rut_greentideant_body_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/rut_greentideant_body_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/rut_greentideant_carapacewall_atlas.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/rut_greentideant_carapacewall_menuicon.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_bladderboilcatch_a.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_bladderboilcatch_b.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_bladderboilcatch_c.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_dosscatch_a.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_dosscatch_b.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_dosscatch_c.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_eeshcatch_a.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_eeshcatch_b.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_eeshcatch_c.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_ekkelcatch_a.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_ekkelcatch_b.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_ekkelcatch_c.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_karrashcatch_a.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_karrashcatch_b.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_karrashcatch_c.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_muddalcatch_a.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_muddalcatch_b.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_muddalcatch_c.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_rainbowpigment_a.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_rainbowpigment_b.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_rainbowpigment_c.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_saalcatch_a.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_saalcatch_b.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_saalcatch_c.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_shullacatch_a.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_shullacatch_b.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_shullacatch_c.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_steamcatchbuilding_a.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_thuumcatch_a.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_thuumcatch_b.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_thuumcatch_c.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_ventbuilding_a.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_ventbuilding_b.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_wreckframe_a.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_wreckframe_b.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_wreckframe_c.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_wreckhull_a.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_wreckhull_b.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_wreckhull_c.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_wrecktank_a.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_wrecktank_b.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/scald2_wrecktank_c.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_bezzul_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_bezzul_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_bezzul_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_greateroomb_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_greateroomb_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_greateroomb_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_hennul_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_hennul_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_hennul_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_mubbaro_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_mubbaro_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_mubbaro_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_oomb_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_oomb_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_oomb_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_thummorak_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_thummorak_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_thummorak_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_vohhm_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_vohhm_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_vohhm_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_wuppik_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_wuppik_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_wuppik_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_wuum_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_wuum_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_wuum_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_yollum_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_yollum_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/slime_yollum_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_east.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_north.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_south.json   (ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's)
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   (pre-existing backup/snapshot file, predates this window)
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   (pre-existing backup/snapshot file, predates this window)
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   (pre-existing backup/snapshot file, predates this window)
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   (pre-existing backup/snapshot file, predates this window)
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   (pre-existing backup/snapshot file, predates this window)
?? src/RimMandrake/Utils/firehawk_flight_probe.py   (another live FOUNDRY window -- building the Pawn_FlightTracker state-read tool per FIREHAWK_FLIGHT_BEHAVIOR_1's no-screenshot-flight-testing ruling; in progress, not this window's)
```

