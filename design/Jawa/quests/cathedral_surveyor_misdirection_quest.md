# Quest spec — the surveyor misdirection ("Boring Answers")

**Item lineage:** the survey-misdirection beat of `CATHEDRAL_PLAYER_CONCEALMENT_ARC_1`
(`design/Jawa/cathedral_concealment_arc_spec.md` §4), **RULED IN by CARD A4,
2026-09-12** — "the one place the player actively practices concealment rather
than abstaining." Prose spec per `skills/rimworld-quests/SKILL.md` §2; the def
is the second half of the work and is not authored here. No defNames are coined —
every `<RUT_...>` token below is a placeholder that binds at build time under
`design/NAMING_SCHEME_PLAN.md`.

**Laws this spec lives under (inherited, not restated):** the knowledge gate
(nobody in-world knows the Cathedral is alive — every player-facing line here
reads as guild pragmatism, never as protecting a person); sheet §6 bans 1/2/3/6
(no §GM truth, no mercy explanation, no Sentinel-raid story, no drill
explanation); rationed patience — nothing here can make faction 13 raid, ever;
K2 anti-laundering — success scrubs no Imperial Heat; the two LLM laws — the
game is whole with the Oracle absent, Oracle upgrades voice only; no Force; no
worldgen (the survey camp is a quest Site on an existing tile of the fixed
world, standard quest machinery, not generation).

---

## 1. Premise and player fantasy

An Imperial survey team sets up camp on Cathedral-adjacent ground and starts
doing what surveys do: coring, sounding, weighing, asking. The Cathedral has
survived three centuries of exactly this by looking exceptionally dull — and
now the answers the surveyors get depend on the player, because the player's
salvage operation is the loudest thing on the ground.

The fantasy is **being the one who feeds the Empire boring, believable lies** —
not fighting, not hiding, but performing dullness so well the surveyors write
"low-grade scrap field, no further action" and leave. It is the player doing,
knowingly or not, what the Cathedral has always done. Success is the loudest
possible signal that the player has understood what this place is doing —
without one line of text saying so (arc spec §4, verbatim intent).

**The reason (one sentence, no reward named):** Imperial surveyors on your
salvage ground means questions, and questions become garrisons — and a
garrison is the end of free salvage. That is the whole in-world motive; it is
true, it is guild self-interest, and it respects the knowledge gate.

## 2. How it is offered — route 2, a dedicated incident

**Route: a dedicated `IncidentDef` (skill §7 route 2) with
`rootSelectionWeight 0`, fired by the GM blackboard through the bridge.**

Why not the other three:

- **Natural random pool (route 1) — no.** The offer must be a function of
  GM-blackboard state the storyteller cannot read: Imperial Heat in a band
  (tunable — the survey IS Heat made local), Cathedral Regard stage
  TOLERATED+ (the letter needs a channel; at WARY nobody would ask the player
  anything), and exposure pressure below the gone-dark threshold. A weighted
  root would fire on colonies where none of that holds.
- **Quest giver (route 3) — no.** `givenBy` channels (traders etc.) put the
  offer on someone's schedule, not the survey's; and the asker here must be
  the deniable enclave/Utinni channel, not a passing trader.
- **Framework scheduler (route 4) — fallback only.** The arc spec §7 names
  CQF/bridge-injected letters as the family; if the build lands on CQF the
  incident is still the shape underneath — the GM decides *when*, the
  incident delivers *that*.

`rootSelectionWeight 0` is the deliberate idiom for incident-only firing
(skill §7); it also gives the deterministic dev trigger the skill demands —
dev mode → Quests → Generate, or the bridge fires `<RUT_IncidentSurveyorMisdirection>`
directly. `minRefireDays` ~30 (tunable): the second telling cheapens the first,
and the GM layer additionally caps occurrences per campaign (tunable, register:
2–3 at most).

