# The Unfinished Line — the Hive/Enclaves droid-production quest chain (design proposal, 2026-10-02)

Item: `DROID_MASS_PRODUCTION_QUEST_CHAIN_1`. **DESIGN ONLY**, for the owner to rule on: no defs, no
code, nothing filed. Written by a BENCH helper under the `rimworld-quests` skill. Engine facts are
from RimSage (decompiled 1.6) unless marked UNMEASURED.

**One-line pitch.** The Enclaves are dying one droid at a time, and the Hive is sitting on a factory
it cannot run. The Jawa are outsiders to both, and salvagers who already repair droids, so they are
the only people who can stand between them. Five beats take the player from repairing three broken
Enclave droids to defending the first production run against the Empire. The payoff is a working
line **in the world**, a large Free Droid reputation gain, and droid construction opening to the
player. **The head-gate stays intact**: the line makes bodies, never minds.

---

## 1. What exists (measured)

### 1.1 The two factions (shipped)

| | defName | file | notes |
|---|---|---|---|
| Hive | `RUT_Jawa_GeonosianFoundryHive` | `src/RimUtinni/UtinniPatches/Defs/FactionDefs/JawaGeonosianFoundryHive.xml` | `OutlanderFactionBase`, Spacer, Archduke leader, culture `RUT_Jawa_Culture_Geonosian`, ideo `Meckgin`; kinds `RUT_Jawa_Geonosian_Grunt/_Heavy/_Specialist/_Leader`. **No hive, foundry or queen buildings exist in `src/`.** Vanilla `Settlement` world objects only. |
| Enclaves | `RUT_Jawa_FreeDroidEnclaves` | `src/RimUtinni/UtinniPatches/Defs/FactionDefs/JawaFreeDroidEnclaves.xml` | ideo `the Continuity Protocol`, First Speaker R-41 Rell; kinds `RUT_Jawa_Droid_Grunt/_Heavy/_Specialist/_Leader`. ⚠️ These still `MayRequire Neronix17.OuterRim.DroidDepot`, so they are not yet re-pointed to Droidworks races. That is the C1/C2 work in `DROID_UNIFIED_FRAMEWORK_DESIGN.md` §3.2. |

**The lore the chain must honour** (all from the owner, with the trace to his words):

- **The Hive and the Enclaves are formally allied, with trade** (owner 2026-08-17,
  `design/Jawa/worldbuilding/FACTION_SPEC.md` "RULED 2026-08-17"; `faction_roster_v2.md:189`). Both
  came from the same silicax-oxalate company site. The Hive was **bought whole on indenture**, and
  when the company left, **the queen would not leave: "too much left undone" IS Meckgin**. The Hive
  has two sites, the **Ore Seams** and the **Plateau** splinter that worships the Rust Cathedral. The
  Cathedral ignores the Plateau because they are organic (`reconciled_lore/04_factions.md` §8).
- **The Jawa clans stole their sandcrawlers from that same collapsed silicax holding**
  (`reconciled_lore/06_the_ship.md:124`). So all three parties share one ruin, which no doc yet uses.
- **The Hive is hostile to the player at start** (−100 is the design figure;
  `faction_tech_alignment.md:277` says *"−100 start, 'not permanently' hostile; a mid-game wedge"*).
  It does not trade with the player, ransom or rescue (`04_factions.md` §8). ⚠️ The live start
  value is UNMEASURED: `FactionDef` has no goodwill field, and the roster notes *"CUT FROM V1"*.
- **The Enclaves start at goodwill 0**, as *"a HISTORY, not a dial"*. They do not raid; they judge.
  Restraining bolts are slavery, and memory erasure is worse than killing (`04_factions.md` §5).
- **The Geonosian Alliance arc already exists** (owner 2026-09-04, `04_factions.md` §8 and
  `09_arcs_dungeons_quests.md` 2a). The Hive, unsung and desperate, trades a protected base for
  ship/urn tech, *"until the Empire catches wind and utterly destroys their settlements.
  Geonosians just don't understand politics at all."* **This chain must interlock with that arc,
  not duplicate it** (see Q4).
- **The gods.** ② **Ohm** is *"lonely for his lost hands (droids); pressures the clan toward
  droids"*. ⑤ **Rekko of the Second Hand**: *"restore ≠ transcend"*. ③ **Oomo** *"hates droids in
  chambers meant for eggs"*. ⑨ **Ozzik**'s pride meter is the anti-exponential clock. The win-path
  map gives **Ohm+Sh'kaar → droid-army-by-force** (`reconciled_lore/05_the_clan.md`). A factory is
  exactly where Ohm and Rekko fight.

