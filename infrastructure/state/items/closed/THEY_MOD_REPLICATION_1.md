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

## FOUNDRY progress, 2026-09-28 (offline pass; live verify pivoted away mid-session)

**Re-verified the prior build stands, nothing rebuilt.** `src/RimUtinni/GreentideRaidAnt/About/About.xml`
carries `mandrake.rut.greentideraidant`; `RM_CreatureBehaviors.csproj` still lists
`<Compile Include="RM_DirectedAssaultExtension.cs" />` and
`RM_JobGiver_DirectedAssault.cs`; both source files exist; `git status` on
`src/RimUtinni/GreentideRaidAnt` and `src/RimMandrake/CreatureBehaviors` is clean
(committed at `feddf8808`/`dff88d3e0`); `dll_source_stamp.py check` reports MATCH
for `RimMandrake.CreatureBehaviors.dll` — no rebuild needed.

**Deploy: already in sync, no `--apply` needed.**
`deploy_custom_mods.py --mod GreentideRaidAnt` → "in sync (7 files)".
`RM_CreatureBehaviors` is folded into `RimMandrake.Biomes` now (wave 2,
`Biomes.compose.json` entry `CreatureBehaviors`/`group: engine`) —
`deploy_custom_mods.py --compose biomes` → "in sync (1108 files, 9 held)", the 9
holds are all unrelated TheSump art-pending items. Both mods were deployed to the
live Mods folder before this pass; nothing needed writing this time.

