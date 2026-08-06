# Custom Quest Framework — what kinds of quests you can build

*Simple explainer, derived from reading the CQF source (`mod_sources/CustomQuestFramework-Old-src/`), keyed to the Jawa gravship campaign. Workshop 2978572782. Author: examined 2026-08-06.*

> **What CQF is (one line).** A visual, in-game editor that lets you hand-author quests as **explorable maps + talkable objects + branching dialog + scripted effects**, saved as XML defs — no C# required. It's the mod that makes the "authored set-piece" delivery path in `desert_world_design.md` §3E / §3E-bis real without writing an assembly.
>
> **Evidence basis.** Everything below is read directly from the source (class names quoted). Where I say "you'd use this for X in the campaign," that's *my inference/recommendation*, marked as such. The mechanics themselves are established from the code.

---

## 1. The mental model — CQF's four building blocks

CQF quests are assembled from four kinds of thing. Understanding these four is understanding the whole mod:

1. **Custom maps (submaps)** — hand-built explorable locations you design in a map editor and save to file (`GenStep_CustomMap`, `QuestEditor_SaveMapToFile`, `QuestEditor_CustomQuestMap`). These are the "dungeons": a derelict refinery interior, a buried city district, a Hutt market layout. You paint terrain (`GenStep_SetTerrain`), set fog (`GenStep_SetFog`), and place objects.

2. **Custom things (interactable objects)** — buildings the player's pawns can walk up to and *use*. The source has a family of these:
   - **`InteractableThing`** — a talkable/usable object (a console, a shrine, an NPC-ish machine). Interacting fires effects and/or opens dialog. *This is the persona-core voice hook* (`context.md` §D).
   - **`LootBox`** (`CustomThingData_LootBox`, `JobDriver_OpenLootBox`) — a container a pawn must travel to and open to release contents.
   - **`CustomTrap`** — a triggered hazard.
   - **`CustomMapEntrance` / `CustomMapExit`** — doorways that move pawns between the world and a submap (with a `_Chance` variant for randomized entrances).
   - **`ZoneCore`** — a zone whose completion is measured by conditions (size, tag, wealth).
   - **`Spawner`** — spawns things on a schedule.

3. **Dialog trees** — the branching-conversation engine (`DialogManagerDef` → `DialogTreeDef` → `DialogNode` → `DialogOption` → `DialogResult`). A `DialogManager` picks which tree to show based on **conditions**; each **option** can be gated, can **consume required items**, and fires **results** (effects). This is how you build "choose your response" quests.

4. **Actions (effects) — the `CQFAction` verbs** — the scripted consequences. This is the payload of every option/result/trap/interaction. Full verb list in §3 below.

