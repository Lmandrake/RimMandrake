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
| 2 | **row 4 scrapfields** | **not biome-gated** — hooks `Base_Player` genSteps, so ANY fresh map shows it. 🔴 **Look before any destroy** — the last map's evidence died in a 43,288-thing wipe |
| 3 | **row 4 dune seas** | ⚠️ **do NOT eyeball it.** A density change 0.65→0.55 is unjudgeable without a control. **Read the live `BiomeDef`**, confirm `terrainPatchMakers` 0.55 / 0.50 |
| 4 | **ground hulk** `00a1398` — wide shot + one casket bank | 619 of 1,200 cells; 0 overlaps, 0 out-of-bounds, 0 props off-deck |
| 5 | **the ten art-fix mods** — one spawn, one look each | eight deployed + enabled; two new ones are **not** (below) |
| 6 | **`NoPathToPilotConsole`** — ✅ **one call, no walk:** `jawa/order_pawn targetId=<console> waitTicks=0 unpause=false` returns `canReach` on a **paused** game (BRIDGE `bee5da9`) | doors are in the export — **a door is not a path**, and this is a launch gate. 🔴 **`pathEndMode` must be `interactioncell`** (the default when `targetId` is set) — the vanilla gate is `PawnCanFillRole` → `CanReach(..., InteractionCell, ...)`, and the cell *beside* a console is a **different verdict** |

| 7 | 🔴 **NEW, and it is the cheapest-now item here** — place one `SmallThruster` at the stern (x45 z131) and read whether it says `WarningThrusterInside`. **Outdoor-required ⇒ the EXPORTED hull needs its stern cut back**, a deck re-lay; substructure-free-only ⇒ nothing to change (77 free cells in zone `S`, exclusion run falls off the deck at z133-137). Ruling and numbers: §11 |

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

### 📦 ✅ Both new fix mods DEPLOYED and ENABLED by OPS — `cb6c2f7`, `dd66fe6`
`mandrake.phytokinbarkheadfix` @562 (donor @388) and
`mandrake.kotorbandoliernorthfix` @**579** — deliberately outside the 556–563
art-fix slot, because its donor `guy762.mm.kotorcore` is at **572** and ships
loose art. `mandrake.missingartfixes` removed from the list, closing C11 step 3.
⚠️ **These shipped BEFORE the stop-fixing-art directive and stay in place.**

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
