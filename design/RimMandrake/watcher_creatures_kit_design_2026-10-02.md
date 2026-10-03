# Watcher creatures kit — design (WATCHER_CREATURES_MOD_1)

Status: DESIGN for the owner to rule on. BENCH helper, 2026-10-02. Nothing built, nothing filed.
Builds on the pitch `design/RimMandrake/watchers_mod_pitch_2026-09-30.md` (his card rulings of
2026-09-30: hide = vanish in place + a sign on the cell; flinch cue = anything not its own kind;
its own standalone mod; Q9 answered by typing: check whether a creature can look different per
medium, and bind each watcher to one medium, the Stillsand members to its fine sand). This doc
does not repeat the pitch's 29-row member census; it narrows to the kit and the piinnok.

## 1. What already exists (measured, with paths)

**The headline: the engine already switches an animal's sprite by state, with no code.** Read on
RimSage (decompiled 1.6) on 2026-10-02:

- `Verse.Pawn.DrawNonHumanlikeStationaryGraphic` (`Source/Verse/Pawn.cs` ~l.1696): true when the
  pawn is spawned, non-humanlike, **not `pather.Moving`**, and its life stage has
  `stationaryGraphicData`. Vanilla Odyssey's **hermit crab** uses exactly this
  (`Defs/Odyssey/ThingDefs_Races/Races_Animal_Coastal.xml`, `HermitCrabA_Stationary`): a different
  sprite whenever it stands still. No C# in the engine names the hermit crab, so it is data only.
- `Verse.Pawn.DrawNonHumanlikeSwimmingGraphic` (~l.1680): true when spawned, non-humanlike, the
  pawn **has a `WaterCellCost`** (race `waterCellCost` or a gene), its life stage has
  `swimmingGraphicData`, and **the terrain under it `IsWater`**.
- `Verse.PawnRenderNodeWorker_AnimalBody.GetGraphicState`: swimming is checked **first**, then
  stationary, then the normal body. `PawnRenderNode_AnimalPart_Body.StateGraphicsFor` yields
  exactly those two extra states (`GraphicStateDefOf.Swimming`, `.Stationary`), with female and
  alternate-graphic variants and skin tint applied.
- `RCellFinder` (~l.395): vanilla wander refuses `avoidWander` terrain **unless** the terrain
  `IsWater` and the race is `waterSeeker`. `Pawn_PathFollower` (~l.739) and
  `PathFinderCostTuning` (~l.47) replace a water cell's cost with the pawn's `WaterCellCost`.

**Our deep sand is "water" to the engine.** `RM_DeepSand`
(`src/RimMandrake/FlowWorks/Defs/ManyWaters/TerrainDefs/RM_DeepSand.xml`) carries the `Water` tag
(so `IsWater` is true; that is how sand fishing works), `avoidWander true`, `pathCost 300`. It is
the Stillsand's dominant terrain by `terrainPatchMakers` ("Muchly", threshold 0.2) over a `Sand`
base (`src/RimMandrake/Stillsand/Defs/BiomeDefs/RM_Stillsand_Biome.xml`). The qorrax already ships a
`swimmingGraphicData` sprite that this rule shows on deep sand
(`src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Qorrax.xml`).

