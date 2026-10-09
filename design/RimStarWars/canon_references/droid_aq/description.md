# AQ-series battle droid / aqua droid (repo chassis: AQ battle droid, JDS)

**defName**: not a xenotype. Real defs on disk:
- `RSW_DW_Race_JDSCIS_AQ_Battle_Droid` — label **"AQ Battle Droid"**,
  `ParentName="DW_Family_Battle"`, `baseHealthScale` **1.5**, `MoveSpeed` **1.7**,
  `headTypes` = `RSW_DW_HeadType_Blank` (one body sprite, no separate head asset) —
  `src/RimStarWars/Droidworks/Defs/Races_JDS.xml:422`
- `RSW_DW_JDSCIS_AQ_Battle_Droid` — PawnKindDef, `combatPower` **45**, `weaponTags`
  `AQ_Battle_Blaster`, `forcedTraits` `ShootingAccuracy -1`
  (`src/RimStarWars/Droidworks/Defs/PawnKinds_JDS.xml:225`)
- `DroidworksExtension`: `powerFallPerDay` 1.0, `energyDensity` **0**, `chassisClass` **3**,
  `deliberateDenyModule` true

Sprites: `src/RimStarWars/Droidworks/Textures/JDS/Things/AQ_Battle_Droid_{south,east,north}.png`
plus a duplicate `AQ_Battle_Droid.png` (byte-identical to `_south`), **320×320**.

🔴 **This chassis has NO `colorChannels` and no mask files** — unlike the OuterRim and KotOR
donors in this batch, its colour is **baked into the PNG**. So every colour finding below is
a **repaint**, not a one-line def edit. That is the single most important practical
difference between this entry and the other four.

⚠️ **Repo inconsistency, not a canon matter:** the def carries
`CompProperties_DroidDetonation` under the rollout comment "*every `energyDensity>0` race
gets this*", but this race's `energyDensity` is **0**. Noted for whoever owns
`DROIDWORKS_DETONATION_ROLLOUT_1`; it is outside this library's remit and is **not** a
canon contradiction.

## Canon variants this one repo chassis covers

- **AQ-series battle droid** — the only canon row (`DROIDS_INDEX.md:218`).

✅ **The index's continuity column is RIGHT for this row** — the one row in this batch that
is. `DROIDS_INDEX.md:218` marks it `canon`, and the article opens
`{{Top|legends=Aqua droid/Legends}}`, i.e. this *is* the canon article and its Legends
counterpart is the separate page `Aqua droid/Legends` (**not fetched this pass**, and not in
scope for this chassis).

⚠️ **Name trap.** The article carries `{{Youmay|the aqua droid of the Separatist Droid
Army|the [[aquatic battle droid]] seen on [[Glee Anselm]]}}` — the **aquatic battle droid** is
a **different model**. Do not merge them.

**One sourced sub-variant the repo does not have:** "The **heavy aqua droid** variant existed
which had an **integrated missile launcher on the right arm**, similar to the **B2-HA super
battle droid**." One repo sprite currently serves both the standard and heavy readings.

## Sourced text (Wookieepedia)

