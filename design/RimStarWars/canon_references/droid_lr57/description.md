# LR-57 combat droid / Retail Caucus droid (repo chassis: LR-57, JDS)

**defName**: droids are **not xenotypes**. One race def on disk:
- `RSW_DW_Race_JDSCIS_LR-57_Combat_Droid` — label `LR-57_Combat_Droid` (the underscores are in
  the label itself, a JDS-absorption artifact), `src/RimStarWars/Droidworks/Defs/Races_JDS.xml:644`.
  `ParentName="DW_Family_Battle"`, `baseHealthScale` **1.5**, `MoveSpeed` **1.7**,
  `skinShader` **Cutout** (not `CutoutComplex` — so **no colour channels, no mask, the PNG's own
  colours ship as-is**), `headTypes` = `RSW_DW_HeadType_Blank` (body graphic only, no separate
  head layer), `DroidworksExtension` with `chassisClass` 3, `energyDensity` 0,
  `deliberateDenyModule` true, plus `CompProperties_DroidDetonation`.
- **No PawnKindDef found.** A grep of `Defs/PawnKinds_JDS.xml` and the rest of
  `src/RimStarWars/` for `LR-57` / `LR57` returns only this race def, its texture path, and the
  index. If a pawnkind exists it is not named for the model — stated as a finding, not fixed.

Sprites: `src/RimStarWars/Droidworks/Textures/JDS/Things/LR-57_Combat_Droid{,_south,_east,_north}.png`,
512×512, three directions.

## Canon variants this chassis covers

Two rows in `DROIDS_INDEX.md`, and they are the **same droid across the canon/Legends fork**:

| canon row | continuity | index line |
|---|---|---|
| LR-57 combat/retail droid | canon | 1031 |
| LR-57 combat droid | **Legends** | 1030 |

Each article carries the other as its counterpart (`{{Top|legends=…}}` / `{{Top|canon=…}}`), so
this is a continuity fork, not two models. ⚠️ **The index's row names are reversed relative to
continuity intuition**: the *canon* article is titled "LR-57 combat/**retail** droid" and the
*Legends* one is the plainer "LR-57 combat droid" — do not sort them by name.

Also-known-as, across both: **Retail Caucus droid**, **retail droid**, and (Legends only)
**mine droid**.

One named individual is in canon and is repo-relevant: **Battle droid 513** — an LR-57 in Death
Watch's Carlac camp, used as target practice, **right leg replaced with an LM-432 crab droid's
and right arm with a B1 battle droid's**. A canon precedent for a mismatched-salvage droid,
which is squarely a Jawa-clan idea.

## Sourced text (Wookieepedia)