**There is no terrain called "fine sand".** `RM_FineSand` in our source is an **item** (the sand
sieve's output, `src/RimMandrake/Stillsand/Source/RM_SandSieve.cs`). `AB_FineSand` is a donor
terrain from Alpha Biomes named in `design/Jawa/worldbuilding/biome_terrain_palette.md`; whether it
is loaded is UNMEASURED and it is not on any Stillsand map. See Q1.

**Kit pieces already built in our source, to reuse rather than re-invent:**

| need | existing piece | path |
|---|---|---|
| geophone (lenses sink for a buried giant) | `RM_SandSwimUtility.SubmergedSwimmersNear(map, cell, radius, minBodySize)`, written as "§8, the piinnok hook" | `src/RimMandrake/CreatureBehaviors/Source/RM_CompSandSwim.cs` |
| invisible-in-place hide | hediff with vanilla `HediffComp_Invisibility` (murrek, sand swimmers' `RM_SandSwim_Hediffs.xml`) | `src/RimMandrake/BlueDesert/Source/RM_MurrekDrift.cs`, `src/RimMandrake/CreatureBehaviors/Defs/HediffDefs/RM_SandSwim_Hediffs.xml` |
| hide-as-a-job with one cleanup on every exit | `RM_JobDriver_Burrow` + `RM_JobGiver_BurrowOnFire` + `RM_BurrowOnFireExtension` (`AddFinishAction` removes the hediff on every path) | `src/RimMandrake/Pyrelands/Source/` |
| global think-tree insert, no-op for other animals | `Animal_PreWander` / `Animal_PreMain` inserts | `src/RimMandrake/CreatureBehaviors/Defs/ThinkTreeDefs/RM_ThinkTree_ShadeSeekingWander.xml`, `RM_ThinkTree_VerminBehaviors.xml`, `src/RimMandrake/Pyrelands/Defs/ThinkTreeDefs/RM_BurrowOnFireThinkTree.xml` |
| wander confined by a validator | `RM_JobGiver_WanderInShadeGrid : JobGiver_Wander` (`wanderDestValidator`) | `src/RimMandrake/CreatureBehaviors/Source/RM_JobGiver_WanderInShadeGrid.cs` |
| medium lock backstop | `RM_CompWaterLocked` (stops a pawn found off its medium; documents that vanilla has no terrain-only traverse mode) | `src/RimMandrake/EnvironmentalHazards/Source/RM_CompWaterLocked.cs` |
| "walk toward tagged terrain" | `RM_JobGiver_SeekMarkedTerrain` + `RM_SeekTargetExtension` | `src/RimMandrake/CreatureBehaviors/Source/` |
| same-kind cascade (a field going dark together) | `RM_ReactionPropagationRule_SameKindWithinRadius` | `src/RimMandrake/CreatureBehaviors/Source/` |
| injected comp from an extension alone | `RM_SandSwimStartup` (adds the comp to every race carrying the extension) | `RM_CompSandSwim.cs` |

Not found: any "watch/peek" ThinkNode or JobDriver in `src/` (grep of `watch|peek|burrow|hide`
over `*.cs` hit only unrelated settings, quest watchers and the pieces above). No piinnok def,
no piinnok art (`artpipe_state.py find piinnok`: 0 hits across 7,891 entries). The piinnok's
design text is in `design/Jawa/worldbuilding/biomes/stillsand_bedazzle_review_2026-09-29.md`
(row 2, "the watching glass") and `stillsand_bedazzle_cast_2026-09-30.md` (admitted, owned by this
item).

## 2. Behaviour states and transitions

Four states, as ruled in the pitch. One job (`RM_JobDriver_Watch`) holds them as toils.

| state | sprite shown (engine rule) | engine state |
|---|---|---|
| **Hidden** | nothing (invisibility hediff stops all drawing); a **sign Thing** marks the cell | hediff on, sign spawned |
| **Emerging** | puff fleck + sound, then the stationary sprite | hediff off, sign destroyed |
| **Watching** | the **stationary sprite = the peek pose**, turned to face the nearest pawn | toil `handlingFacing = true`, `FaceTarget` every ~30 ticks |
| **Flinch** | puff + sound, back to Hidden | hediff on, sign spawned, cooldown starts |
| *(Relocating)* | the **moving sprite** (whole creature scuttling), visible | ordinary goto; never hidden while moving |

Transitions:
- Hidden → Emerging: the re-emerge delay (default 1–3 h) has passed **and** no non-own-kind pawn
  is within `flinchRadius` **and** no geophone trigger is live.
- Watching → Flinch: a non-own-kind pawn enters `flinchRadius` (ruled flinch cue), or the
  geophone fires (`SubmergedSwimmersNear(..., watchRadius, geophoneMinBodySize) > 0`), or it takes
  damage.
- Any → Relocating: its cell stops being its medium, gets built over, burns or floods. It walks
  visibly to the nearest medium cell, then hides there.
- Any exit of the job (interrupt, damage, capture, death, downed, settings off) → one
  `AddFinishAction` removes the hediff **and** the sign. The hidden state can never outlive the job.

Facing is Rot4 (pitch, verified): it snaps through quarter turns. **The piinnok's art therefore
needs a readable iris direction in each of north/east/south**, or the tracking cannot be seen.

## 3. How a creature opts in

One `DefModExtension` on the race; the comp is injected (the `RM_SandSwimStartup` pattern), so a
member writes XML only:

```xml
<li Class="RimMandrake.Watchers.RM_WatcherExtension">
  <mediumTerrains><li>RM_DeepSand</li></mediumTerrains>  <!-- empty = no medium lock (cover watchers) -->
  <flinchRadius>6</flinchRadius>
  <watchRadius>14</watchRadius>
  <hideTicks>2500~7500</hideTicks>
  <hiddenHediff>RM_WatcherHidden</hiddenHediff>          <!-- carries HediffComp_Invisibility -->
  <signDef>RM_WatcherSign_SandDimple</signDef>
  <emergeFleck>…</emergeFleck><emergeSound>…</emergeSound>
  <geophoneMinBodySize>0</geophoneMinBodySize>          <!-- 0 = no geophone; piinnok ~2.5 -->
</li>
```

- `RM_JobGiver_Watch` at `Animal_PreWander` (first line: no extension → null). Hunger, sleep,
  fleeing and taming sit above it in Core's tree, so a watcher still lives normally.
- `RM_JobGiver_WanderInMedium : JobGiver_Wander` with a `wanderDestValidator` that only offers
  medium cells (the shade-grid pattern), at the same insert.
- `RM_CompWatcher` (injected): the medium backstop (the `RM_CompWaterLocked` shape: found off its
  medium and not already relocating → start Relocating), and a spawn fix-up (a wild spawn on a
  non-medium cell walks to the nearest medium cell; if the map has none, it behaves as a plain
  sessile animal and never hides, so it can never vanish where no sign could read).
- **Data levers on the race, no code:** `waterSeeker true` and a low `waterCellCost` make vanilla
  wander *prefer* deep sand and path through it cheaply (section 1). That is half the medium lock
  for free, for any medium that is `IsWater`. Non-water media (crack, crust, ice) need the
  validator alone.

## 4. The Fine Sand restriction

Recommended reading of his words ("the Fine Sand of the deep desert … these creatures lurk just
under its surface"): **`RM_DeepSand`**, the Stillsand's dominant terrain, the one the swimmers swim
in, already described in-game as "something lives in it". That makes the lock:

1. `mediumTerrains = [RM_DeepSand]` on the extension (validator + backstop),
2. `waterSeeker` + `waterCellCost` on the race (vanilla wander and pathing prefer it),
3. wild spawn fix-up as above.

What this cannot promise (same honesty as `RM_CompWaterLocked`'s header): a *path* may cross a
cell of plain `Sand` on the way between deep-sand patches before the backstop next fires. Deep sand
is laid in broad patches (minSize 60), so the patches are large but **not proven connected**;
whether a stranded piinnok on an isolated patch matters is a tuning question, not a blocker.
UNMEASURED: whether `WildAnimalSpawner` places animals on `IsWater` cells at all; the spawn
fix-up covers either answer.

Alternatives are Q1.

## 5. Per-medium art feasibility (engine-checked)

His question: *can a creature look different in different mediums?* Answer, from the source read
in section 1:

| what | feasible? | how | cost |
|---|---|---|---|
| a different look **while still** vs **while moving** | **yes, vanilla, data only** | `stationaryGraphicData` (hermit crab precedent) | one extra sprite set |
| a different look on **`IsWater` terrain** (which includes our deep sand) vs everything else | **yes, vanilla, data only** | `swimmingGraphicData` + race `waterCellCost`; swimming outranks stationary | one extra sprite set |
| a different look per **specific** terrain (sand vs gravel vs ice) | buildable, **not proven** | a C# subclass of the animal body node + worker yielding extra `GraphicStateDef`s keyed on terrain; the hooks are `protected override` so it is reachable, but nothing in our source or vanilla does it | C# + a sprite set per terrain |
| anything drawn **while hidden** | **no** | the invisibility hediff stops the whole pawn draw; the sign must be a separate Thing (pitch, verified) | — |

So the one-medium binding he proposed is the right call and needs **no per-terrain art at all**.
With the piinnok locked to deep sand, the clean art plan is:

- `stationaryGraphicData` = **the peek pose**: the lens dome and a little sand rim, no body.
- `bodyGraphicData` = **the whole creature**, seen only in the rare moment it relocates.
- `dessicatedBodyGraphicData` = corpse, as usual.
- **No** `swimmingGraphicData`. ⚠️ Trap: if the race gets `waterCellCost` (for the wander lever)
  **and** a swimming sprite, the swimming sprite wins on deep sand in every state and the
  stationary peek never shows. Either leave swimming out (recommended), or make the swimming
  sprite *be* the peek pose and drop the stationary one (then it peeks even while moving).
- The sign Thing (sand dimple) is its own small sprite.

## 6. Mod Settings

Per the 2026-09-12 rule; defaults are shipped behaviour.

| setting | default | off / range |
|---|---|---|
| Watchers enabled (master) | on | they are ordinary sessile animals that never hide |
| Hide and flinch | on | they watch but never hide |
| Turn to face | on | they hide but do not track |
| Stay on their medium | on | they may wander off it (and then never hide off it) |
| Geophone (lenses sink for buried giants) | on | ignore subsurface movement |
| Flinch radius | 6 | 3–12 cells |
| Re-emerge delay | 1–3 h | slider |
| Max active watchers per map | 40 | above this, extras sit as plain animals |

The readable sign has no toggle: it is the "no animal vanishes" rule, not a feature.

## 7. The piinnok, first user

From its admitted design text: a sessile burrower whose one exposed organ is a water-clear lens
dome; "the one thing that tracks anything: you"; harmless, edible; butchers to a better grade of
biosilica; lenses sink when something large moves under the sand.

| aspect | piinnok setting |
|---|---|
| medium | `RM_DeepSand` only |
| flinch | anything not a piinnok within 6 |
| geophone | on: a submerged swimmer of body size ≥ ~2.5 within 14 sinks every piinnok in range. Reuses `SubmergedSwimmersNear` as written. Droids never trigger it (they are not swimmers) |
| body | tiny (bodySize ~0.15), no attack worth naming, `herdAnimal false`, group 2–4 |
| butcher | meat + the better biosilica (defName to be read from the Stillsand glass chain at build time, never guessed) |
| sign | "sand dimple" |
| roster | `RM_Stillsand` row only, added by `STILLSAND_BEDAZZLE_CONTENT_1` once the def exists (its own note) |
| art (one artpipe job, after Q2) | stationary peek (lens + rim, iris direction readable N/E/S), whole-body move sprite, dessicated, dimple sign |

## 8. Other existing creatures that fit

From the pitch's census, re-read against the one-medium rule:

| creature | path | medium | fit |
|---|---|---|---|
| `RM_Thollim` | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_GreySeaFauna.xml` | sea-floor sediment | good: "valves half down in the sediment"; stationary = gape |
| `RM_Tarruq` | Cracked Lands | crack | good; non-water medium, validator only |
| `RM_Peeper` | Contagion | goo margin | good |
| `RM_Fessk` | `RM_GreySeaFauna.xml` | none (cover) | partial: mobile, leans out from a pillar; no hide hediff, empty `mediumTerrains` |
| Shiro (canon) | Utinni patch layer | shell | good, and the hermit crab is its exact vanilla shape (stationary = withdrawn) |
| `RM_Qorrax` | `RM_Qorrax.xml` | deep sand | **not** a watcher (a swimmer), but it is the proof the swimming-sprite rule already works on deep sand |

## 9. Build plan for FOUNDRY

New mod `mandrake.rm.watchers` (ruled standalone), loading after and referencing the
CreatureBehaviors assembly for `SubmergedSwimmersNear`. Debug-process rule applies: a first
functional script with a recorded run before content.

| step | work | size |
|---|---|---|
| 1 | mod skeleton, About, settings screen (section 6) | S |
| 2 | `RM_WatcherExtension` with ConfigErrors; startup comp injection | S |
| 3 | `RM_WatcherHidden` hediff (copy the sand-swim submerged hediff shape); sign ThingDef base + sand dimple | S |
| 4 | `RM_JobGiver_Watch` + `RM_JobDriver_Watch` (4 toils, one finish action) + ThinkTreeDef at `Animal_PreWander` | M |
| 5 | medium lock: `RM_JobGiver_WanderInMedium`, `RM_CompWatcher` backstop + spawn fix-up | M |
| 6 | geophone hook | S |
| 7 | piinnok race + kind + butcher, art job via artpipe (search first, per the art rule) | M |
| 8 | `validation.py` + selftests; quicktest proof by **state read** (hidden hediff present, sign on cell, rotation changes as a pawn walks round it, geophone fires when a submerged swimmer is moved near) | M |
| 9 | flush designation — only if Q4 picks it | M |

About two FOUNDRY sessions for 1–8. Wave 2 (other members) goes biome by biome at each sitting.

## 10. Questions for the owner

**Q1. Which ground is "the fine sand" the piinnok lives in?**
- **(a) Deep sand only** (recommended). The sinking sand the swimmers swim in, which covers most of
  the Stillsand. Strongest "lurking just under the surface" read, and the engine already treats it
  like water, so half the lock is free. Trade: a piinnok on a small cut-off patch stays there.
- **(b) Any loose sand** (plain sand, soft sand and deep sand, the swimmers' full set). More room
  to live. Trade: on plain sand there is nothing "under the surface" to lurk in, and the lock
  becomes all custom code.
- **(c) A new terrain called fine sand**, painted into the Stillsand. Truest to the name. Trade: a
  new terrain, new ground art, and a map-gen change, before any watcher exists.

**Q2. How should a piinnok look when it moves?** (The game can show one picture while an animal
stands still and another while it walks, with no code; vanilla's hermit crab does this.)
- **(a) Two pictures** (recommended): standing still it is the peek (lens over a sand rim); in the
  rare moment it moves you see the whole creature. Trade: two art sets instead of one.
- **(b) One picture always**, the peek pose, as first planned. Trade: cheapest, but a lens-and-rim
  sliding across the sand when it relocates looks odd.

**Q3. Does a tamed piinnok have to stay on deep sand?**
- **(a) Yes, always.** A tamed one lives in a pen with deep sand, or heads back to it. Trade: pure
  to the fiction, fussier for the player.
- **(b) Wild ones stay; tamed ones may go anywhere** but only hide on deep sand. Trade: easier pet,
  weaker rule.
- **(c) It cannot be tamed.** Trade: simplest; loses the "living alarm at your base" idea.

**Q4. How do you hunt one?**
- **(a) Flush only** (recommended): you cannot target a dimple; a pawn sent to it makes it bolt,
  then it can be hunted. Trade: one more order to build.
- **(b) Shoot it while it peeks.** Trade: no extra build, but hunting becomes reaction speed,
  which the game always wins for you.
