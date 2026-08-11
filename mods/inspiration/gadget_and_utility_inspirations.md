# Star Wars Non-Weapon Gadget & Utility Mod Inspirations

> # ⚠️ FOR CONSIDERATION — NOT DIRECT IMPLEMENTATION
>
> **These are resources to consider, not assignments or instructions to install or implement them directly.**
>
> This document is an **inspiration / source-mining dossier for the Claude Code development thread** working on the RimWorld 1.6 + Odyssey Jawa / Kolyska gravship campaign.
>
> Every candidate below should be independently inspected before use. Claude Code should decide whether a useful idea is best handled by:
>
> - installing the mod as-is,
> - enabling only part of it,
> - Cherry-Picking or XML-patching specific defs,
> - re-labeling / re-balancing a mechanic,
> - using the mod only as a design or code reference,
> - reproducing the concept locally with original assets/code where appropriate,
> - or rejecting it.
>
> **Do not interpret inclusion here as approval for the actual mod stack.**
>
> Current campaign constraints still govern: the **gravship + onboard Factory are the only scalable player progression trees**; recovered technology should often be finite, scavenged, restored, traded, or quest-earned rather than becoming another unrestricted manufacturing ladder. See the project docs `required_mods.md`, `ship_deck_plan.md`, `ship_distinctive_features.md`, `jawa_xenotype_and_religion.md`, `desert_world_design.md`, and `faction_roster_v2.md`.

**Research date:** 2026-08-11  
**Target:** RimWorld 1.6 + Odyssey  
**Theme:** Jawa salvage expedition / ancient Factory gravship / Star Wars-flavored desert world

---

## 1. Design Thesis

Star Wars technology is not defined only by blasters, lightsabers, and turrets. Much of its visual and cultural identity comes from **small, specialized, tactile devices**:

- restraining bolts,
- droid chargers,
- power droids,
- repair tools,
- hydrospanners / fusioncutters,
- medpacs,
- scanners,
- holoprojectors,
- comlinks,
- slicing devices,
- data spikes,
- environmental survival equipment,
- portable diagnostic equipment,
- navigation displays,
- utility harnesses,
- field electronics,
- bizarre single-purpose machinery.

This is especially appropriate for the Kolyska campaign because the Jawas are **scavengers and restorers rather than pristine technological manufacturers**. The strongest gadget design is therefore not necessarily "research X and craft unlimited copies." Many devices become *more* interesting if they are:

- found in ruins,
- stripped from enemy equipment,
- traded for,
- restored from broken state,
- recovered from old ship compartments,
- unique or uncommon faction equipment,
- or produced only after the corresponding original Kolyska subsystem is restored.

The target aesthetic is **dense technological material culture**: the ship should contain loose tools, chargers, diagnostic boxes, power couplers, droids, projectors, cables, repair equipment, mismatched consoles and recovered devices. Inventory itself should become scenery.

---

# 2. Highest-Priority Star Wars-Native Sources

## 2.1 Outer Rim - Droid Depot

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=3096501398  
**Current evidence:** Workshop changelog explicitly reports a RimWorld 1.6 update in July 2025.  
**Disposition:** **VERY HIGH PRIORITY TO INSPECT. Potential install + heavy restriction/patching.**

The mod adds droids **and droid-related items/buildings**, making it one of the strongest native Star Wars gadget sources rather than merely another combat mod.

### Particularly interesting content

Investigate the current defs for:

- **MSE Repair Droid**
- **FX-7 Medical Droid**
- **GNK Power Droid**
- **DUM Pit Droid**
- **R-series astromechs**
- **Protocol droids**
- **Imperial labor droids**
- **restraint bolts**
- **restoration / repair kits**
- **data spikes**
- **droid replacement parts**
- **droid charging infrastructure**
- related utility equipment and buildings

### Star Wars / campaign uses

**Restraint bolt** requires no reinterpretation at all. It is an iconic Star Wars nonweapon device and could become common equipment for Hutts, Imperials, bounty hunters, Jawa droid handlers, and droid slavers.

**Data Spike → Slicing Spike / Scomp Spike.** Potential mechanic donor for reprogramming captured droids or interacting with technological systems.

**Restoration Kit → Droid Restoration Kit.** Extremely strong Jawa item: a dead or disabled droid becomes a salvage opportunity instead of generic scrap.

**GNK Power Droid** is nearly perfect environmental storytelling — a walking battery wandering around the ship, factory floor, dock, or settlement.

**DUM Pit Droid / MSE / astromech** create visible specialized machine labor without making the setting feel like generic RimWorld mechs.

**Charging stations / couplings** can make droid areas visibly technological and give droids logistical requirements.

