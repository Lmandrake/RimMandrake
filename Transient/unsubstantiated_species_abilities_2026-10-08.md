# Unsubstantiated species abilities - reverse audit (UNSUBSTANTIATED_SPECIES_ABILITIES_1)

Status: COMPLETE report, 2026-10-08. Read-only; no def changed. Owner rules; aptitude corrections one at a time (standing 2026-09-17).

## 1. Method and counts

- **Xenotypes examined: 70** (MEASURED: 69 in `RimMandrakeXenotypes.xml` + 1 in `MandrakeJawaXenotype.xml`); **all 70 carry at least one effect-bearing gene** (cosmetic skin/eye/hair genes excluded) (psychic, combat, resilience, aptitude, metabolic, longevity, immunity). 
- Every gene was resolved from its GeneDef in the **frozen-era def dump capture 2026-10-09T01-58-44Z** (`DefDump/captures/.../defs/GeneDef.json`, 4180 GeneDefs; all 428 distinct genes used resolved, 0 missing), reading `statOffsets/statFactors/aptitudes/abilities/makeImmuneTo/hediffGiversCannotGive` and descriptions, not names. Aptitude levels: Strong +4, Remarkable +8 plus a passion. Robust x0.75 incoming damage; MeleeDamage_Strong x1.5; Duelist x1.5 hit and dodge; Evasive +10 raw dodge.
- Sanity probe PASSED: census found Rakata `PsychicAbility_Enhanced` + `Turn_Gene_LatentPsychic` + `Turn_Gene_FastNeuralHeat`, and Cerean `PsychicAbility_Enhanced`.
- Note: `Turn_Gene_SlowNeuralHeat` (Cerean, Wookiee, Umbaran) is a **cost** (x0.75 recovery), not an advantage; excluded.
- Canon check: each species' entry in `design/RimStarWars/canon_references/` (all 70 species have one; entries marked VERIFIED were independently re-sourced 2026-09-20). **The library was not treated as authority**: where it asserts "well sourced" with no citation the row is verdict **L**. High-impact genes with a silent or doubtful library were checked live against Wookieepedia (`Anzat (species)`, `Feeorin/Legends`, `Gand/Legends`, `Kel Dor/Legends`, `Hutt`, `Nautolan/Legends`, `Wookiee`, `Nikto/Legends`, `Kubaz/Legends`, `Mirialan/Legends`). Canon and Legends are not separated in the verdict; a Legends-only source is named in the source column.
- Verdict legend: **C** contradicted (source says the opposite) / **U** unsubstantiated (no source found anywhere checked) / **L** unsourced library claim (library asserts, cites nothing, not independently found) / **S** substantiated.
- Rows (gene-level, grouped where identical across species): **C 10, U 88, L 3, S 34**. S rows are aggregated, so S undercounts genes. Impact score 1-10 = effect on play (combat/survival/psychic highest; cosmetic-weight genes 1-2).
- Not covered: an "ungranted" canon ability (the forward audit, `XENOTYPE_CANON_CORRECTION_1`), and low-impact comfort/cosmetic genes (temperature, beauty, mood, skin).

## 2a. Contradicted by the source (rank by impact)

