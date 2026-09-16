# Zeltron

**defName**: `RSW_RimMandrakeZeltron` (verified in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml:2210`).
Assigned `Jawa_HuttCartel: S` — some, and only there. Canonically apt: Zeltrons turn up
where pleasure is a trade.

## Sourced text (Wookieepedia)

⚠️ **The canon article is a stub** — it carries `{{Species-stub}}` and is the thinnest
of this batch (7,109 chars of wikitext against 17–28k for the others). Almost everything
substantive below comes from the **Legends** article, and is marked as such.

**Canon article.** Zeltrons were a **humanoid sentient species whose skin varied in
shades of red.** Infobox: class humanoid; **skin colour red, magenta, pink**; **hair
colour black, purple, brown**; origin, height, mass, lifespan, eye colour, habitat and
diet **all empty**. 🔴 **Canon does not even name a homeworld for them** — the `origin`
field is blank.

The canon body text is short enough to give nearly whole: **"Whenever a Zeltron became
angry, their skin turned a deeper red."** **"Allegedly, the Zeltrons gave off pheromones
that made people like them and had a calming effect."** The framing there is careful —
Lorica Demaris *"was unsure of the veracity of that belief,"* though **"she did manage to
calm down an angry Gigoran by petting her."** 🔑 **"At any rate, due to their unique
nature, Zeltrons experienced amplified versions of the feelings of those around them,
especially those they cared about."** That sentence is the one unhedged canon ability.
And on culture: **"On their very first day of grade school, young Zeltrons were taught
that they should not let themselves be led around by their emotions."** In-universe, from
Lorica Demaris: *"I'm Zeltron. We know about feelings."* Canon records Zeltrons as a
journalist, a Jedi Padawan, a Jedi youngling and a Resistance fighter — **not as a
uniformly hedonistic species.**

**Legends article** — the source of every number: **height 1.8 meters**; **skin light
pink to deep crimson**; **hair red, blue, brown, black, white, silver, pink**;
**distinctions "capable of producing powerful pheromones" and "Two Livers"**; **lifespan
up to 80 standard years**; **origin Zeltros**. Body text: **near-Human**, and *"one of
the few near-Human races who had differentiated from the baseline stock enough to be
considered a new species of the Human genus, rather than simply a subspecies."* **"They
all produced potent pheromones, similar to the Falleen species, which enhanced their
attractiveness and likeability."** **"They also possessed limited telepathic abilities,
used to project emotions onto others, as well as allowing them to read and even feel the
emotions of others; some Zeltrons were hired by the Exchange for this ability."**
**"Because of their telepathic ability, positive emotions such as happiness, love and
pleasure became very important to them, while negative ones such as anger, fear, or
depression were shunned."** The **second liver** *"allowed Zeltrons to enjoy a larger
number of alcoholic beverages than other humanoids."* Also: **"It was said that Zeltrons
tended to look familiar to other people, even if they had never met them,"** and **"Most
Zeltrons were in excellent physical shape, and their incredible metabolisms allowed them
to eat even the richest of foods."**

Behaviour, Legends, from Lumiya: *"All Zeltrons are obsessed with romance. When they
cannot love, they fight. Both are sports to them. Coupled with their love of gambling, it
makes one Zeltron in the grip of enthusiasm a formidable enemy. A pack of adolescents is
virtually a force of nature."* ⚠️ That is an antagonist's characterisation inside the
article, not the article's own voice — useful flavour, weak evidence.

**Unusual abilities.** Ranked by how firmly they are sourced: **empathic amplification**
of surrounding emotion (canon, unhedged); **pheromones** producing likeability and a
calming effect (canon *"allegedly"*, Legends flatly); **limited telepathic projection and
reading of emotion** (Legends only); **skin deepens in colour with anger** (canon);
**two livers → alcohol tolerance** (Legends). Nothing here is a Force power.

## Visual brief

🔑 **Zeltrons are a colour problem, not a shape problem.** Every reference shows a
fully human silhouette, human face, human proportions. Unlike the Kaminoan in this same
batch, nothing structural needs changing — **the entire read is skin hue, hair hue, and
the relationship between the two.**

**The canonical range is wider than either single image, and the two images bracket it:**

- `wookieepedia_dani_comic_infobox.jpg` — the canon infobox image, full figure, comic
  linework. Skin is a **bright rose-magenta**, fairly saturated and even, with cooler
  magenta shadow. Hair is a **matching magenta-pink**, worn long.
- `wookieepedia_legends_dani.jpg` — the Legends infobox image, full figure, painted comic
  style. Skin is a **deeper, warmer coral/salmon-red** with distinctly red shadow
  modelling, several steps darker and less pink than the canon image. Hair is **dark
  brown, near-black**.
- `wookieepedia_legends_female.jpg` — a Legends portrait. Skin is **mid coral-red**, and
  it usefully shows the hue **holding up on a rendered face with real modelling** rather
  than flat comic fill; hair is **very dark blue-black**.

So the Legends infobox's **"light pink to deep crimson"** is the honest description, and
the three images sit at rose-magenta, mid-coral and deep coral respectively. ⚠️ **A
single fixed pink is wrong; the species needs a range**, and the canon note that **anger
deepens the red** means the palette has a *direction* built into it.

⚠️ **The canon infobox contradicts its own image on hair.** It lists hair as **black,
purple, brown** — and the image directly beside that list shows **magenta-pink hair**.
Trusting the image, as this library does on appearance: **pink/magenta hair is
canonical**, and Legends independently lists pink, red, blue, silver and white as well.
The dark-haired Legends figures show the other pole. **Hair hue is not tied to skin hue**
— the canon figure matches hair to skin, both Legends figures contrast dark hair against
red skin, and both readings are supported.

**Face and features**, consistent across all three: entirely human — human eyes with
ordinary sclera and iris, human nose, human mouth, human ears, no markings, no crests, no
non-human anatomy of any kind. The Legends portrait shows **dark lips and dark brows**
against the red skin, which is the only "extra" contrast feature any image offers.
**Build**: human, slim, athletic — consistent with Legends' *"most Zeltrons were in
excellent physical shape."* Legends' **1.8 m** is ordinary human height, so **no body-size
change is warranted.**

**`donor_current_sprite.png` is a UI icon, not pawn art, and is weak evidence** — the only
Zeltron-specific texture in the repo is
`RimMandrakeSW/OR/OuterRim/XenotypeIcons/Xenotype_Zeltron.png` (512×512), a menu glyph.
**There is no Zeltron head, body or hair texture in `src/`**, which is correct and
expected: a Zeltron is a human with a different skin and hair colour, so the species
should be built purely from colour genes and needs no new art. Every correction below
lands on a **gene choice**.

**Repo def versus canon — findings.**

1. ⚠️ **The skin gene pair covers only the pale half of the range.** `Skin_PaleRed` +
   `Outland_Skin_PalePink` bracket "light pink" well but there is nothing at the **deep
   crimson / deep coral** end that both Legends prose and two of the three reference
   images show. A Zeltron in game can currently only be pale.
2. **Nothing represents "skin turns a deeper red when angry."** This is the species'
   single canon dynamic feature and the most distinctive thing about it. Recorded as a
   gap, not a defect — it may simply not be expressible.
3. **The hair colour set is good and well sourced.** `Hair_SnowWhite`, `Hair_DarkBlack`,
   `Outland_HairColor_DarkPurple`, `…BrightPurple`, `…BrightMagenta` all appear in one or
   both infobox lists, and `Hair_Grayless` is harmless. **Missing from the def but listed
   in Legends: red, blue, brown, silver.**
4. **The psychic/empathic cluster is the best-founded part of this def.**
   `RSW_statgene_PsyHarmonize`, `PsychicBonding`, `Outland_Empathic` and
   `Outland_CalmingPheromones` map almost one-to-one onto canon's emotional amplification
   and Legends' pheromones and emotion-reading. `Beauty_Beautiful` matches *"most of them
   were considered highly attractive."* `AptitudeStrong_Social` matches the whole
   article. **Do not let a later pass strip these as unsourced — they are the opposite.**
5. ⚠️ **`Turn_Gene_MotivationLow` is unsourced and arguably contradicted.** Nothing in
   either article makes Zeltrons unmotivated; Legends says they are in excellent physical
   shape, and canon shows Zeltron journalists, Jedi and Resistance fighters. It looks
   like an inference from the hedonism stereotype.
6. **`Libido_High` is Legends-only** (*"obsessed with romance"*, and that from a hostile
   speaker). Not contradicted by canon, but not supported by it either — worth knowing
   it rests on the weakest evidence in the entry.
7. **Not represented: two livers / alcohol tolerance** (Legends), and the **80-year
   lifespan**, which happens to match RimWorld baseline anyway.

## Source URLs

- https://starwars.fandom.com/wiki/Zeltron — canon article. HTML is Cloudflare-walled;
  wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Zeltron&format=json&prop=wikitext`
  (7,109 chars, 2026-09-15). ⚠️ Carries `{{Species-stub}}`; no height, mass, lifespan,
  eye colour or homeworld.
- https://starwars.fandom.com/wiki/Zeltron/Legends — Legends article, same API route
  (16,596 chars, 2026-09-15). Source of the 1.8 m height, the 80-year lifespan, the
  light-pink-to-deep-crimson range, the two livers, the pheromone/telepathy detail and
  the homeworld Zeltros.
- https://static.wikia.nocookie.net/starwars/images/2/27/DaniGammill-DuelOfTheReprobates.png
  (File:DaniGammill-DuelOfTheReprobates.png, the canon infobox image →
  `wookieepedia_dani_comic_infobox.jpg`)
- https://static.wikia.nocookie.net/starwars/images/e/eb/Zeltron.jpg
  (File:Zeltron.jpg, the Legends infobox image → `wookieepedia_legends_dani.jpg`)
- https://static.wikia.nocookie.net/starwars/images/4/44/Zeltron_Female.jpg
  (File:Zeltron Female.jpg, captioned "A female Zeltron" in the Legends Biology section →
  `wookieepedia_legends_female.jpg`)
- **No Databank page exists to fetch.** Unlike the other three species in this batch, the
  Zeltron article cites **no `{{Databank|…}}` entry at all** — the species was made canon
  in 2015 only by an author's blog note about an unnamed background youngling, and
  starwars.com has never given it a Databank article. Nothing was omitted here; there is
  nothing to omit.

## Candidate images

- `wookieepedia_dani_comic_infobox.jpg` — **the canon reference of record**, and the only
  canon image the article offers. Full figure, comic linework: bright rose-magenta skin,
  matching magenta-pink hair, entirely human proportions and features. **Its main value
  is that it contradicts its own infobox's hair list** (which omits pink), which is the
  finding this library exists to catch.
- `wookieepedia_legends_dani.jpg` — the Legends infobox plate, same character in the
  original continuity. **The deep end of the skin range**: warm coral-red with red shadow
  modelling, against dark brown hair. Legends design, so a variant — but the range it
  establishes is confirmed by the prose in both articles.
- `wookieepedia_legends_female.jpg` — Legends portrait, painted rather than inked. Kept
  because it is the only reference showing **red Zeltron skin with real light modelling
  on a face**, which is what a sprite has to survive; also shows dark lips and brows as
  the natural contrast features. Small and low-resolution — supporting evidence only.
- `donor_current_sprite.png` — the repo's `Xenotype_Zeltron` UI icon, kept only to record
  that **the sole Zeltron-specific texture in the repo is a menu glyph.** Its absence of
  pawn art is correct for this species rather than a defect.

## ruling

(empty — owner has not reviewed this race yet)
