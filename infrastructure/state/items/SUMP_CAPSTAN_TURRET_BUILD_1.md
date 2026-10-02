# SUMP_CAPSTAN_TURRET_BUILD_1

Spec: `design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md` §5 ("the capstan turret"). Owner, typed, turn 1: *"I love the Blackline Capstan. Model it after the Lasso already built in the game (pulls people towards you, weirdly nonphysical since it doesn't move you at all. But if that mechanic is attached to a turret, it makes complete sense and is awesome. Remove lasso's from the game, but keep this)"*.

1. The lasso: Melee Animation (`co.uk.epicguru.meleeanimation`, workshop 2944488802), `1.6/Defs/Lassos.xml`. The pull is job `AM_GrapplePawn`, driver `AM.Grappling.JobDriver_GrapplePawn`, tuned by stats `AM_GrappleRadius`, `AM_GrappleCooldown`, `AM_GrappleSpeed`.
2. A fixed turret (`RM_CapstanTurret`, free tier) that ropes one visible pawn (enemy, animal, or a friendly downed colonist) and reels it toward the turret. Range, reel speed and cooldown use the lasso's numbers set on the building; the lasso mod's mass, body-size and building-fill caps apply. A heavy or struggling target can snap the line and damage the anchor.
3. 🔴 The hook is UNMEASURED: read `JobDriver_GrapplePawn` (RimSage or the decompiled `zAnimationMod.dll`) before writing code. Either a building verb starts that pull with the turret as anchor, or the turret re-implements the pull (a forced move along a cell line) with the same numbers. Melee Animation stays a soft dependency only if the driver is reused; otherwise none.
4. Learned at the Sump: a hidden research row taught by studying two preserved draw-joints from the dig strata (`RUT_DigStratumTable` gains the find); after that it is buildable anywhere. First recipe from local materials (tar-glass bearings, seepwax-packed cable); learned recipe steel, components, cloth.
5. Crewed or powered: FOUNDRY picks the vanilla shape that reads cleanest.
6. Readable signs: a visible line, a rising ratchet sound, a snapped-line mote and message.
7. Mod Settings: on/off, range, reel speed, cooldown, friendly pull, snap chance.

Art: `infrastructure/artpipe/art_lists/sump_bedazzle_cast.csv` (base and top).

## verify
- Quicktest: the turret pulls a raider several cells toward it; a downed colonist can be pulled in; an over-mass target snaps the line with a message.
