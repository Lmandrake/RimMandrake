# KX-series security droid (repo chassis: KX-series, OuterRim)

**defName**: droids are **not xenotypes**; nothing here is in `RimMandrakeXenotypes.xml`.
Real defs on disk, all in the Droidworks OuterRim donor set:
- `RSW_DW_Race_OuterRim_KXSecurityDroid` — label "KX Security Droid"
  (`src/RimStarWars/Droidworks/Defs/Races_OuterRim.xml:336`), `baseBodySize` **1**,
  `baseHealthScale` **1.2**, `MoveSpeed` **4.8**
- `RSW_DW_HeadType_OuterRim_KXSecurityDroid` (HeadTypeDef, same file, :33)
- PawnKinds in `Defs/PawnKinds_OuterRim.xml`: `RSW_DW_OuterRim_KXSecurityDroid` (:103) and
  `RSW_DW_OuterRim_ImperialKXSecurityDroid` (:370) — **two pawnkinds, one race, both labelled
  "KX Security Droid"**

Sprites: `src/RimStarWars/Droidworks/Textures/OuterRim/Droid/KX/Body/Naked_Male_{south,east,north}.png`
and `KX/Head/Head_{south,east,north}.png`, each with a matching `…m.png` mask. 256×256, three
directions only (west is mirrored from east, the OuterRim convention).

⚠️ **Do not confuse this with `RSW_DW_Race_guy762_DroidRace_KX12UPD` /
`_KX12APD`** in `Defs/Races_KotOR.xml:450,507` — those are the **K-X12 utility probe droid**,
an unrelated KotOR-donor model that merely shares the letters "KX". Different chassis,
different sprites (`KotOR/Droid/KX12/KX12`), not covered by this entry.

## Canon variants this chassis covers

One row in `DROIDS_INDEX.md:992` — **KX-series security droid**, marked `canon`. No other canon
row maps to this chassis.

The article itself names sub-forms the repo does **not** distinguish:
- **Security Droid Enforcer** — a variant existing by 9 BBY with **tan plating rather than
  black**, an electro riot baton, and a reinforced chassis; explicitly "far more dangerous than
  the standard model," built primarily to train stormtroopers in electrobaton use. If the repo
  ever wants a second KX pawnkind that reads differently, this is the canon one to build, and
  the tan repaint is nearly free.
- **KXFO-series security droid** — the First Order's model. The KX article's `{{Youmay}}`
  hatnote points at it as a **separate article**, i.e. a different model, not a KX variant.
  Not in this repo, not covered here.

## Sourced text (Wookieepedia)

