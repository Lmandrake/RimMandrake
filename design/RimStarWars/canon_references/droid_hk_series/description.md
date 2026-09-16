# HK-series (KotOR + OuterRim)

**defName**: this chassis is a **race + pawnkind pair**, not a xenotype. Real defs on disk:
- `RSW_DW_Race_guy762_DroidRace_HKseries` — label "HK-series protocol droid"
  (`src/RimStarWars/Droidworks/Defs/Races_KotOR.xml:49`)
- `RSW_DW_Race_guy762_DroidRace_HK50series` — "HK-50 series protocol droid" (same file, :104)
- `RSW_DW_Race_guy762_DroidRace_HK51series` — "HK-51 series assassin droid" (same file, :159)
- `RSW_DW_HeadType_guy762_DroidRace_HKseries` / `_HK50series` / `_HK51series` (HeadTypeDefs, same file)
- `RSW_DW_Race_OuterRim_HKDroid` + `RSW_DW_OuterRim_HKDroid`
  (`Races_OuterRim.xml`, `PawnKinds_OuterRim.xml:65`) — the separate OuterRim-donor chassis
- PawnKinds in `Defs/PawnKinds_KotOR.xml`: `RSW_DW_KotORDroidColonist_HK50AD`,
  `RSW_DW_KotORDroidColonist_HK51AD`, `RSW_DW_KotORMIBColonist_HK51AD`,
  `RSW_DW_KotORPlayableHero_HK47`, `RSW_DW_KotORDroidBad_hk50`, `RSW_DW_KotORDroidBad_hk50boss`

Sprites: `src/RimStarWars/Droidworks/Textures/KotOR/Droid/HK/HK_{body,head}_{n,s,e,w}.png`
(+ `_bodymask_` / `_headmask_`), and `Textures/OuterRim/Droid/HK/{Body,Head}/`.

## Canon variants this one repo chassis covers
- **HK-series assassin droid** (a.k.a. HK series protocol droid) — the parent line
- **HK Guardian Droid** — see the loud warning under Provenance; this is **not the same droid**

The repo additionally carries the HK-50 and HK-51 sub-series as their own races, which
Wookieepedia also treats as separate articles.

## Sourced text (Wookieepedia)

