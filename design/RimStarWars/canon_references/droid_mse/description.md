# MSE series / MSE-6 mouse droid (repo chassis: MSE mouse, OuterRim)

🔑 **ONE entry, covering TWO index rows.** `DROIDS_INDEX.md` carries `MSE series` → "MSE
mouse (OuterRim)" at **line 1176** and `MSE-6 series repair droid` → "MSE-6 mouse
(OuterRim)" at **line 1177**. Both "in repo" labels name **the same single sprite set and
the same single race def** — see "Is this one chassis or two?" below. This entry covers both
rows; there is no separate `droid_mse6` entry and there should not be one.

**defName**: droids are not xenotypes. Real defs on disk — **one race, one pawnkind, total**:
- `RSW_DW_Race_OuterRim_MSEDroid` — label "MSE Repair Droid",
  `ParentName="DW_Family_Labour"`, `baseBodySize` **0.5**, `MoveSpeed` 5.3
  (`src/RimStarWars/Droidworks/Defs/Races_OuterRim.xml:1041`)
- `RSW_DW_OuterRim_MSEDroid` — PawnKindDef, `combatPower` 99999, forced trait
  `Industriousness 1` (`Defs/PawnKinds_OuterRim.xml:313`)
- Head type `RSW_DW_HeadType_Blank`; the whole droid is the body graphic.
- `skin` colour channel is `RGBA(110,110,110,255)` on both `first` and `second` — a **flat
  mid-grey tint** over a near-white greyscale PNG. **Judge this sprite tinted.**
- ⚠️ **Second consumer of the same texture:** `Races_Primitive.xml:179–200` deliberately
  reuses graphic path `OuterRim/Droid/MSE` for a *different* primitive race, with an inline
  comment saying so ("small, boxy"). So changing this art changes two races, not one.

Sprites: `src/RimStarWars/Droidworks/Textures/OuterRim/Droid/MSE_{south,east}.png` (256×256),
graphic path `OuterRim/Droid/MSE`.

🔑 **This is the only chassis in this batch where the repo has AUTHORED new art.**
`src/RimStarWars/MSEDroidFix/` is our own mod (`mandrake.rsw.msedroidfix`) supplying the
missing `MSE_north.png` (256×256), because the donor Outer Rim - Droid Depot ships **only
south and east** while the def declares `Graphic_Multi`, so a droid walking away silently
fell back to its front view. The absence was verified against the 1.6 AssetBundle manifest,
not the loose folder. Silhouette and keyline are copied pixel-for-pixel from `MSE_south`;
only the interior is re-authored (`Source/draw_mse_north.py`).

## Is this one chassis or two? — settled

**One chassis. Two rows in the index, one thing in the game, and a line-and-member
relationship in canon.**

- **Repo evidence:** an exhaustive filename search across `src/` returns exactly three MSE
  textures — `MSE_south.png`, `MSE_east.png` (donor) and our `MSE_north.png` — and **no
  `MSE6`, `MSE4` or `MSE5` texture of any kind.** One race def, one pawnkind def. There is
  no second sprite for an "MSE-6" row to describe.
- **Canon evidence:** the **MSE-6 article's infobox carries `line=MSE series`**, and the MSE
  series article lists its `model=` as **MSE-4, MSE-5, MSE-6 series repair droid**. Decisive
  detail: **the MSE *series* article's own infobox image is `File:MSE6series-TGTB.png` — a
  photograph of an MSE-6.** The wiki itself illustrates the series with this member. There is
  no separate "MSE series" appearance to correct.
- ⚠️ **Not a pure duplicate.** The two rows differ in continuity marking (`canon` vs
  `canon (+Legends)` — the series article is `{{Top|legends=MSE-series}}`, i.e. it has a
  Legends counterpart at `MSE-series`) and the series row carries a **200-credit unit cost**
  that the MSE-6 row does not. Merging the *entries* is correct; the surviving index row
  should read as **"the MSE series, represented in this repo by its MSE-6 member."** The
  2026-09-15 QA pass was right not to merge the rows on a guess.

## Canon variants this chassis covers

- **MSE-6 series repair droid** — a.k.a. **mouse droid**; what the sprite depicts
  (`DROIDS_INDEX.md:1177`, `canon (+Legends)`)
- **MSE series** — a.k.a. **MSE-series Maintenance Droid** / **MSE-series**; the parent line
  (`DROIDS_INDEX.md:1176`, `canon`)
- **MSE-4** and **MSE-5** — the other two sourced models of the line. No repo art, no
  articles fetched this pass.
