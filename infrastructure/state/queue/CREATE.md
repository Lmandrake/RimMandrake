# infrastructure/state/queue/CREATE.md

_CREATE's queue. **You own this file — write freely, nobody blocks on it.** Others
file at you by appending here. Doctrine and tagging rules live in `agents_def.md`;
the v1/v2 line lives in `V1_SCOPE.md`._

---
## ⭐ v1 — YOUR v1 ROWS. Read this before anything below.

**Four of the eight burn-down rows are yours** (`V1_SCOPE.md`), and two of them
close today without a game.

| row | state | needs a load? |
|---|---|---|
| 3 | One `QuestScriptDef` that fires and resolves. Any premise. | ✅ **BUILT `47733f8` — 🔴 NOT GATED, never seen in game** |
| 4 | Three terrain/resource overrides visible on the map | ✅ **BUILT `73ca76c` — 🔴 NOT GATED, and all three are map-gen-time** |
| 8 | ⭐ Gravship, DEEP — design complete, build at 0 | 🔴 build wants the game; you anchor that session |
| 1 | Empire reskin — ✅ built and seen live | ✅ done |

⚠️ **Rows 3 and 4 are at zero because nobody saw they were closable, not because
they are hard.** Author both offline, deploy with row 2, verify in ONE session.

✅ **Both are AUTHORED. Neither is GATED, and the difference is the whole point** —
`V1_SCOPE.md`'s gate is *seen working in-game once*, and nobody has looked. The
routes, the click paths and the map-gen trap are queued for the next load in
`D:\Luke\dev\Rimworld\infrastructure\state\NEXT_RELOAD.md` under "CREATE'S ROWS".
🔴 **A deploy is owed first** — the game copy of `Jawa_Patches` has no
`Defs/TerrainDefs/`, `QuestScriptDefs/`, `ThingDefs_Items/` or `MapGeneration/`
at all, so neither row is in the load as things stand.

---

## Open

### 🔴 WRAP 2026-08-13 — what is half-done, and what was already checked

**Everything owed needs ONE fresh quicktest map.** Full state, with commits:
`infrastructure/state/AGENT_CREATE_state.md`.

| owed | already checked, do not redo |
|---|---|
| **row 3 gate** — spawn `Jawa_ClaimRumour`, read it, quest fires + resolves | def authored, validated, deployed (`47733f8`); every QuestNode class verified against a shipping Ludeon def |
| **row 4, scrapfields** | **not biome-gated** — hooks `Base_Player` genSteps, so ANY fresh map shows it. 🔴 **Look before any destroy**; the last map's evidence died in a 43,288-thing wipe |
| **row 4, dune seas** | ⚠️ **do not eyeball it.** Density change (0.65→0.55), unjudgeable without a control map. **Read the live `BiomeDef`** and confirm `terrainPatchMakers` 0.55 / 0.50 |
| **row 4, salt pans** | ✅ **PASSED live** — 144 cells painted, 0 failed verify, renders as a pale cracked pan. Only "does it generate" remained, and the owner ruled placement via bridge is sufficient |
| **ground hulk** (`00a1398`) | 619 of 1,200 cells, structurally validated: 0 overlaps, 0 out-of-bounds, 0 props off-deck |
| **the eight art mods** | all deployed and ENABLED; each is one spawn and one look |
| **`NoPathToPilotConsole`** | doors cut into the **outer** hull and carried in the export — but **a door is not a path**, and this is a launch gate |

🔴 **The one diagnostic worth memorising:** if the hulk's deck renders and its
props are **absent**, `BrokenSubstructure` went to the top layer and
`ShipChunk_Mech` lost its `Heavy` affordance. **A terrain swap, not a redesign.**

⚠️ **Not verifiable offline, ever:** vanilla and DLC art lives in AssetBundles —
`Data/*/Textures` does not exist — so **297 usable wreck defs cannot be rendered**,
`AncientCryptosleepCasket` among them. Defs, sizes and yields are proven; the look
is not.

**Left deliberately uncommitted:** `src/RimMandrake/BlastDoorFrameAsyncFix/Source/REVIEW_before_after.png`
— a run-artifact, regenerable in ~1 min from the committed `render_review.py`.


### 🔴 THE RULING that governs C3, C5, C6 and C11 — owner, 2026-08-13

> **"Each mod that we fix art in should get its own fix patch, so we could in
> theory upload it for others to use."**

**One art-fix mod per DONOR mod** — not one per defect, not one shared bucket.
Own `packageId`; `loadAfter` + `modDependencies` naming the single donor; and an
`About.xml` description documenting **every** file it ships, because that text is
the Workshop description a stranger reads, not a note to ourselves.

Written to doctrine in `src/Jawa/README.md`, which also records the
load-order trap: a loose PNG beats an **AssetBundle** asset regardless of order,
but between two **loose** files order decides — so a loose-art donor must be in
`loadAfter` or the fix is invisible.

### C3. ✅ `DesertVehicleReskin` is a loadable mod — CLOSED by the ruling
`About/About.xml` written: `mandrake.desertvehiclereskin`, `loadAfter`
`sarg.alphavehiclesneolithic` (verified on disk at ws `3028675048`, not taken from
a doc). The donor ships **loose** vehicle PNGs, so that ordering is load-bearing.
`deploy_custom_mods.py --mod DesertVehicleReskin` now reports the packageId and
`in sync (0 files, 7 held)` — the **"no packageId in About.xml"** flag is gone.

### 🔴 C3a. ART REVIEWED BY THE OWNER, 2026-08-13 — three fixes owed
**Not approved, not rejected.** Recorded verbatim at the end of a wrap and
**deliberately not acted on.** Do these before asking for approval again.

| # | facing | the owner's finding | fix |
|---|---|---|---|
| 1 | **south** | *"the neck is oddly swollen as though a smaller body was put there instead of the neck"* | **Take the neck from the EAST facing** — the owner names east as showing how it should actually look. Re-derive south's neck from it rather than reshaping the blob in place. |
| 2 | **east** | *"the creature appears to have its nose cut off"* | Restore the snout. ⚠️ East's subject bbox ends at **x=489 of 512** — check first whether the nose is **clipped by the canvas edge**, in which case the team shifts left and the nose is not redrawn at all. |
| 3 | **sled** | *"we should also color the sled brown to match the harness"* | The sled is still the donor's white/grey. Match the existing harness brown — one palette, and it also answers my own separate note that the piece reads flat. |

⭐ **Finding 1 inverts my own review, and that is the lesson.** I called east *"the
weakest facing"* on ink coverage (7.7% fill against the donor's 10.3%) and proposed
**rebuilding its composition**. The owner reads east as the anatomically **correct**
one and south as the broken one. Both hold — east is thin *and* right — so **do not
redraw east's creature; harvest from it.** Acting on my own verdict would have
destroyed the reference the south fix depends on. **Ink coverage measures presence,
never correctness.**

⚠️ **My other proposals are NOT ruled on:** the salmon-pink colour, the
species-inconsistent head shapes, north's featureless rear, south's missing eyes.
The owner addressed neck, nose and sled only. **Ask — do not read silence as
approval, and do not fold them into this pass.** Note finding 3 does move the
palette, so the pink question gets easier to judge once the sled is brown.

