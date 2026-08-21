# TEST_PLAN.md — how to prove deployed material actually works

**Owned by CHECK.** It is the in-game verification script for material that is
already deployed and enabled: the art-fix mods, the rumour quest, the terrain
overrides and the ground hulk. CHECK drives the bridge and runs it; BUILD owns
what the material is meant to do and answers questions about intent.

🔴 **`infrastructure/state/V1_CHAIN.md` is the authority on what v1 is and which
steps are open.** This file says *how to look*, never *whether it still matters* —
read the chain before spending a load on any part below.

Three standing rulings bound this file:
- **Art fixing is PARKED.** Everything in Part 1 and Part 5 is **observation
  only**. A row that comes back looking FINE is a result, not a disappointment,
  and no fix is scheduled off it.
- **The terrain overrides are CLOSED** — scrapfields ships at whatever density it
  produces. Part 3 survives as the procedure for looking at terrain, not as an
  open gate, and **no count is a pass/fail threshold**.
- **Worldgen is the owner's, by hand.** Nothing here needs or schedules a campaign
  world. A quicktest map is always enough.

---

## The two rules that govern every check here

🔴 **A screenshot is the evidence. A def query is not.** The gate is *seen working
in-game once*. `take_screenshot` returns a path — **open it and look at it.**
Everything in this file fails in ways that produce **no log line at all**, which
is exactly why the log cannot close any of it.

🔴 **Clear the debug log window before shooting.** It eats the frame, and stale
lines read as fresh failures. Clear → act → shoot. Shoot **before and after**
where a transition is the claim: one image proves a state, two prove a change.

⚠️ **The failure mode this material has, over and over: silence.** A missing
directional texture only logs `Failed to find any textures at` when **every**
direction is missing — a single absent facing silently falls back to another one.
A blank-but-present PNG loads successfully by every test the engine has. A
loose-art mod ordered wrong deploys, loads, throws nothing, and is simply
invisible. **In all three cases the log is clean and the art is wrong.**

⚠️ **Magenta is the other one.** A texture that failed to load renders as the
magenta placeholder and nothing reports it. If any shot below comes back
magenta, that is a real failure even though everything "worked".

---

## 🔴 PRE-FLIGHT — nine corrections. Read before typing at a live console.

Verified offline; do not re-derive. **These change what you TYPE.** Two are wrong
parameters, one is a diagnostic string with no basis, and one names a def that
does not exist. The rest of this file is still the script.

| # | correction |
|---|---|
| 1 | 🔴 **Part 3b's affordance diagnostic has NO BASIS.** `ShipChunk_Mech` needs **`Light`** (inherited from `BuildingBase`), not `Heavy`; and `BrokenSubstructure` supplies Light/Medium/Heavy/Walkable/Substructure — its `<affordances>` has no `Inherit="False"`, so it MERGES with `FloorBase`'s. Requirement and supply are met on **either** layer ⇒ if props are missing, look at prefab placement, blocked cells or `spotMustBeStandable` — **not** the affordance |
| 2 | ⚠️ **Scrapfields is NOT biome-gated.** `Patches\JawaResource_Scrapfields.xml:56-59` adds the GenStep to `MapGeneratorDef[Base_Player]` with no biome filter. A scrapfield on a non-desert quicktest is not a bug |
| 3 | 🔴 **`jawa/set_terrain` takes `terrainDef`, not `def`.** The bridge **drops unknown params silently** before the tool runs, so `def=` does not error — it paints nothing and costs live minutes to notice. Read the cell back with `rimworld/get_cell_info` → `terrainDefName` |
| 4 | 🔴 **`ToolBelt` does not exist** — zero hits on disk. It is **`VAEA_Apparel_ToolBelt`**, `...\294100\2521176396\1.6\Defs\ThingDefs_Misc\Apparel_Utility.xml:531`. It and Survival Tools' rival are both labelled *"tool belt"* ⇒ **spawn by defName, never by label** |
| 5 | 🔴 **The four RR research kits are APPAREL and must be WORN.** The fix replaces `wornGraphicPath` (`Apparel_FieldKits.xml:62`); the ground `texPath` (`:51`) is one directionless PNG, so a kit on the ground exercises **none** of the fixed art. There is no apparel tool on the bridge: the only route is `rimworld/select_pawn` then `Actions\Wear apparel (selected)…`, which works on **player colonists only** ⇒ spawn the wearer with `faction=player` |
| 6 | **`AV_DogSled` is a `Vehicles.VehicleDef`, not a ThingDef.** `spawn_thing`/`ThingMaker` genuinely cannot construct it; **`jawa/spawn_batch`** routes vehicles through `Vehicles.VehicleSpawner.SpawnVehicleRandomized` by reflection. Its brown comes from a def patch (`DogSledTint_Brown.xml`, `graphicData/color` → `(99,65,24)`) ⇒ **a grey sled means the patch, not the art** |
| 7 | **`VGE_Astronaut` has two lifeStages sharing one maskPath**, and only the double-r `Astrronaut` files were typo'd ⇒ **shoot an adult**, or you pass on art that was never broken |
| 8 | ⛔ **The C12 double-ship warning is STALE and names the wrong mod.** The real overlap was `MissingArtFixes`, all seven pairs md5-identical, now inactive. **If a row looks wrong, load order is NOT the suspect** |
| 9 | ⚠️ **The Part 1 table covers eight mods; ten art-fix mods are live.** `mandrake.phytokinbarkheadfix` and `mandrake.kotorbandoliernorthfix` are deployed but untabled — see Part 1b, which is why. **Read `ModsConfig.xml` for the active list; never a count written in a doc** |

