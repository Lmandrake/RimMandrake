# FLOOD_WITNESS_EVENT_1 — design draft: the witnessed flood

_Fable draft, 2026-09-09. PROPOSAL for an owner sitting — nothing here is built,
deployed, or ruled. Sources: `infrastructure/state/items/FLOOD_WITNESS_EVENT_1.md`;
`biomes/the_cracked_lands.md` §3/§4b/§9/§10b/§11/§12 (frozen — this design adds
detail, changes no ruling); `infrastructure/state/items/EXPLOSIVE_PLANT_GROWTH_1.md`;
`biomes/rosters/_fish_assignment_proposal.md` §1 row `the_cracked_lands` (the
no-truce canyon water). Quest machinery per the `rimworld-quests` skill._

**Every rule this document invents is marked 🄸 INVENTED.** Everything unmarked
traces to the frozen sheet or the item files.

---

## 1. The prose spec — what the player lives through

### The one-sentence reason (no reward named)

The flood is the Cracked Lands' whole story — death, then soil, then the bloom —
and it almost never happens while anyone is standing there; the plot puts the
colony on the ledge when it does.

### The fiction of the offer — RULED: a Moisture Farmer invitation (owner, 2026-09-10)

**A Moisture Farmer speaks.** The owner chose the warmer voice over the drafted
Jawa flood-news: the offer letter is an invitation from the Moisture Farmers,
seeding that relationship early. The substance is unchanged — the Contagion's
storm is building on the Dew Horn peaks, a named canyon is going to take the wall
within days, and whoever is on the refuge ledge when it passes gets first pick of
whatever the water tears open; the Farmers know because they read the sky for a
living, and they are inviting the clan to see it. The sheet's §12 salvage-strike
rhythm stays Jawa property — the Farmers bring the news, the clan brings the
crawlers. The timing is honest inside the fiction — the storm is *already
forming* when the letter arrives, which is why the plot, not weather RNG, owns
the clock.

### Beat by beat

**Beat 0 — the offer.** Letter (quest offer). Accept → a site appears on the
world map in the Cracked Lands: a slot canyon with (all sheet-sanctioned §8/§11
furniture) refuge ledges cut along the road, waymark cairns, water chimes seated
in the walls, a flood-marked ruin — the farm built one meter too low — and loose
salvage scattered on the canyon floor. 🄸 INVENTED: the floor salvage is the
deliberate temptation; everything valuable starts at the bottom and safety is at
the top. (Loose items and a pre-ruined ruin — no authored *structure* on the
floor; §6 ban 8 holds.)

**Beat 1 — arrival, the dry stillness.** The player's caravan or gravship
arrives. Nothing moves. The floor salvage is harvestable immediately; the ledges
are marked and empty. Most Cracked Lands visits are exactly this (sheet §10b) —
the event's job is to be the one visit that isn't.

**Beat 2 — the forewarning ladder**, armed the moment the site map generates,
in the sheet's fixed sensory order (§3/§4b/§9 — smell before sound, ground before
sky). 🄸 INVENTED: the intervals. Total lead time arrival→wall ≈ 1.5 in-game
days, so a player who came for the salvage has real hauling time to gamble with:

| T (from map gen) | beat | delivery |
|---|---|---|
| 0 | **the storm breaks on the peaks** — dry lightning flickers over the off-map Dew Horn | letter (neutral), ambient weather |
| +8 h | **wet clay on the wind** — the nose knows first | on-screen message |
| +1 d | **the flats begin to tick — the Sealed wake**; sleepers boil up out of the cracked pans | incident (spectacle), message |
| +1 d 6 h | **the water chimes ring** — tones rolling up through the stone, ahead of any sound of water | letter (THREAT tone): *"the chimes are ringing — climb NOW"* |
| +1 d 8 h | **THE WALL** — red-brown water down the canyon | the flood condition starts |

The chimes-to-wall gap of ~2 h is the escape pressure: enough for any pawn on
the floor to reach a ledge, not enough to finish loading the mule.

