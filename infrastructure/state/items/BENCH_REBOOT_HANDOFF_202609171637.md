# BENCH_REBOOT_HANDOFF_202609171637 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609160549`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

🔴 **The north-star system cannot GREEN anything today, and no view says so.** `shows=` — the
marker by which a component claims a bar — appears in **0 of 17** `validation.py` files, MEASURED
twice independently (BENCH by grep, and the determinism assessment separately). So the 44 bars
binding across the four VALIDATED mods are **44 bound, 0 covered**: every `modcheck run` of a
validated mod returns REFUSED before the game is ever consulted. The machinery is specified,
hash-protected and judge-wired, and structurally cannot pass a mod.

🔑 **What this means for the work the owner just ordered:** authoring more bars adds refusals, not
coverage. `NORTH_STAR_PIT_PILOT_1` is the falsification test for the whole design and its second
half has never run. It is Desktop-only. **Do not treat any GREEN in `modcheck status` as
meaningful** — it prints `FluidCanals GREEN` for a mod that does not exist and `FlowWorks NEVER
RUN` for the one that does, because the summary reads a stored field while the detail re-derives.

And the sharpest instance: **`Pits`' checklist is VALIDATED with 12 binding bars against
`src/RimMandrake/Pits`, which holds only `__pycache__`** — the mod was merged into FlowWorks at
`cade628c1`. One of his four approvals points at nothing.

## What the owner should see

**1. THE GRID — his next step, and it needs the Desktop.** He asked for a grid of naked species
facing south, screenshotted. ⚠️ **A deploy comes first**: everything below is in the repo, and the
game reads `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`. The grid now tests
THREE things in one trip: the 7 skin-colour corrections, whether the 29 shader-flag removals make
faces tint, and which species still look wrong.

**2. He is verifying the canon dossier by web search himself.** `Transient/canon_appearance_dossier.md`.
His words: *"I will manually confirm with a web search."* If a citation fails his check, the matching
skin change is reversible in one commit. Best-sourced three, which he intended to check first:
Ithorian, Bith, Zygerrian. ⛔ **One claim is OURS, not canon** — Umbaran lavender-violet exists in
no text; it is an agent's read of one painted illustration. He was told, and the sourced "pale and
bluish" was shipped instead.

**3. Shipped with a flag raised, and he can veto it:** 29 `useSkinShader=false` removals
(`bb51a1aac`). This is a **hypothesis**, not a proven fix — the flag's presence is measured byte
for byte and the textures in pixels, but its render-time behaviour lives in a third-party mod
(`TabulaRasa`/`neronix17.toolbox`) absent from the laptop. The grid settles it. Reverts as one file.

**4. The de-duplication he ordered is 5× what he was told.** I reported "three duplicate pairs";
MEASURED, it is **30 walks pointing at 9 folders** (7 at SWBestiary, 6 at MandrakePatches). He
chose "repoint AND de-duplicate, then author" — the repointing landed (`071a4e667`), the
de-duplication has not. Only one north star per folder can ever bind, so this blocks authoring.

**5. The art selftest regression is NOT this window's.** Suite went 43/54 → 42/54 with
`selftest_art_checks.py` newly failing. Stashing the head-flag change leaves the identical failure.
It tracks the other window's in-flight creature art (`86ed9a960`, `bd9a1b8ee`, `9e7e773a0`) —
that selftest exercises Gizka, Anooba, Nuna, Orray, Zeer. Recorded, deliberately not touched.

