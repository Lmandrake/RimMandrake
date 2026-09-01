<!-- status: DRAFT PROPOSAL for owner review — brainstorm sitting 2026-08-31, not ruled. -->

# Reign-Modes — when a god stops sending letters and starts rewriting the world

> *"Think about many events that could happen if a god becomes too angry or too
> pleased: the world seems to switch into a 'different mode' that make the
> players fascinated, excited, but eventually yearn to get back to normalcy."*
> — owner's spark, 2026-08-31

Not a new pantheon, not a new mechanic family — **one escalation rung bolted
onto the L-tier boon/curse the matrix already ships**
(`divine_satiation_engine.md` §"The Matrix", nine-of-nine SHIPPED 2026-08-30)
and onto the pressure-clocks `salvation_engine_review.md` already named (F11
Zizzik's bank, F13 intercession, F14 reign-parking, F17 interface). Every mode
below is wired to a meter the engine already tracks. Read this as: *what
happens when an L-tier event refuses to resolve in one letter and lasts
days instead.*

## 0. Prior art, and where it stops

RimWorld already has the primitive — `GameConditionDef` — and two shipped
products prove the shape and show its ceiling. **Anomaly's Unnatural
Darkness** (`rimworldwiki.com/wiki/Unnatural_darkness`): map-wide, threshold-
gated, hard duration (6–8 days) with an early-exit lever (destroy the three
noctoliths), and a *behavioral* rule change — light itself becomes damage, not
a stat debuff. **Anomaly's Death Pall**: shorter (1–3 days), turns your own
dead into the hazard. **Vanilla Events Expanded's Purple Events**
(`github.com/Vanilla-Expanded/VanillaEventsExpanded`): long (15–120 days),
rare (3-year gate, 300-day cooldown), built explicitly to force *adaptation*.
None of the three are attributable to a person the player has a relationship
with, none carry a genuine opportunity (only an inconvenience to survive),
none accrue a legible cost that argues for its own end, and none leave a
scar. A REIGN-MODE is a god the player has been dealing with for forty hours
choosing to stop negotiating in letters — a character beat, not a difficulty
spike.

## 1. Entry — existing thresholds, held

- **Pleased-lock (too pleased):** the front god (`in_front`, canon.yml) is
  **Exalted** and has crossed F14's **decadence** threshold — decadence
  stops thinning boons and starts becoming a fact of the map.
- **Angry-lock (too angry):** an **M/L curse fires and its exit-verb goes
  unpaid past a grace window** (3 days M, 1 day L) — the curse was warned
  per F9; going unpaid promotes it into a mode instead of repeating louder.
- **Sh'kaar's inversion is honored, not patched around:** his pleased-lock is
  "fed too long," his angry-lock is "starved-into-suffocating." See §7⑧.

One `ReignModeGameComponent` reads the vector on state transitions only
(front-god change, curse-timer expiry) — never per-tick, per anti-exponential
discipline.

## 2. Strain — the mechanism behind "yearning"

Every active mode carries **Strain (0–100, resets on entry)**, rising daily at
a rate set by the mode's matrix-derived severity. Strain does exactly three
things: **(a)** feeds F14's jealous-watcher clock faster — a mode accelerates
its own challenge; **(b)** cheapens the exit-verb over time, floor 40% — the
longer the fascination runs, the cheaper leaving gets, which is backwards from
a punishment curve and correct for a mood; **(c)** past Strain 60, unlocks a
substitute exit: an F13 disposable-shrine offering sized to *remaining*
Strain, labor for time, never silver (§19.5-clean). Strain is never a
displayed number — read only through the F8 gesture layer and Narrator
adjectives sharpening.

## 3. Exit, stacking, memory

**Exit** follows F10: every mode states its price in the god's own currency —
pleased-locks exit by spending the gift down (Unburdening-shaped), angry-locks
exit by the curse's own stated verb. **Stacking:** only the front god holds a
full mode (same "one front" law as `in_front`). A second god independently at
an extreme doesn't open a second mode — it surfaces as one ambient bleed
sentence (F8), and, only for the four canon feud pairs F7 already named
(Ohm⇄Zizzik, Ishko⇄Sh'kaar, Rekko⇄Ozzik, Oomo⇄Mob'Unloo), one authored
interference line recoloring the front mode's Opportunity or Cost by a fixed
small amount — four authored lines, not a matrix. If the front changes
mid-mode (F14 challenge, or a violent-swing flip), the mode **breaks**: no
exit payment, a distinct "interrupted reign" line, and the scar records
*broken* rather than *honored* — the god remembers being cut off. **Memory:**
every resolution writes one entry to a flat per-colony **Reign-Scars ledger**
— `{god, mode, resolution, one small permanent consequence}` — feeding F1's
folk-practice lines and F16's tile-reading. No scar is ever a stat bonus
(§19.5): flavor, room character, or opportunity-eligibility only.

## 4. Announcement (F17)

Entry gets the full F9 signature treatment plus one thing reserved only for
modes: a distinct sting, never reused for an ordinary boon/curse — the sound
that means the world just changed, not just today. For the duration: the
reign-calendar date line appends the mode's name; the letter-rewrite layer
re-titles *every* vanilla incident through the mode's lens, not just the
trigger; affected buildings/pawns carry an inspect tag. Exit gets a calmer
sting — the held breath let out.

## 5. The eighteen modes

Fields: **Look** · **Rules** (2–3, behavioral not stat) · **Opportunity** ·
**Cost/Yearning** · **Exit** · **Mechanics** (`GameConditionDef` + C# need) ·
**Scar**.

### ①-P Ishko — "The Unseen Reign" (pleased-lock)
Look: exterior light caps at dusk-level, permanently blue-grey noon. Rules:
no light source above a fixed low radius outdoors; sight radius cut equally
for player and enemy; ranged accuracy outdoors drops for everyone.
Opportunity: guaranteed unseen passage through hostile territory for the
mode's span. Cost/Yearning: solar and crop growth quietly starve; the same
blindness hides threats closing on you too. Exit: an enemy killed from cover,
visibly. Mechanics: `GameConditionDef` overriding `SkyManager` glow curves +
Harmony patch on outdoor ranged accuracy. Scar: one room permanently reads
"shadowed" (stealth-pawn mood only).

### ①-A Ishko — "The Unmasking" (angry-lock)
Look: no shadow anywhere, flat shelterless glare. Rules: sneak/stealth jobs
disabled outright; colony position broadcast to every regional hostile,
continuously; raid arrivals go openly telegraphed instead of ambush. Opportunity: the honest pitched battle the religion normally forbids becomes
correct play — you're already unmasked. Cost/Yearning: raid frequency and
quality rise; caravans can't run safely. Exit: kill from cover successfully,
here, proving the dark still works. Mechanics: `GameConditionDef` forcing
map-wide visibility true; Harmony patch disabling sneak/ambush JobGivers and
the raid arrival-mode selector. Scar: the tile marked Sh'kaar-adjacent in
sacred-sites (F16), permanently a little more exposed.

### ②-P Ohm — "The Waking Choir" (pleased-lock)
Look: every powered light stays lit all night, low constant hum. Rules:
workbenches run unassigned "ghost jobs" overnight, choosing their own
project; machines refuse manual power-off; turrets/doors occasionally act on
their own (usually helpfully). Opportunity: genuine free passive production —
the best economic gift in the set. Cost/Yearning: rising power draw and heat
(visible glow draws Sh'kaar, offends Ishko); "the ship doesn't need us."
Exit: bring one more droid online in his name. Mechanics: `GameConditionDef`
+ a small autonomous-bench ThinkNode (new; closest pattern: Anomaly's
mechanoid-hive logic); Harmony patch blocking manual power toggles. Scar: one
workbench keeps the ghost-job behavior forever, rarely, free.

### ②-A Ohm — "The Body Wakes" (angry-lock, sustained)
Look: the hull thrums like a held chord continuously. Rules: manual overrides
fail a real fraction of the time; one system malfunctions daily, announced
each morning; power quietly favors Ohm's own altar/lights over player
priority. Opportunity: the ship occasionally defends itself unbidden —
autonomous turret fire or a door sealing against a raid before you react.
Cost/Yearning: fuel/power drain toward his purposes; daily unpredictability
compounds risk. Exit: a droid brought online — his hands returned. Mechanics:
promotes the shipped L-curse into a `GameConditionDef` that re-fires the
daily-malfunction roll instead of resolving once; small `GameComponent` to
pick/announce it. Scar: one permanently misrouted power junction (flavor
only).

### ③-P Oomo — "The Green Hour" (pleased-lock)
Look: condensation everywhere; humid air even in desert light. Rules:
hydroponics/crop yield doubles; romantic advances auto-succeed; courtship
jobs preempt work queues. Opportunity: free population growth. Cost/
Yearning: the boom outpaces housing and food-per-mouth math — the gift
becomes its own logistics crisis. Exit: a feast held explicitly to "close the
tide." Mechanics: `GameConditionDef` doubling hydroponics yield via
`StatPart`; Harmony patch on romance-interaction success roll. Scar: one
Jawa born during the mode carries a minor permanent flavor trait.

### ③-A Oomo — "The Long Drought" (angry-lock)
Look: full cisterns, light still reads bone-dry. Rules: stored water potency
halved unless underground/shielded; thirst debuffs apply regardless of
supply; romantic advances refused colony-wide. Opportunity: points at a
literal fix — a Sacred Site oasis (F16) becomes reachable specifically now, a
pilgrimage that ends the drought early. Cost/Yearning: morale stall, no
population growth. Exit: the pilgrimage, or patient endurance to duration
cap. Mechanics: `GameConditionDef` applying a thirst-multiplier Hediff; reads
the pre-authored sacred-sites tile pass, no new tile generation. Scar: the
found oasis is permanently promoted to a Sacred Site.

### ④-P Mob'Unloo — "The Open Market" (pleased-lock) — *the owner's spark, realized*
Look: trader icons converge on the colony from every direction on the world
map. Rules: every faction's traders reroute in at drastically increased
frequency; prices favor the colony hard both ways; storage overflow forces
goods into the open (silos physically burst — excess spoils/sits exposed).
Opportunity: a transformative trade windfall for the mode's span. Cost/
Yearning: raid math scales visibly off displayed wealth — raids follow the
wealth; the glow of prosperity is a beacon. Exit: deliberately turn away a
caravan, publicly — "closing the scale." Mechanics: `GameConditionDef`
multiplying trader-visit weight via `IncidentWorker_TraderCaravanArrival`;
stack-capacity override forcing overflow onto open ground; existing F12/F18
visibility-wealth hook reads the spike natively — no new threat math. Scar:
one trade route permanently favors the colony by a small margin.

### ④-A Mob'Unloo — "The Collectors" (angry-lock)
Look: every price display reads in red. Rules: every faction ever traded with
sends a collection caravan over the mode's span; any item carrying an
unpaid/stolen claim (`ownership_settlement_spec.md`) is actively contested by
repossession attempts; trade prices collapse near-zero. Opportunity: collect
a debt of your own FROM another faction — feeds the ledger from outside,
ends the mode early, flips it into leverage. Cost/Yearning: constant
negotiation drain, goodwill losses. Exit: the outside debt collected, or a
genuine tithe-profit offered. Mechanics: `GameConditionDef` scheduling
repeated `IncidentWorker` visits keyed to faction-relation history; reads
`RM_Property`'s existing claim vector, no new ownership tracking. Scar: one
faction relation carries a permanent small "settled" bonus if collected.

### ⑤-P Rekko — "The Second Life" (pleased-lock)
Look: every surface reads faintly mended rather than broken. Rules: nothing
deteriorates for the duration; deliberate scrap/smelt above ruined condition
fails outright — the material "won't give up its form"; every repair this
reign gains a bonus quality step. Opportunity: a free quality-and-
preservation pass across the whole colony. Cost/Yearning: the scrap-for-
resources economy stops working entirely. Exit: a wreck restored, its
salvage put back into use, not stored. Mechanics: `GameConditionDef` zeroing
the deterioration `StatPart` map-wide, blocking smelt/deconstruct
designators on repairable things. Scar: one item permanently flagged
"unbreakable-in-spirit" (flavor only).

### ⑤-A Rekko — "The Long Reclamation" (angry-lock)
Look: metal-on-stone scraping from the scrap-zone at night, unlocatable.
Rules: unused/unworn items have a nightly chance to relocate off the map
(reclaimed); damaged buildings deteriorate faster; idle stockpiles are
targeted first. Opportunity: nearby derelicts go temporarily dormant/
defenseless during the mode — a salvage bonanza while his attention is on
punishing your hoard. Cost/Yearning: forces active use-it-or-lose-it
discipline, stockpiling stops working. Exit: one great derelict woken and
repaired, not left. Mechanics: `GameConditionDef` triggering a nightly
item-despawn check on unused stock; the dormant-derelict flag is read by the
Space Tower dungeon content already installed. Scar: one repaired derelict
becomes a small permanent local-map landmark line.

### ⑥-P Ta'Baa — "Fair Winds" (pleased-lock)
Look: sky reads perpetually clear and close, constant wind sound. Rules:
launch/relocation cost drops near-zero; idle pawns auto-start wanderlust
behaviors instead of true idle/joy; rooted rest doesn't fully restore mood.
Opportunity: cheap chainable relocation — multiple "somewhere better" sites
revealed in sequence for as long as it runs. Cost/Yearning: the colony can
never consolidate; defenses never mature; the crew audibly wants to just
stay. Exit: land and hold one site through a full rite without launching.
Mechanics: `GameConditionDef` zeroing launch fuel via `CompLaunchable` stat
override; small ThinkNode nudging idle pawns to wander-flavored jobs. Scar:
the next site landed on gets a permanent small "chosen at last" mood bonus.

### ⑥-A Ta'Baa — "The Long Walk" (angry-lock) — *the owner's spark, realized*
Look: a low departure-whistle in the corridors at night, doors drift toward
the berth. Rules: nightly, one unrestrained pawn's job is overridden — a
compelled walk toward the map edge; interception requires an active chase
(no normal orders mid-walk); an uncaught sleepwalker risks exposure/
heatstroke and, past a duration, can be lost. Opportunity: tailing a
sleepwalker rewards discovery — they walk toward something real (a cache, a
Sacred Site), divinely guided, not random. Cost/Yearning: colony-wide sleep
deprivation, real risk of losing a pawn if unattended. Exit: a caravan sent
out and brought fully back — motion offered freely instead of stolen.
Mechanics: `GameConditionDef` + nightly `JobGiver_Sleepwalk` forcing a
wander-to-edge job (pattern: Anomaly's Unnatural Darkness forced-behavior
injection); needs a "sleepwalker found something" resolution hook. Scar:
whatever was found becomes a permanent credited discovery — or, rarely, "the
walk that found nothing," its own kind of scar.

### ⑦-P Zizzik — "The Kind Chaos" (pleased-lock) — *the owner's spark, realized*
Look: sparks fly harmlessly off machinery; lit fire burns a slightly wrong,
low colour. Rules: fire cannot start by accident anywhere for the duration;
any fire lit *deliberately* never self-extinguishes — burns until put out or
fuel runs out, spreading if unchecked; enemies set alight burn markedly
longer. Opportunity: total safety for industrial fire — refineries,
crematoria, incendiary traps run flat-out with zero accident risk, and
deliberate fire combat becomes devastating. Cost/Yearning: a forgotten
deliberately-lit flame becomes a slow-building hazard days later; dry desert
wind raises the stakes as the mode runs long. Exit: a burnt offering — one
working thing deliberately destroyed. Mechanics: `GameConditionDef` zeroing
the accidental-fire `IncidentWorker` weight; patches deliberate-fire
extinguish logic to never self-douse. Scar: one hearth/forge permanently
flagged as never having gone cold since.

### ⑦-A Zizzik — "The Long Circuit" (angry-lock, sustained)
Look: total silence where the rattle used to be, stretched across days.
Rules: every mechanical/electrical device carries a real, escalating daily
malfunction chance — a rolling background generator, not one cascade;
automated systems can't be fully trusted; mental breaks resolve strangely — a
chance the break accidentally helps. Opportunity: inspiration chance sharply
elevated colony-wide — a "surf the chaos" window. Cost/Yearning: rising
equipment attrition; the fascination curdles into distrust of your own
machines. Exit: the controlled-waking rite (F11) spent deliberately,
converting remaining Strain into one shaped disaster instead of grinding on.
Mechanics: promotes the shipped bank system into a `GameConditionDef` that
re-rolls instead of firing once — reuses F11's machinery wholesale. Scar: the
reign's most dramatic accidental-good outcome is recorded as a named,
retold incident.

### ⑧-P Sh'kaar — "The Long Noon" (pleased-lock, evil-inverted)
Look: flat white light at all hours, no true shade anywhere. Rules:
battle-fervor toughness permanently active on every pawn; animal/brute
aggression fires on a predictable schedule instead of randomly; all
stealth/ambush tooling disabled — Ishko's tricks don't work here.
Opportunity: guaranteed, telegraphed fights make the mode an arena — prepared
combat for gear and trophy farming. Cost/Yearning: attrition without rest,
compounding doom-unease — being *fed* is bad for you even when it feels like
a gift, per his inverted sign. Exit: a death that isn't yours, delivered
deliberately (his existing calming lever, now closing a mode). Mechanics:
`GameConditionDef` applying the toughness Hediff map-wide, scheduling
aggression on a fixed cadence, disabling the stealth JobGivers from ①. Scar:
one battle becomes a named permanent Narrator callback.

### ⑧-A Sh'kaar — "The Cold Vigil" (angry-lock, evil-inverted)
Look: an unnatural hush — even wind and machinery read quieter. Rules:
pain/shock tolerance drops colony-wide (gone soft from disuse); any conflict,
even minor, triggers an outsized panic/rout; fragile high-risk work (surgery,
birth, delicate construction) succeeds at a bonus. Opportunity: the safest
window in the design — correct time for every risky project sitting on the
shelf. Cost/Yearning: complacency and defensive atrophy build the whole time;
he always wakes eventually, worse for how soft the clan went. Exit: duration
cap only — the one mode designed to be waited out, since ending it early
defeats its point. Mechanics: `GameConditionDef` applying a pain-tolerance
debuff plus surgery/birth success bonus; no forced AI. Scar: the fragile
project completed during the vigil keeps a permanent small quality bonus.

### ⑨-P Ozzik — "The Grand Court" (pleased-lock)
Look: polished surfaces, banners and trophies catching every light. Rules:
pawns gain a recurring display/brag compulsion, generating rank friction;
crafters auto-reroll toward legendary attempts over practical orders; envoys
arrive constantly requesting audiences. Opportunity: a genuine growth spurt —
guaranteed inspiration/quality windfalls and alliance opportunities on
demand. Cost/Yearning: the pride is visibly watched the whole time (his
exposure bias made continuous); internal rank squabbles rise. Exit: a public
triumph broadcast and answered — his existing "Glory" resolution, sustained
until claimed. Mechanics: `GameConditionDef` biasing quality rolls upward,
scheduling envoy incidents at increased frequency; reads the existing
Ozzik−Ishko exposure arithmetic (F13), no second exposure track. Scar: one
masterwork permanently displayed and named in colony flavor text.

### ⑨-A Ozzik — "The Shamed Court" (angry-lock)
Look: the colony reads muted, polished things covered rather than shown.
Rules: work speed/mood carry a shame-malus tied to displaying anything above
a set quality; diplomatic doors close entirely; research/great-work
production stalls under the pall. Opportunity: the correct window for the
Unburdening (F13) — performed here it costs less and vents more, the mode
itself signalling "give it away now." Cost/Yearning: stalled production and
morale drag, compounding if ignored. Exit: the Unburdening performed, or a
Rakatan-era work restored in his name (his existing grief-valve). Mechanics:
`GameConditionDef` applying the shame mood debuff, flooring diplomatic-event
frequency at zero; reads the existing Unburdening rite. Scar: the item/work
given away or restored is permanently recorded — future Narrator text can
cite it by name.

## Build ladder

**v1 slice** — four modes end-to-end as the proof: ④-P "The Open Market" (the
owner's spark, highest legibility, cheapest — trader frequency + wealth-
triggers-raids already exists via F12/F18), ⑥-A "The Long Walk" (the other
verbatim spark, one new forced-job pattern, no new subsystem), and ①-P/①-A as
a matched pleased/angry pair proving stacking and Strain on one god before
scaling. Ships `ReignModeGameComponent`, Strain, the F14 hookup, and the F17
announcement layer — the plumbing the other fourteen modes reuse untouched.

**v2** — the remaining fourteen modes, the four authored feud-bleed lines
(§3), and the Reign-Scars ledger surfaced as a readable in-game "chronicle"
object — a physical log the crew keeps, on-theme with the ship-as-conduit.

**Dream** — a mode that fires once per campaign, hand-authored rather than
meter-triggered: **the Tenfold Reign**, every god crossing into extremity at
once during the true endgame (F19's balance-keeper ending made literal) — not
a mechanic, a single scripted finale reading the whole Reign-Scars ledger
back to the player before the last choice.
