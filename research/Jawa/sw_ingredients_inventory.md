> **LIVE-DATA OVERRIDE:** `observed/2026-08-13_pre-restructure/live_mod_inventory.md` (generated 2026-08-09 from the machine) is authoritative for mod identity — existence, Workshop IDs, packageIds, versions. This file keeps the reasoning only. "Faction Filter" never existed; the live equivalents are **Sensible Factions** (3531306011) and **Faction Control** (2882785581).

# Star Wars Faction-Mod Ingredient Inventory — INSPIRATION ONLY

> ## ⚠️⚠️ NOT 1.6 — DO NOT LOAD THESE SIX MODS ⚠️⚠️
> **Every mod in the "Outer Rim faction series" section below ships `1.4` + `1.5` folders ONLY — no `/1.6` folder, no `LoadFolders.xml` remap, About.xml `supportedVersions` = 1.4/1.5.** [SRC-AUDITED 2026-08-06, all six extracted in `mod_sources/`.]
> They are kept in `mod_sources/` as a **parts bin / design donor** — a catalogue of how the Outer Rim series structures factions, unit ladders, weapons, and mechanics — **NOT** as installable content. Anything we want from here must be **re-authored** for 1.6. **XML-vs-assembly triage COMPLETE (2026-08-06) — see the ⭐ TRIAGE section below: the port is cheap (content is ~99% pure XML; the real mechanics we want already ship in 1.6 Core + Droid Depot).** Treat this whole file as a mood board, not a shopping list.

**Last updated:** 2026-08-06

---

## The six INSPIRATION-ONLY faction mods (1.4/1.5, extracted in `mod_sources/`)

| Mod dir | FactionDefs shipped | Pawnkinds | ThingDefs |
|---|---|---|---|
| `Outer-Rim-Galactic-Empire-main` | Galactic Empire, Imperial Outpost | 24 | 112 |
| `Outer-Rim-Galactic-Republic-main` | Galactic Republic, Republic Outpost | 122 | 160 |
| `Outer-Rim-Mandalore-main` | Death Watch, Death Watch (Honour), Neo-Crusaders, Mandalorian Outpost | 40 | 126 |
| `Outer-Rim-Old-Republic-main` | Old Republic, Republic Outpost, Sith Empire, Sith Outpost | 42 | 46 |
| `Outer-Rim-Rebel-Alliance-main` | Rebel Alliance, Rebel Outpost | 26 | 43 |
| `Outer-Rim-Seperatists-main` | Confederacy of Independent Systems, Separatist Outpost | 26 | 17 |

Structural pattern worth stealing: each ships a **main aggressive faction + a settleable "Outpost" variant** — the series' standard way to make a militarized faction both raid you and hold territory.

---

## Ingredient catalogue (mine, don't adopt)

**Unit ladders (best inspiration — maps to our Act I→III escalation):**
- *Empire:* cadet → trooper → scout/snow/desert/range/jump/incinerator/artillery → stormtrooper → death trooper → ISB agent → officer→commander (+KX security, DT sentry droids). Grey-conscript-to-elite-specialist ladder.
- *Mandalore:* light/medium/heavy/melee weight-classes + field marshal + rally master — armor-tier grammar, not role-tier.
- *Separatists:* battle → super battle → commando → tactical → super tactical → destroyer (droideka) → crab droid — pure mechanical-swarm escalation.
- *Old Republic:* mirrored Republic-vs-Sith trooper ladders.

**Weapons library (labels verified):** Empire blasters (E-11/11D/10/22, DLT-19/19X/20A, EC-17, SE-14R, TL-50, D-72W flame); Mandalore (Amban sniper, WESTAR-18/34/35, EE-3, EE-13, Galaar-15, IB-94; beskad, mando hammer/warhammer/hookblade, munitkad halberd; jetpacks); Separatist (E-5, E-5s, RG4D, BX vibroblade).

**Apparel:** per-tier trooper armor sets; Mandalore's **16 clan decal apparel items** (Vizsla, Mudhorn, Nite Owls, Mythosaur, Jaig Eyes…) = ready-made heraldry system.

**Buildings / heavy weapons:** light/medium/heavy laser cannons (Corellia/Coruscant/Tatooine skins), ion cannons, Anaxes turret, P-Tower, proton artillery, turbolaser, proton-torpedo turret, shield generators, Hypertech terminals.

