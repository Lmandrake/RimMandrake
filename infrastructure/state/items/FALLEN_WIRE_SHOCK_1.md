# FALLEN_WIRE_SHOCK_1 — live fallen wires shock and light spilled fuel (GS-2 + X-7)

Decision taken by question card 2026-10-08. The owner typed on the card: "doesn't have to be instantly
lethal. Death should be rare, instead it knocks people out and throws them back a little (more realistic).
Only people with weak heart conditions or existing heart damage get taken out."

## what was built
GimmeSomeSlack, `Source/Aerial/RM_FallenWireShock.cs`, driven from `RM_MapComponent_Aerial.MapComponentTick`.
- Contact cells: every cell a live fallen strand (`FallenLiveCached`) lies across, except the anchor's own cell,
  rebuilt on the existing 250-tick sweep. Pawns on them are checked every 20 ticks.
- Any flesh pawn, colonists included, is thrown back up to `fallenWireKnockback` cells (default 2) away from the
  live end and gets `RM_FallenWireShock`: Consciousness capped at 0.1, so vanilla downs it. It is dazed below
  severity 0.3 and the hediff is gone after about 2 in-game hours. A pawn already knocked out is not re-shocked.
- A weak heart is killed instead. That means vanilla `HeartArteryBlockage`, an ongoing `HeartAttack`, or a natural
  heart below full part health (an artificial heart does not count). The pawn gets vanilla `HeartAttack` at
  severity 1, so the death reads as a heart attack.
- Fire (X-7): each sweep, a live end has a 35% chance to light what it lies in. That is vanilla `Filth_Fuel`
  through `FireUtility.TryStartFireIn`, or a FlowWorks burnable liquid through a reflection lookup of
  `RM_MapComponent_Excavation.LiquidFire.IgniteNow(Map, ex, IntVec3)`. Without FlowWorks that half is off. A
  missing member logs one warning, never an error.
- Mod Settings (Aerial tab): shock on/off, knockback 0-3 cells, ignite on/off. All numbers are PROVISIONAL.

## criteria
- O1 L0: GimmeSomeSlack builds; validate_patch is clean on its Defs; selftests show no new failure
- A1 L1: RM_FallenWireShock HediffDef loads, and a pawn given it is downed
- A2 L2: live, a colonist walked onto a live fallen wire is moved 1-2 cells away from the end and downed, and wakes within about 2 in-game hours
- A3 L2: live, a pawn with HeartArteryBlockage that touches a live fallen wire dies of a heart attack
- A4 L2: live, a dead (unpowered) fallen wire does nothing to a pawn standing on it
- A5 L2: live, a live end lying in a chemfuel puddle starts a fire within a few sweeps; with FlowWorks, one lying in canal oil lights the oil
- H1 L4: the owner judges the knockback, knock-out length and ignition chance in a sitting (PROVISIONAL until then)

## verify

Run each criterion at its stated level and record it with `rimflow verify FALLEN_WIRE_SHOCK_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- L0: offline build, selftest/fuzz/lint (already run at implementation).
- L1: one minimal-list load, read Player.log for config/cross-reference errors and the specific line, or one spawn-and-read bridge probe.
- L2: one quicktest map via the bridge or modcheck: set up the scenario in the criterion, step ticks, read the state named.
- L4: owner judgement in a sitting; not a FOUNDRY acceptance task.
Evidence is the Player.log line or bridge read the criterion names; a screenshot is not evidence of state.
