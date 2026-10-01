The slate has the right spine, but it should be tightened around one rule: **the Dark is physical ecology, not a generic fog-of-war debuff.** Build the field first, then let weather, creatures, resources, worship and the gravship interact with that same field.

## 1. The Folded Dark — Heat cuts holes in a material night

**Pitch:** Warmth creates sharp-edged clear pockets; outside them, light and gunfire are swallowed by the aerosol.

Players see lamps fade into black at a visible boundary while campfires, heaters and warm rooms carve temporary windows through it. Shots crossing dense Dark become unreliable; nothing provides clean sensing through it. A thermometer explains why one apparently identical patch is clear and another blind.

**Marks:** Unique mechanic, discoverable technology, interesting weather.

**Build:** Large C#. A coarse `MapComponent` density grid updated from temperature, weather and local emitters; a `SectionLayer` haze mask; line-integrated penalties patched into ranged shot calculations; registered light-radius attenuation rather than destructive edits to `GlowGrid`. Add intensity, accuracy-cap and visual-opacity settings. A first naturally formed pocket triggers a research opportunity for the **fold-lamp**, which is explicitly a heater that clears air, not a magical sensor.

**Why here:** The Crags are the only biome where visibility is a phase state of airborne matter controlled by ordinary heat.

## 2. The Unveiling — For a few hours, the whole veil lifts

**Pitch:** A rare, merciful weather event reveals the true scale and colour of the Crags before darkness closes again.

The haze retreats across the map like a curtain. Distant yellow flora answer the blue gammas, animals freeze or scatter, and a low chord replaces the usual silence. Awake outdoor pawns receive “I saw the Black Crags”; veil-revering ideoligions may begin a vigil. It should reveal things through normal sight, not automatically expose every secret or grant omniscient targeting.

**Marks:** Interesting weather, relationship to the gods, surprising creatures.

**Build:** Medium C#. A `GameConditionDef` overriding Dark density, paired with a rare incident and dedicated sky/colour grading; XML thoughts and an Ideology ritual/precept gated to the condition. Single-digit occurrences per year and a Mod Setting for frequency.

**Why here:** Other rare weather is danger. The Crags’ miracle is simply being allowed to see.

## 3. Ghorrumak, the Thunder’s Answer — Put the existing giant on the map

**Pitch:** Witchfire thunder sometimes answers itself, and then a sixteen-square dragon descends through the crags.

A subsonic call arrives several seconds before a false “lightning” flash. A ghorrumak then enters visibly from the map edge, crosses or settles, breathing fire and regenerating. Its arrival gets a letter and recognizable call; if it leaves, it physically reaches an edge rather than vanishing.

**Marks:** GIANT beast, soundscape, surprising creatures.

**Build:** XML plus small C#. Wire the rostered animal and owned art; add a storm-gated incident, call `SoundDef`, and visible entry behaviour. First measure and normalize its contradictory body-size values.

**Why here:** It converts the Crags’ broken thunder into an animal voice, rather than adding another generic megafauna encounter.

## 4. Etchfall Boundary — Heat brings down the grain that eats stone

**Pitch:** Collapsed Dark precipitates around clear pockets, corroding exposed construction but leaving valuable tholin.

During Etchfall, pale grains tick against rock and collect in ragged rings near the edges of warm clearings. Unroofed steel and stone slowly pit; roofs protect them. Colonists can sweep the deposit into `RM_Tholin`, refining it into chemfuel or fold-lamp consumables.

**Marks:** Unique resources, interesting weather, discoverable technology.

**Build:** Medium C#. A WeatherDef reads the Dark grid’s falling-density boundaries, applies restrained exposure damage, and spawns harvestable dust. A dedicated cleaning job yields an item; XML recipes handle refinement.

**Why here:** Unlike the Warscar’s Settling, this residue does not preserve history. It marks where darkness chemically died, consumes structures, and becomes fuel.

## 5. The Hidden Gravship — Land here to disappear, at a price

**Pitch:** A grounded gravship slowly acquires a Dark mask that delays hostile detection while cutting it off from orbit.

A visible “signature masked” meter rises while the ship remains grounded in dense Dark. Pursuit warnings lengthen, but orbital trade and long-range scans fail. Starting the grav engine tears the mask away in a luminous wake and immediately makes the ship detectable again.

**Marks:** Gravship touch, unique mechanic.

**Build:** Small–medium C#. First correct `surveyShadowBiomes` for both RM and campaign defs. Then add a map/ship comp tracking exposure to Dark and an inspectable status consumed by pursuit and orbital-comms checks.

**Why here:** The Crags become somewhere a travelling settlement deliberately runs to—not another biome that merely damages ships.

## 6. Gharrek Gust-Feast — The food web visibly wakes when the air moves

