# DUM-series pit droid (repo chassis: DUM pit droid, OuterRim)

**defName**: droids are not xenotypes. Real defs on disk:
- `RSW_DW_Race_OuterRim_DUMDroid` — label "DUM Repair Droid",
  `ParentName="DW_Family_Labour"`, `baseBodySize` 0.75, `MoveSpeed` 5.2
  (`src/RimStarWars/Droidworks/Defs/Races_OuterRim.xml:881`)
- `RSW_DW_OuterRim_DUMDroid` — PawnKindDef, `combatPower` 99999, forced trait
  `Industriousness 1` (`Defs/PawnKinds_OuterRim.xml:256`)
- `SWCP_DroidNamer_DUMpitdroid` — RulePackDef for its names
  (`Defs/Absorbed_KotorCore/Absorbed_KotorCore_RulePacks_DroidNameMakers.xml:104`)
- Head type `RSW_DW_HeadType_Blank`; the whole droid is the body graphic.

Sprites: `src/RimStarWars/Droidworks/Textures/OuterRim/Droid/DUM_{north,south,east}.png` —
three 256×256 frames, graphic path `OuterRim/Droid/DUM`. 🔑 **The PNGs are near-white
greyscale and must be judged tinted, not raw**: the def's `skin` colour channel is
`RGBA(112,68,55,255)` on both `first` and `second`, i.e. a **mid rust-brown**. There is no
`_m` mask file for DUM (unlike GNK and SalvageAssist, which ship `*m.png`), so it is a
single flat tint over the whole body.

## Canon variants this chassis covers

- **DUM-series pit droid** — a.k.a. simply *pit droid* (`DROIDS_INDEX.md:579`, marked
  `canon (+Legends)`). One row, one chassis. Named individuals in canon (**WAC-47**,
  **G-LN**, Peli Motto's three, Ody Mandrell's team) are characters on this chassis, not
  separate models, and are not separate index rows.

## Sourced text (Wookieepedia)

