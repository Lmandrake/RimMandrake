# DSD1 dwarf spider droid (repo chassis: DSD1 dwarf spider, JDS)

**defName**: droids are not xenotypes. Real defs on disk:
- `RSW_DW_Race_JDSCIS_DSD1_Dwarf_Spider_Droid` — label "DSD1 Dwarf Spider Droid",
  `ParentName="DW_Family_Heavy"`, `baseBodySize` 0.7, `baseHealthScale` 1.5,
  `MoveSpeed` 1.7 (`src/RimStarWars/Droidworks/Defs/Races_JDS.xml:599`)
- `RSW_DW_JDSCIS_DSD1_Dwarf_Spider_Droid` — PawnKindDef, `combatPower` 99999, weapon
  `DSD1_Dwarf_Spider_Blaster` (`Defs/PawnKinds_JDS.xml:313`)
- `DroidworksExtension`: `chassisClass` 4, `energyDensity` 2, `powerFallPerDay` 1.0,
  `deliberateDenyModule` true; plus `CompProperties_DroidDetonation`
- Weapon ThingDef art: `src/RimStarWars/Armoury/Textures/Things/Weapons/DSD1_Dwarf_Spider_Blaster.png`

Sprites: `src/RimStarWars/Droidworks/Textures/JDS/Things/DSD1_Dwarf_Spider_Droid{,_north,_south,_east}.png`
— four 512×512 frames, graphic path `JDS/Things/DSD1_Dwarf_Spider_Droid`. **No
`colorChannels` block**, so unlike the OuterRim droids this sprite ships in the colour it
was drawn in and is judged as-is, not tinted.

## Canon variants this chassis covers

- **DSD1 dwarf spider droid** — a.k.a. simply *dwarf spider droid*, a.k.a. **burrowing
  spider droid** (`DROIDS_INDEX.md:572`, marked `canon (+Legends)`). One row, one chassis.

⚠️ **Not this chassis, despite the near-identical name**: `A-DSD advanced dwarf spider
droid` (`DROIDS_INDEX.md:169`) is a separate row with a different manufacturer (**Commerce
Guild Manufacturers**, not Baktoid) and **no repo art** — it is not served by this sprite
and is not covered here.

## Sourced text (Wookieepedia)

