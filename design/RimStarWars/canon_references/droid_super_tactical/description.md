# ST-series super tactical droid (repo chassis: ST super tactical — JDS **and** OuterRim)

**defName**: droids are **not xenotypes**. **Two race defs across two donor mods** — the index
names only the first:
- **JDS:** `RSW_DW_Race_JDSCIS_ST_Super_Tactical_Droid` — label "ST Super Tactical Droid"
  (`src/RimStarWars/Droidworks/Defs/Races_JDS.xml:290`). `ParentName="DW_Family_Heavy"`,
  `baseBodySize` **0.7**, `MoveSpeed` **2.0**, `skinShader` **Cutout** (no mask, no colour
  channel), `headTypes` = `RSW_DW_HeadType_Blank`, `DroidworksExtension` with `energyDensity` 2 /
  `chassisClass` 4 / `deliberateDenyModule` true, plus `CompProperties_DroidDetonation`.
  Sprites `JDS/Things/ST_Super_Tactical_Droid{,_south,_east,_north}.png`, 256×256.
- **OuterRim:** `RSW_DW_Race_OuterRim_SuperTacticalDroid` — label "Super Tactical Droid"
  (`Defs/Races_OuterRim.xml:578`), plus HeadTypeDef
  `RSW_DW_HeadType_OuterRim_SuperTacticalDroid` (:48) and PawnKindDef
  `RSW_DW_OuterRim_SuperTacticalDroid` (`Defs/PawnKinds_OuterRim.xml:180`).
  `baseHealthScale` **0.8**, `MoveSpeed` **4.6**, `skinShader` **CutoutComplex** with a
  **three-option random colour palette** (below). Sprites
  `OuterRim/Droid/SuperTactical/{Body/Naked_Male,Head/Head}_{south,east,north}.png`, 512×512.
- **No PawnKindDef found for the JDS race.** The OuterRim one has one; the JDS one does not.

⚠️ **`DROIDS_INDEX.md` names only "ST super tactical (JDS)".** The OuterRim chassis above exists
on disk and is a **second, visually different donor** for the same canon droid. Reporting, not
fixing the index.

## Canon variants this chassis covers

| canon row | continuity | index line | mapped in index? |
|---|---|---|---|
| Super tactical droid | **Legends** | 1627 | ✅ `ST super tactical (JDS)` |
| ST-series military strategic analysis and tactics droid | canon | 1603 | 🔴 **blank** |

🔴 **The index has mapped the Legends row and left its canon counterpart unmapped.** The two
articles carry each other as continuity counterparts (`{{Top|canon=…}}` / `{{Top|legends=…}}`)
and give the **same height, 1.94 m** — they are one droid across the canon/Legends fork. So
`DROIDS_INDEX.md:1603` (`ST-series military strategic analysis and tactics droid`, `canon`,
manufacturer **Baktoid Combat Automata**) **belongs to this chassis and should carry
`ST super tactical (JDS)` in its `in repo` column.** As filed, the repo's only super tactical
droid is bound to the *Legends* row, whose infobox has **no manufacturer at all** — so the
better-sourced canon data is orphaned. This is the same class of miss as the HK entry's wrong
`canon` flag: an index bookkeeping error, not a content error.

Also-known-as, from the canon article: **ST-series super tactical droid**, **ST-series tactical
droid**, **Super Tactical Command Droid**, and simply **super tactical droid**.

Named sub-variants the repo does **not** distinguish (canon infobox `model=`): **Auxiliary
Command Droid** and **Super Tactical Command and Control Droid**.

## Sourced text (Wookieepedia)

