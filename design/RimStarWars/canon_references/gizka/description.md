# Gizka

**defName**: `RSW_Gizka` (vendored in this repo's SWBestiary mod)

## Sourced text (Wookieepedia — Legends is the substantial article; the
current-canon "Gizka" page is a one-line stub)
Gizka were small reptiles found across the galaxy, on planets including
Lehon and Manaan, though their true homeworld is unconfirmed — speculated
to be Lehon, spreading via the wreckage of crashed starships during the era
of the Infinite Empire. Infobox: green skin color, omnivorous diet, and
their single defining trait is an extraordinary reproduction rate — they
bred explosively fast, to the point of being considered pests on nearly
every world they reached, commonly infesting starship wiring and
insulation and squeezing into openings to nest inside bulkheads. Gizka meat
had a "universal flavor" prized as a delicacy (gizka steak); some
carnivorous species such as Trandoshans reportedly thought everything
tasted like gizka. Every attempt at domesticating them failed, since they
always escaped or chewed through vital electronics looking for food. Their
best-known appearance is the *Star Wars: Knights of the Old Republic*
(2003) "Trouble with Gizka" side content aboard the *Ebon Hawk*, where a
cargo mishandling incident leaves the player fighting a rapidly-multiplying
gizka infestation cleared with "Gizka poison" pellets — a deliberate homage
to the *Star Trek: TOS* episode "The Trouble with Tribbles." First
mentioned in current Disney canon only much later, in the 2017 novel
*Aftermath: Empire's End*.

## Visual brief
Judged against the owner's two supplied reference images
(`owner_reference_sideview.jpg`, `owner_reference_card.jpg`, both of the
KOTOR in-game model — owner ruling below). Gizka is a **small bipedal
DINOSAUR-like reptile, emphatically not a frog or toad**: a compact
theropod build with the **body held horizontal** over two strong hind
legs, and a **thick tapering tail extending behind for balance** — the
tail is prominent in both references and is part of the silhouette. Small
vestigial forelimbs are held tucked against the chest, never
weight-bearing. The **head** is oversized relative to the body with a
**rounded, blunt, beak-like snout**, broad fleshy cheeks, a downturned
mouth, and a **backswept crest at the rear of the skull**. **TWO
modest-sized eyes sit on the sides of the head** — never a single central
cyclops eye, and never huge bulging frog eyes dominating the face; a
front (south) view shows both. Hide is **scaly and mottled in tan, warm
orange-brown and olive patches** (the side-view reference reads warm
tan-orange; the card reads greener) — never a flat colour — with paler
skin at the belly and joints. `kotor_screenshot.jpg` shows two gizka in
the *Ebon Hawk* cargo hold, confirming pack/infestation behavior and a
size reference — roughly knee-height or smaller, a fast-breeding
vermin-scale creature rather than a large animal.

No donor mod screenshot could be obtained — `mlie.starwarsanimalcollection`
is not present anywhere on this machine's disk (Workshop cache or common
Mods folder), so there is no `donor_current_sprite.png` candidate for this
entry.

## Must show
- [ ] Small bipedal dinosaur-like reptile — theropod build, body held HORIZONTAL over two strong hind legs; NOT a frog, NOT a toad, NOT an upright hopper
- [ ] A thick tapering TAIL extending behind for balance — part of the silhouette in every facing
- [ ] Tiny vestigial forelimbs tucked against the chest, never weight-bearing
- [ ] Oversized head with a rounded, blunt, beak-like snout, broad cheeks and a backswept crest at the rear of the skull
- [ ] TWO modest-sized eyes on the sides of the head — a front (south) view shows both; never a single central cyclops eye, never huge bulging frog eyes
- [ ] Scaly mottled hide in tan, warm orange-brown and olive patches — not a flat colour
- [ ] Roughly knee-height or smaller — a vermin-scale creature, not a large animal

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Gizka (current-canon stub article;
  pulled via
  `starwars.fandom.com/api.php?action=parse&page=Gizka&prop=wikitext`,
  2026-09-13 — one paragraph, no visual/biological detail)
- https://starwars.fandom.com/wiki/Gizka/Legends (the substantial Legends
  article this entry is sourced from; pulled via
  `starwars.fandom.com/api.php?action=parse&page=Gizka/Legends&prop=wikitext`,
  2026-09-13)
- https://static.wikia.nocookie.net/starwars/images/b/b8/Onegizka.jpg
  (species infobox image, in-game 3D render, close head/body view)
- https://static.wikia.nocookie.net/starwars/images/9/98/CreepyFaceGizka-WotC.jpg
  (Wizards of the Coast concept-art-style painted rendering of the model)
- https://static.wikia.nocookie.net/starwars/images/0/0a/GIZKA.jpg (in-game
  screenshot, two gizka aboard the Ebon Hawk cargo hold)

## Candidate images
- `owner_reference_sideview.jpg` — 🔴 the owner's supplied reference (2026-09-16),
  side view of the KOTOR model: horizontal dinosaur posture, counterbalancing
  tail, beak-like snout, backswept skull crest, small side-set eye, warm
  tan-orange mottled hide. THE authority for body plan and silhouette.
- `owner_reference_card.jpg` — the owner's second supplied reference, 3/4
  front view of the same model in grass: confirms the crest, the beaked
  snout, both eyes, and the green/tan/orange mottle
- `wookieepedia_infobox.jpg` — species infobox render, close head/body view
- `wookieepedia_concept_art.jpg` — painted rendering of the same model
- `kotor_screenshot.jpg` — in-game screenshot of two gizka in the *Ebon
  Hawk* cargo hold ("Trouble with Gizka"), confirms pack behavior and
  gives a small vermin-scale size reference

## ruling
2026-09-16, owner: "Check your canon. I see clear references to bipedal and no
mention of four legs. I think this is a canon error in your search." Upheld on
re-inspection: the background gizka in kotor_screenshot.jpg stands wholly on
its two hind legs, forelimbs raised; the infobox render's thin forelimbs are
not weight-bearing. The earlier Visual brief's "quadruped in a sprawling
stance" was a misread of the foreground close-up and is superseded by the
Must-show line above. Gizka renders BIPEDAL: two working hind legs, vestigial
raised forelimbs.

2026-09-16, owner (giz art review): gizka has TWO eyes. The south-facing
review renders showed a single central cyclops eye — that came from this
entry's own earlier "reads almost one-eyed/cyclopean" phrasing, which the
image model took literally on the front view; the phrasing is removed and the
brief now states two eyes, one per side, both visible from the front. Same
sitting: east-facing versions came out too top-down — east/west must be side
profiles, now enforced in the daemon's facing hook (artpiped.py).

2026-09-16, owner, on the v4 biped renders, supplying two KOTOR reference
images: "Use these as gizka references. You just made a frog. I don't want a
frog." The frog/toad reading is DEAD: gizka is a small dinosaur-like biped —
horizontal body, counterbalancing tail, beaked snout, backswept skull crest,
modest side-set eyes. The Visual brief and Must show are rewritten against
his two images (`owner_reference_sideview.jpg`, `owner_reference_card.jpg`),
which outrank the wookieepedia thumbnails wherever they disagree.