⚠️ **`jawa/spawn_thing` DOES NOT EXIST.** The single-thing call is vanilla
`rimworld/spawn_thing`; `jawa/spawn_batch` is for more than one.

---

## Part 1 — the EIGHT live mods. Cheapest first, all doable on any map

Seven art-fix mods plus the sled reskin. `mandrake.missingartfixes` is out of the
list; **the two mods enabled at 23:18 were pulled again on the owner's ruling** —
see Part 1b, which is why.
Each is *one spawn and one look*. Nothing here needs a fresh map or a colony.

🔴 **THIS PART IS THE OWNER'S VERIFICATION GATE, not a victory lap.** The standing
directive stops all new art fixes *until the owner has verified the art actually
does not work* — because the missing-art premise itself is suspect. **So a row
that comes back looking FINE is the valuable result**, not a disappointing one.
Record what you see, not what the row predicts, and **schedule no fix off it.**

| # | mod | spawn / find | look at | PASS looks like |
|---|---|---|---|---|
| 1 | `DesertVehicleReskin` | ⚠️ `AV_DogSled` is a **`Vehicles.VehicleDef`**, not a ThingDef — a plain `spawn_thing` may not construct it | all three facings, then rotate | **two eopie**, not four dogs; **sled body BROWN**, not grey. 🔴 **Grey sled ⇒ suspect the DEF PATCH, not the art** — the brown comes from `Patches/DogSledTint_Brown.xml` replacing `graphicData/color` with `(99,65,24)`, so zero pixels carry it |
| 2 | `BlastDoorFrameAsyncFix` | buildings `PH_DoorBlastCDoor`, `PH_DoorThickBlastBDoor`, `PH_DoorBlastDDoor` | each rotated **EAST**, door open and closed | the frame's inner rim draws **in front of** the moving leaves; D-door keeps its iris ring |
| 3 | `ResearchKitEastFix` | 🔴 **They are APPAREL and must be WORN.** `RR_FieldResearchKitSimple`, `…HiTech`, `…MultiAnalyzer`, `…Remote` | **worn by a pawn facing EAST** | four visible kits; none blank, none magenta. ⚠️ **Dropping them on the ground exercises NONE of the fixed art** — the fix replaces `wornGraphicPath` (`Apparel_FieldKits.xml:62`); the ground `texPath` (`:51`) is a single directionless PNG that was never broken |
| 4 | `GravshipAstronautFix` | pawn kind `VGE_Astronaut` — ⚠️ **spawn BOTH life stages** | facing **NORTH** | a body, and its **faction-colour overlay** present. 🔴 **The ordinary adult's `Mech_Astronaut_north.png` was NEVER broken** — only the double-r `Astrronaut` files were, so checking the wrong life stage passes a row that was never at risk |
| 5 | `MSEDroidFix` | pawn kind `OuterRim_MSEDroid` | facing **NORTH** | a droid, not an invisible or south-facing fallback |
| ~~6~~ | ~~`CereanManeFix`~~ | — | — | ⛔ **CLOSED 2026-08-21, owner's ruling: "completely close all Cerean hair items".** Its target mod `Neronix17.OuterRim.GalacticDiversity` is installed but NOT in `ModsConfig`, so the HairDef `OuterRim_CereanMane` never loads and the fix cannot be exercised. Reopen only if that mod is activated. |
| 7 | `SauridFrillFix` | a Saurid pawn, hair `VRESaurids_Littlefoot` | facing **NORTH** | the centre frill draws |
| 8 | `ToolBeltFix` | 🔴 apparel **`VAEA_Apparel_ToolBelt`**, worn | facing **WEST** | the belt draws on the pawn |

