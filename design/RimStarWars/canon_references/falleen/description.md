# Falleen

**defName**: `RSW_RimMandrakeFalleen` (verified in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`, line 560 —
that file is GENERATED, do not hand-edit). Matrix placement `Jawa_HuttCartel: S` —
some, in the Cartel, which is exactly where canon puts them: the Falleen are the
species that ran **Black Sun**.

## Sourced text (Wookieepedia)

🔴 **The colour-shifting skin — the thing this species is famous for — is a LEGENDS
trait and appears nowhere in the canon article.** The canon page describes fixed
"mottled green" skin and says nothing about pigment change. Everything below is marked
by continuity, and the distinction matters, because the repo def's green-only palette
is *correct for canon* and *badly incomplete for Legends*.

### Canon

Falleen are a **repto-mammalian** sentient species native to the planet **Falleen**.
Infobox: skin colour **green**; hair colour **black** or **brown**; eye colour **blue,
brown, green, orange, purple, yellow**; distinctions **ridged skulls** and a **dorsal
spine**. **Height, mass and lifespan are blank** — recorded as absent, not guessed.

They "had a **distinctive alien appearance**… distinguished by their **mottled green
skin, ridged skulls, and their long, black hair which they typically wore in
ponytails**. Falleen **exuded powerful pheromones which they used to attract mates**."
They were **capable of projecting powerful pheromones**.

They were **a colonial species who had migrated and adapted to dominate many worlds**,
also inhabiting Ord Mantell alongside a human population. During the Clone Wars **a
cabal of Falleen nobles led the Black Sun criminal syndicate** from a well-defended
fortress on Mustafar — Xomit Grunseit led the cabal until **Maul** usurped control and
installed the leg-breaking lieutenant **Ziton Moj** as its ruler.

**The pheromones are shown working, and being resisted.** Asajj Ventress "coerced a
Falleen guard on Mustafar, **leading him to believe his powerful pheromones had worked
on her**," then strong-armed him for information — so the effect is real enough to be
believed in and social enough to be faked. Under the Empire, Falleen (with Umbarans and
Neimoidians) "were typically the butt of running jokes at Imperial Academies." Falleen
turn up as gangsters, crime lords, slaver overseers and bounty-hunter targets.

First appeared in "**Eminence**," *The Clone Wars* S5E14, aired **19 January 2013**.

### Legends (`Falleen/Legends`) — where the colour change lives

**Size: 1.4–1.6 meters** — shorter than a human average. **Lifespan: up to 250 standard
years; up to 400 years in rare cases.** Class **reptilian**, **cold-blooded**. Skin
colour is listed as **gray-green, green, orange, and red**; hair **black**; eyes
**blue**. Distinctions: **small scales, naturally exude pheromones at will.**

🔑 **The colour mechanism, in full.** "Falleen skin was generally **green or gray-green**
in color, though it could become **red to orange** when certain **pheromones were
released**." And, crucially: "**The skin pigmentation of the Falleen changed naturally
to reflect the mood of the individual; however, the Falleen long ago mastered the
ability to change their skin tone at will and used this as something of a covert weapon
in their politics, fostering an appearance of calm, for example, when they were really
panicking.**"

So there are **two things bundled together**, and they are separable:
1. **Involuntary** — pigment tracks mood, green/gray-green at rest, red-to-orange when
   pheromones are released.
2. **Voluntary** — mastered control of skin tone, used deliberately to *deceive*.
   The tell is that a calm-looking Falleen may be lying with their skin.

"The sleek symmetry of their features, calculating and cold demeanors, their exotic
looks, and **their ability to alter their skin pigmentation** meant that the Falleen
were **often considered to be among the most aesthetically pleasing beings in the
galaxy**." They possessed **incredibly quick reflexes** and exuded pheromones "which
made them **all but irresistible to individuals regardless of gender or species**" —
Quinlan Vos fell under a *male* Falleen's pheromones. They had **small scales all over
their bodies**, **slightly clawed fingers and toes**, and **prominent facial and spinal
ridges, though females tended to have slighter, more subtle growths.**

**Semi-aquatic**: able to **hold their breath underwater for a long period**, leading
exobiologists to believe their ancestors were **completely aquatic**. ⚠️ **The
appearance of breasts and other mammalian characteristics in Falleen females AND males**
led exobiologists to infer a **mammal ancestor** — this is why the class is
repto-mammalian, and it bears on the egg-laying question below. They were **one of the
few species resistant to mind tricks**, and had **green blood**.

**Behaviour, and it is unusually well-specified.** Society was **feudal, with noble
houses ruling over the lower classes**; the upper echelons were "**rife with politics
and intrigue, but they rarely spilled blood** over blatant disputes or open warfare."
As a cold-blooded species they **respected discipline and control, particularly
self-control**; they **shunned public displays of emotion**, were **very patient**, and
**looked down on the more openly passionate as lacking self-control**. They had "**a
towering sense of superiority** which they felt was only right and proper due to their
discipline and rigid self-control," and regarded **Falleen, not Coruscant, as the
civilized and cultural capital of the galaxy**. This arrogance made them **isolationist**
— "though they were not a rare species, **it was rare to find them away from their
homeworld**."

Two quotes worth keeping:

> "Those of your world use pheromones to **addle the minds of others**." — Darth Vader
> to Xora

> "**They're not open to suggestion.**" — Aayla Secura *(the mind-trick resistance)*

**Behind the scenes**: "Different artists have depicted Falleen with either **four- or
five-fingered hands**" — so finger count is genuinely unsettled, do not treat either as
canonical.

## Visual brief

🔴 **The colour shift is not a hue drift — it goes all the way to a saturated RED, and
the images prove it.** `wookieepedia_xizor_colorshift_red.jpg` is captioned by the wiki
as "**Xizor altering his skin pigmentation from green to red**," and in it he is **not
greenish-red or flushed — he is fully, uniformly orange-red across the entire head and
face**, the same value and saturation a green Falleen's skin has in its resting state.
This is the single most important image in the directory. A text-only prompt reads
"could become red to orange" and produces a green alien with a blush; the reference
shows **a complete repaint of the same anatomy**. The ridged skull, brow and cheek
structure are unchanged — **only the hue moves.** That is the correct model: one
geometry, two (or a continuum of) skin colours.

**The resting green is mottled and varies between individuals, not a flat fill.**
`wookieepedia_infobox_ziton_moj.jpg` (the canon infobox, a high-fidelity CG render) is
the reference of record for the resting state and shows **mid green with distinctly
darker green mottling patches** concentrated on the forehead, temples and cheeks. The
`wookieepedia_black_sun_nobles.jpg` frame is the best evidence on **range**: five
Falleen in one shot run from **yellow-green through mid green to a distinctly
teal/blue-green** on the central figure. So the hue varies individual to individual
inside "green" — matching the Legends "green or gray-green" — *before* any mood shift
is applied.

**The skull ridges are raised plates, not texture.** In the Ziton Moj render the ridges
read as **a defined pattern of raised, scaled plates** running over the crown, brow and
cheekbones — a hard structural crest, catching its own specular highlight, distinct in
value from the surrounding skin. ⚠️ They are **not** a bumpy skin texture, which is the
easy wrong reading of "ridged skulls." At small scale they should read as a **crest
silhouette on the head**, not as noise.

**The ponytail is real, prominent, and consistent.** Every image with hair shows **long
hair, very dark (blue-black), gathered high and pulled back into a single tail** — Ziton
Moj's falls past the shoulder, the Legends outlaw's is bound high on the crown. The
def's `Hair_LongOnly` + `Hair_DarkBlack` is well aimed. Ziton Moj also carries a **small
dark chin tuft/goatee**, which is worth noting because the def forces
`Beard_NoBeardOnly`.

**Face and build.** The features are **sleek and symmetrical** — a narrow, angular,
almost aristocratic face with a straight nose, thin lips and high cheekbones — matching
"sleek symmetry" and "aesthetically pleasing" rather than a monstrous alien. Eyes read
**dark/yellow** in the Moj render; the canon infobox's six-colour eye list is
individual variation and none of it is contradicted. Build is **lean and upright**
throughout, never bulky. `wookieepedia_legends_outlaw.jpg` and `wookieepedia_uil.jpg`
are both **yellow-green, lean, and ponytailed**, and agree with the CG render on
everything except palette saturation (they are more acid/yellow-green; both are painted
or inked, so treat exact hue as the artist's).

**No visible anatomical dimorphism in these references.** The Legends text says females
had **slighter, more subtle** facial and spinal ridges, which is a real and usable art
split, but no female reference here is clear enough to confirm the degree — record it as
text-only. Note the *voluntary* colour control cuts both ways for art: canon says a
Falleen may deliberately look calm while panicking, so **skin colour is not a reliable
mood readout** in-fiction.

**`donor_current_sprite.png` is genuinely good, and it is the one part of this species
the mod already gets right.** It is
`SWX/Pawn/BodyAttachments/falleen/ridgedspine_male_north.png` — **a vertical column of
five chevron/arrowhead dorsal plates** with dark bases and white highlights, worn down
the back. That is the canon infobox distinction "**dorsal spine**" and the Legends
"**prominent facial and spinal ridges**," rendered correctly and even given per-body
variants (`male`, `female`, `fat`, `thin`, `hulk`). Two limitations: it exists only in
**`_north` and `_east`** — there is **no `_south`**, so the dorsal spine is invisible
when the pawn faces the camera, which is the most common view; and being a back
attachment it does no work on the head. **There is no Falleen-specific head, face or
skull-ridge art on disk at all** — the facial ridges ride the generic
`RSW_FacialRidges_bumpy` / `Outland_RidgedSkin` genes, which per the visual brief above
is the wrong idiom (texture, not plates).

## Repo def versus canon

🔴 **The colour-shifting skin is entirely absent, and it is the point of the species.**
`RSW_RimMandrakeFalleen` carries four skin genes — `Outland_Skin_Sage`,
`Outland_Skin_PaleSage`, `Outland_Skin_DeepViridian`, `Outland_Skin_Viridian` — and
**every one of them is green.** There is **no red or orange skin gene** and **no
mechanism of any kind for pigment change**, voluntary or mood-driven. The Legends
infobox lists **orange** and **red** as Falleen skin colours outright, the article
describes the shift as a **covert political weapon**, and the wiki's own caption on the
Xizor image is about nothing else. Whatever the eventual implementation (a hediff, a
mood-linked graphic, a second skin gene, or simply admitting red into the palette),
**the current def cannot represent the trait at all.** This is the finding to act on.

🔴 **No mind-trick resistance.** Legends: "**They were one of the few species resistant
to mind tricks**," reinforced by Aayla Secura's "They're not open to suggestion." Same
class of trait as the Hutt's mind-trick immunity recorded in `hutt/description.md`, and
it matters for the same reason — it is a Force-resistance, so it lands if Force powers
ever do. Nothing in the def touches it.

⚠️ **`Outland_EggLayer` sits against the species' explicitly mammalian half.** Falleen
are **repto-mammalian**, and the Legends article's stated reason is that **breasts and
other mammalian characteristics appear in both females and males**, implying a mammal
ancestor. Egg-laying is not flatly contradicted — they are half reptile, and no canon
text describes Falleen reproduction either way — but it is an invented choice on a
species whose sourced biology leans the other way. Flagged rather than called an error.

⚠️ **`RSW_lifespan_double` undershoots by a lot.** Legends gives **up to 250 standard
years, up to 400 in rare cases**. Doubling a human lifespan lands near 160. Directionally
right, numerically short of the only sourced figure.

⚠️ **No body-size gene, and Falleen are short.** Legends: **1.4–1.6 m**, below human
average. The def carries `Body_Standard` and no size gene.

⚠️ **`MeleeDamage_Strong` is the wrong stat for the sourced trait.** Canon gives Falleen
**"incredibly quick reflexes"** twice and never gives them strength. Reflexes would map
to melee *dodge*, aim speed or work speed, not damage.

⚠️ **`Beard_NoBeardOnly` versus the reference image.** Ziton Moj — the canon infobox
individual — has a visible dark chin tuft. Minor, but the def forbids what the primary
reference shows.

**Well matched, recorded so a later pass does not undo them.** This def is one of the
better-aimed ones in the file on everything except colour:
`Outland_CalmingPheromones` + `Outland_FamiliarScent` (canon: exude powerful pheromones
at will — "calming" is a partial reading of a trait canon frames as *attraction* and
*mind-addling*, but it is the right mechanism in the right place);
`Outland_WebbedFeet` (Legends: semi-aquatic, hold breath a long time, probably aquatic
ancestors — this is a real hit); `Outland_Blood_Green` (Legends: "had green blood",
exactly right); `Hair_LongOnly` + `Hair_DarkBlack` (long black hair in ponytails);
`RSW_BodyAttachment_falleen` + `Outland_RidgedSkin` + `RSW_FacialRidges_bumpy` (dorsal
spine and facial/skull ridges — the mechanism is right, see the visual brief for the
idiom); `RSW_butchergene_lizardskin` (reptilian, small scales all over the body);
`MinTemp_SmallIncrease` + `MaxTemp_LargeIncrease` (cold-blooded);
`Turn_Gene_TraitGrandeur`, `Turn_Gene_Certain`, `Turn_Gene_HighBeautyStandard` and
`AptitudeStrong_Social` — collectively an excellent read of "towering sense of
superiority," "rigid self-control," "among the most aesthetically pleasing beings in
the galaxy," and a species that ran a criminal syndicate through politics rather than
open warfare.

## Source URLs

- https://starwars.fandom.com/wiki/Falleen — canon article. Direct page HTML is
  Cloudflare-walled; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Falleen&format=json&prop=wikitext`
  (11,415 chars, 2026-09-15). ⚠️ Carries an `{{Expand|all sections}}` banner — flagged
  incomplete by the wiki's own editors, and it contains **no mention of pigment change**.
- https://starwars.fandom.com/wiki/Falleen/Legends — the Legends article, and the sole
  source for the colour shift, the size, the lifespan, the mind-trick resistance, the
  semi-aquatic biology, the scales and claws, and the feudal society. Pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Falleen/Legends&format=json&prop=wikitext`
  (20,036 chars, 2026-09-15). Carries a `{{Citation}}` maintenance banner, and its
  biology paragraphs are cited largely to *Ultimate Alien Anthology* and *Scum and
  Villainy*.
- https://static.wikia.nocookie.net/starwars/images/1/18/ZitonMoj-BHUSC.png —
  File:ZitonMoj-BHUSC.png, the **canon infobox image** → `wookieepedia_infobox_ziton_moj.jpg`
- https://static.wikia.nocookie.net/starwars/images/e/e1/XizorHoldsHisBreathUntilMomGetsHimAToy-SOTETC.jpg —
  File:XizorHoldsHisBreathUntilMomGetsHimAToy-SOTETC.jpg, captioned by the wiki "Xizor
  altering his skin pigmentation from green to red" → `wookieepedia_xizor_colorshift_red.jpg`
- https://static.wikia.nocookie.net/starwars/images/0/07/BlackSunLeaders-Eminence.png —
  File:BlackSunLeaders-Eminence.png, the Falleen nobles of Black Sun →
  `wookieepedia_black_sun_nobles.jpg`
- https://static.wikia.nocookie.net/starwars/images/f/fc/Falleen_Outlaw.jpg —
  File:Falleen_Outlaw.jpg, the **Legends infobox image** → `wookieepedia_legends_outlaw.jpg`
- https://static.wikia.nocookie.net/starwars/images/7/71/Uil-HanSolo2.png —
  File:Uil-HanSolo2.png, the Falleen U'il → `wookieepedia_uil.jpg`
- https://www.starwars.com/databank/falleen — **cited by the canon article as `{{Databank|falleen}}`
  and is the source of the "mottled green skin, ridged skulls, long black hair in
  ponytails" sentence, but was NOT fetched directly this pass.** The sentence above is
  quoted from the Wookieepedia wikitext, which attributes it to that Databank page.
- **Unsourced in canon, recorded as absent rather than guessed**: height, mass,
  lifespan, habitat, diet, language. *(Legends supplies height 1.4–1.6 m and lifespan
  250/400 years — marked as Legends throughout, never presented as canon.)* **Finger
  count is explicitly unsettled** — the wiki records four- and five-fingered depictions
  by different artists.

## Candidate images

- `wookieepedia_xizor_colorshift_red.jpg` — 🔑 **the reference this entry exists for.**
  A painted piece the wiki captions as Xizor **altering his skin pigmentation from green
  to red**, showing the shifted state as a **fully saturated orange-red across the whole
  head**, with the ridged-skull anatomy unchanged. Settles that the shift is a complete
  repaint, not a flush. Painted, so treat brush and lighting as the artist's — but the
  *magnitude* of the colour change is the point and is unambiguous.
- `wookieepedia_infobox_ziton_moj.jpg` — **the reference of record for the resting
  state.** The canon infobox: a high-fidelity full-body CG render of Ziton Moj. Settles
  the mottled mid-green skin, the raised scaled plate structure of the skull ridges, the
  long dark ponytail, the chin tuft, the sleek angular face and the lean upright build.
- `wookieepedia_black_sun_nobles.jpg` — an in-show frame of five Falleen nobles seated
  together. Its value is **range**: hue runs yellow-green → mid green → teal within one
  shot, establishing that individual variation exists inside "green" independently of
  the mood shift. Dim cinematic lighting, so not a palette authority.
- `wookieepedia_legends_outlaw.jpg` — the **Legends infobox image**: a lean yellow-green
  Falleen with a high-bound dark ponytail. Painted and small; confirms silhouette,
  ponytail and lean build, agrees with the CG render on everything but saturation.
- `wookieepedia_uil.jpg` — the canon Falleen U'il, from a *Han Solo* comic. Inked, so
  stylized; kept as a third independent confirmation of green skin plus dark ponytail.
- `donor_current_sprite.png` — the repo's own art,
  `SWX/Pawn/BodyAttachments/falleen/ridgedspine_male_north.png`: five chevron dorsal
  plates down the back. **The strongest donor asset in this batch** — a correct rendering
  of the canon "dorsal spine" distinction, with per-body variants. Limitations: **no
  `_south` variant**, and no Falleen head or facial-ridge art exists on disk.

## ruling

(empty — owner has not reviewed this race yet)
