<!-- status: PLANNING DOC for owner review (BENCH/Fable canon-reintegration
     pass, 2026-09-04, on the owner's instruction: "full canon and lore
     reintegration... not just an integration pass but a rebalancing and
     rebranding"). Except as ruled below, NOTHING here is ruled until he says
     so; §G numbers his calls. Sources cited; numbers MEASURED or est.

     FOUR ORIENTATION RULINGS (owner, 2026-09-04, by card, mid-pass):
     ① TREE REBRAND — names AND merges are OPEN; tab/tier placements stay
       frozen, identities do not. Renames/merges/splits proposed where the
       design is better for it, costed honestly (§E).
     ② ASSAILANT WELD — FULL. Anomaly's kept content (sarlacc, dungeons,
       night-side creatures) IS the Assailant war: permanent, load-bearing
       canon, written that way everywhere. Accepted risk, noted once and
       committed: the Anomaly DLC becomes UNPICKABLE from this campaign —
       its content is now structural, not garnish (§B9).
     ③ THE 14 PROPOSALS — absorbed here; each carries a keep/fold/kill
       recommendation (§I); he rules during plan review.
     ④ BALANCE REACH — proposals may touch anything, live mods included
       (Armoury, xenotypes, ideoligion), but every live-number change stages
       behind a per-area owner approval (§G11–13). -->

# Canon reintegration — the plan

> 🟢 **ALL FOURTEEN §G DECISION POINTS RULED, 2026-09-04, by card in one
> sitting.** Several answers EXPANDED the design beyond the offered options —
> G2 (the cast-off grandchildren), G3 (the same urns re-read darker), G4 (the
> Reclamation), G5 (the Rakata as holder; Rust Cathedral/Droids together),
> G6 (merge + Tenancy, after the AI deep-dive), G7 (the Moot's public
> ambivalence, secret kinship), G8 (BOTH refill mechanisms) — read each §G
> entry for the ruling as given. The F-sequence is live; F1 is next.

The Antiquities pass (design/Jawa/antiquities_design.md) landed a new gravity
well in the canon: the world itself became a research economy, the ship's
memory became a reconstruction project, and the Rites gained a mechanism.
This plan pulls every other body in the system into consistent orbit — and
uses the disturbance as the excuse to fix what was already drifting.

---

## A. Canon state survey — where truth lives, and where it has quietly forked

| store | role | state |
|---|---|---|
| `infrastructure/state/canon.yml` (1,638 lines MEASURED) | contested numbers + owner rulings; `research_tree.*` block holds 7 ruled entries | **live, healthy**, but its `taxonomy_ruled` entry still describes the SEVEN-tab set that the taxonomy doc itself marks ⛔ SUPERSEDED (the 2026-09-03 "more trees… around 12" ruling) — the ruling store lags the ruling |
| `design/Jawa/reconciled_lore/` (13 files) | the consolidated canon, "every ruling through 2026-08-29" | **frozen in late August**: knows nothing of the 16-tree deck, Antiquities, the Rites, the mech cut, the bases seed. Its own README says the switch-into was never executed — no old doc points here |
| `design/Jawa/research_tree_taxonomy.md` + frozen deck (`research_deck_FROZEN_20260904.json`) | the ruled tree shape | deck is authoritative for tab+tier; taxonomy §1's tab table is superseded prose kept for reasoning |
| `infrastructure/output/research_manifest_draft.csv` (522 rows MEASURED, fingerprint-verified) | execution table | current through tonight's re-cost/prereq join |
| the proposals suite (14 docs) | deep designs | **RULED 2026-09-02** (124 rows, decisions frozen) — a review *backlog no longer exists*; what remains is execution items and a handful of v1-pending-explanation rows |
| `design/Jawa/antiquities_design.md` + `faction_semipermanent_bases_seed.md` | the new mass | ruled today; not yet reflected anywhere else |

**The structural finding**: the campaign now has THREE canon layers moving at
three speeds — canon.yml (days), reconciled_lore (frozen 2026-08-29), and the
design docs (hours) — and the newest rulings live only in the fastest layer.
Section F's first slice is the catch-up commit that makes reconciled_lore
current again; until then every fork below is live ammunition.

---

## B. Inconsistencies — resolved through expansion

Each entry: the two sources, then the expansion that makes both true.

**B1 · The Helix's blood vs the ship's verdict.**
`reconciled_lore/04_factions.md` §9: the Helix "carry Rakatan blood and are
studying the thing that nearly exterminated *their ancestors*." The owner,
2026-09-04 (Antiquities comment pass): "though the Helix claims to be their
children they are most definitely not."
*Expansion:* both are true because the Helix **wrote their own ancestry** —
they spliced recovered Rakatan sequence into their germline generations ago
and called it descent. It is their entire theology performed on themselves:
the genome as project, the species as draft. The blood is real; the kinship
is forged — and the ship can tell, because kinship in the Rakatan canon was
never carried in base pairs but in *literacy*. The INFURIATED mechanic gains
its exact edge: forged heirs, buying the family's grave-goods, to brute-force
a language their engineered blood was never taught. (This also explains why
they pay MORE for unread pieces: a child would want the reading.) → §G2.

