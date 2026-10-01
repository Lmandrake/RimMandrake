## Recommendations

### 1. The Droid Hospice — “Carry the casualty home; rebuild a person, not a prize.”

Build this first. Players find deliberately posed, powered-down servitors among the defensive rings. An intact chassis must be physically hauled to a hospice cradle, diagnosed, supplied with components and repaired over several days. Indicator lights, hesitant limb movements and recovered voice fragments make awakening feel gradual; failures leave an identifiable irreparable wreck.

- **Lifts:** 2 Discoverable technology, 3 Unique resources, 4 Surprising creatures
- **Build:** `ThingDef` chassis and hospice; study/work jobs; staged `Comp` state; pawn conversion and campaign droid substitution. **Large C#**
- **Warscar fit:** It turns the battlefield’s abandoned defenders into patients. No other biome should make salvage feel like battlefield medicine.

### 2. The Settling — “When the wind dies, the war comes down.”

After sustained calm, pale aerosol begins falling vertically. Metal creaks stop, the world becomes unnaturally quiet, and unroofed pawns accumulate vanilla toxic buildup. A thin film records directional footprints, blood trails and the chatrak’s circling until wind returns and visibly strips the record away.

Use a bounded track grid rather than thousands of filth objects; cap decals and prioritize recent humanoid and large-animal tracks.

- **Lifts:** 1 Unique mechanic, 7 Soundscape, 8 Interesting weather
- **Build:** Weather/GameCondition defs; wind-watching `MapComponent`; Harmony hook on path-cell entry; overlay mesh and save data. **Large C#**
- **Warscar fit:** The signature hazard is not a storm but a battlefield becoming legible during silence.

### 3. The Projectors Still Hum — “Study an ancient clean-air circle and take it aboard.”

Some ruined projector rings retain power. During a Settling, their protection is unmistakable: film stops at a perfect boundary while the machinery produces a low, uneven hum. Studying one unlocks a compact aerosol screen usable in every polluted biome and on gravships.

Keep it narrow: small radius, substantial power draw, and replaceable reaction membranes. It blocks particulate fallout and toxic buildup, never gases, heat or weapons.

- **Lifts:** 2 Discoverable technology, 3 Unique resources, 6 Gravship touch
- **Build:** Studyable ruin, research unlock, cached protected-cell field, exposure hooks, gravship building category. **Large C#**
- **Warscar fit:** This is the place where ancient defenses still attempt their original job, without explaining whom they protected.

### 4. The Embankment That Breathes — “One section of the Last Line stands up and begins eating it.”

A dormant **totchak** remains on-map as a huge, faintly breathing fortification silhouette. Nearby mining, deconstruction or explosions wake it with a letter and a shower of slag. It prefers ancient walls and wreckage, but eventually consumes player walls too, leaving tooth-scored rubble and permanent breaches before lying down somewhere new.

- **Lifts:** 4 Surprising creatures, 5 GIANT beast
- **Build:** Custom race and renderer state; dormancy/noise comp; building-eating job giver; ruin-first targeting and bite-mark filth. **Large C#**
- **Warscar fit:** It is neither an ancient weapon nor the unnamed enemy—only an enormous animal that learned fortifications were food.

### 5. The Chatrak’s Snap — “The grazer gives you a day of warnings before fear finally reaches it.”

Replace the donor stand-in with the owned **chatrak**, restricted to Warscar. Its incubation progresses through readable stages: lifted plates, refusal to eat, repetitive circling, then a clearly announced charge. Ricocheting armour makes an enraged animal dangerous without giving it supernatural attacks.

- **Lifts:** 1 Unique mechanic, 4 Surprising creatures
- **Build:** XML race, armour and hediff stages; small renderer overlay; conditional think-tree jobs; port the franchise-free scaria arming to RM. **Small C#**
- **Warscar fit:** It literally eats wreckage until the battlefield’s sickness turns it into another weapon.

### 6. The Rainbow Pools — “Their colours are chemistry, not life, and beauty is the danger sign.”

Pools cycle through visually distinct reaction phases, accompanied by slow boiling and different surface icons for colour-blind accessibility. Rim taps extract phase-specific reagents: dielectric gel for projector membranes, etchant for hospice work, and a medical coagulant. The most luminous phase causes the worst acid burns.

