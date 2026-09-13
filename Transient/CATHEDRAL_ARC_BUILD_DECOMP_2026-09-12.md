# CATHEDRAL_PLAYER_CONCEALMENT_ARC_1 — build decomposition (2026-09-12)

Source: `design/Jawa/cathedral_concealment_arc_spec.md` (A1–A7 all RULED),
`design/Jawa/worldbuilding/biomes/kits/rust_cathedral_kit_spec.md`,
`design/Jawa/kyber_trade_plot_spec.md` §2/§3/§4/§7,
`infrastructure/state/items/CATHEDRAL_PLAYER_CONCEALMENT_ARC_1.md`.

Standing constraints on EVERY item below (arc spec §"The law"): knowledge gate
(late-game lore, player only); sheet §6 bans 1/2/3/6; rationed patience — the
vanilla −75/0 faction-13 hysteresis bounds every authored consequence, no raids,
no manhunts; text/menu Oracle authority only and every beat complete with the
Oracle absent; no Force routes; no worldgen. No new defNames beyond kit/origin
canon except those flagged NEW below (all RUT_, tier grammar).

---

## 1. CATHEDRAL_REGARD_BLACKBOARD_1 — Cathedral Regard counter + stage machine on the GM blackboard, shadow-mode first

### spec
Python, GM external blackboard alongside Imperial Heat and Hutt Interest
(kyber spec §2/§3, build_plan.md §2/M4 pattern). Builds:
- **Regard counter** — never a save stat, never a UI gauge (arc §0). Inputs per
  arc §2: manners (polls kit §1 band history via bridge), Assailant-register
  mission completions (story flags), Heat low/falling while on Cathedral ground
  (reads the Heat number it already shares a blackboard with), zero-mindstone-
  sales standing credit, §4 restore choice (mirrors origin-canon §4 pricing,
  adds nothing), misdirection-quest success (item 5). Losses: Heat brought
  near, every mindstone/kyber sale, sacrilege mirrored from faction-13 goodwill
  deltas (one act, two ledgers — the blackboard polls goodwill, no double
  machinery), anomaly sales **by volume not buyer** (A5: running sales-volume
  counter over bolt-shed curiosities + eel-catch). Never-movers: bulk salvage,
  provoked-Sentinel fights, anything unknowable.
- **Stage machine** — WARY/TOLERATED/VOUCHED/REVEALED = f(Regard, faction-13
  goodwill, story flags) per arc §1; knowledge one-way, standing two-way;
  REVEALED entered only by item 7's beat.
- **Exposure pressure** — the §6.1 number (fed by Heat-near-Cathedral, sales
  volume, pursuit events resolving on Cathedral ground); go-dark demotion to
  WARY posture at threshold. The completion chain is item 8's, this item owns
  only the number and the dark flip.
- Consequence outputs fire through the existing bridge/CQF injection lane
  (kyber §2); this item publishes stage + dark-flag for items 2–8 to consume.

### verify
Arc §8 seed 1, in shadow mode: each §2 input moves Regard in the stated
direction; bulk salvage and provoked-Sentinel kills move nothing; a crafting
consumption moves no sale counter (kyber §2 sold-vs-crafted caveat); no input
writes any save stat; demotion 2→1→0-posture works; REVEALED unreachable from
Regard alone.

### criteria
Counter, stages, exposure pressure live in shadow mode with logged would-be
consequences; thresholds/rates in one tunable table (GM tuning owns numbers);
dark flip demotes posture without erasing history.