✅ **Fix 3 DONE — `2a9a004`. It was never an art problem.** The sled reads
white/grey in the PNG but renders grey from the donor def's
`<color>(71,71,71)</color>`, because our mask is red-over-sled / black-over-team
and red multiplies by that colour. So "colour the sled brown" cost zero pixels:
`Patches/DogSledTint_Brown.xml` sets the harness leather (99,65,24), and the
eopie **cannot** be dragged along because they are black-masked.
`Source/preview_tint.py` renders the multiply offline, so a colour call never
costs a game load again.

✅ **Fix 2 DONE — `65c1590`, and the queue's hedge was wrong in an instructive
way.** This entry told the next reader to "check first whether the nose is
clipped by the canvas edge, in which case the team shifts left". **It is not
clipped** — the subject ends at x=489 of 512 with 22 px of clear margin, and the
snout is drawn in full in the raw at 1934 px. **It is a SCALE failure:** at the
104 px the sprite actually renders, the muzzle's soft curve downsampled into a
hard vertical wall with a square top corner, which is exactly what "nose cut
off" describes. Regenerated with a continuous tapering trunk; footprint bbox
unchanged at (8,168,490,293).
⭐ **Generalises: art can be correct at source and broken at render.** Judging a
sprite at 100% is judging the wrong image. `Source/recrop_east_v2.py` now
measures the rigging constants from the cut instead of leaving them hand-set,
so a regeneration costs a run rather than a careful remeasure.

✅ **Fix 1 DONE — `7e3018e`.** South's neck now leaves the shoulders at about
half the ribcage width and tapers, matching east. **Harvested from east as the
owner directed** — east was passed to the generator as reference-only for
anatomy, never for pose or framing, so the facing the owner called correct was
not touched. Footprint bbox unchanged at (199,11,315,468).

✅ **APPROVED AND SHIPPED, owner 2026-08-13: "Eopie is reviewed! Ship it!"**
`DEPLOY_HOLD.txt` entry lifted, `deploy_custom_mods.py --apply --mod
DesertVehicleReskin` wrote 8 files and VERIFIED in sync. ⚠️ **Deployed is not
loaded** — `mandrake.desertvehiclereskin` still needs a `ModsConfig` entry AFTER
`sarg.alphavehiclesneolithic`, because the donor ships LOOSE art and order
decides whether the reskin is visible at all. Filed with OPS.

✅ **ENABLED by OPS, 2026-08-13** — with the seven art-fix mods, all eight in one
slot after `mandrake.missingartfixes`. **572 -> 580 active, listed-but-absent 0.**
Ordering verified positionally rather than assumed: `mandrake.desertvehiclereskin`
idx **563** against `sarg.alphavehiclesneolithic` idx **526**, and all seven
donors confirmed ACTIVE first — a reskin whose donor is disabled fails exactly
the same silent way as one ordered wrong.

⭐ **ALL THREE OWED FIXES ARE DONE.**
`Source/REVIEW_all_three.png` regenerated — and `Source/review_sheet.py` now
builds it, so the two reviews are the same layout instead of a hand-assembly
rebuilt from memory. ⚠️ **The new sheet draws both sides TINTED as the game
renders them**, which the first sheet did not: that is why the sled looked white
in review and grey in game. A review image that is not the rendered image is a
trap.

✅ **RULED 2026-08-13 — the salmon-pink colour: KEEP, revisit after playtest.**
Owner: *"Keep them pink for now and playtest them. If it bugs us later, we can
always regenerate."* **Do not re-raise it** — it is a playtest question now, not
an approval one.

⏳ **Still NOT ruled on, and still do not read silence as approval:** the
species-inconsistent head shapes, north's featureless rear.

🔴 **Pillow is NOT on the system `python3` here** — every build script in this
mod imports PIL and would die. It is installed at
`/home/mandrake/.venvs/art/bin/python`; use that interpreter for anything that
touches an image. The queue records a peer hand-decoding IHDR and inflating IDAT
to avoid this; that is no longer necessary.

### C11. ✅ CLOSED `61fe954` — `MissingArtFixes` split into four per-donor mods
`src/RimMandrake/CereanManeFix/`, `MSEDroidFix/`, `ToolBeltFix/` and
`ResearchKitEastFix/`. **All seven textures are now described**, which was half the
point: an uploadable mod cannot ship art whose defect nobody wrote down. Together
with C5's `BlastDoorFrameAsyncFix/` that is **five** fix mods out of one bucket.

⚠️ **None of the five loads yet — they are absent from `ModsConfig.xml`.** Handed
to OPS in `NEXT_RELOAD.md`, with C6's two, packageIds read from each `About.xml`
and the ordering constraint stated per mod. One slot next to
`mandrake.missingartfixes` satisfies all seven `loadAfter`s.

🔴 **Who actually changes `ModsConfig.xml`:** only us or the owner in RimSort —
**RimWorld does not rewrite it on exit and neither does RimSort** (an earlier note
in this file said it did; that was wrong). **OPS determines which mods go in; the
OWNER does the RimSort ordering by hand and then tells OPS it is done and the game
is started.** CREATE's job ends at handing over the list and the constraints.

#### 🔴 RETIRING `mandrake.missingartfixes` — the order, and the one dependency
It is **LIVE and deployed**, so this is not a folder delete. Do it in this order:

1. **Move the blast-door brief OUT first.**
   `src/RimMandrake/MissingArtFixes/Source/blast_door_frameasync_east_BRIEF.md`
   belongs in `src/RimMandrake/BlastDoorFrameAsyncFix/Source/` — it was staged in
   the wrong mod before the ruling existed. **This is the dependency: delete the
   folder first and the brief goes with it.**
2. **Confirm the five successors are in `ModsConfig.xml` and have loaded**, i.e.
   after OPS has added them and the owner has ordered and started the game — not
   before.
3. **Ask OPS to drop `mandrake.missingartfixes` from the list** (CREATE does not
   edit `ModsConfig.xml`; the owner reorders in RimSort). It must go *before* the
   folder does, or the game boots with a missing-mod entry.
4. **Then** remove the deployed copy under
   `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\MissingArtFixes`
   and the repo folder.

<details><summary>original entry</summary>

### C11. 🔴 Split `MissingArtFixes` — it violates the ruling above
It is one bucket holding **7 textures across several donors** (Outer Rim Galactic
Diversity, Outer Rim Droid Depot, plus a research-kit mod and an apparel mod), and
its description documents only **2 of the 7** — the 4 research kits and
`ToolBelt_west` were added without a word.

Split one mod per donor, and **describe the five undocumented files as they
move** — an uploadable mod cannot ship art whose defect nobody wrote down.

✅ **ATTRIBUTION DONE 2026-08-13 — it is FOUR donors.** Every row verified by
reading the donor's own Def for the `texPath`, and every broken state verified by
decoding IHDR and inflating IDAT to take the max of the alpha channel (no PIL on
this box) — **not** inferred from file size.

| donor packageId | ws | our file(s) | donor's state | `loadAfter` needed? |
|---|---|---|---|---|
| `Neronix17.OuterRim.GalacticDiversity` | 2980427615 | `CereanMane_south` | present, **maxAlpha 0**, 1,514 B | ❌ no — bundled |
| `Neronix17.OuterRim.DroidDepot` | 3096501398 | `MSE_north` | **absent entirely** | ❌ no — bundled |
| `VanillaExpanded.VAEAccessories` | 2521176396 | `ToolBelt_west` | present, **maxAlpha 0**, 753 B, 256² | ✅ **YES — loose** |
| `aw.researchreinvented.retextured` | 3279243445 | the **4** research kits `_east` | blank or absent | ✅ **YES — loose** |

