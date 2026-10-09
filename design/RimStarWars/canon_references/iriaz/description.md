# Iriaz

**defName**: `RSW_Iriaz` (vendored in this repo's own `src/RimStarWars/SWBestiary` mod)

## Sourced text (Wookieepedia)
**Important provenance note**: Iriaz is a *Star Wars Legends* (old expanded
universe) creature, not current Disney canon — it was intended to appear in *Star Wars:
Knights of the Old Republic* (2003) but the living creature was cut. The
shipped game still has the "Murdered Settler" quest dialogue (a suspect
claims to be out hunting iriaz) and Davik Kang's mounted iriaz head in his
Taris estate trophy room; the Wookieepedia appearance list marks KOTOR as
"Head only". Mods can restore the dormant model. All
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
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."**

**Animation-only canon — no realistic source found (searched: Wookieepedia `Iriaz/Legends` page images; the creature is a cut *Knights of the Old Republic* asset with only a Wizards of the Coast card painting and an in-engine model screenshot).** The images below are animated/stylised; render this creature realistically anyway — real-world anatomy, materials and lighting, not the cartoon's flat shading or exaggerated proportions. Both images stay (they are the owner's "canon imagery" in his 2026-10-04 ruling below). Think of a real antelope/gerenuk-proportioned animal with smooth, finely textured greenish hide, real pigment spots, ridged keratin horns and natural light — not the card's airbrushed gloss or the game model's low-poly texture.

Only two images exist for this creature, both drawn from the same cut
KOTOR asset: promotional card art and an in-engine screenshot of the unused
model. They agree closely with each other. Iriaz reads as a **long-necked,
antelope/giraffe-proportioned quadruped** — thin legs, a long slender neck,
and a horse-or-goat-like head — with a base skin color of **muted
green/olive-teal**, overlaid with **leopard-style orange-yellow spotted
markings** scattered across the neck, shoulders and flank. It carries a
pair of long, ridged, backward-curving horns sweeping up from the top of the
head, as the card art shows (the in-game model reads as one prominent horn;
the owner ruled for two on 2026-10-04). The tail is thin and whip-like,
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
*Rewritten 2026-10-09 to the canon_check leniency lesson (`Transient/canon_check_leniency_2026-10-09.md`): body plan, colour layout and a negative, each checkable on a 256px sprite. Grounded in both images and the `## ruling` below.*
- [ ] BODY PLAN: a tall, lean, standing four-legged browser: legs long and thin (leg length at least equal to body depth), a long slender neck rising steeply so the head sits well above the back, a narrow body with a visible tucked waist, and a thin whip tail ending in a small tuft
- [ ] Horns: exactly two long, ridged, dark horns rising from the top of the head and sweeping BACKWARD in a curve over the neck (owner ruling 2026-10-04: "Four legs, two horns, greenish")
- [ ] COLOUR LAYOUT: muted green/olive-teal base all over; orange-yellow leopard-like spots concentrated along the top of the neck, shoulders and back, fading out toward the belly and lower legs; horns dark brown, darker than the hide
- [ ] Long narrow horse/goat-like head with a blunt muzzle carried forward at the top of the neck
- [ ] Feet end in pale claws, not hooves
- [ ] Smooth fine hide with no visible fur
- [ ] Realistic rendering: natural finely textured hide, keratin horns and lighting, no outlines, no airbrushed or low-poly game look
- [ ] NEGATIVE: not a horse, deer or goat (no fur coat, no hooves, no antlers), not one single horn, not a short-legged or stocky animal

## Engine limits
- Spots confined to the neck/shoulder/back over a plain green base is a per-region pattern: needs art, not a tint value.

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
- `wookieepedia_wotc_card.jpg` — STYLISED ILLUSTRATION, Wizards of the Coast promotional/card art, full body, green-teal skin with orange leopard-spot markings, single dominant ridged horn
- `wookieepedia_cutmodel.jpg` — GAME (stylised 2003 engine) in-engine screenshot of the unused KOTOR 3D model standing in a grassy canyon, confirms the same coloring and long-necked antelope body plan from a different angle

## ruling
**Antelope — canon identity stands.** Owner, 2026-09-18: *"antelope and close,
this is acceptance"* (on PYRELANDS_CREATURE_RERENDER_1's acceptance). The
four-legged Dantooine grassland quadruped described above IS the identity;
the shipped painterly v2 set was drawn from this entry and the owner locked
that specific art 2026-09-17 (*"Lock in that Iriaz."* — one horn, the second
protrusion confirmed as an ear). A "two-legged Dathomir" alternative was
flagged once (2026-09-14) and investigated on IRIAZ_ART_REGEN_1: it matches
nothing in this repo and is dead — do not re-render against it.

**Two horns — REDO** (owner, 2026-10-04, doubles sheet `Transient/art_doubles_compare_2026-10-04.decisions.json`, item ART_VERSION_WRANGLING_1), superseding the 2026-09-17 one-horn lock:

> "Use canon imagery. Four legs, two horns, greenish. Try again. B is almost good except for one horn."

(B = the shipped `IriazArtOverride` set, the one-horn art locked 2026-09-17.)