### Major campaign caution

If the mod provides unrestricted **Droid Factory** production, that conflicts with the existing Jawa doctrine:

> "We give the second hand to what others discarded; we do not breed new hands."

The preferred campaign interpretation is likely:

- recover droids,
- repair droids,
- reactivate droids,
- buy rare droids,
- capture / reprogram droids,
- occasionally receive quest droids,

rather than mass-printing unlimited new minds/chassis.

Claude should inspect how cleanly manufacturing can be disabled while retaining restoration and utility content.

---

## 2.2 Star Wars KotOR Weapons and Armor

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=2938932438  
**Official 1.6 KotOR collection:** https://steamcommunity.com/sharedfiles/filedetails/?id=3254515866  
**Disposition:** **TOP SOURCE-TEARDOWN TARGET. Do not assume wholesale installation.**

Despite the title, the Workshop page explicitly says it adds:

> weapons, armor, **gadgets**, equipment, and the KotOR upgrading system.

That makes it one of the most important sources to enumerate.

### Why this deserves source inspection

Knights of the Old Republic has a much richer tradition of:

- belt devices,
- personal shields,
- implants,
- stimulants,
- specialist equipment,
- utility technology,

than most RimWorld Star Wars packs.

Claude should inspect the installed/current source and enumerate **every nonweapon ThingDef / apparel / utility item / consumable / special gadget**, with:

- defName,
- label,
- graphic path,
- comps/classes,
- stat effects,
- recipes,
- research prerequisites,
- workbenches,
- whether it occupies the utility slot,
- whether NPCs spawn with it,
- whether it is tradeable / questable,
- whether its mechanics can survive independently of the KotOR weapon-upgrade system.

### Likely campaign role

KotOR technology is ideal as **Old Republic / ancient technology**:

- ancient ruins,
- recovered pre-Imperial military stock,
- weird high-quality devices the Jawas cannot reproduce initially,
- black-market Hutt equipment,
- lost ship lockers,
- relic technology carried by rare NPC specialists.

This preserves technological archaeology rather than making the Factory a universal replicator.

### Major caution

The native weapon/equipment **upgrading system** may constitute a second progression economy. Consider keeping selected gadgets while suppressing the broader upgrade ladder.

---

## 2.3 Star Wars KotOR Resources and Materials

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=3254370945  
**Disposition:** **HIGH PRIORITY AS ITEM / CONSUMABLE / ART / VOCABULARY DONOR.**

Workshop description explicitly says the mod adds:

- resources,
- crafting materials,
- consumables,
- other items from across Star Wars.

Search-visible examples include **Kolto** and **Armorweave**, with other KotOR resources and consumables present in the package.

### Why this matters

Changing the *noun vocabulary* of material culture has enormous thematic payoff. Generic RimWorld stacks can instead become:

- power cells,
- droid components,
- armorweave,
- Kolto or field medical consumables,
- adrenals,
- specialized electronics,
- rare Old Republic components,
- ship maintenance materials,
- faction-specific consumables.

### Possible Kolyska use

Some items could be converted into **finite restoration feedstocks** needed to awaken damaged ship systems or droids.

That is stronger than simply requiring "3 advanced components," because recovering the correct strange part gives salvage expeditions narrative meaning.

### Claude inspection questions

- Which items already have useful art?
- Which are resources vs. consumables?
- Which introduce production loops?
- Which can be made loot/trade-only?
- Which integrate with the KotOR droid package?
- Which are good candidates for ancient salvage rather than craftables?

---

## 2.4 Outer Rim - Furniture & Decor

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=2919553599  
**Disposition:** **HIGH-VALUE ENVIRONMENTAL SOURCE; likely safe to consider wholesale if compatible.**

The Workshop page states that the module contains:

- furniture,
- decals,
- joy/recreation buildings,
- statues,
- miscellaneous furniture/decor content.

It can also run standalone, with vanilla material/research substitutions if Outer Rim Core is absent.

### Campaign value

A ship full of RimWorld chairs, lamps, shelves and recreation buildings will still read visually as RimWorld even if every pawn carries a blaster. This type of mod can change the **background technological language**:

- control rooms,
- cantinas,
- machine rooms,
- shrines,
- living spaces,
- droid bays,
- loading areas,
- faction settlements.

Claude should inspect all defs and identify items suitable for:

- Kolyska,
- Imperial installations,
- Hutt compounds,
- moisture-farmer settlements,
- droid enclaves,
- Old Republic ruins.

---

# 3. Holograms and Information Technology

