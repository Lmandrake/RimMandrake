# R-8009 utility droid (repo chassis: R8-009, KotOR)

**defName**: not a xenotype. Real defs on disk:
- `RSW_DW_Race_guy762_DroidRace_R8009UD` — label **"R-8009 series utility droid"**,
  `ParentName="DW_Family_Astromech"`, `baseHealthScale` 0.8, `MoveSpeed` 3,
  `customDrawSize` **(0.9)**, `headTypes` = `RSW_DW_HeadType_Blank` (the whole droid is one
  body sprite) — `src/RimStarWars/Droidworks/Defs/Races_KotOR.xml:615`
- PawnKindDefs: `RSW_DW_KotORDroidColonist_R8009UD`
  (`src/RimStarWars/Droidworks/Defs/PawnKinds_KotOR.xml:65`) and
  `RSW_DW_KotORDroidGood_R8009` (same file, :510)

Sprites: `src/RimStarWars/Droidworks/Textures/KotOR/Droid/R8009/R8009_{south,east,north,west}.png`
with `R8009_mask_{south,east,north,west}.png` — 512×512, greyscale, two-channel masked.
**This chassis has all four directions**, unlike several others in the KotOR donor. There is
no `design/Jawa/fauna/sprites/` file for it.

⚠️ **Taxonomy note, not a canon error:** the repo files it under
`ParentName="DW_Family_Astromech"`, but canon classes it a **maintenance droid, Class 5**
(the infobox `class`/`degree`), and it is not an astromech. The family assignment is a repo
mechanical grouping; do not read it as a canon claim.

## Canon variants this one repo chassis covers

- **R-8009 utility droid** — the only canon row (`DROIDS_INDEX.md:1336`). One canon model,
  one repo chassis.

⚠️ **The index's continuity column is wrong for this row.** `DROIDS_INDEX.md:1336` marks it
`canon`; the article opens `{{Top|leg}}` and every internal link is a `/Legends` link. This
is a **Legends** droid — sole appearance *Star Wars: Knights of the Old Republic*, sole
source the *Knights of the Old Republic Campaign Guide*. No current-canon counterpart exists.

⚠️ **Slug/name note.** The repo and this entry's slug use **R8-009**; the canon article title
is **R-8009 utility droid**, and the def/texture paths use **R8009**. All three refer to the
same droid; the canon spelling is `R-8009`.

## Sourced text (Wookieepedia)

