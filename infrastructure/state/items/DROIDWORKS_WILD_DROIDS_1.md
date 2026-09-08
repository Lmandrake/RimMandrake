# DROIDWORKS_WILD_DROIDS_1 — wild crashed droids (packet E4)

Filed thin (title only). The spec below is FOUNDRY's own, written while building,
derived from `design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` §0 ruling 2,
§3.2's "wild droids" row, §5's E4 row, and unit 14 of
`design/Jawa/droid_system_build_spec.md`.

## spec

Owner ruling 2, verbatim, is the load-bearing clause: *"there's the wild droids
that have gone crazy from being left out in the desert after crashing"* — and, in
the same ruling, **no rogue droid faction, ever**. Unit 14's original shape
("Wild-droid faction + seek-a-master behavior") is therefore SUPERSEDED on its
first half: there is no faction. What survives from unit 14 is
"reprogram-as-recruit w/ resistance", which is what this packet builds.

1. **Incident** — a single droid, belonging to no faction at all (`Faction ==
   null`), walks in off the map edge in an erratic hostile mental state. Random
   incident pool only; capped frequency.
2. **Capture** — vanilla, unchanged. Down it, haul it to a prisoner bed. Nothing
   new is needed and nothing new was built.
3. **Reprogram-as-recruit with resistance** — the already-built
   `RSW_DW_DataSpike_Wild` (packet B3, keyed `factionless=true`) is the verb. It
   does NOT flip the droid on the first use: each spike grinds down the pawn's
   vanilla recruitment resistance, and only the use that takes it to zero
   converts the droid to a colonist.

criteria: the incident fires and produces a factionless hostile droid; the
capture loop completes end to end (downed → prisoner → spiked → colonist).

## Built

| file | what |
|---|---|
| `src/RimStarWars/Droidworks/Defs/IncidentDefs/IncidentDefs_Droidworks.xml` | NEW. `RSW_DW_WildDroidCrash` — ThreatSmall, `baseChance 0.7`, `minRefireDays 20`, `Map_PlayerHome`, `pointsScaleable false`. Carries the droid pool as a `WildDroidCrashExtension` modExtension (13 weighted kinds, all Droidworks' own). |
| `src/RimStarWars/Droidworks/Source/Droidworks/IncidentWorker_WildDroidCrash.cs` | NEW. The worker + `WildDroidCrashExtension` + `WildDroidOption`. Generates one pawn with `faction: null`, spawns it at a pawn entry cell, puts it in `ManhunterPermanent`. |
| `src/RimStarWars/Droidworks/Source/Droidworks/CompDWDataSpike.cs` | `requiresPrisoner` and `resistancePerUse` added to `CompProperties_DWDataSpike`; `ValidTarget()` (one shared legality test) and `TryReprogram()` (the resistance loop + the faction flip) added to the comp. |
| `src/RimStarWars/Droidworks/Source/Droidworks/JobDriver_DWDataSpike.cs` | The completion finish-action now calls `comp.ValidTarget` / `comp.TryReprogram` instead of open-coding the downed/prisoner check and an unconditional `SetFaction`. |
| `src/RimStarWars/Droidworks/Source/Droidworks/CompTargetable_DWDataSpike.cs` | Targeting validator now calls the same `ValidTarget`, so the UI gate and the job's own re-check cannot drift. |
| `src/RimStarWars/Droidworks/Defs/ThingDefs/DataSpikes_Droidworks.xml` | `RSW_DW_DataSpike_Wild` gains `requiresPrisoner true`, `resistancePerUse 8`; description rewritten to say so. The three faction-keyed spikes are untouched and keep the original one-use instant flip. |
| `src/RimStarWars/Droidworks/Source/Droidworks/Droidworks.csproj` | one `<Compile Include>` for the new worker. |

Build: 0 errors, 0 warnings. Deployed with `deploy_custom_mods.py --mod
Droidworks --apply` (3 files, "VERIFIED in sync").

## verify

**Offline**

- `xml.etree` well-formedness on all three changed/new XML files: OK.
- `validate_patch.py` on both def files against 601 active mods + the live dump
  `.../DefDump/captures/2026-09-08T22-57-53Z`: **0 errors, 0 warnings**. The one
  `info` line is the expected "no def in the load set uses
  `WildDroidCrashExtension`" — it is our own class, public, namespace matches.
- `IncidentDef.ConfigErrors()` read in the engine source before authoring:
  `category` set, `targetTags` set, no `questScriptDef` → cannot trip the
  both-firing-routes error that killed C5's paired def.

**Live — minimal list (25 mods), quicktest map, 2026-09-08**

| step | observed |
|---|---|
| `jawa/get_def IncidentDef RSW_DW_WildDroidCrash` | found, `modName: Droidworks` — the def loaded, the modExtension did not eat it |
| `jawa/fire_incident RSW_DW_WildDroidCrash dryRun=false` | `fired: true`, 35 points, no dialog |
| the spawned pawn | `faction: null`, `factionName: null`, at a map edge cell; kinds drawn were `RSW_DW_Primitive_G2` and `RSW_DW_OuterRim_BattleDroid` across two firings |
| `jawa/pawn_mental` | `currentState: ManhunterPermanent` on both |
| `pawn_force_incapacitate` → `pawn_set_guest_status Prisoner` | `guestStatusAfter: Prisoner`, **`resistanceAfter: 19.0`** — resistance really is rolled on capture, from the 10~20 the mod's own PawnKind patch supplies, and the pawn's `faction` stayed `null` so the Wild spike still matched |
| colonist Intellectual set to 10 (factor 1.0 → 8/spike), 5 spikes spawned, `ordered_job RSW_DW_DataSpike` repeated | droid stayed factionless after spikes 1 and 2; **flipped to `PlayerColony` on the third** — 19 → 11 → 3 → 0, exactly the designed arithmetic |
| `rimworld/list_colonists` | count 3 → **4**, "Ulyana Vulcafide" now in the roster; host faction and prisoner status gone |
| Player.log | no Droidworks/WildDroid/DataSpike error or NullReference. The only mod exception is the pre-existing `OuterRimCore.OuterRimCoreMod` one |

⇒ E4's verify line ("incident fires; capture loop completes") is **met, live**.

**Not proven** — behaviour on the owner's full 600-mod list (only the minimal
list was loaded), and how often the storyteller actually picks this def in real
play at `baseChance 0.7` / `minRefireDays 20`. Both are load-round questions, not
mechanism questions.

