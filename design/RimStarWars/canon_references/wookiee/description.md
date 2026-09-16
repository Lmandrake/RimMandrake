# Wookiee

**defName**: `RSW_RimMandrakeWookiee` (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Assigned `Jawa_WildsteamClan: A` — abundant, and the Wildsteam Clan's defining
species (`04_factions.md` faction 6: "a forest people on the wrong planet").

## Sourced text (Wookieepedia)
Infobox: **height 2.23–2.54 meters**; **mass 100 kg (average female) / 150 kg
(average male)**; **lifespan over 400 standard years**; hair colour brown, black,
gray, white; eye colour blue, brown, gray; subspecies **Silverbacks**; origin
Kashyyyk; habitat forest; diet omnivore; languages **Shyriiwook, Thykarann,
Xaczik**. Distinctions: "shaggy water-shedding coat of hair", "long lifespans".
🔴 **Note the infobox gives NO skin colour** — the coat covers it.

Wookiees were a tall species of furry humanoids from Kashyyyk, who **could grow to
a height of nearly three meters**. They were **covered from head to toe in a thick,
shaggy coat of hair with water-shedding properties** that came in shades of brown,
black, gray and white. **Males grew long beards in adult life.** Eye colour ranged
from blue to brown.

**Diet and metabolism.** Wookiees were **big eaters, with the average adult
requiring 3,500–6,000 calories a day**. Diet: wild plants, berries, meat, spices;
**they preferred their spices hot**. During their prime growing years Wookiees were
often hungry, forcing them to eat whenever they could. They did not like eating
**blosphi extract**, but it provided enough nutrition to survive. "**Wookiee flu**"
was a sickness affecting Wookiees which, when caught by other species, was an
overwhelming sickness that disgusted their fellows. The literary collective term
was **a grove of Wookiees**.

**Unusual abilities — three, and all three are mechanically usable.**
- 🔑 **Extendable claws**, used for climbing. 🔴 **Using them for anything else
  violated the Wookiee honour code** — the constraint is as canonical as the claw,
  and it is exactly the sort of thing to build a precept or trait around rather
  than a melee bonus.
- 🔑 **When angered, Wookiees were known to descend into a berserker rage** —
  despite being regarded as intelligent, sophisticated, loyal and trusting.
- 🔑 **They could learn to understand other languages, like Galactic Basic, but
  were physically unable to SPEAK them** due to vocal cords that prevented verbal
  languages. To those who had not learned Shyriiwook they appeared to speak in
  growls and purrs. (A hard constraint on any Wookiee dialogue or voice work.)
- **Longevity**: average lifespan 400 standard years, and **they appeared not to
  age over a span of fifty years**. Lifespans dramatically decreased under the
  harsh working conditions of the spice mines of Kessel. One Wookiee, Lohgarra,
  lived healthily for centuries — **the only distinction being her white fur**
  (so white fur = great age, and the "Silverbacks" subspecies line points the same
  way).
- **Force-sensitive Wookiees were possible** though rare, and some joined the Jedi,
  becoming a source of great pride for their people (Kelnacca, Arkoff, Burryaga
  Agaburry, Tyvokka, Gungi).

## Visual brief
🔑 **`wookieepedia_anatomy_diagram.jpg` is the most useful single image in this
whole library so far, because it shows the body UNDER the fur — which is precisely
what a text-only prompt cannot invent.** It is a sepia anatomical study plate
(skeleton, musculature, detail studies) and it settles several things the prose
never states:

- **The skeleton is human-plan but heavier throughout** — broad deep ribcage, heavy
  pelvis, long arms relative to the torso. **The legs are plantigrade** (a long
  flat sole with five toes), NOT digitigrade. This is worth knowing because
  "furry humanoid" invites a digitigrade guess.
- **The skull carries a projecting muzzle/jaw with large canines** — the face is
  prognathous, not flat. Under the beard there is a real snout.
- **The claw is drawn as a mechanism**: a sequence of detail studies at lower-left
  shows a claw sliding out of a sheath within the finger. This confirms
  "extendable" literally — the claws retract into the digit, they are not
  permanently protruding talons.
- **The hand is long-fingered with five digits.**
- **A comparison silhouette pair at bottom centre shows a human beside a Wookiee**,
  the Wookiee substantially taller and much broader through the shoulders — a
  direct scale reference, consistent with the 2.23–2.54 m infobox range.

From the full-body reference and the animated youngling:
- **The coat is long, shaggy and directional** — it falls, and it falls *downward
  and outward*, longest at the shoulders, upper arms, chest and thighs, shorter on
  the face and the backs of the hands. It is not uniform plush. The water-shedding
  property in the text is visible as this directional fall.
- **Colour is a mid warm brown with darker roots and lighter tips**, with a paler
  muzzle/face mask and a paler chest. The animated youngling (Gungi) is a much
  cooler grey-brown with a distinctly lighter face — so within-species hue
  variation is wide, and the **face is reliably lighter than the body** in both.
- **The face is the exception to the coat**: eyes, nose and mouth sit in a
  short-haired mask, so the face reads as a face rather than a fur ball. Eyes are
  small, dark and set close; the nose is a broad flat dark pad.
- **Bandolier over one shoulder** is the single canonical accessory in the
  full-body reference — worth noting because it is the only thing breaking the fur
  silhouette, and RimWorld's apparel layer will otherwise bury the coat entirely.

**donor_current_sprite.png is partial evidence and is one of the better donor
sprites in this library.** The copied file is
`SWX/Pawn/HeadType/wookiee/wookiee1_south.png`, and there are three variants
(`wookiee1/2/3`) rather than the usual one — so the mod does treat Wookiees as
needing dedicated heads. Verified from the xenotype's gene list, what IS wired:
`RSW_WookieeHead`, `Furskin`, `RSW_BodySizeGene_big`, `Body_Standard` /
`Body_Hulk`, `Outland_Skin_Brown` / `Outland_Skin_PaleBrown`, and hair colours
`Hair_Gray` / `Hair_DarkBrown` / `Hair_DarkBlack` / `RSW_Hair_SlateBlue`. So a
big, brown, fur-skinned pawn with a dedicated Wookiee head lands. 🔴 **But
`Hair_BaldOnly` is also wired** — which for a species whose entire appearance is a
shaggy coat plus (for adult males) a long beard is a direct contradiction with the
canon, and means the beard cannot appear. **Nothing on disk supplies the
directional shaggy coat over the body**, the retractable claws, or the lighter
face mask.

## Source URLs
- https://starwars.fandom.com/wiki/Wookiee (Wookieepedia article; direct page HTML is
  Cloudflare-walled — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Wookiee&format=json&prop=wikitext`,
  101,371 chars, 2026-09-15)
- https://static.wikia.nocookie.net/starwars/images/b/b6/WookieeAnatomyDiagram-TSotW.png (File:WookieeAnatomyDiagram-TSotW.png → wookieepedia_anatomy_diagram.jpg)
- https://static.wikia.nocookie.net/starwars/images/1/1e/Chewbacca-Fathead.png (File:Chewbacca-Fathead.png, the infobox image → wookieepedia_infobox_fullbody.jpg)
- https://static.wikia.nocookie.net/starwars/images/2/2a/Gungi-TCWs5BR1.png (File:Gungi-TCWs5BR1.png → wookieepedia_youngling_animated.jpg)
- NOT fetched this pass: https://www.starwars.com/databank/wookiee (official Databank).

## Candidate images
- `wookieepedia_anatomy_diagram.jpg` — **the highest-value image here.** An
  in-universe anatomical study plate (skeleton, musculature, hand/claw mechanism,
  human-vs-Wookiee scale silhouettes). The only reference in this library that shows
  a species' skeleton, and therefore the only one that settles body plan
  independently of costume: plantigrade legs, prognathous muzzled skull with large
  canines, sheathed retractable claws, human-plan-but-heavier skeleton, and a
  direct height comparison against a human.
- `wookieepedia_infobox_fullbody.jpg` — the infobox image (Chewbacca): a full-body
  adult male on a transparent background at very high resolution. Settles the
  directional shaggy fall of the coat, the mid-warm-brown-with-lighter-face
  palette, the short-haired face mask, and the single-shoulder bandolier.
- `wookieepedia_youngling_animated.jpg` — Gungi, an animated Wookiee youngling.
  Stylized, so treat line as the artist's; its value is showing the within-species
  hue range (much cooler grey-brown) and confirming the lighter-face-than-body rule
  across media and age.

## ruling
(empty — owner has not reviewed this race yet)