**Beat 3 — the wall.** The flood condition runs ~6 h 🄸 INVENTED: floor cells
flood (moving-water terrain, drowning/damage to anything standing there),
ledges and benches untouched. The floor salvage the player didn't take is swept.
The too-low ruin is torn open. The colony watches from the ledge — the sheet's
whole artistic theme (§9) compressed into one screen: the roar, the red-brown,
the stillness above it.

**Beat 4 — death, then soil.** The water recedes into the cracks and hides
(§3). Left behind: wet mud and fresh soil terrain on the floor, drowned Spender
carrion, crack-wax scattered on the pans, and — 🄸 INVENTED — the ruin's cache
broken open plus re-dealt salvage the wall carried in: the Jawa payoff, fresh
exactly as long as the mud is.

**Beat 5 — the bloom.** `EXPLOSIVE_PLANT_GROWTH_1`'s guaranteed showcase: the
soaked floor visibly GROWS on screen — the bloom crop, the Spender carpet, the
fliers wheeling in to feed (and, near the canyon water, dipping to fish — the
no-truce water of the fish proposal row: what they pull out has teeth). The
player harvests bloom crop and salvage for as long as they care to stay; the
quest is already won.

### Why it's worth playing rather than reading

The greed-versus-altitude gamble. Every beat of the ladder is a decision the
player makes with their hands: keep hauling or start climbing, and the game
never says which — the chimes do. Then the two faces land in order, on screen:
the wall that would have killed them, and the bloom that exists because of it.
A cutscene shows that; this makes the player *choose their moment to believe
the warnings*, which is the Farmer's craft (§9: "an experienced Farmer trusts
the ground before the chimes").

### The skill's ten questions, answered

1. Reason without reward: yes (above). 2. A decision with two defensible
answers: haul vs climb, continuously re-asked. 3. Later acknowledgement: the
post-flood letter names what was lost to the water vs carried up 🄸 INVENTED.
4. Failable and survivable: yes — leave early and it ends `Unknown` (retry,
§2 below); stay and lose floor goods, never the run. 5. Reward proportional:
the reward is diegetic (salvage + bloom), scaled by nerve. 6. Deadline real,
enforced, shown: the ladder is the deadline and every rung is shown.
7. One sitting: ~3 days on-site. 8. Existing mechanics only: the quest yes;
it *invokes* the flood engine and growth burst, which are separately-owed
items (§3 boundary below). 9. Ask/reward/deadline findable at a glance: offer
letter carries all three. 10. Firing route: taken, deliberately (§2).

---

## 2. The trigger design — how the plot guarantees one witnessed flood

### Offer route: a dedicated incident (skill route 2), never the random pool

`rootSelectionWeight 0` + `isRootSpecial true` on the QuestScriptDef; an
`IncidentDef` (`<category>GiveQuest</category>`,
`<workerClass>IncidentWorker_GiveQuest</workerClass>`,
`<questScriptDef>RUT_FloodWitness</questScriptDef>`) is the only way it fires.
**Why:** the owner's constraint is *timing rides the plot, never weather RNG* —
and the natural random pool is exactly storyteller RNG. A named incident is the
one deterministic offer route that doesn't need a framework dependency.

🄸 INVENTED — **the plot scheduler and the guarantee flag.** A small C#
`GameComponent` (campaign assembly, `RimMandrake.Utinni` namespace per the
naming scheme) fires the incident when the campaign beat arrives (Q4 asks the
owner which beat), and **re-fires it on a long delay until one instance of the
quest has ended `Success`** — checked against `Find.QuestManager`'s history for
this script, no new save state needed. That loop IS the guarantee of "at least
once": not one offer, but offers until one witnessing completes.

### What "in the canyons" means, detectably

🄸 INVENTED — **presence = the site map exists.** The quest runs on its own
generated site; a site map exists only while player pawns are on it, and the
engine raises `MapRemoved` when the last one leaves. So the whole detection
problem is structural, in vanilla signal vocabulary, with no polling and no C#:

