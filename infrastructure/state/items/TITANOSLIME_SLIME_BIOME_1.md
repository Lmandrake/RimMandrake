# TITANOSLIME_SLIME_BIOME_1 — owner ask: a titanic green slime for RUT_Slime

## what is wrong

Nothing broken — this is a fresh creative ask from the owner, 2026-09-20, made
mid-session while reviewing `SHEET_ORPHAN_CONSUMPTION_1`'s sizeBin channel:

> *"For the slime biome, I am now enchanted by the idea of a titanic green
> slime. So make one of those too as its own custom creature. The Titanoslime.
> It should have the devoured ability to swallow pawns whole of nearly any
> size. And I have a question. Is it possible to have a creature that gets
> larger as it eats?"*

`RUT_Slime` is a live biome (seen in `biome_flora.py`'s roster set). No
`Titanoslime` or equivalent def exists anywhere in `src/`.

## the engine question, answered (MEASURED, not guessed)

**Yes, "grows as it eats" is buildable, but not as a vanilla field —
`Pawn.BodySize` is a computed property, not a settable one:**

```csharp
// Source/Verse/Pawn.cs:2499
public float BodySize => ageTracker.CurLifeStage.bodySizeFactor * RaceProps.baseBodySize;
```

Vanilla only varies this by **age-stage** (`LifeStageDef.bodySizeFactor`), on a
fixed tick schedule — there is no "eat N meals → grow" hook anywhere in
`Pawn_AgeTracker` or `FoodUtility`. The buildable route: a **Harmony postfix on
`Pawn.BodySize`** (or on whatever draws/uses it — check render size and combat
scaling separately, they may need their own postfixes) that multiplies the
vanilla result by a factor read off a **custom Hediff's severity**, where the
hediff's severity increases each time the creature finishes eating (hook
`Pawn_FoodTracker` or `Toils_Ingest`/`JobDriver_Ingest`'s completion, or a
`ThingComp` watching `Ingested()`). This project already has a working
"custom creature behavior comp" pattern to build from —
`RimMandrake.CreatureBehaviors` (used by `RSW_Drazzik` and others, see
`BRIDGE_PAWN_SPAWN_CRASHES_VEF_1`'s root-cause finding this session for where
that assembly lives). Whoever designs this should decide: a cap (does it stop
growing, or shrink over time/on a hunger cycle — a permanent one-way grow is a
balance risk), whether growth is visual only or also scales combat stats
(melee damage/HP typically key off `BodySize` already, so this may be "free"
once the postfix lands), and whether it persists across save/load (a Hediff
does, by default).

## the devour ability — reuse, don't reinvent

This codebase already has a shipped "swallow pawns whole" pattern, designed
for the Sarlacc (`design/Jawa/worldbuilding/sarlacc_spec.md` §2, "Grab-and-drag"):

> *"`CompDevourer`'s despawn + `IThingHolder` container is the shipped hold
> pattern — a grabbed pawn lives inside the tentacle/maw, struggles (job-driven
> timer), and is rescued by killing the holder."*

The owner's "swallow pawns whole of nearly any size" ask maps directly onto
this — reuse `CompDevourer` rather than building a second hold-mechanism from
scratch. The "nearly any size" part may need checking: does `CompDevourer`
have a size/weight gate on what it can grab? If so, that's the one field a
Titanoslime variant needs to widen.

## the decision this needs (design, not build — routes to BENCH/Fable)

1. Confirm/refine the name (owner already named it "Titanoslime" — treat as
   settled unless he says otherwise).
2. The growth mechanic's exact shape: growth curve, a cap or not, whether it
   resets, whether it's visual-only or stat-scaling, save/load behavior.
3. The devour ability's exact numbers: size/weight gate (or none, per "nearly
   any size"), duration held, escape/rescue mechanics (reuse `CompDevourer`'s
   existing shape unless there's a reason to diverge), what happens to a
   devoured pawn (Sarlacc's precedent has a "swallow route in" to a nested map
   — decide whether Titanoslime's devour is lethal, a debuff-and-release, a
   captured-state, or something else; it is a wandering wild creature in an
   open biome, not a dungeon feature, so the Sarlacc's "route into a pocket
   map" framing likely does NOT transfer as-is).
4. Where it sits in `RUT_Slime`'s roster (rarity/commonality — "titanic"
   implies rare/apex, not ambient) and whether it's hostile-by-default or
   provokable.