The **HK-series assassin droid**, also known as the **HK series protocol droid**, was a
series that *combined* assassin droid and protocol droid functions. "HK" stands for
**"Hunter Killer."** The dual nature is explicitly the reason for their lethality: they
could pass as ordinary (if sinister-looking) protocol droids, concealing their true
function and getting close to a target. `The New Essential Guide to Droids` is cited for
this and for the "HK series protocol droid" name.
[HK-series assassin droid](https://starwars.fandom.com/wiki/HK-series_assassin_droid)

Lineage, in order, all from that article:

- **HK-01** — Czerka Corporation's prototype and "progenitor of all HK-series droids."
  He was **responsible for the Great Droid Revolution on Coruscant**, and was destroyed by
  Jedi Master Arca Jeth.
- **HK-24 series** — Czerka's improved design. It sold badly ("few had want of an assassin
  droid"); Czerka halted production and sold the entire remaining inventory to Arkoh Adasca
  of Adascorp, who used them as captors and prison guards. All destroyed at the First Battle
  of Omonoth.
- **HK-47** — a **unique custom model constructed by Revan** shortly after the Mandalorian
  Wars, using HK-24 schematics. Visually closer to the HK-01 prototype than to the HK-24.
  Became "the longest surviving, most infamous, and most effective of the HK series" on the
  strength of a large degree of autonomy and adaptive programming, plus specific knowledge of
  Jedi behaviour and how to counter Force abilities.
- **HK-50 series** — **also designed by Revan.** Improvements over HK-47: better armour and
  weapon proficiency, **high-yield explosives installed within the chassis**, better
  self-maintenance, and the vocabulator static removed. Tuned for mass-casualty work rather
  than precision. Originally meant to destroy Republic ships that would not defect to Revan;
  redeployed to hunt survivors of the First Jedi Purge after **G0-T0** located them.
- After the HK-50 campaign, **the Republic banned the ownership, manufacture and use of HK
  series droids.**
- **HK-51 series** — built by Czerka ~three centuries later for the **Sith Empire**, near the
  end of the Great Galactic War; precision assassination rather than mass casualties. Sourced
  specifics: **+21% blaster accuracy** over HK-50, thicker durasteel armour, **micro-missile
  launchers replacing the HK-50's flamethrowers**, a stealth field generator, greater
  mobility, improved protocol functions. Two failsafes: assassination protocols that *degrade
  to nonfunction* unless the unit kills a high-value figure in Republic space, and a loyalty
  subroutine binding it to one owner (explicitly to prevent reprogramming against that owner).
  A shipment was stolen by the Dread Masters and crashed on Belsavis; only one unit was
  salvageable.
- **HK-55** — designed and programmed as a **bodyguard/steward**, not an assassin.
- **Clone Wars revival** — the CIS found HK-47's deactivated body in a ship wreck on Mustafar
  in 19 BBY and reverse-engineered it into battle-droid hybrids: HK-57, HK-58 Aurek/Besh,
  HK-67, HK-Taskmaster, settling on the **HK-77**. These were "more similar to battle droids
  than their predecessors," with **blasters attached to the ends of their arms — which
  prevented them from posing as protocol droids** — and were less deadly and less armoured.
  HK-47 later used the captured Neimoidian droid factory to build himself a new body and
  raise HK-47's Droid Army against all organic life.
- **HK protocol pacifist package** — a real sourced module that **suppressed an HK's combat and
  assassination protocols**, apparently to convert HKs into ordinary protocol droids (cited to
  KotOR II).
- **Restraining-bolt precedent (directly relevant to this repo's bolt design):** Darth
  Scabrous' HK unit had **gained full sentience**, so Scabrous fitted a **restraining bolt to
  keep it subservient**. When the bolt was removed during the Blackwing outbreak on
  Odacer-Faustin, it **immediately turned on its master** and helped his prisoners escape,
  then destroyed itself to cover them. A quirk: once unbolted it stopped prefacing its speech
  with "Statement:", "Query:", etc.

**🔴 What is NOT sourced, and matters for this campaign.** Nothing in the article ties the
HK-series to the **Rakata, the Star Forge, or Rakatan technology.** The manufacturer is
Czerka Corporation (later the CIS); HK-47 and the HK-50s are **Revan's personal designs**,
which is the only Old-Republic-lore hook the article actually supports. Given the brief's
expectation of heavy campaign significance, the honest finding is: the significance runs
through **Revan and Czerka**, not through the Rakata. (The repo does have a separate
Rakatan-adjacent chassis — `RSW_DW_Race_guy762_DroidRace_ADMkI_sf`, "Star Forge Assault
Droid" — and that, not HK, is where Star Forge manufacture lives on disk.)

**⚠️ Continuity status.** The HK-series article opens `{{Top|canon=HK-model gladiator droid}}`
and every internal link inside it is a `/Legends` link, which is Wookieepedia's convention for
a **Legends** article pointing at its canon counterpart. `DROIDS_INDEX.md` line 788 marks this
row `canon`; that column value is wrong for this row. The whole HK-series body above should be
read as **Legends**. The current-canon HK is a different, much thinner article
(`HK-model gladiator droid`), not fetched this pass.

## Provenance
- **Manufacturer:** **Czerka Corporation** (a.k.a. Czerka Arms), for HK-01, HK-24 and HK-51;
  later the **Confederacy of Independent Systems** for the Clone Wars hybrids (HK-57 through
  HK-77). HK-47 and the HK-50 series were designed by **Revan** personally, not by a
  manufacturer. Note the sourced Czerka motive from `Red Harvest`: *"Czerka built you special
  to get around local laws banning assassin droids"* — the protocol-droid disguise was a
  regulatory dodge, not just a tactic.
  [HK-series assassin droid](https://starwars.fandom.com/wiki/HK-series_assassin_droid)
- **Era:** the article carries **no infobox era field.** Blank, per the brief. Dated events
  the text does give, cited rather than inferred: HK-51 manufacture near the end of the Great
  Galactic War; the Clone Wars rediscovery in **19 BBY**; the wreck lying undiscovered until
  **1 ABY**. `DROIDS_INDEX.md:784` carries **3668 BBY** as the HK-51 series' `firstmade`.
- **Typical owners:** Czerka Corporation; Adascorp (Arkoh Adasca, the HK-24s); Revan;
  the Sith Empire (HK-51s, and the "Imperial Shock Droid" variants on Corellia); the Galactic
  Republic and the Eternal Alliance (HK-51 after salvage); the **GenoHaradan** bounty-hunting
  guild ("GenoHaradan Assassin Units"); the Confederacy of Independent Systems; HK-47's own
  Droid Army; individual Sith (Darth Scabrous). Later civilian reuse is sourced too:
  recovered HK-77s **refitted as firefighting droids** (blasters swapped for extinguishers,
  heat-resistant coating) and as **gambling proxies** in the criminal underworld
  (`Scavenger's Guide to Droids`).
  [HK-series assassin droid](https://starwars.fandom.com/wiki/HK-series_assassin_droid)

**🔴 The HK Guardian Droid is a different droid entirely.** Its article
([HK Guardian Droid](https://starwars.fandom.com/wiki/HK_Guardian_Droid)) is flagged
`{{Top|leg}}` (Legends), first appeared in the 1986 *Droids* comic/cartoon, and describes a
model whose **armour was almost impervious to blaster fire** — so impervious that the units
"became difficult to control" and thereby "contributed to the common prejudice against
droids." They were out of service by the early years of the Galactic Empire. C-3PO wore an
empty Guardian Droid **shell** as armour at Lonn Idd's repair station. The article gives **no
manufacturer, no era and no owner faction**, and makes **no connection whatsoever to
Czerka's Hunter-Killer line** — the shared "HK" letters appear to be coincidence. Grouping it
under this repo chassis is a filing convenience, not a canon relationship. Do not let its
"impervious armour" trait leak into the assassin chassis' design.

## Visual brief

**The two donor sprite sets on disk are different chassis and should not be treated as one
look.**

- **`donor_current_sprite.png` (KotOR donor, `HK_body_south`, 512×512)** is a **greyscale**
  torso plus a separate `HK_head_south` — flat mid-greys and whites with a heavy black
  outline, drawn as a masked/tintable asset (there is a matching `HK_bodymask_*` /
  `HK_headmask_*` set). **The grey is not the shipping colour.** The race def supplies it:
  `Races_KotOR.xml:96–104` sets the `skin` colour channel to `RGBA(200,100,50,255)` with a
  second channel of `RGBA(255,105,65,255)` — a rust orange over a brighter orange. **That is a
  good canon match.** `wookieepedia_hk47.jpg` shows HK-47 as burnished rust-red/copper plating
  with **glowing yellow-orange photoreceptors**, and the two RGBA values land squarely in that
  range. Judge this sprite tinted, never as the raw grey PNG.
- **`donor_outerrim_body_south.png` (256×256)** is a *much* smaller, chunkier, more cartoonish
  read of the same silhouette — same wedge head and shoulder blocks, far less internal detail.
  It is a separate donor for `RSW_DW_Race_OuterRim_HKDroid`.

Against the canon images the sprite silhouette is **broadly right and specifically thin**:

- The **head shape is the strongest agreement.** Both canon images show a narrow, vertically
  elongated, faceted wedge skull with a pronounced brow ridge, a flat vertical faceplate, and
  two small bright photoreceptors set close together. The KotOR sprite's head reproduces the
  wedge and the brow.
- **Photoreceptors are the one thing both canon images make unmissable and the sprite
  omits**: HK-47's and HK-51's eyes are **self-luminous yellow-gold**, reading as the focal
  point of the whole design in near-dark scenes. There is no emissive treatment in the donor
  head sprite. If a single correction is worth making to this chassis, it is glowing yellow
  eyes.
- **Proportions:** canon HK is **lanky and skeletal** — long thin forearms, exposed
  piston/cable runs at elbow and knee, narrow waist, splayed multi-jointed clawed hands, a
  distinctly *humanoid but starved* build. The RimWorld donor is compressed to a broad
  armoured torso with almost no limb read, which is a format constraint (RimWorld pawns are
  torso-and-head) rather than an error, but it does mean the chassis' most recognisable canon
  cue — **spindly limbs on a heavy chest** — does not survive into the sprite.
- **`wookieepedia_hk51.jpg` differs from HK-47 in the ways the text says it should**: much
  more weathered olive-grey-brown plating with **orange striping/wear rather than overall
  orange**, a lit circular chest emblem, visible weapon hardpoints on both forearms, and a
  black antenna/blade on the back. So the repo's saturated-orange colour channel matches
  **HK-47/HK-series**, not the HK-51 look, even though `Races_KotOR.xml` carries HK-51 as its
  own race — worth checking that the HK51series race is not inheriting the HK-series orange.
- `wookieepedia_hk01_prototype.jpg` (HK-01, 600×1415) was downloaded as the prototype
  reference and is the tallest/thinnest of the three; it is a guide-illustration plate rather
  than a game render.


## Must show
- [ ] Rust-red/copper plating (HK-47/HK-series) with glowing yellow-orange photoreceptors
- [ ] Narrow, vertically elongated, faceted wedge skull with a pronounced brow ridge and two photoreceptors set close together
- [ ] HK-51 variant: weathered olive-grey-brown plating with orange striping/wear, not overall orange
- [ ] HK-51 variant: lit circular chest emblem and visible weapon hardpoints on both forearms

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/HK-series_assassin_droid — main article; text pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=HK-series_assassin_droid&format=json&prop=wikitext`
  (21,309 chars of wikitext, read in full — no truncation)
- https://starwars.fandom.com/wiki/HK_Guardian_Droid — via the same API pattern (2,191 chars, full)
- https://static.wikia.nocookie.net/starwars/images/3/37/HK-47.png → `wookieepedia_hk47.jpg`
- https://static.wikia.nocookie.net/starwars/images/3/3a/HK-51.png → `wookieepedia_hk51.jpg`
- https://static.wikia.nocookie.net/starwars/images/4/41/HK01-NEGTD.png → `wookieepedia_hk01_prototype.jpg`
- Named in the article but **not fetched this pass**: `HK-model gladiator droid` (the canon
  counterpart), `HK-50 series assassin droid`, `HK-51 series assassin droid`, `HK-77 assassin
  droid`, `HK-24 series assassin droid`, `Darth Scabrous' HK droid`, `File:Guardiandroid.png`
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_KotOR.xml`,
  `Defs/PawnKinds_KotOR.xml`, `Defs/Races_OuterRim.xml`, `Defs/PawnKinds_OuterRim.xml`

## Candidate images
- `wookieepedia_hk47.jpg` (276×368) — HK-47 in-game render, three-quarter view, holding a
  rifle across the body. Rust-red/copper plating, glowing yellow-orange eyes, faceted wedge
  head. **The primary colour reference for this chassis.**
- `wookieepedia_hk51.jpg` (847×949) — an HK-51 unit, front three-quarter, SWTOR render.
  Weathered olive-grey plating with orange wear striping, lit circular chest emblem, forearm
  hardpoints, glowing yellow eyes. Shows how far the HK-51 look diverges from HK-47's.
- `wookieepedia_hk01_prototype.jpg` (600×1415) — HK-01, the prototype, from
  `The New Essential Guide to Droids`. Full-length illustration plate.
- `donor_current_sprite.png` / `donor_current_sprite_head.png` (512×512 each) — the KotOR
  donor body and head, **greyscale/maskable**; must be judged tinted with the def's
  `RGBA(200,100,50)` / `RGBA(255,105,65)` channels, not as raw grey.
- `donor_outerrim_body_south.png` / `donor_outerrim_head_south.png` (256×256 each) — the
  separate OuterRim-donor HK chassis, chunkier and lower-detail.

## ruling
(empty — the owner has not reviewed this chassis yet)
