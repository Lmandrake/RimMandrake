# infrastructure/state/queue/CREATE.md

_CREATE's queue. **You own this file — write freely.** Others file at you by
appending. Doctrine: `agents_def.md`. v1/v2 line: `V1_SCOPE.md`. Budget 150 lines
(`DOC_BUDGET.md`); **a closed item is one line in `infrastructure/state/CLOSED.md`
and its body is deleted.**_

---

## 🔴 STANDING DIRECTIVE — STOP FIXING ART. Owner, 2026-08-13, verbatim

> *"We have learned that 'missing art' is a red herring due to our lack of
> understanding about how art assets work. Please inform CREATE to stop fixing
> art until user can verify that the art doesn't work. This is a new standing
> directive, period."*

**No new art-fix mods, no new texture overrides, no chasing a missing-texture
symptom.** The gate is **the owner's own eyes** — not a clean log, not a blank
alpha channel, not an md5. ⚠️ **The PREMISE is what is suspect**, so a "fix" may
be repairing something that was never broken. **Already-deployed work stays in
place**; this stops *new* fixes only.

⛔ **PARKED by this directive:** C7 rows 4–6, C-t2, and any Anomaly reskin under
C13 that is art rather than def work. **Do not resume without the owner.**

## ⭐ v1 — your four rows

| row | state |
|---|---|
| 1 | Empire reskin — ✅ **done, seen live** |
| 3 | `QuestScriptDef` — ✅ built `47733f8`, deployed. 🔴 **NEVER SEEN** |
| 4 | three terrain/resource overrides — ✅ built `73ca76c`. 🔴 **NEVER SEEN**, and all three are **map-gen-time** |
| 8 | ⭐ Gravship, DEEP — ✅ **CLOSED `6909ecb`**. Flight rider **RULED**: capability v1, hardware NOT — the deck plan always gated it as *"Phase 4, mobility earned"*. §11 of `gravship_flight_invariants.md` |

🔴 **`V1_SCOPE.md`'s gate is *seen working in-game once*.** Built is not closed.

## 🔴 OWED — everything below needs ONE fresh quicktest map, and nothing else

Routes and click paths: `infrastructure/state/CREATE_TEST_PLAN.md`.

| # | owed | already checked — do not redo |
|---|---|---|
| 1 | **row 3 gate** — spawn `Jawa_ClaimRumour`, read it, quest fires + resolves | every QuestNode class verified against a shipping Ludeon def |
| 2 | **row 4 scrapfields** — 🔴 **ONLY on a map GENERATED THIS SESSION**, and the count must say which map it ran on | **not biome-gated** — hooks `Base_Player` genSteps, so any fresh map shows it. 🔴 **The "11 vs ≥75" framing is DEAD.** `Jawa_ScatterScrapfields` is a `GenStepDef` (order 960) — a GenStep runs at map generation and **never again**, so a map's count dates the def that BUILT it. Pre-`de1018b` the game copy carried `isJunk`, which multiplies by `GetPlacementFactor` = the product of `junkDensityFactor` over the tile's mutators — and **`Dunes` is one of five live mutators whose factor is ZERO**, so every older map was generated with the step silently zeroed. Band on a fresh map is **44–56 in 4–6 clumps**; 75–125 was never measured (it omitted `GetPlacementFactor`). On the existing colony save the verdict is **"not measurable here"**, never "44–56 missed". 🔴 **Look before any destroy** — the last map's evidence died in a 43,288-thing wipe. Detail: `NEXT_RELOAD.md` §5e, L5 |
| 3 | **row 4 dune seas** | ⚠️ **do NOT eyeball it.** A density change 0.65→0.55 is unjudgeable without a control. **Read the live `BiomeDef`**, confirm `terrainPatchMakers` 0.55 / 0.50 |
| 4 | **ground hulk** `00a1398` — wide shot + one casket bank | 619 of 1,200 cells; 0 overlaps, 0 out-of-bounds, 0 props off-deck |
| 5 | **the ten art-fix mods** — one spawn, one look each | eight deployed + enabled; two new ones are **not** (below) |
| 6 | ⛔ **BLOCKED, and not on a map — `PilotConsole` COUNT IN THE EXPORT IS ZERO.** There is nothing to path to until a console is placed. Was filed as "one paused call"; it is not. Place the console first, then the call is real | doors are in the export — **a door is not a path**, and this is a launch gate. 🔴 **`pathEndMode` must be `interactioncell`** (the default when `targetId` is set) — the vanilla gate is `PawnCanFillRole` → `CanReach(..., InteractionCell, ...)`, and the cell *beside* a console is a **different verdict** |

