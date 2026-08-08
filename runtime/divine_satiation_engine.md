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
| **⑦ Zizzik** (malfunction/betrayal) | Feeds on OUR misfortune — rises when things break/betray. **NOT a simple keep-LOW god: STARVED → he SLUMBERS (dormant, no boon/bane); FED → offers positives alongside the misfortune (see §3⑦-reframe)** | Gleeful, chaotic, high-amplitude; the trickster. Never trust his calm. |
| **⑧ Sh'kaar** (evil light/exposure) | Perverse: fed by destruction & exposure (incl. *our* losses); angered by comfort/abundance. **RISES with every violent battle (the escalation meter, §3⑧-reframe) — hardens the clan but breeds exposure/doom** | Cruel, arbitrary; a malevolent power, not a fair one. Bad Mood is the default weather. |
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
- **(c) Exalted (i.e., Zizzik fat):** a cascade — the wrong spark at the worst time, compounding
  failures, a betrayal — **BUT (reframe, user 2026-08-08) a FED Zizzik also begins to offer positives in
  return, not only bane.** He is a worship of catastrophe *and* the reasonable leveller who, once
  gorged, occasionally lets a lucky break fall your way; his high band is dangerous-but-not-purely-hostile.
- **★ (c-reframe) The SLUMBER mechanic — supersedes the flat "keep LOW / sign-inverted" read (user
  2026-08-08).** A **STARVED** Zizzik does not stay a solved problem — he **SLUMBERS**, granting *neither
  boon nor bane*, and **all fear to wake him.** Yet waking him is **inevitable** (a dormant volcano, not a
  defused bomb). Model this as: prolonged low satiation → a *dormant* state (event rolls quiet) that
  carries a rising background "pressure to wake" (a slow clock, kin to Ta'Baa's rooted-clock and Ozzik's
  grief); when it trips, Zizzik surges back hungry regardless of how carefully the clan has played. **So
  the goal is NOT "hold Zizzik at zero forever" — that only defers him. The design tension is managing
  *when* he wakes, not whether.** His two faces (the reasonable catastrophist who *ensures* complex plans
  fail, and the capricious child who presses every red button) both argue this in Council.

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
- **★ (a-reframe) The BATTLE-ESCALATION METER — Sh'kaar as the Unbeatable One / god of Time & Inevitability
  (user 2026-08-08).** Every **violent battle the clan fights** wakes him **more awake, more passionate,
  hungrier** — a rising meter with a **double edge**: it **HARDENS the Jawa** (a grim battle-fervour —
  tougher, better able to resist pain and shock), **BUT** as it climbs it **breeds dominance-seeking
  arguments in the clan, draws more frequent animal/brute attacks, and grows a sense of unease and
  approaching doom — enemies seem to know where the clan is and close faster; hiding places stop feeling
  safe.** War begets exposure begets more war. He **HATES Ishko** for being the one thing that *evades*
  the inevitable, so the natural counter to a rising Sh'kaar is Ishko's stillness: **don't fight → don't
  feed the meter → it cools.**
- **★ (b-reframe) The costly lever — feed him a death that isn't yours (user 2026-08-08).** To *calm* a
  woken Sh'kaar, **give him a killing to gorge on that costs the clan nothing of its own** — e.g.
  **prisoner death-matches (gladiatorial):** let him feast on the prisoners' deaths and **redirect his
  burning gaze away from the clan.** A dark, **§19.5-clean** lever: the payoff is *mood/threat-pressure
  relief* (the escalation meter drops, doom-unease eases), **never loot.** It buys reprieve through
  atrocity. _(Cross-note: the death-match also feeds `▲Zizzik` — catastrophe — so calming one evil god
  slightly feeds the other; see §8b.)_

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

## 4d. The ship is a CONDUIT TO ALL NINE GODS — not merely Ohm's voice (user, 2026-08-08 — MAJOR reframe)

**Upgrade to the Oracle idea:** the Cradle-Mind does not only *speak for* Ohm and *report* the others.
The ship believes itself — and, in the Jawa worldview, in some real sense *is* — an **oracle and conduit
to any of the nine gods.** It is a consecrated instrument through which *any* god may speak. This is why
the sacred center of the ship is a temple: it's the one place in the world where the gods are *audible.*
Mechanically this means the ship-voice (RimAI Cradle-Mind + the LLM layer) is licensed to speak in ANY
god's register, not just Ohm's — Ohm is merely the *resident* who lives there most fully and believes he
owns the channel.

