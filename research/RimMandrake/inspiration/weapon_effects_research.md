# RimWorld 1.6 Spectacular Weapon Effects — Research Handoff

**Project:** Kolyska / Jawa Gravship Expedition  
**Purpose:** inspiration inventory for later detailed investigation and implementation by Claude Code.  
**Date:** 2026-08-11

> **Important:** Nothing in this document is an assignment of a weapon technology to a particular faction, nor is inclusion here a decision to install a mod. These are **effect/mechanic/art/audio inspirations** to investigate. The campaign can patch damage, penetration, range, research, recipes, availability, faction tags, graphics, sounds, and progression as needed.
>
> The useful design target is **technological diversity that is legible in combat**: beams should look different from blaster bolts; ion weapons should arc or EMP; plasma should visibly behave unlike lasers; projectile weapons should have smoke/trails/impact character; biological/chemical weapons should have their own visual language. Kolyska's possible ancient beam-weapon lineage is one promising example, not a final faction assignment.

---

## 1. Highest-priority effect donors

### 1.1 Dedicated Turrets
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=3739213606  
**Status observed:** Steam page currently tags it **RimWorld 1.6**. Small mod; no DLC or third-party dependency listed.

**Why promising:** The author explicitly describes custom graphics, projectile visuals, and effects. More importantly, the four turrets have genuinely different firing behaviors rather than merely different DPS.

- **Atomiser** — microwave-style lock-on beam. Its firing rate increases and the beam draws wider the longer it stays locked to the same target.
- **Vaporiser** — sustained laser beam running down an entire firing lane; damages targets caught anywhere along the beam path, including friendlies.
- **Sludger** — cone spray of adhesive sludge; no direct damage, but severe movement/accuracy/melee debuffs.
- **Zapper** — electrical/chain-lightning style defensive concept; inspect code and VFX closely.

**Possible inspiration uses (NOT assignments):**
- Ancient thermal lance / industrial cutter.
- Heavy continuous-beam ship turret.
- Microwave or radiation lock-on weapon.
- Ion/arc cannon.
- Hutt-style restraint/sludge projector.
- Area-denial weapon that visually communicates its firing lane.

**Claude Code investigation:**
1. Inspect how the sustained beam path is rendered and how repeated pulses are scheduled.
2. Inspect how Atomiser tracks lock duration and changes beam width/rate.
3. Inspect Zapper chain-target logic and lightning visuals.
4. Determine whether individual turret classes/effects can be reproduced cleanly without importing the research tree.
5. Determine licensing before reusing source/assets.

---

### 1.2 Laser Cannon
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=3586248892  
**Source linked by author:** https://github.com/JohnCannon87/RimworldLaserCannon  
**Status observed:** Steam page tags **1.6** and requires **Biotech**.

**Distinctive effects/mechanics:**
- One large, high-powered **beam** rather than a normal projectile stream.
- Visible **charging animation before firing**.
- Fires over walls and ordinary roofs (but not thick roofs), simulating an elevated emplacement.
- Draws stored battery power for each shot.
- Can intercept incoming mortar shells and rockets.
- Author explicitly exposes source for reuse/learning.

**Possible inspiration uses:**
- Large Kolyska hull-mounted ancient laser.
- Precursor defense cannon.
- Ship-mounted anti-air/point-defense beam.
- Energy cannon with capacitor/charge-cycle presentation.
- Industrial excavation or asteroid-cutting laser repurposed as a weapon.

**Claude Code investigation:**
- Charging animation implementation.
- Beam rendering and hit handling.
- Projectile interception logic.
- Whether the turret can be enlarged into a visually massive multi-tile ship weapon.
- Separate gameplay power draw from visual charge effects so balance can be reauthored.

---

### 1.3 Vanilla Weapons Expanded — Laser
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=1989352844

**Distinctive effects/mechanics:**
- Introduces a dedicated **laser beam** projectile rather than simply recoloring bullets.
- Beam can ignite targets.
- Family includes handheld laser weapons and salvaged variants.
- The concept of malfunction-prone / inferior **salvaged lasers** is particularly useful for a scavenger setting.
- Current Workshop comments should be checked because at least one 2025 user reports the warm-up behavior not working correctly under 1.6.

**Possible inspiration uses:**
- Ancient coherent-beam handheld weapon lineage.
- Repaired/salvaged beam rifles with instability or overheating.
- Rare precursor emitters that eventually become reproducible once a factory line is restored.
- Visual contrast against ordinary Star-Wars-style bolt blasters.

