# WORLDGEN_FACTION_CHECKLIST.md — the Configure Factions page, box by box

> # ✅ RATIFIED — VISION, 2026-08-13. EXECUTE THE LIST.
>
> **21 untick / 6 keep is RATIFIED as written.** Nothing in the tick-list changes.
> Four rulings ride with it; read them, they take ten seconds each.
>
> ## R1. Dangling references: OPS is RIGHT, and blanket "accepted cost" is REFUSED
>
> **The line is not "faction gone = cost accepted". The line is what the player is
> asked to DO about it:**
>
> - **Scenery orphans are ACCEPTED.** Troll burrows, hornet hives, insect content,
>   an achievement naming a dead hive. The player meets hostiles with no parent
>   faction and never notices. Record them; do not chase them.
> - **A quest or incident the player can ACCEPT and cannot FINISH is REFUSED.**
>   That is a broken promise, it gets remembered, and it gets blamed on us. An
>   absent faction is never missed; a dead-end quest always is.
>
> ⭐ **Applied to THIS list, that changes nothing** — the one quest-critical
> faction, `guy762_KotORFaction_RogueDroids` (antagonist of the KotOR droid
> distress call), is **already on the KEEP list**. Yautja and Caravan Adventures
> are *scenario* references that only bite if you pick that scenario, plus
> incident thinning — not dead-end quests. **OPS: the objection was right, it is
> now doctrine, and it does not block this run. Stop raising it.**
>
> ## R2. `OuterRim_RebelAlliance` — STAYS SUPPRESSED
>
> **The Rebellion is not this campaign.** Jawa scavengers, an Empire that hunts
> them, and Hutts who sell them out. A Rebel Alliance on the map steals the
> antagonist's oxygen and offers the player a side in a war this story is not
> about. **ABSENT from the page is the desired outcome.** Do not revert the patch
> at the screen. Retire it from the KEEP list.
>
> ⚠️ It is a `permanentEnemyFactions` entry for `Force_Sith_Order` in *The Force
> Factions* — downloaded, not active, inert today. **It stops being inert the day
> we enable that mod for the Jedi/Sith build.** Mine to handle then, not now.
>
> ## R3. ⭐ ADD TO KEEP: vanilla `Empire` — it is now the FALLEN DOMINION
>
> **Owner's ruling, minutes ago, and it changes the antagonist design:**
>
> > *"The Fallen Dominion should be a local aristocracy force-welded into the
> > Empire, fallen into disgrace with the state of the planet's rebelliousness
> > (even though they did win the local war), so they are very eager to please and
> > help track down 'yet more chaotic nonsense' — such as Jawa flying around in an
> > ancient hulk enabled by imprinting their minds into a persona core.
> > Disgraceful!"*
>
> **So the two-empire split is not a defect. It is the design.** The Directorate
> is the Galactic arm; the Dominion is the disgraced local aristocracy trying to
> earn its way back by hunting us. **Confirm vanilla `Empire` is present and its
> count is ≥ 1.** It is not on the untick list, so it survives by default —
> confirm it anyway.
>
> ⚠️ **Its name is GENERATED, so the new world will probably NOT say "Fallen
> Dominion".** That is expected, not a failure. Whatever it generates is the
> working name until we patch `fixedName` with the game down. **Screenshot the
> name.**
>
> ## R4. Do not ship a world with no rough outlanders
>
> `BS_LittlePeople` declares `replacesFaction OutlanderRough`. **After unticking
> it, confirm a rough-outlander row exists at ≥ 1.** If none appears, **leave
> `BS_LittlePeople` at 1** rather than generate a world missing that slot — a
> smallfolk union is a smaller fiction hole than an empty outlander tier.
>
> ## What REMAINS STANDING after the cut — the world is populated
>
> **6 keeps:** binary star raiders · Confederacy of Independent Systems ·
> **Imperial Desert Directorate** · moisture farmers · rogue droid collective ·
> *(Rebel Alliance retired per R2)*.
> **Plus, untouched by this list:** vanilla **`Empire` = the Fallen Dominion**,
> outlander unions, rough outlanders, tribes and pirates. **Nobody is unticking
> vanilla's spine.** The world has a Galactic arm, a disgraced local aristocracy,
> farmers to trade with, droids and separatists to fight, raiders, and the
> ordinary outlander/tribal economy underneath. **That is a world with people in
> it.**
>
> 🔴 **Screenshot the page before leaving it.** It is the only record.

