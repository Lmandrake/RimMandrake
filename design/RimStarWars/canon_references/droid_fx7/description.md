# FX-series / FX-7 medical assistant droid (repo chassis: FX-7, OuterRim)

🔑 **ONE entry, covering TWO index rows.** `DROIDS_INDEX.md` carries
`FX-7 medical assistant droid` → "FX-7 (OuterRim)" at **line 697** and
`FX-series medical assistant droid` → "FX-series (OuterRim)" at **line 699**. Those two
"in repo" labels name **the same single sprite set and the same single race def** — see
"Is this one chassis or two?" below. This entry covers both rows; there is no separate
`droid_fx_series` entry and there should not be one.

**defName**: droids are not xenotypes. Real defs on disk — **one race, one pawnkind, total**:
- `RSW_DW_Race_OuterRim_FX7Droid` — label "fx-7 medical droid" (lowercase in the def),
  `ParentName="DW_Family_Labour"`, `baseBodySize` 0.75, `MoveSpeed` 2.4
  (`src/RimStarWars/Droidworks/Defs/Races_OuterRim.xml:931`)
- `RSW_DW_OuterRim_FX7Droid` — PawnKindDef, label "fx-7 medical Droid", `combatPower`
  99999, forced trait `Industriousness 1` (`Defs/PawnKinds_OuterRim.xml:275`)
- Head type `RSW_DW_HeadType_Blank`; the whole droid is the body graphic.
- `skin` colour channel is `RGBA(255,255,255,255)` on both `first` and `second` — i.e. **an
  identity tint**. This sprite ships in the colours it was drawn in.

Sprites: `src/RimStarWars/Droidworks/Textures/OuterRim/Droid/FX7_{north,south,east}.png` —
three 256×256 frames, graphic path `OuterRim/Droid/FX7`.

## Is this one chassis or two? — settled

**One chassis. Two lines in the index, one thing in the game and one relationship in canon.**

- **Repo evidence:** an exhaustive filename search across `src/` finds exactly three FX
  textures (`FX7_north.png`, `FX7_south.png`, `FX7_east.png`) and **no `FX`, `FXseries`,
  `FX6` or `FX9` texture of any kind.** Exactly one race def and one pawnkind def mention
  FX. There is no second sprite for an "FX-series" row to describe, so a second entry would
  be an art-correction document about art that does not exist.
