# CHILL_FIRE_BAN_1 — fire is impossible at the bottom of the Chill

## what

Owner physics ruling, typed this session (2026-09-27): *"So there's no oxygen
down in the sea floor so it's not explosive."* Card ruling: **total ban** —
no flame works on the Chill seabed map. Campfires fizzle, chemfuel won't
light, molotovs/incendiaries splash inert, torches die. Heat is electric only
(which forces CHILL_THERMAL_ENGINE_1's power problem).

Fire exists below **only where someone pumps air down** — this is the hook the
war-lab burn routes hang on (CHILL_WARLAB_ROUTES_1): an oxygenated zone is an
ignitable zone.

## the one exception, by ruling

**Fuselight** (the peroxide lamp) carries its own oxidizer — its teeth really
explode (card ruling, twice confirmed). The only fire at the bottom of the
world is a flower. Built under CHILL_FLORA_BUILD_1; this item's ignition
suppression must not suppress Fuselight's detonation.

## deliverable

Map-scoped ignition suppression on the Chill seabed biome (mechanism the
builder's choice — likely a MapComponent/Harmony gate on ignition attempts),
plus the oxygenated-zone override interface the bomb/burn routes will call.
Surface/shore maps unaffected: fire lives above, where the air is, and the
whole existing deflagration/saturation machinery (PropaneLakeMechanics) stays
a surface mechanic.

## provenance

Owner typed the physics; total-ban scope decision taken by question card
2026-09-27. Filed by BENCH out of the Chill concept sitting.