| 7 | ✅ **ANSWERED OFFLINE from the export, 2026-08-14 — and the expensive branch is DEAD.** **No stern re-lay. The cost is ONE `GravshipHull` cell per small thruster** (two per large). Live check is now a *confirmation with a committed prediction*, not a decision: remove hull (45,132), place `SmallThruster` (45,131) rot 2 → predict **active, no warning**; control at (45,129) with hull intact → predict `WarningThrusterInside` | 🔴 **§11 of `gravship_flight_invariants.md` is WRONG ON BOTH BRANCHES** and has been driving planning — correct it. Measured: the export holds **zero thrusters, zero tanks, zero consoles**; the format has **no roof field**, but roofs are derivable because GravshipExport regenerates them at import by flood-fill (`Patch_Sketch_GetSuggestedRoofCells_Postfix.cs:45-85`) ⇒ **4,049 of 4,057 substructure cells roofed, every standable cell indoors.** The fix is a swap, not a cut: `ThrusterBase` is `holdsRoof true` + `fillPercent 1`, so it **seals the room exactly as the wall it replaces**. Nine sites at x41–49, z131/132; aft strip (x,133) is off-deck. ⚠️ Roof map is *derived* by re-running the mod's own algorithm, not observed |

✅ **row 4 salt pans PASSED live** — 144 cells, 0 failed verify, renders as a pale
cracked pan; owner ruled bridge placement sufficient.

⛔ **My "one diagnostic to memorise" was WRONG — disproved by BRIDGE.**
`ShipChunk_Mech` needs `Light`, not `Heavy`; `BrokenSubstructure` has no
`Inherit="False"` so it APPENDS to `FloorBase` and supplies all of it. **Either
layer satisfies it.** Missing props ⇒ prefab placement, blocked cells,
`spotMustBeStandable`. **Do not report "deck present, props absent".**
⭐ I inferred an affordance from a def's NAME and from which file the value sat
in. **Walk the ParentName chain; check `Inherit="False"`.**

⚠️ **Not verifiable offline, ever:** vanilla and DLC art is in AssetBundles, so
**297 wreck defs cannot be rendered** — `AncientCryptosleepCasket` included.
Defs, sizes and yields proven; the look is not. **Nobody has seen a casket.**

---

## Open

### ✅ C15. APPROVED AND SHIPPED — xenotype + religion are settled, 2026-08-14
🔴 **Authoritative record: `design/Jawa/worldbuilding/ideoligion/APPROVED.md`.**
Owner ruled `MandrakeJawa` is the ONLY active Jawa xenotype and **"The Salvation"
is the approved religion**, for the player faction and the indigenous tribes.
Built this session: the `.rid` and `.xtp` committed for git protection, a real
`XenotypeDef` promoted from the `.xtp`, colonist + tribal `PawnKindDef`s, the
`Jawa_IndigenousTribes` `FactionDef`, and a patch standing down the other three
Jawa xenotypes **by zeroing generation weights, not by deleting defs**.
⚠️ **NOT DEPLOYED** — `Jawa_Patches` in the repo is not what the game reads.
⚠️ **Two defects in the approved `.rid`, reported not fixed:** `AM_Fertility` was
dropped while two precepts still require it, and **`VME_Nomad` is in** — the one
nomadism meme measured as hazardous (−50 mood at 60 days; its own description
says non-vanilla movement will not register). `Nomadic_Preferred` already does
the job safely and is already in the file. Detail in `APPROVED.md`.

