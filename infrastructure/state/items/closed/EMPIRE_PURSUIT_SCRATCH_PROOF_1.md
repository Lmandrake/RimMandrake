# EMPIRE_PURSUIT_SCRATCH_PROOF_1 — scratch proof of the pursuit scenario part

Filed by FOUNDRY, 2026-08-29, under owner override (verbatim: "I think there's one for
adding a scenario part that we could do now..."). Split out of `EMPIRE_PURSUIT_SCENPART_INSTALL_1`
because that item is BENCH's and belongs to a real sitting with the owner on the campaign
save; this is only the scratch-verification slice its own `verify` section calls for
("a scratch-game live check with a tiny firstRaidDelayHours proves waves actually fire"),
done on a FOUNDRY quicktest map, not the campaign.

## Spec
Install `RuthlessPursuingMechanoids.ScenPart_RuthlessPursuingMechanoids` via
`jawa/scenario_part_add` on a scratch quicktest map, using BENCH's own pre-planned test call
(`infrastructure/state/ledger/events.jsonl`, BENCH note 2026-08-29T07:28:54Z) with
`FirstRaidDelayHours=1` instead of the campaign's `156`, everything else identical to the
ruled campaign values (`pursuitFactionDef=Empire`, `canDoNormalRaid=true`,
`PursuitRaidType=RandomDrop`, etc., `initCalls=PostWorldGenerate;PostMapGenerate`). Prove the
part installs, resolves the correct faction, and its timer actually fires.

## What happened

**Dry run then real `jawa/scenario_part_add`** — all 13 fields applied clean, no refusals,
`PursuitFactionName` resolved to `'Galactic Empire'` (confirms `pursuitFactionDef=Empire`
correctly resolves to the reskinned vanilla faction, not `OuterRim_GalacticEmpire`).
`partCount` 23→24 on the scratch scenario ("Crashlanded").

**Timer math verified EXACTLY.** Read the mod's bundled source directly (workshop
`3621784437/Source/RuthlessPursuingMechanoids/RuthlessPursuingMechanoids.cs`, `Tick()` /
`StartTimers()` / `TimerIntervalTick()`): raid and warning timers round UP to the next
`GenDate.TicksPerHour` (2500-tick) boundary. Hand-computed the target tick from the install
time; stepped the game there (`rimworld/step_game_ticks` — `rimworld/play_for` kept getting
externally re-paused within 33ms every attempt, likely active combat/alerts on this
well-used scratch map; not investigated, stepping worked fine as an alternative).
`jawa/list_letters` confirmed a letter titled **"Galactic Empire Ambush!" arriving at EXACTLY
tick 10000** — the mod source's own special case for "warning timer == raid timer" (`(*Faction=
...)Galactic Empire(/Faction) faction got the drop on you!... a massive force will arrive
imminently"`) — matching the hand-calculated tick to the integer. This proves the scenario
part, its timers, and its faction resolution all work correctly end to end.

**The raid itself did not deliver pawns at that tick** (pawn census unchanged before/after, no
separate raid-arrival letter at tick 10000 — the one "Raid: Galactic Empire" letter present is
leftover from an earlier, unrelated manual `jawa/fire_raid` test on this same scratch map,
`arrivalTick: 4904`). Given `InitialRaidFloor: 2000` puts the actual raid well above the
`maxPawnCostPerTotalPointsCurve` gate found in `EMPIRE_RAID_NEVER_GENERATES_1` (250-cap at
2000pts, Jawa_Empire_Grunt combatPower 101 — comfortably under), this reads as the SAME general
`TryExecute`-silently-returns-false intermittency already documented twice this session
(`AUTHORED_FACTION_RAID_SPAWNS_NOTHING_1`, `EMPIRE_RAID_NEVER_GENERATES_1`), not a defect in
this scenario part or its install. Not chased further on this item — would need several more
156±36h timer cycles to gather a real sample, a lot of stepped ticks for a question this
session already has a documented, accepted answer to.

## Watch out
⚠️ The mod's `Tick()` only runs its body on ticks that are exact multiples of `GenDate
.TicksPerHour` (2500) — `if (Find.TickManager.TicksGame % TickInterval != 0) return;`. A live
check that steps ticks in irregular chunks (as `rimworld/step_game_ticks` does when it times
out and gets re-called) still works because ticks are advanced one at a time underneath, not
skipped — but do the same 2500-tick-boundary math before concluding a timer "didn't fire".
⚠️ `rimworld/play_for` (real wall-clock unpause) got immediately re-paused (33ms, 0 ticks
advanced) every one of 6 attempts on this scratch map — not root-caused. If BENCH hits the
same thing on the campaign save, `rimworld/step_game_ticks` is the working alternative.
⚠️ The scenario part was installed on a DISPOSABLE scratch map (per `map-state-is-disposable-
debug` — this quicktest is never kept). Nothing here touched the campaign save.

## Verify
The install mechanism itself needs no further scratch proof — timer math and faction
resolution are confirmed exact. What's still unverified is whether `FireRaid_NewTemp`'s raid
call reliably delivers pawns over several cycles; that's the same open question
`EMPIRE_RAID_NEVER_GENERATES_1` already owns, not specific to this scenario part.

## criteria
- [x] Part installs cleanly via `jawa/scenario_part_add`, resolves `Empire` correctly.
- [x] Internal timer fires an accurate warning at the exact predicted tick (10000, hand-verified).
- [ ] Raid wave reliably delivers pawns — hit known `TryExecute` intermittency once; not
      resolved here, tracked under `EMPIRE_RAID_NEVER_GENERATES_1`.
