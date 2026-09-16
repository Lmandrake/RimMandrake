# T1 tactical (JDS) — 🔴 **the index has this chassis mapped to the WRONG canon droid**

**defName**: droids are **not xenotypes**. One race def on disk:
- `RSW_DW_Race_JDSCIS_T1_Tactical_Droid` — label "T1 Tactical Droid",
  `src/RimStarWars/Droidworks/Defs/Races_JDS.xml:246`. `ParentName="DW_Family_Heavy"`,
  `baseBodySize` **0.7**, `MoveSpeed` **2.0**, `skinShader` **Cutout** (no mask, no colour
  channel), `headTypes` = `RSW_DW_HeadType_Blank`, `DroidworksExtension` with `energyDensity` 2 /
  `chassisClass` 4 / `deliberateDenyModule` true, plus `CompProperties_DroidDetonation`.
  Absorbed from `JDS_Separatists` (`JDSCIS_T1_Tactical_Droid`) — i.e. a **Separatist** donor mod.
- **No PawnKindDef found** for this race anywhere in `src/RimStarWars/`.
- Sprites: `src/RimStarWars/Droidworks/Textures/JDS/Things/T1_Tactical_Droid{,_south,_east,_north}.png`,
  256×256.

`Races_JDS.xml` is **generated** by `src/RimStarWars/Droidworks/Source/gen_droidworks_defs.py`.

## 🔴 The finding: this is a T-series tactical droid, not a T1-series utility droid

`DROIDS_INDEX.md:1650` maps this chassis to the canon row **"T1-series utility droid"**. That is
the wrong droid. The two share nothing but the letter-and-digit string "T1".

| | **T1-series utility droid** (what the index says) | **T-series … tactics droid / "T-1"** (what the sprite is) |
|---|---|---|
| role | **maintenance / cleaning droid**, class two | **tactical droid**, class four — a battlefield commander |
| height | **0.96 m** | **1.93 m** |
| manufacturer | **Duwani Mechanical Products** | **Baktoid Combat Automata** |
| owners | infobox `affiliation=` is **empty** | **Confederacy of Independent Systems**, Confederacy military, Zygerrian Slave Empire, Separatist holdouts, Bedlam Raiders, Atha Prime, Rebel officer corps |
| armament | **none listed** — equipment is an auditory/sonar scanner, a radar eye, a multi-function arm | **E-5 blaster rifle** |
| continuity | **Legends** (`{{Top\|leg}}`) | **canon** |
| first appearance | *KotOR II: The Sith Lords* | *The Clone Wars* |
| looks like | squat yellow-and-white two-legged drum with one big stalked radar eye | tall gaunt tan humanoid with a visor head and a ribbed chest grille |

**The evidence that settles it, three independent ways:**

