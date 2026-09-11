<!-- status: RULED 2026-09-11 (card sitting, §5) + legends-sitting corrections
     same day (mindstone_arc_legends.md). Propagated to both frozen sheets. -->

# Mechanoid origin canon — the mindstone, the crystal-mind race, and the Cathedral's true children

_Draft under `MECHANOID_ORIGIN_CANON_1`. The owner's charge (2026-09-06,
`biomes/the_lantern_deeps.md` §8, verbatim in intent): a special droid mind made
from the mindstone *"is not really a droid any more — a new race,"* and that
**"explains what the mechanoids and the Rust Cathedral are: a very different
form of AI, not so artificial after all, and the Deeps' crystal minds are their
'wild cousins.'"**_

## 0. What binds this design (quoted, with sources)

- **The Cathedral's mind-nature is ruled and frozen** (`the_rust_cathedral.md`
  §GM, 🧊 `BIOME_FREEZE_FABLE_REVIEW_1`): *"It is a kyber-crystal engineered
  mind (owner, this sitting) — the same nature as the mechanoids' minds, but
  vastly more powerful."* This draft ADDS DETAIL under the freeze rule; it
  changes no ruling.
- **Terramanufacture** (`ASHKARR_WORLD_DEFINITION.md` §3b; Cathedral §GM
  amendment 2026-09-11, `TERRAMANUFACTURE_CANON_1`): the planet's fate was
  *"a tremendous factory… Not terraforming: terramanufacture"*; **the Cathedral
  is the planet-scale power dynamo's remnant**, the mind that was to
  *"manage and coordinate the entire planetary factory and surrounding area."*
- **The factory is already placed** (Cathedral §GM, owner 2026-09-10): *"The
  night-side sentry factory IS the Lantern Deeps' mechanoid production facility
  (`MECHANOID_ORIGIN_CANON_1`) — one factory, not on Cathedral ground, not
  running under its hand today; the Cathedral would like it restarted."* Listed
  in `03_deep_history.md` as one of the Cathedral's *"two unspent reserves."*
- **The droid/mech wall** (`droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` §1.1,
  RULED 2026-09-06): a droid is a HAR humanlike of `RSW_DW_FleshType_Droid`,
  *"never a mech… Shared code: none, keep it none."* And **§0 ruling 3, owner:
  "Mindstone race = a Droidworks chassis with a special head (rides B3)"** —
  B3 already names **`RSW_DW_Head_Mindstone`**. §0 ruling 2: **no rogue droid
  faction, ever** — droids ride other factions' loadouts.
- **Kyber is crafting material only** (`the_lantern_deeps.md` §6.4,
  `FORCE_POWERS_ARE_V2_1`): *"the mindstone's droid race is likewise no Force
  route."*
- **The Oracle's two laws, unchanged** (`RimMandrake/llm_ingame_wiring_spec.md`
  §0): *"Text authority, or menu authority — never free authority"* and *"The
  game is whole with the LLM absent."* Transport is `claude -p` (owner
  2026-09-05), a fact about the machine, not this design.
- **Presence discipline**: `MECH_PRESENCE_ENFORCEMENT_1` closed 2026-09-11
  (XML pieces landed; shrine-guardian gate spun to
  `SHRINE_GUARDIAN_BIOME_GATE_1`); `mechanoid_biome_presence_draft.md` already
  rows both halves of this item: the facility as *"site/dungeon… not a mapgen
  scatter"* and the wild cousins as *"narrative (dialogue, quests), never an
  ambient-spawn axis."* The Empire is reskinned vanilla `Empire` (faction
  consequences in §4 price against it). **No worldgen, in any form.**
- **"Forgotten Sentries" CONFIRMED to exist**: `the_lantern_deeps.md:184` and
  `:223`, and `mechanoid_biome_presence_draft.md:96` — but it collides with the
  Cathedral sheet's frozen naming settlement (**Forgotten Sentinels**) and
  `03_deep_history.md`'s **Forsaken Sentinels**. Card N3.