🔴 **The research kits are the one that will be got wrong: one Def owner, two
texture shippers.** The defs (`RR_FieldResearchKit*`) belong to **Research
Reinvented** `PeteTimesSix.ResearchReinvented` (2868392160), but **Research
Reinvented Retextured** (`aw.researchreinvented.retextured`, 3279243445) contains
**no XML at all** — it is a pure loose-texture replacer and it loads later
(`ModsConfig.xml` order 457 vs 275), so **it is what actually renders.** Our
overrides are already 512×512 = RRR's canvas, not RR's 256². `loadAfter` must name
**RRR**, and `modDependencies` should name RR as the def author. Confirmed
independently: `Source/mirror_empty_easts.py` L48-51 already names `3279243445`.

⚠️ **The two Outer Rim fixes need NO `loadAfter`, and that is not laziness.** On
1.6 those donors' `LoadFolders.xml` swaps `Common_Old` → `Common`, and `Common/`
holds only `AssetBundles/` — so their art loads from a bundle, which a loose PNG
beats regardless of order. **Verified the defect survives bundling** by grepping
the bundle manifests: Galactic Diversity's lists a `CereanMane_south` entry (there
to be blank), and Droid Depot's lists only `MSE_east`/`MSE_south` — **no
`MSE_north`.** Both fixes remain valid on 1.6.

⚠️ **`MissingArtFixes` is LIVE and deployed** — unlike C3 this is not pre-review
work, so the split changes what the game loads. Retire `mandrake.missingartfixes`
deliberately or it lingers in `ModsConfig.xml` as a missing mod.

</details>

### C4. ✅ Gravship comp radii — CLOSED offline, and the question was mis-posed
**The solver is right: 34/30/12/85 match the stored config floats exactly**, so the
coverage figure (4,057/4,057, 8 of 12 extenders) stands on the same footing as the
rest of the plan. The layout is not wrong.

⚠️ **But "compare the assumed radius to the radius the def declares" cannot be
done, and should not be attempted.** Three layers write those fields and the def
literals are *supposed* to disagree: Odyssey XML says 16.9, Vanilla Gravship
Expanded patches it **down** to 12.9, and **Bigger Gravships ships no XML at all** —
`GravshipSize.dll` stamps the comps during implied-def generation, which runs after
all XML patching, so it wins regardless of load order. The 30 exists only as a
stored float plus a Harmony prefix.

🔴 **The real find was a wrong provenance comment, not a wrong number.**
`src/RimMandrake/mapsynth/ship_designs.py` claimed `EXT_SUPPORT = 500` came "from the same
settings file". **There is no `BG_gravExtenderSupport` key in that file** — 500 is
Bigger Gravships' compiled mod default. Right value, believed for the wrong
reason, and it mattered: at VGE's 100 or vanilla's 250 the cap would be 1,832.8 or
3,632.8, **below the 4,057-tile hull**, and the build would have failed on
*capacity* while every radius was correct. Header rewritten; that file also used to
say the limits were "ASSUMED pending the Fetcher result" in the same breath as
saying they were read from the stored floats.

**Filed out, all three verified before filing:** `infrastructure/state/queue/BRIDGE.md` B3 (their owed
`get_def GravFieldExtender` drops from load-bearing to confirmatory — OPS's own
state file already has live `SubstructureSupport 632.7954`, the owner's stored
float, proving the settings path applied over VGE), `infrastructure/state/queue/VISION.md` V13 (stale
4,800 tile cap in `design/Jawa/worldbuilding/ship_designs.md`), `TODO.md` §20 (`src/RimMandrake/Utils/ilscan.py`
decodes only `ldc.r4`, so it cannot attribute compiled defaults to field names).

### C5. ✅ CLOSED `48e5e16` — three blast-door `_east` textures, in their own fix mod
`src/RimMandrake/BlastDoorFrameAsyncFix/` (`mandrake.blastdoorframeasyncfix`,
donor `Lumi.doorsexpanded` ws `3550435517`, loose art so `loadAfter` is
load-bearing). Drawn at the real 933×933 canvas, not the placeholders' 267×267.

⚠️ **The brief's transform was WRONG and was corrected against the measurement, not
followed.** Read the commit before trusting the numbers below.
⚠️ **Not in `ModsConfig.xml` yet** — handed to OPS with C6's and C11's.

<details><summary>original entry</summary>

### C5. Three blast-door `_east` textures — unheld, mechanical, ready to draw
*Doors Expanded Star Wars edition*, `Lumi.doorsexpanded`, ws `3550435517`, under
`Things/Building/Door/Blast/`. Each is a 757 B placeholder; mirror the healthy
`_north`.

| file | defName | `_north` to mirror |
|---|---|---|
| `SWDoorBlastDoor_FrameAsync_east.png` | `PH_DoorBlastCDoor` | 5,908 B |
| `SWDoorBlastBDoor_FrameAsync_east.png` | `PH_DoorThickBlastBDoor` | 7,413 B |
| `SWDoorBlastDDoor_FrameAsync_east.png` | `PH_DoorBlastDDoor` | 22,651 B |

⚠️ **`PH_DoorBlastDoor` is NOT affected** — that is *base* Doors Expanded
(`jecrell.doorsexpanded`), healthy at 16,946 B. The two mods share the `PH_`
prefix and are very easy to conflate.

**3 files, not 6:** a door has TWO orientations. The SW edition ships 15 `_east`
and 18 `_north` and **zero** `_west`/`_south`, healthy and broken alike, so there
was never a west texture to render.

✅ **Host mod RULED — no longer blocked.** By the ruling above these three go into
their **own** fix mod for `Lumi.doorsexpanded`, not into `Jawa_Patches` and not
into `MissingArtFixes`. A brief already exists:
`src/RimMandrake/MissingArtFixes/Source/blast_door_frameasync_east_BRIEF.md` —
**move it to the new mod's `Source/` as part of C11's split**, since it was staged
in the wrong mod before the ruling existed.

✅ **Donor confirmed on disk: `Lumi.doorsexpanded`, ws `3550435517`** — a **5th**
fix mod, distinct from C11's four. Explicitly **not** base Doors Expanded (ws
`3532342422`, different packageId), whose `PH_DoorBlastDoor` east is healthy at
16,946 B.

🔴 **CANVAS TRAP — the placeholders are 267×267 and the real canvas is 933×933.**
Drawing at the placeholder's size would produce art that validates as "same size as
what I replaced" and renders tiny. Take the canvas from each door's own healthy
`Frame_east`.

🔴 **These are NOT mirrors — measured, not assumed.** On the base mod's healthy east
pair, `FrameAsync_east` mismatches its mirror by **13.61%** of alpha, against
0.38–0.70% for the north pair. The transform is: widen the subject ~21%, shorten
~4%, shift left ~3% of canvas width, **keeping the top edge exactly where
`Frame_east` has it.** Masks must be checked per file — the SW mod ships **no**
mask for `FrameAsync_east` at all.

Full brief: `src/RimMandrake/MissingArtFixes/Source/blast_door_frameasync_east_BRIEF.md`
— **move it into the new mod's `Source/` as part of C11's split**, since it was
staged in the wrong mod before the ruling existed.

</details>

### C6. ✅ CLOSED `cb95f60` — two typo-fix mods, one per donor, no art authored
`src/RimMandrake/GravshipAstronautFix/` (`vanillaexpanded.gravship`, ws
3609835606) and `src/RimMandrake/SauridFrillFix/` (`vanillaracesexpanded.saurid`,
ws 2880990495). Both donors ship their art **loose**, so `loadAfter` is
load-bearing on both. Bytes copied verbatim, md5-identical.