**Related appearance/audio mod: VWE Laser Reskin**
https://steamcommunity.com/sharedfiles/filedetails/?id=3382711469

The reskin explicitly aims for a heavier, somewhat Star-Wars-inspired appearance and also patches sounds. Treat it as **art/audio inspiration**, not automatically as the preferred texture set.

**Claude Code investigation:**
- Beam projectile class.
- Salvaged weapon differences.
- Heat/warm-up implementation and 1.6 behavior.
- Sound defs and opportunities for a dedicated ancient-technology sound palette.

---

### 1.4 Volt Weaponry
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=3551721422

**Distinctive effects/mechanics:**
- Adds **seven beam-based weapons**.
- Small, focused content pack.
- Workshop description says no framework/core mod is required.
- Useful as a clean source to study multiple beam weapon implementations without a huge faction framework.

**Important compatibility clue:** Workshop discussion reports an asset-name conflict with Vanilla Spacer Weapons – Beam Gun (Continued), specifically a shared `BeamLance` texture name. That makes namespace hygiene worth examining if borrowing code/assets.

**Possible inspiration uses:**
- Multiple classes of coherent energy weapon.
- Industrial or non-standard beam weapons.
- Short, long, sniper, heavy, or specialist beam emitters within one technological lineage.

**Claude Code investigation:**
- Compare its beam classes with VWE Laser and Biotech's native beam implementation.
- Identify which effects are XML-only versus C#.
- Check namespaces/texture names before combining with other beam mods.

---

### 1.5 Dubs Rimatomics
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=1127530465  
**Status observed:** Steam page currently includes a **1.6** tag.

**Distinctive technology/effects explicitly listed by the author:**
- Microwave area-denial systems.
- Tesla coils.
- High-energy lasers.
- Railguns.
- Anti-mortar systems.
- Nuclear weapons.
- Large power infrastructure and a custom research system.

**Why promising:** This is one of the richest sources of **large-emplacement spectacle** and nonstandard weapon mechanics.

**Critical campaign caveat:** The native Rimatomics research/reactor progression is itself a major technological progression tree. For this project, the attractive target is **individual weapon mechanics, visuals, or source patterns**, not necessarily adopting its progression wholesale.

**Possible inspiration uses:**
- Enormous ship defense emplacements.
- High-energy beam cannon.
- Tesla/ion defense.
- Electromagnetic mass driver.
- Strategic defense / interceptor turret.
- Rare doomsday-scale relic weapon.

**Claude Code investigation:**
- Identify individual weapon classes and dependencies on Rimatomics' power/research systems.
- Determine whether selected effects can be isolated or reimplemented.
- Review Odyssey/gravship interactions; current Workshop comments include some Odyssey-specific reports, so test rather than assume full compatibility.

---

## 2. Beam and particle weapon families

### 2.1 Vanilla Spacer Weapons — Beam Gun (Continued)
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=3251505960

**Status/caveat:** Search results show 1.5/1.6 tagging, but Steam currently displays the page as removed/incompatible in some locales. Treat this as a **legacy/source/inspiration lead**, not a safe install recommendation until verified locally.

**Distinctive concept:**
- Sustained beam weapons that remain visually connected to the target.
- The original family emphasizes beam behavior rather than discrete blaster bolts.

**Possible inspiration uses:**
- Persistent cutting beam.
- Damage that ramps while contact is maintained.
- Mining/industrial beam repurposed for combat.
- Beam glaive or unusual alien emitter concepts.

---

### 2.2 Rimlaser
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=1465459039

**Distinctive concept explicitly stated by its page:**
- Weapons fire **proper laser beams**.
- Includes pistol, rifle, heavy, sniper, minigun, incendiary laser, and Tesla gun families.
- Uses special crystals as a production ingredient.

**Possible inspiration uses:**
- Full coherent-laser technology family.
- Incendiary beam variants.
- Laser minigun / rapid scanning beam.
- Crystal-dependent emitter technology.
- Tesla gun as an ion/arc effect donor.

**Claude Code note:** Verify current 1.6 functionality before treating as installable; it is valuable even if only as an old implementation/art reference.

---

### 2.3 Vanilla XCOM Laser Weapons
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=2848053220

**Distinctive effects:**
- Custom gunshot sounds.
- Laser beams.
- Rifle, sniper, scatter laser, heavy laser, pistol, and railgun concepts.

