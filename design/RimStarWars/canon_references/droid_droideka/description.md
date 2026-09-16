# Droideka / destroyer droid (repo chassis: Droideka + Sharpshooter, JDS + OuterRim)

**defName**: no single def — three defs across two donor mods.
- JDS: `RSW_DW_Race_JDSCIS_Droideka_Droid` and
  `RSW_DW_Race_JDSCIS_Droideka_Sharpshooter_Droid` (ThingDefs, `Defs/Races_JDS.xml`,
  both `baseHealthScale` 1.5), with PawnKindDefs `RSW_DW_JDSCIS_Droideka_Droid` and
  `RSW_DW_JDSCIS_Droideka_Sharpshooter_Droid` (`Defs/PawnKinds_JDS.xml`).
- OuterRim: `RSW_DW_Race_OuterRim_DestroyerDroid`, **label "Destroyer Droid"**
  (`Defs/Races_OuterRim.xml`, `bodySize` 1.0), graphic path
  `OuterRim/Droid/Droideka/Droideka` — a single 256×256 four-direction graphic set, **not**
  a Body/Head pawn rig like the OuterRim B1/B2/BX/Magnaguard. "Destroyer droid" is a real
  canon synonym for droideka, so the label is correct, not a mistake; but a name search
  for "Droideka" in the OuterRim defs finds only the texture path, not the defName.
- Droids are **not xenotypes**; nothing here is in `RimMandrakeXenotypes.xml`.

## Canon variants this one chassis covers (11 rows in `DROIDS_INDEX.md`)

| canon row | continuity | what distinguishes it |
|---|---|---|
| Droideka | canon (+Legends) | the baseline; Colicoid Creation Nest |
| Droideka Sharpshooter | canon | long-barrel heavy blaster rifle; **1.87 m**, bronzium, red photoreceptors |
| Droideka Mark II | canon | Phlac-Arphocc design, built by Zann Consortium Droid Works |
| Droideka Oppressor | canon | used by **both** the Rebel Alliance and the Galactic Empire |
| Droideka Sentinel | canon | likewise Alliance and Empire |
| Grapple droideka | canon | Colicoid-built, Trade Federation |
| P-series droideka | canon (+Legends) | Colicoid Creation Nest; Trade Federation / CIS |
| Q-series droideka | canon (+Legends) | Colicoid Creation Nest; CIS |
| W-series droideka | **Legends** | Phlac-Arphocc Automata Industries |
| Sniper droideka | **Legends** | Colicoid-built; CIS |
| Ultra Droideka | canon | CIS; manufacturer not recorded |

Two of the eleven (`W-series droideka`, `Sniper droideka`) are **Legends-only** and their
index URLs point at `/Legends` pages. `Droideka Oppressor` and `Droideka Sentinel` are the
only two in the group with a **Rebel Alliance** owner — worth noting if the campaign wants
a non-Separatist droideka.

## Sourced text (Wookieepedia)

Droidekas, **also known as destroyer droids** ("destroyers" for short) and as **"rollies"
in clone trooper slang**, are battle droids used by the Trade Federation at the Invasion
of Naboo and later by the CIS during the Clone Wars. **Manufactured by the Colicoids on
Colla IV** (infobox: **Colicoid Creation Nest**). Infobox: **1.83 meters** tall (6 ft),
plating **bronze**, sensor colour **red**, armament **2 twin blaster cannons**; the body
text says shelled in **bronzium** armor.

🔑 **Two forms, one droid.** "They could **transform their shape by curling into a ball
and moving up to 75 kilometers per hour** across a surface, or **stand on three legs and
utilize a shield generator while firing at a target.**" The three-legged deployed form is
the combat form; the ball is the transit form. Ahsoka Tano's line for them is "rolling
death balls."

Armament and defence: **twin repeating blaster cannons** plus a **personal deflector
shield generator**. The shield is **polarized/phased** so the droideka's own bolts travel
outward while incoming projectiles are stopped. Most hand-held weapons cannot pierce it —
sidearms and blasters are ineffective; what works is an EMP or ion grenade through the
shield, anti-armour weapons, or artillery. Anakin Skywalker penetrated a droideka's
shields with an N-1 starfighter's blasters at the Battle of Naboo.

Two canon weaknesses, stated as tactical doctrine: **droidekas are blind from behind**, so
a distraction plus a rear assault kills; and the **shields are ineffective against slow or
stationary objects** — they are designed to absorb them so nothing hinders the droid's
movement, which is why a well-timed droid popper (EMP grenade) works. Crushing one with a
large heavy object also works. Pronoun usage varies in canon: some destroyers are
he/him, some she/her, some it/its.