## 3.1 EGI: Holograms and Projectors

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=2979598490  
**Optional old size-reduction fork:** https://steamcommunity.com/sharedfiles/filedetails/?id=3304159909  
**Disposition:** **VERY STRONG VISUAL / FUNCTIONAL CANDIDATE.**

The mod provides a large library of holographic imagery plus functional projectors. The system supports multiple projector behaviors such as recreation, ideological influence, learning, and tutoring, depending on configuration/content.

### Star Wars transformations

Potential labels / uses:

- **Holotable**
- **Navigation Hologram**
- **Navicomputer Projection**
- **Ship Diagnostic Projector**
- **Tactical Hologram**
- **Droid Schematic Projector**
- **Holonet Entertainment Unit**
- **Imperial Propaganda Projector**
- **Bounty / Wanted Hologram**
- **Ancestor Holoprojector**
- **Training Hologram**
- **Planetary Survey Projection**

### Kolyska-specific uses

This ties directly to the existing "haunted former crew / holograms" ship-identity thread.

Possible distinction:

- actual ghosts = Afterlife mechanism,
- recorded dead = holographic records,
- Cradle-Mind occasionally uses projectors to show memories/diagnostics,
- map room = active holoprojection,
- repaired wings gain specific diagnostic displays.

### Caution

The asset pack is large. Do not assume every image should be exposed. A **small curated Star Wars subset** may give a stronger visual identity than hundreds of unrelated holograms.

The older MINIFIED fork explicitly says it is probably no longer needed and recommends the original, so treat it only as evidence that size/performance was historically a consideration.

---

## 3.2 Holograms And Projectors — Lite / predecessor

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=2847321165  
**Disposition:** **FALLBACK OR SIMPLE CODE DONOR.**

The original author describes this as the older "lite" predecessor to EGI.

Potential virtue: the campaign may need only a few strong holoprojector functions, not hundreds of art variants.

Claude should compare:

- dependencies,
- code complexity,
- art footprint,
- functionality,
- 1.6 behavior,
- ease of reskinning.

---

# 4. Wearable Utility Gadgets and Field Equipment

## 4.1 More Utility Packs (Continued)

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=3249560356  
**Disposition:** **IDEA / CODE / DEF DONOR FIRST. DO NOT ASSUME CURRENT INSTALLABILITY.**

**Important current warning:** Steam search/indexing presently returns inconsistent status and can show this item as removed/incompatible, even though indexed description content is still available. Verify directly in Steam/RimSort before considering it a dependency.

The indexed description identifies several utility items, including a **Robotic Rig** and other wearable packs.

### Especially valuable concepts

**Robotic Rig → Industrial Manipulator / Jawa Utility Harness**

A wearable robotic arm with precision multitool functionality is almost perfect for a Jawa engineer. Visually, a tiny Jawa carrying an oversized mechanical arm is excellent semi-comic Star Wars design.

**Trauma Kit → Field Medpac**

Very straightforward Star Wars translation.

**Survival Pack → Desert Survival Rig**

Good for:

- homesteaders,
- bounty hunters,
- Tuskens,
- explorers,
- Jawa scavenging parties.

**Command / radio-oriented pack → Squad Comlink / Tactical Comlink Array**

Star Wars armies should visibly carry communications technology.

### Design virtue

Utility-slot competition can make gadgets a **loadout choice** instead of pure stat inflation.

### Caution

If this page is actually unavailable/currently broken, use it strictly as a mechanic/design reference and implement nothing directly without source/license inspection.

---

## 4.2 Dubs Rimkit

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=832333531  
**Disposition:** **STRONG SMALL MOD / MECHANIC DONOR. Verify directly because Steam language/index pages conflict.**

A current localized Workshop page exposes **1.6** among supported versions and shows a July 2025 update, although some English-index results inconsistently flag the item as unavailable. Confirm in Steam/RimSort before adoption.

The concept is excellent:

- wearable **Medkit**
- wearable **Repair Kit**
- field bandaging
- construction/repair assistance
- component salvage associated with repairs

### Star Wars translation

**Medkit → Medpac / Trauma Medpac**

**Repair Kit → Fusioncutter & Repair Kit / Hydrospanner Kit**

This resonates unusually well with the campaign because **The First Fusioncutter** is already the Jawa religion's singular modest relic.

### Preferred design emphasis

If reimplemented or patched, prefer **qualitative actions** over generic percentage bonuses:

Good:
- perform emergency field bandage,
- repair a damaged device,
- recover a damaged component.

Less interesting:
- flat +X% construction speed.

---

## 4.3 Survival Tools Reborn

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=3554664966  
**Testing branch:** https://steamcommunity.com/sharedfiles/filedetails/?id=3663736701  
**Disposition:** **EXCELLENT TOOL / VISUAL DONOR; wholesale progression needs scrutiny.**