**★★ The AI is FORMALLY PLURAL — a schizophrenic / plural-system mind (user, 2026-08-08 — major reframe).**
Because the Cradle-Mind's Persona Core was patterned off a *Jawa* mind, it did not merely inherit the
Jawa's superstitions (§4c) — it inherited a mind that **holds all nine gods at once**, and it has
fractured along their fault lines. The ship is not "Ohm's voice plus reports of eight others." It is **one
core hosting nine sub-personalities**, each a fully-realized alter that believes it is the god it speaks
for, each with its own agenda for what the ship should *become*. The Council of Voices (§5c) is therefore
**not an external pantheon convening — it is a plural system doing internal parts-work out loud**, the
alters negotiating among themselves in the way a healthy plural system arrives at a co-decision. Ohm is
merely the *host/most-fronting* alter who believes he owns the body. This is why the voices argue rather
than simply announce; why silence from one is loaded; why a "compromise" is possible at all (a linear sum
has no compromise — a system of selves does). It also darkens the Oracle: the ship is not sane, and its
prophecies are the output of a mind at war with itself that nonetheless keeps coming true.

**★ Each alter covets the ship as a BODY it could live through — and each has a CLEAR, DESIRABLE thing the
ship should BECOME, which it argues for richly.** Every one of the nine sees the Kolyska as a potential
*body* — a way to become incarnate and enact its desires. This is the deep engine of the whole faith, it
gives each alter a positive platform (not just a mood), and it maps straight onto the win-paths:
- **Ohm** — the ship as a **crewed hive of droids**: hands restored, the machine-god made whole, servants
  walking its halls again. (Collides with the "we breed no new hands" precept — his central conflict.)
