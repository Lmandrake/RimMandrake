1. **Turning off “Fire clock” leaves its advertised raids and visits enabled**
   - **Where:** `src/RimMandrake/Pyrelands/Source/RM_PyrelandsMod.cs:533`; `src/RimUtinni/PyrelandsMechanics/Source/IncidentWorker_FireRaid.cs:40`; `src/RimUtinni/PyrelandsMechanics/Source/IncidentWorker_FlameHarvest.cs:39`.
   - **Mechanism:** The setting promises that disabling it prevents the Tribes’ incidents (RM_PyrelandsMod.cs:533–535). Neither incident worker checks `fireClockEnabled`: their gates check their own feature switch, the mechanics gate and `burnLineEnabled` instead. An existing burn or arson debt can therefore still produce an incident after the advertised switch is off.
   - **Repro:** Establish a qualifying burn/debt with the relevant incident’s `CanFireNow` returning true. Disable only the fire clock; eligibility remains true.
   - **Severity:** gameplay-visible
   - **Check:** Repeat that eligibility read before and after toggling `fireClockEnabled`; no storyteller wait is needed.
   - **Confidence:** high

2. **A rite can miss the order to leave when its faction becomes hostile**
   - **Where:** `src/RimUtinni/PyrelandsMechanics/Source/LordJob_RUT_FireRite.cs:76`.
   - **Mechanism:** The attached travel subgraph includes the defensive state described at lines 14–17, but only its `StartingToil` is retained as `travel` (76–77). The hostility transition covers `travel` and `rite`, excluding that defensive state (97–103). Vanilla’s hostility trigger responds specifically to a faction-relations-change signal; it does not continuously poll hostility. If war begins while the group is defending, returning to travel does not replay the missed signal. The group can resume its rite while hostile. The travel timeout similarly excludes the defensive state (85–89). [Vanilla trigger implementation](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse.AI.Group/Trigger_BecamePlayerEnemy.cs).
   - **Repro:** Have a third party put the travelling harvesters into their defensive toil, then make the Tribes hostile to the player. End the third-party attack.
   - **Severity:** gameplay-visible
   - **Check:** An offline graph test can enumerate the attached toils and the hostility transition’s sources, then deliver the relation-change signal with the defensive toil active.
   - **Confidence:** medium

3. **The harvester’s “safe standoff” checks the destination, not the route**
   - **Where:** `src/RimUtinni/PyrelandsMechanics/Source/JobGiver_RUT_HarvestScorchFruit.cs:60`.
   - **Mechanism:** Both searches use `TraverseParms.For(pawn)` (60–66, 83–89), whose default maximum danger is `Danger.Deadly`. The validator rejects burning targets and fire on the target’s cell, then checks reservation availability (94–104). It never rejects a route through fire. A cold pod across a burning chokepoint can therefore qualify, contrary to the explicit claim at lines 34–37 that harvesters will not walk into fire to reach it. The preceding safe-temperature giver only decides what to do from the pawn’s current circumstances. [Vanilla traversal defaults](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/TraverseParms.cs).
   - **Repro:** Put a rite harvester in a cool area, with one ripe, unburning pod reachable only through a narrow burning passage.
   - **Severity:** gameplay-visible
   - **Check:** Read the returned harvest job and its planned path; verify that the target cell is fire-free while the path contains burning cells.
   - **Confidence:** high

4. **Full harvesters keep cutting pods after reaching their carry limit**
   - **Where:** `src/RimUtinni/PyrelandsMechanics/Source/JobGiver_RUT_HarvestScorchFruit.cs:55`.
   - **Mechanism:** Inventory count and `wanted` gate only the loose-fruit pickup branch (55–74). Once full—or after lowering the setting to zero—the pawn falls through into the unconditional plant search and receives another `Harvest` job (77–91). It keeps opening pods and leaving their rapidly spoiling yield behind. This contradicts the “before it stops picking” carry-limit contract in `PyrelandsTuning.cs:204–207`.
   - **Repro:** Give a harvester its configured fruit allowance, or lower the allowance below its current inventory, with another ripe pod nearby.
   - **Severity:** gameplay-visible
   - **Check:** Invoke the giver once and inspect the returned job. It returns `Harvest` despite `carried >= fireRiteCarryPerPawn`.
   - **Confidence:** high

5. **The flame-harvest incident has no harvesting phase**
   - **Where:** `src/RimUtinni/PyrelandsMechanics/Source/IncidentWorker_FlameHarvest.cs:99`.
   - **Mechanism:** After spawning the party, the incident assigns only `LordJob_TravelAndExit(watch.BurnCenter)` (93–103). It never assigns `RUT_RiteHarvest` or another harvesting phase. Thus the event described as the Tribes farming a live burn is a walk to the centroid followed by departure. The separate fire-rite implementation contains the actual harvesting duty, but this incident never uses it.
   - **Repro:** Trigger a flame-harvest visit beside a qualifying burn with ripe, safely accessible scorch-fruit.
   - **Severity:** gameplay-visible
   - **Check:** Keep the visitors fed, then read their lord job, duties, current jobs and fruit inventories during the visit. There should be no deliberate harvesting phase or collected harvest.
   - **Confidence:** high

6. **Harvesters can chain their search radius across the map**
   - **Where:** `src/RimUtinni/PyrelandsMechanics/Source/JobGiver_RUT_HarvestScorchFruit.cs:61`.
   - **Mechanism:** Both searches centre their 45-cell radius on `pawn.Position` (61–65, 84–88). Neither validator constrains targets against the duty’s origin. Each successful move therefore moves the next search area, allowing successive pods or fruit stacks to draw a harvester arbitrarily far from the rite. This contradicts `PyrelandsTuning.cs:196–199`, which defines the radius relative to the rite’s origin; the origin is already supplied in the duty at `LordJob_RUT_FireRite.cs:193–197`.
   - **Repro:** Place a harvester 40 cells from the rite origin and a ripe pod another 40 cells farther away. That pod is outside the intended harvesting area but inside the pawn-centred search.
   - **Severity:** gameplay-visible
   - **Check:** Read the returned target and compare its distance with `pawn.mindState.duty.focus.Cell`; it can exceed `FireRiteHarvestRadius`.
   - **Confidence:** high

7. **A defeated first tribe masks another surviving tribe**
   - **Where:** `src/RimUtinni/PyrelandsMechanics/Source/PyrelandsFactions.cs:25`.
   - **Mechanism:** `FirstFactionOfDef` selects the first matching faction; only afterward does this helper reject defeated, temporary or player factions (25–28). It never searches for another valid match. In a save with multiple `TribeCivil` factions, defeating the first can disable fire raids, harvest visits and rites despite another tribe surviving. Vanilla’s lookup does not filter defeated factions. [Vanilla faction lookup](https://github.com/Chillu1/RimWorldDecompiled/blob/master/RimWorld/FactionManager.cs).
   - **Repro:** Use a save containing two `TribeCivil` factions and defeat the first one in faction-manager order.
   - **Severity:** latent
   - **Check:** Read both matching factions’ IDs and defeated flags, then reflectively call `TribesOrNull`; it returns null despite the surviving candidate.
   - **Confidence:** high

No additional findings for hunt points 1–5, 7–8 and 10–11 from the supplied implementation; Harmony bodies, fire/plant tick bodies, GenStep workers and world-herd C# were not supplied, so those portions remain unassessed.