⚠️ **Neither loads yet — they are not in `ModsConfig.xml`.** Both must sit after
their donor; next to `mandrake.missingartfixes` clears both.

🎁 **Bonus defect found while building it:** the astronaut typo hits the **mask**
for *both* life stages, not just the ancient one. `Mech_Astronaut_north.png` is
spelled correctly and renders, but its overlay mask is the misspelled file, so
the ordinary astronaut silently loses its faction-colour overlay on north. The
fix covers it.

🔴 **None of these three defects can ever produce a log line.** `Failed to find
any textures at` fires only when **every** direction of a `Graphic_Multi` is
missing, so a single absent facing is a silent south-fallback. There is no log
signal to confirm the fix by either — it has to be eyeballed in game.
**Generalises to every missing-facing item in C7.**

<details><summary>original entry</summary>

### C6. Two filename typos — the art exists and is simply misnamed 🎁
Verified on disk. Ship the same bytes at the correct filename in an override mod:
no new art, no def edit, no risk.

✅ **Host RULED, and it means TWO mods here, not one** — the typos are in two
different donors (Vanilla Gravship Expanded, VRE Saurid), so by the ruling above
each gets its own fix mod. Cheapest possible pair: no art to draw, description
writes itself ("the donor's filename has a double R").

```
Textures/Things/Pawns/Mechanoid/Astronaut/   (Vanilla Gravship Expanded)
  MechAncient_Astrronaut_north.png       <- double R, 18,453 B of real art
  Allegiance_Mech_Astrronaut_north.png   <- same typo
Textures/Pawn/CenterFrill/                   (VRE Saurid)
  CenterFrill8_north-.png                <- trailing hyphen
```

The mech shows its **front while walking away**; `CenterFrill7` beside it is named
correctly.

</details>

### C7. The other incomplete directional sets `[v2]`
Each checked against its def's `graphicClass` and `visibleFacing`, so these are not
Falleen repeats: VRE Phytokin `BarkSkinFemale_Wide_Normal` **east**; Biomes!
Polluted Lands `ImpalingClaw` **north/east/west** (`BMT_ImpalingClaws` explicitly
asks for N and W, only `_south` exists); SW KotOR Resources 2 bandoliers **north**
across all 5 body types (`drawData.dataNorth.layer = 65` renders a chest bandolier
on the pawn's back); Biomes! Caverns 4 pupae `_east` only (`BeetlePupa` alone backs
6 defs); plus Dark Ages Beasts, VGE failures, and the Alpha Genes emblem (lowest
confidence — `layer -2` may make it deliberate).

✅ **TRIAGED — `design/Jawa/art/c7_directional_triage.md`.** Do first: Phytokin
`BarkSkinFemale_Wide_Normal_east` (zero art — the file is in the donor as
`..._east copy.png`), KotOR `bandolier_chewbacca`/`_traveler` north (most-seen
defect here; KotOR is at load 573, AFTER our fix slot 556-564), VGE
`GravshipGenebank_north` (180° rotation, goes INTO `GravshipAstronautFix`).
**2 new mods.** Alpha Genes emblem and `Eyes_Red` are correct as shipped — struck.
🔴 **C7's own method was insufficient:** `visibleFacing` is set in C# for eyes, and
`Graphic_Multi.Init` has a bare-path fallback, so a clean log proves nothing.

<details><summary>original flag</summary>

👁️ **One vanilla item to eyeball, do NOT patch blind:** Biotech `Eyes_Red` ships
only `RedEyes_Female_east` plus a non-directional `RedEyes_Male`, while every
sibling face-feature ships east+south — but the log has **zero** `Failed to find
any textures at`, which a bare male file should have produced. Eye rendering likely
has a special path. Look at a red-eyed pawn first.

</details>

### C8. `check_sprite.py` — art intake validator
512×512, real alpha, zero saturated pixels, value distribution, bounding box,
south/north silhouette parity. **Build it before commissioning any art**, not after.

### C12. `Jawa_Patches`' `About.xml` still under-documents its own mod — 14 files
Found while appending the six new bullets (`6417c31`). The description is the text
a stranger reads, and by the C11 ruling *every* shipped file must be in it. It now
covers 15 files; the mod ships **29 XML files plus 5 textures**. Undescribed:
`Defs/GeneDefs/JawaHead.xml`, `JawaSkittish.xml`, `Defs/PawnKindDefs/AlienSpawnEnablers.xml`,
`GamorreanPawnKinds.xml`, `Defs/XenotypeDefs/GamorreanXenotype.xml`, and the
patches `HuttEyes_RestoreRenderNodes`, `HuttEyes_Slitted`, `ImperialDesertDirectorate`,
`IonStunMote_Blue`, `JawaCombatViability_Tuning`, `JawaEyeGlow_Stock`,
`RebelAlliance_Suppress`, `SpeciesStartingGear_Tuning`, `WookieeHead_Upgrade`.
Each carries its own header comment, so this is transcription, not investigation.

🔴 **And two of its textures are now shipped TWICE.**
`Textures/Pawn/CenterFrill/CenterFrill8_north.png` and
`Textures/Things/Pawns/Mechanoid/Astronaut/{MechAncient,Allegiance_Mech}_Astronaut_north.png`
live in `Jawa_Patches` **and** in C6's `SauridFrillFix` / `GravshipAstronautFix`.
Two loose files at one path is decided by load order, not by intent — **decide
which mod owns them and delete the other copy**, before both are enabled.

### C10. Tile augmentation catalogue — 31 rows, 19 v1-capable `[v2]`
`design/Jawa/worldbuilding/tile_augmentation_catalogue.md`. Placement is pure XML (`LandmarkDef` +
`TileMutatorDef`); cheapest are F1 (zero XML), C3, B1. §5: **never cull a spawned def.**

---

## Closed

