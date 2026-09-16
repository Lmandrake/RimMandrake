# B2-series super battle droid (repo chassis: B2, JDS + OuterRim)

**defName**: no single def — four defs across two donor mods.
- JDS: `RSW_DW_Race_JDSCIS_B2_Super_Battle_Droid` and
  `RSW_DW_Race_JDSCIS_B2_HA_Super_Battle_Droid` (ThingDefs, `Defs/Races_JDS.xml`, both
  `bodySize` 0.7), with PawnKindDefs `RSW_DW_JDSCIS_B2_Super_Battle_Droid` and
  `RSW_DW_JDSCIS_B2_HA_Super_Battle_Droid` (`Defs/PawnKinds_JDS.xml`).
- OuterRim: `RSW_DW_Race_OuterRim_SuperBattleDroid` (label "B2 Super Battle Droid",
  `Defs/Races_OuterRim.xml`); textures at
  `Textures/OuterRim/Droid/B2/Body/` — **body only, no `Head/` folder**, unlike the
  OuterRim B1/B1A/BX/Magnaguard which all have one. That is consistent with canon (a
  B2 has no separable head) but is worth knowing before anyone writes a head texture
  for it.
- Droids are **not xenotypes**; nothing here is in `RimMandrakeXenotypes.xml`.

## Canon variants this one chassis covers (6 rows in `DROIDS_INDEX.md`)

| canon row | what distinguishes it |
|---|---|
| B2-series super battle droid | the baseline; CIS heavy infantry |
| B2 buzzsaw droid | close-combat saw variant, CIS |
| B2 chainsaw droid | close-combat saw variant, CIS |
| B2 grapple droid | close-range variant despite the B2's firepower |
| B2 groundmech | **not a battle droid** — a Cybot Galactica groundmech used by the Andor family and the Ferrix resistance |
| B-2 series mercenary sentry droid | post-war sentry of the Droid Gotra / "The Twins" on Nal Hutta |

⚠️ **Index gap**: the repo ships a `B2_HA_Super_Battle_Droid` sprite and def, and canon
has a `B2-HA super battle droid` (a cannon-arm variant firing homing rockets, seen
commanding small units — *The Clone Wars*, "Bombad Jedi"), but `DROIDS_INDEX.md` does
**not** carry a B2-HA row marked in-repo. The repo's art is ahead of the index here.
Other canon B2 variants with no repo art at all: B2-RP (flight-capable), B2 super
rocket trooper, B2-ACM Trooper, and the **C-B3 cortosis battle droid** (fortified with
cortosis, resistant to blaster bolts *and* lightsabers).

## Sourced text (Wookieepedia)

The B2-series super battle droid is a **battle droid**, **class four / fourth degree**,
**1.93 meters tall** (6 ft 4 in), manufactured by **Baktoid Combat Automata**. Plating
is **dull silver**; sensor colours are black, white, and a **red chest light** (purple
under Scourge infection). Armament is a **dual wrist blaster** — one model carried a
wrist blaster only on the right forearm, another on both forearms; B2s were also
equipped with **wrist rockets** and a rapid-fire function.

B2s were **much stronger than their B1 predecessors** — strong enough to lift a clone
trooper off the ground — and, like the updated CIS B1s, **required no command system**,
giving them limited independence. The key improvement is a **thick armor casing that
contains their fragile sensors**. Against that, they were **designed with simple
processors**, limiting strategy formulation, so they **relied on organic commanders or
T-series tactical droids** to operate effectively.

Developed before the Clone Wars, the first batch went into action at the First Battle of
Geonosis; they could take more hits and stand up to enemies better than a B1, and saw
greater production after that battle. But a B2 **cost more than a B1**, and the cost
ratio meant there were **often one hundred B1s for every B2** on a battlefield. B2s
served to the end of the war — Outer Rim Sieges, Anaxes, Yerbana, and aboard Grievous's
*Invisible Hand* at the Battle of Coruscant — and **all B2 units were shut down** when
the Separatist Council was executed on Mustafar. Post-war they became **"extremely
rare"** (Neeku Vozo, *Resistance*, "The Mutiny"); individual survivors turn up among
scrappers and in pit fighting.

## Provenance

- **Manufacturer**: **Baktoid Combat Automata** (main line). Per-variant: **Cybot
  Galactica** for the B2 groundmech; blank for the buzzsaw, chainsaw and mercenary
  sentry rows; Baktoid Combat Automata *(Legends)* for the grapple droid.
- **Era**: **blank** — the `{{DroidSeries}}` infobox carries no firstmade/retired date
  for any of the six rows. In-text dates exist for events (first deployed at the First
  Battle of Geonosis; all units shut down at the end of the Clone Wars) but those are
  history, not an infobox era, and are recorded above as history rather than promoted
  into this field.
