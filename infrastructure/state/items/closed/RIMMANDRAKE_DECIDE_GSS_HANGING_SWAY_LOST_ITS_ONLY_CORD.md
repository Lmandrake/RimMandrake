## spec
RIMMANDRAKE_FIX_SLACK_CORD_ENDS_OWNER_CAUGHT_TWO (owner 2026-11-16: *"both a hanging out sparking end as well as the wire plugging into the same point on the wall. That's not ok"*) removed the wire that hung out of a wall terminal's hole. That wire was the ONLY `Lifted` strand GSS draws, so the settings "Hanging cords sway in the wind" (`sway`) and the CPU/shader radio (`swayMode`) now move nothing, and live rows B7_sway_cpu_two_frame / B7b_sway_shader_path read UNMEASURED (B12 already did when nothing is lifted). `swayAmplitude` still scales the floor ripple. The downed-wire drip (`downedWire`) still runs: it rides the wall end's single loose end.
Every mod ships superb Mod Settings (CLAUDE.md): a toggle that does nothing is a defect. Decide: retire `sway`/`swayMode` (and their rows), or give sway a subject that does not put two ends at one point.

## verify
Acceptance test: none, a design decision (Designer, then the build it picks gets its own test).

## criteria
No GSS setting is shown that changes nothing on any map.