**6. `infrastructure/DETERMINISM_ASSESSMENT.md`** answers his "pull LLM work into deterministic
Python" question. Top three: a walk linter (**25 more tests that cannot fail**, 24 walks, runs in
0.11 s), a registry cross-check, and bar-scoped hashing (**47–57% of every validated hash is
prose**). Also found: **97 of 227 DIRTY code-review entries are dead paths**, and **27 walks whose
mod ships PNGs have no LOOK step** where a doc claimed 7.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `NORTH_STAR_WALK_AUTHORING_1` — **step 1 of 5 done, step 2 done, step 3 NOT done, and step 3
  blocks the rest.** Triage complete: **32 bar owed · 38 no bar · 2 uncertain = 72**, re-measured by
  BENCH not taken from the subagent. Repointing complete (`071a4e667`) — all 78 subjects now name a
  real folder. ⛔ **NEXT ACTION: resolve the 9 folder collisions** (30 walks share 9 folders; only
  one north star per folder can bind), then ask him the provenance question. That question is
  unasked and is the gate on all authoring: all four VALIDATED walks distilled their bars from a
  **verbatim paragraph he dictated**, and drafting from mechanical assertions was explicitly NOT
  authorised. The 2 `uncertain` want his eye: AshkarrFlora (15 PNGs in an `_artsrc/` scratch dir, its
  `texPath` resolves to nothing, so a flora mod ships no art) and RiverSteam (now inside the
  already-VALIDATED FlowWorks under another name — arguably not a separate walk at all).

- `XENOTYPE_CANON_CORRECTION_1` — **skin done, everything else open.** DONE: 7 species' skin
  (`f60d197b0`, `b2a800d5c`), the invented Nelvaanian sentence deleted, 29 shader flags removed
  (`bb51a1aac`). NOT DONE, in his priority order: **head art for Nelvaanian and Lasat** — he ruled
  *"prioritise by how broken it looks in play, not by citation strength."* ⚠️ **Lasat carries a RIG
  limit — digitigrade legs with prehensile toes cannot be expressed on a human-skeleton pawn. Do
  not commission legs**; retarget to best-achievable silhouette. No head gene exists for 8 of the 13
  species, so "point it at the right head" is never available — art must be drawn.
  ALSO NOT DONE: the **six aptitude inversions**, which he ruled get fixed but **each confirmed with
  him individually** — ⛔ not as a batch. And the 9 placeholder `<description>` values (Defel, Gand,
  Hutt, Kel Dor, Kubaz, Lasat, Mimbanese, Taung, Ugnaught) plus 7 wrong/absent `nameMaker`s are owed
  and need no ruling.
  ⚠️ **Zygerrian's borrowed head is defensible** — canon classes it *feline* and Cathar are feline;
  only its `iconPath` is sloppy. Do not "fix" it as an error.

- `UNSUBSTANTIATED_SPECIES_ABILITIES_1` — filed this window on his ask, **not started**. The mirror
  audit: abilities the defs GRANT that canon does not substantiate. Known starters: Rakata psychic
  genes (post-plague Rakata are Force-blind), Cerean enhanced psychic.

- **UNMEASURED and it changes the work:** whether a water-breathing gene EXISTS to assign. Four
  aquatic species lack one — confirmed absent from the xenotype file and our `GeneDefs/` — but if
  none exists in vanilla or a DLC, that is a **mechanic to build, not a value to set.** No RimSage
  on the laptop. Measure on the Desktop before scheduling it.

## Traps learned

🔴 **1. A texture glob that matches `*south*` reads the MASK, not the base — non-deterministically.**
`glob(path + '*south*.png')` matches BOTH `X_south.png` (the base art) and `X_southm.png` (the colour
mask). RimWorld masks are saturated across ~99% of pixels by convention (measured: 259,344 of
262,144), so any head whose mask got picked looked like it had baked-in colour. `hits[0]` is
filesystem order, so the same script gives different answers for identical files. **It inverted 4 of
7 decisions and I applied the result before catching it.** The tell was male and female Cathar
reporting 253 vs 0 when the two files are byte-identical in structure. **Test `_south.png` alone.**

🔴 **2. `[ -e "$path" ]` does not mean "a mod lives here".** `src/RimMandrake/Pits` passes it while
containing only `__pycache__`. My subject-path checker reported **0 failures** on that basis and
missed the single worst case in the repo. **Test for `$path/About/About.xml`.**

🔴 **3. A checker keyed to a fixed line number lies quietly.** My first sweep read `subject:` from
**line 2**; `AtmosphericBase.md` carries it on line 3, so the check passed by skipping the only file
still broken. Use the first matching line, never an index.

