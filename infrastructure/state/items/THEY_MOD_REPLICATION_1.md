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

## FOUNDRY progress, 2026-09-25

Bridge was held by another FOUNDRY window's live-verify batch the whole
session (idle-checked, not stale), so nothing here touched the live game or
deployed to the Mods folder — that would have contaminated the concurrent
session's test. Everything below is repo-only, offline-validated.

**Done** — the donor's own on-disk XML was read directly (workshop id
3620253282, never decompiled) and re-authored 1:1 into a new standalone
mod, `src/RimUtinni/GreentideRaidAnt` (`mandrake.rut.greentideraidant`):
race (`RUT_GreentideAntRace`), both pawn kinds (`RUT_GreentideAnt`,
`RUT_GreentideAntSoldier`), the hidden permanentEnemy faction
(`RUT_GreentideAntFaction`), the carapace leather (`RUT_GreentideAntCarapace`)
and the carapace wall (`RUT_GreentideAntCarapaceWall`) — all well-formed XML,
no defName collisions in the live dump. The values donor's
MegafaunaYield.xml/AnimalTolerances_Ashkarr.xml/Armour_Leather.xml patches
computed (MeatAmount 280, BoneAmount 100, ComfyTemperature -63.2..75.8, the
boosted armor statFactors) and OnlyOurFactions.xml's
`startingCountAtWorldCreation 0` are now stated directly in our own defs, so
none of those four patches need to target it — their donor-referencing
blocks were removed instead (git provenance covers what they said). Doctrine's
`loadAfter` entry for `Sapiently.TheyAtomicMonsters` is gone too.

The one donor C# piece, `MyAntMod.JobGiver_AntRaid` (not decompiled), is
replaced by a new generic pair in `mandrake.rm.creaturebehaviors`:
`RM_DirectedAssaultExtension` + `RM_JobGiver_DirectedAssault` — built from
vanilla patterns (`AttackTargetFinder.BestAttackTarget`, the same call
`JobGiver_AIFightEnemy` makes) rather than the donor's bytecode: attack the
nearest hostile if one is in range, otherwise march on the colony instead of
idling, replicating the "off-map directed assault bypassing the incident
system" shape. Gated behind a new mod-settings toggle
(`directedAssaultBehaviorEnabled`, #29 in that assembly's kit). Builds clean
(`dotnet build … RM_CreatureBehaviors.csproj -c Release`, 0 warnings/0
errors) and the new `.dll` is committed. `RUT_ThinkTree_GreentideAnt` mirrors
donor's subtree order exactly, swapping in the new JobGiver.

`design/Jawa/fauna/cast_assignment.csv` row and
`design/Jawa/worldbuilding/biomes/rosters/the_greentide.json`'s roster entry
now point at `RUT_GreentideAntRace` instead of `GiantAnt_Race`.

Validated: `validate_patch.py --live <dump>` on all four edited patch files —
0 errors (2370 pre-existing advisory warnings, none new). `run_selftests.py`
— 73/75 pass; the 2 failures (`selftest_live_prep`,
`selftest_deployed_biome_refs`) are pre-existing, on RotSporeKit/Scald-flora
content this item never touched — not introduced here.

8 artpipe jobs filed (`fill_queue.py`, no `reference=` — new art, not a
reskin) for the body (3 facings), the dessicated body (3 facings), the wall
atlas and the wall menu icon, sized to match the donor's own canvas
(512×512 body/dessicated at drawSize 2.0, 640×640/128×128 wall) —
`infrastructure/artpipe/pending/rut_greentideant_*.json`; nothing equivalent
existed in `artpipe/done/` already (checked by subject before filing).
These are left uncommitted deliberately — the daemon claims and moves them
through `active/`→`done/` on its own schedule.

**Owed, and why it isn't done here:**
1. **The label is still the donor's own plain-English "giant ant"** — a
   coined pseudo-Star-Wars name is a `kind: design` decision per
   `NONCANON_BEAST_RENAME_1`, carded to the owner in a batch, never ruled by
   a build seat. defNames are already ours and stable; only the label (and
   its description) need to change once carded.
2. **Art isn't rendered yet** — queued, not generated or reviewed.
3. **Live full-list verify** (They! disabled, raids still fire, carapace +
   wall buildable) needs the bridge, which another FOUNDRY window held for
   its own live-verify batch the entire session.
4. **Deployment and the actual `ModsConfig.xml`/mod-list removal** — not
   attempted for the same reason (would contaminate the concurrent bridge
   session); `deploy_custom_mods.py` + a cold load are the next steps once
   the bridge is free.

Left `doing`, not `blocked` — nothing here is stuck, it just needs the art
job to finish, a naming batch with the owner, and a free bridge, none of
which are answered by asking a question back.
