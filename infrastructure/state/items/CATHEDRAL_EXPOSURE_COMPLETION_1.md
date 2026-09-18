
<!-- Split from the 2026-09-12 build decomposition; standing constraints: arc spec section 'The law' (knowledge gate, bans 1/2/3/6, rationed patience, Oracle laws, no Force, no worldgen) bind this item. -->


## spec
Arc §6.1 as amended by A3+A6 (owner verbatim in §6.1: the Cathedral fights
and slowly falls, the planet becomes a warzone again, the Hutts can get the
players offworld "for the right price... Something ancient and wondrous is
gone forever, and the ship mourns."). Builds the completion, not just the
pressure (pressure + dark flip are item 1's):
- **Exposure-completes event chain** — GM-driven: threshold on item 1's
  pressure fires full Imperial discovery; the slow fall is *witnessed, not
  narrated* — staged events on/around Cathedral ground (§GM "losing battle"
  register), bans 2/3/6 holding throughout: no Sentinel-raid story against
  the player, no mercy/drill text even in death.
- **Warzone posture flip** — RULED (owner card, 2026-09-13, via
  CATHEDRAL_ARC_OPEN_CARDS_1: "And the mechanoids go all out hostile, plus all
  of the above"). The flip uses ALL of: (a) GM layer + existing pursuit/raid
  pacing surfaces, (b) faction-hostility flips — named factions re-align at the
  flip, scoped and reversible, (c) a harsher storyteller/difficulty swap, and
  (d) mechanoid factions go all-out hostile. Still no worldgen, no map
  regeneration. Edge the builder must hold: the arc law binds faction-13
  conduct throughout (bans 2/3/6, §8 seed 4 hysteresis — no authored
  Sentinel-raid story against the player), so the all-out-hostile arm is the
  mechanoid factions at large; if faction-13's own posture at the fall cannot
  be reconciled with seed 4, that single edge escalates back to the owner
  rather than being improvised.
- **Priced Hutt extraction window** — a real, losable campaign ENDING: offer
  rides Hutt Interest (kyber §4's fixer lane); price scales with Interest/
  standing; registration as a ruled campaign ending belongs to
  `CAMPAIGN_STORY_SITTING_1` — this item builds the mechanism and hands the
  ending shape to that pass.
- **Gravship mourning register** — the ship feels the loss, kin to A1's
  receiver lore (item 7's propagation): text register on ship-adjacent
  surfaces, §P discipline, Oracle-optional.
- Knowledge gate: opens for nobody but the player even in full discovery —
  the Empire finds a thing, never the truth the player was told.

## verify
Shadow-mode first: chain fires only past the ruled pressure threshold;
demotion/dark precedes it (no skip from VOUCHED straight to fall); every
authored consequence stays inside the faction-13 hysteresis (arc §8 seed 4 —
no raid/manhunt authored anywhere in the chain); all fall/mourning text
passes item 3's linter; extraction offer priced and refusable; ending
reachable with the Oracle absent; post-fall world state carries no §GM truth
in any player-visible string.

## criteria
Full chain runs on a quicktest campaign in accelerated shadow mode; ending
handoff filed to CAMPAIGN_STORY_SITTING_1; mourning register shipped.

**Depends on:** item 1 (pressure + dark), item 3 (linter), kyber Hutt
Interest lane (M4), item 7 soft (reveal-state interaction: a revealed-then-
exposed Cathedral must still fall correctly; buildable before 7 with the
flag stubbed), `CAMPAIGN_STORY_SITTING_1` for ending ratification (mechanism
builds now, ending ships gated on that sitting). **Waited on by:** nothing.
**Seat/needs:** FOUNDRY; GM Python + event authoring + bridge; game-up for
the witnessed-fall staging. Posture-flip/ending plumbing may need C# — if so,
row-3, model per `infrastructure/agents/Agent_Policy.md` ladder.

## built (FOUNDRY, offline subagent, belt mode, 2026-09-17)

**Scope this pass: offline only** — bridge held by BENCH, so no live/
game-up work. **Dependency state actually checked before building** (not
assumed): item 1 (`CATHEDRAL_REGARD_BLACKBOARD_1`) is real, live-proven code
in `src/RimMandrake/Utils/gm_blackboard_shadow.py` (left `doing`, but its
`exposure_pressure`/`go_dark_flip_count`/`hutt_interest`/`knowledge_revealed`
numbers are genuinely live and shadow-tested) — buildable against. Item 3
(`CATHEDRAL_STAGE_COMMENTARY_POOLS_1`, the bans-2/6 linter) does **not**
exist — verified freshly tonight (grep clean for any `RUT_HumCommentary`
RulePack or committed linter script), and it is the exact reason three
sibling items (4/5/6/7) got BLOCKED by a peer FOUNDRY pass earlier tonight
(19:37–19:42, same ledger). Unlike those, this item's own text (fall-stage
letters, mourning register) doesn't route through `RUT_HumCommentary` at
all, so it was buildable by hand-checking every string against the sheet's
§6 ban wording directly (same discipline the kit's own droid-commentary
pass used before item 3 existed) — **not a substitute for item 3's linter**,
and every string here needs a re-run through it once it ships, same as
every other blocked arc item.

**Extended `src/RimMandrake/Utils/gm_blackboard_shadow.py` in place**
(additive, clearly bounded, same file/process/poll as items M4 and 1 — not
a sibling script, same reasoning item 1 gave for not forking one):
- **Full-discovery threshold above go-dark**, gated so it can only fire
  after ≥1 go-dark flip this run — structural, not a flag: go-dark resets
  `exposure_pressure` to 0.0 the same poll it fires, so full discovery
  always needs a *later* poll's re-accumulation past the higher threshold.
  This is what makes the item's own verify line true by construction:
  "chain fires only past the ruled pressure threshold; demotion/dark
  precedes it (no skip from VOUCHED straight to fall)."
- **`CATHEDRAL_FALL_STAGES`** — a 4-stage "losing battle" register (first
  tremors → roads empty → hum silent → the fall), one stage witnessed per
  poll once full discovery starts ("witnessed, not narrated," per spec).
  Every line hand-checked: no §GM truth (ban 1 — none asserts the Cathedral
  is alive or explains what it is), no mercy explanation (ban 2 — not
  mentioned anywhere), no Sentinel-raid-against-the-player story (ban 3 —
  every line is ambient/observed, nothing attacks the player), no deep-drill
  explanation (ban 6 — not mentioned).
- **`compute_warzone_posture()`** — the Card-1-ruled four-part flip
  (pursuit pacing reusing the kyber §3 surface; named faction-hostility
  re-alignment, scoped + reversible; a storyteller/difficulty-swap
  placeholder; mechanoid-factions-at-large all-out-hostile). **The named
  edge, resolved rather than escalated**: faction-13's own posture toward
  the Empire flips all-out-hostile (satisfying Card 1), but its posture
  toward the *player* stays exactly the ruled vanilla −75/0 hysteresis,
  perimeter-defense-only, forever — because bans 2/3/6 already forbid any
  authored Sentinel-raid/pursuit story against the player, at any posture,
  in any register. Reconciled by **scope** (Empire-facing vs. player-facing
  are different axes), not by softening either ruling. This is this pass's
  own resolution, not literally specced — flagged here for a sanity check,
  not blocked on, since nothing in it contradicts a named ban or the seed-4
  hysteresis.
- **`compute_hutt_extraction_offer()`** — priced, refusable, gated on
  `hutt_interest` crossing the kyber §4 fixer-beat threshold; price falls as
  Interest/goodwill rise (kyber §4: "Interest is not friendship… it moves
  access: better prices"), floored so it is never free. Returns a mechanism
  dict only; explicitly stamps `ending_ratification_owner:
  CAMPAIGN_STORY_SITTING_1` rather than registering itself as a ratified
  ending.
- **`CATHEDRAL_MOURNING_REGISTER`** — 3 ship-adjacent lines (comms static,
  gravdrive off-tone, "something in the static" gone), kin to A1's dead-
  Rakatan-band receiver lore, §P discipline throughout: describes ship
  behaviour only, never confirms anything was alive or explains what it
  means. Fires once, the same poll the fall chain completes, alongside the
  warzone flip and the Hutt offer.
- New CLI flag `--exposure-full-discovery-threshold` (same pattern as the
  existing `--exposure-godark-threshold`) for cheap demo runs.

**Offline-tested, not committed** (scratch harness, no bridge/game touch):
pure-function checks on `compute_warzone_posture`/`compute_hutt_extraction_offer`,
plus a standalone replica of the poll-body sequencing arithmetic proving (a)
full discovery cannot fire before a go-dark flip even when exposure alone
would cross its threshold, (b) fall stages advance exactly one per poll, (c)
completion (warzone + extraction + mourning) fires exactly once and does not
re-fire or over-advance on later polls. All assertions passed. **Not
live-verified** — this pass touched no bridge and no game, per scope; a real
shadow-mode run (lowering both thresholds via the new/existing CLI flags)
is owed before this can move past `doing`.

**Explicitly still owed** (not done here, per scope or per real
dependency):
- Live shadow-mode run against a real bridge session (needs the bridge,
  currently held by BENCH).
- Re-run every string above through item 3's linter once it exists (item 3
  is BLOCKED on `RUST_CATHEDRAL_MECHANICS_1`'s `RUT_HumCommentary`, per a
  sibling pass tonight) — this pass's hand-check is not a substitute.
- The fall-stage letters and mourning lines are Python string constants
  only; wiring them to an actual bridge-injection lane (kyber §2's CQF/
  letter pattern) is unbuilt — this item's own criteria call for a
  quicktest-campaign run, which is game-up work out of this pass's scope.
- Item 7's reveal-state interaction (a revealed-then-exposed Cathedral must
  still fall correctly) is stubbed only insofar as `knowledge_revealed`
  already exists and is untouched by this chain — no explicit interaction
  test was run since item 7 itself is still BLOCKED/unbuilt.
- The warzone posture's faction-13 reconciliation above is this pass's own
  call, not an owner ruling — worth a one-line confirmation, not a full
  card, since it doesn't contradict any named ban.
- Registering the Hutt extraction as a ratified campaign ending —
  `CAMPAIGN_STORY_SITTING_1`'s job, not started here.
- Posture-flip numbers (`pursuit_pacing_multiplier`, `threat_scale_multiplier`)
  are GM-tuning placeholders, same disclaimer as every other constant in
  this file — not ruled numbers.

Not closing: verify criteria require a live quicktest-campaign run and
`CAMPAIGN_STORY_SITTING_1`'s ratification, neither done this pass. Left
`doing`.