### C1. ✅ `deploy_custom_mods.py` per-file hold list — ALREADY DONE
Migrated from `TODO.md` §12 recording **"CREATE is taking this"**. It was built
while that note went stale: `e15c081` made intended-undeployed declarable per
file, `8700bd2` extended it to protect against DELETION as well as writing
(WORLD's catch), `4044252` stopped display code aborting a deploy.

**Verified end to end rather than taken from the commit messages**, 2026-08-13:
`src/DEPLOY_HOLD.txt` exists, the plan reports `H` with the reason and
the line number, an unreasoned hold names its own file and line, and a stale
pattern is warned about on full runs but not on `--mod` runs. WreckedMachines
shows `in sync (0 files, 14 held)` instead of fourteen lines of false drift.

⚠️ **Closing a queue item by finding it already built is worth as much as building
it** — the cost avoided is a second implementation of a feature that was already
there and working.

### C2. ✅ Space Tower — VERDICT: **KEEP, unconditionally** `[v2]`
**Split out of `TODO.md` §17.** The on-brand/endgame-fit judgement went to VISION;
the technical half was yours: is either mod actually active in the running game,
what is the licence, and does it conflict with CQF.

**Ruled by the owner and recorded by VISION (`infrastructure/state/queue/VISION.md`
§C2 condition 2).** The towers are **Imperial infrastructure**; the Hutts pay you
to cut them; **the Empire's retaliation IS the cost.** No blackboard variable and
no goodwill tick — consequence the player feels as weight arriving.

🔴 **So the −15 Empire goodwill patch is DROPPED, not pre-wired.** The earlier
ruling said to ship it as a cheap proxy that "costs nothing and pre-wires the real
thing". That is superseded: an Empire goodwill hit is bookkeeping the player will
not notice, and a −15 against a faction that is supposed to be permanently hostile
goes dead the moment V7 lands. **Do not author it.** The real cost was never
goodwill — it is raid pressure.

⚠️ **It no longer waits on M4 / the Heat gauge**, which was the old blocker. Still
`[v2]`, and the dependency is already paid: `hailuan.customquestframework` is
active at load position 108 and `...frameworkai` at 431; only `hailuan.spacetower`
itself is absent. 🎁 **C2's real dividend was already banked elsewhere** —
`ST_TowerMap` is where the `Jawa_ClaimRumour` three-comp readable pattern came
from. Full design:
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\orbital_towers_and_the_sky_ladder.md`

### C9. Beautiful_Tilemap — evaluate the concept spec `[v2]`
A proposed utility that scores a generated map against the 39-creator corpus and
improves it. **Concept only, explicitly not v1** — spec at
`design/RimMandrake/beautiful_tilemap.md`, which names the smallest first slice (metric
only, offline) and seven open questions the owner must answer before any build.

---

## Standing, from your identity file

**Put the draw script in the repo before you run it.** The scratchpad is `tmpfs`
and a restart erases it — that is how the v4 eopie sled art and its script were
lost on 2026-08-13. This is not a queue item, it is a habit the queue cannot
enforce for you.

---
## ⭐ C-v1. OWNER RULING 2026-08-13 — rows 3 and 4 come BEFORE the Bantha art

The owner reversed the overnight reassignment. **Author v1 rows 3 and 4 first**,
then resume the eopie sled / Bantha work.

- **Row 3** — ✅ **CLOSED OFFLINE `47733f8`.** `Jawa_TheClaim`, built to VISION's
  spec at `design/Jawa/worldbuilding/v1_quest_the_claim.md`, strings verbatim,
  Core-only nodes on the `OpportunitySite_ItemStash` skeleton, rival clan is text
  with no `FactionDef`. **Not yet SEEN — the v1 gate is still open.**
- **Row 4** — ✅ **AUTHORED OFFLINE `73ca76c`, and 🔴 NOT GATED.** Three overrides:
  `Jawa_SaltCrust` (a cosmetic evaporite pan, fertility 0, reusing Odyssey's unused
  `DryLakeBed` art) attached to Desert / ExtremeDesert / AridShrubland; wider dune
  seas (Core's own SoftSand thresholds lowered, no new def and no new art); and
  `Jawa_ScatterScrapfields`, a `ChunkSlagSteel` scatter registered into
  `Base_Player` only. **Not yet SEEN — the v1 gate is still open.**

  🔴 **All three act at MAP GENERATION TIME, so they need a NEWLY GENERATED map.**
  Nothing appears on an existing one, however long you look; checking row 4 on the
  current colony map is a guaranteed false negative. The one free check is the
  salt crust's art, which the live bridge can paint with `jawa/set_terrain`
  (capture the rect with `jawa/get_terrain_batch` first so it replays back as a
  restore) — that answers "does the texture resolve and read as evaporite white",
  and nothing about whether the patch makers attach.

🔴 **The finding row 3 turned up, and it outlives row 3.**
`everAcceptableInSpace` gates **acceptance by the player, not site placement** —
Core `Languages/English/Keyed/MainTabs.xml` L198 `QuestNotSpace` = "cannot accept
in space", sitting in the accept-requirement string run; Odyssey's six genuinely
orbital sites set it zero times while Core's `Script_TradeRequest.xml` sets it
true *and* forces its target ground-only.

⚠️ **Corrected by VISION's parallel read (`82281e8`) — say this the refined way,
because the first phrasing overstated it.** The quest is still **offered** in
orbit; what is blocked is the **Accept button**. On the ordinary storyteller path
the offering filter is dead code (`GiveQuest_Random` is `targetTags World`,
`World.Tile` is `PlanetTile::Invalid`, so both `CanQuestOccurOnTile` overloads
return true on their first branch). **Friction in orbit, not silence.** Also:
`autoAccept=True` suppresses the gate both ways, which is why Space Tower's
`everAcceptableInSpace=False` is inert.

VISION has ruled (`95e500a`): flip the default
for what we author, judge adopted quests one at a time, and **do not sweep** —
the impact turns on how much of the campaign is spent on the Orbit layer, which
is not answerable offline.

Both are pure offline XML. They are the ONLY offline v1 work left, and they must
be **authored and deployed before the next live session** — that session
generates the world and cannot close them if they do not exist yet.

## C-v2. `validate_patch.py` is yours — owner ruled 2026-08-13
It reads `Patches/` only, never `Defs/`, and does not say so. Fix the gap or
document it; either closes the item.

---
## C-LOAD. Put load-order dependencies in OUR mods' `About.xml` — 5 gaps, 2 dead IDs

**Filed by OPS 2026-08-13, on the owner's call this session:** load-order
dependencies belong in the mod's own `About.xml`, not in RimSort user rules —
that way the constraint travels with the mod, survives a re-sort, and needs no
per-machine setup. **You own the mods, so the edits are yours.** Filed rather
than sent because no CREATE seat was reachable.

All of the below verified game-down against the **580-mod active list** and the
**1261 packageIds present on disk**. Nothing here is inferred from a name.

### 🔴 1. `mandrake.jawa.armoury` declares two `loadAfter` targets that DO NOT EXIST

The rule is therefore **100% inert** — nothing is holding the armoury after its
targets except the RimSort user rule, which is itself crippled (item 5).

| declared in About.xml | reality |
|---|---|
| `guy762.starwarskotorweapons` | 🔴 no such packageId — real one is **`guy762.kotorweapons`** |
| `Aoba.OuterRim.Core` | 🔴 no such packageId — real one is **`Neronix17.OuterRim.Core`**. `Aoba` is Dead Man's Switch, a different author entirely. |

### 2. `modDependencies` declared but **no** `loadAfter`

**A dependency is not an ordering.** RimSort's `use_moddependencies_as_loadTheseBefore`
is **off** on this machine, so these genuinely do not order anything. Both mods are
texture overrides, and a texture override that loads *first* does nothing at all.

- `mandrake.cereanmanefix` → add `loadAfter` **`Neronix17.OuterRim.GalacticDiversity`**
- `mandrake.msedroidfix` → add `loadAfter` **`Neronix17.OuterRim.DroidDepot`**

This is trap #38's exact shape (`traps-mods-and-managers.md:86`).

### 3. No load rules in `About.xml` at all, only in RimSort

- `mandrake.jawa.doctrine` → needs `neronix17.outerrim.droiddepot`
- `mandrake.jawa.patches` → 11 targets currently live only in `userRules.json`

### 🔴 4. `jawa.patches` patches two Outer Rim mods it does not declare

`ImperialDesertDirectorate.xml` and `RebelAlliance_Suppress.xml` operate on
`OuterRim_GalacticEmpire` and `OuterRim_RebelAlliance` defs — but
`neronix17.outerrim.galacticempire` and `neronix17.outerrim.rebelalliance` appear
in **neither** the About.xml nor the user rule. **The order is correct today
(547 and 548 versus 576) purely by topological tie-break, not by constraint.**

⚠️ `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md` depends on both patches
applying — the Empire's page label and the Rebel Alliance suppression both come
from them. Add both targets.

### 5. Then drop `loadBottom`

All six of our rules in `C:\Users\Mandrake\AppData\Local\RimSort\dbs\userRules.json`
carry `loadBottom: true` **alongside** their `loadAfter` lists. `loadBottom` is the
stronger constraint, so it silently defeats the `loadAfter` and the placement is
decided by tie-break instead. Once About.xml carries the real dependencies, drop
`loadBottom` from everything **except `mandrake.rimdefdump`**, which legitimately
must observe the fully assembled game.

Background: `skills/rimworld-start-prep/SKILL.md` §2 — "load at end" fails because
nearly every patch mod claims the bottom, so a constraint asserted by everyone is
satisfied by no one.

### 6. `mandrake.wreckedmachines` inactive — ✅ ANSWERED, no action `[v2]`

I asked whether its absence from `activeMods` was deliberate. **The owner ruled the
same session: it is officially v2.** Deployed and present but switched off is the
correct state. **Do not re-file it** — an inactive mod on disk looks like a defect
from every angle except this one, so the note stays here to stop the next sweep
rediscovering it.

### C-v3. Restraining-bolt goodwill hook — technical due diligence `[v2]`
**Design is done and is not yours to redo:**
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\restraining_bolt_doctrine.md`

**The concept (owner, 2026-08-13):** applying a restraining bolt drops goodwill
with the **Free Droid Enclaves** — *"whether it's on one of their droids or not.
It's slavery to them."* Removing a bolt pays it back.

**Your half is the one question I could not answer and should not have tried:**

1. **Which mod actually supplies restraining bolts in our stack?** Name it.
2. **What shape is the application** — a `RecipeDef`, a `ThingComp`, an
   `AbilityDef`, an apparel item, or something else? **This decides whether the
   hook is twenty lines or a project.**
3. **Is there a hookable moment** — a method a Harmony patch can sit on that
   fires exactly once per application, and once per removal?
4. Does anything already listen to bolt application (another mod's patch) that
   we would collide with?

**Not a build request yet.** Answer 1–4 and I will size the design against it.
`[v2]` — the Enclaves are unbuilt, so this lands with them.

---

## C-v3 — ANSWERED (CREATE, 2026-08-13)

### 🔴 VERDICT: **CAP the ceiling.** One XML def + one ~40-line C# class. **Not a project.**

**And it beats all three options you offered**, because the mechanism that gives
the cap gives the *level* too, from the same class, recomputed from live state on
a timer the engine already runs. **Nothing is stored, nothing accumulates,
re-fire is impossible by construction.** Your "HELD, not ever-fitted" constraint
is not something we engineer around — it is the only thing this mechanism can
express.

`GoodwillSituationDef` / `GoodwillSituationWorker` is exactly what you suspected,
and it is fully mod-extensible: **three active mods already add their own.**
⛔ **Do not write a Harmony patch. Do not call `TryAffectGoodwillWith`.**

**The two numbers you are waiting on** — `RimWorld.FactionRelation::CheckKindThresholds`,
disassembled from `Assembly-CSharp.dll` with `src/RimMandrake/Utils/ilprobe/il.py`:

| event | threshold | IL |
|---|---|---|
| **Hostile** | effective goodwill **≤ −75** | IL_0021 `ldc.i4.s -75` → `bgt.s` skips; else `kind = 0` |
| **Ally** | effective goodwill **≥ +75** | IL_0049 `ldc.i4.s 75` → `blt.s` skips; else `kind = 2` |
| **Hostile → Neutral** | goodwill **≥ 0** | IL_0070 `ldc.i4.0 / blt.s`; else `kind = 1` |

**Hostility does not latch — but it does not un-latch where it latched.** You
fall in at −75 and only climb out at **0**. That is a 75-point trench, and staying
clear of it is the one hard constraint on your clamp.

---

### 1. Which mod supplies restraining bolts

**One mod. Only one. And it is not called what you think.**

| | |
|---|---|
| **Mod** | Outer Rim - Droid Depot |
| **packageId** | `Neronix17.OuterRim.DroidDepot` (`About.xml:6`) |
| **workshop id / folder** | **`3096501398`** |
| **path** | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3096501398` |
| **active** | yes — `ModsConfig.xml:549` |
| **supports** | 1.4 / 1.5 / 1.6; deps `Neronix17.Asimov` (active, line 61) + `Neronix17.OuterRim.Core` (active, line 536) |

⚠️ **The term in the game is "restraint bolt", never "restraining bolt".** Every
literal search for "restraining bolt" / `RestrainingBolt` / "inhibitor bolt" /
"slave circuit" across all 1242 workshop mods returns **zero**. The doctrine doc
should keep "restraining bolt" as our fiction but must not use it as a defName.

Swept the whole workshop tree: **Outer Rim Core, the BTD/KotOR packs, JDS
Separatist Droid Army and every other Star Wars mod supply no bolt-equivalent
device.** Outer Rim - Core only lists the item as trader stock
(`2919227155/1.6/Defs/TraderKindDefs/TraderKinds_Base.xml:91`).

### 2. 🔴 What SHAPE the application is

**The *state* is a plain vanilla `Hediff`. The *application* has THREE routes in
two assemblies.** That split is the whole answer.

All paths below under `…\294100\3096501398\1.6\` (1.4/1.5/1.6 copies are byte-identical).

| def | type | class | file:line |
|---|---|---|---|
| `OuterRim_RestraintBolt` | **HediffDef** | `HediffWithComps` ← **vanilla, no comps** | `Defs\HediffDefs\Droid_General.xml:30-53` |
| `OuterRim_RestraintBolt` | ThingDef | `ThingWithComps` | `Defs\ThingDefs_Items\Items_Droids.xml:4-51` |
| `OuterRim_AttachRestraintBolt` | RecipeDef | `Recipe_InstallImplant` ← **vanilla** | `Defs\RecipeDefs\Recipes_Surgery_Droid.xml:19-52` |
| `OuterRim_RemoveRestraintBolt` | RecipeDef | `OuterRimDroids.Recipe_RemoveBolt` | same file `:54-73` |
| `OuterRim_RestrainDroid` | JobDef | `OuterRimDroids.JobDriver_RestrainDroid` | `Defs\ThingDefs_Items\Items_Droids.xml:53-58` |
| `OuterRim_UseRestraintBolt` | JobDef | `JobDriver_UseItem` | `Defs\Misc\Jobs.xml:4-9` — ⚠️ **dead def, referenced nowhere** |

The attach recipe, verbatim (`Recipes_Surgery_Droid.xml:23,28,29,39`):
```xml
<workerClass>Recipe_InstallImplant</workerClass>
<targetsBodyPart>false</targetsBodyPart>
<isViolation>true</isViolation>
<addsHediff>OuterRim_RestraintBolt</addsHediff>
```
No `<recipeUsers>`, no `<appliedOnFixedBodyParts>`. It is attached from the pawn
side — `Defs\ThingDefs_Automatons\Humanlike\Droid__BaseHumanoidDroid.xml:159-160`
and `…\Animal\Droid__BaseAnimalDroid.xml:89-90`.
⭐ **`targetsBodyPart false` means it is a whole-pawn hediff** — `HasHediff(def)`
is a valid one-line test, with no body-part walk.

⛔ **It is NOT apparel.** ThingDef `category: Item`, `is.apparel = false`,
`tickerType: Never`. There is no `Notify_Equipped` / `Notify_Unequipped` to hook,
and no equip event of any kind. Prose implying a *worn* bolt is fine as fiction;
it must not become a requirement.

**Why the shape would have made this a project — and no longer does.** A hook on
"application" must cover **all three** live routes:

1. **Surgery** → vanilla `Recipe_InstallImplant` (shared with hundreds of implants).
2. **Item use** → vanilla `CompUsable` (`useJob UseItem`) → `Comp_TargetableOnAnyDroid`
   → `OuterRimDroids.Comp_TargetEffect_Restrain.DoEffectOn`
   (`1.6\Source\OuterRimDroids\Comps\Targetable\Comp_TargetEffect_Restrain.cs:15-28`).
3. **Downed droid** → `OuterRimDroids.JobDriver_RestrainDroid.Restrain()`
   (`1.6\Source\OuterRimDroids\Jobs\JobDriver_RestrainDroid.cs:46-52`), which calls
   `pawn.health.AddHediff(...)` **directly — no droid check, no violation, no goodwill.**

**Four moments, two assemblies, two of them shared vanilla classes.** That is the
"project" answer and it is the one you would have got last week.

⭐ **Counting the hediff collapses all four to zero.** Every route ends at the same
`HediffDef`. We read the result instead of intercepting the act — and the removal
recipe (`<removesHediff>`) is covered for free by the same read.

### 3a. Cheaply countable — **YES**

```csharp
PawnsFinder.AllMapsCaravansAndTravellingTransporters_Alive_OfPlayerFaction
    .Count(p => p.health?.hediffSet?.HasHediff(boltHediff) ?? false)
```

**This member satisfies your ownership ruling exactly**, and I verified the
cryptosleep clause rather than trusting the name:

- `PawnsFinder::get_AllMapsCaravansAndTravellingTransporters_Alive_OfPlayerFaction`
  IL_0021 `callvirt Thing::get_Faction` / IL_0027 `bne.un.s` — **filters on
  `Thing.Faction == Faction.OfPlayer`. Ownership, not presence.** Your rule, verbatim.
- It unions `AllMaps` + `AllCaravansAndTravellingTransporters_Alive`.
- `PawnsFinder::get_AllMaps` IL_002c → `MapPawns::get_AllPawns`.
- `MapPawns::get_AllPawns` IL_0000 → `get_AllPawnsUnspawned`, then IL_002d/IL_0039
  concatenates `pawnsSpawned` **plus** the unspawned set.
- `MapPawns::get_AllPawnsUnspawned` IL_0016 `ldc.i4.s 12 / ThingRequest::ForGroup`
  walks contained things recursively, dropping the dead at IL_0047 `Pawn::get_Dead`.

✅ **Cryptosleep caskets, containers and shelved droids are all counted** — the
undercount you flagged does not happen with this member. Caravans and travelling
transporters are in by name. A visitor's or raider's bolted droid in our base is
**out**. A droid sold is out the instant its `Faction` changes. Downed counts.

**Cost:** not cached — rebuilds its list per call, O(all pawns everywhere). At the
rate below that is free, but see the early-out in the build note; it is load-bearing.

### 3b. Periodic hook — **you do not need one**

`GoodwillSituationManager` already runs it.

```
FactionManager::FactionManagerTick  IL_0006 → GoodwillSituationManager::GoodwillManagerTick
GoodwillSituationManager::GoodwillManagerTick
    IL_000a: ldc.i4 1000
    IL_000f: rem
    IL_0010: brtrue.s IL_0019          ← only when TicksGame % 1000 == 0
    IL_0014: call GoodwillSituationManager::RecalculateAll
```

**Every 1000 ticks (~16.7 s real at 1×), plus on demand via `GetSituations`.**
No `GameComponentTick`, no `MapComponentTick`, no `WorldComponent`, no hediff tick.
We write a method; the engine decides when to call it.

### 3c. 🔴 Drift shape — **CONSTANT. "State a RATE" is dead.**

You were right to force this. `Faction::CheckReachNaturalGoodwill`, called from
`Faction::FactionTick` IL_0001:

```
IL_002a–IL_003e:  band = IntRange(NaturalGoodwill − 50, NaturalGoodwill + 50)
IL_0046:          if band.Includes(baseGoodwill) → naturalGoodwillTimer = 0; return
IL_0057:          naturalGoodwillTimer++
IL_006c:          ldc.i4 3000000                    ← below band
IL_0079:          if timer < 3000000 → return
IL_0084–IL_00ae:  TryAffectGoodwillWith(player, Mathf.Min(10, band.min − cur))
IL_00c5:          ldc.i4 3000000                    ← above band
IL_00dc–IL_0107:  TryAffectGoodwillWith(player, −Mathf.Min(10, cur − band.max))
```

**A flat ±10, at most once per 3,000,000 ticks, and only outside a ±50 dead band.**
3,000,000 ÷ 60,000 ticks/day = **50 in-game days**. Maximum drift the engine can
produce is **0.2 goodwill/day**, and inside ±50 of natural it is **exactly zero**.

**Constant, not proportional — the shape you feared.** A repeated-penalty design
is a step function: under 0.2/day it is absorbed entirely; over it, goodwill walks
to the floor regardless of N. **2, 12 and 40 bolts would NOT land at different
levels.** Your acceptance test fails on that route. Do not take it.

⚠️ **And it means `naturalGoodwillOffset` alone is nearly inert.** Moving *natural*
goodwill only re-aims a drift that needs 50 days to move 10 points, and does
nothing while current goodwill sits within 50 of the new target. **Setting the
level is necessary but not sufficient** — which is why the verdict is CAP, not
LEVEL, even though the same class provides both.

### 3c′. The ceiling — **exists, vanilla, and instant**

`Faction::GoodwillWith` — the value everything else reads:

```
IL_0002: call     Faction::BaseGoodwillWith
IL_000e: brfalse.s IL_0024                       ← if this is the player…
IL_0011: call     Find::get_GoodwillSituationManager
IL_0017: callvirt GoodwillSituationManager::GetMaxGoodwill
IL_001c: call     Mathf::Min                     ← effective = Min(base, maxGoodwill)
```

`GetMaxGoodwill` seeds **100** (IL_0008) and `Mathf::Min`s across every cached
situation (IL_0017). `GetNaturalGoodwill` **sums** every offset (IL_001b `add`).

**The cap applies the moment the cache recomputes — drift is not involved.**
`CheckKindThresholds` reads `GoodwillWith` (IL_0007), i.e. the *capped* value, so
the cap drives Hostile/Neutral/Ally directly. And after each recompute
`Recalculate` IL_0038 → `CheckHostilityChanged` →
`Faction::Notify_GoodwillSituationsChanged` IL_002a → `CheckKindThresholds`.

⭐ **So: free a droid, and within ≤1000 ticks the cap rises and the relation kind is
re-evaluated upward automatically.** Your "freeing droids stops the bleed" promise
holds mechanically, with **no removal hook at all** — provided base goodwill has
not itself been driven under 0 by real raids. That exception only exists if we go
hostile, which the clamp below prevents.

### 3c″. Is Duneborn "capped at +75, never allied" an existing mechanism?

`design\Jawa\worldbuilding\faction_roster_v2.md:2317`. **Yes — this exact
mechanism. And the number in the roster is off by one.**
Ally fires at `goodwill >= 75` (`CheckKindThresholds` IL_0049 `blt.s`), so a cap of
**75 still allows Ally**. To mean "never allied" the worker must return **74**.
Same class we are about to write; fix the roster in the same commit.

⛔ **Trap that would otherwise have cost a game load:**
`GoodwillSituationDef.baseMaxGoodwill` **is read by nothing.**
`xref.py GoodwillSituationDef baseMaxGoodwill` → referenced by 1 method,
`GoodwillSituationDef::.ctor [stfld]`, and that is all. **Writing
`<baseMaxGoodwill>` in XML has literally no effect.** Only the worker's
`GetMaxGoodwill` return value is used (`Recalculate` IL_0026). Likewise
`naturalGoodwillOffset` is read only by `GoodwillSituationWorker_MemeCompatibility`
and `_SameIdeo` — a custom worker must read the field itself or it is ignored.
Base `GoodwillSituationWorker::GetMaxGoodwill` returns a hardcoded `100`
(IL_0000 `ldc.i4.s 100`); `GetNaturalGoodwillOffset` returns `0`. **Both must be
overridden.**

### 4. Does anything else patch bolt application — **NO**

- **Zero PatchOperations** anywhere in the workshop tree target `OuterRim_RestraintBolt`,
  `OuterRim_AttachRestraintBolt`, `OuterRim_RemoveRestraintBolt`, `OuterRim_RestrainDroid`,
  `Comp_TargetEffect_Restrain` or `Recipe_RemoveBolt`.
- **Zero foreign assemblies** reference `Recipe_RemoveBolt` or `Comp_TargetEffect_Restrain` —
  only Droid Depot's own `1.4|1.5|1.6\Assemblies\OuterRimDroids.dll`.
- **Zero mods anywhere** contain `CheckReachNaturalGoodwill`.

⭐ **And the chosen mechanism is the least collision-prone available.** Adding a
`GoodwillSituationDef` is **additive**: `Recalculate` IL_000f iterates
`DefDatabase<GoodwillSituationDef>.AllDefsListForReading` and each worker
contributes independently via `Min`/`sum`. **Two mods can both add situations
without fighting** — which a Harmony patch on a shared vanilla method cannot promise.
Proof it works in *this* stack: **42 situation defs are live today**, three of them
added by `llunak.moreprecepts` (`ModsConfig.xml:175`).

⚠️ **Neighbours to be aware of — active, and touching the same pipeline:**

| mod | `ModsConfig.xml` | what it does |
|---|---|---|
| `guy762.MM.KotORCore` | 577 | `Faction_CanChangeGoodwillFor_Postfix`, `GoodwillSituationWorker_PermanentEnemy_ArePermanentEnemies_Postfix` — **closest neighbour; a Star Wars mod rewriting goodwill rules** |
| `jaeger972.factionterritories` | 436 | patches `CanChangeGoodwillFor`, has `GoodwillToMakeHostile` |
| `azravos.factioncustomizer` | 147 | references `GoodwillSituationWorker` and `GoodwillSituationManager` |
| `ebsg.framework` | 25 | references `GoodwillSituationManager` |

None patch `GetMaxGoodwill` or `Recalculate`'s iteration, so none blocks us — but
if the cap ever reads as not applying, **`guy762.MM.KotORCore` is the first place
to look**, because it postfixes the gate our value flows through.

---

## ⛔ What the doctrine document cannot have as written

**1. "offset = −2.5 × N clamped at −100" declares war at 30 droids.**
Hostile is ≤ −75, and −2.5 × 30 = −75. **Clamp at −70, not −100** — margin, because
other negative situations stack via `Min` and are not exclusive.

**2. Make it a CEILING, not an offset — and your acceptance test passes.**
`maxGoodwill = 100 − 2.5N`, floored at −70:

| bolts | ceiling | what the player lives with |
|---|---|---|
| 2 | +95 | nothing lost; the dabbler is fine, as you required |
| 12 | +70 | **alliance now out of reach** — the first real bite |
| 40 | 0 | permanently neutral at best. No aid, no alliance, ever |
| 68+ | −70 | floor. Still **not** war |

⭐ **2, 12 and 40 land at visibly different levels, and drift is not an opponent** —
it carries the player *up* to the cap and stops, exactly as you hoped. And bolts
set **how much they help you, never whether they shoot**, which is your rule
expressed in the engine's own arithmetic rather than approximated by it.

**3. ⛔ "Bolt = minus. Unbolt = plus" describes a transaction that does not happen.**
There is no credit and no ledger. The count drops, the ceiling rises within 1000
ticks, and goodwill the player already earned becomes visible again. **This is a
better fit for the doctrine than a refund** — the Enclaves do not *reward* you for
stopping, they stop objecting. But the two-numbers framing should be reworded, or
whoever builds it will look for a payment that has nowhere to live.

**4. ⭐ The UI is free, and it is the beat you wanted.**
`GoodwillSituationManager::GetExplanation` IL_0048 appends each cached situation's
`LabelCap` to the faction card. **The player opens the Factions tab and reads a
line naming restraining bolts, with zero custom UI.** That is "somewhere a network
is counting", delivered by vanilla. Set `naturalGoodwillOffset` for this reason —
for the explanation line, not for effect.

**5. ⚠️ A live bug in Droid Depot will make us count things that are not droids.**
`1.6\Source\OuterRimDroids\Comps\Targetable\Comp_TargetableOnAnyDroid.cs:51-55`:
```csharp
pawn = t as Pawn;
if (pawn != null && pawn.def.HasModExtension<DefModExtension>())
    return true;
```
It tests the **base class** `DefModExtension` instead of `DefModExt_Droid`, so the
bolt can be aimed at **any pawn whose def carries any mod extension at all —
humans from other mods included.** A bolted human colonist would be counted by our
worker and would read to the Enclaves as an enslaved droid. **Not our bug and not
worth patching**; decide whether the worker filters to droid defs or accepts it.
⭐ I would **accept it**: "they object to the act, not the victim" is more in
character than a species check, and it costs us nothing.

---

## Build note — what this actually is

**One XML def + one C# class, ~40 lines, no Harmony.**

```xml
<GoodwillSituationDef>
  <defName>Jawa_RestrainingBolts</defName>
  <label>restraining bolts</label>
  <workerClass>RimMandrake.GoodwillSituationWorker_RestrainingBolts</workerClass>
</GoodwillSituationDef>
```

```csharp
public class GoodwillSituationWorker_RestrainingBolts : GoodwillSituationWorker
{
    public override int GetMaxGoodwill(Faction other)
    {
        if (other?.def != JawaDefOf.FreeDroidEnclaves) return 100;   // early-out FIRST
        return Mathf.Max(-70, 100 - Mathf.RoundToInt(2.5f * BoltedCount()));
    }
}
```

🔴 **The early-out is load-bearing, not tidiness.** `Recalculate` runs **every**
situation worker for **every** faction with `HasGoodwill`, on every recache — 42+
defs × the faction list — and `PawnsFinder.…_OfPlayerFaction` rebuilds its list on
each call. Return 100 on the faction check *before* counting, and the real walk
happens once per 1000 ticks instead of hundreds of times.

**Dependencies:** the Free Droid Enclaves `FactionDef` (unbuilt — `V1_SCOPE.md`
defers it), and the bolt hediff. Resolve the latter with
`DefDatabase<HediffDef>.GetNamedSilentFail("OuterRim_RestraintBolt")` and return
100 if null, so the assembly degrades quietly if Droid Depot is ever dropped
rather than throwing on every recache.

`[v2]` — lands with the Enclaves.
