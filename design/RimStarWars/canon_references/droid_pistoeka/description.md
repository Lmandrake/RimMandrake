# Pistoeka sabotage droid / buzz droid (repo chassis: Pistoeka, JDS)

**defName**: droids are **not xenotypes**. One race def on disk:
- `RSW_DW_Race_JDSCIS_Pistoeka_Sotage_Droid` — label **"Pistoeka Sotage Droid"**,
  `src/RimStarWars/Droidworks/Defs/Races_JDS.xml:8`. `ParentName="DW_Family_Labour"`,
  `baseBodySize` **0.7**, `baseHealthScale` **0.3**, `MoveSpeed` **4.0**, `skinShader`
  **Cutout** (no colour channels, no mask — the PNG's own pixels ship), `headTypes` =
  `RSW_DW_HeadType_Blank`, and **no `DroidworksExtension` and no `CompDroidDetonation`**, unlike
  the LR-57 in the same file.
- **No PawnKindDef found** for this race anywhere in `src/RimStarWars/`.

🔴 **"Sotage" is a misspelling of "Sabotage", and it is in the defName, the label and the
texture filenames** (`JDS/Things/Pistoeka_Sotage_Droid*.png`). It comes from the upstream JDS
donor (`JDSCIS_Pistoeka_Sotage_Droid`) and is carried through verbatim by the absorber.
`Races_JDS.xml` is **generated** by `src/RimStarWars/Droidworks/Source/gen_droidworks_defs.py`
and says so in its header — so this is not a hand-edit; reporting it, not fixing it. Note that
a player sees "Pistoeka Sotage Droid" in-game.

Sprites: `src/RimStarWars/Droidworks/Textures/JDS/Things/Pistoeka_Sotage_Droid{,_south,_east,_north}.png`,
256×256, three directions.

## Canon variants this chassis covers

| canon row | continuity | index line | what distinguishes it |
|---|---|---|---|
| Pistoeka sabotage droid | canon (+Legends) | 1288 | the baseline buzz droid; Colicoid Creation Nest |
| Mark One Pistoeka sabotage droid | canon | 1075 | first-generation; **doonium shell** over the droid brain |

Also-known-as: **buzz droid** — overwhelmingly the common name, and the only name the films use.

The **Mark One** is a stub article (1,988 chars) and its only distinguishing fact is the shell
material. Thrawn, quoted directly: *"That particular model had a **doonium shell** protecting the
brain core. It was **removed in later versions.** The high value of the metal meant that the cost
outweighed the defensive benefits."* Mark Ones "were fairly similar to the later versions **to
the point that many couldn't distinguish the different models from each other**" — so the repo
serving both with one sprite is canon-defensible, not a shortcut. Their doonium made them
valuable to collectors and scrappers; Thrawn bought two non-functional ones for **500 credits**
and repaired them. That is the single most Jawa-relevant fact in this entry: **a buzz droid is
worth money for its shell, not its function.**

## Sourced text (Wookieepedia)

The **Pistoeka sabotage droid**, also known as the **buzz droid**, was a model of sabotage droid
manufactured by **Colicoid Creation Nest** that **could speak the Colicoid language**, used by
the CIS during the **later stages of the Clone Wars** to disable enemy craft.
[Pistoeka sabotage droid](https://starwars.fandom.com/wiki/Pistoeka_sabotage_droid)

🔑 **Size: 0.25 meter (10 inches) — and that figure is explicitly the DIAMETER "in sphere
mode."** Cited to *The Clone Wars: Character Encyclopedia — Join the Battle!* for the number and
to the *Star Wars Encyclopedia* for the "in sphere mode" qualifier. **Mass is empty.** So canon
gives a folded diameter and **no deployed span at all** — a deployed buzz droid's leg-to-leg
width is UNSOURCED. This matters for the repo, which depicts only the deployed form (below).

**Two forms, and canon states the transition.** They were "transferred to enemy fighters via
specialized **discord missiles**, and then **popped open, to reveal their insect-looking body.**"
They were "tiny saboteurs **encased in armored shells**." A discord missile could carry **up to
seven** buzz droids, fired from **HMP droid gunships**, **vulture droids**, or **droid
tri-fighters**.

**Armament — all four are tools, not guns** (infobox, each cited to the *Star Wars
Encyclopedia*): **circular saw**, **drill head**, **pincer arm**, **plasma torch**. Body text
adds that they used these "to swiftly dismantle starfighters, vehicles, **or even other
droids**," and that they had a **magnetic grip**.

**Sensor: red.** 🔑 **And the red eye is the canonical weak point, stated as doctrine:** "the
central eye was a weak spot which could take the buzz droid out of commission when hit.
**Zapping this big red eye sent a chain reaction down the entire droid**, and shut it down almost
immediately."

**Disposable and swarming.** *Collapse of the Republic* calls them **"disposable weapons"**;
"despite their individual insignificance, **a swarm of buzz droids were capable of making short
work of a craft by targeting its vital systems.**"

**History points:** at the **Carida incident**, a super tactical droid sent buzz droids after
D-Squad aboard a *Venator*, and M5-BZ blew them out an airlock into hyperspace; they nearly
killed Anakin Skywalker at the **defense of Cato Neimoidia**; at the **Battle of Ringo Vinda** an
HMP gunship used them to disable the shuttle carrying the clone trooper Tup; at the **Battle of
Coruscant** they **destroyed Obi-Wan Kenobi's astromech R4-P17**. Four years after the Empire
rose, the **Free Ryloth Movement modified large numbers of them to explode** and delivered them
inside modified vulture droids against the *Perilous* over Ryloth. Before the **Battle of
Jakku**, an undercover Imperial released a swarm against the New Republic Star Destroyer
*Deliverance*, killing an engineer and the captain.

⚠️ The article carries an `{{Update|Thrawn (novel), Dark Disciple}}` banner — **Wookieepedia's
own flag that it has not integrated those two sources.** Both articles were pulled and read in
full (11,740 and 1,988 chars); nothing is truncated, but the baseline article is
self-declared incomplete.

## Provenance

- **Manufacturer:** **Colicoid Creation Nest** (cited to *Ultimate Star Wars*) for the baseline.
  **Blank for the Mark One** — its infobox `manufacturer=` is empty, and it carries only
  `line=Pistoeka sabotage droid`. Note the Colicoids also built the droideka, so **this chassis
  and `droid_droideka` share a manufacturer** — and both are ball-folding designs, which is
  probably not coincidence.
  [Pistoeka sabotage droid](https://starwars.fandom.com/wiki/Pistoeka_sabotage_droid) ·
  [Mark One Pistoeka sabotage droid](https://starwars.fandom.com/wiki/Mark_One_Pistoeka_sabotage_droid)
- **Era:** **blank.** `firstmade=` and `retired=` are empty in both infoboxes.
- **Typical owners:** **Confederacy of Independent Systems**; **Free Ryloth Movement**;
  **Mining Guild**; **Galactic Empire**. The Mark One's sole listed affiliation is
  **Mitth'raw'nuruodo (Thrawn)** personally — a *collector*, not a military user, which is why
  the Mark One row's owners field reads as one name.
  `DROIDS_INDEX.md:1288,1075` matches both infoboxes exactly.

## Visual brief

🔴 **Answering the question directly: the repo sprite shows the DEPLOYED form — shell split into
two open hemispheres held up like wings, limbs and eye exposed. The folded sphere does not exist
on disk in any direction.** This is the same class of gap as the droideka's missing ball, and
here it is arguably worse: canon gives the **folded diameter as the droid's only stated
dimension**, and the sphere is how a buzz droid arrives (inside a discord missile) and how it
would be found as scrap. A Jawa clan would encounter the sphere far more often than the spider.

**The two forms share nothing.** Folded: a **smooth armoured ball**, roughly grapefruit-sized at
0.25 m. Deployed: an **insectile spider** with the shell halves flung open behind it and six-plus
tool limbs splayed forward.

**`wookieepedia_buzzdroid_detail.jpg` (1300×1300) is the proportion authority for the deployed
form.** What it shows:

- **The two shell halves opened wide and held high**, one to each side, like scarab wing cases.
  Their **outer faces are a mottled olive/khaki-yellow with dark grey ribbing and segmented
  panel lines**; their **inner faces are dark grey mechanism**. The shells are the largest and
  most colourful part of the droid, and the **only** part carrying warm colour.
- **A compact dark grey-black central body** on the vertical axis, narrow and stacked, with a
  small domed cap on top and a thin whip antenna rising from it.
- 🔑 **Multiple red photoreceptors, not one.** The render shows a **large central red eye** with
  **at least two smaller red lenses stacked above and below it** on the body's front face, plus
  small red points out on the limb bases. The prose singles out "this **big** red eye" as the
  weak spot, so the central one is the important one — but the *look* is a cluster, not a
  cyclops.
- **Six or more long thin multi-jointed black limbs** splayed forward and down, each terminating
  in a **different tool**: a visible **toothed circular saw disc** at lower left, a **flat pad /
  pincer**, a **drill**, hooked claws. The limbs are the droid's whole width and read as
  spider-like.
- Overall palette: **near-black body and limbs, olive-khaki shells, red eyes.** No bright metal.

`wookieepedia_buzzdroid_tools.jpg` is the article's "well equipped for sabotage and mayhem"
plate — a second view of the same deployed configuration, and the reference for the tool heads
specifically. `wookieepedia_buzzdroid_on_starfighter.jpg` shows them **in their actual canon
context — clinging to the hull of Skywalker's Eta-2 in flight** — which is the one thing a
RimWorld pawn can never depict.

**What the repo sprite shows, and it is a strong match:**

- `donor_current_sprite.png` (256×256, `south`/top-down) is the deployed form read from above:
  **two olive-khaki shell halves opened symmetrically left and right** with grey inner
  mechanism, a **dark near-black central body** on the vertical axis with a thin antenna spike at
  the top, and a **single red photoreceptor** in the centre of the body. The **shell colour is an
  excellent match** to the canon khaki-olive, and the open-wing layout is exactly right.
- ⚠️ **Two specific deficits against the reference.** (1) **One red eye instead of the canon
  cluster** — the big central eye is there, the stacked smaller lenses are not. (2) **The tool
  limbs are the weakest part.** Canon's silhouette is dominated by six-plus long spider legs
  ending in a **saw disc, a drill and a pincer**; the sprite's limbs are short, few, and carry no
  distinguishable tool heads. At thumbnail size the repo droid reads as *a beetle with open wing
  cases*, where canon reads as *a spider with power tools*. Adding the **saw disc** alone would
  do most of the work, since it is the most recognisable single feature in the canon render.
- ⚠️ **`skinShader` is `Cutout` with no mask and no colour channel**, so the PNG's own pixels are
  the shipping appearance. There is no def-side tint to blame or to fix — judge it literally.
- 🔴 **Scale is the loudest def-versus-canon problem in this entry: `baseBodySize` is 0.7 for a
  droid canon states at 0.25 m folded.** 0.7 in RimWorld is roughly dog-scale — several times the
  sourced size. Canon buzz droids are hand-sized things that swarm; a 0.7-body-size pawn is a
  substantial creature. Flagging, not fixing. (`baseHealthScale` **0.3** is, by contrast, a good
  match to "disposable weapons" and "individual insignificance", and `MoveSpeed` **4.0** suits a
  fast little saboteur.)
- ⚠️ **The parent family is `DW_Family_Labour`.** Every other droid in this batch that fights
  sits under `DW_Family_Battle`. Canon classes the Pistoeka as a **sabotage droid** whose entire
  armament is **cutting and drilling tools** — so "labour" is a defensible reading of the
  toolset and a poor reading of the role. Worth the owner's eye.
- 🔴 **Deeper than art: canon buzz droids attach to a craft in flight and dismantle it.** In this
  repo the chassis is a **walking pawn on a map**. That is a role translation, not a bug, but it
  means none of the droid's canon behaviour — discord-missile delivery, magnetic grip, hull
  clinging, swarming a vehicle's vital systems — has any expression on disk. The nearest
  RimWorld-native equivalents the canon text actually supports are **swarm counts (up to seven
  per missile)**, **dismantling other droids**, and **being killed by a single hit to the eye.**


## Must show
- [ ] Deployed form only: two shell halves opened wide and held high to each side, outer faces mottled olive-khaki with dark grey ribbing
- [ ] Compact dark near-black central body with a thin whip antenna rising from the top
- [ ] Multiple red photoreceptors (a cluster, not a single eye) on the body's front face
- [ ] Six or more long thin multi-jointed black limbs splayed forward, with distinguishable tool heads (saw disc, drill, pincer)

## Engine limits
`skinShader` is `Cutout` with no colour channel and no mask — the PNG's own pixels are the shipping appearance, so a colour correction requires a repaint, not a def edit.

## Source URLs

- https://starwars.fandom.com/wiki/Pistoeka_sabotage_droid — main article; wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=Pistoeka_sabotage_droid&format=json&prop=wikitext`
  (11,740 chars, **read in full**). Rendered HTML is Cloudflare-walled; the API is not.
- https://starwars.fandom.com/wiki/Mark_One_Pistoeka_sabotage_droid — same API pattern
  (1,988 chars, **read in full**; the article is a `{{Droid-stub}}`)
- https://static.wikia.nocookie.net/starwars/images/4/4d/BuzzDroidDetail-SWE.png
  (File:BuzzDroidDetail-SWE.png → `wookieepedia_buzzdroid_detail.jpg`)
- https://static.wikia.nocookie.net/starwars/images/a/af/BuzzDroid-TCWCEJtB.png
  (File:BuzzDroid-TCWCEJtB.png → `wookieepedia_buzzdroid_tools.jpg`)
- https://static.wikia.nocookie.net/starwars/images/1/1a/AhsokaEta2.png
  (File:AhsokaEta2.png → `wookieepedia_buzzdroid_on_starfighter.jpg`)
- https://static.wikia.nocookie.net/starwars/images/4/47/MarkOnePistoekaSabotageDroid-Thrawn2.png
  (File:MarkOnePistoekaSabotageDroid-Thrawn2.png → `wookieepedia_markone.jpg`)
- Named in the articles, **not fetched this pass**:
  https://starwars.fandom.com/wiki/Discord_missile ·
  https://starwars.fandom.com/wiki/Colicoid_Creation_Nest ·
  https://starwars.fandom.com/wiki/Scav_droid
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_JDS.xml` (generated by
  `src/RimStarWars/Droidworks/Source/gen_droidworks_defs.py` — do not hand-edit)

⚠️ **Not sourceable this pass:** no image of the **folded sphere** was found in either
article's image set — all four images show the deployed form or the droid attached to a hull. So
the sphere's exact appearance is asserted here **only from prose** ("encased in armored shells",
"popped open", "0.25 meter diameter in sphere mode"). If the owner wants the sphere authored, a
further image hunt is owed — the same debt the droideka entry records for its ball form.

## Candidate images

- `wookieepedia_buzzdroid_detail.jpg` (1300×1300) — the article infobox: full deployed buzz droid
  on transparent background, shells open. **The proportion, limb-count and colour authority.**
- `wookieepedia_buzzdroid_tools.jpg` (1015×770) — "well equipped for sabotage and mayhem";
  second deployed view. **The reference for the individual tool heads** (saw, drill, pincer).
- `wookieepedia_buzzdroid_on_starfighter.jpg` (1485×800) — buzz droids clinging to Anakin
  Skywalker's Eta-2 at Cato Neimoidia. The canonical *context*, and evidence for scale relative
  to a starfighter hull.
- `wookieepedia_markone.jpg` (416×274) — the **Mark One** infobox image from *Thrawn* 2. Small
  and comic-styled; **weak evidence for appearance**, and canon says the Mark One is anyway
  near-indistinguishable from later models except for the doonium shell.
- `donor_current_sprite.png` (256×256) — repo JDS sprite, `south`/top-down, **deployed form**.
  Judge literally: `skinShader` is `Cutout`, no tint applied.
- `donor_body_east.png` (256×256) — the profile frame.

## ruling

(empty — the owner has not reviewed this chassis yet)
