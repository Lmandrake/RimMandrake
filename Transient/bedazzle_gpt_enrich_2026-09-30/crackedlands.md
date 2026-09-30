# GPT enrichment consult: The Cracked Lands (formerly Flooded Canyon)

Asked 2026-09-30 via codex exec (gpt-5.6-sol, xhigh). Advice only: nothing here is ruled.

Recommendations are ordered toward the weakest marks first: discoverable technology, gravship integration, and the gods, followed by sound, weather, and ecological depth.

### 1. The One-Stay Water Survey — *Read the canyon, locate one hidden cistern, and carry the Swale home as knowledge.*

- **Experience:** Veqma tips form a faint green contour; sleeper clusters and tarruq runs corroborate it. Completing several field observations narrows the search to a diggable cell. The player may excavate a persistent cistern or sell the named survey before departing. The first success permanently unlocks the Swale in the Utinni campaign.
- **Marks:** 2 Discoverable technology, 3 Unique resources.
- **Build:** **Small C#**. A MapComponent creates one hidden-water field and tracks observations; inspect/gizmo jobs reveal progressively smaller search zones. Add XML for the survey item, observation jobs, cistern head, and campaign unlock. Keep the Swale normally available outside Utinni.
- **Why here:** Every clue is part of the Cracked Lands’ sealed-versus-flooded ecology. It produces a complete payoff during one gravship visit rather than demanding settlement.

### 2. The Belly Sounder — *A gravship survey instrument learned here, not a chime carried away.*

- **Experience:** When the grounded ship fires a sounding pulse, dust jumps from the canyon walls and a bass vibration travels through the hull. It reveals broad probability bands for water, fossil strata, and suspiciously regular pan formations—never exact cells.
- **Marks:** 6 Gravship touch, 2 Discoverable technology.
- **Build:** **Small C#** plus XML. A ship-registered building comp queries the survey and fossil map components, then draws temporary overlays. Unlock its recipe alongside or just after the first completed hand survey.
- **Why here:** It is seismic fieldcraft derived from cracked strata and sleeping giants. It preserves the rejected ruling: no ship-mounted chime and no wax tank.

### 3. The Ledges of Mercy — *Ancient refuge ledges make the flood’s theology physically useful.*

- **Experience:** Map generation places high ledges bearing worn figures, old offerings, and chime-lines stretched across the canyon below. Inscriptions describe the flood as “the mercy that kills, then feeds.” During warnings, neutral visitors and trained animals attempt to reach the nearest ledge.
- **Marks:** 9 Relationship to the gods, 1 Unique mechanic.
- **Build:** **Small C#** with XML ruins. MapGen scatters ledge prefabs above the flood mask; a flood-phase lord/job temporarily favors them. Inspectable carvings and one-shot memories provide lore without adding campaign precepts.
- **Why here:** Its religion is inseparable from lethal water, refuge height, and the soil left afterward—not a portable temple aesthetic.

### 4. Five Beats Before Water — *Turn the existing flood clock into a spatially staged sound composition.*

- **Experience:** Wind threads the slots; sleeper pans begin ticking; tarruq calls stop; physical chime-lines toll from far canyon to near; finally the flood becomes a continuous roar. Players can estimate urgency with their eyes closed.
- **Marks:** 7 Soundscape, 1 Unique mechanic.
- **Build:** **Small C#** plus bespoke SoundDefs. Replace the global `TinyBell` call with emitters attached to map-generated chime anchors. Select stages from flood phase and distance; gate tarruq ambience off during pre-chime.
- **Why here:** These are strings hung across real canyon gaps, activated by rising water and wind—not magical alarms or generic desert ambience.

### 5. Peakstorm Light — *A dry horizon storm forecasts water arriving from somewhere the player cannot see.*

- **Experience:** The map remains rainless, but the northern sky turns bruised red and distant lightning silhouettes the peaks. Dust motes briefly reverse direction as cool, wet-clay air pushes through the slots.
- **Marks:** 8 Interesting weather, 7 Soundscape.
- **Build:** **XML + small C#**. A precipitation-free WeatherDef supplies sky colors, wind, overlay motes, and distant thunder. The flood component raises its probability before some floods without making it a perfectly reliable timer.
- **Why here:** It dramatizes upstream water in a canyon that receives floods without local rain. It would be meaningless in an ordinary desert or volcanic biome.

