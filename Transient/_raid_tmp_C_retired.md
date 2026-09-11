# Retired-donor Star Wars proper-noun raid — 2026-09-11

Disk-raid research only. No code/game changes made.

## Method

1. Extracted `<li>packageId</li>` from the current live
   `/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml`
   (595 packageIds) and from the union of five early/mid snapshots in
   `/mnt/d/Luke/dev/Rimworld/infrastructure/state/modlists/`:
   `ModsConfig.FULL.20260819_201527.xml`, `ModsConfig.FULL.20260820_004136.xml`,
   `ModsConfig.FULL.20260826_070210.xml`, `ModsConfig.FULL.20260829_pre_pawnflavor.xml`,
   `ModsConfig.FULL.20260830_pre_rename.xml` (590 packageIds, lower-cased union).
2. `comm -23` diff (old-union minus current, case-insensitive) → **76 retired
   packageIds** (mods that were once active and are gone from the live list
   today). Full list kept in the session scratchpad, not repeated here in
   full — most are non-SW (our own renamed `mandrake.*` mods from the
   naming-scheme migration, QoL mods, unrelated creature packs).
3. Filtered the 76 for Star-Wars-themed names (star/wars/sw/jawa/mandal/
   sith/jedi/droid/blaster/saber/wookiee/hutt/rebel/empire/republic/clone/
   trooper/outerrim/kotor, or known SW vocabulary) → **12 candidates**
   examined in depth below. `mandrake.*`/`mandrake.jawa*`/`mandrake.starwarsraces`/
   `mandrake.empirepursuit` etc. were EXCLUDED — those are our own mods
   renamed under `NAMING_SCHEME_EXECUTION_1`, not third-party donors.
4. For each candidate, grepped
   `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/*/About/About.xml`
   for an exact `<packageId>` self-declaration to find the owning Workshop
   folder, then read its `Defs/` for `<label>` text (and `defName`/`fixedName`
   for factions/xenotypes).
5. Cross-checked against `design/Jawa/sw_ownership_survey.md`,
   `design/Jawa/droid_ruling.md`, and the `DROID_RETIRE_*`/`WEAPONS_DONOR_RETIREMENT_1`/
   `KOTORWEAPONS_ABSORPTION_DANGLING_REFS_1` items in
   `infrastructure/state/items/` for names not visible in a single grep pass
   (e.g. faction defNames quoted in prose).

## Retired SW-themed packageIds — disposition

| packageId | Mod name | Workshop folder | Content on disk? |
|---|---|---|---|
| `guy762.KotORDroids` | Star Wars KotOR Droids | `3047371944` | YES |
| `guy762.KotORWeapons` | Star Wars KotOR Weapons and Armor | `2938932438` | YES |
| `Lumi.doorsexpanded` | Doors Expanded Star Wars edition | `3550435517` | YES (thin — 2 named doors only) |
| `lumi.swlights` | Star Wars Lights | `2265746202` | YES (thin — 2 generic-named lights) |
| `M3.Continued.JangoDsoul.StarWars.TSDA` | [JDS] StarWars - The Separatist Droid Army | `3276499495` | YES |
| `M3.Continued.JangoDsoul.StarWars.BTI` | [JDS] StarWars - Armory | `3511954303` | YES |
| `Neronix17.OuterRim.DroidDepot` | Outer Rim - Droid Depot | `3096501398` | YES |
| `Sov.Sith` | Rimwars:Pureblood Xenotype | `3485069256` | YES |
| `StarWars.ThemedSounds` | Star Wars Themed Sounds | `3249480517` | YES (audio patches only, zero proper nouns) |
| `Neronix17.Asimov` | Asimov | `3096481956` | YES (droid-support infra, no SW-specific proper nouns of its own) |
| `Killathon.ArtificialBeings` | ABF: Synstructs Core | `3288463094` | YES (generic "Synstruct" framework vocabulary, zero SW proper nouns) |
| `killathon.artificialbeings.syncore` | "SynCore" (per `DROID_RETIRE_ABF_SYNCORE_1.md`) | — | **NO — no folder self-declares this exact packageId.** Recovered name only from `infrastructure/state/items/DROID_RETIRE_ABF_SYNCORE_1.md`, which itself flags a mismatch: that item's own investigation found `3288463094`'s About.xml self-declares packageId `Killathon.ArtificialBeings` (no `.syncore` suffix) even though the repo's dependency chain treats it as the separate "SynCore" mod — an unresolved donor-header inconsistency, not something this pass could fix. |

