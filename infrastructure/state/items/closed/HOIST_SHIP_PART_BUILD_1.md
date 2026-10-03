# HOIST_SHIP_PART_BUILD_1 — the keel hoist as a gravship part

## spec
Authority: `design/RimMandrake/ship_cargo_hoist_design_2026-10-01.md` §2 and §5 row 1 (RULED 2026-10-01). Build the ship form, `RM_KeelHoist : MapPortal`, with
`RM_CompKeelHoist` in a new free-tier mod `mandrake.rm.keelhoist`.
- Only buildable in a structure carrying a GravEngine. Copy `PlaceWorker_NeedsGravEngine` in; do not reference
  DivingInteraction, which is being retired (`SEA_DIVE_HATCH_RETIRE_1`).
- Targets: any `MapPortal` within range (map-to-map, cradle cell below for up-loads), and an unwalkable cell on
  the same map. One pairing per hoist.
- Moves items, awake colonists, slaves, prisoners, tame animals, downed colonists, and **downed strangers and wild
  animals, who arrive captured**. Use a hoist-scoped dialog or postfix; never patch the shared `AllSendablePawns`.
- Tether lock: a Harmony postfix on `Building_GravEngine.CanLaunch` refuses launch while a cable is down.
- Manifest (inspect tab) and an Open Line counter stub with a readout. Research row and Mod Settings per §2e.
- First test: drop the cable down `RM_LanternDeepMineshaft`.

## criteria
- Items and a downed wild animal go down and come up. The animal arrives captured, and the manifest records both.
- Launch is refused while the cable is deployed, and allowed once it is reeled in.
- All Mod Settings toggles degrade gracefully when off.

## Watch out
- 🔑 **Animation is optional polish, and it comes LAST.** Ship with a drawn cable line (`GenDraw.DrawLineBetween`) and static sprites; transit is a hidden timer (vanish, wait, appear). Art is the final step and may be skipped. A descent animation is never in scope (owner: *"careful we don't get caught in endless animation development"*).
- The sea hatch is not a model or a target. The seas are the ship's `RM_SeabedLayer`.
