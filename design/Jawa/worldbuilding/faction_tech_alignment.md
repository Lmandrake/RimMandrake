# Faction tech alignment — who holds which technology, and why

Item: `TECHPRINT_FACTION_GATING_1`. Design pass 2026-09-26, written for BENCH from the owner's
ruling of the same day. Status: DRAFT, awaiting the owner's read of §6.

## 1. The ruling

Owner, 2026-09-26, verbatim:

> "Those four make sense, plus Homestead has the unique vaporator tech for repairing and creating
> them. Wildsteam may have some unique tech related to their jungle home. Hutts fencing them makes
> sense, but they may have some black market unique items too. Galactic Empire loot could have
> 'plans you need to steal' for industrial materials to manufacture in your factories (possible,
> TBD) plus things like drop pods, smaller shuttles, and true hyperspace capabilities. Junkers had
> originally been thought to hold flame-based tech, sump gas tech, all warcasket tech. Tusken might
> have some environmental suit tech to survive heat. Empire holds true vacsuit ability. Deepwater
> holds rebreathers. See what I'm doing? I'm looking through the 'local tech' and connecting them
> together with faction sources in addition to the chance observation in the environment, plus
> thinking what tech they themselves need to survive."

> "Yes, price is the gate, and likely the only route to marked-up imperial goods. For the drugs,
> chemfuel, infrastructure that's a mix between Imperial and Junker depending on how advanced it is."

> "long-courting isn't all critical path: you don't HAVE to have bowcasters, let the player go
> after it if they really want it. Only the critical path should be normalized. Side-questing is a
> good thing."

"Those four" are the four holders the manifest already carries and he had just been shown:
Enclaves (droid construction), Junkers (warcaskets), Hive (sonic + hivetech), Helix (genetics).
They are SOURCED in `infrastructure/output/research_manifest_draft.csv` `holder` column (MEASURED
this pass: Enclaves 27 rows, Helix 8, Junkers 7, Rakata 5, Hive 4, RustCathedralDroids 2, Hutts 1)
and in the 2026-09-03 rulings recorded in `design/Jawa/research_tree_taxonomy.md` §1.

### The three-source method, stated plainly

For every faction, what it holds is derived from three sources, in this order of strength:

1. **What the faction needs to survive where it lives.** Deepwater lives in water → rebreathers.
   Tuskens live in the killing heat of the open desert → environment suits. Homesteaders farm
   moisture on dry tiles → vaporators. If a faction could not exist without a technology, it
   holds that technology, and holds it well.
2. **The local tech the player can already observe in that faction's environment**, i.e. what is
   already authored in the campaign around it — the terrain, the hazards, the buildings the
   faction's settlements are described as containing.
3. **What the faction is already documented as making** — the "## Technology and economy" bullet
   list of each dossier in `design/Jawa/worldbuilding/faction_roster_v2.md`.

His named assignments are seeds. §2 applies the method to all twelve.

### How to read the tags in §2

- `SOURCED` — traceable to a document read this pass; the path is cited.
- `PROPOSED` — this pass's extension of the method; needs his read (collected in §6).
- `BUILT` — a shipping def already exists in `src/` (or a donor mod is already adopted), so the
  holding is a *gating* decision, not a *content* decision.
- `UNMEASURED` — this pass could not confirm whether a def exists; do not treat as absent.

## 2. The map — one subsection per faction

Live FactionDefs are in `src/RimUtinni/UtinniPatches/Defs/FactionDefs/` (defNames `RUT_Jawa_*`;
MEASURED this pass — the item file's "checked `src/RimStarWars`, zero hits" and
`faction_locked_trees.md`'s `src/SPLIT_Phase3/…` path are both stale). Today's `categoryTag`s:
six `Outlander` (Hutt, Helix, Deepwater, Enclaves, Hive, Wildsteam), Junkers `Pirate`, Trade Moot
`Tribal`; the three vanilla-vessel factions keep vanilla's (`Empire`, `Outlander` for Homestead,
`Tribal` for the Tuskens); Blackstar's `Pirate` vessel has none. The mechanism is in the item file
and is not restated here.

Holdings are given as plain subjects, never as tab names (§7). "Manifest today" cites what the
draft CSV currently says so the build step can see the delta; it does not assign rows.

### 2.1 Hutt Cartel — the fence, plus a black-market shelf of its own

| holds | why (source #) | status |
|---|---|---|
| **The fence: everything, at a markup.** Any faction-held techprint that reaches a market can appear in Hutt stock at a premium. | #3 — *"rare spacer equipment obtained by trade, not production"*, trader types *bulk goods, exotic goods, weapons, water* (`faction_roster_v2.md` §1 Technology, Faction settings) | SOURCED — owner's own words above; §4 |
| **Spice and the drug trade** — psychite/psychoid refining, smokeleaf, the spicehouse | #3 — *"psychoid, smokeleaf, beer, chemfuel"*, drug labs; the Pykes handle spice at 7% of the faction | SOURCED (`faction_roster_v2.md` §1) — ⚠️ the earlier v3 pass found `KOTOR_Research_Spice` cannot be locked without leaking into an ungated implant row (`faction_locked_trees.md` §7). Holding is real; which rows carry it is the build step's problem |
| **Contraband gas** — the tibanna black market | #2 — *"the Cartel runs the tibanna black market"* (`design/Jawa/tibanna_embargo_plot_spec.md` §4) | SOURCED |
| **Restraint and coercion hardware** — cages, the slave economy's tools | #3 — prisons, slaves/prisoners trader type; manifest today already holds `OilPourCageResearch` (Torment Master) as `Hutts` | SOURCED (manifest `holder` column) |
| **Kajidic equipment** — the Cartel's own gear catalogue | #3 — v3 re-aims `guy762_ResearchKotOR_hutts` and `_exchange` (the Exchange is absent; the Cartel *is* this planet's syndicate) to a Hutt tag | SOURCED as a proposal (`faction_locked_trees.md` §6), not yet ruled |
| **Orbital services** — landing-pad shuttle trade, airstrikes-for-hire, orbital healing | #2 — MiningCo reskin (`faction_roster_v2.md` §1 ORBITAL MECHANICS) — these are *services bought with silver*, not techprints | SOURCED — and deliberately NOT a holding: a service is priced, never learned. Listed so nobody files it as research |