The **LR-57 combat/retail droid** was a model of battle droid used by the **Retail Caucus** and
the **Confederacy of Independent Systems** during the Clone Wars, most prominently at the
**Battle of Christophsis**.
[LR-57 combat/retail droid](https://starwars.fandom.com/wiki/LR-57_combat/retail_droid)

🔑 **Height: 2.58 meters (8 ft 6 in)** — stated in *both* infoboxes, canon (cited to
*The Clone Wars: Character Encyclopedia — Join the Battle!*) and Legends (cited to
*Star Wars: The Clone Wars Character Encyclopedia*). This is a **big** droid, half a metre
taller than the KX-series and well over a metre taller than a droideka. **Mass is empty in both
infoboxes.** Cost appears **only in Legends: 16,000 credits** (*The Clone Wars Campaign Guide*);
the canon infobox's `cost=` is empty.

**Appearance and construction, canon body text.** "With its relatively low versatility, the
LR-57 was used for very particular situations. It stood bipedal like its more common **B1** and
**B2** counterparts, but was **taller and wider in size.** Its **legs were attached to a small
pelvic mount that held its large head.** The **front face of the head had between one and three
photoreceptors.** From the **back of the cylindrical head protruded two arms equipped with
double laser cannons.**" Those cannons "primarily functioned as typical blasters at mid-range,
however they could also be used for **physical attacks for close-combat**." They could
**vocalize in Galactic Basic Standard**.

🔑 **The unusual ability, and the reason this droid exists: it is a self-burying mine.** "Located
near the front of its head, the LR-57 had **two sensory antennae on either side**, that aided one
of their specialties as **ambush attackers**. The droid was able to **lay dormant in shallow
ground** in wait of enemies traversing above, using the **exposed antennae to detect
disturbances.** When set in a dense arrangement, **tripping a single dormant LR-57 would cause
all others within a short proximity to also activate.**" Legends puts it more bluntly: the
antennae "searched for specific types of signals, activity, or other disturbances, **enabling
the droids to be used as autonomous mines**," and gives the alternate name **mine droid**.

🔑 **They are slow, and canon says so as a weakness.** At Christophsis, Skywalker "began cutting
down LR-57 units **as they slowly react** to the Jedi's sudden appearance"; Legends is explicit —
"while they outnumbered the two Jedi, their **sluggish reactions made them easy prey.**" Half
were destroyed by Skywalker, the rest crushed when Ahsoka Tano pulled a wall down on them.

**History:** first seen at the **Battle of Christophsis**, an indeterminate number **buried
around a deflector shield generator** as a last line of protection; later at the **Battle of
Malastare** alongside B1s, B2s and dwarf spider droids, all destroyed or deactivated by the
Republic's prototype **electro-proton bomb**; Legends adds the **Battle of Tirahnn**. Battle
droid 513's Carlac story is above.

**Behind the scenes (Legends article):** "The retail droid's design is **based after early
concept art of the droideka.**" That is a real, sourced kinship with `droid_droideka` in this
library, and it explains the shared bronze-brown palette and arched-shell read.

Both articles were pulled in full (8,024 and 5,787 chars) — **no truncation, nothing unread**
except the Appearances/Sources listings.

## Provenance

- **Manufacturer:** **Retail Caucus** (canon infobox, cited to *Star Wars: On the Front Lines*;
  Legends lists Retail Caucus as both creator and manufacturer). Both articles carry
  `Category:Retail Clan products`. Legends gives a **homeworld: Christophsis**, and a **line:
  LR-series**; canon gives neither.
  [LR-57 combat/retail droid](https://starwars.fandom.com/wiki/LR-57_combat/retail_droid) ·
  [LR-57 combat droid/Legends](https://starwars.fandom.com/wiki/LR-57_combat_droid/Legends)
- **Era:** **blank.** `firstmade=` and `retired=` are empty in **both** infoboxes. In-text the
  droid is a Clone Wars unit (Christophsis, Malastare, Carlac), but that is narrative and is not
  promoted here.
- **Typical owners:** **Retail Caucus** and the **Confederacy of Independent Systems** — those
  two, in both continuities, and nothing else. `DROIDS_INDEX.md:1030–1031` agrees exactly. One
  off-faction possession is attested but not an affiliation: a captured unit (Battle droid 513)
  held by **Death Watch** on Carlac as target practice.

## Visual brief

🔴 **Canon and Legends disagree on both the plating colour and the gun count, and the repo has
picked the canon side of one and neither side of the other.**

- **Plating.** Canon infobox: **brown** (cited to the *Clone Wars* film). Legends body text:
  "**orange-colored** retail droids were used as guards of the energy shield projector." The
  infobox render is a **weathered warm brown with rust-orange banding**, which is arguably both.
  The repo sprite is brown. **The repo matches canon here.**
- **Armament.** Canon infobox: "**Double laser cannons (2)**." Legends infobox: "**Blaster
  cannons (4)**." Both describe the same physical thing — two arms, each ending in a double
  barrel — counted differently (2 arms vs 4 barrels). Not a real contradiction in the art, but a
  real one in the text, and anything that reads a number out of the infobox will get a different
  answer depending on which page it hit.

**`wookieepedia_lr57_infobox.jpg` is the proportion authority, and the silhouette is genuinely
strange — this droid is not humanoid.** What it shows:

- **A huge horizontal cylinder** — the "large head" — lying on its side like a barrel, ribbed
  along its flank, occupying roughly the **top half of the whole droid**. There is no torso: the
  cylinder *is* the body.
- **The face is the flat circular end-cap of that cylinder**, tilted forward and carrying **one
  large teardrop/comma-shaped photoreceptor plus one small round one below it** — i.e. the
  "between one and three photoreceptors" the text allows for, here reading as two.
- **Two long thin cannon arms projecting straight out from the rear/underside of the cylinder**,
  each a segmented tube ending in a **fine double muzzle**. They stick out well past the body's
  width — the widest thing about the droid.
- **Two very long, whip-thin antennae** rising vertically from the top of the cylinder. These are
  the mine sensors and they are visually unmissable.
- **A small pelvic drum below and behind the cylinder**, from which **two long backward-jointed
  bird legs** descend to **flat splayed clawed feet**. The legs are thin and the stance is
  wide-set and unstable-looking, which fits "sluggish."
- Palette: **warm mid-brown with darker brown shadow and rust-orange band accents**, heavily
  weathered and dusty.

**What the repo sprite shows — and it is one of the better matches in this library:**

- `donor_current_sprite.png` (512×512, top-down, `south`) reads the cylinder correctly: a
  **ribbed brown barrel filling the frame vertically**, with the **circular end-cap face at the
  bottom carrying the teardrop photoreceptor and a bright red pupil dot**, the **small pelvic
  drum below it**, and **two long thin dark antennae running down either side.** The palette is
  the canon warm brown. The teardrop eye shape, the ribbing and the antennae are all present and
  correct.
- ⚠️ **The red photoreceptor dot is right for canon and wrong for the render.** The canon infobox
  states sensor colour **red** (cited to "A Friend in Need"), so the red pupil is *sourced* — but
  `wookieepedia_lr57_infobox.jpg` shows the eye as a dull unlit brown-grey lens with no red at
  all. Trusting the images on appearance, per the brief: this is a case where the **text and one
  image disagree**, and the repo followed the text. Worth the owner's eye rather than a silent
  correction either way.
- 🔴 **The cannon arms barely survive.** In canon they are the droid's widest feature and the
  entire reason it is a combat droid; in the sprite the only things at the flanks are the two
  thin antennae. Seen top-down the arms should read as **two tubes projecting outward past the
  barrel's silhouette** — as they do, faintly, in the small grey shoulder blocks. If one
  correction is worth making to this chassis it is **lengthening and darkening the cannon arms
  so the droid reads as armed at thumbnail size.**
- **The legs are absent**, which is a RimWorld format constraint rather than an error — but note
  this droid's height lives almost entirely in its legs and pelvic mount, so the sprite reads
  much shorter than 2.58 m.
- ⚠️ **`skinShader` is `Cutout` and there is no colour channel and no `…m.png` mask**, unlike the
  KX and HK chassis. So **this sprite's own pixels are the shipping appearance** — there is no
  def-side tint to rescue or blame. Judge the PNG literally.
- ⚠️ **The def has no `baseBodySize` override at all** (only `baseHealthScale` 1.5), so it
  inherits `DW_Family_Battle`'s. For the tallest droid in this batch, that is worth checking.
  **`MoveSpeed` 1.7 is, by contrast, an excellent canon match** to the sourced "sluggish
  reactions" — that number is doing real lore work.
- **Nothing in the repo depicts the buried/dormant state.** Same class of gap as the droideka's
  missing ball form: the LR-57's one distinctive canon behaviour — lying under shallow ground
  with only antennae showing, and chain-activating its neighbours — has no art and no mechanic on
  disk. Unlike the ball, though, the dormant state's art is nearly free: **two antennae and a
  patch of disturbed ground.**


## Must show
- [ ] Huge horizontal ribbed cylinder occupying roughly the top half of the whole droid, with no separate torso
- [ ] Flat circular end-cap face carrying one large teardrop photoreceptor plus one small round one below it
- [ ] Two long thin cannon arms projecting from the rear/underside, each ending in a fine double muzzle, projecting past the body's width
- [ ] Two very long, whip-thin antennae rising vertically from the top of the cylinder
- [ ] Warm mid-brown plating with darker brown shadow and rust-orange band accents

## Engine limits
`skinShader` is `Cutout` with no colour channel and no mask — the PNG's own pixels are the shipping appearance, so a colour correction requires a repaint, not a def edit.

## Source URLs

- https://starwars.fandom.com/wiki/LR-57_combat/retail_droid — canon article; wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=LR-57_combat/retail_droid&format=json&prop=wikitext`
  (8,024 chars, **read in full**)
- https://starwars.fandom.com/wiki/LR-57_combat_droid/Legends — Legends article, same API
  pattern (5,787 chars, **read in full**)
- https://static.wikia.nocookie.net/starwars/images/c/ce/RetailCaucusDroid-TCWCEJtB.png
  (File:RetailCaucusDroid-TCWCEJtB.png → `wookieepedia_lr57_infobox.jpg`) — the shared infobox
  image of both articles
- https://static.wikia.nocookie.net/starwars/images/7/7a/LR-57CombatDroid-AoN.png
  (File:LR-57CombatDroid-AoN.png → `wookieepedia_lr57_bd513_carlac.jpg`)
- Named in the articles, **not fetched this pass**:
  https://starwars.fandom.com/wiki/Battle_droid_513 ·
  https://starwars.fandom.com/wiki/Retail_Caucus
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_JDS.xml`

## Candidate images

- `wookieepedia_lr57_infobox.jpg` (885×1160) — the infobox render, full body three-quarter on
  transparent background. **The proportion and colour authority**: horizontal cylinder body,
  end-cap face, two double-barrelled cannon arms, two whip antennae, backward-jointed legs,
  weathered brown with rust banding.
- `wookieepedia_lr57_bd513_carlac.jpg` (1008×887) — **Battle droid 513**, a *modified* LR-57,
  fighting Death Watch on Carlac. **Weak evidence for the stock chassis and label it as such**:
  this unit has an LM-432 crab droid leg and a B1 arm grafted on. Strong evidence for the
  salvage-hybrid look.
- `donor_current_sprite.png` (512×512) — the repo JDS sprite, `south`/top-down. Judge literally:
  `skinShader` is `Cutout`, so no tint is applied over it.
- `donor_body_east.png` (512×512) — the profile frame.

## ruling

(empty — the owner has not reviewed this chassis yet)
