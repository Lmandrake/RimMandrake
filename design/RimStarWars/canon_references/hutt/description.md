# Hutt

**defName**: `RSW_RimMandrakeHutt` (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Assigned `Jawa_HuttCartel: A` — abundant, and the Cartel's defining species.
Note `04_factions.md`: **"A Hutt never appears in a raid group"** — Hutts are seen
seated in palaces, so the *sitting* silhouette matters more than a walk cycle.

## Sourced text (Wookieepedia)
Hutts are a sentient, **reptiloid** species. Infobox: **length 3.9 meters**
(length, not height — a Hutt is measured like a snake); **lifespan up to 1,000
years**; distinctions **3 lungs** and **slug-like**; habitat swamp; language
Huttese; origin Varl, later Nal Hutta. Skin color is listed as a very wide
individual menu — black, blue, brown, gold, green, mottled brown, pink, purple,
tan, white, yellow — and eye color as blue, gray, green, orange, turquoise,
violet, yellow.

Hutts were a massive slug-like reptiloid species who had **large mouths and stubby
arms**. They had **three lungs**. They were tough and muscular with **thick
leathery skin, which was wrinkled and slimy**. Hutts often had **watery eyes and
slack facial expressions**. **Their tails were supported by a skeletal spine and
allowed Hutts to propel themselves through muck which legs would sink into** — the
tail is a locomotor organ, not decoration. Hutts possessed skeletons and were not
known for being healthy. **Some Hutts suffered from a genetic defect that caused
their skin to be bereft of pigment and prone to cracking** (a canonical albino /
cracked-skin variant, if a pale Hutt is ever wanted).

Nal Hutta — a planet with a hot atmosphere frequently streaked by greasy rains,
creating a fetid sauna in which Hutts were most comfortable — later became their
considered homeworld.

**Unusual abilities.** 🔑 **Hutts were immune to mind tricks.** That is the one
hard mechanical trait the article gives, and it is a Force-resistance, so it
matters if Force powers ever land (v2 per `04_factions.md`). Longevity is the
other: Hutts could live for centuries — **Jabba was 604 when he was killed** — and
lifespans could span over 1,000 years, while growing to enormous sizes.

**Life cycle, which the art must respect.** Despite their legendary adult size,
Hutts started out as tiny **Huttlets less than half a meter in height**. Hutts
spent **the first 50 years of their life in the brood pouches of their parents**;
when they emerged, they were described as having the mind of an infant. The
literary collective term for Hutts was **a bulge of Hutts**.

## Visual brief
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."**
The comic council panel (`wookieepedia_hutt_council_comic.jpg`) was removed. The adult references are now all realistic: `wookieepedia_adult_jabba.jpg` (photoreal full-body render), `wookieepedia_jabba_palace_rotj.png` (Return of the Jedi live-action puppet, full body with tail, beside Bib Fortuna), `wookieepedia_jabba_puppet_face.png` (puppet face close-up) and `wookieepedia_rotta_adult_mandalorian_and_grogu.png` (a second adult Hutt, Rotta, live-action CGI from *The Mandalorian and Grogu*). The Clone Wars Huttlet (`wookieepedia_huttlet.jpg`) is **kept only as animated reference for juvenile proportions** — no realistic juvenile Hutt exists; render one realistically anyway.

🔴 **Where the live-action look refines the old brief:** the real Jabba puppet is **warmer and browner** than "olive/grey-green" suggests — dorsal surfaces are **olive-brown to dark khaki**, the face and belly **orange-tan to reddish-brown** (strongly reddish in the face close-up), and the whole hide is **deeply furrowed and glistening**, with heavy horizontal fold lines across the brow and the belly. Rotta (live-action) is **grey-olive and much more uniform**, with only a slightly paler belly — so the dorsal/ventral two-tone is strong in Jabba and weak in Rotta. Preserve the wet, furrowed, heavy-folded hide in every case; let hue vary from olive-brown to grey-olive.

🔴 **The infobox's eleven-colour skin menu badly misrepresents the canonical
Hutt, which is TWO-TONE with a specific arrangement.** The adult reference image
(Jabba, full body, transparent background) shows:

- **Dorsal and limb surfaces mottled dark olive/grey-green with darker blotches**
  — the crown of the head, the back, the outsides of both arms and the whole tail.
- **Ventral surfaces warm pale peach/salmon-tan** — the entire front of the belly,
  the chest, the underside of the jaw and the lower face.
- **The transition is a wide speckled/mottled band, not a hard edge.** A flat
  single-colour Hutt (either green OR tan) is the failure mode a text-only prompt
  produces from the colour list, and it is wrong for the iconic case.
- **Skin reads WET.** Specular highlights across the belly and head, plus fine
  crazed wrinkle networks over the whole ventral surface — the "wrinkled and
  slimy" text is doing real work and should not be dropped.

Head and face, from the same image:
- **Enormously wide, thin-lipped mouth spanning the full width of the head**, with
  the corners turned down; the mouth is the widest feature of the silhouette.
- **Small eyes set high and wide on a broad flat skull, amber/yellow with
  horizontal slit pupils**, under heavy shelf-like brow ridges — small eyes on a
  huge head is the proportion to hit, and it matches "watery eyes and slack facial
  expressions."
- **Broad flat nose with two slit nostrils**, low on the face between the eyes and
  the mouth.
- **Multiple heavy jowl/chin folds** stacked under the jaw, continuous with the
  belly folds — the head does not have a neck.
- **Arms are short, thick and set high on the chest**, ending in broad hands with
  **three thick blunt digits**; they read as vestigial relative to the mass.
- **The tail is long, tapering and dorsoventrally flattened**, laid flat on the
  ground and extending well behind the body — consistent with the "skeletal spine
  supported / propels through muck" text.
- **Posture: the torso rears upright while the mass sits on the coiled tail.** The
  species has no legs at all. Any RimWorld representation is going to be a
  compromise here, and the compromise should be documented rather than hidden.

The **Huttlet** image (animated, *The Clone Wars*) is the other end of the life cycle and confirms the
half-metre juvenile: much greener overall, proportionally enormous head and eyes, tiny arms, short blunt tail.
**A Huttlet is not a small Jabba — the proportions genuinely differ.** Jabba and Rotta together show that the
hue varies between individuals (olive-brown, grey-olive) while the body plan, the furrowed wet hide and the
paler underside stay constant.

**donor_current_sprite.png is weak evidence, but not for the reason it looks.** It
is `SWX/Pawn/HeadType/hutt/Male_FatHead_south.png` — a **greyscale mask**, which
is correct and expected for a RimWorld humanlike head: the game tints these at
runtime from the pawn's skin-colour gene, so the absence of colour here is NOT a
defect and the canon hue findings above belong on the *gene*, not on this file.
What IS missing is shape: the sprite is a broad low triangular dome with a wide
down-turned mouth (which does capture the wide-mouth and low-broad-skull reads)
but has **no jowl folds, no nostril slits, no brow shelf and no wrinkle
texture**, and its eyes are ordinary small dots rather than slit-pupilled. More
fundamentally, the mod represents a Hutt as **a head on a normal humanoid
RimWorld body** — the only Hutt body art on disk is
`SWX/Pawn/BodyAttachments/hutt/bp_fat_{east,north}.png`, i.e. a fat body-plate
overlay with no south variant and no tail at all. **The legless, tail-propelled
body plan — the species' single most defining feature — is not represented.**

## Must show
*Rewritten 2026-10-09 to the canon_check leniency lesson (`Transient/canon_check_leniency_2026-10-09.md`): body plan, colour layout and a negative, each checkable on a 256px sprite. Grounded in the live-action/photoreal adult references (Jabba render, ROTJ puppet, Rotta) and the canon prose, per the visual brief.*
- [ ] BODY PLAN: a massive legless slug: the torso rears upright and the mass sits on a long, tapering, dorsoventrally flattened tail that lies along the ground behind the body; short thick arms set high on the chest ending in broad hands with three thick blunt digits
- [ ] Head: broad and flat with NO neck — heavy jowl/chin folds stacked under the jaw run continuously into the belly folds
- [ ] Mouth: enormously wide, thin-lipped and down-turned, spanning the full width of the head (the widest feature of the face), with a broad flat nose with two slit nostrils above it
- [ ] Eyes: small orange/amber eyes with horizontal slit pupils, set high and wide under heavy shelf-like brow ridges
- [ ] COLOUR LAYOUT: darker dorsal surfaces (crown, back, outsides of the arms, tail) olive-brown to grey-olive, over a paler tan/orange-brown belly, chest, jaw underside and face, blended through a mottled band rather than hard-edged; whole hide deeply furrowed and glistening wet, with heavy horizontal folds across brow, jowls and belly
- [ ] Realistic rendering: live-action puppet skin texture and lighting, no outlines, no cartoon shading (owner ruling 2026-10-08: "That's realistic, not these cartoon versions you keep using.")
- [ ] NEGATIVE: not a fat human or humanoid with legs (no legs, no neck), not a flat single-colour green or tan slug, not dry matte skin; an adult is not a Huttlet (no oversized head and eyes)

## Engine limits
none known — the head-mask colour findings above belong on the skin-colour gene, not on the
donor sprite. The unrepresented legless, tail-propelled body plan is a missing-art gap, not
a rendering constraint.

## Source URLs
- https://starwars.fandom.com/wiki/Hutt (Wookieepedia article; direct page HTML is
  Cloudflare-walled — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Hutt&format=json&prop=wikitext`,
  73,505 chars, 2026-09-15)
- https://static.wikia.nocookie.net/starwars/images/c/cc/Jabba-USCVV.png (File:Jabba-USCVV.png, the infobox "Adult" option → wookieepedia_adult_jabba.jpg)
- https://static.wikia.nocookie.net/starwars/images/b/b8/Rotta-SWCT.png (File:Rotta-SWCT.png, the infobox "Huttlet" option → wookieepedia_huttlet.jpg)
- NOT fetched this pass: https://www.starwars.com/databank/jabba-the-hutt (official
  Databank; a species-level Databank page was not attempted).

## Candidate images
- `wookieepedia_adult_jabba.jpg` — **reference of record for the body plan.** Infobox "Adult" image, file `Jabba-USCVV.png`: photoreal full-body Jabba on a transparent background — two-tone hide, wide mouth, three-digit stubby arms, flattened tail. https://static.wikia.nocookie.net/starwars/images/c/cc/Jabba-USCVV.png
- `wookieepedia_jabba_palace_rotj.png` — *Return of the Jedi* live-action puppet, full body on his dais with the tail laid out, Bib Fortuna beside for scale; file `BibFortunaJabba-CGSWG.png` — https://static.wikia.nocookie.net/starwars/images/5/55/BibFortunaJabba-CGSWG.png/revision/latest?cb=20250127035911
- `wookieepedia_jabba_puppet_face.png` — the Jabba puppet's face close-up (*The Moviemaking Magic of Star Wars: Creatures & Aliens*): furrowed reddish-brown wet hide, slit-pupilled orange eyes, brow shelf, nostril slits; file `Jabba MMSWCA.png` — https://static.wikia.nocookie.net/starwars/images/f/fe/Jabba_MMSWCA.png/revision/latest?cb=20231031040818
- `wookieepedia_rotta_adult_mandalorian_and_grogu.png` — Rotta as an adult, live-action CGI, *The Mandalorian and Grogu*: a second individual, grey-olive and more uniform in hue; file `Rotta-MG-Profile.png` — https://static.wikia.nocookie.net/starwars/images/1/1b/Rotta-MG-Profile.png/revision/latest?cb=20260512153846
- `wookieepedia_huttlet.jpg` — **animated (The Clone Wars), juvenile proportions only.** Infobox "Huttlet" image, file `Rotta-SWCT.png`: huge head and eyes, tiny arms, short blunt tail. Not a rendering-style target. https://static.wikia.nocookie.net/starwars/images/b/b8/Rotta-SWCT.png

## ruling
(empty — owner has not reviewed this race yet)