5. Art direction — new art only, standing ruling; check
   `infrastructure/artpipe/done/`/`registry.jsonl` first per the standing
   check-before-queuing rule even though this is a brand-new concept (in case
   a prior "titan slime" or similar concept already has something usable).

## Watch out

- `Pawn.BodySize` is read in many places beyond rendering (melee damage
  scaling, `FoodUtility` prey-catching math, bed sizing, corpse-large
  filters) — a postfix changes the pawn everywhere at once, which is the
  point, but means combat balance for a "nearly any size" devourer needs a
  real playtest, not just a visual check.
- `CompDevourer`'s hold is same-map only in vanilla (per the Sarlacc spec) —
  fine for an open-biome wanderer, just don't assume the Sarlacc's
  pocket-map/portal machinery is needed or wanted here.
- This is fresh creative content — per this repo's design/build split, FOUNDRY
  files and researches the engine feasibility (done above) but does not
  design the creature itself in-window; that's this item's `for: BENCH`,
  `kind: design`, backgrounded to a Fable subagent.

## design — DONE 2026-09-20 (Fable pass, backgrounded from BENCH)

**Spec: `design/RimMandrake/RM_titanoslime_spec.md`.** Every decision point above
is answered there; the item stays `doing` for the FOUNDRY build pass (§8 of the
spec is the sized build list with a quicktest gate per piece). The headlines,
so nobody has to open the spec to know the shape:

- **Home:** `mandrake.rm.gelatinousslime` (RimMandrake tier — not Star Wars),
  `RM_Titanoslime`; campaign wiring is one `wildAnimals` line in
  `UtinniPatches/Defs/BiomeDefs/RUT_Slime.xml` + a roster JSON row.
- **Growth is NOT a Harmony postfix** — the sketch above is superseded. It is the
  vanilla life-stage system with the stage index **locked by our comp**
  (`Pawn_AgeTracker.LockCurrentLifeStageIndex`, public + scribed, MEASURED): five
  `LifeStageDef`s carry `bodySizeFactor`/`healthScaleFactor`/`meleeDamageFactor`/
  `foodMaxFactor`, five kind life-stages carry `drawSize`, and `Pawn.BodySize`,
  the sprite, the Titanic tier, the Large Pawns footprint and the T3 corpse-site
  all follow that one index. Ladder: BodySize 6 → 10 → 16 → 24 → 40 (T1/T2/T2/T3/T3).
  Counter `absorbedMass` (scribed): +prey.BodySize per absorption, +0.25×nutrition
  for ordinary eating (polls the `NutritionEaten` record), −1/day starving, −0.5/day
  off slime terrain, −1 per shed gelatid; thresholds 4/12/28/60, cap 80, max-stage
  Mod Setting. Runs both ways; nothing is permanent.
- **Swallow is a melee tool**, not an ability: `ManeuverDef RM_Engulf` → our
  `Verb_MeleeAttack` subclass → `RM_CompEngulfer` (the `CompDevourer` hold shape
  rewritten with zero Anomaly defs — vanilla `CompDevourer` needs `Defs/Anomaly/`
  content, MEASURED, so it cannot be reused in a base-game mod). Reached through
  the ordinary predator hunt and ordinary fights; the vanilla animal think tree is
  untouched. Gate: prey ≤ 0.5 × own BodySize (so "nearly any size" is earned by
  growing), flesh only, capacity floor(BodySize/4). Hold: several at once, no job,
  the slime keeps moving with its cargo. Digest 20–400 s by prey size; held pawns
  struggle (damage the slime from inside) and big ones can burst out. Downed or
  killed → everything drops, stunned, acid-burned, +0.15 slimification.
  **Timer runs out → absorbed: killed, no corpse, gear regurgitated, mass gained.**
