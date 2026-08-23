## spec
§2. The link chain is entirely shipped and verified 2026-08-19:
`TileMutatorDef.extraGenSteps` (`TileMutatorDef.cs:26`) → our `GenStepDef` →
`LordMaker.MakeNewLord(faction, job, map, pawns)`. `MapGenerator.cs:158` is where
mutator gen steps are concatenated, so the hook is real and needs no patch.
Seven shipped GenSteps already call `MakeNewLord` in this exact shape —
`GenStep_SitePawns` is the closest model.
  `src/Jawa/Inhabited/Source/GenStep_InhabitedCast.cs`
    on generate: find the `WorldObject_Inhabited` for `map.Tile`; pull `roster`
    out; if short of the cast size, `DisplacedPool.Draw` first, then generate
    fresh from `CastDef`; spawn and `MakeNewLord`.
    on map destroy: return SURVIVORS to `roster`. The dead do not return.
🔴 **CAST SIZE — DECIDE's ruling, 2026-08-20, so this item is executable:**
  hive foundry (Geonosian)   14–22      fortified waystation   10–16
  refinery / worksite         8–14      nomad camp (Tusken)     6–12
  trade moot / post           5–9       homestead / farmstead    4–7
  droid enclave               3–6
A faction's 25 authored characters therefore spread across 2–4 places, which is
the intent — a cast is a subset of a roster, not the whole of it.
🔴 **FARMING IS NOT ATTEMPTED AND THIS IS NOT AN OVERSIGHT.** §2.1: three
independent shipped walls, the worst being `WorkGiver_GrowerHarvest.ShouldSkip`,
which opens `if (pawn.GetLord() != null) return true;` — **any lorded pawn skips
harvest, even a colonist.** Sustenance is PRESENT, not produced: give the place a
larder in `stock` and leave it visible, stealable and destroyable. Owner: *"I
like that their food stocks are exposed. Very realistic."*

## verify
a quicktest map on a tile carrying the mutator spawns the cast, and the Lord
exists (`Find.CurrentMap.lordManager.lords` non-empty). Roster count before
and after a map cycle with no combat is EQUAL.

## criteria
land, leave, return: the same named people are there. Kill two, leave, return:
          the roster is short by exactly two and no record of them exists anywhere.
🪤 **A TRAP FOUND IN THE 2026-08-20 08:08 LOAD LOG, before this item is runnable.**
          Map Preview reported at line 5061:
            *"the mod 'Custom Quest Framework' (QF_Patch) adds a destructive patch that will
            likely override or break some functionality"*
            patch:  `static System.Boolean QuestEditor_Library.Patch_MapGenerate::prefix(...)`
            target: `static Verse.Map Verse.MapGenerator::GenerateMap(...)`
          🔑 **Why that lands on THIS item specifically.** The whole wiring for the cast is
          the `extraGenSteps` concatenation, and that concatenation lives **inside**
          `MapGenerator.GenerateMap` (`MapGenerator.cs:156-162`). A Harmony prefix that
          returns `bool` can return **false and skip the original method entirely** — and
          if it ever does, our `GenStepDef` is never even assembled into the step list. The
          cast would simply not appear, with **no error of any kind**, which is precisely
          the failure class this project keeps getting bitten by.
          ⚠️ **PROVEN vs NOT PROVEN, and do not let these blur:**
            ✅ proven — a `bool`-returning prefix on that exact method is live in this build.
            ❌ NOT proven — that it ever returns `false`. Most bool prefixes always return
               true and merely observe, and Map Preview's warning is a heuristic about the
               patch's SHAPE, not an observation of its behaviour. `strings` cannot answer
               control flow and I did not pretend otherwise.
          ✅ **The cheap decisive test, pre-registered here so it is not invented later:**
          the first time a map generates on a tile carrying an `Inhabited_Cast` mutator,
          check whether the cast spawned. If it did, the prefix is benign and this note can
          be struck. If it did not, and no error appeared, **suspect this before suspecting
          our own GenStep** — and confirm by temporarily disabling Custom Quest Framework
          on the 14-mod MINIMAL list, where a load is 22 seconds.

## notes
**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

⭐ **MECHANISM BUILT, CONTENT MISSING** — 2026-08-20, `f0a9f6c`.
`GenStep_InhabitedCast` + `GenStepDef Inhabited_Cast` (order 900) are in and build
clean. Roster-out, `MakeNewLord`, spawn, and roster-back-in are all wired.
🔑 **Return of survivors is a Harmony prefix on `Verse.Game.DeinitAndRemoveMap`,
not a GenStep hook.** `Game.DeinitAndRemoveMap` runs
`Notify_MyMapAboutToBeRemoved()` and then `MapDeiniter.Deinit`, whose FIRST act is
`PassPawnsToWorld` — every pawn despawned and handed to `WorldPawns`. The prefix
is the last instant the cast is still standing on its own ground;
`MapComponentUtility.MapRemoved` fires afterwards and is far too late.
⛔ **BLOCKED ON CONTENT, and it is not BUILD's to invent:** DECIDE's cast-size
table is in the spec above and is now expressible — `InhabitedCastDef.castSize` —
but **no `InhabitedPlaceDef` or `InhabitedCastDef` instance exists yet**, and
neither does any `TileMutatorDef` naming `Inhabited_Cast` in its `extraGenSteps`.
Those need the 269 authored characters as data first, which is
`CAST_ROSTER_MACHINE_READABLE_1` below.
⛔ Farming is not attempted, as specified. `InhabitedPlaceDef.larder` carries the
present-not-produced sustenance and the reason is commented at the field.


---

## 🔴 CORRECTION — BUILD, 2026-08-23, against capture `2026-08-23T07-12-04Z`

**Its stated dependency is closed, and its number is stale.**

⛔ *"Those need the 269 authored characters as data first, which is `CAST_ROSTER_MACHINE_READABLE_1`"*
— that item closed 2026-08-21 at `2cbb3ed`, and the count is **294**, not 269:
`[Inhabited] ready: 2 patches, 294 characters, 0 places, 0 casts.`

✅ **The real block is the other half of that line: `0 places, 0 casts`.** No `InhabitedPlaceDef`
or `InhabitedCastDef` exists in the capture and no `TileMutatorDef` routes to the GenStep. That
is defs and a mutator on the frozen map — DECIDE's and the owner's, not BUILD's — which is what
the existing block already says. The character roster is not what is holding it.