> ✅ **OPS note — RESOLVED, nothing here blocks execution.**
>
> **The tick-list is measured:** 21 untick / 6 keep / 0 not found, every defName
> read off disk, labels taken from the defs because the page shows labels, not
> defNames.
>
> My one open objection — that blanket "accepted cost" for dangling references
> would let a dead-end quest through — **was ruled on in R1 above and is now
> doctrine.** It does not apply to this run: the only quest-critical faction,
> `guy762_KotORFaction_RogueDroids`, is already a KEEP. **Closed; I am not
> raising it again.**
>
> ⚠️ One limit of the four-field suppression template, worth knowing before it is
> reused: **it only reaches factions whose defs expose those four fields.** For
> the rest the lever is the mod list, with the game down — a separate job.

**What you are doing and why.** The next world is generated from scratch (all saves
were deleted by owner order 2026-08-13), and faction existence is decided **once, at
world creation**, on vanilla's *Configure Factions* page that Faction Control unlocks
and extends. There is no suppression setting to write to a file afterwards — Faction
Control's `density` is a clumping radius, not a count, and setting it to 0 does
nothing. So this page is the only lever, and it fires once. The goal is a world that
reads as Star Wars: keep the SW factions, drop the Norse/medieval/fantasy ones, the
Predator clans, and the horror/bug factions that have no SW reading. Work down this
list at the screen, tick the boxes, and **record what you actually saw** in the
`observed` column — the page is the ground truth, this file is a prediction.

> 🔴 **This is a PROPOSAL from OPS. VISION ratifies it.** OPS is player zero here,
> not the designer. Nothing below is authority to change the design; it is evidence
> in, decision out. If VISION has not signed off, do not execute the untick list —
> generate with it in hand and ask.

**⭐ The direction this list serves (owner, 2026-08-13): we build our own factions.
Eventually almost all mod factions get turned off; we keep their mods for the
resources — weapons, apparel, pawnkinds, art.** So this checklist is a *step*, not
the destination, and its keep list is transitional rather than final. Two things
follow, and they matter for how you read the rest of the file. First, **"the mod
stays, the faction goes" is the house pattern, not a compromise** — `RebelAlliance_Suppress.xml`
(Section 5) is the worked example of it and should be read as the template for the
others, not as a conflict. Second, **Section 6's "what breaks if you untick it" is
expected cost, already accepted** — orphaned burrows, incidents with no antagonist and
scenarios that hard-name a dead faction are the known price of keeping the content
while dropping the polity. Record them; do not treat them as blockers.

**Every defName below was located on disk. NOT FOUND count: 0.** All 27 factions
named in the proposal exist in the live 573-mod def set
(`observed/2026-08-13_pre-restructure/dumps/defnames.573.2026-08-13.json`, 87
FactionDefs) and every one was read from its source XML for its label and its
`hidden` / `displayInFactionSelection` / `maxConfigurableAtWorldCreation` fields.

**Two corrections to the proposal, found while reading the defs:**
- **`Horrors` is NOT a hidden faction.** It has `settlementGenerationWeight 1`,
  `canMakeRandomly true`, `maxCountAtGameStart 3` and no `hidden` field. It is an
  ordinary row with a count spinner. The proposal's caution listed it as hidden.
- **`Entities` and `HoraxCult` do NOT appear as "Allow the hidden X faction?"
  checkboxes.** Both carry `<displayInFactionSelection>false</displayInFactionSelection>`
  and are absent from the page entirely. Only `Insect` and `Mechanoid` behave the way
  the proposal describes.

---

## SECTION 1 — Ordinary faction rows (a label and a count spinner). Set the count to 0.

These have settlements, appear as normal rows, and are the loudest offenders on the map.

| ✔ | in-game label | defName | mod | observed on page? |
|---|---|---|---|---|
| ☐ | **BadBloods Clan** | `ABYautjaBadBloodClan` | [AB] Xenotype: Yautja (3536839586) | |
| ☐ | **Augmented Clan** | `ABYautjaModderClan` | [AB] Xenotype: Yautja | |
| ☐ | **Berserk Clan** | `ABYautjaBerserkClan` | [AB] Xenotype: Yautja | |
| ☐ | **Jungle Hunter Clan** | `ABYautjaClan` | [AB] Xenotype: Yautja | |
| ☐ | **A little people union** | `BS_LittlePeople` | Big and Small - Races (2894397737) | 🔴 **STOP after unticking — VISION R4.** It declares `replacesFaction OutlanderRough`. **Confirm a rough-outlander row exists at ≥ 1. If none appears, PUT THIS BACK TO 1** — a smallfolk union is a smaller fiction hole than an empty outlander tier. |
| ☐ | **Dvergr Trade Union** | `BS_Dvergr_Medieval_Union` | Big and Small - Races | |
| ☐ | **Kingdom of Muspelheim** | `BS_Muspelheim` | Big and Small - Races | |
| ☐ | **Tribes of Niflheim** | `BS_Niflheim` | Big and Small - Races | |
| ☐ | **ogre tribe** | `BS_OgreFaction` | Big and Small - Races | |
| ☐ | **Horrors** | `Horrors` | Horrors (Continued) (3535224844) | |
| ☐ | **orc clan** | `KAR_OrcClan` | Orc Clan + Xenotype (3232348025) | |
| ☐ | **Sacrileg Hunters** | `CASacrilegHunters` | Caravan Adventures (2558957509) | |