- **Typical owners**: Techno Union, Trade Federation, Confederacy of Independent Systems
  (Separatist Droid Army), Separatist holdouts, Bedlam Raiders, Plazir-15's government,
  Droid Gotra, "The Twins". The groundmech's owners are instead the **Andor family and
  the Ferrix resistance movement**.

## Visual brief

**The repo sprite reads correctly as a B2 and is clearly distinguishable from the B1 at
sprite scale.** `donor_current_sprite.png` (JDS, 128×128, top-down) shows a **grey**
mass whose widest feature is a pair of enormous armoured shoulder pauldrons, thick arms
folded down beside a segmented armoured torso, **no head visible as a separate shape**,
and small feet. A single **red dot** sits on the droid's shoulder — matching the canon
red sensor/chest light. Palette matches canon "dull silver".

- `wookieepedia_infobox.png` (front view, film-model render) is the authority. What it
  shows that the prose undersells: the **head is a small smooth dome sunk directly into
  the shoulder yoke with no neck at all**, the **chest is a single broad armoured
  carapace** over a dark exposed ribbed midsection, the **arms are enormous** —
  forearm diameter comparable to the B1's whole torso — and the **hips are a cluster of
  exposed piston/joint rings**, the only unarmoured part of the silhouette. A **red dot
  on the shoulder** is present in the render.
- 🔴 **Correction to the common description: the B2 is not shorter than a B1.** Both are
  **1.93 m**. In the reference render the B2's legs are long and comparatively slim, and
  the droid stands upright. "Squat" is a true impression but it comes entirely from
  **torso and shoulder mass plus the absent neck**, not from height. Anyone reskinning
  from a text prompt will get this wrong in the direction of a short stubby dwarf; the
  image says tall with a boxer's upper body.
- 🔴 **B1 versus B2 at 128 px**: the only two cues that survive are **shoulder width**
  and **whether a head protrudes**. The B1 has a long head that reads clearly past the
  shoulders and a narrow frame; the B2 has shoulders roughly twice the torso width and
  nothing projecting forward. The repo's two sprites already carry this contrast — do
  not "improve" either one in a way that erodes it.
- The **B2-HA** repo sprite (`JDSCIS_B2_HA_Super_Battle_Droid.png`, examined for this
  brief, not copied here) is the same silhouette with a **more detailed, angrier
  face-plate** picked out on the shoulder hump and the same red shoulder dot. It does
  not show the canon **cannon arm / homing-rocket launcher** that defines the B2-HA, so
  the variant currently reads as a paint-detail change rather than a weapon change.
- **No repo art exists** for the buzzsaw, chainsaw, grapple, groundmech or mercenary
  sentry variants, nor for the cortosis C-B3.


## Must show
- [ ] Grey ("dull silver") plating overall
- [ ] Enormous armoured shoulder pauldrons wider than the torso
- [ ] No head visible as a separate shape — head sunk directly into the shoulder yoke with no neck
- [ ] Thick arms, forearm diameter comparable to a B1's whole torso
- [ ] Red sensor dot on the shoulder

## Engine limits
none known

## Source URLs

- https://starwars.fandom.com/wiki/B2-series_super_battle_droid — main article; wikitext
  pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=B2-series_super_battle_droid&format=json&prop=wikitext`
  (rendered HTML is Cloudflare-walled, the API is not). Sections read: the
  `{{DroidSeries}}` infobox, the lead/description, History (The Clone Wars, Post-Clone
  Wars), and Specialized B2-series super battle droids. "Behind the scenes" and
  Appearances were **not** read.
- Per-variant rows and their URLs (infobox-derived, from `DROIDS_INDEX.md`; the
  individual articles were **not** separately fetched this pass):
  https://starwars.fandom.com/wiki/B-2_series_mercenary_sentry_droid ·
  https://starwars.fandom.com/wiki/B2_buzzsaw_droid ·
  https://starwars.fandom.com/wiki/B2_chainsaw_droid ·
  https://starwars.fandom.com/wiki/B2_grapple_droid ·
  https://starwars.fandom.com/wiki/B2_groundmech
- https://static.wikia.nocookie.net/starwars/images/7/7b/SuperBattleDroidDetail-SWE.png
  (File:SuperBattleDroidDetail-SWE.png → `wookieepedia_infobox.png`)

## Candidate images

- `wookieepedia_infobox.png` — the article's infobox image: a full-body front render of a
  standing B2 with its right arm raised and wrist blaster extended, on transparent
  background. The proportion authority: neckless dome head, huge shoulder yoke, ribbed
  exposed midsection, exposed hip joint rings, dull silver plating, red shoulder dot.
- `donor_current_sprite.png` — the repo's current JDS B2 super battle droid pawn sprite
  (`design/Jawa/fauna/sprites/JDSCIS_B2_Super_Battle_Droid.png`, 128×128, top-down).
  Live shipping art, not a corpse variant. The sibling
  `JDSCIS_B2_HA_Super_Battle_Droid.png` was also examined; see Visual brief.

## ruling

(empty — owner has not reviewed this chassis yet)