**Offer gates (all tunable, all GM-side, shadow-mode first):** Regard stage ≥
TOLERATED; Imperial Heat ≥ the Act-I band that makes a survey plausible; not
during Cathedral gone-dark posture. Note for the build: if the GM ever wants a
WARY-stage survey (surveyors arrive, no letter, player watches it happen),
that is a *different, letter-less event* — this quest is the asked version only.

## 3. The offer text and the asker

A letter through the enclave channel — deniably sourced per arc spec §3:
"Vent Forty asks", "the Utinni insists", never the Cathedral. The letter's
register is salvage-guild pragmatism throughout:

> *An Imperial survey detail has staked ground by the [surveySite_label]. They
> core, they weigh, they ask questions. Vent Forty has seen what happens to
> ground the Empire finds interesting, and would prefer this ground stay
> boring. So would you.*

**Register bans enforced here and in every string below:** no agency attributed
to the Cathedral (pre-stage-3 grep gate, arc spec §8); no mercy explanation
(ban 2 — the droids and Sentinels do not come up at all); no drill lore
(ban 6); nothing that reads the ground as a person. The words "it prefers",
"it wants", "it watches" are banned even as color. The Cathedral appears in
this quest only as terrain.

Accepting means taking the enclave's request. **Declining is a real choice**
(see §5, "do nothing") — the survey still happens in the fiction; the GM layer
reads the declined/expired offer and applies the passive-survey exposure bump
(§6). Build note: a declined quest leaves no QuestParts, so that consequence
is GM-side by design, keyed on the offer's non-acceptance — not a def bug.

## 4. The shape on the map

On accept (structure, not defNames):

- A **survey camp Site** spawns on a Cathedral-adjacent tile of the fixed
  world (`Util_GenerateSite` family; generate-then-spawn so a pre-accept
  invalidation leaves no litter). Dressing: existing Empire faction pawns —
  pursuit-spine dressing, **no new faction** (arc spec §4).
- A **survey window**: 10 days (tunable, range 8~12), the quest's real and
  shown deadline — `WorldObjectTimeout` with `isQuestTimeout`, armed on
  accept. What the player sees: "the survey concludes in [surveyTicks_duration]."
  The deadline is enforced: when it lapses, the surveyors file whatever they
  have (§6). No fake urgency.
- The camp is a place you can caravan to, deliver to, and (ruinously) attack.
  It is never hostile unprovoked.

## 5. The choice — three deception verbs, and the two doors around them

The decision with defensible answers on every side (skill §2 Q2). The player
picks a verb by *doing* it — no menu; each verb is a structural act vanilla
already knows (item handover, labor, pawn lending), per skill §9's XML test.
The verbs are not exclusive; the strongest play stacks them, at stacked cost.

**Verb 1 — FORGE the ledgers.** Craft a `<RUT_ForgedSalvageLedger>` (a cheap
craftable: work amount tunable, register "an afternoon at a desk"; requires a
colonist with Intellectual ≥ threshold, tunable) and deliver it to the camp —
decades of doctored guild tallies showing exactly the boring yields a scrap
field should show.
*Trade:* cheapest and fastest, weakest alone — paper convinces clerks, not
instruments. Counts as a **partial** answer: alone, it downgrades the survey's
report but does not close it (partial-success weighting tunable).

**Verb 2 — STAGE the dig.** Deliver N units (tunable, register: a genuinely
annoying amount — ~400 of common deck-plate scrap / steel) to the survey camp
inside the window: let them watch the bulk come out of the ground, then let
them weigh it. The extraction loop performed as theater — which is, verbatim
canon, what the extraction loop *is*.
*Trade:* the expensive, load-bearing verb — real colonist labor-days spent
mining worthless bulk under a deadline, hauled to an Imperial camp while your
Heat is by definition nonzero. Alone it is a **full** answer. It is also the
arc's named "large Regard gain" act (§4): the player practicing the
Cathedral's own cover.

