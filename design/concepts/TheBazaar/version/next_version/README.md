# TheBazaar: next version (after the current build)

Divergent work: anything that extends the current vision of TheBazaar. Each entry is a pre-written ticket with its acceptance test, who proposed it, when, and why it was not taken now. **Protected: append-only for agents; removing an entry is his call.** No version opens from this file: his review of the scope comes first.

## BAZAAR_STOLEN_GOODS_PROPERTY_1: stolen goods as a trade mechanic, with RimProperty, the registry scanner and the transponder reader (moved from the ledger 2026-11-27)
- **Title (ledger):** "Stolen goods as a trade mechanic: RimProperty integration, the scanner registry, and the transponder reader".
- **Filed:** OWNER, 2026-09-20T14:08:00Z, kind design, for BENCH. His words on the file event: "The stolen goods angle is brilliant and now must be included as integration with the property mod."
- **Target v2** by his card of 2026-10-20 ("Bazaar trade window and in-game LLM voices → Both to v2").
- **Sweep:** home `mod:TheBazaar`, group `trade-window` (2026-11-24).
- **What is built:** none of the mechanic. TheBazaar has code (`src/RimMandrake/TheBazaar/`, the droid modules in `Defs/Modules/RM_BazaarModules.xml`, `RM_ManifestDecoder` among them); RimProperty exists (`src/RimMandrake/RimProperty/`). No stolen-goods ownership model, inkling, discount or transponder scanner exists.
- **Watch out:** the raid and goodwill consequence is faction work. It waits for his word that faction work starts (CLAUDE.md §No faction work starts until the owner says so). The rest (ownership, inkling, discount, scanners) is not faction work.
- **Acceptance test:** none, a design pass that he rules comes first (the ticket's own verify section).
- **Moved whole from the ledger 2026-11-27** (Conductor call on the doubtful tickets of `design/pre_design_concepts/moved_2026-11-26.md`). The other events were the reassignments of the retired FOUNDRY seat and a needs triage. The prose file follows, verbatim, headings demoted.

### BAZAAR_STOLEN_GOODS_PROPERTY_1 — stolen goods as a trade mechanic

Filed by BENCH, 2026-09-20, in the bench sitting that reworked The Bazaar's three
artifacts into protocol-droid modules. Parent design:
`design/RimMandrake/bazaar_trade_window_design.md` §4. The owner called this
*"worth its own awesome design pass to expand"* — so this item is RULED IN
PRINCIPLE and owes a full design pass before any build.

#### spec

Buying goods someone else still owns becomes a real decision with real
consequences, integrated with the property mod (RimProperty).

**The owner's rulings, 2026-09-20, verbatim:**

- *"The stolen goods angle is brilliant and now must be included as integration
  with the property mod."*
- *"Without a scanner the social skill will give you some inkling that something
  is stolen, proportional to how distinct the item is."*
- *"Cheaper but may gain the wrath of the owner or even raids."*
- *"The scanner is a registry of known lost and stolen goods."*
- *"A different scanner should allow you to recognize the goods on a new trader
  due to transponders they are radiating when interested as well as
  settlements."*
- *"Protocol droids know how to 'speak' the language of trade droids (how Star
  Wars seems to handle databases and data formats)."*
- *"Knowing property is from the fall would actually help avoid stolen goods."*

**What that settles:**

1. **Stolen goods are cheaper**, and the discount is the bait.
2. **Consequences scale to being caught holding them** — the owner's hostility,
   up to and including raids.
3. **There is an ungated read.** Social skill alone gives an *inkling*, and its
   strength is **proportional to how distinct the item is** — a unique artifact
   is obviously someone's; a stack of steel is not.
4. **`RM_ManifestDecoder` is the registry module** — a registry of known lost
   and stolen goods. It turns the inkling into a fact.
5. **A SECOND, distinct scanner module reads transponders** that goods radiate,
   working on **both traders and settlements** — it identifies goods on a trader
   you have never met, and on a settlement you are looking at.
6. **Fall-salvage provenance reads as SAFE.** Knowing a thing came off the fall
   is what lets you buy it without risk — which makes provenance protective,
   not merely decorative.
7. **In-fiction, the droid is the reader** because protocol droids speak the
   language of trade droids; this is how Star Wars handles databases and data
   formats.

#### verify

The design pass produces: the ownership model (who owns what, and how the game
knows), the distinctness metric behind the Social inkling, the discount curve,
the detection-and-consequence chain from purchase to raid, and the two modules'
exact division of labour. Nothing is built until that pass is ruled.

#### Watch out

- 🔴 **The player did not fall from space** (owner, 2026-09-20). Nothing here may
  assume the player character arrived by the fall or owns a wreck from it. The
  fall's wrecks are someone else's — which is the entire reason fall-salvage
  provenance is a *question* worth scanning for.
- RimProperty (`mandrake.rm.property`) is the integration target. Read what it
  actually models before designing against it; do not assume it already has an
  ownership concept this can hang off.
- The Bazaar's price engine is **read-side only** by ruling — a stolen-goods
  discount must not become a global MarketValue hook, which is the specific
  thing Vanilla Trading Expanded was rejected for.
- Raids as a consequence touch faction goodwill and the storyteller; a mechanic
  that can summon raids off a purchase needs a Mod Settings switch like every
  other major mechanic.