**Caveat:** Steam search currently shows the item as removed/incompatible in at least one locale. Treat as an **effect/art/audio reference** unless a working fork is found.

**Possible inspiration uses:**
- Modern/reverse-engineered beam tech visually distinct from truly ancient emitters.
- Scatter laser.
- Heavy infantry laser.
- Dedicated sound language for coherent energy weapons.

---

### 2.4 Vanilla XCOM Plasma Weapons
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=2834362415

**Distinctive effects explicitly advertised:**
- Custom gunshot sounds.
- Custom aiming sounds.
- “Lots of beams.”
- Plasma Rifle, Plasma Lance, Storm Gun, Beam Cannon, Beam Pistol, Beam Autopistol, Shadow Lance, Uranium Phase-Cannon, etc.

**Possible inspiration uses:**
- Plasma/particle family deliberately distinguished from coherent lasers.
- Thick energetic streaks, lances, burst plasma, heavy cannons.
- A faction-specific sound palette where even **aiming** sounds technologically distinct.

---

### 2.5 Phasers
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=2812697392

**Distinctive concept:**
- Beam weapon modeled as an accelerated stream of particles.
- Standard version is described as a highly painful/incapacitating weapon suitable for urban/shipboard use with reduced collateral damage.
- Also includes more lethal variants and turrets.

**Possible inspiration uses:**
- Stunner / pain-beam technology.
- Security weapons meant to incapacitate rather than kill.
- Shipboard internal-defense beams where hull penetration is undesirable.
- Particle stream visually distinct from a hot laser.

**Claude Code note:** Verify 1.6 status before installation; the mechanic is useful even if reproduced elsewhere.

---

### 2.6 Grandyy's Laser Turrets
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=2883943346

**Distinctive concept:**
- Three compact laser turrets using laser effect code based on Biotech.
- Tracker, shooter, and longer-range/heavier roles.

**Caveat:** Some Steam locale results currently display the item as incompatible, even while current 1.6 collections include it. Verify locally.

**Possible inspiration uses:**
- Small point-defense beam turrets.
- A family of differently tuned ship laser emplacements using a shared visual language.
- Reference for leveraging Biotech beam effects on buildings.

---

## 3. Electrical / ion / EMP inspirations

### 3.1 Weapons of Elysion (Continued)
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=2793869556

**Standout effect: Voltaic Hand-Cannon**
- Functions as a true **lightning shotgun**.
- Fires separate shotgun pellets represented by individual lightning strikes rather than one generic blast.
- Burns targets.
- Also acts as a weaker EMP weapon.

**Possible inspiration uses:**
- Arc scattergun.
- Ion scattergun.
- Droid-disabling boarding weapon.
- Strange salvaged electrical weapon.
- Weapon whose visual spread communicates its shotgun pattern.

---

### 3.2 Ion Weaponry (Continued)
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=3532877485

**Why promising:**
- Dedicated ion-weapon concept.
- Continued mod is active enough to appear in current 1.6 mod collections.
- User reports specifically call out usefulness against mechanoids.

**Possible inspiration uses:**
- Dedicated ion rifles/carbines.
- Low-organic-damage / high-machine-disruption weapon family.
- EMP splash or disruptive particle effects.
- Faction technology where machinery is disabled rather than destroyed.

**Claude Code investigation:** Inspect the actual projectile defs, EMP behavior, graphics, and dependencies rather than relying on secondary descriptions.

---

### 3.3 VFE — Security
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=1845154007  
**Status observed:** Current page explicitly tags **1.6**.

**Spacer defenses explicitly listed:**
- Charge turrets.
- Charge complexes.
- Railguns.
- **Tesla blasters.**
- Shock mines.

**Possible inspiration uses:**
- Tesla/ion emplacements.
- Charge-bolt heavy weapons.
- Mass-driver/rail emplacement.
- Distinctive mine and defensive technologies.
- Medium-scale faction defense between ordinary turrets and giant ship guns.

**Claude Code investigation:** Determine whether Tesla and railgun VFX are sufficiently distinctive in play or mainly mechanical; screenshots/source should settle this.

---

## 4. Plasma, exotic projectile, and high-impact weapons

### 4.1 Bill Doors' Plasma Weapons — 1.6 Temporary
**Current 1.6 temporary fork:** https://steamcommunity.com/sharedfiles/filedetails/?id=3643309973  
**Original:** https://steamcommunity.com/sharedfiles/filedetails/?id=2937054043