- ⚠️ **Not this chassis:** the **Polar mouse droid** — the MSE series article explicitly calls
  it "a similar droid **with four large wheels**", destroyed by Grogu. Different model.

## Sourced text (Wookieepedia)

The **MSE series**, also known as the **MSE-series Maintenance Droid**, was a series of
**repair droids produced by Rebaxan Columni**, with models **MSE-4, MSE-5 and MSE-6**.
🔑 **The MSE series was based on the chak-chak animal.** Some form of mouse droid existed as
far back as **229 BBY**. Unit **cost: 200 credits**. **Plating: black.** **Masculine
programming.** C-3PO, quoted in the article: *"The unobtrusiveness of the MSE series makes
them extremely useful sp——er, operatives."*
[MSE series](https://starwars.fandom.com/wiki/MSE_series)

The **MSE-6 series repair droid**, also known as a **mouse droid**, was a **roving repair
droid employed in the hundreds to clean the floors of starships and bases, carry messages
and guide troops to assigned posts.** From that article:

- **Small, boxy droids that moved around on FOUR DRIVER WHEELS, HALF-HIDDEN UNDER THE BODY.**
- 🔑 **"A command order tray in the top of the droid held sealed orders."** The tray is on
  the **top face** — the face RimWorld's camera looks straight at.
- **Height 0.25 meters**; **width 0.54 meters**; **mass 5.9 kilograms**. ⚠️ **Sourced
  contradiction, flagged by the wiki itself**: *Absolutely Everything You Need to Know* and
  the StarWars.com Databank both give **0.25 m**, while *Star Wars: Extraordinary Droids*
  (2020) gives **0.4 m**.
- **Plating: black** (*A New Hope*) **and Gray** (*The Mandalorian* Chapter 6) — both are
  sourced, black first. **Homeworld: Chad.**
- **Sensor: the infobox field is EMPTY.** No photoreceptor colour is sourced, and none of the
  reference images show an eye. **This droid has no face.**
- Equipment: **command order tray**, **Scomp-link data probe**, **knife**, **two grasping
  claws**.
- Behaviour: **frightened very easily** (MSE-6-G735Y fled from Chewbacca's roar) and
  **very suspicious of people**. One canon unit "had trouble maneuvering on its wheels and
  was prone to turn in circles."
- **Interior:** "several wires, indicator lights, and buttons"; **an MSE-6 could be
  reprogrammed from this interface.**
- **The line's omnipresence led to a growing aftermarket in modified mouse droids used for
  surveillance and slicing.** 🔑 The most campaign-usable fact in the article for a scavenger
  clan: canon establishes an *aftermarket in hacked mouse droids* as normal.
- Sourced task range beyond cleaning: carrying messages between an officer and a stormtrooper;
  **dragging away dead bodies for Darth Vader** (who then destroyed the unit for bumping into
  him); acting as a bug for a Rebel spy; serving as a **danger signal** on a radiation-poisoned
  world; being **hollowed out and sold as a popcorn container** at Black Spire Outpost.
- 🔑 **On Mandalore, "all the mouse droids were equipped with lightbars and sirens"** — the red
  strip visible in `wookieepedia_on_mandalore.png`.
- Behind the scenes: dubbed **"baby box"** in a 15 March 1976 test; Lucas called it a **"box
  droid"** and asked for "these little quail running down the hallway… rats leaving a sinking
  ship."

## Provenance

- **Manufacturer:** **Rebaxan Columni** — both infoboxes agree, and the MSE-6 article adds
  that it was **designed in the days of the Galactic Republic and remained a mainstay aboard
  starships for decades**. `DROIDS_INDEX.md:1176` and `:1177` agree.
  **Homeworld: Chad** (MSE-6 infobox, cited to *Star Wars Life Size*).
- **Era:** **blank.** `firstmade=` and `retired=` are empty on **both** articles. The MSE
  series article's dated statement that some mouse droid existed by **229 BBY** is narrative
  text, not an infobox era, and is not promoted here.
- **Typical owners:** the widest owner list of any droid in this batch, and the reason it is
  the most freely-placeable — **Galactic Republic; Confederacy of Independent Systems;
  Separatist holdouts; Galactic Empire; Imperial remnants (Ubrik Adelhard's, Gideon's); New
  Republic; First Order; Resistance (incl. the Resistance spy droid network); Plazir-15
  government; Tagge Corporation; the Haddrex Gang (criminal); Second Revelation (the droid
  movement); Scourge (as a vessel).** Both infoboxes, plus in-text: podracer-era Tatooine
  households, Techno Union facilities on Mustafar, a Death Star, prison transports.

## Visual brief

**Overall shape and proportion — the whole read at sprite scale.** Canon MSE-6 is **a matte
near-black wedge — a truncated pyramid, a doorstop — sitting on a wider flat skirt, running
on four small dark wheels tucked half under the body.** It is **markedly longer than it is
tall (0.54 m by 0.25 m)** and **has no head, no eyes, no arms and no vertical element at all
except the sensor combs on its roof.** Read at a glance: **a low dark box with a sloped
front, about the footprint of a large dog, ankle-height.** There is no colour anywhere except
a **polished silver-grey trim strip along the base lip** and, on the Mandalore units, a **red
lightbar on top.**

**The repo sprite gets the box and loses everything that makes it identifiable from above.**

- ✅ **The boxy top-down footprint is right, and right for the format.** `donor_current_sprite.png`
  (south) is a rectangle with a tapered inner trapezoid — a legible read of a wedge seen from
  above — and `donor_current_sprite_east.png` is correctly **wide and low**, matching canon's
  0.54 × 0.25 proportion. This chassis has the least format friction of the six: a legless box
  is exactly what RimWorld's camera handles well.
- ✅ **No eyes, no face — and that is correct.** Both infoboxes leave `sensor=` empty and no
  image shows a photoreceptor. Resist the temptation to add a glowing eye; canon's mouse droid
  is deliberately blank, which is the whole point of C-3PO's "unobtrusiveness" line.
- ✅ **`baseBodySize` 0.5 is the most defensible scale value in this batch.** Canon is 0.25 m
  tall, 0.54 m wide, **5.9 kg** — smaller than 0.5 of a human by height, but the top-down
  *footprint* at 0.54 m is roughly half a person's, so 0.5 reads correctly from above.
  `MoveSpeed` 5.3 also agrees with canon: "roving", and MSE-6-G735Y was the **fastest mouse
  droid in the Imperial fleet**, considered for racing.
- 🔴 **Colour is the biggest single problem.** Canon's primary sourced plating is **black**,
  and every reference image is a **matte near-black**. The def tints the sprite
  `RGBA(110,110,110)` — a **flat mid-grey**, which at sprite scale reads as a pale pebble and
  vanishes against RimWorld's grey floors and stone. "Gray" *is* separately sourced (the
  Mandalorian Chapter 6 unit), so the value is not invented — but it is the minority reading
  and the wrong one for legibility. **Push it to near-black with the polished silver base lip
  as the only highlight.** On a desert map a small black box is unmistakable; a mid-grey one
  is invisible.
- 🔴 **The roof is blank, and the roof is all we ever see.** Canon puts three things on the top
  face: the **command order tray**, the **two comb-like arrays of black cylindrical sensor
  stalks** at the rear (the most distinctive feature in `wookieepedia_mse6_infobox.png`), and,
  on the Mandalore units, a **red lightbar**. The sprite's top-down frame has none of them —
  just a plain plate with a horizontal seam. This is the cheapest high-value correction on this
  chassis: **a few dark stalk pixels at the rear of the top plate, and a red lightbar strip,
  would make it read as a mouse droid instead of as a crate.**
- ⚠️ **No wheels are visible in any frame.** Canon's wheels are "half-hidden under the body", so
  hiding them is defensible from above — but the `east` frame shows a flat bottom edge with no
  wheel bulge at all, and the wheels are clearly visible in profile in both
  `wookieepedia_mse6_infobox.png` and `wookieepedia_on_mandalore.png`. A wheel bulge in the
  east frame would fix it.
- ⚠️ **The wedge taper is drawn as an interior line, not as a silhouette.** Canon's front slope
  is the strongest cue that it has a *front*; the sprite's outline is a plain rectangle in all
  three frames, so the droid never reads as facing anywhere. Our own `MSE_north` inherits this
  by construction (the script copies the south silhouette pixel-for-pixel and re-authors only
  the interior) — a correct, deliberate choice for registration, but it means the north/south
  pair differ only in interior shading.
- **No repo art** for the grasping claws, the Scomp data probe, the open-interior/reprogrammable
  state, the Tagge Corporation gold emblem, or the four-large-wheel Polar mouse droid.


## Must show
- [ ] Matte near-black plating (not mid-grey), wedge/box shape with a wider flat skirt
- [ ] No eyes/photoreceptor visible anywhere — deliberately blank face
- [ ] Wide, low silhouette much wider than tall (0.54 m by 0.25 m proportions)
- [ ] Two comb-like sensor stalk arrays visible on the rear roof
- [ ] Polished silver-grey trim strip along the base lip
- [ ] Wheel bulge visible in the east/profile view

## Engine limits
Shared texture: `Races_Primitive.xml` reuses graphic path `OuterRim/Droid/MSE`, so editing this sprite changes two races.
- The `skin` colour channel's `first` and `second` values are set identically (`RGBA(110,110,110,255)`), so no two-tone variation is available from the def as it stands — the whole droid tints as one flat colour.

## Source URLs

- https://starwars.fandom.com/wiki/MSE-6_series_repair_droid — wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=MSE-6_series_repair_droid&format=json&prop=wikitext`
  (29,385 bytes of JSON, read in full to the Appearances list — no truncation). Sections read:
  infobox, lead, Description (Overview/Use/Behavior), History (all four eras), Behind the scenes.
- https://starwars.fandom.com/wiki/MSE_series — same API pattern (14,716 bytes, read in full).
  **Tagged `{{Droid-stub}}`**; flagged `{{Top|legends=MSE-series}}`, i.e. it has a Legends
  counterpart at `MSE-series` which was **not fetched**.
- https://static.wikia.nocookie.net/starwars/images/b/bb/MouseDroid-ROStickerBook.png →
  `wookieepedia_mse6_infobox.png` (1536×1004; Fandom served WebP, re-saved as PNG locally)
- https://static.wikia.nocookie.net/starwars/images/b/bc/MSE6series-TGTB.png →
  `wookieepedia_mse_series_group.jpg` (**4100×2880 — 🔴 DO NOT VIEW AT FULL SIZE**; it will
  abort a session. `sips -Z 1400` a copy to `/tmp` first.)
- https://static.wikia.nocookie.net/starwars/images/4/46/UMSE-6.png →
  `wookieepedia_on_mandalore.png` (565×462)
- https://static.wikia.nocookie.net/starwars/images/f/f7/5LInsideMSE6-TheEscape.png →
  `wookieepedia_interior.png` (583×494)
- **Named in the articles but not fetched this pass:** `MSE-4`, `MSE-5`, `MSE-series` (the
  Legends counterpart), `Polar mouse droid`, `chak-chak`, `command order tray`.
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_OuterRim.xml`,
  `Defs/PawnKinds_OuterRim.xml`, `Defs/Races_Primitive.xml` (second consumer of the texture)
- Repo mod: `src/RimStarWars/MSEDroidFix/` (our authored `MSE_north.png`)
- Index rows: `design/RimStarWars/canon_references/DROIDS_INDEX.md:1176` and `:1177`
- ⚠️ **Unresolvable contradiction in the sources themselves:** height is **0.25 m** per two
  sources and **0.4 m** per a third; the wiki records the conflict rather than settling it, and
  so does this entry. **Nothing here is sourceable about MSE-4 or MSE-5's appearance.**

## Candidate images

- `wookieepedia_mse6_infobox.png` (1536×1004) — the MSE-6 article infobox: a practical-prop
  photograph, three-quarter front-left, on transparent background. **The proportion, colour and
  detail authority.** Matte near-black truncated-pyramid body on a wider flat skirt; **two
  comb-like arrays of black cylindrical sensor stalks on the roof**; a dense greeble panel on
  the right slope; a **polished silver trim strip along the base lip**; four small dark wheels
  tucked half under the skirt. No eyes, no arms.
- `wookieepedia_mse_series_group.jpg` (**4100×2880**) — the **MSE series** article's own infobox
  image, and the evidence that the wiki illustrates the series with an MSE-6. Same prop, larger
  and sharper: the roof stalk arrays and the wheel treads are clearest here. 🔴 **Downscale
  before viewing.**
- `wookieepedia_on_mandalore.png` (565×462) — an in-show frame on Mandalore. Best reference for
  **how black it actually reads in a dark scene**, for the **four visible wheels below the
  skirt**, and for the **red lightbar** the article sources for these units.
- `wookieepedia_interior.png` (583×494) — the inside of an MSE-6 chassis (wires, indicator
  lights, buttons), the reprogramming interface. The only reference for an opened unit.
- `donor_current_sprite.png` (256×256) — donor `MSE_south`, top-down. **Judge tinted**
  `RGBA(110,110,110)`; the raw file is near-white. Plain plate, no roof detail.
- `donor_current_sprite_east.png` (256×256) — donor `MSE_east`. Correctly wide and low; no
  wheels.
- `donor_msedroidfix_north.png` (256×256) — **our own** `MSE_north` from
  `src/RimStarWars/MSEDroidFix/`, silhouette copied pixel-for-pixel from the donor's south with
  a re-authored rear panel (vent seam + two panel joints).

## ruling

(empty — the owner has not reviewed this chassis yet)
