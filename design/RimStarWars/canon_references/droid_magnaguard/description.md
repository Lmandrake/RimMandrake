# IG-100 MagnaGuard (repo chassis: MagnaGuard, JDS + OuterRim)

**defName**: two defs across two donor mods.
- JDS: `RSW_DW_Race_JDSCIS_IG-100_MagnaGuards` (ThingDef, `Defs/Races_JDS.xml`,
  **`bodySize` 0.7**) with PawnKindDef `RSW_DW_JDSCIS_IG-100_MagnaGuards`
  (`Defs/PawnKinds_JDS.xml`). Note the plural "MagnaGuards" in both defNames and labels.
- OuterRim: `RSW_DW_Race_OuterRim_MagnaGuardDroid` (label "MagnaGuard Droid",
  `Defs/Races_OuterRim.xml`), head type `RSW_DW_HeadType_OuterRim_MagnaGuardDroid`,
  textures at `Textures/OuterRim/Droid/Magnaguard/{Body,Head}/`.
- Droids are **not xenotypes**; nothing here is in `RimMandrakeXenotypes.xml`.

## Canon variants this chassis covers

**One index row**: `IG-100 MagnaGuard`
(https://starwars.fandom.com/wiki/IG-100_MagnaGuard), continuity **canon (+Legends)**.
There is no separate index row for a MagnaGuard sub-model; canon instead varies them by
**colour** (see below).

## Sourced text (Wookieepedia)

The **IG-100 MagnaGuard** — also the **MagnaGuard**, the **magnadroid**, or, from
development, the **Prototype Self-Motivating Heuristically Programmed Combat Droid** — is
a **bodyguard droid** and type of battle droid created by **Holowan Mechanicals**, part of
Holowan Laboratories. Infobox: **1.95 meters** (6 ft 5 in) and **123 kilograms**; sensor
colours **red** and **yellow** (purple under Scourge infection); classes **assassin droid,
battle droid, bodyguard droid**; armament **electrostaff**, RPS-6 rocket launcher,
precision laser dart, **electro-whip**.

They were **a favourite of General Grievous**, who used them as his bodyguards during the
Clone Wars, and also accompanied other high-ranking Separatists including **Count Dooku**.
Their **electrostaffs can be used against Jedi lightsabers**, and they can **keep fighting
after losing one or several limbs, or even their heads**. They are a match for the most
skilled Jedi — one backed Obi-Wan Kenobi into a corner. They also **pilot *Rogue*-class
Porax-38 starfighters** and use blasters and RPS-6 rocket launchers. **They usually fight
in pairs: one occupies the Jedi's lightsaber while the other attacks the unguarded flank
or rear.** The presence of MagnaGuards signals that high-ranking commanders are present,
and gives them **automatic authority over other battle droids** deployed.

🔑 **Appearance is deliberate intimidation, and it is Kaleesh.** The droid was **designed
to look intimidating**; each model is distinguished by a **colour: black, alabaster, blue,
or gray**, with **dull red or yellow glare** from the photoreceptors, expressionless faces
and sheer physical mass. The **head was modelled on the legacy Krath war droids**. Built to
Grievous's own specifications, MagnaGuards **resemble the Kaleesh warriors of his past**.
🔴 Just as his facemask honours his Kaleesh past, **Grievous ordered his MagnaGuards
outfitted with cloaks bearing mumuu markings and half-hoods**, in honour of his original
Izvoshra bodyguards and the traditions of Kalee — and to look more menacing still.

Two things in the development name mark them out from typical battle droids: they are
**self-motivated and require no droid control programming**, completing assigned tasks
sensibly and overcoming obstacles cleverly; and they are **heuristically programmed**, so
they **learn from experience**. Grievous personally trained them in everything he had
learned and used them as sparring partners; survivors carry **dents and scars** from that
training regimen. Their success led Dooku to adopt them as bodyguards too. Grakkus later
describes them as "relics of the Clone War, designed to battle Jedi Knights."

## Provenance

- **Manufacturer**: **Holowan Mechanicals**, a part of **Holowan Laboratories**. Designed
  to General Grievous's specifications.
- **Era**: **blank** — the article's `firstmade=` and `retired=` infobox fields are
  literally empty. Nothing is inferred from the Clone Wars setting.
- **Typical owners**: **Confederacy of Independent Systems** (Separatist Droid Army) —
  in practice **General Grievous** personally and **Count Dooku**; later the **Infinite
  Coil**, the **Bedlam Raiders**, the **Scourge** (as a vessel), and **Zahra's raider
  crew**. Grakkus the Hutt kept some post-war. Like the BX, this chassis has real
  post-Clone-Wars criminal ownership, so it is campaign-plausible outside a Separatist
  context.

## Visual brief

**The repo sprite gets the head right and omits the cloak, which is the largest single
silhouette element in canon.** `donor_current_sprite.png` (JDS, 128×128, top-down) shows a
**silver-grey** droid with a distinctive head: a **helmet-like crown over two large round
red photoreceptors** and a **vertical ribbed grille/muzzle** below them, plus a **large red
dot centred on the chest**. Shoulders are rounded pads, the torso tapers to a narrow
waist, and the legs read as splayed. The head and the red-eye pair are unmistakably
MagnaGuard and match the reference closely.

- 🔴 **The cloak and half-hood are missing.** In `wookieepedia_infobox.png` the
  MagnaGuard's outline is dominated by a **heavy pale cloak with a half-hood** hanging from
  the shoulders down past the knees, bearing a green **mumuu** marking on the chest panel.
  Canon states Grievous *ordered* this specifically. From directly above, a cloak is
  exactly the kind of feature that changes a RimWorld silhouette most — it would broaden
  and soften the outline and make the droid read as a robed figure rather than a bare
  frame. The repo sprite is a bare, uncloaked MagnaGuard. Whether that is acceptable is
  the owner's call, but it should be a call, not an accident. (RimWorld has an apparel
  layer, so a cloak could also be authored as apparel rather than baked into the body.)
