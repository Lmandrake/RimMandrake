<!-- status: RULED (owner, 2026-09-04, by card) and REVISED same day by the
     owner's comment pass, ingested throughout:
     ① failability is now APPARENT, not absolute — the gods rage and intone
       hopelessness, but the Recovery Raid (§7) can pay the error back at
       great cost (supersedes the card's "permanently failable");
     ② the Rites↔Antiquities WELD stands and IS the Rites' revealed-not-bought
       gate (supersedes the "later ship-memory work" placeholder in
       src/RimUtinni/Rites/About/About.xml);
     ③ the Call-Out's LOST-ledger gate is HARD — the world remembers what you
       sold — but see ① for the payback route;
     ④ the Testament is AMBIVALENT — gratitude without warmth.
     Comment pass also landed: the degraded-archive ship canon (§1), god
     reactions + the Narrator's register + techprint radiation (§2.1), the
     Urn Reading Station (§4.2), the ornate narrative register (§4.3),
     Helix-directed god anger (§6), the Empire urn-hunt + Shattered Vault
     (§8.1), and the faction semi-permanent bases seed
     (design/Jawa/faction_semipermanent_bases_seed.md).
     Feeds RESEARCH_TREE_NORMALIZATION_1, VAULT_DUNGEON_CONCEPT_1,
     ASSAILANT_DUNGEON_BUILD_1, and the Rites/ShipMemory line.
     Execution: ANTIQUITIES_TREE_BUILD_1 — UNBLOCKED 2026-09-04 (owner:
     the expansion/review sitting this was waiting on concluded; tree
     rebrand names/merges stay open, but slices 1-2 do not depend on them).
     Slice 1 (tree + items + reading loop) shipped same day,
     src/RimUtinni/Antiquities/ — see the item file for what's built vs.
     still owed. -->

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

**And the Utinni is party to it — but not as a neat lockbox.** The ship is
Rakata substrate (canon: substrate kinship, the vault-draw), and her
knowledge store is **severely degraded**: damaged and faded across the
centuries, then rudely overwritten by the damaged, kludged Jawa-mind persona
core that is now her living soul. What remains is a massive archive of
fragments and incomprehensible garbage. Each urn read into her offers
**pattern-matching and a reconstruction framework** for a small portion of
it — the way seemingly random fragments of correct DNA can begin to
reassemble even on a poor scaffold. This is the literal mechanism of "each
urn advances a research tech that helps the ship unlock more of its own
memories": not password hints, not a download — **strand-by-strand
regeneration of a ruined archive against a template the world still holds.**

Two hard limits keep the soul of the campaign safe: the urns do not encode
the ship's operating system or any live system, so **nothing they restore
can ever overwrite the Jawa-born gods** — it is the *racial and faction
database* of the Rakata that is being regenerated, nothing else. And the
record comes back incomplete by nature: what the restoration yields is
never a primer, always a damaged text that must still be proven out by
trial, error, and testing **with Jawa hands and minds participating** — the
research is real research, seeded rather than skipped.

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
  CULTURE; The Gods Speak Back needs VOICE). The mechanism, precisely: **the
  Rites are authorization** — they permit the ship to allocate her own
  resources to the database restoration/reintegration, and they permit the
  gods to alter their own existence to come into harmony with what returns.
  The ship cannot perform a liturgy in a language the clan has not yet
  taught her to read; the gods cannot integrate what no rite has authorized.
  This also solves the Rites' missing revealed-not-bought gate — the reveal
  channel is Antiquities progress.
- The already-flagged repurpose hooks slot in (functionless_tech_candidates):
  **Xenobiology** becomes Antiquities-adjacent (the study of what the
  Assailant *is*, unlocked at CULTURE); **Subspace gravitic penetration**
  keeps its God-Speaker fold-in; the **ship-design trio** stays on the
  memory_core channel that Antiquities feeds.

### 2.1 The gods at each integration — and what radiates outward

Every integration (an urn read out into the ship) produces **per-god
reactions from each god's own vantage**: they are free to be pleased or
displeased by the *content* — a war-grief text may sadden the gentle and
vindicate the wrathful — but all are pleased, to varying degrees, by the
**wholeness** it brings. Net mood is always positive; the spread between
gods is flavor and characterization, rolled off the narrative's axes (§4.3
register + imagery domain map naturally onto god temperaments).

**The ship never explains any of this in systems language.** The Narrator
carries it, in an intoned register whose canonical example is the owner's
own (verbatim, the tone target for every integration letter):

