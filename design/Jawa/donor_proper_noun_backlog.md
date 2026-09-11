# Donor stack off-lore proper nouns — bounded rename backlog

Deliverable of `DONOR_PROPER_NOUN_SCAN_1` (2026-09-11). Source spec:
`text_lore_load_report.md` §4 — *"the RENAME backlog is bounded by off-lore
proper nouns, not by volume — the worst leaks are named (orc clans, trolls,
MiningCo., unthemed xenotypes)."*

**Instrument**: `defs.sqlite` at
`/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/defs.sqlite`,
`modlist_fingerprint 6fdca6f582164e2a`, captured 2026-09-10T08:36:27Z, 577
mods, 80,037 defs — the SAME dump the load-report's §4 numbers came from.
Queried the `json` column (full per-def serialized fields, not just
`label`/`defName`) with a Python word-boundary regex per term, not a bare
grep, to avoid the "42,019 LIKE-rows but only 12 real hits" substring-match
trap (e.g. `orc` also matches `Force`, `Divorced`; `troll` also matches
`Controller`, `Controlled`). Cull status checked with
`src/RimMandrake/Utils/cherrypicker.py` (`cuts.cut_name(defName)`) against the
live Cherry Picker settings file — **every entry below returned `False`
(not cut)**, so none of this is pending removal.

Full FactionDef census (83 across the whole 577-mod stack) and full
XenotypeDef census (136) were read in their entirety — small enough to
eyeball completely rather than sample — to make sure the "worst leaks" list
below is not missing a sibling.

## How to use this

Each entry names the defName(s), the mod/packageId, the field, and the exact
player-visible text. None of these were patched in this pass — see
"Why left in the backlog" below. Whoever picks this up:

