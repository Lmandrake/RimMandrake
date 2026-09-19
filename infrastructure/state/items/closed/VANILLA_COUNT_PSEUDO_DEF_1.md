# VANILLA_COUNT_PSEUDO_DEF_1

Split off KOTOR_HEADBAND_DANGLING_REFS_1's crossref bucket (2026-09-03 big-dump
harvest): alongside the 23 guy762_Headband_* dangling refs (root cause found
and fixed separately — an accidental file deletion, restored), the same
harvest logged unresolved crossrefs to `MealSimple10`, `Chemfuel60`,
`Steel75`, `Silver120`, `ComponentIndustrial12` — none of which are real
defNames in vanilla or any def dump.

## investigation (FOUNDRY, 2026-09-03, live bridge session, fresh 589-mod restart)

Confirmed live in a fresh `Player.log`, all five as the exact same shape:

    Could not resolve cross-reference: No Verse.ThingDef named MealSimple10 found to give to Verse.ThingDefCountClass (1x null)

**`Verse.ThingDefCountClass` is the tell.** RimWorld's `ThingDefCountClass`
supports a compact single-token XML shorthand — `<li>Steel 75</li>`, parsed by
splitting on whitespace into defName + count — so `MealSimple10` reads as
exactly what that parser produces when the defName and count were
concatenated with **no space**: `MealSimple`+`10` → `MealSimple10`, a single
token neither half of which is a real defName on its own once joined. Same
shape for all five: `Chemfuel`+`60`, `Steel`+`75`, `Silver`+`120`,
`ComponentIndustrial`+`12`.

**This is not a static XML authoring typo — checked, and ruled out.** A
missing-space typo in some mod's raw `<li>Steel75</li>` was the obvious first
guess, so it was checked exhaustively rather than assumed: a full scan of
every `.xml` file in the ENTIRE subscribed Steam Workshop library (not just
the 589 active mods — the whole content-294100 folder), **68,641 XML files,
zero occurrences of any of the five literal strings.** If a mod's own XML
ever wrote `MealSimple10` as a bare token, this would have found it. It
didn't.

**Conclusion: these five defNames are constructed at runtime, not written in
any XML file on disk.** Some mod's C# builds a `ThingDefCountClass`-shaped
value (most likely for a reward/loot/cost list — a `ThingSetMaker`,
incident reward generator, or trade-response system) by string-concatenating
a defName and a count in memory — e.g. `defName + amount.ToString()` where
`" " + amount.ToString()` was meant — and hands the result to something that
re-parses it as if it were the compact XML shorthand string. Tracing the
exact mod requires finding which one's compiled assembly builds and
re-parses a `ThingDefCountClass`(-like) string at runtime, which needs
decompiling/searching third-party DLLs across the mod set (`ilprobe` typedef
dumps, one at a time) rather than a text scan — a materially bigger and
different search than the one this item was filed expecting.

## spec (revised)

~~Identify which mod/file emits these five (or more — the harvest only
sampled) count-suffixed pseudo-defNames~~ — revised given the finding above:
identify which mod's **C# code** builds a `ThingDefCountClass` (or
equivalent) via string concatenation without a separating space between the
defName and the count, since no mod's static XML is responsible.

## verify

Not yet done — needs an `ilprobe` sweep of candidate assemblies (reward/loot/
trade-generation mods) for a `ThingDefCountClass`-shaped string build, or a
live in-game trigger (a quest offer, a trade window, a raid reward) that
reproduces one of the five errors freshly with dev-mode logging pinned to the
triggering incident.

## criteria

Source **mod** named (this is very unlikely to be ours — checked our own
`src/` for all five tokens earlier this session too, no hits). If ours: fix
the concatenation. If third-party: recorded here as such, and whether it's
worth a defensive patch on our side (a `ThingDefCountClass` this fragile
could misfire again with a different number) is a call for whoever picks this
back up, not decided here — this pass's job was narrowing the search, which
it did: from "some mod's XML" to "some mod's C#", a materially smaller and
differently-shaped remaining search.
