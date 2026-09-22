# MACBENCH_REBOOT_HANDOFF_202609221537 — READ FIRST on wake

Follows `MACBENCH_REBOOT_HANDOFF_202609162042`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
🔴 **Check whether a system already exists before designing one — it corrected my premise FOUR
times in one session, twice publicly.** Every correction came from measuring rather than
reasoning, and each would have shipped a wrong design:

1. `SEA_FLOOR_AND_CATCH_PASS_1` nearly became a new fish programme. `FISH_BESTIARY_BUILD_1` is
   open, ratified, six waves in, 32 species across 7 waters, with every question already ruled.
2. I stated the Twilight Sea has no `fishTypes`. It has **9 catches on correct `saltwater_*`
   bands** — in `Patches/BiomeFishTypes_TwilightDeep.xml`, not on the def. Scanning BiomeDefs
   only is how you miss a patched-in table.
3. I suspected the Scald's `freshwater_*` bands were wrong for an ocean terrain. That was tested
   LIVE by wave 5 and the truth is different: the deep water is `Saltwater`, but the **intended**
   fishing spot is the freshwater shallow cove `RUT_ScaldMargin`, which matches the bands — and
   which **has never been painted on the planet**, so a Fishing zone is refused on 100/100
   cells. The wiring needs no change at all.
4. The swarm mechanism his shoal ruling seemed to require already ships: `SeaBeasts_Swarm.xml`
   holds three, and `RSW_Mee` ("a silver-blue **schooling** scalefish") is already wired as one
   spawnable floor animal in the Scald.

🔑 **And a number the same discipline caught:** a naive donor-name scan reports **182** stale
roster rows. The real figure is **32**. The other 150 are bare Star Wars names (`Kreetle`,
`Bantha`) that resolve fine against an ACTIVE donor. Only the `BMT_` subset is dead, because
only `biomesteam.biomescaverns` is inactive. An alarming round number is a query bug until proven
otherwise.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1. 🔴 **The `RSW_Stoneback` collision was TWO different animals sharing one defName** — bokka
   (bodySize 0.4) and korrum (4.00) — so one did not exist in the shipped game and nothing said
   which. Resolved on your sheet ruling: korrum → `RSW_Korrum`, both placed, one home each.
   **Root cause is a guard that did not exist, not a careless port:** the 349-duplicate sweep
   closed *"0 duplicates"* at 10:50 PDT on 2026-09-20 and the desert port reintroduced one at
   **17:35 PDT the same day**. Built the missing guard
   (`selftest_no_duplicate_defs.py`), verified by re-introducing the original bug.
2. ⚠️ **Two numbers in the files are mine, flagged for overrule.** `RSW_Korrum` into the
   Scarlands at **0.05, not its roster's 0.5** (that roster is the thinnest at 8 species and the
   weakest pyramid at 53% small; 0.5 makes a mountain-sized crab a quarter of all sightings).
   And the Wasteland's row read as the bokka rather than the korrum.
3. 🔴 **The cave lemming breaks the food-pyramid law on your explicit ruling**, and the Nightside
   Ice `wildAnimals` block now says so in as many words — bodySize 1.0 at 0.03 takes that biome
   from ~69% to ~42% small. You were shown the cost and chose it. ⛔ Nobody should "fix" it.
4. **`FISH_BESTIARY_BUILD_1` cannot pass its own verify today**: it requires
   `RUT_MeeCatch`/`FaaCatch`/`LaaCatch` as ours rather than Mlie's `swfish_` defs, and **none of
   the three exists**. The animal half is already live, so this is the cheapest possible proof of
   your new pairing rule.
5. **Deleted on your ruling**: `StructureInjectionsRUT/Source/Defs` (4 files). Verifying per file
   earned its keep — 3 were byte-identical but `QuestScriptDefs/RUT_VaultThaw.xml` was stale AND
   wrong, still carrying the `rootSelectionWeight 1.0` that `VAULT_THAW_FIXED_TILES_UNFIREABLE_1`
   had fixed to 0. A file I had called harmless dead weight was a latent regression.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `SEA_FLOOR_AND_CATCH_PASS_1` — filed, ruled, nothing built; **NEXT: build
  `RUT_MeeCatch`/`FaaCatch`/`LaaCatch`** as our own items and wire them, reading
  `design/Jawa/worldbuilding/fish_bestiary_commission_2026-09-10.md` for which water's register
  each belongs to (do NOT infer it — `RSW_Laa`'s adult home is unconfirmed, and the Miasma holds
  the `*Juv` nursery forms). Deliberately not started at the tail of this session.
- `ROSTER_DEAD_BMT_NAMES_SWEEP_1` — filed with full per-species evidence, 14 rows; **NEXT: move
  `BMT_Megakrill` and `BMT_CrystalCrab` into their rosters' `evictions`** (pure bookkeeping — one
  is a fishing result by its own law, the other is evicted by the Deeps sheet's ban 3), then take
  the sea surface-vs-floor question, which your two-defs ruling has now largely answered.
- `BIOME_SPECIFIC_FAUNA_LAW_1` — filed, 52 multi-homed species measured, nothing adjudicated;
  **NEXT: bucket the 52** (flier / juvenile-line / twin-or-alias artifact / genuinely duplicated)
  and publish the buckets before changing anything. The law is STRICT — see the trap below.
