# Saved notes — telemetry/analytics, tabletop review criteria, colony-sim design

Compiled 2026-09-11.

## Game analytics — the standard reference book

Seif El-Nasr, M., Drachen, A., & Canossa, A. (eds.) (2013; Springer softcover
printing sometimes cited as 2016). *Game Analytics: Maximizing the Value of Player
Data.* Springer London. Confirmed as a real, existing, heavily-cited edited volume
via two independent OpenAlex lookups (once as a Wikipedia citation, once directly).
**Not read this session** — only its existence/editors/publisher confirmed. This is
the standard reference for telemetry metric families (DAU/MAU, retention, funnels,
heatmaps) that the brief asked about by name; a follow-up session should actually
read chapters rather than cite it by reputation alone.

Related paper actually indexed with an abstract-level citation: Bauckhage, C.,
Drachen, A., & Sifa, R. (2014). "Clustering game behavior data." IEEE Transactions
on Computational Intelligence and AI in Games, 7(3), 266–278. (Existence/venue
confirmed via Wikipedia's citation list; not read.)

**Why telemetry mostly does NOT transfer to RimMaster:** the whole metric family
(DAU/MAU, retention curves, funnels, A/B-tested drop-off) presumes a live population
of many concurrent players and an instrumentation pipeline. RimMaster ships as ONE
frozen savegame to (per repo CLAUDE.md) the owner and however many people he shares
it with — there is no multi-player telemetry pipeline and the brief says so
explicitly. The transferable pieces are conceptual, not infrastructural: a
**death map** (where do playtesters actually die/fail in a dungeon) and a **funnel**
(what fraction of testers reach each ring/room) are collectible by hand from a
handful of owner/bench playtests without any telemetry SDK — just logging tile
coordinates and outcomes per playtest run. This is a DOWNGRADE of a telemetry
concept to manual data collection, not the real thing; say so if it's proposed.

## Tabletop adventure review criteria — tenfootpole.org / Bryce Lynch

Source: WebFetch of tenfootpole.org's front page/about content (read this session;
the site is real and live, so this is CONFIRMED-VIA-DIRECT-READ of the site itself,
though I did not enumerate every review to extract a fully itemized rubric — Lynch's
criteria are expressed through review prose, not a single posted checklist).

**Extracted criteria, in his own recurring vocabulary:**
- **"Specificity" over "detail."** Detail = unnecessary trivia explaining WHY or HOW
  something is the way it is. Specificity = a terse, memorable, concrete element
  that inspires actual play. Verbatim: "If a picture is worth a thousand words then
  one well written specific sentence is worth more than a page of details."
- Values: interactivity/player agency inside an encounter; classic dungon design
  using the environment itself as an obstacle; relatable, imaginatively-conceived
  situations; terse room text that does NOT spoon-feed the solution; a coherent
  theme that ties elements together.
- Penalizes: padding and unnecessary backstory; long read-aloud boxed text in
  italics (loses the table's attention); inconsistent or unclear mechanics; generic
  NPCs without a memorable specific hook; incoherent modular/geomorph products that
  don't cohere into one place.
- **Rating vocabulary** (informal tiers, not a numeric scale): "No Regerts," "Meh.
  It's fine," "Do Not Buy Ever." This is closer to a gut-check triage than a scored
  rubric — useful as a STYLE of verdict-writing (a short, quotable, decisive verdict
  line) more than as a set of weighted dimensions.
- **Translation to RimMaster's dungeon rubric:** "specificity vs. detail" maps
  directly onto set-piece/lore-text review (the V6 casket-hall text in
  `dungeons_arc_spec.md` §3.10 is exactly this register); "does the environment
  itself constitute the obstacle" maps onto whether a ring's guardian/terrain
  combination reads as a real tactical problem vs. a generic pawn-density wall.

## RimWorld's own design — Tynan Sylvester

Sylvester, T. (2013). *Designing Games: A Guide to Engineering Experiences.*
O'Reilly Media. ISBN 978-1-4493-3802-2. Existence/publisher/year/ISBN CONFIRMED
via Wikipedia's "Tynan Sylvester" article (tertiary source, not the book itself —
the book's actual content/claims were NOT read this session and should not be cited
beyond bibliographic facts without a follow-up read).

Per the Wikipedia "RimWorld" article (tertiary source, read this session):
- Three built-in storytellers with named, different pacing philosophies: **Cassandra
  Classic** (traditional rising/falling tension arc), **Phoebe Chillax** (more
  downtime between events), **Randy Random** (prioritizes randomness over narrative
  coherence over pacing).