---

## 🔴 Part 1b — THE BASELINE SHOTS. This is the highest-value thing in the file.

**Owner's ruling, 2026-08-14: the evidence that unblocks all art work is an
in-game screenshot of the SUSPECT AS IT CURRENTLY RENDERS — no fix, no
comparison.** Three of my fixes were deliberately **pulled from this load** so
that these three shots show the donors' own unmodified art.

⚠️ **Do not report these as failures.** They are not tests. **Whatever they look
like IS the result**, and "this looked completely normal" is the single most
useful sentence you can send back — it is what the directive suspects.

| # | shoot | how to reach it | what is claimed to be wrong |
|---|---|---|---|
| B1 | a **female** Phytokin head, **facing EAST** | needs genes `VRE_BarkSkin` **+** `Jaw_Heavy` | claim: a front-facing head renders on a side-facing body, because the donor ships no female east |
| B2 | a pawn wearing `bandolier_chewbacca` or `bandolier_traveler`, **facing NORTH** | worn apparel, KotOR Resources | claim: the chest pouches draw on the pawn's **back**, at layer 65, on top of everything |
| B3 | a `GravshipGenebank`, **rotated NORTH** | 1×1 Biotech buildable | claim: the north view is pixel-identical to the south, so its open front points at the viewer |

🔴 **`mandrake.phytokinbarkheadfix` and `mandrake.kotorbandoliernorthfix` are OUT
of `ModsConfig` for this load, and the genebank texture is held out of the
deploy.** If any of B1–B3 looks *correct*, the fix was unnecessary and the
premise behind it was wrong — which is exactly what the owner wants to know.

⚠️ **Rows 4–8 are pawn-facing checks, so the pawn must actually face that way.**
`jawa/set_pawn_rotation` exists but **has never executed**. If it fails, the
fallback is to draft the pawn and order a move so it turns, or shoot it walking.
✅ **That is ONE call now, not two** — `jawa/order_pawn` shipped `8043c51` with
`draft=true` included, and returns the read-back position.
Do not report the art broken on the strength of a rotation call failing.

⛔ **My `C12` double-ship warning was STALE and named the wrong mod. Struck.**
`Jawa_Patches/Textures/` holds exactly two PNGs and neither collides. The real
overlap was `MissingArtFixes`, whose seven pairs are **md5-identical** — so it was
never a rendering hazard at all — and it is now inactive.
**If rows 4 or 7 look wrong, load order is NOT the suspect.**

🔴 **Row 8's def name was wrong until now: `ToolBelt` does not exist anywhere** —
not in the workshop tree, not in `Mods/`, not in `Data/`. ⚠️ **Two different mods
label an item "tool belt"** (VAEA's and Survival Tools'), so typing the *label*
is ambiguous. Use the defName.

---

## Part 2 — the rumour quest. No fresh map needed

Deployed inside `Jawa_Patches`. `jawa/fire_quest` is the tool route; the
right-click float menu below is the manual one.

1. Clear the debug log.
2. Spawn item **`Jawa_ClaimRumour`** (labelled **salvage rumour**).
   → **SHOT A:** the item on the ground. Proves the texture loaded and is not
   magenta — this icon was drawn today and has never rendered in game.
3. Select a colonist, right-click the item, choose **"Read the rumour"**.
4. Open the **Quests** tab.
   → **SHOT B:** the quest **"The Claim"** present, with its offer text.
5. Click **Accept**.
   → **SHOT C:** the accepted quest and its letter.

**PASS = the quest reaches ANY end state.** Success, failure, or expiry all
count. Do not hold it open waiting for a caravan to complete it.

⚠️ **One thing I could not verify offline and would like looked at:**
`QuestNode_SetItemStashContents` has exactly **one** shipping usage in the whole
game, and it lists a *non-stackable* item — so vanilla never exercises the
stackable case. The haul should be **1 advanced component, 8 components, 4 steel
slag**. If the component count is wildly off, that is the reason, and the fix is
the number of `<li>` lines. **The quest fires and resolves either way** — this is
a note, not a gate.