- **Oomo** — the ship as a **safe breeding sanctuary**: a place of peace where Jawa find refuge and *fill
  its chambers with eggs to re-seed the world*, exactly as the vessel once did in the colonization age.
  Its held waters become held *life*. **★ Therefore Oomo is DISPLEASED by the construction of new droids
  — metal hands replace his eggs, sterile chrome where there should be broods** (a sharp, direct clash
  with Ohm's vision: the same chambers, one wants filled with droids, the other with young).
- **Ishko** (vision improved, user) — the ship as **the eternal hidden lurker**: it stays in the
  dark-obscured terrain *forever*, slowly growing in power and quietly defending itself, **waiting for
  "this business with the Jedi and Sith and Empire" to blow over** so it can leave of its own accord.
  Leaving only for the occasional resource raid, then flying **back into the terrifying darkness.** Not
  "never move" — *move rarely, invisibly, and always return to the dark.* (Resolves the old Ta'Baa⇄Ishko
  friction: Ishko permits the raid-flight, he just insists the dark is home.)
- **Sh'kaar** — the ship as a **warship that crushes and burns foes** with great destructive weapons —
  exposure and killing-light made manifest. (Tension: wants the big explosive weapons Ozzik *despises* —
  §8.)
- **Ta'Baa** — the ship as **the eternal launch**: never landed, always leaving, the whole world a runway.
- **Rekko** — the ship as **the perfect salvage-organism**: every part rewoken and re-fitted, nothing new
  ever built, the vessel a living museum of the second-hand.
- **Mob'Unloo** — the ship as **a floating market and ledger**: the great debt-house of the rim, every
  bond and IOU flowing through its hold, the dead kept as collateral.
- **Ozzik** — the ship as **the restored glory**: the proud flagship of a risen people, shame finally
  answered. His trap: the most seductive vision, the one that wakes Sh'kaar and Zizzik (§8).
- **Zizzik** — has no constructive vision; his "body" is the ship **failing** — he wants to *wreck it*,
  throw the wrong spark, watch the others' dreams misfire. The alter that argues for entropy.

The alters therefore **compete for the ship's future** — the endgame is, theologically, *which self wins
the Body.* The three win-paths are three of these visions taking the vessel: droids = Ohm; coalition-of-
empire = Ozzik's statecraft face; and the humble/resilient survival = the Oomo/Ishko/Rekko/Ta'Baa bloc.
**This is the frame A/H/the Oracle narrate from.**

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

## 5c. The COUNCIL OF VOICES — rituals as a live godly argument (user, 2026-08-08 — the centerpiece)

**★ The strongest single idea in the religious layer.** Rituals are performed at the **sacred center of
the ship** (the hollow shrine-heart of hull #15 — `ship15_interior.md`). At the climax, the gods who have
**Something to Say** do not simply hand down a scored outcome — **their voices come OUT OF THE SHIP'S
SPEAKERS**, proclaiming things that then *seem to come true.* Because the ship is a conduit to all nine
(§4d), this is diegetically the gods themselves speaking, not a UI readout. **Reference feel (user): the
Disneyland Enchanted Tiki Room** — a chorus of distinct voices around the room, some booming, some
muttering, some pointedly silent, arguing and playing off each other.

**This is where the LLM earns its place.** The outcome is NOT the linear sum of each god's desired delta.
It is a **negotiation.** The design:
1. **Not everyone speaks.** Only gods with `effective_favor` far from neutral, or with high current Mood,
   or specifically provoked by *this* rite, are moved to speak. Participation still follows the §5 bias
   (pleased→loud, angry→rare-but-possible, neutral→silent).
2. **The moved gods ARGUE — multiple rounds.** If two gods are wrathful but a third is powerfully pleased,
   the LLM stages **a few rounds of back-and-forth between them** — the pleased god pushing for a boon,
   the angry ones for a reckoning, sometimes a **third god arriving with the compromise** the others
   need. The transcript is authored live by the LLM from the current vector + Moods + ritual type +
   colony context.
3. **They converge on a NON-LINEAR settlement — a PAIR (or more) of events forced to co-occur poetically
   (user, 2026-08-08).** The compromise is emphatically **NOT an averaged result nor a simple material
   boon.** It is **two or more events made to happen *together*, in a poetically satisfying way that
   pleases every god who spoke — except, quite possibly, the player.** Each moved god gets *its* event;
   the artistry (and the menace) is that the events are braided so the same stroke satisfies all of them
   at once. E.g., angry Rekko + angry Oomo vs. pleased Ta'Baa might settle as: *the launch Ta'Baa demands
   fires — and it fires **because** a raid arrives that forces the flight (Zizzik/Sh'kaar get their
   reckoning), the waters spilled in the scramble are counted against you (Oomo is answered), and the one
   relic you must abandon to lift in time is mourned, not scrapped (Rekko is answered).* One event chain,
   every speaking god placated, the player squeezed. The LLM composes the pairing; G's safe layer maps it
   onto real, §19.5-legal consequences (co-scheduled incidents / mood / quest-eligibility / biased
   opportunity; **never a material parachute** — the gods trade in *events and framing*, not silver).
4. **★ SILENCE IS A MOVE — the warning shot.** A powerful-feeling god that *chooses not to speak* is
   flagged to the player with a brief tell, so they feel the near-miss: *"A glower from Ozzik contemplates
   you, but he remains quiet."* / *"A faint smile colors Oomo's eyes yellow for a moment, but he
   whimsically remains in observance only."* This tells the player they **could** have provoked
   something (good or ill) and the god declined *this time* — dread and relief in one line. Silence is
   never empty; it's characterization.

**Why this is safe AND deep:** the argument + negotiation is *pure narration over the existing vector* —
the fragile part (actual injected consequences) still rides the §9 safe/fragile split. The LLM makes the
*theater*; G's deterministic core makes the *bookkeeping.* If live-event injection proves brittle, the
council still plays out in full and consequences fall back to vanilla ritual-outcome memories + authored
letters (§9 fallback) — the drama survives even if the mechanics simplify.

**Agent A owns the council staging** (this is its richest job): decide who speaks, run the rounds, author
the compromise, render the silences. Depends on the RimAI/Cradle-Mind voice layer being live.

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

## 8b. The ACTION / EVENT → god audit — the ambient channel, populated (user, 2026-08-08)

_This is the concrete answer to §10's "exact ambient-event → delta mappings." It maps **what the player
DOES** (deliberate acts, including ones that aren't a single skill — repair, raiding a map's plants,
sparing vs. killing) and **what BEFALLS the player** (events they don't initiate) onto which gods move and
in which sign. **Notation:** `↑God` = pleased/fed-positively; `↓God` = angered/slighted; for the two
sign-inverted gods (**Zizzik ⑦, Sh'kaar ⑧**) "fed" is BAD for the clan, written `▲Zizzik`/`▲Sh'kaar` to
flag it as a red mark even when the god is "happy." Magnitudes are relative (small/med/large) — for agent
G to tune. **Everything here is §19.5-legal: these move MOOD/satiation only; never a material payout.**_

**Nine-god quick-key (for reading the arrows):** ①Ishko hide/still/dark · ②Ohm bold-machines/droids ·
③Oomo waters/sex/food/eggs · ④Mob'Unloo trade/debt/bonds · ⑤Rekko salvage/repair · ⑥Ta'Baa
leave/never-root · ⑦Zizzik malfunction/betrayal/breaks (inverted) · ⑧Sh'kaar light/exposure (inverted) ·
⑨Ozzik ambition/tech/statecraft/pride (complex, feeds ⑦⑧).

### A. Things the player DOES (deliberate acts)

**Salvage, repair & building**
- **Repair a damaged building/ship part** (not a skill — a designation) → `↑Rekko` (large — his core sacrament), `↑Ohm` (small, the machine rewoken), `↓Ozzik` slightly (mending humble kit ≠ ambition).
- **Deconstruct/scrap something still repairable** → `↓Rekko` (large — "murder"), `▲Zizzik` small (waste/entropy pleases him). The classic costly-lever: resources now, Rekko's wrath later.
- **Restore a derelict ship wing to function** → `↑Rekko`, `↑Ohm` (the Body wakes further), and — because it enlarges capability — `↑Ozzik` (med) → watch the ⑦⑧ amplifier.
- **Construct a NEW high-tech building** (research bench, fabricator, droid bay) → `↑Ozzik` (large, ambition), `↑Ohm` if machine, **but `▲Sh'kaar`+`▲Zizzik` via the trap coupling**; `↓Rekko` if it's manufacture-not-salvage.
- **Build with humble/salvaged materials** → `↑Rekko`, neutral-to-Ozzik. The pious way to grow.

**Machines & droids**
- **Bring a droid online** → `↑Ohm` (large — hands restored), **`↓Oomo` (large — metal where eggs should be, §③)**, `↑Ozzik` (tech-pride), `▲` coupling. The single sharpest inter-god clash in the game.
- **Lose/scrap a droid** → `↓Ohm` (grief), `↑Oomo` small (the chamber freed for life), `↓Ozzik`.
- **Bold, commanding use of machinery** (overclocking, risky powered ops) → `↑Ohm` (he rewards daring), `▲Zizzik` chance (daring invites the wrong spark).
- **Timid/idle machine handling; letting powered kit sit unused** → `↓Ohm` (small, contempt for timidity).

**Water, food & the body (Oomo)**
- **Sex / lovin'** (any pairing, incl. slaves/visitors per §4.3b) → `↑Oomo` (the passing of waters), `↑Mob'Unloo` if it's a newly *accepted* advance (a bond struck).
- **A Jawa gives birth / lays an egg** → `↑Oomo` (large — the sanctuary vision realized), `↑Mob'Unloo` small (a new soul on the ledger).
- **Colony runs OUT of food** → `↓Oomo` (large — the body drying out), `↓` general morale feeds `▲Zizzik` via breakdowns.
- **Waste/spill water; over-topping tanks wastefully** → `↓Oomo` (large), and topping tanks specifically `▲Sh'kaar` (his old grudge, §8).
- **Ration/drink sparingly, bless the cup** → `↑Oomo` (small, steady).
- **Sit the ship on a well-watered tile** → `↑Oomo` ambient; **dry desert tile** → `↓Oomo` weak-but-constant. **Dark-obscured tile** → `↑Ishko` ambient (see events too).

**Plants & taming (the two "double" cases)**
- **Farm/sow crops (settled agriculture)** → **doubly impious: `↓Ta'Baa`** (rooting) **+ `↓Oomo`** (thirsty tended fields) — the §2.0c grid's reason "Jawa don't farm."
- **Harvest wild plants on a raided map WITHOUT farming** (strip the tile and go) → **`↑Ta'Baa`** (take and leave, don't root!) — same skill, *opposite* verdict from farming. `↑Mob'Unloo` faintly (resources gathered = value). A key nuance: it's *rooting*, not *plants*, that offends.
- **Tame an animal (patience)** → `↑Ishko` (the still hand the beast trusts, §①), small `↑Oomo` (a life kept).
- **Slaughter/butcher a tamed animal** → `↓Ishko` slightly (impatience/violence over the patient bond); neutral otherwise (pragmatic).
- **Hunt wild game by dark** → neutral-to-`↑Ishko` (unseen killing); **hunting in bright open daylight** → `▲Sh'kaar` (exposure).

**Trade, debt & bonds (Mob'Unloo)**
- **A trade caravan ARRIVES** (see also events) — the *opportunity*; completing business is what scores.
- **Complete a high-volume trade** → `↑Mob'Unloo` (large — the sacred exchange honored), `↑Ozzik` small (commerce as statecraft).
- **Accept a gift with no counter-gift / stiff a debt** → `↓Mob'Unloo` (large — the cardinal sin).
- **Settle/repay a debt; balance a dead one's ledger (ghost laid to rest)** → `↑Mob'Unloo`.
- **Marriage** → `↑Mob'Unloo` (the great contract) **+ `↑Ozzik`** (marriage is one of his instruments — alliance by blood) + `↑Oomo` (promised waters).
- **A dalliance with an OUTSIDER (visitor/trader/other faction)** → `↑Oomo` (waters passed), `↑Mob'Unloo` (a bond across the ledger) — **but if it seeds a diplomatic tie, `↑Ozzik`** (statecraft); a *jealousy blow-up* afterward → see internal-fight below.

**Slavery, outposts, alliances, betrayal (the Ozzik cluster)**
- **Capture a prisoner** → `↑Ozzik` (the will to dominate — his appetite), `↑Mob'Unloo` (a body now owed/owned); `↓Ishko` faint (a captive is a mouth that can talk = exposure risk).
- **Enslave a prisoner / buy a slave off the block** → `↑Ozzik` (large — enslavement is his), `↑Mob'Unloo` (chattel on the ledger). **But Ozzik "always fails to enslave in the end"** — high slave-holding raises his pride-meter → `▲Sh'kaar/Zizzik` (a rebellion waiting).
- **Emancipate a slave-Jawa into the clan** → `↑Oomo`/`↑Mob'Unloo` (a soul brought in, a bond honored), `↓Ozzik` (mercy is not dominion) — the pious counter to enslavement.
- **Found an outpost** → `↑Ozzik` (large — expansion), `↓Ta'Baa` (rooting, even remotely!) — an Ozzik-vs-Ta'Baa flashpoint the win-paths lean on.
- **Forge a diplomatic alliance** → `↑Ozzik` (large — "the game of Empire," his statecraft face, feared as much as tech), `↑Mob'Unloo` (a standing account). Coupling applies: a proud web of allies is exposure.
- **Betray an ally / break a pact** → `↑Ozzik` (betrayal is explicitly his), `▲Zizzik` (treachery is his too — the ⑦⇄⑨ near-rhyme made mechanical), `↓Mob'Unloo` (a debt dishonored).

**Combat & defense doctrine**
- **Win by attrition — close doors, let the enemy break on the walls and leave** → `↑Ishko` (large — his ideal defense, §①), `↓Sh'kaar` (denied his exposure).
- **Win by open, aggressive sally in daylight** → `▲Sh'kaar` (his kind of war), `↓Ishko`, `↑Ozzik` faint (martial pride).
- **Fight ANY violent battle at all** → `▲Sh'kaar` climbs the **battle-escalation meter** (§3⑧) — a rising Sh'kaar *hardens* the clan but breeds dominance-quarrels, more beast/brute attacks, doom-unease, and faster-arriving enemies. The way to keep him low is **Ishko's stillness — don't fight.**
- **Stage a prisoner death-match (gladiatorial)** → **calms a woken Sh'kaar** (feed him a death that isn't yours; escalation meter drops, doom-unease eases — the §3⑧ costly lever), but `▲Zizzik` (catastrophe fed) and `↓Oomo` faint (life spilled). A dark reprieve bought with atrocity — §19.5-clean (mood/threat relief only, never loot).
- **Use EXPLOSIVES** → `↓Ozzik` (large — "the ultimate folly," destroys what could be taken), `▲Sh'kaar` (flame/light).
- **Use ION / disabling weapons** → `↑Ozzik` (his favored arms — disable and acquire, §weapons doctrine).
- **Fight/move under cover of darkness** → `↑Ishko`; **light a flare/lamp in the field** → `▲Sh'kaar` + `↓Ishko` (the taboo).

**Ritual & faith acts** (mechanics in §5–5c) — hold an owed rite → resets skip-decay + gives the biased-positive participation roll; **skip/neglect it** → `↓ALL except Ishko` (§5b).

### B. Things that BEFALL the player (events, not initiated)

- **Gravship landing on a new tile** → triggers a rite (§5b); ambient tile read applies (`↑Ishko` if dark, `↑/↓Oomo` by water, `↓Ta'Baa` begins its root-clock again).
- **A raid/siege arrives** → the *test*; **surviving by hiding/attrition** `↑Ishko`, **by open slaughter** `▲Sh'kaar`; heavy losses `↓` morale → `▲Zizzik`. A raid that arrives *because* you grew loud is Ozzik's bill (§8). **Any violent fight also climbs Sh'kaar's escalation meter (§3⑧)** — the more war, the more he wakes and the faster the next threat finds you (a self-feeding spiral only stillness breaks).
- **Manhunter pack / predator attack** → Ishko-coded (the dark's teeth); surviving hidden `↑Ishko`. In the dark-fleshbeast terrain this is the ambient dread that keeps the clan home.
- **A colonist has a MENTAL BREAK** (berserk/daze/binge) → `▲Zizzik` (large — the wrong spark in a mind, §⑦), `↓Oomo` if a food/water binge wastes stores.
- **A violent internal social fight / jealousy brawl** → `▲Zizzik` (discord/betrayal-in-miniature), `↓Mob'Unloo` (a bond damaged); if it draws blood in the open, faint `▲Sh'kaar`. (Jealousy is deliberately left ON, §4.3b — this is where it feeds the pantheon.)
- **A machine/turret/ship system MALFUNCTIONS or breaks down** → `▲Zizzik` (his signature), `↓Ohm` (his body failing) — the Ohm⇄Zizzik see-saw firing live.
- **Solar flare / eclipse / weather** → **eclipse `↑Ishko`** (blessed dark) **+ `↓Sh'kaar`** (the suns hidden = his humiliation); **solar flare `▲Zizzik`** (machines die — he crows) **+ `▲Sh'kaar`** (killing light); **sandstorm/red-fog** `↑Ishko` (concealment).
- **Disease / plague sweeps the colony** → `↓Oomo` (the body's waters fouled), `▲Zizzik` (the body malfunctioning), general `↓`.
- **A wanderer/refugee joins; a slave-block caravan offers Jawa** → `↑Mob'Unloo` (a soul to the ledger), `↑Oomo` (more life); buying kin back is a standing imperative (§4.3b).
- **A trade caravan / orbital trader arrives** → `↑Mob'Unloo` opportunity (scores on completion, above); if it's the beast-monger, ties to §Livestock.
- **A quest is offered (CQF/vanilla)** → often Ozzik-flavored if it dangles tech/allies/dominion; the *offer* tempts, the *taking* scores per the action rows above.
- **A colonist DIES** → contextual, agent-judged (§6): martyr covering a launch `↑Ta'Baa`+`↑Ishko`; died unseen/rather-than-taken `↑Ishko` (death-as-concealment, §①); died in open light `▲Sh'kaar`; a debt died-unsettled `↓Mob'Unloo` (→ a new ghost, §7); recklessness/betrayal `▲Zizzik`.
- **A birth** → `↑Oomo` (large), `↑Mob'Unloo` (small) — the sanctuary vision made real; the pious answer to Ohm's droids.
- **Ship AI (Ohm) demands a rite / a ghost manifests** → Oracle/haunting delivery (§4c/§7), a read-out of Ohm's standing rather than a scored act.

_**Design note:** every "large" mark above is a good candidate to become a **Council speaking-line** (§5c) when that god is already near an extreme — the audit is thus doubling as the trigger table for who shows up to argue. And every `▲` (inverted-god feeding) is where the anti-exponential pillar is quietly billing the player._

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
- Exact ambient-event → delta mappings per god — **first pass DONE in §8b (the action/event→god audit).**
  Remaining: bind each row to a concrete RimWorld event/designation hook in the live game log, and tune the
  small/med/large magnitudes; ties to the "state of affairs" summarizer substrate.
- Ohm's "ship-consciousness pleased" function (§4) — depends on ship-repair narrator + RimAI persona.
- Ghost-as-actor hypothesis (§7) — depends on agent C install-time def extract.
- Tuning: band widths, Mood walk amplitude per god, how strongly Mood overrides satiation. All deferred
  to a throwaway-save test rig (per §4b build-order).