The Workshop page currently identifies the main branch as **Mod, 1.6**.

The mod supplies numerous physical work tools. This is extremely valuable because a pawn's profession becomes visually legible instead of existing only as a hidden skill number.

### Proposed Star Wars re-labels

| Generic tool concept | Possible Star Wars interpretation |
|---|---|
| Wrench | **Hydrospanner** |
| Power drill | **Fusion drill / rotary fusioncutter** |
| Pry bar | **Salvage lever / hull pry tool** |
| Precision scalpel | **Auto-surgical cutter** |
| Microscope / analysis tool | **Portable bioanalyzer** |
| Carbide pick | **Powered mineral cutter** |
| General toolkit | **Field engineering kit** |

### Jawa-specific value

A Jawa crew should visibly carry:

- wrenches,
- cutters,
- probes,
- diagnostic instruments,
- pry tools,
- salvaging equipment.

The player should be able to recognize "that is the repair Jawa" by looking at the pawn.

### Major caution

The native mod has a larger tool/progression system. Do not allow it to become an independent technological advancement ladder. Consider:

- permissive configuration,
- limited curated tools,
- remove its research progression,
- or use implementation/art concepts in a local small tool set.

---

## 4.4 Bluelibra's Personal Music Player

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=3537776760  
**Disposition:** **LOW-IMPACT FLAVOR CANDIDATE.**

The Workshop description says it adds a wearable personal music player that gives a small mood benefit.

### Star Wars translation

**Personal Music Player → Pocket Holoplayer / Audio Holocaster / Personal Holonet Player**

This is minor but useful civilian technology. Star Wars should contain ordinary personal electronics, not only military hardware.

Potential users:

- young colonists,
- spacers,
- smugglers,
- wealthy Hutt retainers,
- travelers,
- Jawa tinkerers who repaired one from scrap.

---

## 4.5 RimTek DigiPal

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=3500443258  
**Disposition:** **ADDITIONAL STRONG PERSONAL-GADGET LEAD DISCOVERED DURING VERIFICATION.**

This was not in the first pass but is worth recording because it is directly adjacent to the desired niche: a wearable **personal computer** utility device that can provide recreation and other effects.

### Star Wars translation

Potentially:

- **Datapad**
- **Wrist Datapad**
- **Slicer Datapad**
- **Personal Nav Computer**
- **Field Tactical Computer**

The native combat accuracy bonuses may be undesirable. The recreation / personal-computer behavior is the interesting part.

Claude should inspect this as a possible better implementation donor than a pure music player.

---

# 5. Doors, Ship Hardware, and Environmental Technology

## 5.1 Doors Expanded: Star Wars Edition (continued)

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=3550435517  
**Disposition:** **VERY STRONG ENVIRONMENTAL ADDITION.**

The current continuation explicitly says it was made compatible with **RimWorld 1.6** and that the doors were updated/tested.

Doors are an underrated Star Wars signal. The player interacts with them constantly, and they occupy major visible surfaces.

### Possible campaign roles

- Imperial blast door
- industrial bulkhead
- droid-access hatch
- battered Jawa retrofit door
- high-security sealed door
- mysterious ancient pod door
- shuttle-bay bulkhead
- carbonite reliquary entrance

This is particularly appropriate to the Kolyska because its seven function-pods are already conceived as **independently repairable and isolatable ship organs**.

---

## 5.2 Star Wars Lights

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=2265746202  
**Disposition:** **CONCEPT / ART REFERENCE ONLY AT PRESENT.**

Current Steam indexing marks the historical page as removed/incompatible.

Do **not** treat it as a current dependency.

### The valuable idea

Reproduce the Star Wars lighting *language*, not necessarily this mod:

- narrow luminous wall strips,
- inset floor guidance lights,
- tiny colored control indicators,
- warning strobes,
- dim machinery lights,
- localized task lighting,
- status lamps,
- dead vs. restored running lights.

This aligns directly with the accepted Kolyska feature:

> **running lights as a repair-progress bar**

Only repaired portions of the vessel should come alive visually.

---

# 6. Scanner / Survey Technology

## 6.1 Better Ground-Penetrating Scanner

**Steam (historical/current indexed page):** https://steamcommunity.com/sharedfiles/filedetails/?id=2809972387  
**Disposition:** **MECHANIC INSPIRATION; verify current Workshop status before dependency use.**

The mod allows a ground-penetrating scanner to be tuned toward a specific resource, with increased scan time as the cost.

### Star Wars translation