> *"As the ancient lore enters the collective Knowing of the gods, its
> truths radiate outward like an organizing principle. Where they are
> needed, they bind and mend. Where there is dissent, they withdraw. What
> is left is less cracked, less fragmented, and the patterns restored find
> yet other places where relevance guides. To remember one thing is to
> remember others too, or at least recognize their absence."*

**Techprint radiation**: occasionally an integration emits a techprint for
ship function, manufacturing capability, or ship repair — weapons, engines,
systems — because as one portion of the database learns to repair itself,
the same lesson applies elsewhere. These land as ordinary techprints into
THE SHIP tree's economy: the knowledge *seeds* the research, and Jawa hands
still do the proving. Frequency is a tuning knob; the feel target is
"a gift, not a faucet."

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

### 4.2 Reading — the loop, and the Urn Reading Station

Reading happens at the **Urn Reading Station** — a custom piece of ritual
furniture, authored with real art effort and **animation**, placed at the
center of the shrine where the god holograms begin to appear. It is the
physical centerpiece of the whole progression meter: the station turning an
urn slowly in a scanning cradle while glyph-light crawls its glaze is the
image the campaign wants burned into the player. (Art + animation is its own
slice in §9 and worth the spend — this object is on screen for the entire
campaign.) The Scrap Shrine hosts it; the station is the instrument.

The job (`RUT_ExamineAntiquity`, Intellectual + Artistic average, ~1 in-game
day per piece) is **non-destructive**: the piece gains a `Catalogued` flag
(comp state), fires its read narrative as a letter, triggers the gods'
integration reactions (§2.1), and contributes one techprint-application to
the current stage node. A catalogued piece is *spent for knowledge but
intact for silver* — the whole Helix tension in one flag (§6).

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
  · gene-braids and decanting · maker's marks and workshop lineages · the Choir of
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
- **E. Data-density tell** (owner's revision — every narrative carries at
  least one): a fractal edge that keeps resolving past every magnification ·
  detail sharp to the finest resolution of the clan's scanning instruments,
  and clearly not exhausted there · a thin diamond coating sealing the work
  against the centuries · a second reading channel in a physical medium
  (sunlight, fire-flicker, touch, tilt, magnification, temperature) ·
  halos, borders or grounds that are visibly *structured information in an
  unknown format* rather than ornament. The tell is what makes an urn feel
  like **massive data encrypted in subtle ways** — a terabyte wearing a
  pot's shape — and it is also the mechanism the Shattered Vault event
  (§8.1) relies on: fractal encoding means a shard still carries a
  readable fraction of the whole.

**Ten example narratives** (tone target — alien associations, no
fantasy-generic "runes of power"; ornate, and always suggesting **massive
data encrypted in subtle ways**. #1 is the owner's own, verbatim, the
register the other nine follow):

1. *Nine hundred birds in nine bands, and every bird's eye is a punched hole
   with a surprising fractal edge. Held to the sun, the holes form a star
   map. Held to a fire, the flickering motion surrounds each star with a
   halo of encrypted information in an unknown format. The rim repeats a
   phrase your reader renders as: "The sky we kept / The Sky we fed / The
   Sky we lost." The glaze patterns are extremely detailed and sharp to the
   finest resolution of your scanning instruments, and a thin coating of
   diamond has been used to seal away the centuries.*
2. *A procession of figures carrying water uphill; the water is painted
   flowing down, and the contradiction is the sentence. Under magnification
   every droplet in the false-falling stream is itself a vessel, and every
   vessel holds a smaller procession, five recursions deep before your
   instruments blur — your reader believes the whole column names the
   Scald, the lake that should not be, and reads the recursion as a promise
   kept and kept and kept.*
3. *The glaze is full of ash, and the ash is full of half-burned glyphs — a
   library's cremains, fired into the vessel that outlived it. Spectrograph
   raking finds the fragments are not scattered: they are SORTED, graded by
   char into strata, a filing system for the destroyed. The only painted
   figure kneels, hands open, depicted deliberately without a mouth, and
   the diamond seal over its face is twice as thick as anywhere else.*
4. *Seventeen interlocking spirals; the seventeenth is wrong. The error,
   read against the canon, resolves into a maker's mark — and the clan has
   seen that mark before, stamped deep in the Utinni's keel plates where
   only the crawlspace welders go. The same workshop. Each spiral's
   groove-wall carries sub-ridging too fine for the eye that your scanner
   renders as a dense, regular signal in no known encoding — kilometers of
   it, coiled into a handspan of clay.*
5. *A child's grave-good: a toy engine, anatomically perfect, every part
   labeled in the civic register except the core, which is labeled in no
   register at all — a word appearing on no other object in the world. The
   toy's surfaces are machined to interference-pattern tolerances; tilted
   in lamplight it projects a faint moiré that is almost certainly a
   schematic, of something no toy should know. Its parents gave it one word
   and one machine the enemy could never have heard before.*
