<!-- status: RULED (owner, 2026-09-04, by card — all four §10 questions):
     ① VOICE is permanently FAILABLE (Testament the only guaranteed piece);
     ② the Rites↔Antiquities WELD stands and IS the Rites' revealed-not-bought
       gate (supersedes the "later ship-memory work" placeholder in
       src/RimUtinni/Rites/About/About.xml);
     ③ the Call-Out's LOST-ledger gate is HARD — the world remembers what you sold;
     ④ the Testament is AMBIVALENT — gratitude without warmth.
     Feeds RESEARCH_TREE_NORMALIZATION_1, VAULT_DUNGEON_CONCEPT_1,
     ASSAILANT_DUNGEON_BUILD_1, and the Rites/ShipMemory line.
     Execution: ANTIQUITIES_TREE_BUILD_1 (slices per §9). -->

# ANTIQUITIES — the tree you dig up one urn at a time

## 0. Concept, in three sentences

The ancients wrote nothing down — except on everything they made. Every urn,
stele and grave-good on Ash'karr is a page of an encrypted civilization, and
the campaign's deepest progression is the clan **reading the world back into
existence**: language, then religion, then culture, then maps, then a voice
that the last living ancients will actually answer. It is a research tree
where the research points are physical objects with stories on them, dug out
of ruins and vaults, coveted by the Helix, and read aloud to a ship that is
slowly realizing the encryption is *its own*.

## 1. Lore canon — the Doctrine of the Unwritten (written as truth)

The Rakata of Ash'karr were not always secretive. The war made them so.

The Assailant did not defeat armies; it defeated *records*. It was built to
read — to infest datastores, learn access codes, replay authentication,
speak in the voices of the dead. Every archive was a weapon handed to the
enemy. Within a generation the ancients burned their own libraries and
adopted the **Doctrine of the Unwritten**: nothing stored, nothing indexed,
nothing machine-readable. Knowledge would live in two places only — in minds,
and in *art*.

Because art was the one thing the Assailant provably could not parse. It
could dissolve a data-lattice in seconds and stare at a glazed urn forever.
Metaphor, allusion, deliberate error, sacred repetition, meaning carried in
the *choice* of what not to depict — the bioweapon's mad completeness had no
purchase on any of it. So the ancients encoded everything that mattered —
their liturgy, their genealogies, their door-codes, the coordinates of their
vaults — into a civilization-wide artistic canon in which **every decorated
object is a sentence** and only the cultured can read.

Then they died, or slept. And the sleepers are the wrong ancients: the **war
children**, decanted mid-crisis, raised inside single fortresses, taught only
their garrison's fragment of the canon. Wake one and it can fight, grieve,
and leave. It cannot tell you where the vaults are, because *its parents
deliberately never told it* — children were the most likely thing the
Assailant would wear as a skin. The full canon existed only distributed:
across ten thousand urns, on purpose, so that no single mind or object was
worth capturing.

**And the Utinni is party to it.** The ship is Rakata substrate (canon:
substrate kinship, the vault-draw). Her deep memory partitions were sealed
the same way everything was sealed in the war years — behind canon-art
challenge locks. She cannot simply remember; she must be *shown the art*,
piece by piece, until the challenge phrases resolve. This is the literal
mechanism of the owner's line "each urn advances a research tech in
antiquities that helps the ship unlock more of its own memories": the urns
are not teaching the ship history. **They are her password hints.**

The Helix knows none of this. They buy urns because their gene-cults
correctly suspect Rakata bioscience is written *somewhere*, and they are
methodically buying the planet's art in the hope of brute-forcing a canon
that was specifically engineered to resist exactly that approach. They are
the Assailant's error, repeated politely, with silver.

## 2. Where it sits — a 17th tree, interlocked with the Rites

**Recommendation: Antiquities is its own tree** (the 17th slide), locked —
but its gate is not a faction: it is the **world itself**. Every node is
`source_gate: antiquity` — advanced only by applying read artifacts, never by
lab-hours alone. This uses the ruled general mechanism verbatim: *"the
techprint economy IS the gate"* (canon research-access classes) — urns are
techprints that the planet holds instead of a faction.

The relationship to **The Rites** is a double helix, not a merger:

- **Antiquities is outward**: the clan learning the *ancients'* canon.
- **The Rites are inward**: the ship practicing what she is remembering.
- They interlock as **hidden prereqs**: each Rites tier past the Scrap Shrine
  carries a hidden prereq on an Antiquities stage (Conduit Choir needs
  LANGUAGE; God-Speaker Array needs RELIGION; Liturgy of the Hull needs
  CULTURE; The Gods Speak Back needs VOICE). The fiction is exact: the ship
  cannot perform a liturgy in a language the clan has not yet taught her to
  read. This also quietly solves the Rites' missing revealed-not-bought
  gate — the reveal channel is Antiquities progress.
