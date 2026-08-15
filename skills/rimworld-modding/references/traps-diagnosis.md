# traps — Reading errors, and the live game

Log triage, error counts, and calls into a running game.

**Read this one before trusting a diagnosis** — especially before repeating a claim about the engine that you did not verify yourself.

What goes in, and what does not: `references/traps.md`.

---

### An error count is a count of victims, not of causes — abstract bases multiply
**Symptom:** 16 × `Could not resolve cross-reference: No Verse.SoundDef named Pawn_Melee_Punch_HitBuilding found to give to Verse.RaceProperties`. Sixteen looks like a widespread problem across many mods.
**Cause:** **two** lines of XML, in two `Abstract="True"` base ThingDefs (`AsimovNonEnergyAutomatonBase`, `JDSSWCIS_Droids`). Every concrete race inheriting a base inherits the dangling reference and fails to resolve it independently, so one authoring mistake bills once per descendant.
**Fix:** none needed — the engine falls back with *"using undefined sound"*. Divide before you panic: N identical messages naming the same missing def usually means one mistake in an abstract base with N-ish descendants, so search `Abstract="True"` defs for the reference first.
**Recurs when:** triaging by volume — severity comes from the `wanter` (SKILL.md §7), not the tally; a large count is not automatically severe and a small one is not automatically safe.

---

### A strictly read-only live-bridge call hung the game and cost a 23-minute load
**Symptom:** `rimworld/list_debug_action_roots` returned but slowly; `rimworld/search_debug_actions` never returned. `Player.log` stopped mid-line, the socket timed out at 60 s, and Windows raised `AppHangB1` and closed RimWorld. Nothing had been mutated — the calls were pure discovery.
**Cause:** bridge tools execute **on the game's main thread**. Both of those build RimWorld's debug-action node graph, and across 562 mods that build never completed — a livelock, not a deadlock: CPU pinned, log still growing, until the process was killed.
**Fix:** never run enumerating discovery tools against a game you care about — learn the paths on a throwaway quick-test colony, then use the known path on the real one. The vanilla surface is also obtainable fully offline: parsing `[DebugAction]` attributes out of `Assembly-CSharp.dll` yields all **411** of them with categories and target kinds.
**Recurs when:** any in-process bridge tool named list/search/discover — classify bridge tools by how much work they do on the thread that must keep responding, not by whether they mutate state.

---

### The same mod stayed dead through two correct fixes, for three different reasons
**Symptom:** `Error in static constructor of ChooseWildAnimalSpawns.Main` on three consecutive loads, always thrown from `BiomeDef.CommonalityOfAnimal`, and twice running with the *identical* `ArgumentNullException: Value cannot be null. Parameter name: key` at the identical frame.
**Cause:** three unrelated bugs converging on one line, `cachedAnimalCommonalities.Add(key, value)`. Load 1: `ArgumentException` duplicate key — `Armadillo` registered from both directions. Load 2: `ArgumentNullException` because the **BiomeDef** was null (our own `<li>` bug). Load 3: same exception because the **PawnKindDef** was null — five unresolved `BiomeAnimalRecord` entries injected by a compat patch guarded on the mod rather than the def.
**Fix:** each one separately. An exception that keeps the same *type* at the same *frame* can still be a different bug, so ask "what is null this time, and who put it there", never "is it still broken".
**Recurs when:** any single `Dictionary.Add` reachable from several feeders — the frame identifies the *victim*, never the cause. Diff the surrounding evidence between loads instead of comparing the exception line.

---

### An extrapolation from a sampled instrument is not a count
**Symptom:** a queue carried *"scrapfields: **11 measured** against a fully-derived 75-125"* as an open engine defect for a day. There was no measurement of 11: the source is 9 rects of 30x30 = 8,100 cells, ~13% of the map, holding **one** `ChunkSlagSteel`, divided by 0.13 to "~7 map-wide" and then drifting to 11 in the retelling.
**Cause:** where the 9 sample rects sat was never recorded, so the uniform-coverage assumption the division rests on is permanently unverifiable — 1 chunk in that sample is equally consistent with 7 map-wide and with 90.
**Fix:** prefer the instrument that cannot sample. A full-map `jawa/list_things` count exists and costs **one call**; it was never run. Where a number really is sampled, label it an estimate and carry its coverage, its sample locations and its n.
**Recurs when:** screenshot rects, a grep over one harvested log, a spot-check of N of M mods, a partial def dump. ⚠️ The tell is a suspiciously round divisor in the provenance — `/0.13`, `x8`, "so about".

### A one-shot generator's output dates the DEF THAT BUILT THE MAP, not the def on disk
**Symptom:** v1 row 4 was about to be closed or failed on a full-map `ChunkSlagSteel` count against a band of **44–56**, derived from `Jawa_ScatterScrapfields` as it stands in the repo today. The map the count would have run on was generated **before** that def reached the game copy. A near-zero result was queued to be read as *"the fix did not work"*; the fix was never in the map.
**Cause:** `Jawa_ScatterScrapfields` (`src/Jawa/Jawa_Patches/Defs/MapGeneration/JawaScrapfields.xml:104`) is a `GenStepDef` wrapping `GenStep_ScatterThings`. **A GenStep runs once, at map generation, and never again.** So the population of anything it places is frozen at the instant that map was made, carrying whatever def was **deployed to the game folder** at that instant — not what is in the repo, and not what is deployed now. Here `isJunk` was live in the game copy until 13:40 that day (`de1018b` removed it, and `GetPlacementFactor` ≈ 0 on a Dunes tile meant the step was silently zeroing itself), so **every pre-existing map was generated by the broken def.**
**Fix:** ⭐ **before counting anything a GenStep placed, ask when the map was made and what was deployed then.** Three states, and only one is measurable: a map generated after the deploy → the band applies; a map generated before it → the honest verdict is **"not measurable here"**, never "missed the band"; a map of unknown vintage → establish the vintage first, it is one `mtime` on the save. **Any report of such a count must name the map it ran on**, because the number is meaningless without it.
**Recurs when:** every one-shot generator — `GenStep_Scatterer` and its subclasses, terrain and mutator GenSteps, worldgen faction placement, quest-time site generation, anything whose output is baked into a `.rws`. ⚠️ **The tell is a def edit that "should" change a count on a save that already exists.** It cannot. **Generalises to** the whole *artifact right, consumer stale* family — **here the stale consumer is the MAP**, which read the def once, months or hours ago, and will never read it again. **Distinct from** a patch or a stat def, which the game re-reads every load and where a redeploy genuinely does change behaviour on an old save.