- `STILLSAND_KORRUM_HOLE_1` — filed; **NEXT: search the unplaced cast and the canon library for a
  large dune-sea animal** before designing one, and do not repeat the korrum's armoured-plodder
  niche, which is the Scarlands' now.
- `KORRUM_ART_REGEN_1` — filed, blocked; **NEXT: after ~2026-09-26T19:52 UTC check
  `artpipe/registry.jsonl` for the three re-keyed `RSW_Korrum_*` jobs**, land them under our own
  Textures path, and repoint all three `lifeStages` entries.
- `STONEBACK_BOKKA_ART_STANDARD_1` — filed; **NEXT: LOOK at the bokka's three facings and state a
  verdict.** He asked a question, not for a regen.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
1. **A `git add` with explicit paths does not stage a DELETION you forgot to list.** My commit
   `4b068ea5d` added three re-keyed art jobs but left the three old ones in the tree, so HEAD
   carried SIX queued jobs where disk had three — a daemon on a fresh clone would have generated
   korrum art twice, once under the bokka's defName. Found only because he said "check". **Diff
   HEAD against disk after any rename-by-recreate** (filed: LESSONS_INBOX).
2. **A duplicate-defName scan over-reports unless you key on def TYPE.** Mine said 32
   collisions; 6 were ThingDef/PawnKindDef pairs legitimately sharing a name (a PawnKindDef has
   a `<race>` element, which is what fooled the filter), and 30 were a dead def tree under
   `Source/`, which RimWorld never loads. Exactly **one** was real (filed: LESSONS_INBOX).
3. **`--owner-said` is checked against the session transcript, and a question-card LABEL is not
   his words.** I wrote "RM_GelatinousSlime survives" into two files as a verbatim quote; it was
   my option text, which he selected. `block_forged_owner_said.py` caught it at the rimflow call.
   A card selection IS a ruling — record it as "decision taken by question card", never as a
   quote (filed: LESSONS_INBOX).
4. 🔴 **NEW — a card answer can be narrower than it reads, and I over-applied one.** "Any arid
   biome where it's needed (desert, extreme desert, or other hot arid day-side)" is a CANDIDATE
   set, not an assignment: *"you are not understanding. I meant pick one arid home."* A shared
   habitat class is **not** an in-game reason to multi-home an animal. Recorded in CLAUDE.md and
   in `BIOME_SPECIFIC_FAUNA_LAW_1`, because the 52-species adjudication turns on it.
5. **NEW — `measure` is not executable on this Mac** (`permission denied`), and there is no local
   def dump, so "does every roster species resolve against the live mod list" is UNMEASURABLE
   here. Said so on the item rather than closing it (filed: LESSONS_INBOX).

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (0) — the next seat's queue

Nothing filed in this window.

## Commits

```
4f7b2fbd1 The sea pairing rule is ruled, and it needs no new mechanism
818d37dc3 SEA_FLOOR_AND_CATCH_PASS_1: the floor half is the gap, not the catch
0a49085fc Delete the dead vault def tree, and record when a roster hole gets filled
576abc14c One arid home each — correcting BENCH's misreading, and a commit that lied
6302f2bc1 File the two art follow-ups from his sheet notes
15eeb382c Close STONEBACK_DEFNAME_COLLISION_1, and build the guard it needed
4b068ea5d The korrum becomes RSW_Korrum: collision resolved, both animals placed
864ebe307 Picker sheet for the stoneback identity collision
30a6fdba0 RSW_Stoneback is two different animals on one defName — blocks a ruling
28ef99344 Wire the cave lemming into the Nightside Ice, breaking the pyramid on purpose
b2927cab7 Two standing rulings: one animal one biome, and a sea owes floor AND catch
f54dd59d8 chore(sync): laptop 2026-09-21T23:50:42-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 3 more
b9468c87d File ROSTER_DEAD_BMT_NAMES_SWEEP_1: the 14 rows that need judgment, not a sweep
b173e699d The dead-donor-name defect was never three rosters — it was twelve
37989ba8a CLAUDE.md: a review sheet's cut is scoped to that sheet's biome
429446d0d MIASMA_FEVERWOOD_GREENTIDE_BMT_1: the last two, under a new standing ruling
255ecbd77 MIASMA_FEVERWOOD_GREENTIDE_BMT_1: 5 of 7 were stale names, not real defects
c5a06e6fc rimflow: close SLIME_STANDALONE_MOD_1, move prose to items/closed/
1197642c9 Slime twin ruled, and two stale status claims removed
8ecaf515b chore(sync): laptop 2026-09-21T21:46:49-07:00 — infrastructure/state/facts/biome_paint_list.md
... 610 more: git log --oneline 33521b93e..HEAD
```

## Game / bridge / tree state at wrap

- Bridge: FREE    since 2026-09-18T03:58:39Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   automated health publisher (rimflow-triggered regen), not hand-edited — not mine to commit
 M Transient/codebase_health.json   automated health publisher (rimflow-triggered regen), not hand-edited — not mine to commit
 M Transient/codebase_health_artifact.html   automated health publisher (rimflow-triggered regen), not hand-edited — not mine to commit
 M infrastructure/dashboards/hub/data/health.json   automated health publisher (rimflow-triggered regen), not hand-edited — not mine to commit
 M infrastructure/state/codebase_health_last.json   automated health publisher (rimflow-triggered regen), not hand-edited — not mine to commit
 M infrastructure/state/queue/FOUNDRY.md   rimflow's own queue-snapshot regen from my filings, not hand-edited
```

