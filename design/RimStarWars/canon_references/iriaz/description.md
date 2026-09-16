# Iriaz

**defName**: `RSW_Iriaz` (vendored in this repo's own `src/RimStarWars/SWBestiary` mod)

## Sourced text (Wookieepedia)
**Important provenance note**: Iriaz is a *Star Wars Legends* (old expanded
universe) creature, not current Disney canon — its only real appearance is as
a cut/unused creature model from *Star Wars: Knights of the Old Republic*
(2003); it's referenced only in unseen dialogue in the shipped game ("Murdered
Settler" quest) about a hunter who claimed to be out hunting iriaz. All
Wookieepedia material on it is Legends-tagged. Iriaz were docile, herbivorous,
horned herd animals native to the grassland planet Dantooine, grazing on
grasses, berries, and shoots near the Jedi Enclave. Not normally aggressive,
but capable of charging with their horns if provoked; capable of short
tremendous bursts of speed to flee predators such as kath hounds, though this
left them winded. Rarely encountered alone — a lone iriaz was usually sick,
old, injured, or a rogue male. Hunted heavily by locals for their pelts and
horns, which fetched a high market price; a crime lord (Davik Kang) had a
mounted iriaz head as a trophy.

## Visual brief
Only two images exist for this creature, both drawn from the same cut
KOTOR asset: promotional card art and an in-engine screenshot of the unused
model. They agree closely with each other. Iriaz reads as a **long-necked,
antelope/giraffe-proportioned quadruped** — thin legs, a long slender neck,
and a horse-or-goat-like head — with a base skin color of **muted
green/olive-teal**, overlaid with **leopard-style orange-yellow spotted
markings** scattered across the neck, shoulders and flank. It carries a
single long, ridged, backward-curving horn sweeping up from the top of the
head (the card art shows what could read as a pair, but the in-game model
clearly shows one prominent ridged horn). The tail is thin and whip-like,
feet appear clawed rather than hooved. No fur is visible — smooth,
reptilian-adjacent hide despite being classed a "creature" rather than
explicitly scaled.

**The current donor sprite (`donor_current_sprite.png`) is a genuinely close
match** — it already uses a green/olive body with yellow-orange spotted
markings, a pair of curved horns, and a long neck, which lines up with both
reference images far better than most other creatures in this library. The
donor's silhouette is more compact/rounded (a coiled sitting pose vs. the
references' standing long-legged pose) and gives it two horns rather than the
one clearly dominant horn in the in-game model, but the palette and marking
pattern are already correct — this is the strongest existing donor-vs-canon
agreement found in this pass.

## Must show
- [ ] Long-necked, antelope/giraffe-proportioned quadruped body with thin legs
- [ ] Base skin colour is muted green/olive-teal
- [ ] Leopard-style orange-yellow spotted markings scattered across neck, shoulders and flank
- [ ] A single long, ridged, backward-curving horn (the in-game model shows one dominant horn, not a pair)
- [ ] Thin, whip-like tail
- [ ] Smooth hide with no visible fur

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Iriaz/Legends (Wookieepedia article text,
  pulled via
  `starwars.fandom.com/api.php?action=parse&page=Iriaz&prop=wikitext`,
  2026-09-13 — the base "Iriaz" title itself redirects/serves the Legends
  article, confirming no current-canon version exists)
- https://static.wikia.nocookie.net/starwars/images/b/bd/WotC_Iriaz.jpg (Wizards of the Coast promotional card/concept art, "Creatures of KOTOR 2" article)
- https://static.wikia.nocookie.net/starwars/images/8/8d/Iriaz.jpg (in-engine screenshot of the cut KOTOR creature model, standing in grassland)

## Candidate images
- `donor_current_sprite.png` — this repo's current shipped sprite (SWBestiary mod, `Iriaz_east` base variant), green/olive body with orange-yellow spots and a pair of curved horns
- `wookieepedia_wotc_card.jpg` — Wizards of the Coast promotional/card art, full body, green-teal skin with orange leopard-spot markings, single dominant ridged horn
- `wookieepedia_cutmodel.jpg` — in-engine screenshot of the unused KOTOR 3D model standing in a grassy canyon, confirms the same coloring and long-necked antelope body plan from a different angle

## ruling
(empty — owner has not reviewed this creature yet)
