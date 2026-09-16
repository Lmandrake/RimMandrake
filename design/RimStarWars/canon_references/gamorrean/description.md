# Gamorrean

**defName**: `RSW_RimMandrakeGamorrean` (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Assigned `Jawa_Junkers: A` (abundant) and `Jawa_HuttCartel: S`.

## Sourced text (Wookieepedia)
Infobox: **height 1.8 meters; mass 100 kilograms**; origin Gamorr; habitat forest;
language Gamorrean; skin colour **green** or **pink**; distinctions "upturned nose,
fangs, poor eyesight, tusks".

A species of **tall, strong bipeds**, the Gamorreans had **porcine traits**: an
**upturned, large-nostriled cartilaginous snout**, **jowls**, and **upturned
tusks**. Gamorrean younglings had **baby teeth** that would irritate them and
eventually come loose after some time. Their **hulking bodies were covered in
green or rarely pink, thick and hairless skin**. They had **five digits on every
extremity, each sporting a hard nail**; the digits of their hands included **an
opposable thumb**, which allowed them to easily grasp and handle objects. The
species had two sexes: males are **boars**, females are **sows**. Other species
used the term "pig" to insult Gamorreans.

**Unusual abilities / notable traits.** The only sourced physiological
peculiarity in the infobox is a negative one — 🔑 **poor eyesight** — which is
worth carrying into any stat or trait work as a deliberate weakness rather than
being quietly dropped. Nothing in the canon article claims Gamorrean regeneration,
toxin resistance or any other special capability; the species' whole profile is
strength and mass. Do not invent an ability here.

## Visual brief
🔴 **"Tall" is the word to distrust.** At 1.8 m a Gamorrean is only about
human-average height, and the full-body reference render reads unmistakably as
**short and enormously wide** — a barrel-chested, no-neck, big-bellied, bandy-legged
mass with the head sunk into the shoulders. The impression is *squat*, not *tall*.
Nothing in the images supports a lanky or towering build, and a sprite built from
the word "tall" will get the silhouette exactly backwards. **The correct read: human
height at 100 kg on a frame roughly twice human width.**

From the full-body reference render:
- **Colour is not flat green.** The body is a mid olive-to-grey-green, but the
  **centre of the face, the underside of the jaw and the belly are a much paler
  tan/cream** — a distinct pale ventral zone the two-word colour list
  ("green / pink") completely misses. The pale zone around the snout is the
  brightest area of the whole figure.
- **The head is disproportionately large** and sits directly on the shoulders with
  no visible neck. Broad flat skull, a leathery/bony crest ridge across the crown,
  heavy overhanging brow.
- **Two tusks curve UP from the lower jaw** past the sides of the snout — the
  single most identifying feature, and the reason the silhouette reads porcine at
  thumbnail size.
- **A large upturned snout with two big forward-facing nostrils**, blunt and flat
  at the tip — the snout is broad and stubby, not a long muzzle.
- **Small, deep-set, dark eyes** under the brow shelf — consistent with the
  "poor eyesight" note, and again the small-eyes-on-huge-head proportion.
- **Heavy hanging jowls** along the jaw line, continuous with the shoulders.
- **Skin is bumpy/warty and entirely hairless**, with a matte leathery finish.
- **Dress is crude and layered, and it is part of the read**: decorated metal or
  hardened-leather **shoulder pauldrons**, a **leather jerkin**, a **fur kilt or
  loin piece**, a **wide belt with a round central buckle**, **sandals with metal
  shin greaves**, and a **broad-bladed axe** carried in one hand. The
  Hutt-palace-guard look is what "Gamorrean" means visually to most players.
- **Five thick digits with hard nails** on the hands, confirming the text.
- The **infobox image** and the **animated Clone Wars** image agree on all of the
  above and on the pale-ventral/green-dorsal split; the animated piece pushes the
  green cooler and greyer, so the honest range is olive-green to grey-green.

**donor_current_sprite.png is weak evidence — but the shipped composite is better
than this file suggests, and that was verified rather than assumed.** The copied
file is `SWX/Pawn/HeadAttachments/gamorrean/tusks_south.png`: two tiny black tusk
marks and nothing else. **There is no Gamorrean head sprite on disk at all** —
`SWX/Pawn/HeadType/` has no `gamorrean` directory — so the species is a vanilla
RimWorld head with overlays. Checking the xenotype's gene list, the overlays that
ARE wired are `RSW_Face_tusks` (this file), `RSW_Face_jowls`,
`Headbone_MiniHorns`, `RSW_BodySizeGene_big`, `Body_Fat`, `Skin_Green` and
`RSW_Skin_DarkGreen` — so tusks, jowls, a big fat body and green skin all land.
**What no file on disk supplies: the upturned large-nostrilled snout** (the
species' defining feature after the tusks), **the pale tan ventral/facial zone,
the warty skin finish, and the crest ridge.** A Gamorrean in game is currently a
big green fat human with small tusks.

## Must show
- [ ] Squat and wide silhouette at roughly human height — barrel-chested, no visible neck, big-bellied, bandy-legged — never a lanky or towering build
- [ ] Olive-to-grey-green dorsal skin with a distinct paler tan/cream zone across the face centre, jaw underside and belly
- [ ] Two tusks curving up from the lower jaw past the sides of the snout
- [ ] A large, blunt, upturned snout with two big forward-facing nostrils
- [ ] Small, deep-set, dark eyes under a heavy overhanging brow
- [ ] Bumpy/warty, entirely hairless skin with a matte leathery finish

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Gamorrean (Wookieepedia article; direct page HTML
  is Cloudflare-walled — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Gamorrean&format=json&prop=wikitext`,
  36,323 chars, 2026-09-15)
- https://static.wikia.nocookie.net/starwars/images/9/9f/GamorreanGuard-CGSWG.png (File:GamorreanGuard-CGSWG.png → wookieepedia_guard_fullbody.jpg)
- https://static.wikia.nocookie.net/starwars/images/4/41/Gamorrean-BOBFADVG.png (File:Gamorrean-BOBFADVG.png, the infobox image → wookieepedia_infobox.jpg)
- https://static.wikia.nocookie.net/starwars/images/b/be/Gamorrean_prisoner_SaV.png (File:Gamorrean_prisoner_SaV.png → wookieepedia_animated_clonewars.jpg)
- NOT fetched this pass: https://www.starwars.com/databank/gamorreans (official Databank).

## Candidate images
- `wookieepedia_guard_fullbody.jpg` — **the reference of record.** A full-body
  Gamorrean guard on a transparent background, costume-photography fidelity.
  Settles the squat-and-wide silhouette (against the prose's "tall"), the pale
  ventral zone against olive-green dorsal, the upturned tusks, the blunt upturned
  snout, the small deep-set eyes under a brow shelf, the warty hairless finish, and
  the full pauldron/jerkin/fur-kilt/greaves/axe dress.
- `wookieepedia_infobox.jpg` — the Wookieepedia infobox image; independent
  agreement on head shape, tusks and palette from a different source.
- `wookieepedia_animated_clonewars.jpg` — a Clone Wars-era animated Gamorrean.
  Stylized, so treat line and exact hue as the artist's; its value is confirming
  the green-dorsal/pale-ventral split survives a different medium, at a cooler,
  greyer green.

## ruling
(empty — owner has not reviewed this race yet)
