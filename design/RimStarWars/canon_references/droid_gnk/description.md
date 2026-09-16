# GNK gonk power droid (repo chassis: GNK gonk, KotOR + OuterRim)

**defName**: not a xenotype. **Only ONE of the two donor sprite sets is actually wired:**
- `RSW_DW_Race_OuterRim_GNKDroid` — label **"gnk power Droid"**,
  `ParentName="DW_Family_Power"`, `baseBodySize` 1.0, `baseHealthScale` 1.0,
  `MoveSpeed` **1.9** (the slowest race in the file), `headTypes` =
  `RSW_DW_HeadType_Blank` — `src/RimStarWars/Droidworks/Defs/Races_OuterRim.xml:981`
- `RSW_DW_OuterRim_GNKDroid` — PawnKindDef, label "gnk power Droid",
  `combatPower` **99999**, `forcedTraits` `Nerves 1`
  (`src/RimStarWars/Droidworks/Defs/PawnKinds_OuterRim.xml:293`)
- Referenced once as a spawn option, `weight 2`, in
  `src/RimStarWars/Droidworks/Defs/IncidentDefs/IncidentDefs_Droidworks.xml:70`
- Carries `RimMandrake.StarWars.Droidworks.CompProperties_DroidDetonation`. The def's own
  comment records the reason — *"the gonk detonates by nature" (BENCH)* — and notes this was
  **the first race to prove that comp's wiring end to end**, which is why every other
  Droidworks race's detonation comment says "GNK proved the wiring."
- There is also a **`RSW_DW_Head_Power`** ThingDef ("power droid head") whose icon is
  `KotOR/UI/Icon_gonk` (`src/RimStarWars/Droidworks/Defs/ThingDefs/Heads_Droidworks.xml:170`)
  — the salvage item, not a pawn.

Sprites (wired): `src/RimStarWars/Droidworks/Textures/OuterRim/Droid/GNK_{south,east,north}.png`
+ `GNK_{south,east,north}m.png` masks, 256×256.

🔴 **The KotOR gonk art is an ORPHAN — no def references it.**
`src/RimStarWars/Droidworks/Textures/KotOR/Droid/gonk/gonk_{south,east,north}.png` plus
`gonk_mask_*` (512×512) exist on disk, but a repo-wide search for `Droid/gonk` / `gonk_south`
across every `.xml` and `.cs` under `src/RimStarWars/` returns **no match**. So although the
index assigns this chassis to "KotOR + OuterRim", only the OuterRim half is live, and the
KotOR half — which is the **higher-quality, higher-resolution art of the two** — is dead
weight. Copied here as `donor_orphan_kotor_gonk.png`. See the visual brief.

## Canon variants this one repo chassis covers — and the two-row question

`DROIDS_INDEX.md` carries **two rows** for this chassis:

| index row | line | continuity | manufacturer | owners |
|---|---|---|---|---|
| GNK power droid | 739 | Legends | Industrial Automaton | Galactic Republic |
| GNK-series power droid | 740 | canon | Industrial Automaton | Galactic Republic; Alliance to Restore the Republic; Scourge (as a vessel); New Republic |

🔑 **Answering the question directly: canon treats these as ONE droid, not two models.** This
is not an assumption — both articles say so in their own first line:

- The canon article opens `{{Top|canon=...}}`… actually `{{Top|legends=GNK power droid/Legends}}`
  — i.e. "my Legends counterpart is *GNK power droid/Legends*."
- The Legends article opens `{{Top|canon=GNK-series power droid}}` — "my canon counterpart is
  *GNK-series power droid*."

That reciprocal pair is Wookieepedia's **continuity fork** convention: one subject, two
articles, one per continuity. It is exactly the same relationship as `ASP-19 Battle Droid`
vs `ASP-19 battle droid/Legends`, which the index's own QA header (line 32) already
identifies as "an explicit canon/Legends continuity fork, not a spelling duplicate." So the
index is **right to keep both rows** and right to grade one `canon` and one `Legends`; they
should **not** be merged, and they correctly map to **one** repo chassis. Both articles also
give the same manufacturer and the same nickname ("gonk droid"), which is corroboration
rather than coincidence.