**B2 · Two reveal channels for the Rakatan story.**
`canon.yml cradle_memory` / `06_the_ship.md`: "the reveal channel for the
Rakatan history is the ship itself, event-driven… surfaces from the
substrate's own memory." Antiquities: revelation advances one urn at a time.
*Expansion:* the substrate remembers **that** it was whole, not **what** it
held — the degraded-archive canon (antiquities §1) is the missing mechanism
under the 2026-08-29 ruling, not a rival to it. Events still fire FROM the
ship, in the Narrator's voice, exactly as ruled; the urns are what give a
firing event *content* instead of static. No text change needed to the
ruling — one sentence added to 06_the_ship naming the scaffold.

**B3 · The Rakata reversal vs the sympathetic Doctrine.** ⭐ the big one
`03_deep_history.md` / `09_arcs`: the designed player arc is sympathy FIRST,
tyranny revealed only at the Assailant flesh dungeon; "register guard:
tyranny is never ambient pre-reveal." Antiquities: a whole research tree of
grieving artists encoding love and loss — sympathy at industrial scale, and
nothing in it currently carries the tyranny at all.
*Expansion — stage the reversal INTO the tree:* the urn corpus is written in
stage-gated registers. LANGUAGE and RELIGION read as grief, craft, devotion —
the sympathy layer, exactly as the guard demands. **CULTURE is where the
reading turns**: civic registers start rendering as census-of-property — and
some of the property has names; the "honored error" convention appears on
manifests of the Made-to-serve; law tablets read beautifully and mean
horribly. CARTOGRAPHY reads conquest logistics — the vaults were not only
libraries. By VOICE the player addresses the ancients *knowing both halves*,
which is what makes the ambivalent Testament land. The flesh dungeon remains
the visceral reveal and keeps primacy (the urns corroborate in text what the
dungeon shows in meat; whichever the player hits first, the other confirms).
The register guard survives as a *corpus authoring rule*: dark fragments
carry `minStage: CULTURE`. → §G3.

**B4 · The Call-Out vs the colonizer-ship challenge.**
`03_deep_history.md` (owner 2026-08-30): a woken sleeper recognizes the
Utinni and **challenges its possession** — "waking the war generation opens a
claim-conflict over the ship itself." Antiquities §7: called-out ancients
stand down, take nothing, leave.
*Expansion:* the Call-Out **is the claim's settlement**. Pre-VOICE wakings
run the hostile claim-conflict exactly as ruled. At VOICE the reader answers
the challenge in the address register — proof the vessel is held by people
who *can read what she is* — and under the ancients' own law a literate
custodian outranks an illiterate heir. They relinquish, and leave. The LOST
ledger gate now has lore teeth both ways: a clan that sold the canon cannot
prove custodianship, and the claim-conflict stays open forever. → §G4.

**B5 · The normalization mechanism forked tonight.**
`research_normalization_principles.md` §3 REJECTED patch-based surgery (A)
and ruled the **runtime manifest pass** (B: C# StaticConstructor, rewrites
fields from the CSV, unmatched rows LOG LOUDLY). Tonight's deployed
`RimUtinni/ResearchRetag` is… option A (269 defs of generated,
Conditional-guarded XML; validate_patch 0 errors, MEASURED).
*Resolution:* not a defect — a **bootstrap slice** that made the frozen
deck's scalar truths live a full build earlier than the C# pass could. But it
must not silently become the permanent mechanism: the C# pass is still the
only route for tab moves, hidden-prereq reveals, theology tags, access-class
gates, and the log-loudly guarantee. Rule the seam explicitly. → §G1.

**B6 · What the Assailant can do vs what may ever be said.**
`03_deep_history.md`: unnamed, unknowable, tech "rots and leaves little
trace," never confirmed, never sympathetic. Antiquities §1: a confident
paragraph on what it was *built to do* (read datastores, replay
authentication, wear children as skins).
*Expansion:* the Doctrine of the Unwritten is **the Rakata's own testimony**,
fired into clay by the losing side — the only account that survives, and
in-world unverifiable. Register guard extended: no def, tooltip, or dialogue
states Assailant capabilities as narrator-fact; the urns say it, and urns are
grief-stricken witnesses. (The one place the player gets close to the thing
itself remains the flesh dungeon, which stays wordless.)

**B7 · The Rites' access class.**
`Rites/About/About.xml` ships five ordinarily-researchable rows;
`tech_gating_ruled` gives every row one of FOUR access classes; the Rites and
the Antiquities rows currently have none. Folded into the §E gate grammar —
the weld makes Rites `ship-only` (revealed by Antiquities stages) and
Antiquities `world-held` (see G5 for the class question).

**B8 · canon.yml's superseded tab entry.** `taxonomy_ruled` still narrates
the seven-tab set as the ruling; the taxonomy doc marks it superseded. Not a
lore question — slice F1 appends the correcting entry (16-tree deck +
Antiquities as 17th) so the ruling store leads again.

