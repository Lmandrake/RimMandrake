<!-- status: live -->
# Coastal Mesa — LLM-authored map improvement

**Approach:** every design decision below was made by reasoning, not by an
algorithm. There is no heuristic edit-engine choosing what changes or where.
The renderer (`author_coastal_mesa.py`) is only a pen — it draws exactly the
regions, coastlines, and set-pieces specified by hand, as vector shapes on a
smooth surface, so the result reads as a designed map instead of a pixel grid.

## The base map (BEFORE)
A blank starter: a straight-edged ocean band on the west, one featureless
sand flat, a plain rock massif in the NE, and a bare gravel patch in the SE.
Nothing to fight over, nothing to explore, no reason this tile exists.

## Region decomposition and judgment
| Region | Problem in the base | What I changed |
|---|---|---|
| Ocean (W) | Ruler-straight coast, single flat blue | Meandering coastline — headland (N), deep cove (mid), gentle point (S); depth-graded water deep→shallow; wet-sand beach ribbon; an offshore sandbar in the cove |
| Sand flat (center) | Empty, tactically dead | A dry wash (arroyo) snakes SW→NE giving a line of movement + soft chokepoints; scrub stands cluster along it; an outcrop knoll gives mid-map high ground; a fertile hollow at a wash bend is the farm start |
| Rock massif (NE) | Solid blob, no interior | Modelled with light/shadow; a cavern chamber carved into the SE face with a mouth toward the flat; a talus/scree apron softens the west foot |
| Gravel flat (SE) | Bare | Hosts the refinery set-piece |

## Hand-placed exotic set-pieces (the campaign flavor)
1. **Crashed Factory-ship** — a scorched impact furrow gouged NW→SE, tapering
   and charring toward a broken hull fragment; debris scattered around it.
   (The ship your Jawa inherited — the theme's origin, written into the terrain.)
2. **Abandoned mine** — a timber-framed adit on the massif's west flank with a
   gravel tailings fan spilling downslope.
3. **Semi-working refinery** — an ancient-concrete pad with two intact tanks, one
   ruptured (rust gash + spill stain), connecting pipes, and a small derrick.
4. **Dead droid in an impact crater** — a rimmed crater with a scorch streak and
   a toppled droid, dead red optic, one splayed limb.
5. **Cavern** — an enclosed dark chamber inside the massif with a throat opening
   onto the sand (ancient danger / infestation seed, not free real estate).

## Why this is "improved," by the four axes
- **Realism** — coastlines meander, water grades with depth, washes connect high
  to low ground, tailings fall downhill, the massif is lit consistently.
- **Interest** — five distinct landmarks and a reason to move through the map.
- **Tactical** — the wash is a channel and chokepoint; the knoll and massif are
  high ground; the cove and headland shape any seaborne approach; the refinery
  pad is a defensible strongpoint.
- **Artificiality (lower = better)** — nothing is grid-locked or stamped on open
  ground; every feature sits where terrain logic would put it.

## Design decisions I'd flag
- The refinery is drawn schematically (tanks/pipes/derrick) so it reads at a
  glance; in-game these map to real Rimefeller/derelict-structure props.
- Placement here is illustrative geometry on a semantic map — it demonstrates
  the *design reasoning*. Translating to an actual save still needs the terrain
  names/props resolved against the live mod list (the shortHash issue), which
  is deliberately out of scope for this authoring exercise.