- The storyteller "will analyze the player's current situation and choose events
  based on what it assesses will make the most interesting narrative" — i.e., the
  storyteller is explicitly framed as optimizing for NARRATIVE INTEREST, not for a
  fixed difficulty curve.
- Sylvester designed RimWorld as a "story generator" rather than a skill-based
  challenge, per Wikipedia's framing of an early prototype where playtesters stayed
  up until 2 AM despite falling asleep because "they still wanted to play" —
  i.e. the original validation signal for the whole design was voluntary attention
  persistence past the point of fatigue, not a score or completion metric.
- **Relevance to dungeon evaluation:** this is a strong steer AWAY from judging a
  RimMaster dungeon purely by combat-difficulty tuning, and TOWARD judging it by
  whether it keeps generating narrative interest (the wake/loot/leave branch
  structure in a vault, or the thaw-gate one-way state change in the Assailant
  complex, are exactly this kind of narrative-pacing device, not a combat curve).

## Darkest Dungeon — Stress/attrition math (exact numbers, game data not academic)

Source: darkestdungeon.wiki.gg "Stress" page, read via WebFetch this session.
Real, exact, currently-live numbers (game data, not a validated research
instrument — cite as "shipped game balance data," a design precedent, not a
psychometric finding):
- Stress bar: 0–200.
- At 100 stress: hero rolls for an Affliction (bad) or, with a small chance, a
  Virtue (good) instead.
- At 200 stress: heart attack — death, or entry into "Death's Door" if already
  there. If the roll at 200 produces Virtue instead, stress resets to 0 and the
  heart attack is skipped.
- Idle recovery: 5 stress/week baseline; a specific town building (Puppet Theatre
  district) raises this to 15/week.
- Becoming virtuous resets stress down to 40–45 (not to 0).
- Various in-combat heals: 3 stress on landing a critical hit (attacker), 25%
  chance of 3 stress to each ally on a crit; 3 stress relief on a kill (50% chance
  per killing hero); virtuous-party heal of 6 stress to all allies; some virtue
  buffs heal 15 stress or drip 3 stress/turn to others.
- **Explicit design guardrail:** stress-damage-reduction sources are capped so they
  "cannot exceed reducing this by 80%" — i.e. the designers deliberately preserved
  a floor of unavoidable attrition even for a fully-optimized party.
- **Relevance to RimMaster:** this is the sharpest available real-number example of
  an "attrition math" system that deliberately creates irreversible risk/tedium
  trade-offs (a floor that CANNOT be optimized away) — directly comparable to the
  vault ladder's WAKE/LOOT/LEAVE one-way choices and the Assailant thaw-gate's
  one-way state flip in `dungeons_arc_spec.md`.

## Not obtained this session (explicitly flagged gaps)

- XCOM difficulty tuning: no primary or secondary source fetched this session — do
  not treat anything said about XCOM in this research as sourced.
- Dwarf Fortress balance discussion: same — not fetched, not sourced.
- Valve's and Riot's own published playtest methodology: the Fetcher SEARCH engine
  was degraded for the entire session (see below) and no working alternative path
  (arXiv/OpenAlex have no coverage of internal-studio blog posts/GDC talks) was
  found in the time available. **This is a real gap, not a "nothing exists"
  finding** — Valve and Riot have both published playtest-practice material
  (GDC talks, engineering blogs) that a working web search would very likely
  surface; it should be chased in a follow-up pass with a healthy Fetcher queue.
- Jesse Schell's "interest curve" (Art of Game Design) and Raph Koster's specific
  claims (A Theory of Fun for Game Design): both books' existence is extremely
  well-established general knowledge, but NEITHER was independently verified from
  a fetched primary or secondary source this session (several attempts 403'd or
  hit maintenance pages). Treat any "interest curve" or "fun = pattern recognition,
  stops when the pattern is fully learned" claim as UNSOURCED FOLKLORE until a real
  copy is read.

## Note on tooling degradation this session

Fetcher's own SEARCH directive (bing, "after brave(error)") was returning
essentially random/unrelated results for the entire research window — queries were
apparently being truncated to their first token and matched against ad inventory
(e.g. "MCTS agent playtesting balance level generation" returned office-furniture
retailers). All useful search-style discovery in this file and in METRICS.md came
from **WebFetch against arXiv's export API, OpenAlex's bibliographic API, and
Wikipedia** — not from Fetcher SEARCH. Whoever runs a follow-up pass should verify
whether Fetcher's search backend has recovered before relying on it.
