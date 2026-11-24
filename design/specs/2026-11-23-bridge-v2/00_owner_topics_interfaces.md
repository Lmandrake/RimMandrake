# Topics the owner introduced for BRIDGE v2.0: high-level interfaces

The owner gave this text on 2026-11-23. He said: "Here's the topics I meant to introduce". Earlier that day he put the
same thought in his own words: "Claude does better when it has a small number of very rich entry points into programs
with excellent documentation" more than "a thousand entry points to sort through and remember." He asked that this
thinking be ingested into the BRIDGE v2.0 designs and plans.

The text below is his paste, kept word for word. It is source material from outside this project. It is not a ruling. The
related study in this repo is `design/RimMandrake/mattpocock_design_suggestions.md` and
`design/RimMandrake/2026-11-07-pocock-design/03-merged.md` (deep modules, the deletion test).

## The pasted text

In software engineering with Claude (especially via Claude Code), the biggest shift is moving from writing low-level code
to designing high-level interfaces and system boundaries. Because agentic tools handle the boilerplate and execution
loop, the human engineer's primary value moves up the abstraction stack.

### Why High-Level Interfaces Matter More Now

- **Intent Over Implementation.** Instead of dictating how a function should be written line-by-line, you define the
  contract: inputs, outputs, state transitions, and constraints. Claude handles the execution loop—reading files, running
  tests, and refining the code until the contract is met.
- **Decoupling the "Brain" from the "Hands".** Modern agentic architectures rely on clean boundaries between the
  reasoning model, the execution environment (sandboxes/tools), and session state. Similarly, in your own codebase,
  well-defined module interfaces prevent an AI agent from causing cascading side effects when modifying isolated
  components.
- **Context Window Management.** Large codebases fail when you dump everything into context. Clean interfaces allow
  Claude to traverse the filesystem, inspect a header or type definition, and understand how to interact with a module
  without needing to read its deep internal implementation.
- **Verification Gates.** High-level architecture allows you to build automated "gates" (type checks, integration tests,
  Playwright UI checks). If your interfaces are rigid, Claude can self-correct against compiler errors and test failures
  before you ever review a Pull Request.

### High-Level vs. Deep Implementation: Where Each Lives

| Responsibility | Human Engineer (High-Level) | Claude / Subagents (Deep Execution) |
|---|---|---|
| System Design | Defines API contracts, data schemas, and module boundaries. | Propagates interface changes across controllers, queries, and UI. |
| Workflow & Orchestration | Splits work into isolated tickets or git worktrees; sets architectural rules (CLAUDE.md). | Runs parallel sessions, greps codebases, and executes bash commands. |
| Quality Assurance | Reviews architectural fit, security boundaries, and edge-case logic. | Writes unit tests, runs linters, and fixes failing assertions in a loop. |

### Practical Takeaways for Your Workflow

- **Front-load your design.** Spend your energy defining strict types, API specs, and clear tickets before letting Claude
  write code.
- **Use subagents for deep dives.** Keep your main session focused on high-level orchestration, and delegate deep
  codebase exploration or isolated refactoring tasks to subagents so your primary context stays clean.
- **Automate the feedback loop.** Connect Language Server Protocol (LSP) diagnostics and test runners via hooks so Claude
  immediately sees "red squigglies" when it violates an interface contract.

## What a BRIDGE v2.0 design pass must answer from this

1. **The contract of each entry point.** For each of the few entry points: its inputs, outputs, state transitions and
   constraints, on one page that an agent can read without reading the implementation.
2. **Read the contract, not the internals.** Where that page lives, and how a test author or an agent finds it in one
   step. Today the bridge has about 547 tools and a skill file.
3. **Rigid interfaces and gates.** The check that turns red at once when a caller breaks an entry point's contract (a
   typed schema, a contract test for each entry point, a refusal by name).
4. **Brain and hands.** Which side decides (Python, outside the game) and which side only acts and records (the game).
5. **The owner's part.** The design names the interface contracts that the owner reviews before the build. He reviews
   contracts, not code.
