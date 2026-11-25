# BOUNDARY: the flight probes and the flapping-bird judge (BRIDGE v2.0), Design Version 0.1.0

Code: `src/RimMandrake/Utils/flight_frames.py` (all of it), `flight` and `ProbeTrack` in
`src/RimMandrake/Utils/scene_cond.py`, the `pawn.flight.*`/`pawn.anim.*` reads (`BindFlight`, `SelectedState`) in
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchCondProbes.cs`, and
`src/RimMandrake/bridgetools/scene_flight_takeoff_and_flap.py`.
Item: `RIMMANDRAKE_BUILD_FLIGHT_PROBES_STATE_AND_FRAME_NO_PICTURES`. Design: `../2026-11-23-bridge-v2/05_build_design.md`
§Decision 3, `../2026-11-23-bridge-v2/02_needs_design.md` worked example 3. Tests: `src/RimMandrake/Utils/selftest_flight_frames.py`.

The probes `pawn.flight.state|lerp_tick|height` and `pawn.anim.name|start_tick|graphic|texpath|facing` (one `pawn` arg)
are in both twins of the condition core (`JawaBenchCondCore.cs`, `Utils/conds.py`) and are read in
`JawaBenchCondProbes.cs`: reflection reads of the flight tracker's private `flightState`/`lerpTick`, and the body
node's `TryGetAnimationGraphicState`. No Harmony patch, no write, no picture. `scene_cond.flight(pawn)` records the
eight of them in `s.run` as named probes (`{name, probe}` of `jawa/run_until`). `Utils/flight_frames.py` judges the
series; `bridgetools/scene_flight_takeoff_and_flap.py` is the scene (worked example 3), the owner's act, UNRUN.

## ACCEPTS

 one row per tick per bird, from a kept `scene_trace_v1` or by hand; a kind's prefix, frame count and
ticks per frame from our def XML (`kind_of`; a value inherited through `ParentName` is not followed).

## DOES NOT SURVIVE

 a downed flyer (the keyframe worker shows no frame while downed); a tick of
facing change that also restarts the animation late by more than one tick; vanilla kinds (`kind_of` reads our src
only; pass the kind by hand); what reaches the screen after the selected frame (the owner's eye).

## PROMISES (each one is a test `t_<name>` in `selftest_flight_frames.py`)

- **a-full-flight-passes.** A whole natural flight reads PASS, read through the track names that `scene_cond.flight()`
  records, and the run is SUCCESS.
- **a-skipped-state-fails.** A step that `Pawn_FlightTracker.FlightTick` never makes is `STATE_SKIP`: MOD FAILURE.
- **a-flip-book-that-repeats-one-frame-fails.** One whole loop on one frame is `FROZEN`.
- **a-frame-held-for-the-wrong-number-of-ticks-fails.** A frame other than `GetKeyframeForTick` of the def's ticks per
  frame is `FRAME`. Frame 0 shows 1 tick and the last frame 3*tpf-1 ticks; that pattern is expected.
- **a-landing-that-keeps-a-flying-picture-fails.** A fly picture from the second Grounded tick on is `LANDED_FLYING`.
- **a-bird-still-in-the-air-at-the-limit-is-not-judged.** It is no miss; beside a bird that passed, the run is SUCCESS.
- **no-bird-took-off-is-an-allowed-miss.** RANDOM MISS.
- **the-asset-audit-names-a-missing-texture.** `<prefix><i>_<east|north|south>.png` for every frame (female set too).
