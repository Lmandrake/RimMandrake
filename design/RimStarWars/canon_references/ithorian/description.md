# Ithorian

**defName**: `RSW_RimMandrakeIthorian`
(`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
🔴 Its `<nameMaker>` is **`RSW_KoTOR_NamerSullustan`** — the wrong species' name
generator (see Def-versus-canon).

## Sourced text (Wookieepedia)
Ithorians, **commonly referred to as "hammerheads,"** are a sentient species from the
planet **Ithor**, **living in the forests or jungles**. Infobox: skin **brown**
(Databank "byph"), **green** (*Rebels: Recon Missions*), **light brown** (*Star Wars
Lightsabers*), **orange** (*Rebels*, "The Future of the Force"); eyes **black, blue,
brown, orange, yellow**; habitat **forest or jungle**; recognised subspecies the
**Ottegan**; distinctions **curved neck**, **two mouths**, and **long lifespan**.
**Height, mass and the lifespan field itself are EMPTY** — the only quantity anywhere is
a footnote that in *Galaxy's Edge: Traveler's Guide to Batuu*, **Dok-Ondar is said to be
more than 240 years old**. That is one individual's age, not a species lifespan. Do not
invent a height, mass or lifespan.

*Biology and appearance*, in full: Ithorians **had a unique set of twin mouths on
opposite sides of their necks with four throats, making them speak in stereo with deep,
rumbling voices**. They **had two stomachs**. **Their unique throat structure prevented
them from speaking Galactic Basic Standard**, mitigated by devices such as the
**translator collar**, which translated from Ithorese into Basic. **They could be
Force-sensitive.** They were called **"leathernecks"** as an insult by Imperial
stormtroopers. **The Ottegan species were a genetic offshoot of the Ithorians**, with a
similar physiology but **only one mouth instead of two**.

**Behaviour.** **Most Ithorians were peaceful and revered nature. The species' pacifism
was so strong that they exiled violent individuals from their homeworld of Ithor.** They
considered Ithor sacred and **strictly prohibited hunting on the planet's surface**. A
majority of Ithor's surface was the **Mother Jungle**, a vast rainforest they held
sacred and **forbade anyone from setting foot within**, while they tended forest gardens
elsewhere. Ithorians were **organized into herds — extended tribes connected by
tradition and intermarriage**. Culture valued nature and handcraft: **Ithorian totems**
hand-carved from stone marked graves and carried deep spiritual meaning, and **Ithorian
Weather Chimes** were handcrafted and prayed to for fertile soil and good weather.

## Visual brief
Three canon references, tightly consistent, and the thing they agree on is not a head —
it is a **neck**.

- 🔑 **The defining structure is a long, thick, muscular neck that rises from the
  shoulders and curves FORWARD and DOWN**, carrying the head out in front of the chest
  like a swan's or a vulture's. In `wookieepedia_ithorian_swtve.jpg` (a profile view of
  a physical costume) it is unmistakable: the neck is as thick as the torso and arcs a
  long way forward. **This cannot be expressed in a head sprite alone**, and it is the
  single most important fact in this entry.
- **The head itself is a T-shaped hammer crossbar at the top of that neck**, wider than
  it is deep, with **the eyes at the extreme outer ends of the crossbar on protruding
  lateral pods** — very far apart, facing outward and forward. Hence "hammerhead."
- **The twin mouths are on the SIDES OF THE NECK, not on the face.** On Mok Shaiz the
  right-side mouth is plainly visible as a large oval opening ringed with plate-like
  teeth partway down the neck, with a metal band/collar fitted around it. There is **no
  mouth on the front of the head at all** — the front of the neck instead carries a
  broad, smooth, downward-hanging fleshy lobe.
- **Skin is leathery, deeply wrinkled and creased**, especially across the crossbar and
  along the neck — "leathernecks" is descriptive, not just an insult.
- 🔴 **The hands are THICK, SHORT, BLUNT and few-digited** — heavy stubby fingers with
  broad pads, reading closer to a tortoise's or elephant's foot than a human hand. The
  feet are the same: broad, splayed, three thick toes. This directly contradicts the
  `ElongatedFingers` gene in the def.
- **Build: bulky and heavy through the torso with relatively short legs and a stooped,
  forward-leaning stance** — the forward-carried head pulls the whole posture over.
  Consistent across all three images.
- **Palette varies across individuals and all of it is in the earth range**: Mok Shaiz
  is a warm olive-tan/yellow-ochre; Onca is a pinkish-tan; Bulduga is a darker
  grey-brown; the costume photo is mid-brown. **Nothing is blue.**
- Costume note worth having: Mok Shaiz wears dark green robes with gold embroidery
  (a magistrate); Onca and Bulduga wear vests, bandoliers, gunbelts, boots and in one
  case a wide-brimmed hat (bounty hunters). The species is not visually locked to
  pacifist gardener dress even though that is the cultural default.

`donor_current_sprite.png` is the mod's current head mask (greyscale — correct, tinted at
runtime). It gets the general idea: a broad upper cranium with two eyes in lateral
protruding pods, and a long tapering lobe descending below. What it misses: the **eyes
are far too small and set too far inboard** — they should be out at the tips of a wide
crossbar; the **hammer T-shape is compressed into a rounded dome**; there are **no mouths
on the sides**; and the wrinkle/crease texture is absent. Most fundamentally, a
RimWorld head sprite **cannot carry the forward-curving neck**, which is where both mouths
live and where most of the species' silhouette is. Whatever is done here, that compromise
should be documented rather than hidden.

## Def-versus-canon (flagged)
- 🔴 **`nameMaker` is `RSW_KoTOR_NamerSullustan`** — Ithorian pawns are being named as
  Sullustans. A concrete, cheap bug; note the file already contains species-specific
  namers for other races, so a correct one may exist or may need writing.
- 🔴 **`ElongatedFingers` contradicts every canon image.** Ithorian hands are short,
  thick and blunt-digited. This is a visible, wrong-in-game trait.
- 🔴 **`Outland_Skin_DeepAzure` (blue) is unsourced**, and **orange — which IS sourced**
  (*Rebels*, "The Future of the Force") — has no gene. `Skin_PaleRed` is also unsourced.
  The sourced palette is brown / light brown / green / orange, i.e. entirely earth tones;
  `Outland_Skin_DeepSage`, `Outland_Skin_DeepBrown` and `Outland_Skin_Brown` cover three
  of the four correctly.
- 🔴 **`Outland_EggLayer` is unsourced.** Nothing in the article attests egg-laying.
  `Outland_DeceleratedPregnancy` is likewise unsourced.
- 🔴 **"Long lifespan" is a listed infobox distinction and there is no lifespan gene.**
  Dok-Ondar at 240+ years is the attested datum. Note that the *number* is one
  individual's age, so a multiplier should be recorded as a judgement, not as canon.
- 🔴 **Pacifism — the species' single most distinctive cultural fact, strong enough that
  they exiled violent individuals from their homeworld and banned hunting on it — is
  unrepresented.** No aversion, no penalty, no trait. This is the biggest behavioural
  gap in the entry.
- ⚠️ **Force sensitivity** ("They could be Force-sensitive") is unrepresented — noted as
  canon content, deferred with everything Force-related.
- ⚠️ **`RSW_BodySizeGene_big` and `MoveSpeed_Slow` are unsourced.** No height or mass
  exists for the species. Both are defensible from the bulky, stooped, short-legged build
  in the images, but they rest on the art, not on a number — record them as reads, not
  facts.
- ✅ Correct and canon-supported: **`StrongStomach` + `RobustDigestion`** (canonically
  **two stomachs** — a good match), **`Outland_UnusualSpeech`** (four throats, stereo
  deep rumbling voice, and a physical inability to speak Basic — well chosen),
  **`AptitudeStrong_Plants`** (forest gardeners who revere nature and tend the Mother
  Jungle — the strongest def/canon match here), **`RSW_IthorianHead`** as a concept,
  **`Hair_BaldOnly` + `Beard_NoBeardOnly`**, **`Outland_Skin_DeepSage`/`DeepBrown`/`Brown`**.
- Not representable, recorded so nobody "fixes" it: **two mouths, four throats**. The
  **translator collar** is a canonical worn item and could be real gear rather than a
  gene — Mok Shaiz visibly wears a band at his neck mouth.
- Unbuilt canon hook: the **Ottegan**, a genetic offshoot with identical physiology but
  **one mouth**, has no def. Flagged as existing canon content, not a defect.

## Source URLs
- https://starwars.fandom.com/wiki/Ithorian (article HTML Cloudflare-walled; wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=Ithorian&format=json&prop=wikitext`,
  38,530 chars, 2026-09-15)