Early draws fill a player journal; complete observations unlock a phase reader.

- **Lifts:** 2 Discoverable technology, 3 Unique resources
- **Build:** FlowWorks-backed liquid or custom pool terrain; phase `MapComponent`; animated overlay; rim-harvester and journal UI. **Large C#**
- **Warscar fit:** These are leaking military reactions that never finished, not an oasis or ecosystem.

### 7. The Geiger Choir — “You navigate contamination by beetles, wind-harps and missing sound.”

Visible **tetchik** colonies provide the fiction, while a proximity sound controller supplies performance-safe clicking whose tempo follows local glower density. Ruin barrels keen in wind and stop during the Settling. Pools boil softly. Campaign Sentinel ground creates an abrupt hole in every ambient layer.

Include real settings for master volume, tick density and reduced-repetition mode.

- **Lifts:** 4 Surprising creatures, 7 Soundscape
- **Build:** `SoundDef`s, biome ambience, camera-local sustainers and tagged source extension. **Small C#**
- **Warscar fit:** The soundscape measures residue and broken machinery; silence itself predicts fallout.

### 8. The Old Tongue — “The battlefield’s manuals are still written on its walls.”

Inscription panels require sustained transcription by a high-Intellectual pawn. Partial readings produce rubbings and practical clues; completed sets unlock hospice protocols, projector calibration and the pool phase reader rather than generic research points. Campaign scholars can accelerate translation but do not monopolize free-tier progress.

- **Lifts:** 2 Discoverable technology, 9 Relationship to the gods
- **Build:** Studyable panel defs, transcription job, collection tracker and conditional research unlocks. **Small C#**
- **Warscar fit:** Warscar technology is recovered as doctrine and testimony, never found intact in an exposed chest.

### 9. The Mark, Made a Trade — “The scar hurts, but it teaches a pawn how ruins conceal their dead.”

Move the permanent mark into RM with its mood cost and severity floor. Marked pawns gain speed only when salvaging registered ancient structures and occasionally expose sealed caches. The cache appears physically behind a loosened panel; it never materializes unexplained. Marks cannot stack or be profitably farmed.

- **Lifts:** 1 Unique mechanic
- **Build:** XML hediff/thoughts plus a salvage stat worker and cache-reveal hook. **Small C#**
- **Warscar fit:** The biome changes visitors into better readers of the record while ensuring the change remains a wound.

### 10. The Pilgrim Ends — “Every terminal camp supplies evidence, never an answer.”

Place campaign-only camps at authored locations on the fixed planet. Bedroll orientations, abandoned provisions, journals and remains show how each pilgrimage ended. Reading the record advances one Scarlands lore rung. Ideoligion-dependent thoughts interpret each discovery as shrine, grave or machine-site without confirming the hidden truth.

- **Lifts:** 9 Relationship to the gods
- **Build:** Preplaced `SitePartDef`s, readable records, lore-stage calls and conditional thoughts/history events. **Small–medium C#**
- **Warscar fit:** Its theology is archaeological: people come here to confront a dead power, and the ground refuses to settle the argument.

### 11. The Wreck-Eater Ecology — “Everything living here consumes one layer of the aftermath.”

Complete the free-tier repaint: add ruin-only wreck-lichen; move the pallbearer and scar roach into RM; wire finished glower art; retire Scorched Stars; remove Soil; correct the biome label. Chatraks rasp lichen from wrecks, pallbearers process corpses, scar roaches clean residue, and tetchik inhabit glower crust.

- **Lifts:** 3 Unique resources, 4 Surprising creatures
- **Build:** Mostly XML; small placement validator for wreck-lichen. **XML + small C#**
- **Warscar fit:** It enforces the biome’s admission test: nothing pastoral, nothing green, and nothing alive without a relationship to the war’s remains.

## Top 3

1. **The Droid Hospice** — The binding first build: it gives the biome an emotional centre and immediately joins exploration, technology and a memorable new companion.
2. **The Settling** — It turns Warscar’s “ground as record” thesis into distinctive moment-to-moment play.
3. **The Projectors Still Hum** — It converts the signature hazard into valuable learned technology and finally gives Warscar a meaningful gravship legacy.