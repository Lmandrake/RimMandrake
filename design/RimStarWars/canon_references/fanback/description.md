# Fanback

**defName**: `Fanback` (third-party, mlie.starwarsanimalcollection, not vendored — see Watch out)

## Sourced text (Wookieepedia)
Legends-only entry (page carries the `{{Top|leg}}` Legends banner — no current-canon
page exists for this creature). Source: *Episode I Adventures 11: Pirates from
Beyond the Sea*, cited via the "Complete Star Wars Encyclopedia".

- **Species infobox**: skin color listed as **Green**; origin **Naboo**. No
  height/length/mass/lifespan fields filled in.
- **Body plan**: a cold-blooded amphibian with a large dorsal spine (sail) and a
  sensitive snout.
- **Diet/behavior**: carnivore; preyed on "egg-eaters" (a separate Naboo species).
- **Canon role**: minor background fauna. Shortly after 32 BBY the Gungans
  transported fanbacks (and other animals) to the moon Ohma-D'un to try to
  establish an ecosystem there; most of that flora/fauna was later destroyed by
  Separatists during the Battle of Ohma-D'un.
- **Behind the scenes**: the wiki explicitly notes the fanback resembles the
  extinct Earth species *Dimetrodon* (the sail-backed "mammal-like reptile," not
  a dinosaur, despite popular association).
- **Appearances**: *Episode I Adventures 9: Rescue in the Core*, *Episode I
  Adventures 11: Pirates from Beyond the Sea*, and the PC game *Star Wars
  Episode I: The Gungan Frontier* (first appearance). Non-canon: *Star Wars:
  Super Bombad Racing*.

## Visual brief
Only two images exist on the Wookieepedia page: the species infobox
illustration and a separate "fanback egg" illustration (a nest scene, no
adult animal visible). Both are the same era/style of Episode I Adventures
book illustration — muted, painterly, sepia-toned page background.

- `wookieepedia_infobox.jpg` — the primary (and only) reference for the
  animal itself. Shows a **Dimetrodon-shaped** reptile/amphibian: squat
  low-slung body, thick tail, short stubby legs, and a wide toothy jaw with
  visible lower fangs — reads as an active predator, not docile. Body color
  is **tan/khaki-olive with darker brown mottled spots**, NOT the vivid or
  clean green the infobox metadata field claims. The dorsal sail is the
  standout feature: tall, rounded, running most of the spine's length,
  colored a darker brown-to-near-black at its trailing/upper edge, lighter
  tan at its base where it meets the body.
- `wookieepedia_egg.jpg` — no animal visible; shows only a sand/mud nest
  mound with dry grass tufts and one large cream-white egg with fine dark
  speckling, half-buried in a shallow brown depression. Useful only for
  confirming egg-laying (oviparous) behavior and a desert/dune nesting
  habitat consistent with Naboo's swamp-adjacent drylands, not for body
  color.

**Text vs. image disagreement**: the species infobox metadata field says
`skincolor=Green`, but the actual illustration does not read as green — it
reads as tan/olive-brown with dark mottling, closer to a real-world monitor
lizard or Dimetrodon reconstruction than anything green-skinned. Treat the
illustration as the stronger signal (per this library's standing rule that
images outrank text), and note the "Green" field as likely an
approximation/rounding by whoever filled in the old infobox rather than an
accurate description of the single piece of art that exists. No second
independent image exists to cross-check this against, which is itself worth
flagging: this creature has effectively **one** surviving canon depiction.

**Net read for art**: sail-backed, Dimetrodon-silhouette reptilian
amphibian; tan/khaki-olive base coat with darker brown mottled spots; sail
darker brown to near-black along its edge; toothy predator jaw; short legs;
thick tail; desert/mudflat nesting habitat with a large speckled egg.

## Must show
- [ ] Dimetrodon-shaped body: squat, low-slung, thick tail, short stubby legs
- [ ] Tall, rounded dorsal sail running most of the length of the spine
- [ ] Tan/khaki-olive base coat with darker brown mottled spots
- [ ] Sail colored darker brown-to-near-black at its trailing/upper edge, lighter tan at its base
- [ ] Wide, toothy jaw with visible lower fangs

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Fanback (page; fetched via MediaWiki API
  `action=parse&prop=wikitext`, 2026-09-13, since the direct page URL
  returned an error through the fetch tool available this pass)
- https://starwars.fandom.com/api.php?action=parse&page=Fanback&format=json&prop=wikitext
- https://static.wikia.nocookie.net/starwars/images/d/db/Fanback.jpg
  (species infobox illustration)
- https://static.wikia.nocookie.net/starwars/images/1/1e/Fanback_eggpic.jpg
  (fanback egg/nest illustration)
- Donor mod `mlie.starwarsanimalcollection` — checked the current Steam
  Workshop page directly (id 3497316713, "Star Wars Animal Collection
  (Continued)"). "Fanback" appears exactly once on that page, as a bare
  text entry in the mod's alphabetical list of included creatures
  (`...Falumpaset<br>Fambaa<br>Fanback<br>Feral Grazer...`) — **not** as a
  captioned screenshot. The page's actual image hosts
  (`avatars.akamai.steamstatic.com`) are all commenter/rater avatar
  thumbnails, not mod preview screenshots. No screenshot of any kind
  specifically showing a Fanback was found on the workshop page.

## Candidate images
- `wookieepedia_infobox.jpg` — Fanback species infobox illustration
  (Episode I Adventures book art): sail-backed Dimetrodon-shaped predator,
  tan/khaki-olive body with dark brown mottling, dark brown-to-black dorsal
  sail edge, toothy jaw. **Primary/only reference for the animal's body and
  color.**
- `wookieepedia_egg.jpg` — Fanback egg/nest illustration: single large
  cream-white speckled egg in a sand/mud nest with dry grass. No adult
  animal visible; useful for habitat/nesting only, not coloration.
- **No donor-mod (`mlie.starwarsanimalcollection`) screenshot included** —
  confirmed absent from the current Steam Workshop page (checked directly,
  see Source URLs); the mod is not installed or vendored on this machine
  either.

## ruling
**RULED** (owner, 2026-09-14, review sheet): `wookieepedia_infobox.jpg`

> "But it's supposed to be olive green, not just brown. That's a sepia picture for some reason. Make it Olive colored."
