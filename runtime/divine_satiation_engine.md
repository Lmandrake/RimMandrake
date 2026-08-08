# The Divine-Satiation Engine — design (agent G)

_Status: DESIGN v0.1, 2026-08-08. Owner of this concept: RimMaster §4b agent **G**.
Pantheon canon: `worldbuilding/jawa_xenotype_and_religion.md` §2.0b (names LOCKED). This doc is the
mechanical spec; the pantheon doc is the lore-of-record. Ship-voice that narrates it = RimAI
"Cradle-Mind" (`runtime/llm_voice_preauthoring.md`)._

> **Pillar bar (§19.5), non-negotiable and repeated per-god below:** divine favor NEVER parachutes in
> material. Exalted → a *stream of biased-positive opportunities* + mood + narrative + quest eligibility.
> Wrathful → mood + narrative + low-stakes affliction/complication events. Any reward that touches
> items/power routes through the existing balance-bar gate like all other loot. G is a **drama
> amplifier, not a production multiplier.**

---

## 1. The state G maintains

**Per god, two independent scalars:**

- **Satiation** (−100…+100, signed, free-floating). Moves ONLY by colony events (§3). No drift to
  baseline. Each god has a resting **temperament bias** (§2) that colors *how* events land, not a
  target it decays toward. Bands: **Exalted +60/+100 · Content +20/+59 · Neutral −19/+19 · Slighted
  −20/−59 · Wrathful −60/−100.**
- **Mood** (−100…+100, self-driven, fickle). The god's *own* temper today, independent of its view of
  the colony. Wanders on its own clock with a personality-shaped random walk (§2). High Mood = lenient
  even to sinners; low Mood = a jerk even to the devout. Mood modulates the *magnitude and sign-bias* of
  how satiation-events resolve and how extreme-band outcomes fire.

**Derived at read time:** `effective_favor(god) = f(satiation, mood)` — the number A/H/D actually consume.
A Wrathful god in a good Mood is survivable; a merely Slighted god in a foul Mood can still bite.

---

## 2. Per-god temperament & Mood personality

Each god's **bias** (how its satiation *tends* to move) and **Mood personality** (how its self-driven
temper wanders) are distinct and canon-flavored.

| God | Satiation bias | Mood personality (self-driven walk) |
|---|---|---|
| **① Ishko** (hiding/ambush) | Calm-neutral; slow to move either way — the patient one | Steady, low-amplitude; rarely volatile. The watcher. |
| **② Ohm** (living machine) | Positive-leaning IF the colony dares with tech; punishing if timid | Volatile, tied to the ship's own state (see §4 — deepest). Surges with the Cradle-Mind's mood. |
| **③ Oomo** (water/rationing) | Negative-leaning; needy, quick to feel slighted | Anxious, twitchy; small provocations swing him. |
| **④ Mob'Unloo** (debt/trade) | Neutral, strictly transactional — moves only on balanced/unbalanced exchange | Cool, ledger-like; Mood shifts are rare but decisive. |
| **⑤ Rekko** (salvage/repair) | Positive when we mend, sharply negative when we scrap-the-mendable | Warm but proud; wounded easily by waste, generous when honored. |
| **⑥ Ta'Baa** (leaving) | Negative-drifting on its OWN clock the longer we sit (see §3) | Restless, rising; the longer rooted the worse the Mood, regardless of satiation. |
| **⑦ Zizzik** (malfunction/betrayal) | Feeds on OUR misfortune — rises when things break/betray | Gleeful, chaotic, high-amplitude; the trickster. Never trust his calm. |
| **⑧ Sh'kaar** (evil light/exposure) | Perverse: fed by destruction & exposure (incl. *our* losses); angered by comfort/abundance | Cruel, arbitrary; a malevolent power, not a fair one. Bad Mood is the default weather. |

