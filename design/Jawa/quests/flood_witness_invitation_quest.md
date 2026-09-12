# The Flood-Witness Invitation — Utinni campaign quest spec

_Prose spec per `skills/rimworld-quests/SKILL.md` §2, authored 2026-09-12.
Downstream of the RULED design in
`design/Jawa/worldbuilding/flood_witness_event_design.md` (owner rulings
2026-09-10: declinable Moisture Farmer invitation with a re-offer scheduler,
never a forced interception; lethality capped at injury+knockdown, no deaths;
one canonical fixed authored Cracked Lands tile; trigger = the player's first
gravship landing within range). This file adds no ruling and reverses none._

**Layer boundary — read this first.** The flood mechanism itself (canyon flood
cycle, warning chimes, the wall, recede-to-soil, soak-driven growth) ships as
the standalone RimMandrake mod built under `FLOOD_CANYON_BIOME_1`
(`src/RimMandrake/FloodedCanyon/`, packageId `mandrake.rm.floodedcanyon`).
THIS quest is the Utinni campaign layer that **consumes that mod as a hard
dependency**. Nothing mechanism-level is designed here: no terrain lists, no
flood-fill rules, no damage math. Where the machinery addendum notes vanilla
Odyssey `Flood.cs` exists, the subclass-vs-custom fork is the mechanism mod's
build decision, settled by quicktest at build — this spec is agnostic to how
the wall moves, and binds only to *that* the dependency can be told "flood
this map, on this schedule, with the full chime ladder."

Every number this spec invents is marked **⚙ tunable**. The quest is whole
with no Oracle — no LLM call anywhere in it. No Force content. No worldgen:
the witness site is one hand-authored map at one fixed tile on the frozen
world.

---

## 1. Premise and fantasy

The Cracked Lands' whole story is the flood — death, then soil, then the
bloom — and it almost never happens while anyone is standing there. The
Moisture Farmers read the sky for a living, and this once, early, they extend
a neighbor's courtesy: a storm is already building on the Dew Horn peaks, a
named canyon is going to take the wall within days, and there is a refuge
ledge with room on it. Come and see.

The player fantasy is **choosing your moment to believe the warnings**. The
canyon floor holds the salvage; the ledge holds safety; every forewarning is
a fresh chance to stop hauling and start climbing, and the game never says
which — the chimes do. Then the two faces of the flood land in order, on one
screen: the wall that would have killed them, and the bloom that exists
because of it. A cutscene could show that; this quest makes the player *earn
the believing*, which is the Farmers' own craft ("an experienced Farmer
trusts the ground before the chimes").

The one-sentence reason, no reward named: *the Farmers are offering the clan
a seat at the one moment that explains everything else about this place.*

---

## 2. The offer

### Trigger and route

- **Trigger beat (RULED):** the player's first gravship landing within range
  of the Cracked Lands. A small campaign-assembly scheduler (C#,
  `RimMandrake.Utinni` namespace) watches for that beat and fires the offer
  via a dedicated GiveQuest incident — never the storyteller's random pool.
  "Within range" threshold: ⚙ tunable, propose ~30 world tiles.
- **Never forced.** The offer is a letter the player may decline, ignore, or
  accept and then abandon. There is no interception, no forced map, no
  penalty channel of any kind on refusal.

### The invitation letter (voice)

A Moisture Farmer speaks — warm, plain, weather-literate. Not a summons, not
a transaction. The letter carries, findable at a glance:

- **The ask:** travel to the named canyon and be on the refuge ledge when the
  water comes through.
- **The why (no reward named):** the storm is *already forming* on the Dew
  Horn peaks — this is why the plot, not weather RNG, owns the clock — and
  floods wait for no one; the Farmers are offering their read of the sky as a
  gift.
- **The deadline:** the offer expires if never taken up — ⚙ tunable, ~15
  days — framed in the fiction as "this storm will spend itself whether you
  come or not."

What the letter does NOT promise: loot. The salvage and the bloom are
discovered on-site, diegetically. The invitation is to *see*, and the seeing
is honestly the payload (§5).

### The re-offer scheduler

The guarantee of "at least one witnessed flood" is not one offer — it is
**offers until one witnessing completes.** The scheduler re-fires the
GiveQuest incident on a long beat until one instance of this quest has ended
`Success`, checked against the quest history (no new save state), then stops
forever.

| the player… | quest outcome | then |
|---|---|---|
| declines the letter outright | quest never created | re-offer after ⚙ ~1 quadrum: a NEW storm, a new letter |
| accepts, never travels; site times out (⚙ ~15 d) | `End Unknown` — no fault, no verdict | re-offer, same beat |
| arrives, leaves before the wall | `End Unknown` + a letter: the canyon flooded at their backs, wet clay on the wind | re-offer — the fiction supports retries indefinitely |
| is on the site map when the wall passes | `Success` (armed; ends when they eventually leave, so the harvest stays alive) | scheduler stops forever |