- **Roster:** wild predator, solitary, commonality 0.12 with `ecoSystemWeight` 6
  (≈ one per map, rarely two), placid when fed, hunts when hungry (colonists too
  where `predatorsHuntHumanlikes` allows — left as the player's setting), 100 %
  manhunter on damage. Sheds gelatids as it is cut (stage ≥ 2). No incident, no
  event — a resident. Spawns at stage 1–3; stages 4–5 are only ever earned on the
  player's map.
- **Art:** nothing usable exists (checked artpipe done/registry/status/decisions —
  nearest is Oozemaw, which must stay visibly distinct). One 1024 px set, three
  facings, reused across stages by drawSize (Thrumbo precedent); a glassy bright
  green *hill* of jelly with faint half-dissolved "entries" inside; never eyes,
  never a mouth, never limbs.
- Two engine facts the build inherits: `Devourer` sets `specificMeatDef Meat_Twisted`,
  so `Gelatid.xml`'s comment that no vanilla animal points meatDef at a hand-authored
  def is false (fix it in passing); and whether GelatinousSlime is on the campaign's
  full list is UNMEASURED this pass (spec §9).

## verify

A design doc exists naming the growth mechanic's exact mechanism, the devour
ability's exact numbers, and the roster placement — ready for a FOUNDRY build
pass without further creative judgment calls. **Satisfied 2026-09-20 by
`design/RimMandrake/RM_titanoslime_spec.md`.** The build pass's own verify is the
spec's §8 gate table (seven pieces, each with a quicktest assertion); the item
closes when all seven pass on the quicktest list with all five DLC loaded.

## criteria

The owner's ask ("a titanic green slime, in the slime biome, that swallows
pawns whole and can grow as it eats") has a concrete, buildable spec.

## build progress 2026-09-20

**BUILT AND COMMITTED, NOTHING DEPLOYED.** RimWorld was running and another
window held the bridge for the whole pass, so the DLL could not be written into
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\`. Everything below
is in the repo only; the deploy is the first item of the next shutdown window.

Commits: `cadfd8a83` (the mod), `016a7b45e` (campaign roster). Selftests 67/67.

### what exists now

All inside `src/RimMandrake/GelatinousSlime/` (packageId
`mandrake.rm.gelatinousslime`, namespace `RimMandrake.GelatinousSlime`), plus one
line in the campaign biome.

| piece | file | state |
|---|---|---|
| race + kind (5 lifeStages) | `Defs/ThingDefs_Races/Titanoslime.xml` | written, validates 0 errors against the full 618-mod load set |
| growth ladder | `Defs/LifeStageDefs/Titanoslime.xml` | 5 LifeStageDefs, bodySize 6/10/16/24/40 |
| body | `Defs/BodyDefs/AmorphousBody.xml`, `Defs/BodyPartDefs/AmorphousParts.xml`, `Defs/BodyPartGroupDefs/AmorphousGroups.xml` | 3 parts, one vital nucleus |
| the swallow | `Defs/Maneuvers/Engulf.xml`, `Defs/ToolCapacityDefs/Engulf.xml` | ManeuverDef → `RM_Verb_MeleeEngulf` |
| C# | `Source/Titanoslime.cs`, `Source/TitanoslimeVerb.cs` | **COMPILES** (`dotnet build -c Release`, 0 warnings 0 errors) |
| Mod Settings (5 knobs + rarity) | `Source/SlimeMod.cs` | engulf on/off · grows on/off · reversible on/off · max stage 1–5 · sheds on/off · rarity 0–3× |
| campaign wiring | `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Slime.xml` + `design/Jawa/worldbuilding/biomes/rosters/the_slime.json` | one `wildAnimals` line, commonality 0.12, `MayRequire` guarded |

Owner defaults from spec §11 all shipped as written: digestion is lethal (no
corpse, gear regurgitated), colonists follow the player's own
`predatorsHuntHumanlikes`, prey gate ≤ 0.5 × own BodySize, growth reversible,
resident only (spawn stages 1–3, no incident), five stage labels on the inspect
string.

### two spec seams resolved by measurement this pass

- **`LifeStageDef.statFactors` DOES reach `MoveSpeed`** (spec §2.1 flagged this
  VERIFY AT BUILD). `StatWorker.GetValueUnfinalized` applies
  `pawn.ageTracker.CurLifeStage.statFactors.GetStatFactorFromList(stat)` to every
  stat on a pawn — `RimWorld/StatWorker.cs:297`. So the per-stage slowdown is XML
  and needs no hediff.
- **`FoodTypeFlags.OmnivoreAnimal` = `0x1F1B` carries `Corpse` (0x8) but NOT
  `Plant` (0x40)** — `RimWorld/FoodTypeFlags.cs`. Spec §3.1 flagged the corpse
  bit; the bit actually missing was the plant one, and the spec's own prose
  requires grazing slime-grass. Shipped as `OmnivoreRoughAnimal` (`0x1F5B`).

### two build calls that differ from the spec's letter

- **The rarity slider edits the loaded def by reflection, not by a pretty public
  API.** `BiomeDef.wildAnimals` is a *private* `List<BiomeAnimalRecord>` and its
  commonality lookup is memoised in a private `[Unsaved]` dictionary (MEASURED).
  `TitanoslimeSpawnTuning` reads both by `GetField(..., NonPublic)`, remembers the
  shipped commonality on first touch so repeated writes cannot compound, and
  fails soft with one `Log.WarningOnce` if the field is ever renamed. No Harmony.
- **The engulf maneuver reuses vanilla's `Maneuver_Bite_*` RulePackDefs** rather
  than hand-authored ones, exactly as spec §3.3 permits. The combat log says
  "bites"; the wording is not load-bearing and a malformed RulePackDef reference
  would silently disarm the creature.

### art — OWED, nothing generated

texPath is `Things/Pawn/Animal/Titanoslime/RM_Titanoslime`, needing
`RM_Titanoslime_south/east/north.png` at 1024 px (west mirrors east). Until they
land the creature renders magenta, which is deliberate: the texture binds by
texPath, so the PNGs drop in later without touching any def. Brief is spec §7 —
a glassy bright-green *hill* of jelly, faint half-dissolved "entries" inside,
never eyes, never a mouth, never limbs; must read visibly distinct from Oozemaw.
`validate_patch.py` reports the missing path as a WARN, 10 times (once per
lifeStage graphic); that count is expected and is not a defect.

### the shutdown window: exact steps

1. `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod GelatinousSlime`
   (read the plan), then `--apply`. The DLL cannot be written while the game
   runs, so this must happen with RimWorld closed.
2. Build the test list: minimal + `GelatinousSlime` + `TitanicCreatures` +
   Large Pawns + **all five DLC** (`modset_builder.py`; DLC is mandatory on every
   tier by the 2026-09-19 ruling). A quicktest map is ~90 s.
3. Run spec §8's seven gates in order. The dev gizmos needed by gates 2 and 4 are
   already on the comp: *DEV: +6 absorbed mass*, *DEV: -6 absorbed mass*,
   *DEV: release held* (dev mode only).
   1. `measure count ThingDef` shows `RM_Titanoslime`; `jawa/spawn_pawn` places
      one; `jawa/list_things` reports BodySize 6.
   2. +6 mass twice → BodySize 16, drawSize 6, Titanic tier T2, Large Pawns 3×3
      (wait 60 ticks for its cache); save, reload, all four unchanged.
   3. One stage-1 + 4 drafted colonists in melee: a colonist is swallowed within
      60 s; the inspect string shows the countdown; downing the slime drops them
      stunned, acid-burned, `RM_Slimification` +0.15; letting the timer run
      absorbs — no corpse, gear on the ground, `absorbedMass` +1, food full.
   4. Spawn ten muffalo, not one (one burst-out is pure RNG): most should burst
      out of a stage-1 within ~1 min. Cut a stage-2 to 50 % → ≥ 3 gelatids shed
      and it drops to stage 1.
   5. Each of the five settings toggles observed live; `titanoslimeMaxStage 2`
      refuses stage 3 at `absorbedMass` 12.
   6. Kill a dev-grown stage-4 → `RM_TitanicCorpseSite` building, and anything
      held is on the map *before* the conversion.
   7. Art, once it exists: judged at display size at stages 1 and 5, all three
      facings.
4. 🔴 **Assert `BodySize` through the bridge, never the sprite.** A stage that
   "grew" on screen proves only that `drawSize` changed. And `measure count`
   before believing any spawn: a def with an unresolvable `Class=` attribute is
   discarded silently, and this one carries two of our own classes.
