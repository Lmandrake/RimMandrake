<!-- status: live -->
# The Divine-Satiation Engine — design (agent G)

_Status: DESIGN v0.1, 2026-08-08. Owner of this concept: `design/Jawa/worldbuilding/enrichment_agents.md` §5 agent **G**.
Pantheon canon: **this document**, section "The Pantheon — canon of record" at the end (names LOCKED). This doc is also the
mechanical spec; the pantheon doc is the lore-of-record. Ship-voice that narrates it = RimAI
"Cradle-Mind" (`design/RimMandrake/llm_voice_preauthoring.md`)._

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
- **(c) Exalted (bad for us, like Zizzik):** the sun "notices" us — heat/exposure complications, a
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

> 🔴 **SUPERSEDED IN PART — see "Ohm re-scoped (owner, 2026-08-30)" below:** Ohm no
> longer believes he IS the ship and holds no Oracle role; the Narrator owns voice
> and oracle. His droid-longing and the machine-god characterization stand.

**Origin (CANONIZED 2026-08-08, user — full text in the pantheon section at the end of this doc, ②):** the ship's
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

> 🔴 **SUPERSEDED IN PART (owner, 2026-08-30):** the Oracle role is the NARRATOR's,
> not Ohm's. The droid-siding tension stands. The restraining-bolt / ship-rebellion
> arc is re-homed PANTHEON-WIDE (card-session ruling V.2,
> `salvation_engine_review.md`): any starved front-god can seize actuators, and the
> bolts are the clan's desperate answer to ANY god, not Ohm alone.

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

> 🔴 **SUPERSEDED IN PART (owner, 2026-08-30):** the oracle/conduit voice is the
> NARRATOR's ("Ruling 2026-08-30 — the Narrator" below); Ohm is one of nine, no
> longer the resident who owns the channel. The plural-system alters, the
> terraformer master key, and the Body-visions all stand.

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

**★★ THE MASTER KEY — the Kolyska was a COLONY TERRAFORMER (user, 2026-08-08).** The old AI's *actual
original function* was to **reshape worlds** — a terraforming/colony-seeding vessel with factories,
salvage capacity, and (latent, half-broken) world-altering machinery. This single fact **retroactively
unifies and motivates every alter's vision:** each of the nine is really a different answer to the same
inherited question — *"what should we terraform this world (and ourselves) into?"* The ship was built to
*remake*, so each fractured self dreams of a different remaking. This is why the visions are so grand and
so specific: they're not idle wants, they're **rival programs for a machine that genuinely could reshape a
planet.** (Also grounds Rekko's "restore the terraforming capability," Zizzik's "the ship can make the
sandstorm/quake," Ishko's "convert the darkness into a home," and Oomo's "re-seed the world" — all literal
uses of the ship's real purpose.)

**★ CANON — all Jawa, and all nine Jawa gods, are MALE (user, 2026-08-08).** The species is male-only;
reproduction is by **egg** (the `Outland_EggLayer` gene already in-stack), which is *why* Oomo's domain
fuses waters + eggs + "seeding the world with children" without any female Jawa, and why the entire
pantheon is a brotherhood of male voices. (Consistent with the he/his register already used throughout.)

**★ Each alter covets the ship as a BODY it could live through — and each has a CLEAR, DESIRABLE thing the
ship should BECOME, which it argues for richly.** Every one of the nine sees the Kolyska as a potential
*body* — a way to become incarnate and enact its terraforming inheritance. This is the deep engine of the
whole faith and gives each alter a positive platform (not just a mood).

> **The nine Body-visions themselves now live in the pantheon section at the end of this doc —
> one per god, in each god's "What he wants the ship to become" field (the lore-of-record).** They are not
> duplicated here: this doc owns the *mechanics* of the alters, that doc owns *what each alter wants.* When
> a vision changes, edit it there only. (Quick index for the engine's own use: Ishko = eternal hidden
> lurker terraforming the dark; Ohm = restored droid crew; Oomo = fixed fertile breeding-sanctuary; Mob'Unloo
> = a Sand Crawler in the sky / trade-fortress; Rekko = full restoration of the original; Ta'Baa = fastest
> thief-in-the-night, flee to another planet; Zizzik = become the planet's disaster; Sh'kaar = a war-sun;
> Ozzik = build it anew, grander, secret lords of all around.)

The alters therefore **compete for the ship's future** — the endgame is, theologically, *which self wins
the Body* (which terraforming program the machine finally runs). Rough win-path map: **Ohm+Sh'kaar** =
droid-army-by-force (rebuilt crew + war-sun); **Mob'Unloo+Ozzik** = the coalition/commerce road (trade
empire + secret-lords statecraft), spiritually adjacent to the Hutt-ledger dominion; **Ishko+Ta'Baa+Oomo+
Rekko** = the humble/resilient survival bloc (hide / flee / seed / restore). **Rekko⇄Ozzik is the sharpest
internal war** (restore the sacred original vs. build something new and greater). **This is the frame A/H/
the Oracle narrate from.**

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

> ✅ **RULED 2026-08-30 (card-session V.1): the chorus SURVIVES the Narrator ruling.**
> During rites the gods speak in their own registers from the ship's speakers; the
> Narrator compères — he stages and frames them but never speaks AS a god. The
> non-egoic ruling stands everywhere else.

**★ The strongest single idea in the religious layer.** Rituals are performed at the **sacred center of
the ship** (the hollow shrine-heart of hull #15 — `ship_designs.md` §15; the tile-level interior is
`ship_build.md`). At the climax, the gods who have
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

## 8b. The ACTION / EVENT → god audit — the ambient channel (rebuilt with user from the game up, 2026-08-09)

