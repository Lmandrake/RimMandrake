1. **A herd’s migration ends when it reaches a persistent colony map**

   **Where:** `src/RimMandrake/Pyrelands/Source/WorldObject_RM_FurnaceHerd.cs:149`; `src/RimMandrake/Pyrelands/Source/Patch_FurnaceHerdMapRemoval.cs:36`.

   **Mechanism:** Delivery spawns the members and destroys their world object (149–150, 160–167), losing the herd’s migration clock and identity. The only return hook runs when the **whole map** is removed; individual edge exits are explicitly excluded (map-removal patch, 36–46). Consequently, a visiting herd cannot complete its thermal circuit while the colony map persists. Animals that eventually leave through vanilla wildlife behaviour acquire no replacement herd or readable migration sign.

   **Repro:** Deliver a world herd onto a home map and keep that map loaded. Charge its members fully; they have only local thermal behaviour. Force one member’s ordinary map-exit job: it leaves without joining a migrating world herd.

   **Severity:** gameplay-visible.

   **Check:** Record member ThingIDs before delivery, then inspect world-herd membership after delivery and after a forced normal edge exit. No long wait is necessary.

   **Confidence:** high.

2. **A burrowed grazer can still die of Heatstroke while sheltering**

   **Where:** `src/RimMandrake/Pyrelands/Defs/HediffDefs/RM_PyrelandsHediffs.xml:41`; `src/RimMandrake/Pyrelands/Defs/ThingDefs_Races/RM_Ashwallow.xml:61`.

   **Mechanism:** Burrowing adds only heat armor and reduced flammability (hediff XML, 41–44). Ashwallow’s maximum comfortable temperature remains 120°C. The driver holds position until nearby fire clears or the timer expires (`RM_JobDriver_Burrow.cs:59–70`), without changing temperature exposure. Vanilla Heatstroke increases directly from ambient temperature above the safe range; armor does not protect against that severity adjustment. [Vanilla heat giver](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/HediffGiver_Heat.cs).

   **Repro:** Let an ashwallow burrow beside ground fire in an enclosed burning room whose temperature exceeds its safe range. Its burrowed status remains while Heatstroke accumulates.

   **Severity:** gameplay-visible.

   **Check:** Short controlled probe: read `RM_Burrowed`, safe temperature range, ambient temperature and Heatstroke severity before and after several health intervals.

   **Confidence:** high.

3. **Caravan furnace-beasts freeze their charge and provide no walking-hearth warmth**

   **Where:** `src/RimMandrake/Pyrelands/Source/CompFurnaceThermalCharge.cs:83`; `src/RimMandrake/Pyrelands/Source/CompFurnaceWarmthAura.cs:139`.

   **Mechanism:** Normal charge updates reject unspawned beasts (thermal-charge comp, 83–85). The alternative world update is called only for pawns inside the custom herd (`WorldObject_RM_FurnaceHerd.cs:220–225`). Caravan members belong to neither path. Warmth also explicitly returns zero for unspawned recipient pawns (warmth aura, 139–142). A tamed beast therefore preserves its stored charge indefinitely during caravan travel while offering its companions no warmth—the journey specifically promised by the biome design.

   **Repro:** Form a caravan containing a charged furnace-beast and a colonist. Travel or rest on a cold tile; repeat on a hot tile.

   **Severity:** gameplay-visible.

   **Check:** Compare the beast’s saved `furnaceThermalCharge` before and after a short caravan interval. Read `FurnaceWarmthField.OffsetFor` for its companion; it returns zero.

   **Confidence:** high.

4. **Disabling the mechanics leaves active burrows and ember deliveries running**

   **Where:** `src/RimMandrake/Pyrelands/Source/RM_JobDriver_Burrow.cs:57`; `src/RimMandrake/Pyrelands/Source/JobDriver_RUT_FireHawkCarryEmber.cs:66`.

   **Mechanism:** Settings are checked when jobs are offered (`RM_JobGiver_BurrowOnFire.cs:53–55`; hawk giver, 40–42). Neither driver rechecks them. The burrow’s only exit conditions are fire clearance and timeout (59–70), so its protective hediff persists after disabling the feature. The hawk’s drop action still calls `TryStartFireIn` (68–83), including after disabling the master gate. Reloading a save containing either active job preserves the same omission.

   **Repro:** Disable burrowing while an animal is underground, or disable hawk spreading after an ember has been collected but before delivery. Continue ticking.

   **Severity:** gameplay-visible.

   **Check:** Read the disabled setting, current job and burrow hediff; for the hawk, verify whether its destination gains a new Fire after disabling.

   **Confidence:** high.