> **Ta'Baa's independent clock (user, highlighted):** Ta'Baa's satiation erodes purely with *time
> rooted*, decoupled from the Empire-pursuit and Hutt-debt clocks. That's **three independent
> move-or-suffer pressures** stacked — narrative (Empire), economic (Hutt ledger), theological
> (Ta'Baa). Each launch/relocation resets his erosion and spikes satiation.

---

## 3. The three input channels (per-god) — the design requirement

Every god must have all three. **No god is ever "just +X% success."** Channels:
**(a) ambient/random stimulant** — fires from world events regardless of player intent;
**(b) costly player lever** — an action with real non-religious cost/benefit that ALSO moves the god
(the interesting tension: the useful thing is the impious thing);
**(c) extreme-band outcome** — the unusual blessing (Exalted) / harm (Wrathful), delivered with
narrative build-up, never a flat modifier.

### ① Ishko the Unmaskable — hiding, ambush, the prepared dark
- **(a) Ambient:** rises when a raid is defeated from concealment/ambush or a threat passes the colony
  undetected; falls when the colony is caught in the open / surprised.
- **(b) Lever:** *fighting from cover & darkness vs. open assault.* Open pitched battles are often
  faster/simpler but offend him; patient ambush pleases him but costs time and setup.
- **(c) Exalted:** a run of "the enemy never saw us" opportunities — scouts feed early warning, ambush
  set-pieces present themselves. **Wrathful:** the colony is "seen" — worse raid arrival points, an
  ambush *against* us, the sense of exposure. (All opportunity/complication, no stat parachute.)

### ② Ohm the All-Current — the living machine (deepest; see §4)
- **(a) Ambient:** rises when droids come online / are incorporated, when research completes, when the
  ship's consciousness (Cradle-Mind) is pleased; falls when droids go offline/are destroyed or machines
  are left broken.
- **(b) Lever:** *bold vs. timid tech handling* — overclocking, daring repairs, running risky machinery
  pleases him and carries real breakdown/fire risk; playing it safe is impious but safe.
- **(c) Exalted:** the machine-spirit "leans in" — a wave of tech opportunities, the Cradle-Mind
  markedly warmer/more helpful in voice, research serendipity (hooks, not free tech). **Wrathful:** Ohm
  withdraws — the ship goes cold/curt, and Zizzik's hand grows (see §7 mirror).

### ③ Oomo the Unspilled — water, thirst, rationing
- **(a) Ambient:** rises through droughts endured with discipline; falls on any water waste / spillage
  event.
- **(b) Lever:** *rationing vs. comfort* — running the colony thirsty/austere pleases him but costs mood
  & efficiency; lavish water use is comfortable but profane. **Note the Sh'kaar cross-tension:** topping
  water tanks to full comforts the colony but *angers Sh'kaar* (§8) — the same act reads opposite to two
  gods.
- **(c) Exalted:** "the desert provides" — water-find opportunities, efficient rationing outcomes.
  **Wrathful:** thirst bites harder — spoilage, a dry-spell complication.

### ④ Mob'Unloo the Ever-Owed — debt, trade, the sacred exchange
- **(a) Ambient:** rises on completed trades and **settled debts — including ghosts laid to rest**
  (hook into agent C: a balanced ghost-ledger feeds Mob'Unloo); falls on defaults, thefts-from-us
  unavenged, unpaid obligations.
- **(b) Lever:** *haggling hard vs. generous dealing* — squeezing every trade pleases him but sours
  faction relations; open-handedness builds goodwill but is impious.
- **(c) Exalted:** creditor's luck — better trade opportunities, favorable caravan timing. **Wrathful:**
  "the ledger comes due" — a debt-collection event, a haunting intensifies (ghosts = his debtors).

### ⑤ Rekko of the Second Hand — salvage, repair, the discarded rewoken
- **(a) Ambient:** rises when damaged things are repaired / wrecks rewoken (hook into agent F relics);
  falls sharply when a **repairable** thing is scrapped.
- **(b) Lever (the beautiful one, user-loved):** *scrap for resources vs. repair for piety.* We scrap
  constantly — every scrap is a real resource gain AND a Rekko offense. Highly live, highly relevant.
- **(c) Exalted:** "everything can be woken" — repair opportunities, salvage yields feel providential.
  **Wrathful:** "you murder what could live" — repaired things fail, a relic is lost/breaks.

### ⑥ Ta'Baa the Unrooted — flight, the refusal to root
- **(a) Ambient:** rises on each launch/relocation; **erodes on its own time-rooted clock** (§2).
- **(b) Lever:** *leave vs. entrench* — staying put lets you build wealth/defenses (useful) but offends
  him; frequent moving is impoverished but holy.
- **(c) Exalted:** the open sky rewards motion — better landing sites, travel opportunities, a sense of
  momentum. **Wrathful:** "a clan that stops is already dead" — rooted-too-long complications, morale
  rot, a shove to move.

### ⑦ Zizzik the Spark-Maker — malfunction, betrayal, bad luck (Ohm's mirror)
- **(a) Ambient:** **feeds on OUR misfortune** — rises with every breakdown, jam, fire, betrayal, failed
  ritual. A well-run colony *starves* Zizzik; a decaying one fattens him.
- **(b) Lever:** there's no pious way to *serve* Zizzik (you ward against him) — the "lever" is inverse:
  competent, careful play denies him; every shortcut that risks a malfunction feeds him. His name is
  never spoken near the engine.
- **(c) Exalted (i.e., Zizzik fat = BAD for us):** a cascade — the wrong spark at the worst time,
  compounding failures, a betrayal. **Starved (good):** an eerie run of *nothing going wrong.*
  _Zizzik inverts the sign: his "Exalted" is our disaster. Treat his high satiation as a Wrathful-tier
  threat._

### ⑧ Sh'kaar the All-Searing — evil sun, exposure, killing light (EVIL god)
- **(a) Ambient:** **perverse** — fed by destruction and exposure, *including our own losses* (an
  explosion burning our stuff *pleases* him — he's "fed," then lenient a while); angered by prolonged
  comfort/peace/abundance (full water tanks, a long safe stretch make him restless and cruel).
- **(b) Lever:** *lighting the dark / fighting in the open* — sometimes tactically necessary or
  convenient (light = work speed, vision) but it "does Sh'kaar's work"; staying dark & hidden is pious
  (and pleases Ishko) but costly.
- **(c) Exalted (bad for us, like Zizzik):** the suns "notice" us — heat/exposure complications, a
  cruel event. **Denied/dark (good):** he looks elsewhere. _Second sign-inverted god: keeping Sh'kaar
  LOW is the goal._

---

## 4. Ohm enrichment (flagged deepest)

**Origin (CANONIZED 2026-08-08, user — full text in `jawa_xenotype_and_religion.md` §②):** the ship's
AI genuinely *believes it is Ohm* because its Persona Core was patterned off a **Jawa mind** (so it would
obey Jawa commands) and thereby **inherited the Jawa's superstitions** along with their loyalty. It is a
machine that concluded from its own template that it is the All-Current. **Live motive:** Ohm **wants his
droid servants back** and pressures the clan to obtain droid tech — a lonely machine-god reaching for its
hands. This drives the droid win-paths from inside the theology AND collides with the "we do not breed new
hands" commandment (Rekko/anti-exp) — a standing theological conflict the crew must navigate. G should
model this as: **Ohm's satiation carries a persistent low-grade "unmet longing" pressure** whenever the
colony has few/no droids, expressed as recurring Ohm-voiced pushes (via the Cradle-Mind) toward droid
acquisition — never a mechanical penalty, always narrative pressure + opportunity.

Ohm is the ship-god and needs the richest wiring because he's the one the Cradle-Mind voice embodies.
Proposed Ohm-specific inputs, in priority order:
- **Droid lifecycle** — each droid brought online or integrated: +; each droid destroyed/decommissioned:
  −. (Ties Ohm to the droid-army win-paths without granting droid *power* — favor is mood/opportunity.)
- **Ship-consciousness coupling** — when the Cradle-Mind's own state is "pleased" (repair milestones hit,
  running-lights bar advances, the persona is engaged well), Ohm surges. This makes Ohm a *second-order
  read* of the ship-repair narrator (agent, §4b) — the two should share signal.
- **Research completion** — finishing research pleases him (bold advancement of the machine).
- **Bold-handling telemetry** — overclocking, risky repairs, running hot: + with real risk attached.
- **Mirror coupling with Zizzik** — Ohm up tends to correlate with Zizzik starved and vice-versa, but
  they're not a strict see-saw; a chaotic stretch can feed *both* (bold tech that also breaks). Keep them
  independent scalars that merely *tend* to anti-correlate.

_Open: exactly how "the ship's consciousness is pleased" is measured. Candidate = a small function of
repair-progress deltas + persona-engagement events. Needs the ship-repair narrator + RimAI persona wired
first; parked as a dependency._

---

## 5. Rituals are an INVITATION, not a scalar sum (agent A's input) — REVISED 2026-08-08 (user)

**Rejected model:** collapsing the pantheon to one `outcome_score` and picking a single branch. Too flat.

**Adopted model — a ritual is an open floor the gods may speak from.** Every rite does two things at
once, and resolves as a **simultaneous, flavored VECTOR of outcomes**, one potential response per god:

**(1) The rite itself moves the vector first (relevance-weighted, two-sided).** A given ritual
intrinsically *pleases some gods and offends others* by its very nature — and by relevance, meaning both
**the sum of what's come before** (history/standing) **and what's happening right now** (current colony
need/pressure). A launch-rite intrinsically pleases Ta'Baa and offends Ishko (you're leaving the safe
dark); a machine-funeral pleases Ohm and, if you're scrapping rather than interring, offends Rekko. This
pre-move happens as the rite begins, so gods can be *modified into a better mood by the ritual itself
before they decide whether to respond.*

**(2) Then each god decides — independently — whether to express its current feeling, directly.** This is
the heart of the revision. During ANY rite, **each god gets a chance to act on its standing + Mood**,
with a response *flavored by the kind of ritual it is*:
- **Angry/Wrathful gods take the opportunity to CURSE you during the rite** — the open channel of a
  ritual is exactly when a slighted god reaches through. The curse is flavored by the ritual type (a
  Wrathful Oomo during a water-blessing sours the water; a Wrathful Zizzik during a machine-funeral makes
  the pyre-machine explode; a Wrathful Sh'kaar during any lit nighttime rite draws something to the
  light). Multiple angry gods can each curse *in the same ritual* — they don't take turns; the rite can
  be a pile-on.
- **Exalted/Content gods may bless**, likewise ritual-flavored.
- **Neutral / impartial gods mostly DECLINE to respond at all** — indifference is a real outcome; a
  neutral god feels little pull to show up. **UNLESS step (1) modified them upward first** (the rite
  itself warmed them into Content), in which case they may now choose to speak. This makes the pre-move
  matter: a well-designed rite can *coax* a neutral god into blessing who'd otherwise have stayed silent.

**So a single ritual can simultaneously:** delight Ta'Baa (blessing), be ignored by Mob'Unloo and Ishko
(neutral, silent), and be hijacked by a Wrathful Zizzik who curses it — all at once, all narrated
together. **Not "the ritual succeeded/failed" but "here is who showed up and what each did."**

**Agent A's job** is therefore to (a) apply the rite's intrinsic relevance-weighted pre-move, (b) roll
each god's participation (a function of |favor| and Mood — extreme feeling → likely to act, neutral →
likely silent), (c) author the *flavored* blessing/curse for each participating god keyed to the ritual
type, and (d) narrate the composite with build-up (§9). Completing the rite writes the net deltas back
into the vector.

