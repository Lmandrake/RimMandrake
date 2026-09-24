# THEY_MOD_REPLICATION_1 — replicate They! (Giant Ants) ourselves, retire the dependency

## the ruling

Owner, 2026-09-24 (typed this session): the ant is queued for replacement and
retirement; he asked for a scan of what else the mod holds and how hard it is
to replicate. Scan done same day (BENCH subagent, read the installed mod at
workshop id 3620253282). **No prior retirement ruling exists** — the only prior
ruling on this mod is usage: `GiantAnt_Race` is Greentide raid-events-only, not
wildlife (`BIOME_FAUNA_ASSIGNMENT_SITTING_1`, closed).

## What the mod is — MEASURED 2026-09-24

`Sapiently.TheyAtomicMonsters`, 1.6-only, tiny: 1 race (`GiantAnt_Race`),
2 PawnKindDefs, 1 hidden permanentEnemy FactionDef, 1 ThinkTreeDef whose raid
behavior lives in ONE custom C# JobGiver (`MyAntMod.JobGiver_AntRaid`,
10.75 KB DLL — an off-map directed assault bypassing the incident system).
**Beyond beasts + raids it holds only:** `They_AntCarapace` (leather-category
stuff) and `They_CarapaceWall` (one building), plus 2 sounds and 8 textures.
No research, quests, terrain, apparel, or settlements.

## Our touchpoints to unwind (from the scan)

- `src/RimUtinni/Doctrine/About.xml:100` — the dependency listing.
- `design/.../rosters/the_greentide.json` + `cast_assignment.csv:173` — the
  raid-events-only import (commonality 0.5, Greentide).
- Patches referencing it: `Doctrine/Patches/MegafaunaYield.xml`,
  `UtinniPatches/Patches/AnimalTolerances_Ashkarr.xml`,
  `UtinniPatches/Patches/FactionSlate/OnlyOurFactions.xml` (already zeroes its
  faction at worldgen), `RimStarWars/Armoury/Patches/Armour_Leather.xml`.
- Not in any `WildAnimals_*.xml`; no Cherry Picker cut touches it.

## spec

1. Re-author the whole surface in our tier (race, 2 pawnkinds, hidden raid
   faction, carapace stuff, carapace wall, 2 sounds): plain XML, trivial.
2. Re-implement the one C# piece — a small JobGiver/ThinkNode driving the
   directed off-map assault — in our own assembly, from vanilla JobGiver
   patterns, NOT by decompiling the DLL. Remember
   `RM_CreatureBehaviors.csproj` lists every file: new `.cs` needs its
   `<Compile Include>` line.
3. New art: ant + dessicated + wall textures (queue via artpipe; no
   `reference=` — new art, not a reskin). Sounds: two short clips, source or
   synthesize.
4. The replicated beast takes a COINED pseudo-SW name per
   `NONCANON_BEAST_RENAME_1`'s standard ("giant ant" is an Earth name) — card
   the name with the next batch; the def is born with the ruled label.
5. Retire: flip the Greentide import to our def, remove the About.xml
   dependency and the four donor-referencing patches (or convert to target our
   def), then the mod leaves the list per the Charter's expensive-list process.

## verify

Full-list session with They! disabled: no missing-def errors, Greentide ant
raids still fire from our def, carapace + wall buildable.

## criteria

Nothing in the campaign references `Sapiently.TheyAtomicMonsters`; the ant
experience survives under our own defs, name, and art. Estimated scope from
the scan: **about a day** — the JobGiver is the only real work.
