# GE3 (KotOR)

**defName**: a race + pawnkind pair, not a xenotype. Real defs on disk:
- `RSW_DW_Race_guy762_DroidRace_GE3PD` — label "GE3-series protocol droid"
  (`src/RimStarWars/Droidworks/Defs/Races_KotOR.xml:214`), parent `DW_Family_Protocol`
- `RSW_DW_Race_guy762_DroidRace_GE3LD` — label "GE3-series **labor** droid"
  (same file, `:246`), parent `DW_Family_Labour` — **shares the same body and head textures**
- Head types: `RSW_DW_HeadType_guy762_DroidRace_GE3PD` and `_GE3LD` (same file, `:23` and `:28`)
- PawnKinds (`Defs/PawnKinds_KotOR.xml`): `RSW_DW_KotORDroidColonist_GE3PD` (`:103`),
  `RSW_DW_KotORDroidColonist_GE3LD` (`:84`), `RSW_DW_KotORDroidGood_GE3PD` (`:534`),
  `RSW_DW_KotORDroidGood_GE3LD` (`:558`)

Sprites: `src/RimStarWars/Droidworks/Textures/KotOR/Droid/GE3/GE3_{body,head}_{north,south,east}.png`
plus `GE3_{bodymask,headmask}_*`. **There is no `_west` texture** — RimWorld mirrors east, so
this is normal, not a gap.

## Canon variants this one repo chassis covers
- **GE3-series protocol droid** — the only canon row assigned to this chassis

The repo's second race, "GE3-series **labor** droid", is **not a canon model name.** It is a
repo-side split of the same chassis. See the note under Provenance — canon does support the idea
that many physically identical GE3 sub-models existed with different skills, so the split is
defensible even though the specific name is invented.

## Sourced text (Wookieepedia)

