# RimWorld Sarlacc Encounter — Current Design Direction

## Core Concept

The Sarlacc will be a **large-scale C# encounter system**, not a conventional RimWorld pawn.

It is a gigantic, mostly subterranean organism whose visible presence is only the feeding pit, mouth, tentacles, disturbed terrain, debris, and other surface effects. This allows truly enormous specimens without forcing RimWorld to treat the entire creature as one gigantic pathfinding entity.

The encounter should feel like a major environmental catastrophe and boss-scale predator while remaining technically manageable in RimWorld 1.6.

## Star Wars Lore Foundation

A mature Sarlacc is essentially a **sessile, deeply buried organism**. Its enormous body remains underground while its mouth and feeding structures interact with the surface.

For the mod, this means:

- The Sarlacc is already beneath the map.
- The encounter begins when it awakens, is disturbed, or begins feeding.
- The **pit opens** as sand and terrain collapse inward.
- Tentacles and other feeding structures emerge from the newly exposed pit.
- Very large specimens may have subterranean tendrils capable of surfacing far from the central mouth.
- Sarlaccs can occur on multiple worlds because their lifecycle allows them to establish themselves far from their point of origin.

The important visual idea is not that a giant creature walks onto the map, but that the player discovers that an enormous organism has been underneath the terrain all along.

## Encounter Architecture

The Sarlacc will be implemented as an **encounter controller coordinating multiple specialized graphical and gameplay elements**.

Likely major elements include:

- Central Sarlacc encounter controller
- Maw / pit object
- Independently controlled tentacles
- Terrain-collapse effects
- Sand, dust, debris, and environmental animation
- Grapple and dragging states for living targets
- Structural-damage interactions
- Size and age parameters controlling encounter scale

The visible footprint can be dramatically larger than the actual logical footprint used for collision and pathfinding.

## Visual Presentation

The mouth should be built from multiple animated rendering layers rather than a single static sprite.

Possible layers include:

- Collapsing outer sand bowl
- Deep pit shadow
- Organic lip or rim tissue
- Teeth
- Inner throat
- Beak or central feeding structure
- Dust and sand effects
- Falling debris
- Independent tentacles

This should make the Sarlacc appear much larger and more animated than normal RimWorld creatures.

## Tentacles

Tentacles are one of the primary gameplay and spectacle systems.

A tentacle can be represented logically by a small number of control points and a target endpoint while being rendered as a long segmented or spline-like graphical structure.

This allows:

- Very long tentacles without dozens of physical map objects
- Smooth animation
- Tentacles wrapping around or striking targets
- Individual tentacles to act independently
- Large numbers of tentacles on ancient specimens

For enormous Sarlaccs, some attacks can travel underground.

A subterranean tendril can be represented by:

- Moving ridges in the sand
- Dust bursts
- Shaking vegetation
- Tossed rocks or debris
- A visible disturbance racing toward a target
- A tentacle erupting from the ground at the destination

This allows the largest Sarlaccs to threaten much of the map without drawing every tentacle continuously from the central pit.

## What the Sarlacc Can Grab

The Sarlacc can physically drag mobile or disposable targets toward the pit, including:

- Pawns
- Animals
- Corpses
- Loose items
- Debris
- Vegetation

Dragged pawns can visibly move toward the mouth while struggling or being rescued.

Tentacles can also attack major fixed objects.

## Buildings and Vehicles

Buildings and vehicles remain in place while the Sarlacc attacks them.

Tentacles can:

- Wrap around them
- Strike them
- Apply structural damage
- Tear pieces away
- Destroy components
- Generate debris
- Damage occupants
- Collapse or destroy the target

Debris and loose material created by this destruction can then be pulled toward the mouth.

This keeps interaction with RimWorld buildings, rooms, power systems, and vehicle frameworks tractable while preserving the spectacle of the Sarlacc tearing a colony apart.

## Variable Sarlacc Scale

Sarlaccs can vary enormously in size.

Useful ecological categories include:

### Juvenile

- Small pit
- Few tentacles
- Limited reach
- Dangerous local predator

### Mature

- Large visible pit
- Multiple active tentacles
- Significant local destruction
- Capable of attacking colony infrastructure

### Ancient / Leviathan

- Massive pit or crater-like feeding area
- Numerous tentacles
- Extremely long reach
- Underground tendrils capable of surfacing across large portions of the map
- Major colony-scale environmental threat
- Potentially ancient enough to have accumulated unusual intelligence and memories

Actual dimensions can vary procedurally inside each category.

## Encounter Escalation

The event should develop in stages rather than appearing instantly at full intensity.

Possible early signs include:

- Animals becoming agitated or fleeing
- Slight ground movement
- Objects trembling
- Unusual sinkholes or depressions
- Bones or remains around suspicious terrain
- Sand shifting
- Linear underground disturbances

The awakening then escalates into:

1. Terrain cracking and subsidence
2. Sand collapsing inward
3. The central pit opening
4. Nearby objects and vegetation being pulled toward the collapse
5. Mouth structures becoming visible
6. Tentacles emerging
7. Increasingly aggressive feeding behavior
8. Larger structural attacks as the Sarlacc becomes more active or threatened

The encounter should feel like a buried ecosystem suddenly revealing itself.

## Ancient Sarlacc Intelligence

Legends material provides an especially strong concept for very old Sarlaccs: over immense periods of digestion, they can absorb fragments of victims' memories and consciousness.

Ancient specimens can therefore possess a strange accumulated intelligence assembled from generations of consumed beings.

This can appear through:

- Fragmentary voices or messages
- Knowledge originating from past victims
- Recognition of names or languages
- Behavioral adaptation
- More sophisticated target selection
- Memories or information that predate the colony
- A sense that many partially preserved minds exist within the creature

This does not require a complex simulated intelligence system. It can primarily function as an encounter-personality layer, narrative system, and set of targeting modifiers.

## Relevant RimWorld 1.6 Engineering References

Existing active 1.6-era mod projects provide useful implementation patterns.

### Vehicle Framework

Useful for:

- Large and multi-cell entities
- Custom movement and pathing concepts
- Composite graphics
- Component damage
- Compatibility considerations for vehicles

### Vanilla Factions Expanded — Insectoids 2

Useful for:

- Complex encounter controllers
- Burrowing creatures
- Special AI
- Custom rendering
- Think trees and verbs
- Event systems
- Large hostile environmental entities

Its history of changing burrow collision behavior to avoid pathfinding performance problems is particularly relevant to the Sarlacc architecture.

### Big and Small Framework

Useful for:

- Rendering entities far outside normal RimWorld pawn scale
- Size-related rendering techniques

### Alpha Animals

Useful for:

- Exotic creature behaviors
- Specialized damage and ability systems
- Mature examples of unusual RimWorld creature mechanics

### Vehicle and Boss Mods

Large vehicle and boss mods demonstrate that RimWorld can successfully present entities far larger and more visually elaborate than ordinary pawns.

The Sarlacc can build on those rendering and encounter patterns while using its own specialized architecture.

## Current Experience Goal

The Sarlacc should feel less like a conventional high-HP boss and more like a **living environmental disaster**.

The player sees the desert itself change:

- Ground collapses
- Sand pours inward
- Tentacles erupt
- Pawns are grabbed
- Vegetation disappears
- Structures are battered apart
- Vehicles are damaged
- Debris is dragged toward the maw
- Huge underground tendrils race beneath the colony

The defining realization of the encounter is:

**The Sarlacc did not arrive on the map. The colony was built over it.**