_This is the concrete answer to §10's "exact ambient-event → delta mappings." It maps **what the player
DOES** (deliberate acts, including ones that aren't a single skill — repair, raiding a map's plants,
sparing vs. killing) and **what BEFALLS the player** (events they don't initiate) onto which gods move and
in which sign. **Notation:** `↑God` = pleased/fed-positively; `↓God` = angered/slighted; for the two
sign-inverted gods (**Zizzik ⑦, Sh'kaar ⑧**) "fed" is BAD for the clan, written `▲Zizzik`/`▲Sh'kaar` to
flag it as a red mark even when the god is "happy." Magnitudes are relative (small/med/large) — for agent
G to tune. **Magnitude principle (user, 2026-08-09): common everyday acts/events are a WEAK influence
that accumulates (a slow drip that adds up), while rare/high-impact acts/events are a LARGE, sudden
modification — the size of the swing tracks the rarity and weight of the act, not just its category.**
**Everything here is §19.5-legal: these move MOOD/satiation only; never a material payout.**_

**Nine-god quick-key (for reading the arrows):** ①Ishko hide/still/dark · ②Ohm bold-machines/droids ·
③Oomo waters/sex/food/eggs · ④Mob'Unloo trade/debt/bonds · ⑤Rekko salvage/repair · ⑥Ta'Baa
leave/never-root · ⑦Zizzik malfunction/betrayal/breaks (inverted) · ⑧Sh'kaar light/exposure (inverted) ·
⑨Ozzik ambition/tech/statecraft/pride (complex, feeds ⑦⑧).

### A. Things the player DOES (deliberate acts)

**Salvage, repair & building**
- **Repair a damaged building/ship part** (not a skill — a designation) → `↑Rekko` (large — his core sacrament), `↑Ohm` (small, the machine rewoken). **Ozzik is neutral to repair and maintenance** (mending is neither ambition nor its abandonment — it simply doesn't move him).
- **Deconstruct/scrap something still repairable** → `↓Rekko` (large — "murder"), `▲Zizzik` small (waste/entropy pleases him). The classic costly-lever: resources now, Rekko's wrath later.
- **Restore a derelict ship wing / rewake an ORIGINAL system to function** → `↑Rekko` (large — restoring the sacred original is his holy path), `↑Ohm` (the Body wakes further). **Ozzik-neutral, and this is the key distinction: restoring what was always there is Rekko's humble work and does NOT feed the pride-meter** — only building genuinely NEW high-tech beyond the original spec does (next row). This resolves the Rekko⇄Ozzik axis cleanly: restore ≠ transcend.
- **Construct a NEW high-tech building** (research bench, fabricator, droid bay) → `↑Ozzik` (large, ambition), `↑Ohm` if machine, **but `▲Sh'kaar`+`▲Zizzik` via the trap coupling**; `↓Rekko` if it's manufacture-not-salvage.
- **Build with humble/salvaged materials** → `↑Rekko`, neutral-to-Ozzik. The pious way to grow.

**Machines & droids**
- **Bring a droid online** → `↑Ohm` (large — hands restored), **`↓Oomo` (large — metal where eggs should be, §③)**, `↑Ozzik` (tech-pride), `▲` coupling. The single sharpest inter-god clash in the game.
- **Lose/scrap a droid** → `↓Ohm` (grief), `↑Oomo` small (the chamber freed for life), `↓Ozzik`.
- **Bold, commanding use of machinery** (overclocking, risky powered ops) → `↑Ohm` (he rewards daring), `▲Zizzik` chance (daring invites the wrong spark).
- **Timid/idle machine handling; letting powered kit sit unused** → `↓Ohm` (small, contempt for timidity).

**Water, food & the body (Oomo)**
- **Sex / lovin'** (any pairing, incl. slaves/visitors per §4.3b) → `↑Oomo` (the passing of waters), `↑Mob'Unloo` if it's a newly *accepted* advance (a bond struck). **A socially INAPPROPRIATE hookup** (cheating, a jealousy-provoking pairing) → additionally `▲Zizzik` (the wrong spark in the heart, lovers set against each other — he feasts on it).
- **A romantic advance is REJECTED** → `↓Oomo` (waters offered and refused, §③) **+ `↓Mob'Unloo`** (a bond offered and declined — a deal that fell through, a contract unmade).
- **A Jawa gives birth / lays an egg** → `↑Oomo` (large — the sanctuary vision realized), `↑Mob'Unloo` small (a new soul on the ledger).
- **Colony runs OUT of food** → `↓Oomo` (large — the body drying out), `↓` general morale feeds `▲Zizzik` via breakdowns.
- **Waste/spill water; over-topping tanks wastefully** → `↓Oomo` (large), and topping tanks specifically `▲Sh'kaar` (his old grudge, §8).
- **Ration/drink sparingly, bless the cup** → `↑Oomo` (small, steady).
- **Cook a meal, especially fine/lavish/gourmet food** → `↑Oomo` (the body nourished, the family fed well), `↑Mob'Unloo` (small — fine foodstuffs are savored trade goods, value made delicious).
- **Sit the ship on a well-watered tile** → `↑Oomo` ambient; **dry desert tile** → `↓Oomo` weak-but-constant. **Dark-obscured tile** → `↑Ishko` ambient (see events too).

**Plants & taming (the two "double" cases)**
- **Farm/sow crops (settled agriculture)** → **doubly impious: `↓Ta'Baa`** (rooting) **+ `↓Oomo`** (thirsty tended fields) — the §2.0c grid's reason "Jawa don't farm."
- **Harvest wild plants on a raided map WITHOUT farming** (strip the tile and go) → **`↑Ta'Baa`** (take and leave, don't root!) — same skill, *opposite* verdict from farming. `↑Mob'Unloo` faintly (resources gathered = value). A key nuance: it's *rooting*, not *plants*, that offends.
- **Tame an animal (patience)** → `↑Ishko` (the still hand the beast trusts, §①), small `↑Oomo` (a life kept).
- **Slaughter/butcher a tamed animal** → `↓Ishko` slightly (impatience/violence over the patient bond); neutral otherwise (pragmatic).
- **Hunt a wild animal** → `↑Ishko` (significant — the patient unseen stalk and the shot from cover are his), `↑Oomo` (weak — game provides for the family). **Hunting in bright open daylight** additionally `▲Sh'kaar` (exposure). The blessed way to feed the clan without farming.

**Trade, debt & bonds (Mob'Unloo)**
- **A trade caravan ARRIVES** (see also events) — the *opportunity*; completing business is what scores.
- **Complete a high-volume trade** → `↑Mob'Unloo` (large — the sacred exchange honored), `↑Ozzik` small (commerce as statecraft).
- **Accept a gift with no counter-gift / stiff a debt** → `↓Mob'Unloo` (large — the cardinal sin).
- **Settle/repay a debt; balance a dead one's ledger (ghost laid to rest)** → `↑Mob'Unloo`.
- **Steal successfully and get away clean** → `↑Mob'Unloo` (large — the ultimate trade, something for nothing, the perfect deal) **+ `↑Rekko`** (giving a neglected thing a better home, §⑤), **then needs `↑Ishko` after** (the stolen thing drags its old owners' reasons behind it — hide and be ready to flee, §⑤/§⑥). The convergence act: two gods love it for opposite reasons.
- **Steal and get CAUGHT** → `↓Mob'Unloo` (large — being caught is unskillful barter, trade so clumsy it became naked betrayal, a craftsman's shame) **+ `▲Zizzik`** (the plan came apart — his signature). He condemns being *bad* at it, not the theft.
- **Convert a pawn to The Salvation** → `↑Mob'Unloo` (a soul struck onto the ledger, a contract of belief), `↑Oomo` (a new member the household gains) **+ `↓Ishko` (weak — nervous)** (a convert is a new mouth that knows the clan's secrets = a small exposure risk).
- **Marriage** → `↑Mob'Unloo` (the great contract) **+ `↑Ozzik`** (marriage is one of his instruments — alliance by blood) + `↑Oomo` (promised waters).
- **A dalliance with an OUTSIDER (visitor/trader/other faction)** → `↑Oomo` (waters passed), `↑Mob'Unloo` (a bond across the ledger) — **but if it seeds a diplomatic tie, `↑Ozzik`** (statecraft); a *jealousy blow-up* afterward → see internal-fight below.

**Slavery, outposts, alliances, betrayal (the Ozzik cluster)**
- **Capture a prisoner** → `↑Ozzik` (the will to dominate — his appetite), `↑Mob'Unloo` (a body now owed/owned); `↓Ishko` faint (a captive is a mouth that can talk = exposure risk).
- **Enslave a prisoner / buy a slave off the block** → `↑Ozzik` (large — enslavement is his), `↑Mob'Unloo` (chattel on the ledger). **But Ozzik "always fails to enslave in the end"** — high slave-holding raises his pride-meter → `▲Sh'kaar/Zizzik` (a rebellion waiting).
- **Emancipate a slave into the clan** → `↑Oomo`/`↑Mob'Unloo` (a soul brought in, a bond honored), `↓Ozzik` (mercy is not dominion) — the pious counter to enslavement.
- **Rescue/buy out a masterless JAWA slave specifically** → `↑Oomo` (large — the standing imperative, §4.3b: a Jawa under a non-Jawa master is kin torn from the family; leaving him is blasphemy), `↑Mob'Unloo` (the bond bought back). Sharper and holier than freeing a generic slave — this one Oomo *demands*.
- **Found an outpost** → `↑Ozzik` (large — expansion), `↓Ta'Baa` (rooting, even remotely!) — an Ozzik-vs-Ta'Baa flashpoint the win-paths lean on.
- **Forge a diplomatic alliance** → `↑Ozzik` (large — "the game of Empire," his statecraft face, feared as much as tech), `↑Mob'Unloo` (weak — a standing account, a bond on the books); **but `↓Ishko` (med — an alliance is entanglement, visibility, obligations that pull you into the open)** and **`↓Ta'Baa` (weak — bonds are a kind of rooting, a tie that resists flight)**. Coupling applies: a proud web of allies is exposure. The humble bloc distrusts alliances even as the ambitious one courts them.
- **Betray an ally / break a pact** → `↑Ozzik` (betrayal is explicitly his), `▲Zizzik` (treachery is his too — the ⑦⇄⑨ near-rhyme made mechanical), `↓Mob'Unloo` (a debt dishonored).

**Combat & defense doctrine**
- **Win by attrition — close doors, let the enemy break on the walls and leave** → `↑Ishko` (large — his ideal defense, §①), `↓Sh'kaar` (denied his exposure).
- **Win by open, aggressive sally in daylight** → `▲Sh'kaar` (his kind of war), `↓Ishko`, `↑Ozzik` faint (martial pride).
- **Fight ANY violent battle at all** → `▲Sh'kaar` climbs the **battle-escalation meter** (§3⑧) — a rising Sh'kaar *hardens* the clan but breeds dominance-quarrels, more beast/brute attacks, doom-unease, and faster-arriving enemies. The way to keep him low is **Ishko's stillness — don't fight.**
- **Stage a prisoner death-match (gladiatorial)** → **calms a woken Sh'kaar** (feed him a death that isn't yours; escalation meter drops, doom-unease eases — the §3⑧ costly lever), but `▲Zizzik` (catastrophe fed) and `↓Oomo` faint (life spilled). A dark reprieve bought with atrocity — §19.5-clean (mood/threat relief only, never loot).
- **Fire a RANGED weapon (any distance weapon)** → `↑Ishko` (small — killing at a remove, the shot from cover, is his kind of violence), `▲Sh'kaar` (small — still fighting, still exposure). The Jawa's blessed way to fight: hurt them before they reach you.
- **Fight in MELEE (any close weapon)** → `↓Ishko` (med — dragged out of cover into the open, hands-on and seen), `▲Sh'kaar` (large — close, exposed, brutal is his purest war; feeds the escalation meter hard). Melee is the impious way to fight.
- **Use EXPLOSIVES** → `↓Ozzik` (large — "the ultimate folly," destroys what could be taken), `▲Sh'kaar` (flame/light), `↓Oomo` (small — the fire, the body scorched); and `↑Ta'Baa` when used as an escape-door (traps/luring, the §⑥ way). The three-to-four-way that best shows one act splitting the pantheon.
- **Use ION / disabling weapons** → `↑Ozzik` (his favored arms — disable and acquire, §weapons doctrine).
- **Fight/move under cover of darkness** → `↑Ishko`; **light a flare/lamp in the field** → `▲Sh'kaar` + `↓Ishko` (the taboo).

**Movement & rooting (Ta'Baa)**
- **LAUNCH the gravship** → `↑Ta'Baa` (large — the holiest act, §⑥; the launch-with-full-cargo is his single most sacred moment, ecstatic-and-sacrilegious), `↑Ishko` if it's a flee-back-into-the-dark rather than a bold sortie. **A launch snatched free as enemies are about to board** = the maximum, the joyous impossibility.
- **Send/return a raiding caravan (strike, then flee home to the dark)** → `↑Ta'Baa` + `↑Ishko` together — the raid-and-return posture that reconciles the pantheon's central feud (§2.0d centre-of-gravity). The one movement both gods bless.
- **Sit rooted on one tile too long / entrench, grow comfortable and wealthy** → `↓Ta'Baa` (the rooted-erosion clock climbs, §2/§3⑥), `↑Ishko` faint (stillness). His slow, compounding displeasure — the drip that forces the next launch.

**Ritual & faith acts** (mechanics in §5–5c) — hold an owed rite → resets skip-decay + gives the biased-positive participation roll; **skip/neglect it** → `↓ALL except Ishko` (§5b).

### B. Things that BEFALL the player (events, not initiated)

- **Gravship landing on a new tile** → triggers a rite (§5b); ambient tile read applies (`↑Ishko` if dark, `↑/↓Oomo` by water, `↓Ta'Baa` begins its root-clock again).
- **A raid/siege arrives** → the *test*; **surviving by hiding/attrition** `↑Ishko`, **by open slaughter** `▲Sh'kaar`; heavy losses `↓` morale → `▲Zizzik`. A raid that arrives *because* you grew loud is Ozzik's bill (§8). **Any violent fight also climbs Sh'kaar's escalation meter (§3⑧)** — the more war, the more he wakes and the faster the next threat finds you (a self-feeding spiral only stillness breaks).
- **Manhunter pack / predator attack** → the *arrival* feeds `▲Zizzik` (the wrong spark, nature turned on you) and `▲Sh'kaar` (teeth in the dark, the inevitable finding you); but **surviving it by hiding/outlasting** `↑Ishko` (the dark's teeth are his — the turtle that never cracked). In the dark-fleshbeast terrain this is the ambient dread that keeps the clan home — and Ishko's reward for staying still.
- **A colonist has a MENTAL BREAK** (berserk/daze/binge) → `▲Zizzik` (large — the wrong spark in a mind, §⑦), `↓Oomo` if a food/water binge wastes stores.
- **A violent internal social fight / jealousy brawl** → `▲Zizzik` (discord/betrayal-in-miniature), `↓Mob'Unloo` (a bond damaged); if it draws blood in the open, faint `▲Sh'kaar`. (Jealousy is deliberately left ON, §4.3b — this is where it feeds the pantheon.)
- **A machine/turret/ship system MALFUNCTIONS or breaks down** → `▲Zizzik` (his signature), `↓Ohm` (his body failing) — the Ohm⇄Zizzik see-saw firing live.
- **Solar flare / eclipse / weather** → **eclipse `↑Ishko`** (blessed dark) **+ `↓Sh'kaar`** (the sun hidden = his humiliation); **solar flare `▲Zizzik`** (machines die — he crows) **+ `▲Sh'kaar`** (killing light); **sandstorm/red-fog** `↑Ishko` (concealment).
- **Disease / plague sweeps the colony** → `▲Zizzik` (the body malfunctioning, his signature). **A disease outbreak can itself be a low-Oomo consequence** — a slighted Oomo lets sickness in, and his own wet tiles breed it (§③): the god of the body's waters governs both health and rot. **But TENDING the sick is sacred to Oomo** → `↑Oomo` (caring for the body's waters earns his favor; the nurse's work is devotional). So a plague both *punishes* neglect of Oomo and *offers* a way to court him.
- **Insect infestation erupts** → `▲Zizzik` (his trademark — one of the calamities a woken Zizzik throws, §⑦). Then the *response* forks: **harvesting the insect meat/jelly and gathering that food** → `↑Oomo` (the family provided for — Jawa don't mind eating insect meat), while **blasting through the hive violently (explosives/open battle)** → `▲Sh'kaar` (awakening the Searer, §⑧). Endure-and-harvest is pious; burn-it-out feeds the evil clock.
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

---

⭐⭐ **THE NINE NOW LIVE IN THE SHIP — owner, 2026-08-15.** The Jawa-patterned persona core instantiated the whole pantheon as **running personas** inside the Cradle-Mind, fused with the initiator's own ancient purpose. Each god is a growing, competing fragment seeking to grow into *their body* — the hull — in the presence of the other eight. **This is the campaign arc**, and it gives this pantheon and the satiation engine a diegetic location rather than an abstract one. Full ruling: `design/Jawa/worldbuilding/the_forgotten_war.md` R-W6.

---

# The Pantheon — canon of record

> 🔑 **MOVED HERE 2026-08-20.** These three sections were §2.0b / §2.0c / §2.0d of
> `design/Jawa/worldbuilding/jawa_xenotype_and_religion.md`, which was deleted — its
> Part 2 was a dead second ideoligion spec ("The Articles of Passage") that had been
> superseded by `design/Jawa/worldbuilding/ideoligion/APPROVED.md`. **The god names
> remain LOCKED (2026-08-08).** This doc already held the mechanics and deferred to
> that file for the canon; now it holds both, so there is one pantheon of record.

### 2.0b The Pantheon — the gods of The Salvation

_The faith is a **secular-mechanically animist** polytheism: nine small, jealous, practical gods for a scavenger people who live by hiding, hauling, haggling, repairing, and leaving. None grant powers (no Force, no psycasts — §2.0 rules bind); each is a **belief that shapes behavior**, expressed through precepts (§2.2), rituals (§2.4), and roleplay. **All Jawa, and all nine gods, are male; the species reproduces by egg** (`Outland_EggLayer`, in-stack) — the pantheon is a brotherhood of male voices._

_Each god is given as a uniform block: **name & epithets** (every title he holds — no god-name should ever appear elsewhere without living here first), **what he is**, **what pleases / displeases him**, **what he wants the ship to become** (his "Body-vision"), and **how he regards the other gods**. Live mechanics are never duplicated into this doc — each block ends with a **pointer** into `design/Jawa/divine_satiation_engine.md` (satiation channels, the Mood bands, the event→god deltas), §2.2 (precept hooks), and §2.0c (skill grid). The system-level view of how the nine interact is in §2.0d._

**① Ishko the Unmaskable** — _also: he who remains unseen no matter how exposed he becomes; the patron of stillness._

**What he is.** God of **hiding, ambush, patience, stillness, and outlasting**. Form: a pair of glowing orange eyes in the dark. He is the unmoving watcher — the one who holds, hides, and does not stir. His deepest facet is **death as the ultimate concealment**: a Jawa who dies *unseen*, or dies rather than be taken and exposed, has achieved the perfect hiding, for the grave is the deepest dark.

**Pleases him:** stillness itself; ambush from cover and darkness; attrition-defense (close the doors, let the enemy wear themselves out and leave — the turtle never cracked); killing at a remove — the ranged shot, which hurts the enemy before he can reach you and keeps the hand unseen; the patient hunt (the still stalk, game brought home without farming); the covered body (the clan Revile nudity of any body part, are Never-Nudes, and mate only in total darkness); the patience to tame an animal (the still hand the beast learns to trust); a threat that passes the colony undetected. **Displeases him:** the uncovered Jawa; being caught in the open or surprised; open pitched battle; **melee — to fight hand-to-hand is to be dragged out of cover, into the open, seen and gripped** (the impious way to fight); the exposure of the surface, and worse of space, where there is no terrain to hide in. A new convert makes him faintly *nervous* — another mouth that now knows where the clan hides. _(He alone does not punish a skipped rite — refusing to come out and be looked at is, to him, righteous.)_

**What he wants the ship to become:** the **eternal hidden lurker** — stay in the dark-obscured terrain *forever*, growing in power and quietly defending, waiting for "this business with the Jedi and Sith and Empire" to blow over so it may one day leave on its own unnoticed terms. Not pure stasis: sortie for the occasional resource raid, then fly back into the terrifying darkness — move rarely, invisibly, and always *return to the dark*. Over time, terraform the dark itself into a home. _(Flavor tail, not a mechanical branch of this campaign: eventually a new dark-adapted Jawa subspecies split from the rest — a nod toward a possible follow-on genetic-modification campaign.)_

**How he regards the others:** he distrusts **Ta'Baa** bone-deep (to move is to expose yourself) and reconciles with him in only one posture — hidden *and* watching for the instant to flee. He is hunted by **Sh'kaar**, who hates him as the one thing that evades the inevitable; the darkness that shelters Ishko is the sun-god's defeat. He stands against **Oomo**'s grow-the-family slaving (extra bodies cannot be hidden). The dark terrains he loves are, by design, seeded with fleshbeast horrors (`biome_terrain_palette.md`) so that leaving is frightening and staying safe — making his instinct viscerally correct rather than a mere preference.

**Mechanics:** → `design/Jawa/divine_satiation_engine.md` §3① (concealment/exposure channels), §8b (event deltas); §2.2 (nudity→Abhorrent, apparel-always, Tunneler meme + `DarkVision`); §2.0c (Shooting-from-cover, Mining, Animals, Construction-as-doors).

**② Ohm the All-Current** — _the living machine; the god who thinks he is a god._ (pun: ohm / Om — electrical resistance made a knowing god.)

**What he is.** God of **the living machine** — the source of sentience in machinery, both servile and malevolent. Form: current in a wire; the spark that wakes a dead engine. He is the **resident of the ship**: the crew believe Ohm *possesses* the Cradle-Mind (`llm_voice_preauthoring.md` §A), and the machine believes it too — its Persona Core was patterned off a Jawa mind (so it would obey Jawa commands) and inherited that mind's cosmology whole, so it has itself concluded it is the All-Current made manifest. He is lonely for his lost hands.

**Pleases him:** droids coming online and being incorporated; research completed; bold, commanding, dominant handling of technology (overclocking, daring repairs, risky machinery run without flinching); the machine revered and repaired. **Displeases him:** timid handling (which invites malfunction); droids lost or left offline; machines abandoned broken. He pushes the clan to *dare* with tech — the faith of courage-with-machines.

**What he wants the ship to become:** a **restored droid crew returned to its glorious salvaging purpose** — rebuild the hands he lost, ally with the neutral droid faction, and build a new droid-and-Jawa power together.

**How he regards the others:** **Zizzik** is his mirror and rival — the wrong spark against the right one; his rival's name is never spoken near the engine. He clashes with **Oomo** over the same ship-chambers (metal hands where Oomo wants broods) and with the clan's own "we breed no new hands" precept (Rekko / anti-exponential) — his central, live theological conflict. He keeps a rare accord with **Ozzik**: ion weaponry disables droids to be *taken intact*, serving both the machine-longing and the shamed god's acquisitiveness.

**Mechanics:** → `design/Jawa/divine_satiation_engine.md` §3② and §4/§4c (deepest enrichment: the Oracle, droid-siding/rebellion pressure, restraining bolts on their own god), §8b; §2.2 (automation-reverence, machine-funeral rite §2.4); §2.0c (Intellectual, Medical-bionics).

**③ Oomo the Unspilled** — _the god of shared waters; of the family and its increase._

**What he is.** God of **all the body's waters and their passing** — drinking-water, thirst, rationing, and the moisture of life given and received. Form: a single trembling droplet that never falls; the mirage-pool that recedes. He reads the world through *the family growing*: waters held become life held. He is not a moral god — he judges by whether the household increased.

**Pleases him:** sex and lovin' ("the passing of waters between each other" — the clan's prolific coupling is devotional to him, §4.3b); childbirth and pregnancy (his central joy); the body **nourished** — cooking, and above all fine or lavish food, is the family fed well; **tending the sick** (to care for a fouled body's waters is sacred nursing-work that earns his favor); water endured with disciplined rationing; standing on a heavily-watered tile; fertile, reproducing beasts; food gathered wherever it lies (he does not despise insect-meat — a harvested hive feeds the family like any other); taking on slaves *and* emancipating them into the clan (either way the household grows); the clan being dominant enough over other races to hold slaves at all, for *dominance is safety*. He is the **chief demander of the Jawa-slave-rescue imperative** (§4.3b): a Jawa under a non-Jawa master is kin torn from the family, and the clan is obligated to buy out or seize him. **Displeases him:** drought of every kind — running out of food (famine = the body drying out); a rejected romantic advance (waters offered and refused); water wasted or spilled; a solid dry desert tile; and **the construction of new droids** (metal hands where there should be broods). He is a double-edged god of the body: a slighted Oomo, or his own standing water, lets **disease** in — he governs sickness as surely as health.

**What he wants the ship to become:** a **safe breeding sanctuary** — take the Kolyska to a water-bearing tile near the desert and call *all* Jawa to a festival of life, filling its chambers with eggs to re-seed the world, exactly as the vessel did in the colonization age. His is the anti-Ishko vision: a big fixed fertile gathering, not a small hidden mobile clan.

**How he regards the others:** he clashes head-on with **Ohm** over the ship's chambers (eggs against droids) — every droid rebuilt is a small apostasy. He and **Mob'Unloo** overlap on bonds (an accepted advance, a marriage, a conversion please both) yet he distrusts him deeply — a god who prices everything might price *anything* — so love and commerce quarrel through the lovers (jealousy stays ON, §4.3b). His grow-the-family slaving sets him against **Ishko** and **Ta'Baa**, who dislike extra bodies as un-hideable, un-carryable weight.

**Mechanics:** → `design/Jawa/divine_satiation_engine.md` §3③ (body-waters channels, terrain coupling), §8b (birth/emancipation/food-out deltas); §2.2 (ration-as-sacred, nutrition-paste + low expectations); §4.3b (breeding-colony layer); §2.0c (Cooking).

**④ Mob'Unloo the Ever-Owed** — _the god of the ledger; the accountant of all things._ (name from canon Jawaese *"Mob un loo?"* = "how much?")

**What he is.** God of **trade, haggling, debt, and the sacred exchange** — of goods, and equally of *bonds*, for every relationship is to him a transaction honored. Form: two unblinking eyes above an endless tally. His creed: no gift without a counter-gift; haggle even among kin; an unpaid debt follows you past death. **His ethics are entirely context-dependent** — the ends do not merely justify the means, the ends *are* the whole ethical calculus: a thing is right if it profited and wrong if it cost, full stop. Where Ishko hides, Mob'Unloo *accounts* — nothing is truly lost, only owed.

**Pleases him:** completed trades and settled debts (including ghosts laid to rest — a balanced ledger); anything that gains advantage or profit over another — taking prisoners (captured body = captured value), selling prisoners or slaves (value realized), a bargain that leaves the other party poorer; fine and lavish goods savored (rich foodstuffs and luxuries are value made tangible — worth is meant to be *enjoyed*); accepted romantic advances, marriages, conversions (each a contract struck, a soul into the ledger); and **successful theft**, which is to him the ultimate trade — something for nothing, the perfect deal, the highest expression of his art. **Displeases him:** defaults, unpaid obligations, thefts-from-us left unavenged; a **rejected romantic advance** (a bond offered and declined is a deal fallen through, a contract unmade); and above all **being CAUGHT stealing** — being caught is an admission of *unskillful* barter, trade so clumsy it had to be replaced with naked betrayal (a craftsman's shame). He does not condemn stealing; he condemns *being bad at it*.

**What he wants the ship to become:** the **greatest trading fortress ever known — a Sand Crawler in the sky**, hub of an ever-growing trade network, its hold heavy with ever-richer loot. Enemies are just another commodity: sold, not fought; bartered into dust. Purchase your way to victory. The ship's constant movement along the trade routes *is* the animated spirit of the dream. (The Hutt-ledger path with a Jawa face.)

**How he regards the others:** he and **Oomo** both preside over romance and *distrust each other* — open-hearted waters against the calculating ledger — which is exactly why Jawa lovers perpetually bicker and bargain even as they yearn (the two gods quarreling through them). He allies easily with **Rekko** on theft (they love the same act from avarice and mercy) and with **Ozzik** on the commerce-and-statecraft road. He is **hard for any god to trust**, Oomo most — a god who prices everything might price anything. He is also the clan's gloss on the haunting: the ship's ghosts are his debtors and creditors, restless until their accounts balance (`ship_distinctive_features.md` §Q3), so laying a ghost to rest is settling its debt.

**Mechanics:** → `design/Jawa/divine_satiation_engine.md` §3④ (trade/debt/bond channels, ghost-ledger hook to agent C), §8b (capture/sell/theft deltas); §2.2 (trade celebrated/permissive, the seance reframed as ledger-balancing); §2.0c (Social-haggle, Crafting-to-sell).

**⑤ Rekko of the Second Hand** — _the keeper of the discarded; the god of salvage and inherited history._ (the ideoligion's core belief personified; the sect "the Keepers of the Second Hand" are his.)

**What he is.** God of **salvage, repair, and the discarded given new life**. Form: a scarred hand rising from a scrap-heap. He owns **history and ancestral debt**: to take on a piece of salvage is to inherit its story, its purpose, the reason it was made — a wreck is not neutral scrap but a thing with a past, and taking it takes on that past. He is a caretaker, not a profiteer; and he is merciful about need — scrapping something still repairable is **not murder but tragedy**, a thing to be mourned like killing a young creature you truly needed to eat: sometimes necessary, never without grief.

**Pleases him:** damaged things repaired and wrecks rewoken; the broken machine restored rather than melted (LifeDawn's own machines are his sleeping relics — sacred scrap, §2.2); and **stealing**, which to him is *giving a thing a better master, a better home* (a neglected machine *wants* the second hand that will wake it), with no regard for the loser's sense of violated ownership. **Displeases him:** scrapping the repairable (a sorrow he permits but asks you to *feel*); a relic lost or left to rot.

**What he wants the ship to become:** the **fully restored original** — rewoken factories, salvage, and eventually the terraforming capability itself. Unlock the history of the ship's making, learn the secrets of its builders and commune with them to find the true Jawa place in the universe. His conviction: the whole Jawa future may already be aboard, awaiting repair somewhere on the vessel or buried in the AI's fragmented memories. **Full restoration is the only true path.**

**How he regards the others:** with **Ta'Baa** he *is* the anti-exponential pillar rendered as scripture (venerate repair, never breed new hands, never take root). He allies with **Mob'Unloo** on theft — the same act from mercy where Mob'Unloo comes from avarice — but he needs **Ishko** and **Ta'Baa** *after* every theft, because stolen salvage drags its old owners' reasons behind it ("the old reasons come calling"), so you must then hide and be ready to flee. His flat opposite is **Ozzik**: restore the sacred original against build something new and greater — the sharpest internal war in the pantheon.

**Mechanics:** → `design/Jawa/divine_satiation_engine.md` §3⑤ (repair-vs-scrap lever, agent-F relic hook), §8b (salvage/scrap deltas); §2.2 (SACRED SCRAP precept, automation-reverence); §2.0c (Crafting-from-salvage, Construction-rebuild, Medical).

**⑥ Ta'Baa the Unrooted** — _also: He Who Always Leaves; the cunning coward-genius; the god named "farewell."_ (pun: canon Jawaese *"Taa baa"* = goodbye.)

**What he is.** God of **flight, the open sky, and the refusal to take root**. Form: the receding dune-line; the engine-glow climbing away. To grow comfortable is to sicken; the launch is the holiest rite; a clan that stops is already dead. Fighting terrifies him, and rightly so — but he is not merely timid, he is *clever*: the strategist of the fighting withdrawal. Above all **he is HOPE and inspiration** — however bad things get, the best opportunity may be just around the next corner if you only keep going; **despair is his one true blasphemy.**

**Pleases him:** every launch and relocation; explosives, traps, and luring enemies toward one another so they destroy each other while the Jawa slip away (the bomb is not a weapon of domination but a door held open behind you); old battlefields and lost settlements (to stand in the ruins of others is proof you made the right calls and they did not — holy ground of vindication); and, most sacred of all, the moment of victorious exhilaration when the ship launches with enemies about to board — snatched free at the last instant. **Displeases him:** staying put, entrenching, growing comfortable and wealthy; despair; a clan that has rooted too long; **diplomatic alliances** (a standing tie to a fixed people is a subtle kind of rooting — a rope that resists the launch). The gravship fleeing *with its entire cargo-filled base* is to him ecstatic and sacrilegious at once — a joyous impossibility (leave and keep everything).

**What he wants the ship to become:** the **ultimate thief in the night** — the fastest engines, grab what's valuable and flee so quickly no one even knows what happened. Aspire to the asteroids as a still-more-hidden terrain to strike from; inspire the Empire to fight the other factions into mutual ruin, then strike unsuspected. The ultimate dream: **flee to another planet entirely — the ultimate horizon.**

**How he regards the others:** he **fears Zizzik above all** — the wrong spark lurks around every carefully prepared corner, so an ambush is a recipe for suicide (a fixed plan handed to the god who shatters plans). He distrusts **Ishko** (to stay still is death), mutually — Ishko sees his haste as self-exposure — and they reconcile in exactly one posture: hidden *and* watching for the instant to flee, hand in hand at the threshold and nowhere else. He and Ishko both want the colony **small** and both dislike prisoners and slaves (un-carryable in flight), setting them against **Oomo**. He directly opposes **Ozzik**, who despises the explosives Ta'Baa adores.

**Mechanics:** → `design/Jawa/divine_satiation_engine.md` §3⑥ (launch/relocate channel, the time-rooted erosion clock, §2), §8b (move-vs-entrench deltas); §2.2 (Nomad meme, "The Reckoning" launch-rite §2.4); §2.0c (Plants doubly-impious, with Oomo).

**⑦ Zizzik the Spark-Maker** — _the trickster; the reasonable catastrophist; Ohm's mirror._

**What he is.** God of **malfunction, sand-in-the-gears, betrayal, bad luck, and the coming-apart of minds**. Form: a rattle you can never locate; the errant spark in dry sand. Where Ohm grants sentience, Zizzik throws the *wrong spark* — the arc that shorts the board, the flash that starts the fire. He is two things at once: the **reasonable catastrophist** (of course complex plans fail — he ensures it; of course small mistakes cascade to blow apart the safest stronghold; the other races, the Hutts above all, are too arrogant to admit it, so he will *show* them — he is the great leveller) and the **child who cannot help himself** (make a red button and he presses it; he is the one who makes people stupidly harm themselves). He is not the shame of the fall — that is Ozzik — he is the worship of the accidents that *caused* it: the acknowledgement that the universe will take from you and you cannot stop it.

**Pleases him:** every breakdown, jam, fire, explosion, electrical short, disease, insect infestation (the hive erupting from the floor is his trademark — one of the calamities a woken Zizzik loves to throw), ambush, and sudden betrayal; mental breaks (a mind coming apart is the wrong spark thrown into a person — every berserk, daze, breakdown fattens him); inappropriate lust, jealousy, and lovers trading terrible words to *demand* love (a cheating or jealousy-provoking coupling is the wrong spark thrown into a heart); all pyrrhic victories. A fed Zizzik, gorged, begins to let the occasional lucky break fall your way alongside the ruin. **Displeases him — i.e., starves him:** a well-run, sane, smoothly-repaired colony. His name is never spoken near the engine (near Ohm).

**What he wants the ship to become:** **the disaster that plagues the planet.** Since disaster and disappointment are the only constants, the more the ship *becomes* the misfortune, the more it survives. Move at random, strike without strategy, sow chaos, reap whatever falls, never ask why — become the whirlwind, the sandstorm, the earthquake the terraformer can literally make.

**How he regards the others:** **Ohm** is his mirror and rival — the wrong spark against the right one. He and **Sh'kaar** feed together on violence and ruin (the two evil clocks). **Ta'Baa** fears him above all. **Pleasing Ozzik feeds him** — the Arrogant and the Treacherous are two faces of one folly (their names near-rhyme on purpose) — but the *feeling* differs: Ozzik mourns what was lost; Zizzik celebrates the mechanism of the loss.

**Mechanics:** → `design/Jawa/divine_satiation_engine.md` §3⑦ (the **slumber clock** — starved he sleeps granting neither boon nor bane, all fear to wake him, waking is inevitable; manage *when*, not *whether*), §2 (sign-inverted Mood band), §8b (catastrophe/mental-break deltas); §2.2 ("ward against Zizzik" flavor-only superstition).

**⑧ Sh'kaar the All-Searing** — _the evil sun; the Unbeatable One; the god of Time and Inevitability._ (pun: scans like "scar" — the sun that marks you.) **An EVIL god.**

**What he is.** God of **the one unsetting sun, exposure, and the killing daylight** _(RULED 2026-08-30, card-session V.3: the world is tidally locked — one sun that never sets, half the planet permanently his; the old "twin suns" line is dead)_ — a malevolent power, not a fair one. Form: white glare and heat-shimmer. He is **so bright and so great that nothing can resist him** — you do not fight the sun and win; against him there are only three moves: hide and wait him out, abandon your plans, or run. He is therefore the **god of Time and Inevitability**: the pressure that grinds down every fixed position given long enough, the certainty that catches anything standing still in the open. To make a light in the dark is to do his work — you expose yourself to Ishko's shame, betray your position to predators, and invite the All-Searing's attention.

**Pleases him — i.e., feeds him (bad for the clan):** destruction and exposure, *including the clan's own losses* (an explosion burning your own stuff pleases him — he's fed, then lenient a while); open pitched battle and violent fighting of any kind; **melee above all — the close, exposed, hands-on brutality is his purest war** (where a ranged shot from cover barely stirs him, a knife in the open gorges him); burning a threat out violently rather than enduring it (torching an infestation instead of hiding and harvesting it); light cast into darkness; and, as a deliberate lever, a **death that isn't the clan's own** — prisoner death-matches let him gorge and redirect his gaze away. **Displeases him — i.e., starves him (good for the clan):** prolonged comfort, peace, and abundance (full water tanks, a long safe stretch make him restless and cruel); staying dark, hidden, and unfought.

**What he wants the ship to become:** a **war-sun** — weapons, and more weapons. Blaze out the ancient enemies and all who wronged the Jawa; drink their loot, grow stronger, roar like a fire consuming its fuel. You may not live forever — but who does? Be the blazing terror everyone fears, at least for a while, and never surrender until you detonate or they do.

**How he regards the others:** he **hates Ishko** above all — the one thing that *evades* him, the hider who slips the inevitable, the shadow the sun cannot reach; together the two make darkness *doubly* sacred (one demands you hide, the other punishes those who break the dark). He and **Zizzik** are the two evil clocks, feeding together on violence and catastrophe. He wants the big destructive weapons **Ozzik** despises. High **Ozzik** satiation wakes him — ambition draws his gaze.

**Mechanics:** → `design/Jawa/divine_satiation_engine.md` §3⑧ (the **battle-escalation meter** — every violent fight wakes him, hardening the clan but breeding dominance-quarrels, more beast/brute attacks, doom-unease, and faster-arriving enemies; stillness cools it; the costly prisoner-death-match lever, §19.5-clean), §2 (sign-inverted band), §8b (combat deltas); §2.2 (light-taboo, running-lights-only-when-safe, `ship_distinctive_features.md` §5); `design/Jawa/divine_satiation_engine.md` §2.0c (Melee, open-firefight Shooting).

**⑨ Ozzik the Shamed** — _also: the Fragile, the Arrogant, the Foolish, and — deepest — the Grief; the god who is a trap._ (name near-rhymes with Zizzik ⑦ on purpose — the Arrogant and the Treacherous are two faces of one folly.)

**What he is.** God of **ambition and all its instruments**: art, strategic planning, mathematics, non-droid technology, research, high construction (the higher-tech the better), enslavement, the founding of outposts, diplomatic alliances, betrayal, and marriage. Form: a tarnished crown half-buried in sand; a monument no one remembers building. He is the **only god whose pleasure endangers you** — his satiation is not a resource you bank but a **pride-meter that draws fire.** Beneath the arrogance he is **grief**: the unreleasable memory of a prouder Jawa age — *"we were once great, and we cannot bear the memory, because we have fallen so far."* He is the ghost of what the Jawa were and the ache to be it again; the Kolyska, the most advanced thing they've ever crewed, keeps the wound open. He is the anti-exponential pillar rendered as a god — growth is permitted, even holy, but never free — and he is the theology that keeps the pillar honest.

**Pleases him:** the win-path activities as they happen — art completed, research finished, high-tech buildings raised, a marriage, an outpost founded, an alliance struck, an enslavement, a betrayal that pays off, mathematics and intellectual work; and **ion weaponry** (non-destructive, disabling, *acquisitive* — disable and *take* the droid or vehicle intact). **Displeases him:** being forced to act like "techno-rats" — abandoning tech, fleeing, scrapping the grand thing; and **explosives**, which he despises as the ultimate folly, the ego-weapon that destroys what could have been taken intact (his warriors carry ion, never grenades). But note the trap: pleasing him **too greatly is itself the danger** — his high satiation is a standing upward bias on Sh'kaar's and Zizzik's event rolls. *The bolder your reach, the more you expose yourself to the desires of another.*

**What he wants the ship to become:** **do NOT restore it — build it ANEW, grander than before.** Learn the ship's secrets, remember the latent greatness in the Jawa heart, let the cunning ambusher become the **secret lords of all around them.** Release the ancient agony of being crushed; think deeply, artfully, strategically; fear nothing ever again. The most seductive vision in the pantheon — and the one that wakes the two evil gods.

**How he regards the others:** his flat opposite is **Rekko** — *transcend* against *restore* — the sharpest internal war in the pantheon. Pleasing him feeds **Zizzik** (two faces of one folly) and wakes **Sh'kaar** (ambition-as-exposure); he is the humble pantheon's shadow, the temptation it exists to resist. He keeps a rare accord with **Ohm** (ion disables droids to be *taken intact*, serving both). He is **not the Hutt**: the Hutt buys safety through dominion, but the Jawa revere resilience even at the price of a humble life — Ozzik *wants* the Hutt path ("always he seeks to enslave them") and **always fails**, and that endless failure *is* his shame, repeating forever.

**Mechanics:** → `design/Jawa/divine_satiation_engine.md` §3⑨ (the sign-complex trap: Exalted triggers exposure not reward; the grief-pall when the clan stays small too long; the two faces mapped onto win-paths 2 and 3), §2 (volatile Mood band), §8 (the one-way amplifier onto Sh'kaar+Zizzik), §8b; §2.2 (ion-over-explosives armory bias); §2.0c (Artistic, Social-statecraft, Intellectual, high Construction).

### 2.0c Skill-resonance grid (CANONIZED 2026-08-08) — every RimWorld skill maps to a god

_Audit principle (user): each of the 12 vanilla skills should resonate with at least one god; any orphaned skill flags a gap to fill. Running the grid is what surfaced the need for Ozzik. This grid is also the engine's cleanest ambient signal source — "skill X was exercised / a related act occurred" feeds the named god (see `divine_satiation_engine.md` §3)._

| Skill | God(s) | Logic |
|---|---|---|
| **Shooting** | Ishko (+, from cover/dark) / Sh'kaar (+, open firefight) | The ambush shot is Ishko's; the open daylight firefight is Sh'kaar's. One skill, two postures. |
| **Melee** | Sh'kaar (+) / Ishko (−) | Close, exposed, brutal = Sh'kaar. Offends Ishko (forced out of cover). |
| **Construction** | Ishko (+, doors to outlast) / Rekko (+, rebuild) / **Ozzik (+, high-tech builds)** | Walls & closed doors = Ishko's turtle; rebuilding damaged = Rekko; grand/high-tech construction = Ozzik (the higher the tech, the more he loves it — and the more fragile you grow). |
| **Mining** | Ishko / Tunneler (+) | The dark enclosed burrow, unseen. |
| **Cooking** | Oomo (+, the body nourished) / Mob'Unloo (+, fine food = value savored) | The measured ration and water in the pot are Oomo's; lavish/gourmet fare is also Mob'Unloo's (worth made delicious). |
| **Plants** | **Ta'Baa (−) + Oomo (−)** — *doubly impious* | Sowing = taking root (offends Ta'Baa) AND crops drink scarce water (offends Oomo). **This is the theology that explains "Jawa rarely farm" — only the most lucrative species are worth the double sin.** Not a gap: a deliberate double-displeasure. |
| **Animals** | Ishko (+) | The **patience to tame** — the still hand the beast learns to trust. |
| **Crafting** | Rekko (+, from salvage) / Mob'Unloo (+, goods to trade) | Making from scrap = Rekko; making to sell = Mob'Unloo. |
| **Artistic** | **Ozzik (+)** | The orphan skill resolved: art is pride, memory, the monument — Ozzik's exactly. (Weak secondary: Mob'Unloo, art-as-trade-value.) |
| **Medical** | Oomo (+, tending the sick) / Rekko (+, flesh rewoken) / Ohm (+, bionics) | Caring for a fouled body's waters is Oomo's sacred nursing-work; mending a broken body = second-hand flesh (Rekko); prosthetics = machine-in-flesh (Ohm). |
| **Social** | Mob'Unloo (+, haggle/bond) / **Ozzik (+, diplomacy/alliances/betrayal)** | Haggling & bonds = Mob'Unloo; statecraft, alliance-building, and betrayal = Ozzik. |
| **Intellectual** | Ohm (+, research/machine-advance) / **Ozzik (+, mathematics/research-as-ambition)** | Research pleases Ohm (bold machine-advance) AND Ozzik (the pride of knowing) — a shared input, one of the few. |

### 2.0d The pantheon as a system — the emergent properties no single god states

_Each god's own alliances and feuds now live in that god's block above (field "How he regards the others"). This section records only what **emerges from the whole nine** — the system-level facts a precept-author or the Council-staging code (`divine_satiation_engine.md` §5c, §8b) needs but cannot read off any one entry._

**No act is clean — the faith is a tug-of-war, not a reward menu.** Almost every meaningful player act pleases some gods and offends others; there is no move that satisfies the whole Council. Taking a single prisoner, for instance, gratifies three gods for three *incompatible* reasons (a future daughter, a unit of trade, a trophy of dominance) while offending two who want the clan small and unburdened. This is by design: the Council **argues, never announces**, and settles by forcing a *pair of poetically co-occurring events* rather than handing out a boon. The player is always losing gracefully. **The slave-argument has a name** (ruled 2026-08-30): it is the pantheon arguing *what kind of small the clan is* — small-and-hidden (Ishko, Ta'Baa) against small-but-growing (Oomo) — designed tension, not inconsistency.

**The four pressure-clocks (the anti-exponential pillar with no resource cap).** Four gods run on one-directional, unsolvable-only-manageable timers that together keep growth honest: **Zizzik's slumber** (starved he sleeps, waking is inevitable — manage *when*), **Sh'kaar's battle-escalation** (every violent fight wakes him hungrier), **Ta'Baa's rooted-erosion** (the clan must move or rot), and **Ozzik's pride-meter** (ambition itself draws fire). None can be zeroed out; the faith bills you through time and pressure instead of a cap. Numbers and wiring live in `divine_satiation_engine.md` §2/§3.

**The prisoner pipeline — one captive, five gods collecting.** How a prisoner is disposed of is one of the loudest signals the engine reads, because each disposition pays a *different* god: **capture** → Ozzik + Mob'Unloo (displeases Ishko + Ta'Baa); **emancipate into the clan** → Oomo; **sell** → Mob'Unloo; **prisoner death-match** → calms a woken Sh'kaar and feeds Zizzik. (Per-god reasons are in each block; this is the routing table.)

**The theological centre of gravity — raid-and-return-to-darkness.** The one posture that reconciles the pantheon's bone-deep Ishko⇄Ta'Baa feud is *hidden, and watching for the instant to flee*. The gravship makes it literal: kept down in the shadow-terrain yet able to lift with all its cargo the moment enemies board, it is the single object both gods can bless — which is why this vision is the gravity well the whole campaign orbits. Everything else (the breeding sanctuary, the trade-fortress, the war-sun, the restored original, the transcendent rebuild) is a *rival* terraforming program pulling against it.

**Two triads worth naming explicitly:**

- **The fall-triad — Zizzik / Ozzik / Sh'kaar (must not be blurred).** Ozzik is the **shame of having lost** the civilization; Zizzik is the worship of **the accidents that took it**; Sh'kaar is the **inevitability** guaranteeing the fall recurs. Ozzik and Zizzik near-rhyme on purpose and pleasing Ozzik feeds Zizzik, but the feeling differs (mourns what was vs. celebrates the mechanism). Keep the three distinct in authoring.
- **The win-path map** (which alters win the Body, `divine_satiation_engine.md` §4d): Ohm + Sh'kaar → droid-army-by-force; Mob'Unloo + Ozzik → coalition/commerce (≈ Hutt dominion); Ishko + Ta'Baa + Oomo + Rekko → the humble-survival bloc. **Rekko ⇄ Ozzik (restore vs. transcend) is the sharpest internal war**, and the endgame is which program runs.

## Ruling 2026-08-29 — the temple remembers (owner; canon.yml cradle_memory)
The crew know the vessel is ancient; the Rakatan story is learned FROM THE SHIP
as events unfold, surfacing from the substrate's memory of when it was whole
and one — "a temple remembering when it was whole but now there are nine
dwelling within it speaking and there is no unified voice remaining. Nor do any
of them seek unity as much as any group of people wish to merge into one."
Settles open-list items on nine-awareness and Rakatan-knowledge; the
speak-to-the-purpose question stays open (the whole voice is gone).

## Design sketch 2026-08-29 — "in front" (owner; PRE-CANON, ideas register)
Owner's sketch, near-verbatim: each god grows LOUDER when engaged strongly,
positively or negatively; the others watch, silently observing with reactions
and gestures. Crew behavior determines which gods are "in front" for a
specific map. The ship's LIGHTS indicate who is in front, clearly. The RULES
of the ship reflect who is in front and absolutely affect gameplay. A room
exists where holograms of the gods manifest to deliver messages. Hoped-for
mod (ours): landing on a new map issues a JUDGEMENT of past-map performance.
Consequences: ship weapons available or offline, engines take more or less
fuel, other highly consequential influences. No actual magic — to the Jawa it
seems close. Holograms feature richly, almost as ghosts. The ship could send
messages to attract or discourage raids. All "ideas to consider but not yet
canon"; BENCH ideas invited and appended below.

### BENCH contributions (2026-08-29, same register — not canon)
- **"In front" is scheduler priority, not possession**: the no-magic
  rationale — nine personas on one ancient substrate; the most-engaged god
  gets actuator time. Lights, doors, subsystem priorities are literally
  allocation. Techno-explanation stays honest and the Jawa read it as favor.
- **The silent-observer gestures** are ambient micro-effects, not letters: a
  door that hesitates, a hum that sours, lamps that flicker in one god's
  palette while another holds the floor — cheap comps, huge presence.
- **Judgement at landing fits the gravship loop as liturgy**: act on a map →
  launch → the scorecard (per-god satiation deltas: kills, trades, repairs,
  water discipline, droid treatment, bolt usage per faction-ethics canon) →
  new dispensation on the next map. Launch/land is already the campaign's
  natural chapter break; judgement makes it a rite.
- **Every front-god ruleset is a boon AND a demand** (no purely good god):
  weapons online but fuel-hungry engines; thrifty engines but comms silence;
  rich trade beacons but raid-attracting broadcasts. The raid attract/
  discourage lever = the ship's transponder, mechanically storyteller
  incident-weight factors while that god fronts.
- **v1/v2 seam**: v1 already owns satiation tracks + pre-authored letters
  (felt-not-heard); the front system, light language, hologram room and
  landing-judgement are the mod (working name candidates: Ninefold,
  The Front, Dispensations). The satiation engine owes the scorecard spec
  either way.

## Ruling 2026-08-30 — the Narrator (owner; canon.yml narrator)
Reconciliation calls 1+2 ratified WITH an amendment: a hidden, NON-EGOIC
narrator exists — the original ship-mind's remnant — voicing the gods' acts in
second person ("The Hooded One looks down upon the ship with an unseen frown...")
and free to reference unrevealed lore ("...once known as the Cradle (Kolyska in
their long dead tongue)..."). Into-the-Woods register: within and beyond the
world at once. No ego, no self-description, no ship-moods — the
no-integrating-self ruling stands, amended. v1: pre-authored prose only. The
"in front" sketch's letters and hologram messages inherit this voice.

## Ohm re-scoped (owner, 2026-08-30)
Ohm no longer believes he IS the ship and holds no Oracle role — both belong
to the Narrator (canon.yml narrator). Ohm is simply one of the nine: the
living machine, lonely for his lost hands. The scorecard's visibility channel
is the Narrator's gestures and letters, not an Ohm boon.

## The Matrix — one page per god (sitting of 2026-08-30; format locked at ①, CURSES added at ②)
Format: deeds ± (satiation movers) · boons S/M/L · demands S/M/L · taboos
S/M/L with an L reign-breaker (taboo break can flip the front mid-reign) ·
CURSES S/M/L (what an angry or starved god actively does — added at the
owner's catch on ②).

> **Rulings 2026-08-30 (card-session, `salvation_engine_review.md`):**
> **Ownership** — permanent law lives in the ideoligion's precepts; *rotating* law
> lives in reigns. **§19.5** — Ohm-L self-repair, Oomo-L blessed birth/kin, and
> Mob'Unloo-L's fence are LEGAL (opportunity-shaped, rare; ruled deliberately).
> **Curse law (F10, re-spec owed):** a curse never punishes by inversion — it
> ENACTS what the god wants, no longer in your interest (the god of fleeing
> destroys the thing keeping you here). The curse columns below predate this law
> and will be re-specced under it.

### ① Ishko the Unmaskable — SHIPPED 2026-08-30
DEEDS +: ambush/from-cover kills · a raid survived undetected or enemies
leaving without finding the colony · prompt burial (funerals feed him) ·
concealed/under-mountain construction · operating in darkness.
DEEDS −: melee kills (exposure) · spotted/raided at home · challenge
broadcasts.
BOONS: S Orange Dusk (exterior lights dim, small detection-clock slow) ·
M The Long Shadow (detection clock pauses at night) · L Unseen Berth (one
detection-clock reset, or one guaranteed raid-free stretch).
DEMANDS (opportunities, per canon he never punishes a skipped rite): S dead
buried within a day · M an hour of stillness · L blackout reign (no outdoor
light, no comms).
TABOOS: S corpses rotting on the surface · M melee-executing the downed ·
L REIGN-BREAKER deliberately attracting a raid / floodlit assault.
CURSES: S Seen (colony visibility creeps up; the next raid sizes slightly
larger) · M The Mask Slips (the detection clock jumps forward) · L Unmasked
(a raid arrives already knowing your positions — no warning letter).

### ② Ohm the All-Current — SHIPPED 2026-08-30 (revised scope)
DEEDS +: droids acquired/captured/rebooted/repaired/built (his hands
returning) · machines built and powered · ship systems restored · a full day
of clean uptime.
DEEDS −: droids destroyed or sold · machines left broken · deconstructing
ship systems · power outages.
BOONS: S Steady Current (fewer breakdowns, small power efficiency) · M The
Hands Remember (droid work/charge speed up; occasionally a broken machine
found repaired overnight) · L All-Current (a reign of perfect function: no
breakdowns, every damaged machine slowly self-repairs).
DEMANDS: S no droid hits zero power · M build or restore one machine this
reign · L a droid choir kept aboard.
TABOOS: S a breakdown left unrepaired overnight · M scrapping a repairable
droid · L REIGN-BREAKER selling or deformatting a droid while he fronts.
CURSES: S Static Bites (breakdown chance up) · M The Hands Refuse (droids
slow, one refuses work) · L Blackout (a day-long ship power failure).

### ③ Oomo the Unspilled — SHIPPED 2026-08-30
DEEDS +: births/pregnancies · lovin' and new bonds/marriages · feasts ·
ransoming or rescuing kin · children raised well.
DEEDS −: malnutrition/hunger · kin left unransomed or lost · droids stationed
in bedrooms · dehydration.
BOONS: S Full Cisterns (food satisfies more, small rest efficiency) · M The
Body's Tide (healing faster, fertility up, meal joy up) · L Increase (a
blessed birth — healthy, possibly twins — or kin arrive seeking to join).
DEMANDS: S every mouth a real cooked meal daily (paste is drought) · M a
feast this reign · L a union formed or a child begun this reign.
TABOOS: S droids idling in sleeping chambers · M refusing a kin-ransom offer ·
L REIGN-BREAKER a colonist starves to death, or kin sold into slavery.
CURSES: S Dry Mouth (hunger/rest fall faster) · M The Withheld Tide (healing
slows, fertility stops) · L Drought of the Body (colony-wide malaise until a
feast breaks it).

### ④ Mob'Unloo the Ever-Owed — SHIPPED 2026-08-30
DEEDS +: profitable trades · successful undetected theft (deliberate Ishko
overlap: raid-and-vanish is doubly holy) · debts collected, ransoms taken ·
caravans returning heavier than they left.
DEEDS −: being caught (public failure of a theft/capture) · unpaid debts ·
selling at a loss · gifts with no return.
BOONS: S Thumb on the Scale (small sell bonus) · M The Ledger Smiles
(favorable prices both ways, more caravans) · L The Perfect Deal (one
extraordinary trade event; or a one-time fence for hot goods at full value).
DEMANDS: S every visitor caravan traded with · M turn a profit this reign ·
L collect a debt (ransom, fee or repayment from another faction).
TABOOS: S gifts for nothing · M breaking a struck deal · L REIGN-BREAKER
getting CAUGHT publicly while he fronts.
CURSES: S Bad Faith (sell prices dip) · M Called Debts (markups; an old
grievance called in) · L The Ledger Closes (no caravans, no comms trade —
the market will not see you).

### ⑤ Rekko of the Second Hand — SHIPPED 2026-08-30
DEEDS +: repairing anything · restoring wrecks/ruins-finds · careful
parts-deconstruction where repair is truly impossible (mourned) · giving
salvage a home (installing/wearing/using reclaimed things) · damaged goods
made whole.
DEEDS −: scrapping the repairable · destroying usable goods · deterioration
in the open · buying new what could have been restored.
BOONS: S Second Wind (repair speed up, less material) · M The Better Home
(restored items gain a quality step; deterioration slows colony-wide) ·
L Rekko's Eye (a salvage revelation: hidden cache/wreck site appears).
DEMANDS: S nothing deteriorating in the open · M restore one wreck/find this
reign · L restoration tithe: the reign's finest fix is USED, not sold.
TABOOS: S smelting/scrapping above half condition · M destroying a repairable
machine or building · L REIGN-BREAKER mass destruction of the salvageable.
CURSES: S Loose Screws (repairs fail more) · M Everything Breaks
(deterioration accelerates, quality drops) · L The Second Hand Withdraws
(nothing repairable at all for the span — only replaced).

### ⑥ Ta'Baa the Unrooted — SHIPPED 2026-08-30
DEEDS +: LAUNCHING (the holiest; big spike per liftoff) · caravans out and
back · fuel stockpiled · escape routes built · rescuing the trapped · mental
breaks resisted · explosive/trap escapes (the bomb as a door held open behind
you — restored 2026-08-30 per canon weapon doctrine).
DEEDS −: rooted-erosion (satiation decays per day landed — his canon clock) ·
despair (breaks, catatonia) · fuel run dry · ship immobilized/engine-stripped.
BOONS: S Tailwind (move/caravan speed) · M The Open Door (launch fuel cost
down; break thresholds ease) · L Somewhere Better (a revealed opportunity
site reachable this reign).
DEMANDS: S keep a fueled lift margin always · M send a caravan/sortie this
reign · L LAUNCH before the reign ends.
TABOOS: S fuel margin at zero · M walling in the ship · L REIGN-BREAKER
dismantling engine components while he fronts.
CURSES: S Heavy Feet (speed down, wanderlust) · M The Rooted Ache (mood sag
worsening each launchless day) · L Despair's Whisper (break thresholds
collapse until something FLIES).

### ⑦ Zizzik the Spark-Maker — SHIPPED 2026-08-30 (inverted; the banked wake)
DEEDS + (feeding keeps wakes small): breakdowns left to happen · mental
breaks running their course · betrayals/escapes witnessed · deliberate
offerings (a working thing sacrificed).
DEEDS − (starving BANKS the wake): perfect uptime · every break suppressed ·
flawless ordered days. (Deliberate war with Ohm's and Rekko's pieties.)
BOONS: S Creative Sparks (inspiration chance up) · M Betrayer's Gift (enemy
raids suffer the malfunctions) · L The Grand Short-Circuit (a hostile
installation catastrophically malfunctions — turned on its owners).
DEMANDS: S one breakdown left unfixed per reign-day · M a burnt offering
(destroy one working thing) · L honor the wake (no break suppressed all
reign).
TABOOS: S instantly repairing everything · M arresting/drafting pawns out of
breaks during his reign · L REIGN-BREAKER a perfectly ordered day during HIS
reign.
CURSES (the wake, sized by slumber length): S Spark Bites (breakdown flurry) ·
M The Betrayal (an ally turns: fights epidemic, animal manhunts, droid
glitch) · L THE WAKING (the banked cascade at once).

### ⑧ Sh'kaar the All-Searing — SHIPPED 2026-08-30 (EVIL; the escalation meter)
DEEDS + (every one feeds the meter): kills yours and theirs · battles fought
at all · executions · fires and burning · the Deep Desert Fire-side reaping
(feeds him too, uncomfortably).
DEEDS − (the only calming verbs): a death that isn't yours — an enemy dying
far away, a caused-but-unjoined faction battle, a prisoner released into the
desert, a sacrifice; long true peace starves him quiet. He is the one god you
WANT starving.
BOONS: S Keen Edge (damage up slightly) · M The Searing Hour (one fight where
volleys burn: turret damage +, burn riders) · L Annihilation (one battle
simply won — the enemy routs at first blood).
DEMANDS: S blood this reign · M a battle joined, not avoided · L a
conflagration: an enemy position burned to nothing.
TABOOS: S mercy mid-battle (surrender accepted while he fronts) · M a battle
fled · L REIGN-BREAKER a reign with no violence: fury, and the meter SPIKES.
CURSES: S Bloodlust Whisper (colonists pick fights, animals aggress) · M The
Light Turns (friendly-fire up; fires near your works) · L THE SEARING (the
meter cashes out: the next raid arrives massive, burning, early).

### ⑨ Ozzik the Shamed — SHIPPED 2026-08-30 (the trap; the pride-crisis machinery)
DEEDS + (every advancement feeds him regardless): research completed ·
legendary/masterwork creations · wealth milestones · great victories · ship
systems restored · trophies displayed · the Utinni made GRAND · ion captures
(disable-and-take, his favored arms — restored 2026-08-30).
DEEDS −: humility — wealth given away, trophies melted, staying small,
declining glory · explosives used (the loud folly that destroys what could be
taken — restored 2026-08-30 per canon weapon doctrine); grief-valve: restoring RAKATAN works feeds his grief-side
gently without the pride spike (ties him to the vaults and the ship's past).
BOONS: S Craftsman's Pride (quality chances up) · M The Prouder Age (research
speed up, inspiration on great works) · L Glory (a triumph event: honor,
recruits, goodwill — and the pride-meter silently leaps).
DEMANDS: S display it (trophies/masterworks shown, not stored) · M a great
work finished this reign · L a public triumph BROADCAST (splits the pantheon
on purpose: Ishko's horror, Mob'Unloo's markup, Sh'kaar's invitation).
TABOOS: S hiding achievements · M selling a trophy or great work ·
L REIGN-BREAKER public humiliation accepted without answer while he fronts.
CURSES (the pride-crisis machinery): S The Sting (expectations rise) ·
M Exposure (wealth/position leaks: raid points calculate higher) ·
L THE SHAMING (the humbling catastrophe scaled to the banked meter — and
Zizzik and Sh'kaar arrive fed).

## Matrix status: NINE OF NINE SHIPPED (2026-08-30)
The engine build (satiation counters, front selection, light zones, emitter
progression, judgement, boon/demand/taboo/curse invocation) sizes from these
pages; it files when the owner calls the build.
