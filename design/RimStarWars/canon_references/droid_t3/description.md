# T3 (KotOR)

**defName**: a race + pawnkind pair, not a xenotype. Real defs on disk:
- `RSW_DW_Race_guy762_DroidRace_T3series` — label "T3-series utility droid"
  (`src/RimStarWars/Droidworks/Defs/Races_KotOR.xml:666`), parent `DW_Family_Astromech`
- `RSW_DW_KotORDroidColonist_T3UD` (`Defs/PawnKinds_KotOR.xml:8`)
- `RSW_DW_KotORPlayableHero_T3M4` (`Defs/PawnKinds_KotOR.xml:459`) — the named hero unit
- Head type: `RSW_DW_HeadType_Blank` (headless; the whole droid is one body sprite)

Sprite: `src/RimStarWars/Droidworks/Textures/KotOR/Droid/T3/T3_{north,south,east,west}.png`
plus `T3_mask_*` for all four facings.

## Canon variants this one repo chassis covers
- **T3-series utility droid** — the only canon row assigned to this chassis

Sibling series that Wookieepedia treats as separate models and the repo also carries as their
own races (out of this entry's scope, listed so the boundary is clear):
`RSW_DW_Race_guy762_DroidRace_3Cseries` (3C-series) and
`RSW_DW_Race_guy762_DroidRace_ITseries` (IT-series).

## Sourced text (Wookieepedia)

The **T3-series utility droid** was a **maintenance droid** produced by **Duwani Mechanical
Products** at some point prior to the Great Droid Revolution. It remained popular for years;
after roughly **130 years in use** it was still the most recent of a long line of
**physically identical** models as of **3956 BBY**. Earlier models in the same series were the
**3C**, **IT** and **T1**. The T3 was internally more advanced than its predecessors but not
outwardly different.
[T3-series utility droid](https://starwars.fandom.com/wiki/T3-series_utility_droid)

**Sourced infobox figures** (all from `The New Essential Guide to Droids` via the article's
`{{DroidSeries}}` box; nothing here is inferred):
- **Class:** maintenance droid
- **Height: 0.96 metres**
- **Cost: 3,500 credits**
- **Sensor colour: blue, yellow, and red**
- **Plating: brown; silver**
- **Armament: variable**
- **Equipment:** tool access port · auditory and sonar scanner · radar eye · radionic sensor ·
  multi-function arm
- `firstmade` / `retired`: **both blank** → no era, per the brief
- `mass`, `length`, `width`, `homeworld`, `affiliation`: **all blank** → unsourced, recorded as
  absent rather than guessed

**Body plan, verbatim in substance from the article's Characteristics section:**
- **Four wheeled legs.** The **front two** are attached to the blocky chassis by **rotating
  joints, allowing the droid to slide backwards and forwards to adjust the unit's height.**
- A **roughly toroidal head** carrying **one large main photoreceptor plus two secondary
  ones**, a **broadcast antenna**, and a **vocabulator** — it speaks only **Droidspeak
  (Binary)**, not Basic.
- Optimum performance **aboard starships**; designed for repair and general maintenance of
  mechanical and electronic systems.
- Loaded mechanical/computer training software let it act as an **engineer or even a copilot**,
  making it a favoured purchase for **traders and smugglers**.
- **Common modification:** a **starfighter interface package** letting it plug into a
  specialised starfighter slot. **Duwani did not endorse this**, but fighter pilots insisted on
  it as a survivability measure (`Knights of the Old Republic Campaign Guide`).
- **Some custom units carried weapon mounts** for readily available blaster pistols — the
  article calls this "an unusual feature for a droid designed for everyday tasks."

**⭐ Directly relevant to this repo's memory-wipe and personality-drift design, and sourced:**
*"Without periodic memory wipes, these models developed personality and behavioral traits. It
was even known for some units to form gangs, making a living as thieves. Others sold their
computer-slicing skills to criminals."* The article also opens with a `Trampeta's Star Guide`
quote, circa **4086 BBY**: *"TARIS: We received a dreadful welcome when T3 droids at the
starport made off with our baggage."* So T3s stealing from travellers is canon flavour, not an
invention — a good hook for a scavenger-clan campaign.

**History:** the famous unit is **T3-M4**, a prototype of an upgraded T3 that Duwani introduced
prior to the **Jedi Civil War**. By the Galactic Alliance era, surviving T3s were "seldom found
outside of private collections."

**⚠️ Continuity status: this article is explicitly Legends** — it opens
`{{Top|leg|canon=Unidentified maintenance droid (ML-08)}}`, and it also carries a
`{{Citation}}` maintenance banner, meaning the wiki itself flags parts of it as
under-referenced. `DROIDS_INDEX.md:1651` marks this row `canon`; that column value is wrong
for this row. Everything above should be read as **Legends**, and the canon counterpart is an
unnamed background droid (`Unidentified maintenance droid (ML-08)`), which will carry almost no
description. **This chassis' design therefore rests on KotOR game assets and Legends
sourcebooks, not on canon description.**

## Provenance
- **Manufacturer:** **Duwani Mechanical Products**
  [T3-series utility droid](https://starwars.fandom.com/wiki/T3-series_utility_droid)
  (the article also carries `Category:Duwani Mechanical Products products`)
- **Era:** **blank.** The infobox's `firstmade` and `retired` fields are both empty. The
  article does give sourced *relative* anchors — produced before the Great Droid Revolution,
  in use ~130 years by **3956 BBY**, T3s attested at Taris circa **4086 BBY**, T3-M4 introduced
  before the Jedi Civil War, near-extinct by the Galactic Alliance era — but no era field, so
  this stays blank per the brief.
- **Typical owners:** the infobox `affiliation` field is **blank**. What the body text
  actually attests: **starport operators** (Taris), **traders and smugglers** (the article
  names them as the favoured buyers), **starfighter pilots** (via the unendorsed interface
  package), **criminals** buying slicing services from unwiped units, and later **private
  collectors**. `DROIDS_INDEX.md:1651` also leaves the owners column blank for this row.
  [T3-series utility droid](https://starwars.fandom.com/wiki/T3-series_utility_droid)

## Visual brief

**🔴 The repo tints this droid the wrong colour, and the def says so in a number.**
`Races_KotOR.xml:686–697` sets the single `skin` colour channel to **`RGBA(235,255,255,255)`** —
a near-white, very slightly cyan-tinted off-white. The canon infobox `plating` field is
**"Brown" and "Silver"**, and `wookieepedia_t3m4_infobox.jpg` confirms it emphatically: T3-M4
is a **heavily weathered, dirty brown-and-tan machine** with a dull mauve-brown dome top,
oxidised bronze accents and a lot of grime in the panel lines. The sprite reads as a clean
white appliance. This is the single most useful correction on this chassis.

**Where the sprite is right:**
- **The photoreceptor cluster is correct in kind and in colour count.** The donor sprite shows
  **one large blue main lens** with a bright cyan-white core, plus a **small yellow** and a
  **small orange** secondary lamp to its right — three sensors, matching both the text's "a
  large main photoreceptor and two secondary ones" and the infobox's **"Blue, yellow, and
  red"** sensor colours. (Canon renders show the main lens closer to **teal/green** than pure
  blue; the infobox field says blue, so the sprite is defensible.)
- **The broadcast antenna is present** — a thin hooked stalk rising off the back-left of the
  dome, matching the antenna in both canon images.
- **The toroidal/dome head over a blocky body** silhouette is right, and the head sits low and
  wide as it should.
- **Headless by design is correct here.** The def wires `RSW_DW_HeadType_Blank`, so the whole
  droid is one body texture — appropriate for a droid whose "head" is a fused dome, not a
  separate rotating unit.

**Where the sprite is thin or diverges:**
- **Leg count reads as two, not four.** Canon is unambiguous: **four wheeled legs**, front two
  on rotating joints. The south-facing sprite shows a pair of tall thin outer legs plus a
  central body panel; the rear pair is not readable. Whether that is occlusion or omission
  cannot be settled from one facing.
- **The wheels are not readable at all.** Canon T3 walks on **wheeled** feet — the infobox
  render shows big splayed pad-feet with wheel housings, and the KotOR-2 render shows large
  visible wheel discs at the hip. The sprite's feet are plain rounded stubs.
- **No sliding-height mechanism is legible.** That is arguably unfixable in a top-down sprite,
  but it means the chassis' most distinctive mechanical trait is absent.
- **Detail density is far lower** than canon: canon T3 is covered in exposed frame trusses,
  strut work, hydraulic runs and an open central bay with a visible manipulator arm poking out
  of the chest. The sprite has flat grey panels and a suggestion of a central column. **The
  multi-function arm / tool access port** — both named canon equipment, and both visible in
  the infobox render as a jointed arm emerging from the chest cavity — do not appear.
- The sprite is drawn as a **maskable asset** (`T3_mask_*` exists for all four facings), so it
  is designed to be recoloured. Correcting the brown/silver problem is a def colour change, not
  necessarily a repaint.

`wookieepedia_t3_schematics.svg` is kept as a **line-drawing reference for proportion and leg
geometry** — it is the clearest source for the four-leg arrangement. It is an SVG (nominal
2406×974) and was **not viewed** in this pass; treat it as unverified-by-eye but retained
because it is the only orthographic reference available.

## Must show
- [ ] One large main photoreceptor lens plus two smaller secondary lamps (three sensors total)
- [ ] Broadcast antenna: thin hooked stalk rising off the back of the dome
- [ ] Toroidal/dome head sitting low and wide over a blocky body
- [ ] Brown-and-tan weathered plating, not white/cyan-tinted

## Engine limits
Only a single `skin` colour channel is defined — it can drive one hue, so it cannot express canon's two-tone brown-and-silver plating through tinting alone; a second channel or new art would be needed.

## Source URLs
- https://starwars.fandom.com/wiki/T3-series_utility_droid — main article; text pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=T3-series_utility_droid&format=json&prop=wikitext`
  (5,579 chars of wikitext, read in full — no truncation)
- https://static.wikia.nocookie.net/starwars/images/2/2e/T3M4-NEGD.png → `wookieepedia_t3m4_infobox.jpg`
- https://static.wikia.nocookie.net/starwars/images/2/2e/T3M4_kotor2.jpg → `wookieepedia_t3m4_kotor2.jpg`
- https://static.wikia.nocookie.net/starwars/images/6/65/T3-schematics.svg → `wookieepedia_t3_schematics.svg`
- Named in the article but **not fetched this pass**: `Unidentified maintenance droid (ML-08)`
  (the canon counterpart), `T3-M4`, `3C-series utility droid`, `IT-series utility droid`,
  `T1-series utility droid`, https://www.starwars.com/databank/t3m4
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_KotOR.xml`,
  `src/RimStarWars/Droidworks/Defs/PawnKinds_KotOR.xml`

## Candidate images
- `wookieepedia_t3m4_infobox.jpg` (1135×1200) — the `{{DroidSeries}}` infobox render of T3-M4,
  three-quarter view on white. **The primary colour and detail reference.** Shows the weathered
  brown/tan plating, mauve-brown dome, teal main photoreceptor with two small secondary lamps,
  antenna, four splayed wheeled feet, exposed frame trusses, and a manipulator arm out of the
  chest bay.
- `wookieepedia_t3m4_kotor2.jpg` (945×945) — T3-M4 in a KotOR II render; a second angle
  agreeing on colour and on the wheel/leg arrangement.
- `wookieepedia_t3_schematics.svg` (2406×974 nominal) — orthographic schematic line drawing;
  the clearest reference for the four-leg geometry. **Not viewed** (SVG, oversize) — retained
  unverified.
- `donor_current_sprite.png` (512×512) — the repo's `T3_south` donor. Near-white/pale grey
  plating with a blue main lens plus yellow and orange secondaries and a hooked antenna.
  Maskable (`T3_mask_south` exists).

## ruling
(empty — the owner has not reviewed this chassis yet)