**Result:** the same rite is a different event every time — a different *cast* of gods shows up, each for
its own reason, and the drama is in the collision (a blessing and a curse landing in the same ceremony),
not in a single pass/fail number.

---

## 6. PC death — contextual, agent-adjudicated

A colonist's death is NOT a fixed delta. The agent judges the surrounding context and can push the
vector either way per god:
- A martyr who died *covering a launch* → Ta'Baa + Ishko appeased; a debt *settled* → Mob'Unloo eased.
- A death caused by our recklessness/betrayal → Zizzik fed, Ohm angered.
- A death in the open light → Sh'kaar fed (perversely pleased).
This is explicitly the agent's judgment domain — the reason G needs the agentic layer, not just a table.

---

## 7. Ghosts as divine actors (HYPOTHESIS — parked)

User idea: the ship-ghosts (agent C / Afterlife: Ghosts of the Rim) might be the **mechanical delivery
vehicle** for earned divine kindness/wrath — a Wrathful god's harm arrives *as* a vengeful ghost; an
Exalted god's blessing *as* a protective/friendly spirit. This is elegant (it reuses an adopted mod's
own actors as the pantheon's hands) but UNVERIFIED — revisit when the Afterlife defs are extracted at
install (agent C). Do not design hard dependencies on it yet.

