# The Webwork — invented fauna roster (resident cast besides the Ollathrix)

_Owner + BENCH, 2026-09-23 sitting; drafted by a Fable design subagent against the frozen sheet._

**Status: DESIGN PROPOSAL. Nothing authored.**

## READ FIRST — five rows, and the silence is the sixth

This is the **resident cast besides the Ollathrix**, per §0 ruling 5 of the sitting record
(`webwork_owner_and_nest_2026-09-23.md`): *very thin, 4–6 rows — anchor-beetle, egg-mite,
one or two trace prey, one trace flier.* This roster is **5 rows**, every one invented,
every one `RM_` tier (Q11a), and 🔴 **every row carries a WAR or a USE — silence is
doctrine.** The donor's animalDensity 5.4 inverted to low-but-lethal because this
jungle's ordinary wildlife has been *eaten* (sheet §1, §4b); a filler-wildlife row here
is not a gap filled, it is the design broken.

⛔ **Two things are out of scope and must not be folded in:**

| not here | why | who owns it |
|---|---|---|
| **the Ollathrix itself** | the owner species is the sitting record's §1, whole — one race, one kind, no castes | `webwork_owner_and_nest_2026-09-23.md` |
| **the 4 existing wildAnimals rows** | evictions are stopped as a sweep; this is the biome's own sitting, so their dispositions are **PROPOSED in §7** and executed by nobody | the owner, §6 item 7 of the sitting record |

Rows the sitting record already cites by name and which therefore exist here exactly as
cited: **`RM_Quarrok`** is fauna row 1 (the anchor-beetle — §1a's consumer race, §3b's
herded corridor-cutter) and **`RM_Vennick`** is fauna row 2 (the egg-mite — §3a's
mite-trail). ⚠️ Naming follows the sibling rosters' register — one planet, one language —
and ⛔ no name here collides with the Fever Wood's 29, the Greentide's 22, the flora
roster's 16, or any shipped def (Appendix, MEASURED this pass).

🔑 **Per the standing rule: if it flies in the fiction, it flies in the game.** The trace
flier takes real flight — `MaxFlightTime`/`FlightCooldown` plus the race flags, Core in
1.6, a **stat, not a bool**. The flight animation is a separate whole-body flip-book and
⛔ never blocks flight.

---

## At a glance

| the two wars (sheet §4b) | the trace prey | the trace flier |
|---|---|---|
| **quarrok** — chews the anchors, cuts the blind corridor | **skennet** — the stock in the ledger | **sivvern** — skims the mites off the high lines |
| **vennick** — eats the eggs, leads you to the nest | **cravvet** — cracks the bones the owner leaves | |

---

## 1. The rulings this roster serves

