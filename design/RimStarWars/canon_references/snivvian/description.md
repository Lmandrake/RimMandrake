# Snivvian

**defName**: `RSW_RimMandrakeSnivvian` (verified present in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Matrix placement `Jawa_Junkers: S` — some, so a recurring face in the scrapper faction
rather than a crowd.

## Sourced text (Wookieepedia)

**Canon.** Snivvians, nicknamed **Snaggletooths**, were a species of sentient
**mammalian humanoids** native to **Cadomai Prime**. They had **large mouths and
short fangs**. The **winters on their home planet were long, harsh, and difficult
to survive**; during winter the Snivvians spent their time in **underground caverns
in artistic pursuits**. Some escaped the icy tundras to become bounty hunters
offworld — **as a species they displayed great tracking skills**, so were
particularly suited to that work.

Infobox (canon): class **mammalian**; **distinctions — protruding lower jaw and
large nostrils; two small tusks**; origin **Cadomai Prime**; habitat **ice and
snow**; skin colour listed as blue, brown, yellow, fair, light, pale, pink, white,
grey; **hair colour black or brown**; eye colour black, blue, gold, green.
**No height, mass or lifespan is given in canon** — UNMEASURED, do not invent one.

An in-universe artist's journal quoted in *Star Wars: Alien Archive*:
> "I met a couple of snaggletooths in the cantina looking for work. **Their thick
> hides were unsuited to the heat in the desert!**"

🔑 That line is the single most campaign-relevant fact in the article: a Snivvian on
a **desert** world is canonically **out of its element in the heat**.

**Legends** (`Snivvian/Legends`, cited for the numbers canon lacks — mark them as
Legends if used): **height 1.4 meters**; **lifespan up to 105 standard years**;
skin brown, hair brown, eyes black; distinctions **thick skin, protruding jaws,
short fangs**. Sometimes called Snaggletooths **due to their protruding jaws and
short fangs**. They came from a planet with a cold environment, but **had evolved to
have thick skin instead of fur**. **Due to their oversized snouts, Snivvians made
excellent scouts and trackers.** Snivvians were **among the most renowned artists
and authors in the galaxy**, channelling hardship into their artistic work; their
culture was nearly destroyed by Thalassian slavers before the Republic intervened.

**Unusual abilities.** Nothing exotic — no Force affinity, no toxin, no
regeneration. The species' two mechanically interesting traits are both sensory /
skill claims: **tracking and scouting by scent** (the oversized snout, canon and
Legends agreeing), and **artistic output** (Legends, strongly). Cold tolerance is
environmental, not an ability.

## Visual brief

**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."** The three animated images were deleted: `wookieepedia_unidentified_snivvian.jpg` (*Bad Batch* CGI), `wookieepedia_kattmol_tcw.jpg` (*Clone Wars* Katt Mol) and `wookieepedia_sinrich_legends.jpg` (*Clone Wars*-style encyclopedia render of Sinrich). Added the original Databank photograph of the 1977 practical mask (`wookieepedia_databank_mask_photo.jpg`). What remains is all realistic: two practical-mask photos, the realistic Ankeefo render, and the painted KOTORCG portrait.

🔑 **The practical mask is the target look:** pinkish-tan to grey-brown deeply wrinkled leathery skin, a wide flat-fronted snout with two huge round nostrils, a heavy jutting lower jaw curling up into a lopsided toothy grin with small uneven yellowed teeth and one small tusk, small glossy dark eyes with pink rims high under a ridged brow, and **wispy, thin, unkempt brown hair** on the crown.

What every image shows:

- **A broad, flat, forward-projecting muzzle carrying two enormous rounded nostrils
  on its front face.** This is the silhouette. The nostrils are the largest feature
  of the face — bigger than the eyes — set side by side on the snout's flat front,
  not underneath it. "Large nostrils" in the text is an understatement.
- **A heavy, protruding lower jaw and thick lower lip**, giving a mouth line that
  curves *upward* at the corners into what reads as a permanent lopsided grin. In
  `wookieepedia_databank_mask_photo.jpg` small uneven yellowed teeth sit exposed
  along the grin.
- **Small, deep-set eyes placed high and wide** under a heavily wrinkled,
  shelf-like brow. Small eyes on a large blunt head is the proportion to hit.
- **Leathery, wrinkled, hairless facial skin** — creases radiate from the eyes and
  run across the muzzle and throat. This matches Legends' "thick skin instead of
  fur" and is the texture the sprite needs; a smooth face is wrong.
- **Small, rounded, low-set ears**, close to the skull — human-ish in placement,
  never pointed or large.
- **Short, stocky, wide-shouldered build** with a thick neck and no waist,
  consistent with the Legends 1.4 m and with the def's `RSW_BodySizeGene_small`.

🔴 **Tusks: canonical, but small, lower-jaw, upward-curving, and NOT universal.**
This is the finding most likely to be got wrong.
- `wookieepedia_kotorcg_portrait.jpg` (painted, the clearest) shows **two white
  tusks emerging from the corners of the lower jaw and curving upward** across the
  outside of the muzzle, tips ending roughly level with the nostrils.
- `wookieepedia_snaggletooth_cardtrader.jpg` (Zutton, the original 1977 cantina
  mask) shows **a single small yellowish tusk** at one mouth corner only.
- `wookieepedia_infobox_ankeefo.jpg` shows **no tusks at all.**
So: two small tusks is the modal case, one or none occurs, and they rise from the
**lower** jaw at the mouth corners. **Downward boar tusks, or upper-jaw tusks, are
wrong.** They are also *small* — the repo's gene is labelled "large tusks" (see
below), which pushes the sprite past canon.