6. *The urn depicts urns. Rows of them, each tiny vessel's pattern legible
   under magnification and each one real — a catalogue of pieces your clan
   has not found. Deeper magnification finds the painted urns bear painted
   urns of their own, and the census continues past your optics' floor. It
   was painted as if to say: we counted on you, and we counted
   everything.*
7. *A wide unpainted band where the principal figure should stand. The
   figures at either side avert their faces from the blankness in postures
   of love, not fear — and the "blank" band, under raking light, is a
   relief-map of microscopic stippling: not empty, ENCRYPTED, a name
   written so it could be mourned without ever being read.*
8. *Two figures exchange breath through a reed. Below, the same two figures
   exchange the reed through breath. Your reader marks it liturgical, flags
   the inversion as the oldest known instance of the Choir's
   call-and-answer — and notes that the reed's bore, magnified, is scored
   with a helical track like a record's groove, which the instruments can
   trace but nothing in the clan's possession can play.*
9. *Battle scene: ancients firing into a tide of shapes drawn as ABSENCES —
   urn-colored silhouettes, unpainted, as if the enemy could not be
   depicted, only left out. The silhouettes are not paint-bare: they are
   micro-etched with dense garbage, deliberate noise, the one place on the
   vessel where the patterning carries NO information at all — a portrait
   of the enemy made of meaninglessness. One silhouette has begun,
   horribly, to paint itself.*
10. *The stele's face is blank. Its four EDGES carry the entire text, one
    glyph-row deep, readable only by walking its perimeter with a hand on
    the stone: a road-sign for a road that arrives underground, in the
    dark, by touch. The glyph-row's floor is diamond-sealed and fractally
    ridged; a fingertip reads the road, a scanner reads the toll, and your
    reader is certain some third instrument the clan does not own would
    read the reason.*

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