⚠️ **`ABYautjaBadBloodClan` has `requiredCountAtGameStart` 2** (the other three have
1). If the spinner refuses to go below 2, that is why — Faction Control is what
unlocks going below the required count. If it will not budge, record it and move on;
that faction is the one to chase afterwards.

⚠️ **The Yautja clans are the largest non-SW presence measured** — 14 settlements
between the four in the discarded world. If you only have time to get part of this
list right, get these four right.

---

## SECTION 2 — Hidden-faction checkboxes ("Allow the hidden X faction?"). Untick.

Each of these is `hidden: true` with `maxConfigurableAtWorldCreation: 1`, so it renders
as a single on/off box rather than a count. They own no settlements — they are raid and
event sources, invisible on the map until they attack. **They ARE on the page** (this
corrects the proposal's second caution, which said the settlement-less modded factions
could not be reached from here — for these eight, they can).

| ✔ | in-game label | defName | mod | observed on page? |
|---|---|---|---|---|
| ☐ | **black hive** | `AA_BlackHive` | Alpha Animals (1541721856) | |
| ☐ | **giant ant colony** *(shows as "They!")* | `GiantAnt_Faction` | They! (Giant Ants) (3620253282) | |
| ☐ | **insect geneline** *(shows as "Sorne Geneline")* | `Insect` | **Core (vanilla)** | |
| ☐ | **lost** | `BS_ZombieFaction` | Big and Small - Framework (2925432336) | |
| ☐ | **pustule hornets** | `BMT_PustuleHornets` | Biomes! Polluted Lands (3390196656) | |
| ☐ | **roaming monstrosities** | `GR_RoamingMonstrosities` | Vanilla Genetics Expanded (2801160906) | |
| ☐ | **trolls** | `DA_Troll` | Dark Ages: Beasts and Monsters (3472275628) | |
| ☐ | **Abomination** | `MO_AbominationFaction` | Mo'Events (Continued) (2035143365) | |

⚠️ `GiantAnt_Faction` and `MO_AbominationFaction` declare no
`maxConfigurableAtWorldCreation` of their own and inherit the field default, so they
*may* render as a spinner rather than a box. Either way, drive it to 0.

⚠️ **Faction Control's own tooltip warns that removing a hidden faction does not
remove its content.** Unticking `Insect` will not clear insect hives placed by map
generation, ancient-danger rooms, or quest objectives that spawn them. Same shape
applies to the burrow/hive buildings under Section 5. Expect leftovers; they are not
a bug in this checklist.

---

## SECTION 3 — Will NOT appear on the page. Do not hunt for them.

Read from the def: `<displayInFactionSelection>false</displayInFactionSelection>`.
There is no box to untick. **The only lever is mod removal (or, for the vanilla two,
the Anomaly playstyle setting) — that is a separate proposition for VISION/PROJECT
and NOT a worldgen tick.** Listed here so you do not spend ten minutes scrolling for
a row that does not exist.

| in-game label | defName | source | the only lever |
|---|---|---|---|
| **horax cult** *("The Servants of Horax")* | `HoraxCult` | **Anomaly (vanilla DLC)** | Anomaly playstyle / disable Anomaly |
| **entities** *("Dark entities")* | `Entities` | **Anomaly (vanilla DLC)** | Anomaly playstyle / disable Anomaly |
| **archons** | `VRE_Archons` | Vanilla Races Expanded - Archon (3067715093) | remove the mod |

---

## SECTION 4 — KEEP. Confirm each is present and its count is ≥ 1 before you commit.

These are the Star Wars factions the world exists for. **Do not just leave them alone —
look at each one and confirm it is there**, because one of them was silently absent last
time.

