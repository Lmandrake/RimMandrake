# Palettes — the ingredients for tilemap work

A palette is what a *kind of thing* is legitimately made of in the current build:
the floors, objects, colours and materials, plus the constraints that decide whether
any of it reads on screen. It exists so that authoring a rusted ship, an industrial
ruin or a scoured outpost does not start by asking the game the same questions again.

**Each file is prose for humans with one fenced ` ```palette ` block that machines
load.** `src/RimMandrake/Utils/palette.py` is the loader; generators import a palette
instead of declaring their own tables, so a generator can no longer quietly
contradict the palette it was built from.

```
python3 src/RimMandrake/Utils/palette.py <name>            # load and print it
python3 src/RimMandrake/Utils/palette.py <name> --check     # validate against the def dump
```

## The distinction that matters most

🔑 **A palette holds OPTIONS. A `ramp` is one build's CHOICE.**

Rust really can be saturated orange; the Gravship Cradle simply took the brown
ramps. Recording that as "orange is forbidden" would have been wrong, and would have
broken the `two_tone` treatment that still uses it. **Never delete an option because
one build passed it over** — add a ramp, and record the choice in `used`.

## What is here

| palette | is | state |
|---|---|---|
| `flooring_rusted` | metal × rusted — corroded decking, the ship's own vocabulary | **in use.** `gravship_floor_v2.py` imports it |
| `machinewreck` | condition — mangled metal, dead machinery, crash debris | **candidates.** Nobody has looked at the sprites yet |
| `sandscoured` | condition — what wind-driven sand does to anything left outside | **unused.** Composes with the other two |

Two axes generate most of what is still missing: **material** (metal · stone · wood ·
organic · glass) × **condition** (pristine · worn · rusted · burnt · wrecked ·
scoured). A *faction* palette is not a third axis — it is a selection across these,
so write it as preferences pointing at other palettes rather than as a copy.

**Create them as the work demands them, not in advance.** Every palette here was
extracted from a build that had already paid for the knowledge.

## Grammar

```
color NAME  R,G,B              @mod=<Mod>  | description
role  ROLE  <TerrainDef|->     @mod=<Mod>  | description     -  means a hole
thing ROLE  <ThingDef>         @mod=<Mod>  | description
ramp  NAME  A > B > C                      | description
stuff ROLE  key=<ThingDef> ...  @mod=<Mod>  | description     merges across lines
param NAME  VALUE                          | description
rule  <a hard constraint, in words>
used  <which ramps a build took, and where>
```

`@mod=` is the mod that **supplies** the def. `--check` reads the def dump and
reports `MISSING` for a def that has gone, `MOVED` for one now supplied by a
different mod, and `WRONGTYPE` for one used as the wrong kind — which is how a
palette otherwise fails silently when a mod leaves the list.

## Writing a good one

The def lists are the cheap part; they can be rebuilt from the dump in a minute.
**The `rule` lines are what a palette is actually for.** Reserve them for
constraints that were *measured* — the colour grid multiplies, floors below ~155
crush the grate, a warm ship must be darker than the desert. Design judgement that
has not been tested yet goes in the prose, marked as such, so the two never get
confused.

Record `used` whenever a build ships. Knowing which ramp was taken, and which were
available and passed over, is what stops the next build re-litigating a settled look.