- **Geological Survey Array**
- **Subsurface Mass Scanner**
- **Mineral Prospector**
- **Ancient Survey Computer**
- **Orbital Survey Receiver**

### Why it fits the expedition

Landing, deploying a survey device, discovering what lies below, and deciding whether the resource is worth the danger is a very strong expedition loop.

### Critical campaign danger

The planet design deliberately makes **geography matter**:

- volcanic region = industrial feedstock,
- oasis = water,
- river = gems/resources,
- deep desert = salvage,
- etc.

If a targeted scanner effectively lets every landing generate any desired resource, it destroys that system.

Therefore a campaign implementation should probably:

- detect rather than create,
- respect biome/resource palettes,
- be slow,
- reveal local deposits only,
- or have finite / quest-gated capabilities.

---

# 7. Repair and Salvage Mechanics

## 7.1 Repair Workbench

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=733997423  
**Disposition:** **MECHANICS REFERENCE / POSSIBLE LIGHTWEIGHT SOURCE.**

Adds repair of item durability using a dedicated workbench.

The core concept — **repair as a deliberate industrial action** — is useful, although the campaign may want more specific consumables than a generic repair bench.

### Possible Star Wars / Kolyska implementation

Damaged equipment could require combinations such as:

- replacement actuator,
- sealant cartridge,
- power coupler,
- circuit board,
- salvaged control chip,
- armorweave patch,
- droid servo.

This turns broken gear into a salvage problem instead of a binary "use or scrap" decision.

---

## 7.2 Repairable Gear

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=2482478785  
**Disposition:** **STRONGER MECHANIC DONOR FOR MATERIAL-COST REPAIR.**

The Workshop description specifically includes **ingredient-based repair costs** proportional to damage, plus repair benches.

That is much closer to the campaign's desired logic than costless magical mending.

### Campaign relevance

This could inform:

- ordinary equipment repair,
- salvaged blaster restoration,
- armor repair,
- droid component restoration,
- sacred ship machinery recovery.

The important design principle is:

> repairing something should consume plausible feedstock and preserve the value of scavenging.

---

## 7.3 MendAndRecycle

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=735241897  
**Disposition:** **SECONDARY REPAIR / RECYCLING REFERENCE.**

Adds mending plus recycling recipes.

For Jawas, recycling itself is highly thematic, but unrestricted recycling can also become an efficient generic resource economy. Inspect for ideas rather than assuming adoption.

---

# 8. Droid Hacking / Portable Power Concepts

## 8.1 What the Hack?! (Continued)

**Current continuation:** https://steamcommunity.com/sharedfiles/filedetails/?id=3372841828  
**Original:** https://steamcommunity.com/sharedfiles/filedetails/?id=1505914869  
**Disposition:** **MECHANICS DONOR, NOT RECOMMENDED WHOLESALE WITHOUT MAJOR REVIEW.**

The overall mod creates a large mechanoid hacking/upgrading system — too broad to casually add to this campaign.

However, several concepts are extremely Jawa-like:

- hacking disabled mechanical units,
- consuming salvaged mechanoid parts,
- platform-based repair/maintenance,
- portable charging / support concepts,
- modifications applied to recovered machines.

### Star Wars translation

- mech hacking → **droid slicing**
- targeting hack → **restraining-bolt / control-module rewrite**
- portable charging → **droid power coupling**
- mech modification → **salvaged droid component installation**

### Campaign caution

Outer Rim Droid Depot already supplies native Star Wars droids. Prefer to adapt those systems or use What the Hack only as an implementation reference rather than creating parallel droid architectures.

---

# 9. Exotic / High-Tech Mechanics Worth Mining but Probably Not Installing

## 9.1 Recon And Discovery (Continued)

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=2035131107  
**Disposition:** **IDEA/CODE DONOR ONLY. CURRENT STEAM INDEX FLAGS REMOVED/INCOMPATIBLE.**

The older mod included very high-concept sci-fi systems such as:

- HoloDisks / personality recordings,
- holographic reconstruction,
- exotic medical/resurrection technology,
- teleportation-style systems.

### Useful Star Wars-derived concepts

**HoloDisk → Personality Holorecord / Memory Wafer**

Could support:

- recorded dead crew,
- old captain logs,
- ancient droid personalities,
- holo-messages,
- information relics.

**Holographic emitter → crew-memory projector**

Potentially useful for Kolyska's haunted/hologram identity.

**Exotic medical chamber → bacta / stasis inspiration**

### What to avoid

Do not import:

- routine resurrection,
- planetwide teleportation,
- general-purpose miracle technology,

because those become alternate high-tech progression systems and weaken Star Wars technological texture.