**Declining gracefully:** no goodwill loss, no Farmer sulk, no scolding text.
Each re-offer is a fresh storm and a fresh courtesy — the Farmers' patience
is characterization, and the punishment for refusing is only ever missing
the show. Mid-quest abandonment is equally free: `Unknown`, never `Fail`.

---

## 3. The beats at the witness site

The site is the one canonical authored slot canyon (RULED: fixed tile,
hand-authored layout under the same template machinery as
`MOISTURE_FARM_TEMPLATES_1`): refuge ledges cut along the old road, waymark
cairns, water chimes seated in the walls, a flood-marked ruin — the farm
built one meter too low — and loose salvage scattered on the canyon floor.
The deliberate temptation: everything valuable starts at the bottom, and
safety is at the top.

Total lead time, arrival → wall: ⚙ tunable, ~1.5 in-game days, so a player
who came for the salvage has real hauling time to gamble with. The quest
arms the dependency's chime-and-flood cycle on this schedule the moment the
site map generates — never on accept, so nothing runs while the player is
still at home.

### Phase 1 — Arrival

Dry stillness. Nothing moves. The floor salvage is harvestable immediately;
the ledges are marked, sheltered, and empty. Most Cracked Lands visits are
exactly this — the phase's job is to look like every visit that isn't the
one.

**Player can DO:** haul floor salvage; scout the too-low ruin from outside;
set up camp — and the first real choice is *where*: pitching on the ledge
costs hauling distance every trip, pitching on the floor is faster and is
the wrong answer they don't know yet. Pack animals and crawlers park
somewhere, and that somewhere matters later.

### Phase 2 — The Chimes (the forewarning ladder)

The dependency's fixed sensory order, delivered as quest letters and
messages layered over the mechanism's own tells — smell before sound, ground
before sky. ⚙ All intervals tunable:

| T from map gen ⚙ | tell | delivery |
|---|---|---|
| 0 | dry lightning over the off-map Dew Horn — the storm breaks | neutral letter + ambient weather |
| +8 h | wet clay on the wind | on-screen message |
| +1 d | the flats tick — the Sealed wake, sleepers boiling up out of the cracked pans | incident (spectacle) + message |
| +1 d 6 h | **the water chimes ring** — tones rolling up through the stone ahead of any sound of water | THREAT letter: *"the chimes are ringing — climb NOW"* |
| +1 d 8 h | the wall | Phase 3 |

The chimes-to-wall gap (⚙ ~2 h) is the escape pressure: enough for any pawn
on the floor to reach a ledge, not enough to finish loading the mule.

**Player can DO:** the haul-versus-climb gamble, continuously re-asked at
every rung — each tell is a fresh decision point with two defensible
answers. Move camp upslope. Send animals up early (they walk slower than the
player thinks). Push one last greedy trip into the ruin. Or trust the ground
before the chimes and be sitting comfortable on the ledge a day early with
less loot — also a defensible answer.

### Phase 3 — The Wall

Red-brown water down the canyon; the flood condition runs ⚙ ~6 h. Floor
cells flood; ledges and benches are untouched. Floor salvage not taken is
swept. The too-low ruin is torn open. The colony watches from the ledge —
the biome's whole artistic theme compressed into one screen: the roar, the
red-brown, the stillness above it.

**Lethality (RULED): injury + knockdown ceiling. Nobody drowns outright.**
A pawn caught by the wall is hurt and downed, never killed by it. (The live
campaign list carries `troopersmith1.deathrattle`; any edge-case mortal
outcome resolves through its dying-state rescue window — that mod is the
protection layer; this quest builds no second one.)

**Player can DO — the rescue moment:** a downed pawn on the floor is
reachable. The injury-ceiling law is precisely what makes rescue *playable*
instead of body-recovery: someone can rope down or dash the shallows to drag
a knocked-down pawn (or the mule) to a ledge ramp, taking their own capped
hit for it. Fail, and the pawn surfaces battered in the mud in Phase 4 —
worse for wear, alive, a story. Also playable: nothing — standing on the
ledge and just watching is the intended default, and it is allowed to be
enough.

### Phase 4 — The Growth

The water recedes into the cracks and hides. Then the soaked floor visibly
GROWS on screen — the dependency's soak-driven growth showing off: the bloom
crop coming up fast, the Spender carpet, fliers wheeling in to feed and
dipping to fish the canyon water (what they pull out has teeth — that water
holds no truce). This is `EXPLOSIVE_PLANT_GROWTH_1`'s guaranteed showcase
edge if that engine ships; if it hasn't, the phase degrades to the
dependency's own growth coupling plus the letter — the quest is whole either
way.