- The forewarning ladder arms on **`site.MapGenerated`** (player arrived).
- "Witnessed" = the wall-arrives signal fires **while the map still exists** —
  i.e. `WallPassed` beats `map.MapRemoved` in a plain signal race.
- A pawn asleep in a tent still "witnesses"; good enough, and the alternative
  is a custom C# line-of-sight check nothing justifies.

🄸 INVENTED — **the witness canyon is one authored place.** The world is one
frozen hand-made map; the site spawns at a fixed, hand-picked Cracked Lands
world tile (chosen at authoring time from the Cracklands region), with a
hand-authored map layout — ledges, cairns, chimes, the too-low ruin — under the
same template machinery as `MOISTURE_FARM_TEMPLATES_1`. Full authorial control
of the survival geometry, at the price of travel distance (Q2 offers the owner
the floating-site alternative).

### Abort / retry rules 🄸 INVENTED

| the player… | quest outcome | then |
|---|---|---|
| never travels; site offer times out (~15 days) | `End Unknown` — no fault, no verdict | scheduler re-offers after a long beat (~1 quadrum) |
| arrives, then leaves before the wall (`map.MapRemoved` before `WallPassed`) | `End Unknown` + a letter: the canyon flooded behind them — smell of wet clay at their backs | scheduler re-offers; a NEW storm, a new letter — the fiction supports retries indefinitely |
| declines the offer outright | quest never created | scheduler re-offers |
| is on the map when the wall passes | `Success` armed; quest ends `Success` when they eventually leave (so the site — bloom, salvage — stays alive for the whole harvest) | flag set; scheduler stops forever |

Mid-chain abort is deliberately *cheap for the player and free of punishment*
— the punishment is missing the show, and the plot just re-arranges it.

### Later natural floods — settled here (the item hands this to the design)

🄸 INVENTED, proposed as the ruling to ratify:

1. **Before the witnessed flood: no natural floods on any player-occupied
   map.** The first wall the player ever sees is the scripted one — the beat
   is never spoiled by RNG delivering a lesser version first.
2. **After it: the flood becomes a standing rare incident** on player-occupied
   Cracked Lands maps (incident-driven with a long refire, not weather RNG —
   the same engine event the quest invokes), and it **always runs the full
   forewarning ladder**: chimes are physics, not quest script, so every future
   flood is survivable by attention. This is how the mechanic "recurs as a
   designed moment" (`EXPLOSIVE_PLANT_GROWTH_1`'s requirement) instead of
   being a one-off.
3. Natural floods are honest: floor structures and pawns that ignore the
   ladder take the consequences (§6 ban 8 exists because the floor is where
   things die). Lethality ceiling is Q1's second half.

---

## 3. The machinery map

### Ownership boundary — what this quest is and is not