### 1.2 The droid platform: what a droid IS here (Droidworks, shipped)

- **One construction method, "the shop".** A droid is **1 head + 1 frame + a part set**, assembled at
  `RSW_DW_ReassemblyHarness` (recipe `RSW_DW_AssembleDroid`, worker
  `RimMandrake.StarWars.Droidworks.Recipe_AssembleDroid`). Repair happens at `RSW_DW_RepairBench`.
  Heads: `RSW_DW_Head_Labour/_Protocol/_Astromech/_Battle/_Heavy/_Probe/_Power/_Primitive`
  (`src/RimStarWars/Droidworks/Defs/ThingDefs/Heads_Droidworks.xml`).
- **The head-gate (owner ruling 6, 2026-09-06, `design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md`
  §0).** The brain trio (`RSW_DW_PersonalityMatrix`, `RSW_DW_Processor`, `RSW_DW_Databank`) is
  *"too high tech and specialized for anyone on this world to make"*. It comes only as salvage,
  stock or quest loot. *"No head, no droid."*
- **Research** (`src/RimStarWars/Droidworks/Defs/ResearchProjectDefs/ResearchProjects_Droidworks.xml`):
  `RSW_DW_Research_Reboot → _Bolting → _Spiking → _ShopRepair → _Reassembly → _PrimitiveFabrication
  → _Formatting`. Primitive part recipes are gated on `_PrimitiveFabrication`.
- **Axis 18b** (`design/RimMandrake/balance_paradigm.md:466`): *"parts are manufacturable; minds are
  not"*. Whole droids are **not** manufacturable. The creed is *"we do not breed new hands"*. Its
  closing line, *"'the neutral droids taught us to tend our own' is a quest reward that hands over
  technique, not a factory"*, is the closest prior ruling to this chain.
- **Droid construction is an Enclave-held faction reward** (owner 2026-09-03,
  `faction_tech_alignment.md` §2.5; the manifest holds 27 rows as `Enclaves`). The v4 shape
  (`research_review/droid_and_saber_rulings.md:300-330`) is that *"every print is paid in a freed
  droid"*, and that *"what you build with their teaching is born free"*.
- **Droid Depot's auto-factory is dead.** `src/RimUtinni/Doctrine/Patches/NoDroidManufacture.xml`
  clears `OuterRim_DroidFactory`'s designation, and the Droidworks design cut *"the auto-factory"*
  as magic. ⇒ **The line must not be a pawn-printer.** It is a shop-floor that turns out bodies.

### 1.3 Quests we ship (patterns to reuse)

There are 12 shipped `QuestScriptDef`s. The relevant precedents:

- **`RUT_DroidRepairJob`** (`src/RimUtinni/DroidRepairJobs/`) uses custom `QuestNode_DroidRepairJob`
  and `QuestPart_DroidRepairJobOutcome`. Beat 1 is built directly on it.
- **`RUT_KyberHomesteadVisit` / `RUT_KyberDonationSmuggle`** are signal-fired, weight-0 chain links
  (`src/RimUtinni/KyberTradePlot/`). They are our existing proof of a chained quest.
- **`RM_Quest_RiteOfTipping`** is incident-fired and carries a custom `QuestPartActivable`.
- **`RUT_VaultThaw_V1_RustCathedral`** uses `isRootSpecial` plus a GiveQuest incident.

### 1.4 Engine facts this design rests on (RimSage, decompiled 1.6)

- **Epic chains are native.** `QuestScriptDef.epicParent` exists (`QuestScriptDef.cs:82`).
  `QuestPart_SubquestGenerator` (abstract, `QuestPartActivable`) generates child quests with
  `quest.parent` set, counts `SuccessfulSubquestCount`, and completes at `maxSuccessfulSubquests`.
  Ideology's Relic Hunt (`QuestNode_Root_RelicHunt`) is the worked example. The subclass must
  supply `GetNextSubquestDef()` and `InitSlate()`; vanilla's own subclasses pick **at random**, so a
  **sequential** chain needs our own small subclass.
- `QuestPart_AddQuest` (abstract) generates **and auto-accepts** a follow-on quest on a signal.
- `QuestNode_ChangeFactionGoodwill` takes `faction`, `change`, `reason` (a `HistoryEventDef`) and
  `ensureHostile`.