- **Who the buyer is matters as much as the flag** (owner's revision). It
  will become revealed, as integrations accumulate, that the ship does not
  want the *Helix in particular* acquiring this knowledge: only the Rakata
  are meant to know it, and though the Helix claims to be their children,
  **they are most definitely not.** The god-mood ladder:
  - unread piece → **Helix**: the gods are **INFURIATED** (the strongest
    standing displeasure in the campaign; the letter says so in the
    Narrator's register, not in numbers);
  - catalogued piece → **Helix**: the gods are **UNHAPPY** — the knowledge
    is kept, but the wrong children hold a page of it;
  - any piece → **any other faction**: **neutral** — they cannot understand
    what they are holding, and the gods know it.
- Selling a **catalogued** piece to a non-Helix buyer: clean silver,
  Rekko-neutral — the intended late-game faucet.
- Selling an **unread** piece to anyone: premium silver + a permanent entry
  in the **LOST ledger** + a one-line ship reaction on the letter ("The
  Utinni was still reading that."). The ledger counts *reading lost*, and it
  counts it whoever the buyer was; the god-mood above is the separate,
  Helix-directed judgment. The feeling is designed to arrive later, at
  CARTOGRAPHY, when the player is 2 short and the ledger says LOST: 9 —
  and §7's Recovery Raid is what that feeling can be spent on.
- **The Temptation quest** (repeatable, rare): the Helix requests N unread
  pieces NOW for a genuinely excellent boon (Ascendant Ladder techprint,
  gene-pack, a serum cache). This is the campaign's temptation gradient in
  miniature and belongs on the same pride register as The Reach.

## 7. The living ancients — from targets to strangers

- Pre-VOICE: war children wake hostile, fight, and (per existing canon) want
  nothing but out. CULTURE lets the player *see who they are*; that alone
  reframes every fight the player has already had.
- **VOICE enables the Call-Out**: a targeted interaction (ability on the
  station-trained reader, or a lord-toggle incident) usable on a waking
  chamber or mid-fight. The reader speaks the address register. Roll is not
  random: it succeeds if the speaker's Artistic+Intellectual passes a bar
  and the clan's LOST ledger is under a threshold — *the world remembers
  what you sold.* Success: the ancients stand down (lord switches to a
  leave-map behavior), take nothing, harm no one, and go. They do not help.
  They were never going to help. That is the point.
- **Apparent failability, and the Recovery Raid** (owner's revision,
  superseding the earlier "permanently failable" card). When the ledger is
  over threshold, the campaign is designed to *feel* lost: the gods grow
  angry, the Narrator intones in the register of finality, no UI promises a
  way back. But one exists — **attack the faction the urns were sold to.**
  The sold pieces persist, tracked to a randomized settlement of the buying
  faction; a raid can take them back, converting LOST entries to RECLAIMED
  at the cost of a war the clan chose. The error can be paid back — at
  great cost, in the open, against a faction the player made rich. (A fun
  consequence, not a fail state; the hopeless *tone* is part of the
  design and must not leak the mechanism early.)
- **The Testament**: the first time a Call-Out succeeds at a waking chamber,
  one ancient pauses at the map edge, sets down a fresh urn, and leaves.
  `RUT_Antiquity_Testament` — the only piece written *in the player's era*,
  its narrative unique and hand-authored: what the war children think of
  the small scavengers who learned to read. Reading it is the emotional
  receipt for the whole tree (and worth 3 toward VOICE if it isn't already
  complete). The frozen-Rakata vault scene (type ③, tile 20853's V6) is
  this beat's big sibling and should require VOICE — the one vault where
  the payoff is a conversation.

## 8. Vaults as urn payouts — and the Empire's war on memory

### 8.1 The Empire arc (late game)

- **Rumors first**: after CULTURE, trade-tab whispers and comms chatter that
  the Empire has begun hunting urns down **to destroy them** — not to use,
  not to sell; to spite. (In truth an intelligence assessment concluded the
  artifacts are "a morale asset of the anomalous vessel" — they think the
  urns are a fetish, a value thing. They have no idea.)
- **The Shattered Vault** (event, post-CARTOGRAPHY): one revealed vault
  site, visited, is found ALREADY RAIDED — the Empire noticed the pattern
  in where the player's caravans keep going and got there first. Rubble,
  scorch, and the floor carpeted with **shattered urn shards**. The gut
  punch is the point.
- **And then the turn**: the fractal encoding (§4.3 axis E) means a shard
  still carries a readable fraction of the whole. Gathering ALL the
  fragments opens a reconstruction job that the clan cannot do alone — it
  needs the **droids' computing resources, in partnership with the Rust
  Cathedral** (and their semi-permanent base thread; see the bases seed
  doc). Weeks of compute, then a partial payout: some fraction of the
  hoard's stages-worth, recovered from what the Empire thought it erased.
  The Empire destroyed the pots. It did not destroy a single sentence it
  could not read.

### 8.2 Vaults as urn payouts

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
| 8 | **Urn Reading Station** | ThingDef + authored art + ANIMATION (the campaign's centerpiece object — real art budget, sprite pipeline + review save) | L, art-heavy |
| 9 | God integration reactions + Narrator letters | per-god reaction table off axes A–D + the intoned letter register (§2.1); techprint radiation hook into THE SHIP economy | M |
| 10 | Helix god-mood ladder + sold-urn tracking | buyer-aware sale hooks; sold-piece registry per faction settlement (feeds 11) | M |
| 11 | Recovery Raid | quest/raid on the randomized holding settlement; LOST→RECLAIMED conversion; the hopeless-tone gating (no early leak) | M/L |
| 12 | Empire arc: rumors + Shattered Vault + shard reconstruction | 2 incidents + a shard item + a droid/Rust-Cathedral compute job | L |

Slice 1+2 alone already play: find urns, read urns, watch a tree fill, feel
the Helix pull. Everything after deepens it.

## 10. Rulings and what the next sitting holds

All four original questions RULED 2026-09-04 (header block): apparent
failability with the Recovery Raid as payback (supersedes "permanently
failable"); the Rites weld confirmed; the hard LOST-ledger gate kept (with
the payback route); the Testament ambivalent.

⛔ SUPERSEDED 2026-09-04 — the owner unblocked `ANTIQUITIES_TREE_BUILD_1`
once the expansion/review sitting below concluded (all fourteen sec-G
decision points ruled by card; this doc ruled). Slice 1 is built:
`src/RimUtinni/Antiquities/`, `infrastructure/state/items/
ANTIQUITIES_TREE_BUILD_1.md`.

Open threads staged for the next sitting:

1. **God roster mapping** — which gods react how to which registers/domains
   (§2.1's table needs the actual god roster put against axes A and D).
2. **Techprint radiation rate** — "a gift, not a faucet" needs a number.
3. **The bases seed** — the faction semi-permanent bases concept
   (`design/Jawa/faction_semipermanent_bases_seed.md`) wants its own design
   pass; Antiquities touches it twice (urn sanctum at the Rust Cathedral,
   the shard-reconstruction compute partnership).
4. **Ship footprint concern** — the owner flags the gravship may be too big
   for standard maps; very large maps or off-ship storage (the bases) are
   the two compensators named so far. Belongs to the gravship/map thread,
   recorded in the bases seed.