**Mechanics (from HediffDefs — the gold):**
- **Carbonite freezing / "frozen in carbonite"** — stasis hediff + building. See dedicated design below.
- **Restraint bolt** — droid-control hediff; synergizes with the Jawa "recycle Empire droids into DroidBrains" verb.
- **Training hediffs** (stormtrooper / death-trooper / ISB / clone training) — express "elite" as an *acquired buff*, not stat inflation → fits anti-exponential pillar.
- **Stealth field**, **ion buildup** (anti-droid damage axis), **blaster burn** (damage flavor).

---

## ⭐ CARBONITE TROPHY — greenlit; FULL DESIGN PARKED → `carbonite_trophy_mod.md`

**Premise CORRECTED (SRC-audited 2026-08-06):** the donor carbonite is NOT what we hoped. Outer Rim **Core**'s carbonite (`Hediff_Carbonite.cs` + `Ability_CryobanProjector.xml` + `Damage_CryoBan`) is a **cryoban WEAPON** — a freeze projectile that applies a **timed** hediff (`HediffComp_Disappears`) so the pawn is stunned in `Stance_Frozen` and **thaws on a timer**. It is combat crowd-control, *not* a permanent sellable/displayable slab. **No tradeable carbonite-slab ThingDef and no permanent-freeze building exist anywhere on disk** [grep-confirmed]. So the "Han Solo on the wall" fantasy is entirely unbuilt.

**User verdict 2026-08-06:** donor version is "so much lamer than the carbonite I thought we might have" → **build our own, much cooler.** Full parked design (permanent slab: haulable/minifiable, wall-mountable trophy w/ beauty+impressiveness scaled to occupant, costed freeze recipe consuming pawn+steel/plasteel+coolant+components+power, reversible thaw-for-ransom loop, rarity grades, malfunction + extraction-raid + brownout-thaw danger hooks, Hutt-market synergy, 7-question PASS) is in **`carbonite_trophy_mod.md`**. Feasibility: small-to-medium 1.6 C# mod (pawn-container comp + 2 recipes/jobdrivers, rest XML); Droid Depot's `JobDriver_RestrainDroid`/`Recipe_RemoveBolt` are a portable template shape.

---

## ⭐ XML-vs-ASSEMBLY TRIAGE — COMPLETE (SRC-audited 2026-08-06)

**Headline: the port is FAR cheaper than "assembly-backed" implied. The content we want is ~99% pure XML, and the few real C# mechanics we actually want (carbonite, restraint bolt, training curves) live in modules that ALREADY ship 1.6 — Outer Rim Core and Droid Depot.** The six faction mods are 1.4/1.5-only, but their assemblies are almost entirely dead weight.

### What the six faction-mod assemblies actually contain
- **3 of the 6 ship NO code at all** — Old Republic, Rebel Alliance, Separatists are **pure XML** (no `.dll`, no `.cs`). Their content = FactionDefs, PawnKindDefs, ThingDefs, apparel, weapons, buildings → **re-authoring for 1.6 is a mechanical folder-copy + `supportedVersions`/LoadFolders bump + defName collision check.** Trivial.
- **3 ship an assembly (Empire, Republic, Mandalore) — but it's mostly settings plumbing.** Across all three, the ONLY content-bearing C# classes are:
  - **Mandalore `IncidentWorker_HonourRaid`** (135 lines) — the "Honour Raid" allied-Mando incident. The one genuinely custom behavior; a clean, self-contained port if we want that verb.
  - **Republic `Gene_CloneBiochip`** (28 lines) — forces clone pawns male + sets age on generation. Tiny; only needed if we adopt the clone-army gimmick. Skippable.
  - **Republic 2 Harmony patches** (romance/relations tweaks for clones) — cosmetic; skip.
  - Everything else = `Mod`/`ModSettings`/`PatchOperation_SettingActive`/`LogUtil`/colour-picker UI = **toggle plumbing we don't need** (we're curating fixed loadouts, not shipping a settings menu).