The **DUM-series pit droid** was a model of **repair droid** manufactured by
**Serv-O-Droid, Inc.**, **Class 5**, and had **already been in use for about two centuries
by the time of the Invasion of Naboo**.
[DUM-series pit droid](https://starwars.fandom.com/wiki/DUM-series_pit_droid)

Sourced appearance, size and behaviour, all from that article:

- **1.19 meters tall** (3 ft 11 in). Short — chest height on a human.
- **Sensor colour: black.** (Also **purple while under Scourge infection** — a real sourced
  alternate, from *Doctor Aphra* (2020) 37.) The infobox gives **no plating colour**.
- 🔑 **They fold into a compact form when not in use, and the fold is toggled by tapping
  the droid's "nose."** This is the single most distinctive thing about the chassis and it
  is fully sourced (*The Phantom Menace*).
- **Cheap, expendable, and incredibly durable.** **Encased in hardened alloy casings that
  allowed them to endure the harsh weather on Tatooine.** 🔑 This is the campaign-relevant
  fact: canon explicitly builds this droid for a desert world's weather.
- **Able to lift objects several times their own weight.**
- **Programmed with a sense of urgency**, but **minimal logic processors prevented them
  from completing complex tasks**. At the Mos Espa Grand Arena they refuelled vehicles,
  reached tight spaces, and made simple wire connections.
- **If one could not reach what it needed to work on, it recruited other pit droids into an
  unstable, haphazard droid pyramid.** **Fearless** — "happy to throw themselves into
  danger."
- Sourced comic beat: one was **sucked into the intake of Ody Mandrell's podracer** at the
  Boonta Eve Classic (32 BBY). **The droid survived; the engine did not.**
- Peli Motto, quoted: *"You know, it's costing me a lot of money to keep these droids even
  powered up."*
- Post-Empire reuse is sourced and broad: dock repairs at Mos Eisley, **a bartender on a
  space station**, green-liveried units renting hydroskiffs at the Veelo Docks, labor and
  loader work aboad the *Colossus*, and a member of a **parts-stealing gang** on Garel
  (3 BBY).

⚠️ The article carries `{{Expand|all sections}}` — the wiki itself flags it as incomplete.
Sections read in full: infobox, lead, Characteristics, History, Behind the scenes.

## Provenance

- **Manufacturer:** **Serv-O-Droid, Inc.**
  ([article](https://starwars.fandom.com/wiki/DUM-series_pit_droid) infobox
  `manufacturer=`, cited to *Star Wars Character Encyclopedia: Updated and Expanded*).
  `DROIDS_INDEX.md:579` agrees.
- **Era:** **blank.** `firstmade=` and `retired=` are empty in the wikitext. The article's
  own dated statement — in use "for about two centuries" by the Invasion of Naboo, with
  `232 BBY` linked — is narrative text, not an infobox era, and is not promoted here.
- **Typical owners:** **Galactic Republic**; **Alliance to Restore the Republic**;
  **Scourge** (marked in the infobox as *"as a vessel"* — i.e. infected hosts, not owners);
  the **Colossus** (infobox `affiliation=`, same article). In-text also: podracer pit crews
  on **Tatooine** (Ody Mandrell), independent mechanics (**Peli Motto**, Mos Eisley),
  **Skraik's gang** on Garel, and the Veelo Docks. **No Separatist affiliation is sourced** —
  this is a Republic/civilian/underworld droid, which makes it the most plausible of these
  six as legitimately-owned Jawa salvage stock.

## Visual brief

**Overall shape and proportion — the whole read at sprite scale.** Canon is a **spindly
skeletal biped, roughly a metre tall, whose head is a wide flat flared cone — a conical
hat, or an arrowhead — much wider than the body beneath it.** Under the brim, at the front,
sits **one large single dark round photoreceptor** on a short stalk neck. **Two long thin
whip antennae** rise from the crown. Everything below is thin: a small boxy chest, a narrow
segmented waist, long tubular arms ending in **three-fingered claws that hang past the
hips**, long legs with prominent ball knee-joints, and **broad flat splayed feet**. There is
almost no mass anywhere except the head. At any distance it reads as **a wide dark chevron
balanced on two sticks**, with two hairlines above it.

**The repo sprite gets the identity cue right and loses the limbs.**

- ✅ **The hat-brim silhouette is the correct read and the sprite nails it.** The wide flared
  cone over a narrow body dominates `donor_current_sprite.png`, exactly as it dominates
  canon. Of the six droids in this batch this is the strongest silhouette match. At three or
  four pixels tall this is still legible as "wide hat, thin body" and nothing else in the
  game looks like it.
- ✅ **One large black eye, centred under the brim** — and the infobox sources **sensor
  colour: black**. The sprite draws it as a solid black disc. Correct, and it is the only
  high-contrast feature, so it carries the read at small size.
- ✅ **Two antennae.** Canon has two thin whips from the crown; the sprite has two. Keep
  them: with the brim, they are the whole signature.
- ✅ **Tint colour is a good canon match.** `RGBA(112,68,55)` is a mid rust-brown; every
  reference image shows weathered coppery-brown/rust plating (`wookieepedia_infobox.png` is
  a dusty grey-brown, `wookieepedia_reddish_clonewars.png` is a distinctly reddish-copper
  brown). **Judge this sprite tinted; the raw PNG is white and misleading.**
- ✅ **Def scale is roughly right.** `baseBodySize` 0.75 against a canon **1.19 m** versus a
  human's ~1.8 m (ratio ≈ 0.66) — slightly generous but defensible, and unlike the DSD1 it
  is not a contradiction. `MoveSpeed` 5.2 (fast) agrees with the sourced "sense of urgency".
- 🔴 **The arms are gone.** Canon's long dangling thin arms with three-fingered claws are
  its second-strongest cue, and they read at small size because they break the outline on
  both sides. The sprite truncates them into shoulder stubs — the south frame has no arm
  outboard of the body at all, and the east frame shows one short rectangular block. The
  droid consequently reads as a *mushroom* rather than a *biped*. If one correction is made,
  it is **long thin arms hanging clear of the body**.
- 🔴 **No folded/compact form exists on disk in any frame.** Canon's defining trick —
  folding down when idle, toggled by tapping the nose — has no art, and would need a second
  graphic set plus a state to switch on, exactly as the droideka's ball form does. Flagged
  as a **content** gap, not just an art gap.
- ⚠️ **The eye is centred in the brim rather than set forward on a neck.** Canon puts the
  lens on a short stalk projecting *forward and down* from under the front of the cone, so
  the head reads as "hat + separate eye pod". The sprite fuses them into one disc on one
  dome. Minor at sprite scale, but it is why the sprite reads slightly cuter and rounder
  than canon's angular, brittle-looking original.
- ⚠️ **Legs are short and fused.** Canon's legs are long, visibly double-jointed, with big
  ball knees and broad splayed feet; the sprite gives a single tapering skirt with a small
  foot block. The `north` frame is the weakest of the three — with no eye to anchor it, it
  is an unreadable white cone.
- The purple **Scourge-infected** sensor variant is sourced but has **no repo art**, and
  nothing in this repo depicts the droid-pyramid behaviour.


## Must show
- [ ] Wide flared cone-shaped head, much wider than the body beneath it
- [ ] One large black photoreceptor centred under the brim
- [ ] Two long thin whip antennae rising from the crown
- [ ] Rust-brown/copper weathered plating tint
- [ ] Long thin arms hanging clear of the body, ending in three-fingered claws
- [ ] Long legs with prominent ball knee-joints and broad flat splayed feet

## Engine limits
none known

## Source URLs

- https://starwars.fandom.com/wiki/DUM-series_pit_droid — main article; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=DUM-series_pit_droid&format=json&prop=wikitext`
  (18,446 bytes of JSON, read in full to the Appearances list — no truncation). Article is
  tagged `{{Expand|all sections}}` by the wiki.
- https://static.wikia.nocookie.net/starwars/images/2/21/PitDroid-AG.png →
  `wookieepedia_infobox.png` (480×1340; Fandom served WebP, re-saved as PNG locally)
- https://static.wikia.nocookie.net/starwars/images/a/ac/DUM-series_pit_droid.png →
  `wookieepedia_reddish_clonewars.png` (620×1185; same conversion)
- https://static.wikia.nocookie.net/starwars/images/8/81/PitDroid-Db.png →
  `wookieepedia_with_wrench.png` (510×700; same conversion)
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_OuterRim.xml`,
  `Defs/PawnKinds_OuterRim.xml`,
  `Defs/Absorbed_KotorCore/Absorbed_KotorCore_RulePacks_DroidNameMakers.xml`
- Index row: `design/RimStarWars/canon_references/DROIDS_INDEX.md:579`
- ⚠️ **Not sourceable this pass:** the article's image set contains **no image of the folded
  compact form**, so its exact appearance rests only on the prose ("fold into a compact
  form"). If the owner wants the folded state authored, a further image hunt is owed.

## Candidate images

- `wookieepedia_infobox.png` (480×1340) — the article infobox: full-length three-quarter
  render on transparent background. **The proportion authority.** Shows the wide flared cone
  head, the single dark lens on a forward stalk, two whip antennae, the tiny boxy chest, the
  long thin arms with three-fingered claws hanging past the hips, ball knees and broad
  splayed feet. Dusty grey-brown plating.
- `wookieepedia_reddish_clonewars.png` (620×1185) — captioned by the wiki "a reddish colored
  pit droid during the Clone Wars". **The best colour reference**: distinctly reddish-copper
  brown with a pale green-grey wash on the crown. Supports the def's rust-brown tint.
- `wookieepedia_with_wrench.png` (510×700) — a pit droid inspecting equipment while holding
  a power wrench. Shows the working posture and the claw hand gripping a tool.
- `donor_current_sprite.png` (256×256) — repo `DUM_south`, top-down. **Judge tinted**
  `RGBA(112,68,55)`; the raw file is white greyscale. Best of the three frames.
- `donor_current_sprite_east.png` (256×256) — repo `DUM_east`. Shows the single stub arm.
- `donor_current_sprite_north.png` (256×256) — repo `DUM_north`. The weakest frame: with the
  eye hidden it is an unreadable cone.

## ruling

(empty — the owner has not reviewed this chassis yet)
