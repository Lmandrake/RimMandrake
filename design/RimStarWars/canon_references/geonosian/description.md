# Geonosian

**defName**: `RSW_RimMandrakeGeonosianVariants`
(`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Carries `combatPowerFactor 0.7`, no `nameMaker`, and a generic icon
(`CustomXenotypeIcon8` — the same generic icon `RSW_RimMandrakeGand` uses).

## Sourced text (Wookieepedia)
Geonosians are a **semi-insectoid** sentient species native to **Geonosis**. Infobox:
**height 1.7 meters (5 ft 7 in)** (*The Clone Wars: Character Encyclopedia — Join the
Battle!*) — a hard, sourced measurement, and it is **human-average**; **skin dark
orange to green** (*Attack of the Clones*); habitat **desert or wasteland**; language
**Geonosian hive-mind**; sole listed distinction **Hive-based**. **Mass, lifespan and
eye colour are EMPTY** — no mass and no lifespan exists for this species. The canon
article has **no "Biology and appearance" section at all**; the biology below is drawn
from *Society and culture*.

**Caste and body plan.** A **caste-based species separated by positions that included
drones, warriors, and elites**, born into hives each led by a **queen** who lays the
hive's eggs and issues orders to the public leaders of Geonosis. 🔑 **"Even though they
were born without wings, drones were capable of becoming warriors if they proved
themselves worthy by successfully defeating other drones in an arena."** Warriors
**had wings and a thick exoskeleton, and they were dedicated to warfare.** So **wings
are earned and caste-specific, not universal** — this is the single most load-bearing
fact for how a Geonosian should look. **Geonosians also had two sets of mandibles,
outer and inner, which they used to gesture** — clicking the outer pair twice meant
"Work Harder," clicking both sets meant "Die." **The Geonosians had yellow-colored
blood.** **Geonosians could also be sensitive to the Force.** Queens **took no more
than two years to grow from a small egg to a considerable size** and resided
underground in the catacombs; one, **Karina the Great**, could control sentient beings
including her own kind via **brain worms**. Colonies also existed on Foundry and Hypori.

**Behaviour.** **Naturally industrious and barbaric**, known for taking on
**construction projects from outside parties** — Baktoid Armor Workshop had them design
the Trade Federation's factories, and Orson Krennic: *"another thing most beings fail to
realize about the Geonosians is that it's in your nature to be industrious."*
**Productivity was key to Geonosian society, and if not kept in check with enough
tasks, hives could devolve into civil war and result in the deaths of thousands.** They
celebrated **Meckgin**, a day for the virtues of industry, and believed themselves
blessed by "the Creator." They **got drunk by eating a special fungus** which reacted
with their stomach fluids to create a euphoric body odour. They **mistrusted bounty
hunters**.

**Behind the scenes.** The species was inspired by a **termite infestation in George
Lucas's house**; the basic design came from **unused concept art of the Neimoidians**
that resembled B1 battle droids. Lucas originally wanted them **chameleon-like, able to
change colour with their surroundings** — nixed, though "the texture and colour of the
Geonosians do match that of their homeworld." The hive-mind language was mixed by Ben
Burtt from recordings of **penguin mating cries, fruit bats fighting over a banana, and
flying foxes**.

## Visual brief
🔴 **The two canon individuals in this folder look almost nothing alike, and that is the
point: this is a caste species, not a species with one appearance.** Do not average them.

**Sun Fac (`wookieepedia_sunfac_swctp.png`) — the WARRIOR read, and the default:**
- **Tall, gaunt, skeletal.** Extremely thin limbs with visible joint knobs and elbow
  spurs, a narrow ribbed thorax, and a pronounced **red slit down the mid-chest**. The
  silhouette is all length and no mass.
- **Digitigrade legs** with long shins and **splayed clawed feet showing three forward
  toes**.
- **A pair of long, narrow, translucent wings folded down the back to about knee
  height**, warm brown-red tinted with visible venation. One pair, not several.
- **An elongated, forward-jutting head with a long down-curved snout/muzzle**, and **two
  large curved horns sweeping up and outward from the sides of the skull** (Sun Fac's
  signature — check before generalising the horns to all warriors).
- **Chitin colour: mottled tan-brown with olive and grey blooms**, weathered and
  stone-like. Gold armour collar, gold belt-plate and loincloth with red cabochons.

**Poggle the Lesser (`wookieepedia_poggle_geo.jpg`) — the ELITE read:**
- **A broad, flaring, mitre-like crown**: two large flattened upswept lobes rising off
  the top of the skull, far wider than the face.
- **Deeply wrinkled, sagging, leathery hide** — the whole head is a mass of folds. Skin
  reads **dusty mauve-pink with olive-grey**, not orange and not green.
- **Narrow, deep-set, hooded eyes** under heavy brow folds. **Small and slitted, dark —
  the opposite of a big round bug eye.**
- **A long, heavy, pendulous wattle/dewlap hanging from the chin down onto the chest**,
  with thin tendril-like strands falling from the sides of the face.
- **No wings visible**, robed in rich fabric with gold arm bands and a spider brooch;
  long thin many-jointed fingers. An aristocrat, not a soldier.

**Terryl Whitlatch concept art (`wookieepedia_geonosianconceptart.jpg`) — historical, NOT
canon appearance.** Two gaunt grey-green figures with smooth conical heads, **large dark
almond eyes**, digitigrade legs, and **three or four pairs of long transparent dragonfly
wings each** (the sheet is annotated "transparent wings"). ⚠️ **This is pre-final
design and it disagrees with both film references** — the final Geonosian has one wing
pair, a snouted/wattled head, and no large almond eyes. Keep it as **design-history
reference only**; do not draw from it.

🔴 **`donor_current_sprite.png` is wrong for the species.** The greyscale head mask shows
a flat-topped triangular skull with **two large round bulging lateral eyes rendered as
white sclera with dark pupils**, a narrow ridged nose, and a wide down-turned frowning
mouth. Every canon Geonosian eye is **small, dark, narrow and deep-set under hooded
folds**; large white-sclera googly eyes read as a fish/amphibian head, not a
semi-insectoid one. The sprite also has **no mandibles** (canon gives *two* sets, outer
and inner), **no crown lobes**, **no wattle** and **no snout**. This is the
highest-value correction in this entry.

## Def-versus-canon (flagged)
- 🔴 **`RSW_BodySizeGene_small` directly contradicts the sourced height of 1.7 m.**
  Geonosians are human-average in stature. They are *gaunt* — thin, not small. Body_Thin
  is already in the list and is the correct way to say it; the size gene should not be
  doing this job.
- 🔴 **Skin colour is sourced as "dark orange to green" and the def has neither.** The
  list is `Outland_Skin_DeepBrown`, `Outland_Skin_Brown`, `Outland_Skin_PaleBrown` — the
  brown band only. No orange gene, no green gene. (The images add a third real tone,
  Poggle's mauve-pink, which is also absent.)
- 🔴 **`MeleeDamage_Weak` + `Pain_Extra` + `combatPowerFactor 0.7` contradict the
  warrior caste**, which canon describes as having a **thick exoskeleton** and being
  **dedicated to warfare**. `Pain_Extra` is unsourced outright.
- 🔴 **`AptitudeTerrible_Intellectual` contradicts the record.** Geonosians designed the
  Trade Federation's droid factories, engineered the Death Star superstructure, and
  Poggle the Lesser was an Archduke. "Naturally industrious and barbaric" supports the
  *social* penalty; nothing supports an intellectual one.
- 🔴 **Two sets of mandibles — the species' communicative anatomy — are unrepresented**,
  in the def and in the head sprite. So is **yellow blood**, and so is **Force
  sensitivity** (canon: "Geonosians could also be sensitive to the Force").
- ⚠️ **`Outland_Wings_Insect` is species-wide, but canon says Geonosians are born
  WITHOUT wings** and only drones who win an arena fight become winged warriors. Given
  the defName is `...GeonosianVariants`, the caste split may have been the intent; as
  shipped, every Geonosian is a warrior. Recorded as a design choice to confirm, not a
  bug.
- ⚠️ **`Outland_AcceleratedAgeing` is an over-read.** The two-year growth figure is
  specifically about **queens** going from egg to considerable size, not about drone
  lifespan — and **no Geonosian lifespan is sourced at all**.
- ⚠️ Generic icon shared with Gand (`CustomXenotypeIcon8`); no `nameMaker`.
- ✅ Correct and canon-supported: **`AptitudeRemarkable_Construction` +
  `AptitudeRemarkable_Crafting`** (the strongest def/canon match in this batch — an
  industrious builder species, by every source), **`Turn_Gene_MotivationHigh`**
  (productivity as a societal necessity), **`Outland_EggLayer`** (hive queens lay eggs),
  **`Outland_Voice_Insect`** (the hive-mind language), **`AptitudeTerrible_Social`**
  ("barbaric," mistrustful of outsiders), **`Body_Thin`** (the gaunt build in both
  images), **`RSW_butchergene_insectmeat` + `Outland_InsectBody`**, **`Hair_BaldOnly` +
  `Beard_NoBeardOnly`**, **`RSW_GeonosianHead`** as a concept (the art needs fixing, not
  the gene).

## Source URLs
- https://starwars.fandom.com/wiki/Geonosian (article HTML Cloudflare-walled; wikitext
  via
  `https://starwars.fandom.com/api.php?action=parse&page=Geonosian&format=json&prop=wikitext`,
  32,704 chars, 2026-09-15. Note the article carries an `{{Update}}` banner and has **no
  Biology and appearance section**.)