🔴 **Hair: the images contradict the def's "brown and black" and go beyond the
canon infobox.** Trust the images.
- `wookieepedia_infobox_ankeefo.jpg`: **long, thick, curly grey hair** worn as a
  full mane past the shoulders.
- `wookieepedia_snaggletooth_cardtrader.jpg`, `wookieepedia_databank_mask_photo.jpg`:
  thin, wispy, unkempt brown hair (the practical mask).
- `wookieepedia_kotorcg_portrait.jpg`: near-bald with light stubble.
**Grey is attested in the realistic art (blond appeared only in the deleted animated images) and absent from both the canon infobox and
the def's gene list.** Hair is head-only; there is no body fur in any image.

**Skin** varies as widely as the text promises and the images bear it out
individually: mid-brown and leathery (Ankeefo), pinkish-tan to grey-brown
(Zutton practical mask), warm ochre (KOTORCG portrait). **No two agree**, which makes the def's wide skin range correct and
means skin hue is not a thing a sprite has to commit to.

**No donor sprite exists.** There is no `snivvian/` texture directory anywhere under
`src/RimStarWars/StarWarsRaces/Textures/` — the xenotype builds its face out of
generic parts (`Nose_Pig`, `Jaw_Heavy`, `RSW_Face_tusks`) and carries the **vanilla
placeholder icon** `UI/Icons/Xenotypes/Custom/CustomXenotypeIcon1`, not a Star Wars
icon. So there is nothing on disk to compare canon against, and `donor_current_sprite.png`
is absent by fact, not by oversight.

## Must show
- [ ] Broad, flat, forward-projecting muzzle carrying two enormous rounded nostrils on its front face — the largest feature of the face, bigger than the eyes
- [ ] Heavy, protruding lower jaw with a thick lower lip, giving a mouth line that curves upward at the corners into a lopsided grin
- [ ] Small, deep-set eyes placed high and wide under a heavily wrinkled, shelf-like brow
- [ ] Leathery, wrinkled, hairless facial skin — never a smooth face
- [ ] Where tusks appear, they are small, rise from the lower jaw at the mouth corners, and curve upward — never downward boar tusks, upper-jaw tusks, or present on every individual
- [ ] Short, stocky, wide-shouldered build with a thick neck and no waist
- [ ] Realistic rendering: natural leathery practical-mask skin texture and lighting, no outlines, no cartoon shading

## Engine limits
none known

### 🔴 Def-versus-canon contradictions (report only, do not fix)

- **`RSW_Face_tusks` is labelled "large tusks"** (`Defs/GeneDefs/SW_Genes.xml:1610`,
  "Carriers of this gene grow large tusks") where canon says **two *small* tusks**.
  Wrong magnitude, and the shared texture is the one also used by Aqualish/Gamorrean
  /Kaleesh tusks.
