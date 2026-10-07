# BENCH_REBOOT_HANDOFF_202610070103 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610061302`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
This window was a cleanup-only wake after a logout. Nothing new was built. The real loss risk was the predecessor's tail: 8 local commits (6 already on origin under other hashes), uncommitted ledger and art-ledger state, and 185 sheet webps referenced by committed sheets. All of it is now pushed (`8e66c9842`, `6d2fce793`). ⇒ On any wake after a logout, run `git status -sb` against a fresh fetch before trusting the handoff's "everything pushed" line.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- The game is RUNNING, but the Grey Sea floor-density fix (`d97142596`) is NOT deployed. I couldn't find the DivingInteraction DLL anywhere under the game's Mods folder, and Player.log lacks the "densities were reset by another mod" line. Testing it needs a close → compose → cold load, which is his call while he may be playing.
- Untracked and left deliberately: `Transient/flowworks_playtest_review_2026-10-06/` (61 GPT-bundle extracts), `Transient/northstar_review_2026-10-06/` (5 extracts), `Transient/canon_owed_batch{1,2,3}_2026-10-04.txt`, two `.serve.log` files, `Transient/modcheck/fixtures.json` and `Transient/player_missions/CURRENT`. All are derived or program-read caches, so none needs committing.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `FLOWWORKS_PLAYTEST_CAMPAIGN_1` — filed this day; runner (8 scenes), pit ladder fix, artboard live half and GSS B-fuzz are committed (d8fafb5d0, ae66c2d73, 42d1b8edd, 2fabd2d06), but the campaign log `design/RimMandrake/flowworks_playtest_campaign_2026-10-06.md` stops at the artboard offline half; NEXT: append those four results to the log's finding/method table, then run the runner's full recipe live.
- `GREYSEA_FLOOR_PASS_1` — fix committed, not deployed; NEXT: with the game closed run `deploy_custom_mods.py --compose biomes --apply`, launch, run `python.exe src/RimMandrake/DivingInteraction/northstar/run_grey_floor_live.py`, expect flora/cast GREEN.
- `SHEET_DONOR_COLUMN_FALSE_PASS_1` — untouched; NEXT: export `ours`, count an owner-purged donor original as shown-and-rejected, rebuild Abyss/TheRot/Feverwood/WeepingStones.
- `BIOME_FLORAFAUNA_ART_REVIEW_1` — Grey Sea, The Chill, Twilight Sea, Webwork, The Scald ready to sit; NEXT: rerun `scaled_review_gate.py all` after the art queue drains and list PASS sheets for him.
- `FLYER_FLIPBOOK_ART_1` — 48 Pyrelands frames pending; NEXT: when they land, rebuild the Pyrelands sheet and take his flight pick.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A handoff's "everything pushed" is a snapshot: a logged-out session committed 8 more and pushed none (see: this handoff).
- zsh treats a bare `echo ===` as `=` expansion and aborts the whole compound command with `== not found` (see: this handoff).

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (1) — the next seat's queue

- `FLOWWORKS_PLAYTEST_CAMPAIGN_1` — FlowWorks bugs via new test methods + rich-screenshot art pre-review; method-per-bug-class data

## Commits

```
6d2fce793 Sheet renders referenced by the committed biome sheets (185 webp, left untracked at logout)
8e66c9842 BENCH state: ledger bridge events, art ledger events and sheet snapshots left uncommitted at logout
566b06f68 Campaign log: artboard offline half + first real trial
e9c9984a5 Campaign log: GSS scoping (owner-found defects were all visual)
ea51294cf Review batch 10: nine files marked clean after fresh full reviews (shade grid, tether pull, watchers, Warscar/RustCathedral/TerminalBiomes settings, pilgrim camps, Unfinished Line tithe patch)
fe6140ff4 Review batch 9: middens, foundry spunstone parts, spunstone study and tree-fall utility clean
490988350 UNFINISHED_LINE_TITHE_BEAT_1: beat 4 'The Tithe and the Hands' - Enclave shuttle waits for the tithe and a Crafting 8+ colonist lent 10 days; 6 settings (PROVISIONAL); Harmony dependency added; site delivery awaits UNFINISHED_LINE_SITE_CHOICE_1
bb7b2cecf LongShade validation: five creatures/plants moved to other biomes on the 2026-10-04 sheet are checked in their new homes, not flagged missing from the Long Shade roster
2a704a08e LONGSHADE_MIDDENS_DESIGN_1: midden heap, vrekka builds and tends heaps, colonists search for vanilla items, 2 toggles (PROVISIONAL); settings screen reachable; map-gen seeding and clean-patch warning not built
3666db8a6 FORGE_SPUNSTONE_SOURCES_1: foundry salvage cache becomes a second spunstone study source (guarded patch, tickerType Rare; offline-applied only, def is in DEPLOY_HOLD)
dc097d11a Review batch 8: shade-grid light layer no longer doubles light after a toggle and no longer cancels shade-gear cover; Solar Mirrors, ledge refuge and sun-heat math clean
19f4d8374 FORGE_SPUNSTONE_SOURCES_1 (part): floatstone door and floatstone-only spunstone hull wall, both gated on spunstone bonding with their own toggles (PROVISIONAL); salvage-cache source needs a UtinniPatches patch, beam awaits a ruling
82f8e7ea1 Settings screens fixed in the remaining 25 rows (wave 3): scroll view + one-column flag + measured heights; sweep table complete
99b61e39b Solar Mirrors uses a real light-layer hook in CreatureBehaviors' shade grid (IRM_LightLayer) instead of patching its internals; per-tick allocs, world-map drawing and stale-cache bugs fixed; behaviour with no subscriber unchanged
c992f1cb2 Review batch 7: flushing a tamed watcher no longer hunts the colony's pet; a hungry watcher no longer loops hide/emerge; 8 files clean
384baa9eb Bacta: add the missing .dll.srchash stamp for the rebuilt DLL
0c8060355 Settings screens fixed in 12 more mods (wave 2); 25 lower-priority rows remain in the sweep table
e7f68adf0 GLOOMCAST_WAKE_RIDERS_1: tebbra and gennok follow the gloomcast shadow (search radius 60 borrowed, PROVISIONAL; live follow check owed)
3858dbb01 Settings screens that hid their lower sections fixed in 12 mods (one-column flag / scroll view); table of the remaining ~32 at risk in Transient/settings_overflow_sweep_20261006.md
e2edd5cc3 CRACKEDLANDS_LEDGES_OF_MERCY_1 (part): form-independent refuge-ledge and chime-anchor markers; neutral visitors and trained animals run to a ledge from the first warning until recede (PROVISIONAL); ledge defs and carvings await the physical-form ruling
... 94 more: git log --oneline d0ea42029..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-06T19:31:49Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
?? conversations/   hook transcripts, never committed by a seat
```