- File:MokShaiz-CGSWG.png — the infobox image (Mok Shaiz, mayor of Mos Espa) →
  `wookieepedia_mokshaiz_cgswg.png`
- Onca and Bulduga, Ithorian bounty hunters and brothers — the *Biology and appearance*
  inline image → `wookieepedia_oncabulduga_db.png`
- A physical Ithorian costume/figure in profile, from *Star Wars: The Visual
  Encyclopedia* → `wookieepedia_ithorian_swtve.jpg`
- NOT fetched this pass: https://www.starwars.com/databank/ithorians (official Databank —
  the source for the curved neck, two mouths and sentience citations).

## Candidate images
- `wookieepedia_mokshaiz_cgswg.png` — **the reference of record.** Film-quality Mok
  Shaiz seated in dark green gold-embroidered robes: settles the hammer-crossbar head
  with eyes at the outer tips, the thick forward-curving neck, **the side-of-neck mouth
  with its plate teeth and fitted collar band**, the olive-tan wrinkled leathery hide,
  and the short blunt thick-digited hands and broad three-toed feet.
- `wookieepedia_ithorian_swtve.jpg` — **the best view of the neck**, which is the whole
  species: a physical costume photographed near-profile in a cream coat, showing how far
  forward and how thick the neck arcs. Photographed from a printed page (paper grain
  visible), so treat hue as approximate; treat the silhouette as authoritative.
- `wookieepedia_oncabulduga_db.png` — Onca and Bulduga, two Ithorian bounty hunters, one
  pinkish-tan and one grey-brown, in vests, bandoliers and a wide-brimmed hat. Confirms
  the head/neck plan recurs across individuals while the hue shifts, and shows the
  species out of pacifist-gardener costume. Small in frame.
- `donor_current_sprite.png` — the mod's current head mask, for comparison only. Right
  idea, wrong proportions; see the visual brief.

## ruling
(empty — owner has not reviewed this race yet)