### The real mechanics we want are NOT stranded in 1.4/1.5 — they're in 1.6 modules
- **Carbonite** → Outer Rim **Core** (`1.6/Source`, Core is **1.6-supported**). But see above: it's only the *timed cryoban weapon*, which we're **replacing with our own** design anyway.
- **Restraint bolt** (droid-control, synergizes with Jawa "recycle Empire droids" verb) → **Droid Depot**, which is **1.6-supported** and ships `JobDriver_RestrainDroid` + `Recipe_RemoveBolt` in `1.6/Source`. **Available now, no port needed.**
- **Training-as-acquired-buff** hediffs (Stormtrooper/DeathTrooper/ISB — "elite = earned XP, not stat inflation," a pillar-perfect mechanic) → the *hediff XML* is in the 1.4/1.5 Empire mod, but its `hediffClass` is **`OuterRimCore.Hediff_Training`** + `DefModExt_TrainingCurve`, both of which live in **Core 1.6**. So porting the training ladder = **copy the HediffDef XML into a 1.6 mod; the class it needs already exists in Core.** Cheap.

### Cross-mod class dependency scan (what the faction XML actually references)
Custom classes referenced by the six mods' defs resolve almost entirely to **already-1.6 frameworks**: `OuterRimCore.*` (Core, 1.6), `KCSG.*` (Vanilla Expanded Framework/Custom Structure Gen, 1.6), `Asimov.*` (Droid Depot dep, 1.6), `VanillaGenesExpanded.GeneExtension` (VGE, 1.6). **The only non-1.6 framework reference is Mandalore's `Vehicles.*` + `SmashTools.*`** (Vehicle Framework) — used for Mando flyer/launch defs. So Mandalore's *vehicle* content is the one piece with a heavier dependency; its faction/weapon/heraldry XML does not need vehicles.

### VERDICT per module (for 1.6 re-authoring effort)
| Module | Code? | Port effort | Verdict |
|---|---|---|---|
| Old Republic | none | trivial (XML copy) | **EASY** — pure XML; Sith-Order pawnkinds = donor for Empire Sith-elite ranks |
| Rebel Alliance | none | trivial | **EASY** (low priority — off-theme for our roster) |
| Separatists | none | trivial | **EASY** — droid-swarm ladder = clean donor for our droid factions |
| Galactic Empire | plumbing only | easy (drop the settings .cs; copy defs; training hediff needs Core) | **EASY** — the big prize (trooper ladder, blaster library, training buffs) |
| Galactic Republic | plumbing + tiny CloneBiochip | easy (skip clone gimmick, or port 28-line class) | **EASY-MODERATE** |
| Mandalore | plumbing + HonourRaid (135 lines) + Vehicle deps | moderate (port HonourRaid if wanted; skip/replace vehicle defs) | **MODERATE** — heraldry/weapons easy; vehicles + Honour Raid are the only real work |

### Bottom line / recommended next step
Nothing here is blocked by "needs a C# port." The plan is: **cherry-pick XML defs** (trooper/droid ladders, blaster & Mando weapon libraries, 16-clan heraldry, laser-cannon turret line, training hediffs) **into a single custom 1.6 sub-mod**, pointing `hediffClass`/`DefModExt` references at **Core 1.6** (already installed) and Droid Depot 1.6 (already installed). The only bespoke C# we'd *choose* to write is (a) our **custom Carbonite Trophy** (parked, `carbonite_trophy_mod.md`) and optionally (b) a port of **Honour Raid** if we want that incident. Everything else is copy-audit-load. **Tradeoff:** doing it as our own curated sub-mod (vs. loading the dead 1.4/1.5 mods) also lets us apply the anti-exponential balance pass and Faction-Filter restriction in the same step — cleaner than patching someone else's live mod.

---

## Gamorrean answer (the Hutts' pig-soldiers)

**Pig-soldiers of the Hutts = Gamorreans** (green Gamorrean Guards, Jabba's palace).
**Do we have them? Not as a race/xenotype.** [SRC-AUDITED 2026-08-06:] no `Gamorrean` XenotypeDef or PawnKindDef exists anywhere on disk. Only *references*: a KotOR-Weapons `HC_gamorrean_melee` equipper tag + a "gamorrean axe" weapon skin; SW Animal Collection has a **Pufferpig** (not a Gamorrean). **Already-decided stand-in (cherry_picker_killlist.md §2):** reflavor the vanilla **Pigskin** xenotype → **Gamorrean** (pig-like, tough, ugly — near 1:1). So the Hutt pig-guards are covered by a reflavor, not a dedicated race.
