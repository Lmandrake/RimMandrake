# Pre-release hidden-behaviour hunt: Gimme Some Slack (RimWorld 1.6 mod) — consult {PART}

You are a senior RimWorld 1.6 modder (Verse/RimWorld internals, Harmony, Scribe, map components, section layers,
power nets, Ideology styles) doing the last source read before this mod ships. The live test suite passes 110/110
on fresh maps, so the bugs left are the ones that test path does NOT walk. Your job is to find them.

`CONTEXT.md` (inlined first) says what the mod is, what the owner wants a player to see (north star), what is already
known or fixed (the previous GPT read — do not re-report those unless the fix is missing, wrong or incomplete), and how
we debug. The design excerpt shows intended behaviour; a place where the code does not do what the design or the
north star says is a finding.

**This consult covers: {SCOPE}** Other files of the mod are in sibling consults; when a finding depends on a file you
cannot see, say exactly what you assumed about it.

Hunt specifically for:
1. **Save/load and reload-to-earlier-tick.** Fields not scribed, scribed but not re-derived, PostLoadInit ordering,
   cross-references to destroyed/despawned things, state rebuilt from the wrong tick, "pending" queues lost on save.
2. **Static state that outlives a game or a map** — the class that just bit us: static dictionaries/sets/latches
   keyed by thingIDNumber, Map, map index, cell or tick that survive "load a save", "new game", "quicktest map
   destroyed and regenerated". IDs and ticks REPEAT across reloads. Also static caches of Materials/Meshes/Textures.
3. **Map removal and multiple maps.** Map components holding references to other maps; things in caravans/pods/
   gravships (1.6 gravship moves buildings between maps!); MapComponent work that only happens for Find.CurrentMap;
   a map that is never viewed.
4. **Harmony patch conflicts** with common mods (Dubs Bad Hygiene, Rimefeller, VE Framework/Power, Performance
   Optimizer, Rocketman, Multiplayer, Replace Stuff, Vehicle Framework, Allow Tool, Ideology style mods, other
   invisible-conduit mods), prefixes that return false, patch targets that may not exist, transpilers.
5. **Performance per tick and per frame** on a 500-mod list and a 5,000-conduit base: allocations in ticks/draws,
   O(n^2) sweeps, rebuilds triggered every frame, mesh regeneration storms, section-layer dirtiness.
6. **Threading** (RimWorld long events, map-gen threads, mesh building off main thread, Unity API off main thread).
7. **Null / destroyed / despawned things**, Faction null, comps on minified things, things reinstalled after
   minify, things with stuff changed, def removed from a save.
8. **Settings toggled mid-game** (master switches on/off, numeric changes) — what is left stale or half-applied.
9. **Def / inheritance / XML errors** — ParentName, abstract defs, ThingStyleDef wiring, comps, placeWorkers,
   translation keys referenced in code (`.Translate()`) that have no Keyed entry, labels missing.
10. **Map edges and odd geometry** — cells out of bounds, 1-wide maps, pocket maps, edges of roofed areas, walls of
    natural rock, doors, bridges, water.
11. **Design-vs-code mismatches** with the north star and design excerpt.

For EACH finding give, in a markdown table or numbered list:
- **id** ({PART}1, {PART}2, ...), **severity** (critical = save corruption / crash / red error spam / power
  wrongly delivered; high = visible wrong behaviour in normal play; medium = edge case; low = cosmetic/perf nit),
- **file:line** (line numbers as in the inlined file),
- **what happens** and the **mechanism** (why the code does it), quoting the decisive line,
- **repro**: the shortest in-game or offline sequence that shows it,
- **check**: one concrete offline check (a selftest assertion, a grep, an XML validation) or one live bridge check
  (spawn X, step N ticks, read Y via a probe verb, save+reload, read Y again) that would decide it,
- **confidence** (high/medium/low).

Rank by severity. Be concrete and skeptical: no generic advice, no style comments, no "consider adding tests".
If an area looks correct, say so in one line under a "checked, looks fine" list so we know it was covered.
Do not attempt to open files from disk; everything you get is inlined.
