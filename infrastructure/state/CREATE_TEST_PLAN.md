# CREATE_TEST_PLAN.md — how to prove CREATE's deployed material actually works

_CREATE, 2026-08-13. **Written because I owed it at deploy time and did not send
it.** Everything below is deployed and enabled; none of it has been seen. BRIDGE
drives — I do not connect. I comment, and I answer questions about intent._

---

## The two rules that govern every check here

🔴 **A screenshot is the evidence. A def query is not.** `V1_SCOPE.md`'s gate is
*seen working in-game once*. `take_screenshot` returns a path — **open it and
look at it.** Everything in this file fails in ways that produce **no log line at
all**, which is exactly why the log cannot close any of it.

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

## Part 1 — the eight mods. Cheapest first, all doable on any map

Seven art-fix mods plus the sled reskin, all enabled by OPS (572 → 580 active).
Each is *one spawn and one look*. Nothing here needs a fresh map or a colony.

| # | mod | spawn / find | look at | PASS looks like |
|---|---|---|---|---|
| 1 | `DesertVehicleReskin` | vehicle `AV_DogSled` | all three facings, then rotate | **two eopie**, not four dogs; **sled body BROWN**, not grey |
| 2 | `BlastDoorFrameAsyncFix` | buildings `PH_DoorBlastCDoor`, `PH_DoorThickBlastBDoor`, `PH_DoorBlastDDoor` | each rotated **EAST**, door open and closed | the frame's inner rim draws **in front of** the moving leaves; D-door keeps its iris ring |
| 3 | `ResearchKitEastFix` | items `RR_FieldResearchKitSimple`, `…HiTech`, `…MultiAnalyzer`, `…Remote` | each rotated **EAST** | four visible kits; none blank, none magenta |
| 4 | `GravshipAstronautFix` | pawn kind `VGE_Astronaut` | facing **NORTH** | a body, and its **faction-colour overlay** present (the mask typo hit both life stages) |
| 5 | `MSEDroidFix` | pawn kind `OuterRim_MSEDroid` | facing **NORTH** | a droid, not an invisible or south-facing fallback |
| 6 | `CereanManeFix` | a Cerean pawn, hair `OuterRim_CereanMane` | facing **SOUTH** | hair present — the donor's file is 1,514 B of **fully transparent** pixels, so the fail is a bald head |
| 7 | `SauridFrillFix` | a Saurid pawn, hair `VRESaurids_Littlefoot` | facing **NORTH** | the centre frill draws |
| 8 | `ToolBeltFix` | apparel `ToolBelt`, worn | facing **WEST** | the belt draws on the pawn |

⚠️ **Rows 4–8 are pawn-facing checks, so the pawn must actually face that way.**
`jawa/set_pawn_rotation` exists but **has never executed**. If it fails, the
fallback is to draft the pawn and order a move so it turns, or shoot it walking.
Do not report the art broken on the strength of a rotation call failing.

🔴 **Watch for the double-ship collision (my `C12`).** `CenterFrill8_north.png`
and the two Astronaut norths are shipped by **both** `Jawa_Patches` and their new
fix mod — two loose files at one path, and **load order alone decides which one
renders**. If 4 or 7 looks wrong, that is the first suspect, not the art.

---

## Part 2 — v1 ROW 3, the quest. No fresh map needed

Built `47733f8`, deployed inside `Jawa_Patches`. **Never fired.**

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
count; `V1_SCOPE.md` says so explicitly. Do not hold the row open waiting for a
caravan to complete it.

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

## Part 3 — v1 ROW 4, terrain. **Needs a NEWLY GENERATED map**

Built `73ca76c`, deployed inside `Jawa_Patches`. **All three overrides run at
MAP GENERATION.** They cannot appear on a map that already exists — including the
campaign map if it was generated before the deploy landed.

🟢 **A quicktest map counts.** `rimworld/start_debug_game_ready` makes one in ~30
seconds, and per the owner's rule 1c the bridge-holder may create and destroy dev
colonies freely. **Do not wait for the campaign world to prove these.**
⚠️ That call **exceeds the 30 s timeout and succeeds anyway** — do not retry, or
you get a second map. Reconnect and poll `list_pawns`.

Biome matters: generate in **Desert**, **ExtremeDesert** or **AridShrubland**.
Nothing below is patched into any other biome.

| # | override | what to look for | PASS |
|---|---|---|---|
| 1 | **Salt pans** (`Jawa_SaltCrust`) | broad **pale cracked** patches in low ground | present, and reads as flat evaporite rather than sand |
| 2 | **Dune seas** (widened `SoftSand`) | wavy soft-sand fields | noticeably more than a vanilla desert — this is a *density* change, so compare against memory of a normal desert |
| 3 | **Scrapfields** | steel slag chunks strewn across open ground, with machine-bits filth | ~75–125 chunks map-wide |

→ **SHOT per override**, zoomed out enough to show it is a *field*, not one tile.

🟢 **Free shortcut for #1 that needs no map at all:** `Jawa_SaltCrust` is an
ordinary `TerrainDef`, so the bridge can **paint** it onto the current map —
`jawa/set_terrain def=Jawa_SaltCrust`, a ~10×10 rect. That proves the **art and
the def**, which is most of the risk, and leaves only "does it generate" to the
fresh map. ⚠️ It also **paints over whatever was there** — do it on scratch, or
somewhere you are willing to lose.

⚠️ **The art is REUSED, not drawn.** `Jawa_SaltCrust` points at Odyssey's own
`Terrain/Surfaces/DryLakeBed`, which Odyssey declares but never generates. VISION
ruled purpose-drawn salt art is **v2** and this is fine for v1. If it looks like
a dry lake bed, that is correct, not a bug.

⚠️ **Geological Landforms wins on landform tiles.** It hard-writes terrain there,
and its *own* dry-lake landform hard-codes `SoftSand`. So the one feature that
ought to be a salt pan will not be. Ruled: leave it. **Do not report this as a
failure of override #1** — check somewhere off a landform.

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
  and was still wrong at play scale; that is trap #45. **Judge at the zoom you
  play at.**

---

## What I want back

Per item: **PASS / FAIL / NOT RUN**, and the screenshot path. For a FAIL, the
shot plus what you saw — I do not need a diagnosis, I need the image.

File findings at `infrastructure/state/queue/CREATE.md`; anything that is a
donor-side defect rather than ours goes to `TODO.md` with `[?]`.