What they need to survive (#1): nothing technical — the Cartel survives by owning the oasis and
charging for it. That is why its holdings are *commercial* (fence, drugs, contraband, coercion)
and not *environmental*. The one exception is the walled cistern, which is Deepwater/Homestead
tech bought in.

### 2.2 Galactic Empire — permanent enemy; everything arrives by loot or theft (§5)

| holds | why | status |
|---|---|---|
| **True vacuum capability** — the sealed suit that reaches space | #1 — the Empire holds orbit and runs it from orbital installations (`faction_roster_v2.md` §2, 7–8 orbital holdings); owner: *"Empire holds true vacsuit ability"* | SOURCED. BUILT as content: Odyssey `Apparel_Vacsuit`/`Apparel_VacsuitHelmet` under `OrbitalTech` (`design/RimMandrake/exposure_gear_matrix_spec.md` §0, MEASURED there). The **deluxe tier** of the exposure matrix is exactly this holding |
| **Drop pods** | #3 — *"drop pods, mortars, shield packs, jump packs"*, drop-pod use *Common*, drop-pod batteries | SOURCED. Manifest today: `TransportPod` (Core) is `common` — the delta is the build step's |
| **Smaller shuttles** | #3 — Imperial patrols, the large spaceport as planetary seat; owner names it | SOURCED as intent. Manifest today: `Shuttles` (Odyssey) is `common`, tab The Utinni |
| **True hyperspace** | owner names it; #1 — the only faction on the planet with an off-world supply line | PROPOSED shape (§5): this is *not* the gravship tree, which is ship-only via the Memory Core. Hyperspace is a separate, endgame, stolen capability |
| **Standardised spacer military kit** — charge weapons, marine-grade plate, imperial trooper apparel | #3 — *"complete spacer military technology"* (`faction_roster_v2.md` §2) | SOURCED — reaches the player as **loot on corpses**, not as research. No techprint needed for what you can strip off a body |
| **Imperial archives** — Sith/Jedi/Republic/Echani equipment, Stygium cloaking, positronic brains | already carry an `Empire` tag in the shipped KotOR research (`Absorbed_KotorCore_Czerkatech_Techprint_Research.xml`, MEASURED) | SOURCED (`faction_locked_trees.md` §6 keeps them Empire-held, "confiscated") |
| **Atmospheric condensers and reservoir bunkers** | #3 — *"in every installation"* | SOURCED — but this is Homestead's vaporator lineage industrialised; see §6 Q4 for who holds the *print* |
| **Mechanitor / mechanoid infrastructure, growth vats, gene banks, cryptosleep** | #3 | SOURCED as *possessed*; NOT proposed as an Imperial *holding* — genetics is Helix's, droids are the Enclaves', and mechanitor rows are already `cut` in the manifest |

What they need to survive (#1): nothing local — they are supplied from orbit. That is why the
Empire's holdings are *off-world* technologies (vacuum, orbit, hyperspace, pods, shuttles) and
why every one of them is stolen, never bought.

### 2.3 Homestead Defense League — vaporators: make them, mend them

| holds | why | status |
|---|---|---|
| **Vaporator manufacture and repair** — building a moisture vaporator, and keeping one running | #1 — *"Settlements store water but have no source"*, *"pull moisture from the air"*; #3 — *"vaporator arrays and cistern storage — the faction's defining infrastructure"*; the recurring *vaporator repair party* group (`faction_roster_v2.md` §3) | SOURCED; owner names it verbatim. BUILT as content: `KotOR_MoistureVaporator_big` (`src/RimStarWars/Armoury/…/Absorbed_KotorCore_Building_MoistureVaporators.xml`) gated by `KOTOR_Research_MoistureVaporator` ("Atmospheric Moisture Collection"), manifest today `common`, T2. ⚠️ A separate **repair** mechanic does not exist as a def (UNMEASURED beyond the KotOR building's own hit points) — "repairing them" is a def to author, and the Homestead's repair parties are its fiction |
| **Cistern storage** | #3 — the same bullet | SOURCED — shared with Deepwater (whose cisterns are the export); Homestead's is the *dry-tile* variant, stored not sourced |
| **Farmstead basics** — refrigeration, hydroponics in richer holds, livestock, leather, medicine | #3 | SOURCED as *possessed*, but PROPOSED as **common, not held** — these are survival rows (T3 of `faction_locked_trees.md` §3 forbids gating food/medicine) |
| **Repaired firearms** — kinetic, bolt-action, pump shotgun | `faction_equipment_clusters.md` Part 2: idiom *repaired*, kinetic | SOURCED as loadout; NOT a holding (everyone has kinetic) |

What they need to survive (#1): water from air, on a tile with none. Everything else about the
Homestead is ordinary; the vaporator is the one thing they alone cannot live without, so it is the
one thing they alone hold. This is the cleanest instance of the method.

### 2.4 Deep Desert Tribes (Tusken) — heat-survival apparel, venom, and a dead print to fix

| holds | why | status |
|---|---|---|
| **Heat-environment apparel** — the wrap/mask/robe that lets a body walk the 51–60 °C deep desert | #1 — sited at 51–60 °C, *"never a water tile"*, no roads (`ASHKARR_WORLD_DEFINITION.md` faction table); owner: *"Tusken might have some environmental suit tech to survive heat"* | PROPOSED, with a wrinkle: `faction_equipment_clusters.md` Part 2 MEASURED Tusken masks at `Insulation_Heat 50` and robes 20–25 — *"the correct look, not the survival answer"*. So the Tusken holding is the **cheap tier of the exposure matrix's heat column** (`exposure_gear_matrix_spec.md` §2: `RM_Apparel_ScaldWrap`, ruled numbers, unbuilt) skinned as Tusken wraps, not a "suit". See §6 Q2 |
| **Tusken Raider equipment** — cycler rifles, gaderffii | already a techprint row: `guy762_ResearchKotOR_tusken` held by `Raider` — a tag **no faction on the planet carries**, so it is unreachable today (`faction_locked_trees.md` §4.1) | SOURCED defect; v3's fix (re-tag to `Tribal`) is a proposal. Either way the Tuskens must hold their own gear |
| **Sandbat venom treatment** — the toxic tag on all clan melee | #3 — *"gaderffii treated with sandbat venom"* | SOURCED as content; PROPOSED as a holding (the one chemical craft the Tuskens have) |
| **Concealed cisterns and water-rite** — finding water where there is none | #1/#3 — *"concealed cisterns"*, water by raid and ritual; the adoption quest rewards *"access to hidden cisterns"* | SOURCED — but this is a **quest reward**, not a techprint; listed so nobody files it as research |

What they need to survive (#1): heat and dryness on foot, with no water tile and no road. That
argues for *apparel* and *water-finding*, and explicitly against any powered kit — the equipment
matrix marks energy weapons as sacrilege and captured tech is destroyed, not used. A Tusken
"environment suit" must be cloth and leather, or it is not Tusken.

### 2.5 Free Droid Enclaves — droid construction, held; hydrogen cracking, proposed

| holds | why | status |
|---|---|---|
| **Droid construction** — the whole droid-building branch | owner ruling 2026-09-03: *"droid construction is owned by the droid faction and is a faction reward; the Jawa keep only low-tier repair, reconstruction and maintenance"* (`research_tree_taxonomy.md` §1); manifest today holds 27 rows as `Enclaves` | SOURCED — one of "those four". ⚠️ `faction_locked_trees.md` §7 had rejected this holder on canon grounds (the Enclaves define the Jawa loop as slavery). The owner's later ruling overrides that rejection; the tension is *the point* of the branch (`faction_roster_v2.md` §5 ENDGAME WILDCARD: ally them or raid them) |
| **Droid brains** — the scarce input every built droid needs | `faction_roster_v2.md` §5: *"fought for… or acquired through quests/trade, never crafted or researched"* (owner, 2026-08-06) | SOURCED — and NOT a techprint: it is an item with no research row by ruling. Listed so nobody files it |
| **Hydrogen cracking** — splitting a water tile for fuel cells and coolant | #1 — *"hydrogen cracking plant — the reason they hold water tiles"*, Water doctrine *Deny* (`faction_roster_v2.md` §5) | PROPOSED holding. No research row matches (manifest probe: 0 hits on hydrogen/crack); no def in `src/` (UNMEASURED beyond a filename grep). A cracking works is new content if it is wanted at all — §6 Q5 |
| **Ionic and EMP weapons; integrated armour** | #3; `faction_equipment_clusters.md`: idiom *integral*, ionic + charge | SOURCED as loadout; NOT a holding — ion is the Jawa's own doctrine (`RSW_JawaIon_Weaponry` is jawa-special by the v3 proposal), and EMP is Deepwater's signature |

What they need to survive (#1): power and coolant, with no thirst. The cracking plant is the one
thing they build that nobody else needs, and it is why a decontamination quest costs their
goodwill — take the water tile back and you have unplugged them.

### 2.6 Wildsteam Clan — steam-works, the blower, the boiler: jungle survival tech

| holds | why | status |
|---|---|---|
| **Wet-bulb survival kit** — the dry-air blower, the sealed suit, boiler tech, bathhouses, blower-door domes | #1 — *"Large, high-mass, fur-bearing, rainforest-evolved fighters on a desert world"*, Require (severe) (`faction_roster_v2.md` §6); #2 — the Greentide is *"home ground… steam-works culture… bathhouses, boiler tech"*, *"windowless round mud domes… blower doorways"*, and the owner's own machine, *"the dry-air blower (owner's machine, three jobs in one)"* (`design/Jawa/worldbuilding/biomes/the_greentide.md` §4b, §8) | SOURCED as the answer to his open *"Wildsteam may have some unique tech related to their jungle home"*: **the wet-bulb kit IS the jungle tech.** BUILT in part: `RUT_SealedSuit` (`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Apparel/RUT_SealedSuit.xml`, `RM_WetBulbProtection 0.6`, Industrial) ships; the blower is specced in the Greentide kit (`kits/greentide_kit_spec.md`), UNMEASURED whether built. §6 Q1 |
| **Bowcaster manufacture** | #3 — *"advanced woodworking; bowcaster manufacture"* (`faction_roster_v2.md` §6); owner's worked example of a SIDE-QUEST holding | SOURCED. BUILT as content: `Absorbed_KotorWeapons_WeaponRanged_KotORBowcaster.xml`; no dedicated research row matched (manifest probe 0 on bowcaster) — it hangs off a KotOR maker row (`guy762_ResearchKotOR_wookiee`, which v3 re-aims to Wildsteam) |
| **Greenwood and advanced woodworking; wood-road passage** | #2 — the Fever Wood's *"wood-road passage… Wildsteam-kept"* (`biomes/the_fever_wood.md`); `STRUCTURE_TEMPLATE_ENGINE_SPEC.md` Q2: *"Wildsteam is canonically the only faction that plants"* | PROPOSED holding: tree-planting and greenwood construction on a planet with 11 Woody stuffs. Manifest today: `TreeSowing` (Core) is `common` |
| **High-quality melee and animal training** | #3 | SOURCED as loadout; NOT a holding (survival-adjacent, and everyone trains animals) |

What they need to survive (#1): to not cook in saturated 45 °C air. Every piece of the kit
answers that one need, which is why it hangs together as a faction signature rather than a
grab-bag.

### 2.7 Deepwater Compact — rebreathers, the dive, purification, EMP

| holds | why | status |
|---|---|---|
| **Rebreathers and the dive** — the moderate tier of the no-air axis | #1 — *"Every combat pawn kind is amphibian or aquatic-evolved. This is physiology"*; the Compact *"holds every natural water tile"* (`faction_roster_v2.md` §7); owner: *"Deepwater holds rebreathers"*; the Depths seed wants *"the Deepwater faction have settlements beneath the waves"* (`depths_concept.md`) | SOURCED. Specced: `RM_Apparel_Rebreather` + `RM_Apparel_BoilSuit` (`exposure_gear_matrix_spec.md` §2 moderate/liquid, unbuilt); the dive hatch ships (`src/RimMandrake/DivingInteraction/…/RM_SeaDiveHatch.xml`). `faction_equipment_clusters.md` already assigns Deepwater *"Environmental suits & breathers"* |
| **Purification, desalination, cisterns** — clean water from fouled | #3 — *"the faction's export"* (`faction_roster_v2.md` §7); #2 — the Scald's steam-catch is *"the Deepwater Compact's headwater interest"* (`biomes/the_scald.md` §7) | SOURCED. BUILT in part: `RUT_SteamCatch` (`src/RimMandrake/TerminalBiomes/…/RUT_SteamCatch.xml`). No purification research row matched in the manifest (probe: only hydroponics/watermill) — desalination as *research* is new content |
| **EMP weapons and EMP traps** | #3 — *"EMP weapons and defensive turrets"*, EMP specialist kind; `faction_equipment_clusters.md`: primary harm **A4 EMP** | SOURCED. Manifest today: `RR_EMP` is `common`, T1 — §6 Q6 on whether to lock a T1 row |
| **Hospital and sterile medicine** | #3 | SOURCED as *possessed*; PROPOSED **common** (medicine is survival; T3) |

What they need to survive (#1): water they can breathe in and water others can drink. Both are
held. The Compact is the only faction whose survival tech is *also* its export, which is why it
is the planet's neutral trader and why nothing here is a side-quest.

### 2.8 Geonosian Foundry Hive — sonic, hivetech, deep-rock water

| holds | why | status |
|---|---|---|
| **Sonic weaponry** | owner ruling 2026-09-03: *"Sonic weaponry likewise Geonosian"* (`research_tree_taxonomy.md` §1); manifest today: `guy762_ResearchKotOR_sonic` held by `Hive` | SOURCED — one of "those four" |
| **Hivetech** — the insectoid production line | manifest today: `VFEI2_BasicHivetech`/`_Standard`/`_Exotic` held by `Hive`; `FACTION_SPEC.md:388` names the Hive the authored insectoid power | SOURCED |
| **Battle-droid mass production** | #3 — *"fabrication, advanced components, droid production"*; the Enclaves' chassis are *"escaped Geonosian Foundry product"* (`faction_roster_v2.md` §5 Origin) | SOURCED as content; **contested as a holding** — v3 proposed moving `OuterRim_BattleDroids` to the Hive, the manifest today holds it as `Enclaves`. §6 Q7 |
| **Deep-rock condensate and deep drilling** — water from stone | #1 — *"Drones take moisture from food and deep-rock condensate"*, Forbid (arid-adapted); #3 — *"extensive mining and deep drilling; deep-rock condensate collection"* | PROPOSED holding: the Hive is the only faction that can sustain a deep-desert siege, and this is how. No matching research row (probe: 0 on condens); deep drilling is Core `DeepDrilling` — UNMEASURED whether it is in the manifest under that name |
| **Drop pods, mortars, growth vats** | #3 | SOURCED as *possessed*; NOT holdings — pods are the Empire's, vats the Helix's |

What they need to survive (#1): water from rock and workers that need none. Sonic and hivetech
are what they *make*; condensate is what they *need*, and it is the one holding here that is
new.

### 2.9 Ascendant Helix — the gene ladder, kolto, and closed-loop water

| holds | why | status |
|---|---|---|
| **The gene ladder** — growth vats, xenogermination, gene processing, biosculpting, archogenetics, bioregeneration, neural supercharger, fertility procedures | manifest today: 8 rows held by `Helix`; *"the Ascendant Genome"*; *"complete gene extraction and implantation"* (`faction_roster_v2.md` §9) | SOURCED — one of "those four". v3's argument stands: pricing the temptation in *who you had to befriend* beats pricing it in points |
| **Kolto and advanced medical implants** | `faction_locked_trees.md` §6 re-aims `KOTOR_Research_Kolto` and `guy762_ResearchKotOR_czerka` to the Helix | SOURCED as a proposal, not yet ruled; manifest today `common` |
| **Closed-loop water recycling** | #1 — *"Closed-loop recyclers make the Helix siting-indifferent"*; #3 — *"bulk water purchase and recycling plant"* | PROPOSED holding: the one environmental tech the Helix has, and the thing that makes it independent of hydrology. No matching research row (probe 0). §6 Q8 |
| **Engineered security organisms** — the `GR_` hybrids as escaped experiments | #3 — *"The Helix owns the planet's monsters"* | SOURCED as lore; NOT a holding — the `GR_Genetic*` rows are `cut` in the manifest, and the creatures are bestiary content, never a recipe |
| **Prosthetics, basic bionics, cryptosleep** | #3 | SOURCED as *possessed*; PROPOSED **common** (T3 — a peg leg is survival) |

What they need to survive (#1): water for vats without a water tile. Recycling is the only
survival tech here; the rest is what they *sell*, which is exactly why the Helix is the
faction whose holdings are the temptation.

### 2.10 Blackstar Company — hunter's kit, combat drugs, contract information

| holds | why | status |
|---|---|---|
| **Mandalorian-pattern hunter equipment; disruptors** | `faction_locked_trees.md` §6 re-aims `guy762_ResearchKotOR_mando` and `_disruptor` from the dead `Pirate` tag to a `BlackstarCompany` tag — *"the planet's elite hunters"*; Blackstar's vessel `Pirate` has no `categoryTag` today (§1 table) | SOURCED as a proposal. ⚠️ Vanilla `Pirate` carries no tag, so Blackstar can hold **nothing** until one is added — a one-line XML change the build step owns |
| **Combat drugs** | #3 — *"bionics and combat drugs"* (`faction_roster_v2.md` §10) | PROPOSED holding — a hunter on a water clock needs go-juice; the *pharmaceutical* half of drugs (§4) is not the Hutts' spice |
| **Contract information / bounty pucks** | #3 — *"weapons, armour, prisoners, contract information as quest rewards"* | SOURCED — and NOT a techprint: it is a **quest reward class**. Listed so nobody files it |
| **Water clock gear** — carrying water, not making it | #1 — *"food and water bought in, which is the range constraint"* | Deliberately NO holding: the Company's survival need is bought from Deepwater, which is the doctrine |

What they need to survive (#1): nothing they make — they buy it, and that buying is their range
limit. So their holdings are what they *carry*: personal kit, drugs, and information.

### 2.11 Jawa Trade Moot — pre-ship technique, held by kin and taught by quest

| holds | why | status |
|---|---|---|
| **The clan's own gear and ion doctrine** | v3 proposes `guy762_ResearchKotOR_jawa` and `RSW_JawaIon_Weaponry` as **jawa-special** (known at colony start) — the player IS a Jawa | SOURCED as a proposal (`faction_locked_trees.md` §6). Manifest today: both `common`, T0 |
| **Crawler stills** — carried water, buried cisterns on the circuit | #1 — *"Manufacture (crawler stills)… condensers on the crawler spine"*; §"What the player learns here": *"crawler stills, sand-proofing, animal handling, low-tech ion work"* are *"keys, in the Axis 18a sense"* (`faction_roster_v2.md` §11) | SOURCED — as **quest-taught technique**, the roster's own word. §6 Q9: techprint, or quest reward? Position: quest reward, because the roster already says so and the Moot cannot ally |
| **Sand-proofing** — keeping a mechanism working in sand | #2 — *"sand fouls mechanisms (L12)"* (`faction_equipment_clusters.md` Part 2, the Tusken row) | PROPOSED holding, same route as the stills |
| **Droid parts and low-tier droid repair** | trader type *droid parts*; owner 2026-09-03: the Jawa keep *"low-tier repair, reconstruction and maintenance"* | SOURCED — and this is the player's *starting* competence, not a Moot print |

What they need to survive (#1): water on a crawler that never stops. The stills are the whole
answer, and the roster already makes them a lesson rather than a purchase — which is right for a
faction that will trade with kin but never stand beside them.

### 2.12 The Junkers — warcaskets, big flame, sump gas; taken off the dead

| holds | why | status |
|---|---|---|
| **All warcasket technology** | owner ruling 2026-09-03: *"all things warcasket is uniquely Junker… earned from the Junkers themselves"*; manifest today: 7 `VFEP_*` rows held by `Junkers` | SOURCED — one of "those four". BUILT: `Warcasket_BuildPathCut.xml` closes the player build path; the salvaged-shell route is designed, unbuilt (`faction_roster_v2.md` §12 Q1/Q2). ⚠️ `VFEP_WarcasketRemoval` is in the manifest's Junker set; v3 argued it must stay **common** (freeing a welded pawn is a mercy) — §6 Q10 |
| **Big flame** — flamethrowers and heavy projectors | owner ruling 2026-09-04: *"BIG flame weapons — flamethrowers and heavy projectors — join the Junker unlock"*; small flame stays common (`design/Jawa/canon_reintegration_plan.md` §6) | SOURCED. Manifest today: `RR_IncendiaryWeapons` `common` T0 (small flame, correct); no big-flame row surfaced in the probe — it is a **per-unlock split of recipes**, not a row move, per that ruling |
| **Sump gas** — tar, derrick pumping, barrel yards, the poured moat that lights | #1/#2 — the Sump's *"Junker stations — pumping derricks… holding ponds, barrel yards… the biome's only industry, law, and light"* (`biomes/the_sump.md` §7b, §8); owner: *"Junkers had originally been thought to hold… sump gas tech"* | SOURCED as environment; PROPOSED as the holding's shape: **crude tar and sump-gas extraction** is Junker, **refined chemfuel** is common/Imperial by tier (§4). No research row is Sump-specific yet (the biome's kit is `SUMP_MECHANICS_1`) |
| **Fire-spewing suicide droids** | `DROID_UNIFIED_FRAMEWORK_DESIGN.md` §: *"1–2 atrocious fire-spewing suicide droids"* | SOURCED as a Junker pawn kind; NOT a holding — nobody wants the print |

What they need to survive (#1): they manufacture nothing and steal water. Their holdings are the
three things they *do* make — welded steel, fire, and tar — and the route is **raid loot and
quest reward only**: `PirateBandBase` gives them no traders and a loot maker with no techprints
(`faction_locked_trees.md` §4.2, §5.1). This is the one faction where "earn it" means "kill for it".

## 3. Critical path vs side-quest

Owner: *"Only the critical path should be normalized. Side-questing is a good thing."*

**The rule applied:** a holding is NORMALIZED when the player *needs* it to finish the campaign
or to survive the world they are on, so an ordinary route (trade with a neutral faction, a
common quest, or loot from a faction you will fight anyway) must exist. A holding is SIDE-QUEST
when the player can win without it; it may then sit behind a hard faction, a long courtship, or
a raid the player chooses to run, and that difficulty is the content. The bowcaster is his worked
example: nobody *needs* a bowcaster.

The critical path, per `faction_roster_v2.md` §1 ENDGAME PURPOSE and §5 ENDGAME WILDCARD: get
the ship whole (ship-only, Memory Core), get off-world (Hutt alliance or Hutt debt; the Empire
holds orbit), and survive the biomes the road crosses. So *survival* holdings are NORMALIZED
and *ambition* holdings are SIDE-QUEST.

| holding | holder | class | ordinary route |
|---|---|---|---|
| The fence (markup buying) | Hutt | NORMALIZED | it *is* the ordinary route — §4 |
| Spice / drug trade | Hutt | SIDE-QUEST | drugs are not survival; the Hutts are hostile-by-default and courting them is the campaign's long grind |
| Contraband tibanna | Hutt | SIDE-QUEST | the embargo plot is optional (`tibanna_embargo_plot_spec.md`) |
| Coercion hardware | Hutt | SIDE-QUEST | |
| Kajidic equipment | Hutt | SIDE-QUEST | |
| Vacuum capability | Empire | NORMALIZED (endgame) | loot from any Imperial installation raid — the player must fight them anyway (§5). The deluxe exposure tier is how you walk a hull |
| Drop pods | Empire | SIDE-QUEST | a convenience; caravans and the ship exist |
| Smaller shuttles | Empire | SIDE-QUEST | |
| Hyperspace | Empire | NORMALIZED (endgame) | §5 — the last stolen thing, or the campaign has no ending |
| Imperial archives (Sith/Jedi/Republic gear, cloaking, positronic) | Empire | SIDE-QUEST | already Empire-tagged, already optional |
| Vaporator make/mend | Homestead | NORMALIZED | Homestead is `raidsForbidden`, friendly, Medium caravans — the easiest print on the planet. Water is survival |
| Cistern storage | Homestead / Deepwater | NORMALIZED | two neutral holders |
| Heat apparel (cheap tier) | Tusken | NORMALIZED as *content*, SIDE-QUEST as *Tusken print* | the cheap heat wrap must be reachable without courting Tuskens (they start at −80 and never build roads) — so the **cheap tier is common** and the Tusken-held print is the *better* wrap. §6 Q2 |
| Tusken Raider equipment; venom | Tusken | SIDE-QUEST | adoption quest chain, the whole point |
| Droid construction | Enclaves | SIDE-QUEST | the branch is a *choice* (ally or raid), and the droid brain caps it regardless — the campaign is winnable with restrained salvage droids |
| Hydrogen cracking | Enclaves | SIDE-QUEST | |
| Wet-bulb kit (sealed suit, blower, boiler) | Wildsteam | NORMALIZED as *content* | the Fever Wood and Greentide are *on the road* (Sporefall "on the road", owner); Wildsteam is friendly by default and sells both survival kits (`the_greentide.md` §8, "Jawa presence: both survival kits sold"). Route: trade, easy |
| Bowcaster | Wildsteam | SIDE-QUEST | the owner's example |
| Greenwood / tree-planting | Wildsteam | SIDE-QUEST | |
| Rebreather / dive | Deepwater | NORMALIZED | the Compact trades with everyone; the seas hold the Rakatan wreck and the dive maps — reachable by ordinary trade |
| Purification / desalination | Deepwater | NORMALIZED | water is survival; Deepwater is the neutral supplier |
| EMP | Deepwater | SIDE-QUEST | a counter, not a need |
| Sonic | Hive | SIDE-QUEST | −100 start, "not permanently" hostile; a mid-game wedge, and sonic is thin by ruling |
| Hivetech | Hive | SIDE-QUEST | |
| Deep-rock condensate | Hive | SIDE-QUEST | |
| Gene ladder | Helix | SIDE-QUEST | the temptation, by design (`faction_locked_trees.md` §5.3) |
| Kolto / advanced implants | Helix | SIDE-QUEST | |
| Closed-loop recycling | Helix | SIDE-QUEST | |
| Hunter equipment / disruptors | Blackstar | SIDE-QUEST | |
| Combat drugs | Blackstar | SIDE-QUEST | |
| Clan gear / ion doctrine | Trade Moot | NORMALIZED (jawa-special) | known at start |
| Crawler stills / sand-proofing | Trade Moot | NORMALIZED | quest-taught by kin who are friendly by default; water is survival |
| Warcaskets | Junkers | SIDE-QUEST | *"What a player who never fights them gets: no warcaskets. That is the whole point"* |
| Big flame | Junkers | SIDE-QUEST | small flame is common for holding wildlife off; big flame is a want |
| Sump gas / tar | Junkers | SIDE-QUEST as *Junker print*; the crude tier is biome-observable | you can dig tar in the Sump without a Junker's permission (`the_sump.md` §7b "Player play: dig the tar…"); the *pumping* print is theirs |

Count: **11 NORMALIZED, 24 SIDE-QUEST** (two rows split by tier). Every NORMALIZED holding has a
friendly-by-default or neutral holder (Homestead, Deepwater, Wildsteam, Trade Moot, the Hutt
fence) or is Imperial loot the player must fight for regardless. No NORMALIZED holding sits
behind a −100 start or a raid-only route. That is the check the build step should re-run after
rows are assigned.

## 4. The Hutt fence

Owner: *"Yes, price is the gate, and likely the only route to marked-up imperial goods. For the
drugs, chemfuel, infrastructure that's a mix between Imperial and Junker depending on how
advanced it is."*

### 4.1 What the fence is

The Cartel manufactures nothing it holds (`faction_equipment_clusters.md` Part 2: *"nothing they
manufactured — it is all purchased"*). Its holding is **access at a price**: a second, dearer
copy of every other holder's techprint, plus the only market for Imperial goods that were never
for sale. The fence never replaces the holder's own route; it is the *expensive shortcut past
courtship*.

| primary holder | what the fence carries | how it interacts |
|---|---|---|
| **Empire** | marked-up Imperial goods — pods, shuttle parts, vac gear, spacer plate | the fence is the **only trade route** for these (owner). Loot remains the *free* route (§5). No techprint the Empire holds is fenced *as a print* — the Cartel sells the goods, not the plans; plans are stolen (§5) |
| **Homestead, Deepwater, Wildsteam, Trade Moot** (the neutral/friendly holders) | their prints, at markup | pointless for a player on good terms with them; useful for a player who has *burned* one of them (attacked a Compact water convoy, cut a Moot claim) — the fence is the second chance, priced |
| **Helix, Hive, Blackstar** (the neutrals-to-cold) | their prints, at markup | the shortcut past a long courtship — "buy the gene ladder from a Hutt" is exactly the pride-marked temptation the theology wants |
| **Enclaves** | droid prints at markup | canon-consistent: *"the Cartel occasionally still hires them"* (`faction_roster_v2.md` §5 Origin) and the Enclaves hate the Hutts — a fenced Enclave print deepens the grievance, which is a feature |
| **Junkers** | warcaskets at markup? | **NO** — position: the fence does not carry Junker prints. The Junkers are the Cartel's talent intake (§12 elevation pipeline), not a supplier, and *"warcaskets… can only be approached by earning those tech prints from the Junkers themselves"* is his ruling. §6 Q11 |
| **Tusken** | — | **NO** — the Tuskens destroy captured tech and sell nothing; there is nothing to fence |

### 4.2 The drugs / chemfuel / infrastructure split, made concrete

"Depending on how advanced it is" — a tier line, with the Junkers below it and the Empire above,
and the Hutts fencing both ends:

| subject | crude / low tier → **Junker** (raid loot) | refined / high tier → **Imperial** (loot/theft) or fenced | stays **common** |
|---|---|---|---|
| **Drugs** | none — the Junkers hold no pharmacy | glitterworld medicine, advanced combat stims → Imperial loot, fenced at markup; the *spice* trade itself is the Hutts' own (§2.1) | psychoid, smokeleaf, penoxycyline, wake-up, basic medicine — survival and vanilla-T0 (`DrugProduction`, `PsychiteRefining` etc. are `common` today, correctly) |
| **Chemfuel** | crude tar, sump-gas pumping, the poured moat — the Sump's derrick industry | refined fuel processing, astrofuel, deep oil wells → Imperial loot; astrofuel is already ship-only (`VGE_AstrofuelRefining`) | biofuel refining, basic chemfuel — vanilla T1 and survival for generators |
| **Infrastructure** | scavenged power, degraded generators — nothing the player would want a print for | advanced fabrication, ultra-components, durasteel-grade materials, hypertech fabrication → **"plans you need to steal"** (§5) | electricity, batteries, solar, wind, machining, basic fabrication — every faction has them, T0/T1 |

The reading of his sentence this doc commits to: **the Junkers hold the *dirty* end and the Empire
holds the *clean* end of the same three subjects, and the Hutts sell you either end at a markup
if you cannot or will not go and get it yourself.** Nothing in the middle is faction-held; the
middle is the common economy.

## 5. The Empire — loot and theft, never trade

`permanentEnemy: true` (`faction_roster_v2.md` §2). No trader, no caravan but military and water
convoys, no quest reward from a faction that cannot be at peace. So every Imperial holding
reaches the player by exactly two routes:

1. **Loot** — what a dead stormtrooper or a raided installation physically yields. This needs
   no techprint: charge rifles, marine plate, vac gear, a shuttle's parts are *items*. The
   existing mechanism covers it (`ThingSetMaker_Techprints` in a raid loot maker and map-gen
   loot, `faction_locked_trees.md` §2.4, §2.8) and the Empire already carries the `Empire`
   `categoryTag`, so an Empire-held print already drops from Imperial raid loot with no new
   wiring. **What is owed is only the row assignment** (build step).
2. **Theft — "plans you need to steal"** (owner, marked TBD by him). The proposal below.

### 5.1 The proposal: stolen plans — PROPOSED, needs his ruling

**Shape.** A *plan* is a techprint that is never in any stock and never in raid loot. It exists
only inside an Imperial installation, as a **thing on the map** — a data-core, a safe, a
fabrication bay's controller — that the player must reach, take and carry out. Three concrete
choices, each a yes/no:

| choice | position | why |
|---|---|---|
| **What a plan unlocks** | the *industrial-material* recipes only: advanced components, ultra-components, durasteel-grade materials, hypertech fabrication — "industrial materials to manufacture in your factories" | his words; and it keeps the plan class small (≈4–6 subjects) so each theft is an event, not a grind |
| **Where a plan lives** | as a **map-spawned item inside Imperial settlements and the large spaceport**, never in orbit-only holdings | the 3 surface seats and the spaceport are raidable; the 7–8 orbital holdings are not world tiles. A plan that lives only in orbit is a plan the player cannot steal until the endgame — which is the right place for **hyperspace**, and the wrong place for everything else |
| **How a plan is delivered** | the vanilla techprint item, carried out and applied at a research bench, with `heldByFactionCategoryTags` = `Empire` and the row's `techprintCount` set so **no other route can complete it** | the pure-XML mechanism stands (item file §4). The one thing it does not do is *place* the print on the map deterministically — that is a settlement-generation or quest step, and it is the one piece that may need a QuestScriptDef (`rimworld-quests` skill) rather than a `StockGenerator` |

**Hyperspace specifically.** Position: hyperspace is the single plan that lives in orbit, so it
is the *last* theft — reachable only once the Hutt orbital route (alliance or settled debt) has put
the player on the station, and the Empire's orbital holdings become raidable. That makes
"true hyperspace" the campaign's closing act rather than a mid-game shopping item, and it ties
the Empire's endgame holding to the Hutt endgame route the roster already designed. ⚠️ Whether
hyperspace is a *research row* at all is UNMEASURED — nothing in the manifest names it; the
gravship tree is ship-only via the Memory Core and is a different thing (the ship flies; it does
not jump). This is content to author, not a row to retag.

**Drop pods and smaller shuttles.** Position: **loot, not plans.** They are items and buildings
the Empire uses in every raid; the player who beats a drop-pod strike has the pods. Their
research rows (`TransportPod`, `Shuttles`) become Empire-held prints that drop in raid loot —
route 1, nothing new.

**Vacuum capability.** Position: **loot.** `OrbitalTech` (Odyssey, T0 `common` today) is the
gate on the vacsuit; making it Empire-held and dropping it from installation raids gives the
deluxe exposure tier a story. The moderate tier (Deepwater's rebreather + boil suit, partial
vacuum with Odyssey) stays the *local* answer, per the exposure matrix's "locals make their own".

### 5.2 What the Empire is NOT the holder of

Growth vats, gene banks, mechanitor gear and cryptosleep all appear in the Imperial dossier's
"possessed" list. They are not Imperial *holdings*: genetics is the Helix's signature, droids are
the Enclaves', and the mechanitor rows are already cut. A faction that owns everything holds
nothing; the Empire holds what only an off-world power could have.

## 6. Open questions for the owner

Each has a position so the answer is yes/no.

| # | question | position |
|---|---|---|
| Q1 | **Wildsteam's jungle tech is the wet-bulb kit** — sealed suit, dry-air blower, boiler/steam-works, blower-door domes — held by them and sold to the player as a survival kit. Yes? | **Yes.** It is already authored as their home-ground culture in `the_greentide.md`, and it is the one thing a fur-bearing people needs to live at 45 °C wet-bulb. Nothing else in their dossier is unique |
| Q2 | **Tusken heat apparel is cloth, in two tiers**: the cheap heat wrap is common (anyone can sew one), the *Tusken* print is a better wrap with real heat numbers. Yes? | **Yes.** The cheap tier must be reachable without courting a −80 faction that builds no roads; the Tusken-held tier is the adoption chain's reward. A powered "suit" is against their sacrilege rule |
| Q3 | **Hyperspace is the last theft, in orbit, after the Hutt route** — not a mid-game print. Yes? | **Yes.** It closes the campaign and ties the two endgame factions together |
| Q4 | **Atmospheric condensers**: the Homestead holds the vaporator print; the Empire's condensers are the same lineage and are NOT a separate Imperial holding. Yes? | **Yes.** One water-from-air print, one holder. The Empire's version is fiction for why garrisons can be anywhere |
| Q5 | **Hydrogen cracking** for the Enclaves — author it as a new holding (a cracking works that consumes a water tile for fuel), or leave the Enclaves at droid construction only? | **Leave it at droid construction for now.** Droids are the branch; cracking is why they hold water tiles and needs no print to do that job. File it as a v2 want, not a gap |
| Q6 | **EMP** (a T1 vanilla-adjacent row today): lock it to Deepwater, or leave it common and give Deepwater only the *traps/turrets*? | **Lock the EMP *weapons*; leave the EMP *grenade/basic* row common.** The equipment matrix names EMP as Deepwater's primary harm, but a T1 counter to droids should not require courting anyone |
| Q7 | **Battle-droid mass production**: Hive (v3's proposal, canon origin) or Enclaves (manifest today, his 2026-09-03 droid ruling)? | **Enclaves.** His ruling is later and explicit; the Hive keeps *hivetech*, and its droids are fiction for its siege doctrine. Do not split the droid branch across two holders |
| Q8 | **Closed-loop water recycling** as a Helix holding — new content, or drop? | **Drop for now.** The Helix's signature is genes; recycling is a siting excuse. Same disposition as Q5 |
| Q9 | **Crawler stills / sand-proofing**: techprint from the Moot's traders, or quest-taught (the roster's word)? | **Quest-taught.** The Moot cannot ally, sells at kin prices, and the roster already calls these "keys… taught by quest chains". A techprint in a stall cheapens the kinship beat |
| Q10 | **Warcasket removal** — Junker-held (manifest today) or common (v3: freeing a welded pawn is a mercy)? | **Common.** Gating a rescue behind allying the welders is the wrong story |
| Q11 | **Does the fence carry Junker prints?** | **No.** Junker tech is "from the Junkers themselves" by his ruling, and the Junkers are the Cartel's intake, not its supplier |
| Q12 | **Big flame**: is the Junker unlock the *weapons* (flamethrower, heavy projector) only, with incendiary shells/grenades/launcher common? | **Yes** — that is the 2026-09-04 ruling as recorded; restated here only because the manifest has no big-flame row and the build step will need to split recipes, not move rows |
| Q13 | **Sump gas / tar**: Junker-held *pumping* print, with tar-digging free in the biome? | **Yes.** The Sump sheet already lets the player dig; the derrick is the Junkers' industry |
| Q14 | **Spice** (`KOTOR_Research_Spice`): accept that it stays common because an implant row depends on it, or re-point that prerequisite so the Hutts can hold spice? | **Re-point the prerequisite** (`KOTOR_Research_AdvImplants` should not need spice). Spice is the single most Hutt thing on the planet and should be theirs |
| Q15 | **Blackstar combat drugs** as a holding — yes, or fold into the common drug rows? | **Yes, hold the combat stims only.** The hunter on a water clock is the one pawn who needs them |

Also flagged, not a question: the manifest today carries two holders that are **not campaign
factions** — `Rakata` (5 `RUT_Antiq_*` rows) and `RustCathedralDroids` (`GravBionics`,
`GravWeapon`, plus 2 `source_gate=faction:RustCathedral_boon` rows). Both are event/arc gates
riding the same column, not faction techprints. They are out of scope here and should not be
re-tagged by the faction build step.

## 7. What this does NOT decide

- **The research tab/tree roster.** The seven-tab table is SUPERSEDED (`research_tree_taxonomy.md`
  §1); his "around 12 trees" ruling replaced it and nothing has been ruled in its place. v3/v4
  (`research_review/faction_locked_trees.md`, `restructured_model_v4.json`) are proposals he has
  not ruled. This doc therefore names holdings as **subjects**, never as tabs, and the `tab`
  column values quoted from the manifest (`The Junker Yards`, `The Foundry Hive`, …) are the
  draft's labels, not rulings.
- **Row assignment.** No `source_gate`/`access`/`holder` value in
  `infrastructure/output/research_manifest_draft.csv` is changed by this pass. "Manifest today"
  lines record the delta for the build step (`TECHPRINT_FACTION_GATING_1`'s verify list), which
  is someone else's.
- **`categoryTag` values.** Which new tags to mint (v3 proposed `GeonosianHive`,
  `AscendantHelix`, `HuttCartel`, `WildsteamClan`, `BlackstarCompany`) and the mod-stack grep
  each `Outlander` re-tag needs are build-step work. This doc only establishes *that* each of
  the eleven tag-bearing factions needs a tag of its own if it holds anything.
- **The ship-only class and the Memory Core reveal trigger.** Unchanged and untouched; the
  gravship tree is not an Imperial holding (§5).
- **Techprint counts, costs, tiers.** Not this doc's.
- **New content implied above** — vaporator repair, a desalination row, the cheap/Tusken heat
  wraps, a hyperspace row, the stolen-plan placement — is *named* so it can be filed, not
  specced. Each is a `rimflow file` for the seat that owns it, after his §6 answers.