1. 🔑 **"T-1" is a sourced alternate name for the tactical droid.** The canon article's own lead:
   "The **T-series military strategic analysis and tactics droid**, also known as the *T-series
   tactical droid*, the *standard tactical droid*, or **the 'T-1'** and initially designated the
   *CDE-T* …" So "T1 Tactical Droid" is a perfectly ordinary name for the Clone Wars droid, and
   the collision with the KotOR-II utility line is pure string coincidence.
   [T-series military strategic analysis and tactics droid](https://starwars.fandom.com/wiki/T-series_military_strategic_analysis_and_tactics_droid)
2. **The donor mod is `JDS_Separatists`.** The T1-series utility droid has **no faction
   affiliation at all** in its infobox and predates the Republic/Separatist conflict by
   millennia. A Separatist mod would have no reason to ship one.
3. **The sprite settles it visually.** `donor_current_sprite.png` shows the **visor-style head
   with two slit photoreceptors** and the **vertically-ribbed chest grille** in tan over dark
   blue-grey — a direct, recognisable read of `wookieepedia_tseries_infobox.jpg` (TA-175). It has
   no resemblance whatever to `wookieepedia_t1_series_utility_droid.jpg`.

**What should be true instead.** This chassis belongs to `DROIDS_INDEX.md:1647`
(**T-series military strategic analysis and tactics droid**, `canon`, Baktoid Combat Automata)
and its Legends fork at `:1648` (**T-series tactical droid**). Both currently carry a **blank**
`in repo` column while the utility droid at `:1650` wrongly carries `T1 tactical (JDS)`.

⚠️ **Two further index errors found alongside it:**
- `:1650` marks the T1-series utility droid **`canon`**. Its article opens `{{Top|leg}}` —
  it is **Legends**. Same class of error as the one the HK entry records at `:788`.
- The repo also holds **`RSW_DW_Race_OuterRim_TacticalDroid`, label "T-Series Tactical Droid"**
  (`Defs/Races_OuterRim.xml:653`) — a **second donor for the same canon droid**, likewise
  unmapped in the index.

🔴 **Reporting, not fixing** — per the brief, a def-versus-canon contradiction is filed for the
owner, and `Races_JDS.xml` is generated besides. Note that the **repo label is not wrong**: "T1
Tactical Droid" is a legitimate name for the droid it depicts. **The index's canon mapping is
what is wrong.** Nothing needs renaming in `src/`.

**⚠️ The slug `droid_t1_tactical` is kept** as assigned, so the entry is findable from the task
that commissioned it. Read it as *the chassis the repo calls "T1 Tactical Droid"*, whose canon
subject is the T-series tactical droid.

## Canon variants this chassis covers

What it **actually** covers:

| canon row | continuity | index line | mapped? |
|---|---|---|---|
| T-series military strategic analysis and tactics droid | canon | 1647 | 🔴 blank |
| T-series tactical droid | Legends | 1648 | 🔴 blank |

What the index **says** it covers — retained here as the **negative reference**, since correcting
the mapping is the owner's call:

| canon row | continuity | index line |
|---|---|---|
| T1-series utility droid | **Legends** (index says canon) | 1650 |

## Sourced text (Wookieepedia)

### The droid the sprite depicts — T-series tactical droid ("T-1")

Manufactured by **Baktoid Combat Automata**, the company that also developed the B1-series
battle droid. Used by the CIS through the Clone Wars, T-1s "aided in the coordination of their
military, acting as **advisors and often generals** for their superior officers," deployed at
**Christophsis**, **Ryloth** and the **Second Battle of Geonosis**.
[T-series military strategic analysis and tactics droid](https://starwars.fandom.com/wiki/T-series_military_strategic_analysis_and_tactics_droid)

🔑 **Height: 1.93 meters (6 ft 4 in)**; **class four droid**; **cost 8,000 credits**
(*Lead by Example*). **Mass empty.** Sensor colour is listed as **red, white *and* yellow** —
three options, not one — plus **purple under Scourge infection**. Armament: **E-5 blaster rifle**.
Equipment: **holographic projectors**, **datapad**, **macrobinoculars**.

**Appearance.** "T-series tactical droids, also referred to as **T-1s**, were **humanoid** fourth
class tactical droids standing at a height of 1.93 meters tall … Compared to the standard B1s who
served under them, they were **boxier in appearance and often sported varying color schemes.**
However, despite the T-1s often receiving **individualized color schemes and even their own
voices**, they were more or less the same unit at heart."

**Behaviour.** "Designed to **avoid the front lines** and calculate battle strategies from the
safety of flagships or other fortified locations. They were **prone to expressing their
superiority over all other droid models**." They were "known to **sacrifice a large number of
their own troops if they got in the way**" and to "**leave behind their superior officers to
survive**." 🔑 **Their canonical weakness:** "their **reliance on precise calculations meant they
lacked imagination when dealing with unexpected situations**, and soon enough the Galactic
Republic began to exploit this." Rarely seen fighting, though "some T-1s occasionally participated
wielding E-5 blaster rifles." 🔑 One unusual sourced ability: T-1s "possessed an ability to
**detect the clone troopers of the Republic Grand Army from a great distance and identify them by
CT-number.**"

**Named individuals:** **TA-175**, **TX-20**, **TJ-55**, **TI-99** (aboard Admiral Trench's
*Invincible*). Introduced under the name **CDE-T** in the years before the Clone Wars — over a
decade before, Atha Prime used CDE-Ts as security. Superseded by the **ST-series** (see
`droid_super_tactical`) but still in use "up until at least **19 BBY**," with remnants surviving
into the **Imperial Era**; Ahsoka Tano gave the crew of the *Ghost* **the head of a T-1** to help
find Captain Rex on Seelos, and other surviving T-1s "eventually became a part of the **Rebel
officer corps**."

⚠️ 23,155 chars. **Read: infobox, lead, Description, History through the Clone Wars.** The later
History, "Behind the scenes" and Appearances are **UNREAD, not absent.**

### The droid the index names — T1-series utility droid

"The **T1-series utility droid** was a series of **maintenance droids** manufactured by **Duwani
Mechanical Products** prior to the introduction of the **T3-series utility droid**." **0.96
meters**; class **maintenance droid**; sensor **green, yellow and blue**; equipment **auditory
and sonar scanner, radar eye, multi-function arm**; **no armament and no affiliation**. Its
article is `{{Top|leg}}` — **Legends** — and its only appearance is *KotOR II: The Sith Lords*.
[T1-series utility droid](https://starwars.fandom.com/wiki/T1-series_utility_droid)

🔑 **A naming trap worth recording, because it is the same trap twice.** The article explains that
"the **original** T1 series of droids — the **T1-series bulk-loading droid** — were manufactured
by **Kellenech Technologies** before the Great Sith War, but the company collapsed … Its assets
were liquidated and the **T1-series trademark was purchased by Duwani Mechanical Products**," who
"manufactured their **unrelated** T1-series of utility droids using the designation, and as a
result, Kellenech's old T1-series became commonly known as the **'LB'-series**." So **"T1" has
already been reused for two unrelated droids inside canon itself**, before the repo added a third
collision with the Clone Wars T-1. Any future index pass matching on the string "T1" should expect
this. Article read in full (1,682 chars).

## Provenance

Provenance for the droid **the sprite actually depicts**:

- **Manufacturer:** **Baktoid Combat Automata** (cited to *Ultimate Star Wars*) — the same
  manufacturer as the ST-series super tactical droid and the B1-series battle droid.
  [T-series … tactics droid](https://starwars.fandom.com/wiki/T-series_military_strategic_analysis_and_tactics_droid)
- **Era:** **blank.** `firstmade=` and `retired=` are empty. Dated events the text gives, cited
  rather than inferred: CDE-T use over a decade before the Clone Wars; three T-1s in the
  Christophsis campaign in **22 BBY**; continued service "up until at least **19 BBY**".
- **Typical owners:** **Confederacy of Independent Systems** and its **Confederacy military**;
  **Atha Prime**; **Zygerrian Slave Empire**; **Separatist holdouts** (the **Desix** holdout);
  **Bedlam Raiders**; **Alliance to Restore the Republic**, specifically the **Rebel officer
  corps**; the **Scourge** (as a vessel). 🔑 **The Rebel and Bedlam Raider entries matter for this
  campaign**: a T-1 in scavenger or insurgent hands is canon, not an invention.

For completeness, provenance of the **wrongly-mapped** droid: manufacturer **Duwani Mechanical
Products**; era **blank**; **typical owners: none listed** — the infobox `affiliation=` is empty,
which is itself a hint that the index row was a poor match for a Separatist-mod asset.

## Visual brief

🔴 **The sprite is a good T-series tactical droid and a nonsensical T1-series utility droid.** The
whole point of this section is that the mismatch is visible at a glance.

**`wookieepedia_tseries_infobox.jpg` (1230×3110 — TA-175) is the proportion authority.** What it
shows:

- **A tall, gaunt, distinctly humanoid droid** — narrow everywhere, with **very long thin
  splayed legs** that flare slightly at the shin and end in **flat splayed clawed feet**.
- 🔑 **A visor head**: a wide flat helmet-like crown with a **pair of horizontal slit
  photoreceptors** behind a grille, sitting on a **short exposed piston neck**. This is the
  chassis' unmistakable cue — it reads as a droid wearing goggles.
- 🔑 **A large dark vertically-ribbed rectangular grille filling the belly/lower chest** — the
  single most distinctive torso feature, and it dominates the front silhouette.
- **Boxy shoulder plates** with visible round joint hubs, and **thin forearms folded across the
  chest** in the render's pose.
- **Palette (this unit): weathered tan / bone over dark blue-grey**, with blue-grey wear
  streaking on the shins and a dark blue-grey chest panel. Canon licenses variation — see below.
- **A hip skirt of tan plates** below the grille.

`wookieepedia_tseries_colour_variants.jpg` is the article's own **"Tactical droids came in a
variety of color schemes"** plate — three units side by side. **Keep it as a positive reference
precisely because the three differ**: as with the ST-series, per-unit colour is canon, so an
unattested palette in the repo is not automatically an error.

**`wookieepedia_t1_series_utility_droid.jpg` (512×640) is a NEGATIVE reference — it is the droid
the index names, and it is not this chassis.** It shows a **squat two-legged utility droid**: a
**flat disc-shaped top plate**, a **single large stalked radar eye glowing green ringed in
magenta**, a small boxy midsection covered in panel decals, and **short chunky bracket-shaped
feet**, in **yellow-and-white** with rust weathering, standing in a KotOR-II interior. Roughly
knee-high on a human at 0.96 m. **Nothing about it matches the repo sprite.** Retained in the
directory as the evidence for the mapping finding, and labelled here so no later pass mistakes it
for a reference to draw from.

**What the repo sprite shows:**

- ✅ `donor_current_sprite.png` (256×256, top-down) is a **strong match to TA-175**: the **visor
  crown with two pale horizontal slit photoreceptors**, a **tan/bone face plate**, dark
  **blue-grey shoulder blocks**, a tan chest with a dark centre panel, and the **vertically-ribbed
  grille** rendered as a striped block on the lower body. Palette is the canon tan-over-blue-grey.
  Whoever drew this was clearly looking at a T-series tactical droid.
- ⚠️ **The legs are absent**, a RimWorld format constraint — but this droid's height and its
  spindly, wide-set stance live almost entirely in the legs, so the sprite reads much stockier
  than 1.93 m.
- ⚠️ **`skinShader` is `Cutout` with no mask and no colour channel**, so the PNG's own pixels are
  the shipping appearance and this chassis **cannot roll a colour scheme** — where canon says T-1s
  "often sported varying color schemes" and the article ships an image specifically to show it.
  Contrast `RSW_DW_Race_OuterRim_SuperTacticalDroid`, which does exactly this correctly with a
  three-option palette. **If one def-side correction is worth making here, it is giving this
  chassis a mask and a colour palette.**
- ⚠️ **`baseBodySize` 0.7 for a 1.93 m droid.** Note the JDS file gives **0.7** to the B2 super
  battle droid and the ST super tactical droid as well, so this looks like a JDS-wide default
  rather than a value considered for this chassis.
- ⚠️ **`MoveSpeed` 2.0 is identical to the ST super tactical droid's and to the B1's.** Canon
  distinguishes the ST-series from the T-series partly by **"more fluid motion programming"**, so
  giving predecessor and successor the same speed erases a sourced difference. The T-1's 2.0 is
  defensible on its own; it is the *equality* that is wrong.
- ⚠️ **Nothing depicts the T-1's actual canon behaviour** — commanding from a flagship, projecting
  holograms, reading a datapad, identifying clones by CT-number at range. It is a heavy-family
  combat pawn on disk, where canon is emphatic that T-1s **avoid the front lines**.


## Must show
- [ ] Visor head: wide flat helmet-like crown with a pair of horizontal slit photoreceptors behind a grille
- [ ] Large dark vertically-ribbed rectangular grille filling the belly/lower chest
- [ ] Boxy shoulder plates with visible round joint hubs
- [ ] Weathered tan/bone plating over dark blue-grey

## Engine limits
`skinShader` is `Cutout` with no mask and no colour channel, so this chassis cannot roll a colour scheme even though canon states T-1s "often sported varying color schemes."

## Source URLs

- https://starwars.fandom.com/wiki/T-series_military_strategic_analysis_and_tactics_droid — the
  droid the sprite depicts; wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=T-series_military_strategic_analysis_and_tactics_droid&format=json&prop=wikitext`
  (23,155 chars; infobox + lead + Description + Clone Wars History read, **remainder unread**).
  Rendered HTML is Cloudflare-walled; the API is not.
- https://starwars.fandom.com/wiki/T1-series_utility_droid — the droid the index names; same API
  pattern (1,682 chars, **read in full**). `{{Top|leg}}` — **Legends.**
- https://static.wikia.nocookie.net/starwars/images/e/e8/TA175-MF54.png
  (File:TA175-MF54.png → `wookieepedia_tseries_infobox.jpg`). ⚠️ **1230×3110 — over the 2000px
  viewing limit.** The full-size original is kept as the reference asset; it was viewed only as a
  593×1500 downscale at `/tmp/tser_small.jpg`, per the brief. **Do not open the original
  directly.**
- https://static.wikia.nocookie.net/starwars/images/e/e5/TacticalDroidTrio-BYOR2D2-50.png
  (File:TacticalDroidTrio-BYOR2D2-50.png → `wookieepedia_tseries_colour_variants.jpg`)
- https://static.wikia.nocookie.net/starwars/images/5/5c/T1N1.png
  (File:T1N1.png → `wookieepedia_t1_series_utility_droid.jpg`) — **negative reference**
- Named in the articles, **not fetched this pass**:
  https://starwars.fandom.com/wiki/T-series_tactical_droid/Legends ·
  https://starwars.fandom.com/wiki/LB-series_bulk-loading_droid ·
  https://starwars.fandom.com/wiki/T3-series_utility_droid ·
  https://starwars.fandom.com/wiki/TX-20 · https://starwars.fandom.com/wiki/TA-175 ·
  https://starwars.fandom.com/wiki/Duwani_Mechanical_Products
  ⚠️ Also **not downloaded**:
  `https://static.wikia.nocookie.net/starwars/images/…/TseriesTacticalDroid-SWL2024update.png`
  — recorded because the equivalent ST-series file measured 3840×2690 and this one is likely
  oversized too; a later pass should size-check before fetching.
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_JDS.xml` (generated by
  `src/RimStarWars/Droidworks/Source/gen_droidworks_defs.py`),
  `Defs/Races_OuterRim.xml` (the second, unmapped T-series donor at :653)

## Candidate images

- `wookieepedia_tseries_infobox.jpg` (1230×3110) — **TA-175**, full-body render on transparent
  background. **The proportion and colour authority for what this chassis actually is.** 🔴 Over
  2000px: view a `/tmp` downscale, never the original.
- `wookieepedia_tseries_colour_variants.jpg` (925×765) — the article's "Tactical droids came in a
  variety of color schemes" plate, three units together. **Positive reference for palette
  variation**, and the argument for giving this chassis a colour channel.
- `wookieepedia_t1_series_utility_droid.jpg` (512×640) — the **T1-series utility droid**, the
  droid `DROIDS_INDEX.md:1650` names. 🔴 **NEGATIVE REFERENCE — do not draw from this.** Kept as
  the evidence for the mismatch finding.
- `donor_current_sprite.png` (256×256) — repo JDS sprite, `south`/top-down. Judge literally:
  `skinShader` is `Cutout`, no tint applied.
- `donor_body_east.png` (256×256) — the profile frame.

## ruling

(empty — the owner has not reviewed this chassis yet. 🔴 **The index mapping question above is
his to settle**; nothing in `src/` was changed and nothing in `DROIDS_INDEX.md` was edited.)