- The already-flagged repurpose hooks slot in (functionless_tech_candidates):
  **Xenobiology** becomes Antiquities-adjacent (the study of what the
  Assailant *is*, unlocked at CULTURE); **Subspace gravitic penetration**
  keeps its God-Speaker fold-in; the **ship-design trio** stays on the
  memory_core channel that Antiquities feeds.

## 3. The tree — five stages, tier grammar conformant

Five nodes, T0–T4, one per stage. Costs sit in-band but are *floors* — the
real cost is artifacts applied (`baseCost` is the cataloguing labor).

| stage | tier | node (defName) | artifacts to complete | what completing it means |
|---|---|---|---|---|
| **LANGUAGE** | T0 · 500 | `RUT_Antiq_Language` | 4 | The glyph-grammar cracks. Every later urn read yields MORE (see §4 yield curve). Map: ancient sites get true-name labels. |
| **RELIGION** | T1 · 1200 | `RUT_Antiq_Religion` | 7 | The liturgical register. Shrine sites revealed on the world map; Conduit Choir unhidden; ancient "graves" become readable (mood buffs for respectful handling, debuffs for looting-without-reading). |
| **CULTURE** | T2 · 2400 | `RUT_Antiq_Culture` | 10 | Daily life, law, grief. War children become *identifiable* (inspect shows name, fortress, generation). Xenobiology unhidden. God-Speaker Array unhidden. |
| **CARTOGRAPHY** | T3 · 4000 | `RUT_Antiq_Cartography` | 12 | The secret geography. Vault sites revealed (the 5–7 of VAULT_DUNGEON_CONCEPT_1), each with its *access phrase* — a read-open route that bypasses the siege turrets for one crew, once. Liturgy of the Hull unhidden. |
| **VOICE** | T4 · 6000 | `RUT_Antiq_Voice` | 15 | The living register — how to *address* an ancient. Enables the Call-Out (§7). The Gods Speak Back unhidden. The ship's last partitions accept the challenge phrases. |

Total: **48 artifacts read** across the campaign (of a world population of
~70–90 generated pieces — scarcity real but not brutal; see §5). Theology
per the principles doc: Antiquities completions are **Rekko-tagged,
pride-neutral** — reading what was always written is restoration, not
transcendence. (The Helix's approach is the prideful mirror, and the tree's
tooltips can say so.)

## 4. The urn system — objects that are pages

### 4.1 The items

One family, `ThingDef` parent `RUT_AntiquityBase`, minifiable, beautiful,
absurdly heavy silver value *to the Helix only* (§6):

- `RUT_Antiquity_Urn` (common, ~70% of generation) — the ubiquitous form.
- `RUT_Antiquity_Stele` (uncommon) — boundary-stones; cartography-weighted.
- `RUT_Antiquity_Gravegood` (uncommon) — personal items; culture-weighted.
- `RUT_Antiquity_Testament` (unique class, §7) — written in the player's era.

Each carries two generated text fields at spawn: a **surface description**
(what anyone sees) and a **read narrative** (revealed after reading — richer,
and stage-aware: the same urn re-inspected after LANGUAGE shows more than it
did before, which is cheap to fake by unlocking the second field).

### 4.2 Reading — the loop

Reading happens at the **Scrap Shrine** (the Rites T0 building gains a second
job: `RUT_ExamineAntiquity`, Intellectual + Artistic average, ~1 in-game day
per piece). Reading is **non-destructive**: the piece gains a `Catalogued`
flag (comp state), fires its read narrative as a letter, and contributes one
techprint-application to the current stage node. A catalogued piece is
*spent for knowledge but intact for silver* — the whole Helix tension in one
flag (§6).