🔴 **4. `modcheck run` is NOT read-only — it rewrites the live `ModsConfig.xml`.** It died on the Mac
only because the Windows path is absent. **On the Desktop it would have swapped his mod list to
MINIMAL without asking.** It is a Charter expensive-list action wearing a read-only-looking verb.

**5. A negative assertion keyed to a dead identifier passes forever.** The canal walk's step 1
checked the log for the ABSENCE of an error naming a packageId retired weeks earlier, so it was green
by construction however broken the XML was. The determinism assessment found **25 more of these**.

**6. A doc's "verified against the code on <date>" can be false on the same date it claims.** The
canal walk asserted every line was verified 2026-09-16 while ruling 24 had deleted
`CompFluidReservoir` and `RM_FluidSpring_Test` that same day.

**7. Laptop-only friction, so nobody rediscovers it:** `measure` is not on PATH · `./game` is
permission-denied · `handoff.py`/`rimflow` need `RIMFLOW_SEAT=BENCH` (there is no seat profile here,
and **`MACBENCH` is NOT a valid seat** — valid are BENCH/FOUNDRY/OWNER plus legacy) · `timeout` does
not exist (BSD userland) · `rimflow file` requires `--title` and there is no `list` verb.

**8. An item's own figures decay.** `XENOTYPE_CANON_CORRECTION_1` said 5 placeholder descriptions;
there are **9**. A subagent dossier then refuted a third of that item's premises outright — Ortolan
and Mimbanese have no skin defect, Ewok's is fur not skin, Abednedo ships 8 skin genes not 0.
**Verify an item's numbers before briefing anyone with them.**

## Closed since the last handoff (1)

- `ATMOSPHERIC_BASE_LAW_CONFLICTS_1` — 872b3814e

## Filed and still open (23) — the next seat's queue