Plus two cross-cutting systems: **conditions** (gate what's visible/available, §4) and **signals** (loose coupling between quest pieces, §5).

---

## 2. Spawn triggers — *when* a quest piece activates

Custom things carry a `SpawnType` (enum, verified — exactly four values):

| Trigger | Fires when… | Campaign use (inference) |
|---|---|---|
| `MapGeneration` | the map is generated | Standard set-piece placement — the refinery is *there* when you arrive. |
| `BuildingDamaged` | a specified building takes damage | A machine that "wakes" or retaliates when attacked — pairs with the **sacred-scrap** theme (strike the derelict → consequence). |
| `BuildingTick` | every tick while the building exists | Slow ambient effects — a leaking reactor, a pollution source. |
| `BuildingDestroyed` | the building is destroyed | The classic "you broke it, now the quest turns" beat. |

*Inference:* `BuildingDamaged` + `BuildingDestroyed` are the two that make the **sacred-scrap** rule (`context.md` §E) diegetic — you can attach a real in-fiction penalty (mood hit, faction anger, ambush) to violating a repairable ruin, rather than relying on a soft rule.

---

## 3. The action verbs — *what a quest can DO*

Every `CQFAction` subclass, read from `EditorBase.cs` (this is the complete list — 21 verbs). These are the atoms you compose quests from:

**Flow control (compose other actions):**
- **`Sequence`** — run a list of actions in order.
- **`Random`** — run one of several at random.
- **`Chance`** — run an action with probability *p*.

**Communication / signalling:**
- **`Message`** — show the player a message/letter.
- **`SentSignal`** — broadcast a named signal (see §5 — this is how quest pieces talk to each other).
- **`StartDialog`** — open a dialog tree (branch into conversation).

**Target-affecting verbs** (all extend `CQFAction_Target` — they act on pawns/things the quest references):
- **`Spawn`** — spawn a pawn/thing/building.
- **`Replace`** — swap one thing for another (e.g., intact console → broken console).
- **`Destory`** *(sic — spelled that way in source)* — destroy a target.
- **`Faction`** — **set a thing's faction** (recruit a pawn to the player, defect a building, flip ownership). Reads `FactionDef` — works with your roster factions.
- **`OpenLootBox`** — release a loot box's contents.
- **`RemoveDialogManager`** — retire a conversation (mark it "done"/consumed).
- **`SetDuty`** — assign an AI duty to a pawn (patrol, wait, guard — drives NPC behavior on submaps).
- **`Hediff`** — add/remove a health condition (injury, disease, implant, buff).
- **`Trait`** — add/remove a pawn trait.
- **`Explosion`** — detonate at a target.
- **`TakeDamage`** — damage a target.
- **`GainMood`** — apply a mood/thought (reward or punish emotionally).
- **`GainExperience`** — grant skill XP.

*Translation for the campaign:* with just these verbs you can author a quest that, on a dialog choice, **consumes a droid brain** (required-item, §6), **spawns** a repaired droid **set to the player faction** (`Faction`), grants the crafter **skill XP** (`GainExperience`) and a **mood** lift (`GainMood`) — with **no new mod and no research node**. That's the droid-manufacture and quest-progression economy (`context.md` branch-4; `required_mods.md` progression-source ruling) expressed entirely in CQF.

---

## 4. Conditions — *gating* visibility and choices

Conditions decide which dialog tree shows and which options a pawn qualifies for. Verified condition types:

- **`DialogTreeCondition_Faction`** — gate a whole tree on the interacting pawn's/target's faction (e.g., "the Hutt broker only talks to you if you're not hostile").
- **`DialogCondition_Skill`** — gate an option on a pawn skill level ("[Intellectual 8+] Splice the security loop").
- **`DialogCondition_Hediff`** — gate on a health condition ("[Cybernetic eye] Read the encrypted display").
- **`DialogCondition_Trait`** — gate on a trait ("[Kind] Reassure the frightened droid").

Plus **`ZoneCondition`** variants for zone-completion objectives: **Size**, **Tag**, **CoreTag**, **Wealth** (e.g., "clear a zone of a certain wealth" / "bring tagged items into this zone").

*Inference:* skill/trait/hediff gating is exactly the "roleplay-check" texture that makes the five authored Jawa founders (`jawa_crew_personas.md`) matter — a quest can react to *which* Jawa you send in.

---

## 5. Signals — how quest pieces coordinate (the "wiring")

`CQFAction_SentSignal` broadcasts a **named signal** via RimWorld's `SignalManager`. Other quest elements listen for that name. This is CQF's loose-coupling glue: instead of one monolithic script, you build many small pieces that fire and react to signals.

*Pattern:* "open loot box" → `SentSignal("refinery_looted")` → a separate trap/spawner listening for `refinery_looted` triggers the ambush. There's a `signalIsOnlyValidInPart` flag to scope a signal to the current quest instance so signals don't leak between quests.

---

## 6. Required items — quests that *cost* something

Dialog options can require (and consume) items before firing their result — `GameTools.ConsumeRequiredThings` (seen in `DialogTree.cs`). This is the mechanical backbone of a **barter/turn-in quest**:

- Turn in **droid brains** → get a working droid (the anti-exponential throttle made literal).
- Pay a **tribute of silver/goods** → the Hutt broker stands down (dovetails with the Tribute Demand / Raid Protection Fee mods already adopted).
- Deliver **artifacts** → a faction reward (or, at the §3E-bis archaeological preserve, *decline* to and keep goodwill).

---

## 7. The seven quest *shapes* you can build (composed from the above)

Putting the primitives together, these are the practical quest archetypes CQF supports — each mapped to a campaign use:

1. **Explorable dungeon.** A custom submap reached through a `CustomMapEntrance`, populated with loot boxes, traps, and guardian pawns. → *Buried-city district, derelict refinery interior, crashed-capital-ship hull (`desert_world_design.md` §3E-bis nodes 1, 11, 14).*

2. **Talk-to-the-object quest.** An `InteractableThing` + `DialogTree`, options gated by skill/trait/faction, firing effects. → *The **LifeDawn persona core**: walk up to the restored grav-controller, it speaks via a dialog tree (`context.md` §D).*

3. **Turn-in / barter quest.** Dialog option with **required items** → reward action. → *Droid-brain → droid; tribute → safety; artifacts → reward.*

4. **Break-it / trap quest.** `BuildingDamaged`/`BuildingDestroyed` spawn triggers + `Explosion`/`Spawn`/`GainMood`. → *Sacred-scrap enforcement: violate a repairable ruin, suffer a consequence.*

5. **Escort / duty quest.** `SetDuty` + patrol jobs + map entrances/exits. → *Guide a rescued NPC off a submap; a guarded caravan.*

6. **Zone-objective quest.** `ZoneCore` + `ZoneCondition` (size/tag/wealth). → *"Secure this district," "gather X into the hold."*

7. **Multi-stage chained quest.** Everything above wired with **signals** + `RemoveDialogManager` to advance state. → *The 3-act Empire arc beats seeded across tiles — each set-piece sends a signal; a hidden "arc tracker" reacts.*

---

## 8. Limits & cautions (so we author to CQF's grain, not against it)

- **This is a `-Old-src` snapshot.** Verify the *installed* build matches these class names before authoring at scale; the editor UI may have moved on. *(Recommendation: confirm against the live mod in-game once installed.)*
- **`Destory` is misspelled in source** — a cosmetic tell that this is community code; not a functional problem, but a reminder to test each authored quest in a throwaway save.
- **No native "timer that moves a site every year"** — the §3E-bis relocating-market (node 12) and re-exposing-battlefield (node 3) need a spawn/despawn hook that CQF's `SpawnType` doesn't directly express; those two likely lean on the **RimMaster/RimBridge** layer or a `Spawner` + signal loop. *(Flagged in `desert_world_design.md` §3E-bis as build-time TBD.)*
- **Anti-exponential discipline still applies.** CQF makes it *easy* to hand the player rewards — every authored reward inherits the §19.5 arsenal-audit caveat (`Custom_World.md`) and the 7-question test (`forbidden_mods.md`). CQF is a delivery tool, not a license to inflate the player ceiling.

---

## 9. Decision translation (for the campaign)

- **Decision this enables:** author the §3E / §3E-bis set-pieces *in-game* as reusable CQF quests instead of relying solely on save-editing — the preferred delivery path (`desert_world_design.md` §3E, tier "Ancient Urban Ruins + CQF").
- **Viable alternatives:** native Odyssey Landmarks (cheapest, least controllable); RimMaster save-authoring (most controllable, most fragile). CQF sits in the middle: reusable, in-game, no code.
- **Tradeoffs:** CQF authoring is *hand-work* per quest (editor time), but the pieces are reusable and version-safe in a way save-edits aren't.
- **Dependencies:** CQF (2978572782) installed + 1.6-verified; Ancient Urban Ruins for the ruin submaps; roster `FactionDef`s must exist for `Faction`-based conditions/actions.
- **Principal risk:** authoring the `-Old-src` API against a drifted live build — test early on a scratch save.
- **Missing info:** whether the installed CQF version's editor still exposes all 21 action verbs and 4 spawn types as read here. *Next step:* install, open the Quest Editor, and confirm the verb/condition palette matches this document before committing to CQF for arc-critical nodes.