## Assumptions / judgment calls

1. **"Resistance" = the vanilla prisoner recruitment resistance, ground down one
   spike at a time.** This is the least-specified part of the packet and the
   choice was mine. Reasons: the engine already rolls, stores, scribes and
   *displays* `Pawn_GuestTracker.resistance` on any prisoner (the prisoner tab is
   the progress bar, free), it survives save/load with no new state, and it turns
   the loop into something with a cost — spikes are consumable, so a stubborn
   droid costs several. It also makes honest use of the flat 10~20 range
   `Patches/PawnKind_HumanoidDroidResistanceWill.xml` already added as an
   engine-satisfying placeholder; that file's own header said "revisit if
   resistance ever becomes load-bearing for droids specifically" — this is that
   moment, and I deliberately left its numbers alone and tuned the spike's bite
   instead. The alternative considered and rejected was a bespoke
   HediffComp-driven "unstable window" modelled on B5's bolt-rebellion: more
   code, new scribed state, and a payload the player cannot see.
2. **Numbers**: `resistancePerUse 8`, scaled `0.5 + 0.05 x Intellectual level`
   (0.5x at 0, 1.0x at 10, 1.5x at 20). Against 10~20 resistance that is roughly
   2–4 spikes for an average colonist. Intellectual rather than Social because
   nobody is talking the droid round.
3. **`requiresPrisoner true` on the Wild spike only.** `resistance` is the -1
   "unset" sentinel until `CapturedBy` runs, so field-spiking a merely-downed
   wild droid would have no resistance to grind. Requiring capture also matches
   the packet's own ordering. The faction-keyed spikes keep working in the field.
4. **One droid per incident, never a pack.** Not a scope cut — an engine
   constraint found by reading `MentalState_Manhunter.ForceHostileTo(Thing)`:
   for a `Faction == null` target it returns `pawn.RaceProps.Humanlike`. Every
   Droidworks droid race IS humanlike (HAR), so two factionless wild droids
   would be force-hostile **to each other** and brawl on arrival instead of
   coming for the colony. Vanilla never hits this because its manhunters are
   animals, which that same line excludes. A pack would need a faction (ruled
   out) or a different mental state.
5. **`ManhunterPermanent`, not a new MentalStateDef and not `Berserk`.** It is
   the vanilla state for "factionless, permanently hostile, attacks humanlikes",
   its subtree (`SubTrees_Misc.xml`, inside `MentalStateNonCritical`) is reached
   by the humanlike think tree, and `recoverFromCaptured` clears it on capture so
   the prisoner is calm. `Berserk` is already spoken for by B5's bolt rebellion
   and would make the droid attack anything including itself-adjacent neutrals.
6. **No `exitMapAfterTick`.** Vanilla's manhunter animals get one; a humanlike
   manhunter's think-tree branch holds `JobGiver_Manhunter` and
   `JobGiver_WanderAnywhere` and no exit-map giver, so setting it would promise a
   departure that never happens. The droid stays until killed or taken — which is
   also the honest fiction. The frequency cap is what keeps the map clean.
7. **No points scaling and no `combatPower`-driven pick.** Every utility droid
   kind in this mod carries the `combatPower 99999` "keep out of raid pools"
   sentinel, so any points arithmetic over the pool would have silently excluded
   precisely the abandoned-labour droids that are most on-theme.
8. **Pool composition is mine**: 13 kinds, all Droidworks' own (so the pool
   cannot break when the donors retire under D2/D3/D4), weighted abandoned
   labour/salvage highest, old war leftovers next, oddities (G2, gonk) rarest.
   The Junker suicide droid is deliberately excluded — it is Junker-faction
   flavour, C1's business, not a desert wreck.
9. **`WildDroidOption` is a plain `<li>` list, not vanilla's `PawnGenOption`.**
   `PawnGenOption` carries a `LoadDataFromXmlCustom`, and an `<li>` against such
   a field discards the whole containing def silently. Not worth the risk for a
   field-name saving.
10. **Worldgen rule is not engaged.** This is a live incident firing during play,
    not worldgen; nothing generates a planet, a variant or a seed.
