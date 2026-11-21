# RIMMANDRAKE_MOCK_FLOWWORKS_WATER_BY_DEPTH_ON_REAL_GROUND

## What the card said

<!-- answered 2026-11-20T15:08:05Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** FlowWorks is at Design Version 0.1.0 and has not passed yet. On your walk today you asked for a full design pass on water: colour, transparency and waves as a function of depth. History: on 11-12 you said water was too opaque; a fix made it darker and half as opaque; on 11-13 you said it looked great; today shallow water barely reads. That is three reversals with no written target to tune toward. A 'mockup' here means flat pictures made outside the game, one per depth, for you to pick from before any code changes. Effort figures are my guesses; the code read is still running. (Hard to read? Type STE, Binding or Both for a rewrite.) Where does the water design work belong?
**Picked:** Colour and clarity now (Recommended)
**Its description:** Why: shallow water you cannot see is a defect a player would reject, so it belongs in 0.1.0. Buys: mockups per depth, you pick, that becomes the written target, then one build. Waves wait for 0.2.0. Costs: one more look from you, about 1 to 2 helper runs. Recommended: it ends the reversals without holding 0.1.0 for waves.
**His words:** (1) and it needs to be on representative terrain (put some different textures on the ground as well as furniture, bodies, etc).
**Other options:** Full pass now, waves too · Small fix now, design later · Wait for the code read

## spec

FlowWorks Design Version 0.1.0, Convergent (his card 2026-11-20, above). Replaces RIMMANDRAKE_TUNE_WATER_CLARITY_DARKER_AND_HALF_AS_OPAQUE,
which asked for half the opacity; he now asks for the opposite at shallow depth. Source: `design/RimMandrake/validation_holding/flowworks_walk_20261120.md` #2, #7, #10.

**Nothing changed since his 11-13 approval** [measured]: the law (`RM_UnderLiquid.Seen`, `src/RimMandrake/FlowWorks/Source/Superdeep/RM_UnderLiquid.cs:173`;
deep opacity 0.90 at 4 m, curve power 1.4, fresh water seeThrough 0.45) is commit 9a5bbf7a66 (11-12 21:22), inside the build he
approved on 11-13; his settings file holds no under-liquid key. It hides 6% at 0.2 m, 15% at 0.5 m, 30% at 1 m, 56% at 2 m, 90% at 5 m.
**What the 11-13 look showed him** [measured, `D:\ClaudeWork\rimmandrake\conductor\afk_20261112_night\live\REVIEW_ME.md` lines 10-12]:
the big-pit series BP0 dry, BP1 0.5 m, BP2 1 m, BP3 2 m, BP4 3 m, BP5 4 m (brim), BP6 1.5 m tar, on the save
`UNDER_LIQUID_LAW_AFK_20261112c`. The same page (line 64) reports a spill that raised BP0 to BP4 by 1 m each during that night's run;
whether the 0.5 m pit still held 0.5 m when he looked is not recorded [unknown]. Three reversals so far (11-12 too opaque, 11-13 great,
11-20 too transparent) with no written target: this item makes one.

His write-in: the mockups must be on representative terrain: different ground textures, furniture, bodies and the like.

## verify

Offline mockup sheets (no game): water at 0.2, 0.5, 1, 1.5, 2, 5 m and deeper over several ground textures (sand, soil, stone, the pit floor), with furniture, a body, a pawn, a ladder and pit walls under it; several candidate colour and opacity curves side by side, true scale. A judge that did not make them reads them first. He picks; the pick is written down as the target (curve and colour per depth); then one build to it.

## criteria

Acceptance test: none, his pick of a look. Once picked: a selftest that `RM_UnderLiquid.Seen` and the body colour at each listed depth equal the written target (and `model/underliquid.py` stays equal to it).
