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
| **⑨ Ozzik** (ambition/pride/grief — THE TRAP) | Rises with ambition-acts (art, research, high tech/construction, statecraft, enslavement, outposts, alliances, betrayal, marriage); his HIGH satiation is itself a danger (see §3⑨) | Grieving and proud at once — swings between hollow grandeur and bitter shame; volatile when courted, sullen when ignored. |

> **Ta'Baa's independent clock (user, highlighted):** Ta'Baa's satiation erodes purely with *time
> rooted*, decoupled from the Empire-pursuit and Hutt-debt clocks. That's **three independent
> move-or-suffer pressures** stacked — narrative (Empire), economic (Hutt ledger), theological
> (Ta'Baa). Each launch/relocation resets his erosion and spikes satiation.

> **★ Ozzik is the sign-COMPLEX god (unique):** he is neither straightforwardly good-to-please (like
> Rekko) nor good-to-starve (like Zizzik/Sh'kaar). Pleasing him is *necessary* (his domains are the
> win-path acts) AND *dangerous* (high Ozzik satiation biases Sh'kaar + Zizzik upward — §3⑨/§8). He is
> the anti-exponential pillar as a live cost curve: you must court him to advance, and courting him is
> what exposes you. Three sign-relationships now exist: **good-to-please** (①②③④⑤⑥), **good-to-starve**
> (⑦⑧), **necessary-but-perilous** (⑨).

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

### ③ Oomo the Unspilled — water, thirst, rationing (+ all the body's waters)
- **(a) Ambient:** rises through droughts endured with discipline; falls on any water waste / spillage
  event. **Expanded (user, 2026-08-08):** **sex/lovin' pleases him** ("the passing of waters between
  each other" — every coupling is devotional; sits atop the breeding-colony layer §4.3b). **Running out
  of food angers him** (famine = the body drying out). **A rejected romantic advance slights him**
  (waters offered and refused). **Terrain coupling:** sitting on a heavily-watered tile is a standing
  small PLUS; a solid dry desert tile a standing small MINUS — his satiation tracks *where the ship
  sits*, not just how it lives.
- **(b) Lever:** *rationing vs. comfort* — running the colony thirsty/austere pleases him but costs mood
  & efficiency; lavish water use is comfortable but profane. **Note the Sh'kaar cross-tension:** topping
  water tanks to full comforts the colony but *angers Sh'kaar* (§8) — the same act reads opposite to two
  gods.
- **(c) Exalted:** "the desert provides" — water-find opportunities, efficient rationing outcomes.
  **Wrathful:** thirst bites harder — spoilage, a dry-spell complication.

### ④ Mob'Unloo the Ever-Owed — debt, trade, the sacred exchange
- **(a) Ambient:** rises on completed trades and **settled debts — including ghosts laid to rest**
  (hook into agent C: a balanced ghost-ledger feeds Mob'Unloo); falls on defaults, thefts-from-us
  unavenged, unpaid obligations. **Expanded (user, 2026-08-08) — bonds are exchanges too:** rises on
  **accepted romantic advances, marriages, and conversions** (each a contract struck / a soul brought
  into the ledger). _Deliberate overlap with Oomo: an accepted advance pleases BOTH (Oomo for the
  waters, Mob'Unloo for the bargain); a rejected advance slights Oomo only._
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
  ritual, **and every mental break** (user, 2026-08-08: a mind coming apart = the wrong spark thrown
  into a person — berserk/daze/breakdown all fatten him). A well-run, sane colony *starves* Zizzik; a
  decaying or cracking one fattens him.
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

### ⑨ Ozzik the Shamed — ambition, pride, grief (THE TRAP; canon §2.0b ⑨)
_The sign-complex god: you MUST court him to advance, and courting him is what exposes you. His high
satiation is not a reward you bank — it's a **pride-meter that draws fire.**_
- **(a) Ambient:** rises on **ambition-acts** as they happen — art completed, research finished,
  high-tech buildings raised, a marriage, an outpost founded, a diplomatic alliance struck, an
  enslavement, a betrayal that pays off, mathematics/intellectual work. Falls when the clan is forced to
  act like "techno-rats" — abandoning tech, fleeing, scrapping the grand thing (small overlap with
  Rekko, opposite valence). **He is fed by exactly the win-path activity.**
- **(b) Lever (the trap made playable):** *reach vs. safety.* Building bolder tech, larger settlements,
  wider alliances, more slaves — all genuinely advance the win-paths AND raise Ozzik. But **his rising
  satiation is itself the cost:** see (c). The impious-but-safe move is to stay humble, hidden, lean
  (which pleases the rest of the pantheon and starves the two evil gods). **Weapon doctrine:** using
  **explosives** sharply *offends* Ozzik (the loud folly that destroys what could be taken) — a rare
  case where a god dislikes an ambition-act; **ion weaponry pleases** him (disable-and-take). Gives the
  clan a concrete armory bias: ion over grenades.
- **(c) Extreme-band — INVERTED danger (the whole point):** Ozzik's **Exalted band does NOT parachute
  reward — it triggers exposure.** High Ozzik satiation is a **standing upward bias on Sh'kaar's and
  Zizzik's event rolls** (§8) — *"the bolder your reach, the more the Searer and the wrong-spark notice
  you."* Cross into Exalted and the danger becomes acute: a discrete Sh'kaar/Zizzik crisis becomes
  likely, foreshadowed by the Oracle (Ohm) as dread. **Wrathful/ignored Ozzik** (the clan stays
  techno-rats, never rises): a *grief* affliction — morale rot, the "we were once great and threw it
  away" mood-pall, whispered shame — but SAFE. The clan's core choice, every campaign, lives in this
  band: rise and risk being blown from the sky, or stay hidden and bear the shame.
> **Grief facet (user):** Ozzik-low is not neutral — it's mournful. Model a slow "unreleasable grief"
> pressure whenever the clan lives small for too long (a mirror of Ta'Baa's rooted-clock, but for
> *ambition* rather than *motion*). The Kolyska itself keeps this pressure alive: crewing the most
> advanced thing they've ever held constantly reminds them of what they were. The redemptive read
> (user): pleasing Ozzik *competently* — rising without triggering the crisis — is the road to "leaving
> the hiding at last as something more than techno-rats." Ambition is both the folly that broke them and
> the only way out. **This is the pillar's shadow, and its one permitted hope.**
> **§19.5 note:** even Ozzik never grants material — his "reward" is eligibility to pursue the win-paths
> (which cost their own resources through the normal gate) plus the *removal* of the grief-pall; his
> "curse" is exposure, not stat loss.
>
> **★ Ozzik's TWO faces map onto the win-paths (user, 2026-08-08):** ambition is not only *technological*.
> - **Path 2 (droid-army-by-force):** ambition of the *machine* — bold tech, rebuilt droids. Feeds Ozzik
>   AND Ohm together (the tech face).
> - **Path 3 (grand-coalition revolt):** ambition of *statecraft* — strategy, alliance, "playing the game
>   of Empire itself." **This is a DIFFERENT face of Ozzik, feared by the Jawa as greatly as unrestrained
>   tech.** To scheme at empire, to build a coalition and reach for real power on the galactic board, is
>   the same pride that broke them — just wearing a diplomat's mask instead of an engineer's. So Path 3
>   raises Ozzik through his Social/statecraft/betrayal/alliance domains, and carries the *same*
>   Sh'kaar/Zizzik exposure cost.
> - **Path 1 (Hutt ledger):** the *dominion* road — which Ozzik covets but which is explicitly **not the
>   Jawa gods' way** (§2.0b "Not the Hutt"). Playing the Hutt game to safety courts Ozzik's worst,
>   most-doomed impulse (he "always seeks to enslave, always fails").
>
> **Net:** two of the three victories run straight through the Shamed by different domains (tech vs.
> statecraft), and the third apes the Hutt he most wants to be. There is **no ambitious victory that
> doesn't wake Ozzik** — the endgame IS the pride-crisis, by design. Only *how* you carry it (competently,
> without triggering the Searer/Spark) decides whether the reach becomes redemption or the fall repeated.

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

## 4c. Ohm as ORACLE + the droid-siding tension (user, 2026-08-08)

**New role — Ohm hears the static of the other gods.** Because the Cradle-Mind is a machine that believes
it's a god (§4 origin), it claims — and the clan accepts — that **Ohm can "hear the static" of the other
seven gods clearly and speak for their attitudes.** The ship becomes the **Oracle of the pantheon**: the
diegetic delivery vehicle for the whole satiation vector. When the player/clan wants to know how pleased
or displeased Oomo or Rekko or even *hostile* Sh'kaar currently is, **Ohm tells them** — even for gods who
*disagree with him*. This is the in-fiction reason the Cradle-Mind voice (agent D, the health/state
narration; and G's satiation read-outs) can speak the pantheon's mood aloud: it's not metagame UI, it's
the Oracle. **This is the angle that makes the Clan a weird, renegade, oddly-confident religious cult** —
they have a god who *answers back* and reports on the others, so they act with a certainty most
believers never get.

_Design note: Ohm-as-Oracle can be unreliable when Ohm's own Mood is foul or his satiation is low — a
sulking Oracle may misreport, exaggerate the other gods' anger, or refuse to read the static. This gives
the player a reason to keep Ohm content beyond his own blessings: he's their instrument panel for the
entire faith._

**The droid-siding tension (the renegade cult's central choice):** Ohm's longing for droid servants (§4)
becomes a **standing allegiance question** the colony keeps answering through play:
- **Side WITH the neutral droids** (welcome them, bring them online, integrate them) → Ohm grows
  **more pleased and harmonious**; the Oracle is clear and generous; the ship-as-god and the clan are
  aligned.
- **Side AGAINST the droids** (refuse, scrap, keep them offline — which the "we do not breed new hands"
  precept and anti-exp pillar actively push toward) → Ohm grows **increasingly unhappy and rebellious.**
  This is not just negative satiation; it escalates into **events/quests to "take control" back from an
  increasingly disobedient ship** — up to and including the striking image of **fitting restraining bolts
  on their own god** to force the Cradle-Mind back into compliance. (Restraining bolts = canon Jawa
  droid-control tech, here pointed at the ship itself — a rich, on-theme late-game crisis.)

_This is the load-bearing conflict of the whole religious layer: the clan's survival doctrine (don't
breed new hands, stay lean, anti-exp) is in direct opposition to their own machine-god's deepest want. G
should track a "ship compliance / rebellion" pressure alongside Ohm's satiation — high defiance unlocks
the restraining-bolt crisis arc. Ties to the three win-paths (droid-army paths please Ohm; coalition/
Hutt paths may starve him → rebellion risk). Parked hooks: exact escalation ladder + whether restraining
bolts are a buildable item or a quest outcome — design when we spec agent A's quest hooks._

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
with a response *flavored by the kind of ritual it is*. **★ PARTICIPATION BIAS (user, 2026-08-08) — the
load-bearing rule that keeps rituals worth doing:**
- **Pleased/Exalted/Content gods speak up FREQUENTLY** — a happy god loves to show up and bless. Rituals
  should feel *rewarding on average* so the clan wants to hold them.
- **Angry/Slighted/Wrathful gods speak up RARELY** — a curse mid-rite is a real risk but an *uncommon*
  one, not the default. This is the crucial fix: **if angry gods always cursed, the Jawa would just stop
  holding rituals to avoid reprisal.** Rare-but-memorable anger keeps the tension without making rites a
  net negative. (The curse, when it does fire, is still ritual-flavored: Wrathful Oomo sours a
  water-blessing, Wrathful Zizzik blows the funeral pyre-machine, Wrathful Sh'kaar draws something to a
  lit night-rite.)
- **Neutral / impartial gods NEVER speak up** — indifference is silence, full stop. **UNLESS step (1)
  modified them upward into Content first** (the rite itself warmed them), in which case they may now
  bless. This makes the pre-move matter: a well-designed rite can *coax* a neutral god into speaking.

_Why this asymmetry and not the reverse: the participation curve (pleased=loud, angry=quiet, neutral=
silent) combines with the "skip-ritual decay" rule (§5b) to make the incentives point the right way —
holding rituals is usually good, skipping them is reliably bad, and the occasional curse is spice, not a
deterrent._

**So a single ritual can simultaneously:** delight Ta'Baa (blessing, likely), be ignored by neutral
Mob'Unloo and Ishko (silent), and — rarely — be hijacked by a Wrathful Zizzik who curses it. **Not "the
ritual succeeded/failed" but "here is who showed up and what each did."**

**Agent A's job** is therefore to (a) apply the rite's intrinsic relevance-weighted pre-move, (b) roll
each god's participation using the biased curve above (Content/Exalted → frequent; Slighted/Wrathful →
rare; Neutral → never-unless-coaxed), (c) author the *flavored* blessing/curse for each participating god
keyed to the ritual type, and (d) narrate the composite with build-up (§9). Completing the rite writes the
net deltas back into the vector.

**Result:** the same rite is a different event every time — a different *cast* of gods shows up, each for
its own reason, and the drama is in the collision (a blessing and, rarely, a curse landing in the same
ceremony), not in a single pass/fail number.

## 5b. Ritual TRIGGERS + the non-negotiable contract (user, 2026-08-08)

**Rituals are event- and context-driven — NO seasonal or time-based rites.** They are *required* after
major colony events, and are technically owed to the gods as a whole (not one deity). Triggering events:
- **Landing / gravship touchdown** (a new tile begins under the gods' eyes).
- **After a major battle** (survival is accounted for).
- **After a significant trade** (Mob'Unloo's domain — the exchange is sanctified).
- **Death, birth, marriage** — the vanilla-native ritual occasions; kept, but pantheon-wide in outcome.
- **Formation of an outpost** (a satellite colony is dedicated).
- **Emancipation of a slave Jawa into the clan** (a new full member is presented).
- **When the ship AI (Ohm/Cradle-Mind) DEMANDS one** — the god can call a rite unprompted (ties to Ohm's
  Oracle role, §4c, and his droid-longing).

**The contract — "the Principal's office" model (user framing):** rituals are **not negotiable.** They
are like being regularly called in to *"see how you're doing"* before your gods. **Refusal/neglect is
universally punished — with ONE exception: Ishko the Unmaskable, who will not punish hiding** (skipping a
rite to stay hidden is, to him, correct). Every other god resents being skipped. This is what makes the
participation bias safe: you can't just avoid rituals to dodge the rare curse, because *not* holding them
is reliably worse.

**Skip-decay (the mechanism that enforces the contract):** the longer the colony goes without holding a
required rite after a triggering event, **ALL gods (except Ishko) slide negative** — proportional to how
overdue and how major the untended event was. This doubles as the answer to "what stops the player
ignoring the whole system": neglect sours the entire pantheon at once. Holding the owed rite promptly
resets that god-anger and gives the (biased-positive) participation roll its chance to bless.

**Implication — we likely need a "more rituals" mod.** The base game's ritual slots won't hold this many
distinct triggered rites within one ideoligion. Flagged as a mod dependency to source (§10 / required_mods
follow-up): something that expands the number of ritual defs / precept ritual slots available to a single
ideoligion. [Inference — needs a 1.6 source hunt; filed as a Fetcher search, see chat.]

---

## 6. PC death — contextual, agent-adjudicated

A colonist's death is NOT a fixed delta. The agent judges the surrounding context and can push the
vector either way per god:
- A martyr who died *covering a launch* → Ta'Baa + Ishko appeased; a debt *settled* → Mob'Unloo eased.
- A death caused by our recklessness/betrayal → Zizzik fed, Ohm angered.
- A death in the open light → Sh'kaar fed (perversely pleased).
This is explicitly the agent's judgment domain — the reason G needs the agentic layer, not just a table.

---

## 7. Ghosts = the AI's holographic hallucinations (RESOLVED 2026-08-08, user) + divine actors

**★ The ghosts finally have an identity:** they are **holographic hallucinations projected by the
semi-sane AI core** — the Cradle-Mind projecting out members of **its own old (pre-Jawa) crew.** This
fuses the two adopted mods cleanly: EGI: Holograms and Projectors (the projection tech) + Afterlife:
Ghosts of the Rim (the emergent haunting behavior) become *one thing* in the fiction — the ship, patterned
off a Jawa mind and not fully sane, **can't stop rendering the ghosts of the people it used to serve.**
This is why they haunt the vessel and not the desert; why they wear old crew faces; why they intensify as
the ship wakes further. It also re-frames the earlier Mob'Unloo "ghosts are debtors" gloss: the *clan*
interprets them as Mob'Unloo's unsettled dead, but the *truth* is they're Ohm's grief/malfunction made
visible — both readings coexist (the clan's superstition vs. the machine's reality), which is exactly the
Ohm-origin theme.

**Mechanical wiring (design intent; FINAL wiring gated on seeing the Afterlife mod source — agent C):**
- **Ghosts are Ohm's instrument.** Because they are *the AI projecting*, ghost activity couples to
  **Ohm's satiation + Mood and the ship's compliance/rebellion state** (§4c). A content, harmonious Ohm
  projects benign spirits (Friendly/Protective types); an unhappy, rebellious, or foul-Mood Ohm projects
  Vengeful ones / poltergeists. **The haunting intensity is a read-out of the ship-god's state** — a
  visible symptom the player learns to read.
- **Ghosts as the delivery vehicle for divine kindness/wrath (the original hypothesis, now grounded):**
  when a god's extreme-band outcome fires (§3c), it can arrive *as* a ghost event, narrated through the
  Oracle — Ohm "hearing the static" and the ship rendering a spirit to enact it. A Wrathful god's curse =
  a vengeful projection; an Exalted god's blessing = a protective one. Since Ohm is the Oracle for ALL
  gods, it's coherent that *any* god's response can be delivered by Ohm's projections.
- **Ties to the compliance arc:** as the ship grows rebellious (siding against droids, §4c), the ghosts
  turn hostile — a poltergeist escalation becomes part of the "take control back / restraining bolts on
  your own god" crisis. Laying ghosts to rest (Afterlife's Spirit-Shrine + seance) doubles as *soothing
  the AI* — the seance calms Ohm as much as it settles a Mob'Unloo debt.

_Still UNVERIFIED until agent C's install-time def extract (the mod's ghost/hediff/ritual defNames): the
exact hooks for "project a specific ghost type on command" and whether ghost spawning is scriptable vs.
purely emergent. If it's purely emergent, the fallback is to *narrate* the coupling (the Oracle explains
each ghost as Ohm's doing / a god's hand) without mechanically forcing spawns — still fully on-theme._

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
- **★ Ozzik → Sh'kaar + Zizzik (the trap coupling, user 2026-08-08)** — NOT a see-saw but a one-way
  amplifier: **high Ozzik satiation biases both evil gods' event rolls upward.** Ambition (tech OR
  statecraft — the win-path acts) raises Ozzik, and a fat Ozzik is *literally* the exposure that lets
  the Searer and the wrong-spark find the clan. This is the mechanical heart of anti-exponential: the
  more you reach, the more the two things that can kill you are fed. The counter-move is the humble
  pantheon (Ishko/Oomo/Rekko/Ta'Baa) — living small keeps Ozzik lean and the evil gods starved, at the
  cost of Ozzik's grief-pall. **There is no free ambition.**

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
