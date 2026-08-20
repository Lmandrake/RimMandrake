# WORLDGEN_FACTION_CHECKLIST.md — the Configure Factions page, box by box

> 🔴 **STANDING OWNER RULING — 2026-08-15. THERE IS NO WORLDGEN FEATURE, IN ANY VERSION.**
>
> Verbatim: *"There is no auto worldgen we are building. The world will be user-made and
> frozen. We are NOT enabling worldgen, we will provide players a savegame with a fixed
> world, period. That's it. True worldgen is OUT of any version, even v2."*
> Clarified moments later: *"(but designing worldgen by hand and design documents to
> guide that are in)"*
>
> **OUT, permanently — this is not a deferral:**
> - Any automated or programmatic worldgen we build. No tool, script, DLL or bridge verb
>   that generates a world as a product.
> - Worldgen as a player-facing capability. **Players never generate anything.** They
>   receive a savegame containing the fixed world.
> - Any v2 worldgen item. ⛔ **v2 is NOT a parking space for this** — mark such work
>   dead, do not move it to `design/V2_DREAMS.md`.
>
> **IN, unchanged and still wanted:**
> - The owner building the world **by hand, once**. That is how the fixed world exists.
> - **Design documents that guide him doing it** — `WORLDGEN_FACTION_CHECKLIST.md`,
>   `SCENARIO_SETTINGS_SPEC.md`, the faction, biome and terrain specs. Keep writing them.
>
> 🔑 **The consequence, and it got stronger rather than weaker:** one hand-made world,
> frozen, then shipped to every player. **A faction, ideoligion or setting absent when he
> builds it is absent from every player's game forever, with no regenerate to fall back
> on.** That is why the faction roster and the faith text stay v1.


> # ✅ RATIFIED — a retired seat, 2026-08-13. EXECUTE THE LIST.
>
> **21 untick / 6 keep is RATIFIED as written.** Nothing in the tick-list changes.
> Four rulings ride with it; read them, they take ten seconds each.
>
> ## R1. Dangling references: a retired seat was RIGHT, and blanket "accepted cost" is REFUSED
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
> incident thinning — not dead-end quests. **The objection was right, it is
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
> ## R3. ⭐ ADD vanilla `Empire` to KEEP — it is THE GALACTIC EMPIRE

**Owner's canon, 2026-08-13.** Vanilla `Empire` is reskinned as **the Galactic
Empire**, led by **Emperor Palpatine**. It is the campaign's **one permanent
enemy** and the thing that pursues the gravship.

🔴 **The "Fallen Dominion" and the two-Empire split are STRUCK from the design.**
There is no local or planetside Empire. Any earlier note describing a disgraced
local aristocracy is superseded and must not be acted on.

**Confirm vanilla `Empire` is present and its count is ≥ 1.** It is not on the
untick list, so it survives by default — confirm it anyway. ⚠️ **Its name is
generated**, so the world will not say "Galactic Empire" until a `fixedName`
patch lands. **Screenshot whatever it does say.**

## R4. Do not ship a world with no rough outlanders
>
> `BS_LittlePeople` declares `replacesFaction OutlanderRough`. **After unticking
> it, confirm a rough-outlander row exists at ≥ 1.** If none appears, **leave
> `BS_LittlePeople` at 1** rather than generate a world missing that slot — a
> smallfolk union is a smaller fiction hole than an empty outlander tier.
>
> ## What REMAINS STANDING after the cut — the world is populated
>
> **6 keeps:** binary star raiders · Confederacy of Independent Systems ·
> **the Galactic Empire** · moisture farmers · rogue droid collective ·
> *(Rebel Alliance retired per R2)*.
> **Plus, untouched by this list:** vanilla **`Empire` = the Fallen Dominion**,
> outlander unions, rough outlanders, tribes and pirates. **Nobody is unticking
> vanilla's spine.** The world has a Galactic arm, a disgraced local aristocracy,
> farmers to trade with, droids and separatists to fight, raiders, and the
> ordinary outlander/tribal economy underneath. **That is a world with people in
> it.**
>
> 🔴 **Screenshot the page before leaving it.** It is the only record.

