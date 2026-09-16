# B1-A air battle droid (repo chassis: B1A, OuterRim)

**defName**: not a xenotype. Real defs on disk:
- `RSW_DW_Race_OuterRim_BattleDroidAdvanced` — label **"B1A Battle Droid"**, an
  `AlienRace.ThingDef_AlienRace` with `ParentName="DW_Family_Battle"`
  (`src/RimStarWars/Droidworks/Defs/Races_OuterRim.xml:113`). `baseBodySize` 1,
  `baseHealthScale` 0.8, `MoveSpeed` 4.2.
- `RSW_DW_HeadType_OuterRim_BattleDroidAdvanced` (the only entry in its `headTypes`).
- `RSW_DW_OuterRim_BattleDroidAdvanced` — PawnKindDef, label "B1A Battle Droid",
  `combatPower` 40, `forcedTraits` `ShootingAccuracy -1`
  (`src/RimStarWars/Droidworks/Defs/PawnKinds_OuterRim.xml:27`).

Sprites: `src/RimStarWars/Droidworks/Textures/OuterRim/Droid/B1A/Body/Naked_Male_{south,east,north}.png`
and `.../B1A/Head/Head_{south,east,north}.png`, each with a matching `*m.png` mask —
256×256, greyscale, tinted by the def's colour channels. **There is no
`design/Jawa/fauna/sprites/OuterRim_B1A*.png`** — this chassis is not in the contact-sheet
sprite folder, only in the mod's own Textures tree.

## Canon variants this one repo chassis covers

- **B1-A air battle droid** — the only canon row (`DROIDS_INDEX.md:283`). One canon model,
  one repo chassis; no grouping needed.

⚠️ **The index's continuity column is wrong for this row.** `DROIDS_INDEX.md:283` marks it
`canon`, but the article opens `{{Top|leg}}` and every internal link in it is a `/Legends`
link. This is a **Legends** droid — it first appeared in the 2005 *Revenge of the Sith*
video game and has no current-canon counterpart article.

⚠️ **Name trap.** The article carries `{{Youmay|...|the similarly named
[[D1-series aerial battle droid]]}}` — the **D1-series aerial battle droid** is a different
model. Do not merge them.

## Sourced text (Wookieepedia)

