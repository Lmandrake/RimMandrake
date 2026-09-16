# Mimbanese

**defName**: `RSW_RimMandrakeMimbanese` (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`,
verified present). Matrix placement: `TribeCivil: R` — rare, tribal faction, which suits a
species defined by guerrilla warfare and improvised camouflage.

## Sourced text (Wookieepedia)
The Mimbanese, also **Mimbanites**, were **one of several sentient species native to Mimban**
(so "a Mimbanese" is not the same as "a native of Mimban"). **Experts in guerrilla warfare, the
Mimbanese had the unsettling ability to seemingly disappear into the mud and murk of their
homeworld.** Habitat: **subterranean**. The infobox gives **no height, no mass, no lifespan and
no hair colour** — all unsourced in canon and recorded here as absent, not guessed.

Skin colour is sourced three ways — **red** (*Solo*), **brown** (*Bounty Hunters* 15), **grey**
(*The Acolyte: The Visual Guide*). Eye colour likewise three ways — **blue** (*Solo*), **black**
(*Acolyte VG*), **turquoise** (*Squadrons*).

Biology: **the Mimbanese had lurid, red skin, lidless blue eyes, and two rows of short horns
above their brows.** 🔑 **The bright red colour of the Mimbanese came from their keratin
scutes, although they could fade in colour** — so the red is a *scale/plate* colour that
weathers, which is why brown and grey are also sourced rather than being separate morphs. **The
Mimbanese had enhanced eyesight, adapted to the low light of their homes.**

Society: they **lived underground and were experts in camouflage**, and 🔴 **were both highly
aggressive and highly intelligent**, **capable of creating improvised traps and covering
themselves in mud for camouflage.**

History (relevant to a tribal-faction read): they allied with the Republic in the Clone Wars
under tribal leader **Iasento**, who organised the **Mimbanese Liberation Army**; after the
Empire's founding they fought Imperial swamp troopers of the 224th Armoured Division. Some
joined the **Nihil** in the High Republic era; one, **Kierah Koovah**, lost an arm at the
Battle of Mimban, took a cybernetic replacement, and later led the New Republic's Vanguard
Squadron as a U-wing pilot. Han Solo on them: *"It's their planet. **We're** the hostiles."*

⚠️ The canon article carries `{{Species-stub}}` but **does** have a biology section. **No
Legends article was needed or found for this species** — the Mimbanese are a *Solo*-era canon
creation, so unlike Kel Dor and Kubaz there is no Legends fallback supplying height, mass or
lifespan. **Those three are simply unsourced in any continuity and must not be invented.**

## Visual brief
All three references are *Solo*-era practical-costume photography of the same design, which
makes them unusually reliable — they show a real built suit, not an illustrator's read.

🔑 **The face is bare skin. There is no mask and no goggles** — this is the opposite of the
Kel Dor and Kubaz cases in the same batch, and worth stating because the silhouette *looks*
masked at a glance.
- **The eyes are FACE**: **two large, round, protuberant, pale-blue eyes**, set wide, with **no
  eyelid fold** — a dark orbital rim runs right around each one, which is what a **lidless** eye
  reads as. Matches the sourced "lidless blue eyes" exactly. ⚠️ At small scale the dark rims can
  be mistaken for goggle bezels; they are not. There *are* small dark fittings at the temples,
  which read as **costume clips holding the headwrap**, not eyewear.
- **The nose is a broad, flattened, downward-tapering snout** occupying the lower centre of the
  face, with paired nostril openings at its tip. No mouth is prominent.
- 🔑 **The two rows of short horns above the brows are present and readable**: a **dark,
  serrated crown of short spikes running in a V across the forehead above each eye.** Clearest
  in `wookieepedia_trio_soldiers.jpg` and `wookieepedia_iasento_full.jpg`. This is the single
  most species-identifying feature after the eyes.
- **The cranium is smooth and domed**, hairless, with no ears visible.

**Skin colour, and a trap.** The face is a **saturated salmon/brick red**, mottled and streaked
with dried mud. 🔴 **But so is the clothing** — every reference wears a **red-dyed coverall**
in nearly the same hue, and **the hands are gloved in all three images**, so the *only* skin on
show is the face. A prompt fed "red-skinned species" plus these images will paint the whole
figure red skin when in fact it is red skin plus a coincidentally red garment. Note also that
the sourced red *fades* (keratin scutes), which is the canonical route to the brown and grey
citations — so a weathered, desaturated individual is correct, not a mistake.

**Silhouette — this is what makes a Mimbanese recognisable at RimWorld scale.** All three
figures are buried in **enormous ragged ghillie capes of dried reeds, straw and grass bundles**
hanging from the shoulders, back and limbs, over **wooden slat plates and scavenged armour
panels**, with **ammunition bandoliers**, **mud-caked pale-grey boots**, slugthrower/blaster
rifles and a hand axe. The camouflage layer is bigger than the body. This is the visual form of
the sourced "improvised traps… covering themselves in mud for camouflage."

**Build.** 🔴 **Ordinary humanoid proportions** — upright, human height, human mass, normal
limb thickness and shoulder width in all three references. **Nothing reads gaunt, thin or
emaciated.**

### Def-versus-canon (flagged — not fixed here)
- 🔴 **`AptitudePoor_Intellectual` and `RSW_GS_Primitive` directly contradict the sourced text**,
  which says the Mimbanese were **"both highly aggressive and highly intelligent."** The def
  keeps the aggression (`Aggression_Aggressive`, correctly) and inverts the intelligence. This
  is the flagship defect for this species. The same source credits them with **improvised trap
  construction**, and canon has a Mimbanese leading a New Republic starfighter squadron.
- 🔴 **`RSW_Head_Devolved` renders a Mimbanese with TUSKEN RAIDER head art.** Traced:
  `RSW_Head_Devolved` (`SW_Genes.xml:2206`, label *"Devolved head"*, description *"Carriers of
  this gene have a devolved facial appearance"*) forces head types
  `RSW_Male_DevolvedNormal` / `RSW_Female_DevolvedNormal`, whose `graphicPath` in
  `SW_HeadTypes.xml:507` and `:234` is **`RimMandrakeSW/SWX/Pawn/HeadType/Sov_tusken/HeadSandM`
  / `HeadSandF`** — i.e. the Tusken "HeadSand" sprite. Saved here as
  `donor_current_head_is_tusken_art.png`: **a broad blank rounded head with two plain black
  dots for eyes, no nose, no mouth, no horns.** A Mimbanese therefore ships with a Tusken's
  featureless wrapped head and **none** of its own three identifying features. Same class of
  cross-species borrowing as the `RSW_RimMandrakeIthorian` → Sullustan namer the previous batch
  found, but visual rather than textual.
- 🔴 **The gene's own label and description — "devolved" — editorialise against canon.** Naming
  aside, it is the wrong word for a species the source calls highly intelligent, and it will
  surface in the player's gene UI.
- 🔴 **`RSW_Body_gaunt` + `Body_Thin`** against three references that all show **normal human
  build.** Nothing in canon or in any image supports gaunt or thin. No height or mass is sourced
  in *any* continuity, so these genes are inventions, not interpretations.
- ⚠️ **`RSW_Eyes_Big` gives "large, **black** eyes"** (`SW_Genes.xml:1023`). Large is right and
  well chosen; **black is one of three sourced colours (Acolyte VG) but is not what the
  reference images show** — the *Solo* design, which is the primary and most-cited appearance, is
  **pale blue**. The mod has `RSW_Eyes_BigGreen/Orange/Red/Yellow` variants but apparently no
  blue, so the closest canon colour may not be expressible.
- ⚠️ **Nothing represents the two rows of short brow horns as horns.** The one Mimbanese-specific
  art asset on disk is `HeadAttachments/mimbanese/RidgedBrow_south.png` (`RSW_Brow_Ridged`), and
  it is a **creditable near-miss** — two dark serrated comb-like arcs forming a V above the eyes,
  which does read as a row of short spikes. But `RSW_FacialRidges_bumpy` + `RSW_FacialRidges_broad`
  are *ridges*, not horns, and the Iridonian def shows a real horn gene exists in this mod
  (`RSW_Headbone_zabrak`). Nothing expresses the **lidless** quality of the eyes, or the
  **keratin scutes** that make the skin red and let it fade.
- ⚠️ Unsourced: `Outland_AcceleratedPregnancy`, `Outland_ThickSkin`, `AptitudeStrong_Mining`
  (subterranean habitat is sourced; mining aptitude is not).
- ⚠️ `<description>` is the single character **`e`** — no description ships for this xenotype.
  (Same defect as `RSW_RimMandrakeKubaz` in this batch and `RSW_RimMandrakeGand` in the last.)
- ✅ **Correct, and worth recording as correct**: `nameMaker` is `RSW_KoTOR_NamerMimbanese` — the
  right species' namer. `Skin_DeepRed` matches the sourced lurid red and the images.
  `DarkVision` and `UVSensitivity_Mild` both match **"enhanced eyesight, adapted to the low
  light of their homes"** plus the subterranean habitat — a genuinely well-chosen pair.
  `Aggression_Aggressive` and `AptitudeStrong_Melee` match "highly aggressive" and the guerrilla
  warfare. `RSW_Brow_Ridged` is the right idea, imperfectly executed.

## Source URLs
- https://starwars.fandom.com/wiki/Mimbanese — canon article; rendered HTML is Cloudflare-walled,
  wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Mimbanese&format=json&prop=wikitext`
  (8,170 chars, 2026-09-15). Carries `{{Species-stub}}`.
- **No `Mimbanese/Legends` article exists** — the species is canon-only (*Solo*, 2018 onward), so
  there is no Legends fallback for height, mass or lifespan. Those remain **UNSOURCED**.
- https://static.wikia.nocookie.net/starwars/images/9/9d/Mimbanese-SoloUSC.png
  (File:Mimbanese-SoloUSC.png, canon infobox → `wookieepedia_infobox.jpg`)
- https://static.wikia.nocookie.net/starwars/images/4/40/IasentoFull-BTCG.png
  (File:IasentoFull-BTCG.png, *"Iasento, leader of the Mimbanese Liberation Army"* →
  `wookieepedia_iasento_full.jpg`)
- https://static.wikia.nocookie.net/starwars/images/9/93/MimbaneseTrio-SoloASWS.png
  (File:MimbaneseTrio-SoloASWS.png, *"A trio of Mimbanese soldiers"* →
  `wookieepedia_trio_soldiers.jpg`)
- Repo sources for the head-art trace: `src/RimStarWars/StarWarsRaces/Defs/GeneDefs/SW_Genes.xml:1023`
  (`RSW_Eyes_Big`), `:2206` (`RSW_Head_Devolved`);
  `src/RimStarWars/StarWarsRaces/Defs/HeadTypeDefs/SW_HeadTypes.xml:234` and `:507`
  (the Tusken `graphicPath`).
- NOT fetched this pass: no `starwars.com/databank` page for the Mimbanese was attempted.

## Candidate images
- `wookieepedia_iasento_full.jpg` — **the reference of record.** The largest and clearest of the
  three: Iasento full-body on white, from practical costume photography. Settles the pale-blue
  lidless eyes with dark orbital rims, the serrated brow-horn crown, the broad flattened snout,
  the red face-versus-red-garment distinction, the reed ghillie cape with slat plates and
  bandoliers, and the ordinary human build.
- `wookieepedia_infobox.jpg` — the canon infobox, a second full-body costume shot of a different
  individual. Independently confirms every feature above and shows the camouflage layer at its
  most extreme (reed bundles projecting well past the shoulder line).
- `wookieepedia_trio_soldiers.jpg` — three Mimbanese soldiers together. **Small and low
  resolution**, so poor for fine detail, but its value is showing that **the brow-horn crown and
  the red head / red coverall combination recur across individuals** — i.e. they are species
  traits, not one costume.
- `donor_current_sprite.png` — the mod's current Mimbanese-specific art,
  `SWX/Pawn/HeadAttachments/mimbanese/RidgedBrow_south.png` (`RSW_Brow_Ridged`). Greyscale, which
  is correct and expected. **A near-miss worth keeping**: two dark serrated arcs in a V above the
  eyes, which does approximate the sourced two rows of short brow horns.
- `donor_current_head_is_tusken_art.png` — 🔴 **negative reference, kept and labelled.** This is
  `SWX/Pawn/HeadType/Sov_tusken/HeadSandM_south.png`, **the head a Mimbanese pawn actually
  renders with** by way of `RSW_Head_Devolved`. It is **Tusken Raider art**: a broad blank
  rounded head, two plain black dots for eyes, faint cheek shading, no nose, no mouth, no horns.
  It is not evidence about Mimbanese appearance in any sense — it is the defect.

## ruling
(empty — owner has not reviewed this race yet)