**Player can DO:** watch it happen — the phase is staged to be *looked at*;
begin harvesting bloom crop as it matures; hunt or fish at the player's own
risk near the no-truce water; walk pawns onto the fresh soil the letter just
named.

### Phase 5 — The Aftermath (the harvest window)

Left behind on the floor: wet mud and fresh soil, drowned Spender carrion,
crack-wax scattered on the pans, the ruin's cache broken open, and re-dealt
salvage the wall carried in — the Jawa payoff, fresh exactly as long as the
mud is. The quest is already won the moment the wall passed; this phase is
pure temptation with the clock running the other way.

**Player can DO — the harvest-window gamble in reverse:** stay and strip the
canyon (carrion spoils ⚙, mud dries ⚙, bloom crop runs its cycle ⚙ — all the
dependency's numbers, not this spec's), or leave early and keep the caravan
tight. Success does not end the quest until they leave the map, so the site
— bloom, salvage, carrion — stays alive for the whole stay. A closing letter
on departure names, in the Farmer's voice, what was carried up against what
the water took: the quest's later acknowledgement of every haul-or-climb
choice the player made.

---

## 4. Knowledge and reward

**The reward is diegetic, scaled by nerve.** Salvage hauled before the wall,
the ruin's opened cache, re-dealt flood salvage, crack-wax, carrion, and the
bloom harvest — plus the sight itself. **No `QuestNode_GiveRewards`, no pod
drop, no silver:** a payment on top would cheapen the invitation and add an
asker-faction reward dependency the fiction doesn't have.

**What witnessing durably grants:**

1. **The record:** `RUT_FloodWitnessed` history event on `Success` — the
   campaign's permanent fact that this colony has seen the wall. It is what
   stops the re-offer scheduler.
2. **The standing mechanic (design §"later natural floods"):** after the
   witnessed flood, floods run as a standing rare incident on player-occupied
   Cracked Lands maps, always with the full chime ladder — the witnessed one
   is the tutorial the world then holds the player to.
3. **⚑ FLAGGED OPTION — UNRULED, not a fact of this spec:** the machinery
   addendum proposes gating the home-map "plant reached the tell" alert on
   having witnessed this event — witnessing becomes the knowledge unlock.
   Carried here as an option for an owner sitting; the quest as specced
   neither grants nor withholds it, and nothing else in this file depends on
   the answer.

---

## 5. Replay behavior

- **Guaranteed first:** the scheduler re-offers until one `Success`, then
  never again. Before that first witnessed flood, no natural flood runs on
  any player-occupied map — the first wall the player ever sees is this one;
  RNG never delivers a lesser version first.
- **Natural afterwards:** post-witness floods are the dependency's standing
  mechanic (incident-driven, long refire ⚙, full chime ladder every time,
  same injury-ceiling law). The quest itself never re-offers; the *flood*
  recurs as a designed moment. Honest consequences apply: floor structures
  and pawns that ignore the ladder take the (capped, non-lethal) hit.
- Abandoned or expired instances end `Unknown` and cost nothing; each
  re-offer is fictionally a new storm, so repetition reads as weather, not
  as a stuck quest log.

---

## 6. Def-shape sketch

Placeholders only — `<RUT_...>` names per `design/NAMING_SCHEME_PLAN.md`
campaign tier; every node name to be copied from shipped defs at build time,
never guessed. The dependency's own defs (`RM_` tier) are named by that mod
and are cited here only as the contract surface.

**Defs this quest owns:**