**10 of 12 still have content on disk**, cached by Steam workshop even though
removed from the active list; only `killathon.artificialbeings.syncore` is
name-only.

Also checked and **ruled OUT** as not SW-themed (retired, but generic):
`matathias.ruthlessmechanoids` (Ruthless Faction Pursuit — generic mechanoid
pursuit tuning), `titans.fl` (Titans — generic hostile creature), `mf.jfklanding`
(Just F*king Landing — gameplay QoL), `joe.cephaloids` (Cephaloids — octopus
alien race, no SW theme). No proper-noun extraction done for these.

`guy762.KotORFactions` (workshop `3379096669`, "Star Wars KotOR Factions") has
content on disk and is clearly related, but **does not appear in any of the
five snapshots checked nor the current list** — cannot be classified as
"retired" by this method (it may never have been active within the sampled
window). Not included in the counts below; flagged for a follow-up sweep of
the full ~90-snapshot set if it matters later.

---

## Category: Creature / species

### Droid chassis (this repo's closest functional equivalent of "species" for droids)

**`guy762.KotORDroids`** (3047371944):
3C-series utility droid · IT-series utility droid · R-8009 series utility
droid · GE3-series labor droid · GE3-series protocol droid · KM1-B Excavation
Droid · KM1-series Mining Droid · K-X12 assassin/utility probe droid ·
Municipal Patrol Droid Mark I · Assault Droid Mark I / Mark IV / Mark IV Type
B · Devastator-class (Type II assassin droid / war droid) · Sentinel-class
war droid · Star Forge Assault Droid · HK-50 series protocol droid · HK-51
series assassin droid · T3-series utility droid · G0-T0 superintelligence
droid.
*Note: all confirmed KOTOR-canon droid model lines; content still fully on disk.*

**`M3...StarWars.TSDA`** (3276499495, Separatist Droid Army):
B1 Battle Droid · B1 Commander Droid · B1 Security Droid · B2 Super Battle
Droid · B2 HA Super Battle Droid · BX Commando Droid · DSD1 Dwarf Spider
Droid · Droideka Droid · Droideka Sharpshooter Droid · IG-100 MagnaGuards ·
LR-57 Combat Droid · ST Super Tactical Droid · T1 Tactical Droid · AQ Battle
Droid · Pistoeka Sotage Droid (mod's own spelling — canon name is
"Pistoeka Saboteur Droid").
*Note: these are canon prequel-trilogy/Clone Wars droid lines.*

**`Neronix17.OuterRim.DroidDepot`** (3096501398):
B1A Battle Droid · Destroyer Droid · DUM Repair Droid · GNK Power Droid ·
HK-Series Assassin Droid · Imperial Labor Droid · KX Security Droid ·
MagnaGuard Droid · MSE Repair Droid · Muckraker Crab Droid · R-Series Droid ·
Super Tactical Droid · T-Series Tactical Droid · FX-7 medical droid ·
Astromech Droid.
*Note: this mod's `restraint bolt`/`attach restraint bolt` items are the
disk-confirmed source of this repo's own "restraining bolt doctrine" naming
(`design/Jawa/worldbuilding/restraining_bolt_doctrine.md`).*

### Non-droid sentient species (recovered as item-name adjectives; source `guy762.KotORWeapons`, 2938932438 — no dedicated XenotypeDef/PawnKindDef for these species existed in this mod, only equipment named after them)

Bothan · Baragwin · Echani · Gand · Geonosian · Kaleesh · Krath · Nagai ·
Rakatan · Trandoshan · Tusken (Raider) · Verpine · Zabrak · Arkanian ·
Dashade · Ankarres.

