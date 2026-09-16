# BX-series droid commando (repo chassis: BX commando, JDS + OuterRim)

**defName**: two defs across two donor mods.
- JDS: `RSW_DW_Race_JDSCIS_BX_Commando_Droid` (ThingDef, `Defs/Races_JDS.xml`) with
  PawnKindDef `RSW_DW_JDSCIS_BX_Commando_Droid` (`Defs/PawnKinds_JDS.xml`).
- OuterRim: `RSW_DW_Race_OuterRim_CommandoDroid` (label "BX Commando Droid",
  `Defs/Races_OuterRim.xml`, `bodySize` 1, `baseHealthScale` 0.8), head type
  `RSW_DW_HeadType_OuterRim_CommandoDroid`, textures at
  `Textures/OuterRim/Droid/BX/{Body,Head}/`.
- Droids are **not xenotypes**; nothing here is in `RimMandrakeXenotypes.xml`.

## Canon variants this chassis covers

**One index row**: `BX-series droid commando`
(https://starwars.fandom.com/wiki/BX-series_droid_commando), continuity **canon
(+Legends)**. The article names sub-types that have no index row of their own and no repo
art: **Commando Droid Diplomat** (brown, yellow and blue plating), **commando droid
captain** (white identifiers on head and chest), and the **cortosis-plated** BX units used
as security in the Spire prison on Stygeon Prime.

## Sourced text (Wookieepedia)

Also called BX-series commando droids, BX commando droids, BX droids, or simply **commando
droids**. Advanced commando battle droids used by the CIS during the Clone Wars, designed
for **infiltration and action behind enemy lines**, and also used for **security,
bodyguard and enforcer duties** for high-ranking Separatists. Infobox: **1.91 meters**
(6 ft 3 in), plating **black, or light-gray**, sensors **white**, class **battle droid**,
degree **fourth-degree**, manufactured by **Baktoid Combat Automata** and the
**Confederacy of Independent Systems**. Armament: E-5 blaster rifle, thermal detonator,
**vibrosword**, **BX Sniper Rifle**, RPS-6 rocket launcher, **droid commando personal
shield**, electrostaff.

BX units are **more adaptable, smarter and much sturdier than B1s**, programmed with
improved combat tactics and battlefield awareness, and fitted with **glowing white
photoreceptors**. The body is **titanium-reinforced steel** acting as blaster-resistant
armour, and **even the internal components are shielded**. Heavy armour lets one
**withstand several direct hits from a DC-15A blaster carbine**, though a point-blank
headshot from an ELG-3A blaster pistol destroys one instantly. They are **extremely agile
and acrobatic** — midsection armour is more flexible than a B1's, they move and react much
faster, perform multiple flips, and **keep fighting after severe damage**, including
having their legs cut off with a lightsaber; contrast the B1, which can be defeated by
simply knocking it over. They are strong enough to lift a person by the neck (done to
Captain Rex, to Morgan Elsbeth, and to Crosshair). They are skilled melee fighters with
**vibroswords**.

🔑 **A more compact head than the B1** is the canon reason a commando droid **can wear
Phase I clone trooper armor** for infiltration. They can also **alter their vocabulators
to imitate clone troopers** — the ruse is detectable by awkward movement in the armour and
atypical responses to orders (the giveaway being the battle-droid "roger, roger").

Programming is explicitly for **combat, clandestine infiltration and assassination**.
Ruthless and lethal; multiple squads can turn a battle, and they can **put a Jedi on the
back foot** and match the most skilled clones. Their **hefty price tag prevented mass
production**, which is why the B1 remained the CIS standard infantry. Considered "new" in
22 BBY and undergoing preliminary testing early in the Clone Wars, though one unit claimed
to have been built five "cycles" before the war began.

Later service: the BX **ND-5** is a named post-war individual (companion to Kay Vess) who
recalls that as a battle droid he cared only about following orders and destroying targets.

## Provenance

- **Manufacturer**: **Baktoid Combat Automata**; the **Confederacy of Independent
  Systems** is also listed as a manufacturer in the infobox.
- **Era**: **blank** — the article's `firstmade=` and `retired=` infobox fields are
  literally empty. The in-text "new in 22 BBY" and "built five cycles before the Clone
  Wars" are narrative statements, recorded above as such and deliberately **not** promoted
  into an era field.
- **Typical owners**: Confederacy of Independent Systems (Separatist Droid Army);
  **Hutt Clan** — Ziro the Hutt's criminal organization and Jabba's criminal empire;
  **Cad Bane's group**; Separatist holdouts (including the Desix holdout); **Bedlam
  Raiders**; Tech Masters; Darth Vader's secret forces. Post-war criminal and holdout use
  is unusually broad for a Separatist droid, which makes the BX the most plausible of these
  six chassis to appear in a scavenger-era campaign.

## Visual brief

**The repo sprite matches canon well, including a detail a text prompt would miss.**
`donor_current_sprite.png` (JDS, 128×128, top-down) shows a **near-black body with
copper/brown accents at the shoulder, elbow and knee joints**, a compact rounded head with
**two pale white photoreceptors**, and a **small red dot on the chest**. The canon render
(`wookieepedia_infobox.png`) independently shows exactly that combination: dark
grey-purple plating with **burnt-orange/copper joint segments** at shoulders, upper arms,
elbows, hips and knees, **white slit photoreceptors**, and a **red dot on the chest**. The
copper joints are the single most distinctive BX colour cue and the repo already has them.

- The canon render's proportions: **slim and human-proportioned**, standing upright, with a
  **smooth compact rounded helmet-like head** set on a short neck, a flat armoured chest
  plate, and long straight legs. It reads far more like an athletic humanoid than the B1
  does.
- 🔴 **Head shape is the one thing to watch.** Canon's defining BX trait is a head
  **compact enough to fit inside a Phase I clone helmet** — short, rounded, no long
  muzzle. The repo sprite's head is rounder and shorter than the repo B1's, so the
  distinction is present, but it still carries a small forward snout. If the owner wants
  the BX to read as "could pass for a clone from behind," shortening that snout further is
  the correction.
- 🔴 **Do not lighten it toward the B1 palette.** Canon plating is **black or light-gray**
  with copper joints — never the B1's bone/tan. The near-black repo body is right. The
  contrast with the tan B1 is a large part of how a player tells an elite unit from cannon
  fodder at a glance.
- **No repo art exists** for the Commando Droid Diplomat (brown/yellow/blue), the white
  head-and-chest identifiers of a commando droid captain, or the cortosis-plated Spire
  units. All three are marking/paint changes on an already-correct silhouette, so they are
  the cheapest variant art in this whole batch.


## Must show
- [ ] Near-black (or light-gray) body plating, not the B1's tan/bone
- [ ] Copper/burnt-orange accent segments at shoulder, elbow, and knee joints
- [ ] Compact, smooth, rounded helmet-like head with no long muzzle/snout
- [ ] Two pale white photoreceptors
- [ ] Small red dot on the chest

## Engine limits
none known

## Source URLs

- https://starwars.fandom.com/wiki/BX-series_droid_commando — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=BX-series_droid_commando&format=json&prop=wikitext`
  (rendered HTML is Cloudflare-walled, the API is not). Sections read: `{{DroidSeries}}`
  infobox, lead, Characteristics, and the opening of History. The remainder of History,
  the Equipment section, Specialized BX-series commando droids, and Behind the scenes were
  **not** read in full — the Diplomat, captain and cortosis details above come from the
  Characteristics section, not from the Specialized section.
- https://static.wikia.nocookie.net/starwars/images/2/27/CommandoDroid-TCWCEJtB.png
  (File:CommandoDroid-TCWCEJtB.png → `wookieepedia_infobox.png`)

## Candidate images

- `wookieepedia_infobox.png` — the article infobox: full-body render of a BX commando in a
  running/lunging pose holding a rifle, on transparent background. Authority for the
  copper joint accents, white slit photoreceptors, red chest dot, compact head and slim
  human proportions.
- `donor_current_sprite.png` — the repo's current JDS BX commando pawn sprite
  (`design/Jawa/fauna/sprites/JDSCIS_BX_Commando_Droid.png`, 128×128, top-down). Live
  shipping art, not a corpse variant.

## ruling

(empty — owner has not reviewed this chassis yet)
