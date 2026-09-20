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

## verify

A design doc exists naming the growth mechanic's exact mechanism, the devour
ability's exact numbers, and the roster placement — ready for a FOUNDRY build
pass without further creative judgment calls.

## criteria

The owner's ask ("a titanic green slime, in the slime biome, that swallows
pawns whole and can grow as it eats") has a concrete, buildable spec.
