# Broadening (2026-11-11 22:30 -08:00, GPT via gpt_consult.py --codex wsl, model gpt-6.1-sol)

## Question

> RimWorld 1.6 mod (Odyssey DLC present). On an airless underwater "Chill seabed" map, fire is banned unless a cell is oxygenated. Odyssey's OxygenPump (wall-attached, Placeworker_AttachedToWall, standable non-edifice in the cell in front of the wall, flickable, breakdownable, CompLowPowerInSpace) gets our comp RM_CompChillAirSupply: on that map only, while powered/on/not broken it marks every cell of its room oxygenated if the room is sealed (!TouchesMapEdge, !UsesOutdoorTemperature, !IsDoorway) and room.CellCount <= 60 * live pumps in the room; it draws 300 W, overriding vanilla's 10% low-power mode. Per-provider ledger with per-cell counts so two pumps keep the room lit until both stop. Settings: toggle, watts, cells per pump.
> Statement to make true: A2 a fuelled stove in a sealed roofed room with a powered pump lights; switched off it goes dark. A3 two pumps: one off keeps it lit, both off ends it. A4 a pump in an unroofed or edge-touching room oxygenates nothing and says so in its inspect line. Plus: research-gated (OrbitalTech), settings toggle.
> Tested so far: offline build, seeded fuzz of the ledger vs a reference model (3000 cases), RoomServed boundary units, patch matches 1 def. Old live run (a month ago) passed A2-A4 with pumps spawned mid-room and power forced on by a dev call. Today I fixed: vanilla "Power mode: Low" line contradicting 300 W; immediate room-wide refresh on FlickedOff/Breakdown/PowerTurnedOff signals; refresh at load end (ledger is not saved).
> Question: what would a real player (new, experienced, adversarial, messy real base) try that this testing misses? List the 6 most revealing concrete cases, most likely-to-break first, each with what to observe. Be terse.

(file attached: `src/RimMandrake/DivingInteraction/Source/RM_CompChillAirSupply.cs`)

## Answer (verbatim)

1. **Build it normally.** Start before OrbitalTech; research, construct against walls in each orientation, wire normally, then cook. Observe research gating, which side receives air, and whether the stove actually works without forced power.

2. **Change a running room.** Remove one roof tile, then all roofing; breach toward the map edge; merge and partition rooms. Observe stove behavior throughout, oxygen lingering in former room cells, and whether “not sealed” matches the resulting room.

3. **Remove pooled capacity.** Put two pumps in a 61-cell room. Flick one off, restore it, break it, then deconstruct or uninstall it. Each loss must stop service from the remaining pump. Compare with a 60-cell room, where one survivor should suffice; watch for service lingering until a rare tick.

4. **Run on marginal real power.** Use a grid that supports the vanilla low draw but cannot sustain 300 W; exhaust batteries, cut cables, then restore supply. Observe actual grid consumption, unexpected power cycling, immediate loss of air, and recovery—not just inspect text.

5. **Reload before anything ticks.** Save paused with a working room and reload; repeat with an off pump, broken pump, and insufficient pooled capacity. Observe correct oxygen immediately after loading, including no brief service from inactive pumps.

6. **Change settings during operation.** Toggle the feature and master setting; change watts and capacity across the current room’s threshold. Observe existing pumps and stoves updating, old oxygen disappearing, and actual consumption matching the new setting. Re-enable without rebuilding.

## What I did with it (offline lane: no game, so by reading vanilla source via RimSage and our code)

- **Case 3 (remove pooled capacity) was a real defect, fixed.** Deconstructing, uninstalling or destroying one of two
  pumps in a 61-cell room cleared only the removed pump; the survivor went on serving a room it cannot fill until its
  own next rare tick (up to 250 ticks). `PostDeSpawn` now makes every pump left in the room re-count. Flick-off,
  restore, breakdown and power loss were already fixed this round the same way (`ReceiveCompSignal` on
  `FlickedOff`/`FlickedOn`/`Breakdown`/`PowerTurnedOff`/`PowerTurnedOn`, signal names read from vanilla
  `CompFlickable`, `CompBreakdownable`, `CompPowerTrader`).
- **Case 4 (marginal power), read, no defect.** `CompPowerTrader.Off` is true whenever the net has cut the pump; both
  vanilla `CompLowPowerInSpace` and our comp only set the draw while not Off, so a cut pump keeps asking 300 W and the
  net brings it back only when 300 W is there: no 15 W/300 W cycling. The inspect line now agrees (Power mode: High).
- **Case 5 (reload paused), fixed earlier this round.** The ledger is not saved; each pump now refreshes in
  `LongEventHandler.ExecuteWhenFinished` after a load, from saved `powerOn`/switch/breakdown state, so an off or broken
  pump never serves and a working room is lit before the first tick.
- **Case 1 (which side receives air), read, matches vanilla.** The pump is a standable attachment in the cell in front
  of its wall; vanilla `CompOxygenPusher` and our comp both use `parent.GetRoom()`, so a pump hung on the outside face
  of a wall serves the outside (and says "Not a sealed room"). Research gate is Odyssey's own `OrbitalTech`.
- **Cases 2 and 6 (room edits, settings changes mid-run): not fixed, by choice.** They take effect on the pump's next
  rare tick (about 4 s of game time), the same cadence vanilla uses for room temperature and oxygen. Not seen live.
- **Not checked at all:** every case on a live map. This lane may not run the game; A1-A4 owe a live re-proof at the
  new sha (see BLOCKED.md).