| def | type |
|---|---|
| `RUT_FloodWitness` | QuestScriptDef |
| `RUT_GiveQuest_FloodWitness` | IncidentDef (`GiveQuest` / `IncidentWorker_GiveQuest`) |
| `RUT_WitnessCanyon` | SitePartDef + authored layout (template machinery) |
| `RUT_FloodWitnessed` | HistoryEventDef |
| (C#) witness scheduler | `GameComponent`, `RimMandrake.Utinni` namespace — fires the incident on the first-gravship-landing-in-range beat; re-fires until one `Success` |

**Offer route:** route 2 (dedicated incident) — `rootSelectionWeight 0`,
`isRootSpecial true`, `expireDaysRange` ⚙ ~15, `everAcceptableInSpace true`
(gravship campaign — unset, Accept greys out in space and reads as a dead
quest). The validator's "no XML firing route" warning is expected; the
deterministic test is dev-mode *Generate quest…*, never waiting on the
scheduler.

**Node outline (vanilla vocabulary; ladder armed on `site.MapGenerated`,
NEVER on accept):**

```
QuestScriptDef RUT_FloodWitness
  root = QuestNode_Sequence
    QuestNode_Set                  cosmetic slate strings; no rewardValue
    Util_GenerateSite / QuestNode_GenerateSite → storeAs: site   (fixed authored tile — no tile-picker)
    QuestNode_SpawnWorldObjects    (site)
    QuestNode_WorldObjectTimeout   (site, ⚙ ~15 d, isQuestTimeout,
                                    inSignalDisable: site.MapGenerated) → NeverCame
    QuestNode_End                  inSignal NeverCame · outcome Unknown

    -- the ladder: each rung chained off the previous rung's outSignal --
    QuestNode_Letter               inSignal site.MapGenerated      (storm on the peaks)
    [arm-the-dependency step]      inSignal site.MapGenerated      (see contract below)
    QuestNode_Delay ⚙              → ClaySmell → Message
    QuestNode_Delay ⚙              → SealedWake → CreateIncidents (on $site map)
    QuestNode_Delay ⚙              → ChimesRing → Letter (ThreatBig: "climb NOW")
    QuestNode_Delay ⚙ ~2h          → WallArrives  (the dependency's flood runs on $site map)
    QuestNode_Delay ⚙ ~8h          → FloodPassed → Letter (death, then soil, then this)
    QuestNode_CreateIncidents      inSignal FloodPassed  (bloom showcase — degradable stub)

    -- the witness race: same signal, two meanings, resolved structurally --
    QuestNode_SignalActivable      inSignalEnable: FloodPassed
                                   inSignal: site.MapRemoved → WitnessedAndLeft
    QuestNode_End                  inSignal WitnessedAndLeft · outcome Success
                                   (successHistoryEvent RUT_FloodWitnessed)
    QuestNode_SignalActivable      inSignal: site.MapRemoved (armed from start,
                                   inSignalDisable: FloodPassed) → LeftEarly
    QuestNode_End                  inSignal LeftEarly · outcome Unknown
```

**Witness detection is structural, no C#:** presence = the site map exists;
"witnessed" = `FloodPassed` beats `site.MapRemoved` in a plain signal race
(`SignalActivable` enable/disable pair — the vanilla idiom for one signal
meaning different things in different phases). A pawn asleep in a tent still
witnesses; good enough.

**Dependency contract (named, not designed):** the quest needs exactly one
verb from `mandrake.rm.floodedcanyon` — *arm the chime-and-flood cycle on
this map, now, on this lead time* — the production twin of the mod's
existing "Arm chime + flood soon" debug action. Whether that surfaces as an
IncidentDef the quest fires via `QuestNode_CreateIncidents`, or one tiny
custom node calling the mod's MapComponent, is a build decision made against
the mod's real API; either way the mechanism, pacing, terrain, damage cap
and chime audio all stay the mod's. Declared as a hard `<modDependencies>`
entry.

**Known traps carried from the design (build checklist, not prose):** never
rename `site` (four load-bearing signals hang on it); every ladder node
carries an `inSignal` (a missing one runs the flood while the player is
home); `SignalActivable` starts disabled — forget `inSignalEnable` and
Success can never fire; `grep -n '\['` every rule string; validate with
`skills/rimworld-quests/scripts/validate_quest.py` before any deploy.

---

## 7. Text register notes

- **The Farmer's voice, everywhere the quest speaks:** offer letter, ladder
  letters, the left-early letter, the closing tally. Warm, plain, concrete,
  weather-literate — a person who reads the sky for a living and says so in
  small words. Never portentous, never system-flavored ("a flood event will
  occur" is banned register). The threat letter is the one place the voice
  sharpens, and it sharpens into *urgency*, not menace: the chimes are
  ringing, climb now.
- **The Jawa side stays the clan's:** salvage-strike rhythm, crawlers, the
  greed — the Farmers bring the news, the clan brings the crawlers. Farmer
  text never scolds the player for hauling; at most it observes, dryly, what
  the water thought of the mule.
- **Sensory order is canon:** smell before sound, ground before sky. Letters
  land in that order and name those senses.
- **Honest timing in the fiction:** the storm is already forming when each
  letter arrives — every offer and re-offer reads as news, not as a spawned
  task.
- **Grammar discipline:** no literal square brackets in any rule string; a
  fallback sibling for every conditional symbol; suffixes copied from the
  corpus (`_definite` replaces `_label`; `_duration`, never `_ticksToDays`).
- **No Oracle text path.** All strings are authored rule packs; the quest
  reads identically with no LLM on the machine.
