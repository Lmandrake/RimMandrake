
## Hunt list (cover every one that applies to the files you were given)
1. Save/load: every field that must survive a save is Scribed; Scribe order/labels; null after load (PostLoadInit);
   jobs/drivers resuming mid-toil after load; **reload of an earlier save in the same session** (same thing IDs, earlier
   tick) — static/session-wide caches, "last tick" fields that are now in the future, dictionaries keyed by thingIDNumber
   or map index.
2. Static state that leaks across games, across maps, or across a "new game" from the main menu.
3. Map removal / multiple maps / pocket maps (Odyssey gravship & space layers, Anomaly pocket maps): MapComponents on
   non-Pyrelands maps, Find.CurrentMap vs parent map, references to destroyed maps or despawned things.
4. Fire spread and performance: per-tick allocations, full-map scans, LINQ in ticks, Rand state / seeding, unbounded
   fire, fires that never die, interactions with vanilla Fire and FireWatcher, rain, snuff.
5. Plant tick rules: Plant only ticks TickLong; comps on plants; growth math that assumes a finer tick.
6. Animal AI / jobs / duties: think-tree insertion order, job givers returning bad jobs, toils that never end,
   reservations, flee vs custom behaviour races, tame/caravan/roped/downed/drafted/mental-state pawns, animals in
   caravans or on the world map, pawns that despawn without a readable sign.
7. Heat/hediff interactions: vanilla Heatstroke/Hypothermia, temperature push, room temperature, comfortable temp
   ranges; anything that creates a second "kind" of heat.
8. Harmony patches: target signatures in 1.6, prefix return semantics, conflicts with common mods (CE, VEF,
   Performance Optimizer, Dubs), patches that run on every map not just Pyrelands.
9. Mod Settings changed mid-game: toggling a feature off/on with live state, defaults vs shipped behaviour, ranges.
10. Def / XML errors: inheritance (ParentName, Abstract), missing fields, wrong class names, comps on wrong thing
    classes, patches that silently match nothing, MayRequire misuse, defName collisions.
11. Map generation on a Pyrelands tile (GenSteps, scorched ruins, initial fire, plant/animal density). NOT world
    generation (ruled out of scope).
12. Design-vs-code mismatches: compare the design docs, north-star bars and known-behaviours log against the code.

## Output format (strict)
A numbered list of findings, most severe first. Each finding:
- **Title** (one line)
- **Where:** file:line (use the FILE headers given; line numbers counted within that file)
- **Mechanism:** what the code does and why it goes wrong (cite the exact lines)
- **Repro:** the concrete in-game or offline sequence that triggers it
- **Severity:** crash/corruption · gameplay-visible · cosmetic/perf · latent
- **Check:** the cheapest offline or live check that would confirm it (bridge static call, save inspection, selftest,
  Player.log string). For fire-hawk flight, only state reads, never visual flight checks.
- **Confidence:** high / medium / low
Do not pad with generic advice. Do not report the ruled-out items listed in the context (worldgen, DLC absence, a
biome on zero world tiles). If you find nothing for a hunt-list point, say so in one line at the end.