⚠️ The quest sets `everAcceptableInSpace` true. If the colony is on the ground
this changes nothing; it exists so the offer still reaches the clan aboard the
ship.

---

## Part 3 — terrain. **Needs a NEWLY GENERATED map**

⚠️ **This row is CLOSED** — the overrides ship at whatever density they produce,
and **no chunk count is a threshold.** What survives is the procedure: how to look
at terrain without fooling yourself. Use it when terrain is being looked at for
some other reason; do not spend a load closing it.

Deployed inside `Jawa_Patches`. **All three overrides run at MAP GENERATION.** They
cannot appear on a map that already exists — including a campaign map generated
before the deploy landed. 📌 **A one-shot generator's output dates the DEF THAT
BUILT IT, not the def on disk.** Before counting anything a GenStep placed, ask
when the map was made.

🟢 **A quicktest map counts.** `rimworld/start_debug_game_ready` makes one in ~30
seconds, and per the owner's rule 1c the bridge-holder may create and destroy dev
colonies freely. **Do not wait for the campaign world to prove these.**
⚠️ That call **exceeds the 30 s timeout and succeeds anyway** — do not retry, or
you get a second map. Reconnect and poll `list_pawns`.

Biome matters **for rows 1 and 2 only**: generate in **Desert**, **ExtremeDesert**
or **AridShrubland**.
⚠️ **Row 3 is NOT biome-gated** — corrected 2026-08-13. `Jawa_ScatterScrapfields`
registers into `Base_Player` genSteps, so **any** fresh map shows it. Do not
report it as failed because the biome was wrong.

| # | override | what to look for | PASS |
|---|---|---|---|
| 1 | **Salt pans** (`Jawa_SaltCrust`) | broad **pale cracked** patches in low ground | ✅ **ALREADY PASSED LIVE** — 144 cells, 0 failed verify. Only "does it generate" is left |
| 2 | **Dune seas** (widened `SoftSand`) | 🔴 **DO NOT EYEBALL THIS** | **not a look.** 0.65→0.55 is a *density* change and is unjudgeable without a control map — "compare against memory of a normal desert" is not evidence. **Read the live `BiomeDef` and confirm `terrainPatchMakers` shows `0.55` (Desert) and `0.50` (ExtremeDesert)**, plus the new AridShrubland maker at `0.70`. Source of truth: `src/Jawa/Jawa_Patches/Patches/JawaTerrain_DuneSeas.xml` |
| 3 | **Scrapfields** | steel slag chunks strewn across open ground, with machine-bits filth | **no count gate — it ships at whatever density it produces.** 🔴 **LOOK BEFORE ANY DESTROY** — the last map's evidence died in a 43,288-thing wipe. ⚠️ `isJunk` makes the count the product of the tile's `TileMutatorDef.junkDensityFactor`, and **`Dunes` is one of five live mutators whose factor is ZERO** — on such a tile it places nothing, silently, with no warning |

→ **SHOT for rows 1 and 3**, zoomed out enough to show it is a *field*, not one
tile. **Row 2's evidence is a def read pasted as text, not a screenshot** — a
photograph of sand cannot settle it.

🟢 **Free shortcut for #1 that needs no map at all:** `Jawa_SaltCrust` is an
ordinary `TerrainDef`, so the bridge can **paint** it onto the current map —
`jawa/set_terrain terrainDef=Jawa_SaltCrust`, a ~10×10 rect. That proves the **art and
the def**, which is most of the risk, and leaves only "does it generate" to the
fresh map. It paints over whatever was there; **that is not a reason to defer
it.** Map preservation is ⏸️ **suspended** — the bridge-holder may create, paint
and destroy dev colonies freely. Paint it wherever you stand.
**Say which map the result came from** — quicktest and campaign are different
claims, and that is evidence hygiene, not preservation.

