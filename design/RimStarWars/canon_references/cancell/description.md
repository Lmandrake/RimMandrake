# Can-cell

**defName**: `RSW_CanCell` (vendored in SWBestiary, texture folder `CanCell`)

## Sourced text (Wookieepedia)
A species of flying insect found on many planets across the galaxy —
Kashyyyk (first/primary appearance, *Star Wars: Episode III – Revenge of the
Sith*), Batuu, Aleen, Ryloth, Rodia, Taul, and Teth. Class: Insect.
Skin color: **red and blue**. Eye color: **green**. Length: more than 3
meters (9 ft 10 in) — a large creature, not a small bug. They have **quad
wings** (two pairs) and large eyes. Wookiees on Kashyyyk consider seeing a
can-cell good luck and modeled the *Raddaugh Gnasp* fluttercraft's design on
them; can-cells are drawn to the buzzing engine sound of Wookiee jet
catamarans and congregate at their landing pads. Some Batuu residents keep
native can-cells as pets. In *The Clone Wars* film, Anakin Skywalker and
Ahsoka Tano ride one on Teth to escape Asajj Ventress and reach the
*Twilight*. Length (>3 m) is
from *The Visual Encyclopedia*, not a wingspan or height. Also named as
present on Taul and in *Bombad Jedi* (Rodia), *Mercy Mission* (Aleen) and
*Innocents of Ryloth* (carcass). The separate Legends page
(https://starwars.fandom.com/wiki/Can-cell/Legends) gives 3.35 m, red-brown
skin, green eyes. Source: https://starwars.fandom.com/wiki/Can-cell

## Visual brief
Three images, and they diverge in fidelity/style but agree on the core
dragonfly-like body plan:
- **The movie-accurate CGI render (Teth, *Clone Wars* film)** is the clearest
  selected visual reference (both films are canon; this is clarity, not rank): an elongated **red/maroon segmented insectoid
  body**, large **bright green compound eyes** (exact match to the "eyecolor:
  Green" field), **dark blue-black jointed legs**, yellow-tipped antennae/
  mandible fringe, and two pairs of long, thin, translucent dragonfly wings
  extending in both directions — this is the strongest single confirmation
  of the sourced "red and blue" skin + "green" eyes.
- **The ROTS Kashyyyk wide shot** shows only a small silhouette in flight
  over misty mountains — confirms the elongated dragonfly-like flying
  silhouette and large wingspan relative to body, but no usable color detail
  at this resolution.
- **The "TGTB" image** (File:Can-Cell-TGTB.png, the canon page's own infobox
  image; "TGTB" abbreviates *Star Wars: Galaxy's Edge: Traveler's Guide to
  Batuu*, which the page cites for quad wings, large eyes and Batuu pet
  can-cells) shows a **brown/tan feathered-looking body** with a rounded
  **teal/turquoise crest** on the head and long clawed legs, gliding on what
  appear to be tether lines — bird-like in my reading; its palette does not
  match the film's "red and blue". Treat the Teth CGI render as the colour
  reference; this image is the Batuu-context depiction.

**The current donor sprite** (`donor_current_sprite.png`) shows an
insect/dragonfly-like creature with a long segmented body, a pair of large
translucent wings, and a distinct head with a visible eye — muted pink/cream/
tan coloring with faint blue-ish streaks near the head/neck. It agrees with
canon on the broad body plan (elongated insect with large wings) but its pale
pink-tan palette matches neither the sourced "red and blue" skin nor either
candidate image's palette well; the closest canon match for color is the Teth
CGI render (red body, blue legs, green eyes) — a regen should push the donor's
washed-out pink-tan toward that stronger red/blue/green palette.

## Must show
- [ ] Elongated, segmented dragonfly-like insectoid body
- [ ] Two pairs of long, thin, translucent wings
- [ ] Large compound eyes reading green
- [ ] Body colour reads red/maroon with dark blue-black legs, not pale pink-tan

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Can-cell (Wookieepedia, fetched via the
  MediaWiki API `action=parse&prop=wikitext` endpoint, 2026-09-13)
- https://starwars.fandom.com/wiki/File:TethCan-cell-TCW.png
- https://starwars.fandom.com/wiki/File:Can-cell_kashyyyk.png
- https://starwars.fandom.com/wiki/File:Can-Cell-TGTB.png

## Candidate images
- `donor_current_sprite.png` — this repo's current shipped sprite (SWBestiary
  mod, east-facing base variant): elongated insectoid body with large
  translucent wings, pale pink/cream/tan coloring with faint blue streaks
  near the head — matches the general insect-with-wings body plan but not
  the sourced red/blue/green palette.
- `wookieepedia_teth_tcw.jpg` — clean CGI model render from *The Clone Wars*
  film (Teth sequence): red/maroon segmented body, bright green compound
  eyes, dark blue legs, two pairs of long thin wings. **Strongest/most
  authoritative reference.**
- `wookieepedia_rots_kashyyyk.jpg` — wide establishing shot from *Revenge of
  the Sith*'s Kashyyyk battle: a small dragonfly-silhouette in flight over
  misty mountain terrain, confirms flight silhouette and wingspan only.
- `wookieepedia_tgtb.jpg` — a differently-styled render (brown/tan feathered
  body, teal head crest, bird-like) that disagrees with the sourced "red and
  blue" coloration; included as a documented outlier, not a recommendation.

## ruling
**RULED** (owner, 2026-09-14, review sheet): `wookieepedia_teth_tcw.jpg`

> "Rename to Can-cell. Follow this render: https://static.wikia.nocookie.net/starwars/images/9/94/Can-cell.png/revision/latest/scale-to-width-down/1000?cb=20220914023816 (same as #3)"