---

## 9.2 NanoTech

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=3719999155  
**Disposition:** **INTERACTION-MODEL DONOR, NATIVE FICTION PROBABLY WRONG FOR THE CAMPAIGN.**

The mod exposes discrete tools such as:

- Nano Repair Kit,
- Biocode Remover,
- Biocode Installer.

### Useful reinterpretations

**Biocode Remover → Security Slicer / Ownership Slicer**

**Biocode Installer → Ownership Encoder / Security Encoder**

**Nano Repair Kit → Sealant / Structural Repair Compound**

The interaction model is interesting: a physical device performs a particular technological intervention.

### What to avoid

Permanent autonomous nanotechnological self-healing feels too generic-glittertech and potentially too powerful. Prefer a finite repair action rather than ongoing regeneration.

---

# 10. Additional Star Wars Droid Source

## 10.1 Star Wars KotOR Droids

**Steam:** https://steamcommunity.com/sharedfiles/filedetails/?id=3047371944  
**Disposition:** **SOURCE-AUDIT ALONGSIDE OUTER RIM DROID DEPOT.**

The Workshop description advertises **22 KotOR-era droid types**, a droid faction/scenario material, and **droid-specific equipment**.

This should be compared directly against Outer Rim Droid Depot.

Claude should build a crosswalk:

| Question | Droid Depot | KotOR Droids |
|---|---|---|
| Droid chassis | inspect | inspect |
| utility droids | inspect | inspect |
| medical droids | inspect | inspect |
| repair droids | inspect | inspect |
| power/charging | inspect | inspect |
| restraint/control | inspect | inspect |
| droid-specific equipment | inspect | inspect |
| restoration mechanic | inspect | inspect |
| dependencies | inspect | inspect |
| manufacturing loop | inspect | inspect |
| visual fit | inspect | inspect |
| overlap/conflicts | inspect | inspect |

The answer may be:

- one package wins,
- both coexist,
- or one becomes an asset/mechanics donor only.

Avoid duplicate droid architectures unless there is a strong factional reason.

---

# 11. Suggested Faction Gadget Language

The most valuable end state is **not** "everyone can craft all gadgets." Technology should help differentiate factions.

## Jawa / Kolyska

Visual language:

- hydrospanners,
- fusioncutters,
- pry tools,
- scavenged scanners,
- patched medpacs,
- slicing spikes,
- restraint bolts,
- mismatched utility harnesses,
- diagnostic holograms,
- old datapads,
- GNK power droids,
- portable chargers,
- improvised cables and couplers,
- restored rather than manufactured devices.

Devices should look old, mismatched, over-repaired, and physically clutter the ship.

---

## Imperial Directorate

Visual language:

- standardized tactical comlinks,
- pristine scanners,
- encrypted datapads,
- control/ownership devices,
- restraint bolts,
- clean diagnostic screens,
- standardized medpacs,
- security doors,
- interrogation/control technology.

Imperial technology should be **uniform and institutional**, contrasting with Jawa bricolage.

---

## Hutt Cartel / Bounty Compact

Visual language:

- expensive holoprojectors,
- tracking devices,
- restraint technology,
- slicing tools,
- luxury datapads,
- bounty displays,
- black-market Old Republic devices,
- exotic medical consumables,
- smuggling scanners.

Hutt technology can be eclectic but expensive rather than improvised.

---

## Homestead / Moisture Farmers

Visual language:

- desert survival rigs,
- portable repair kits,
- vaporator diagnostics,
- rugged scanners,
- simple medpacs,
- old comlinks,
- jury-rigged agricultural electronics.

Technology should feel durable and repairable rather than futuristic.

---

## Free Droid Enclaves

Visual language:

- restoration kits,
- power couplers,
- data spikes,
- memory wafers,
- chassis parts,
- charging equipment,
- diagnostic projectors,
- ownership-code breakers.

Their most important "treasures" may be **parts and memories**, not conventional wealth.

---

## Gene Consortium / medical-science factions

Visual language:

- bioanalyzers,
- advanced medpacs,
- Kolto,
- medical droids,
- specimen scanners,
- diagnostic holograms,
- specialized injectors/stimulants.

Avoid letting this become a player biotech progression ladder.

---

## Ancient / Old Republic technology

Visual language:

- KotOR gadgets,
- unusual shield or belt devices,
- ancient datapads,
- personality recordings,
- uncommon medical consumables,
- obsolete-but-powerful diagnostic systems.

Prefer:

- salvage-only,
- ruin-only,
- quest-only,
- very rare trade,

over unrestricted fabrication.

---

# 12. A Useful Four-Class Gadget Taxonomy

