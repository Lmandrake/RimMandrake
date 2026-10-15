1. **Scorch-fruit’s Normal ticker bypasses the plant lifecycle**
   - **Where:** `src/RimMandrake/Pyrelands/Defs/ThingDefs_ScorchFruit/ScorchFruit.xml:89–90`; `src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs:238–239`
   - **Mechanism:** The def explicitly schedules `Plant` as Normal, while plant growth, ageing and environmental checks run through `TickLong`. The spawn code also never assigns `Growth`, despite the XML’s claim that pods spawn ripe (lines 13–15). Pods therefore retain their initial growth. The very low harvest threshold, `0.01` (line 76), can conceal this behind successful harvest tests. Normal ticking can run inherited comp ticking; this finding does **not** assume that rot is disabled.
   - **Repro:** Spawn a pod in favourable temperature and daylight; inspect growth and age before and after 4,000 simulated ticks.
   - **Severity:** gameplay-visible
   - **Check:** Read the merged def’s ticker, then compare the spawned plant’s growth and age across that short advance.
   - **Confidence:** high

2. **Saving and loading gives surviving fires another scorch-fruit roll**
   - **Where:** `src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs:149–160,220–239`; `src/RimMandrake/Pyrelands/Source/Kernel/RM_FireEcoKernel.cs:323–330`
   - **Mechanism:** The per-map weak table correctly fixes the logged cross-reload ID collision. However, its replacement map starts with an empty, unsaved set. Fires restored from the save consequently lose their “already rolled” status and pass lines 221–229 again. This breaks the stated one-roll-per-Fire rule for fires that survive a save/load.
   - **Repro:** Let a cohort of long-lived fires take its rolls, save while they remain alive, then load and advance one fire interval. Those same saved fires roll again.
   - **Severity:** gameplay-visible
   - **Check:** Temporarily set fruit chance to 1 with cap headroom. Save after the first placements, reload, and check for additional pods from unchanged fire IDs.
   - **Confidence:** high

3. **Fruit placement accepts unburned neighbours, including firebreaks**
   - **Where:** `src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs:223–239`; `src/RimMandrake/Pyrelands/Source/Kernel/RM_FireEcoKernel.cs:286–301`
   - **Mechanism:** Only the fire’s source terrain passes the scorchable-ground gate. Candidate destinations need merely be in bounds, standable and plant-free (line 227). Nothing checks destination terrain, roof, or burn history. An occupied burning cell can therefore seed a pod onto an adjacent, untouched firebreak or paved cell. Direct `GenSpawn.Spawn` supplies no missing wild-plant placement checks.
   - **Repro:** Ignite grass on eligible ground beside a bare firebreak; keep the source plant standing until the roll. With chance 1, the first accepted bare neighbour receives a pod without burning.
   - **Severity:** gameplay-visible
   - **Check:** Record destination terrain and burn stamp before ignition, then read the spawned pod’s position. A pod on the never-burned firebreak confirms it.
   - **Confidence:** high

4. **Ordinary fires activate Pyrelands ecology without biome opt-in**
   - **Where:** `src/RimMandrake/Pyrelands/Source/Kernel/RM_FireEcoKernel.cs:74–84,98–102,202–210`; `src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs:174–185`
   - **Mechanism:** Vanilla `Soil`, `SoilRich`, `Sand` and `Gravel` qualify everywhere. The fire postfix checks the global mechanics switch, feature switches and source terrain, but never the map’s biome or cross-biome selection. Thus an ordinary forest fire can stamp fresh-burn fertility, dust custom ash and produce scorch-fruit with cross-biome opt-in disabled. The comment promising vanilla terrains “for biomes that opt in” has no corresponding gate.
   - **Repro:** With normal Pyrelands defaults and cross-biome options off, burn a grass patch on vanilla Soil on a TemperateForest map.
   - **Severity:** gameplay-visible
   - **Check:** Set fruit chance to 1 and inspect for pods and burn stamps on that control map.
   - **Confidence:** medium

5. **The furnace-beast’s vanilla room heater has no visible settings gate**
   - **Where:** `src/RimMandrake/Pyrelands/Patches/RM_PyrelandsIgniters_Comps.xml:29–33,84–95`
   - **Mechanism:** When the FindMod branch matches, the patch installs an ordinary `CompProperties_HeatPusher` with positive heat output (lines 88–90). Vanilla owns its execution; the XML supplies no connection to the Pyrelands master or furnace feature switches. Unless another patch outside this packet suppresses that vanilla comp, disabling the mechanics leaves room heating active.
   - **Repro:** Put a furnace-beast in a room below 24°C, disable Pyrelands mechanics, and compare room temperature with an otherwise equivalent empty room.
   - **Severity:** gameplay-visible
   - **Check:** First inspect installed Harmony patches for a relevant `CompHeatPusher` gate. If absent, perform the short room-temperature comparison with the custom aura disabled.
   - **Confidence:** medium

6. **Burn history retains expired grazing anchors indefinitely during quiet periods**
   - **Where:** `src/RimMandrake/Pyrelands/Source/MapComponent_BurnLine.cs:117–132,324–328`; `src/RimMandrake/Pyrelands/Source/Kernel/RM_BurnKernel.cs:49–76`
   - **Mechanism:** Ten-day pruning occurs only when `RecordHistory` adds a sample (kernel lines 55–60). The component returns before calling it when no burn centre exists (lines 119–121). Meanwhile, `HistoryIndexAgo` accepts arbitrarily old samples. A prolonged fireless map therefore continues returning an obsolete location as its two-day-old burn anchor.
   - **Repro:** Record a burn, extinguish it, disable the fire clock and prevent lawful reseeding. After more than ten days, query `BurnCenterAgo(120000)`.
   - **Severity:** gameplay-visible
   - **Check:** Offline, retain one old sample and call `HistoryIndexAgo` with `now` beyond the retention period: it still returns that sample. No long live wait is necessary.
   - **Confidence:** high

7. **Dense burns repeatedly allocate and scan for fruit positions before grass dies**
   - **Where:** `src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs:139–146,220–235`; `src/RimMandrake/Pyrelands/Source/Kernel/RM_FireEcoKernel.cs:292–319`
   - **Mechanism:** Every unrolled fire constructs a capturing placement delegate and checks up to nine cells each interval. With no bare destination, nothing records a retry deadline, so the entire operation repeats at camera-dependent intervals of 1–15 ticks. The fruit cap is checked only afterward, so a full cap does not avoid this work. For 1,000 waiting fires, that is up to 9,000 destination probes per interval plus the delegate allocations.
   - **Repro:** On a densely grassed 250×250 map, ignite a broad cohort and profile the period before the plants burn away; compare close and off-screen camera positions.
   - **Severity:** cosmetic/perf
   - **Check:** Sample allocations and time in the placement lambda and `FirstFruitSpot`, recording concurrent unrolled fires and `delta`. This confirms the cost without treating a timing threshold as a Boolean correctness test.
   - **Confidence:** high

No additional findings established for hunt points 2, 3, 6, 8 or 11 from the supplied implementation. Ash-field grid allocation, resizing/removal and black-rain washing remain unassessed: `MapComponent_PyrelandsAshField` was referenced but not supplied.