**Yield curve** (the LANGUAGE payoff): before LANGUAGE completes, each read
contributes 1 and takes a full day ("we copy patterns we cannot read").
After, reads take half a day and *common* urns still yield 1 — but the reader
occasionally (say 15%) identifies a piece as a **key-text** worth 2. Later
stages raise the key-text rate. Knowledge accelerates itself; the early game
is deciphering, the late game is *fluency*. (This is the Heaven's Vault
loop — translation starts as guesswork and becomes sight-reading — and Outer
Wilds' rule that the only real currency is understanding.)

### 4.3 The narrative generator — grammar of an alien canon

Generation composes each narrative from four axes (data-driven lists,
assembled by a small C# text builder or, v1, ~200 curated fragments in defs):

- **A. Imagery domain** (what is depicted): tide-mechanics of a locked world
  · gene-braids and decanting · door-music (codes as melody) · the Choir of
  Conduits · war-grief · orbital shepherding · the Scald's spill · null-bands
  (deliberate blankness).
- **B. Formal device** (how meaning is carried): sacred repetition counts ·
  the honored error (every piece contains one deliberate flaw as signature) ·
  negative space as speech · interlocking borders that continue onto other
  urns (pieces literally quote each other) · glaze layers read by touch.
- **C. Erasure motif** (the war's shadow): the unpainted band where a name
  was withheld · the eaten figure · ash-tempered glaze from burned archives ·
  a figure depicted refusing to speak to its own child.
- **D. Register** (which stage it feeds): liturgical / civic / funerary /
  cartographic / address.

**Ten example narratives** (tone target — alien associations, no
fantasy-generic "runes of power"):

1. *Nine hundred birds in nine bands, and every bird's eye is a punched hole.
   Held to the sun, the holes are a star map. Held to a fire, a different
   one. The rim repeats a phrase your reader renders as: "the sky we kept /
   the sky we fed."*
2. *A procession of figures carrying water uphill. The water is painted
   flowing down. The contradiction is the sentence — your reader believes it
   names the Scald, the lake that should not be, and calls it a promise
   kept.*
3. *The glaze is full of ash, and the ash is full of half-burned glyphs — a
   library's cremains, fired into the vessel that outlived it. The only
   painted figure kneels, hands open, depicted deliberately without a
   mouth.*
4. *Seventeen interlocking spirals; the seventeenth is wrong. Reading the
   error against the canon yields four tones. The clan has heard the
   Utinni's door-chime make three of them.*
5. *A child's grave-good: a toy engine, anatomically perfect, every part
   labeled in the civic register except the core, which is labeled in no
   register at all — a word that appears on no other object. Its parents
   gave it one word the enemy could never have heard before.*
6. *The urn depicts urns. Rows of them, each tiny vessel's pattern legible
   under magnification and each one real — a catalogue of pieces your clan
   has not found, painted as if to say: we counted on you.*
7. *A wide unpainted band where the principal figure should stand. The
   figures at either side avert their faces from the blankness in postures
   of love, not fear. The ancients could mourn a name they refused to
   write.*
8. *Two figures exchange breath through a reed. Below, the same two figures
   exchange the reed through breath. Your reader marks it liturgical,
   flags the inversion as the oldest known instance of the Choir's
   call-and-answer, and admits the second panel still defeats them.*
9. *Battle scene: ancients firing into a tide of shapes that are drawn as
   ABSENCES — urn-colored silhouettes, unpainted, as if the enemy could not
   be depicted, only left out. One silhouette has begun, horribly, to
   paint itself.*
10. *The stele's face is blank. Its four EDGES carry the entire text, one
    glyph-row deep, readable only by walking its perimeter with a hand on
    the stone: a road-sign for a road that arrives underground, in the
    dark, by touch.*

### 4.4 Where they generate

- **Ancient shrines/ruin map-gen** on the frozen world: 1–3 per ancient
  structure (patch existing ruin prefabs and the vanilla ancient-complex
  loot tables; the "ubiquitous urns RimWorld always puts there" become THIS
  item on Ash'karr).
- **Vault set pieces** (§8): hoards of 8–15.
- **Quests/traders** (§5): rare, priced absurdly once word spreads.
- The map is FROZEN — the world-map placement pass is authored once via the
  bridge, like everything else on Ash'karr.

## 5. Economy & tensions

World supply ~70–90 pieces vs 48 needed: the player can miss, sell, or lose
a third of the world's art and still finish — but *cannot both finish and
sell freely*. That arithmetic is the whole point and should be discoverable
in-game (the tree UI shows `pieces read / pieces known to exist / pieces
LOST` once LANGUAGE completes — urn #6 above is the in-fiction census).

- Early game: urns are heavy trinkets. Caravans sell them cheap.
- After the Helix's standing order becomes known (first Helix visit after
  the player owns 3+): every trader reprices. The world notices demand.
- After CULTURE: caravans essentially stop selling — "a buyer on retainer
  already." Supply becomes expedition-only. The economy tightens exactly as
  the player's fluency peaks.

## 6. The Helix tension — one flag, three feelings

The Helix (Ascendant Ladder faction) maintains a **standing purchase order**:
any antiquity, generous silver, no questions — and pointedly **more for
uncatalogued pieces** ("unhandled specimens"; they believe reading
contaminates provenance — they are wrong about the canon in every possible
way, and this is one more).

- Selling a **catalogued** piece: clean silver. The knowledge is kept; the
  object goes. Rekko-neutral. (Late game this is the intended faucet — the
  owner's "Helix buys ALL urns" stands; the ship just sees them first.)
- Selling an **unread** piece: premium silver + a permanent entry in the
  LOST ledger + a one-line ship reaction on the letter ("The Utinni was
  still reading that."). No mood mechanics, no punishment — just a counter
  that never goes down, on the same screen where the tree is. The feeling
  is designed to arrive later, at CARTOGRAPHY, when the player is 2 short
  and the ledger says LOST: 9.
- **The Temptation quest** (repeatable, rare): the Helix requests N unread
  pieces NOW for a genuinely excellent boon (Ascendant Ladder techprint,
  gene-pack, a serum cache). This is the campaign's temptation gradient in
  miniature and belongs on the same pride register as The Reach.

## 7. The living ancients — from targets to strangers

- Pre-VOICE: war children wake hostile, fight, and (per existing canon) want
  nothing but out. CULTURE lets the player *see who they are*; that alone
  reframes every fight the player has already had.
- **VOICE enables the Call-Out**: a targeted interaction (ability on the
  Scrap-Shrine-trained reader, or a lord-toggle incident) usable on a waking
  chamber or mid-fight. The reader speaks the address register. Roll is not
  random: it succeeds if the speaker's Artistic+Intellectual passes a bar
  and the clan's LOST ledger is under a threshold — *the world remembers
  what you sold.* Success: the ancients stand down (lord switches to a
  leave-map behavior), take nothing, harm no one, and go. They do not help.
  They were never going to help. That is the point.
- **The Testament**: the first time a Call-Out succeeds at a waking chamber,
  one ancient pauses at the map edge, sets down a fresh urn, and leaves.
  `RUT_Antiquity_Testament` — the only piece written *in the player's era*,
  its narrative unique and hand-authored: what the war children think of
  the small scavengers who learned to read. Reading it is the emotional
  receipt for the whole tree (and worth 3 toward VOICE if it isn't already
  complete). The frozen-Rakata vault scene (type ③, tile 20853's V6) is
  this beat's big sibling and should require VOICE — the one vault where
  the payoff is a conversation.

## 8. Vaults as urn payouts

VAULT_DUNGEON_CONCEPT_1's payoff ladder gains a fourth rail: every vault
core includes an **urn hoard** (8–15 pieces, cartographic/liturgical
weighted) — the ancients' own curated caches, stored where they stored
everything else worth keeping. To vanilla eyes, absurd loot ("you fought a
Singularity Cannon for POTTERY"); to this campaign, each hoard is 1–2 full
stages of progress and the player will plan sieges around it. CARTOGRAPHY's
access phrases close the loop: deep fluency converts future vaults from
siege-problems into pilgrimage-problems — one crew, read-open route, once.

## 9. Build plan — slices, each shippable alone

| # | slice | mechanism | cost |
|---|---|---|---|
| 1 | Tree + items + reading loop | XML defs (5 research + tab or Rites-tab share, 4 ThingDefs w/ comp flag) + RR techprint economy for one-piece-one-advance + one WorkGiver | S — days; the ruled techprint route means near-zero C# |
| 2 | Narrative generator | v1: ~200 curated fragments as defs + combinatorial assembly comp (axes A–D); v2: grammar builder | S/M — writing-heavy, code-light |
| 3 | Progress meter + reveals + LOST ledger | one GameComponent, cloned from `ShipMemory`'s (same reveal-letter + hidden-prereq unhide pattern, already shipped) | M |
| 4 | Map reveals | world objects/labels via the bridge on the frozen map at stage completion | M — bridge tooling exists |
| 5 | Helix order + Temptation quest | trade patch + one QuestScriptDef | M |
| 6 | Call-Out + Testament | C#: ability + lord-job swap + edge-drop; the one genuinely new mechanic | L |
| 7 | Vault hoards | rides VAULT_DUNGEON_BUILD_1's loot pass | folds in |

Slice 1+2 alone already play: find urns, read urns, watch a tree fill, feel
the Helix pull. Everything after deepens it.

## 10. Open questions — genuinely the owner's

1. **Scarcity temperature**: 70–90 world pieces vs 48 needed — is a
   permanently-failable VOICE acceptable if a player sells recklessly, or
   should late quests backstop the count? (Design recommends: failable, with
   the Testament as the only guaranteed piece.)
2. **The Rites' hidden prereqs on Antiquities stages** — this welds the two
   trees permanently. Confirm the weld (it supersedes "Rites reveal gate is
   later ship-memory work" with a concrete mechanism).
3. **Call-Out gating on the LOST ledger** — "the world remembers what you
   sold" is a hard consequence for silver taken 40 hours earlier. Keep, or
   soften to a higher bar instead of a lockout?
4. **Testament tone** — grateful, ambivalent, or unreadable-by-design? (One
   paragraph, but it is the campaign's emotional signature; his voice.)
