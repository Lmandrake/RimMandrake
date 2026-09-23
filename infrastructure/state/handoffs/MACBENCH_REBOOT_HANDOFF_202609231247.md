# MACBENCH_REBOOT_HANDOFF_202609231247 — READ FIRST on wake

Follows `MACBENCH_REBOOT_HANDOFF_202609230538`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

🔴 **This project has built far more than its own documents admit, and the cheapest first move in any
design pass is to read the source.** Four times in one session a thing the owner proposed as new turned
out to be shipped, and once it was the centrepiece of his own idea:

- His *"special oil to permanently seal a portion of the tree so it will not grow back"* is
  **`RM_ToxinSealant`** — an item crafted at a machining table plus a terrain, with
  `RM_MapComponent_LivingRegrowth` **already gating regrowth on that terrain**. Its description already
  reads *"The living wood beneath cannot push through it, or close the cut you made."* Permanent
  habitation inside a greatbole works **today**.
- The grubs' two behaviours are `RM_EatCleanableExtension` (forage named items, fires for **wild** pawns)
  and `RM_ParentalEnrageExtension` (guard a thing, scoped rage, no warning) — one axis widened each.
- Their tribble breeding is `RM_CompVerminBreeder` + `RM_MapComponent_VerminPopulation` + its alert, which
  already ship interval breeding, soft/hard caps and an **aggression curve that ramps between them**; the
  only gap is that they do not gate on food.
- The 40/60/70 thresholds need **no new tracking**: `BoleRecord.footprint` + per-cell `timers` are already
  Scribed.

⇒ That turned "build a large feature" into "finish how it looks", and it is why the greatbole spec lists
**four of six mechanisms as already built**.