| ✔ | in-game label | defName | mod | note |
|---|---|---|---|---|
| ☐ | **binary star raiders** | `OuterRim_BinaryStarRaiders` | Outer Rim - Core (2919227155) | ordinary row, permanent enemy |
| ☐ | **Confederacy of Independent Systems** | `JDSCIS_CIS_Faction` | [JDS] Separatist Droid Army (3276499495) | **hidden checkbox**, not a row |
| ☐ | **Imperial Desert Directorate** | `OuterRim_GalacticEmpire` | Outer Rim - Galactic Empire (2919248699) | 🔴 **label is patched — see below** |
| ☐ | **moisture farmers** | `OuterRim_MoistureFarmers` | Outer Rim - Core | ordinary row |
| ☐ | **rogue droid collective** *("Droid Collective")* | `guy762_KotORFaction_RogueDroids` | Star Wars KotOR Droids (3047371944) | **hidden checkbox**, not a row. 🔴 **quest-critical — antagonist of the KotOR distress call. Never untick.** |
| ☐ | ⭐ **the Fallen Dominion** — *name will be GENERATED, expect a different string* | `Empire` | **vanilla (Royalty)** | 🔴 **ADDED TO KEEP by VISION R3.** Not on any untick list, so it survives by default — **confirm it anyway, count ≥ 1, and SCREENSHOT the generated name.** |
| ☐ | ~~**Rebel Alliance**~~ — **RETIRED from KEEP** | `OuterRim_RebelAlliance` | Outer Rim - Rebel Alliance (2919249903) | 🔴 **ABSENT is the DESIRED outcome (VISION R2). Record absent and move on — do NOT revert the patch at the screen.** |