The **GE3-series protocol droid** was a **bipedal protocol droid manufactured by Czerka
Corporation**. It "vaguely resembl[ed] later models from Cybot Galactica" — i.e. it is the
Old-Republic ancestor of the C-3PO silhouette — and GE3s were **"one of the most common and
best-selling droids in the galaxy" during both the Jedi Civil War and the Dark Wars.**
[GE3-series protocol droid](https://starwars.fandom.com/wiki/GE3-series_protocol_droid)

**Sourced infobox figures** (from the article's `{{DroidSeries}}` box, cited to the
`Knights of the Old Republic Campaign Guide` — the article's **only** source):
- **Class:** protocol droid
- **Cost: 2,500 credits**
- **Sensor colour: blue, yellow, and white**
- **Armament: None**
- **Equipment:** audio recorder · comlink
- **Gender:** *"Both masculine and feminine programming"* — with a footnote that **S4-C8-GE3 is
  the only known GE3 with feminine programming**
- **`plating`, `height`, `width`, `length`, `mass`, `degree`, `affiliation`, `firstmade`,
  `retired`: ALL BLANK.** So: **no sourced colour, no sourced size, no sourced mass, no era.**
  Recorded as absent, not guessed. This is a genuinely thin article — 3,914 characters of
  wikitext, one source, no History section.

**Characteristics, from the article:**
- **Programmable for many roles:** waiter, bartender, tour guide, receptionist, secretary,
  errand-runner, diplomatic aide, **medical droid**, or even **swoop pilot.** (Note the medical
  and pilot roles — this is a general-purpose social chassis, not a narrow translator.)
- Programming "specifically designed for social tasks, with an emphasis on **Human-cyborg
  relations** and a massive database of languages, cultures, and customs of thousands of
  species."
- **Vocabulators with versatile translator units.**
- **⭐ Sourced mass-market economics, useful for a scavenger setting:** demand was high, they
  were "a common sight on nearly every planet in the Galactic Republic," and **Czerka sold them
  in bulk at a significant discount to planetary governments.** This is the most abundant droid
  chassis in the batch — the one that should be lying around everywhere.
- **⭐ Sourced naming convention:** *"There were numerous models, physically identical, but
  differing in internal details and skills. Each GE3 had a full designation which included the
  suffix 'GE3' at the end, for example, S-0D3-GE3."* Named units on the wiki: 1B-8D-GE3,
  B-4D4-GE3, B-4R5-GE3, B-5D8-GE3, C6-E3-GE3, C7-E3-GE3, C8-42-GE3, C9-T9-GE3, S-0D3-GE3,
  S4-C8-GE3, TT-32-GE3. **If this chassis needs a name generator, that is the pattern:
  `<2-4 alphanumerics>-<2-4 alphanumerics>-GE3`.**
- The Jedi Exile found a note about Czerka-produced droids left by **Dergar Chester**, head
  technician of the Jedi Enclave, in the Enclave sublevel.

**Behind the scenes / canon crossover:** in the **canon** short comic *"Off the Rails"*, the
featured croupier droid **greatly resembles** the GE3-series. That is the article's only link to
current canon, and it is a resemblance claim about a background droid, not a canon description
of the GE3.

**⚠️ Continuity status: this article is explicitly Legends** (`{{Top|leg}}`, no canon counterpart
named). `DROIDS_INDEX.md:724` marks this row `canon`; that column value is wrong for this row.
**This chassis rests on KotOR game assets and one Legends sourcebook. There is no canon
description of a GE3, and no sourced plating colour anywhere** — so any colour decision the
owner makes here is authorship, not correction.

## Provenance
- **Manufacturer:** **Czerka Corporation** (Czerka Arms)
  [GE3-series protocol droid](https://starwars.fandom.com/wiki/GE3-series_protocol_droid)
  (also `Category:Czerka Arms products`). Note this puts GE3 and the **HK-series** under the
  same manufacturer — and the HK article's whole premise is that Czerka disguised assassins **as
  protocol droids to get around laws banning assassin droids** (`Red Harvest`). The GE3 is the
  innocuous Czerka protocol droid that disguise trades on. That connection is worth keeping.
- **Era:** **blank.** `firstmade` and `retired` are both empty. The only sourced time anchors
  are relative: best-selling during the **Jedi Civil War** and the **Dark Wars**.
- **Typical owners:** the infobox `affiliation` field is **blank**, and `DROIDS_INDEX.md:724`
  correspondingly leaves the owners column blank. What the body text attests: **planetary
  governments of the Galactic Republic** (bulk purchases at a discount), and effectively
  everyone — "a common sight on nearly every planet in the Galactic Republic." Attested
  individual employers: cantinas and bars (waiter/bartender roles), tour operations, offices
  (receptionist/secretary), diplomatic staffs, medcentres, swoop racing, and the **Jedi Enclave**
  on Dantooine.
  [GE3-series protocol droid](https://starwars.fandom.com/wiki/GE3-series_protocol_droid)

## Visual brief

**This is the chassis where the sprite is most faithful and the canon prose is most useless.**
The article gives **no plating colour and no dimensions at all**, so `wookieepedia_ge3_infobox.jpg`
is the *only* appearance evidence, and it must be trusted outright.

What the canon render shows:
- A **tall, lean, humanoid biped** in the C-3PO mould — the article's "vaguely resembling later
  models from Cybot Galactica" is exactly right.
- **Plating is weathered gunmetal / dull pewter with green-grey oxidation and brown grime** —
  emphatically **not** gold, and not clean. It reads as second-hand industrial metal.
- **Black ribbed/segmented sleeves at the upper arms, waist, upper thighs and knees** — dark
  flexible joint bellows against pale hard plates. This high-contrast light-plate /
  dark-bellows alternation is the chassis' single most recognisable cue.
- **Head:** a narrow faceted skull with a **large circular plate/disc on the crown**, two small
  round photoreceptors set wide, and a **vertical ribbed grille where a mouth would be**
  (the vocabulator). The infobox `sensor=Blue, yellow, and white` is not clearly readable in
  this render.
- **Hands are fully articulated five-fingered manipulators** — the render's raised right hand is
  a deliberate "presenting" protocol-droid gesture.
- **Feet are broad flat pads** with a visible ankle joint.

Against `donor_current_sprite.png` (`GE3_body_south`, 512×512) and
`donor_current_sprite_head.png` (`GE3_head_south`, 512×512):

- **✅ The light-plate / dark-bellows alternation survives, and it is the right call.** The
  sprite's torso is pale grey with a **dark ribbed waistband** and **dark ribbed bands at the
  upper thighs/knees**, plus dark shoulder recesses. That is the canon cue, correctly picked out
  as the thing worth keeping at sprite scale.
- **✅ The chest plate shape reads correctly** — a keeled central breastplate with a vertical
  seam and a small circular fitting at upper left, both present in the canon render.
- **✅ The narrow shoulders / tapered waist / separated legs silhouette** is a fair top-down read
  of a lean humanoid protocol droid.
- **⚠️ Colour is unresolved rather than wrong.** `RSW_DW_Race_guy762_DroidRace_GE3PD` declares
  **no `colorChannels` block at all** (`Races_KotOR.xml:214–243`), so the protocol variant
  inherits whatever `DW_Family_Protocol` (`Races_Families.xml:80`) supplies. The **labor**
  variant *does* set colours explicitly: `RGBA(80,115,125,255)` (a desaturated teal-grey) over
  `RGBA(205,155,130,255)` (a warm tan). **Neither can be called a canon error, because canon
  gives no plating colour.** But the teal-grey primary is a reasonable match to the render's
  green-grey oxidised metal, and the warm tan second channel is *not* something the render
  supports. **Recommendation for the owner: judge these two in-game side by side; the render
  argues for weathered pewter with green-grey oxidation for both.**
- **⚠️ The head sprite is the weak asset.** The canon head's distinguishing features are the
  **crown disc**, the **wide-set round photoreceptors** and the **vertical grille mouth**. At
  512×512 top-down the donor head is a small pale wedge and none of those three read clearly.
  The head is where a correction would buy the most recognition.
- **⚠️ `MoveSpeed 1` on the protocol variant** (against `2` on the labor variant) is very slow.
  Canon offers no speed statement either way, but it is worth noting canon GE3s were programmed
  as **errand-runners and swoop pilots** — not obviously a shuffling chassis.
- **✅ Unarmed is correct** — canon `armament=None`.
- **⭐ The repo's two-races-one-texture arrangement is canon-supported.** Canon: *"numerous
  models, physically identical, but differing in internal details and skills."* GE3PD and GE3LD
  sharing `GE3_body` / `GE3_head` and differing only in colour and stats is precisely that. The
  invented part is only the word "labor" as a model name.

## Must show
- [ ] Weathered gunmetal/dull pewter plating with green-grey oxidation and brown grime, not gold and not clean
- [ ] Black ribbed/segmented bellows at the upper arms, waist, upper thighs, and knees against pale hard plates
- [ ] Keeled central breastplate with a vertical seam
- [ ] Narrow tapered waist and separated legs on a lean humanoid silhouette
- [ ] Head shows a large circular plate/disc on the crown, wide-set round photoreceptors, and a vertical ribbed grille mouth

## Engine limits
The protocol variant (GE3PD) defines no `colorChannels` block of its own and inherits whatever `DW_Family_Protocol` supplies, so its colour cannot be tuned independently of the parent family without adding an override.

## Source URLs
- https://starwars.fandom.com/wiki/GE3-series_protocol_droid — main article; text pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=GE3-series_protocol_droid&format=json&prop=wikitext`
  (3,914 chars of wikitext, read in full — no truncation). **Single-source article**
  (`Knights of the Old Republic Campaign Guide`), no History section.
- https://static.wikia.nocookie.net/starwars/images/4/48/CzerkaDroid.jpg → `wookieepedia_ge3_infobox.jpg`
- Named in the article but **not fetched this pass**: the eleven notable units
  (`S-0D3-GE3`, `S4-C8-GE3`, `B-4D4-GE3`, etc.), `Off the Rails (comic story)`,
  `Dergar Chester`
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_KotOR.xml`,
  `src/RimStarWars/Droidworks/Defs/PawnKinds_KotOR.xml`,
  `src/RimStarWars/Droidworks/Defs/Races_Families.xml`

## Candidate images
- `wookieepedia_ge3_infobox.jpg` (544×792) — the `{{DroidSeries}}` infobox image
  (`File:CzerkaDroid.jpg`), a KotOR model render on flat grey, full body, three-quarter view
  with the right hand raised in a presenting gesture. **The only appearance evidence that
  exists for this chassis**, and therefore authoritative on colour: weathered gunmetal/pewter
  with green-grey oxidation and brown grime, black ribbed bellows at arms/waist/thighs/knees,
  crown disc on the head, wide-set round photoreceptors, vertical grille mouth, five-fingered
  hands, broad flat feet.
- `donor_current_sprite.png` (512×512) — the repo's `GE3_body_south` donor. Pale grey torso,
  dark ribbed waistband and thigh bands, keeled breastplate. Maskable (`GE3_bodymask_south`).
- `donor_current_sprite_head.png` (512×512) — the repo's `GE3_head_south` donor. Small and
  featureless relative to the canon head; the crown disc, photoreceptors and grille do not read.

## ruling
(empty — the owner has not reviewed this chassis yet)
