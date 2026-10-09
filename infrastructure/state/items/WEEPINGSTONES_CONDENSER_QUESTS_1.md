# WEEPINGSTONES_CONDENSER_QUESTS_1 — two optional quests on the walking condenser: the Hutts' capture for the Arena, or keeping it free with the Moisture Farmers against Blackstar's fame hunters

Caused by `WEEPINGSTONES_SCORING_SITTING_1` (turn 1). **Tier: quest machinery free, faction mapping campaign.**
The two QuestScriptDefs live in `mandrake.rm.weepingstones` with faction *slots* filled by vanilla factions in the
free mod (a wealthy collector faction for the capture; a settler faction and a pirate faction for keep-free); the
campaign layer (`src/RimUtinni/UtinniPatches`) maps the slots to the canon/campaign factions the owner named. Hutts are
IP and never appear in free text (Q11, Q11a: the free mod looks the same save the canon content). Design: `design/Jawa/worldbuilding/biomes/weepingstones_bedazzle_review_2026-10-02.md` §8.

Ruling: owner, typed 2026-10-02: *"I love (1). Optional quest from Hutts to capture it for the Arena (sad), or work
with Moisture Farmers to keep it free by foiling fellow hunters (Blackstar hunting it for fame)."*

## What exists

- `RUT_Jawa_HuttCartel` (FactionDef). The Arena is offstage by `HUTT_SLAVE_PIT_TEST_SITE_1` (*"A visitable arena is a
  later, separate build"*): the captured crab goes to it by letter.
- Blackstar Company reskins vanilla `Pirate` (`BlackstarCompany.xml`; `faction_roster_v2.md` l.171).
- "Moisture Farmer" is a forced pawn kind of the Homestead faction (`faction_roster_v2.md` l.955; the sheet's
  *"vaporator farmers"*). Its FactionDef defName: **measure, do not guess**.
- No quest, def or design text for either branch exists (searched `src/`, `design/`, items: "Arena" hits are the
  Geonosian hive and the slave pit's offstage note only).

## spec

Both optional, offered once the walking condenser is known; taking one forecloses the other.

1. **Capture for the Arena (sad).** The Hutt Cartel (free: a wealthy collector) offers a large reward to subdue and
   deliver the oldest gorrask alive. The crab is not killed: it is downed/sedated and hauled out by the buyer's
   party. The moving oasis ends; a letter says where it went and that it will never walk again (the sadness is in
   the text). Relations: buyer pleased; the water stewards and the moisture farmers displeased.
2. **Keep it free.** The Moisture Farmers (free: a settler faction) ask the clan to protect the crab through its next
   season; Blackstar hunters (free: a pirate faction) arrive hunting it **for fame** (trophy, not profit: their
   letter brags). Foil them (fight, misdirect, or turn the truce on them: a hunter who strikes first at the crab's
   pool brings the wild herds down on Blackstar). Success: farmers' goodwill, the crab walks on, and the farmers
   share a season at its pool.
3. Readable signs throughout (letters, quest text, the truce radius drawn at the crab's pool).
4. Quest validator: `rimworld-quests` skill's offline validator before any load.

Depends on: `WEEPINGSTONES_WALKING_CONDENSER_1`, `WEEPINGSTONES_TRUCE_HUNT_SUPPRESSION_1`.

## criteria

- Both QuestScriptDefs pass the offline validator; each fires from the dev quest menu on a quicktest with a
  debug-spawned condenser crab.
- Capture branch: crab removed with letter; the walking condenser's world state ends.
- Keep-free branch: hunters spawn, a guilty strike at the pool triggers retribution against their faction; success
  letter and goodwill.
- Free mod alone: no Hutt/Blackstar/canon string in any free-tier text (search); campaign loaded: the slots show the
  Hutt Cartel, the Homestead's moisture farmers and Blackstar.

## built (offline, FOUNDRY 2026-10-06; not seen in game)

- `src/RimMandrake/WeepingStones/Defs/QuestScriptDefs/RM_CondenserQuests.xml`: `RM_CondenserCapture`, `RM_CondenserKeepFree`
  (validator: 0 errors, 0 warnings). Random pool route, gated by `RM_QuestNode_GetCondenserCrab`.
- `Source/RM_CondenserQuests.cs`: crab gate + claim (accepting one withdraws the other; a Success settles it for the
  world), faction-slot node, downed watcher (no vanilla Downed signal), buyer takes the crab (DeSpawn + world pawn,
  pool dried, oasis ended), hunters raid targeting the crab (vanilla `QuestPart_RandomRaid.attackTargets`).
  Retribution is the existing water truce, not new code. Mod Settings toggle `condenserQuestsEnabled`.
- Slots: `Defs/FactionSlotDefs/RM_CondenserQuestSlots.xml`. Free: buyer Empire (else most advanced friendly),
  settlers OutlanderCivil, hunters Pirate.
- Campaign mapping: `src/RimUtinni/UtinniPatches/Patches/RUT_CondenserQuestSlots.xml` puts `RUT_Jawa_HuttCartel`
  at the head of `RM_FactionSlot_CondenserBuyer/preferredFactions` (Empire stays next). Homestead and Blackstar
  reskin OutlanderCivil and Pirate, so those two slots already land on them. L0: validate_patch 1 match;
  `selftest_condenser_slots.py`.
- Deviations: the buyer's crew taking the crab happens offstage, in a letter. No new truce-radius overlay was drawn.
  The "water stewards" have no free-tier faction, so only the settlers lose goodwill.

## verify

### Exact checks 2026-10-09 (acceptance sitting)
- C6 CHECK: Two loads. Free-tier list (no Utinni patches): `jawa/get_defs defs="RimMandrake.WeepingStones.RM_FactionSlotDef/RM_FactionSlot_CondenserBuyer;RimMandrake.WeepingStones.RM_FactionSlotDef/RM_FactionSlot_CondenserSettlers;RimMandrake.WeepingStones.RM_FactionSlotDef/RM_FactionSlot_CondenserHunters;QuestScriptDef/RM_CondenserCapture;QuestScriptDef/RM_CondenserKeepFree" fields="label,description,preferredFactions"` then regex the returned text for `Hutt|Blackstar|Homestead|Jawa|Kyber`. Campaign list (adds `src/RimUtinni/UtinniPatches/Patches/RUT_CondenserQuestSlots.xml`): the same call plus `FactionDef/RUT_Jawa_HuttCartel`, read preferredFactions. PASS: free list: success=true, the regex finds nothing and preferredFactions[0] is Empire; campaign list: preferredFactions[0] resolves to the Hutt Cartel faction (and the Settlers/Hunters slots to Homestead and Blackstar). FAIL: a canon string in the free-list text (IP leak across tiers), or the campaign list still showing Empire first (the patch missed its `li[1]` xpath and logs nothing).
