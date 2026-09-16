# Chagrian

**defName**: `RSW_RimMandrakeChagrian` (verified in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`, line 296 —
that file is GENERATED, do not hand-edit). Matrix placement `Jawa_DeepwaterCompact: S`
— **some**, in the water faction, which is exactly right for an amphibian.

## Sourced text (Wookieepedia)

Chagrians are an **amphibian** sentient species, native to **Champala**, habitat
**ocean**. Infobox skin color is **blue only**; eye color **blue only**; the sole
listed distinction is **primary horns**. No height, mass or lifespan in the infobox
— but the article body gives height (below). Class `Amphibian` is cited to *Tarkin*.

**Life cycle.** Chagrians begin life in an **immature tadpole stage**, born in
**clutches of two or three**, each tadpole about **thirty centimeters long** and
initially entirely aquatic. They can only breathe air after developing **lungs** as
they mature, at which point they develop two arms and two legs; once the limbs are
fully developed they leave the water and the rest of their intermediate physiology
fades away. Juvenile tadpoles are cared for by their parents, who keep them in **a
sealed tub inside the home**.

**Adult body.** Bipedal humanoids, **two meters tall on average** — tall, and worth
holding onto, because the def gives them no body-size gene at all. They remain as
comfortable submerged as out of water, breathe fully underwater, and can spend
**weeks, months or even years entirely submerged**. Their bodies are **muscular and
powerful**, making them adept swimmers and suited to **heavy labor**. Hands have
**five fingers**.

**Senses — a real behavioural quirk.** Constant exposure to Champala's saltwater
means a Chagrian **can rarely taste anything but salt** and has an **extremely weak
sense of taste**. Their **tongues serve smell rather than taste**, reptile-fashion:
a Chagrian **briefly flicks the tongue in and out of the mouth** to assess new food
and drink, the tongue stirring the air to pick up particles and vibrations. As a
consequence most Chagrians treat meals as an inconvenience and **carry nutritional
supplements or food capsules**; celebratory banquets are unheard of in their society
except at offworlder resorts. They also **secrete green sweat when subjected to
heat**.

**Radiation resistance.** Chagrian skin ranges **light blue → cerulean → indigo** as
a direct result of the species evolving under an **unstable sun**; the skin developed
**an innate resistance to harmful radiation**, which became a **dominant trait of the
species**. This is the one hard mechanical trait canon gives them.

**Horns, and the dimorphism.** All Chagrians possess a pair of elegant horns called
**lethorns**, which **grow down on either side of the head, protruding down over the
torso from a pair of fleshy head tentacles**. **Male Chagrians also possess a second
set of horns which protrude straight up from the top of the head.** The horns are
**darker purple or brown at the base, with the upper and mid portions white or
yellow**. The head has two **eyes well developed to see in dim sub-aquatic light**
and a nose above the mouth. Males originally used their lethorns in **mating rituals
and as weapons in formal duels** (outlawed by the Galactic Civil War); males still
treat their horns as a status symbol, **devoting a large part of the daily routine to
caring for them** and showing "uncharacteristic vanity in filing and decorating" them.

**Behaviour.** Serene, balanced and stoic; **obedient and accommodating people, even
to a fault** (a consequence of a tourism economy). Chagrian culture **values justice,
legal and social, above all other things**, making them sticklers for rules and
unwilling to deviate from a legal or bureaucratic system. Law enforcement is taken
very seriously and investigations are meticulous. Most speak **Chagri**, with few
learning Galactic Basic. Seeing poverty, prejudice, homelessness, disease or
starvation moves a Chagrian greatly, and they will try to remedy it directly or
through charity or law.

## Visual brief

**Look at `wookieepedia_male_closeup.jpg` before anything else — it is the reference
of record, and it settles three things the prose gets you only halfway to.**

🔴 **There are TWO separate horn structures and they are different colours. Conflating
them is the failure mode.**

1. **The upward primary horns** (male only): a pair of tall, slender, smooth horns
   rising from the top of the skull and curving gently back. In the close-up they are
   **dark purple/mauve**, tapering to fine points, and are **the tallest thing in the
   silhouette** — Mas Amedda's read almost like antennae at full-body distance.
2. **The lethorns**: **massive fleshy lobes**, hanging over the ear position down
   each side of the head. 🔑 **The lobes are SKIN, not horn** — the same blue-grey/
   lavender as the face and carrying the same mottling. Each lobe then terminates in
   **a long, thin, downward-tapering horn/tusk** that hangs onto the chest, and *that*
   tip is the part which is **purple at its base and shades to pale yellow/cream at
   the point.** So the infobox's "darker purple or brown at the base, upper and mid
   portions white or yellow" is describing **the pendant tip only**, not the whole
   structure. A text-only prompt reads that sentence and paints the entire side
   structure as a cream horn — which is wrong, and loses the fleshy-lobe silhouette
   that actually identifies the species.

**Skin is not a flat blue.** The close-up shows **pale blue-grey to lavender, heavily
mottled with pale cream-yellow patches**, particularly across the lobes and the crown.
The female image (`wookieepedia_female.jpg`) is a more saturated **purple/lavender**
with less mottling. So "blue" in the infobox is the low end of a blue→lavender→indigo
range, and **mottling is a real feature, not artist noise** — it appears in both the
practical-effects close-up and the full-body infobox shot.

⚠️ **The images disagree with the infobox on eye colour.** The infobox cites **blue
only** (*The Phantom Menace*). The close-up plainly shows **orange/amber irises** in
deep-set sockets under a heavy brow. Trusting images on appearance: **orange is
attested**, and the repo's `Outland_Eye_Orange` gene is therefore defensible rather
than an error. The female image reads dark/neutral. Record both.

**The dimorphism is larger than "males get extra horns."** In the female image the
lethorn lobes are **shorter and blunter**, curving forward to end in **rounded fleshy
tips near the chin** with no long pendant tusk visible at all; the male's lobes are
bigger and carry the long tapering tips down onto the chest. She also has a
**noticeably more human face** — visible lips (pink), a normal nose, ordinary human
eyes — where the male close-up is a heavy-browed, thin-lipped, deeply-lined alien
face. Some of that is 1990s practical-makeup versus a painted book plate, so treat
the *degree* as uncertain; the **lobe length/tip difference** is the part both images
support.

**Head shape**: hairless, elongated backward and upward into a smooth cranial dome
that the upward horns spring from; **no hair anywhere**, consistent with the def's
`Hair_BaldOnly`.

`wookieepedia_wave_skimmer.jpg` is a small painted illustration and is useful for
exactly one thing: it confirms the **silhouette still reads at tiny scale** — two
uprights plus two forward-hanging pendants — which is the relevant test for a
RimWorld head sprite.

**`donor_current_sprite.png` is good, and unusually so — but there is one specific
thing it gets backwards.** It is
`OR/OuterRim/Genes/Headbone/Chagrian1_south.png`, a greyscale render-node mask (so
absence of colour is correct and expected — the hue findings above belong on the skin
and eye *genes*, not on this file). The shape work is right: **two upward horns, two
fleshy side lobes, two long downward tapering tips**, and the female variant
(`ChagrianF_south.png`) correctly **drops the upward pair while keeping lobes and
tips**, which is the canonical dimorphism. ⚠️ What is inverted is **where the value
gradient sits**: the sprite ramps the **fleshy lobe** from dark at the top to near-
white at the bottom, and paints the **pendant tip a flat mid-grey**. Canon is the
reverse emphasis — the **lobe is uniform skin colour** (it is skin) and the **tip** is
the element that ramps, purple → yellow. Whoever corrects this should move the ramp
onto the tip and flatten the lobe to skin value.

## Must show
- [ ] Two separate horn structures: upright primary horns (male only) rising from the top
  of the skull, AND fleshy lateral head lobes (lethorns) hanging down each side that
  terminate in a long tapering pendant tip
- [ ] The lethorn lobes themselves are skin-coloured flesh, not horn material — only the
  pendant tip is purple-to-yellow
- [ ] Skin reads pale blue-grey to lavender/purple, heavily mottled with pale cream-yellow
  patches — not a flat blue
- [ ] Hairless, elongated cranial dome
- [ ] Female lethorn lobes are shorter and blunter, curving forward to rounded tips near
  the chin, with no long pendant tusk

## Engine limits
none known

## Repo def versus canon

🔴 **The xenotype carries orange skin, and canon Chagrian skin has no orange in it.**
`RSW_RimMandrakeChagrian` lists `Outland_Skin_DeepOrange` and `Skin_Orange` alongside
`Skin_Blue` and `Outland_Skin_DeepAzure`. Canon is **light blue → cerulean → indigo,
and the blue is causally load-bearing** — it is the visible result of evolved
radiation resistance under an unstable sun. An orange Chagrian is not a colour variant,
it contradicts the species' stated biology. Two of the four skin genes should go.
(Reported, not fixed — the file is generated.)

⚠️ **No radiation resistance gene.** The one hard mechanical trait canon gives the
species — **innate resistance to harmful radiation, a dominant trait** — is absent.
The def instead carries `ToxResist_Partial` and `FireWeakness`; toxin is a plausible
stand-in, but the fire weakness is unsourced either way.

⚠️ **Nothing represents the aquatic body plan or the 2-meter height.** Canon Chagrians
breathe fully underwater, can stay submerged for years, are muscular and suited to
heavy labor, and stand **two meters**. The def has no body-size gene, no swimming or
aquatic gene, and `AptitudePoor_Plants`/`AptitudePoor_Animals` with
`AptitudeStrong_Medicine`/`AptitudeStrong_Social` — a diplomat build, not a strong
swimmer-labourer. The Social aptitude is well supported by the justice/bureaucracy
material; the physical side is simply unrepresented.

**Defensible on inspection**, recorded so a later pass does not "fix" them:
`Outland_EggLayer` + `Outland_DeceleratedPregnancy` (canon: clutches of two or three
aquatic tadpoles), `Hair_BaldOnly` / `Beard_NoBeardOnly` (hairless in every image),
`Outland_Blood_Green` (canon attests **green sweat**, not green blood — close, and not
contradicted), `Outland_FamiliarScent` and `Outland_Eye_Orange` (see visual brief).

## Source URLs

- https://starwars.fandom.com/wiki/Chagrian — Wookieepedia article. Direct page HTML is
  Cloudflare-walled; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Chagrian&format=json&prop=wikitext`
  (26,516 chars, 2026-09-15). ⚠️ The article carries an `{{Expand|all sections}}`
  banner, so it is flagged incomplete by the wiki's own editors. Nearly all of the
  biology and society detail above is cited to a single source, ***Lead by Example***
  (`LBE`).
- https://static.wikia.nocookie.net/starwars/images/a/a5/MasAmeddaEpIFull-SWBC66.png —
  File:MasAmeddaEpIFull-SWBC66.png, the infobox image → `wookieepedia_infobox_mas_amedda.jpg`
- https://static.wikia.nocookie.net/starwars/images/c/c3/Mas_Amedda_SWE.png —
  File:Mas_Amedda_SWE.png → `wookieepedia_male_closeup.jpg`
- https://static.wikia.nocookie.net/starwars/images/f/fc/Chagrian_female_LBE.png —
  File:Chagrian_female_LBE.png → `wookieepedia_female.jpg`
- https://static.wikia.nocookie.net/starwars/images/9/98/Chagrian_Wave-Skimmer_LBE.png —
  File:Chagrian_Wave-Skimmer_LBE.png → `wookieepedia_wave_skimmer.jpg`
- Not fetched this pass: `https://www.starwars.com/databank/` has no Chagrian species
  page cited by the article; the infobox's own citations are to *Star Wars: Alien
  Archive*, *Tarkin*, *Lead by Example* and *Episode I*, all print.
- **Unsourced, recorded as absent rather than guessed**: mass, lifespan, diet.
  Height (2 m) comes from the article body, not the infobox.

## Candidate images

- `wookieepedia_male_closeup.jpg` — **the reference of record.** A high-resolution
  bust of Mas Amedda from a practical-effects still: settles the two-structure horn
  anatomy, the purple upward horns, the fleshy skin-coloured lethorn lobes with
  purple→yellow pendant tips, the mottled blue-lavender skin, and the orange irises.
- `wookieepedia_infobox_mas_amedda.jpg` — the Wookieepedia infobox image: the same
  individual full-length in robes. Its value is **the silhouette at distance** and
  showing how the horns read against a costumed body; at this size the lethorn lobes
  wash out to a pale mass, which is a caution about small-scale rendering, not a
  colour fact.
- `wookieepedia_female.jpg` — a female Chagrian in an orange pilot flightsuit
  (File:Chagrian_female_LBE.png). Confirms **no upward horns**, shorter blunter
  lethorn lobes, and a more saturated purple skin. A painted/printed book plate, so
  treat line and exact palette as the artist's.
- `wookieepedia_wave_skimmer.jpg` — a small painted scene of a Chagrian on a
  wave-skimmer. Stylized and low-resolution; kept only as **evidence the silhouette
  survives at sprite scale**.
- `donor_current_sprite.png` — the repo's own art,
  `OR/OuterRim/Genes/Headbone/Chagrian1_south.png` (male variant). Greyscale render-node
  mask. See the visual brief: shape correct, value gradient on the wrong element.

## ruling

(empty — owner has not reviewed this race yet)