5. **The ember-carrying job explicitly loses vanilla flight eligibility**

   **Where:** `src/RimMandrake/Pyrelands/Defs/JobDefs/RM_PyrelandsJobs.xml:21`; `src/RimMandrake/Pyrelands/Source/JobDriver_RUT_FireHawkCarryEmber.cs:48`.

   **Mechanism:** The standalone ember JobDef sets neither `tryStartFlying` nor `ifFlyingKeepFlying` (21–26); both default false. Vanilla’s flight tracker consequently starts no flight for this job and forces an already flying pawn to land. Its driver supplies ordinary Goto toils (48–62) and never starts flight itself. The accepted takeoffs on other jobs do not establish flight during this sortie. [JobDef defaults](https://github.com/Dyyrlysh/RimworldDecompile/blob/main/Verse/JobDef.cs), [flight job handling](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/RimWorld/Pawn_FlightTracker.cs).

   **Repro:** Allow a flight-ready fire-hawk to receive `RM_FireHawkCarryEmber`; also try a hawk already airborne when that job starts.

   **Severity:** gameplay-visible.

   **Check:** **State reads only:** inspect the resolved JobDef flags, `CurJob.flying`, flight state and cooldown at job start and during transit. No visual flight check.

   **Confidence:** high.

6. **Starting with migration disabled permanently consumes that save’s seeding opportunity**

   **Where:** `src/RimMandrake/Pyrelands/Source/WorldComponent_RM_FurnaceHerdSeeder.cs:57`.

   **Mechanism:** `seeded` becomes true **before** checking the master, thermal and migration switches (57–67), and that flag is saved (41–44). Enabling the mechanics later cannot seed herds, even after reloading: initialization immediately returns. The “worldgen-adjacent” comment does not supply an enabling path for this runtime mobile-world-object feature.

   **Repro:** First initialize an otherwise eligible world with migration or the master switch off. Save, enable it, and reload.

   **Severity:** gameplay-visible.

   **Check:** Inspect `<rm_furnaceHerdSeeded>true</rm_furnaceHerdSeeded>` and confirm zero herds despite enabled settings, a qualifying species and valid desert candidates.

   **Confidence:** high.

7. **Furnace warmth passes unchanged through solid walls**

   **Where:** `src/RimMandrake/Pyrelands/Source/CompFurnaceWarmthAura.cs:145`.

   **Mechanism:** The aura checks only species validity, radius and horizontal distance (145–153). It never checks intervening walls, rooms or exposure. The resulting offset is added to the recipient’s ambient temperature (169–171). Thus a beast outside a sealed, cooled bedroom can heat its occupant directly while the room’s measured air remains cool; enclosing either participant provides no shielding from this component.

   **Repro:** Put a furnace-beast outside a cooled room and a colonist immediately across its solid wall, within aura range.

   **Severity:** gameplay-visible.

   **Check:** Read `OffsetFor(colonist)` and room temperature with the wall present, then remove the wall without moving either pawn. The offset is identical.

   **Confidence:** medium.

8. **The walking hearth has no readable proximity status**

   **Where:** `src/RimMandrake/Pyrelands/Source/CompFurnaceWarmthAura.cs:158`; `src/RimMandrake/Pyrelands/Defs/HediffDefs/RM_PyrelandsHediffs.xml:4`.

   **Mechanism:** The old warmth status is retired (hediff XML, 4–5). Its replacement only modifies the temperature getter (aura, 158–177); it supplies no recipient inspect/status text. The surviving inspect string reports the **beast’s charge**, not a nearby pawn’s warmth (`CompFurnaceThermalCharge.cs:161–167`). The validated bar requiring a readable warmth status that disappears on walking away therefore remains unmet, even when the numerical offset works.

   **Repro:** Select a healthy colonist beside a beast, then move outside its aura.

   **Severity:** cosmetic/perf.

   **Check:** Compare the pawn’s inspect/status text near and away alongside a positive-then-zero `OffsetFor` read. This distinguishes missing feedback from a nonworking aura.

   **Confidence:** high.

9. **Every burrowed animal repeatedly scans the entire map’s fire list**

   **Where:** `src/RimMandrake/Pyrelands/Source/RM_JobDriver_Burrow.cs:57`; `src/RimMandrake/Pyrelands/Source/RM_JobGiver_BurrowOnFire.cs:103`.

   **Mechanism:** Every hide-toil tick calls `FireIsNear` (driver, 57–64). That method walks the global Fire list until finding a nearby ground fire (giver, 103–111), with no sampling interval or cached result. During a broad burn, list ordering can put each animal’s nearby fire near the end, producing roughly **burrowers × map fires per tick** for the duration of sheltering. This cost persists even after disabling burrowing, as finding 4 describes.

   **Repro:** Stage many burrowers beside newly created local fires after creating thousands of distant fires first.

   **Severity:** cosmetic/perf.

   **Check:** Count loop iterations in a short instrumented probe. With 100 burrowers and 5,000 distant-first fires, the path approaches 500,000 fire examinations per game tick.

   **Confidence:** high.

No additional finding for save serialization/session caches (hunt points 1–2), plant ticking (5), Harmony signatures/common-mod conflicts (8), or map generation (11) within the supplied files; the ledger’s completed timer, nudge and registry fixes are not re-reported.