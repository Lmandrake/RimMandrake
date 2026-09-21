# TUNNELSNAKE_VIOLATES_SIZE_LADDER_1 — a resident creature sits in the band ruled empty

## what is wrong

`design/Jawa/worldbuilding/biomes/arid_shrubland.md` §"The size ladder" is an **owner's
ruling, marked ratified**:

> **Small, medium, then NOTHING large — until huge.** The large band is a void, populated by
> exactly one thing: the young of the huge… nothing resident occupies large.

and the same doc's ban 4:

> 🔴 **No resident creature in the LARGE band.** Large is legal only as the juvenile stage of
> a huge species — a standalone large creature def in this biome is a violation.

The ladder explicitly files **"snake-analogs in the tunnels" under MEDIUM**.

MEASURED 2026-09-21: `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_TunnelSnake.xml`
line 151 carries **`<baseBodySize>2.0</baseBodySize>`** — cow-sized, and the biome's
signature resident predator. ⚠️ The file's own header comment says *"bodySize 1.5"*, so the
prose and the def disagree as well.

⇒ The biome's flagship medium predator is shipping in the band its own ratified ruling
declares empty.

## Watch out

- ⚠️ **The field is `baseBodySize` inside `<race>`, not `<bodySize>`.** A grep for
  `<bodySize>` on this file returns NOTHING and reads as "no such field" — that exact wrong
  instrument was used once already on 2026-09-21 and briefly made a true finding look false.
- ⚠️ `bodySize` is not a free number: it drives carrying capacity, food need, meat yield,
  hunt difficulty and melee reach. ⛔ Do not simply retype 2.0 as 1.2 — check what else
  moves. (Project precedent: ceiling fields break when doubled; `bodySize` ≠ melee damage.)
- ⚠️ The header comment's 1.5 is ALSO in the large band if the boundary is 1.5, so
  "restore the commented value" is not automatically the fix. The boundary itself is
  UNMEASURED here — the doc names bands, not thresholds.

## spec

1. Establish what the band thresholds actually are. The doc gives names, not numbers; the
   sibling design (`sweetline_guardian_spec.md`) reads medium as `< 1.5`. Get this written
   down once — every future creature in this biome needs it.
2. Decide the fix: bring the tunnel snake into medium, or put it to the owner as a
   deliberate exception. ⛔ Do not silently rule it an exception — the ladder is his and it
   is marked ratified.
3. Fix the file's header comment either way; prose and def must agree.
4. Sweep the rest of the biome's residents against the same threshold before closing — one
   violation found by accident usually means nobody has checked the others.

## criteria

Every resident creature in the arid shrubland sits in a band the ratified ladder permits,
the thresholds are written down as numbers, and any exception is the owner's explicit call.