| Impact | Species | Gene | Effect (from GeneDef) | Verdict | Source / note |
|---|---|---|---|---|---|
| 9 | Cerean | `PsychicAbility_Enhanced` | +0.2 psychic sensitivity, +0.1 meditation focus, +0.1 neural-heat recovery | C | canon_references/cerean: Legends 'Force-sensitivity ... similar to baseline Humans' |
| 9 | Rakata | `PsychicAbility_Enhanced` | +0.2 psychic sensitivity, +0.1 meditation focus, +0.1 neural-heat recovery | C | canon_references/rakata: later Rakata 'all Force-blind' (plague); W: Rakata |
| 8 | Echani | `AptitudeRemarkable_Melee` | +8 melee levels and a passion | C | canon_references/echani: Legends 'not a biological trait inherent to the Echani'; skill is cultural |
| 8 | Echani | `MeleeDamage_Strong` | melee damage x1.5 | C | canon_references/echani (same; library later lists it 'well-sourced', self-contradictory) |
| 8 | Rakata | `Turn_Gene_LatentPsychic` | may grant psylink 1, then up to level 3 (every ~5.5 y after 45) | C | canon_references/rakata (same); grants psylink 1-3 |
| 7 | Echani | `Turn_Gene_Duelist` | melee hit x1.5 and dodge x1.5 | C | canon_references/echani (same) |
| 4 | Kel Dor | `RSW_lifespan_double` | lifespan x2 | C | canon_references/kel_dor: Legends 70+ years (human-normal), not double |
| 4 | Nikto | `ToxicEnvironmentResistance_Total` | immune to toxic fallout/pollution | C | canon_references/nikto: distinctives are morphological, no resistance attested |
| 4 | Rakata | `Turn_Gene_FastNeuralHeat` | neural heat recovers x1.25 | C | canon_references/rakata (same) |
| 1 | Duros | `Outland_Scalebody` | incoming damage x0.95 | C | canon_references/duros: canon smooth skin (cosmetic-weight 5% damage) |

## 2b. Unsubstantiated (rank by impact)

