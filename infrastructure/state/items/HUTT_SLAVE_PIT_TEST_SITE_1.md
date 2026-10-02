# HUTT_SLAVE_PIT_TEST_SITE_1 — the Hutt slave pit, at a small stand-alone test site

## spec
Authority: `design/RimMandrake/ship_cargo_hoist_design_2026-10-01.md` §3a and §5 row 3 (RULED). A small stand-alone Hutt site (not Gorga's Palace) with a `RUT_` cast
and a fixed `RM_HoistFrame` over the pit.
- **Sell for silver:** slaves, unenslaved prisoners, and knocked-out beasts, tame or not. The player's own pawns
  walk them to the hoist and lower them. Silver comes up. Price multiplier in Mod Settings.
- **The oubliette:** a sealed map feature holding slaves. Nobody enters it. **Only the ship's hoist can lift them
  out, and only after the site is attacked and taken** (owner, verbatim in the doc §1b).
- **Arena offstage:** hinted at only in pit prices and letters. A visitable arena is a later, separate build.

## criteria
- A peaceful landing, a sale of each of the three cargo kinds, and silver received.
- The oubliette is unreachable while the Hutts hold the site, and liftable by the ship's hoist after conquest.

## Watch out
- This site's **oubliette** is a sealed map feature, not the pit "oubliette fitting" the owner CUT on 2026-09-17
  (`PIT_SUPERDEEP_COLLAPSE_1`). With FlowWorks it is simply an enclosed superdeep (D=4) room with no ladder:
  nobody climbs out by rule (`design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md`).
- Depends on HOIST_SHIP_PART_BUILD_1, HOIST_FIXED_SITE_FRAMES_1 and **GRAVSHIP_PEACEFUL_SETTLEMENT_LANDING_1**
  (owner: *"We need a way for gravship to land properly in settlement and not be seen as attacking."*).
- 🔑 **Animation is optional polish, and it comes LAST.** Ship with a drawn cable line (`GenDraw.DrawLineBetween`) and static sprites; transit is a hidden timer (vanish, wait, appear). Art is the final step and may be skipped. A descent animation is never in scope (owner: *"careful we don't get caught in endless animation development"*).
