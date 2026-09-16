# K-X12 probe droid (repo chassis: K-X12 probe, KotOR)

**defName**: not a xenotype. **One canon model, split into two races on disk** — both share
the *same* graphic set:
- `RSW_DW_Race_guy762_DroidRace_KX12UPD` — label **"K-X12 utility probe droid"**,
  `ParentName="DW_Family_Probe"`, `baseHealthScale` 0.6, `MoveSpeed` 3
  (`src/RimStarWars/Droidworks/Defs/Races_KotOR.xml:450`)
- `RSW_DW_Race_guy762_DroidRace_KX12APD` — label **"K-X12 assassin probe droid"**,
  `baseHealthScale` 0.8, `MoveSpeed` 3 (same file, :507)
- Both use `headTypes` = `RSW_DW_HeadType_Blank` (no head asset — the whole droid is the
  body sprite) and both carry
  `RimMandrake.StarWars.Droidworks.CompProperties_DroidDetonation`.

PawnKindDefs (`src/RimStarWars/Droidworks/Defs/PawnKinds_KotOR.xml`):
`RSW_DW_KotORDroidColonist_KX12UPD` (:123), `RSW_DW_KotORDroidColonist_KX12APD` (:142),
`RSW_DW_KotORDroidGood_KX12UPD` (:581), `RSW_DW_KotORDroidBad_KX12UPD` (:686),
`RSW_DW_KotORDroidBad_KX12APD` (:740), `RSW_DW_KotORDroidBad_KX12APD_sapper` (:768).

Sprites: `src/RimStarWars/Droidworks/Textures/KotOR/Droid/KX12/KX12_{south,east,north}.png`
with `KX12_mask_{south,east,north}.png` — 512×512, greyscale, two-channel masked. **There is
no `design/Jawa/fauna/sprites/` file for this chassis**; it exists only in the mod's own
Textures tree.