### 6. The Three-Height Flora — *Give the canyon plants for sun-flat, shade-line, and wall-seam rather than one generic plant roster.*

- **Experience:** Red-brown **qirra mats** unfold only on recently wetted open clay; Veqma maps hidden water in blue shade; pale **talus clasps** root beside fossil-bearing rock and slowly pry cracks wider. Only Veqma shows green, and only inside the shade line.
- **Marks:** 3 Unique resources, 4 Surprising life, 8 Weather/ecological response.
- **Build:** **XML + small C#**. Three PlantDefs with terrain/glow restrictions; the flood component wakes qirra mats, while a placement worker limits talus clasps to natural walls. Optional harvests should be minor so their primary value remains ecological information.
- **Why here:** The flora visibly occupies the canyon’s three governing strata: flood, shade, and cracked stone.

### 7. Fossils That Remember the Map — *Make every flood expose a few new pages of the canyon’s geological ledger.*

- **Experience:** Receding water leaves fresh pale scars in selected wall cells. Mining yields common impressions, articulated alien skeletons, or named deep-stratum specimens showing pan-giants curled in the seal position. Mounted fossils retain where and when they were found.
- **Marks:** 3 Unique resources, 9 Gods/lore.
- **Build:** **Small C#** plus XML. Convert eligible flood-adjacent natural rock into fossil mineables; use a quality/name comp for rare finds and display furniture. Store map, quadrum, stratum, and specimen text in CompProperties.
- **Why here:** The recurring flood actively recuts ancient canyon walls. Elsewhere fossils would be static ore; here the landscape keeps revealing its dead.

### 8. A Muttavaq Never Disappears — *Its movement and reburial permanently rewrite the player’s map.*

- **Experience:** The awakened giant pushes through the flood like a moving hill, leaving a shallow channel, crushed structures, and mud windrows. When it seals again, drag furrows terminate at a new visibly irregular pan marked “freshly sealed.”
- **Marks:** 5 Giant beast, 1 Unique mechanic.
- **Build:** **Large C#**. A controlled path writer alters only validated terrain cells and records damage. Reburial serializes the pawn inside a persistent `RM_MuttavaqPan` thing rather than silently despawning it; emergence restores the same individual.
- **Why here:** It embodies the biome’s central inversion: apparent terrain is fauna, and fauna becomes terrain again—with readable evidence throughout.

### 9. The Recede Feast — *Irqit hatch in millions, and the migrant sky arrives to harvest the brief abundance.*

- **Experience:** Flood-touched mud suddenly moves like fur. Irqit breed once, then die into visible windrows as the ground dries. Convor, Can-cell, and woolamander migrants physically fly in, feed, and later depart overhead.
- **Marks:** 4 Surprising creatures, 7 Soundscape.
- **Build:** **Small C#** plus XML. Spawn bounded irqit cohorts from the soaked-cell list with lifecycle hediffs; death leaves corpses or eggfield filth. Trigger existing flight mechanics for migrant arrival and departure—never edge-spawn or vanish them invisibly.
- **Why here:** It makes the Cracked Lands’ “nothing, then everything, then nothing” calendar playable while preserving the fliers’ single native biome.

### 10. The Floodline Salvage Claim — *Recession exposes wreckage, but another scavenger crew may already have marked it.*

- **Experience:** Mud reveals half-buried components and recognizable wreck silhouettes. Claim stakes appear; a rival crew arrives to negotiate, race the player, or steal only after relations collapse.
- **Marks:** 1 Unique mechanic, 3 Unique resources.
- **Build:** **Small C#**. Scatter disciplined loot from recorded flood cells and run a temporary visitor lord with claim-area jobs. The base RM layer uses generic scavengers; the Utinni patch substitutes Jawas, crawler props, and Star Wars dialogue.
- **Why here:** It turns “a flood is a salvage strike” into a social event tied to freshly scoured ground, not another random ancient-danger cache.

## Top 3

1. **The One-Stay Water Survey** — completes the ruled transient-player loop and makes the Swale a memorable, durable discovery.
2. **The Belly Sounder** — fills the gravship mark with a useful ship system that grows directly from canyon fieldcraft.
3. **The Ledges of Mercy** — gives the gods physical presence, practical flood value, and unmistakably local theology.