- **Canon evidence:** the **FX-7 article's own infobox carries `line=FX-series medical
  assistant droid`**, and the FX-series article says the series is a **ten-model series** of
  which **FX-9 and FX-7** are two named members. So canon's relation is **line → member**,
  not two rival models. The two index rows are a series and one of its units.
- ⚠️ **Not a pure duplicate, though.** The two articles differ on owners (FX-7: Republic +
  Alliance; FX-series: **Empire** + Alliance) and on continuity marking (`canon` vs
  `canon (+Legends)`), and their infobox images show **visibly different droids** — FX-7 is a
  tall blue-grey ribbed column, while the FX-series infobox picture is **FX-9**, a squat dark
  body with a row of red lamps. Merging the *entries* is correct; the surviving row should be
  read as **"the FX-series line, represented in this repo by its FX-7 member."** The 2026-09-15
  QA pass was right not to merge the index rows on a guess — they are not spelling variants.

## Canon variants this chassis covers

- **FX-7 medical assistant droid** — the unit the sprite actually depicts
  (`DROIDS_INDEX.md:697`, `canon`)
- **FX-series medical assistant droid** — a.k.a. **FX-series medical droid**, a.k.a.
  **"Fixits"**; a **ten-model** line (`DROIDS_INDEX.md:699`, `canon (+Legends)`)
- **FX-9 surgical assistant** — a named member of the line, no repo art, no index row of its
  own found in this batch's scope
- ⚠️ **Not this chassis:** the **FX-2 droid** and **FX-6 droid** are separate High Republic
  Era articles that the FX-series article explicitly calls out as merely *similarly named*.
  Do not fold them in.

## Sourced text (Wookieepedia)

The **FX-series medical assistant droid**, also called an **FX-series medical droid** or
**"Fixits"**, was a **medical droid that was part of a ten-model series manufactured by
Medtech Industries.** They were **often paired with 2-1B-series medical droids**, and were
**"designed with multiple arms and to look after patients, perform tests, operate equipment
and recommend procedures."** Infobox `equipment=`: **"Multiple arms and medical tools."**
Hera Syndulla's line, quoted in the article: **"That's a Medtech. FX-something."**
[FX-series medical assistant droid](https://starwars.fandom.com/wiki/FX-series_medical_assistant_droid)

The **FX-7 medical assistant droid** is a **Class one droid**, **1.7 meters tall** (5 ft
7 in), and its infobox names its `line` as the **FX-series**. **FX-7** monitored **Luke
Skywalker during his bacta treatment on Hoth**; another FX-7 aboard the *Tribunal* was used
by **Ahsoka Tano — she used one of the droid's arms to scan Rex's head for an inhibitor
chip**, and it failed to find it.
[FX-7 medical assistant droid](https://starwars.fandom.com/wiki/FX-7_medical_assistant_droid)

**FX-9** supplied the severely wounded **Darth Vader with a blood transfusion during his
major surgery** (*Revenge of the Sith*).

🔴 **Both articles are `{{Droid-stub}}`s and are extremely thin.** Between them there is
**no sourced plating colour, no sensor colour, no mass, no armament, no era, and no height
for the series as a whole.** For this chassis the images are doing nearly all the work, and
that is a limit of the sources, not an omission here.

## Provenance

- **Manufacturer:** **Medtech Industries**, for both the series and the FX-7 (both infoboxes,
  each cited to *Ultimate Star Wars*). `DROIDS_INDEX.md:697` and `:699` agree. Corroborated
  in-universe by Hera Syndulla identifying one on sight as "a Medtech."
- **Era:** **blank** on both articles — `firstmade=` and `retired=` are empty in both
  wikitexts. Do not infer one from *Empire Strikes Back*.
- **Typical owners:** **Galactic Republic** and the **Alliance to Restore the Republic**
  (FX-7 infobox); **Galactic Empire** and the **Alliance to Restore the Republic**
  (FX-series infobox — FX-9 served in the Empire's medical facility during Vader's surgery).
  So the line is **used by every major faction of both eras** and is not factionally marked
  — which makes it the most freely-placeable droid in this batch.

## Visual brief

**Overall shape and proportion — the whole read at sprite scale.** Canon FX-7 is **not a
biped and has no legs**: it is a **tapered vertical cylinder**, widest at a flared circular
base pedestal and narrowing as it rises, capped by a **stack of horizontal banded rings**
ending in a small domed sensor turret. Its one unmistakable feature is that **the entire
lower body is sheathed in a dense vertical bundle of many long thin jointed arms**, folded
flat against the drum like reeds, with **one or two arms extended outward** ending in a
clawed instrument cluster. Colour is **steel blue-grey**. Read at a glance: **a ribbed
blue-grey barrel wearing a crown of rings, with spider-thin arms hanging out of one side.**

**The repo sprite gets the body and misses the arms and the colour.**

- ✅ **The barrel silhouette is right, and right for the format.** A legless drum is easy to
  draw top-down and the sprite's rounded-rectangle body with a domed cap reads correctly as
  a cylinder standing on end. At sprite scale it will read as a canister, which is what this
  droid is.
- ✅ **The vertical ribbing is the right instinct.** `donor_current_sprite_south.png` covers
  the lower body in close-spaced vertical lines, which is a legible shorthand for canon's
  packed arm bundle. Keep it; if anything make the ribs coarser so they survive downscaling.
- ✅ **`MoveSpeed` 2.4 is defensible.** Canon FX-7 has no legs, so slow is correct — arguably
  it should barely move at all.
- 🔴 **Colour is wrong in the direction that matters most.** Canon FX-7 is distinctly
  **steel blue-grey**; the sprite is a **neutral charcoal-to-mid grey with no blue at all**,
  and the def's identity tint (`RGBA(255,255,255)`) means nothing corrects it at runtime. At
  RimWorld scale colour is most of the read, and a neutral grey canister is
  indistinguishable from a dozen other grey mechanoids in the stack. **Push it blue.** This
  is the single highest-value correction to this chassis.
- 🔴 **No arms break the silhouette.** Canon's extended arm-and-claw cluster is the feature
  that says *medical droid* rather than *barrel*, and it is the only part of the droid that
  projects. The sprite keeps every arm flush inside the outline, so from above there is
  nothing to distinguish it from a generic drum. **At least one arm should project past the
  body edge**, ideally in the `east` frame.
- ⚠️ **The FX-9 look is not served at all.** `wookieepedia_fx9_series_infobox.png` (the
  FX-series article's own infobox image) shows a **squat, rounded, near-black body with a
  horizontal row of bright red lamps across the front** and several splayed thin arms
  holding tools — a very different, much more sinister read than FX-7's tall pale column.
  If the campaign wants an Imperial-side surgical droid, that red lamp row is the cue, and
  **no repo art has it.**
- ⚠️ **Scale contradiction in the def.** `baseBodySize` is **0.75**, but canon FX-7 is
  **1.7 m** — about 94% of an adult human. It should be near 1.0. Report, do not fix.
  (Contrast the DUM pit droid, where 0.75 is roughly correct.)
- ⚠️ **The three frames are nearly identical**, differing only in the top cap's small boss
  and one short nub in the `east` frame. That is acceptable for a rotationally symmetric
  drum, but it does mean the droid never reads as facing anywhere.
- ⚠️ Cosmetic def issue: the label is **"fx-7 medical droid"** in lowercase, against the
  canon name **"FX-7 medical assistant droid"**. Not an art matter, but it will show in
  tooltips.

## Must show
- [ ] Legless, tapered vertical cylinder body, widest at a flared circular base pedestal
- [ ] Steel blue-grey plating, not neutral grey
- [ ] Dense vertical ribbing over the lower body (the folded arm bundle)
- [ ] Stack of horizontal banded rings near the top, capped by a small domed sensor turret
- [ ] At least one clawed instrument arm projecting past the body's outline

## Engine limits
The `skin` colour channel is set to identity white (`RGBA(255,255,255)`), a no-op tint — colour cannot be corrected through the def as it stands; the canon steel blue-grey requires a repaint.

## Source URLs

- https://starwars.fandom.com/wiki/FX-7_medical_assistant_droid — wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=FX-7_medical_assistant_droid&format=json&prop=wikitext`
  (6,563 bytes of JSON, read in full). **Tagged `{{Droid-stub}}`; the entire body is two
  sentences.**