- **Relation hysteresis** (`FactionRelation.CheckKindThresholds`): Hostile at ≤ −75, back to
  Neutral **only at ≥ 0**, Ally at ≥ 75, losing Ally only at ≤ 0. Lifting the Hive out of hostility
  from −100 therefore takes **+100**.
- `QuestNode_GetFaction` has **no goodwill threshold filter** (fields: allowEnemy, allowNeutral,
  allowAlly, allowPermanentEnemy, leaderMustBeSafe, …). A "goodwill ≥ N" gate needs C#.
- Stock nodes used below, all verified to exist: `QuestNode_RequirementsToAcceptResearch`,
  `QuestNode_ExtraFaction`, `QuestNode_LendColonistsToFaction`, `QuestNode_TradeRequest_Initiate`
  (**one** `requestedThingDef` per request, and it needs a non-hostile `Settlement`),
  `QuestNode_GenerateMonumentMarker`, `QuestNode_SignalActivable`, `QuestNode_Signal`,
  `QuestNode_GenerateSite`, `QuestNode_QuestUnique`.

### 1.5 Contradictions found — RULED and propagated 2026-10-03

The three contradictions (roster Hive droids as mass-produced at 35–55 % of combat points; the
Enclave-theft heist premise; the tech-alignment "contested" holding) were corrected in place in
`faction_roster_v2.md`, `FACTION_SPEC.md`, `faction_tech_alignment.md`, `09_arcs_dungeons_quests.md`
and their inbound references. The Hive's droids are repaired company-era leftovers (share unset).

---

## 2. The chain, step by step

### 2.0 Spec (the six lines, `rimworld-quests` §2)

| line | answer |
|---|---|
| **The ask** | Repair, broker, salvage, supply and defend a droid line that neither ally can build alone. |
| **The reason** (no reward named) | The Enclaves cannot replace a single fallen droid. Every loss is permanent, and the Hive's queen cannot bear work left undone. |
| **The choice** | **Where the line stands, and who it answers to** (beat 2). It is acknowledged in beats 4–5 and in the epilogue. A second choice is **sell the pattern cores** (beat 3). |
| **The failure state** | Each beat can fail survivably and costs goodwill. Only betrayal or the line's destruction ends the chain. The epic parent can be re-offered after a long cooldown. |
| **The reward** | Enclave reputation up to Ally, the Enclave droid-construction branch, and a line that runs in the world. No silver payouts beyond reimbursement. |
| **The deadline** | Every beat carries a real, shown timer (`QuestNode_Delay isQuestTimeout`). Between beats the parent waits 5–10 days, the Relic Hunt cadence (300000–600000 ticks). |

**Fiction: why the player is needed.** The obstacle is will, not hostility, and it runs both ways.
**Meckgin will not hand over the work**: knowledge given away is work undone, so the Hive will
only share the patterns if a line is actually *built and worked*. **The Continuity Protocol will
not let organics hold a droid factory**, because that is how they were made the first time. Each
ally needs the other and cannot trust the other with the line. The Jawa are salvagers, outsiders
to both and already the planet's droid repairers. They are the neutral hands both can tolerate in
the middle. That is the hook, and it uses only established facts.

### 2.1 Beat 1 — "The Count" (Enclave asker)

- **Offer.** This is the epic parent's first child. The parent fires from a GiveQuest incident gated
  on: Enclave goodwill ≥ 20 and not hostile; the player has `RSW_DW_Research_ShopRepair`; at least
  one Hive and one Enclave settlement exist; and the day is ≥ 30 (§3.2).
- **Ask.** A protocol-droid principal brings three badly damaged Enclave droids for repair within
  6 days. This is the `RUT_DroidRepairJob` machinery with the faction fixed to the Enclaves. The
  letter carries **the count**: *"Forty-one of us fell this year. None were replaced. None can be."*
- **Choice.** Fit **your own good parts** (they cost you, give +goodwill, and the protocol droid
  notes it) or **scrounge inferior parts** (cheap, and the droids leave with hardware quirks). A
  Jawa choice, and the Enclaves remember it in beat 2's text.
- **Failure.** A droid destroyed in your care costs −15 Enclave goodwill (`QuestPawnLost`-style
  event), and the parent re-offers beat 1 after 15 days. Running out of time costs −5.
- **Reward / unlock.** +10 Enclave goodwill. **R-41 Rell asks the question**: the Hive has the
  patterns, and will the Jawa carry the Enclaves' word? This unlocks beat 2.

### 2.2 Beat 2 — "The Envoy" (the broker beat; the central choice)

