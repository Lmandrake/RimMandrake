## spec
✅ **OWNER, 2026-08-22 13:04:** *"Around the gray sea I would like there to be some small
patchy bits of water dotted around as though low-lying regions were still flooded with brine
while it slowly dessicates away, like the Dead Sea."*

⛔ **QUEUED, NOT STARTED** — the owner ruled this comes *"only after we've closed out anything
that affects the next game reload."*

## what he is describing
A **desiccation halo**: the Grey Sea retreats, and what it leaves behind is not dry ground but
a scatter of disconnected brine pans sitting in whatever local depressions were deep enough to
hold the last of the water. **Patchy, small, irregular, and clearly remnants of one larger
body** — not a second sea, and not evenly spaced. The Dead Sea's evaporation ponds and the
Aral Sea's remnant lobes are the reference.

🔑 **Pair it with `MERIDIAN_WATER_HALVED_1`.** The patches ARE the half that was removed,
which is why the two must land together — halving alone leaves a clean shoreline that reads as
a normal sea, and that is the opposite of the story.

## siting rule
Place them in **genuine local minima** near the retreating margin, not scattered at random. A
brine pan sits where water could not drain away. ⚠️ §4 rule 4 says basins shallower than 70 m
are filled and deeper ones are left endorheic — these remnants are the *shallow* case and are
consistent with it.

## the engine constraint
`SurfaceTile.WaterCovered => elevation <= 0f`. **A brine patch must be at or below 0 m to read
as water at all** — a biome or terrain label alone produces a dry tile that merely claims to be
wet. Same rule that forced the Scald to −30 m (`SCALD_WATER_RULING_1`).

## verify
🔑 **By looking.** Render with `worldview.py` and ask the owner's own question — does it read
as a photograph of a real drying sea? Numbers cannot answer this one. Supporting checks: every
patch at or below 0 m; patches disconnected from the main body and from each other; none of
them fed by a river (§4 rule 7 forbids terminator rivers).

## criteria
The Grey Sea's surroundings read as a slowly desiccating brine field, approved by the owner
looking at a render.

## watch out
⚠️ Water is a canon figure — count these into the `MERIDIAN_WATER_HALVED_1` re-measure rather
than updating `canon.yml > planet.water_pct` twice.