**Patch/dependency sweep — confirmed clean, no functional donor reference anywhere.**
Grepped the 4 named patches (`MegafaunaYield.xml`, `AnimalTolerances_Ashkarr.xml`,
`OnlyOurFactions.xml`, `Armour_Leather.xml`) plus `Doctrine/About/About.xml` for
`Sapiently|TheyAtomicMonsters|GiantAnt_Race|MyAntMod`: the only hits are a removal
comment in `MegafaunaYield.xml` ("BoneAmount block removed — GiantAnt_Race is
retired") and a "REMOVED" line in Doctrine's About.xml provenance comment — no
`<modDependencies>`, `<loadAfter>`, or `MayRequire` targets the donor anywhere. A
sitewide sweep (`grep -rl "Sapiently\.TheyAtomicMonsters\|MyAntMod\."` over `src/`
and `design/`) turns up only prose/doc-comment mentions in our own new files
(`RM_DirectedAssaultExtension.cs`, `RM_JobGiver_DirectedAssault.cs`,
`GreentideRaidAnt`'s own About.xml/race/thinktree XML) — all describing what was
replaced, none of them a live reference.

**Savegame donor-reference check — done directly against the raw `.rws`, no bridge
needed, confirms the item's prior "no save-embedded Things" finding rather than
assuming it.** Grepped `CANONICAL_ASHKARR_START_2026-09-12.rws` (17.5 MB, offline
file read) for `GiantAnt_Race`, `They_AntCarapace`, `They_CarapaceWall`,
`GiantAnt_Faction`, `Corpse_GiantAnt_Race`: 12 + 8 + 1 + 7 raw hits, but every one
is inside a universal catalog list — `ThingFilter`/stockpile-bill `allowedDefs`
`<li>` lists (which enumerate every ThingDef the game knows, used or not), a
per-def `recordsDeflate` production-stats bucket (`<thingDef>...</thingDef>`, same
universal-catalog shape), a `FactionManager`-style known-factions `<li>` list, and
an animal-catalog `<li>` list — never the placed-object pattern. Checked the
placed-object pattern directly: `<def>GiantAnt_Race</def>`,
`<def>They_AntCarapace</def>`, `<def>They_CarapaceWall</def>`,
`<def>GiantAnt_Faction</def>`, `<def>Corpse_GiantAnt_Race</def>` (a Thing/Pawn's
own def tag as a direct sibling, not inside a `<li>` filter list) all return **0**,
and `GiantAnt_Faction` never appears as an actual `<faction>` record (leader,
goodwill, etc.) — only the one catalog `<li>`. **Confirmed: a savegame scrub is not
needed for this retirement**, matching the original scan's conclusion but now
checked against the actual canonical save rather than assumed.

**Added `modset_builder.py` tier `greentideant`** (`src/RimMandrake/Utils/modset_builder.py`):
`want = [BRIDGE, "mandrake.rm.biomes", "mandrake.rut.greentideraidant"]` resolves
to a clean 14-mod dependency closure with **no** `MISSING` and, critically,
**`Sapiently.TheyAtomicMonsters` absent from the want list entirely** — that
absence *is* the retirement test. Plan-only run confirmed the closure (Harmony,
Core+5 DLC, RimBridgeServer, VEF, AlphaBiomes, FlowWorks, LuminousPigment,
mandrake.rm.biomes, mandrake.rut.greentideraidant — 14 total, down from 614).
**Not yet applied or loaded.**

**Live verify did NOT happen this pass — pivoted away mid-session.** Took the
bridge (`rimflow bridge take`) and measured the game directly: `RimWorldWin64`
running, bridge answering (`Bridge token:` fresh in `Player.log`, main-menu
startup on the full 614-mod list, no colony/save loaded — confirmed via a
`Player.log` tail before touching anything, so no active campaign was ever at
risk). Mid-preparation (writing the `greentideant` tier, about to bring the game
down to apply it), the coordinating session relayed that another window had
broadcast `./game down` and instructed this window to stop bridge work and pivot
to offline-only. **No live action was taken on the process or on
`ModsConfig.xml`** — `bridge release` was run immediately, and the
`greentideant` tier plan was never `--apply`'d.

**Deliberately NOT done this pass, and why:**
1. **Live full-list-analog verify** (race/pawnkinds load with no missing-def
   errors under the `greentideant` tier; carapace item + wall buildable/spawnable;
   `RM_JobGiver_DirectedAssault` actually drives an off-map assault) — blocked on
   a free bridge and `needs: game-up`; the tier to run it with now exists
   (`modset_builder.py --tier greentideant --apply`).
2. **Retirement-completion**: removing `Sapiently.TheyAtomicMonsters` from the
   live `ModsConfig.xml` and from `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`,
   and adding it to `infrastructure/state/facts/retired_mods.json` (the
   `51ede08fe` biomescore-retirement pattern) — deliberately deferred until the
   live verify above actually passes; doing it first would retire the dependency
   before proving the replacement works.
3. Wall art (`rut_greentideant_carapacewall_atlas`/`_menuicon`) — still pending in
   `infrastructure/artpipe/pending/`, artpipe daemon's Codex auth issue, not
   something this pass can fix or needs to block on for the verify itself (the
   6 done art jobs cover the body/dessicated states).
4. The naming card (`NONCANON_BEAST_RENAME_1`) — unchanged, still owed, still not
   a build-seat decision.

Left `doing`. Everything above the "Live verify" heading is genuinely finished
and does not need repeating; what remains is exactly steps 1-2 immediately above,
both gated on `needs: game-up` + a free bridge, next FOUNDRY pass.

## FOUNDRY progress, 2026-09-28 (live verify completed, retirement closed)

Bridge confirmed free and taken (`bridge take --for "live verify + finish donor
retirement"`); game confirmed RUNNING via `./game`, matching the prior pass's
handoff state.

**Built and applied `modset_builder.py --tier greentideant --apply`** (14 mods:
Harmony, Core+5 DLC, RimBridgeServer, VEF, AlphaBiomes, FlowWorks,
LuminousPigment, `mandrake.rm.biomes`, `mandrake.rut.greentideraidant` —
`Sapiently.TheyAtomicMonsters` absent). Confirmed `mandrake.rm.biomes`
(deployed at `RimMandrake.Biomes\Biomes\_Kits\CreatureBehaviors\Assemblies\
RimMandrake.CreatureBehaviors.dll`) carries the DirectedAssault DLL before
restarting.

**Found and fixed a genuine, unrelated, live-blocking bug on the very first
restart** (fixed on sight per CLAUDE.md "correctness outranks seat
ownership" — not part of this item's original scope, but it stood between
any live verify and a working game, and left standing it would have crashed
the NEXT fresh worldgen — quicktest or otherwise — under the full campaign
list too):

- Three `ParentName="<ConcreteVanillaDefName>"` references
  (`RM_ChillHeatedSuit` → `Apparel_Vacsuit`, `RM_SandBusterMound` → `Hive`,
  `RM_SandBusterTunnel` → `TunnelHiveSpawner`, all authored earlier the same
  day, `5eaa306e4`/`0c6e84064`) **never resolved, on any mod list, ever** —
  RimSage-confirmed against the decompiled `Verse/XmlInheritance.cs`:
  `GetBestParentFor` indexes inheritance-parent candidates *only* by an XML
  node's own `Name="..."` attribute, never by `<defName>`, and none of those
  three vanilla/Odyssey defs carry one (they're concrete, playable defs, not
  templates). Left null `thingClass` NREs
  `ReadingPolicyDatabase.GenerateStartingPolicies()`
  (`item.thingClass.SameOrSubclassOf<Book>()`) inside `Game..ctor()` —
  crashing new-colony creation, quicktest, AND campaign save load alike, the
  moment any of the three is active. Confirmed deployed live and byte-identical
  to repo before fixing (both files are folded into `mandrake.rm.biomes`,
  which is in the live campaign's `ModsConfig.FULL.LATEST.xml`) — this was a
  real, latent risk to the owner's own next load, found only because this
  item's live verify happened to construct a `Game` for the first time since
  those files landed. Fixed by inheriting from the actual abstract templates
  (`ApparelBase`, `BuildingNaturalBase`, `EtherealThingBase` — all of which do
  carry `Name=`) and restating, verbatim, every field the concrete defs added
  on top of them, so nothing the original authors intended to inherit was lost.
- A second, independent instance of the same defect class:
  `RM_LanternDeeps` (`0c6e84064`-adjacent, `LANTERNDEEPS_RM_MOD_BUILD_1`,
  2026-09-26) declares no `<workerClass>` at all and never sets
  `generatesNaturally=false`/`canAutoChoose=false` (unlike its sibling seabed
  placeholder biomes, which do). `WorldGenStep_Terrain.BiomeFrom` iterates
  every `BiomeDef` for every tile of a fresh world and only short-circuits on
  `generatesNaturally` before touching `.Worker` (RimSage-confirmed) — so with
  it left `true` (the field's default), this def entered ordinary surface-tile
  scoring and crashed `BiomeDef.Worker` (`workerClass` null) on effectively the
  first tile of any fresh worldgen. The file's own header already claimed "no
  seed can place it" / "nothing here for worldgen to score" — the fix
  (`generatesNaturally=false`, `canAutoChoose=false`) simply makes that true,
  matching the pattern already used for the seabed placeholders two mods over.
- Both fixes are additive/restorative only — no field any other item depends
  on was removed. Deployed (`deploy_custom_mods.py --compose biomes --apply`),
  restarted, and reverified clean before proceeding (0 "Could not find parent
  node" hits, 0 null-thingClass Config errors, worldgen completed).
- **Noted but NOT fixed** (out of scope, does not block this item, not
  introduced by anything here): one further `Could not find parent node named
  "RM_BaseGasDamaging"` hit on the full 614-mod boot — same defect family,
  different content, worth a follow-up item but not chased down this pass.

**Live verify, on the fixed 14-mod `greentideant` tier**
(`start_debug_game_ready`, worldgen succeeded once the LanternDeeps fix
landed):
- `jawa/get_defs` on all 7 replicated defs (`RUT_GreentideAntRace`, both
  pawnkinds, `RUT_GreentideAntFaction`, the carapace item, the carapace wall,
  `RUT_ThinkTree_GreentideAnt`) — **7 of 7 resolved**, no errors.
- `Player.log`: zero `Sapiently`/`TheyAtomicMonsters`/`MyAntMod` hits anywhere
  on the tier; the only GreentideAnt-related lines are two expected
  texture-not-found warnings (body + wall atlas art still pending, as already
  noted above — unrelated to this pass).
- Spawned `RUT_GreentideAntCarapace` and `RUT_GreentideAntCarapaceWall` via
  `rimworld/spawn_thing`, then independently confirmed both as real map
  presences via `jawa/list_things` (not trusting the bare `success: true`):
  carapace item 100/100 HP at its spawn cell, carapace wall building 250/250
  HP at its spawn cell, `scanned: 33372`.
- Spawned 12 `RUT_GreentideAntSoldier` pawns hostile-factioned, recorded
  positions, ran `rimworld/step_game_ticks` (583 ticks, game stayed paused —
  a mutation observed without a UI unpause), and read positions back: **12 of
  12** moved ~25-28 tiles, converging tightly on a point directly along the
  vector from their spawn cluster toward the actual colonist positions ~80
  tiles away — real directed movement toward the colony, not idling or random
  wander, confirming `RM_JobGiver_DirectedAssault` actually drives the
  behavior (`directedAssaultBehaviorEnabled` confirmed `true` by default in
  `RM_CreatureBehaviorsMod.cs`).

**Retirement completed.** Killed the game (Steam launch preserved throughout;
`Stop-Process`/relaunch via `steam.exe -applaunch` only), built the
post-retirement list from the verified pre-session full list
(`deployed/config/ModsConfig.before-tier-greentideant.xml`, 614 mods,
confirmed byte-identical in content to `ModsConfig.FULL.LATEST.xml` before
touching anything): removed `sapiently.theyatomicmonsters`, inserted
`mandrake.rut.greentideraidant` immediately after `mandrake.rm.biomes` (its
functional dependency, and — since `mandrake.rm.biomes` was already the last
entry — also the new last entry, a safe position since GreentideRaidAnt
patches nothing and needs no specific load-order relative to anything else).
Wrote the result to **both** the live `ModsConfig.xml` and
`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (614 mods each,
donor absent, replacement present — verified by parsing, not counting).
Backed up the live file first
(`deployed/config/ModsConfig.before-THEY_MOD_REPLICATION_1-retirement-write.xml`).

**Restarted on the real, full 614-mod list** (~17 minutes, `Bridge token:`
at `Player.log` line 59432) as the full-campaign-tolerates-the-removal proof
— boot-to-main-menu only, no quicktest/worldgen attempted on the full list
per the standing doctrine against that. Result: **no** corrupted-mods
recovery reset, **zero** `Sapiently`/`TheyAtomicMonsters`/`MyAntMod` hits
anywhere in the whole log, **zero** Config errors or exceptions naming any
GreentideAnt/Carapace/ChillHeatedSuit/SandBusterMound/LanternDeeps def. The
9 exceptions and 322 Config errors present in the full-list log are
pre-existing and unrelated (ShipVermin, RSW_Shokk, FlowWorks/DeepSand,
KurrethSwarm, TheSump, CannibalPirate/PirateYttakin — none touched by this
item). This is the boot-to-menu-is-sufficient path from the task brief, not
a full colony/save load — judged sufficient because the quicktest tier
already proved mechanism+behavior and this pass only needed to prove the
full dependency graph tolerates the swap.

Added the retirement to `infrastructure/state/facts/retired_mods.json`
(packageId `Sapiently.TheyAtomicMonsters`, `retiredOn: 2026-09-28`, `item:
THEY_MOD_REPLICATION_1`), following the schema and `51ede08fe` precedent.

**Still owed, explicitly out of this item's/a build seat's scope, does not
block closing:**
1. The coined pseudo-Star-Wars name (`NONCANON_BEAST_RENAME_1`) — labels are
   still the donor's plain-English "giant ant" / "heated dive suit"-adjacent
   text; defNames are stable and ready for the label swap once carded.
2. Wall + body art — artpipe jobs already filed
   (`infrastructure/artpipe/pending/rut_greentideant_*.json`), daemon-side,
   not a build-seat blocker.
3. Follow-up item for the `RM_BaseGasDamaging` parent-node XML error found
   on the full-list boot (same defect family as the three fixed here,
   different content, not chased down this pass).

Released the bridge as the last action. Closing via `rimflow close`.
