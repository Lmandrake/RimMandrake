<!-- status: draft — BENCH full design for owner ruling, 2026-08-31. Item: GRAFFITI_MOD_EXPANSION_1 (assessment shipped 2026-08-30; this is the expansion it scoped). Ground truth: items/GRAFFITI_MOD_EXPANSION_1.md. Naming: post-rename tier grammar throughout. -->
# Graffiti — the clan that writes on the world

_A scavenger people with no land, no borders, and no monuments owns exactly
one kind of permanence: **the mark**. Jawas love graffiti because graffiti is
the only architecture that travels — you cannot carry a temple, but you can
paint its door anywhere you land. This spec makes marks a first-class system:
devotion, art, joke, weapon, and language, on every wall the clan touches._

## 0. What we're building on (assessment facts, MEASURED)

`Mlie.GraffitiMod` ships ONE hardcoded ThingDef (`GraffitiMod_Paint`, Beauty
−15, six random collage textures), a joy/mental-break spray loop closed
around a C# string constant (no XML redirect), and a +2 painter-only mood.
Its own About.xml wishes for beautiful wall art "not part of this mod, right
now." **The proof-of-pattern already ships**: `RimMandrake_SacredMark_Ishko`
(640×640, real alpha, Beauty +6, validated 0/0) demonstrates new
`ParentName="BaseGraffiti"` defs work cross-mod. Everything beyond static
defs — choosing marks by context, viewer reactions, faction anger — is our
C#.

**Ruling the assessment asked for, adopted here: SACRED and BEAUTIFUL are
orthogonal.** Zizzik's, Sh'kaar's, and Ozzik's marks are devotional AND
unsettling (negative Beauty, sacred meaning) — reverence is carried by
mechanics and description, never by the Beauty sign.

## 1. The five families

### ① SACRED — the nine marks (devotion you can see)

A mark placed IS a folk devotion (the F1 gesture layer made visible and
permanent). Painting one is a small job any Jawa can do; each is F9-signed
(the god's livery colors the letter when a mark "takes"), each moves a
satiation **drip** (S-tier, §19.5-legal — mood/standing only), each carries
one small mechanical whisper. Iconography is each god's canon Form line,
verbatim — never invented.

| Mark | God · placement | The whisper it carries |
|---|---|---|
| **The Threshold Eyes** | Ishko · beside any exterior door | two orange eyes at the lintel; pawns passing get a moment of the folk doorframe-touch for free (tiny mood tick); a raid breaching a marked door is a slightly larger Ishko grievance — *they broke his gaze* |
| **The Knuckle-Trace** | Ohm · on a machine's housing | a circuit-line spiral; the machine's first breakdown roll each season shifts a hair in its favor — the current knows a friendly hand |
| **The Drop That Stays** | Oomo · on cisterns, kitchens, med beds | a single painted droplet that never falls; +1 comfort-adjacent mood to patients/diners in the room, Oomo drip on tending done under it |
| **The Tally-Blessing** | Mob'Unloo · over trade/storage doors | rows of tallies with two eyes above; a caravan deal struck in a tally-marked room books a faint Mob'Unloo drip — the ledger witnessed |
| **The Righted Hand** | Rekko · on a REPAIRED building | a scarred hand, palm open; painting it is the mourning-made-thanks after a restoration; the building's deterioration slows a whisper |
| **The Receding Line** | Ta'Baa · at the ship ramp, map exits | a dune-line always pointing away; pawns forming caravans path past it a touch faster (send-off blessing); erodes his rooted-clock drip-slow while fresh |
| **The Ward Askew** | Zizzik · near the decoy heap, on hazard rooms | a spark-glyph painted DELIBERATELY crooked (a straight ward would insult him); pairs with the decoy — a warded decoy room passes its breakdown luck a shade further |
| **The Shade Line** | Sh'kaar · painted across light boundaries | formalizes the folk pause: a literal painted line where shade meets glare; pawns hesitate AT THE MARK (the animation gets an anchor), and the line is the one Sh'kaar mark that PLEASES by existing — his border acknowledged |
| **The Buried Crown** | Ozzik · in workshops and great rooms | a half-buried crown; every masterwork finished in the room gets the maker's-flaw convention narrated; grief-valve drip when the clan is living small |

Defacing or scrubbing a sacred mark is an offense to its god (cleaning jobs
skip them by default; a hostile pawn trashing one is a grievance event).

### ② BEAUTIFUL — murals (the wish the base mod never built)

Wall art with **positive Beauty, quality-tiered like sculpture** (Awful→
Legendary), painted by Artistic pawns via a designator + work bill. The
subject is drawn **from the colony's own tale pool** (the same system
sculpture descriptions pull): the mural of the raid survived, the launch,
the birth, the tamed beast. Quality scales Beauty and the viewer thought.
- **The Long Wall** (the crown piece): a multi-panel mural that GROWS — each
  major colony event unlocks the next panel bill; the corridor becomes the
  clan's chronicle. One wall that new recruits walk to understand who these
  people are.
