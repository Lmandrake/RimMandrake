# RIMMANDRAKE_REBUILD_SWALE_AS_SOAKING_FLOOR_NOT_FURNITURE

## spec

Owner, live look 2026-11-14 about 11:30 AM to 12:10 PM PST (finding 4, `D:\ClaudeWork\rimmandrake\conductor\sitting_20261114\OWNER_LOOK_WORDS.md`):

> "The Swale should be a floor-tile type that encourages rapid water absorption and transforms nearby terrain to fertile soil, not a weird metal slide-looking piece of furniture."

Today `RM_Swale` is a `Building` ThingDef in `src/RimMandrake/FlowWorks/Defs/Canals/ThingDefs/FlowWorks_ThingDefs.xml` (about line 226), with texPath `Things/Building/FlowWorks/Canals/RM_Swale`. Its description already promises the behaviour: it seeps water and turns sand to soil to rich soil within a couple of paces.

The work:
- Rebuild it as a constructible floor (TerrainDef).
- Move its soak and improve behaviour onto the terrain.
- Give it flat floor-tile art.
- Fix every inbound reference to the old ThingDef: research, recipes, Cracked Lands and save migration. Wrong material is deleted, not superseded.

Related items:
- `RIMMANDRAKE_REPAINT_SWALE_AS_FLOOR_TILE` (art only, filed 2026-11-13). Its art becomes this item's floor texture.
- `SWALE_CANAL_ART_REFERENCE_1` and `CRACKEDLANDS_SWALE_CAMPAIGN_LOCK_1` (both blocked).

Design Version class: PROPOSED Convergent-Problem (current FlowWorks 0.1.0). This is an owner call.

Build effort: medium.

Acceptance test (offline, a local model could run it):
- An XML check finds `RM_Swale` as a TerrainDef with a designation category and no Building ThingDef of that name.
- Nothing in the repo references the old ThingDef.
- A FlowWorks selftest asserts that a swale cell soaks water faster than plain soil and upgrades an adjacent sand cell toward soil.