- **Ask.** On acceptance a **brokered truce** applies (custom part, §3.3; Q2): the Hive becomes
  Neutral for the chain's duration. A Hive envoy then arrives at your colony and stays 4 days: a
  **Foundry Engineer** (Savant caste), an **aristocrat**, and two Enclave security droids as escort.
  They lodge under the vanilla Hospitality pattern (`QuestNode_ExtraFaction`). The envoy judges
  whether Jawa hands can be trusted with the work.
- **Pressure inside the beat.** Meckgin reads idleness as *"the beginning of the end of the
  world"*. If the envoy sees the colony's work bills sitting idle, Hive goodwill drops (optional
  custom tick check, behind a setting). The aristocrats compete with each other, so the aristocrat
  needles the Enclave escort, and a social fight is possible.
- **THE CHOICE: where the line stands.** It is offered as a `QuestPart_Choice` on success, with
  one `End` per option:

  | site | who it answers to | Enclave | Hive | Empire exposure | unlocks |
  |---|---|---|---|---|---|
  | **A. The old silicax foundry ruin** (neutral ground; recommended) | joint, with the Jawa as stewards | ++ | ++ | the site, not your base | beats 3–5 at a world site |
  | **B. Your colony** | the Jawa | + (wary: organics holding the line) | + | **your base** | beats 3–5 at home; you get the building (Q1) |
  | **C. Enclave ground** (Cathedral plateau) | the Enclaves | +++ | − (Meckgin unsatisfied: they cannot work it) | the Enclave settlement | beats 3–5 at that settlement |
  | **D. The Ore Seams** (the aristocrat's offer) | the Hive | −− (*"Foundry product, again"*) | +++ | the Hive settlement, which speeds up the Alliance arc's doom | beats 3–5 at the Hive |

- **Failure.** The envoy is harmed, or the player attacks a Hive pawn. The truce ends,
  `ensureHostile` fires on the Hive, and the chain fails (the parent may be re-offered after 60 days).
- **Reward.** +15 Hive goodwill and +10 Enclave goodwill, adjusted per site. The Engineer's
  description names what is needed: **the three pattern cores** still sealed in the ruin.

### 2.3 Beat 3 — "The Pattern Cores" (site quest)

- **Ask.** A site at the old silicax foundry ruin (`Util_GenerateSite`, a new `SitePartDef`).
  Recover **three `RUT_FoundryPatternCore`** (new quest item) from the collapsed fabrication hall.
  The hall is held by **wild droids gone crazy in the desert** (the Droidworks wild-droid kinds, ruling 2),
  scaled by `points` through `Util_AdjustPointsForDistantFight`.
- **Choice (light).** Spike and capture the wild droids, or destroy them. **Every captured one
  that is handed to the Enclaves unbolted** adds goodwill. This ties straight into the liberation line
  (*"every print is paid in a freed droid"*). Killing them is faster and safer.
- **Choice (heavy, the betrayal; Q3).** Once the cores are on your map, an **Imperial salvage
  broker** (or a Hutt fence, per Q3) makes contact and offers to buy them. Accept, and the cores
  leave by shuttle. That is a separate `End` (outcome `Success` for *this* quest, with silver and
  Empire/Hutt goodwill). The parent catches it and **ends the chain**: Enclaves and Hive both
  `ensureHostile`, and the *"Nothing they freed comes back"* text fires.
- **Failure.** A core is destroyed (`cores.Destroyed`), or the timer expires (12 days) → Fail. The
  parent re-offers beat 3 once. A second failure ends the chain with outcome `Unknown`, so there is
  no reputation hit beyond what the beats already cost.
- **Reward / unlock.** Cores delivered to the chosen site, +10 to both factions → beat 4.

### 2.4 Beat 4 — "The Tithe and the Hands"

The Hive's gap is *"resources and capacity"* (the owner's words), so this beat is that gap,
paid by the player.

- **Ask, part 1: the tithe.** Material, and large, scaled to wealth. Proposed basket at 1× tithe
  scale: plasteel ×300, components ×40, steel ×800, uranium ×60.
  - Sites A, C, D: delivered by caravan as a **sequence of four `TradeRequest`s** to the site's
    settlement. Stock nodes allow one ThingDef per request, so the sequence is the workaround, or
    one small custom multi-item part (§3.3).
  - Site B: a **monument-style blueprint** at your colony (`QuestNode_GenerateMonumentMarker`
    pattern, Royalty, all DLCs assumed). You build the line's shell, and `.MonumentCompleted` is
    the success signal.