- File:SunFac-SWCTP.png — the infobox image → `wookieepedia_sunfac_swctp.png`
- Poggle the Lesser, the *Society and culture* inline image ("Poggle the Lesser was an
  Archduke") → `wookieepedia_poggle_geo.jpg`
- Terryl Whitlatch concept art, the *Concept and development* inline image →
  `wookieepedia_geonosianconceptart.jpg`
- Primary sources behind the infobox: *Attack of the Clones* (skin dark orange to green),
  *The Clone Wars: Character Encyclopedia — Join the Battle!* (1.7 m), *Star Wars:
  Complete Locations* (semi-insectoid), Databank "geonosian" (origin).

## Candidate images
- `wookieepedia_sunfac_swctp.png` — **the reference of record for the warrior caste.**
  A full-body Sun Fac on a transparent background: gaunt skeletal build, mottled
  tan-brown-olive chitin, one pair of long folded translucent wings, digitigrade
  three-toed legs, elongated snouted head with two large upswept side horns, gold
  armour. Settles proportion, wing shape and palette.
- `wookieepedia_poggle_geo.jpg` — **the reference of record for the elite caste**, and
  the best *head* reference in the folder: a film-quality close-up of Poggle the Lesser
  showing the mitre-like crown lobes, the deeply folded leathery hide, the narrow
  hooded eyes, the long pendulous chin wattle and the facial strands. Its palette
  (mauve-pink/olive) is a third real tone absent from the def.
- `wookieepedia_geonosianconceptart.jpg` — ⚠️ **design-history / negative reference
  only.** Terryl Whitlatch pre-final concept art with multiple wing pairs, large almond
  eyes and a smooth conical head — none of which survived to the films. Kept to document
  where the design came from, not to draw from.
- `donor_current_sprite.png` — ⚠️ **negative reference.** The mod's current head mask,
  whose large white-sclera round eyes and absent mandibles/crown/wattle contradict both
  canon individuals. See the visual brief.

## ruling
(empty — owner has not reviewed this race yet)
