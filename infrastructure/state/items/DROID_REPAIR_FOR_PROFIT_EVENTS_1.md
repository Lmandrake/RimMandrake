## spec
Thin when filed — no spec/verify/criteria in the queue entry itself, but fully
specced as packet C5 of `design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md`
§5 (inputs: owner ruling 2, the `rimworld-quests` skill, B4b — closed; outputs:
"recurring incident/quest: a friendly arrives with a broken/under-spec droid,
pays for repair/upgrade; options to fit inferior parts, keep the good ones, or
'lose' a problem droid — reputation effects"; verify: "quest fires, completes,
pays; validator clean"; after: B4b, C1, both closed). Built directly from that
packet, FOUNDRY, 2026-09-08.

Owner ruling 2, 2026-09-06, the load-bearing clause: *"there should be regular
events where various local friendlies come to have you repair or upgrade their
droids for profit... it's just what everyone knows Jawa are supposed to do. And
there should be real opportunities to use superior or inferior parts, get rid of
problematic droids or parts, and otherwise be... Jawa."*

**Tier: RUT**, per §7 contradiction note 4 — the customer layer is "still a pack
on top (C5, RUT tier)", and Droidworks stays pure platform. Nothing in this
packet was added to the Droidworks mod.

## Built
A new RimUtinni sub-mod, `src/RimUtinni/DroidRepairJobs/`, packageId
`mandrake.rut.droidrepairjobs`, namespace `RimMandrake.Utinni.DroidRepairJobs`,
`RUT_` prefixes throughout (CLAUDE.md's three-tier grammar).

### The quest — `RUT_DroidRepairJob` (`Defs/QuestScriptDefs/Quest_DroidRepairJob.xml`)
Structure is `RM_Stranded`'s (`src/RimMandrake/StrandedQuest`), which is the
house shape for "a pawn is left in your care for N days and you may keep them".

- **Trigger: the natural random pool** — `rootSelectionWeight 1.1` (in-family;
  shipped weights run 0.15–2.0), `rootMinProgressScore 4`, `expireDaysRange 2~4`.
  That is what makes it the *recurring* event ruling 2 asked for, with no
  incident of its own needed.
- **Frequency cap: `minRefireDays 15`** — §6's anti-exponential guardrail,
  enforced on the def.
- **Customer: any nearby friendly.** `QuestNode_GetNearbySettlement`
  (`maxTileDistance 36`) yields only `settlement.Visitable` settlements, i.e.
  non-hostile ones — verified by reading `QuestNode_GetNearbySettlement.cs`. No
  faction is hard-coded or excluded, so every faction C1 wired droids into can
  send work — Homestead Defense League (`OutlanderCivil`), the Hutt Cartel
  (`Jawa_HuttCartel`), the Junkers (`Jawa_Junkers`), the Jawa Trade Moot
  (`Jawa_IndigenousTribes`), the Empire while non-hostile — plus every other
  neutral/allied settlement on the planet. That is the correct shape for a shop:
  customers are whoever is nearby and not shooting at you.
- **The droid** arrives as a **quest lodger in the player's own faction**
  (`QuestNode_PawnsArrive joinPlayer true` + `QuestNode_ExtraFaction
  factionType HomeFaction`, the vanilla Royalty hospitality shape). One of four
  civilian kinds via `QuestNode_RandomNode`:
  `RSW_DW_KotORDroidColonist_{T3UD,R8009UD,GE3LD}` and
  `RSW_DW_KotORDroidGood_3C`.
- **Job window** 5–9 days, shown as the quest timer (`QuestNode_Delay`
  `isQuestTimeout`), firing `PickupDue`.

### The resolution mechanism is B4b's, not a new one
🔴 **The load-bearing discovery of this packet.**
`ITab_Pawn_Health.ShouldAllowOperations()` (read in Assembly-CSharp) returns
**false** for a friendly, non-downed, non-player-faction pawn — so a droid that
merely *visited* could never be operated on and the whole design would have been
dead on arrival, silently, with the operations tab simply absent. Making the
droid a **player-faction quest lodger** is what satisfies that gate
(`pawn.Faction == Faction.OfPlayer` is the first `true` branch).
`RecipeDef.allowedForQuestLodgers` defaults to `true`, so B4a's install recipes
need no change.

The player therefore repairs it with the **already-built** system: the health
tab's `RSW_DW_Install{LegActuator,ManipulatorArm,Sensor,Motivator,Servo}`
recipes (`Recipe_InstallDroidPartAtBench`, which requires an
`RSW_DW_RepairBench` within 15 tiles), consuming the player's **own**
`RSW_DW_Part_*` stock. Nothing here duplicates a Droidworks mechanism.

### The three choices, and how each resolves
`Recipe_InstallDroidPart` already grades a fitted part by its `CompQuality` and
grants one of an Inferior / Standard / Superior hediff per slot, replacing any
earlier tier. So *"which quality of part did the Jawa fit"* is already recorded
on the pawn. `QuestPart_DroidRepairJobOutcome` only reads it, at `PickupDue`,
**best tier present wins**:

| what the player did | tier | payment | goodwill | quest outcome |
|---|---|---|---|---|
| fitted an Excellent/Masterwork/Legendary part | Fine | `payFine` | **+8** `RUT_DroidJobFineWork` | Success |
| fitted a Normal/Good part | Honest | `payHonest` | **+4** `RUT_DroidJobHonestWork` | Success |
| fitted an Awful/Poor part, kept the good one | Shoddy | `payShoddy` | **−3** `RUT_DroidJobShoddyWork` | Success |
| never opened the panel | Neglected | 0 | **−8** `RUT_DroidJobNeglected` | Fail |
| arrested it — bolted it, it is yours | (signal `lodgers.Arrested`) | 0 | **−18** `RUT_DroidJobDroidKept` | Fail |
| it died / was stripped | (signal `lodgers.Destroyed`) | 0 | **−12** `RUT_DroidJobDroidKept` | Fail |

Goodwill is applied by `QuestNode_ChangeFactionGoodwill`, whose `QuestPart_
FactionGoodwillChange` is vanilla's own `TryAffectGoodwillWith` path — the same
node `RUT_Reclamation` (VaultDungeons) already uses in this repo. It takes
`<faction>` directly rather than `QuestNode_End`'s `goodwillChangeFactionOf`,
which needs a `Thing` and would silently apply **nothing** if the faction had no
leader.

### Payment formula (FOUNDRY's own numbers, §6's guardrail)
Computed at generation time in `QuestNode_DroidRepairJob`, written to the slate
as `payFine` / `payHonest` / `payShoddy` so the quest description can quote all
three before the player commits:

```
base          = 320 silver                     (XML <basePayment>)
wealthFactor  = 0.7 neolithic/animal | 0.8 medieval | 1.0 industrial
                | 1.3 spacer | 1.5 ultra+       (faction.def.techLevel)
repFactor     = 0.75 + clamp(faction.PlayerGoodwill, 0, 100)/100 * 0.5   -> 0.75..1.25
payHonest     = round(base * wealthFactor * repFactor)
payFine       = round(payHonest_unrounded * 1.6)
payShoddy     = round(payHonest_unrounded * 0.4)
```
Range: **67 silver** (shoddy job for a poor, barely-tolerant clan) to **960**
(fine work for a rich ally). "Wealth" is proxied by `techLevel` because RimWorld
factions carry no wealth stat — recorded as an assumption below.

Payment is delivered by drop pod at `DropCellFinder.TradeDropSpot`, credited to
the customer faction.

### The one custom verb (`Source/`, `RimMandrake.Utinni.DroidRepairJobs.dll`)
Everything a stock node can already do stays in XML — skill §9's hybrid shape.

- **`QuestNode_DroidRepairJob`** — at generation: adds `RUT_DroidJobFault` to the
  droid (this is why the customer is here), computes and stores the three
  payments, and emits the QuestPart. The three Inferior/Standard/Superior hediff
  lists are passed **from XML**, not resolved through a `DefOf`: the def loader
  then cross-checks all 15 names at load, and the assembly carries no
  compile-time dependency on Droidworks.
- **`QuestPart_DroidRepairJobOutcome`** — at `PickupDue`: grades, removes the
  fault if any part was fitted, drops the silver, and fires one of
  `WorkFine` / `WorkHonest` / `WorkShoddy` / `WorkNeglected`. Every letter,
  goodwill change and `QuestNode_End` hangs off those four signals in XML, so
  the lifecycle stays editable without a rebuild.

### Other defs
- `RUT_DroidJobFault` (HediffDef) — the fault the droid arrives with: Moving
  −0.45, Manipulation −0.30, WorkSpeedGlobal −0.35. A droid the player **keeps**
  keeps its fault until they fix it themselves.
- Five HistoryEventDefs, the goodwill reasons above.
🔴 **No IncidentDef ships.** A first draft included
`RUT_GiveQuest_DroidRepairJob` (`ParentName GiveQuestBase`, `baseChance 0`) as a
deterministic test trigger. The live load refused it:

```
Config error in RUT_GiveQuest_DroidRepairJob: quest is run from both incident and random quest.
```

`IncidentDef.ConfigErrors()` fires on `questScriptDef != null &&
questScriptDef.rootSelectionWeight != 0f` and **never looks at `baseChance`** —
so the two firing routes are mutually exclusive no matter how the incident is
weighted, and the "baseChance 0 makes it inert" assumption was simply wrong.
The def was deleted; the natural pool is the only route, which is what ruling 2
asked for anyway. Dev mode's *Debug actions → Quests → Generate quest* and a
`jawa/fire_quest` bridge call both take a QuestScriptDef directly, so nothing was
lost. **This is the one thing the offline validators could not see** and the sole
reason the cold load earned its ~17 minutes.

## verify

**Offline — clean.**

- `xml.etree` parses all 5 created XML files.
- `dotnet build -c Release`: **0 errors, 0 warnings**, first try.
- **`validate_quest.py`: 0 errors, 0 warnings.** Two INFOs, both deliberate and
  documented in the def's header: `foreign-node` (the node is this mod's own —
  namespace confirmed by reading the built assembly's metadata with a copy of
  `src/RimMandrake/Utils/ilprobe/meta_core.py`, which lists
  `('QuestNode_DroidRepairJob', 'RimMandrake.Utinni.DroidRepairJobs')`, not by
  grep) and `space-acceptance` (`everAcceptableInSpace` left unset on purpose —
  the droid walks in, so Accept *should* be grey on a space map).
- ⚠️ The validator's first pass raised three `unresolved-symbol` warnings on
  `[payFine_money]`/`[payHonest_money]`/`[payShoddy_money]` — it cannot see
  inside a C# node, so it could not know the node stores them. Fixed **honestly
  rather than by suppression**: three stock `QuestNode_Set` nodes now write
  unscaled defaults (320/512/128) before the custom node overwrites them. That
  is also a real safety net — `QuestNode.Run()` *swallows* an exception and only
  logs it, and one unresolvable `[symbol]` blanks the **whole** description
  rather than degrading, so a failure in the custom node now costs accurate
  numbers instead of the entire quest text.
- **`validate_patch.py`: 0 errors, 0 warnings** on all 4 def files, against the
  live 600-mod load set (`--defs` Data + Mods + workshop) and the
  `2026-09-08T22-04-59Z` capture (69,797 defNames, 446 types).
- **Every referenced defName MEASURED present** on that same capture (`measure
  get`, after `measure build`): 4 PawnKindDefs, 15 `RSW_DW_PartEffect_*`
  HediffDefs, `Silver`, `RSW_DW_RepairBench`, `RSW_DW_InstallLegActuator` — **22
  of 22**. `GiveQuestBase` is abstract and so is absent from any dump by
  construction; its resolution was checked by `validate_patch.py`'s ParentName
  pass against the load set instead.
- **Deployed** (`deploy_custom_mods.py --mod DroidRepairJobs --apply`): 6 files,
  all additions, nothing overwritten, `-> VERIFIED in sync`.
- **`ModsConfig.xml`**: `mandrake.rut.droidrepairjobs` inserted directly after
  `mandrake.rsw.droidworks` (its `loadAfter`), 600 → **601** active. Snapshot
  taken first, per CHARTER's expensive list:
  `infrastructure/state/modlists/ModsConfig.PRESWAP.20260908_151432_before_C5_droidrepairjobs.xml`.

**Live — PARTIAL. Half the verify line is met; the other half is owed.**

Full 601-mod cold load, FOUNDRY, 2026-09-08 15:16→15:33 local (~17 min). The
game was at the **main menu with no game loaded** when the reboot was called
(`rimworld/list_colonists` → "No game is currently loaded"), so nothing the owner
was playing was killed — the one thing `GAME_STATE_WORKFLOW.md` §"A REBOOT IS
YOURS TO CALL" does not unlock. Bridge was FREE and taken for the reboot.

✅ **What the load proved:**
- **The mod is active**: `mandrake.rut.droidrepairjobs` appears in the log's own
  active-mod dump (Player.log:12984), after `mandrake.rsw.droidworks`.
- **Zero cross-reference errors on the whole load.** That is the proof that all
  15 `RSW_DW_PartEffect_*` names in the three tier lists, the four PawnKindDefs
  and `RUT_DroidJobFault` resolved — a bad name there would have been a
  `Could not resolve cross-reference` line.
- **Zero type-load errors, and the custom node's `Class=` resolved.** A `Class`
  the game cannot resolve throws away the **whole parent def** silently; the
  QuestScriptDef survived, so `RimMandrake.Utinni.DroidRepairJobs.
  QuestNode_DroidRepairJob` was found in the deployed assembly.
- **Exactly ONE new `Config error in` line versus the pre-restart baseline (24
  vs 23)** — the IncidentDef one above, now deleted. Nothing on the
  QuestScriptDef, the HediffDef or the five HistoryEventDefs.

✅ **The IncidentDef fix re-verified on a SECOND full cold load** (15:44→16:01):
`Config error in` count back to **23**, i.e. exactly the pre-restart baseline;
`grep -i "DroidRepairJob\|RUT_DroidJob"` over the whole Player.log returns
**nothing at all**; cross-reference errors **0**.

❌ **What is still owed — "quest fires, completes, pays".** `jawa/fire_quest`
needs a map ("No current map. Load a game first."), and **RimWorld died during
quicktest map generation on BOTH attempts**, one per cold load. Process gone,
no exception logged, and the last four log lines are **byte-identical** between
the two crashes (Ninefold research-completion messages during scenario setup,
after Geological Landforms / Map Designer / ore steps) — a deterministic crash in
quicktest map gen on this 601-mod list, not a flake.

🔴 **Not attributable to this packet**, and worth knowing for every future
FOUNDRY live test: this mod ships no map-gen code, no Harmony patch and no comp;
its entire footprint in the log across three loads was the one config error above
(now gone). `rimworld/start_debug_game` takes **no parameters**, so the map size
(250) cannot be reduced to dodge it. ⇒ **A quicktest is not currently available
on the full list; live droid work must use the minimal Droidworks mod list.**
Two attempts were spent, which is the budget this packet was given.

⚠️ **This was already a known trap and I walked into it anyway.** The last line
of `infrastructure/state/LESSONS_INBOX.md` before this packet reads: *"FOUNDRY
2026-09-08: `rimworld/start_debug_game_ready` crashed the game outright (not just
hung) on the owner's full ~599-mod list… Never run it on the full list; swap to
the minimal list first."* Reading LESSONS_INBOX before spending a load round
would have saved both attempts and ~34 minutes. The correct move was: cold-load
on the **minimal Droidworks list**, quicktest there, then restore. Recorded here
rather than as a new lesson line because the lesson already exists — what was
missing was reading it.

⚠️ Note that the **completion** leg would likely have stalled anyway: finishing
this quest requires a `Recipe_Surgery` bill actually being worked, and
`DROIDWORKS_LIVE_LOOP_PROOF_1` (A1), `DROIDWORKS_HEADS_BRAINS_SPIKES_1` (B3),
`DROIDWORKS_FINE_PARTS_1` (B4a) and `DROIDWORKS_SHOP_BENCHES_1` (B4b) have each
hit the same wall today — no bridge tool forces a `JobDriver_DoBill` to
completion, and colonists would not pick the job up across ~34,000 ticks.

**The precise run-sheet for whoever picks this up on the next load** (cheap on a
minimal Droidworks list, ~1 min, rather than the full 601):
1. `jawa/fire_quest` `RUT_DroidRepairJob` (or dev *Generate quest*).
2. Confirm the quest **description is not blank** — one unresolvable `[symbol]`
   blanks the whole thing, and `[payFine_money]`/`[payHonest_money]`/
   `[payShoddy_money]` come from the custom node. Blank ⇒ the node threw; look
   for `Exception running QuestNode_DroidRepairJob` in the log.
3. Confirm the three fee figures are **scaled**, not the 320/512/128 XML
   fallbacks — equal to the fallbacks means the node did not run.
4. `jawa/list_things` / pawn health: the droid carries `RUT_DroidJobFault`.
5. Fit an Excellent `RSW_DW_Part_Leg` via `RSW_DW_InstallLegActuator` near an
   `RSW_DW_RepairBench`; at pickup expect the `WorkFine` branch, a silver drop
   pod and **+8** goodwill.

## Assumptions recorded (Charter: "record what you assumed")

1. **"Lose the problem droid" (ruling 2's least-specified clause) is read as two
   things, both shipped.** (a) *Getting rid of problem PARTS* is the Shoddy
   outcome: fitting your worn salvage into someone else's droid, keeping the good
   part, and taking the smaller fee and the worse name. That is a genuinely
   profitable option, not a punishment, and it is the most literally Jawa thing
   in the packet. (b) *Getting rid of a problem DROID* is inverted — the
   customer's droid becomes yours. Arrest is the route the game actually offers
   on a quest lodger (`FloatMenuOptionProvider_Arrest.cs:55` explicitly permits
   arresting one), costing −18 goodwill and the whole fee, and buying a chassis
   worth far more. **What was NOT built:** handing the customer a *different*,
   junk droid in place of theirs. It is the better fiction, but there is no
   player-facing way to move a pawn into another faction, so it would have needed
   a new gizmo and a new UI — a mod, not a quest (skill §2 question 8).
2. **Faction "wealth" is proxied by `techLevel`.** RimWorld factions have no
   wealth stat. §6 asks payment to scale with "the customer's faction wealth and
   reputation"; reputation is exact (`PlayerGoodwill`), wealth is this proxy.
3. **The four droid kinds** are a FOUNDRY pick from the civilian/utility end of
   Droidworks' roster — the design doc names no kind. All four are C1-confirmed
   live.
4. **`base 320` silver, the ×1.6/×0.4 outcome multipliers, and the +8/+4/−3/−8/
   −18/−12 goodwill numbers are FOUNDRY's own.** The packet specifies none of
   them. 320 is roughly a good-quality prosthetic's worth of work.
5. **Grading takes the BEST tier present, across all five slots.** Fitting one
   excellent part and four awful ones grades Fine — not a cheat, because the
   recipe consumed a real excellent part out of the player's own stores, which is
   exactly the trade the packet asks the player to make.
6. **`lodgers.Recruited` is deliberately NOT wired.** With `joinPlayer true` the
   droid is already in the player's faction, so nothing can raise it; a branch on
   it would be dead XML. `.Arrested` and `.Destroyed` carry the keep-it case.
7. **`everAcceptableInSpace` left unset**, so Accept is grey on a space map. That
   is correct for an EdgeWalkIn arrival and is called out in the def's header so
   the next reader does not "fix" it.