- `FLUID_SOURCE_STOCK_MODEL_1` — Give CompFluidReservoir a real volume stock per the owner's 2026-09-16 reversal - debit on fill and on pump, limited-vs-limitless by map-edge contact,
- `CANYON_FLOOD_ERASES_CANALS_1` — A canyon flood permanently erases a dug canal - RM_MapComponent_CanyonFlood.StartFlood writes SetTerrain over every flood cell and RecedeFlood convert
- `TEMP_TERRAIN_DLC_GATE_1` — DESKTOP FIRST TASK - can we ship our OWN temporary=true terrains? Every base-game temporary terrain is MayRequireOdyssey, which is why FloodedCanyon w
- `STALE_RENAME_GATE_SWEEP_1` — Sweep the dead NAMING_SCHEME_EXECUTION_1 rename gate out of ~10 design drafts (item closed 2026-08-31 at 54a8e28d); also fix liquids_framework_design.
- `AFTERMATH_DEAD_LETTERS_1` — Aftermath's payload letters never reach the screen: letterLabel/letterText declared at RM_AftermathRuleDef.cs:56-57 and read NOWHERE, so all 8 rules a
- `SALVAGECLAIM_WALK_STALE_1` — design/validation_walks/RimMandrake/SalvageClaim.md names a subject that no longer exists (src/RimMandrake/SalvageClaim is gone, consolidated into Rim
- `GRAFFITI_VANDAL_ART_REGEN_1` — Regenerate all 6 RM_Graffiti_Vandal variants as punk/urban marks with ZERO real-world lettering (vandal_0.png ships the donor author's legible tag 'TA
- `GRAFFITI_WARNGLYPH_INUNIVERSE_1` — Replace RM_Graffiti_WarningGlyph's 2 sprites: the modern ISO hazard triangle becomes an in-universe glyph (Aurebesh character or Jawa clan mark) - own
- `GRAFFITI_VARIANT_COUNTS_1` — Graffiti variant counts are lopsided 6:2:2:2 - Scratches, TallyMarks and WarningGlyph have only 2 variants each so Graphic_Random repeats visibly on a
- `NORTHSTAR_HASH_SCOPE_1` — The north-star validated-hash covers the WHOLE section including explanatory prose, so fixing a stale caveat or a typo silently reverts a VALIDATED ch
- `WRECKEDMACHINES_VFE_SMELTER_REMOVAL_1` — Remove VFEFactory_AutomatedSmelter from the build menu so it no longer sits indistinguishably beside our RM_WM_AutomatedSmelter tiers - owner ruling 2
- `WRECKEDMACHINES_MOD_SETTINGS_1` — WreckedMachines ships NO Mod Settings at all (no ModSettings/DoSettingsWindowContents anywhere in the mod, MEASURED 2026-09-16) - violates MOD_OPTIONS
- `ORACLE_FALLBACK_UNVALIDATED_1` — Oracle's fallback text bypasses OracleValidator: RequestOhmLetter takes fallbackText as a CALLER argument and DeliverFallback ships it verbatim to Rec
- `AFTERMATH_TELEGRAPH_REFERENT_1` — RM_AftermathRule_AlliesArrive's one substitution slot has two referents: SendTelegraph formats with ResolveTargetFaction's result, the ALLY under Ally
- `READ_LINE_REGISTRY_SHARED_1` — OWNER RULING 2026-09-16: read-line ids are GLOBAL with a shared registry — recurring demands (no engineering marker in player text, tier-neutral prose
- `REACTIVE_SHIP_LIGHTING_1` — NO MOD OWNS mood lighting, reactive light pulses, or lights that act alive — MEASURED 2026-09-16: zero such dir in src/, zero ledger items, zero desig
- `PYRELANDS_TERRAIN_BURNDEF_1` — RM_FE terrain burnedDef flammable config errors on load
- `NINEFOLD_LOUDNESS_FRONT_1` — Ninefold owes LOUDNESS and THE FRONT, which canon rules exist and no code computes — MEASURED 2026-09-16: GameComponent_Ninefold's entire public read 
- `FLOWWORKS_MECHANICS_TABLE_STALE_1` — FlowWorks' mechanics table (flowworks_mod_definition.md section 4) is stale in the DANGEROUS direction - it says UNBUILT for code that exists, so a se
- `NORTHSTAR_MOTION_FRAMES_1` — A north-star line about CHANGE is evidenced by an ordered frame sequence, not one screenshot - owner ruling 2026-09-17, spec 4b. judge.py takes shots[
- `NORTH_STAR_ATMOSPHERIC_TBD_1` — TBD by owner ruling 2026-09-17: how the ship-lighting north star bars get automated waits on live play. Verbatim: 'I am not sure we should worry about
- `MODCHECK_STATUS_ORPHANED_BY_RENAME_1` — modcheck_status.json records the canal mod's GREEN under the dead key FluidCanals while the mod ships as FlowWorks, and there is no CLI verb to move o
- `UNSUBSTANTIATED_SPECIES_ABILITIES_1` — Reverse audit: every species ability the defs GRANT that canon does not substantiate - the mirror of XENOTYPE_CANON_CORRECTION_1, which only found abi

## Commits

```
bb51a1aac 29 faces can take skin colour again
86ed9a960 facing_set_audit: south viewpoint gate (the top-down-south class)
daf766e30 Ledger sync: FlowWorks Phase 5 live-restart pass closed out
fac8d2672 Full mod list: add 3 missing Pyrelands mods
bd9a1b8ee Gizka: dino_v5 is the locked set (owner, 2026-09-17)
9e7e773a0 Wire approved Pyrelands creature render wave into art-override mods
1f8d8b20b FlowWorks: fix viscosityClass casing, was silently discarding vanilla terrain
de46f98c1 Gizka biped + Iriaz v2 wired (owner rulings 2026-09-17)
b2a800d5c Ugnaught skin is dull pink, on the films
9e6ad6ce8 chore(sync): laptop 2026-09-17T08:47:44-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
a97ce794e The canon dossier he will check by hand
f60d197b0 Six species get the skin canon actually sources
ccf21240a Four species rulings, and the reverse audit he asked for
d11280cda chore(sync): laptop 2026-09-17T08:29:17-07:00 — infrastructure/DETERMINISM_ASSESSMENT.md
657d2a8fd chore(sync): laptop 2026-09-17T08:13:56-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
071a4e667 Every checklist now names a folder that exists
f873119d9 Repair the documents before writing to them
db60eff8d Ledger sync: FlowWorks Phase 5 recovery note
52e312a15 FlowWorks Phase 5: superdeep capture, ladders, ruling-23 shooting rule
8afddf9a9 Ledger sync: union of the rebase-window events
c63807a9d Pyrelands: rescue 5 flora textures that lived only in the game copy
ce96c5b7d Strike the reservoir era from the canal walk
875bada07 Step 1 was a check that could not fail
4071837b1 chore(sync): laptop 2026-09-17T07:01:25-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
5dd16639f Only mods you can look at owe visual bars
538796cd9 The canal's 16 bars are his now
77ca3c8b5 chore(sync): laptop 2026-09-17T06:41:19-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
d753e6a11 Declare the canal's three change bars, and delete the claim that there was one
353f59404 Two lessons from the ship-lighting walk
5a2798ef7 Stop the ship-lighting north star at intent, on his word
4c8075f65 Three rulings on the ship-lighting list: one cut, one moved, one split in four
77f8f7a33 Ruling: the alarm may be learned, not read on sight
2cb408c31 chore(sync): laptop 2026-09-17T06:12:52-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
76c910258 Ruling: a north-star bar about change is evidenced by a frame sequence
d122894ff File the canal walk under the name the mod actually ships as
25aa8864a chore(sync): laptop 2026-09-17T05:27:57-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
1eefeae9a File the stale mechanics table, with the rows I verified myself
c2c0e1a6f Rulings 34-36: walking the canal checklist deleted art instead of adding it
7a41307da chore(sync): laptop 2026-09-17T05:06:56-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
f20473605 Four rulings onto the ledger; the law-conflicts item closes with all three resolved
872b3814e The gods are holograms, so a dark ship is witnessed after all
2a00b10ac chore(sync): laptop 2026-09-17T04:27:07-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 5 more
15414ff32 PITCELL_PRISONER_BED_BRIDGE_GAP_1: live proof closes it
f54338cfe DROID_REPAIR_FOR_PROFIT_EVENTS_1: live verify closes it
69664cff7 chore(sync): laptop 2026-09-16T22:21:51-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 4 more
2e4029791 Drop the Transient duplicates a rebase reinstated
b09f87f67 Phase 0 is eight questions, not seven — the doc claimed an edit I had not made
cae747843 Six lessons from the AtmosphericBase sitting
407855a27 The repo answers back: AtmosphericBase has no canvas, and no rank supplier
7160e8a50 FlowWorks rulings 28-33 recorded; Quarry perspective reference saved
c4ca4fe3c AtmosphericBase hook ecosystem: the rank source is owed, and the ship has no canvas
0e5d58211 The AtmosphericBase build programme: eleven phases, and Phase 0 is only questions
a6bb05724 Fix the walk's line format — the parser read zero lines from the first draft
8bb7c29d2 FlowWorks Phases 2-4 complete; Odyssey decoupled; canyon flood is a client
c1e67088b AtmosphericBase's north star, and an axis the system does not have
6999f2c85 AtmosphericBase: the mod he designed tonight, with every ruling verbatim
4c3ed4151 FlowWorks: LiquidCorrosion/LiquidIgnition gated OFF by default
6a073f249 artpipe state sync: six claimed pending files, throughput log
cade628c1 FlowWorks Phase 1: rename, ruling-24 deletions, three-mod merge (FLOWWORKS_BUILD_PROGRAM_1)
e3b6b577d FlowWorks Phase 0 blockers MEASURED via RimSage; gizka dino v5 rendered
0d1fed5d7 chore(sync): laptop 2026-09-16T21:00:36-07:00 — Transient/dynamiclighting_scheme_catalog_DRAFT_2026-09-16.md
57fdb69cb Gizka is a dinosaur, not a frog — owner's KOTOR references land in canon
942ccc764 codex_image.py: stdin=DEVNULL cures the daemon-wide stdin hang; gizka v4 r2 rendered
45f6884ab Gizka review rulings: two eyes, east/west are side profiles (owner 2026-09-16)
a7c1d5792 Pyrelands census sheets 2026-09-16 + 3 EmberGrass leafless alternates
e9e7e76ac chore(sync): laptop 2026-09-16T19:04:00-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 4 more
89232b332 facing_set_audit.py: the full wiring-time metric gate for creature facing sets
53c4dbb8b Lesson: pathspec commits are the only safe commit in the shared worktree
47efcc641 rimflow ledger sync: FLOWWORKS_BUILD_PROGRAM_1 start + core-engine note
4db4b3852 FLOWWORKS core engine: depth/fill grid, the pulse, dig-to-depth
39b977eeb FLOWWORKS art candidates: four dry-excavation depths, ladder, designators, sluice gate
6fd764fac FlowWorks program 1: grouped validation checklist, name-collision check, Liquid Logistics correction
679d1d209 Three rulings on the read axis, and a capability nobody owns
e14c9cfed FloodedCanyon: dug canals survive a canyon flood cycle
fb9345c06 File the Aftermath telegraph's wrong referent — verified, not taken on report
af1f8e69f Aftermath read-axis draft, and rule 2's telegraph names the wrong faction
6f4e7e3f5 Reboot lessons: the stale gate, the hash trap, and the pathspec rule
097bce16c WreckedMachines VALIDATED, and the owner overruled the judge asymmetry
b24c35d78 chore(sync): laptop 2026-09-16T17:40:51-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
11bdbeaf3 The must read axis, and it costs zero re-validation
dca82d184 WreckedMachines' north star, and the owner chose to bind a vision he has not built yet
abb619826 Graffiti is VALIDATED and now refuses itself — the system's second proof
1320d91ef chore(sync): laptop 2026-09-16T16:52:46-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
477e2c79a Keep the north-star state: field a bare token — modcheck parses it
bddc55dc3 Graffiti's north star, ruled in an owner sitting — and it refuses two of four marks
16726a1b7 chore(sync): laptop 2026-09-16T16:10:12-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
745ddc2f0 North-star batch 1 drafted, and the dismissals were hiding a real bug
54b0acfd3 chore(sync): laptop 2026-09-16T15:54:00-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
5fbbc162d Four of seven visual-pass dismissals judged: two sound, one time-bounded, one challenged
660827578 The canon library gets an index that cannot go stale, and a skill that fires
1b1620a1b chore(sync): laptop 2026-09-16T15:22:41-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
252f8ff2e Canon library census: one dangling image, and the droid item's premise is already met
7343e307f A rename gate that closed on 2026-08-31 was still stopping work 16 days later
01de1faaa The pit's art spec joins FlowWorks instead of floating beside it
df9b1c656 chore(sync): laptop 2026-09-16T13:59:31-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
69491c8a5 Regenerating the pit into FlowWorks does not discharge its visual requirement
581840a2d chore(sync): laptop 2026-09-16T13:46:56-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
f7a940c7e MACBENCH reboot handoff — and handoff.py no longer guesses the seat
c2f6977c7 A v2 dream was mostly delivered by v1, and the walk says it is scheduled for replacement
e09bd85c4 Resolve the docs and queue items today's rulings falsified
01d3bcef1 Pits' north star is VALIDATED — and the falsification test passes offline
2b9f8fbe9 Three lessons from the FlowWorks design session
5a188da03 chore(sync): laptop 2026-09-16T11:39:40-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
0ced17e8a FLOWWORKS_BUILD_PROGRAM_1 — the ticket for the Fable process on the Desktop
7fa541ef3 Rulings 24-27: sources become terrain, rain needs no roof, SUPERDEEP captures regardless of fill, merge before the pit art
76ca92619 Gizka bipedal facing set validated — artpipe state for the quota-delayed drain
43af1ae4a Rulings 20-23: the mod is FlowWorks; terrace farming general and gated; one shooting exception
1e73ce51b DEEP_TRIBES_FIRE_RITE_1: the Deep Tribes come and light it themselves
ea4b748d3 Ruling 19: four depths - plus the two laws and one algorithm that give terraces without a Z-system
f27beebc4 ScorchFruit density: one 1-in-20 roll per burned cell, not per fire-tick
5e7ab077d Ruling 18: Pits IS Canals - depth is the primitive, and it collapses three ladders into one
4d6605cef Canals and Pits compose rather than merge - and it deletes planned work
930d82498 The Fluidity boundary as a principle, plus detonation, sticky-limitless, dry-channel cost, and fill-in advice
b2866cab0 chore(sync): laptop 2026-09-16T09:45:27-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
e45229d67 Gizka canon corrected: bipedal hopper — owner ruling recorded in the entry
9490e2aa8 FLAMEFANG_SNAKE_REBIRTH_1: recommit after a concurrent rebase dropped e63fae1e3
ad449c467 Propagate the Fluidity consolidation into the framework's client map
988599e40 Ruling: one mod called Fluidity, absorbing Many Waters and Liquid Logistics; sluice gates yes; ignition is per-liquid
dd5c2336c Ledger sync: PYRELANDS_SCORCHED_RUINS_1 closed, FIREHAWK_FLIGHT_BEHAVIOR_1 noted blocked-on-art
58a08013f Pyrelands: the biome's fire clock, and the furnace-beast's thermal capacitor
cad170e94 PYRELANDS_SCORCHED_RUINS_1: ruins scorch and burn via BiomeDef.extraGenSteps
f67c8d4b4 Pyrelands SW-canon fidelity check: 6 of 7 pass, iriaz fails the one-horn line
6d452b001 chore(sync): laptop 2026-09-16T09:04:38-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
5af00922c File the Desktop's first task (temp-terrain DLC gate) and the sink item
ee9b32883 Ruling: this mod IS the liquid engine - plus sinks, and it needs a new name
2102e0988 File the canyon-flood-erases-canals collision
80161da41 Three more rulings: three fill tiers, self-drain returns, and burn as a rate on the tier ladder
1688d9a2a Quickgrass reads its growth: sprout, half-grown, tall lush
06b3062de chore(sync): laptop 2026-09-16T08:44:52-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
3b123dac9 statusline: the digits were overstating context headroom by ~440k
097183478 ScorchFruit ships as 4 random ash-buried variants, tint dropped, stalk art dead
0c45174ba Ledger sync: Pyrelands full-review art wave notes (4 items)
c51c341ba Pyrelands full-review art wave: 30 painterly renders, 8 canon creatures + Sytheclaw restyle + Mantistanis S/E + quickgrass burn state
44f7c9531 Two rulings: filling a canal in displaces liquid back, and tar gets viscosity first
8a7f18ad1 chore(sync): laptop 2026-09-16T07:35:41-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
e824de757 The art survey: partial fill is nearly free, and tar currently looks like water
64b2c66e8 Record the FluidCanals north star draft against the 77-walk authoring item
9456d910a Draft the FluidCanals north star from his own words — DRAFT, binding nothing
219ef6bcf Fire: name what is unknown, and why the decision does not wait on it
de9c1292e The two hardest parts of the canal design are already built — in FloodedCanyon
ce2926e93 chore(sync): laptop 2026-09-16T07:14:36-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
97b613102 Fold the Pits vocabulary into the canal definition — and one line of his prose is false today
c6c8d854f Fluid Canals mod definition (DRAFT) — and RimSage cannot be reached from this machine
148db88f4 File the three items his rulings created; fix a walk asserting a field that isn't there
0f8cdabdb Scarcity is stock: propagate the owner's reversal, and delete two stale claims
80cb83777 chore(sync): laptop 2026-09-16T04:55:07-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
de7859ff4 Close NORTH_STAR_RUNNER_WIRING_1; one lesson to the inbox
758c6d7f6 The north star now binds: a run's verdict reads the screen, not just the state
a3b849fe7 chore(sync): laptop 2026-09-15T22:57:48-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
```

## Game / bridge / tree state at wrap

- <could not run /Users/mandrake/dev/RimMaster/game: [Errno 13] Permission denied: '/Users/mandrake/dev/RimMaster/game'>
- Bridge: FREE    since 2026-09-17T16:16:55Z

Working tree clean apart from untracked `Transient/`.