🔑 **And the same held for CONTENT, three times.** The flora roster had already written where the wasps
live (sarquin's *"the drip is why insects are there"*), where the ant hive's farm comes from (raids hauling
thornbugs away **alive**), and which plant supplies the sealant's reagent (gorbeleth's *"its toxin is worth
extracting, which means going close"*). ⇒ **Read the roster and the source before inventing — this project
keeps having already answered the question.**

## What the owner should see

1. 🔴 **I told him the artpipe queue was empty. It held 182 jobs.** I counted `artpipe/queue/`, which does
   not exist — `ls` on a missing directory pipes nothing to `wc -l`, so the answer was a confident 0. The
   real path is `artpipe/pending/`. ⚠️ **And the daemon is not running on this laptop**, so the 18 Greentide
   jobs generate nothing until the Desktop runs it. He chose to leave the desert wave ahead of them, so
   jungle art is genuinely days out and the 22-row legibility review waits on it. (filed: LESSONS)
2. 🔴 **His *"how this became a Deep Drill I have no idea"* has an answer, and it is a real defect in shipped
   content.** The blob (`RUT_GreatboleHeartwood`) is a `RockBase` mineable carrying its own flat-colour
   placeholder. The retinted `DeepDrillPowered` sprite is on `RUT_GreatboleCore`, the **1×1 bookkeeping
   marker**, which draws at **7×7** — so a recoloured mining drill renders across the middle of the wood.
   ⚠️ I got this wrong twice before measuring it (first "the landmark has no art", then "the landmark is a
   drill"). `GREATBOLE_BARK_EDGE_ART_1`.
3. ⚠️ **One part of the song he specified may not be achievable as described.** Dissonance from two
   overlapping sustainers is safe; a true **beat frequency** needs two tones a few Hz apart holding a phase
   relationship, and engines commonly randomise playback phase. Fallback is baking the beat into a single
   authored file. ⛔ Nobody may report the live two-layer version as working until he has heard it.
4. 🔴 **A tier problem I flagged and did not decide.** `RM_Greatbole` (the mature fellable giant) is
   franchise-free tier; the ancient form it grows into, `RUT_GreatboleCore`, is **campaign-only**. So a
   free-mod player grows greatboles that can never become the landmark — contradicting his own ruling that
   the free mod looks the same *"save for any star wars beasts"*. "Greatbole" is an invented name, so nothing
   about it needs to stay behind the campaign layer. **Unruled; he needs a card.**
5. **`GREENTIDE_RM_MOD_BUILD_1` step 4 closed with nothing owed.** Its five "genuinely owed" files were all
   XML comments or a deliberate non-patch block, and `gen_cast_patch.py` has zero Greentide occurrences. The
   real gap is a different item: `RM_Greentide`'s own `wildPlants` still holds the six vanilla rows he
   rejected (oak, poplar, bush, grass, tall grass, berry), blocked on the fire measurement.
6. **The humming grove is written but NOT compiled**, and one call in it is unverified — the member that
   reads `Find.CameraDriver`'s position. It is isolated in one method and fails silent rather than throwing.

⚠️ **Twice in one session I turned a loosely-framed question of his into a decision that did not need
making** — the Star-Wars-naming tier question (previous handoff) and then the anima/servants question, where
he had only meant "both, as mod options". Recorded in auto-memory rather than here, since it is about how he
works rather than about this repo.

## What is half-done, and where it stops

- `GREATBOLE_HARVEST_LADDER_1` — fully designed across four card rounds, **nothing built**, 14 unmeasured engine questions; NEXT: on the Desktop answer spec §10 question 1 — **whether a plant's growth rate can read adjacent terrain** — because the seed's water requirement (§3c) rests entirely on it and it is the one piece that could come back "not expressible".
- `GREATBOLE_BARK_EDGE_ART_1` — filed, nothing done, and the bark edge is the greatbole's only genuinely *missing* mechanic (`graphicClass` is `Graphic_Single`, no edge-vs-interior distinction at all); NEXT: on the Desktop **read a live vanilla rock ThingDef and whatever `RockBase` supplies** to learn how its outer edge differs from its interior — ⛔ before commissioning any art, because the wrong number of PNGs is the expensive mistake here.
- `GREENTIDE_HUMMING_GROVE_1` — built, registered in the csproj, selftests unchanged at 61/73, **not compiled**; NEXT: **confirm the `Find.CameraDriver` position member** on the Desktop, fix the single marked line in `TryGetListenerCell`, then compile.
- `REACTION_MECHANISM_GENERALISE_1` — designed, nothing built, and three items are queued to duplicate it; NEXT: **build the event object, the shared budget and the spawn response under the wasps**, whose failure mode is measurable rather than subjective.
- `GREENTIDE_WASP_SWARM_1` — designed (`RM_Skerrel` + its gall, hosts named, flight via the stat), nothing built; NEXT: **measure whether many tiny pawns are affordable at all**, since that can kill the feature rather than shrink it.
- `GREENTIDE_JUNGLE_TREE_ROSTER_1` — art gate CLEARED, 18 jobs queued behind 182; NEXT: when the art lands, **build the 22-row map as a savegame with a grid key** for the legibility review he owes an eye on.
- **The greatbole tier problem** — flagged in two places, unruled; NEXT: **card him on whether `RUT_GreatboleCore` moves to `RM_` tier or the free mod gets its own**, noting the genstep that places it must come along either way.
- `SEA_FLOOR_AND_CATCH_PASS_1` / `DUPLICATE_CANON_DEFNAME_PAIRS_1` — genuinely Desktop-only, untouched for a third session; NEXT: read `MACBENCH_REBOOT_HANDOFF_202609230538` for their state, which is unchanged.
- `ROSTER_DEAD_BMT_NAMES_SWEEP_1`, `KORRUM_ART_REGEN_1`, `STONEBACK_BOKKA_ART_STANDARD_1` — inherited across three handoffs, still untouched; NEXT: **work one or drop it** — carrying them a fourth time is exactly the pattern this ritual exists to catch.

## Traps learned

1. `ls <nonexistent-dir> | wc -l` returns **0**, not an error, so a queue check against a guessed path reports "empty" with total confidence — 182 jobs invisible (filed: LESSONS).
2. An art brief's `style_notes` can name a reference image **that does not exist**; only the `reference` field is existence-checked (filed: LESSONS).
3. A question-card option **label** he clicked is our sentence, not his — the forged-quote guard is right to refuse it; record a click as "decision taken by question card" (filed: LESSONS).
4. That same guard reads **commit message bodies**, and being `PreToolUse` it refuses the **whole compound command**, so a chained write-then-commit loses the write too (filed: LESSONS).
5. `RM_CreatureBehaviors.csproj` sets `EnableDefaultCompileItems false`: an unregistered `.cs` **compiles into nothing, silently** (filed: LESSONS).
6. Renumbering a document's sections breaks cross-references in **other** files, and a mechanical remap can land a ref on a real-but-wrong heading (filed: LESSONS).
7. `handoff.py` needs `AGENT_SEAT=MACBENCH_REBOOT`, not `MACBENCH` — the seat must match the handoff **filename prefix**, and the short name silently reports "nothing to wake from" instead of refusing (see: this file's own name).

## Commits

```
3786f8808 Fix two refs the spec renumbering left stale in the item
c77c37fef The anima and servant crossovers are player options, not a choice I had to make
c94ebd6e9 chore(sync): laptop 2026-09-23T05:36:46-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
e53409205 Fruitfall completes the fruit economy, and the pilgrims come for the song
853512439 The greatbole harvest: three thresholds, and the sealing oil he invented already ships
655401067 chore(sync): laptop 2026-09-23T04:35:19-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
c9add991c The humming grove built generic, with the one unverified call isolated instead of guessed
ad481b94b The greatbole he described is already built, except the bark edge - and the drill is the marker
7bd58f4a8 Two traps from tonight: a count of zero that meant a wrong path, and a reference image that does not exist
8b78ea48d All 18 Greentide flora art jobs filed, and the landmark has no art to match
288e3c4c0 chore(sync): laptop 2026-09-23T00:29:19-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
19083cb2b The Greentide migration's remaining work was five files that turn out to be comments
769d4dd57 The wasps designed, and the roster already said where they live
e0a8fbc83 Four items were about to build one mechanism, and per-source limits are why chains run away
f4f107031 The roster now matches his size rulings, so art is unblocked - and the doc was arguing against them
8596307c2 The jungle exchange binds, and the provenance guard was right to refuse my first try
0e8369254 Three more rulings, and one of them moves the risk from the hazard to the tool
c91a52307 Four owner rulings: the jungle gets wasps, the Frenzy gets a shelf, the amoeba dies
```

## Tree state at wrap

- upstream: origin/main, pushed

Working tree clean.

