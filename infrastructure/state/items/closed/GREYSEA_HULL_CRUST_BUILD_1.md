Split from `GREYSEA_RULED_CONTENT_1` (rulings 6-7, Q10/Q11). Design: `design/Jawa/worldbuilding/biomes/the_grey_deep_danger_floor_pass_2026-09-27.md` §1.

## spec
- Clock on the Grey map only (`RM_MapComponent_GreyHullCrust`), hourly, while a grav engine with substructure sits on `RM_GreySea`. Pace = setting rate x salt snow (`RM_GreySaltSnow`, default 2x) x brine berth (brine channel / chimney seep / salt chimney within 5 cells of the hull, default 1.5x). Nothing purchasable modifies it (no heat, no fuel).
- Ladder (Q10 a): rime filth from 1 day; first exterior hull door salted at 2.5 days, one more per effective day; crust things (`RM_HullSaltCrust`, passable, non-edifice) ramp in from day 5 to every hour by day 15, capped at a third of the hull cells.
- Salted door: `PawnCanOpen` false for everyone; game-wide id set so it travels with the ship; first one sends a once-per-game teaching letter; BasicWorker chip job (240 ticks, no tools) from either side, so a pawn inside can always get out.
- Crust: Mining chip job (420 ticks) for 4 `RM_RawSalt`; door pays 2. Every chip rewinds the clock 0.25 day (no ratchet).
- Launch gate: second `CanLaunch` postfix counts crust on valid substructure; only downgrades an Accepted report (never strands).
- Mod Settings: on/off, pace, salt-snow and berth multipliers. Off removes every constraint.

## verify
- Live: `jawa/static_call RimMandrake.TerminalBiomes.RM_GreyHullCrustProof.ProofAdvance 16` on a Grey map with a parked gravship reports rime >= 1, saltedDoors >= 1 (if it has an exterior door), crust >= 1, gate not accepted; chipping all crust lets `ProofState` report gate=accepted. Chain `grey_hull_crust`.