⚠️ **Quoted above as written, but superseded:** the words "`Empire` = the Fallen
Dominion" and "a disgraced local aristocracy" are STRUCK — see the ruling at the
top of this section. Vanilla `Empire` **is** the Galactic Empire; there is no
second Empire. The keep itself stands: confirm vanilla `Empire` present, count ≥ 1.

> ✅ **A retired seat's note — RESOLVED, nothing here blocks execution.**
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

**What you are doing and why.** v1 generates a new world from scratch, and faction
existence is decided **once, at world creation**, on vanilla's *Configure Factions*
page that Faction Control unlocks and extends.

> ⚠️ **Premise corrected 2026-08-13, same day this was written.** The original text
> here said the old saves were deleted and therefore gone. **They are back** — Steam
> Cloud restored 26 `.rws` (701 MB, original mtimes) at the 17:30 launch, including
> `New Arrivals2.rws` at 43,738,239 bytes. The delete happened and simply did not
> survive. **This does not change the checklist**: the owner's decision to regenerate
> for v1 stands on its own, and a faction baked into the old save still cannot be
> removed by any setting. But do not repeat "the saves are gone" — it is false on
> disk. ❌ **"Re-deleting needs Steam Cloud disabled first" was WRONG and is
> superseded by the owner's ruling of 2026-08-14: delete while the game is
> RUNNING.** Cloud reconciles at launch and wins, so a delete with the game DOWN
> is what got undone; the live window is where it sticks. **Do NOT disable Steam
> Cloud — that is no longer the fix and was never asked for.**
> ⏳ **This rule EXPIRES the day the real campaign starts.** It exists only for
> throw-away debugging worlds, and a standing "delete the saves" against a live
> campaign would be destructive.

There is no suppression setting to write to a file afterwards — Faction
Control's `density` is a clumping radius, not a count, and setting it to 0 does
nothing. So this page is the only lever, and it fires once. The goal is a world that
reads as Star Wars: keep the SW factions, drop the Norse/medieval/fantasy ones, the
Predator clans, and the horror/bug factions that have no SW reading. Work down this
list at the screen, tick the boxes, and **record what you actually saw** in the
`observed` column — the page is the ground truth, this file is a prediction.

> 🔴 **This is a PROPOSAL from a retired seat. DECIDE ratifies it.** That seat was player zero here,
> not the designer. Nothing below is authority to change the design; it is evidence
> in, decision out. If DECIDE has not signed off, do not execute the untick list —
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
(`observed/2026-08-13/dumps/manifest.573.2026-08-13.json`, 87
FactionDefs — the `defnames.573` dump the count was first read from is bulk, deliberately
not committed, and no longer on disk; the manifest carries the same `defCounts`) and every one was read from its source XML for its label and its
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
| ☐ | **A little people union** | `BS_LittlePeople` | Big and Small - Races (2894397737) | 🔴 **STOP after unticking — R4 above.** It declares `replacesFaction OutlanderRough`. **Confirm a rough-outlander row exists at ≥ 1. If none appears, PUT THIS BACK TO 1** — a smallfolk union is a smaller fiction hole than an empty outlander tier. |
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
| ☐ | **giant ant colony** *(shows as "They!")* | `GiantAnt_Faction` | They! (Giant Ants) (3620253282) | 🔴 **OWNER WANTS THESE IN v2** — dangerous deep-desert colonies (`design/V2_DREAMS.md`). A faction absent at world creation can NEVER be added later, so unticking it here means v2 ants need a new campaign. **Leave at 1 if the idea is wanted.** |
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
the Anomaly playstyle setting) — NOT a worldgen tick.** Listed here so you do not
spend ten minutes scrolling for a row that does not exist.

