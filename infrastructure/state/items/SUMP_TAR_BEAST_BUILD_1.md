# SUMP_TAR_BEAST_BUILD_1

Spec: `design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md` §3 ("the tar beast, the full station-eater"). Ruled by the owner, turn 1, by card. Sheet `the_sump.md` §4 and ban 2 (never a fightable spawn).

1. `RM_TarBeast` (free tier), label "tar beast", about bs 9, static art at a huge draw size on an ordinary footprint, three facings, no new rig. Replaces the Thrumbo placeholder in `RUT_BeastBulge`'s `CompProperties_PawnSpawnOnWakeup`.
2. Behaviour when woken: very slow (about a tenth of a pawn's walk) toward the densest cluster of buildings; every cell crossed becomes shallow tar (the tar coating); a building reached is swallowed (destroyed, a tar mound left, a letter naming it); pawns in the way are shoved aside (stagger, no bite); very high health and armour; after a set time or a building count it sinks into the deepest tar and becomes a bulge again elsewhere.
3. Wake causes: the built two (damage, construction within 20 cells) plus a deep dig at a dig shaft and pumping (derrick or deep drill) within range.
4. Readable signs: the bulge; mouse-lines bending (`RM_MapComponent_DreadField`); a room-sized bubble sound and a slow ring of filth a day before a wake; the tar trail and swallowed-building mounds after. Nothing vanishes.
5. Mod Settings: on/off, wake sensitivity, speed, buildings taken before sinking.
6. Lift the `DEPLOY_HOLD` on the bulge set once art lands. Art: `infrastructure/artpipe/art_lists/sump_bedazzle_cast.csv`.

## verify
- Quicktest: a bulge woken by a nearby explosion emerges a tar beast that crawls to buildings, swallows one with a mound and a letter, lays tar, and later sinks back to a bulge.