**Depends on:** GM blackboard M4 (kyber build_plan §2) live in shadow mode;
faction-13 goodwill readable over the bridge (kit §1 ledger is vanilla — no
kit C# strictly required to start). **Waited on by:** items 2–8 (all).
**Seat/needs:** FOUNDRY; offline Python + bridge for polling tests; game-up
only for end-to-end shadow runs. Not row-3.

---

## 2. CATHEDRAL_STAGE_HUM_BRIDGE_1 — stage → hum-baseline bridge lane

### spec
Arc §3 bullet 1: stage sets the *baseline* the kit's composite band recovers
toward — WARY reads flat/dull, TOLERATED+ breathes (richer band range, faster
recovery from low bands). Mechanism: a bridge lane feeding the kit's
data-driven `RM_BiomeAttitudeDef` thresholds (kit §1) — a small setter on
`RM_MapComponent_BiomeAttitude` exposed as a JawaBench bridge tool
(rimbridge-companion pattern), NOT a second attitude system. Dark flip (item
1) drives baseline back to WARY-flat regardless of history. No new defNames;
binds to the kit's two classes exactly as coined.

### verify
Bridge test on a quicktest Cathedral map: set stage WARY → band ceiling
flattens, dull drone only; set TOLERATED → band range widens and recovery
rate rises; irritation/goodwill machinery unchanged (kit §1's own tests still
pass); hysteresis bounds untouched (arc §8 seed 4); baseline survives save/
load without writing a new save stat beyond the map component's own state.

### criteria
One documented bridge tool; baseline parameters live in `RM_BiomeAttitudeDef`
data, not code; kit selftests green.

**Depends on:** RUST_CATHEDRAL_MECHANICS_1 §1 (the component + def exist);
item 1 (stage source). **Waited on by:** items 7, 8 (their hum registers).
**Seat/needs:** FOUNDRY; C# companion build + bridge + quicktest (game-up on
minimal list). Row-3 hard (C#, companion DLL) — model per
`infrastructure/agents/Agent_Policy.md` ladder.

---

## 3. CATHEDRAL_STAGE_COMMENTARY_POOLS_1 — stage-keyed RUT_HumCommentary pools + the bans linter gate

### spec
Arc §3 bullet 2: the kit's `RUT_HumCommentary` RulePack (kit §1) gains
stage-keyed line pools (key = band × stage). Register: droids report what
they *feel*, never what it *means*; pre-reveal no line attributes agency;
post-reveal lines still never explain the mercy (ban 2) or the drill (ban 6).
Stage-transition letters in §P register only ("the ground here has been...
easier, lately"). PLUS the enforcement instrument the whole arc's verify
rides: a **linter script** (extends
`skills/rimworld-modding/scripts/validate_patch.py` family or standalone)
that greps every player-facing string in the arc's content (RulePacks,
letters, quest text from items 4/5/7/8) for (a) agency attribution before
stage 3 — flag terms naming the Cathedral as actor/quest-giver, (b) mercy
explanation, (c) drill description. Wired so items 4/5/7/8 run it in their
own verify.

### verify
Arc §8 seed 2 executed literally: linter run over all shipped strings returns
zero findings; a deliberately-poisoned fixture line IS caught (the linter is
tested, not trusted); commentary fires on band transitions per stage key on a
quicktest map; Oracle absent throughout (these are RulePack strings — no
Oracle involvement at all).

### criteria
Pools shipped for all 4 stages × bands v1; linter committed with fixture
tests; every later arc item's verify section cites the linter by path.

**Depends on:** RUST_CATHEDRAL_MECHANICS_1 §1 (`RUT_HumCommentary` exists);
item 1 (stage key source, via item 2's lane or direct flag). **Waited on
by:** items 4, 5, 7, 8 (they must pass its gate). **Seat/needs:** FOUNDRY;
offline content + linter, quicktest for transition firing. Not row-3.

---

## 4. CATHEDRAL_MISSION_BOON_OFFERS_1 — deniably-sourced missions + Heat-gated gravtech boons

### spec
Arc §3 bullet 3. TOLERATED: first mission offers against the Assailant
register arrive via droid/enclave channels — never attributed to the
Cathedral (linter-enforced). VOUCHED: gravtech boons (plot-tier per
`03_deep_history.md`) open, each priced against **current Imperial Heat** —
when the Empire is looking, it does not act; boons suspend on the dark flip.
Surface: CQF quest/letter or bridge-injected letters (kyber §7 lane,
inheriting its CQF caveat); offers keyed off item 1's stage + Heat read.
Completion feeds Regard (item 1 input). Fallback text ships first; Oracle
upgrades voice only. NEW defNames (flag): quest/letter defs
`RUT_CathedralAssailantMission_*`, boon defs as the gravtech content pass
names them — coin the minimum, RUT_ tier.

### verify
Offer appears only at correct stage; quest-giver string passes item 3's
linter (no Cathedral attribution pre-stage-3); boon availability flips with a
shadow-mode Heat change; dark flip closes both; every beat completes Oracle-
absent; K2 anti-laundering: completing missions scrubs zero Heat.

### criteria
≥1 Assailant mission shape + the boon-offer gate live end to end on a
quicktest; Regard feedback observed in shadow logs.

**Depends on:** item 1; item 3 (linter); CQF-vs-thin-config reconciliation
(build_plan §6.1 — inherited caveat, assume CQF like kyber). **Waited on
by:** item 7 (VOUCHED must be reachably earnable). **Seat/needs:** FOUNDRY;
quest authoring (rimworld-quests skill) + bridge + quicktest.

---

## 5. CATHEDRAL_SURVEY_MISDIRECTION_QUEST_1 — the A4 Imperial-survey misdirection beat

### spec
Arc §4, RULED IN. An Imperial survey/research party works Cathedral-adjacent
ground — pursuit-spine dressing, **no new faction**. Three outs: (a) nothing;
(b) feed the surveyors boring expected answers — salvage-guild banality,
text/menu dialog — success = large Regard gain, zero text saying why; (c)
point them at the anomaly = §6.1 exposure input (feeds item 1's pressure).
Anti-laundering (K2): (b) scrubs no Imperial Heat. Same CQF/bridge-letter
surface and caveat as item 4. NEW defName (flag):
`RUT_CathedralSurveyMisdirection` quest script (+ its letters), RUT_ tier.

### verify
Fires from the pursuit spine dressing without inventing a faction; (b)
success moves Regard up in shadow mode and Heat not at all; (c) moves
exposure pressure; all dialog passes item 3's linter (no line explains what
the player protected); completes Oracle-absent with prescribed fallback text.

### criteria
Quest lands, all three branches playable on a quicktest, consequences logged
on the blackboard.

**Depends on:** item 1 (Regard/exposure sinks), item 3 (linter), pursuit
spine Act I dressing available (kyber §3). **Waited on by:** nothing hard
(item 7's "sustained good conduct" does not require it). **Seat/needs:**
FOUNDRY; quest authoring + bridge + quicktest.

---

## 6. CATHEDRAL_MECHANOID_PASS_VERBS_1 — the GRANT/REVOKE relationship instrument

### spec
Arc §3 "Mechanoid pass" (RULED, owner verbatim quoted there). Two verbs:
- **GRANT** — at VOUCHED+, the Cathedral may extend the Helix-style pass to
  the clan: its machines read pass-holders as non-hostile. Priced like any
  boon against Imperial Heat (offer rides item 4's lane); revocable when the
  relationship cools (stage demotion) or goes dark. Implementation: NEW
  (flag) `RUT_CathedralPass` hediff/flag on clan pawns + a targeting/hostility
  exception for faction-13 Sentinels and Cathedral-controlled mechs toward
  pass-holders — likely one scoped Harmony patch on the hostility check;
  scope it to faction 13 + Cathedral maps, never global.
- **REVOKE (Helix)** — the Helix's own pass is the Cathedral's silent
  tolerance; the reveal (item 7's flag) is what enables stripping it — a
  legible consequence, not a new mechanism: a GM-layer relation flip keyed on
  the reveal flag. Build against the flag name; dormant until item 7 lands.
- **Never**: the pass opens nothing at the antipode war lab — command codes
  sit on the Spire's isolated system (`worldbuilding/ashfall_research_base.md`
  §6). Assert in tests, not just prose.

### verify
Quicktest with hostile faction 13: pass-holder pawns untargeted, non-holders
targeted (spawn many — one pawn is RNG, per memory); REVOKE returns targeting
within the vanilla hysteresis bounds, no manhunt/raid behavior introduced
(arc §8 seed 4); war-lab access unchanged with pass held; grant/revoke driven
purely by blackboard verbs over the bridge.

### criteria
Both verbs callable from the GM layer; Harmony scope reviewed (mark-clean
path); no behavior off Cathedral maps.

**Depends on:** item 1 (stage + verbs), item 4 (offer lane, soft), item 7
(Helix-REVOKE trigger only — GRANT ships without it). **Waited on by:**
nothing. **Seat/needs:** FOUNDRY; C# + Harmony + quicktest (game-up, minimal
list). Row-3 hard — model per `infrastructure/agents/Agent_Policy.md` ladder.

---

## 7. CATHEDRAL_DESCENT_REVEAL_SITE_1 — the A7 real under-plate descent + the reveal beat + A1 propagation

### spec
Arc §5, A7 RULED: a **real structure-injected site the player walks** in v1 —
no worldgen; structure injection on the fixed world / a descent map, built
via the bridge lanes (rimworld-world-editing / layout injection; smaller
set-piece and text-only options were DECLINED). Content: canyon-scale halls,
the mile-long production line, the second coolant circuit toward the Scald,
Sentinels walking past the party (pass behavior — reuse item 6's exception
scoped to the escort). One-time escorted descent; at the bottom the first
direct address in the whispered-voices register through droid/comms gear
(origin canon §3 channel grammar) — text/menu, prescribed fallback first,
Oracle upgrades voice only. Discloses aliveness + scale + the-audition ONLY
(A2); bans 2/6 hold; scoped to the player — no faction text, trader chatter,
or codex artifact changes; after-letters stay §P. Trigger: VOUCHED + post-
restore-choice flag (the choice itself, either answer), never Regard alone;
fires ONCE, sets the reveal flag items 6/8 read. **A1 propagation rides this
item:** the Utinni is the usher — she KNOWS because she receives the dead
Rakatan transponder band; propagate the receiver-lore into
`reconciled_lore/03_deep_history.md` and the gravship/Utinni bond material in
the same change (owner: "propagate when the arc builds"). NEW defNames
(flag): descent site/quest defs `RUT_CathedralDescent_*`, RUT_ tier; walls
and dressing reuse kit §2 defs wherever possible.

### verify
Arc §8 seed 3: fires once, only from the ruled trigger set (dev-flag matrix:
VOUCHED without flag = no fire; flag without VOUCHED = no fire); re-trigger
attempts refused; no faction-visible text changes anywhere (diff the string
surface); all reveal text passes item 3's linter (scale/aliveness yes, mercy/
drill never); completes Oracle-absent end to end; site verified actually
present per-slot (`jawa/list_things`, not the placement log's net count); A1
lore landed in the named docs with inbound references fixed.

### criteria
Descent playable start-to-bottom on a quicktest-loaded save; reveal flag
published to the blackboard; stage 3 entered by this beat and only this beat.

**Depends on:** item 1 (VOUCHED + flags), item 2 (stage-3 hum register),
item 3 (linter), item 4 (VOUCHED earnable), item 6 soft (escort pass
behavior — can stub with faction-neutral spawns if 6 lags), restore-choice
flag existing (origin canon §4 — already specced, mirror only). **Waited on
by:** item 6's Helix-REVOKE, item 8 (bans-through-the-fall use the same
string gate; gate stays player-only through it). **Seat/needs:** FOUNDRY;
bridge + game-up (structure injection, escort run); quest authoring for the
escort shell.

---

## 8. CATHEDRAL_EXPOSURE_COMPLETION_1 — the A6 pyrrhic discovery ending

### spec
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
- **Warzone posture flip** — planet-level posture change via the GM layer +
  existing pursuit/raid pacing surfaces; no worldgen, no map regeneration.
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

### verify
Shadow-mode first: chain fires only past the ruled pressure threshold;
demotion/dark precedes it (no skip from VOUCHED straight to fall); every
authored consequence stays inside the faction-13 hysteresis (arc §8 seed 4 —
no raid/manhunt authored anywhere in the chain); all fall/mourning text
passes item 3's linter; extraction offer priced and refusable; ending
reachable with the Oracle absent; post-fall world state carries no §GM truth
in any player-visible string.

### criteria
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

---

## Build order

1 (REGARD_BLACKBOARD, shadow) → 2 (STAGE_HUM_BRIDGE, once kit §1 lands) → 3
(COMMENTARY_POOLS + linter) → 4 (MISSION_BOON_OFFERS) and 6-GRANT
(MECHANOID_PASS) in parallel → 5 (SURVEY_MISDIRECTION, parallelizable with
4/6) → 7 (DESCENT_REVEAL — needs 1–4) → 6-Helix-REVOKE arm → 8
(EXPOSURE_COMPLETION — mechanism can start after 1+3, ships last).

External gates: RUST_CATHEDRAL_MECHANICS_1 §1 gates items 2/3; GM blackboard
M4 shadow mode gates item 1; CQF reconciliation (build_plan §6.1) shapes
items 4/5; CAMPAIGN_STORY_SITTING_1 ratifies item 8's ending.

## Flags

- **Warzone posture flip has no owning mechanism spec.** "The planet becomes
  a warzone again" (A6) names an outcome; no ruled surface defines
  planet-level posture (raid pacing? faction hostility matrix? storyteller
  swap?). Item 8 assumes GM-layer + existing pursuit surfaces; if that
  proves insufficient it needs a card, not improvisation.
- **The Hutt extraction ENDING mechanism is ratified elsewhere.** A6 assigns
  the ending to CAMPAIGN_STORY_SITTING_1; item 8 builds the window but the
  campaign-ending shape (what "offworld" means mechanically for a gravship
  campaign) is not specced anywhere read for this decomposition.
- **Mechanoid-pass scope is unruled at the edge:** "non-hostile to the
  Mechanoids" — faction-13 Sentinels certainly; whether it covers vanilla/
  other mechanoid factions on Cathedral ground is item 6 build discretion;
  assumed faction-13 + Cathedral-controlled only (narrowest reading). One
  owner sentence would settle it.
- **Inherited, known:** CQF-vs-thin-config contradiction (build_plan §6.1)
  still unreconciled — items 4/5 assume CQF like the kyber spec and inherit
  the reconciliation.
- NEW defNames coined (all RUT_, minimum set, flagged in-item):
  `RUT_CathedralPass` (6), `RUT_CathedralSurveyMisdirection` (5),
  `RUT_CathedralAssailantMission_*` (4), `RUT_CathedralDescent_*` (7).
