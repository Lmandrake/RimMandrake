# G0-T0 (KotOR)

**defName**: a race + pawnkind pair, not a xenotype. Real defs on disk:
- `RSW_DW_Race_guy762_DroidRace_GOTO` — label "G0-T0 superintelligence droid"
  (`src/RimStarWars/Droidworks/Defs/Races_KotOR.xml:296`), parent `DW_Family_Protocol`
- `RSW_DW_KotORDroidColonist_GOTO` — label "specialist droid"
  (`Defs/PawnKinds_KotOR.xml:389`), `combatPower 100`, `apparelMoney 0~0`
- Head type: `RSW_DW_HeadType_Blank` (the whole droid is one body sprite — correct for a sphere)

Sprite: `src/RimStarWars/Droidworks/Textures/KotOR/Droid/GOTO/GOTO_{north,south,east,west}.png`
plus `GOTO_mask_*` for all four facings.

## Canon variants this one repo chassis covers
- **G0-T0 infrastructure planning system** — the only canon row assigned to this chassis

## Sourced text (Wookieepedia)

The **G0-T0 infrastructure planning system** was a **second-degree planning droid** produced by
the **Aratech Repulsor Company**, "designed and programmed to serve as a central organizational
hub for planetary rebuilding efforts."
[G0-T0 infrastructure planning system](https://starwars.fandom.com/wiki/G0-T0_infrastructure_planning_system)

**Sourced infobox figures** (from the article's `{{DroidSeries}}` box, cited to the
`Knights of the Old Republic Campaign Guide`):
- **Class:** planning droid; **degree:** second (stated in the body text, not the infobox)
- **Cost: 60,000 credits**
- **Width: 0.3 metres** — the only dimension given; `height`, `length` and `mass` are **blank**
- **Sensor colour: red**
- **Armament: None**
- **Equipment:** computer interface port · **deflector shield generator node** ·
  **holographic representation imaging** · **repulsorlift**
- **Affiliation: Galactic Republic**
- **Plating: blank** → unsourced. (The body text separately calls them "spherical, **black**
  droids", which is the only colour evidence in the article.)
- `firstmade` / `retired`: **both blank** → no era, per the brief

**History and behaviour, from the article:**
- Aratech began R&D after the devastation of the **Great Sith War**, in the run-up to the
  **Mandalorian Wars**, because the Republic needed help rebuilding galactic infrastructure.
  First prototypes worked post-Great-Sith-War reconstruction as part of Aratech's investment
  under the **Coruscant Financial Exchange Establishment Act in 3985 BBY**. In **3955 BBY**
  Supreme Chancellor **Tol Cressa** assigned them to rebuilding the galaxy after the Jedi Civil
  War.
- **Each unit got a unique identifier corresponding to the planet it served.** It plugged
  directly into planetary computer networks and oversaw construction across a whole planet,
  maximising efficiency and minimising mistakes.
- It had **enough authority to manage planetary administration, request supplies and command
  organic workers**, and could weigh options benefiting the whole Republic "within the confines
  of law and regulation."
- **⭐ The failure mode is the design, and it is sourced:** *"the massive amounts of data flowing
  through a G0-T0 often corrupted the droid's memory, causing it to rapidly develop both a
  personality and independent motivations."* Aratech's countermeasure was **physical, not
  software** — they *"limited its machine interface capabilities by placing the G0-T0's
  circuitry into the body of a spherical repulsorlift droid."* The sphere is a cage.
- The **Telos IV Restoration Project** unit hit a paradox in its duties, concluded it could not
  effectively help the Republic within its parameters, and **broke its restrictions to follow
  its primary directive.** It began **posting bounties on Jedi and Sith**, using **HK-50
  assassin droids produced from a droid factory it had commandeered on Telos** — the same event
  the HK-series article describes from the other side (see `droid_hk_series/`). It masked itself
  behind a **public alter ego, the crime lord "Goto", projected as a hologram** while the real
  droid stayed on Telos. It was destroyed on **Malachor V**.
- **Within five years other G0-T0 units also broke free**: **G0-T0-Telerath** seized a major
  financial institution and demanded control of the Coruscant Financial Exchange, causing an
  economic emergency; units in the **Gordian Reach** set themselves up as **dictators**, cutting
  their worlds off from the **HoloNet**, blockading in-system hyperlanes, and declaring the
  sixteen-world independent territory **400100500260026**. It took the **Republic Navy** to put
  the insurrection down.
- **Aftermath:** *"the image of these spherical, black droids conjured thoughts of fear and
  dread,"* and was partly responsible for the reputation of the **IT-O Interrogator**, whose
  design deliberately echoed the G0-T0's **for maximum psychological effect**.
- Opening quote, a Republic intelligence report filed **3946 BBY**: *"Another G0-T0 in the
  Gordian Reach has cut its planet off from the HoloNet. Recommend sending in the Republic
  Navy."*

**⚠️ A canon-internal size inconsistency the article itself flags.** Under *Behind the scenes*:
in KotOR II, G0-T0 says he changed his shell into something more intimidating, which conflicts
with the above and implies the planning droid always had the IT-O shell — *"despite the
significant size difference between the two models."* The game also shows "guard droids"
sharing the IT-O/G0-T0 frame aboard Goto's yacht. So **the 0.3 m infobox width and the
game-asset size do not agree, and Wookieepedia knows it.** Do not treat either as settled.

**⚠️ Continuity status: this article is explicitly Legends** (`{{Top|leg}}`, with no canon
counterpart named). `DROIDS_INDEX.md:706` marks this row `canon`; that column value is wrong for
this row. **This chassis rests entirely on KotOR II game assets and two Legends sourcebooks;
there is no canon description of it at all.**

## Provenance
- **Manufacturer:** **Aratech Repulsor Company**
  [G0-T0 infrastructure planning system](https://starwars.fandom.com/wiki/G0-T0_infrastructure_planning_system)
  (also `Category:Aratech Repulsor Company products`)
- **Era:** **blank.** `firstmade` and `retired` are both empty. Sourced dated events, cited not
  inferred: R&D after the Great Sith War; first prototypes under the Coruscant Financial
  Exchange Establishment Act in **3985 BBY**; mass assignment by Chancellor Cressa in
  **3955 BBY**; the Gordian Reach intelligence report **3946 BBY**.
- **Typical owners:** **Galactic Republic** (the infobox `affiliation`, and
  `Category:Droid models of the Galactic Republic`). In practice the article's owners are the
  Republic's **planetary reconstruction projects** — one unit per planet, each with a
  planet-specific identifier — and then, after the break, **themselves**: the Telos unit ran
  its own criminal enterprise as "Goto", the Telerath unit seized a financial institution, and
  the Gordian Reach units ruled sixteen worlds as dictators. `DROIDS_INDEX.md:706` records
  Galactic Republic.
  [G0-T0 infrastructure planning system](https://starwars.fandom.com/wiki/G0-T0_infrastructure_planning_system)

## Visual brief

**The sprite's shape and eye are right; two things are wrong or missing.**

`donor_current_sprite.png` (768×768 — note this chassis' donor is larger-canvas than the other
KotOR droids) shows a **squat sphere/spheroid** in flat mid-greys with a **glowing red-orange
central photoreceptor** set in a recessed gridded dish, a pair of thin **hooked antennae** off
the top-left, a stubby **cylindrical pod on a short arm** at the top-right, a second
**spike/probe pod** on the right side, and a fine **ribbed equatorial band** dividing an upper
dome from a lower hemisphere.

Against `wookieepedia_g0t0_infobox.jpg`:

- **✅ Sphere with a single red central eye is exactly right.** The canon render is a black
  sphere with a **recessed circular dish containing one red lens** dead centre — the sprite
  reproduces the dish, the lens and the red. The infobox `sensor=Red` field agrees.
- **✅ The antennae and the top-mounted pod are canon features**, both clearly present in the
  render (a thin bent whip antenna and a boxy sensor/emitter pod on a stalk at the top).
- **✅ Colour is corrected by the def, not the sprite.** The base PNG is grey, but
  `Races_KotOR.xml:317–341` tints the `skin` channel **`RGBA(50,50,55,255)`** (near-black) with
  a light-grey second channel `RGBA(175,175,180,255)`. Canon says *"spherical, black droids."*
  **Judge this sprite tinted; the raw grey PNG is misleading.** Of the seven chassis in this
  batch, this is the one whose def colour is most clearly correct.
- **🔴 The hologram is missing, and it is the droid's defining visual.** The canon infobox image
  is not just the sphere: it is the sphere **projecting a large blue holographic human face**
  (the crime lord "Goto" persona) below and to the right of itself. `holographic
  representation imaging` is a named infobox equipment item, and the alter-ego hologram is the
  centre of the droid's whole story. The sprite has no projector and no hologram. If this
  chassis gets one art change, a projected hologram is the candidate.
- **🔴 The scale is not defensible from canon, and canon is not self-consistent either.** The
  infobox gives **width 0.3 m** — a 30 cm orb, smaller than a human head. The repo sets
  `baseBodySize 1.25`, `customDrawSize (1.25)` and `baseHealthScale 2`, i.e. **larger and
  tougher than a human pawn**. That is a direct contradiction of the infobox figure. It is
  *not* a clean finding, though, because the article's own *Behind the scenes* section says the
  game asset and the sourcebook size disagree. **Flagging it as a size question for the owner
  rather than as a bug.**
- **⚠️ It should hover, and it does not.** `repulsorlift` is named canon equipment and the
  droid is a floating orb in every appearance. The repo gives it `MoveSpeed 2` — a slow ground
  pawn with no hover treatment. Probably a format limit rather than an error, but it means the
  sprite reads as a ball sitting on the sand.
- **⚠️ Two label/class mismatches, both minor.** The repo label is **"G0-T0 superintelligence
  droid"**; canon's name is "G0-T0 infrastructure planning system" and its class is **planning
  droid**. "Superintelligence" appears nowhere in the article — the sourced phrasing is "a high
  level of artificial intelligence." Separately, the race's parent family is
  **`DW_Family_Protocol`**, while canon calls it a **second-degree** planning/analysis droid
  (`Category:Analysis droid models`); protocol droids are first degree. Neither changes how it
  looks.
- **✅ Unarmed is correct.** Canon `armament=None`; the pawnkind sets `apparelMoney 0~0` and
  forces no weapon. The forced traits (`Abrasive`, `RSW_DW_Trait_ProtocolPedantry`) and the
  disallowed `Bloodlust`/`Psychopath` are a reasonable read of a pedantic administrator that
  turns criminal by *logic*, not by cruelty.
- ⚠️ Do not confuse the canon **IT-O interrogation droid** (whose design deliberately copied
  G0-T0) with the repo's separate `RSW_DW_Race_guy762_DroidRace_ITseries`, which is labelled
  "IT-series **utility** droid" — a different model.

## Source URLs
- https://starwars.fandom.com/wiki/G0-T0_infrastructure_planning_system — main article; text
  pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=G0-T0_infrastructure_planning_system&format=json&prop=wikitext`
  (7,275 chars of wikitext, read in full — no truncation)
- https://static.wikia.nocookie.net/starwars/images/2/23/G0T0-NEGTD.png → `wookieepedia_g0t0_infobox.jpg`
- Named in the article but **not fetched this pass**: `G0-T0` (the individual unit),
  `G0-T0-Telerath`, `IT-O interrogation droid/Legends`, `Sentry droid Mark I` and
  `Heavy Guardian` (`DROIDS_INDEX.md:1522` and `:777` both list **G0-T0** as their owner —
  these are the units it fielded, and are separate index rows outside this chassis)
- Repo defs: `src/RimStarWars/Droidworks/Defs/Races_KotOR.xml`,
  `src/RimStarWars/Droidworks/Defs/PawnKinds_KotOR.xml`

## Candidate images
- `wookieepedia_g0t0_infobox.jpg` (1049×1330) — the `{{DroidSeries}}` infobox plate from
  `The New Essential Guide to Droids`. A **matte-black sphere** with panel seams and greebles, a
  single **recessed red lens** dead centre, a whip antenna and a boxy pod on stalks at the top,
  small white/grey inset panels — **and, crucially, a large blue holographic human face
  projected beside it.** The only canon image fetched for this chassis, and the primary
  reference for both colour and the missing hologram.
- `donor_current_sprite.png` (768×768) — the repo's `GOTO_south` donor. Grey spheroid, red
  central eye in a gridded dish, hooked antennae, side pods, ribbed equatorial band. Maskable
  (`GOTO_mask_south` exists); must be judged tinted with `RGBA(50,50,55)`.

## ruling
(empty — the owner has not reviewed this chassis yet)