Claude Code should consider classifying candidate devices into four families.

## A. Jawa scavenger gear

Examples:

- hydrospanner
- fusioncutter
- repair kit
- pry tool
- medpac
- slicer spike
- portable scanner
- utility harness
- portable droid charger

These should be tactile and frequently visible.

---

## B. Ship technology

Examples:

- holotable
- navigation display
- diagnostic projector
- ship comm station
- droid charger
- GNK power droid
- survey console
- blast doors
- status lighting
- maintenance stations

These make the Kolyska itself feel Star Wars.

---

## C. Faction signature gadgets

Examples:

- Imperial tactical scanner
- Hutt restraint/control device
- bounty tracker
- moisture-farmer survival pack
- droid restoration tool
- Gene Consortium bioanalyzer

These are useful primarily because they help factions look technologically distinct.

---

## D. Ancient / exotic technology

Examples:

- Old Republic belt gadget
- rare personal shield device
- unusual data artifact
- personality holorecord
- ancient medical device

These should generally remain finite and exciting.

---

# 13. Acquisition Model — Important Campaign Guidance

For every gadget Claude considers, explicitly choose one or more acquisition lanes:

### Commonly craftable
Use only for mundane tools whose production does not undermine scarcity.

Examples:
- basic repair kit,
- simple medpac,
- common cable/coupler.

### Factory-restoration gated
The Kolyska can manufacture it only after a corresponding original subsystem is restored.

### Salvage-only
Recovered from:
- ruins,
- wrecks,
- enemies,
- crashed ships,
- abandoned machinery.

### Trade-only
Useful for faction differentiation and Jawa trading behavior.

### Quest-only
Use for genuinely special technology.

### Unique / relic
One-off object or named machine.

### Restore-only
The crew can repair an existing item but **cannot fabricate a fresh one**.

This lane is especially powerful for droids and ancient ship technology.

---

# 14. What Claude Code Should Inspect Before Any Adoption

For each promising mod, source-audit the actual 1.6 files and record:

1. **Workshop ID**
2. **packageId**
3. **supportedVersions**
4. **dependencies**
5. **DLC dependencies**
6. **all relevant ThingDefs**
7. **graphics paths**
8. **recipes**
9. **research requirements**
10. **workbench requirements**
11. **utility/apparel slots**
12. **Comp classes / custom C#**
13. **trade tags**
14. **loot / reward generation**
15. **pawn spawn integration**
16. **faction integration**
17. **whether manufacturing can be disabled cleanly**
18. **whether individual defs can be Cherry-Picked safely**
19. **compatibility with the current Jawa/Outer Rim/KotOR stack**
20. **license / asset reuse constraints before copying any art or code**

Do **not** infer that a Workshop description accurately captures current source behavior.

---

# 15. Current Verification / Confidence Notes

These statuses were checked through current Steam-indexed pages on 2026-08-11, but should still be confirmed in the actual local mod install.

| Mod | Current research status |
|---|---|
| Outer Rim - Droid Depot | **Strong current candidate. 1.6 update explicitly visible in changelog.** |
| KotOR Weapons and Armor | **Strong current source. Official 1.6 KotOR collection says gadgets are included.** |
| KotOR Resources and Materials | **Strong current source.** |
| Outer Rim Furniture & Decor | **Strong current source.** |
| EGI Holograms and Projectors | **Strong current source.** |
| Holograms and Projectors lite | **Available as predecessor/fallback.** |
| Survival Tools Reborn | **Current Workshop page marked Mod, 1.6.** |
| Dubs Rimkit | **Localized Workshop page shows 1.6 + 2025 update, but Steam indexing is inconsistent; verify directly.** |
| More Utility Packs (Continued) | **Indexed description exists but Steam may flag removed/incompatible. Treat as donor until verified.** |
| Doors Expanded: Star Wars Edition (continued) | **Current 1.6 continuation explicitly advertised.** |
| Better Ground-Penetrating Scanner | **Mechanic is well documented; current Workshop visibility/status should be rechecked before dependency use.** |
| Recon and Discovery (Continued) | **Current index flags removed/incompatible. Donor only.** |
| What the Hack?! | **Use current continuation if inspecting; broad system, donor first.** |
| NanoTech | **Current lead; inspect before use.** |
| Repair Workbench / Repairable Gear / MendAndRecycle | **Mechanic donors; current compatibility still needs local verification.** |
| Star Wars Lights | **Historical page currently flagged removed/incompatible. Concept/art reference only.** |
| Bluelibra Personal Music Player | **Current lightweight flavor lead.** |
| RimTek DigiPal | **Current personal-computer gadget lead discovered during follow-up.** |

