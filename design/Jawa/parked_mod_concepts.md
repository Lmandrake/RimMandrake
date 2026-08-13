# parked_mod_concepts.md — mod ideas worth building later

_Started 2026-08-10. A home for **mechanics we liked but aren't building yet** —
usually because the donor mod is broken, abandoned, or off-theme, but the *idea*
is good enough to reimplement or extend later._

Sits alongside the committed authoring work in `required_mods.md` §6
(JawaIonWeapons, Jawa_Patches) and `design/Jawa/carbonite_trophy_mod.md`. Nothing
here is a commitment — it's a shelf, not a queue.

**Entry format:** what it did · why it fits · what went wrong · what we'd build.

---

## 1. Consequential theft from outsiders — extending RimSteal

**Donor:** RimSteal, WS `3722523355`, packageId `stealmod.author`, v1.0.0.
**Status:** removed from the load order 2026-08-10 (broken — see below). No
GitHub repo, no `<url>` in About.xml; Steam comments are the only contact route.

### What it did (worth preserving verbatim)

A **D&D-style stealing system aimed at non-faction pawns** — visitors, traders,
anyone passing through:

- Right-click a non-faction pawn to attempt a steal.
- **1d20 + proficiency** resolves it. Natural 20 = guaranteed success, natural 1
  = guaranteed failure.
- **Advantage** (roll twice, keep highest) from the *God Thief* trait or from
  invisibility.
- A hidden **Alertness hediff** accumulates on nearby pawns after each theft, so
  repeat thefts in one area get progressively harder.
- A **stealth check runs 5 ticks after** a successful steal — detection is
  deferred, not instant.
- On failure, a dialog offers **Quibble / Threaten / Admit** — a social
  consequence branch rather than a flat penalty.
- Animals delegate the attempt to a nearby human of their faction.

### Why it fits this campaign

This is a *much* better fit for a Jawa scavenger clan than pickpocketing your own
colonists (which is what **Stealing Mod** `3775811814` does, and which we kept).
Stealing from **traders and visitors** is on-theme for hooded scrappers, and the
Quibble/Threaten/Admit branch is exactly the texture the comedy register wants —
a failed theft becoming a negotiation is funnier and more interesting than a
mood debuff.

It also plugs into systems we already have:

- **Faction goodwill** — a caught theft should cost standing with the victim's
  faction. Ties directly to the Hutt-debt and trade-dependency layers.
- **Imperial Heat** — stealing from an Imperial-aligned trader is a natural
  Heat-raising action for the GM layer.
- **The pantheon** — theft is a *doctrinally interesting* act. Mob'Unloo (the
  ledger/balance god) plausibly cares whether a debt was settled or dodged;
  Ishko cares about nerve. The satiation engine already wants exactly this kind
  of morally-legible event to react to.
- **CQF DialogTrees** — the Quibble/Threaten/Admit dialog is structurally a
  DialogTree, which we're already committed to authoring for the arc.

### What went wrong

```
Could not instantiate a GameComponent of type StealMod.Core.DelayedActionComp:
  System.MissingMethodException: Constructor on type
  'StealMod.Core.DelayedActionComp' not found.
  at Verse.Game.FillComponents ()
```

A RimWorld `GameComponent` requires a public constructor taking `(Game game)`.
RimSteal's doesn't have one, so the component never instantiates.

⚠️ **Why that made it dangerous rather than merely broken:** `DelayedActionComp`
is what runs the *deferred stealth check*. With the component dead, that check
plausibly never fires — meaning **successful thefts are never detected**.
Consequence-free stealing is precisely the silent-exploit shape the
anti-exponential pillar exists to catch. Removing it was a balance decision, not
just housekeeping.

### If we build it

Scope is modest — this is a small C# mod, not a framework:

1. **Core roll.** 1d20 + a proficiency stat, advantage/disadvantage sources.
   Keep the nat-20 / nat-1 extremes; they generate stories.
2. **Deferred detection**, done correctly — a `GameComponent` with the right
   `(Game game)` constructor, or simpler, a `Hediff`/`ThingComp` tick so there's
   no game-level component to get wrong.
3. **Escalating Alertness** as a hediff on nearby pawns — the original's best
   idea, and it self-balances repeat theft without a hard cap.
4. **Consequence branch as a CQF DialogTree** rather than a bespoke window, so
   it inherits the arc's authoring tools and voice.
5. **Wire the outcomes:** faction goodwill delta on detection, an Imperial Heat
   bump when the mark is Empire-aligned, and an event emitted to the satiation
   blackboard so the gods can have opinions.

**Guardrail:** loot must stay junk-tier and quest-irrelevant. Theft is a
*narrative* and *social* mechanic here, not an acquisition channel — it must
never become a way to bypass the techprint/quest gates. §19.5 applies.

**Cheapest first step:** skip the mod entirely and prototype the *social* half as
a CQF DialogTree fired by an existing theft event. If the Quibble/Threaten/Admit
beat lands in play, then it's worth writing the dice layer underneath it.
