## spec
found-by: CLAUDE_ARCHMAGI_FWLIVE, live, 2026-11-11 (PIT_TEMPERATURE_SOFTENING_1 proof run, `whittle/pit_temperature_softening_1/evidence/run8_rain_flooded_pit_A_20261111T233048.json`).

MEASURED: on a dev quicktest map (AridShrubland, flowworks tier, defaults: `rainFillsExcavationsEnabled` on,
`rainFillPerPulse` 0.1), a 5x5 open pit dug 8 notches (4 m) filled to the brim with rain in one night: rain began about
03:00, and the climb depth under the prisoner read 8 at 07:00, 5 at 08:00, 4 at 09:00 and 3 at 10:00; at 15:00 the pit
read `depthRaw 8, fillRaw 8` (terrain WaterDeep). Its roofed twin beside it stayed dry (fill 0). The prisoner in it
swam out at about 10:30 (owner R12: water 2 m or deeper is swimmable to its lip) and left the map by 14:00.

That is roughly half a metre of water an hour from rain falling on the pit alone. Real heavy rain is about 10-50 mm an
hour, so a 4 m pit should take days of storm to brim, not a night. Consequence in play: an open pit prison empties
itself in any overnight rain.

Question to answer: is `rainFillPerPulse` 0.1 (one notch per ~10 pulses at rain rate 1) the intended speed, or should a
pit catch only the rain that falls on it (plus run-off from the lip, if that is modelled)? A number change is a Mod
Setting default (owner rule: defaults = shipped behaviour); the realism case is above.

Related, not the same: `PIT_RAIN_FIX_FRACTIONAL_HEADROOM_FULL` (fractional headroom), `EXCAVATION_RAIN_TAME_ONE_TICK_DELUGE`
(the per-pulse slice).