**KX-series security droids**, also known as **KX-series enforcer droids**, **KX enforcer
droids**, **KX units**, **KX droids**, or **executor droids**, were a model of security droid
manufactured by **Arakyd Industries** in service to the Galactic Empire during the Galactic
Civil War.
[KX-series security droid](https://starwars.fandom.com/wiki/KX-series_security_droid)

🔑 **Height is stated, and it is the fact this entry exists for: 2.16 meters** (infobox, cited
to *Star Wars: Absolutely Everything You Need to Know, Updated and Expanded*). That is well
over a tall human. **Mass is not given** — the infobox `mass=` field is empty. Cost is
**50,000 credits** (*Dawn of Rebellion*).

Infobox specifics: class **security droid**; degree **fourth-degree droid**; plating
**carboplast**; sensor colour **white** (and **purple** while under Scourge infection, from
*Dark Droids* 1); gender **masculine programming**, with feminine programming also attested.
`firstmade=` and `retired=` are both **empty** in the wikitext.

**Appearance, from the body text.** "They had a **black-colored body designed with exaggerated
human proportions** but with the **mobility of a human athlete.**" The shell around the head's
cognitive module and the fists were **carboplast composite**. Their **upper legs had shock
absorbing struts**; the **ring joints in their knees included a servo driver**; a complex
**gyro-balance system** kept them walking upright. The **Imperial crest was imprinted on the
side of each shoulder**, and one shoulder crest could be **emblazoned in gold** for a droid of
enhanced status. Built-in comm package, recharge port, chest-mounted **olfactory sensors**, and
a **Scomp-link data spike hidden in the fist**.

**Behaviour.** Programmed to speak and interact with people but **not as proficient at it as
protocol droids**; they could fail to understand a statement by **processing it as an order to
be taken literally.** They could escort dignitaries, protect important people and defend
Imperial installations, and were pre-programmed in the operation of **more than forty Imperial
transport vehicles**. Beyond security work they could do manual labour and translation, but
their programming made them **find those tasks tedious**. Their size and strength made them
**intimidating and unsettling to Imperials and rebels alike**.

🔑 **The regulatory dodge, which is a repo-relevant pattern.** The Imperial Senate had
prohibited the creation of **battle droids**, so Arakyd **used a loophole by marketing the
KX-series as "security droids."** They were **programmed without the standard restriction
against harming organic sentient lifeforms**, and were programmed to **recognise and defer to
Imperial Military officers ranked lieutenant or higher.** (Structurally the same trick the HK
entry records for Czerka's assassin-as-protocol-droid framing — worth noting that canon uses it
twice.)

**Armament** (infobox, each separately cited): E-11 medium blaster rifle; E-22 reciprocating
double-barreled blaster rifle; electro riot baton; T-21 light repeating blaster; sonic grenade.
So the chassis is a **carrier of ordinary infantry weapons**, not an integral-weapon droid —
unlike the droideka or the LR-57.

**History points actually dated in the article:** deployed **as early as 18 BBY**; used to guard
the Imperial Refinery on Kashyyyk, the mining headquarters on Ilum, and Fortress Inquisitorius
on Nur; a large group destroyed by Cal Kestis on Ilum; several stationed on the beaches of
Niamos in **5 BBY**; **six** participated in the **Ghorman Massacre**, one of which was
**K-2SO**, damaged when Ghorman Front operative Samm hit it against a wall with a troop
transport and then salvaged and reprogrammed by Cassian Andor.

**⚠️ Not read this pass:** the article is 36,942 characters and carries an
`{{Expand|all sections}}` banner (Wookieepedia's own flag that its sections are incomplete).
Sections read in full: infobox, lead, Description, and History through the Galactic Civil War.
The remainder of History, "Behind the scenes" and Appearances are **UNREAD, not absent.**

## Provenance

- **Manufacturer:** **Arakyd Industries** (cited to *Star Wars: Commander*).
  [KX-series security droid](https://starwars.fandom.com/wiki/KX-series_security_droid)
- **Era:** **blank.** The infobox `firstmade=` and `retired=` fields are literally empty. The
  dated in-text events above (18 BBY deployment, 9 BBY Enforcer variant, 5 BBY Niamos) are
  narrative and are **not promoted into this field**, per the brief.
- **Typical owners:** **Galactic Empire** — Imperial Military, Imperial Security Bureau, the
  Inquisitorius; **Alliance to Restore the Republic** (*appropriated*) and **Rogue One**
  (*appropriated*); Second Revelation; the Droid uprising; the **Scourge** (as a vessel); the
  **New Republic**; the Brotherhood of Wire and Bone; the **Droid Gotra**; The Twins.
  [same article, infobox `affiliation`]
  Note the index row (`DROIDS_INDEX.md:992`) lists only the first four of these; the infobox
  carries more.

## Visual brief

🔴 **The donor sprite is white-and-grey; canon KX plating is black. The def fixes it, and the
raw PNG must never be judged on its own.** `Races_OuterRim.xml:366–384` sets both `skin` colour
channels to `RGBA(20,20,20,255)` — near-black — at weight 100 with no alternative option. That
is a **good canon match** to "a black-colored body" and to every reference image. The sprite is
a maskable greyscale asset (`Naked_Male_southm.png`, `Head_southm.png` exist alongside).
**Judge this chassis tinted near-black, exactly as the HK entry warns for its KotOR donor.**

**`wookieepedia_kx_infobox.jpg` is the proportion authority, and the proportions are the whole
point of this chassis.** What it shows, and none of it survives into a RimWorld top-down sprite:

- **A hunched, forward-leaning stance.** The droid does not stand upright like a battle droid;
  the shoulders carry forward and the neck cranes down and out. This is the single most
  recognisable KX cue on screen.
- **A large, smoothly domed dorsal/shoulder carapace** that sits *above and behind* a
  comparatively **narrow, skeletal torso** — the visual mass is in the shoulders, not the chest.
  The **Imperial crest is clearly stencilled on the shoulder plate**, weathered and scuffed.
- **Extreme limb length.** The arms hang past the knee; the legs are two long thin tubes with
  **prominent exposed ring joints at knee and ankle**, matching the sourced "shock absorbing
  struts" and "ring joints … servo driver." The hands are **long, thin, multi-jointed and
  splayed**, with visibly more finger length than a human hand.
- **A small, smooth, egg-shaped head** on a thin neck, with **two small round pale
  photoreceptors** set wide and a narrow slotted mouth grille below. The head is the *least*
  massive part of the droid.
- **Almost no colour at all**: matte black-to-charcoal with grey scuffing and a single thin gold
  arc on the shoulder carapace. No emissive treatment on the eyes in this render — consistent
  with the infobox's **white** sensor rather than a glow.
- **Non-humanoid feet**: flat splayed pads, not boots.

**What the repo sprites show:**

- `donor_current_sprite.png` (KX body, `south`, 256×256, top-down) reads as a **broad rounded
  torso with heavy dark shoulder wedges** and a light central chest panel — i.e. it puts the
  mass in the shoulders, which is *directionally* right for the dorsal carapace. But it is a
  **squat, wide, human-width torso**: nothing in it reads as gaunt, and the 2.16 m height and
  spindly limbs are absent.
- `donor_current_sprite_head.png` (256×256) is a **tall rounded arch outline with a slotted
  mouth grille and no visible eyes**. The arch silhouette is a reasonable read of the smooth
  egg head from directly above; the **two pale photoreceptors, the strongest facial cue in
  canon, are not drawn.**
- `donor_body_east.png` is the profile frame and shares the same broad-torso proportions.
- 🔴 **The forward hunch cannot be shown top-down**, so the chassis' defining posture is
  structurally unavailable in this art format. If the owner wants KX to read as KX, the
  available levers are the **shoulder-carapace overhang** (draw it overlapping forward past the
  chest), the **long splayed hands** at the sprite's edges, and the **shoulder Imperial crest**
  — which the current sprite's light chest panel does not carry.
- ⚠️ **`baseBodySize` is 1** — the same value the repo gives a 1.83 m droideka — for a droid
  canon states at **2.16 m**. Flagging, not fixing: if body size is doing any work as an
  in-world scale cue, this chassis is undersized relative to its own sourced height.


## Must show
- [ ] Near-black plating
- [ ] Large, smoothly domed dorsal/shoulder carapace with an Imperial crest stencilled on the shoulder plate
- [ ] Extreme limb length — arms hanging past the knee, legs with prominent exposed ring joints at knee and ankle
- [ ] Small, smooth, egg-shaped head with two small round pale photoreceptors and a narrow slotted mouth grille
- [ ] Thin gold arc accent on the shoulder carapace

## Engine limits
The forward-hunched stance is the chassis' defining posture and cannot be shown in a top-down sprite — it is structurally unavailable in this art format.

## Source URLs

- https://starwars.fandom.com/wiki/KX-series_security_droid — main article; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=KX-series_security_droid&format=json&prop=wikitext`
  (36,942 chars; infobox + lead + Description + History-to-Galactic-Civil-War read, remainder
  **unread**). Rendered HTML is Cloudflare-walled; the API is not.
- Named in the article, **not fetched this pass**:
  https://starwars.fandom.com/wiki/KXFO-series_security_droid ·
  https://starwars.fandom.com/wiki/Security_Droid_Enforcer ·
  https://starwars.fandom.com/wiki/K-2SO
- https://static.wikia.nocookie.net/starwars/images/f/fb/KXseriesSecurityDroid1-SWBC35.png
  (File:KXseriesSecurityDroid1-SWBC35.png → `wookieepedia_kx_infobox.jpg`)
- https://static.wikia.nocookie.net/starwars/images/0/01/KXseriesSecurityDroid-SWBC35.png
  (File:KXseriesSecurityDroid-SWBC35.png → `wookieepedia_kx_stature.jpg`)
- https://static.wikia.nocookie.net/starwars/images/e/e5/SecurityDroidsIlum.png
  (File:SecurityDroidsIlum.png → `wookieepedia_kx_group_ilum.jpg`)
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_OuterRim.xml`,
  `src/RimStarWars/Droidworks/Defs/PawnKinds_OuterRim.xml`

## Candidate images

- `wookieepedia_kx_infobox.jpg` (590×1490) — the article infobox: full-body three-quarter render
  on transparent background, hunched forward, matte black. **The proportion and colour
  authority for this chassis.**
- `wookieepedia_kx_stature.jpg` (575×1480) — the article's "KX executor droids had an
  intimidating stature" plate; a second full-body render, same chassis, confirming the hunch and
  the limb length independently.
- `wookieepedia_kx_group_ilum.jpg` (1741×580) — a group of KX units from the Ilum Imperial
  garrison, in-game lighting. Shows the chassis at squad scale rather than as an isolated
  render.
- `donor_current_sprite.png` / `donor_current_sprite_head.png` (256×256 each) — the OuterRim
  donor body and head, `south`. **Greyscale/maskable; must be judged tinted with the def's
  `RGBA(20,20,20)` channels, not as the raw white PNG.**
- `donor_body_east.png` (256×256) — the profile frame.

## ruling

(empty — the owner has not reviewed this chassis yet)