Also referenced in a design comment at
`src/RimStarWars/Droidworks/Defs/Races_Primitive.xml:176` ("Gonk/KX-12 nature raise
density") — tuning precedent, not a def for this chassis.

## Canon variants this one repo chassis covers

- **K-X12 probe droid** — the only canon row (`DROIDS_INDEX.md:967`).

🔑 **The repo's two-race split is canon-defensible, not an invention.** The article
explicitly says the K-X12 "could be adapted to play many roles… allowed it to act as a
security droid, a patrol droid, a medical droid, a hunting droid, a **utility droid** or a
**battle droid**." So one canon chassis serving both a utility and a combat role is exactly
what the source describes. There is no separate canon "assassin probe droid" article.

⚠️ **The index's continuity column is wrong for this row.** `DROIDS_INDEX.md:967` marks it
`canon`; the article opens `{{Top|leg}}` and every internal link is a `/Legends` link. This
is a **Legends** droid, from *Knights of the Old Republic* I and II. No current-canon
counterpart article exists.

⚠️ **Title/spelling trap.** The article is titled **"K-X12 probe droid"** but its own lead
sentence calls it the **"MerenData KX-12 probe droid"** — unhyphenated. Both spellings are
the article's own; the repo's `KX12` matches the lead.

## Sourced text (Wookieepedia)

The **MerenData KX-12 probe droid** was a **multi-function droid model commonly used around
3956 BBY and 3951 BBY.** "Billed as a probe droid by its manufacturer, it gained popularity
for its **adaptability**."
[K-X12 probe droid](https://starwars.fandom.com/wiki/K-X12_probe_droid)

Physical description, verbatim from the article: "It was a **nonhumanoid** model equipped
with a **red photoreceptor**, **three multi-jointed appendages equipped with claw graspers**,
a **blaster**, and a **repulsorlift**." Infobox: `height` **1 meter**, `cost` **6,000
credits**, `sensor` **Red**, `equipment` = *Claw graspers*, *Blaster*, *Repulsorlift*.

🔑 **The blaster is officially a lie.** "MerenData maintained the **blaster appendage was
designed to clear debris**, but its firepower, in conjunction with its ability to **hover
into dangerous locations**, allowed it to act as a security droid, a patrol droid, a medical
droid, a hunting droid, a utility droid or a battle droid." A civilian-rated tool that is
actually a weapon is the sourced character of this droid.

Deployment and reuse, all from the article:

- "Many KX-12s were later **reprogrammed and sent on espionage missions.** They could be
  **loaded into hollowed shells and fired at an enemy planet**, detonating the shell before
  impact and **using its repulsors to brake** to avoid destruction on impact with the
  surface." — an orbital-insertion delivery method, and the closest thing the article gives
  to a "drop pod" arrival.
- Used as **security droids** in the **Peragus Mining Facility**, in **Khoonda**, and on
  **Tatooine**.
- 🔑 **`G0-T0` ("Goto") reprogrammed one to serve as a torture droid on his yacht** (the
  *Visionary*), and **Davik Kang also used the droid as a torture droid.** The repo already
  carries a `droid_g0t0` entry — this is a direct, sourced link between two chassis in this
  library.

**Unsourced and therefore absent:** mass, plating colour, `firstmade` / `retired`,
`affiliation` (the infobox field is empty — this droid has **no recorded faction owner**),
`class`, `degree`, `homeworld`, `line`, `model`.

## Provenance

- **Manufacturer:** **MerenData** — stated in the infobox and repeated twice in the body,
  including MerenData's own claim about the blaster appendage. `DROIDS_INDEX.md:967` agrees.
  [K-X12 probe droid](https://starwars.fandom.com/wiki/K-X12_probe_droid)
- **Era:** **blank.** No `firstmade` or `retired` value in the infobox. The article's body
  does give **3956 BBY and 3951 BBY** as when the model was "commonly used" — that is a
  narrative usage window, cited here rather than promoted into the era field.
- **Typical owners:** ⚠️ **the infobox `affiliation` field is empty and
  `DROIDS_INDEX.md:967` carries a blank owners column.** No faction owns this droid. What the
  article does name are *individual and site* users: the **Peragus Mining Facility**,
  **Khoonda** (Dantooine), **Tatooine**, **G0-T0** aboard the *Visionary*, and **Davik
  Kang** (Taris crime lord). That pattern — bought by whoever, repurposed by whoever — is
  itself the sourced answer, and fits a scavenger campaign better than a faction droid would.
  [K-X12 probe droid](https://starwars.fandom.com/wiki/K-X12_probe_droid)

## Visual brief

**This is the best canon-to-sprite match of the five chassis in this batch. The silhouette
is right.** Canon (`wookieepedia_kx12_infobox.jpg`) is a **hovering, legless droid**: a
smooth **tapered inverted-cone body**, widest at the top and narrowing to a point at the
bottom, with **three long, thin, multi-jointed arms** radiating outward and ending in
**pointed claw graspers**, plus a **small barrel projecting from the bottom tip** (the
"blaster appendage"). The repo `south` sprite reproduces all of it: the tapered cone body,
two arms spread left and right, the third arm angled back/up behind the body, and the barrel
at the bottom point.

**Judge the sprite tinted, never as the raw grey PNG.** `KX12_mask_south.png` is a
two-channel mask: **red covers the whole body and arms** (the `skin` `first` channel) and
**green covers four small round lens spots on the lower body** (the `second` channel). Those
four green dots are the photoreceptor/lens cluster, and they are the only thing the second
colour drives.

- ✅ **`RSW_DW_Race_guy762_DroidRace_KX12UPD` is correct.** `first` =
  `RGBA(180,190,185,255)` — a pale neutral grey-green, close enough to the canon image's
  polished chrome-silver body — and `second` = **`RGBA(255,0,0,255)`, pure red**, matching
  the infobox's `sensor = Red` and the red lenses in the image exactly.
- 🔴 **`RSW_DW_Race_guy762_DroidRace_KX12APD` renders its photoreceptors MAGENTA.** Its
  `second` channel is **`RGBA(255,0,255,255)`** (`Races_KotOR.xml:541–549`). Canon `sensor`
  is **Red**, and the canon image's lenses are red. Magenta photoreceptors on the assassin
  variant are a **def-versus-canon contradiction**, and it looks like a deliberate
  "sinister variant" recolour rather than a typo — but there is nothing in the article
  supporting a colour other than red for any K-X12. Its `first` channel,
  `RGBA(85,85,90,255)` (dark gunmetal), is also a departure from the canon chrome, though a
  darkened chassis for a covert unit is at least a defensible authored choice; the magenta
  eye is not.
- ⚠️ **The canon body is brighter and more reflective than either def channel.** The infobox
  render is **bright polished chrome with strong specular highlights** — it reads almost
  mirror-like. Both repo tints are matte. If a correction is wanted beyond the magenta, it
  is raising the utility variant's brightness toward chrome.
- **No repulsorlift cue exists in the sprite.** Canon is unambiguous that this droid
  **hovers** — no legs, repulsorlift in the infobox equipment list, "hover into dangerous
  locations" in the body text. The sprite's arms hang downward in a way that reads
  correctly as suspended, so this is arguably already handled by silhouette alone, but there
  is no shadow, glow or thruster treatment marking it as airborne.
- **Arm count is right but arm *placement* differs slightly.** In the canon render the three
  arms emerge from the **top rim** of the cone and sweep outward and down. In the sprite the
  two side arms emerge from the top rim (correct) while the third reads as emerging from
  behind the body and pointing *up*. At RimWorld's top-down angle that is a reasonable
  projection of the same geometry, not an error.

## Must show
- [ ] Tapered inverted-cone body, hovering and legless, narrowing to a point at the bottom
- [ ] Three long, multi-jointed arms radiating outward from the top rim, ending in pointed claw graspers
- [ ] Small barrel/blaster appendage projecting from the bottom tip
- [ ] Pale neutral grey-green (chrome-silver) body with red photoreceptor lens dots

## Engine limits
none known

## Source URLs

- https://starwars.fandom.com/wiki/K-X12_probe_droid — main article; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=K-X12_probe_droid&format=json&prop=wikitext`
  (2,636 bytes of JSON, article read in full — no truncation). Rendered HTML is
  Cloudflare-walled; the API is not.
- https://static.wikia.nocookie.net/starwars/images/7/7c/Drdprobe.jpg
  (File:Drdprobe.jpg, 480×480) → `wookieepedia_kx12_infobox.jpg`
- ⚠️ **This is the article's only image.** `{{Mediacat|imagecat=Images of K-X12 probe
  droids}}` implies a category with more, but the article body embeds none — so there is **no
  second angle, no in-game scene shot and no scale reference** available from the article
  itself. A further image hunt is owed if the owner wants the `east`/`north` frames judged
  against canon.
- Named in the article but **not fetched this pass**:
  https://starwars.fandom.com/wiki/G0-T0 (the torture-droid reprogrammer),
  https://starwars.fandom.com/wiki/Davik_Kang, `Peragus Mining Facility`, `Khoonda`
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_KotOR.xml`,
  `src/RimStarWars/Droidworks/Defs/PawnKinds_KotOR.xml`

## Candidate images

- `wookieepedia_kx12_infobox.jpg` (480×480) — the article's sole image and its infobox
  render: three-quarter view of the hovering droid on a flat grey background. **Bright
  polished chrome** tapered cone body, **three long spindly multi-jointed arms with pointed
  claw tips**, **red lens spots** on the lower body (one large, two small), small barrel at
  the bottom tip. **The colour, proportion and lens-count authority.**
- `donor_current_sprite.png` (512×512) — repo `south` frame
  (`Textures/KotOR/Droid/KX12/KX12_south.png`, byte-identical). Greyscale / two-channel
  masked; must be judged tinted. Shared by **both** the utility and assassin races, so the
  only thing distinguishing them on screen is the colour channels — which is why the magenta
  finding matters.

## ruling

(empty — the owner has not reviewed this chassis yet)
