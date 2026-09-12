# MOD_VALIDATION_PIT_PILOT_1 — the pit mod proves modcheck end-to-end

Blocked on MOD_VALIDATION_RUNNER_1 shipping. Spec:
`design/RimMandrake/mod_validation_runner_spec.md`.

## spec
Write the pit mod's `validation.steps.yaml`: one component per settings toggle
(the floor) plus beyond-toggle components for everything the mod defines —
falls-in on walk-over, climb-out succeeds for a pawn that can, climb-out fails
for one that cannot, and the rest of its functionality hit once each. Run it
green on the minimal list; put the HTML sheet in front of the owner ONCE to
ratify the report format before the retrofit wave adopts it.

## verify
- `rimflow verify` event N/N green recorded; sheet path handed to the owner
  with a full native path.
- The steps file exercises every settings toggle (runner floor check passes).