1. Decide the retheme (new faction/xenotype name + description, fitting the
   Ash'karr desert Star Wars register) — **this is a design call, not a
   mechanical swap**: a faction rename touches `label`, `fixedName`,
   `description`, `leaderTitle`, sometimes `pawnSingular`/`pawnsPlural`, and
   ties to the xenotype/gene names it spawns.
2. Write a `PatchOperationReplace` (or `PatchOperationReplace` per field) in
   a new patch file under the tier that owns cross-mod compat patches
   (`src/RimUtinni/.../Patches/` per the naming-scheme doc — check
   `NAMING_SCHEME_PLAN.md` for whether a donor-retheme patch is RUT-tier
   compat content or something else).
3. Validate: `python3 skills/rimworld-modding/scripts/validate_patch.py <patch> --defs <dump-derived source>`.

## Why left in the backlog, not fixed now

Every hit below is a **faction or xenotype identity**, not a single stray
word in flavor text. Renaming "Orc Clan" or "Kingdom of Muspelheim" is a
naming-grammar/design decision (what does this faction become in an
Ash'karr-desert Star Wars frame — reskinned as a scavenger clan? a rival
Hutt-adjacent syndicate? dropped from the settled roster entirely?), not a
mechanical one-word swap — which is exactly the class of fix this item's
brief said to defer rather than guess at. No trivial, unambiguous,
single-word flavor-text swap turned up in this scan; if one had, it would
have been fixed directly per the item's own instruction.

---

## Category 1: Orc Clan + Xenotype (karew.orcclan) — full fantasy race+faction

| defName | Type | Field | Text |
|---|---|---|---|
| `KAR_OrcClan` | FactionDef | label | `orc clan` |
| `KAR_OrcClan` | FactionDef | description | "An orcish clan of reclaimers and raiders. While sometimes welcoming of outsiders, they tend to be distrustful of other groups..." |
| `KAR_OrcClan` | FactionDef | leaderTitle | `cnarlord` |
| `KAR_Orc` | XenotypeDef | label | `Orc` |
| `KAR_Tusks`, `KAR_OrcishEars`, `KAR_Orc_Metamorphosis`, `KAR_Orc_Retromorphosis` | GeneDef | label/description | orc-flavored gene text ("stout, pointed orc ears", etc.) |
| `CultureDef Orcish` | CultureDef | — | mod-level culture pack |
| `RulePackDef KAR_LeaderTitleMaker_Orcish` | RulePackDef | — | orc naming grammar |

Faction table (§4) rates faction read-probability ~100% once a world
generates with the mod's faction active — this is not buried content.

## Category 2: Dark Ages: Beasts and Monsters (van.beasts) — troll faction + creature line

| defName | Type | Field | Text |
|---|---|---|---|
| `DA_Troll` | FactionDef | fixedName / description | `Trolls` / "Trolls" |
| `DA_TrollOutbreak` | GameConditionDef | descriptionFuture | "a troll outbreak has been detected in the region..." — **a letter the player reads** |
| `DA_TrollBurrow_Incident` | IncidentDef | letterText/letterLabel | "Trolls have dug their way out from underground..." |
| `DA_TrollBurrow`, `DA_FreshTrollBurrow`, `DA_BeardedTroll`, `DA_RockTroll`, `DA_HibernatingRockTroll`, `DA_TrollRug`, `DA_TrollMeat`, `DA_Sangonite`, `DA_Leather_RockTroll`, `DA_Leather_Troll` | ThingDef/PawnKindDef | label/description | troll-burrow flavor text, "rock troll", "bearded troll" etc. |

This is the incident-letter case explicitly called out by the load report as
the worst kind of leak (a raid-adjacent letter the player is guaranteed to
read if the incident fires).

## Category 3: Big and Small — Races (redmattis.bigsmall) — Norse-mythology race pack

Largest single leak by defcount. One coherent Norse fantasy setting bolted
onto the donor stack: dwarves, gnomes, ogres, giants, trolls, dark elves.
**Recommend a pack-level decision** (retheme the whole pack under one lore
frame, or nominate it for a Cherry Picker cull) rather than 20 one-off
patches — flagging that choice here rather than making it.

Factions (all `~100%` read-probability per §4 if active):

| defName | label | fixedName/notes |
|---|---|---|
| `BS_Dvergr_Medieval_Union` | Dvergr Trade Union | "Most Dvergr don't even like the companies of their own families..." |
| `BS_JotunPlayerColony` | Jotun Settlement | player-selectable start faction |
| `BS_Muspelheim` | Kingdom of Muspelheim | fixedName `Muspelheim`; "fire giants of Muspelheim" |
| `BS_Niflheim` | Tribes of Niflheim | fixedName `Niflheim`; "Frost Jotun tribes" |
| `BS_OgreFaction` | ogre tribe | fixedName `Ogre Tribes`; leaderTitle `chef` |
| `BS_LittlePeople` | A little people union | — |

XenotypeDefs (chargen/pawn-tooltip visible): `BS_Dwarf` (label "Dvergr"),
`BS_Gnome` (label "Nisse"), `BS_Ogre`, `BS_GreatOgre`, `BS_Jotun`,
`BS_FireJotun`, `BS_FrostJotun`, `BS_Half_Jotun`, `BS_Svartalf`,
`BS_Redcap`, `BS_Surtr` (label "Heir of Surtr"), `BS_Ymir` (label "Heir of
Aurgelmir"), `BS_Hearthguard`, `BS_Hearthdoll`, `BS_PilotableFleshGolem`,
`BS_FleshGolemServant`, `BS_BrokenTitan`, `BS_Corrupterd_Titan`, plus the
troll trio (`BS_Troll`/`BS_TrollAdult`/`BS_TrollOld`) and their ~20
supporting GeneDefs (ears/hair/nose/horns/beard cosmetic genes — cosmetic
only, lowest priority within this already-low-priority mod).

## Category 4: MiningCo. mod family (mlie.miningcospaceship / miningcodrillturret / miningcomms / miningcoalertspeaker) — sci-fi corporate brand

| defName | Type | Field | Text |
|---|---|---|---|
| `MiningCo` | FactionDef | label/fixedName | `MiningCo.` |
| `MiningCo` | FactionDef | description | "MiningCo. is the most famous deep-space mining company through the galaxy..." |
| `MiningCo` | FactionDef | leaderTitle | `planetary commander` |
| `MiningCo` | ResearchTabDef | label | `MiningCo.` |
| `ResearchMobileMineralSonar` | ResearchProjectDef | description | "Study the famous MiningCo. MiSoTech*..." |
| `OrbitalRelay`, `Spaceship`, `SpaceshipCargo` | ThingDef | description | "...MiningCo. ships..." / "used by MiningCo. to..." |

A named corporate brand is the single easiest category to swap for an
in-universe equivalent (a Trade Federation/Guild-flavored analog already
exists in RSW canon) once someone signs off on which one.

## Category 5: Horrors (Continued) (mlie.horrors) — unthemed horror faction

| defName | Type | Field | Text |
|---|---|---|---|
| `Horrors` | FactionDef | label/description | "Horrors" / "Dangerous skulking Horrors, persistant in their attacks on the colonies." |
| `Horrors` | FactionDef | leaderTitle | `Mastermind` |
| `HorrorWastes` | BiomeDef | description | "A frozen region, contorted by alien fauna and flora... A terrible place." — biome unlikely to matter on a desert-only world (`the_one_map.md` — no worldgen, frozen world) but the FactionDef is still live if the mod ships it as a raidable faction. |

## Category 6: Mo'Events (Continued) (mlie.moevents) — "Abomination" faction

| defName | Type | Field | Text |
|---|---|---|---|
| `MO_AbominationFaction` | FactionDef | label/fixedName | `Abomination` / `abomination` |
| `MO_AbominationFaction` | FactionDef | description | "Abominations are slow, hulking, relentless manifestations of flesh..." |
| `MO_AbominationPawnKind`, `MO_AbominationRace`, `Corpse_MO_AbominationRace` | PawnKindDef/ThingDef | label | `Abomination` / `Abomination corpse` |

## Category 7: Vanilla Races Expanded — Archon (vanillaracesexpanded.archon)

| defName | Type | Field | Text |
|---|---|---|---|
| `VRE_Archons` | FactionDef | label/fixedName | `archons` / `Archons` |
| `VRE_Archon` | XenotypeDef | label | `archon` |
| supporting Backstory/Gene/Ability defs | — | — | dimensional/void-magic lore register ("born from the void's energies", "Archotech Project") — a different sci-fantasy register than SW, not a proper-noun clash per se but a tonal one. |

**Lower priority than categories 1–6** — no single hard proper-noun clash
(no real-world or fantasy IP name), just an off-register lore voice. Flagged
for completeness; a call on whether it's worth a pass at all is deferred to
whoever picks this up.

## Checked and ruled OUT (false positives / not worth a line item)

- **Vanilla Races Expanded — Saurid** (`VRESaurids_*`, "rough saurid union",
  "cold-blooded lizard-like people") — generic alien-race flavor, no
  proper-noun clash; "saurid" reads as a plausible in-universe xenotype
  name. Not carried forward.
- **`abomination`** as a bare word — 16 word-boundary hits, only the
  Mo'Events faction (Category 6) is a proper noun; the rest (Vanilla
  Genetics Expanded creature flavor text, an Ideology precept line, Alpha
  Animals thought label) use it as an ordinary descriptive word, which is
  in-register for RimWorld generally and not a lore clash.
- **`horrors`** as a bare word — 102 word-boundary hits, only the `Horrors`
  faction/biome (Category 5) is a proper noun; the rest are Core-game
  backstory prose ("knew the horrors of war") and a Vanilla Ideology
  Expanded rules-string ("comic horror") — ordinary usage, not a leak.
- **`archon`** — 154 word-boundary hits; only Category 7 above is a real
  faction/xenotype identity. The rest (AbilityDef/BackstoryDef/GeneDef rows
  belonging to the same mod) are that mod's own internal vocabulary, not
  separate leaks.
- **`HoraxCult`** (Anomaly, `ludeon.rimworld.anomaly`) — this is vanilla
  RimWorld canon (the Anomaly DLC's own cult), not donor content. Out of
  scope by definition.
- **`GiantAnt_Faction` ("giant ant colony")**, **`AA_BlackHive` ("black
  hive")**, **`DV_PirateKeshig` ("keshig horde")**, **`DV_OutlanderRoughBuzzer`**
  — literal/descriptive names with no fantasy-IP or corporate-brand clash;
  read as generic sci-fi/RimWorld flavor. Not carried forward.
- **SW-flavored donor factions** (Outer Rim's Galactic Empire / Rebel
  Alliance / moisture farmers / binary star raiders, VFE Pirates' Junkers,
  VFE Tribals' Wild Men) — surface-checked per the item's own "SW donors
  last" ordering; all read as near-lore already, matching §4's own call.
  No further SW-donor sweep was done in this pass (budget spent on
  categories 1–7 first, per the item's explicit priority order).
- **Full FactionDef (83) and XenotypeDef (136) census** — both read in full
  above; nothing else in either list carries a fantasy/corporate/off-theme
  proper noun beyond what's listed in categories 1–7.

## Not scanned this pass (named, not a gap)

- Item/weapon/apparel/building label-and-description text (§4: 3,591 / 340
  / 470 / 6,884 donor defs) — the report's own read-probability column
  (30–50%) and its own ruling ("most donor thought/hediff/recipe text is
  universe-neutral and needs nothing") put this below the faction/xenotype
  layer for a first bounded pass. A future pass could grep this layer with
  the same word-boundary method against the same term list plus whatever
  new terms turn up once categories 1–7 are ruled on.
- Quest/incident letter text beyond the two troll-burrow letters already
  found in Category 2 — `DONOR_PROPER_NOUN_SCAN_1`'s scope was proper
  nouns, not a full quest-text audit; a quest/incident sweep for OTHER
  off-lore letters (not proper-noun-keyed) would need its own instrumented
  pass with a different search strategy (can't grep for a term you don't
  know yet).