| Impact | Species | Gene | Effect (from GeneDef) | Verdict | Source / note |
|---|---|---|---|---|---|
| 9 | Anzati | `TotalHealing` | heals one old wound/chronic illness every 15-30 days | U | Wookieepedia 'Anzat (species)' (Legends): long-lived, Force-sensitive, telepathic, fast; no healing/regeneration. canon_references/anzati silent |
| 9 | Anzati | `PerfectImmunity` | immune to flu, malaria, plague, sleeping sickness, wound infection, lung rot, gut worms, muscle parasites, organ decay | U | same: no disease immunity stated |
| 9 | Feeorin | `TotalHealing` | heals one old wound/chronic illness every 15-30 days | U | canon_references/feeorin + W 'Feeorin/Legends': only 'grew stronger with age rather than weaker' |
| 9 | Kel Dor | `PsychicAbility_Enhanced` | +0.2 psychic sensitivity, +0.1 meditation focus, +0.1 neural-heat recovery | U | canon_references/kel_dor + W 'Kel Dor/Legends': only silver-iris minority; telepathy claim exposed as a lie |
| 8 | Anzati | `Robust` | incoming damage x0.75 | U | same: strength 'ordinary human to peak athlete' only |
| 8 | Dathomirian | `MeleeDamage_Strong` | melee damage x1.5 | U | canon_references/dathomirian: unsourced as species traits |
| 8 | Dathomirian | `Robust` | incoming damage x0.75 | U | canon_references/dathomirian: Zabrak 'evolved to be tough' - an ENDURANCE (two hearts) trait, not damage reduction |
| 8 | Ewok | `Robust` | incoming damage x0.75 | U | canon_references/ewok: 'strong enough to overpower combat-trained humans' is strength not damage reduction |
| 8 | Falleen | `MeleeDamage_Strong` | melee damage x1.5 | U | canon_references/falleen: canon gives quick reflexes, never strength |
| 8 | Feeorin | `Robust` | incoming damage x0.75 | U | same (library calls these the largest invented power) |
| 8 | Feeorin | `MeleeDamage_Strong` | melee damage x1.5 | U | same: 'oldest and strongest' elders, no species strength claim |
| 8 | Gamorrean | `Robust` | incoming damage x0.75 | U | canon_references/gamorrean: 'tall, strong'; 'no regeneration, toxin resistance or special capability' |
| 8 | Gand | `PsychicAbility_Enhanced` | +0.2 psychic sensitivity, +0.1 meditation focus, +0.1 neural-heat recovery | U | Wookieepedia 'Gand/Legends': 'limited telepathy among some'; findsmen Force-sensitivity is a belief of offworlders |
| 8 | Herglic | `MeleeDamage_Strong` | melee damage x1.5 | U | canon_references/herglic: no combat aptitude or damage resistance in either article |
| 8 | Kel Dor | `Turn_Gene_LatentPsychic` | may grant psylink 1, then up to level 3 (every ~5.5 y after 45) | U | same |
| 8 | Klatooinian | `MeleeDamage_Strong` | melee damage x1.5 | U | canon_references/klatooinian: 'strong build, useful laborers'; no resistance/regeneration |
| 8 | Klatooinian | `Robust` | incoming damage x0.75 | U | same |
| 8 | Nikto | `MeleeDamage_Strong` | melee damage x1.5 | U | canon_references/nikto: no strength/capability claim |
| 7 | Anzati | `WoundHealing_Fast` | injury healing x2 | U | same |
| 7 | Anzati | `DiseaseFree` | no age-related chronic disease (cancer, bad back, dementia, ...) | U | same ('long-lived' is not disease-free) |
| 7 | Chagrian | `WoundHealing_Fast` | injury healing x2 | U | canon_references/chagrian: not attested |
| 7 | Dathomirian | `Turn_Gene_Duelist` | melee hit x1.5 and dodge x1.5 | U | same |
| 7 | Feeorin | `DiseaseFree` | no age-related chronic disease (cancer, bad back, dementia, ...) | U | same |
| 7 | Gamorrean | `AptitudeRemarkable_Melee` | +8 melee levels and a passion | U | same: 'strong' supports Strong at most |
| 7 | Mirialan | `Turn_Gene_Duelist` | melee hit x1.5 and dodge x1.5 | U | canon_references/mirialan: 'flexible and agile' only (Evasive is the weak match) |
| 7 | Nautolan | `WoundHealing_Fast` | injury healing x2 | U | canon_references/nautolan: unsourced; W 'Nautolan/Legends' gives tough cartilage (glancing-blow resistance) only |
| 7 | Nautolan | `Turn_Gene_Duelist` | melee hit x1.5 and dodge x1.5 | U | canon_references/nautolan: Kit Fisto is an individual |
| 7 | Yoda species | `DiseaseFree` | no age-related chronic disease (cancer, bad back, dementia, ...) | U | canon_references/yoda_species: unsourced (900-year lifespan is sourced; disease-freedom is not) |
| 7 | Yoda species | `Turn_Gene_Duelist` | melee hit x1.5 and dodge x1.5 | U | same |
| 7 | Zygerrian | `Turn_Gene_Duelist` | melee hit x1.5 and dodge x1.5 | U | canon_references/zygerrian: unsourced |
| 6 | Dathomirian | `Turn_Gene_LatentPsychic` | may grant psylink 1, then up to level 3 (every ~5.5 y after 45) | U | canon_references/dathomirian: graded - witches Force-practising, males 'rudimentary'; flat species-wide gene overshoots (S for females) |
| 6 | Gamorrean | `Unstoppable` | no stagger when hit | U | same |
| 6 | Muun | `AptitudeRemarkable_Crafting` | +8 levels and a passion | U | canon_references/muun: unsourced |
| 6 | Taung | `Unstoppable` | no stagger when hit | U | canon_references/taung: unsourced as biology |
| 5 | Chagrian | `ToxResist_Partial` | toxic resistance +0.5 | U | canon_references/chagrian: canon gives RADIATION resistance, toxin is adjacent |
| 5 | Herglic | `AptitudeStrong_Melee` | +4 skill levels | U | same |
| 5 | Mon Calamari | `Turn_Gene_MotivationHigh` | general labour speed x1.3 | U | no source found in canon_references/mon_calamari |
| 5 | Yoda species | `AptitudeStrong_Melee` | +4 skill levels | U | canon_references/yoda_species: Jedi training, species has 3 known members |
| 4 | Anzati | `LowSleep` | rest falls x0.4 | U | same |
| 4 | Aqualish | `Pain_Reduced` | pain x0.5 | U | canon_references/aqualish: nothing attested |
| 4 | Dathomirian | `Pain_Reduced` | pain x0.5 | U | same |
| 4 | Falleen | `Pain_Reduced` | pain x0.5 | U | canon_references/falleen: not attested |
| 4 | Gand | `Pain_Reduced` | pain x0.5 | U | canon_references/gand: nothing attested (regeneration IS attested but not granted) |
| 4 | Iktotchi | `Turn_Gene_FastNeuralHeat` | neural heat recovers x1.25 | U | canon_references/iktotchi: unsourced |
| 4 | Kaleesh | `Outland_Evasive` | +10 melee dodge (raw) | U | canon_references/kaleesh: unsourced |
| 4 | Kubaz | `ToxicEnvironmentResistance_Partial` | toxic environment resistance +0.5 | U | canon_references/kubaz + W 'Kubaz/Legends': nothing |
| 4 | Rodian | `Outland_Evasive` | +10 melee dodge (raw) | U | canon_references/rodian |
| 4 | Taung | `Outland_Evasive` | +10 melee dodge (raw) | U | canon_references/taung |
| 4 | Weequay | `ToxicEnvironmentResistance_Total` | immune to toxic fallout/pollution | U | canon_references/weequay: nothing sourced |
| 4 | Weequay | `Pain_Reduced` | pain x0.5 | U | canon_references/weequay |
| 4 | Wookiee | `Pain_Reduced` | pain x0.5 | U | canon_references/wookiee: nothing; (inhibitor-chip pain, berserker rage only) |
| 4 | Yoda species | `Outland_Evasive` | +10 melee dodge (raw) | U | same |
| 3 | Abednedo | `Outland_ThickSkin` | +0.2 blunt armour | U | canon_references/abednedo (verified): no toughness claim |
| 3 | Abednedo | `AptitudeStrong_Construction` | +4 skill levels | U | canon_references/abednedo (verified) |
| 3 | Anzati | `Superclotting` | bleeding closes very quickly | U | same |
| 3 | Cathar | `AptitudeStrong_Shooting` | +4 skill levels | U | canon_references/cathar: cuts against canon (claw/predator species) |
| 3 | Chadra-Fan | `AptitudeStrong_Mining` | +4 skill levels | U | canon_references/chadra_fan (verified) |
| 3 | Chadra-Fan | `AptitudeStrong_Crafting` | +4 skill levels | U | canon_references/chadra_fan (verified) |
| 3 | Chagrian | `Learning_Fast` | learning +50% | U | canon_references/chagrian: not attested |
| 3 | Chiss | `Turn_Gene_NaturalLeader` | inspire others to work faster (needs role) | U | canon_references/chiss: flagged as unsupported |
| 3 | Dathomirian | `Outland_ThickSkin` | +0.2 blunt armour | U | same |
| 3 | Duros | `AptitudeStrong_Shooting` | +4 skill levels | U | canon_references/duros |
| 3 | Falleen | `Outland_ThickSkin` | +0.2 blunt armour | U | canon_references/falleen: scales are small, not armour |
| 3 | Feeorin | `Outland_ThickSkin` | +0.2 blunt armour | U | same |
| 3 | Gamorrean | `AptitudeStrong_Shooting` | +4 skill levels | U | same |
| 3 | Gand | `AptitudeStrong_Construction` | +4 skill levels | U | canon_references/gand: library: wrong way round (hunting/tracking is the sourced skill) |
| 3 | Gand | `AptitudeStrong_Crafting` | +4 skill levels | U | same |
| 3 | Gungan | `Outland_LeaperLegs` | Outland_Leap ability | U | canon_references/gungan: jumping not sourced |
| 3 | Gungan | `AptitudeStrong_Social` | +4 skill levels | U | canon_references/gungan |
| 3 | Herglic | `Outland_ThickSkin` | +0.2 blunt armour | U | same |
| 3 | Jawa | `Superclotting` | bleeding closes very quickly | U | canon_references/jawa |
| 3 | Klatooinian | `AptitudeStrong_Shooting` | +4 skill levels | U | same |
| 3 | Lasat | `Superclotting` | bleeding closes very quickly | U | canon_references/lasat: no canon basis |
| 3 | Mimbanese | `Outland_ThickSkin` | +0.2 blunt armour | U | canon_references/mimbanese: unsourced |
| 3 | Mirialan | `RSW_statgene_PsyHarmonize` | custom hediff RSW_Hediff_PsyHarmonize (emotion sync) | U | canon_references/mirialan: Force belief is cultural |
| 3 | Muun | `AptitudeStrong_Medicine` | +4 skill levels | U | canon_references/muun: unsourced |
| 3 | Nikto | `Superclotting` | bleeding closes very quickly | U | canon_references/nikto |
| 3 | Pyke | `Outland_ThickSkin` | +0.2 blunt armour | U | canon_references/pyke: canon implies fragility |
| 3 | Pyke | `AptitudeStrong_Plants` | +4 skill levels | U | canon_references/pyke: misreading of spice |
| 3 | Pyke | `AddictionResistant_x3` | addiction chance x0.5 (GoJuice, Psychite, WakeUp) | U | canon_references/pyke: game inference, not Wookieepedia |
| 3 | Rodian | `Superclotting` | bleeding closes very quickly | U | canon_references/rodian: nothing attested (Rodians susceptible to vitiligo) |
| 3 | Sith Zuguruk | `AptitudeStrong_Cooking` | +4 skill levels | U | canon_references/sith_species: unsourced |
| 2 | Anzati | `ArchiteMetabolism` | no direct stat effect (gene-budget metabolic quality) | U | same; gene has no direct stat effect (gene-budget quality only) |
| 2 | Ortolan | `Immunity_Strong` | immunity gain x1.1 | U | canon_references/ortolan: neither vision nor disease sourced |
| 2 | Togorian | `Immunity_Strong` | immunity gain x1.1 | U | canon_references/togorian |
| 1 | Aqualish | `Outland_InsectBody` | incoming damage x0.95 | U | canon_references/aqualish: overreach |
| 1 | Selkath | `NakedSpeed` | slower clothed, faster naked | U | canon_references/selkath: oblique |
| 1 | Zygerrian | `Turn_Gene_Certain` |  | U | canon_references/zygerrian |

