# The Forge's new slow-ground creature: three concepts, 2026-10-20

`FORGE_SNAILHOLE_FILL_EMPTY_SHELL_LEFT_BEHIND`: LavaSnail (Odyssey) was cut from RM_/RUT_TheForge
(03ac7f26a), which left the slow small-grazer slot empty. The owner's order: *"Create something truly
alien and interesting based on the Forge description. Be impressive. Offer three options and ask us what
it might be, then do it."* He picks first. No defs are built until he does.

Rooted in the BiomeDef description (the towers streaming vent-steam like banners, red seams and flows, ash
skirts, *"mosses drink in the seconds between fall and flash"*, *"the toughest alloys they knew"*) and the
six-phase cycle in `FORGE_CYCLE_MECHANICS_1`: still heat, gas wash, boiling rain, freeze to basalt crust,
growth, then glowing cracks and melt-back.

The roster this sits beside has no overlap with any of the three. Ground creatures: dhokkur (an obsidian
hill that wakes in rain), julmox (a kettle-slab that sits sealed between rains), dhuvvox (slag nodules
that hatch), dhoggur (an ash digger), metallovore (eats metal). Air: bulloo, greater bulloo, fleet
flier, jossur.

Concept renders are artpipe jobs `forgeslow_<name>_v1_east`, filed from
`design/RimMandrake/forge_slowground_concepts_2026-10-20.json`. Each is drawn at the lost slot's measured
size (LavaSnail drawSize 2.1 cells) until a def sets its own.

| | **Kettugal**, the walking crucible | **Ummisk**, the glasswake | **Brazzok**, the chimney-walker |
|---|---|---|---|
| looks like | a low ceramic bowl on six basalt-disc legs, carrying a level pool of glowing slag; a long dipping lip-snout | a dome of hundreds of hollow glassy tubes packed like reeds, beaded with rain and steaming, on a fringe of cilia-legs; no face | a tall stack of fused kiln rings on four stilt legs, a firebox mouth at the base, a steam banner from the top |
| ecology | sips melt from the red seams; metals settle out in its bowl. It is slow because the bowl must stay level | it *is* the moss that drinks between fall and flash: a walking colony that soaks up the scalding rain and stores it | breathes in ash and vent gas, burns it in a furnace gut and vents steam: a small copy of the foundry towers |
| gameplay hook | **a living warning of melt-back**: the first thing to walk off the crust when the cracks begin to glow. Shearing it gives slag beads or alloy. Killed or hit, its bowl spills burning slag | **leaves a path**: its wet underside quenches lava-edge cells into a short-lived glass trail you can walk on. Follow an ummisk across the flows | **lore and landmarks**: herds stand in lines through the still heat with their plumes up, reading as towers on the skyline. Rumour says the ancients grew the first towers from brazzok shells. Shearing gives fired ceramic plates |
| silhouette in the rig | a wide low dome with a bright top. Reads at any zoom; one body sprite, no appendages | a lumpy round mound with steam wisps. One body sprite | tall and vertical, unlike anything else on the roster. One body sprite; the plume can be a mote |
| why it is not a reskin | no vanilla or donor animal carries liquid food or warns of a terrain phase | no animal changes terrain; it has no head, so it is no vanilla body plan | no vanilla quadruped is a tall, vertical shape on stilts |
| cost to build | a ThingComp to read the cycle phase and drive a flee job, plus a shear product. Medium | a terrain-swap comp feeding the existing freeze machinery. Medium to high | defs, a shear product and a steam mote. Low |

**Agent's lean: Kettugal.** It ties to the alloys line and gives the colonist a readable sign before the
deadliest phase of the cycle. It also has the strongest silhouette at game zoom. Ummisk is the most
alien of the three; Brazzok is the cheapest to build and the best for lore.