✅ **The vanilla two are RESOLVED, not open.** The owner ruled 2026-08-13 that
**Anomaly content is set to zero**, so `HoraxCult` and `Entities` are handled by
that setting and need nothing from this checklist. *(This was carried here as "a
separate proposition for two now-retired seats"; it is decided.)* The DLC stays enabled —
its creatures and abilities remain available to us for reskinning.

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
| ~~☐~~ | ~~**`OuterRim_GalacticEmpire`**~~ | ~~`OuterRim_GalacticEmpire`~~ | ~~Outer Rim - Galactic Empire (2919248699)~~ | ⛔ **DEAD ROW 2026-08-20 — do not check it, do not expect it.** Owner: *"OuterRim_GalacticEmpire is no longer in the game, we patch Empire."* The Galactic Empire's vessel is **vanilla `Empire`** (the ⭐ row below) and nothing patches this def. Whatever this row does or does not say at worldgen is **not a signal about anything**. See `infrastructure/state/OWNER_DECISIONS.md`. |
| ☐ | **moisture farmers** | `OuterRim_MoistureFarmers` | Outer Rim - Core | ordinary row |
| ☐ | **rogue droid collective** *("Droid Collective")* | `guy762_KotORFaction_RogueDroids` | Star Wars KotOR Droids (3047371944) | **hidden checkbox**, not a row. 🔴 **quest-critical — antagonist of the KotOR distress call. Never untick.** |
| ☐ | ⭐ **vanilla `Empire`** — *name will be GENERATED, expect a different string* | `Empire` | **vanilla (Royalty)** | 🔴 **ADDED TO KEEP by R3 above.** Not on any untick list, so it survives by default — **confirm it anyway, count ≥ 1, and SCREENSHOT the generated name.** |
| ☐ | ~~**Rebel Alliance**~~ — **RETIRED from KEEP** | `OuterRim_RebelAlliance` | Outer Rim - Rebel Alliance (2919249903) | 🔴 **ABSENT is the DESIRED outcome (R2 above). Record absent and move on — do NOT revert the patch at the screen.** |

⭐ **On vanilla `Empire` (R3 above, owner's ruling).** Vanilla `Empire` **is** the
Galactic Empire — the campaign's one permanent enemy, led by Emperor Palpatine.
🔴 **The "Fallen Dominion" and the two-Empire split are STRUCK from the design**
(see the header of this file). There is no local or planetside Empire, no
disgraced local aristocracy, and nothing on this page turns on that reading.
**The only gate here is: vanilla `Empire` is PRESENT and its count is ≥ 1.**
⚠️ **Its name is generated, so the world will not say "Galactic Empire" until a
`fixedName` patch lands. That is expected, not a failure.** Whatever it generates
is the working name. **Screenshot it — that string is the only record.**

⛔ **THIS WHOLE PARAGRAPH IS DEAD, 2026-08-20 — it tells you to expect a string that
can no longer appear.** `ImperialDesertDirectorate.xml` was re-pointed on 2026-08-14 and
**every xpath in it now targets vanilla `Empire`**; it does not mention
`OuterRim_GalacticEmpire` outside its own comment header. Nothing patches that mod def
any more, so there is **no expectation to check** on it. The string to look at is on the
⭐ vanilla `Empire` row above — the patch adds `fixedName` **"Galactic Empire"**, so that
row should read *Galactic Empire* rather than a generated name once the deploy has
landed. See `infrastructure/state/OWNER_DECISIONS.md`.

~~🔴 **On the `OuterRim_GalacticEmpire` row, expect "Imperial Desert Directorate" —
and do not stop for it.**
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Jawa_Patches\Patches\ImperialDesertDirectorate.xml`
(repo copy: `D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\Patches\ImperialDesertDirectorate.xml`,
byte-identical on disk 2026-08-13) replaces `label` **and** `fixedName` on
`OuterRim_GalacticEmpire` with **"Imperial Desert Directorate"**, and `leaderTitle`
with **"Sector Director"**. That is the string that will be on the page.~~

~~**It is superseded scaffolding, not a defect.** The Directorate reskin predates
a retired seat's strike of the two-Empire split and has not been redeployed, so the old
string simply survives. ⚠️ **Seeing "Imperial Desert Directorate" is EXPECTED and
is NOT evidence of a bad deploy — do not abort worldgen over it.** If the row
instead reads the stock **"Galactic Empire"**, that only means the Jawa_Patches
deploy did not land; **record which of the two strings you saw and carry on** —
neither blocks generation, because this faction is no longer the antagonist the
design hangs on.~~

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
  Flag for DECIDE alongside the Section 5 contradiction.

**Additive only, no action:** ReGrowth 2 (2260097569) patches both `OuterRim_GalacticEmpire`
(⛔ **not our Empire** — the vessel is vanilla `Empire`, 2026-08-20; this is a third-party
patch on a def we do not use, and it is listed here only for completeness)
and `OuterRim_RebelAlliance` biome/settlement data, and three mods patch `HoraxCult`
(2661356814, 2893432492, 3407831843). All are `PatchOperation`s against defs that
still exist; unticking a faction does not delete its def.

---


## SECTION 4b — 🔴 OUR OWN FACTIONS. SET EACH TO AT LEAST 1.

**These did not exist when the rest of this file was written.** They are the
campaign's authored roster, built and deployed 2026-08-14.

> 🔴 **A faction absent at worldgen CANNOT be added later.** This is the single
> most expensive mistake available on this page. If one of these reads 0 when you
> leave, that faction does not exist in your campaign, permanently.

⚠️ **A strict diff against this file's other sections will show these as
"unexpected". That is the expected outcome** — they postdate the untick list.

### The 8 that appear as NEW rows — set each ≥ 1

| ✔ | expect the label | defName |
|---|---|---|
| ☐ | **Hutt Cartel** | `Jawa_HuttCartel` |
| ☐ | **Free Droid Enclaves** | `Jawa_FreeDroidEnclaves` |
| ☐ | **Wildsteam Clan** | `Jawa_WildsteamClan` |
| ☐ | **Deepwater Compact** | `Jawa_DeepwaterCompact` |
| ☐ | **Geonosian Foundry Hive** | `Jawa_GeonosianFoundryHive` |
| ☐ | **Ascendant Helix** | `Jawa_AscendantHelix` |
| ☐ | **the Junkers** | `Jawa_Junkers` |
| ☐ | **Jawa Trade Moot** | `Jawa_IndigenousTribes` |

All seven authored defs carry `requiredCountAtGameStart 1`, so they *should* be
forced — but **"should be" is not "was"**, and this run is permanent. Look at each.

### The 5 vanilla rows we RESKINNED — confirm present, do not untick

| ✔ | on the page it will read | defName | is now |
|---|---|---|---|
| ☐ | a generated Empire name | `Empire` | **the Galactic Empire** — also in Section 4 |
| ☐ | an outlander union | `OutlanderCivil` | **Homestead Defense League** |
| ☐ | a tribe | `TribeCivil` | **Deep Desert Tribes** |
| ☐ | a pirate band | `Pirate` | **Blackstar Company** |
| ☐ | *(hidden checkbox)* | `Mechanoid` | **the Forgotten Arsenal** |

🔴 **Unticking any of these five deletes one of our factions.** They look like
ordinary vanilla rows and they are not any more.

⛔ **The Unbound Hive is NOT here and that is deliberate.** `Insect` stays on the
Section 2 untick list; the faction was cut for exactly that reason. Do not hunt
for it.

## Tally

| | count |
|---|---|
| **UNTICK — Section 1, ordinary rows** | 12 |
| **UNTICK — Section 2, hidden checkboxes** | 8 |
| **UNTICK — Section 3, not on the page (mod removal only)** | 1 *(`HoraxCult`; `Entities` and `VRE_Archons` listed alongside as cautions, not on the untick list)* |
| **UNTICK total proposed** | **21** |
| **KEEP — Section 4** | **6** |
| **SET ≥ 1 — Section 4b, our own** | **13** *(8 new rows + 5 reskinned vanilla rows)* |
| **NOT FOUND on disk** | **0** |

**Before you leave the page**, screenshot it. It is the only record of what was
actually ticked, the world is not reproducible from this file, and a cold load is
~23–30 minutes.