| ruling | source | what the roster owes it |
|---|---|---|
| **Resident cast is very thin, 4–6 rows; every row a war or a use** | §0 ruling 5 (decision taken by question card, 2026-09-23) | 5 rows, no filler. The near-emptiness IS the design (roster JSON notes) |
| **The three wars are why the Webwork has not won** | sheet §4b | rows 1 and 2 are two of the three wars (the third — themselves — is the owner's own §1) |
| **The mites can lead you there** | sheet §8; sitting record §3a | `RM_Vennick`'s trail is the living treasure map; its JobGiver is owed (§5 of the sitting record) |
| **Beetle-cut corridors are blind** | kit §5 via sitting record §3b | `RM_Quarrok` is the consumer race for the shipped `RM_JobGiver_ChewAnchors` + `RM_ChewableExtension` |
| **Few will enter — a thin prey trickle keeps the hunts visible** | roster JSON, trace-prey band law | rows 3 and 4: something for the burst to land on, in view of the player |
| **This is a plantation, and every living thing is stock in the ledger** | sheet §3 | the prey rows are *kept* animals, not an ecosystem — one is the crop, one is the cleanup |
| **One animal, one biome** | owner ruling 2026-09-21 (CLAUDE.md) | every row is Webwork-only, one home, no exceptions claimed — the flier lairs here and does not migrate |
| **If it flies in the fiction, it flies in the game** | owner standing rule 2026-09-19 | `RM_Sivvern` gets `MaxFlightTime` > 0, not wings drawn on |
| **No tamed Wyyyschokk; no truce; no vanilla-Earth fauna** | sheet §6 bans 1–3 | nothing here tames the owner, parleys with it, or is Earth-nameable |

## Rows — five residents, two of them at war

### 2. The anchor war — `RM_Quarrok` (row 1)

| field | value |
|---|---|
| defName / label | `RM_Quarrok` / quarrok |
| silhouette FORM | **broad low-slung beetle, mandibles wider than its head, always facing a line** |
| look, one line | A great slab-backed jungle beetle, dull bronze-black under a dusting of silk lint, jaws like shears — unhurried, unbothered, and always at work on an anchor. |
| war / use | 🔴 **WAR — the anchor war** (sheet §4b): it hates the spiders instinctively and chews through web anchors, slowly undoing the networks. **USE — the corridor-cutter**: it is *herdable* — lure quarrok along a route and they cut a safe corridor; beetle-cut anchors deregister SenseWeb cells, so a quarrok corridor is a **blind** corridor, the only silent approach to a nest (sitting record §3b route 3). |
| body size class | **large insect** — ❓ bodySize ~1.4; slow (the donor interim body's spd 3.1 non-predator read is the register to keep); heavily armoured about the head |
| one-home note | Webwork only. Its whole biology is web-anchors; there is nothing for it anywhere else, and no in-game mechanism moves it. |
| mechanism | ✅ `RM_JobGiver_ChewAnchors` + `RM_ChewableExtension` are **shipped with no consumer race** (sitting record §1a, MEASURED) — this row is the consumer. Herding rides the living-tool pattern (lure, not tame commands). |
| replaces | the interim `RSW_JewelBeetle` body (disposition §7 row 2) |
| art | **OWED** |

⚠️ **Neutral, unbothered — not a guard animal.** A quarrok never fights an Ollathrix; the
war is infrastructure sabotage, not combat. Making it a battle-pet breaks §4b's register.

### 3. The egg war — `RM_Vennick` (row 2)

| field | value |
|---|---|
| defName / label | `RM_Vennick` / vennick |
| silhouette FORM | **fist-sized dot with legs, in a moving STREAM along a line — the stream is the silhouette** |
| look, one line | A fist-sized silk-runner, pale grey with a bone-white back that catches the gloom, never alone: vennick read as a current, not as animals. |
| war / use | 🔴 **WAR — the egg war** (sheet §4b): it runs the silk to seek out and devour Ollathrix eggs. **USE — the living treasure map**: harmless to a pawn, so a vennick stream is a free, safe guide — it paths along registered SenseWeb cells *toward the nearest clutch* (sitting record §3a; sheet §8: "the mites can lead you there"). |
| body size class | **tiny** — ❓ bodySize ~0.12; quick on silk, poor off it |
| one-home note | Webwork only. It eats one thing, which exists in one biome. |
| mechanism | `RM_JobGiver_RunToEggs` — **owed**, promoted from the kit's deferred list by the sitting record (§3a, §5). Until it exists the def can ship but the treasure map is dead behaviour. |
| art | **OWED** — and the sprite must read at stream density, not as one animal |

🔑 **The two wars are the biome's toolkit.** The quarrok makes corridors, the vennick
finds nests — the player's two instruments against the owner are both *animals used
well*, which is the donor's canonized advice (sheet §7b: USE the spiders — and their
enemies) made concrete.

### 4. The trace prey — `RM_Skennet` and `RM_Cravvet` (rows 3–4)

*"It is eerily silent — most of the animals have been eaten, and few will enter"* (sheet
§1). What remains is not an ecosystem; it is stock in the owner's ledger (sheet §3).

| field | `RM_Skennet` (row 3) | `RM_Cravvet` (row 4) |
|---|---|---|
| label | skennet | cravvet |
| silhouette FORM | **long-legged pale runner, neck low, always mid-stride** | **squat domed sheller, head down, parked on a stain** |
| look, one line | A nervous, bone-pale runner on stilt legs, built for one sprint it will eventually lose. | A knuckle-shaped armoured scuttler, mud-dark, jaws built for cracking what mandibles left. |
| war / use | **USE — the crop, and the visible hunt.** It gleans fellome pods along the web-lines (flora §5 row 14): the plantation's livestock, sown and kept by the owner. A thin trickle of skennet is what keeps the hunts visible — the burst has a target the player can watch. Huntable small game, at the usual price of being on the silk when it happens. | **USE — the kill-site tell, and the cleanup.** It follows kills and cracks the bones and broken armour the Ollathrix leaves (sheet §4: devoured in ripped-off portions — someone tidies). Cravvet parked on a stain means a fresh kill site: readable danger, plus chitin and meat for whoever shoots it. |
| war? | none — it is prey, and that is its job | none — a tolerated scavenger; the owner's leavings feed it, so the owner ignores it |
| body size class | **small** — ❓ bodySize ~0.35, fast | **small-medium** — ❓ bodySize ~0.5, slow, hard-shelled |
| one-home note | Webwork only — its food grows on web-lines | Webwork only — its food is what an Ollathrix leaves |
| mechanism | none; grazing biased to web-line cells is placement, not C# | none; carrion preference is vanilla behaviour |
| art | **OWED** | **OWED** |

⛔ **Two is the ceiling.** Ruling 5 allows "one or two trace prey"; two are taken, for the
two halves of a hunt — the chase and the aftermath. A third prey row is filler by
definition.

### 5. The trace flier — `RM_Sivvern` (row 5)

| field | value |
|---|---|
| defName / label | `RM_Sivvern` / sivvern |
| silhouette FORM | **narrow swept crescent, membranous, low over the canopy — never perched in the open** |
| look, one line | A slender dusk-flier on taut grey membranes, silent as everything here, tracing the high lines and dipping to pick vennick off the silk. |
| war / use | **USE — the third party in the egg war, and an aerial tell.** It eats egg-mites, which makes it the nest's unwitting ally — and makes sivvern circling low a sign of heavy mite traffic beneath, which is itself a sign of eggs (a second, longer-range read on the treasure map). Hunting one is possible; reading one is better. |
| body size class | **small** — ❓ bodySize ~0.3 |
| one-home note | Webwork only. It lairs in the sealed canopy and hunts one prey that exists in one biome; ⛔ no migration mechanism is claimed, so no second home is either (the flier carve-out is narrow and this row does not invoke it). |
| flight | 🔴 **real flight, per the standing rule**: `MaxFlightTime` ❓ ~8, `FlightCooldown` ❓ ~5, `flightSpeedFactor` ❓ ~2.5, `canFlyIntoMap` true, **`canLeaveMapFlying` omitted — it lairs** (the Locust shape, stat-not-bool). Flight animation frames are a separate flip-book, **OWED but never blocking** — with no frames it flies without a wing-beat, which is correct and plainer. |
| mechanism | prey preference for `RM_Vennick`; otherwise vanilla predator behaviour |
| art | **OWED** — grounded set plus, eventually, the directional flip-book |

## 6. Legibility matrix — the acceptance test

Five residents plus the owner; every form must be nameable from a top-down sprite at
display size, and none may blur into the Ollathrix's *too many sharp legs under too large
a shadow*.

| form | row | reads as |
|---|---|---|
| broad low beetle, shear-jaws on a line | quarrok | a demolition crew of one |
| a moving stream of pale dots on silk | vennick | a current — the map, flowing |
| pale stilt-runner, mid-stride | skennet | the thing that gets caught |
| squat dome parked on a stain | cravvet | evidence |
| narrow membranous crescent over the canopy | sivvern | the only thing in the sky |

🔑 **Motion doctrine** (sheet §9: *almost none — churn in the thicket, a mite-stream on a
line, then the burst*): the vennick stream and the sivvern's low pass are two of the
biome's three permitted motions. Neither may become busy ambient wildlife; both are
signals the player reads.

---

## 7. What is replaced — disposition of the 4 existing wildAnimals rows (PROPOSED)

The live `RUT_Webwork` cast is 4 wired rows (`rosters/the_webwork.json`; the JSON's other
two fauna entries — the `AA_Feralisk` merge row and `GR_Chickenspider` — are dead or
unwired and already discharged by §0 ruling 2 / §1a of the sitting record, so they are
not dispositioned here). ⛔ **PROPOSED only — evictions are stopped as a sweep; this is
the Webwork's own sitting, so these are the owner's call here and nowhere else (sitting
record §6 item 7). Nothing is executed by this document.**

| live row | band, comm. | disposition (PROPOSED) | why, in one line |
|---|---|---|---|
| `Wyyyschokk` (donor, `mlie.starwarsanimalcollection`) | owner, 0.4 | **CUT from this biome — the owner species becomes `RM_Ollathrix`, with the Wyyyschokk as its Utinni skin patch** | sitting record §0 ruling 1 and §1c: one defName, the campaign layer patches label/description/art over it; the donor def stays in the game but homeless |
| `RSW_JewelBeetle` (ours, ported) | anchor-beetle, 0.3 | **CUT from this biome — superseded by `RM_Quarrok`** | its own JSON law line calls it an *interim body* for the chew-behaviour; the purpose-built consumer race replaces it, and the RSW_ def goes to the homeless reserve unless another sitting seats it |
| `Kreetle` (donor, bare defName — the convention, not a defect) | trace-prey, 0.2 | **CUT from this biome — replaced by `RM_Skennet`/`RM_Cravvet`** | a donor multi-homer standing where invented one-home prey now stands; cutting it here also removes this biome from `DUPLICATE_CANON_DEFNAME_PAIRS_1`'s Kreetle-vs-`RSW_Kreetle` count (sitting record §5) |
| `Shyrack` (donor, multi-homer) | trace-flier, 0.2 | **CUT from this biome — replaced by `RM_Sivvern`** | its flier claim is UNMEASURED (JSON confidence block: the register's flies flag is broken) while the replacement takes real, stat-backed flight; and a cave-mouth rooster was never this canopy's animal |

⚠️ A row cut *here* and alive in another biome is correct, not a leak — a sheet's cut is
scoped to its own biome (owner ruling 2026-09-21).

---

## 8. Canon injection (additive, Utinni layer)

The Utinni layer may add canon beasts on top; the free `RM_` roster above must stand rich
alone (Q11a) — and here "rich" is *thin on purpose*, which makes the injection bar the
highest of any biome:

- **The one injection this biome is built around is not a wildAnimals row at all**: the
  Wyyyschokk arrives as a **skin patch on `RM_Ollathrix`** (sitting record §1c —
  label, plural, description, texPaths, leather label; ⛔ nothing on mechanics). That is
  the whole Star Wars presence the resident cast needs.
- **No canon wildAnimals injection is recommended.** Every candidate must survive the
  eaten-default (sheet §1: the wildlife has been *eaten*) and must not hand the biome a
  second motion, a second sound, or a rival ambusher — the roster JSON's eviction list is
  a catalogue of things that failed exactly those tests. A canon beast that genuinely
  earns a slot would have to be a fourth war, and inventing wars is the owner's, not an
  injection pass's.
- ⚠️ If a candidate is ever proposed, it is verified through the Wookieepedia search API
  (`action=query&list=search&srsearch=`), never a guessed title and never a donor mod's
  defName — a canon claim sourced to a donor def is not sourced at all.

---

## Appendix — collision sweep (MEASURED, this pass)

Python sweep (never a zsh loop), case-insensitive, over all `.md/.xml/.json/.cs/.py/.txt/.csv`
under `design/` and `src/` — 4,581 files scanned. **Sanity probes first**: `korrum` 37
occurrences in 9 files, `stoneback` 162 in 41, `hawkbat` 259 in 48. ✅ The instrument sees.

**Result: all 5 fauna defNames have 0 occurrences outside the three Webwork sitting
docs.** Per-name totals (all inside the sitting docs, expected self-citations):
`quarrok` 15, `vennick` 14 (both pre-cited by the sitting record), `skennet` 7,
`cravvet` 7, `sivvern` 9. The same sweep caught one flora-side collision (*skarrow*,
already a Rot label) — renamed there before commit; see the flora roster's appendix.