**Distinctive effects/mechanics described on the original/fork pages:**
- Dedicated plasma weapon family.
- Unique automated ammunition mechanism.
- Plasma projectiles **gradually fade** and stop causing damage beyond weapon range.
- Largest plasma turret has a narrow fan-shaped explosion behavior when hit.

**Possible inspiration uses:**
- Visibly decaying plasma bolts.
- Heavy plasma turrets.
- Weapons where range is communicated by projectile dissipation rather than an invisible cutoff.
- Alien ammunition/energy-cell economy.

**Claude Code investigation:** Use the current 1.6 temporary fork for implementation testing, but inspect original design/source provenance carefully.

---

### 4.2 Cybernetic Warfare and Special Weapons (Continued)
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=2155485488  
**Original:** https://steamcommunity.com/sharedfiles/filedetails/?id=1811369911

**Why promising:** Broad special-weapons mod with many nonstandard weapon concepts and cyberware integration. Secondary current summaries describe a strong focus on high-impact special combat systems and unusual weapon modes.

**Effect families worth inspecting in source/assets:**
- Plasma.
- Laser.
- Electro.
- Flamethrower / animated flame concepts.
- Heavy explosive and crowd-control systems.
- Specialized firing modes.

**Caveat:** Steam currently displays the Continued page as removed/incompatible in some results. Treat primarily as a **source/idea donor** unless a working current fork is confirmed.

**Possible inspiration uses:**
- Individual bounty-hunter exotic weapons.
- One-off experimental faction guns.
- Flame projector.
- Coil/accelerator specialist weapons.
- Crowd-control technology.

---

## 5. Biological and chemical weapon inspirations

### 5.1 Antediluvian's Biological Warfare
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=3610522205

**Distinctive mechanic:**
- Weaponized diseases spread from detonation/exposure.
- Infected pawns can become secondary transmission sources.
- PPE/vaccine counterplay.
- Some effects cannot simply be cured after exposure.

**Possible inspiration uses:**
- Bio-agent grenades.
- Spore weapons.
- Contagious area-denial munitions.
- Experimental biological faction technology.
- Hazmat-equipment-dependent combat encounters.

**Campaign caution:** This can have enormous systemic consequences beyond a normal gunfight. If borrowed, preserve the *visual/qualitative threat* while deliberately tuning contagion duration and persistence.

---

### 5.2 Biological Warfare
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=3221550806

**Concept:** Dedicated biological offensive/defensive arsenal with vanilla-style graphics and original lore.

**Caveat:** Steam currently marks the item removed/incompatible. Keep as a **concept/art/source research lead**, not an installation candidate.

---

### 5.3 Dedicated Turrets — Sludger
See: https://steamcommunity.com/sharedfiles/filedetails/?id=3739213606

Worth repeating as a chemical-effect donor because the Sludger:
- Fires a **48-degree cone** rather than a bullet.
- Leaves custom sludge filth.
- Applies a dedicated debuff.
- Sacrifices damage entirely for movement/combat disruption.

Possible reinterpretations include adhesive foam, capture goo, industrial sealant, riot-control polymer, corrosive sludge, or restraint technology.

---

## 6. Global VFX/audio enhancement layers

These are especially interesting because they can make **custom patched weapons** feel different without requiring every effect to be built from scratch.

### 6.1 Muzzle Flash
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=2917732219  
**Source/patching reference mentioned by author:** http://github.com/IssacZhuang/Rimworld-Mod-Muzzle_Flash

**Effects:**
- Flame effects at gun muzzles.
- Lightning effects on charged weapons.
- Built-in patches for mod weapons.
- XML-driven patching support.
- Debug hot-reload command for effect-patch authoring.

**Why especially valuable for Claude Code:** This is not just eye candy; it provides a **patchable interface for giving different weapon families different firing signatures**.

**Possible uses:**
- Imperial blasters: sharp muzzle flash.
- Coil/slug weapons: violent conventional flash.
- Charge/plasma weapons: electrical corona.
- Custom faction guns: unique firing signatures.

**Known Odyssey note:** Author currently lists muzzle flash not displaying in vacuum as a known issue — arguably physically appropriate, but relevant for gravship combat.

---

### 6.2 Extra Explosion Effects
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=3066208882

**Effects described in Workshop/collection text:**
- Extra visual treatment for high explosives.
- Shockwaves.
- Bright flashes.
- Sparks.
- Rising black smoke.
- Crater/ash-style aftermath.
- Intended as eye candy rather than a gameplay rebalance.

