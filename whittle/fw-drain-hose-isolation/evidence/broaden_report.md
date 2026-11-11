I made no edits. I read STATEMENT.md, NOTES.md (it holds only a heading), all of `HoseNetChecks.cs`, the `RM_NetComponents` section of `RM_LiquidNetKernel.cs`, design §3.1, and small parts of `HoseChecks.cs`, `Program.cs` and `NetComponentChecks.cs`.

## Why the current g3 check passes without testing anything

- `HoseNetChecks.cs:178-182` names the cells `a1` and `b1`. The fake graph decides a vertex's role from its first letter (`HoseNetChecks.cs:47`), and only names starting with lowercase `c` count as pipes. So `a1` and `b1` are not pipes.
- The kernel only starts a member's network from cells whose role is Pipe (`RM_LiquidNetKernel.cs:316`). P1 therefore has no network at all, its store is empty, and `!Contains("TV")` passes whether or not tanks conduct.
- The same happens on T's side: T's pipe cells are worked out in reverse from the pipe-to-tank table (`HoseNetChecks.cs:55`), giving `a1, b1`, and both are filtered out the same way.

## Suggested checks (narrow, test-only, g3 only)

**1. Positive and exact (the fix the statement asks for).** Rename the cells to `ca1` and `cb1`. Keep P1's touch table empty and leave no adjacency between the two cells.
```csharp
G.Add(g3.PipeOf, "P1", "ca1");
G.Add(g3.PT, "ca1", "T");
G.Add(g3.PT, "cb1", "T");
G.Add(g3.PT, "cb1", "TV");
RM_NetResult r3 = Walk(g3, "P1");
Check(Tanks(r3).SequenceEqual(new[] { "T" }) && Route(r3, "T") == "", "two pipe runs touching one tank stay two nets: the pump reaches T over its run, never TV");
```
- On the old `a1`/`b1` names this fails because the store is empty. That is the "fails on the old unrecognized fixture" control.
- The empty route rules out a hose path. Leaving the touch table empty rules out reaching T by touch instead of by pipe.

**2. Both runs exist and stay separate.** Use a fresh `RM_NetComponents` instance:
```csharp
var c3 = new RM_NetComponents(g3);
RM_NetComponent near = c3.ComponentOfNode("ca1"), far = c3.ComponentOfNode("cb1");
Check(near != null && far != null && near != far && far.Tanks.Contains("TV") && !near.Tanks.Contains("TV")
      && c3.ComponentsOf("T").Count == 2, "can-fail: both runs are recognized pipes, T is in both, TV only on the far one");
```
- `ComponentOfNode` returns null for a vertex that doesn't conduct (`:291`). So a misspelled cell name now fails loudly instead of passing quietly.
- This mirrors the existing T/TU check at `:188`.

**3. Optional.** Only add a third check if a reviewer asks for one. Checks 1 and 2 cover the statement.

## How the proposed mutant behaves

The mutant: in an isolated copy of the kernel, add this in `Build` right after the tank loop at `:374`:
```csharp
foreach (object c in g.OriginPipeCells(t)) if (g.RoleOf(c) == RM_NetRole.Pipe) { Visit(comp, c, i, q); st?.Add(new Step { Kind = 3, Obj = c }); }
```

| | production kernel | mutant kernel |
|---|---|---|
| old g3 (`a1`/`b1`) | passes (proves nothing) | passes (misses the mutant) |
| new g3 (`ca1`/`cb1`) | passes | check 1 fails (store is {T, TV}); check 2 fails (`near == far`) |

I went through every other fixture in `HoseNetChecks`: in each one, the tank's pipe cells are already in the network being built (`c2`/T2, `c3`/T7, `c8`/T8, `c1`/T, `c5`/T5). So in a HoseNetChecks-only build, only the g3 messages should fail under the mutant. The expected number of failures can be stated in advance and matched exactly.

## Pitfalls

1. **Record the step.** The mutant must call `st?.Add(... Kind = 3 ...)`. The fake graph supplies a node order, so `Reroot` (`:387`) replays only recorded steps. With `ca1 < cb1` the root stays at index 0 and the replay is skipped, but a different naming would silently drop the merged node and corrupt indices. Either record the step or keep the near cell's name sorting first.
2. **The full selftest can't show which check caught the mutant.** `NetComponentChecks.cs:26-44` ("Net_tank_between_two_runs…") already uses recognized `ca*`/`cb*` names and would also kill the mutant. Use the full production-linked wrapper only for the pass on final sources. If the mutant ever goes through it, filter with `--only HoseNetChecks` (the hose-suite filter in `HoseChecks.cs:29`).
3. **Exact source identity.** Hash the final `HoseNetChecks.cs` and the production kernel. Show the offline project compiles that same `HoseNetChecks.cs` byte for byte, and that the mutant lives only in a copied kernel. The production kernel's hash should be unchanged, and the diff should touch only `HoseNetChecks.cs`; that also covers "shipping behaviour and GSS cord appearance preserved".
4. **Stub `Program.Check` correctly.** The offline stub needs `RimMandrake.FlowWorks.SelfTest.Program.Check(bool, string)` that counts failures and prints the message. If it swallows failures, the mutant run passes falsely. Also catch exceptions per suite, as `HoseSuite` does.
5. **Weak assertion forms.** Don't keep `!Contains("TV")` alone. Don't let P1's pipe cells include `cb1`. Don't put T in P1's touch table.
6. **Unstable sort.** If you ever assert an exact sequence of two tanks with the same route length and the same order key (T and TV both parse to 0), `List.Sort` gives no guaranteed order. Check 1 has only one tank, so it is safe.
7. **Messages are part of the evidence.** If you change the g3 message wording, update whatever greps or counts the evidence relies on for the expected `FAIL hosenet:` lines.
8. **Limitation to state.** The design says a tank attaches to a pipe "cardinal to it or under it", but the fake graph's reverse lookup doesn't model geometry. The test proves that tanks don't conduct between networks, not the adjacency rule. The mutant also covers only the pipe–tank–pipe path; tank conduction across hoses is covered separately by the `g`/TU checks at `:169` and `:188`.

## Scope creep (leave out)

- A guard in the shared fake graph `G` that throws on unrecognized names. Seven other suites use `G`, so this is a broader change.
- Multi-cell runs, a pump on the far run, pipes-off variants, or extra mutants such as tanks conducting over their hoses. None of these discriminate the target mutant better.
- Editing `NetComponentChecks` or the kernel.