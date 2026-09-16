# B1-series battle droid (repo chassis: B1, JDS + OuterRim)

**defName**: no single def — this chassis is FIVE defs across two donor mods.
- JDS: `RSW_DW_Race_JDSCIS_B1_Battle_Droid` / `RSW_DW_Race_JDSCIS_B1_Security_Droid` /
  `RSW_DW_Race_JDSCIS_B1_Commander_Droid` (ThingDefs, `Defs/Races_JDS.xml`), each with a
  matching PawnKindDef of the same name minus `_Race_` (`RSW_DW_JDSCIS_B1_Battle_Droid`
  etc., `Defs/PawnKinds_JDS.xml`).
- OuterRim: `RSW_DW_Race_OuterRim_BattleDroid` (label "B1 Battle Droid",
  `Defs/Races_OuterRim.xml`), head type `RSW_DW_HeadType_OuterRim_BattleDroid`.
- Droids are **not xenotypes** — none of these appear in
  `RimMandrakeXenotypes.xml`, and they should not be looked for there.

## Canon variants this one chassis covers (11 rows in `DROIDS_INDEX.md`)

| canon row | what distinguishes it |
|---|---|
| B1-series battle droid | the baseline; Trade Federation / CIS infantry |
| B-1 series mercenary sentry droid | post-Clone-Wars sentry unit of the Droid Gotra on Nal Hutta |
| B-1 series protocol droid | B1 chassis reassigned to protocol work |
| B1 melee battle droid | melee-specialised; Bedlam Raiders only, post-Clone-Wars |
| B1 recon droid | purpose-built for reconnaissance |
| B1 grapple droid | hand-to-hand specialist, **white and green plating** |
| B1 repeater blaster droid | repeating blaster; markings identical to a standard B1 |
| B1-series rocket battle droid | rocket pack, built to hunt escape pods; **orange and black body** |
| B1 supervisor droid | supervisory unit, c. 32 BBY |
| B1 Electrostaff droid | electrostaff-armed; CIS and Commerce Guild |
| B1-series worker droid | loader/class-five; AccuTronics, used by the Galactic Empire |

⚠️ The repo's third JDS sprite is a **B1 Commander** droid, which in canon is not a
separate model but an **OOM-series** command unit distinguished only by yellow
markings — see Visual brief. The task brief that commissioned this entry listed a
"security" row; the index has no `B1 security droid` row, it has
`B-1 series mercenary sentry droid`. The repo's `B1_Security_Droid` sprite is best
matched to the canon OOM **red = security** marking convention, not to a distinct
canon model.

## Sourced text (Wookieepedia)

B1-series battle droids were humanoid **fourth-class / fourth-degree battle droids**,
**1.93 meters tall** and **65 kilograms**, with masculine programming, black
photoreceptors, and plating described as **bone-white, rust brown, or light grey**
(infobox, [B1-series battle droid]). Standard armament is the **E-5 blaster rifle**;
also attested are a Radiation Cannon, electropole, thermal detonators and the RPS-6
rocket launcher. Standard equipment includes a **comlink booster pack** with an
integrated comms antenna, a logic module, datapad and macrobinoculars. Created by the
**Geonosians**; manufactured by the **Techno Union**, with **Baktoid Combat Automata**
and **Baktoid Armor Workshop** named under it, plus **Geonosis Industries**. Homeworlds
of manufacture: the Geonosian droid factories on Geonosis, the Kudo droid foundry on
Kudo III, and the Akiva droid factory. The **OOM-series battle droid** is a mark of the
B1-series; the **631 model** is a more cheaply made model.

The humanoid physique was **specifically commissioned by the Trade Federation** so B1s
could operate machinery, vehicles and weapons designed for organic pilots — STAPs,
Armored Assault Tanks, Multi-Troop Transports and Federation battleships — saving
retrofitting cost. They were also **designed to resemble their Geonosian creators**.
The body **folds into a compact stowed configuration**: 112 B1s fit inside a
Multi-Troop Transport, and a B1 low on power folds down to recharge. On activation the
**limbs unfold first and the long neck unfolds last**.

