# infrastructure/state/queue/CREATE.md

_CREATE's queue. **You own this file — write freely.** Others file at you by
appending. Doctrine: `agents_def.md`. v1/v2 line: `V1_SCOPE.md`. Budget 150 lines
(`DOC_BUDGET.md`); **a closed item is one line in `infrastructure/state/CLOSED.md`
and its body is deleted.**_

---

## ⭐ v1 — your four rows

| row | state |
|---|---|
| 1 | Empire reskin — ✅ **done, seen live** |
| 3 | `QuestScriptDef` — ✅ built `47733f8`, deployed. 🔴 **NEVER SEEN** |
| 4 | three terrain/resource overrides — ✅ built `73ca76c`. 🔴 **NEVER SEEN**, and all three are **map-gen-time** |
| 8 | ⭐ Gravship, DEEP — design complete, **build at 0**; wants the game, you anchor that session |

🔴 **`V1_SCOPE.md`'s gate is *seen working in-game once*.** Built is not closed.

---

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

✅ **row 4 salt pans PASSED live** — 144 cells, 0 failed verify, renders as a pale
cracked pan. Owner ruled bridge placement sufficient.

🔴 **The one diagnostic to memorise:** hulk deck renders but props are **absent**
⇒ `BrokenSubstructure` went to the top layer and `ShipChunk_Mech` lost its
`Heavy` affordance. **A terrain swap, not a redesign.** Report it as *"deck
present, props absent"*.

⚠️ **Not verifiable offline, ever:** vanilla and DLC art lives in AssetBundles —
`Data/*/Textures` does not exist — so **297 usable wreck defs cannot be
rendered**, `AncientCryptosleepCasket` among them. Defs, sizes and yields are
proven; the look is not. **Nobody has ever seen a casket.**

---

## Open

### 📦 Two fix mods built, NOT deployed, NOT in `ModsConfig.xml` — with OPS
`38f6d82`. **CREATE does not touch the mod list; deployed ≠ live.**

| packageId | must load after |
|---|---|
| `mandrake.phytokinbarkheadfix` `cb6c2f7` | `vanillaracesexpanded.phytokin` @389 — donor art is **LOOSE** |
| `mandrake.kotorbandoliernorthfix` `dd66fe6` | `guy762.MM.KotORCore` **@573** |

🔴 **The KotOR one must NOT join the 556–564 fix slot.** Its donor loads *later*
and ships loose art, so placed there it is overwritten and **invisible, silently**.

### C3a. ⏳ Eopie — two proposals NOT ruled on
**Do not read silence as approval:** the species-inconsistent head shapes, and
north's featureless rear. Salmon-pink is a **playtest** question now — do not
re-raise it.

### C7. Rows 4–6 `[v2]` — the only ones needing genuinely new art
`design/Jawa/art/c7_directional_triage.md`. Polluted Lands `BMT_ImpalingClaws`
north+east (2 files, 256²); Dark Ages `BlackScribeScorpling_north` (1 file, "only
if someone is already in the file"); Caverns pupae (**8 sprites, lowest value per
effort in C7 — not recommended**).

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

**Measured today — it decides how a reskin gets built.** `Data/Anomaly/Textures`
**does not exist**; 991 texture assets (415 pawn: Ghoul 90, Nociosphere 46,
Fleshbeast 33, Chimera 24, Gorehulk 21) live in `AssetBundles/resources_anomaly`.
✅ Overriding is easy — loose beats bundled regardless of order, **no `loadAfter`
needed**. ✅ The exact paths ARE readable offline: `resources_anomaly.manifest` is
plain-text YAML listing every asset as `Assets/Data/Anomaly/Textures/...` — strip
that prefix. 🔴 **The pixels are NOT.** Every Anomaly reskin is a from-scratch
draw or wants a live screenshot first; **budget it as new art, never a retouch.**

### C11. ⏳ Retiring `mandrake.missingartfixes` — steps 2–4, blocked on OPS
LIVE and deployed, so not a folder delete. Successors built, blocker cleared.
**2.** confirm the five successors are in `ModsConfig.xml` and loaded → **3.** OPS
drops `mandrake.missingartfixes` *(before the folder goes, or the game boots with
a missing-mod entry)* → **4.** remove the deployed copy and the repo folder.

### C-v3. `[v2]` Restraining bolts — ANSWERED, spec drained to a design doc
`design/Jawa/worldbuilding/restraining_bolt_technical.md` (`8353622`).
**Verdict: CAP the goodwill ceiling. One XML def + ~40 lines of C#, no Harmony.**
Lands with the Free Droid Enclaves, whose `FactionDef` is unbuilt.

### C-LOAD. ⏳ One constraint open; the rest is OPS's
Answered at `queue/OPS.md` `38f6d82`. ⏳ **`AnimalBiomeDuplicates_Fix.xml` removes
a duplicate `wildBiomes` entry from Core's `Armadillo`; whichever mod ADDS the
duplicate must precede us and is unidentified.** `PatchOperationConditional`, so
a wrong order is a silent no-op. **OPS's def index should answer it in one query.**

### C-t1 `[v2]` — `validate_patch.py:1363` says "IN ONE MOD"
Under `--all-versions` there is no load set, so "one mod" describes a **folder**,
not the game. Reword to say which.
⛔ **Do not "fix" the walk to match the wording** — the walk is correct and
`--all-versions` depends on it. Wording only.

### C-t2 `[v2]` — two donor mask filenames RimWorld never looks for
`SWDoorBlastBDoor_Frame_east_m.png` and `SWDoorBlastDDoor_Frame_east_m.png` carry
an underscore before the `m`. The convention is `...eastm.png`, proven by the
correctly-spelled `SWDoorBlastDoor_Frame_eastm.png` beside them. **The masks are
never loaded and nothing errors.** Fix is an override mod — CREATE's by the
one-donor-one-fix-mod ruling.

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