## 1. The origin story this canon tells (the unifying frame)

The Rakata did not build minds; **they grew them.** Kyber-family crystal is the
one substrate on Ash'karr that thinks — quiet where lanternstone glows —
and Rakatan mind-engineering was the art of seeding, shaping and harnessing
crystal intelligence into housings: small ones for the Sentinels, one vast one
for the Cathedral, engineered to coordinate a planet-factory. That is what
*"a very different form of AI, not so artificial after all"* means mechanically
and in lore: **the mechanoids are not programs in metal; they are grown minds
in armor.** The Deeps' crystal minds — Shard-minds, Chorus, mindstone — are the
same order of being that was never seeded, never shaped, never housed: the
**wild cousins**. The Cathedral's tragedy restates cleanly in this frame: an
engineered crystal mind, cut to a purpose that no longer exists, holding the
wild kin in the same regard a plantation holds a forest.

Register discipline: everything in this section is §GM-tier plot. Player-facing
text gets the mystery, never the mechanism (Cathedral §6.1 stands).

## 2. The mindstone as a findable

- **What it IS in-world**: the third and rarest crystal of the Deeps
  (`the_lantern_deeps.md` §3/§7 — lanternstone glows, kyber is quiet, *"the
  mindstone is aware"*): a naturally sentient crystal, a wild mind that never
  grew a colony. Holding one is holding a person who has never had a body.
- **Where it surfaces**: ONLY inside Lantern Deeps cave maps — mined from rare
  formations deep in a Deep, salvaged from the well-provisioned dead (a prior
  expedition's find, still in its case), or **given** — the wild cousins can
  offer one as payment/trust in the §3 dialogue line. Never on surface maps,
  never in ordinary trader stock (a single scripted quest-trader appearance is
  permissible as a plot beat, priced absurdly). No worldgen: the Deeps are the
  ruled injection layer (≤ −40 °C hosts, persistent, frozen sheet) and the
  formations are authored into those cave maps.
- **Rarity register**: rarer than kyber; a campaign expects to see **a handful,
  not a stack** — each one findable is a potential colonist-equivalent, so
  scarcity is the balance lever. Proposed: one guaranteed plot stone (the
  dialogue line's gift), 0–2 minable/lootable per Deep at the "deepest room"
  tier, weighted so a full campaign yields ~3–5.
- **Item shape**: a `ThingDef` resource (`RUT_Mindstone`, §5 name card N1) with
  no use but the §2b recipe and trade — selling one raises the same Imperial
  heat as kyber (it IS kyber-family; `KYBER_TRADE_PLOT_1`'s law applies), and
  the wild cousins remember mindstone sales (a permanent dialogue-register
  grudge, text-only).

## 2b. The crafting route and the race's representation

**Representation is already ruled and this draft complies**: framework §0
ruling 3 — *a Droidworks chassis with a special head*. Weighing the two options
the item names, for the record:

| option | verdict |
|---|---|
| **Droid side: HAR chassis + `RSW_DW_Head_Mindstone`** | ✅ RULED (framework ruling 3). Buys the whole shop economy for free: reassembly harness, fine parts, module slots, capture verbs, needs tiers. The head carries identity (`CompHeadIdentity`), which is exactly right — the PERSON is the crystal, the body is clothes. |
| Mechanoid class (`FleshTypeDefOf.Mechanoid`) | ⛔ dead on three laws: the droid/mech wall (*"shared code: none"*), force-kill-on-down would make the race uncapturable and unlivable as a colonist, and ruling 2's no-droid-faction grammar has no slot for a player-side mech race without mechanitor baggage. |

- **The route**: mindstone + a droid head casing at the reassembly harness →
  **`RUT_MindstoneMatrix`** — the mindstone REPLACES the personality matrix in
  the brain trio (the one component *"no one on this world can make"*, framework
  ruling 6 — the wild crystal is the one local thing that beats an import).
  Processor and databank are still imported parts: the mind is grown, the
  interface is bought. Fit the finished `RSW_DW_Head_Mindstone` to any chassis.
- **What the tier buys**: SAPIENT format always (framework ruling 4 — full
  needs), stat superiority per B3's *"mindstone head yields the ruled stats"*
  (numbers owed to B3, not this doc), **immunity to wipes and spikes** — you
  cannot memory-wipe a person made of mineral; a wipe/spike attempt fails with
  text, which is the mechanical spine of "not really a droid any more."
- **A new RACE, not a new race def**: in lore it is a race; on the platform it
  is head-carried identity on existing chassis — the body is incidental, which
  is the point. If the owner wants them visually distinct, that is a chassis
  ART variant, not a new `ThingDef_AlienRace`.
- **Tier grammar**: the crystal, matrix recipe, dialogue and site content are
  **RUT_** — they are Ash'karr campaign lore (the Deeps, the Cathedral, the
  Rakata), meaningless in a generic Star Wars scenario. The head item stays
  **`RSW_DW_Head_Mindstone`** as B3 already names it — it is a Droidworks
  platform slot the campaign fills (card N4 flags the seam).
- **No Force route** (Deeps §6.4): the race's intelligence is stats and
  dialogue register, never sensitivity, powers or attunement.
- **🔴 Knowledge scoping (owner, legends sitting 2026-09-11): THE KINDLED HAVE
  NEVER BEEN MADE.** *"They are a totally new concept that has not yet been
  made."* Everything above is DESIGN — the recipe the player can discover —
  not in-world knowledge: no faction knows the route or the race, no rumor
  circulates, and the legends deck (`worldbuilding/mindstone_arc_legends.md`)
  deliberately contains no Kindled entry. The first making is an in-play
  event. What IS observed in-world: droids act strangely or simply stop near
  mindstone and avoid the Deeps at all costs; dead droid chassis work the
  galleries of their own accord ("the Working Dead"); droids that leave exit
  effectively mind-wiped, go rogue, and drift to the neutral factions.

## 3. The wild-cousins dialogue — Oracle/text authority only

The crystal minds **talk**. That is their entire mechanical presence
(`mechanoid_biome_presence_draft.md`: *"never an ambient-spawn axis"*).

- **Both laws hold verbatim**: every wild-cousin communication is display text
  or a selection from a pre-validated menu; every beat ships its prescribed
  fallback text first and the Oracle (`claude -p` transport) only upgrades it.
  No free text ever names a def, spawns a thing or moves a number.
- **The voice**: Shard-mind register (Deeps §4) — through electronics: the
  player's own droids, a dead suit's speakers, a comms console carried into a
  Deep. A mindstone-headed colonist is the premium channel: the cousins speak
  to the player *through their own colonist*, in that pawn's log/letter voice.
- **The content** (owner's charge): they ask for **help and defense against
  "the insane enslaved one"** — the Rust Cathedral — *"which seeks to mine
  them all up and use them in its never-ending hunger."* Design reading:
  this is **their testimony, not narration** — partial, frightened, and in
  tension with the Cathedral's ruled register (card C2). "Enslaved" is their
  word for engineered-to-orders; the player is never handed an arbiter.
- **What the dialogue can DO** (menu authority): offer the gift mindstone;
  mark a Deep location the player already can reach; ask the player to refuse
  the Cathedral's §4 restoration request; grade the player's standing (heat
  with the cousins mirrors mindstone sales and §4 choices). All pre-validated
  event branches with fixed fallbacks.
- **Bans respected**: nothing they say explains the droids' mercy at the
  Cathedral (§6.2), leaks §GM mechanism into ambient text, or offers Force
  anything.

## 4. The production facility as a site

**One factory** (Cathedral §GM 2026-09-10): the night-side sentry factory in a
Lantern Deep. A site/dungeon on the frozen map — hand-placed, bridge-authored,
no worldgen — reached through a Deep's mouth per the ruled map-chain.

- **Working vs slumbering — proposed: BOTH, in sequence** (card C1 carries the
  choice). The reconciling read of *"still working… at a very slow rate — or a
  slumbering one"* against *"not running under its hand today; the Cathedral
  would like it restarted"*: the factory **ticks over autonomously** — a
  trickle of Sentinels on ancient standing orders — feeding the SECRET CACHES
  and the Cathedral's few store vaults and supply lines, which is why the
  Arsenal never ran out (surface Sentinels are NOT replenished; see §5
  legends-sitting refinement) — but it is
  **not under the Cathedral's command**, and its mind-seeding line (the part
  that grows crystal minds for the bodies) is dark. "Restore" means handing the
  Cathedral its factory back, seeding line and all.
- **In play**: the site holds the assembly halls (faction-13 Sentinels at
  vault-perimeter density — perimeter, never manhunt, per the ruled presence
  register), the dark seeding line, well-provisioned dead from prior attempts,
  and the restoration objective: a physical act (power, coolant, a carried
  component) plus a **choice delivered as text/menu** — the Cathedral asks
  through its channels; the wild cousins beg against it through theirs.
- **Restore** — consequences: the Cathedral gains its *"unspent reserve"* —
  gratitude in the only currencies it has (gravtech boons per
  `03_deep_history.md`, standing, missions); **"restore its 'true children'
  and it might no longer love its Free Droids quite so much"** (owner) — the
  FDE's whispered voices go quiet, enclave standing toward the player cools,
  and the pet-droid tenderness in `03_deep_history.md` is priced as the thing
  the player traded away; the wild cousins register it as arming their miner.
  Empire-facing: more Sentinels on the night side is more anomaly for
  Imperial survey — a slow heat tick (the Empire is reskinned vanilla
  `Empire`; consequences ride goodwill/heat, no new faction).
- **Refuse (or sabotage)** — consequences: the cousins' trust line opens fully
  (the gift stone, the §3 aid register); the Cathedral adds it to the ledger
  of things it tolerates and remembers — colder boons, and the Utinni's
  vouching (`03_deep_history.md`) is spent a little further. Not hostility:
  the Cathedral's ruled posture is rationed patience, not raids (§6.3).
- **The Helix shadow** (adjacent per the charge; `INHABITED_CAST_HELIX.md` +
  `TERRAMANUFACTURE_CANON_1`): the Helix's *"attempt to control the old
  technology now has a purpose to fail at"* — a working mind-factory is the
  single greatest prize on the planet for a cult trying to inherit the species
  that drafted planets, and the Cathedral **hates the Helix** (ruled). Hook,
  not build: a Helix expedition sniffing the Deep after any restore is the
  natural follow-on quest seed (`KYBER_TRADE_PLOT_1`-adjacent register).

## 5. 🟢 RULED — the card sitting of 2026-09-11 (all nine cards + the flagged invention)

**Contradiction rulings:**

- **C1+C4 — ADOPTED: the autonomous trickle, enriched.** The factory runs an
  autonomous trickle on the last standing orders — which is also where the
  ages of Sentinel attrition replacement came from; the mindstone-seeding
  line is dark; "restore" means handing it to the Cathedral. Owner-verbatim:
  *"the slow trickle shows that there ARE still automated mining facilities
  working, automated supply lines slowly delivering, automated manufacturing.
  But most was found and destroyed, and only by sleeping most of them
  religiously has it maintained them. To use them is to risk them, so it's
  kept at the most basic level that actually is slowly winding down.
  Especially now that the Empire is so close. There has ALWAYS been someone
  dangerous too close... it doesn't even know if it could ever start to
  spiral up again. Likely not, just slow the decay."* Supersedes the
  working-vs-slumbering open fork in Deeps §8's phrasing; does NOT change the
  Cathedral's "not running under its hand" line — both frozen sheets stand.
- **C2 — ADOPTED: intent, not act.** No active crystal-mind mining today; the
  threat IS the restore. Owner-verbatim: *"the crystal entities have little
  concept of time, so their memory is of the voracious hunger that WAS when
  it was operating and growing. The crystals are one of the most limited
  resources the Cathedral needs to build more of its sentinel (and self).
  Very rare and difficult to get access to."* Both frozen registers stand;
  the cousins' testimony is a timeless memory of the hunger-that-was.
- **C3 — CONFIRMED: testimony register.** "Enslaved" is the wild minds' word
  for engineered-to-purpose; there is no hidden literal enslaver and no canon
  change.
- **C5 — CONFIRMED: head-carried identity, with a ruled taxonomy.**
  Owner-verbatim: *"Droids are parts-based mechanical body + mechanical mind.
  Mechanoids (sentinel) are pseudo-organic inorganic constructs without parts
  fused with a crystal mind. The new creation would be parts-based mechanical
  body + crystal-operating-neural-circuits manually. New life form."* So:
  the mechanoids/Sentinels are ALREADY crystal-mind-fused constructs (this is
  now canon detail on both sheets); the Kindled are the third form. "Race"
  stays lore register; no distinct chassis — body incidental is the point.

**Name rulings:**

- **N1 — KEEP "mindstone."** Def token `RUT_Mindstone`.
- **N2 — the race is THE KINDLED.** Def token `RUT_Kindled`. (Per-speaker
  variant names remain available as flavor; "the Kindled" is the primary.)
- **N3 — "Forgotten Sentinels" is official canon.** Owner-verbatim: *"While
  (1) should be the official canon, all of them should easily map to the same
  thing"* — canon docs and defs say Forgotten Sentinels; "Forgotten Sentries"
  and "Forsaken Sentinels" survive ONLY as in-world speech variants in
  dialogue/flavor text, never in doc voice or def tokens. Doc-voice
  occurrences corrected in this propagation.
- **N4 — ACCEPT the seam.** `RSW_DW_Head_Mindstone` stands as the platform
  slot the campaign fills — with rich lore owed. Owner-verbatim: *"(1) but
  with big, thick lore to explain it richly. Making my own legends entries."*
  The legends entries are an OWNER-authored deliverable, filed as
  `MINDSTONE_LEGENDS_ENTRIES_1`.
- **Wipe/spike immunity (§2b) — RATIFIED.** Wipes and spikes fail with text
  on a mindstone head; the mineral mind cannot be erased. The §2b invention
  is now ruled mechanics.

**Legends-sitting refinements (owner, same day —
`worldbuilding/mindstone_arc_legends.md` §Canon corrections):**

- **C1+C4 surface reading corrected.** The trickle restocks the hidden
  reserve — secret caches (ancient-danger-like), the Cathedral's few store
  vaults and supply lines — NEVER the surface. Surface Sentinels are SPARSE
  (battle-signs and battlements ubiquitous, standing warriors uncommon), are
  units the Cathedral has LOST control of and cannot recall, and are NOT
  replenished: they SELF-REPAIR and slowly devolve — that technology being
  lost is why it looks like replenishment. Surface strays malfunction and
  hide in plain sight; a night-wanderer reads as harmless old junk while
  some are fully operational.
- **The Kindled: never made** (see §2b knowledge scoping) — no lore, no
  rumor; first making is an in-play event.
- **Knowledge gate (hard).** Nobody in-world — the Junkers included — knows
  the Cathedral is alive or wants the crystals; that is late-game lore only.
  The Junkers hold fragments of the Deeps stories; the ancient miner's
  testimony survives as a data entry in the tall tower's computer in the
  forge dungeon (site identifier unresolved — resolve at wiring, do not
  guess) and as a Junkers goodwill unlock. Two sources, owner-ruled.

## Owed on ruling — status after the 2026-09-11 propagation

Amendments landed as detail on the two frozen sheets; doc-voice loser names
corrected (in-world speech variants deliberately retained). Still owed: B3
inherits the ruled stats charge, and `MECHANOID_BIOME_PRESENCE_REVIEW_1` is
fed per the item spec.