**Verb 3 — GUIDE them to the decoy.** Lend one colonist to the survey detail
as a local guide for M days (tunable, 3~5; hospitality-lodger machinery — the
pawn leaves with them and returns) to walk the surveyors to a genuinely
strange-but-dead site the guild "happens to know": a dead-smartsteel seam, a
Scarlands-margin wreck (site chosen from existing fixed-world dressing; no
new lore objects). The survey gets a *finding* — a real one, a boring-once-
understood one — and findings close surveys.
*Trade:* strongest single verb, and it burns two real things: the colonist
(gone M days, at Imperial elbow — if pursuit-spine events are live, the guide
is exposed to them; tunable risk), and the decoy itself — the site's salvage
value transfers to an Imperial claim marker and is lost to the player for
good. Feeding the Empire *something* is how you feed it nothing.

**The passive door — do nothing.** Decline, or accept and let the window
lapse without acting. Defensible: every verb puts colonists or paper in
Imperial hands while Heat is high; a cautious clan stays home. The survey
then runs on its own instruments (§6, failure-by-default).

**The dark door — point them at the anomaly.** The player can walk into the
camp and hand over the real thing: coordinates, hum recordings, a live-metal
sample. This is arc spec §4 option (c) and §6.1's deliberate-exposure door,
and it belongs in the quest as a genuine (terrible) choice, delivered as an
item handover of a `<RUT_AnomalyEvidence>`-class item the player must
deliberately assemble (no accidental betrayal — assembling it is its own
informed act; components tunable). Text at handover stays in Imperial
bureaucratic register; no string acknowledges what was betrayed, because no
string in this quest may know.

## 6. Success, failure, and the ledgers they move

Structural outcomes (one `QuestNode_End` per branch, outcome hard-coded):

| Branch | Quest outcome | What the world does |
|---|---|---|
| Full answer delivered in window (verb 2, or verb 3, or verb 1 + either) | **Success** | Camp packs up early; letter in §P register (below). |
| Only verb 1 in window | **Success** (with a partial flag on the slate for the GM) | Camp leaves at window's end; drier letter. |
| Window lapses, nothing delivered | **Fail** | Camp leaves; the report files itself. |
| `<RUT_AnomalyEvidence>` delivered | **Fail** (betrayal flag) | Camp leaves *fast*. §6.1/§6.2 consequences (GM-side). |
| Player attacks the camp | **Fail** | Empire goodwill hit + the report the survivors (or the silence) files. |
| Camp destroyed by third parties, no player agency | **Unknown** | No verdict either way — the gate holds both ways: no punishing, and no crediting, what the player did not do. |
| Surveyors invalidated pre-accept | **InvalidPreAcceptance** | Disappears silently (`NotYetAcceptedOnly`). |

**Cathedral Regard (GM blackboard, invisible, shadow-mode first — all deltas
tunable, registers per arc spec §2):**

- Success via verb 2 (staged dig): **the large gain** — the arc's single
  biggest earnable credit outside the §4 restore choice.
- Success via verb 3 or verb 1+3: large gain, one step below verb 2 (the dig
  is the Cathedral's own move; the decoy is merely clever). Tunable.
- Partial (verb 1 alone): small gain.
- Do-nothing: **zero Regard change** — abstention is not an offense; the
  needle-mover list's spirit (no punishing what wasn't done) applied. Tunable
  to a token loss at VOUCHED stage only, where more was ratable, if the GM
  pass wants it — but zero is the default.
