# Ewok

**defName**: `RSW_RimMandrakeEwok` (verified in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`, line 516 —
that file is GENERATED, do not hand-edit). Matrix placement `Jawa_WildsteamClan: S` —
some, in the Wildsteam Clan.

## Sourced text (Wookieepedia)

🔑 **This is the only species in this batch with BOTH height and mass sourced.**
Infobox: **height 1 meter**; **mass 30 kilograms (66 lbs)**; skin colour **brown**; hair
colour **black**; eye colour **black**. Origin is the **forest moon of Endor**. Lifespan
and diet are blank in the infobox — but the article body states they are **omnivorous**.

**Body plan.** "Ewoks were sentient humanoids, averaging about **one meter** in height.
**Omnivorous**, they were **covered in fur from head to toe**, with **brown and black as
the most common colors**. **Most Ewoks had solid-colored fur, though a few sported
stripes.** Ewoks had **large, bright eyes**, **small humanoid noses**, and **hands that
possessed two fingers and an opposable thumb**" — i.e. **three digits per hand**, not
five.

**Strength and senses — the two hard mechanical traits.** "**Despite their small size,
Ewoks were physically strong enough to overpower combat-trained humans.**" And:
"Additionally, they are also able to **see in the dark** and can use their **keen senses
to locate enemies that are not immediately visible.**"

**Behaviour.** Canon frames them as genuinely dangerous, not cuddly, and the article
opens the biology section with a joke that makes the point:

> "The Ewoks are **fierce warriors. The top of the food chain on a savage planet!**" /
> "Okay, first of all, they live on a **moon**, not a planet. Second of all—" — two Whills

They are **tribal and village-dwelling**: the Empire razed an Ewok village to erect the
Death Star's **shield generator** complex, forcing survivors to a neighbouring village,
**Bright Tree Village**, led by **Chief Chirpa**. Governance includes a **Chief**, a
**shaman** (**Logray**), and a **Council of Elders**. ⚠️ **They practise ritual sacrifice
of outsiders**: on identifying C-3PO as **the Golden One** — a figure they believed had
brought balance to Endor millennia before — Logray **attempted to sacrifice Leia and the
others as a feast in C-3PO's honour**, and was only stopped when Luke used the Force to
levitate the droid. They then **accepted the Rebels into their tribe**.

**Combat record, which is the reason to take them seriously.** **Multiple Ewok tribes**
joined the ground battle against the shield generator, and "their **primitive weapons
felled the stormtroopers and the scout walkers** of the Empire, although they took many
losses to Imperial blaster fire." Their assistance paved the way for the destruction of
the second Death Star. "**Legend claimed it was the first time the Ewoks had returned to
combat in generations**" — so their martial capability is treated in-universe as
exceptional and dormant, not routine.

**After Endor**: an **Ewok Civil War** broke out, requiring a New Republic diplomatic
mission. By two years after the battle **many Ewoks had become caf farmers**, and at
least one, **Peekpa**, worked for the New Republic as a **slicer** — so they are not
locked at a stone-age tech level in canon.

## Visual brief

**The body plan is the easy part and all four references agree on it.** Look at
`wookieepedia_infobox_three_ewoks.jpg` (three Ewoks in practical costume, the article's
infobox image): a **short, rounded, pot-bellied torso with no visible neck**, **short
stubby arms hanging to about hip level**, **short legs**, and **plantigrade bare feet
with visible pale toes**. The head is **large relative to the body** and sits directly on
the shoulders. Fur covers everything except the muzzle, palms and soles. The overall read
is **teddy bear**, which is what the def's `Outland_Ears_Teddy` is reaching for and is
correct.

🔴 **The fur colour range is wider than "brown and black," and the def's palette misses
the most prominent member of it.** The three infobox figures are:
1. **Warm mid-brown / tan**, with a paler face and a dark muzzle.
2. **Solid deep black**, with a contrasting **pale grey-tan muzzle**.
3. **Grizzled grey-and-white** — silver-tipped fur over a darker base, with an almost
   **white face**.

So: brown ✓ and black ✓ as canon says, plus a **grizzled grey/white morph** the prose
does not mention at all. **The black one is the centre figure of the species' own infobox
image**, and there is no black fur gene in the def (see below).

🔑 **The muzzle is a distinct pale patch, and it is the main facial landmark.** On every
reference, the area around the nose and mouth is a **markedly lighter, shorter-furred
patch** than the surrounding coat — pale grey-tan on the black Ewok, near-white on the
grizzled one. The muzzle itself is **very short and blunt**, not canine; the nose is a
**small dark button**. **Small teeth are just visible** at the mouth on two of the three.
An Ewok head sprite without that pale muzzle patch will not read as an Ewok.

⚠️ **The eyes are the one place prose and images genuinely fight, and the resolution is
interesting.** The article says "**large, bright eyes**," and the def carries
`RSW_Eyes_Big`. But the three **adults** in the infobox image have **small, round, dark,
beady eyes** — visually a minor feature. `wookieepedia_woklings_juveniles.jpg` (juvenile
Ewoks, "woklings") shows the opposite: **enormous, glossy, domed black eyes dominating
the face.** Two things are going on and both are usable:
- **Juveniles genuinely have proportionally huge eyes** — the same adult/juvenile
  proportion split recorded for the Hutt and Huttlet in `hutt/description.md`. A young
  Ewok is not a small adult.
- **Several individuals carry pale fur rings around the eyes** — a spectacle-like marking
  which makes the eyes *read* far larger than they are. This is visible on the adult in
  the woklings frame and is the likeliest origin of "large, bright eyes."

So: **on an adult, draw small dark eyes but consider the pale eye-ring** that sells them
as large; on a juvenile, draw them genuinely huge. Do not simply scale one from the other.

**Hoods are so consistent they are part of the silhouette.** All three infobox figures
and Wicket in `wookieepedia_wicket_with_leia.jpg` wear a **fabric hood or cowl** — brown,
teal-blue, dark — often with a fastening at the throat and sometimes a small bone or
bead ornament. It is **costume, not anatomy**, and should not become a gene; but a
hoodless Ewok will look wrong to anyone who knows the species, and it is worth recording
that canon Ewok material culture is **hood, sling/pouch, and a hand weapon**.

**Hands.** Canon specifies **two fingers and an opposable thumb**. The woklings frame is
the only reference where hands are clearly visible, and they are **small, pale pinkish-tan
and short-digited** — consistent with a low digit count, though not clear enough to count
in the image. Treat the three-digit hand as **text-sourced, image-neutral**.

`wookieepedia_endor_celebration.jpg` and `wookieepedia_wicket_with_leia.jpg` are both
low-resolution film frames in dim forest light. They are kept for **scale and context**,
not appearance: the celebration frame shows many Ewoks together against human-sized
figures, which is the best available check on the **1-meter height**, and the Wicket
frame shows one **in its forest habitat** with a human for comparison. Do not read
palette off either.

**`donor_current_sprite.png` is correct as far as it goes, and it does not go far.** It
is `SWX/Pawn/HeadAttachments/ewok/RoundEars_south.png` — a greyscale render-node mask of
**a pair of round ears set high and wide on the skull**, which is the right shape and the
right placement for the teddy-bear head, and it exists in `_south`/`_east`/`_north` so
coverage is complete. That plus the ears is the **entire** inventory of Ewok-specific art
in the repo: **no muzzle patch, no fur body, no juvenile variant.** The species is
otherwise assembled from generic genes (`Furskin`, `RSW_Eyes_Big`,
`Outland_Nose_Leathery`, `RSW_BodySizeGene_smaller`), so the two things that most identify
an Ewok's face — **the pale short-furred muzzle** and the **pale eye-rings** — are
unrepresented.

## Must show
- [ ] Short, rounded, pot-bellied torso with no visible neck; short stubby arms/legs; bare plantigrade feet with visible toes
- [ ] A distinct pale, short-furred muzzle patch around the nose and mouth — the main facial landmark
- [ ] Small dark button nose
- [ ] Adult eyes are small, round and dark (not oversized); juveniles instead have proportionally huge, glossy, domed eyes
- [ ] Round ears set high and wide on the skull (teddy-bear silhouette)
- [ ] Fur colour can be solid deep black (with a paler muzzle), not only brown — the black individual is the centre figure of the species' own reference image

## Engine limits
none known — the current gap is missing art (only a round-ears mask exists in the repo,
with no muzzle patch, eye-ring, or fur body), not a rendering constraint.

## Repo def versus canon

🔴 **There is no black fur gene, and black is one of the two colours canon names as most
common.** The def's hair palette is `Hair_SnowWhite`, `Hair_Blonde`, `Hair_SandyBlonde`,
`Hair_LightOrange`, `Hair_ReddishBrown`, `Hair_DarkBrown`, `Hair_DarkReddish`,
`RSW_Hair_SlateBlue`, `RSW_Hair_SlateRed`. The darkest available is `Hair_DarkBrown`.
Canon: "**brown and black as the most common colors**," the infobox cites hair colour
**black**, and **the black Ewok is the centre figure of the infobox image.** A player will
never roll the most iconic variant.

🔴 **`RSW_Hair_SlateBlue` and `RSW_Hair_SlateRed` are attested nowhere.** No blue or red
Ewok appears in the article or in any of the four references. The palette has room for two
invented colours while missing the canonical one.

⚠️ **No stripe option.** Canon: "Most Ewoks had solid-colored fur, **though a few sported
stripes**." A rare striped variant is explicitly canonical and cheap to represent, and
there is nothing for it. Note this is the same class of miss as the anooba striping that
this library was built on — except here the prose *does* say stripes and the def ignores it.

⚠️ **`Body_Hulk` on a 30 kg, 1-meter species.** The def carries `RSW_BodySizeGene_smaller`
(good, and well matched to the sourced 1 m / 30 kg) but also lists **both**
`Body_Standard` **and** `Body_Hulk`. Canon does say Ewoks are "physically strong enough to
overpower combat-trained humans," so the *strength* is sourced — but a hulk body shape is
a different claim from strength-at-small-size, and no reference shows a bulky Ewok. If the
intent was to carry the strength, `Robust` (also present) already does it.

⚠️ **Nothing represents the three-digit hand.** "Two fingers and an opposable thumb" is a
specific, cited anatomical fact and there is no gene or art for it.

⚠️ **`Turn_Gene_LowBeautyStandard`, `Libido_High`, `Fertile`,
`Outland_AcceleratedPregnancy` and `Outland_AcceleratedMaturation` are all unsourced.**
Nothing in the article addresses Ewok beauty standards, libido, fertility, gestation or
maturation rate. Recorded as invented rather than wrong — but note the def's own
`<description>` claim that Ewoks are "**highly aggressive and capable predators**"
oversells canon slightly too: canon says **omnivorous**, **fierce warriors**, and that
returning to combat was so rare it was **legendary**. The def has no diet gene, which is
correct for an omnivore.

⚠️ **The `Turn_Gene_GauranlenNeed` / `Turn_Gene_PruningAccelerated` pair is an invention,
and a defensible one.** Nothing in canon bonds Ewoks to a tree in the Gauranlen sense. But
they live on a **forest moon**, in **Bright Tree Village**, in an arboreal village culture,
and the mapping is thematically apt. Flagged so a later pass knows it is authored rather
than sourced, **not** as an error to remove.

⚠️ **Nothing represents the tribal social structure** — Chief, shaman, Council of Elders,
inter-tribal war — which is the richest sourced material about the species and is the kind
of thing an ideoligion rather than a gene would carry. Noted for scope, not as a def bug.

**Well matched, recorded so a later pass does not undo them**: `RSW_BodySizeGene_smaller`
(1 m / 30 kg — the best-sourced size in this batch), `Furskin` (covered in fur head to
toe), `DarkVision` (canon: **able to see in the dark**, and keen senses to locate enemies
not immediately visible — a precise hit), `Outland_Ears_Teddy` (correct, and matched by the
repo's `RoundEars` art), `RSW_Eyes_Big` (canon prose says large bright eyes — see the
visual brief for the adult/juvenile nuance), `Robust` and `Aggression_Aggressive` (canon:
overpower combat-trained humans, fierce warriors, felled stormtroopers and scout walkers),
`RSW_statgene_predator` (defensible via the ritual-feast episode and "top of the food
chain," though canon's stated diet is omnivorous), `NakedSpeed` (they wear no real
clothing beyond hoods and slings), `RSW_GS_Primitive` (primitive weapons, tribal
villages), `Outland_Nose_Leathery` (small dark button nose), and `Outland_UnusualSpeech`
(they speak Ewokese, not Basic).

## Source URLs

- https://starwars.fandom.com/wiki/Ewok — Wookieepedia article. Direct page HTML is
  Cloudflare-walled; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Ewok&format=json&prop=wikitext`
  (45,397 chars, 2026-09-15) — the longest of the five in this batch. ⚠️ Carries a
  `{{MultipleIssues|expand|image}}` banner, so the wiki's own editors flag it as needing
  expansion and better images. Biology is cited to *Return of the Jedi* and the official
  **Databank**; height to the Databank, mass to *Star Wars Life Size*; the dark-vision
  line to *Battlefront II*.
- https://static.wikia.nocookie.net/starwars/images/a/a8/Ewoks_Encyclopedia.png —
  File:Ewoks_Encyclopedia.png, the **infobox image** → `wookieepedia_infobox_three_ewoks.jpg`
- https://static.wikia.nocookie.net/starwars/images/f/fc/Woklings_btm.jpg —
  File:Woklings_btm.jpg, juvenile Ewoks → `wookieepedia_woklings_juveniles.jpg`
- https://static.wikia.nocookie.net/starwars/images/f/f5/Leia_Wicket.png —
  File:Leia_Wicket.png, Wicket W. Warrick meeting Leia Organa on Endor →
  `wookieepedia_wicket_with_leia.jpg`
- https://static.wikia.nocookie.net/starwars/images/2/20/EndorParty-ROTJ.png —
  File:EndorParty-ROTJ.png, Ewoks celebrating after the Battle of Endor →
  `wookieepedia_endor_celebration.jpg`
- https://www.starwars.com/databank/ewok — **cited by the article as `{{Databank|ewok}}`
  and is the source of the 1-meter height, but was NOT fetched directly this pass.** The
  height above is quoted from the Wookieepedia infobox, which attributes it there.
- **Unsourced, recorded as absent rather than guessed**: **lifespan**. (Height, mass, diet,
  origin, skin/hair/eye colour are all sourced — unusually complete for this batch.)

## Candidate images

- `wookieepedia_infobox_three_ewoks.jpg` — **the reference of record.** The Wookieepedia
  infobox image: three Ewoks in practical costume on a clean background, at high
  resolution. Settles the pot-bellied neckless body plan, the short stubby limbs and bare
  plantigrade feet, the pale short-furred muzzle patch, the small dark beady adult eyes,
  the universal hood, and — most valuably — **three distinct fur morphs in one frame**
  (mid-brown, solid black, grizzled grey-white).
- `wookieepedia_woklings_juveniles.jpg` — **the reference of record for juveniles, and the
  reason the eye question is resolvable.** Shows woklings with **enormous glossy domed
  black eyes**, plus an adult with **pale fur eye-rings**; also the only clear look at
  Ewok hands (small, pale, short-digited). Dim warm-lit film still, so not a palette
  authority.
- `wookieepedia_wicket_with_leia.jpg` — a film frame of Wicket W. Warrick with Leia Organa
  in the Endor forest. Low resolution and dim; kept for **habitat and human-scale
  comparison** only.
- `wookieepedia_endor_celebration.jpg` — a film frame of many Ewoks celebrating after the
  Battle of Endor. Kept as the best available check on **1-meter height against
  human-sized figures**, and as evidence of the species in numbers. Not a palette or
  detail authority.
- `donor_current_sprite.png` — the repo's own art,
  `SWX/Pawn/HeadAttachments/ewok/RoundEars_south.png`: a pair of round ears set high and
  wide. Greyscale render-node mask, complete in three facings, correct in shape and
  placement — and, with its two siblings, the complete inventory of Ewok art on disk.
  **No muzzle patch, no eye-ring, no fur body, no juvenile variant.**

## ruling

(empty — owner has not reviewed this race yet)
