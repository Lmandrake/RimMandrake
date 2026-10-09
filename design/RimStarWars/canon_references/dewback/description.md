# Dewback

**defName**: `RSW_Dewback` (vendored in this repo's own `src/RimStarWars/SWBestiary` mod)

## Sourced text (Wookieepedia)
Dewbacks were thick-skinned reptiles native to the desert planet of Tatooine,
used as beasts of burden and as mounts for specialized sandtroopers ("Dewback
troopers"). Rugged reptilian lizards, they withstood the heat of Tatooine's
binary suns and the dust that fouled high-tech vehicles. Wookieepedia gives:
thick hides of **scaly green skin**, **long, rounded heads and short tails**,
with their **backs partially covered with fur**. Four clawed feet, capable of
brief bursts of speed when prodded but otherwise plodding. Height 2 meters (Databank); the infobox also lists length 9 meters
(*Star Wars Encyclopedia: The Comprehensive Guide*), but the article's Behind the scenes notes the
reference books mis-convert these units (*Ultimate Star Wars* turned a 6 ft height into 9 m; the
Encyclopedia lists 9 m length but "six feet"), so treat the 9 m figure as unreliable.
Females lay fifty to eighty-five eggs each standard year; lethargic at night and in cold climates;
"plodding but reliable" mounts with brief bursts of speed. Two breeds: pearled and witla.
Named for licking morning dew off their backs with a flicking tongue. Diet:
tubers, grass, womp rats, sage, desert vegetation (omnivore). Canon role:
Tatooine's default riding/pack beast — moisture farmers, merchants, Mos Eisley
locals, and above all Imperial sandtroopers on patrol ride dewbacks; Obi-Wan
Kenobi owned one while in hiding on Tatooine (*Rebels*, "Twin Suns"). Podrace
crews used them to haul podracer parts to the starting grid in *The Phantom
Menace*. Appears on-screen in *A New Hope* (first appearance; animatronic, with some back fur in
the original version, replaced by a CGI version in the 1997 Special Edition), *The Phantom Menace*,
*Rebels* "Twin Suns", and *The Mandalorian* "Chapter 5: The Gunslinger".

## Visual brief
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."** The smooth, cartoon-shaded Star Wars Insider illustration of Obi-Wan riding a bright yellow-green dewback (`wookieepedia_kenobi_screencap.jpg`) was deleted. The remaining references are realistic: `wookieepedia_infobox.jpg` (realistic CGI side profile, the image this entry's ruling picked) and `wookieepedia_behindthemagic.jpg` (*A New Hope* live-action practical dewback with a sandtrooper rider, the ruling's "#4").

What they show:
- **Body:** elongated, heavy, low-slung lizard body on short, thick, bowed legs with blunt clawed toes; a long, heavy, tapering tail dragging low; a deep belly.
- **Head:** broad, heavy, blunt-snouted head with a wide closed mouth line and small eyes under a heavy brow.
- **Hide:** dense small pebbled/raised scales over the whole body, thick folded skin at the neck and legs. 🔴 **Colour differs between the two realistic sources:** the CGI infobox is a dusty **grey-brown / taupe**, while the ANH live-action puppet reads **olive to yellow-green** in sunlight. The deleted cartoon was bright yellow-green — do not use that saturation. Aim for a muted, dusty olive-to-grey-brown desert reptile.
- No back "fur" is legible in any image; treat the text's partial back fur as subtle at most.

**The current donor sprite (`donor_current_sprite.png`) disagrees with canon
in two clear ways**: it is rendered in flat **grey/white**, not green, and it
has a rounded, blobby, almost seal-like silhouette with no scale texture and
no elongated tail — closer to a cartoon manatee than the long low reptile
in every reference image. Any regen should correct the color to dusty olive/grey-brown
and give the body a longer, lower, more lizard-like silhouette with a visibly
scaled hide.

## Must show
- [ ] Scaly, reptilian, elongated low-slung body — not a rounded, blobby, seal-like silhouette
- [ ] Muted, dusty olive-green to grey-brown hide (between the ANH puppet and the CGI profile), not bright yellow-green
- [ ] Long heavy tail carried low
- [ ] Broad, heavy, blunt-snouted head with a wide mouth line
- [ ] Short, thick, bowed legs built to carry a rider or pack saddle
- [ ] Dense small pebbled scale texture all over, with thick folded skin at neck and legs
- [ ] Realistic rendering: natural pebbled reptile-hide texture and desert lighting, no outlines, no cartoon shading

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Dewback (Wookieepedia article text, pulled
  via `starwars.fandom.com/api.php?action=parse&page=Dewback&prop=wikitext`,
  2026-09-13)
- https://static.wikia.nocookie.net/starwars/images/7/7d/Dewback-CGSWG.png (infobox art, *Star Wars: Creatures Great and Small*/CGSWG source)
- https://static.wikia.nocookie.net/starwars/images/c/c0/KenobiDewback-SWI211.png (Star Wars Insider #211 — Obi-Wan Kenobi riding a dewback)
- https://static.wikia.nocookie.net/starwars/images/1/11/Dewback_btm.jpg (behind-the-scenes/making-of still — a sandtrooper astride a dewback on location)

## Candidate images
- `donor_current_sprite.png` — this repo's current shipped sprite (SWBestiary mod, east-facing base variant), grey/white, non-scaly, blob-shaped
- `wookieepedia_infobox.jpg` — Wookieepedia infobox realistic CGI render, full side profile, green scaly hide, long tail, clearly reptilian body plan
- `wookieepedia_behindthemagic.jpg` — *A New Hope* live-action practical dewback (Star Wars: Behind the Magic), sandtrooper close-up astride a dewback, shows scale texture and eye/head detail against blue sky

## ruling
**RULED** (owner, 2026-09-14, review sheet): `wookieepedia_infobox.jpg`

> "I think the Donor white shading means it can come in a variety of colors or something, Rimworld seems to do this sometimes. Follow #4 closest."
