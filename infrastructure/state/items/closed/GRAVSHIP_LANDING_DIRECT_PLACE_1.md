# GRAVSHIP_LANDING_DIRECT_PLACE_1 — land a gravship without the cutscene machinery

From GRAVSHIP_LAUNCH_TRAVEL_1's live proof: `marker.BeginLanding` enters vanilla's landing
chain (skybox/terrain/gravship GPU captures + camera-pan callbacks + long events) and that
chain WEDGED under automation before `PlaceGravship` ran — cutscene stuck forever, marker
consumed, ship unrecoverable except by save reload. Window focus did not help.

## spec
A companion route that lands WITHOUT the render chain: reproduce the "PreparingForLanding"
long-event body (`PlaceGravship(gravship, landingPos, map)` + mask regeneration + the
LandingEnded state cleanup) directly, or find vanilla's own cutscene-off path (what does
`Prefs.GravshipCutscenes=false` actually skip? read the WorldComponentUpdate tail past line
430) and drive that. jawa/gravship_land then gains `skipCutscene=true` defaulting true.

## verify
Scratch map: launch, arrive, land via the new route; engine + furniture + pawns all present
on the new map; no reload needed.

## BUILT 2026-08-28 (BENCH), same session it was filed
`jawa/gravship_land` gained `skipCutscene` (DEFAULT TRUE): reproduces PlaceGravship
(6 public calls) + LandingEnded's state tail (negative-outcome roll, Current.Game.Gravship
cleared, Scenario.PostGravshipLanded, mask layers regenerated) with two reflection touches
(controller.landingMarker field, GravshipPlacementUtility.PostSwapMap internal). Deviation
from vanilla, documented in the tool description: game left PAUSED, not forced to Normal.
Compiled clean; surface still 244; awaits the next down-window deploy, then the scratch
launch+land run in prove_gravship.py (which needs its authoring preamble revisited per
THRUSTER_INSTABUILD_NEVER_ACTIVE_1 — or a campaign-save flight like tonight's).

## criteria
- [x] Deployed; a full launch -> arrive -> land completes with no reload and the engine +
      pawns verified on the new map.

## PROVEN LIVE 2026-08-29 (BENCH), scratch quicktest, 582-mod list
Full cycle with no reload: authored ship (pad + engine + console + tank + thruster +
astrofuel pipes), 3/3 colonists walked aboard, dryRun moved nothing, launch -> takeoff
cutscene -> travel -> landingConfirmationPending -> `jawa/gravship_land` (skipCutscene
default) placed the ship SYNCHRONOUSLY at (81,92) on the new map: tile == target
(111827), all four parts + 12 pipes + 3 colonists verified present. The vanilla wedge
never engaged. Getting the ship FLYABLE surfaced three stacked authoring traps, closed
into THRUSTER_INSTABUILD_NEVER_ACTIVE_1 and baked into prove_gravship.py.

## DEPLOYED 2026-08-28 (BENCH), game-down window
`build.py --gm --apply` clean. Two guard notes from the deploy:
- The gate guard was refusing EVERY default build on a false positive — other
  tools' Description strings mention "jawa/fire_incident". Fixed with exact
  length-prefixed matching, calibrated both directions (gm build -> 1 hit,
  default -> 0). The guard still refuses a real leak.
- Deployed --gm to keep the existing live surface (the game copy already
  carried the GM pair; EMPIRE_RAID_QUICKTEST_1 needs jawa/fire_incident).
Remaining: the live launch -> arrive -> land proof (needs game-up + bridge),
via prove_gravship.py (menu-guard + gizmo-fuel revisions committed 24b15280).
