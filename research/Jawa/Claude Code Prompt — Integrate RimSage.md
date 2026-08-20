Integrate **RimSage** into this RimWorld development environment as a project-level MCP service and make it a productive part of our existing development/debugging workflow.

RimSage endpoint:

`https://mcp.rimsage.com/mcp`

Use the current Claude Code MCP mechanism and project scope, equivalent to:

`claude mcp add --transport http rimsage --scope project https://mcp.rimsage.com/mcp`

Do the following:

1. **Inspect our existing environment first.**
   - Understand the current repository structure.
   - Read the relevant CLAUDE.md files, skills, agent definitions, build/test instructions, and RimBridge documentation.
   - Do not create a parallel workflow if we already have an appropriate place for this capability.

2. **Install/configure RimSage as a project MCP server.**
   - Prefer project scope so the configuration lives with this repository.
   - Verify that Claude Code recognizes the MCP server and that it connects successfully.
   - Do not self-host RimSage at this stage unless the hosted service proves inadequate.

3. **Discover the actual RimSage tool surface rather than assuming it.**
   It should provide capabilities along the lines of:
   - searching RimWorld C# source;
   - reading source files;
   - reading specific C# symbols/classes/interfaces;
   - searching XML Defs;
   - resolving Def details and inheritance;
   - browsing relevant source directories.

4. **Run several real smoke tests against RimWorld 1.6 source/Defs.**
   Demonstrate that you can:
   - locate a known RimWorld C# class by symbol;
   - trace a method or behavior through source;
   - find a vanilla Def by defName and inspect its resolved definition;
   - search for an implementation when we know the behavior but not the class responsible for it.

5. **Integrate RimSage conceptually with RimBridge.**

   Treat them as complementary systems:

   **RimSage = static implementation/source truth**
   - What classes, methods, fields, interfaces and signatures actually exist?
   - How does vanilla RimWorld implement a behavior?
   - What XML Defs exist and what do they resolve to?
   - What inheritance/implementation patterns should our mod follow?

   **RimBridge = live runtime/game truth**
   - What is actually happening in the running game?
   - What objects/state exist right now?
   - Can we invoke the behavior?
   - Can we reproduce the bug?
   - Did our change actually work?
   - What do the logs, screenshots, map state, pawns, Things, jobs, etc. show?

   The preferred debugging loop should therefore become:

   `problem → inspect live behavior with RimBridge → inspect relevant vanilla implementation with RimSage → inspect our code → form hypothesis → modify → build → test through RimBridge → use RimSage again when implementation/API questions arise → verify`

6. **Establish sensible usage rules.**
   Incorporate these into the existing skill/instruction architecture in the smallest appropriate place rather than bloating global instructions:

   - When making claims about RimWorld C# APIs, prefer checking RimSage over relying on model memory.
   - Before inventing a Harmony patch target, verify the actual class/method/signature with RimSage.
   - Before reimplementing substantial vanilla behavior, inspect how vanilla does it.
   - When working with Def inheritance or unfamiliar XML, inspect the actual Defs.
   - Use targeted symbol/source retrieval rather than loading enormous portions of RimWorld source unnecessarily.
   - Do not call RimSage mechanically for things already established by our own code or documentation.
   - RimSage answers implementation questions; RimBridge answers runtime questions. Use both when a problem spans both layers.

7. **Fit this into our existing agent/skill governance.**
   We already have established skills and agent responsibilities. Determine where RimSage guidance properly belongs and update that existing structure rather than proliferating redundant skills, agents, or documentation.

8. **Report what you changed and demonstrate the resulting workflow.**
   Show:
   - where the MCP configuration was installed;
   - whether RimSage is connected;
   - which tools it exposes;
   - what persistent project guidance you changed, if any;
   - results of the smoke tests;
   - one concrete example of how RimSage + RimBridge together improve our current mod-development/debugging loop.

Do not stop at merely adding the MCP configuration. The objective is to make RimSage an understood, tested, appropriately documented part of our actual RimWorld build and validation environment.