The **DSD1 dwarf spider droid**, or simply the **dwarf spider droid**, was a model of
**battle droid** manufactured by **Baktoid Armor Workshop**, favoured by the **Commerce
Guild**. It was **first used against renegade miners in skirmishes deep underground**, and
was also known as the **burrowing spider droid for its ability to invade narrow spaces**.
It later became a mainstay of the Separatist Droid Army through the Clone Wars.
[DSD1 dwarf spider droid](https://starwars.fandom.com/wiki/DSD1_dwarf_spider_droid)

Sourced hard numbers and appearance facts, all from that article:

- **1.98 meters tall** (6 ft 6 in), explicitly **excluding the antenna**.
- **3.05 meters wide.** 🔑 **It is half again as wide as it is tall** — the legs, not the
  body, are the dominant dimension.
- **Plating: gray.** **Sensor colour: red.** Photoreceptors **see into the infrared** and
  let it see in total darkness.
- Armament: **one nose-mounted laser cannon** — "centrally mounted heavy blaster cannon",
  capable of both rapid-fire and high-intensity burst — plus a **self-destruct mechanism**.
- Equipment: **two echolocation emitters**, **two infrared photoreceptors**, **one tracing
  antenna**.
- **Four legs**, "designed and manufactured to allow attachment and movement on vertical
  terrain, such as cliffs" — at the Battle of Teth they clung to the monastery cliff face
  to gain a firing angle. Good for guard duty and reconnaissance.
- **Masculine programming.** Programmed "about as smart as domestic animals" and as a
  result **would sometimes refuse to follow dangerous orders**.
- **Weak point: the underbelly.** Rex destroyed one by planting a thermal detonator on its
  stomach at Teth. Also vulnerable to attack from above.
- Used as an **anti-air** weapon (Teth; shot down the Bad Batch's LAAT at Anaxes). Clone
  slang for them, quoted in the article: **"We got spiders inbound!"** (Rex, Malastare).

## Provenance

- **Manufacturer:** **Baktoid Armor Workshop**
  ([article](https://starwars.fandom.com/wiki/DSD1_dwarf_spider_droid), infobox
  `manufacturer=`, cited to *Ultimate Star Wars*). `DROIDS_INDEX.md:572` agrees.
- **Era:** **blank.** The infobox's `firstmade=` and `retired=` fields are literally empty
  in the wikitext. In-text the model appears from *Attack of the Clones* through the Battle
  of Kashyyyk, but that is narrative and is not promoted into this field.
- **Typical owners:** **Commerce Guild** (and its **Punitive Security Forces**), **Trade
  Federation**, **Confederacy of Independent Systems** / **Separatist Droid Army** —
  infobox `affiliation=`, same article. The earliest sourced use is corporate suppression
  of **miners underground**, not front-line war, which is the most campaign-usable fact
  here: a scavenger clan on a mined-out desert world plausibly meets this droid as
  *abandoned mining-security hardware*, and that reading is sourced, not invented.

## Visual brief

**Overall shape and proportion — the whole read at sprite scale.** Canon is a **small
domed body slung between four long, wide-splayed, multi-jointed legs**, with a **needle
antenna** rising straight up from the dome and a **stubby cannon barrel** projecting
forward from the face. There is no torso and no head: the dome *is* the droid. At any
distance it reads as **a wide, low, four-pointed star with a dark ball in the middle** and
one thin vertical line above it.

**The repo sprite gets the features right and the proportion wrong.**

- ✅ **Colour agrees with canon.** The sprite is flat mid-grey with a heavy black outline
  and a brown-olive belly band; canon plating is sourced as **gray**. Note that
  `wookieepedia_infobox.jpg` (the Geonosis film frame) looks warm ochre-brown — that is
  **dust and sunset light on Geonosis, not the plating colour**; the text says gray and the
  concept plate `wookieepedia_from_above.jpg` shows dark grey-black plating with pale tan
  leg armour. Trust "gray"; the sprite is right.
- ✅ **The eye array is unusually faithful.** Canon shows **two large red photoreceptors in
  raised bezels, set wide on the dome, with a row of three small red lamps between them.**
  The sprite reproduces exactly this — two big red eyes plus three small red dots. At two
  or three pixels those five red points are the single strongest identity cue this droid
  has, and they survive.
- ✅ **The antenna is right and worth keeping long.** Canon height is measured *without*
  the antenna, so a tall thin spike above the dome is correct, and at sprite scale it is
  the second identity cue.
- ✅ **Self-destruct is a genuine def/canon match.** The article sources a self-destruct
  mechanism; the def carries `CompProperties_DroidDetonation`. Rare in this library —
  record it as agreement, not a finding.
- 🔴 **The legs are far too short and too tucked in.** Canon is **3.05 m wide against
  1.98 m tall** — the legs splay well clear of the body and the four long shins are most
  of the silhouette. The sprite's legs are short rounded stubs that barely clear the dome,
  making the droid read as roughly square, and at RimWorld scale as **a grey ball with
  bumps**. If one correction is made to this chassis, it is **extend and splay the legs**
  so the footprint is visibly ~1.5× the body width. This is the difference between reading
  as a spider and reading as a rock.
- ⚠️ **The nose cannon reads inconsistently between frames.** In `donor_current_sprite.png`
  (south) it is a dark wedge angled down-forward, roughly right. In
  `donor_current_sprite_east.png` it is a **long thin needle projecting horizontally**,
  longer than the body and easy to mistake for a second antenna; canon's cannon is short,
  thick and blunt. The east frame's barrel should be shortened and thickened.
- ⚠️ **Only two legs are visible in the east frame** — acceptable for a profile, but the
  canon profile shows the near pair and the far pair at different heights (the joint
  geometry is a broad flat thigh plate folding down to a thin shin), which would help the
  four-legged read from the side. The sprite's east legs are identical stubs.
- 🔴 **Scale contradiction in the def.** `baseBodySize` is **0.7** — smaller than a human
  (1.0). Canon is **1.98 m tall and 3.05 m wide**, i.e. taller than a person and with a
  footprint several times a person's. "Dwarf" in the name is relative to the full-size
  spider droid, not to a human. A DSD1 rendering smaller than a Jawa is wrong; report, do
  not fix. (`MoveSpeed` 1.7 is defensible — canon stresses climbing and guard duty, not
  speed.)
- **Nothing in the repo depicts the cliff-climbing pose**, the echolocation emitters, or
  the vulnerable underbelly. The first is the droid's most distinctive canon behaviour and
  there is no art for it.

## Must show
- [ ] Small domed body slung between four long, wide-splayed, multi-jointed legs
- [ ] Needle antenna rising straight up from the dome
- [ ] Stubby cannon barrel projecting forward from the face, short and blunt (not a long thin needle)
- [ ] Two large red photoreceptors in raised bezels plus a row of three small red lamps between them
- [ ] Gray plating
- [ ] Legs splayed to roughly 1.5× the body width, not tucked in as short stubs

## Engine limits
No `colorChannels` block — this sprite ships in the colour it was drawn in and cannot be tinted via the def; a colour correction would require a repaint.

## Source URLs

- https://starwars.fandom.com/wiki/DSD1_dwarf_spider_droid — main article; wikitext pulled
  via `https://starwars.fandom.com/api.php?action=parse&page=DSD1_dwarf_spider_droid&format=json&prop=wikitext`
  (11,250 bytes of JSON, read in full — no truncation). Sections read: `{{DroidSeries}}`
  infobox, lead, Characteristics. Appearances/Sources lists not treated as facts. The
  article carries a `{{Droid-stub}}` tag, so it is thin by the wiki's own admission.
- https://starwars.fandom.com/wiki/A-DSD_advanced_dwarf_spider_droid — **not fetched**;
  named here only to exclude it from this chassis.
- https://static.wikia.nocookie.net/starwars/images/3/3f/Dwarf_Spider_Dwarf.jpg →
  `wookieepedia_infobox.jpg` (960×960; Fandom served WebP, converted to JPEG locally)
- https://static.wikia.nocookie.net/starwars/images/7/70/TakeThatClankers-SWQ21.png →
  `wookieepedia_from_above.jpg` (2000×1852; served WebP, converted to JPEG. **Do not view
  at full size** — 2000 px is at the hard limit; view a downscaled copy.)
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_JDS.xml`,
  `src/RimStarWars/Droidworks/Defs/PawnKinds_JDS.xml`
- Index row: `design/RimStarWars/canon_references/DROIDS_INDEX.md:572`

## Candidate images

- `wookieepedia_infobox.jpg` (960×960) — the article infobox: a dwarf spider droid striding
  across Geonosis, three-quarter front, battle droid ranks behind. **The proportion
  authority**: dome body, four long splayed multi-jointed legs, needle antenna, two large
  red bezelled photoreceptors plus three small red lamps, stubby nose cannon. Warm ochre
  cast is Geonosis dust and light, **not** the plating colour.
- `wookieepedia_from_above.jpg` (2000×1852) — concept/cover plate of Captain Rex destroying
  one from above. Best reference for **plating colour without the dust wash** (dark
  grey-black body, pale tan leg armour) and for the single large red eye read at an angle.
  Also illustrates the sourced "vulnerable from above" weakness.
- `donor_current_sprite.png` (512×512) — repo `DSD1_Dwarf_Spider_Droid_south`, top-down.
  What the repo actually ships. Eyes and antenna faithful; legs too short.
- `donor_current_sprite_east.png` (512×512) — repo `..._east` profile. Shows the
  over-long needle barrel and the two-identical-stub leg problem.

## ruling

(empty — the owner has not reviewed this chassis yet)