The **ST-series military strategic analysis and tactics droid** was an advanced tactical droid
used as an **enhanced version of the T-series military strategic analysis and tactics droid**. In
the **second year of the Clone Wars (20 BBY)**, because of the T-series' "inflexible and
predictable deficiencies," the ST-series was produced by **Baktoid Combat Automata** for the CIS
as a solution.
[ST-series military strategic analysis and tactics droid](https://starwars.fandom.com/wiki/ST-series_military_strategic_analysis_and_tactics_droid)

🔑 **Height: 1.94 meters (6 ft 4 in)** — stated in *both* infoboxes (canon cited to
*The Clone Wars: Character Encyclopedia — Join the Battle!*; Legends to the *Star Wars
Encyclopedia*'s General Kalani entry). **Mass is empty in both.** Class **tactical droid**, degree
**class four droid**. Legends adds gender **masculine programming**.

🔑 **"Taller than their forebears by a single centimeter"** — the ST-series is only **1 cm**
taller than the T-series, "however … **they managed to seem far bigger, dominating a room with an
arrogantly assured presence that the boxy T-series never managed.**" So the difference between
this chassis and a T-series is **build and bearing, not height.** That sentence is the single
most useful line in the article for art purposes.

**Design differences over the T-series, all sourced:**
- **Superior armor plating, particularly on the limbs**, and tougher **neck joints**.
- 🔑 **A third photoreceptor** — "the super tactical droids had a total of **three
  photoreceptors**, which gave them sight to a large range of the light spectrum." This is the
  chassis' most checkable visual signature.
- **Magnatomic grip panels** in the palms and inner hand surfaces, "which allowed them to pick up
  and use **most weapons, tools and equipment made for organic beings**, without dropping them."
- **Greater heat ventilation**: they retained abdominal heat sinks *and* gained "additional
  ventilation holes in their armor on the **sides of their chest units, just below the shoulder
  joints**," because their extra processing power made more heat.
- A **status indicator for their central processing hubs**.
- Vocoders with "a **more threatening robotic voice** than their predecessors," and **more fluid
  motion programming**.

🔑 **Individuality, and it is a colour fact.** "Super tactical droids also **developed their own
personalities.** Some of them, such as General **Kalani**, **gave themselves names instead of
numbers.** They also **often chose their own personalized color schemes and decorations for their
armored bodies**, with **Kalani choosing ornate gold trims to his armor, while Kraken went for a
swirling pattern of gold on his green armor.**" Sourced individual customisation means **there is
no single correct paint job for this chassis** — variation is canon.

**Behaviour.** Programmed to serve as **generals and admirals**; "ruthless and calculating
leaders but still **arrogant and overconfident** like earlier tactical droid models";
"argumentative and operated **without sympathy or morality**." They had complete faith in their
own abilities "to the extent they also believed themselves to be better than the majority of the
organic beings they served," which gave them "the clear conscience to make sacrifices to assure
victory, **even if it meant the loss of allied organic troops and commanders.**" 🔑 **Their
canonical failure mode, stated explicitly:** "while the processor deficiencies of the T-series
made them predictable, the super tactical droids were **so convinced that they were right that
they would dismiss data and tactical options that did not conform to their choices.**" They were
also **resistant to interrogation** (Legends states this too), and would not hesitate to use
**threats and torture** as interrogation means themselves. Rex's assessment in *Rebels*, quoted
in the article: *"It's really bad. That droid's **extremely intelligent.**"*

**Armament** (canon infobox): **E-5 blaster rifle**, **electrostaff**, **heavy arm cannon**. The
Legends infobox lists only the E-5. So this is a **commander that carries organic-issue
weapons** — consistent with the magnatomic grip panels — not an integral-weapon droid.

**Named individuals** (all sourced): Commanders **Aut-O** and **Kraken**, Generals **Kalani**
(who served directly under Count Dooku) and **Linwodo**. Kalani survived to the *Rebels* era in
the **Agamar garrison** of the **Separatist holdouts**. One ST-series unit "**hybridized itself
onto the legs of a droideka**" (image caption, `File:Exterminate-SWQ29_Sergey_Glushakov.png`) —
another canon salvage-hybrid precedent, and a direct link to `droid_droideka`.

⚠️ The canon article is 30,926 chars and carries `{{Update|Master of Evil, …}}` — Wookieepedia's
own incompleteness flag. **Read in full: infobox, lead, Description/Design, Performance.**
The History sections and Appearances are **UNREAD, not absent.** The Legends article (6,480
chars) was **read in full.**

## Provenance

- **Manufacturer:** **Baktoid Combat Automata** (canon infobox, cited to *Ultimate Star Wars*;
  the body text repeats that the CIS "commissioned the battle droid manufacturer, Baktoid Combat
  Automata"). 🔴 **The Legends infobox's `manufacturer=` is EMPTY** — which is why
  `DROIDS_INDEX.md:1627`, the row the repo is mapped to, shows a blank manufacturer while
  line 1603 shows Baktoid. Same droid, one blank row.
- **Era:** **blank.** `firstmade=` and `retired=` are empty in both infoboxes. The article does
  date production to the **second year of the Clone Wars, 20 BBY**, in prose — narrative, not an
  infobox era, and not promoted here.
- **Typical owners:** **Confederacy of Independent Systems** and its **Confederacy military**;
  **Infinite Coil**; **Separatist holdouts**, specifically the **Agamar garrison**. The Legends
  row lists the CIS only. `DROIDS_INDEX.md:1603` matches the canon infobox; `:1627` matches the
  Legends one.
  [ST-series …](https://starwars.fandom.com/wiki/ST-series_military_strategic_analysis_and_tactics_droid) ·
  [Super tactical droid/Legends](https://starwars.fandom.com/wiki/Super_tactical_droid/Legends)

## Visual brief

✅ **Both repo donors get the chassis' one checkable signature right: three photoreceptors.**
This is the rare case in this library where the sprites agree with canon on the detail that
matters most, and it is worth saying plainly.

**`wookieepedia_std_kraken.jpg` is the proportion authority.** What it shows:

- **A tall, lean, distinctly humanoid skeleton** — narrow waist, long thin arms and legs with
  **prominent exposed cylindrical joints at shoulder, elbow, hip, knee and ankle**, and a
  comparatively **broad flat chest plate** with vertical ribbing at the sternum. Nothing about it
  is boxy; the read is *armoured athlete*, which is exactly the "seemed far bigger … arrogantly
  assured presence" the text claims over the T-series.
- **A small rounded head sitting low between high shoulder plates**, with **three glowing
  yellow photoreceptors** — two set wide, one above and between them — and a narrow vertical
  faceplate below.
- **Palette (this unit, Kraken): dark green armour with bright gold swirling patterns** across
  the chest, shoulders, thighs and forehead, over pale grey-white joint hardware. This matches
  the sourced "Kraken went for a swirling pattern of gold on his green armor" exactly — so the
  image is confirming the text, not contradicting it.
- **Hands are long and thin with visible finger segments** (the magnatomic grip panels' housing),
  clearly built to hold an organic-issue rifle.
- **Feet are flat splayed pads**, not boots.

`wookieepedia_std_kalani.jpg` is the **Legends infobox image — General Kalani**, and is the
reference for the *other* sourced paint scheme ("ornate gold trims"). Keep both: **the pair is
the evidence that this chassis has no single canon colour.**

**What the repo sprites show:**

- ✅ **JDS (`donor_current_sprite.png`, 256×256, top-down).** A **blue-grey and tan-brown
  armoured figure** with **three pale photoreceptors** in a triangle on the head, dark shoulder
  blocks to either side, a ribbed central chest panel and a tapering lower body. **Three eyes:
  correct.** The blue-grey-over-tan palette is not either sourced scheme (Kraken's green/gold,
  Kalani's gold trim), but given that canon explicitly licenses **personalised colour schemes**,
  an unattested palette here is **not a canon error** — it is one more customised unit.
- ✅ 🔑 **OuterRim, and this is the best def-side canon match in the batch.**
  `Races_OuterRim.xml:604–640` gives the `skin` channel **three equally-weighted options** —
  `RGBA(130,150,176)` blue-grey, `RGBA(155,171,132)` **olive-green**, `RGBA(163,127,111)`
  tan-brown — so **every spawned OuterRim super tactical droid rolls a different armour colour.**
  That is a direct mechanical expression of the sourced fact that these droids "often chose their
  own personalized color schemes." The olive-green option in particular lands close to Kraken.
  **Do not "fix" this to a single colour: the randomisation is the canon-correct behaviour.**
- ✅ `donor_outerrim_head_south.png` (512×512) also carries **three cream photoreceptors** in the
  canon triangle arrangement, on a faceted grey helmet-like head with a narrow vertical
  faceplate. Closest thing in the repo to the canon head.
- ⚠️ **The gold trim/swirl decoration is absent from both donors.** Canon's two attested units
  are *both* gold-decorated, and it is the cue that reads "this one is a named general" rather
  than "this one is a droid." A gold accent pass is the cheapest way to make an ST-series pawn
  read as a commander.
- ⚠️ **The chest ventilation holes below the shoulder joints** — a sourced ST-only feature — are
  not distinguishable in either sprite.
- 🔴 **The two donors' stats disagree sharply, and the JDS one looks wrong.** JDS: `MoveSpeed`
  **2.0**, `baseBodySize` **0.7**. OuterRim: `MoveSpeed` **4.6**, `baseHealthScale` **0.8**.
  Canon gives the ST-series "**more fluid motion programming than the T-series**" and a build
  described as athletic rather than boxy — so **2.0 (slower than the OuterRim T-series line and
  as slow as a B1) contradicts the sourced text**, while 4.6 supports it. Flagging, not fixing.
- ⚠️ **`baseBodySize` 0.7 on the JDS race** for a droid canon states at **1.94 m** — a hair
  taller than a tall human. Note the JDS file gives the **B2 super battle droid the same 0.7**,
  so 0.7 appears to be a JDS-wide default rather than a considered value for this chassis.
- ⚠️ **JDS `skinShader` is `Cutout`** — no mask, no colour channel — so **that sprite's pixels
  are its shipping appearance and it can never roll a colour**, unlike its OuterRim twin.


## Must show
- [ ] Three glowing yellow/cream photoreceptors in a triangle arrangement on the head
- [ ] Tall, lean, humanoid frame with prominent exposed cylindrical joints at shoulder, elbow, hip, knee, and ankle
- [ ] Broad flat chest plate with vertical ribbing at the sternum
- [ ] Gold swirling/trim decoration on named-commander units

## Engine limits
The JDS variant's `skinShader` is `Cutout` with no mask and no colour channel, so that sprite's pixels are its shipping appearance and it can never roll a colour — unlike its OuterRim twin, which uses `CutoutComplex` with a three-option palette.

## Source URLs

- https://starwars.fandom.com/wiki/ST-series_military_strategic_analysis_and_tactics_droid —
  canon article; wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=ST-series_military_strategic_analysis_and_tactics_droid&format=json&prop=wikitext`
  (30,926 chars; infobox + lead + Description/Design + Performance read, **History and
  Appearances unread**). Rendered HTML is Cloudflare-walled; the API is not.
- https://starwars.fandom.com/wiki/Super_tactical_droid/Legends — Legends article, same API
  pattern (6,480 chars, **read in full**)
- https://static.wikia.nocookie.net/starwars/images/1/1d/KrakenFull-BYOR2D2-51.png
  (File:KrakenFull-BYOR2D2-51.png → `wookieepedia_std_kraken.jpg`) — the canon article's infobox
  image
- https://static.wikia.nocookie.net/starwars/images/1/15/GeneralKalaniFull-SWE.png
  (File:GeneralKalaniFull-SWE.png → `wookieepedia_std_kalani.jpg`) — the Legends article's
  infobox image
- ⚠️ **Deliberately NOT downloaded:**
  `https://static.wikia.nocookie.net/starwars/images/2/24/SuperTacticalDroid-SWL2024update.png`
  is **3840×2690** — over the 2000px viewing limit in the agent brief. Recorded here so a later
  pass can fetch and downscale it rather than rediscover it.
- Named in the articles, **not fetched this pass**:
  https://starwars.fandom.com/wiki/Auxiliary_Command_Droid ·
  https://starwars.fandom.com/wiki/Super_Tactical_Command_and_Control_Droid ·
  https://starwars.fandom.com/wiki/Kalani · https://starwars.fandom.com/wiki/Kraken ·
  https://starwars.fandom.com/wiki/Aut-O ·
  https://starwars.fandom.com/wiki/T-series_military_strategic_analysis_and_tactics_droid
  (the direct predecessor — relevant to `droid_t1_tactical`, see that entry)
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_JDS.xml` (generated by
  `src/RimStarWars/Droidworks/Source/gen_droidworks_defs.py`),
  `Defs/Races_OuterRim.xml`, `Defs/PawnKinds_OuterRim.xml`

## Candidate images

- `wookieepedia_std_kraken.jpg` (1080×1895) — Commander **Kraken**, full-body three-quarter
  render on transparent background. **The proportion authority**, and the reference for the
  sourced green-with-gold-swirls scheme. Three glowing yellow photoreceptors clearly visible.
- `wookieepedia_std_kalani.jpg` (700×1170) — General **Kalani**, the Legends infobox render. The
  reference for the *other* sourced scheme (gold trim). **Kept as a second positive reference
  precisely because it differs** — canon licenses per-unit colour.
- `donor_current_sprite.png` (256×256) — repo **JDS** sprite, `south`/top-down. Judge literally:
  `skinShader` is `Cutout`, no tint applied. **Three photoreceptors present.**
- `donor_body_east.png` (256×256) — the JDS profile frame.
- `donor_outerrim_body_south.png` / `donor_outerrim_head_south.png` (512×512 each) — the separate
  **OuterRim** donor. **Must be judged tinted**, rolling one of the def's three colour options;
  the head carries three photoreceptors.

## ruling

(empty — the owner has not reviewed this chassis yet)
