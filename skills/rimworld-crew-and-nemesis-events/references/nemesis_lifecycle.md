# Nemesis lifecycle: Rimesis distilled onto OldFriends

Rimesis' full mechanism, numbers and defects are in `design/RimMandrake/event_quest_wisdom.md`
§2.7. This file is the build plan for *our* version: what OldFriends already has, what the
return needs, and the order to build it. Sketches only; re-read every engine method named.

## What `GameComponent_OldFriends` already does (src/RimMandrake/RaidRedesigner/Source/)

- Scribed roster of `OldFriendEntry` (pawn ref, faction at entry, `RoleTag`, encounter list,
  grudge, notability, last seen, dead, `PinnedByUs`, `KinOf`, dead summary).
- One entry point `RecordEncounter(pawn, faction, role, tick, summary, grudgeDelta, notabilityDelta, pin)`,
  fed by Harmony postfixes (fled raider and captain, kidnapped colonist, caravan robbed,
  prisoner escaped, prisoner released / named hunter, a woken-ancient stub).
- Cap (`MaxLivingEntries` 24, a setting), prune lowest notability, release the pins it placed;
  pins with `PassToWorld(pawn, PawnDiscardDecideMode.KeepForever)`.
- A master switch in Mod Settings.

So the "promotion" and "memory" halves exist. Missing: eligibility, return, letter, growth, death.

## The return, in build order

1. **Eligibility** (pure function, offline-testable like `RM_RosterKernel`): entry alive, faction
   hostile to the player, not captured or recruited, `TicksGame >= eligibleReturnTick`, still a
   world pawn, not already spawned. Add `eligibleReturnTick`, `returnCount`, `deathCount`,
   `lastKiller`, `lastWeapon`, `lastLostPart` to `OldFriendEntry` (Scribed, with defaults so old
   saves load).
2. **Selection per raid**: when a RaidEnemy for faction F generates its Combat group, pick at
   most one (two at high notability) eligible entry of F, ordered by `returnCount` then age
   (Rimesis' fairness rotation). Cache the choice for the duration of that raid generation only.
3. **Injection**: postfix `PawnGroupMakerUtility.GeneratePawns(PawnGroupMakerParms, bool)`
   (signature VERIFIED) for `PawnGroupKindDefOf.Combat` when the faction matches; remove the pawn
   from world pawns and yield the same object after the vanilla pawns. Do not raise points; the
   named pawn is the escalation. One owner of this postfix in our whole mod set.
4. **Counter-play instead of stats**: before he arrives, choose one equipment or role change from
   a scan of the colony (turrets → an EMP item; walls → a breach tool; the colonist who wounded
   him → a grudge target via `attackTargets` or a duty). Keep a list; one change per return.
5. **The letter**: append a paragraph to the raid letter (Rimesis patches the RaidEnemy letter
   label/text; a cheaper route is a second letter in the same tick) naming him and reading back
   his last encounter: who, with what, which part.
6. **Death**: on his death, `deathCount++`; return chance first 1.0, second 0.95, then minus a
   small decay per death to a floor (Rimesis: 0.02 per death, floor 0.25) — or simply "a second
   return, then final" for our scale. A final death gets its own letter and stays in the roster
   as history (dead entries are already kept by OldFriends).
7. **Retaliation** (optional, later): when we defeat one of F's settlements, record it; F's next
   raid is "armed" — it brings a named entry if any exists, else a generated leader recorded
   into the roster, and targets the ship. No points multiplier.

## Save and safety checklist

- Every new field Scribed with a default; old saves load.
- Pins re-checked on load (`ForcefullyKeptPawns` / KeepForever) and released on eviction.
- No static plan survives quit-to-menu; reset caches in the component constructor.
- A dead pawn is never moved into world pawns by us.
- A setting turns returns off; another caps returns per raid.
- The offline selftest (`RaidRedesigner/Source/SelfTest`) gets the eligibility and selection
  kernels before any live test.