- Canon proportions from the reference: **tall, lean and long-limbed** with **dark
  blue-grey plate over a white/alabaster underlayer**, heavy scuffing and battle scarring
  on every panel, **thin exposed cabling at the joints**, a **red sensor dot on the chest**,
  and **hoof-like splayed feet**. The scarring is canon-supported — survivors carry dents
  and scars from sparring with Grievous — and none of it appears on the clean repo sprite.
- **Colour is a free choice within canon**: black, alabaster, blue or gray are all attested,
  so the repo's grey is legitimate and needs no correction. **Eyes may be dull red *or*
  yellow**; the repo uses red, also legitimate.
- ⚠️ **Possible def-versus-canon inversion**: canon makes the MagnaGuard the **tallest
  (1.95 m) and heaviest (123 kg)** of the six Separatist chassis in this batch, yet
  `RSW_DW_Race_JDSCIS_IG-100_MagnaGuards` sets **`bodySize` 0.7** — the same value as the
  JDS B2 and below the RimWorld human baseline of 1.0, while the OuterRim B1 and BX both
  get 1.0. Reported, not fixed; a reviewer should confirm what the Droidworks parent def
  contributes before treating it as a bug.
- **No repo art** depicts the electrostaff, but in RimWorld terms that is a weapon, not
  body art, so it is not a sprite defect.


## Must show
- [ ] Helmet-like crown over two large round red or yellow photoreceptors, with a vertical ribbed grille/muzzle below
- [ ] Red sensor dot centred on the chest
- [ ] Heavy pale cloak with a half-hood hanging from the shoulders down past the knees
- [ ] Visible battle scarring/scuffing and thin exposed cabling at the joints
- [ ] Hoof-like splayed feet

## Engine limits
none known

## Source URLs

- https://starwars.fandom.com/wiki/IG-100_MagnaGuard — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=IG-100_MagnaGuard&format=json&prop=wikitext`
  (rendered HTML is Cloudflare-walled, the API is not). Sections read: `{{DroidSeries}}`
  infobox, lead, and the opening of Characteristics. The rest of Characteristics and the
  whole of History (Twilight of the Republic through Age of the Empire) were **not** read.
- https://static.wikia.nocookie.net/starwars/images/e/eb/MagnaGuard-SWCTP.png
  (File:MagnaGuard-SWCTP.png → `wookieepedia_infobox.png`)

## Candidate images

- `wookieepedia_infobox.png` — the article infobox: full-body render of a cloaked
  MagnaGuard in a fighting stance holding an active (purple-crackling) electrostaff
  two-handed, on transparent background. Authority for the cloak and half-hood, the
  mumuu marking, the red twin photoreceptors and grille face, the blue-grey-over-alabaster
  plating, the battle scarring, and the hoof-like feet.
- `donor_current_sprite.png` — the repo's current JDS MagnaGuard pawn sprite
  (`design/Jawa/fauna/sprites/JDSCIS_IG-100_MagnaGuards.png`, 128×128, top-down). Live
  shipping art, not a corpse variant.

## ruling

(empty — owner has not reviewed this chassis yet)