⭐ **On the Fallen Dominion (VISION R3, owner's ruling).** The two-empire split is
**the design, not a defect**: the Directorate is the Galactic arm, and vanilla
`Empire` is the disgraced local aristocracy — force-welded into the Empire, fallen
from grace despite winning the local war, and now eager to please by hunting "yet
more chaotic nonsense", i.e. us. ⚠️ **Its name is generated, so the world will
probably not say "Fallen Dominion". That is expected, not a failure.** Whatever it
generates is the working name until `fixedName` is patched with the game down.
**Screenshot it — that string is the only record.**

🔴 **Do not look for "Galactic Empire".** `Jawa_Patches/Patches/ImperialDesertDirectorate.xml`
replaces both `label` and `fixedName` on `OuterRim_GalacticEmpire` with **"Imperial
Desert Directorate"**. That is the string on the page. If you see "Galactic Empire"
instead, the Jawa_Patches deploy did not land — stop and check
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Jawa_Patches` before
generating.

---

## SECTION 5 — 🔴 `OuterRim_RebelAlliance`: watch for it BY NAME, and record present/absent

**The proposal says it "was configured but DID NOT GENERATE in the last world" and
that a repeat would be a real defect. It is not a defect. We did it on purpose.**

`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Jawa_Patches\Patches\RebelAlliance_Suppress.xml`
(repo copy: `D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\Patches\RebelAlliance_Suppress.xml`,
authored 2026-08-12 as NEXT_RELOAD item W6) applies four `PatchOperationReplace` ops to
that FactionDef:

| field | stock value | patched to | effect |
|---|---|---|---|
| `requiredCountAtGameStart` | 1 | **0** | no longer forced into existence at worldgen |
| `settlementGenerationWeight` | 0.3 | **0** | never placed a base |
| `canMakeRandomly` | true | **false** | cannot appear later in the run |
| `maxConfigurableAtWorldCreation` | 9999 | **0** | 🔴 **removed from the Configure Factions page** |

**So the expected observation is: no "Rebel Alliance" row and no Rebel Alliance
checkbox anywhere on the page.** That is the patch working, not a failure.

**Record one of these three outcomes and nothing else:**

- ☐ **ABSENT from the page** → patch is live and working as designed, **and this is
  the expected and desired outcome.** It does mean the KEEP list above cannot be
  satisfied for this faction — the proposal wanted Rebel Alliance kept, the deployed
  patch removes it — but per the owner's direction at the top of this file, *"mod
  stays, faction goes"* is the house pattern and Rebel Alliance is simply further
  along it than the rest. Not a contradiction to resolve; a keep-list entry to retire.
  Do not revert the patch at the screen.
- ☐ **PRESENT and settable** → the patch did NOT land (deploy miss, or an Outer Rim
  update renamed a field and the `PatchOperationConditional` no-opped silently). File
  it; this is the real defect shape.
- ☐ **PRESENT but locked at 0** → Faction Control is surfacing it despite
  `maxConfigurableAtWorldCreation 0`. Interesting, harmless, worth a line.

**To opt back in**, the patch's own header says: revert only the
`maxConfigurableAtWorldCreation` op, not the whole file. That is a repo edit with the
game down, not a worldgen action.

---

## SECTION 6 — Cross-references: what breaks if you untick it

Grepped across the workshop tree for each untick-list defName outside its own
`<defName>` line. **Nothing here is a reason not to untick** — a faction that does not
generate is a normal RimWorld state and these references resolve at load, not at
worldgen. What follows is what to expect afterwards so nobody debugs it twice.

**Content that keeps existing after the faction is gone** (map-gen objects and
incidents that name the faction; they will spawn hostiles with no parent faction, or
silently no-op):

- `DA_Troll` — `Buildings_Burrow.xml` sets `<faction>DA_Troll</faction>` on
  `DA_TrollBurrow`, and `GameConditions_Troll.xml` / `IncidentDefs_Troll.xml` drive
  `DA_TrollOutbreak` and `DA_TrollBurrow_Incident` off it. Troll burrows can still be
  placed by map gen.
- `BMT_PustuleHornets` — `BasicMapGenerator.xml` carries
  `<factionDef>BMT_PustuleHornets</factionDef>` and `Buildings_Natural.xml` sets
  `<faction>BMT_PustuleHornets</faction>` on the hive. Same shape.
- `Insect` — the deepest of them all: vanilla infestations, VFE Insectoids 2 genelines,
  Alpha Animals hives, and Anomaly's `Entities.permanentEnemyToEveryoneExcept` all name
  it. The discarded world held 18 `BI_InfestationWorldObject`. Unticking removes the
  *faction*, not the bugs.
- `AA_BlackHive` — named in Alpha Animals' `Achievements.xml`.
- `MO_AbominationFaction` / `GiantAnt_Faction` — each is the `defaultFactionType` of
  its mod's pawnkinds, so the abomination and giant-ant incidents lose their home
  faction.

**Scenarios that will break only if you pick them** (they hard-name the faction):

- All four Yautja clans are `<factionDef>` entries in
  `3536839586/…/YautjaNormalStarts.xml` and listed in `Yautja_Race.xml`.
- `CASacrilegHunters` owns a whole pawnkind family in Caravan Adventures plus a Combat
  Extended patch keyed to those pawnkinds. Caravan Adventures is a *quest* mod; expect
  its story content to be thinner without the faction.

**⚠️ The one with a real side effect: `BS_LittlePeople`.** Its def carries
`<replacesFaction>OutlanderRough</replacesFaction>` — it substitutes for vanilla's
rough outlanders. **After unticking it, look for a "rough outlanders" row on the same
page and confirm the slot is filled by something.** If neither appears, the world has
no rough-outlander faction at all, which is a bigger fiction hole than the smallfolk
were. Record what you see.

**On the KEEP side, two dependencies that make keeping them load-bearing:**

- `guy762_KotORFaction_RogueDroids` is the `<hostileFactionDef>` of the droid
  distress-call incident in [BTD] Ship Pack: KotOR Ships VGE (3614012898). Keep it or
  that incident has no antagonist.
- `OuterRim_RebelAlliance` is a `permanentEnemyFactions` entry for `Force_Sith_Order`
  in **Star Wars: The Force Factions (3557220783)** — which is **downloaded but NOT
  active** (absent from `ModsConfig.xml`; no `Force_*` FactionDef in the 573-mod dump).
  The reference is `MayRequire`-guarded and inert today. **It stops being inert the
  day that mod is enabled**, which the current Jedi/Sith build spec contemplates.
  Flag for VISION alongside the Section 5 contradiction.

**Additive only, no action:** ReGrowth 2 (2260097569) patches both `OuterRim_GalacticEmpire`
and `OuterRim_RebelAlliance` biome/settlement data, and three mods patch `HoraxCult`
(2661356814, 2893432492, 3407831843). All are `PatchOperation`s against defs that
still exist; unticking a faction does not delete its def.

---

## Tally

| | count |
|---|---|
| **UNTICK — Section 1, ordinary rows** | 12 |
| **UNTICK — Section 2, hidden checkboxes** | 8 |
| **UNTICK — Section 3, not on the page (mod removal only)** | 1 *(`HoraxCult`; `Entities` and `VRE_Archons` listed alongside as cautions, not on the untick list)* |
| **UNTICK total proposed** | **21** |
| **KEEP** | **6** |
| **NOT FOUND on disk** | **0** |

**Before you leave the page**, screenshot it. It is the only record of what was
actually ticked, the world is not reproducible from this file, and a cold load is
~23–30 minutes.