History: faced by Qui-Gon Jinn and Obi-Wan Kenobi aboard a Droid Control Ship before the
Naboo ground invasion; at the Battle of Naboo they cut through the Gungan formation and
shot out the shield generators the Fambaa carried; later Separatist Droid Army service
through the Clone Wars; **ordered to shut down** after the Separatist Council was
massacred on Mustafar. Post-war individuals survive — one, "The Unwinder," became a
gladiatorial arena champion.

## Provenance

- **Manufacturer**: **Colicoid Creation Nest** — the Colicoids, on **Colla IV** — for the
  baseline, Sharpshooter, grapple, P-series, Q-series and Sniper variants.
  **Phlac-Arphocc Automata Industries** designed the Mark II and built the W-series;
  the Mark II's production is credited to **Zann Consortium Droid Works**. Manufacturer is
  blank for the Oppressor, Sentinel and Ultra Droideka.
- **Era**: **blank** — no `firstmade` or `retired` value in the infobox for any of the
  eleven rows (the baseline article's `firstmade=` and `retired=` fields are literally
  empty in the wikitext). In-text history places them at the Invasion of Naboo through the
  end of the Clone Wars, with a shutdown order after Mustafar, but that is narrative, not
  an infobox era, and is not promoted into this field.
- **Typical owners**: Trade Federation (Trade Federation Droid Army), Confederacy of
  Independent Systems (Separatist Droid Army), Separatist holdouts (Desix, the Agamar
  garrison), Xrexus Cartel, Bedlam Raiders, Klik-Klak's droid army, Crymorah-backed
  pirates. Variant-specific: **Zann Consortium** (Mark II); **Alliance to Restore the
  Republic and Galactic Empire** (Oppressor, Sentinel).

## Visual brief

🔴 **Answering the question directly: every droideka asset in this repo depicts the
DEPLOYED three-legged form. The rolled-up ball form does not exist on disk in any
donor, in any direction, for either chassis.** Since the ball is canonically the
droideka's *transit* mode and the thing clone troopers named it after ("rollies",
"rolling death balls"), a RimWorld droideka that never rolls is a real content gap, not
just an art gap — and it would need a second graphic set plus a state to switch on, not a
repaint.

**The two forms share almost no silhouette.** Deployed: a **tall vertical droid** — an
arched carapace shell over the top, a segmented spine, **two arm-mounted twin cannons held
out to the sides**, a spherical lower body, and **three splayed clawed legs**. Rolled: a
**featureless wheel/ball** with the legs and arms folded inside and the shell forming the
tread surface. Nothing about the deployed sprite can be reused for the ball.

- `wookieepedia_infobox_deployed.png` is the proportion authority for the deployed form:
  **dark bronze-brown with near-black weathering**, a big smooth curved dorsal shell that
  arcs forward over the head, a small head with **three red photoreceptors on a stalk
  assembly**, thin double-jointed arms ending in **paired cannon barrels**, a **spherical
  belly**, hip shield plates, and three long thin legs with hooked claw feet. Height sits
  in the legs and the arched shell, not in a torso.
- `wookieepedia_deployed_in_show.png` (Rex facing droidekas, in-show frame) confirms the
  deployed stance and the head-forward arch at a distance, in show lighting rather than a
  clean render.
- `wookieepedia_cutaway.png` shows a droideka **with its deflector shield up** — a
  translucent bubble around the whole deployed droid. Nothing in the repo art depicts the
  shield at all.
- **JDS deployed sprite (`donor_current_sprite.png`, 128×128, top-down) is a good match.**
  It shows the dorsal shell as a rounded brown dome filling the upper half, **three red
  photoreceptors**, two grey arm cannons out to left and right, grey hip plates, and the
  rear body ball. Palette is **bronze-brown**, agreeing with canon bronzium.
- 🔴 **The OuterRim droideka's palette contradicts canon.**
  `donor_current_sprite_outerrim.png` and the underlying 256×256 set
  (`Textures/OuterRim/Droid/Droideka/Droideka_*.png`) are **white and light grey** with
  only the three red photoreceptors for colour. Canon plating is **bronze / bronzium** and
  every reference image is a dark warm brown-bronze. The two donors therefore disagree with
  each other as well as with canon, and the OuterRim one is the wrong one. (Its geometry is
  right: the `south` view is the same deployed top-down layout as the JDS sprite, and the
  `east` view is a correct *profile* of the deployed form, with the dorsal shell arcing
  forward over the head and the body ball below. That profile view is what
  `design/Jawa/fauna/sprites/OuterRim_DestroyerDroid.png` shows — it is the east frame, not
  a rolled-up droid, despite reading as a hook shape at thumbnail size.)
