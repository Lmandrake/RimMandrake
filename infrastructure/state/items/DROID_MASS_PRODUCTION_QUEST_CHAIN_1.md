# DROID_MASS_PRODUCTION_QUEST_CHAIN_1 — the tech one faction has and cannot use, and another needs and cannot get

## the ruling

Owner, at the bench 2026-09-26, typed — asked which faction mass-produces battle
droids, he rejected the question and ruled something better:

> *"NOBODY currently mass produces droids on this planet. And I'm now ruling a cool
> change. The Genosians know HOW To mass produce (the factory tech) and the droids NEED
> it (don't currently have it, are just repairing each other) but want it badly. They
> are all escaped droids. But the Genosians don't currently have the resources or
> capacity to use that tech at their current limited faction level (themselves left
> behind workers from a factory installation, not a full society), so it's latent in
> their databases. This should be the basis of an entire quest chain that could earn
> huge free droid faction reputation."*

⇒ **`TECHPRINT_FACTION_GATING_1`'s Q7 is SUPERSEDED, not answered.** It asked Hive or
Enclaves. The answer is neither, and the gap between them is content.

## the shape

| | |
|---|---|
| **Geonosian Foundry Hive** | Knows **how**. The factory tech sits **latent in their databases**. They are *left-behind workers from a factory installation, not a full society* — so they have neither the resources nor the capacity to use what they know. |
| **Free Droid Enclaves** | **Need it badly.** They are all **escaped** droids and today they only **repair each other**. No production, no replacement, no growth. |
| **The player** | The only party who can connect the two. |
| **The reward** | **Huge Free Droid faction reputation** — his words. Not a techprint drop; a relationship. |

🔑 **The dramatic engine is that neither faction can solve this alone, and they are
already formally allied** (Hive ↔ Enclaves went to *"FORMALLY ALLIED, with trade"* on
2026-08-17, per `faction_roster_v2.md`'s relations matrix — *"both fled the same
collapsed company site… the hive has no interest in enslaving droids"*). So the obstacle
is capacity and will, never hostility. That is a rarer and better quest than a heist.

⚠️ **A droid faction that cannot reproduce is on a clock.** Every Enclave droid lost is
lost permanently until this chain completes. That is the pressure the chain should feel
like it is relieving — worth building into the letters even if it is not simulated.

## what is NOT ruled — design work this item owes

- The chain's beats, length and failure modes. Nothing about the structure is ruled.
- Whether completing it actually creates a **working production line** in the world (a
  buildable, a settlement change, a new pawnkind source) or ends at reputation and
  fiction. His words name reputation as the reward; he did not say the factory runs.
- Whether the player can betray it — sell the databases to the Empire, or keep them.
- What the Hive wants in exchange. They are a hive under an immobile queen; "resources
  and capacity" is the stated gap, so the ask is probably material and large.

## before designing — read these, do not re-invent
🔑 This project keeps having already built the thing.
- `design/Jawa/worldbuilding/faction_roster_v2.md` — both factions' dossiers and the
  relations matrix; the Hive's *"## Technology and economy"* names droid production,
  sonic weapons and deep drilling.
- `design/Jawa/worldbuilding/faction_tech_alignment.md` §2 — what each holds.
- `design/RimMandrake/droid_system_spec.md` — the droid tiers and what a droid IS here.
- The existing droid items before inventing a mechanism; search `src/` for what ships.
- `rimworld-quests` skill before writing any `QuestScriptDef` — a quest node tree runs
  once at offer time and most quest bugs are silent.

## criteria
- [ ] Chain designed end to end: beats, the Hive's price, the Enclave payoff, failure modes.
- [ ] Ruled explicitly whether completion changes the WORLD or only the relationship.
- [ ] Every faction fact traced to the roster, not invented — this is an established
      relationship between two authored factions, not a blank page.
- [ ] Owner sitting on the beats before any `QuestScriptDef` is written.

## consequences elsewhere
- `TECHPRINT_FACTION_GATING_1` Q7: mark SUPERSEDED, pointing here. Neither faction gets
  a battle-droid production holding in the manifest.
- `faction_tech_alignment.md` §2: the Hive's droid line becomes *latent, not held*; the
  Enclaves' becomes *repair only*.