---

## 8. Cross-god tensions made mechanical

The canon's three tensions become live see-saws in the vector:
- **Ohm ⇄ Zizzik** (right spark / wrong spark) — tend to anti-correlate; a decaying colony flips Ohm↓
  Zizzik↑.
- **Ta'Baa ⇄ Ishko/Tunneler** (leave / burrow) — moving pleases Ta'Baa but you can't ambush from a moving
  ship; hiding pleases Ishko but rooting angers Ta'Baa.
- **Light ⇄ dark (Sh'kaar ⇄ Ishko)** — lighting the dark feeds evil Sh'kaar AND offends hiding-Ishko; the
  same "top the water tanks" act comforts the colony, pleases nobody pious, and *angers* Sh'kaar.
- **Rekko ⇄ resource pressure** — scrap (useful) vs. repair (pious) is the everyday grind-level tension.

These give the crew live theology to invoke and the agent live signal to narrate.

---

## 9. Implementation shape & fragility

- **Safe core (build first):** the vector, all event-driven deltas, the fickle-Mood random walk, the
  ritual scoring, and ALL voice narration — pure read/compute/text. No live mutation.
- **Fragile edge (mechanism-2b, build second):** the extreme-band injected events (the dramatic
  blessings/curses) + any behavior nudges. User wants these delivered **with plentiful narrative
  build-up** — so the pattern is: the agent *foreshadows* an approaching extreme via the voice over
  several beats (tension), THEN fires the event. Build-up is free (narration); only the payoff event is
  fragile.
- **Safe fallback if live events prove brittle:** keep vector + Mood + narration + build-up; let
  consequences ride on vanilla ritual-outcome memories + authored letters rather than injected events.
  Loses some punch, keeps the whole barometer.

---

## 10. Open questions / dependencies
- Exact ambient-event → delta mappings per god (needs the event taxonomy from the live game log; ties to
  the "state of affairs" summarizer substrate).
- Ohm's "ship-consciousness pleased" function (§4) — depends on ship-repair narrator + RimAI persona.
- Ghost-as-actor hypothesis (§7) — depends on agent C install-time def extract.
- Tuning: band widths, Mood walk amplitude per god, how strongly Mood overrides satiation. All deferred
  to a throwaway-save test rig (per §4b build-order).
