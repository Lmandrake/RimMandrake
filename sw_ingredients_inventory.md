# Star Wars Faction-Mod Ingredient Inventory — INSPIRATION ONLY

> ## ⚠️⚠️ NOT 1.6 — DO NOT LOAD THESE SIX MODS ⚠️⚠️
> **Every mod in the "Outer Rim faction series" section below ships `1.4` + `1.5` folders ONLY — no `/1.6` folder, no `LoadFolders.xml` remap, About.xml `supportedVersions` = 1.4/1.5.** [SRC-AUDITED 2026-08-06, all six extracted in `mod_sources/`.]
> They are kept in `mod_sources/` as a **parts bin / design donor** — a catalogue of how the Outer Rim series structures factions, unit ladders, weapons, and mechanics — **NOT** as installable content. Anything we want from here must be **re-authored** for 1.6 (and triaged XML-vs-assembly first). Treat this whole file as a mood board, not a shopping list.

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

## ⭐ CARBONITE TROPHY — greenlit as a costed sink (user loved this, 2026-08-06)

**Concept:** freeze a (downed/captured) pawn into a **carbonite slab** — a high-value tradeable trophy. Diegetically perfect Star Wars; mechanically a captive-disposal + wealth-conversion sink. Sell to the Hutts (and it stacks with the Hutt "tradeable-regardless-of-standing" market verb).

**HARD RULE (user, 2026-08-06): it is NOT free.** Freezing must consume real inputs so it's a deliberate economic choice, never a free win-button. Recipe cost (design target — tune at authoring):
- the **pawn** (downed/prisoner — consumed/immobilized),
- **components** (industrial; advanced components for higher-value targets),
- **power** (a running carbonite-chamber building draws heavy wattage during the freeze),
- **plus other resources** — e.g. steel/plasteel for the slab casing, chemfuel or a cryo/coolant reagent for the freezing medium. [design placeholder — pick the exact reagents at authoring.]

**Value logic (anti-exponential guard):** trophy sale value should roughly track the *inputs + the pawn's own market value*, NOT mint free wealth. It's a **conversion** (prisoner + materials + power → sellable good), not generation. Higher-tier captives (named Empire officers, Force-users) = rarer, costlier freeze, higher payout — keeps it a special-occasion play, not a grind.

**Pillar check (7-question):** raises no *player combat* ceiling (it's an economy building), gated behind components+power+research, and is a sink for prisoners we'd otherwise release/execute. Passes as a costed conversion. ✅

**Status:** GREENLIT concept — to be **authored fresh for 1.6** (the donor carbonite defs are in the 1.4/1.5 Empire/Old-Republic mods above, INSPIRATION ONLY). Open: confirm whether the donor carbonite implementation is pure-XML (portable) or assembly-backed (must reimplement) — part of the pending XML-vs-assembly triage.

---

## Gamorrean answer (the Hutts' pig-soldiers)

**Pig-soldiers of the Hutts = Gamorreans** (green Gamorrean Guards, Jabba's palace).
**Do we have them? Not as a race/xenotype.** [SRC-AUDITED 2026-08-06:] no `Gamorrean` XenotypeDef or PawnKindDef exists anywhere on disk. Only *references*: a KotOR-Weapons `HC_gamorrean_melee` equipper tag + a "gamorrean axe" weapon skin; SW Animal Collection has a **Pufferpig** (not a Gamorrean). **Already-decided stand-in (cherry_picker_killlist.md §2):** reflavor the vanilla **Pigskin** xenotype → **Gamorrean** (pig-like, tough, ugly — near 1:1). So the Hutt pig-guards are covered by a reflavor, not a dedicated race.