### Xenotype

**`Sov.Sith`** (3485069256) — `XenoType.xml` defName `PureBlood`, label
"Pureblood". **Divergence note**: despite the packageId/mod being named
"Sith", the def's own label/description never say "Sith" anywhere — it's a
generic crimson-skinned xenohuman xenotype ("Rimwars:Pureblood Xenotype"),
not an explicit Sith Pureblood def. Any in-repo claim that a "Sith Pureblood"
xenotype def exists would be wrong; only the flavor (crimson skin, facial
bone ridges, psychic sensitivity) matches Sith Pureblood lore.

---

## Category: Character (all recovered as possessive item-name prefixes in `guy762.KotORWeapons`, 2938932438 — no separate NamedCharacterDef; these are KOTOR-canon named individuals)

Bacca (`Bacca's Ceremonial Blade`) · Bastila [Shan] (`Bastila's Tunic`) ·
Bendak [Starkiller] (`Bendak's Blaster`) · Calrissian [Lando]
(`Calrissian's utility belt`) · Cassus Fett (`Cassus Fett's Heavy Pistol`) ·
Darth Malak (`Darth Malak's Armored Cape/Tunic`) · Darth Malgus (`breath
mask` / `masked hood` / `powered battle armor`) · Darth Nihilus (`Cloak` /
`Mask` / `Robes`) · Darth Revan (`Armor` / `Mask` / `cloak`) · Darth Sion
(`Armor`) · Darth Traya (bare label, and `Darth Traya's Robes`) · Exar Kun
(`light battle suit`) · Freedon Nadd (`Blaster`) · HK-47 (`Assassin Rifle`) ·
Jamoh Hogra (`Assault Rifle` / `Carbine`) · Jolee [Bindo] (`Jolee's Tunic`) ·
Juhani (bare label, and `Juhani's Tunic`) · Jurgan Kalta (`Assault Rifle` /
`Carbine`) · Luxa (`Modified Disruptor`) · Mandalore [title/name]
(`Mandalore's Assault Rifle`) · Mira (`Hold Out Repeater`) · Mission [Vao]
(`Mission's Vibroblade`) · Ordo [Canderous] (`Ordo's Repeating Blaster`) ·
Onasi [Carth] (`Onasi Blaster`) · Qel-Droma [Ulic/Cay] (`Qel-Droma belt`) ·
Sanasiki (`Sanasiki's Blade`) · Visas [Marr] (`hood` / `robes`) · Yusanis
(`Yusanis' Brand`) · Zaalbar (`Zaalbar's Bowcaster`).

---

## Category: Faction

| Name | Source mod | Note |
|---|---|---|
| Confederacy of Independent Systems | `M3...StarWars.TSDA` (3276499495) — `defName JDSCIS_CIS_Faction`, `fixedName` confirmed on disk | canon CIS/Separatists |
| rogue droid collective | `guy762.KotORDroids` (3047371944), FactionDef quoted as `guy762_KotORFaction_RogueDroids` in `design/Jawa/droid_ruling.md:568` | the actual FactionDef itself lives in the separate, out-of-scope `guy762.KotORFactions` folder — this mod only supplies its PawnKindDefs |
| Exchange | `guy762.KotORWeapons` (2938932438) — item labels `Exchange Negotiator`, `Exchange Poison Blade`, `Exchange Shadow Caster`, `Exchange utility belt`, `Exchange visor`, `Exchange work gloves` | canon criminal syndicate; no separate FactionDef in this mod, name only survives via item labels |
| Mandalorian(s) | `guy762.KotORWeapons` | large item family (armor/weapon prefix), no dedicated FactionDef in this mod |
| Sith | `guy762.KotORWeapons` | item-label-only (Commando/Trooper/Marauder/Assassin/Officer gear); this mod is separate from `Sov.Sith` |
| Republic | `guy762.KotORWeapons` | item-label-only (`Republic Blaster`, `Republic Commando Powered Armor/Helmet`, `Republic uniform`) |
| Czerka | `guy762.KotORWeapons` | corporation, item-label-only (`Czerka Enforcer Armor/Helmet`, employee/officer/laborer uniforms) |
| GenoHaradan | `guy762.KotORWeapons` | bounty-hunter guild, item-label-only (`GenoHaradan Blaster`, `GenoHaradan Stealth Unit`) |