## 2c. Unsourced library claims (library asserts, no citation)

| Impact | Species | Gene | Effect (from GeneDef) | Verdict | Source / note |
|---|---|---|---|---|---|
| 8 | Kaleesh | `MeleeDamage_Strong` | melee damage x1.5 | L | canon_references/kaleesh: only 'MeleeDamage_Strong-adjacent warrior traits'; no strength claim |
| 7 | Massassi | `WoundHealing_Fast` | injury healing x2 | L | canon_references/massassi calls it 'well sourced' but cites nothing; only extreme skin toughness attested |
| 4 | Massassi | `Pain_Reduced` | pain x0.5 | L | same |

## 2d. Substantiated (aggregated; for completeness and so a later pass does not undo them)

| Impact | Species | Gene | Effect (from GeneDef) | Verdict | Source / note |
|---|---|---|---|---|---|
| 8 | Anzati | `PsychicAbility_Enhanced` | +0.2 psychic sensitivity, +0.1 meditation focus, +0.1 neural-heat recovery | S | Wookieepedia 'Anzat (species)' (Legends): Force-sensitive, telepathic, grows with age |
| 8 | Hutt | `Robust` | incoming damage x0.75 | S | W 'Hutt': 'tough and muscular with thick leathery skin' (partial) |
| 8 | Iktotchi | `PsychicAbility_Enhanced` | +0.2 psychic sensitivity, +0.1 meditation focus, +0.1 neural-heat recovery | S | telepathy (Legends); see off-world caveat in table above - RULING 7 |
| 8 | Massassi | `Robust, MeleeDamage_Strong, AptitudeRemarkable_Melee` | incoming damage x0.75 | S | canon_references/massassi: extremely tough skin; warrior caste |
| 8 | Sith Kissai | `PsychicAbility_Enhanced / LatentPsychic / FastNeuralHeat` | +0.2 psychic sensitivity, +0.1 meditation focus, +0.1 neural-heat recovery | S | Wookieepedia 'Sith (species)/Legends': entire species strongly Force-sensitive |
| 8 | Taung | `Robust / MeleeDamage_Strong / Duelist` | incoming damage x0.75 | S | canon_references/taung (Legends): 'extremely resilient'; blood duels |
| 8 | Togorian | `Robust / Pain_Reduced` | incoming damage x0.75 | S | canon_references/togorian (Legends): extremely dense bone tissue |
| 8 | Trandoshan | `BS_Fast_TotalHealing` | regrows scars/limbs/organs | S | canon_references/trandoshan: regrow limbs/scales (plasma blasts defeat regrowth) |
| 8 | Yoda species | `PsychicAbility_Enhanced / LatentPsychic / FastNeuralHeat / PsyHarmonize` | +0.2 psychic sensitivity, +0.1 meditation focus, +0.1 neural-heat recovery | S | canon_references/yoda_species: every known member Force-sensitive (W 'Yoda's species') |
| 6 | Dathomirian | `Turn_Gene_LatentPsychic (females)` |  | S | partial, see U row for males |
| 6 | Geonosian | `Remarkable Construction/Crafting, MotivationHigh, InsectBody` |  | S | canon_references/geonosian |
| 6 | Lasat | `MeleeDamage_Strong, Jump` | melee damage x1.5 | S | canon_references/lasat (verified): strength, jumping |
| 6 | Snivvian | `AptitudeRemarkable_Artistic` |  | S | canon_references/snivvian: renowned artists (Legends) |
| 6 | Umbaran | `AptitudeRemarkable_Social` |  | S | canon_references/umbaran (verified) |
| 6 | Wookiee | `MeleeDamage_Strong, lifespan_quad` | melee damage x1.5 | S | canon_references/wookiee: strong; 400-year lifespan |
| 5 | Devaronian | `ToxResist_Total, FireResistant` |  | S | canon_references/devaronian: toxin-cleansing livers; skin immune to fire |
| 5 | Selkath/Gungan/Mon Cal/Nautolan | `RSW_WaterBreathing` |  | S | amphibious per library entries |
| 4 | Chadra-Fan | `LowSleep` | rest falls x0.4 | S | canon_references/chadra_fan: ~3h sleep |
| 4 | Falleen | `RSW_lifespan_double` | lifespan x2 | S | canon_references/falleen: 250-400 years (undershoots) |
| 4 | Feeorin | `RSW_lifespan_quad` | lifespan x4 | S | 400 years (W Feeorin/Legends) |
| 4 | Hutt | `RSW_lifespan_nine` | lifespan x9 | S | up to 1000 years |
| 4 | Kel Dor | `Outland_ThickSkin, Outland_Evasive` | +0.2 blunt armour | S | W 'Kel Dor/Legends': leathery hide survives vacuum; heightened reflexes (library wrongly lists Evasive as unsourced) |
| 4 | Ugnaught | `lifespan_double, Remarkable Construction/Crafting, MotivationHigh` |  | S | canon_references/ugnaught (verified): 200+ years, builders (lifespan undershoots) |
| 4 | Yoda species | `RSW_lifespan_nine` | lifespan x9 | S | ~900 years |
| 4 | Zeltron | `PsyHarmonize / PsychicBonding / Empathic` |  | S | limited telepathy / empathy (W, Legends + canon 'allegedly') |
| 3 | Anzati | `LongjumpLegs / AptitudeStrong_Melee` |  | S | same: prodigious speed, agility, reflexes |
| 3 | Cathar/Defel/Nagai/Mirialan/Twi'lek | `Quick, Evasive, Strong_Melee, predator` |  | S | library: swift/claws/agile (weak-to-moderate) |
| 3 | Echani | `AptitudeStrong_Crafting` | +4 skill levels | S | canon_references/echani: excellent craftsmen of weapons |
| 3 | Iktotchi | `Outland_ThickSkin` | +0.2 blunt armour | S | canon_references/iktotchi: 'very resistant skin' |
| 3 | Ithorian | `StrongStomach, RobustDigestion, Plants` |  | S | canon_references/ithorian |
| 3 | Kaminoan/Muun/Bith/Bothan/Arkanian/Neimoidian/Sullustan | `Intellectual/Medicine/Social aptitudes` |  | S | library cites cultural/scientific roles |
| 3 | Quarren | `RSW_AbilityGene_inkspray` |  | S | canon_references/quarren: spits ink |
| 3 | Weequay | `Outland_ThickSkin` | +0.2 blunt armour | S | canon_references/weequay: leathery skin resists blaster fire |
| 1 | Gand | `Outland_InsectBody` | incoming damage x0.95 | S | exoskeleton (W Gand/Legends) |

## 3. Owner rulings needed (each a one-line draft decision he can accept)

Per his standing rule these are one at a time; none applied.

1. **Rakata psychic genes (C, impact 9):** Remove `PsychicAbility_Enhanced`, `Turn_Gene_LatentPsychic`, `Turn_Gene_FastNeuralHeat` from Rakata (post-plague Rakata are Force-blind). Draft: ACCEPT removal.
2. **Cerean `PsychicAbility_Enhanced` (C, 9):** Remove; keep `AptitudeStrong_Intellectual` (best-sourced). Draft: ACCEPT removal.
3. **Anzati healing package (U, 9/9/8/7/7):** `TotalHealing`, `PerfectImmunity`, `DiseaseFree`, `Robust`, `WoundHealing_Fast` (+`ArchiteMetabolism`, `Superclotting`, `LowSleep`) have no source; keep only psychic, speed and (Legends) longevity. Draft: ACCEPT removal of the healing/immunity set, keep psychic.
4. **Feeorin `TotalHealing` + `DiseaseFree` + `Robust` + `MeleeDamage_Strong` (U, 9/7/8/8):** canon says only "grew stronger with age". Draft: ACCEPT removal of all four; keep `RSW_lifespan_quad`.
5. **Echani melee package (C, 8/8/7):** Legends says Echani skill is culture, "not a biological trait". Draft: DEMOTE to `AptitudeStrong_Melee` only (keep `AptitudeStrong_Crafting`); or KEEP as game-representation of culture, your call.
6. **Kel Dor and Gand psychic (U, 9/8 and 8):** silver-iris minority only (Kel Dor); "limited telepathy among some" (Gand). Draft: remove Kel Dor `PsychicAbility_Enhanced`+`LatentPsychic`, remove Gand `PsychicAbility_Enhanced`; also Kel Dor `RSW_lifespan_double` -> remove (Legends 70+ y).
7. **Iktotchi `PsychicAbility_Enhanced` (S with caveat):** telepathy sourced but precognition "very limited" off Iktotch. Draft: KEEP as is (substantiated), drop `Turn_Gene_FastNeuralHeat` (unsourced).
8. **Strength/toughness cluster (U, 8 each):** `MeleeDamage_Strong` / `Robust` on Nikto, Herglic, Klatooinian, Gamorrean, Falleen, Dathomirian, Ewok. Draft: remove `Robust` and `MeleeDamage_Strong` where canon gives only "strong"/"reflexes"; substitute `AptitudeStrong_Melee` or nothing (one species per card).
9. **Wound/pain package on Chagrian, Nautolan, Massassi, Falleen, Weequay, Wookiee, Aqualish, Gand (U/L, 4-7):** `WoundHealing_Fast`, `Pain_Reduced`. Draft: ACCEPT removal; Massassi keep `Robust` (extremely tough skin, sourced).
10. **Duelist (U/C, 7):** Dathomirian, Nautolan, Zygerrian, Mirialan, Yoda species. Draft: remove `Turn_Gene_Duelist` from all five (individuals, not species); keep Taung (blood duels) and Rakata.
11. **Toxin resistance (U/C, 4-5):** Nikto, Weequay, Kubaz, Chagrian. Draft: remove; Devaronian stays (sourced).

Follow-ups outside this item: Yoda species `DiseaseFree` (U, 7) and `AptitudeStrong_Melee`; Ugnaught/Falleen/Wookiee lifespan multipliers undershoot sourced figures; Kel Dor `Outland_Evasive` is substantiated though the library calls it unsourced (library correction owed); the library's Echani entry contradicts itself (says "not biological" yet lists the genes "well-sourced").