**B1-A air battle droids** were battle droids in the **Separatist Droid Army** that
"utilized **jetpacks** and a personal **shield**."
[B1-A air battle droid](https://starwars.fandom.com/wiki/B1-A_air_battle_droid)

Characteristics, all from that article:

- Their design "shared design characteristics with that of the **B1-Series battle droids**
  though were **more bulky in appearance in a similar vein as the B2 super battle droid**."
- Equipment: **two short blades**, **arm-mounted blasters**, and a **shield that could block
  lightsabers**.
- A **built-in repulsor pack** let them **hover on the battlefield**, giving "a high degree
  of mobility allowing them to either harass enemies from a distance or charge at them in
  close quarter combat."
- 🔑 **The canon weakness is the wings.** "There were high hopes for the design, but it was
  easy for clone troopers to shoot them down because they had a **weak spot on their wings**.
  If one was shot, then it lost control." So the wings are load-bearing to the design, not
  decoration — see the visual brief.
- Infobox fields: `line` = **B-series battle droid**, `class` = **Battle droid**,
  `cost` = **2,100 credits**, `sensor` = **Black**, `armament` = *two wrist-mounted blasters*
  and *two double-edged blades*, `affiliation` = **Confederacy of Independent Systems**.

History (sparse, two engagements only): units were aboard the *Invisible Hand* during the
**Battle of Coruscant** and were destroyed by Obi-Wan Kenobi and Anakin Skywalker during the
rescue of Chancellor Palpatine; more were present on **Utapau** against Kenobi.

**Unsourced and therefore absent:** height, mass, plating colour, `firstmade` / `retired`.
The infobox `manufacturer`, `creator`, `designer` and `homeworld` fields are all **empty** —
this droid has no recorded manufacturer, despite being a B-series derivative.

## Provenance

- **Manufacturer:** ⚠️ **none recorded.** The infobox `manufacturer`, `creator` and
  `designer` fields are literally empty, and `DROIDS_INDEX.md:283` likewise carries a blank
  manufacturer. Do **not** infer Baktoid Combat Automata from the B1 lineage — the article
  does not say it. The only sourced lineage claim is `line = B-series battle droid`.
  [B1-A air battle droid](https://starwars.fandom.com/wiki/B1-A_air_battle_droid)
- **Era:** **blank.** No `firstmade` or `retired` value in the infobox. The in-text history
  places its two appearances at the Battle of Coruscant and on Utapau — narrative placement,
  not an infobox era, and not promoted into this field.
- **Typical owners:** **Confederacy of Independent Systems**, specifically the **Separatist
  Droid Army**. That is the entire sourced owner list — one faction, no species, no world.
  [B1-A air battle droid](https://starwars.fandom.com/wiki/B1-A_air_battle_droid)

## Visual brief

🔴 **The repo colour is wrong, and it is wrong in a way that is one line to fix.** The def
tints this chassis **pale blue-grey over slate blue** — `skin` channel
`first = RGBA(146,148,172,255)`, `second = RGBA(65,107,127,255)`
(`Races_OuterRim.xml:145–160`). **Every canon image of the B1-A is tan/beige with
rust-orange accents.** For contrast, the *plain* B1 in the same file
(`RSW_DW_Race_OuterRim_BattleDroid`) is tinted `RGBA(239,228,176,255)` — a correct B1 tan.
So the repo already knows the right palette and the B1A simply does not use it. Canon does
give the B1-A a distinguishing colour treatment — **rust-orange panels over the tan**, most
visible on the shoulder yoke, wing leading edges and the weapon pod — so a straight copy of
the B1 tan would be the *near*-right answer; tan base plus orange accent is the right one.

🔴 **The wings are missing from the sprite entirely.** This is the bigger finding. The
concept art (`wookieepedia_concept_art.jpg`) makes the silhouette unmistakable: **two long
swept blade-like wings** projecting well past the shoulders, with the rear-view inset
showing **four glowing blue-white thruster nozzles** set in the wing roots. The article's
one stated weakness is the wing weak spot. The repo body sprite
(`donor_current_sprite.png`, the `south` body frame) shows **a plain rounded torso with
shoulder caps and no wings, no thrusters and no glow at all**. A top-down RimWorld pawn is
exactly the view in which swept wings would read best, so this is a real omission rather
than a format constraint.

**Where the images and the prose disagree, and which to trust:**

- The prose says **"jetpacks"** in the lead and **"repulsor pack"** in Characteristics.
  Neither image shows a back-mounted pack of the kind a clone trooper jetpack looks like —
  the concept art shows thrust integrated into the **wing roots**. Trust the images: this is
  a *winged* droid with wing-root thrusters, not a droid with a jetpack strapped on.
- The prose says **"more bulky … in a similar vein as the B2 super battle droid."** The
  infobox render (`wookieepedia_infobox.png`) does **not** support "B2-bulky": the limbs are
  as spindly as a B1's, and the bulk is concentrated in a **wide flared trapezoidal shoulder
  yoke** that sits above and around the head. The bulk is in the shoulders only. The repo
  sprite has neither the yoke nor the bulk.
- The infobox render shows the **arm-mounted blaster pod** on the droid's left forearm as a
  wedge housing with a **lit blue circular lens** and a barrel projecting forward — the one
  emissive detail on the whole model, and absent from the sprite.
- The **blades** are visible in the infobox render as a single very thin needle-like blade in
  the right hand; the concept art shows the same slim profile. They read as thin spikes, not
  broad swords, so "two double-edged blades" should be drawn thin.

**Head.** `donor_current_sprite_head.png` (the `Head_south` frame, 256×256) is a plain
elongated ovoid with **two small dark eye slits** — the classic B1 snout head, and a
*different asset* from the OuterRim B1's head (verified: different md5). The two dark eyes
do agree with the infobox's `sensor = Black`, which is one of the few things this chassis
gets right. But in both canon images the head is **recessed under the flared yoke** and is
not the widest part of the silhouette; in the sprite the head is a free-standing ovoid.

**Both sprite frames are greyscale/maskable** (there is a `Naked_Male_southm.png` /
`Head_southm.png` mask beside each), so judge them tinted with the def's two RGBA values,
never as the raw grey PNG.

`wookieepedia_invisible_hand.jpg` (259×194) is a low-resolution in-game frame from the
*Revenge of the Sith* game showing air battle droids fighting Kenobi and Skywalker aboard
the *Invisible Hand*. At that size it confirms only the **tan/orange palette and the
wings-out silhouette in the air**; it is not usable for detail. Note the frame also contains
a B2 grapple droid (the tall blue-grey figure at right), which is **not** a B1-A — do not
read its colour as this droid's.


## Must show
- [ ] Tan/beige base plating with rust-orange accent panels, not blue-grey/slate blue
- [ ] Two long swept blade-like wings projecting past the shoulders
- [ ] Four glowing blue-white thruster nozzles at the wing roots
- [ ] Wide flared trapezoidal shoulder yoke, with bulk concentrated in the shoulders rather than the limbs
- [ ] Arm-mounted blaster pod with a lit blue circular lens on the forearm
- [ ] Two small dark eye slits in an elongated ovoid head, recessed under the shoulder yoke

## Engine limits
none known

## Source URLs

- https://starwars.fandom.com/wiki/B1-A_air_battle_droid — main article; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=B1-A_air_battle_droid&format=json&prop=wikitext`
  (4,029 bytes of JSON, article read in full — no truncation). Rendered HTML is
  Cloudflare-walled; the API is not.
- https://static.wikia.nocookie.net/starwars/images/9/91/AirBattleDroid-ROTSVG.png
  (File:AirBattleDroid-ROTSVG.png) → `wookieepedia_infobox.png`
- https://static.wikia.nocookie.net/starwars/images/1/1c/DroidFlyer.jpg
  (File:DroidFlyer.jpg) → `wookieepedia_concept_art.jpg`
- https://static.wikia.nocookie.net/starwars/images/1/15/Droids_and_Jedi_on_Invisible_Hand.jpg
  (File:Droids_and_Jedi_on_Invisible_Hand.jpg) → `wookieepedia_invisible_hand.jpg`
- Named in the article but **not fetched this pass**:
  https://starwars.fandom.com/wiki/D1-series_aerial_battle_droid (the similarly-named
  different model), `B-series battle droid/Legends`, `B2 grapple droid/Legends`
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_OuterRim.xml`,
  `src/RimStarWars/Droidworks/Defs/PawnKinds_OuterRim.xml`

## Candidate images

- `wookieepedia_infobox.png` (665×918) — the article infobox render, full body,
  three-quarter, transparent background. **Tan/beige plating with rust-orange panels**, wide
  flared trapezoidal shoulder yoke over a recessed head, segmented ribbed abdomen, spindly
  double-jointed legs with three-toed feet, thin needle blade in the right hand, wedge
  blaster pod with a lit blue lens on the left forearm. **The primary colour and proportion
  authority.** Wings are not visible in this pose.
- `wookieepedia_concept_art.jpg` (640×880) — concept art plate, three views (hero
  three-quarter, front orthographic, rear orthographic). **The wing authority**: long swept
  blade wings and four blue-white thruster nozzles in the wing roots. Same tan-plus-orange
  palette. This is the single most useful image for correcting the sprite.
- `wookieepedia_invisible_hand.jpg` (259×194) — in-game frame, *Invisible Hand*. Low
  resolution; palette and airborne silhouette only. **Contains a B2 grapple droid too** —
  partial negative reference, do not read the blue-grey figure as a B1-A.
- `donor_current_sprite.png` (256×256) — repo body `south` frame
  (`Textures/OuterRim/Droid/B1A/Body/Naked_Male_south.png`, byte-identical). Greyscale /
  maskable; must be judged tinted with `RGBA(146,148,172)` / `RGBA(65,107,127)`. **No wings.**
- `donor_current_sprite_head.png` (256×256) — repo head `south` frame
  (`Textures/OuterRim/Droid/B1A/Head/Head_south.png`). Greyscale / maskable. Standard B1
  snout ovoid with two dark eye slits; no shoulder yoke.

## ruling

(empty — the owner has not reviewed this chassis yet)