**AQ-series battle droids, more commonly known as aqua droids**, "were an **amphibious** model
of **battle droid** and **droid tank** manufactured by **Haor Chall Engineering Corporation**.
They were **excellent swimmers**, possessed a **retractable laser cannon on their right
wrist**, and were used by the **Confederacy of Independent Systems to lay siege to aquatic
planets such as Kamino and Mon Cala** during the Clone Wars."
[AQ-series battle droid](https://starwars.fandom.com/wiki/AQ-series_battle_droid)

🔑 **Origin: it is a converted B2, not a B1 derivative.** "The aqua droid was created by the
**Techno Union**, which made the droid by **adapting the B2-series super battle droid for
underwater warfare**." Compared to a B1 it "had a **bulkier physique**… boasting a **massive
chest with ridged shoulders**, **elongated legs**, a **polygon shaped head which could be
retracted into the droid's body to reduce drag while swimming**, and a **set of feet that
could switch between a standard walking stance on land or fold into propellers
underwater**." It also used **less metal** in production than a B2.

🔑 **Two modes, and the repo has only one.** Like the droideka's ball form, the AQ's
**swimming mode** is a genuinely different silhouette — head retracted, body horizontal and
streamlined, feet folded into propeller blades. "Underwater, the aqua droids were **more
streamlined and agile** than their B2 model cousins were on land."

🔑 **On land it is slow and it is a sniper magnet.** "Despite being incredibly mobile
underwater, the droids **marched in a slow lumbering pattern similar to super battle droids
while operating on land, which made them targets for enemy snipers.**" The repo's
`MoveSpeed 1.7` — among the slowest in the mod — reproduces this exactly. **Do not speed it
up.**

Armament, sourced: a **single retractable laser cannon on the right wrist**; the bulky arms
themselves used as melee weapons "to execute sufficient damage against enemy vehicles, such
as Kamino submarines, underwater"; and on more heavily armoured models, **grenade launchers
or missile launchers**.

Infobox fields: `creator` **Techno Union**; `manufacturer` **Haor Chall Engineering
Corporation**; `class` **Battle droid** *and* **Droid tank**; `height` **2.83 meters
(9 ft 3 in)**; `gender` **Masculine programming**; `sensor` **Red**; `plating` **Gray**;
`armament` retractable laser cannon (1) + grenade or missile launcher (1); `equipment`
**Propellers (2)**; `affiliation` **Confederacy of Independent Systems → Separatist Droid
Army**.

History, summarised from the article's own two sections:

- **Battle of Kamino, 21 BBY.** Deployed secretly under **Asajj Ventress**; Separatist
  support-ship debris dropped **Trident-class assault ships** into the ocean which the aqua
  droids **assembled underwater**. They swarmed Obi-Wan Kenobi's submarine and disabled its
  engines; he escaped on an **aiwha**. They then drilled into **Tipoca City**, dispensing aqua
  droids and B1s inside, as a diversion for Ventress' attempt on **Jango Fett's genetic
  template**. Pushed back by clone forces.
- **Battle of Mon Cala, 20 BBY.** **Riff Tamson's** army of aqua droids fought alongside
  defecting **Quarren** against the Mon Calamari; reinforced by **hydroid medusas**. Aqua
  droids became **prisoner-camp guards** and search parties hunting Prince Lee-Char.
- Later listed in **"Neyo's Almanac of Clankers,"** a clone survival compendium, in an entry
  written by Commander **Monnk**.

⚠️ **The article is flagged `{{Droid-stub}}`** despite its length. Its `{{ScrollBox}}`
*Appearances* section (~3.1 KB) was **not read** — UNREAD, not absent.

**Unsourced and therefore absent:** mass, length, width, cost, homeworld, designer, degree,
`firstmade` / `retired`.

## Provenance

- **Manufacturer:** **Haor Chall Engineering Corporation** (infobox `manufacturer`, and
  repeated twice in the body), with the **Techno Union** as `creator` — the Techno Union
  designed it by adapting the B2, Haor Chall built it. Both cited to *Star Wars: The Clone
  Wars: Character Encyclopedia — Join the Battle!*; the Techno Union attribution is
  additionally cited to *Understanding Robotics*. `DROIDS_INDEX.md:218` carries Haor Chall and
  omits the Techno Union — the index is incomplete here rather than wrong.
  [AQ-series battle droid](https://starwars.fandom.com/wiki/AQ-series_battle_droid)
- **Era:** **blank.** `firstmade` and `retired` are both empty in the infobox. Cited dated
  events, not promoted into this field: **Battle of Kamino 21 BBY**, **Battle of Mon Cala
  20 BBY** — i.e. mid-Clone Wars. `DROIDS_INDEX.md:218` also carries a blank era.
- **Era (from article prose) *(prose pass 2026-10-03)*:** first seen deployed at Kamino in **21 BBY**, and again at Mon Cala in **20 BBY** (article body, History). No production date is stated; the field stays blank. [AQ-series battle droid](https://starwars.fandom.com/wiki/AQ-series_battle_droid)
- **Typical owners:** **Confederacy of Independent Systems**, specifically the **Separatist
  Droid Army**. Named individual commanders: **Asajj Ventress** (Kamino) and **Riff Tamson**
  (Mon Cala), with **Count Dooku** sending the Mon Cala reinforcements. Allied troops:
  **Quarren** defectors. No civilian, species or scavenger owner is recorded anywhere in the
  article. This is the most narrowly-owned chassis of the five in this batch — a pure
  Separatist military asset.
  [AQ-series battle droid](https://starwars.fandom.com/wiki/AQ-series_battle_droid)

## Visual brief

**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."**

**Animation-only canon — no realistic source found (searched: Wookieepedia `AQ-series battle droid`, `Aqua droid/Legends`, `Images of aqua droids` — every screen image is The Clone Wars / Gungan Attack 3D animation; no live-action, photoreal game or databank render exists).** The images below are animated/stylised; render this droid realistically anyway — real-world anatomy, materials and lighting, not the cartoon's flat shading or exaggerated proportions.

Removed 2026-10-08: the two Clone Wars battle frames `wookieepedia_kamino_siege.png` and `wookieepedia_tamson_moncala.png` (low-detail scene shots, the second tinted blue by water). Kept: the Clone Wars CGI turnaround (`wookieepedia_infobox.png`) and swim-mode render, plus a **photograph of the painted physical Star Wars: Legion miniatures** (`wookieepedia_legion_miniatures.png`) — the only real-object depiction. The miniature agrees with the render on silhouette and colour: brushed pale silver-grey plating, **pale ice-blue trim lines** along the panel edges of the shoulder yoke, forearms and shins, dark gunmetal joints and hands, red lens. Read the metal as real weathered brushed steel, not the render's soft airbrushed gradients.

🔴 **The repo sprite is far too DARK, and it has none of the blue.** This is the headline
finding, and it is a repaint.

- The canon render (`wookieepedia_infobox.png`) is **pale grey-white / near-white**, a
  cold light plating with soft grey shading. The infobox agrees: `plating = Gray`.
- The article body adds: "The droids were also **given a blue color scheme to match the
  waters they were designed to operate in**," and the swimming-mode render
  (`wookieepedia_swimming_mode.png`) bears this out — distinct **teal / blue-green panels**
  on the shoulder shroud and around the head.
- 🔑 **The infobox and the body text are reconcilable, not contradictory** (both cite the
  same episode, "ARC Troopers"): the droid is **light grey plating with teal-blue accent
  panels.** Read together with the images, that is the answer — not "grey" and not "blue."
  Underwater battle frames read overwhelmingly blue from the water lighting, not the plating; the infobox render and the Legion miniature both show pale grey with ice-blue trim.
- The repo sprite (`donor_current_sprite.png`) is **dark charcoal / gunmetal**, several stops
  darker than any canon reference, with **zero teal or blue anywhere**. It reads as a black
  droid. Correcting it means lightening the body substantially **and** adding the teal accent
  panels — and because there is no mask, that is art work, not a def value.

✅ **The red eye is right, and it is the sprite's best feature.** Infobox `sensor = Red`; both
clean renders show a **red visor slit / red lens** in the small polygonal head; the sprite
carries a **bright red vertical slit** in exactly the right place. Keep it.

**Silhouette agreement is genuinely good** — better than the colour suggests:

- Canon is a **wide swept shoulder yoke** projecting well past the body on both sides, above
  a **narrow tapering segmented torso**. The sprite reproduces both: broad swept wing-like
  shoulder planes and a ribbed tapering torso beneath.
- Canon's **small polygonal head sits recessed between the shoulders**, not above them. The
  sprite gets this right too.
- Canon's **elongated legs and large splayed feet** are the model's most distinctive lower
  feature, and the feet are functionally important (they **fold into propellers**). The
  sprite shows no legs and no feet — only two dark rounded masses low on the body reading as
  fists. Partly a top-down format constraint, but the AQ is 2.83 m of mostly *leg*, so this
  is a bigger loss here than on a squat chassis.
- **The retractable wrist cannon is not depicted.** Canon puts it on the **right** wrist; the
  clean render shows a cylindrical barrel housing on one forearm. The sprite has no barrel,
  no hardpoint, and no asymmetry between the arms. The def instead grants a `weaponTags`
  entry `AQ_Battle_Blaster` — so the weapon is a held item in-game rather than part of the
  chassis, which is a defensible RimWorld choice but does mean the canon *built-in* cannon
  reads nowhere.

🔴 **Swimming mode does not exist on disk, in any direction.** Same class of gap as the
droideka's ball form: the head-retracted, horizontal, propeller-footed swim configuration is
a **second silhouette sharing nothing with the standing one**, and it is half of what makes
this droid the AQ rather than a repainted B2. `wookieepedia_swimming_mode.png` is the only
reference for it. It would need a second graphic set plus a state to switch on.

⚠️ **`donor_contactsheet.png` (128×128) is not the shipping asset.** It is
`design/Jawa/fauna/sprites/JDSCIS_AQ_Battle_Droid.png`, and its md5 differs from
`AQ_Battle_Droid_south.png` (128×128 vs 320×320) — a downscaled contact-sheet copy. Judge
from `donor_current_sprite.png`.

**Campaign note, flagged rather than decided.** This droid's entire sourced identity is
**water** — amphibious classification, propeller feet, streamlined swim mode, Kamino and Mon
Cala, "to match the waters they were designed to operate in." On a **desert world** it can
only be a scavenged import or a wreck, and its two most canon-distinctive features (swim mode,
propeller feet) are unusable there. That is a legitimate scavenger-clan story — a
Separatist amphibious asset stranded where its whole design is pointless — but it should be a
**conscious** choice, and the owner's ruling, not an accident of which donor mod happened to
carry the sprite.

## Must show
*Rewritten 2026-10-09 to the canon_check leniency lesson (`Transient/canon_check_leniency_2026-10-09.md`): chassis, finish/colour layout and a negative, each checkable on a 256px sprite. Grounded in the Clone Wars CGI infobox turnaround, the swim-mode render and the Legion miniatures photograph, as described in the visual brief.*
- [ ] CHASSIS: a tall bipedal battle droid (2.83 m, mostly leg): a wide swept shoulder yoke projecting well past the body on both sides, over a narrow tapering segmented torso; elongated legs ending in large splayed feet
- [ ] Small polygonal head recessed between the shoulders, not projecting above them, with a bright red visor slit/lens
- [ ] FINISH / COLOUR LAYOUT: pale grey-white plating over the whole body with teal/blue-green (ice-blue) accent panels and trim lines along the shoulder yoke, forearms, shins and around the head; dark gunmetal joints and hands; not solid grey or solid blue
- [ ] Retractable cannon/barrel visible on the right wrist (an asymmetry between the arms)
- [ ] Realistic rendering: brushed weathered steel plating, real metal specular and lighting, no outlines, no cartoon shading (owner ruling 2026-10-08: "That's realistic, not these cartoon versions you keep using.")
- [ ] NEGATIVE: not a dark charcoal/gunmetal black droid (the current donor); not a plain B2 super battle droid (no recessed polygonal head, no swept yoke, short legs); not the different aquatic battle droid of Glee Anselm

## Engine limits
No `colorChannels` block or mask file on this chassis — colour is baked directly into the PNG, so correcting the colour requires a repaint (new art), not a def edit.

## Source URLs

- https://starwars.fandom.com/wiki/AQ-series_battle_droid — main article; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=AQ-series_battle_droid&format=json&prop=wikitext`
  (14,128 bytes of JSON). Sections read in full: `{{Top}}`, `{{Youmay}}`,
  `{{DroidSeries}}` infobox, the Ventress quote, lead, *Description*, *History* (both
  Battle of Kamino and Battle of Mon Cala). **Not read:** the `{{ScrollBox}}` *Appearances*
  section (~3.1 KB) — **UNREAD, not absent.** Rendered HTML is Cloudflare-walled; the API is
  not.
- https://static.wikia.nocookie.net/starwars/images/e/e9/Aqua_droid-SW_Card_Trader.png
  (File:Aqua droid-SW Card Trader.png, **1850×2740**) → `wookieepedia_infobox.png`
  ⚠️ **Over 2000px — do not open directly.** Viewed as a 945×1400 copy at
  `/tmp/aq_infobox_small.png`; the full-size original is kept here as the reference asset.
- https://static.wikia.nocookie.net/starwars/images/6/6d/AquaDroid-TCWs4BR1.png
  (File:AquaDroid-TCWs4BR1.png, 1000×400) → `wookieepedia_swimming_mode.png`
- Named in the article but **not fetched this pass**:
  https://starwars.fandom.com/wiki/Aqua_droid/Legends (the Legends counterpart),
  https://starwars.fandom.com/wiki/Aquatic_battle_droid (the different, similarly-named
  model), `B2-HA super battle droid` (the heavy variant's stated analogue),
  `Haor Chall Engineering Corporation`, `Techno Union`, `Droid tank`, `Trident-class assault
  ship`
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_JDS.xml`,
  `src/RimStarWars/Droidworks/Defs/PawnKinds_JDS.xml`

## Candidate images

- `wookieepedia_infobox.png` (**1850×2740 — downscale before viewing**) — The Clone Wars CGI (animated) model render, file `Aqua droid-SW Card Trader.png` — https://static.wikia.nocookie.net/starwars/images/e/e9/Aqua_droid-SW_Card_Trader.png — the article infobox:
  full-body three-quarter render on transparent background, standing/land mode. **Pale
  grey-white plating**, wide swept ridged shoulder yoke, small polygonal head recessed
  between the shoulders with a **red visor slit**, narrow segmented torso, very long legs,
  large splayed feet, a cylindrical cannon housing on one forearm. **The primary colour and
  proportion authority.**
- `wookieepedia_swimming_mode.png` (1000×400) — The Clone Wars (animated) promo render, file `AquaDroid-TCWs4BR1.png` — https://static.wikia.nocookie.net/starwars/images/6/6d/AquaDroid-TCWs4BR1.png — the **swimming-mode** render: head retracted,
  body horizontal and streamlined, arms folded back, feet folded into propeller blades. Shows
  the **teal / blue-green accent panels** most clearly, plus the red lens. **The only
  reference for the second silhouette, and the blue-accent authority.**
- `wookieepedia_legion_miniatures.png` (1800×1850) — photograph of the painted physical Star Wars: Legion *Aqua Droids Unit Expansion* miniatures (real object, not animation); file `SWQ136-Miniatures1.png` — https://static.wikia.nocookie.net/starwars/images/d/de/SWQ136-Miniatures1.png/revision/latest?cb=20250705204524 . Best evidence for real metal materials and the ice-blue trim lines.
- `donor_current_sprite.png` (320×320) — the shipping repo sprite
  (`Textures/JDS/Things/AQ_Battle_Droid_south.png`, byte-identical). **Dark charcoal, no
  mask, no colour channels** — colour is baked in. Correct swept-shoulder silhouette and
  correct red eye slit; wrong value and missing the teal.
- `donor_contactsheet.png` (128×128) — `design/Jawa/fauna/sprites/JDSCIS_AQ_Battle_Droid.png`.
  **Not byte-identical** to the shipping texture; a downscaled contact-sheet copy. Weak
  evidence.

## ruling

(empty — the owner has not reviewed this chassis yet)
