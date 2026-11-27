Pawn_FlightTracker.StartFlying() leaves flightState TakingOff (raw 2), not Flying (1); FlightTick moves it to Flying 50 ticks later. A check that reads raw state == Flying misses every pawn that the engine just launched; Pawn.Flying (state != Grounded) counts TakingOff and Landing too.
item: RIMMANDRAKE_PROVE_FLIGHT_MAINTAIN_HOLDS_ONLY_STARTED_PAWNS
home: skills/rimworld-modding/references/flight.md
