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