**Caveat:** Steam currently marks the original Workshop item removed/incompatible in some views, although it continues appearing in 1.6 collections. Treat as a **source/visual target** unless local testing confirms a usable build.

**Possible uses:**
- Thermal detonators.
- Heavy artillery.
- Missile impacts.
- Geonosian or Imperial explosive cannons.
- Ship-scale weapons whose impact should visibly dwarf handheld guns.

---

### 6.3 Gunplay
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=2034896549

**Global effects:**
- Long projectile trails, wider for more damaging weapons.
- Projectiles originate from the gun barrel rather than pawn center.
- Weapon movement animation on misses.
- Particle collision visuals.
- Faster-looking projectile travel.
- Some custom sounds/animations for vanilla weapons.

**Why promising:** It can turn kinetic/coil weapons into a visually distinct technology family without changing their mechanics.

**Major caution:** Current Workshop comments include reports of projectile trails persisting and causing severe performance degradation, especially with some gauss/coil weapons. Do **not** assume it is safe globally.

**Possible Claude Code approach:** Study or reproduce selected projectile-origin/trail/impact ideas instead of installing the entire global patch.

---

### 6.4 Better Projectile Origin
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=2843040075

**Effect:** Scans weapon textures and moves projectile spawn to the weapon muzzle rather than pawn center.

**Possible use:** Lightweight visual polish if Gunplay is too invasive. Especially valuable for long or unusually shaped alien weapons where center-spawn looks obviously wrong.

---

### 6.5 VWE Laser Reskin
**Workshop:** https://steamcommunity.com/sharedfiles/filedetails/?id=3382711469

**Effect focus:**
- Retextures the entire VWE Laser family.
- Author explicitly says the goal was a heavier, somewhat Star-Wars-inspired look.
- Includes sound changes.

**Use:** Art/audio reference for making ancient or faction-specific energy weapons visually belong in the Star Wars-inspired setting while retaining non-blaster beam behavior.

---

## 7. Secondary promising leads

These are worth opening during the deeper Claude Code pass, but are lower priority than the sections above.

### Laser Weapons: Re-Examined
https://steamcommunity.com/sharedfiles/filedetails/?id=3451325196

Current Steam tags include 1.5/1.6. Worth inspecting for beam/turret rebalance ideas and any additional visual handling.

### Grandyy's Laser Turrets
https://steamcommunity.com/sharedfiles/filedetails/?id=2883943346

Compact beam turret family; potentially useful as small point-defense references.

### Laser Turret (Continued)
https://steamcommunity.com/sharedfiles/filedetails/?id=2828255998

Simple endgame laser turret. Less mechanically exotic, but may contain reusable turret/beam patterns.

### Laser Technology
https://steamcommunity.com/sharedfiles/filedetails/?id=3173480205

Includes laser-defense progression and a portable mini-laser turret concept. Inspect if a small deployable beam turret becomes useful.

### Rimlaser
https://steamcommunity.com/sharedfiles/filedetails/?id=1465459039

Older but rich family: proper beams, incendiary lasers, Tesla gun, multiple handheld classes.

### Phasers
https://steamcommunity.com/sharedfiles/filedetails/?id=2812697392

Potential inspiration for disabling/pain/shipboard beam technology rather than raw lethality.

---

## 8. Suggested effect taxonomy for the later implementation pass

Claude Code should classify candidate weapons by **what the player perceives**, not merely by damage type.

| Visual/mechanical signature | Candidate donors |
|---|---|
| Instant coherent beam | VWE Laser, Volt, Rimlaser |
| Sustained beam / firing lane | Dedicated Turrets Vaporiser, Spacer Beam Gun |
| Lock-on beam that ramps | Dedicated Turrets Atomiser |
| Huge charged ship beam | Laser Cannon, Rimatomics |
| Lightning / chain arc | Dedicated Turrets Zapper, Weapons of Elysion, VFE Security Tesla |
| EMP / ion pulse | Ion Weaponry, VFE Security, Elysion |
| Plasma bolt / fading energy packet | Bill Doors Plasma, XCOM Plasma |
| Particle/pain stream | Phasers |
| Rail/kinetic streak | Rimatomics railguns, VFE Security railguns, Gunplay effects |
| Adhesive/chemical cone | Dedicated Turrets Sludger |
| Biological cloud / contagious payload | Antediluvian's Biological Warfare |
| Flame stream | Cybernetic Warfare / conventional flame mods |
| Heavy explosion shockwave | Extra Explosion Effects |
| Distinct muzzle corona/flash | Muzzle Flash |
| Distinct projectile trail/impact | Gunplay / Better Projectile Origin |