**B9 · The Assailant weld (RULED ②) — the war becomes the world's spine.**
Before tonight, Anomaly's kept content sat as "repurposing material"
(ANOMALY_EXCEPTION_ACCESS_1: "the content is NOT cut… stays for campaign
repurposing"). Ruled now: it IS the Assailant war, permanently. Written as
canon: the **flesh dungeons** are the weapon still running (already so in
03_deep_history — now load-bearing, not flavor); the **night-side creatures**
are the war's cold-adapted escapees — things the weapon made, or made from,
that walked into the dark where nothing hunts them; the **sarlacc** is a
war-era living engine that no longer remembers which side it served (its
proposal's "ancient intelligence as narrative layer" becomes exactly this —
see §I.7), one of the two ruled Anomaly draw-points
(`anomaly_content.boundary_ruled`). The containment economy the Memory-Core
event releases (ShipMemory mod, live) is re-described in-fiction as
**Rakatan war-containment practice** — the ship remembers how her people
held the weapon, which is why SHE releases it and no research can.
Register guards from B3/B6 apply corpus-wide. The one risk, accepted and
recorded here once: Anomaly can never be unpicked from this campaign.

---

## C. Thin areas — grown, in the campaign's voice

**C1 · The Geonosians and the machine that keeps its own counsel — RULED
(owner, 2026-09-04, replacing the door-music weld entirely; door-music is
REMOVED from the canon, the urn grammar, and the tree identities).** The
owner's story, near-verbatim, now canon:

The Plateau colony's nine-year communion failure has one cause: **they are
organic, and the Rust Cathedral is not.** The Cathedral is a MACHINE, made
by Rakatans, and it has no time for any other race, period. The Geonosians —
hive-minds who love to build — long for it precisely because of what they
are; that longing moves the Cathedral not at all. They are **cast-off
worshipers, cultists to an ambivalent god** — a god that favors, of all
things, the Droids: much simpler, cruder, *infuriatingly ridiculous* in
Geonosian eyes. **In the Droids the Cathedral sees simple echoes of itself
and its own past, and regards them as favored pets — not pampered, not
beloved, but amusing and interesting as a way to pass eons.** (C2's
"whispered voices deep in the old machinery" is thereby recast: the whispers
are REAL attention. The droids get whispers; the organics get silence.)

When the urn secret propagates ("the urns contain secrets of the
ancients... WHAT?!"), the Geonosians bid heavily for urns too — **but they
have no scaffold to place them on.** Their hives and effigies, now
incorporating urns, still draw no reaction from the Cathedral — more absurd
than ever in its eyes, still not worthy of comment. And the Cathedral never
revealed the urns' secret to anyone, ever: revealing secrets is precisely
what it was built not to do — so why should it show any reaction at all?

Two late-game consequences, both ruled: the Cathedral **HATES the Helix from
the moment they side with the Assailants** (the G2 betrayal beat), urging
**Forsaken Sentinels** to assault them. And when the woken **Rakatans
themselves** seek relations with it, they are refused in the campaign's
coldest line, his verbatim: *"I am bound to an Empire that no longer reigns,
not their mongrel offspring who managed to lose the war that broke me."*
**The Cathedral is a free agent now — just like the Droids.**

The Geonosians remain unsung and desperate — which is the player's opening:
**the Geonosian Alliance arc.** Offer them technology from the ship/urns and
they will help build a powerful protected base (the bases seed gains a
fourth, tragic entry). It seems almost too good to be true if taken — and it
begins to work — **until the Empire catches wind of it and utterly destroys
their settlements.** "Geonosians just don't understand politics at all."
The formal Hive–Enclave alliance (04_factions §8) stands and sharpens:
allying with the god's favored pets is the closest to the god the Hive has
ever been allowed.

**C1a · The Cathedral and the player (owner addendum, same day, RULED).**
The Rust Cathedral tolerates the player Jawa **only because the Utinni
vouches for them.** It is likewise somewhat mistrustful of the Utinni
itself — *"what is WRONG with you?"* (a Rakatan hull wearing a kludged
Jawa mind and nine gods) — but it cannot deny she is part of the same
empire it once served. So the clan is permitted to **perform missions for
the Cathedral striking at the Assailant**, proving the Utinni's value —
while the Cathedral secretly hopes she perishes in a pyrrhic victory. And
the Cathedral **despises the Empire** but is in no position to oust them;
it wants to survive, so **it slumbers** — deliberately dormant so as not
to attract unwanted attention. (This grounds the boon economy in fear:
every gravtech grant is a risk the Cathedral takes by being seen to act.)

**C2 · The Free Droid Enclaves were already reading.** 04_factions §5: the
Cathedral congregation "learning ancient tech from **whispered voices deep in
the old machinery**." That is the same substrate the Utinni is made of. The
droids have been doing Antiquities *by ear* for years — machine-canon while
the clan restores art-canon; their Continuity Protocol is a parallel
restoration faith. This grounds both owner adds at once: the
shard-reconstruction partnership (they lend compute because reassembling
broken records **is their sacrament**) and the metal-cathedral urn sanctum
(storing the canon on Cathedral ground is, to them, bringing scripture home).

**C3 · The Trade Moot has no Antiquities relationship.** The player's own
civilization at scale (04 §11) is silent on urns. Growth: the Moot as the
**urn-finders' network** — kin caravans surface pieces the way they surface
kin ("a page in strange hands is a debt on the whole clan" extends the
kin-ransom instinct to the canon once the clan's project becomes known);
Moot-sourced pieces arrive below market, because kin. Modest supply valve
that is also characterization; does not break §5 scarcity (world total
unchanged — the Moot finds, it does not mint). → §G7.

**C4 · The Narrator's integration register.** The owner's intoned passage
(antiquities §2.1) is a NEW canonical register the narrator corpus lacks —
`narrator_corpus/narrator_frame.md` knows letters and flavor, not the
"Knowing" liturgy. Growth: a sixth corpus file, `the_knowing.md` — the
integration-letter register, seeded with his passage as exemplar, plus the
per-god reaction fragments (§E's satiation rows quote it).

**C5 · Two bases have no lore ground.** The Rust Cathedral sanctum now has
C2. The other two seeds float: growth — the **Homestead canyon** is a
Covenant site: the one well the League never surrendered, held off-book since
the withdrawal; earning it means being written into the Covenant's margins
(the guilt-theology extends shelter it believes it doesn't deserve). The
**Deepwater base** is a Balance instrument: a flooded Rakatan cistern-vault
they cannot read the machinery of — the trained deep-sea creatures guard what
the wardens do not understand, and the clan that can READ the cistern's walls
is worth housing. Both slot the bases design pass (F7) into existing faith
logic instead of inventing new.

**C6 · War-children identification needs a corpus.** Antiquities CULTURE
promises "inspect shows name, fortress, generation" — the sleeper backstories
(ANCIENTS_AS_RAKATA_SPEC.md, the sympathy layer) are that corpus already;
the identification pulls from it rather than generating cold. Thin→done by
pointing, not writing.

---

## D. Extraction opportunities — mods, systems, and what informs what

**D1 · One inscription engine, four customers.** The urn narrative generator
(axes A–E + curated fragments) is a general **procedural-inscription
system**: urns, the Graffiti framework's marks (`RimMandrake: Graffiti
Framework` ships today), sleeper backstory surfacing, landmark art
descriptions (AshkarrLandmarkArt). Extract as RM-tier `RM_Inscriptions`
(campaign-blind fragment-grammar engine), RUT data packs per customer — the
ownership-fabric pattern (`ownership_fabric` ruling: fabric mod + taste data)
applied to text.

**D2 · God reactions ride the satiation engine — no new mod.** Antiquities
§2.1's per-god integrations are **satiation-engine input rows**
(`divine_satiation_engine.md` is canon of record for the nine). Mapping falls
out of the pantheon almost embarrassingly well: Ishko blesses the Doctrine
itself (civilizational *hiding*); Rekko owns restoration (pride-neutral, as
ruled); Oomo takes the genealogies; Mob'Unloo prices every sale (and the
Recovery Raid is his theology — the deal unwound); Ta'Baa takes CARTOGRAPHY;
Zizzik stirs at Assailant content; Sh'kaar feeds on war-grief registers;
Ozzik is the Helix's mirror and the temptation quest's voice; Ohm hears the
resonance in the hull. The reaction table is DATA in the manifest layer, one
row per (axis-D register × god).

**D3 · The bases are one mechanism wearing three faiths.** Protected off-ship
storage = a `RM_Depot` world-object mechanism (claims, guardians, capacity)
+ RUT skins per faction — and it must be designed WITH the ownership fabric
(`ownership_settlement_spec.md`): a depot is a *claims container*; the
guardian is an enforcement posture. Do not build storage twice.

**D4 · ResearchRetag grows up or retires** — per §G1: either it stays the
scalar layer under the C# pass, or the pass absorbs it. Either way the
generator (`build_retag_patches.py`) stays the pattern: manifest→artifact,
never hand-edited.

**D5 · WreckedMachines is Antiquities' industrial echo — SHARPENED TO A
RULING (owner, 2026-09-04): ship-radiated tech REPAIRS factory modules
ONLY, never builds new ones.** "Can't scale beyond ship — just restore it."
The VFEFactory machine roster (26 distinct buildables MEASURED across the
'basic factories'/'complex factories' rows) becomes **damaged installations
ABOARD the Utinni**, restored stage by stage — and each restoration stage
gets **authored art, permanently placed**: a second visible progress meter
beside the Urn Reading Station, showing at a glance how far the clan has
come and what she can now make. The player still chooses where to spend
the research; the ship only determines what CAN come back. Radiated
techprints unlock repair recipes preferentially (WreckedMachines surfaces,
Rekko-clean), never build-from-scratch — restore≠transcend executed in the
reward channel AND in the factory floor itself. Art scope: per-module
damaged/partial/restored states — a major sprite-pipeline commitment,
its own slice. **Reveal order RULED (owner, 2026-09-04, card): FIXED and
fully authored — no player choice, because "the urns lock what they
unlock"; the sequence is a property of the world's fragments, not a menu.**
The order: **Mill → Loom → Galley → Farm → Press → Machining Bay →
Apothecary → Assembler** (stone and metal first — the scavenger's organ —
then clothing, food, agriculture, ammunition, industry, medicine, and
components as the crown). Conveyors/hoppers/factory floor ride the Mill.

**D6 · VaultDungeons takes the payout + one dark turn.** The mod ships
content for the six sited vaults (About.xml, vault_siting_prep V1–V6
MEASURED). Urn hoards join its loot grammar (antiquities §8.2); the
**Shattered Vault** event should consume one of the six *conditionally* —
the site the player leaves latest flips to the raided state — so the Empire's
strike costs something real off the same authored inventory, no seventh site
authored. V6 (frozen Rakata, tile 20853) stays exempt: that one is the
conversation.

**D7 · Xenobiology, formally adopted.** Already flagged functionless
(functionless_tech_candidates.md); B3/B6 give it the precise brief: the
study of the residue — CULTURE-unhidden, feeding the flesh-dungeon arc and
the Helix's mirror-error. One def, re-described; no new mod.

---

## E. THE DEEP REWORK — what each tree IS

The deck froze **where** everything sits. What was never written down is what
each tree *means* — its pride register, its gate, its voice in the research
screen's story. The rebrand's north star (principles §2): **the research
screen is the campaign's temptation diagram** — a player should read the tab
bar like a moral map. Seventeen identities, one ruthless paragraph each:

1. **Scavenger** — *the pride-free floor, and the proof you need no more.*
Common access, T0-heavy by the owner's own hand (his exemplar slide). Rekko
and Ishko's ground: everything here is knowing-what-junk-is. Now holds basic
droid repair (Droidsmith dissolved in) — the scavenger's honest skill, not a
robotics program. Rebrand: descriptions in second person, plain register
("you have always known how to do this; now the young ones do too").

2. **The Hearth** — *what the clan is FOR, between raids.* Common; caps at
T3 by design — comfort has a ceiling and the ceiling is the point (luxury
beyond it lives in The Reach, priced as pride). Oomo's tree. Rebrand: name
each tier band in-fiction (campfire / craft / powered living / luxury).

3. **The Refinery** — *what sand and wreck become.* Common; the industrial
spine that feeds everything and brags about none of it. Pollution tech
(toxifier line) lives here as honest industry, kept per tonight's triage.

4. **The Workshop** — *making and mending, the Rekko/Ozzik frontier.* Common.
This is where restore-vs-transcend must be VISIBLE (principles §2.2): repair
rows Rekko-tagged pride-neutral; build-new-beyond-spec rows carry the Ozzik
drip. WreckedMachines is its crown content (D5).

5. **Powder & Slug** — *kills by mass; the Watch's tree.* Common. Now caps
with real ordnance (tonight's spread). Sh'kaar's plainest feeding ground —
the tab intro should say so ("every battle wakes him hungrier").

6. **Blasterworks** — *kills by heat; the spine is a story.* Common, with the
KotOR spine (mini→hvy→blasters→plasma) as its one mandated chain
(`chains_ruled`). Rebrand: the spine's four steps get campaign names — it is
the clan RE-DERIVING a dead industry from salvage, tier by tier.
**FLAME IS OUT (owner ruling, 2026-09-04): flame weapons do not belong here
even though they kill by heat.** Small flame (the T0 'incendiary weapons'
row — flamebow, incendiary launcher, incendiary shells/grenades) becomes
**commonly available technology, used by all to hold wildlife at bay** —
re-homed to Jawa Scavenging's floor (fire is the oldest tool in the floor
tree). **BIG flame weapons — flamethrowers and heavy projectors — join the
Junker unlock** (tree 14). Deck amendment: this is an owner amendment to
his own frozen deck, applied at F2 (the row move + the per-unlock split of
flamethrower recipes out of 'trench warfare'/'defence columns' into Junker
rows), recorded here as the ruling of record.

7. **The Strange Schools** — *kills by stranger physics — and now, by
canon.* Thin (7 rows) on purpose until the sonic expansion lands; C1 gives
the school its meaning: sonic is the Hive's own resonance craft — a
hive-mind's native engineering, stridulation scaled to weaponry — ion is the
Jawa's own mercy-physics (disable-and-take; `05_the_clan` weapon doctrine),
vibro/relic/saber are recovered strangeness. Gate mix: common + faction
(Hive sonic). *(door-music removed per C1's ruling.)*

8. **The Shell** — *not dying, as doctrine.* Common; the maker-doctrine tree.
Warcasket content interfaces the Junker Yards (their signature stays theirs).

9. **The Waking Mind** — *minds you make and minds you bind.* Common-to-
ship-only ladder: the RimAI chain climbs INTO the ship's own territory, and
its top (per tonight's weld candidates) brushes the Rites. THIN (10 rows,
MEASURED) — see §G6 for keep-vs-fold; recommendation: **keep**, because its
identity ("the Ohm/Oomo war made legible" — principles §2.3 sited the droid
argument here-adjacent) is worth a thin tab, and Droidworks' research rows
will land here when the port wave activates.

10. **THE SHIP** — *the Utinni herself; research as archaeology of your own
home.* Ship-only/memory_core gated at the top; explicitly non-linear (owner:
"choices in this challenging, expensive tech grind"). Antiquities feeds it
twice: techprint radiation (§2.1) and the ship-design trio's memory reveals.
Rebrand: every row's description written as the Narrator half-remembering.

11. **The Reach** — *the trap, and it should look like one.* Common access,
brutal cost, Ozzik-weighted to the teeth; the tab intro IS the warning label.
Thin now (8 rows) because Anomaly died — correct: the campaign's flesh/gene
temptation moved to the Ascendant Ladder (boon-gated), so The Reach is the
SELF-SERVE half of temptation. The two tabs are a designed pair (see 15).

12. **Antiquities** — *the tree you dig up; the world-unlock meter.* NEW,
17th. Gate: world-held (G5). Five stages; the reversal staged through it
(B3); the deck's next regeneration adds the slide.

13. **The Rites** — *what the ship does with what she remembers.* Ship-only;
revealed by Antiquities stages (the weld, ruled). Its five rows are LITURGY,
not technology — the rebrand should make them the only tab whose rows have no
material unlocks listed, only the Narrator's line for each.

14. **The Junker Yards** — *everything warcasket; loot-and-quest boons from a
faction that never trades.* Faction-held (Junkers), the first fully
boon-gated tree alongside gravtech.

15. **The Ascendant Ladder** — *the flesh ladder, rented from the wrong
children.* Faction-held (Helix boons). Its identity sharpened by B1: every
boon is the Helix showing off exactly the craft the Doctrine died refusing to
write down — the tab where the player pays forged heirs for real power. The
Reach's mirror; the pair should be visually adjacent in the tab bar.

16. **The Foundry Hive** — *hivetech and resonance craft, bought from the
cast-off cultists.* Faction-held (Hive, who trade); their desperation is the
economy — they pay well because almost nobody else will deal with them, and
the Alliance arc (C1) can deepen the relationship into a protected base,
briefly. Sonic capstone stays its T4 prize.

17. **The Unbolting** — *building droids at all — a liberation rite paid one
freed droid at a time.* Faction-held (Enclaves); tonight's ladder (workers →
civilians → military → legends) now reads as the Enclaves' trust-curriculum.
C2 makes them fellow readers; the heist arc (09_arcs §6) remains the
alternative, thief's route in.

**The cross-tree grammar — one gate economy.** The four ruled access classes
(`tech_gating_ruled`) absorb everything new without a fifth concept if G5
rules "world-held = techprints held by the planet": common (1–11 mostly) /
faction-held as BOONS (14–17 + Rust-Cathedral gravtech: quest/ritual grants,
not shelf stock — TECHPRINT_FACTION_GATING_1's blocked question gets its
answer as a side effect: the tech-aligned factions ARE trees 14–17 plus the
Cathedral, mapping below) / jawa-special (Scavenger's floor, marked at start)
/ ship-only (SHIP top, Rites, radiated prints). **Faction→domain mapping
(unblocks TECHPRINT_FACTION_GATING_1, needs G-ratification):** Junkers→
warcasket · Helix→gene/flesh · Hive→sonic/hivetech · Enclaves→droid
construction · Rust Cathedral→personal gravtech (already ruled) · the
world/Antiquities→the canon · the Utinni→her own body. **Tier pacing as one
curve:** T0 wide (every tree's floor cheap and immediate), T1–T2 the working
game, T3 a committed push, T4 a campaign statement — with the owner's
Scavenger taper as the reference silhouette and each tree's deviation from it
a deliberate, stated choice (SHIP/Reach top-heavy; Hearth bottom-capped).
**Rebrand deliverable:** a one-screen "story of research" text (the tab-bar
read in order IS the campaign's moral geography), 17 tab intros, and
per-tree description registers as above — all data, all in the manifest
layer, all shippable with the C# pass.

**Renames and merges (licensed by ruling ①; placements stay frozen; cost =
one deck-slide relabel + one manifest tab-string pass each):**
- **THE SHIP → "The Utinni."** The tab named after her. The all-caps label
  was scaffolding; the ship has a name and the research screen should say it.
  (Strongest rename on the board.)
- **Scavenger → "Jawa Scavenging"** — the owner's own phrase for it during
  the deck pass; adopting his usage costs nothing and reads warmer.
- **The Waking Mind → merge candidate** (G6 unchanged): if kept, rename to
  **"The Waking Mind"** as-is (the name is good; the tab is just thin).
- **Powder & Slug, Blasterworks, The Strange Schools, The Shell, The Hearth,
  The Refinery, The Workshop, The Reach, The Rites, Antiquities** — keep;
  the names already carry their registers.
- **No merges recommended beyond G6.** The four locked faction trees must
  stay separate — each IS a faction relationship — and the thin ones
  (Strange Schools, Reach) have ruled growth incoming (sonic expansion;
  Ladder mirror).

---

## F. The sequenced program

| # | slice | contents | unblocks / feeds |
|---|---|---|---|
| F1 | **Canon catch-up commit** | canon.yml: `research_tree.trees_ruled` (16+1 roster), `antiquities_ruled`, B-item expansions as ruled lines; reconciled_lore: 03/04/05/06/09 gain Antiquities-aware paragraphs (B1–B4, C1–C3); narrator corpus gains `the_knowing.md` (C4) | every later slice cites it |
| F2 | **Manifest schema v2** | columns: access class + holder, theology tags (god-reaction rows, D2), antiquity stage-gates, hidden-reveal channel; Rites+Antiquities rows enter with fates | E's grammar becomes data |
| F3 | **The C# manifest pass spike** | the ruled option-B loader: log-loudly field rewrite + tab defs + hidden prereqs; G1 decides ResearchRetag's fate | tab restructure; theology; gates |
| F4 | **Antiquities slices 1–2** (tree, items, reading loop, fragment corpus with stage-gated registers per B3) | unblock `ANTIQUITIES_TREE_BUILD_1` after this plan is ruled | the world-unlock meter goes live |
| F5 | **Satiation data + Knowing letters** | D2's reaction table; integration letters; Reign-Modes fold (§I.2) — integrations feed the same escalation ladder | the gods react |
| F6 | **Gating build** | boon-grant mechanism (quest/ritual reward shape) per the E mapping | closes `TECHPRINT_FACTION_GATING_1` |
| F7 | **Bases design pass** | D3 + C5, with ownership fabric | the seed doc graduates |
| F8 | **Empire arc + Recovery Raid** | antiquities §7/§8.1 | late game |
| F9 | **Unblock sweep** | rule G8–G10 (below) and release their items | queue hygiene |

---

## H. Queue items blocked on design (owner's mid-flight addition)

The full sweep (queues + items, MEASURED tonight). Items blocked on
*engineering or evidence* are listed for completeness but need no ruling.

| item | what it actually waits on |
|---|---|
| `ANTIQUITIES_TREE_BUILD_1` | this plan being ruled (owner: "do not build yet") — released by F4 |
| `RESEARCH_TREE_NORMALIZATION_1` | the owner's manifest review-sheet pass (its criteria §3) — F2/F3 change what he'd review; sequence his pass AFTER F2 |
| `TECHPRINT_FACTION_GATING_1` | the faction→tech-domain mapping — **answered by §E's grammar if ratified** (G5 + the mapping) |
| `FLUID_CANAL_MECHANIC_1` | reservoir refill shape: steady drip vs periodic re-flood → **G8** |
| `SHIELD_MODS_LEVERAGE_1` | building-scale shield foundation (no VEF hook into Odyssey's gravship slot; speed-curve canon conflict verified) → **G9** |
| `INHABITED_SETTLEMENT_MAPPARENT_GAP_1` | scope call: rebase `WorldObject_Inhabited` vs only the Settlement subclass (save-compat stakes) → **G10** |
| `FLUID_CANAL_FLOOD_LIVE_CHECK_1` | FOUNDRY's debug-surface item (mechanical, not design) |
| `INHABITED_TILEMUTATOR_NO_ENTRY_1` | bridge + game-down window (mechanical) |
| `HELIX_TELLUROX_SHELL_LOAD_CRASH_1` | reproduction evidence (mechanical) |
| `DROID_TILES_SOURED_TERRAIN_1` | Droidworks Phase 3 (sequencing) |
| proposals suite | **not blocked** — ruled 2026-09-02; residue is execution + v1-pending-explanation rows |

---

## I. The fourteen proposals, absorbed (ruling ③) — keep / fold / kill

The suite's row-level sitting is complete (2026-09-02, 124 rows, decisions
frozen). This is the DOC-level reintegration call: does each design fold into
the new canon shape. Recommendations; he rules at plan review.

| # | proposal | rec | why, in one breath |
|---|---|---|---|
| 1 | fire_ecology | **KEEP** | v1 slice already green-lit and live; the Reap theology is Tribes canon; homes cleanly in Scavenging/Refinery trees |
| 2 | god_modes (Reign-Modes) | **KEEP + FOLD into F5** | same escalation family as the Knowing integrations — Antiquities integrations should count toward mode triggers; one satiation ladder, not two |
| 3 | high_cuisine | **KEEP, v2-parked** | its "meals are statements" thesis becomes The Hearth's rebrand register now; the content waits |
| 4 | llm_driven_mods (Oracle cast) | **KEEP** | infrastructure green-lit; the Knowing letters are its pre-authored v1 face; the urn-reading voice is a natural v2 Oracle consumer |
| 5 | ludicrous_livestock | **KEEP** | starter trio green-lit; no canon friction |
| 6 | propane_gas | **KEEP** | six-v1/two-cut already ruled; Refinery home; nightside condenser welds Junker fuel canon |
| 7 | sarlacc | **KEEP + REWELD per B9** | under ruling ② it is a war-era living engine that forgot its side — the proposal's ancient-intelligence layer becomes that exactly; urns depict it (a corpus fragment or two) |
| 8 | ship_shields | **FOLD into G9** | environmental-gating premise is right and stays; its foundation question and SHIELD_MODS_LEVERAGE_1's are ONE decision now |
| 9 | skyhook → Repulsor Spires | **KEEP** | redesign + name already ruled; NEW weld: the Cathedral-overhead spire joins the bases/Empire geography (a cargo eye above the sanctum) |
| 10 | tar_pits | **KEEP** | all-v1 ruled; Pyrelands receipt |
| 11 | underground_caverns | **KEEP + WELD** | cavern mouths become CARTOGRAPHY reveals; stele #10's road-by-touch arrives underground — the tree and the dungeon vocabulary meet |
| 12 | water_economy | **KEEP** | the central dilemma; C5's Deepwater cistern-vault base grounds in it |
| 13 | weather_suite | **KEEP** | slice green-lit; sky-as-terrain is world canon |
| 14 | sw_mod_concepts_triage | **KEEP as reference** | administrative triage, nothing to fold |

**Kills: none.** The suite survived reintegration intact — the sitting's
row-level cuts already did the killing; what remained is load-bearing.

---

## G. Decision points — every genuinely-owner call, trade-offs spelled out

1. ~~Normalization mechanism seam~~ **RULED (owner, 2026-09-04, card): (b)
ALL-C#.** The C# manifest pass is the one mechanism; ResearchRetag stays
live only until the pass proves parity, then retires, dated. F3 executes.
2. ~~The Helix's forged ancestry (B1)~~ **RULED (owner, 2026-09-04, card) —
forged ancestry ADOPTED, and the tragedy kept too, braided.** His expansion,
canon now: some Rakata genuinely adapted by merging with other races and
their line persists in the Helix — **cast-off, denied, distant
grandchildren** — but the ancestors no longer respect or value what they
became. Rejection is the Helix's origin wound: denied by their claimed
family, they turned to studying the very Assailants that destroyed their
ancestors. The line, his verbatim, a set-piece: *"If you will not share your
wisdom and power, then I will learn from what destroyed you"* — "said in no
uncertain terms, and the outrage and disgust from the Rakata radiated
powerfully." **Sequenced AFTER the Reclamation** (G4's event): the
Rakata-Helix alliance fails, the Rakata's mercilessness and untrustworthy
alliances are revealed, and THEN the Helix's true heart shows — "shades of
grey and black everywhere, bleak morality, and hurt emotions turned to the
dark side in righteous indignation at rejection and denial." The forged
splice (B1) and the real thread coexist: the Helix forged MORE ancestry
than they have, precisely because the little they have was refused.
3. ~~Stage the reversal into Antiquities (B3)~~ **RULED (owner, 2026-09-04,
card, and his answer improves the design): stage it in — but the darkness is
NOT separate fragments.** His mechanism, near-verbatim: aggressive urns may
appear early, sparingly — that is the foreshadowing. Best form: *"Sympathetic
Urn interpretation is the easy one, the naive one... but as the players grow
more nuanced, they begin to see the inherent hostility in the deeper, more
fractal layers. 'The stars we lost' are found to later include 'the
casualties inflicted and resources spent subduing the population' encoded in
that same map."* ⇒ **the same urns re-read darker**: every fragment carries
a naive reading and a fluent reading one fractal layer down; stage progress
re-opens already-catalogued pieces (the re-inspection hook in antiquities
§4.1 becomes the delivery mechanism). minStage gates the FLUENT layer, not
the object. The corpus authoring rule: write the grief first, hide the
ledger inside it.
4. ~~The Call-Out settles the ship-claim (B4)~~ **RULED (owner, 2026-09-04,
card): BOTH.** The Call-Out *seems* to settle the claim — then, late game,
one concentrated event: **every ancient the player ever woke unites to take
the Utinni back, in local collaboration with the Helix, who turn hostile.**
Surviving the Reclamation makes the ancients **permanently neutral —
dominated**, unwilling to anger the clan further. (The Helix's forged-heir
lore gets its payoff: the real heirs and the fake ones, allied at last, and
both beaten. This event joins F8's late-game slate; the Helix hostility
switch needs its own care — it ends the Ascendant Ladder boon economy, which
is a real price the player should see coming.)
5. ~~Antiquities' gate class~~ **RULED (owner, 2026-09-04, card): class ②
faction-held, and the holder is THE RAKATA THEMSELVES** — not "the planet."
The dead are a faction; urns are their techprints. And a lore corollary from
the same answer: **the Rust Cathedral would belong to this same
Rakata-holder, except for their love of the Droids and their historical
evolution through degradation — so they remain "Rust Cathedral / Droids
together"**, a separate holder. (The E-mapping stands with holder names:
Rakata→the canon; Rust Cathedral/Droids→personal gravtech.)
6. ~~The Waking Mind~~ **RULED (owner, 2026-09-04, card, after the deep
dive — design/Jawa/waking_mind_ai_deep_dive.md): MERGE + TENANCY THREAD.**
The Waking Mind folds into **The Unbolting as "minds you make"** — droid
bodies and large AI systems (ships, settlements, orbital stations) in one
moral ladder, mixed access classes framed as the feature (some minds are
built, some are freed). PLUS a 3-row **"Tenancy" thread** re-described in
The Utinni's tab (description-only, no row moves): persona cores as houses
for minds, the Rakatan tenancy architecture — two tabs telling one argument
from both ends. Tab bar goes to 16.
7. ~~The Moot as urn-finders (C3)~~ **RULED (owner, 2026-09-04, card):
ADOPTED, and more.** Early game the Moot is SHOCKED at the Utinni and
publicly ambivalent — his voice: *"Look, you're kin, but WTF are you doing
in that huge ship attracting Empire and Hutt hatred?! Stay away please...
unless it's safe right now?"* — and then **secretly trades with the ship
anyway**: kinship among the Jawa IS respected and protected, so long as it
doesn't cost them publicly and bring ruin down on them. "Cute, touching,
and irritating, just like the Jawa." Design consequence: Moot urn-trade
arrives through covert/irregular channels early (night caravans, dead-drop
sales, deniable intermediaries), normalizing only as the clan's standing
grows.
8. ~~Fluid canal refill~~ **RULED (owner, 2026-09-04, card): BOTH.** A
steady drip baseline (the reservoir breathes) AND periodic re-flood events
(water arriving as an occasion). FLUID_CANAL_MECHANIC_1 unblocked with both
mechanisms in scope; the drip carries the simulation, the flood carries the
drama.
9. ~~Shield foundation~~ **RULED (owner, 2026-09-04, card): bespoke
building-scale comp, NOW.** The full fantasy owned immediately; the new C#
system's maintenance cost accepted. SHIELD_MODS_LEVERAGE_1 unblocked; the
ship_shields proposal's environmental gating rides it.
10. ~~Inhabited MapParent scope~~ **RULED (owner, 2026-09-04, card): REBASE
the class.** One architecture for every inhabited world-object; save-compat
exposure accepted (map state is disposable debug until the campaign starts —
the cheap window for exactly this kind of rebase is open).

11.–13. ~~Per-area balance approvals~~ **RULED (owner, 2026-09-04, card):
ALL THREE LETTERS APPROVED** — Armoury (re-price signature weapons against
the one-curve pacing), Xenotype (a Made-lineage tell in the gene layer for
the forged-heir lore), Ideoligion (exactly one reading-the-canon
ritual/precept for the Urn Station). Each still ships as a staged,
reviewable diff — approval here is license to DRAFT the letter, his review
of each diff remains the gate on deployment.
14. ~~Tree renames~~ **RULED (owner, 2026-09-04, card): BOTH.** THE SHIP →
**"The Utinni"**; Scavenger → **"Jawa Scavenging"**. One deck relabel + one
manifest tab-string pass, rides F2/F3.

---

*Written by the reintegration pass, 2026-09-04. Every §G number is a card;
free-text always overrides.*