- https://starwars.fandom.com/wiki/FX-series_medical_assistant_droid — same API pattern
  (6,048 bytes, read in full). **Also tagged `{{Droid-stub}}`.**
- https://static.wikia.nocookie.net/starwars/images/4/43/FX-7-BYOR2D2-19.png →
  `wookieepedia_fx7.png` (480×875; Fandom served WebP, re-saved as PNG locally)
- https://static.wikia.nocookie.net/starwars/images/0/0b/FX-9_Medical_Droid_SWL.png →
  `wookieepedia_fx9_series_infobox.png` (1044×720; same conversion)
- **Named in the articles but not fetched this pass:** `FX-9 surgical assistant`,
  `FX-2 droid`, `FX-6 droid`, `2-1B surgical droid`.
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_OuterRim.xml`,
  `Defs/PawnKinds_OuterRim.xml`
- Index rows: `design/RimStarWars/canon_references/DROIDS_INDEX.md:697` and `:699`
- 🔴 **Not sourceable this pass:** plating colour, sensor colour, mass and era are absent
  from **both** infoboxes. The "steel blue-grey" colour claim in the visual brief above comes
  **only from `wookieepedia_fx7.png`**, i.e. from the image, not from any prose. Per the
  brief's rule, the image is trusted on appearance — but it is a single image, so treat the
  colour as image-derived rather than text-sourced.

## Candidate images

- `wookieepedia_fx7.png` (480×875) — the FX-7 article infobox: full-length front view on
  white. **The proportion and colour authority for this chassis.** Tapered steel-blue-grey
  cylinder on a flared base, banded ring stack and small sensor turret on top, the lower body
  sheathed in a dense vertical bundle of thin jointed arms, one arm extended right with a
  clawed instrument cluster. No legs.
- `wookieepedia_fx9_series_infobox.png` (1044×720) — the **FX-series** article infobox, which
  actually depicts **FX-9** in a *Star Wars: Legion* illustration: squat rounded near-black
  body, **horizontal row of red lamps**, several thin tool arms, in a dark red-lit surgical
  bay. Use as the reference for the *other* end of the line — and as evidence that the two
  index rows are not describing the same-looking droid, even though they share one sprite.
- `donor_current_sprite_south.png` (256×256) — repo `FX7_south`, top-down. What the repo
  ships: charcoal ribbed drum, grey domed cap with a central boss. **Judge as-is** — the
  def's tint is identity white.
- `donor_current_sprite_east.png` (256×256) — repo `FX7_east`. Near-identical to south; one
  small nub on the cap is the only difference.
- `donor_current_sprite_north.png` (256×256) — repo `FX7_north`.

## ruling

(empty — the owner has not reviewed this chassis yet)