---

## 9. Design inspiration — deliberately NOT faction assignments

The following are **technology archetypes to keep available**, not decisions about who owns them:

1. **Ancient coherent-beam lineage** — immaculate or damaged continuous lasers; possible Kolyska inspiration.
2. **Mass-produced blaster lineage** — familiar discrete Star-Wars-like bolts.
3. **Ion/arc lineage** — lightning, EMP, machine-disruption weapons.
4. **Plasma lineage** — luminous packets/lances with different flight and impact behavior.
5. **Accelerator/rail lineage** — kinetic streaks, penetration, large muzzle effects.
6. **Chemical/restraint lineage** — sludge, adhesive foam, stun and capture tools.
7. **Biological lineage** — disease/spore/toxin weapons with PPE counterplay.
8. **Industrial repurposed weapon lineage** — mining/cutting/microwave tools turned into weapons.
9. **Unique hunter/mercenary lineage** — one-off exotic weapons rather than a standardized family.
10. **Ship-scale defense lineage** — charged beams, interception weapons, massive thermal or kinetic cannon.

The later faction-equipment design should select among these based on culture, industrial capacity, battlefield doctrine, racial physiology, access to trade, and narrative history. A faction should not receive a technology merely because it is statistically convenient.

---

## 10. Claude Code research checklist

For every candidate above:

1. **Fetch the current Workshop package/source** and confirm RimWorld 1.6 compatibility from `About.xml`, not just the Workshop tag.
2. Record `packageId`, dependencies, DLC requirements, assembly names, and license.
3. Enumerate weapon/turret `ThingDef` / `Verb` / `ProjectileDef` / `DamageDef` names.
4. Identify which distinctive behavior is:
   - XML only,
   - vanilla class reuse,
   - Harmony patch,
   - custom C# class,
   - AssetBundle/VFX,
   - custom sound.
5. Capture screenshots/GIF/video of every promising effect in action.
6. Determine whether the effect can be:
   - used by installing the mod,
   - Cherry Picked,
   - XML-patched,
   - subclassed,
   - cleanly reimplemented locally.
7. Ignore native damage/balance if necessary; this project's mechanics can be reauthored.
8. Check whether weapon visuals can be recolored/retextured without losing the effect.
9. Check muzzle-origin alignment and interaction with Muzzle Flash.
10. Check Odyssey/gravship behavior, especially:
    - firing from gravship hulls,
    - vacuum,
    - roof handling,
    - projectile interception,
    - map transition,
    - save/load.
11. Check interactions among multiple beam mods for class/asset namespace conflicts.
12. Only after the effect library is understood should technologies be proposed for specific factions.

---

## 11. Shortlist for first source-code teardown

If time is limited, investigate in this order:

1. **Dedicated Turrets** — unusually diverse behaviors in one tiny current 1.6 package.
2. **Laser Cannon** — ideal charged large-emplacement reference with public GitHub source.
3. **Volt Weaponry** — compact current beam-weapon family.
4. **VWE Laser** — mature handheld beam family + salvaged technology concept.
5. **Muzzle Flash** — reusable faction-signature VFX layer.
6. **Dubs Rimatomics** — source of large high-energy/rail/Tesla ideas; isolate rather than adopt progression blindly.
7. **Weapons of Elysion** — unusual lightning-shotgun implementation.
8. **Bill Doors' Plasma Weapons 1.6 Temporary** — fading plasma/projectile behavior.
9. **Ion Weaponry (Continued)** — dedicated ion/EMP family.
10. **Antediluvian's Biological Warfare** — qualitatively different weapon threat.
11. **Gunplay** — inspect selectively for projectile-origin/trail effects; test performance before adoption.
12. **Legacy beam/XCOM/Cybernetic packs** — mine for ideas/assets/code only after current mods are understood.

---

## Source note

All links above are direct Steam Workshop or author-linked source references located/rechecked during the 2026-08-11 research pass. Workshop availability can change. Items explicitly marked removed/incompatible should be treated as **historical research leads**, not current install recommendations. The authoritative compatibility determination for this campaign should come from the downloaded 1.6 package and its `About.xml` during the Claude Code pass.