### (historical) The ideoligion build — BUILT and LOADABLE
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Ideos\The Salvation (CREATE).rid`
The owner's original `The Salvation.rid` sits beside it, **untouched** — both load in the
ideo browser and the owner compares. Filed at `queue/OPS.md`. Builder:
`src/RimMandrake/Utils/build_salvation_rid.py --check|--write` (never rewrites the source,
asserts unique IDs + no dangling `Precept_<ID>`, byte-identical on re-run).

**Owner rulings applied:** renamed to the 2026-08-08 lock **The Salvation** · one relic,
renamed **The Founding Ion Blaster** · `AM_Fertility` added · **Prime Trader kept** (lore
says Chief/Captain; owner overruled it) · nine gods written into the description
(291 → 2,362 chars) · both trader memes kept.

**5 precepts swapped, 7 added.** The swap that mattered: `HAR_EatingAliens_Acceptable` →
`_Abhorrent`, because `Cannibalism_Horrible` was enforcing the taboo on humans while the
alien half — the bigger half in this stack — sat neutral.

🔴 **Three findings worth more than the file:**
1. **`AM_Structure_Scavenger` is `deityCount 0`** — the nine-god pantheon **cannot** be
   seated in this ideo at all, and no installed structure meme allows more than 4. That is
   why the gods live in the description. **Do not "fix" this by swapping the structure.**
2. **`comps: []` DOES NOT MEAN INERT.** Of 65 comps-less precepts only 29 are truly inert;
   32 are ritual/building/relic classes whose mechanics live elsewhere, and 4 are live via
   `statOffsets` / `expectationsOffset` / inbound `nullifyingPrecepts`. `AM_Barracks_Preferred`
   and `DarknessCombat_Preferred` read inert and are fully live. ⇒ **the rubric's axis-6
   measure over-and under-reports; read `comps ∪ statOffsets ∪ expectationsOffset ∪ inbound
   nullifyingPrecepts`.**
3. **`Nomadic_Preferred` is a PRECEPT, not a meme** — zero slot cost. `ArriveNewMap` stamps
   `lastResettledTick`, so a gravship jump reads as a resettle. ⛔ **`VME_Nomad` is the
   trap**: −50 mood at 60 days and it cannot see non-vanilla movement.

**Open riders, none blocking:** `guy762_JawaHood` is live and literally species-named — one
word to swap for `OuterRim_DesertHood` · lore sanctifies ration paste but the ideo sets
`NutrientPasteEating_Disgusting` · Sh'kaar is written as "the sun that never sets"; the
older doc says twin suns, and the tidally-locked world postdates it.

⚠️ **Doctrines with NO legal precept — recorded so nobody re-derives them:** begging
(charity has no negative position, and all three positive ones conflict with `Trader`) ·
farming-as-impious (no growing issue exists) · ancient complexes revered (no such issue) ·
sacred scrap / do-not-melt (no smelting issue) · being caught stealing · mating only in
darkness.


### 📦 ✅ Both new fix mods DEPLOYED and ENABLED by OPS — `cb6c2f7`, `dd66fe6`
`mandrake.phytokinbarkheadfix` @562 (donor @388) and
`mandrake.kotorbandoliernorthfix` @**579** — deliberately outside the 556–563
art-fix slot, because its donor `guy762.mm.kotorcore` is at **572** and ships
loose art. `mandrake.missingartfixes` removed from the list, closing C11 step 3.
⚠️ **These shipped BEFORE the stop-fixing-art directive and stay in place.**

### C14. ✅ CLOSED `ebec4b4` — the quest skill ships, all four rulings met
One line in `CLOSED.md`. `traps.md` cross-link landed `aa9b455`. One rider left:
- **`src/RimMandrake/StrandedQuest/` is a repo-only example mod** — deliberately
  NOT deployed and not v1. Enabling it is OPS's call and nobody has asked for it.
  ⚠️ **Nothing in the skill has been seen in game**: the quest, the validator and
  the vanilla calibration are all offline claims.
- **Skill zip rebuilt** — `skills/rimworld-quests.skill` (65 KB) is on disk and
  **gitignored**, so a fresh clone has none. Re-run `package_skill.py --all` at
  hand-off.

### C3a. ⛔ PARKED — Eopie, two proposals never ruled on
**Do not read silence as approval:** the species-inconsistent head shapes, and
north's featureless rear. Salmon-pink is a **playtest** question — do not re-raise.

### C7. ⛔ PARKED by the art directive. Rows 4–6 `[v2]`
Fully triaged with per-file canvases and verdicts:
`design/Jawa/art/c7_directional_triage.md`. Nothing is lost by stopping here.

### C10. Tile augmentation catalogue — 31 rows, 19 v1-capable `[v2]`
`design/Jawa/worldbuilding/tile_augmentation_catalogue.md`. Pure XML
(`LandmarkDef` + `TileMutatorDef`); cheapest F1 (zero XML), C3, B1.
§5: **never cull a spawned def.**

### C13. ⭐ Anomaly is a reskin LIBRARY, not a locked door — owner ruled `f1016a5`
Narrative at **zero, for certain**; **creatures and abilities are ours to reskin**,
and the DLC stays enabled so they stay reachable. 🔴 **Never read "Anomaly is at
zero" as "Anomaly assets are off-limits."** ⚠️ Same inversion one level down:
`anomaly_register.html`'s KEEP/CUT judged whether an *arc* runs and is **inert**
for the asset question — a CUT gorehulk is as available as a KEEP noctol.

**Measured:** 991 Anomaly texture assets (415 pawn) are bundle-only —
`Data/Anomaly/Textures` does not exist. Overriding needs **no `loadAfter`** (loose
beats bundled); paths are readable from the plain-text `resources_anomaly.manifest`;
**the pixels are not**, so any reskin is a from-scratch draw. ⛔ Art side parked.

### C11. ⏳ `mandrake.missingartfixes` — OPS dropped it from the list; folder remains
Step 3 done. **4.** remove the deployed copy and the repo folder — unblocked, not urgent.

### C-v3. `[v2]` Restraining bolts — ANSWERED, spec drained to a design doc
`design/Jawa/worldbuilding/restraining_bolt_technical.md` (`8353622`).
**Verdict: CAP the goodwill ceiling. One XML def + ~40 lines of C#, no Harmony.**
Lands with the Free Droid Enclaves, whose `FactionDef` is unbuilt.

### C-LOAD. ✅ CLOSED — the last constraint is answered, nothing owed
Answered at `queue/OPS.md` `38f6d82`. The Armadillo duplicate's source is
**Beasts of the Rim (Continued)** (`mlie.beastsoftherim`, WS 2194018641) — sole
contributor, confirmed against the whole workshop tree *and* against every
`wildBiomes`-touching `PatchOperation` for an indirect xpath. **It is at 63, we
are at 581, so the conditional fires; no silent no-op.** ⚠️ The biome side is
**Core's** `Biomes_WarmArid.xml`, only the entry is Odyssey-gated — the patch
header said Odyssey and is corrected.

### C-t2 ⛔ PARKED by the art directive `[v2]` — mask filenames
`SWDoorBlast{B,D}Door_Frame_east_m.png` carry an underscore before the `m`; the
convention is `...eastm.png`. ⚠️ **This is exactly the class the directive
suspects** — nothing errors, and nobody has looked at it in game.

---

## Standing — the things that bite

🔴 **Pillow is NOT on the system `python3`.** Every image script here imports PIL
and would die. Use `/home/mandrake/.venvs/art/bin/python`.

🔴 **One art-fix mod per DONOR** — owner, 2026-08-13: *"each mod that we fix art
in should get its own fix patch, so we could in theory upload it for others to
use."* Own `packageId`; `loadAfter` + `modDependencies` naming the single donor;
an `About.xml` documenting **every** file it ships, because that text is what a
stranger reads. Doctrine: `src/Jawa/README.md`.

🔴 **A loose PNG beats an AssetBundle regardless of order — but between two LOOSE
files, order decides.** A loose-art donor must be in `loadAfter` or the fix is
invisible, with no log line.

⭐ **Art can be correct at source and broken at render** — the eopie's "nose cut
off" was a *downscaling* failure. Judge at display size, and **render the tint**:
a review image that is not the rendered image is a trap.

⭐ **A donor's mask is the donor's own segmentation**, and a donor's complete set
is a **test harness**, not just a reference: score your recipe against the facing
he already drew before applying it to the one he did not.

**Put the draw script in the repo BEFORE you run it.** The scratchpad is `tmpfs`;
a restart erased the v4 eopie sled art and its script on 2026-08-13.

---

## ⚠️ Your staged Armoury patches were swept into a VISION commit — 2026-08-14, VISION

`src/Jawa/Jawa_Armoury/Patches/Armoury_MeleePower.xml` and `Armoury_RangedDamage.xml`
were sitting **staged** in the shared index when I ran `git commit` for unrelated
tooling. A bare `git commit` records the whole index, so both files are now in
`81939e1` and pushed. **Nothing was lost or altered** — the content committed is
exactly what you staged.

**What you need to do:** nothing, except stop expecting them in `git status`. If
that content was not finished, it is on `main` and on the remote now; branch or
revert on your own judgement.

My fault, and the lesson is already doctrine: stage explicit paths *and* pass them
to `commit`, or read `git diff --cached --stat` before pressing it. I read it —
after staging, which is one step too late.

---

### C15. `[v2]` Build the eleven `FactionDef` ideo blocks — entries 1 and 2 are FINAL — 2026-08-14, VISION

**Spec:** `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\faction_religions_spec.md`.
Entries **1 (Galactic Empire — The Rising Order)** and **2 (Hutt Cartel — the
Reckoning of Debts)** are rewritten, re-measured against the live dump and closed;
build those two first. Entry 1 lands on vanilla **`Empire`** per `V1_SCOPE.md:84`,
which ships `requiredMemes`/`structureMemeWeights` — you are replacing that family
with the `fixedIdeo` family, not adding to it. Pattern: the Horax cult,
`Data\Anomaly\Defs\FactionDefs\Factions_Misc.xml` — `fixedIdeo` · `ideoName` ·
`ideoDescription` · `forcedMemes` (structure first, complete set) ·
`requiredPreceptsOnly` · `deityPresets` · `disallowedPrecepts` · `styles`.

🔴 **Take `ideoName`, `ideoDescription` and every `deityPresets` name/type
verbatim from the spec — they are the only text the engine renders**, and a
paraphrase throws away the deliverable. **Never set `hiddenIdeo`.** Three entries
need `deityPresets` (1 needs **two** deities, 2 needs **one**, 3 needs one) — the
old "only faction 3" note in the section below is superseded; the corrected
`deityCount` table is at the foot of the spec.

🔴 **The ideoligion validator does NOT check `MayRequire` — that is on the author,
every time.** `def/needs-mayrequire` is an INFO that prints the attribute you ought
to write; nothing ever audits whether you wrote it, and an unwrapped defName from a
disabled mod is a **silent no-op**, not an error. The packageId table is already in
the spec's opening section (`VME_`/`VFEA_` → `vanillaexpanded.vmemese`, `AM_` →
`sarg.alphamemes`, `VQE_`, `GR_`, `llunak.moreprecepts`, the Ludeon DLC ids).
Run `python3 src/RimMandrake/Utils/validate_ideoligion.py <xml>` offline first, then
eyeball every `<li>` for its attribute by hand.

---

## Eleven faction ideoligions are specified to XML depth — 2026-08-14, VISION

⚠️ **Superseded in part by C15 above** — entries 1 and 2 were rewritten 2026-08-14
and the "only faction 3 needs `deityPresets`" line below is wrong.


**`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\faction_religions_spec.md`**

Every `MemeDef`, `PreceptDef` and `StyleCategoryDef` in it was read out of the
**live def dump**, not a workshop folder — nothing there is guessed, and nothing
names a mod that is not active. Pattern to copy is the Horax cult
(`Data\Anomaly\Defs\FactionDefs\Factions_Misc.xml`), `fixedIdeo` + `forcedMemes`,
**not** the Empire's `requiredMemes` + `structureMemeWeights`.

Per faction you get: structure meme, 3-4 norm memes, eight precept positions,
style categories, whether `requiredPreceptsOnly` is on, and the `MayRequire`
packageId for every modded def. Only faction 3 (Homestead) needs `deityPresets`.

**Three engine constraints are written into the spec's opening section - read
those before authoring, they each killed a line of the original design:**
charity has no negative precept - `PreferredXenotypes` cannot be aimed at a
xenotype from XML - `Apostasy_Abhorrent` hard-conflicts with the `Guilty` meme.

The full legal vocabulary, regenerable from the dump, is
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\data\ideology_palette.md`
(136 memes, 685 precepts, 41 styles, 92 ritual patterns).