Early B1s were driven by a **central command signal** from a Central Control Computer
aboard an orbiting Lucrehulk-class Droid Control Ship — a Trade Federation cost saving.
By the CIS period B1s had been reworked to run without one and were **capable of
limited independent thought**; older signal-dependent models remained in service (e.g.
RB-551 at the Battle of Ryloth). A comlink sits **just below the head**;
photoreceptors can switch to **infrared**, and B1s can pick up electromagnetic fields
such as those from holoprojectors. Simple **vocabulators** give most B1s high-pitched
voices, though some speak in lower monotone; they can express fear, confusion and
excitement. These "personality quirks" are **programming glitches**, never fixed
because swarm tactics did not require better programming.

Inexpensive but durable metal protects the signal-receiver assembly, but it protects
poorly against blaster fire and lightsabers. Snipers target the **capacitors** — a hit
between them takes a unit out. Captain Rex's advice to the Onderon rebels was that the
only true kill is **taking out the head**, because the body is not needed to report
intel. Individually ineffective against clone troopers, the B1 relies on **mass-assault
tactics**; its cheapness makes sacrificing whole battalions acceptable. Motion-capture
data from trained organics gives the B1 a range of combat stances.

Command structure is read off **colored markings on the armor**, not off different
bodies: within the OOM-series, **blue = pilot, red = security, yellow = command**, with
green markings on AAT drivers. Individual identity is only a **numerical marking on the
back of the comlink booster pack**. Other variants carry their own liveries — rocket
droids orange and black; grapple droids white and green; firefighter droids mostly
black with yellow stripes and a single red spot on the head; Heavy Battle Droids overall
grey with dark red paint.

## Provenance

- **Manufacturer**: Techno Union (Baktoid Combat Automata; Baktoid Armor Workshop) and
  Geonosis Industries; **created by the Geonosians**. Named per-variant manufacturers
  differ: Baktoid Combat Automata for the Electrostaff, recon, repeater-blaster and
  rocket variants; **Bedlam Raiders** for the melee variant; **AccuTronics** for the
  worker variant. [B1-series battle droid], and the per-variant rows in
  `DROIDS_INDEX.md`.
- **Era**: **blank** — Wookieepedia's droid infobox carries no era for the B1-series.
  The one exception in this chassis group is `B1 supervisor droid`, whose infobox gives
  **c. 32 BBY**. Nothing else here is inferred.
- **Typical owners**: Trade Federation (and Trade Federation military), Techno Union,
  Confederacy of Independent Systems (and Confederacy military), Cato Neimoidian
  government, Jedi Order (captured units). Post-war: Droid Gotra and "The Twins" on Nal
  Hutta (mercenary sentry), Bedlam Raiders (melee), Commerce Guild (Electrostaff),
  Galactic Empire and Radell Mining Corporation (worker).

## Visual brief

**The repo sprite is a top-down RimWorld pawn sprite, and it gets the B1 silhouette
essentially right.** `donor_current_sprite.png` (JDS, 128×128) shows, from directly
above: a **long narrow head projecting forward past the shoulders** — the single most
identifying B1 feature, and correctly present — a **thin neck**, **narrow shoulders**,
thin arms held close in, and a rifle carried diagonally over the right shoulder. The
palette is **tan / bone-khaki**, agreeing with canon "bone-white, rust brown, or light
grey" and with the reference photograph.

- `wookieepedia_infobox.png` (side view, film-model render) is the proportion
  authority: **spindly limbs, a hunched forward-leaning stance, an elongated
  down-tilted head like an animal skull**, a visibly thin waist, and knees and elbows
  that read as exposed hinge joints rather than armour. Height is carried in the legs,
  not the torso.
- `wookieepedia_folded_stages.png` shows the **five-stage unfold** from stowed to
  standing. This is worth keeping because it proves the "hunch" is not a pose choice:
  even fully deployed the B1 stands with the head thrust forward and down.
