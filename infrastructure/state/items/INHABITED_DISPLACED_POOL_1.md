## spec
§4. `src/Jawa/Inhabited/Source/DisplacedPool.cs`, a `GameComponent` so it is
saved with the game and reachable from anywhere.
  `Dictionary<Faction, ThingOwner<Pawn>> pools`  — people who lost their place
  `void Absorb(Pawn p, Faction f)`               — on FATE:flee
  `List<Pawn> Draw(Faction f, int count)`        — removes and returns up to
                                                   `count`, oldest-displaced first
🔑 **Any cast being instantiated draws from the pool BEFORE generating anyone
new.** That single ordering rule is the whole recurring-character effect.
🔑 **This does NOT violate "frozen until visited"** — redistribution happens at
cast INSTANTIATION, when a map generates, never on a background tick. Do not add
a `GameComponentTick` that moves people around.
⛔ The dead never enter the pool (§3.1).

## verify
`dotnet build` clean. A `[DebugAction]` that absorbs 5 pawns and draws 3 returns
3 distinct pawns and leaves 2, across a save/load.

## criteria
raid a cast, leave, land on a second place of the same faction, and at least one
pawn there is a survivor of the first — same name, and RimWorld's own opinion
system already knows what you did to him.

## notes
**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

built 2026-08-20, `f0a9f6c`. Build clean; the save/load half is CHECK's, filed
under `ROSTER_SOAK_100_DAYS_1`.
🔴 **ONE DEVIATION, and it is a save-correctness fix, not a preference.** The spec
asked for `Dictionary<Faction, ThingOwner<Pawn>> pools`. **That container cannot
round-trip:** a `ThingOwner` must be constructed with its `IThingHolder` owner,
and `Scribe_Collections`' deep look has no way to hand one to a value it is
reconstructing — the owners come back null and every pool empties on load.
Shipped instead: ONE `ThingOwner<Pawn>` plus a faction QUERY. `Absorb(Pawn,
Faction, reason, origin)` and `Draw(Faction, int)` are the specified API,
unchanged, and `Draw` returns longest-waiting first as specified.
⛔ The dead never enter the pool; `Absorb` refuses them on the first line.
⛔ There is no `GameComponentTick` and there must not be one.
