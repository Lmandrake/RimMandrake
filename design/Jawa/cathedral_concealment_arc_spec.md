# The Cathedral and the player — concealment, thaw, and the reveal

**Item:** `CATHEDRAL_PLAYER_CONCEALMENT_ARC_1`. **Source of intent:** owner-ratified
canon, 2026-09-10, frozen into `design/Jawa/worldbuilding/biomes/the_rust_cathedral.md`
§7b (the arc's canon home — this spec adds mechanism, changes no ruling there).
**Sibling precedent:** `kyber_trade_plot_spec.md`, `tibanna_embargo_plot_spec.md` —
this spec reuses their GM-blackboard pattern and the Cathedral kit's hum machinery
wholesale, and cites rather than restates.

## 🔴 The law (frozen canon, §7b amendment, owner-ratified)

The Cathedral survives by looking **exceptionally dull and giving boring, expected
answers** — *which is why it permits salvage*: the extraction loop IS the cover. Few
grasp how massive or deep it is; it wants it that way. The Empire's modern presence
is the top threat; it dreads being pulled into a "local skirmish." **The player's
Rakatan gravship flying around agitating the Empire is exactly the danger it fears —
so it dislikes the player at first and hides from them for a long while.** The
manners of §7b are how the player earns their way out of that.

Standing gates this spec lives under:
- 🔴 **The knowledge gate (hard)** — `RUT_mechanoid_origin_canon.md` §5: nobody
  in-world knows the Cathedral is alive or wants the crystals; **late-game lore
  only.** Every beat before the reveal (§5) must read, in-world, as a place with
  strange weather — never as a person.
- 🔴 Cathedral sheet §6 bans, verbatim and forever: no §GM truth in player-facing
  text (ban 1), no explanation of the droids' mercy (ban 2), **no hunting Sentinels /
  no Sentinel raid story (ban 3)**, no deep-drill explanation (ban 6).
- 🔴 Rationed patience, never raids — origin canon §4: hostility is the ruled
  −75/0 goodwill hysteresis, perimeter-only; the Cathedral's answer to betrayal is
  withdrawal, not vengeance.
- The two LLM laws: any Oracle-voiced beat is text/menu authority only, and the
  game is whole with the Oracle absent. No Force routes. No worldgen.

## 0. What already exists, and what this spec adds

| Existing machinery | Owner | This spec's use |
|---|---|---|
| Faction-13 goodwill + vanilla −75/0 hysteresis | Cathedral kit §1 (verified vanilla) | the slow ledger — unchanged |
| `RM_MapComponent_BiomeAttitude` (irritation, bands 0–4, hum layers, bolt display, droid commentary) | kit §1 (`RUST_CATHEDRAL_MECHANICS_1`) | the on-map voice of every stage |
| Imperial Heat, GM external blackboard, shadow-mode first | `kyber_trade_plot_spec.md` §2 (build_plan.md §2/M4) | exposure pressure input |
| Pursuit spine Act I–III | `kyber_trade_plot_spec.md` §3 | what "agitating the Empire" is |
| Mindstone-sale grudge + heat | origin canon §2, kyber spec §1 | a needle-mover here too |
| §4 restore choice + priced consequences | origin canon §4 | the vouched-stage hinge |
| The Utinni's vouching, gravtech boons, Free-Droid tension | `reconciled_lore/03_deep_history.md` §The Rust Cathedral | the arc's cast |

**One new number, nothing else:** **Cathedral Regard** — a counter on the same GM
external blackboard as Heat and Hutt Interest, same shadow-mode discipline, never a
stat in the save and never a UI gauge (Embargo-Clock precedent: register through
texture, not instruments). Stage = f(Regard, faction-13 goodwill, story flags).
No new faction, no new relationship system.

## 1. The stages

| stage | name | what it is | entered by |
|---|---|---|---|
| 0 | **WARY** (start) | It hides. The hum reads the player as weather reads anyone; boons: none; missions: none. Its dislike is invisible — indistinguishable, in-world, from the place simply being dead. | campaign start — the gravship IS the reason |
| 1 | **TOLERATED** | The Utinni's vouching has been accepted on probation. Manners are being graded. First mission offers (against the Assailant register, per `03_deep_history.md`) arrive through droid/enclave channels — never attributed to the Cathedral. | sustained good conduct on Cathedral ground + Regard floor |
| 2 | **VOUCHED** | The clan runs its missions to prove her value. Gravtech boons open — each one "a risk it takes by being seen to act," so each is priced against current Imperial Heat (§3). The §4 restore choice is offered in this stage. | missions completed + Regard threshold; accelerated or chilled by the restore choice |
| 3 | **REVEALED** | Late-game. The knowledge gate opens for the player alone (§5). | §5's beat, and only that beat |

Stage transitions are one-way ratchets on knowledge (what has been seen cannot be
unseen) but two-way on standing: Regard loss demotes conduct-stages (2→1→0-in-
posture); the reveal, once fired, never unfires — a revealed-and-betrayed Cathedral
is §6's second failure direction.

## 2. What moves the needle

**Up (Regard gains):**
- **Manners** (§7b verbatim): sustained low-irritation presence — mine the bulk,
  touch nothing sacred, stop when the hum drops. Fed by the kit's band history, not
  a new tracker.
- **Missions against the Assailant register** — the ruled proving-ground
  (`03_deep_history.md`: the clan runs missions "to prove her value").
- **Keeping the Empire away from it**: Imperial Heat *low or falling* while the
  player operates on/near Cathedral ground; no pursuit-spine events landing there.
- **Refusing the crystal trade**: a campaign with zero mindstone sales is itself a
  standing credit (the crystals are what it needs and what exposes it — origin
  canon §5 C2).
- **The §4 restore choice, restored**: the single largest gain — priced exactly as
  origin canon §4 already rules it (FDE voices quiet, enclave standing cools,
  cousins' grudge; this spec adds nothing to that ledger).
- **Protecting its cover** (§4 below): the misdirection beat, if the owner rules
  it in (CARD A4).

**Down (Regard losses):**
- **Empire heat brought near**: high Heat while parked on/adjacent to the
  Cathedral region; any Act II+ pursuit event resolving on Cathedral ground is a
  large hit — the "local skirmish" it dreads, made real by the player.
- **Mindstone/kyber sales** — every one, on top of their existing prices (kyber
  spec §3, origin canon §2): Imperial crystal attention is Cathedral exposure.
- **Sacrilege and the drill**: the existing ledger already prices these
  (faction-13 goodwill, kit §1/§5); they mirror into Regard at the same moments —
  one act, two ledgers, no double machinery (the GM blackboard polls goodwill
  deltas the way it polls trade sessions).
- **Selling the anomaly**: bolt-shed curiosities and eel-catch are "both salable,
  both watched" (sheet §7) — sales to ordinary buyers are the cover working;
  sales into Imperial-survey-adjacent channels are exposure (CARD A5 owns the
  line's exact position).
- **Deliberate exposure** (§6.1): telling the Empire is not a needle-move, it is
  the failure direction.

**Never a needle-mover:** ordinary bulk salvage (the cover IS the loop — heavy
deck-plate mining is what it wants to be seen permitting); fighting Sentinels the
player provoked (already priced by goodwill; the Cathedral does not double-charge
its own hysteresis); anything the player could not have known (the gate holds both
ways — no punishing clairvoyance).

## 3. How each stage surfaces in play (text/menu only; game whole without the Oracle)

- **Hum-mood tiers**: stage sets the *baseline* the kit's composite band recovers
  toward — WARY ground reads flat and dull (the hiding, audible as absence);
  TOLERATED+ ground breathes (richer band range, faster recovery from low bands).
  Mechanism: the stage feeds the kit's data-driven `RM_BiomeAttitudeDef`
  thresholds through the same bridge lane the GM layer already owns — no second
  attitude system.
- **Droid commentary**: the kit's `RUT_HumCommentary` RulePack gains stage-keyed
  line pools. Register discipline: droids report what they *feel*, never what it
  *means* (ban 2 stands; the sheet's one permitted register is their
  incomprehension). Pre-reveal, no line may attribute agency; post-reveal lines
  still never explain the mercy.
- **Missions and boons**: offered as quests/letters through enclave and Utinni
  channels — pre-reveal, always deniably sourced ("the enclaves ask...", "the
  Utinni insists..."); the Cathedral is never the named quest-giver until stage 3.
  Gravtech boons (plot-tier, per `03_deep_history.md`) unlock at VOUCHED, and
  each boon's availability is inversely gated on current Imperial Heat — when the
  Empire is looking, it does not act. Fallback text ships first; the Oracle only
  upgrades voice (both laws, verbatim).
- **The Mechanoid pass — a relationship instrument (RULED, plot sitting
  2026-09-12).** Owner verbatim: "The Helix use their pseudo-genetic makeup to
  appear as non-hostiles to the Mechanoids (but this can be overrided by the
  Cathedral if it chooses to reveal itself). The Cathedral can also grant this
  to the player jawas if it chooses." ⇒ Two verbs the arc owns: **GRANT** —
  at VOUCHED or later the Cathedral may extend the pass to the clan (its
  machines read them as non-hostile), priced like any boon against Imperial
  Heat and revocable when the relationship cools or goes dark (§6); **REVOKE**
  — the Helix's pass is the Cathedral's silent tolerance, and revealing itself
  (§5) is what lets it strip that tolerance, so a revealed Cathedral turning
  on the Helix is a legible consequence of the reveal, not a new mechanism.
  What the pass does NOT do: open the antipode war lab — its command codes sit
  on the Spire's isolated system, never ceded to the Cathedral and ungrantable
  by it (`worldbuilding/ashfall_research_base.md` §6).
- **Letters at stage transitions**: §P register only — the world describing
  behavior ("the ground here has been... easier, lately"), never intent.
- **No gauge, ever**: the player reads the relationship the way the fiction does —
  hum, bolts, droids, what gets offered. (Hum-literacy, sheet §7, is the
  in-fiction skill of reading exactly this; its design pass stays deferred per
  the kit.)

## 4. Protecting it — the player as accomplice

The passive protections (low Heat, no sales, manners) are §2. One active beat is
worth its own quest shape, **pending CARD A4**: an Imperial survey/research party
works Cathedral-adjacent ground (pursuit-spine dressing, no new faction); the
player can (a) do nothing, (b) feed the surveyors the same boring, expected
answers the Cathedral has given for centuries — salvage-guild banality, text/menu
— or (c) point them at the anomaly (§6.1's door). Success at (b) is a large
Regard gain and the loudest possible signal that the player has understood what
the place is doing — without one line of text saying so. Anti-laundering law
(kyber K2 precedent): protecting it scrubs no Imperial Heat — the Empire's
suspicion of the *player* is not the Cathedral's ledger.

## 5. The reveal — how massive, how deep

**The beat (stage 3, late-game, one time):** the Cathedral opens a way down. A
one-time escorted descent — a site/mission on the fixed world, no worldgen —
through the under-plate works: halls the size of canyons, a production line a
mile long that the player has only ever *heard* cycle, the second coolant
circuit running down toward the Scald, and Sentinels that walk past the party
the way they have always walked past droids. At the bottom, the first direct
address: the whispered-voices register (`03_deep_history.md` — the enclaves'
whispers "are real attention"), through the party's droid or comms gear, Shard-
mind style (origin canon §3's channel grammar). Text/menu; prescribed fallback
first.

**What it discloses, and what it never does (knowledge-gate compliance):**
- **In**: that it is alive; that it is vast — the plateau IS the works, the
  flatness is a built surface (§GM's scale facts, now spoken to the one
  audience the gate names); that the salvage loop was cover and the player's
  manners were an audition.
- **Still out, forever**: the droids' mercy (ban 2 — *it does not explain
  itself even now*); the deep-drill response (ban 6); and the full
  terramanufacture picture — dynamo, plasma fountain, the Assailants, the
  reserves — which stays §GM unless CARD A2 opens more. The reveal shows
  SCALE and ALIVENESS; purpose stays in the dark it prefers.
- **Scoped to the player**: the world does not learn. No faction text, trader
  chatter, or codex-visible artifact changes; the letter register afterward
  stays §P. The gate says *late-game lore*, not *public knowledge*.

**Trigger discipline**: fires only from VOUCHED standing plus a late-game flag
(post-restore-choice, either way chosen — the choice itself, not its answer, is
the maturity test), never from Regard alone; exact flag set is build tuning,
shadow-mode first like every blackboard number.

## 6. The failure directions

**6.1 Exposure — the Empire learns.** The player (or the player's Heat) drags
Imperial attention onto the anomaly. Graduated, and — RULED (A3, 2026-09-12) —
it CAN complete: full discovery is a real, losable v1 outcome:
- Rising exposure pressure = the Cathedral goes *dark*: stage demotion to WARY
  posture regardless of history, boons suspended, hum flattened to the dull
  drone it shows strangers, missions stop. The relationship does not break; it
  hides from the player again — the arc's opening state, now legible as choice.
- The canon endpoint, if it ever fires, is ruled: *"challenged, probed, and
  forced to defend itself or self destruct... a losing battle"* (§GM). That is
  a campaign-catastrophe register, not an incident — v1 builds the pressure
  and the withdrawal, not the apocalypse.

**6.2 Betrayal — the player exposes or despoils it deliberately.** Rationed
patience, never raids (origin canon §4; sheet §6 ban 3):
- The ledger does what it already does: sacrilege goodwill to −75 flips
  faction 13 hostile — perimeter hostility only, un-hostile at 0, exactly the
  ruled hysteresis. No manhunts, no pursuit, no Sentinel vengeance story.
- What betrayal *uniquely* costs is the arc: Regard floors permanently, boons
  and missions close for good (kyber's one-Rebellion-cell grammar), the
  Utinni's vouching is spent — her text register carries the loss — and
  enclave standing drops. A revealed-then-betrayed Cathedral says nothing at
  all, ever again: the silence of the organics (`03_deep_history.md`),
  extended to the player as a verdict.

## 7. Build surfaces (for the eventual implementation item)

| Piece | Surface | Owner of the number |
|---|---|---|
| Cathedral Regard counter, stage thresholds, exposure pressure | GM blackboard (Python, M4), shadow-mode first | GM tuning |
| Stage → hum baseline | bridge lane into kit §1's `RM_BiomeAttitudeDef` thresholds | kit build |
| Stage-keyed droid lines | kit §1's `RUT_HumCommentary` RulePack pools | content pass |
| Mission/boon offers, survey beat, descent site | CQF quest/event or bridge-injected letters (inherits kyber spec §7's CQF caveat) | quest authoring |
| Restore-choice mirroring | already specced, origin canon §4 | no new work |

No new defNames are coined here; every token cited (`RM_MapComponent_BiomeAttitude`,
`RM_BiomeAttitudeDef`, `RUT_HumCommentary`, `RUT_Mindstone`) is the kit's or the
origin canon's, and binds at their builds.

## 8. Verify (mirrors the item)

- Shadow-mode: each §2 input moves Regard in the stated direction; bulk salvage
  moves nothing; no input writes a save stat.
- Grep gate: no player-facing string (letters, commentary pools, quest text)
  attributes agency to the Cathedral before stage 3; post-reveal strings still
  contain no mercy explanation and no drill description (bans 2/6 linter rule).
- The reveal fires once, from the ruled trigger set, and changes no faction-
  visible text.
- Betrayal path: faction 13 behavior is bounded by the vanilla hysteresis —
  no raid, no manhunt, in any authored consequence.
- Every beat completes with the Oracle absent.

## Cards for the owner

- **A1 — RULED (owner card, 2026-09-12): she KNOWS — the gate's sole
  exception.** Verbatim: "She knows, because she can 'feel' (receive) the
  Ratakan transponder working on frequencies no longer used." ⇒ The Utinni
  RECEIVES the Rakatan transponder band nobody else listens on — that is HOW
  she knows the Cathedral is alive, and it makes her the natural reveal
  usher. New lore mechanism this creates: the Utinni is a receiver on
  dead Rakatan frequencies (bears on her bond with the player's Rakatan
  gravship; propagate when the arc builds).
- **A2 — RULED (2026-09-12): aliveness + scale only.** §5 stands as written;
  purpose (the Assailants, the decline, the reserves) is held back for a later
  sitting's content.
- **A3 — RULED (2026-09-12): exposure CAN complete — a real, losable v1
  outcome.** Full Imperial discovery is buildable and ends the relationship in
  the §GM catastrophe register ("a losing battle"). ⇒ SUPERSEDES this spec's
  own asymptotic-v1 assumption everywhere it appears (§6.1 amended in the same
  change); the discovery event and its aftermath must be authored as part of
  the arc's build.
- **A4 — RULED (2026-09-12): IN.** The survey-misdirection quest beat is built —
  the one place the player actively practices concealment.
- **A5 — RULED (2026-09-12): volume, not identity.** Occasional curiosities are
  safe with any buyer; selling IN BULK is what draws eyes, whoever buys.
  Exposure pricing keys off a running sales-volume counter, not the buyer's
  faction.

---

**Register note:** this spec is DESIGN. Nothing above is in-world knowledge; no
rumor of any of it circulates (same scoping law as the Kindled, origin canon §2b).