The **R-8009 utility droid** was a **maintenance droid** manufactured by **Serv-O-Droid,
Inc.**, "and used during the **Old Republic era** for a number of functions such as **basic
maintenance and cleaning**."
[R-8009 utility droid](https://starwars.fandom.com/wiki/R-8009_utility_droid)

🔑 **Its one distinguishing capability, verbatim:** "Unlike other utility droids of that era,
the R-8009 had the skills and hardware to **directly interface with other droids and
computers**, which allowed the owner to program the droid to **return to a designated
computer terminal and receive new instructions** without the need for another droid to
constantly update the R-8009's programming." That is the whole point of the model — it is a
*self-retasking* cleaner, and it is the only droid in this batch whose sourced special
ability is a software one.

"**Cheap, relatively skilled, and capable of operating quietly, subtly, and unobtrusively
around living beings**, the R-8009 could be found everywhere from the **Deep Core** to the
**Outer Rim**." A cheap, ubiquitous, quiet Outer Rim maintenance droid is an unusually good
fit for a scavenger campaign, and every word of that sentence is sourced.

Infobox fields: `class` **Maintenance droid**, `degree` **Class 5**, `cost` **800 credits**
(the cheapest of the five chassis in this batch, against the K-X12's 6,000), `sensor`
**Black**, `plating` **Yellow**.

⚠️ **This is a very short article** — a lead plus one paragraph, ~1.8 KB of wikitext, read in
full. There is no History section, no named individual unit, no named owner and no named
world. What is absent here is genuinely absent from the source, not unread.

**Unsourced and therefore absent:** height, mass, length, width, homeworld, designer,
`firstmade` / `retired`, `affiliation`, `armament`, `equipment`.

## Provenance

- **Manufacturer:** **Serv-O-Droid, Inc.** — infobox and body text agree, and the article
  carries `[[Category:Serv-O-Droid, Inc. products]]`. `DROIDS_INDEX.md:1336` agrees.
  [R-8009 utility droid](https://starwars.fandom.com/wiki/R-8009_utility_droid)
- **Era:** **blank** as an infobox value — `firstmade` and `retired` are both empty. ⚠️ The
  body text *does* name the **Old Republic era** in prose ("used during the Old Republic
  era"), which is unusual for a droid article; it is recorded here as a cited prose statement
  and **not** promoted into the era field, per the brief.
- **Typical owners:** ⚠️ **none recorded.** The infobox `affiliation` field is empty and
  `DROIDS_INDEX.md:1336` carries a blank owners column. No faction, species or world owns
  this droid. The only sourced statement about who had them is geographic and deliberately
  broad — "could be found everywhere from the **Deep Core** to the **Outer Rim**" — i.e. a
  generic commercial droid, sold to anyone. That absence is the answer, not a gap.
  [R-8009 utility droid](https://starwars.fandom.com/wiki/R-8009_utility_droid)

## Visual brief

**The silhouette is a strong match.** Canon (`wookieepedia_r8009_infobox.jpg`, an in-game
KotOR render on desert ground) is a **squat legless-looking tub**: a **tapered barrel body**,
wider at the top, capped by a **low domed lid** with **two thin whip antennae** rising from
it; a **large dark barrel-lens photoreceptor assembly** set into the front of the dome rim,
with a **small iridescent round light** beside it; and below the body a chunky chassis
carrying **two wide truncated-cone feet** splayed out to the sides. The repo `south` sprite
reproduces every one of those elements, in the right proportions — barrel body, domed cap,
two antennae, offset lens, small light, and the two splayed cone feet.

**Judge the sprite tinted, never as the raw grey PNG.** `R8009_mask_south.png` is a
two-channel mask, and the split is meaningful:
- **red (`skin` `first` = `RGBA(190,170,120,255)`)** covers the **main barrel body**, the
  lens surround, and the **cylindrical part of each foot**;
- **green (`second` = `RGBA(130,140,155,255)`)** covers the **domed cap, the antennae, the
  lower chassis block, and the cap of each foot** plus their vertical detail strips.

✅ **The second channel is right.** `RGBA(130,140,155)` is a slate blue-grey, and the canon
dome, antennae, lower chassis and foot caps are exactly that slate blue-grey. The mask/def
pairing reproduces canon's two-tone construction correctly, element for element.

🔴 **The first channel is the finding, and the prose and the image disagree about it.**
- The **infobox says `plating = Yellow`.** The def's `RGBA(190,170,120)` is a pale sandy
  yellow-tan — so **the def matches the infobox text.**
- **The image does not.** The canon render's barrel body and foot cylinders are a distinctly
  **saturated rust-orange / terracotta brown**, several steps darker and much more saturated
  than a sandy yellow.
- Per the brief, **trust the image on appearance**: the body should be a warm ochre /
  rust-orange, not a pale sand. ⚠️ One honest caveat: this render is an in-game shot on
  **bright sand under warm desert light**, which will push a yellow plating warmer, so part
  of the orange may be lighting rather than albedo. But the shift is large — the plating
  reads brown-orange even in the shaded lower body and in shadow — so lighting does not
  account for all of it. The defensible correction is a **warmer, more saturated ochre**
  somewhere between the def's sand and the render's terracotta.
- 🔑 For a desert-world campaign this matters less than usual and more usefully: a sand-tan
  droid on a sand map is nearly invisible, whereas the canon rust-orange reads clearly
  against desert ground. Canon and legibility point the same way here.

✅ **The sensor is right.** Infobox `sensor = Black`, canon render shows a **black barrel
lens**, and the sprite's lens is drawn black in the base texture (it is *not* on either
colour channel, so it stays black whatever the def says). The small green light beside it in
the sprite matches the small iridescent light in the render.

**No repo art contradiction between directions:** all four frames exist and share the mask
scheme, so the correction above is one value in one def, not a repaint.

**Not depicted anywhere:** the article's one special capability — the computer/droid
interface that lets it self-retask — has **no visual cue at all**, in canon or in the sprite.
Canon gives it no visible dataport or probe arm. So there is nothing to correct there; it is
a behavioural trait with no appearance.

## Source URLs

- https://starwars.fandom.com/wiki/R-8009_utility_droid — main article; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=R-8009_utility_droid&format=json&prop=wikitext`
  (1,807 bytes of JSON — the shortest of the batch, **read in full, no truncation**).
  Rendered HTML is Cloudflare-walled; the API is not.
- https://static.wikia.nocookie.net/starwars/images/2/24/Utility1.jpg
  (File:Utility1.jpg, 529×698) → `wookieepedia_r8009_infobox.jpg`
- ⚠️ **This is the article's only image**, and the article carries **no `{{Mediacat}}`** at
  all, so there is not even a linked image category to hunt further in. No second angle, no
  scale reference, no clean-background render. The `east`/`north`/`west` sprite frames
  therefore **cannot be checked against canon** this pass.
- Named in the article but **not fetched this pass**:
  https://starwars.fandom.com/wiki/Serv-O-Droid,_Inc.,
  `Maintenance droid/Legends`, `Class five droid/Legends`, `Old Republic era`
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_KotOR.xml`,
  `src/RimStarWars/Droidworks/Defs/PawnKinds_KotOR.xml`

## Candidate images

- `wookieepedia_r8009_infobox.jpg` (529×698) — the article's sole image: in-game KotOR
  render, front three-quarter, standing on desert ground with a cast shadow. **Rust-orange /
  terracotta barrel body and foot cylinders; slate blue-grey domed cap, antennae, lower
  chassis and foot caps; black barrel lens with a small iridescent light beside it.** The
  colour and proportion authority — and the reason the def's pale-sand body colour is flagged.
  Weak on detail (game-era texture resolution) and warm-lit, which is noted above.
- `donor_current_sprite.png` (512×512) — repo `south` frame
  (`Textures/KotOR/Droid/R8009/R8009_south.png`, byte-identical copy). Greyscale /
  two-channel masked; must be judged tinted with `RGBA(190,170,120)` (body, foot cylinders)
  and `RGBA(130,140,155)` (dome, antennae, chassis, foot caps). Silhouette is a good canon
  match; the body hue is the open question.

## ruling

(empty — the owner has not reviewed this chassis yet)