- Betrayal door: Regard floors permanently — arc spec §6.2 verbatim (boons
  and missions close for good; the Utinni's vouching is spent; her register
  carries the loss, elsewhere, later — not in this quest's text).

**Exposure pressure (the A3 losable track — this quest FEEDS it on failure):**

- Success (full): the survey closes clean — exposure pressure *reduced* by a
  tunable step, or its next scheduled rise skipped (GM's choice of mechanism;
  register: a real, felt reprieve).
- Partial: exposure unchanged.
- Do-nothing / lapsed: **exposure bump** (tunable, moderate) — "anomalous
  readings, recommend follow-up" enters the Imperial paper trail. This is the
  ruled consistency with A3: failure here is a real installment on the real,
  losable full-discovery outcome.
- Attacked camp: **large exposure bump** + standard Empire goodwill/Heat
  consequences — nothing makes the Empire more interested in ground than
  salvagers killing a survey detail on it.
- Betrayal door: the largest single exposure event in the arc (tunable;
  register: most of the distance to gone-dark in one act).

**What never moves (hard bounds):**

- **Imperial Heat is never scrubbed by success** — K2 anti-laundering,
  verbatim: the Empire's suspicion of the *player* is not the Cathedral's
  ledger. Heat moves only by its own existing rules (attacking the camp is an
  ordinary Heat event; deception success changes Heat not at all).
- **Faction-13 goodwill does not move from this quest.** Regard is the arc's
  ledger; goodwill mirrors sacrilege/drill acts only (arc spec §2 — one act,
  two ledgers, no double machinery, and none of this quest's acts is
  sacrilege). Nothing here can approach −75; the hysteresis is untouched.
- **No Cathedral response is authored.** No Sentinel reaction, no hum event
  scripted by this quest — the stage/hum consequences arrive later, through
  the kit's existing stage-baseline lane, unattributed. The quest ends and
  the ground says nothing. (Skill §6: nothing scheduled after `QuestNode_End`
  runs anyway — the delayed consequence lives on the GM blackboard, which is
  this arc's version of "the goodwill change the storyteller turns into
  raids": the Regard change the GM turns into thaw.)

## 7. Rewards — deniably sourced, per the arc's surfacing rules

No player-facing string attributes Cathedral agency before stage 3, so the
paying party is the asker: the enclave channel.

- **On full success:** payment from Vent Forty in the guild's own coin —
  silver plus a salvage-rights sweetener (a marked cache of dead smartsteel,
  "a seam the guild surveyed and never filed"; value tunable, proportional to
  the labor verb 2 actually costs — skill §2 Q5). Delivered by pods or at the
  enclave, never "found" on Cathedral ground: a reward materializing from the
  terrain would attribute agency by placement, which the grep gate cannot see
  and this spec therefore bans by rule.
- **The real reward is invisible:** the Regard gain, which the player reads
  only later and only the fiction's way — hum, bolts, droids, what gets
  offered next (arc spec §3, no gauge ever). The quest must feel slightly
  underpaid in silver; the arc pays the balance in thaw. This asymmetry is
  deliberate and is the design (register note for the tuning pass: do not
  "fix" it).
- **On partial:** silver only, reduced.
- **Never:** gravtech, boons, or anything the concealment arc gates behind
  VOUCHED — this quest is how you *reach* those, not where they leak.
- Betrayal door pays **Imperial** coin, promptly and well (tunable — the
  Empire pays for findings), because the dark door must be a real temptation
  or the choice is fake. What it costs arrives silently, forever, per §6.

## 8. Text register (whole-quest discipline)

- Every string — name, description, letters, camp inspect text — is
  salvage-guild pragmatism or Imperial bureaucratic dryness. Two voices, no
  third. The Cathedral is terrain in every line.
- Success letter, §P register (the world describing behavior, never intent):
  > *The survey detail has struck camp. Their report, a clerk let slip, runs
  > four lines. Ground like this doesn't rate five.*
- Failure (lapsed) letter:
  > *The surveyors packed their cores and left without goodbyes. Whatever
  > their instruments made of this ground, it is written down now, and filed
  > where filed things wait.*
- Bans checked by the arc's grep gate (arc spec §8): no agency attribution
  pre-stage-3; no mercy explanation ever (ban 2 — no droid or Sentinel is
  mentioned in any string of this quest); no drill description (ban 6); no
  Sentinel-raid framing (ban 3 — the camp's fate if attacked involves only
  Imperial consequences).
- Grammar hygiene per skill §5: no literal square brackets in any string;
  every conditional symbol gets an unconditional empty-fallback sibling; all
  ticks surfaced via `_duration`.
- Oracle: all of the above ships as fixed fallback text FIRST; the Oracle may
  upgrade the droid commentary pools active during the survey window (kit
  lane, not quest text) — text/menu authority only. Every beat of this quest
  completes with the Oracle absent.

## 9. Def-shape sketch (outline only — no defNames coined)

Validator (`skills/rimworld-quests/scripts/validate_quest.py`) runs before any
deploy; every node name below is to be copied from a shipped def at build
time, never trusted from this sketch.

```
<RUT_IncidentSurveyorMisdirection>            IncidentDef
  category GiveQuest · workerClass IncidentWorker_GiveQuest
  questScriptDef → <RUT_QuestSurveyorMisdirection>
  baseChance 0 (GM/bridge-fired only; dev-triggerable)

<RUT_QuestSurveyorMisdirection>               QuestScriptDef
  rootSelectionWeight 0                       (deliberate: route-2 idiom)
  expireDaysRange 3~5 (tunable)               (the OFFER window)
  defaultChallengeRating 2 (tunable)
  questNameRules / questDescriptionRules      (§3/§8 text; fallbacks on every
                                               conditional symbol)
  root = QuestNode_Sequence
    ├─ QuestNode_GetMap                       → slate: map
    ├─ Util_GetDefaultRewardValueFromPoints   → slate: rewardValue (then
    │     damped, tunable — §7's deliberate underpayment)
    ├─ site generation (Util_GenerateSite family)
    │     generate → slate: surveySite · spawn on accept
    │     surveyor pawns: existing Empire faction, addToList surveyors
    │     (LIST var, not storeAs — object signals hang on the list)
    ├─ QuestNode_WorldObjectTimeout           surveyTicks = 10 days (tunable)
    │     isQuestTimeout · inSignalDisable    ← SurveyAnswered
    │     outSignal                           → SurveyLapsed
    ├─ delivery branch A (ledger item at camp)     → LedgerDelivered
    ├─ delivery branch B (N bulk-scrap at camp)    → DigStaged
    ├─ lend-colonist branch C (lodger-style, M days,
    │     returns via shuttle/walk-out)            → DecoyTaken
    ├─ delivery branch D (<RUT_AnomalyEvidence>)   → AnomalyHandedOver
    ├─ signal composition (SignalActivable / AnySignal shapes —
    │     arm order per skill §6: enable BEFORE listen):
    │     DigStaged | DecoyTaken | (LedgerDelivered + any) → SurveyAnswered
    │     LedgerDelivered alone at timeout          → SurveyAnsweredPartial
    ├─ QuestNode_Letter nodes                 (each WITH inSignal — a
    │     top-level Letter with none fires on accept, skill §6 trap)
    ├─ QuestNode_GiveRewards  inSignal SurveyAnswered   (sibling BEFORE End)
    ├─ QuestNode_End  Success   ← SurveyAnswered / SurveyAnsweredPartial
    ├─ QuestNode_End  Fail      ← SurveyLapsed
    ├─ QuestNode_End  Fail      ← AnomalyHandedOver     (betrayal flag for GM)
    ├─ QuestNode_End  Fail      ← surveyors.Destroyed [player agency route]
    │     (⚠ build note: distinguishing player attack from third-party
    │      destruction is the sketch's hardest seam — see UNKNOWN)
    ├─ QuestNode_End  Unknown   ← surveySite destroyed, no player agency
    └─ QuestNode_End  InvalidPreAcceptance
          signalListenMode NotYetAcceptedOnly
  NO goodwillChangeAmount on any End for faction 13 — Regard is GM-side;
  Empire goodwill on the attacked branch uses a <RUT_...> HistoryEventDef
  (a defName and a label, nothing more) so the faction-tab line exists.

<RUT_ForgedSalvageLedger>                     cheap craftable, quest-delivered
<RUT_AnomalyEvidence>                         deliberately-assembled item (§5)
```

**Silent-failure traps this sketch has already stepped around** (skill §6/§7,
kept here so the builder does not re-learn them): renamed `storeAs` kills
every `inSignal` on it — the names above are contracts; `.Killed` has no XML
precedent, `.Destroyed` is the attested suffix; there is no `Quest.Accepted`
signal — acceptance is `signalListenMode`; nothing after `QuestNode_End` runs
— all delayed consequences are GM-side; a def with `rootSelectionWeight 0`
and no incident never fires — the incident above IS the firing route; one
literal `[` blanks the whole description.

**GM handshake (arc spec §7's build surfaces):** the GM blackboard fires the
incident (bridge lane), then reads the outcome — Success/partial/Fail flags
and the betrayal flag — from the quest's end state via the same bridge lane,
and applies §6's Regard/exposure deltas in shadow mode first. The quest def
itself writes no blackboard number and stores no Regard anywhere in the save
(arc spec §0: never a stat in the save).

## 10. The skill's ten questions, answered

1. One sentence, no reward: §1's reason — surveys become garrisons, garrisons
   end salvage. **Yes.**
2. Two defensible answers: every verb against every other, and do-nothing
   against all of them, at high Heat especially. **Yes.**
3. Later acknowledgment: the arc itself is the acknowledgment — stage thaw,
   hum baseline, what gets offered next; plus the divergent §P letters.
   **Yes.**
4. Failable and survivable: failable four ways; all survivable — failure
   feeds a pressure track, not a game-over (full discovery is a separate,
   later, ruled outcome). **Yes.**
5. Reward proportional: silver deliberately slightly under; balance paid in
   Regard (§7, marked deliberate). **Yes, by design.**
6. Deadline real, enforced, shown: the survey window, `isQuestTimeout`,
   surfaced via `_duration`. **Yes.**
7. One sitting: the window is days, but each verb resolves in one sitting;
   the quest needs no cross-session memory. **Yes.**
8. Existing mechanics only: item delivery, bulk hauling, pawn lending, site,
   timer, signals. No new subsystem; the GM blackboard already exists.
   **Yes** (attack-attribution seam flagged in UNKNOWN).
9. Ask/reward/deadline findable in a glance: description names all three.
   **Yes.**
10. Firing route taken (route 2) and every conditional symbol has a fallback
    (§8 rule). **Yes.**

## UNKNOWN

- **Attack attribution:** whether vanilla signal vocabulary can distinguish
  "player destroyed the survey camp" from "a third party did" without a C#
  node (the `Unknown`-outcome row depends on it). Vanilla precedent unclear;
  if XML cannot, the cheap fallback is: any camp destruction pre-answer →
  `Fail`, and the GM layer, which can see who fought, refunds the exposure
  bump in shadow mode. Decide at build, against real shipped defs.
- **Lodger-style lending to a NON-asker faction camp** (verb 3): vanilla
  lodger machinery assumes the asker's shuttle/walk-out; whether it composes
  with a hostile-capable Empire site needs a corpus check
  (`references/vanilla_corpus.md`) before verb 3 is promised in the def.
- **Exact CQF-vs-pure-incident choice** inherits kyber spec §7's CQF caveat;
  route 2 is the ruling here for *shape*, the framework question stays with
  the arc's build item.

---

**Register note:** this spec is DESIGN. Nothing above is in-world knowledge;
no rumor of any of it circulates (same scoping law as the arc spec). Every
number above — days, unit counts, deltas, thresholds, refire caps, damping —
is **tunable** and marked so; registers (small/large/largest) are the design
content, constants are the GM tuning pass's.