---

## Category: Planet (recovered as item-name adjectives, `guy762.KotORWeapons`)

Nar Shaddaa (`Nar Shaddaa Grinder`) · Onderon (`Onderon Repeating Carbine`) ·
Taris (`Taris survival gloves`) · Eriadu (`Eriadu Prototype Armor` /
`Stealth Unit`) · Bonadan (`Bonadan Alloy Heavy Suit`) · Cinnagar /
Cinnagaran (`Cinnagar Plate/War/Weave Armor`, `Cinnagaran Battle Rifle` /
`Carbine`) · Barab (`Barab Ore Ingot`) · Balmorra (`Balmorran overshield` /
`prototype overshield`).

---

## Category: Ship

**None found.** No ThingDef/vehicle labels in any of the 12 retired mods
name a specific canon starship (no Millennium Falcon-class analogue, no
named capital ship). The closest is the **Star Forge** (ancient Rakatan
droid-factory space station — `Star Forge Assault Droid`, `Star Forge
Cloak/Mask/Robes`, `Star Forge shield`) which is a mega-structure/artifact
in KOTOR canon, not a ship — filed under Other below.

---

## Category: Item / artifact (named unique items, `guy762.KotORWeapons`, 2938932438)

Heart of the Guardian · Mantle of the Force · Pride of Mandalore · Ultima
Pearl · Krayt Dragon Pearl · Lorrdian Gemstone · "Whistling Birds" (+
launcher) — signature Wookiee bowcaster ammo.

### Lightsaber/blaster crystal names (same mod)

Adegan · Artusian · Bondar · Damind · Dragite · Eralam · Firkann · Hurrikaine
· Jenurax · Kaiburr · Kasha · Luxum · Nextor · Opila · Phond · Pontite ·
Qixoni · Rubat · Ruusan · Sapith · Sigil · Solari · Stygium · Upari ·
Velmorite · Viridian (plus plain-color crystals: Red/Blue/Green/Orange/
Yellow/Silver/Violet/Fuchsia/Turquoise — not proper nouns, excluded).

### Named weapon model codes (`M3...StarWars.BTI`, 3511954303 — canon clone-wars-era blaster designations)

DC-15A · DC-15S · DC-15x · DC-17 · DC-17M · DC-17S · E-5 · E-5C · E-5S ·
E-60R · EE-3 · SE-14 · Westar-33 · Westar-34 · Westar-35 · Westar-44 ·
Westar-M5 · Z6 (Rotary Blaster Cannon) · Amban (Blaster Rifle).

---

## Category: Other

- **Star Forge** — ancient droid-factory mega-structure (see Ship section
  above); appears only as an item-name prefix in `guy762.KotORWeapons`,
  content still on disk.
- **M'uhk'gfa** — a KotOR Weapons item label (2938932438); likely a Wookiee-
  or Shyriiwook-language creature/item name, exact canon referent not
  identified in this pass (flagging rather than guessing).

---

## Summary counts

- Retired packageIds overall (old-snapshot-union minus current live list): **76**
- SW-themed retired packageIds examined: **12** (10 with content still on
  disk, 1 name-only, 1 — `guy762.KotORFactions` — excluded as not provably
  "retired" within the sampled snapshot window)
- Non-SW retired mods checked and ruled out: 4 (`matathias.ruthlessmechanoids`,
  `titans.fl`, `mf.jfklanding`, `joe.cephaloids`)
- Names extracted by category: creature/species ~53 (36 droid chassis + 16
  non-droid species adjectives + 1 xenotype), character 27, faction 8,
  planet 8, ship 0, item/artifact ~32 (7 unique artifacts + 25 named
  crystals/weapon codes), other 2.
