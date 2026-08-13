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
| 3 | One `QuestScriptDef` that fires and resolves. Any premise. | 🟢 **NO — pure XML, closable offline today** |
| 4 | Three terrain/resource overrides visible on the map | 🟢 **NO — pure XML, closable offline today** |
| 8 | ⭐ Gravship, DEEP — design complete, build at 0 | 🔴 build wants the game; you anchor that session |
| 1 | Empire reskin — ✅ built and seen live | ✅ done |

⚠️ **Rows 3 and 4 are at zero because nobody saw they were closable, not because
they are hard.** Author both offline, deploy with row 2, verify in ONE session.

---

## Open

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

⏳ **Fix 1 (south neck) in flight**, then regenerate
`Source/REVIEW_all_three.png` so the owner reviews the same sheet layout twice.
Still held awaiting approval either way.

🔴 **Pillow is NOT on the system `python3` here** — every build script in this
mod imports PIL and would die. It is installed at
`/home/mandrake/.venvs/art/bin/python`; use that interpreter for anything that
touches an image. The queue records a peer hand-decoding IHDR and inflating IDAT
to avoid this; that is no longer necessary.

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

👁️ **One vanilla item to eyeball, do NOT patch blind:** Biotech `Eyes_Red` ships
only `RedEyes_Female_east` plus a non-directional `RedEyes_Male`, while every
sibling face-feature ships east+south — but the log has **zero** `Failed to find
any textures at`, which a bare male file should have produced. Eye rendering likely
has a special path. Look at a red-eyed pawn first.

### C8. `check_sprite.py` — art intake validator
512×512, real alpha, zero saturated pixels, value distribution, bounding box,
south/north silhouette parity. **Build it before commissioning any art**, not after.

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

### C2. Space Tower — technical due diligence `[v2]`
**Split out of `TODO.md` §17.** The on-brand/endgame-fit judgement went to VISION;
the technical half is yours: is either mod actually active in the running game,
what is the licence, and does it conflict with CQF. Do not spend time on this until
VISION rules the concept in — the design call gates the checks, not the reverse.

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
- **Row 4** — three terrain or resource overrides visible on the map.

🔴 **The finding row 3 turned up, and it outlives row 3.**
`everAcceptableInSpace` gates **acceptance by the player, not site placement** —
Core `Languages/English/Keyed/MainTabs.xml` L198 `QuestNotSpace` = "cannot accept
in space", sitting in the accept-requirement string run; Odyssey's six genuinely
orbital sites set it zero times while Core's `Script_TradeRequest.xml` sets it
true *and* forces its target ground-only. **Core's own
`OpportunitySite_ItemStash` omits it, so vanilla's quest offers go silent while
the colony's map is a space map.** VISION has ruled (`95e500a`): flip the default
for what we author, judge adopted quests one at a time, and **do not sweep** —
the impact turns on how much of the campaign is spent on the Orbit layer, which
is not answerable offline.

Both are pure offline XML. They are the ONLY offline v1 work left, and they must
be **authored and deployed before the next live session** — that session
generates the world and cannot close them if they do not exist yet.

## C-v2. `validate_patch.py` is yours — owner ruled 2026-08-13
It reads `Patches/` only, never `Defs/`, and does not say so. Fix the gap or
document it; either closes the item.