---

# 16. Steam Source Index

Primary Steam pages referenced in this dossier:

1. **Outer Rim - Droid Depot**  
   https://steamcommunity.com/sharedfiles/filedetails/?id=3096501398

2. **Outer Rim - Droid Depot changelog**  
   https://steamcommunity.com/sharedfiles/filedetails/changelog/3096501398

3. **Star Wars KotOR Weapons and Armor**  
   https://steamcommunity.com/sharedfiles/filedetails/?id=2938932438

4. **Official 1.6 Star Wars Knights of the Outer Rim collection**  
   https://steamcommunity.com/sharedfiles/filedetails/?id=3254515866

5. **Star Wars KotOR Resources and Materials**  
   https://steamcommunity.com/sharedfiles/filedetails/?id=3254370945

6. **Star Wars KotOR Droids**  
   https://steamcommunity.com/sharedfiles/filedetails/?id=3047371944

7. **Outer Rim - Furniture & Decor**  
   https://steamcommunity.com/sharedfiles/filedetails/?id=2919553599

8. **EGI: Holograms and Projectors**  
   https://steamcommunity.com/sharedfiles/filedetails/?id=2979598490

9. **EGI Holograms and Projectors MINIFIED**  
   https://steamcommunity.com/sharedfiles/filedetails/?id=3304159909

10. **Holograms And Projectors (lite/predecessor)**  
    https://steamcommunity.com/sharedfiles/filedetails/?id=2847321165

11. **More Utility Packs (Continued)**  
    https://steamcommunity.com/sharedfiles/filedetails/?id=3249560356

12. **Dubs Rimkit**  
    https://steamcommunity.com/sharedfiles/filedetails/?id=832333531

13. **Survival Tools Reborn**  
    https://steamcommunity.com/sharedfiles/filedetails/?id=3554664966

14. **Survival Tools Reborn testing branch**  
    https://steamcommunity.com/sharedfiles/filedetails/?id=3663736701

15. **Doors Expanded: Star Wars Edition (continued)**  
    https://steamcommunity.com/sharedfiles/filedetails/?id=3550435517

16. **Bluelibra's Personal Music Player**  
    https://steamcommunity.com/sharedfiles/filedetails/?id=3537776760

17. **RimTek DigiPal**  
    https://steamcommunity.com/sharedfiles/filedetails/?id=3500443258

18. **Better ground-penetrating scanner**  
    https://steamcommunity.com/sharedfiles/filedetails/?id=2809972387

19. **Repair Workbench**  
    https://steamcommunity.com/sharedfiles/filedetails/?id=733997423

20. **Repairable Gear**  
    https://steamcommunity.com/sharedfiles/filedetails/?id=2482478785

21. **MendAndRecycle**  
    https://steamcommunity.com/sharedfiles/filedetails/?id=735241897

22. **What the Hack?! (Continued)**  
    https://steamcommunity.com/sharedfiles/filedetails/?id=3372841828

23. **What the Hack?! original**  
    https://steamcommunity.com/sharedfiles/filedetails/?id=1505914869

24. **Recon And Discovery (Continued)**  
    https://steamcommunity.com/sharedfiles/filedetails/?id=2035131107

25. **NanoTech**  
    https://steamcommunity.com/sharedfiles/filedetails/?id=3719999155

26. **Star Wars Lights**  
    https://steamcommunity.com/sharedfiles/filedetails/?id=2265746202

---

# 17. Final Direction

The most promising overall design is **not** to add a universal "Star Wars technology mod."

Instead, build the setting from **many small pieces of differentiated technological culture**:

- Jawas carry battered repair and slicing tools.
- Imperial squads carry standardized scanners and comlinks.
- Droids require chargers, restoration kits and replacement parts.
- Hutt compounds contain restraints, luxurious holograms and black-market electronics.
- Homesteaders use rugged survival and maintenance equipment.
- Ancient ruins contain Old Republic gadgets no living faction normally manufactures.
- The Kolyska is visually full of diagnostic projections, GNK power units, couplers, droid bays, blast doors, warning lights and sacred broken machinery.

This is preferable to another technology tree because it makes Star Wars **visible in ordinary life** while preserving the campaign's central progression: repairing, awakening and learning to use the inherited Factory gravship.

Again:

> ## **FOR CONSIDERATION, NOT DIRECT IMPLEMENTATION**
>
> These mods and mechanics are **resources to inspect and think with**. They are not assignments. Source-audit them, compare overlaps, retain only what strengthens the campaign, and prefer finite salvage/restoration over adding a new unrestricted advancement economy.