- 🔴 **Do not conflate B1 and B2 proportions.** The B1 is *tall and thin*: the same
  1.93 m as a B2 but at 65 kg, with narrow shoulders barely wider than its own head and
  a torso that is a thin box. The B2 (see `droid_b2/`) is *squat and armoured*: the same
  nominal height, but the head is sunk into a huge armoured shoulder yoke and the arms
  are as thick as the B1's torso. At 128 px the difference must be carried by
  **shoulder width and the presence or absence of a protruding head**, because nothing
  else survives at that scale. The repo's two sprites do currently carry that
  distinction correctly — the B1 has a head that reads separately from the shoulders,
  the B2 does not.
- **The repo's marking colours agree with canon.** `JDSCIS_B1_Security_Droid.png` is
  the base tan body with **dark red** chest/shoulder markings; the commander sprite is
  the base body with **yellow** shoulder and chest markings and a yellow crown patch.
  Canon says red = security, yellow = command. This is a match, not a contradiction.
- **What the sprites do NOT cover**: none of the 11 canon variants above has its own
  art. There is no orange-and-black rocket B1, no white-and-green grapple B1, no
  blue pilot B1, no worker/loader livery, and no folded/stowed pose. All of that is
  reskin-scale work on an existing correct silhouette.

## Must show
- [ ] Long narrow head projecting forward past the shoulders
- [ ] Narrow shoulders with thin arms held close to the body
- [ ] Tan/bone-khaki base plating
- [ ] Hunched, forward-leaning stance with the head tilted down
- [ ] Security markings dark red, command markings yellow, on shoulder and chest

## Engine limits
none known

## Source URLs

- https://starwars.fandom.com/wiki/B1-series_battle_droid — main article; wikitext
  pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=B1-series_battle_droid&format=json&prop=wikitext`
  (rendered HTML is Cloudflare-walled, the API is not). Sections read in full:
  Description/Design, Performance, Specialized B1 battle droids, and the `{{DroidSeries}}`
  infobox. History sections were **not** read.
- Per-variant rows and their source URLs (infobox-derived, taken from
  `design/RimStarWars/canon_references/DROIDS_INDEX.md`; the individual articles were
  **not** separately fetched in this pass):
  https://starwars.fandom.com/wiki/B-1_series_mercenary_sentry_droid ·
  https://starwars.fandom.com/wiki/B-1_series_protocol_droid ·
  https://starwars.fandom.com/wiki/B1_Electrostaff_droid ·
  https://starwars.fandom.com/wiki/B1_grapple_droid ·
  https://starwars.fandom.com/wiki/B1_melee_battle_droid ·
  https://starwars.fandom.com/wiki/B1_recon_droid ·
  https://starwars.fandom.com/wiki/B1_repeater_blaster_droid ·
  https://starwars.fandom.com/wiki/B1_supervisor_droid ·
  https://starwars.fandom.com/wiki/B1-series_rocket_battle_droid ·
  https://starwars.fandom.com/wiki/B1-series_worker_droid
- https://static.wikia.nocookie.net/starwars/images/c/cd/Battle_Droid.png (File:Battle_Droid.png → `wookieepedia_infobox.png`)
- https://static.wikia.nocookie.net/starwars/images/e/e7/B1stages-SWBC13.png (File:B1stages-SWBC13.png → `wookieepedia_folded_stages.png`)

## Candidate images

- `wookieepedia_infobox.png` — the article's infobox image: a full-body side-three-quarter
  render of a standing B1 with an E-5 blaster rifle held across its body, on transparent
  background. The proportion reference: spindly, hunched, long forward head.
- `wookieepedia_folded_stages.png` — a five-figure sequence showing a B1 unfolding from
  its stowed configuration to standing, from *Star Wars Build the Millennium Falcon* 13.
  Confirms the fold-down behaviour described in the text and the standing hunch.
- `donor_current_sprite.png` — the repo's current JDS B1 battle droid pawn sprite
  (`design/Jawa/fauna/sprites/JDSCIS_B1_Battle_Droid.png`, 128×128, top-down). Strong
  evidence: it is the live shipping art, not a corpse variant. Two sibling sprites in the
  same folder (`JDSCIS_B1_Security_Droid.png`, `JDSCIS_B1_Commander_Droid.png`) are the
  red and yellow marking variants and were also examined for this brief.

## ruling

(empty — owner has not reviewed this chassis yet)