- 🔴 **The repo Sharpshooter is a recolour of the standard droideka, not the canon
  Sharpshooter.** `donor_current_sprite_sharpshooter.png` keeps the standard rounded dorsal
  dome, **three** red photoreceptors, and the same hip plates, adding one forward barrel.
  Canon (`wookieepedia_sharpshooter.png`) is markedly different: a **large flat crescent
  back-shield** standing up behind the droid rather than a rounded dome; **two** large red
  photoreceptors on a horizontal bar; a **single long thin sniper barrel** projecting well
  forward; **flat angular side shield plates instead of arm cannons**; and a **pale
  green-grey** body with yellow trim, not brown. If the Sharpshooter is meant to read as a
  distinct unit on screen, the back-shield and the two-eye bar are the cues to add.
- **No repo art exists** for the Mark II, Oppressor, Sentinel, grapple, P-, Q-, W-series,
  Sniper (Legends) or Ultra Droideka. All nine are currently served by the one bronze
  deployed sprite.

## Source URLs

- https://starwars.fandom.com/wiki/Droideka — main article; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Droideka&format=json&prop=wikitext`
  (rendered HTML is Cloudflare-walled, the API is not). Sections read: `{{DroidSeries}}`
  infobox, lead, Description, History. "Behind the scenes" and Appearances **not** read.
- https://starwars.fandom.com/wiki/Droideka_Sharpshooter — wikitext pulled the same way;
  infobox read (1.87 m, bronzium, red photoreceptors, long-barrel heavy blaster rifle,
  Colicoid Creation Nest, Trade Federation / CIS). Body text **not** read in full.
- Remaining variant rows, infobox-derived from `DROIDS_INDEX.md`; these articles were
  **not** separately fetched this pass:
  https://starwars.fandom.com/wiki/Droideka_Mark_II ·
  https://starwars.fandom.com/wiki/Droideka_Oppressor ·
  https://starwars.fandom.com/wiki/Droideka_Sentinel ·
  https://starwars.fandom.com/wiki/Grapple_droideka ·
  https://starwars.fandom.com/wiki/P-series_droideka ·
  https://starwars.fandom.com/wiki/Q-series_droideka ·
  https://starwars.fandom.com/wiki/W-series_droideka/Legends ·
  https://starwars.fandom.com/wiki/Sniper_droideka/Legends ·
  https://starwars.fandom.com/wiki/Ultra_Droideka
- https://static.wikia.nocookie.net/starwars/images/9/9d/Droideka-SWE.png (File:Droideka-SWE.png → `wookieepedia_infobox_deployed.png`)
- https://static.wikia.nocookie.net/starwars/images/7/75/Droideka-USC.png (File:Droideka-USC.png → `wookieepedia_cutaway.png`)
- https://static.wikia.nocookie.net/starwars/images/5/53/Rex-vs-droidekas.png (File:Rex-vs-droidekas.png → `wookieepedia_deployed_in_show.png`)
- https://static.wikia.nocookie.net/starwars/images/2/23/SniperDroideka-TCWCEJtB.png (File:SniperDroideka-TCWCEJtB.png → `wookieepedia_sharpshooter.png`)

⚠️ **Not sourceable this pass**: the `Droideka` article's own image set contains **no
image of the rolled-up ball form** — only the three files above. So the ball's exact
appearance is asserted here only from the article's prose ("curling into a ball"). If the
owner wants the ball authored, a further image hunt is owed.

## Candidate images

- `wookieepedia_infobox_deployed.png` — the article infobox: full-body three-quarter render
  of a **deployed** droideka on transparent background. The proportion authority.
- `wookieepedia_cutaway.png` — the same deployed droideka **with its deflector shield
  bubble raised**. The only reference here for the shield.
- `wookieepedia_deployed_in_show.png` — in-show frame of Captain Rex facing droidekas;
  deployed form at combat distance in show lighting.
- `wookieepedia_sharpshooter.png` — the Droideka Sharpshooter infobox render. **Negative
  reference for the repo's Sharpshooter sprite**: it shows how different the canon
  Sharpshooter is (flat crescent back shield, two eyes, long single barrel, pale
  green-grey).
- `donor_current_sprite.png` — repo JDS droideka
  (`design/Jawa/fauna/sprites/JDSCIS_Droideka_Droid.png`, 128×128, top-down, deployed).
- `donor_current_sprite_sharpshooter.png` — repo JDS Droideka Sharpshooter
  (`JDSCIS_Droideka_Sharpshooter_Droid.png`). Weak evidence of the canon variant; strong
  evidence of what the repo currently ships.
- `donor_current_sprite_outerrim.png` — repo OuterRim destroyer droid
  (`OuterRim_DestroyerDroid.png`, 92×128); the **east/profile** frame of the deployed form,
  in the OuterRim mod's white-grey palette.

## ruling

(empty — owner has not reviewed this chassis yet)