**Pitch:** Every gust opens hundreds of chemotrophic gill-fans at once.

Stillness leaves gharreks plated shut and stone-cold. A gust lands with a hard whump; blue fans flare across the map in a rolling rustle while predators begin hunting. Penned animals gain nutrition only during these pulses and occasionally shed useful gill-ash.

**Marks:** Surprising creatures, soundscape, unique resources.

**Build:** Small–medium C#. One irregular `RM_GustController` provides short pulses to animal comps, sound sustainers and later systems. XML supplies the creature, products and pen behaviour. This controller must enforce true stillness between gusts.

**Why here:** It embodies “a gust is a meal.” The Leaning Scrub predicts wind as a calendar; the Crags experience it as an ecological heartbeat.

## 7. Ulkhorr Halo — A predator carries darkness into the warm refuge

**Pitch:** The ulkhorr is a moving hole in the colony’s biological light.

Players first notice lamps dimming in sequence and animals refusing a corridor. The halo remains visible as a dark knot around the beast even inside heated rooms. Killing it still summons the existing eclipse, turning victory into an ominous consequence.

**Marks:** Surprising creatures, unique mechanic.

**Build:** Medium C#. A pawn comp writes a moving high-density disc into the Dark field, with a fallback local light suppressor if the full field is disabled. Port it to an owned def alongside the finished art.

**Why here:** It breaks the otherwise reliable rule that warmth means sight, without introducing supernatural clean sensing.

## 8. Durrgak Cairns and the Veil Vigil — Worship grows around deniable arrangements

**Pitch:** An animal’s compulsive stone rings become sacred—or unsettling—without ever proving who taught it.

Durrgaks construct small obsidian rings, aligned caches and over-provisioned dens. Pawns find useful items among them and gain “Someone arranged this.” Ideologies may treat a cairn as the focus of a **Veil Vigil**, with its best outcome during an Unveiling. Campaign-only rings can advance ambiguous Nightbrother rumours, never confirm Forsakens.

**Marks:** Relationship to the gods, surprising creatures.

**Build:** XML plus small C#. Animal job giver, cairn ThingDefs, scatter incident, thought, ritual target and optional staged-lore call.

**Why here:** No other biome makes deliberate arrangement itself the disturbing evidence.

## 9. Krizzak Lampfall — A flying swarm eats illumination, not electricity

**Pitch:** Perimeter lights go dark one by one as moth-like krizzaks settle on them.

Players hear soft glassy clatter before seeing silhouettes clustered around lamps and glow plants. Perched swarms shorten glow radius and suppress plant glow; nearby heat drives them away. They visibly fly between targets using `PawnFlyer`, never teleport.

**Marks:** Surprising creatures, soundscape.

**Build:** Medium C#. Custom flight/job logic, a perch comp registering local light attenuation, heat avoidance, and XML incident/animal defs.

**Why here:** Mynocks attack machinery; krizzaks consume the Crags’ actual currency—light.

## 10. Etchcap Hollows — Make the gourmet line a reward for precipitation

**Pitch:** Etchfall creates rare chemical soils where an intensely valuable fungus can grow.

Black-violet caps appear in low, recently etched hollows and glow only when mature. Harvests become preserved **etchcap relish** or a dedicated lavish crag meal with a distinctive mood thought and strong trade value.

**Marks:** Unique resources, discoverable technology.

**Build:** XML plus small C#. `RM_EtchHollow` terrain, wild/sowable plant, recipes and food defs; the Dark/Etchfall component occasionally converts suitable low cells. Avoid fragile attempts to preserve ingredient bonuses through ordinary meals.

**Why here:** It turns the destruction of rock by collapsed darkness into cuisine, without relying on sunlight.

## Slate cuts and corrections

- **Cut gust turbines for now.** “Random wind generator that breaks” is mechanically thin and too close to the Leaning Scrub. The gust controller earns its place first through ecology and sound.
- **Defer grown light.** It risks echoing both Twilight Deep and Lantern Deeps. Keep gammas as ecology until their actual glow and crop-light thresholds are measured.
- **Do not invent Lightfall’s bottom.** It needs the owner’s authored revelation; procedural mystery filler would weaken it.
- The free-tier body port, labels, flora requirements, settings and dusk-rat art remain necessary release work, but they are foundations rather than bedazzle features.

## Top 3

1. **The Folded Dark** — It is the biome’s irreplaceable rule and the foundation for technology, combat, weather and ecology.
2. **The Unveiling** — It turns temporary visibility into awe, memory and worship instead of merely removing a debuff.
3. **Ghorrumak, the Thunder’s Answer** — It closes the giant and soundscape gaps cheaply with an already rostered, already illustrated icon.