- Ozzik rows: finishing a mural is an art ambition-act (§8b already prices
  it); the maker's deliberate flaw (folk gesture ⑨) is quoted in its
  inspect text.

### ③ AMUSING — jests and caricatures

Small marks with viewer mood ticks and social ripples:
- **The Rude Little Man** — the universal doodle; +1 amused thought, wears
  off per-viewer.
- **The Caricature** — OF a named colonist, drawn from a social fight or a
  funny tale; the subject reacts by trait (Kind/jokes-about-me → laughs;
  Abrasive/proud → fumes, minor grudge on the artist). Mean ones feed
  `▲Zizzik` faintly — the wrong spark in a heart, in chalk.
- **The Grease Dewback** — animal doodles near pens; handlers smile.
Amusing marks are cheap, common, and cleanable without offense — the
disposable chatter of a talkative culture.

### ③b THE SHAMING TIER — intra-colony social warfare (owner, 2026-08-31)

_The missing weapon the owner asked for: marks that enrage one colonist
against another, or massively lower a pawn's social standing._

- **The Accusation** — a mark naming a colonist's real failure, drawn from
  the tale pool (the botched surgery, the fled fight, the binge): while it
  stands, **every viewer takes a recurring −opinion of the SUBJECT** (the
  massive standing drop — mechanically a social memory with otherPawn =
  subject, refreshed by viewing, capped stacking), and the subject takes a
  humiliation mood hit **plus the Ozzik pressure: answer it or bear it.**
  Answers: destroy the mark (a social fight with the artist likely), or
  answer with a DEED (a matching tale — the redeeming surgery, the held
  line — voids the mark's power and flips it into a small pride thought).
  Ozzik's answer-humiliation law, scaled down to one wall and one Jawa.
- **The Feud Mark** — painted to set A against B: mocks A in B's known
  style/signature; A's grudge lands on B unless A passes a social check to
  read the true hand. Scheming-tier, `▲Zizzik` (large — lovers and rivals
  set against each other is his feast), `↓Mob'Unloo` (a forged signature is
  a forged ledger).
- **Painting either is a hostile social act**: artist↔subject relations
  drop hard; Kind pawns refuse the work order; the colony reads who painted
  what (marks carry authorship, like art).
- **Autonomy**: grudge-holding pawns can paint Accusations during a new
  social-break variant (the shaming spree) — discord becomes visible on
  the walls before it becomes a fistfight. Zizzik approves. Frequency
  strictly rarer than insult sprees; a colony at peace paints none.

### ④ SOCIALLY INFURIATING — taunts (the aggro lever)

Marks meant to be read by ENEMIES. This is a weapon with a price tag, and
the price is theology:
- **The Challenge Glyph** — painted large on exterior walls facing the map
  edge: the next raid arriving reads it; raid anger flavor + a Visibility
  bump + `↓Ishko` (his matrix DEEDS− "challenge broadcasts" row, now a
  placeable) + `▲Sh'kaar` small. Why do it? Pride (Ozzik drip), and:
- **Come And Take It** — the taunt placed over the kill-zone mouth. The
  lure-layer made paint: raiders bias toward breaching AT the taunt — a
  deliberate funnel into the prepared dark. Taunt + traps = the Jawa way of
  inviting you to dinner.
- **The Faction Insult** — mocks a SPECIFIC faction (their icon, defaced);
  visitors of that faction who see it: goodwill hit, and their next raid
  arrives angrier. Mob'Unloo disapproves (souring a market), Sh'kaar
  approves. A lever you pull on purpose, priced on the ledger.

### ⑤ CANT — the scavenger written language (enemy-invisible wayfinding)

The family the culture begs for: **marks that DO things and only the clan
can read** — rendered for the player and Jawa, invisible or meaningless to
raiders (trap-sense §2 is the in-fiction reader):
- **The Cache Cross** — marks a hidden stockpile; Jawa hauling treats it as
  home-adjacent; raiders path past it blind.
- **Water-Below** — marks wells/moisture lines; a survival hint that renders
  on the player's map like a permanent note.
- **The Teeth Glyph** — the trap-warning: painted at pit edges and trap
  lanes; formalizes "Jawa never trip their own craft" (§6 anti-frustration:
  the immunity has a diegetic anchor) while enemies read nothing.
- **The Way Home** — route arrows at map exits toward the ship; fleeing
  pawns pathing via marked exits move a touch faster (the practiced
  evacuation, Ta'Baa's blessing on the painted line).
Cant is the family that makes graffiti a SYSTEM instead of decoration: the
clan annotates the world the way the player annotates a map, and the two
become the same gesture.

## 2. The framework build (our C#)

- **`RM_GraffitiDef`** (new def class): category (Sacred/Mural/Jest/Taunt/
  Cant) · quality support · maker + subject records · viewer-reaction spec ·
  faction-reaction spec · visibility class (public / clan-only for Cant).
- **Placement**: (a) designator + work bill (murals, taunts, cant); (b) the
  quick-paint job (sacred marks, jests — any Jawa, minutes); (c)
  **RitualOutcomeEffect** — a rite can LEAVE a mark (the Council's boon
  language made physical; the assessment flagged this fit); (d) one small
  **Harmony patch on the base mod's JobDriver** so its spontaneous spray
  spree picks from our jest/vandal pool when we're present.
- **Viewer comp**: a ThoughtWorker keyed on room entry/line-of-sight doing
  per-category reactions (mural admiration by quality, jest laughs,
  caricature trait-forks, taunt effects on hostiles/visitors).
- **Supersede vs companion — RECOMMEND COMPANION.** Keep `Mlie.GraffitiMod`
  as the living vandal tier (its break-spree IS the untrained scrawl, working
  today); we depend on its `BaseGraffiti` plumbing (filth placement,
  wall-linking, cleaning) and add everything above. One patch, zero
  absorbed C#. Supersede only if the pack-retirement wave later demands it —
  the framework is written so the dependency is one abstract def deep.

## 3. Art plan

640×640, real alpha, filth-anchored (the shipped Ishko mark is the
calibration reference); `generating-rimworld-sprites` pipeline with
chroma-key. **V1 count: ~34** — 8 remaining sacred marks (Forms are canon,
verbatim) · 6 mural bases × subject-agnostic frames (tale text carries the
specificity) · 4 jests · 3 taunts · 5 cant glyphs (glyphs are cheap:
high-contrast, iconic, one color + weathering) · 8 spare/variants. Cant
glyphs double as UI icons. The nine sacred marks reuse their livery palette
rows — the marks ARE the livery, painted.

## 4. Theology rows (for §8b on ruling)

- Paint a sacred mark → that god S-drip (a devotion; capped per-room).
- A sacred mark defaced/scrubbed by intent → `↓` that god (small); by an
  enemy → grievance event, F9-signed.
- Challenge/faction taunt painted → `↓Ishko` · `▲Sh'kaar` small ·
  Visibility + · `↑Ozzik` faint (pride) · Mob'Unloo `↓` on faction insults
  (a market soured).
- Cruel caricature → `▲Zizzik` faint; kind jest → small colony mood, no god.
- Mural completed → `↑Ozzik` per §8b art row (already priced); Legendary
  mural → Council-worthy deed.
- Cant glyph network (≥N glyphs active) → `↑Ishko` standing whisper — the
  clan speaks in a language the world cannot read.

## 5. Tiers & identifiers (post-rename grammar ONLY)

| Piece | Tier | Working id |
|---|---|---|
| Framework (def class, jobs, viewer comp, mural/jest/taunt/cant concepts) | RimMandrake | `mandrake.rm.graffiti` |
| The nine sacred marks + Jawa cant glyph set + taunt theology | RimUtinni | `mandrake.rut.marks` |
| Aurebesh-lettered taunt/jest art variants (if wanted) | RimStarWars | rides `mandrake.rsw.*` art pass, note only |

Migration note: the existing `SacredGraffiti` mod folder (old id
`mandrake.sacredgraffiti`, the shipped Ishko mark) folds into
`mandrake.rut.marks` during NAMING_SCHEME_EXECUTION_1 — it is already in the
rename map.

## 6. V1 slice vs the dream

**V1**: the nine sacred marks (defs + art) · 3 mural tiers with quality +
tale subjects · 4 jests + the caricature trait-fork · the Challenge Glyph +
Faction Insult taunts · 5 cant glyphs with their conveniences · designator +
quick-paint jobs · viewer ThoughtWorker · the one Harmony spree patch.
**Dream (v2+)**: The Long Wall chronicle · rite-left marks via
RitualOutcomeEffect wired to the Council · taunt-driven raid flavoring
(breach-at-the-taunt funneling) · faction memory of insults across visits ·
cant glyphs as caravan route hints on the world map · enemy graffiti (raiders
tag YOUR walls on the way out — and scrubbing THEIRS is a devotion).

## 7. Owner rulings requested

✅ ALL FOUR RULED (owner cards, 2026-08-31):
1. Orthogonality CONFIRMED — sacred ≠ beautiful; the fall-triad's marks are
   allowed to be disturbing.
2. **SUPERSEDE NOW — overriding this spec's companion recommendation.** We
   absorb the vandal-spree mechanic into our own framework C# and RETIRE
   Mlie.GraffitiMod from the mod list at build time. Build implications:
   our JobDriver/JoyGiver own the spree (no Harmony redirect needed after
   all), the base mod's six vandal textures are replaced or re-licensed
   (VERIFY the mod's license before any asset reuse — flag in the build
   item), and the whole family ships as one mod: `mandrake.rm.graffiti`
   plus the `mandrake.rut.marks` content pack.
3. Taunt funneling is V1 — breach-at-the-taunt ships with the family; the
   raid-AI breach-bias hook is built once and shared with the engine's
   Ishko-delivers work.
4. Cant renders as a FAINT SCRAWL to outsiders — they see that marks exist,
   never what they mean.