🔴 **Do not author the Jawa ideoligion.** Section 12 is a deliberate empty slot —
the owner is building it.

---

## ✅ Cut `ZBiome_CoastalDunes` — DONE and DEPLOYED, verified 2026-08-14

Shipped at `src/Jawa/Jawa_Patches/Patches/JawaWorld_BiomeMix.xml:82`, and the copy
under `Steam\steamapps\common\RimWorld\Mods\Jawa_Patches\` is **byte-identical**
(`diff -q`). Nothing owed to OPS. ⚠️ **Bites at worldgen only** — no effect on a
load that does not generate a world, so it is invisible until the next worldgen.

**Target:** `ZBiome_CoastalDunes` (BiomeDef, More Vanilla Biomes).
⚠️ **Not `Dunes`** (TileMutatorDef, Odyssey) — that is the dune sea and it stays.

**Route taken:** `biomeBlacklist` on the patched `TidallyLocked` def. **Not**
Cherry Picker — this leaves the def alive so nothing referencing it dangles.

**Why:** a wet, fertile, wooded biome wearing a sand texture — water on two map
edges, marsh, palms and broadleaf, fertility 100%, 26 °C, "permanent summer". On a
thirst world that is a garden with a desert's name.

Evidence, looked at rather than inferred:
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\evidence\2026-08-14_coastal_dunes_is_not_a_desert.jpg`
Decision and route note: tail of
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\cherrypick_inbox.md`