- **Ask, part 2: the hands.** Lend one colonist with Crafting ≥ 8 to the line for 10 days
  (`QuestNode_LendColonistsToFaction` via `Util_TransportShip_Pickup`, the vanilla PawnLend
  pattern). Organic hands the Hive cannot spare, beside droid hands that have never built. The two
  peoples learn to work one line *together*, which is the dramatic heart of the alliance.
- **Failure.** The lent colonist dies → Fail with −10 to both factions, and the parent re-offers
  beat 4. The deadline expires (20 days) → Fail and re-offer once.
- **Reward / unlock.** The colonist returns with a Crafting XP gift. **The line is assembled** →
  beat 5 fires on a 2–4 day delay.

### 2.5 Beat 5 — "First Light" (the climax)

- **Fiction.** The line's first run lights the sky. The Empire, which enslaved Geonosians to build
  the Death Star, *notices*. This is the Alliance arc's *"until the Empire catches wind"* moment,
  happening early and on a small scale.
- **Ask.** Hold the line through its first run: 2 days of production while an Imperial strike
  (stormtroopers plus attack droids, the Empire's ruling-2 loadout) arrives.
  - Site B: a raid on your home map (`Util_Raid`).
  - Sites A, C, D: a defence site the player caravans or shuttles to, where Enclave and Hive
    defenders fight alongside you (allied pawns via the site's faction).
  - Ends on `AllEnemiesDefeated` *and* the production `Delay` completing.
- **Failure.** The line's core building (`RUT_FoundryLineCore`, §4) is destroyed → Fail. The
  chain's goodwill gains so far **stand**. The epilogue does not fire. The parent can re-offer
  beats 4–5 (the rebuild) once, after 30 days.
- **Reward.** The epic parent completes (§2.6).

### 2.6 Epilogue — "The Unbolting of the Line" (parent success)

- **The Enclave rite.** The first frame off the line is carried to the Rust Cathedral and fitted
  with a salvaged head. That is the Unbolting rite reflavoured (`faction_roster_v2.md` §5,
  Rituals). The letter closes the clock the item asked for: *"Forty-one fell. Today one stood
  up."*
- **Reputation.** +40 Enclave goodwill (which reaches Ally from a typical ~60 total), plus the
  `RUT_UnfinishedLineCompleted` HistoryEvent shown in the faction tab. The Hive gets +20, and its
  Meckgin is satisfied: **the queen's unfinished work is, for once, being finished**.
- **Unlock.** The **Enclave droid-construction branch opens to the player**, either by goodwill or
  by techprints sold at Ally (wiring per `TECHPRINT_FACTION_GATING_1`). *"What you build with their
  teaching is born free"* applies, per §4.3.
- **The gods** (event hooks; wiring via `NINEFOLD_MISSING_EVENT_HOOKS_1`): Ohm surges, Rekko
  mourns (*"new hands, not second ones"*), and Ozzik's pride meter takes a step. No act is clean.

**What each choice is acknowledged by later:** beat 1's parts choice shows in beat 2's letter text.
The beat 2 site choice decides where beats 3–5 happen, who owns the line, and the goodwill split.
The beat 3 capture count shows in the epilogue text and goodwill. Betrayal ends the chain and
recolours both factions.

---

## 3. Mapping to quest defs and custom nodes

### 3.1 Def inventory (proposed names, `RUT_` tier since it is campaign content)

| def | kind | route |
|---|---|---|
| `RUT_UnfinishedLine` | epic parent `QuestScriptDef`, `isRootSpecial true`, weight 0, `QuestNode_QuestUnique tag UnfinishedLine` | `IncidentDef RUT_UnfinishedLine_Offer` (category GiveQuest, custom worker for the gates) |
| `RUT_UnfinishedLine_1_Count` … `_5_FirstLight` | children, `epicParent RUT_UnfinishedLine`, weight 0, `sendAvailableLetter true` | generated by the parent's sequential subquest part |
| `RUT_UnfinishedLine_2_Envoy` variants | one def. **The site choice uses `QuestPart_Choice`** with four reward-less choices whose chosen signal writes the site var | the stock reward-choice UI. ⚠️ Whether a `QuestPart_Choice` with no `Reward` items renders cleanly is UNMEASURED. The fallback is a dialog-letter with options (custom `ChoiceLetter`), which is small C#. |
| `RUT_UnfinishedLine_Betrayal` | HistoryEventDef plus the beat 3 betrayal `End` | n/a |
| HistoryEventDefs | `RUT_UnfinishedLineCompleted`, `RUT_UnfinishedLineBetrayed`, `RUT_EnvoyHarmed`, `RUT_LineCoreLost` | goodwill reasons |
| `RUT_FoundryPatternCore` | ThingDef (quest item, unminifiable, a value the player can feel) | beat 3 |
| `RUT_SilicaxFoundryRuin` | SitePartDef, plus a map gen (reuses `RUT_FoundrySalvageCache` / `RUT_FoundryTowerEntrance` art where it fits; they exist in `UtinniPatches/Defs/ThingDefs_Buildings/`) | beat 3, and the site A line |

### 3.2 Firing route

**Route 2 (a dedicated incident).** `RUT_UnfinishedLine` sets `isRootSpecial` and
`rootSelectionWeight 0`. That is mandatory, because an `IncidentDef` with `questScriptDef` and a
non-zero weight is a hard ConfigError (`IncidentDef.cs:235`). A custom
`IncidentWorker_RUT_UnfinishedLine` checks the four gates in `CanFireNowSub`. The vanilla GetFaction
cannot filter on goodwill, so the gate must live in C#. Also: `minRefireDays` 9999 on the incident,
and a **dev-mode debug action** "Offer The Unfinished Line" for verification. Never gate a test on
the storyteller.

### 3.3 Custom C# (small, and each piece justified)

| class | why vanilla can't | size |
|---|---|---|
| `QuestNode_RUT_Root_UnfinishedLine` + `QuestPart_RUT_SequentialSubquests : QuestPart_SubquestGenerator` | vanilla subclasses pick a random child; we need **ordered** beats, a per-beat retry count, and passing the site var to later children through `InitSlate()` | ~150 LOC |
| `QuestPart_RUT_BrokeredTruce` | holds the Hive at Neutral (goodwill floor 0) while active; reverts on chain Fail or Betrayal with `ensureHostile`. Nothing vanilla offers a *temporary* relation | ~60 LOC. Q2 may delete it. |
| `IncidentWorker_RUT_UnfinishedLine` | the goodwill/research/settlement gates | ~40 LOC |
| `QuestNode_RUT_MultiTradeRequest` (optional) | one delivery with four ThingDefs, instead of four chained `TradeRequest`s | ~80 LOC; skip if the chained version reads acceptably |
| `QuestPart_RUT_EnvoyWatchesIdle` (optional) | Meckgin idle-penalty tick | ~50 LOC, behind a setting |

Everything else is stock XML: `Util_GenerateSite`, `Util_Raid`, `Util_TransportShip_Pickup`,
`QuestNode_LendColonistsToFaction`, `QuestNode_ExtraFaction`, `QuestNode_ChangeFactionGoodwill`,
`QuestNode_RequirementsToAcceptResearch`, `QuestNode_Delay isQuestTimeout`,
`QuestNode_GenerateMonumentMarker`, and `QuestNode_End` with `goodwillChange*`. Beat 1 reuses the
shipped `QuestNode_DroidRepairJob` with the faction pinned. Per skill §9, each child keeps the
`QuestNode_Sequence` wrapper, so the end/fail/timeout branches stay editable without a rebuild.

### 3.4 Signal plan (names must agree, so they are listed here once)

Parent listens for: `Child.Succeeded` / `Child.Failed`, routed by the part's own `outSignals`.
`BetrayalAccepted` → parent `End Fail` with both goodwill hits. `LineCoreLost` → parent marks beat
5 for retry. The children's own signals are `cores.Destroyed`, `lentPawns.Destroyed`,
`envoy.Destroyed`, `envoy.Arrested`, `site.MapRemoved`, the monument's `.MonumentCompleted`, and
`raid.AllEnemiesDefeated`. **Suffixes only from the attested 75. Use `.Destroyed`, never
`.Killed`** (skill §6).

---

## 4. Mass production once unlocked, and how it stays balanced

### 4.1 What "mass production" means here (recommended reading of both rulings)

The 2026-09-26 ruling says the Enclaves *need* production. The 2026-09-06 head-gate says nobody on
the planet can make a mind. **Both hold if the line makes bodies.** The Enclaves' tragedy is
precisely that **heads survive and bodies do not**: parts always survive state 4, and state 5
leaves a few (`08_droids.md`). Every fallen Enclave droid whose head was recovered is a person
waiting for a body, and nobody has been able to make them one. **The line ends that.** It turns
the liberation economy (recovered heads and freed droids) into Enclave population growth. Nothing
breaks the gate.

### 4.2 In the world (all sites)

- **`WorldComponent_RUT_EnclaveFoundry`.** While the line stands, Enclave settlements regain
  defenders over time, and Enclave trader stock adds **Foundry-grade frames and part sets**: better
  than Primitive and worse than donor, never heads. It also tracks a **"heads delivered"** ledger:
  every droid head or freed droid the player hands over raises the Enclaves' growth rate and pays
  goodwill.
- **Volunteers.** A recurring, capped quest (`RUT_LineVolunteer`, about one per 20–30 days at
  Ally) brings a **free Enclave droid who chooses to join** the clan. That is a re-bodied head, never
  bolted, using `QuestNode_PawnsArrive joinPlayer`. **This is how "mass-produced" droids reach the
  player without the player printing minds.** Bolting or wiping one fires the
  `ENCLAVE_REMEMBERING_QUEST_1`-shaped penalty: goodwill collapse, and the volunteers stop.
- **The Hive.** Its company-era droids get replacement bodies, so its raids keep their 35–55 %
  droid share *legitimately*, which resolves contradiction 1 in §1.5. With site D chosen, Hive
  droid share rises further and the Empire's attention on the Hive (the Alliance arc doom)
  accelerates.

### 4.3 At the player's colony (site B, or as the Ally reward; Q1)

- **`RUT_FoundryLineCore`**: a large building (about 5×3) that runs batch bills for **frames and part
  sets** at a work-efficiency bonus over the harness's parts recipes. It needs power, plus **one
  organic Crafting pawn and one droid pawn working it together** (a two-worker job, or a simple
  "requires a droid present in the room" check). The theme is the alliance made physical.
- **It never produces heads or pawns.** Assembly stays at `RSW_DW_ReassemblyHarness`. Axis 18b's
  *"whole droids are not manufacturable"* stays literally true: the line makes inventory, and a
  person still does the assembly.

### 4.4 Balance: four brakes, three of them free

1. **The head-gate (hard).** Output is capped by heads, which come only from salvage, Trade Moot
   stock, liberation and quests. A thousand frames make zero droids.
2. **Empire heat (soft).** Each batch run adds to a line-heat counter. That raises the weight of an
   Imperial "Foundry strike" incident against wherever the line stands. Beat 5 is the first such
   strike; later ones follow the same counter. This is the Alliance arc's doom, made playable.
3. **The gods (soft, already designed).** Running the line feeds Ozzik's pride meter and grieves
   Rekko (*"restore ≠ transcend"*). Oomo objects to droids in egg chambers. Ohm is pleased. This is
   the existing anti-exponential pillar, so no new resource cap is needed.
4. **The Enclaves' conditions (social).** Line-built droids are *"born free"*. Bolting one
   collapses Enclave goodwill and shuts off the volunteers, the stock and the construction prints.
   *"The shop is the relationship."*

---

## 5. Mod Settings

One settings page (the house standard: on/off per feature, defaults = shipped behaviour,
all-off degrades gracefully).

| setting | default | notes |
|---|---|---|
| Enable The Unfinished Line chain | on | off: the incident never fires; nothing else changes |
| Offer gate: minimum Enclave goodwill | 20 | 0–75 |
| Earliest day | 30 | |
| Tithe scale | 1.0× | 0.25–3× on the beat 4 basket |
| Brokered truce with the Hive | on | off: Hive beats route through Enclave proxies only (Q2's option C) |
| Allow selling the pattern cores (betrayal) | on | Q3 |
| Hive envoy watches for idleness | on | the Meckgin tick |
| The line runs in the world (Enclave regrowth, stock) | on | off: reputation and fiction only (Q1's option C) |
| Player-buildable Foundry Line | per Q1 | |
| Volunteer rate | 1 per 25 days at Ally | 0 = no volunteers |
| Empire Foundry strikes from line heat | on | **affects the world**: labelled as such |
| Dev: offer the chain now / jump to beat N | dev-mode only | verification without the storyteller |

---

## 6. Build plan (FOUNDRY)

Sized for one agent per packet. It ships with a functional script from day one
(`debug_process.md` §2). It also depends on the Enclave kinds being re-pointed to Droidworks (C1/C2), on the wild
droid kinds (E4), and on the Empire attack-droid loadouts. **Check those items' states before
filing.**

| # | packet | contents | size | depends on |
|---|---|---|---|---|
| P0 | **Propagation** (BENCH, after ruling) | fix the three contradictions in §1.5; mark `TECHPRINT_FACTION_GATING_1` Q7 superseded; update `faction_tech_alignment.md` §2.5/§2.8 | S | owner ruling |
| P1 | **Chain spine (C#)** | `QuestPart_RUT_SequentialSubquests`, root node, incident worker, truce part, dev actions, selftest | M | — |
| P2 | **Beats 1–2 (XML)** | parent and two children, HistoryEventDefs, rule packs; reuse `QuestNode_DroidRepairJob`; `validate_quest.py` clean | M | P1 |
| P3 | **Beat 3 content** | `RUT_FoundryPatternCore`, `RUT_SilicaxFoundryRuin` site part and map gen, betrayal End | M | P1, wild-droid kinds |
| P4 | **Beats 4–5 (XML)** | chained TradeRequests or `QuestNode_RUT_MultiTradeRequest`, PawnLend, monument variant, Imperial strike | M | P2, P3 |
| P5 | **Line in the world** | `WorldComponent_RUT_EnclaveFoundry`, stock-generator patch, volunteer quest, heat counter + strike incident | M | P4 |
| P6 | **Player line** (if Q1 = B) | `RUT_FoundryLineCore`, batch recipes for frames/part sets, two-worker gate | M | P5, Droidworks parts |
| P7 | **Settings + functional script** | settings page; a modcheck walk that drives each beat via the dev actions on a minimal list and asserts the signal arrives | S–M | P1–P5 |

Verification is **offline first**: the validator plus selftests. Then one minimal-list load round
uses the dev actions (jump to beat N) to watch each `End` fire. No storyteller waits.

---

## 7. Questions for the owner

**Ruled 2026-10-03 (owner, typed):** *"Either it must be somehow bartered from the Hive (unlikely) or
stolen from the Hive by the Jawa (likely)."* The Enclaves never hold the secret; it is latent with the
Hive. Theft from the Hive is the likely path, barter the unlikely one, and the sell-out fork
(Q3-A, selling the pattern cores in beat 3) stands as ruled in the chain. Questions below remain open.

**Q1. When the chain is done, what actually changes?**
- **A (recommended). The Enclaves get a working line, and you get its fruits.** Their settlements
  regrow, their traders sell good droid frames and parts, and free droids sometimes volunteer to
  join you. You still need a salvaged head for every droid you build. *Trade-off:* moderate build
  work, and the world visibly changes.
- **B. All of A, plus your own Foundry Line building** that turns out frames and parts in bulk.
  *Trade-off:* the most satisfying payoff, but it bends "we do not breed new hands" and needs the
  Empire-heat and god pressure to keep it honest.
- **C. Reputation and story only.** A big goodwill jump and a great epilogue, and nothing runs.
  *Trade-off:* cheapest, but the Enclaves' "every loss is permanent" clock never actually stops.

**Q2. The Hive starts hostile to you. How do you deal with them during the chain?**
- **A (recommended). The Enclaves broker a truce.** The Hive is held neutral while the chain runs,
  and it snaps back to hostile if you betray them or harm their envoy. *Trade-off:* a little custom
  code, and the chain reads cleanly.
- **B. Earn it the slow way.** Each beat raises Hive goodwill until they stop being hostile around
  beat 3. *Trade-off:* no special code, but it takes +100 goodwill to get there, and Hive raids keep
  hitting you mid-chain.
- **C. Never deal with them directly.** Everything goes through Enclave go-betweens. *Trade-off:*
  simplest, but you lose the envoy-at-your-colony scene, which is the best one.

**Q3. Can the player sell out?**
- **A (recommended). Yes: sell the pattern cores to the Empire** (or a Hutt fence) in beat 3.
  You get a big payday, and both the Hive and the Enclaves turn on you for good. *Trade-off:* it
  gives the chain real weight, and it fits Mob'Unloo's *"being caught is the sin"*.
- **B. Yes, and also keep them yourself.** Build a line with no partners, while both factions turn
  hostile. *Trade-off:* the most "Jawa" option, and the hardest to balance.
- **C. No betrayal path.** *Trade-off:* simpler, but the chain has no moral fork.

**Q4. How does this relate to the existing Geonosian Alliance arc** (where the Hive trades you a
fortified base for ship tech until the Empire wipes them out)?
- **A (recommended). Keep them separate but linked.** This chain's final battle is the *first* time
  the Empire notices the Hive, and running the line raises the odds of the Alliance arc's
  destruction later. *Trade-off:* two stories that feed each other.
- **B. Merge them into one long arc.** The droid line and the fortified base are the same deal.
  *Trade-off:* tighter, but longer and harder to build in pieces.
- **C. No Empire involvement here.** *Trade-off:* the finale loses its antagonist and needs a new one.