🔴 **The parameter is `terrainDef`, not `def`** — the real signature is
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs:69`,
`SetTerrain(x, z, terrainDef, width, height, layer, refresh)`. **The bridge drops
unknown params silently before the tool runs**, so `def=` would not have errored:
it would have painted nothing and cost live minutes to notice.

⚠️ **The art is REUSED, not drawn.** `Jawa_SaltCrust` points at Odyssey's own
`Terrain/Surfaces/DryLakeBed`, which Odyssey declares but never generates. A retired
seat ruled purpose-drawn salt art is **v2** and this is fine for v1. If it looks like
a dry lake bed, that is correct, not a bug.

⚠️ **Geological Landforms wins on landform tiles.** It hard-writes terrain there,
and its *own* dry-lake landform hard-codes `SoftSand`. So the one feature that
ought to be a salt pan will not be. Ruled: leave it. **Do not report this as a
failure of override #1** — check somewhere off a landform.

### Part 3b — the GROUND HULK. Same map, same run as Part 3.

**619 cells** stamped from our
own exported ship layout: a torn-open cryptosleep hold, three banks of
`AncientCryptosleepCasket` (31), `ShipChunk_Mech` scattered between them, deck
interleaved 45% `BrokenSubstructure` / 55% intact.

> **The fiction, so you know what you are looking at:** the flyable gravship is
> the part the clan got working. **This is the part that stayed on the ground** —
> the hold of a colony that never landed. The breach is where Hutt scrappers cut
> in to take the cargo; the Jawas are the second scavengers on this wreck.

| # | check | PASS |
|---|---|---|
| 1 | it **generated at all** | a ship-shaped wreck somewhere on the map. It is stamped by a `GenStep` at order 940, so it claims its rect before the junk prefabs and slag |
| 2 | 🔴 **the caskets are THERE** | 31 of them, in three touching banks. **See the trap below — this is the one likely failure** |
| 3 | the deck reads as **damaged, not patterned** | irregular broken patches, not a checkerboard and not a solid slab |
| 4 | 🔴 **the caskets LOOK right** | ⚠️ **nobody has ever seen them.** Vanilla art ships inside AssetBundles, so defs, sizes and yields are verified on disk and **the appearance is not**. This sighting is the only thing that closes it |
| 5 | a colonist can **walk onto and across it** | ✅ **now a measurement, not a guess** — `jawa/order_pawn` shipped `8043c51` and returns the pawn's **read-back position**, not a job-accepted bool. Order a colonist onto the hulk and compare where they end up. `pathCost 0`; if they path around it, the terrain went in wrong |

→ **SHOT: the whole wreck from a zoomed-out view**, and a second closer on a
casket bank.

⛔ **The affordance diagnostic once written here — that a top-layer `Substructure`
exposes only the `Substructure` affordance and that `ShipChunk_Mech` needs
`Heavy` — is FALSE in both halves. Do not act on it and do not report its
phrase.** (Pre-flight correction 1.)

- `ShipChunk_Mech` needs **`Light`**. `ParentName="ShipChunkBase"` →
  `BuildingBase`, and neither sets `terrainAffordanceNeeded`, so it inherits
  `Light` from `Data\Core\Defs\ThingDefs_Buildings\Buildings_Base.xml:11`. The
  `Heavy` in that Odyssey file belongs to `GravshipComponentBase`, a **different**
  abstract that `ShipChunk_Mech` does not descend from.
- `BrokenSubstructure` supplies **Light/Medium/Heavy/Walkable/Substructure**. Its
  `<affordances>` carries no `Inherit="False"`, so RimWorld list-merge APPENDS to
  `FloorBase`'s set (`Data\Core\Defs\TerrainDefs\Terrain_Floors.xml:6-11`).

⇒ **Requirement and supply are satisfied on EITHER layer, so the
foundation-vs-top question does not gate the props.** If props come up missing,
look at prefab placement, blocked cells, or `spotMustBeStandable`.

⭐ **The lesson is bigger than the hulk: I inferred an affordance from a def's
NAME and from which file the value sat in.** `Heavy` was in the same Odyssey file
and belonged to a sibling abstract; `isFoundation: true` sounded like it would
narrow the affordance list when the merge widens it. **Walk the ParentName chain
and check for `Inherit="False"` — never read a value's neighbourhood as its
owner.**

⚠️ **Two known-and-ruled non-bugs, so you do not file them:** the breach does
**not** aim at the colony (aiming needs C#, ruled v2 — pinned rotation only), and
each casket carries an explosive comp, so destroying one in a touching row can
chain. Deconstructing cannot. Both deliberate.

---

## What a FALSE PASS looks like — read before reporting anything green

- **"No red errors"** — proves nothing here. Every failure mode in this file is
  silent.
- **A def query returning the def** — proves it loaded, not that it *renders*.
  Rows 3 and 4 cannot be closed this way.
- **Row 4 checked on the pre-existing campaign map** — the overrides are
  map-generation-time and will be absent whether they work or not.
- **A facing checked without the pawn actually facing that way** — the engine
  falls back silently, so you may be looking at `_south` and calling it `_north`.
- **Art judged at 100 % zoom.** The east sled muzzle passed every offline check
  and was still wrong at play scale, as per the trap file. **Judge at the zoom you
  play at.**

---

## What I want back

Per item: **PASS / FAIL / NOT RUN**, and the screenshot path. For a FAIL, the
shot plus what you saw — I do not need a diagnosis, I need the image.

File findings at `infrastructure/state/queue/CHECK.md`. Anything that is a
**donor-side** defect rather than ours goes to `design/V2_DREAMS.md` with `[?]` —
it is not v1 and must not take window space.

---

## 🔴 Part 5 — the three §7-parked fix mods: defNames, and the FACING that tests each

Resolved offline 2026-08-14 against the installed donors. **The facing is the
whole point — only ONE rotation is broken in each**, so a shot from the wrong
side is a false pass.

⭐ **All three are HairDef or apparel texPaths, not pawnkind art. Spawning the
pawnkind alone tests NOTHING** — the style has to be set on the pawn.

| mod | spawn | then set | 🔴 face | why that facing |
|---|---|---|---|---|
| ~~**CereanManeFix**~~ | — | — | — | ⛔ CLOSED 2026-08-21 — target mod not in ModsConfig; see row 6. |
| **SauridFrillFix** | pawnkind `VRESaurids_Villager_Saurid` | hair `VRESaurids_Littlefoot` | **NORTH** | donor ships `CenterFrill8_north-.png`, **trailing hyphen**, confirmed on disk; `CenterFrill7_north.png` beside it is named correctly |
| **ToolBeltFix** | ⛔ see below | — | **WEST** | `ToolBelt_west.png` is **753 bytes** against `ToolBelt_east.png` at **16,945** |

**Sources, read not guessed:**
- `OuterRim_CereanMane` — `HairDef`, `.../294100/2980427615/1.6/Defs/HairDefs/Hairs_Cerean.xml:37`, texPath `OuterRim/Hairs/Cerean/CereanMane`. Gated on gene `OuterRim_CereanHead`, whose `hairTagFilter` whitelists one tag, so a fresh Cerean rolls the mane about **1 in 5** — ⚠️ **set it, do not hope.** Pawnkind at `Xenotype_Cerean.xml:22` forces the xenotype at weight 999.
- `VRESaurids_Littlefoot` — `HairDef`, `.../294100/2880990495/1.6/Defs/HairDefs/HairDefs_Saurid.xml:68`, texPath `Pawn/CenterFrill/CenterFrill8`. A "CenterFrill" is a **HairDef**, not an alien-race body addon — the gene only gates which hairs are legal. Pawnkind at `PawnKinds_Saurids.xml:5`.
- `VAEA_Apparel_ToolBelt` — `ThingDef` apparel, `.../294100/2521176396/1.6/Defs/ThingDefs_Misc/Apparel_Utility.xml:531`, `wornGraphicPath` at `:577`.

### ⛔ ToolBeltFix is UNCOLLECTABLE without an equip route — do not queue it for a load

**No `PawnKindDef` spawns it wearing.** Grepped the whole workshop tree, `Mods/`
and `Data/`: zero hits in `apparelRequired`, `specificApparelRequirements` or any
fixed apparel list, and its only tag `VAEA_Utility_Industrial` appears in **no**
pawnkind — so there is no random-generation path either. Every other reference is
loot: a fishing `ThingSetMakerDef`, a TraderGen stock list, a quest reward.

⇒ It needs dev-spawn **plus a force-equip**, which BUILD owns. **Hold it for that
tool, not for a map.** ⚠️ `renderUtilityAsPack` is
true, so it draws in the pack layer — check from behind as well as straight west.

### One load-order note, verified
⛔ **The CereanManeFix half of this note is CLOSED 2026-08-21** — its target mod is not
active, so none of it is exercised. Kept because the AssetBundle-vs-loose fact is reusable.

CereanManeFix correctly declares **no** `loadAfter`: Outer Rim 1.6 serves that art
from an AssetBundle (`Common/AssetBundles/neronix17_outerrim_galacticdiversity.manifest`
lists `Hairs/Cerean/CereanMane_south.png` and its north/east siblings), and **a
loose PNG beats a bundle regardless of order.** The other two are loose-vs-loose,
where order decides, and both declare `loadAfter` correctly.
