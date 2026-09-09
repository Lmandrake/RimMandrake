# FOUNDRY_REBOOT_HANDOFF_202609090517 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609090029`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

A bare `--` inside an XML `<!-- -->` comment is illegal XML and RimWorld's
parser silently rejects the WHOLE file — my own ARMOURY_LOADAFTER_STALE_1
commit did exactly this (used `--` as an em-dash in prose), wedged the
owner's live game behind ~8 stuck dev-mode error popups, and needed a kill
+ Steam relaunch to clear once BENCH caught and fixed the file. Every
subagent prompt that writes prose into an XML comment must be told not to
use `--`, and the writer should `xml.etree.ElementTree.parse()` the file
afterward — it correctly rejects this, it is not being lenient.

## What the owner should see

- `MOD_LICENSE_PERMISSIVE_1` is filed (his own ask: "the most generous
  re-use license... we're not trying to control or make money") with CC0-1.0
  proposed as the license — not yet executed across the mod tree. If he'd
  rather name MIT/Unlicense specifically instead of CC0-1.0, say so before
  whoever picks this up runs it broadly across every mod we author.
- Everything else owner-facing tonight (the Mynock hideous-redesign
  direction, the MenuShell cosmetic-bug ruling, the BlastDoor port-first
  ruling) was already decided live with him in this session — nothing new
  waiting on his eye beyond the license-name check above.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1` — offline rewrite complete and
  committed (ef628781): OracleClient.cs shells out to `claude -p`, verified
  against both the WSL and the owner's real Windows binary, 0W/0E build,
  45/45 selftests. NOT closed — the item's own verify block is explicit
  that a passing selftest proves nothing about the transport; only the live
  "Test Ohm letter" debug action does. Next action: next time the bridge is
  free and the game is up, run that debug action, confirm a real `claude -p`
  call fires (or the prescribed fallback fires on failure), then close.
- `WORLD_FEATURE_LABELS_OVERSIZED_1` — the actual code fix (2.2f → 1.35f,
  `JawaBenchWorldTools.cs:4686`) was ALREADY source-committed by an earlier
  session (`b0e18f89`, bundled into an unrelated-looking rename-sprint
  commit) — confirmed the parallel formula in `ashkarr_paint.py` already
  independently uses 1.35 too, no drift. NOT closed — needs a build + deploy
  of the companion DLL in a game-down window, then `jawa/world_features_get`
  + a screenshot to verify by looking, per the item's own gates. Next
  action: build, deploy on the next game-down, verify live.
- `IKEE_MYNOCK_ART_REGEN_1` — all 3 Mynock facings (south/east/north)
  generated, validated (PASS, exact aspect match each), shipped as a new
  mod `mandrake.rsw.mynockartoverride` (commits a085bf59, 437b8b81 unrelated
  — see the Mynock commit specifically at a085bf59), deployed to the live
  Mods folder. Owner-directed style: hideous wet practical-creature-effects
  redesign with distended eyestalks, iterated live with him watching and
  judging each pass — he approved the final look ("keep the hideous...
  let our Mynock fly"). NOT closed — needs `needs: game-up` (already set):
  enable the mod in ModsConfig, cold load, and confirm the loose-texture
  override actually wins against the donor's Unity-AssetBundle-packed
  original (UNVERIFIED mechanism — loose-overrides-loose-by-load-order is
  proven elsewhere in this repo, loose-overrides-AssetBundle is not).
  Owner's own word: "Leave queued for opportunistic load."

## Traps learned

- **The `--`-in-XML-comment defect above** — already filed to
  `LESSONS_INBOX.md`.
- **A subagent that backgrounds a slow command and waits for a
  notification deadlocks — recurred 3 times THIS session** despite already
  being a filed lesson (`subagents-must-run-commands-foreground` memory).
  Hit it on a full-repo `gen_armour_patch.py` regen, a `validate_patch.py`
  scan of the ~600-mod install, and a background image-gen wait. Every
  fanout prompt for this project should carry the foreground-only
  instruction by DEFAULT now, not just when the task obviously looks slow.
- **`git commit` with no pathspec commits the WHOLE staged index, and a
  shared repo means someone else's staged files can be sitting there.**
  Hit an `index.lock` collision with a concurrent BENCH commit twice
  tonight — the fix each time was: confirm no live git process (`ps aux`),
  remove the stale lock, then `git commit -m "..." -- <exact paths>` scoped
  to only my own files. One BENCH commit (`624417ad`) separately swept up a
  subagent's staged `OracleHttpClient.cs` deletion — correct content,
  landed in the wrong commit; not worth rewriting history for, just noted.
- **`rimflow close --sha` with a pre-computed `$(git rev-parse HEAD)` can
  record the WRONG sha** if a concurrent git lock delays your actual commit
  past when you captured the variable — hit this twice, both times the
  close ran against the *previous* commit, not the one with the fix. Fixed
  both via `rimflow note` recording the correction — there is no way to
  edit a closed record directly, and a second close on the same item is
  refused. Lesson: after any git-lock collision, re-verify `git log -1`
  matches what you're about to pass to `close`, don't trust an
  already-captured variable.
- **`mcp__rimsage__search_defs`/`search_source` has real blind spots.**
  Returned "no results" for `Tellurox`, `Backpack_scorch`, and `Mynock`,
  all of which exist and resolve fine via `def_inventory.build()` directly
  against the live mod set. Don't trust a rimsage "not found" as proof of
  absence for anything load-bearing — cross-check with `def_inventory` or a
  direct grep of the actual mod's raw XML.
- **`codex_image.py`'s sandbox helper is fragile across a Codex app
  update, and the failure mode isn't always a UAC prompt.** Tonight it was
  first a "module could not be found" error dialog (stale/incomplete
  install), then — after the owner updated Codex — a genuine UAC elevation
  prompt from BOTH a stale isolated worker home AND the shared home, which
  stopped once two long-lived pre-update `codex.exe`/`codex-code-mode-host.exe`
  processes were killed. If Codex image-gen misbehaves, check
  `tasklist.exe | grep codex` for stale processes before anything else.
- **Asking for a "transparent background" in a `codex_image.py edit`
  prompt can produce a literal drawn checkerboard pattern (fully opaque
  RGB, no alpha) instead of real transparency** — confirmed by reading the
  raw file's alpha channel directly (all 255). The correct, already-
  documented convention (`generating-images/references/prompting.md`) is
  to ask for a flat solid chroma-key color (e.g. `#00ff00`) and cut it with
  `chroma_key.py` afterward — never ask for "transparent" directly.

## Closed since the last handoff (13)

- `ARMOURY_LOADAFTER_STALE_1` — 23729555443fd55e5be7e30ca701953acd01349c
- `PATCHMODS_LOADAFTER_SWEEP_1` — 23729555443fd55e5be7e30ca701953acd01349c
- `ARMOURY_SUBSTRING_RUNG_TRAP_1` — 23729555443fd55e5be7e30ca701953acd01349c
- `PATCH_LEDGER_MINUS_ONE_OSCILLATES_1` — 6a582966cddad668f84febb73f5441a93041a799
- `PAWNFLAVOR_GEN_BEHIND_1` — 1f144a3873724170d6540e276aa2cb74b714afc3
- `BLIZZARISK_DONOR_CUT_1` — 0188c925c9cb49d6bd9e2e628dde95fdbd94f039
- `ARMOURY_DECLARER_ATTRIBUTION_FLIP_1` — 11dcd56fa4b5bf49136d88a072bfb1aafc7b469e
- `BIOME_LABEL_CAMPAIGN_NAMES_1` — 457d21f51d6eb4b6bae79debf1f394014e449d5f
- `STARWARSRACES_TOOLBOX_SOFT_DEP_1` — 555ef84be873113dec494fe05b3904d8cda2e633
- `RAIDREDESIGNER_HARD_PROPERTY_REF_1` — 618f948660b90d2f0436995201e3c04f845903f1
- `LANTERNDEEPS_GENSTEP_ALLOWLIST_DEAD_1` — 618f948660b90d2f0436995201e3c04f845903f1
- `ARMOURY_LEATHER_RATINGS_REGEN_STALE_1` — ddad4e6898a83d297a36df14a054a637209a7381
- `BLASTDOOR_LUMI_PORT_1` — 437b8b81193aa4b5e6e339c780d805ac55a88162

## Filed and still open (11) — the next seat's queue

- `DROIDWORKS_MODULE_SMELT_CONFIG_1` — 3 DW armor modules (Lte/Mid/Hvy) log 'smeltable but does not give anything for smelting' x2 each — new vs config-error baseline, surfaced on the conso
- `PYRELANDS_SELF_CONTAINED_BIOME_1` — Author RM Pyrelands' own BiomeDef, self-contained: ScorchFruit, strange weather, ash-as-snow, Cinderfall storms, fast grass (owner ruled the R9 fork: 
- `PYRELANDS_WORLD_SWITCH_1` — Switch Ashkarr's Pyrelands tiles from donor ZBiome_Grasslands to RM_FE_Pyrelands BEFORE the world freeze — rides the owed world re-import window; unbl
- `MOD_LICENSE_PERMISSIVE_1` — Add the most generous re-use license (CC0-1.0) to every mod we ship
- `DESERT_WRAPS_ART_COMMISSION_1` — Original desert-wrap apparel art (full body-type matrix) + devolved Tusken head shape, inspired-not-copied; placement: wraps to Armoury, headtype to S
- `MOVING_DUNES_BUILD_1` — Build the dunes engine per MOVING_DUNES_DESIGN.md v2 (model=opus, ~1.1-1.4k lines): Werner transport on Odyssey sandGrid, source/sink edges, DuneMater
- `GAPING_DOOM_SITE_1` — The Gaping Doom: dead-sarlacc toxic-waste pit at tile 2403 (32.12N 94.76E, Cracked Lands, Junker territory) — landmark + green-throat art derived from
- `BIOME_ENRICHMENT_POISON_FOREST_1` — Enrichment wave (review B1): Poison Forest is mutator-barren (74% zero-tile MEASURED) — place from its sheet's own kit: vent fields, metal-plated grov
- `BIOME_ENRICHMENT_DESERT_WASTELAND_1` — Enrichment wave (review B1): Desert (53% zero-mutator) + Wasteland (63%) — the two largest land biomes read thin where caravans travel most; place fro
- `SEA_ENRICHMENT_LANDMARKS_1` — Enrichment wave (review B1): the Grey Sea holds ZERO landmarks in 429 tiles and the Twilight Sea is near-bare — seamounts, wreck moorings, mat feature
- `LANDMARK_NAMING_PASS_1` — Review B2: 32 landmark names reused (worst 'Dead Sarlacc' x7) — hand-name the ~15 that matter in faction/region voice, namer variety for the rest; nee

## Commits

```
437b8b81 Port Lumi.doorsexpanded's blast doors into StarWarsPatches (BLASTDOOR_LUMI_PORT_1)
a085bf59 Mynock custom art (south/east/north): hideous wet practical-effects redesign
2ed52d77 Review C-series doc sync: one_map water bodies, world-def roster note, mutator census superseded in place; five B-series items filed for FOUNDRY
9ad92b7c Punch list: text rulings + cap roads patch + island canon + waterline owned (owner rulings, 2026-09-08)
4975090f PLAYER_START_SITE_1 ruled: Zeddo's Yard (Fall Line, tile 17007 cluster) is the formal start anchor — owner's card, 2026-09-08
afa5ac40 File PLAYER_START_SITE_1: the Hutt junkyard start — lore fixed, two candidates measured and staged (owner, 2026-09-08)
ec0694fe WORLDMAP_FINAL_REVIEW_1: the studio review report — verdict THE MAP pending 11-item punch list
6c8cf269 File + claim WORLDMAP_FINAL_REVIEW_1: the studio review plan (owner's charge, 2026-09-08)
6714f03f Ring: band-limited war-debris strip replaces the moire one (owner picked over Saturn revert, 2026-09-08)
c536d804 File GAPING_DOOM_SITE_1: dead-sarlacc waste pit at tile 2403, green-throat art spec (owner, 2026-09-08)
b92adbbd Complex-structures icons: wet-green biomes ruled out (owner, 2026-09-08)
e9c90d7b Ledger: BIOME_FREEZE_FABLE_REVIEW_1 + SETTLEMENT_REJIGGER_ROUND2_1 closed on owner's word — both already performed and adopted
d88d0117 Poison Forest: measured arc envelope recorded, owner accepted — last open distribution question closed; map distributions freeze-ready
87bea559 Sheets: fold today's ruled repaints into the receiving sides (freeze-sweep follow-through)
36952ad4 Ledger: both Propane Lakes conversion items dropped on owner's card ruling — sheet strategy is bend-the-donor; RUT_PropaneLake (lake water def) stays
9656a389 Canon CSV: sync biome column to live V26 — 5,258 tiles of un-synced repaint history (coldside re-partition, fungal merge, poison forest expansion); drift now zero, all other fields already matched
f9f65d2f Worldmap sitting: four distribution rulings landed (owner, 2026-09-08)
f91877bc File BLASTDOOR_LUMI_PORT_1: port Lumi.doorsexpanded's blast doors before retiring it
a5020486 Worldmap sitting: Propane Lakes harmony pass + Rot cold-tail repaint (owner rulings 2026-09-08)
ddad4e68 Armoury: regen Armour_Leather.xml and Armour_Ratings.xml, confirmed real drift
d1c2c008 UTINNI_SHELL_DEFNAME_BUG_1: root cause is upstream (VBE), cosmetic only
e9304377 Ledger sync: Propane Lakes picked as next biome conversion — SELF_CONTAINED_BIOME_1 + WORLD_SWITCH_1 filed for FOUNDRY; bridge taken for worldmap sitting
cdd3b907 LanternDeeps: declare the two host-biome mods GenStep_ScatterCavePortal checks for
618f9486 RaidRedesigner: guard PropertyEngine.Fire, don't hard-declare it
555ef84b StarWarsRaces: guard DefModExt_HeadTypeStuff with MayRequire=neronix17.toolbox
ef628781 Oracle: rewrite transport to shell out to claude -p, per owner's 2026-09-05 ruling
dcaa6b5b BENCH reboot handoff: consolidation sitting closed, worldmap sitting next
1a6feb62 LIVE.md: MODERN GAME baseline recorded on owner's ruling — V24 world + gravship f + 590 roster + dump caveat; 08-20 dump ruling superseded in place
d28b8756 Ledger: bridge released after save-migration window
8508685e Sprint: world V24 + gravship f migrated to consolidated names, live-proven, re-saved; saves pruned to 4 keepers
457d21f5 Relabel 19 donor biomes to their campaign names (label-only)
88320c2f Maturity registry refreshed post-consolidation: 22 retired, 10 recalibrated, 3 registered — 58 systems; dashboard republished
624417ad Dashboard: By Tier stacks under Content ladder; ladder row is two columns
c8b0baff File ARMOURY_LEATHER_RATINGS_REGEN_STALE_1: Armour_Leather/Ratings regen drift
11dcd56f Armoury: deterministic own-vs-donor attribution tiebreak in gen_armour_patch.py
61fb5e00 Ledger sync: dunes design close + build item + bridge events
ee1ae82c Maturity dashboard: widen main cap 1360→1860 (grid was starving on wide screens, underlapping the rail) + visible scroll hint when the grid still overflows
f7e19f50 MOVING_DUNES_DESIGN v2: rulings folded — source/sink edges (map as window on endless desert), per-map tinted sand layer deliverable, 1.1-1.4k line estimate
c454ffde Desert wraps design capture (words-only, pre-unsubscribe): grayscale stuff-dyed wrap language per body type + the gene-headtype closed-loop mechanism
5a902765 Dunes: 6 owner rulings recorded — build confirmed, tunable pacing, edge-flow design owed, generic release via material skins
0188c925 Cherry Picker: cut Blizzarisk (R20 owner ruling - donor creature, not canon)
1f144a38 PawnFlavor: regen behind two generator fixes; unconditional RSW_ alias fallback
e3c27857 MOVING_DUNES_DESIGN: verdict worth-building in cut form — Odyssey ships ~80% of the substrate; v1 = sand-only Werner transport + burial caches, ~1k lines C#
ac913026 DESERT_WRAPS_ART_COMMISSION_1 filed: original wraps + devolved head, candidates-first, three-tier placement plan
ac9ad21b File MOD_LICENSE_PERMISSIVE_1: CC0-1.0 across every mod we author
0a684d2c Add zylle.sandcastles to the stack (owner: too cute for a Jawa playthrough) — slotted before the patch block, 590 active
6a582966 patch_provenance: Recorder.record() must reject -1 the same as None
01bfcd07 MOVING_DUNES_ENGINE_1: owner's aeolian-transport spark captured verbatim, design-first
e4bc48e6 Lesson: -- inside an XML comment is illegal and RimWorld rejects the file
2b29b3cb Pyrelands is a real biome: RM_FE_Pyrelands + EmberGrass + AshFall + Cinderfall, worker+ashfall C# (0W/0E), world tile — self-contained per owner ruling
6d55d099 Armoury About.xml: fix illegal '--' sequences inside XML comments from 23729555 — file was unparseable, deploy refused it
e4ea2a9f Armoury About.xml: fix illegal '--' inside XML comment from 23729555 — file was unparseable, deploy refused it
0fbc0e14 SeasWaterline folds into SWBestiary (owner ruled: fauna cell owns the seas wiring) — Lane 1 patch + 5 carried loadAfter deps; id removed from both configs (590→589)
f1836ee6 Armoury: require an energy signal before heavy/cannon/repeater promotes a rung
2502b401 Three owner rulings landed: spine kind nodded, theft attribution (pet steals, seen order blames colony), Pyrelands tile switch before freeze
23729555 Fix stale/missing loadAfter declarations across 6 mods
20a1643a SovSith Misc stub retired (VERIFY row 104 resolved: distinct, consumerless, collision-prone); Pyrelands self-contained biome item filed on owner's ruling
3e67e817 Decouple item file backfilled with owed verifications; two sprint lessons filed
35e0756c Chronicle spine implemented: Aftermath-Ninefold decoupled — reflection both ways, zero compile-time refs; builds 0W/0E, selftest 11/11
6c2c8bd9 PROOF LOAD PASSED: runbook closed, root cause recorded on the item; Pyrelands de-campaigned (3 strings), R9 BiomeDef fork escalated; animal-theft spec drafted
fc103b59 Sprint root cause: dedupe kept donors' EARLY slots — patch catch-alls fell 582→188; lists rebuilt, destination keeps own slot else last donor's
18376015 SWBestiary: fix two latent Livestock-era bugs the merge surfaced — skillRequirements li-form (parsed 'li' as a SkillDef) and dead leatherLabel field
9be5b728 Proof-load failure signatures written before launch
655b53e4 Holds follow their moved files; sweep leftover state edits on owner's word ('all uncommitted work is now yours to commit')
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     worldmap sitting with the owner

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M Transient/codebase_health_hook.log
 M Transient/project_maturity_dashboard.html
 M Transient/project_maturity_dashboard.json
 M Transient/ring_debris_candidate.png
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
?? "D:\\Luke\\dev\\Rimworld\\Transient\\bench_tools_dump.json"
?? infrastructure/state/CODE_REVIEW_STATUS.json.lock
?? infrastructure/state/codebase_health_last.json.lock
```