Practical consequence: **facts below are labelled C (canon article) or L (Legends article)**,
because on several points they differ, and because the campaign may want only one.

## Sourced text (Wookieepedia)

**(C) The GNK-series power droid, also known as the gonk droid**, "was a well-known type of
power droid manufactured by **Industrial Automaton**. They were often referred to as gonk
droids **in imitation of their honking sound**."
[GNK-series power droid](https://starwars.fandom.com/wiki/GNK-series_power_droid)

**(L) GNK power droids** "were an Industrial Automaton **knockoff of the successful EG-6
power droid**." ⚠️ **EG-6 is a different droid** and was **not fetched this pass**; note it is
also **not** the library's `droid_ge3` entry, which covers the GE3-series *protocol* droid —
different designation, different role.
[GNK power droid/Legends](https://starwars.fandom.com/wiki/GNK_power_droid/Legends)

**(L) What it actually is:** "effectively **power generators with legs and simple artificial
intelligence** so they could understand rudimentary commands. They were most commonly found
on **under-developed worlds that did not have an expansive power grid**, or in **mobile
military operations**." 🔑 That sentence is the single best canon justification for a gonk on
a scavenger desert world in this campaign, and it is sourced verbatim.

**(C+L) The honking.** "They often made a low honking noise that sounded like the word
'gonk,'" and this form of droidspeak is named **"Gonkian"** (L). The canon article carries an
in-universe announcement aboard the New Republic cruiser *Temperance*: *"Advisory: even if
you can't understand gonk droids, **they can understand you**. Interact accordingly."*

**(C) Where they are seen and what they get used for:** "**often be seen around Tatooine
working on moisture farms or spaceports like Mos Eisley**"; used **as a table to play board
games on**; used to hold other equipment such as a payment dispenser. On **Jedha**,
caretakers used GNK droids "to transport materials and house data; these droids would
sometimes be **interred along with their owners**."

🔑 **(C) The Alliance weaponised them, and this is the canon warrant for the repo's
detonation comp:** "The **Alliance to Restore the Republic modified GNK units so that they
acted as weapons; once deployed, those droids would march slowly across the battlefield
until they collided with an enemy building and explode.**" So a GNK that walks slowly into
something and detonates is **canon**, not a repo invention — and the repo's `MoveSpeed 1.9`
plus `CompDroidDetonation` reproduce that pairing almost literally.

**(L) They have also been armed, once:** a year before the Clone Wars, **Groodo the Hutt**
fielded GNK power droids in his Droid Control Army "modified with **rapid-repeating blasters
in their upper casings**"; Mace Windu severed the blaster as it emerged **from beneath a lid
in the droid's upper frame**. So the upper casing canonically opens.

**(C) Named individual units:** `4B-EG-6`, `Gonky` (*Uprising*), `Gonky` of Clone Force 99,
and **a grey GNK in Jabba's Palace around 4 ABY "where it squealed in pain, as 8D8, under
the command of its supervisor droid EV-9D9, lowered a hot glowing iron on the soles of its
feet in order to torture it."** Note the sourced colour word: **grey**.

**(L) Cult of the Power Droids** — post-Endor rumour that a pair of GNKs would come to your
door soliciting funds for a fringe religious group.

**Infobox fields, both continuities:**

| field | canon | Legends |
|---|---|---|
| manufacturer | Industrial Automaton | Industrial Automaton |
| class | Power droid | Power droid |
| degree | **Class two** | *(blank)* |
| height | **1.1 meters** | **1 meter** (approx.) |
| cost | *(blank)* | **New: 100 credits / Used: 60 credits** |
| armament | *(blank)* | **None** |
| sensor | ⚠️ **"Purple — under Scourge infection"** | *(blank)* |
| plating | *(blank)* | *(blank)* |
| firstmade / retired | blank / blank | blank / blank |

🔴 **Do not paint the eyes purple.** The canon infobox `sensor` value is **conditional** —
`Purple {{C|Under [[Scourge crisis|Scourge infection]]}}`, cited to *Doctor Aphra* (2020) 37.
It describes an **infected** gonk during the Scourge crisis, **not the model's normal
indicator colour**, and the normal colour is not recorded in either infobox. A naive read of
the index or the infobox would produce a purple-lit gonk, which would be wrong for every
ordinary unit.

⚠️ **The canon article is flagged `{{Droid-stub}}`** and the Legends article carries
`{{MultipleIssues|citation|expand}}` — both are acknowledged by the wiki as incomplete. The
canon article's *Appearances* list is enormous (100+ entries) while its body is four
paragraphs; the appearances and non-canon sections were **not** read beyond confirming their
extent. So there is likely more sourced GNK material in individual works that neither article
summarises.

**Unsourced and therefore absent (both continuities):** mass, plating colour, homeworld,
designer, creator, `firstmade`, `retired`.

## Provenance

- **Manufacturer:** **Industrial Automaton**, in **both** continuities — canon cites
  *Star Wars Character Encyclopedia: Updated and Expanded*, Legends cites *Star Wars
  Character Encyclopedia*. Legends adds that it is a **knockoff of the EG-6 power droid**.
  `DROIDS_INDEX.md:739` and `:740` both agree.
  [canon](https://starwars.fandom.com/wiki/GNK-series_power_droid) ·
  [Legends](https://starwars.fandom.com/wiki/GNK_power_droid/Legends)
- **Era:** **blank.** `firstmade` and `retired` are empty in **both** infoboxes. Cited dated
  statements, not promoted into this field: (L) "GNK droids have existed **at least since the
  time of the Cold War**"; (L) Groodo's armed GNKs **23 BBY**; (C) the tortured grey unit in
  Jabba's Palace **around 4 ABY**. ⚠️ Note the model spans an enormous stretch of the
  timeline — Old Republic Cold War through the sequel-era Resistance — so *any* era value
  would be misleading even if one existed. Blank is the right answer here for a reason beyond
  "the field is empty."
- **Typical owners:** the richest owner list of the five chassis in this batch.
  - **(C)** **Galactic Republic**; **Alliance to Restore the Republic** (and *Uprising*);
    **Scourge** — *as a vessel*, i.e. the droid was a host, not an operator; **New Republic**;
    **Resistance**.
  - **(L)** **Galactic Republic** only in the infobox; the body adds the **Confederacy of
    Independent Systems** by implication (the *Renown* survivor was Republic crew),
    **Groodo the Hutt's Droid Control Army**, and Imperial worlds during the Cold War.
  - Non-faction users, sourced: **Tatooine moisture farmers and Mos Eisley spaceport**,
    **Jedha caretakers**, **Jabba's Palace**, **Clone Force 99**.
  🔑 For this campaign the useful part is that a gonk belongs to **whoever needs power** —
  moisture farms and under-developed worlds are named explicitly — which is a better fit for
  a Jawa scavenger clan than any faction droid in the batch.
  [canon](https://starwars.fandom.com/wiki/GNK-series_power_droid) ·
  [Legends](https://starwars.fandom.com/wiki/GNK_power_droid/Legends)

## Visual brief

**Canon appearance is remarkably stable across four references spanning 1977 prop
photography to a 2013 animated series.** A GNK is a **walking crate**: a **boxy body of
stacked rectangular blocks**, wider at the bottom, encrusted with greeblies (knobs, dials,
bolt rows, a recessed indicator panel), standing on **two short ribbed accordion-bellows
legs** that end in **flat, angular, splayed grey feet**. There is **no head, no arms, no
lens, no neck** — the indicator panel on the upper front face is the only "face" it has.
Every reference agrees on all of that.

**Colour, across the four references:** weathered **grey-beige to warm tan-brown**, heavily
scuffed and dust-toned, with the **feet a distinctly cooler/darker grey** than the body. The
Legends prop photo adds a **yellow stripe** running across the front at the mid-body seam and
**small green and red indicator lamps** in the panel; the Clone Wars render is a darker
**brown-grey** with a lit **amber/orange** indicator panel. The canon article separately
records a **grey** GNK (Jabba's Palace). So: dusty neutral warm grey-tan is the safe centre,
and the model is canonically repainted/weathered per unit.

✅ **The repo tint is broadly right.** `RSW_DW_Race_OuterRim_GNKDroid` sets **both** channels
to `RGBA(138,136,125,255)` — a warm neutral grey — which lands inside the canon range and is
the closest colour match of any chassis in this batch.

🔴 **But both colour channels are set to the same value, which throws the mask away.**
`GNK_southm.png` is a genuine two-channel mask: **red covers the body** and **green covers a
distinct band across the upper rim** (with the indicator panel masked black, so it keeps the
base texture and can never be tinted). Setting `first` and `second` to the identical RGBA
means that upper band renders exactly like the body and the two-tone construction is
invisible. Canon puts real tonal separation right there — the prop's stacked upper block and
its yellow seam stripe, the Clone Wars unit's darker upper cowl. **This is a free correction:
one RGBA value, no art change, and it recovers a canon cue the art already supports.**

🔴 **The indicator panel is never lit in the wired sprite.** In `GNK_southm.png` the panel is
**masked black**, so it renders as flat base-texture grey regardless of the def. Canon lights
it in every reference that shows it in colour — **green + red lamps** on the prop, **amber /
orange** in the Clone Wars render. An unlit panel is the one thing that makes the repo gonk
read as scrap rather than as a working power droid, and it is the only emissive detail canon
gives this chassis.

🔴 **The orphan KotOR art is better and it already lights the panel.**
`donor_orphan_kotor_gonk.png` (512×512, unreferenced by any def) shows the boxy body with a
recessed panel carrying a **lit warm-amber lamp and a lit blue lamp**, two grille vents, and
**two legs visible below the body** — noticeably more detail and more canon-correct
lighting than the 256×256 wired OuterRim frame, which is a plain box with a small grey panel
and **no legs visible at all**. Two caveats before promoting it: its **blue lamp has no canon
support** (canon lamps are amber/orange, green and red — never blue), and its legs read as
smooth columns rather than the canon **ribbed accordion bellows**. Worth the owner's
attention as a swap candidate, with the blue lamp recoloured.

⚠️ **Accordion legs and feet are absent from both sprites.** They are the single most
distinctive silhouette feature of a gonk after the box itself — every canon reference shows
them clearly — and neither the wired 256×256 frame nor the 128×126 contact-sheet copy shows a
bellows or a foot. Partly a top-down format constraint (a squat box hides its own legs from
above), so this is noted rather than flagged: the `east` frame would be where to check, and
canon material for a *side* comparison exists in all four reference images.

✅ **Two def values agree with canon and should not be "fixed".** `MoveSpeed 1.9` is the
slowest race in `Races_OuterRim.xml`, matching "march **slowly** across the battlefield" and
Legends' generators-with-legs framing; and `combatPower 99999` on the PawnKindDef keeps the
gonk out of raid-point selection, matching the Legends infobox `armament = None`.

## Source URLs

- https://starwars.fandom.com/wiki/GNK-series_power_droid — **canon** article; wikitext pulled
  via `https://starwars.fandom.com/api.php?action=parse&page=GNK-series_power_droid&format=json&prop=wikitext`
  (16,490 bytes of JSON). Sections read in full: `{{Top}}`, `{{DroidSeries}}` infobox, the
  *Temperance* quote, and the entire four-paragraph body. **Not read:** the `{{ScrollBox}}`
  *Appearances* list (100+ entries) and *Non-canon appearances* beyond confirming their
  extent — that material is **UNREAD, not absent.**
- https://starwars.fandom.com/wiki/GNK_power_droid/Legends — **Legends** article; same API
  pattern (12,019 bytes of JSON). Sections read in full: `{{Top}}`, infobox, the "Declaration
  of Self Determination" quote, *Characteristics*, *History*, *Behind the scenes*. **Not
  read:** *Appearances*.
- Rendered article HTML is Cloudflare-walled; the API is not. Neither article was truncated
  in the parts named above.
- https://static.wikia.nocookie.net/starwars/images/c/c4/GNKpowerdroid-DB.png
  (File:GNKpowerdroid-DB.png, 540×720) → `wookieepedia_canon_databank.png`
- https://static.wikia.nocookie.net/starwars/images/d/d7/Gonkpromo.jpg
  (File:Gonkpromo.jpg, 290×406) → `wookieepedia_legends_promo.jpg`
- https://static.wikia.nocookie.net/starwars/images/5/52/Gonk1.jpg
  (File:Gonk1.jpg, 274×446) → `wookieepedia_mos_espa.jpg`
- https://static.wikia.nocookie.net/starwars/images/5/53/RenownGNK-PoNR.png
  (File:RenownGNK-PoNR.png, 540×720) → `wookieepedia_clonewars_renown.png`
- Named in the articles but **not fetched this pass**:
  https://starwars.fandom.com/wiki/EG-6_power_droid/Legends (the droid the GNK knocks off),
  https://starwars.fandom.com/wiki/Power_droid, `4B-EG-6`, `Gonky (Clone Force 99)`,
  `Gonky (Uprising)`, `Scourge crisis`, `Gonkian/Legends`, `Cult of the Power Droids`,
  `Unidentified GNK power droid/Legends`
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_OuterRim.xml`,
  `Defs/PawnKinds_OuterRim.xml`, `Defs/IncidentDefs/IncidentDefs_Droidworks.xml`,
  `Defs/ThingDefs/Heads_Droidworks.xml`

## Candidate images

- `wookieepedia_legends_promo.jpg` (290×406) — the **Legends article infobox**: a studio photo
  of the physical prop, three-quarter rear-ish view on a plain grey background. Weathered
  tan-grey stacked boxes, dense greeblies, knobs and dials, small **green and red indicator
  lamps**, a **yellow stripe** across the front mid-seam, **ribbed accordion legs** and
  **flat angular grey feet** with a trailing cable. **The detail and construction authority
  for this chassis** — the clearest of the four.
- `wookieepedia_canon_databank.png` (540×720) — the **canon article infobox**, Databank image:
  a GNK on Tatooine sand in daylight, three-quarter. Sun-bleached pale tan body, cooler grey
  feet. Confirms the desert-world palette and the *in situ* read; low on fine detail.
- `wookieepedia_mos_espa.jpg` (274×446) — a GNK in **Mos Espa**, near-profile. Grey-green-brown
  weathering, clearest view of the **accordion bellows legs and splayed feet** in motion. The
  best leg reference.
- `wookieepedia_clonewars_renown.png` (540×720) — the *Renown* GNK from *The Clone Wars*
  ("Point of No Return"). Darker **brown-grey** animated design with a **lit amber/orange
  indicator panel** on the upper front face. **The lit-panel authority**, and evidence that
  the design is stable across media. ⚠️ Another droid is partly visible at right — not a GNK.
- `donor_current_sprite_outerrim.png` (256×256) — the **wired** repo sprite
  (`Textures/OuterRim/Droid/GNK_south.png`, byte-identical). Greyscale / two-channel masked;
  judge tinted with `RGBA(138,136,125)` on **both** channels. Plain box, small **unlit** grey
  panel, no legs, no feet.
- `donor_orphan_kotor_gonk.png` (512×512) — the **orphan** KotOR art
  (`Textures/KotOR/Droid/gonk/gonk_south.png`, byte-identical). **Referenced by no def.**
  Higher detail, grille vents, legs visible, and a lit amber lamp — but also a **blue lamp
  with no canon support.** A swap candidate, not current shipping art.
- `donor_contactsheet_128.png` (128×126) — `design/Jawa/fauna/sprites/OuterRim_GNKDroid.png`.
  ⚠️ **Not byte-identical to the wired texture** (different md5, and 128×126 vs 256×256), so
  it is a downscaled contact-sheet copy, not the shipping asset. Weak evidence — use
  `donor_current_sprite_outerrim.png` for any judgement.

## ruling

(empty — the owner has not reviewed this chassis yet)
