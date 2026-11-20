# RIMMANDRAKE_RESUME_WALK_SORT_WITH_PART_TWO_THEN_CARD

## What the card said

<!-- answered 2026-11-20T15:08:05Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** FlowWorks is at Design Version 0.1.0 and has not passed yet. On your walk today you asked for a full design pass on water: colour, transparency and waves as a function of depth. History: on 11-12 you said water was too opaque; a fix made it darker and half as opaque; on 11-13 you said it looked great; today shallow water barely reads. That is three reversals with no written target to tune toward. A 'mockup' here means flat pictures made outside the game, one per depth, for you to pick from before any code changes. Effort figures are my guesses; the code read is still running. (Hard to read? Type STE, Binding or Both for a rewrite.) Where does the water design work belong?
**Picked:** Colour and clarity now (Recommended)
**Its description:** Why: shallow water you cannot see is a defect a player would reject, so it belongs in 0.1.0. Buys: mockups per depth, you pick, that becomes the written target, then one build. Waves wait for 0.2.0. Costs: one more look from you, about 1 to 2 helper runs. Recommended: it ends the reversals without holding 0.1.0 for waves.
**His words:** (1) and it needs to be on representative terrain (put some different textures on the ground as well as furniture, bodies, etc).
**Other options:** Full pass now, waves too · Small fix now, design later · Wait for the code read

**Question:** Second question. You dug a pit with a step in its floor: two rows 3.5 m deep beside one row 5 m deep. Movement obeys the step, but the floor draws as one flat dark area. Your words: "Clearly you have not implemented the pit visuals as relative terrain representation... That won't do. Need more generalization." 'Relative terrain' means the wall and shading art is drawn wherever two neighbouring squares differ in height, not only where a pit meets the surface. I guess, at about 50%, that the same change would also fix the pit walls showing through the cover at station 47. Effort is unread; the helper is reading the draw code now. Where does drawing pits as relative terrain belong?
**Picked:** In 0.1.0, full rebuild (Recommended)
**Its description:** Why: you said "That won't do", and stepped digs are ordinary play. Buys: inner walls and shading at every height change. Costs: a rewrite of pit drawing; my guess is 2 to 4 runs, geometry solved offline first, then one look from you. 0.1.0 waits on it. Recommended: by your rule a defect a player would reject stays in the current version.
**Other options:** Cheap cue now, rebuild later · Next version entirely · Wait for the code read