- **Hair colour genes include `Hair_DarkSaturatedReddish` and `Hair_DarkReddish`.**
  Red hair is **unsourced** — canon lists only black and brown, and the art adds grey
  and blond. Neither grey nor blond is in the gene list.
- **`MinTemp_SmallDecrease` with no matching heat penalty.** Canon's one quoted line
  about Snivvians in a desert is that their **thick hides were unsuited to the
  heat**. On a desert world that is the trait that should be felt, and it is absent;
  only the cold bonus is present.
- **`AptitudeTerrible_Social` is unsupported.** Canon and Legends make them renowned
  **artists and authors** (`AptitudeRemarkable_Artistic` is well founded) and cast
  them as bounty hunters and confidence men — Marn Hierogryph is a Legends con
  artist. Nothing sources a social deficit.
- **`Beauty_Ugly` + `Turn_Gene_LowBeautyStandard` are an aesthetic judgement, not a
  sourced trait.** Recorded, not argued.
- **Nothing represents the canonical scouting/tracking sense** — "great tracking
  skills" (canon) / "oversized snouts made them excellent scouts and trackers"
  (Legends). No aptitude, no gene.
- **The xenotype ships a vanilla placeholder icon** (`CustomXenotypeIcon1`) rather
  than a Star Wars xenotype icon.

## Source URLs

- https://starwars.fandom.com/wiki/Snivvian — canon article. Direct HTML is
  Cloudflare-walled; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Snivvian&format=json&prop=wikitext`
  (200, 29,547 chars, 2026-09-15).
- https://starwars.fandom.com/wiki/Snivvian/Legends — Legends article, same API
  route (200, 13,678 chars, 2026-09-15). Source of the 1.4 m height, 105-year
  lifespan, "thick skin instead of fur" and the scout/tracker claim.
- https://static.wikia.nocookie.net/starwars/images/d/d7/Ankeefo-MandoVG.png (File:Ankeefo-MandoVG.png, canon infobox image → `wookieepedia_infobox_ankeefo.jpg`)
- https://static.wikia.nocookie.net/starwars/images/0/06/Snaggletooth_CT.png (File:Snaggletooth CT.png, Zutton → `wookieepedia_snaggletooth_cardtrader.jpg`)
- https://static.wikia.nocookie.net/starwars/images/0/04/Snivvian.jpg (File:Snivvian.jpg, original Databank photo of the practical mask → `wookieepedia_databank_mask_photo.jpg`)
- https://static.wikia.nocookie.net/starwars/images/a/a3/Snivvian_KOTORCG.jpg (File:Snivvian KOTORCG.jpg, *Knights of the Old Republic Campaign Guide* portrait → `wookieepedia_kotorcg_portrait.jpg`)
- NOT fetched this pass: https://www.starwars.com/databank/snivvian (the canon
  article cites a Databank entry for the "protruding lower jaw and large nostrils"
  line; the Databank page itself was not retrieved).

## Candidate images

- `wookieepedia_infobox_ankeefo.jpg` — **the reference of record for build and
  costume.** The canon infobox image: a full-body Snivvian (Ankeefo) on a white
  background, practical build, mid-brown leathery skin, long curly **grey** mane,
  no tusks. Settles the short stocky proportions and the leathery wrinkle texture.
- `wookieepedia_kotorcg_portrait.jpg` — **the reference of record for the tusks and
  the snout.** Painted RPG portrait, three-quarter view: two white lower-jaw tusks
  curving up, the two-nostril flat muzzle at its clearest, deep brow wrinkles.
  Painted, so treat palette as one artist's.
- `wookieepedia_databank_mask_photo.jpg` — **the reference of record for the face.** Photograph of the original practical Snivvian mask (Zutton), from the original Databank, file `Snivvian.jpg` (290×406): wrinkled pinkish-tan leathery skin, flat two-nostril snout, upturned toothy grin, one small tusk, wispy brown hair — https://static.wikia.nocookie.net/starwars/images/0/04/Snivvian.jpg/revision/latest?cb=20051106001730
- `wookieepedia_snaggletooth_cardtrader.jpg` — Zutton, the 1977 practical cantina
  mask. Low resolution and a costume rather than a design document, so weak on
  detail, but it is the species' origin appearance and the source of the
  "Snaggletooth" nickname: grey-brown, **one** small tusk.

## ruling

(empty — owner has not reviewed this race yet)
