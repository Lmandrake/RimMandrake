# CHILL_VWAKE_WIRING_VERIFY_1 — is V-Wake's pump agitation actually wired?

## what

UNMEASURED, flagged during the Chill assembly sweep (2026-09-27):
`CompVWakeAgitation` exists in `src/RimUtinni/PropaneLakeMechanics/Source/`
and `RUT_VWake` ships with the comp referenced, but whether the ruled
behavior — *"propane-native, agitated by pumping, attacking pawns and pipe on
sight"* (`the_propane_lakes.md` §4) — is live end-to-end is unverified. The
creature also still carries `manhunterOnDamageChance 1.0`, which was the
stand-in before the pipe network existed.

## deliverable

1. Read the comp + `MapComponent_PipeNetworks` and confirm the agitation
   signal actually flows pump → network → comp → aggression (including the
   Mod Settings toggle's default state).
2. If wired: remove or justify the flat `manhunterOnDamageChance` stand-in
   and close.
3. If not wired: finish the wiring (the gap PROPANE_LAKE_PIPE_MECHANICS_1's
   closure implies was done — its prose was corrected 2026-09-27 to say the
   mod is built, but this one edge was never proven).

Offline source-read first; only escalate to a live test if the code read is
genuinely ambiguous.

## provenance

Filed by BENCH from the assembly sweep, caused by
PROPANE_LAKE_PIPE_MECHANICS_1's closure. No owner ruling needed — this
verifies an already-ruled behavior.
