# RIMMANDRAKE_FIX_STRANDED_COLONIST_READS_UNTRAPPED_NO_RESCUE — a colonist in a sealed 4 m pit reads untrapped; nobody rescues him

## spec
Found live 2026-11-12 (CLAUDE_ARCHMAGI_FWLIVE, PIT_TEMPERATURE_SOFTENING_1 run 18, flowworks tier, FlowWorks DLL 8286201b).
Evidence: `whittle/pit_temperature_softening_1/evidence/run18_colonist_stranded_in_roofed_pit.json` and
`whittle/pit_temperature_softening_1/evidence/run18_site_20261112T032231.jpg`; the review save
`RM_PitExposure_Review_20261112T032231` (Saves folder) reproduces it on load.

- At noon of an idle quicktest colony, Thib (a colonist, not a prisoner) stood inside a roofed 5x5 pit dug 8 notches (4 m),
  beside the prisoner held there.
- `RM_NorthstarProofs.ProofClimb pawn:<id>`: `held=False trapped=False`, `POCKET k=2 pocket=True size=25 depth=8`.
- Drafted and ordered to a cell 5 north of the pit: moved 0 cells. Left alone for 5 game hours: wanders the 25 cells, then
  sleeps there. Inspect: "Climbs out of steps up to 1 m deep."
- So he is stranded (no move leaves the pocket) while the trap reads false, and the stranded-colonist rescue never queues.

Two questions for whoever takes it (MOD, live): (1) how did he get in? (the run logs prisoners only; wander and the
warden lip jobs are the suspects; the design lets a pawn walk in "that is how you fall in", but an idle colonist should not
choose to); (2) `TrappedIn` for an own-faction pawn when `superdeepCapturesOwnFaction` is off: not "held" must not mean
"not stranded" when the pocket has no climbable exit.

## verify
Load the review save; ProofClimb on the stranded colonist reads trapped (or he is rescued / climbs out within a game day);
a fresh idle colony beside an open and a roofed 4 m pit keeps every colonist out of both over a day.