The quest is **choreography only**: it creates the site, runs the signal
ladder, and *invokes* engine events that other items own. The flood itself
(rising water, drowning, soil deposition, flood-marked terrain — the biome
sheet's "Owed: the flood as an event (engine)"), the Sealed wake, and the
bloom burst (`EXPLOSIVE_PLANT_GROWTH_1`'s terminal moment) are built under
those items and merely *triggered* here. The quest ships last and rides them.

### Defs implied 🄸 INVENTED (names per `design/NAMING_SCHEME_PLAN.md`, campaign tier)

| def | type | owner item |
|---|---|---|
| `RUT_FloodWitness` | QuestScriptDef | this item |
| `RUT_GiveQuest_FloodWitness` | IncidentDef (GiveQuest) | this item |
| `RUT_WitnessCanyon` | SitePartDef + authored layout | this item + template machinery |
| `RUT_CanyonFlood` | GameConditionDef + worker | flood engine (biome sheet "Owed") |
| `RUT_SealedWake` | IncidentDef | flood engine |
| `RUT_BloomBurst` | IncidentDef | `EXPLOSIVE_PLANT_GROWTH_1` |
| `RUT_FloodWitnessed` | HistoryEventDef (success record) | this item |

### QuestScriptDef node sketch — vanilla vocabulary throughout

```
QuestScriptDef RUT_FloodWitness
  rootSelectionWeight 0 · isRootSpecial true · expireDaysRange ~15
  questNameRules / questDescriptionRules  (flood-news letter text)
  root = QuestNode_Sequence
    QuestNode_Set                 points, cosmetic slate strings
    (site tile is a constant — the authored canyon; no tile-picker node needed)
    Util_GenerateSite / QuestNode_GenerateSite   → storeAs: site  (RUT_WitnessCanyon part)
    QuestNode_SpawnWorldObjects   (site)
    QuestNode_WorldObjectTimeout  (site, ~15 d, isQuestTimeout,
                                   inSignalDisable: site.MapGenerated)
                                   → outSignal NeverCame
    QuestNode_End                 inSignal NeverCame · outcome Unknown

    -- the ladder: every rung chained off the previous rung's outSignal,
    -- ROOT-ARMED ON site.MapGenerated, never on accept --
    QuestNode_Letter              inSignal site.MapGenerated   (storm on the peaks)
    QuestNode_Delay 8h            inSignal site.MapGenerated → ClaySmell
    QuestNode_Message             inSignal ClaySmell           (wet clay on the wind)
    QuestNode_Delay …             inSignal ClaySmell → SealedWake
    QuestNode_CreateIncidents     inSignal SealedWake  (RUT_SealedWake, on $site map)
    QuestNode_Delay …             inSignal SealedWake → ChimesRing
    QuestNode_Letter (ThreatBig)  inSignal ChimesRing          ("climb NOW")
    QuestNode_Delay 2h            inSignal ChimesRing → WallArrives
    QuestNode_GameCondition       inSignal WallArrives (RUT_CanyonFlood, ~6h, $site map)
    QuestNode_Delay ~8h           inSignal WallArrives → FloodPassed
    QuestNode_CreateIncidents     inSignal FloodPassed (RUT_BloomBurst)
    QuestNode_Letter              inSignal FloodPassed         (death, then soil, then this)

    -- the witness race, resolved structurally --
    QuestNode_SignalActivable     inSignalEnable: FloodPassed
                                  inSignal: site.MapRemoved → outSignal WitnessedAndLeft
    QuestNode_End                 inSignal WitnessedAndLeft · outcome Success
                                  (successHistoryEvent RUT_FloodWitnessed)
    QuestNode_SignalActivable     inSignal: site.MapRemoved   (armed from start,
                                  inSignalDisable: FloodPassed) → outSignal LeftEarly
    QuestNode_End                 inSignal LeftEarly · outcome Unknown
```

Whichever `site.MapRemoved` listener is live wins the race — `SignalActivable`'s
enable/disable pair is the exact vanilla idiom (`Script_ChangeRoyalHeir`
precedent per the skill's corpus) for "the same signal means different things
in different phases."

Rewards: **no `QuestNode_GiveRewards`.** The payout is on the ground (salvage,
bloom, crack-wax) — a `GiveRewards` pod drop on top of it would cheapen the
diegetic reward and add an asker-faction dependency the fiction doesn't have.
🄸 INVENTED.

### Where custom C# is genuinely needed — and where it is not

| need | verdict |
|---|---|
| the quest tree itself | **XML, all vanilla nodes** — sequence, delays, letters, message, CreateIncidents, GameCondition, SignalActivable, WorldObjectTimeout, End. Nothing here needs a new verb. |
| detecting player presence / the witness condition | **no C#** — the map-exists signal race above |
| picking the site tile | **no C#** — fixed authored tile (if Q2 goes "floating site," a small tile-picker node becomes the one custom node) |
| the plot scheduler + fire-until-witnessed guarantee | **C#, small** — a GameComponent; no vanilla scheduler retries an incident until a quest succeeds |
| the flood condition, Sealed wake, bloom burst | **C#, but not this item's** — owned by the flood engine and `EXPLOSIVE_PLANT_GROWTH_1`; the skill's bar ("a new verb") is met there, not here |
| the authored canyon map layout | template/genstep work under the layout machinery, not quest C# |

### Tie into EXPLOSIVE_PLANT_GROWTH_1

The `FloodPassed → RUT_BloomBurst` edge is the contract: this quest guarantees
the growth mechanic one on-screen, on-purpose performance (the item names this
event as its showcase). The quest passes nothing but the map; intensity,
terminal moment, and harvest rules are entirely that item's. If the growth
item ships first, its incident def slots in; if this ships first, the node
stubs to a placeholder incident and the beat degrades to "the bloom" letter —
the quest is whole without it (the standing Oracle-law shape: text/menu
authority only, no LLM and no sibling mod load-bearing). No Oracle call
anywhere in this design.

---

## 4. Failure modes — the skill's traps, applied to THIS design

| trap | where this design would hit it | guard |
|---|---|---|
| **storeAs rename kills every inSignal** | `site` carries FOUR load-bearing signals (`MapGenerated` ×2 roles, `MapRemoved` ×2 listeners). Rename it and the quest offers, spawns a site, and never does anything else — silently. | validator; never rename `site` |
| **arming inversion** | the deadliest one here: a `QuestNode_Delay` in the ladder with a missing `inSignal` starts **at accept** — the flood runs while the player is still at home and they arrive to wet mud and a finished bloom. The event "works" and the entire point is lost. | every ladder node's inSignal chains to the previous rung; test by accepting and NOT travelling for 2 days |
| **SignalActivable starts disabled** | the `WitnessedAndLeft` listener needs `inSignalEnable` AND `inSignal`; forget the enable and Success can never fire — the quest hangs forever after a perfect witnessing | validator + the paired-listener pattern above |
| **one unresolvable [symbol] blanks ALL text** | the flood-news letter is atmosphere-dense prose; any literal square bracket, or a suffix typo (`[site_labelDefinite]` — doesn't exist; `_definite` replaces `_label`), renders the offer EMPTY | `grep -n '\['` every rule string; fallback sibling for every conditional symbol |
| **quest never fires** | route 2 + `isRootSpecial` means the validator will warn "no XML firing route" for the scheduler-fired path — that warning is *expected*; the real risk is the C# scheduler's beat never triggering, which no XML tool can see | dev-mode `Generate quest…` is the deterministic test; never wait on the scheduler for verification |
| **nothing after QuestNode_End runs** | tempting to end at `FloodPassed` and "let the site linger" — ending there tears down the QuestParts and (site-linked) the harvest window | end only on the post-flood `MapRemoved`, as sketched |
| **TestRunInt drops quests silently** | only if Q2 forces a custom tile-picker root node; the sketch keeps a pure `QuestNode_Sequence` root precisely to avoid this class | keep the root vanilla |
| **`everAcceptableInSpace`** | a gravship campaign — the player may be IN SPACE when the offer lands; unset, Accept is greyed and reads as a dead quest | set `everAcceptableInSpace true` |

Validation: `python3 skills/rimworld-quests/scripts/validate_quest.py` before
any deploy; the known-expected warning is the firing route.

---

## 5. Owner rulings (2026-09-10 morning batch — all four answered)

1. **Lethality: injury+knockdown ceiling**, first flood AND the post-witness
   natural floods — nobody drowns outright; lethality lives only in flagship
   set-pieces (ruled at one stroke with the growth design's Q1).
   `troopersmith1.deathrattle` is live in the mod list, so any edge-case
   mortal outcome resolves through its dying-state rescue window — that mod is
   the protection layer; build no second one.
2. **Site: one canonical, fixed authored tile** in the Cracked Lands — full
   control of ledges/ruin/chimes, a nameable place in the campaign. No
   floating site, no custom tile-picker C#.
3. **Voice: a Moisture Farmer invitation** (see the rewritten offer fiction
   above). Colors goodwill toward later Farmer content.
4. **Trigger beat: first gravship landing within range** of the Cracked
   Lands — tied to player motion, not the calendar and not a held lever.
