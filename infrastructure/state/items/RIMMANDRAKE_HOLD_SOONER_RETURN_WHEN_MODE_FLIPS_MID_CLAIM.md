## spec
Found by the Graffiti 0.1.0 blind challenge, cycle 2 (RIMMANDRAKE_JUDGE_GRAFFITI_BLIND_CYCLE_TWO_TESTS_FIRST), 2026-11-17. Class: **Polish**, bar `raider_pressure`.

**Criterion:** sooner mode: the faction's next raid comes sooner, by the setting's delay

**Evidence:**
- RaiderPressure.Refresh: an entry made in Larger mode keeps returnTick -1; switching to Sooner then sets returnTick = since + ret, so a claim older than 15/push days fires its return raid on the next refresh (250 ticks), not ret after the switch [read, not run: game-side]

**Smallest fix:** returnTick = Math.Max(since + ret, now + some floor) when the entry first enters Sooner, or count from now

Record: `design/concepts/Graffiti/version/blind_challenge/cycle_2/lane2/faults.json`.

## criteria
a mode switch mid-claim schedules the return no earlier than the switch plus ret (or keeps since + ret only when that is still ahead)

## verify
Acceptance test: none offline, game-side (RaiderPressure.Refresh is Verse); the live check is sc_raider_pressure with the mode flipped to sooner after the claim's 15/push days, reading returnIn > 0.
